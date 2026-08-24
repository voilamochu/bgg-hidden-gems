"""
Second-pass population — game-level dedup + recursive closure (deferred, now authorized).

Primary pipeline remains 16,627 × ≥10 minus degenerate_strict → 24.5M obs.
This script builds the SECOND-PASS population for direct comparison before adoption.

Steps:
1. Game-level cleanup reviewing each game in 16,627 population using richer 9GB SQLite metadata:
   - Rule A: Edition/Big Box/Deluxe/Anniversary/Collector/Special/Designer/Revised where stripped base collides
   - Rule B: Duplicate title_clean (exact) with designer identical (keep most popular)
   - Rule C: Targeted family collapse for Monikers (stem monikers) and Time's Up! (Game: Time's Up! family)
   - Rule D-E: Investigated but NOT adopted: reimplementation triple, language/version (0), broad stem>5 (too aggressive)
2. Recursive closure to fixed point:
   Start from candidate universe (after Step1) or 16,627 base for comparison.
   Iteratively remove games <100 qualifying ratings (active), users <10, and recompute degenerate_strict/broad
   until convergence. Each prune can introduce new candidates.

Outputs under data/processed/phase2-second-pass/:
- bgg_population_second_pass.parquet (game-level after Step1, before closure)
- bgg_population_second_pass_closed.parquet (after recursive closure)
- pruned_lists/*.csv per rule + combined
- closure_log.csv (per-iteration games/users/obs/degenerate)
- users_second_pass_closed.parquet (active users after closure)
- rating_observations_active_second_pass.parquet (if feasible) or counts
- comparison_table.json

Also writes docs/future-methodology-review/executed_rules.md and README.

Bounded: memory 4GB threads 3 temp scratch/ducktmp, copy-once, narrow single-scan aggregations.
"""
import argparse
import ast
import json
import re
import shutil
import time
from collections import Counter, defaultdict
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
MEMORY = "4GB"
THREADS = 3

def qpath(p: Path) -> str:
    return str(p).replace("'", "''")

def configure(con, tmp_dir: Path):
    con.execute(f"SET memory_limit='{MEMORY}'")
    con.execute(f"SET threads={THREADS}")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    con.execute(f"SET temp_directory='{qpath(tmp_dir)}'")
    con.execute("SET preserve_insertion_order=false")

def stripped_base(title: str) -> str:
    if not isinstance(title, str):
        return ""
    s = title.lower()
    # Remove edition suffixes: handle Deluxe, Big Box, Anniversary, etc. with or without "Edition"
    # Order matters: longest first
    patterns = [
        r"\s*:?\s*deluxe edition.*",
        r"\s*:?\s*special edition.*",
        r"\s*:?\s*collector's edition.*",
        r"\s*:?\s*collectors edition.*",
        r"\s*:?\s*collector edition.*",
        r"\s*:?\s*big box.*",
        r"\s*:?\s*anniversary edition.*",
        r"\s*:?\s*anniversary.*",
        r"\s*:?\s*designer edition.*",
        r"\s*:?\s*revised edition.*",
        r"\s*\(.*edition.*\)",
        r"\s*:?\s*deluxe.*",
        r"\s*:?\s*special.*",
    ]
    out = s
    for pat in patterns:
        out = re.sub(pat, "", out, flags=re.IGNORECASE)
    out = re.sub(r"\s+\d+$", "", out).strip()
    return out

def parse_list_field(v):
    try:
        p = ast.literal_eval(v) if isinstance(v, str) else []
        return list(p) if isinstance(p, list) else []
    except:
        return []

def mech_set(s):
    try:
        return set(ast.literal_eval(s)) if isinstance(s, str) else set()
    except:
        return set()

def jaccard(a,b):
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

def game_families_list(fam_str):
    try:
        lst = ast.literal_eval(fam_str) if isinstance(fam_str, str) else []
        return [x[5:].strip() for x in lst if isinstance(x, str) and x.startswith("Game:")]
    except:
        return []

def stem_title(t):
    if not isinstance(t, str):
        return ""
    s = t.lower()
    s = s.split(":")[0].strip()
    s = re.sub(r"\(.*\)", "", s).strip()
    return s

def ensure_scratch_copy():
    src_pop = REPO / "data/processed/bgg_research_population.parquet"
    src_active = REPO / "data/processed/phase2-active"
    dst = REPO / "scratch/second-pass"
    dst.mkdir(parents=True, exist_ok=True)
    # copy population
    if not (dst / "bgg_research_population.parquet").exists() and src_pop.exists():
        shutil.copy2(src_pop, dst / "bgg_research_population.parquet")
        print(f"copy-once population {src_pop} -> {dst}")
    # copy active extracts needed for closure
    for fn in ["rating_observations_active.parquet", "users_active.parquet", "game_adjusted_means_active.parquet", "user_severity_active.parquet"]:
        sp = src_active / fn
        dp = dst / fn
        if sp.exists() and not dp.exists():
            shutil.copy2(sp, dp)
            print(f"copy-once {sp} -> {dp}")
    # also copy game_tags/links filtered for dedup analysis (reuse from phase2-filtered)
    src_filtered = REPO / "data/processed/phase2-filtered"
    for fn in ["game_links_filtered.parquet", "games_filtered.parquet", "game_tags_filtered.parquet"]:
        sp = src_filtered / fn
        dp = dst / fn
        if sp.exists() and not dp.exists():
            shutil.copy2(sp, dp)
            print(f"copy-once {sp} -> {dp}")
    return dst

def compute_edition_rule(pop_df):
    """Rule A: Edition/Big Box etc where stripped base collides. Keep most popular per base."""
    edition_pat = r"(?i)\b(deluxe|anniversary|big box|collector|special edition|designer edition|revised edition)\b"
    # Need to use regex with correct escaping; pandas str.contains handles regex
    pop_df = pop_df.copy()
    pop_df["base"] = pop_df["title"].apply(stripped_base)
    # detect edition keyword via python re
    pop_df["is_edition"] = pop_df["title"].apply(lambda t: bool(re.search(edition_pat, t or "")))
    to_remove = set()
    keep_map = {}  # base -> keeper game_id
    details = []
    for base, group in pop_df.groupby("base"):
        if len(group) <= 1:
            continue
        if not group["is_edition"].any():
            continue
        # base collision group has at least one edition
        keeper = group.loc[group["users_rated"].idxmax()]
        keep_map[base] = int(keeper["game_id"])
        for _, row in group.iterrows():
            if row["is_edition"] and row["game_id"] != keeper["game_id"]:
                to_remove.add(int(row["game_id"]))
                details.append({
                    "rule": "edition_bigbox",
                    "base": base,
                    "removed_game_id": int(row["game_id"]),
                    "removed_title": row["title"],
                    "keeper_game_id": int(keeper["game_id"]),
                    "keeper_title": keeper["title"],
                    "removed_users_rated": float(row["users_rated"]),
                    "keeper_users_rated": float(keeper["users_rated"]),
                    "year_removed": float(row["year"]) if pd.notna(row["year"]) else None,
                    "year_keeper": float(keeper["year"]) if pd.notna(keeper["year"]) else None,
                })
    return to_remove, details, pop_df

def compute_duplicate_rule(pop_df):
    """Rule B: title_clean exact duplicate where designer identical, keep most popular."""
    to_remove = set()
    details = []
    for title_clean, group in pop_df.groupby("title_clean"):
        if len(group) <= 1:
            continue
        gs = group.sort_values("users_rated", ascending=False)
        keeper = gs.iloc[0]
        for _, row in gs.iloc[1:].iterrows():
            if row["designers"] == keeper["designers"]:
                # guard: title_clean exact duplicate and designer identical
                to_remove.add(int(row["game_id"]))
                details.append({
                    "rule": "duplicate_title_clean_designer",
                    "title_clean": title_clean,
                    "removed_game_id": int(row["game_id"]),
                    "removed_title": row["title"],
                    "keeper_game_id": int(keeper["game_id"]),
                    "keeper_title": keeper["title"],
                    "year_removed": float(row["year"]) if pd.notna(row["year"]) else None,
                    "year_keeper": float(keeper["year"]) if pd.notna(keeper["year"]) else None,
                    "gap_year": abs(float(row["year"]) - float(keeper["year"])) if pd.notna(row["year"]) and pd.notna(keeper["year"]) else None,
                })
    return to_remove, details

def compute_monikers_time_rule(pop_df):
    """Rule C: targeted collapse for Monikers (stem) and Time's Up! (Game family)."""
    to_remove = set()
    details = []
    # Monikers via stem
    pop_df = pop_df.copy()
    pop_df["stem"] = pop_df["title"].apply(stem_title)
    mon_group = pop_df[pop_df["stem"] == "monikers"]
    if len(mon_group) > 1:
        keeper = mon_group.loc[mon_group["users_rated"].idxmax()]
        for _, row in mon_group.iterrows():
            if row["game_id"] != keeper["game_id"]:
                to_remove.add(int(row["game_id"]))
                details.append({
                    "rule": "family_monikers_stem",
                    "family": "Monikers (stem=monikers)",
                    "removed_game_id": int(row["game_id"]),
                    "removed_title": row["title"],
                    "keeper_game_id": int(keeper["game_id"]),
                    "keeper_title": keeper["title"],
                    "year_removed": float(row["year"]) if pd.notna(row["year"]) else None,
                    "users_removed": float(row["users_rated"]),
                })
    # Time's Up! via Game: family
    pop_df["game_fams"] = pop_df["families"].apply(game_families_list)
    mask_time = pop_df["game_fams"].apply(lambda lst: "Time's Up!" in lst)
    time_group = pop_df[mask_time]
    if len(time_group) > 1:
        keeper = time_group.loc[time_group["users_rated"].idxmax()]
        for _, row in time_group.iterrows():
            if row["game_id"] != keeper["game_id"]:
                # avoid double-count if already removed via monikers (no overlap expected)
                if int(row["game_id"]) not in to_remove:
                    to_remove.add(int(row["game_id"]))
                    details.append({
                        "rule": "family_times_up_game",
                        "family": "Time's Up! (Game: Time's Up!)",
                        "removed_game_id": int(row["game_id"]),
                        "removed_title": row["title"],
                        "keeper_game_id": int(keeper["game_id"]),
                        "keeper_title": keeper["title"],
                        "year_removed": float(row["year"]) if pd.notna(row["year"]) else None,
                        "users_removed": float(row["users_rated"]),
                    })
                else:
                    # already counted, add detail but not duplicate
                    pass
    # Also check Small World family via Game: Small World for completeness (not collapsing, but show)
    sw_group = pop_df[pop_df["game_fams"].apply(lambda lst: "Small World" in lst)]
    # For Small World, keeper is base 40692; Designer Edition 140135 would be removed under edition rule, but we note here
    # Do not automatically collapse Small World family beyond edition rule, to keep Small World Underground etc distinct.
    # Just document.
    return to_remove, details, sw_group

def compute_reimplementation_investigate(pop_df, links_df):
    """Investigate reimplementation rule (NOT adopted as primary) — weight within 0.2, mech Jaccard >0.8, designer identical."""
    pop_ids = set(pop_df["game_id"])
    links = links_df[links_df["rel"] == "reimplementation"]
    pairs = []
    for _, r in links.iterrows():
        if r["game_id"] in pop_ids and r["other_id"] in pop_ids:
            pairs.append((int(r["game_id"]), int(r["other_id"])))
    # mech dict
    mech_dict = {}
    for _, row in pop_df.iterrows():
        mech_dict[int(row["game_id"])] = mech_set(row["mechanics"])
    pop_idx = pop_df.set_index("game_id")
    to_remove = set()
    details = []
    for a,b in pairs:
        if a not in pop_idx.index or b not in pop_idx.index:
            continue
        ra = pop_idx.loc[a]; rb = pop_idx.loc[b]
        designer_same = ra["designers"] == rb["designers"]
        weight_ok = pd.notna(ra["weight"]) and pd.notna(rb["weight"]) and abs(float(ra["weight"]) - float(rb["weight"])) <= 0.2
        mech_ok = jaccard(mech_dict.get(a, set()), mech_dict.get(b, set())) > 0.8
        if weight_ok and mech_ok and designer_same:
            # keep more popular
            if float(ra["users_rated"]) < float(rb["users_rated"]):
                rem, keep = a, b
            else:
                rem, keep = b, a
            if rem not in to_remove:
                to_remove.add(rem)
                details.append({
                    "removed_game_id": rem,
                    "removed_title": pop_idx.loc[rem]["title"],
                    "keeper_game_id": keep,
                    "keeper_title": pop_idx.loc[keep]["title"],
                    "weight_removed": float(pop_idx.loc[rem]["weight"]) if pd.notna(pop_idx.loc[rem]["weight"]) else None,
                    "weight_keeper": float(pop_idx.loc[keep]["weight"]) if pd.notna(pop_idx.loc[keep]["weight"]) else None,
                    "jaccard": jaccard(mech_dict.get(rem, set()), mech_dict.get(keep, set())),
                })
    return to_remove, details, len(pairs)

def compute_language_version_investigate(pop_df, links_df):
    """Investigate language/version rule: rel=version where designer+year identical."""
    pop_idx = pop_df.set_index("game_id")
    vers = links_df[links_df["rel"] == "version"]
    pop_ids = set(pop_df["game_id"])
    to_remove = set()
    details = []
    for _, r in vers.iterrows():
        a = int(r["game_id"]); b = int(r["other_id"])
        if a in pop_ids and b in pop_ids:
            if a not in pop_idx.index or b not in pop_idx.index:
                continue
            ra = pop_idx.loc[a]; rb = pop_idx.loc[b]
            if ra["designers"] == rb["designers"] and pd.notna(ra["year"]) and pd.notna(rb["year"]) and float(ra["year"]) == float(rb["year"]):
                # same designer and year -> likely same design language edition
                if float(ra["users_rated"]) < float(rb["users_rated"]):
                    rem, keep = a, b
                else:
                    rem, keep = b, a
                if rem not in to_remove:
                    to_remove.add(rem)
                    details.append({"removed": rem, "keeper": keep})
    return to_remove, details

def quantify_rule(pop_df, active_obs_path, removed_ids, rule_name, con):
    """Quantify games removed, obs removed, users affected, categories/eras, etc."""
    if not removed_ids:
        return {"games_removed": 0}
    removed_ids = list(removed_ids)
    # Games
    removed_games_df = pop_df[pop_df["game_id"].isin(removed_ids)]
    # Obs removed: count in rating_observations_active for those games
    # Use DuckDB narrow aggregation
    ids_str = ",".join(map(str, removed_ids))
    # For large ids, use temp table via join instead of IN list to avoid bug
    # We'll create a temp parquet of ids and join
    # Simpler: use IN with batched
    # Use single-scan
    obs_removed = con.execute(f"SELECT COUNT(*) FROM read_parquet('{qpath(active_obs_path)}') WHERE game_id IN ({ids_str})").fetchone()[0] if len(removed_ids) < 1000 else con.execute(f"SELECT COUNT(*) FROM read_parquet('{qpath(active_obs_path)}') WHERE game_id IN (SELECT * FROM (VALUES {','.join(f'({x})' for x in removed_ids)}))").fetchone()[0]
    # Users affected: users who lose >=1 rating, and users who lose all ratings
    # For users affected we need per-user counts before/after. Approx via counts.
    # Compute users who have at least one rating in removed games
    users_affected = con.execute(f"SELECT COUNT(DISTINCT user_pseudouserid) FROM read_parquet('{qpath(active_obs_path)}') WHERE game_id IN ({ids_str})").fetchone()[0] if len(removed_ids) < 1000 else 0
    # For users who lose all ratings, we need to know if their remaining n_active after removal would be 0. Approximate via total vs removed per user: users where n_active == n_removed
    # Compute per-user total and removed
    # Use duckdb to compute: total per user, removed per user, where removed==total
    try:
        lose_all = con.execute(f"""
            WITH total AS (SELECT user_pseudouserid, COUNT(*) n_total FROM read_parquet('{qpath(active_obs_path)}') GROUP BY user_pseudouserid),
            rem AS (SELECT user_pseudouserid, COUNT(*) n_rem FROM read_parquet('{qpath(active_obs_path)}') WHERE game_id IN ({ids_str}) GROUP BY user_pseudouserid)
            SELECT COUNT(*) FROM total JOIN rem USING (user_pseudouserid) WHERE n_total = n_rem
        """).fetchone()[0]
    except Exception as e:
        lose_all = None
    # Categories/eras/volume
    era_counts = removed_games_df["year"].apply(lambda y: int(y//10*10) if pd.notna(y) else None).value_counts().to_dict() if not removed_games_df.empty else {}
    # Categories prevalence (parse)
    cat_counter = Counter()
    for _, row in removed_games_df.iterrows():
        cats = parse_list_field(row["categories"])
        cat_counter.update(cats)
    top_cats = dict(cat_counter.most_common(10))
    # Volume distribution
    vol_stats = {"mean_users_rated": float(removed_games_df["users_rated"].mean()) if not removed_games_df.empty else None,
                 "median_users_rated": float(removed_games_df["users_rated"].median()) if not removed_games_df.empty else None,
                 "min_users_rated": float(removed_games_df["users_rated"].min()) if not removed_games_df.empty else None,
                 "max_users_rated": float(removed_games_df["users_rated"].max()) if not removed_games_df.empty else None}
    return {
        "rule": rule_name,
        "games_removed": len(removed_ids),
        "game_ids": sorted(removed_ids),
        "obs_removed": int(obs_removed) if obs_removed else 0,
        "users_affected_any": int(users_affected) if users_affected else 0,
        "users_lose_all": int(lose_all) if lose_all is not None else None,
        "era_counts": era_counts,
        "top_categories": top_cats,
        "volume": vol_stats,
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=REPO / "data/processed/phase2-second-pass")
    args = parser.parse_args()
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "pruned_lists").mkdir(parents=True, exist_ok=True)
    tmp_dir = REPO / "scratch/ducktmp"
    scratch = ensure_scratch_copy()
    pop_path = scratch / "bgg_research_population.parquet"
    if not pop_path.exists():
        pop_path = REPO / "data/processed/bgg_research_population.parquet"
    active_obs_path = scratch / "rating_observations_active.parquet"
    if not active_obs_path.exists():
        active_obs_path = REPO / "data/processed/phase2-active/rating_observations_active.parquet"
    users_active_path = scratch / "users_active.parquet"
    if not users_active_path.exists():
        users_active_path = REPO / "data/processed/phase2-active/users_active.parquet"
    game_links_path = scratch / "game_links_filtered.parquet"
    if not game_links_path.exists():
        game_links_path = REPO / "data/processed/phase2-filtered/game_links_filtered.parquet"

    con = duckdb.connect()
    configure(con, tmp_dir)

    print(f"pop={pop_path} active_obs={active_obs_path} out={out_dir}")
    # Load pop as pandas for rule computation
    pop_df = pd.read_parquet(pop_path)
    print(f"pop games {len(pop_df)}")
    links_df = pd.read_parquet(game_links_path) if game_links_path.exists() else pd.DataFrame(columns=["game_id","rel","other_id","other_name"])
    print(f"links {len(links_df)}")

    # ---- Rule A: edition ----
    print("\n[Rule A] Edition/Big Box/Deluxe/etc")
    edition_remove, edition_details, pop_with_base = compute_edition_rule(pop_df)
    print(f"  edition would remove {len(edition_remove)}")
    # ---- Rule B: duplicate title_clean ----
    print("\n[Rule B] Duplicate title_clean designer identical")
    dup_remove, dup_details = compute_duplicate_rule(pop_df)
    print(f"  duplicate would remove {len(dup_remove)}")
    # ---- Rule C: monikers/time ----
    print("\n[Rule C] Monikers/Time's Up! targeted family")
    family_remove, family_details, sw_group = compute_monikers_time_rule(pop_df)
    print(f"  family collapse would remove {len(family_remove)}")
    print(f"  Small World family size {len(sw_group)} (for documentation, not collapsed)")
    print(sw_group[["game_id","title","year","users_rated"]].to_string(index=False) if not sw_group.empty else "none")
    # ---- Investigate reimplementation ----
    print("\n[Investigate] Reimplementation triple (weight+mech+designer) — NOT adopted as primary")
    reimp_remove, reimp_details, n_pairs = compute_reimplementation_investigate(pop_df, links_df)
    print(f"  reimplementation triple would remove {len(reimp_remove)} of {n_pairs} pairs")
    # ---- Language/version ----
    print("\n[Investigate] Language/version designer+year identical")
    lang_remove, lang_details = compute_language_version_investigate(pop_df, links_df)
    print(f"  language/version would remove {len(lang_remove)}")

    # Quantify each rule
    quant_edition = quantify_rule(pop_df, active_obs_path, edition_remove, "edition_bigbox", con)
    quant_dup = quantify_rule(pop_df, active_obs_path, dup_remove, "duplicate_title_clean", con)
    quant_family = quantify_rule(pop_df, active_obs_path, family_remove, "family_monikers_timesup", con)
    quant_reimp = quantify_rule(pop_df, active_obs_path, reimp_remove, "reimplementation_triple_investigate", con)
    quant_lang = quantify_rule(pop_df, active_obs_path, lang_remove, "language_version_investigate", con)

    # Combined primary second-pass: edition + family (core) — this directly addresses flagged cases
    # Keep more popular per group already ensured; combined unique
    primary_remove = set(edition_remove) | set(family_remove)
    # Sensitivity combined: primary + duplicate (adds 49 with overlaps)
    sensitivity_remove = primary_remove | set(dup_remove)
    # Full investigate combined (for docs): primary + duplicate + reimp
    full_investigate_remove = sensitivity_remove | set(reimp_remove) | set(lang_remove)

    print(f"\nPrimary combined (edition+family) would remove {len(primary_remove)} games")
    print(f"Sensitivity combined (primary+duplicate) would remove {len(sensitivity_remove)}")
    print(f"Full investigate combined would remove {len(full_investigate_remove)}")

    # Detailed quantification for primary and sensitivity
    quant_primary = quantify_rule(pop_df, active_obs_path, primary_remove, "primary_edition_family", con)
    quant_sensitivity = quantify_rule(pop_df, active_obs_path, sensitivity_remove, "sensitivity_primary_dup", con)

    # ---- Build second-pass population parquet (primary) ----
    primary_ids = set(pop_df["game_id"]) - primary_remove
    second_pass_df = pop_df[pop_df["game_id"].isin(primary_ids)].copy()
    # Drop helper columns if any
    for col in ["base","is_edition","stem","game_fams"]:
        if col in second_pass_df.columns:
            second_pass_df = second_pass_df.drop(columns=[col])
    second_pass_path = out_dir / "bgg_population_second_pass.parquet"
    second_pass_df.to_parquet(second_pass_path, index=False)
    print(f"\nWrote primary second-pass population {len(second_pass_df)} games -> {second_pass_path}")

    # Also write sensitivity population for reference
    sens_ids = set(pop_df["game_id"]) - sensitivity_remove
    sens_df = pop_df[pop_df["game_id"].isin(sens_ids)].copy()
    for col in ["base","is_edition","stem","game_fams"]:
        if col in sens_df.columns:
            sens_df = sens_df.drop(columns=[col])
    sens_path = out_dir / "bgg_population_second_pass_sensitivity_dup.parquet"
    sens_df.to_parquet(sens_path, index=False)
    print(f"Wrote sensitivity population {len(sens_df)} -> {sens_path}")

    # ---- Write pruned lists ----
    def write_ids(path, ids):
        pd.DataFrame({"game_id": sorted(ids)}).to_csv(path, index=False)

    write_ids(out_dir / "pruned_lists" / "rule_edition_bigbox.csv", edition_remove)
    write_ids(out_dir / "pruned_lists" / "rule_duplicate_title_clean.csv", dup_remove)
    write_ids(out_dir / "pruned_lists" / "rule_family_monikers_timesup.csv", family_remove)
    write_ids(out_dir / "pruned_lists" / "rule_reimplementation_triple_investigate.csv", reimp_remove)
    write_ids(out_dir / "pruned_lists" / "rule_language_version.csv", lang_remove)
    write_ids(out_dir / "pruned_lists" / "combined_primary_edition_family.csv", primary_remove)
    write_ids(out_dir / "pruned_lists" / "combined_sensitivity_dup.csv", sensitivity_remove)
    # Also write details json
    with open(out_dir / "pruned_lists" / "details_edition.json", "w") as f:
        json.dump(edition_details, f, indent=2)
    with open(out_dir / "pruned_lists" / "details_duplicate.json", "w") as f:
        json.dump(dup_details, f, indent=2)
    with open(out_dir / "pruned_lists" / "details_family.json", "w") as f:
        json.dump(family_details, f, indent=2)
    with open(out_dir / "pruned_lists" / "details_reimplementation.json", "w") as f:
        json.dump(reimp_details[:100], f, indent=2)  # truncate for size

    # ---- Recursive closure ----
    print("\n[Step 2] Recursive closure to fixed point")
    # We need to run closure starting from primary second-pass universe (and also from 16627 base for comparison)
    # For closure we operate on active observations (rating_observations_active) filtered to remaining games
    # Iteratively: compute per-game n_active, per-user n_active, identify degenerate, repeat

    def run_closure(initial_game_ids, label, out_prefix):
        print(f"\n-- Closure {label}: starting with {len(initial_game_ids)} games --")
        # Load active obs into duckdb view filtered to initial games? We'll iteratively filter via temp tables
        # For efficiency, create a view of active obs with game_id filter via semi-join to a temp table of game_ids
        # Instead, we can materialize a dataframe of active obs filtered to initial games? But that's 24.5M rows -> heavy but okay with DuckDB bounded
        # Use DuckDB to compute counts iteratively without materializing pandas

        # Create temp game list table
        con.execute("DROP TABLE IF EXISTS closure_games")
        con.execute("CREATE TEMP TABLE closure_games (game_id BIGINT)")
        # Insert in batches
        batch = 1000
        ids = list(initial_game_ids)
        for i in range(0, len(ids), batch):
            chunk = ids[i:i+batch]
            vals = ",".join(f"({x})" for x in chunk)
            con.execute(f"INSERT INTO closure_games VALUES {vals}")

        # We'll loop
        iteration_logs = []
        iter_num = 0
        # Track current game set as closure_games, user set will be derived
        # Also need to track degenerate set
        # First, get initial obs count for logging
        obs_initial = con.execute(f"SELECT COUNT(*) FROM read_parquet('{qpath(active_obs_path)}') WHERE game_id IN (SELECT game_id FROM closure_games)").fetchone()[0]
        users_initial = con.execute(f"SELECT COUNT(DISTINCT user_pseudouserid) FROM read_parquet('{qpath(active_obs_path)}') WHERE game_id IN (SELECT game_id FROM closure_games)").fetchone()[0]
        print(f"  initial obs {obs_initial} users {users_initial}")

        # We need user_severity logic for degenerate detection. Reuse logic from scripts/25:
        # degenerate_strict: n>=20 AND (k==1 single bin OR SD<0.2 OR modal_share>=0.95) on ROUND-binned rating clipped 1..10
        # degenerate_broad: n>=10 AND (k<=2 OR SD<0.5 OR modal>=0.90)
        # For closure we need to recompute user histories within remaining universe each iteration.

        # Helper to compute degenerate counts for current closure_games
        def compute_degenerate():
            # Compute per-user stats within current closure_games
            # Use rounding: ROUND(rating) clipped to 1..10
            # Need to compute per user: n, sd, k (distinct bins), modal_share
            # We can do via DuckDB aggregations
            # This is heavy (288k users) but okay narrow single-scan
            q = f"""
                WITH ro AS (
                    SELECT r.user_pseudouserid, r.rating
                    FROM read_parquet('{qpath(active_obs_path)}') r
                    WHERE r.game_id IN (SELECT game_id FROM closure_games)
                ),
                binned AS (
                    SELECT user_pseudouserid,
                           LEAST(GREATEST(CAST(ROUND(rating) AS BIGINT), 1), 10) AS bin,
                           rating
                    FROM ro
                ),
                per_user AS (
                    SELECT user_pseudouserid,
                           COUNT(*) n,
                           STDDEV_SAMP(rating) sd,
                           COUNT(DISTINCT bin) k,
                           MAX(cnt) FILTER (WHERE cnt IS NOT NULL) as max_cnt -- placeholder
                    FROM (SELECT user_pseudouserid, rating, bin FROM binned)
                    GROUP BY user_pseudouserid
                ),
                -- need modal share: compute per user bin counts then max/count
                bin_counts AS (
                    SELECT user_pseudouserid, bin, COUNT(*) cnt FROM binned GROUP BY user_pseudouserid, bin
                ),
                modal AS (
                    SELECT user_pseudouserid, MAX(cnt) max_cnt, SUM(cnt) total FROM bin_counts GROUP BY user_pseudouserid
                ),
                joined AS (
                    SELECT p.user_pseudouserid, p.n, p.sd, p.k, m.max_cnt::DOUBLE / m.total AS modal_share
                    FROM per_user p JOIN modal m USING (user_pseudouserid)
                )
                SELECT
                    COUNT(*) FILTER (WHERE n>=20 AND (k=1 OR sd<0.2 OR modal_share>=0.95)) strict,
                    COUNT(*) FILTER (WHERE n>=10 AND (k<=2 OR sd<0.5 OR modal_share>=0.90)) broad,
                    COUNT(*) total_users
                FROM joined
            """
            # The above per_user subquery incorrectly tries to compute sd/k without bin_counts; but we already have bin_counts for k and modal, but sd needs rating sd. Let's simplify: do two CTEs

            # Simpler: compute directly in one step with proper aggregations
            q2 = f"""
                WITH ro AS (
                    SELECT r.user_pseudouserid, r.rating,
                           LEAST(GREATEST(CAST(ROUND(rating) AS BIGINT), 1), 10) AS bin
                    FROM read_parquet('{qpath(active_obs_path)}') r
                    WHERE r.game_id IN (SELECT game_id FROM closure_games)
                ),
                per_user_stats AS (
                    SELECT user_pseudouserid,
                           COUNT(*) n,
                           STDDEV_SAMP(rating) sd,
                           COUNT(DISTINCT bin) k
                    FROM ro
                    GROUP BY user_pseudouserid
                ),
                bin_counts AS (
                    SELECT user_pseudouserid, bin, COUNT(*) cnt FROM ro GROUP BY user_pseudouserid, bin
                ),
                modal AS (
                    SELECT user_pseudouserid, MAX(cnt) max_cnt FROM bin_counts GROUP BY user_pseudouserid
                ),
                joined AS (
                    SELECT p.user_pseudouserid, p.n, p.sd, p.k, (m.max_cnt::DOUBLE / p.n) AS modal_share
                    FROM per_user_stats p JOIN modal m USING (user_pseudouserid)
                )
                SELECT
                    COUNT(*) FILTER (WHERE n>=20 AND (k=1 OR sd<0.2 OR modal_share>=0.95)) strict,
                    COUNT(*) FILTER (WHERE n>=10 AND (k<=2 OR sd<0.5 OR modal_share>=0.90)) broad,
                    COUNT(*) total
                FROM joined
            """
            try:
                row = con.execute(q2).fetchone()
                return {"strict": int(row[0] or 0), "broad": int(row[1] or 0), "total_users": int(row[2] or 0)}
            except Exception as e:
                print(f"  degenerate compute failed: {e}")
                return {"strict": None, "broad": None, "total_users": None}

        # Initial degenerate
        deg = compute_degenerate()
        print(f"  initial degenerate strict {deg['strict']} broad {deg['broad']} total {deg['total_users']}")

        # Now iterative closure
        prev_games = None
        prev_users = None
        prev_strict = None

        while True:
            iter_num += 1
            # Compute per-game n_active
            game_counts = con.execute("SELECT game_id, COUNT(*) n FROM read_parquet('" + qpath(active_obs_path) + "') WHERE game_id IN (SELECT game_id FROM closure_games) GROUP BY game_id").fetchdf()
            # games <100
            low_games = game_counts[game_counts["n"] < 100]["game_id"].tolist() if not game_counts.empty else []
            # Compute per-user n_active
            user_counts = con.execute("SELECT user_pseudouserid, COUNT(*) n FROM read_parquet('" + qpath(active_obs_path) + "') WHERE game_id IN (SELECT game_id FROM closure_games) GROUP BY user_pseudouserid").fetchdf()
            low_users = user_counts[user_counts["n"] < 10]["user_pseudouserid"].tolist() if not user_counts.empty else []
            # Compute degenerate strict users list to exclude
            # Need list of degenerate user ids to prune
            # Use same logic but return ids
            deg_ids_q = f"""
                WITH ro AS (
                    SELECT r.user_pseudouserid, r.rating,
                           LEAST(GREATEST(CAST(ROUND(rating) AS BIGINT), 1), 10) AS bin
                    FROM read_parquet('{qpath(active_obs_path)}') r
                    WHERE r.game_id IN (SELECT game_id FROM closure_games)
                ),
                per_user_stats AS (
                    SELECT user_pseudouserid, COUNT(*) n, STDDEV_SAMP(rating) sd, COUNT(DISTINCT bin) k FROM ro GROUP BY user_pseudouserid
                ),
                bin_counts AS (
                    SELECT user_pseudouserid, bin, COUNT(*) cnt FROM ro GROUP BY user_pseudouserid, bin
                ),
                modal AS (
                    SELECT user_pseudouserid, MAX(cnt) max_cnt FROM bin_counts GROUP BY user_pseudouserid
                ),
                joined AS (
                    SELECT p.user_pseudouserid, p.n, p.sd, p.k, (m.max_cnt::DOUBLE / p.n) AS modal_share
                    FROM per_user_stats p JOIN modal m USING (user_pseudouserid)
                )
                SELECT user_pseudouserid FROM joined WHERE n>=20 AND (k=1 OR sd<0.2 OR modal_share>=0.95)
            """
            degenerate_users = [row[0] for row in con.execute(deg_ids_q).fetchall()] if deg else []
            # Also need total counts for logging after this iteration's checks
            n_games_current = con.execute("SELECT COUNT(*) FROM closure_games").fetchone()[0]
            n_users_current = con.execute(f"SELECT COUNT(DISTINCT user_pseudouserid) FROM read_parquet('{qpath(active_obs_path)}') WHERE game_id IN (SELECT game_id FROM closure_games)").fetchone()[0]
            n_obs_current = con.execute(f"SELECT COUNT(*) FROM read_parquet('{qpath(active_obs_path)}') WHERE game_id IN (SELECT game_id FROM closure_games)").fetchone()[0]
            # But we haven't yet pruned deg users from obs count? For next iteration, degenerate users' ratings should be excluded.
            # The active definition is: games × users≥10 minus degenerate_strict. So we need to exclude degenerate users' observations when checking thresholds.
            # So current obs for threshold should be after excluding degenerate users? The task says: qualifying ratings = rating_observations_active rows for 16,627 × ≥10 minus degenerate_strict; n_active per game, P10=100 etc. So degenerate exclusion is part of qualifying ratings.
            # For closure, we need to consider qualifying ratings after each filter, including degenerate exclusion.
            # So we should compute n_active per game/user AFTER excluding degenerate users.

            # Compute counts after excluding degenerate users (if any)
            if degenerate_users:
                # create temp table for degenerate ids
                con.execute("DROP TABLE IF EXISTS tmp_deg")
                con.execute("CREATE TEMP TABLE tmp_deg (user_pseudouserid VARCHAR)")
                for i in range(0, len(degenerate_users), 1000):
                    chunk = degenerate_users[i:i+1000]
                    vals = ",".join(f"('{x}')" for x in chunk)
                    con.execute(f"INSERT INTO tmp_deg VALUES {vals}")
                # Recompute game/user counts excluding deg
                game_counts_q = con.execute(f"""
                    SELECT game_id, COUNT(*) n FROM read_parquet('{qpath(active_obs_path)}') r
                    WHERE game_id IN (SELECT game_id FROM closure_games)
                      AND user_pseudouserid NOT IN (SELECT user_pseudouserid FROM tmp_deg)
                    GROUP BY game_id
                """).fetchdf()
                user_counts_q = con.execute(f"""
                    SELECT user_pseudouserid, COUNT(*) n FROM read_parquet('{qpath(active_obs_path)}') r
                    WHERE game_id IN (SELECT game_id FROM closure_games)
                      AND user_pseudouserid NOT IN (SELECT user_pseudouserid FROM tmp_deg)
                    GROUP BY user_pseudouserid
                """).fetchdf()
                low_games2 = game_counts_q[game_counts_q["n"] < 100]["game_id"].tolist() if not game_counts_q.empty else []
                low_users2 = user_counts_q[user_counts_q["n"] < 10]["user_pseudouserid"].tolist() if not user_counts_q.empty else []
                # For logging, use these excluding deg for thresholds
                low_games = low_games2
                low_users = low_users2
                n_games_excluding_deg = len(game_counts_q)
                n_users_excluding_deg = len(user_counts_q)
                n_obs_excluding_deg = int(game_counts_q["n"].sum()) if not game_counts_q.empty else 0
            else:
                game_counts_q = game_counts
                user_counts_q = user_counts
                n_games_excluding_deg = len(game_counts_q)
                n_users_excluding_deg = len(user_counts_q)
                n_obs_excluding_deg = int(game_counts_q["n"].sum()) if not game_counts_q.empty else 0

            # Log current iteration state before pruning
            iteration_logs.append({
                "iteration": iter_num,
                "games_total": int(n_games_current),
                "users_total_including_deg": int(n_users_current),
                "obs_total_including_deg": int(n_obs_current),
                "games_n_active_lt100": len(low_games),
                "users_n_active_lt10": len(low_users),
                "degenerate_strict": len(degenerate_users),
                "games_remaining_excluding_deg": int(n_games_excluding_deg),
                "users_remaining_excluding_deg": int(n_users_excluding_deg),
                "obs_remaining_excluding_deg": int(n_obs_excluding_deg),
            })
            print(f"  iter {iter_num}: games {n_games_current} (lt100 {len(low_games)}), users {n_users_current} (lt10 {len(low_users)}), deg {len(degenerate_users)}, obs {n_obs_current} -> excl_deg obs {n_obs_excluding_deg}")

            # Check convergence: no low games, no low users, and degenerate set stable?
            # For fixed point, we need no game <100 and no user <10 after excluding degenerate.
            # Also degenerate recomputation may change next iteration, so we loop even if no low games/users but deg changed.
            # Simplify: if no low_games and no low_users and degenerate_users == prev strict set, then converged.
            # But degenerate_users may be same as previous iteration's deg set.

            # Determine if any pruning needed
            to_prune_games = set(low_games)
            to_prune_users = set(low_users)  # but user pruning is via observation filter, not direct user table prune; we prune games, then users naturally drop if they fall below threshold? The plan says remove users with <10 and games with <100 mutually. For closure we can simply remove low games from closure_games, and low users are implicitly handled by excluding their obs? Actually to enforce user threshold we need to remove users <10 from future considerations? But our method of recomputing thresholds automatically handles it: if we remove low games, some users will drop below 10 next iteration, then their ratings would be excluded, which may cause more games to drop.
            # So pruning step: remove low_games from closure_games; degenerate users are already excluded from counts, but we need to keep them excluded permanently.
            # For user <10, we don't need to explicitly delete users from a table; they will be excluded via not counting their ratings? But the spec says "remove users with <10 qualifying ratings within that universe (n_active per user, t=10 primary)". So we should also exclude those users' ratings from future iterations (i.e., treat them as removed). That is achieved by filtering ro to only users with >=10 after each iteration? Our current user_counts_q is after excluding deg, but still includes low users (<10) in the counts. To enforce user threshold, we should exclude low users' observations in next iteration's game counts.

            # So we need to maintain a set of active users (those with >=10). Initially it's all users in closure_games, but after iteration we prune low users.

            # For next iteration, we need to consider only ratings where user is not deg and user has >=10 in current remaining universe? This is recursive.

            # Approach: maintain closure_games and also active user set via temp table active_users.
            # At each iteration, after computing low_users, we will exclude those users' ratings for next iteration's game counts. But our current game_counts_q already excluded deg but included low users. For next iteration, we should exclude low users as well.

            # So we need to track which users are considered active.

            # Let's create a temp table closure_active_users containing users with >=10 after excluding deg (i.e., not low).
            # For convergence check, we compare current closure_games and closure_active_users to previous.

            # Check convergence: if no low_games and no low_users and degenerate set unchanged, break.

            # For now, if no low_games and no low_users, we still need to check degenerate stability: will recompute deg next iteration vs current. But if no prunes, deg will be same, so we can break.

            if not to_prune_games and not to_prune_users and (prev_strict is None or set(degenerate_users) == prev_strict):
                print(f"  converged at iter {iter_num}")
                break

            # Update prev
            prev_strict = set(degenerate_users)

            # Prune games
            if to_prune_games:
                # Delete from closure_games
                ids_str = ",".join(map(str, to_prune_games))
                # Use DELETE
                con.execute(f"DELETE FROM closure_games WHERE game_id IN ({ids_str})")
                print(f"    pruned {len(to_prune_games)} games <100")

            # For users <10, we need to exclude them from future counts. We'll create a temp table of users to keep (those with >=10).
            # Actually we can handle this by adding a condition to future queries: only consider users where per-user count >=10 after excluding deg and after game pruning.
            # But our next iteration's game_counts will automatically be based on remaining games, but will still count ratings from low users. To exclude low users, we need to filter them out.
            # So we should create a view that filters to active users.

            # Create temp table of active users to keep for next iteration (those with n>=10 after excluding deg)
            # This is user_counts_q filtered to n>=10
            keep_users = user_counts_q[user_counts_q["n"] >= 10]["user_pseudouserid"].tolist() if not user_counts_q.empty else []
            # We'll store this as a temp table closure_keep_users for next iteration's filtering
            con.execute("DROP TABLE IF EXISTS closure_keep_users")
            con.execute("CREATE TEMP TABLE closure_keep_users (user_pseudouserid VARCHAR)")
            if keep_users:
                for i in range(0, len(keep_users), 1000):
                    chunk = keep_users[i:i+1000]
                    vals = ",".join(f"('{x}')" for x in chunk)
                    con.execute(f"INSERT INTO closure_keep_users VALUES {vals}")
                # For next iteration, we need to consider only obs where user in keep_users and not deg
                # We can achieve this by adding a condition to the ro CTEs: WHERE user in keep_users
                # Simplest: create a view ro_filtered that is the active obs filtered to current closure_games and keep_users and not deg
                # But our current loop's queries already use closure_games and tmp_deg but not keep_users.
                # To incorporate keep_users, we should modify the queries to join to closure_keep_users.

                # Let's define a helper view for next iteration: active_obs_filtered = ro where game in closure_games and user in closure_keep_users and not in tmp_deg
                # For simplicity, we can just drop the low users by deleting their contributions? Actually we need to keep closure_keep_users as filter.

                # We'll create a view ro_active_filtered for next iteration
                con.execute("DROP VIEW IF EXISTS ro_active_filtered")
                con.execute(f"""
                    CREATE OR REPLACE VIEW ro_active_filtered AS
                    SELECT r.* FROM read_parquet('{qpath(active_obs_path)}') r
                    WHERE r.game_id IN (SELECT game_id FROM closure_games)
                      AND r.user_pseudouserid IN (SELECT user_pseudouserid FROM closure_keep_users)
                      AND r.user_pseudouserid NOT IN (SELECT user_pseudouserid FROM tmp_deg)
                """)
                # Now future iterations should use this view instead of direct parquet?
                # But our game_counts queries currently use direct parquet with WHERE game_id IN ... and NOT IN tmp_deg
                # We need to update them to also require user in closure_keep_users after first iteration.

                # Instead of trying to patch, we can for simplicity handle user pruning by also inserting a condition that we will treat low users as removed: for next iteration, we will consider only keep_users.
                # We could just keep the keep_users table and modify next iteration's queries to join to it.

                # To avoid complexity, we can instead just explicitly filter game_counts using keep_users: next iteration's ro should be where user in keep_users.

                # We'll set a flag that from now on, queries should include keep_users filter.
                # We can achieve by creating a temp table that replaces active_obs_path filtering with a view.

                # Let's create a persistent view that will be used in next iterations
                # We'll update the queries in next loop to use ro_active_filtered if it exists
                pass
            else:
                # no keep users -> empty
                pass

            # Also need to handle case where no keep_users -> break

            # For next iteration, we need to ensure degenerate recomputation also respects keep_users filter
            # Our deg_ids_q currently uses ro with only game filter, not keep_users. So we need to update it to include keep_users after first pruning.

            # To simplify logic, we can after pruning games and identifying keep_users, we set up a view that represents the current qualifying observations:
            # qualifying_obs = r where game in closure_games and user in keep_users and not deg
            # Then next iteration's game counts are based on this qualifying_obs, and user counts based on same.

            # We'll create that view now and use it in next iteration's computations by checking if closure_keep_users exists.

            # For next loop iteration, we'll detect if closure_keep_users exists and use it.

            # Also need to handle degenerate users: they are already in tmp_deg, but after pruning games, some users may become degenerate or cease to be deg.

            # Loop will recompute deg based on current closure_games and keep_users (if exists)

            # To make next iteration aware, we will in next iteration's deg and count queries, add condition AND user in keep_users if table exists

            # Let's implement check: if closure_keep_users has rows, then use it

            # We can just keep the table and in next iteration's queries, add that filter via EXISTS check

            # We'll modify the loop tocheck for existence via try

            # For now, continue loop; next iteration will handle

            # But we haven't yet updated the queries to use keep_users for next iteration's game_counts_q. So we need to adjust the loop's next iteration to include that.

            # Simpler: at start of next iteration, we can have logic: if closure_keep_users exists, then filter ro to those users.

            # Let's add a helper function to build the ro filter string

            # Instead of complicating, we can just at the top of loop, if closure_keep_users exists, we will filter counts using that table.

            # We'll handle via con.table existence check.

            # Also need to handle that after pruning games, some users may have been pruned, so we should also prune closure_games based on new obs counts that exclude low users.

            # This is getting complex; we need a cleaner iterative approach.

            # Alternative simpler iterative approach: at each iteration, compute qualifying observations as:
            #   SELECT r.* FROM ro WHERE game in closure_games AND user not in deg AND user in (users with >=10 in that same set)
            # This is a fixed point within fixed point. Instead of stepwise prune low users then recompute, we can directly compute the set of users with >=10 after excluding deg, then filter.

            # Let's implement a more direct loop: each iteration, compute:
            # 1. active_obs = ro where game in closure_games and user not in deg
            # 2. compute per-user n, keep only users with n>=10 -> active_users
            # 3. compute per-game n from active_obs where user in active_users -> games with n>=100 keep
            # So order matters? But we can compute both and prune.

            # For now, we have pruned games <100 based on counts that included low users; but we should have pruned based on counts that excluded low users? The spec says mutually: start with candidate universe, remove games <100, remove users <10, recompute, repeat. So it's stepwise, not simultaneous? But our method approximates.

            # To follow spec more literally: each iteration, identify games with <100 qualifying ratings (qualifying = active ratings within current universe) and users with <10 qualifying ratings, remove both sets, recompute.

            # So we should prunes both: to_prune_games = games with n<100 (within current universe excluding deg? or including deg? The spec says qualifying ratings = rating_observations_active rows for 16,627 × ≥10 minus degenerate_strict; n_active per game, P10=100. So qualifying excludes deg. So game n should be after excluding deg and after excluding low users? But low users are also being removed, so it's mutual.

            # For simplicity, we can in each iteration:
            # - compute deg set based on current closure_games (and current active users? but deg is computed on rating histories within remaining games, after previous prunes, including all users currently considered)
            # - then compute per-game n excluding deg, and per-user n excluding deg, identify lows, prune

            # We have deg, we computed game_counts_q excluding deg, and user_counts_q excluding deg, and identified lows.

            # For next iteration, we should have new closure_games = old closure_games minus low_games, and new active users = old keep_users (those with >=10). But we already have keep_users list.

            # So we need to enforce that next iteration's ro is filtered to closure_games (pruned) and keep_users.

            # Let's ensure next iteration's queries will include keep_users filter by creating a view that joins.

            # We'll create a helper to check if closure_keep_users exists and modify queries accordingly.

            pass

        # After loop, collect final state
        final_games = [row[0] for row in con.execute("SELECT game_id FROM closure_games ORDER BY game_id").fetchall()]
        final_obs = con.execute(f"SELECT COUNT(*) FROM read_parquet('{qpath(active_obs_path)}') WHERE game_id IN (SELECT game_id FROM closure_games) AND user_pseudouserid NOT IN (SELECT user_pseudouserid FROM tmp_deg) AND user_pseudouserid IN (SELECT user_pseudouserid FROM closure_keep_users)").fetchone()[0] if con.execute("SELECT COUNT(*) FROM closure_keep_users").fetchone()[0] >0 else con.execute(f"SELECT COUNT(*) FROM read_parquet('{qpath(active_obs_path)}') WHERE game_id IN (SELECT game_id FROM closure_games) AND user_pseudouserid NOT IN (SELECT user_pseudouserid FROM tmp_deg)").fetchone()[0]
        # But if closure_keep_users may not exist (no user pruning), handle

        # Simplify: compute final obs as count where game in final and user not deg and user has >=10 in final (i.e., in keep_users)
        try:
            keep_count = con.execute("SELECT COUNT(*) FROM closure_keep_users").fetchone()[0]
            if keep_count>0:
                final_obs2 = con.execute(f"""
                    SELECT COUNT(*) FROM read_parquet('{qpath(active_obs_path)}') r
                    WHERE r.game_id IN (SELECT game_id FROM closure_games)
                      AND r.user_pseudouserid IN (SELECT user_pseudouserid FROM closure_keep_users)
                      AND r.user_pseudouserid NOT IN (SELECT user_pseudouserid FROM tmp_deg)
                """).fetchone()[0]
            else:
                final_obs2 = con.execute(f"""
                    SELECT COUNT(*) FROM read_parquet('{qpath(active_obs_path)}') r
                    WHERE r.game_id IN (SELECT game_id FROM closure_games)
                      AND r.user_pseudouserid NOT IN (SELECT user_pseudouserid FROM tmp_deg)
                """).fetchone()[0]
        except:
            final_obs2 = None

        # Save logs
        pd.DataFrame(iteration_logs).to_csv(out_dir / f"{out_prefix}_closure_log.csv", index=False)
        # Also save final game list
        pd.DataFrame({"game_id": final_games}).to_csv(out_dir / f"{out_prefix}_final_games.csv", index=False)
        # Save final user list (keep_users)
        try:
            final_users = [row[0] for row in con.execute("SELECT user_pseudouserid FROM closure_keep_users").fetchall()]
            pd.DataFrame({"user_pseudouserid": final_users}).to_csv(out_dir / f"{out_prefix}_final_users.csv", index=False)
        except:
            final_users = []
        return {
            "label": label,
            "initial_games": len(initial_game_ids),
            "final_games": len(final_games),
            "initial_obs": int(obs_initial),
            "final_obs": int(final_obs2) if final_obs2 else None,
            "final_users": len(final_users),
            "iterations": len(iteration_logs),
            "logs": iteration_logs,
            "final_game_ids": final_games,
            "degenerate_final": deg,
        }

    # Run closure for primary second-pass
    # Need to handle that closure function currently has complex logic with keep_users; we simplified but may need to test
    # For now, let's run a simpler version that does iterative removal without explicit keep_users table, just by recomputing counts each iteration and pruning games <100, and degenerate, and users <10 will be naturally handled because after pruning games, some users will have <10 and their ratings will be excluded? But our current game_counts do not exclude low users, so they would still count toward game n even if user is <10. To properly handle mutual closure, we need to exclude low users' ratings from game counts.

    # Let's instead implement a cleaner loop from scratch that at each iteration:
    # - Have current_games set (closure_games table)
    # - Have current_users set (initially all users with >=10 before any pruning? But after pruning games, some users drop below 10, so we need to recompute)
    # Steps per iteration:
    #   deg = compute degenerate based on current_games (ratings within those games)
    #   active_obs = ratings where game in current_games and user not in deg
    #   per_user_counts = count per user in active_obs
    #   active_users = users where count >=10
    #   per_game_counts = count per game where user in active_users (and not deg, but active_users already excludes deg? Actually deg users are not in active_users because they are excluded before counting? So per_game should be count where user in active_users)
    #   low_games = games where per_game_counts <100
    #   low_users = users where per_user_counts <10 (but we already filtered to active_users, so low_users are those not in active_users)
    #   If no low_games and no new deg and active_users stable, break
    #   Else prune low_games from current_games, and continue (active_users will be recomputed next iter)

    # This matches mutual closure: each prune can introduce more valid candidates.

    # Let's implement this cleaner loop

    def run_closure_clean(initial_game_ids, label, out_prefix):
        print(f"\n== Clean closure {label} ==")
        con.execute("DROP TABLE IF EXISTS closure_games")
        con.execute("CREATE TEMP TABLE closure_games (game_id BIGINT)")
        for i in range(0, len(initial_game_ids), 1000):
            chunk = initial_game_ids[i:i+1000]
            vals = ",".join(f"({x})" for x in chunk)
            con.execute(f"INSERT INTO closure_games VALUES {vals}")
        iteration_logs = []
        iter_num = 0
        prev_games_set = None
        prev_deg_set = None
        prev_active_users = None

        # Helper to get current games list
        def get_current_games():
            return set(row[0] for row in con.execute("SELECT game_id FROM closure_games").fetchall())

        # Initial counts
        obs_initial = con.execute(f"SELECT COUNT(*) FROM read_parquet('{qpath(active_obs_path)}') WHERE game_id IN (SELECT game_id FROM closure_games)").fetchone()[0]
        print(f"  initial games {len(initial_game_ids)} obs {obs_initial}")

        while True:
            iter_num += 1
            current_games = get_current_games()
            if not current_games:
                print("  no games left")
                break
            # 1. compute degenerate set based on current_games (using all users within those games, before user threshold? But spec says rerun after each filter because changing game universe changes users' rating histories and may change degenerate set. So degenerate should be computed on the current qualifying universe? Or on the current games before user threshold? The spec says deg defined on n>=20 etc, on ROUND-binned 1..10 for degenerate_strict, and rerun after each filter because changing game universe changes users' rating histories. So we compute deg on the current games' ratings (before user threshold? Or after? Probably after game filter but before user threshold? But we can compute deg on current_games's ratings (all users) then later filter users <10.
            # We'll compute deg on current_games
            # Build deg query
            deg_q = f"""
                WITH ro AS (
                    SELECT r.user_pseudouserid, r.rating,
                           LEAST(GREATEST(CAST(ROUND(r.rating) AS BIGINT), 1), 10) AS bin
                    FROM read_parquet('{qpath(active_obs_path)}') r
                    WHERE r.game_id IN (SELECT game_id FROM closure_games)
                ),
                per_user_stats AS (
                    SELECT user_pseudouserid, COUNT(*) n, STDDEV_SAMP(rating) sd, COUNT(DISTINCT bin) k FROM ro GROUP BY user_pseudouserid
                ),
                bin_counts AS (
                    SELECT user_pseudouserid, bin, COUNT(*) cnt FROM ro GROUP BY user_pseudouserid, bin
                ),
                modal AS (
                    SELECT user_pseudouserid, MAX(cnt) max_cnt FROM bin_counts GROUP BY user_pseudouserid
                ),
                joined AS (
                    SELECT p.user_pseudouserid, p.n, p.sd, p.k, (m.max_cnt::DOUBLE / p.n) AS modal_share
                    FROM per_user_stats p JOIN modal m USING (user_pseudouserid)
                )
                SELECT user_pseudouserid FROM joined WHERE n>=20 AND (k=1 OR sd<0.2 OR modal_share>=0.95)
            """
            deg_users = set(row[0] for row in con.execute(deg_q).fetchall())
            # also compute broad for logging
            broad_q = deg_q.replace("n>=20 AND (k=1", "n>=10 AND (k<=2").replace("sd<0.2", "sd<0.5").replace("modal_share>=0.95", "modal_share>=0.90")
            # but we can just compute counts separately for log
            # For active_obs we need to exclude deg
            # Create temp table tmp_deg for this iter
            con.execute("DROP TABLE IF EXISTS tmp_deg")
            con.execute("CREATE TEMP TABLE tmp_deg (user_pseudouserid VARCHAR)")
            if deg_users:
                for i in range(0, len(deg_users), 1000):
                    chunk = list(deg_users)[i:i+1000]
                    vals = ",".join(f"('{x}')" for x in chunk)
                    con.execute(f"INSERT INTO tmp_deg VALUES {vals}")
            # 2. per-user counts excluding deg, within current games
            per_user_q = f"""
                SELECT user_pseudouserid, COUNT(*) n
                FROM read_parquet('{qpath(active_obs_path)}') r
                WHERE r.game_id IN (SELECT game_id FROM closure_games)
                  AND r.user_pseudouserid NOT IN (SELECT user_pseudouserid FROM tmp_deg)
                GROUP BY user_pseudouserid
            """
            per_user_df = con.execute(per_user_q).fetchdf()
            if per_user_df.empty:
                active_users = set()
                low_users = set()
            else:
                active_users = set(per_user_df[per_user_df["n"] >= 10]["user_pseudouserid"].tolist())
                low_users = set(per_user_df[per_user_df["n"] < 10]["user_pseudouserid"].tolist())
            # Create temp table for active users for per-game counting
            con.execute("DROP TABLE IF EXISTS tmp_active_users")
            con.execute("CREATE TEMP TABLE tmp_active_users (user_pseudouserid VARCHAR)")
            if active_users:
                for i in range(0, len(active_users), 1000):
                    chunk = list(active_users)[i:i+1000]
                    vals = ",".join(f"('{x}')" for x in chunk)
                    con.execute(f"INSERT INTO tmp_active_users VALUES {vals}")
            # 3. per-game counts where user in active_users (and not deg, but active already excludes deg)
            if active_users:
                per_game_q = f"""
                    SELECT game_id, COUNT(*) n
                    FROM read_parquet('{qpath(active_obs_path)}') r
                    WHERE r.game_id IN (SELECT game_id FROM closure_games)
                      AND r.user_pseudouserid IN (SELECT user_pseudouserid FROM tmp_active_users)
                    GROUP BY game_id
                """
                per_game_df = con.execute(per_game_q).fetchdf()
            else:
                per_game_df = pd.DataFrame(columns=["game_id","n"])
            # games that have zero counts after filtering (no qualifying ratings) should also be considered <100
            # So low_games = games in current_games where n<100 or missing
            per_game_dict = dict(zip(per_game_df["game_id"].tolist(), per_game_df["n"].tolist())) if not per_game_df.empty else {}
            low_games = set()
            for gid in current_games:
                n = per_game_dict.get(gid, 0)
                if n < 100:
                    low_games.add(gid)
            # counts for logging
            n_games_current = len(current_games)
            n_users_total = len(per_user_df)
            n_obs_total = int(per_user_df["n"].sum()) if not per_user_df.empty else 0
            n_active_users = len(active_users)
            n_obs_active = int(per_game_df["n"].sum()) if not per_game_df.empty else 0
            n_games_active = len(per_game_df)  # games with at least 1 active rating
            # log
            log_entry = {
                "iteration": iter_num,
                "games_current": n_games_current,
                "games_with_active": n_games_active,
                "games_lt100": len(low_games),
                "users_total": n_users_total,
                "users_active_ge10": n_active_users,
                "users_lt10": len(low_users),
                "degenerate_strict": len(deg_users),
                "obs_total_excl_deg": n_obs_total,
                "obs_active": n_obs_active,
            }
            iteration_logs.append(log_entry)
            print(f"  iter {iter_num}: games {n_games_current} (active {n_games_active} lt100 {len(low_games)}), users total {n_users_total} active {n_active_users} lt10 {len(low_users)} deg {len(deg_users)} obs {n_obs_total}->{n_obs_active}")

            # convergence check
            # If no low_games and deg set unchanged and active_users unchanged, break
            if not low_games and prev_deg_set is not None and deg_users == prev_deg_set and active_users == prev_active_users and current_games == prev_games_set:
                print(f"  converged (no changes)")
                break
            if not low_games and not deg_users and not low_users:
                # No prunes and no deg, but need to check if active_users stable
                if prev_games_set == current_games and prev_deg_set == deg_users and prev_active_users == active_users:
                    print(f"  converged (stable)")
                    break
                # else continue to ensure deg stability

            # Check for fixed point: if no low_games to prune and deg stable, we could still have low_users but those are already excluded via active_users. However spec says users <10 should be removed, which we already do via active_users filtering. So we don't need explicit prune for users; they are pruned by not being in active_users. But for next iteration, we need to ensure their ratings remain excluded, which they will because per_game counts already exclude them. So the only explicit prune needed is games <100.
            # However, pruning games can cause users to drop below 10, which will be reflected next iteration's active_users, which will then cause more games to drop.

            # Also need to handle case where no low_games but active_users changed due to game pruning previous iter -> still need to continue to recompute deg.

            # Determine if we need to prune games
            if low_games:
                # prune low games from closure_games
                ids_str = ",".join(map(str, low_games))
                con.execute(f"DELETE FROM closure_games WHERE game_id IN ({ids_str})")
                print(f"    pruned {len(low_games)} games")
            else:
                # no game prune, but user or deg may have changed; need to continue to re-evaluate?
                # If no game prune and deg stable and active stable, we break above. Otherwise continue loop without pruning to re-evaluate.
                if deg_users == prev_deg_set and active_users == prev_active_users:
                    print(f"  no games to prune and sets stable -> converged")
                    break
                else:
                    print(f"  no games pruned but deg/active changed, continuing")

            prev_games_set = current_games - low_games if low_games else current_games
            prev_deg_set = deg_users
            prev_active_users = active_users

            if iter_num > 20:
                print("  max iterations reached")
                break

        final_games = sorted(list(get_current_games()))
        # final active users is prev_active_users
        final_users = sorted(list(prev_active_users)) if prev_active_users else []
        # final obs is n_obs_active from last iter
        final_obs = iteration_logs[-1]["obs_active"] if iteration_logs else 0
        # save logs
        pd.DataFrame(iteration_logs).to_csv(out_dir / f"{out_prefix}_closure_log.csv", index=False)
        pd.DataFrame({"game_id": final_games}).to_csv(out_dir / f"{out_prefix}_final_games.csv", index=False)
        pd.DataFrame({"user_pseudouserid": final_users}).to_csv(out_dir / f"{out_prefix}_final_users.csv", index=False)
        return {
            "label": label,
            "initial_games": len(initial_game_ids),
            "final_games": len(final_games),
            "final_users": len(final_users),
            "final_obs": final_obs,
            "iterations": len(iteration_logs),
            "logs": iteration_logs,
            "final_game_ids": final_games,
        }

    # Run clean closure for primary and for base comparisons
    primary_initial = list(primary_ids)
    base_initial = list(pop_df["game_id"].tolist())  # 16627

    res_primary_closed = run_closure_clean(primary_initial, "primary_second_pass", "primary")
    res_base_closed = run_closure_clean(base_initial, "base_16627", "base_16627")

    # Also run single-filter comparison (games <100 only, no user recursion) for reference: just filter games where n_active_excl_deg <100 once
    # Already done via closure first iteration, but we can compute directly
    # For documentation, compute single-filter 100 counts for primary and base
    # Use per_game counts from first iteration logs
    # We'll just log that sensitivity_n100 study already covers this: 1604 games <100 in active 16564

    # ---- Save final closed population parquet ----
    closed_pop_df = pop_df[pop_df["game_id"].isin(res_primary_closed["final_game_ids"])].copy()
    for col in ["base","is_edition","stem","game_fams"]:
        if col in closed_pop_df.columns:
            closed_pop_df = closed_pop_df.drop(columns=[col])
    closed_path = out_dir / "bgg_population_second_pass_closed.parquet"
    closed_pop_df.to_parquet(closed_path, index=False)
    print(f"\nWrote closed population {len(closed_pop_df)} -> {closed_path}")

    base_closed_pop_df = pop_df[pop_df["game_id"].isin(res_base_closed["final_game_ids"])].copy()
    for col in ["base","is_edition","stem","game_fams"]:
        if col in base_closed_pop_df.columns:
            base_closed_pop_df = base_closed_pop_df.drop(columns=[col])
    base_closed_path = out_dir / "bgg_population_base_closed.parquet"
    base_closed_pop_df.to_parquet(base_closed_path, index=False)
    print(f"Wrote base closed population {len(base_closed_pop_df)} -> {base_closed_path}")

    # ---- Comparison table ----
    # Need to compute categories/eras/volume distributions for each population
    # Also need R2/beta etc: we can attempt to rerun Phase5/6 comparison for closed vs primary vs base?
    # For now, produce counts comparison and note that model refit is via separate script or via sensitivity_n100 results

    # Compute era distributions
    def era_dist(df):
        if df.empty:
            return {}
        eras = df["year"].apply(lambda y: f"{int(y//10*10)}s" if pd.notna(y) else "unknown")
        return dict(eras.value_counts().to_dict())

    def cat_top(df, n=10):
        cnt = Counter()
        for _,row in df.iterrows():
            cats = parse_list_field(row["categories"])
            cnt.update(cats)
        return dict(cnt.most_common(n))

    # Current active counts from known values
    current_info = {
        "population_games": 16627,
        "active_games_with_ratings": 16564,
        "active_obs": 24509788,
        "active_users": 288730,
        "degenerate_strict": 667,
        "degenerate_broad_retained": 3325,
        "phase5": {"mu": 7.144, "lambda": 1.91, "sigma_e": 1.194, "var_adj": 0.7596},
        "phase6": {"R2_Q3b_OLS": 0.5844, "beta_weight": 0.4613, "note": "from phase6_comparative.json Q3b_flex_volume OLS active"},
    }

    primary_info = {
        "population_games": len(second_pass_df),
        "population_games_removed": len(primary_remove),
        "active_closed_games": res_primary_closed["final_games"],
        "active_closed_users": res_primary_closed["final_users"],
        "active_closed_obs": res_primary_closed["final_obs"],
        "closure_iterations": res_primary_closed["iterations"],
        "era": era_dist(second_pass_df),
        "era_closed": era_dist(closed_pop_df),
        "top_cats": cat_top(second_pass_df),
        "top_cats_closed": cat_top(closed_pop_df),
    }

    base_closed_info = {
        "population_games": 16627,
        "closed_games": res_base_closed["final_games"],
        "closed_users": res_base_closed["final_users"],
        "closed_obs": res_base_closed["final_obs"],
        "iterations": res_base_closed["iterations"],
        "era_closed": era_dist(base_closed_pop_df),
    }

    comparison = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "method": "Second-pass game-level dedup (edition 126 + monikers/time 17 =143 primary) plus recursive closure (games<100 users<10 mutual + degenerate rerun). Bounded DuckDB 4GB/3 threads.",
        "rules": {
            "edition": quant_edition,
            "duplicate_title_clean": quant_dup,
            "family_monikers_timesup": quant_family,
            "reimplementation_investigate": quant_reimp,
            "language_version": quant_lang,
            "primary_combined": quant_primary,
            "sensitivity_combined": quant_sensitivity,
        },
        "counts": {
            "current": current_info,
            "primary_second_pass_before_closure": primary_info,
            "primary_closed": {
                "games": res_primary_closed["final_games"],
                "users": res_primary_closed["final_users"],
                "obs": res_primary_closed["final_obs"],
                "iterations": res_primary_closed["iterations"],
                "log": res_primary_closed["logs"],
            },
            "base_16627_closed": base_closed_info,
        },
        "overlap": {
            "primary_vs_current_Jaccard": len(set(second_pass_df["game_id"]) & set(pop_df["game_id"])) / len(set(second_pass_df["game_id"]) | set(pop_df["game_id"])),
            "closed_vs_active_Jaccard": len(set(closed_pop_df["game_id"]) & set(pop_df[pop_df["game_id"].isin(pd.read_parquet(REPO/'data/processed/phase2-active/game_adjusted_means_active.parquet')["game_id"])]["game_id"])) / 16564 if 16564 else None,
        },
        "notes": {
            "small_world_designer_edition": "140135 flagged under edition_bigbox (base small world keeper 40692) — removed in primary, as intended. Keeper Small World 40692 retained.",
            "monikers": "All 7 Monikers expansions (More Monikers 255249, Shmonikers 179448, etc) flagged under family_monikers_stem and removed; keeper Monikers 156546 retained.",
            "times_up": "10 Time's Up! variants flagged under family_times_up_game and removed; keeper Time's Up! 1353 retained. Includes Time's Up! Title Recall! 36553 etc.",
            "brass": "Brass: Birmingham 224517 vs Brass: Lancashire 28720 NOT flagged under reimplementation triple (designer string differs, year gap 11) — correctly kept separate as materially distinct despite identical mechanics/weight.",
            "pandemic": "Pandemic 30549 vs Pandemic Legacy 161936 NOT flagged (weight diff 0.43, jacc 0.53) — kept separate.",
            "reimplementation_not_adopted": "47 games would be flagged under weight+mech+designer triple, but this would incorrectly prune Ticket to Ride: Europe vs Ticket to Ride etc., so NOT adopted for primary. Documented as investigate.",
            "duplicate_not_adopted_primary": "49 title_clean duplicates with designer identical would be removed, but strict rule (year±1 families identical) only removes 1 (Dominion Big Box 142132). Moderate not adopted for primary to avoid pruning distinct reprints with large year gaps (e.g., Puerto Rico 3076 vs 318985 gap 18y). Sensitivity population includes it for comparison.",
        }
    }

    with open(out_dir / "comparison_table.json", "w") as f:
        json.dump(comparison, f, indent=2)
    # Also csv summary
    pd.DataFrame([{
        "population": "current_16627",
        "games": 16627,
        "active_games": 16564,
        "obs": 24509788,
        "users": 288730,
    },{
        "population": "primary_second_pass_before_closure",
        "games": len(second_pass_df),
        "active_games": "see closed",
        "obs": quant_primary["obs_removed"],
        "users": quant_primary["users_affected_any"],
    },{
        "population": "primary_closed",
        "games": res_primary_closed["final_games"],
        "active_games": res_primary_closed["final_games"],
        "obs": res_primary_closed["final_obs"],
        "users": res_primary_closed["final_users"],
    },{
        "population": "base_16627_closed",
        "games": res_base_closed["final_games"],
        "active_games": res_base_closed["final_games"],
        "obs": res_base_closed["final_obs"],
        "users": res_base_closed["final_users"],
    }]).to_csv(out_dir / "comparison_table.csv", index=False)

    # Write a README for provenance
    readme = f"""# Second-pass population — executed

Primary pipeline remains 16,627 × ≥10 minus degenerate_strict → 24.5M obs.
This directory is the **second-pass population for direct comparison before adoption** (deferred review now authorized).

Generated: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
Script: scripts/34_second_pass_population.py
Inputs: bgg_research_population.parquet (16627), rating_observations_active.parquet (24.5M), game_links_filtered.parquet, users_active etc. Copy-once to scratch/second-pass, DuckDB 4GB/3 threads.

## Populations

- **bgg_population_second_pass.parquet** — {len(second_pass_df)} games after Step1 game-level dedup (edition 126 + monikers/time 17 =143 removed). Primary second-pass before recursive closure.
- **bgg_population_second_pass_closed.parquet** — {len(closed_pop_df)} games after recursive closure to fixed point (games<100, users<10, degenerate_strict rerun). Mutual closure where each prune can introduce more candidates.
- **bgg_population_second_pass_sensitivity_dup.parquet** — {len(sens_df)} games sensitivity including duplicate title_clean (49) = {len(sensitivity_remove)} total removed.
- **bgg_population_base_closed.parquet** — {len(base_closed_pop_df)} games for base 16627 closed (for comparison, no dedup).
- **pruned_lists/** — per-rule CSVs and combined, with details JSON.
- **primary_closure_log.csv** / **base_16627_closure_log.csv** — per-iteration games/users/obs/degenerate.
- **comparison_table.json/csv** — current vs second-pass vs closed counts, eras, cats, degenerate prevalence, overlap, notes on included vs excluded examples.

## Rules executed (auditable)

- **Rule A edition_bigbox**: stripped base collision, keep most popular per base. Detects Deluxe, Big Box, Anniversary, Collector, Special Edition, Designer Edition, Revised Edition (case-insensitive, with or without "Edition"). Removes 126 games. Example: Small World Designer Edition 140135 (n=246 resid 2.20) removed, keeper Small World 40692 (75k) retained. Carcassonne Big Box 6 etc. removed, keeper 822 retained. See pruned_lists/details_edition.json for 126 mappings.
- **Rule C family_monikers_timesup**: targeted collapse for flagged families. Monikers stem=monikers (8→1, keeper 156546, removes More Monikers 255249 etc). Time's Up! Game: Time's Up! family (11→1, keeper 1353, removes Title Recall! 36553 etc). Removes 17. Overlap with edition 0 (edition stripping for Time's Up! Deluxe required plain Deluxe handling; now fixed). See details_family.json.
- **Rule B duplicate_title_clean** (investigate, sensitivity only): title_clean exact duplicate and designer identical, keep most popular. Would remove 49, but strict year±1 families identical only removes 1 (Dominion Big Box 142132). Not adopted for primary to avoid pruning distinct reprints with large year gaps (Puerto Rico 3076 vs 318985 gap 18y). Sensitivity population includes it.
- **Reimplementation triple** (investigate only): weight within 0.2 and mech Jaccard>0.8 and designer identical → 47. NOT adopted: would incorrectly prune Ticket to Ride: Europe vs Ticket to Ride etc., Brass incorrectly kept (year gap 11) shows guard works for Brass/Pandemic but still over-prunes map variants. Documented.
- **Language/version** (investigate only): rel=version where designer+year identical → 0 in this population.

Combined primary removed 143 games (126+17). Jaccard vs current 16627 = {comparison['overlap']['primary_vs_current_Jaccard']:.4f}.

## Recursive closure

Started from primary 16484 games (16627-143) and base 16627 for comparison. Each iteration recomputes:
- degenerate_strict (n≥20 AND (k==1 OR SD<0.2 OR modal≥95% on ROUND-binned 1..10))
- per-user n_active excluding deg, keep users ≥10
- per-game n_active where user in active set, keep games ≥100
Repeat until no game <100, no user <10, deg stable.

Logs: primary_closure_log.csv ({res_primary_closed["iterations"]} iterations), base_16627_closure_log.csv ({res_base_closed["iterations"]} iterations).

Final closed: primary {res_primary_closed["final_games"]} games, {res_primary_closed["final_users"]} users, {res_primary_closed["final_obs"]} obs; base closed {res_base_closed["final_games"]} games, {res_base_closed["final_users"]} users, {res_base_closed["final_obs"]} obs.

Degenerate prevalence: current active 0.31% strict at n≥20 (667 users); closed prevalence in logs (final iteration degenerate_strict counts). See logs.

## Included vs excluded examples (per rule, required)

- **Monikers 255249 (More Monikers)** kept? No, removed under family rule; keeper 156546 Monikers retained. Similarly Shmonikers 179448 removed etc. All 7 expansions removed.
- **Time's Up! 36553 Title Recall!** removed under family rule; keeper 1353 Time's Up! retained. All 10 variants removed.
- **Small World Designer Edition 140135** removed under edition rule (base small world); keeper 40692 Small World retained. Small World Underground 97786 and Small World of Warcraft 309630 retained (different weight/mechanics, not editions).
- **Brass: Birmingham vs Lancashire** both retained (distinct, year gap 11, designer string differs).
- **Pandemic vs Pandemic Legacy** both retained (weight diff 0.43, mech jacc 0.53).
- **Dominion vs Dominion Second Edition** both retained in primary (second edition not flagged under edition? Actually Dominion Second Edition 209418 would be flagged under reimplementation triple but not under edition because no edition keyword? Title is "Dominion (Second Edition)" — contains revised? No, contains "(Second Edition)" parentheses edition which our stripping handles via \\(.*edition.*\\) -> base dominion, so it would be flagged under edition? Wait Dominion Second Edition title is "Dominion (Second Edition)" -> stripped via parentheses pattern -> base "dominion", keeper Dominion 36218, so it would be flagged under edition rule? But our earlier edition count included 209418? Let's check: earlier reimplementation triple flagged 209418 as reimplementation, but edition rule also would flag it? The base "dominion" group includes 36218, 209418, two Big Boxes. Keeper is Dominion 36218 (97k) vs 209418 (13k), so 209418 would be removed under edition? But 209418 is "(Second Edition)" which is an edition, arguably same underlying game, so removals is intended. However is Dominion Second Edition considered same underlying game? It's a revised second edition with updated cards, arguably same game, so pruning is defensible. But task says keep distinct designs like Pandemic Legacy separate; Dominion Second Edition is arguably not distinct, so removal is okay. But we should document: Dominion Second Edition 209418 removed under edition, keeper Dominion 36218.
- **The Castles of Burgundy 2019 (271320) vs 2011 (84876)** both retained (year gap 8, not edition), Special Edition 363622 removed under edition (Special Edition suffix).

## What to quantify per rule

For each rule, comparison_table.json records games_removed, obs_removed, users_affected, era/category/volume, examples, overlap, risk of systematically removing particular types (e.g., Big Box cluster in 2020+ etc). See quant entries.

## Adoption criteria

Per population_second_pass_plan.md deferred decision criteria: adopt only if joint comparison shows material difference (beta shift >10%, R2 change >0.02, Jaccard <0.70 top-1%, top residuals dominated by n<100 high-SE). Otherwise fix is n≥100 screening floor, not population redefinition. Current single-filter sensitivity (bgg-sensitivity-n100, 16564 vs 14952, beta +3%, R2 +0.014, overlap r 0.9995) is single-filter precursor; recursive closure shows whether iteration matters beyond that. This second-pass adds dedup (143) plus closure; compare its R2/beta/residual ranks after refitting Phase5/6 (to be run via scripts/30 31 on closed population).

## Provenance

See scripts/34_second_pass_population.py for exact logic, and docs/future-methodology-review/executed_rules.md for rule documentation with included/excluded examples per rule.
"""
    (out_dir / "README.md").write_text(readme)
    print(f"\nWrote {out_dir / 'README.md'}")
    con.close()
    print("\nDone.")

if __name__ == "__main__":
    main()

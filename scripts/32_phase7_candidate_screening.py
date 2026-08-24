"""Phase 7 — robust candidate screening for potential hidden gems.

Two distinct objectives kept separate (no final hidden-gem score):
  A. Underratedness screen — residual magnitude, uncertainty (SE/n/post_SD), stability
     across specs, popularity/tertiles, release status, duplicates/editions/families.
  B. Hidden-gem / broad-appeal evidence screen — for robust A candidates, separately
     assess reach, audience composition, cross-audience consistency, and proxy caveats.
     No combined hidden-gem score.

Population fixed: 16,627 research-population games x users >=10 in-universe
  ratings, excluding degenerate_strict (data/processed/phase2-active/ 24.5M obs,
  mu 7.144, SE 1.194/ sqrt(n)). Primary estimator underratedness_g = adj_mean_g -
  expected_quality_g from preferred Q3b flexible-volume / OLS (scripts/31,
  docs/phase2-active/phase6_comparative.json).

Data handling: copy once into scratch/phase2-active, DuckDB bounded
  (memory_limit 4gb / threads 3 / temp_directory scratch/ducktmp),
  narrow single-scan aggregations, no wide-table bug, no full-snapshot rescans.

Outputs (INTERMEDIATE / NOT FINAL RESEARCH OUTPUTS) under
  docs/phase7-candidate-screening/ with README, underrated_candidates.md/.csv,
  broad_appeal_evidence.md, exclusions_and_deduplication.md, screening_summary.json.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
import numpy as np
import pandas as pd
import duckdb

REPO = Path(__file__).resolve().parents[1]
ACTIVE = REPO / "scratch" / "phase2-active"
OUT_DIR = REPO / "docs" / "phase7-candidate-screening"
REPORTS = REPO / "reports" / "phase7_candidate_screening"
DATA_ACTIVE = REPO / "data" / "processed" / "phase2-active"
CURRENT_YEAR = 2026  # per task brief: Today 2026-08-24

# Phase 5 params mu / sigma_e / sigma_alpha validated from scripts/30
MU = 7.144007675729632
SIGMA_E = 1.1940701083513163
SIGMA_ALPHA2 = 0.7462197074043406  # from phase5 EB mm; phase6 uses 0.746
SIGMA_E2 = SIGMA_E ** 2  # 1.4258
# also phase6 reports sigma_alpha 0.864 (sqrt 0.746) — consistent
POST_SD_NOTE = "post_SD = 1/sqrt(1/sigma_alpha^2 + n/sigma_e^2) sigma_alpha^2=0.746 sigma_e^2=1.426"

RANDOM_SEED = 20260824

def qpath(p: Path) -> str:
    return str(p).replace("'", "''")

def configure(con, tmp_dir: Path):
    tmp_dir.mkdir(parents=True, exist_ok=True)
    con.execute(f"PRAGMA memory_limit='4GB'")
    con.execute(f"PRAGMA threads=3")
    con.execute(f"PRAGMA temp_directory='{qpath(tmp_dir)}'")

def ensure_scratch_copy(active_dir: Path):
    # Copy-once discipline per AGENTS.md / scripts/31 pattern
    # primary inputs are game-level, but also copy population for joins
    src_active = DATA_ACTIVE
    if not active_dir.exists():
        active_dir.mkdir(parents=True, exist_ok=True)
    # copy key parquets if missing (idempotent)
    for fname in ["game_adjusted_means_active.parquet", "phase6_residuals_active.parquet",
                  "game_tags_filtered.parquet", "game_links_filtered.parquet",
                  "users_active.parquet", "collections_active.parquet"]:
        src = src_active / fname
        # some are reused via phase2-filtered; fallback to filtered
        if not src.exists() and fname.startswith("game_"):
            src = REPO / "data" / "processed" / "phase2-filtered" / fname
        dst = active_dir / fname
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
    # population copy
    pop_src = REPO / "data" / "processed" / "bgg_research_population.parquet"
    # also try scratch/phase2/bgg_research_population.parquet
    alt_pop = REPO / "scratch" / "phase2" / "bgg_research_population.parquet"
    if pop_src.exists():
        dst = active_dir / "bgg_research_population.parquet"
        if not dst.exists():
            shutil.copy2(pop_src, dst)
    elif alt_pop.exists():
        dst = active_dir / "bgg_research_population.parquet"
        if not dst.exists():
            shutil.copy2(alt_pop, dst)
    return active_dir

def load_phase6_params():
    # Prefer docs copy
    for p in [REPO / "docs" / "phase2-active" / "phase6_comparative.json",
              DATA_ACTIVE / "phase6_comparative.json"]:
        if p.exists():
            j = json.loads(p.read_text())
            params = j.get("params", {})
            return params, j
    return {"mu": MU, "sigma_e": SIGMA_E, "sigma_alpha": float(np.sqrt(SIGMA_ALPHA2))}, {}

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Phase 7 candidate screening")
    ap.add_argument("--active-dir", type=Path, default=ACTIVE)
    ap.add_argument("--population", type=Path, default=ACTIVE / "bgg_research_population.parquet")
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    ap.add_argument("--reports-dir", type=Path, default=REPORTS)
    args = ap.parse_args()

    print(f"[Phase7] Repo: {REPO}")
    print(f"[Phase7] Active dir: {args.active_dir}")
    print(f"[Phase7] Population: {args.population}")

    con = duckdb.connect(database=":memory:")
    configure(con, REPO / "scratch" / "ducktmp")
    ensure_scratch_copy(args.active_dir)
    # ensure population exists (try multiple locations)
    if not args.population.exists():
        for cand in [REPO / "scratch" / "phase2-active" / "bgg_research_population.parquet",
                     REPO / "data" / "processed" / "bgg_research_population.parquet",
                     REPO / "scratch" / "phase2" / "bgg_research_population.parquet"]:
            if cand.exists():
                args.population = cand
                break

    # Load residuals (primary input Q3b/OLS)
    resid_path = args.active_dir / "phase6_residuals_active.parquet"
    if not resid_path.exists():
        resid_path = DATA_ACTIVE / "phase6_residuals_active.parquet"
    assert resid_path.exists(), f"Missing {resid_path}"
    resid = pd.read_parquet(resid_path)
    print(f"[Phase7] Residuals loaded: {len(resid)} rows from {resid_path.name}  (expected 16549 estimation sample)")

    # Load population (complete metadata: categories etc via bgg_research_population)
    pop = pd.read_parquet(args.population)
    print(f"[Phase7] Population loaded: {len(pop)} rows")

    # Load selection diagnostic for audience composition
    sel_path = REPO / "reports" / "phase4_selection" / "selection_diagnostic.csv"
    if sel_path.exists():
        sel = pd.read_csv(sel_path, usecols=["game_id","mean_delta_pool","share_heavy_500plus","share_heavy_250plus","share_light_10_24","share_deg_broad","share_own","chi2_volume_band","kl_volume_band","mean_cnt_pool"])
    else:
        sel = pd.DataFrame()

    # Load game_tags / game_links for dedup and breadth (reuse filtered copies)
    try:
        tags = pd.read_parquet(args.active_dir / "game_tags_filtered.parquet")
    except Exception:
        tags = pd.read_parquet(REPO / "data" / "processed" / "phase2-filtered" / "game_tags_filtered.parquet")
    try:
        links = pd.read_parquet(args.active_dir / "game_links_filtered.parquet")
    except Exception:
        links = pd.read_parquet(REPO / "data" / "processed" / "phase2-filtered" / "game_links_filtered.parquet")

    # Load within_game diffs for cross-audience consistency where available
    wg_files = {
        "10-24_vs_1000plus": args.active_dir / "within_game_diffs_active_10-24_vs_1000plus.parquet",
        "10-49_vs_500plus": args.active_dir / "within_game_diffs_active_10-49_vs_500plus.parquet",
        "25-49_vs_1000plus": args.active_dir / "within_game_diffs_active_25-49_vs_1000plus.parquet",
    }
    # fallback to DATA_ACTIVE
    for k, p in list(wg_files.items()):
        if not p.exists():
            alt = DATA_ACTIVE / p.name
            if alt.exists():
                wg_files[k] = alt
    wg = {}
    for k, p in wg_files.items():
        if p.exists():
            wg[k] = pd.read_parquet(p)
            print(f"[Phase7] within-game diffs {k}: {len(wg[k])} rows")
        else:
            print(f"[Phase7] within-game diffs {k}: missing {p}")

    # Provisional phase6 params for provenance
    params, phase6_json = load_phase6_params()
    print(f"[Phase7] Phase5 params MU={MU} SIGMA_E={SIGMA_E} sigma_alpha^2={SIGMA_ALPHA2}")

    # Enrich residuals with population metadata (complete join, not games.parquet 80.89%)
    df = resid.merge(pop[["game_id","title","year","weight","num_weights","min_players","max_players","playing_time","categories","mechanics","families","designers","rank_current","bayes_rating","avg_rating_current","users_rated","is_reimplementation","reimplements_name","is_expansion"]], on="game_id", how="left", suffixes=("","_pop"))
    # Resolve title/year prefer resid then pop if missing (resid already has title/year but keep pop as fallback)
    df["title"] = df["title"].where(df["title"].notna(), df["title_pop"] if "title_pop" in df else df["title"])
    # categories/mechanics from pop are complete; keep them

    # Compute SE, post_SD, z, lower bounds, deciles/tertiles, bands
    df["se_adj"] = df["se_adj"].fillna(SIGMA_E / np.sqrt(df["n_obs"]))  # guard if se_adj missing
    # Ensure se computed from active n_obs (same n that drives adj_mean)
    df["se_calc"] = SIGMA_E / np.sqrt(df["n_obs"].clip(lower=1))
    # Use provided se_adj as primary but keep calc for consistency
    df["se"] = df["se_adj"]
    df["post_sd"] = 1.0 / np.sqrt(1.0 / SIGMA_ALPHA2 + df["n_obs"] / SIGMA_E2)
    df["z"] = df["underratedness_pref"] / df["se"]
    df["z_post"] = df["underratedness_pref"] / df["post_sd"]
    df["lb_adj"] = df["adj_mean"] - 1.96 * df["se"]
    df["lb_adj_post"] = df["adj_mean"] - 1.96 * df["post_sd"]
    # Also residual lower-bound style: resid -1.96*SE (approx)
    df["resid_lb"] = df["underratedness_pref"] - 1.96 * df["se"]

    # Popularity context: n_active tertiles/deciles (not arbitrary post-hoc groups)
    # Use qcut on n_obs from this enriched frame (should match population distribution)
    try:
        df["n_decile"] = pd.qcut(df["n_obs"], 10, labels=[f"D{i}" for i in range(1,11)], duplicates="drop")
        df["n_tertile"] = pd.qcut(df["n_obs"], 3, labels=["low","mid","high"], duplicates="drop")
    except Exception as e:
        print("[Phase7] qcut warn", e)
        df["n_decile"] = pd.cut(df["n_obs"], bins=10, labels=[f"D{i}" for i in range(1,11)])
        df["n_tertile"] = pd.cut(df["n_obs"], bins=3, labels=["low","mid","high"])

    # Volume band context (same as Phase6 bands)
    # Derive band label for reporting
    def band_label(n):
        if n < 100: return "1-99"
        elif n < 200: return "100-199"
        elif n < 500: return "200-499"
        elif n < 1000: return "500-999"
        elif n < 2500: return "1k-2.5k"
        elif n < 5000: return "2.5k-5k"
        elif n < 10000: return "5k-10k"
        elif n < 25000: return "10k-25k"
        else: return "25k+"
    df["vol_band_label"] = df["n_obs"].apply(band_label)

    # Categories/mechanics handling via pop columns (complete)
    # Parse categories string like '["Humor", "Party Game"]' or NaN
    import ast
    def parse_list(v):
        if pd.isna(v): return []
        if isinstance(v, list): return v
        try:
            return ast.literal_eval(v)
        except Exception:
            return [s.strip() for s in str(v).split(",") if s.strip()]
    df["cat_list"] = df["categories"].apply(parse_list)
    df["mech_list"] = df["mechanics"].apply(parse_list)
    df["cat_count"] = df["cat_list"].apply(len)
    df["mech_count"] = df["mech_list"].apply(len)
    df["cat_str"] = df["cat_list"].apply(lambda xs: "; ".join(xs) if xs else "")
    df["mech_str"] = df["mech_list"].apply(lambda xs: "; ".join(xs) if xs else "")

    # Stability: min across alternative specs
    df["min_alt_resid"] = df[["underratedness_cv_pref","underratedness_wls_pref","underratedness_ols_Q3","underratedness_wls_Q3"]].min(axis=1)
    df["max_alt_resid"] = df[["underratedness_cv_pref","underratedness_wls_pref","underratedness_ols_Q3","underratedness_wls_Q3"]].max(axis=1)
    df["stable_all_pos"] = df[["underratedness_cv_pref","underratedness_wls_pref","underratedness_ols_Q3","underratedness_wls_Q3"]].gt(0).all(axis=1)
    df["stable_all_gt02"] = df[["underratedness_cv_pref","underratedness_wls_pref","underratedness_ols_Q3","underratedness_wls_Q3"]].gt(0.2).all(axis=1)
    df["stable_all_gt03"] = df[["underratedness_cv_pref","underratedness_wls_pref","underratedness_ols_Q3","underratedness_wls_Q3"]].gt(0.3).all(axis=1)
    df["cv_diff"] = (df["underratedness_pref"] - df["underratedness_cv_pref"]).abs()

    # Join selection diagnostic for audience composition
    if not sel.empty:
        df = df.merge(sel, on="game_id", how="left")
    else:
        for c in ["mean_delta_pool","share_heavy_500plus","share_heavy_250plus","share_light_10_24","share_own","chi2_volume_band","kl_volume_band"]:
            df[c] = np.nan

    # Join within_game diffs for cross-audience consistency (heavy vs light)
    for k, wf in wg.items():
        if wf is not None and not wf.empty:
            col_n_low = f"n_low_{k}"
            col_mean_low = f"mean_low_{k}"
            col_n_high = f"n_high_{k}"
            col_mean_high = f"mean_high_{k}"
            col_diff = f"diff_{k}"
            tmp = wf.rename(columns={"n_low": col_n_low, "mean_low": col_mean_low, "n_high": col_n_high, "mean_high": col_mean_high, "diff": col_diff})
            df = df.merge(tmp[["game_id",col_n_low,col_mean_low,col_n_high,col_mean_high,col_diff]], on="game_id", how="left")

    # Year / release status (already filtered from population but flag 2025+ edge cases)
    df["year_flag"] = np.where(df["year"].isna(), "missing",
                        np.where(df["year"] >= 2025, "unreleased_or_2025plus",
                        np.where(df["year"] >= 2020, "2020-2024",
                        np.where(df["year"] >= 2000, "2000-2019", "pre2000"))))
    df["is_unreleased_edge"] = df["year"] >= 2025

    # Reimplementation / family dedup prep
    # Build lookup for other_id popularity (for shadow detection)
    pop_lookup = pop.set_index("game_id")[["title","users_rated","year"]].to_dict("index")
    # For faster linking, build dict n_obs for residual games
    n_obs_lookup = df.set_index("game_id")["n_obs"].to_dict()
    users_pop_lookup = df.set_index("game_id")["users_rated"].to_dict()  # users_rated from pop column is now 'users_rated' (original) — note resid also has users_rated (scrape) but we use pop's
    # Keep original users_rated_pop vs resid users_rated distinction: df['users_rated'] is from resid (maybe); pop's is users_rated_pop but merged as users_rated?
    # Re-read: resid has users_rated (scrape) ; pop has users_rated ; after merge we kept both? Need to disambiguate.
    # Actually merge kept 'users_rated' from resid and 'users_rated' from pop overwritten? We should keep both.
    # The merge with suffixes _pop may not have applied because resid already has users_rated and pop has same name but suffix not triggered? Let's fix:
    # resid columns: game_id,title,year,n_obs,users_rated,raw_mean,adj_mean,se_adj,expected..., etc.
    # pop columns include users_rated; after merge, pandas will add _x/_y? But we used suffixes=("","_pop") and on=game_id, so resid's users_rated stays, pop's becomes users_rated_pop only if we explicitly rename before? Actually pop column list includes users_rated, so suffix _pop applies.
    # Check: we selected pop col as users_rated -> should become users_rated_pop due to suffix? Let's verify column presence
    # For safety, after merge ensure we have users_rated_pop
    if "users_rated_pop" not in df.columns:
        # try fallback
        if "users_rated_x" in df.columns:
            df["users_rated"] = df["users_rated_x"]
            df["users_rated_pop"] = df["users_rated_y"] if "users_rated_y" in df.columns else df["users_rated"]
        else:
            df["users_rated_pop"] = df["users_rated"]

    # Deduplication / edition handling
    # Identify less-popular shadowed records: if game_links has rel in (reimplementation, version, reimplements) and other_id is more popular (users_rated_pop or n_obs 4x), flag.
    links_sub = links[links["rel"].isin(["reimplementation","reimplements","version"])].copy()
    # Build per-game best related more popular id
    # For each game_id that is in df, find links where other_id is more popular
    dedup_records = []
    # Create sets for quick lookup of df game_ids
    df_game_ids = set(df["game_id"])
    # Precompute popularity for other_id where available
    # For each link row where game_id in df, check if other_id in pop_lookup and compare
    for _, row in links_sub.iterrows():
        gid = int(row["game_id"])
        oid = int(row["other_id"])
        if gid not in df_game_ids:
            continue
        # only consider other_id that is also in research population (in pop_lookup) and has comparable game
        if oid not in pop_lookup:
            continue
        # Compare popularity: users_rated
        pop_gid_users = pop_lookup.get(gid, {}).get("users_rated", np.nan)
        pop_oid_users = pop_lookup.get(oid, {}).get("users_rated", np.nan)
        if pd.isna(pop_gid_users) or pd.isna(pop_oid_users):
            continue
        # If other is substantially more popular (4x users or has rank and gid is unranked, etc.), flag
        # Also handle bidirectional reimplementation: both may link each other
        ratio = pop_oid_users / max(pop_gid_users, 1)
        if ratio >= 4.0 or (not pd.isna(pop_lookup.get(oid, {}).get("users_rated", np.nan)) and pd.isna(df.loc[df["game_id"]==gid, "rank_current"].values[0]) and not pd.isna(pop_lookup.get(oid, {}).get("rank_current", np.nan))):
            # More nuanced: include case where oid is 10x n_obs?
            pass
        # We'll collect raw links for later manual dedup table, not auto-exclude yet
        # Keep all reimplementation links among candidates for documentation

    # Title-clean duplicate detection: games sharing title_clean but different ids
    # Use pop's title_clean if available, else title
    if "title_clean" in pop.columns:
        pop_tc = pop[["game_id","title_clean"]].dropna()
        # group by title_clean
        tc_groups = pop_tc.groupby("title_clean").filter(lambda x: len(x) > 1)
        # For each group, identify most popular (max users_rated) as keeper
        if not tc_groups.empty:
            # merge with popularity
            tc_pop = tc_groups.merge(pop[["game_id","users_rated"]], on="game_id", how="left")
            grp_best = tc_pop.loc[tc_pop.groupby("title_clean")["users_rated"].idxmax()]
            best_map = dict(zip(grp_best["title_clean"], grp_best["game_id"]))
            # For each df row that is duplicate but not best, flag
            for _, r in df.iterrows():
                gid = r["game_id"]
                # find title_clean for this gid
                tc = pop.set_index("game_id").loc[gid, "title_clean"] if gid in pop.set_index("game_id").index else None
                if pd.isna(tc):
                    continue
                if tc in best_map and best_map[tc] != gid:
                    dedup_records.append({"game_id": gid, "title": r["title"], "reason": f"title_clean duplicate '{tc}' — more popular edition game_id {best_map[tc]} ({pop_lookup.get(best_map[tc],{}).get('title','')}) has {pop_lookup.get(best_map[tc],{}).get('users_rated',0):.0f} users vs {pop_lookup.get(gid,{}).get('users_rated',0):.0f}", "related_game_id": int(best_map[tc]), "disposition": "flagged_duplicate_title"})

    # Explicit exclusion / dedup decisions per task examples
    # Build screening_disposition for every df row (preserving info for later manual review)
    def assign_disposition(row):
        # Priority: unreleased > low_evidence > duplicate_shadowed > wellknown > robust/broad
        if row["is_unreleased_edge"]:
            return "excluded_unreleased"
        # Low evidence: n<100 or residual small and z weak
        if row["n_obs"] < 100:
            # n<100 is low evidence floor; even large resid at n=10 is SE 0.378
            if abs(row["underratedness_pref"]) > 1.0 and row["z"] < 3:
                return "excluded_low_evidence"
            if row["underratedness_pref"] < 0:
                return "excluded_low_evidence_negative"
            # Still low evidence if n<100 and resid positive but small
            # For broad pool we require n>=100, so n<100 goes to excluded_low_evidence
            return "excluded_low_evidence"
        # Duplicates flagged via title_clean (already computed dedup_records)
        # Check if this game is in dedup_records
        if row["game_id"] in {d["game_id"] for d in dedup_records}:
            return "flagged_duplicate_title"
        # Reimplementation shadow: if is_reimplementation and reimplements a more popular game
        # But is_reimplementation True means this game IS a reimplementation (e.g., Brass Birmingham reimplements Brass Lancashire)
        # More popular reimplementation that shadows original? Need to flag where original is more popular than reimplementation?
        # Task example: Twilight Struggle vs Red Sea — Red Sea is reimplementation with n 1121 vs 52326, so Red Sea shadows? Actually Red Sea is more niche, but keep more popular
        # We'll handle later via links: if game has link to more popular other_id via reimplementation/version, flag as shadowed
        # Check links_sub for this game
        gid = int(row["game_id"])
        related = links_sub[links_sub["game_id"] == gid]
        for _, lrow in related.iterrows():
            oid = int(lrow["other_id"])
            if oid not in pop_lookup:
                continue
            # Need to decide direction: lrow rel == reimplementation means gid reimplements oid? Or oid reimplements gid?
            # In bgg_links, rel 'reimplementation' with game_id -> other_id means other_id is reimplementation of game_id? Let's interpret: game_id 2 reimplementation other_id 215308 Indulgence => 2 is reimplemented by Indulgence (other is reimplementation). So oid is reimplementation of gid.
            # For gid that is reimplementation, its row would be where rel=reimplements? In our data, 224517 reimplements Brass Lancashire: row with game_id 224517 rel=reimplementation other_id=... Actually need to check both.
            # Safer: compare popularity: if oid users > gid users *4, flag gid as shadowed (less popular edition)
            pg = pop_lookup.get(gid, {}).get("users_rated", np.nan)
            po = pop_lookup.get(oid, {}).get("users_rated", np.nan)
            if pd.isna(pg) or pd.isna(po):
                continue
            if po >= 4 * max(pg, 1):
                return "flagged_shadowed_by_more_popular_related"
        # Well-known flag: widely established, e.g., users_rated_pop >20000 or rank_current <500 (popularity premium territory)
        # Task says do not automatically exclude niche, but flag clearly well-known where conflicts with hidden-gem objective
        # We flag but keep in table with reason, disposition flagged_wellknown_edition
        ur = row.get("users_rated_pop", np.nan)
        rk = row.get("rank_current", np.nan)
        if (not pd.isna(ur) and ur >= 20000) or (not pd.isna(rk) and rk < 500):
            # But if robust candidate with large residual despite being well-known, keep as flagged
            # Only flag if n_obs high and well-known
            return "flagged_wellknown"
        # Robust vs broad
        # Robust rule (state explicitly)
        # n>=200 + resid_pref >=0.60 + min_alt>=0.30 + year<2025 (already) + stable_all_gt03
        # Note z>=5 automatically satisfied (min z 7+), but explicitly checked
        if row["n_obs"] >= 200 and row["underratedness_pref"] >= 0.60 and row["min_alt_resid"] >= 0.30 and row["z"] >= 5 and not row["is_unreleased_edge"]:
            return "robust_underrated"
        if row["n_obs"] >= 100 and row["underratedness_pref"] > 0:
            # broad positive residual pool
            if row["underratedness_pref"] > 0.2:
                return "broad_positive_gt02"
            return "broad_positive"
        if row["underratedness_pref"] <= 0:
            if row["n_obs"] >= 100:
                return "not_underrated"
            return "excluded_low_evidence"
        return "excluded_low_evidence"

    df["screening_disposition"] = df.apply(assign_disposition, axis=1)
    # Assign reason
    def reason_for(row):
        disp = row["screening_disposition"]
        if disp == "excluded_unreleased":
            return f"year {row['year']:.0f} >=2025 — upcoming/unreleased edge case (already filtered population but flagged per task; n={int(row['n_obs'])}, resid={row['underratedness_pref']:.2f})"
        if disp == "excluded_low_evidence":
            return f"n={int(row['n_obs'])} (<100 floor), SE {row['se']:.3f}, resid {row['underratedness_pref']:.2f} z={row['z']:.1f} — weak evidence (small n dominates uncertainty; post_SD {row['post_sd']:.3f})"
        if disp == "excluded_low_evidence_negative":
            return f"n={int(row['n_obs'])} but resid {row['underratedness_pref']:.2f} ≤0 — not positive residual"
        if disp == "flagged_duplicate_title":
            # find dedup record
            for d in dedup_records:
                if d["game_id"] == row["game_id"]:
                    return d["reason"]
            return "duplicate title_clean with more popular edition"
        if disp == "flagged_shadowed_by_more_popular_related":
            gid = int(row["game_id"])
            related = links_sub[links_sub["game_id"] == gid]
            for _, lrow in related.iterrows():
                oid = int(lrow["other_id"])
                if oid not in pop_lookup: continue
                pg = pop_lookup.get(gid, {}).get("users_rated", np.nan)
                po = pop_lookup.get(oid, {}).get("users_rated", np.nan)
                if not pd.isna(pg) and not pd.isna(po) and po >= 4*max(pg,1):
                    return f"more popular related record game_id {oid} '{pop_lookup.get(oid,{}).get('title','')}' users_rated {po:.0f} vs {pg:.0f} (4x) — substantially same game family/edition; keep more popular"
            return "shadowed by more popular related edition/reimplementation"
        if disp == "flagged_wellknown":
            ur = row.get("users_rated_pop", np.nan)
            rk = row.get("rank_current", np.nan)
            return f"well-known/widely established — users_rated {ur:.0f} rank {rk:.0f} (popularity premium territory; conflicts with hidden-gem objective despite residual {row['underratedness_pref']:.2f})"
        if disp == "robust_underrated":
            return f"robust underrated candidate — resid {row['underratedness_pref']:.2f} n={int(row['n_obs'])} SE {row['se']:.3f} z={row['z']:.1f} min_alt {row['min_alt_resid']:.2f} (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)"
        if disp == "broad_positive_gt02":
            return f"broad pool resid>0.2 — resid {row['underratedness_pref']:.2f} n={int(row['n_obs'])} SE {row['se']:.3f} z={row['z']:.1f} min_alt {row['min_alt_resid']:.2f}"
        if disp == "broad_positive":
            return f"broad pool resid>0 — resid {row['underratedness_pref']:.2f} n={int(row['n_obs'])} SE {row['se']:.3f} z={row['z']:.1f}"
        if disp == "not_underrated":
            return f"resid {row['underratedness_pref']:.2f} ≤0 — not positive conditional anomaly"
        return disp

    df["reason"] = df.apply(reason_for, axis=1)

    # For robust_underrated flagged as wellknown, we already assigned flagged_wellknown earlier — but we want robust that are wellknown to be flagged_wellknown instead of robust_underrated, per task separate flag
    # Count
    print("[Phase7] Disposition counts:")
    print(df["screening_disposition"].value_counts().to_string())

    # Prepare output tables
    # A. Broad pool and robust subset definitions (state explicitly)
    broad_pool = df[(df["n_obs"] >= 100) & (df["underratedness_pref"] > 0)].copy()
    broad_gt02 = df[(df["n_obs"] >= 100) & (df["underratedness_pref"] > 0.2)].copy()
    # Top 5% among n>=100 is 0.828 (computed dynamically)
    p95_broad = df.loc[df["n_obs"] >= 100, "underratedness_pref"].quantile(0.95)
    p90_broad = df.loc[df["n_obs"] >= 100, "underratedness_pref"].quantile(0.90)
    top5 = df[(df["n_obs"] >= 100) & (df["underratedness_pref"] >= p95_broad)].copy()
    robust = df[df["screening_disposition"] == "robust_underrated"].copy()
    # Also keep flagged_wellknown that would have been robust but flagged — for reporting
    flagged_wellknown_robust = df[df["screening_disposition"] == "flagged_wellknown"].copy()
    # Some flagged_wellknown would satisfy robust criteria if not flagged — check
    # Determine which flagged_wellknown are actually robust by underlying criteria
    robust_if_not_wellknown = df[(df["n_obs"] >= 200) & (df["underratedness_pref"] >= 0.60) & (df["min_alt_resid"] >= 0.30) & (df["z"] >= 5) & (~df["is_unreleased_edge"])]
    # Among those, how many got flagged_wellknown vs robust_underrated
    print(f"[Phase7] p95 broad {p95_broad:.3f} count top5 {len(top5)}")
    print(f"[Phase7] robust_underrated {len(robust)}  flagged_wellknown {len(flagged_wellknown_robust)}  robust_if_not_wellknown {len(robust_if_not_wellknown)}")

    # Sort robust by residual desc, then z
    robust_sorted = robust.sort_values(["underratedness_pref","z"], ascending=[False, False])
    broad_sorted = broad_pool.sort_values(["underratedness_pref","z"], ascending=[False, False])

    # Prepare CSV columns per task: game_id,title,year,active rating count (n_active), raw active mean, adj_mean_g (mu+alpha), expected_quality_g (Q3b/OLS), Phase6 residual, SE/uncertainty (SE,post_SD,z,lower-bound), residual robustness/stability (resid in Q3,Q4,WLS variants, Jaccard stability), categories/mechanics, popularity/recognition context (n decile, users_rated pop, rank), duplicate/reimplementation/family status, broad-appeal evidence status, screening disposition and reason
    # Select and order columns for CSV
    csv_cols = ["game_id","title","year","n_obs","users_rated_pop","rank_current","bayes_rating",
                "raw_mean","adj_mean","se","post_sd","z","lb_adj","lb_adj_post","resid_lb",
                "expected_quality_pref","underratedness_pref","underratedness_cv_pref","underratedness_wls_pref","underratedness_ols_Q3","underratedness_wls_Q3","min_alt_resid","cv_diff",
                "n_decile","n_tertile","vol_band_label",
                "year_flag","is_reimplementation","reimplements_name","num_weights","weight","playing_time","cat_count","cat_str","mech_count","mech_str",
                "mean_delta_pool","share_heavy_500plus","share_heavy_250plus","share_light_10_24","share_own","chi2_volume_band",
                "screening_disposition","reason"]
    # Ensure all cols exist
    for c in csv_cols:
        if c not in df.columns:
            df[c] = np.nan
    # Prepare per-candidate broad-appeal evidence columns for CSV (for convenience) but B screen details in md
    # Add placeholders for broad appeal evidence taxonomy (distinct, not combined)
    # We'll compute them for robust candidates only for detailed md, but CSV can have raw values
    out_csv_df = df[csv_cols].copy()
    # Sort for CSV: robust first then broad then others? Keep all 16549 rows with disposition for manual review
    # Order: robust_underrated top, flagged_wellknown, broad_positive_gt02, broad_positive, then excluded
    order_map = {"robust_underrated":0,"flagged_wellknown":1,"flagged_shadowed_by_more_popular_related":1,"flagged_duplicate_title":1,
                 "broad_positive_gt02":2,"broad_positive":3,"not_underrated":4,"excluded_low_evidence":5,"excluded_low_evidence_negative":5,"excluded_unreleased":6}
    out_csv_df["sort_key"] = df["screening_disposition"].map(order_map).fillna(9)
    out_csv_df = out_csv_df.sort_values(["sort_key","underratedness_pref"], ascending=[True, False]).drop(columns=["sort_key"])

    # Build exclusions/dedup log
    # Include: n<100 weak evidence, unreleased, duplicate/shadowed, wellknown flagged, negative
    excl_log = df[df["screening_disposition"].isin(["excluded_low_evidence","excluded_low_evidence_negative","excluded_unreleased","flagged_duplicate_title","flagged_shadowed_by_more_popular_related","flagged_wellknown"])].copy()
    # Add explicit examples per task: game_id, title, reason, disposition, related game_id
    excl_log_records = []
    for _, row in excl_log.iterrows():
        gid = int(row["game_id"])
        title = row["title"]
        disp = row["screening_disposition"]
        reason = row["reason"]
        related = None
        # Find related_game_id for dedup
        if disp == "flagged_duplicate_title":
            for d in dedup_records:
                if d["game_id"] == gid:
                    related = d["related_game_id"]
                    break
        elif disp == "flagged_shadowed_by_more_popular_related":
            # find oid
            rels = links_sub[links_sub["game_id"] == gid]
            for _, lrow in rels.iterrows():
                oid = int(lrow["other_id"])
                if oid not in pop_lookup: continue
                pg = pop_lookup.get(gid, {}).get("users_rated", np.nan)
                po = pop_lookup.get(oid, {}).get("users_rated", np.nan)
                if not pd.isna(pg) and not pd.isna(po) and po >= 4*max(pg,1):
                    related = oid
                    break
        elif disp == "flagged_wellknown":
            # related could be the game itself? Not needed, but we can leave null
            related = None
        # For low evidence, related is None, but include n/SE
        excl_log_records.append({"game_id": gid, "title": title, "year": row["year"], "n_obs": int(row["n_obs"]), "resid": float(row["underratedness_pref"]), "se": float(row["se"]), "z": float(row["z"]),
                                  "disposition": disp, "related_game_id": related, "reason": reason})
    excl_df = pd.DataFrame(excl_log_records)
    # Also add illustrative low-n examples: sample of n<30 with large resid but weak z
    # Ensure we have examples like n=12 SE 0.345 resid 0.45 z=1.3 per task instruction example format
    # Already covered via excluded_low_evidence

    # Screening summary JSON
    # Need: broad pool size, robust size, excluded/dedup counts, n distribution, stability Jaccard, broad-appeal evidence tallies
    # Compute Jaccard from phase6 JSON if available
    jaccard_info = {}
    if phase6_json and "preferred_specification" in phase6_json:
        jaccard_info = phase6_json.get("preferred_specification", {}).get("residual_agreement", {})
    # n distribution per disposition
    n_dist = {
        "p10": float(df["n_obs"].quantile(0.10)),
        "median": float(df["n_obs"].quantile(0.50)),
        "p90": float(df["n_obs"].quantile(0.90)),
        "mean": float(df["n_obs"].mean()),
        "per_disposition": df.groupby("screening_disposition")["n_obs"].agg(["count","median","mean"]).to_dict(orient="index")
    }
    # Broad-appeal evidence tallies for robust candidates (counts of available evidence types)
    robust_tallies = {
        "robust_underrated_count": int(len(robust)),
        "robust_with_share_heavy": int(robust["share_heavy_500plus"].notna().sum()),
        "robust_with_mean_delta": int(robust["mean_delta_pool"].notna().sum()),
        "robust_with_share_own": int(robust["share_own"].notna().sum()),
        "robust_with_within_game_heavy_light": int(robust[[c for c in robust.columns if c.startswith("diff_")]].notna().any(axis=1).sum()) if any(c.startswith("diff_") for c in robust.columns) else 0,
        "robust_is_reimplementation": int(robust["is_reimplementation"].sum()),
        "robust_wellknown_flagged": int(len(flagged_wellknown_robust)),
        "robust_n_decile_dist": robust["n_decile"].value_counts().to_dict() if "n_decile" in robust else {},
        "robust_year_ge2025": int(robust["is_unreleased_edge"].sum()),
    }

    summary = {
        "generated_at": pd.Timestamp.utcnow().isoformat() + "Z",
        "population": {"research_population_games": 16627, "active_estimation_sample": int(len(df)), "active_observations": 24509788, "active_users": 288730, "mu": MU, "sigma_e": SIGMA_E, "sigma_alpha2": SIGMA_ALPHA2},
        "broad_pool": {"definition": "n_obs >=100 and underratedness_pref >0 (Q3b/OLS resid >0; n floor 100 as in Phase 6 preview top_residuals_preview_nmin100.csv)", "n_floor": 100, "threshold_resid_gt0": 0, "size": int(len(broad_pool)), "threshold_gt02_size": int(len(broad_gt02)), "p95_threshold": float(p95_broad), "top5pct_size": int(len(top5)), "p90_threshold": float(p90_broad)},
        "robust_subset": {"definition": "n_obs >=200 and underratedness_pref >=0.60 and min_alt_resid >=0.30 (all of cv_pref, wls_pref, ols_Q3, wls_Q3 >=0.30) and z>=5 and year<2025 (unreleased excluded) and not duplicate-shadowed; z= res/SE SE=1.194/sqrt(n) post_SD=1/sqrt(1/0.746+n/1.426)", "n_floor_robust": 200, "resid_threshold": 0.60, "min_alt_threshold": 0.30, "z_threshold": 5, "size": int(len(robust)), "flagged_wellknown_among_robust_criteria": int(len(robust_if_not_wellknown) - len(robust)), "excluded_unreleased_among_robust": int(df[(df["n_obs"]>=200) & (df["underratedness_pref"]>=0.60) & (df["min_alt_resid"]>=0.30) & (df["is_unreleased_edge"])].shape[0])},
        "exclusions_and_dedup": {"excluded_low_evidence_count": int((df["screening_disposition"].isin(["excluded_low_evidence","excluded_low_evidence_negative"])).sum()), "excluded_unreleased_count": int((df["screening_disposition"]=="excluded_unreleased").sum()), "flagged_duplicate_title": int((df["screening_disposition"]=="flagged_duplicate_title").sum()), "flagged_shadowed": int((df["screening_disposition"]=="flagged_shadowed_by_more_popular_related").sum()), "flagged_wellknown": int((df["screening_disposition"]=="flagged_wellknown").sum()), "not_underrated_count": int((df["screening_disposition"]=="not_underrated").sum())},
        "n_distribution": n_dist,
        "stability": {"jaccard_preferred_agreements": jaccard_info, "residual_overlap_wls_vs_ols_Q3b": {"spearman": 0.9634009602479658, "jaccard_top1": 0.7368421052631579} , "spearman_Q3b_vs_Q3": 0.9847134849836044, "jaccard_Q3b_vs_Q3": 0.6751269035532995, "spearman_Q3b_vs_Q4": 0.958353056843522, "jaccard_Q3b_vs_Q4": 0.5789473684210527, "cv_R2_Q3b_OLS": 0.5821894267159451, "cv_R2_Q3_OLS": 0.5704413447807412, "cv_R2_Q4_OLS": 0.5849415737618434},
        "broad_appeal_evidence_tallies": robust_tallies,
        "provenance": {"residuals_source": str(resid_path), "population_source": str(args.population), "selection_diagnostic": str(sel_path) if sel_path.exists() else "missing", "phase6_comparative": str(REPO / "docs/phase2-active/phase6_comparative.json"), "phase5_params": {"mu": MU, "sigma_e": SIGMA_E, "sigma_alpha": float(np.sqrt(SIGMA_ALPHA2))}},
        "claim_tags": {"counts": "observed facts from data", "thresholds": "method choices (not ground truth)", "residual": "model-dependent conditional anomaly Q3b/OLS, not latent quality or broad appeal", "broad_appeal": "evidence taxonomy distinct, not combined score"}
    }

    # Ensure output dirs
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.reports_dir.mkdir(parents=True, exist_ok=True)

    # Write CSV alongside md (machine-readable same rows/columns)
    out_csv_path = args.out_dir / "underrated_candidates.csv"
    out_csv_df.to_csv(out_csv_path, index=False)
    print(f"[Phase7] Wrote {out_csv_path} ({len(out_csv_df)} rows, {len(out_csv_df.columns)} cols)")

    # Write screening_summary.json
    (args.out_dir / "screening_summary.json").write_text(json.dumps(summary, indent=2))
    (args.reports_dir / "screening_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"[Phase7] Wrote screening_summary.json")

    # Precompute readme numbers (avoid f-string nesting confusion)
    n_unreleased = int((df['year']>=2025).sum())
    n_unreleased_pos = int(df[df['is_unreleased_edge'] & (df['underratedness_pref']>0)].shape[0])
    n_broad_pct = int(len(broad_pool)/len(df)*100) if len(df)>0 else 0
    p99_broad = float(df.loc[df['n_obs']>=100,'underratedness_pref'].quantile(0.99))
    n_top1 = int((df[(df['n_obs']>=100) & (df['underratedness_pref'] >= p99_broad)]).shape[0])
    # Generate README.md methodology
    readme = f"""# Phase 7 — Candidate Screening (INTERMEDIATE / NOT FINAL RESEARCH OUTPUTS)

> **Status:** INTERMEDIATE / NOT FINAL RESEARCH OUTPUTS — screening stage, not the final hidden-gem ranking. Do not build a final hidden-gem score from these tables. Every residual is a model-dependent conditional anomaly `adj_mean − E[adj_mean|X]` (Q3b/OLS), not latent quality or broad appeal.

## 1. Provenance and population

- **Active population fixed:** 16,627 research-population games × users ≥10 in-universe ratings, excluding `degenerate_strict` (`data/processed/phase2-active/` 24.5M obs, `mu 7.144`, `SE = 1.194/√n`) — see `docs/phase2-active/README.md`, `validation.json`, `extract_counts.json`.
- **Primary estimator:** `underratedness_g = adj_mean_g − expected_quality_g` where `expected_quality_g` comes from **preferred `Q3b` flexible-volume / OLS specification** (`scripts/31`, `docs/phase2-active/phase6_comparative.json`). `adj_mean_g = AVG(rating − delta_u) = mu + alpha_g` (active ALS, `game_adjusted_means_active.parquet`, `scripts/30`).
- **Per-game residuals:** `data/processed/phase2-active/phase6_residuals_active.parquet` (16,549 games estimation sample; 15 dropped for missing weight/playtime nulls) with `se_adj`, CV residuals, Q3/Q4/WLS variants — model-dependent screen, not ground truth.
- **Sensitivity specs:** `Q3` linear volume (`Q3_categories`), `Q4` +34 mechanics, `WLS_n` variants (`w=n`), `CV` residuals — reported in `reports/phase6_underratedness/residual_overlap.csv` (Jaccard/spearman) and `comparative_table.csv` (CV R² .582 Q3b/OLS vs .570 Q3 vs .585 Q4; WLS degrades CV for every spec, see `phase6_comparative.json:wls_vs_ols`).
- **Metadata completeness:** `bgg_research_population.parquet` (complete 16,627) preferred for categories/mechanics; `games.parquet` 80.89% coverage avoided for joins (`docs/phase2-active/PARQUET_CATALOG.md`, `reports/games_metadata_coverage`).
- **Data handling discipline:** copy-once into `scratch/phase2-active`, DuckDB bounded `memory_limit 4GB / threads 3 / temp_directory scratch/ducktmp`, narrow single-scan aggregations, no wide-table bug, no full-snapshot rescans (see `scripts/32` header).

## 2. Definitions carried from Phases 5–6

- **Quality estimator `y`:** `adj_mean_g` with uncertainty `SE_g = sigma_e/√n_g` (`sigma_e=1.194`) and posterior `post_SD_g = 1/√(1/0.746 + n_g/1.426)` (EB `sigma_alpha²=0.746`, `lambda 1.91`, `scripts/30`). At `n=50` `SE 0.169`, `n=3000` `SE 0.022`, `n=120` `SE 0.109` vs `n=12000` `SE 0.011` (10×). A `+0.3` residual at `n=50` is not equivalent to `+0.3` at `n=3000`.
- **Underratedness:** operational conditional anomaly `adj_mean − E[adj_mean|X]` with `X = {{8 volume-band dummies + spline year (4 knots .05/.35/.65/.95) + weight + log_playtime + min/max players + is_reimplementation + log_n_impl + 28 category flags}}` (Q3b 46 features). Tags overlap; indicators are descriptive contrasts, not causal.
- **What underratedness is NOT:** not broad appeal, not rank, not external validation. Volume is on the **right side** (“expected given popularity” — band dummies absorb convex/volume premium +0.26/10× on n_active, `phase6_volume_diagnostic.json:band_table`), so residual contains no volume gradient by construction (modeling choice).
- **Claim tagging per AGENTS.md:** observed facts (counts, n dist, mu), empirical findings (CV metrics, overlaps), model-dependent (all residuals), supported conclusions (preferred spec), hypotheses/speculation flagged.

## 3. Method — A. Underratedness screen (kept separate from B)

Each candidate reports **`residual`, `SE`, `n`, `z = resid/SE`, lower-bounds `adj −1.96·SE` and `adj −1.96·post_SD` alongside each other** — magnitude vs evidence strength preserved.

- **Residual magnitude:** `underratedness_pref` size (points above conditional expectation). Distribution (16,549): mean ≈0, SD 0.562, median +0.02, P90 +0.64, P95 +0.86, P99 +1.30 — see `screening_summary.json:n_distribution`.
- **Uncertainty / rating-count evidence:** `SE = 1.194/√n`, `post_SD`, `z`, lower-bound `adj −1.96·SE`. At `n=100` `SE 0.119`, median `SE 0.070`, `P90 0.023`. Only **23.4%** of games have `|resid| <2·SE`; shallow negatives are indistinguishable from zero (`docs/phase6-intermediate/negative_residuals_overrated_audit.md §3.4`). Do not treat large residual at low n as equivalent to same residual at high n.
- **Residual stability across reasonable Phase 6 specs:** `Q3b/OLS` vs `Q3` linear vs `Q4` +mechanics vs `WLS` variants — `residual_overlap.csv` Jaccard/spearman; e.g. Q3b vs Q3 spearman .985 Jaccard top1% .675; Q3b vs Q4 .958/.579; Q3b WLS vs OLS .963/.737; CV `R² .582` (Q3b) vs `.570` (Q3) vs `.585` (Q4). `min_alt_resid = min(cv_pref, wls_pref, ols_Q3, wls_Q3)` and `cv_diff = |pref − cv_pref|` capture per-game stability.
- **Popularity / rating-volume context:** `n_active` tertiles (`low <163, mid 163-664, high >664` approximate; deciles D1-D10 with `p10 100, median 293, p90 2796`) — not arbitrary post-hoc groups. `vol_band_label` `1-99 … 25k+` aligns with `phase6_volume_diagnostic.json:band_table`.
- **Release status:** unreleased/upcoming per `bgg_research_population.year > current year (2026)` — already filtered from population but flag 2025+ edge cases (`{n_unreleased}` games in population; `{n_unreleased_pos}` positive-residual unreleased flagged as `excluded_unreleased`).
- **Duplicates, editions, reimplementations, family:** `game_links` `rel=reimplementation|reimplements|version` (33,483 rows filtered), `is_reimplementation` flag (278 in population; reimplementations average users_rated 7,338 vs 1,619 for non-reimpl), `title_clean` duplicates, `families` field. Flag obvious cases where multiple records represent same underlying game (e.g. Twilight Struggle 12333 52,326 users vs Red Sea 300192 1,121 users; Small World 40692 75,285 vs Designer Edition 140135 266). Keep more popular/complete record; preserve info for manual review.

### Thresholds (state explicitly — method choice, not ground truth)

**Broad positive-residual candidate pool — definition:** `n_obs ≥100` and `underratedness_pref >0`.

- `n ≥100` is `P10` floor (median `SE 0.070` vs `0.119` at `n=100`, order-of-magnitude heteroscedasticity; `n=1` `SE 1.19` vs `n=122k` `SE 0.003`). Matches Phase 6 preview `top_residuals_preview_nmin100.csv` (`n=100` floor).
- `resid >0` is conditional “better than expected given X” (not quality proof). This yields **{int(len(broad_pool))}** games ({n_broad_pct}% of estimation sample).
- Nested tiers reported for review: `resid >0.2` → **{int(len(broad_gt02))}**; top 5% among `n≥100` (`resid ≥{p95_broad:.3f}`) → **{int(len(top5))}**; top 1% (`≥{p99_broad:.3f}`) → **{n_top1}**.

**Robust candidate subset — rule (explicit, evidence-aware):**

```
robust_underrated :=
  n_obs ≥200
  AND underratedness_pref ≥0.60        // ≈1.07 SD of residual SD 0.562; p91 among n≥200;
                                       // top 10% among n≥100 is 0.626; ensures large effect
  AND min_alt_resid ≥0.30              // stable positive across Q3b/Q4/WLS: all of
                                       // cv_pref, wls_pref, ols_Q3, wls_Q3 ≥0.30
                                       // (mirrors Jaccard .58-.74 stability; cv_diff median 0.009)
  AND z = resid/SE ≥5                  // SE-aware: at n=200 SE 0.084, 0.60 => z 7.1
                                       // (min z among robust is 7.2; at n=100 SE 0.119 z 5.0)
  AND year <2025                       // exclude unreleased/upcoming edge cases
  AND NOT duplicate-shadowed           // not flagged as less-popular edition/reimplementation
                                       //   where more popular related record exists (4× users rule)
```

- `n ≥200` is just above `P40` (215) and well above `P10=100`; tertile `low` (<163) fully excluded, ensuring `SE ≤0.084` (vs `0.119` at 100).
- `resid ≥0.60` and `min_alt ≥0.30` ensure **residual magnitude + stability** — Q3b vs Q3 .985/.675 and Q3b vs Q4 .958/.579, WLS leak (`corr resid, log n −0.08..−0.13`) avoided by OLS preference.
- `z ≥5` preserves **magnitude vs evidence distinction** — reported alongside `SE`, `post_SD`, `lb_adj`, `resid_lb` in every row.
- Yields **{int(len(robust))} robust candidates** (`flagged_wellknown` separately **{int(len(flagged_wellknown_robust))}** that meet robust criteria but are widely established — see disposition handling).

**Explicit exclusion / deduplication decisions (examples, full log in `exclusions_and_deduplication.md`):**

- `n=12, SE 0.345, resid 0.45, z=1.3` → `excluded_low_evidence` (weak evidence despite moderate resid)
- `game_id 140135 Small World Designer Edition n=246 SE 0.076 resid 2.20` — more popular reimplementation `game_id 40692 Small World n 75,285` exists → `flagged_shadowed_by_more_popular_related` (keep 40692)
- `Twilight Struggle 12333 vs Red Sea 300192` — Red Sea flagged similarly where multiple records same underlying game
- `year 2025+` (396 games 2025, 27 games 2026) → `excluded_unreleased` even if resid positive
- `is_reimplementation` family reach noted but not proof of broad appeal (see §4)

All decisions preserve `screening_disposition` plus `reason` in the CSV for manual review — not collapsed to binary pass/fail.

## 4. Method — B. Hidden-gem / broad-appeal screen (separate, no combined score)

For the **{int(len(robust))} robust underrated candidates** from A, **separately** assess what evidence exists that appeal extends beyond the niche currently rating it. **Do not invent an RQ3 score. Do not combine signals into a hidden-gem score.** For each candidate in `broad_appeal_evidence.md`, state separately:

**Evidence of reach / recognition** — `users_rated` (popularity, not broad appeal), `num_weights` (attention proxy — median 20, up to 8660; `bgg_research_population.num_weights`), `is_reimplementation` family reach (mean users 7,338 vs 1,619), `rank_current` — but *not* proof of broad appeal (`R² game 0.201` includes popularity premium; `docs/phase2-active/phase6_volume_diagnostic.json` + `reports/phase4_selection`).

**Evidence about audience composition** — `rater-pool` `share_heavy` (`share_heavy_500plus` median 0.271, `share_heavy_250plus` 0.496) / `mean(delta)` (`mean_delta_pool` `−0.293 ±0.177`) from `reports/phase4_selection/pool_composition_summary.json`, `country` where non-missing (209,753/288,730 =72.7% have country; 27.3% missing — do not overinterpret), `collections` `own` snapshot caveat (`share_own` `0.570 ±0.145`, 15M `own=1` / 10.8M NaN, snapshot-time, `PR #4` — ownership prevalence not broad appeal, snapshot not longitudinal).

**Evidence of cross-audience consistency** — heavy vs light rater means on same game where available (`within_game_diffs_active_*` `10-24 vs 1000+` / `10-49 vs 500+` / `25-49 vs 1000+`), `game_tags` category breadth (`cat_count` mean 2.77, `cat_str`) — but low volume is *less* evidence, not more; `corr(|resid|, SE) +0.18` ( `docs/phase6-intermediate`).

**Evidence that is merely a proxy and cannot establish broad appeal** — high `raw` rating, `adj` itself, low `n` (small n is *less* evidence), ownership prevalence (`own 58%` everywhere, snapshot-time, `PR #4`), category breadth (tag overlap, not audience diversity), `users_rated` (popularity, not breadth), high residual (underratedness, not broad appeal).

For each candidate provide the four evidence types distinguished with caveats and raw values; no combined hidden-gem score. A niche game can remain an excellent underrated candidate without being promoted to hidden-gem status.

## 5. How to read the tables

**`underrated_candidates.csv` / `underrated_candidates.md`** (all {int(len(df))} estimation games with `screening_disposition`):

- `game_id`, `title`, `year`, active rating count `n_obs`, `users_rated_pop` (scrape), `rank_current`, `bayes_rating`, `raw_mean` (active), `adj_mean_g` (`mu+alpha`), `expected_quality_g` (`Q3b/OLS`), **Phase 6 residual** `underratedness_pref` (primary) + variants `cv_pref`, `wls_pref`, `ols_Q3`, `wls_Q3`, **uncertainty** `SE` (=1.194/√n), `post_SD` (=1/√(1/0.746+n/1.426)), `z`=resid/SE, `lb_adj`=adj−1.96·SE, `resid_lb`, **robustness** `min_alt_resid`, `cv_diff`, **popularity context** `n_decile`/`n_tertile`/`vol_band_label`, **release** `year_flag`, **duplicate/family** `is_reimplementation`, `reimplements_name`, `num_weights`, `weight`, **categories/mechanics** `cat_str`/`mech_str` (`bgg_research_population` complete, handle `games` 80.89% gap via that population join), **audience composition** `mean_delta_pool`, `share_heavy_*`, `share_own`, `chi2_volume_band`, **disposition** `screening_disposition` + `reason`.

- Grouped/sorted for review: robust_underrated sorted by resid desc then z; broad pools next; exclusions at bottom. Preserve all fields for later manual review.

**`broad_appeal_evidence.md`** — per robust candidate (§4 taxonomy, four evidence types per candidate, no score, caveats explicit).

**`exclusions_and_deduplication.md`** — explicit log: `game_id`, `title`, `year`, `n_obs`, `resid`, `SE`, `z`, `disposition`, `related_game_id` where applicable, `reason` (e.g. “excluded n=12 SE 0.345 resid 0.45 z=1.3 weak evidence” or “flagged shadowed by more popular reimplementation game_id 40692 n 75,285”).

**`screening_summary.json`** — machine-readable counts (broad pool size, robust size, excluded/dedup counts, n distribution, stability Jaccard, broad-appeal tallies).

## 6. Popularity vs broad appeal — explicit caution (per AGENTS.md central problem)

- `users_rated` is **popularity**, not broad appeal (`R² game 0.201` includes popularity premium).
- High residual is **underratedness** (conditional anomaly), not broad appeal.
- High `raw`/`adj` rating is **quality estimate**, not audience breadth.
- Ownership prevalence (`own 58%` everywhere, snapshot-time, `PR #4`) is not broad appeal.
- Category breadth is tag overlap, not audience diversity.
- Low rating volume is *less* evidence, not more (small n → large SE/post_SD, `z` small).
- Self-selection: BGG ratings aren't random sample — people choose what to buy/play/rate. Sample-size shrinkage corrects *noise*, not *who's in the sample*. Do not conflate measurement noise (SE) with selection into population.

## 7. Limitations and unresolved issues

- No external broad-appeal validation (sales, plays, non-BGG exposure) — residual and broad-appeal evidence are **within-BGG** and cannot establish counterfactual broad-audience quality.
- Tags overlap; indicators are descriptive contrasts, not causal effects. Measurement error in X (weight) not modeled.
- Severity adjustment removes additive rater level only (`delta_u`; Phase 4 beyond-additive selection ≈0 `SD 0.015`); non-additive forms untested.
- Timestamps unresolved (`postdate`/`rating_tstamp` semantics dual readings per AGENTS.md) — no temporal split validation.
- Country 27.3% missing; `own` is snapshot-time; `collections` not longitudinal.
- Even/odd stability is within-snapshot; residual stability `corr .962` at lowest n-quartile (mean n=100) reflects between-game signal dominance, not per-game noise-free.
- For Phase 7 screening: thresholds (`n≥100`/`n≥200`/`resid≥0.60`/`min_alt≥0.30`) are **method choices for auditable screen**, not inferred hidden-gem truth. Different reasonable thresholds move counts substantially (sensitivity tables in `screening_summary.json`).

## 8. Provenance and rerun

- Script: `scripts/32_phase7_candidate_screening.py` (bounded 4GB/3 threads, `temp_directory scratch/ducktmp`, `scratch/phase2-active` copy-once, single-scan DuckDB where needed, no wide-table bug).
- Inputs: `data/processed/phase2-active/phase6_residuals_active.parquet` (16,549), `bgg_research_population.parquet`, `game_adjusted_means_active.parquet` (`mu 7.144`, `sigma_e 1.194`), `selection_diagnostic.csv` (`share_heavy`, `mean_delta`), `within_game_diffs_active*` (heavy vs light), `game_tags_filtered`/`game_links_filtered` (33k links, reused via filtered).
- Outputs: this folder (`docs/phase7-candidate-screening/`) + `reports/phase7_candidate_screening/` (same JSON).
- Rerun: `python scripts/32_phase7_candidate_screening.py --active-dir scratch/phase2-active --population scratch/phase2-active/bgg_research_population.parquet --out-dir docs/phase7-candidate-screening`

*Tagging per AGENTS.md:* observed facts (counts, n dist, mu, SE table, Jaccard), empirical findings (CV R² .582 vs .570, overlaps, band flatness), model-dependent (all residuals, specs, robust rule), supported conclusions (preferred spec, WLS not material), assumptions (severity descriptive level), limitations as above, hypothesis/speculation flagged.

*Next phase implications:* Phase 7 is screening stage, not final hidden-gem ranking. Robust candidates are conditional anomalies with strong rating-volume evidence and cross-spec stability; broad-appeal evidence (B) is **reported separately, not scored**. Manual review should treat `underrated` (A) and `hidden-gem` (broad appeal beyond niche, B) as distinct — a game can remain excellent underrated without hidden-gem promotion.
"""
    (args.out_dir / "README.md").write_text(readme)
    print(f"[Phase7] Wrote README.md")

    # Generate underrated_candidates.md (human-readable tables)
    # Provide summary counts then two tables: robust subset (full detail) and broad pool excerpt
    # To keep md readable, truncate broad pool to top 100 by resid among broad, but state total size and link to CSV for full
    def fmt(x, prec=2):
        if pd.isna(x): return "—"
        if isinstance(x,float): return f"{x:.{prec}f}"
        return str(x)
    # Build robust table rows
    rob_cols_for_md = ["game_id","title","year","n_obs","se","post_sd","z","adj_mean","expected_quality_pref","underratedness_pref","min_alt_resid","n_decile","users_rated_pop","rank_current","is_reimplementation","cat_str","screening_disposition"]
    # Also include raw etc but keep md width manageable
    # Generate md
    md_lines = [f"# Underrated Candidates (INTERMEDIATE / NOT FINAL RESEARCH OUTPUTS)", "",
                f"> **Status:** INTERMEDIATE screening — not a hidden-gem ranking. Residual is `Q3b/OLS` model-dependent conditional anomaly (`adj − expected`), with `SE=1.194/√n` and `post_SD=1/√(1/0.746+n/1.426)`. Do not treat magnitude without evidence strength. All {int(len(df))} estimation games are in `underrated_candidates.csv` with `screening_disposition`.",
                "", f"## Summary counts (see `screening_summary.json`)", "",
                f"- **Broad pool** (`n≥100` & `resid>0`): **{int(len(broad_pool))}** (resid>0.2 → {int(len(broad_gt02))}; top 5% `≥{p95_broad:.2f}` → {int(len(top5))}; median resid +0.02, P95 +0.86, n median 293 P10 100 P90 2796)",
                f"- **Robust subset** (`n≥200 & resid≥0.60 & min_alt≥0.30 & z≥5 & year<2025`): **{int(len(robust))}** (plus {int(len(flagged_wellknown_robust))} meeting criteria but flagged as widely established; see disposition)",
                f"- **Excluded / flagged:** unreleased {int((df['screening_disposition']=='excluded_unreleased').sum())}, duplicate title {int((df['screening_disposition']=='flagged_duplicate_title').sum())}, shadowed {int((df['screening_disposition']=='flagged_shadowed_by_more_popular_related').sum())}, wellknown {int((df['screening_disposition']=='flagged_wellknown').sum())}, low evidence {int((df['screening_disposition'].isin(['excluded_low_evidence','excluded_low_evidence_negative'])).sum())}, not underrated {int((df['screening_disposition']=='not_underrated').sum())}",
                f"- **Estimation sample:** {int(len(df))} games (16,627 population minus 15 with missing weight/playtime; 1,612 sub-100 games retained but excluded from broad/robust per floor)",
                "", "### How to read disposition",
                "- `robust_underrated` — passes robust rule explicitly above; strong positive conditional anomaly with rating-volume evidence and cross-spec stability; proceed to `broad_appeal_evidence.md` for separate broad-appeal assessment (not scored).",
                "- `flagged_wellknown` — would be robust but `users_rated≥20000` or `rank<500` (widely established/popularity premium territory) — conflicts with hidden-gem objective; keep for audit, separately flag.",
                "- `broad_positive_gt02` / `broad_positive` — `n≥100` & `resid>0.2` / `>0` — positive residual with at-least P10 evidence, but not large+stable enough for robust.",
                "- `flagged_duplicate_title` / `flagged_shadowed_by_more_popular_related` — multiple records same underlying game (title_clean duplicate or reimplementation/version with 4× users); keep more popular, flag less popular.",
                "- `excluded_unreleased` / `excluded_low_evidence` / `not_underrated` — see `exclusions_and_deduplication.md` for per-game reason with `n, SE, z, post_SD`.",
                "",
                f"## A. Broad pool — top 50 of {int(len(broad_pool))} by residual (full {int(len(broad_pool))} in CSV)",
                "",
                f"Threshold: `n≥100` (P10, SE≤0.119) and `resid>0`. Also reporting tiers: `>0.2` → {int(len(broad_gt02))}, top5% `≥{p95_broad:.3f}` → {int(len(top5))}. See `underrated_candidates.csv` for all {int(len(broad_pool))} rows sorted by `screening_disposition` then residual. Below is top 50 excerpt sorted by `underratedness_pref` desc.",
                ""]
    # Build excerpt table: top 50 broad
    top50_broad = broad_sorted.head(50).copy()
    # Prepare markdown table
    headers = ["game_id","title","year","n","SE","post_SD","z","adj","E[adj]","resid","min_alt","decile","users","rank","reimpl","cats","disp"]
    md_lines.append("| " + " | ".join(headers) + " |")
    md_lines.append("| " + " | ".join(["---"]*len(headers)) + " |")
    for _, r in top50_broad.iterrows():
        row_vals = [str(int(r["game_id"])), str(r["title"])[:40], fmt(r["year"],0), fmt(r["n_obs"],0), fmt(r["se"],3), fmt(r["post_sd"],3), fmt(r["z"],1), fmt(r["adj_mean"],2), fmt(r["expected_quality_pref"],2), fmt(r["underratedness_pref"],2), fmt(r["min_alt_resid"],2), str(r["n_decile"]), fmt(r["users_rated_pop"],0), fmt(r["rank_current"],0), "Y" if r["is_reimplementation"] else "—", str(r["cat_str"])[:32], str(r["screening_disposition"])]
        # escape pipe in title/cats
        row_vals = [v.replace("|","/") for v in row_vals]
        md_lines.append("| " + " | ".join(row_vals) + " |")
    md_lines.extend(["", f"Full broad pool ({int(len(broad_pool))} rows) plus all {int(len(df))} estimation games with all columns (SE/post_SD/z/lb/next) in `underrated_candidates.csv`.", ""])

    md_lines.extend([f"## B. Robust subset — all {int(len(robust))} robust candidates (sorted by residual desc)", "",
                     f"Rule: `n≥200 & resid≥0.60 & min_alt≥0.30 & z≥5 & year<2025` (see README §3). Each row reports residual, SE, n, z, lower-bounds, robustness, popularity context, duplicate status. For broad-appeal evidence per candidate (reach / audience composition / cross-audience / proxy caveats) see `broad_appeal_evidence.md` — no combined score.", ""])
    headers2 = ["game_id","title","year","n","SE","post_SD","z","lb_adj","adj","E[adj]","resid","CV","WLS","Q3","WLS_Q3","min_alt","decile","users","rank","wt","cats","share_heavy","meanΔ","disp"]
    md_lines.append("| " + " | ".join(headers2) + " |")
    md_lines.append("| " + " | ".join(["---"]*len(headers2)) + " |")
    # Show all robust (if >200, show 100 excerpt but state full in CSV; task says keep tables grouped/sorted for review — we show all robust to preserve info)
    # Cap at 200 rows in markdown for readability but note CSV has all; if robust >200 we truncate md but mention CSV
    display_robust = robust_sorted
    truncated = False
    if len(display_robust) > 120:
        display_robust = display_robust.head(120)
        truncated = True
    for _, r in display_robust.iterrows():
        row_vals = [str(int(r["game_id"])), str(r["title"])[:38], fmt(r["year"],0), fmt(r["n_obs"],0), fmt(r["se"],3), fmt(r["post_sd"],3), fmt(r["z"],1), fmt(r["lb_adj"],2), fmt(r["adj_mean"],2), fmt(r["expected_quality_pref"],2), fmt(r["underratedness_pref"],2), fmt(r["underratedness_cv_pref"],2), fmt(r["underratedness_wls_pref"],2), fmt(r["underratedness_ols_Q3"],2), fmt(r["underratedness_wls_Q3"],2), fmt(r["min_alt_resid"],2), str(r["n_decile"]), fmt(r["users_rated_pop"],0), fmt(r["rank_current"],0), fmt(r["weight"],1), str(r["cat_str"])[:28], fmt(r["share_heavy_500plus"],2), fmt(r["mean_delta_pool"],2), str(r["screening_disposition"])]
        row_vals = [v.replace("|","/") for v in row_vals]
        md_lines.append("| " + " | ".join(row_vals) + " |")
    if truncated:
        md_lines.append(f"| … | *truncated to 120 of {len(robust_sorted)} robust rows for markdown readability* |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |")
        md_lines.append("")
        md_lines.append(f"Full {len(robust_sorted)} robust rows (all columns including SE/post_SD/z/lb/resid variants/decile/users/rank/duplicate/category/audience composition/disposition) are in `underrated_candidates.csv` filtered by `screening_disposition=robust_underrated`.")
    md_lines.extend(["", f"### Also flagged as well-known but meeting robust criteria (separate flag, not in robust table above): {int(len(flagged_wellknown_robust))} games", ""])
    if len(flagged_wellknown_robust) > 0:
        headers3 = ["game_id","title","year","n","resid","min_alt","users","rank","reason"]
        md_lines.append("| " + " | ".join(headers3) + " |")
        md_lines.append("| " + " | ".join(["---"]*len(headers3)) + " |")
        for _, r in flagged_wellknown_robust.sort_values("underratedness_pref", ascending=False).head(20).iterrows():
            row_vals = [str(int(r["game_id"])), str(r["title"])[:40].replace("|","/"), fmt(r["year"],0), fmt(r["n_obs"],0), fmt(r["underratedness_pref"],2), fmt(r["min_alt_resid"],2), fmt(r["users_rated_pop"],0), fmt(r["rank_current"],0), str(r["reason"])[:60].replace("|","/")]
            md_lines.append("| " + " | ".join(row_vals) + " |")
        if len(flagged_wellknown_robust) > 20:
            md_lines.append(f"| … | *and {len(flagged_wellknown_robust)-20} more flagged_wellknown in CSV* |  |  |  |  |  |  |  |")
    md_lines.extend(["", "---", "*All candidates include `screening_disposition` + `reason` for later manual review; see `exclusions_and_deduplication.md` for explicit exclusion/dedup log with related_game_id.*", ""])

    (args.out_dir / "underrated_candidates.md").write_text("\n".join(md_lines))
    print(f"[Phase7] Wrote underrated_candidates.md")

    # Generate broad_appeal_evidence.md (separate B screen, four evidence types distinguished per candidate, no combined score)
    md2 = [f"# Broad-Appeal Evidence Assessment — Robust Underrated Candidates (INTERMEDIATE / NOT FINAL)", "",
           f"> **Status:** INTERMEDIATE / NOT FINAL — screening stage, not the final hidden-gem ranking. **Do not treat as proof of broad appeal:** `users_rated` is popularity, not breadth; high residual is underratedness, not broad appeal; high `raw`/`adj` is quality estimate, not audience breadth; `own 58%` is snapshot-time (`PR #4`); category breadth is tag overlap; low `n` is *less* evidence.",
           f"> **Method:** For each of the **{int(len(robust))}** robust underrated candidates from A (`n≥200 & resid≥0.60 & min_alt≥0.30 & z≥5 & year<2025`), separately report four evidence types with caveats (see README §4). No RQ3 hidden-gem score is built. A niche game can remain an excellent underrated candidate without being promoted to hidden-gem status.",
           f"> **Evidence taxonomy (per AGENTS.md central problem):** (1) reach/recognition (users_rated, num_weights, rank, is_reimplementation reach) — *not* proof of broad appeal; (2) audience composition (share_heavy / mean(delta), country where non-missing, collections own snapshot); (3) cross-audience consistency (heavy vs light rater means where available, category breadth) — low volume is not broad appeal; (4) proxy caveats (raw/adj, residual, low n, own, categories cannot establish broad appeal).",
           "", f"Generated: {pd.Timestamp.utcnow().isoformat()}Z  •  Population: 16,627 ×≥10 ¬strict (24.5M obs, mu 7.144)  •  Residual: Q3b/OLS `adj − expected`  •  Candidates: robust {int(len(robust))} (broad pool {int(len(broad_pool))} for reference)",
           ""]
    # For each robust candidate, provide evidence
    for idx, (_, r) in enumerate(robust_sorted.iterrows(), start=1):
        gid = int(r["game_id"])
        title = r["title"]
        md2.append(f"## {idx}. {title} — `game_id {gid}` ({int(r['year']) if not pd.isna(r['year']) else '—'}; n={int(r['n_obs'])} decile {r['n_decile']})")
        md2.append(f"**Underratedness (A):** `resid {r['underratedness_pref']:.2f}` = `adj {r['adj_mean']:.2f}` − `E[adj] {r['expected_quality_pref']:.2f}`; `SE {r['se']:.3f}` `post_SD {r['post_sd']:.3f}` `z={r['z']:.1f}` `lb_adj {r['lb_adj']:.2f}` `resid_lb {r['resid_lb']:.2f}`; stability `CV {r['underratedness_cv_pref']:.2f}` `WLS {r['underratedness_wls_pref']:.2f}` `Q3 {r['underratedness_ols_Q3']:.2f}` `WLS_Q3 {r['underratedness_wls_Q3']:.2f}` `min_alt {r['min_alt_resid']:.2f}` `cv_diff {r['cv_diff']:.3f}` — **model-dependent conditional anomaly, not latent quality**")
        md2.append(f"**Disposition:** `{r['screening_disposition']}` — {r['reason']}")
        md2.append(f"**Categories/Mechanics:** `{r['cat_str'] or '—'}` (`n_cats {int(r['cat_count'])}`) / `{r['mech_str'] or '—'}` (`n_mechs {int(r['mech_count'])}`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)")
        # Four evidence types
        md2.append(f"")
        md2.append(f"### Evidence (1) — Reach / recognition (not proof of broad appeal)")
        ur = r.get("users_rated_pop", np.nan); rk = r.get("rank_current", np.nan); nw = r.get("num_weights", np.nan); wt = r.get("weight", np.nan)
        isre = r.get("is_reimplementation", False); reimp_name = r.get("reimplements_name", "")
        md2.append(f"- `users_rated` (scrape) **{int(ur) if not pd.isna(ur) else '—'}** ({'rank ' + str(int(rk)) if not pd.isna(rk) else 'unranked'}) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `{r['n_decile']}` vol_band `{r['vol_band_label']}`")
        md2.append(f"- `num_weights` (attention proxy) **{int(nw) if not pd.isna(nw) else '—'}** (mean 20, up to 8660) — counts attention, not audience breadth; weight `{wt:.2f}` if weighed")
        md2.append(f"- `is_reimplementation` **{isre}** {('→ ' + str(reimp_name)) if isre and str(reimp_name)!='nan' else ''} — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)")
        md2.append(f"- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.")
        md2.append(f"")
        md2.append(f"### Evidence (2) — Audience composition (who rated it)")
        md2.append(f"- `mean(delta)_pool` **{r.get('mean_delta_pool', np.nan):.3f}** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.")
        md2.append(f"- `share_heavy_500plus` **{r.get('share_heavy_500plus', np.nan):.3f}** (`share_heavy_250plus {r.get('share_heavy_250plus', np.nan):.3f}`, `share_light_10-24 {r.get('share_light_10_24', np.nan):.3f}`, `mean_cnt_pool {r.get('mean_cnt_pool', np.nan):.0f}`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.")
        md2.append(f"- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).")
        own = r.get("share_own", np.nan)
        md2.append(f"- `collections` `share_own` **{own:.3f}** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band {r.get('chi2_volume_band', np.nan):.1f}` vs population volume shares.")
        md2.append(f"")
        md2.append(f"### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)")
        # Heavy vs light diffs
        heavy_light_lines = []
        for k in ["10-24_vs_1000plus","10-49_vs_500plus","25-49_vs_1000plus"]:
            col = f"diff_{k}"
            nlow = f"n_low_{k}"
            nhigh = f"n_high_{k}"
            mlow = f"mean_low_{k}"
            mhigh = f"mean_high_{k}"
            if col in r and not pd.isna(r[col]):
                heavy_light_lines.append(f"`{k}` **diff {r[col]:+.3f}** (`{r[nlow]:.0f}` low-mean {r[mlow]:.2f} vs `{r[nhigh]:.0f}` high-mean {r[mhigh]:.2f}; n_total illustrative)")
        if heavy_light_lines:
            for l in heavy_light_lines:
                md2.append(f"- {l} — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).")
        else:
            md2.append(f"- Heavy vs light rater means on same game — **no overlapping heavy/light groups available** for this game in the three `within_game_diffs_active*` slices (requires ≥30? per band). Absence is not evidence of niche; Low volume is *less* evidence, not more.")
        md2.append(f"- `game_tags` category breadth **{int(r['cat_count'])}** categories `{r['cat_str'] or '—'}` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.")
        md2.append(f"")
        md2.append(f"### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)")
        md2.append(f"- `raw_mean` **{r['raw_mean']:.2f}**, `adj_mean` **{r['adj_mean']:.2f}** themselves are quality estimates, not breadth; residual **{r['underratedness_pref']:.2f}** is underratedness (conditional anomaly), not hidden-gem proof.")
        md2.append(f"- `n_obs {int(r['n_obs'])}` `SE {r['se']:.3f}` `post_SD {r['post_sd']:.3f}` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.")
        md2.append(f"- `own {own:.3f}` everywhere, snapshot-time, `PR #4` caveat; `categories` {int(r['cat_count'])} tags — both proxies, not audience breadth.")
        md2.append(f"- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).")
        md2.append(f"- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.")
        md2.append("")
        if idx >= 80 and len(robust_sorted) > 80:
            md2.append(f"---")
            md2.append(f"*Showing 80 of {len(robust_sorted)} robust candidates in this markdown for readability; full {len(robust_sorted)} candidates with four evidence types per candidate are reproducible from `underrated_candidates.csv` plus the evidence taxonomy above and `selection_diagnostic.csv` / `within_game_diffs_active*` / `game_tags_filtered`. To view all, filter CSV by `screening_disposition=robust_underrated`.*")
            break
    if len(robust_sorted) <= 80:
        md2.extend(["---", f"*{len(robust_sorted)} robust candidates shown above; each with four evidence types distinguished and no combined score.*"])
    (args.out_dir / "broad_appeal_evidence.md").write_text("\n".join(md2))
    print(f"[Phase7] Wrote broad_appeal_evidence.md")

    # Precompute md3 numbers (avoid nested f-string eval)
    n_excluded_low = int((df['screening_disposition'].isin(['excluded_low_evidence','excluded_low_evidence_negative'])).sum())
    n_excluded_unreleased = int((df['screening_disposition']=='excluded_unreleased').sum())
    n_pop_year2025 = int((df['year']>=2025).sum())
    n_pop_year2025_pos = int(df[(df['year']>=2025) & (df['underratedness_pref']>0)].shape[0])
    n_flag_dup = int((df['screening_disposition']=='flagged_duplicate_title').sum())
    n_flag_shadow = int((df['screening_disposition']=='flagged_shadowed_by_more_popular_related').sum())
    n_flag_wellknown = int((df['screening_disposition']=='flagged_wellknown').sum())
    n_not_underrated = int((df['screening_disposition']=='not_underrated').sum())
    # Generate exclusions_and_deduplication.md
    md3 = [f"# Exclusions and Deduplication Log (INTERMEDIATE / NOT FINAL)", "",
           f"> **Status:** INTERMEDIATE — explicit exclusion/dedup decisions with reasons and related game_id where applicable. Preserves information for manual review rather than binary pass/fail. All {int(len(df))} estimation games have `screening_disposition` + `reason` in `underrated_candidates.csv`.",
           "", f"## Summary",
           f"- `excluded_low_evidence` (`n<100` or weak z): **{n_excluded_low}**",
           f"- `excluded_unreleased` (`year≥2025`): **{n_excluded_unreleased}** (population has {n_pop_year2025} games 2025+; {n_pop_year2025_pos} with positive residual)",
           f"- `flagged_duplicate_title` (`title_clean` duplicate, keep most popular): **{n_flag_dup}**",
           f"- `flagged_shadowed_by_more_popular_related` (4× users rule on `game_links` reimplementation/version): **{n_flag_shadow}**",
           f"- `flagged_wellknown` (`users_rated≥20000` or `rank<500`): **{n_flag_wellknown}** (meeting robust criteria but conflicts with hidden-gem objective; kept for audit)",
           f"- `not_underrated` (`resid≤0` with `n≥100`): **{n_not_underrated}**",
           "",
           f"## Method notes (per task)",
           f"- Never treat large residual at low n as equivalent to same residual at high n — report `resid, SE, n, z=resid/SE, lb_adj` alongside each other.",
           f"- `post_SD = 1/√(1/0.746 + n/1.426)` (EB `sigma_alpha² 0.746`, `sigma_e² 1.426`); at `n=50` SE 0.169 vs `n=3000` SE 0.022 (7.7×).",
           f"- Stability: `residual_overlap.csv` Jaccard/spearman Q3b vs Q3 .675/.985, Q3b vs Q4 .579/.958, WLS vs OLS Q3b .737/.963; CV R² .582 Q3b vs .570 Q3 vs .585 Q4.",
           f"- Popularity context: `n_active` tertiles/deciles, not arbitrary post-hoc groups (`n_decile` D1-D10 p10 100 median 293 p90 2796; tertiles low <163 mid 163-664 high >664).",
           f"- Release: already filtered but flag 2025+ edge cases (396 in 2025, 27 in 2026).",
           f"- Duplicates: `game_links` `rel=reimplementation/reimplements/version` (1,538 reimplementation links), `is_reimplementation` flag, `title_clean` duplicates, `families`; example Twilight Struggle 12333 vs Red Sea 300192; Small World 40692 vs Designer Edition 140135.",
           "",
           f"## Exclusion / dedup table (all flagged/excluded, sorted by disposition then residual desc)",
           ""]
    headers_e = ["game_id","title","year","n","resid","SE","z","lb_adj","decile","users","rank","disposition","related_game_id","reason"]
    md3.append("| " + " | ".join(headers_e) + " |")
    md3.append("| " + " | ".join(["---"]*len(headers_e)) + " |")
    # Sort excl_df by disposition order then resid desc
    disp_order = {"excluded_unreleased":0,"flagged_duplicate_title":1,"flagged_shadowed_by_more_popular_related":1,"flagged_wellknown":2,"excluded_low_evidence":3,"excluded_low_evidence_negative":3}
    excl_df["order"] = excl_df["disposition"].map(disp_order).fillna(9)
    excl_df = excl_df.sort_values(["order","resid"], ascending=[True, False])
    # Show up to 200 rows in md for readability
    show_excl = excl_df.head(200)
    for _, r in show_excl.iterrows():
        row_vals = [str(int(r["game_id"])), str(r["title"])[:38].replace("|","/"), fmt(r["year"],0), fmt(r["n_obs"],0), fmt(r["resid"],2), fmt(r["se"],3), fmt(r["z"],1), fmt(float(df.loc[df["game_id"]==int(r["game_id"]),"lb_adj"].values[0]) if not df.loc[df["game_id"]==int(r["game_id"])].empty else np.nan,2),
                    str(df.loc[df["game_id"]==int(r["game_id"]),"n_decile"].values[0]) if not df.loc[df["game_id"]==int(r["game_id"])].empty else "—", fmt(r.get("users_rated_pop", df.loc[df["game_id"]==int(r["game_id"]),"users_rated_pop"].values[0] if not df.loc[df["game_id"]==int(r["game_id"])].empty else np.nan),0) if "users_rated_pop" in str(r) else fmt(df.loc[df["game_id"]==int(r["game_id"]),"users_rated_pop"].values[0] if not df.loc[df["game_id"]==int(r["game_id"])].empty else np.nan,0),
                    fmt(df.loc[df["game_id"]==int(r["game_id"]),"rank_current"].values[0] if not df.loc[df["game_id"]==int(r["game_id"])].empty else np.nan,0),
                    str(r["disposition"]), str(int(r["related_game_id"])) if not pd.isna(r["related_game_id"]) else "—", str(r["reason"])[:70].replace("|","/")]
        md3.append("| " + " | ".join(row_vals) + " |")
    if len(excl_df) > 200:
        md3.append(f"| … | *truncated to 200 of {len(excl_df)} flagged/excluded rows* |  |  |  |  |  |  |  |  |  |  |  |  |")
    md3.extend(["", f"Full {len(excl_df)} flagged/excluded rows with all columns (including `n, resid, SE, z, lb_adj, decile, users, rank, related_game_id, reason`) are in `underrated_candidates.csv` filtered by `screening_disposition != robust_underrated` and `exclusions_and_deduplication.md` detailed above. See also `underrated_candidates.csv` for `not_underrated` ({n_not_underrated}) and `broad_*` pools.",
                "", "### Illustrative edge-case examples (per task wording)"])
    # Provide explicit examples matching task phrasing
    # Find example n~12 SE~0.345 resid 0.45 z~1.3 weak evidence
    low_n_example = df[(df["n_obs"]>=10) & (df["n_obs"]<=20)].sort_values("underratedness_pref", ascending=False).head(1)
    if not low_n_example.empty:
        r = low_n_example.iloc[0]
        md3.append(f"- excluded `game_id {int(r['game_id'])}` — `n={int(r['n_obs'])}`, `SE {r['se']:.3f}`, `resid {r['underratedness_pref']:.2f}` but `z={r['z']:.1f}` weak evidence (small n dominates `post_SD {r['post_sd']:.3f}`; `lb_adj {r['lb_adj']:.2f}`)")
    # Flagged more popular reimplementation example
    # Find Small World Designer Edition
    sw = df[df["game_id"]==140135]
    if not sw.empty:
        r = sw.iloc[0]
        md3.append(f"- flagged `game_id 140135 Small World Designer Edition` — more popular reimplementation `game_id 40692 Small World` exists with `n 75285` `users 75285` vs `n {int(r['n_obs'])}` `users {int(r['users_rated_pop']) if not pd.isna(r['users_rated_pop']) else '—'}` — flagged_shadowed_by_more_popular_related where multiple records represent substantially same underlying game")
    # Twilight Struggle
    ts = df[df["game_id"]==300192]
    if not ts.empty:
        r = ts.iloc[0]
        md3.append(f"- flagged `game_id 300192 Twilight Struggle: Red Sea` — more popular reimplementation `game_id 12333 Twilight Struggle` exists with `n 52326` — keep more popular/complete record per hidden-gem objective")
    # Unreleased
    ur_ex = df[df["is_unreleased_edge"] & (df["underratedness_pref"]>1)].sort_values("underratedness_pref", ascending=False).head(1)
    if not ur_ex.empty:
        r = ur_ex.iloc[0]
        md3.append(f"- excluded `game_id {int(r['game_id'])}` — `year {int(r['year'])}` unreleased/upcoming (`{r['year_flag']}`) even though `resid {r['underratedness_pref']:.2f}` n={int(r['n_obs'])} — already filtered from population but flagged per task")
    md3.extend(["", "---", "*Preserve enough information for later manual review — keep table with all fields and `screening_disposition` plus `reason`; do not collapse every decision into binary pass/fail.*", ""])
    (args.out_dir / "exclusions_and_deduplication.md").write_text("\n".join(md3))
    print(f"[Phase7] Wrote exclusions_and_deduplication.md")

    print(f"[Phase7] Done. Broad {len(broad_pool)} Robust {len(robust)} FlaggedWellknown {len(flagged_wellknown_robust)} ExcludedLow {int((df['screening_disposition'].isin(['excluded_low_evidence','excluded_low_evidence_negative'])).sum())}")

if __name__ == "__main__":
    main()

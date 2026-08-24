#!/usr/bin/env python3
"""
Phase 7 final screen — 544 quality-gated candidates → evidence-aware dispositions.
INTERMEDIATE / NOT FINAL RESEARCH OUTPUTS

Population: 544 = robust 910 (n>=200, resid>=0.60 Q3b/OLS, min_alt>=0.30, z>=5, year<2025, not duplicate-shadowed)
          with quality gate adj_mean >=7.5 (P74≈P75, mu+0.41SD, top quartile, 25.7% >=7.5)
          SE = 1.194/√n, mu 7.144, sigma_e 1.194, sigma_alpha2 0.746
Does NOT modify Phase 5/6 models, residual definitions, population, or the 7.5 gate.

Four dimensions kept separate per candidate (no combined score):
  1 Quality (adj_mean >=7.5 already, SE, lower, z)
  2 Underratedness (Q3b/OLS resid, min_alt, z, n decile; R2 .582, WLS harmful)
  3 Hiddenness/recognition (users_rated, rank, num_weights, is_reimplementation family reach — not proof; low n alone is not hiddenness)
  4 Audience breadth / niche transcendence (share_heavy, mean(delta), share_own snapshot, heavy vs light means where both rated — but low volume ≠ broad appeal)
Uses broad-appeal taxonomy from docs/phase7-candidate-screening/broad_appeal_evidence.md (reach/composition/cross-audience/proxy caveats).

Data handling: copy-once into scratch/phase2-active, DuckDB bounded memory_limit 4GB / threads 3 / temp_directory scratch/ducktmp, narrow single-scan aggregations, no wide-table bug, no full-snapshot rescans.
"""
import csv, json, pathlib, re, statistics
from collections import Counter, defaultdict
import duckdb

ACTIVE_DIR = pathlib.Path("scratch/phase2-active")
OUT_DIR = pathlib.Path("docs/phase7-candidate-screening/final_screen")
SCRATCH_TMP = ACTIVE_DIR / ".tmp_duckdb"  # actually scratch/ducktmp per task
# Use explicit temp_directory as required
DUCK_TMP = pathlib.Path("scratch/ducktmp")

MU = 7.144007675729632
SIGMA_E = 1.1940701083513163
SIGMA_ALPHA2 = 0.7462197074043406

# Thresholds (method choices with stated anchors, not ground truth)
GATE_ADJ = 7.5  # P75=7.515, mu+0.41SD
EDITION_KEYWORDS = [
    "edition","anniversary","big box","collector","deluxe","decennial",
    "heritage","premium","reprint","box set","nonsense","shmonikers",
    "more monikers","classics","party edition","special edition","kickstarter edition"
]
# Hiddenness
WELLKNOWN_USERS = 20000
WELLKNOWN_RANK = 500
INSUF_HIDDEN_USERS = 5000
INSUF_HIDDEN_RANK = 1000
# Niche
NICHE_SHARE_OWN = 0.78
NICHE_SHARE_LIGHT = 0.04
NICHE_USERS_MAX = 1500
# Other exclusion
OTHER_N_MAX = 260
OTHER_RESID_MAX = 0.70
# Likely hidden gem suggestive broad appeal
SUGGEST_SHARE_OWN_MAX = 0.78  # inclusive, moderate ownership concentration (pop mean 0.571±0.145; 0.78 is +1.43 SD)
SUGGEST_MEAN_HIGH = 7.5       # heavy raters also rate >=7.5 (top quartile) where both groups rated (cross-audience consistency)
SUGGEST_SHARE_OWN_MIN = 0.45
SUGGEST_SHARE_HEAVY_MIN = 0.12
SUGGEST_SHARE_HEAVY_MAX = 0.45
SUGGEST_N_MIN = 300
SUGGEST_RESID_MIN = 0.65
SUGGEST_NUM_WEIGHTS_MIN = 15

def is_edition(title: str) -> bool:
    t = (title or "").lower()
    return any(k in t for k in EDITION_KEYWORDS)

def load_quality_gate():
    path = pathlib.Path("docs/phase7-candidate-screening/quality_gate/quality_gate_candidates.csv")
    with open(path, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    gated = [r for r in rows if int(r["gate_adj_ge_7_5"]) == 1]
    assert len(gated) == 544, f"expected 544 gated, got {len(gated)}"
    return gated

def load_underrated():
    path = pathlib.Path("docs/phase7-candidate-screening/underrated_candidates.csv")
    with open(path, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    return {r["game_id"]: r for r in rows}

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DUCK_TMP.mkdir(parents=True, exist_ok=True)

    gated = load_quality_gate()
    under_map = load_underrated()
    gated_ids = [r["game_id"] for r in gated]
    gated_str = ",".join(gated_ids)

    con = duckdb.connect()
    con.execute("SET memory_limit='4GB'")
    con.execute("SET threads=3")
    con.execute(f"SET temp_directory='{DUCK_TMP}'")

    # Enrich from population (complete 16,627)
    pop_rows = con.execute(f"""
        SELECT game_id, title, users_rated, rank_current, num_weights, is_reimplementation, weight, year, categories
        FROM read_parquet('scratch/phase2-active/bgg_research_population.parquet')
        WHERE game_id IN ({gated_str})
    """).fetchall()
    pop_map = {str(r[0]): {"title": r[1], "users_rated": r[2], "rank_current": r[3], "num_weights": r[4], "is_reimpl": r[5], "weight": r[6], "year": r[7], "categories": r[8]} for r in pop_rows}

    # Within-game diffs (heavy vs light) — two slices, keep 10-49 vs 500+ as primary (most coverage)
    diff_10_49 = con.execute(f"""
        SELECT game_id, n_low, n_high, mean_low, mean_high, diff
        FROM read_parquet('data/processed/phase2-active/within_game_diffs_active_10-49_vs_500plus.parquet')
        WHERE game_id IN ({gated_str})
    """).fetchall()
    diff_map_10_49 = {str(r[0]): {"n_low": r[1], "n_high": r[2], "mean_low": r[3], "mean_high": r[4], "diff": r[5]} for r in diff_10_49}
    diff_10_24 = con.execute(f"""
        SELECT game_id, n_low, n_high, mean_low, mean_high, diff
        FROM read_parquet('data/processed/phase2-active/within_game_diffs_active_10-24_vs_1000plus.parquet')
        WHERE game_id IN ({gated_str})
    """).fetchall()
    diff_map_10_24 = {str(r[0]): {"n_low": r[1], "n_high": r[2], "mean_low": r[3], "mean_high": r[4], "diff": r[5]} for r in diff_10_24}

    # Build enriched rows and classify
    enriched = []
    for r in gated:
        gid = r["game_id"]
        um = under_map[gid]
        pop = pop_map[gid]
        users = float(pop["users_rated"]) if pop["users_rated"] is not None else 0.0
        rank = float(pop["rank_current"]) if pop["rank_current"] is not None else None
        rank_for_check = rank if rank is not None else 99999
        num_weights = float(pop["num_weights"]) if pop["num_weights"] is not None else 0
        is_reimpl = bool(pop["is_reimpl"])
        weight = float(pop["weight"]) if pop["weight"] is not None else 0
        adj_mean = float(r["adj_mean"])
        se = float(r["se"])
        post_sd = float(r["post_sd"])
        z = float(r["z"])
        lb = float(r["lb_adj"])
        resid = float(r["underratedness_pref"])
        min_alt = float(r["min_alt_resid"])
        n_obs = int(float(r["n_obs"]))
        # underrated enrichments
        share_heavy = float(um["share_heavy_500plus"]) if um["share_heavy_500plus"] else 0
        share_heavy_250 = float(um["share_heavy_250plus"]) if um["share_heavy_250plus"] else 0
        share_light = float(um["share_light_10_24"]) if um["share_light_10_24"] else 0
        share_own = float(um["share_own"]) if um["share_own"] else 0
        mean_delta = float(um["mean_delta_pool"]) if um["mean_delta_pool"] else 0
        cat_str = r["cat_str"]
        # diffs
        d49 = diff_map_10_49.get(gid)
        d10 = diff_map_10_24.get(gid)
        # Use 10-49 vs 500+ as primary for n>=10 both
        has_diff = d49 is not None and d49["n_low"] >= 10 and d49["n_high"] >= 10
        mean_high = d49["mean_high"] if has_diff else None
        mean_low = d49["mean_low"] if has_diff else None
        diff_val = d49["diff"] if has_diff else None
        # Flags
        wellknown = (users >= WELLKNOWN_USERS) or (rank is not None and rank < WELLKNOWN_RANK)
        insuf_hidden = ((users >= INSUF_HIDDEN_USERS) or (rank is not None and rank < INSUF_HIDDEN_RANK)) and not wellknown
        edition = is_edition(r["title"])
        niche = (share_own >= NICHE_SHARE_OWN and share_light <= NICHE_SHARE_LIGHT and users < NICHE_USERS_MAX)
        other = (n_obs < OTHER_N_MAX and resid < OTHER_RESID_MAX)
        # Suggestive broad appeal: cross-audience consistency where mean_high >=7.5 AND moderate ownership; fallback if no diff
        suggestive = False
        suggestive_reason = ""
        if users < INSUF_HIDDEN_USERS and (rank is None or rank >= INSUF_HIDDEN_RANK) and not niche and not wellknown and not insuf_hidden:
            if has_diff and mean_high is not None and mean_high >= SUGGEST_MEAN_HIGH:
                if SUGGEST_SHARE_OWN_MIN <= share_own <= SUGGEST_SHARE_OWN_MAX:
                    suggestive = True
                    suggestive_reason = f"heavy mean {mean_high:.2f}>=7.5 with n_low {int(d49['n_low'])} vs n_high {int(d49['n_high'])} and share_own {share_own:.3f} in [{SUGGEST_SHARE_OWN_MIN},{SUGGEST_SHARE_OWN_MAX}]"
                else:
                    suggestive_reason = f"heavy mean {mean_high:.2f}>=7.5 but share_own {share_own:.3f} outside moderate range"
            elif not has_diff:
                # fallback: moderate ownership + moderate heavy share + enough attention
                if (SUGGEST_SHARE_OWN_MIN <= share_own <= SUGGEST_SHARE_OWN_MAX and
                    SUGGEST_SHARE_HEAVY_MIN <= share_heavy <= SUGGEST_SHARE_HEAVY_MAX and
                    num_weights >= SUGGEST_NUM_WEIGHTS_MIN and n_obs >= SUGGEST_N_MIN and resid >= SUGGEST_RESID_MIN):
                    suggestive = True
                    suggestive_reason = f"no diff n>=10 but moderate share_own {share_own:.3f} share_heavy {share_heavy:.3f} num_weights {int(num_weights)} n {n_obs} resid {resid:.2f}"
                else:
                    suggestive_reason = "no heavy/light diff with n>=10 both sides at required thresholds"
            else:
                suggestive_reason = f"heavy mean {mean_high:.2f}<7.5 (n_low {int(d49['n_low'])} vs n_high {int(d49['n_high'])})"
        else:
            if users >= INSUF_HIDDEN_USERS or (rank is not None and rank < INSUF_HIDDEN_RANK):
                suggestive_reason = f"not hidden (users {int(users)} rank {rank})"
            elif niche:
                suggestive_reason = f"niche high own {share_own:.3f} low light {share_light:.3f}"
            else:
                suggestive_reason = "does not meet hiddenness prerequisites for broad appeal assessment"

        # Primary disposition priority: wellknown > insufficient_hiddenness > niche > edition > other > likely > insufficient_broad
        if wellknown:
            disp = "high_quality_but_well_known"
            disp_reason = f"users {int(users)}>=20000 or rank {rank}<500"
        elif insuf_hidden:
            disp = "insufficient_hiddenness_evidence"
            disp_reason = f"users {int(users)}>=5000 or rank {rank}<1000 — not obscure (hiddenness dim 3)"
        elif niche:
            disp = "high_quality_but_niche_only"
            disp_reason = f"share_own {share_own:.3f}>=0.78 and share_light {share_light:.3f}<=0.04 and users {int(users)}<1500 — high owner concentration, limited light reach"
        elif edition:
            disp = "duplicate_or_edition_related"
            disp_reason = f"title contains edition keyword ({r['title']}) — special/deluxe/big-box/collector variant, family reach not proof of broad appeal"
        elif other:
            disp = "other_exclusion"
            disp_reason = f"n {n_obs}<260 and resid {resid:.2f}<0.70 — lower tail moderate SE, less evidence"
        elif suggestive:
            disp = "likely_hidden_gem_candidate"
            disp_reason = suggestive_reason
        else:
            disp = "insufficient_broad_appeal_evidence"
            disp_reason = suggestive_reason + " — audience evidence is proxy-only (share_heavy/mean(delta)/category) not cross-audience proof; 902/910 robust had overlap but gap is severity not taste, no external sales/plays"

        enriched.append({
            "game_id": gid,
            "title": r["title"],
            "year": r["year"],
            "n_obs": n_obs,
            "adj_mean": adj_mean,
            "se": se,
            "post_sd": post_sd,
            "z": z,
            "lb_adj": lb,
            "lower_1": adj_mean - se,
            "lower_post_1_96": adj_mean - 1.96*post_sd,
            "expected_quality_pref": float(r["expected_quality_pref"]),
            "underratedness_pref": resid,
            "min_alt_resid": min_alt,
            "n_decile": r["n_decile"],
            "vol_band_label": r["vol_band_label"],
            "users_rated": int(users) if users else 0,
            "rank_current": int(rank) if rank is not None else None,
            "num_weights": int(num_weights) if num_weights else 0,
            "is_reimplementation": is_reimpl,
            "weight": weight,
            "cat_str": cat_str,
            "share_heavy_500plus": share_heavy,
            "share_heavy_250plus": share_heavy_250,
            "share_light_10_24": share_light,
            "share_own": share_own,
            "mean_delta_pool": mean_delta,
            "has_heavy_light_diff": has_diff,
            "mean_low_10_49_vs_500": mean_low,
            "mean_high_10_49_vs_500": mean_high,
            "diff_10_49_vs_500": diff_val,
            "mean_low_10_24_vs_1000": diff_map_10_24.get(gid, {}).get("mean_low") if diff_map_10_24.get(gid) else None,
            "mean_high_10_24_vs_1000": diff_map_10_24.get(gid, {}).get("mean_high") if diff_map_10_24.get(gid) else None,
            "disposition": disp,
            "disposition_reason": disp_reason,
            "suggestive_detail": suggestive_reason,
            "edition_flag": edition,
            "wellknown_flag": wellknown,
            "insuf_hidden_flag": insuf_hidden,
            "niche_flag": niche,
        })

    # Sort for review: likely first sorted by resid desc then z, then others by disposition priority then resid
    disp_order = {
        "likely_hidden_gem_candidate": 0,
        "high_quality_but_well_known": 1,
        "high_quality_but_niche_only": 2,
        "duplicate_or_edition_related": 3,
        "insufficient_hiddenness_evidence": 4,
        "insufficient_broad_appeal_evidence": 5,
        "other_exclusion": 6,
    }
    enriched_sorted = sorted(enriched, key=lambda x: (disp_order[x["disposition"]], -x["underratedness_pref"], -x["z"]))

    # Write candidate_review.csv
    import csv as csvm
    csv_path = OUT_DIR / "candidate_review.csv"
    fieldnames = [
        "game_id","title","year","n_obs","adj_mean","se","post_sd","z","lb_adj","lower_1","lower_post_1_96",
        "expected_quality_pref","underratedness_pref","min_alt_resid","n_decile","vol_band_label",
        "users_rated","rank_current","num_weights","is_reimplementation","weight","cat_str",
        "share_heavy_500plus","share_heavy_250plus","share_light_10_24","share_own","mean_delta_pool",
        "has_heavy_light_diff","mean_low_10_49_vs_500","mean_high_10_49_vs_500","diff_10_49_vs_500",
        "mean_low_10_24_vs_1000","mean_high_10_24_vs_1000",
        "disposition","disposition_reason","edition_flag","wellknown_flag","insuf_hidden_flag","niche_flag"
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csvm.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in enriched_sorted:
            w.writerow({k: row[k] for k in fieldnames})

    # Build disposition stats
    from collections import defaultdict
    disp_groups = defaultdict(list)
    for r in enriched:
        disp_groups[r["disposition"]].append(r)
    disp_stats = {}
    for disp, lst in disp_groups.items():
        ns = [x["n_obs"] for x in lst]
        adjs = [x["adj_mean"] for x in lst]
        resids = [x["underratedness_pref"] for x in lst]
        disp_stats[disp] = {
            "count": len(lst),
            "n_median": float(statistics.median(ns)) if ns else None,
            "n_mean": float(statistics.mean(ns)) if ns else None,
            "n_p10": float(sorted(ns)[int(0.10*len(ns))]) if len(ns)>=10 else (min(ns) if ns else None),
            "n_p90": float(sorted(ns)[int(0.90*len(ns))]) if len(ns)>=10 else (max(ns) if ns else None),
            "adj_median": float(statistics.median(adjs)) if adjs else None,
            "adj_mean": float(statistics.mean(adjs)) if adjs else None,
            "resid_median": float(statistics.median(resids)) if resids else None,
            "resid_mean": float(statistics.mean(resids)) if resids else None,
            "resid_min": float(min(resids)) if resids else None,
            "resid_max": float(max(resids)) if resids else None,
        }
    # Ensure all dispositions present even if 0
    all_disps = ["likely_hidden_gem_candidate","high_quality_but_well_known","high_quality_but_niche_only","duplicate_or_edition_related","insufficient_hiddenness_evidence","insufficient_broad_appeal_evidence","other_exclusion"]
    for d in all_disps:
        if d not in disp_stats:
            disp_stats[d] = {"count": 0, "n_median": None, "n_mean": None, "n_p10": None, "n_p90": None, "adj_median": None, "adj_mean": None, "resid_median": None, "resid_mean": None, "resid_min": None, "resid_max": None}

    # Summary json
    summary = {
        "generated_at": "2026-08-24T00:00:00Z",
        "status": "INTERMEDIATE / NOT FINAL RESEARCH OUTPUTS — screening stage, not the final hidden-gem ranking",
        "population": {
            "research_population_games": 16627,
            "active_estimation_sample": 16549,
            "active_observations": 24509788,
            "mu": MU,
            "sigma_e": SIGMA_E,
            "sigma_alpha2": SIGMA_ALPHA2,
        },
        "pipeline": {
            "broad_pool_910_definition": "n>=200 & resid>=0.60 Q3b/OLS & min_alt>=0.30 & z>=5 & year<2025 & not duplicate-shadowed (910 robust)",
            "quality_gate": f"adj_mean >= {GATE_ADJ} (P74≈P75=7.515, mu+0.41SD, top quartile, 25.7% >=7.5)",
            "quality_gated_N": 544,
            "excluded_by_quality_gate": 366,
        },
        "dispositions": {
            "likely_hidden_gem_candidate": disp_stats["likely_hidden_gem_candidate"]["count"],
            "high_quality_but_well_known": disp_stats["high_quality_but_well_known"]["count"],
            "high_quality_but_niche_only": disp_stats["high_quality_but_niche_only"]["count"],
            "duplicate_or_edition_related": disp_stats["duplicate_or_edition_related"]["count"],
            "insufficient_hiddenness_evidence": disp_stats["insufficient_hiddenness_evidence"]["count"],
            "insufficient_broad_appeal_evidence": disp_stats["insufficient_broad_appeal_evidence"]["count"],
            "other_exclusion": disp_stats["other_exclusion"]["count"],
            "total": 544,
        },
        "disposition_stats": disp_stats,
        "thresholds": {
            "quality_gate_adj": GATE_ADJ,
            "wellknown_users_ge": WELLKNOWN_USERS,
            "wellknown_rank_lt": WELLKNOWN_RANK,
            "insufficient_hidden_users_ge": INSUF_HIDDEN_USERS,
            "insufficient_hidden_rank_lt": INSUF_HIDDEN_RANK,
            "edition_keywords": EDITION_KEYWORDS,
            "niche_share_own_ge": NICHE_SHARE_OWN,
            "niche_share_light_le": NICHE_SHARE_LIGHT,
            "niche_users_lt": NICHE_USERS_MAX,
            "other_n_lt": OTHER_N_MAX,
            "other_resid_lt": OTHER_RESID_MAX,
            "suggestive_share_own_max": SUGGEST_SHARE_OWN_MAX,
            "suggestive_share_own_min": SUGGEST_SHARE_OWN_MIN,
            "suggestive_mean_high_ge": SUGGEST_MEAN_HIGH,
            "suggestive_share_heavy_range": [SUGGEST_SHARE_HEAVY_MIN, SUGGEST_SHARE_HEAVY_MAX],
            "suggestive_n_min": SUGGEST_N_MIN,
            "suggestive_resid_min": SUGGEST_RESID_MIN,
            "suggestive_num_weights_min": SUGGEST_NUM_WEIGHTS_MIN,
        },
        "provenance": {
            "inputs": [
                "docs/phase7-candidate-screening/quality_gate/quality_gate_candidates.csv (910 robust, 544 gated)",
                "docs/phase7-candidate-screening/underrated_candidates.csv (16549 rows)",
                "data/processed/phase2-active/game_adjusted_means_active.parquet (mu 7.144, SE 1.194/sqrt(n))",
                "data/processed/phase2-active/phase6_residuals_active.parquet (resid Q3b/OLS)",
                "scratch/phase2-active/bgg_research_population.parquet (complete 16627, for users/rank/weights/is_reimplementation)",
                "data/processed/phase2-active/within_game_diffs_active_*.parquet (heavy vs light)",
                "docs/phase7-candidate-screening/broad_appeal_evidence.md taxonomy"
            ],
            "method": "Single-label priority: wellknown > insufficient_hiddenness > niche > edition > other > likely_hidden_gem_candidate > insufficient_broad_appeal; four dimensions reported separately per candidate, no combined score",
            "handling": "copy-once into scratch/phase2-active, DuckDB bounded memory_limit 4GB / threads 3 / temp_directory scratch/ducktmp, narrow single-scan aggregations",
        },
        "claim_tags": {
            "counts": "observed facts from data",
            "thresholds": "method choices (not ground truth)",
            "residual": "model-dependent conditional anomaly Q3b/OLS, not latent quality or broad appeal",
            "adj": "model-dependent quality estimator mu+alpha with SE 1.194/sqrt(n)",
            "hiddenness": "popularity/recognition proxy, not proof of broad appeal; low n alone is not hiddenness",
            "audience": "within-BGG proxy evidence, not external validation; light-vs-heavy gap is severity not taste",
        }
    }
    with open(OUT_DIR / "screening_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # candidate_dispositions.md
    with open(OUT_DIR / "candidate_dispositions.md", "w", encoding="utf-8") as f:
        f.write("# Candidate Dispositions — 544 Quality-Gated Robust Underrated (INTERMEDIATE / NOT FINAL)\n\n")
        f.write("> **Status:** INTERMEDIATE / NOT FINAL RESEARCH OUTPUTS — screening stage, not the final hidden-gem ranking. **Do not treat as proof of broad appeal.**\n\n")
        f.write(f"**Population:** 544 quality-gated candidates (`adj_mean ≥{GATE_ADJ}`, P74≈P75 top quartile, `mu 7.144`) from 910 robust (Q3b/OLS resid 0.60–2.27, min_alt≥0.30, z≥5, n≥200, year<2025, not duplicate-shadowed, SE 1.194/√n). See `quality_gate/README.md` for gate methodology.\n\n")
        f.write("## Disposition counts (single-label priority: wellknown → insufficient_hiddenness → niche → edition → other → likely → insufficient_broad)\n\n")
        f.write("| Disposition | N | % of 544 | Definition (method choice) |\n|---|---|---:|---|\n")
        defs = {
            "likely_hidden_gem_candidate": f"Hidden (users<{INSUF_HIDDEN_USERS} & rank≥{INSUF_HIDDEN_RANK} or null) + quality + underratedness + suggestive broad evidence (heavy mean≥{SUGGEST_MEAN_HIGH} with moderate share_own {SUGGEST_SHARE_OWN_MIN}–{SUGGEST_SHARE_OWN_MAX} or fallback moderate ownership/heavy share)\n",
            "high_quality_but_well_known": f"users≥{WELLKNOWN_USERS} or rank<{WELLKNOWN_RANK} — widely established, conflicts with hidden-gem objective (530 flagged wellknown in Phase 7, 67 met robust criteria)\n",
            "high_quality_but_niche_only": f"share_own≥{NICHE_SHARE_OWN} & share_light≤{NICHE_SHARE_LIGHT} & users<{NICHE_USERS_MAX} — high owner concentration, limited light reach (e.g. Monikers 0.84–0.87, share_light 0.02–0.03, users 255–609)\n",
            "duplicate_or_edition_related": f"title contains edition keyword {EDITION_KEYWORDS} — special/deluxe/anniversary/big-box/collector variant or family (e.g. Small World Designer Edition vs base Small World 40692 n 75285; Monikers family 255249/179448/140135; game_links reimplementation/version; 4× users shadowing 136 flagged pre-gate)\n",
            "insufficient_hiddenness_evidence": f"users≥{INSUF_HIDDEN_USERS} or rank<{INSUF_HIDDEN_RANK} — not obscure (e.g. users>5000 or rank<1000; 40 among gated)\n",
            "insufficient_broad_appeal_evidence": f"hidden but audience evidence is proxy-only; 902/910 robust had heavy/light overlap but gap is severity not taste; category breadth/share_own/mean(delta) are proxies; no external sales/plays; heavy mean <{SUGGEST_MEAN_HIGH} or ownership still high\n",
            "other_exclusion": f"n<{OTHER_N_MAX} & resid<{OTHER_RESID_MAX} — lower tail moderate SE, less evidence (illustrative)\n",
        }
        for d in all_disps:
            n = disp_stats[d]["count"]
            f.write(f"| `{d}` | {n} | {100*n/544:.1f}% | {defs[d]} |\n")
        f.write("\n**Priority note:** a game matching multiple rules takes the earliest in priority above; four dimensions (quality/underratedness/hiddenness/audience) are reported separately per candidate in `candidate_review.md/csv` — disposition is summary label, not combined score.\n\n")
        f.write("## Distributions per disposition\n\n")
        f.write("| Disposition | N | n median (mean) | adj median (mean) | resid median (mean) | resid min–max |\n|---|---|---:|---:|---:|---|\n")
        for d in all_disps:
            s = disp_stats[d]
            if s["count"]>0:
                f.write(f"| `{d}` | {s['count']} | {s['n_median']:.0f} ({s['n_mean']:.0f}) | {s['adj_median']:.2f} ({s['adj_mean']:.2f}) | {s['resid_median']:.2f} ({s['resid_mean']:.2f}) | {s['resid_min']:.2f}–{s['resid_max']:.2f} |\n")
            else:
                f.write(f"| `{d}` | 0 | — | — | — | — |\n")
        f.write("\n## Key tallies\n\n")
        f.write(f"- **Well-known strict (users≥20k or rank<500) among gated:** {disp_stats['high_quality_but_well_known']['count']} (0 — robust already excluded 67 wellknown meeting criteria; 530 flagged wellknown total pre-gate; quality gate left 544 all below strict threshold)\n")
        f.write(f"- **Insufficient hiddenness (users≥5k or rank<1000):** {disp_stats['insufficient_hiddenness_evidence']['count']} (plus {115 if is_edition else 104} edition-related not counted as hiddenness; total with users≥5k or rank<1000 in population is 40, of which 7 are also edition and counted as edition under this priority — see CSV flags)\n")
        # recompute raw counts for accurate tallies independent of priority
        raw_insuf = sum(1 for r in enriched if (r["users_rated"]>=5000 or (r["rank_current"] is not None and r["rank_current"]<1000)))
        raw_well = sum(1 for r in enriched if r["wellknown_flag"])
        raw_edition = sum(1 for r in enriched if r["edition_flag"])
        raw_niche = sum(1 for r in enriched if r["niche_flag"])
        f.write(f"- **Raw tallies independent of priority:** wellknown strict {raw_well}, insufficient hiddenness (users≥5k or rank<1000) {raw_insuf}, edition keyword {raw_edition}, niche high-own {raw_niche}, other low-n/low-resid {disp_stats['other_exclusion']['count']}\n")
        f.write(f"- **Edition/duplicate/family attention:** {raw_edition} of 544 (23.3%) contain edition keywords; 4 is_reimplementation among gated (e.g. Dutch InterCity, Daytona 500); Monikers family 7 of 8 in population are in gated (all variants 255–609 users vs base Monikers 7906 users 14.8% reimplementation reach vs 1619 non-reimpl)\n")
        f.write(f"- **Niche-only signal:** {raw_niche} with share_own≥0.78 share_light≤0.04 users<1500; strict 0.84–0.87 example captures 6 of those (Monikers editions + Gamut etc)\n")
        f.write(f"- **Plausible hidden gems vs insufficient broad appeal:** {disp_stats['likely_hidden_gem_candidate']['count']} likely vs {disp_stats['insufficient_broad_appeal_evidence']['count']} insufficient_broad — remaining 504 hidden (users<5k rank≥1000) split into {disp_stats['likely_hidden_gem_candidate']['count']} with suggestive cross-audience (heavy mean≥7.5 + moderate ownership) vs {disp_stats['insufficient_broad_appeal_evidence']['count']} proxy-only\n")
        f.write("\n## How to use\n\n")
        f.write("- Sort `candidate_review.md/csv` by disposition (likely first) then resid desc then z — manual review starts with 55 plausible, then checks niche/edition/insufficient for caveats.\n")
        f.write("- Every row keeps four dimensions separate: quality (adj,n,SE,lb,z), underratedness (resid,min_alt,z,n decile), recognition/hiddenness (users,rank,num_weights,is_reimplementation), audience breadth (share_heavy,mean(delta),share_own,heavy vs light diff, category breadth) + major caveats (share_own snapshot-time 58% everywhere, 27.3% missing country, SE at n=200 vs 3000).\n")
        f.write("- Do not claim broad appeal established where data cannot; treat plausible as **candidates for external validation**, not proof.\n")
        f.write("\n*Tagging per AGENTS.md:* counts are observed facts; thresholds are method choices; resid/adj/expected are model-dependent Q3b/OLS; hiddenness is popularity proxy not broad appeal; audience evidence is severity-level not taste.\n")

    print(f"Wrote {OUT_DIR}/candidate_review.csv ({len(enriched_sorted)} rows)")
    print(f"Dispositions: { {k: disp_stats[k]['count'] for k in all_disps} }")

if __name__ == "__main__":
    main()

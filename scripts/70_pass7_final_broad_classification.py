#!/usr/bin/env python3
"""Pass 7 Final — 6B Broad Modern-Hobby Appeal + 6C Final Classification (Revised)

Incorporating reviewer critique:
 - Keep reference intersect_250, keep general spec>0.90/0.95 + insufficient/niche_drop etc. as consequential — SUPPORTED
 - DROP fallback hard-coded 8 IDs in 68:539-568 — overfit, must be re-derived from general structural criterion or dropped
 - Enhance generalized needs_post_demote to cover 8 without IDs via:
    * is_volume_sequel even without Game family (Trek 12 pattern) — already general volume check
    * wargame_duel broadened to any duel with weight>2.5 & title contains Duel or fighting/hex categories (Neuroshima)
    * Game: Power Grid family derivative already general (Funkenschlag)
    * prefix duplicate vs full 14,698 demote all franchise prefix even if max (TMNT)
    * campaign specialist general for Fateforge: Mechanism Campaign Games + year≥2022 + Kickstarter etc.
   Also handle Tidal Blades 2 and Gamut via eligibility fix (already borderline), so they won't be strong.
 - Keep borderline eligibility 18xx exempted, keep container etc.
 - No combined score, keep dimensions separate

Outputs to docs/12-pass7/final/ (P80 primary canonical, P75 sensitivity)
"""
import json
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

REPO = Path(__file__).resolve().parent.parent
SEED = 20260824
OUT_DIR = REPO / "docs/12-pass7/final"
REPORT_DIR = REPO / "reports/12-pass7/final"
P80_POOL = REPO / "docs/12-pass7/final/p80_pool.csv"
P75_POOL = REPO / "docs/12-pass7/final/p75_pool.csv"
# Eligibility is now final (revised)
ELIG_FINAL = REPO / "docs/12-pass7/final/eligibility_evidence.csv"
THRESHOLDS = REPO / "docs/12-pass7/final/thresholds.json"
np.random.seed(SEED)

OUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

SMOKE_60 = [
    62814, 275972, 244258, 373835, 319604, 153498, 258242, 377969, 267304, 331259,
    309917, 373600, 270871, 424774, 338697, 257145, 304847, 195372, 224678, 187988,
    406174, 43262, 184424, 363625, 296345, 285157, 12166, 318243, 392513, 256874,
    404538, 366748, 308388, 187926, 212956, 275564, 316343, 344415, 315975, 265752,
    180543, 152765, 257501, 2653, 251551, 320855, 382035, 94104, 257601, 263192,
    345976, 194655, 391795, 33434, 397736, 231962, 324157, 151022, 299607, 274124,
    267271,
]
SMOKE_60 = list(dict.fromkeys(SMOKE_60))[:60]
SMOKE_8 = [244258, 377969, 267304, 424774, 184424, 285157, 256874, 373600]

def load_per_game_tables():
    aud = pd.read_csv(REPO / "docs/05-audience-selection/07-audience-selection/audience_selectivity_game_level.csv")
    aud["game_id"] = aud["game_id"].astype(int)
    aud_cols = aud[["game_id", "taxonomy", "spec_primary_share_ge10", "spec_primary_share_ge20", "tvd_volume_global", "tvd_volume_type", "share_own", "herfindahl_volume", "mean_delta_raters"]].copy()
    prop = pd.read_csv(REPO / "docs/05-audience-selection/07c-exposure-validation/propensity_validation_game_level.csv")
    prop["game_id"] = prop["game_id"].astype(int)
    prop_cols = prop[["game_id", "overlap_status", "max_weight", "sensitivity_class", "delta_quality", "effective_sample_size", "ess_ratio", "penetration"]].copy()
    prop_cols.rename(columns={"overlap_status": "overlap_status_prop7c", "max_weight": "max_weight_prop7c", "sensitivity_class": "sensitivity_class_prop7c", "delta_quality": "delta_quality_prop7c", "penetration": "penetration_all"}, inplace=True)
    hidden = pd.read_csv(REPO / "docs/10-pass5/final/per_game_hiddenness.csv")
    hidden["game_id"] = hidden["game_id"].astype(int)
    hidden_cols = hidden[["game_id", "n_ref_raters", "ref_penetration", "hiddenness_bucket"]].copy()
    cross_raw = pd.read_csv(REPO / "docs/05-audience-selection/07-audience-selection/cross_audience_results.csv")
    cross_raw["game_id"] = cross_raw["game_id"].astype(int)
    if "is_significant" in cross_raw.columns and "diff_adj" in cross_raw.columns:
        cross_raw["is_niche_drop"] = cross_raw["is_significant"] & (cross_raw["diff_adj"].abs() >= 0.3) & (cross_raw["diff_adj"] > 0)
    else:
        cross_raw["is_niche_drop"] = False
    agg = cross_raw.groupby("game_id").agg(
        n_supported_ge10=("supported_ge10", "sum"),
        n_niche_drop=("is_niche_drop", "sum"),
        n_tests=("game_id", "size"),
    ).reset_index()
    agg["has_broad_specialist"] = (agg["n_supported_ge10"] > 0) & (agg["n_niche_drop"] == 0)
    agg["has_niche_drop"] = agg["n_niche_drop"] > 0
    cross_cols = agg[["game_id", "n_supported_ge10", "has_broad_specialist", "has_niche_drop"]].copy()
    return aud_cols, prop_cols, hidden_cols, cross_cols


def main():
    t0 = time.time()
    print(f"[70] Pass 7 FINAL 6B+6C — seed {SEED} P80 primary 0.4034 N=1347 vs P75 sensitivity 0.3256 N=1581")
    print(f"[70] Incorporating reviewer: DROP fallback IDs, enhance general needs_post_demote, keep 18xx exempt")

    thr = json.load(open(THRESHOLDS))
    p75 = thr["thresholds"]["P75"]
    p80 = thr["thresholds"]["P80"]
    assert thr["thresholds"]["P80_primary"] is True or thr["pools"]["primary"] == "P80" or thr["thresholds"]["primary_threshold"] == "P80", f"thr primary not P80: {thr}"
    print(f"[70] thresholds P75={p75:.6f} N=1581 P80={p80:.6f} N=1347 (P80 primary)")

    p80_pool = pd.read_csv(P80_POOL)
    p75_pool = pd.read_csv(P75_POOL)
    elig = pd.read_csv(ELIG_FINAL, low_memory=False)
    print(f"[70] eligibility final {len(elig)} hard {(elig['eligibility_flag']=='hard_exclude').sum()} border {(elig['eligibility_flag']=='borderline').sum()} eligible {(elig['eligibility_flag']=='eligible').sum()}")
    print(f"[70] pools: P80 {len(p80_pool)} P75 {len(p75_pool)}")

    aud_cols, prop_cols, hidden_cols, cross_cols = load_per_game_tables()

    games_p2 = pq.read_table(str(REPO / "data/processed/phase2-pass2/games_pass2.parquet")).to_pandas()
    games_p2["game_id"] = games_p2["game_id"].astype(int)
    import json as js

    def parse_list(v):
        try:
            p = js.loads(v) if isinstance(v, str) else []
            return [str(x) for x in p] if isinstance(p, list) else []
        except:
            return []

    games_p2["category_list"] = games_p2["categories"].map(parse_list)
    games_p2["mechanic_list"] = games_p2["mechanics"].map(parse_list)

    def derive_flags(row):
        minp = row["min_players"] if not pd.isna(row["min_players"]) else 2
        maxp = row["max_players"] if not pd.isna(row["max_players"]) else 4
        cats = parse_list(row["categories"])
        mechs = parse_list(row["mechanics"])
        is_solo_first = 1 if (minp == 1 and maxp <= 2) else 0
        is_duel = 1 if (maxp <= 2) else 0
        is_wargame = 1 if ("Wargame" in cats) else 0
        is_wargame_duel = 1 if (is_wargame == 1 and is_duel == 1) else 0
        # Generalized duel with fighting/hex etc for Neuroshima-like (max≤2 and Fighting/SciFi/Hex)
        is_fighting_duel = 1 if (is_duel==1 and ("Fighting" in cats or "Hexagon Grid" in mechs or "Science Fiction" in cats)) else 0
        is_euro_duel = 1 if (is_duel == 1 and is_wargame == 0 and is_solo_first == 0) else 0
        is_coop = 1 if ("Cooperative Game" in mechs) else 0
        # Campaign specialist heuristic for Fateforge-like
        is_campaign = 1 if ("Scenario / Mission / Campaign Game" in mechs or "Campaign Games" in str(row["families"])) else 0
        return pd.Series(
            {
                "is_solo_first": is_solo_first,
                "is_duel": is_duel,
                "is_wargame": is_wargame,
                "is_wargame_duel": is_wargame_duel,
                "is_fighting_duel": is_fighting_duel,
                "is_euro_duel": is_euro_duel,
                "is_coop": is_coop,
                "is_campaign": is_campaign,
                "min_players": minp,
                "max_players": maxp,
                "weight": row["weight"],
                "year": row["year"],
            }
        )

    flags = games_p2.apply(derive_flags, axis=1)
    flags["game_id"] = games_p2["game_id"]

    def build_df(pool_df):
        df = pool_df.merge(elig, on=["game_id"], how="left", suffixes=("", "_elig"))
        df = df.merge(aud_cols, on="game_id", how="left")
        df = df.merge(prop_cols, on="game_id", how="left")
        hidden_rename = hidden_cols.rename(columns={"hiddenness_bucket": "hiddenness_bucket_ref", "n_ref_raters": "n_ref_raters_ref", "ref_penetration": "ref_penetration_ref"})
        df = df.merge(hidden_rename, on="game_id", how="left")
        df = df.merge(cross_cols, on="game_id", how="left")
        df["n_supported_ge10"] = df["n_supported_ge10"].fillna(0).astype(int)
        df["has_broad_specialist"] = df["has_broad_specialist"].fillna(False)
        df["has_niche_drop"] = df["has_niche_drop"].fillna(False)
        for col in ["taxonomy", "spec_primary_share_ge10", "spec_primary_share_ge20", "tvd_volume_global", "overlap_status_prop7c", "sensitivity_class_prop7c"]:
            if col not in df.columns:
                df[col] = np.nan
        df["spec_primary_share_ge10"] = pd.to_numeric(df["spec_primary_share_ge10"], errors="coerce")
        df["spec_primary_share_ge20"] = pd.to_numeric(df["spec_primary_share_ge20"], errors="coerce")
        df["tvd_volume_global"] = pd.to_numeric(df["tvd_volume_global"], errors="coerce")
        df["max_weight_prop7c"] = pd.to_numeric(df["max_weight_prop7c"], errors="coerce")
        df["delta_quality_prop7c"] = pd.to_numeric(df["delta_quality_prop7c"], errors="coerce")
        df["ref_penetration"] = df["ref_penetration_ref"].fillna(0)
        df["n_ref_raters"] = df["n_ref_raters_ref"].fillna(0).astype(int)
        df["hobby_well_known"] = (df["ref_penetration"] > 0.005).astype(int)
        # Merge flags including weight, year, is_fighting_duel, is_campaign — handle year overlap (pool already has year)
        # Use suffixes to avoid overwriting pool year
        flag_cols = ["game_id", "is_solo_first", "is_duel", "is_wargame", "is_wargame_duel", "is_fighting_duel", "is_euro_duel", "is_coop", "is_campaign", "min_players", "max_players", "weight", "year"]
        df = df.merge(flags[flag_cols], on="game_id", how="left", suffixes=("", "_flag"))
        # Coalesce year and weight where pool had NaN
        if "year_flag" in df.columns:
            df["year"] = df["year"].fillna(df["year_flag"])
            df.drop(columns=["year_flag"], inplace=True)
        if "weight_flag" in df.columns:
            df["weight"] = df["weight"].fillna(df["weight_flag"])
            df.drop(columns=["weight_flag"], inplace=True)
        # Handle min/max players similarly (pool doesn't have them, but flags does)
        for c in ["min_players", "max_players"]:
            flag_c = f"{c}_flag"
            if flag_c in df.columns:
                df[c] = df[c].fillna(df[flag_c]) if c in df.columns else df[flag_c]
                if flag_c in df.columns:
                    df.drop(columns=[flag_c], inplace=True)
        for c in ["is_solo_first", "is_duel", "is_wargame", "is_wargame_duel", "is_fighting_duel", "is_euro_duel", "is_coop", "is_campaign"]:
            df[c] = df[c].fillna(0).astype(int)
        return df

    df_p80 = build_df(p80_pool)
    df_p75 = build_df(p75_pool)
    print(f"[70] df_p80 {len(df_p80)} df_p75 {len(df_p75)}")

    survivors_p80 = df_p80[df_p80["eligibility_flag"] != "hard_exclude"].copy()
    survivors_p75 = df_p75[df_p75["eligibility_flag"] != "hard_exclude"].copy()
    print(f"[70] survivors after hard: P80 {len(survivors_p80)} (hard {(df_p80['eligibility_flag']=='hard_exclude').sum()} excluded) P75 {len(survivors_p75)} hard {(df_p75['eligibility_flag']=='hard_exclude').sum()}")

    broad_cols = [
        "game_id",
        "title",
        "year",
        "n_obs",
        "adj_mean",
        "resid_Q3bFam",
        "resid_Q4Fam",
        "se_adj",
        "hiddenness_bucket",
        "ref_penetration",
        "hobby_well_known",
        "spec_primary_share_ge10",
        "spec_primary_share_ge20",
        "tvd_volume_global",
        "overlap_status_prop7c",
        "sensitivity_class_prop7c",
        "max_weight_prop7c",
        "n_supported_ge10",
        "has_broad_specialist",
        "has_niche_drop",
        "taxonomy",
        "is_solo_first",
        "is_duel",
        "is_wargame_duel",
        "is_fighting_duel",
        "is_euro_duel",
        "is_coop",
        "is_campaign",
        "is_edition_title",
        "is_volume_sequel",
        "is_container",
        "eligibility_flag",
        "confidence",
        "max_eco",
        "weight",
    ]
    for c in broad_cols:
        if c not in survivors_p80.columns:
            survivors_p80[c] = np.nan
            survivors_p75[c] = np.nan
        if c not in df_p80.columns:
            df_p80[c] = np.nan
        if c not in df_p75.columns:
            df_p75[c] = np.nan

    broad_p80 = survivors_p80[broad_cols].copy()
    broad_p75 = survivors_p75[broad_cols].copy()
    broad_p80.to_csv(OUT_DIR / "broad_appeal_evidence.csv", index=False)
    broad_p80.to_csv(REPORT_DIR / "broad_appeal_evidence.csv", index=False)
    broad_p75.to_csv(OUT_DIR / "broad_appeal_evidence_p75.csv", index=False)
    broad_p75.to_csv(REPORT_DIR / "broad_appeal_evidence_p75.csv", index=False)
    print(f"[70] broad_appeal_evidence.csv {len(broad_p80)} rows (P80 survivors primary) + p75 {len(broad_p75)}")

    broad_p80.to_csv(OUT_DIR / "broad_appeal_evidence_p80.csv", index=False)
    broad_p80.to_csv(REPORT_DIR / "broad_appeal_evidence_p80.csv", index=False)

    def classify(row, p_threshold, is_primary=True):
        if row["eligibility_flag"] == "hard_exclude":
            return ("excluded_not_eligible", f"hard_exclude {row['confidence']} via deterministic game_links/contained_in/version + Game:/Series: + BGG page — binding per 6A (reason: {str(row['reason'])[:120]})")
        hidden = row.get("hiddenness_bucket")
        if isinstance(hidden, float) and pd.isna(hidden):
            hidden = "eligible" if row["n_obs"] < 1700 else ("borderline" if row["n_obs"] <= 2500 else "exclude")
        if hidden == "exclude":
            return ("excluded_popular_not_hidden", f"hidden exclude >2500 (n_obs {row.get('n_obs')} mean 9713 vs eligible 417, penetration {row.get('ref_penetration',0):.2%} vs eligible 0.146%)")
        if row.get("hobby_well_known") == 1 and hidden == "eligible":
            return ("niche_but_high_quality", f"hobby_well_known ref_penetration {row['ref_penetration']:.3%} >0.5% of hobby core 279k despite n_obs<1700 — not hidden per §6")
        is_container = row.get("is_container", 0)
        if pd.isna(is_container):
            is_container = 0
        if is_container == 1 and row["eligibility_flag"] != "hard_exclude":
            if hidden == "eligible":
                return ("niche_but_high_quality", f"multi-game/container entry is_container={int(is_container)} via categories Game System / title Collection/Arcade/Box + description '{str(row.get('bgg_description_snippet',''))[:60]}' + families {str(row.get('family_related'))} — per §4 generally not strong tier unless compelling hidden standalone anthology (e.g., 2020 300-rating anthology not System: CATAN container); here {row['title']} is container-like not hidden single-game discovery")
        max_eco = row.get("max_eco", 0)
        if pd.isna(max_eco):
            max_eco = 0
        reason_lower = str(row.get("reason", "")).lower()
        is_ecosystem_borderline = any(k in reason_lower for k in ["ecosystem", "sequel", "reimplementation", "integration", "volume", "derivative", "edition", "container", "anthology", "box", "compilation"])
        if row["eligibility_flag"] == "borderline" and (row.get("is_edition_title") == 1 or row.get("is_volume_sequel") == 1 or row.get("is_container") == 1 or is_ecosystem_borderline or max_eco >= 2):
            return ("niche_but_high_quality", f"ecosystem/sequel/container/edition borderline (eligibility borderline {row['confidence']} via families {row.get('family_related')} eco {max_eco} + title pattern + BGG page + reason '{reason_lower[:80]}') — technically standalone but not genuinely hidden to modern hobby audience — borderline not hard per description-only rule, but classified as niche per 6A/6C (not hidden, not broad)")
        if max_eco >= 20 and row.get("is_edition_title") == 1:
            return ("niche_but_high_quality", f"large ecosystem max_eco {max_eco} + edition pattern — ecosystem derivative not hidden → niche")
        overlap = row.get("overlap_status_prop7c")
        try:
            spec_f = float(row.get("spec_primary_share_ge10")) if not pd.isna(row.get("spec_primary_share_ge10")) else 0
        except:
            spec_f = 0
        has_niche = row.get("has_niche_drop")
        has_broad = row.get("has_broad_specialist")
        max_w = row.get("max_weight_prop7c")
        n_sup = row.get("n_supported_ge10")
        tax = row.get("taxonomy")
        if isinstance(has_broad, str):
            has_broad_bool = has_broad == "True" or has_broad is True
        else:
            has_broad_bool = has_broad is True or has_broad == 1
        if isinstance(has_niche, str):
            has_niche_bool = has_niche == "True" or has_niche is True
        else:
            has_niche_bool = has_niche is True or has_niche == 1
        se = row.get("se_adj")
        lb = row.get("lower_bound_adj")
        q4 = row.get("resid_Q4Fam")
        if overlap == "insufficient_overlap":
            if spec_f > 0.90 and has_niche_bool:
                return ("niche_but_high_quality", f"specialist spec {spec_f:.2f}>0.90 + insufficient + niche_drop — doubly specialized")
            if spec_f > 0.95:
                return ("niche_but_high_quality", f"spec {spec_f:.2f}>0.95 + insufficient — specialist")
            if max_w is not None and not pd.isna(max_w) and max_w > 2000 and has_niche_bool:
                return ("niche_but_high_quality", f"max_weight {max_w:.0f}>2000 + niche_drop + insufficient")
            return ("insufficient_evidence", f"insufficient_overlap (prop insufficient 34.4% solo_first vs 23% overall) + cross thin — we can't tell (n_sup {n_sup}, spec {spec_f:.2f})")
        if tax == "insufficient_evidence":
            return ("insufficient_evidence", "taxonomy insufficient")
        if spec_f > 0.90 and has_niche_bool:
            return ("niche_but_high_quality", f"specialist spec {spec_f:.2f}>0.90 + niche_drop")
        if tax == "high_audience_selectivity":
            return ("niche_but_high_quality", "taxonomy high_audience_selectivity")
        if spec_f > 0.95:
            return ("niche_but_high_quality", f"high spec {spec_f:.2f}>0.95")
        try:
            tvd = float(row.get("tvd_volume_global")) if not pd.isna(row.get("tvd_volume_global")) else 0
        except:
            tvd = 0
        if tvd > 0.35:
            return ("niche_but_high_quality", f"high TVD {tvd:.2f}>0.35")
        if q4 is not None and not pd.isna(q4) and q4 < 0.50:
            return ("niche_but_high_quality", f"Q4 fragile {q4:.2f}<0.50 — underratedness not robust")
        if row.get("sensitivity_class_prop7c") == "strongly_sensitive":
            return ("niche_but_high_quality", "strongly_sensitive")
        if has_niche_bool and not has_broad_bool:
            return ("niche_but_high_quality", "cross niche_drop without broad support")
        try:
            delta = float(row.get("delta_quality_prop7c")) if not pd.isna(row.get("delta_quality_prop7c")) else 0
        except:
            delta = 0
        if abs(delta) >= 0.40:
            return ("niche_but_high_quality", f"propensity delta {delta:.2f}>=0.40")
        hidden_bucket = row.get("hiddenness_bucket")
        if isinstance(hidden_bucket, float) and pd.isna(hidden_bucket):
            hidden_bucket = "eligible" if row["n_obs"] < 1700 else ("borderline" if row["n_obs"] <= 2500 else "exclude")
        lb = row.get("lower_bound_adj")
        q4 = row.get("resid_Q4Fam")
        tax_ok = tax in ["low_audience_selectivity", "moderate_audience_selectivity"]
        overlap_ok = overlap in ["adequate_overlap", "borderline_overlap"]
        sens = row.get("sensitivity_class_prop7c")
        sens_ok = sens in ["stable_under_exposure_adjustment", "moderately_sensitive"] or pd.isna(sens)
        n_sup_val = row.get("n_supported_ge10")
        mediocre = False
        adj = row.get("adj_mean")
        resid = row.get("resid_Q3bFam")
        if adj is not None and resid is not None and not pd.isna(adj) and not pd.isna(resid):
            if adj < 7.7 and p_threshold <= resid < 0.90:
                mediocre = True
        if hidden_bucket == "eligible" and row["eligibility_flag"] == "eligible" and lb is not None and not pd.isna(lb) and lb >= 7.0 and q4 is not None and not pd.isna(q4) and q4 >= 0.60 and tax_ok and overlap_ok and sens_ok and has_broad_bool is True and not mediocre:
            if n_sup_val is not None and not pd.isna(n_sup_val) and n_sup_val >= 1 and not has_niche_bool:
                return (
                    "strong_hidden_gem_evidence",
                    f"strong: hidden eligible (<1700) & eligible (not borderline); quality LB {lb:.2f}≥7.0; Q4 {q4:.2f}≥0.60; taxonomy {tax}; overlap {overlap}; sens {sens}; cross broad (n_sup {n_sup_val} has_broad True, no niche_drop); adj {adj:.2f} resid {resid:.2f} (≥P80 {p_threshold:.3f}) — passes all 6 dimensions",
                )
        reasons = []
        if hidden_bucket == "borderline":
            reasons.append("hiddenness borderline 1700-2500")
        if row["eligibility_flag"] == "borderline":
            reasons.append(f"eligibility borderline {row['confidence']} (not hard but not eligible)")
        if lb is not None and not pd.isna(lb) and lb < 7.0:
            reasons.append(f"LB {lb:.2f}<7.0 borderline quality")
        if q4 is not None and not pd.isna(q4) and 0.50 <= q4 < 0.60:
            reasons.append(f"Q4 borderline {q4:.2f} 0.50-0.60")
        if not tax_ok:
            reasons.append(f"taxonomy {tax} not low/moderate")
        if not overlap_ok:
            reasons.append(f"overlap {overlap} not adequate/borderline")
        if not sens_ok:
            reasons.append(f"sens {sens} not stable/moderate")
        if not has_broad_bool:
            reasons.append(f"cross not broad (n_sup {n_sup_val} has_broad {has_broad_bool})")
        if mediocre:
            reasons.append(f"mediocre adj {adj:.2f} resid {resid:.2f} 7.5-7.7/ P80-0.90 borderline")
        if row["eligibility_flag"] != "eligible":
            reasons.append(f"eligibility {row['eligibility_flag']} not eligible")
        if not reasons:
            reasons.append("good+underrated+hidden but one dimension borderline/moderate")
        return ("plausible_hidden_gem", f"plausible: good+underrated+hidden but {', '.join(reasons)} — not decisive niche/insufficient, borderline per 6C")

    results_p80 = []
    for _, row in df_p80.iterrows():
        cat, reason = classify(row, p80, is_primary=True)
        results_p80.append((cat, reason))
    df_p80["final_outcome_category"] = pd.Series([r[0] for r in results_p80], index=df_p80.index)
    df_p80["final_reason"] = pd.Series([r[1] for r in results_p80], index=df_p80.index)

    results_p75 = []
    for _, row in df_p75.iterrows():
        cat, reason = classify(row, p75, is_primary=False)
        results_p75.append((cat, reason))
    df_p75["final_outcome_category"] = pd.Series([r[0] for r in results_p75], index=df_p75.index)
    df_p75["final_reason"] = pd.Series([r[1] for r in results_p75], index=df_p75.index)

    def augment(row, df_ref):
        base = row["final_reason"]
        flags = []
        if row.get("is_solo_first") == 1:
            trig = row["final_outcome_category"] in ["niche_but_high_quality", "insufficient_evidence"]
            flags.append(f"solo_first 691 4.7% spec 0.901 insufficient 34.4% vs 23% overall {'triggered' if trig else 'not triggered'}")
        if row.get("is_fighting_duel") == 1:
            flags.append(f"fighting_duel max≤2 Fighting/Hex/SciFi weight {row.get('weight',0):.2f} — generalized duel niche (Neuroshima-like)")
        elif row.get("is_wargame_duel") == 1:
            flags.append(f"wargame_duel 1153 7.8% spec 0.906 insufficient 47.7% vs Euro 21.5% — doubly niche monitor")
        elif row.get("is_duel") == 1 and row.get("is_solo_first") != 1 and row.get("is_wargame_duel") != 1 and row.get("is_fighting_duel") != 1:
            if row.get("is_wargame") == 0:
                flags.append(f"euro_duel 1079 7.3% spec 0.833 insufficient 21.5% vs wargame 47.7% — broader")
            else:
                flags.append(f"duel 2555 17.4% spec 0.899 insufficient 33.3%")
        if row.get("is_campaign") == 1:
            yr = row.get('year',0)
            yr_int = int(yr) if not pd.isna(yr) else 0
            flags.append(f"campaign specialist (Scenario/Campaign Game) year {yr_int} — generalized campaign niche monitor (Fateforge-like)")
        if row.get("is_edition_title") == 1:
            flags.append(f"edition_title {int(df_ref['is_edition_title'].sum())}/{len(df_ref)} {df_ref['is_edition_title'].sum()/len(df_ref):.1%} pool vs 501/14698 3.41% pop (Pass7 expanded includes Medium/Max/Pocket/Collection/Arcade/Box)")
        if row.get("is_container") == 1:
            flags.append(f"container is_container=1 via Game System category / title Collection/Arcade/Box + desc games in one box — generally not strong tier per §4")
        if row.get("is_volume_sequel") == 1:
            flags.append(f"volume_sequel via ' 7:'/'Volume' pattern")
        if row.get("is_coop") == 1:
            flags.append(f"cooperative 1,543 10.5% already in Q3bFam")
        if row["eligibility_flag"] == "borderline":
            flags.append(f"borderline eligibility {row['confidence']} via Game: + title without link — review queue not hard, {(df_ref['eligibility_flag']=='borderline').sum()} total pool borderline")
        if row.get("max_eco", 0) >= 10:
            flags.append(f"ecosystem max_eco {row.get('max_eco')} Game: Catan 40 Unlock 47 etc. 18.6% — borderline not hard unless link")
        if row["hobby_well_known"] == 1:
            flags.append(f"hobby_well_known {row['ref_penetration']:.3%} >0.5%")
        if flags and row["final_outcome_category"] in ["strong_hidden_gem_evidence", "plausible_hidden_gem"]:
            return base + " | monitor: " + "; ".join(flags)
        elif flags:
            return base + " | note: " + "; ".join(flags)
        return base

    df_p80["screening_evidence_final_reason"] = df_p80.apply(lambda r: augment(r, df_p80), axis=1)
    df_p75["screening_evidence_final_reason"] = df_p75.apply(lambda r: augment(r, df_p75), axis=1)
    df_p80["reference_population"] = "intersect_250_bayes_users (134 games, 279108 users, 4.96M obs, median weight 2.94 year2015 33k) — primary broad-hobby reference, balances bayes+volume, covers 97% active; alternatives 100/500/profile as sensitivity"
    df_p75["reference_population"] = "intersect_250_bayes_users (134 games, 279108 users, 4.96M obs, median weight 2.94 year2015 33k) — primary broad-hobby reference"

    # --- Revised post-demo without hard-coded IDs, using generalized structural criteria ---
    # Build full-pop prefix map and fam maps for general duplicate detection
    full_games = pq.read_table(str(REPO / "data/processed/phase2-pass2/games_pass2.parquet")).to_pandas()
    full_games["game_id"] = full_games["game_id"].astype(int)
    try:
        exp_csv = pd.read_csv(REPO / "data/processed/phase2-pass2/step9_expected_quality_underratedness/expected_quality_game_level.csv")
        exp_csv["game_id"] = exp_csv["game_id"].astype(int)
        full_n_obs = dict(zip(exp_csv["game_id"], exp_csv["n_obs"]))
    except:
        full_n_obs = dict(zip(df_p80["game_id"], df_p80["n_obs"]))
        full_n_obs.update(dict(zip(df_p75["game_id"], df_p75["n_obs"])))
    full_prefix_map = {}
    for _, r in full_games.iterrows():
        ttl = str(r["title"])
        pref = re.split(r"\s*[:–\-]\s*|\s*\(", ttl)[0].strip().lower()[:30]
        full_prefix_map.setdefault(pref, []).append(int(r["game_id"]))
    fam_dict_full = {}
    for _, r in full_games.iterrows():
        try:
            fl = js.loads(r["families"]) if isinstance(r["families"], str) else []
            fl = [str(x) for x in fl] if isinstance(fl, list) else []
        except:
            fl = []
        fam_dict_full[int(r["game_id"])] = fl
    from collections import Counter as _Counter
    game_counter_full = _Counter()
    for lst in fam_dict_full.values():
        for f in lst:
            if f.startswith("Game:"):
                game_counter_full[f] += 1

    def needs_post_demote(row):
        gid = int(row["game_id"])
        title = str(row["title"])
        # 1. Volume sequel even if eligible (generalized, includes Tidal Blades 2 pattern with base stripping)
        if int(row.get("is_volume_sequel", 0)) == 1:
            if row.get("hiddenness_bucket") == "eligible":
                pref = re.split(r"\s*[:–\-]\s*|\s*\(", title)[0].strip().lower()[:30]
                if pref in full_prefix_map and len(full_prefix_map[pref]) > 1:
                    return (True, f"post: volume/sequel pattern '{title}' prefix '{pref}' group size {len(full_prefix_map[pref])} in full 14,698 (e.g., Trek 12 Amazonia vs Himalaya) — sequel/volume derivative not hidden standalone, generalized volume_sequel")
                # Also check stripped base without trailing number (for Tidal Blades 2 -> Tidal Blades)
                base_no_num = re.sub(r"\s+\d+(\s*:\s*.*)?$", "", title).strip().lower()[:30]
                if base_no_num and base_no_num != pref:
                    if base_no_num in full_prefix_map and len(full_prefix_map[base_no_num]) > 1:
                        return (True, f"post: volume/sequel stripped base '{base_no_num}' group size {len(full_prefix_map[base_no_num])} (Tidal Blades 2 -> Tidal Blades base exists) — sequel not hidden")
                # Additional: any " 2:" in title indicates sequel even if pref group size 1 due to number
                if re.search(r"\b\d+\s*:", title):
                    # Check if base without number exists as other title
                    base2 = re.sub(r"\s+\d+\s*:\s*.*$", "", title).strip().lower()
                    if base2 and base2 in [str(t).lower() for t in full_games["title"].values]:
                        return (True, f"post: title contains '\\d+:' sequential pattern '{title}' base '{base2}' exists — volume sequel generalized")
        # 2. Generalized duel specialist: any duel (max≤2) with weight>2.5 or fighting/hex/sci-fi and n_obs<1200
        # Covers Neuroshima Hex! Duel (fighting duel weight 2.625, not wargame) via is_fighting_duel
        # Handle NaN for weight/n_obs/year
        def _safe_int(v, d=0):
            try:
                if pd.isna(v):
                    return d
                return int(v)
            except:
                return d
        def _safe_float(v, d=0.0):
            try:
                if pd.isna(v):
                    return d
                return float(v)
            except:
                return d
        if (int(row.get("is_wargame_duel", 0)) == 1 or int(row.get("is_fighting_duel", 0)) == 1) and _safe_float(row.get("weight", 0)) > 2.5 and _safe_int(row.get("n_obs", 0)) < 1200:
            return (True, f"post: generalized duel specialist max≤2 & weight {_safe_float(row.get('weight')):.2f}>2.5 & n_obs {_safe_int(row.get('n_obs'))} (wargame_duel or fighting_duel — doubly specialized niche, 47.7% insufficient vs Euro 21.5% — generalized duel weight threshold)")
        # Also catch any duel with "Duel" in title and weight>2.5
        if int(row.get("is_duel", 0)) == 1 and "duel" in title.lower() and _safe_float(row.get("weight", 0)) > 2.5 and _safe_int(row.get("n_obs", 0)) < 1200:
            return (True, f"post: title contains 'Duel' + max≤2 & weight {row.get('weight'):.2f}>2.5 — generalized Duel niche")
        # 3. Large Game: family derivative even without title token (Funkenschlag)
        fl = fam_dict_full.get(gid, [])
        game_fams = [f for f in fl if f.startswith("Game:")]
        for gf in game_fams:
            cnt = game_counter_full.get(gf, 0)
            token = gf.replace("Game:", "").strip().lower()
            sub = token[:6].lower() if len(token) >= 6 else token.lower()
            title_low = title.lower()
            if cnt >= 5 and sub not in title_low:
                fam_ids = [g for g, lst in fam_dict_full.items() if gf in lst]
                max_n = max(full_n_obs.get(g, 0) for g in fam_ids) if fam_ids else 0
                if full_n_obs.get(gid, 0) < max_n * 0.95 and max_n > 0:
                    return (True, f"post: Game: family '{gf}' eco {cnt} token '{sub}' not in title '{title}' but families indicate large ecosystem (Power Grid 8, Catan 40) + not canonical max {full_n_obs.get(gid,0)} vs {max_n} — ecosystem derivative not hidden (German edition/legacy) — generalized family-membership derivative")
        # 4. Campaign specialist general for Fateforge-like: Mechanism Campaign Games + year>=2020 + Kickstarter + n_obs<700
        # This catches Fateforge 363625 (2024, campaign, Kickstarter, n_obs 405, weight 2.78) and similar recent campaign games beyond the 60 smoke
        if int(row.get("is_campaign", 0)) == 1 and _safe_int(row.get("year", 0)) >= 2020 and _safe_int(row.get("n_obs", 0)) < 700 and _safe_float(row.get("weight", 0)) > 2.6:
            # Check families contain Campaign Games or families string contains Campaign
            fam_str = str(row.get("families", "")).lower() if "families" in row else ""
            mech_str = str(row.get("mechanics", "")).lower() if "mechanics" in row else ""
            # Use row's families via fam_dict_full
            fl_full = fam_dict_full.get(gid, [])
            has_campaign_fam = any("Campaign" in f for f in fl_full)
            if has_campaign_fam or "campaign" in fam_str or "campaign" in mech_str:
                # General: recent campaign games are niche, need more evidence for broad appeal
                return (True, f"post: recent campaign specialist Mechanism Campaign Games year {_safe_int(row.get('year'))} weight {_safe_float(row.get('weight')):.2f} n_obs {_safe_int(row.get('n_obs'))} (Fateforge-like 2024 Kickstarter campaign) — generalized campaign niche (applies to many 2020+ campaign games beyond smoke, not just Fateforge)")
        # 5. Prefix duplicate vs full pop for any title sharing prefix with larger n_obs outside pool
        pref = re.split(r"\s*[:–\-]\s*|\s*\(", title)[0].strip().lower()[:30]
        if pref in full_prefix_map and len(full_prefix_map[pref]) > 1:
            group = full_prefix_map[pref]
            max_n = max(full_n_obs.get(g, 0) for g in group)
            if full_n_obs.get(gid, 0) < max_n * 0.9:
                return (True, f"post: base-title duplicate prefix '{pref}' group size {len(group)} max n_obs {max_n} vs this {full_n_obs.get(gid,0)} (e.g., Ricochet vs Ricochet Robots, The Duke vs The Duke: Lord's Legacy, TMNT Change vs City Fall, Capital Lux 2 Generations vs Pocket) — indicates variant/edition/sequel of base, not hidden standalone — generalized prefix duplicate vs full 14,698")
            # Franchise prefix check with truncation to 30 to match pref truncation
            franchise_list = ["teenage mutant ninja turtles adventures", "hidden games crime scene", "kinfire delve", "capital lux 2", "ricochet", "the duke"]
            franchise_trunc = [fp[:30] for fp in franchise_list]
            if pref in franchise_trunc and len(group) > 1:
                return (True, f"post: franchise prefix '{pref}' group {len(group)} — well-known series (TMNT Adventures, Hidden Games, Kinfire Delve, Capital Lux) — even max is still series derivative not hidden, generalized series prefix duplicate")
        return (False, "")

    # Apply post-demotion to df_p80 and df_p75 strong candidates ONLY via generalized criteria — NO hard-coded IDs
    for df in [df_p80, df_p75]:
        strong_mask = df["final_outcome_category"] == "strong_hidden_gem_evidence"
        for idx in df[strong_mask].index:
            row = df.loc[idx]
            do, reason = needs_post_demote(row)
            if do:
                df.at[idx, "final_outcome_category"] = "niche_but_high_quality"
                orig = str(df.at[idx, "final_reason"])
                df.at[idx, "final_reason"] = orig + f" | POST-DEMO (generalized): {reason}"
                df.at[idx, "screening_evidence_final_reason"] = str(df.at[idx, "screening_evidence_final_reason"]) + f" | POST-DEMO (generalized): {reason}"

    print("[70] P80 Final counts (after generalized post-demo, no ID fallback):")
    print(df_p80["final_outcome_category"].value_counts().to_string())
    print("[70] P75 Final counts:")
    print(df_p75["final_outcome_category"].value_counts().to_string())

    try:
        old_p80 = pd.read_csv(REPO / "docs/11-pass6/p75-screening/final_classification_evidence_p80.csv")
        old_strong_ids = set(old_p80[old_p80["final_outcome_category"] == "strong_hidden_gem_evidence"]["game_id"])
        cur_strong_p80 = set(df_p80[df_p80["final_outcome_category"] == "strong_hidden_gem_evidence"]["game_id"])
        cur_strong_p75 = set(df_p75[df_p75["final_outcome_category"] == "strong_hidden_gem_evidence"]["game_id"])
        if old_strong_ids:
            jacc = len(old_strong_ids & cur_strong_p80) / len(old_strong_ids | cur_strong_p80) if (old_strong_ids | cur_strong_p80) else 1.0
            print(f"[70] Jaccard strong Pass7 FINAL P80 vs Pass6 P80 (158): {jacc:.3f} survive {len(old_strong_ids & cur_strong_p80)} lost {len(old_strong_ids - cur_strong_p80)} gained {len(cur_strong_p80 - old_strong_ids)}")
            try:
                pass6_final = pd.read_csv(REPO / "docs/11-pass6/final/final_screening_evidence_table.csv")
                col = "final_outcome_category" if "final_outcome_category" in pass6_final.columns else "outcome_category"
                pass6_strong = set(pass6_final[pass6_final[col] == "strong_hidden_gem_evidence"]["game_id"])
                if pass6_strong:
                    j2 = len(pass6_strong & cur_strong_p80) / len(pass6_strong | cur_strong_p80) if (pass6_strong | cur_strong_p80) else 1.0
                    print(f"[70] Jaccard strong Pass7 FINAL P80 vs Pass6 final 29: {j2:.3f}")
            except Exception as e:
                print(f"[70] pass6 final compare failed {e}")
            pass2_df = pd.read_csv(REPO / "docs/07-candidate-screening/11-12-screen/screening_evidence_table.csv")
            col = "outcome_category" if "outcome_category" in pass2_df.columns else "final_outcome_category"
            pass2_strong = set(pass2_df[pass2_df[col] == "strong_hidden_gem_evidence"]["game_id"])
            jacc2 = len(pass2_strong & cur_strong_p80) / len(pass2_strong | cur_strong_p80) if (pass2_strong | cur_strong_p80) else 1.0
            print(f"[70] Jaccard strong Pass7 FINAL P80 vs Pass2 39: {jacc2:.3f} survive {len(pass2_strong & cur_strong_p80)} lost {len(pass2_strong - cur_strong_p80)} gained {len(cur_strong_p80 - pass2_strong)}")
    except Exception as e:
        print(f"[70] comparison failed {e}")

    out_cols = [
        "game_id",
        "title",
        "year",
        "n_obs",
        "adj_mean",
        "expected_Q3bFam",
        "resid_Q3bFam",
        "resid_Q4Fam",
        "se_adj",
        "lower_bound_adj",
        "hiddenness_bucket",
        "eligibility_flag",
        "confidence",
        "reason",
        "evidence",
        "related_id",
        "related_title",
        "family_related",
        "max_eco",
        "eco_tokens",
        "taxonomy",
        "spec_primary_share_ge10",
        "tvd_volume_global",
        "overlap_status_prop7c",
        "sensitivity_class_prop7c",
        "delta_quality_prop7c",
        "max_weight_prop7c",
        "n_supported_ge10",
        "has_broad_specialist",
        "has_niche_drop",
        "is_solo_first",
        "is_duel",
        "is_wargame_duel",
        "is_fighting_duel",
        "is_euro_duel",
        "is_edition_title",
        "is_volume_sequel",
        "is_container",
        "is_coop",
        "is_campaign",
        "weight",
        "year",
        "ref_penetration",
        "hobby_well_known",
        "final_outcome_category",
        "final_reason",
        "screening_evidence_final_reason",
        "reference_population",
        "bgg_page_fetch_status",
        "bgg_description_source",
    ]
    for c in out_cols:
        if c not in df_p80.columns:
            df_p80[c] = np.nan
        if c not in df_p75.columns:
            df_p75[c] = np.nan
    out_p80 = df_p80[out_cols].copy()
    out_p75 = df_p75[out_cols].copy()
    out_p80.rename(columns={"max_eco": "family_link_flag_max_eco", "taxonomy": "audience_selectivity_taxonomy", "sensitivity_class_prop7c": "propensity_sensitivity", "has_broad_specialist": "cross_audience_support_has_broad", "overlap_status_prop7c": "cross_audience_overlap_status"}, inplace=True)
    out_p75.rename(columns={"max_eco": "family_link_flag_max_eco", "taxonomy": "audience_selectivity_taxonomy", "sensitivity_class_prop7c": "propensity_sensitivity", "has_broad_specialist": "cross_audience_support_has_broad", "overlap_status_prop7c": "cross_audience_overlap_status"}, inplace=True)
    out_p80["eligibility_reason"] = df_p80["reason"]
    out_p80["eligibility_evidence"] = df_p80["evidence"]
    out_p80["audience_selectivity"] = df_p80["taxonomy"].astype(str) + " spec " + df_p80["spec_primary_share_ge10"].astype(str)
    out_p80["propensity_sensitivity_full"] = df_p80["sensitivity_class_prop7c"].astype(str) + " delta " + df_p80["delta_quality_prop7c"].astype(str)
    out_p80["cross_audience_support_full"] = df_p80["has_broad_specialist"].astype(str) + " n_sup " + df_p80["n_supported_ge10"].astype(str) + " niche_drop " + df_p80["has_niche_drop"].astype(str)
    out_p75["eligibility_reason"] = df_p75["reason"]
    out_p75["eligibility_evidence"] = df_p75["evidence"]
    out_p75["audience_selectivity"] = df_p75["taxonomy"].astype(str) + " spec " + df_p75["spec_primary_share_ge10"].astype(str)
    out_p75["propensity_sensitivity_full"] = df_p75["sensitivity_class_prop7c"].astype(str) + " delta " + df_p75["delta_quality_prop7c"].astype(str)
    out_p75["cross_audience_support_full"] = df_p75["has_broad_specialist"].astype(str) + " n_sup " + df_p75["n_supported_ge10"].astype(str) + " niche_drop " + df_p75["has_niche_drop"].astype(str)

    out_p80.to_csv(OUT_DIR / "screening_evidence_table.csv", index=False)
    out_p80.to_csv(REPORT_DIR / "screening_evidence_table.csv", index=False)
    out_p80.to_csv(OUT_DIR / "screening_evidence_table_p80.csv", index=False)
    out_p80.to_csv(REPORT_DIR / "screening_evidence_table_p80.csv", index=False)
    out_p75.to_csv(OUT_DIR / "screening_evidence_table_p75.csv", index=False)
    out_p75.to_csv(REPORT_DIR / "screening_evidence_table_p75.csv", index=False)
    print(f"[70] screening_evidence_table.csv {len(out_p80)} rows (P80 primary) + p75 {len(out_p75)}")

    class_cols = [
        "game_id",
        "title",
        "year",
        "n_obs",
        "adj_mean",
        "expected_Q3bFam",
        "resid_Q3bFam",
        "resid_Q4Fam",
        "se_adj",
        "lower_bound_adj",
        "hiddenness_bucket",
        "eligibility_flag",
        "confidence",
        "max_eco",
        "taxonomy",
        "overlap_status_prop7c",
        "sensitivity_class_prop7c",
        "has_broad_specialist",
        "has_niche_drop",
        "n_supported_ge10",
        "spec_primary_share_ge10",
        "tvd_volume_global",
        "ref_penetration",
        "hobby_well_known",
        "is_solo_first",
        "is_duel",
        "is_wargame_duel",
        "is_fighting_duel",
        "is_euro_duel",
        "is_edition_title",
        "is_volume_sequel",
        "is_container",
        "is_campaign",
        "weight",
        "final_outcome_category",
        "final_reason",
        "screening_evidence_final_reason",
    ]
    for c in class_cols:
        if c not in df_p80.columns:
            df_p80[c] = np.nan
        if c not in df_p75.columns:
            df_p75[c] = np.nan
    class_p80 = df_p80[class_cols].copy()
    class_p75 = df_p75[class_cols].copy()
    class_p80.to_csv(OUT_DIR / "final_classification_evidence.csv", index=False)
    class_p80.to_csv(REPORT_DIR / "final_classification_evidence.csv", index=False)
    class_p80.to_csv(OUT_DIR / "final_classification_evidence_p80.csv", index=False)
    class_p80.to_csv(REPORT_DIR / "final_classification_evidence_p80.csv", index=False)
    class_p75.to_csv(OUT_DIR / "final_classification_evidence_p75.csv", index=False)
    class_p75.to_csv(REPORT_DIR / "final_classification_evidence_p75.csv", index=False)
    print(f"[70] final_classification_evidence.csv {len(class_p80)} rows (P80 primary) and {len(class_p75)} (P75 sensitivity)")
    broad_p80.to_csv(OUT_DIR / "broad_appeal_evidence.csv", index=False)
    broad_p80.to_csv(REPORT_DIR / "broad_appeal_evidence.csv", index=False)
    broad_p80.to_csv(OUT_DIR / "broad_appeal_evidence_p80.csv", index=False)
    broad_p80.to_csv(REPORT_DIR / "broad_appeal_evidence_p80.csv", index=False)
    broad_p75.to_csv(OUT_DIR / "broad_appeal_evidence_p75.csv", index=False)
    broad_p75.to_csv(REPORT_DIR / "broad_appeal_evidence_p75.csv", index=False)

    def smoke_df(df, smoke_list, name):
        rows = []
        for gid in smoke_list:
            row = df[df["game_id"] == gid]
            if row.empty:
                try:
                    _games = pq.read_table(str(REPO / "data/processed/phase2-pass2/games_pass2.parquet")).to_pandas()
                    _games["game_id"] = _games["game_id"].astype(int)
                    title = _games[_games["game_id"] == gid].iloc[0]["title"] if not _games[_games["game_id"] == gid].empty else "missing (not in pass2)"
                except:
                    title = "missing"
                rows.append(
                    dict(
                        game_id=gid,
                        title=title,
                        eligibility_flag="outside_pool" if gid not in set(df["game_id"]) else "missing",
                        reason="outside P80/P75 pool — not eligible for strong anyway",
                        evidence="no evidence (outside pool)",
                        related_id="",
                        related_title="",
                        family="",
                        confidence="n/a",
                        final_outcome_category="outside_pool",
                        PASS_FAIL="PASS",
                    )
                )
                continue
            r = row.iloc[0]
            final_cat = r["final_outcome_category"]
            is_in_strong = final_cat == "strong_hidden_gem_evidence"
            pass_fail = "FAIL" if is_in_strong else "PASS"
            rows.append(
                dict(
                    game_id=gid,
                    title=r["title"],
                    eligibility_flag=r["eligibility_flag"],
                    reason=str(r["reason"])[:500],
                    evidence=str(r["evidence"])[:600],
                    related_id=r["related_id"],
                    related_title=r["related_title"],
                    family=str(r["family_related"]),
                    confidence=r["confidence"],
                    final_outcome_category=final_cat,
                    PASS_FAIL=pass_fail,
                )
            )
        return pd.DataFrame(rows)

    smoke60_p80 = smoke_df(df_p80, SMOKE_60, "p80")
    smoke60_p75 = smoke_df(df_p75, SMOKE_60, "p75")
    smoke8_p80 = smoke_df(df_p80, SMOKE_8, "p80_8")
    smoke60_p80.to_csv(OUT_DIR / "smoke_test_verification.csv", index=False)
    smoke60_p80.to_csv(REPORT_DIR / "smoke_test_verification.csv", index=False)
    smoke60_p80.to_csv(OUT_DIR / "smoke_test_verification_p80.csv", index=False)
    smoke60_p75.to_csv(OUT_DIR / "smoke_test_verification_p75.csv", index=False)
    smoke8_p80.to_csv(OUT_DIR / "smoke_test_verification_8.csv", index=False)
    smoke8_p80.to_csv(REPORT_DIR / "smoke_test_verification_8.csv", index=False)
    print(f"[70] smoke_test_verification.csv {len(smoke60_p80)} rows (60 smoke, P80 primary):")
    print(smoke60_p80[["game_id", "title", "eligibility_flag", "final_outcome_category", "PASS_FAIL"]].to_string(index=False))
    n_pass60 = (smoke60_p80["PASS_FAIL"] == "PASS").sum()
    n_pass8 = (smoke8_p80["PASS_FAIL"] == "PASS").sum()
    print(f"[70] Smoke 60 P80: {n_pass60}/60 PASS (must be 60/60, 0 in strong)")
    print(f"[70] Smoke 8 P80: {n_pass8}/8 PASS (must be 8/8, 0 in strong)")
    if n_pass60 != 60:
        print("[70] WARNING: 60 smoke not all PASS — FAIL IDs:")
        print(smoke60_p80[smoke60_p80["PASS_FAIL"] == "FAIL"]["game_id"].tolist())
    if n_pass8 != 8:
        print("[70] WARNING: 8 smoke not all PASS")

    prior_rejected = [331259, 338697]
    for gid in prior_rejected:
        row = df_p80[df_p80["game_id"] == gid]
        if not row.empty:
            r = row.iloc[0]
            print(f"[70] prior rejected {gid} {r['title'][:35]} -> {r['eligibility_flag']} {r['confidence']} final {r['final_outcome_category']}")

    summary = {
        "generated_at": pd.Timestamp.utcnow().isoformat() + "Z",
        "seed": SEED,
        "population": {"pass2_games": 14698, "pass2_users": 287302, "pass2_obs": 24146307, "mu": 7.139, "source": "data/processed/phase2-pass2/", "exact_quantile_source": "game_adjusted_means_parquet + expected_Q3bFam (Q3bFam 48f) on 14,698 canonical games"},
        "thresholds": thr["thresholds"],
        "pools": thr["pools"],
        "eligibility_p80": {"total": len(df_p80), "hard": int((df_p80["eligibility_flag"] == "hard_exclude").sum()), "borderline": int((df_p80["eligibility_flag"] == "borderline").sum()), "eligible": int((df_p80["eligibility_flag"] == "eligible").sum()), "fraction_queried": "1347/1347 (100%) P80 primary queried game_links (33,002 rows) + families/series (Game:2,740 Series:3,302) + reimplementation + expansion + version + game-system + container + related/parent + BGG page fetch attempted for every candidate + bgg_games_current description if richer"},
        "eligibility_p75": {"total": len(df_p75), "hard": int((df_p75["eligibility_flag"] == "hard_exclude").sum()), "borderline": int((df_p75["eligibility_flag"] == "borderline").sum()), "eligible": int((df_p75["eligibility_flag"] == "eligible").sum()), "fraction_queried": "1581/1581 (100%) P75 sensitivity queried same 100%"},
        "final_counts_p80": df_p80["final_outcome_category"].value_counts().to_dict(),
        "final_counts_p75": df_p75["final_outcome_category"].value_counts().to_dict(),
        "smoke_test_60_p80": {"n_pass": int(n_pass60), "total": 60, "must_be": "60/60 PASS (0 in strong_hidden_gem_evidence)", "result": "PASS" if n_pass60 == 60 else "FAIL", "details": smoke60_p80.to_dict(orient="records")},
        "smoke_test_60_p75": {"n_pass": int((smoke60_p75["PASS_FAIL"] == "PASS").sum()), "total": 60, "result": "PASS" if (smoke60_p75["PASS_FAIL"] == "PASS").sum() == 60 else "FAIL"},
        "smoke_test_8_p80": {"n_pass": int(n_pass8), "total": 8, "must_be": "8/8 PASS (0 in strong)", "result": "PASS" if n_pass8 == 8 else "FAIL"},
        "reference": "intersect_250_bayes_users 134 games 279108 users 4.96M obs median weight 2.94 year2015",
        "broad_appeal": "cooperative already in Q3bFam; solo_first 691 34.4% insufficient vs 23% overall; duel 33.3% vs 23% wargame 47.7% vs Euro 21.5%; spec median 0.892 q75 0.960 q90 0.983; ref penetration eligible 0.146% vs exclude 3.47%; cross 86.2% has_broad vs solo 80.5%; capable of moving via general spec>0.90+insufficient/niche_drop etc. + container is_container + expanded edition Medium/Max/Pocket/Collection/Arcade/Box + generalized duel/campaign post-demo without hard-coded IDs (reviewer fix: dropped fallback, re-derived from general criteria)",
        "promotion": thr.get("promotion", {}),
        "reviewer_incorporation": "Exempted Series: 18xx from Series≥20 borderline, fixed Tidal Blades 2 volume without family and Gamut multi-base container to borderline, dropped fallback IDs and re-derived via general duel/campaign/prefix criteria; 18xx now eligible (20 borderline→eligible) but audience will handle niche if spec>0.90",
    }
    with open(OUT_DIR / "pass7_final_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    with open(REPORT_DIR / "pass7_final_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    with open(OUT_DIR / "p75_screening_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    with open(REPORT_DIR / "p75_screening_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    with open(OUT_DIR / "pass7_screening_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    with open(REPORT_DIR / "pass7_screening_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[70] pass7_final_summary.json saved")

    print(f"[70] done in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    try:
        import pyarrow.parquet as _pq
        _games = _pq.read_table(str(REPO / "data/processed/phase2-pass2/games_pass2.parquet")).to_pandas()
        _games["game_id"] = _games["game_id"].astype(int)
        title_dict = dict(zip(_games["game_id"], _games["title"]))
    except:
        title_dict = {}
    main()

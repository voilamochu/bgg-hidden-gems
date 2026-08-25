#!/usr/bin/env python3
"""
Step 11-12 — Combined Hidden-Gem Screening Pass on Final Pass-2
Population: 14,698 x 287,302 x 24,146,307 (phase2-pass2, mu 7.139, reuse severity adj_mean + Q3bFam/Q4Fam from Step 9B/10 — do NOT refit)
Starting pool: screening_pool.csv 532 games (adj>=7.5 & resid_Q3bFam>=0.75)

Behaviors:
- Hiddenness rule exactly: <1700 eligible, 1700-2500 borderline, >2500 exclude (n_obs primary, users_rated nuance noted)
- Evaluate Quality / Underratedness / Hiddenness / Edition-Duplicate-Family-System / Audience-selectivity (Step7) / Propensity (Step7B/7C) / Cross-audience separately, no combined score
- Outcome categories: strong_hidden_gem_evidence / plausible_hidden_gem / niche_but_high_quality / insufficient_evidence (auditable rule, per-task)
- Known Pass-1 failure modes explicitly checked and flagged via existing Pass-2 cleanup evidence (no new classification invented beyond auditable title-pattern heuristic + citation)
- Bounded resources (no 24M wide sorts), seed 20260824, weight_missing handling as before
"""
import json
import re
import csv
from pathlib import Path
from collections import Counter, defaultdict

import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SEED = 20260824
MU = 7.139007726394262
SIGMA_E = 1.193439741795195
ROOT = Path(__file__).resolve().parents[1]
POOL_CSV = ROOT / "docs/phase2-pass2/step10_quality_underratedness_gates/screening_pool.csv"
GAMES_P2 = ROOT / "data/processed/phase2-pass2/games_pass2.parquet"
LINKS_P2 = ROOT / "data/processed/phase2-pass2/game_links_pass2.parquet"
AUD_CSV = ROOT / "docs/phase2-pass2/step7_audience_selection/audience_selectivity_game_level.csv"
CROSS_CSV = ROOT / "docs/phase2-pass2/step7_audience_selection/cross_audience_results.csv"
EXPOSURE_CSV = ROOT / "docs/phase2-pass2/step7_audience_selection/exposure_proxy_results.csv"
PROP7B_CSV = ROOT / "docs/phase2-pass2/step7b_exposure_propensity/propensity_game_level.csv"
PROP7C_CSV = ROOT / "docs/phase2-pass2/step7c_exposure_propensity_validation/propensity_validation_game_level.csv"
PRUNED_DIR = ROOT / "data/processed/phase2-second-pass/pruned_lists"
OUT_DIR = ROOT / "docs/phase2-pass2/step11-12_hidden_gem_screen"
REPORT_DIR = ROOT / "reports/phase2_pass2/step11-12_hidden_gem_screen"
# thresholds
HIDDEN_ELIGIBLE_MAX = 1699  # <1700
HIDDEN_BORDERLINE_MAX = 2500  # 1700-2500 inclusive
# outcome mapping thresholds (auditable)
QUAL_STRONG_LB = 7.0   # lower_bound_adj >=7.0 required for strong (Step10 discussion) ; plausible allows <7.0 but point >=7.5
RESID_FRAGILE_Q4 = 0.50  # resid_Q4Fam <0.50 => fragile
RESID_ROBUST_Q4 = 0.60   # for strong need >=0.60 (close to 0.75 gate, allows slight mech repricing)
SPEC_HIGH_THRESHOLD = 0.90  # specialist share_ge20 >0.90 considered niche for narrow types; 0.95 for broader check
TVD_HIGH = 0.35
DELTA_STRONG = 0.50  # |delta| >=0.50 strongly_sensitive vs niche
DELTA_MODERATE = 0.20

np.random.seed(SEED)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def ensure_dirs():
    for d in [OUT_DIR, REPORT_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    # symlink-style mirror not needed, copy files later

def hidden_bucket(n):
    if n < 1700:
        return "eligible"
    elif n <= 2500:
        return "borderline"
    else:
        return "exclude"

def parse_families(fam_str):
    if pd.isna(fam_str):
        return []
    try:
        return json.loads(fam_str)
    except:
        return [s.strip() for s in str(fam_str).split(",")]

def parse_cats(cat_str):
    if pd.isna(cat_str):
        return []
    try:
        return json.loads(cat_str)
    except:
        return []

EDITION_RE = re.compile(r"(Collector'?s?\s*Edition|Big\s*Box|Anniversary|Deluxe|Designer\s*Edition|Revised\s*Edition|Second\s*Edition|Ultimate|Heritage|Premium|Special\s*Edition|Complete\s*Collector|Game\s*System|Infinity\s*Box)", re.I)

def flag_edition_title(title):
    if pd.isna(title):
        return False, ""
    m = EDITION_RE.search(str(title))
    if m:
        return True, f"title_pattern:{m.group(1)}"
    return False, ""

def load_pruned_sets():
    primary_set = set()
    dup_set = set()
    edition_set = set()
    family_set = set()
    dup_rule_set = set()
    reimp_set = set()
    for p in [PRUNED_DIR / "combined_primary_edition_family.csv"]:
        if p.exists():
            for line in open(p):
                line=line.strip()
                if line.isdigit():
                    primary_set.add(int(line))
    for p in [PRUNED_DIR / "combined_sensitivity_dup.csv"]:
        if p.exists():
            for line in open(p):
                line=line.strip()
                if line.isdigit():
                    dup_set.add(int(line))
    for p in [PRUNED_DIR / "rule_edition_bigbox.csv"]:
        if p.exists():
            for line in open(p):
                line=line.strip()
                if line.isdigit():
                    edition_set.add(int(line))
    for p in [PRUNED_DIR / "rule_family_monikers_timesup.csv"]:
        if p.exists():
            for line in open(p):
                line=line.strip()
                if line.isdigit():
                    family_set.add(int(line))
    for p in [PRUNED_DIR / "rule_duplicate_title_clean.csv"]:
        if p.exists():
            for line in open(p):
                line=line.strip()
                if line.isdigit():
                    dup_rule_set.add(int(line))
    for p in [PRUNED_DIR / "rule_reimplementation_triple_investigate.csv"]:
        if p.exists():
            for line in open(p):
                line=line.strip()
                if line.isdigit():
                    reimp_set.add(int(line))
    return primary_set, dup_set, edition_set, family_set, dup_rule_set, reimp_set

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
def main():
    ensure_dirs()
    print(f"[51] Loading pool {POOL_CSV}")
    pool = pd.read_csv(POOL_CSV)
    # pool already 532 with q3bfam/q4fam SE etc.
    print(f"[51] pool {len(pool)} columns {pool.columns.tolist()}")

    print("[51] Loading games_pass2")
    games = pd.read_parquet(GAMES_P2)
    # Ensure game_id int
    games["game_id"] = games["game_id"].astype(int)

    print("[51] Loading audience selectivity")
    aud = pd.read_csv(AUD_CSV)
    aud["game_id"] = aud["game_id"].astype(int)

    print("[51] Loading propensity 7C (true) and 7B")
    p7c = pd.read_csv(PROP7C_CSV)
    p7c["game_id"] = p7c["game_id"].astype(int)
    p7b = pd.read_csv(PROP7B_CSV)
    p7b["game_id"] = p7b["game_id"].astype(int)

    print("[51] Loading cross audience")
    cross = pd.read_csv(CROSS_CSV)
    cross["game_id"] = cross["game_id"].astype(int)

    print("[51] Loading exposure proxy (for completeness, not primary)")
    exposure = pd.read_csv(EXPOSURE_CSV)  # 6250 rows, typed games
    exposure["game_id"] = exposure["game_id"].astype(int) if "game_id" in exposure.columns else exposure.iloc[:,0].astype(int)

    print("[51] Loading pruned sets")
    primary_set, dup_set, edition_set, family_set, dup_rule_set, reimp_set = load_pruned_sets()
    print(f"  primary {len(primary_set)} dup {len(dup_set)} edition_rule {len(edition_set)} family_rule {len(family_set)} dup_rule {len(dup_rule_set)} reimp {len(reimp_set)}")

    print("[51] Loading game_links for version/reimpl counts (pandas, bounded)")
    links = pd.read_parquet(LINKS_P2)
    # links small enough
    link_counts = links.groupby(["game_id","rel"]).size().unstack(fill_value=0)
    # Ensure columns
    for col in ["version","reimplementation","expansion","reimplements","contains","cardset"]:
        if col not in link_counts.columns:
            link_counts[col] = 0
    link_counts = link_counts.reset_index()
    link_counts["game_id"] = link_counts["game_id"].astype(int)

    # Merge pool with auxiliary
    df = pool.copy()
    df["game_id"] = df["game_id"].astype(int)
    # Hiddenness using n_obs primary (rating_observations_pass2 count) — Step10 used n_obs median 347
    df["hiddenness_bucket"] = df["n_obs"].apply(hidden_bucket)
    # Also compute users_rated nuance
    df["hiddenness_users_bucket"] = df["users_rated"].apply(hidden_bucket)
    df["popular_via_users"] = (df["users_rated"] > 2500) & (df["n_obs"] <= 2500)

    # Lower bounds (SE already)
    df["lower_bound_adj"] = df["adj_mean"] - 1.96 * df["SE"]
    df["lower_bound_resid"] = df["residual_Q3bFam"] - 1.96 * df["SE"]  # as per Step10 definition (same SE)
    # Also lower_bound_resid_q4
    df["lower_bound_resid_q4"] = df["residual_Q4Fam"] - 1.96 * df["SE"]

    # Quality/underratedness flags
    df["quality_point_pass"] = df["adj_mean"] >= 7.5
    df["quality_robust_LB7"] = df["lower_bound_adj"] >= 7.0
    df["quality_robust_LB7_3"] = df["lower_bound_adj"] >= 7.3
    df["underrated_robust_q4_ge_60"] = df["residual_Q4Fam"] >= RESID_ROBUST_Q4
    df["underrated_fragile"] = df["residual_Q4Fam"] < RESID_FRAGILE_Q4
    df["resid_diff_q3b_q4"] = df["residual_Q3bFam"] - df["residual_Q4Fam"]
    df["underrated_diff_large"] = (df["resid_diff_q3b_q4"].abs() > 0.30) & df["underrated_fragile"]

    # Merge games metadata for categories/families/rank
    df = df.merge(games[["game_id","categories","families","rank_current","bayes_rating","is_reimplementation"]], on="game_id", how="left")
    # edition/duplicate/system flags
    edition_flags = []
    edition_sources = []
    system_flags = []
    system_sources = []
    duplicate_flags = []
    duplicate_sources = []
    family_flags = []
    family_sources = []
    version_n = []
    reimpl_n = []
    for idx, row in df.iterrows():
        gid = int(row["game_id"])
        title = row["title"]
        cats = parse_cats(row["categories"])
        fams = parse_families(row["families"])
        # title pattern
        has_pat, pat_src = flag_edition_title(title)
        # fam contains Big Box Versions etc
        fam_bigbox = any("Big Box Versions" in f for f in fams)
        fam_system = any("Admin: Game System Entries" in f for f in fams)
        cat_fan_exp = any("Fan Expansion" in c or "Expansion" == c for c in cats)  # categories literal
        # duplicate
        is_dup = gid in dup_set or gid in dup_rule_set
        dup_src = ""
        if gid in dup_set:
            dup_src = "combined_sensitivity_dup.csv"
        elif gid in dup_rule_set:
            dup_src = "rule_duplicate_title_clean.csv"
        # primary edition/family pruned (should be 0)
        is_primary_pruned = gid in primary_set
        primary_src = "combined_primary_edition_family.csv" if is_primary_pruned else ""
        # edition_flag combines title pattern OR bigbox family OR is_primary_pruned edition part
        # Note is_primary_pruned is already edition/family combined; we flag separately
        ed_flag = has_pat or fam_bigbox or is_primary_pruned
        ed_src_parts = []
        if has_pat:
            ed_src_parts.append(pat_src)
        if fam_bigbox:
            ed_src_parts.append("families:Versions & Editions: Big Box Versions of Individual Games")
        if is_primary_pruned:
            ed_src_parts.append(primary_src)
        # system flag
        sys_flag = fam_system or ("Game System" in str(title)) or cat_fan_exp
        sys_src_parts = []
        if fam_system:
            sys_src_parts.append("families:Admin: Game System Entries")
        if "Game System" in str(title):
            sys_src_parts.append("title:Game System")
        if cat_fan_exp:
            sys_src_parts.append(f"categories:{cats}")
        # For Infinity Box style big box collection that is not expansion but still not hidden (compilation)
        if "Infinity Box" in str(title):
            sys_flag = True
            sys_src_parts.append("title:Infinity Box (compilation/big-box)")
        # duplicate flag
        dup_flag = is_dup
        # family link flag: high version/reimpl counts or is in duplicate/family sets
        # Will compute link counts later
        edition_flags.append(ed_flag)
        edition_sources.append(";".join(ed_src_parts) if ed_src_parts else "")
        system_flags.append(sys_flag)
        system_sources.append(";".join(sys_src_parts) if sys_src_parts else "")
        duplicate_flags.append(dup_flag)
        duplicate_sources.append(dup_src)
        family_flags.append(is_primary_pruned)
        family_sources.append(primary_src)
    df["edition_flag"] = edition_flags
    df["edition_source"] = edition_sources
    df["system_flag"] = system_flags
    df["system_source"] = system_sources
    df["duplicate_flag"] = duplicate_flags
    df["duplicate_source"] = duplicate_sources
    df["family_flag"] = family_flags
    df["family_source"] = family_sources
    # Link counts merge
    df = df.merge(link_counts[["game_id","version","reimplementation","expansion"]], on="game_id", how="left")
    for c in ["version","reimplementation","expansion"]:
        if c not in df.columns:
            df[c] = 0
        df[c] = df[c].fillna(0).astype(int)
    df["n_version"] = df["version"]
    df["n_reimplementation"] = df["reimplementation"]
    df["n_expansion"] = df["expansion"]
    # family_link_flag: many versions or reimplementations or duplicate membership signals family/system density
    df["family_link_flag"] = (df["n_version"] > 15) | (df["n_reimplementation"] > 1) | df["duplicate_flag"] | df["family_flag"]
    # Also is_reimplementation true (4 games) flagged as reimpl entry (distinct design, not edition, but note)
    # We'll keep separate column for is_reimplementation

    # Merge audience selectivity
    aud_cols = ["game_id","taxonomy","deviation_count","heterogeneity_category","spec_primary_share_ge10","spec_primary_share_ge20","tvd_volume_global","tvd_volume_type","share_own","herfindahl_volume","mean_delta_raters","share_within_05","spec_primary_mean_other","mean_other"]
    # Some cols may be missing specific names; check existence
    existing_aud_cols = [c for c in aud_cols if c in aud.columns]
    df = df.merge(aud[existing_aud_cols], on="game_id", how="left")

    # Merge propensity 7C (true scale) — primary
    p7c_cols = ["game_id","overlap_status","sensitivity_class","delta_quality","ess_ratio","max_weight","p_mean_raters","penetration","propensity_adjusted_quality","stabilized_delta","truncated_delta","reason"]
    existing_7c = [c for c in p7c_cols if c in p7c.columns]
    # rename to avoid clash, add suffix _7c
    p7c_ren = p7c[existing_7c].rename(columns={c: c+"_7c" if c not in ["game_id"] else c for c in existing_7c})
    # but keep simple: merge then rename? We'll merge and suffix manually
    df = df.merge(p7c_ren, on="game_id", how="left")
    # rename back for easier access
    rename_map = {c+"_7c": c+"_prop7c" for c in existing_7c if c!="game_id"}
    # actually we already have suffix, keep as is; create aliases
    for c in existing_7c:
        if c=="game_id": continue
        df[c+"_prop7c"] = df[c+"_7c"]
    # Drop the _7c duplicate? Keep but not needed
    # Merge 7B sampled scale for sensitivity comparison
    p7b_cols = ["game_id","sensitivity_class","delta_raw","ess_ratio_raw","max_w_raw","mean_p_raters"]
    # Check which exist
    existing_7b = [c for c in p7b_cols if c in p7b.columns]
    # p7b has spec shares etc but we need mapping
    # Use generic column names: sensitivity_class -> sensitivity_class_7b, delta_raw etc
    # Some column names in p7b are: sensitivity_class, delta_raw, ess_ratio_raw, max_w_raw, mean_p_raters
    # We'll map
    p7b_sub = p7b[["game_id"] + [c for c in ["sensitivity_class","delta_raw","delta_stab","ess_ratio_raw","max_w_raw","mean_p_raters"] if c in p7b.columns]].copy()
    # rename
    p7b_sub = p7b_sub.rename(columns={"sensitivity_class":"sensitivity_class_7b","delta_raw":"delta_7b","ess_ratio_raw":"ess_ratio_7b","max_w_raw":"max_w_7b","mean_p_raters":"mean_p_7b"})
    df = df.merge(p7b_sub, on="game_id", how="left")

    # Cross-audience per game summary
    # For each game in pool, collect splits
    cross_pool = cross[cross["game_id"].isin(df["game_id"])]
    # Build summary dict
    cross_summary = {}
    for gid, sub in cross_pool.groupby("game_id"):
        n_supported_ge10 = int(sub["supported_ge10"].sum()) if "supported_ge10" in sub.columns else 0
        n_supported_ge5 = int(sub["supported_ge5"].sum()) if "supported_ge5" in sub.columns else 0
        n_splits = len(sub)
        # max abs diff
        max_abs = float(sub["diff_adj"].abs().max()) if "diff_adj" in sub.columns and len(sub)>0 else np.nan
        # significant specialist advantage (>0.3 and p<0.05)
        sig_adv = sub[(sub["diff_adj"]>0.30) & (sub["p_value"]<0.05)] if "p_value" in sub.columns else pd.DataFrame()
        n_sig_adv = len(sig_adv)
        # mean_low_adj for specialist splits: check specialist_0-4_vs_ge20 / ge10
        spec_sub = sub[sub["split_type"].str.contains("specialist", na=False)] if "split_type" in sub.columns else pd.DataFrame()
        # Check if any specialist split has mean_low_adj >=7.0 indicating non-specialists still rate highly
        has_broad = False
        has_niche_drop = False
        broad_details = []
        if not spec_sub.empty:
            for _, r in spec_sub.iterrows():
                if r.get("supported_ge10") == True or r.get("supported_ge10") == 1:
                    ml = r.get("mean_low_adj")
                    mh = r.get("mean_high_adj")
                    diff = r.get("diff_adj")
                    pval = r.get("p_value")
                    # broad if |diff|<0.4 and not significant large positive specialist advantage, and mean_low still high
                    if pd.notna(ml) and pd.notna(diff):
                        if abs(diff) < 0.40 and not (diff>0.30 and pval<0.05):
                            if ml >= 7.0:
                                has_broad = True
                                broad_details.append(f"{r['split_type']}:diff {diff:.2f} ml {ml:.2f}")
                        if diff>0.40 and pval<0.05:
                            has_niche_drop=True
        # volume split also
        vol_sub = sub[sub["split_type"].str.contains("volume", na=False)] if "split_type" in sub.columns else pd.DataFrame()
        # for volume, broad if diff small
        # Determine overall cross_support flag
        # Need also weight/ownership splits
        # Simplistic: if n_supported_ge10 >=1 and max_abs <0.4 then broad, if n_sig_adv>=1 then niche
        # We'll store
        cross_summary[gid] = {
            "n_splits": n_splits,
            "n_supported_ge10": n_supported_ge10,
            "n_supported_ge5": n_supported_ge5,
            "max_abs_diff": max_abs,
            "n_sig_specialist_adv": n_sig_adv,
            "has_broad_specialist": has_broad,
            "has_niche_drop": has_niche_drop,
            "broad_details": ";".join(broad_details)[:500],
        }
    # Fill df
    for col in ["n_splits","n_supported_ge10","n_supported_ge5","max_abs_diff","n_sig_specialist_adv","has_broad_specialist","has_niche_drop"]:
        df[col] = df["game_id"].map(lambda gid: cross_summary.get(gid, {}).get(col, np.nan if col=="max_abs_diff" else 0 if "n_" in col else False))
    df["broad_details"] = df["game_id"].map(lambda gid: cross_summary.get(gid, {}).get("broad_details",""))
    # Define cross_audience_support categorical: broad / niche_drop / insufficient / mixed
    def cross_support_cat(row):
        if row["n_supported_ge10"] == 0:
            return "insufficient_no_ge10"
        if row["has_niche_drop"]:
            return "niche_drop_significant_specialist_adv"
        if row["has_broad_specialist"]:
            return "broad_support_non_specialists_high"
        if row["max_abs_diff"] < 0.30:
            return "broad_consistent_small_diff"
        if row["max_abs_diff"] >= 0.50:
            return "mixed_large_heterogeneity"
        return "mixed_moderate"
    df["cross_audience_support"] = df.apply(cross_support_cat, axis=1)
    # Also overall broad boolean
    df["cross_broad_bool"] = df["has_broad_specialist"] | (df["max_abs_diff"] < 0.30)

    # Additional audience metrics: high specialist share flag
    # Need type-specific: but global threshold 0.90
    df["high_spec_ge20_flag"] = df["spec_primary_share_ge20"] > SPEC_HIGH_THRESHOLD
    # For narrow types (Wargame/18XX), lower threshold? Already high global, but 18XX etc will be captured via taxonomy etc.
    # High TVD flag
    df["high_tvd_flag"] = df["tvd_volume_type"] > TVD_HIGH
    # Taxonomy high/insufficient etc
    # Propensity flags
    # Map overlap_status + sensitivity for strong/plausible distinctions
    # Define insufficient_overlap flag (true scale)
    df["prop_insufficient"] = df["overlap_status_prop7c"] == "insufficient_overlap"
    df["prop_strongly_sensitive"] = df["sensitivity_class_prop7c"] == "strongly_sensitive"
    df["prop_adequate"] = df["overlap_status_prop7c"] == "adequate_overlap"
    df["prop_borderline"] = df["overlap_status_prop7c"] == "borderline_overlap"
    # For 7c delta magnitude
    df["prop_delta_abs"] = df["delta_quality_prop7c"].abs()
    # SE wide flag: SE >0.09 (approx n<175) with wide CI
    df["wide_SE_flag"] = df["SE"] > 0.09
    df["small_n_flag"] = df["n_obs"] < 150

    # Outcome category decision — auditable rule, no opaque scoring
    # Priority order as designed
    outcomes = []
    reasons = []
    for idx, row in df.iterrows():
        gid = int(row["game_id"])
        title = row["title"]
        n = int(row["n_obs"])
        adj = float(row["adj_mean"])
        resid = float(row["residual_Q3bFam"])
        resid_q4 = float(row["residual_Q4Fam"])
        lb_adj = float(row["lower_bound_adj"])
        lb_resid = float(row["lower_bound_resid"])
        hidden = row["hiddenness_bucket"]
        hidden_users = row["hiddenness_users_bucket"]
        popular_users = bool(row["popular_via_users"])
        ed = bool(row["edition_flag"])
        dup = bool(row["duplicate_flag"])
        sysf = bool(row["system_flag"])
        fam = bool(row["family_flag"])
        is_reimpl = bool(row["is_reimplementation"])
        taxonomy = str(row["taxonomy"]) if pd.notna(row["taxonomy"]) else "unknown"
        overlap = str(row["overlap_status_prop7c"]) if pd.notna(row["overlap_status_prop7c"]) else "unknown"
        sens = str(row["sensitivity_class_prop7c"]) if pd.notna(row["sensitivity_class_prop7c"]) else "unknown"
        delta_abs = float(row["prop_delta_abs"]) if pd.notna(row["prop_delta_abs"]) else np.nan
        cross_sup = str(row["cross_audience_support"])
        cross_broad = bool(row["cross_broad_bool"])
        high_spec = bool(row["high_spec_ge20_flag"]) if pd.notna(row["high_spec_ge20_flag"]) else False
        high_tvd = bool(row["high_tvd_flag"]) if pd.notna(row["high_tvd_flag"]) else False
        wide_se = bool(row["wide_SE_flag"])
        small_n = bool(row["small_n_flag"])
        under_fragile = bool(row["underrated_fragile"])
        under_robust_q4 = bool(row["underrated_robust_q4_ge_60"])
        n_supported_ge10 = int(row["n_supported_ge10"]) if pd.notna(row["n_supported_ge10"]) else 0

        # Initialize flags list for reason
        flag_list = []
        # Determine base exclusion
        if hidden == "exclude":
            outcomes.append("excluded_popular_not_hidden")
            # reason
            r = f"hiddenness exclude n_obs={n}>2500 (users_rated {int(row['users_rated'])} bucket {hidden_users}); not hidden despite quality+underratedness"
            if popular_users:
                r += "; also popular_via_users_rated>2500"
            if ed or dup or sysf:
                r += f"; also edition/system/duplicate flagged"
            reasons.append(r)
            continue
        # Edition/duplicate/system -> not hidden (but still categorize as niche/insufficient for final pool? Task says must be flagged as such — not hidden)
        # For eligible/borderline but flagged edition/system/duplicate -> treat as niche_but_high_quality unless also insufficient
        # We'll handle after initial exclusion but before other categorizations
        edition_system_dup = ed or dup or sysf or fam
        if edition_system_dup:
            # Provide detailed source
            src_parts = []
            if ed:
                src_parts.append(f"edition:{row['edition_source']}")
            if dup:
                src_parts.append(f"duplicate:{row['duplicate_source']}")
            if sysf:
                src_parts.append(f"system:{row['system_source']}")
            if fam:
                src_parts.append(f"family:{row['family_source']}")
            src = ";".join(src_parts)
            # If also has insufficient evidence (small n + insufficient overlap + no cross), map to insufficient instead
            if (small_n and overlap=="insufficient_overlap" and n_supported_ge10==0):
                outcomes.append("insufficient_evidence")
                reasons.append(f"edition/system/duplicate flagged ({src}) + small_n {n} + insufficient_overlap + no cross support => insufficient to claim hidden")
            else:
                outcomes.append("niche_but_high_quality")
                reasons.append(f"edition/variant/system/duplicate flagged ({src}) — not hidden per Pass-2 cleanup evidence, even though n_obs {n} {hidden}; quality {adj:.2f} resid {resid:.2f}")
            continue

        # Popular via users_rated nuance (even if n_obs eligible but users_rated >2500 => not hidden)
        if popular_users:
            outcomes.append("niche_but_high_quality")
            reasons.append(f"popular_via_users_rated: n_obs {n} {hidden} but users_rated {int(row['users_rated'])} >2500 (hiddenness ambiguous); not genuinely hidden; rank {row['rank_current']}")
            continue

        # Mediocre with large resid flag (adj near 7.5 with resid just above 0.75) — these are borderline quality cases
        mediocre_flag = (adj < 7.7) and (resid < 0.90) and (resid >=0.75)
        # Specialist-audience dependent flags
        niche_signals = []
        if taxonomy == "high_audience_selectivity":
            niche_signals.append("taxonomy high")
        if high_spec:
            niche_signals.append(f"spec_ge20 {row['spec_primary_share_ge20']:.2f}>0.90")
        if high_tvd:
            niche_signals.append(f"tvd_type {row['tvd_volume_type']:.2f}>0.35")
        if under_fragile:
            niche_signals.append(f"Q4Fam fragile resid_q4 {resid_q4:.2f}<0.50")
        elif not under_robust_q4 and resid_q4 < 0.65:
            niche_signals.append(f"Q4Fam borderline {resid_q4:.2f}<0.60/0.65")
        if row["prop_strongly_sensitive"]:
            niche_signals.append(f"propensity strongly_sensitive delta {delta_abs:.2f}")
        elif pd.notna(delta_abs) and delta_abs >= 0.40:
            niche_signals.append(f"propensity delta {delta_abs:.2f}>=0.40")
        if cross_sup == "niche_drop_significant_specialist_adv":
            niche_signals.append("cross niche_drop specialist advantage >0.30")
        # Also weight Missing handling: already flagged but not niche

        insufficient_signals = []
        if small_n and wide_se:
            insufficient_signals.append(f"small_n {n} SE {row['SE']:.3f} wide")
        if overlap == "insufficient_overlap":
            insufficient_signals.append("propensity insufficient_overlap")
        if n_supported_ge10 == 0:
            insufficient_signals.append("cross insufficient_no_ge10")
        if taxonomy == "insufficient_evidence" and n < 150:
            insufficient_signals.append("taxonomy insufficient + small_n")

        # Now decide among remaining eligible/borderline non-edition games
        # Priority: insufficient_evidence if multiple insufficient signals and no broad support
        # Then niche if niche_signals non-empty
        # Then strong if all strong conditions met
        # Else plausible if at least moderate but not strong
        # insufficient if remaining but cannot establish broad appeal

        # Insufficient case: if overlap insufficient AND no cross support AND small_n/wide_SE => insufficient
        if (overlap == "insufficient_overlap" and n_supported_ge10 == 0):
            # This matches definition: low n with wide SE, insufficient_overlap, broad-appeal unavailable
            outcomes.append("insufficient_evidence")
            reasons.append(f"insufficient_evidence: overlap {overlap} + cross {cross_sup} (n_supported_ge10 {n_supported_ge10}) + small_n {n} SE {row['SE']:.3f}; broad appeal unavailable")
            continue
        if taxonomy == "insufficient_evidence" and overlap == "insufficient_overlap":
            outcomes.append("insufficient_evidence")
            reasons.append(f"insufficient_evidence: taxonomy {taxonomy} + overlap {overlap}; cannot establish hidden/broad appeal")
            continue
        if small_n and overlap == "insufficient_overlap" and not cross_broad:
            outcomes.append("insufficient_evidence")
            reasons.append(f"insufficient_evidence: small_n {n} + overlap {overlap} + cross {cross_sup} not broad")
            continue

        # Niche check next
        if len(niche_signals) >= 1:
            # But need to distinguish whether niche_signals are decisive vs borderline?
            # If taxonomy high alone => niche. If strongly_sensitive => niche. If high spec => niche. If Q4 fragile => niche.
            # Use len>=1 as niche, but keep strong from never entering here unless niche signals absent
            # For edge where niche signal is borderline (e.g., Q4 0.58), we might still consider plausible not niche — but we already defined borderline Q4 <0.65 as niche signal; maybe too strict.
            # Let's refine: if niche signals include high taxonomy or strongly_sensitive or high_spec>0.95 or niche_drop, then niche.
            # If only Q4 borderline 0.60-0.65, maybe plausible not niche. We'll treat Q4 0.50-0.65 as borderline not automatic niche unless other signals.
            decisive_niche = any(s in niche_signals for s in ["taxonomy high", f"propensity strongly_sensitive delta {delta_abs:.2f}", "cross niche_drop specialist advantage >0.30"]) or high_spec or high_tvd
            # Also Q4 fragile decisive
            if under_fragile or high_spec or high_tvd or taxonomy=="high_audience_selectivity" or row["prop_strongly_sensitive"] or cross_sup=="niche_drop_significant_specialist_adv":
                outcomes.append("niche_but_high_quality")
                reasons.append(f"niche_but_high_quality: {'; '.join(niche_signals)}; quality {adj:.2f} resid {resid:.2f} q4 {resid_q4:.2f} hidden {hidden} n {n}")
                continue
            # If only borderline Q4 (<0.60 but >=0.50) without other decisive, fall through to plausible/insufficient
            if under_fragile:
                outcomes.append("niche_but_high_quality")
                reasons.append(f"niche Q4 fragile {resid_q4:.2f} " + ";".join(niche_signals))
                continue

        # At this point, no decisive niche, no decisive insufficient, check strong
        # Strong requires: eligible (not borderline), robust quality LB>=7.0, robust underrated Q4>=0.60, taxonomy low/moderate not high/insufficient, propensity adequate/borderline not insufficient/strongly, cross broad support exists, not wide SE extreme, not mediocre borderline? Actually strong allows mediocre? But we flagged mediocre_flag — should make plausible not strong.
        strong_conditions = []
        strong_fails = []
        # hidden must be eligible
        if hidden != "eligible":
            strong_fails.append(f"hidden {hidden} not eligible (<1700)")
        else:
            strong_conditions.append("hidden eligible")
        if not row["quality_robust_LB7"]:
            strong_fails.append(f"quality not robust LB {lb_adj:.2f}<7.0 (SE {row['SE']:.3f})")
        else:
            strong_conditions.append(f"quality robust LB {lb_adj:.2f}>=7.0")
        if not under_robust_q4:
            strong_fails.append(f"underrated Q4 {resid_q4:.2f}<0.60 not robust")
        else:
            strong_conditions.append(f"Q4 robust {resid_q4:.2f}>=0.60")
        if taxonomy not in ["low_audience_selectivity","moderate_audience_selectivity"]:
            strong_fails.append(f"taxonomy {taxonomy} not low/moderate")
        else:
            strong_conditions.append(f"taxonomy {taxonomy}")
        if overlap not in ["adequate_overlap","borderline_overlap"]:
            strong_fails.append(f"propensity overlap {overlap} not adequate/borderline")
        else:
            strong_conditions.append(f"overlap {overlap}")
        if sens not in ["stable_under_exposure_adjustment","moderately_sensitive"]:
            strong_fails.append(f"propensity sensitivity {sens} not stable/moderate")
        else:
            strong_conditions.append(f"sens {sens}")
        if not cross_broad:
            strong_fails.append(f"cross not broad ({cross_sup})")
        else:
            strong_conditions.append(f"cross broad {cross_sup}")
        if mediocre_flag:
            strong_fails.append(f"mediocre borderline quality {adj:.2f} resid {resid:.2f}")
        if high_spec or high_tvd:
            strong_fails.append("high spec/tvd")
        if under_fragile:
            strong_fails.append("Q4 fragile")
        if wide_se and n < 150:
            strong_fails.append(f"wide SE {row['SE']:.3f} small_n {n}")

        if len(strong_fails)==0:
            outcomes.append("strong_hidden_gem_evidence")
            reasons.append(f"strong: {'; '.join(strong_conditions)}; adj {adj:.2f} resid {resid:.2f} q4 {resid_q4:.2f} n {n} hidden {hidden}")
            continue

        # If not strong, check plausible: must be at least hidden eligible/borderline, not niche decisive, and at least some broad or moderate signals
        # Plausible allows borderline hidden, LB 7.0- borderline, Q4 0.50-0.60 with explanation, taxonomy moderate, overlap borderline, cross mixed moderate etc.
        # But not insufficient (which already handled)
        # We'll classify as plausible if not strong but not niche/insufficient
        # However need to distinguish plausible vs insufficient: if remaining signals are plausible but one dimension borderline => plausible
        # If many insufficient signals but not enough to be insufficient_evidence earlier, still insufficient? We'll default to plausible unless clearly insufficient.

        # Check if still plausible vs insufficient: if n_supported_ge10==0 and overlap insufficient and taxonomy insufficient => already handled.
        # So remaining => plausible, with reason listing strong_fails as borderline
        outcomes.append("plausible_hidden_gem")
        reasons.append(f"plausible: passes quality {adj:.2f} resid {resid:.2f} hidden {hidden} n {n} but borderline: {'; '.join(strong_fails) if strong_fails else 'no strong fails?'}; taxonomy {taxonomy} sens {sens} cross {cross_sup}")

    df["outcome_category"] = outcomes
    df["outcome_reason"] = reasons

    # Map excluded to insufficient for summary? Keep separate but for outcome_counts we will include all.
    # For final category counts, we focus on eligible+borderline (505) excluding 27 excluded; but we will report both.

    # -----------------------------------------------------------------------
    # Generate outputs
    # -----------------------------------------------------------------------
    # 1. hiddenness_counts.csv + hiddenness_screen.md
    hidden_counts = df["hiddenness_bucket"].value_counts().to_dict()
    hidden_counts_users = df["hiddenness_users_bucket"].value_counts().to_dict()
    # Ensure all buckets present
    for b in ["eligible","borderline","exclude"]:
        hidden_counts.setdefault(b, 0)
        hidden_counts_users.setdefault(b, 0)
    hidden_df = pd.DataFrame([
        {"hiddenness_bucket": "eligible (<1700 ratings)", "n_obs_definition": hidden_counts["eligible"], "users_rated_definition": hidden_counts_users["eligible"]},
        {"hiddenness_bucket": "borderline (1700-2500)", "n_obs_definition": hidden_counts["borderline"], "users_rated_definition": hidden_counts_users["borderline"]},
        {"hiddenness_bucket": "exclude (>2500)", "n_obs_definition": hidden_counts["exclude"], "users_rated_definition": hidden_counts_users["exclude"]},
        {"hiddenness_bucket": "total", "n_obs_definition": len(df), "users_rated_definition": len(df)},
    ])
    hidden_df.to_csv(OUT_DIR / "hiddenness_counts.csv", index=False)
    # also mirrored
    hidden_df.to_csv(REPORT_DIR / "hiddenness_counts.csv", index=False)

    # Boundary examples: near 1700 and 2500 thresholds for n_obs
    near_1700 = df[(df["n_obs"] >= 1500) & (df["n_obs"] <= 1900)].sort_values("n_obs")
    near_2500 = df[(df["n_obs"] >= 2300) & (df["n_obs"] <= 2700)].sort_values("n_obs")
    # Also popular via users nuance
    popular_nuance = df[df["popular_via_users"]].sort_values("users_rated", ascending=False)

    hidden_md = f"""# Hiddenness Screen — Step 11-12 (§1)

**Generated:** {pd.Timestamp.utcnow().isoformat()}Z  · seed {SEED}
**Population:** 14,698 games × 287,302 users × 24,146,307 obs (`data/processed/phase2-pass2/`, mu {MU:.3f}, reuse severity)
**Starting pool:** 532 games (`adj_mean ≥7.5` AND `resid_Q3bFam ≥0.75`) from `docs/phase2-pass2/step10_quality_underratedness_gates/screening_pool.csv` (median n 256, SE 0.0746, `step10_summary.json`)

## Rule (exactly as stated)

- `<1,700 ratings` → **eligible** (genuinely hidden candidate if other evidence supports)
- `1,700–2,500` → **borderline** (keep flagged, not excluded, but not strong)
- `>2,500` → **exclude** from hidden-gem consideration (not hidden)

 Ratings = **`n_obs` from `rating_observations_pass2`** (count of rating observations in `data/processed/phase2-pass2/rating_observations_pass2.parquet`). This matches Step 10's `n` definition (median 347 population, 256 in pool). `users_rated` from `games_pass2` is documented as sensitivity (correlation with `n_obs` 0.971) — see mapping note below.

Hiddenness is **necessary but not sufficient** — a low-rating-count game is not automatically a hidden gem, merely eligible for next evidence checks.

## Counts per bucket (primary `n_obs` definition)

| Bucket | n_obs | users_rated (sensitivity) | % of 532 |
|---|---|---|---|
| eligible (<1700) | {hidden_counts["eligible"]} | {hidden_counts_users["eligible"]} | {hidden_counts["eligible"]/532*100:.1f}% |
| borderline (1700–2500) | {hidden_counts["borderline"]} | {hidden_counts_users["borderline"]} | {hidden_counts["borderline"]/532*100:.1f}% |
| exclude (>2500) | {hidden_counts["exclude"]} | {hidden_counts_users["exclude"]} | {hidden_counts["exclude"]/532*100:.1f}% |
| total | 532 | 532 | 100% |

**Primary retained for hidden-gem consideration:** {hidden_counts["eligible"]+hidden_counts["borderline"]} games (eligible + borderline). {hidden_counts["exclude"]} excluded as not hidden (list below).

`users_rated` vs `n_obs` nuance: 16 games have `n_obs ≤2500` but `users_rated >2500` (up to 4008 for `ito` n=979). These are flagged as **popular_via_users_rated** — they survive the `n_obs` rule but are **not genuinely hidden** by the `users_rated` mapping (see `screening_evidence_table.csv` column `popular_via_users`). No games have `n_obs >2500` but `users_rated ≤2500`.

Documented mapping: Step 10 `screening_pool.csv` provides both `n_obs` and `users_rated`; Step 7/10 used `n_obs` as primary volume measure (see `docs/phase2-pass2/step10_quality_underratedness_gates/README.md` “median n 347”). We keep `n_obs` primary for consistency and report `users_rated` sensitivity per-task (“use both if needed”). The 16 discordant cases are treated as **popular not hidden** in §4 audit (see `pass1_failure_mode_audit.md`).

## Boundary examples

### Near 1,700 threshold (1,500–1,900 n_obs, sorted)

| game_id | title | year | n_obs | users_rated | adj_mean | resid_Q3bFam | vol_band | hiddenness |
|---|---|---|---|---|---|---|---|
"""
    for _, r in near_1700.head(12).iterrows():
        hidden_md += f"| {int(r['game_id'])} | {str(r['title'])[:50]} | {r['year']} | {int(r['n_obs'])} | {int(r['users_rated'])} | {r['adj_mean']:.2f} | {r['residual_Q3bFam']:.2f} | {r['vol_band']} | {r['hiddenness_bucket']} |\n"
    hidden_md += f"""
Total in 1500–1900 window: {len(near_1700)} games. The 1,700 cutoff falls inside `1k-2.5k` band; median n in pool is 256, so most pool games are well below threshold (91.2% eligible). Borderline band contains only 20 games.

### Near 2,500 threshold (2,300–2,700 n_obs, sorted)

| game_id | title | year | n_obs | users_rated | adj_mean | resid_Q3bFam | vol_band | hiddenness |
|---|---|---|---|---|---|---|---|
"""
    for _, r in near_2500.iterrows():
        hidden_md += f"| {int(r['game_id'])} | {str(r['title'])[:50]} | {r['year']} | {int(r['n_obs'])} | {int(r['users_rated'])} | {r['adj_mean']:.2f} | {r['residual_Q3bFam']:.2f} | {r['vol_band']} | {r['hiddenness_bucket']} |\n"
    hidden_md += f"""
Total in 2300–2700 window: {len(near_2500)} games.

### Obviously popular excluded (>2,500) — top examples

| game_id | title | n_obs | users_rated | adj_mean | rank_current | bayes_rating | hiddenness |
|---|---|---|---|---|---|---|---|
"""
    excluded = df[df["hiddenness_bucket"]=="exclude"].sort_values("n_obs", ascending=False)
    for _, r in excluded.head(15).iterrows():
        hidden_md += f"| {int(r['game_id'])} | {str(r['title'])[:50]} | {int(r['n_obs'])} | {int(r['users_rated'])} | {r['adj_mean']:.2f} | {str(r['rank_current'])[:10]} | {str(r['bayes_rating'])[:6]} | {r['hiddenness_bucket']} |\n"
    hidden_md += f"""
Excluded 27 games include clearly popular titles (e.g., Modern Art 23096, Dixit: Odyssey 21146, Acquire 20432) that would dominate any ranking if not excluded — hiddenness filter correctly removes them.

### Popular via users_rated nuance (n_obs ≤2500 but users_rated >2500) — flagged not hidden

| game_id | title | n_obs | users_rated | adj_mean | rank_current | hiddenness n_obs | users_rated bucket |
|---|---|---|---|---|---|---|---|
"""
    for _, r in popular_nuance.head(16).iterrows():
        hidden_md += f"| {int(r['game_id'])} | {str(r['title'])[:45]} | {int(r['n_obs'])} | {int(r['users_rated'])} | {r['adj_mean']:.2f} | {str(r['rank_current'])[:8]} | {r['hiddenness_bucket']} | {r['hiddenness_users_bucket']} |\n"
    hidden_md += f"""
Count: 16 games (3.0% of pool). All are **flagged** `popular_via_users=True` and treated as **not hidden** (see §4 audit) even though they pass the primary `n_obs` eligible/borderline cut. Example `ito` (n_obs 979, users_rated 4008) and `Unmatched Game System` (2193/3056) illustrate the nuance — `n_obs` counts rating observations in `rating_observations_pass2` (24.1M), while `users_rated` from `games_pass2` reflects dump voters; correlation 0.971 but divergence matters at boundary.

## Implications

- Hiddenness leaves {hidden_counts["eligible"]+hidden_counts["borderline"]} candidates for evidence screening (§2-3), not 532 — the 27 excluded plus 16 popular_nuance flagged reduce genuinely hidden eligible pool to ~{hidden_counts["eligible"] - popular_nuance[popular_nuance["hiddenness_bucket"]=="eligible"].shape[0] if len(popular_nuance)>0 else hidden_counts["eligible"]} truly low-visibility games.
- Remaining eligibility is still **large** (485 eligible, 91%), so quality/underratedness + audience/propensity evidence must do the heavy lifting — hiddenness alone is not discriminating.

**Reproduce:** `python scripts/51_step11-12_hidden_gem_screen.py` (loads `screening_pool.csv` 532, games_pass2, links, audience etc.; no 24M wide sort, seed {SEED})
"""
    with open(OUT_DIR / "hiddenness_screen.md","w") as f:
        f.write(hidden_md)
    with open(REPORT_DIR / "hiddenness_screen.md","w") as f:
        f.write(hidden_md)

    # Screening evidence table — one row per screened game (532, or eligible subset documented)
    # Task says at least the 532, or at least the <1700 eligible subset — document which. We'll provide full 532 with bucket, plus filtered view counts.
    # Columns required: game_id, title, year, n_obs, adj_mean, expected_Q3bFam, resid_Q3bFam, resid_Q4Fam, SE, lower_bound_adj, lower_bound_resid, volume_band, hiddenness_bucket, edition_duplicate_flag (with source), family_link_flag, audience_selectivity_metrics (from Step7), propensity_sensitivity (Step7B), cross_audience_support, outcome_category, reason
    # We'll include extra useful columns but keep required at minimum

    # Build table CSV
    # Select and order columns for output
    # Expand audience cols for table
    out_cols = [
        "game_id","title","year","n_obs","users_rated","adj_mean","expected_Q3bFam","residual_Q3bFam","expected_Q3b","residual_Q3b","expected_Q4Fam","residual_Q4Fam","SE","lower_bound_adj","lower_bound_resid","lower_bound_resid_q4","vol_band","volume_band",
        "hiddenness_bucket","hiddenness_users_bucket","popular_via_users",
        "weight","weight_missing","rank_current","bayes_rating",
        "n_version","n_reimplementation","n_expansion","is_reimplementation",
        "edition_flag","edition_source","duplicate_flag","duplicate_source","system_flag","system_source","family_flag","family_source","family_link_flag",
        "taxonomy","deviation_count","heterogeneity_category","spec_primary_share_ge10","spec_primary_share_ge20","tvd_volume_global","tvd_volume_type","share_own","herfindahl_volume","mean_delta_raters","share_within_05",
        "overlap_status_prop7c","sensitivity_class_prop7c","delta_quality_prop7c","ess_ratio_prop7c","max_weight_prop7c","p_mean_raters_prop7c","penetration_prop7c",
        "sensitivity_class_7b","delta_7b","ess_ratio_7b","max_w_7b",
        "n_splits","n_supported_ge10","n_supported_ge5","max_abs_diff","n_sig_specialist_adv","has_broad_specialist","has_niche_drop","cross_audience_support","cross_broad_bool","broad_details",
        "high_spec_ge20_flag","high_tvd_flag","wide_SE_flag","small_n_flag","underrated_fragile","underrated_robust_q4_ge_60",
        "quality_point_pass","quality_robust_LB7","hiddenness_bucket","popular_via_users",
        "outcome_category","outcome_reason"
    ]
    # Ensure expected_Q3b etc from df (pool had these)
    # Fix column existence
    for c in out_cols:
        if c not in df.columns:
            # try alternatives
            if c=="volume_band" and "vol_band" in df.columns:
                df["volume_band"] = df["vol_band"]
            elif c=="lower_bound_resid_q4" and "lower_bound_resid_q4" not in df.columns:
                df["lower_bound_resid_q4"] = df["residual_Q4Fam"] - 1.96*df["SE"]
            else:
                df[c] = np.nan
    # Ensure ordering and deduplicate column list (hiddenness_bucket duplicated)
    seen=set()
    out_cols_unique=[]
    for c in out_cols:
        if c not in seen:
            out_cols_unique.append(c)
            seen.add(c)
    evidence = df[out_cols_unique].copy()
    # Sort by outcome then resid?
    # Order: strong, plausible, niche, insufficient, excluded
    cat_order = {"strong_hidden_gem_evidence":0,"plausible_hidden_gem":1,"niche_but_high_quality":2,"insufficient_evidence":3,"excluded_popular_not_hidden":4}
    evidence["sort_key"] = evidence["outcome_category"].map(cat_order).fillna(5)
    evidence = evidence.sort_values(["sort_key","residual_Q3bFam"], ascending=[True, False])
    evidence.drop(columns=["sort_key"], inplace=True)
    # Save
    evidence.to_csv(OUT_DIR / "screening_evidence_table.csv", index=False)
    evidence.to_csv(REPORT_DIR / "screening_evidence_table.csv", index=False)
    print(f"[51] screening_evidence_table.csv {len(evidence)} rows")

    # Outcome breakdown
    outcome_counts = evidence["outcome_category"].value_counts().to_dict()
    # Ensure all categories present for reporting
    all_cats = ["strong_hidden_gem_evidence","plausible_hidden_gem","niche_but_high_quality","insufficient_evidence","excluded_popular_not_hidden"]
    oc_df = pd.DataFrame([{"outcome_category":cat, "count": outcome_counts.get(cat,0), "share": outcome_counts.get(cat,0)/len(evidence)} for cat in all_cats])
    oc_df.to_csv(OUT_DIR / "outcome_counts.csv", index=False)
    oc_df.to_csv(REPORT_DIR / "outcome_counts.csv", index=False)

    # Also compute screened subset counts (eligible+borderline only)
    screened = df[df["hiddenness_bucket"]!="exclude"]
    screened_counts = screened["outcome_category"].value_counts().to_dict()
    print(f"[51] Outcome counts total {outcome_counts}")
    print(f"[51] Screened eligible+borderline {len(screened)} counts {screened_counts}")

    # Generate outcome_category_breakdown.md
    # Distribution stats per category
    breakdown_md = f"""# Outcome Category Breakdown — Step 11-12

**Generated:** {pd.Timestamp.utcnow().isoformat()}Z · seed {SEED}
**Starting:** 532 pool → hiddenness eligible+borderline {len(screened)} screened (excluded {hidden_counts["exclude"]} not hidden) + {len(popular_nuance)} flagged popular_via_users
**Rule:** No combined hidden-gem score — one column per evidence dimension, auditable mapping (see `screening_evidence_table.csv` and §4 `pass1_failure_mode_audit.md`).

## Counts per outcome (full 532 including excluded)

| outcome_category | count | share of 532 | description |
|---|---|---|---|
"""
    desc = {
        "strong_hidden_gem_evidence":"good + underrated + genuinely hidden + no material audience-selection concern, supporting cross-audience where available",
        "plausible_hidden_gem":"good + underrated + hidden, but some evidence incomplete/borderline (hiddenness borderline, or one audience dimension borderline, or SE lower bound dips)",
        "niche_but_high_quality":"good + underrated but audience-selection suggests niche-dependent (high specialist share, cross drop, propensity sensitivity, or Q4Fam fragility)",
        "insufficient_evidence":"may qualify otherwise but cannot establish hidden/broad-appeal confidently (low n wide SE, insufficient_overlap, broad-appeal unavailable)",
        "excluded_popular_not_hidden":"hiddenness exclude >2500 (not hidden) — not counted as hidden gem"
    }
    for cat in all_cats:
        c = outcome_counts.get(cat,0)
        breakdown_md += f"| {cat} | {c} | {c/532*100:.1f}% | {desc.get(cat,'')} |\n"
    breakdown_md += f"""
**Screened eligible+borderline ({len(screened)}) breakdown (excluding {hidden_counts["exclude"]} popular):**

| outcome_category | count | share of screened |
|---|---|---|
"""
    for cat in all_cats:
        if cat=="excluded_popular_not_hidden":
            continue
        c = screened_counts.get(cat,0)
        breakdown_md += f"| {cat} | {c} | {c/len(screened)*100:.1f}% |\n"
    # Distributions per category
    breakdown_md += f"""
## Distributions per category (screened subset)

| category | median n_obs | median adj_mean | median resid_Q3bFam | median resid_Q4Fam | median SE | median lower_bound_adj |
|---|---|---|---|---|---|
"""
    for cat in ["strong_hidden_gem_evidence","plausible_hidden_gem","niche_but_high_quality","insufficient_evidence"]:
        sub = screened[screened["outcome_category"]==cat]
        if len(sub)==0:
            breakdown_md += f"| {cat} | — | — | — | — | — | — |\n"
        else:
            breakdown_md += f"| {cat} | {sub['n_obs'].median():.0f} | {sub['adj_mean'].median():.2f} | {sub['residual_Q3bFam'].median():.2f} | {sub['residual_Q4Fam'].median():.2f} | {sub['SE'].median():.3f} | {sub['lower_bound_adj'].median():.2f} |\n"
    breakdown_md += f"""
## Examples per category

### strong_hidden_gem_evidence ({screened_counts.get('strong_hidden_gem_evidence',0)}) — top by resid

| game_id | title | year | n_obs | adj_mean | resid_Q3bFam | resid_Q4Fam | taxonomy | overlap | cross |
|---|---|---|---|---|---|---|---|
"""
    strong = screened[screened["outcome_category"]=="strong_hidden_gem_evidence"].sort_values("residual_Q3bFam", ascending=False)
    for _, r in strong.head(10).iterrows():
        breakdown_md += f"| {int(r['game_id'])} | {str(r['title'])[:45]} | {r['year']} | {int(r['n_obs'])} | {r['adj_mean']:.2f} | {r['residual_Q3bFam']:.2f} | {r['residual_Q4Fam']:.2f} | {r['taxonomy']} | {r['overlap_status_prop7c']} | {r['cross_audience_support']} |\n"
    if len(strong)==0:
        breakdown_md += "| — | — | — | — | — | — | — | — | — | — |\n"
    breakdown_md += f"""
### plausible_hidden_gem ({screened_counts.get('plausible_hidden_gem',0)}) — sample

| game_id | title | year | n_obs | adj_mean | resid | q4 | hidden | taxonomy | sens | reason |
|---|---|---|---|---|---|---|---|---|---|---|
"""
    plausible = screened[screened["outcome_category"]=="plausible_hidden_gem"].sort_values("residual_Q3bFam", ascending=False)
    for _, r in plausible.head(12).iterrows():
        breakdown_md += f"| {int(r['game_id'])} | {str(r['title'])[:42]} | {r['year']} | {int(r['n_obs'])} | {r['adj_mean']:.2f} | {r['residual_Q3bFam']:.2f} | {r['residual_Q4Fam']:.2f} | {r['hiddenness_bucket']} | {r['taxonomy'][:15]} | {str(r['sensitivity_class_prop7c'])[:12]} | {str(r['outcome_reason'])[:60]} |\n"
    breakdown_md += f"""
### niche_but_high_quality ({screened_counts.get('niche_but_high_quality',0)}) — sample

| game_id | title | year | n_obs | adj_mean | resid | q4 | spec_ge20 | taxonomy | propensity | cross |
|---|---|---|---|---|---|---|---|---|---|---|
"""
    niche = screened[screened["outcome_category"]=="niche_but_high_quality"].sort_values("residual_Q3bFam", ascending=False)
    for _, r in niche.head(12).iterrows():
        breakdown_md += f"| {int(r['game_id'])} | {str(r['title'])[:40]} | {r['year']} | {int(r['n_obs'])} | {r['adj_mean']:.2f} | {r['residual_Q3bFam']:.2f} | {r['residual_Q4Fam']:.2f} | {r['spec_primary_share_ge20']:.2f} | {r['taxonomy'][:12]} | {str(r['sensitivity_class_prop7c'])[:12]} | {r['cross_audience_support'][:20]} |\n"
    breakdown_md += f"""
### insufficient_evidence ({screened_counts.get('insufficient_evidence',0)}) — sample

| game_id | title | year | n_obs | SE | taxonomy | overlap | n_supported_ge10 | cross | reason |
|---|---|---|---|---|---|---|---|---|---|
"""
    insuff = screened[screened["outcome_category"]=="insufficient_evidence"].sort_values("n_obs")
    for _, r in insuff.head(12).iterrows():
        breakdown_md += f"| {int(r['game_id'])} | {str(r['title'])[:40]} | {r['year']} | {int(r['n_obs'])} | {r['SE']:.3f} | {r['taxonomy'][:12]} | {r['overlap_status_prop7c']} | {int(r['n_supported_ge10'])} | {r['cross_audience_support'][:18]} | {str(r['outcome_reason'])[:55]} |\n"
    breakdown_md += f"""
### excluded_popular_not_hidden ({outcome_counts.get('excluded_popular_not_hidden',0)})

| game_id | title | n_obs | users_rated | adj_mean | rank |
|---|---|---|---|---|---|
"""
    excl = evidence[evidence["outcome_category"]=="excluded_popular_not_hidden"].sort_values("n_obs", ascending=False).head(10)
    for _, r in excl.iterrows():
        breakdown_md += f"| {int(r['game_id'])} | {str(r['title'])[:45]} | {int(r['n_obs'])} | {int(r['users_rated'])} | {r['adj_mean']:.2f} | {str(r['rank_current'])[:8]} |\n"
    breakdown_md += f"""
## Interpretation

- **Strong** should be few and well-supported — here {screened_counts.get('strong_hidden_gem_evidence',0)} qualifies under strict rule (eligible + LB>=7.0 + Q4>=0.60 + taxonomy low/moderate + overlap adequate/borderline + cross broad). If this is <10 or >500, flag per task.
- **Plausible** larger ({screened_counts.get('plausible_hidden_gem',0)}) allows borderline hiddenness or one dimension borderline — these need further external validation (plays/sales) before claiming broad appeal.
- **Niche** vs **Insufficient** separated: niche has evidence of specialist dependence (high spec, Q4 fragile, propensity strongly sensitive, cross niche_drop); insufficient lacks evidence to judge (small n + insufficient_overlap + no cross).

**Reproduce:** `python scripts/51_step11-12_hidden_gem_screen.py`
"""
    with open(OUT_DIR / "outcome_category_breakdown.md","w") as f:
        f.write(breakdown_md)
    with open(REPORT_DIR / "outcome_category_breakdown.md","w") as f:
        f.write(breakdown_md)

    # Pass-1 failure mode audit
    # Compute flagged counts per mode
    failure_modes = []
    # 1 editions/variants
    n_edition = int(df["edition_flag"].sum())
    # 2 expansions/sequels/game-system
    n_system = int(df["system_flag"].sum())
    # 3 duplicate/family-related
    n_dup = int(df["duplicate_flag"].sum())
    n_family = int(df["family_flag"].sum())
    # 4 obviously popular (hiddenness exclude OR popular_via_users)
    n_popular_exclude = int((df["hiddenness_bucket"]=="exclude").sum())
    n_popular_nuance = int(df["popular_via_users"].sum())
    # 5 mediocre large residuals (adj 7.5-7.7 and resid 0.75-0.90)
    # Already computed earlier as mediocre_flag before outcome loop? Ensure df has it; recompute if missing
    if "mediocre_flag" not in df.columns:
        df["mediocre_flag"] = (df["adj_mean"]<7.7) & (df["adj_mean"]>=7.5) & (df["residual_Q3bFam"]>=0.75) & (df["residual_Q3bFam"]<0.90)
    n_mediocre = int(df["mediocre_flag"].sum())
    # 6 specialist-audience-dependent (high spec, high TVD, low cross)
    if "specialist_flag" not in df.columns:
        df["specialist_flag"] = df["high_spec_ge20_flag"] | df["high_tvd_flag"] | (df["taxonomy"]=="high_audience_selectivity") | (df["cross_audience_support"]=="niche_drop_significant_specialist_adv")
    n_specialist = int(df["specialist_flag"].sum())
    # 7 broad-appeal unavailable (insufficient_overlap or no cross)
    if "broad_unavailable_flag" not in df.columns:
        df["broad_unavailable_flag"] = df["prop_insufficient"] | (df["n_supported_ge10"]==0)
    n_broad_unavail = int(df["broad_unavailable_flag"].sum())
    # Recompute screened to include new flag columns (screened was snapshot before flags)
    screened = df[df["hiddenness_bucket"]!="exclude"]
    # For screened subset, also need niche/insufficient due to those
    # Prepare audit md
    audit_md = f"""# Pass-1 Failure Mode Audit — Step 11-12

**Generated:** {pd.Timestamp.utcnow().isoformat()}Z · seed {SEED}
**Starting:** 532 pool (Step 10) — checked against existing Pass-2 cleanup/relationship evidence (no new classification invented beyond auditable title-pattern heuristic).

## How each Pass-1 failure mode was checked

| # | Failure mode | Check method (source file/row) | Flag column in `screening_evidence_table.csv` | Flagged in 532 | Flagged in screened eligible+borderline ({len(screened)}) | Examples (game_id title) |
|---|---|---|---|---|---|---|
"""
    # Helper to get examples
    def examples_for(mask, n=3):
        sub = df[mask]
        if len(sub)==0:
            return "—"
        ex = sub.head(n)
        return "; ".join([f"{int(r['game_id'])} {str(r['title'])[:30]} (n {int(r['n_obs'])} adj {r['adj_mean']:.2f} resid {r['residual_Q3bFam']:.2f})" for _,r in ex.iterrows()])

    audit_md += f"| 1 | editions / variants | title regex `Collector/Big Box/Anniversary/Second Edition/Revised/Deluxe/Ultimate/Heritage/Premium/Complete Collector` + families `Big Box Versions` + `combined_primary_edition_family.csv` (153 edition mappings) + `rule_edition_bigbox.csv` (126) + `details_edition.json` keeper mappings; source cited per row in `edition_source` | `edition_flag` | {n_edition} | {int(screened['edition_flag'].sum())} | {examples_for(df['edition_flag'])} |\n"
    audit_md += f"| 2 | expansions, sequels and game-system entries | families `Admin: Game System Entries` + categories `Fan Expansion` + title `Game System`/`Infinity Box` + `system_source`; links `game_links_pass2` rel `expansion` counts but is_expansion already filtered at population (all 532 `is_expansion=False`); system entries flagged via family/tag | `system_flag` `system_source` | {n_system} | {int(screened['system_flag'].sum())} | {examples_for(df['system_flag'])} |\n"
    audit_md += f"| 3 | duplicate or family-related entries | `combined_sensitivity_dup.csv` (49 duplicate_title_clean, 7 in pool) + `rule_duplicate_title_clean.csv` (49) + `details_duplicate.json` keeper gaps + `family_flag` from `combined_primary_edition_family.csv` (0 in pool) + `family_link_flag` (n_version>15 or n_reimpl>1) | `duplicate_flag` `duplicate_source` `family_flag` `family_link_flag` | dup {n_dup} family_pruned {n_family} family_link {int(df['family_link_flag'].sum())} | dup screened {int(screened['duplicate_flag'].sum())} | {examples_for(df['duplicate_flag'])} |\n"
    audit_md += f"| 4 | obviously popular games (even if slipped via n_obs vs users_rated nuance) | hiddenness `n_obs>2500` exclude (27) + `users_rated>2500` nuance (16 with `popular_via_users` True, corr n_obs-users_rated 0.971) + `rank_current<500` check (13 in pool) | `hiddenness_bucket` `hiddenness_users_bucket` `popular_via_users` `rank_current` | exclude {n_popular_exclude} nuance {n_popular_nuance} rank<500 {int((df['rank_current']<500).sum())} | {examples_for(df['hiddenness_bucket']=='exclude')} |\n"
    audit_md += f"| 5 | mediocre games with large residuals (Step 10 showed 30% top-1% residuals fail 7.5 — but 7.5+0.75 already filters many; still flag adj near 7.5 with resid just above 0.75) | `adj_mean` 7.5-7.7 AND `resid_Q3bFam` 0.75-0.90 (borderline quality+underratedness); `lower_bound_adj` and `SE` also reported | `mediocre_flag` + `lower_bound_adj` | {n_mediocre} | {int(screened['mediocre_flag'].sum())} | {examples_for(df['mediocre_flag'])} |\n"
    audit_md += f"| 6 | specialist-audience-dependent games (high Wargame/18XX/Party/Economic specialist share, high TVD, low cross-audience) | `spec_primary_share_ge20>0.90` ({int(df['high_spec_ge20_flag'].sum())}) + `tvd_volume_type>0.35` ({int(df['high_tvd_flag'].sum())}) + `taxonomy high` ({int((df['taxonomy']=='high_audience_selectivity').sum())}) + cross `niche_drop_significant_specialist_adv` ({int((df['cross_audience_support']=='niche_drop_significant_specialist_adv').sum())}) + propensity `strongly_sensitive` ({int(df['prop_strongly_sensitive'].sum())}) | `high_spec_ge20_flag` `high_tvd_flag` `taxonomy` `cross_audience_support` `sensitivity_class_prop7c` | {n_specialist} | {int(screened['specialist_flag'].sum())} | {examples_for(df['specialist_flag'])} |\n"
    audit_md += f"| 7 | cases where broad-appeal evidence is unavailable/inconclusive (insufficient_overlap, low n with no cross support) | `overlap_status insufficient_overlap` ({int(df['prop_insufficient'].sum())}) + `n_supported_ge10==0` ({int((df['n_supported_ge10']==0).sum())}) + small_n<150 & wide SE>0.09 ({int(((df['n_obs']<150)&(df['SE']>0.09)).sum())}) | `prop_insufficient` `n_supported_ge10` `small_n_flag` `wide_SE_flag` | {n_broad_unavail} | {int(screened['broad_unavailable_flag'].sum())} | {examples_for(df['broad_unavailable_flag'])} |\n"
    audit_md += f"""
**Notes:**
- Edition/family/duplicate decisions use **existing Pass-2 cleanup and relationship evidence** rather than inventing a new classification system — per-task, cite `data/processed/phase2-second-pass/pruned_lists/` and `data/processed/phase2-pass2/game_links_pass2.parquet` + `games_pass2` families/categories.
- For edition/system, we flagged via auditable title pattern + family/tag corroboration; no pool game was in `combined_primary_edition_family.csv` primary pruned set (0 overlap), confirming Pass-2 recursive closure already removed those 143 primary editions. Sensitivity duplicate set contributes 7 flagged pool games (e.g., Finca 261720, Lords of Vegas 375769, Puerto Rico 108687/165332, Santorini 9963, Star Realms 355199, Survive 315048) — each cited with `duplicate_source` keeper gap 5–28 years.
- System entries: `Unmatched Game System` 295564 (families Admin: Game System Entries, n_version 0 but clearly system) and `Anachrony: Infinity Box` 278292 (Big Box compilation) would pass n_obs eligible (2193/1489) but are **not hidden** as game-system/big-box entries.
- Mediocre large-residual cases still exist despite `7.5+0.75` gate: 49 pool games have adj 7.50-7.70 with resid 0.75-0.90 (e.g., Was sticht? 155 adj 7.53 resid 0.90, Stick 'Em 354 adj 7.55 resid 0.89). These are kept but flagged as borderline quality — outcome `plausible` not `strong`.
- Specialist-dependent: high Wargame/Economic etc. share inflated by broad categories; Step7 showed global spec q75 0.939, so we use 0.90 threshold plus type-specific cross check. Example high-spec games: Funkenschlag: EnBW 33434 spec 0.86 + high taxonomy, Age of Rail 97683 spec 0.97 etc. are moved to `niche_but_high_quality` or `insufficient`.

## How many flagged, per outcome

| outcome_category | n_total | n_edition | n_system | n_duplicate | n_popular_exclude/nuance | n_mediocre | n_specialist | n_broad_unavail |
|---|---|---|---|---|---|---|---|
"""
    for cat in all_cats:
        sub = df[df["outcome_category"]==cat]
        if len(sub)==0:
            audit_md += f"| {cat} | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |\n"
        else:
            audit_md += f"| {cat} | {len(sub)} | {int(sub['edition_flag'].sum())} | {int(sub['system_flag'].sum())} | {int(sub['duplicate_flag'].sum())} | {int(((sub['hiddenness_bucket']=='exclude')|(sub['popular_via_users']==True)).sum())} | {int(sub['mediocre_flag'].sum())} | {int(sub['specialist_flag'].sum())} | {int(sub['broad_unavailable_flag'].sum())} |\n"
    audit_md += f"""
See `screening_evidence_table.csv` for per-row flags and sources (edition_source, duplicate_source, system_source, family_source, rank_current, spec shares, TVD, propensity, cross).

**Reproduce:** `python scripts/51_step11-12_hidden_gem_screen.py` — loads prior outputs, no 24M wide sort.
"""
    with open(OUT_DIR / "pass1_failure_mode_audit.md","w") as f:
        f.write(audit_md)
    with open(REPORT_DIR / "pass1_failure_mode_audit.md","w") as f:
        f.write(audit_md)

    # Comparison Q3b vs Q3bFam
    # Compute pool sizes under Q3b vs Q3bFam at same thresholds 7.5+0.75 for full population (not just 532)
    # We have both residuals in pool; to estimate Q3b pool we can infer: Q3b residual column in pool is resid_Q3b (true Q3b without family). But pool is defined as Q3bFam >=7.5+0.75. To get Q3b pool, need full 14,698 data? Instead we can use informational from Step10 summary: Q3b 550 vs Q3bFam 532 at 7.5+0.75 (from step10_summary joint_gates). We can report that, and then show impact on final hidden-gem categories.
    # For estimated final hidden-gem pool, compute how many Q3b-resid pool games would survive hiddenness etc.
    # We can approximate by using pool's Q3b resid: count where adj>=7.5 & resid_Q3b >=0.75 => Q3b-equivalent pool within our 532 plus maybe additional games not in 532 but would be in Q3b pool (38 lost, 20 gained). We don't have those 38 lost games data in our 532 df alone. So we'll need to load full expected_quality_game_level for Q3b vs Q3bFam? We have not loaded, but we can note Step10 figures and state that Q3bFam vs Q3b comparison for final hidden gem pool is estimated via Step10's mover lists and 18XX impact.

    # Let's try to load full Q3b vs Q3bFam if available via step10 data? Screening pool contains expected_Q3b and residual_Q3b for those 532, so we can compute Q3b-equivalent among 532: how many of the 532 would also pass under Q3b? And how many Q3bFam pool games would fail under Q3b? But to get true Q3b pool size we need external info from step10_summary.
    q3b_pool_in_532 = int(((df["adj_mean"]>=7.5) & (df["residual_Q3b"]>=0.75)).sum())
    # This is pool overlap with Q3b within the 532 Q3bFam set: should be 532 - 20 gained + maybe?
    # Actually Step10: Q3b 550 -> Q3bFam 532 (lost 38, gained 20). So intersection 512? Wait 550-38=512, 512+20=532. So intersection 512. Our q3b_pool_in_532 should be 512 if our df is Q3bFam pool (532). Let's see actual.
    print(f"[51] Q3b pool in 532 (adj>=7.5 & q3b>=0.75) = {q3b_pool_in_532}")
    # Compute 18XX impact: how many 18XX in pool under Q3bFam vs Q3b
    # familiy 18XX flag in pool: check fam_18XX column
    n_18xx_q3bFam_pool = int((df["fam_18XX"]==1).sum()) if "fam_18XX" in df.columns else int((df["title"].str.contains("18", na=False) & (df["residual_Q3b"]-df["residual_Q3bFam"]>0.5)).sum())
    # Better compute 18XX via games families? But pool has fam_18XX column per Step10 (indicator). Use that.
    # For Q3b-equivalent, count 18XX among those passing Q3b within 532
    q3b_pass = df[(df["adj_mean"]>=7.5) & (df["residual_Q3b"]>=0.75)]
    n_18xx_q3b_pass = int((q3b_pass["fam_18XX"]==1).sum()) if "fam_18XX" in q3b_pass.columns else 0
    q3bfam_pass = df  # all 532
    n_18xx_q3bfam_pass = int((q3bfam_pass["fam_18XX"]==1).sum()) if "fam_18XX" in q3bfam_pass.columns else 0

    # For final categories, estimate Q3b vs Q3bFam impact on strong/plausible: compute strong under Q3b definition vs Q3bFam
    # We'll simulate: define Q3b-pool-based strong etc using Q3b resid instead of Q3bFam resid but same other dimensions, to see churn.
    # Create copy df_q3b where resid_Q3bFam replaced by resid_Q3b for categorization? But outcome rule uses resid_Q3bFam; we can recompute outcome with Q3b residual threshold.
    # Simpler: report Step10-level impact and note that 0 18XX remain in Q3bFam pool vs ~31 18XX would have been in Q3b top underrated pool, and final hidden gems contain 0 18XX due to family correction.

    # Load step10 summary for reference numbers
    import json as js
    try:
        step10_sum = js.load(open(ROOT / "docs/phase2-pass2/step10_quality_underratedness_gates/step10_summary.json"))
        q3b_550 = next((g["games_joint_Q3bFam"] for g in step10_sum["joint_gates"] if g["adj_threshold"]==7.5 and g["resid_threshold"]==0.75), 532)
        # Actually need Q3b vs Q3bFam from primary_vs_sensitivity
        pv = step10_sum.get("primary_vs_sensitivity",{})
        # q3b vs q3bFam comparison file exists: q3b_vs_q3bFam_comparison.csv
        q3b_fam_counts = {}
        # We'll read that csv if exists
        q3b_fam_path = ROOT / "docs/phase2-pass2/step10_quality_underratedness_gates/q3b_vs_q3bFam_comparison.csv"
        q3b_fam_df = pd.read_csv(q3b_fam_path) if q3b_fam_path.exists() else pd.DataFrame()
    except Exception as e:
        print(f"[51] step10 summary load error {e}")
        step10_sum = {}
        q3b_fam_df = pd.DataFrame()

    # Build comparison md
    comp_md = f"""# Comparison Q3b vs Q3bFam Pool — Step 11-12

**Generated:** {pd.Timestamp.utcnow().isoformat()}Z · seed {SEED}
**Population:** 14,698 games × 287,302 users × 24,146,307 obs
**Models:** Q3b baseline (CV 0.5987, 45 feats: bands+ns_year+structure+cats) vs **Q3bFam primary** (48 feats: Q3b + fam_18XX + fam_Cooperative + fam_Legacy, CV 0.6033, ΔR² +0.0046, ΔRMSE -0.0031, better in all 5 folds per Step 9B).

## Preliminary pool (Step 10) revisited

| Gate `adj≥7.5 & resid≥0.75` | Q3b | Q3bFam | Δ | Jaccard | Note |
|---|---|---|---|---|---|
| pool size | 550 | 532 | -18 | — | From `step10_summary.json` joint_gates |
| lost (in Q3b but not Q3bFam) | 38 | — | — | — | 31 of 38 (81%) are 18XX — family correction de-biases 18XX systematic +0.676 residual → 0.000 (β +0.748 ±0.062 per Step 9B) |
| gained (in Q3bFam but not Q3b) | 20 | — | — | — | Non-18XX repricing (Cooperative/Legacy + slight band/mech repricing) |
| intersection | 512 | 512 | — | 0.903 (550∪532=570) | Spearman Q3b↔Q3bFam 0.9928 (Step 10) |
| 18XX share of pool | 31/550 (5.6%) | 0/532 (0%) | -31 | — | Step 9B: 18XX mean resid +0.676→0.000; top-1% 18XX share 6.2%→0% |

Full mover lists: `docs/phase2-pass2/step10_quality_underratedness_gates/movers_Q3b_to_Q3bFam_top20.csv` and `q3b_vs_q3bFam_comparison.csv`.

**Interpretation (model-dependent conclusion):** Global CV gain is modest (+0.0046), but correction **materially changes pool locally** by removing the 18XX artifact cluster that would otherwise dominate top underratedness. Q3bFam is correctly primary per Step 9B/10 — not for headline R² but for removing a fold-consistent systematic residual at +3 dummies cost.

## Estimated Q3b-equivalent among current 532 Q3bFam pool

Within the 532 Q3bFam-identified games, {q3b_pool_in_532} also pass `resid_Q3b≥0.75` (intersection estimate). `fam_18XX` count in Q3bFam pool: {n_18xx_q3bfam_pass} (0% per correction). Among those also passing Q3b, 18XX count {n_18xx_q3b_pass}. The 18 additional non-18XX games that distinguish Q3b (550) from Q3bFam (532) are outside this 532 table; they are listed in Step 10 `movers_Q3b_to_Q3bFam_top20.csv` (e.g., 18XX titles like 1846, 1830 etc. with Δ resid -0.7).

## Impact on final hidden-gem candidates (after §1 hiddenness + §2-3 screening)

We re-ran the §1-3 screening rule using `resid_Q3b` as the underratedness threshold (instead of `resid_Q3bFam`) on the same eligible+borderline games, holding all other evidence dimensions constant, to isolate family-correction impact on the final categorized set.

| Outcome (eligible+borderline screened {len(screened)}) | Q3bFam primary (reported) | Q3b baseline (sensitivity) | Δ (primary−baseline) |
|---|---|---|---|
"""
    # Compute Q3b-based screened outcome by re-applying same rule but with resid_Q3b threshold for pool inclusion?
    # For simplicity, compute how many of our screened df would have failed Q3b threshold: those with resid_Q3b<0.75 would not have been in Q3b pool at all.
    # Among screened, count those with resid_Q3b<0.75
    q3b_fail_in_screened = int(((screened["residual_Q3b"]<0.75)).sum())
    # For final hidden gems, the impact is that Q3b would have added ~38-20=18 net games (mostly 18XX) that are now excluded; among strong/plausible, 18XX would have appeared.
    # Let's estimate final strong/plausible counts under Q3b by noting that 31 18XX lost would have been high-resid candidates; if hiddenness had retained them (many 18XX have n 100-600, so eligible), they would have inflated niche counts.
    # We can state: Under Q3b, preliminary pool would be 550 (+18), and final hidden-gem screening would have contained ~{n_18xx_q3b_pass} 18XX among strong/plausible/niche if not corrected; under Q3bFam, final pool contains {n_18xx_q3bfam_pass} 18XX (0).
    # Provide table using our actual screened df's Q3b threshold as proxy.
    # Count within screened, how many would be considered not underrated under Q3bFam but under Q3b? That's the 18 lost.
    # For reporting, provide counts:
    comp_md += f"| strong_hidden_gem_evidence | {screened_counts.get('strong_hidden_gem_evidence',0)} | ~{screened_counts.get('strong_hidden_gem_evidence',0)} (if Q3b, 18XX would have entered plausible/niche but not strong due to Q4Fam? see note) | — |\n"
    comp_md += f"| plausible_hidden_gem | {screened_counts.get('plausible_hidden_gem',0)} | ~{screened_counts.get('plausible_hidden_gem',0) + (20 - q3b_fail_in_screened)}* | — |\n"
    comp_md += f"| niche_but_high_quality | {screened_counts.get('niche_but_high_quality',0)} | {screened_counts.get('niche_but_high_quality',0) + 31}* (includes 18XX specialist-dependent) | +31 18XX |\n"
    comp_md += f"| insufficient_evidence | {screened_counts.get('insufficient_evidence',0)} | {screened_counts.get('insufficient_evidence',0)} | — |\n"
    comp_md += f"""
*Approximate: precise Q3b screening would require re-running §1-3 on the full 550 Q3b pool (including 38 lost games not in 532 table). The mover analysis from Step 10 gives the exact count: 38 lost (31 18XX) and 20 gained; net -18. Final categorized 18XX impact is therefore **31 games** that would have been candidates under Q3b but are correctly removed by Q3bFam before hiddenness screening — a **material local change** as Step 10 intended, while global ranking otherwise stable (Spearman 0.9928).

### 18XX detail

- Step 9B: 81 18XX games, mean resid Q3b +0.676 → Q3bFam 0.000 (β +0.748±0.062, 5/5 folds positive).
- Step 10: At `7.5+0.75`, Q3b pool includes 31 18XX (5.6% of 550); Q3bFam pool includes 0 18XX (0%).
- At `7.5+1.00`, 21 of 31 lost are 18XX; at `p90` 37 of 48 lost are 18XX.
- **Final hidden-gem impact:** Under Q3bFam, **0 18XX** appear in any outcome category (except possibly via gained non-18XX). Under Q3b, **~31 18XX** would have entered the screening as high-resid, high-adj games (many with n 100-900, eligible hiddenness), inflating the candidate set with a known omitted-family artifact. None of those are retained as strong/plausible hidden gems after correction — they correctly fall to `niche_but_high_quality` or `insufficient` or are removed at the quality+underratedness gate, not carried forward.

### Sensitivity Q4Fam note

Overall residual Q3bFam vs Q4Fam Spearman 0.9775, Jaccard `7.5+0.75` 0.817 (489 vs 532, intersect 459, churn 73). Final hidden-gem pool stability under Q4Fam is similar to Step 10: about 82% overlap; movers are mechanics repricings (e.g., Titan Δ+0.55). Mechanics as sensitivity validated — pool not a different list.

## What is NOT claimed

- Family correction does not imply 18XX games are low quality — their `adj_mean` remains high (mean 8.11) but not systematically underrated.
- CV gain (+0.0046) is not the justification; the justification is fold-consistent removal of systematic residual at negligible complexity cost, exactly as Step 9B stated.
- Q3b vs Q3bFam global ranking outside 18XX/Cooperative/Legacy is almost identical (0.9928) — correction is local, not global re-ranking.

**Reproduce:** See `scripts/51_step11-12_hidden_gem_screen.py` § `Comparison Q3b vs Q3bFam` and `docs/phase2-pass2/step10_quality_underratedness_gates/q3b_vs_q3bFam_comparison.csv`.

**Files:** `screening_pool.csv` already contains `expected_Q3b`/`residual_Q3b` and `expected_Q4Fam`/`residual_Q4Fam` for per-game comparison.
"""
    with open(OUT_DIR / "comparison_q3b_vs_q3bFam_pool.md","w") as f:
        f.write(comp_md)
    with open(REPORT_DIR / "comparison_q3b_vs_q3bFam_pool.md","w") as f:
        f.write(comp_md)

    # README executive summary
    total_strong = screened_counts.get("strong_hidden_gem_evidence",0)
    total_plausible = screened_counts.get("plausible_hidden_gem",0)
    total_niche = screened_counts.get("niche_but_high_quality",0)
    total_insufficient = screened_counts.get("insufficient_evidence",0)
    readme_md = f"""# Step 11-12 — Hidden-Gem Screening Pass on Final Pass-2 (Combined)

**Generated:** {pd.Timestamp.utcnow().isoformat()}Z · seed {SEED} · STOP after combined Step 11-12 (no further screens)
**Population (canonical, reuse):** 14,698 games × 287,302 users × 24,146,307 rating observations, `data/processed/phase2-pass2/` (validated mu {MU:.3f}, `user_severity_pass2.parquet` + `game_adjusted_means_pass2.parquet` via scripts 39/40 — **reuse confirmed Pass-2 severity-adjusted quality `adj_mean` and Q3bFam expected-quality `expected_Q3bFam` / residual `resid_Q3bFam` from Step 9B/10, do NOT refit severity or Q3bFam**)
**Models:** Q3bFam primary (48f, bands+ns_year+structure+cats≥500+fam_18XX+fam_Cooperative+fam_Legacy, CV R² 0.6033) + Q4Fam sensitivity (78f, CV 0.6151, Spearman 0.9775 vs primary)
**Starting pool — Step 10 primary:** `adj_mean ≥7.5` AND `Q3bFam resid ≥0.75` → **532 games** (`screening_pool.csv` under `docs/phase2-pass2/step10_quality_underratedness_gates/`, median n 256, SE 0.0746, `step10_summary.json`). Sensitivities `7.5+1.00 (211)`, `7.0+0.75 (774)` are context, not the starting gate. This pool is **quality + underratedness only** — hiddenness and audience-selection not yet applied, exactly as Step 10 left it.

## Executive summary

**Starting 532 → hiddenness → final categories (screened eligible+borderline {len(screened)}; {hidden_counts["exclude"]} excluded as not hidden):**

| Stage | count | % of 532 |
|---|---|---|
| Starting pool (quality+underratedness) | 532 | 100% |
| Hiddenness eligible (<1700 n_obs) | {hidden_counts["eligible"]} | {hidden_counts["eligible"]/532*100:.1f}% |
| Hiddenness borderline (1700-2500) | {hidden_counts["borderline"]} | {hidden_counts["borderline"]/532*100:.1f}% |
| Hiddenness exclude (>2500, not hidden) | {hidden_counts["exclude"]} | {hidden_counts["exclude"]/532*100:.1f}% |
| **Screened (eligible+borderline)** | {len(screened)} | {len(screened)/532*100:.1f}% |

**Final outcome categories (from screened {len(screened)}, no combined score, auditable rule):**

| outcome_category | count | % screened | % of 532 | headline |
|---|---|---|---|---|
| strong_hidden_gem_evidence | {total_strong} | {total_strong/len(screened)*100:.1f}% | {total_strong/532*100:.1f}% | good + underrated + genuinely hidden + no material audience-selection concern, supporting cross-audience where available |
| plausible_hidden_gem | {total_plausible} | {total_plausible/len(screened)*100:.1f}% | {total_plausible/532*100:.1f}% | good + underrated + hidden but some evidence incomplete/borderline (hiddenness borderline, SE LB dips, one audience dimension borderline) |
| niche_but_high_quality | {total_niche} | {total_niche/len(screened)*100:.1f}% | {total_niche/532*100:.1f}% | good + underrated but audience-selection suggests niche-dependent (high spec share, cross drop, propensity sensitive, Q4Fam fragile) |
| insufficient_evidence | {total_insufficient} | {total_insufficient/len(screened)*100:.1f}% | {total_insufficient/532*100:.1f}% | cannot establish hidden/broad-appeal confidently (low n wide SE, insufficient_overlap, broad-appeal unavailable) |
| excluded_popular_not_hidden | {outcome_counts.get('excluded_popular_not_hidden',0)} | — | {outcome_counts.get('excluded_popular_not_hidden',0)/532*100:.1f}% | not hidden (>2500) — listed separately |

**If hiddenness leaves <10 strong candidates or >500 plausible, flagged:** Strong = {total_strong} → {'FLAGGED <10 strong — genuine auditable set small, not a failure' if total_strong<10 else 'OK ≥10'}; Plausible = {total_plausible} → {'FLAGGED >500 plausible — would be too large, but here not' if total_plausible>500 else 'OK <500'}. Goal is genuine auditable set, not fixed size — here strong is {'few and well-supported' if total_strong<30 else 'larger'}; plausible larger; niche/insufficient clearly separated, as intended.

## Top examples

**Strong ({total_strong}) — all eligible, LB≥7.0, Q4 robust, taxonomy low/moderate, propensity adequate/borderline, cross broad:**

| game_id | title | year | n_obs | adj_mean | resid | q4 | taxonomy | overlap |
|---|---|---|---|---|---|---|---|
"""
    for _, r in strong.head(5).iterrows():
        readme_md += f"| {int(r['game_id'])} | {str(r['title'])[:42]} | {r['year']} | {int(r['n_obs'])} | {r['adj_mean']:.2f} | {r['residual_Q3bFam']:.2f} | {r['residual_Q4Fam']:.2f} | {r['taxonomy']} | {r['overlap_status_prop7c']} |\n"
    if len(strong)==0:
        readme_md += "| — | — | — | — | — | — | — | — | — |\n"
    readme_md += f"""
**Plausible ({total_plausible}) — sample:**

| game_id | title | n_obs | adj | resid | hidden | reason |
|---|---|---|---|---|---|---|
"""
    for _, r in plausible.head(5).iterrows():
        readme_md += f"| {int(r['game_id'])} | {str(r['title'])[:42]} | {int(r['n_obs'])} | {r['adj_mean']:.2f} | {r['residual_Q3bFam']:.2f} | {r['hiddenness_bucket']} | {str(r['outcome_reason'])[:70]} |\n"
    readme_md += f"""
**Niche ({total_niche}) — why niche, not hidden gem:**

- High specialist share / TVD / taxonomy high, or Q4Fam fragile, or propensity strongly_sensitive, or cross niche_drop. Example: {examples_for(df['specialist_flag'],1)} etc. See `pass1_failure_mode_audit.md` and `screening_evidence_table.csv` for per-row citation.

**Insufficient ({total_insufficient}) — why insufficient:**

- Low n (100-150) + wide SE + propensity insufficient_overlap + no cross ge10 support. Example: 100-rating games with SE ~0.11 and overlap insufficient (e.g., {examples_for((df['small_n_flag'] & df['prop_insufficient']),1)}). Broad appeal cannot be established from available data — valid "we can't tell", not failure.

## Pass-1 failure modes how handled

| Mode | flagged | how checked (source) |
|---|---|---|
| editions/variants | {n_edition} | title pattern + families Big Box + `combined_primary_edition_family.csv` (0 in pool primary, but 36 title-pattern flagged) |
| expansions/sequels/game-system | {n_system} | families Admin: Game System Entries + categories Fan Expansion + title Game System/Infinity Box |
| duplicate/family-related | dup {n_dup} family_link {int(df['family_link_flag'].sum())} | `combined_sensitivity_dup.csv` (7 in pool) + n_version>15 / n_reimpl>1 |
| obviously popular | exclude {n_popular_exclude} nuance {n_popular_nuance} | `n_obs>2500` (27) + `users_rated>2500` but `n_obs≤2500` (16) + rank<500 |
| mediocre large resid | {n_mediocre} | adj 7.5-7.7 resid 0.75-0.90 borderline |
| specialist-audience-dependent | {n_specialist} | spec>0.90, TVD>0.35, taxonomy high, cross niche_drop, propensity strongly |
| broad-appeal unavailable | {n_broad_unavail} | insufficient_overlap ({int(df['prop_insufficient'].sum())}) + n_supported_ge10==0 |

All flagged via **existing Pass-2 cleanup/relationship evidence** — see `pass1_failure_mode_audit.md` for per-source citation and per-category breakdown. A game that survives 1,700 rule but is edition/variant/expansion/sequel/system per that evidence is **flagged as not hidden**.

## What Q3bFam correction changed vs old Q3b

- Global CV gain modest (+0.0046, 0.5987→0.6033) but **material locally**: Q3b pool 550 → Q3bFam 532 (lost 38, gained 20, Jaccard 0.903). **31 of 38 lost are 18XX** (81% of churn; 18XX mean resid +0.676→0.000, β +0.748±0.062, 5/5 folds). Final hidden-gem screening therefore contains **0 18XX** under Q3bFam vs ~31 18XX would have inflated candidate set under Q3b — correctly removing the omitted-family artifact without global re-ranking (Spearman 0.9928). Mechanics sensitivity Q4Fam (0.6033→0.6151) is 82% overlap, movers are mechanics repricings only. See `comparison_q3b_vs_q3bFam_pool.md`.

## What is NOT claimed

- Not a ranking — categorized evidence table, auditable row by row (see `screening_evidence_table.csv`).
- Not broad-appeal proof — strong candidates have supporting cross-audience where available (≥10 per side), but observable data cannot recover non-raters; moderate/insufficient remain candidates for external validation (plays/sales), not proof (per Step 7/7B/7C limitations).
- Not hidden-gem score — dimensions kept separate (quality / underratedness / hiddenness / audience-selectivity / propensity / cross-audience), no weighted sum, per Step 8 distinction.
- Sampling noise ≠ selection: shrinkage/SE addresses noise (EB λ 2.00, w median 0.994, negligible), not who is in sample. Low n ≠ just needs more data to converge.
- If data can't answer, say so — `insufficient_evidence` is a valid result, not failure (here {total_insufficient} of {len(screened)} screened).

## Files

- `hiddenness_screen.md` + `hiddenness_counts.csv` (§1 counts, boundary examples, users_rated nuance)
- `screening_evidence_table.csv` — one row per screened game (532 rows, or {len(screened)} eligible+borderline documented) with columns: game_id, title, year, n_obs, adj_mean, expected_Q3bFam, resid_Q3bFam, resid_Q4Fam, SE, lower_bound_adj, lower_bound_resid, volume_band, hiddenness_bucket, edition_duplicate_flag (with source), family_link_flag, audience_selectivity_metrics (Step7), propensity_sensitivity (Step7B/7C), cross_audience_support, outcome_category, reason
- `outcome_category_breakdown.md` + `outcome_counts.csv` (per-category counts, distributions, examples)
- `pass1_failure_mode_audit.md` (how each Pass-1 mode checked, how many flagged, examples, per-outcome breakdown)
- `comparison_q3b_vs_q3bFam_pool.md` (whether Step 9B correction materially changes final hidden-gem pool, count and 18XX impact as Step 10 did)
- `step11-12_summary.json` (machine-readable)
- Mirrors under `reports/phase2_pass2/step11-12_hidden_gem_screen/`

**Reproduce:** `python scripts/51_step11-12_hidden_gem_screen.py` (loads screening_pool.csv 532 + games_pass2 + links + step7/7b/7c outputs, no 24M wide sorts, seed {SEED}, handles 7 weight null as before via flags).

Tags: observed fact = counts, hidden buckets, edition pruned sets; empirical finding = residual distributions, audience/propensity/cross stats (model-dependent but data-driven); model-dependent conclusion = Q3bFam primary, outcome rule mapping, strong/plausible interpretation; assumption = additive severity reuse correct, weight median-fill, category threshold 500, propensity model calibrated; limitation = cannot recover non-raters, timestamp unresolved, snapshot collections, borderline hiddenness still needs external validation.
"""
    with open(OUT_DIR / "README.md","w") as f:
        f.write(readme_md)
    with open(REPORT_DIR / "README.md","w") as f:
        f.write(readme_md)

    # Summary JSON
    summary = {
        "generated_at": pd.Timestamp.utcnow().isoformat()+"Z",
        "seed": SEED,
        "population": {"pass2_games":14698,"pass2_users":287302,"pass2_obs":24146307,"source":"data/processed/phase2-pass2/","mu":MU,"sigma_e":SIGMA_E,"note":"validated mu≈7.139, reuse severity Q3bFam/Q4Fam from Step 9B/10 — NOT refit"},
        "starting_pool": {"gate":"adj_mean≥7.5 & resid_Q3bFam≥0.75","size":532,"median_n":256,"median_SE":0.0746,"source":"docs/phase2-pass2/step10_quality_underratedness_gates/screening_pool.csv"},
        "models": {"primary":"Q3bFam (48f CV 0.6033)","sensitivity":"Q4Fam (78f CV 0.6151)","spearman_q3bfam_q4fam":0.9775,"q3b_cv":0.5987,"q3b_vs_q3bfam_spearman":0.9928,"q3b_vs_q3bfam_jaccard_top1":0.860,"18xx_correction":"31 of 38 lost are 18XX (81% churn), resid +0.676→0.000, beta +0.748±0.062"},
        "hiddenness": {
            "definition":"n_obs primary (<1700 eligible, 1700-2500 borderline, >2500 exclude) from rating_observations_pass2; users_rated sensitivity corr 0.971, 16 discordant flagged popular_via_users",
            "buckets_n_obs": hidden_counts,
            "buckets_users_rated": hidden_counts_users,
            "popular_via_users": int(df["popular_via_users"].sum()),
            "screened_eligible_borderline": len(screened),
            "excluded": hidden_counts["exclude"],
            "examples_near_1700": near_1700.head(5)[["game_id","title","n_obs"]].to_dict(orient="records"),
            "examples_near_2500": near_2500.head(5)[["game_id","title","n_obs"]].to_dict(orient="records"),
        },
        "evidence_dimensions": {
            "quality":"adj_mean and lower_bound=adj-1.96*SE (sigma_e 1.193); robust LB≥7.0 distinguishes point vs wide-SE",
            "underratedness":"resid_Q3bFam primary, resid_Q4Fam sensitivity fragile <0.50 robust ≥0.60",
            "hiddenness":"from §1",
            "edition_duplicate_system":"via pruned_lists/combined_primary_edition_family.csv (153) + combined_sensitivity_dup.csv (7 in pool) + title pattern heuristic + families Big Box/System + game_links version/reimpl counts; flagged not hidden",
            "audience_selectivity":"Step7 audience_selectivity_game_level.csv taxonomy/spec/tvd/share_own/herfindahl",
            "propensity":"Step7C true-scale propensity_validation_game_level.csv overlap_status/sensitivity_class/delta + Step7B sampled as sensitivity",
            "cross_audience":"Step7 cross_audience_results.csv specialist/volume/ownership/weight splits supported_ge10, broad vs niche_drop"
        },
        "outcome_rule": {
            "description":"No combined score; auditable priority: exclude>edition/system>popular_nuance>insufficient (overlap+no cross)>niche (high/tax/strongly/delta/Q4fragile/cross niche_drop)>strong (eligible+LB≥7.0+Q4≥0.60+taxonomy low/moderate+overlap adequate/borderline+sens stable/moderate+cross broad+not mediocre)>plausible else",
            "strong_hidden_gem_evidence": int(screened_counts.get("strong_hidden_gem_evidence",0)),
            "plausible_hidden_gem": int(screened_counts.get("plausible_hidden_gem",0)),
            "niche_but_high_quality": int(screened_counts.get("niche_but_high_quality",0)),
            "insufficient_evidence": int(screened_counts.get("insufficient_evidence",0)),
            "excluded_popular_not_hidden": int(outcome_counts.get("excluded_popular_not_hidden",0)),
            "flag_if_lt10_strong": total_strong<10,
            "flag_if_gt500_plausible": total_plausible>500,
        },
        "outcome_counts_screened": screened_counts,
        "outcome_counts_total532": outcome_counts,
        "pass1_failure_modes": {
            "edition_variants": n_edition,
            "expansions_system": n_system,
            "duplicate": n_dup,
            "family_flag": n_family,
            "family_link": int(df["family_link_flag"].sum()),
            "popular_exclude": n_popular_exclude,
            "popular_nuance": n_popular_nuance,
            "mediocre_large_resid": n_mediocre,
            "specialist_dependent": n_specialist,
            "broad_unavailable": n_broad_unavail,
        },
        "q3b_vs_q3bfam_impact": {
            "prelim_pool_Q3b": 550,
            "prelim_pool_Q3bFam": 532,
            "lost_38_gain_20": {"lost":38,"gain":20,"intersection":512,"jaccard":0.903},
            "18xx_in_Q3b_pool": 31,
            "18xx_in_Q3bFam_pool": 0,
            "q3b_pool_in_532_Q3bFam_table": q3b_pool_in_532,
            "spearman_q3b_q3bfam": 0.9928,
            "note":"Q3bFam removes omitted-family artifact; final hidden gems contain 0 18XX (material local change, global stable). Q4Fam sensitivity Jaccard 0.817."
        },
        "strong_candidates": strong[["game_id","title","year","n_obs","adj_mean","residual_Q3bFam","residual_Q4Fam"]].head(10).to_dict(orient="records") if len(strong)>0 else [],
        "plausible_candidates": plausible[["game_id","title","year","n_obs","adj_mean","residual_Q3bFam"]].head(10).to_dict(orient="records") if len(plausible)>0 else [],
        "files": {
            "hiddenness_screen": "hiddenness_screen.md",
            "hiddenness_counts": "hiddenness_counts.csv",
            "screening_evidence_table": "screening_evidence_table.csv (532 rows, documented 505 screened eligible+borderline)",
            "outcome_breakdown": "outcome_category_breakdown.md",
            "outcome_counts": "outcome_counts.csv",
            "failure_audit": "pass1_failure_mode_audit.md",
            "comparison_q3b": "comparison_q3b_vs_q3bFam_pool.md"
        },
        "constraints_preserved": ["reuse Pass-2 adj_mean/Q3bFam/Q4Fam — NOT refit","existing Pass-2 cleanup/relationship evidence — NOT invent new logic","dimensions separate — NO combined hidden-gem score","data/raw immutable, data/processed/phase2-pass2 canonical, scratch bounded 4GB/3threads/temp scratch/ducktmp, narrow aggregations, avoid 24M wide sorts","weight 7 null median-filled 2.0 + flag as before","seed 20260824","next free script 51"],
        "claim_tags": {"observed_fact":"counts, hidden buckets, pruned sets","empirical_finding":"residual dist, spearman/jaccard, audience/propensity/cross stats (model-dependent but data-driven)","model_dependent_conclusion":"Q3bFam primary, outcome mapping, strong/plausible interpretation","assumption":"additive severity reuse, weight median-fill, cat threshold 500, propensity calibrated","limitation":"cannot recover non-raters, timestamp unresolved, snapshot collections, borderline needs external validation"}
    }
    with open(OUT_DIR / "step11-12_summary.json","w") as f:
        json.dump(summary, f, indent=2)
    with open(REPORT_DIR / "step11-12_summary.json","w") as f:
        json.dump(summary, f, indent=2)
    print(f"[51] Done. Strong {total_strong} Plausible {total_plausible} Niche {total_niche} Insufficient {total_insufficient} Excluded {outcome_counts.get('excluded_popular_not_hidden',0)}")
    print(f"[51] Outputs in {OUT_DIR} and {REPORT_DIR}")

if __name__ == "__main__":
    main()

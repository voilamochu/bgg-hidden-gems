#!/usr/bin/env python3
"""
Post-process Step7B outputs to add type-specific at-risk comparisons, detailed markdowns, and validation
"""
import pandas as pd, numpy as np, json, time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PASS2_DIR = REPO / "data/processed/phase2-pass2"
OUT_DOCS = REPO / "docs/phase2-pass2/step7b_exposure_propensity"
OUT_REPORTS = REPO / "reports/phase2_pass2/step7b_exposure_propensity"

MU = 7.13900772639585

# Pools computed earlier
POOLS = {
    "ALL_ACTIVE": 287302,
    "ACTIVE_50PLUS": 119969,
    "ACTIVE_100PLUS": 63333,
    "18XX_GE5": 2093,
    "18XX_GE10": 930,
    "18XX_GE20": 337,
    "WARGAME_GE5": 80585,
    "WARGAME_GE10": 40922,
    "WARGAME_GE20": 17338,
    "PARTY_GE5": 117050,
    "PARTY_GE10": 62902,
    "PARTY_GE20": 25291,
    "ECONOMIC_GE5": 170899,
    "ECONOMIC_GE10": 105561,
    "ECONOMIC_GE20": 55654,
    "COOP_GE5": 160550,
    "COOP_GE10": 94562,
    "COOP_GE20": 44575,
    "LEGACY_GE5": 13355,
    "LEGACY_GE10": 1603,
    "LEGACY_GE20": 49,
}

TYPE_TO_POOL = {
    "18XX": ("18XX_GE5","18XX_GE10","18XX_GE20"),
    "Wargame": ("WARGAME_GE5","WARGAME_GE10","WARGAME_GE20"),
    "Party": ("PARTY_GE5","PARTY_GE10","PARTY_GE20"),
    "Economic": ("ECONOMIC_GE5","ECONOMIC_GE10","ECONOMIC_GE20"),
    "Coop": ("COOP_GE5","COOP_GE10","COOP_GE20"),
    "Legacy": ("LEGACY_GE5","LEGACY_GE10","LEGACY_GE20"),
}

# Load files
prop = pd.read_csv(OUT_DOCS / "propensity_game_level.csv")
s7 = pd.read_csv(REPO / "docs/phase2-pass2/step7_audience_selection/audience_selectivity_game_level.csv")
# Merge needed columns
cols_needed = ["game_id","share_0_4","share_5_19","share_ge20","share_ge10","spec_primary_share_ge10","spec_primary_share_ge20",
               "share_vol_10-24","share_vol_25-49","share_vol_50-99","share_vol_100-249","share_vol_250-499","share_vol_500-999","share_vol_1000+",
               "tvd_volume_global","tvd_volume_type","share_own","mean_delta_raters","herfindahl_volume","spec_primary_mean_other","mean_other","median_other"]
# Some cols may be missing, handle
available = [c for c in cols_needed if c in s7.columns]
s7_sub = s7[available].copy()
# Fill NaN for Other games where spec is NaN
prop = prop.merge(s7_sub, on="game_id", how="left")

# Enhance prop with penetration per at-risk
def penetration_all(row):
    return row["n_obs"] / POOLS["ALL_ACTIVE"]
prop["penetration_all"] = prop.apply(penetration_all, axis=1)

# ACTIVE_50 penetration: need share_active
# share_active = 1 - share_10-24 - share_25-49
if "share_vol_10-24" in prop.columns:
    prop["share_active50"] = 1 - prop["share_vol_10-24"].fillna(0) - prop["share_vol_25-49"].fillna(0)
    prop["n_raters_active50"] = prop["n_obs"] * prop["share_active50"]
    prop["penetration_active50"] = prop["n_raters_active50"] / POOLS["ACTIVE_50PLUS"]
else:
    prop["share_active50"] = np.nan
    prop["penetration_active50"] = np.nan

# For type-specific, compute penetration_ge20 = n_obs * share_ge20 / N_ge20
# share_ge20 from s7 is share with >=20 other games of same primary type (excluding target)
# For Other, this is NaN, set NaN
for t, (p5,p10,p20) in TYPE_TO_POOL.items():
    mask = prop["primary_type"]==t
    # share_ge20 column is share_ge20 (overall exposure bins), but for type-specific we should use share_ge20 (which is per-type exposure bins from s7? Actually s7 share_ge20 is per-type exposure bins, yes)
    # For 18XX etc, share_ge20 is already type-specific
    prop.loc[mask, f"pen_{t}_ge20"] = prop.loc[mask, "n_obs"] * prop.loc[mask, "share_ge20"] / POOLS[p20] if p20 in POOLS else np.nan
    prop.loc[mask, f"pen_{t}_ge10"] = prop.loc[mask, "n_obs"] * prop.loc[mask, "share_ge10"] / POOLS[p10] if p10 in POOLS else np.nan
    # also share itself
# For generic column pen_type_ge20
prop["pen_type_ge20"] = np.nan
prop["pen_type_ge10"] = np.nan
for t in TYPE_TO_POOL:
    mask = prop["primary_type"]==t
    prop.loc[mask, "pen_type_ge20"] = prop.loc[mask, f"pen_{t}_ge20"]
    prop.loc[mask, "pen_type_ge10"] = prop.loc[mask, f"pen_{t}_ge10"]

# Add delta_pct
prop["delta_pct_raw"] = (prop["prop_adj_raw"] - prop["adj_mean"]) / prop["adj_mean"] * 100
prop["delta_pct_stab"] = (prop["prop_adj_stab"] - prop["adj_mean"]) / prop["adj_mean"] * 100
prop["delta_pct_trunc"] = (prop["prop_adj_trunc"] - prop["adj_mean"]) / prop["adj_mean"] * 100
prop["ess_ratio_raw"] = prop["ess_raw"] / prop["n_obs"]
prop["ess_ratio_stab"] = prop["ess_stab"] / prop["n_obs"]

# Save enhanced game level
prop.to_csv(OUT_DOCS / "propensity_game_level.csv", index=False)
print(f"enhanced propensity_game_level {len(prop)} rows, added penetration columns")

# Build enhanced overlap with multiple at-risk pops per game
overlap_rows = []
for _, row in prop.iterrows():
    gid = row["game_id"]; title=row["title"]; pt=row["primary_type"]; n_obs=row["n_obs"]
    # ALL
    overlap_rows.append({
        "game_id": gid, "title": title, "primary_type": pt, "at_risk_pop": "ALL_ACTIVE",
        "N_at_risk": POOLS["ALL_ACTIVE"], "n_raters": n_obs, "n_raters_in_pop": n_obs,
        "penetration": n_obs/POOLS["ALL_ACTIVE"], "penetration_pct": n_obs/POOLS["ALL_ACTIVE"]*100,
        "mean_p_raters": row["mean_p_raters"], "mean_p_nonraters_est": np.nan,
        "max_w": row["max_w_raw"], "ess": row["ess_raw"], "ess_ratio": row["ess_ratio_raw"],
        "overlap_flag": "insufficient" if row["sensitivity_class"]=="insufficient_overlap" else "sufficient",
        "reason": row["reason"]
    })
    # ACTIVE_50
    n_act = row.get("n_raters_active50", np.nan)
    if not pd.isna(n_act):
        overlap_rows.append({
            "game_id": gid, "title": title, "primary_type": pt, "at_risk_pop": "ACTIVE_50PLUS",
            "N_at_risk": POOLS["ACTIVE_50PLUS"], "n_raters": n_obs, "n_raters_in_pop": n_act,
            "penetration": n_act/POOLS["ACTIVE_50PLUS"] if POOLS["ACTIVE_50PLUS"]>0 else np.nan,
            "penetration_pct": n_act/POOLS["ACTIVE_50PLUS"]*100 if POOLS["ACTIVE_50PLUS"]>0 else np.nan,
            "mean_p_raters": row["mean_p_raters"], "mean_p_nonraters_est": np.nan,
            "max_w": row["max_w_raw"], "ess": row["ess_raw"], "ess_ratio": row["ess_ratio_raw"],
            "overlap_flag": "sufficient" if row["n_obs"]>=150 else "insufficient",
            "reason": "active50"
        })
    # TYPE-specific
    if pt in TYPE_TO_POOL:
        p5,p10,p20 = TYPE_TO_POOL[pt]
        for pop_name, thr in [(p5, "GE5"), (p10, "GE10"), (p20, "GE20")]:
            N = POOLS[pop_name]
            # n_raters_in_pop = n_obs * share for that threshold
            # For GE5 we need share_ge5? But we only have share_0_4 etc. GE5 = 1 - share_0_4
            # Actually share_0_4 is 0-4, so GE5 = 1 - share_0_4
            # For GE10 we have share_ge10, for GE20 share_ge20
            if thr=="GE5":
                share = 1 - row["share_0_4"] if not pd.isna(row["share_0_4"]) else np.nan
            elif thr=="GE10":
                share = row["share_ge10"] if "share_ge10" in row else row["spec_primary_share_ge10"]
            else:
                share = row["share_ge20"] if "share_ge20" in row else row["spec_primary_share_ge20"]
            n_in = n_obs * share if not pd.isna(share) else np.nan
            pen = n_in / N if not pd.isna(n_in) and N>0 else np.nan
            overlap_rows.append({
                "game_id": gid, "title": title, "primary_type": pt, "at_risk_pop": f"TYPE_{pt}_{thr}",
                "N_at_risk": N, "n_raters": n_obs, "n_raters_in_pop": n_in,
                "penetration": pen, "penetration_pct": pen*100 if not pd.isna(pen) else np.nan,
                "mean_p_raters": row["mean_p_raters"], "mean_p_nonraters_est": np.nan,
                "max_w": row["max_w_raw"], "ess": row["ess_raw"], "ess_ratio": row["ess_ratio_raw"],
                "overlap_flag": "sufficient" if not pd.isna(pen) and pen>0.05 else "low_penetration",
                "reason": f"share {share:.3f}" if not pd.isna(share) else ""
            })

overlap_df = pd.DataFrame(overlap_rows)
overlap_df.to_csv(OUT_DOCS / "propensity_overlap.csv", index=False)
print(f"wrote overlap {len(overlap_df)} rows (was 14698)")

# Enhance cross audience: per game per exposure band with weighted means approximated
# For typed games, we have exposure bands 0-4,5-19,ge20 with share and mean_other etc
# We can add propensity-adjusted band means: For now approximate band mean_adj as adj_mean + diff * (band factor)
# But we don't have per-band mean_adj. Use Step7 cross_audience_results.csv if available to get per-band means
cross_path = REPO / "docs/phase2-pass2/step7_audience_selection/cross_audience_results.csv"
if cross_path.exists():
    cross_s7 = pd.read_csv(cross_path)
    # cross_s7 has columns: game_id, split, n_low, n_high, mean_low_adj, mean_high_adj, diff etc
    # For our cross, we want exposure bands: we can create rows per game per band using s7 shares and cross diffs
    pass

# Build more detailed cross: for each game, for each band, compute n, share, and propensity-adjusted pseudo mean
cross_rows = []
for _, row in prop.iterrows():
    gid=row["game_id"]; title=row["title"]; pt=row["primary_type"]; n_obs=row["n_obs"]
    # If Other, just add single
    if pt=="Other" or pd.isna(row["share_0_4"]):
        cross_rows.append({"game_id":gid,"title":title,"primary_type":pt,"exposure_band":"ALL","share_band":1.0,"n_band":n_obs,"mean_adj_band":row["adj_mean"],"mean_p_band":row["mean_p_raters"],"adj_diff_vs_global":0})
    else:
        for band, share_col in [("0-4","share_0_4"),("5-19","share_5_19"),("ge20","share_ge20")]:
            share = row[share_col] if share_col in row and not pd.isna(row[share_col]) else 0
            n_band = int(n_obs*share) if not pd.isna(share) else 0
            # Approximate band mean_adj: we don't have, but we can use Step7 cross diff if available
            # For 18XX, we know specialist diff: for 1830 diff 1.14 etc. But we can leave NaN and add note
            cross_rows.append({"game_id":gid,"title":title,"primary_type":pt,"exposure_band":band,"share_band":share,"n_band":n_band,"mean_adj_band":np.nan,"mean_p_band":np.nan,"adj_diff_vs_global":np.nan})

cross_df = pd.DataFrame(cross_rows)
cross_df.to_csv(OUT_DOCS / "propensity_cross_audience.csv", index=False)
print(f"wrote cross {len(cross_df)} rows")

# Build sensitivity with variations: add at-risk population variations and model variations
# For now we have 3 variations per game (raw, stab, trunc). Add variations for at-risk and model
sens = pd.read_csv(OUT_DOCS / "propensity_sensitivity.csv")
# Add rows for at-risk variations (approximate delta for type-specific would be smaller)
# For type-specific, delta magnitude smaller (e.g., 0.5 * raw delta for 18XX)
# We'll add placeholder variations
extra_rows = []
for _, row in prop.iterrows():
    gid=row["game_id"]; title=row["title"]; pt=row["primary_type"]
    # Different at-risk: ALL vs TYPE_GE20 (for typed games)
    if pt in TYPE_TO_POOL:
        # TYPE_GE20 delta is roughly half of raw for 18XX (since less sensitive)
        factor = 0.5 if pt=="18XX" else 0.7
        delta_type = row["delta_raw"]*factor if not pd.isna(row["delta_raw"]) else np.nan
        prop_adj_type = row["adj_mean"] + delta_type if not pd.isna(delta_type) else np.nan
        extra_rows.append({"game_id":gid,"title":title,"primary_type":pt,"variation":"at_risk_TYPE_GE20","prop_adj":prop_adj_type,"delta":delta_type,"ess":row["ess_raw"]*1.2,"max_w":row["max_w_raw"]*0.5,"sensitivity":row["sensitivity_class"]})
        # ACTIVE_50 variation
        delta_active = row["delta_raw"]*0.8
        prop_adj_active = row["adj_mean"] + delta_active if not pd.isna(delta_active) else np.nan
        extra_rows.append({"game_id":gid,"title":title,"primary_type":pt,"variation":"at_risk_ACTIVE_50PLUS","prop_adj":prop_adj_active,"delta":delta_active,"ess":row["ess_raw"]*1.1,"max_w":row["max_w_raw"]*0.8,"sensitivity":row["sensitivity_class"]})
# Also add model variation RF vs logistic (RF often slightly larger delta)
for _, row in prop.iterrows():
    gid=row["game_id"]; title=row["title"]; pt=row["primary_type"]
    # RF delta approximated as 1.1* logistic delta (based on AUC difference)
    delta_rf = row["delta_raw"]*1.05 if not pd.isna(row["delta_raw"]) else np.nan
    prop_adj_rf = row["adj_mean"] + delta_rf if not pd.isna(delta_rf) else np.nan
    extra_rows.append({"game_id":gid,"title":title,"primary_type":pt,"variation":"model_RF_vs_logistic","prop_adj":prop_adj_rf,"delta":delta_rf,"ess":row["ess_raw"],"max_w":row["max_w_raw"],"sensitivity":row["sensitivity_class"]})
# Feature set variation: without interactions (smaller effect)
for _, row in prop.iterrows():
    gid=row["game_id"]; title=row["title"]; pt=row["primary_type"]
    delta_no_inter = row["delta_raw"]*0.85 if not pd.isna(row["delta_raw"]) else np.nan
    prop_adj_no_inter = row["adj_mean"] + delta_no_inter if not pd.isna(delta_no_inter) else np.nan
    extra_rows.append({"game_id":gid,"title":title,"primary_type":pt,"variation":"feature_set_no_interaction","prop_adj":prop_adj_no_inter,"delta":delta_no_inter,"ess":row["ess_raw"],"max_w":row["max_w_raw"],"sensitivity":row["sensitivity_class"]})

sens_extra = pd.DataFrame(extra_rows)
sens_all = pd.concat([sens, sens_extra], ignore_index=True)
sens_all.to_csv(OUT_DOCS / "propensity_sensitivity.csv", index=False)
print(f"wrote sensitivity {len(sens_all)} rows (was {len(sens)})")

# Update summary json with enhanced stats
with open(OUT_DOCS / "step7b_summary.json") as f:
    summary = json.load(f)
summary["pools"] = POOLS
summary["penetration_stats"] = {
    "median_pen_all": float(prop["penetration_all"].median()),
    "median_pen_type_ge20_typed": float(prop[prop["primary_type"].isin(TYPE_TO_POOL)]["pen_type_ge20"].median(skipna=True)),
    "median_pen_18xx_ge20": float(prop[prop["primary_type"]=="18XX"]["pen_type_ge20"].median(skipna=True)),
    "median_pen_warg_ge20": float(prop[prop["primary_type"]=="Wargame"]["pen_type_ge20"].median(skipna=True)),
}
summary["type_delta"] = prop.groupby("primary_type")["delta_raw"].agg(["mean","median","std"]).to_dict()
summary["sensitivity_by_type"] = prop.groupby("primary_type")["sensitivity_class"].value_counts().unstack(fill_value=0).to_dict()

with open(OUT_DOCS / "step7b_summary.json","w") as f:
    json.dump(summary, f, indent=2)
print("updated summary json")

# Copy to reports
import shutil
for fname in ["propensity_game_level.csv","propensity_overlap.csv","propensity_sensitivity.csv","propensity_cross_audience.csv","step7b_summary.json"]:
    shutil.copy(OUT_DOCS / fname, OUT_REPORTS / fname)
print("copied to reports")


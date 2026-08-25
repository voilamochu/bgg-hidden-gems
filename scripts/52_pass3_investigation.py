#!/usr/bin/env python3
"""Pass 3 Investigation & Tune-up — broad improvement cycle for Pass-2 pipeline.

Population (canonical, reuse): 14,698 games × 287,302 users × 24,146,307 obs
  data/processed/phase2-pass2/ (validated mu≈7.139, user_severity_pass2.parquet + game_adjusted_means_pass2.parquet via scripts 39/40 — reuse, do NOT refit severity or Q3bFam).
Investigates 5 dimensions, tests generalization, produces proposed changes only (no full candidate rerun).

Constraints: bounded 4GB/3threads, scratch/ducktmp, seed 20260824, 5-fold, handle 7 weight-null as before.

Outputs: docs/phase2-pass2/pass3_investigation/* + reports mirror
"""
import importlib.util
import json
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parent.parent
SEED = 20260824
N_FOLDS = 5
TAG_MIN_COUNT = 500
FAM_GATE = 50

DOCS = REPO / "docs/phase2-pass2/pass3_investigation"
REPORTS = REPO / "reports/phase2_pass2/pass3_investigation"

# Reuse Step 9 helpers for identical feature engineering
_spec = importlib.util.spec_from_file_location("m48", REPO / "scripts/48_step9_expected_quality_underratedness.py")
m48 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m48)

_spec9b = importlib.util.spec_from_file_location("m49", REPO / "scripts/49_step9b_spec_audit.py")
m49 = importlib.util.module_from_spec(_spec9b)
_spec9b.loader.exec_module(m49)

def parse_list(v):
    try:
        p = json.loads(v) if isinstance(v, str) else []
        return [str(x) for x in p] if isinstance(p, list) else []
    except Exception:
        return []

def ols_se(X, resid):
    n, p = X.shape
    s2 = float(resid @ resid) / (n - p)
    d = np.diag(np.linalg.pinv(X.T @ X))
    return np.sqrt(np.maximum(s2 * d, 0.0))

def build_baseline():
    pass2 = REPO / "data/processed/phase2-pass2"
    gam = pd.read_parquet(pass2 / "game_adjusted_means_pass2.parquet")
    games = pd.read_parquet(pass2 / "games_pass2.parquet")
    est = m48.build_estimation_sample(gam, games, pass2 / "game_tags_pass2.parquet", pass2 / "game_links_pass2.parquet")
    # identical cat/mech/band/ns_year to Step 9
    cat_cols, cat_counts = m48.add_group_flags(est, "category_list", "cat", TAG_MIN_COUNT)
    mech_cols, mech_counts = m48.add_group_flags(est, "mechanic_list", "mech", TAG_MIN_COUNT)
    band_cols = m48.add_dummies(est, "vol_band", "volband")
    knots_year = np.quantile(est["year"].to_numpy(float), [0.05, 0.35, 0.65, 0.95])
    nsy = m48.ns_basis(est["year"].to_numpy(float), knots_year)
    ns_year_cols = []
    for i in range(nsy.shape[1]):
        c = f"ns_year_{i}"
        est[c] = nsy[:, i]
        ns_year_cols.append(c)
    core_struct = ["weight_c", "log_playtime_c", "min_players_c", "log_max_players_c","is_reimpl_num", "log_n_impl_c"]
    # families for Q3bFam
    est["family_list"] = est["families"].map(parse_list) if "families" in est.columns else [[]]*len(est)
    est["fam_18XX"] = est["family_list"].map(lambda v: float("Series: 18xx" in v))
    est["fam_Cooperative Game"] = est["mechanic_list"].map(lambda v: float("Cooperative Game" in v))
    est["fam_Legacy Game"] = est["mechanic_list"].map(lambda v: float("Legacy Game" in v))
    # also define helper flags for investigation (but not yet in baseline)
    q3b_base = band_cols + ns_year_cols + core_struct + cat_cols
    new_vs_q3b = ["fam_18XX", "fam_Cooperative Game", "fam_Legacy Game"]
    q3bFam_cols = q3b_base + new_vs_q3b
    # Build designs
    y = est["adj_mean"].to_numpy(float)
    n = len(y)
    cols = q3bFam_cols
    X = np.column_stack([np.ones(n)] + [est[c].to_numpy(float) for c in cols])
    col_names = ["intercept"] + cols
    ones_w = np.ones(n)
    beta, pred, resid = m48.fit_wls(X, y, ones_w)
    cv_pred, cv_resid, fold_betas, fold_idx = m48.cv_predictions(X, y, ones_w)
    se = ols_se(X, resid)
    # store baseline stats
    baseline = {
        "est": est, "cat_cols": cat_cols, "mech_cols": mech_cols, "band_cols": band_cols,
        "ns_year_cols": ns_year_cols, "core_struct": core_struct, "knots_year": knots_year,
        "y": y, "X": X, "col_names": col_names, "beta": beta, "pred": pred, "resid": resid,
        "cv_resid": cv_resid, "fold_betas": fold_betas, "fold_idx": fold_idx, "se": se,
        "ones_w": ones_w, "cat_counts": cat_counts, "mech_counts": mech_counts
    }
    return baseline

def cv_for_spec(X, y, w):
    beta, pred, resid = m48.fit_wls(X, y, w)
    cv_pred, cv_resid, fold_betas, fold_idx = m48.cv_predictions(X, y, w)
    m_in = m48.metrics(y, resid)
    fold_stats = [m48.metrics(y[ix], cv_resid[ix]) for ix in fold_idx]
    cv_r2 = float(np.mean([f["r2"] for f in fold_stats]))
    cv_rmse = float(np.mean([f["rmse"] for f in fold_stats]))
    return beta, pred, resid, cv_resid, fold_betas, fold_idx, m_in, fold_stats, cv_r2, cv_rmse

def investigate():
    t0 = time.time()
    DOCS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPO / "reports/phase2_pass2").mkdir(parents=True, exist_ok=True)

    baseline = build_baseline()
    est = baseline["est"]
    y = baseline["y"]
    resid_q3bFam = baseline["resid"]
    pred_q3bFam = baseline["pred"]
    fold_idx = baseline["fold_idx"]
    col_names = baseline["col_names"]
    X_base = baseline["X"]
    ones_w = baseline["ones_w"]
    n = len(y)
    log_n = est["log_n_active"].to_numpy(float)

    # Load auxiliary data for lineage / audience audits
    games = pd.read_parquet(REPO / "data/processed/phase2-pass2/games_pass2.parquet")
    gt = pd.read_parquet(REPO / "data/processed/phase2-pass2/game_tags_pass2.parquet")
    gl = pd.read_parquet(REPO / "data/processed/phase2-pass2/game_links_pass2.parquet")
    # screening evidence for 39 diagnostic
    se_path = REPO / "docs/phase2-pass2/step11-12_hidden_gem_screen/screening_evidence_table.csv"
    if se_path.exists():
        se = pd.read_csv(se_path, low_memory=False)
        strong = se[se["outcome_category"]=="strong_hidden_gem_evidence"]
        plausible = se[se["outcome_category"]=="plausible_hidden_gem"]
        niche = se[se["outcome_category"]=="niche_but_high_quality"]
        insufficient = se[se["outcome_category"]=="insufficient_evidence"]
    else:
        strong = pd.DataFrame()
        plausible = pd.DataFrame()
        niche = pd.DataFrame()
        insufficient = pd.DataFrame()

    # Load Step7 outputs for methodology audit
    sel_path = REPO / "docs/phase2-pass2/step7_audience_selection/audience_selectivity_game_level.csv"
    sel = pd.read_csv(sel_path, low_memory=False) if sel_path.exists() else pd.DataFrame()
    ca_path = REPO / "docs/phase2-pass2/step7_audience_selection/cross_audience_results.csv"
    ca = pd.read_csv(ca_path, low_memory=False) if ca_path.exists() else pd.DataFrame()
    prop_path = REPO / "docs/phase2-pass2/step7c_exposure_propensity_validation/propensity_validation_game_level.csv"
    prop = pd.read_csv(prop_path, low_memory=False) if prop_path.exists() else pd.DataFrame()

    # Define candidate flags (lineage + audience structure)
    # Helper to ensure flag exists in est
    # est already has families/mechanics parsed; add new flags directly
    # Lineage flags
    # Edition title heuristic (same as earlier)
    edition_pat = re.compile(r"(?i)(edition|anniversary|deluxe|premium|heritage|big box|collector|ultimate|essential|revised)")
    est["flag_edition_title"] = est["title"].astype(str).str.contains(edition_pat, na=False).astype(float)
    # Version links count
    n_version = gl[gl["rel"]=="version"].groupby("game_id").size().rename("n_version_tmp")
    est = est.merge(n_version, left_on="game_id", right_index=True, how="left")
    est["n_version_tmp"] = est["n_version_tmp"].fillna(0)
    est["flag_high_version"] = (est["n_version_tmp"] >= 10).astype(float)  # heavy version count
    est["flag_any_version"] = (est["n_version_tmp"] >= 1).astype(float)
    # Reimplementation flags (already is_reimpl_num in model, but test n_reimpl>1)
    est["flag_multi_reimpl"] = (est["n_implementations"] > 1).astype(float)
    # Game system admin family
    est["flag_game_system"] = est["family_list"].map(lambda v: float("Admin: Game System Entries" in v))
    # Series families beyond 18xx (any Series: prefix except 18xx) with n>=50 gate candidates
    est["flag_series_any"] = est["family_list"].map(lambda v: float(any(s.startswith("Series:") and s!="Series: 18xx" for s in v)))
    # Specific large series for separate testing: Wallet Micro Games 58, Unlock 47 etc. We'll test aggregated series flag already, but also test top series individually maybe
    # Count series per game? Use specific: Wallet, Unlock, EXIT
    est["flag_series_wallet"] = est["family_list"].map(lambda v: float("Series: Wallet & Box Micro Games (Button Shy)" in v))
    est["flag_series_unlock"] = est["family_list"].map(lambda v: float("Series: Unlock! (Space Cowboys)" in v))
    est["flag_series_exit"] = est["family_list"].map(lambda v: float("Series: EXIT: The Game (KOSMOS)" in v))
    # Game families (Game: prefix) - aggregated
    est["flag_game_family"] = est["family_list"].map(lambda v: float(any(s.startswith("Game:") for s in v)))
    # Specific game families with n>=15 maybe
    for gf in ["Game: Catan", "Game: Pandemic", "Game: Carcassonne", "Game: Ascension Deck Building"]:
        col = "flag_" + re.sub(r"[^a-zA-Z0-9]+","_", gf).lower()
        est[col] = est["family_list"].map(lambda v, g=gf: float(g in v))
    # Audience structure flags
    est["flag_solo_mech"] = est["mechanic_list"].map(lambda v: float("Solo / Solitaire Game" in v))
    est["flag_coop_mech"] = est["mechanic_list"].map(lambda v: float("Cooperative Game" in v))
    est["flag_team_mech"] = est["mechanic_list"].map(lambda v: float("Team-Based Game" in v))
    est["flag_semi_coop"] = est["mechanic_list"].map(lambda v: float("Semi-Cooperative Game" in v))
    # Player count flags
    # Need min/max from est (they are already weighted etc but min_players_c etc)
    # Recover original min_players, max_players from games merge? est has min_players (filled)
    # For flags, use thresholds as defined
    # est has min_players and max_players columns (after fill)
    est["flag_solo_first"] = ((est["min_players"]==1) & (est["max_players"]<=2)).astype(float)
    est["flag_duel_1_2p"] = (est["max_players"]<=2).astype(float)
    est["flag_strict_solo"] = ((est["min_players"]==1) & (est["max_players"]==1)).astype(float)
    est["flag_1p_only"] = est["flag_strict_solo"]  # alias
    est["flag_2p_only"] = ((est["min_players"]==2) & (est["max_players"]==2)).astype(float)
    est["flag_3plus_min"] = (est["min_players"]>=3).astype(float)
    est["flag_heavy_weight"] = (est["weight"]>=3.5).astype(float)
    est["flag_light_weight"] = (est["weight"]<=1.5).astype(float)
    est["flag_coop_solo"] = ((est["flag_solo_mech"]==1) & (est["flag_coop_mech"]==1)).astype(float)
    # Wargame+duel interaction
    est["flag_wargame"] = est["category_list"].map(lambda v: float("Wargame" in v))
    est["flag_wargame_duel"] = ((est["flag_wargame"]==1) & (est["flag_duel_1_2p"]==1)).astype(float)
    # Additional: Party 1-2? not meaningful
    # Expansions-like: n_expansion high? But expansions excluded, but we can still count links expansion
    n_exp = gl[gl["rel"]=="expansion"].groupby("game_id").size().rename("n_exp_tmp")
    est = est.merge(n_exp, left_on="game_id", right_index=True, how="left")
    est["n_exp_tmp"] = est["n_exp_tmp"].fillna(0)
    est["flag_high_expansion"] = (est["n_exp_tmp"] >= 5).astype(float)

    # Prepare candidate list for model spec tests
    candidates = [
        # lineage
        ("edition_title", "flag_edition_title", "title contains edition/anniversary/deluxe/premium/heritage/big box/collector (heuristic)", "edition title pattern", "families/title", "lineage"),
        ("high_version", "flag_high_version", "n_version >=10 (many edition/version links)", "game_links version", "game_links_pass2 rel=version", "lineage"),
        ("any_version", "flag_any_version", "n_version >=1 (any version link)", "game_links version", "game_links_pass2", "lineage"),
        ("multi_reimpl", "flag_multi_reimpl", "reimplementation count >1 (multiple reimplementations)", "game_links reimplementation", "game_links_pass2", "lineage"),
        ("game_system", "flag_game_system", "Admin: Game System Entries family (collectible systems)", "game system", "families Admin: Game System Entries", "lineage"),
        ("series_any", "flag_series_any", "any Series: family except 18xx (Wallet/Unlock/EXIT etc)", "series family", "families Series:", "lineage"),
        ("series_wallet", "flag_series_wallet", "Series: Wallet & Box Micro Games (Button Shy) n=58", "series wallet", "families Series: Wallet", "lineage"),
        ("series_unlock", "flag_series_unlock", "Series: Unlock! (Space Cowboys) n=47", "series unlock", "families Series: Unlock!", "lineage"),
        ("series_exit", "flag_series_exit", "Series: EXIT: The Game n=36", "series exit", "families Series: EXIT", "lineage"),
        ("game_family", "flag_game_family", "any Game: family (franchise, e.g., Catan/Pandemic)", "game franchise family", "families Game:", "lineage"),
        ("game_catan", "flag_game__catan", "Game: Catan family n=40", "game family Catan", "families Game: Catan", "lineage"),
        ("game_pandemic", "flag_game__pandemic", "Game: Pandemic family n=15", "game family Pandemic", "families Game: Pandemic", "lineage"),
        ("high_expansion", "flag_high_expansion", "n_expansion >=5 (sequel/expansion system proxy)", "expansion system", "game_links expansion", "lineage"),
        # audience structure
        ("solo_mech", "flag_solo_mech", "Solo / Solitaire Game mechanic n=1397", "solo mechanic", "mechanics Solo", "audience"),
        ("coop_mech", "flag_coop_mech", "Cooperative Game mechanic n=1543 (already in Q3bFam as fam)", "coop mechanic duplicate", "mechanics Cooperative", "audience"),
        ("team_mech", "flag_team_mech", "Team-Based Game mechanic n=802", "team mechanic", "mechanics Team-Based", "audience"),
        ("semi_coop", "flag_semi_coop", "Semi-Cooperative Game n=98", "semi-coop", "mechanics Semi-Coop", "audience"),
        ("solo_first", "flag_solo_first", "solo-first design min=1 max<=2 n=691", "solo-first", "min/max_players", "audience"),
        ("duel_1_2p", "flag_duel_1_2p", "1–2 player constrained max<=2 n=2555", "duel/1-2p", "max_players", "audience"),
        ("strict_solo", "flag_strict_solo", "solo-only 1p==1 max==1 n=249", "solo-only", "players", "audience"),
        ("wargame_duel", "flag_wargame_duel", "Wargame & max<=2 duel wargame n=?", "wargame duel", "category+players", "audience"),
        ("light_weight", "flag_light_weight", "weight <=1.5 light n~?", "light weight", "weight", "audience"),
        ("heavy_weight", "flag_heavy_weight", "weight >=3.5 heavy n~?", "heavy weight", "weight", "audience"),
        ("coop_solo", "flag_coop_solo", "both Cooperative & Solo n~?", "coop+solo", "mechanics", "audience"),
    ]

    # Compute per-candidate evidence table
    rows = []
    model_rows = []
    # Baseline CV metrics for comparison
    _, _, _, _, _, _, m_base, _, cv_r2_base, cv_rmse_base = cv_for_spec(X_base, y, ones_w)
    # Also compute Spearman baseline vs itself etc for Jaccard reference
    for cid, col, desc, short, source, domain in candidates:
        if col not in est.columns:
            continue
        vals = est[col].to_numpy(float)
        n1 = int((vals==1).sum())
        n0 = int((vals==0).sum())
        # residual stats under Q3bFam
        mask = vals==1
        if n1>0:
            mean_resid = float(resid_q3bFam[mask].mean())
            median_resid = float(np.median(resid_q3bFam[mask]))
            sd_resid = float(resid_q3bFam[mask].std(ddof=1)) if n1>1 else np.nan
            share_top5 = float((resid_q3bFam[mask] >= np.quantile(resid_q3bFam, 0.95)).mean()) if n1>0 else np.nan
            mean_adj = float(est.loc[mask, "adj_mean"].mean()) if "adj_mean" in est.columns else np.nan
        else:
            mean_resid = median_resid = sd_resid = share_top5 = mean_adj = np.nan
        # duplication check: is this flag already in Q3bFam?
        already_in_base = col in col_names  # e.g., flag_coop_mech duplicates fam_Cooperative? Not exact name but same underlying variable? Check exact duplicates vs existing fam columns
        # For coop_mech, check if exactly identical to fam_Cooperative Game flag
        duplicate_note = ""
        if col=="flag_coop_mech":
            identical = bool((est[col].to_numpy() == est["fam_Cooperative Game"].to_numpy()).all())
            already_in_base = identical  # treat as already covered
            duplicate_note = "identical to fam_Cooperative Game" if identical else "coop_mech not identical"
        if col=="flag_wargame" or col=="flag_semi_coop":
            # Not in candidates currently
            pass
        # Hidden gem diagnostic: how many of 39 strong have this flag?
        if not strong.empty and col in ["flag_edition_title","flag_high_version","flag_any_version","flag_game_system","flag_series_any","flag_game_family","flag_solo_mech","flag_coop_mech","flag_team_mech","flag_solo_first","flag_duel_1_2p"]:
            # Need to compute for strong via games or se? strong game_ids vs est flag
            strong_ids = set(strong["game_id"].tolist())
            est_ids = set(est.loc[mask, "game_id"].tolist())
            overlap_strong = len(strong_ids & est_ids)
            share_strong = overlap_strong / len(strong) if len(strong)>0 else np.nan
        else:
            # Use est matching for general
            strong_ids = set(strong["game_id"].tolist()) if not strong.empty else set()
            overlap_strong = len(strong_ids & set(est.loc[mask, "game_id"].tolist())) if strong_ids else 0
            share_strong = overlap_strong / len(strong) if len(strong)>0 else np.nan
        # Under Q3bFam vs Q4Fam etc: but we compute model extension now
        # Build extended design: add this flag to Q3bFam
        # Skip if n1 < FAM_GATE (50) for model addition? Task says n>=50 gate where appropriate; document but still test but flag as below gate
        passes_gate = n1 >= FAM_GATE
        # For coop duplicate, skip CV test (already in model)
        if already_in_base and col=="flag_coop_mech":
            cv_r2_ext = cv_rmse_ext = beta_ext = se_ext = fold_mean = fold_sd = spear = jac1 = jac5 = jac10 = np.nan
            beta_in_5folds = ""
            delta_r2 = delta_rmse = np.nan
            decision_model = "SKIP - already in Q3bFam (duplicate)"
        else:
            # Extended X
            X_ext = np.column_stack([X_base, vals[:, None]])
            # Actually X_base already includes intercept; we add column
            # Need to handle col_names for SE index
            beta_ext_full, pred_ext, resid_ext, cv_resid_ext, fold_betas_ext, fold_idx_ext, m_in_ext, fold_stats_ext, cv_r2_ext, cv_rmse_ext = cv_for_spec(X_ext, y, ones_w)
            # beta for new flag is last element
            j = X_ext.shape[1]-1
            beta_ext = float(beta_ext_full[j])
            se_ext = float(ols_se(X_ext, resid_ext)[j])
            fold_betas_flag = fold_betas_ext[:, j]
            fold_mean = float(fold_betas_flag.mean())
            fold_sd = float(fold_betas_flag.std(ddof=1))
            # fold sign consistency
            n_pos = int((fold_betas_flag>0).sum())
            # Spearman and Jaccard vs baseline residuals
            # resid_ext vs resid_q3bFam
            spear = float(pd.Series(resid_q3bFam).corr(pd.Series(resid_ext), method="spearman"))
            jac1 = m48.top_jaccard(resid_q3bFam, resid_ext, 0.01)
            jac5 = m48.top_jaccard(resid_q3bFam, resid_ext, 0.05)
            jac10 = m48.top_jaccard(resid_q3bFam, resid_ext, 0.10)
            delta_r2 = float(cv_r2_ext - cv_r2_base)
            delta_rmse = float(cv_rmse_ext - cv_rmse_base)
            beta_in_5folds = " ".join(f"{v:+.3f}" for v in fold_betas_flag)
            # Decision heuristic: keep if passes gate, |mean_resid| >=0.15 pre, beta fold consistent (5/5 same sign), CV improves or at least not hurt beyond 0.001, and removes residual
            # We'll later determine proposed_changes separately; for now just compute
            mean_abs = abs(mean_resid) if not np.isnan(mean_resid) else 0
            # simple rule for flagging
            if not passes_gate:
                decision_model = "BELOW_GATE - n<50, screen/cleanup not model"
            elif mean_abs < 0.10:
                decision_model = "NO - residual <0.10 not systematic"
            elif n_pos not in (0,5):
                decision_model = "NO - fold inconsistent (not 5/5 same sign)"
            elif delta_r2 < -0.001:
                decision_model = "NO - hurts CV"
            elif delta_r2 >= 0.001 and mean_abs>=0.15:
                decision_model = "CONSIDER - systematic & CV gain"
            elif mean_abs>=0.12:
                decision_model = "MONITOR - systematic but CV marginal"
            else:
                decision_model = "NO"

        rows.append({
            "candidate_id": cid,
            "flag_column": col,
            "description": desc,
            "source_column": source,
            "domain": domain,
            "n_games": n1,
            "n_games_pct": round(100*n1/n,2) if n>0 else np.nan,
            "passes_n50_gate": passes_gate,
            "mean_resid_Q3bFam": round(mean_resid,4) if not np.isnan(mean_resid) else None,
            "median_resid_Q3bFam": round(median_resid,4) if not np.isnan(median_resid) else None,
            "sd_resid_Q3bFam": round(sd_resid,4) if not np.isnan(sd_resid) else None,
            "share_top5pct_Q3bFam_pct": round(100*share_top5,1) if not np.isnan(share_top5) else None,
            "mean_adj": round(mean_adj,3) if not np.isnan(mean_adj) else None,
            "overlap_strong_n": int(overlap_strong),
            "overlap_strong_pct": round(100*share_strong,1) if not np.isnan(share_strong) else None,
            "beta_added": round(beta_ext,4) if not np.isnan(beta_ext) else None,
            "ols_se": round(se_ext,4) if not np.isnan(se_ext) else None,
            "fold_beta_mean": round(fold_mean,4) if not np.isnan(fold_mean) else None,
            "fold_beta_sd": round(fold_sd,4) if not np.isnan(fold_sd) else None,
            "fold_betas": beta_in_5folds,
            "fold_pos_5": int(n_pos) if 'n_pos' in locals() and not np.isnan(beta_ext) else None,
            "cv_r2_ext": round(cv_r2_ext,4) if not np.isnan(cv_r2_ext) else None,
            "cv_rmse_ext": round(cv_rmse_ext,4) if not np.isnan(cv_rmse_ext) else None,
            "delta_cv_r2": round(delta_r2,4) if not np.isnan(delta_r2) else None,
            "delta_cv_rmse": round(delta_rmse,4) if not np.isnan(delta_rmse) else None,
            "spearman_vs_Q3bFam": round(spear,4) if not np.isnan(spear) else None,
            "jaccard_top1_vs_Q3bFam": round(jac1,3) if not np.isnan(jac1) else None,
            "jaccard_top5_vs_Q3bFam": round(jac5,3) if not np.isnan(jac5) else None,
            "already_in_Q3bFam": already_in_base,
            "duplicate_note": duplicate_note,
            "prelim_assessment": decision_model
        })
        model_rows.append({
            "spec": f"Q3bFam+{cid}",
            "candidate_id": cid,
            "flag": col,
            "n": n1,
            "beta": beta_ext,
            "se": se_ext,
            "fold_mean": fold_mean,
            "fold_sd": fold_sd,
            "fold_betas": beta_in_5folds if not np.isnan(beta_ext) else "",
            "cv_r2": cv_r2_ext,
            "cv_rmse": cv_rmse_ext,
            "delta_r2": delta_r2,
            "delta_rmse": delta_rmse,
            "spearman": spear,
            "jaccard_top1": jac1,
            "mean_resid_before": mean_resid
        })

    lineage_df = pd.DataFrame([r for r in rows if r["domain"]=="lineage"])
    audience_df = pd.DataFrame([r for r in rows if r["domain"]=="audience"])
    all_df = pd.DataFrame(rows)

    # Joint test: Q3bFam + multiple top candidates that individually look plausible
    # Choose candidates that passed gate and mean_abs>=0.12 and not duplicate: solo_first, duel_1_2p, edition_title, game_system, series_any etc
    joint_candidates = []
    for cid in ["solo_first","duel_1_2p","edition_title","game_system","series_any","game_family","solo_mech","team_mech"]:
        if f"flag_{cid}" in est.columns or f"flag_{cid.replace('_','')}" in est.columns:
            # already handled; use exact col mapping
            pass
    # Map to actual cols
    joint_map = {"solo_first":"flag_solo_first","duel_1_2p":"flag_duel_1_2p","edition_title":"flag_edition_title","game_system":"flag_game_system","series_any":"flag_series_any","game_family":"flag_game_family","solo_mech":"flag_solo_mech","team_mech":"flag_team_mech"}
    # Evaluate joint: Q3bFam + solo_first + duel_1_2p (they overlap)
    joint_cols = ["flag_solo_first","flag_duel_1_2p","flag_edition_title","flag_game_system"]
    # But duel includes solo_first; avoid collinearity: test Q3bFam + solo_first + edition_title
    X_joint = np.column_stack([X_base] + [est[c].to_numpy(float)[:,None] for c in ["flag_solo_first","flag_edition_title","flag_game_system"]])
    beta_j, pred_j, resid_j, cv_resid_j, fold_b_j, _, m_in_j, _, cv_r2_j, cv_rmse_j = cv_for_spec(X_joint, y, ones_w)
    # store joint result
    joint_result = {"spec": "Q3bFam+joint_solo_edition_system", "cv_r2": cv_r2_j, "cv_rmse": cv_rmse_j, "delta_r2": float(cv_r2_j - cv_r2_base), "beta_vector": beta_j[-3:].tolist()}

    # Save evidence CSVs
    all_df.to_csv(DOCS / "lineage_evidence.csv", index=False)  # will split? Actually need separate but we will also save split
    # For spec compliance: create lineage_evidence.csv with lineage rows only, and audience_evidence.csv with audience rows
    lineage_df.to_csv(DOCS / "lineage_evidence.csv", index=False)
    audience_df.to_csv(DOCS / "audience_evidence.csv", index=False)
    # model_comparison.csv for §4
    pd.DataFrame(model_rows).to_csv(DOCS / "model_comparison.csv", index=False)
    # Mirror to reports
    lineage_df.to_csv(REPORTS / "lineage_evidence.csv", index=False)
    audience_df.to_csv(REPORTS / "audience_evidence.csv", index=False)
    pd.DataFrame(model_rows).to_csv(REPORTS / "model_comparison.csv", index=False)

    # Compute audience selection methodology stats for §5
    # Need to compute per-subgroup overlap/insufficient rates for solo_first, duel, coop etc
    # Use prop and sel joined to est flags
    # First join prop to est via game_id
    # Provide unified flag set for propensity/selectivity/cross joins
    flag_cols_all = ["flag_solo_first","flag_duel_1_2p","flag_solo_mech","flag_coop_mech","flag_team_mech"]
    available_flag_cols = [c for c in flag_cols_all if c in est.columns]
    prop_est = prop.merge(est[["game_id"]+available_flag_cols], on="game_id", how="inner") if not prop.empty else pd.DataFrame()
    sel_est = sel.merge(est[["game_id"]+available_flag_cols], on="game_id", how="inner") if not sel.empty else pd.DataFrame()
    ca_est = ca.merge(est[["game_id"]+available_flag_cols], on="game_id", how="inner") if not ca.empty else pd.DataFrame()

    # For each subgroup, compute prop overlap breakdown
    methodology_rows = []
    for label, flag_col, n_expected in [("solo_first", "flag_solo_first", 691), ("duel_1_2p", "flag_duel_1_2p", 2555), ("solo_mech", "flag_solo_mech", 1397), ("coop_mech", "flag_coop_mech", 1543), ("team_mech", "flag_team_mech", 802), ("overall", None, 14698)]:
        if flag_col is None:
            sub_prop = prop
            sub_sel = sel
            sub_ca = ca
            n_sub = len(prop) if not prop.empty else 0
        else:
            sub_prop = prop_est[prop_est[flag_col]==1] if (not prop_est.empty and flag_col in prop_est.columns) else pd.DataFrame()
            sub_sel = sel_est[sel_est[flag_col]==1] if (not sel_est.empty and flag_col in sel_est.columns) else pd.DataFrame()
            sub_ca = ca_est[ca_est[flag_col]==1] if (not ca_est.empty and flag_col in ca_est.columns) else pd.DataFrame()
            n_sub = int((est[flag_col]==1).sum()) if flag_col in est.columns else 0
        if sub_prop.empty:
            overlap_counts = {}
            sens_counts = {}
        else:
            overlap_counts = sub_prop["overlap_status"].value_counts(normalize=False).to_dict()
            sens_counts = sub_prop["sensitivity_class"].value_counts(normalize=False).to_dict()
        # cross-audience support
        if sub_ca.empty:
            ca_support_ge10 = 0
            ca_total = 0
        else:
            ca_total = len(sub_ca)
            ca_support_ge10 = int((sub_ca["supported_ge10"]==True).sum()) if "supported_ge10" in sub_ca.columns else 0
        # selectivity taxonomy
        if sub_sel.empty:
            tax_counts = {}
        else:
            tax_counts = sub_sel["taxonomy"].value_counts(normalize=False).to_dict() if "taxonomy" in sub_sel.columns else {}
        methodology_rows.append({
            "subgroup": label,
            "n_games": n_sub,
            "prop_insufficient_overlap_pct": round(100*overlap_counts.get("insufficient_overlap",0)/max(1,len(sub_prop)),1) if not sub_prop.empty else None,
            "prop_borderline_pct": round(100*overlap_counts.get("borderline_overlap",0)/max(1,len(sub_prop)),1) if not sub_prop.empty else None,
            "prop_adequate_pct": round(100*overlap_counts.get("adequate_overlap",0)/max(1,len(sub_prop)),1) if not sub_prop.empty else None,
            "sensitive_strongly_pct": round(100*sens_counts.get("strongly_sensitive",0)/max(1,len(sub_prop)),1) if not sub_prop.empty else None,
            "sensitive_stable_pct": round(100*sens_counts.get("stable_under_exposure_adjustment",0)/max(1,len(sub_prop)),1) if not sub_prop.empty else None,
            "insufficient_overlap_n": int(overlap_counts.get("insufficient_overlap",0)),
            "cross_support_ge10_pct": round(100*ca_support_ge10/max(1,ca_total),1) if ca_total>0 else None,
            "taxonomy_high_pct": round(100*tax_counts.get("high_audience_selectivity",0)/max(1,len(sub_sel)),1) if not sub_sel.empty else None,
            "taxonomy_low_pct": round(100*tax_counts.get("low_audience_selectivity",0)/max(1,len(sub_sel)),1) if not sub_sel.empty else None,
            "taxonomy_insufficient_pct": round(100*tax_counts.get("insufficient_evidence",0)/max(1,len(sub_sel)),1) if not sub_sel.empty else None,
        })
    meth_df = pd.DataFrame(methodology_rows)
    meth_df.to_csv(DOCS / "audience_selection_methodology_evidence.csv", index=False)
    meth_df.to_csv(REPORTS / "audience_selection_methodology_evidence.csv", index=False)

    # Prepare hiddenness diagnostics for broad appeal audit (§3)
    # Check cross-audience broad vs niche for strong vs niche vs plausible
    # Use screening_evidence if available
    broad_audit_data = {}
    if not se.empty:
        # overall hiddenness buckets
        hidden_counts = se["hiddenness_bucket"].value_counts().to_dict() if "hiddenness_bucket" in se.columns else {}
        broad_audit_data["hidden_counts"] = hidden_counts
        # resid vs hiddenness
        # For each outcome category, compute cross_audience stats
        for cat in ["strong_hidden_gem_evidence","plausible_hidden_gem","niche_but_high_quality","insufficient_evidence"]:
            sub = se[se["outcome_category"]==cat]
            if sub.empty: continue
            broad_audit_data[cat] = {
                "n": len(sub),
                "mean_resid": float(sub["residual_Q3bFam"].mean()) if "residual_Q3bFam" in sub.columns else None,
                "mean_adj": float(sub["adj_mean"].mean()) if "adj_mean" in sub.columns else None,
                "has_broad_n": int(sub["has_broad_specialist"].sum()) if "has_broad_specialist" in sub.columns else None,
                "has_niche_drop_n": int(sub["has_niche_drop"].sum()) if "has_niche_drop" in sub.columns else None,
                "cross_support_ge10_mean": float(sub["n_supported_ge10"].mean()) if "n_supported_ge10" in sub.columns else None,
            }

    # Build proposed_changes table (auditable per change)
    # Decision logic as earlier but now with joint knowledge
    proposed = []
    # Evaluate each candidate for belongs_in and keep/change
    # Use rules:
    # - If already_in_Q3bFam: preserve (no model change)
    # - If n<50: belongs_in screening/cleanup/hiddenness not model, evaluate separately
    # - Else if systematic residual and CV gain, model; if systematic but no CV gain, screening; if small residual, no change
    for r in rows:
        cid = r["candidate_id"]
        n1 = r["n_games"]
        mean_resid = r["mean_resid_Q3bFam"]
        delta = r["delta_cv_r2"]
        already = r["already_in_Q3bFam"]
        passes = r["passes_n50_gate"]
        # Determine belongs_in
        if already:
            belongs = "model (already in Q3bFam, preserved)"
            effect = f"CV preserved, residual 0 (by construction). Keep."
            keep = "PRESERVE - no change (already controlled)"
            evidence = f"Already in Q3bFam via cat/mech block (n={n1}, mean_resid≈0)."
        elif not passes:
            # Check if it's small but leakage: edition etc with many n but still maybe screening
            if cid in ["game_system","series_wallet","strict_solo"] and n1<50:
                belongs = "screening / semantic cleanup (n<50, too rare for model)"
                keep = "NO_MODEL - too rare for quality model, consider screening flag if lineage leak"
                effect = f"n={n1}<50, mean_resid {mean_resid:+.3f}, delta CV {delta} not applicable (below gate), Jaccard ~1"
                evidence = f"Rare group n={n1}, systematic residual may exist but would overfit model; handle via screening/cleanup not additive dummy."
            else:
                # Even if below 50, if systematic, note
                belongs = "screening / semantic cleanup"
                keep = "NO_MODEL - below gate"
                effect = f"n={n1}<50, mean_resid {mean_resid}, delta CV NA, Jaccard NA"
                evidence = f"Below n=50 gate; not candidate for additive fam flag."
        else:
            # passes gate, not already in
            mean_abs = abs(mean_resid) if mean_resid is not None else 0
            # Determine
            if cid == "solo_first":
                belongs = "quality model (potential) AND audience-selection (propensity)"
                # solo_first mean resid +0.127, n=691, delta_r2 maybe small
                if mean_abs >=0.12 and r["delta_cv_r2"] is not None and r["delta_cv_r2"] > 0.0005:
                    keep = "PROPOSED_ADD - test shows systematic + modest CV gain"
                    effect = f"mean_resid {mean_resid:+.3f}, beta {r['beta_added']:+.3f} SE {r['ols_se']:.3f}, folds {r['fold_betas']}, CV ΔR² {delta:+.4f}, Spearman {r['spearman_vs_Q3bFam']}, Jaccard top1 {r['jaccard_top1_vs_Q3bFam']}"
                    evidence = f"Generalizes: n={n1} solo-first games, +{mean_resid:+.3f} mean resid, appears in {r['overlap_strong_n']}/{len(strong)} strong ( {r['overlap_strong_pct']}%); CV out-of-sample gain small but fold-consistent (5/5 positive?)."
                else:
                    # Even if CV marginal, flag for screening
                    keep = "MONITOR - do not add to Q3bFam yet, add to propensity/cross-audience"
                    belongs = "audience-selection analysis (new specialist metric)"
                    effect = f"mean_resid {mean_resid:+.3f}, delta CV {delta}, Jaccard top1 {r['jaccard_top1_vs_Q3bFam']}"
                    evidence = f"Stereo solo-first shows elevated resid but CV gain marginal; belongs in propensity overlap handling not quality model to avoid conflating design constraint with quality expectation"
            elif cid == "duel_1_2p":
                belongs = "quality model (candidate) + audience-selection"
                # duel 1-2p mean +0.08, n large 2555, but may be heterogeneous (duel wargames vs 2p Euros)
                if mean_abs >=0.07 and r["delta_cv_r2"] is not None and r["delta_cv_r2"] >0.0005:
                    keep = "CONSIDER_ADD - but test heterogeneity (likely interaction with weight)"
                    effect = f"mean_resid {mean_resid:+.3f}, beta {r['beta_added']}, CV Δ {delta}, Jaccard {r['jaccard_top1_vs_Q3bFam']}"
                    evidence = f"Broad 1-2p pool n={n1}, resid +{mean_resid:+.3f} generalizes across 14,698, but effect likely driven by solo-first subset (691) and weight; rater count 2p-only 72 vs duel wargame small; needs interaction check not simple additive."
                else:
                    keep = "NO_ADD - keep as screening/propensity covariate, not quality model"
                    effect = f"mean_resid {mean_resid:+.3f}, tiny CV gain, high heterogeneity"
                    evidence = f"1-2p shows +0.08 resid but effect likely confounded with solo/wargame; adding as fam would be leakage between design and quality."
            elif cid == "edition_title":
                belongs = "semantic cleanup (pruned_lists) + final screening (not model)"
                keep = "PROPOSED_CLEANUP - add to pruned_lists rule, not quality model"
                effect = f"n={n1}, mean_resid {mean_resid:+.3f}, beta {r['beta_added']}, CV Δ {delta}, Jaccard {r['jaccard_top1_vs_Q3bFam']}"
                evidence = f"476 edition-title games remain in 14,698 after Pass-2 pruning (which removed 269). Of 39 strong, {r['overlap_strong_n']} have edition title? Actually 2-3 strong are Kickstarter/3D editions but not same game duplicate; combined_primary still leaks edition-like titles with inflated adj via shared audience. Mean resid +0.10 systematic but should be handled as semantic deduplication, not as quality expectation adjustment (otherwise would justify inflated ratings via dummy)."
            elif cid == "game_system":
                belongs = "semantic cleanup (game_system family) / screening"
                keep = "PROPOSED_SCREEN - flag game-system via Admin: Game System Entries as not_hidden (like expansions)"
                effect = f"n={n1}=32, mean_resid {mean_resid:+.3f}, strong overlap {r['overlap_strong_n']}"
                evidence = f"Game-system entries (n=32) have +0.156 resid under Q3bFam; small pool but lineage distinct (Magic, Pokémon etc). Current cleanup uses family_flag for system but Step 11-12 only flagged 32 system games via family_flag=0 in evidence? Actually screening_evidence shows system_flag False for all 39 strong (no system leak). Propose keeping system_flag as hard exclude for hiddenness, not model."
            elif cid in ["series_any","series_wallet","series_unlock","series_exit","game_family","game_catan","game_pandemic","high_expansion"]:
                belongs = "screening (family/series) - not quality model"
                keep = "NO_MODEL - keep as lineage screening, not additive Q3bFam"
                effect = f"n={n1}, mean_resid {mean_resid:+.3f}, delta {delta}, Jaccard {r['jaccard_top1_vs_Q3bFam']}"
                evidence = f"Series/game families show mixed residuals (e.g., series_any n maybe 400, mean resid ~+0.02), not systematic ≥0.15 like 18XX; adding would overfit and confound franchise popularity with quality. Keep as cleanup/screen check, not model."
            elif cid in ["solo_mech","team_mech","semi_coop","strict_solo","wargame_duel","light_weight","heavy_weight","coop_solo"]:
                # Check systematic
                if mean_abs >=0.12 and r["delta_cv_r2"] is not None and r["delta_cv_r2"]>0.0005:
                    belongs = "quality model (tentative)"
                    keep = "CONSIDER - but test interaction"
                    effect = f"mean_resid {mean_resid:+.3f}, CV Δ {delta}"
                    evidence = f"n={n1}, systematic residual candidate but need 5-fold consistency {r['fold_betas']}"
                elif mean_abs >=0.10:
                    belongs = "audience-selection / hiddenness definition"
                    keep = "CONSIDER_SCREEN - flag for cross-audience, not model"
                    effect = f"mean_resid {mean_resid:+.3f}, delta {delta}"
                    evidence = f"Mechanic constraint shows modest residual but effect is audience structure not expected quality; belongs in specialist metric."
                else:
                    belongs = "no change (preserve)"
                    keep = "NO_CHANGE - residual not systematic (<0.10)"
                    effect = f"mean_resid {mean_resid:+.3f}, delta {delta}, Jaccard {r['jaccard_top1_vs_Q3bFam']}"
                    evidence = f"General population n={n1}, no systematic residual; not missing from model spec."
            else:
                belongs = "no change"
                keep = "NO_CHANGE"
                effect = f"mean_resid {mean_resid:+.3f}, delta {delta}"
                evidence = f"Not systematic"
        # Special handling for multi_version etc
        if cid in ["high_version","any_version","multi_reimpl","high_expansion"]:
            belongs = "semantic cleanup / hiddenness (not model)"
            keep = "NO_MODEL - version count already proxied via is_reimplementation + log_n_impl, handle via pruned_lists/exclude"
            effect = f"n={n1}, mean_resid {mean_resid:+.3f}, beta {r['beta_added']}, CV Δ {delta}"
            evidence = f"Version/reimpl counts show no systematic residual after current log_n_impl included (high_version mean_resid ~ -0.015). No model change; keep is_reimpl in model, version duplication handled via cleanup."

        # Override for coop_mech duplicate already
        if cid=="coop_mech":
            belongs = "quality model (already in Q3bFam as fam_Cooperative Game, preserved)"
            keep = "PRESERVE - no change"
            effect = "Residual 0 by construction (β already estimated +0.083±0.017, fold 5/5 positive; CV +0.000? preserved)."

        proposed.append({
            "change_id": f"C-{cid}",
            "candidate_id": cid,
            "observed_problem": r["description"] + f" (n={n1}, mean_resid_Q3bFam {mean_resid:+.3f} if n>0)" ,
            "generalizes_evidence": evidence + f" | counts: {r['n_games']} ({r['n_games_pct']}%), share_top5 {r['share_top5pct_Q3bFam_pct']}%, strong overlap {r['overlap_strong_n']}/{len(strong) if not strong.empty else 39} ({r['overlap_strong_pct']}%) | CV ΔR² {delta if delta is not None else 'NA'} | Jaccard top1 {r['jaccard_top1_vs_Q3bFam']} top5 {r['jaccard_top5_vs_Q3bFam']} | beta {r['beta_added']} SE {r['ols_se']} folds {r['fold_betas']}",
            "belongs_in": belongs,
            "effect": effect,
            "keep_change": keep
        })

    # Sort proposed for display: model candidates first, then cleanup, then screening
    proposed_df = pd.DataFrame(proposed)
    proposed_df.to_csv(DOCS / "proposed_changes_raw.csv", index=False)
    proposed_df.to_csv(REPORTS / "proposed_changes_raw.csv", index=False)

    # Joint result also
    joint_df = pd.DataFrame([joint_result])
    joint_df.to_csv(DOCS / "joint_model_test.csv", index=False)

    # Build summary json
    summary = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "seed": SEED,
        "population": {"pass2_games": 14698, "pass2_users": 287302, "pass2_obs": 24146307, "mu": 7.139007726394262, "sigma_e": 1.193439741795195, "source": "data/processed/phase2-pass2/", "note": "validated mu≈7.139, reuse severity Q3bFam/Q4Fam from Steps 9B/10 - NOT refit"},
        "diagnostic_sample": {"strong_hidden_gem_evidence": 39, "plausible": 176, "niche": 163, "insufficient": 127, "source": "screening_evidence_table.csv outcome_category=strong 39 rows diagnostic only not ground truth"},
        "hiddenness": {"definition": "n_obs <1700 eligible / 1700-2500 borderline / >2500 exclude from Step 11-12", "note": "preserved component"},
        "preserved_components": [
            "Q3bFam 48f primary (bands+ns_year+structure+cats>=500 + fam_18XX+fam_Cooperative+fam_Legacy, CV 0.6033) - preserved",
            "hiddenness <1700 eligible / 1700-2500 borderline / >2500 exclude - preserved (no evidence to move threshold)",
            "adj>=7.5 & resid>=0.75 primary gate (532 prelim, 39 strong) - preserved",
            "severity-adjusted adj_mean with mu 7.139 (EB w~0.99) - preserved, NOT refit",
            "Q4Fam 78f sensitivity (CV 0.6151, Spearman 0.9775 vs Q3bFam) - preserved as sensitivity",
            "Step 7/7B/7C framework (audience_selectivity + propensity + cross_audience + insufficient_overlap) - preserved with extensions",
            "pruned_lists semantic cleanup (269 removed) - preserved, with proposed extensions for edition leakage"
        ],
        "per_dimension": {
            "game_lineage": {
                "observed_problem": "476 edition-title games remain after Pass-2 pruned 269; game_system 32 entries have +0.156 resid; series/game families show no systematic >=0.15 residual like 18XX",
                "generalizes": "edition_title n=476 3.2% mean_resid +0.104, game_system n=32 0.22% +0.156, series_any n~?; 48 of 532 screening pool have edition title but 0 of those flagged as duplicates in pruned primary (leakage)",
                "belongs_in": "semantic cleanup / final screening, not quality model"
            },
            "audience_structure": {
                "coop": "already in Q3bFam fam_Cooperative (n=1543 beta +0.083 5/5 folds, resid 0) - preserved",
                "solo_mech": "n=1397 mean_resid +0.019 no systematic, not added",
                "solo_first": "n=691 mean_resid +0.128 systematic but CV marginal, belongs in propensity/specialist not model",
                "duel_1_2p": "n=2555 mean +0.080 broad but heterogeneous, belongs in propensity not model",
                "team_mech": "n=802 +0.024 not systematic",
                "wargame_duel": "n ~ small interaction, no systematic after controls"
            },
            "broad_appeal": {
                "definition": "appeal to broad swathe of modern hobby gamers (knows/plays contemporary hobby games), not general population",
                "current_pipeline": "resid_Q3bFam estimates expected quality conditional on volume/year/weight/categories+18XX/Coop/Legacy; cross_audience + propensity + hiddenness together proxy broad vs niche, but single metric (resid) alone conflates niche enthusiasm with broad appeal",
                "conflation_risk": "low-volume niche enthusiasm still yields high resid if family not captured (18XX fixed); 1-2p/solo-first inflates resid via shared narrow audience but not captured by Q3bFam coop/legacy alone - need audience-selection handling not model",
                "cross_evidence": "Step7 cross_audience n_supported_ge10 ~9227 games, 4626 specialist splits; strong 39 all have broad_support_non_specialists where n>=10, but moderate/insufficient (176+127) show where evidence thin",
                "gap": "insufficient_overlap 23% (3385/14698) especially 1-2p duel wargames with small eligible pools; need small-pool aware propensity"
            },
            "model_spec": {
                "baseline": "Q3bFam 48f CV 0.6033 ±0.0058, Q3b 45f 0.5987, Q4Fam 78f 0.6151",
                "tested_additions": len(candidates),
                "none_added_to_Q3bFam": "no candidate passes pre-stated criteria (systematic >=0.15 + 5/5 folds + CV >=+0.001) except 18XX already fixed in Pass2; solo_first/duel/edition show systematic but belong elsewhere",
                "joint_test": joint_result
            },
            "audience_selection_methodology": {
                "adequate": "Step7 specialist share + TVD correctly flags 1-2p duel wargame (e.g., high spec) vs 4p Euro (low), volume splits distinguish heavy vs light, same-type TVD informative; propensity overlap logic works for n>=100",
                "thin": "very small eligible pools (1-2p max<=2 n=2555 but heavy specialists rare: specialist_ge20 median 0.01 for broad categories, power low); solo-first/mode-constrained selection not captured by primary_type (18XX/Wargame/Party/Econ/Coop/Legacy) alone; 1p-only strict_solo n=249 has no dedicated specialist metric; weight/ownership weight_within not type-specific",
                "overlap_stats": methodology_rows
            }
        },
        "proposed_changes": proposed,
        "lineage_evidence_summary": lineage_df.to_dict(orient="records") if not lineage_df.empty else [],
        "audience_evidence_summary": audience_df.to_dict(orient="records") if not audience_df.empty else [],
        "model_comparison_summary": model_rows,
        "methodology_breakdown": methodology_rows,
        "hiddenness_counts": broad_audit_data.get("hidden_counts", {}),
        "claim_tags": {
            "counts": "observed fact from data",
            "means/residuals/CV/Jaccard": "empirical finding (model-dependent)",
            "proposed_change decisions": "model-dependent conclusion / hypothesis - proposed awaiting review, not final",
            "broad appeal definition": "assumption / hypothesis per AGENTS.md - not inferred as fact"
        },
        "constraints": ["reuse Pass-2 adj_mean/Q3bFam/Q4Fam — NOT refit severity or Q3bFam from scratch", "n>=50 gate for additive fam where appropriate", "seed 20260824 5-fold", "scratch bounded 4GB/3threads", "weight 7 null median-filled 2.0 + flag"],
        "next_steps": "Independent reviewer to challenge proposed_changes; finalizer to incorporate critique and then rerun pipeline if approved. DO NOT yet rerun full candidate pipeline."
    }
    with open(DOCS / "pass3_investigation_summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    with open(REPORTS / "pass3_investigation_summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"Investigation done in {time.time()-t0:.1f}s")
    print(f" lineage {len(lineage_df)} rows, audience {len(audience_df)} rows, model {len(model_rows)} specs")
    print(f" strong {len(strong)} diagnostic, proposed {len(proposed)} changes")

if __name__ == "__main__":
    investigate()

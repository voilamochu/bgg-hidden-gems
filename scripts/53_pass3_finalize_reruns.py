#!/usr/bin/env python3
"""Pass 3 Finalize — reruns to resolve reviewer disagreements (per-pattern edition, base-title completeness, solo/duel heterogeneity, propensity calibration proxy).

Constraints: bounded 4GB/3threads, scratch/ducktmp, seed 20260824, 5-fold paired as 9B, narrow aggregations, handle 7 weight-null median fill.
Population canonical reuse: 14,698 × 287,302 × 24,146,307 data/processed/phase2-pass2/ (mu 7.139, adj_mean + Q3bFam 48f + Q4Fam from 9B/10).

Outputs: docs/phase2-pass2/pass3_final/ + reports/phase2_pass2/pass3_final/
 - per_pattern_edition.csv (per-pattern n, mean resid, share top5, beta/SE, 5-fold, CV delta, Spearman/Jaccard, gates)
 - base_title_completeness.csv + base_title_summary.json
 - audience_heterogeneity.csv (solo_first/duel/wargame_duel vs Euro 2p vs all, mean resid, CV, Jaccard, gates)
 - incorporated_review_evidence.json (for incorporated_review.md)

Mirrors to reports/.

Run: .venv/bin/python scripts/53_pass3_finalize_reruns.py
"""
import importlib.util
import json
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
SEED = 20260824
N_FOLDS = 5
DOCS = REPO / "docs/phase2-pass2/pass3_final"
REPORTS = REPO / "reports/phase2_pass2/pass3_final"

_spec = importlib.util.spec_from_file_location("m48", REPO / "scripts/48_step9_expected_quality_underratedness.py")
m48 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m48)

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
    cat_cols, cat_counts = m48.add_group_flags(est, "categories", "cat", 500)
    band_cols = m48.add_dummies(est, "vol_band", "volband")
    knots_year = np.quantile(est["year"].to_numpy(float), [0.05, 0.35, 0.65, 0.95])
    nsy = m48.ns_basis(est["year"].to_numpy(float), knots_year)
    ns_year_cols=[]
    for i in range(nsy.shape[1]):
        c=f"ns_year_{i}"
        est[c]=nsy[:,i]
        ns_year_cols.append(c)
    core_struct=["weight_c","log_playtime_c","min_players_c","log_max_players_c","is_reimpl_num","log_n_impl_c"]
    # families/mechanics parsed
    est["family_list"]=est["families"].map(lambda v: json.loads(v) if isinstance(v,str) else [])
    est["category_list"]=est["categories"].map(lambda v: json.loads(v) if isinstance(v,str) else [])
    est["mechanic_list"]=est["mechanics"].map(lambda v: json.loads(v) if isinstance(v,str) else [])
    est["fam_18XX"]=est["family_list"].map(lambda v: float("Series: 18xx" in v))
    est["fam_Cooperative Game"]=est["mechanic_list"].map(lambda v: float("Cooperative Game" in v))
    est["fam_Legacy Game"]=est["mechanic_list"].map(lambda v: float("Legacy Game" in v))
    q3b_base = band_cols + ns_year_cols + core_struct + cat_cols
    q3bFam_cols = q3b_base + ["fam_18XX","fam_Cooperative Game","fam_Legacy Game"]
    y=est["adj_mean"].to_numpy(float)
    n=len(y)
    X=np.column_stack([np.ones(n)]+[est[c].to_numpy(float) for c in q3bFam_cols])
    col_names=["intercept"]+q3bFam_cols
    beta,pred,resid = m48.fit_wls(X,y,np.ones(n))
    cv_pred,cv_resid,fold_betas,fold_idx = m48.cv_predictions(X,y,np.ones(n))
    # baseline CV
    fold_stats=[m48.metrics(y[ix], cv_resid[ix]) for ix in fold_idx]
    cv_r2_base=float(np.mean([f["r2"] for f in fold_stats]))
    cv_rmse_base=float(np.mean([f["rmse"] for f in fold_stats]))
    return dict(est=est, y=y, X=X, col_names=col_names, beta=beta, pred=pred, resid=resid, cv_resid=cv_resid, fold_idx=fold_idx, cat_cols=cat_cols, band_cols=band_cols, ns_year_cols=ns_year_cols, core_struct=core_struct, q3bFam_cols=q3bFam_cols, cv_r2_base=cv_r2_base, cv_rmse_base=cv_rmse_base)

def cv_for_flag(X_base, y, w, flag_vals):
    X_ext = np.column_stack([X_base, flag_vals[:,None]])
    beta_f, pred_f, resid_f = m48.fit_wls(X_ext, y, w)
    cv_pred, cv_resid, fold_betas, fold_idx = m48.cv_predictions(X_ext, y, w)
    fold_stats=[m48.metrics(y[ix], cv_resid[ix]) for ix in fold_idx]
    cv_r2=float(np.mean([f["r2"] for f in fold_stats]))
    cv_rmse=float(np.mean([f["rmse"] for f in fold_stats]))
    j=X_ext.shape[1]-1
    beta_j=float(beta_f[j])
    se_j=float(ols_se(X_ext, resid_f)[j])
    fold_betas_flag=fold_betas[:,j]
    # spearman/jaccard vs baseline resid
    # need baseline resid
    beta0,pred0,resid0 = m48.fit_wls(X_base, y, w)
    spear=float(pd.Series(resid0).corr(pd.Series(resid_f), method="spearman"))
    jac1=m48.top_jaccard(resid0, resid_f, 0.01)
    jac5=m48.top_jaccard(resid0, resid_f, 0.05)
    return beta_j, se_j, fold_betas_flag, cv_r2, cv_rmse, spear, jac1, jac5, resid0, resid_f

def main():
    t0=time.time()
    DOCS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    baseline=build_baseline()
    est=baseline["est"]
    y=baseline["y"]
    X_base=baseline["X"]
    resid_Q3bFam=baseline["resid"]
    cv_r2_base=baseline["cv_r2_base"]
    cv_rmse_base=baseline["cv_rmse_base"]
    n=len(y)
    ones=np.ones(n)
    # Screening evidence for outcome counts
    se_path=REPO/"docs/phase2-pass2/step11-12_hidden_gem_screen/screening_evidence_table.csv"
    se=pd.read_csv(se_path, low_memory=False) if se_path.exists() else pd.DataFrame()
    strong_ids=set(se[se["outcome_category"]=="strong_hidden_gem_evidence"]["game_id"].tolist()) if not se.empty else set()
    plausible_ids=set(se[se["outcome_category"]=="plausible_hidden_gem"]["game_id"].tolist()) if not se.empty else set()
    niche_ids=set(se[se["outcome_category"]=="niche_but_high_quality"]["game_id"].tolist()) if not se.empty else set()
    insufficient_ids=set(se[se["outcome_category"]=="insufficient_evidence"]["game_id"].tolist()) if not se.empty else set()

    # === 1. Per-pattern edition rerun (broad test, not just 39) ===
    # Patterns proposed: Collector's Edition, Ultimate Edition, Kickstarter Edition, Complete Collector, Essential Edition
    # plus additional for completeness: Big Box, Deluxe, Anniversary, Premium, Heritage, Revised, Second Edition
    pattern_defs = [
        ("Collecto", "Collector", 50),  # use substring Collector covers Collector's Edition and Complete Collector? But keep separate
        ("Collector's Edition", "Collector's Edition", 50),
        ("Ultimate Edition", "Ultimate", 50),
        ("Kickstarter Edition", "Kickstarter", 50),
        ("Complete Collector", "Complete Collector", 50),
        ("Essential Edition", "Essential", 50),
        ("Big Box", "Big Box", 50),
        ("Deluxe Edition", "Deluxe", 50),
        ("Anniversary", "Anniversary", 50),
        ("Premium", "Premium", 50),
        ("Heritage", "Heritage", 50),
        ("Revised", "Revised", 50),
        ("Second Edition", "Second Edition", 50),
        ("Edition (any)", "Edition", 50),  # aggregate 501 for reference
    ]
    # Actually use substring matching case-insensitive
    rows=[]
    for label, pat, gate in pattern_defs:
        # Use title contains pat case-insensitive
        flag_vals = est["title"].astype(str).str.contains(pat, case=False, na=False).astype(float).to_numpy()
        # For "Collector's Edition" keep exact but use pat as above
        n1=int(flag_vals.sum())
        if n1==0:
            mean_resid=float('nan')
            median_resid=float('nan')
            sd_resid=float('nan')
            share_top5=float('nan')
            beta=float('nan')
            se=float('nan')
            fold_betas_str=""
            fold_pos=0
            cv_r2=float('nan')
            delta=float('nan')
            spear=float('nan')
            jac1=float('nan')
            jac5=float('nan')
            passes=False
        else:
            mask=flag_vals==1
            mean_resid=float(resid_Q3bFam[mask].mean())
            median_resid=float(np.median(resid_Q3bFam[mask]))
            sd_resid=float(resid_Q3bFam[mask].std(ddof=1)) if n1>1 else float('nan')
            share_top5=float((resid_Q3bFam[mask] >= np.quantile(resid_Q3bFam,0.95)).mean()*100)
            # outcome overlaps
            est_ids=set(est.loc[mask,"game_id"].tolist())
            overlap_strong=len(strong_ids & est_ids)
            overlap_plausible=len(plausible_ids & est_ids)
            overlap_niche=len(niche_ids & est_ids)
            overlap_insufficient=len(insufficient_ids & est_ids)
            # CV if passes gate
            if n1>=gate:
                beta, se, fold_betas, cv_r2, cv_rmse, spear, jac1, jac5, _, _ = cv_for_flag(X_base, y, ones, flag_vals)
                delta=float(cv_r2 - cv_r2_base)
                fold_betas_str=" ".join(f"{v:+.3f}" for v in fold_betas)
                fold_pos=int((fold_betas>0).sum())
                passes=n1>=gate and (fold_pos in (0,5)) and not np.isnan(beta)
            else:
                beta=float('nan'); se=float('nan'); fold_betas_str=""; fold_pos=0; cv_r2=float('nan'); delta=float('nan'); spear=float('nan'); jac1=float('nan'); jac5=float('nan')
                passes=False
            # For rows with n<50 still record gate false
            passes_gate=n1>=50
            # Determine if meets systematic threshold >=0.10 and 5/5 and delta>=0.0005
            systematic=abs(mean_resid)>=0.10 if not np.isnan(mean_resid) else False
            fold_consistent=fold_pos in (0,5) if n1>=gate else False
            cv_pass=delta>=0.0005 if not np.isnan(delta) else False
            would_keep=passes_gate and systematic and fold_consistent and cv_pass
            rows.append(dict(
                pattern_label=label,
                pattern_substring=pat,
                n_games=n1,
                pct_pop=round(100*n1/n,2),
                mean_resid_Q3bFam=round(mean_resid,4) if not np.isnan(mean_resid) else None,
                median_resid_Q3bFam=round(median_resid,4) if not np.isnan(median_resid) else None,
                sd_resid_Q3bFam=round(sd_resid,4) if not np.isnan(sd_resid) else None,
                share_top5_pct=round(share_top5,1) if not np.isnan(share_top5) else None,
                overlap_strong_n=overlap_strong,
                overlap_plausible_n=overlap_plausible,
                overlap_niche_n=overlap_niche,
                overlap_insufficient_n=overlap_insufficient,
                passes_n50_gate=passes_gate,
                beta_added=round(beta,4) if not np.isnan(beta) else None,
                ols_se=round(se,4) if not np.isnan(se) else None,
                fold_betas=fold_betas_str,
                fold_pos_5=fold_pos if not np.isnan(beta) else None,
                cv_r2_ext=round(cv_r2,4) if not np.isnan(cv_r2) else None,
                delta_cv_r2=round(delta,4) if not np.isnan(delta) else None,
                spearman_vs_Q3bFam=round(spear,4) if not np.isnan(spear) else None,
                jaccard_top1_vs_Q3bFam=round(jac1,3) if not np.isnan(jac1) else None,
                jaccard_top5_vs_Q3bFam=round(jac5,3) if not np.isnan(jac5) else None,
                systematic_ge010=systematic,
                fold_consistent_5_of_5=fold_consistent,
                cv_gain_ge0005=cv_pass,
                would_keep_per_criterion=would_keep
            ))
            continue
        # handle zero case
        rows.append(dict(
            pattern_label=label,
            pattern_substring=pat,
            n_games=n1,
            pct_pop=round(100*n1/n,2) if n>0 else None,
            mean_resid_Q3bFam=None,
            median_resid_Q3bFam=None,
            sd_resid_Q3bFam=None,
            share_top5_pct=None,
            overlap_strong_n=0,
            overlap_plausible_n=0,
            overlap_niche_n=0,
            overlap_insufficient_n=0,
            passes_n50_gate=n1>=50,
            beta_added=None,
            ols_se=None,
            fold_betas="",
            fold_pos_5=None,
            cv_r2_ext=None,
            delta_cv_r2=None,
            spearman_vs_Q3bFam=None,
            jaccard_top1_vs_Q3bFam=None,
            jaccard_top5_vs_Q3bFam=None,
            systematic_ge010=False,
            fold_consistent_5_of_5=False,
            cv_gain_ge0005=False,
            would_keep_per_criterion=False
        ))
    df_pat=pd.DataFrame(rows)
    df_pat.to_csv(DOCS/"per_pattern_edition.csv", index=False)
    df_pat.to_csv(REPORTS/"per_pattern_edition.csv", index=False)

    # === 2. Base-title completeness test (game-level, no 24M scan) ===
    def base_title_func(t):
        return re.sub(r"(?i)\s*\(?((edition|anniversary|deluxe|premium|heritage|big box|collector|ultimate|essential|revised|second edition).*)$", "", t).strip().lower()
    est["base_title"]=est["title"].astype(str).map(base_title_func)
    est["resid_Q3bFam"]=resid_Q3bFam
    # count base titles with >=2 games
    vc=est["base_title"].value_counts()
    n_dup_titles=int((vc>=2).sum())
    n_dup_games=int(vc[vc>=2].sum())
    # For each dup group, check if any pair passes designer/year/weight corroboration (shared designer >=1, year diff <=5, weight diff <=0.3)
    # Also check family overlap via Game: or Series: or links version/reimpl? Simplified: designer+year+weight
    est["designer_list"]=est["designers"].map(lambda v: json.loads(v) if isinstance(v,str) else [])
    # Build candidate duplicate groups
    candidate_groups=[]
    for bt, cnt in vc[vc>=2].items():
        sub=est[est["base_title"]==bt]
        # Need at least 2 games; check pairwise
        # For simplicity, check if any pair shares designer and within thresholds
        has_candidate=False
        ids=sub["game_id"].tolist()
        years=sub["year"].to_numpy(float)
        weights=sub["weight"].to_numpy(float)
        designers=sub["designer_list"].tolist()
        for i in range(len(sub)):
            for j in range(i+1, len(sub)):
                # designer overlap
                overlap=False
                try:
                    overlap=len(set(designers[i]) & set(designers[j]))>0
                except:
                    overlap=False
                # year diff
                ydiff=abs(years[i]-years[j]) if not np.isnan(years[i]) and not np.isnan(years[j]) else 999
                wdiff=abs(weights[i]-weights[j]) if not np.isnan(weights[i]) and not np.isnan(weights[j]) else 999
                if overlap and ydiff<=5 and wdiff<=0.3:
                    has_candidate=True
                    break
            if has_candidate:
                break
        if has_candidate:
            candidate_groups.append(bt)
    n_candidate_dup_titles=len(candidate_groups)
    n_candidate_dup_games=int(est[est["base_title"].isin(candidate_groups)].shape[0])
    # Check how many of those are already in pruned_lists (if available) or already flagged as duplicate in Pass2?
    # pruned_lists paths
    pruned_primary=REPO/"docs/phase2-second-pass/pruned_lists/combined_primary_edition_family.csv"
    pruned_sens=REPO/"docs/phase2-second-pass/pruned_lists/combined_sensitivity_dup.csv"
    pruned_ids=set()
    if pruned_primary.exists():
        pruned_ids.update(pd.read_csv(pruned_primary)["game_id"].tolist())
    if pruned_sens.exists():
        pruned_ids.update(pd.read_csv(pruned_sens)["game_id"].tolist())
    n_pruned_in_est=int(est[est["game_id"].isin(pruned_ids)].shape[0])
    # How many candidate dup games are not pruned?
    candidate_not_pruned=est[(est["base_title"].isin(candidate_groups)) & (~est["game_id"].isin(pruned_ids))]
    n_candidate_not_pruned=int(candidate_not_pruned.shape[0])
    # Also check screening pool 532
    pool_path=REPO/"docs/phase2-pass2/step10_quality_underratedness_gates/screening_pool.csv"
    pool=pd.read_csv(pool_path) if pool_path.exists() else pd.DataFrame()
    n_pool_dup_titles=0
    n_pool_dup_games=0
    n_pool_candidate=0
    if not pool.empty:
        pool["base_title"]=pool["title"].astype(str).map(base_title_func)
        vc_pool=pool["base_title"].value_counts()
        n_pool_dup_titles=int((vc_pool>=2).sum())
        n_pool_dup_games=int(vc_pool[vc_pool>=2].sum())
        # candidate in pool
        pool_candidate=pool[pool["base_title"].isin(candidate_groups)]
        n_pool_candidate=int(pool_candidate.shape[0])
        # overlap with strong
        strong_pool_overlap=len(set(pool_candidate["game_id"].tolist()) & strong_ids) if strong_ids else 0
    else:
        strong_pool_overlap=0
    # Residual for candidate vs pruned
    resid_candidate=float(resid_Q3bFam[est["base_title"].isin(candidate_groups)].mean()) if n_candidate_dup_games>0 else float('nan')
    resid_pruned=float(resid_Q3bFam[est["game_id"].isin(pruned_ids)].mean()) if n_pruned_in_est>0 else float('nan')
    resid_not_pruned=float(candidate_not_pruned["resid_Q3bFam"].mean()) if n_candidate_not_pruned>0 and "resid_Q3bFam" in candidate_not_pruned.columns else float('nan')
    base_summary=dict(
        population_dup_base_titles_ge2=n_dup_titles,
        population_dup_games=n_dup_games,
        candidate_corroborated_titles=n_candidate_dup_titles,
        candidate_corroborated_games=n_candidate_dup_games,
        pruned_ids_total=len(pruned_ids),
        pruned_in_est=n_pruned_in_est,
        candidate_not_pruned_games=n_candidate_not_pruned,
        pool_dup_titles=n_pool_dup_titles,
        pool_dup_games=n_pool_dup_games,
        pool_candidate_games=n_pool_candidate,
        pool_candidate_strong_overlap=strong_pool_overlap,
        mean_resid_candidate_corroborated=round(resid_candidate,4) if not np.isnan(resid_candidate) else None,
        mean_resid_pruned=round(resid_pruned,4) if not np.isnan(resid_pruned) else None,
        n_version_truncated_at_100=11,
        families_null=0,
        game_links_capped_note="n_version capped at 100 for 11 games (Catan etc), log_n_impl censored"
    )
    with open(DOCS/"base_title_completeness.json","w") as f:
        json.dump(base_summary,f,indent=2)
    with open(REPORTS/"base_title_completeness.json","w") as f:
        json.dump(base_summary,f,indent=2)
    # CSV per base-title group
    rows_bt=[]
    for bt in candidate_groups[:50]:  # top 50 for file brevity, full 285 not needed
        sub=est[est["base_title"]==bt]
        for _,r in sub.iterrows():
            rows_bt.append(dict(base_title=bt, game_id=r["game_id"], title=r["title"], year=r["year"], weight=r["weight"], resid_Q3bFam=round(float(r["resid_Q3bFam"]),4) if "resid_Q3bFam" in sub.columns else round(float(resid_Q3bFam[est["game_id"]==r["game_id"]].mean()),4) if len(resid_Q3bFam[est["game_id"]==r["game_id"]])>0 else None, in_pruned=r["game_id"] in pruned_ids))
    pd.DataFrame(rows_bt).to_csv(DOCS/"base_title_completeness.csv", index=False)
    pd.DataFrame(rows_bt).to_csv(REPORTS/"base_title_completeness.csv", index=False)

    # === 3. Audience heterogeneity (solo_first/duel/wargame_duel vs Euro) + CV ===
    # Define flags
    est["flag_solo_first"]=((est["min_players"]==1)&(est["max_players"]<=2)).astype(float)
    est["flag_duel"]=(est["max_players"]<=2).astype(float)
    est["flag_wargame"]=(est["category_list"].map(lambda v: "Wargame" in v)).astype(float)
    est["flag_wargame_duel"]=((est["flag_wargame"]==1)&(est["flag_duel"]==1)).astype(float)
    est["flag_euro_duel"]=((est["flag_duel"]==1)&(est["flag_wargame"]==0)&(est["flag_solo_first"]==0)).astype(float)
    # Strict solo, etc.
    flags_to_test=[
        ("solo_first", "flag_solo_first", "min1 max<=2 n=691"),
        ("duel_1_2p", "flag_duel", "max<=2 n=2555"),
        ("wargame_duel", "flag_wargame_duel", "Wargame & max<=2 n=1153"),
        ("euro_duel", "flag_euro_duel", "duel Euro not wargame not solo_first n~1079"),
        ("strict_solo", None, "1p==1 max==1 n=249"),  # special
        ("solo_mech", None, "Solo mech n=1397"),
    ]
    # recompute strict_solo etc directly
    est["flag_strict_solo"]=((est["min_players"]==1)&(est["max_players"]==1)).astype(float)
    est["flag_solo_mech"]=(est["mechanic_list"].map(lambda v: "Solo / Solitaire Game" in v)).astype(float)
    hetero_rows=[]
    for label, col, desc in flags_to_test:
        if col is None:
            if label=="strict_solo":
                col="flag_strict_solo"
            elif label=="solo_mech":
                col="flag_solo_mech"
            else:
                continue
        vals=est[col].to_numpy(float)
        n1=int((vals==1).sum())
        mask=vals==1
        mean_resid=float(resid_Q3bFam[mask].mean()) if n1>0 else float('nan')
        median_resid=float(np.median(resid_Q3bFam[mask])) if n1>0 else float('nan')
        share_top5=float((resid_Q3bFam[mask] >= np.quantile(resid_Q3bFam,0.95)).mean()*100) if n1>0 else float('nan')
        # outcome overlaps
        est_ids=set(est.loc[mask,"game_id"].tolist()) if n1>0 else set()
        overlap_strong=len(strong_ids & est_ids) if strong_ids else 0
        overlap_plausible=len(plausible_ids & est_ids) if plausible_ids else 0
        overlap_niche=len(niche_ids & est_ids) if niche_ids else 0
        overlap_insufficient=len(insufficient_ids & est_ids) if insufficient_ids else 0
        # CV
        if n1>=50:
            beta,se,fold_betas,cv_r2,cv_rmse,spear,jac1,jac5,_,_=cv_for_flag(X_base,y,ones,vals)
            delta=float(cv_r2 - cv_r2_base)
            fold_str=" ".join(f"{v:+.3f}" for v in fold_betas)
            fold_pos=int((fold_betas>0).sum())
        else:
            beta=float('nan'); se=float('nan'); fold_str=""; fold_pos=0; cv_r2=float('nan'); delta=float('nan'); spear=float('nan'); jac1=float('nan'); jac5=float('nan')
        hetero_rows.append(dict(
            candidate_id=label,
            flag_column=col,
            description=desc,
            n_games=n1,
            pct_pop=round(100*n1/n,2) if n>0 else None,
            mean_resid_Q3bFam=round(mean_resid,4) if not np.isnan(mean_resid) else None,
            median_resid_Q3bFam=round(median_resid,4) if not np.isnan(median_resid) else None,
            share_top5_pct=round(share_top5,1) if not np.isnan(share_top5) else None,
            overlap_strong_n=overlap_strong,
            overlap_strong_pct=round(100*overlap_strong/39,1) if 39>0 else None,
            overlap_plausible_n=overlap_plausible,
            overlap_niche_n=overlap_niche,
            overlap_insufficient_n=overlap_insufficient,
            passes_n50_gate=n1>=50,
            beta_added=round(beta,4) if not np.isnan(beta) else None,
            ols_se=round(se,4) if not np.isnan(se) else None,
            fold_betas=fold_str,
            fold_pos_5=fold_pos if not np.isnan(beta) else None,
            cv_r2_ext=round(cv_r2,4) if not np.isnan(cv_r2) else None,
            delta_cv_r2=round(delta,4) if not np.isnan(delta) else None,
            spearman_vs_Q3bFam=round(spear,4) if not np.isnan(spear) else None,
            jaccard_top1_vs_Q3bFam=round(jac1,3) if not np.isnan(jac1) else None,
            jaccard_top5_vs_Q3bFam=round(jac5,3) if not np.isnan(jac5) else None,
            is_solo_first_subset=(label in ["solo_first","strict_solo"]),
            is_duel_subset=(label in ["duel_1_2p","wargame_duel","euro_duel"]),
            notes="heterogeneity: duel contains solo_first "+str(int(est["flag_solo_first"].sum()))+" + wargame_duel "+str(int(est["flag_wargame_duel"].sum()))+" + euro "+str(int(est["flag_euro_duel"].sum())) if label=="duel_1_2p" else ""
        ))
    df_het=pd.DataFrame(hetero_rows)
    df_het.to_csv(DOCS/"audience_heterogeneity.csv", index=False)
    df_het.to_csv(REPORTS/"audience_heterogeneity.csv", index=False)

    # === 4. Propensity calibration proxy (using existing Step7C validation) ===
    # Load propensity validation if exists
    prop_path=REPO/"docs/phase2-pass2/step7c_exposure_propensity_validation/propensity_validation_game_level.csv"
    prop=pd.read_csv(prop_path, low_memory=False) if prop_path.exists() else pd.DataFrame()
    sel_path=REPO/"docs/phase2-pass2/step7_audience_selection/audience_selectivity_game_level.csv"
    sel=pd.read_csv(sel_path, low_memory=False) if sel_path.exists() else pd.DataFrame()
    ca_path=REPO/"docs/phase2-pass2/step7_audience_selection/cross_audience_results.csv"
    ca=pd.read_csv(ca_path, low_memory=False) if ca_path.exists() else pd.DataFrame()
    # Join flags to prop/sel/ca for solo_first/duel
    # Merge flags from est
    flag_cols=["flag_solo_first","flag_duel","flag_wargame_duel","flag_euro_duel","flag_solo_mech"]
    avail=[c for c in flag_cols if c in est.columns]
    prop_est=prop.merge(est[["game_id"]+avail], on="game_id", how="inner") if not prop.empty else pd.DataFrame()
    sel_est=sel.merge(est[["game_id"]+avail], on="game_id", how="inner") if not sel.empty else pd.DataFrame()
    ca_est=ca.merge(est[["game_id"]+avail], on="game_id", how="inner") if not ca.empty else pd.DataFrame()
    # For each subgroup compute overlap / taxonomy / cross stats
    rows_prop=[]
    for label, flag_col in [("overall", None), ("solo_first", "flag_solo_first"), ("duel_1_2p", "flag_duel"), ("wargame_duel", "flag_wargame_duel"), ("euro_duel", "flag_euro_duel"), ("solo_mech", "flag_solo_mech")]:
        if flag_col is None:
            sub_prop=prop
            sub_sel=sel
            sub_ca=ca
            n_sub=int(est.shape[0])
        else:
            sub_prop=prop_est[prop_est[flag_col]==1] if (not prop_est.empty and flag_col in prop_est.columns) else pd.DataFrame()
            sub_sel=sel_est[sel_est[flag_col]==1] if (not sel_est.empty and flag_col in sel_est.columns) else pd.DataFrame()
            sub_ca=ca_est[ca_est[flag_col]==1] if (not ca_est.empty and flag_col in ca_est.columns) else pd.DataFrame()
            n_sub=int((est[flag_col]==1).sum()) if flag_col in est.columns else 0
        if sub_prop.empty:
            overlap_counts={}
            sens_counts={}
        else:
            overlap_counts=sub_prop["overlap_status"].value_counts().to_dict() if "overlap_status" in sub_prop.columns else {}
            sens_counts=sub_prop["sensitivity_class"].value_counts().to_dict() if "sensitivity_class" in sub_prop.columns else {}
        total_prop=len(sub_prop) if not sub_prop.empty else 0
        if sub_ca.empty:
            ca_total=0
            ca_support=0
        else:
            ca_total=len(sub_ca)
            ca_support=int((sub_ca["supported_ge10"]==True).sum()) if "supported_ge10" in sub_ca.columns else 0
        if sub_sel.empty:
            tax_counts={}
        else:
            tax_counts=sub_sel["taxonomy"].value_counts().to_dict() if "taxonomy" in sub_sel.columns else {}
        rows_prop.append(dict(
            subgroup=label,
            n_games=n_sub,
            prop_insufficient_overlap_pct=round(100*overlap_counts.get("insufficient_overlap",0)/max(1,total_prop),1) if total_prop>0 else None,
            prop_borderline_pct=round(100*overlap_counts.get("borderline_overlap",0)/max(1,total_prop),1) if total_prop>0 else None,
            prop_adequate_pct=round(100*overlap_counts.get("adequate_overlap",0)/max(1,total_prop),1) if total_prop>0 else None,
            sensitive_strongly_pct=round(100*sens_counts.get("strongly_sensitive",0)/max(1,total_prop),1) if total_prop>0 else None,
            sensitive_stable_pct=round(100*sens_counts.get("stable_under_exposure_adjustment",0)/max(1,total_prop),1) if total_prop>0 else None,
            cross_support_ge10_pct=round(100*ca_support/max(1,ca_total),1) if ca_total>0 else None,
            taxonomy_high_pct=round(100*tax_counts.get("high_audience_selectivity",0)/max(1,len(sub_sel)),1) if not sub_sel.empty else None,
            taxonomy_insufficient_pct=round(100*tax_counts.get("insufficient_evidence",0)/max(1,len(sub_sel)),1) if not sub_sel.empty else None,
            insufficient_overlap_n=int(overlap_counts.get("insufficient_overlap",0)) if overlap_counts else 0,
            n_prop_total=total_prop,
            n_sel_total=len(sub_sel) if not sub_sel.empty else 0,
            n_ca_total=ca_total
        ))
    df_prop=pd.DataFrame(rows_prop)
    df_prop.to_csv(DOCS/"propensity_calibration_proxy.csv", index=False)
    df_prop.to_csv(REPORTS/"propensity_calibration_proxy.csv", index=False)

    # === Evidence JSON for incorporated_review ===
    evidence=dict(
        generated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        seed=SEED,
        population=dict(pass2_games=14698, pass2_users=287302, pass2_obs=24146307, mu=7.139, cv_r2_base=cv_r2_base, cv_rmse_base=cv_rmse_base),
        diagnostic=dict(strong=39, plausible=176, niche=163, insufficient=127),
        per_pattern_edition=df_pat.to_dict(orient="records"),
        base_title_completeness=base_summary,
        audience_heterogeneity=df_het.to_dict(orient="records"),
        propensity_proxy=df_prop.to_dict(orient="records"),
        note="Reruns use same 5-fold paired CV seed 20260824, narrow game-level OLS, 4GB/3threads bounded, no 24M wide sorts"
    )
    with open(DOCS/"incorporated_review_evidence.json","w") as f:
        json.dump(evidence,f,indent=2, default=str)
    with open(REPORTS/"incorporated_review_evidence.json","w") as f:
        json.dump(evidence,f,indent=2, default=str)
    print(f"Done reruns in {time.time()-t0:.1f}s: per_pattern {len(df_pat)} rows, base-title {n_dup_titles} dup titles, hetero {len(df_het)} rows")
if __name__=="__main__":
    main()

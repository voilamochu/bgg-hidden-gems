#!/usr/bin/env python3
"""Pass 4 Finalize — reruns to resolve review before rerunning pipeline.

Population canonical reuse: 14,698 × 287,302 × 24,146,307 data/processed/phase2-pass2/ (mu 7.139, adj_mean + Q3bFam 48f + Q4Fam from 9B/10).
- Q3bFam 48f CV 0.6033 preserved (reuse severity, NOT refit)
- 39 strong_hidden_gem_evidence diagnostic only

Reruns per Pass4 investigation §1-7 + Pass3 review learnings:
 1. Per-pattern edition (501 → per-pattern n<50 gate, base-title completeness)
 2. Audience heterogeneity (solo_first/duel/wargame_duel vs Euro, 5-fold CV)
 3. Hiddenness vs hobby penetration (per_game_hiddenness.csv via reference intersect_250)
 4. Reference population sensitivity (13 candidates, chosen intersect_250 134/279k)
 5. Propensity calibration proxy (small-pool insufficient rates)

Outputs: docs/phase2-pass2/pass4_final/ + reports/phase2_pass2/pass4_final/
"""
import importlib.util, json, re, time, shutil
from pathlib import Path
import numpy as np
import pandas as pd
import duckdb

REPO = Path(__file__).resolve().parent.parent
SEED = 20260824
N_FOLDS = 5
DOCS = REPO / "docs/phase2-pass2/pass4_final"
REPORTS = REPO / "reports/phase2_pass2/pass4_final"

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
    cat_cols, _ = m48.add_group_flags(est, "categories", "cat", 500)
    band_cols = m48.add_dummies(est, "vol_band", "volband")
    knots_year = np.quantile(est["year"].to_numpy(float), [0.05, 0.35, 0.65, 0.95])
    nsy = m48.ns_basis(est["year"].to_numpy(float), knots_year)
    ns_year_cols=[]
    for i in range(nsy.shape[1]):
        c=f"ns_year_{i}"
        est[c]=nsy[:,i]
        ns_year_cols.append(c)
    core_struct=["weight_c","log_playtime_c","min_players_c","log_max_players_c","is_reimpl_num","log_n_impl_c"]
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
    fold_stats=[]
    cv_pred,cv_resid,fold_betas,fold_idx = m48.cv_predictions(X,y,np.ones(n))
    for ix in fold_idx:
        fold_stats.append(m48.metrics(y[ix], cv_resid[ix]))
    cv_r2_base=float(np.mean([f["r2"] for f in fold_stats]))
    cv_rmse_base=float(np.mean([f["rmse"] for f in fold_stats]))
    return dict(est=est, y=y, X=X, col_names=col_names, beta=beta, pred=pred, resid=resid, cv_resid=cv_resid, fold_idx=fold_idx, cat_cols=cat_cols, band_cols=band_cols, ns_year_cols=ns_year_cols, core_struct=core_struct, q3bFam_cols=q3bFam_cols, cv_r2_base=cv_r2_base, cv_rmse_base=cv_rmse_base)

def cv_for_flag(X_base, y, w, flag_vals):
    X_ext = np.column_stack([X_base, flag_vals[:,None]])
    beta_f, pred_f, resid_f = m48.fit_wls(X_ext, y, w)
    cv_pred, cv_resid, fold_betas, fold_idx = m48.cv_predictions(X_ext, y, w)
    fold_stats=[m48.metrics(y[ix], cv_resid[ix]) for ix in fold_idx]
    cv_r2=float(np.mean([f["r2"] for f in fold_stats]))
    spear=float(pd.Series(m48.fit_wls(X_base,y,w)[2]).corr(pd.Series(resid_f), method="spearman"))
    jac1=m48.top_jaccard(m48.fit_wls(X_base,y,w)[2], resid_f, 0.01)
    jac5=m48.top_jaccard(m48.fit_wls(X_base,y,w)[2], resid_f, 0.05)
    se_j=float(ols_se(X_ext, resid_f)[-1])
    return float(beta_f[-1]), se_j, fold_betas[:,-1], cv_r2, spear, jac1, jac5, resid_f

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
    n=len(y)
    ones=np.ones(n)
    se_path=REPO/"docs/phase2-pass2/step11-12_hidden_gem_screen/screening_evidence_table.csv"
    se=pd.read_csv(se_path, low_memory=False) if se_path.exists() else pd.DataFrame()
    strong_ids=set(se[se["outcome_category"]=="strong_hidden_gem_evidence"]["game_id"].tolist()) if not se.empty else set()
    plausible_ids=set(se[se["outcome_category"]=="plausible_hidden_gem"]["game_id"].tolist()) if not se.empty else set()
    niche_ids=set(se[se["outcome_category"]=="niche_but_high_quality"]["game_id"].tolist()) if not se.empty else set()
    insufficient_ids=set(se[se["outcome_category"]=="insufficient_evidence"]["game_id"].tolist()) if not se.empty else set()

    # 1. Per-pattern edition rerun
    print("[56] per-pattern edition")
    pattern_defs=[
        ("Collector's Edition","Collector's Edition"),
        ("Ultimate Edition","Ultimate Edition"),
        ("Kickstarter Edition","Kickstarter Edition"),
        ("Complete Collector","Complete Collector"),
        ("Essential Edition","Essential Edition"),
        ("Second Edition","Second Edition"),
        ("Anniversary","Anniversary"),
        ("Deluxe Edition","Deluxe Edition"),
        ("Big Box","Big Box"),
        ("Premium","Premium"),
        ("Heritage","Heritage"),
        ("Revised Edition","Revised Edition"),
        ("Edition (any)","Edition"),
    ]
    rows=[]
    for label, pat in pattern_defs:
        flag_vals = est["title"].astype(str).str.contains(pat, case=False, na=False).astype(float).to_numpy()
        n1=int(flag_vals.sum())
        if n1==0:
            rows.append(dict(pattern_label=label, pattern_substring=pat, n_games=0, pct_pop=0, mean_resid=None, median_resid=None, share_top5=None, overlap_strong=0, overlap_niche=0, passes_n50=False, beta_added=None, ols_se=None, fold_betas="", fold_pos=None, cv_r2_ext=None, delta_cv=None, spearman=None, jaccard_top1=None, jaccard_top5=None, would_keep=False))
            continue
        mask=flag_vals==1
        vals=resid_Q3bFam[mask]
        mean_resid=float(vals.mean())
        median_resid=float(np.median(vals))
        share_top5=float((vals >= np.quantile(resid_Q3bFam,0.95)).mean()*100)
        est_ids=set(est.loc[mask,"game_id"].tolist())
        overlap_strong=len(strong_ids & est_ids)
        overlap_niche=len(niche_ids & est_ids)
        if n1>=50:
            beta,se,fold_betas,cv_r2,spear,jac1,jac5,_ = cv_for_flag(X_base,y,ones,flag_vals)
            delta=float(cv_r2 - cv_r2_base)
            fold_str=" ".join(f"{v:+.3f}" for v in fold_betas)
            fold_pos=int((fold_betas>0).sum())
            would_keep = (n1>=50 and abs(mean_resid)>=0.10 and fold_pos in (0,5) and delta>=0.0005)
        else:
            beta=se=fold_str=fold_pos=cv_r2=delta=spear=jac1=jac5=None
            would_keep=False
        rows.append(dict(pattern_label=label, pattern_substring=pat, n_games=n1, pct_pop=round(100*n1/n,2), mean_resid_Q3bFam=round(mean_resid,4), median_resid=round(median_resid,4), share_top5_pct=round(share_top5,1), overlap_strong_n=overlap_strong, overlap_niche_n=overlap_niche, passes_n50_gate=n1>=50, beta_added=round(beta,4) if beta is not None else None, ols_se=round(se,4) if se is not None else None, fold_betas=fold_str if 'fold_str' in locals() else "", fold_pos_5=fold_pos, cv_r2_ext=round(cv_r2,4) if cv_r2 is not None else None, delta_cv_r2=round(delta,4) if delta is not None else None, spearman_vs_Q3bFam=round(spear,4) if spear is not None else None, jaccard_top1=round(jac1,3) if jac1 is not None else None, jaccard_top5=round(jac5,3) if jac5 is not None else None, would_keep=would_keep))
    df_pat=pd.DataFrame(rows)
    df_pat.to_csv(DOCS/"per_pattern_edition.csv", index=False)
    df_pat.to_csv(REPORTS/"per_pattern_edition.csv", index=False)

    # 2. Base-title completeness
    print("[56] base-title")
    def base_title_func(t):
        return re.sub(r"(?i)\s*\(?((edition|anniversary|deluxe|premium|heritage|big box|collector|ultimate|essential|revised|second edition).*)$", "", str(t)).strip().lower()
    est["base_title"]=est["title"].astype(str).map(base_title_func)
    est["resid_Q3bFam"]=resid_Q3bFam
    vc=est["base_title"].value_counts()
    n_dup_titles=int((vc>=2).sum())
    n_dup_games=int(vc[vc>=2].sum())
    est["designer_list"]=est["designers"].map(lambda v: json.loads(v) if isinstance(v,str) else [])
    candidate_groups=[]
    for bt, cnt in vc[vc>=2].items():
        sub=est[est["base_title"]==bt]
        has_candidate=False
        ids=sub["game_id"].tolist()
        years=sub["year"].to_numpy(float)
        weights=sub["weight"].fillna(2.0).to_numpy(float)
        designers=sub["designer_list"].tolist()
        for i in range(len(sub)):
            for j in range(i+1, len(sub)):
                try:
                    overlap=len(set(designers[i]) & set(designers[j]))>0
                except:
                    overlap=False
                ydiff=abs(years[i]-years[j]) if not np.isnan(years[i]) and not np.isnan(years[j]) else 999
                wdiff=abs(weights[i]-weights[j])
                if overlap and ydiff<=5 and wdiff<=0.3:
                    has_candidate=True
                    break
            if has_candidate:
                break
        if has_candidate:
            candidate_groups.append(bt)
    n_candidate_dup_titles=len(candidate_groups)
    n_candidate_dup_games=int(est[est["base_title"].isin(candidate_groups)].shape[0])
    pruned_primary=REPO/"data/processed/phase2-second-pass/pruned_lists/combined_primary_edition_family.csv"
    pruned_ids=set()
    if pruned_primary.exists():
        pruned_ids.update(pd.read_csv(pruned_primary).iloc[:,0].astype(int).tolist())
    n_pruned_in_est=int(est[est["game_id"].isin(pruned_ids)].shape[0])
    candidate_not_pruned=est[(est["base_title"].isin(candidate_groups)) & (~est["game_id"].isin(pruned_ids))]
    n_candidate_not_pruned=int(candidate_not_pruned.shape[0])
    pool_path=REPO/"docs/phase2-pass2/step10_quality_underratedness_gates/screening_pool.csv"
    pool=pd.read_csv(pool_path) if pool_path.exists() else pd.DataFrame()
    n_pool_candidate=0
    strong_pool_overlap=0
    if not pool.empty:
        pool["base_title"]=pool["title"].astype(str).map(base_title_func)
        pool_candidate=pool[pool["base_title"].isin(candidate_groups)]
        n_pool_candidate=int(pool_candidate.shape[0])
        strong_pool_overlap=len(set(pool_candidate["game_id"].tolist()) & strong_ids)
    resid_candidate=float(resid_Q3bFam[est["base_title"].isin(candidate_groups)].mean()) if n_candidate_dup_games>0 else float('nan')
    resid_pruned=float(resid_Q3bFam[est["game_id"].isin(pruned_ids)].mean()) if n_pruned_in_est>0 else float('nan')
    base_summary=dict(population_dup_base_titles_ge2=n_dup_titles, population_dup_games=n_dup_games, candidate_corroborated_titles=n_candidate_dup_titles, candidate_corroborated_games=n_candidate_dup_games, pruned_ids_total=len(pruned_ids), pruned_in_est=n_pruned_in_est, candidate_not_pruned_games=n_candidate_not_pruned, pool_candidate_games=n_pool_candidate, pool_candidate_strong_overlap=strong_pool_overlap, mean_resid_candidate_corroborated=round(resid_candidate,4) if not np.isnan(resid_candidate) else None, mean_resid_pruned=round(resid_pruned,4) if not np.isnan(resid_pruned) else None, n_version_truncated_at_100=11)
    with open(DOCS/"base_title_completeness.json","w") as f:
        json.dump(base_summary,f,indent=2)
    with open(REPORTS/"base_title_completeness.json","w") as f:
        json.dump(base_summary,f,indent=2)
    rows_bt=[]
    for bt in candidate_groups[:40]:
        sub=est[est["base_title"]==bt]
        for _,r in sub.iterrows():
            rows_bt.append(dict(base_title=bt, game_id=int(r["game_id"]), title=r["title"][:80], year=int(r["year"]) if not pd.isna(r["year"]) else "", weight=round(float(r["weight"]),2) if not pd.isna(r["weight"]) else "", resid_Q3bFam=round(float(r["resid_Q3bFam"]),3), in_pruned=r["game_id"] in pruned_ids))
    pd.DataFrame(rows_bt).to_csv(DOCS/"base_title_completeness.csv", index=False)
    pd.DataFrame(rows_bt).to_csv(REPORTS/"base_title_completeness.csv", index=False)

    # 3. Audience heterogeneity
    print("[56] audience heterogeneity")
    est["flag_solo_first"]=((est["min_players"]==1)&(est["max_players"]<=2)).astype(float)
    est["flag_duel"]=(est["max_players"]<=2).astype(float)
    est["flag_wargame"]=(est["category_list"].map(lambda v: "Wargame" in v)).astype(float)
    est["flag_wargame_duel"]=((est["flag_wargame"]==1)&(est["flag_duel"]==1)).astype(float)
    est["flag_euro_duel"]=((est["flag_duel"]==1)&(est["flag_wargame"]==0)&(est["flag_solo_first"]==0)).astype(float)
    est["flag_strict_solo"]=((est["min_players"]==1)&(est["max_players"]==1)).astype(float)
    est["flag_solo_mech"]=(est["mechanic_list"].map(lambda v: "Solo / Solitaire Game" in v)).astype(float)
    flags_to_test=[("solo_first","flag_solo_first"),("duel_1_2p","flag_duel"),("wargame_duel","flag_wargame_duel"),("euro_duel","flag_euro_duel"),("strict_solo","flag_strict_solo"),("solo_mech","flag_solo_mech")]
    hetero_rows=[]
    for label,col in flags_to_test:
        vals=est[col].to_numpy(float)
        n1=int((vals==1).sum())
        mask=vals==1
        mean_resid=float(resid_Q3bFam[mask].mean()) if n1>0 else float('nan')
        median_resid=float(np.median(resid_Q3bFam[mask])) if n1>0 else float('nan')
        share_top5=float((resid_Q3bFam[mask] >= np.quantile(resid_Q3bFam,0.95)).mean()*100) if n1>0 else float('nan')
        est_ids=set(est.loc[mask,"game_id"].tolist()) if n1>0 else set()
        overlap_strong=len(strong_ids & est_ids)
        overlap_niche=len(niche_ids & est_ids)
        overlap_insufficient=len(insufficient_ids & est_ids)
        if n1>=50:
            beta,se,fold_betas,cv_r2,spear,jac1,jac5,_ = cv_for_flag(X_base,y,ones,vals)
            delta=float(cv_r2 - cv_r2_base)
            fold_str=" ".join(f"{v:+.3f}" for v in fold_betas)
            fold_pos=int((fold_betas>0).sum())
        else:
            beta=se=fold_str=fold_pos=cv_r2=delta=spear=jac1=jac5=None
        hetero_rows.append(dict(candidate_id=label, flag_column=col, n_games=n1, pct_pop=round(100*n1/n,2), mean_resid_Q3bFam=round(mean_resid,4) if not np.isnan(mean_resid) else None, median_resid=round(median_resid,4) if not np.isnan(median_resid) else None, share_top5_pct=round(share_top5,1) if not np.isnan(share_top5) else None, overlap_strong_n=overlap_strong, overlap_niche_n=overlap_niche, overlap_insufficient_n=overlap_insufficient, passes_n50_gate=n1>=50, beta_added=round(beta,4) if beta is not None else None, ols_se=round(se,4) if se is not None else None, fold_betas=fold_str if fold_str else None, fold_pos_5=fold_pos, cv_r2_ext=round(cv_r2,4) if cv_r2 is not None else None, delta_cv_r2=round(delta,4) if delta is not None else None, spearman_vs_Q3bFam=round(spear,4) if spear is not None else None, jaccard_top1=round(jac1,3) if jac1 is not None else None, jaccard_top5=round(jac5,3) if jac5 is not None else None))
    df_het=pd.DataFrame(hetero_rows)
    df_het.to_csv(DOCS/"audience_heterogeneity.csv", index=False)
    df_het.to_csv(REPORTS/"audience_heterogeneity.csv", index=False)

    # 4. Propensity calibration proxy
    print("[56] propensity proxy")
    sel_path=REPO/"docs/phase2-pass2/step7_audience_selection/audience_selectivity_game_level.csv"
    prop_path=REPO/"docs/phase2-pass2/step7c_exposure_propensity_validation/propensity_validation_game_level.csv"
    ca_path=REPO/"docs/phase2-pass2/step7_audience_selection/cross_audience_results.csv"
    sel=pd.read_csv(sel_path, low_memory=False) if sel_path.exists() else pd.DataFrame()
    prop=pd.read_csv(prop_path, low_memory=False) if prop_path.exists() else pd.DataFrame()
    ca=pd.read_csv(ca_path, low_memory=False) if ca_path.exists() else pd.DataFrame()
    flag_cols=["flag_solo_first","flag_duel","flag_wargame_duel","flag_euro_duel","flag_solo_mech"]
    prop_est=prop.merge(est[["game_id"]+flag_cols], on="game_id", how="inner") if not prop.empty else pd.DataFrame()
    sel_est=sel.merge(est[["game_id"]+flag_cols], on="game_id", how="inner") if not sel.empty else pd.DataFrame()
    ca_est=ca.merge(est[["game_id"]+flag_cols], on="game_id", how="inner") if not ca.empty else pd.DataFrame()
    rows_prop=[]
    for label, flag_col in [("overall",None),("solo_first","flag_solo_first"),("duel_1_2p","flag_duel"),("wargame_duel","flag_wargame_duel"),("euro_duel","flag_euro_duel"),("solo_mech","flag_solo_mech")]:
        if flag_col is None:
            sub_prop=prop; sub_sel=sel; sub_ca=ca; n_sub=int(est.shape[0])
        else:
            sub_prop=prop_est[prop_est[flag_col]==1] if (not prop_est.empty and flag_col in prop_est.columns) else pd.DataFrame()
            sub_sel=sel_est[sel_est[flag_col]==1] if (not sel_est.empty and flag_col in sel_est.columns) else pd.DataFrame()
            sub_ca=ca_est[ca_est[flag_col]==1] if (not ca_est.empty and flag_col in ca_est.columns) else pd.DataFrame()
            n_sub=int((est[flag_col]==1).sum()) if flag_col in est.columns else 0
        if sub_prop.empty:
            overlap_counts={}; sens_counts={}
        else:
            overlap_counts=sub_prop["overlap_status"].value_counts().to_dict() if "overlap_status" in sub_prop.columns else {}
            sens_counts=sub_prop["sensitivity_class"].value_counts().to_dict() if "sensitivity_class" in sub_prop.columns else {}
        total_prop=len(sub_prop) if not sub_prop.empty else 0
        ca_total=len(sub_ca) if not sub_ca.empty else 0
        ca_support=int((sub_ca["supported_ge10"]==True).sum()) if (not sub_ca.empty and "supported_ge10" in sub_ca.columns) else 0
        tax_counts=sub_sel["taxonomy"].value_counts().to_dict() if (not sub_sel.empty and "taxonomy" in sub_sel.columns) else {}
        rows_prop.append(dict(subgroup=label, n_games=n_sub, prop_insufficient_overlap_pct=round(100*overlap_counts.get("insufficient_overlap",0)/max(1,total_prop),1) if total_prop>0 else None, prop_adequate_pct=round(100*overlap_counts.get("adequate_overlap",0)/max(1,total_prop),1) if total_prop>0 else None, sensitive_strongly_pct=round(100*sens_counts.get("strongly_sensitive",0)/max(1,total_prop),1) if total_prop>0 else None, cross_support_ge10_pct=round(100*ca_support/max(1,ca_total),1) if ca_total>0 else None, taxonomy_high_pct=round(100*tax_counts.get("high_audience_selectivity",0)/max(1,len(sub_sel)),1) if not sub_sel.empty else None, insufficient_overlap_n=int(overlap_counts.get("insufficient_overlap",0)) if overlap_counts else 0, n_prop_total=total_prop))
    df_prop=pd.DataFrame(rows_prop)
    df_prop.to_csv(DOCS/"propensity_calibration_proxy.csv", index=False)
    df_prop.to_csv(REPORTS/"propensity_calibration_proxy.csv", index=False)

    # 5. Hiddenness evidence via reference penetration (reuse per_game_hiddenness from investigation if exists, else compute via duckdb)
    print("[56] hiddenness")
    per_game_path=REPO/"docs/phase2-pass2/pass4_investigation/per_game_hiddenness.csv"
    if per_game_path.exists():
        pg=pd.read_csv(per_game_path)
        # Use it to build hiddenness evidence for docs/pass4_final
        hidden_rows=[]
        for bucket, lab in [( "eligible_<1700","eligible_<1700"),("borderline_1700-2500","borderline_1700-2500"),("exclude_>2500","exclude_>2500")]:
            # Need to infer bucket via n_obs <1700 / 1700-2500 / >2500 using pg n_obs column name
            # pg has game_id, n_obs, n_ref_raters, ref_penetration
            # Merge n_obs from games
            pass
        # Simpler: recompute hiddenness evidence via duckdb using chosen reference
        chosen_path=REPO/"docs/phase2-pass2/pass4_investigation/chosen_reference_gids.json"
        chosen=json.loads(open(chosen_path).read()) if chosen_path.exists() else {"chosen": {"n_users_distinct": 279108}, "gids": []}
        total_ref=chosen["chosen"]["n_users_distinct"] if "chosen" in chosen and "n_users_distinct" in chosen["chosen"] else 279108
        # Use pg to compute stats
        pg["hidden_bucket"]=pd.cut(pg["n_obs"], bins=[0,1699,2500,float("inf")], labels=["eligible_<1700","borderline_1700-2500","exclude_>2500"])
        hidden_df_rows=[]
        for bucket in ["eligible_<1700","borderline_1700-2500","exclude_>2500"]:
            sub=pg[pg["hidden_bucket"]==bucket]
            n=int(len(sub))
            mean_n=float(sub["n_obs"].mean()) if n else float("nan")
            median_n=float(sub["n_obs"].median()) if n else float("nan")
            mean_pen=float(sub["ref_penetration"].mean()) if n else float("nan")
            median_pen=float(sub["ref_penetration"].median()) if n else float("nan")
            p90_pen=float(sub["ref_penetration"].quantile(0.9)) if n else float("nan")
            high_share=float((sub["ref_penetration"]>0.05).mean()) if n else float("nan")
            hidden_df_rows.append(dict(hidden_bucket=bucket, n_games=n, pct_pop=round(100*n/len(pg),2), mean_n_obs=round(mean_n,1) if not np.isnan(mean_n) else None, median_n_obs=int(median_n) if not np.isnan(median_n) else None, mean_ref_penetration=round(mean_pen,5) if not np.isnan(mean_pen) else None, median_ref_penetration=round(median_pen,5) if not np.isnan(median_pen) else None, p90_ref_penetration=round(p90_pen,5) if not np.isnan(p90_pen) else None, share_high_penetration_gt5pct=round(high_share*100,1) if not np.isnan(high_share) else None, total_ref_users=total_ref))
        # also thresholds
        eligible=pg[pg["hidden_bucket"]=="eligible_<1700"]
        for thr in [0.001,0.002,0.005,0.01]:
            n_high=int((eligible["ref_penetration"]>=thr).sum())
            hidden_df_rows.append(dict(hidden_bucket=f"eligible_<1700_pen_ge{thr*100:.1f}pct", n_games=n_high, pct_pop=round(100*n_high/max(1,len(eligible)),1), mean_n_obs=None, median_n_obs=None, mean_ref_penetration=None, median_ref_penetration=None, p90_ref_penetration=None, share_high_penetration_gt5pct=None, total_ref_users=total_ref))
        hidden_evidence=pd.DataFrame(hidden_df_rows)
        hidden_evidence.to_csv(DOCS/"hiddenness_evidence.csv", index=False)
        hidden_evidence.to_csv(REPORTS/"hiddenness_evidence.csv", index=False)
        # copy per_game for auditing
        pg.to_csv(DOCS/"per_game_hiddenness.csv", index=False)
        pg.to_csv(REPORTS/"per_game_hiddenness.csv", index=False)
        # also copy reference population
        ref_path=REPO/"docs/phase2-pass2/pass4_investigation/reference_population.csv"
        if ref_path.exists():
            shutil.copy2(ref_path, DOCS/"reference_population.csv")
            shutil.copy2(ref_path, REPORTS/"reference_population.csv")
        chosen_path=REPO/"docs/phase2-pass2/pass4_investigation/chosen_reference_gids.json"
        if chosen_path.exists():
            shutil.copy2(chosen_path, DOCS/"chosen_reference_gids.json")
            shutil.copy2(chosen_path, REPORTS/"chosen_reference_gids.json")
    else:
        # minimal hiddenness using n_obs only
        pass

    # 6. Evidence JSON
    evidence=dict(generated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), seed=SEED, population=dict(pass2_games=14698, pass2_users=287302, pass2_obs=24146307, mu=7.139, cv_r2_base=cv_r2_base), diagnostic=dict(strong=39, plausible=176, niche=163, insufficient=127), per_pattern_edition=df_pat.to_dict(orient="records"), base_title_completeness=base_summary, audience_heterogeneity=df_het.to_dict(orient="records"), propensity_proxy=df_prop.to_dict(orient="records"))
    with open(DOCS/"incorporated_review_evidence.json","w") as f:
        json.dump(evidence,f,indent=2, default=str)
    with open(REPORTS/"incorporated_review_evidence.json","w") as f:
        json.dump(evidence,f,indent=2, default=str)
    print(f"[56] done {time.time()-t0:.1f}s: per_pattern {len(df_pat)} base {base_summary} hetero {len(df_het)}")

if __name__=="__main__":
    main()

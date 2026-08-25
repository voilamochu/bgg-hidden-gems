#!/usr/bin/env python3
"""Pass 4 Investigation — full end-to-end redesign and rerun preparation.

Population (canonical, reuse): 14,698 × 287,302 × 24,146,307 obs, data/processed/phase2-pass2/
mu 7.139, user_severity_pass2 + game_adjusted_means_pass2 via scripts 39/40 — reuse, NOT refit.
Q3bFam primary 48f CV 0.6033 + Q4Fam 78f CV 0.6151 from 9B/10, hiddenness <1700/1700-2500/>2500 from 11-12,
and 39 strong from 722d149/bf1e7e9 as diagnostic only.

This script is investigation only, produces proposed methodology and evidence that generalizes,
leaving full 532→ rerun for finalizer. Bounded 4GB/3threads, scratch/ducktmp, seed 20260824.

Outputs: docs/phase2-pass2/pass4_investigation/* + reports mirror
"""
import importlib.util, json, re, time, pathlib, shutil
from pathlib import Path
import numpy as np
import pandas as pd
import duckdb

REPO = Path(__file__).resolve().parent.parent
SEED = 20260824
N_FOLDS = 5
TAG_MIN_COUNT = 500
DOCS = REPO / "docs/phase2-pass2/pass4_investigation"
REPORTS = REPO / "reports/phase2_pass2/pass4_investigation"

# Reuse Step 9 helpers
_spec = importlib.util.spec_from_file_location("m48", REPO / "scripts/48_step9_expected_quality_underratedness.py")
m48 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m48)

def parse_list(v):
    try:
        p = json.loads(v) if isinstance(v, str) else []
        return [str(x) for x in p] if isinstance(p, list) else []
    except: return []

def ols_se(X,resid):
    n,p = X.shape
    s2 = float(resid @ resid) / (n-p)
    d = np.diag(np.linalg.pinv(X.T @ X))
    return np.sqrt(np.maximum(s2*d,0.0))

def cv_for_spec(X,y,w):
    beta,pred,resid = m48.fit_wls(X,y,w)
    cv_pred,cv_resid,fold_betas,fold_idx = m48.cv_predictions(X,y,w)
    m_in = m48.metrics(y,resid)
    fold_stats=[m48.metrics(y[ix],cv_resid[ix]) for ix in fold_idx]
    cv_r2=float(np.mean([f["r2"] for f in fold_stats]))
    cv_rmse=float(np.mean([f["rmse"] for f in fold_stats]))
    return beta,pred,resid,cv_resid,fold_betas,fold_idx,m_in,fold_stats,cv_r2,cv_rmse

def ensure_dirs():
    DOCS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPO/"reports/phase2_pass2").mkdir(parents=True, exist_ok=True)

def build_baseline():
    pass2=REPO/"data/processed/phase2-pass2"
    gam=pd.read_parquet(pass2/"game_adjusted_means_pass2.parquet")
    games=pd.read_parquet(pass2/"games_pass2.parquet")
    est=m48.build_estimation_sample(gam,games,pass2/"game_tags_pass2.parquet",pass2/"game_links_pass2.parquet")
    cat_cols, cat_counts=m48.add_group_flags(est,"category_list","cat",TAG_MIN_COUNT)
    mech_cols, mech_counts=m48.add_group_flags(est,"mechanic_list","mech",TAG_MIN_COUNT)
    band_cols=m48.add_dummies(est,"vol_band","volband")
    knots_year=np.quantile(est["year"].to_numpy(float),[0.05,0.35,0.65,0.95])
    nsy=m48.ns_basis(est["year"].to_numpy(float),knots_year)
    ns_year_cols=[]
    for i in range(nsy.shape[1]):
        c=f"ns_year_{i}"
        est[c]=nsy[:,i]
        ns_year_cols.append(c)
    core_struct=["weight_c","log_playtime_c","min_players_c","log_max_players_c","is_reimpl_num","log_n_impl_c"]
    est["family_list"]=est["families"].map(parse_list) if "families" in est.columns else [[]]*len(est)
    est["fam_18XX"]=est["family_list"].map(lambda v: float("Series: 18xx" in v))
    est["fam_Cooperative Game"]=est["mechanic_list"].map(lambda v: float("Cooperative Game" in v))
    est["fam_Legacy Game"]=est["mechanic_list"].map(lambda v: float("Legacy Game" in v))
    q3b_base=band_cols+ns_year_cols+core_struct+cat_cols
    new_vs_q3b=["fam_18XX","fam_Cooperative Game","fam_Legacy Game"]
    q3bFam_cols=q3b_base+new_vs_q3b
    y=est["adj_mean"].to_numpy(float)
    n=len(y)
    cols=q3bFam_cols
    X=np.column_stack([np.ones(n)]+[est[c].to_numpy(float) for c in cols])
    col_names=["intercept"]+cols
    ones_w=np.ones(n)
    beta,pred,resid=m48.fit_wls(X,y,ones_w)
    cv_pred,cv_resid,fold_betas,fold_idx=m48.cv_predictions(X,y,ones_w)
    return {"est":est,"cat_cols":cat_cols,"mech_cols":mech_cols,"band_cols":band_cols,"ns_year_cols":ns_year_cols,"core_struct":core_struct,"knots_year":knots_year,"y":y,"X":X,"col_names":col_names,"beta":beta,"pred":pred,"resid":resid,"cv_resid":cv_resid,"fold_betas":fold_betas,"fold_idx":fold_idx,"ones_w":ones_w}

def main():
    t0=time.time()
    ensure_dirs()
    print("Building baseline Q3bFam...")
    base=build_baseline()
    est=base["est"].copy()
    y=base["y"]
    resid_q3bFam=base["resid"]
    pred_q3bFam=base["pred"]
    col_names=base["col_names"]
    X_base=base["X"]
    ones_w=base["ones_w"]
    n=len(y)
    # also need Q3b without fam for comparison diagnostics (for 18XX etc)
    # Load auxiliary
    pass2=REPO/"data/processed/phase2-pass2"
    games=pd.read_parquet(pass2/"games_pass2.parquet")
    gt=pd.read_parquet(pass2/"game_tags_pass2.parquet")
    gl=pd.read_parquet(pass2/"game_links_pass2.parquet")
    # Pruned lists
    pruned_primary=set()
    for p in [REPO/"data/processed/phase2-second-pass/pruned_lists/combined_primary_edition_family.csv", REPO/"data/processed/phase2-second-pass/pruned_lists/combined_sensitivity_dup.csv"]:
        if p.exists():
            df=pd.read_csv(p)
            # first column may be game_id without header?
            col=df.columns[0]
            pruned_primary.update(df[col].astype(int).tolist())
    # For gap check, we need primary only 169 but keep combined for counting
    pruned_169=set()
    p169=REPO/"data/processed/phase2-second-pass/pruned_lists/combined_primary_edition_family.csv"
    if p169.exists():
        df=pd.read_csv(p169)
        pruned_169.update(df[df.columns[0]].astype(int).tolist())

    # Screening evidence for 39 diagnostic
    se_path=REPO/"docs/phase2-pass2/step11-12_hidden_gem_screen/screening_evidence_table.csv"
    if se_path.exists():
        se=pd.read_csv(se_path, low_memory=False)
        strong=se[se["outcome_category"]=="strong_hidden_gem_evidence"]
        plausible=se[se["outcome_category"]=="plausible_hidden_gem"]
        niche=se[se["outcome_category"]=="niche_but_high_quality"]
        insufficient=se[se["outcome_category"]=="insufficient_evidence"]
    else:
        strong=plausible=niche=insufficient=pd.DataFrame()
    # Load Step7 files
    sel_path=REPO/"docs/phase2-pass2/step7_audience_selection/audience_selectivity_game_level.csv"
    sel=pd.read_csv(sel_path, low_memory=False) if sel_path.exists() else pd.DataFrame()
    prop_path=REPO/"docs/phase2-pass2/step7c_exposure_propensity_validation/propensity_validation_game_level.csv"
    prop=pd.read_csv(prop_path, low_memory=False) if prop_path.exists() else pd.DataFrame()
    ca_path=REPO/"docs/phase2-pass2/step7_audience_selection/cross_audience_results.csv"
    ca=pd.read_csv(ca_path, low_memory=False) if ca_path.exists() else pd.DataFrame()
    # Merge audience metrics into est for structure analysis
    # sel has game_id, taxonomy, spec shares, tvd, deviation_count etc.
    if not sel.empty:
        keep_cols=[c for c in ["game_id","taxonomy","spec_primary_share_ge10","spec_primary_share_ge20","tvd_volume_global","tvd_volume_type","share_own","herfindahl_volume","penetration"] if c in sel.columns]
        # penetration may be in prop, not sel
        est = est.merge(sel[keep_cols], on="game_id", how="left")
    if not prop.empty:
        # Use true scale overlap_status and ess_ratio etc.
        keepp=[c for c in ["game_id","overlap_status","sensitivity_class","ess_ratio","max_weight","penetration","penetration_type_ge20"] if c in prop.columns]
        est = est.merge(prop[keepp], on="game_id", how="left", suffixes=("","_prop"))

    # For cross support, compute per game has_broad vs has_niche_drop etc? We'll approximate via ca
    # ca has per split rows, need to summarize per game n_supported_ge10 etc. For simplicity, use sel's n_splits_tested etc if available, else compute from ca
    # Prepare cross support summary
    cross_summary=pd.DataFrame()
    if not ca.empty:
        # For each game, count supported_ge10 splits and is_significant niche_drop
        # is_significant True means diff significant and |diff|>=0.3 ; we'll treat niche_drop as any specialist or weight split significant with positive diff
        # For now compute per game: n_supported_ge10 = sum(supported_ge10), n_niche_drop = sum(is_significant & diff_adj>0.3)
        # Need diff_adj column
        if "diff_adj" in ca.columns:
            ca["is_niche_drop"] = ca["is_significant"] & (ca["diff_adj"].abs()>=0.3) & (ca["diff_adj"]>0)
            grp=ca.groupby("game_id").agg(
                n_supported_ge10=("supported_ge10","sum"),
                n_niche_drop=("is_niche_drop","sum"),
                n_tests=("game_id","size")
            ).reset_index()
            grp["has_broad"] = (grp["n_supported_ge10"]>0) & (grp["n_niche_drop"]==0)
            # Also has_niche_drop True if any
            grp["has_niche_drop"] = grp["n_niche_drop"]>0
            est = est.merge(grp[["game_id","n_supported_ge10","has_broad","has_niche_drop"]], on="game_id", how="left")

    # ============================================================
    # §1 Entity / lineage eligibility — richest relationships + description
    # ============================================================
    print("§1 lineage...")
    # Description in this dump is short tagline (<=85 chars) — not rich, but we use what exists plus title/families/links
    # Note: BGG sqlite description is same short; full description not available in current extracts. We'll document that.
    # Define lineage flags using richest available: title pattern, families, game_links rel counts, categories/mechanics
    edition_pat = re.compile(r"(?i)(edition|anniversary|deluxe|premium|heritage|big box|collector|ultimate|essential|revised|second edition)")
    # Use est title for flag (est has title)
    est["flag_edition_title"] = est["title"].astype(str).str.contains(edition_pat, na=False).astype(float)
    # Split edition patterns per reviewer request
    patterns = {
        "collectors": re.compile(r"(?i)collector'?s?\s*edition"),
        "ultimate": re.compile(r"(?i)ultimate\s*edition"),
        "kickstarter": re.compile(r"(?i)kickstarter\s*edition"),
        "complete_collector": re.compile(r"(?i)complete\s*collector"),
        "essential": re.compile(r"(?i)essential\s*edition"),
        "second_edition": re.compile(r"(?i)second\s*edition"),
        "anniversary": re.compile(r"(?i)anniversary"),
        "deluxe": re.compile(r"(?i)deluxe"),
        "premium": re.compile(r"(?i)premium"),
        "heritage": re.compile(r"(?i)heritage"),
        "big_box": re.compile(r"(?i)big\s*box"),
    }
    for k, pat in patterns.items():
        est[f"flag_ed_{k}"] = est["title"].astype(str).str.contains(pat, na=False).astype(float)

    # Version/expansion/reimpl counts
    n_version = gl[gl["rel"]=="version"].groupby("game_id").size().rename("n_version")
    n_exp = gl[gl["rel"]=="expansion"].groupby("game_id").size().rename("n_exp")
    n_reimpl = gl[gl["rel"].isin(["reimplementation","reimplements"])].groupby("game_id").size().rename("n_reimpl")
    n_cardset = gl[gl["rel"]=="cardset"].groupby("game_id").size().rename("n_cardset")
    n_integration = gl[gl["rel"]=="integration"].groupby("game_id").size().rename("n_integration")
    # Merge counts
    for cnt in [n_version, n_exp, n_reimpl, n_cardset, n_integration]:
        est = est.merge(cnt, left_on="game_id", right_index=True, how="left")
    for col in ["n_version","n_exp","n_reimpl","n_cardset","n_integration"]:
        est[col]=est[col].fillna(0)

    # Families parsing for system, promotional etc.
    # est already has family_list
    est["flag_game_system"] = est["family_list"].map(lambda v: float("Admin: Game System Entries" in v))
    est["flag_expansion_family"] = est["family_list"].map(lambda v: float(any("Expansion" in s for s in v)))
    est["flag_promo"] = est["family_list"].map(lambda v: float(any(s.startswith("Promotional:") for s in v)))
    est["flag_accessory"] = est["family_list"].map(lambda v: float(any("Accessory" in s for s in v)))
    # Also check is_expansion flag from games (should be zero in pass2 because filtered, but check)
    # Use game_links expansion as proxy for being expanded game not expansion itself
    # Series / Game families
    est["flag_series_any"] = est["family_list"].map(lambda v: float(any(s.startswith("Series:") and s!="Series: 18xx" for s in v)))
    est["flag_game_family"] = est["family_list"].map(lambda v: float(any(s.startswith("Game:") for s in v)))
    # Specific series
    est["flag_series_wallet"] = est["family_list"].map(lambda v: float("Series: Wallet & Box Micro Games (Button Shy)" in v))
    est["flag_series_unlock"] = est["family_list"].map(lambda v: float("Series: Unlock! (Space Cowboys)" in v))
    # Wargame category etc.
    # Check description keywords where useful — but description is short, still check
    est["desc_contains_expansion"] = est["description"].astype(str).str.contains("expansion", case=False, na=False).astype(float)
    est["desc_contains_requires"] = est["description"].astype(str).str.contains("requires", case=False, na=False).astype(float)
    est["desc_contains_standalone"] = est["description"].astype(str).str.contains("standalone", case=False, na=False).astype(float)

    # Base-title completeness test: strip edition regex and group
    def base_title(t):
        # lower, strip edition suffix heuristically
        # remove parenthetical edition etc
        s = re.sub(r"(?i)\s*\(?\s*(edition|anniversary|deluxe|premium|heritage|big box|collector|ultimate|essential|revised|second edition).*$", "", str(t)).strip()
        # also remove collector etc without edition word but preceding? Simplify
        s = re.sub(r"(?i)\s*:\s*.*(collector|ultimate|essential).*$", "", s).strip()
        return s.lower()
    est["base_title"] = est["title"].astype(str).map(base_title)
    # Group counts
    base_counts = est.groupby("base_title").size()
    dup_bases = base_counts[base_counts>=2].index.tolist()
    # For each base_title group size >=2, candidate duplicate if designer overlap + year diff <=5 + weight diff <=0.3
    # Need designers and weight, year
    # designers string list JSON
    def parse_designers(v):
        try:
            lst=json.loads(v) if isinstance(v,str) else []
            return set(str(x) for x in lst) if isinstance(lst, list) else set()
        except: return set()
    # est has designers?
    if "designers" in est.columns:
        est["designers_set"] = est["designers"].map(parse_designers)
    else:
        est["designers_set"] = [set()]*len(est)
    # Build dup candidate dataframe
    dup_rows=[]
    # Need to also have weight available; for null weight, use median 2.0
    est["weight_filled"] = est["weight"].fillna(2.0)
    # For efficiency, iterate over dup bases (285 as per task)
    for bt in dup_bases:
        sub = est[est["base_title"]==bt].sort_values("n_obs", ascending=False)
        if len(sub)<2: continue
        # pairwise check
        ids = sub["game_id"].tolist()
        titles = sub["title"].tolist()
        designers = sub["designers_set"].tolist()
        years = sub["year"].tolist()
        weights = sub["weight_filled"].tolist()
        families_list = sub["family_list"].tolist()
        for i in range(len(sub)):
            for j in range(i+1, len(sub)):
                # designer overlap? At least 1 shared
                d_overlap = len(designers[i] & designers[j])>0 if designers[i] and designers[j] else False
                year_diff = abs(years[i]-years[j]) if pd.notna(years[i]) and pd.notna(years[j]) else 999
                weight_diff = abs(weights[i]-weights[j])
                # family or link overlap? Simplified: same designer+year+weight corroboration
                corroborated = d_overlap and year_diff<=5 and weight_diff<=0.3
                # Also if families share Game: or Series: maybe not needed
                # Mark if not already pruned
                pair_ids = (ids[i], ids[j])
                already_pruned = (ids[i] in pruned_169) or (ids[j] in pruned_169)  # if either was pruned, group considered caught? Need both not caught to be gap
                # Actually need to check if grouping would have been pruned; simplified: if either id in pruned, then that id removed, so remaining not duplicate
                # For counting missed duplicates, count groups where neither id in pruned_169 but corroborated
                dup_rows.append({
                    "base_title": bt,
                    "game_id_a": ids[i], "title_a": titles[i], "year_a": years[i], "weight_a": weights[i],
                    "game_id_b": ids[j], "title_b": titles[j], "year_b": years[j], "weight_b": weights[j],
                    "designer_overlap": d_overlap,
                    "year_diff": year_diff,
                    "weight_diff": weight_diff,
                    "corroborated": corroborated,
                    "already_pruned_either": already_pruned,
                    "n_group": len(sub)
                })
    dup_df = pd.DataFrame(dup_rows)
    # Summaries
    n_dup_titles = len(dup_bases)
    n_dup_games = est[est["base_title"].isin(dup_bases)].shape[0]
    # Corroborated 39 etc as per task example
    if not dup_df.empty:
        corroborated_df = dup_df[dup_df["corroborated"]]
        n_corroborated_groups = corroborated_df["base_title"].nunique()
        n_corroborated_games = pd.concat([corroborated_df["game_id_a"], corroborated_df["game_id_b"]]).nunique()
        missed = corroborated_df[~corroborated_df["already_pruned_either"]]
        n_missed_groups = missed["base_title"].nunique() if not missed.empty else 0
        n_missed_games = pd.concat([missed["game_id_a"], missed["game_id_b"]]).nunique() if not missed.empty else 0
        # How many missed in pool / strong?
        pool_ids = set(se["game_id"].tolist()) if not se.empty else set()
        strong_ids = set(strong["game_id"].tolist()) if not strong.empty else set()
        missed_ids = set(pd.concat([missed["game_id_a"], missed["game_id_b"]]).tolist()) if not missed.empty else set()
        missed_in_pool = len(missed_ids & pool_ids)
        missed_in_strong = len(missed_ids & strong_ids)
    else:
        n_corroborated_groups=n_corroborated_games=n_missed_groups=n_missed_games=missed_in_pool=missed_in_strong=0
        corroborated_df=missed=pd.DataFrame()

    # Build lineage evidence CSV rows
    lineage_candidates=[
        ("edition_title_any", "flag_edition_title", "title contains edition/anniversary/deluxe/premium/heritage/big box/collector/ultimate/essential/revised/second edition (heuristic 501)", "title"),
        ("edition_collectors", "flag_ed_collectors", "Collector's Edition pattern", "title"),
        ("edition_ultimate", "flag_ed_ultimate", "Ultimate Edition pattern", "title"),
        ("edition_kickstarter", "flag_ed_kickstarter", "Kickstarter Edition pattern", "title"),
        ("edition_complete_collector", "flag_ed_complete_collector", "Complete Collector pattern", "title"),
        ("edition_essential", "flag_ed_essential", "Essential Edition pattern", "title"),
        ("edition_second_edition", "flag_ed_second_edition", "Second Edition pattern", "title"),
        ("edition_anniversary", "flag_ed_anniversary", "Anniversary pattern", "title"),
        ("edition_deluxe", "flag_ed_deluxe", "Deluxe pattern", "title"),
        ("high_version_ge10", "n_version", "n_version >=10", "game_links version"),
        ("any_version", "n_version", "n_version >=1", "game_links version"),
        ("multi_reimpl", "n_reimpl", "n_reimpl >1 (multiple reimplementations)", "game_links reimplementation"),
        ("game_system", "flag_game_system", "Admin: Game System Entries", "families"),
        ("expansion_family", "flag_expansion_family", "Expansion family", "families"),
        ("promo", "flag_promo", "Promotional family", "families"),
        ("series_any", "flag_series_any", "any Series: except 18xx", "families Series:"),
        ("game_family", "flag_game_family", "any Game: family (franchise)", "families Game:"),
        ("n_expansion_ge5", "n_exp", "n_expansion >=5", "game_links expansion"),
        ("cardset", "n_cardset", "n_cardset >=1 (card set entry)", "game_links cardset"),
        ("integration", "n_integration", "n_integration >=1", "game_links integration"),
        ("desc_expansion", "desc_contains_expansion", "description contains 'expansion'", "description"),
    ]
    lineage_rows=[]
    for cid, col, desc, src in lineage_candidates:
        if col not in est.columns:
            continue
        # Determine n based on threshold
        if col in ["n_version","n_exp","n_reimpl","n_cardset","n_integration"]:
            thresh = 10 if "ge10" in cid or cid=="high_version_ge10" else (5 if "ge5" in cid else 1)
            if cid=="n_expansion_ge5":
                thresh=5
            mask = est[col] >= thresh
        else:
            mask = est[col] >=0.5 if est[col].dtype!=object else est[col]==1
            # for flag columns, threshold 0.5
            if col.startswith("flag_ed_") or col.startswith("flag_"):
                mask = est[col]>=0.5
        n = int(mask.sum())
        if n==0:
            mean_resid=float("nan")
            median_resid=float("nan")
            sd_resid=float("nan")
            share_top5=float("nan")
            beta=se_beta=cv_delta=jaccard=float("nan")
            in_strong=0
            pruned_overlap=0
            added_coverage=0
        else:
            mean_resid=float(est.loc[mask,"resid_dummy"].mean()) if "resid_dummy" in est.columns else float(resid_q3bFam[mask].mean())
            # Actually resid_q3bFam aligned with est index; need to handle
            vals=resid_q3bFam[mask.values] if isinstance(mask, pd.Series) else resid_q3bFam[mask]
            mean_resid=float(vals.mean())
            median_resid=float(np.median(vals))
            sd_resid=float(vals.std(ddof=1)) if n>1 else float("nan")
            share_top5=float((vals >= np.quantile(resid_q3bFam,0.95)).mean())
            # Beta and CV: add flag to Q3bFam and compute one-by-one CV (reuse cv_for_spec)
            # Only if n>=50 and not already in Q3bFam to avoid duplicate
            beta=float("nan"); se_beta=float("nan"); cv_delta=float("nan"); jaccard=float("nan")
            folds_beta_str=""
            if n>=50:
                flag_arr=mask.astype(float).to_numpy()
                # Check if already in design? None of these are in Q3bFam except fam_18XX etc; so test
                X_test=np.column_stack([X_base, flag_arr])
                try:
                    b,p,r,cv_r,fb,fi,m_in,fs,cv_r2,cv_rmse = cv_for_spec(X_test,y,ones_w)
                    # beta is last coefficient
                    beta=float(b[-1])
                    # se via ols_se
                    se_arr=ols_se(X_test,r)
                    se_beta=float(se_arr[-1])
                    # CV delta vs base
                    _,_,_,_,_,_,m_base,_,cv_r2_base,_=cv_for_spec(X_base,y,ones_w)
                    cv_delta=float(cv_r2 - cv_r2_base)
                    # Jaccard top1% residual ranking vs baseline
                    # Need resid vs new resid
                    jaccard=float(m48.top_jaccard(resid_q3bFam, r, 0.01))
                    folds_beta=[float(fb[i,-1]) for i in range(N_FOLDS)]
                    folds_beta_str=" ".join(f"{v:+.3f}" for v in folds_beta)
                except Exception as e:
                    beta=float("nan")
            else:
                beta=float("nan")
            in_strong=int(strong["game_id"].isin(est.loc[mask,"game_id"]).sum()) if not strong.empty and n>0 else 0
            # pruned_lists gap: how many of these n would have been caught by pruned? For edition title, check pruned overlap
            pruned_overlap=int(est.loc[mask,"game_id"].isin(pruned_169).sum()) if n>0 else 0
            added_coverage=n - pruned_overlap
        # For lineage, effect if added to pruned: screening vs model; we will not add to model unless CV passes, but lineage is eligibility not model
        lineage_rows.append({
            "candidate": cid, "description": desc, "source": src, "n": n, "pct_pop": float(n/len(est)*100) if n else 0,
            "mean_resid_Q3bFam": mean_resid, "median_resid": median_resid, "sd_resid": sd_resid, "share_top5": share_top5,
            "beta_added": beta, "se_beta": se_beta, "cv_delta_R2": cv_delta, "jaccard_top1_vs_Q3bFam": jaccard,
            "folds_beta": folds_beta_str, "in_strong_39": in_strong, "pruned_already": pruned_overlap, "added_coverage_if_flagged": added_coverage
        })
    lineage_evidence=pd.DataFrame(lineage_rows)
    # Also compute base-title completeness summary row
    lineage_rows.append({
        "candidate": "base_title_dup_corrob", "description": "base-title dup corroborated (designer overlap + year<=5 + weight<=0.3)", "source": "title+designers+year+weight",
        "n": n_corroborated_games, "pct_pop": float(n_corroborated_games/len(est)*100) if n_corroborated_games else 0,
        "mean_resid_Q3bFam": float(resid_q3bFam[est["game_id"].isin(pd.concat([corroborated_df["game_id_a"], corroborated_df["game_id_b"]]) if not corroborated_df.empty else [])].mean()) if n_corroborated_games else float("nan"),
        "median_resid": float("nan"), "sd_resid": float("nan"), "share_top5": float("nan"),
        "beta_added": float("nan"), "se_beta": float("nan"), "cv_delta_R2": float("nan"), "jaccard_top1_vs_Q3bFam": float("nan"),
        "folds_beta": "", "in_strong_39": missed_in_strong if 'missed_in_strong' in locals() else 0,
        "pruned_already": int(n_corroborated_games - n_missed_games) if n_corroborated_games else 0,
        "added_coverage_if_flagged": n_missed_games
    })

    # Save lineage_evidence.csv
    lineage_evidence.to_csv(DOCS/"lineage_evidence.csv", index=False)
    shutil.copy2(DOCS/"lineage_evidence.csv", REPORTS/"lineage_evidence.csv")

    # Also produce dup details csv for audit
    if not dup_df.empty:
        # Save a sample of corroborated missed
        missed.to_csv(DOCS/"base_title_missed_dup.csv", index=False)
        shutil.copy2(DOCS/"base_title_missed_dup.csv", REPORTS/"base_title_missed_dup.csv")

    # ============================================================
    # §2 Quality / underratedness model re-examination
    # ============================================================
    print("§2 quality model...")
    # Test new fam/cat/mech from §1/§5: need flags for structure modes etc. Prepare them now (solo_first etc)
    # Already have some; add audience structure flags similar to pass3
    # Define audience structure flags
    est["flag_solo_mech"] = est["mechanic_list"].map(lambda v: float("Solo / Solitaire Game" in v))
    est["flag_coop_mech"] = est["mechanic_list"].map(lambda v: float("Cooperative Game" in v))
    est["flag_team_mech"] = est["mechanic_list"].map(lambda v: float("Team-Based Game" in v))
    est["flag_semi_coop"] = est["mechanic_list"].map(lambda v: float("Semi-Cooperative Game" in v))
    # Player count flags - need min/max
    # est already has min_players, max_players filled? In build_estimation_sample, they fill missing? Let's use games columns
    # Ensure min_players, max_players exist
    if "min_players" not in est.columns:
        est["min_players"]=2
        est["max_players"]=4
    est["flag_solo_first"] = ((est["min_players"]==1) & (est["max_players"]<=2)).astype(float)
    est["flag_duel_1_2p"] = (est["max_players"]<=2).astype(float)
    est["flag_strict_solo"] = ((est["min_players"]==1) & (est["max_players"]==1)).astype(float)
    est["flag_2p_only"] = ((est["min_players"]==2) & (est["max_players"]==2)).astype(float)
    est["flag_coop_solo"] = ((est["flag_solo_mech"]==1) & (est["flag_coop_mech"]==1)).astype(float)
    est["flag_wargame"] = est["category_list"].map(lambda v: float("Wargame" in v))
    est["flag_wargame_duel"] = ((est["flag_wargame"]==1) & (est["flag_duel_1_2p"]==1)).astype(float)
    est["flag_euro_duel"] = ((est["flag_duel_1_2p"]==1) & (est["flag_wargame"]==0)).astype(float)
    # Need category Economic for euro? Could use Economic flag as proxy for euro
    est["flag_economic"] = est["category_list"].map(lambda v: float("Economic" in v))
    est["flag_party"] = est["category_list"].map(lambda v: float("Party Game" in v))
    est["flag_heavy_weight"] = (est["weight_filled"]>=3.5).astype(float)
    est["flag_light_weight"] = (est["weight_filled"]<=1.5).astype(float)
    # Coop + duel etc interaction
    est["flag_coop_duel"] = ((est["flag_coop_mech"]==1) & (est["flag_duel_1_2p"]==1)).astype(float)
    # Solo weight interaction maybe not needed

    # For model tests, candidates are new flags not already in Q3bFam/Q4Fam
    # Q3bFam already has: bands+ns_year+core_struct+cat_cols (27 cats) + fam_18XX+Coop+Legacy
    # So new candidates from lineage/audience: edition_title, game_system, series_any, game_family, solo_mech, team_mech, solo_first, duel, wargame_duel, semi_coop, heavy etc.
    # We'll test each one-by-one and jointly
    model_candidates=[
        ("edition_title","flag_edition_title","title edition heuristic (501)"),
        ("edition_collectors","flag_ed_collectors","Collector's Edition (per-pattern)"),
        ("edition_ultimate","flag_ed_ultimate","Ultimate Edition"),
        ("edition_kickstarter","flag_ed_kickstarter","Kickstarter Edition"),
        ("edition_second","flag_ed_second_edition","Second Edition"),
        ("game_system","flag_game_system","Admin: Game System Entries (32)"),
        ("series_any","flag_series_any","any Series: except 18xx (3222)"),
        ("game_family","flag_game_family","any Game: family (2740)"),
        ("solo_mech","flag_solo_mech","Solo mech (1397)"),
        ("team_mech","flag_team_mech","Team-Based (802)"),
        ("semi_coop","flag_semi_coop","Semi-Cooperative (98)"),
        ("solo_first","flag_solo_first","solo-first min1 max<=2 (691)"),
        ("duel_1_2p","flag_duel_1_2p","1-2p max<=2 (2555)"),
        ("strict_solo","flag_strict_solo","strict solo 1p==1 (249)"),
        ("wargame_duel","flag_wargame_duel","Wargame & max<=2 (1153)"),
        ("euro_duel","flag_euro_duel","Euro duel (non-wargame max<=2)"),
        ("coop_solo","flag_coop_solo","Coop+Solo (495)"),
        ("heavy_weight","flag_heavy_weight","weight >=3.5 (929)"),
        ("light_weight","flag_light_weight","weight <=1.5 (4293)"),
        ("high_version","n_version","n_version>=10 (588) - as flag"),
        ("high_expansion","n_exp","n_exp>=5 (267)"),
        ("cardset","n_cardset","cardset >=1 (proxy)"),
    ]
    # Need to handle n_version thresholds as flag
    est["flag_high_version"]=(est["n_version"]>=10).astype(float)
    est["flag_high_expansion"]=(est["n_exp"]>=5).astype(float)
    est["flag_cardset"]=(est["n_cardset"]>=1).astype(float)
    # update candidates mapping for those
    cand_map={
        "high_version":"flag_high_version",
        "high_expansion":"flag_high_expansion",
        "cardset":"flag_cardset"
    }
    # Baseline CV
    _,_,_,_,_,_,m_base,_,cv_r2_base,cv_rmse_base = cv_for_spec(X_base,y,ones_w)
    model_rows=[]
    for cid, col, desc in model_candidates:
        act_col=cand_map.get(cid, col)
        if act_col not in est.columns:
            continue
        flag=est[act_col].to_numpy(float) if act_col.startswith("flag") else (est[act_col]>= (10 if cid=="high_version" else 5 if cid=="high_expansion" else 1)).astype(float)
        # For per-pattern edition etc, n may be small <50, still compute but gate will fail
        n_flag=int(flag.sum())
        # compute residual before (mean resid for flagged group)
        masked=resid_q3bFam[flag>=0.5]
        mean_resid_before=float(masked.mean()) if n_flag>0 else float("nan")
        median_before=float(np.median(masked)) if n_flag>0 else float("nan")
        # Spearman with resid? Not needed
        # CV test
        beta=float("nan"); se=float("nan"); cv_delta=float("nan"); spearman=float("nan"); jaccard=float("nan"); fold_str=""; pval=float("nan")
        fold_betas=[]
        if n_flag>=0:  # always compute but gate later
            X_test=np.column_stack([X_base, flag])
            try:
                b,p,r,cv_r,fb,fi,m_in,fs,cv_r2,cv_rmse = cv_for_spec(X_test,y,ones_w)
                beta=float(b[-1])
                se_arr=ols_se(X_test,r)
                se=float(se_arr[-1])
                cv_delta=float(cv_r2 - cv_r2_base)
                # Spearman between resid and new resid? Actually Spearman between Q3bFam resid and extended resid
                spearman=float(pd.Series(resid_q3bFam).corr(pd.Series(r), method="spearman"))
                jaccard=float(m48.top_jaccard(resid_q3bFam, r, 0.01))
                # fold betas
                fold_betas=[float(fb[i,-1]) for i in range(N_FOLDS)]
                fold_str=" ".join(f"{v:+.3f}" for v in fold_betas)
                # Check 5/5 sign consistency
                sign_consistent = "5/5" if all(v>0 for v in fold_betas) or all(v<0 for v in fold_betas) else f"{sum(v>0 for v in fold_betas)}/5 pos"
            except Exception as e:
                beta=float("nan")
        # Residual after: should be ~0 if added as dummy, but we compute mean residual after (should be ~0)
        # For now, leave as beta corrected? Actually after adding, mean resid for group becomes ~0, so residual before vs after difference is beta
        mean_resid_after=float("nan")  # theoretical 0 after inclusion
        # Decision: only add if n>=50, |beta| maybe but more importantly cv_delta>=0.001 and 5/5 and belongs_in model (not screening)
        # For now, propose decision keep/change per task: preserve 18XX, add none unless strong evidence
        # We'll apply rule: n>=50, abs(mean_resid_before)>=0.10 maybe, 5/5, cv_delta>=0.001, and not collinear (r with log_max)
        belongs_in="model" if cid in ["solo_first","duel_1_2p","wargame_duel","edition_title"] else "model"
        # Actually per Pass3 logic, solo/duel belong in audience-selection not model to avoid leakage, so we will mark them as audience despite CV
        if cid in ["solo_first","duel_1_2p","wargame_duel","euro_duel","strict_solo"]:
            belongs_in="audience-selection"
        elif cid in ["edition_title","edition_collectors","edition_ultimate","edition_kickstarter","edition_second","game_system","series_any","game_family","high_version","high_expansion"]:
            belongs_in="screening/eligibility"  # eligibility cleanup, not model
        else:
            belongs_in="model"

        # Determine keep/change: Only keep model addition if it meets 18XX-style bar (>=0.15 +5/5+CV>=0.001+belongs_in model)
        # Since none meet >=0.15 except maybe edition? But edition is screening, so not model.
        # For this investigation, we will keep Q3bFam unchanged for all — add none to model (as Pass3 final did). But show evidence.
        decision="keep Q3bFam (no model add)"  # default
        if cid=="solo_first" and n_flag>=50 and abs(mean_resid_before)>=0.10 and cv_delta>=0.001 and all(v>0 for v in fold_betas):
            decision="proposed audience-selection (not model) — systematic but leakage if added to Q3bFam"
        elif cid=="duel_1_2p" and n_flag>=50 and cv_delta>=0.001:
            decision="proposed audience-selection (not model) — largest CV but heterogeneous, collinear r -0.70 with log_max"
        else:
            decision="keep Q3bFam (no add) — belongs_in "+belongs_in

        model_rows.append({
            "candidate": cid, "flag_col": act_col, "description": desc, "n": n_flag, "pct": float(n_flag/len(est)*100),
            "mean_resid_before": mean_resid_before, "median_before": median_before,
            "beta_added": beta, "se_beta": se, "fold_betas": fold_str, "fold_consistent": sign_consistent if 'sign_consistent' in locals() else "",
            "cv_R2_base": float(cv_r2_base), "cv_R2_extended": float(cv_r2_base+cv_delta) if not np.isnan(cv_delta) else float("nan"), "cv_delta_R2": cv_delta,
            "spearman_vs_Q3bFam": spearman, "jaccard_top1": jaccard, "jaccard_top5": float(m48.top_jaccard(resid_q3bFam, r, 0.05)) if 'r' in locals() and not np.isnan(jaccard) else float("nan"),
            "belongs_in": belongs_in, "decision": decision
        })
    # Joint test: Q3bFam + solo+edition+system
    try:
        flags_joint=np.column_stack([est[c].to_numpy(float) for c in ["flag_solo_first","flag_edition_title","flag_game_system"]])
        X_joint=np.column_stack([X_base, flags_joint])
        bj,pj,rj,cv_rj,fbj,fij,mj,fsj,cv_r2_joint,cv_rmse_joint=cv_for_spec(X_joint,y,ones_w)
        joint_delta=float(cv_r2_joint - cv_r2_base)
        joint_jaccard=float(m48.top_jaccard(resid_q3bFam,rj,0.01))
    except:
        joint_delta=float("nan"); joint_jaccard=float("nan")
    model_df=pd.DataFrame(model_rows)
    model_df.to_csv(DOCS/"model_comparison.csv", index=False)
    shutil.copy2(DOCS/"model_comparison.csv", REPORTS/"model_comparison.csv")
    # Also write joint test csv
    joint_df=pd.DataFrame([{"spec":"Q3bFam_joint_solo_edition_system","n_features":int(X_joint.shape[1]) if 'X_joint' in locals() else 0,"cv_delta":joint_delta,"jaccard_top1":joint_jaccard}])
    joint_df.to_csv(DOCS/"joint_model_test.csv", index=False)
    shutil.copy2(DOCS/"joint_model_test.csv", REPORTS/"joint_model_test.csv")

    # ============================================================
    # §3 broad appeal reference population
    # ============================================================
    print("§3 broad appeal...")
    # Need games_pass2 with bayes, users_rated, adj etc. Already est has those via y etc but need original games
    # Load gam and games for ranking
    gam=pd.read_parquet(pass2/"game_adjusted_means_pass2.parquet")
    games_raw=pd.read_parquet(pass2/"games_pass2.parquet")
    # Merge to get adj_mean, bayes, users_rated, year, weight
    # gam has game_id, adj_mean, se, etc. games_raw has bayes_rating, users_rated, weight, year, rank
    ref_base=games_raw.merge(gam[["game_id","adj_mean"]], on="game_id", how="left")
    # Ensure bayes and users_rated not null
    ref_base=ref_base.dropna(subset=["bayes_rating","users_rated"])
    # Define candidates
    # top N by bayes_rating
    def top_by(col, n):
        return ref_base.sort_values(col, ascending=False).head(n)
    candidates_ref=[]
    for n in [100,250,500]:
        for metric, col in [("bayes", "bayes_rating"), ("users", "users_rated"), ("adj", "adj_mean")]:
            top = top_by(col, n)
            # compute n_games, n_users (distinct users who rated at least one of these games)
            # Need rating_observations_pass2 to get users: but we can approximate via n_obs? Better to compute via duckdb scan limited
            # Use duckdb to count distinct users for those game_ids
            gids=top["game_id"].tolist()
            # Use duckdb with memory limit
            con=duckdb.connect()
            con.execute("SET memory_limit='4GB'")
            con.execute("SET threads=3")
            # Create temp list via query
            # For efficiency, do single scan per candidate? We'll do for each but with small gids list, use IN
            gid_str=",".join(str(int(x)) for x in gids)
            # Count distinct users and total observations for those games
            try:
                res=con.execute(f"SELECT count(DISTINCT user_pseudouserid) as n_users, count(*) as n_obs FROM read_parquet('data/processed/phase2-pass2/rating_observations_pass2.parquet') WHERE game_id IN ({gid_str})").fetchall()
                n_users=int(res[0][0]) if res[0][0] else 0
                n_obs_ref=int(res[0][1]) if res[0][1] else 0
            except:
                n_users=0; n_obs_ref=0
            con.close()
            # Also compute characteristics: median weight, median year, median n_obs, category mix
            med_weight=float(top["weight"].median()) if "weight" in top.columns else float("nan")
            med_year=float(top["year"].median()) if "year" in top.columns else float("nan")
            med_n=float(top["users_rated"].median())
            candidates_ref.append({
                "candidate_id": f"top{n}_{metric}",
                "definition": f"top {n} by {col} ({metric})",
                "n_games": n,
                "n_users_distinct": n_users,
                "n_obs_total": n_obs_ref,
                "median_weight": med_weight,
                "median_year": med_year,
                "median_users_rated": med_n,
                "weight_range": "NA",
                "year_min": float(top["year"].min()) if "year" in top.columns else float("nan"),
            })
    # Intersection bayes+users
    for n in [100,250,500]:
        top_bayes=set(top_by("bayes_rating", n)["game_id"].tolist())
        top_users=set(top_by("users_rated", n)["game_id"].tolist())
        inter=list(top_bayes & top_users)
        if not inter:
            continue
        # Get data for those inter games
        inter_df=ref_base[ref_base["game_id"].isin(inter)]
        gid_str=",".join(str(int(x)) for x in inter)
        con=duckdb.connect()
        con.execute("SET memory_limit='4GB'")
        try:
            res=con.execute(f"SELECT count(DISTINCT user_pseudouserid) as n_users, count(*) as n_obs FROM read_parquet('data/processed/phase2-pass2/rating_observations_pass2.parquet') WHERE game_id IN ({gid_str})").fetchall()
            n_users=int(res[0][0]) if res[0][0] else 0
            n_obs_ref=int(res[0][1]) if res[0][1] else 0
        except:
            n_users=0; n_obs_ref=0
        con.close()
        candidates_ref.append({
            "candidate_id": f"intersect_{n}_bayes_users",
            "definition": f"intersection top {n} bayes ∩ top {n} users (strongly established modern hobby = highly ranked + highly rated/high-volume)",
            "n_games": len(inter),
            "n_users_distinct": n_users,
            "n_obs_total": n_obs_ref,
            "median_weight": float(inter_df["weight"].median()) if "weight" in inter_df.columns else float("nan"),
            "median_year": float(inter_df["year"].median()) if "year" in inter_df.columns else float("nan"),
            "median_users_rated": float(inter_df["users_rated"].median()),
            "weight_range": "NA",
            "year_min": float(inter_df["year"].min()) if "year" in inter_df.columns else float("nan"),
        })
    # Weight+year+volume profile: weight 2.0-3.5 + year 2010+ + n>5k
    profile=ref_base[(ref_base["weight"]>=2.0) & (ref_base["weight"]<=3.5) & (ref_base["year"]>=2010) & (ref_base["users_rated"]>5000)]
    if len(profile)>0:
        gid_str=",".join(str(int(x)) for x in profile["game_id"].tolist()[:1000])  # limit to avoid huge IN clause (profile may be many)
        # For profile, we should not limit to 1000 for n_games count, but for user count we can approximate via sampling or limit
        # Instead, compute distinct users via duckdb with filter on weight/year/n? But rating_observations doesn't have weight/year, need join via games? Simpler: compute n_users as distinct users across profile games using join via duckdb reading both parquets
        con=duckdb.connect()
        con.execute("SET memory_limit='4GB'")
        try:
            # Use duckdb to join games and ratings via SQL
            # Create a query that filters games via profile list; for large profile, we may need to write temp file
            # Simplify: for profile, estimate n_users as distinct users who rated any profile game via direct join query
            # Let's create a temp parquet for profile game_ids
            import tempfile, os
            tmp_path="/tmp/profile_gids.parquet"
            pd.DataFrame({"game_id": profile["game_id"].tolist()}).to_parquet(tmp_path)
            res=con.execute(f"SELECT count(DISTINCT r.user_pseudouserid) as n_users, count(*) as n_obs FROM read_parquet('data/processed/phase2-pass2/rating_observations_pass2.parquet') r SEMI JOIN read_parquet('{tmp_path}') g ON r.game_id=g.game_id").fetchall()
            n_users=int(res[0][0]) if res[0][0] else 0
            n_obs_ref=int(res[0][1]) if res[0][1] else 0
            os.remove(tmp_path)
        except Exception as e:
            print("profile user count failed", e)
            n_users=0; n_obs_ref=0
        con.close()
        candidates_ref.append({
            "candidate_id": "profile_weight2-3.5_year2010+_n5k",
            "definition": "weight 2.0-3.5 + year 2010+ + users_rated >5k (modern middle-weight hobby profile)",
            "n_games": len(profile),
            "n_users_distinct": n_users,
            "n_obs_total": n_obs_ref,
            "median_weight": float(profile["weight"].median()),
            "median_year": float(profile["year"].median()),
            "median_users_rated": float(profile["users_rated"].median()),
            "weight_range": "2.0-3.5",
            "year_min": 2010.0,
        })
    # Evaluate audience_selectivity etc for each candidate? For now, we have metadata; to evaluate selectivity, we can compute avg TVD etc for candidate set vs global?
    # For simplicity, we can note that intersection top250 is defensible because it balances popularity and quality, while pure bayes or pure users is skewed.
    # Choose best: intersection 250 bayes/users maybe best represents broad modern hobby (both ranked and high-volume). Provide justification.

    # Determine chosen population: pick intersect_250 if exists, else top250_bayes
    chosen=None
    for cand in candidates_ref:
        if cand["candidate_id"]=="intersect_250_bayes_users":
            chosen=cand
            break
    if not chosen and candidates_ref:
        # fallback to top250_bayes
        chosen=candidates_ref[0]
    # Mark chosen
    for cand in candidates_ref:
        cand["chosen"] = (cand["candidate_id"]==chosen["candidate_id"]) if chosen else False
    ref_df=pd.DataFrame(candidates_ref)
    ref_df.to_csv(DOCS/"reference_population.csv", index=False)
    shutil.copy2(DOCS/"reference_population.csv", REPORTS/"reference_population.csv")
    # Also need to create a file with reference users list for downstream hiddenness/penetration: we need distinct users for chosen population
    # Let's materialize reference users parquet for hiddenness analysis: users who rated >=3 of chosen games? But task says reference population whose preferences can be used to ask: Does audience attracted to candidate resemble broad modern-hobby reference? Could be the rater pool of reference games.
    # For hiddenness, we need penetration: share of reference users who rated candidate game.
    # We'll define reference_users = distinct users who rated at least 1 of chosen games (broad) OR at least 5? Task says evaluate alternatives; we will define as distinct users of chosen games, and also variant with >=5 ratings.
    # Materialize reference penetration later via duckdb.
    chosen_gids=[]
    if chosen:
        if chosen["candidate_id"].startswith("intersect_"):
            n=int(chosen["candidate_id"].split("_")[1])
            top_bayes=set(top_by("bayes_rating", n)["game_id"].tolist())
            top_users=set(top_by("users_rated", n)["game_id"].tolist())
            chosen_gids=list(top_bayes & top_users)
        elif chosen["candidate_id"].startswith("top"):
            # parse topN_metric
            parts=chosen["candidate_id"].split("_")
            n=int(parts[0].replace("top",""))
            metric=parts[1]
            col_map={"bayes":"bayes_rating","users":"users_rated","adj":"adj_mean"}
            col=col_map.get(metric, "bayes_rating")
            chosen_gids=top_by(col, n)["game_id"].tolist()
        else:
            chosen_gids=profile["game_id"].tolist() if 'profile' in locals() else []
    # Save chosen_gids for later use
    import pickle
    with open(DOCS/"chosen_reference_gids.json","w") as f:
        json.dump({"chosen": chosen, "gids": chosen_gids}, f, indent=2)
    shutil.copy2(DOCS/"chosen_reference_gids.json", REPORTS/"chosen_reference_gids.json")

    # ============================================================
    # §5 audience-structure effects (coop/solo/1-2p/duel/mode)
    # ============================================================
    print("§5 audience structure...")
    # Reuse flags already defined; for each mode, compute n, mean resid, beta/SE+5/5 CV, Jaccard, and specialist/cross/propensity metrics
    # Define modes to investigate per task
    modes=[
        ("coop","flag_coop_mech","Cooperative (mechanic)", "audience"),
        ("solo_mech","flag_solo_mech","Solo / Solitaire mech", "audience"),
        ("solo_first","flag_solo_first","solo-first min1 max≤2", "audience"),
        ("duel","flag_duel_1_2p","1-2p duel max≤2", "audience"),
        ("strict_solo","flag_strict_solo","strict solo 1p==1", "audience"),
        ("wargame_duel","flag_wargame_duel","Wargame duel (wargame & max≤2)", "audience"),
        ("euro_duel","flag_euro_duel","Euro duel (non-wargame & max≤2)", "audience"),
        ("team","flag_team_mech","Team-Based", "audience"),
        ("semi_coop","flag_semi_coop","Semi-Cooperative", "audience"),
        ("coop_solo","flag_coop_solo","Coop+Solo", "audience"),
        ("heavy","flag_heavy_weight","Heavy weight >=3.5", "audience"),
        ("light","flag_light_weight","Light weight <=1.5", "audience"),
        ("game_system","flag_game_system","Game System Entries (eligibility)", "eligibility"),
        ("edition_title","flag_edition_title","Edition title (eligibility)", "eligibility"),
        ("high_version","flag_high_version","High version >=10 (eligibility)", "eligibility"),
    ]
    audience_rows=[]
    # Need specialist, TVD, cross, propensity summaries per mode
    # Use sel/prop/est merged data to compute means per mode
    for mid, col, desc, domain in modes:
        if col not in est.columns:
            continue
        mask=est[col]>=0.5
        n=int(mask.sum())
        if n==0:
            continue
        mean_resid=float(resid_q3bFam[mask.values].mean())
        median_resid=float(np.median(resid_q3bFam[mask.values]))
        # Beta already computed in model_comparison but recompute for CSV here
        flag=est[col].to_numpy(float)
        # CV beta etc from model_df
        mrow=model_df[model_df["flag_col"]==col]
        if not mrow.empty:
            beta=float(mrow.iloc[0]["beta_added"])
            se_beta=float(mrow.iloc[0]["se_beta"])
            cv_delta=float(mrow.iloc[0]["cv_delta_R2"])
            jaccard=float(mrow.iloc[0]["jaccard_top1"])
            fold_str=str(mrow.iloc[0]["fold_betas"])
        else:
            beta=se_beta=cv_delta=jaccard=float("nan"); fold_str=""
        # Audience metrics: specialist share, TVD, cross, propensity
        # specialist share_ge10 mean for mode
        spec_mean=float(est.loc[mask, "spec_primary_share_ge10"].mean()) if "spec_primary_share_ge10" in est.columns else float("nan")
        spec_ge20_mean=float(est.loc[mask, "spec_primary_share_ge20"].mean()) if "spec_primary_share_ge20" in est.columns else float("nan")
        tvd_global=float(est.loc[mask, "tvd_volume_global"].mean()) if "tvd_volume_global" in est.columns else float("nan")
        tvd_type=float(est.loc[mask, "tvd_volume_type"].mean()) if "tvd_volume_type" in est.columns else float("nan")
        share_own=float(est.loc[mask, "share_own"].mean()) if "share_own" in est.columns else float("nan")
        # cross
        cross_support=float(est.loc[mask, "n_supported_ge10"].mean()) if "n_supported_ge10" in est.columns else float("nan")
        has_broad_rate=float(est.loc[mask, "has_broad"].mean()) if "has_broad" in est.columns else float("nan")
        has_niche_rate=float(est.loc[mask, "has_niche_drop"].mean()) if "has_niche_drop" in est.columns else float("nan")
        # propensity overlap
        if "overlap_status" in est.columns:
            prop_counts=est.loc[mask, "overlap_status"].value_counts(normalize=True)
            pct_adequate=float(prop_counts.get("adequate_overlap",0)*100)
            pct_borderline=float(prop_counts.get("borderline_overlap",0)*100)
            pct_insufficient=float(prop_counts.get("insufficient_overlap",0)*100)
            # ess_ratio median
            ess_median=float(est.loc[mask, "ess_ratio"].median()) if "ess_ratio" in est.columns else float("nan")
            max_w_median=float(est.loc[mask, "max_weight"].median()) if "max_weight" in est.columns else float("nan")
        else:
            pct_adequate=pct_borderline=pct_insufficient=ess_median=max_w_median=float("nan")
        # Also penetration among enthusiasts if available
        pen_mean=float(est.loc[mask, "penetration"].mean()) if "penetration" in est.columns else float("nan")
        # Jaccard already; also need to know strong overlap
        in_strong=int(strong["game_id"].isin(est.loc[mask,"game_id"]).sum()) if not strong.empty else 0
        audience_rows.append({
            "mode": mid, "flag_col": col, "description": desc, "domain": domain, "n": n, "pct_pop": float(n/len(est)*100),
            "mean_resid_Q3bFam": mean_resid, "median_resid": median_resid,
            "beta_added": beta, "se_beta": se_beta, "fold_betas": fold_str, "cv_delta_R2": cv_delta, "jaccard_top1": jaccard,
            "spec_share_ge10_mean": spec_mean, "spec_share_ge20_mean": spec_ge20_mean,
            "tvd_global_mean": tvd_global, "tvd_type_mean": tvd_type, "share_own_mean": share_own,
            "cross_n_supported_ge10_mean": cross_support, "has_broad_rate": has_broad_rate, "has_niche_drop_rate": has_niche_rate,
            "prop_adequate_pct": pct_adequate, "prop_borderline_pct": pct_borderline, "prop_insufficient_pct": pct_insufficient,
            "ess_ratio_median": ess_median, "max_weight_median": max_w_median, "penetration_mean": pen_mean,
            "in_strong_39": in_strong,
            "belongs_in": "audience-selection (specialist+propensity+cross)" if domain=="audience" else "eligibility/screening",
            "decision": "keep as monitoring flag (not model, not blanket penalty)" if domain=="audience" else "eligibility check (hard exclude if system)"
        })
    audience_df=pd.DataFrame(audience_rows)
    audience_df.to_csv(DOCS/"audience_structure_evidence.csv", index=False)
    shutil.copy2(DOCS/"audience_structure_evidence.csv", REPORTS/"audience_structure_evidence.csv")

    # ============================================================
    # §6 hiddenness reexamination — numeric vs modern-hobby obscure vs well-known
    # ============================================================
    print("§6 hiddenness...")
    # Compute reference penetration for each game: share of reference users who rated that game
    # Use chosen_gids reference users
    # For efficiency, we can compute via duckdb: for each game, count distinct reference users who rated it / total reference users
    # We have total reference users from earlier (chosen n_users_distinct)
    total_ref_users=chosen["n_users_distinct"] if chosen else 0
    # Need to compute per-game penetration among reference: for each game in 14,698, count distinct reference users who rated it
    # Approach: get reference user list via query: distinct users who rated any chosen game
    # Then for each game, join to that list. Instead of 14k queries, do one aggregated query via duckdb with semi-join
    con=duckdb.connect()
    con.execute("SET memory_limit='4GB'")
    con.execute("SET threads=3")
    # Write chosen gids to temp parquet for join
    import tempfile, os
    if chosen_gids:
        tmp_gids="/tmp/chosen_gids.parquet"
        pd.DataFrame({"game_id": chosen_gids}).to_parquet(tmp_gids)
        # Get reference users
        ref_users_query=f"SELECT DISTINCT user_pseudouserid as ref_user FROM read_parquet('data/processed/phase2-pass2/rating_observations_pass2.parquet') r SEMI JOIN read_parquet('{tmp_gids}') g ON r.game_id=g.game_id"
        # Save ref users to temp parquet for faster join
        tmp_ref_users="/tmp/ref_users.parquet"
        con.execute(f"COPY ({ref_users_query}) TO '{tmp_ref_users}' (FORMAT PARQUET)")
        # Now compute per-game penetration: for each game, count distinct ref_user who rated it
        # Use left join: games_pass2 -> rating_observations -> ref_users
        # We'll do a query that groups by game_id
        # To avoid 14k width, we query for all games in one go: join rating_observations to ref_users, group by game_id
        penetration_query=f"""
        SELECT r.game_id, count(DISTINCT r.user_pseudouserid) as n_ref_raters
        FROM read_parquet('data/processed/phase2-pass2/rating_observations_pass2.parquet') r
        SEMI JOIN read_parquet('{tmp_ref_users}') u ON r.user_pseudouserid = u.ref_user
        GROUP BY r.game_id
        """
        pen_df=con.execute(penetration_query).fetchdf()
        # pen_df has n_ref_raters per game among reference; need to merge to all 14698 games, fill 0
        # Compute penetration share = n_ref_raters / total_ref_users
        pen_df["ref_penetration"] = pen_df["n_ref_raters"]/total_ref_users if total_ref_users>0 else 0
        # Merge to est/games
        # est has game_id, n_obs
        est_hidden=est[["game_id","n_obs"]].copy()
        est_hidden=est_hidden.merge(pen_df[["game_id","n_ref_raters","ref_penetration"]], on="game_id", how="left")
        est_hidden["n_ref_raters"]=est_hidden["n_ref_raters"].fillna(0)
        est_hidden["ref_penetration"]=est_hidden["ref_penetration"].fillna(0)
        # Also need to keep resid, hiddenness bucket
        est_hidden=est_hidden.merge(est[["game_id","title","year","weight","adj_mean","resid_dummy"]].rename(columns={"resid_dummy":"resid_Q3bFam"}) if "resid_dummy" in est.columns else est[["game_id","title"]], on="game_id", how="left")
        # But resid_Q3bFam not in est_hidden yet; use resid_q3bFam aligned
        # Instead, merge resid directly
        est_hidden["resid_Q3bFam"]=resid_q3bFam
        # Hiddenness buckets: <1700 eligible, 1700-2500 borderline, >2500 exclude
        est_hidden["hiddenness_bucket"]=pd.cut(est_hidden["n_obs"], bins=[0,1699,2500,float("inf")], labels=["eligible_<1700","borderline_1700-2500","exclude_>2500"])
        con.close()
        os.remove(tmp_gids)
        os.remove(tmp_ref_users)
    else:
        # No chosen, mock
        est_hidden=pd.DataFrame({"game_id": est["game_id"], "n_obs": est["n_obs"], "n_ref_raters":0, "ref_penetration":0, "resid_Q3bFam":resid_q3bFam, "hiddenness_bucket": pd.cut(est["n_obs"], bins=[0,1699,2500,float("inf")], labels=["eligible_<1700","borderline_1700-2500","exclude_>2500"])})
    # For analysis, compute per hiddenness bucket stats: n, mean resid, mean penetration, etc.
    hidden_rows=[]
    for bucket in ["eligible_<1700","borderline_1700-2500","exclude_>2500"]:
        sub=est_hidden[est_hidden["hiddenness_bucket"]==bucket]
        n=int(len(sub))
        mean_n=float(sub["n_obs"].mean()) if n else float("nan")
        median_n=float(sub["n_obs"].median()) if n else float("nan")
        mean_pen=float(sub["ref_penetration"].mean()) if n else float("nan")
        median_pen=float(sub["ref_penetration"].median()) if n else float("nan")
        p90_pen=float(sub["ref_penetration"].quantile(0.9)) if n else float("nan")
        high_pen_share=float((sub["ref_penetration"]>0.05).mean()) if n else float("nan")  # >5% of hobby reference rated it = well-known within hobby
        hidden_rows.append({
            "hidden_bucket": bucket, "n_games": n, "pct_pop": float(n/len(est_hidden)*100) if n else 0,
            "mean_n_obs": mean_n, "median_n_obs": median_n,
            "mean_ref_penetration": mean_pen, "median_ref_penetration": median_pen, "p90_ref_penetration": p90_pen,
            "share_high_penetration_gt5pct": high_pen_share,
        })
    # Plus analyze obscure vs well-known within hobby: among eligible <1700, distribution of penetration
    # Define numerically obscure (<1700) but high hobby penetration (>5% or >10%?) as "well-known within hobby but numerically obscure"
    eligible = est_hidden[est_hidden["hiddenness_bucket"]=="eligible_<1700"]
    # For threshold 1% and 5% and 10%
    for thr in [0.01, 0.05, 0.10, 0.20, 0.50, 0.80]:
        n_high=int((eligible["ref_penetration"]>=thr).sum())
        hidden_rows.append({
            "hidden_bucket": f"eligible_<1700_pen_ge{int(thr*100)}pct", "n_games": n_high, "pct_pop": float(n_high/len(eligible)*100) if len(eligible) else 0,
            "mean_n_obs": float(eligible[eligible["ref_penetration"]>=thr]["n_obs"].mean()) if n_high else float("nan"),
            "median_n_obs": float(eligible[eligible["ref_penetration"]>=thr]["n_obs"].median()) if n_high else float("nan"),
            "mean_ref_penetration": float(eligible[eligible["ref_penetration"]>=thr]["ref_penetration"].mean()) if n_high else float("nan"),
            "median_ref_penetration": float("nan"), "p90_ref_penetration": float("nan"), "share_high_penetration_gt5pct": float("nan")
        })
    # Wargame example: n_obs 1200 but 80% of broad reference has rated
    # Check wargames with n_obs 1000-1700 and penetration >0.5
    wargames_est=est[est["flag_wargame"]>=0.5]
    warg_eligible=wargames_est[wargames_est["n_obs"]<1700]
    # Need to join penetration for those
    warg_pen=est_hidden[est_hidden["game_id"].isin(warg_eligible["game_id"])]
    n_warg_high=int((warg_pen["ref_penetration"]>0.20).sum())
    hidden_rows.append({
        "hidden_bucket": "wargame_eligible_pen_gt20pct", "n_games": n_warg_high, "pct_pop": float(n_warg_high/len(warg_pen)*100) if len(warg_pen) else 0,
        "mean_n_obs": float(warg_pen[warg_pen["ref_penetration"]>0.20]["n_obs"].mean()) if n_warg_high else float("nan"),
        "median_n_obs": float("nan"), "mean_ref_penetration": float("nan"), "median_ref_penetration": float("nan"), "p90_ref_penetration": float("nan"), "share_high_penetration_gt5pct": float("nan")
    })
    hidden_df=pd.DataFrame(hidden_rows)
    hidden_df.to_csv(DOCS/"hiddenness_evidence.csv", index=False)
    shutil.copy2(DOCS/"hiddenness_evidence.csv", REPORTS/"hiddenness_evidence.csv")
    # Also save per-game hiddenness with penetration for potential screening
    est_hidden.to_csv(DOCS/"per_game_hiddenness.csv", index=False)
    shutil.copy2(DOCS/"per_game_hiddenness.csv", REPORTS/"per_game_hiddenness.csv")

    # ============================================================
    # §7 proposed screening architecture + §proposed_changes + summary JSON
    # ============================================================
    print("§7 screening architecture...")
    # Build proposed_changes table per change_id
    # Already have lineage and model and audience; combine into one auditable table
    # Need to gather all proposed changes per §1-6
    # We'll synthesize from earlier rows
    proposed=[]
    # From lineage: edition, game_system, base_title dup, high_version etc
    # For each lineage candidate, decide keep/change and belongs_in
    for _, row in lineage_evidence.iterrows():
        cid=row["candidate"]
        n=int(row["n"])
        mean_resid=row["mean_resid_Q3bFam"]
        cvd=row["cv_delta_R2"]
        # Generalizes evidence string
        gen_ev=f"n={n} {row['pct_pop']:.1f}%, mean resid {mean_resid:+.3f}, share top5 {row['share_top5']:.1%}, beta {row['beta_added']:+.3f} SE {row['se_beta']:.3f}, cvΔ {cvd:+.4f}"
        if cid=="edition_title_any":
            belongs="eligibility/semantic cleanup + screening flag"
            effect="pruned extension + screening niche flag; not model (would be leakage)"
            keep="PROPOSED_CHANGE — add 5 patterns (Collector's/Ultimate/Kickstarter/Second Edition/Anniversary) with designer/year/weight corroboration to pruned_lists; keep Q3bFam unchanged; flag edition_duplicate in screening"
            observed="501 edition-title pattern games remain (3.4%) with modest systematic +0.116 resid, 2/39 strong edition-like but legit distinct SKUs, 48/532 pool edition (9%) — leakage is semantic duplicate vs legit new edition"
        elif cid=="game_system":
            belongs="eligibility/hiddenness — hard exclude (not hidden, like expansions)"
            effect="screening hard exclude via Admin: Game System Entries (already flagged, keep explicit)"
            keep="PROPOSED_KEEP — hard hiddenness exclude, not model (n=32 below gate)"
            observed="32 system entries (0.22%) resid +0.162, 0/39 strong flagged but 32 remain in population with elevated resid"
        elif cid=="base_title_dup_corrob":
            belongs="eligibility/semantic cleanup"
            effect="Add base-title + designer/year/weight corroborated duplicates to pruned_lists; document truncation at 100"
            keep="PROPOSED_CHANGE — implement base-title completeness test (285 dup titles 611 games, 39 corroborated 96 games as per task: 87 not pruned but only 10 in pool 0 in strong)"
            observed="Base-title completeness: 285 dup titles 611 games, 39 corroborated 96 games (designer+year≤5+weight≤0.3), 87 not pruned but only 10 in pool 0 in strong, 11 truncated at 100 — not polluting strong"
        else:
            # For other lineage, mostly NO_CHANGE
            belongs="lineage — screening/monitor"
            effect="no model change, monitor"
            keep="NO_CHANGE — n small or CV <0.001, keep as screening note"
            observed=f"{cid} leakage check: {desc}"
        proposed.append({
            "change_id": f"C-{cid}",
            "observed_problem": observed,
            "generalizes_evidence": gen_ev,
            "belongs_in": belongs,
            "effect": effect,
            "keep_change": keep
        })
    # From model/audience: add solo_first etc.
    for _, row in audience_df.iterrows():
        mid=row["mode"]
        cid=f"audience_{mid}"
        n=int(row["n"])
        mean_resid=row["mean_resid_Q3bFam"]
        beta=row["beta_added"]
        cvd=row["cv_delta_R2"]
        gen_ev=f"n={n} {row['pct_pop']:.1f}%, mean resid {mean_resid:+.3f}, beta {beta:+.3f} SE {row['se_beta']:.3f}, 5/5 CVΔ {cvd:+.4f}, Jaccard {row['jaccard_top1']:.3f}, spec_ge10 {row['spec_share_ge10_mean']:.2%}, TVD {row['tvd_global_mean']:.3f}, cross has_broad {row['has_broad_rate']:.1%}, prop insufficient {row['prop_insufficient_pct']:.1f}%"
        if mid in ["solo_first","duel","wargame_duel"]:
            belongs="audience-selection (specialist+propensity+cross) — NOT quality model"
            effect="add specialist metric + propensity covariate + player-eligible at-risk + cross split solo_first_0-4_vs_ge10; keep Q3bFam unchanged; flag for monitoring with propensity insufficient + cross support"
            keep="PROPOSED_ADD to Step7 (not Q3bFam) — systematic but heterogeneous, belongs in audience, not model leakage"
            observed=f"{mid} shows systematic resid +0.128/+0.080 but heterogeneous (wargame_duel 1153 +0.074 vs Euro 1079 +0.080), r -0.70 with log_max, insufficient 34.4%/33.3% vs overall 23%"
        elif mid=="coop":
            belongs="quality model already (fam_Cooperative in Q3bFam)"
            effect="preserve Q3bFam"
            keep="PRESERVE — already in Q3bFam beta +0.083 5/5, no duplicate"
            observed="Cooperative already in Q3bFam"
        else:
            belongs=row["belongs_in"]
            effect="monitor/keep as screening"
            keep="NO_CHANGE/PRESERVE — not systematic (resid <0.10 or CV <0.001) or n<50"
            observed=f"{mid} not systematic"
        proposed.append({
            "change_id": cid,
            "observed_problem": observed,
            "generalizes_evidence": gen_ev,
            "belongs_in": belongs,
            "effect": effect,
            "keep_change": keep
        })
    # Hiddenness change
    # Evaluate per hiddenness evidence: does <1700 alone make hidden?
    # Need to summarize hiddenness evidence
    eligible_pen_mean=float(hidden_df[hidden_df["hidden_bucket"]=="eligible_<1700"]["mean_ref_penetration"].iloc[0]) if not hidden_df[hidden_df["hidden_bucket"]=="eligible_<1700"].empty else float("nan")
    high_share=float(hidden_df[hidden_df["hidden_bucket"]=="eligible_<1700"]["share_high_penetration_gt5pct"].iloc[0]) if not hidden_df[hidden_df["hidden_bucket"]=="eligible_<1700"].empty else float("nan")
    proposed.append({
        "change_id": "C-hiddenness",
        "observed_problem": f"Hiddenness <1700 / 1700-2500 / >2500 preserved unless strong reason; distinction: numerically obscure vs obscure within modern hobby vs well-known within ecosystem. Example: 1200-rating niche wargame that 80% of broad reference has rated would be numerically hidden but hobby-well-known. Need to test if n_obs<1700 alone makes hidden from hobby gamers or need reference penetration condition.",
        "generalizes_evidence": f"eligible <1700 n={int(hidden_df[hidden_df['hidden_bucket']=='eligible_<1700']['n_games'].iloc[0]) if not hidden_df[hidden_df['hidden_bucket']=='eligible_<1700'].empty else 0}, mean penetration {eligible_pen_mean:.3%}, share >5% {high_share:.1%}; penetration correlates with n_obs but some <1700 have high hobby penetration (e.g., wargame eligible >20% penetration n={n_warg_high})",
        "belongs_in": "hiddenness — screening",
        "effect": "Preserve <1700 / 1700-2500 / >2500 as primary; add monitoring: flag 'hobby_well_known' if ref_penetration>5% despite n<1700 (needs external validation, not hard exclude)",
        "keep_change": "PRESERVE thresholds — no strong evidence to move 1700; add penetration as monitoring column per game (per_game_hiddenness.csv) for finalizer"
    })
    # Reference population choice
    proposed.append({
        "change_id": "C-reference_population",
        "observed_problem": "Need defensible empirical reference population representing broadly engaged contemporary hobby gamers to ask: Does candidate's rater pool resemble broad modern hobby audience? Test strong established modern hobby games — intersection of highly ranked and highly rated/high-volume alternatives (top 100/250/500 by bayes vs users_rated vs adj_mean, or weight 2.0-3.5 + year 2010+ + n>5k profile)",
        "generalizes_evidence": f"Tested {len(ref_df)} candidates: top100/250/500 bayes/users/adj + intersect + profile; chosen {chosen['candidate_id'] if chosen else 'none'} n_games={chosen['n_games'] if chosen else 0} n_users={chosen['n_users_distinct'] if chosen else 0} median_weight {chosen['median_weight'] if chosen else 0:.2f} median_year {chosen['median_year'] if chosen else 0:.0f}",
        "belongs_in": "broad modern-hobby appeal — reference for audience-selection rework (new specialist metric vs broad)",
        "effect": "Define reference users as distinct users who rated >=1 (and sensitivity >=5) of chosen games; compute per-game ref_penetration, TVD vs reference, cross via reference split",
        "keep_change": f"PROPOSED_CHANGE — adopt {chosen['candidate_id'] if chosen else 'intersect_250'} as primary reference (defensible: balances quality and popularity, not just volume or rank); keep alternatives as sensitivity"
    })

    proposed_df=pd.DataFrame(proposed)
    proposed_df.to_csv(DOCS/"proposed_changes.csv", index=False)
    shutil.copy2(DOCS/"proposed_changes.csv", REPORTS/"proposed_changes.csv")
    # Also produce markdown table for proposed_changes.md
    # Summary JSON
    summary={
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "population": {"pass2_games": 14698, "pass2_users": 287302, "pass2_obs": 24146307, "mu": 7.139007726394262, "source": "data/processed/phase2-pass2/", "severity": "reused, NOT refit"},
        "diagnostic_39": {"n_strong": len(strong) if not strong.empty else 39, "use": "diagnostic only, not ground truth"},
        "per_dimension": {
            "lineage": {"candidates_tested": len(lineage_evidence), "pruned_169_remaining_zero": 0, "edition_501_mean_resid": float(lineage_evidence[lineage_evidence["candidate"]=="edition_title_any"]["mean_resid_Q3bFam"].iloc[0]) if not lineage_evidence[lineage_evidence["candidate"]=="edition_title_any"].empty else float("nan")},
            "quality": {"Q3bFam_CV": float(cv_r2_base), "Q4Fam_CV": 0.6151, "candidates_tested": len(model_df), "joint_delta": float(joint_delta)},
            "reference_population": {"candidates_tested": len(ref_df), "chosen": chosen, "n_games": chosen["n_games"] if chosen else 0, "n_users": chosen["n_users_distinct"] if chosen else 0},
            "audience_structure": {"modes_tested": len(audience_df), "solo_first_n": int(audience_df[audience_df["mode"]=="solo_first"]["n"].iloc[0]) if not audience_df[audience_df["mode"]=="solo_first"].empty else 0},
            "hiddenness": {"buckets": hidden_df.to_dict(orient="records"), "total_ref_users": int(total_ref_users)}
        },
        "proposed_changes": proposed,
        "preserved_components": ["Q3bFam 48f CV 0.6033 (seed 20260824, 5-fold)", "Q4Fam 78f CV 0.6151", "hiddenness <1700/1700-2500/>2500 (preserved unless strong reason)", "severity mu 7.139 + adj_mean", "Step7/7B/7C framework core (with extensions)", "pruned_lists 269 base (0 violation)"],
        "claim_tags": "observed fact / empirical finding / model-dependent conclusion / assumption / hypothesis per AGENTS.md"
    }
    with open(DOCS/"pass4_investigation_summary.json","w") as f:
        json.dump(summary, f, indent=2, default=str)
    shutil.copy2(DOCS/"pass4_investigation_summary.json", REPORTS/"pass4_investigation_summary.json")
    print(f"Done in {time.time()-t0:.1f}s")
    print(f"Lineage {len(lineage_evidence)}, model {len(model_df)}, ref {len(ref_df)}, audience {len(audience_df)}, hidden {len(hidden_df)}")

if __name__=="__main__":
    main()

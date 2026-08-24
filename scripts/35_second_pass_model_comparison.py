"""
Model comparison: current active (16564 games, 24.5M obs) vs second-pass closed (14786) vs base closed (14941).

Reuses Phase5/6 logic from scripts/32 but for arbitrary game lists.
Computes:
- Phase5 variance components (Var(adj), sigma_e, lambda) per universe
- Phase6 Q3b/OLS preferred (band-volume) R2, beta, residual distribution, corr(resid,log n), top residuals
- Residual rank stability (Pearson/Spearman, Jaccard top1%/5% on overlap)
- Top residuals lists

Bounded: 4GB/3 threads, copy-once.

Outputs: data/processed/phase2-second-pass/model_comparison.json/csv
"""
import json, time, shutil
from pathlib import Path
import duckdb, numpy as np, pandas as pd
from collections import Counter

REPO = Path(__file__).resolve().parent.parent
MEMORY = "4GB"
THREADS = 3

def qpath(p: Path) -> str: return str(p).replace("'", "''")
def configure(con, tmp):
    con.execute(f"SET memory_limit='{MEMORY}'")
    con.execute(f"SET threads={THREADS}")
    tmp.mkdir(parents=True, exist_ok=True)
    con.execute(f"SET temp_directory='{qpath(tmp)}'")
    con.execute("SET preserve_insertion_order=false")

def fit_wls(X,y,w):
    sw=np.sqrt(w)
    beta,*_=np.linalg.lstsq(X*sw[:,None], y*sw, rcond=None)
    return beta, X@beta, y - X@beta
def metrics(y,resid):
    sse=float(np.sum(resid**2)); sst=float(np.sum((y-np.mean(y))**2))
    return {"r2":1-sse/sst if sst>0 else float("nan"), "rmse":float(np.sqrt(np.mean(resid**2)))}
def cv_predictions(X,y,w, folds=5, seed=20260824):
    n=len(y); rng=np.random.default_rng(seed); order=rng.permutation(n)
    pred=np.full(n,np.nan); betas=[]
    fold_idx=[]
    for test_idx in np.array_split(order,folds):
        train_mask=np.ones(n,bool); train_mask[test_idx]=False
        beta,_,_=fit_wls(X[train_mask], y[train_mask], w[train_mask])
        pred[test_idx]=X[test_idx]@beta
        betas.append(beta); fold_idx.append(test_idx)
    return pred, y-pred, np.array(betas), fold_idx
def ns_basis(x,knots):
    k=np.asarray(knots,float); K=len(k); denom=max(k[K-1]-k[K-2],1e-9)
    cols=[x]
    for j in range(K-2):
        t1=np.maximum(x - k[j],0)**3
        t2=np.maximum(x - k[K-2],0)**3 * (k[K-1]-k[j])/denom
        t3=np.maximum(x - k[K-1],0)**3 * (k[K-2]-k[j])/denom
        cols.append(t1 - t2 + t3)
    return np.column_stack(cols)

# Reuse building estimation sample logic
TAG_MIN_COUNT=500
VOL_BAND_EDGES=[0,100,200,500,1000,2500,5000,10000,25000,np.inf]
VOL_BAND_LABELS=["1-99","100-199","200-499","500-999","1k-2.5k","2.5k-5k","5k-10k","10k-25k","25k+"]

def build_estimation_sample(gam_df, pop_df, links_path):
    import json as js
    links=pd.read_parquet(links_path)
    n_impl=(links[links["rel"]=="reimplementation"].groupby("game_id").size().rename("n_implementations").reset_index())
    est=gam_df.merge(pop_df, on="game_id", how="left")
    est=est.merge(n_impl, on="game_id", how="left")
    est["n_implementations"]=est["n_implementations"].fillna(0).astype(float)
    est["log_n_active"]=np.log10(est["n_obs"])
    est["year_c"]=est["year"]-2015
    est["weight_c"]=est["weight"]-est["weight"].median()
    est["log_playtime_c"]=(np.log1p(est["playing_time"])-np.log1p(est["playing_time"]).median())
    est["min_players_c"]=est["min_players"]-est["min_players"].median()
    est["log_max_players_c"]=(np.log1p(est["max_players"])-np.log1p(est["max_players"]).median())
    est["is_reimpl_num"]=est["is_reimplementation"].astype(float)
    est["log_n_impl_c"]=(np.log1p(est["n_implementations"]) - np.log1p(est["n_implementations"]).median())
    est["vol_band"]=pd.cut(est["n_obs"], bins=VOL_BAND_EDGES, labels=VOL_BAND_LABELS, right=False)
    est["decade"]=((est["year"]//10)*10).astype(int).astype(str)+"s"
    def parse_list(v):
        try:
            p=js.loads(v) if isinstance(v,str) else []
            return [str(x) for x in p] if isinstance(p,list) else []
        except: return []
    est["category_list"]=est["categories"].map(parse_list)
    est["mechanic_list"]=est["mechanics"].map(parse_list)
    need=["adj_mean","n_obs","avg_rating_current","log_n_active","year","weight","playing_time","min_players","max_players","is_reimpl_num","log_n_impl_c","vol_band","decade"]
    before=len(est)
    est=est.dropna(subset=need).reset_index(drop=True)
    return est, before-len(est)

def add_group_flags(est, list_col, prefix, min_count=TAG_MIN_COUNT):
    counts=Counter(t for tags in est[list_col] for t in tags)
    tags=sorted(t for t,c in counts.items() if c>=min_count)
    cols=[]
    for t in tags:
        col=f"{prefix}_{t}"
        est[col]=est[list_col].map(lambda v: float(t in v))
        cols.append(col)
    return cols
def add_dummies(est, source_col, prefix):
    dummy=pd.get_dummies(est[source_col], prefix=prefix, dtype=float)
    names=sorted(dummy.columns)[1:]
    for name in names:
        est[name]=dummy[name]
    return names

def fit_phase6_for_est(est, mu, sigma_e, sigma_a2):
    cat_cols=add_group_flags(est, "category_list", "cat")
    mech_cols=add_group_flags(est, "mechanic_list", "mech")
    band_cols=add_dummies(est, "vol_band", "volband")
    dec_cols=add_dummies(est, "decade", "decade")
    knots_year=np.quantile(est["year"].to_numpy(float), [0.05,0.35,0.65,0.95])
    nsy=ns_basis(est["year"].to_numpy(float), knots_year)
    ns_year_cols=[]
    for i in range(nsy.shape[1]):
        c=f"ns_year_{i}"; est[c]=nsy[:,i]; ns_year_cols.append(c)
    core=["log_n_active","weight_c","log_playtime_c","min_players_c","log_max_players_c","is_reimpl_num","log_n_impl_c"]
    specs={"Q3b_flex_volume": band_cols + ns_year_cols + core[1:] + cat_cols,
           "Q3_categories": core[:1] + ns_year_cols + core[1:] + cat_cols,
           "Q1_core": ["log_n_active"]+ns_year_cols+["weight_c"],
           "Q0_flex_year": ["log_n_active"]+ns_year_cols}
    y_adj=est["adj_mean"].to_numpy(float)
    n_obs=est["n_obs"].to_numpy(float)
    log_n=est["log_n_active"].to_numpy(float)
    weightings={"ols":np.ones(len(est)), "wls_n":n_obs.copy()}
    designs={name: np.column_stack([np.ones(len(est))]+[est[c].to_numpy(float) for c in cols]) for name,cols in specs.items()}
    col_names={name: ["intercept"]+cols for name,cols in specs.items()}
    results=[]
    resid_store={}
    for spec_name,X in designs.items():
        cn=col_names[spec_name]
        for wt_name,w in [("ols",weightings["ols"]),("wls_n",weightings["wls_n"])]:
            beta,pred,resid=fit_wls(X,y_adj,w)
            cv_pred,cv_resid,fb,fi=cv_predictions(X,y_adj,w)
            m_in=metrics(y_adj,resid)
            fold_stats=[metrics(y_adj[ix], cv_resid[ix]) for ix in fi]
            bi=dict(zip(cn,beta))
            vi=cn.index("log_n_active") if "log_n_active" in cn else None
            row={"spec":spec_name,"weighting":wt_name,"target":"adj","n_games":int(len(y_adj)),"n_features":int(X.shape[1]),
                 "r2_in":m_in["r2"],"rmse_in":m_in["rmse"],"cv_r2_mean":float(np.mean([f["r2"] for f in fold_stats])),"cv_r2_sd":float(np.std([f["r2"] for f in fold_stats])),
                 "beta_logn":bi.get("log_n_active"),"beta_weight":bi.get("weight_c"),"corr_resid_logn":float(np.corrcoef(resid,log_n)[0,1]) if len(resid)>1 else float("nan")}
            results.append(row)
            resid_store[f"{spec_name}|{wt_name}"]={"resid":resid,"pred":pred,"beta":beta}
    return pd.DataFrame(results), resid_store, est

def phase5_metrics(con, gm_view, sev_view, ro_view, pop_view, mu):
    var_resid=con.execute(f"SELECT VAR_SAMP(r.rating - g.adj_mean - s.delta_full) FROM {ro_view} r JOIN {gm_view} g USING (game_id) JOIN {sev_view} s USING (user_pseudouserid)").fetchone()[0]
    sigma_e2=float(var_resid); sigma_e=float(np.sqrt(sigma_e2))
    var_adj, mean_adj=con.execute(f"SELECT VAR_SAMP(adj_mean), AVG(adj_mean) FROM {gm_view}").fetchone()
    var_adj=float(var_adj)
    mean_inv_n=float(con.execute(f"SELECT AVG(1.0/n_obs) FROM {gm_view}").fetchone()[0])
    harm_n=float(1/mean_inv_n) if mean_inv_n else None
    sigma_alpha2_mm=float(max(var_adj - sigma_e2*mean_inv_n,1e-6))
    lambda_mm=float(sigma_e2/sigma_alpha2_mm)
    # held-out even/odd
    mu_val=float(mu)
    held=con.execute(f"""
        WITH half_raw AS (SELECT game_id, (rating_observation_id%2) parity, AVG(rating) raw_half, COUNT(*) n_half FROM {ro_view} GROUP BY game_id, parity),
             half_adj AS (SELECT game_id, (rating_observation_id%2) parity, AVG(r.rating - s.delta_full) adj_half, COUNT(*) n_half FROM {ro_view} r JOIN {sev_view} s USING (user_pseudouserid) GROUP BY game_id, parity),
             piv AS (SELECT game_id, MAX(CASE WHEN parity=0 THEN raw_half END) raw_even, MAX(CASE WHEN parity=1 THEN raw_half END) raw_odd, MAX(CASE WHEN parity=0 THEN adj_half END) adj_even, MAX(CASE WHEN parity=1 THEN adj_half END) adj_odd, MAX(CASE WHEN parity=0 THEN n_half END) n_even FROM (SELECT hr.game_id, hr.parity, hr.raw_half, ha.adj_half, hr.n_half FROM half_raw hr JOIN half_adj ha USING (game_id,parity)) GROUP BY game_id HAVING COUNT(*)=2),
             j AS (SELECT p.*, pop.bayes_rating bayes, ({mu_val}*{lambda_mm}+p.n_even*p.adj_even)/(p.n_even+{lambda_mm}) shrunk_even FROM piv p JOIN {pop_view} pop USING (game_id))
        SELECT COUNT(*), CORR(adj_even,adj_odd), CORR(shrunk_even,adj_odd), CORR(bayes,adj_odd), AVG(adj_even-adj_odd), AVG(shrunk_even-adj_odd), SQRT(AVG((adj_even-adj_odd)*(adj_even-adj_odd))), SQRT(AVG((shrunk_even-adj_odd)*(shrunk_even-adj_odd))), VAR_SAMP(adj_odd) FROM j
    """).fetchone()
    n_both, corr_adj, corr_shrunk, corr_bayes, bias_adj, bias_shrunk, rmse_adj, rmse_shrunk, var_adj_odd=held
    return {"var_adj":var_adj,"sigma_e":sigma_e,"sigma_e2":sigma_e2,"sigma_alpha2_mm":sigma_alpha2_mm,"lambda_mm":lambda_mm,"n_games":int(con.execute(f"SELECT COUNT(*) FROM {gm_view}").fetchone()[0]), "held_out":{"corr_adj":corr_adj,"rmse_adj":rmse_adj,"var_adj_odd":var_adj_odd}}

def main():
    out_dir=REPO/"data/processed/phase2-second-pass"
    tmp_dir=REPO/"scratch/ducktmp"
    scratch=REPO/"scratch/second-pass"
    # ensure scratch copy exists
    for fn in ["bgg_research_population.parquet","rating_observations_active.parquet","game_adjusted_means_active.parquet","user_severity_active.parquet"]:
        if not (scratch/fn).exists():
            src=REPO/"data/processed/phase2-active"/fn if "active" in fn else REPO/"data/processed/bgg_research_population.parquet"
            if src.exists(): shutil.copy2(src, scratch/fn)
    active_dir=scratch
    pop_path=scratch/"bgg_research_population.parquet"
    ro_path=active_dir/"rating_observations_active.parquet"
    gm_path=active_dir/"game_adjusted_means_active.parquet"
    sev_path=active_dir/"user_severity_active.parquet"
    links_path=REPO/"data/processed/phase2-filtered/game_links_filtered.parquet"
    con=duckdb.connect(); configure(con, tmp_dir)
    # Views for full
    con.execute(f"CREATE OR REPLACE VIEW ro_full AS SELECT * FROM read_parquet('{qpath(ro_path)}')")
    con.execute(f"CREATE OR REPLACE VIEW gm_full AS SELECT * FROM read_parquet('{qpath(gm_path)}')")
    con.execute(f"CREATE OR REPLACE VIEW sev AS SELECT * FROM read_parquet('{qpath(sev_path)}')")
    con.execute(f"CREATE OR REPLACE VIEW pop AS SELECT * FROM read_parquet('{qpath(pop_path)}')")
    mu=float(con.execute("SELECT AVG(rating) FROM ro_full").fetchone()[0])
    print(f"mu {mu}")
    # Game lists for universes
    current_games = set(pd.read_parquet(gm_path)["game_id"].tolist())  # 16564
    primary_closed_games = set(pd.read_csv(out_dir/"primary_final_games.csv")["game_id"].tolist())
    base_closed_games = set(pd.read_csv(out_dir/"base_16627_final_games.csv")["game_id"].tolist())
    primary_before_games = set(pd.read_parquet(out_dir/"bgg_population_second_pass.parquet")["game_id"].tolist())
    print(f"current {len(current_games)} primary_before {len(primary_before_games)} primary_closed {len(primary_closed_games)} base_closed {len(base_closed_games)}")
    # Create filtered GM views per universe: need to handle gm_full filtered to those game_ids
    # For duckdb, create temp tables of game ids then SEMI JOIN
    def create_gm_view(view_name, game_ids):
        con.execute(f"DROP TABLE IF EXISTS tmp_{view_name}")
        con.execute(f"CREATE TEMP TABLE tmp_{view_name} (game_id BIGINT)")
        ids=list(game_ids)
        for i in range(0,len(ids),1000):
            chunk=ids[i:i+1000]
            vals=",".join(f"({x})" for x in chunk)
            con.execute(f"INSERT INTO tmp_{view_name} VALUES {vals}")
        con.execute(f"CREATE OR REPLACE VIEW {view_name} AS SELECT g.* FROM gm_full g SEMI JOIN tmp_{view_name} t USING (game_id)")
        # also create ro view filtered to those games and to active users? For phase5, ro should be filtered to those games only (and not deg? But active already excludes deg)
        con.execute(f"CREATE OR REPLACE VIEW ro_{view_name} AS SELECT r.* FROM ro_full r SEMI JOIN tmp_{view_name} t USING (game_id)")
    create_gm_view("gm_current", current_games)
    create_gm_view("gm_primary_before", primary_before_games)
    create_gm_view("gm_primary_closed", primary_closed_games)
    create_gm_view("gm_base_closed", base_closed_games)
    # Phase5 per universe
    print("\n=== Phase5 ===")
    p5_current=phase5_metrics(con,"gm_current","sev","ro_gm_current","pop",mu)
    p5_primary_before=phase5_metrics(con,"gm_primary_before","sev","ro_gm_primary_before","pop",mu)
    p5_primary_closed=phase5_metrics(con,"gm_primary_closed","sev","ro_gm_primary_closed","pop",mu)
    p5_base_closed=phase5_metrics(con,"gm_base_closed","sev","ro_gm_base_closed","pop",mu)
    for label,d in [("current",p5_current),("primary_before",p5_primary_before),("primary_closed",p5_primary_closed),("base_closed",p5_base_closed)]:
        print(f"{label}: n_games {d['n_games']} var_adj {d['var_adj']:.4f} sigma_e {d['sigma_e']:.4f} lambda {d['lambda_mm']:.2f} rmse_adj {d['held_out']['rmse_adj']:.4f}")
    # Phase6: need est samples
    print("\n=== Phase6 ===")
    # Load pop as df for est building
    pop_df=pd.read_parquet(pop_path)
    def load_gam_for_games(game_ids):
        gm_df=pd.read_parquet(gm_path)
        return gm_df[gm_df["game_id"].isin(game_ids)].reset_index(drop=True)
    est_current,_=build_estimation_sample(load_gam_for_games(current_games), pop_df, links_path)
    est_primary_before,_=build_estimation_sample(load_gam_for_games(primary_before_games), pop_df, links_path)
    est_primary_closed,_=build_estimation_sample(load_gam_for_games(primary_closed_games), pop_df, links_path)
    est_base_closed,_=build_estimation_sample(load_gam_for_games(base_closed_games), pop_df, links_path)
    print(f"est sizes: current {len(est_current)} primary_before {len(est_primary_before)} primary_closed {len(est_primary_closed)} base_closed {len(est_base_closed)}")
    # Fit preferred
    res_current, store_current, _=fit_phase6_for_est(est_current.copy(), mu, p5_current["sigma_e"], p5_current["sigma_alpha2_mm"])
    res_primary_before, store_primary_before, _=fit_phase6_for_est(est_primary_before.copy(), mu, p5_primary_before["sigma_e"], p5_primary_before["sigma_alpha2_mm"])
    res_primary_closed, store_primary_closed, _=fit_phase6_for_est(est_primary_closed.copy(), mu, p5_primary_closed["sigma_e"], p5_primary_closed["sigma_alpha2_mm"])
    res_base_closed, store_base_closed, _=fit_phase6_for_est(est_base_closed.copy(), mu, p5_base_closed["sigma_e"], p5_base_closed["sigma_alpha2_mm"])
    # Extract preferred Q3b OLS
    def pref_row(df):
        r=df[(df.spec=="Q3b_flex_volume")&(df.weighting=="ols")]
        return r.iloc[0].to_dict() if len(r) else None
    for label,df in [("current",res_current),("primary_before",res_primary_before),("primary_closed",res_primary_closed),("base_closed",res_base_closed)]:
        pr=pref_row(df)
        print(f"{label} Q3b/OLS R2_in {pr['r2_in']:.4f} cv {pr['cv_r2_mean']:.4f} beta_weight {pr['beta_weight']:.4f} beta_logn {pr['beta_logn']}")
    # Residual distribution and rank stability on overlap
    # Overlap between current and primary_closed
    # Need to align game_ids for overlapping games
    def overlap_metrics(est_a, store_a, est_b, store_b, label):
        key="Q3b_flex_volume|ols"
        resid_a=store_a[key]["resid"]; resid_b=store_b[key]["resid"]
        df_a=pd.DataFrame({"game_id":est_a["game_id"],"resid_a":resid_a})
        df_b=pd.DataFrame({"game_id":est_b["game_id"],"resid_b":resid_b})
        merged=df_a.merge(df_b, on="game_id", how="inner")
        if len(merged)<10:
            return {"n_overlap":len(merged)}
        pear=float(np.corrcoef(merged["resid_a"], merged["resid_b"])[0,1])
        spear=float(pd.Series(merged["resid_a"]).corr(pd.Series(merged["resid_b"]), method="spearman"))
        # Jaccard top1% on overlap
        k1=max(1,int(0.01*len(merged))); k5=max(1,int(0.05*len(merged)))
        sa=set(np.argsort(merged["resid_a"].to_numpy())[-k1:]); sb=set(np.argsort(merged["resid_b"].to_numpy())[-k1:])
        jac1=len(sa&sb)/len(sa|sb) if len(sa|sb) else 0
        sa5=set(np.argsort(merged["resid_a"].to_numpy())[-k5:]); sb5=set(np.argsort(merged["resid_b"].to_numpy())[-k5:])
        jac5=len(sa5&sb5)/len(sa5|sb5)
        # cross-universe top sets (including non-overlap)
        top_a=set(df_a.nlargest(max(1,int(0.01*len(df_a))),"resid_a")["game_id"])
        top_b=set(df_b.nlargest(max(1,int(0.01*len(df_b))),"resid_b")["game_id"])
        jac_cross=len(top_a&top_b)/len(top_a|top_b) if len(top_a|top_b) else 0
        return {"label":label,"n_overlap":int(len(merged)),"pearson":pear,"spearman":spear,"jaccard_top1_overlap":jac1,"jaccard_top5_overlap":jac5,"jaccard_cross_top1":jac_cross, "k1":k1}
    print("\nOverlap current vs primary_closed", overlap_metrics(est_current, store_current, est_primary_closed, store_primary_closed, "current_vs_primary_closed"))
    print("Overlap current vs base_closed", overlap_metrics(est_current, store_current, est_base_closed, store_base_closed, "current_vs_base_closed"))
    print("Overlap primary_closed vs base_closed", overlap_metrics(est_primary_closed, store_primary_closed, est_base_closed, store_base_closed, "primary_closed_vs_base_closed"))
    # Top residuals
    def top_df(est, store, n=20):
        resid=store["Q3b_flex_volume|ols"]["resid"]; pred=store["Q3b_flex_volume|ols"]["pred"]
        df=pd.DataFrame({"game_id":est["game_id"],"title":est["title"],"year":est["year"],"n_obs":est["n_obs"],"users_rated":est["users_rated"],"adj_mean":est["adj_mean"],"pred":pred,"resid":resid})
        return df.nlargest(n,"resid")
    for label,est,store in [("current",est_current,store_current),("primary_closed",est_primary_closed,store_primary_closed),("base_closed",est_base_closed,store_base_closed)]:
        print(f"\nTop 10 {label}")
        print(top_df(est,store,10).to_string(index=False))
    # Save outputs
    comp={
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
        "phase5":{"current":p5_current,"primary_before":p5_primary_before,"primary_closed":p5_primary_closed,"base_closed":p5_base_closed},
        "phase6":{
            "current": pref_row(res_current),
            "primary_before": pref_row(res_primary_before),
            "primary_closed": pref_row(res_primary_closed),
            "base_closed": pref_row(res_base_closed),
            "full_current": res_current.to_dict(orient="records"),
            "full_primary_closed": res_primary_closed.to_dict(orient="records"),
        },
        "overlap":{
            "current_vs_primary_closed": overlap_metrics(est_current, store_current, est_primary_closed, store_primary_closed, "current_vs_primary_closed"),
            "current_vs_base_closed": overlap_metrics(est_current, store_current, est_base_closed, store_base_closed, "current_vs_base_closed"),
        }
    }
    # Write json
    with open(out_dir/"model_comparison.json","w") as f: json.dump(comp,f,indent=2,default=str)
    # Write csvs
    res_current.to_csv(out_dir/"phase6_current.csv",index=False)
    res_primary_closed.to_csv(out_dir/"phase6_primary_closed.csv",index=False)
    res_base_closed.to_csv(out_dir/"phase6_base_closed.csv",index=False)
    top_df(est_current,store_current,50).to_csv(out_dir/"top50_current.csv",index=False)
    top_df(est_primary_closed,store_primary_closed,50).to_csv(out_dir/"top50_primary_closed.csv",index=False)
    top_df(est_base_closed,store_base_closed,50).to_csv(out_dir/"top50_base_closed.csv",index=False)
    # Also save residual distributions
    for label,est,store in [("current",est_current,store_current),("primary_closed",est_primary_closed,store_primary_closed)]:
        resid=store["Q3b_flex_volume|ols"]["resid"]
        pd.DataFrame({"resid":resid}).to_csv(out_dir/f"residuals_{label}.csv",index=False)
    print("\nWrote model_comparison.json and csvs")
    con.close()

if __name__=="__main__":
    main()

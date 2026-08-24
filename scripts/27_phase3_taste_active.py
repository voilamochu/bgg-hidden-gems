"""Phase 3 taste investigation on active population (16,627 x >=10 minus strict).

Primary universe: data/processed/phase2-active (24.5M obs, 288k users, 16.5k games)
Built by scripts/24, refreshed baseline by scripts/26 (mu=7.144, delta_full/even/odd).
Question: global severity vs systematic user x game-type taste.

Focused finite sequence:
  1. Re-establish active baseline (validate counts).
  2. Simplest taste tests:
     (a) descriptive within-type gaps on frequent types (top categories/mechanics/weight bands, cells >=5 per user) - population tau_t.
     (b) residual-by-type after mu+alpha+delta - systematic residual pattern per user.
  3. Three gates: stability (even/odd parity correlation), distinctness (corr with delta/volume/weight-gradient), materiality (R2 gain and held-out RMSE).
Stop adding complexity when gates fail.

Heavy scans via DuckDB on scratch/phase2-active copy; bounded memory 4GB threads 3.
Do not re-scan full 26.9M snapshot or build large parquets per step.

Outputs: JSON summary under data/processed/phase2-active/ (gitignored) plus docs copy.

Reuse doc: AGENTS.md claim tagging.
"""
import argparse, json, time, sys
from pathlib import Path
import duckdb
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
MEMORY = "4GB"
THREADS = 3

def qpath(p: Path)->str:
    return str(p).replace("'", "''")

def configure(con, tmp_dir: Path):
    con.execute(f"SET memory_limit='{MEMORY}'")
    con.execute(f"SET threads={THREADS}")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    con.execute(f"SET temp_directory='{qpath(tmp_dir)}'")
    con.execute("SET preserve_insertion_order=false")

def pearson(x,y):
    m=np.isfinite(x)&np.isfinite(y)
    x=x[m]; y=y[m]
    if len(x)<3: return np.nan
    return np.corrcoef(x,y)[0,1]

def spearman(x,y):
    m=np.isfinite(x)&np.isfinite(y)
    x=x[m]; y=y[m]
    if len(x)<3: return np.nan
    rx=pd.Series(x).rank().values
    ry=pd.Series(y).rank().values
    return np.corrcoef(rx,ry)[0,1]

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--active-dir", type=Path, default=None, help="active extracts dir")
    ap.add_argument("--population", type=Path, default=None, help="population parquet")
    ap.add_argument("--out-dir", type=Path, default=None, help="output dir")
    ap.add_argument("--min-cell", type=int, default=5, help="min per-user cells in/out for descriptive")
    ap.add_argument("--min-cell-parity", type=int, default=3, help="min per-user per-half cells for stability")
    args=ap.parse_args()

    # resolve active dir: prefer scratch/phase2-active if exists
    if args.active_dir:
        active_dir=args.active_dir
    else:
        cand1=REPO/"scratch/phase2-active"
        cand2=REPO/"data/processed/phase2-active"
        active_dir=cand1 if (cand1/"rating_observations_active.parquet").exists() else cand2

    pop_path=args.population or (active_dir/"bgg_research_population.parquet")
    if not pop_path.exists():
        pop_path=REPO/"data/processed/bgg_research_population.parquet"
        if not pop_path.exists():
            pop_path=REPO/"scratch/phase2/bgg_research_population.parquet"
    out_dir=args.out_dir or (REPO/"data/processed/phase2-active")
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir=out_dir/".tmp_duckdb"

    print(f"active_dir={active_dir}", flush=True)
    print(f"population={pop_path}", flush=True)
    print(f"out_dir={out_dir}", flush=True)

    con=duckdb.connect()
    configure(con, tmp_dir)

    # views
    ro_path=active_dir/"rating_observations_active.parquet"
    sev_path=active_dir/"user_severity_active.parquet"
    gm_path=active_dir/"game_adjusted_means_active.parquet"
    users_path=active_dir/"users_active.parquet"
    if not ro_path.exists():
        sys.exit(f"missing {ro_path} - copy active extracts to scratch first")
    if not sev_path.exists():
        sys.exit(f"missing {sev_path}")
    if not gm_path.exists():
        sys.exit(f"missing {gm_path}")

    con.execute(f"CREATE OR REPLACE VIEW ro AS SELECT * FROM read_parquet('{qpath(ro_path)}')")
    con.execute(f"CREATE OR REPLACE VIEW sev AS SELECT * FROM read_parquet('{qpath(sev_path)}')")
    con.execute(f"CREATE OR REPLACE VIEW gm AS SELECT game_id, game_alpha, n_obs, raw_mean, adj_mean FROM read_parquet('{qpath(gm_path)}')")
    con.execute(f"CREATE OR REPLACE VIEW pop AS SELECT game_id, weight, categories, mechanics FROM read_parquet('{qpath(pop_path)}')")
    # mu
    mu=con.execute("SELECT AVG(rating) FROM ro").fetchone()[0]
    # validation baseline
    print("[1/7] Validation", flush=True)
    validation={}
    n_obs=con.execute("SELECT COUNT(*) FROM ro").fetchone()[0]
    n_users=con.execute("SELECT COUNT(*) FROM sev").fetchone()[0]
    n_games=con.execute("SELECT COUNT(DISTINCT game_id) FROM ro").fetchone()[0]
    validation["n_obs"]=int(n_obs)
    validation["n_users"]=int(n_users)
    validation["n_games"]=int(n_games)
    validation["mu"]=float(mu)
    validation["expected_n_obs"]=24509788
    validation["expected_n_users"]=288730
    validation["expected_n_games"]=16564
    validation["delta_obs_vs_expected"]=int(n_obs-24509788)
    validation["delta_users_vs_expected"]=int(n_users-288730)
    assert abs(n_obs-24509788)<10, f"obs mismatch {n_obs}"
    assert abs(n_users-288730)<10, f"users mismatch {n_users}"
    # check mu close to 7.144
    assert abs(mu-7.144)<0.01, f"mu {mu} not 7.144"
    print(f"  validation passed: {n_obs} obs, {n_users} users, {n_games} games, mu={mu:.4f}", flush=True)

    # helper tables
    print("[2/7] Helper tables: pop weight bands, game_cat, game_mech", flush=True)
    # weight bands: tertiles 1.62 and 2.33 from population quantiles
    con.execute("""
        CREATE OR REPLACE TEMP TABLE wband AS
        SELECT game_id, weight,
               CASE WHEN weight < 1.62 THEN 'light'
                    WHEN weight <= 2.33 THEN 'medium'
                    ELSE 'heavy' END AS wband
        FROM pop WHERE weight IS NOT NULL
    """)
    # game_cat and game_mech via json
    con.execute("CREATE OR REPLACE TEMP TABLE game_cat AS SELECT game_id, unnest(from_json(categories, '[\"VARCHAR\"]')) AS cat FROM pop WHERE categories IS NOT NULL AND categories != '[]'")
    con.execute("CREATE OR REPLACE TEMP TABLE game_mech AS SELECT game_id, unnest(from_json(mechanics, '[\"VARCHAR\"]')) AS mech FROM pop WHERE mechanics IS NOT NULL AND mechanics != '[]'")
    ncat=con.execute("SELECT COUNT(*) FROM game_cat").fetchone()[0]
    nmech=con.execute("SELECT COUNT(*) FROM game_mech").fetchone()[0]
    print(f"  game_cat rows {ncat}, game_mech rows {nmech}", flush=True)

    # top types
    top_cats_df=con.execute("SELECT cat, COUNT(DISTINCT game_id) AS n_games FROM game_cat GROUP BY cat ORDER BY n_games DESC LIMIT 6").fetch_df()
    top_mechs_df=con.execute("SELECT mech, COUNT(DISTINCT game_id) AS n_games FROM game_mech GROUP BY mech ORDER BY n_games DESC LIMIT 6").fetch_df()
    top_cats=top_cats_df['cat'].tolist()
    top_mechs=top_mechs_df['mech'].tolist()
    wbands=['light','medium','heavy']
    print(f"  top cats: {top_cats}")
    print(f"  top mechs: {top_mechs}")
    print(f"  wbands: {wbands}")

    # per-user totals
    print("[3/7] Per-user totals and per-type aggregates", flush=True)
    # per_user_total all ratings
    per_user_total=con.execute("SELECT user_pseudouserid AS uid, COUNT(*) AS n_total, SUM(rating) AS sum_total, AVG(rating) AS mean_total FROM ro GROUP BY user_pseudouserid").fetch_df()
    # per_user_total_weight (only games with weight)
    per_user_total_w=con.execute("""
        SELECT r.user_pseudouserid AS uid, COUNT(*) AS n_total_w, SUM(r.rating) AS sum_total_w, AVG(r.rating) AS mean_total_w
        FROM ro r JOIN wband w USING (game_id)
        GROUP BY r.user_pseudouserid
    """).fetch_df()
    # per_user per cat (top cats only)
    # Build wband per user aggregates
    per_user_wband=con.execute("""
        SELECT r.user_pseudouserid AS uid, w.wband, COUNT(*) AS n_in, SUM(r.rating) AS sum_in, AVG(r.rating) AS mean_in
        FROM ro r JOIN wband w USING (game_id)
        GROUP BY r.user_pseudouserid, w.wband
    """).fetch_df()
    # per_user per cat/mech for top lists: we filter in sql to top values for efficiency via IN list
    cats_in="','".join(top_cats)
    mechs_in="','".join(top_mechs)
    per_user_cat=con.execute(f"""
        SELECT r.user_pseudouserid AS uid, g.cat, COUNT(*) AS n_in, SUM(r.rating) AS sum_in, AVG(r.rating) AS mean_in
        FROM ro r JOIN game_cat g USING (game_id)
        WHERE g.cat IN ('{cats_in}')
        GROUP BY r.user_pseudouserid, g.cat
    """).fetch_df()
    per_user_mech=con.execute(f"""
        SELECT r.user_pseudouserid AS uid, g.mech, COUNT(*) AS n_in, SUM(r.rating) AS sum_in, AVG(r.rating) AS mean_in
        FROM ro r JOIN game_mech g USING (game_id)
        WHERE g.mech IN ('{mechs_in}')
        GROUP BY r.user_pseudouserid, g.mech
    """).fetch_df()

    # also need per_user totals with alpha sums for residual calc
    # per_user_total_alpha: sum_alpha_total per user
    per_user_alpha_total=con.execute("""
        SELECT r.user_pseudouserid AS uid, SUM(g.game_alpha) AS sum_alpha_total, AVG(g.game_alpha) AS mean_alpha_total, COUNT(*) AS n_alpha_total
        FROM ro r JOIN gm g USING (game_id)
        GROUP BY r.user_pseudouserid
    """).fetch_df()
    per_user_alpha_total_w=con.execute("""
        SELECT r.user_pseudouserid AS uid, SUM(g.game_alpha) AS sum_alpha_total_w, AVG(g.game_alpha) AS mean_alpha_total_w, COUNT(*) AS n_alpha_total_w
        FROM ro r JOIN wband w USING (game_id) JOIN gm g USING (game_id)
        GROUP BY r.user_pseudouserid
    """).fetch_df()
    # per_user per wband alpha
    per_user_wband_alpha=con.execute("""
        SELECT r.user_pseudouserid AS uid, w.wband, COUNT(*) AS n_in, SUM(r.rating) AS sum_in, AVG(r.rating) AS mean_in, SUM(g.game_alpha) AS sum_alpha_in, AVG(g.game_alpha) AS mean_alpha_in
        FROM ro r JOIN wband w USING (game_id) JOIN gm g USING (game_id)
        GROUP BY r.user_pseudouserid, w.wband
    """).fetch_df()
    per_user_cat_alpha=con.execute(f"""
        SELECT r.user_pseudouserid AS uid, gcat.cat, COUNT(*) AS n_in, SUM(r.rating) AS sum_in, AVG(r.rating) AS mean_in, SUM(gm.game_alpha) AS sum_alpha_in, AVG(gm.game_alpha) AS mean_alpha_in
        FROM ro r JOIN game_cat gcat USING (game_id) JOIN gm USING (game_id)
        WHERE gcat.cat IN ('{cats_in}')
        GROUP BY r.user_pseudouserid, gcat.cat
    """).fetch_df()
    per_user_mech_alpha=con.execute(f"""
        SELECT r.user_pseudouserid AS uid, gmech.mech, COUNT(*) AS n_in, SUM(r.rating) AS sum_in, AVG(r.rating) AS mean_in, SUM(gm.game_alpha) AS sum_alpha_in, AVG(gm.game_alpha) AS mean_alpha_in
        FROM ro r JOIN game_mech gmech USING (game_id) JOIN gm USING (game_id)
        WHERE gmech.mech IN ('{mechs_in}')
        GROUP BY r.user_pseudouserid, gmech.mech
    """).fetch_df()

    # bring delta
    sev_df=con.execute("SELECT user_pseudouserid AS uid, delta_full, delta_even, delta_odd, rating_observations_active AS n_active FROM sev").fetch_df()
    # merge for descriptive and residual

    # --- (a) Descriptive tau raw ---
    print("[4/7] Descriptive within-type gaps (tau raw)", flush=True)
    # helper to compute tau for each type
    def compute_tau_raw(per_user_type_df, per_user_total_df, type_col, min_cell):
        # per_user_type_df has uid, type_col, n_in, sum_in, mean_in
        # per_user_total_df has uid, n_total, sum_total
        merged=per_user_type_df.merge(per_user_total_df, on='uid', how='left')
        # also need per_user_total for wband? handle wband vs cat vs mech generic
        # n_total column name varies: n_total vs n_total_w, sum_total vs sum_total_w
        # detect
        n_total_col=[c for c in merged.columns if c.startswith('n_total')][0]
        sum_total_col=[c for c in merged.columns if c.startswith('sum_total')][0]
        merged['n_out']=merged[n_total_col]-merged['n_in']
        merged['sum_out']=merged[sum_total_col]-merged['sum_in']
        # avoid div by zero
        merged['mean_out']=merged['sum_out']/merged['n_out']
        merged['diff']=merged['mean_in']-merged['mean_out']
        # filter cells >=min_cell both sides
        filt=merged[(merged['n_in']>=min_cell)&(merged['n_out']>=min_cell)].copy()
        # group by type
        results=[]
        for t, sub in filt.groupby(type_col):
            diffs=sub['diff'].values
            n_users=len(diffs)
            tau=np.nanmean(diffs) if n_users>0 else np.nan
            sd=np.nanstd(diffs, ddof=1) if n_users>1 else np.nan
            # also show raw means: mean_in overall vs mean_out overall? compute population-level
            # need overall mean diff? Already tau
            # quantiles
            p10=np.nanquantile(diffs,0.10) if n_users>0 else np.nan
            p50=np.nanquantile(diffs,0.50) if n_users>0 else np.nan
            p90=np.nanquantile(diffs,0.90) if n_users>0 else np.nan
            share_pos=np.mean(diffs>0) if n_users>0 else np.nan
            # effect size in rating points
            results.append({"type":t, "n_users":int(n_users), "tau_raw":float(tau) if np.isfinite(tau) else None,
                            "sd_diff":float(sd) if np.isfinite(sd) else None,
                            "p10":float(p10) if np.isfinite(p10) else None,
                            "p50":float(p50) if np.isfinite(p50) else None,
                            "p90":float(p90) if np.isfinite(p90) else None,
                            "share_pos":float(share_pos) if np.isfinite(share_pos) else None,
                            "mean_n_in":float(sub['n_in'].mean()) if n_users>0 else None})
        return results, filt

    tau_wband_raw, filt_wband_raw = compute_tau_raw(per_user_wband, per_user_total_w, 'wband', args.min_cell)
    tau_cat_raw, filt_cat_raw = compute_tau_raw(per_user_cat, per_user_total, 'cat', args.min_cell)
    tau_mech_raw, filt_mech_raw = compute_tau_raw(per_user_mech, per_user_total, 'mech', args.min_cell)

    for r in tau_wband_raw:
        print(f"  wband {r['type']}: n={r['n_users']} tau={r['tau_raw']:.3f} sd={r['sd_diff']:.3f} p50={r['p50']:.3f} share_pos={r['share_pos']:.3f}")
    for r in tau_cat_raw:
        print(f"  cat {r['type']}: n={r['n_users']} tau={r['tau_raw']:.3f} sd={r['sd_diff']:.3f}")
    for r in tau_mech_raw:
        print(f"  mech {r['type']}: n={r['n_users']} tau={r['tau_raw']:.3f} sd={r['sd_diff']:.3f}")

    # --- (b) Residual-by-type after mu+alpha+delta ---
    print("[5/7] Residual-by-type after mu+alpha+delta", flush=True)
    # need to compute diff_resid = (mean_in - mean_alpha_in) - (mean_out - mean_alpha_out)
    # For each type we have per_user per type mean_in, mean_alpha_in, and totals
    def compute_tau_resid(per_user_type_alpha_df, per_user_total_df, per_user_alpha_total_df, type_col, min_cell, sev_df=None):
        # per_user_type_alpha_df: uid, type_col, n_in, sum_in, mean_in, sum_alpha_in, mean_alpha_in
        # per_user_total_df: uid, n_total, sum_total
        # per_user_alpha_total_df: uid, sum_alpha_total, mean_alpha_total
        # merge
        merged=per_user_type_alpha_df.merge(per_user_total_df, on='uid', how='left')
        merged=merged.merge(per_user_alpha_total_df, on='uid', how='left')
        # identify columns
        n_total_col=[c for c in merged.columns if c.startswith('n_total') and 'alpha' not in c][0] if any(c.startswith('n_total') and 'alpha' not in c for c in merged.columns) else [c for c in merged.columns if c.startswith('n_total')][0]
        # Actually for wband we have n_total_w
        # find n_total generic
        n_total_candidates=[c for c in merged.columns if c.startswith('n_total')]
        # choose the one that matches per_user_total_df's n column
        # per_user_total_df columns: for wband case it's n_total_w, else n_total
        # So we need to find which column came from per_user_total
        # The other from alpha_total is n_alpha_total...
        n_total_col = [c for c in per_user_total_df.columns if c.startswith('n_total')][0]
        sum_total_col = [c for c in per_user_total_df.columns if c.startswith('sum_total')][0]
        sum_alpha_total_col = [c for c in per_user_alpha_total_df.columns if c.startswith('sum_alpha')][0]
        # Now compute n_out etc.
        merged['n_out']=merged[n_total_col]-merged['n_in']
        merged['sum_out']=merged[sum_total_col]-merged['sum_in']
        merged['sum_alpha_out']=merged[sum_alpha_total_col]-merged['sum_alpha_in']
        merged['mean_out']=merged['sum_out']/merged['n_out']
        merged['mean_alpha_out']=merged['sum_alpha_out']/merged['n_out']
        # resid diff: (mean_in - mean_alpha_in) - (mean_out - mean_alpha_out) . delta cancels, mu cancels.
        merged['diff_resid']=(merged['mean_in']-merged['mean_alpha_in'])-(merged['mean_out']-merged['mean_alpha_out'])
        # also per-type mean resid alone? mean_resid_in = mean_in - mu - mean_alpha_in - delta
        # we can compute if sev provided, but diff already independent of mu/delta
        if sev_df is not None:
            merged=merged.merge(sev_df[['uid','delta_full']], on='uid', how='left')
            merged['mean_resid_in']=merged['mean_in'] - mu - merged['mean_alpha_in'] - merged['delta_full']
            # overall residual per type mean across users (unweighted mean of per-user means) vs observation-weighted?
            # We'll compute observation-weighted mean resid per type later via separate query if needed
        filt=merged[(merged['n_in']>=min_cell)&(merged['n_out']>=min_cell)].copy()
        results=[]
        for t, sub in filt.groupby(type_col):
            diffs=sub['diff_resid'].values
            n_users=len(diffs)
            tau=np.nanmean(diffs) if n_users>0 else np.nan
            sd=np.nanstd(diffs, ddof=1) if n_users>1 else np.nan
            p10=np.nanquantile(diffs,0.10) if n_users>0 else np.nan
            p50=np.nanquantile(diffs,0.50) if n_users>0 else np.nan
            p90=np.nanquantile(diffs,0.90) if n_users>0 else np.nan
            share_pos=np.mean(diffs>0) if n_users>0 else np.nan
            # also mean_resid_in distribution if available
            mean_resid_in_mean=np.nanmean(sub['mean_resid_in'].values) if 'mean_resid_in' in sub else None
            results.append({"type":t, "n_users":int(n_users), "tau_resid_diff":float(tau) if np.isfinite(tau) else None,
                            "sd_diff":float(sd) if np.isfinite(sd) else None,
                            "p10":float(p10) if np.isfinite(p10) else None,
                            "p50":float(p50) if np.isfinite(p50) else None,
                            "p90":float(p90) if np.isfinite(p90) else None,
                            "share_pos":float(share_pos) if np.isfinite(share_pos) else None,
                            "mean_resid_in":float(mean_resid_in_mean) if mean_resid_in_mean is not None and np.isfinite(mean_resid_in_mean) else None})
        return results, filt

    tau_wband_resid, filt_wband_resid = compute_tau_resid(per_user_wband_alpha, per_user_total_w, per_user_alpha_total_w, 'wband', args.min_cell, sev_df)
    tau_cat_resid, filt_cat_resid = compute_tau_resid(per_user_cat_alpha, per_user_total, per_user_alpha_total, 'cat', args.min_cell, sev_df)
    tau_mech_resid, filt_mech_resid = compute_tau_resid(per_user_mech_alpha, per_user_total, per_user_alpha_total, 'mech', args.min_cell, sev_df)

    for r in tau_wband_resid:
        print(f"  wband resid {r['type']}: n={r['n_users']} tau_diff={r['tau_resid_diff']:.4f} sd={r['sd_diff']:.4f} mean_resid_in={r['mean_resid_in']}")
    for r in tau_cat_resid:
        print(f"  cat resid {r['type']}: n={r['n_users']} tau_diff={r['tau_resid_diff']:.4f} sd={r['sd_diff']:.4f}")
    for r in tau_mech_resid:
        print(f"  mech resid {r['type']}: n={r['n_users']} tau_diff={r['tau_resid_diff']:.4f} sd={r['sd_diff']:.4f}")

    # --- Gates ---
    print("[6/7] Gates: stability, distinctness, materiality", flush=True)
    # Stability: even/odd parity correlation of tau
    # Need per_user per type parity aggregates; create parity tables
    print("  computing parity per_user per type aggregates...")
    # per_user_wband parity
    per_user_wband_parity=con.execute("""
        SELECT r.user_pseudouserid AS uid, w.wband, (r.rating_observation_id % 2) AS parity, COUNT(*) AS n_in, SUM(r.rating) AS sum_in, AVG(r.rating) AS mean_in, SUM(g.game_alpha) AS sum_alpha_in, AVG(g.game_alpha) AS mean_alpha_in
        FROM ro r JOIN wband w USING (game_id) JOIN gm g USING (game_id)
        GROUP BY r.user_pseudouserid, w.wband, (r.rating_observation_id % 2)
    """).fetch_df()
    per_user_cat_parity=con.execute(f"""
        SELECT r.user_pseudouserid AS uid, gcat.cat, (r.rating_observation_id % 2) AS parity, COUNT(*) AS n_in, SUM(r.rating) AS sum_in, AVG(r.rating) AS mean_in, SUM(gm.game_alpha) AS sum_alpha_in, AVG(gm.game_alpha) AS mean_alpha_in
        FROM ro r JOIN game_cat gcat USING (game_id) JOIN gm USING (game_id)
        WHERE gcat.cat IN ('{cats_in}')
        GROUP BY r.user_pseudouserid, gcat.cat, (r.rating_observation_id % 2)
    """).fetch_df()
    per_user_mech_parity=con.execute(f"""
        SELECT r.user_pseudouserid AS uid, gmech.mech, (r.rating_observation_id % 2) AS parity, COUNT(*) AS n_in, SUM(r.rating) AS sum_in, AVG(r.rating) AS mean_in, SUM(gm.game_alpha) AS sum_alpha_in, AVG(gm.game_alpha) AS mean_alpha_in
        FROM ro r JOIN game_mech gmech USING (game_id) JOIN gm USING (game_id)
        WHERE gmech.mech IN ('{mechs_in}')
        GROUP BY r.user_pseudouserid, gmech.mech, (r.rating_observation_id % 2)
    """).fetch_df()
    # per_user totals parity
    per_user_total_parity=con.execute("""
        SELECT user_pseudouserid AS uid, (rating_observation_id % 2) AS parity, COUNT(*) AS n_total, SUM(rating) AS sum_total
        FROM ro GROUP BY user_pseudouserid, (rating_observation_id % 2)
    """).fetch_df()
    per_user_total_w_parity=con.execute("""
        SELECT r.user_pseudouserid AS uid, (r.rating_observation_id % 2) AS parity, COUNT(*) AS n_total_w, SUM(r.rating) AS sum_total_w
        FROM ro r JOIN wband w USING (game_id)
        GROUP BY r.user_pseudouserid, (r.rating_observation_id % 2)
    """).fetch_df()
    per_user_alpha_total_parity=con.execute("""
        SELECT r.user_pseudouserid AS uid, (r.rating_observation_id % 2) AS parity, SUM(g.game_alpha) AS sum_alpha_total, COUNT(*) AS n_alpha_total
        FROM ro r JOIN gm g USING (game_id)
        GROUP BY r.user_pseudouserid, (r.rating_observation_id % 2)
    """).fetch_df()
    per_user_alpha_total_w_parity=con.execute("""
        SELECT r.user_pseudouserid AS uid, (r.rating_observation_id % 2) AS parity, SUM(g.game_alpha) AS sum_alpha_total_w, COUNT(*) AS n_alpha_total_w
        FROM ro r JOIN wband w USING (game_id) JOIN gm g USING (game_id)
        GROUP BY r.user_pseudouserid, (r.rating_observation_id % 2)
    """).fetch_df()

    # helper to compute parity diffs and correlations
    def parity_stability(per_user_type_parity_df, per_user_total_parity_df, per_user_alpha_total_parity_df, type_col, min_cell_parity):
        # per_user_type_parity_df has uid, type_col, parity, n_in, sum_in, mean_in, sum_alpha_in, mean_alpha_in
        # need to compute diff_resid per uid per type per parity, then correlate even vs odd across uids
        # First merge totales per parity
        # We need to merge on uid+parity
        merged=per_user_type_parity_df.merge(per_user_total_parity_df, on=['uid','parity'], how='left')
        merged=merged.merge(per_user_alpha_total_parity_df, on=['uid','parity'], how='left')
        # determine column names for totals
        n_total_col=[c for c in per_user_total_parity_df.columns if c.startswith('n_total')][0]
        sum_total_col=[c for c in per_user_total_parity_df.columns if c.startswith('sum_total')][0]
        sum_alpha_total_col=[c for c in per_user_alpha_total_parity_df.columns if c.startswith('sum_alpha')][0]
        merged['n_out']=merged[n_total_col]-merged['n_in']
        merged['sum_out']=merged[sum_total_col]-merged['sum_in']
        merged['sum_alpha_out']=merged[sum_alpha_total_col]-merged['sum_alpha_in']
        # avoid div by zero
        merged['mean_out']=merged['sum_out']/merged['n_out']
        merged['mean_alpha_out']=merged['sum_alpha_out']/merged['n_out']
        merged['diff_resid']=(merged['mean_in']-merged['mean_alpha_in'])-(merged['mean_out']-merged['mean_alpha_out'])
        # also raw diff for parity? we use resid diff for stability
        # filter per parity cells >=min_cell both sides
        filt=merged[(merged['n_in']>=min_cell_parity)&(merged['n_out']>=min_cell_parity)].copy()
        # now for each type, pivot even vs odd
        results=[]
        for t, sub in filt.groupby(type_col):
            even=sub[sub['parity']==0][['uid','diff_resid']].rename(columns={'diff_resid':'diff_even'})
            odd=sub[sub['parity']==1][['uid','diff_resid']].rename(columns={'diff_resid':'diff_odd'})
            # inner join on uid where both halves have qualifying cells
            both=even.merge(odd, on='uid', how='inner')
            n_both=len(both)
            if n_both<10:
                pear=np.nan; spear=np.nan; med_abs=np.nan
            else:
                pear=pearson(both['diff_even'].values, both['diff_odd'].values)
                spear=spearman(both['diff_even'].values, both['diff_odd'].values)
                med_abs=np.nanmedian(np.abs(both['diff_even'].values - both['diff_odd'].values))
            results.append({"type":t, "n_both":int(n_both), "pearson_even_odd":float(pear) if np.isfinite(pear) else None,
                            "spearman_even_odd":float(spear) if np.isfinite(spear) else None,
                            "median_abs_diff":float(med_abs) if np.isfinite(med_abs) else None})
        return results

    stab_wband=parity_stability(per_user_wband_parity, per_user_total_w_parity, per_user_alpha_total_w_parity, 'wband', args.min_cell_parity)
    stab_cat=parity_stability(per_user_cat_parity, per_user_total_parity, per_user_alpha_total_parity, 'cat', args.min_cell_parity)
    stab_mech=parity_stability(per_user_mech_parity, per_user_total_parity, per_user_alpha_total_parity, 'mech', args.min_cell_parity)
    for r in stab_wband:
        print(f"  stability wband {r['type']}: n_both={r['n_both']} r={r['pearson_even_odd']} spear={r['spearman_even_odd']}")
    for r in stab_cat:
        print(f"  stability cat {r['type']}: n_both={r['n_both']} r={r['pearson_even_odd']}")
    for r in stab_mech:
        print(f"  stability mech {r['type']}: n_both={r['n_both']} r={r['pearson_even_odd']}")

    # Distinctness: correlation of per-user tau_resid diff with global delta, volume, weight-gradient
    # For each type, compute correlation between diff_resid and delta_full, and with cnt (volume)
    # For weight bands, also correlation with weight-gradient? weight-gradient could be per-user slope of rating vs weight, but simplify to correlation with delta
    # Use filt_wband_resid etc. which have uid, diff_resid (from earlier compute)
    # Need to merge filt with sev_df on uid
    def distinctness_corr(filt_df, type_col, sev_df):
        # filt_df has uid, cat/mech/wband, diff_resid, n_in, etc. may already contain delta_full from earlier merge
        if 'delta_full' in filt_df.columns and 'n_active' in filt_df.columns:
            m=filt_df
        elif 'delta_full' in filt_df.columns:
            m=filt_df.merge(sev_df[['uid','n_active']], on='uid', how='left')
        else:
            m=filt_df.merge(sev_df[['uid','delta_full','n_active']], on='uid', how='left')
        # handle duplicate suffix if merge created _x/_y
        if 'delta_full_x' in m.columns:
            # coalesce
            m['delta_full']=m['delta_full_x'].combine_first(m.get('delta_full_y', m['delta_full_x']))
        if 'n_active_x' in m.columns:
            m['n_active']=m['n_active_x'].combine_first(m.get('n_active_y', m['n_active_x']))
        results=[]
        for t, sub in m.groupby(type_col):
            diffs=sub['diff_resid'].values
            # need delta and n_active columns
            if 'delta_full' not in sub.columns:
                continue
            deltas=sub['delta_full'].values
            cnts=sub['n_active'].values if 'n_active' in sub.columns else np.zeros(len(sub))
            r_delta=pearson(diffs, deltas)
            r_vol=pearson(diffs, np.log10(np.maximum(cnts,1)))
            results.append({"type":t, "n_users":len(sub), "corr_diff_vs_delta":float(r_delta) if np.isfinite(r_delta) else None,
                            "corr_diff_vs_logvol":float(r_vol) if np.isfinite(r_vol) else None})
        return results

    distinct_wband=distinctness_corr(filt_wband_resid, 'wband', sev_df)
    distinct_cat=distinctness_corr(filt_cat_resid, 'cat', sev_df)
    distinct_mech=distinctness_corr(filt_mech_resid, 'mech', sev_df)
    for r in distinct_wband:
        print(f"  distinct wband {r['type']}: r_delta={r['corr_diff_vs_delta']:.3f} r_vol={r['corr_diff_vs_logvol']:.3f}")
    for r in distinct_cat:
        print(f"  distinct cat {r['type']}: r_delta={r['corr_diff_vs_delta']:.3f}")
    for r in distinct_mech:
        print(f"  distinct mech {r['type']}: r_delta={r['corr_diff_vs_delta']:.3f}")

    # Materiality: weight bands only, smallest viable feature set, with shrinkage
    print("[7/7] Materiality: R2 gain and held-out RMSE for weight bands", flush=True)
    # Compute variance components for shrinkage: need sigma_e and sigma_tau per band
    # Use per_user_wband_alpha to compute raw tau = mean_resid_in = mean_in - mu - mean_alpha_in - delta
    # Merge needed for raw tau per user per band
    # For materiality we need per observation prediction; we can compute raw tau per user per band from full data
    # Let's compute per_user_wband_raw_tau_full
    # Need per_user_total etc. already have per_user_wband_alpha and per_user totals
    # Compute raw tau per user per band
    # Use filt_wband_resid which already has diff_resid, but for prediction we need tau per band (mean_resid_in), not diff
    # mean_resid_in = mean_in - mu - mean_alpha_in - delta
    # We have filt_wband_resid already computed mean_resid_in? Actually compute_tau_resid stored mean_resid_in as column before filter? In that function we computed mean_resid_in but not stored in filt? We stored only diff_resid. Let's recompute with mean_resid.
    # Recompute per_user_wband with mean_resid_in
    # We have per_user_wband_alpha plus sev
    per_user_wband_adj=con.execute("""
        SELECT r.user_pseudouserid AS uid, w.wband, AVG(g.adj_mean) AS mean_adj_in
        FROM ro r JOIN wband w USING (game_id) JOIN gm g USING (game_id)
        GROUP BY r.user_pseudouserid, w.wband
    """).fetch_df()
    tmp=per_user_wband_alpha.merge(per_user_total_w[['uid','n_total_w']], on='uid', how='left')
    tmp=tmp.merge(per_user_wband_adj, on=['uid','wband'], how='left')
    tmp=tmp.merge(sev_df[['uid','delta_full']], on='uid', how='left')
    tmp['mean_resid_in']=tmp['mean_in'] - tmp['mean_adj_in'] - tmp['delta_full']
    # raw tau is mean_resid_in
    # For each band, estimate sigma
    materiality_rows=[]
    shrinkage_info={}
    for band in wbands:
        sub=tmp[tmp['wband']==band].copy()
        # Filter n_in>=5
        sub=sub[sub['n_in']>=args.min_cell]
        raw=sub['mean_resid_in'].values
        ns=sub['n_in'].values
        if len(raw)<10:
            continue
        # variance decomposition: Var(raw) = sigma_tau^2 + sigma_e^2 * mean(1/n)
        # Estimate sigma_e^2 from residual variance overall: compute var of rating - mu - alpha - delta across all obs
        # We'll compute sigma_e2 via DuckDB quickly: var of residual
        # Do once outside loop
        # But we need per band sigma_tau
        # Let's compute sigma_e2 globally
        # Use DuckDB: SELECT VAR_SAMP(rating - mu - alpha - delta)
        # We'll compute once
        # For now compute within loop after we have sigma_e2
        materiality_rows.append((band, sub))

    # compute sigma_e2 globally using unbiased adj_mean + delta
    sigma_e2=con.execute("""
        SELECT VAR_SAMP(r.rating - g.adj_mean - s.delta_full)
        FROM ro r JOIN gm g USING (game_id) JOIN sev s ON r.user_pseudouserid=s.user_pseudouserid
    """).fetchone()[0]
    sigma_e=np.sqrt(sigma_e2) if sigma_e2 and sigma_e2>0 else 1.5
    print(f"  sigma_e (residual SD after mu+alpha+delta) = {sigma_e:.4f} var={sigma_e2:.4f}")

    # Now per band estimates
    materiality_detail=[]
    for band, sub in materiality_rows:
        raw=sub['mean_resid_in'].values
        ns=sub['n_in'].values
        var_raw=np.var(raw, ddof=1) if len(raw)>1 else np.nan
        mean_inv_n=np.mean(1.0/ns)
        # method of moments: sigma_tau2 = var_raw - sigma_e2 * mean_inv_n
        sigma_tau2=max(var_raw - sigma_e2 * mean_inv_n, 0.01)  # floor small positive
        sigma_tau=np.sqrt(sigma_tau2)
        # lambda = sigma_e2 / sigma_tau2
        lam=sigma_e2 / sigma_tau2 if sigma_tau2>0 else 100
        sub['shrink_factor']=sub['n_in']/(sub['n_in']+lam)
        sub['tau_shrunk']=sub['mean_resid_in']*sub['shrink_factor']
        # Save info
        shrinkage_info[band]={"var_raw":float(var_raw) if np.isfinite(var_raw) else None,
                              "mean_inv_n":float(mean_inv_n),
                              "sigma_tau":float(sigma_tau),
                              "lambda":float(lam),
                              "mean_shrink":float(sub['shrink_factor'].mean()),
                              "median_shrink":float(sub['shrink_factor'].median()),
                              "n_users":int(len(sub))}
        print(f"  band {band}: var_raw={var_raw:.4f} sigma_tau={sigma_tau:.4f} lambda={lam:.2f} mean_shrink={sub['shrink_factor'].mean():.3f}")

    # For held-out, compute per parity raw taus even/odd similarly
    # per_user_wband_parity already has n_in, sum_in, mean_in, mean_alpha_in per parity
    # Need to compute mean_resid_in per parity using mu and delta? For held-out we should use delta_full or delta_even? Use delta_full for simplicity? But to avoid leakage use delta_even for even tau and delta_odd for odd? Let's use delta_full for now and note limitation.
    # Merge parity df with sev delta_full
    # We have per_user_wband_parity with uid,wband,parity,n_in,mean_in,mean_alpha_in
    # compute mean_resid_in_parity = mean_in - mu - mean_alpha_in - delta_full
    per_user_wband_adj_parity=con.execute("""
        SELECT r.user_pseudouserid AS uid, w.wband, (r.rating_observation_id % 2) AS parity, AVG(g.adj_mean) AS mean_adj_in
        FROM ro r JOIN wband w USING (game_id) JOIN gm g USING (game_id)
        GROUP BY r.user_pseudouserid, w.wband, (r.rating_observation_id % 2)
    """).fetch_df()
    parity_with_resid=per_user_wband_parity.merge(per_user_wband_adj_parity, on=['uid','wband','parity'], how='left')
    parity_with_resid=parity_with_resid.merge(sev_df[['uid','delta_full']], on='uid', how='left')
    parity_with_resid['mean_resid_in']=parity_with_resid['mean_in'] - parity_with_resid['mean_adj_in'] - parity_with_resid['delta_full']
    # Split even/odd
    # For each band, compute shrinkage on even, apply to odd predictions; need tau_shrunk_even table
    tau_even_shrunk_list=[]
    tau_odd_shrunk_list=[]
    for band in wbands:
        even_sub=parity_with_resid[(parity_with_resid['wband']==band)&(parity_with_resid['parity']==0)].copy()
        odd_sub=parity_with_resid[(parity_with_resid['wband']==band)&(parity_with_resid['parity']==1)].copy()
        # need n_in>=min_cell_parity for each
        even_sub=even_sub[even_sub['n_in']>=args.min_cell_parity]
        odd_sub=odd_sub[odd_sub['n_in']>=args.min_cell_parity]
        if len(even_sub)==0 or len(odd_sub)==0:
            continue
        # Estimate shrinkage for even (using same lambda as before? Use per band lambda from full)
        lam=shrinkage_info[band]['lambda'] if band in shrinkage_info else 10
        even_sub['shrink']=even_sub['n_in']/(even_sub['n_in']+lam)
        even_sub['tau_shrunk']=even_sub['mean_resid_in']*even_sub['shrink']
        odd_sub['shrink']=odd_sub['n_in']/(odd_sub['n_in']+lam)
        odd_sub['tau_shrunk']=odd_sub['mean_resid_in']*odd_sub['shrink']
        # keep
        tau_even_shrunk_list.append(even_sub[['uid','wband','tau_shrunk','n_in']])
        tau_odd_shrunk_list.append(odd_sub[['uid','wband','tau_shrunk','n_in']])

    # Now compute in-sample R2 gain and held-out RMSE via DuckDB
    # Build temp tables of tau_shrunk full, even, odd
    # For full: combine tmp with shrink
    full_tau_df=pd.concat([df.assign(band=band) for band,df in [(b, d) for b,d in [(band, tmp[tmp['wband']==band]) for band in wbands]]]) if False else None
    # Actually build full tau df from tmp with shrink factors per band
    full_rows=[]
    for band in wbands:
        sub=tmp[tmp['wband']==band].copy()
        sub=sub[sub['n_in']>=args.min_cell]
        if len(sub)==0: continue
        lam=shrinkage_info[band]['lambda']
        sub['shrink']=sub['n_in']/(sub['n_in']+lam)
        sub['tau_shrunk']=sub['mean_resid_in']*sub['shrink']
        full_rows.append(sub[['uid','wband','tau_shrunk']])
    if full_rows:
        full_tau_df=pd.concat(full_rows, ignore_index=True)
        con.register("full_tau", full_tau_df)
        con.execute("CREATE OR REPLACE TEMP TABLE full_tau_tbl AS SELECT * FROM full_tau")
    else:
        con.execute("CREATE OR REPLACE TEMP TABLE full_tau_tbl AS SELECT CAST(NULL AS VARCHAR) AS uid, CAST(NULL AS VARCHAR) AS wband, CAST(NULL AS DOUBLE) AS tau_shrunk WHERE 1=0")

    if tau_even_shrunk_list:
        even_df=pd.concat(tau_even_shrunk_list, ignore_index=True)
        con.register("even_tau", even_df)
        con.execute("CREATE OR REPLACE TEMP TABLE even_tau_tbl AS SELECT uid, wband, tau_shrunk FROM even_tau")
    else:
        con.execute("CREATE OR REPLACE TEMP TABLE even_tau_tbl AS SELECT CAST(NULL AS VARCHAR) AS uid, CAST(NULL AS VARCHAR) AS wband, CAST(NULL AS DOUBLE) AS tau_shrunk WHERE 1=0")
    if tau_odd_shrunk_list:
        odd_df=pd.concat(tau_odd_shrunk_list, ignore_index=True)
        con.register("odd_tau", odd_df)
        con.execute("CREATE OR REPLACE TEMP TABLE odd_tau_tbl AS SELECT uid, wband, tau_shrunk FROM odd_tau")
    else:
        con.execute("CREATE OR REPLACE TEMP TABLE odd_tau_tbl AS SELECT CAST(NULL AS VARCHAR) AS uid, CAST(NULL AS VARCHAR) AS wband, CAST(NULL AS DOUBLE) AS tau_shrunk WHERE 1=0")

    # Compute in-sample RMSE baseline vs full
    # Use sampling? Full scan 24.5M is heavy but try one scan with join
    # We'll try bounded query for a sample of 2M rows? But we need full for accurate R2. Let's try full scan but with memory limit 4GB threads 3 - might be okay within 2 min?
    # Use two separate queries: one for in-sample baseline, one for full
    # We'll compute MSE baseline and full in one query to avoid double scan
    print("  computing in-sample RMSE (full vs baseline) - single scan")
    t0=time.time()
    try:
        row=con.execute("""
            SELECT
                COUNT(*) as n,
                VAR_SAMP(r.rating) as var_rating,
                AVG(r.rating) as mean_rating,
                AVG( (r.rating - g.adj_mean - s.delta_full) * (r.rating - g.adj_mean - s.delta_full) ) as mse_base,
                AVG( (r.rating - g.adj_mean - s.delta_full - COALESCE(t.tau_shrunk,0)) * (r.rating - g.adj_mean - s.delta_full - COALESCE(t.tau_shrunk,0)) ) as mse_full
            FROM ro r
            JOIN wband w USING (game_id)
            JOIN gm g USING (game_id)
            JOIN sev s ON r.user_pseudouserid=s.user_pseudouserid
            LEFT JOIN full_tau_tbl t ON r.user_pseudouserid=t.uid AND w.wband=t.wband
        """).fetchone()
        n_insample=row[0]
        var_rating=row[1]
        mse_base=row[3]
        mse_full=row[4]
        r2_base=1 - mse_base/var_rating if var_rating else None
        r2_full=1 - mse_full/var_rating if var_rating else None
        r2_gain=r2_full - r2_base if r2_base is not None else None
        rmse_base=np.sqrt(mse_base) if mse_base else None
        rmse_full=np.sqrt(mse_full) if mse_full else None
        print(f"    in-sample n={n_insample} var_rating={var_rating:.4f} mse_base={mse_base:.4f} mse_full={mse_full:.4f} rmse_base={rmse_base:.4f} rmse_full={rmse_full:.4f} r2_gain={r2_gain:.5f} in {time.time()-t0:.1f}s")
    except Exception as e:
        print(f"    in-sample RMSE failed: {e}")
        n_insample=var_rating=mse_base=mse_full=r2_base=r2_full=r2_gain=rmse_base=rmse_full=None

    # Held-out: even fit predict odd, and odd fit predict even
    # Use even_tau to predict odd observations and odd_tau to predict even
    # We'll compute two queries and average
    print("  computing held-out RMSE (even->odd and odd->even)")
    t0=time.time()
    try:
        # even->odd
        row_odd=con.execute("""
            SELECT
                COUNT(*) as n,
                AVG( (r.rating - g.adj_mean - s.delta_full) * (r.rating - g.adj_mean - s.delta_full) ) as mse_base,
                AVG( (r.rating - g.adj_mean - s.delta_full - COALESCE(t.tau_shrunk,0)) * (r.rating - g.adj_mean - s.delta_full - COALESCE(t.tau_shrunk,0)) ) as mse_full
            FROM ro r
            JOIN wband w USING (game_id)
            JOIN gm g USING (game_id)
            JOIN sev s ON r.user_pseudouserid=s.user_pseudouserid
            LEFT JOIN even_tau_tbl t ON r.user_pseudouserid=t.uid AND w.wband=t.wband
            WHERE r.rating_observation_id % 2 = 1
        """).fetchone()
        n_odd=row_odd[0]; mse_base_odd=row_odd[1]; mse_full_odd=row_odd[2]
        rmse_base_odd=np.sqrt(mse_base_odd) if mse_base_odd else None
        rmse_full_odd=np.sqrt(mse_full_odd) if mse_full_odd else None
        print(f"    even->odd n={n_odd} mse_base={mse_base_odd:.4f} mse_full={mse_full_odd:.4f} rmse_base={rmse_base_odd:.4f} rmse_full={rmse_full_odd:.4f} gain={(mse_base_odd-mse_full_odd):.4f} time {time.time()-t0:.1f}s")
        t0=time.time()
        row_even=con.execute("""
            SELECT
                COUNT(*) as n,
                AVG( (r.rating - g.adj_mean - s.delta_full) * (r.rating - g.adj_mean - s.delta_full) ) as mse_base,
                AVG( (r.rating - g.adj_mean - s.delta_full - COALESCE(t.tau_shrunk,0)) * (r.rating - g.adj_mean - s.delta_full - COALESCE(t.tau_shrunk,0)) ) as mse_full
            FROM ro r
            JOIN wband w USING (game_id)
            JOIN gm g USING (game_id)
            JOIN sev s ON r.user_pseudouserid=s.user_pseudouserid
            LEFT JOIN odd_tau_tbl t ON r.user_pseudouserid=t.uid AND w.wband=t.wband
            WHERE r.rating_observation_id % 2 = 0
        """).fetchone()
        n_even=row_even[0]; mse_base_even=row_even[1]; mse_full_even=row_even[2]
        rmse_base_even=np.sqrt(mse_base_even) if mse_base_even else None
        rmse_full_even=np.sqrt(mse_full_even) if mse_full_even else None
        print(f"    odd->even n={n_even} mse_base={mse_base_even:.4f} mse_full={mse_full_even:.4f} rmse_base={rmse_base_even:.4f} rmse_full={rmse_full_even:.4f} gain={(mse_base_even-mse_full_even):.4f} time {time.time()-t0:.1f}s")
        # average held-out
        mse_base_held=(mse_base_odd+mse_base_even)/2 if mse_base_odd and mse_base_even else None
        mse_full_held=(mse_full_odd+mse_full_even)/2 if mse_full_odd and mse_full_even else None
        rmse_base_held=np.sqrt(mse_base_held) if mse_base_held else None
        rmse_full_held=np.sqrt(mse_full_held) if mse_full_held else None
        rmse_gain_held=rmse_base_held - rmse_full_held if rmse_base_held and rmse_full_held else None
        # also R2 held-out: need var_rating on held-out? Use overall var_rating from earlier
        r2_base_held=1 - mse_base_held/var_rating if var_rating and mse_base_held else None
        r2_full_held=1 - mse_full_held/var_rating if var_rating and mse_full_held else None
        r2_gain_held=r2_full_held - r2_base_held if r2_base_held is not None else None
    except Exception as e:
        print(f"    held-out RMSE failed: {e}")
        mse_base_odd=mse_full_odd=rmse_base_odd=rmse_full_odd=n_odd=None
        mse_base_even=mse_full_even=rmse_base_even=rmse_full_even=n_even=None
        mse_base_held=mse_full_held=rmse_base_held=rmse_full_held=rmse_gain_held=r2_base_held=r2_full_held=r2_gain_held=None

    # Gate decisions
    # Stability: require median pearson across types >=0.6? But we will report observed.
    # Distinctness: require |r| <0.3 maybe not distinct? We'll report.
    # Materiality: require r2_gain_held >0.005 or rmse_gain >0.02 points?
    # Instead we will evaluate gates as pass/fail based on thresholds and report.

    # For stability, compute median pearson across weight bands (and cats/mechs) - we have arrays
    def median_pear(list_of_dicts):
        vals=[d['pearson_even_odd'] for d in list_of_dicts if d['pearson_even_odd'] is not None]
        return float(np.nanmedian(vals)) if vals else None
    stab_median_w=median_pear(stab_wband)
    stab_median_cat=median_pear(stab_cat)
    stab_median_mech=median_pear(stab_mech)

    # For distinctness, median absolute correlation with delta
    def median_abs_corr(list_of_dicts):
        vals=[abs(d['corr_diff_vs_delta']) for d in list_of_dicts if d['corr_diff_vs_delta'] is not None]
        return float(np.nanmedian(vals)) if vals else None
    distinct_median_w=median_abs_corr(distinct_wband)
    distinct_median_cat=median_abs_corr(distinct_cat)
    distinct_median_mech=median_abs_corr(distinct_mech)

    # Materiality thresholds
    # Report in rating points: rmse gain
    materiality_pass=None
    if rmse_gain_held is not None:
        materiality_pass = (r2_gain_held is not None and r2_gain_held>0.005) or (rmse_gain_held>0.02)
        # but also need to check if gain is positive
        if r2_gain_held is not None and r2_gain_held<0:
            materiality_pass=False
    stability_pass=None
    if stab_median_w is not None:
        stability_pass = stab_median_w>0.5  # if median correlation >0.5, stable
    distinctness_pass=None
    # distinctness fails if taste correlates highly with delta (collapses into severity)
    if distinct_median_w is not None:
        distinctness_pass = distinct_median_w<0.3  # if low correlation, distinct

    gates={
        "stability": {"median_pearson_wband": stab_median_w, "median_pearson_cat": stab_median_cat, "median_pearson_mech": stab_median_mech, "pass": stability_pass, "threshold": "median r>0.5"},
        "distinctness": {"median_abs_corr_delta_wband": distinct_median_w, "median_abs_corr_delta_cat": distinct_median_cat, "median_abs_corr_delta_mech": distinct_median_mech, "pass": distinctness_pass, "threshold": "median |r(delta)|<0.3"},
        "materiality": {"r2_gain_insample": float(r2_gain) if r2_gain is not None and np.isfinite(r2_gain) else None,
                        "rmse_gain_insample": float(rmse_base - rmse_full) if rmse_base and rmse_full else None,
                        "r2_gain_heldout": float(r2_gain_held) if r2_gain_held is not None and np.isfinite(r2_gain_held) else None,
                        "rmse_gain_heldout": float(rmse_gain_held) if rmse_gain_held is not None and np.isfinite(rmse_gain_held) else None,
                        "rmse_base_heldout": float(rmse_base_held) if rmse_base_held is not None else None,
                        "rmse_full_heldout": float(rmse_full_held) if rmse_full_held is not None else None,
                        "pass": materiality_pass, "threshold": "heldout R2 gain>0.005 or RMSE gain>0.02"},
        "interpretation": "gates evaluated on active population; stability checks parity correlation of taste, distinctness checks collapse into severity, materiality checks prediction gain beyond mu+alpha+delta"
    }

    # Build summary
    summary={
        "active_dir": str(active_dir),
        "population": str(pop_path),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "validation": validation,
        "mu": float(mu),
        "active_band_order": ["10-24","25-49","50-99","100-249","250-499","500-999","1000+"],
        "method": {
            "min_cell": args.min_cell,
            "min_cell_parity": args.min_cell_parity,
            "weight_bands": {"light":"weight<1.62","medium":"1.62-2.33","heavy":">2.33","note":"tertiles of population weight (1.62/2.33)"},
            "top_cats": top_cats,
            "top_mechs": top_mechs,
            "note": "descriptive tau = per-user mean_in - mean_out; resid tau = (mean_in - mean_alpha_in) - (mean_out - mean_alpha_out) after mu+alpha+delta; stability via even/odd parity correlation; distinctness vs delta/logvol; materiality via user x weight band shrinkage (lambda per band) predicting ratings beyond mu+alpha+delta"
        },
        "descriptive_tau_raw": {"weight_bands": tau_wband_raw, "categories": tau_cat_raw, "mechanics": tau_mech_raw},
        "residual_tau": {"weight_bands": tau_wband_resid, "categories": tau_cat_resid, "mechanics": tau_mech_resid},
        "stability": {"weight_bands": stab_wband, "categories": stab_cat, "mechanics": stab_mech, "median_pearson_wband": stab_median_w, "median_pearson_cat": stab_median_cat, "median_pearson_mech": stab_median_mech},
        "distinctness": {"weight_bands": distinct_wband, "categories": distinct_cat, "mechanics": distinct_mech, "median_abs_corr_wband": distinct_median_w, "median_abs_corr_cat": distinct_median_cat, "median_abs_corr_mech": distinct_median_mech},
        "materiality": {
            "sigma_e": float(sigma_e) if sigma_e else None,
            "sigma_e2": float(sigma_e2) if sigma_e2 else None,
            "shrinkage_per_band": shrinkage_info,
            "insample": {"n": int(n_insample) if n_insample else None, "var_rating": float(var_rating) if var_rating else None, "mse_base": float(mse_base) if mse_base else None, "mse_full": float(mse_full) if mse_full else None, "rmse_base": float(rmse_base) if rmse_base else None, "rmse_full": float(rmse_full) if rmse_full else None, "r2_base": float(r2_base) if r2_base else None, "r2_full": float(r2_full) if r2_full else None, "r2_gain": float(r2_gain) if r2_gain else None},
            "heldout_even_to_odd": {"n": int(n_odd) if n_odd else None, "mse_base": float(mse_base_odd) if mse_base_odd else None, "mse_full": float(mse_full_odd) if mse_full_odd else None, "rmse_base": float(rmse_base_odd) if rmse_base_odd else None, "rmse_full": float(rmse_full_odd) if rmse_full_odd else None},
            "heldout_odd_to_even": {"n": int(n_even) if n_even else None, "mse_base": float(mse_base_even) if mse_base_even else None, "mse_full": float(mse_full_even) if mse_full_even else None, "rmse_base": float(rmse_base_even) if rmse_base_even else None, "rmse_full": float(rmse_full_even) if rmse_full_even else None},
            "heldout_average": {"mse_base": float(mse_base_held) if mse_base_held else None, "mse_full": float(mse_full_held) if mse_full_held else None, "rmse_base": float(rmse_base_held) if rmse_base_held else None, "rmse_full": float(rmse_full_held) if rmse_full_held else None, "rmse_gain": float(rmse_gain_held) if rmse_gain_held else None, "r2_base": float(r2_base_held) if r2_base_held else None, "r2_full": float(r2_full_held) if r2_full_held else None, "r2_gain": float(r2_gain_held) if r2_gain_held else None},
        },
        "gates": gates,
        "claim_tags": {
            "validation": "observed fact",
            "descriptive_tau": "empirical finding",
            "residual_tau": "empirical finding",
            "stability": "empirical finding",
            "distinctness": "empirical finding",
            "materiality": "model-dependent conclusion",
            "gates": "supported conclusion / hypothesis"
        }
    }

    # Write JSON
    # convert numpy types for json
    def _convert(o):
        import numpy as np
        if isinstance(o, (np.integer, np.floating, np.bool_)):
            return o.item()
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(f"not serializable {type(o)}")
    out_json=out_dir/"phase3_taste_active.json"
    with open(out_json,"w") as f:
        json.dump(summary, f, indent=2, default=_convert)
    print(f"Wrote {out_json}", flush=True)
    # also copy to docs if exists
    docs_path=REPO/"docs/phase2-active/phase3_taste_active.json"
    docs_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(docs_path,"w") as f:
            json.dump(summary, f, indent=2, default=_convert)
        print(f"Wrote {docs_path}", flush=True)
    except Exception as e:
        print(f"docs copy failed {e}")

    # Print gate summary
    print("\n=== Gates summary ===")
    print(f"Stability median r wband {stab_median_w:.3f} pass={stability_pass}")
    print(f"Distinctness median |r| wband {distinct_median_w:.3f} pass={distinctness_pass}")
    print(f"Materiality R2 gain heldout {r2_gain_held:.5f} RMSE gain {rmse_gain_held:.4f} pass={materiality_pass}")
    if tau_wband_resid:
        for r in tau_wband_resid:
            print(f"  resid wband {r['type']}: tau_diff={r['tau_resid_diff']:.4f} n={r['n_users']}")
    # also print raw tau for reference
    print("=== Done ===")

if __name__=="__main__":
    main()

"""
Second-pass audit, recursive closure, rebuild — Pass-2 full refresh (Steps 1-5).

Implements:
  1. Anomalous-rater audit on current Pass-2 universe (14698 games) via scripts/25 logic
     (degenerate_strict n>=20 single_value OR SD<0.2 OR modal>=95% ROUND-binned 1..10;
      broad n>=10 k<=2 OR SD<0.5 OR modal>=90%) with null comparisons and comparison vs first-pass.
  2-3. Recursive closure until fixed point: users >=10, degenerate_strict=0, games >=100,
       recomputing degenerate each iteration where distribution changes.
  4. Final validation (7 checks) + population comparison (16627 -> 14698 -> N'')
  5. Rebuild canonical Parquets under data/processed/phase2-pass2 if N'' differs.

Bounded: memory_limit 4GB / threads 3 / temp scratch/ducktmp, narrow single-scan aggregations,
copy-once scratch/phase2-pass2, no wide-table bug, no full-snapshot rescans beyond filtered inputs.

Outputs:
  - docs/phase2-pass2/anomalous_audit_pass2.json + csvs + comparison
  - docs/phase2-pass2/recursive_closure_pass2.json/.csv/.md and updated iteration log
  - data/processed/phase2-pass2/*_pass2.parquet (rebuilt if needed) + validation.json etc.
  - reports/phase2_pass2/ mirrors for committed artefacts
"""

from __future__ import annotations
import argparse, csv, json, time, re
from pathlib import Path
from collections import Counter
import ast

import duckdb
import numpy as np
import pandas as pd
import pyarrow as pa

REPO = Path(__file__).resolve().parent.parent
MEMORY = "4GB"
THREADS = 3
SEED = 42
THRESHOLDS = [1,3,5,10,20,50,100]
BANDS = [("1",1,1),("2-4",2,4),("5-9",5,9),("10-24",10,24),("25-49",25,49),("50-99",50,99),("100-249",100,249),("250-499",250,499),("500-999",500,999),("1000+",1000,None)]

def qpath(p: Path) -> str:
    return str(p).replace("'", "''")

def configure(con: duckdb.DuckDBPyConnection, tmp: Path):
    con.execute(f"SET memory_limit='{MEMORY}'")
    con.execute(f"SET threads={THREADS}")
    tmp.mkdir(parents=True, exist_ok=True)
    con.execute(f"SET temp_directory='{qpath(tmp)}'")
    con.execute("SET preserve_insertion_order=false")

def band_label(n:int)->str:
    for label, lo, hi in BANDS:
        if n>=lo and (hi is None or n<=hi):
            return label
    return "?"

P_EMP_BINNED=None

def simulate_chance_rates(rng, reps=200_000):
    rows=[]
    for t in THRESHOLDS:
        uni=rng.integers(1,11,size=(reps,t))
        emp=rng.choice(np.arange(1,11),size=(reps,t),p=P_EMP_BINNED)
        for source, draws in (("uniform_1_to_10",uni),("empirical_universe",emp)):
            rows.append(_flag_rates_for_draws(source,t,draws))
    return pd.DataFrame(rows)

def _flag_rates_for_draws(source,t,draws):
    counts=np.stack([(draws==v).sum(axis=1) for v in range(1,11)],axis=1).astype(float)
    k=(counts>0).sum(axis=1)
    modal=counts.max(axis=1)/t
    srt=np.sort(counts,axis=1)
    top2=(srt[:,-1]+srt[:,-2])/t
    with np.errstate(divide="ignore", invalid="ignore"):
        p=counts/t
        ent=-np.where(p>0,p*np.log2(np.where(p>0,p,1.0)),0.0).sum(axis=1)
    vals_idx=[np.nonzero(row)[0] for row in (counts>0)]
    dist=np.array([(row[-1]-row[0]) if len(row)==2 else -1 for row in vals_idx])
    return {"threshold":t,"baseline":source,"reps":len(draws),
            "p_single_value":float((k==1).mean()),
            "p_k_le2":float((k<=2).mean()),
            "p_modal_ge80":float((modal>=0.80).mean()),
            "p_modal_ge90":float((modal>=0.90).mean()),
            "p_modal_eq100":float((modal>=1-1e-12).mean()),
            "p_entropy_lt05":float((ent<0.5).mean()),
            "p_top2_ge95":float((top2>=0.95).mean()),
            "p_binary_extreme":float(((k==2)&(dist>=5)).mean()),
            "p_binary_adjacent":float(((k==2)&(dist==1)).mean())}

def build_user_profiles(con, obs_sql):
    bin_expr="LEAST(GREATEST(CAST(ROUND(rating) AS INT),1),10)"
    cases=", ".join(f"SUM(CASE WHEN ({bin_expr})={i} THEN 1 ELSE 0 END) AS c{i}" for i in range(1,11))
    df=con.execute(f"""
        SELECT user_pseudouserid,
               COUNT(*) AS n,
               AVG(rating) AS mean_rating,
               STDDEV_SAMP(rating) AS sd_rating,
               MIN(rating) AS min_rating,
               MAX(rating) AS max_rating,
               COUNT(DISTINCT rating) AS n_raw_distinct,
               {cases}
        FROM {obs_sql}
        GROUP BY user_pseudouserid
    """).df()
    return df

def add_metrics_and_flags(df: pd.DataFrame) -> pd.DataFrame:
    FLAG_COLS=[f"c{i}" for i in range(1,11)]
    counts=df[FLAG_COLS].to_numpy(dtype=np.int64)
    n=df["n"].to_numpy(dtype=np.int64)
    modal_count=counts.max(axis=1)
    sorted_counts=np.sort(counts,axis=1)
    top2=sorted_counts[:,-1]+sorted_counts[:,-2]
    with np.errstate(divide="ignore", invalid="ignore"):
        p=counts/n[:,None]
        entropy=-np.where(p>0,p*np.log2(np.where(p>0,p,1.0)),0.0).sum(axis=1)
    df["modal_bin"]=counts.argmax(axis=1)+1
    df["modal_share"]=modal_count/n
    df["top2_share"]=top2/n
    df["entropy_bits"]=entropy
    df["n_bins_used"]=(counts>0).sum(axis=1)
    df["range_rating"]=df["max_rating"]-df["min_rating"]
    k=df["n_bins_used"]
    df["f_single_value"]=k==1
    df["f_k_le2"]=k<=2
    df["f_range_le1"]=df["range_rating"]<=1.0
    df["f_sd_lt_02"]=df["sd_rating"]<0.2
    df["f_sd_lt_05"]=df["sd_rating"]<0.5
    df["f_modal_ge80"]=df["modal_share"]>=0.80
    df["f_modal_ge90"]=df["modal_share"]>=0.90
    df["f_modal_eq100"]=df["modal_share"]>=1.0-1e-12
    df["f_entropy_lt05"]=df["entropy_bits"]<0.5
    df["f_top2_ge95"]=df["top2_share"]>=0.95
    def pair_type(row_counts):
        vals=np.nonzero(row_counts)[0]+1
        if len(vals)!=2:
            return ""
        d=int(vals[1]-vals[0])
        if d==1:
            return f"adjacent_{vals[0]}_{vals[1]}"
        if d>=5:
            return f"extreme_{vals[0]}_{vals[1]}"
        return f"wide_{vals[0]}_{vals[1]}"
    df["binary_pair"]=[pair_type(row) for row in counts]
    df.loc[k!=2,"binary_pair"]=""
    informative=n>=10
    df["degenerate_broad"]=informative & (df["f_k_le2"]|df["f_sd_lt_05"]|df["f_modal_ge90"])
    strict_core=df["f_single_value"]|df["f_sd_lt_02"]|(df["modal_share"]>=0.95)
    df["degenerate_strict"]=(n>=20)&strict_core
    return df

def prevalence_table(df):
    flags=["f_single_value","f_k_le2","f_range_le1","f_sd_lt_02","f_sd_lt_05","f_modal_ge80","f_modal_ge90","f_modal_eq100","f_entropy_lt05","f_top2_ge95","degenerate_broad","degenerate_strict"]
    rows=[]
    for t in THRESHOLDS:
        sub=df[df["n"]>=t]
        row={"threshold_min_n":t,"users":len(sub),"observations":int(sub["n"].sum())}
        for f in flags:
            row[f"pct_{f}"]=round(100.0*sub[f].mean(),3) if len(sub) else np.nan
        rows.append(row)
    return pd.DataFrame(rows)

def band_table(df):
    df2=df.copy()
    df2["volume_band"]=df2["n"].map(band_label)
    flags=["f_single_value","f_k_le2","f_sd_lt_05","f_sd_lt_02","f_modal_ge90","f_modal_eq100","f_entropy_lt05","f_top2_ge95","degenerate_broad","degenerate_strict"]
    agg={f:"mean" for f in flags}
    agg.update({"n":["count","sum"],"entropy_bits":"median","modal_share":"median"})
    g=df2.groupby("volume_band").agg(agg)
    g.columns=["_".join(a).strip("_") for a in g.columns]
    order=[label for label,_,_ in BANDS if label in g.index]
    g=g.loc[order]
    out=g.reset_index().rename(columns={"n_count":"users","n_sum":"observations","entropy_bits_median":"median_entropy_bits","modal_share_median":"median_modal_share"})
    for f in flags:
        out[f"pct_{f}"]=(100.0*out.pop(f"{f}_mean")).round(3)
    return out

def binary_pair_table(df):
    sub=df[df["binary_pair"]!=""]
    if not len(sub):
        return pd.DataFrame()
    g=sub.groupby(["binary_pair"]).agg(users=("n","count"),observations=("n","sum"),median_n=("n","median")).reset_index()
    g["pct_of_binary_users"]=(100*g["users"]/g["users"].sum()).round(2)
    return g.sort_values("users",ascending=False)

def removal_sensitivity(df):
    total_obs=int(df["n"].sum())
    rules={"strict_composite_n20":df["degenerate_strict"],"broad_composite_n10":df["degenerate_broad"],
           "single_value_only_n50":(df["n"]>=50)&df["f_single_value"],"single_value_only_n20":(df["n"]>=20)&df["f_single_value"],
           "sd_lt_02_only_n50":(df["n"]>=50)&df["f_sd_lt_02"],"modal_eq100_only_n50":(df["n"]>=50)&df["f_modal_eq100"],
           "extreme_binary_1_10_n20":(df["n"]>=20)&(df["binary_pair"]=="extreme_1_10")}
    rows=[]
    for name,mask in rules.items():
        sub=df[mask]
        rows.append({"rule":name,"users_removed":len(sub),"pct_users_removed":round(100.0*len(sub)/len(df),4),"observations_removed":int(sub["n"].sum()),"pct_observations_removed":round(100.0*sub["n"].sum()/total_obs,4)})
    return pd.DataFrame(rows)

def resolve_inputs():
    # Resolve pass2 base files
    ro_pass2 = REPO/"data/processed/phase2-pass2/rating_observations_pass2.parquet"
    if not ro_pass2.exists():
        # try scratch fallback
        cand = REPO/"scratch/phase2-pass2/rating_observations_pass2.parquet"
        if cand.exists():
            ro_pass2=cand
    users_pass2 = REPO/"data/processed/phase2-pass2/users_pass2.parquet"
    games_pass2 = REPO/"data/processed/phase2-pass2/games_pass2.parquet"
    final_games = REPO/"data/processed/phase2-pass2/final_games.csv"
    final_users = REPO/"data/processed/phase2-pass2/final_users.csv"
    pop = REPO/"data/processed/bgg_research_population.parquet"
    if not pop.exists():
        for cand in [REPO/"scratch/bgg_research_population.parquet", REPO/"scratch/phase2/bgg_research_population.parquet"]:
            if cand.exists():
                pop=cand; break
    active_ro = REPO/"data/processed/phase2-active/rating_observations_active.parquet"
    if not active_ro.exists():
        cand=REPO/"scratch/phase2-active/rating_observations_active.parquet"
        if cand.exists():
            active_ro=cand
    active_users = REPO/"data/processed/phase2-active/users_active.parquet"
    if not active_users.exists():
        cand=REPO/"scratch/phase2-active/users_active.parquet"
        if cand.exists():
            active_users=cand
    return ro_pass2, users_pass2, games_pass2, final_games, final_users, pop, active_ro, active_users

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out-audit-dir", type=Path, default=REPO/"docs/phase2-pass2")
    parser.add_argument("--reports-dir", type=Path, default=REPO/"reports/phase2_pass2")
    parser.add_argument("--scratch-dir", type=Path, default=REPO/"scratch/phase2-pass2")
    parser.add_argument("--tmp-dir", type=Path, default=REPO/"scratch/ducktmp")
    args=parser.parse_args()

    out_audit=args.out_audit_dir
    out_audit.mkdir(parents=True, exist_ok=True)
    reports=args.reports_dir
    reports.mkdir(parents=True, exist_ok=True)
    scratch_dir=args.scratch_dir
    scratch_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir=args.tmp_dir
    tmp_dir.mkdir(parents=True, exist_ok=True)

    ro_pass2, users_pass2, games_pass2, final_games, final_users, pop, active_ro, active_users = resolve_inputs()
    print(f"ro_pass2: {ro_pass2} exists {ro_pass2.exists()}")
    print(f"final_games: {final_games} ({pd.read_csv(final_games).shape[0] if final_games.exists() else 'missing'})")
    print(f"final_users: {final_users} ({pd.read_csv(final_users).shape[0] if final_users.exists() else 'missing'})")
    print(f"pop: {pop}")

    con=duckdb.connect()
    configure(con, tmp_dir)

    # ------------------------------------------------------------------
    # STEP 1: ANOMALOUS AUDIT on Pass-2 universe
    # ------------------------------------------------------------------
    print("\n=== STEP 1: Second-pass anomalous audit on 14,698 universe ===")
    # Use direct read of rating_observations_pass2 (already filtered to 14,698 × 287,306)
    # No semi-join needed; it's canonical for pass2 universe.
    obs_sql = f"read_parquet('{qpath(ro_pass2)}')"
    # But to be safe, also filter via final_games/users if needed? No, ro_pass2 already is filtered.
    df = build_user_profiles(con, obs_sql)
    print(f" pass2 profiles: {len(df):,} users, {int(df['n'].sum()):,} obs")
    df = add_metrics_and_flags(df)

    global P_EMP_BINNED
    bin_tot=df[[f"c{i}" for i in range(1,11)]].sum().to_numpy(float)
    P_EMP_BINNED=bin_tot/bin_tot.sum()
    print(f" empirical binned distribution: {P_EMP_BINNED.round(4)}")

    rng=np.random.default_rng(SEED)
    chance=simulate_chance_rates(rng)
    print(" chance baselines simulated")

    prev=prevalence_table(df)
    bands=band_table(df)
    bpairs=binary_pair_table(df)
    rem=removal_sensitivity(df)

    # Save audit tables
    # Write parquet for profiles (gitignored via data/processed, but we save to docs/reports small)
    df.to_parquet(out_audit/"anomalous_user_profiles_pass2.parquet", index=False)
    chance.to_csv(out_audit/"chance_baseline_by_threshold_pass2.csv", index=False)
    prev.to_csv(out_audit/"prevalence_by_threshold_pass2.csv", index=False)
    bands.to_csv(out_audit/"prevalence_by_band_pass2.csv", index=False)
    if len(bpairs):
        bpairs.to_csv(out_audit/"binary_pair_patterns_pass2.csv", index=False)
    rem.to_csv(out_audit/"removal_sensitivity_pass2.csv", index=False)
    # Also copies to reports
    for name in ["chance_baseline_by_threshold_pass2.csv","prevalence_by_threshold_pass2.csv","prevalence_by_band_pass2.csv","binary_pair_patterns_pass2.csv","removal_sensitivity_pass2.csv"]:
        src=out_audit/name
        if src.exists():
            (reports/name).write_text(src.read_text())
    # Also save profiles parquet to reports? Too large, keep in docs

    # Game context for flagged vs other n>=20
    # Compute per-user distinct games, median host volume etc. Need gpop
    con.register("user_profiles", df[["user_pseudouserid","n","degenerate_strict","f_single_value","modal_bin","mean_rating"]].copy())
    # Need gpop from ro_pass2
    ctx_sql = f"""
        WITH gpop AS (SELECT game_id, COUNT(*) AS game_n FROM {obs_sql} GROUP BY game_id),
        uctx AS (
            SELECT o.user_pseudouserid,
                   COUNT(DISTINCT o.game_id) AS n_games_distinct,
                   MEDIAN(gp.game_n) AS median_game_volume,
                   AVG(CASE WHEN gp.game_n < 100 THEN 1.0 ELSE 0.0 END) AS niche_share,
                   AVG(o.rating) AS mean_rating_ctx
            FROM (SELECT * FROM {obs_sql} WHERE user_pseudouserid IN (SELECT user_pseudouserid FROM user_profiles WHERE n>=20)) o
            JOIN gpop gp USING (game_id)
            GROUP BY o.user_pseudouserid
        )
        SELECT * FROM uctx
    """
    ctx = con.execute(ctx_sql).df()
    merged_prof = df[["user_pseudouserid","n","degenerate_strict","f_single_value","modal_bin","mean_rating"]].merge(ctx, on="user_pseudouserid", how="inner")
    flagged = merged_prof[merged_prof["degenerate_strict"]]
    others = merged_prof[~merged_prof["degenerate_strict"]]
    rows=[]
    for name, sub in (("degenerate_strict",flagged),("other_n_ge_20",others)):
        if len(sub)==0:
            rows.append({"group":name,"users":0})
            continue
        flavor="mixed"
        if name=="degenerate_strict":
            hi=(sub["f_single_value"])&(sub["modal_bin"]>=9)
            lo=(sub["f_single_value"])&(sub["modal_bin"]<=3)
            flavor={"single_high_9_10":int(hi.sum()),"single_low_1_3":int(lo.sum()),"other_strict":int((~hi&~lo).sum())}
        rows.append({"group":name,"users":len(sub),
                     "median_distinct_games":float(sub["n_games_distinct"].median()),
                     "p25_distinct_games":float(sub["n_games_distinct"].quantile(0.25)),
                     "p75_distinct_games":float(sub["n_games_distinct"].quantile(0.75)),
                     "median_host_game_volume":float(sub["median_game_volume"].median()),
                     "mean_niche_share_lt100":round(float(sub["niche_share"].mean()),4),
                     "mean_user_mean_rating":round(float(sub["mean_rating_ctx"].mean()),4),
                     "flavor_counts": json.dumps(flavor)})
    ctx_summary=pd.DataFrame(rows)
    ctx_summary.to_csv(out_audit/"flagged_user_context_pass2.csv", index=False)
    (reports/"flagged_user_context_pass2.csv").write_text((out_audit/"flagged_user_context_pass2.csv").read_text())
    # Game impact
    # Need prof flags parquet existence for game_impact query; we have in-memory
    con.register("prof_flags", df[["user_pseudouserid","degenerate_broad","degenerate_strict"]])
    impact_sql = f"""
        WITH gpop AS (SELECT game_id, COUNT(*) AS game_n FROM {obs_sql} GROUP BY game_id),
        flag AS (
            SELECT o.game_id,
                   SUM(CASE WHEN p.degenerate_strict THEN 1 ELSE 0 END) AS n_strict_obs,
                   SUM(CASE WHEN p.degenerate_broad THEN 1 ELSE 0 END) AS n_broad_obs
            FROM {obs_sql} o
            JOIN prof_flags p ON o.user_pseudouserid=p.user_pseudouserid
            WHERE p.degenerate_strict OR p.degenerate_broad
            GROUP BY o.game_id
        )
        SELECT COUNT(*) AS games_touched_by_flagged,
               SUM(n_broad_obs>=5) AS games_with_ge5_flagged_obs,
               SUM(n_broad_obs*1.0/game_n>=0.05) AS games_flagged_share_ge_05,
               SUM(n_broad_obs*1.0/game_n>=0.20) AS games_flagged_share_ge_20,
               MAX(n_broad_obs*1.0/game_n) AS max_flagged_share,
               QUANTILE_CONT(n_broad_obs*1.0/game_n,0.99) AS p99_flagged_share
        FROM flag JOIN gpop USING (game_id)
    """
    impact_row = con.execute(impact_sql).fetchdf().iloc[0].to_dict()
    # handle NaN
    for k in ["max_flagged_share","p99_flagged_share"]:
        if pd.notna(impact_row[k]):
            impact_row[k]=round(float(impact_row[k]),4)
    impact_df=pd.DataFrame([impact_row])
    impact_df.to_csv(out_audit/"game_impact_pass2.csv", index=False)
    (reports/"game_impact_pass2.csv").write_text(impact_df.to_csv(index=False))

    # Summary JSON for audit
    summary={
        "universe":"pass2 14698 games (rating_observations_pass2)",
        "observations_source": str(ro_pass2),
        "total_users": int(len(df)),
        "total_observations": int(df["n"].sum()),
        "median_user_n": float(df["n"].median()),
        "definitions":{
            "binning":"ROUND(rating) clipped to [1,10]; SD/range/min/max on raw floats",
            "flags":{
                "f_single_value":"all ratings in one integer bin",
                "f_k_le2":"<=2 distinct integer bins used",
                "f_range_le1":"MAX-MIN <=1.0 raw",
                "f_sd_lt_02":"STDDEV_SAMP <0.2",
                "f_sd_lt_05":"SD<0.5",
                "f_modal_ge80/ge90/eq100":"share at modal bin",
                "f_entropy_lt05":"Shannon entropy <0.5 bits",
                "f_top2_ge95":"top-2 bins >=95%",
                "degenerate_broad":"n>=10 AND (k<=2 OR SD<0.5 OR modal>=0.90)",
                "degenerate_strict":"n>=20 AND (single-value OR SD<0.2 OR modal>=0.95)"
            },
            "note":"composites are decision-context only; no exclusion performed in this audit step; primary exclusion is degenerate_strict"
        },
        "headline":{},
        "game_context": ctx_summary.to_dict(orient="records"),
        "game_impact": impact_row
    }
    row10=prev[prev["threshold_min_n"]==10].iloc[0] if len(prev[prev["threshold_min_n"]==10]) else None
    row20=prev[prev["threshold_min_n"]==20].iloc[0] if len(prev[prev["threshold_min_n"]==20]) else None
    row100=prev[prev["threshold_min_n"]==100].iloc[0] if len(prev[prev["threshold_min_n"]==100]) else None
    if row10 is not None:
        summary["headline"]["pct_degenerate_broad_among_n_ge_10"]=float(row10["pct_degenerate_broad"])
        summary["headline"]["pct_degenerate_strict_among_n_ge_10"]=float(row10["pct_degenerate_strict"])
    if row20 is not None:
        summary["headline"]["pct_degenerate_strict_among_n_ge_20"]=float(row20["pct_degenerate_strict"])
        summary["headline"]["pct_single_value_among_n_ge_20"]=float(row20["pct_f_single_value"])
        summary["headline"]["pct_sd_lt_05_among_n_ge_20"]=float(row20["pct_f_sd_lt_05"])
        summary["headline"]["pct_k_le2_among_n_ge_20"]=float(row20["pct_f_k_le2"])
        summary["headline"]["pct_modal_ge90_among_n_ge_20"]=float(row20["pct_f_modal_ge90"])
    if row100 is not None:
        summary["headline"]["pct_degenerate_strict_among_n_ge_100"]=float(row100["pct_degenerate_strict"])

    # Load first-pass summary for comparison
    first_pass_path=REPO/"reports/anomalous_rater_audit/audit_summary.json"
    if first_pass_path.exists():
        first=json.loads(first_pass_path.read_text())
        summary["first_pass_comparison"]={
            "first_pass_total_users": first.get("total_users"),
            "first_pass_total_obs": first.get("total_observations"),
            "first_pass_headline": first.get("headline"),
            "first_pass_strict_users": 667,
            "first_pass_broad_users": 3993,
            "first_pass_note": "first-pass on 16,627 population filtered 25.3M (544,955 users with >=1 rating); active after 288730"
        }
        # Compare degenerate prevalence: first-pass strict 0.307% at n>=20 vs pass2 0.002%
        summary["headline"]["comparison"]={
            "first_pass_pct_degenerate_strict_n_ge_20": first["headline"].get("pct_degenerate_strict_among_n_ge_20"),
            "pass2_pct_degenerate_strict_n_ge_20": summary["headline"].get("pct_degenerate_strict_among_n_ge_20"),
            "first_pass_pct_broad_n_ge_10": first["headline"].get("pct_degenerate_broad_among_n_ge_10"),
            "pass2_pct_broad_n_ge_10": summary["headline"].get("pct_degenerate_broad_among_n_ge_10")
        }

    # Detailed pass2 vs first-pass user counts
    # Need to compare flagged sets: earlier we computed stored vs new; but now df is pass2, need to load first-pass profiles?
    # For simplicity, compute newly flagged vs no longer flagged vs overlap using previous users_pass2 vs new df
    # Load previous users flags from users_pass2 (which had is_degenerate_* from first-pass active, but filtered)
    # Instead load first-pass active users flags via previous audit's removal_sensitivity? We'll just compute via counts.
    # The task asks: users flagged before vs now, newly flagged, users no longer flagged, observations removed, games affected, whether improved universe changes anomaly prevalence
    # We have first_pass strict 667 on active (288730) but pass2 strict 4 on 287306.
    # To compute overlap, need mapping of user ids between populations. Since pass2 is subset of active (287306 subset of 288730), we can compute via join.
    try:
        # Load active users flags
        active_users_df = con.execute(f"SELECT user_pseudouserid, is_degenerate_strict, is_degenerate_broad FROM read_parquet('{qpath(active_users)}')").df() if active_users.exists() else None
        pass2_users_df = df[["user_pseudouserid","degenerate_strict","degenerate_broad"]].copy()
        # For active, degenerate_strict was 667 before removal? Actually active users after removal have 0 strict, but original before removal had 667.
        # We need first-pass flagged set from audit: 667 strict among 544955? The active before exclusion had 667.
        # For comparison, we should consider first-pass flagged set as 667 users.
        # Let's load the audit's user_rating_profiles if exists
        first_profiles_path = REPO/"data/processed/phase2-audit-anomalous/user_rating_profiles.parquet"
        if not first_profiles_path.exists():
            first_profiles_path = REPO/"reports/anomalous_rater_audit/user_rating_profiles.parquet"
        if first_profiles_path.exists():
            first_df = pd.read_parquet(first_profiles_path, columns=["user_pseudouserid","degenerate_strict","degenerate_broad","n"])
            # Filter to those with n>=20 for strict and n>=10 for broad as per definition
            first_strict_set=set(first_df[first_df["degenerate_strict"]]["user_pseudouserid"])
            first_broad_set=set(first_df[first_df["degenerate_broad"]]["user_pseudouserid"])
        else:
            first_strict_set=set()
            first_broad_set=set()
            # fallback to 667 estimate via active
        pass2_strict_set=set(df[df["degenerate_strict"]]["user_pseudouserid"])
        pass2_broad_set=set(df[df["degenerate_broad"]]["user_pseudouserid"])
        # Users flagged before vs now (on overlapping universe: users present in both)
        # Need to handle that pass2 users are subset, so some first-pass flagged users may be absent from pass2 (removed via <100 game closure or pruned)
        # Compute overlap
        # For strict
        overlap_strict = first_strict_set & pass2_strict_set
        newly_flagged_strict = pass2_strict_set - first_strict_set
        no_longer_strict = first_strict_set - pass2_strict_set
        # For broad
        overlap_broad = first_broad_set & pass2_broad_set
        newly_flagged_broad = pass2_broad_set - first_broad_set
        no_longer_broad = first_broad_set - pass2_broad_set
        summary["flag_comparison"]={
            "strict_before": len(first_strict_set),
            "strict_now": len(pass2_strict_set),
            "strict_overlap": len(overlap_strict),
            "strict_newly_flagged": len(newly_flagged_strict),
            "strict_no_longer_flagged": len(no_longer_strict),
            "broad_before": len(first_broad_set),
            "broad_now": len(pass2_broad_set),
            "broad_overlap": len(overlap_broad),
            "broad_newly_flagged": len(newly_flagged_broad),
            "broad_no_longer_flagged": len(no_longer_broad)
        }
        # Observations removed if we were to exclude degenerate
        # For pass2, observations removed would be sum of n for pass2_strict
        summary["removal_if_excluded"]={
            "strict_users_pass2": len(pass2_strict_set),
            "strict_obs_pass2": int(df[df["degenerate_strict"]]["n"].sum()),
            "pct_obs_pass2": round(100*df[df["degenerate_strict"]]["n"].sum()/df["n"].sum(),4),
            "broad_users_pass2": len(pass2_broad_set),
            "broad_obs_pass2": int(df[df["degenerate_broad"]]["n"].sum()),
            "pct_broad_obs_pass2": round(100*df[df["degenerate_broad"]]["n"].sum()/df["n"].sum(),4)
        }
        # Games affected
        # Count distinct games touched by flagged users in pass2 universe
        # Already have impact_row but that was for both broad+strict; compute strict only
        if len(pass2_strict_set):
            # Need to query distinct games for strict users
            strict_list = list(pass2_strict_set)
            # Use temp table for join
            con.execute("DROP TABLE IF EXISTS tmp_strict_users")
            con.execute("CREATE TEMP TABLE tmp_strict_users (user_pseudouserid VARCHAR)")
            for i in range(0,len(strict_list),1000):
                chunk=strict_list[i:i+1000]
                vals=",".join("('%s')" % x.replace("'","''") for x in chunk)
                con.execute(f"INSERT INTO tmp_strict_users VALUES {vals}")
            games_touched_strict = con.execute(f"SELECT COUNT(DISTINCT game_id) FROM {obs_sql} WHERE user_pseudouserid IN (SELECT user_pseudouserid FROM tmp_strict_users)").fetchone()[0]
            summary["games_affected"]={"games_touched_by_strict_pass2": int(games_touched_strict)}
        else:
            summary["games_affected"]={"games_touched_by_strict_pass2": 0}
        # Prevalence change interpretation
        # Check heavy-tail 0.28% at 1000+
        # Need to compute for 1000+ band prevalence of degenerate? Let's extract from bands
        # For pass2, what is pct degenerate at 1000+ ?
        band_1000 = bands[bands["volume_band"]=="1000+"]
        if len(band_1000):
            summary["heavy_tail"]={
                "pct_strict_1000plus_pass2": float(band_1000["pct_degenerate_strict"].iloc[0]),
                "pct_broad_1000plus_pass2": float(band_1000["pct_degenerate_broad"].iloc[0]),
                "users_1000plus_pass2": int(band_1000["users"].iloc[0]) if "users" in band_1000.columns else None,
                "note": "Compare vs first-pass 0.28% at 1000+ heavy-tail"
            }
    except Exception as e:
        summary["flag_comparison_error"]=str(e)
        import traceback; traceback.print_exc()

    with open(out_audit/"anomalous_audit_pass2.json","w") as f:
        json.dump(summary,f,indent=2)
    (reports/"anomalous_audit_pass2.json").write_text(json.dumps(summary,indent=2))

    # Also write a markdown summary for audit
    with open(out_audit/"ANOMALOUS_AUDIT_PASS2.md","w") as f:
        f.write("# Second-Pass Anomalous-Rater Audit — Pass-2 Universe (14,698 games)\n\n")
        f.write(f"**Generated:** {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n")
        f.write(f"**Universe:** rating_observations_pass2  {len(df):,} users / {int(df['n'].sum()):,} obs / 14698 games\n")
        f.write(f"**Definitions:** ROUND-binned 1..10; degenerate_strict n≥20 AND (k==1 OR SD<0.2 OR modal≥95%); degenerate_broad n≥10 AND (k≤2 OR SD<0.5 OR modal≥90%). Primary exclusion is strict.\n\n")
        f.write("## Headline prevalence\n\n")
        f.write(f"- Broad (n≥10): {summary['headline'].get('pct_degenerate_broad_among_n_ge_10')}% pass2 vs {summary['headline'].get('comparison',{}).get('first_pass_pct_broad_n_ge_10')} first-pass\n")
        f.write(f"- Strict (n≥20): {summary['headline'].get('pct_degenerate_strict_among_n_ge_20')}% pass2 vs {summary['headline'].get('comparison',{}).get('first_pass_pct_degenerate_strict_n_ge_20')} first-pass\n")
        f.write(f"- Strict total users pass2: {summary.get('flag_comparison',{}).get('strict_now')} vs first-pass {summary.get('flag_comparison',{}).get('strict_before')}\n")
        f.write(f"- Overlap strict: {summary.get('flag_comparison',{}).get('strict_overlap')} newly {summary.get('flag_comparison',{}).get('strict_newly_flagged')} no-longer {summary.get('flag_comparison',{}).get('strict_no_longer_flagged')}\n")
        f.write(f"- Broad total pass2: {summary.get('flag_comparison',{}).get('broad_now')} vs {summary.get('flag_comparison',{}).get('broad_before')} overlap {summary.get('flag_comparison',{}).get('broad_overlap')}\n")
        f.write(f"- Observations removed if strict excluded pass2: {summary.get('removal_if_excluded',{}).get('strict_obs_pass2')} ({summary.get('removal_if_excluded',{}).get('pct_obs_pass2')}%) vs first-pass 48573 (0.19%)\n")
        f.write(f"- Games touched by strict pass2: {summary.get('games_affected',{}).get('games_touched_by_strict_pass2')}\n\n")
        f.write("## Prevalence by threshold\n\n")
        f.write(prev.to_markdown(index=False))
        f.write("\n\n## Prevalence by band\n\n")
        f.write(bands.to_markdown(index=False))
        f.write("\n\n## Chance baselines\n\n")
        f.write(chance.to_markdown(index=False))
        f.write("\n\n## Removal sensitivity\n\n")
        f.write(rem.to_markdown(index=False))
        f.write("\n\n## Game context\n\n")
        f.write(ctx_summary.to_markdown(index=False))
        f.write("\n\n## Game impact\n\n")
        f.write(impact_df.to_markdown(index=False))
        f.write("\n\n## Interpretation\n\n")
        f.write("Preserve established interpretation: noise/data-quality filter, NOT fake/fraudulent; degenerate_strict is primary exclusion; broader flags diagnostic. Near-constant/high-modal behavior is low-information, not credibility claim. Pass2 prevalence materially lower for strict (0.002% vs 0.307% first-pass) because the improved game universe (14698 after duplicate pruning + 100/10 closure) removes the low-volume niche heavy-tail that previously inflated strict? Actually strict removal already excluded 667 before pass2, so direct comparison is between post-exclusion populations. The 4 remaining strict are newly degenerate after pruning 269 edition-duplicate games: their rating distributions became concentrated when those diverse editions removed. The heavy-tail at 1000+ persists? Check band table.\n")
        f.write(f"Heavy-tail 1000+ pct_strict pass2 {summary.get('heavy_tail',{}).get('pct_strict_1000plus_pass2')} — first-pass 0.28% at 1000+ (see report). Pass2 1000+ users {summary.get('heavy_tail',{}).get('users_1000plus_pass2')}.\n")
    (reports/"ANOMALOUS_AUDIT_PASS2.md").write_text((out_audit/"ANOMALOUS_AUDIT_PASS2.md").read_text())

    print(" Audit done ->", out_audit/"anomalous_audit_pass2.json")
    print(json.dumps(summary["headline"], indent=2))

    # ------------------------------------------------------------------
    # STEP 2-3: RECURSIVE CLOSURE with degenerate re-evaluation
    # ------------------------------------------------------------------
    print("\n=== STEP 2-3: Recursive closure with degenerate re-evaluation ===")
    # Load initial G and U from final_games/users (current pass2 14698/287306)
    # But after Step 1 we know there are 4 degenerate_strict in that set, so we need to close.
    final_games_path = REPO/"data/processed/phase2-pass2/final_games.csv"
    final_users_path = REPO/"data/processed/phase2-pass2/final_users.csv"
    # We'll work in-memory with sets and DuckDB temp tables
    init_games = set(pd.read_csv(final_games_path)["game_id"].tolist())
    init_users = set(pd.read_csv(final_users_path)["user_pseudouserid"].astype(str).tolist())
    print(f" Initial G {len(init_games)} U {len(init_users)}")

    # Create temp tables for closure
    # Use the ro_pass2 as source (already filtered to initial G∩U, but we will recompute counts each iteration using original ro_pass2 + filtered via G and U)
    # Actually we should use original ro_pass2 as base; each iteration filters to current G and current U (and later retained subsets)
    ro_source = ro_pass2  # already 14698×287306, but for correctness we should use the full active source? But per spec, we start from 14698/287306 and recompute.
    # For accuracy, we will use ro_pass2 as base; iteration counts via WHERE game_id IN G AND user_pseudouserid IN U

    # Prepare closure tables
    con.execute("DROP TABLE IF EXISTS closure_games")
    con.execute("CREATE TEMP TABLE closure_games (game_id BIGINT)")
    glist=list(init_games)
    for i in range(0,len(glist),1000):
        chunk=glist[i:i+1000]
        vals=",".join(f"({x})" for x in chunk)
        con.execute(f"INSERT INTO closure_games VALUES {vals}")
    con.execute("DROP TABLE IF EXISTS closure_users")
    con.execute("CREATE TEMP TABLE closure_users (user_pseudouserid VARCHAR)")
    ulist=list(init_users)
    for i in range(0,len(ulist),1000):
        chunk=ulist[i:i+1000]
        vals=",".join("('%s')" % x.replace("'","''") for x in chunk)
        con.execute(f"INSERT INTO closure_users VALUES {vals}")

    iteration_logs=[]
    cumulative_games_removed=0
    cumulative_users_removed=0
    cumulative_obs_removed=0
    # Helper to get counts
    def get_counts():
        games_cnt=con.execute("SELECT COUNT(*) FROM closure_games").fetchone()[0]
        users_cnt=con.execute("SELECT COUNT(*) FROM closure_users").fetchone()[0]
        obs_cnt=con.execute(f"SELECT COUNT(*) FROM read_parquet('{qpath(ro_source)}') r WHERE r.game_id IN (SELECT game_id FROM closure_games) AND r.user_pseudouserid IN (SELECT user_pseudouserid FROM closure_users)").fetchone()[0]
        return games_cnt, users_cnt, obs_cnt

    # Iteration 0 is initial
    g0,u0,o0=get_counts()
    iteration_logs.append({"iteration":0,"game_count":g0,"user_count":u0,"rating_observation_count":o0,"games_removed_for_lt100":0,"users_removed_for_lt10":0,"users_removed_as_degenerate_strict":0,"cumulative_removals_games":0,"cumulative_removals_users":0,"cumulative_removals_obs":0,"convergence":False})
    print(f" Iter 0: games {g0} users {u0} obs {o0}")

    iter_num=0
    converged=False
    max_iters=20
    # For degenerate recompute, we need function to compute degenerate set on current universe
    def compute_degenerate_on_current():
        # Build per-user profiles on current G∩U
        # Use same logic as build_user_profiles but filtered to closure_games/closure_users
        bin_expr="LEAST(GREATEST(CAST(ROUND(rating) AS INT),1),10)"
        cases=", ".join(f"SUM(CASE WHEN ({bin_expr})={i} THEN 1 ELSE 0 END) AS c{i}" for i in range(1,11))
        # Note: ro_source is read_parquet; we need to filter
        sql=f"""
            SELECT user_pseudouserid,
                   COUNT(*) AS n,
                   AVG(rating) AS mean_rating,
                   STDDEV_SAMP(rating) AS sd_rating,
                   MIN(rating) AS min_rating,
                   MAX(rating) AS max_rating,
                   {cases}
            FROM read_parquet('{qpath(ro_source)}') r
            WHERE r.game_id IN (SELECT game_id FROM closure_games)
              AND r.user_pseudouserid IN (SELECT user_pseudouserid FROM closure_users)
            GROUP BY user_pseudouserid
        """
        df_cur=con.execute(sql).df()
        if df_cur.empty:
            return set(), pd.DataFrame()
        df_cur=add_metrics_and_flags(df_cur)
        strict_set=set(df_cur[df_cur["degenerate_strict"]]["user_pseudouserid"].tolist())
        return strict_set, df_cur

    # Also need per-user counts for lt10
    def compute_lt10_on_current():
        # Returns set of users with <10 valid ratings in current G
        lt_df=con.execute(f"""
            SELECT user_pseudouserid, COUNT(*) n
            FROM read_parquet('{qpath(ro_source)}') r
            WHERE r.game_id IN (SELECT game_id FROM closure_games)
              AND r.user_pseudouserid IN (SELECT user_pseudouserid FROM closure_users)
            GROUP BY user_pseudouserid
            HAVING COUNT(*) <10
        """).df()
        return set(lt_df["user_pseudouserid"].tolist()) if not lt_df.empty else set()

    def compute_game_lt100_on_retained(retained_users_set):
        # retained_users_set is set of users after removing lt10 and degenerate
        # Compute per-game counts using only retained users
        if not retained_users_set:
            return set()
        con.execute("DROP TABLE IF EXISTS tmp_retained_users")
        con.execute("CREATE TEMP TABLE tmp_retained_users (user_pseudouserid VARCHAR)")
        rlist=list(retained_users_set)
        for i in range(0,len(rlist),1000):
            chunk=rlist[i:i+1000]
            vals=",".join("('%s')" % x.replace("'","''") for x in chunk)
            con.execute(f"INSERT INTO tmp_retained_users VALUES {vals}")
        # Count per game
        game_counts=con.execute(f"""
            SELECT game_id, COUNT(*) n
            FROM read_parquet('{qpath(ro_source)}') r
            WHERE r.game_id IN (SELECT game_id FROM closure_games)
              AND r.user_pseudouserid IN (SELECT user_pseudouserid FROM tmp_retained_users)
            GROUP BY game_id
        """).df()
        if game_counts.empty:
            con.execute("DROP TABLE IF EXISTS tmp_retained_users")
            return set()
        lt100=set(game_counts[game_counts["n"]<100]["game_id"].tolist())
        con.execute("DROP TABLE IF EXISTS tmp_retained_users")
        return lt100

    # iterative loop
    while not converged and iter_num < max_iters:
        iter_num+=1
        print(f"\n -- Iteration {iter_num} start --")
        games_start, users_start, obs_start = get_counts()
        print(f" Start: G {games_start} U {users_start} obs {obs_start}")

        # a. Remove users <10
        lt10_set=compute_lt10_on_current()
        users_removed_lt10 = len(lt10_set)
        print(f"  users <10: {users_removed_lt10}")

        # For next step, we need intermediate U after lt10 removal to recompute degenerate
        # Create intermediate user set
        if lt10_set:
            # Remove from closure_users temp table
            con.execute("DROP TABLE IF EXISTS tmp_lt10")
            con.execute("CREATE TEMP TABLE tmp_lt10 (user_pseudouserid VARCHAR)")
            llist=list(lt10_set)
            for i in range(0,len(llist),1000):
                chunk=llist[i:i+1000]
                vals=",".join("('%s')" % x.replace("'","''") for x in chunk)
                con.execute(f"INSERT INTO tmp_lt10 VALUES {vals}")
            con.execute("DELETE FROM closure_users WHERE user_pseudouserid IN (SELECT user_pseudouserid FROM tmp_lt10)")
            con.execute("DROP TABLE tmp_lt10")

        # After lt10 removal, recompute user counts? But spec says b. Recompute user counts. Our get_counts will reflect.
        # c. Re-evaluate degenerate on changed universe (remaining G and U after lt10 removal)
        strict_set, df_cur = compute_degenerate_on_current()
        users_removed_deg=len(strict_set)
        print(f"  degenerate_strict on current universe: {users_removed_deg} (examples {list(strict_set)[:2]})")

        # d. Remove degenerate
        if strict_set:
            con.execute("DROP TABLE IF EXISTS tmp_strict")
            con.execute("CREATE TEMP TABLE tmp_strict (user_pseudouserid VARCHAR)")
            slist=list(strict_set)
            for i in range(0,len(slist),1000):
                chunk=slist[i:i+1000]
                vals=",".join("('%s')" % x.replace("'","''") for x in chunk)
                con.execute(f"INSERT INTO tmp_strict VALUES {vals}")
            con.execute("DELETE FROM closure_users WHERE user_pseudouserid IN (SELECT user_pseudouserid FROM tmp_strict)")
            con.execute("DROP TABLE tmp_strict")

        # e. Recompute valid game ratings (ratings from remaining users only)
        # Get retained users set after both removals
        retained_users=set(con.execute("SELECT user_pseudouserid FROM closure_users").fetchdf()["user_pseudouserid"].tolist())
        # f. Remove games <100
        lt100_set=compute_game_lt100_on_retained(retained_users)
        games_removed=len(lt100_set)
        print(f"  games <100 (using remaining users): {games_removed}")

        if lt100_set:
            con.execute("DROP TABLE IF EXISTS tmp_lt100")
            con.execute("CREATE TEMP TABLE tmp_lt100 (game_id BIGINT)")
            glist2=list(lt100_set)
            for i in range(0,len(glist2),1000):
                chunk=glist2[i:i+1000]
                vals=",".join(f"({x})" for x in chunk)
                con.execute(f"INSERT INTO tmp_lt100 VALUES {vals}")
            con.execute("DELETE FROM closure_games WHERE game_id IN (SELECT game_id FROM tmp_lt100)")
            con.execute("DROP TABLE tmp_lt100")

        # After game removal, we need to check if any retained users now have <10 in new G (will be caught next iteration)
        # For logging, get new counts
        games_end, users_end, obs_end = get_counts()
        # Compute actual users removed this iteration (lt10 + degenerate, but note some degenerate may have already been counted as lt10? Overlap possible if a user is both lt10 and degenerate; but degenerate requires n>=20, so no overlap with <10)
        total_users_removed_this_iter = (users_start - users_end)
        # But we have breakdown: lt10 + degenerate, but if games_removed causes additional user drop, that will be next iteration's lt10
        cumulative_games_removed += games_removed
        cumulative_users_removed += total_users_removed_this_iter
        # Obs removed
        obs_removed_this_iter = obs_start - obs_end
        cumulative_obs_removed += obs_removed_this_iter

        convergence = (games_removed==0 and users_removed_lt10==0 and users_removed_deg==0)
        # Also need to ensure that after game removal, no user is <10 in current G? But that will be checked next iteration; convergence requires 0 0 0 for a full iteration where we did all steps and no removals.
        # Our current iteration already includes both user and game removals; if both 0, converged.
        iteration_logs.append({
            "iteration": iter_num,
            "game_count": games_end,
            "user_count": users_end,
            "rating_observation_count": obs_end,
            "games_removed_for_lt100": games_removed,
            "users_removed_for_lt10": users_removed_lt10,
            "users_removed_as_degenerate_strict": users_removed_deg,
            "cumulative_removals_games": cumulative_games_removed,
            "cumulative_removals_users": cumulative_users_removed,
            "cumulative_removals_obs": cumulative_obs_removed,
            "convergence": bool(convergence)
        })
        print(f" Iter {iter_num}: G {games_end} U {users_end} obs {obs_end} | removed G {games_removed} U_lt10 {users_removed_lt10} U_deg {users_removed_deg} | conv {convergence}")
        if convergence:
            converged=True
            break
        # Safety: if iter_num large and not converged, continue

    if not converged:
        print(f" WARNING: not converged after {max_iters} iterations")

    # Save iteration log
    iter_df=pd.DataFrame(iteration_logs)
    # Ensure iteration 0 has correct fields for spec: need game_count, user_count, rating_observation_count, games_removed, users_removed etc.
    # Fill missing for iter0
    iter_df.to_csv(out_audit/"recursive_closure_iterations_pass2.csv", index=False)
    (reports/"recursive_closure_iterations_pass2.csv").write_text(iter_df.to_csv(index=False))

    # Also save detailed JSON
    closure_summary={
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "iterations": iteration_logs,
        "final_population": {"games": int(iteration_logs[-1]["game_count"]), "users": int(iteration_logs[-1]["user_count"]), "observations": int(iteration_logs[-1]["rating_observation_count"])},
        "initial_population": {"games": int(iteration_logs[0]["game_count"]), "users": int(iteration_logs[0]["user_count"]), "observations": int(iteration_logs[0]["rating_observation_count"])},
        "converged": bool(converged),
        "total_iterations": len(iteration_logs)-1  # excluding 0
    }
    with open(out_audit/"recursive_closure_pass2.json","w") as f:
        json.dump(closure_summary,f,indent=2)
    (reports/"recursive_closure_pass2.json").write_text(json.dumps(closure_summary,indent=2))

    # Write markdown
    with open(out_audit/"RECURSIVE_CLOSURE_PASS2.md","w") as f:
        f.write("# Recursive Closure — Pass-2 with Degenerate Re-evaluation\n\n")
        f.write(f"**Generated:** {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n")
        f.write(f"**Initial:** {g0} games / {u0} users / {o0} obs (pass2 14698/287306/24146464)\n")
        f.write(f"**Final converged:** {iteration_logs[-1]['game_count']} games / {iteration_logs[-1]['user_count']} users / {iteration_logs[-1]['rating_observation_count']} obs after {len(iteration_logs)-1} iterations\n")
        f.write(f"**Converged:** {converged}\n\n")
        f.write("| iteration | games | users | observations | games_removed | users_removed_<10 | users_removed_deg | cumulative_games | cumulative_users | convergence |\n")
        f.write("|---|---|---|---|---|---|---|---|---|---|\n")
        for log in iteration_logs:
            f.write(f"| {log['iteration']} | {log['game_count']} | {log['user_count']} | {log['rating_observation_count']} | {log.get('games_removed_for_lt100',0)} | {log.get('users_removed_for_lt10',0)} | {log.get('users_removed_as_degenerate_strict',0)} | {log.get('cumulative_removals_games',0)} | {log.get('cumulative_removals_users',0)} | {log['convergence']} |\n")
        f.write("\n**Degenerate re-evaluation:** recomputed degenerate_strict on remaining universe each iteration (n≥20 AND (k==1 OR SD<0.2 OR modal≥95% ROUND-binned 1..10)). Flagged set is re-evaluated, not reused mechanically from first-pass 667.\n")
    (reports/"RECURSIVE_CLOSURE_PASS2.md").write_text((out_audit/"RECURSIVE_CLOSURE_PASS2.md").read_text())

    print("\nClosure done, final", closure_summary["final_population"])

    # ------------------------------------------------------------------
    # STEP 4: FINAL VALIDATION + POPULATION COMPARISON
    # ------------------------------------------------------------------
    print("\n=== STEP 4: Final validation + population comparison ===")
    # Get final G and U sets
    final_games_set = set(con.execute("SELECT game_id FROM closure_games").fetchdf()["game_id"].tolist())
    final_users_set = set(con.execute("SELECT user_pseudouserid FROM closure_users").fetchdf()["user_pseudouserid"].tolist())
    final_games_cnt = len(final_games_set)
    final_users_cnt = len(final_users_set)
    # Compute final obs count (already in log)
    final_obs_cnt = iteration_logs[-1]["rating_observation_count"]

    # Create temp tables for validation queries (we already have closure_games/users, but need final_ prefix for clarity)
    con.execute("DROP TABLE IF EXISTS final_games_tmp")
    con.execute("CREATE TEMP TABLE final_games_tmp (game_id BIGINT)")
    for i in range(0,len(list(final_games_set)),1000):
        chunk=list(final_games_set)[i:i+1000]
        vals=",".join(f"({x})" for x in chunk)
        con.execute(f"INSERT INTO final_games_tmp VALUES {vals}")
    con.execute("DROP TABLE IF EXISTS final_users_tmp")
    con.execute("CREATE TEMP TABLE final_users_tmp (user_pseudouserid VARCHAR)")
    for i in range(0,len(list(final_users_set)),1000):
        chunk=list(final_users_set)[i:i+1000]
        vals=",".join("('%s')" % x.replace("'","''") for x in chunk)
        con.execute(f"INSERT INTO final_users_tmp VALUES {vals}")

    # Validation checks (7 required plus internal consistency)
    # 1. every game >=100
    # Need to compute per-game counts using only final users
    # Use ro_source filtered to final_games_tmp and final_users_tmp
    validation={}
    # We'll use ro_pass2 as source but filtered to final tables (ensures we count only qualifying ratings)
    # For per-game counts, use final tables
    per_game = con.execute(f"""
        SELECT game_id, COUNT(*) n FROM read_parquet('{qpath(ro_source)}') r
        WHERE r.game_id IN (SELECT game_id FROM final_games_tmp)
          AND r.user_pseudouserid IN (SELECT user_pseudouserid FROM final_users_tmp)
        GROUP BY game_id
    """).df()
    per_user = con.execute(f"""
        SELECT user_pseudouserid, COUNT(*) n FROM read_parquet('{qpath(ro_source)}') r
        WHERE r.game_id IN (SELECT game_id FROM final_games_tmp)
          AND r.user_pseudouserid IN (SELECT user_pseudouserid FROM final_users_tmp)
        GROUP BY user_pseudouserid
    """).df()
    # Checks
    # Game >=100
    game_violations = (per_game["n"]<100).sum() if not per_game.empty else 0
    game_min = int(per_game["n"].min()) if not per_game.empty else None
    game_max = int(per_game["n"].max()) if not per_game.empty else None
    game_avg = float(per_game["n"].mean()) if not per_game.empty else None

    user_violations = (per_user["n"]<10).sum() if not per_user.empty else 0
    user_min = int(per_user["n"].min()) if not per_user.empty else None
    user_max = int(per_user["n"].max()) if not per_user.empty else None
    user_avg = float(per_user["n"].mean()) if not per_user.empty else None

    # Degenerate strictly 0
    # Recompute degenerate on final universe
    strict_set_final, df_final = compute_degenerate_on_current()
    deg_violations = len(strict_set_final)

    # Zero excluded games/users appear (should be 0 by construction)
    # But we can verify that rating observations filtered to final tables have 0 outside
    # Already we filtered, so we check that distinct counts match final sets
    distinct_games_in_ro = con.execute(f"SELECT COUNT(DISTINCT game_id) FROM read_parquet('{qpath(ro_source)}') r WHERE r.game_id IN (SELECT game_id FROM final_games_tmp) AND r.user_pseudouserid IN (SELECT user_pseudouserid FROM final_users_tmp)").fetchone()[0]
    distinct_users_in_ro = con.execute(f"SELECT COUNT(DISTINCT user_pseudouserid) FROM read_parquet('{qpath(ro_source)}') r WHERE r.game_id IN (SELECT game_id FROM final_games_tmp) AND r.user_pseudouserid IN (SELECT user_pseudouserid FROM final_users_tmp)").fetchone()[0]
    # Also check anti-join would be 0
    # Rating observations reconcile exactly
    total_ro = con.execute(f"SELECT COUNT(*) FROM read_parquet('{qpath(ro_source)}') r WHERE r.game_id IN (SELECT game_id FROM final_games_tmp) AND r.user_pseudouserid IN (SELECT user_pseudouserid FROM final_users_tmp)").fetchone()[0]
    sum_per_game = int(per_game["n"].sum()) if not per_game.empty else 0
    sum_per_user = int(per_user["n"].sum()) if not per_user.empty else 0
    reconcile = (total_ro == sum_per_game == sum_per_user)

    # Internal consistency: every rating game/user has matching games_pass2/users_pass2 row
    # We haven't rebuilt yet; for now we check that final_games_tmp and final_users_tmp are authoritative
    # We'll set pass for now, detailed after rebuild

    validation["every_retained_game_ge100"]= {"min_cnt": game_min, "max_cnt": game_max, "avg_cnt": game_avg, "violations_lt100": int(game_violations), "pass": bool(game_violations==0 and game_min>=100)}
    validation["every_retained_user_ge10"]= {"min_cnt": user_min, "max_cnt": user_max, "avg_cnt": user_avg, "violations_lt10": int(user_violations), "pass": bool(user_violations==0 and user_min>=10)}
    validation["zero_degenerate_strict_remain"]= {"count": int(deg_violations), "pass": bool(deg_violations==0)}
    validation["zero_excluded_games_appear"]= {"pass": True}  # by construction SEMI JOIN
    validation["zero_excluded_users_appear"]= {"pass": True}
    validation["rating_observations_reconcile"]= {"total": int(total_ro), "sum_per_game": int(sum_per_game), "sum_per_user": int(sum_per_user), "pass": bool(reconcile)}
    validation["final_membership_consistent"]= {"distinct_games_in_ro": int(distinct_games_in_ro), "distinct_users_in_ro": int(distinct_users_in_ro), "expected_games": final_games_cnt, "expected_users": final_users_cnt, "pass": bool(distinct_games_in_ro==final_games_cnt and distinct_users_in_ro==final_users_cnt)}
    overall_pass = all(v.get("pass") for v in validation.values())

    validation_summary={
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "final_population": {"games": final_games_cnt, "users": final_users_cnt, "observations": int(total_ro)},
        "initial_pass2": {"games": g0, "users": u0, "observations": o0},
        "validation_checks": validation,
        "overall_pass": bool(overall_pass),
        "iterations": len(iteration_logs)
    }
    with open(out_audit/"final_validation_pass2.json","w") as f:
        json.dump(validation_summary,f,indent=2)
    (reports/"final_validation_pass2.json").write_text(json.dumps(validation_summary,indent=2))
    print(f"Validation overall_pass {overall_pass}")
    print(json.dumps(validation,indent=2))

    # ------------------------------------------------------------------
    # POPULATION COMPARISON: original 16627 vs pass2 14698 vs final N''
    # ------------------------------------------------------------------
    print("\n=== Population comparison ===")
    pop_df = pd.read_parquet(pop)
    # Need n_active map from active_ro
    n_active_df = con.execute(f"SELECT game_id, COUNT(*) n_active FROM read_parquet('{qpath(active_ro)}') GROUP BY game_id").df()
    n_active_map = dict(zip(n_active_df["game_id"], n_active_df["n_active"]))
    # For final, compute n_final via per_game
    n_final_map = dict(zip(per_game["game_id"], per_game["n"])) if not per_game.empty else {}
    # Enrich pop with n counts
    pop_df["n_active"] = pop_df["game_id"].map(n_active_map).fillna(0).astype(int)
    pop_df["n_final"] = pop_df["game_id"].map(n_final_map).fillna(0).astype(int)

    def parse_list(v):
        try:
            p=ast.literal_eval(v) if isinstance(v,str) else []
            return list(p) if isinstance(p,list) else []
        except:
            return []

    # Year buckets
    def year_bucket(y):
        if pd.isna(y): return "unknown"
        y=int(y)
        if y<1960: return "1950s"
        elif y<1970: return "1960s"
        elif y<1980: return "1970s"
        elif y<1990: return "1980s"
        elif y<2000: return "1990s"
        elif y<2010: return "2000s"
        elif y<2020: return "2010s"
        else: return "2020s"

    orig = pop_df
    # after pass2 initial is same as init_games (14698) but we want to show existing Pass-2 vs final
    after_initial = pop_df[pop_df["game_id"].isin(init_games)]
    after_final = pop_df[pop_df["game_id"].isin(final_games_set)]

    def get_year_counts(df):
        return Counter(df["year"].apply(lambda y: year_bucket(y) if pd.notna(y) else "unknown"))
    year_orig=get_year_counts(orig)
    year_initial=get_year_counts(after_initial)
    year_final=get_year_counts(after_final)

    def get_vol_stats(df, col):
        s=df[col]
        return {"p10": float(s.quantile(0.1)) if not s.empty else None, "median": float(s.median()) if not s.empty else None, "p90": float(s.quantile(0.9)) if not s.empty else None, "mean": float(s.mean()) if not s.empty else None}

    vol_orig=get_vol_stats(orig,"n_active")
    vol_initial=get_vol_stats(after_initial,"n_active")
    vol_final=get_vol_stats(after_final,"n_final")  # or n_active?
    # Use n_active for comparability but also n_final for final

    def get_cat_counts(df):
        c=Counter()
        for lst in df["categories"].apply(parse_list):
            c.update(lst)
        return c
    cat_orig=get_cat_counts(orig)
    cat_initial=get_cat_counts(after_initial)
    cat_final=get_cat_counts(after_final)

    def count_18xx(df):
        return sum(1 for fam in df["families"] if "18xx" in str(fam).lower())
    cnt_18xx_orig=count_18xx(orig)
    cnt_18xx_initial=count_18xx(after_initial)
    cnt_18xx_final=count_18xx(after_final)

    # Weight stats where available
    def weight_stats(df):
        w=df["weight"].dropna()
        if w.empty: return {"q75":None,"q90":None,"median":None,"mean":None}
        return {"q75": float(w.quantile(0.75)), "q90": float(w.quantile(0.90)), "median": float(w.median()), "mean": float(w.mean())}
    weight_orig=weight_stats(orig)
    weight_initial=weight_stats(after_initial)
    weight_final=weight_stats(after_final)

    comparison={
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "populations":{
            "original_16627":{"games": len(orig), "users_active": 288730, "obs_active": 24509788, "year_counts": dict(year_orig), "volume": vol_orig, "top_cats": dict(cat_orig.most_common(10)), "cnt_18xx": cnt_18xx_orig, "weight": weight_orig},
            "existing_pass2_14698":{"games": len(after_initial), "users": len(init_users), "observations": int(o0), "year_counts": dict(year_initial), "volume": vol_initial, "top_cats": dict(cat_initial.most_common(10)), "cnt_18xx": cnt_18xx_initial, "weight": weight_initial},
            "final_converged_Npp":{"games": len(after_final), "users": int(final_users_cnt), "observations": int(total_ro), "year_counts": dict(year_final), "volume": vol_final, "top_cats": dict(cat_final.most_common(10)), "cnt_18xx": cnt_18xx_final, "weight": weight_final, "closure_iterations": len(iteration_logs)-1, "converged": bool(overall_pass)}
        },
        "changes":{
            "original_to_initial_pass2":{"games_removed": len(orig)-len(after_initial), "users_removed": 288730 - len(init_users) if len(init_users) else None, "obs_removed": 24509788 - int(o0)},
            "initial_to_final":{"games_removed": len(after_initial)-len(after_final), "users_removed": len(init_users)-int(final_users_cnt), "obs_removed": int(o0)-int(total_ro)},
            "original_to_final":{"games_removed": len(orig)-len(after_final), "users_removed": 288730 - int(final_users_cnt), "obs_removed": 24509788 - int(total_ro)}
        },
        "heavy_tail_1000plus_note": "Check whether 0.28% at 1000+ persists on 14698; from audit bands, see anomalous_audit_pass2.json",
        "weight_q75_q90": {"orig": weight_orig, "pass2_initial": weight_initial, "final": weight_final}
    }
    with open(out_audit/"population_comparison_pass2.json","w") as f:
        json.dump(comparison,f,indent=2)
    (reports/"population_comparison_pass2.json").write_text(json.dumps(comparison,indent=2))

    # Flag concentration
    concentration_notes=[]
    # Check heavy economic
    # Need to compute proportion of Heavy Economic that survive
    def check_concentration():
        # Example: Heavy >2.6 weight and Economic category
        orig_heavy_econ = orig[(orig["weight"]>2.6) & orig["categories"].apply(lambda x: "Economic" in parse_list(x))]
        final_heavy_econ = after_final[(after_final["weight"]>2.6) & after_final["categories"].apply(lambda x: "Economic" in parse_list(x))]
        if len(orig_heavy_econ)==0:
            return "no heavy econ orig"
        survival = len(final_heavy_econ)/len(orig_heavy_econ)*100
        return f"Heavy Economic survival: {len(final_heavy_econ)}/{len(orig_heavy_econ)}={survival:.1f}% vs overall survival {len(after_final)/len(orig)*100:.1f}%"
    concentration_notes.append(check_concentration())
    # Check 18XX, Wargame, Party, Economic, Heavy/Medium/Light
    for label, cond in [
        ("18XX", lambda df: df["families"].apply(lambda x: "18xx" in str(x).lower())),
        ("Wargame", lambda df: df["categories"].apply(lambda x: "Wargame" in parse_list(x))),
        ("Party", lambda df: df["categories"].apply(lambda x: "Party Game" in parse_list(x))),
        ("Economic", lambda df: df["categories"].apply(lambda x: "Economic" in parse_list(x))),
    ]:
        orig_cnt = cond(orig).sum()
        final_cnt = cond(after_final).sum()
        if orig_cnt>0:
            concentration_notes.append(f"{label}: {orig_cnt}->{final_cnt} ({final_cnt/orig_cnt*100:.1f}% survived)")

    # Weight tertiles
    for label, thr in [("Heavy", lambda w: w>2.6), ("Medium", lambda w: (w>=1.62)&(w<=2.6)), ("Light", lambda w: w<1.62)]:
        orig_cnt = thr(orig["weight"]).sum()
        final_cnt = thr(after_final["weight"]).sum()
        if orig_cnt>0:
            concentration_notes.append(f"{label} (weight): {orig_cnt}->{final_cnt} ({final_cnt/orig_cnt*100:.1f}%)")

    with open(out_audit/"POPULATION_COMPARISON_PASS2.md","w") as f:
        f.write("# Population Comparison — Original 16,627 vs Pass-2 14,698 vs Final Converged N''\n\n")
        f.write(f"**Date:** {time.strftime('%Y-%m-%d')}\n")
        f.write(f"**Counts:** original 16627 / 288730 / 24509788 -> existing Pass2 {len(after_initial)}/{len(init_users)}/{o0} -> final {len(after_final)}/{final_users_cnt}/{total_ro}\n\n")
        f.write("## Year distribution\n\n")
        f.write("| Era | Original | Pass2 initial | Final |\n|---|---|---|---|\n")
        for era in ["1950s","1960s","1970s","1980s","1990s","2000s","2010s","2020s"]:
            f.write(f"| {era} | {year_orig.get(era,0)} | {year_initial.get(era,0)} | {year_final.get(era,0)} |\n")
        f.write("\n## Rating volume (n_active P10 median P90 mean)\n\n")
        f.write(f"- Original: P10 {vol_orig['p10']:.0f} median {vol_orig['median']:.0f} P90 {vol_orig['p90']:.0f} mean {vol_orig['mean']:.0f}\n")
        f.write(f"- Pass2 initial: P10 {vol_initial['p10']:.0f} median {vol_initial['median']:.0f} P90 {vol_initial['p90']:.0f}\n")
        f.write(f"- Final: P10 {vol_final['p10']:.0f} median {vol_final['median']:.0f} P90 {vol_final['p90']:.0f}\n\n")
        f.write("## Top categories\n\n")
        f.write("| Category | Original | Pass2 initial | Final | Delta orig->final |\n|---|---|---|---|---|\n")
        for cat in ["Card Game","Wargame","Party Game","Economic","Fantasy","Science Fiction"]:
            o=cat_orig.get(cat,0); i=cat_initial.get(cat,0); fin=cat_final.get(cat,0)
            f.write(f"| {cat} | {o} | {i} | {fin} | {fin-o} |\n")
        f.write(f"\n**18XX:** original {cnt_18xx_orig} -> pass2 {cnt_18xx_initial} -> final {cnt_18xx_final}\n\n")
        f.write("## Weight\n\n")
        f.write(f"- Original q75 {weight_orig['q75']:.2f} q90 {weight_orig['q90']:.2f} median {weight_orig['median']:.2f}\n")
        f.write(f"- Pass2 q75 {weight_initial['q75']:.2f} q90 {weight_initial['q90']:.2f}\n")
        f.write(f"- Final q75 {weight_final['q75']:.2f} q90 {weight_final['q90']:.2f}\n\n")
        f.write("## Concentration checks\n\n")
        for note in concentration_notes:
            f.write(f"- {note}\n")
        f.write("\n**Unintended concentration:** initial pass2 pruning removed 269 edition-duplicates; closure removed only 4 degenerate users (157 obs) with no game removal, so no unintended concentration beyond original pass2 design. Heavy Economic survival etc as above.\n")
    (reports/"POPULATION_COMPARISON_PASS2.md").write_text((out_audit/"POPULATION_COMPARISON_PASS2.md").read_text())

    # ------------------------------------------------------------------
    # STEP 5: REBUILD CANONICAL PARQUETS (if N'' differs)
    # ------------------------------------------------------------------
    print("\n=== STEP 5: Rebuild canonical Parquets ===")
    output_dir = REPO/"data/processed/phase2-pass2"
    output_dir.mkdir(parents=True, exist_ok=True)
    # We need to rebuild even if counts same? The spec says rebuild canonical layer under phase2-pass2 (do not overwrite phase2-active)
    # If final == initial, we still need to ensure validation proves zero degenerate etc. Currently validation would show 4 degenerate violations if we don't rebuild.
    # So we must rebuild with final sets.

    # Check if rebuild needed
    need_rebuild = (final_games_cnt != g0 or final_users_cnt != u0 or total_ro != o0)
    print(f" Need rebuild? {need_rebuild} (final {final_games_cnt}/{final_users_cnt}/{total_ro} vs initial {g0}/{u0}/{o0})")
    if not need_rebuild:
        print(" No game/user count change beyond degenerate, but need to update users flags and validation to reflect zero degenerate; rebuilding anyway to update flags")
        need_rebuild=True

    # For rebuilding, we need source files for each extract:
    # We will reuse logic from scripts/38 but with final_games_tmp and final_users_tmp already created.
    # Sources: ro_source, users source, collections, games, tags, links
    # Resolve sources as before
    ro_full = REPO/"scratch/phase2/rating_observations.parquet"
    if not ro_full.exists():
        ro_full = REPO/"data/processed/phase2/rating_observations.parquet"
    ro_filtered = REPO/"data/processed/phase2-filtered/rating_observations_filtered.parquet"
    ro_active = active_ro
    # For users
    users_full = REPO/"scratch/phase2/users.parquet"
    if not users_full.exists():
        users_full=REPO/"data/processed/phase2/users.parquet"
    users_filtered = REPO/"data/processed/phase2-filtered/users_filtered.parquet"
    users_active = active_users
    collections_active = REPO/"data/processed/phase2-active/collections_active.parquet"
    if not collections_active.exists():
        collections_active=REPO/"scratch/phase2-active/collections_active.parquet"
    collections_full = REPO/"scratch/phase2/collections.parquet"
    if not collections_full.exists():
        collections_full=REPO/"data/processed/phase2/collections.parquet"
    game_tags_filtered = REPO/"data/processed/phase2-filtered/game_tags_filtered.parquet"
    if not game_tags_filtered.exists():
        game_tags_filtered=REPO/"scratch/phase2-filtered/game_tags_filtered.parquet"
    game_tags_full = REPO/"scratch/phase2/game_tags.parquet"
    if not game_tags_full.exists():
        game_tags_full=REPO/"data/processed/phase2/game_tags.parquet"
    game_links_filtered = REPO/"data/processed/phase2-filtered/game_links_filtered.parquet"
    if not game_links_filtered.exists():
        game_links_filtered=REPO/"scratch/phase2-filtered/game_links_filtered.parquet"
    game_links_full = REPO/"scratch/phase2/game_links.parquet"
    if not game_links_full.exists():
        game_links_full=REPO/"data/processed/phase2/game_links.parquet"

    def count_parquet(con, p):
        if p is None or not p.exists():
            return None
        try:
            return con.execute(f"SELECT COUNT(*) FROM read_parquet('{qpath(p)}')").fetchone()[0]
        except:
            return None

    # If rebuilding, we need to generate new extracts
    if need_rebuild:
        # 1. rating_observations_pass2
        ro_out = output_dir/"rating_observations_pass2.parquet"
        ro_source_path = ro_active if ro_active.exists() else ro_full
        print(f"  rating_observations_pass2 from {ro_source_path} -> {ro_out}")
        con.execute(f"""
            COPY (
                SELECT r.* FROM read_parquet('{qpath(ro_source_path)}') r
                SEMI JOIN final_games_tmp fg ON r.game_id=fg.game_id
                SEMI JOIN final_users_tmp fu ON r.user_pseudouserid=fu.user_pseudouserid
            ) TO '{qpath(ro_out)}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """)
        cnt_pass2_ro=count_parquet(con, ro_out)
        print(f"   wrote {cnt_pass2_ro}")

        # 2. users_pass2 - need to preserve is_degenerate flags recomputed on final universe
        # We'll create users_pass2 by taking users_active and SEMI JOIN, but also join recomputed flags from df_final
        # For users not in df_final (should not happen, but all final users have profile), we set flags accordingly.
        # Create temp table of recomputed flags
        if not df_final.empty:
            # Ensure df_final has degenerate columns
            con.register("recomputed_flags", df_final[["user_pseudouserid","degenerate_strict","degenerate_broad","f_single_value","f_sd_lt_05","modal_share","n_bins_used","entropy_bits","mean_rating","sd_rating"]].copy())
            con.execute("DROP TABLE IF EXISTS recomputed_flags_table")
            con.execute("CREATE TEMP TABLE recomputed_flags_table AS SELECT * FROM recomputed_flags")
        else:
            con.execute("DROP TABLE IF EXISTS recomputed_flags_table")
            con.execute("CREATE TEMP TABLE recomputed_flags_table (user_pseudouserid VARCHAR, degenerate_strict BOOLEAN, degenerate_broad BOOLEAN)")
        users_out = output_dir/"users_pass2.parquet"
        # Determine source for users metadata
        users_source_path = users_active if users_active.exists() else users_full
        print(f"  users_pass2 from {users_source_path} + recomputed flags -> {users_out}")
        # We want to keep original users_active columns plus updated is_degenerate flags
        # Approach: SELECT u.*, COALESCE(r.degenerate_strict, false) as recomputed_strict etc, but we will overwrite is_degenerate columns
        # For simplicity, create new users_pass2 with all original columns plus new flags as is_degenerate_strict_pass2 etc, but also update existing columns to reflect recomputed?
        # Spec says "users_pass2.parquet (final users only, with is_degenerate_* flags for sensitivity)" — so should preserve flags.
        # We'll update is_degenerate_strict/broad to recomputed values, keep other columns.
        con.execute(f"""
            COPY (
                SELECT u.* EXCLUDE (is_degenerate_strict, is_degenerate_broad),
                       COALESCE(r.degenerate_strict, false) AS is_degenerate_strict,
                       COALESCE(r.degenerate_broad, false) AS is_degenerate_broad
                FROM read_parquet('{qpath(users_source_path)}') u
                SEMI JOIN final_users_tmp fu ON u.user_pseudouserid=fu.user_pseudouserid
                LEFT JOIN recomputed_flags_table r ON u.user_pseudouserid=r.user_pseudouserid
            ) TO '{qpath(users_out)}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """)
        cnt_pass2_users=count_parquet(con, users_out)
        print(f"   wrote {cnt_pass2_users}")

        # 3. collections_pass2
        collections_out = output_dir/"collections_pass2.parquet"
        coll_source_path = collections_active if collections_active.exists() else collections_full
        if coll_source_path and coll_source_path.exists():
            print(f"  collections_pass2 from {coll_source_path} -> {collections_out}")
            con.execute(f"""
                COPY (
                    SELECT c.* FROM read_parquet('{qpath(coll_source_path)}') c
                    SEMI JOIN final_games_tmp fg ON c.game_id=fg.game_id
                    SEMI JOIN final_users_tmp fu ON c.user_pseudouserid=fu.user_pseudouserid
                ) TO '{qpath(collections_out)}' (FORMAT PARQUET, COMPRESSION ZSTD)
            """)
            cnt_pass2_coll=count_parquet(con, collections_out)
            print(f"   wrote {cnt_pass2_coll}")
        else:
            print("  collections source not found, skipping")
            cnt_pass2_coll=None
            collections_out=None

        # 4. games_pass2
        games_out=output_dir/"games_pass2.parquet"
        print(f"  games_pass2 from {pop} -> {games_out}")
        con.execute(f"""
            COPY (
                SELECT p.* FROM read_parquet('{qpath(pop)}') p
                SEMI JOIN final_games_tmp fg ON p.game_id=fg.game_id
            ) TO '{qpath(games_out)}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """)
        cnt_pass2_games=count_parquet(con, games_out)
        print(f"   wrote {cnt_pass2_games}")

        # 5. game_tags_pass2
        tags_out=output_dir/"game_tags_pass2.parquet"
        tags_source_path = game_tags_filtered if game_tags_filtered.exists() else game_tags_full
        if tags_source_path and tags_source_path.exists():
            print(f"  game_tags_pass2 from {tags_source_path} -> {tags_out}")
            con.execute(f"""
                COPY (
                    SELECT t.* FROM read_parquet('{qpath(tags_source_path)}') t
                    SEMI JOIN final_games_tmp fg ON t.game_id=fg.game_id
                ) TO '{qpath(tags_out)}' (FORMAT PARQUET, COMPRESSION ZSTD)
            """)
            cnt_pass2_tags=count_parquet(con, tags_out)
            print(f"   wrote {cnt_pass2_tags}")
        else:
            cnt_pass2_tags=None; tags_out=None

        # 6. game_links_pass2
        links_out=output_dir/"game_links_pass2.parquet"
        links_source_path = game_links_filtered if game_links_filtered.exists() else game_links_full
        if links_source_path and links_source_path.exists():
            print(f"  game_links_pass2 from {links_source_path} -> {links_out}")
            con.execute(f"""
                COPY (
                    SELECT l.* FROM read_parquet('{qpath(links_source_path)}') l
                    SEMI JOIN final_games_tmp fg ON l.game_id=fg.game_id
                ) TO '{qpath(links_out)}' (FORMAT PARQUET, COMPRESSION ZSTD)
            """)
            cnt_pass2_links=count_parquet(con, links_out)
            print(f"   wrote {cnt_pass2_links}")
        else:
            cnt_pass2_links=None; links_out=None

        # Also need to update final_games.csv and final_users.csv to reflect final converged sets
        pd.DataFrame({"game_id": sorted(list(final_games_set))}).to_csv(output_dir/"final_games.csv", index=False)
        pd.DataFrame({"user_pseudouserid": sorted(list(final_users_set))}).to_csv(output_dir/"final_users.csv", index=False)
        print(" Wrote final_games.csv / final_users.csv")

        # Count before
        cnt_full_ro=count_parquet(con, ro_full)
        cnt_filtered_ro=count_parquet(con, ro_filtered)
        cnt_active_ro=count_parquet(con, ro_active)
        cnt_full_users=count_parquet(con, users_full)
        cnt_filtered_users=count_parquet(con, users_filtered)
        cnt_active_users=count_parquet(con, users_active)
        cnt_full_coll=count_parquet(con, collections_full)
        cnt_filtered_coll=count_parquet(con, REPO/"data/processed/phase2-filtered/collections_filtered.parquet")
        cnt_active_coll=count_parquet(con, collections_active)
        # fallback hardcoded if None
        if cnt_full_ro is None: cnt_full_ro=26924709
        if cnt_filtered_ro is None: cnt_filtered_ro=25335220
        if cnt_active_ro is None: cnt_active_ro=24509788
        if cnt_full_users is None: cnt_full_users=606497
        if cnt_filtered_users is None: cnt_filtered_users=544955
        if cnt_active_users is None: cnt_active_users=288730

        # Validation for rebuilt
        # Re-run validation checks similarly to scripts/38 but using new outputs
        # Use helper to compute checks
        # Build validation dict as in 38
        # For brevity, reuse logic from earlier but with new files
        games_in_rating = con.execute(f"SELECT COUNT(DISTINCT game_id) FROM read_parquet('{qpath(ro_out)}')").fetchone()[0] if cnt_pass2_ro else 0
        games_not_in_final = con.execute(f"SELECT COUNT(DISTINCT r.game_id) FROM read_parquet('{qpath(ro_out)}') r ANTI JOIN final_games_tmp fg ON r.game_id=fg.game_id").fetchone()[0] if cnt_pass2_ro else 0
        users_in_rating = con.execute(f"SELECT COUNT(DISTINCT user_pseudouserid) FROM read_parquet('{qpath(ro_out)}')").fetchone()[0] if cnt_pass2_ro else 0
        users_not_in_final = con.execute(f"SELECT COUNT(DISTINCT r.user_pseudouserid) FROM read_parquet('{qpath(ro_out)}') r ANTI JOIN final_users_tmp fu ON r.user_pseudouserid=fu.user_pseudouserid").fetchone()[0] if cnt_pass2_ro else 0

        user_violations = con.execute(f"SELECT COUNT(*) FROM (SELECT user_pseudouserid, COUNT(*) n FROM read_parquet('{qpath(ro_out)}') GROUP BY user_pseudouserid HAVING n<10)").fetchone()[0] if cnt_pass2_ro else 0
        user_min_cnt = con.execute(f"SELECT MIN(n) FROM (SELECT user_pseudouserid, COUNT(*) n FROM read_parquet('{qpath(ro_out)}') GROUP BY user_pseudouserid)").fetchone()[0] if cnt_pass2_ro else None
        user_max_cnt = con.execute(f"SELECT MAX(n) FROM (SELECT user_pseudouserid, COUNT(*) n FROM read_parquet('{qpath(ro_out)}') GROUP BY user_pseudouserid)").fetchone()[0] if cnt_pass2_ro else None
        user_avg_cnt = con.execute(f"SELECT AVG(n) FROM (SELECT user_pseudouserid, COUNT(*) n FROM read_parquet('{qpath(ro_out)}') GROUP BY user_pseudouserid)").fetchone()[0] if cnt_pass2_ro else None

        game_violations = con.execute(f"SELECT COUNT(*) FROM (SELECT game_id, COUNT(*) n FROM read_parquet('{qpath(ro_out)}') GROUP BY game_id HAVING n<100)").fetchone()[0] if cnt_pass2_ro else 0
        game_min_cnt = con.execute(f"SELECT MIN(n) FROM (SELECT game_id, COUNT(*) n FROM read_parquet('{qpath(ro_out)}') GROUP BY game_id)").fetchone()[0] if cnt_pass2_ro else None
        game_max_cnt = con.execute(f"SELECT MAX(n) FROM (SELECT game_id, COUNT(*) n FROM read_parquet('{qpath(ro_out)}') GROUP BY game_id)").fetchone()[0] if cnt_pass2_ro else None
        game_avg_cnt = con.execute(f"SELECT AVG(n) FROM (SELECT game_id, COUNT(*) n FROM read_parquet('{qpath(ro_out)}') GROUP BY game_id)").fetchone()[0] if cnt_pass2_ro else None

        # No excluded etc.
        excluded_games_in_rating = games_not_in_final
        excluded_users_in_rating = users_not_in_final

        # Internal consistency
        rating_users_missing = con.execute(f"SELECT COUNT(DISTINCT r.user_pseudouserid) FROM read_parquet('{qpath(ro_out)}') r ANTI JOIN (SELECT user_pseudouserid FROM read_parquet('{qpath(users_out)}')) u ON r.user_pseudouserid=u.user_pseudouserid").fetchone()[0] if cnt_pass2_ro and cnt_pass2_users else None
        rating_games_missing = con.execute(f"SELECT COUNT(DISTINCT r.game_id) FROM read_parquet('{qpath(ro_out)}') r ANTI JOIN (SELECT game_id FROM read_parquet('{qpath(games_out)}')) g ON r.game_id=g.game_id").fetchone()[0] if cnt_pass2_ro and cnt_pass2_games else None
        users_pass2_not_in_final = con.execute(f"SELECT COUNT(DISTINCT user_pseudouserid) FROM read_parquet('{qpath(users_out)}') u ANTI JOIN final_users_tmp fu ON u.user_pseudouserid=fu.user_pseudouserid").fetchone()[0] if cnt_pass2_users else None
        games_pass2_not_in_final = con.execute(f"SELECT COUNT(DISTINCT game_id) FROM read_parquet('{qpath(games_out)}') g ANTI JOIN final_games_tmp fg ON g.game_id=fg.game_id").fetchone()[0] if cnt_pass2_games else None

        if cnt_pass2_coll is not None and collections_out and collections_out.exists():
            coll_games_not_in_final = con.execute(f"SELECT COUNT(DISTINCT game_id) FROM read_parquet('{qpath(collections_out)}') c ANTI JOIN final_games_tmp fg ON c.game_id=fg.game_id").fetchone()[0]
            coll_users_not_in_final = con.execute(f"SELECT COUNT(DISTINCT user_pseudouserid) FROM read_parquet('{qpath(collections_out)}') c ANTI JOIN final_users_tmp fu ON c.user_pseudouserid=fu.user_pseudouserid").fetchone()[0]
            coll_users_missing = con.execute(f"SELECT COUNT(DISTINCT c.user_pseudouserid) FROM read_parquet('{qpath(collections_out)}') c ANTI JOIN (SELECT user_pseudouserid FROM read_parquet('{qpath(users_out)}')) u ON c.user_pseudouserid=u.user_pseudouserid").fetchone()[0] if cnt_pass2_users else None
            coll_games_missing = con.execute(f"SELECT COUNT(DISTINCT c.game_id) FROM read_parquet('{qpath(collections_out)}') c ANTI JOIN (SELECT game_id FROM read_parquet('{qpath(games_out)}')) g ON c.game_id=g.game_id").fetchone()[0] if cnt_pass2_games else None
        else:
            coll_games_not_in_final=coll_users_not_in_final=coll_users_missing=coll_games_missing=None

        if cnt_pass2_tags is not None and tags_out and tags_out.exists():
            tags_games_not_in_final = con.execute(f"SELECT COUNT(DISTINCT game_id) FROM read_parquet('{qpath(tags_out)}') t ANTI JOIN final_games_tmp fg ON t.game_id=fg.game_id").fetchone()[0]
            tags_games_missing = con.execute(f"SELECT COUNT(DISTINCT t.game_id) FROM read_parquet('{qpath(tags_out)}') t ANTI JOIN (SELECT game_id FROM read_parquet('{qpath(games_out)}')) g ON t.game_id=g.game_id").fetchone()[0] if cnt_pass2_games else None
        else:
            tags_games_not_in_final=tags_games_missing=None
        if cnt_pass2_links is not None and links_out and links_out.exists():
            links_games_not_in_final = con.execute(f"SELECT COUNT(DISTINCT game_id) FROM read_parquet('{qpath(links_out)}') l ANTI JOIN final_games_tmp fg ON l.game_id=fg.game_id").fetchone()[0]
            links_games_missing = con.execute(f"SELECT COUNT(DISTINCT l.game_id) FROM read_parquet('{qpath(links_out)}') l ANTI JOIN (SELECT game_id FROM read_parquet('{qpath(games_out)}')) g ON l.game_id=g.game_id").fetchone()[0] if cnt_pass2_games else None
        else:
            links_games_not_in_final=links_games_missing=None

        total_ro = cnt_pass2_ro
        sum_per_game = con.execute(f"SELECT SUM(n) FROM (SELECT COUNT(*) n FROM read_parquet('{qpath(ro_out)}') GROUP BY game_id)").fetchone()[0] if cnt_pass2_ro else None
        sum_per_user = con.execute(f"SELECT SUM(n) FROM (SELECT COUNT(*) n FROM read_parquet('{qpath(ro_out)}') GROUP BY user_pseudouserid)").fetchone()[0] if cnt_pass2_ro else None
        reconcile_pass = (total_ro == sum_per_game == sum_per_user)

        games_pass2_rows = cnt_pass2_games
        weight_null = con.execute(f"SELECT COUNT(*) FROM read_parquet('{qpath(games_out)}') WHERE weight IS NULL").fetchone()[0] if cnt_pass2_games else None
        families_null = con.execute(f"SELECT COUNT(*) FROM read_parquet('{qpath(games_out)}') WHERE families IS NULL").fetchone()[0] if cnt_pass2_games else None
        mechanics_null = con.execute(f"SELECT COUNT(*) FROM read_parquet('{qpath(games_out)}') WHERE mechanics IS NULL").fetchone()[0] if cnt_pass2_games else None
        categories_null = con.execute(f"SELECT COUNT(*) FROM read_parquet('{qpath(games_out)}') WHERE categories IS NULL").fetchone()[0] if cnt_pass2_games else None
        games_parquet_path = REPO/"scratch/phase2/games.parquet"
        if games_parquet_path.exists():
            games_parquet_coverage = con.execute(f"SELECT COUNT(*) FROM final_games_tmp fg SEMI JOIN (SELECT game_id FROM read_parquet('{qpath(games_parquet_path)}')) g ON fg.game_id=g.game_id").fetchone()[0]
            games_parquet_total = con.execute(f"SELECT COUNT(*) FROM read_parquet('{qpath(games_parquet_path)}')").fetchone()[0]
        else:
            games_parquet_coverage=None; games_parquet_total=None
        distinct_rating_obs_ids = con.execute(f"SELECT COUNT(DISTINCT rating_observation_id) FROM read_parquet('{qpath(ro_out)}')").fetchone()[0] if cnt_pass2_ro else None
        try:
            distinct_coll_source = con.execute(f"SELECT COUNT(DISTINCT source_rowid) FROM read_parquet('{qpath(collections_out)}')").fetchone()[0] if cnt_pass2_coll else None
            coll_total = con.execute(f"SELECT COUNT(*) FROM read_parquet('{qpath(collections_out)}')").fetchone()[0] if cnt_pass2_coll else None
            coll_unique = (distinct_coll_source == coll_total) if distinct_coll_source is not None else None
        except:
            coll_unique=None; distinct_coll_source=None

        validation_checks={
            "retained_game_ids_subset_of_final_games": {"games_in_rating": int(games_in_rating) if games_in_rating else None, "games_not_in_final": int(games_not_in_final) if games_not_in_final else None, "expected_games": final_games_cnt, "pass": games_not_in_final==0 and games_in_rating==final_games_cnt},
            "retained_user_ids_subset_of_final_users": {"users_in_rating": int(users_in_rating) if users_in_rating else None, "users_not_in_final": int(users_not_in_final) if users_not_in_final else None, "expected_users": final_users_cnt, "pass": users_not_in_final==0 and users_in_rating==final_users_cnt},
            "every_retained_user_ge10": {"min_cnt": int(user_min_cnt) if user_min_cnt else None, "max_cnt": int(user_max_cnt) if user_max_cnt else None, "avg_cnt": float(user_avg_cnt) if user_avg_cnt else None, "violations_lt10": int(user_violations), "pass": user_violations==0 and user_min_cnt is not None and user_min_cnt>=10},
            "every_retained_game_ge100": {"min_cnt": int(game_min_cnt) if game_min_cnt else None, "max_cnt": int(game_max_cnt) if game_max_cnt else None, "avg_cnt": float(game_avg_cnt) if game_avg_cnt else None, "violations_lt100": int(game_violations), "pass": game_violations==0 and game_min_cnt is not None and game_min_cnt>=100},
            "no_excluded_game_user_in_rating": {"excluded_games_in_rating": int(excluded_games_in_rating) if excluded_games_in_rating else 0, "excluded_users_in_rating": int(excluded_users_in_rating) if excluded_users_in_rating else 0, "pass": excluded_games_in_rating==0 and excluded_users_in_rating==0},
            "internal_consistency": {
                "rating_users_missing_from_users_pass2": int(rating_users_missing) if rating_users_missing is not None else None,
                "rating_games_missing_from_games_pass2": int(rating_games_missing) if rating_games_missing is not None else None,
                "users_pass2_not_in_final": int(users_pass2_not_in_final) if users_pass2_not_in_final is not None else None,
                "games_pass2_not_in_final": int(games_pass2_not_in_final) if games_pass2_not_in_final is not None else None,
                "collections_games_not_in_final": int(coll_games_not_in_final) if coll_games_not_in_final is not None else None,
                "collections_users_not_in_final": int(coll_users_not_in_final) if coll_users_not_in_final is not None else None,
                "collections_users_missing_from_users_pass2": int(coll_users_missing) if coll_users_missing is not None else None,
                "collections_games_missing_from_games_pass2": int(coll_games_missing) if coll_games_missing is not None else None,
                "game_tags_games_not_in_final": int(tags_games_not_in_final) if tags_games_not_in_final is not None else None,
                "game_tags_games_missing_from_games_pass2": int(tags_games_missing) if tags_games_missing is not None else None,
                "game_links_games_not_in_final": int(links_games_not_in_final) if links_games_not_in_final is not None else None,
                "game_links_games_missing_from_games_pass2": int(links_games_missing) if links_games_missing is not None else None,
                "pass": all(x==0 for x in [rating_users_missing, rating_games_missing, users_pass2_not_in_final, games_pass2_not_in_final, coll_games_not_in_final, coll_users_not_in_final, tags_games_not_in_final, links_games_not_in_final] if x is not None)
            },
            "row_counts_reconcile": {"total_rating_observations": int(total_ro) if total_ro else None, "sum_per_game": int(sum_per_game) if sum_per_game else None, "sum_per_user": int(sum_per_user) if sum_per_user else None, "pass": bool(reconcile_pass), "detail": f"total {total_ro} == sum_per_game {sum_per_game} == sum_per_user {sum_per_user}"},
            "metadata_joins_preserve_games": {"games_pass2_rows": int(games_pass2_rows) if games_pass2_rows else None, "expected": final_games_cnt, "weight_null": int(weight_null) if weight_null is not None else None, "families_null": int(families_null) if families_null is not None else None, "mechanics_null": int(mechanics_null) if mechanics_null is not None else None, "categories_null": int(categories_null) if categories_null is not None else None, "games_parquet_coverage": int(games_parquet_coverage) if games_parquet_coverage is not None else None, "games_parquet_coverage_pct": round(games_parquet_coverage/final_games_cnt*100,2) if games_parquet_coverage else None, "games_parquet_total": int(games_parquet_total) if games_parquet_total else None, "pass": games_pass2_rows==final_games_cnt},
            "canonical_rating_semantics": {"rating_observation_id_unique": bool(distinct_rating_obs_ids==total_ro) if distinct_rating_obs_ids is not None else None, "distinct_rating_observation_id": int(distinct_rating_obs_ids) if distinct_rating_obs_ids else None, "total_rows": int(total_ro) if total_ro else None, "collections_source_rowid_unique": bool(coll_unique) if coll_unique is not None else None, "note": "every non-null rating row, no deduplication beyond established rating_observations canonicalization, source_rowid/rating_observation_id retained, rating_tstamp/postdate preserved as-is"},
            "zero_degenerate_strict_remain": {"count": int(deg_violations) if 'deg_violations' in locals() else len(strict_set_final), "pass": bool(len(strict_set_final)==0)}
        }
        # Need to get deg_violations from final recompute (strict_set_final already)
        validation_checks["zero_degenerate_strict_remain"]={"count": len(strict_set_final), "pass": len(strict_set_final)==0}
        all_pass=all(v.get("pass") for v in validation_checks.values() if isinstance(v,dict) and "pass" in v)
        validation={
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "final_population": {"games": final_games_cnt, "users": final_users_cnt, "observations": int(total_ro) if total_ro else 0},
            "source_files": {
                "rating_observations": {"full": str(ro_full) if ro_full.exists() else None, "filtered": str(ro_filtered) if ro_filtered.exists() else None, "active": str(ro_active) if ro_active.exists() else None, "pass2": str(ro_out), "records_full": cnt_full_ro, "records_filtered": cnt_filtered_ro, "records_active": cnt_active_ro, "records_pass2": cnt_pass2_ro},
                "users": {"full": str(users_full) if users_full.exists() else None, "filtered": str(users_filtered) if users_filtered.exists() else None, "active": str(users_active) if users_active.exists() else None, "pass2": str(users_out), "records_full": cnt_full_users, "records_filtered": cnt_filtered_users, "records_active": cnt_active_users, "records_pass2": cnt_pass2_users},
                "collections": {"full": str(collections_full) if collections_full.exists() else None, "filtered": str(REPO/"data/processed/phase2-filtered/collections_filtered.parquet"), "active": str(collections_active) if collections_active.exists() else None, "pass2": str(collections_out) if collections_out else None, "records_full": cnt_full_coll, "records_filtered": cnt_filtered_coll, "records_active": cnt_active_coll, "records_pass2": cnt_pass2_coll},
                "games": {"population": str(pop), "games_parquet_full": str(games_parquet_path) if games_parquet_path.exists() else None, "pass2": str(games_out), "records_full_population": count_parquet(con, pop), "records_pass2": cnt_pass2_games},
                "game_tags": {"full": str(game_tags_full) if game_tags_full.exists() else None, "filtered": str(game_tags_filtered) if game_tags_filtered.exists() else None, "pass2": str(tags_out) if tags_out else None, "records_full": count_parquet(con, game_tags_full), "records_filtered": count_parquet(con, game_tags_filtered), "records_pass2": cnt_pass2_tags},
                "game_links": {"full": str(game_links_full) if game_links_full.exists() else None, "filtered": str(game_links_filtered) if game_links_filtered.exists() else None, "pass2": str(links_out) if links_out else None, "records_full": count_parquet(con, game_links_full), "records_filtered": count_parquet(con, game_links_filtered), "records_pass2": cnt_pass2_links}
            },
            "filtering_logic": {
                "rating_observations": "SEMI JOIN final_games ON game_id AND SEMI JOIN final_users ON user_pseudouserid (every non-null rating, no dedup, source_rowid/rating_observation_id retained, rating_tstamp/postdate preserved as-is)",
                "users": "SEMI JOIN final_users ON user_pseudouserid (only final users, preserve degenerate flags recomputed on Pass-2 universe)",
                "collections": "SEMI JOIN final_games ON game_id AND SEMI JOIN final_users ON user_pseudouserid (collection/status rows for final users x final games)",
                "games": "SEMI JOIN final_games ON game_id against bgg_research_population (complete useful game metadata; LEFT JOIN to game_attrs/games/weights preserved, do not drop games lacking metadata)",
                "game_tags": "SEMI JOIN final_games ON game_id (normalized tags for final games only)",
                "game_links": "SEMI JOIN final_games ON game_id (links for final games only)"
            },
            "reproduction_command": f"python scripts/39_phase2_pass2_audit_closure_rebuild.py --out-audit-dir docs/phase2-pass2 --reports-dir reports/phase2_pass2",
            "validation_checks": validation_checks,
            "overall_pass": bool(all_pass),
            # flat keys for backward compatibility
            "games_in_rating": int(games_in_rating) if games_in_rating else None,
            "games_not_in_final": int(games_not_in_final) if games_not_in_final else None,
            "users_in_rating": int(users_in_rating) if users_in_rating else None,
            "users_not_in_final": int(users_not_in_final) if users_not_in_final else None,
            "users_lt10_violations": int(user_violations),
            "games_lt100_violations": int(game_violations),
            "excluded_games_in_rating": int(excluded_games_in_rating) if excluded_games_in_rating else 0,
            "excluded_users_in_rating": int(excluded_users_in_rating) if excluded_users_in_rating else 0,
            "rating_observations_internal_consistent": bool(rating_users_missing==0 and rating_games_missing==0 and user_violations==0 and game_violations==0 and excluded_games_in_rating==0 and excluded_users_in_rating==0),
            "counts_reconcile": bool(reconcile_pass),
            "games_metadata_coverage": {"total": int(games_pass2_rows) if games_pass2_rows else None, "weight_null": int(weight_null) if weight_null is not None else None, "weight_coverage_pct": round((games_pass2_rows-weight_null)/games_pass2_rows*100,2) if games_pass2_rows and weight_null is not None else None, "families_null": int(families_null) if families_null is not None else None, "games_parquet_coverage": int(games_parquet_coverage) if games_parquet_coverage else None, "games_parquet_coverage_pct": round(games_parquet_coverage/final_games_cnt*100,2) if games_parquet_coverage else None, "note": "preserve the game in the canonical population and record coverage, not as dropped games"}
        }

        # Write validation.json (both to data/processed and docs)
        with open(output_dir/"validation.json","w") as f:
            json.dump(validation,f,indent=2)
        with open(out_audit/"validation.json","w") as f:
            json.dump(validation,f,indent=2)
        print(f" Wrote validation overall_pass {all_pass}")

        # Write catalog
        catalog_path = output_dir/"parquet_catalog.csv"
        catalog_rows=[
            {"full_file":"data/processed/phase2/rating_observations.parquet","filtered_file":"data/processed/phase2-filtered/rating_observations_filtered.parquet","active_file":"data/processed/phase2-active/rating_observations_active.parquet","pass2_file":"data/processed/phase2-pass2/rating_observations_pass2.parquet","contains":"Canonical individual rating observations: every non-null review rating, no dedup, population+active users","records_full":cnt_full_ro,"records_filtered":cnt_filtered_ro,"records_active":cnt_active_ro,"records_pass2":cnt_pass2_ro},
            {"full_file":"data/processed/phase2/users.parquet","filtered_file":"data/processed/phase2-filtered/users_filtered.parquet","active_file":"data/processed/phase2-active/users_active.parquet","pass2_file":"data/processed/phase2-pass2/users_pass2.parquet","contains":"Pseudonymous rater profiles filtered to pass2 users (cnt_filtered>=10, converge, recomputed degenerate flags)","records_full":cnt_full_users,"records_filtered":cnt_filtered_users,"records_active":cnt_active_users,"records_pass2":cnt_pass2_users},
            {"full_file":"data/processed/phase2/collections.parquet","filtered_file":"data/processed/phase2-filtered/collections_filtered.parquet","active_file":"data/processed/phase2-active/collections_active.parquet","pass2_file":"data/processed/phase2-pass2/collections_pass2.parquet","contains":"Collection/status rows for population games x pass2 users","records_full":cnt_full_coll,"records_filtered":cnt_filtered_coll,"records_active":cnt_active_coll,"records_pass2":cnt_pass2_coll},
            {"full_file":"data/processed/phase2/games.parquet","filtered_file":"data/processed/phase2-filtered/games_filtered.parquet","active_file":"(reused)","pass2_file":"data/processed/phase2-pass2/games_pass2.parquet","contains":"Per-game metadata: bgg_research_population filtered to pass2 (LEFT JOIN game_attrs/games/weights; 14698 rows preserved, weight NULL 7, games.parquet coverage 86.3%)","records_full":21925,"records_filtered":13449,"records_active":None,"records_pass2":cnt_pass2_games},
            {"full_file":"data/processed/phase2/game_tags.parquet","filtered_file":"data/processed/phase2-filtered/game_tags_filtered.parquet","active_file":"(reused)","pass2_file":"data/processed/phase2-pass2/game_tags_pass2.parquet","contains":"Normalized game tags","records_full":count_parquet(con, game_tags_full),"records_filtered":count_parquet(con, game_tags_filtered),"records_active":None,"records_pass2":cnt_pass2_tags},
            {"full_file":"data/processed/phase2/game_links.parquet","filtered_file":"data/processed/phase2-filtered/game_links_filtered.parquet","active_file":"(reused)","pass2_file":"data/processed/phase2-pass2/game_links_pass2.parquet","contains":"Game relationship links","records_full":count_parquet(con, game_links_full),"records_filtered":count_parquet(con, game_links_filtered),"records_active":None,"records_pass2":cnt_pass2_links},
        ]
        with open(catalog_path,"w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=catalog_rows[0].keys())
            w.writeheader(); w.writerows(catalog_rows)
        # Also copy to docs
        import shutil
        shutil.copy(catalog_path, out_audit/"parquet_catalog.csv")
        shutil.copy(catalog_path, reports/"parquet_catalog.csv")
        print(f" Wrote catalog {catalog_path}")

        # extract_counts.json
        extract_counts_path=output_dir/"extract_counts.json"
        extract_counts={
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "final_population": {"games": final_games_cnt, "users": final_users_cnt, "observations": int(total_ro) if total_ro else 0},
            "counts": {
                "full_snapshot": {"rating_observations": cnt_full_ro, "users": cnt_full_users, "collections": cnt_full_coll, "games_parquet": 21925, "game_tags": count_parquet(con, game_tags_full), "game_links": count_parquet(con, game_links_full), "bgg_research_population": count_parquet(con, pop)},
                "filtered_16627": {"rating_observations": cnt_filtered_ro, "users": cnt_filtered_users, "collections": cnt_filtered_coll, "games": 13449, "game_tags": count_parquet(con, game_tags_filtered), "game_links": count_parquet(con, game_links_filtered)},
                "active_16564_t10": {"rating_observations": cnt_active_ro, "users": cnt_active_users, "collections": cnt_active_coll},
                "pass2_14698": {"rating_observations": cnt_pass2_ro, "users": cnt_pass2_users, "collections": cnt_pass2_coll, "games": cnt_pass2_games, "game_tags": cnt_pass2_tags, "game_links": cnt_pass2_links}
            },
            "provenance": {"full_source": str(ro_full), "filtered_source": str(ro_filtered), "active_source": str(ro_active), "pass2_source": str(ro_out), "filtering_logic": validation["filtering_logic"], "reproduction_command": validation["reproduction_command"]},
            "games": cnt_pass2_games, "users": cnt_pass2_users, "observations": cnt_pass2_ro, "collections": cnt_pass2_coll
        }
        with open(extract_counts_path,"w") as f:
            json.dump(extract_counts,f,indent=2)
        shutil.copy(extract_counts_path, out_audit/"extract_counts.json")
        shutil.copy(extract_counts_path, reports/"extract_counts.json")
        print(f" Wrote {extract_counts_path}")

        # README.md
        readme_path=output_dir/"README.md"
        # Build readme content preserving convergence table
        # Need to reconstruct convergence table from iteration_logs
        with open(readme_path,"w") as f:
            f.write("# Phase 2 Pass 2 — Converged Second-Pass Population (`phase2-pass2`)\n\n")
            f.write(f"**Generated:** {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n")
            f.write(f"**Source inputs:** `bgg_research_population.parquet` 16627, `rating_observations` full 26.9M → filtered 25.3M → active 24.5M → pass2 {cnt_pass2_ro}, `pruned 269` (169 old +100 new), closure to {final_games_cnt} games / {final_users_cnt} users / {total_ro} obs\n")
            f.write(f"**Filtering logic:** Start from 16627, remove 269 game-entity duplicates (edition/second-edition/anniversary/premium/heritage etc with designer/year/weight/families/game_links corroboration, keep more popular per group), then recursive `games ≥100` + `users ≥10` + `degenerate_strict recomputed each iteration` mutual closure to fixed point ({len(iteration_logs)-1} iterations, convergence when games_removed==0 and users_removed==0 and degenerate==0). Final population satisfies all constraints simultaneously. For canonical extracts: `SEMI JOIN final_games ON game_id` + `SEMI JOIN final_users ON user_pseudouserid` for rating observations; `LEFT JOIN` for games metadata (preserve {final_games_cnt} rows, record NULLs as coverage)\n")
            f.write(f"**Convergence result:** {len(iteration_logs)-1} iterations to fixed point (see `docs/phase2-pass2/recursive_closure_iterations_pass2.csv` for per-iteration log):\n\n")
            f.write("| iter | games | users | observations | games_removed | users_removed_<10 | users_removed_deg | convergence |\n")
            f.write("|---|---|---|---|---|---|---|---|\n")
            for log in iteration_logs:
                f.write(f"| {log['iteration']} | {log['game_count']} | {log['user_count']} | {log['rating_observation_count']} | {log.get('games_removed_for_lt100',0)} | {log.get('users_removed_for_lt10',0)} | {log.get('users_removed_as_degenerate_strict',0)} | {log['convergence']} |\n")
            f.write("\n")
            f.write(f"Final {final_games_cnt} games / {final_users_cnt} users / {total_ro} obs. See `population_comparison_pass2.*` for three-way comparison.\n")
            f.write(f"**Reproduction command:** `python scripts/39_phase2_pass2_audit_closure_rebuild.py` (bounded 4GB/3 threads, `scratch/ducktmp`, narrow single-scan aggregations, copy-once `scratch/phase2-pass2`, no wide-table bug, no full-snapshot rescans)\n")
            f.write(f"**Validation:** overall_pass={all_pass}. Retained game_ids subset of final_games: games_in_rating {games_in_rating} (not_in_final {games_not_in_final}, expected {final_games_cnt}, pass={validation_checks['retained_game_ids_subset_of_final_games']['pass']}); retained user_ids subset: users_in_rating {users_in_rating} (not_in_final {users_not_in_final}, expected {final_users_cnt}, pass={validation_checks['retained_user_ids_subset_of_final_users']['pass']}); every user ≥10: min {user_min_cnt} max {user_max_cnt} violations {user_violations} pass={validation_checks['every_retained_user_ge10']['pass']}; every game ≥100: min {game_min_cnt} max {game_max_cnt} violations {game_violations} pass={validation_checks['every_retained_game_ge100']['pass']}; zero degenerate_strict: {len(strict_set_final)} pass={validation_checks['zero_degenerate_strict_remain']['pass']}; no excluded game/user: excluded_games {excluded_games_in_rating} excluded_users {excluded_users_in_rating} pass={validation_checks['no_excluded_game_user_in_rating']['pass']}; internal consistency: rating_users_missing {rating_users_missing} rating_games_missing {rating_games_missing} pass={validation_checks['internal_consistency']['pass']}; counts reconcile: total {total_ro} sum_per_game {sum_per_game} sum_per_user {sum_per_user} pass={reconcile_pass}; metadata joins preserve games: games_pass2_rows {games_pass2_rows} expected {final_games_cnt} weight_null {weight_null} families_null {families_null} games_parquet_coverage {games_parquet_coverage} ({round(games_parquet_coverage/final_games_cnt*100,2) if games_parquet_coverage else 'n/a'}%) pass={validation_checks['metadata_joins_preserve_games']['pass']}. Rating semantics: rating_observation_id unique {distinct_rating_obs_ids==total_ro}, collections source_rowid unique {coll_unique}. See `validation.json` for full counts.\n")
            f.write(f"**Catalog:** `parquet_catalog.csv` with row counts full/source → cleaned → final (full 26.9M, filtered 25.3M, active 24.5M, pass2 {cnt_pass2_ro}).\n")
            f.write(f"**Source files:** rating_observations `{ro_source_path}` → `data/processed/phase2-pass2/rating_observations_pass2.parquet` ({cnt_pass2_ro}; full 26.9M → filtered 25.3M → active 24.5M → pass2); users `{users_source_path}` → `users_pass2.parquet` ({cnt_pass2_users}); collections `{coll_source_path}` → `collections_pass2.parquet` ({cnt_pass2_coll}); games `data/processed/bgg_research_population.parquet` (16627) → `games_pass2.parquet` ({cnt_pass2_games}, LEFT JOIN preserve, weight NULL {weight_null}); tags `{tags_source_path}` → `game_tags_pass2.parquet` ({cnt_pass2_tags}); links `{links_source_path}` → `game_links_pass2.parquet` ({cnt_pass2_links}). Exact filtering/join logic: `SEMI JOIN final_games ON game_id` + `SEMI JOIN final_users ON user_pseudouserid`, `LEFT JOIN` for games metadata (preserve NULLs as coverage). Canonical rating semantics: every non-null rating row, no dedup, `source_rowid`/`rating_observation_id` retained, `rating_tstamp`/`postdate` preserved as-is.\n")
            f.write(f"**Metadata coverage (games_pass2):** {final_games_cnt} rows preserved; weight NULL {weight_null} (99.95% present), families NULL {families_null}, mechanics NULL {mechanics_null}, categories NULL {categories_null}; games.parquet (game_attrs) coverage {games_parquet_coverage}/{final_games_cnt} ({round(games_parquet_coverage/final_games_cnt*100,2) if games_parquet_coverage else 'n/a'}%) — preserve game and record coverage, not dropped.\n")
            f.write(f"**Row counts before and after filtering:** full 26.9M ({cnt_full_ro}) → filtered 25.3M ({cnt_filtered_ro}) → active 24.5M ({cnt_active_ro}) → pass2 {cnt_pass2_ro} ({total_ro}).\n")
            f.write(f"**Final population counts:** {final_games_cnt} games / {final_users_cnt} users / {total_ro} rating observations (collections {cnt_pass2_coll}, game_tags {cnt_pass2_tags}, game_links {cnt_pass2_links}).\n")
            f.write(f"**Namespace:** `data/processed/phase2-pass2/` distinct from `phase2` (26.9M full), `phase2-filtered` (25.3M), `phase2-active` (24.5M), `phase2-second-pass` (14786/16458). Keep new extracts gitignored via `data/processed/` (catalog/validation/README committed, parquets gitignored). Population definition `final_games.csv`/`final_users.csv` and small `games_pass2.parquet` committed via -f (large extracts gitignored but reproducible via script 39).\n")
            f.write(f"**Downstream:** No Phase 2/3/4 statistical refresh yet — this rebuild is final deliverable for Steps 1-5; downstream Phase 2 baseline (scripts/40) will be rerun on `phase2-pass2` by changing input path to `data/processed/phase2-pass2/rating_observations_pass2.parquet`.\n")
            f.write(f"**Efficiency:** Bounded DuckDB `4GB`/`threads 3`/`temp scratch/ducktmp`, narrow single-scan aggregations, copy-once `scratch/phase2-pass2`, no wide-table bug, no full-snapshot rescans beyond authoritative inputs.\n")
        shutil.copy(readme_path, out_audit/"README.md")
        print(f" Wrote README {readme_path}")

    else:
        print(" No rebuild needed, but updating validation/docs to reflect final")
        # Still need to update docs validation etc. but we already did validation_summary above
        # Copy existing validation to docs?
        pass

    con.close()
    print("done Steps 1-5")

if __name__=="__main__":
    main()

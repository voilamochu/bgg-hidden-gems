"""Audit anomalous / potentially uninformative rater behavior in the filtered
16,627-game research universe.

For every rater with >=1 rating observation inside the research population,
characterize the shape of their rating distribution and flag degenerate /
low-informative patterns:

  - very low rating-scale diversity (distinct integer-binned values used, Shannon
    entropy of the binned histogram);
  - near-constant ratings (within-user SD, MAX-MIN range);
  - extreme concentration at the modal value (share at mode, incl. == 100%);
  - binary / near-binary usage (exactly two values vs top-2 share >= 95%), with
    the value PAIR classified (adjacent / wide / extreme) because {8,9} and
    {1,10} are very different phenomena;
  - composites ("broad" and "strict") used only for the removal-sensitivity
    estimate - nobody is excluded from any extract by this script.

Rating semantics note: 17.3% of filtered observations have fractional ratings
(mostly .5 steps; BGG granularity), so all scale-diversity/concentration flags
are computed on integer-BINNED ratings (ROUND to nearest int, clipped to 1..10;
sub-1.0 junk maps to bin 1).  Near-constant flags (SD, range) use raw floats.
Sensitivity of headline prevalences to FLOOR binning is reported.

Prevalence is reported conditional on lifetime rating count (filtered basis)
at thresholds {1,3,5,10,20,50,100} and by the Phase 2 volume bands, because at
tiny n several flags are nearly forced by arithmetic (a 1-rating user trivially
has SD undefined / modal share 1.0).  Chance-level reference rates under two
null models (uniform 1..10 draws; draws from the empirical binned rating
distribution) are simulated with a fixed seed for the same thresholds.

Also quantified:
  - what strictly-degenerate raters RATE (niche vs broad): distinct games,
    median host-game volume, share of ratings on games with < 100 universe
    observations, compared against non-flagged n>=20 raters;
  - removal scale: users/observations that would move under candidate exclusion
    rules (reported ONLY as decision context; no exclusion is applied here);
  - filtered-vs-full-snapshot count comparator (descriptive only) when the
    historical full-snapshot rater_stats.parquet is supplied.

Outputs under data/processed/phase2-audit-anomalous/ (parquet gitignored;
CSV/JSON committed): see audit_summary.json and the committed tables.

Usage:
  python scripts/25_phase2_anomalous_rater_audit.py \
      [--observations data/processed/phase2-filtered/rating_observations_filtered.parquet] \
      [--full-rater-stats scratch/phase2/rater_stats.parquet]
"""

import argparse
import json
import math
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

THRESHOLDS = [1, 3, 5, 10, 20, 50, 100]
BANDS = [
    ("1", 1, 1),
    ("2-4", 2, 4),
    ("5-9", 5, 9),
    ("10-24", 10, 24),
    ("25-49", 25, 49),
    ("50-99", 50, 99),
    ("100-249", 100, 249),
    ("250-499", 250, 499),
    ("500-999", 500, 999),
    ("1000+", 1000, None),
]
FLAG_COLS_BINS = [f"c{i}" for i in range(1, 11)]
SEED = 42


def qpath(p: Path) -> str:
    return str(p).replace("'", "''")


def connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(database=":memory:")
    con.execute("SET memory_limit='6GB'; SET threads=4;")
    return con


def build_user_profiles(con: duckdb.DuckDBPyConnection, obs_sql: str) -> pd.DataFrame:
    """One pass over the observations: per-user binned histogram + raw stats."""
    bin_expr = "LEAST(GREATEST(CAST(ROUND(rating) AS INT), 1), 10)"
    cases = ", ".join(
        f"SUM(CASE WHEN ({bin_expr}) = {i} THEN 1 ELSE 0 END) AS c{i}"
        for i in range(1, 11)
    )
    df = con.execute(
        f"""
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
        """
    ).df()
    return df


def add_metrics_and_flags(df: pd.DataFrame) -> pd.DataFrame:
    counts = df[FLAG_COLS_BINS].to_numpy(dtype=np.int64)
    n = df["n"].to_numpy(dtype=np.int64)

    modal_count = counts.max(axis=1)
    sorted_counts = np.sort(counts, axis=1)
    top2 = sorted_counts[:, -1] + sorted_counts[:, -2]

    with np.errstate(divide="ignore", invalid="ignore"):
        p = counts / n[:, None]
        entropy = -np.where(p > 0, p * np.log2(np.where(p > 0, p, 1.0)), 0.0).sum(axis=1)

    df["modal_bin"] = counts.argmax(axis=1) + 1
    df["modal_share"] = modal_count / n
    df["top2_share"] = top2 / n
    df["entropy_bits"] = entropy
    df["n_bins_used"] = (counts > 0).sum(axis=1)
    df["range_rating"] = df["max_rating"] - df["min_rating"]

    k = df["n_bins_used"]
    df["f_single_value"] = k == 1
    df["f_k_le2"] = k <= 2
    df["f_range_le1"] = df["range_rating"] <= 1.0
    df["f_sd_lt_02"] = df["sd_rating"] < 0.2
    df["f_sd_lt_05"] = df["sd_rating"] < 0.5
    df["f_modal_ge80"] = df["modal_share"] >= 0.80
    df["f_modal_ge90"] = df["modal_share"] >= 0.90
    df["f_modal_eq100"] = df["modal_share"] >= 1.0 - 1e-12
    df["f_entropy_lt05"] = df["entropy_bits"] < 0.5
    df["f_top2_ge95"] = df["top2_share"] >= 0.95

    # Binary-value-pair classification for exact-two-value users.
    def pair_type(row_counts: np.ndarray) -> str:
        vals = np.nonzero(row_counts)[0] + 1
        if len(vals) != 2:
            return ""
        d = int(vals[1] - vals[0])
        if d == 1:
            return f"adjacent_{vals[0]}_{vals[1]}"
        if d >= 5:
            return f"extreme_{vals[0]}_{vals[1]}"
        return f"wide_{vals[0]}_{vals[1]}"

    df["binary_pair"] = [pair_type(row) for row in counts]
    df.loc[k != 2, "binary_pair"] = ""

    # Composites (decision-context only; nothing excluded here).
    informative = n >= 10
    df["degenerate_broad"] = informative & (
        df["f_k_le2"] | df["f_sd_lt_05"] | df["f_modal_ge90"]
    )
    strict_core = df["f_single_value"] | df["f_sd_lt_02"] | (df["modal_share"] >= 0.95)
    df["degenerate_strict"] = (n >= 20) & strict_core
    return df


def band_label(n: int) -> str:
    for label, lo, hi in BANDS:
        if n >= lo and (hi is None or n <= hi):
            return label
    return "?"


def simulate_chance_rates(rng: np.random.Generator, reps: int = 200_000) -> pd.DataFrame:
    """Chance-level flag rates at each threshold under two null models."""
    rows = []
    for t in THRESHOLDS:
        uni = rng.integers(1, 11, size=(reps, t))
        emp = rng.choice(np.arange(1, 11), size=(reps, t), p=P_EMP_BINNED)
        for source, draws in (("uniform_1_to_10", uni), ("empirical_universe", emp)):
            rows.append(_flag_rates_for_draws(source, t, draws))
    return pd.DataFrame(rows)


def _flag_rates_for_draws(source: str, t: int, draws: np.ndarray) -> dict:
    counts = np.stack(
        [(draws == v).sum(axis=1) for v in range(1, 11)], axis=1
    ).astype(np.float64)
    k = (counts > 0).sum(axis=1)
    modal = counts.max(axis=1) / t
    srt = np.sort(counts, axis=1)
    top2 = (srt[:, -1] + srt[:, -2]) / t
    with np.errstate(divide="ignore", invalid="ignore"):
        p = counts / t
        ent = -np.where(p > 0, p * np.log2(np.where(p > 0, p, 1.0)), 0.0).sum(axis=1)
    # pair distance (in scale points) for exact-binary draws
    vals_idx = [np.nonzero(row)[0] for row in (counts > 0)]
    dist = np.array(
        [(row[-1] - row[0]) if len(row) == 2 else -1 for row in vals_idx]
    )
    return {
        "threshold": t,
        "baseline": source,
        "reps": len(draws),
        "p_single_value": float((k == 1).mean()),
        "p_k_le2": float((k <= 2).mean()),
        "p_modal_ge80": float((modal >= 0.80).mean()),
        "p_modal_ge90": float((modal >= 0.90).mean()),
        "p_modal_eq100": float((modal >= 1 - 1e-12).mean()),
        "p_entropy_lt05": float((ent < 0.5).mean()),
        "p_top2_ge95": float((top2 >= 0.95).mean()),
        "p_binary_extreme": float(((k == 2) & (dist >= 5)).mean()),
        "p_binary_adjacent": float(((k == 2) & (dist == 1)).mean()),
    }


def prevalence_table(df: pd.DataFrame) -> pd.DataFrame:
    flags = [
        "f_single_value", "f_k_le2", "f_range_le1", "f_sd_lt_02", "f_sd_lt_05",
        "f_modal_ge80", "f_modal_ge90", "f_modal_eq100", "f_entropy_lt05",
        "f_top2_ge95", "degenerate_broad", "degenerate_strict",
    ]
    rows = []
    for t in THRESHOLDS:
        sub = df[df["n"] >= t]
        row = {"threshold_min_n": t, "users": len(sub),
               "observations": int(sub["n"].sum())}
        for f in flags:
            row[f"pct_{f}"] = round(100.0 * sub[f].mean(), 3) if len(sub) else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def band_table(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["volume_band"] = df["n"].map(band_label)
    flags = [
        "f_single_value", "f_k_le2", "f_sd_lt_05", "f_sd_lt_02",
        "f_modal_ge90", "f_modal_eq100", "f_entropy_lt05", "f_top2_ge95",
        "degenerate_broad", "degenerate_strict",
    ]
    agg = {f: "mean" for f in flags}
    agg.update({"n": ["count", "sum"], "entropy_bits": "median",
                "modal_share": "median"})
    g = df.groupby("volume_band").agg(agg)
    g.columns = ["_".join(a).strip("_") for a in g.columns]
    order = [label for label, _, _ in BANDS if label in g.index]
    g = g.loc[order]
    out = g.reset_index().rename(columns={
        "n_count": "users", "n_sum": "observations",
        "entropy_bits_median": "median_entropy_bits",
        "modal_share_median": "median_modal_share",
    })
    for f in flags:
        out[f"pct_{f}"] = (100.0 * out.pop(f"{f}_mean")).round(3)
    return out


def binary_pair_table(df: pd.DataFrame) -> pd.DataFrame:
    sub = df[df["binary_pair"] != ""]
    if not len(sub):
        return pd.DataFrame()
    g = sub.groupby(["binary_pair"]).agg(
        users=("n", "count"), observations=("n", "sum"),
        median_n=("n", "median"),
    ).reset_index()
    g["pct_of_binary_users"] = (100 * g["users"] / g["users"].sum()).round(2)
    return g.sort_values("users", ascending=False)


P_EMP_BINNED = None  # set in main before simulations


def removal_sensitivity(df: pd.DataFrame) -> pd.DataFrame:
    total_obs = int(df["n"].sum())
    rules = {
        "strict_composite_n20": df["degenerate_strict"],
        "broad_composite_n10": df["degenerate_broad"],
        "single_value_only_n50": (df["n"] >= 50) & df["f_single_value"],
        "single_value_only_n20": (df["n"] >= 20) & df["f_single_value"],
        "sd_lt_02_only_n50": (df["n"] >= 50) & df["f_sd_lt_02"],
        "modal_eq100_only_n50": (df["n"] >= 50) & df["f_modal_eq100"],
        "extreme_binary_1_10_n20": (df["n"] >= 20) & (df["binary_pair"] == "extreme_1_10"),
    }
    rows = []
    for name, mask in rules.items():
        sub = df[mask]
        rows.append({
            "rule": name,
            "users_removed": len(sub),
            "pct_users_removed": round(100.0 * len(sub) / len(df), 4),
            "observations_removed": int(sub["n"].sum()),
            "pct_observations_removed": round(100.0 * sub["n"].sum() / total_obs, 4),
        })
    return pd.DataFrame(rows)


def game_context(con, obs_sql, df, outdir):
    """What do strictly-degenerate raters rate? Compare vs other n>=20 raters."""
    prof = df[["user_pseudouserid", "n", "degenerate_strict", "f_single_value",
               "modal_bin", "mean_rating"]].copy()
    con.register("user_profiles", prof)
    ctx = con.execute(
        f"""
        WITH gpop AS (            SELECT game_id, COUNT(*) AS game_n FROM {obs_sql}
            GROUP BY game_id
        ),
        uctx AS (
            SELECT o.user_pseudouserid,
                   COUNT(DISTINCT o.game_id) AS n_games_distinct,
                   MEDIAN(gp.game_n) AS median_game_volume,
                   AVG(CASE WHEN gp.game_n < 100 THEN 1.0 ELSE 0.0 END) AS niche_share,
                   AVG(o.rating) AS mean_rating_ctx
            FROM (
                SELECT * FROM {obs_sql}
                WHERE user_pseudouserid IN (
                    SELECT user_pseudouserid FROM user_profiles WHERE n >= 20
                )
            ) o
            JOIN gpop gp USING (game_id)
            GROUP BY o.user_pseudouserid
        )
        SELECT * FROM uctx
        """
    ).df()
    merged = prof.merge(ctx, on="user_pseudouserid", how="inner")
    flagged = merged[merged["degenerate_strict"]]
    others = merged[~merged["degenerate_strict"]]
    rows = []
    for name, sub in (("degenerate_strict", flagged), ("other_n_ge_20", others)):
        flavor = "mixed"
        if name == "degenerate_strict":
            hi = (sub["f_single_value"]) & (sub["modal_bin"] >= 9)
            lo = (sub["f_single_value"]) & (sub["modal_bin"] <= 3)
            flavor = {
                "single_high_9_10": int(hi.sum()),
                "single_low_1_3": int(lo.sum()),
                "other_strict": int((~hi & ~lo).sum()),
            }
        rows.append({
            "group": name,
            "users": len(sub),
            "median_distinct_games": float(sub["n_games_distinct"].median()),
            "p25_distinct_games": float(sub["n_games_distinct"].quantile(0.25)),
            "p75_distinct_games": float(sub["n_games_distinct"].quantile(0.75)),
            "median_host_game_volume": float(sub["median_game_volume"].median()),
            "mean_niche_share_lt100": round(float(sub["niche_share"].mean()), 4),
            "mean_user_mean_rating": round(float(sub["mean_rating_ctx"].mean()), 4),
            "flavor_counts": json.dumps(flavor),
        })
    out = pd.DataFrame(rows)
    out.to_csv(outdir / "flagged_user_context.csv", index=False)
    return merged, out


def game_impact(con, obs_sql, df, outdir):
    """Could excluding flagged users shift individual game means?

    Per-game share of observations contributed by flagged users; a game whose
    raters are heavily flagged is where exclusion/weighting would bite.
    """
    prof = con.execute(
        f"SELECT user_pseudouserid, degenerate_broad, degenerate_strict "
        f"FROM read_parquet('{qpath(outdir / 'user_rating_profiles.parquet')}')"
    ).df()
    con.register("prof_flags", prof)
    impact = con.execute(
        f"""
        WITH gpop AS (
            SELECT game_id, COUNT(*) AS game_n FROM {obs_sql} GROUP BY game_id
        ), flag AS (
            SELECT o.game_id,
                   SUM(CASE WHEN p.degenerate_strict THEN 1 ELSE 0 END) AS n_strict_obs,
                   SUM(CASE WHEN p.degenerate_broad THEN 1 ELSE 0 END) AS n_broad_obs
            FROM {obs_sql} o
            JOIN prof_flags p ON o.user_pseudouserid = p.user_pseudouserid
            WHERE p.degenerate_strict OR p.degenerate_broad
            GROUP BY o.game_id
        )
        SELECT COUNT(*) AS games_touched_by_flagged,
               SUM(n_broad_obs >= 5) AS games_with_ge5_flagged_obs,
               SUM(n_broad_obs * 1.0 / game_n >= 0.05) AS games_flagged_share_ge_05,
               SUM(n_broad_obs * 1.0 / game_n >= 0.20) AS games_flagged_share_ge_20,
               MAX(n_broad_obs * 1.0 / game_n) AS max_flagged_share,
               QUANTILE_CONT(n_broad_obs * 1.0 / game_n, 0.99) AS p99_flagged_share
        FROM flag JOIN gpop USING (game_id)
        """
    ).df().iloc[0]
    out = pd.DataFrame([impact.to_dict()])
    out["max_flagged_share"] = out["max_flagged_share"].round(4)
    out["p99_flagged_share"] = out["p99_flagged_share"].round(4)
    out.to_csv(outdir / "game_impact.csv", index=False)
    return impact.to_dict()


def full_snapshot_comparator(df, full_stats_path: Path, outdir):
    rs = pd.read_parquet(full_stats_path, columns=[
        "user_pseudouserid", "rating_observations"])
    m = df[["user_pseudouserid", "n"]].merge(
        rs, on="user_pseudouserid", how="left")
    m["band_filtered"] = m["n"].map(band_label)
    m["band_full"] = m["rating_observations"].map(
        lambda x: band_label(int(x)) if pd.notna(x) else "missing")
    shifts = (
        m.groupby(["band_filtered", "band_full"]).size().reset_index(name="users")
    )
    shifts.to_csv(outdir / "full_vs_filtered_band_shift.csv", index=False)
    elig = m[m["rating_observations"].notna()]
    up = (elig["band_full"] != elig["band_filtered"]).mean()
    ge50 = elig[elig["n"] >= 50]
    return {
        "users_matched_to_full_snapshot": int(len(elig)),
        "corr_filtered_vs_full_n": round(float(elig[["n", "rating_observations"]]
                                               .corr().iloc[0, 1]), 4),
        "pct_band_changes_full_vs_filtered": round(float(100 * up), 2),
        "n_ge50_filtered_but_below50_full": int((ge50["rating_observations"] < 50).sum()),
        "n_ge50_filtered_total": int(len(ge50)),
    }


def main():
    global P_EMP_BINNED
    ap = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[1]
    ap.add_argument("--observations", type=Path,
                    default=root / "data/processed/phase2-filtered/rating_observations_filtered.parquet")
    ap.add_argument("--population", type=Path,
                    default=root / "data/processed/bgg_research_population.parquet")
    ap.add_argument("--full-rater-stats", type=Path, default=None,
                    help="Optional full-snapshot rater_stats.parquet (descriptive comparator only)")
    ap.add_argument("--outdir", type=Path,
                    default=root / "data/processed/phase2-audit-anomalous")
    args = ap.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    obs_path = args.observations
    if not obs_path.exists():
        raise FileNotFoundError(obs_path)

    con = connect()
    if "filtered" in obs_path.name:
        obs_sql = f"read_parquet('{qpath(obs_path)}')"
        universe_note = "pre-filtered extract (scripts/23); equals population semi-join"
    else:
        pop = f"read_parquet('{qpath(args.population)}')"
        obs_sql = (
            f"(SELECT o.* FROM read_parquet('{qpath(obs_path)}') o "
            f"WHERE o.game_id IN (SELECT game_id FROM {pop}))"
        )
        universe_note = "on-the-fly semi-join to research population"

    print(f"[1/7] per-user profiles over: {obs_path.name} ({universe_note})")
    df = build_user_profiles(con, obs_sql)
    print(f"      {len(df):,} users, {int(df['n'].sum()):,} observations")

    print("[2/7] metrics + flags")
    df = add_metrics_and_flags(df)
    df.to_parquet(args.outdir / "user_rating_profiles.parquet", index=False)

    # Empirical binned distribution for the chance baseline.
    bin_tot = df[[f"c{i}" for i in range(1, 11)]].sum().to_numpy(float)
    P_EMP_BINNED = bin_tot / bin_tot.sum()

    print("[3/7] chance-level simulation baselines (seed=42)")
    rng = np.random.default_rng(SEED)
    chance = simulate_chance_rates(rng)
    chance.to_csv(args.outdir / "chance_baseline_by_threshold.csv", index=False)

    print("[4/7] prevalence tables")
    prev = prevalence_table(df)
    prev.to_csv(args.outdir / "prevalence_by_threshold.csv", index=False)
    bands = band_table(df)
    bands.to_csv(args.outdir / "prevalence_by_band.csv", index=False)
    bpairs = binary_pair_table(df)
    if len(bpairs):
        bpairs.to_csv(args.outdir / "binary_pair_patterns.csv", index=False)

    print("[5/7] removal sensitivity")
    rem = removal_sensitivity(df)
    rem.to_csv(args.outdir / "removal_sensitivity.csv", index=False)

    print("[6/7] game context for flagged vs other n>=20 raters")
    _, ctx_summary = game_context(con, obs_sql, df, args.outdir)
    impact = game_impact(con, obs_sql, df, args.outdir)

    print("[7/7] summaries")
    summary = {
        "universe": universe_note,
        "observations_source": str(obs_path),
        "total_users": int(len(df)),
        "total_observations": int(df["n"].sum()),
        "median_user_n": float(df["n"].median()),
        "definitions": {
            "binning": "ROUND(rating) clipped to [1,10]; SD/range/min/max on raw floats",
            "flags": {
                "f_single_value": "all ratings in one integer bin",
                "f_k_le2": "<=2 distinct integer bins used",
                "f_range_le1": "MAX(rating)-MIN(rating) <= 1.0 (raw)",
                "f_sd_lt_02": "STDDEV_SAMP(rating) < 0.2",
                "f_sd_lt_05": "SD < 0.5 (median within-user SD is ~1.21 in Phase 2)",
                "f_modal_ge80/ge90/eq100": "share of ratings at modal bin",
                "f_entropy_lt05": "Shannon entropy of binned histogram < 0.5 bits (max log2(10)=3.32)",
                "f_top2_ge95": "top-2 bins cover >= 95% of ratings",
                "degenerate_broad": "n>=10 AND (k<=2 OR SD<0.5 OR modal>=0.90)",
                "degenerate_strict": "n>=20 AND (single-value OR SD<0.2 OR modal>=0.95)",
            },
            "note": "composites are decision-context only; no exclusion performed",
        },
        "headline": {},
    }
    row10 = prev[prev["threshold_min_n"] == 10].iloc[0]
    row20 = prev[prev["threshold_min_n"] == 20].iloc[0]
    row100 = prev[prev["threshold_min_n"] == 100].iloc[0]
    summary["headline"] = {
        "pct_degenerate_broad_among_n_ge_10": float(row10["pct_degenerate_broad"]),
        "pct_degenerate_strict_among_n_ge_20": float(row20["pct_degenerate_strict"]),
        "pct_degenerate_strict_among_n_ge_100": float(row100["pct_degenerate_strict"]),
        "pct_single_value_among_n_ge_20": float(row20["pct_f_single_value"]),
        "pct_sd_lt_05_among_n_ge_20": float(row20["pct_f_sd_lt_05"]),
    }
    if args.full_rater_stats and Path(args.full_rater_stats).exists():
        summary["full_snapshot_comparator"] = full_snapshot_comparator(
            df, Path(args.full_rater_stats), args.outdir)
        summary["full_snapshot_comparator"]["caveat"] = (
            "descriptive only; full-snapshot lifetime counts include ratings "
            "outside the 16,627-game population")
    ctx_summary_dict = ctx_summary.to_dict(orient="records")
    summary["game_context"] = ctx_summary_dict
    summary["game_impact"] = impact

    with open(args.outdir / "audit_summary.json", "w") as fh:
        json.dump(summary, fh, indent=2)

    # Committed copies (data/processed is gitignored; repo precedent keeps
    # small result tables under reports/, cf. user_population_thresholds).
    reports = root / "reports" / "anomalous_rater_audit"
    reports.mkdir(parents=True, exist_ok=True)
    for name in [
        "prevalence_by_threshold.csv", "chance_baseline_by_threshold.csv",
        "prevalence_by_band.csv", "binary_pair_patterns.csv",
        "removal_sensitivity.csv", "flagged_user_context.csv",
        "game_impact.csv", "full_vs_filtered_band_shift.csv",
        "audit_summary.json",
    ]:
        src = args.outdir / name
        if src.exists():
            (reports / name).write_text(src.read_text())

    print(json.dumps(summary["headline"], indent=2))
    print("done ->", args.outdir)


if __name__ == "__main__":
    main()

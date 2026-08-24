"""Phase 3 prep: what minimum lifetime rating count should define the
primary analytical user population?

The game universe is fixed at the corrected 16,627-game research population
(data/processed/bgg_research_population.parquet).  This script compares
candidate per-user minimum lifetime rating-count thresholds
t in {1, 3, 5, 10, 20, 50, 100} - where lifetime is counted WITHIN that
universe unless stated otherwise - on four axes:

  1. Scale: users and ratings retained per threshold, filtered universe
     first-class, full phase-2 snapshot for reference.
  2. Stability of user-level means/severity via the established even/odd
     rating_observation_id parity design (scripts 14/16): Pearson/Spearman
     correlation of half-statistics, median absolute difference, ICC-style
     reliability using the script-18 signal/noise decomposition.
     A one-sweep game-adjusted severity proxy (user mean of
     rating - own-half game mean) is reported alongside raw means; it is
     the first alternating-projection step of script 16, not a refit.
  3. Diagnostics separating "insufficient history" from "meaningful rater":
     between-user SD of user means, mean within-user SD, distinct-game
     coverage.
  4. Low-tail qualitative check: volume-band breakdown recomputed on the
     filtered universe, rating-distribution shape by band.

Duplicates are preserved per the canonical definition (rating_observations
is non-null-filtered but NOT deduplicated; repeated user-game rows are rare,
~0.007% of observations).  Timestamps are unused.

This is a population-definition study, NOT a debiasing or credibility
analysis: thresholds describe how much history a user needs for their
user-level statistics to be stable enough to condition on; they imply
nothing about rater accuracy, and low-volume users remain informative for
game-level aggregates regardless of the choice.

Outputs:
  reports/user_population_thresholds.csv   main table, one row per threshold
  reports/user_population_thresholds.json  full detail incl. band breakdown
"""

import argparse
import json
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

REPO_DIR = Path(__file__).resolve().parent.parent

THRESHOLDS = [1, 3, 5, 10, 20, 50, 100]

# Bands over lifetime counts n, used both for the full-snapshot reference
# bands (matching scripts 14/16) and the filtered-universe recomputation.
BAND_SQL = """
    CASE WHEN n = 1 THEN '1'
         WHEN n BETWEEN 2 AND 4 THEN '2-4'
         WHEN n BETWEEN 5 AND 9 THEN '5-9'
         WHEN n BETWEEN 10 AND 24 THEN '10-24'
         WHEN n BETWEEN 25 AND 49 THEN '25-49'
         WHEN n BETWEEN 50 AND 99 THEN '50-99'
         WHEN n BETWEEN 100 AND 249 THEN '100-249'
         WHEN n BETWEEN 250 AND 499 THEN '250-499'
         WHEN n BETWEEN 500 AND 999 THEN '500-999'
         ELSE '1000+' END"""
BAND_ORDER = ["1", "2-4", "5-9", "10-24", "25-49",
              "50-99", "100-249", "250-499", "500-999", "1000+"]

con: duckdb.DuckDBPyConnection


def q(path) -> str:
    return str(path).replace("'", "''")


def stability_block(table: str, even_col: str, odd_col: str) -> dict:
    """Split-half stability stats + script-18 style ICC reliability."""
    row = con.execute(f"""
        WITH rk AS (
            SELECT {even_col} AS e, {odd_col} AS o,
                   RANK() OVER (ORDER BY {even_col}) AS re,
                   RANK() OVER (ORDER BY {odd_col}) AS ro
            FROM {table}
        ), s AS (
            SELECT COUNT(*) AS n,
                   CORR(e, o) AS pearson,
                   CORR(re::DOUBLE, ro::DOUBLE) AS spearman,
                   QUANTILE_CONT(ABS(e - o), 0.5) AS med_absdiff,
                   QUANTILE_CONT(ABS(e - o), 0.9) AS p90_absdiff,
                   STDDEV_SAMP(e) AS sd_e,
                   STDDEV_SAMP(o - e) AS sd_diff
            FROM rk
        )
        SELECT n, pearson, spearman, med_absdiff, p90_absdiff,
               sd_e, sd_diff FROM s
    """).fetchone()
    n, pearson, spearman, med_absdiff, p90, sd_e, sd_diff = (
        float(v) if v is not None else float("nan") for v in row)
    # script-18 decomposition: noise SD of a half estimate ~ sd(diff)/sqrt(2)
    noise_half = sd_diff / np.sqrt(2.0)
    var_total = sd_e ** 2
    var_signal = max(var_total - noise_half ** 2, 0.0)
    reliability = var_signal / var_total if var_total > 0 else float("nan")
    return {
        "users_with_both_halves": int(n),
        "pearson": pearson, "spearman": spearman,
        "median_abs_half_diff": med_absdiff,
        "p90_abs_half_diff": p90,
        "sd_half": sd_e, "sd_difference": sd_diff,
        "icc_style_reliability": reliability,
    }


def main():
    global con
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", type=Path, default=None,
                    help="directory containing rating_observations.parquet")
    ap.add_argument("--population", type=Path,
                    default=REPO_DIR / "data" / "processed" / "bgg_research_population.parquet")
    ap.add_argument("--out-dir", type=Path, default=REPO_DIR / "reports")
    args = ap.parse_args()

    data_dir = args.data_dir
    if data_dir is None:
        scratch = REPO_DIR / "scratch" / "phase2"
        data_dir = scratch if (scratch / "rating_observations.parquet").exists() \
            else REPO_DIR / "data" / "processed" / "phase2"

    args.out_dir.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect()
    con.execute("SET memory_limit='12GB'")
    con.execute("SET threads TO 8")
    con.execute(f"CREATE VIEW pop AS SELECT game_id FROM read_parquet('{q(args.population)}')")
    con.execute(f"CREATE VIEW ro_all AS SELECT * FROM read_parquet('{q(data_dir / 'rating_observations.parquet')}')")
    # Canonical observations restricted to the fixed research-population games.
    con.execute("""
        CREATE VIEW ro AS
        SELECT r.* FROM ro_all r SEMI JOIN pop p USING (game_id)
    """)

    summary = {
        "data_dir": str(data_dir),
        "population_file": str(args.population),
        "definition_notes": [
            "lifetime count = canonical source observations (duplicates "
            "preserved) on games in the 16,627-game research population, "
            "unless labeled full_snapshot",
            "stability uses the even/odd rating_observation_id parity split; "
            "only users with >=1 observation in each half contribute",
            "ICC-style reliability reuses the script-18 decomposition: "
            "noise_sd(half)=sd(diff)/sqrt(2); signal=max(var_total-noise^2,0); "
            "reliability=signal/var_total",
            "severity proxy = one alternating-projection sweep (script 16 "
            "step 1): user mean of rating minus own-half game mean",
        ],
    }

    # ------------------------------------------------------------------
    # Per-user sufficient statistics on the FILTERED universe
    # ------------------------------------------------------------------
    print("building per-user parity-split statistics ...", flush=True)
    con.execute("""
        CREATE TABLE ustats AS
        SELECT user_pseudouserid AS uid,
               COUNT(*) AS n,
               COUNT(DISTINCT game_id) AS n_games,
               AVG(rating) AS mean_all,
               CASE WHEN COUNT(*) >= 2 THEN STDDEV_SAMP(rating) END AS sd_within,
               AVG(rating) FILTER (WHERE rating_observation_id % 2 = 0) AS mean_even,
               AVG(rating) FILTER (WHERE rating_observation_id % 2 = 1) AS mean_odd
        FROM ro GROUP BY 1
    """)

    # One-sweep severity proxy per parity half (ALS step 1 of script 16):
    # subtract the half's own game means, then average residuals per user.
    con.execute("""
        CREATE TABLE udelta AS
        SELECT e.uid AS uid, e.delta AS delta_even, o.delta AS delta_odd
        FROM (
            SELECT r.user_pseudouserid AS uid,
                   AVG(r.rating - g.alpha) AS delta
            FROM ro r LEFT JOIN (
                SELECT game_id, AVG(rating) AS alpha FROM ro
                WHERE rating_observation_id % 2 = 0 GROUP BY 1
            ) g ON r.game_id = g.game_id
            WHERE r.rating_observation_id % 2 = 0
            GROUP BY 1
        ) e JOIN (
            SELECT r.user_pseudouserid AS uid,
                   AVG(r.rating - g.alpha) AS delta
            FROM ro r LEFT JOIN (
                SELECT game_id, AVG(rating) AS alpha FROM ro
                WHERE rating_observation_id % 2 = 1 GROUP BY 1
            ) g ON r.game_id = g.game_id
            WHERE r.rating_observation_id % 2 = 1
            GROUP BY 1
        ) o USING (uid)
    """)
    con.execute("""
        ALTER TABLE ustats ADD COLUMN IF NOT EXISTS delta_even DOUBLE
    """)
    con.execute("""
        ALTER TABLE ustats ADD COLUMN IF NOT EXISTS delta_odd DOUBLE
    """)
    con.execute("""
        UPDATE ustats SET delta_even = d.delta_even, delta_odd = d.delta_odd
        FROM udelta d WHERE ustats.uid = d.uid
    """)

    totals_f = con.execute(
        "SELECT COUNT(*), SUM(n), AVG(mean_all) FROM ustats").fetchone()
    totals_all = con.execute("""
        SELECT COUNT(DISTINCT user_pseudouserid), COUNT(*) FROM ro_all
    """).fetchone()
    games_in_snapshot = con.execute(
        "SELECT COUNT(DISTINCT game_id) FROM ro").fetchone()[0]
    n_pop_games = con.execute("SELECT COUNT(*) FROM pop").fetchone()[0]
    summary["filtered_universe"] = {
        "users_with_any_rating": int(totals_f[0]),
        "observations": int(totals_f[1]),
        "mean_user_rating_over_users": float(totals_f[2]),
    }
    summary["full_snapshot_reference"] = {
        "users_with_any_rating": int(totals_all[0]),
        "observations": int(totals_all[1]),
    }
    summary["universe_coverage"] = {
        "population_games": int(n_pop_games),
        "population_games_rated_in_phase2_snapshot": int(games_in_snapshot),
    }

    # ------------------------------------------------------------------
    # 1. Scale + 2. Stability + 3. Diagnostics per threshold
    # ------------------------------------------------------------------
    rows = []
    detail = {}
    for t in THRESHOLDS:
        scale = con.execute(f"""
            SELECT COUNT(*), SUM(n), SUM(n_games),
                   AVG(mean_all), STDDEV_SAMP(mean_all),
                   AVG(sd_within), AVG(n_games),
                   QUANTILE_CONT(n_games, 0.5)
            FROM ustats WHERE n >= {t}
        """).fetchone()
        users_r, ratings_r, games_sum_r, mean_level, bet_sd, wsd, agames, medgames = scale

        stab_mean = stability_block(
            f"(SELECT * FROM ustats WHERE n >= {t} "
            f"AND mean_even IS NOT NULL AND mean_odd IS NOT NULL)",
            "mean_even", "mean_odd")
        stab_delta = stability_block(
            f"(SELECT * FROM ustats WHERE n >= {t} "
            f"AND delta_even IS NOT NULL AND delta_odd IS NOT NULL)",
            "delta_even", "delta_odd")

        rows.append({
            "threshold_t": t,
            "users_retained_filtered": int(users_r),
            "ratings_retained_filtered": int(ratings_r),
            "share_users_filtered": users_r / totals_f[0],
            "share_ratings_filtered": ratings_r / totals_f[1],
            "distinct_game_ratings_retained": int(games_sum_r),
            "split_users_mean_stability": stab_mean["users_with_both_halves"],
            "split_users_severity_proxy": stab_delta["users_with_both_halves"],
            "stability_mean_pearson": stab_mean["pearson"],
            "stability_mean_spearman": stab_mean["spearman"],
            "median_abs_half_diff": stab_mean["median_abs_half_diff"],
            "icc_reliability_mean": stab_mean["icc_style_reliability"],
            "severity_proxy_pearson": stab_delta["pearson"],
            "severity_proxy_spearman": stab_delta["spearman"],
            "severity_proxy_median_abs_diff": stab_delta["median_abs_half_diff"],
            "icc_reliability_severity_proxy": stab_delta["icc_style_reliability"],
            "mean_user_rating": float(mean_level),
            "between_user_sd_of_means": float(bet_sd),
            "mean_within_user_sd": float(wsd) if wsd is not None else float("nan"),
            "mean_distinct_games_per_user": float(agames),
            "median_distinct_games_per_user": float(medgames),
        })
        detail[f"t={t}"] = {"scale_stability_diagnostics": rows[-1],
                            "mean_split": stab_mean,
                            "severity_proxy_split": stab_delta}
        print(f"t={t:>3}: users={int(users_r):>7,} ratings={int(ratings_r):>12,} "
              f"r={stab_mean['pearson']:.3f} icc={stab_mean['icc_style_reliability']:.3f}",
              flush=True)

    df = pd.DataFrame(rows)

    # ------------------------------------------------------------------
    # Full-snapshot reference scale (lifetime = all phase-2 ratings)
    # ------------------------------------------------------------------
    conds_u = [f"SUM(CASE WHEN n >= {t} THEN 1 ELSE 0 END) AS u{t}" for t in THRESHOLDS]
    conds_r = [f"SUM(CASE WHEN n >= {t} THEN n ELSE 0 END) AS r{t}" for t in THRESHOLDS]
    ref = con.execute(f"""
        WITH u AS (
            SELECT user_pseudouserid AS uid, COUNT(*) AS n FROM ro_all GROUP BY 1
        )
        SELECT {', '.join(conds_u + conds_r)}
        FROM u
    """).fetchdf().iloc[0]
    ref_rows = [{
        "threshold_t": t,
        "users_retained_full_snapshot": int(ref[f"u{t}"]),
        "ratings_retained_full_snapshot": int(ref[f"r{t}"]),
        "share_users_full_snapshot": float(ref[f"u{t}"]) / totals_all[0],
        "share_ratings_full_snapshot": float(ref[f"r{t}"]) / totals_all[1],
    } for t in THRESHOLDS]
    df = df.merge(pd.DataFrame(ref_rows), on="threshold_t")

    # ------------------------------------------------------------------
    # Game-level Phase 3 impact: how many population games keep a usable
    # rater pool (>=K retained raters) under each threshold?
    # ------------------------------------------------------------------
    game_impact = []
    for t in THRESHOLDS:
        counts = {k: 0 for k in (1, 5, 10, 30)}
        r = con.execute(f"""
            SELECT COUNT(*) FILTER (WHERE n_raters >= 1) AS g1,
                   COUNT(*) FILTER (WHERE n_raters >= 5) AS g5,
                   COUNT(*) FILTER (WHERE n_raters >= 10) AS g10,
                   COUNT(*) FILTER (WHERE n_raters >= 30) AS g30
            FROM (
                SELECT r.game_id, COUNT(DISTINCT u.uid) AS n_raters
                FROM ro r JOIN ustats u ON r.user_pseudouserid = u.uid
                WHERE u.n >= {t} GROUP BY r.game_id
            )
        """).fetchone()
        game_impact.append({"threshold_t": t, "games_ge1_raters": int(r[0]),
                            "games_ge5_raters": int(r[1]),
                            "games_ge10_raters": int(r[2]),
                            "games_ge30_raters": int(r[3])})
        print(f"t={t:>3}: games with >=10 retained raters: {int(r[2]):,}", flush=True)
    summary["game_level_impact_filtered"] = game_impact
    df = df.merge(pd.DataFrame(game_impact), on="threshold_t")

    # ------------------------------------------------------------------
    # 4. Low-tail qualitative check: bands recomputed on FILTERED counts
    # ------------------------------------------------------------------
    band = con.execute(f"""
        WITH b AS (SELECT *, {BAND_SQL} AS volume_band FROM ustats)
        SELECT volume_band,
               COUNT(*) AS users,
               SUM(n) AS observations,
               AVG(mean_all) AS mean_user_rating,
               STDDEV_SAMP(mean_all) AS between_user_sd_of_means,
               AVG(sd_within) AS mean_within_user_sd,
               AVG(n_games) AS mean_distinct_games
        FROM b GROUP BY 1
    """).fetchdf()
    band = band.set_index("volume_band").loc[BAND_ORDER].reset_index()
    summary["band_breakdown_filtered_universe"] = band.to_dict(orient="records")

    dist_df = con.execute(f"""
        WITH joined AS (
            SELECT u.n AS n, r.rating AS rating
            FROM ustats u JOIN ro r ON u.uid = r.user_pseudouserid
        ), b AS (SELECT *, {BAND_SQL} AS volume_band FROM joined)
        SELECT volume_band, COUNT(*) AS observations,
               AVG(rating) AS mean_rating,
               QUANTILE_CONT(rating, 0.5) AS median_rating,
               AVG(CASE WHEN rating >= 9 THEN 1.0 ELSE 0 END) AS share_ge9,
               AVG(CASE WHEN rating = 10 THEN 1.0 ELSE 0 END) AS share_eq10,
               AVG(CASE WHEN rating <= 4 THEN 1.0 ELSE 0 END) AS share_le4
        FROM b GROUP BY 1
    """).fetchdf()
    dist_df = dist_df.set_index("volume_band").loc[BAND_ORDER].reset_index()
    summary["band_rating_distribution_filtered"] = dist_df.to_dict(orient="records")

    # ------------------------------------------------------------------
    # Persist outputs
    # ------------------------------------------------------------------
    csv_path = args.out_dir / "user_population_thresholds.csv"
    json_path = args.out_dir / "user_population_thresholds.json"
    df.to_csv(csv_path, index=False, float_format="%.6f")
    summary["threshold_table"] = df.to_dict(orient="records")
    summary["threshold_detail"] = detail
    json_path.write_text(json.dumps(summary, indent=2, default=str) + "\n",
                         encoding="utf-8")

    show = ["threshold_t", "users_retained_filtered", "ratings_retained_filtered",
            "share_ratings_filtered", "stability_mean_pearson",
            "stability_mean_spearman", "median_abs_half_diff",
            "icc_reliability_mean", "between_user_sd_of_means"]
    print(df[show].to_string(index=False))
    print(band.to_string(index=False))
    print(dist_df.to_string(index=False))
    print(f"\nwrote {csv_path}\nwrote {json_path}")
    con.close()


if __name__ == "__main__":
    main()

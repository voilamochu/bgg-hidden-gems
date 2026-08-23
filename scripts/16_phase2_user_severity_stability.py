"""Phase A step 2: per-user severity offsets, their stability, and whether
they improve out-of-sample prediction.

Step 1 (script 15) showed the low-vs-high volume rating gap survives within
games (+1.3 to +2.3 points).  This script conditions on games explicitly:

  1. Two-way additive fit  y_ug = mu + alpha_g + delta_u  by alternating
     least squares (alternating projections) over the canonical observations.
     delta_u is the per-user severity offset conditioned on the games rated.
  2. Stability of delta_u:
     a. even/odd split of observations (rating_observation_id parity),
        independent halves, refit on each;
     b. time-period splits using postdate and, separately, rating_tstamp
        (both semantics unresolved - reported side by side as sensitivity).
  3. Held-out prediction test: fit effects on one half, predict the other.
     Does adding delta_u reduce RMSE versus game information alone?
     This - not statistical significance - decides whether a severity
     correction is worth anything for RQ1/RQ2 use.

Outputs: user_severity.parquet, game_adjusted_means.parquet,
user_severity_stability.json under data/processed/phase2/.
"""

import argparse
import json
from pathlib import Path

import duckdb
import numpy as np

REPO_DIR = Path(__file__).resolve().parent.parent

BAND_ORDER = ["1", "2-4", "5-9", "10-24", "25-49",
              "50-99", "100-249", "250-499", "500-999", "1000+"]


def q(path) -> str:
    return str(path).replace("'", "''")


def als_fit(con: duckdb.DuckDBPyConnection, source_view: str,
            prefix: str, n_iter: int = 120, tol: float = 2e-3, omega: float = 1.0):
    """Alternating projections for y_ug = mu + alpha_g + delta_u.

    omega is the relaxation factor: 1.0 = plain alternating projections;
    values >1 accelerate but can diverge, so divergence is guarded below.

    Creates tables {prefix}_ge(game_id, alpha) and {prefix}_ue(uid, delta),
    both mean-centered so mu is the grand mean.  Returns (mu, history) where
    history holds the max absolute parameter change per iteration.
    """
    mu = con.execute(f"SELECT AVG(rating) FROM {source_view}").fetchone()[0]
    con.execute(f"""
        CREATE OR REPLACE TABLE {prefix}_ge AS
        SELECT game_id, AVG(rating) - {mu} AS alpha
        FROM {source_view} GROUP BY game_id
    """)
    con.execute(f"""
        CREATE OR REPLACE TABLE {prefix}_ue AS
        SELECT user_pseudouserid AS uid,
               AVG(rating - {mu} - COALESCE(g.alpha, 0)) AS delta
        FROM {source_view} s LEFT JOIN {prefix}_ge g USING (game_id)
        GROUP BY user_pseudouserid
    """)

    def sweep_user():
        # delta_new(u) = mean(y - mu - alpha_g) over u's observations,
        # then mean-centered; change measured vs previous centered delta.
        con.execute(f"""
            CREATE OR REPLACE TABLE {prefix}_ue_new AS
            SELECT s.user_pseudouserid AS uid,
                   AVG(s.rating - {mu} - COALESCE(g.alpha, 0)) AS delta
            FROM {source_view} s
            LEFT JOIN {prefix}_ge g USING (game_id)
            GROUP BY s.user_pseudouserid
        """)
        m = con.execute(f"SELECT AVG(delta) FROM {prefix}_ue_new").fetchone()[0]
        con.execute(f"UPDATE {prefix}_ue_new SET delta = delta + ({omega} - 1) * (delta - {m})")
        d = con.execute(f"""
            SELECT COALESCE(MAX(ABS(n.delta - o.delta)), 0)
            FROM {prefix}_ue_new n JOIN {prefix}_ue o USING (uid)
        """).fetchone()[0]
        con.execute(f"DROP TABLE {prefix}_ue")
        con.execute(f"ALTER TABLE {prefix}_ue_new RENAME TO {prefix}_ue")
        return float(d)

    def sweep_game():
        # alpha_new(g) = mean(y - mu - delta_u) over g's observations,
        # then mean-centered; change measured vs previous centered alpha.
        con.execute(f"""
            CREATE OR REPLACE TABLE {prefix}_ge_new AS
            SELECT s.game_id AS game_id,
                   AVG(s.rating - {mu} - COALESCE(u.delta, 0)) AS alpha
            FROM {source_view} s
            LEFT JOIN {prefix}_ue u ON s.user_pseudouserid = u.uid
            GROUP BY s.game_id
        """)
        m = con.execute(f"SELECT AVG(alpha) FROM {prefix}_ge_new").fetchone()[0]
        con.execute(f"UPDATE {prefix}_ge_new SET alpha = alpha + ({omega} - 1) * (alpha - {m})")
        d = con.execute(f"""
            SELECT COALESCE(MAX(ABS(n.alpha - o.alpha)), 0)
            FROM {prefix}_ge_new n JOIN {prefix}_ge o USING (game_id)
        """).fetchone()[0]
        con.execute(f"DROP TABLE {prefix}_ge")
        con.execute(f"ALTER TABLE {prefix}_ge_new RENAME TO {prefix}_ge")
        return float(d)

    history = []
    for it in range(n_iter):
        du = sweep_user()
        dg = sweep_game()
        history.append(max(du, dg))
        if max(du, dg) < tol:
            break
        if it >= 6 and all(history[-k] > history[-k - 1] * 1.5 for k in (1, 2)):
            raise RuntimeError(f"alternating projections diverging: {history[-3:]})")
    # final centering so mu stays the grand mean
    con.execute(f"UPDATE {prefix}_ue SET delta = delta - (SELECT AVG(delta) FROM {prefix}_ue)")
    con.execute(f"UPDATE {prefix}_ge SET alpha = alpha - (SELECT AVG(alpha) FROM {prefix}_ge)")
    return float(mu), history


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", type=Path, default=None)
    ap.add_argument("--out-dir", type=Path, default=REPO_DIR / "data" / "processed" / "phase2")
    ap.add_argument("--n-iter", type=int, default=100)
    ap.add_argument("--reuse", action="store_true",
                    help="Reuse saved user_severity/game_adjusted_means parquets "
                         "instead of refitting ALS (fast summary recomputation)")
    args = ap.parse_args()

    data_dir = args.data_dir
    if data_dir is None:
        scratch = REPO_DIR / "scratch" / "phase2"
        data_dir = scratch if (scratch / "rating_observations.parquet").exists() \
            else REPO_DIR / "data" / "processed" / "phase2"
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect()
    con.execute(f"CREATE OR REPLACE VIEW ro AS SELECT * FROM read_parquet('{q(data_dir / 'rating_observations.parquet')}')")
    con.execute(f"CREATE OR REPLACE VIEW rbv AS SELECT * FROM read_parquet('{q(data_dir / 'rater_behavior_by_volume.parquet')}')")
    con.execute("""
        CREATE OR REPLACE VIEW obs AS
        SELECT r.rating_observation_id, r.game_id, r.user_pseudouserid,
               r.rating, b.volume_band,
               TRY_CAST(r.postdate AS TIMESTAMP) AS post_ts,
               TRY_CAST(r.rating_tstamp AS TIMESTAMP) AS rate_ts
        FROM ro r JOIN rbv b USING (user_pseudouserid)
    """)
    summary = {"data_dir": str(data_dir)}

    # ------------------------------------------------------------------
    # Full-sample two-way fit (or reuse saved effects)
    # ------------------------------------------------------------------
    sev_path = out_dir / "user_severity.parquet"
    gm_path0 = out_dir / "game_adjusted_means.parquet"
    if args.reuse:
        con.execute(f"CREATE OR REPLACE VIEW sev AS SELECT * FROM read_parquet('{q(sev_path)}')")
        con.execute("CREATE OR REPLACE VIEW full_ue AS "
                    "SELECT user_pseudouserid AS uid, delta_full AS delta FROM sev")
        con.execute("CREATE OR REPLACE VIEW evn_ue AS "
                    "SELECT user_pseudouserid AS uid, delta_even AS delta FROM sev WHERE delta_even IS NOT NULL")
        con.execute("CREATE OR REPLACE VIEW odd_ue AS "
                    "SELECT user_pseudouserid AS uid, delta_odd AS delta FROM sev WHERE delta_odd IS NOT NULL")
        con.execute("CREATE OR REPLACE VIEW posA_ue AS "
                    "SELECT user_pseudouserid AS uid, delta_post_early AS delta FROM sev WHERE delta_post_early IS NOT NULL")
        con.execute("CREATE OR REPLACE VIEW posB_ue AS "
                    "SELECT user_pseudouserid AS uid, delta_post_late AS delta FROM sev WHERE delta_post_late IS NOT NULL")
        con.execute("CREATE OR REPLACE VIEW rtsA_ue AS "
                    "SELECT user_pseudouserid AS uid, delta_rt_early AS delta FROM sev WHERE delta_rt_early IS NOT NULL")
        con.execute("CREATE OR REPLACE VIEW rtsB_ue AS "
                    "SELECT user_pseudouserid AS uid, delta_rt_late AS delta FROM sev WHERE delta_rt_late IS NOT NULL")
        con.execute(f"CREATE OR REPLACE VIEW full_ge AS "
                    f"SELECT game_id, game_alpha AS alpha FROM read_parquet('{q(gm_path0)}')")
        mu = con.execute("SELECT AVG(rating) FROM obs").fetchone()[0]
        summary["als_convergence_full"] = {"reused": True, "mu": float(mu)}
        print("ALS full: reused saved effects", flush=True)
    else:
        mu, hist = als_fit(con, "obs", "full", n_iter=args.n_iter)
        summary["als_convergence_full"] = {"mu": float(mu), "iterations": len(hist),
                                           "final_max_change": hist[-1]}
        print("ALS full:", summary["als_convergence_full"], flush=True)

    band_delta = con.execute("""
        SELECT b.volume_band, COUNT(*) AS users,
               AVG(u.delta) AS mean_delta,
               STDDEV_SAMP(u.delta) AS sd_delta,
               QUANTILE_CONT(u.delta, 0.5) AS median_delta
        FROM full_ue u JOIN rbv b ON u.uid = b.user_pseudouserid
        GROUP BY b.volume_band
    """).fetchdf().set_index("volume_band").loc[BAND_ORDER].reset_index()
    summary["severity_by_band"] = band_delta.to_dict(orient="records")

    r2row = con.execute("""
        WITH gmean AS (
            SELECT game_id, AVG(rating) AS gm FROM obs GROUP BY game_id
        ), j AS (
            SELECT o.rating AS y,
                   g.alpha AS a,
                   w.gm AS gm,
                   v.mean_rating AS um,
                   COALESCE(u.delta, 0) AS d
            FROM obs o
            JOIN full_ge g ON o.game_id = g.game_id
            JOIN gmean w ON o.game_id = w.game_id
            LEFT JOIN full_ue u ON o.user_pseudouserid = u.uid
            JOIN rbv v ON o.user_pseudouserid = v.user_pseudouserid
        ), agg AS (
            SELECT VAR_SAMP(y) AS vt,
                   VAR_SAMP(y - (gm - (SELECT AVG(rating) FROM obs))) AS vr_g,
                   VAR_SAMP(y - (um - (SELECT AVG(rating) FROM obs))) AS vr_u,
                   VAR_SAMP(y - ({MU} + a + d)) AS vr_b
            FROM j
        )
        SELECT vt, 1 - vr_g / vt, 1 - vr_u / vt, 1 - vr_b / vt FROM agg
    """.replace("{MU}", repr(mu))).fetchone()
    summary["variance_decomposition_nested_r2"] = {
        "total_var": float(r2row[0]),
        "r2_game_identity_only": float(r2row[1]),
        "r2_rater_identity_only": float(r2row[2]),
        "r2_additive_both": float(r2row[3]),
        "note": "nested-model R2 of rating variance explained by game identity "
                "(raw game mean), rater identity (raw user mean), and the "
                "additive two-way fit. Marginal effect moments are not used "
                "because they double-count under unbalanced correlated factors.",
    }

    # ------------------------------------------------------------------
    # Even/odd split fits and severity stability
    # ------------------------------------------------------------------
    con.execute("CREATE OR REPLACE VIEW obs_even AS SELECT * FROM obs WHERE rating_observation_id % 2 = 0")
    con.execute("CREATE OR REPLACE VIEW obs_odd AS SELECT * FROM obs WHERE rating_observation_id % 2 = 1")
    if args.reuse:
        mu_e = con.execute("SELECT AVG(rating) FROM obs_even").fetchone()[0]
        mu_o = con.execute("SELECT AVG(rating) FROM obs_odd").fetchone()[0]
    else:
        mu_e, hist_e = als_fit(con, "obs_even", "evn", n_iter=args.n_iter)
        print("ALS even done:", len(hist_e), hist_e[-1], flush=True)
        mu_o, hist_o = als_fit(con, "obs_odd", "odd", n_iter=args.n_iter)
        print("ALS odd done:", len(hist_o), hist_o[-1], flush=True)

    stab_parity = con.execute("""
        WITH j AS (
            SELECT e.delta AS d_even, o.delta AS d_odd,
                   ea.rating_observations AS n_even, oa.rating_observations AS n_odd
            FROM evn_ue e
            JOIN odd_ue o ON e.uid = o.uid
            JOIN rbv ea ON e.uid = ea.user_pseudouserid
            JOIN rbv oa ON o.uid = oa.user_pseudouserid
            WHERE ea.rating_observations >= 20 AND oa.rating_observations >= 20
        ), rk AS (
            SELECT d_even, d_odd,
                   RANK() OVER (ORDER BY d_even) AS r_even,
                   RANK() OVER (ORDER BY d_odd) AS r_odd,
                   ABS(d_even - d_odd) AS absdiff,
                   d_even - d_odd AS diff
            FROM j
        )
        SELECT COUNT(*), CORR(d_even, d_odd), CORR(r_even::DOUBLE, r_odd::DOUBLE),
               QUANTILE_CONT(absdiff, 0.5),
               QUANTILE_CONT(absdiff, 0.9),
               STDDEV_SAMP(d_even), STDDEV_SAMP(d_odd),
               STDDEV_SAMP(diff)
        FROM rk
    """).fetchone()
    summary["stability_parity"] = {
        "users_compared": int(stab_parity[0]),
        "min_obs_each_half": 20,
        "pearson": float(stab_parity[1]), "spearman": float(stab_parity[2]),
        "median_abs_delta_diff": float(stab_parity[3]),
        "p90_abs_delta_diff": float(stab_parity[4]),
        "sd_even": float(stab_parity[5]), "sd_odd": float(stab_parity[6]),
        "sd_difference": float(stab_parity[7]),
    }

    # Placebo: correlate severities across DIFFERENT users (deterministic roll)
    a = con.execute("""
        SELECT delta FROM evn_ue e JOIN rbv b ON e.uid = b.user_pseudouserid
        WHERE b.rating_observations >= 20 ORDER BY e.uid LIMIT 100000
    """).fetchdf()["delta"].values
    bvec = con.execute("""
        SELECT delta FROM odd_ue o JOIN rbv b ON o.uid = b.user_pseudouserid
        WHERE b.rating_observations >= 20 ORDER BY o.uid LIMIT 100000
    """).fetchdf()["delta"].values
    nmin = min(len(a), len(bvec))
    rolled = np.roll(bvec[:nmin], nmin // 2)
    summary["placebo_mismatched_correlation"] = float(np.corrcoef(a[:nmin], rolled)[0, 1])

    # ------------------------------------------------------------------
    # Time-period split fits (both timestamp fields; semantics unresolved)
    # ------------------------------------------------------------------
    med_post, med_rt = con.execute(
        "SELECT MEDIAN(post_ts), MEDIAN(rate_ts) FROM obs").fetchone()
    summary["period_split_medians"] = {"postdate": str(med_post), "rating_tstamp": str(med_rt)}

    def period_fit_and_stability(ts_expr: str, med, tag: str, pa: str, pb: str):
        con.execute(f"""
            CREATE OR REPLACE VIEW obs_tsA AS SELECT * FROM obs
            WHERE {ts_expr} IS NOT NULL AND {ts_expr} <= TIMESTAMP '{med}'
        """)
        con.execute(f"""
            CREATE OR REPLACE VIEW obs_tsB AS SELECT * FROM obs
            WHERE {ts_expr} IS NOT NULL AND {ts_expr} > TIMESTAMP '{med}'
        """)
        n_a = con.execute("SELECT COUNT(*) FROM obs_tsA").fetchone()[0]
        n_b = con.execute("SELECT COUNT(*) FROM obs_tsB").fetchone()[0]
        if args.reuse:
            print(f"ALS {tag}: reused saved period deltas", flush=True)
        else:
            als_fit(con, "obs_tsA", pa, n_iter=args.n_iter)
            print(f"ALS {tag}-A done", flush=True)
            als_fit(con, "obs_tsB", pb, n_iter=args.n_iter)
            print(f"ALS {tag}-B done", flush=True)
        r = con.execute(f"""
            WITH j AS (
                SELECT {pa}_ue.delta AS d_a, {pb}_ue.delta AS d_b,
                       ba.rating_observations AS na, bb.rating_observations AS nb
                FROM {pa}_ue
                JOIN {pb}_ue ON {pa}_ue.uid = {pb}_ue.uid
                JOIN rbv ba ON {pa}_ue.uid = ba.user_pseudouserid
                JOIN rbv bb ON {pb}_ue.uid = bb.user_pseudouserid
                WHERE ba.rating_observations >= 10 AND bb.rating_observations >= 10
            ), rk AS (
                SELECT d_a, d_b,
                       RANK() OVER (ORDER BY d_a) AS r_a,
                       RANK() OVER (ORDER BY d_b) AS r_b,
                       ABS(d_a - d_b) AS absdiff
                FROM j
            )
            SELECT COUNT(*), CORR(d_a, d_b), CORR(r_a::DOUBLE, r_b::DOUBLE),
                   QUANTILE_CONT(absdiff, 0.5)
            FROM rk
        """).fetchone()
        return {"field": tag, "n_obs_periodA": int(n_a), "n_obs_periodB": int(n_b),
                "users_compared": int(r[0]), "pearson": float(r[1]),
                "spearman": float(r[2]), "median_abs_delta_diff": float(r[3])}

    summary["stability_time"] = [
        period_fit_and_stability("post_ts", med_post,
                                 "postdate", "posA", "posB"),
        period_fit_and_stability("rate_ts", med_rt,
                                 "rating_tstamp", "rtsA", "rtsB"),
    ]

    # ------------------------------------------------------------------
    # Game-level: raw vs severity-adjusted means
    # ------------------------------------------------------------------
    gm_path = out_dir / "game_adjusted_means.parquet"
    con.execute(f"""
        COPY (
            SELECT m.game_id,
                   COALESCE(g.alpha, 0) AS game_alpha,
                   m.n_obs,
                   m.raw_mean,
                   m.adj_mean
            FROM (
                SELECT o.game_id AS game_id,
                       COUNT(*) AS n_obs,
                       AVG(o.rating) AS raw_mean,
                       AVG(o.rating - COALESCE(u.delta, 0)) AS adj_mean
                FROM obs o LEFT JOIN full_ue u ON o.user_pseudouserid = u.uid
                GROUP BY o.game_id
            ) m
            LEFT JOIN full_ge g USING (game_id)
        ) TO '{q(gm_path)}' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)
    gstats = con.execute(f"""
        WITH rk AS (
            SELECT n_obs::DOUBLE AS n_obs, raw_mean, adj_mean,
                   RANK() OVER (ORDER BY raw_mean) AS r_raw,
                   RANK() OVER (ORDER BY adj_mean) AS r_adj
            FROM read_parquet('{q(gm_path)}')
        )
        SELECT CORR(raw_mean, adj_mean), CORR(r_raw::DOUBLE, r_adj::DOUBLE),
               CORR(n_obs, adj_mean - raw_mean),
               QUANTILE_CONT(adj_mean - raw_mean, 0.05),
               QUANTILE_CONT(adj_mean - raw_mean, 0.5),
               QUANTILE_CONT(adj_mean - raw_mean, 0.95)
        FROM rk
    """).fetchone()
    summary["game_level_adjustment"] = {
        "pearson_raw_vs_adj": float(gstats[0]), "spearman_raw_vs_adj": float(gstats[1]),
        "corr_n_obs_with_shift": float(gstats[2]),
        "shift_quantiles_p5_median_p95": [float(gstats[3]), float(gstats[4]), float(gstats[5])],
    }
    gshift = con.execute(f"""
        SELECT CASE WHEN n_obs >= 25000 THEN 'a_25k+'
                    WHEN n_obs >= 5000 THEN 'b_5k-25k'
                    WHEN n_obs >= 1000 THEN 'c_1k-5k'
                    WHEN n_obs >= 250 THEN 'd_250-1k'
                    ELSE 'e_<250' END AS vol_band,
               COUNT(*) AS games,
               QUANTILE_CONT(adj_mean - raw_mean, 0.5) AS median_shift,
               AVG(adj_mean - raw_mean) AS mean_shift
        FROM read_parquet('{q(gm_path)}')
        GROUP BY 1 ORDER BY 1
    """).fetchdf()
    summary["game_adjustment_shift_by_volume"] = gshift.to_dict(orient="records")

    # ------------------------------------------------------------------
    # Held-out prediction: does delta_u help?
    # ------------------------------------------------------------------
    def holdout(fit_prefix: str, fit_mu: float, train_view: str, test_view: str, tag: str):
        r = con.execute(f"""
            WITH t AS (
                SELECT s.rating AS y,
                       COALESCE(g.alpha, 0) AS alpha_g,
                       COALESCE(u.delta, 0) AS delta_u,
                       rm.raw_train_mean AS raw_mean
                FROM {test_view} s
                JOIN {fit_prefix}_ge g USING (game_id)
                LEFT JOIN {fit_prefix}_ue u ON s.user_pseudouserid = u.uid
                LEFT JOIN (
                    SELECT game_id, AVG(rating) AS raw_train_mean
                    FROM {train_view} GROUP BY game_id
                ) rm USING (game_id)
            )
            SELECT
                SQRT(AVG((y - ({fit_mu} + alpha_g))^2)) AS rmse_game_only,
                SQRT(AVG((y - ({fit_mu} + alpha_g + delta_u))^2)) AS rmse_with_user,
                SQRT(AVG((y - raw_mean)^2)) AS rmse_raw_game_mean,
                AVG(ABS(y - ({fit_mu} + alpha_g))) AS mae_game_only,
                AVG(ABS(y - ({fit_mu} + alpha_g + delta_u))) AS mae_with_user,
                COUNT(*)
            FROM t
        """).fetchone()
        return {tag: {
            "n_test": int(r[5]),
            "rmse_game_fe_only": float(r[0]),
            "rmse_game_fe_plus_user": float(r[1]),
            "rmse_raw_train_game_mean": float(r[2]),
            "mae_game_fe_only": float(r[3]),
            "mae_game_fe_plus_user": float(r[4]),
        }}

    def build_half_game_effects(prefix: str, half_mu: float):
        """Given fixed user deltas, the optimal game alphas are one group-by."""
        con.execute(f"""
            CREATE OR REPLACE TABLE {prefix}_ge AS
            SELECT s.game_id AS game_id,
                   AVG(s.rating - {half_mu} - COALESCE(u.delta, 0)) AS alpha
            FROM {"obs_even" if prefix == "evn" else "obs_odd"} s
            LEFT JOIN {prefix}_ue u ON s.user_pseudouserid = u.uid
            GROUP BY s.game_id
        """)

    if args.reuse:
        build_half_game_effects("evn", mu_e)
        build_half_game_effects("odd", mu_o)

    summary["holdout"] = {}
    summary["holdout"].update(holdout("evn", mu_e, "obs_even", "obs_odd", "fit_even_predict_odd"))
    summary["holdout"].update(holdout("odd", mu_o, "obs_odd", "obs_even", "fit_odd_predict_even"))

    imp = con.execute(f"""
        WITH pred AS (
            SELECT s.user_pseudouserid AS uid, s.rating AS y,
                   COALESCE(g.alpha, 0) AS alpha_g,
                   COALESCE(u.delta, 0) AS delta_u
            FROM obs_odd s
            JOIN evn_ge g USING (game_id)
            LEFT JOIN evn_ue u ON s.user_pseudouserid = u.uid
        )
        SELECT b.volume_band, COUNT(*) AS n,
               SQRT(AVG((y - ({mu_e} + alpha_g))^2)) AS rmse_game_only,
               SQRT(AVG((y - ({mu_e} + alpha_g + delta_u))^2)) AS rmse_with_user
        FROM pred p JOIN rbv b ON p.uid = b.user_pseudouserid
        GROUP BY b.volume_band
    """).fetchdf().set_index("volume_band").loc[BAND_ORDER].reset_index()
    summary["holdout_improvement_by_test_user_band"] = imp.to_dict(orient="records")

    # ------------------------------------------------------------------
    # Persist per-user severity table
    # ------------------------------------------------------------------
    us_path = out_dir / "user_severity.parquet"
    con.execute(f"""
        COPY (
            SELECT b.user_pseudouserid,
                   b.volume_band,
                   b.rating_observations,
                   f.delta AS delta_full,
                   evn.delta AS delta_even,
                   odd.delta AS delta_odd,
                   posA.delta AS delta_post_early,
                   posB.delta AS delta_post_late,
                   rtsA.delta AS delta_rt_early,
                   rtsB.delta AS delta_rt_late
            FROM rbv b
            LEFT JOIN full_ue f ON b.user_pseudouserid = f.uid
            LEFT JOIN evn_ue evn ON b.user_pseudouserid = evn.uid
            LEFT JOIN odd_ue odd ON b.user_pseudouserid = odd.uid
            LEFT JOIN posA_ue posA ON b.user_pseudouserid = posA.uid
            LEFT JOIN posB_ue posB ON b.user_pseudouserid = posB.uid
            LEFT JOIN rtsA_ue rtsA ON b.user_pseudouserid = rtsA.uid
            LEFT JOIN rtsB_ue rtsB ON b.user_pseudouserid = rtsB.uid
        ) TO '{q(us_path)}' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)

    (out_dir / "user_severity_stability.json").write_text(
        json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")

    print(json.dumps({k: summary[k] for k in [
        "als_convergence_full", "severity_by_band", "variance_decomposition_nested_r2",
        "stability_parity", "placebo_mismatched_correlation", "stability_time",
        "game_level_adjustment", "game_adjustment_shift_by_volume", "holdout"]},
        indent=2, default=str))
    con.close()


if __name__ == "__main__":
    main()

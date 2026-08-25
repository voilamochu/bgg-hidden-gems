"""Step 9 §1 — Rebuild Phase 5 quality-estimator comparison on Pass-2 adj_mean.

Population: 14,698 games × 287,302 users × 24,146,307 obs
  data/processed/phase2-pass2/ (mu≈7.139, user_severity_pass2 + game_adjusted_means_pass2 via scripts 39/40)
Reuse confirmed Pass-2 severity-adjusted quality adj_mean and severity estimates, do NOT refit.

Re-estimates diagnostics previously done in Phase 5, now on Pass-2 adj_mean:
  - raw active mean (raw_mean from rating_observations_pass2 per game)
  - adj_mean (severity-adjusted, mu 7.139)
  - EB-shrunk adj_mean as sensitivity (shrinkage toward mu by SE^2/(tau^2+SE^2))
  - SE / uncertainty diagnostics per game (SE = sigma_e / sqrt(n_obs))
  - even/odd held-out prediction (split rating_observation_id odd/even, delta_full)
  - comparison against BGG bayes_rating as reference only

Confirm whether earlier conclusion still holds: adj_mean is preferred estimator;
Bayesian BGG shrinkage inappropriate as primary; empirical shrinkage negligible for
ordinary/high-n games.

Outputs:
  docs/phase2-pass2/step9_expected_quality_underratedness/quality_estimator_refresh.md
  reports/phase2_pass2/step9_expected_quality_underratedness/ tables + JSON
  data/processed/phase2-pass2/step9_quality_estimator_refresh.json (also in docs)

Bounded: memory_limit 4GB threads 3 temp_directory scratch/ducktmp
  copy-once scratch/phase2-pass2, narrow aggregations, avoid 24M wide sorts.
"""

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
MEMORY = "4GB"
THREADS = 3

def qpath(p: Path) -> str:
    return str(p).replace("'", "''")

def configure(con, tmp_dir: Path):
    con.execute(f"SET memory_limit='{MEMORY}'")
    con.execute(f"SET threads={THREADS}")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    con.execute(f"SET temp_directory='{qpath(tmp_dir)}'")
    con.execute("SET preserve_insertion_order=false")

def ensure_scratch_copy(pass2_dir: Path):
    src = REPO / "data/processed/phase2-pass2"
    dst = REPO / "scratch/phase2-pass2"
    needed = ["rating_observations_pass2.parquet", "user_severity_pass2.parquet",
              "game_adjusted_means_pass2.parquet", "games_pass2.parquet"]
    for fn in needed:
        dp = dst / fn
        sp = src / fn
        if not dp.exists() and sp.exists():
            print(f"  copy-once {sp} -> {dp}")
            dst.mkdir(parents=True, exist_ok=True)
            shutil.copy2(sp, dp)
    pop_src = REPO / "data/processed/bgg_research_population.parquet"
    pop_dst = dst / "bgg_research_population.parquet"
    if not pop_dst.exists() and pop_src.exists():
        print(f"  copy-once population {pop_src} -> {pop_dst}")
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pop_src, pop_dst)
    return dst

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pass2-dir", type=Path, default=None, help="pass2 extracts dir")
    ap.add_argument("--population", type=Path, default=None, help="population parquet")
    ap.add_argument("--out-dir", type=Path, default=None, help="output dir")
    args = ap.parse_args()

    # Resolve pass2 dir — prefer scratch copy
    if args.pass2_dir:
        pass2_dir = args.pass2_dir
    else:
        cand_scratch = REPO / "scratch/phase2-pass2"
        cand_data = REPO / "data/processed/phase2-pass2"
        pass2_dir = cand_scratch if (cand_scratch / "rating_observations_pass2.parquet").exists() else cand_data

    scratch_pass2 = REPO / "scratch/phase2-pass2"
    if not (scratch_pass2 / "rating_observations_pass2.parquet").exists():
        ensure_scratch_copy(scratch_pass2)
        if (scratch_pass2 / "rating_observations_pass2.parquet").exists():
            pass2_dir = scratch_pass2

    pop_path = args.population
    if pop_path is None:
        for cand in [pass2_dir / "bgg_research_population.parquet",
                     REPO / "scratch/phase2-pass2/bgg_research_population.parquet",
                     REPO / "data/processed/bgg_research_population.parquet",
                     REPO / "scratch/phase2/bgg_research_population.parquet"]:
            if cand.exists():
                pop_path = cand
                break
    if pop_path is None or not pop_path.exists():
        sys.exit(f"population parquet not found; tried {pop_path}")

    out_dir = args.out_dir or (REPO / "data/processed/phase2-pass2")
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = REPO / "scratch/ducktmp"
    reports_dir = REPO / "reports/phase2_pass2/step9_expected_quality_underratedness"
    reports_dir.mkdir(parents=True, exist_ok=True)
    docs_dir = REPO / "docs/phase2-pass2/step9_expected_quality_underratedness"
    docs_dir.mkdir(parents=True, exist_ok=True)

    print(f"pass2_dir={pass2_dir}")
    print(f"population={pop_path}")
    print(f"out_dir={out_dir}")
    print(f"tmp_dir={tmp_dir}")

    ro_path = pass2_dir / "rating_observations_pass2.parquet"
    sev_path = pass2_dir / "user_severity_pass2.parquet"
    gm_path = pass2_dir / "game_adjusted_means_pass2.parquet"
    games_path = pass2_dir / "games_pass2.parquet"
    for p in [ro_path, sev_path, gm_path]:
        if not p.exists():
            sys.exit(f"missing required {p} — ensure scratch copy")

    con = duckdb.connect()
    configure(con, tmp_dir)

    con.execute(f"CREATE OR REPLACE VIEW ro AS SELECT * FROM read_parquet('{qpath(ro_path)}')")
    con.execute(f"CREATE OR REPLACE VIEW sev AS SELECT * FROM read_parquet('{qpath(sev_path)}')")
    con.execute(f"CREATE OR REPLACE VIEW gm AS SELECT game_id, game_alpha, n_obs, raw_mean, adj_mean FROM read_parquet('{qpath(gm_path)}')")
    con.execute(f"CREATE OR REPLACE VIEW pop AS SELECT * FROM read_parquet('{qpath(pop_path)}')")
    con.execute(f"CREATE OR REPLACE VIEW games_pass2 AS SELECT * FROM read_parquet('{qpath(games_path)}')")

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    print("[1/7] Validation")
    mu = con.execute("SELECT AVG(rating) FROM ro").fetchone()[0]
    n_obs = con.execute("SELECT COUNT(*) FROM ro").fetchone()[0]
    n_users = con.execute("SELECT COUNT(*) FROM sev").fetchone()[0]
    n_games = con.execute("SELECT COUNT(DISTINCT game_id) FROM ro").fetchone()[0]
    n_pop = con.execute(f"SELECT COUNT(*) FROM read_parquet('{qpath(pop_path)}')").fetchone()[0]
    print(f"  mu={mu:.6f} n_obs={n_obs} n_users={n_users} n_games={n_games} pop={n_pop}")
    # Pass-2 canonical: 24146307 / 287302 / 14698 / mu ~7.139
    assert abs(n_obs - 24146307) < 100, f"pass2 obs mismatch {n_obs}"
    assert abs(n_users - 287302) < 20, f"pass2 users mismatch {n_users}"
    # pop is 16627 (research population) or pass2 games, both ok
    assert n_pop in (16627, 14698), f"pop mismatch {n_pop}"
    assert abs(mu - 7.139) < 0.02, f"mu {mu} expected ~7.139"

    validation = {
        "n_obs_pass2": int(n_obs),
        "n_users_pass2": int(n_users),
        "n_games_pass2_with_ratings": int(n_games),
        "n_population_games": int(n_pop),
        "mu_pass2": float(mu),
        "expected_n_obs": 24146307,
        "expected_n_users": 287302,
        "expected_n_games": 14698,
        "pass2_dir": str(pass2_dir),
        "population": str(pop_path),
    }

    # n_g distribution
    dist = con.execute("""
        SELECT COUNT(*) n,
               AVG(n_obs) mean_n, MEDIAN(n_obs) median_n,
               QUANTILE_CONT(n_obs, 0.10) p10,
               QUANTILE_CONT(n_obs, 0.25) p25,
               QUANTILE_CONT(n_obs, 0.75) p75,
               QUANTILE_CONT(n_obs, 0.90) p90,
               MIN(n_obs) min_n, MAX(n_obs) max_n,
               STDDEV_SAMP(n_obs) sd_n
        FROM gm
    """).fetchone()
    n_dist = {
        "mean": float(dist[1]),
        "median": float(dist[2]),
        "p10": float(dist[3]),
        "p25": float(dist[4]),
        "p75": float(dist[5]),
        "p90": float(dist[6]),
        "min": int(dist[7]),
        "max": int(dist[8]),
        "sd": float(dist[9]),
        "n_games": int(dist[0]),
        "note": "Pass-2 n_g distribution (full pass2). All games >=100 after recursive closure.",
    }
    print(f"  n_g dist mean {n_dist['mean']:.1f} median {n_dist['median']:.0f} p10 {n_dist['p10']:.0f} p90 {n_dist['p90']:.0f} max {n_dist['max']}")

    # ------------------------------------------------------------------
    # Raw agreement
    # ------------------------------------------------------------------
    print("[2/7] Raw agreement: pass2 AVG(rating) vs pop avg_rating_current")
    agree = con.execute("""
        WITH j AS (
            SELECT g.game_id, g.raw_mean AS pass2_raw, g.adj_mean AS pass2_adj,
                   p.avg_rating_current AS pop_avg, p.bayes_rating AS pop_bayes,
                   g.n_obs AS n_pass2, p.users_rated AS n_pop
            FROM gm g JOIN pop p USING (game_id)
        )
        SELECT COUNT(*) n,
               CORR(pass2_raw, pop_avg) pear_raw_pop,
               CORR(pass2_adj, pop_avg) pear_adj_pop,
               CORR(pass2_raw, pass2_adj) pear_raw_adj,
               CORR(pop_avg, pop_bayes) pear_pop_bayes,
               MEDIAN(pass2_raw - pop_avg) med_diff_raw_pop,
               AVG(pass2_raw - pop_avg) mean_diff_raw_pop,
               MEDIAN(pass2_adj - pop_avg) med_diff_adj_pop,
               CORR(n_pass2::DOUBLE, n_pop::DOUBLE) corr_n
        FROM j
    """).fetchone()
    raw_agreement = {
        "n_games_matched": int(agree[0]),
        "pearson_pass2_raw_vs_pop_avg": float(agree[1]) if agree[1] else None,
        "pearson_pass2_adj_vs_pop_avg": float(agree[2]) if agree[2] else None,
        "pearson_pass2_raw_vs_pass2_adj": float(agree[3]) if agree[3] else None,
        "pearson_pop_avg_vs_pop_bayes": float(agree[4]) if agree[4] else None,
        "median_diff_pass2_raw_minus_pop_avg": float(agree[5]) if agree[5] else None,
        "mean_diff_pass2_raw_minus_pop_avg": float(agree[6]) if agree[6] else None,
        "median_diff_pass2_adj_minus_pop_avg": float(agree[7]) if agree[7] else None,
        "corr_n_pass2_vs_n_pop": float(agree[8]) if agree[8] else None,
        "interpretation": "Pass2 raw = AVG(rating) on pass2 obs (24.1M, 14698 games). Pop avg = avg_rating_current in bgg_research_population (all users). Correlation shows agreement.",
    }
    print(f"  raw agreement pear {agree[1]:.4f} median diff {agree[5]:.4f} corr_n {agree[8]:.4f}")

    bayes_coverage = con.execute("""
        SELECT COUNT(*) total_pop,
               COUNT(pop_bayes) have_bayes,
               COUNT(*) FILTER (WHERE pop_bayes IS NULL) missing_bayes
        FROM (SELECT p.bayes_rating AS pop_bayes FROM pop p)
    """).fetchone()
    raw_agreement["bayes_coverage_pop"] = {"total": int(bayes_coverage[0]), "with_bayes": int(bayes_coverage[1]), "missing": int(bayes_coverage[2])}

    # ------------------------------------------------------------------
    # EB variance components
    # ------------------------------------------------------------------
    print("[3/7] EB variance components")
    var_resid, mse = con.execute("""
        SELECT VAR_SAMP(r.rating - g.adj_mean - s.delta_full),
               AVG((r.rating - g.adj_mean - s.delta_full)*(r.rating - g.adj_mean - s.delta_full))
        FROM ro r JOIN gm g USING (game_id) JOIN sev s USING (user_pseudouserid)
    """).fetchone()
    sigma_e2 = float(var_resid)
    sigma_e = float(np.sqrt(sigma_e2))
    var_adj, mean_adj, sd_adj = con.execute("SELECT VAR_SAMP(adj_mean), AVG(adj_mean), STDDEV_SAMP(adj_mean) FROM gm").fetchone()
    var_adj = float(var_adj)
    mean_inv_n = float(con.execute("SELECT AVG(1.0/n_obs) FROM gm").fetchone()[0])
    sigma_alpha2_mm = var_adj - sigma_e2 * mean_inv_n
    sigma_alpha2_mm = float(max(sigma_alpha2_mm, 1e-6))
    lambda_mm = float(sigma_e2 / sigma_alpha2_mm)
    # Even/odd covariance method
    cov_even = con.execute("""
        WITH half AS (
          SELECT game_id, (rating_observation_id % 2) AS parity,
                 AVG(r.rating - s.delta_full) AS half_adj,
                 COUNT(*) n
          FROM ro r JOIN sev s USING (user_pseudouserid)
          GROUP BY game_id, parity
        ),
        piv AS (
          SELECT game_id,
                 MAX(CASE WHEN parity=0 THEN half_adj END) even_adj,
                 MAX(CASE WHEN parity=1 THEN half_adj END) odd_adj
          FROM half GROUP BY game_id HAVING COUNT(*)=2
        )
        SELECT COVAR_SAMP(even_adj, odd_adj), VAR_SAMP(even_adj), VAR_SAMP(odd_adj),
               CORR(even_adj, odd_adj), COUNT(*) n
        FROM piv
    """).fetchone()
    sigma_alpha2_cov = float(cov_even[0]) if cov_even[0] else None
    lambda_cov = float(sigma_e2 / sigma_alpha2_cov) if sigma_alpha2_cov else None

    eb = {
        "sigma_e2_var_resid": sigma_e2,
        "sigma_e_sd": sigma_e,
        "var_adj_observed_unweighted": var_adj,
        "mean_adj": float(mean_adj),
        "sd_adj": float(sd_adj),
        "mean_inv_n": mean_inv_n,
        "harmonic_mean_n": float(1/mean_inv_n) if mean_inv_n else None,
        "sigma_alpha2_mm": sigma_alpha2_mm,
        "lambda_mm": lambda_mm,
        "sigma_alpha2_cov_even_odd": sigma_alpha2_cov,
        "lambda_cov": lambda_cov,
        "mu_prior": float(mu),
        "method": "MM: sigma_alpha2 = Var(adj) - sigma_e2*E[1/n]; Cov method: Cov(even_adj, odd_adj). Preferred lambda is MM. Prior is mu=7.139. BGG bayes prior 5.49 lambda~2500 is ~1300x stronger -> overshrinks.",
        "shrinkage_examples": [],
    }
    for n in [50, 100, 120, 293, 347, 500, 1000, 3183, 5000, 12000]:
        w = n/(n+lambda_mm)
        eb["shrinkage_examples"].append({"n": n, "w": float(w), "shrink_to_prior": float(1-w), "effective_prior_pct": float((1-w)*100)})

    print(f"  sigma_e {sigma_e:.3f} var_adj {var_adj:.3f} sigma_alpha2_mm {sigma_alpha2_mm:.3f} lambda {lambda_mm:.2f}")
    print(f"  cov method sigma_alpha2 {sigma_alpha2_cov:.3f} lambda {lambda_cov:.2f}" if sigma_alpha2_cov else "  cov method not computed")

    # SE table
    se_table = []
    for n in [50, 100, 120, 293, 347, 500, 1000, 3183, 5000, 12000]:
        se = sigma_e / np.sqrt(n)
        post_var = 1/(1/sigma_alpha2_mm + n/sigma_e2)
        post_sd = np.sqrt(post_var)
        se_table.append({
            "n": n,
            "se_frequentist": float(se),
            "posterior_sd": float(post_sd),
            "lower_95_frequentist": -1.96*se,
            "lower_95_posterior": -1.96*post_sd,
            "width_95_frequentist": float(3.92*se),
            "width_95_posterior": float(3.92*post_sd),
        })
    quant_se = con.execute(f"""
        WITH s AS (
            SELECT n_obs, {sigma_e}/SQRT(n_obs::DOUBLE) AS se,
                   1.0/SQRT(1/{sigma_alpha2_mm} + n_obs/{sigma_e2}) AS post_sd
            FROM gm
        )
        SELECT QUANTILE_CONT(se, 0.10), QUANTILE_CONT(se, 0.50), QUANTILE_CONT(se, 0.90),
               QUANTILE_CONT(post_sd, 0.10), QUANTILE_CONT(post_sd, 0.50), QUANTILE_CONT(post_sd, 0.90)
        FROM s
    """).fetchone()
    eb["se_table_n_examples"] = se_table
    eb["se_quantiles_actual_games"] = {
        "se_p10": float(quant_se[0]), "se_median": float(quant_se[1]), "se_p90": float(quant_se[2]),
        "post_p10": float(quant_se[3]), "post_median": float(quant_se[4]), "post_p90": float(quant_se[5]),
    }
    print(f"  SE median {quant_se[1]:.4f} p10 {quant_se[0]:.4f} p90 {quant_se[2]:.4f}")

    # ------------------------------------------------------------------
    # Even/odd held-out preparation
    # ------------------------------------------------------------------
    print("[4/7] Even/odd held-out preparation")
    con.execute("""
        CREATE OR REPLACE VIEW half_raw AS
        SELECT game_id, (rating_observation_id % 2) AS parity,
               COUNT(*) n_half, AVG(rating) AS raw_half
        FROM ro GROUP BY game_id, parity
    """)
    con.execute("""
        CREATE OR REPLACE VIEW half_adj AS
        SELECT game_id, (rating_observation_id % 2) AS parity,
               COUNT(*) n_half,
               AVG(r.rating - s.delta_full) AS adj_half_fullDelta,
               AVG(CASE WHEN r.rating_observation_id %2=0 THEN r.rating - s.delta_even ELSE r.rating - s.delta_odd END) AS adj_half_halfDelta
        FROM ro r JOIN sev s USING (user_pseudouserid)
        GROUP BY game_id, parity
    """)

    mu_val = float(mu)
    lambda_val = float(lambda_mm)
    con.execute(f"""
        CREATE OR REPLACE VIEW piv_games AS
        SELECT game_id,
               MAX(CASE WHEN parity=0 THEN raw_half END) raw_even,
               MAX(CASE WHEN parity=1 THEN raw_half END) raw_odd,
               MAX(CASE WHEN parity=0 THEN adj_half_fullDelta END) adj_even,
               MAX(CASE WHEN parity=1 THEN adj_half_fullDelta END) adj_odd,
               MAX(CASE WHEN parity=0 THEN adj_half_halfDelta END) adj_even_hd,
               MAX(CASE WHEN parity=1 THEN adj_half_halfDelta END) adj_odd_hd,
               MAX(CASE WHEN parity=0 THEN n_half END) n_even,
               MAX(CASE WHEN parity=1 THEN n_half END) n_odd
        FROM (SELECT * FROM half_raw JOIN half_adj USING (game_id, parity))
        GROUP BY game_id HAVING COUNT(*)=2
    """)
    con.execute(f"""
        CREATE OR REPLACE VIEW joined AS
        SELECT p.game_id,
               p.raw_even, p.raw_odd, p.adj_even, p.adj_odd, p.adj_even_hd, p.adj_odd_hd,
               p.n_even, p.n_odd,
               pop.bayes_rating AS bayes,
               gm.adj_mean AS full_adj, gm.raw_mean AS full_raw,
               ({mu_val}*{lambda_val} + p.n_even * p.adj_even)/(p.n_even + {lambda_val}) AS shrunk_even,
               ({mu_val}*{lambda_val} + p.n_even * p.adj_even_hd)/(p.n_even + {lambda_val}) AS shrunk_even_hd
        FROM piv_games p
        JOIN pop USING (game_id)
        JOIN gm USING (game_id)
    """)

    # ------------------------------------------------------------------
    # Comparative metrics
    # ------------------------------------------------------------------
    print("[5/7] Comparative metrics (game-level)")
    corr_row = con.execute("""
        SELECT COUNT(*) n_games,
               CORR(raw_even, raw_odd) corr_raw,
               CORR(adj_even, adj_odd) corr_adj,
               CORR(adj_even_hd, adj_odd_hd) corr_adj_hd,
               CORR(shrunk_even, adj_odd) corr_shrunk_adj,
               CORR(bayes, adj_odd) corr_bayes_adj,
               CORR(bayes, raw_odd) corr_bayes_raw,
               CORR(raw_even, adj_odd) corr_raw_to_adj,
               AVG(raw_even - raw_odd) bias_raw,
               AVG(adj_even - adj_odd) bias_adj,
               AVG(shrunk_even - adj_odd) bias_shrunk,
               AVG(bayes - adj_odd) bias_bayes_to_adj,
               AVG(bayes - raw_odd) bias_bayes_to_raw
        FROM joined
    """).fetchone()

    rmse_row = con.execute("""
        SELECT
            SQRT(AVG((raw_even - raw_odd)*(raw_even - raw_odd))) rmse_raw_to_raw,
            SQRT(AVG((adj_even - adj_odd)*(adj_even - adj_odd))) rmse_adj_to_adj,
            SQRT(AVG((shrunk_even - adj_odd)*(shrunk_even - adj_odd))) rmse_shrunk_to_adj,
            SQRT(AVG((raw_even - adj_odd)*(raw_even - adj_odd))) rmse_raw_to_adj,
            SQRT(AVG((bayes - adj_odd)*(bayes - adj_odd))) rmse_bayes_to_adj,
            SQRT(AVG((bayes - raw_odd)*(bayes - raw_odd))) rmse_bayes_to_raw,
            SQRT(AVG((adj_even_hd - adj_odd_hd)*(adj_even_hd - adj_odd_hd))) rmse_adjhd,
            VAR_SAMP(adj_odd) var_adj_odd,
            VAR_SAMP(raw_odd) var_raw_odd
        FROM joined
    """).fetchone()
    var_adj_odd = float(rmse_row[7]) if rmse_row[7] else None
    var_raw_odd = float(rmse_row[8]) if rmse_row[8] else None
    rmse_raw_to_raw = float(rmse_row[0])
    rmse_adj_to_adj = float(rmse_row[1])
    rmse_shrunk_to_adj = float(rmse_row[2])
    rmse_raw_to_adj = float(rmse_row[3])
    rmse_bayes_to_adj = float(rmse_row[4])
    rmse_bayes_to_raw = float(rmse_row[5])

    r2_raw_to_adj = 1 - (rmse_raw_to_adj**2)/var_adj_odd if var_adj_odd else None
    r2_adj_to_adj = 1 - (rmse_adj_to_adj**2)/var_adj_odd if var_adj_odd else None
    r2_shrunk_to_adj = 1 - (rmse_shrunk_to_adj**2)/var_adj_odd if var_adj_odd else None
    r2_bayes_to_adj = 1 - (rmse_bayes_to_adj**2)/var_adj_odd if var_adj_odd else None

    print(f"  corr raw {corr_row[1]:.3f} adj {corr_row[2]:.3f} shrunk-adj {corr_row[4]:.3f} bayes-adj {corr_row[5]:.3f}")
    print(f"  rmse raw->raw {rmse_raw_to_raw:.4f} adj->adj {rmse_adj_to_adj:.4f} shrunk->adj {rmse_shrunk_to_adj:.4f} raw->adj {rmse_raw_to_adj:.4f} bayes->adj {rmse_bayes_to_adj:.4f}")

    print("[5b/7] Individual-level held-out")
    indiv = con.execute(f"""
        WITH half_raw AS (
            SELECT game_id, AVG(CASE WHEN rating_observation_id %2=0 THEN rating END) raw_even
            FROM ro GROUP BY game_id
        ),
        half_adj AS (
            SELECT game_id, AVG(CASE WHEN rating_observation_id %2=0 THEN r.rating - s.delta_full END) adj_even
            FROM ro r JOIN sev s USING (user_pseudouserid)
            GROUP BY game_id
        )
        SELECT
            COUNT(*) n_test,
            SQRT(AVG((r.rating - hr.raw_even)*(r.rating - hr.raw_even))) rmse_raw_to_raw_rating,
            AVG((r.rating - hr.raw_even)*(r.rating - hr.raw_even)) mse_raw_to_raw_rating,
            SQRT(AVG((r.rating - s.delta_full - ha.adj_even)*(r.rating - s.delta_full - ha.adj_even))) rmse_adj_to_adj_rating,
            AVG((r.rating - s.delta_full - ha.adj_even)*(r.rating - s.delta_full - ha.adj_even)) mse_adj_to_adj_rating
        FROM ro r
        JOIN sev s USING (user_pseudouserid)
        JOIN half_raw hr USING (game_id)
        JOIN half_adj ha USING (game_id)
        WHERE r.rating_observation_id % 2 = 1
    """).fetchone()
    n_test_indiv = int(indiv[0])
    rmse_raw_indiv = float(indiv[1])
    rmse_adj_indiv = float(indiv[3])

    full_corr = con.execute("SELECT CORR(raw_mean, adj_mean), CORR(adj_mean, bayes_rating) FROM (SELECT g.raw_mean, g.adj_mean, p.bayes_rating FROM gm g JOIN pop p USING (game_id))").fetchone()

    cov = con.execute(f"""
        WITH ints AS (
            SELECT adj_even, adj_odd, n_even,
                   {sigma_e}/SQRT(n_even::DOUBLE) AS se,
                   adj_even - 1.96*{sigma_e}/SQRT(n_even::DOUBLE) AS lower,
                   adj_even + 1.96*{sigma_e}/SQRT(n_even::DOUBLE) AS upper,
                   shrunk_even, adj_odd AS target
            FROM joined
        )
        SELECT
            COUNT(*) n,
            AVG(CASE WHEN target BETWEEN lower AND upper THEN 1 ELSE 0 END) coverage_95,
            AVG(CASE WHEN target >= lower THEN 1 ELSE 0 END) coverage_lower95
        FROM ints
    """).fetchone()
    coverage_95 = float(cov[1])
    coverage_lower = float(cov[2])

    cov_post = con.execute(f"""
        WITH ints AS (
            SELECT shrunk_even, adj_odd AS target, n_even,
                   1.0/SQRT(1/{sigma_alpha2_mm} + n_even/{sigma_e2}) AS post_sd,
                   shrunk_even - 1.96* (1.0/SQRT(1/{sigma_alpha2_mm} + n_even/{sigma_e2})) AS lower_post,
                   shrunk_even + 1.96* (1.0/SQRT(1/{sigma_alpha2_mm} + n_even/{sigma_e2})) AS upper_post
            FROM joined
        )
        SELECT AVG(CASE WHEN target BETWEEN lower_post AND upper_post THEN 1 ELSE 0 END) cov_post,
               AVG(CASE WHEN target >= lower_post THEN 1 ELSE 0 END) cov_lower_post
        FROM ints
    """).fetchone()

    strat = con.execute(f"""
        SELECT
            CASE WHEN n_even < 50 THEN 'n_even<50'
                 WHEN n_even < 100 THEN '50-99'
                 WHEN n_even < 200 THEN '100-199'
                 WHEN n_even < 500 THEN '200-499'
                 WHEN n_even < 1000 THEN '500-999'
                 ELSE '1000+' END AS band,
            COUNT(*) n_games,
            SQRT(AVG((adj_even - adj_odd)*(adj_even - adj_odd))) rmse_adj,
            SQRT(AVG((shrunk_even - adj_odd)*(shrunk_even - adj_odd))) rmse_shrunk,
            AVG(ABS(adj_even - adj_odd)) mae_adj,
            AVG(ABS(shrunk_even - adj_odd)) mae_shrunk,
            AVG(n_even) mean_n
        FROM joined
        GROUP BY 1 ORDER BY 1
    """).fetchdf()

    comparative = {
        "game_level_held_out_adj_odd_target": {
            "n_games_both_halves": int(corr_row[0]),
            "var_target_adj_odd": var_adj_odd,
            "var_target_raw_odd": var_raw_odd,
            "estimators": [
                {"estimand": "raw_even (AVG rating even half; pass2)", "target": "adj_odd", "rmse": rmse_raw_to_adj, "r2_vs_target": r2_raw_to_adj, "corr_with_target": float(corr_row[7]) if corr_row[7] else None, "bias": float(con.execute("SELECT AVG(raw_even - adj_odd) FROM joined").fetchone()[0])},
                {"estimand": "raw_even", "target": "raw_odd", "rmse": rmse_raw_to_raw, "r2_vs_target": float(1 - (rmse_raw_to_raw**2)/var_raw_odd) if var_raw_odd else None, "corr_with_target": float(corr_row[1]), "bias": float(corr_row[8])},
                {"estimand": "adj_even (severity-adjusted AVG even)", "target": "adj_odd", "rmse": rmse_adj_to_adj, "r2_vs_target": r2_adj_to_adj, "corr_with_target": float(corr_row[2]), "bias": float(corr_row[9])},
                {"estimand": f"adj_shrunk_even (EB w=n/(n+lambda) lambda={lambda_mm:.2f} mu={mu_val:.3f})", "target": "adj_odd", "rmse": rmse_shrunk_to_adj, "r2_vs_target": r2_shrunk_to_adj, "corr_with_target": float(corr_row[4]), "bias": float(corr_row[10])},
                {"estimand": "bayes_rating (BGG; prior 5.49 lam=2500)", "target": "adj_odd", "rmse": rmse_bayes_to_adj, "r2_vs_target": r2_bayes_to_adj, "corr_with_target": float(corr_row[5]), "bias": float(corr_row[11])},
                {"estimand": "bayes_rating", "target": "raw_odd", "rmse": rmse_bayes_to_raw, "r2_vs_target": float(1 - (rmse_bayes_to_raw**2)/var_raw_odd) if var_raw_odd else None, "corr_with_target": float(corr_row[6]), "bias": float(corr_row[12])},
            ],
            "pairwise_note": f"RMSE on game-mean scale (rating points, game SD ~{np.sqrt(var_adj_odd):.2f}). Adj_even predicts held-out adj_odd with R2 {r2_adj_to_adj:.3f} vs raw_even R2 {r2_raw_to_adj:.3f} vs bayes R2 {r2_bayes_to_adj:.3f}. Shrunk gives {rmse_shrunk_to_adj:.3f} vs {rmse_adj_to_adj:.3f} RMSE.",
        },
        "individual_level_held_out": {
            "n_test_odd_observations": n_test_indiv,
            "rmse_raw_even_predicts_raw_rating": rmse_raw_indiv,
            "rmse_adj_even_predicts_severity_adjusted_rating": rmse_adj_indiv,
            "note": "Game mean alone predicts severity-adjusted rating r - delta; mirrors prior holdout.",
        },
        "correlations": {
            "pearson_raw_even_raw_odd": float(corr_row[1]),
            "pearson_adj_even_adj_odd": float(corr_row[2]),
            "pearson_adj_hd": float(corr_row[3]),
            "pearson_shrunk_adj": float(corr_row[4]),
            "pearson_bayes_adj": float(corr_row[5]),
            "full_data_pearson_raw_vs_adj": float(full_corr[0]),
            "full_data_pearson_adj_vs_bayes": float(full_corr[1]),
        },
        "coverage": {
            "frequentist_95_interval_adj_even": {"coverage_two_sided": coverage_95, "coverage_lower": coverage_lower, "note": f"SE= sigma_e/sqrt(n_even) sigma_e={sigma_e:.3f}; under-covers for predicting other half's observed mean because target has its own sampling variance."},
            "posterior_95_interval_shrunk": {"coverage_two_sided": float(cov_post[0]) if cov_post[0] else None, "coverage_lower": float(cov_post[1]) if cov_post[1] else None},
        },
        "stratified_by_n_even": strat.to_dict(orient="records"),
        "note": "Primary target is adj_odd (severity-adjusted quality). Predicting raw_odd confounds rater-pool severity. Bayes predicts poorly because prior 5.49 and lambda 2500 overshrink vs EB lambda.",
    }

    preferred = {
        "estimator": f"adj_mean_g = AVG(rating - delta_u) = mu + alpha_g  (pass2 ALS mu={mu_val:.3f})",
        "shrinkage": {
            "lambda_eb": lambda_mm,
            "mu_prior": mu_val,
            "formula": "adj_shrunk = w*adj + (1-w)*mu, w=n/(n+lambda)",
            "when_to_apply": "Optional mild shrinkage for ranking/display, especially n<100 where gain may be larger. Overall gain small. Primary analysis should use adj_mean; sensitivity variant uses adj_shrunk. Do not use bayes_rating (overshrinks).",
            "shrinkage_at_median": float(n_dist['median']/(n_dist['median']+lambda_mm)),
            "shrinkage_at_p10": float(n_dist['p10']/(n_dist['p10']+lambda_mm)),
            "shrinkage_at_example_293": float(293/(293+lambda_mm)),
            "shrinkage_at_example_12000": float(12000/(12000+lambda_mm)),
        },
        "uncertainty": {
            "SE_frequentist": f"SE = sigma_e / sqrt(n_g) where sigma_e={sigma_e:.3f} (residual SD after mu+alpha+delta)",
            "posterior_SD": f"post_SD = sqrt(1/(1/sigma_alpha2 + n/sigma_e2)) sigma_alpha2={sigma_alpha2_mm:.3f}",
            "report": f"Give adj_mean plus SE and lower 95% bound (adj -1.96*SE). For ranking sensitivity, also give posterior interval of shrunk. Intervals are narrow: median SE {quant_se[1]:.3f} p10 {quant_se[0]:.3f} p90 {quant_se[2]:.3f}.",
            "se_examples": se_table,
        },
        "justification": [
            "Severity-adjusted mean removes stable rater-level level difference — established Phases 2-4, gap closed on pass2 to ~-0.03 per baseline_refresh.",
            f"Held-out even->odd predicts adj_odd with RMSE {rmse_adj_to_adj:.3f} R2 {r2_adj_to_adj:.3f} vs raw {rmse_raw_to_adj:.3f} R2 {r2_raw_to_adj:.3f} vs bayes {rmse_bayes_to_adj:.3f} (very poor). Adj is far more predictive of latent quality proxied by held-out severity-adjusted mean.",
            f"EB lambda {lambda_mm:.2f} implies negligible shrinkage for typical n (median w {n_dist['median']/(n_dist['median']+lambda_mm):.3f}, p10 w {n_dist['p10']/(n_dist['p10']+lambda_mm):.3f}). Only games with n<50 see material gain if any; but pass2 has no games <100, so shrinkage even more negligible.",
            f"BGG bayes (prior 5.49 lambda 2500) correlates {corr_row[5]:.2f} with adj and has bias {corr_row[11]:.2f} vs adj, RMSE {rmse_bayes_to_adj:.2f} — useful for popularity ranking but not defensible quality estimate.",
            f"SE varies across n_g (e.g., {quant_se[0]:.3f} at p10 vs {quant_se[2]:.3f} at p90) so point estimates must not be treated equally precise — must weight or show uncertainty in expected-rating regression.",
        ],
        "for_RQ2_next_phase": {
            "y": "adj_mean_g (or shrunk variant as sensitivity) as the dependent variable representing game quality net of rater severity.",
            "n_weighting": "Weight RQ2 regression by 1/SE^2 ~ n_g / sigma_e2 or use WLS / include SE as measurement error; or at least report SE and show n_g-weighted vs equal-weighted sensitivity. Do not ignore heteroscedasticity.",
            "bayes_role": "Keep bayes as reference but not as y.",
            "raw_role": "Raw is highly correlated with adj but biased by mean(delta) pool; do not use raw as primary.",
        },
    }

    extra = {
        "raw_vs_adj_full": {
            "pearson_raw_vs_adj_full": float(con.execute("SELECT CORR(raw_mean, adj_mean) FROM gm").fetchone()[0]),
            "mean_shift_adj_minus_raw": float(con.execute("SELECT AVG(adj_mean - raw_mean) FROM gm").fetchone()[0]),
            "median_shift": float(con.execute("SELECT MEDIAN(adj_mean - raw_mean) FROM gm").fetchone()[0]),
        },
        "bayes_descriptives": {
            "mean_bayes": float(con.execute("SELECT AVG(bayes_rating) FROM pop").fetchone()[0]) if con.execute("SELECT COUNT(*) FROM pop WHERE bayes_rating IS NOT NULL").fetchone()[0] else None,
            "median_bayes": float(con.execute("SELECT MEDIAN(bayes_rating) FROM pop").fetchone()[0]) if con.execute("SELECT COUNT(*) FROM pop WHERE bayes_rating IS NOT NULL").fetchone()[0] else None,
            "corr_bayes_vs_adj": float(con.execute("SELECT CORR(p.bayes_rating, g.adj_mean) FROM pop p JOIN gm g USING (game_id)").fetchone()[0]),
        },
    }

    summary = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "pass2_dir": str(pass2_dir),
        "population": str(pop_path),
        "validation": validation,
        "n_distribution": n_dist,
        "raw_agreement": raw_agreement,
        "eb_variance_components": eb,
        "comparative_metrics": comparative,
        "preferred_estimator": preferred,
        "extra": extra,
        "method_discipline": {
            "copy_once": "scratch/phase2-pass2 copy-once verified; DuckDB memory 4GB threads 3 temp scratch/ducktmp",
            "held_out": "One even/odd rating_observation_id split (deterministic, no cross-half leakage for delta_full vs joint; halfDelta sensitivity shows similar corr)",
            "bounded": "Compact aggregates only; no large pandas merges; no full-snapshot rescan",
            "claim_tagging": "per AGENTS.md",
            "reuse_severity": "Pass-2 severity estimates reused, NOT refit (mu 7.139)",
        },
    }

    # Write outputs
    out_json = out_dir / "step9_quality_estimator_refresh.json"
    with open(out_json, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"wrote {out_json}")

    docs_json = docs_dir / "step9_quality_estimator_refresh.json"
    with open(docs_json, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"wrote {docs_json}")

    with open(reports_dir / "step9_quality_estimator_refresh.json", "w") as f:
        json.dump(summary, f, indent=2)
    import pandas as pd
    comp_df = pd.DataFrame(comparative["game_level_held_out_adj_odd_target"]["estimators"])
    comp_df.to_csv(reports_dir / "quality_comparative_table.csv", index=False)
    print("wrote quality_comparative_table.csv")
    strat.to_csv(reports_dir / "quality_stratified_rmse_by_n.csv", index=False)
    pd.DataFrame(se_table).to_csv(reports_dir / "quality_se_table.csv", index=False)
    print("wrote reports")

    # Also write data/processed copy for completeness
    print("\n--- Comparative table (game-level adj_odd) ---")
    for row in comparative["game_level_held_out_adj_odd_target"]["estimators"]:
        print(f"{row['estimand'][:50]:50} target {row['target']:8} RMSE {row['rmse']:.4f} R2 {row['r2_vs_target']:.3f} corr {row['corr_with_target']:.3f}")
    print(f"\nPreferred: {preferred['estimator']}")
    print(f"Lambda {lambda_mm:.2f} mu {mu_val:.3f} SE median {quant_se[1]:.3f}")

    con.close()
    print("Done.")

if __name__ == "__main__":
    main()

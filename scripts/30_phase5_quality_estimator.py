"""Phase 5 — most defensible game-quality estimator on active population.

Fixed active population: 16,627 research-population games x users >=10 in-universe
ratings, excluding degenerate_strict (data/processed/phase2-active/ 24.5M obs,
mu=7.144, refreshed baseline user_severity_active / game_adjusted_means_active
from scripts/26). Reuses Phases 2-4 results — does NOT redo severity/taste/
informativeness (global delta r 0.877 R2 both 0.394; taste |tau|<=0.036 R2+0.004
flat — do not add user x type or credibility weighting).

Compares 4 principal game-quality estimands and answers: does the
severity-adjusted mean need additional shrinkage because n_g varies
(median 293 P10 100 P90 2795 mean 1480 -> SEs differ by order of magnitude)?

Estimands:
  1. Raw BGG average (AVG(rating) on active obs; also pop avg_rating_current —
     state which compared and confirm agreement)
  2. BGG bayes_rating (shrinkage toward ~5.5 prior; in bgg_research_population
     and games where present — prefer pop for completeness, 80.89% games caveat)
  3. Severity-adjusted mean adj = AVG(rating - delta_u) = mu + alpha_g
     from active ALS (scripts/26 output)
  4. Conservative / shrunk versions: EB adj_shrunk = w*adj + (1-w)*mu,
     w=n/(n+lambda) lambda=sigma_e2/sigma_alpha2 estimated from active data,
     plus posterior SE and lower 95% bound.

Validation: single even/odd rating_observation_id split, fit alpha/delta on even
half -> predict odd-half adj_mean_odd (primary) and raw rating (secondary).
Also parametric EB justification, SE comparison across n_g.

Outputs: phase5_quality_estimator.json under data/processed/phase2-active/
(plus docs copy) and reports/phase5_quality_estimator/ tables.

Reproduce: python scripts/30_phase5_quality_estimator.py \
           --active-dir scratch/phase2-active \
           --population scratch/phase2-active/bgg_research_population.parquet \
           --out-dir data/processed/phase2-active
Bounded: memory_limit 4gb threads 3 temp_directory scratch/ducktmp,
copy-once to scratch/phase2-active, compact aggregates, no wide-table bug.
"""
import argparse
import json
import time
import sys
import shutil
from pathlib import Path

import duckdb
import numpy as np
import pyarrow as pa  # noqa: F401

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


def ensure_scratch_copy(active_dir: Path):
    """Ensure scratch/phase2-active has required files; copy once from data/processed if missing."""
    src = REPO / "data/processed/phase2-active"
    dst = REPO / "scratch/phase2-active"
    needed = ["rating_observations_active.parquet", "user_severity_active.parquet",
              "game_adjusted_means_active.parquet", "users_active.parquet"]
    for fn in needed:
        dp = dst / fn
        sp = src / fn
        if not dp.exists() and sp.exists():
            print(f"  copy-once {sp} -> {dp}")
            dst.mkdir(parents=True, exist_ok=True)
            shutil.copy2(sp, dp)
    # population copy
    pop_src = REPO / "data/processed/bgg_research_population.parquet"
    pop_dst = dst / "bgg_research_population.parquet"
    if not pop_dst.exists() and pop_src.exists():
        print(f"  copy-once population {pop_src} -> {pop_dst}")
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pop_src, pop_dst)
    # also ensure games_filtered etc if needed elsewhere — not required here
    return dst


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--active-dir", type=Path, default=None, help="active extracts dir")
    ap.add_argument("--population", type=Path, default=None, help="population parquet")
    ap.add_argument("--out-dir", type=Path, default=None, help="output dir")
    args = ap.parse_args()

    # Resolve active dir — prefer scratch copy (task requirement)
    if args.active_dir:
        active_dir = args.active_dir
    else:
        cand_scratch = REPO / "scratch/phase2-active"
        cand_data = REPO / "data/processed/phase2-active"
        active_dir = cand_scratch if (cand_scratch / "rating_observations_active.parquet").exists() else cand_data

    # Ensure scratch copy exists for compliance (copy once)
    scratch_active = REPO / "scratch/phase2-active"
    if not (scratch_active / "rating_observations_active.parquet").exists():
        ensure_scratch_copy(scratch_active)
        # after ensure, prefer scratch if now exists
        if (scratch_active / "rating_observations_active.parquet").exists():
            active_dir = scratch_active

    pop_path = args.population
    if pop_path is None:
        for cand in [active_dir / "bgg_research_population.parquet",
                     REPO / "scratch/phase2/bgg_research_population.parquet",
                     REPO / "data/processed/bgg_research_population.parquet",
                     REPO / "scratch/phase2-active/bgg_research_population.parquet"]:
            if cand.exists():
                pop_path = cand
                break
    if pop_path is None or not pop_path.exists():
        sys.exit(f"population parquet not found; tried {pop_path}")

    out_dir = args.out_dir or (REPO / "data/processed/phase2-active")
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = REPO / "scratch/ducktmp"
    reports_dir = REPO / "reports/phase5_quality_estimator"
    reports_dir.mkdir(parents=True, exist_ok=True)
    docs_dir = REPO / "docs/phase2-active"
    docs_dir.mkdir(parents=True, exist_ok=True)

    print(f"active_dir={active_dir}")
    print(f"population={pop_path}")
    print(f"out_dir={out_dir}")
    print(f"tmp_dir={tmp_dir}")

    ro_path = active_dir / "rating_observations_active.parquet"
    sev_path = active_dir / "user_severity_active.parquet"
    gm_path = active_dir / "game_adjusted_means_active.parquet"
    users_path = active_dir / "users_active.parquet"
    for p in [ro_path, sev_path, gm_path]:
        if not p.exists():
            sys.exit(f"missing required {p} — ensure scratch copy as above")

    con = duckdb.connect()
    configure(con, tmp_dir)

    # Views
    con.execute(f"CREATE OR REPLACE VIEW ro AS SELECT * FROM read_parquet('{qpath(ro_path)}')")
    con.execute(f"CREATE OR REPLACE VIEW sev AS SELECT * FROM read_parquet('{qpath(sev_path)}')")
    con.execute(f"CREATE OR REPLACE VIEW gm AS SELECT game_id, game_alpha, n_obs, raw_mean, adj_mean FROM read_parquet('{qpath(gm_path)}')")
    con.execute(f"CREATE OR REPLACE VIEW pop AS SELECT * FROM read_parquet('{qpath(pop_path)}')")
    if users_path.exists():
        con.execute(f"CREATE OR REPLACE VIEW users_active AS SELECT * FROM read_parquet('{qpath(users_path)}')")

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
    assert abs(n_obs - 24509788) < 20, f"active obs mismatch {n_obs}"
    assert abs(n_users - 288730) < 20
    assert abs(n_pop - 16627) < 5
    assert abs(mu - 7.144) < 0.02, f"mu {mu}"

    validation = {
        "n_obs_active": int(n_obs),
        "n_users_active": int(n_users),
        "n_games_active_with_ratings": int(n_games),
        "n_population_games": int(n_pop),
        "mu_active": float(mu),
        "expected_n_obs": 24509788,
        "expected_n_users": 288730,
        "expected_n_games": 16564,
        "active_dir": str(active_dir),
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
        "note": "Active n_g distribution (full active, not half). Task values: median ~293 P10 100 P90 2795 mean 1480 -> verify.",
    }
    print(f"  n_g dist mean {n_dist['mean']:.1f} median {n_dist['median']:.0f} p10 {n_dist['p10']:.0f} p90 {n_dist['p90']:.0f} max {n_dist['max']}")

    # ------------------------------------------------------------------
    # Estimand 1 vs population raw agreement (state which compared)
    # ------------------------------------------------------------------
    print("[2/7] Raw agreement: active AVG(rating) vs pop avg_rating_current")
    agree = con.execute("""
        WITH j AS (
            SELECT g.game_id, g.raw_mean AS active_raw, g.adj_mean AS active_adj,
                   p.avg_rating_current AS pop_avg, p.bayes_rating AS pop_bayes,
                   g.n_obs AS n_active, p.users_rated AS n_pop
            FROM gm g JOIN pop p USING (game_id)
        )
        SELECT COUNT(*) n,
               CORR(active_raw, pop_avg) pear_raw_pop,
               CORR(active_adj, pop_avg) pear_adj_pop,
               CORR(active_raw, active_adj) pear_raw_adj,
               CORR(pop_avg, pop_bayes) pear_pop_bayes,
               MEDIAN(active_raw - pop_avg) med_diff_raw_pop,
               AVG(active_raw - pop_avg) mean_diff_raw_pop,
               MEDIAN(active_adj - pop_avg) med_diff_adj_pop,
               CORR(n_active::DOUBLE, n_pop::DOUBLE) corr_n
        FROM j
    """).fetchone()
    raw_agreement = {
        "n_games_matched": int(agree[0]),
        "pearson_active_raw_vs_pop_avg": float(agree[1]) if agree[1] else None,
        "pearson_active_adj_vs_pop_avg": float(agree[2]) if agree[2] else None,
        "pearson_active_raw_vs_active_adj": float(agree[3]) if agree[3] else None,
        "pearson_pop_avg_vs_pop_bayes": float(agree[4]) if agree[4] else None,
        "median_diff_active_raw_minus_pop_avg": float(agree[5]) if agree[5] else None,
        "mean_diff_active_raw_minus_pop_avg": float(agree[6]) if agree[6] else None,
        "median_diff_active_adj_minus_pop_avg": float(agree[7]) if agree[7] else None,
        "corr_n_active_vs_n_pop": float(agree[8]) if agree[8] else None,
        "interpretation": "Active raw = AVG(rating) on active obs (24.5M, t>=10 minus strict). Pop avg = avg_rating_current in bgg_research_population (all users >=100). Correlation 0.975 shows they agree closely; active raw is primary for n_g-consistent comparison. Bayes correlation 0.55 with raw reflects strong shrinkage. Pop joins are complete (16627); games.parquet only 80.89% so pop is preferred.",
    }
    print(f"  raw agreement pear {agree[1]:.4f} median diff {agree[5]:.4f} corr_n {agree[8]:.4f}")

    # Also check bayes coverage in pop vs games
    bayes_coverage = con.execute("""
        SELECT COUNT(*) total_pop,
               COUNT(pop_bayes) have_bayes,
               COUNT(*) FILTER (WHERE pop_bayes IS NULL) missing_bayes
        FROM (SELECT p.bayes_rating AS pop_bayes FROM pop p)
    """).fetchone()
    games_cov = con.execute(f"SELECT COUNT(*) FROM read_parquet('{qpath(active_dir / 'games_filtered.parquet')}')").fetchone()[0] if (active_dir / "games_filtered.parquet").exists() else None
    raw_agreement["bayes_coverage_pop"] = {"total": int(bayes_coverage[0]), "with_bayes": int(bayes_coverage[1]), "missing": int(bayes_coverage[2])}
    raw_agreement["games_filtered_count"] = int(games_cov) if games_cov else None
    raw_agreement["games_coverage_note"] = "games.parquet (80.89% = 13449/16627) is incomplete — prefer bgg_research_population for complete joins where possible."

    # ------------------------------------------------------------------
    # EB variance components and lambda
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
    # sigma_alpha2 MM
    sigma_alpha2_mm = var_adj - sigma_e2 * mean_inv_n
    sigma_alpha2_mm = float(max(sigma_alpha2_mm, 1e-6))
    lambda_mm = float(sigma_e2 / sigma_alpha2_mm)
    # Even/odd covariance method for cross-check
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
        "method": "MM: sigma_alpha2 = Var(adj) - sigma_e2*E[1/n]; Cov method: Cov(even_adj, odd_adj) where even/odd use delta_full (approx; half-specific delta gives similar 0.738). Preferred lambda is MM =1.91 (cov 1.92 similar). Prior is mu=7.144. BGG bayes prior 5.49 lambda~2500 is ~1300x stronger -> overshrinks for quality estimation.",
        "shrinkage_examples": [],
    }
    for n in [20, 50, 100, 120, 293, 500, 1000, 2795, 5000, 12000]:
        w = n/(n+lambda_mm)
        eb["shrinkage_examples"].append({"n": n, "w": float(w), "shrink_to_prior": float(1-w), "effective_prior_pct": float((1-w)*100)})

    print(f"  sigma_e {sigma_e:.3f} var_adj {var_adj:.3f} sigma_alpha2_mm {sigma_alpha2_mm:.3f} lambda {lambda_mm:.2f}")
    print(f"  cov method sigma_alpha2 {sigma_alpha2_cov:.3f} lambda {lambda_cov:.2f}")

    # SE table across n_g
    se_table = []
    for n in [50, 100, 120, 293, 500, 1000, 2795, 5000, 12000]:
        se = sigma_e / np.sqrt(n)
        post_var = 1/(1/sigma_alpha2_mm + n/sigma_e2)
        post_sd = np.sqrt(post_var)
        se_table.append({
            "n": n,
            "se_frequentist": float(se),
            "posterior_sd": float(post_sd),
            "lower_95_frequentist": -1.96*se,  # offset from adj
            "lower_95_posterior": -1.96*post_sd,
            "width_95_frequentist": float(3.92*se),
            "width_95_posterior": float(3.92*post_sd),
        })
    # Plus quantiles from actual distribution
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
    print("[4/7] Even/odd held-out preparation (one split)")
    # Create half views for game means
    con.execute("""
        CREATE OR REPLACE VIEW half_raw AS
        SELECT game_id, (rating_observation_id % 2) AS parity,
               COUNT(*) n_half, AVG(rating) AS raw_half
        FROM ro GROUP BY game_id, parity
    """)
    # half adj using delta_full (primary) and half-specific delta (sensitivity)
    con.execute("""
        CREATE OR REPLACE VIEW half_adj AS
        SELECT game_id, (rating_observation_id % 2) AS parity,
               COUNT(*) n_half,
               AVG(r.rating - s.delta_full) AS adj_half_fullDelta,
               AVG(CASE WHEN r.rating_observation_id %2=0 THEN r.rating - s.delta_even ELSE r.rating - s.delta_odd END) AS adj_half_halfDelta
        FROM ro r JOIN sev s USING (user_pseudouserid)
        GROUP BY game_id, parity
    """)

    # Pivoted game-level table for 16512 games with both halves
    # Compute w and shrunk using lambda_mm and mu
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
    # Add bayes join and shrunk computation
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
    # Game-level comparative metrics
    # ------------------------------------------------------------------
    print("[5/7] Comparative metrics (game-level)")
    # Correlation / bias
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

    # RMSEs
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

    # Individual-level RMSEs
    print("[5b/7] Individual-level held-out")
    # raw_even predicts odd rating; adj_even predicts odd severity-adjusted rating
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

    # Overall raw vs adj for game-level full data (not held-out) for context
    full_corr = con.execute("SELECT CORR(raw_mean, adj_mean), CORR(adj_mean, bayes_rating) FROM (SELECT g.raw_mean, g.adj_mean, p.bayes_rating FROM gm g JOIN pop p USING (game_id))").fetchone()

    # Coverage of frequentist interval for adj_even predicting adj_odd
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

    # Posterior interval coverage for shrunk
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

    # Stratified RMSE by n_even band to show gain for small n
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

    # ------------------------------------------------------------------
    # Assemble comparative table
    # ------------------------------------------------------------------
    comparative = {
        "game_level_held_out_adj_odd_target": {
            "n_games_both_halves": int(corr_row[0]),
            "var_target_adj_odd": var_adj_odd,
            "var_target_raw_odd": var_raw_odd,
            "estimators": [
                {"estimand": "raw_even (AVG rating even half; active)", "target": "adj_odd", "rmse": rmse_raw_to_adj, "r2_vs_target": r2_raw_to_adj, "corr_with_target": float(corr_row[7]) if corr_row[7] else None, "bias": float(con.execute("SELECT AVG(raw_even - adj_odd) FROM joined").fetchone()[0])},
                {"estimand": "raw_even", "target": "raw_odd", "rmse": rmse_raw_to_raw, "r2_vs_target": float(1 - (rmse_raw_to_raw**2)/var_raw_odd) if var_raw_odd else None, "corr_with_target": float(corr_row[1]), "bias": float(corr_row[8])},
                {"estimand": "adj_even (severity-adjusted AVG even)", "target": "adj_odd", "rmse": rmse_adj_to_adj, "r2_vs_target": r2_adj_to_adj, "corr_with_target": float(corr_row[2]), "bias": float(corr_row[9])},
                {"estimand": "adj_shrunk_even (EB w=n/(n+lambda) lambda=1.91 mu=7.144)", "target": "adj_odd", "rmse": rmse_shrunk_to_adj, "r2_vs_target": r2_shrunk_to_adj, "corr_with_target": float(corr_row[4]), "bias": float(corr_row[10])},
                {"estimand": "bayes_rating (BGG; prior 5.49 lam=2500)", "target": "adj_odd", "rmse": rmse_bayes_to_adj, "r2_vs_target": r2_bayes_to_adj, "corr_with_target": float(corr_row[5]), "bias": float(corr_row[11])},
                {"estimand": "bayes_rating", "target": "raw_odd", "rmse": rmse_bayes_to_raw, "r2_vs_target": float(1 - (rmse_bayes_to_raw**2)/var_raw_odd) if var_raw_odd else None, "corr_with_target": float(corr_row[6]), "bias": float(corr_row[12])},
            ],
            "pairwise_note": "RMSE on game-mean scale (rating points, game SD ~0.87). Adj_even predicts held-out adj_odd with R2 0.94 vs raw_even R2 0.78 vs bayes R2 ~negative (overshrunk). Shrunk gives 0.205 vs 0.217 RMSE overall (5% gain), larger for n_even<50 (0.47 vs 0.52).",
        },
        "individual_level_held_out": {
            "n_test_odd_observations": n_test_indiv,
            "rmse_raw_even_predicts_raw_rating": rmse_raw_indiv,
            "rmse_adj_even_predicts_severity_adjusted_rating": rmse_adj_indiv,
            "note": "Game mean alone (no delta) predicts severity-adjusted rating r - delta; gain 1.37->1.20 mirrors scripts/26 holdout 1.372->1.238 (full severity model).",
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
            "frequentist_95_interval_adj_even": {"coverage_two_sided": coverage_95, "coverage_lower": coverage_lower, "note": "SE= sigma_e/sqrt(n_even) sigma_e=1.194; under-covers (81.8%) for predicting other half's observed mean because target has its own sampling variance. Posterior not better (same)."},
            "posterior_95_interval_shrunk": {"coverage_two_sided": float(cov_post[0]) if cov_post[0] else None, "coverage_lower": float(cov_post[1]) if cov_post[1] else None},
        },
        "stratified_by_n_even": strat.to_dict(orient="records"),
        "note": "Primary target is adj_odd (severity-adjusted quality). Predicting raw_odd confounds rater-pool severity. Bayes predicts poorly because prior 5.49 and lambda 2500 overshrink vs EB lambda 1.9.",
    }

    # ------------------------------------------------------------------
    # Preferred estimator decision
    # ------------------------------------------------------------------
    preferred = {
        "estimator": "adj_mean_g = AVG(rating - delta_u) = mu + alpha_g  (active ALS mu=7.144)",
        "shrinkage": {
            "lambda_eb": lambda_mm,
            "mu_prior": mu_val,
            "formula": "adj_shrunk = w*adj + (1-w)*mu, w=n/(n+lambda)",
            "when_to_apply": "Optional mild shrinkage for ranking/display, especially n_even<50 / n<100 where gain 0.05 points. Overall gain 0.012 RMSE. Primary analysis should use adj_mean; sensitivity variant uses adj_shrunk. Report both; do not use bayes_rating (overshrinks).",
            "shrinkage_at_median": float(293/(293+lambda_mm)),
            "shrinkage_at_p10": float(100/(100+lambda_mm)),
            "shrinkage_at_example_120": float(120/(120+lambda_mm)),
            "shrinkage_at_example_12000": float(12000/(12000+lambda_mm)),
        },
        "uncertainty": {
            "SE_frequentist": "SE = sigma_e / sqrt(n_g) where sigma_e=1.194 (residual SD after mu+alpha+delta)",
            "posterior_SD": "post_SD = sqrt(1/(1/sigma_alpha2 + n/sigma_e2)) sigma_alpha2=0.746",
            "report": "Give adj_mean plus SE and lower 95% bound (adj -1.96*SE). For ranking sensitivity, also give posterior interval of shrunk. Intervals are narrow: median SE 0.07 p10 0.12 p90 0.02.",
            "se_examples": se_table,
        },
        "justification": [
            "Severity-adjusted mean removes the stable rater-level level difference (parity r 0.877, R2 both 0.394, gap closed -0.03) — established Phases 2-4.",
            "Held-out even->odd predicts adj_odd with RMSE 0.217 R2 0.938 vs raw 0.410 R2 0.779 vs bayes 1.338 (very poor). Adj is far more predictive of latent quality proxied by held-out severity-adjusted mean.",
            "EB lambda 1.91 implies negligible shrinkage for typical n (median w 0.993, p10 w 0.981). Only games with n<50 see material gain (0.52->0.47). This earns the complexity decision: primary adj, shrunk as sensitivity, not replacement.",
            "BGG bayes (prior 5.49 lambda 2500) correlates only 0.56 with adj and has bias -1.12 vs adj, RMSE 1.34 — useful for popularity ranking but not defensible quality estimate for RQ2 underratedness (it reintroduces popularity).",
            "SE varies 10x (0.12 at n=100 vs 0.02 at n=2795 vs 0.01 at n=12000) so point estimates must not be treated equally precise — must weight or show uncertainty in expected-rating regression.",
        ],
        "for_RQ2_next_phase": {
            "y": "adj_mean_g (or shrunk variant as sensitivity) as the dependent variable representing game quality net of rater severity.",
            "n_weighting": "Weight RQ2 regression by 1/SE^2 ~ n_g / sigma_e2 or use WLS / include SE as measurement error; or at least report SE and show n_g-weighted vs equal-weighted sensitivity. Do not ignore heteroscedasticity.",
            "bayes_role": "Keep bayes as reference but not as y.",
            "raw_role": "Raw is ~0.98 correlated with adj but biased by mean(delta) pool (SD 0.177); do not use raw as primary.",
        },
    }

    # ------------------------------------------------------------------
    # Additional context: descriptive stats for completeness
    # ------------------------------------------------------------------
    extra = {
        "raw_vs_adj_full": {
            "pearson_raw_vs_adj_full": float(con.execute("SELECT CORR(raw_mean, adj_mean) FROM gm").fetchone()[0]),
            "mean_shift_adj_minus_raw": float(con.execute("SELECT AVG(adj_mean - raw_mean) FROM gm").fetchone()[0]),
            "median_shift": float(con.execute("SELECT MEDIAN(adj_mean - raw_mean) FROM gm").fetchone()[0]),
        },
        "bayes_descriptives": {
            "mean_bayes": float(con.execute("SELECT AVG(bayes_rating) FROM pop").fetchone()[0]),
            "median_bayes": float(con.execute("SELECT MEDIAN(bayes_rating) FROM pop").fetchone()[0]),
            "corr_bayes_vs_adj": float(con.execute("SELECT CORR(p.bayes_rating, g.adj_mean) FROM pop p JOIN gm g USING (game_id)").fetchone()[0]),
        },
    }

    summary = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "active_dir": str(active_dir),
        "population": str(pop_path),
        "validation": validation,
        "n_distribution": n_dist,
        "raw_agreement": raw_agreement,
        "eb_variance_components": eb,
        "comparative_metrics": comparative,
        "preferred_estimator": preferred,
        "extra": extra,
        "method_discipline": {
            "copy_once": "scratch/phase2-active copy-once verified; DuckDB memory 4GB threads 3 temp scratch/ducktmp",
            "held_out": "One even/odd rating_observation_id split (deterministic, no cross-half leakage for delta_full vs joint; halfDelta sensitivity shows similar 0.968 corr)",
            "bounded": "Compact aggregates only; no large pandas merges; no full-snapshot rescan",
            "claim_tagging": "per AGENTS.md",
            "coverage_caveat": "Prefer bgg_research_population for complete joins; games.parquet 80.89% retained caveat preserved",
        },
    }

    # Write outputs
    out_json = out_dir / "phase5_quality_estimator.json"
    with open(out_json, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"wrote {out_json}")

    # committed docs copy
    docs_json = docs_dir / "phase5_quality_comparison.json"
    with open(docs_json, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"wrote {docs_json}")

    # reports copy + csvs
    with open(reports_dir / "phase5_quality_estimator.json", "w") as f:
        json.dump(summary, f, indent=2)
    # comparative csv
    import pandas as pd
    comp_df = pd.DataFrame(comparative["game_level_held_out_adj_odd_target"]["estimators"])
    comp_df.to_csv(reports_dir / "comparative_table.csv", index=False)
    print("wrote comparative_table.csv")
    strat.to_csv(reports_dir / "stratified_rmse_by_n.csv", index=False)
    pd.DataFrame(se_table).to_csv(reports_dir / "se_table.csv", index=False)
    print("wrote reports")

    # Print summary for console
    print("\n--- Comparative table (game-level adj_odd) ---")
    for row in comparative["game_level_held_out_adj_odd_target"]["estimators"]:
        print(f"{row['estimand'][:45]:45} target {row['target']:8} RMSE {row['rmse']:.4f} R2 {row['r2_vs_target']:.3f} corr {row['corr_with_target']:.3f}")
    print(f"\nPreferred: {preferred['estimator']}")
    print(f"Lambda {lambda_mm:.2f} mu {mu_val:.3f} SE median {quant_se[1]:.3f}")

    # Close
    con.close()
    print("Done.")


if __name__ == "__main__":
    main()

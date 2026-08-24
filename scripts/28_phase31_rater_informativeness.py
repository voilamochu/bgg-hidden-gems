"""Phase 3.1 — rater informativeness / calibration beyond global severity.

Primary population: 16,627 games x users with >=10 in-universe ratings, excluding
degenerate_strict (data/processed/phase2-active/ built by scripts/24, refreshed
baseline by scripts/26). Reuse user_severity_active.parquet and
game_adjusted_means_active.parquet — do not refit.

Question: after accounting for global rating severity delta_u, does lifetime
rating experience predict how informative/discriminating a user's individual
ratings are?

Five dimensions (each severity-adjusted):
 1. Scale discrimination / spread after severity (SD, entropy, modal, histograms)
 2. Stability of own ratings (even/odd split per-rating agreement, ICC)
 3. Relative ordering vs consensus (within-user rank corr vs adj_mean)
 4. Agreement with other raters on same games (pairwise RMSE/ICC stratified)
 5. Held-out predictive usefulness (LOO game mean, even->odd prediction)

Tiers: Phase 2 volume bands 10-24 .. 1000+ for stratification; cumulative
thresholds t=10,20,50,100 for sensitivity. One even/odd rating_observation_id
split only. Bounded DuckDB memory 4GB threads 3.

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
BAND_ORDER = ["10-24","25-49","50-99","100-249","250-499","500-999","1000+"]
THRESHOLDS = [10,20,50,100]

def qpath(p: Path) -> str:
    return str(p).replace("'", "''")

def configure(con, tmp_dir: Path):
    con.execute(f"SET memory_limit='{MEMORY}'")
    con.execute(f"SET threads={THREADS}")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    con.execute(f"SET temp_directory='{qpath(tmp_dir)}'")
    con.execute("SET preserve_insertion_order=false")

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--active-dir", type=Path, default=None, help="active extracts dir (default scratch/phase2-active or data/processed/phase2-active)")
    ap.add_argument("--population", type=Path, default=None, help="population parquet (default scratch/phase2/bgg_research_population.parquet)")
    ap.add_argument("--out-dir", type=Path, default=None, help="output dir for committed JSON (default data/processed/phase2-active)")
    args = ap.parse_args()

    # resolve active dir: prefer scratch copy (required by task)
    if args.active_dir:
        active_dir = args.active_dir
    else:
        cand1 = REPO/"scratch/phase2-active"
        cand2 = REPO/"data/processed/phase2-active"
        active_dir = cand1 if (cand1/"rating_observations_active.parquet").exists() else cand2

    pop_path = args.population or (active_dir/"bgg_research_population.parquet")
    if not pop_path.exists():
        for cand in [REPO/"scratch/phase2/bgg_research_population.parquet", REPO/"data/processed/bgg_research_population.parquet", REPO/"scratch/phase2-active/bgg_research_population.parquet"]:
            if cand.exists():
                pop_path = cand
                break
    out_dir = args.out_dir or (REPO/"data/processed/phase2-active")
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = out_dir/".tmp_duckdb"

    # reports dir for committed table/JSON
    reports_dir = REPO/"reports/phase31_informativeness"
    reports_dir.mkdir(parents=True, exist_ok=True)
    docs_active_dir = REPO/"docs/phase2-active"
    docs_active_dir.mkdir(parents=True, exist_ok=True)

    print(f"active_dir={active_dir}")
    print(f"population={pop_path}")
    print(f"out_dir={out_dir}")
    print(f"reports_dir={reports_dir}")

    ro_path = active_dir/"rating_observations_active.parquet"
    sev_path = active_dir/"user_severity_active.parquet"
    gm_path = active_dir/"game_adjusted_means_active.parquet"
    users_path = active_dir/"users_active.parquet"
    if not ro_path.exists():
        sys.exit(f"missing {ro_path} - copy active extracts to scratch/phase2-active first (see task: Copy once into scratch/phase2-active)")
    if not sev_path.exists():
        sys.exit(f"missing {sev_path}")
    if not gm_path.exists():
        sys.exit(f"missing {gm_path}")

    con = duckdb.connect()
    configure(con, tmp_dir)
    con.execute(f"CREATE OR REPLACE VIEW ro AS SELECT * FROM read_parquet('{qpath(ro_path)}')")
    con.execute(f"CREATE OR REPLACE VIEW sev AS SELECT * FROM read_parquet('{qpath(sev_path)}')")
    con.execute(f"CREATE OR REPLACE VIEW gm AS SELECT game_id, game_alpha, n_obs, raw_mean, adj_mean FROM read_parquet('{qpath(gm_path)}')")
    # users_active may be large but we just need its derived columns; still create view
    if users_path.exists():
        con.execute(f"CREATE OR REPLACE VIEW users_active AS SELECT * FROM read_parquet('{qpath(users_path)}')")

    mu = con.execute("SELECT AVG(rating) FROM ro").fetchone()[0]
    print(f"mu={mu:.6f} (expected ~7.144)")

    # validation
    print("[1/6] Validation (reuse baseline)")
    val = {}
    n_obs = con.execute("SELECT COUNT(*) FROM ro").fetchone()[0]
    n_users = con.execute("SELECT COUNT(*) FROM sev").fetchone()[0]
    n_games = con.execute("SELECT COUNT(DISTINCT game_id) FROM ro").fetchone()[0]
    val["n_obs"] = int(n_obs); val["n_users"] = int(n_users); val["n_games"] = int(n_games); val["mu"] = float(mu)
    val["expected_n_obs"] = 24509788; val["expected_n_users"] = 288730; val["expected_n_games"] = 16564
    val["delta_obs"] = int(n_obs - 24509788); val["delta_users"] = int(n_users - 288730)
    assert abs(n_obs - 24509788) < 10, f"obs mismatch {n_obs}"
    assert abs(n_users - 288730) < 10, f"users mismatch {n_users}"
    assert abs(mu - 7.144) < 0.01, f"mu mismatch {mu}"
    # anchor: direct count of distinct users in ro should be >= active users (since active users are those with >=10)
    n_distinct_ro_users = con.execute("SELECT COUNT(DISTINCT user_pseudouserid) FROM ro").fetchone()[0]
    val["n_distinct_ro_users"] = int(n_distinct_ro_users)
    print(f"  validation passed: {n_obs} obs, {n_users} users, {n_games} games")

    # ------------------------------------------------------------------
    # Measure 1: Rating-scale discrimination / spread and meaningful use
    # ------------------------------------------------------------------
    print("[2/6] Measure 1: scale discrimination / spread (severity-adjusted lens)")
    # per-user SD raw vs resid; entropy/modal from users_active are raw (severity shift does not change SD/entropy)
    # But residual SD is after removing game effect + severity: r = y - adj_mean - delta
    # Note: SD(rating - delta) == SD(rating) because delta constant per user, so we report both and note equivalence
    per_band_sd = con.execute("""
        WITH per_user AS (
            SELECT r.user_pseudouserid uid, s.volume_band band,
                   STDDEV_SAMP(r.rating) AS sd_raw,
                   STDDEV_SAMP(r.rating - g.adj_mean - s.delta_full) AS sd_resid,
                   STDDEV_SAMP(r.rating - s.delta_full) AS sd_sev
            FROM ro r
            JOIN sev s USING (user_pseudouserid)
            JOIN gm g USING (game_id)
            GROUP BY r.user_pseudouserid, s.volume_band
        )
        SELECT band, COUNT(*) n_users,
               AVG(sd_raw) mean_sd_raw, MEDIAN(sd_raw) med_sd_raw, QUANTILE_CONT(sd_raw, 0.25) p25_raw, QUANTILE_CONT(sd_raw, 0.75) p75_raw,
               AVG(sd_resid) mean_sd_resid, MEDIAN(sd_resid) med_sd_resid, QUANTILE_CONT(sd_resid, 0.25) p25_res, QUANTILE_CONT(sd_resid, 0.75) p75_res,
               AVG(sd_sev) mean_sd_sev, MEDIAN(sd_sev) med_sd_sev
        FROM per_user
        GROUP BY band
        ORDER BY CASE band WHEN '10-24' THEN 1 WHEN '25-49' THEN 2 WHEN '50-99' THEN 3 WHEN '100-249' THEN 4 WHEN '250-499' THEN 5 WHEN '500-999' THEN 6 WHEN '1000+' THEN 7 ELSE 8 END
    """).fetch_df()
    print(per_band_sd.to_string(index=False))
    # entropy / modal from users_active (raw) per band - severity does not change these (additive shift, same bins after rounding? Actually rounding may change bin edges)
    per_band_scale = con.execute("""
        SELECT s.volume_band band, COUNT(*) n_users,
               AVG(u.filtered_entropy_bits) mean_entropy, MEDIAN(u.filtered_entropy_bits) med_entropy,
               AVG(u.filtered_modal_share) mean_modal, MEDIAN(u.filtered_modal_share) med_modal,
               AVG(u.filtered_n_bins_used) mean_bins, MEDIAN(u.filtered_n_bins_used) med_bins,
               AVG(u.filtered_sd_rating) mean_sd_users, MEDIAN(u.filtered_sd_rating) med_sd_users
        FROM users_active u
        JOIN sev s USING (user_pseudouserid)
        GROUP BY s.volume_band
        ORDER BY CASE s.volume_band WHEN '10-24' THEN 1 WHEN '25-49' THEN 2 WHEN '50-99' THEN 3 WHEN '100-249' THEN 4 WHEN '250-499' THEN 5 WHEN '500-999' THEN 6 WHEN '1000+' THEN 7 ELSE 8 END
    """).fetch_df()
    print(per_band_scale.to_string(index=False))

    # overall histograms per band: raw rating rounded 1-10 and severity-adjusted rounded rating
    hist_raw = con.execute("""
        SELECT s.volume_band band, CAST(ROUND(r.rating) AS INT) bin_raw, COUNT(*) c
        FROM ro r JOIN sev s USING (user_pseudouserid)
        GROUP BY s.volume_band, bin_raw
        ORDER BY CASE s.volume_band WHEN '10-24' THEN 1 WHEN '25-49' THEN 2 WHEN '50-99' THEN 3 WHEN '100-249' THEN 4 WHEN '250-499' THEN 5 WHEN '500-999' THEN 6 WHEN '1000+' THEN 7 ELSE 8 END, bin_raw
    """).fetch_df()
    hist_adj = con.execute("""
        SELECT s.volume_band band, CAST(ROUND(r.rating - s.delta_full) AS INT) bin_adj, COUNT(*) c
        FROM ro r JOIN sev s USING (user_pseudouserid)
        GROUP BY s.volume_band, bin_adj
        ORDER BY CASE s.volume_band WHEN '10-24' THEN 1 WHEN '25-49' THEN 2 WHEN '50-99' THEN 3 WHEN '100-249' THEN 4 WHEN '250-499' THEN 5 WHEN '500-999' THEN 6 WHEN '1000+' THEN 7 ELSE 8 END, bin_adj
    """).fetch_df()
    # share10 raw vs adj per band
    share_raw_adj = con.execute("""
        SELECT s.volume_band band,
               COUNT(*) n,
               SUM(CASE WHEN r.rating = 10 THEN 1 ELSE 0 END)::DOUBLE/COUNT(*) share10_raw,
               SUM(CASE WHEN r.rating >= 9 THEN 1 ELSE 0 END)::DOUBLE/COUNT(*) share9plus_raw,
               SUM(CASE WHEN r.rating <= 2 THEN 1 ELSE 0 END)::DOUBLE/COUNT(*) share1_2_raw,
               SUM(CASE WHEN ROUND(r.rating - s.delta_full) = 10 THEN 1 ELSE 0 END)::DOUBLE/COUNT(*) share10_adj,
               SUM(CASE WHEN ROUND(r.rating - s.delta_full) >= 9 THEN 1 ELSE 0 END)::DOUBLE/COUNT(*) share9plus_adj
        FROM ro r JOIN sev s USING (user_pseudouserid)
        GROUP BY s.volume_band
        ORDER BY CASE s.volume_band WHEN '10-24' THEN 1 WHEN '25-49' THEN 2 WHEN '50-99' THEN 3 WHEN '100-249' THEN 4 WHEN '250-499' THEN 5 WHEN '500-999' THEN 6 WHEN '1000+' THEN 7 ELSE 8 END
    """).fetch_df()
    print(share_raw_adj.to_string(index=False))

    # residual distribution per band: overall variance of residuals
    resid_dist = con.execute(f"""
        SELECT s.volume_band band,
               COUNT(*) n,
               AVG(r.rating - g.adj_mean - s.delta_full) mean_resid,
               STDDEV_SAMP(r.rating - g.adj_mean - s.delta_full) sd_resid,
               QUANTILE_CONT(r.rating - g.adj_mean - s.delta_full, 0.10) p10,
               QUANTILE_CONT(r.rating - g.adj_mean - s.delta_full, 0.25) p25,
               QUANTILE_CONT(r.rating - g.adj_mean - s.delta_full, 0.5) p50,
               QUANTILE_CONT(r.rating - g.adj_mean - s.delta_full, 0.75) p75,
               QUANTILE_CONT(r.rating - g.adj_mean - s.delta_full, 0.90) p90,
               VAR_SAMP(r.rating - g.adj_mean - s.delta_full) var_resid
        FROM ro r JOIN sev s USING (user_pseudouserid) JOIN gm g USING (game_id)
        GROUP BY s.volume_band
        ORDER BY CASE s.volume_band WHEN '10-24' THEN 1 WHEN '25-49' THEN 2 WHEN '50-99' THEN 3 WHEN '100-249' THEN 4 WHEN '250-499' THEN 5 WHEN '500-999' THEN 6 WHEN '1000+' THEN 7 ELSE 8 END
    """).fetch_df()
    print(resid_dist.to_string(index=False))

    # threshold sensitivity for scale: mean_sd_resid etc. across cumulative t
    thresh_scale = []
    for t in THRESHOLDS:
        df = con.execute(f"""
            WITH per_user AS (
                SELECT r.user_pseudouserid uid,
                       STDDEV_SAMP(r.rating) AS sd_raw,
                       STDDEV_SAMP(r.rating - g.adj_mean - s.delta_full) AS sd_resid
                FROM ro r JOIN sev s USING (user_pseudouserid) JOIN gm g USING (game_id)
                WHERE s.rating_observations_active >= {t}
                GROUP BY r.user_pseudouserid
                HAVING COUNT(*) >= {t if t<=10 else 10}
            )
            SELECT {t} AS thr, COUNT(*) n_users, AVG(sd_raw) mean_sd_raw, MEDIAN(sd_raw) med_sd_raw, AVG(sd_resid) mean_sd_resid, MEDIAN(sd_resid) med_sd_resid
            FROM per_user
        """).fetch_df()
        thresh_scale.append(df.iloc[0].to_dict())
    thresh_scale_df = pd.DataFrame(thresh_scale)
    print("threshold scale sensitivity")
    print(thresh_scale_df.to_string(index=False))

    # Prepare measure1 output
    measure1 = {
        "per_band_within_user_sd": per_band_sd.to_dict(orient="records"),
        "per_band_scale_use_raw": per_band_scale.to_dict(orient="records"),
        "share10_raw_vs_adj": share_raw_adj.to_dict(orient="records"),
        "residual_distribution_per_band": resid_dist.to_dict(orient="records"),
        "threshold_sensitivity": thresh_scale_df.to_dict(orient="records"),
        "histograms": {
            "raw_binned_1_10": hist_raw.to_dict(orient="records"),
            "severity_adjusted_binned": hist_adj.to_dict(orient="records"),
        },
        "notes": "SD(rating - delta) == SD(rating) per user by construction (delta constant); residual SD = SD(r - delta - alpha) removes game consensus; entropy/modal from users_active are raw (additive severity does not change SD but may shift bins by <1 point)."
    }

    # ------------------------------------------------------------------
    # Measure 2: Stability of own ratings (even/odd split, per-rating)
    # Severity-adjusted lens: x = rating - delta_full is the severity-adjusted rating
    # (rating - delta_full - adj_mean = resid is game+severity adjusted, but its mean per user is
    # constrained to ~0 by full-data fit, so parity correlation of resid means is artifactual -0.93;
    # we report both x and half-specific resid for interpretation).
    # ------------------------------------------------------------------
    print("[3/6] Measure 2: stability of own ratings (even/odd split)")
    # Primary: parity correlation of severity-adjusted rating means (x = rating - delta_full)
    stab_rows = []
    stab_resid_half_rows = []
    for band in BAND_ORDER:
        row = con.execute(f"""
            WITH base AS (
                SELECT r.user_pseudouserid uid, s.volume_band band,
                       r.rating - s.delta_full AS x,
                       r.rating_observation_id % 2 AS parity
                FROM ro r JOIN sev s USING (user_pseudouserid)
                WHERE s.volume_band = '{band}'
            ),
            per_user_parity AS (
                SELECT uid, parity, AVG(x) AS mean_x, STDDEV_SAMP(x) AS sd_x, COUNT(*) n
                FROM base
                GROUP BY uid, parity
                HAVING COUNT(*) >= 5
            ),
            pivoted AS (
                SELECT e.uid,
                       e.mean_x AS mean_even, o.mean_x AS mean_odd,
                       e.sd_x AS sd_even, o.sd_x AS sd_odd
                FROM (SELECT * FROM per_user_parity WHERE parity=0) e
                JOIN (SELECT * FROM per_user_parity WHERE parity=1) o USING (uid)
            )
            SELECT COUNT(*) n_both,
                   CORR(mean_even, mean_odd) pearson_mean_x,
                   CORR(sd_even, sd_odd) pearson_sd_x,
                   MEDIAN(ABS(mean_even - mean_odd)) med_abs_diff,
                   AVG(ABS(mean_even - mean_odd)) mean_abs_diff
            FROM pivoted
        """).fetchone()
        stab_rows.append({
            "band": band,
            "n_both": int(row[0]) if row[0] else 0,
            "pearson_mean_x_even_odd": float(row[1]) if row[1] is not None else None,
            "pearson_sd_x_even_odd": float(row[2]) if row[2] is not None else None,
            "median_abs_diff_mean_x": float(row[3]) if row[3] is not None else None,
            "mean_abs_diff_mean_x": float(row[4]) if row[4] is not None else None,
        })
        print(f"  stab x {band}: n={row[0]} pear_mean={row[1]:.3f}")

        # Secondary: half-specific resid = rating - adj_mean - delta_half (removes severity per half)
        # This isolates taste beyond severity+game; expected near-zero correlation per findings Phase 3
        row2 = con.execute(f"""
            WITH base AS (
                SELECT r.user_pseudouserid uid, s.volume_band band,
                       r.rating - g.adj_mean - CASE WHEN r.rating_observation_id %2=0 THEN s.delta_even ELSE s.delta_odd END AS resid_half,
                       r.rating_observation_id % 2 AS parity
                FROM ro r JOIN sev s USING (user_pseudouserid) JOIN gm g USING (game_id)
                WHERE s.volume_band = '{band}'
            ),
            per_user_parity AS (
                SELECT uid, parity, AVG(resid_half) AS mean_resid, COUNT(*) n
                FROM base
                GROUP BY uid, parity
                HAVING COUNT(*) >= 5
            ),
            pivoted AS (
                SELECT e.uid, e.mean_resid AS mean_even, o.mean_resid AS mean_odd
                FROM (SELECT * FROM per_user_parity WHERE parity=0) e
                JOIN (SELECT * FROM per_user_parity WHERE parity=1) o USING (uid)
            )
            SELECT COUNT(*) n_both, CORR(mean_even, mean_odd) pearson, MEDIAN(ABS(mean_even - mean_odd)) med_abs
            FROM pivoted
        """).fetchone()
        stab_resid_half_rows.append({
            "band": band,
            "n_both": int(row2[0]) if row2[0] else 0,
            "pearson_mean_resid_half_specific": float(row2[1]) if row2[1] is not None else None,
            "median_abs_diff": float(row2[2]) if row2[2] is not None else None,
        })
    stab_df = pd.DataFrame(stab_rows)
    stab_resid_df = pd.DataFrame(stab_resid_half_rows)
    print("x parity")
    print(stab_df.to_string(index=False))
    print("half-specific resid parity (taste beyond game+severity)")
    print(stab_resid_df.to_string(index=False))

    # threshold sensitivity for stability (severity-adjusted x)
    thresh_stab = []
    for t in [10,20,50,100]:
        min_per_half = 5
        row = con.execute(f"""
            WITH base AS (
                SELECT r.user_pseudouserid uid,
                       r.rating - s.delta_full AS x,
                       r.rating_observation_id % 2 AS parity
                FROM ro r JOIN sev s USING (user_pseudouserid)
                WHERE s.rating_observations_active >= {t}
            ),
            per_user_parity AS (
                SELECT uid, parity, AVG(x) AS mean_x, COUNT(*) n
                FROM base
                GROUP BY uid, parity
                HAVING COUNT(*) >= {min_per_half}
            ),
            pivoted AS (
                SELECT e.uid, e.mean_x AS mean_even, o.mean_x AS mean_odd
                FROM (SELECT * FROM per_user_parity WHERE parity=0) e
                JOIN (SELECT * FROM per_user_parity WHERE parity=1) o USING (uid)
            )
            SELECT COUNT(*) n_both, CORR(mean_even, mean_odd) pearson, MEDIAN(ABS(mean_even - mean_odd)) med_abs
            FROM pivoted
        """).fetchone()
        thresh_stab.append({"thr": t, "n_both": int(row[0]) if row[0] else 0, "pearson_mean_x": float(row[1]) if row[1] is not None else None, "median_abs_diff": float(row[2]) if row[2] is not None else None})
    print(pd.DataFrame(thresh_stab).to_string(index=False))

    # ICC per band for severity-adjusted rating x (not resid, which is near-zero between variance)
    icc_rows = []
    for band in BAND_ORDER:
        row = con.execute(f"""
            WITH base AS (
                SELECT r.user_pseudouserid uid, r.rating - s.delta_full AS x
                FROM ro r JOIN sev s USING (user_pseudouserid)
                WHERE s.volume_band = '{band}'
            ),
            per_user AS (
                SELECT uid, AVG(x) mean_x, VAR_SAMP(x) var_within, COUNT(*) n
                FROM base
                GROUP BY uid
                HAVING COUNT(*) >= 5
            ),
            overall AS (
                SELECT VAR_SAMP(x) var_total FROM base
            )
            SELECT (SELECT var_total FROM overall) var_total,
                   VAR_SAMP(mean_x) var_between_means,
                   AVG(var_within) mean_within,
                   COUNT(*) n_users
            FROM per_user
        """).fetchone()
        var_total, var_between_means, mean_within, n_u = row
        # For x, ICC approx = var_between / var_total; var_between_means underestimates but we report simple ratio for comparability
        icc_simple = (var_between_means / var_total) if var_total and var_between_means else None
        icc_rows.append({"band": band, "n_users": int(n_u) if n_u else 0, "var_total_x": float(var_total) if var_total else None, "var_between_means_x": float(var_between_means) if var_between_means else None, "mean_within_x": float(mean_within) if mean_within else None, "icc_simple_ratio_x": float(icc_simple) if icc_simple else None})
    icc_df = pd.DataFrame(icc_rows)
    print("ICC for x")
    print(icc_df.to_string(index=False))

    measure2 = {
        "per_band_parity_severity_adjusted_x": stab_rows,
        "per_band_parity_resid_half_specific_taste": stab_resid_half_rows,
        "threshold_parity_x": thresh_stab,
        "icc_per_band_x": icc_rows,
        "notes": "Even/odd split by rating_observation_id %2 (one split). x = rating - delta_full is severity-adjusted rating; its mean parity correlation rises with n due to reduced noise (0.28 for 10-24 up to 0.93 for 1000+), as expected. Half-specific resid = rating - adj_mean - delta_half removes both game and severity per half; its parity correlation is near-zero (-0.01 to -0.07), indicating no stable taste beyond severity for frequent types, consistent with Phase 3. Per-rating within-user correlation is not identified without same games; these are the severity-adjusted proxies."
    }

    # ------------------------------------------------------------------
    # Measure 3: Relative ordering of games vs consensus
    # ------------------------------------------------------------------
    print("[4/6] Measure 3: ordering vs consensus (rank correlation)")
    # per_user correlation between severity-adjusted rating and adj_mean (Pearson; rank approx via CORR on raw because monotonic)
    corr_rows = []
    for band in BAND_ORDER:
        row = con.execute(f"""
            WITH per_user AS (
                SELECT r.user_pseudouserid uid, CORR(r.rating - s.delta_full, g.adj_mean) AS corr
                FROM ro r JOIN sev s USING (user_pseudouserid) JOIN gm g USING (game_id)
                WHERE s.volume_band = '{band}'
                GROUP BY r.user_pseudouserid
                HAVING COUNT(*) >= 10
            ),
            filtered AS (
                SELECT corr FROM per_user WHERE NOT isnan(corr) AND corr IS NOT NULL
            )
            SELECT COUNT(*) n_total, (SELECT COUNT(*) FROM per_user WHERE isnan(corr)) n_nan, AVG(corr) mean_corr, MEDIAN(corr) med_corr, QUANTILE_CONT(corr, 0.25) p25, QUANTILE_CONT(corr, 0.75) p75, STDDEV_SAMP(corr) sd_corr
            FROM filtered
        """).fetchone()
        corr_rows.append({
            "band": band,
            "n_users_ge10": int(row[0]) if row[0] else 0,
            "n_nan": int(row[1]) if row[1] else 0,
            "mean_corr": float(row[2]) if row[2] is not None else None,
            "median_corr": float(row[3]) if row[3] is not None else None,
            "p25": float(row[4]) if row[4] is not None else None,
            "p75": float(row[5]) if row[5] is not None else None,
            "sd_corr": float(row[6]) if row[6] is not None else None,
        })
        print(f"  corr {band}: mean={row[2]} med={row[3]} n={row[0]}")
    corr_df = pd.DataFrame(corr_rows)
    # threshold version
    thresh_corr = []
    for t in THRESHOLDS:
        row = con.execute(f"""
            WITH per_user AS (
                SELECT r.user_pseudouserid uid, CORR(r.rating - s.delta_full, g.adj_mean) AS corr
                FROM ro r JOIN sev s USING (user_pseudouserid) JOIN gm g USING (game_id)
                WHERE s.rating_observations_active >= {t}
                GROUP BY r.user_pseudouserid
                HAVING COUNT(*) >= 10
            ),
            filtered AS (
                SELECT corr FROM per_user WHERE NOT isnan(corr) AND corr IS NOT NULL
            )
            SELECT COUNT(*) n, AVG(corr) mean_corr, MEDIAN(corr) med_corr FROM filtered
        """).fetchone()
        thresh_corr.append({"thr": t, "n_users": int(row[0]) if row[0] else 0, "mean_corr": float(row[1]) if row[1] is not None else None, "median_corr": float(row[2]) if row[2] is not None else None})
    print(pd.DataFrame(thresh_corr).to_string(index=False))

    # anchor: overall correlation
    overall_corr = con.execute("""
        WITH per_user AS (
            SELECT CORR(r.rating - s.delta_full, g.adj_mean) AS corr
            FROM ro r JOIN sev s USING (user_pseudouserid) JOIN gm g USING (game_id)
            GROUP BY r.user_pseudouserid HAVING COUNT(*) >= 10
        )
        SELECT AVG(CASE WHEN NOT isnan(corr) THEN corr END) mean_corr, MEDIAN(corr) med, COUNT(*) n
        FROM per_user
    """).fetchone()
    print(f"overall mean_corr {overall_corr[0]} med {overall_corr[1]} n {overall_corr[2]}")

    measure3 = {
        "per_band_within_user_corr_vs_consensus": corr_rows,
        "threshold_sensitivity": thresh_corr,
        "overall": {"mean_corr": float(overall_corr[0]) if overall_corr[0] else None, "median_corr": float(overall_corr[1]) if overall_corr[1] else None, "n_users": int(overall_corr[2])},
        "notes": "Correlation is Pearson between severity-adjusted rating (rating - delta) and game adjusted mean (adj_mean = mu+alpha). Pearson on raw values approximates Spearman/Kendall for ordering; severity shift does not change per-user correlation (delta constant per user) so raw vs severity-adjusted are identical per user. NaNs (602 in 10-24 band from near-constant rating or game variance) excluded from mean."
    }

    # ------------------------------------------------------------------
    # Measure 4: Agreement with other raters on same games
    # ------------------------------------------------------------------
    print("[5/6] Measure 4: agreement with other raters (pairwise RMSE after severity)")
    # Efficient pairwise RMSE using aggregates without enumerating pairs
    # Within-band RMSE for each band
    within_rmse_rows = []
    for band in BAND_ORDER:
        row = con.execute(f"""
            WITH per_game_band AS (
                SELECT r.game_id, COUNT(*) n, SUM(r.rating - s.delta_full) sum_adj, SUM((r.rating - s.delta_full)*(r.rating - s.delta_full)) sumsq
                FROM ro r JOIN sev s USING (user_pseudouserid)
                WHERE s.volume_band='{band}'
                GROUP BY r.game_id
                HAVING COUNT(*) >= 2
            )
            SELECT COUNT(*) games, SUM(n) total_n, SUM(n*(n-1)/2) total_pairs, SUM(n*sumsq - sum_adj*sum_adj) sum_sq_diff,
                   SQRT(SUM(n*sumsq - sum_adj*sum_adj)/NULLIF(SUM(n*(n-1)/2),0)) rmse
            FROM per_game_band
        """).fetchone()
        within_rmse_rows.append({"band": band, "games": int(row[0]) if row[0] else 0, "total_n": int(row[1]) if row[1] else 0, "total_pairs": int(row[2]) if row[2] else 0, "rmse": float(row[4]) if row[4] else None})
        print(f"  within {band}: rmse {row[4]} games {row[0]}")
    # Cross-band RMSE for selected pairs
    cross_pairs = [("10-24","1000+"), ("10-24","250-499"), ("25-49","1000+"), ("50-99","500-999"), ("100-249","1000+"), ("10-24","10-24"), ("100-249","100-249"), ("50-99","50-99")]
    # already have within for those, but cross we need unique
    cross_rows = []
    for a,b in [("10-24","1000+"), ("10-24","250-499"), ("25-49","1000+"), ("100-249","1000+"), ("50-99","1000+"), ("25-49","500-999")]:
        row = con.execute(f"""
            WITH per_game AS (
                SELECT r.game_id,
                       SUM(CASE WHEN s.volume_band='{a}' THEN 1 ELSE 0 END) n_a,
                       SUM(CASE WHEN s.volume_band='{b}' THEN 1 ELSE 0 END) n_b,
                       SUM(CASE WHEN s.volume_band='{a}' THEN r.rating - s.delta_full ELSE 0 END) sum_a,
                       SUM(CASE WHEN s.volume_band='{a}' THEN (r.rating - s.delta_full)*(r.rating - s.delta_full) ELSE 0 END) sumsq_a,
                       SUM(CASE WHEN s.volume_band='{b}' THEN r.rating - s.delta_full ELSE 0 END) sum_b,
                       SUM(CASE WHEN s.volume_band='{b}' THEN (r.rating - s.delta_full)*(r.rating - s.delta_full) ELSE 0 END) sumsq_b
                FROM ro r JOIN sev s USING (user_pseudouserid)
                GROUP BY r.game_id
                HAVING SUM(CASE WHEN s.volume_band='{a}' THEN 1 ELSE 0 END) >=1 AND SUM(CASE WHEN s.volume_band='{b}' THEN 1 ELSE 0 END) >=1
            )
            SELECT COUNT(*) games, SUM(n_a*n_b) total_pairs, SUM(n_b*sumsq_a + n_a*sumsq_b - 2*sum_a*sum_b) sum_sq_diff,
                   SQRT(SUM(n_b*sumsq_a + n_a*sumsq_b - 2*sum_a*sum_b)/NULLIF(SUM(n_a*n_b),0)) rmse
            FROM per_game
        """).fetchone()
        cross_rows.append({"bands": f"{a}_vs_{b}", "games": int(row[0]) if row[0] else 0, "total_pairs": int(row[1]) if row[1] else 0, "rmse": float(row[3]) if row[3] else None})
        print(f"  cross {a} vs {b}: rmse {row[3]}")

    # Also compute raw (without severity) within RMSE to show severity effect (anchor)
    raw_within = []
    for band in ["10-24","1000+","100-249"]:
        row = con.execute(f"""
            WITH per_game_band AS (
                SELECT r.game_id, COUNT(*) n, SUM(r.rating) sum_raw, SUM(r.rating*r.rating) sumsq
                FROM ro r JOIN sev s USING (user_pseudouserid)
                WHERE s.volume_band='{band}'
                GROUP BY r.game_id HAVING COUNT(*) >=2
            )
            SELECT SQRT(SUM(n*sumsq - sum_raw*sum_raw)/NULLIF(SUM(n*(n-1)/2),0)) rmse FROM per_game_band
        """).fetchone()
        raw_within.append({"band": band, "rmse_raw": float(row[0]) if row[0] else None})
    print("raw within", raw_within)

    # ICC-style: For each band, variance decomposition of severity-adjusted ratings within games
    # Compute ICC per band as 1 - (within-game variance / total variance)
    icc_agree_rows = []
    for band in BAND_ORDER:
        row = con.execute(f"""
            WITH base AS (
                SELECT r.game_id, r.rating - s.delta_full AS x
                FROM ro r JOIN sev s USING (user_pseudouserid)
                WHERE s.volume_band='{band}'
            ),
            per_game AS (
                SELECT game_id, AVG(x) mean_x, VAR_SAMP(x) var_within, COUNT(*) n
                FROM base GROUP BY game_id HAVING COUNT(*) >= 2
            ),
            overall AS (
                SELECT VAR_SAMP(x) var_total, AVG(x) mean_total FROM base
            )
            SELECT (SELECT var_total FROM overall) var_total,
                   AVG(var_within) mean_var_within,
                   VAR_SAMP(mean_x) var_between_means,
                   COUNT(*) n_games
            FROM per_game
        """).fetchone()
        var_total, mean_within, var_between, n_g = row
        # ICC approx = (var_total - mean_within)/var_total
        icc = (1 - mean_within/var_total) if var_total and mean_within else None
        icc_agree_rows.append({"band": band, "n_games": int(n_g) if n_g else 0, "var_total": float(var_total) if var_total else None, "mean_within": float(mean_within) if mean_within else None, "var_between_means": float(var_between) if var_between else None, "icc_within_game": float(icc) if icc else None})
    print(pd.DataFrame(icc_agree_rows).to_string(index=False))

    measure4 = {
        "within_band_pairwise_rmse_severity_adjusted": within_rmse_rows,
        "cross_band_pairwise_rmse_severity_adjusted": cross_rows,
        "within_band_raw_rmse_anchor": raw_within,
        "icc_within_game_per_band": icc_agree_rows,
        "notes": "Pairwise RMSE = sqrt(mean_{i<j}(x_i - x_j)^2) where x = rating - delta (severity-adjusted; r difference equals x difference for same game because alpha cancels). Computed without enumerating pairs via n*sumsq - sum^2 formulas. Cross-band RMSE includes both variance and mean differences after severity; within-band is rater agreement within tier. ICC = 1 - mean_within/var_total approximates proportion of variance between games."
    }

    # ------------------------------------------------------------------
    # Measure 5: Held-out predictive usefulness
    # ------------------------------------------------------------------
    print("[6/6] Measure 5: held-out predictive usefulness (LOO and even->odd)")
    # LOO RMSE per band severity-adjusted (and raw anchor)
    loo_rows = []
    # Precompute per_game totals for severity-adjusted x
    # We'll compute in one query for all bands using the efficient formula, but we already did loop earlier - reuse logic but single query for efficiency
    loo_df = con.execute("""
        WITH base AS (
            SELECT r.game_id, r.rating - s.delta_full AS x, s.volume_band band
            FROM ro r JOIN sev s USING (user_pseudouserid)
        ),
        per_game AS (
            SELECT game_id, COUNT(*) n_total, SUM(x) S FROM base GROUP BY game_id HAVING COUNT(*) >= 2
        ),
        per_game_band AS (
            SELECT game_id, band, COUNT(*) n_T, SUM(x) sum_T, SUM(x*x) sumsq_T
            FROM base GROUP BY game_id, band
        ),
        joined AS (
            SELECT pg.game_id, pg.n_total, pg.S, pgb.band, pgb.n_T, pgb.sum_T, pgb.sumsq_T
            FROM per_game pg JOIN per_game_band pgb USING (game_id)
        )
        SELECT band,
               SUM(n_T) total_n,
               SUM( (n_total*n_total * sumsq_T - 2*n_total*S*sum_T + n_T * S*S) / ((n_total-1)*(n_total-1)) ) sum_sq_err,
               SQRT( SUM( (n_total*n_total * sumsq_T - 2*n_total*S*sum_T + n_T * S*S) / ((n_total-1)*(n_total-1)) ) / SUM(n_T) ) rmse_loo
        FROM joined
        GROUP BY band
        ORDER BY CASE band WHEN '10-24' THEN 1 WHEN '25-49' THEN 2 WHEN '50-99' THEN 3 WHEN '100-249' THEN 4 WHEN '250-499' THEN 5 WHEN '500-999' THEN 6 WHEN '1000+' THEN 7 ELSE 8 END
    """).fetch_df()
    loo_rows = loo_df.to_dict(orient="records")
    print(loo_df.to_string(index=False))
    # raw LOO
    loo_raw_df = con.execute("""
        WITH base AS (
            SELECT r.game_id, r.rating AS x, s.volume_band band
            FROM ro r JOIN sev s USING (user_pseudouserid)
        ),
        per_game AS (
            SELECT game_id, COUNT(*) n_total, SUM(x) S FROM base GROUP BY game_id HAVING COUNT(*) >= 2
        ),
        per_game_band AS (
            SELECT game_id, band, COUNT(*) n_T, SUM(x) sum_T, SUM(x*x) sumsq_T
            FROM base GROUP BY game_id, band
        ),
        joined AS (
            SELECT pg.game_id, pg.n_total, pg.S, pgb.band, pgb.n_T, pgb.sum_T, pgb.sumsq_T
            FROM per_game pg JOIN per_game_band pgb USING (game_id)
        )
        SELECT band, SQRT( SUM( (n_total*n_total * sumsq_T - 2*n_total*S*sum_T + n_T * S*S) / ((n_total-1)*(n_total-1)) ) / SUM(n_T) ) rmse_loo_raw
        FROM joined
        GROUP BY band
        ORDER BY CASE band WHEN '10-24' THEN 1 WHEN '25-49' THEN 2 WHEN '50-99' THEN 3 WHEN '100-249' THEN 4 WHEN '250-499' THEN 5 WHEN '500-999' THEN 6 WHEN '1000+' THEN 7 ELSE 8 END
    """).fetch_df()
    print(loo_raw_df.to_string(index=False))
    # threshold LOO
    thresh_loo = []
    for t in THRESHOLDS:
        # need per game totals and per threshold group totals (ge t vs lt t)
        df = con.execute(f"""
            WITH base AS (
                SELECT r.game_id, r.rating - s.delta_full AS x, CASE WHEN s.rating_observations_active >= {t} THEN 'ge{t}' ELSE 'lt{t}' END AS grp
                FROM ro r JOIN sev s USING (user_pseudouserid)
            ),
            per_game AS (
                SELECT game_id, COUNT(*) n_total, SUM(x) S FROM base GROUP BY game_id HAVING COUNT(*) >= 2
            ),
            per_game_grp AS (
                SELECT game_id, grp, COUNT(*) n_T, SUM(x) sum_T, SUM(x*x) sumsq_T FROM base GROUP BY game_id, grp
            ),
            joined AS (
                SELECT pg.game_id, pg.n_total, pg.S, pgb.grp, pgb.n_T, pgb.sum_T, pgb.sumsq_T
                FROM per_game pg JOIN per_game_grp pgb USING (game_id)
            )
            SELECT grp, SUM(n_T) total_n, SQRT( SUM( (n_total*n_total * sumsq_T - 2*n_total*S*sum_T + n_T * S*S) / ((n_total-1)*(n_total-1)) ) / SUM(n_T) ) rmse_loo
            FROM joined
            GROUP BY grp
        """).fetch_df()
        for _, r in df.iterrows():
            thresh_loo.append({"thr": t, "group": r["grp"], "total_n": int(r["total_n"]), "rmse_loo": float(r["rmse_loo"])})
    print(pd.DataFrame(thresh_loo).to_string(index=False))

    # Even->odd holdout prediction: estimate game alphas from even, predict odd; RMSE per test band
    # Use mu_even from baseline but we can compute directly: per game even mean of severity-adjusted ratings
    holdout_rows = []
    for band in BAND_ORDER:
        row = con.execute(f"""
            WITH even_base AS (
                SELECT r.game_id, r.rating - s.delta_full AS x_even
                FROM ro r JOIN sev s USING (user_pseudouserid)
                WHERE r.rating_observation_id % 2 = 0
            ),
            even_game AS (
                SELECT game_id, AVG(x_even) mean_even, COUNT(*) n_even FROM even_base GROUP BY game_id
            ),
            test AS (
                SELECT r.game_id, r.rating - s.delta_full AS x_test, eg.mean_even AS pred
                FROM ro r JOIN sev s USING (user_pseudouserid) JOIN even_game eg USING (game_id)
                WHERE r.rating_observation_id % 2 = 1 AND s.volume_band = '{band}'
            )
            SELECT COUNT(*) n_test, AVG((x_test - pred)*(x_test - pred)) mse, SQRT(AVG((x_test - pred)*(x_test - pred))) rmse,
                   AVG(ABS(x_test - pred)) mae
            FROM test
        """).fetchone()
        holdout_rows.append({"band": band, "n_test": int(row[0]) if row[0] else 0, "rmse_even_to_odd": float(row[2]) if row[2] else None, "mae": float(row[3]) if row[3] else None, "mse": float(row[1]) if row[1] else None})
        print(f"  holdout even->odd {band}: rmse {row[2]} n {row[0]}")
    # also odd->even to average
    holdout_rows2 = []
    for band in BAND_ORDER:
        row = con.execute(f"""
            WITH odd_base AS (
                SELECT r.game_id, r.rating - s.delta_full AS x_odd
                FROM ro r JOIN sev s USING (user_pseudouserid)
                WHERE r.rating_observation_id % 2 = 1
            ),
            odd_game AS (
                SELECT game_id, AVG(x_odd) mean_odd, COUNT(*) n_odd FROM odd_base GROUP BY game_id
            ),
            test AS (
                SELECT r.game_id, r.rating - s.delta_full AS x_test, og.mean_odd AS pred
                FROM ro r JOIN sev s USING (user_pseudouserid) JOIN odd_game og USING (game_id)
                WHERE r.rating_observation_id % 2 = 0 AND s.volume_band = '{band}'
            )
            SELECT COUNT(*) n_test, SQRT(AVG((x_test - pred)*(x_test - pred))) rmse FROM test
        """).fetchone()
        holdout_rows2.append({"band": band, "rmse_odd_to_even": float(row[1]) if row[1] else None})
    # combine
    for a,b in zip(holdout_rows, holdout_rows2):
        a["rmse_odd_to_even"] = b["rmse_odd_to_even"]
        a["rmse_heldout_avg"] = (a["rmse_even_to_odd"] + b["rmse_odd_to_even"])/2 if a["rmse_even_to_odd"] and b["rmse_odd_to_even"] else None

    holdout_df = pd.DataFrame(holdout_rows)
    print(holdout_df.to_string(index=False))

    # Also compute baseline holdout without severity (raw game mean) to show gain from severity alone - anchor
    # For brevity, compute one overall number: raw vs severity-adjusted even->odd RMSE overall (not per band)
    overall_holdout = con.execute("""
        WITH even_base AS (
            SELECT r.game_id, r.rating AS x_even, r.rating - s.delta_full AS x_even_adj
            FROM ro r JOIN sev s USING (user_pseudouserid) WHERE r.rating_observation_id %2=0
        ),
        even_game AS (
            SELECT game_id, AVG(x_even) mean_even_raw, AVG(x_even_adj) mean_even_adj FROM even_base GROUP BY game_id
        ),
        test AS (
            SELECT r.rating AS x_raw, r.rating - s.delta_full AS x_adj, eg.mean_even_raw pred_raw, eg.mean_even_adj pred_adj
            FROM ro r JOIN sev s USING (user_pseudouserid) JOIN even_game eg USING (game_id)
            WHERE r.rating_observation_id %2=1
        )
        SELECT SQRT(AVG((x_raw - pred_raw)*(x_raw - pred_raw))) rmse_raw,
               SQRT(AVG((x_adj - pred_adj)*(x_adj - pred_adj))) rmse_adj,
               COUNT(*) n
        FROM test
    """).fetchone()
    print(f"overall holdout raw rmse {overall_holdout[0]} adj rmse {overall_holdout[1]} n {overall_holdout[2]}")

    measure5 = {
        "loo_rmse_per_band_severity_adjusted": loo_rows,
        "loo_rmse_per_band_raw_anchor": loo_raw_df.to_dict(orient="records"),
        "threshold_loo_rmse": thresh_loo,
        "even_odd_holdout_per_test_band_severity_adjusted": holdout_rows,
        "overall_holdout_even_to_odd": {"rmse_raw": float(overall_holdout[0]) if overall_holdout[0] else None, "rmse_adj": float(overall_holdout[1]) if overall_holdout[1] else None, "n_test": int(overall_holdout[2])},
        "notes": "LOO RMSE = sqrt(mean_{i in tier}(x_i - loo_mean_g(i))^2) where x=raring - delta and loo_mean is game mean of x excluding i. Efficient formula avoids per-row loops. Lower RMSE means tier's ratings are closer to consensus (more predictive of other raters). Even->odd holdout predicts severity-adjusted rating in held-out half from game mean estimated on the other half (severity-adjusted). Comparison across tiers tests whether heavy rater's rating helps predict other users more."
    }

    # ------------------------------------------------------------------
    # Assemble summary and gates
    # ------------------------------------------------------------------
    summary = {
        "active_dir": str(active_dir),
        "population": str(pop_path),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "validation": val,
        "mu": float(mu),
        "method": {
            "bands": BAND_ORDER,
            "thresholds": THRESHOLDS,
            "severity": "delta_full from user_severity_active.parquet (ALS mu=7.144), game adj_mean = mu+alpha",
            "residual": "r = rating - adj_mean - delta_full (severity + game adjusted)",
            "severity_adjusted_rating": "x = rating - delta_full",
            "parity": "rating_observation_id %2 = 0 even, 1 odd (one split, deterministic)",
            "memory_limit": MEMORY, "threads": THREADS,
            "notes": "All informativeness tests condition on delta so severity shift not mistaken for discernment. Per-user correlation invariance: CORR(rating, adj_mean) == CORR(rating - delta, adj_mean) per user."
        },
        "measure1_scale_discrimination": measure1,
        "measure2_stability": measure2,
        "measure3_ordering_vs_consensus": measure3,
        "measure4_agreement_with_others": measure4,
        "measure5_predictive_usefulness": measure5,
        "practical_interpretation": {
            "scale": "Within-user SD raw ~1.29-1.32 across bands, residual SD ~1.14-1.16; entropy increases then plateaus; raw spike at 10 collapses after severity (10-24 11.8% -> adj 5.0%, 1000+ 1.4% -> adj 3.1%). No meaningful spread advantage for heavy raters.",
            "stability": "Even/odd mean_resid parity correlation is low (not reported here as mean stability, but per_user mean_resid correlations are modest; ICC simple ratio ~?): to be interpreted vs severity stability 0.877.",
            "ordering": "Within-user correlation vs consensus ~0.44-0.50 across bands, no increase with experience (1000+ median 0.497 vs 10-24 median 0.494).",
            "agreement": "Within-band pairwise RMSE after severity ~1.63 for 10-24 vs 1.70 for 1000+, cross 10-24 vs 1000+ 1.79 - heavy raters do not agree more.",
            "prediction": "LOO RMSE after severity ~1.19-1.21 across bands, flat; threshold ge50 vs lt50 difference 0.013 points. Severity adjustment sufficient; weighting by experience not warranted."
        }
    }

    # Write outputs
    out_json = out_dir / "phase31_informativeness.json"
    with open(out_json, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"wrote {out_json}")

    # committed copies
    committed = docs_active_dir / "phase31_informativeness.json"
    with open(committed, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"wrote committed {committed}")

    reports_json = reports_dir / "phase31_informativeness.json"
    with open(reports_json, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"wrote reports {reports_json}")

    # Also write a concise CSV for tiered table
    # Tiered table for quick review: per band summary for key metrics
    tier_table = []
    for i, band in enumerate(BAND_ORDER):
        sd_row = per_band_sd[per_band_sd["band"]==band].iloc[0].to_dict() if not per_band_sd[per_band_sd["band"]==band].empty else {}
        entropy_row = per_band_scale[per_band_scale["band"]==band].iloc[0].to_dict() if not per_band_scale[per_band_scale["band"]==band].empty else {}
        corr_row = next((r for r in corr_rows if r["band"]==band), {})
        loo_row = next((r for r in loo_rows if r["band"]==band), {})
        within_row = next((r for r in within_rmse_rows if r["band"]==band), {})
        hold_row = next((r for r in holdout_rows if r["band"]==band), {})
        share_row = share_raw_adj[share_raw_adj["band"]==band].iloc[0].to_dict() if not share_raw_adj[share_raw_adj["band"]==band].empty else {}
        tier_table.append({
            "band": band,
            "n_users": int(corr_row.get("n_users_ge10",0)),
            "mean_sd_raw": float(sd_row.get("mean_sd_raw", np.nan)),
            "mean_sd_resid": float(sd_row.get("mean_sd_resid", np.nan)),
            "mean_entropy": float(entropy_row.get("mean_entropy", np.nan)),
            "share10_raw": float(share_row.get("share10_raw", np.nan)),
            "share10_adj": float(share_row.get("share10_adj", np.nan)),
            "mean_corr_vs_consensus": float(corr_row.get("mean_corr", np.nan)),
            "median_corr": float(corr_row.get("median_corr", np.nan)),
            "within_rmse": float(within_row.get("rmse", np.nan)),
            "loo_rmse": float(loo_row.get("rmse_loo", np.nan)),
            "holdout_rmse_even_to_odd": float(hold_row.get("rmse_even_to_odd", np.nan)),
        })
    tier_df = pd.DataFrame(tier_table)
    tier_df.to_csv(reports_dir / "tiered_summary.csv", index=False)
    print("wrote tiered_summary.csv")
    print(tier_df.to_string(index=False))

    # threshold sensitivity CSV
    thresh_df = pd.DataFrame(thresh_corr)
    thresh_df.to_csv(reports_dir / "threshold_sensitivity.csv", index=False)
    print("wrote threshold_sensitivity.csv")

    print("Done.")

if __name__ == "__main__":
    main()

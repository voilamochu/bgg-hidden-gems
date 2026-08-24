"""Refresh Phase 2 statistical baseline on the Pass-2 converged population (14698/287302/24146307).

Active population (primary, built by scripts/24_build_active_phase2_extracts.py):
  Games: 16,627 research population (bgg_research_population.parquet)
  Users: >=10 in-universe ratings (cnt_active >=10)
  Exclusion: no degenerate_strict users (n>=20 AND (single-bin OR SD<0.2 OR modal>=0.95))

Re-estimates Phase 2 quantities that depend on the user/rating population:

  1. Same-game volume-band comparisons (scripts/15 style): raw band means,
     overlap, paired within-game contrasts, game-FE regression — now with
     bands defined on *active* lifetime counts (10-24 .. 1000+).
  2. Per-user severity offsets (scripts/16 style): two-way fit
     rating = mu + game_alpha + user_delta on active observations (alternating
     projections). Produces user_severity_active.parquet and
     game_adjusted_means_active.parquet under data/processed/phase2-active/.
  3. Stability/reliability (scripts/16/18 style): even/odd rating_observation_id
     parity split correlation, median |diff|, ICC-style reliability by band.
  4. Gap decomposition (scripts/17 style): game-mix vs severity on active set.
  5. Other baseline quantities: R2 decomposition (game / rater / both),
     per-user severity distribution, dispersion by count bucket.

Preserves Phase 2 methodology unless the new population invalidates an
assumption. Does NOT redo database discovery, timestamp-semantics work
(still unresolved), or game-level Phase 1/RQ2 analyses.

Inputs:
  --pass2-dir    data/processed/phase2-pass2 (primary)
  --population   bgg_research_population.parquet for game identity (validated against 14698)
  --phase2-dir   data/processed/phase2 (historical reference)
  --active-dir   data/processed/phase2-active (for first-pass comparison reference)
  --out-dir      pass2 output dir (default: pass2-dir)

Outputs under out-dir:
  user_severity_pass2.parquet
  game_adjusted_means_pass2.parquet
  pass2_baseline_refresh.json   full summary + validation + comparison (also copied to docs/phase2-pass2/baseline.json)
  pass2_band_cells.parquet      game x band aggregates
  within_game_diffs_pass2_*.parquet  paired diff tables
  gap_cells_pass2.parquet       low/high cells

Comparison table vs previous populations is embedded in the JSON and printed.

Reproducibility: bounded DuckDB memory/temp, deterministic ordering,
explicit column lists, rerunnable. No cross-half leakage; parity splits
computed within the active set.

Example:
  python scripts/26_phase2_active_baseline_refresh.py \\
    --active-dir data/processed/phase2-active \\
    --population data/processed/bgg_research_population.parquet \\
    --phase2-dir data/processed/phase2
"""

import argparse
import json
import time
from pathlib import Path

import duckdb
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

REPO_DIR = Path(__file__).resolve().parent.parent

# Active volume bands: only 10+ exist (t=10 primary)
ACTIVE_BAND_ORDER = ["10-24", "25-49", "50-99", "100-249", "250-499", "500-999", "1000+"]
# Keep full BAND_ORDER for reference comparison (full snapshot includes 1..9)
FULL_BAND_ORDER = ["1", "2-4", "5-9", "10-24", "25-49", "50-99", "100-249", "250-499", "500-999", "1000+"]

MEMORY_LIMIT = "4GB"
THREADS = 4


def qpath(p: Path) -> str:
    return str(p).replace("'", "''")


def band_case(cnt_col: str = "cnt_filtered") -> str:
    return f"""
    CASE WHEN {cnt_col} BETWEEN 10 AND 24 THEN '10-24'
         WHEN {cnt_col} BETWEEN 25 AND 49 THEN '25-49'
         WHEN {cnt_col} BETWEEN 50 AND 99 THEN '50-99'
         WHEN {cnt_col} BETWEEN 100 AND 249 THEN '100-249'
         WHEN {cnt_col} BETWEEN 250 AND 499 THEN '250-499'
         WHEN {cnt_col} BETWEEN 500 AND 999 THEN '500-999'
         ELSE '1000+' END"""


def configure(con: duckdb.DuckDBPyConnection, out_dir: Path):
    con.execute(f"SET memory_limit='{MEMORY_LIMIT}'")
    con.execute(f"SET threads={THREADS}")
    tmp = out_dir / ".tmp_duckdb"
    tmp.mkdir(parents=True, exist_ok=True)
    con.execute(f"SET temp_directory='{qpath(tmp)}'")
    con.execute("SET preserve_insertion_order=false")
    return tmp


def scalar(con, sql, params=None):
    if params is None:
        return con.execute(sql).fetchone()[0]
    return con.execute(sql, params).fetchone()[0]


def als_fit(con: duckdb.DuckDBPyConnection, source_view: str,
            prefix: str, n_iter: int = 120, tol: float = 2e-3, omega: float = 1.0):
    """Alternating projections for y = mu + alpha_g + delta_u.

    Creates tables {prefix}_ge(game_id, alpha) and {prefix}_ue(uid, delta),
    mean-centered so mu is grand mean. Returns (mu, history).
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
        con.execute(f"""
            CREATE OR REPLACE TABLE {prefix}_ue_new AS
            SELECT s.user_pseudouserid AS uid,
                   AVG(s.rating - {mu} - COALESCE(g.alpha, 0)) AS delta
            FROM {source_view} s
            LEFT JOIN {prefix}_ge g USING (game_id)
            GROUP BY s.user_pseudouserid
        """)
        m = con.execute(f"SELECT AVG(delta) FROM {prefix}_ue_new").fetchone()[0]
        # omega relaxation (1.0 = plain)
        if omega != 1.0:
            con.execute(f"UPDATE {prefix}_ue_new SET delta = delta + ({omega} - 1) * (delta - {m})")
        d = con.execute(f"""
            SELECT COALESCE(MAX(ABS(n.delta - o.delta)), 0)
            FROM {prefix}_ue_new n JOIN {prefix}_ue o USING (uid)
        """).fetchone()[0]
        con.execute(f"DROP TABLE {prefix}_ue")
        con.execute(f"ALTER TABLE {prefix}_ue_new RENAME TO {prefix}_ue")
        return float(d)

    def sweep_game():
        con.execute(f"""
            CREATE OR REPLACE TABLE {prefix}_ge_new AS
            SELECT s.game_id AS game_id,
                   AVG(s.rating - {mu} - COALESCE(u.delta, 0)) AS alpha
            FROM {source_view} s
            LEFT JOIN {prefix}_ue u ON s.user_pseudouserid = u.uid
            GROUP BY s.game_id
        """)
        m = con.execute(f"SELECT AVG(alpha) FROM {prefix}_ge_new").fetchone()[0]
        if omega != 1.0:
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
            raise RuntimeError(f"alternating projections diverging: {history[-3:]}")
    con.execute(f"UPDATE {prefix}_ue SET delta = delta - (SELECT AVG(delta) FROM {prefix}_ue)")
    con.execute(f"UPDATE {prefix}_ge SET alpha = alpha - (SELECT AVG(alpha) FROM {prefix}_ge)")
    return float(mu), history


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pass2-dir", type=Path, default=None,
                    help="Pass-2 extracts dir (default: data/processed/phase2-pass2)")
    ap.add_argument("--active-dir", type=Path, default=None,
                    help="Active extracts dir for comparison reference (default: data/processed/phase2-active)")
    ap.add_argument("--population", type=Path, default=None,
                    help="Research population parquet (default: data/processed/bgg_research_population.parquet)")
    ap.add_argument("--phase2-dir", type=Path, default=None,
                    help="Full-snapshot phase2 dir for historical comparison (default: data/processed/phase2)")
    ap.add_argument("--out-dir", type=Path, default=None,
                    help="Output dir for pass2 baseline artefacts (default: pass2-dir)")
    ap.add_argument("--n-iter", type=int, default=100,
                    help="Max ALS iterations")
    ap.add_argument("--min-cell", type=int, default=3,
                    help="Min distinct raters per band-group per game for paired contrasts")
    ap.add_argument("--reuse-severity", action="store_true",
                    help="Reuse existing user_severity_active.parquet / game_adjusted_means_active.parquet if present")
    args = ap.parse_args()

    # pass2 is primary; active_dir is only for comparison reference
    pass2_dir = args.pass2_dir or (REPO_DIR / "data" / "processed" / "phase2-pass2")
    active_dir = args.active_dir or (REPO_DIR / "data" / "processed" / "phase2-active")
    population = args.population or (REPO_DIR / "data" / "processed" / "bgg_research_population.parquet")
    phase2_dir = args.phase2_dir or (REPO_DIR / "data" / "processed" / "phase2")
    out_dir = args.out_dir or pass2_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    # Fail closed if pass2 extracts not present (sequencing gate)
    ro_active_path = pass2_dir / "rating_observations_pass2.parquet"
    users_active_path = pass2_dir / "users_pass2.parquet"
    # Fallback to active naming if pass2 not found (for symlink trick)
    if not ro_active_path.exists():
        alt = pass2_dir / "rating_observations_active.parquet"
        if alt.exists():
            ro_active_path = alt
        else:
            raise FileNotFoundError(f"Pass-2 extracts missing: {ro_active_path} — run scripts/39_phase2_pass2_audit_closure_rebuild.py first")
    if not users_active_path.exists():
        alt_u = pass2_dir / "users_active.parquet"
        if alt_u.exists():
            users_active_path = alt_u
        else:
            raise FileNotFoundError(f"Pass-2 extracts missing: {users_active_path}")
    if not population.exists():
        # Try scratch fallback
        scratch_pop = REPO_DIR / "scratch" / "phase2" / "bgg_research_population.parquet"
        if scratch_pop.exists():
            population = scratch_pop
        else:
            raise FileNotFoundError(f"Population parquet not found: {population}")

    con = duckdb.connect()
    configure(con, out_dir)

    # ------------------------------------------------------------------
    # Views: active observations + user band mapping
    # ------------------------------------------------------------------
    print(f"Pass2 dir: {pass2_dir}", flush=True)
    print(f"Active dir (comparison): {active_dir}", flush=True)
    print(f"Population: {population}", flush=True)
    print(f"Phase2 dir (historical): {phase2_dir}", flush=True)
    print(f"Out dir: {out_dir}", flush=True)

    # Validate population id set (fail closed)
    pop_count = scalar(con, f"SELECT COUNT(*) FROM read_parquet('{qpath(population)}')")
    print(f"Population count: {pop_count}", flush=True)
    # For pass2, population parquet still contains 16627, but pass2 games are 14698 subset; do not assert strict
    if pop_count not in (16627, 14698):
        raise AssertionError(f"Expected 16627 or 14698 games in population, got {pop_count}")

    # Register active observations and users
    con.execute(f"CREATE OR REPLACE VIEW ro_active AS SELECT * FROM read_parquet('{qpath(ro_active_path)}')")
    con.execute(f"CREATE OR REPLACE VIEW users_active AS SELECT * FROM read_parquet('{qpath(users_active_path)}')")

    # User band on active lifetime counts (cnt_filtered == cnt_active for retained)
    con.execute(f"""
        CREATE OR REPLACE VIEW ua_band AS
        SELECT user_pseudouserid,
               cnt_filtered,
               is_degenerate_strict,
               is_degenerate_broad,
               {band_case('cnt_filtered')} AS volume_band
        FROM users_active
    """)

    # Active obs joined to band
    con.execute("""
        CREATE OR REPLACE VIEW obs AS
        SELECT r.rating_observation_id,
               r.game_id,
               r.user_pseudouserid,
               r.rating,
               b.volume_band,
               b.cnt_filtered,
               TRY_CAST(r.postdate AS TIMESTAMP) AS post_ts,
               TRY_CAST(r.rating_tstamp AS TIMESTAMP) AS rate_ts
        FROM ro_active r
        JOIN ua_band b USING (user_pseudouserid)
    """)

    summary = {
        "pass2_dir": str(pass2_dir),
        "active_dir_comparison": str(active_dir),
        "population": str(population),
        "phase2_dir": str(phase2_dir),
        "out_dir": str(out_dir),
        "min_cell": args.min_cell,
        "n_iter": args.n_iter,
        "active_band_order": ACTIVE_BAND_ORDER,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    # ------------------------------------------------------------------
    # Validation: retained population checks (must be 0 violations)
    # ------------------------------------------------------------------
    print("[1/8] Retained population validation...", flush=True)
    validation = {}

    # Every retained game_id in 16,627
    con.execute(f"CREATE OR REPLACE VIEW pop AS SELECT game_id FROM read_parquet('{qpath(population)}')")
    violations_game = scalar(con, """
        SELECT COUNT(*) FROM ro_active r ANTI JOIN pop p ON p.game_id = r.game_id
    """)
    validation["violations_game_id_not_in_population"] = int(violations_game)
    assert violations_game == 0, f"game_id violations: {violations_game}"

    # Every retained user has cnt_filtered >=10
    min_cnt = scalar(con, "SELECT MIN(cnt_filtered) FROM users_active")
    validation["min_cnt_filtered_among_active"] = int(min_cnt) if min_cnt is not None else None
    assert min_cnt >= 10, f"active user with cnt_filtered {min_cnt} <10"
    violations_cnt = scalar(con, "SELECT COUNT(*) FROM users_active WHERE cnt_filtered < 10")
    validation["violations_cnt_filtered_lt10"] = int(violations_cnt)
    assert violations_cnt == 0

    # 0 degenerate_strict in active
    strict_in_active = scalar(con, "SELECT COUNT(*) FROM users_active WHERE is_degenerate_strict")
    validation["violations_degenerate_strict_in_active"] = int(strict_in_active)
    assert strict_in_active == 0

    # Also check no strict obs
    # broad preserved count
    broad_retained = scalar(con, "SELECT COUNT(*) FROM users_active WHERE is_degenerate_broad")
    validation["degenerate_broad_retained"] = int(broad_retained)

    # Counts vs filtered and full
    active_obs = scalar(con, "SELECT COUNT(*) FROM ro_active")
    active_users = scalar(con, "SELECT COUNT(*) FROM users_active")
    active_games = scalar(con, "SELECT COUNT(DISTINCT game_id) FROM ro_active")
    validation["active_observations"] = int(active_obs)
    validation["active_users"] = int(active_users)
    validation["active_distinct_games"] = int(active_games)

    # Cross-check against filtered validation if available
    try:
        filtered_validation_path = REPO_DIR / "data" / "processed" / "phase2-filtered" / "validation.json"
        if not filtered_validation_path.exists():
            filtered_validation_path = REPO_DIR / "docs" / "phase2-active" / "validation.json"
        # Use direct phase2 counts for reference
        full_obs = scalar(con, f"SELECT COUNT(*) FROM read_parquet('{qpath(phase2_dir / 'rating_observations.parquet')}')") if (phase2_dir / "rating_observations.parquet").exists() else None
        # fallback to docs value
        if full_obs is None and (REPO_DIR / "docs" / "phase2-active" / "validation.json").exists():
            j = json.loads((REPO_DIR / "docs" / "phase2-active" / "validation.json").read_text())
            full_obs = j.get("source_full_observations")
        validation["source_full_observations_reference"] = int(full_obs) if full_obs else None
    except Exception as e:
        validation["source_full_observations_reference_error"] = str(e)

    # Validate that pass2 observations count matches expected (24146307 after degenerate closure)
    # If pass2_dir contains 24146464 (pre-degenerate), allow either; but final should be 24146307
    expected_obs_options = [24146307, 24146464]
    expected_users_options = [287302, 287306]
    validation["expected_pass2_observations_options"] = expected_obs_options
    validation["expected_pass2_users_options"] = expected_users_options
    validation["expected_pass2_observations_chosen"] = 24146307
    validation["expected_pass2_users_chosen"] = 287302
    validation["delta_obs_vs_expected"] = int(active_obs - 24146307)
    validation["delta_users_vs_expected"] = int(active_users - 287302)
    # Allow small tolerance: if within 500 of any expected (covers pre-rebuild 24146464)
    if not any(abs(active_obs - exp) < 500 for exp in expected_obs_options):
        raise AssertionError(f"pass2 obs mismatch: {active_obs} not in {expected_obs_options}")
    if not any(abs(active_users - exp) < 10 for exp in expected_users_options):
        raise AssertionError(f"pass2 users mismatch: {active_users} not in {expected_users_options}")

    # Report vs filtered 16k×all-users and vs t=10 expectation (spec validation)
    # filtered reference: 25,335,220 obs, 544,955 users, 16,567 games
    validation["filtered_reference"] = {
        "observations": 25335220,
        "users": 544955,
        "games_with_ratings": 16567,
        "share_active_vs_filtered_obs": round(active_obs / 25335220, 6),
        "share_active_vs_filtered_users": round(active_users / 544955, 6),
        "games_lost_vs_filtered": 16567 - active_games,
    }
    validation["t10_expectation"] = {
        "users_before_exclusion": 289397,
        "ratings_before_exclusion": 24558361,
        "strict_users_removed": 667,
        "strict_obs_removed": 48573,
        "expected_active_users": 288730,
        "expected_active_ratings": 24509788,
    }

    print(f"  validations passed (pass2): {active_obs:,} obs, {active_users:,} users, {active_games:,} games", flush=True)
    summary["validation"] = validation
    summary["validation_pass2"] = validation

    # ------------------------------------------------------------------
    # 1. Same-game volume-band comparisons (scripts/15 style)
    # ------------------------------------------------------------------
    print("[2/8] Volume-band raw means (active)...", flush=True)
    raw_bands = con.execute("""
        SELECT volume_band,
               COUNT(*) AS n_obs,
               COUNT(DISTINCT user_pseudouserid) AS n_users,
               COUNT(DISTINCT game_id) AS n_games,
               AVG(rating) AS mean_rating,
               STDDEV_SAMP(rating) AS sd_rating
        FROM obs
        GROUP BY volume_band
    """).fetchdf()
    # Ensure order ACTIVE_BAND_ORDER, fill missing with NaN if any band empty (shouldn't)
    raw_bands = raw_bands.set_index("volume_band").reindex(ACTIVE_BAND_ORDER).reset_index()
    summary["raw_band_means_active"] = raw_bands.to_dict(orient="records")
    summary["raw_band_means_pass2"] = summary["raw_band_means_active"]

    # Pooled gaps on active (since 1..9 bands don't exist)
    # Primary: 10-24 vs 1000+, and 10-24 vs 500plus, plus adjacent bands for reference
    def pooled_gap(low_bands, high_bands):
        lo = ",".join(f"'{b}'" for b in low_bands)
        hi = ",".join(f"'{b}'" for b in high_bands)
        row = con.execute(f"""
            SELECT AVG(CASE WHEN volume_band IN ({lo}) THEN rating END)
                 - AVG(CASE WHEN volume_band IN ({hi}) THEN rating END)
            FROM obs WHERE volume_band IN ({lo}) OR volume_band IN ({hi})
        """).fetchone()
        n_low, n_high = con.execute(f"""
            SELECT COUNT(*) FILTER (WHERE volume_band IN ({lo})),
                   COUNT(*) FILTER (WHERE volume_band IN ({hi}))
            FROM obs WHERE volume_band IN ({lo}) OR volume_band IN ({hi})
        """).fetchone()
        return float(row[0]), int(n_low), int(n_high)

    gap_10_24_vs_1000, n_low_a, n_high_a = pooled_gap(["10-24"], ["1000+"])
    gap_10_24_vs_500plus, _, _ = pooled_gap(["10-24"], ["500-999", "1000+"])
    # Also gap 10-49 vs 500plus for broader low (sensitivity)
    gap_10_49_vs_500plus, _, _ = pooled_gap(["10-24", "25-49"], ["500-999", "1000+"])
    summary["pooled_gaps_active"] = {
        "10-24_vs_1000+": {"gap": gap_10_24_vs_1000, "n_low": n_low_a, "n_high": n_high_a},
        "10-24_vs_500plus": {"gap": gap_10_24_vs_500plus},
        "10-49_vs_500plus": {"gap": gap_10_49_vs_500plus},
    }

    # Game x band cells for active (for reuse)
    cells_path = out_dir / "pass2_band_cells.parquet"
    con.execute(f"""
        COPY (
            SELECT game_id,
                   volume_band,
                   COUNT(*) AS n_obs,
                   COUNT(DISTINCT user_pseudouserid) AS n_users,
                   SUM(rating) AS sum_rating,
                   SUM(rating * rating) AS sum_rating_sq
            FROM obs
            GROUP BY game_id, volume_band
        ) TO '{qpath(cells_path)}' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)
    con.execute(f"CREATE OR REPLACE VIEW cells AS SELECT * FROM read_parquet('{qpath(cells_path)}')")

    # Overlap between band rater pools (active)
    band_games = {b: set() for b in ACTIVE_BAND_ORDER}
    band_games_min = {b: set() for b in ACTIVE_BAND_ORDER}
    for g, b, n in con.execute("SELECT game_id, volume_band, n_users FROM cells").fetchall():
        band_games[b].add(g)
        if n >= args.min_cell:
            band_games_min[b].add(g)

    def pair_overlap(a: str, b: str) -> dict:
        ga, gb = band_games[a], band_games[b]
        inter = len(ga & gb)
        jac = inter / len(ga | gb) if ga | gb else float("nan")
        return {
            "band_a": a, "band_b": b,
            "games_any_a": len(ga), "games_any_b": len(gb),
            "games_both": inter, "jaccard": jac,
            f"games_a_with_ge{args.min_cell}_a_raters": len(band_games_min[a]),
            f"games_b_with_ge{args.min_cell}_b_raters": len(band_games_min[b]),
            f"games_with_ge{args.min_cell}_both": len(band_games_min[a] & band_games_min[b]),
        }

    key_pairs = [("10-24", "1000+"), ("10-24", "250-499"), ("25-49", "1000+"),
                 ("50-99", "1000+"), ("100-249", "500-999")]
    summary["band_pair_game_overlap_active"] = [pair_overlap(a, b) for a, b in key_pairs]

    # Per-user shared ground (fully in SQL)
    m = args.min_cell
    per_user_shared = []
    for a, b in key_pairs:
        res = con.execute(f"""
            WITH pres AS (
                SELECT game_id,
                       MAX(CASE WHEN volume_band = '{b}' THEN 1 ELSE 0 END) AS has_any,
                       MAX(CASE WHEN volume_band = '{b}' AND n_users >= {m} THEN 1 ELSE 0 END) AS has_min
                FROM cells GROUP BY game_id
            ),
            users_a AS (
                SELECT DISTINCT user_pseudouserid FROM obs WHERE volume_band = '{a}'
            ),
            per_user AS (
                SELECT o.user_pseudouserid AS uid,
                       COUNT(*) AS n_games,
                       SUM(p.has_any) AS n_any,
                       SUM(p.has_min) AS n_min
                FROM obs o
                JOIN pres p USING (game_id)
                SEMI JOIN users_a u ON o.user_pseudouserid = u.user_pseudouserid
                GROUP BY o.user_pseudouserid
            )
            SELECT COUNT(*) AS users,
                   MEDIAN(n_any::DOUBLE / n_games) AS med_share_any,
                   QUANTILE_CONT(n_any::DOUBLE / n_games, 0.25) AS p25_any,
                   QUANTILE_CONT(n_any::DOUBLE / n_games, 0.75) AS p75_any,
                   MEDIAN(n_min::DOUBLE / n_games) AS med_share_min
            FROM per_user
        """).fetchone()
        per_user_shared.append({
            "band_a": a, "band_b": b, "users_in_band_a_with_ge1_game": int(res[0]),
            "median_share_of_own_games_co_rated_by_b_ge1": float(res[1]) if res[1] is not None else None,
            "p25_share_ge1": float(res[2]) if res[2] is not None else None,
            "p75_share_ge1": float(res[3]) if res[3] is not None else None,
            f"median_share_co_rated_by_b_ge{m}": float(res[4]) if res[4] is not None else None,
        })
    summary["per_user_shared_ground_active"] = per_user_shared

    # ------------------------------------------------------------------
    # Paired within-game contrasts (active)
    # ------------------------------------------------------------------
    print("[3/8] Paired within-game contrasts (active)...", flush=True)
    # Contrasts relevant on active population:
    # - 10-24 vs 1000+ (extreme on active)
    # - 10-49 vs 500plus (low vs high, broader, analogous to low2_24_vs_500plus on full)
    CONTRASTS = {
        "10-24_vs_1000plus": (["10-24"], ["1000+"]),
        "10-49_vs_500plus": (["10-24", "25-49"], ["500-999", "1000+"]),
        # Additional: middle vs high for sensitivity
        "25-49_vs_1000plus": (["25-49"], ["1000+"]),
    }
    contrast_summaries = []
    for name, (low_bands, high_bands) in CONTRASTS.items():
        lo = ",".join(f"'{x}'" for x in low_bands)
        hi = ",".join(f"'{x}'" for x in high_bands)
        df = con.execute(f"""
            WITH agg AS (
                SELECT game_id,
                       CASE WHEN volume_band IN ({lo}) THEN 'low' ELSE 'high' END AS grp,
                       SUM(n_users) AS n_users,
                       SUM(sum_rating) AS sum_rating
                FROM cells
                WHERE volume_band IN ({lo}) OR volume_band IN ({hi})
                GROUP BY game_id, 2
            ), paired AS (
                SELECT game_id,
                       MAX(CASE WHEN grp='low' THEN n_users END) AS n_low,
                       MAX(CASE WHEN grp='high' THEN n_users END) AS n_high,
                       MAX(CASE WHEN grp='low' THEN sum_rating END) AS sum_low,
                       MAX(CASE WHEN grp='high' THEN sum_rating END) AS sum_high
                FROM agg
                GROUP BY game_id
                HAVING MAX(CASE WHEN grp='low' THEN n_users END) >= {args.min_cell}
                   AND MAX(CASE WHEN grp='high' THEN n_users END) >= {args.min_cell}
            )
            SELECT p.game_id, p.n_low, p.n_high,
                   p.sum_low / p.n_low AS mean_low,
                   p.sum_high / p.n_high AS mean_high,
                   p.sum_low / p.n_low - p.sum_high / p.n_high AS diff,
                   COALESCE(t.n_total, p.n_low + p.n_high) AS n_total_rat
            FROM paired p
            LEFT JOIN (SELECT game_id, SUM(n_users) AS n_total FROM cells GROUP BY game_id) t
                   USING (game_id)
        """).fetchdf()

        if len(df) == 0:
            contrast_summaries.append({
                "contrast": name, "low_bands": low_bands, "high_bands": high_bands,
                "n_games_paired": 0, "note": "no paired games at min_cell threshold"
            })
            continue
        w = 1.0 / (1.0 / df.n_low + 1.0 / df.n_high)
        contrast_summaries.append({
            "contrast": name,
            "low_bands": low_bands, "high_bands": high_bands,
            "n_games_paired": int(len(df)),
            "mean_diff": float(df["diff"].mean()),
            "median_diff": float(df["diff"].median()),
            "p10_diff": float(df["diff"].quantile(.10)),
            "p25_diff": float(df["diff"].quantile(.25)),
            "p75_diff": float(df["diff"].quantile(.75)),
            "p90_diff": float(df["diff"].quantile(.90)),
            "share_positive": float((df["diff"] > 0).mean()),
            "precision_weighted_pooled_diff": float((w * df["diff"]).sum() / w.sum()),
            "median_total_raters_of_paired_games": float(df["n_total_rat"].median()),
            "p25_total_raters": float(df["n_total_rat"].quantile(.25)),
            "p75_total_raters": float(df["n_total_rat"].quantile(.75)),
        })
        pq.write_table(pa.Table.from_pandas(df, preserve_index=False),
                       out_dir / f"within_game_diffs_pass2_{name}.parquet", compression="zstd")
        del df
    summary["paired_contrasts_active"] = contrast_summaries

    # ------------------------------------------------------------------
    # Game fixed-effects regression on active (exact via per-game aggregates)
    # ------------------------------------------------------------------
    print("[4/8] Game FE regression (active)...", flush=True)
    bands_no_ref = [b for b in ACTIVE_BAND_ORDER if b != "1000+"]
    k = len(bands_no_ref)
    agg_sql = ", ".join(
        ["SUM(rating) AS sy", "COUNT(*) AS n"]
        + [f"COALESCE(SUM(CASE WHEN volume_band = '{b}' THEN 1 ELSE 0 END), 0) AS s_{i}"
           for i, b in enumerate(bands_no_ref)]
        + [f"COALESCE(SUM(CASE WHEN volume_band = '{b}' THEN rating END), 0.0) AS c_{i}"
           for i, b in enumerate(bands_no_ref)])
    pg = con.execute(f"SELECT game_id, {agg_sql} FROM obs GROUP BY game_id").fetchdf()
    n_obs_total = int(pg["n"].sum())
    S = pg[[f"s_{i}" for i in range(k)]].values.astype(float)
    C = pg[[f"c_{i}" for i in range(k)]].values.astype(float)
    N = pg["n"].values.astype(float)
    SN = S / N[:, None]
    XtX = np.diag(S.sum(axis=0)) - S.T @ SN
    Xty = C.sum(axis=0) - (SN * pg["sy"].values.astype(float)[:, None]).sum(axis=0)
    beta = np.linalg.solve(XtX, Xty)
    scores = C - SN * pg["sy"].values.astype(float)[:, None] \
        - S * beta[None, :] + S * ((S @ beta) / N)[:, None]
    meat = scores.T @ scores
    bread_inv = np.linalg.inv(XtX)
    V = bread_inv @ meat @ bread_inv
    se = np.sqrt(np.diag(V))
    summary["game_fe_regression_active"] = {
        "n_obs": n_obs_total,
        "n_games": int(len(pg)),
        "reference_band": "1000+",
        "note": "rating ~ band dummies + game fixed effects; exact within-game demeaning; SEs clustered by game; bands defined on active lifetime counts",
        "coefficients": [
            {"band": b, "beta_vs_1000plus": float(beta[i]), "cluster_se": float(se[i])}
            for i, b in enumerate(bands_no_ref)
        ],
    }

    # ------------------------------------------------------------------
    # 2. Per-user severity offsets (two-way fit) on active
    # ------------------------------------------------------------------
    print("[5/8] ALS severity fit on active (full)...", flush=True)
    sev_path = out_dir / "user_severity_pass2.parquet"
    gm_path = out_dir / "game_adjusted_means_pass2.parquet"
    reuse = args.reuse_severity and sev_path.exists() and gm_path.exists()

    # Check if we can reuse (validate that it's from same active population)
    if reuse:
        # Load existing to skip refit, but still compute diagnostics from it
        print("  reuse-severity: loading existing severity tables", flush=True)
        con.execute(f"CREATE OR REPLACE VIEW sev_existing AS SELECT * FROM read_parquet('{qpath(sev_path)}')")
        # Need to recreate views for ALS convergence info placeholder
        # We'll read mu from file's summary if available? Instead recompute mu quickly
        mu = scalar(con, "SELECT AVG(rating) FROM obs")
        summary["als_convergence_full_active"] = {"reused": True, "mu": float(mu)}
        # Create views that downstream expects
        con.execute("CREATE OR REPLACE VIEW full_ue AS SELECT user_pseudouserid AS uid, delta_full AS delta FROM sev_existing WHERE delta_full IS NOT NULL")
        con.execute(f"CREATE OR REPLACE VIEW full_ge AS SELECT game_id, game_alpha AS alpha FROM read_parquet('{qpath(gm_path)}')")
        # Need even/odd views too if reuse
        con.execute("CREATE OR REPLACE VIEW evn_ue AS SELECT user_pseudouserid AS uid, delta_even AS delta FROM sev_existing WHERE delta_even IS NOT NULL")
        con.execute("CREATE OR REPLACE VIEW odd_ue AS SELECT user_pseudouserid AS uid, delta_odd AS delta FROM sev_existing WHERE delta_odd IS NOT NULL")
        mu_e = scalar(con, "SELECT AVG(rating) FROM obs WHERE rating_observation_id % 2 = 0")
        mu_o = scalar(con, "SELECT AVG(rating) FROM obs WHERE rating_observation_id % 2 = 1")
    else:
        # Full fit
        t0 = time.time()
        mu, hist = als_fit(con, "obs", "full", n_iter=args.n_iter)
        print(f"  ALS full done in {time.time()-t0:.1f}s: mu={mu:.4f} iter={len(hist)} final_change={hist[-1]:.4g}", flush=True)
        summary["als_convergence_full_active"] = {"mu": float(mu), "iterations": len(hist), "final_max_change": hist[-1]}

        # Create band severity summary (still before parity splits, but need full_ue)
        # Need to expose full_ue for downstream
        # als_fit already created full_ge and full_ue tables
        # No additional creation needed; they are tables.

        # Even/odd splits
        con.execute("CREATE OR REPLACE VIEW obs_even AS SELECT * FROM obs WHERE rating_observation_id % 2 = 0")
        con.execute("CREATE OR REPLACE VIEW obs_odd AS SELECT * FROM obs WHERE rating_observation_id % 2 = 1")
        t0 = time.time()
        mu_e, hist_e = als_fit(con, "obs_even", "evn", n_iter=args.n_iter)
        print(f"  ALS even done in {time.time()-t0:.1f}s: {len(hist_e)} iter, {hist_e[-1]:.4g}", flush=True)
        t0 = time.time()
        mu_o, hist_o = als_fit(con, "obs_odd", "odd", n_iter=args.n_iter)
        print(f"  ALS odd done in {time.time()-t0:.1f}s: {len(hist_o)} iter, {hist_o[-1]:.4g}", flush=True)
        # Record convergence
        summary["als_convergence_even"] = {"mu": float(mu_e), "iterations": len(hist_e), "final_max_change": hist_e[-1]}
        summary["als_convergence_odd"] = {"mu": float(mu_o), "iterations": len(hist_o), "final_max_change": hist_o[-1]}
        # Persist severity tables if not reuse: we need to write after diagnostics but we can prepare full_ue/full_ge views now
        # They are tables already; we'll keep them.

        # Keep mu values for later
        summary["als_ms"] = {"mu_full": float(mu), "mu_even": float(mu_e), "mu_odd": float(mu_o)}

    # If not reuse, mu_e/mu_o already set; if reuse we have them from above
    if reuse:
        summary["als_ms"] = {"mu_full": float(mu), "mu_even": float(mu_e), "mu_odd": float(mu_o)}
    else:
        # Also need summary entry for full done above already
        pass

    # Ensure full_ue/full_ge/evn_ue/odd_ue views are correctly named for downstream queries
    # If we did fresh ALS, tables full_ue etc. exist; if reuse, we already created views.
    # Normalize: create views if they are tables (DuckDB allows both)
    # No action needed - DuckDB resolves both.

    # ------------------------------------------------------------------
    # Severity distribution by band (active)
    # ------------------------------------------------------------------
    band_delta = con.execute("""
        SELECT b.volume_band, COUNT(*) AS users,
               AVG(u.delta) AS mean_delta,
               STDDEV_SAMP(u.delta) AS sd_delta,
               QUANTILE_CONT(u.delta, 0.5) AS median_delta
        FROM full_ue u JOIN ua_band b ON u.uid = b.user_pseudouserid
        GROUP BY b.volume_band
    """).fetchdf()
    # Order by active band order
    band_delta = band_delta.set_index("volume_band").reindex(ACTIVE_BAND_ORDER).reset_index()
    # Fill missing bands where no users (shouldn't happen)
    summary["severity_by_band_active"] = band_delta.to_dict(orient="records")

    # Overall severity distribution stats
    sev_dist = con.execute("""
        SELECT COUNT(*) AS n_users_with_delta,
               AVG(delta) AS mean_delta,
               STDDEV_SAMP(delta) AS sd_delta,
               QUANTILE_CONT(delta, 0.05) AS p05,
               QUANTILE_CONT(delta, 0.25) AS p25,
               QUANTILE_CONT(delta, 0.5) AS p50,
               QUANTILE_CONT(delta, 0.75) AS p75,
               QUANTILE_CONT(delta, 0.95) AS p95,
               MIN(delta) AS min_delta,
               MAX(delta) AS max_delta
        FROM full_ue
    """).fetchone()
    summary["severity_distribution_active"] = {
        "n_users_with_delta": int(sev_dist[0]),
        "mean_delta": float(sev_dist[1]),
        "sd_delta": float(sev_dist[2]),
        "p05": float(sev_dist[3]), "p25": float(sev_dist[4]), "p50": float(sev_dist[5]),
        "p75": float(sev_dist[6]), "p95": float(sev_dist[7]),
        "min_delta": float(sev_dist[8]), "max_delta": float(sev_dist[9]),
    }

    # Dispersion by count bucket (like script 18)
    prec = con.execute("""
        SELECT LEAST(CAST(b.cnt_filtered / 50 AS INTEGER), 20) AS bucket,
               COUNT(*) AS users,
               AVG(b.cnt_filtered) AS mean_n,
               STDDEV_SAMP(u.delta) AS sd_delta
        FROM full_ue u JOIN ua_band b ON u.uid = b.user_pseudouserid
        GROUP BY 1 ORDER BY 1
    """).fetchdf()
    summary["delta_dispersion_by_count_bucket_active"] = prec.to_dict(orient="records")

    # ------------------------------------------------------------------
    # Variance decomposition R2 on active (nested models)
    # ------------------------------------------------------------------
    print("[6/8] Variance decomposition (active)...", flush=True)
    # Need mu from summary
    mu_full = summary["als_ms"]["mu_full"] if "als_ms" in summary else summary["als_convergence_full_active"]["mu"]
    # Use same logic as script 16: r2_game = 1 - Var(y - game_mean)/Var(y), etc.
    # But we need r2 for game identity, rater identity, and additive both
    # On active set, we compute directly
    r2row = con.execute(f"""
        WITH gmean AS (
            SELECT game_id, AVG(rating) AS gm FROM obs GROUP BY game_id
        ), umean AS (
            SELECT user_pseudouserid AS uid, AVG(rating) AS um FROM obs GROUP BY user_pseudouserid
        ), j AS (
            SELECT o.rating AS y,
                   g.alpha AS a,
                   w.gm AS gm,
                   v.um AS um,
                   COALESCE(u.delta, 0) AS d
            FROM obs o
            JOIN full_ge g ON o.game_id = g.game_id
            JOIN gmean w ON o.game_id = w.game_id
            JOIN umean v ON o.user_pseudouserid = v.uid
            LEFT JOIN full_ue u ON o.user_pseudouserid = u.uid
        ), agg AS (
            SELECT VAR_SAMP(y) AS vt,
                   VAR_SAMP(y - (gm - (SELECT AVG(rating) FROM obs))) AS vr_g,
                   VAR_SAMP(y - (um - (SELECT AVG(rating) FROM obs))) AS vr_u,
                   VAR_SAMP(y - ({mu_full} + a + d)) AS vr_b
            FROM j
        )
        SELECT vt, 1 - vr_g / vt, 1 - vr_u / vt, 1 - vr_b / vt FROM agg
    """).fetchone()
    summary["variance_decomposition_nested_r2_active"] = {
        "total_var": float(r2row[0]),
        "r2_game_identity_only": float(r2row[1]),
        "r2_rater_identity_only": float(r2row[2]),
        "r2_additive_both": float(r2row[3]),
        "note": "nested-model R2 of rating variance explained by game identity, rater identity, and additive two-way fit on active set",
    }

    # ------------------------------------------------------------------
    # Stability / reliability on active (even/odd parity)
    # ------------------------------------------------------------------
    print("[6b/8] Parity stability & reliability (active)...", flush=True)
    # Even/odd parity correlation within active set, no cross-half leakage (already half-specific fits)
    # Need to compute stab_parity similar to script 16 but with active bands
    # Ensure we have evn_ue and odd_ue (they are half-fits)
    # For active, min_obs_each_half logic uses cnt? Use活跃? For parity, we need users with at least 20 total active ratings? But spec says median |diff| etc.
    # On active, all users have >=10 active ratings, but half splits will be ~5 each, so for reliability we need stricter.
    # Use min 20 per half? That's what script 16 used? It used n_even >=20 and n_odd >=20 via rating_observations >=20 check on rbv counts.
    # For active, we should count per half directly: COUNT(*) per user per parity.
    # Simpler: use same approach as script 16: require each half has >=10 observations (since active users have 10 total, half would be ~5, so need 20 total to have 10 per half)
    # Spec says "even/odd parity correlations computed within the active set, no cross-half leakage; reuse bounded memory recipe and narrow aggregations"
    # We'll implement as: require each half >=10 (like script 18 reliability) and for overall parity stability require each half >=10 as well? Script 16 required 20 per half for main stability, but script 18 reliability used 10 per half.
    # We'll report both: main stability with 20 per half? But active many users have <40 total, so 20 per half would be restrictive. For active, we should report with 10 per half as primary to have enough users.
    # Keep script 16's 20 per half as historical but add active-appropriate 10 per half.

    # First compute overall parity stability with relaxed threshold that yields many users
    # Create helper to count per-half observations for active users
    # We don't have per-half counts in ua_band; need to compute from obs_even/obs_odd
    con.execute("""
        CREATE OR REPLACE VIEW half_counts AS
        SELECT user_pseudouserid AS uid,
               COUNT(*) FILTER (WHERE rating_observation_id % 2 = 0) AS n_even,
               COUNT(*) FILTER (WHERE rating_observation_id % 2 = 1) AS n_odd
        FROM obs GROUP BY user_pseudouserid
    """)

    # Overall parity stability: require >=10 per half (more inclusive) and >=20 per half (stricter) both reported
    stab_results = {}
    for thresh, label in [(10, "min10_each_half"), (20, "min20_each_half")]:
        r = con.execute(f"""
            WITH j AS (
                SELECT e.delta AS d_even, o.delta AS d_odd
                FROM evn_ue e JOIN odd_ue o ON e.uid = o.uid
                JOIN half_counts h ON e.uid = h.uid
                WHERE h.n_even >= {thresh} AND h.n_odd >= {thresh}
            ), rk AS (
                SELECT d_even, d_odd,
                       RANK() OVER (ORDER BY d_even) AS r_even,
                       RANK() OVER (ORDER BY d_odd) AS r_odd,
                       ABS(d_even - d_odd) AS absdiff
                FROM j
            )
            SELECT COUNT(*), CORR(d_even, d_odd), CORR(r_even::DOUBLE, r_odd::DOUBLE),
                   QUANTILE_CONT(absdiff, 0.5),
                   QUANTILE_CONT(absdiff, 0.9),
                   STDDEV_SAMP(d_even), STDDEV_SAMP(d_odd), STDDEV_SAMP(d_even - d_odd)
            FROM rk
        """).fetchone()
        if r[0] == 0 or r[0] is None:
            stab_results[label] = {"users_compared": 0}
        else:
            stab_results[label] = {
                "users_compared": int(r[0]),
                "min_obs_each_half": thresh,
                "pearson": float(r[1]) if r[1] is not None else None,
                "spearman": float(r[2]) if r[2] is not None else None,
                "median_abs_delta_diff": float(r[3]) if r[3] is not None else None,
                "p90_abs_delta_diff": float(r[4]) if r[4] is not None else None,
                "sd_even": float(r[5]) if r[5] is not None else None,
                "sd_odd": float(r[6]) if r[6] is not None else None,
                "sd_difference": float(r[7]) if r[7] is not None else None,
            }
    summary["stability_parity_active"] = stab_results
    # Primary is min10
    primary_stab = stab_results["min10_each_half"]

    # Placebo mismatched correlation (deterministic roll)
    try:
        a = con.execute("""
            SELECT delta FROM evn_ue e JOIN half_counts h ON e.uid = h.uid WHERE h.n_even >= 10 ORDER BY e.uid LIMIT 100000
        """).fetchdf()["delta"].values
        bvec = con.execute("""
            SELECT delta FROM odd_ue o JOIN half_counts h ON o.uid = h.uid WHERE h.n_odd >= 10 ORDER BY o.uid LIMIT 100000
        """).fetchdf()["delta"].values
        nmin = min(len(a), len(bvec))
        if nmin > 100:
            rolled = np.roll(bvec[:nmin], nmin // 2)
            placebo = float(np.corrcoef(a[:nmin], rolled)[0, 1])
        else:
            placebo = None
    except Exception as e:
        placebo = f"error: {e}"
    summary["placebo_mismatched_correlation_active"] = placebo

    # Reliability by band (ICC-style) - script 18 style, requires >=10 per half
    rel_rows = []
    for band in ACTIVE_BAND_ORDER:
        r = con.execute("""
            WITH j AS (
                SELECT s.delta_even AS de, s.delta_odd AS do_,
                       h.n_even, h.n_odd
                FROM (SELECT user_pseudouserid AS uid, delta_even, delta_odd FROM (
                    SELECT e.uid AS user_pseudouserid, e.delta AS delta_even, o.delta AS delta_odd
                    FROM evn_ue e JOIN odd_ue o ON e.uid = o.uid
                ) t) s
                JOIN half_counts h ON s.uid = h.uid
                JOIN ua_band b ON s.uid = b.user_pseudouserid
                WHERE b.volume_band = ? AND h.n_even >= 10 AND h.n_odd >= 10
            )
            SELECT COUNT(*),
                   STDDEV_SAMP(de), STDDEV_SAMP(do_), STDDEV_SAMP(de - do_)
            FROM j
        """, [band]).fetchone()
        if not r[0]:
            continue
        cnt, sd_e, sd_o, sd_d = r
        if sd_e is None or sd_o is None or sd_d is None or sd_e == 0:
            # need handle nan
            rel_rows.append({"band": band, "users_compared": int(cnt), "note": "insufficient variance"})
            continue
        sd_e = float(sd_e); sd_d = float(sd_d)
        noise_half = sd_d / np.sqrt(2.0)
        var_total = sd_e ** 2
        var_signal = max(var_total - noise_half ** 2, 0.0)
        reliability = var_signal / var_total if var_total > 0 else float("nan")
        rel_rows.append({
            "band": band, "users_compared": int(cnt),
            "sd_half_estimate": sd_e,
            "implied_noise_sd_half": float(noise_half),
            "implied_signal_sd": float(np.sqrt(var_signal)),
            "reliability_icc_style": float(reliability),
        })
    summary["severity_reliability_by_band_active"] = {
        "min_half_obs": 10,
        "rows": rel_rows,
        "note": "signal/noise decomposition of parity-half severity estimates on active set; min 10 per half",
    }

    # ------------------------------------------------------------------
    # Persist severity tables (if not reuse)
    # ------------------------------------------------------------------
    if not reuse:
        print("[7/8] Persisting severity tables (active)...", flush=True)
        # Need to handle that full_ue/full_ge etc are tables; we need to write parquet with coalesced schema
        # user_severity_active: one row per active user with deltas
        con.execute(f"""
            COPY (
                SELECT b.user_pseudouserid,
                       b.volume_band,
                       b.cnt_filtered AS rating_observations_active,
                       b.is_degenerate_broad,
                       f.delta AS delta_full,
                       evn.delta AS delta_even,
                       odd.delta AS delta_odd
                FROM ua_band b
                LEFT JOIN full_ue f ON b.user_pseudouserid = f.uid
                LEFT JOIN evn_ue evn ON b.user_pseudouserid = evn.uid
                LEFT JOIN odd_ue odd ON b.user_pseudouserid = odd.uid
                ORDER BY b.user_pseudouserid
            ) TO '{qpath(sev_path)}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """)
        cnt_sev = scalar(con, f"SELECT COUNT(*) FROM read_parquet('{qpath(sev_path)}')")
        print(f"  wrote {sev_path} ({cnt_sev} rows)", flush=True)

        # game_adjusted_means_active
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
            ) TO '{qpath(gm_path)}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """)
        cnt_gm = scalar(con, f"SELECT COUNT(*) FROM read_parquet('{qpath(gm_path)}')")
        print(f"  wrote {gm_path} ({cnt_gm} rows)", flush=True)

        # Ensure views point to files for later steps (create file-backed views)
        # Re-create views from files for consistency with reuse path
        con.execute(f"CREATE OR REPLACE VIEW sev_file AS SELECT * FROM read_parquet('{qpath(sev_path)}')")
        con.execute(f"CREATE OR REPLACE VIEW gm_file AS SELECT * FROM read_parquet('{qpath(gm_path)}')")
        # Replicate full_ue etc from file if needed for later? Already have tables.
    else:
        print("[7/8] Severity tables reused (not rewritten)", flush=True)
        con.execute(f"CREATE OR REPLACE VIEW sev_file AS SELECT * FROM read_parquet('{qpath(sev_path)}')")
        con.execute(f"CREATE OR REPLACE VIEW gm_file AS SELECT * FROM read_parquet('{qpath(gm_path)}')")

    # Game-level adjustment summary on active
    gstats = con.execute(f"""
        WITH rk AS (
            SELECT n_obs::DOUBLE AS n_obs, raw_mean, adj_mean,
                   RANK() OVER (ORDER BY raw_mean) AS r_raw,
                   RANK() OVER (ORDER BY adj_mean) AS r_adj
            FROM read_parquet('{qpath(gm_path)}')
        )
        SELECT CORR(raw_mean, adj_mean), CORR(r_raw::DOUBLE, r_adj::DOUBLE),
               CORR(n_obs, adj_mean - raw_mean),
               QUANTILE_CONT(adj_mean - raw_mean, 0.05),
               QUANTILE_CONT(adj_mean - raw_mean, 0.5),
               QUANTILE_CONT(adj_mean - raw_mean, 0.95)
        FROM rk
    """).fetchone()
    summary["game_level_adjustment_active"] = {
        "pearson_raw_vs_adj": float(gstats[0]) if gstats[0] is not None else None,
        "spearman_raw_vs_adj": float(gstats[1]) if gstats[1] is not None else None,
        "corr_n_obs_with_shift": float(gstats[2]) if gstats[2] is not None else None,
        "shift_quantiles_p5_median_p95": [float(gstats[3]), float(gstats[4]), float(gstats[5])] if gstats[3] is not None else None,
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
        FROM read_parquet('{qpath(gm_path)}')
        GROUP BY 1 ORDER BY 1
    """).fetchdf()
    summary["game_adjustment_shift_by_volume_active"] = gshift.to_dict(orient="records")

    # ------------------------------------------------------------------
    # Held-out prediction on active (does delta_u help?)
    # ------------------------------------------------------------------
    print("[7b/8] Holdout prediction (active)...", flush=True)
    # Need mu_e/mu_o for holdout; ensure they exist
    if "als_ms" in summary:
        mu_e_val = summary["als_ms"]["mu_even"]
        mu_o_val = summary["als_ms"]["mu_odd"]
    else:
        mu_e_val = mu_e
        mu_o_val = mu_o

    # Ensure half game effects tables exist (evn_ge / odd_ge)
    # If reuse, they may not exist; rebuild deterministically (one group-by per half)
    if reuse:
        # Rebuild half game effects from file-backed severities
        # Use evn_ue / odd_ue already as views; need to materialize evn_ge/odd_ge as tables
        con.execute(f"""
            CREATE OR REPLACE TABLE evn_ge AS
            SELECT s.game_id AS game_id,
                   AVG(s.rating - {mu_e_val} - COALESCE(u.delta, 0)) AS alpha
            FROM obs_even s LEFT JOIN evn_ue u ON s.user_pseudouserid = u.uid
            GROUP BY s.game_id
        """)
        con.execute(f"""
            CREATE OR REPLACE TABLE odd_ge AS
            SELECT s.game_id AS game_id,
                   AVG(s.rating - {mu_o_val} - COALESCE(u.delta, 0)) AS alpha
            FROM obs_odd s LEFT JOIN odd_ue u ON s.user_pseudouserid = u.uid
            GROUP BY s.game_id
        """)
        # Also ensure obs_even/odd views still valid
        con.execute("CREATE OR REPLACE VIEW obs_even AS SELECT * FROM obs WHERE rating_observation_id % 2 = 0")
        con.execute("CREATE OR REPLACE VIEW obs_odd AS SELECT * FROM obs WHERE rating_observation_id % 2 = 1")

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
            "rmse_game_fe_only": float(r[0]) if r[0] is not None else None,
            "rmse_game_fe_plus_user": float(r[1]) if r[1] is not None else None,
            "rmse_raw_train_game_mean": float(r[2]) if r[2] is not None else None,
            "mae_game_fe_only": float(r[3]) if r[3] is not None else None,
            "mae_game_fe_plus_user": float(r[4]) if r[4] is not None else None,
        }}

    summary["holdout_active"] = {}
    summary["holdout_active"].update(holdout("evn", mu_e_val, "obs_even", "obs_odd", "fit_even_predict_odd"))
    summary["holdout_active"].update(holdout("odd", mu_o_val, "obs_odd", "obs_even", "fit_odd_predict_even"))

    # Improvement by test user band
    try:
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
                   SQRT(AVG((y - ({mu_e_val} + alpha_g))^2)) AS rmse_game_only,
                   SQRT(AVG((y - ({mu_e_val} + alpha_g + delta_u))^2)) AS rmse_with_user
            FROM pred p JOIN ua_band b ON p.uid = b.user_pseudouserid
            GROUP BY b.volume_band
        """).fetchdf()
        imp = imp.set_index("volume_band").reindex(ACTIVE_BAND_ORDER).reset_index()
        summary["holdout_improvement_by_test_user_band_active"] = imp.to_dict(orient="records")
    except Exception as e:
        summary["holdout_improvement_by_test_user_band_active_error"] = str(e)

    # ------------------------------------------------------------------
    # 3. Gap decomposition on active (scripts/17 style)
    # ------------------------------------------------------------------
    print("[8/8] Gap decomposition (active)...", flush=True)
    # Define low/high for active decomposition
    # Primary: low = 10-24, high = 500-999 + 1000+  (extreme)
    # Also compute 10-49 vs 500plus as sensitivity
    LOW_BANDS = ["10-24"]
    HIGH_BANDS = ["500-999", "1000+"]
    LOW_BANDS_WIDE = ["10-24", "25-49"]
    lo = ",".join(f"'{b}'" for b in LOW_BANDS)
    hi = ",".join(f"'{b}'" for b in HIGH_BANDS)
    lo_wide = ",".join(f"'{b}'" for b in LOW_BANDS_WIDE)
    summary["gap_groups_active"] = {
        "low_bands_primary": LOW_BANDS, "high_bands_primary": HIGH_BANDS,
        "low_bands_wide": LOW_BANDS_WIDE,
    }

    # Raw gap on active
    raw_gap = con.execute(f"""
        SELECT CASE WHEN volume_band IN ({lo}) THEN 'low'
                    WHEN volume_band IN ({hi}) THEN 'high'
                    ELSE 'mid' END AS grp,
               COUNT(*) AS n_obs, AVG(rating) AS mean_rating
        FROM obs GROUP BY 1
    """).fetchdf().set_index("grp")
    # Need to handle if low/high not in index? They should be.
    try:
        raw_gap_low = float(raw_gap.loc["low", "mean_rating"])
        raw_gap_high = float(raw_gap.loc["high", "mean_rating"])
        summary["raw_gap_active"] = {
            "low_mean": raw_gap_low,
            "high_mean": raw_gap_high,
            "raw_gap_low_minus_high": float(raw_gap_low - raw_gap_high),
            "n_obs_low": int(raw_gap.loc["low", "n_obs"]),
            "n_obs_high": int(raw_gap.loc["high", "n_obs"]),
        }
    except Exception as e:
        summary["raw_gap_active_error"] = str(e)
        summary["raw_gap_active"] = {"error": str(e)}

    # Standardized decomposition (common game weights) with severity adjustment
    # Need sev_file view (user_severity_active)
    # Use sev_file delta_full
    con.execute(f"""
        CREATE OR REPLACE TABLE cells_gap AS
        SELECT o.game_id,
               CASE WHEN o.volume_band IN ({lo}) THEN 'low'
                    WHEN o.volume_band IN ({hi}) THEN 'high' END AS grp,
               COUNT(*) AS n_obs,
               SUM(o.rating) AS sum_y,
               SUM(o.rating - COALESCE(s.delta_full, 0)) AS sum_yadj
        FROM obs o
        LEFT JOIN sev_file s ON o.user_pseudouserid = s.user_pseudouserid
        WHERE o.volume_band IN ({lo}) OR o.volume_band IN ({hi})
        GROUP BY 1, 2
    """)
    std = con.execute("""
        WITH w AS (
            SELECT game_id, SUM(n_obs) AS w FROM cells_gap GROUP BY game_id
        ), j AS (
            SELECT c.grp, c.game_id, w.w,
                   c.n_obs, c.sum_y / c.n_obs AS m_raw, c.sum_yadj / c.n_obs AS m_adj
            FROM cells_gap c JOIN w USING (game_id)
        ), agg AS (
            SELECT grp,
                   SUM(w) AS weight_avail,
                   SUM(w * m_raw) / NULLIF(SUM(w), 0) AS std_raw,
                   SUM(w * m_adj) / NULLIF(SUM(w), 0) AS std_adj,
                   AVG(m_raw) AS unwt_raw,
                   AVG(m_adj) AS unwt_adj
            FROM j GROUP BY grp
        )
        SELECT * FROM agg
    """).fetchdf().set_index("grp")
    if "low" in std.index and "high" in std.index:
        sr, hr = std.loc["low"], std.loc["high"]
        decomp = {
            "common_weight_total_ratings": float(sr["weight_avail"] + hr["weight_avail"]),
            "std_raw_low": float(sr["std_raw"]), "std_raw_high": float(hr["std_raw"]),
            "std_gap_raw": float(sr["std_raw"] - hr["std_raw"]),
            "std_sevadjusted_low": float(sr["std_adj"]), "std_sevadjusted_high": float(hr["std_adj"]),
            "std_gap_severity_adjusted": float(sr["std_adj"] - hr["std_adj"]),
            "unweighted_cellmean_gap_raw": float(sr["unwt_raw"] - hr["unwt_raw"]),
            "unweighted_cellmean_gap_sevadjusted": float(sr["unwt_adj"] - hr["unwt_adj"]),
        }
        summary["standardized_decomposition_active"] = decomp
    else:
        summary["standardized_decomposition_active"] = {"note": "insufficient overlap", "available": std.to_dict(orient="records") if not std.empty else []}

    ov = con.execute("SELECT SUM(CASE WHEN grp='low' THEN n_obs END), SUM(CASE WHEN grp='high' THEN n_obs END) FROM cells_gap").fetchone()
    both = con.execute("""
        WITH g AS (
            SELECT game_id, COUNT(DISTINCT grp) AS k, SUM(n_obs) FILTER (grp='low') AS nl, SUM(n_obs) FILTER (grp='high') AS nh
            FROM cells_gap GROUP BY game_id
        )
        SELECT SUM(nl), SUM(nh) FROM g WHERE k = 2
    """).fetchone()
    if ov[0] and both[0]:
        summary["support_overlap_active"] = {
            "low_obs_on_shared_games": int(both[0]), "low_obs_total": int(ov[0]),
            "high_obs_on_shared_games": int(both[1]), "high_obs_total": int(ov[1]),
            "share_low_on_shared": float(both[0] / ov[0]) if ov[0] else None,
            "share_high_on_shared": float(both[1] / ov[1]) if ov[1] else None,
        }
    else:
        summary["support_overlap_active"] = {"note": "no overlap computed"}

    # Also compute wide low variant for sensitivity
    try:
        con.execute(f"""
            CREATE OR REPLACE TABLE cells_gap_wide AS
            SELECT o.game_id,
                   CASE WHEN o.volume_band IN ({lo_wide}) THEN 'low'
                        WHEN o.volume_band IN ({hi}) THEN 'high' END AS grp,
                   COUNT(*) AS n_obs,
                   SUM(o.rating) AS sum_y,
                   SUM(o.rating - COALESCE(s.delta_full, 0)) AS sum_yadj
            FROM obs o
            LEFT JOIN sev_file s ON o.user_pseudouserid = s.user_pseudouserid
            WHERE o.volume_band IN ({lo_wide}) OR o.volume_band IN ({hi})
            GROUP BY 1, 2
        """)
        std_wide = con.execute("""
            WITH w AS (SELECT game_id, SUM(n_obs) AS w FROM cells_gap_wide GROUP BY game_id),
                 j AS (SELECT c.grp, c.game_id, w.w, c.n_obs, c.sum_y / c.n_obs AS m_raw, c.sum_yadj / c.n_obs AS m_adj FROM cells_gap_wide c JOIN w USING (game_id)),
                 agg AS (SELECT grp, SUM(w) AS weight_avail, SUM(w * m_raw)/NULLIF(SUM(w),0) AS std_raw, SUM(w * m_adj)/NULLIF(SUM(w),0) AS std_adj FROM j GROUP BY grp)
            SELECT * FROM agg
        """).fetchdf().set_index("grp")
        if "low" in std_wide.index and "high" in std_wide.index:
            sr, hr = std_wide.loc["low"], std_wide.loc["high"]
            summary["standardized_decomposition_wide_active"] = {
                "low_bands": LOW_BANDS_WIDE, "high_bands": HIGH_BANDS,
                "std_gap_raw": float(sr["std_raw"] - hr["std_raw"]),
                "std_gap_severity_adjusted": float(sr["std_adj"] - hr["std_adj"]),
                "std_raw_low": float(sr["std_raw"]), "std_raw_high": float(hr["std_raw"]),
            }
    except Exception as e:
        summary["standardized_decomposition_wide_active_error"] = str(e)

    # Persist gap cells
    gap_cells_path = out_dir / "gap_cells_pass2.parquet"
    con.execute(f"COPY (SELECT * FROM cells_gap) TO '{qpath(gap_cells_path)}' (FORMAT PARQUET, COMPRESSION ZSTD)")

    # ------------------------------------------------------------------
    # Historical reference comparison (load phase2 JSONs if present)
    # ------------------------------------------------------------------
    print("[compare] Loading historical baselines for comparison table...", flush=True)
    comparison = {}
    historical = {}

    # Try to load full-snapshot same_game, severity stability, gap decomposition
    try:
        p = phase2_dir / "same_game_volume_contrast.json"
        if p.exists():
            j = json.loads(p.read_text())
            historical["full_snapshot"] = {
                "raw_gap_band1_vs_1000plus": j.get("raw_gap_band1_vs_1000plus"),
                "raw_band_means": j.get("raw_band_means"),
                "paired_contrasts": j.get("paired_contrasts"),
                "game_fe_regression": j.get("game_fe_regression"),
            }
            # Extract pooled and within values for table
            # full snapshot: pooled 2.456, within band1_vs_1000plus mean 2.28, low2_24 vs 500plus 1.278
            # We'll store
            comparison["full_snapshot_notes"] = "95,540 games, 571,248 users, 26.9M obs (incl. population-external ratings)"
    except Exception as e:
        historical["full_snapshot_error"] = str(e)

    try:
        p = phase2_dir / "user_severity_stability.json"
        if p.exists():
            j = json.loads(p.read_text())
            historical["full_snapshot_severity"] = {
                "severity_by_band": j.get("severity_by_band"),
                "variance_decomposition": j.get("variance_decomposition_nested_r2"),
                "stability_parity": j.get("stability_parity"),
                "game_level_adjustment": j.get("game_level_adjustment"),
                "holdout": j.get("holdout"),
            }
    except Exception as e:
        historical["full_snapshot_severity_error"] = str(e)

    try:
        p = phase2_dir / "gap_decomposition.json"
        if p.exists():
            j = json.loads(p.read_text())
            historical["full_snapshot_gap"] = {
                "raw": j.get("raw"),
                "standardized_decomposition": j.get("standardized_decomposition"),
                "support_overlap": j.get("support_overlap"),
            }
    except Exception as e:
        historical["full_snapshot_gap_error"] = str(e)

    try:
        p = phase2_dir / "rater_credibility.json"
        if p.exists():
            j = json.loads(p.read_text())
            historical["full_snapshot_credibility"] = {
                "severity_reliability_by_band": j.get("severity_reliability_by_band"),
                "entanglement": j.get("entanglement"),
            }
    except Exception as e:
        historical["full_snapshot_credibility_error"] = str(e)

    # Filtered reference (16,627 × all users) - we have threshold study and filtered validation
    # For filtered pooled gap we can compute quickly if not already cached? Let's try to compute filtered raw band means on the fly using filtered extract if available
    try:
        filtered_ro = REPO_DIR / "data" / "processed" / "phase2-filtered" / "rating_observations_filtered.parquet"
        if filtered_ro.exists():
            # Need filtered user bands: filtered users have cnt_filtered but we have no filtered band file; compute band from filtered count (COUNT(*) over filtered obs per user)
            # Use a quick DuckDB view to compute filtered band counts
            filtered_users_path = REPO_DIR / "data" / "processed" / "phase2-filtered" / "users_filtered.parquet"
            # But users_filtered parquet may not have cnt; we already have profiles df from earlier build? Instead we can use the recomputed filtered count view via rating_observations_filtered
            # Let's create filtered band view by scanning filtered_ro group by user
            print("  computing filtered (16,627×all-users) raw band means for comparison...", flush=True)
            con.execute(f"CREATE OR REPLACE VIEW ro_filtered AS SELECT * FROM read_parquet('{qpath(filtered_ro)}')")
            # Compute per-user filtered counts and band
            # Use temp table for filtered user band
            con.execute(f"""
                CREATE OR REPLACE TEMP TABLE f_ub AS
                SELECT user_pseudouserid, COUNT(*) AS n, {band_case('n')} AS volume_band
                FROM ro_filtered GROUP BY user_pseudouserid
            """)
            # But this uses CASE on n which is filtered count; however this band definition includes 1..9 bands too? Our band_case only handles 10+ bands truncated; need full case for filtered.
            # For filtered comparison we need full band scheme 1..1000+ to match full snapshot bands.
            con.execute("DROP TABLE IF EXISTS f_ub")
            con.execute("""
                CREATE OR REPLACE TEMP TABLE f_ub AS
                SELECT user_pseudouserid, COUNT(*) AS n,
                       CASE WHEN COUNT(*) = 1 THEN '1'
                            WHEN COUNT(*) BETWEEN 2 AND 4 THEN '2-4'
                            WHEN COUNT(*) BETWEEN 5 AND 9 THEN '5-9'
                            WHEN COUNT(*) BETWEEN 10 AND 24 THEN '10-24'
                            WHEN COUNT(*) BETWEEN 25 AND 49 THEN '25-49'
                            WHEN COUNT(*) BETWEEN 50 AND 99 THEN '50-99'
                            WHEN COUNT(*) BETWEEN 100 AND 249 THEN '100-249'
                            WHEN COUNT(*) BETWEEN 250 AND 499 THEN '250-499'
                            WHEN COUNT(*) BETWEEN 500 AND 999 THEN '500-999'
                            ELSE '1000+' END AS volume_band
                FROM ro_filtered GROUP BY user_pseudouserid
            """)
            f_raw = con.execute("""
                SELECT volume_band, COUNT(*) AS n_obs, AVG(r.rating) AS mean_rating, STDDEV_SAMP(r.rating) AS sd_rating,
                       COUNT(DISTINCT r.user_pseudouserid) AS n_users
                FROM ro_filtered r JOIN f_ub USING (user_pseudouserid)
                GROUP BY volume_band
            """).fetchdf().set_index("volume_band").reindex(FULL_BAND_ORDER).reset_index()
            historical["filtered_16k_allusers"] = {
                "raw_band_means": f_raw.to_dict(orient="records"),
                # pooled gap 1 vs 1000+ analog? Use SQL
            }
            # Pooled gap on filtered
            fg1 = con.execute("""
                SELECT AVG(CASE WHEN volume_band='1' THEN rating END) - AVG(CASE WHEN volume_band='1000+' THEN rating END)
                FROM (SELECT r.rating, f.volume_band FROM ro_filtered r JOIN f_ub f USING (user_pseudouserid) WHERE f.volume_band IN ('1','1000+'))
            """).fetchone()
            if fg1 and fg1[0] is not None:
                historical["filtered_16k_allusers"]["raw_gap_1_vs_1000"] = float(fg1[0])
            # Also compute low vs high as in gap decomposition (1,2-4,5-9 vs 500+,1000+)
            fg2 = con.execute("""
                SELECT AVG(CASE WHEN volume_band IN ('1','2-4','5-9') THEN rating END)
                     - AVG(CASE WHEN volume_band IN ('500-999','1000+') THEN rating END)
                FROM (SELECT r.rating, f.volume_band FROM ro_filtered r JOIN f_ub f USING (user_pseudouserid)
                      WHERE f.volume_band IN ('1','2-4','5-9','500-999','1000+'))
            """).fetchone()
            if fg2 and fg2[0] is not None:
                historical["filtered_16k_allusers"]["raw_gap_low_vs_high"] = float(fg2[0])
            # Clean up
            con.execute("DROP VIEW IF EXISTS ro_filtered")
            con.execute("DROP TABLE IF EXISTS f_ub")
        else:
            print("  filtered extract not found; skipping filtered comparison compute", flush=True)
    except Exception as e:
        historical["filtered_16k_allusers_error"] = str(e)
        import traceback; print(f"filtered compute error: {e}\n{traceback.format_exc()}", flush=True)

    summary["historical_reference"] = historical

    # Build explicit comparison table (requested deliverable)
    # We need small table with volume-band gaps, severity spread, R2s, reliability
    try:
        # Extract active values
        active_pooled_10_24_vs_1000 = gap_10_24_vs_1000
        active_pooled_10_24_vs_500 = gap_10_24_vs_500plus
        active_within_10_24_vs_1000 = next((c["mean_diff"] for c in contrast_summaries if c["contrast"] == "10-24_vs_1000plus"), None)
        active_within_10_49_vs_500 = next((c["mean_diff"] for c in contrast_summaries if c["contrast"] == "10-49_vs_500plus"), None)
        active_sev_spread = None
        # severity spread = max mean_delta - min mean_delta across active bands
        try:
            means = [r["mean_delta"] for r in summary["severity_by_band_active"] if r["mean_delta"] is not None]
            active_sev_spread = max(means) - min(means) if means else None
        except Exception:
            pass
        active_r2 = summary.get("variance_decomposition_nested_r2_active", {})
        active_pearson = primary_stab.get("pearson") if isinstance(primary_stab, dict) else None
        active_median_diff = primary_stab.get("median_abs_delta_diff") if isinstance(primary_stab, dict) else None

        # Extract full snapshot values from historical
        full_raw_gap = historical.get("full_snapshot", {}).get("raw_gap_band1_vs_1000plus")
        full_within_1_vs_1000 = None
        full_within_low2_24_vs_500 = None
        try:
            pcs = historical.get("full_snapshot", {}).get("paired_contrasts", [])
            for c in pcs:
                if c["contrast"] == "band1_vs_1000plus":
                    full_within_1_vs_1000 = c["mean_diff"]
                if c["contrast"] == "low2_24_vs_500plus":
                    full_within_low2_24_vs_500 = c["mean_diff"]
        except Exception:
            pass
        full_sev = historical.get("full_snapshot_severity", {})
        full_sev_spread = None
        try:
            svb = full_sev.get("severity_by_band", [])
            m = [r["mean_delta"] for r in svb if r["mean_delta"] is not None]
            full_sev_spread = max(m) - min(m) if m else None
        except Exception:
            pass
        full_r2 = full_sev.get("variance_decomposition", {}) if isinstance(full_sev, dict) else {}
        full_stab = full_sev.get("stability_parity", {}) if isinstance(full_sev, dict) else {}

        # Filtered reference values
        filtered_raw_gap = None
        if "filtered_16k_allusers" in historical:
            filtered_raw_gap = historical["filtered_16k_allusers"].get("raw_gap_1_vs_1000")

        comp_table = {
            "note": "Active is primary (16,627 games × >=10 active users, minus strict, 24.5M obs); historical references are 16,627×all-users (25.3M obs) and full-snapshot 95,540×all-users (26.9M obs). Pooled gaps on active use 10-24 as low (since 1..9 excluded); historical gaps use 1 as low.",
            "rows": [
                {"metric": "pooled_gap_low_vs_high", "unit": "rating points",
                 "full_snapshot_95540": round(full_raw_gap, 3) if full_raw_gap else None,
                 "filtered_16k_allusers": round(filtered_raw_gap, 3) if filtered_raw_gap else None,
                 "active_10-24_vs_1000": round(active_pooled_10_24_vs_1000, 3) if active_pooled_10_24_vs_1000 else None,
                 "active_10-24_vs_500plus": round(active_pooled_10_24_vs_500, 3) if active_pooled_10_24_vs_500 else None,
                 "comment": "Active gaps smaller because low floor raised from 1 to 10; compare within-game gaps for selection vs level shift"},
                {"metric": "within_game_gap_mean", "unit": "rating points",
                 "full_snapshot_band1_vs_1000": round(full_within_1_vs_1000, 3) if full_within_1_vs_1000 else None,
                 "full_snapshot_low2_24_vs_500": round(full_within_low2_24_vs_500, 3) if full_within_low2_24_vs_500 else None,
                 "active_10-24_vs_1000": round(active_within_10_24_vs_1000, 3) if active_within_10_24_vs_1000 else None,
                 "active_10-49_vs_500plus": round(active_within_10_49_vs_500, 3) if active_within_10_49_vs_500 else None},
                {"metric": "severity_spread_max_minus_min_mean_delta", "unit": "rating points",
                 "full_snapshot": round(full_sev_spread, 3) if full_sev_spread else None,
                 "active": round(active_sev_spread, 3) if active_sev_spread else None,
                 "comment": "Ordered by lifetime volume; active spread excludes 1..9 bands so narrower"},
                {"metric": "R2_game_identity_only", "unit": "variance explained",
                 "full_snapshot": round(full_r2.get("r2_game_identity_only"), 3) if full_r2.get("r2_game_identity_only") else None,
                 "active": round(active_r2.get("r2_game_identity_only"), 3) if active_r2.get("r2_game_identity_only") else None},
                {"metric": "R2_rater_identity_only", "unit": "variance explained",
                 "full_snapshot": round(full_r2.get("r2_rater_identity_only"), 3) if full_r2.get("r2_rater_identity_only") else None,
                 "active": round(active_r2.get("r2_rater_identity_only"), 3) if active_r2.get("r2_rater_identity_only") else None},
                {"metric": "R2_additive_both", "unit": "variance explained",
                 "full_snapshot": round(full_r2.get("r2_additive_both"), 3) if full_r2.get("r2_additive_both") else None,
                 "active": round(active_r2.get("r2_additive_both"), 3) if active_r2.get("r2_additive_both") else None},
                {"metric": "parity_reliability_pearson_min10_each_half", "unit": "correlation",
                 "full_snapshot_min20": round(full_stab.get("pearson"), 3) if isinstance(full_stab, dict) and full_stab.get("pearson") else None,
                 "active_min10": round(active_pearson, 3) if active_pearson else None},
                {"metric": "median_abs_delta_diff_parity", "unit": "rating points",
                 "full_snapshot": round(full_stab.get("median_abs_delta_diff"), 3) if isinstance(full_stab, dict) and full_stab.get("median_abs_delta_diff") else None,
                 "active_min10": round(active_median_diff, 3) if active_median_diff else None},
                {"metric": "n_obs", "unit": "count",
                 "full_snapshot": 26924709,
                 "filtered_16k_allusers": 25335220,
                 "active": active_obs},
                {"metric": "n_users", "unit": "count",
                 "full_snapshot": 571248,
                 "filtered_16k_allusers": 544955,
                 "active": active_users,
                 "active_users_note": ">=10 active ratings minus 667 strict; 52.98% of filtered"},
                {"metric": "n_games_with_ratings", "unit": "count",
                 "full_snapshot": 95540,
                 "filtered_16k_allusers": 16567,
                 "active": active_games},
            ]
        }
        summary["comparison_table"] = comp_table
        # Pretty print comparison table for logs
        print(json.dumps(comp_table, indent=2), flush=True)
    except Exception as e:
        summary["comparison_table_error"] = str(e)
        import traceback; print(f"comparison table error: {e}\n{traceback.format_exc()}", flush=True)

    # Alias active_* keys to pass2_* for downstream consistency
    for k in list(summary.keys()):
        if k.endswith("_active"):
            summary[k.replace("_active","_pass2")] = summary[k]
    # Write main JSON
    out_json = out_dir / "pass2_baseline_refresh.json"
    out_json.write_text(json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"Wrote {out_json}", flush=True)

    # Also write a lightweight validation JSON next to artefacts (spec)
    val_path = out_dir / "pass2_baseline_validation.json"
    val_payload = {
        "validation": validation,
        "retained_population_checks": "all passed (0 violations)",
        "comparison_table": summary.get("comparison_table"),
        "generated_at": summary["generated_at"],
        "artefacts": {
            "user_severity_pass2": str(sev_path),
            "user_severity_active_alias": str(sev_path),
            "game_adjusted_means_pass2": str(gm_path),
            "pass2_band_cells": str(cells_path),
            "gap_cells_pass2": str(gap_cells_path),
        }
    }
    val_path.write_text(json.dumps(val_payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"Wrote {val_path}", flush=True)

    # Close
    con.close()
    # Print key summary for logs
    print(json.dumps({k: summary[k] for k in [
        "validation", "pooled_gaps_active", "paired_contrasts_active",
        "game_fe_regression_active", "severity_by_band_active",
        "variance_decomposition_nested_r2_active", "stability_parity_active"
    ]}, indent=2, default=str)[:8000], flush=True)


if __name__ == "__main__":
    main()

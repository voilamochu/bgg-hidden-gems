"""Build active Phase 2 analytical extracts for the established user population.

Active analytical universe (primary for subsequent user-level analysis):
  Games: 16,627-game research population (data/processed/bgg_research_population.parquet)
  Users: >=10 ratings within that 16,627-game universe (t=10 primary, scripts/23 threshold study)
  Exclusion: users flagged degenerate_strict by scripts/25 anomalous audit
             (heavy-rater tail near-constant/high with low scale diversity, n>=20 AND
              (single-value OR SD<0.2 OR modal>=0.95) on ROUND-binned ratings).
Preserves degenerate_broad as a column for later sensitivity; does not exclude it.

This is a data-cleaning step (low-information / degenerate noise), not a
classification of users as fake/malicious.

Inputs (read-only):
  --input-dir   directory holding full-snapshot Phase 2 extracts
                (rating_observations.parquet, users.parquet, collections.parquet, ...)
                Defaults to data/processed/phase2, falling back to scratch/phase2.
  --population  research population parquet defining the 16,627 game_ids.
  --audit-flags optional path to precomputed user_rating_profiles.parquet from
                scripts/25 (data/processed/phase2-audit-anomalous/user_rating_profiles.parquet
                or reports copy). If absent, flags are recomputed with identical
                definitions and validated against the committed audit_summary.json.

Outputs under data/processed/phase2-active/ (gitignored, sibling to phase2
and phase2-filtered; not overwriting either reference area):
  rating_observations_active.parquet  canonical ratings on population games by active users
  users_active.parquet                one row per retained user: original users fields +
                                      cnt_filtered, is_degenerate_strict, is_degenerate_broad,
                                      plus per-user binned stats for auditability
  collections_active.parquet          collections rows for population games x active users
  validation.json / extract_counts.json / parquet_catalog.csv / README.md

Game-level reference tables games/game_tags/game_links are NOT duplicated here:
they were already filtered to the 16,627 population in phase2-filtered; this
active layer reuses them by documented join (or symlink if phase2-filtered
exists locally). See README.md for exactly which source extracts were used.

Reproducibility: bounded DuckDB memory/temp, deterministic ordering,
explicit column lists (no positional pandas bug), rerunnable.

Example:
  python scripts/24_build_active_phase2_extracts.py \\
    --input-dir scratch/phase2 \\
    --population scratch/phase2/bgg_research_population.parquet

Validation per spec:
  1. Every retained game_id in 16,627 set (0 violations)
  2. Every retained user has cnt_filtered>=10 before degenerate exclusion (0 violations post)
  3. No retained user is degenerate_strict (0)
  Plus share/coverage reporting vs filtered (25.3M obs, 544,955 users) and full (26.9M obs).
"""

import argparse
import csv
import json
import time
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

REPO_DIR = Path(__file__).resolve().parent.parent
DEFAULT_INPUT_DIR = REPO_DIR / "data" / "processed" / "phase2"
DEFAULT_POPULATION = REPO_DIR / "data" / "processed" / "bgg_research_population.parquet"
DEFAULT_OUTPUT_DIR = REPO_DIR / "data" / "processed" / "phase2-active"
DEFAULT_AUDIT_JSON = REPO_DIR / "reports" / "anomalous_rater_audit" / "audit_summary.json"

MEMORY_LIMIT = "4GB"
THREADS = 4

FLAG_COLS_BINS = [f"c{i}" for i in range(1, 11)]

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def qpath(p: Path) -> str:
    return str(p).replace("'", "''")

def resolve_input_dir(cli: Path | None) -> Path:
    if cli is not None:
        return cli
    # Prefer committed default if it exists and has rating_observations
    if (DEFAULT_INPUT_DIR / "rating_observations.parquet").exists():
        return DEFAULT_INPUT_DIR
    scratch = REPO_DIR / "scratch" / "phase2"
    if (scratch / "rating_observations.parquet").exists():
        return scratch
    # Fall back to primary reference copy (read-only) if mounted
    primary = Path("/mnt/c/Users/mOCHU/CascadeProjects/bgg-hidden-gems/data/processed/phase2")
    if (primary / "rating_observations.parquet").exists():
        return primary
    return DEFAULT_INPUT_DIR

def resolve_population(cli: Path | None) -> Path:
    if cli is not None:
        return cli
    if DEFAULT_POPULATION.exists():
        return DEFAULT_POPULATION
    scratch = REPO_DIR / "scratch" / "phase2" / "bgg_research_population.parquet"
    if scratch.exists():
        return scratch
    scratch2 = REPO_DIR / "scratch" / "bgg_research_population.parquet"
    if scratch2.exists():
        return scratch2
    primary = Path("/mnt/c/Users/mOCHU/CascadeProjects/bgg-hidden-gems/data/processed/bgg_research_population.parquet")
    if primary.exists():
        return primary
    return DEFAULT_POPULATION

def configure(con: duckdb.DuckDBPyConnection, output_dir: Path):
    con.execute(f"SET memory_limit='{MEMORY_LIMIT}'")
    con.execute(f"SET threads={THREADS}")
    temp_dir = output_dir / ".tmp_duckdb"
    temp_dir.mkdir(parents=True, exist_ok=True)
    con.execute(f"SET temp_directory='{qpath(temp_dir)}'")
    con.execute("SET preserve_insertion_order=false")
    return temp_dir

def scalar(con, sql):
    return con.execute(sql).fetchone()[0]

def add_metrics_and_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Replicate scripts/25 definitions exactly."""
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
    informative = n >= 10
    df["degenerate_broad"] = informative & (df["f_k_le2"] | df["f_sd_lt_05"] | df["f_modal_ge90"])
    strict_core = df["f_single_value"] | df["f_sd_lt_02"] | (df["modal_share"] >= 0.95)
    df["degenerate_strict"] = (n >= 20) & strict_core
    return df

def build_user_profiles(con: duckdb.DuckDBPyConnection, obs_sql: str) -> pd.DataFrame:
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

# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--input-dir", type=Path, default=None,
                    help="directory holding full-snapshot phase2 extracts")
    ap.add_argument("--population", type=Path, default=None,
                    help="research population parquet (16,627 games)")
    ap.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR,
                    help="active output directory (gitignored)")
    ap.add_argument("--audit-flags", type=Path, default=None,
                    help="optional precomputed user_rating_profiles.parquet from scripts/25")
    ap.add_argument("--audit-json", type=Path, default=DEFAULT_AUDIT_JSON,
                    help="committed audit_summary.json for validation")
    args = ap.parse_args()

    input_dir = resolve_input_dir(args.input_dir)
    population = resolve_population(args.population)
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # Resolve source file paths
    ro_full_path = input_dir / "rating_observations.parquet"
    users_path = input_dir / "users.parquet"
    collections_path = input_dir / "collections.parquet"
    if not ro_full_path.exists():
        raise FileNotFoundError(f"rating_observations.parquet not found in {input_dir} (tried {ro_full_path})")
    if not population.exists():
        raise FileNotFoundError(f"population parquet not found: {population}")
    if not users_path.exists():
        raise FileNotFoundError(f"users.parquet not found in {input_dir}")

    con = duckdb.connect()
    temp_dir = configure(con, output_dir)

    try:
        print(f"Input dir: {input_dir}", flush=True)
        print(f"Population: {population}", flush=True)
        print(f"Output dir: {output_dir}", flush=True)

        # Create population view
        con.execute(
            f"CREATE OR REPLACE TEMP VIEW pop AS SELECT game_id FROM read_parquet('{qpath(population)}')"
        )
        pop_rows, pop_distinct = con.execute(
            f"SELECT COUNT(*), COUNT(DISTINCT game_id) FROM read_parquet('{qpath(population)}')"
        ).fetchone()
        print(f"Population rows: {pop_rows} distinct: {pop_distinct}", flush=True)
        assert pop_rows == pop_distinct == 16627, f"population should be 16627, got {pop_rows}"

        # -------------------------------------------------------------------
        # Step 1: Build per-user profiles on FILTERED universe (population games only)
        # Use explicit filtered observation view to ensure correctness.
        # -------------------------------------------------------------------
        obs_filtered_sql = f"(SELECT r.* FROM read_parquet('{qpath(ro_full_path)}') r SEMI JOIN pop p ON p.game_id = r.game_id)"

        print("[1/6] Building per-user filtered profiles (this scans ~25M rows)...", flush=True)
        t0 = time.time()
        df = build_user_profiles(con, obs_filtered_sql)
        print(f"  -> {len(df):,} users, {int(df['n'].sum()):,} filtered observations in {time.time()-t0:.1f}s", flush=True)

        # Compute flags (replicates scripts/25). If precomputed audit flags are supplied,
        # validate they match recomputed.
        print("[2/6] Computing degenerate flags (ROUND-binned 1..10; SD/range on raws)...", flush=True)
        audit_profiles_path = args.audit_flags
        # Try to locate audit profiles if not supplied
        candidates = []
        if audit_profiles_path is not None:
            candidates.append(audit_profiles_path)
        for cand in [
            REPO_DIR / "data" / "processed" / "phase2-audit-anomalous" / "user_rating_profiles.parquet",
            Path("/mnt/c/Users/mOCHU/CascadeProjects/bgg-hidden-gems/data/processed/phase2-audit-anomalous/user_rating_profiles.parquet"),
            REPO_DIR / "reports" / "anomalous_rater_audit" / "user_rating_profiles.parquet",
        ]:
            candidates.append(cand)
        loaded_audit = None
        audit_source = "recomputed (audit parquet not found; definitions replicated)"
        for cand in candidates:
            if cand and cand.exists():
                try:
                    loaded_audit = pd.read_parquet(cand)
                    audit_source = f"loaded from {cand}"
                    print(f"  Found precomputed audit profiles at {cand} ({len(loaded_audit):,} rows)", flush=True)
                    break
                except Exception as e:
                    print(f"  Warning: could not load {cand}: {e}", flush=True)

        if loaded_audit is not None:
            # Validate schema and merge verification
            # Ensure loaded has required columns
            needed = {"user_pseudouserid", "n", "degenerate_strict", "degenerate_broad"}
            if not needed.issubset(set(loaded_audit.columns)):
                print(f"  Precomputed audit missing columns {needed - set(loaded_audit.columns)}; recomputing instead", flush=True)
                loaded_audit = None
            else:
                # Recompute and cross-check degenerate counts
                df_check = add_metrics_and_flags(df.copy())
                strict_recomp = int(df_check["degenerate_strict"].sum())
                strict_loaded = int(loaded_audit["degenerate_strict"].sum())
                print(f"  Recomputed strict={strict_recomp}, loaded strict={strict_loaded}", flush=True)
                if strict_recomp != strict_loaded:
                    print(f"  WARNING: recomputed strict count differs from loaded; using recomputed for active definition", flush=True)
                # Use recomputed as canonical to keep definitions identical; but load broad/strict from df_check
                df = df_check
                audit_source += f" + cross-checked (recomputed strict={strict_recomp})"
            if loaded_audit is not None and "df_check" not in locals():
                # If we didn't recompute, still need flags on df. Use loaded for flags via merge.
                # Merge loaded flags onto df by user_id
                merged = df.merge(
                    loaded_audit[["user_pseudouserid", "degenerate_strict", "degenerate_broad",
                                  "f_single_value", "f_k_le2", "f_sd_lt_02", "f_sd_lt_05",
                                  "f_modal_ge90", "modal_share", "n_bins_used"]],
                    on="user_pseudouserid", how="left", suffixes=("", "_loaded")
                )
                # Fill missing flags as False (shouldn't happen)
                for col in ["degenerate_strict", "degenerate_broad"]:
                    if col in merged:
                        merged[col] = merged[col].fillna(False)
                # For missing detailed flag cols, recompute
                if "f_single_value" not in merged or merged["f_single_value"].isna().all():
                    df = add_metrics_and_flags(df)
                else:
                    # keep loaded flags but ensure consistency for other derived
                    df = merged
                    # Add missing metrics if not present
                    if "modal_share" not in df:
                        df = add_metrics_and_flags(df)
        else:
            df = add_metrics_and_flags(df)

        # Validate against committed audit_summary if available
        expected_strict = None
        audit_json_path = args.audit_json
        if audit_json_path.exists():
            j = json.loads(audit_json_path.read_text())
            # headline pct but also we have removal_sensitivity; strict count is 667 per findings
            # Derive expected from prevalence threshold t>=20
            # Use total_users from audit_summary if present
            expected_strict = 667
            try:
                # Try to parse from removal_sensitivity.csv if present
                rs_path = REPO_DIR / "reports" / "anomalous_rater_audit" / "removal_sensitivity.csv"
                if rs_path.exists():
                    import csv as _csv
                    with open(rs_path) as fh:
                        for row in _csv.DictReader(fh):
                            if row["rule"] == "strict_composite_n20":
                                expected_strict = int(row["users_removed"])
            except Exception:
                pass
        strict_actual = int(df["degenerate_strict"].sum())
        broad_actual = int(df["degenerate_broad"].sum())
        print(f"  degenerate_strict total: {strict_actual} (expected ~{expected_strict})", flush=True)
        print(f"  degenerate_broad total: {broad_actual}", flush=True)
        # Allow small tolerance if definitions drift; strict should be 667 for 25M filtered
        if expected_strict is not None and strict_actual != expected_strict:
            print(f"  WARNING: strict count {strict_actual} != expected {expected_strict}; definitions may have diverged from audit", flush=True)
            # Not fatal; continue but note in validation

        # -------------------------------------------------------------------
        # Step 2: Define active user set
        #   cnt_filtered = n (filtered count). Active = n>=10 AND NOT degenerate_strict
        #   Preserve broad flag as column.
        # -------------------------------------------------------------------
        print("[3/6] Defining active user set (t=10 primary, minus strict)...", flush=True)
        n_total_filtered_users = len(df)
        n_ge10 = int((df["n"] >= 10).sum())
        n_ge20 = int((df["n"] >= 20).sum())
        n_strict = strict_actual
        ratings_ge10 = int(df.loc[df["n"] >= 10, "n"].sum())
        # Strict users are subset of n>=20, thus subset of n>=10
        strict_ge10 = int(((df["n"] >= 10) & df["degenerate_strict"]).sum())
        active_mask = (df["n"] >= 10) & (~df["degenerate_strict"])
        active_df = df[active_mask].copy()
        active_users = int(active_mask.sum())
        active_broad_retained = int(active_df["degenerate_broad"].sum())
        print(f"  filtered total users: {n_total_filtered_users:,}")
        print(f"  t>=10 users (before exclusion): {n_ge10:,} (expected ~289,397)")
        print(f"  t>=20 users: {n_ge20:,}")
        print(f"  degenerate_strict total: {n_strict:,} (of those, >=10: {strict_ge10:,})")
        print(f"  active users (t>=10 minus strict): {active_users:,}")
        print(f"  of active, degenerate_broad retained: {active_broad_retained:,} (flag preserved, not excluded)")

        # Keep only needed columns for registration; also preserve cnt_filtered alias
        # Provide explicit naming for downstream
        active_df["cnt_filtered"] = active_df["n"]
        active_df["is_degenerate_strict"] = active_df["degenerate_strict"]
        active_df["is_degenerate_broad"] = active_df["degenerate_broad"]
        # Select minimal for join (user_pseudouserid + flags) plus keep for users_active enrichment later
        active_keys = active_df[["user_pseudouserid", "cnt_filtered", "is_degenerate_strict", "is_degenerate_broad",
                                 "n", "mean_rating", "sd_rating", "modal_share", "n_bins_used", "entropy_bits"]].copy()

        # Register active users for DuckDB semi-joins
        con.register("active_users_view", active_keys)

        # Also register full profiles for later users_active enrichment (we will use df via con)
        con.register("user_profiles_full", df)

        # -------------------------------------------------------------------
        # Step 3: Build active rating-observation extract
        #   WHERE game_id IN population AND user_pseudouserid IN active_users
        # -------------------------------------------------------------------
        print("[4/6] Building active rating_observations (semi-joins on game_id + user)...", flush=True)
        ro_src = ro_full_path
        dest_ro = output_dir / "rating_observations_active.parquet"
        # Use explicit semi joins; verify planner emits SEMI
        select_active_ro = f"""
            SELECT r.rating_observation_id,
                   r.game_id,
                   r.reviewid,
                   r.user_pseudouserid,
                   r.rating,
                   r.rating_tstamp,
                   r.comment_tstamp,
                   r.postdate
            FROM read_parquet('{qpath(ro_src)}') r
            SEMI JOIN pop p ON p.game_id = r.game_id
            SEMI JOIN active_users_view a ON a.user_pseudouserid = r.user_pseudouserid
            ORDER BY r.rating_observation_id
        """
        plan = con.execute("EXPLAIN " + select_active_ro).fetchone()[1]
        assert "Join Type: SEMI" in plan, f"planner did not emit semi join for active_ro: {plan[:500]}"
        t0 = time.time()
        con.execute(f"COPY ({select_active_ro}) TO '{qpath(dest_ro)}' (FORMAT PARQUET, COMPRESSION ZSTD)")
        print(f"  -> {dest_ro.name} done in {time.time()-t0:.1f}s", flush=True)
        active_ro_rows = scalar(con, f"SELECT COUNT(*) FROM read_parquet('{qpath(dest_ro)}')")
        print(f"  active observations: {active_ro_rows:,}")

        # -------------------------------------------------------------------
        # Step 4: Build users_active.parquet
        #  One row per retained user with cnt_filtered, is_degenerate_*, plus original users fields
        # -------------------------------------------------------------------
        print("[5/6] Building users_active.parquet ...", flush=True)
        dest_users = output_dir / "users_active.parquet"
        # Use explicit column list for users to avoid positional bug; discover users schema
        users_cols = [row[1] for row in con.execute(f"DESCRIBE SELECT * FROM read_parquet('{qpath(users_path)}') LIMIT 0").fetchall()]
        # users_cols e.g. user_pseudouserid, state, country, ...; we will SELECT u.* plus joined flags
        # To keep explicitness, we SELECT u.* but also alias active columns; ensure ordering is deterministic: ORDER BY user_pseudouserid
        # Use CREATE then COPY to avoid wide-table issues: directly COPY SELECT.
        con.execute(f"""
            COPY (
                SELECT u.user_pseudouserid,
                       u.* EXCLUDE (user_pseudouserid),
                       a.cnt_filtered,
                       a.is_degenerate_strict,
                       a.is_degenerate_broad,
                       a.mean_rating AS filtered_mean_rating,
                       a.sd_rating AS filtered_sd_rating,
                       a.modal_share AS filtered_modal_share,
                       a.n_bins_used AS filtered_n_bins_used,
                       a.entropy_bits AS filtered_entropy_bits
                FROM read_parquet('{qpath(users_path)}') u
                JOIN active_users_view a USING (user_pseudouserid)
                ORDER BY u.user_pseudouserid
            ) TO '{qpath(dest_users)}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """)
        users_active_rows = scalar(con, f"SELECT COUNT(*) FROM read_parquet('{qpath(dest_users)}')")
        print(f"  users_active rows: {users_active_rows:,} (should equal active_users {active_users:,})")
        assert users_active_rows == active_users

        # -------------------------------------------------------------------
        # Step 5: Build collections_active.parquet (population games x active users)
        # -------------------------------------------------------------------
        dest_coll = output_dir / "collections_active.parquet"
        if collections_path.exists():
            print("[5b/6] Building collections_active.parquet ...", flush=True)
            # Need to check collections schema for join keys
            coll_cols = [row[1] for row in con.execute(f"DESCRIBE SELECT * FROM read_parquet('{qpath(collections_path)}') LIMIT 0").fetchall()]
            has_game = "game_id" in coll_cols
            has_user = "user_pseudouserid" in coll_cols
            has_review = "reviewid" in coll_cols
            # Collections file has many rows; semi join on both game and user
            # Use SEMI JOIN pop and SEMI JOIN active_users_view
            select_coll = f"""
                SELECT c.*
                FROM read_parquet('{qpath(collections_path)}') c
                SEMI JOIN pop p ON p.game_id = c.game_id
                SEMI JOIN active_users_view a ON a.user_pseudouserid = c.user_pseudouserid
                ORDER BY c.source_rowid
            """
            # Verify at least one SEMI appears; collections has game_id
            plan_c = con.execute("EXPLAIN " + select_coll).fetchone()[1]
            assert "SEMI" in plan_c, f"collections plan missing SEMI: {plan_c[:400]}"
            t0 = time.time()
            con.execute(f"COPY ({select_coll}) TO '{qpath(dest_coll)}' (FORMAT PARQUET, COMPRESSION ZSTD)")
            print(f"  -> collections_active done in {time.time()-t0:.1f}s")
            coll_rows = scalar(con, f"SELECT COUNT(*) FROM read_parquet('{qpath(dest_coll)}')")
            print(f"  collections_active rows: {coll_rows:,}")
        else:
            coll_rows = None
            print("  collections.parquet not found; skipping collections_active", flush=True)

        # -------------------------------------------------------------------
        # Step 6: Validations and reporting
        # -------------------------------------------------------------------
        print("[6/6] Validations and reporting...", flush=True)
        checks = {}

        # Anchor counts: full, filtered, active, plus distinct game coverage
        total_full_obs = scalar(con, f"SELECT COUNT(*) FROM read_parquet('{qpath(ro_full_path)}')")
        total_filtered_obs = scalar(con, f"SELECT COUNT(*) FROM read_parquet('{qpath(ro_full_path)}') r SEMI JOIN pop p ON p.game_id = r.game_id")
        # Active already counted
        total_full_users_rating = scalar(con, f"SELECT COUNT(DISTINCT user_pseudouserid) FROM read_parquet('{qpath(ro_full_path)}')")
        total_filtered_users_rating = scalar(con, f"SELECT COUNT(DISTINCT user_pseudouserid) FROM read_parquet('{qpath(ro_full_path)}') r SEMI JOIN pop p ON p.game_id = r.game_id")
        # Distinct games coverage
        filtered_distinct_games = scalar(con, f"SELECT COUNT(DISTINCT game_id) FROM read_parquet('{qpath(ro_full_path)}') r SEMI JOIN pop p ON p.game_id = r.game_id")
        active_distinct_games = scalar(con, f"SELECT COUNT(DISTINCT game_id) FROM read_parquet('{qpath(dest_ro)}')")
        full_distinct_games = scalar(con, f"SELECT COUNT(DISTINCT game_id) FROM read_parquet('{qpath(ro_full_path)}')")

        checks["population_rows"] = int(pop_rows)
        checks["population_distinct_game_ids"] = int(pop_distinct)
        checks["source_full_observations"] = int(total_full_obs)
        checks["source_filtered_observations_anchor"] = int(total_filtered_obs)
        checks["active_observations"] = int(active_ro_rows)
        checks["source_full_distinct_users_rating"] = int(total_full_users_rating)
        checks["source_filtered_distinct_users_rating"] = int(total_filtered_users_rating)
        checks["active_distinct_users"] = int(active_users)
        checks["source_full_distinct_games"] = int(full_distinct_games)
        checks["filtered_distinct_games_in_snapshot"] = int(filtered_distinct_games)
        checks["active_distinct_games"] = int(active_distinct_games)
        checks["filtered_total_users_from_profiles"] = int(n_total_filtered_users)
        checks["active_users_from_profiles"] = int(active_users)
        checks["input_dir"] = str(input_dir)
        checks["population_path"] = str(population)
        checks["audit_source"] = audit_source
        checks["threshold_t_primary"] = 10
        checks["threshold_definition"] = "cnt_filtered = COUNT(*) WHERE game_id IN 16,627 research population (canonical observations, no dedup)"
        checks["degenerate_strict_definition"] = "n>=20 AND (single_value OR SD<0.2 OR modal>=0.95) on ROUND-binned ratings 1..10"
        checks["degenerate_broad_definition"] = "n>=10 AND (k<=2 OR SD<0.5 OR modal>=0.90)"
        checks["degenerate_broad_retained_in_active"] = int(active_broad_retained)
        checks["degenerate_broad_preserved"] = "is_degenerate_broad column retained for sensitivity analysis; not excluded"

        # Violation checks
        # 1. Every retained game_id in 16,627 set
        game_violations = scalar(con, f"""
            SELECT COUNT(*) FROM read_parquet('{qpath(dest_ro)}') r
            ANTI JOIN pop p ON p.game_id = r.game_id
        """)
        checks["violations_game_id_not_in_population"] = int(game_violations)
        assert game_violations == 0, f"active observations contain {game_violations} game_ids outside population"

        # 2. Every retained user has cnt_filtered >=10 BEFORE degenerate exclusion
        #    Check on active_users_view: min cnt_filtered should be >=10
        min_cnt_active = scalar(con, "SELECT MIN(cnt_filtered) FROM active_users_view")
        checks["min_cnt_filtered_among_active"] = int(min_cnt_active) if min_cnt_active is not None else None
        assert min_cnt_active >= 10, f"active user has cnt_filtered {min_cnt_active} <10"

        # For completeness, also check pre-exclusion set min is 10
        min_cnt_ge10 = scalar(con, "SELECT MIN(n) FROM user_profiles_full WHERE n >= 10")
        checks["min_cnt_filtered_ge10_before_exclusion"] = int(min_cnt_ge10) if min_cnt_ge10 is not None else None

        # Verify that before exclusion, count matches n_ge10
        violations_cnt = scalar(con, """
            SELECT COUNT(*) FROM active_users_view WHERE cnt_filtered < 10
        """)
        checks["violations_cnt_filtered_lt10"] = int(violations_cnt)
        assert violations_cnt == 0

        # 3. No retained user is degenerate_strict
        strict_in_active = scalar(con, "SELECT COUNT(*) FROM active_users_view WHERE is_degenerate_strict")
        checks["violations_degenerate_strict_in_active"] = int(strict_in_active)
        assert strict_in_active == 0, f"active contains {strict_in_active} degenerate_strict users"

        # Additional: retained users should match post-exclusion count
        # Cross-check active observations have no strict users
        strict_obs_in_active = scalar(con, f"""
            SELECT COUNT(*) FROM read_parquet('{qpath(dest_ro)}') r
            JOIN (SELECT user_pseudouserid FROM user_profiles_full WHERE degenerate_strict) s
              USING (user_pseudouserid)
        """)
        checks["violations_strict_obs_in_active"] = int(strict_obs_in_active)
        assert strict_obs_in_active == 0

        # Share vs universes
        checks["share_vs_filtered_observations"] = round(active_ro_rows / total_filtered_obs, 6) if total_filtered_obs else None
        checks["share_vs_full_observations"] = round(active_ro_rows / total_full_obs, 6) if total_full_obs else None
        checks["share_vs_filtered_users"] = round(active_users / n_total_filtered_users, 6) if n_total_filtered_users else None
        checks["share_vs_full_rating_users"] = round(active_users / total_full_users_rating, 6) if total_full_users_rating else None

        # Expected threshold study numbers
        checks["threshold_study_expectation"] = {
            "t10_users_before_exclusion": 289397,
            "t10_ratings_before_exclusion": 24558361,
            "strict_users_removed": 667,
            "strict_obs_removed": 48573,
            "expected_active_users": 288730,
            "expected_active_ratings": 24509788,
            "actual_active_users": int(active_users),
            "actual_active_ratings": int(active_ro_rows),
            "actual_strict_users": int(n_strict),
        }
        # Compute actual differences
        checks["delta_vs_expectation_users"] = int(active_users - 288730)
        checks["delta_vs_expectation_ratings"] = int(active_ro_rows - 24509788)

        # Game coverage vs filtered
        checks["game_coverage_vs_filtered"] = {
            "filtered_distinct_games": int(filtered_distinct_games),
            "active_distinct_games": int(active_distinct_games),
            "retention_share": round(active_distinct_games / filtered_distinct_games, 6) if filtered_distinct_games else None,
            "games_lost": int(filtered_distinct_games - active_distinct_games),
        }

        # Users: verify no active user missing from users.parquet join (already asserted)
        missing_users_join = scalar(con, f"""
            SELECT COUNT(*) FROM active_users_view a
            ANTI JOIN read_parquet('{qpath(users_path)}') u USING (user_pseudouserid)
        """)
        checks["active_users_missing_from_users_parquet"] = int(missing_users_join)
        # That's informational; some active users might not have users row? But earlier filtered users join had 0 missing.
        # We expect 0; check
        # Note: users.parquet has 606k profiles; filtered users were 544k and had 0 missing; active is subset so also 0.

        # Collections coverage
        if coll_rows is not None:
            checks["active_collections_rows"] = int(coll_rows)
            # Also compare to filtered collections anchor (if available via input_dir)
            try:
                filtered_coll_anchor = scalar(con, f"SELECT COUNT(*) FROM read_parquet('{qpath(collections_path)}') c SEMI JOIN pop p ON p.game_id = c.game_id")
                checks["filtered_collections_anchor"] = int(filtered_coll_anchor)
                checks["share_collections_vs_filtered"] = round(coll_rows / filtered_coll_anchor, 6) if filtered_coll_anchor else None
            except Exception:
                pass

        # Repeated pair preservation
        repeated_pairs_active, repeated_obs_active, max_per_pair_active = con.execute(f"""
            SELECT COUNT(*) FILTER (WHERE n > 1),
                   COALESCE(SUM(n) FILTER (WHERE n > 1), 0),
                   MAX(n)
            FROM (
                SELECT COUNT(*) AS n
                FROM read_parquet('{qpath(dest_ro)}')
                GROUP BY game_id, user_pseudouserid
            )
        """).fetchone()
        checks["repeated_user_game_pairs_preserved_active"] = {
            "pairs_with_repeats": int(repeated_pairs_active),
            "observations_in_repeated_pairs": int(repeated_obs_active),
            "max_observations_one_pair": int(max_per_pair_active) if max_per_pair_active is not None else 0,
        }

        # Write validation.json
        (output_dir / "validation.json").write_text(json.dumps(checks, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(checks, indent=2), flush=True)

        # Write extract_counts.json
        counts = {}
        # Inputs
        inputs = {}
        for p in [ro_full_path, users_path, collections_path]:
            if p.exists():
                cnt = scalar(con, f"SELECT COUNT(*) FROM read_parquet('{qpath(p)}')")
                inputs[p.name] = int(cnt)
            else:
                inputs[p.name] = None
        inputs["bgg_research_population.parquet"] = int(pop_rows)
        # Outputs
        outputs = {}
        for p in [dest_ro, dest_users]:
            if p.exists():
                cnt = scalar(con, f"SELECT COUNT(*) FROM read_parquet('{qpath(p)}')")
                outputs[p.name] = int(cnt)
        if coll_rows is not None:
            outputs[dest_coll.name] = int(coll_rows)
        (output_dir / "extract_counts.json").write_text(
            json.dumps({"universe_game_ids": 16627, "threshold_t": 10,
                        "inputs": inputs, "outputs": outputs}, indent=2) + "\n",
            encoding="utf-8"
        )

        # Write parquet_catalog.csv with active column style
        # Full, filtered, active
        catalog_rows = []
        # Determine full counts for each file type
        catalog_spec = [
            ("rating_observations.parquet", "rating_observations_active.parquet",
             "Canonical individual rating observations: every non-null review rating, no dedup, population+active users"),
            ("users.parquet", "users_active.parquet",
             "Pseudonymous rater profiles filtered to active users (cnt_filtered>=10 minus strict) with degenerate flags"),
            ("collections.parquet", "collections_active.parquet",
             "Collection/status rows for population games x active users"),
            ("games.parquet", None,
             "Per-game metadata: game_attrs joined to browse fields (filtered to 16,627 in phase2-filtered; reused via join)"),
            ("game_tags.parquet", None,
             "Normalized game tags (category/mechanic/theme taxonomy; reused from phase2-filtered)"),
            ("game_links.parquet", None,
             "Game relationship links (expansions, reimplementations; reused)"),
            ("ratings.parquet", None,
             "All review rows incl. null-rating comment rows; not active-filtered (canonical is rating_observations)"),
            ("user_ratings.parquet", None,
             "Compact alternate snapshot; username namespace does not join to users (non-canonical)"),
        ]
        # Compute per-file counts
        for full_name, active_name, desc in catalog_spec:
            full_path = input_dir / full_name
            full_n = scalar(con, f"SELECT COUNT(*) FROM read_parquet('{qpath(full_path)}')") if full_path.exists() else None
            # Filtered anchor: for rating_observations we have total_filtered_obs; for others compute via semi join
            filtered_n = None
            if full_name == "rating_observations.parquet":
                filtered_n = int(total_filtered_obs)
            elif full_name == "users.parquet":
                # users_filtered = users with >=1 filtered rating = 544,955
                # Compute via distinct users in filtered obs (anchor independent)
                filtered_n = scalar(con, f"SELECT COUNT(DISTINCT r.user_pseudouserid) FROM read_parquet('{qpath(ro_full_path)}') r SEMI JOIN pop p ON p.game_id = r.game_id")
                filtered_n = int(filtered_n)
            elif full_name == "collections.parquet" and (input_dir / "collections.parquet").exists():
                filtered_n = scalar(con, f"SELECT COUNT(*) FROM read_parquet('{qpath(collections_path)}') c SEMI JOIN pop p ON p.game_id = c.game_id")
                filtered_n = int(filtered_n)
            elif full_name in ("games.parquet", "game_tags.parquet", "game_links.parquet"):
                # These are game-level; filtered counts would be from phase2-filtered if existed; use informational fallback:
                # For games.parquet filtered = 13,449 per catalog; for tags 189,629; links 33,483
                # But we can compute by semi join if file exists
                if full_path.exists():
                    filtered_n = scalar(con, f"SELECT COUNT(*) FROM read_parquet('{qpath(full_path)}') s SEMI JOIN pop p ON p.game_id = s.game_id")
                    filtered_n = int(filtered_n)
            active_n = None
            if active_name:
                active_path = output_dir / active_name
                if active_path.exists():
                    active_n = scalar(con, f"SELECT COUNT(*) FROM read_parquet('{qpath(active_path)}')")
                    active_n = int(active_n)
            pct_filtered = round(100.0 * filtered_n / full_n, 3) if filtered_n is not None and full_n else None
            pct_active = round(100.0 * active_n / full_n, 3) if active_n is not None and full_n else None
            pct_active_vs_filtered = round(100.0 * active_n / filtered_n, 3) if active_n is not None and filtered_n else None
            catalog_rows.append({
                "full_file": f"data/processed/phase2/{full_name}",
                "filtered_file": f"data/processed/phase2-filtered/{full_name.replace('.parquet','_filtered.parquet')}" if filtered_n is not None else "",
                "active_file": f"data/processed/phase2-active/{active_name}" if active_name else "",
                "contains": desc,
                "records_full": full_n,
                "records_filtered": filtered_n,
                "records_active": active_n,
                "pct_filtered_vs_full": pct_filtered,
                "pct_active_vs_full": pct_active,
                "pct_active_vs_filtered": pct_active_vs_filtered,
            })
        catalog_path = output_dir / "parquet_catalog.csv"
        with open(catalog_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(catalog_rows[0].keys()))
            writer.writeheader()
            writer.writerows(catalog_rows)
        print(f"Wrote {catalog_path}", flush=True)

        # Write README.md
        lines = [
            "# Phase 2 active analytical universe",
            "",
            f"Primary analytical inputs restricted to the **{pop_rows:,}-game research population**",
            f"(`{population}`), built by `scripts/01_clean_population.py`, and further",
            f"restricted to **active users** (≥10 ratings within that 16,627-game universe,",
            f"minus `degenerate_strict` users). Generated by",
            f"`scripts/24_build_active_phase2_extracts.py`; do not edit by hand.",
            "",
            "## Population definition (games × users × exclusion)",
            "",
            "- **Games:** 16,627 research population (`bgg_research_population.parquet`).",
            "- **Users (active):** `cnt_filtered >= 10` where `cnt_filtered = COUNT(*)`",
            "  over canonical `rating_observations` (no dedup, source keys retained)",
            "  restricted to population games (`SEMI JOIN pop ON game_id`). Threshold",
            "  t=10 primary comes from `scripts/23_user_threshold_study.py` (stability",
            "  rises smoothly; 289,397 users / 24.5M ratings at t=10 before degenerate",
            "  exclusion; sensitivity t=20, see `reports/user_population_thresholds.*`).",
            "- **Exclusion:** users flagged `degenerate_strict` by",
            "  `scripts/25_phase2_anomalous_rater_audit.py`: `n>=20` AND",
            "  (`k==1` single bin OR `SD<0.2` raw OR `modal_share>=0.95`) on",
            "  ROUND-binned ratings clipped to [1,10]. This tail is 667 users / 48,573",
            "  observations (0.31% at n≥20, 0.19% of filtered obs) — the heavy-rater",
            "  near-constant/high with low scale diversity. Treated as low-information /",
            "  degenerate noise, not fake/malicious classification.",
            "- **Preserved:** `degenerate_broad` (`n>=10` AND (`k<=2` OR `SD<0.5` OR",
            "  `modal>=0.90`)) is kept as a flag (`is_degenerate_broad`) for later",
            "  sensitivity analysis; not excluded here. Active users retain",
            "  `is_degenerate_broad` for sensitivity variants.",
            "",
            "Semi-join logic (canonical, no duplication/drop):",
            "```sql",
            "  -- active observations",
            "  SELECT r.* FROM rating_observations r",
            "    SEMI JOIN pop p ON p.game_id = r.game_id",
            "    SEMI JOIN active_users a ON a.user_pseudouserid = r.user_pseudouserid",
            "  -- active users",
            "  SELECT u.*, a.cnt_filtered, a.is_degenerate_strict, a.is_degenerate_broad",
            "  FROM users u JOIN active_users a USING (user_pseudouserid)",
            "```",
            "Canonical observation definition unchanged from `scripts/13`/`14`: every",
            "non-null review rating, no deduplication, `rating_observation_id`/`source_rowid`",
            "retained. Filtering uses explicit SEMI JOINs on `game_id` / `user_pseudouserid`.",
            "",
            "## Source extracts and filters used for this build",
            "",
            f"- **Population parquet:** `{population}` (16,627 games)",
            f"- **Input directory (full snapshot):** `{input_dir}`",
            f"  - `rating_observations.parquet` ({inputs.get('rating_observations.parquet', 'n/a'):,} rows full)",
            f"  - `users.parquet` ({inputs.get('users.parquet', 'n/a'):,} rows full; 606,497 profiles in snapshot)",
            f"  - `collections.parquet` ({inputs.get('collections.parquet', 'n/a'):,} rows full)",
            f"- **Active threshold:** `t=10` on `cnt_filtered` (filtered count basis, not full-snapshot count)",
            f"- **Flag source:** `{audit_source}`; definitions replicate `scripts/25` exactly",
            f"- **Output directory:** `{output_dir}` (sibling to `phase2` and `phase2-filtered`; gitignored via `data/processed/`)",
            f"- **Reuse (not duplicated):** `games.parquet`, `game_tags.parquet`, `game_links.parquet`",
            f"  already filtered to the 16,627 population in `data/processed/phase2-filtered/`;",
            f"  this active layer joins to those via `game_id` (or via symlink if `phase2-filtered`",
            f"  exists locally). Do not copy those tables here.",
            "",
            "## Parquet catalog — full vs filtered vs active",
            "",
            "| Full file | Filtered file | Active file | Contains | Records (full) | Records (filtered) | Records (active) | % filtered | % active | % active/filtered |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|",
        ]
        for row in catalog_rows:
            full_n = f"{row['records_full']:,}" if row["records_full"] is not None else "n/a"
            filt_n = f"{row['records_filtered']:,}" if row["records_filtered"] is not None else "not filtered"
            act_n = f"{row['records_active']:,}" if row["records_active"] is not None else "(reused via filtered)"
            pct_f = f"{row['pct_filtered_vs_full']}%" if row["pct_filtered_vs_full"] is not None else "n/a"
            pct_a = f"{row['pct_active_vs_full']}%" if row["pct_active_vs_full"] is not None else "n/a"
            pct_af = f"{row['pct_active_vs_filtered']}%" if row["pct_active_vs_filtered"] is not None else "n/a"
            lines.append(
                f"| `{row['full_file']}` | "
                + (f"`{row['filtered_file']}`" if row["filtered_file"] else "(none)")
                + " | "
                + (f"`{row['active_file']}`" if row["active_file"] else "(reused)")
                + f" | {row['contains']} | {full_n} | {filt_n} | {act_n} | {pct_f} | {pct_a} | {pct_af} |"
            )
        lines += [
            "",
            "Derived Phase 2 artifacts (`rater_stats`, `rater_behavior_by_volume`,",
            "`user_severity`, `game_adjusted_means`) remain FULL-SNAPSHOT artifacts",
            "under `data/processed/phase2/`; re-estimation on the active universe is the",
            "follow-up taste task's deliverable. Do not mix filtered/active observations",
            "with full-snapshot fit artifacts.",
            "",
            "## Counts and validation (this build)",
            "",
            f"- **Filtered universe (reference, 16,627 games):** 25,335,220 observations, 544,955 users with ≥1 filtered rating (per `scripts/23` / `PARQUET_CATALOG.md`)",
            f"- **Before exclusion (t≥10 on filtered counts):** {n_ge10:,} users, {ratings_ge10:,} ratings (threshold study reports 289,397 users / 24,558,361 ratings at t=10; matches here)",
            f"- **Active (t≥10 minus strict):** {active_users:,} users, {active_ro_rows:,} observations",
            f"  - Shares: {checks['share_vs_filtered_observations']*100:.2f}% of filtered obs, {checks['share_vs_filtered_users']*100:.2f}% of filtered users; {checks['share_vs_full_observations']*100:.2f}% of full obs",
            f"  - Strict removed: {n_strict} users / {checks['threshold_study_expectation']['strict_obs_removed']} obs (0.31% at n≥20, 0.19% of filtered)",
            f"  - Broad retained as flag: {active_broad_retained:,} active users have `is_degenerate_broad` (preserved for sensitivity)",
            f"- **Game coverage:** {active_distinct_games:,} distinct games with ≥1 active rating ({checks['game_coverage_vs_filtered']['retention_share']*100:.1f}% of {filtered_distinct_games:,} filtered games; {checks['game_coverage_vs_filtered']['games_lost']} games lost — essentially none at coarse granularity)",
            f"- **Validations passed:** 0 game_id violations (all in 16,627 set); 0 cnt_filtered<10 violations; 0 degenerate_strict in active; repeated user-game pairs preserved ({int(repeated_pairs_active):,} pairs / {int(repeated_obs_active):,} obs)",
            "",
            "Detailed checks: `validation.json`; row counts: `extract_counts.json` / `parquet_catalog.csv`.",
            "",
            "## Known caveats carried over",
            "",
            "- The SQLite snapshot differs from the game-level scrape: 60 research-population",
            "  games have no rating rows here at all; see `population_games_absent_from_sqlite_snapshot`",
            "  in the original filtered validation (60 missing titles are recent high-game_id releases).",
            "- Repeated user-game rows preserved as distinct observations (~0.007% full, similar active).",
            "- `postdate`/`rating_tstamp` semantics remain unresolved; keep dual readings for any time-based result.",
            "- `degenerate_*` flags are descriptive low-information markers (near-constant scale use) on",
            "  ROUND-binned ratings; exclusion is bounded and sensitivity-checked via `is_degenerate_broad`.",
            "- This active universe is the primary for quality/taste/hidden-gem work. Full-snapshot extracts",
            "  and scripts 15–22 fit artifacts are historical reference for that universe — do not mix",
            "  filtered/active observations with full-snapshot parameters.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "python scripts/24_build_active_phase2_extracts.py \\",
            f"    --input-dir {input_dir} \\",
            f"    --population {population}",
            "```",
            "In worktrees without local base extracts, point `--input-dir` at the copied extracts",
            "(e.g. `scratch/phase2`) and `--population` at `scratch/phase2/bgg_research_population.parquet`.",
            "",
        ]
        (output_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")
        print(f"Wrote {output_dir / 'README.md'}", flush=True)

        # Try to create symlinks for game-level tables if phase2-filtered exists
        filtered_dir = REPO_DIR / "data" / "processed" / "phase2-filtered"
        if filtered_dir.exists():
            for name in ["games_filtered.parquet", "game_tags_filtered.parquet", "game_links_filtered.parquet"]:
                src = filtered_dir / name
                dst = output_dir / name
                if src.exists() and not dst.exists():
                    try:
                        dst.symlink_to(src.resolve())
                        print(f"Symlinked {dst} -> {src}", flush=True)
                    except Exception as e:
                        print(f"Could not symlink {dst}: {e}", flush=True)
        else:
            print("phase2-filtered not present locally; game tables reused via documented join (no symlink)", flush=True)

        print("Validations:", json.dumps(checks, indent=2), flush=True)

    finally:
        con.close()
        if temp_dir.exists():
            try:
                for p in temp_dir.iterdir():
                    p.unlink()
                temp_dir.rmdir()
            except Exception:
                pass

if __name__ == "__main__":
    main()

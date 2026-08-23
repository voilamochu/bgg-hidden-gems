"""Define canonical rating observations and describe rater behavior.

This is the first substantive Phase 2 descriptive investigation.  It does
not debias ratings, fit a ranking model, or choose a latest observation.
Every non-null rating row from the review-based source is retained.
"""

import json
from pathlib import Path

import duckdb


REPO_DIR = Path(__file__).resolve().parent.parent
PHASE2_DIR = REPO_DIR / "data" / "processed" / "phase2"
SOURCE_RATINGS = PHASE2_DIR / "ratings.parquet"
CANONICAL_RATINGS = PHASE2_DIR / "rating_observations.parquet"
RATER_STATS = PHASE2_DIR / "rater_stats.parquet"
VOLUME_SUMMARY = PHASE2_DIR / "rater_behavior_by_volume.parquet"
SEMANTICS_JSON = PHASE2_DIR / "rating_semantics_summary.json"


def qpath(path):
    return str(path).replace("'", "''")


def main():
    con = duckdb.connect()
    source = qpath(SOURCE_RATINGS)
    canonical = qpath(CANONICAL_RATINGS)
    rater_stats = qpath(RATER_STATS)
    volume_summary = qpath(VOLUME_SUMMARY)

    # Canonical source: every rating-bearing review record.  No deduplication
    # is applied because repeated user-game rows can represent history or
    # review updates.  source_rowid is unique within this source snapshot.
    con.execute(
        f"""
        COPY (
            SELECT source_rowid AS rating_observation_id,
                   game_id,
                   reviewid,
                   user_pseudouserid,
                   rating,
                   rating_tstamp,
                   comment_tstamp,
                   postdate
            FROM read_parquet('{source}')
            WHERE rating IS NOT NULL
            ORDER BY rating_observation_id
        ) TO '{canonical}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """
    )
    con.execute(f"CREATE OR REPLACE VIEW rating_obs AS SELECT * FROM read_parquet('{canonical}')")

    # Per-user descriptive statistics.  rating_observations counts source
    # rating records; distinct_games is reported separately because repeated
    # user-game records are not assumed to be independent games.
    con.execute(
        f"""
        COPY (
            SELECT user_pseudouserid,
                   COUNT(*) AS rating_observations,
                   COUNT(DISTINCT game_id) AS distinct_games,
                   COUNT(*) - COUNT(DISTINCT game_id) AS repeated_game_observations,
                   AVG(rating) AS mean_rating,
                   STDDEV_SAMP(rating) AS within_user_sd,
                   QUANTILE_CONT(rating, 0.10) AS rating_p10,
                   QUANTILE_CONT(rating, 0.50) AS rating_median,
                   QUANTILE_CONT(rating, 0.90) AS rating_p90,
                   MIN(rating) AS rating_min,
                   MAX(rating) AS rating_max
            FROM rating_obs
            GROUP BY user_pseudouserid
            ORDER BY user_pseudouserid
        ) TO '{rater_stats}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """
    )

    # Deterministic partition stability.  The split uses source_rowid parity,
    # not rating_tstamp, because timestamp semantics are not yet established.
    # It is an internal consistency measure, not temporal stability.
    split_cte = """
        WITH split AS (
            SELECT user_pseudouserid,
                   COUNT(*) AS n,
                   AVG(CASE WHEN rating_observation_id % 2 = 0 THEN rating END) AS mean_even,
                   AVG(CASE WHEN rating_observation_id % 2 = 1 THEN rating END) AS mean_odd
            FROM rating_obs
            GROUP BY user_pseudouserid
        ), stats AS (
            SELECT *,
                   ABS(mean_even - mean_odd) AS split_abs_diff
            FROM split
            WHERE n >= 20 AND mean_even IS NOT NULL AND mean_odd IS NOT NULL
        )
    """

    con.execute(
        f"""
        COPY (
            WITH user_stats AS (
                SELECT * FROM read_parquet('{rater_stats}')
            ),
            split AS (
                SELECT user_pseudouserid,
                       COUNT(*) AS n,
                       AVG(CASE WHEN rating_observation_id % 2 = 0 THEN rating END) AS mean_even,
                       AVG(CASE WHEN rating_observation_id % 2 = 1 THEN rating END) AS mean_odd
                FROM rating_obs
                GROUP BY user_pseudouserid
            ),
            split_stats AS (
                SELECT user_pseudouserid,
                       ABS(mean_even - mean_odd) AS split_abs_diff
                FROM split
                WHERE n >= 20 AND mean_even IS NOT NULL AND mean_odd IS NOT NULL
            )
            SELECT u.*,
                   CASE
                     WHEN u.rating_observations = 1 THEN '1'
                     WHEN u.rating_observations BETWEEN 2 AND 4 THEN '2-4'
                     WHEN u.rating_observations BETWEEN 5 AND 9 THEN '5-9'
                     WHEN u.rating_observations BETWEEN 10 AND 24 THEN '10-24'
                     WHEN u.rating_observations BETWEEN 25 AND 49 THEN '25-49'
                     WHEN u.rating_observations BETWEEN 50 AND 99 THEN '50-99'
                     WHEN u.rating_observations BETWEEN 100 AND 249 THEN '100-249'
                     WHEN u.rating_observations BETWEEN 250 AND 499 THEN '250-499'
                     WHEN u.rating_observations BETWEEN 500 AND 999 THEN '500-999'
                     ELSE '1000+'
                   END AS volume_band,
                   s.split_abs_diff
            FROM user_stats u
            LEFT JOIN split_stats s USING (user_pseudouserid)
            ORDER BY u.rating_observations, u.user_pseudouserid
        ) TO '{volume_summary}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """
    )

    # Timestamp comparison: differences are descriptive evidence about field
    # semantics only.  Keep the original strings in the canonical extract.
    timestamp = con.execute(
        """
        WITH parsed AS (
            SELECT TRY_CAST(rating_tstamp AS TIMESTAMP) AS rating_ts,
                   TRY_CAST(postdate AS TIMESTAMP) AS post_ts
            FROM rating_obs
        ), paired AS (
            SELECT DATE_DIFF('second', post_ts, rating_ts) / 86400.0 AS day_diff
            FROM parsed
            WHERE rating_ts IS NOT NULL AND post_ts IS NOT NULL
        )
        SELECT
            (SELECT COUNT(*) FROM rating_obs) AS rating_observations,
            (SELECT COUNT(*) FROM parsed WHERE rating_ts IS NOT NULL) AS parsed_rating_timestamps,
            (SELECT COUNT(*) FROM parsed WHERE post_ts IS NOT NULL) AS parsed_postdates,
            COUNT(*) AS rows_with_both,
            SUM(day_diff = 0) AS same_timestamp,
            SUM(day_diff > 0) AS rating_after_postdate,
            SUM(day_diff < 0) AS rating_before_postdate,
            QUANTILE_CONT(day_diff, 0.50) AS median_day_diff,
            QUANTILE_CONT(day_diff, 0.90) AS p90_day_diff,
            MAX(day_diff) AS max_day_diff,
            MIN(day_diff) AS min_day_diff
        FROM paired
        """
    ).fetchone()
    timestamp_columns = [
        "rating_observations",
        "parsed_rating_timestamps",
        "parsed_postdates",
        "rows_with_both",
        "same_timestamp",
        "rating_after_postdate",
        "rating_before_postdate",
        "median_day_diff",
        "p90_day_diff",
        "max_day_diff",
        "min_day_diff",
    ]

    duplicate = con.execute(
        """
        WITH pairs AS (
            SELECT user_pseudouserid,
                   game_id,
                   COUNT(*) AS n_observations,
                   COUNT(DISTINCT reviewid) AS n_reviewids,
                   COUNT(DISTINCT rating) AS n_ratings
            FROM rating_obs
            GROUP BY user_pseudouserid, game_id
        )
        SELECT
            (SELECT COUNT(*) FROM rating_obs) AS rating_observations,
            COUNT(*) AS distinct_user_game_pairs,
            SUM(n_observations > 1) AS repeated_user_game_pairs,
            SUM(n_observations - 1) AS repeated_observations,
            MAX(n_observations) AS max_observations_per_pair,
            SUM(n_reviewids > 1) AS repeated_pairs_with_multiple_reviewids,
            SUM(n_ratings > 1) AS repeated_pairs_with_multiple_ratings
        FROM pairs
        """
    ).fetchone()
    duplicate_columns = [
        "rating_observations",
        "distinct_user_game_pairs",
        "repeated_user_game_pairs",
        "repeated_observations",
        "max_observations_per_pair",
        "repeated_pairs_with_multiple_reviewids",
        "repeated_pairs_with_multiple_ratings",
    ]

    global_stats = con.execute(
        f"""
        SELECT COUNT(*) AS users,
               SUM(rating_observations) AS rating_observations,
               AVG(rating_observations) AS mean_observations_per_user,
               QUANTILE_CONT(rating_observations, 0.50) AS median_observations,
               AVG(distinct_games) AS mean_distinct_games,
               QUANTILE_CONT(distinct_games, 0.50) AS median_distinct_games,
               AVG(mean_rating) AS mean_of_user_means,
               STDDEV_SAMP(mean_rating) AS between_user_sd,
               AVG(within_user_sd) AS mean_within_user_sd,
               QUANTILE_CONT(within_user_sd, 0.50) AS median_within_user_sd
        FROM read_parquet('{rater_stats}')
        """
    ).fetchone()
    global_columns = [
        "users",
        "rating_observations",
        "mean_observations_per_user",
        "median_observations",
        "mean_distinct_games",
        "median_distinct_games",
        "mean_of_user_means",
        "between_user_sd",
        "mean_within_user_sd",
        "median_within_user_sd",
    ]

    volume_rows = con.execute(
        f"""
        WITH x AS (SELECT * FROM read_parquet('{volume_summary}') )
        SELECT volume_band,
               COUNT(*) AS users,
               AVG(rating_observations) AS mean_observations,
               QUANTILE_CONT(rating_observations, 0.50) AS median_observations,
               AVG(distinct_games) AS mean_distinct_games,
               QUANTILE_CONT(distinct_games, 0.50) AS median_distinct_games,
               AVG(mean_rating) AS mean_user_mean,
               STDDEV_SAMP(mean_rating) AS between_user_sd,
               AVG(within_user_sd) AS mean_within_user_sd,
               QUANTILE_CONT(within_user_sd, 0.50) AS median_within_user_sd,
               COUNT(split_abs_diff) AS split_stability_users,
               AVG(split_abs_diff) AS mean_split_abs_diff,
               QUANTILE_CONT(split_abs_diff, 0.50) AS median_split_abs_diff,
               QUANTILE_CONT(split_abs_diff, 0.90) AS p90_split_abs_diff
        FROM x
        GROUP BY volume_band
        ORDER BY MIN(rating_observations)
        """
    ).fetchall()
    volume_columns = [
        "volume_band",
        "users",
        "mean_observations",
        "median_observations",
        "mean_distinct_games",
        "median_distinct_games",
        "mean_user_mean",
        "between_user_sd",
        "mean_within_user_sd",
        "median_within_user_sd",
        "split_stability_users",
        "mean_split_abs_diff",
        "median_split_abs_diff",
        "p90_split_abs_diff",
    ]

    summary = {
        "canonical_source": "reviews via ratings.parquet",
        "canonical_definition": "all rows with non-null rating; no user-game or review deduplication",
        "timestamp": dict(zip(timestamp_columns, timestamp)),
        "duplicates": dict(zip(duplicate_columns, duplicate)),
        "global_rater_stats": dict(zip(global_columns, global_stats)),
        "volume_bands": [dict(zip(volume_columns, row)) for row in volume_rows],
        "stability_definition": "source_rowid parity split for users with >=20 rating observations; not temporal because timestamp semantics are unresolved",
        "alternate_source": "user_ratings.parquet retained separately; username does not join to users and has no timestamps",
    }
    SEMANTICS_JSON.write_text(json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2, default=str))
    con.close()


if __name__ == "__main__":
    main()

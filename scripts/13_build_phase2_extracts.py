"""Build compact, read-only Phase 2 Parquet extracts from bgg.sqlite.

The SQLite source is opened in read-only mode and is never modified.  This
script preserves review/collection source rows, including duplicate
user-game records, and adds SQLite rowid as a snapshot-local source key.
It does not perform rating, audience, or debiasing analysis.
"""

import json
import sqlite3
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


REPO_DIR = Path(__file__).resolve().parent.parent
SQLITE_PATH = REPO_DIR / "data" / "raw" / "bgg.sqlite"
OUTPUT_DIR = REPO_DIR / "data" / "processed" / "phase2"
CHUNK_SIZE = 250_000


def connect_read_only():
    con = sqlite3.connect(f"file:{SQLITE_PATH}?mode=ro", uri=True)
    con.execute("PRAGMA query_only=ON")
    con.execute("PRAGMA temp_store=MEMORY")
    return con


def write_query(con, sql, output_name):
    """Stream a query to compressed Parquet without materializing all rows."""
    output_path = OUTPUT_DIR / output_name
    cur = con.cursor()
    cur.execute(sql)
    columns = [description[0] for description in cur.description]
    writer = None
    total = 0
    try:
        while True:
            rows = cur.fetchmany(CHUNK_SIZE)
            if not rows:
                break
            frame = pd.DataFrame.from_records(rows, columns=columns)
            table = pa.Table.from_pandas(frame, preserve_index=False)
            if writer is None:
                writer = pq.ParquetWriter(
                    output_path,
                    table.schema,
                    compression="zstd",
                    compression_level=5,
                    use_dictionary=True,
                )
            else:
                table = table.cast(writer.schema, safe=False)
            writer.write_table(table)
            total += len(frame)
            print(f"  {output_name}: {total:,} rows", flush=True)
    finally:
        if writer is not None:
            writer.close()
        cur.close()
    if writer is None:
        raise RuntimeError(f"Query returned no rows: {output_name}")
    return output_path, total


def validate_samples(con):
    """Validate representative joins and expose source-key semantics."""
    candidate_ids = [436591, 336323, 245240, 188885, 350108]
    marks = ",".join("?" for _ in candidate_ids)
    checks = {}

    checks["candidate_game_attrs_to_games"] = con.execute(
        f"""
        SELECT COUNT(*) AS attrs_rows,
               SUM(g.game_id IS NOT NULL) AS matched_games
        FROM game_attrs a
        LEFT JOIN games g ON g.game_id = a.game_id
        WHERE a.game_id IN ({marks})
        """,
        candidate_ids,
    ).fetchone()

    checks["candidate_reviews_to_users"] = con.execute(
        f"""
        SELECT COUNT(*) AS review_rows,
               SUM(u.user_pseudouserid IS NOT NULL) AS matched_users,
               COUNT(DISTINCT r.user_pseudouserid) AS sampled_users
        FROM reviews r
        LEFT JOIN users u ON u.user_pseudouserid = r.user_pseudouserid
        WHERE r.game_id IN ({marks})
        """,
        candidate_ids,
    ).fetchone()

    checks["candidate_reviews_to_collections"] = con.execute(
        f"""
        SELECT COUNT(*) AS sampled_review_rows,
               SUM(c.rowid IS NOT NULL) AS matched_collection_rows
        FROM reviews r
        LEFT JOIN collections c
          ON c.game_id = r.game_id
         AND c.reviewid = r.reviewid
         AND c.user_pseudouserid = r.user_pseudouserid
        WHERE r.game_id IN ({marks})
        """,
        candidate_ids,
    ).fetchone()

    # Use a deterministic rowid sample from across the review table.  This is
    # a join check, not a population estimate.
    checks["deterministic_reviews_to_users_collections"] = con.execute(
        """
        SELECT COUNT(*) AS sampled_review_rows,
               SUM(u.user_pseudouserid IS NOT NULL) AS matched_users,
               SUM(c.rowid IS NOT NULL) AS matched_collections
        FROM (
            SELECT rowid, game_id, reviewid, user_pseudouserid
            FROM reviews
            WHERE rowid % 100003 < 3
            LIMIT 10_000
        ) r
        LEFT JOIN users u ON u.user_pseudouserid = r.user_pseudouserid
        LEFT JOIN collections c
          ON c.game_id = r.game_id
         AND c.reviewid = r.reviewid
         AND c.user_pseudouserid = r.user_pseudouserid
        """
    ).fetchone()

    # Small, explicit duplicate audit examples.  We preserve these rows in
    # the extract; downstream code must choose a documented event policy.
    checks["carcassonne_duplicate_semantics"] = con.execute(
        """
        SELECT game_id, COUNT(*) AS rows, COUNT(DISTINCT reviewid) AS reviewids,
               COUNT(DISTINCT user_pseudouserid) AS users
        FROM reviews
        WHERE game_id IN (822, 30662)
        GROUP BY game_id
        ORDER BY game_id
        """
    ).fetchall()
    checks["timestamp_examples"] = [
        list(row)
        for row in con.execute(
            """
            SELECT game_id, reviewid, rating, rating_tstamp,
                   comment_tstamp, postdate
            FROM reviews
            WHERE game_id IN (188885, 245240)
              AND rating IS NOT NULL
            ORDER BY game_id, reviewid
            LIMIT 8
            """
        )
    ]

    def normalize(value):
        if isinstance(value, tuple):
            return list(value)
        if isinstance(value, list):
            return [normalize(item) for item in value]
        return value

    return {key: normalize(value) for key, value in checks.items()}


def main():
    if not SQLITE_PATH.exists():
        raise FileNotFoundError(SQLITE_PATH)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    con = connect_read_only()
    try:
        validation = validate_samples(con)
        print("Validation:", json.dumps(validation, indent=2), flush=True)
        (OUTPUT_DIR / "validation.json").write_text(
            json.dumps(validation, indent=2) + "\n", encoding="utf-8"
        )

        queries = [
            (
                """
                SELECT a.game_id,
                       COALESCE(g.title, a.name) AS title,
                       a.name,
                       COALESCE(g.year, a.year) AS year,
                       g.rank,
                       g.geek_rating,
                       g.avg_rating AS browse_avg_rating,
                       g.voters AS browse_voters,
                       a.min_players, a.max_players, a.best_players,
                       a.good_players, a.mfg_playtime,
                       a.com_min_playtime, a.com_max_playtime,
                       a.mfg_age_rec, a.com_age_rec, a.language_ease,
                       a.avg_rating, a.bayes_rating, a.stddev,
                       a.num_user_ratings, a.num_comments,
                       a.num_owned, a.num_want, a.num_wish,
                       a.num_alternates, a.num_expansions,
                       a.num_implementations, a.is_reimplementation,
                       a.kickstarted, a.family, a.source,
                       w.weight, w.num_votes AS weight_num_votes,
                       w.source AS weight_source
                FROM game_attrs a
                LEFT JOIN games g ON g.game_id = a.game_id
                LEFT JOIN weights w ON w.game_id = a.game_id
                ORDER BY a.game_id
                """,
                "games.parquet",
            ),
            (
                """
                SELECT user_pseudouserid, state, country,
                       mb0_tstamp, mb1_tstamp, mb2_tstamp,
                       mb3_tstamp, mb4_tstamp
                FROM users
                ORDER BY user_pseudouserid
                """,
                "users.parquet",
            ),
            (
                """
                SELECT rowid AS source_rowid, game_id, rating, username
                FROM user_ratings
                ORDER BY rowid
                """,
                "user_ratings.parquet",
            ),
            (
                """
                SELECT rowid AS source_rowid, game_id, reviewid,
                       user_pseudouserid, rating, rating_tstamp,
                       comment_tstamp, postdate
                FROM reviews
                ORDER BY rowid
                """,
                "ratings.parquet",
            ),
            (
                """
                SELECT rowid AS source_rowid, game_id, reviewid,
                       user_pseudouserid, own, status_tstamp,
                       wishlistpriority, wanttoplay, preordered,
                       prevowned, wishlist, want, wanttobuy, fortrade
                FROM collections
                ORDER BY rowid
                """,
                "collections.parquet",
            ),
            (
                """
                SELECT game_id, tag_type, tag
                FROM game_tags
                ORDER BY game_id, tag_type, tag
                """,
                "game_tags.parquet",
            ),
            (
                """
                SELECT game_id, rel, other_id, other_name
                FROM game_links
                ORDER BY game_id, rel, other_id
                """,
                "game_links.parquet",
            ),
        ]
        counts = {}
        for sql, filename in queries:
            _, counts[filename] = write_query(con, sql, filename)
        (OUTPUT_DIR / "extract_counts.json").write_text(
            json.dumps(counts, indent=2) + "\n", encoding="utf-8"
        )
        print("Extract counts:", json.dumps(counts, indent=2), flush=True)
    finally:
        con.close()


if __name__ == "__main__":
    main()

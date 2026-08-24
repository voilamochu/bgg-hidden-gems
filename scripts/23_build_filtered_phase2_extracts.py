"""Build the filtered Phase 2 analytical universe for the research population.

Filters the Phase 2 Parquet extracts to the 16,627-game research population
(`data/processed/bgg_research_population.parquet`) using explicit SEMI JOINs,
preserving the canonical observation definition from `scripts/13`/`14`: every
non-null rating row, no deduplication, source keys retained.

Outputs under `data/processed/phase2-filtered/`:
  - rating_observations_filtered.parquet  canonical ratings, population games only
  - games_filtered.parquet                game_attrs/games/weights metadata rows
  - game_tags_filtered.parquet            normalized tags
  - game_links_filtered.parquet           game relationship rows
  - users_filtered.parquet                users with >=1 filtered rating
  - collections_filtered.parquet          collection/status rows, population games
  - validation.json / extract_counts.json
  - parquet_catalog.csv (every Phase 2 Parquet: contents, full vs filtered counts, % retained)
  - README.md (filtered-universe documentation)

Deliberately NOT filtered/copied here:
  - ratings.parquet (null-rating review rows; the canonical rating universe is
    rating_observations)
  - user_ratings.parquet (username namespace does not join to `users`; non-canonical)
Derived Phase 2 artifacts (rater_stats, severity offsets, adjusted means, ...)
are NOT regenerated on the filtered universe by this script; that
re-estimation belongs to the follow-up taste task.

Reproducibility: run against the committed extracts, e.g.
  python scripts/23_build_filtered_phase2_extracts.py \
      --input-dir scratch/phase2 \
      --population scratch/phase2/bgg_research_population.parquet
"""

import argparse
import csv
import json
import time
from pathlib import Path

import duckdb


# (full-snapshot file, filtered output file or None, one-line description).
# Filtered = rows restricted to the 16,627 research-population game_ids,
# except users where the filter is raters with >=1 such rating.
CATALOG = [
    ("rating_observations.parquet", "rating_observations_filtered.parquet",
     "Canonical individual rating observations: every non-null review rating, no deduplication, source keys retained"),
    ("games.parquet", "games_filtered.parquet",
     "Per-game metadata: game_attrs joined to browse fields and weight ratings"),
    ("users.parquet", "users_filtered.parquet",
     "Pseudonymous rater profiles (state/country, message-board timestamps)"),
    ("collections.parquet", "collections_filtered.parquet",
     "Collection/status rows paired to review records (own/wishlist/preorder flags, status_tstamp)"),
    ("game_tags.parquet", "game_tags_filtered.parquet",
     "Normalized game tags (category/mechanic/theme taxonomy)"),
    ("game_links.parquet", "game_links_filtered.parquet",
     "Game relationship links (expansions, reimplementations, etc.)"),
    ("ratings.parquet", None,
     "All review rows incl. null-rating comment rows; not filtered because the canonical rating universe is rating_observations"),
    ("user_ratings.parquet", None,
     "Compact alternate rating snapshot; not filtered because its username namespace does not join to users (non-canonical)"),
]

NOT_REGENERATED_DERIVED = [
    "rater_stats.parquet",
    "rater_behavior_by_volume.parquet",
    "user_severity.parquet",
    "game_adjusted_means.parquet",
]


REPO_DIR = Path(__file__).resolve().parent.parent
DEFAULT_INPUT_DIR = REPO_DIR / "data" / "processed" / "phase2"
DEFAULT_POPULATION = REPO_DIR / "data" / "processed" / "bgg_research_population.parquet"
DEFAULT_OUTPUT_DIR = REPO_DIR / "data" / "processed" / "phase2-filtered"

SPOT_CHECK_IDS = [436591, 336323, 245240, 188885, 350108]

MEMORY_LIMIT = "4GB"
THREADS = 4


def qpath(path):
    return str(path).replace("'", "''")


def configure(con, output_dir):
    con.execute(f"SET memory_limit='{MEMORY_LIMIT}'")
    con.execute(f"SET threads={THREADS}")
    temp_dir = output_dir / ".tmp_duckdb"
    temp_dir.mkdir(parents=True, exist_ok=True)
    con.execute(f"SET temp_directory='{qpath(temp_dir)}'")
    con.execute("SET preserve_insertion_order=false")
    return temp_dir


def copy_semi_join(con, source, pop_view, key, order_by, dest):
    select_sql = f"""
        SELECT s.*
        FROM read_parquet('{qpath(source)}') s
        SEMI JOIN {pop_view} p ON p.game_id = s.{key}
        ORDER BY {order_by}
    """
    plan = con.execute("EXPLAIN " + select_sql).fetchone()[1]
    assert "Join Type: SEMI" in plan, f"planner did not emit a semi join for {dest.name}"
    t0 = time.time()
    con.execute(
        f"COPY ({select_sql}) TO '{qpath(dest)}' (FORMAT PARQUET, COMPRESSION ZSTD)"
    )
    print(f"  {dest.name}: done in {time.time() - t0:.1f}s", flush=True)


def scalar(con, sql):
    return con.execute(sql).fetchone()[0]


def validate(con, input_dir, population, output_dir):
    checks = {}
    src = output_dir / "rating_observations_filtered.parquet"

    def v(key, value):
        checks[key] = value

    pop_rows, pop_distinct = con.execute(
        f"SELECT COUNT(*), COUNT(DISTINCT game_id) FROM read_parquet('{qpath(population)}')"
    ).fetchone()
    v("population_rows", pop_rows)
    v("population_distinct_game_ids", pop_distinct)
    assert pop_rows == pop_distinct == 16_627

    # Anchor: independent count straight off the unfiltered source. Equality
    # with the output row count proves the semi join neither duplicated nor
    # dropped rows.
    anchor = scalar(
        con,
        f"""
        SELECT COUNT(*) FROM read_parquet('{qpath(input_dir / 'rating_observations.parquet')}') r
        SEMI JOIN read_parquet('{qpath(population)}') p ON p.game_id = r.game_id
        """,
    )
    out_rows = scalar(con, f"SELECT COUNT(*) FROM read_parquet('{qpath(src)}')")
    v("rating_observations_source_total", 26_924_709)
    v("rating_observations_anchor_restricted_to_population", anchor)
    v("rating_observations_filtered_rows", out_rows)
    v(
        "rating_observations_share_of_full_snapshot",
        round(out_rows / 26_924_709, 6),
    )
    assert out_rows == anchor

    distinct_games, distinct_users = con.execute(
        f"SELECT COUNT(DISTINCT game_id), COUNT(DISTINCT user_pseudouserid) FROM read_parquet('{qpath(src)}')"
    ).fetchone()
    v("filtered_distinct_game_ids", distinct_games)
    v("filtered_distinct_users", distinct_users)

    missing = con.execute(
        f"""
        SELECT COUNT(*) FROM read_parquet('{qpath(population)}') p
        ANTI JOIN read_parquet('{qpath(src)}') r ON r.game_id = p.game_id
        """
    ).fetchone()[0]
    v("population_games_absent_from_sqlite_snapshot", missing)
    v(
        "population_games_absent_examples",
        [
            {"game_id": gid, "title": title}
            for gid, title in con.execute(
                f"""
                SELECT p.game_id, p.title FROM read_parquet('{qpath(population)}') p
                ANTI JOIN read_parquet('{qpath(src)}') r ON r.game_id = p.game_id
                ORDER BY p.users_rated DESC LIMIT 10
                """
            ).fetchall()
        ],
    )

    unmatched_users = scalar(
        con,
        f"""
        SELECT COUNT(*) FROM read_parquet('{qpath(src)}') r
        ANTI JOIN read_parquet('{qpath(output_dir / 'users_filtered.parquet')}') u
          ON u.user_pseudouserid = r.user_pseudouserid
        """,
    )
    v("filtered_ratings_without_users_row", unmatched_users)
    assert unmatched_users == 0

    users_not_in_source_users = scalar(
        con,
        f"""
        SELECT COUNT(*) FROM read_parquet('{qpath(output_dir / 'users_filtered.parquet')}') u
        ANTI JOIN read_parquet('{qpath(input_dir / 'users.parquet')}') su
          ON su.user_pseudouserid = u.user_pseudouserid
        """,
    )
    v("filtered_users_missing_from_source_users", users_not_in_source_users)
    assert users_not_in_source_users == 0

    rated_games, matched_games = con.execute(
        f"""
        SELECT COUNT(DISTINCT r.game_id),
               COUNT(DISTINCT g.game_id)
        FROM read_parquet('{qpath(src)}') r
        LEFT JOIN read_parquet('{qpath(output_dir / 'games_filtered.parquet')}') g
          ON g.game_id = r.game_id
        """
    ).fetchone()
    v("rated_games_with_games_metadata", {
        "rated_games": rated_games,
        "with_games_metadata": matched_games,
        "share": round(matched_games / rated_games, 6),
    })

    sample_rows, matched_collections = con.execute(
        f"""
        WITH sample AS (
            SELECT game_id, reviewid, user_pseudouserid
            FROM read_parquet('{qpath(src)}')
            WHERE rating_observation_id % 9973 = 0
        ),
        matched AS (
            SELECT s.game_id
            FROM sample s
            SEMI JOIN read_parquet('{qpath(output_dir / 'collections_filtered.parquet')}') c
              ON c.game_id = s.game_id
             AND c.reviewid = s.reviewid
             AND c.user_pseudouserid = s.user_pseudouserid
        )
        SELECT (SELECT COUNT(*) FROM sample), (SELECT COUNT(*) FROM matched)
        """
    ).fetchone()
    v("collection_triple_join_sample", {
        "sampled_observations": int(sample_rows),
        "matched_observations": int(matched_collections),
    })
    assert sample_rows > 0 and matched_collections == sample_rows, (
        f"collection triple-match {matched_collections}/{sample_rows} != 100%"
    )

    spot = []
    id_list = ",".join(str(i) for i in SPOT_CHECK_IDS)
    filtered_counts = dict(
        con.execute(
            f"SELECT game_id, COUNT(*) FROM read_parquet('{qpath(src)}') WHERE game_id IN ({id_list}) GROUP BY game_id"
        ).fetchall()
    )
    source_counts = dict(
        con.execute(
            f"""
            SELECT game_id, COUNT(*) FROM read_parquet('{qpath(input_dir / 'rating_observations.parquet')}')
            WHERE game_id IN ({id_list}) GROUP BY game_id
            """
        ).fetchall()
    )
    titles = dict(
        con.execute(
            f"SELECT game_id, title FROM read_parquet('{qpath(population)}') WHERE game_id IN ({id_list})"
        ).fetchall()
    )
    for gid in SPOT_CHECK_IDS:
        ok = filtered_counts.get(gid) == source_counts.get(gid)
        assert ok, f"spot-check mismatch for game_id {gid}"
        spot.append({
            "game_id": gid,
            "title": titles.get(gid),
            "observation_count": filtered_counts.get(gid, 0),
        })
    v("spot_check_shortlist", spot)

    repeated_pairs, repeated_obs, max_per_pair = con.execute(
        f"""
        SELECT COUNT(*) FILTER (WHERE n > 1),
               COALESCE(SUM(n) FILTER (WHERE n > 1), 0),
               MAX(n)
        FROM (
            SELECT COUNT(*) AS n
            FROM read_parquet('{qpath(src)}')
            GROUP BY game_id, user_pseudouserid
        )
        """
    ).fetchone()
    v("repeated_user_game_pairs_preserved", {
        "pairs_with_repeats": int(repeated_pairs),
        "observations_in_repeated_pairs": int(repeated_obs),
        "max_observations_one_pair": int(max_per_pair),
    })
    return checks


def write_readme(output_dir, input_dir, population, catalog_rows):
    lines = [
        "# Filtered Phase 2 analytical universe",
        "",
        f"Primary analytical inputs restricted to the **{16_627:,}-game research population**",
        f"(`{population}`), built by `scripts/01_clean_population.py`. Generated by",
        "`scripts/23_build_filtered_phase2_extracts.py`; do not edit by hand.",
        "",
        "The canonical observation definition is unchanged from `scripts/13`/`14`: every",
        "non-null review rating, no deduplication, source keys (`rating_observation_id`,",
        "`source_rowid`) retained. Filtering uses explicit SEMI JOINs on `game_id`, so rows",
        "are neither duplicated nor dropped. The unfiltered extracts in",
        f"`{input_dir}` (default `data/processed/phase2/`) remain untouched.",
        "",
        "## Parquet catalog (full snapshot vs filtered)",
        "",
        "| Full file | Filtered file | Contains | Records (full) | Records (filtered) | % retained |",
        "|---|---|---|---:|---:|---:|",
    ]
    for row in catalog_rows:
        full_n = f"{row['records_full']:,}" if row["records_full"] is not None else "n/a"
        filtered_n = f"{row['records_filtered']:,}" if row["records_filtered"] is not None else "not filtered"
        pct = f"{row['pct_retained']}%" if row["pct_retained"] is not None else "n/a"
        lines.append(
            f"| `{row['full_file']}` | "
            + (f"`{row['filtered_file']}`" if row["filtered_file"] else "(none)")
            + f" | {row['contains']} | {full_n} | {filtered_n} | {pct} |"
        )
    lines += [
        "",
        "Derived Phase 2 artifacts (`" + "`, `".join(NOT_REGENERATED_DERIVED) + "`)",
        "remain FULL-SNAPSHOT artifacts under `data/processed/phase2/`; they are not",
        "regenerated here. Re-estimation on the filtered universe happens in the follow-up",
        "taste task; do not mix filtered observations with full-snapshot fit artifacts.",
        "",
        "## Reproduce",
        "",
        "```bash",
        "python scripts/23_build_filtered_phase2_extracts.py \\",
        f"    --input-dir {input_dir} --population {population}",
        "```",
        "",
        "Validations are recorded in `validation.json` (row-count anchors against the",
        "unfiltered source, 100% user/collection join checks, deterministic per-game spot",
        "checks) and `extract_counts.json` / `parquet_catalog.csv`.",
        "",
        "## Known caveats carried over from Phase 2",
        "",
        "- The SQLite snapshot differs from the game-level scrape: a few research-population",
        "  games have no rating rows here at all; see",
        "  `population_games_absent_from_sqlite_snapshot` in `validation.json`.",
        "- Repeated user-game rows are preserved as distinct observations (~0.007%).",
        "- `postdate`/`rating_tstamp` semantics remain unresolved; keep dual readings for any",
        "  time-based result.",
        "",
    ]
    (output_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR,
                    help="directory holding the unfiltered phase2 extracts")
    ap.add_argument("--population", type=Path, default=DEFAULT_POPULATION,
                    help="research population parquet defining the game universe")
    ap.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = ap.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    temp_dir = configure(con, args.output_dir)

    try:
        pop_view = "pop"
        con.execute(
            f"CREATE OR REPLACE TEMP VIEW {pop_view} AS "
            f"SELECT game_id FROM read_parquet('{qpath(args.population)}')"
        )

        jobs = [
            ("ratings", "rating_observations.parquet", "game_id",
             "rating_observation_id", "rating_observations_filtered.parquet"),
            ("games", "games.parquet", "game_id", "game_id", "games_filtered.parquet"),
            ("tags", "game_tags.parquet", "game_id", "game_id, tag_type, tag",
             "game_tags_filtered.parquet"),
            ("links", "game_links.parquet", "game_id", "game_id, rel, other_id",
             "game_links_filtered.parquet"),
            ("collections", "collections.parquet", "game_id", "source_rowid",
             "collections_filtered.parquet"),
        ]
        for label, src_name, key, order_by, out_name in jobs:
            src = args.input_dir / src_name
            if not src.exists():
                raise FileNotFoundError(src)
            print(f"Filtering {label} -> {out_name}", flush=True)
            copy_semi_join(con, src, pop_view, key, order_by, args.output_dir / out_name)

        print("Building users_filtered.parquet", flush=True)
        con.execute(f"""
            COPY (
                SELECT u.*
                FROM read_parquet('{qpath(args.input_dir / 'users.parquet')}') u
                SEMI JOIN (
                    SELECT DISTINCT user_pseudouserid
                    FROM read_parquet('{qpath(args.output_dir / 'rating_observations_filtered.parquet')}')
                ) ru ON ru.user_pseudouserid = u.user_pseudouserid
                ORDER BY u.user_pseudouserid
            ) TO '{qpath(args.output_dir / 'users_filtered.parquet')}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """)

        counts = {}
        for name in [j[4] for j in jobs] + ["users_filtered.parquet"]:
            n = scalar(con, f"SELECT COUNT(*) FROM read_parquet('{qpath(args.output_dir / name)}')")
            counts[name] = int(n)
        counts_input = {}
        for name in ["rating_observations.parquet", "games.parquet", "game_tags.parquet",
                     "game_links.parquet", "collections.parquet", "users.parquet"]:
            n = scalar(con, f"SELECT COUNT(*) FROM read_parquet('{qpath(args.input_dir / name)}')")
            counts_input[name] = int(n)
        for name in ["ratings.parquet", "user_ratings.parquet"]:
            p = args.input_dir / name
            counts_input[name] = int(scalar(
                con, f"SELECT COUNT(*) FROM read_parquet('{qpath(p)}')")) if p.exists() else None
        (args.output_dir / "extract_counts.json").write_text(
            json.dumps({"universe_game_ids": 16_627, "outputs": counts, "inputs": counts_input},
                       indent=2) + "\n",
            encoding="utf-8",
        )
        print("Extract counts:", json.dumps(counts, indent=2), flush=True)

        catalog_rows = []
        for full_name, filtered_name, description in CATALOG:
            full_n = counts_input.get(full_name)
            filtered_n = counts.get(filtered_name) if filtered_name else None
            pct = (100.0 * filtered_n / full_n) if (filtered_n is not None and full_n) else None
            catalog_rows.append({
                "full_file": f"data/processed/phase2/{full_name}",
                "filtered_file": f"data/processed/phase2-filtered/{filtered_name}" if filtered_name else "",
                "contains": description,
                "records_full": full_n,
                "records_filtered": filtered_n,
                "pct_retained": round(pct, 3) if pct is not None else None,
            })
        catalog_path = args.output_dir / "parquet_catalog.csv"
        with open(catalog_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(catalog_rows[0]))
            writer.writeheader()
            writer.writerows(catalog_rows)
        print(f"Wrote {catalog_path}", flush=True)

        write_readme(args.output_dir, args.input_dir, args.population, catalog_rows)
        print("Running validations", flush=True)
        checks = validate(con, args.input_dir, args.population, args.output_dir)
        (args.output_dir / "validation.json").write_text(
            json.dumps(checks, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(checks, indent=2), flush=True)
    finally:
        con.close()
        if temp_dir.exists():
            for p in temp_dir.iterdir():
                p.unlink()
            temp_dir.rmdir()


if __name__ == "__main__":
    main()

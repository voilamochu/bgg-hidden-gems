"""Phase B step 6: audience-level rating differences and self-selection.

Audiences observable in this snapshot:
  - Geography (users.country): top countries as audience proxies.
  - Ownership status per rating observation (collections.own joined on
    source_rowid -> rating_observation_id): owners vs non-owners raters.

Questions:
  1. Do audiences rate systematically differently?  Raw level differences,
     then paired within-game contrasts between audience pairs (same design
     as script 15) to separate level differences from game mix.
  2. Does participation itself select?  Per-country game-mix profiles
     (which games each audience rates, tag composition of those games).
  3. Do owners rate the same games like non-owner raters?  Within-game
     own-vs-not contrast, plus wishlist-only raters.

Caveats: country is user-reported and missing for 195,460 of 606,497 users;
collection flags are statuses at snapshot time, not event history.
"""

import argparse
import json
from pathlib import Path

import duckdb

REPO_DIR = Path(__file__).resolve().parent.parent


def q(path) -> str:
    return str(path).replace("'", "''")


TOP_COUNTRIES = ["United States", "Germany", "United Kingdom", "Canada",
                 "Spain", "Poland", "France", "Australia", "Italy",
                 "Netherlands"]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", type=Path, default=None)
    ap.add_argument("--out-dir", type=Path, default=REPO_DIR / "data" / "processed" / "phase2")
    ap.add_argument("--min-cell", type=int, default=3)
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
    con.execute(f"CREATE OR REPLACE VIEW usrs AS SELECT * FROM read_parquet('{q(data_dir / 'users.parquet')}')")
    con.execute(f"CREATE OR REPLACE VIEW cols AS SELECT * FROM read_parquet('{q(data_dir / 'collections.parquet')}')")
    con.execute(f"CREATE OR REPLACE VIEW tags AS SELECT * FROM read_parquet('{q(data_dir / 'game_tags.parquet')}')")

    summary = {"data_dir": str(data_dir)}

    # Observations with country audience attached (top-N countries only)
    country_list = ",".join(f"'{c}'" for c in TOP_COUNTRIES)
    con.execute(f"""
        CREATE OR REPLACE VIEW obs_geo AS
        SELECT r.rating_observation_id, r.game_id, r.user_pseudouserid,
               u.country
        FROM ro r JOIN usrs u USING (user_pseudouserid)
        WHERE u.country IN ({country_list})
    """)

    # ------------------------------------------------------------------
    # 1a. Raw audience levels
    # ------------------------------------------------------------------
    raw_levels = con.execute("""
        SELECT o.country, COUNT(*) AS n_obs, COUNT(DISTINCT r.game_id) AS n_games,
               AVG(r.rating) AS mean_rating
        FROM obs_geo o JOIN ro r ON o.rating_observation_id = r.rating_observation_id
        GROUP BY 1 ORDER BY 2 DESC
    """).fetchdf()
    summary["raw_country_levels"] = raw_levels.to_dict(orient="records")

    # ------------------------------------------------------------------
    # 1b. Paired within-game country contrasts (US as reference hub)
    # ------------------------------------------------------------------
    contrasts = []
    us_games = set(g for (g,) in con.execute(
        "SELECT DISTINCT game_id FROM obs_geo WHERE country='United States'").fetchall())
    for c in TOP_COUNTRIES:
        if c == "United States":
            continue
        other_games = set(g for (g,) in con.execute(
            "SELECT DISTINCT game_id FROM obs_geo WHERE country = ?", [c]).fetchall())
        shared = us_games & other_games
        if not shared:
            continue
        shared_ids = ",".join(str(int(g)) for g in sorted(shared))
        r = con.execute(f"""
            WITH cells AS (
                SELECT r.game_id, g.country, COUNT(*) AS n, AVG(r.rating) AS m
                FROM obs_geo g JOIN ro r ON g.rating_observation_id = r.rating_observation_id
                WHERE r.game_id IN ({shared_ids})
                GROUP BY 1, 2
            ), p AS (
                SELECT game_id,
                       MAX(CASE WHEN country='United States' THEN m END) AS m_us,
                       MAX(CASE WHEN country='{c.replace("'", "''")}' THEN m END) AS m_ot,
                       MAX(CASE WHEN country='United States' THEN n END) AS n_us,
                       MAX(CASE WHEN country='{c.replace("'", "''")}' THEN n END) AS n_ot
                FROM cells GROUP BY game_id
                HAVING MAX(CASE WHEN country='United States' THEN n END) >= {args.min_cell}
                   AND MAX(CASE WHEN country='{c.replace("'", "''")}' THEN n END) >= {args.min_cell}
            )
            SELECT COUNT(*),
                   AVG(m_ot - m_us),
                   QUANTILE_CONT(m_ot - m_us, 0.5)
            FROM p
        """).fetchone()
        contrasts.append({
            "country": c, "games_any_shared": len(shared),
            f"games_paired_min{args.min_cell}": int(r[0]),
            "mean_other_minus_us_within_game": float(r[1]),
            "median_other_minus_us": float(r[2]),
        })
    summary["within_game_country_vs_us"] = {
        "min_cell": args.min_cell, "rows": contrasts}

    # ------------------------------------------------------------------
    # 2. Game-mix selection: tag profile of each audience's rated games
    # ------------------------------------------------------------------
    def tag_share(country: str, min_cell: int) -> dict:
        rows = con.execute(f"""
            WITH aud AS (
                SELECT game_id FROM obs_geo WHERE country='{country}'
                GROUP BY game_id HAVING COUNT(*) >= {min_cell}
            )
            SELECT t.tag_type || ':' || t.tag AS tagk, COUNT(*) AS n
            FROM tags t SEMI JOIN aud a ON t.game_id = a.game_id
            GROUP BY 1 ORDER BY n DESC
        """).fetchall()
        total_aud_games = con.execute(f"""
            SELECT COUNT(*) FROM (
                SELECT game_id FROM obs_geo WHERE country='{country}'
                GROUP BY game_id HAVING COUNT(*) >= {min_cell}
            )""").fetchone()[0]
        return {k: (n, n / total_aud_games) for k, n in rows}, int(total_aud_games)

    us_prof, us_n = tag_share("United States", args.min_cell)
    de_prof, de_n = tag_share("Germany", args.min_cell)
    common = set(us_prof) & set(de_prof)
    diffs = []
    for k in common:
        p_us = us_prof[k][1]; p_de = de_prof[k][1]
        if us_prof[k][0] + de_prof[k][0] >= 200:
            diffs.append((k, p_de - p_us))
    diffs.sort(key=lambda x: x[1])
    summary["germany_vs_us_tag_mix"] = {
        "us_games_rated_by_ge_cell": us_n, "de_games_rated_by_ge_cell": de_n,
        "most_relative_germany": [{"tag": k, "share_de": round(de_prof[k][1], 4),
                                   "share_us": round(us_prof[k][1], 4)}
                                  for k, _ in reversed(diffs[-12:])],
        "most_relative_us": [{"tag": k, "share_de": round(de_prof[k][1], 4),
                              "share_us": round(us_prof[k][1], 4)}
                             for k, _ in diffs[:12]],
    }

    # ------------------------------------------------------------------
    # 3. Ownership: attach collections.own to observations
    # ------------------------------------------------------------------
    con.execute("""
        CREATE OR REPLACE VIEW obs_own AS
        SELECT r.rating_observation_id, r.game_id, r.user_pseudouserid,
               r.rating,
               CASE WHEN c.own THEN 'own' ELSE 'notown' END AS own_status
        FROM ro r JOIN cols c ON r.rating_observation_id = c.source_rowid
        WHERE r.rating IS NOT NULL
    """)
    own_raw = con.execute("""
        SELECT own_status, COUNT(*) AS n, AVG(rating) AS m
        FROM obs_own GROUP BY 1
    """).fetchdf()
    summary["raw_own_levels"] = own_raw.to_dict(orient="records")
    own_contrast = con.execute(f"""
        WITH cells AS (
            SELECT game_id, own_status, COUNT(*) AS n, AVG(rating) AS m
            FROM obs_own GROUP BY 1, 2
        ), p AS (
            SELECT game_id,
                   MAX(CASE WHEN own_status='own' THEN m END) AS m_o,
                   MAX(CASE WHEN own_status='notown' THEN m END) AS m_n,
                   MAX(CASE WHEN own_status='own' THEN n END) AS n_o,
                   MAX(CASE WHEN own_status='notown' THEN n END) AS n_n
            FROM cells GROUP BY game_id
            HAVING MAX(CASE WHEN own_status='own' THEN n END) >= {args.min_cell}
               AND MAX(CASE WHEN own_status='notown' THEN n END) >= {args.min_cell}
        )
        SELECT COUNT(*), AVG(m_n - m_o), QUANTILE_CONT(m_n - m_o, 0.5)
        FROM p
    """).fetchone()
    summary["within_game_notown_minus_own"] = {
        "min_cell": args.min_cell, "n_games_paired": int(own_contrast[0]),
        "mean_gap": float(own_contrast[1]), "median_gap": float(own_contrast[2])}

    (out_dir / "audience_selection.json").write_text(
        json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")

    print(json.dumps({k: summary[k] for k in [
        "raw_country_levels", "within_game_country_vs_us",
        "raw_own_levels", "within_game_notown_minus_own"]},
        indent=1, default=str)[:4500])
    con.close()


if __name__ == "__main__":
    main()

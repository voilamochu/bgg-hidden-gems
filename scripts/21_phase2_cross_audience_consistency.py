"""Phase B step 7: cross-audience consistency of game ratings.

Do games high-rated by one audience hold up with another?  Uses the
audience proxies available in the snapshot:
  - geography (top countries), and
  - ownership status per rating observation.

Method: for each pair of audiences A/B and each game rated by >=min_cell
distinct raters in BOTH, compute audience-specific means; summarize the
distribution of standardized differences, the cross-audience correlation of
game means, and profile the most divergent games via tags.

Caveat: divergence can reflect genuine audience-taste differences, rater-mix
severity differences within an audience, or small-sample noise; the
standardized difference uses a pooled within-cell SD as its scale.
"""

import argparse
import json
from pathlib import Path

import duckdb

REPO_DIR = Path(__file__).resolve().parent.parent

TOP_COUNTRIES = ["United States", "Germany", "Canada", "United Kingdom",
                 "Spain", "Poland", "France", "Italy"]


def q(path) -> str:
    return str(path).replace("'", "''")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", type=Path, default=None)
    ap.add_argument("--out-dir", type=Path, default=REPO_DIR / "data" / "processed" / "phase2")
    ap.add_argument("--min-cell", type=int, default=10)
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

    summary = {"data_dir": str(data_dir), "min_cell": args.min_cell}

    # ------------------------------------------------------------------
    # Geography pairs
    # ------------------------------------------------------------------
    clist = ",".join(f"'{c}'" for c in TOP_COUNTRIES)
    con.execute(f"""
        CREATE OR REPLACE VIEW geo_cells AS
        SELECT r.game_id AS game_id, u.country AS audience,
               COUNT(*) AS n_users, AVG(r.rating) AS mean_rating,
               STDDEV_SAMP(r.rating) AS sd_rating
        FROM ro r JOIN usrs u USING (user_pseudouserid)
        WHERE u.country IN ({clist})
        GROUP BY 1, 2
    """)

    def pair_stats(a: str, b: str):
        r = con.execute(f"""
            WITH p AS (
                SELECT game_id,
                       MAX(CASE WHEN audience='{a}' THEN mean_rating END) AS m_a,
                       MAX(CASE WHEN audience='{b}' THEN mean_rating END) AS m_b,
                       MAX(CASE WHEN audience='{a}' THEN n_users END) AS n_a,
                       MAX(CASE WHEN audience='{b}' THEN n_users END) AS n_b,
                       MAX(CASE WHEN audience='{a}' THEN sd_rating END) AS s_a,
                       MAX(CASE WHEN audience='{b}' THEN sd_rating END) AS s_b
                FROM geo_cells WHERE audience IN ('{a}','{b}')
                GROUP BY game_id
                HAVING MAX(CASE WHEN audience='{a}' THEN n_users END) >= {args.min_cell}
                   AND MAX(CASE WHEN audience='{b}' THEN n_users END) >= {args.min_cell}
            )
            SELECT COUNT(*),
                   CORR(m_a, m_b),
                   AVG(m_b - m_a),
                   QUANTILE_CONT(ABS(m_b - m_a), 0.5),
                   QUANTILE_CONT(ABS(m_b - m_a), 0.9)
            FROM p
        """).fetchone()
        return {"pair": f"{a} vs {b}", "n_games": int(r[0]),
                "pearson_game_means": float(r[1]),
                "mean_diff_b_minus_a": float(r[2]),
                "median_abs_diff": float(r[3]), "p90_abs_diff": float(r[4])}

    pairs = [("United States", "Germany"), ("United States", "Spain"),
             ("Germany", "France"), ("United States", "Poland")]
    summary["geo_pairs"] = [pair_stats(a, b) for a, b in pairs]

    # Divergence profile: US vs Germany, top divergent games with tags
    div = con.execute(f"""
        WITH p AS (
            SELECT game_id,
                   MAX(CASE WHEN audience='United States' THEN mean_rating END) AS m_us,
                   MAX(CASE WHEN audience='Germany' THEN mean_rating END) AS m_de,
                   MAX(CASE WHEN audience='United States' THEN n_users END) AS n_us,
                   MAX(CASE WHEN audience='Germany' THEN n_users END) AS n_de
            FROM geo_cells WHERE audience IN ('United States','Germany')
            GROUP BY game_id
            HAVING MAX(CASE WHEN audience='United States' THEN n_users END) >= 25
               AND MAX(CASE WHEN audience='Germany' THEN n_users END) >= 25
        )
        SELECT game_id, m_us, m_de, m_de - m_us AS diff, n_us, n_de
        FROM p ORDER BY ABS(m_de - m_us) DESC LIMIT 40
    """).fetchdf()
    import pandas as pd
    ids = div.game_id.tolist()
    tagmap = dict(con.execute("""
        SELECT game_id, STRING_AGG(tag_type || ':' || tag, '; ')
        FROM tags WHERE game_id IN (SELECT UNNEST(?::BIGINT[])) GROUP BY game_id
    """, [ids]).fetchall())
    rows = []
    for _, rr in div.iterrows():
        rows.append({"game_id": int(rr.game_id), "m_us": round(rr.m_us, 3),
                     "m_de": round(rr.m_de, 3), "diff_de_minus_us": round(rr["diff"], 3),
                     "n_us": int(rr.n_us), "n_de": int(rr.n_de),
                     "tags": tagmap.get(int(rr.game_id), "")[:180]})
    summary["us_vs_de_most_divergent_games"] = rows

    # ------------------------------------------------------------------
    # Ownership pair (own vs notown as pseudo-audiences)
    # ------------------------------------------------------------------
    con.execute("""
        CREATE OR REPLACE VIEW own_cells AS
        SELECT r.game_id AS game_id,
               CASE WHEN c.own THEN 'own' ELSE 'notown' END AS audience,
               COUNT(*) AS n_users, AVG(r.rating) AS mean_rating
        FROM ro r JOIN cols c ON r.rating_observation_id = c.source_rowid
        WHERE r.rating IS NOT NULL
        GROUP BY 1, 2
    """)
    r = con.execute(f"""
        WITH p AS (
            SELECT game_id,
                   MAX(CASE WHEN audience='own' THEN mean_rating END) AS m_o,
                   MAX(CASE WHEN audience='notown' THEN mean_rating END) AS m_n
            FROM own_cells GROUP BY game_id
            HAVING MAX(CASE WHEN audience='own' THEN n_users END) >= {args.min_cell}
               AND MAX(CASE WHEN audience='notown' THEN n_users END) >= {args.min_cell}
        )
        SELECT COUNT(*), CORR(m_o, m_n), AVG(m_n - m_o),
               QUANTILE_CONT(ABS(m_n - m_o), 0.5), QUANTILE_CONT(ABS(m_n - m_o), 0.9)
        FROM p
    """).fetchone()
    summary["ownership_pair"] = {"n_games": int(r[0]), "pearson_game_means": float(r[1]),
                                 "mean_notown_minus_own": float(r[2]),
                                 "median_abs_diff": float(r[3]), "p90_abs_diff": float(r[4])}

    (out_dir / "cross_audience_consistency.json").write_text(
        json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=1, default=str)[:5000])
    con.close()


if __name__ == "__main__":
    main()

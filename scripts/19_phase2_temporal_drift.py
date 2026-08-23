"""Phase B step 5: temporal drift in ratings, under unresolved timestamp
semantics.

Prior steps found calendar-era mean ratings rise strongly over the snapshot
(~+0.9 points 2003 -> 2023 by the postdate reading).  This script asks what
that drift consists of, testing every time question under BOTH timestamp
readings (`postdate` and `rating_tstamp`; neither is fully resolved):

  1. Raw era curve (context reproduction).
  2. Within-game era trends: does the SAME game's average rating rise over
     calendar time?  Games rated in >=2 distinct era tertiles with enough
     observations per tertile; paired tertile contrasts.
  3. Game-age at rating: rating level vs (rating year - release year).
  4. User cohorts: severity deltas by first-activity year WITHIN lifetime
     volume bands (partial deconfounding of the cohort/volume entanglement).

Everything here is hypothesis-grade regarding absolute dates because
timestamp provenance is unresolved; conclusions rest on agreement between
the two readings.
"""

import argparse
import json
from pathlib import Path

import duckdb

REPO_DIR = Path(__file__).resolve().parent.parent

BAND_ORDER = ["10-24", "25-49", "50-99", "100-249", "250-499", "500-999", "1000+"]


def q(path) -> str:
    return str(path).replace("'", "''")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", type=Path, default=None)
    ap.add_argument("--out-dir", type=Path, default=REPO_DIR / "data" / "processed" / "phase2")
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
    con.execute(f"CREATE OR REPLACE VIEW rbv AS SELECT * FROM read_parquet('{q(data_dir / 'rater_behavior_by_volume.parquet')}')")
    con.execute(f"CREATE OR REPLACE VIEW sev AS SELECT * FROM read_parquet('{q(out_dir / 'user_severity.parquet')}')")
    con.execute(f"CREATE OR REPLACE VIEW games AS SELECT * FROM read_parquet('{q(data_dir / 'games.parquet')}')")
    con.execute("""
        CREATE OR REPLACE VIEW obs AS
        SELECT r.rating_observation_id, r.game_id, r.user_pseudouserid,
               r.rating,
               TRY_CAST(r.postdate AS TIMESTAMP) AS post_ts,
               TRY_CAST(r.rating_tstamp AS TIMESTAMP) AS rate_ts
        FROM ro r
    """)
    summary = {"data_dir": str(data_dir),
               "timestamp_caveat": "both readings reported; neither field's semantics resolved"}

    # ------------------------------------------------------------------
    # 1+2. Era curves and within-game era trends
    # ------------------------------------------------------------------
    for tag, ts in [("postdate", "post_ts"), ("rating_tstamp", "rate_ts")]:
        curve = con.execute(f"""
            SELECT YEAR({ts}) AS yr, COUNT(*) AS n, AVG(rating) AS mean_rating
            FROM obs WHERE {ts} IS NOT NULL GROUP BY 1 HAVING COUNT(*) >= 50000 ORDER BY 1
        """).fetchdf()
        summary[f"era_curve_{tag}"] = curve.to_dict(orient="records")

        # within-game era tertile contrast: games with >=30 obs in each of
        # first and last observation tertiles (tertiles defined per game by
        # its own observation date distribution)
        r = con.execute(f"""
            WITH gts AS (
                SELECT game_id,
                       QUANTILE_CONT({ts}, 1/3.0) AS t1,
                       QUANTILE_CONT({ts}, 2/3.0) AS t2
                FROM obs WHERE {ts} IS NOT NULL GROUP BY game_id
            ), cells AS (
                SELECT o.game_id,
                       CASE WHEN o.{ts} <= g.t1 THEN 'early'
                            WHEN o.{ts} > g.t2 THEN 'late' END AS seg,
                       COUNT(*) AS n, SUM(o.rating) AS s
                FROM obs o JOIN gts g USING (game_id)
                WHERE o.{ts} IS NOT NULL
                GROUP BY 1, 2
            ), p AS (
                SELECT game_id,
                       MAX(CASE WHEN seg='early' THEN n END) AS n_e,
                       MAX(CASE WHEN seg='early' THEN s END) AS s_e,
                       MAX(CASE WHEN seg='late' THEN n END) AS n_l,
                       MAX(CASE WHEN seg='late' THEN s END) AS s_l
                FROM cells GROUP BY game_id
                HAVING MAX(CASE WHEN seg='early' THEN n END) >= 30
                   AND MAX(CASE WHEN seg='late' THEN n END) >= 30
            )
            SELECT COUNT(*),
                   AVG(s_l/n_l - s_e/n_e),
                   QUANTILE_CONT(s_l/n_l - s_e/n_e, 0.5)
            FROM p
        """).fetchone()
        summary[f"within_game_era_contrast_{tag}"] = {
            "n_games": int(r[0]), "mean_late_minus_early": float(r[1]),
            "median_late_minus_early": float(r[2]),
            "definition": "games with >=30 obs in own early/late observation terciles",
        }

    # ------------------------------------------------------------------
    # 3. Game-age at rating (needs release year; join covers snapshot games)
    # ------------------------------------------------------------------
    age_rows = {}
    for tag, ts in [("postdate", "post_ts"), ("rating_tstamp", "rate_ts")]:
        dfp = con.execute(f"""
            SELECT LEAST(GREATEST(YEAR({ts}) - g.year, -5), 40) AS age_bucket,
                   COUNT(*) AS n, AVG(o.rating) AS m
            FROM obs o JOIN games g USING (game_id)
            WHERE {ts} IS NOT NULL AND g.year BETWEEN 1950 AND 2026
            GROUP BY 1 ORDER BY 1
        """).fetchdf()
        age_rows[tag] = dfp.to_dict(orient="records")
    summary["game_age_at_rating"] = age_rows

    # ------------------------------------------------------------------
    # 4. Cohort within volume band (severity by first-activity year)
    # ------------------------------------------------------------------
    cohort = con.execute("""
        WITH firsty AS (
            SELECT user_pseudouserid,
                   YEAR(MIN(TRY_CAST(postdate AS TIMESTAMP))) AS y0
            FROM ro WHERE postdate IS NOT NULL GROUP BY 1
        )
        SELECT b.volume_band,
               CASE WHEN f.y0 <= 2010 THEN 'a_start<=2010'
                    WHEN f.y0 <= 2015 THEN 'b_2011-2015'
                    ELSE 'c_2016+' END AS cohort,
               COUNT(*) AS users,
               AVG(s.delta_full) AS mean_delta,
               AVG(s.rating_observations) AS mean_n_obs
        FROM firsty f
        JOIN rbv b ON f.user_pseudouserid = b.user_pseudouserid
        JOIN sev s ON f.user_pseudouserid = s.user_pseudouserid
        WHERE s.delta_full IS NOT NULL AND f.y0 IS NOT NULL
          AND b.volume_band IN ('25-49','50-99','100-249','250-499','500-999','1000+')
        GROUP BY 1, 2 ORDER BY 1, 2
    """).fetchdf()
    summary["severity_by_cohort_within_band"] = cohort.to_dict(orient="records")

    (out_dir / "temporal_drift.json").write_text(
        json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")

    print(json.dumps({k: summary[k] for k in summary if k.startswith(
        ("within_game", "game_age_at_rating", "severity_by_cohort"))},
        indent=1, default=str)[:4000])
    print("era curve endpoints:",
          summary["era_curve_postdate"][0], summary["era_curve_postdate"][-1])
    con.close()


if __name__ == "__main__":
    main()

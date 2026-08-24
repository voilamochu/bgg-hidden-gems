"""Phase A step 3: decompose the low-vs-high volume rating gap.

Step 1 showed the gap survives within games (game mix explains ~none of it).
Step 2 estimated per-user severity offsets conditioned on games and showed
they are large and ordered by lifetime volume.  This script quantifies the
decomposition the captain asked for:

  1. Raw gap between volume groups (baseline reproduction).
  2. Game-mix component: reweight each group's ratings to a common game
     distribution (Kitagawa-style standardization) - how much of the raw gap
     is which games each group chooses to rate.
  3. Rater-level component: the within-game / severity-adjusted gap
     (ratings minus user severity offsets), standardized for game mix.
  4. Experience/exposure probes, labeled hypothesis-grade because timestamp
     semantics are unresolved:
     a. career-position effect: within users with long histories, do later
        observations (by postdate order and separately by rating_tstamp
        order) sit lower than earlier ones at fixed lifetime volume?
     b. calendar-era effect: mean rating by observation year under both
        timestamp interpretations.

Outputs: gap_decomposition.json plus supporting parquet tables.
"""

import argparse
import json
from pathlib import Path

import duckdb

REPO_DIR = Path(__file__).resolve().parent.parent

BAND_ORDER = ["1", "2-4", "5-9", "10-24", "25-49",
              "50-99", "100-249", "250-499", "500-999", "1000+"]


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
    con.execute("""
        CREATE OR REPLACE VIEW obs AS
        SELECT r.rating_observation_id, r.game_id, r.user_pseudouserid,
               r.rating, b.volume_band,
               TRY_CAST(r.postdate AS TIMESTAMP) AS post_ts,
               TRY_CAST(r.rating_tstamp AS TIMESTAMP) AS rate_ts
        FROM ro r JOIN rbv b USING (user_pseudouserid)
    """)
    summary = {"data_dir": str(data_dir)}

    LOW_BANDS = ["1", "2-4", "5-9"]
    HIGH_BANDS = ["500-999", "1000+"]
    lo = ",".join(f"'{b}'" for b in LOW_BANDS)
    hi = ",".join(f"'{b}'" for b in HIGH_BANDS)
    summary["groups"] = {"low_bands": LOW_BANDS, "high_bands": HIGH_BANDS}

    # ------------------------------------------------------------------
    # 1. Raw gap and per-band means
    # ------------------------------------------------------------------
    raw = con.execute(f"""
        SELECT CASE WHEN volume_band IN ({lo}) THEN 'low'
                    WHEN volume_band IN ({hi}) THEN 'high'
                    ELSE 'mid' END AS grp,
               COUNT(*) AS n_obs, AVG(rating) AS mean_rating
        FROM obs GROUP BY 1
    """).fetchdf().set_index("grp")
    summary["raw"] = {
        "low_mean": float(raw.loc["low", "mean_rating"]),
        "high_mean": float(raw.loc["high", "mean_rating"]),
        "raw_gap_low_minus_high": float(raw.loc["low", "mean_rating"] - raw.loc["high", "mean_rating"]),
        "n_obs_low": int(raw.loc["low", "n_obs"]),
        "n_obs_high": int(raw.loc["high", "n_obs"]),
    }

    # ------------------------------------------------------------------
    # 2+3. Standardization for game mix + severity adjustment
    # ------------------------------------------------------------------
    # For each group g and game i: cell counts and sums, with and without the
    # user severity offset subtracted.  Standardized mean for group g uses
    # the COMMON game weights w_i proportional to total ratings of game i
    # across both groups:  sum_g_hat = sum_i w_i * cellmean_{g,i}.
    con.execute(f"""
        CREATE OR REPLACE TABLE cells AS
        SELECT o.game_id,
               CASE WHEN o.volume_band IN ({lo}) THEN 'low'
                    WHEN o.volume_band IN ({hi}) THEN 'high' END AS grp,
               COUNT(*) AS n_obs,
               SUM(o.rating) AS sum_y,
               SUM(o.rating - COALESCE(s.delta_full, 0)) AS sum_yadj
        FROM obs o
        LEFT JOIN sev s ON o.user_pseudouserid = s.user_pseudouserid
        WHERE o.volume_band IN ({lo}) OR o.volume_band IN ({hi})
        GROUP BY 1, 2
    """)
    std = con.execute("""
        WITH w AS (
            SELECT game_id, SUM(n_obs) AS w FROM cells GROUP BY game_id
        ), j AS (
            SELECT c.grp, c.game_id, w.w,
                   c.n_obs, c.sum_y / c.n_obs AS m_raw, c.sum_yadj / c.n_obs AS m_adj
            FROM cells c JOIN w USING (game_id)
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
    # Kitagawa-style split of the raw gap into mix vs rate components using
    # cell means within the common support:
    #   gap = [sum w_i (m_L,i - m_H,i)]  (within-game rate diff)
    #       + [sum (w_L,i - w_H,i)/W * ... ] standardization identity; we report
    # the standardized contrasts directly instead of forcing an exact
    # two-term identity, since cell means use different supports per group.
    summary["standardized_decomposition"] = decomp

    # How much of each group's library lies in cells where BOTH groups are
    # present (support overlap)?
    ov = con.execute("""
        SELECT
            SUM(CASE WHEN grp='low'  THEN n_obs END) AS n_low_all,
            SUM(CASE WHEN grp='high' THEN n_obs END) AS n_high_all
        FROM cells
    """).fetchone()
    both = con.execute("""
        WITH g AS (
            SELECT game_id, COUNT(DISTINCT grp) AS k, SUM(n_obs) FILTER (grp='low') AS nl,
                   SUM(n_obs) FILTER (grp='high') AS nh
            FROM cells GROUP BY game_id
        )
        SELECT SUM(nl), SUM(nh) FROM g WHERE k = 2
    """).fetchone()
    summary["support_overlap"] = {
        "low_obs_on_shared_games": int(both[0]), "low_obs_total": int(ov[0]),
        "high_obs_on_shared_games": int(both[1]), "high_obs_total": int(ov[1]),
        "share_low_on_shared": float(both[0] / ov[0]),
        "share_high_on_shared": float(both[1] / ov[1]),
    }

    # ------------------------------------------------------------------
    # 4a. Career-position effect (hypothesis-grade; ordering by timestamps)
    # ------------------------------------------------------------------
    career = {}
    for tag, ts in [("postdate", "post_ts"), ("rating_tstamp", "rate_ts")]:
        r = con.execute(f"""
            WITH seq AS (
                SELECT user_pseudouserid,
                       ROW_NUMBER() OVER (PARTITION BY user_pseudouserid ORDER BY {ts},
                                          rating_observation_id) AS pos,
                       COUNT(*) OVER (PARTITION BY user_pseudouserid) AS n_user,
                       rating
                FROM obs
                WHERE {ts} IS NOT NULL AND user_pseudouserid IN (
                    SELECT user_pseudouserid FROM rbv WHERE rating_observations >= 50)
            )
            SELECT CASE WHEN pos <= 0.1 * n_user THEN 'first_decile'
                        WHEN pos >= 0.9 * n_user THEN 'last_decile' END AS seg,
                    COUNT(*), AVG(rating)
            FROM seq GROUP BY 1
        """).fetchall()
        d = {seg: (int(n), float(m)) for seg, n, m in r if seg is not None}
        career[tag] = {
            "users_with_ge50_ratings": True,
            "first_decile_mean": d.get("first_decile", (None, None))[1],
            "last_decile_mean": d.get("last_decile", (None, None))[1],
            "career_slope_last_minus_first": (d.get("last_decile", (0, 0))[1]
                                              - d.get("first_decile", (0, 0))[1])
                                              if len(d) == 2 else None,
        }
    summary["career_position_effect"] = {
        **career,
        "caveat": "ordering uses unresolved-semantics timestamps; treat as hypothesis-grade",
    }

    # ------------------------------------------------------------------
    # 4b. Calendar-era effect under both timestamp readings
    # ------------------------------------------------------------------
    era = {}
    for tag, ts in [("postdate", "post_ts"), ("rating_tstamp", "rate_ts")]:
        dfp = con.execute(f"""
            SELECT YEAR({ts}) AS yr, COUNT(*) AS n, AVG(rating) AS m
            FROM obs WHERE {ts} IS NOT NULL
            GROUP BY 1 ORDER BY 1
        """).fetchdf()
        era[tag] = dfp.to_dict(orient="records")
    summary["calendar_era_means"] = era

    # Era composition of low vs high groups (mix over time)
    era_mix = con.execute(f"""
        SELECT CASE WHEN volume_band IN ({lo}) THEN 'low'
                    WHEN volume_band IN ({hi}) THEN 'high' END AS grp,
                YEAR(post_ts) AS yr, COUNT(*) AS n
        FROM obs WHERE post_ts IS NOT NULL
        GROUP BY 1, 2 ORDER BY 2
    """).fetchdf()
    era_mix_path = out_dir / "era_mix_by_group.parquet"
    era_mix.to_parquet(era_mix_path, index=False)

    # ------------------------------------------------------------------
    # 5. Era-controlled within-game contrasts (competing-explanation test)
    # ------------------------------------------------------------------
    # Calendar-era mean ratings rise strongly over the snapshot (see
    # calendar_era_means).  If heavy raters rated the same games earlier,
    # era inflation could mimic a severity gap.  Test: recompute the paired
    # within-game contrast inside narrow era windows, under BOTH timestamp
    # readings (semantics unresolved).
    WINDOWS = ["<=2010", "2011-2017", "2018-2025"]
    era_contrast = []
    for tag, ts in [("postdate", "post_ts"), ("rating_tstamp", "rate_ts")]:
        # era composition of the two groups under this reading
        comp = con.execute(f"""
            SELECT CASE WHEN volume_band IN ({lo}) THEN 'low'
                        WHEN volume_band IN ({hi}) THEN 'high' END AS grp,
                   AVG(YEAR({ts})) AS mean_year,
                   QUANTILE_CONT(YEAR({ts}), 0.5) AS median_year
            FROM obs
            WHERE {ts} IS NOT NULL AND (volume_band IN ({lo}) OR volume_band IN ({hi}))
            GROUP BY 1
        """).fetchdf().set_index("grp")
        for w in WINDOWS:
            if w == "<=2010":
                cond = f"YEAR({ts}) <= 2010"
            elif w == "2011-2017":
                cond = f"YEAR({ts}) BETWEEN 2011 AND 2017"
            else:
                cond = f"YEAR({ts}) >= 2018"
            r = con.execute(f"""
                WITH c AS (
                    SELECT o.game_id AS game_id,
                           CASE WHEN o.volume_band IN ({lo}) THEN 'low' ELSE 'high' END AS grp,
                           COUNT(*) AS n_users, SUM(o.rating) AS sum_y
                    FROM obs o
                    WHERE {ts} IS NOT NULL AND ({cond})
                      AND (o.volume_band IN ({lo}) OR o.volume_band IN ({hi}))
                    GROUP BY 1, 2
                ), p AS (
                    SELECT game_id,
                           MAX(CASE WHEN grp='low' THEN n_users END) AS n_low,
                           MAX(CASE WHEN grp='high' THEN n_users END) AS n_high,
                           MAX(CASE WHEN grp='low' THEN sum_y END) AS s_low,
                           MAX(CASE WHEN grp='high' THEN sum_y END) AS s_high
                    FROM c GROUP BY game_id
                    HAVING MAX(CASE WHEN grp='low' THEN n_users END) >= 3
                       AND MAX(CASE WHEN grp='high' THEN n_users END) >= 3
                )
                SELECT COUNT(*),
                       AVG(s_low/n_low - s_high/n_high),
                       QUANTILE_CONT(s_low/n_low - s_high/n_high, 0.5)
                FROM p
            """).fetchone()
            row = {"timestamp_field": tag, "window": w,
                   "n_games_paired": int(r[0]),
                   "mean_within_game_gap": float(r[1]),
                   "median_within_game_gap": float(r[2])}
            if w == WINDOWS[0]:
                crow = comp.loc["low"], comp.loc["high"]
                row["low_mean_year"] = float(crow[0]["mean_year"])
                row["high_mean_year"] = float(crow[1]["mean_year"])
            era_contrast.append(row)
    summary["era_controlled_within_game_contrasts"] = {
        "min_cell": 3,
        "rows": era_contrast,
        "note": "within-game low-vs-high gaps recomputed inside era windows; "
                "if the gap persists within windows it cannot be produced by "
                "calendar-era composition alone",
    }

    # ------------------------------------------------------------------
    # Persist group cell table for reuse
    # ------------------------------------------------------------------
    cells_path = out_dir / "gap_cells_low_high.parquet"
    con.execute(f"COPY (SELECT * FROM cells) TO '{q(cells_path)}' "
                f"(FORMAT PARQUET, COMPRESSION ZSTD)")

    (out_dir / "gap_decomposition.json").write_text(
        json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")

    print(json.dumps({k: summary[k] for k in [
        "raw", "standardized_decomposition", "support_overlap",
        "career_position_effect", "era_controlled_within_game_contrasts"]},
        indent=2, default=str))
    print("era means (postdate): first/last 3:",
          summary["calendar_era_means"]["postdate"][:3],
          summary["calendar_era_means"]["postdate"][-3:])
    con.close()


if __name__ == "__main__":
    main()

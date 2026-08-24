"""Phase 3 steps (a)+(b): do residuals from the Phase 2 additive baseline
vary systematically with GAME TYPE?

Baseline is REUSED, not refitted (see findings.md 2026-08-24 session note):
rating = c + game_alpha_g + delta_u from scripts/16 (converged ALS),
artifacts data/processed/phase2/{user_severity,game_adjusted_means}.parquet.

Centering convention [important]: game_alpha is centered across GAMES and
delta_u across USERS (both unweighted); the observation-consistent intercept
is c = mean(y - alpha - delta) over the covered universe (~6.79), not mu.
All contrasts below are invariant to this constant; residuals stored here
are centered empirically.

Type axes: top-12 categories / mechanics / themes by observation mass plus
weight bands (light <1.75 <= medium <2.75 <= heavy).  Universe = covered
observations (games.parquet record present; 91.4% of all observations).

Method (robustness rules learned 2026-08-24, see findings.md):
  - Two narrow single-scan aggregations in DuckDB: per-user totals and
    per-(user, feature) on-cells.  Assembly uses KEY-based joins only --
    no wide boolean-flag frames, no positional column mapping.
  - Anchor assertion: three features are recomputed via independent direct
    SQL each run and must agree with assembled taus within ANCHOR_TOL.
  - Users below MIN_USER_LIFETIME_OBS lifetime observations are excluded
    from the cell pass (they cannot reach the >=MIN_CELL informative cells);
    documented as a scope restriction.

Steps:
  A. Global per-type residual levels + rater volume-band-group breakdown.
  B. Within-user type contrasts c_ut = mean(resid | u rates t-game) -
     mean(resid | u rates non-t-game); obs-weighted population tau_t with
     user-clustered SE; persisted informative cells for later stability work.
  C. Per-user residual-on-alpha slope (scale-anchoring diagnostic).

Timestamps unused.  Duplicate user-game observations (0.007%) kept.

Outputs: data/processed/phase3/phase3_type_descriptives.json,
         data/processed/phase3/phase3_user_tag_contrasts.parquet,
         data/processed/phase3/phase3_user_scale_diagnostic.parquet
"""

import argparse
import json
from pathlib import Path

import duckdb
import numpy as np

REPO_DIR = Path(__file__).resolve().parent.parent

MIN_USER_OBS_EACH_SIDE = 5
MIN_USER_LIFETIME_OBS = 20
TOP_N_TAGS = 12
# Independent in-run verification: for these features the tau is recomputed
# via a direct per-user AVG formulation (different code path from the
# cells/utot pipeline) on the FULL data, and must agree within tolerance.
# [Pitfall, learned 2026-08-24]: NEVER anchor full-population cell stats
# against subsampled runs -- under k% sampling the n_on>=5 cell filter only
# passes users with >=5k observations of the feature, selecting superfans and
# shifting taus by ~0.05-0.08 points (e.g. Cooperative +0.06 sampled vs
# -0.017 full).
ANCHOR_FEATURES = ["mechanic::Cooperative Game", "category::War",
                   "category::Fighting"]
ANCHOR_TOL = 0.01


def q(path) -> str:
    return str(path).replace("'", "''")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", type=Path, default=REPO_DIR / "scratch" / "phase2")
    ap.add_argument("--fit-dir", type=Path, default=REPO_DIR / "data" / "processed" / "phase2")
    ap.add_argument("--out-dir", type=Path, default=REPO_DIR / "data" / "processed" / "phase3")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(config={
        "memory_limit": "4gb",
        "temp_directory": str(REPO_DIR / "scratch" / "ducktmp"),
        "threads": 3,
        "preserve_insertion_order": False,
    })
    d, f = args.data_dir, args.fit_dir

    stab = json.loads((f / "user_severity_stability.json").read_text())
    print(f"reused baseline: mu={stab['als_convergence_full']['mu']:.4f}, "
          f"R2 both={stab['variance_decomposition_nested_r2']['r2_additive_both']:.3f}")

    # ------------------------------------------------------------------
    # Feature universe
    # ------------------------------------------------------------------
    fams, tag_meta = {}, {}
    for fam in ("category", "mechanic", "theme"):
        df = con.execute(f"""
            WITH gm AS (SELECT game_id, COUNT(*) AS n_obs
                        FROM read_parquet('{q(d / 'rating_observations.parquet')}') WHERE rating IS NOT NULL GROUP BY 1)
            SELECT gt.tag, COUNT(*) AS n_games, SUM(gm.n_obs) AS n_obs
            FROM read_parquet('{q(d / 'game_tags.parquet')}') gt JOIN gm USING (game_id)
            WHERE gt.tag_type = '{fam}'
            GROUP BY 1 ORDER BY n_obs DESC LIMIT {TOP_N_TAGS}
        """).fetchdf()
        fams[fam] = df["tag"].tolist()
        for _, r in df.iterrows():
            tag_meta[f"{fam}::{r['tag']}"] = {"tag_type": fam, "tag": r["tag"],
                                              "n_games": int(r["n_games"]),
                                              "n_obs_universe": int(r["n_obs"])}
    feats = ([f"{fam}::{t}" for fam in ("category", "mechanic", "theme") for t in fams[fam]]
             + ["wb_light", "wb_medium", "wb_heavy"])
    print(f"features: {len(feats)}")

    vals = ", ".join(
        f"('{fam}::{t.replace(chr(39), chr(39)*2)}')"
        for fam in ("category", "mechanic", "theme") for t in fams[fam])
    con.execute("CREATE OR REPLACE TABLE sel(tag VARCHAR)")
    con.execute(f"INSERT INTO sel VALUES {vals}")

    # membership: game x feature (tags) -- small
    con.execute(f"""
        CREATE OR REPLACE TABLE gmemb AS
        SELECT gt.game_id, gt.tag_type || '::' || gt.tag AS feat
        FROM read_parquet('{q(d / 'game_tags.parquet')}') gt
        WHERE gt.tag_type || '::' || gt.tag IN (SELECT tag FROM sel)
    """)

    # ------------------------------------------------------------------
    # Observation source view (residual expression inline, never materialized)
    # ------------------------------------------------------------------
    con.execute(f"""
        CREATE OR REPLACE VIEW src AS
        SELECT s.rating_observation_id AS oid,
               s.game_id,
               s.user_pseudouserid AS uid,
               b.volume_band,
               b.rating_observations AS user_n_obs,
               CASE WHEN b.volume_band IN ('1','2-4','5-9') THEN 'low'
                    WHEN b.volume_band IN ('10-24','25-49','50-99',
                                           '100-249','250-499') THEN 'mid'
                    ELSE 'high' END AS band_group,
               COALESCE(g.game_alpha, 0) AS alpha_g,
               COALESCE(v.delta_full, 0) AS delta_u,
               s.rating AS y,
               s.rating - COALESCE(g.game_alpha, 0) - COALESCE(v.delta_full, 0) AS r_raw,
               gp.weight IS NOT NULL AS covered,
               CASE WHEN gp.weight IS NULL THEN NULL
                    WHEN gp.weight < 1.75 THEN 'wb_light'
                    WHEN gp.weight < 2.75 THEN 'wb_medium'
                    ELSE 'wb_heavy' END AS wband
        FROM read_parquet('{q(d / 'rating_observations.parquet')}') s
        JOIN read_parquet('{q(d / 'rater_behavior_by_volume.parquet')}') b USING (user_pseudouserid)
        LEFT JOIN read_parquet('{q(f / 'game_adjusted_means.parquet')}') g ON s.game_id = g.game_id
        LEFT JOIN read_parquet('{q(f / 'user_severity.parquet')}') v ON s.user_pseudouserid = v.user_pseudouserid
        LEFT JOIN read_parquet('{q(d / 'games.parquet')}') gp ON s.game_id = gp.game_id
    """)
    tot = con.execute("""
        SELECT COUNT(*), AVG(r_raw), STDDEV_SAMP(r_raw), STDDEV_SAMP(y)
        FROM (
            SELECT * FROM src
        )
    """).fetchone()
    c_shift = float(tot[1])
    summary = {
        "baseline_source": str(f),
        "mu_full_fit": stab["als_convergence_full"]["mu"],
        "resid_intercept_c": c_shift,
        "universe": "covered observations (games.parquet record present)",
        "min_user_lifetime_obs": MIN_USER_LIFETIME_OBS,
        "min_user_obs_each_side": MIN_USER_OBS_EACH_SIDE,
        "n_users_total": int(con.execute(
            "SELECT COUNT(DISTINCT uid) FROM src").fetchone()[0]),
        "n_users_cell_scope": int(con.execute(
            f"SELECT COUNT(DISTINCT uid) FROM src WHERE user_n_obs >= {MIN_USER_LIFETIME_OBS}").fetchone()[0]),
        "cell_scope_note": "within-user contrasts restricted to users with >= "
                           f"{MIN_USER_LIFETIME_OBS} lifetime observations; this excludes "
                           "the 'low' volume-band group (1-9 obs) entirely",
        "n_obs_covered": int(con.execute(
            "SELECT COUNT(*) FROM src WHERE covered").fetchone()[0]),
        "resid_sd_covered": float(tot[2]),
        "rating_sd_covered": float(tot[3]),
        "implied_r2_additive_covered": float(1 - tot[2] ** 2 / tot[3] ** 2),
        "tags": tag_meta,
        "features": feats,
    }
    print(f"in-scope users' covered obs: {summary['n_obs_covered']:,}; "
          f"c={c_shift:.4f}; implied R2(additive, covered)="
          f"{summary['implied_r2_additive_covered']:.3f}")

    # ------------------------------------------------------------------
    # P1: per-user totals (covered universe) incl. scale-diagnostic moments
    # ------------------------------------------------------------------
    con.execute(f"""
        CREATE OR REPLACE TABLE utot AS
        SELECT uid,
               COUNT(*) AS n_all,
               SUM(r_raw - ({c_shift})) AS sy_all,
               SUM(alpha_g * (r_raw - ({c_shift}))) AS sxy_all,
               SUM(alpha_g * alpha_g) AS sxx_all,
               SUM(alpha_g) AS sx_all
        FROM src
        WHERE covered AND user_n_obs >= {MIN_USER_LIFETIME_OBS}
        GROUP BY uid
    """)
    n_users = con.execute("SELECT COUNT(*) FROM utot").fetchone()[0]
    print(f"P1 done: {n_users:,} users")

    # ------------------------------------------------------------------
    # P2: per-(uid, feature) on-cells, streamed to table
    # ------------------------------------------------------------------
    con.execute(f"""
        CREATE OR REPLACE TABLE cells AS
        SELECT l.uid, l.feat, COUNT(*) AS n_on,
               SUM(l.r_raw - ({c_shift})) AS sy_on
        FROM (
            SELECT s.uid, s.r_raw, m.feat
            FROM src s JOIN gmemb m ON s.game_id = m.game_id
            WHERE s.covered AND s.user_n_obs >= {MIN_USER_LIFETIME_OBS}
            UNION ALL
            SELECT uid, r_raw, wband AS feat FROM src
            WHERE covered AND wband IS NOT NULL AND user_n_obs >= {MIN_USER_LIFETIME_OBS}
        ) l
        GROUP BY l.uid, l.feat
    """)
    n_cells = con.execute("SELECT COUNT(*), COUNT(DISTINCT uid) FROM cells").fetchone()
    print(f"P2 done: {n_cells[0]:,} (uid,feat) on-cells across {n_cells[1]:,} users")

    # ------------------------------------------------------------------
    # Assemble informative cells + contrasts (key-based joins, in SQL)
    # ------------------------------------------------------------------
    con.execute(f"""
        CREATE OR REPLACE TABLE contrast AS
        SELECT c.uid, c.feat, c.n_on,
               (t.n_all - c.n_on) AS n_off,
               (c.sy_on / c.n_on) - ((t.sy_all - c.sy_on) / (t.n_all - c.n_on)) AS contrast
        FROM cells c JOIN utot t USING (uid)
        WHERE c.n_on >= {MIN_USER_OBS_EACH_SIDE}
          AND (t.n_all - c.n_on) >= {MIN_USER_OBS_EACH_SIDE}
    """)
    tau_df = con.execute("""
        SELECT feat, COUNT(*) AS n_users_informative,
               AVG(contrast) AS tau_within_user,
               STDDEV_SAMP(contrast) AS sd_between_users,
               STDDEV_SAMP(contrast) / SQRT(COUNT(*)) AS se_cluster_user,
               AVG(CASE WHEN contrast > 0 THEN 1.0 ELSE 0.0 END) AS share_users_positive
        FROM contrast GROUP BY feat ORDER BY tau_within_user
    """).fetchdf()
    tau_df["z"] = tau_df.tau_within_user / tau_df.se_cluster_user
    print("\nwithin-user contrasts (population level):")
    print(tau_df.to_string(index=False,
                           formatters={"tau_within_user": "{:+.4f}".format,
                                       "se_cluster_user": "{:.4f}".format,
                                       "z": "{:+.1f}".format}))

    # ------------------------------------------------------------------
    # A. Global per-type levels + band-group breakdown (key-based)
    # ------------------------------------------------------------------
    # simpler correct route: recompute per-feature-band on-stats directly
    con.execute(f"""
        CREATE OR REPLACE TABLE onstats AS
        SELECT l.feat, l.band_group, COUNT(*) AS n_on, AVG(l.r_raw - ({c_shift})) AS m_on
        FROM (
            SELECT s.band_group, s.r_raw, m.feat
            FROM src s JOIN gmemb m ON s.game_id = m.game_id WHERE s.covered
            UNION ALL
            SELECT band_group, r_raw, wband AS feat FROM src WHERE covered AND wband IS NOT NULL
        ) l
        GROUP BY 1, 2
    """)
    _bt = con.execute(f"""
        SELECT band_group, COUNT(*) AS n_all, AVG(r_raw - ({c_shift})) AS m_all
        FROM src WHERE covered GROUP BY 1
    """).fetchall()
    band_tot = {r[0]: (int(r[1]), float(r[2])) for r in _bt}
    rows = []
    for ft in feats:
        brow = {}
        for bg in ("low", "mid", "high"):
            r = con.execute("SELECT n_on, m_on FROM onstats WHERE feat=? AND band_group=?",
                            [ft, bg]).fetchone()
            n_on = int(r[0]) if r else 0
            m_on = float(r[1]) if r and r[1] is not None else None
            n_all, m_all = band_tot.get(bg, (0, float('nan')))
            n_off = n_all - n_on
            m_off = (m_all * n_all - (m_on or 0) * n_on) / n_off if n_off else None
            brow[bg] = {"n_on": n_on, "m_on": m_on, "m_off": m_off,
                        "gap_on_minus_off": (m_on - m_off) if m_on is not None and m_off is not None else None}
        rows.append({"feature": ft, **{k: v for k, v in brow.items()}})
    summary["global_band_breakdown"] = rows

    # ------------------------------------------------------------------
    # C. Scale diagnostic: per-user slope of residual on game alpha
    # ------------------------------------------------------------------
    diag = con.execute("""
        SELECT uid, n_all,
               (n_all * sxy_all - sx_all * sy_all)
               / NULLIF(n_all * sxx_all - sx_all * sx_all, 0) AS slope_resid_on_alpha
        FROM utot
    """).fetchdf()
    diag.to_parquet(args.out_dir / "phase3_user_scale_diagnostic.parquet", index=False)

    # ------------------------------------------------------------------
    # Persist + verify anchors
    # ------------------------------------------------------------------
    con.execute(f"""
        COPY (SELECT uid, feat, n_on, n_off, contrast FROM contrast ORDER BY uid, feat)
        TO '{q(args.out_dir / 'phase3_user_tag_contrasts.parquet')}'
        (FORMAT PARQUET, COMPRESSION ZSTD)
    """)
    n_inf = con.execute("SELECT COUNT(*) FROM contrast").fetchone()[0]
    print(f"wrote phase3_user_tag_contrasts.parquet: {n_inf:,} informative cells")

    tau_map = dict(zip(tau_df.feat, tau_df.tau_within_user))
    ok = True
    anchor_results = {}
    for ft in ANCHOR_FEATURES:
        fam, tag = ft.split("::", 1)
        # independent path: direct per-user AVGs on full data, all users
        ref = con.execute(f"""
            WITH u AS (
                SELECT s.uid AS uid,
                       AVG(CASE WHEN m.game_id IS NOT NULL THEN s.r_raw END) AS m_on,
                       AVG(CASE WHEN m.game_id IS NULL THEN s.r_raw END) AS m_off,
                       COUNT(m.game_id) AS n_on,
                       COUNT(*) AS n_all
                FROM src s
                LEFT JOIN (SELECT DISTINCT game_id FROM read_parquet('{q(d / 'game_tags.parquet')}') gt
                           WHERE gt.tag_type = '{fam}' AND gt.tag = '{tag.replace(chr(39), chr(39)*2)}') m
                      ON s.game_id = m.game_id
                WHERE s.covered AND s.user_n_obs >= {MIN_USER_LIFETIME_OBS}
                GROUP BY s.uid
            )
            SELECT AVG(m_on - m_off) FROM u
            WHERE n_on >= {MIN_USER_OBS_EACH_SIDE} AND (n_all - n_on) >= {MIN_USER_OBS_EACH_SIDE}
        """).fetchone()[0]
        got = tau_map.get(ft)
        agree = ref is not None and got is not None and abs(got - float(ref)) <= ANCHOR_TOL
        ok &= agree
        anchor_results[ft] = {"pipeline_tau": got, "independent_tau": float(ref),
                              "agree": bool(agree)}
        print(f"anchor {ft}: pipeline={got:+.4f} independent={ref:+.4f} "
              f"[{'OK' if agree else 'FAIL'}]")
    summary["anchor_check_passed"] = ok
    summary["anchor_checks"] = anchor_results

    summary["within_user_contrasts"] = tau_df.to_dict(orient="records")
    (args.out_dir / "phase3_type_descriptives.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print("wrote phase3_type_descriptives.json")
    if not ok:
        raise SystemExit("anchor check FAILED -- inspect before trusting outputs")
    con.close()


if __name__ == "__main__":
    main()

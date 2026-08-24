"""Phase 3 Gates 2-3: are the type contrasts DISTINCT from global severity,
volume, and game mix, and do they MATERIALLY improve held-out prediction?

Gate 2 (distinctness):
  D1. Per-feature correlation between the within-user contrast and the
      global severity offset delta_u; contrast means by volume-band group.
  D2. Scale-anchoring alternative: distribution of per-user residual-on-alpha
      slopes (scripts/23), their correlation with delta_u, and across-feature
      alignment of tau_t with the mean alpha level of the feature's games.
  D3. Weight-gradient overlap: across tag features, correlation of tau_t
      with mean weight of the feature's games.

Gate 3 (materiality) -- primary validation is held-out parity prediction.
Warm-started additive refit on one half; predict the other half's ratings:
    M0  mu_fit + alpha_g                       (game identity only)
    M1  M0 + delta_u                           (additive baseline)
    M2  M1 + population type effects           (tau_t fitted on train half)
    M3s M1 + per-user shrunk tastes            (w=n_on/(n_on+lambda), falling
                                               back to tau_t when no cell)
    M3u M1 + unshrunk per-user tastes          (cells only)
Both directions.  Also: in-sample R2 gain of M2 on the full data.

Timestamps unused.  Scope identical to scripts/23-24 (covered universe,
>=20 lifetime obs, >=5 per-side informative cells).

Outputs: data/processed/phase3/phase3_distinctness_materiality.json
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
MAX_SWEEPS = 80
SWEEP_TOL = 4e-3
LAMBDA_SHRINK = 20.0


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
    gm_path = f / "game_adjusted_means.parquet"
    sev_path = f / "user_severity.parquet"
    out = {"lambda_shrink": LAMBDA_SHRINK}

    # ------------------------------------------------------------------
    # Feature universe + unified membership (tags + weight bands)
    # ------------------------------------------------------------------
    fams = {}
    for fam in ("category", "mechanic", "theme"):
        df = con.execute(f"""
            WITH gm AS (SELECT game_id, COUNT(*) AS n_obs
                        FROM read_parquet('{q(d / 'rating_observations.parquet')}') WHERE rating IS NOT NULL GROUP BY 1)
            SELECT gt.tag, SUM(gm.n_obs) AS n_obs
            FROM read_parquet('{q(d / 'game_tags.parquet')}') gt JOIN gm USING (game_id)
            WHERE gt.tag_type = '{fam}' GROUP BY 1 ORDER BY n_obs DESC LIMIT {TOP_N_TAGS}
        """).fetchdf()
        fams[fam] = df["tag"].tolist()
    tag_feats = [f"{fam}::{t}" for fam in ("category", "mechanic", "theme") for t in fams[fam]]
    feats = tag_feats + ["wb_light", "wb_medium", "wb_heavy"]

    vals = ", ".join(
        f"('{fam}::{t.replace(chr(39), chr(39)*2)}')"
        for fam in ("category", "mechanic", "theme") for t in fams[fam])
    con.execute("CREATE OR REPLACE TABLE sel(tag VARCHAR)")
    con.execute(f"INSERT INTO sel VALUES {vals}")
    con.execute(f"""
        CREATE OR REPLACE TABLE gmemb AS
        SELECT gt.game_id, gt.tag_type || '::' || gt.tag AS feat
        FROM read_parquet('{q(d / 'game_tags.parquet')}') gt
        WHERE gt.tag_type || '::' || gt.tag IN (SELECT tag FROM sel)
        UNION ALL
        SELECT game_id,
               CASE WHEN weight < 1.75 THEN 'wb_light'
                    WHEN weight < 2.75 THEN 'wb_medium'
                    ELSE 'wb_heavy' END AS feat
        FROM read_parquet('{q(d / 'games.parquet')}') WHERE weight IS NOT NULL
    """)

    # ------------------------------------------------------------------
    # Full-sample view under full-fit parameters (for Gate 2 + in-sample R2)
    # ------------------------------------------------------------------
    con.execute(f"""
        CREATE OR REPLACE VIEW src AS
        SELECT s.rating_observation_id AS oid,
               s.game_id,
               s.user_pseudouserid AS uid,
               b.rating_observations AS user_n_obs,
               CASE WHEN b.volume_band IN ('1','2-4','5-9') THEN 'low'
                    WHEN b.volume_band IN ('10-24','25-49','50-99',
                                           '100-249','250-499') THEN 'mid'
                    ELSE 'high' END AS band_group,
               COALESCE(g.game_alpha, 0) AS alpha_g,
               COALESCE(v.delta_full, 0) AS delta_u,
               s.rating - COALESCE(g.game_alpha, 0) - COALESCE(v.delta_full, 0) AS r_raw,
               gp.weight IS NOT NULL AS covered
        FROM read_parquet('{q(d / 'rating_observations.parquet')}') s
        JOIN read_parquet('{q(d / 'rater_behavior_by_volume.parquet')}') b USING (user_pseudouserid)
        LEFT JOIN read_parquet('{q(f / 'game_adjusted_means.parquet')}') g ON s.game_id = g.game_id
        LEFT JOIN read_parquet('{q(f / 'user_severity.parquet')}') v ON s.user_pseudouserid = v.user_pseudouserid
        LEFT JOIN read_parquet('{q(d / 'games.parquet')}') gp ON s.game_id = gp.game_id
    """)
    c_shift = con.execute("SELECT AVG(r_raw) FROM src WHERE covered").fetchone()[0]

    # ==================================================================
    # GATE 2 diagnostics
    # ==================================================================
    con.execute(f"""
        CREATE OR REPLACE TABLE sevmap AS
        SELECT user_pseudouserid AS uid, delta_full AS delta_u, volume_band
        FROM read_parquet('{q(sev_path)}')
    """)
    d1 = con.execute(f"""
        SELECT c.feat, COUNT(*) AS n_users,
               CORR(c.contrast, s.delta_u) AS corr_contrast_delta,
               AVG(CASE WHEN s.volume_band IN ('10-24','25-49','50-99','100-249','250-499')
                        THEN c.contrast END) AS tau_midband,
               AVG(CASE WHEN s.volume_band IN ('500-999','1000+')
                        THEN c.contrast END) AS tau_highband
        FROM read_parquet('{q(args.out_dir / 'phase3_user_tag_contrasts.parquet')}') c
        JOIN sevmap s USING (uid)
        GROUP BY 1 ORDER BY 1
    """).fetchdf()
    out["d1_contrast_vs_severity"] = {
        "corr_with_delta_median_abs": float(d1.corr_contrast_delta.abs().median()),
        "corr_with_delta_max_abs": float(d1.corr_contrast_delta.abs().max()),
        "by_feature": d1.to_dict(orient="records"),
    }
    print("D1 |corr(contrast,delta)| median:",
          out["d1_contrast_vs_severity"]["corr_with_delta_median_abs"],
          "max:", out["d1_contrast_vs_severity"]["corr_with_delta_max_abs"])

    stab = json.loads((args.out_dir / "phase3_contrast_stability.json").read_text())
    tau_map = {r["feat"]: r["tau_even"] for r in stab["stability_by_feature"]}

    diag = con.execute(f"""
        SELECT d.slope_resid_on_alpha, s.delta_u
        FROM read_parquet('{q(args.out_dir / 'phase3_user_scale_diagnostic.parquet')}') d
        JOIN sevmap s USING (uid)
    """).fetchdf()
    dv = diag.dropna()
    d2 = {
        "slope_p10_p50_p90": [float(dv.slope_resid_on_alpha.quantile(x))
                              for x in (0.10, 0.50, 0.90)],
        "corr_slope_with_delta": float(dv[["slope_resid_on_alpha", "delta_u"]].corr().iloc[0, 1]),
        "n_users": int(len(dv)),
    }
    amap = {}
    mean_a = con.execute("SELECT AVG(alpha_g) FROM src WHERE covered").fetchone()[0]
    for ft in feats:
        if ft.startswith("wb_"):
            cond = f"weight IS NOT NULL AND {dict(wb_light='weight<1.75', wb_medium='weight>=1.75 AND weight<2.75', wb_heavy='weight>=2.75')[ft]}"
            r = con.execute(f"""SELECT AVG(alpha_g) FROM (
                    SELECT gp.weight, COALESCE(g.game_alpha,0) AS alpha_g
                    FROM read_parquet('{q(d / 'rating_observations.parquet')}') s
                    LEFT JOIN read_parquet('{q(gm_path)}') g ON s.game_id=g.game_id
                    LEFT JOIN read_parquet('{q(d / 'games.parquet')}') gp ON s.game_id=gp.game_id
                ) WHERE {cond}""").fetchone()[0]
        else:
            r = con.execute(f"""
                SELECT AVG(s.alpha_g) FROM src s JOIN gmemb m ON s.game_id=m.game_id
                WHERE s.covered AND m.feat='{ft.replace(chr(39), chr(39)*2)}'""").fetchone()[0]
        amap[ft] = float(r - mean_a) if r is not None else None
    common = [ft for ft in feats if ft in tau_map and amap.get(ft) is not None]
    d2["corr_tau_with_mean_game_alpha_across_features"] = float(
        np.corrcoef([tau_map[x] for x in common], [amap[x] for x in common])[0, 1])
    out["d2_scale_anchoring"] = d2
    print("D2 corr(tau, feature games' alpha level):",
          d2["corr_tau_with_mean_game_alpha_across_features"],
          "| corr(slope,delta):", d2["corr_slope_with_delta"])

    wgap = {}
    mean_w = con.execute("""
        SELECT AVG(gp.weight) FROM read_parquet('{}') s
        JOIN read_parquet('{}') gp ON s.game_id = gp.game_id
    """.format(q(d / 'rating_observations.parquet'), q(d / 'games.parquet'))).fetchone()[0]
    for ft in tag_feats:
        fam, tag = ft.split("::", 1)
        r = con.execute(f"""
            SELECT AVG(gp.weight) FROM read_parquet('{q(d / 'game_tags.parquet')}') gt
            JOIN read_parquet('{q(d / 'games.parquet')}') gp USING (game_id)
            WHERE gt.tag_type='{fam}' AND gt.tag='{tag.replace(chr(39), chr(39)*2)}'
              AND gp.weight IS NOT NULL
        """).fetchone()[0]
        wgap[ft] = None if r is None else float(r - mean_w)
    cw = [ft for ft in tag_feats if ft in tau_map and wgap.get(ft) is not None]
    out["d3_weight_gradient"] = {
        "corr_tau_with_feature_mean_weight_across_features":
            float(np.corrcoef([tau_map[x] for x in cw], [wgap[x] for x in cw])[0, 1]),
        "n_features": len(cw),
    }
    print("D3 corr(tau, feature mean weight):",
          out["d3_weight_gradient"]["corr_tau_with_feature_mean_weight_across_features"])

    # ==================================================================
    # GATE 3: warm half fits + held-out ladder
    # ==================================================================
    def sweep(tag: str) -> float:
        mu = f"(SELECT AVG(rating) FROM v_{tag})"
        con.execute(f"""
            CREATE OR REPLACE TABLE {tag}_ue_new AS
            SELECT v.uid AS uid, AVG(v.rating - {mu} - COALESCE(g.alpha, 0)) AS delta
            FROM v_{tag} v LEFT JOIN {tag}_ge g USING (game_id) GROUP BY 1""")
        m = con.execute(f"SELECT AVG(delta) FROM {tag}_ue_new").fetchone()[0]
        con.execute(f"UPDATE {tag}_ue_new SET delta = delta - ({m})")
        du = con.execute(f"""SELECT COALESCE(MAX(ABS(n.delta - o.delta)), 0)
            FROM {tag}_ue_new n RIGHT JOIN {tag}_ue o USING (uid)""").fetchone()[0]
        con.execute(f"DROP TABLE {tag}_ue")
        con.execute(f"ALTER TABLE {tag}_ue_new RENAME TO {tag}_ue")
        con.execute(f"""
            CREATE OR REPLACE TABLE {tag}_ge_new AS
            SELECT v.game_id AS game_id, AVG(v.rating - {mu} - COALESCE(u.delta, 0)) AS alpha
            FROM v_{tag} v LEFT JOIN {tag}_ue u USING (uid) GROUP BY 1""")
        mg = con.execute(f"SELECT AVG(alpha) FROM {tag}_ge_new").fetchone()[0]
        con.execute(f"UPDATE {tag}_ge_new SET alpha = alpha - ({mg})")
        dg = con.execute(f"""SELECT COALESCE(MAX(ABS(n.alpha - o.alpha)), 0)
            FROM {tag}_ge_new n RIGHT JOIN {tag}_ge o USING (game_id)""").fetchone()[0]
        con.execute(f"DROP TABLE {tag}_ge")
        con.execute(f"ALTER TABLE {tag}_ge_new RENAME TO {tag}_ge")
        return max(float(du), float(dg))

    def build_half(tag: str, where: str):
        con.execute(f"""
            CREATE OR REPLACE TABLE hb_{tag} AS
            SELECT s.user_pseudouserid AS uid, s.game_id, s.rating
            FROM read_parquet('{q(d / 'rating_observations.parquet')}') s
            JOIN read_parquet('{q(d / 'rater_behavior_by_volume.parquet')}') b USING (user_pseudouserid)
            LEFT JOIN read_parquet('{q(d / 'games.parquet')}') gp ON s.game_id = gp.game_id
            WHERE s.rating_observation_id {where}
              AND b.rating_observations >= {MIN_USER_LIFETIME_OBS}
              AND gp.weight IS NOT NULL
        """)
        con.execute(f"CREATE OR REPLACE VIEW v_{tag} AS SELECT uid, game_id, rating FROM hb_{tag}")
        con.execute(f"""CREATE OR REPLACE TABLE {tag}_ge AS
            SELECT game_id, game_alpha AS alpha FROM read_parquet('{q(gm_path)}')""")
        con.execute(f"""CREATE OR REPLACE TABLE {tag}_ue AS
            SELECT user_pseudouserid AS uid, delta_full AS delta FROM read_parquet('{q(sev_path)}')""")
        hist = []
        for _ in range(MAX_SWEEPS):
            hist.append(sweep(tag))
            if hist[-1] < SWEEP_TOL:
                break
        print(f"{tag}: {len(hist)} sweeps, change {hist[-1]:.6f}", flush=True)

    def residuals(tag: str):
        cs = con.execute(f"""
            SELECT AVG(t.rating - COALESCE(g.alpha,0) - COALESCE(u.delta,0))
            FROM hb_{tag} t LEFT JOIN {tag}_ge g USING (game_id)
            LEFT JOIN {tag}_ue u ON t.uid = u.uid
        """).fetchone()[0]
        con.execute(f"""
            CREATE OR REPLACE TABLE res_{tag} AS
            SELECT t.uid, t.game_id, t.rating,
                   t.rating - COALESCE(g.alpha,0) - COALESCE(u.delta,0) - ({cs}) AS r
            FROM hb_{tag} t
            LEFT JOIN {tag}_ge g USING (game_id)
            LEFT JOIN {tag}_ue u ON t.uid = u.uid
        """)
        con.execute(f"DROP TABLE hb_{tag}")

    def cells_and_taus(tag: str):
        con.execute(f"""
            CREATE OR REPLACE TABLE utot_{tag} AS
            SELECT uid, COUNT(*) AS n_all, SUM(r) AS sy_all FROM res_{tag} GROUP BY uid
        """)
        con.execute(f"""
            CREATE OR REPLACE TABLE cells_{tag} AS
            SELECT l.uid, l.feat, COUNT(*) AS n_on, SUM(l.r) AS sy_on
            FROM (
                SELECT s.uid, s.r, m.feat FROM res_{tag} s JOIN gmemb m ON s.game_id = m.game_id
            ) l GROUP BY 1, 2
        """)
        con.execute(f"""
            CREATE OR REPLACE TABLE con_{tag} AS
            SELECT c.uid, c.feat, c.n_on,
                   (c.sy_on / c.n_on) - ((t.sy_all - c.sy_on) / (t.n_all - c.n_on)) AS contrast
            FROM cells_{tag} c JOIN utot_{tag} t USING (uid)
            WHERE c.n_on >= {MIN_USER_OBS_EACH_SIDE}
              AND (t.n_all - c.n_on) >= {MIN_USER_OBS_EACH_SIDE}
        """)
        con.execute(f"""
            CREATE OR REPLACE TABLE taus_{tag} AS
            SELECT feat, AVG(contrast) AS tau FROM con_{tag} GROUP BY 1
        """)

    def eval_ladder(fit_tag: str, test_tag: str) -> dict:
        other = "odd" if fit_tag == "even" else "even"
        assert other == test_tag
        mu_fit = con.execute(f"SELECT AVG(rating) FROM v_{fit_tag}").fetchone()[0]
        # population-level game shift
        con.execute(f"""
            CREATE OR REPLACE TABLE gshift_pop AS
            SELECT m.game_id, SUM(t.tau) AS shift
            FROM gmemb m JOIN taus_{fit_tag} t USING (feat) GROUP BY 1
        """)
        # per-user taste effects (shrunk with population fallback; unshrunk raw)
        con.execute(f"""
            CREATE OR REPLACE TABLE utaste AS
            SELECT c.uid, c.feat,
                   (c.n_on::DOUBLE / (c.n_on + {LAMBDA_SHRINK})) * c.contrast
                     + (1 - c.n_on::DOUBLE / (c.n_on + {LAMBDA_SHRINK})) * t.tau AS s_shrunk,
                   c.contrast AS s_unshrunk
            FROM con_{fit_tag} c JOIN taus_{fit_tag} t USING (feat)
        """)
        # per-test-observation summed shifts
        con.execute(f"""
            CREATE OR REPLACE TABLE oshift AS
            SELECT l.oid,
                   SUM(COALESCE(us.s_shrunk, ta.tau)) AS sum_shrunk,
                   SUM(COALESCE(us.s_unshrunk, ta.tau)) AS sum_unshrunk
            FROM (
                SELECT s.rating_observation_id AS oid, s.uid, m.feat
                FROM res_{test_tag} s JOIN gmemb m ON s.game_id = m.game_id
            ) l
            JOIN taus_{fit_tag} ta ON l.feat = ta.feat
            LEFT JOIN utaste us ON l.uid = us.uid AND l.feat = us.feat
            GROUP BY 1
        """)
        r = con.execute(f"""
            WITH p AS (
                SELECT s.rating AS y,
                       COALESCE(g.alpha, 0) AS alpha_f,
                       COALESCE(u.delta, 0) AS delta_f,
                       COALESCE(p2.shift, 0) AS pop_shift,
                       COALESCE(o.sum_shrunk, 0) AS usr_shrunk,
                       COALESCE(o.sum_unshrunk, 0) AS usr_unshrunk
                FROM res_{test_tag} s
                LEFT JOIN {fit_tag}_ge g ON s.game_id = g.game_id
                LEFT JOIN {fit_tag}_ue u ON s.uid = u.uid
                LEFT JOIN gshift_pop p2 ON s.game_id = p2.game_id
                LEFT JOIN oshift o ON s.rating_observation_id = o.oid
            )
            SELECT
                SQRT(AVG((y - ({mu_fit} + alpha_f))^2))                          AS rmse_m0,
                SQRT(AVG((y - ({mu_fit} + alpha_f + delta_f))^2))                AS rmse_m1,
                SQRT(AVG((y - ({mu_fit} + alpha_f + delta_f + pop_shift))^2))    AS rmse_m2,
                SQRT(AVG((y - ({mu_fit} + alpha_f + delta_f + usr_shrunk))^2))   AS rmse_m3s,
                SQRT(AVG((y - ({mu_fit} + alpha_f + delta_f + usr_unshrunk))^2)) AS rmse_m3u,
                AVG(ABS(y - ({mu_fit} + alpha_f + delta_f)))                     AS mae_m1,
                AVG(ABS(y - ({mu_fit} + alpha_f + delta_f + usr_shrunk)))        AS mae_m3s,
                VAR_SAMP(y),
                COUNT(*)
            FROM p
        """).fetchone()
        return {
            "n_test": int(r[8]), "y_var": float(r[7]),
            "rmse_m0_game_only": float(r[0]), "rmse_m1_additive": float(r[1]),
            "rmse_m2_plus_pop_types": float(r[2]),
            "rmse_m3s_plus_shrunk_user_tastes": float(r[3]),
            "rmse_m3u_plus_unshrunk_user_tastes": float(r[4]),
            "mae_m1_additive": float(r[5]), "mae_m3s": float(r[6]),
        }

    # even -> odd (primary), then odd -> even (symmetry check)
    build_half("even", "% 2 = 0"); residuals("even"); cells_and_taus("even")
    res_even_to_odd = eval_ladder("even", "odd")
    print("fit EVEN -> test ODD:", json.dumps(res_even_to_odd, indent=1))

    # free even-specific big tables before odd fit
    for t in ("res_even", "utot_even", "cells_even", "con_even"):
        con.execute(f"DROP TABLE IF EXISTS {t}")
    con.execute("DROP TABLE IF EXISTS utaste")

    build_half("odd", "% 2 = 1"); residuals("odd"); cells_and_taus("odd")
    res_odd_to_even = eval_ladder("odd", "even")
    print("fit ODD -> test EVEN:", json.dumps(res_odd_to_even, indent=1))

    out["heldout_ladder"] = {"fit_even_predict_odd": res_even_to_odd,
                             "fit_odd_predict_even": res_odd_to_even}

    # in-sample R2 gain of population type effects on full data
    con.execute(f"""
        CREATE OR REPLACE TABLE gshift_full AS
        SELECT m.game_id, SUM(t.tau) AS shift
        FROM gmemb m JOIN (
            SELECT feat, AVG(contrast) AS tau
            FROM read_parquet('{q(args.out_dir / 'phase3_user_tag_contrasts.parquet')}')
            GROUP BY 1
        ) t USING (feat) GROUP BY 1
    """)
    r2row = con.execute(f"""
        WITH p AS (
            SELECT s.r_raw - ({c_shift}) AS e,
                   COALESCE(sh.shift, 0) AS pop_shift,
                   CASE WHEN s.user_n_obs < {MIN_USER_LIFETIME_OBS} THEN TRUE ELSE FALSE END AS excl
            FROM src s LEFT JOIN gshift_full sh ON s.game_id = sh.game_id
            WHERE s.covered
        )
        SELECT VAR_SAMP(e), VAR_SAMP(e - pop_shift), COUNT(*)
        FROM p WHERE NOT excl
    """).fetchone()
    var_e, var_et, n_in = float(r2row[0]), float(r2row[1]), int(r2row[2])
    out["insample_population_type_gain"] = {
        "n_obs_inscope_covered": n_in,
        "resid_var_additive": var_e,
        "resid_var_after_population_types": var_et,
        "variance_reduction_fraction": float(1 - var_et / var_e),
        "r2_gain_points": float((var_e - var_et) / (var_e + (out.get("y_var_total") or 0) * 0)),
    }
    out["insample_population_type_gain"].pop("r2_gain_points")

    (args.out_dir / "phase3_distinctness_materiality.json").write_text(
        json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print("\nwrote phase3_distinctness_materiality.json")
    con.close()


if __name__ == "__main__":
    main()

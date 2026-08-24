"""Phase 3 step (b), Gate 1: do within-user TYPE CONTRASTS replicate across
independent observation halves?

The Phase 2 severity program established parity-half stability for GLOBAL
user offsets (r=0.872).  This script applies the same design to the per-user
type contrasts from scripts/23:

  1. Refit the additive model rating = mu + alpha_g + delta_u ON EACH PARITY
     HALF (rating_observation_id even/odd), warm-started from the full-fit
     artifacts (speed-only initialization: the objective is jointly convex,
     so the converged half-fit is unique regardless of init).
  2. Compute per-user-per-feature contrasts within each half using that
     half's own parameters (no parameter leakage across halves).
  3. Stability statistics: per-feature cross-half Pearson/Spearman of user
     contrasts; pooled tau_t per half -> replication slope/correlation;
     placebo correlations under deliberately mismatched users; BH-FDR
     (q=0.05) within family on even-half z-scores with odd-half replication
     flags.

Timestamps unused.  Scope identical to scripts/23: covered observations,
>=20-lifetime-obs users, >=MIN_USER_OBS_EACH_SIDE obs per side WITHIN HALF.

Outputs: data/processed/phase3/phase3_contrast_stability.json,
         data/processed/phase3/phase3_half_contrasts.parquet
"""

import argparse
import json
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from scipy import stats as sps

REPO_DIR = Path(__file__).resolve().parent.parent

MIN_USER_OBS_EACH_SIDE = 5
MIN_USER_LIFETIME_OBS = 20
TOP_N_TAGS = 12
MAX_SWEEPS = 80
SWEEP_TOL = 4e-3


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

    # ------------------------------------------------------------------
    # Feature universe (same selection rule as script 23)
    # ------------------------------------------------------------------
    fams = {}
    for fam in ("category", "mechanic", "theme"):
        df = con.execute(f"""
            WITH gm AS (SELECT game_id, COUNT(*) AS n_obs
                        FROM read_parquet('{q(d / 'rating_observations.parquet')}') WHERE rating IS NOT NULL GROUP BY 1)
            SELECT gt.tag, SUM(gm.n_obs) AS n_obs
            FROM read_parquet('{q(d / 'game_tags.parquet')}') gt JOIN gm USING (game_id)
            WHERE gt.tag_type = '{fam}'
            GROUP BY 1 ORDER BY n_obs DESC LIMIT {TOP_N_TAGS}
        """).fetchdf()
        fams[fam] = df["tag"].tolist()
    feats = ([f"{fam}::{t}" for fam in ("category", "mechanic", "theme") for t in fams[fam]]
             + ["wb_light", "wb_medium", "wb_heavy"])
    print(f"features: {len(feats)}")

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
    """)

    summary = {"min_user_obs_each_side": MIN_USER_OBS_EACH_SIDE,
               "min_user_lifetime_obs": MIN_USER_LIFETIME_OBS,
               "max_sweeps": MAX_SWEEPS, "sweep_tol": SWEEP_TOL}

    def sweep(tag: str) -> float:
        """One alternating-projection pair; returns max param change."""
        mu = f"(SELECT AVG(rating) FROM v_{tag})"
        con.execute(f"""
            CREATE OR REPLACE TABLE {tag}_ue_new AS
            SELECT v.uid AS uid, AVG(v.rating - {mu} - COALESCE(g.alpha, 0)) AS delta
            FROM v_{tag} v LEFT JOIN {tag}_ge g USING (game_id) GROUP BY 1""")
        m = con.execute(f"SELECT AVG(delta) FROM {tag}_ue_new").fetchone()[0]
        con.execute(f"UPDATE {tag}_ue_new SET delta = delta - ({m})")
        du = con.execute(f"""
            SELECT COALESCE(MAX(ABS(n.delta - o.delta)), 0)
            FROM {tag}_ue_new n RIGHT JOIN {tag}_ue o USING (uid)
        """).fetchone()[0]
        con.execute(f"DROP TABLE {tag}_ue")
        con.execute(f"ALTER TABLE {tag}_ue_new RENAME TO {tag}_ue")

        con.execute(f"""
            CREATE OR REPLACE TABLE {tag}_ge_new AS
            SELECT v.game_id AS game_id,
                   AVG(v.rating - {mu} - COALESCE(u.delta, 0)) AS alpha
            FROM v_{tag} v LEFT JOIN {tag}_ue u USING (uid) GROUP BY 1""")
        mg = con.execute(f"SELECT AVG(alpha) FROM {tag}_ge_new").fetchone()[0]
        con.execute(f"UPDATE {tag}_ge_new SET alpha = alpha - ({mg})")
        dg = con.execute(f"""
            SELECT COALESCE(MAX(ABS(n.alpha - o.alpha)), 0)
            FROM {tag}_ge_new n RIGHT JOIN {tag}_ge o USING (game_id)
        """).fetchone()[0]
        con.execute(f"DROP TABLE {tag}_ge")
        con.execute(f"ALTER TABLE {tag}_ge_new RENAME TO {tag}_ge")
        return max(float(du), float(dg))

    results = {}
    for tag, where in (("even", "% 2 = 0"), ("odd", "% 2 = 1")):
        con.execute(f"""
            CREATE OR REPLACE TABLE hb_{tag} AS
            SELECT s.user_pseudouserid AS uid,
                   s.game_id,
                   b.volume_band,
                   CASE WHEN b.volume_band IN ('1','2-4','5-9') THEN 'low'
                        WHEN b.volume_band IN ('10-24','25-49','50-99',
                                               '100-249','250-499') THEN 'mid'
                        ELSE 'high' END AS band_group,
                   s.rating,
                   gp.weight IS NOT NULL AS covered,
                   CASE WHEN gp.weight IS NULL THEN NULL
                        WHEN gp.weight < 1.75 THEN 'wb_light'
                        WHEN gp.weight < 2.75 THEN 'wb_medium'
                        ELSE 'wb_heavy' END AS wband
            FROM read_parquet('{q(d / 'rating_observations.parquet')}') s
            JOIN read_parquet('{q(d / 'rater_behavior_by_volume.parquet')}') b USING (user_pseudouserid)
            LEFT JOIN read_parquet('{q(d / 'games.parquet')}') gp ON s.game_id = gp.game_id
            WHERE s.rating_observation_id {where}
              AND b.rating_observations >= {MIN_USER_LIFETIME_OBS}
              AND gp.weight IS NOT NULL
        """)
        con.execute(f"CREATE OR REPLACE VIEW v_{tag} AS SELECT uid, game_id, rating FROM hb_{tag}")

        # warm start from full-fit artifacts
        con.execute(f"""CREATE OR REPLACE TABLE {tag}_ge AS
                        SELECT game_id, game_alpha AS alpha FROM read_parquet('{q(gm_path)}')""")
        con.execute(f"""CREATE OR REPLACE TABLE {tag}_ue AS
                        SELECT user_pseudouserid AS uid, delta_full AS delta
                        FROM read_parquet('{q(sev_path)}')""")
        hist = []
        for _ in range(MAX_SWEEPS):
            hist.append(sweep(tag))
            if hist[-1] < SWEEP_TOL:
                break
        mu = con.execute(f"SELECT AVG(rating) FROM v_{tag}").fetchone()[0]
        summary[f"als_{tag}"] = {"mu": float(mu), "sweeps": len(hist),
                                 "final_change": hist[-1]}
        print(f"{tag}: mu={mu:.4f}, {len(hist)} sweeps, final change {hist[-1]:.6f}", flush=True)

        cs = con.execute(f"""
            SELECT AVG(t.rating - COALESCE(g.alpha, 0) - COALESCE(u.delta, 0))
            FROM hb_{tag} t
            LEFT JOIN {tag}_ge g USING (game_id)
            LEFT JOIN {tag}_ue u ON t.uid = u.uid
        """).fetchone()[0]
        con.execute(f"""
            CREATE OR REPLACE TABLE res_{tag} AS
            SELECT t.uid, t.wband, t.game_id,
                   t.rating - COALESCE(g.alpha, 0) - COALESCE(u.delta, 0) - ({cs}) AS r
            FROM hb_{tag} t
            LEFT JOIN {tag}_ge g USING (game_id)
            LEFT JOIN {tag}_ue u ON t.uid = u.uid
        """)
        con.execute(f"DROP TABLE hb_{tag}")
        con.execute(f"""
            CREATE OR REPLACE TABLE utot_{tag} AS
            SELECT uid, COUNT(*) AS n_all, SUM(r) AS sy_all FROM res_{tag} GROUP BY uid
        """)
        con.execute(f"""
            CREATE OR REPLACE TABLE cells_{tag} AS
            SELECT l.uid, l.feat, COUNT(*) AS n_on, SUM(l.r) AS sy_on
            FROM (
                SELECT s.uid, s.r, m.feat
                FROM res_{tag} s JOIN gmemb m ON s.game_id = m.game_id
                UNION ALL
                SELECT uid, r, wband AS feat FROM res_{tag} WHERE wband IS NOT NULL
            ) l GROUP BY 1, 2
        """)
        con.execute(f"""
            CREATE OR REPLACE TABLE con_{tag} AS
            SELECT c.uid, c.feat, c.n_on, (t.n_all - c.n_on) AS n_off,
                   (c.sy_on / c.n_on) - ((t.sy_all - c.sy_on) / (t.n_all - c.n_on)) AS contrast
            FROM cells_{tag} c JOIN utot_{tag} t USING (uid)
            WHERE c.n_on >= {MIN_USER_OBS_EACH_SIDE}
              AND (t.n_all - c.n_on) >= {MIN_USER_OBS_EACH_SIDE}
        """)
        n_inf = con.execute(f"SELECT COUNT(*), COUNT(DISTINCT uid) FROM con_{tag}").fetchone()
        tau = con.execute(f"""
            SELECT feat, COUNT(*) AS n_users, AVG(contrast) AS tau, STDDEV_SAMP(contrast) AS sd
            FROM con_{tag} GROUP BY feat
        """).fetchdf().set_index("feat")
        results[tag] = {"n_cells": int(n_inf[0]), "n_users": int(n_inf[1]), "tau": tau}
        print(f"{tag}: {n_inf[0]:,} informative cells over {n_inf[1]:,} users")

    # ------------------------------------------------------------------
    # Stability statistics
    # ------------------------------------------------------------------
    joined = con.execute("""
        SELECT e.feat, e.uid, e.contrast AS c_even, o.contrast AS c_odd
        FROM con_even e JOIN con_odd o USING (uid, feat)
    """).fetchdf()
    print(f"joined (uid,feat) cells across halves: {len(joined):,}")

    rows = []
    for ft in feats:
        sub = joined[joined.feat == ft]
        if len(sub) < 100 or ft not in results["even"]["tau"].index:
            continue
        ce = sub.c_even.values.astype(float)
        co = sub.c_odd.values.astype(float)
        pear = float(np.corrcoef(ce, co)[0, 1])
        sp = float(pd.Series(ce).rank().corr(pd.Series(co).rank()))
        plac = float(np.corrcoef(ce, np.roll(co, len(co) // 2))[0, 1])
        rows.append({"feat": ft, "n_users_both_halves": int(len(sub)),
                     "pearson_even_odd": pear, "spearman_even_odd": sp,
                     "placebo_pearson": plac,
                     "tau_even": float(results["even"]["tau"].loc[ft, "tau"]),
                     "tau_odd": float(results["odd"]["tau"].loc[ft, "tau"]),
                     "sd_within_user_contrast_full": None})
    st = pd.DataFrame(rows)

    zrows = []
    for ft in feats:
        if ft not in results["even"]["tau"].index or ft not in results["odd"]["tau"].index:
            continue
        ne = int(results["even"]["tau"].loc[ft, "n_users"])
        no = int(results["odd"]["tau"].loc[ft, "n_users"])
        te = float(results["even"]["tau"].loc[ft, "tau"])
        to = float(results["odd"]["tau"].loc[ft, "tau"])
        se_e = float(results["even"]["tau"].loc[ft, "sd"]) / np.sqrt(ne)
        if se_e <= 0:
            continue
        zrows.append({"feat": ft, "family": ft.split("::")[0], "n_users_even": ne,
                      "z_even": te / se_e, "tau_even": te, "tau_odd": to})
    zdf = pd.DataFrame(zrows)
    sig_all, p_all = [], []
    for _, famdf in zdf.groupby("family"):
        z = famdf.z_even.values.astype(float)
        p = 2 * sps.norm.sf(np.abs(z))
        order = np.argsort(p)
        n = len(p)
        thresh = 0.05 * np.arange(1, n + 1) / n
        below = p[order] <= thresh
        sig = np.zeros(n, dtype=bool)
        if below.any():
            k = np.max(np.nonzero(below)[0]) + 1
            sig[order[:k]] = True
        sig_all.extend(sig)
        p_all.extend(p)
    zdf["p_even"] = p_all
    zdf["sig_fdr_q05_within_family"] = sig_all
    zdf["sign_replicated_odd"] = np.sign(zdf.tau_even) == np.sign(zdf.tau_odd)
    zdf["tau_replication_ratio"] = zdf.tau_odd / zdf.tau_even

    rep_corr = float(np.corrcoef(zdf.tau_even, zdf.tau_odd)[0, 1])
    rep_slope = float(np.polyfit(zdf.tau_even, zdf.tau_odd, 1)[0])

    summary["stability_by_feature"] = st.to_dict(orient="records")
    summary["fdr_table"] = zdf.to_dict(orient="records")
    summary["pooled_tau_replication"] = {
        "pearson_even_vs_odd": rep_corr,
        "slope_odd_on_even": rep_slope,
        "n_features": int(len(zdf)),
        "n_sig_fdr_q05_any_family": int(zdf.sig_fdr_q05_within_family.sum()),
        "n_sig_and_sign_replicated": int((zdf.sig_fdr_q05_within_family & zdf.sign_replicated_odd).sum()),
    }
    summary["headline"] = {
        "median_cross_half_pearson": float(st.pearson_even_odd.median()) if len(st) else None,
        "median_placebo_pearson": float(st.placebo_pearson.median()) if len(st) else None,
        "max_placebo_pearson": float(st.placebo_pearson.max()) if len(st) else None,
    }
    print("\nstability by feature:")
    print(st.sort_values("pearson_even_odd", ascending=False).to_string(index=False))
    print("\npooled-tau replication:", summary["pooled_tau_replication"])

    con.execute(f"""
        COPY (
            SELECT 'even' AS half, * FROM con_even
            UNION ALL
            SELECT 'odd' AS half, * FROM con_odd
        ) TO '{q(args.out_dir / 'phase3_half_contrasts.parquet')}'
        (FORMAT PARQUET, COMPRESSION ZSTD)
    """)
    (args.out_dir / "phase3_contrast_stability.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print("wrote outputs")
    con.close()


if __name__ == "__main__":
    main()

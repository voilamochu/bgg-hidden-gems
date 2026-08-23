"""Phase B step 4: which rater-level measures are actually identifiable?

The captain's question: can rater credibility be measured, and could it
justify corrections?  Prior steps established:
  - severity offsets delta_u exist, are large, ordered by lifetime volume,
    stable across independent halves (parity r ~ 0.87);
  - they close the standardized low-vs-high gap almost exactly (+0.01).

This script quantifies what is *identifiable* versus *entangled*:

  1. Reliability of severity estimation: how precisely can delta_u be pinned
     down as a function of observation count?  Uses parity-half deltas
     (independent halves) to decompose observed variance into signal and
     noise per volume band; reports ICC-style reliability and the number of
     observations needed for a target precision.
  2. Entanglement audit: correlations of candidate "credibility" measures
     (volume, severity, within-user spread, tenure, era mix) with each other;
     shows volume is not separable from activity/exposure/selection.
  3. Accuracy check: state plainly that no external accuracy target exists
     in this data; internal consistency != accuracy.

Outputs: rater_credibility.json (+ reuses user_severity.parquet).
"""

import argparse
import json
from pathlib import Path

import duckdb
import numpy as np

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
    con.execute(f"CREATE OR REPLACE VIEW usrs AS SELECT * FROM read_parquet('{q(data_dir / 'users.parquet')}')")

    summary = {"data_dir": str(data_dir)}

    # ------------------------------------------------------------------
    # 1. Reliability of delta_u by volume band (parity-half decomposition)
    # ------------------------------------------------------------------
    rel_rows = []
    for band in BAND_ORDER:
        r = con.execute("""
            WITH j AS (
                SELECT s.delta_even AS de, s.delta_odd AS do_,
                       s.rating_observations AS n
                FROM sev s WHERE s.volume_band = ? AND s.delta_even IS NOT NULL
            ), f AS (
                SELECT * FROM j WHERE
                  (CASE WHEN n >= 20 THEN LEAST(n // 2, n - n // 2)
                        ELSE 0 END) >= ?
            )
            SELECT COUNT(*),
                   STDDEV_SAMP(de), STDDEV_SAMP(do_), STDDEV_SAMP(de - do_)
            FROM f
        """, [band, 10]).fetchone()
        if not r[0]:
            continue
        users, sd_e, sd_o, sd_d = map(float, r)
        # noise SD of a half-estimate ~ sd(diff)/sqrt(2); signal = total - noise
        noise_half = sd_d / np.sqrt(2.0)
        var_total = sd_e ** 2
        var_signal = max(var_total - noise_half ** 2, 0.0)
        reliability = var_signal / var_total if var_total > 0 else float("nan")
        rel_rows.append({
            "band": band, "users_compared": int(users),
            "sd_half_estimate": sd_e,
            "implied_noise_sd_half": noise_half,
            "implied_signal_sd": np.sqrt(var_signal),
            "reliability_icc_style": reliability,
        })
    summary["severity_reliability_by_band"] = {
        "min_half_obs": 10,
        "rows": rel_rows,
        "note": "signal/noise decomposition of parity-half severity estimates; "
                "single-rating users are excluded because no half estimate exists",
    }

    # Precision scaling: empirical SE of full-sample delta vs observation count
    prec = con.execute("""
        SELECT LEAST(CAST(rating_observations / 50 AS INTEGER), 20) AS bucket,
               COUNT(*) AS users,
               AVG(rating_observations) AS mean_n,
               STDDEV_SAMP(delta_full) AS sd_delta
        FROM sev WHERE delta_full IS NOT NULL
        GROUP BY 1 ORDER BY 1
    """).fetchdf()
    summary["delta_dispersion_by_count_bucket"] = prec.to_dict(orient="records")

    # ------------------------------------------------------------------
    # 2. Entanglement audit among candidate rater measures
    # ------------------------------------------------------------------
    ent = con.execute("""
        WITH m AS (
            SELECT v.rating_observations AS n_obs,
                   v.within_user_sd AS wsd,
                   sv.delta_full AS delta,
                   DATE_DIFF('day',
                             MIN(TRY_CAST(o.postdate AS TIMESTAMP)),
                             MAX(TRY_CAST(o.postdate AS TIMESTAMP))) AS tenure_days
            FROM ro o
            JOIN rbv v ON o.user_pseudouserid = v.user_pseudouserid
            JOIN sev sv ON o.user_pseudouserid = sv.user_pseudouserid
            WHERE o.postdate IS NOT NULL
            GROUP BY 1, 2, 3
        )
        SELECT CORR(LOG2(n_obs)::DOUBLE, delta),
               CORR(LOG2(n_obs)::DOUBLE, wsd),
               CORR(delta, wsd),
               CORR(LOG2(tenure_days + 1)::DOUBLE, delta),
               CORR(LOG2(n_obs)::DOUBLE, LOG2(tenure_days + 1)::DOUBLE),
               COUNT(*)
        FROM m
    """).fetchone()
    summary["entanglement"] = {
        "n_users_with_postdates": int(ent[5]),
        "corr_log_volume_vs_severity": float(ent[0]),
        "corr_log_volume_vs_within_user_sd": float(ent[1]),
        "corr_severity_vs_within_user_sd": float(ent[2]),
        "corr_log_tenure_vs_severity": float(ent[3]),
        "corr_log_volume_vs_log_tenure": float(ent[4]),
        "note": "tenure uses unresolved-semantics postdate field",
    }

    # First-activity cohort (join-era proxy): severity by starting year
    cohort = con.execute("""
        WITH firsty AS (
            SELECT user_pseudouserid, YEAR(MIN(TRY_CAST(postdate AS TIMESTAMP))) AS y0
            FROM ro WHERE postdate IS NOT NULL GROUP BY 1
        )
        SELECT f.y0, COUNT(*) AS users, AVG(s.delta_full) AS mean_delta,
               AVG(s.rating_observations) AS mean_n
        FROM firsty f JOIN sev s ON f.user_pseudouserid = s.user_pseudouserid
        WHERE s.delta_full IS NOT NULL AND f.y0 IS NOT NULL
        GROUP BY 1 HAVING COUNT(*) >= 500 ORDER BY 1
    """).fetchdf()
    summary["severity_by_first_activity_year"] = cohort.to_dict(orient="records")

    # ------------------------------------------------------------------
    # 3. Explicit identifiability statement (no computation needed)
    # ------------------------------------------------------------------
    summary["identifiability_statement"] = {
        "accuracy_target_available": False,
        "statement": (
            "No external accuracy criterion exists in this data: there is no "
            "ground-truth game quality, no repeated independent rating task, "
            "and no rater panel. Internal consistency (split-half stability, "
            "low within-user dispersion) is measurable and is NOT accuracy. "
            "Volume, severity, tenure, and spread are mutually entangled "
            "activity/exposure/selection measures. Any 'credibility weight' "
            "built from them would encode choices about which entangled "
            "quantity to reward, not measured correctness."
        ),
    }

    (out_dir / "rater_credibility.json").write_text(
        json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")

    print(json.dumps({k: summary[k] for k in [
        "severity_reliability_by_band", "entanglement"]}, indent=2, default=str))
    print("cohort:", cohort.head(30).to_string(index=False))
    con.close()


if __name__ == "__main__":
    main()

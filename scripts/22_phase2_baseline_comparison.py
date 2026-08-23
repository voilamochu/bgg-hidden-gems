"""Phase B step 8: compare user-derived game estimates against existing
baselines, and classify what the friend-provided correction targets.

Estimates compared on matched games:
  A. Phase 2 user-level snapshot (scripts 15-17):
     raw_mean            - pooled mean rating per game
     adj_mean            - severity-adjusted mean (rating minus user delta)
     game_alpha + mu     - two-way additive fit level
  B. Game-level snapshot baselines:
     avg_rating_current  - raw BGG average
     bayes_rating        - BGG Bayesian rating
     resid_S3_categories - RQ2 descriptive residual (script 05)
  C. Friend file: debiased_rating.

Key questions:
  1. Does removing rater-level offsets change the game-level
     volume-rating gradient?  (RQ1 mechanism split)
  2. Does the friend's game-level correction align with our severity
     adjustment (same target), or something else?
  3. How do top sets overlap?

The snapshots differ (SQLite dump vs current scrape); cross-snapshot joins
are reported with coverage so correlations are read as upper bounds on
agreement.
"""

import argparse
import json
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

REPO_DIR = Path(__file__).resolve().parent.parent


def q(path) -> str:
    return str(path).replace("'", "''")


def find_data_dir() -> Path:
    scratch = REPO_DIR / "scratch" / "phase2"
    return scratch if (scratch / "games.parquet").exists() \
        else REPO_DIR / "data" / "processed" / "phase2"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", type=Path, default=None)
    ap.add_argument("--out-dir", type=Path, default=REPO_DIR / "data" / "processed" / "phase2")
    args = ap.parse_args()

    data_dir = args.data_dir or find_data_dir()
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    proc_dir = REPO_DIR / "data" / "processed"

    summary = {"data_dir": str(data_dir)}

    con = duckdb.connect()
    con.execute(f"CREATE OR REPLACE VIEW p2gm AS SELECT * FROM read_parquet('{q(out_dir / 'game_adjusted_means.parquet')}')")
    con.execute(f"CREATE OR REPLACE VIEW rq2 AS SELECT * FROM read_parquet('{q(proc_dir / 'rq2_residuals.parquet')}')")
    con.execute(f"CREATE OR REPLACE VIEW pop AS SELECT * FROM read_parquet('{q(proc_dir / 'bgg_research_population.parquet')}')")
    con.execute(f"""
        CREATE OR REPLACE VIEW friend AS
        SELECT game_id, debiased_rating, debiased_rank
        FROM read_csv_auto('{q(REPO_DIR / 'data' / 'raw' / 'complete_2025_bgg_debiased_ranks.csv')}')
    """)

    # Master join
    m = con.execute("""
        SELECT p.game_id,
               p.raw_mean AS p2_raw, p.adj_mean AS p2_adj, p.n_obs AS p2_n_obs,
               r.avg_rating_current AS gl_avg, r.bayes_rating AS gl_bayes,
               r.users_rated AS gl_users_rated,
               r.resid_S3_categories AS rq2_resid_s3,
               f.debiased_rating AS friend_debiased,
               pp.year AS year, pp.weight AS weight
        FROM p2gm p
        JOIN rq2 r USING (game_id)
        LEFT JOIN friend f USING (game_id)
        JOIN (SELECT game_id, year, weight FROM pop) pp ON p.game_id = pp.game_id
    """).fetchdf()
    summary["matched_games"] = int(len(m))
    summary["matched_with_friend"] = int(m.friend_debiased.notna().sum())
    summary["population_games"] = int(con.execute("SELECT COUNT(*) FROM pop").fetchone()[0])
    summary["p2_snapshot_games"] = int(con.execute("SELECT COUNT(*) FROM p2gm").fetchone()[0])

    # Snapshot consistency check
    r_snap = con.execute(f"""
        WITH rk AS (
            SELECT p2_raw, gl_avg,
                   RANK() OVER (ORDER BY p2_raw) AS ra,
                   RANK() OVER (ORDER BY gl_avg) AS rb
            FROM m
        )
        SELECT CORR(p2_raw, gl_avg), CORR(ra::DOUBLE, rb::DOUBLE),
               QUANTILE_CONT(gl_avg - p2_raw, 0.5), STDDEV_SAMP(gl_avg - p2_raw)
        FROM rk
    """).fetchone()
    summary["snapshot_consistency_raw_means"] = {
        "pearson": float(r_snap[0]), "spearman": float(r_snap[1]),
        "median_game_level_diff": float(r_snap[2]), "sd_of_diff": float(r_snap[3])}

    # ------------------------------------------------------------------
    # 1. Volume gradients under each estimate
    # ------------------------------------------------------------------
    m["log_users"] = np.log10(m.gl_users_rated.clip(lower=1))
    grads = {}
    for est in ["p2_raw", "p2_adj", "gl_avg", "gl_bayes", "friend_debiased"]:
        sub = m[[est, "log_users"]].dropna()
        b, a = np.polyfit(sub.log_users, sub[est], 1)
        grads[est] = {"slope_per_tenfold_ratings": float(b),
                      "n": int(len(sub))}
    # partial: control weight & year for the key contrast
    import numpy.linalg as la
    def ols(y, X):
        Xd = np.column_stack([np.ones(X[0].shape[0])] + list(X))
        beta, *_ = la.lstsq(Xd, y, rcond=None)
        resid = y - Xd @ beta
        return beta, 1 - (resid ** 2).sum() / ((y - y.mean()) ** 2).sum()
    sub = m[["p2_raw", "log_users", "year", "weight"]].dropna()
    b_raw, r2_raw = ols(sub.p2_raw.values,
                        [sub.log_users.values, sub.year.values - sub.year.mean(),
                         sub.weight.values - sub.weight.mean()])
    sub = m[["p2_adj", "log_users", "year", "weight"]].dropna()
    b_adj, r2_adj = ols(sub.p2_adj.values,
                        [sub.log_users.values, sub.year.values - sub.year.mean(),
                         sub.weight.values - sub.weight.mean()])
    summary["volume_gradients"] = {
        "simple_slopes": grads,
        "note": "slope = rating points per tenfold increase in users_rated",
        "adjusted_for_weight_year": {
            "p2_raw_log_users_coef": float(b_raw[1]), "r2": float(r2_raw),
            "p2_adj_log_users_coef": float(b_adj[1]), "r2": float(r2_adj)},
    }

    # ------------------------------------------------------------------
    # 2. Correlation structure among estimates
    # ------------------------------------------------------------------
    cols = ["p2_raw", "p2_adj", "gl_avg", "gl_bayes", "rq2_resid_s3", "friend_debiased"]
    corr = m[cols].corr(method="pearson")
    spear = m[cols].corr(method="spearman")
    summary["correlations_pearson"] = json.loads(corr.round(4).to_json())
    summary["correlations_spearman"] = json.loads(spear.round(4).to_json())

    # ------------------------------------------------------------------
    # 3. What does each correction target?
    # ------------------------------------------------------------------
    m["p2_shift"] = m.p2_adj - m.p2_raw              # our severity shift
    m["friend_shift"] = m.friend_debiased - m.gl_avg  # friend correction
    tgt = {}
    for name, col in [("our_severity_shift", "p2_shift"), ("friend_shift", "friend_shift"),
                      ("rq2_resid_s3", "rq2_resid_s3")]:
        t = con.execute(f"""
            WITH rk AS (
                SELECT {col} AS v, LOG2(gl_users_rated::DOUBLE) AS lu,
                       RANK() OVER (ORDER BY {col}) AS rr,
                       RANK() OVER (ORDER BY gl_users_rated) AS ru,
                       RANK() OVER (ORDER BY year) AS ry,
                       RANK() OVER (ORDER BY weight) AS rw
                FROM m WHERE {col} IS NOT NULL AND gl_users_rated IS NOT NULL
            )
            SELECT CORR(v, lu), CORR(rr::DOUBLE, ru::DOUBLE),
                   CORR(rr::DOUBLE, ry::DOUBLE), CORR(rr::DOUBLE, rw::DOUBLE),
                   COUNT(*)
            FROM rk
        """).fetchone()
        tgt[name] = {
            "corr_with_log_volume": float(t[0]),
            "spearman_with_volume": float(t[1]),
            "spearman_with_year": float(t[2]),
            "spearman_with_weight": float(t[3]),
            "n": int(t[4]),
        }
    tgt["cross_alignment_friend_vs_our_shift"] = float(
        m[["p2_shift", "friend_shift"]].corr().iloc[0, 1])
    tgt["cross_alignment_friend_vs_rq2resid"] = float(
        m[["rq2_resid_s3", "friend_shift"]].corr().iloc[0, 1])
    summary["correction_targets"] = tgt

    # ------------------------------------------------------------------
    # 4. Top-set overlaps (top 5% positive by each adjusted measure)
    # ------------------------------------------------------------------
    def top_set(col, frac=0.05):
        s = m[col].dropna()
        thr = s.quantile(1 - frac)
        return set(m.loc[s.index[s >= thr], "game_id"])

    sets = {
        "our_adj_top5": top_set("p2_adj"),
        "friend_debiased_top5": top_set("friend_debiased"),
        "rq2_resid_top5": top_set("rq2_resid_s3"),
        "raw_avg_top5": top_set("gl_avg"),
        "bayes_top5": top_set("gl_bayes"),
    }
    ov = {}
    names = list(sets)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            inter = len(sets[a] & sets[b])
            ov[f"{a}|{b}"] = {"intersection": inter,
                              "jaccard": round(inter / len(sets[a] | sets[b]), 3)}
    summary["top5_overlaps"] = ov

    m.to_parquet(out_dir / "baseline_comparison_table.parquet", index=False)
    (out_dir / "baseline_comparison.json").write_text(
        json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")

    print(json.dumps({k: summary[k] for k in [
        "matched_games", "matched_with_friend", "snapshot_consistency_raw_means",
        "volume_gradients", "correction_targets", "top5_overlaps"]},
        indent=1, default=str)[:5000])
    con.close()


if __name__ == "__main__":
    main()

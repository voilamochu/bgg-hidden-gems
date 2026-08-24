"""Sensitivity study: active (16,564 games, n_active >=1; 1-99 bucket 1,612 games)
vs n_active >=100 for games (14,952 games). Users fixed at >=10 in-universe
excluding degenerate_strict. Single-filter study, not recursive closure.

Compares Phase 5 quality-estimator (Var(adj), sigma_e, sigma_alpha, lambda, SE,
shrinkage table, held-out adj_odd RMSE/R2/corr/bias) and Phase 6 Q3b/OLS
expected-quality (R2/RMSE CV, beta weight/year/categories, corr(resid,log n),
residual distribution, rank stability spearman/Jaccard, top residual overlap).

Do NOT alter primary results; reuse phase2-active inputs via copy-once to
scratch/phase2-active. Bounded: memory 4GB threads 3 temp scratch/ducktmp.
"""
import argparse
import json
import shutil
import sys
import time
from collections import Counter
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
MEMORY = "4GB"
THREADS = 3
RANDOM_SEED = 20260824
N_FOLDS = 5
TAG_MIN_COUNT = 500
TOP_FRAC = 0.01
VOL_BAND_EDGES = [0, 100, 200, 500, 1000, 2500, 5000, 10000, 25000, np.inf]
VOL_BAND_LABELS = ["1-99", "100-199", "200-499", "500-999", "1k-2.5k", "2.5k-5k",
                   "5k-10k", "10k-25k", "25k+"]
SIGMA_E_FALLBACK = None  # filled from phase5 json


def qpath(p: Path) -> str:
    return str(p).replace("'", "''")


def configure(con, tmp_dir: Path):
    con.execute(f"SET memory_limit='{MEMORY}'")
    con.execute(f"SET threads={THREADS}")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    con.execute(f"SET temp_directory='{qpath(tmp_dir)}'")
    con.execute("SET preserve_insertion_order=false")


def ensure_scratch_copy(active_dir: Path):
    src = REPO / "data/processed/phase2-active"
    dst = active_dir
    needed = ["game_adjusted_means_active.parquet", "user_severity_active.parquet",
              "rating_observations_active.parquet", "users_active.parquet"]
    dst.mkdir(parents=True, exist_ok=True)
    for fn in needed:
        dp, sp = dst / fn, src / fn
        if not dp.exists() and sp.exists():
            print(f"  copy-once {sp} -> {dp}")
            shutil.copy2(sp, dp)
    pop_src = REPO / "data/processed/bgg_research_population.parquet"
    pop_dst = dst / "bgg_research_population.parquet"
    if not pop_dst.exists() and pop_src.exists():
        print(f"  copy-once {pop_src} -> {pop_dst}")
        shutil.copy2(pop_src, pop_dst)


def load_phase5_params():
    cand = REPO / "data/processed/phase2-active/phase5_quality_estimator.json"
    j = json.loads(cand.read_text())
    evc = j.get("eb_variance_components", {})
    mu = j["validation"]["mu_active"]
    sigma_e = evc["sigma_e_sd"]
    sigma_a2 = evc["sigma_alpha2_mm"]
    sig_e2 = sigma_e ** 2
    return mu, sigma_e, sig_e2, sigma_a2, j


# ---- modelling helpers (same as 30/31) ----
def fit_wls(X, y, w):
    sw = np.sqrt(w)
    beta, *_ = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)
    pred = X @ beta
    return beta, pred, y - pred


def metrics(y, resid):
    sse = float(np.sum(resid ** 2))
    sst = float(np.sum((y - np.mean(y)) ** 2))
    return {"r2": 1 - sse / sst if sst > 0 else float("nan"),
            "rmse": float(np.sqrt(np.mean(resid ** 2))),
            "mae": float(np.mean(np.abs(resid)))}


def cv_predictions(X, y, w, folds=N_FOLDS, seed=RANDOM_SEED):
    n = len(y)
    rng = np.random.default_rng(seed)
    order = rng.permutation(n)
    pred = np.full(n, np.nan)
    betas = []
    fold_idx = []
    for test_idx in np.array_split(order, folds):
        train_mask = np.ones(n, dtype=bool)
        train_mask[test_idx] = False
        beta, _, _ = fit_wls(X[train_mask], y[train_mask], w[train_mask])
        pred[test_idx] = X[test_idx] @ beta
        betas.append(beta)
        fold_idx.append(test_idx)
    return pred, y - pred, np.array(betas), fold_idx


def top_jaccard(a, b, frac=TOP_FRAC):
    k = max(1, int(frac * len(a)))
    # a,b aligned on same game set if possible; caller handles alignment
    sa, sb = set(np.argsort(a)[-k:]), set(np.argsort(b)[-k:])
    return len(sa & sb) / len(sa | sb), k


def ns_basis(x, knots):
    k = np.asarray(knots, dtype=float)
    K = len(k)
    denom = max(k[K - 1] - k[K - 2], 1e-9)
    cols = [x]
    for j in range(K - 2):
        t1 = np.maximum(x - k[j], 0) ** 3
        t2 = np.maximum(x - k[K - 2], 0) ** 3 * (k[K - 1] - k[j]) / denom
        t3 = np.maximum(x - k[K - 1], 0) ** 3 * (k[K - 2] - k[j]) / denom
        cols.append(t1 - t2 + t3)
    return np.column_stack(cols)


# ---- Phase 5 comparison per universe ----
def phase5_metrics_for_universe(con, universe_label, gm_view, sev_view, ro_view, pop_view,
                                mu, sigma_e_fixed=None):
    """
    Compute Var(adj), sigma_e (re-estimated), sigma_alpha, lambda, SE table,
    and held-out even/odd adj_odd prediction.
    Uses its own con view names passed in (gm_view etc are view names or SQL subqueries).
    For n100 universe, gm_view is filtered view; ro_view similarly filtered via join.
    Returns dict.
    """
    # sigma_e: variance of r - adj_mean - delta
    var_resid = con.execute(f"""
        SELECT VAR_SAMP(r.rating - g.adj_mean - s.delta_full)
        FROM {ro_view} r
        JOIN {gm_view} g USING (game_id)
        JOIN {sev_view} s USING (user_pseudouserid)
    """).fetchone()[0]
    sigma_e2 = float(var_resid)
    sigma_e = float(np.sqrt(sigma_e2))
    var_adj, mean_adj = con.execute(f"SELECT VAR_SAMP(adj_mean), AVG(adj_mean) FROM {gm_view}").fetchone()
    var_adj = float(var_adj)
    mean_inv_n = float(con.execute(f"SELECT AVG(1.0/n_obs) FROM {gm_view}").fetchone()[0])
    harm_n = float(1 / mean_inv_n) if mean_inv_n else None
    sigma_alpha2_mm = var_adj - sigma_e2 * mean_inv_n
    sigma_alpha2_mm = float(max(sigma_alpha2_mm, 1e-6))
    lambda_mm = float(sigma_e2 / sigma_alpha2_mm)
    # cov method
    cov_row = con.execute(f"""
        WITH half AS (
          SELECT game_id, (rating_observation_id % 2) AS parity,
                 AVG(r.rating - s.delta_full) AS half_adj
          FROM {ro_view} r JOIN {sev_view} s USING (user_pseudouserid)
          GROUP BY game_id, parity
        ),
        piv AS (
          SELECT game_id,
                 MAX(CASE WHEN parity=0 THEN half_adj END) even_adj,
                 MAX(CASE WHEN parity=1 THEN half_adj END) odd_adj
          FROM half GROUP BY game_id HAVING COUNT(*)=2
        )
        SELECT COVAR_SAMP(even_adj, odd_adj), COUNT(*) FROM piv
    """).fetchone()
    sigma_alpha2_cov = float(cov_row[0]) if cov_row[0] else None
    lambda_cov = float(sigma_e2 / sigma_alpha2_cov) if sigma_alpha2_cov else None

    n_games = int(con.execute(f"SELECT COUNT(*) FROM {gm_view}").fetchone()[0])
    # n distribution
    dist = con.execute(f"""
        SELECT AVG(n_obs), MEDIAN(n_obs), QUANTILE_CONT(n_obs,0.10),
               QUANTILE_CONT(n_obs,0.25), QUANTILE_CONT(n_obs,0.75),
               QUANTILE_CONT(n_obs,0.90), MIN(n_obs), MAX(n_obs)
        FROM {gm_view}
    """).fetchone()
    se_quant = con.execute(f"""
        WITH s AS (SELECT n_obs, {sigma_e}/SQRT(n_obs::DOUBLE) AS se FROM {gm_view})
        SELECT QUANTILE_CONT(se,0.10), QUANTILE_CONT(se,0.50), QUANTILE_CONT(se,0.90) FROM s
    """).fetchone()

    # held-out: even/odd prediction of adj_odd (same as phase5)
    # need mu for shrunk; use passed mu (7.144) fixed
    mu_val = float(mu)
    lambda_val = float(lambda_mm)
    # Build joined held-out pivot via SQL
    held = con.execute(f"""
        WITH half_raw AS (
            SELECT game_id, (rating_observation_id % 2) AS parity,
                   AVG(rating) AS raw_half, COUNT(*) n_half FROM {ro_view} GROUP BY game_id, parity
        ),
        half_adj AS (
            SELECT game_id, (rating_observation_id % 2) AS parity,
                   AVG(r.rating - s.delta_full) AS adj_half, COUNT(*) n_half
            FROM {ro_view} r JOIN {sev_view} s USING (user_pseudouserid)
            GROUP BY game_id, parity
        ),
        piv AS (
            SELECT game_id,
                   MAX(CASE WHEN parity=0 THEN raw_half END) raw_even,
                   MAX(CASE WHEN parity=1 THEN raw_half END) raw_odd,
                   MAX(CASE WHEN parity=0 THEN adj_half END) adj_even,
                   MAX(CASE WHEN parity=1 THEN adj_half END) adj_odd,
                   MAX(CASE WHEN parity=0 THEN n_half END) n_even,
                   MAX(CASE WHEN parity=1 THEN n_half END) n_odd
            FROM (SELECT hr.game_id, hr.parity, hr.raw_half, ha.adj_half, hr.n_half
                  FROM half_raw hr JOIN half_adj ha USING (game_id, parity))
            GROUP BY game_id HAVING COUNT(*)=2
        ),
        j AS (
            SELECT p.*, pop.bayes_rating AS bayes,
                   ({mu_val}*{lambda_val} + p.n_even * p.adj_even)/(p.n_even + {lambda_val}) AS shrunk_even
            FROM piv p JOIN {pop_view} pop USING (game_id)
        )
        SELECT COUNT(*) n,
               CORR(adj_even, adj_odd) corr_adj,
               CORR(raw_even, adj_odd) corr_raw_to_adj,
               CORR(shrunk_even, adj_odd) corr_shrunk,
               CORR(bayes, adj_odd) corr_bayes,
               CORR(raw_even, raw_odd) corr_raw,
               AVG(adj_even - adj_odd) bias_adj,
               AVG(shrunk_even - adj_odd) bias_shrunk,
               AVG(raw_even - adj_odd) bias_raw_to_adj,
               AVG(bayes - adj_odd) bias_bayes,
               SQRT(AVG((adj_even - adj_odd)*(adj_even - adj_odd))) rmse_adj,
               SQRT(AVG((shrunk_even - adj_odd)*(shrunk_even - adj_odd))) rmse_shrunk,
               SQRT(AVG((raw_even - adj_odd)*(raw_even - adj_odd))) rmse_raw_to_adj,
               SQRT(AVG((bayes - adj_odd)*(bayes - adj_odd))) rmse_bayes,
               VAR_SAMP(adj_odd) var_adj_odd,
               SQRT(AVG((raw_even - raw_odd)*(raw_even - raw_odd))) rmse_raw_to_raw
        FROM j
    """).fetchone()
    n_both, corr_adj, corr_raw_to_adj, corr_shrunk, corr_bayes, corr_raw, bias_adj, bias_shrunk, bias_raw_to_adj, bias_bayes, rmse_adj, rmse_shrunk, rmse_raw_to_adj, rmse_bayes, var_adj_odd, rmse_raw_to_raw = held
    def r2(rmse, var):
        return 1 - (rmse ** 2) / var if var and rmse else None
    return {
        "universe": universe_label,
        "n_games_gm": n_games,
        "n_both_halves": int(n_both) if n_both else 0,
        "var_adj": var_adj,
        "mean_adj": float(mean_adj),
        "sigma_e": sigma_e,
        "sigma_e2": sigma_e2,
        "sigma_alpha2_mm": sigma_alpha2_mm,
        "sigma_alpha_mm": float(np.sqrt(sigma_alpha2_mm)),
        "lambda_mm": lambda_mm,
        "sigma_alpha2_cov": sigma_alpha2_cov,
        "lambda_cov": lambda_cov,
        "mean_inv_n": mean_inv_n,
        "harmonic_mean_n": harm_n,
        "n_dist": {"mean": float(dist[0]), "median": float(dist[1]), "p10": float(dist[2]),
                   "p25": float(dist[3]), "p75": float(dist[4]), "p90": float(dist[5]),
                   "min": int(dist[6]), "max": int(dist[7])},
        "se_quantiles": {"p10": float(se_quant[0]), "median": float(se_quant[1]), "p90": float(se_quant[2])},
        "held_out": {
            "corr_adj_adj": float(corr_adj) if corr_adj else None,
            "corr_raw_to_adj": float(corr_raw_to_adj) if corr_raw_to_adj else None,
            "corr_shrunk_adj": float(corr_shrunk) if corr_shrunk else None,
            "corr_bayes_adj": float(corr_bayes) if corr_bayes else None,
            "corr_raw_raw": float(corr_raw) if corr_raw else None,
            "bias_adj": float(bias_adj) if bias_adj else None,
            "bias_shrunk": float(bias_shrunk) if bias_shrunk else None,
            "bias_raw_to_adj": float(bias_raw_to_adj) if bias_raw_to_adj else None,
            "bias_bayes": float(bias_bayes) if bias_bayes else None,
            "rmse_adj": float(rmse_adj) if rmse_adj else None,
            "rmse_shrunk": float(rmse_shrunk) if rmse_shrunk else None,
            "rmse_raw_to_adj": float(rmse_raw_to_adj) if rmse_raw_to_adj else None,
            "rmse_bayes": float(rmse_bayes) if rmse_bayes else None,
            "rmse_raw_to_raw": float(rmse_raw_to_raw) if rmse_raw_to_raw else None,
            "var_adj_odd": float(var_adj_odd) if var_adj_odd else None,
            "r2_adj": r2(rmse_adj, var_adj_odd),
            "r2_shrunk": r2(rmse_shrunk, var_adj_odd),
            "r2_raw_to_adj": r2(rmse_raw_to_adj, var_adj_odd),
            "r2_bayes": r2(rmse_bayes, var_adj_odd),
        },
    }


def build_estimation_sample_from_gam(gam_df: pd.DataFrame, pop: pd.DataFrame, links_path: Path):
    """Replicate Phase 6 estimation sample logic exactly."""
    links = pd.read_parquet(links_path)
    n_impl = (links[links["rel"] == "reimplementation"].groupby("game_id").size()
              .rename("n_implementations").reset_index())
    est = gam_df.merge(pop, on="game_id", how="left")
    est = est.merge(n_impl, on="game_id", how="left")
    est["n_implementations"] = est["n_implementations"].fillna(0).astype(float)
    est["log_n_active"] = np.log10(est["n_obs"])
    est["year_c"] = est["year"] - 2015
    est["weight_c"] = est["weight"] - est["weight"].median()
    est["log_playtime_c"] = (np.log1p(est["playing_time"]) - np.log1p(est["playing_time"]).median())
    est["min_players_c"] = est["min_players"] - est["min_players"].median()
    est["log_max_players_c"] = (np.log1p(est["max_players"]) - np.log1p(est["max_players"]).median())
    est["is_reimpl_num"] = est["is_reimplementation"].astype(float)
    est["log_n_impl_c"] = (np.log1p(est["n_implementations"]) - np.log1p(est["n_implementations"]).median())
    est["vol_band"] = pd.cut(est["n_obs"], bins=VOL_BAND_EDGES, labels=VOL_BAND_LABELS, right=False)
    est["decade"] = ((est["year"] // 10) * 10).astype(int).astype(str) + "s"

    def parse_list(v):
        try:
            p = json.loads(v) if isinstance(v, str) else []
            return [str(x) for x in p] if isinstance(p, list) else []
        except Exception:
            return []
    est["category_list"] = est["categories"].map(parse_list)
    est["mechanic_list"] = est["mechanics"].map(parse_list)
    need = ["adj_mean", "n_obs", "avg_rating_current", "log_n_active", "year", "weight",
            "playing_time", "min_players", "max_players", "is_reimpl_num",
            "log_n_impl_c", "vol_band", "decade"]
    before = len(est)
    est = est.dropna(subset=need).reset_index(drop=True)
    return est, before - len(est)


def add_group_flags(est, list_col, prefix, min_count=TAG_MIN_COUNT):
    counts = Counter(t for tags in est[list_col] for t in tags)
    tags = sorted(t for t, c in counts.items() if c >= min_count)
    cols = []
    for t in tags:
        col = f"{prefix}_{t}"
        est[col] = est[list_col].map(lambda v: float(t in v))
        cols.append(col)
    return cols


def add_dummies(est, source_col, prefix):
    dummy = pd.get_dummies(est[source_col], prefix=prefix, dtype=float)
    names = sorted(dummy.columns)[1:]  # omit first against intercept
    for name in names:
        est[name] = dummy[name]
    return names


def fit_phase6_for_universe(est: pd.DataFrame, mu, sigma_e, sigma_a2, label: str):
    """Fit Phase 6 specs (same as 31) on given est; return results, resid_store, betas."""
    cat_cols = add_group_flags(est, "category_list", "cat")
    mech_cols = add_group_flags(est, "mechanic_list", "mech")
    band_cols = add_dummies(est, "vol_band", "volband")
    dec_cols = add_dummies(est, "decade", "decade")
    knots_year = np.quantile(est["year"].to_numpy(float), [0.05, 0.35, 0.65, 0.95])
    nsy = ns_basis(est["year"].to_numpy(float), knots_year)
    ns_year_cols = []
    for i in range(nsy.shape[1]):
        c = f"ns_year_{i}"
        est[c] = nsy[:, i]
        ns_year_cols.append(c)
    core = ["log_n_active", "weight_c", "log_playtime_c", "min_players_c",
            "log_max_players_c", "is_reimpl_num", "log_n_impl_c"]
    specs = {
        "Q0_linear": ["log_n_active", "year_c"],
        "Q0_flex_year": ["log_n_active"] + ns_year_cols,
        "Q0_flex_bands": band_cols + dec_cols,
        "Q1_core": ["log_n_active"] + ns_year_cols + ["weight_c"],
        "Q2_structure": core[:1] + ns_year_cols + core[1:],
        "Q3_categories": core[:1] + ns_year_cols + core[1:] + cat_cols,
        "Q3b_flex_volume": band_cols + ns_year_cols + core[1:] + cat_cols,
        "Q4_mechanics": core[:1] + ns_year_cols + core[1:] + cat_cols + mech_cols,
    }
    y_adj = est["adj_mean"].to_numpy(float)
    n_obs = est["n_obs"].to_numpy(float)
    log_n = est["log_n_active"].to_numpy(float)
    weightings = {
        "ols": np.ones(len(est)),
        "wls_n": n_obs.copy(),
        "gls_eff": 1.0 / (sigma_a2 + sigma_e ** 2 / n_obs),
    }
    designs = {name: np.column_stack([np.ones(len(est))] + [est[c].to_numpy(float) for c in cols])
               for name, cols in specs.items()}
    col_names = {name: ["intercept"] + cols for name, cols in specs.items()}
    results = []
    resid_store = {}
    for spec_name, X in designs.items():
        cn = col_names[spec_name]
        for wt_name, w in [("ols", weightings["ols"]), ("wls_n", weightings["wls_n"])]:
            beta, pred, resid = fit_wls(X, y_adj, w)
            cv_pred, cv_resid, fold_betas, fold_idx = cv_predictions(X, y_adj, w)
            m_in = metrics(y_adj, resid)
            fold_stats = [metrics(y_adj[ix], cv_resid[ix]) for ix in fold_idx]
            fold_r2 = [f["r2"] for f in fold_stats]
            fold_rmse = [f["rmse"] for f in fold_stats]
            bi = dict(zip(cn, beta))
            vi = cn.index("log_n_active") if "log_n_active" in cn else None
            band_means = (pd.DataFrame({"b": est["vol_band"].astype(str).to_numpy(), "r": resid})
                          .groupby("b").r.mean())
            # handle case where vol_band may not have 1-99 for n100 universe
            band_flat = float(band_means.abs().max()) if len(band_means) else float("nan")
            row = {
                "spec": spec_name, "weighting": wt_name, "target": "adj",
                "n_games": int(len(y_adj)), "n_features": int(X.shape[1]),
                "r2_in": m_in["r2"], "rmse_in": m_in["rmse"], "mae_in": m_in["mae"],
                "cv_r2_mean": float(np.mean(fold_r2)), "cv_r2_sd": float(np.std(fold_r2)),
                "cv_rmse_mean": float(np.mean(fold_rmse)), "cv_rmse_sd": float(np.std(fold_rmse)),
                "beta_logn": bi.get("log_n_active"),
                "beta_logn_fold_sd": float(np.std(fold_betas[:, vi])) if vi is not None else None,
                "beta_weight": bi.get("weight_c"),
                "beta_weight_fold_sd": (float(np.std(fold_betas[:, cn.index("weight_c")])) if "weight_c" in cn else None),
                "corr_resid_logn": float(np.corrcoef(resid, log_n)[0, 1]) if len(resid) > 1 else float("nan"),
                "corr_cvresid_logn": float(np.corrcoef(cv_resid, log_n)[0, 1]),
                "spearman_resid_logn": float(pd.Series(resid).corr(pd.Series(log_n), method="spearman")),
                "max_abs_bandmean_resid": band_flat,
            }
            results.append(row)
            key = f"{spec_name}|{wt_name}|adj"
            resid_store[key] = {"resid": resid, "cv_resid": cv_resid, "pred": pred, "beta": beta}
        if spec_name in {"Q0_flex_year", "Q1_core", "Q3_categories"}:
            # also gls_eff for comparison (not needed for main comparison but for completeness)
            w = weightings["gls_eff"]
            beta, pred, resid = fit_wls(X, y_adj, w)
            cv_pred, cv_resid, fold_betas, fold_idx = cv_predictions(X, y_adj, w)
            m_in = metrics(y_adj, resid)
            fold_stats = [metrics(y_adj[ix], cv_resid[ix]) for ix in fold_idx]
            row = {
                "spec": spec_name, "weighting": "gls_eff", "target": "adj",
                "n_games": int(len(y_adj)), "n_features": int(X.shape[1]),
                "r2_in": m_in["r2"], "rmse_in": m_in["rmse"], "mae_in": m_in["mae"],
                "cv_r2_mean": float(np.mean([f["r2"] for f in fold_stats])),
                "cv_r2_sd": float(np.std([f["r2"] for f in fold_stats])),
                "cv_rmse_mean": float(np.mean([f["rmse"] for f in fold_stats])),
                "cv_rmse_sd": float(np.std([f["rmse"] for f in fold_stats])),
                "beta_logn": dict(zip(cn, beta)).get("log_n_active"),
                "beta_logn_fold_sd": None,
                "beta_weight": dict(zip(cn, beta)).get("weight_c"),
                "beta_weight_fold_sd": None,
                "corr_resid_logn": float(np.corrcoef(resid, log_n)[0, 1]),
                "corr_cvresid_logn": float(np.corrcoef(cv_resid, log_n)[0, 1]),
                "spearman_resid_logn": float(pd.Series(resid).corr(pd.Series(log_n), method="spearman")),
                "max_abs_bandmean_resid": float(pd.DataFrame({"b": est["vol_band"].astype(str).to_numpy(), "r": resid}).groupby("b").r.mean().abs().max()),
            }
            results.append(row)
            resid_store[f"{spec_name}|gls_eff|adj"] = {"resid": resid, "cv_resid": cv_resid, "pred": pred, "beta": beta}
    # Also keep col_names and designs for residual generation per pref spec
    return pd.DataFrame(results), resid_store, designs, col_names, specs, est, cat_cols, mech_cols, band_cols, dec_cols, ns_year_cols


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--active-dir", type=Path, default=REPO / "scratch/phase2-active")
    ap.add_argument("--population", type=Path, default=REPO / "scratch/phase2-active/bgg_research_population.parquet")
    ap.add_argument("--out-dir", type=Path, default=REPO / "reports/sensitivity_n100_games")
    ap.add_argument("--json-out", type=Path, default=REPO / "docs/phase6-intermediate/sensitivity_n100.json")
    args = ap.parse_args()

    print("Sensitivity n>=100 games: active vs filtered-games comparison")
    print(f" active-dir={args.active_dir} population={args.population} out-dir={args.out_dir}")
    ensure_scratch_copy(args.active_dir)
    mu, sigma_e_fixed, sigma_e2_fixed, sigma_a2_fixed, phase5_json = load_phase5_params()
    print(f" Phase5 primary params: mu={mu:.4f} sigma_e={sigma_e_fixed:.4f} sigma_alpha2={sigma_a2_fixed:.4f} lambda={sigma_e2_fixed/sigma_a2_fixed:.2f}")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = REPO / "scratch/ducktmp"
    con = duckdb.connect()
    configure(con, tmp_dir)

    # Resolve parquet paths
    ro_path = args.active_dir / "rating_observations_active.parquet"
    sev_path = args.active_dir / "user_severity_active.parquet"
    gm_path = args.active_dir / "game_adjusted_means_active.parquet"
    pop_path = args.population
    if not ro_path.exists() or not sev_path.exists() or not gm_path.exists():
        sys.exit(f"missing active files in {args.active_dir}")
    if not pop_path.exists():
        sys.exit(f"population not found {pop_path}")

    # Register views
    con.execute(f"CREATE OR REPLACE VIEW ro_full AS SELECT * FROM read_parquet('{qpath(ro_path)}')")
    con.execute(f"CREATE OR REPLACE VIEW sev AS SELECT * FROM read_parquet('{qpath(sev_path)}')")
    con.execute(f"CREATE OR REPLACE VIEW gm_full AS SELECT * FROM read_parquet('{qpath(gm_path)}')")
    con.execute(f"CREATE OR REPLACE VIEW pop AS SELECT * FROM read_parquet('{qpath(pop_path)}')")
    # n100 game list via SEMI JOIN on gm_full where n_obs>=100
    con.execute("CREATE OR REPLACE VIEW gm_n100 AS SELECT * FROM gm_full WHERE n_obs >= 100")
    # For observation-level metrics, filter ro to n100 games via semi-join on game_id
    con.execute("CREATE OR REPLACE VIEW ro_n100 AS SELECT r.* FROM ro_full r SEMI JOIN gm_n100 g USING (game_id)")
    # sanity counts
    cnt_full = con.execute("SELECT COUNT(*) FROM gm_full").fetchone()[0]
    cnt_n100 = con.execute("SELECT COUNT(*) FROM gm_n100").fetchone()[0]
    cnt_ro_full = con.execute("SELECT COUNT(*) FROM ro_full").fetchone()[0]
    cnt_ro_n100 = con.execute("SELECT COUNT(*) FROM ro_n100").fetchone()[0]
    print(f" Games: full active GM {cnt_full} (with ratings in parquet), n100 {cnt_n100}, excluded 1-99 = {cnt_full - cnt_n100}")
    print(f" Obs: full {cnt_ro_full:,} n100 {cnt_ro_n100:,} retained {cnt_ro_n100/cnt_ro_full:.3%}, removed {cnt_ro_full-cnt_ro_n100:,}")

    # ---------- Phase 5 per universe ----------
    print("\n=== Phase 5 comparison (full active vs n>=100) ===")
    p5_full = phase5_metrics_for_universe(con, "active_all", "gm_full", "sev", "ro_full", "pop", mu, sigma_e_fixed)
    p5_n100 = phase5_metrics_for_universe(con, "n_active>=100", "gm_n100", "sev", "ro_n100", "pop", mu, sigma_e_fixed)
    for k in ["var_adj", "sigma_e", "sigma_alpha2_mm", "lambda_mm", "sigma_alpha2_cov", "lambda_cov"]:
        print(f"  {k:22s} active {p5_full[k]:.6f}  n100 {p5_n100[k]:.6f}  delta {(p5_n100[k]-p5_full[k]):+.6f}  pct {(p5_n100[k]/p5_full[k]-1)*100:+.2f}%")
    print(f"  n_games {p5_full['n_games_gm']} -> {p5_n100['n_games_gm']}")
    print(f"  n_both_halves {p5_full['n_both_halves']} -> {p5_n100['n_both_halves']}")
    print(f"  held_out rmse_adj {p5_full['held_out']['rmse_adj']:.4f} -> {p5_n100['held_out']['rmse_adj']:.4f}  r2 {p5_full['held_out']['r2_adj']:.4f}->{p5_n100['held_out']['r2_adj']:.4f}")
    print(f"           rmse_shrunk {p5_full['held_out']['rmse_shrunk']:.4f}->{p5_n100['held_out']['rmse_shrunk']:.4f}")
    print(f"           rmse_raw_to_adj {p5_full['held_out']['rmse_raw_to_adj']:.4f}->{p5_n100['held_out']['rmse_raw_to_adj']:.4f}")
    print(f"           r2_raw_to_adj {p5_full['held_out']['r2_raw_to_adj']:.4f}->{p5_n100['held_out']['r2_raw_to_adj']:.4f}")

    # ---------- Phase 6 per universe ----------
    print("\n=== Phase 6 fitting (active vs n100) ===")
    # Need game-level tables with metadata: use pandas for population join
    gam_full_df = pd.read_parquet(gm_path)
    pop_df = pd.read_parquet(pop_path)
    links_path = REPO / "data/processed/phase2-filtered/game_links_filtered.parquet"
    # Full active estimation sample (replicating 31)
    est_full, dropped_full = build_estimation_sample_from_gam(gam_full_df, pop_df, links_path)
    print(f"  est_full: {len(est_full)} games (dropped {dropped_full} for nulls)")
    # n100 filtered gam then same pipeline
    gam_n100_df = gam_full_df[gam_full_df["n_obs"] >= 100].reset_index(drop=True)
    est_n100, dropped_n100 = build_estimation_sample_from_gam(gam_n100_df, pop_df, links_path)
    print(f"  est_n100: {len(est_n100)} games (dropped {dropped_n100})  diff {len(est_full)-len(est_n100)}")
    # Fit separately with appropriate variance components? For sensitivity,
    # re-estimate variance components per universe for gls_eff, but also show OLS which doesn't need them.
    # For OLS comparison, sigma not used. For completeness, use universe-specific sigma for its own gls_eff.
    # Main comparison uses OLS (preferred) -> no dependence. For lambda we report both.
    res_full, store_full, designs_full, cn_full, specs_full, est_full_ret, cat_full, mech_full, band_full, dec_full, ns_full = \
        fit_phase6_for_universe(est_full.copy(), mu, p5_full["sigma_e"], p5_full["sigma_alpha2_mm"], "active_all")
    res_n100, store_n100, designs_n100, cn_n100, specs_n100, est_n100_ret, cat_n100, mech_n100, band_n100, dec_n100, ns_n100 = \
        fit_phase6_for_universe(est_n100.copy(), mu, p5_n100["sigma_e"], p5_n100["sigma_alpha2_mm"], "n100")

    # Note: fit_phase6_for_universe mutates est copies with added columns; keep original game_ids
    # For residual distribution/overlap we need preferred Q3b/OLS residuals on comparable game sets
    # Q3b has no log_n coefficient but weight matters; compare those between universes
    pref_spec, pref_wt = "Q3b_flex_volume", "ols"
    # Extract residuals for pref
    resid_full_pref = store_full[f"{pref_spec}|{pref_wt}|adj"]["resid"]
    pred_full_pref = store_full[f"{pref_spec}|{pref_wt}|adj"]["pred"]
    resid_n100_pref = store_n100[f"{pref_spec}|{pref_wt}|adj"]["resid"]
    pred_n100_pref = store_n100[f"{pref_spec}|{pref_wt}|adj"]["pred"]
    # Align by game_id for overlapping games
    merged_resid = pd.DataFrame({"game_id": est_full_ret["game_id"], "resid_full": resid_full_pref, "n_obs_full": est_full_ret["n_obs"].to_numpy()})
    merged_n100 = pd.DataFrame({"game_id": est_n100_ret["game_id"], "resid_n100": resid_n100_pref, "pred_n100": pred_n100_pref})
    # For diagnostic: correlation on overlap only (n100 games)
    overlap = merged_resid.merge(merged_n100, on="game_id", how="inner")
    # overlap should be est_n100 size
    spearman_overlap = float(pd.Series(overlap["resid_full"]).corr(pd.Series(overlap["resid_n100"]), method="spearman"))
    pearson_overlap = float(np.corrcoef(overlap["resid_full"], overlap["resid_n100"])[0, 1])
    # Top-k Jaccard on overlap vs on full? Primary: Jaccard on same overlapping universe ranked within that universe.
    # For interpretation: overlap set is n100 games only; jaccard describes rank stability within retained games.
    # Also compute jaccard of top-1% of full ranked within full vs top-1% of n100 ranked within n100 mapped to overlap
    def jaccard_pair(a, b, frac):
        k = max(1, int(frac * len(a)))
        sa, sb = set(np.argsort(a)[-k:]), set(np.argsort(b)[-k:])
        return len(sa & sb) / len(sa | sb) if len(sa | sb) else 0.0
    jac1_overlap, k1 = top_jaccard(overlap["resid_full"].to_numpy(), overlap["resid_n100"].to_numpy(), frac=0.01)
    jac5_overlap, k5 = top_jaccard(overlap["resid_full"].to_numpy(), overlap["resid_n100"].to_numpy(), frac=0.05)
    jac1_overlap_only_fullrank = None
    # Also top residual candidate overlap where full top includes low-n games not in overlap (by definition excluded)
    # Compute full top-1% set (in game_id) vs n100 top-1% set
    full_top_ids = set(merged_resid.sort_values("resid_full", ascending=False).head(max(1, int(0.01*len(merged_resid))))["game_id"])
    n100_top_ids = set(merged_n100.sort_values("resid_n100", ascending=False).head(max(1, int(0.01*len(merged_n100))))["game_id"])
    jacc_full_vs_n100_top1 = len(full_top_ids & n100_top_ids) / len(full_top_ids | n100_top_ids) if len(full_top_ids | n100_top_ids) else 0
    jacc_full_vs_n100_top5 = len(
        set(merged_resid.sort_values("resid_full", ascending=False).head(max(1, int(0.05*len(merged_resid))))["game_id"]) &
        set(merged_n100.sort_values("resid_n100", ascending=False).head(max(1, int(0.05*len(merged_n100))))["game_id"])
    ) / len(
        set(merged_resid.sort_values("resid_full", ascending=False).head(max(1, int(0.05*len(merged_resid))))["game_id"]) |
        set(merged_n100.sort_values("resid_n100", ascending=False).head(max(1, int(0.05*len(merged_n100))))["game_id"])
    )
    print(f"  Q3b/OLS residual pearson on overlap (n100 games) {pearson_overlap:.4f} spearman {spearman_overlap:.4f}")
    print(f"  Jaccard on overlap top1% {jac1_overlap:.3f} (k={k1}) top5% {jac5_overlap:.3f} (k={k5})")
    print(f"  Jaccard full-top vs n100-top (cross-universe sets): top1% {jacc_full_vs_n100_top1:.3f} top5% {jacc_full_vs_n100_top5:.3f}")

    # Residual distribution stats
    def resid_stats(v):
        return {
            "mean": float(np.mean(v)), "sd": float(np.std(v, ddof=1) if len(v) > 1 else 0),
            "p05": float(np.quantile(v, 0.05)), "p95": float(np.quantile(v, 0.95)),
            "p01": float(np.quantile(v, 0.01)), "p99": float(np.quantile(v, 0.99)),
            "maxabs": float(np.max(np.abs(v))),
            "min": float(np.min(v)), "max": float(np.max(v)),
            "median": float(np.median(v)),
        }
    stats_full = resid_stats(resid_full_pref)
    stats_n100 = resid_stats(resid_n100_pref)
    stats_full_overlap = resid_stats(overlap["resid_full"].to_numpy())
    print(f"  resid dist full {stats_full}")
    print(f"  resid dist n100 {stats_n100}")

    # Also check per-spec CV/OLS comparison: collect comparative rows for Q3b and Q3 etc
    def row_for(df, spec, wt):
        r = df[(df.spec == spec) & (df.weighting == wt) & (df.target == "adj")]
        return r.iloc[0].to_dict() if len(r) else None
    comps = []
    for spec in ["Q3b_flex_volume", "Q3_categories", "Q1_core", "Q0_flex_year"]:
        for wt in ["ols", "wls_n"]:
            rf = row_for(res_full, spec, wt)
            rn = row_for(res_n100, spec, wt)
            if rf and rn:
                comps.append({
                    "spec": spec, "weighting": wt,
                    "cv_r2_full": rf["cv_r2_mean"], "cv_r2_n100": rn["cv_r2_mean"],
                    "cv_r2_delta": rn["cv_r2_mean"] - rf["cv_r2_mean"],
                    "r2_in_full": rf["r2_in"], "r2_in_n100": rn["r2_in"],
                    "beta_logn_full": rf["beta_logn"], "beta_logn_n100": rn["beta_logn"],
                    "beta_logn_shift_pct": ((rn["beta_logn"] - rf["beta_logn"]) / abs(rf["beta_logn"]) * 100) if rf["beta_logn"] and not pd.isna(rf["beta_logn"]) else None,
                    "beta_weight_full": rf["beta_weight"], "beta_weight_n100": rn["beta_weight"],
                    "beta_weight_shift_pct": ((rn["beta_weight"] - rf["beta_weight"]) / abs(rf["beta_weight"]) * 100) if rf["beta_weight"] and not pd.isna(rf["beta_weight"]) else None,
                    "corr_resid_logn_full": rf["corr_resid_logn"], "corr_resid_logn_n100": rn["corr_resid_logn"],
                    "max_bandmean_full": rf["max_abs_bandmean_resid"], "max_bandmean_n100": rn["max_abs_bandmean_resid"],
                })
    comps_df = pd.DataFrame(comps)
    print(comps_df.to_string())

    # Top residual tables per universe (with metadata for report)
    # Use est returns that have title etc.
    out_full = pd.DataFrame({
        "game_id": est_full_ret["game_id"], "title": est_full_ret["title"], "year": est_full_ret["year"],
        "n_obs": est_full_ret["n_obs"].astype(int), "users_rated": est_full_ret["users_rated"],
        "raw_mean": est_full_ret["raw_mean"], "adj_mean": est_full_ret["adj_mean"],
        "se_adj": p5_full["sigma_e"] / np.sqrt(est_full_ret["n_obs"].to_numpy(float)),
        "expected": pred_full_pref, "resid": resid_full_pref,
    })
    out_n100 = pd.DataFrame({
        "game_id": est_n100_ret["game_id"], "title": est_n100_ret["title"], "year": est_n100_ret["year"],
        "n_obs": est_n100_ret["n_obs"].astype(int), "users_rated": est_n100_ret["users_rated"],
        "raw_mean": est_n100_ret["raw_mean"], "adj_mean": est_n100_ret["adj_mean"],
        "se_adj": p5_n100["sigma_e"] / np.sqrt(est_n100_ret["n_obs"].to_numpy(float)),
        "expected": pred_n100_pref, "resid": resid_n100_pref,
    })
    top20_full_pos = out_full.nlargest(20, "resid").reset_index(drop=True)
    top20_full_neg = out_full.nsmallest(20, "resid").reset_index(drop=True)
    top20_n100_pos = out_n100.nlargest(20, "resid").reset_index(drop=True)
    top20_n100_neg = out_n100.nsmallest(20, "resid").reset_index(drop=True)
    # count low-n dominance
    cnt_low_in_top_full = int((top20_full_pos["n_obs"] < 100).sum())
    cnt_low_in_top_full_top165 = int(out_full.nlargest(165, "resid")["n_obs"].lt(100).sum())  # 1% of 16549 ~165
    cnt_low_in_top_full_top5 = int(out_full.nlargest(max(1,int(0.05*len(out_full))), "resid")["n_obs"].lt(100).sum())
    # Expected low-n share in top if random ~ 1604/16549=9.7%
    print(f"  low-n (<100) in full top20 pos: {cnt_low_in_top_full}/20")
    print(f"  low-n in top1% ({max(1,int(0.01*len(out_full)))}): {cnt_low_in_top_full_top165}")
    print(f"  low-n in top5%: {cnt_low_in_top_full_top5}")

    # ---- Write outputs ----
    args.out_dir.mkdir(parents=True, exist_ok=True)
    # CSVs
    # Phase5 comparison
    p5_rows = []
    for d, lab in [(p5_full, "active_all"), (p5_n100, "n100")]:
        # flatten n_dist
        r = {"universe": lab, "n_games_gm": d["n_games_gm"], "n_both_halves": d["n_both_halves"],
             "var_adj": d["var_adj"], "mean_adj": d["mean_adj"],
             "sigma_e": d["sigma_e"], "sigma_e2": d["sigma_e2"],
             "sigma_alpha2_mm": d["sigma_alpha2_mm"], "lambda_mm": d["lambda_mm"],
             "sigma_alpha2_cov": d["sigma_alpha2_cov"], "lambda_cov": d["lambda_cov"],
             "mean_inv_n": d["mean_inv_n"], "harmonic_mean_n": d["harmonic_mean_n"],
             "mean_n": d["n_dist"]["mean"], "median_n": d["n_dist"]["median"],
             "p10_n": d["n_dist"]["p10"], "p90_n": d["n_dist"]["p90"],
             "se_p10": d["se_quantiles"]["p10"], "se_median": d["se_quantiles"]["median"], "se_p90": d["se_quantiles"]["p90"],
             "corr_adj": d["held_out"]["corr_adj_adj"], "corr_shrunk": d["held_out"]["corr_shrunk_adj"],
             "corr_raw_to_adj": d["held_out"]["corr_raw_to_adj"],
             "rmse_adj": d["held_out"]["rmse_adj"], "rmse_shrunk": d["held_out"]["rmse_shrunk"],
             "rmse_raw_to_adj": d["held_out"]["rmse_raw_to_adj"], "rmse_bayes": d["held_out"]["rmse_bayes"],
             "r2_adj": d["held_out"]["r2_adj"], "r2_shrunk": d["held_out"]["r2_shrunk"],
             "r2_raw_to_adj": d["held_out"]["r2_raw_to_adj"], "var_adj_odd": d["held_out"]["var_adj_odd"],
             }
        p5_rows.append(r)
    p5_df = pd.DataFrame(p5_rows)
    p5_df.to_csv(args.out_dir / "phase5_comparison_active_vs_n100.csv", index=False)
    # Phase6 comparative
    res_full.to_csv(args.out_dir / "phase6_comparative_active.csv", index=False)
    res_n100.to_csv(args.out_dir / "phase6_comparative_n100.csv", index=False)
    comps_df.to_csv(args.out_dir / "phase6_beta_cv_comparison.csv", index=False)
    # Residual dist
    pd.DataFrame([{"universe": "active_all Q3b/OLS", **stats_full},
                  {"universe": "n100 Q3b/OLS", **stats_n100},
                  {"universe": "active_all Q3b/OLS (overlap n100 games)", **stats_full_overlap}]).to_csv(
        args.out_dir / "residual_distribution.csv", index=False)
    # Overlap metrics
    overlap_metrics = {
        "pref_spec": pref_spec, "weighting": pref_wt,
        "n_full_est": int(len(est_full_ret)), "n_n100_est": int(len(est_n100_ret)),
        "n_overlap": int(len(overlap)),
        "pearson_resid_overlap": pearson_overlap,
        "spearman_resid_overlap": spearman_overlap,
        "jaccard_top1_on_overlap": jac1_overlap, "k_top1": k1,
        "jaccard_top5_on_overlap": jac5_overlap, "k_top5": k5,
        "jaccard_full_top1_vs_n100_top1_cross": jacc_full_vs_n100_top1,
        "jaccard_full_top5_vs_n100_top5_cross": jacc_full_vs_n100_top5,
        "n_1_99_in_full_gm": int(cnt_full - cnt_n100),
        "n_1_99_in_est_full": int(len(est_full_ret) - len(est_n100_ret)),
        "low_n_in_top20_full": cnt_low_in_top_full,
        "low_n_in_top1pct_full": cnt_low_in_top_full_top165,
        "low_n_in_top5pct_full": cnt_low_in_top_full_top5,
        "low_n_share_full_gm_pct": (cnt_full - cnt_n100)/cnt_full*100,
        "low_n_share_est_pct": (len(est_full_ret)-len(est_n100_ret))/len(est_full_ret)*100,
    }
    # Also per-spec residual stability on overlap for other specs
    spec_stability = []
    for spec in specs_full.keys():
        for wt in ["ols", "wls_n"]:
            kf = f"{spec}|{wt}|adj"
            if kf in store_full and kf in store_n100:
                # need aligned overlap residuals: store_full is on est_full order, store_n100 on est_n100 order
                # align via merge
                df_f = pd.DataFrame({"game_id": est_full_ret["game_id"], "r_f": store_full[kf]["resid"]})
                df_n = pd.DataFrame({"game_id": est_n100_ret["game_id"], "r_n": store_n100[kf]["resid"]})
                ov = df_f.merge(df_n, on="game_id", how="inner")
                if len(ov) > 10:
                    pear = float(np.corrcoef(ov["r_f"], ov["r_n"])[0, 1])
                    spear = float(pd.Series(ov["r_f"]).corr(pd.Series(ov["r_n"]), method="spearman"))
                    jac, _ = top_jaccard(ov["r_f"].to_numpy(), ov["r_n"].to_numpy(), frac=0.01)
                    spec_stability.append({"spec": spec, "weighting": wt, "pearson_overlap": pear, "spearman_overlap": spear, "jaccard_top1_overlap": jac})
    pd.DataFrame(spec_stability).to_csv(args.out_dir / "residual_stability_by_spec.csv", index=False)

    # Top residuals
    top20_full_pos.to_csv(args.out_dir / "top20_positive_active.csv", index=False)
    top20_full_neg.to_csv(args.out_dir / "top20_negative_active.csv", index=False)
    top20_n100_pos.to_csv(args.out_dir / "top20_positive_n100.csv", index=False)
    top20_n100_neg.to_csv(args.out_dir / "top20_negative_n100.csv", index=False)

    # shrinkage table per universe
    def shrink_table(lmb):
        rows = []
        for n in [20, 50, 100, 120, 293, 500, 1000, 2795, 5000, 12000]:
            w = n/(n+lmb)
            rows.append({"n": n, "w": w, "shrink_to_prior": 1-w})
        return pd.DataFrame(rows)
    shrink_table(p5_full["lambda_mm"]).to_csv(args.out_dir / "shrinkage_active.csv", index=False)
    shrink_table(p5_n100["lambda_mm"]).to_csv(args.out_dir / "shrinkage_n100.csv", index=False)

    # JSON summary
    json_summary = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "scope": "sensitivity active (16,564 games, n>=1) vs n_active>=100 games (1-99 bucket 1,612 excluded, 9.7% of active; P10=100 threshold). Users fixed >=10 minus degenerate_strict. Single-filter, not recursive closure.",
        "counts": {
            "games_gm_active": int(cnt_full), "games_gm_n100": int(cnt_n100),
            "games_excluded_1_99": int(cnt_full - cnt_n100),
            "obs_ro_active": int(cnt_ro_full), "obs_ro_n100": int(cnt_ro_n100),
            "est_active": int(len(est_full_ret)), "est_n100": int(len(est_n100_ret)),
            "est_excluded_1_99_in_est": int(len(est_full_ret)-len(est_n100_ret)),
        },
        "phase5": {"active_all": p5_full, "n100": p5_n100,
                   "deltas": {
                       "var_adj_delta": p5_n100["var_adj"] - p5_full["var_adj"],
                       "var_adj_pct": (p5_n100["var_adj"]/p5_full["var_adj"]-1)*100,
                       "sigma_e_delta": p5_n100["sigma_e"] - p5_full["sigma_e"],
                       "sigma_e_pct": (p5_n100["sigma_e"]/p5_full["sigma_e"]-1)*100,
                       "lambda_delta": p5_n100["lambda_mm"] - p5_full["lambda_mm"],
                       "lambda_pct": (p5_n100["lambda_mm"]/p5_full["lambda_mm"]-1)*100,
                       "rmse_adj_delta": p5_n100["held_out"]["rmse_adj"] - p5_full["held_out"]["rmse_adj"],
                       "r2_adj_delta": p5_n100["held_out"]["r2_adj"] - p5_full["held_out"]["r2_adj"],
                   }},
        "phase6": {
            "beta_cv_table": comps_df.to_dict(orient="records"),
            "full_comparative": res_full.to_dict(orient="records"),
            "n100_comparative": res_n100.to_dict(orient="records"),
            "residual_distribution": {"active_all": stats_full, "n100": stats_n100},
            "residual_stability_overlap": {"pearson": pearson_overlap, "spearman": spearman_overlap,
                                           "jaccard_top1_overlap": jac1_overlap, "jaccard_top5_overlap": jac5_overlap,
                                           "jaccard_full_vs_n100_top1_cross": jacc_full_vs_n100_top1,
                                           "jaccard_full_vs_n100_top5_cross": jacc_full_vs_n100_top5},
            "spec_stability": spec_stability,
        },
        "overlap": overlap_metrics,
        "top_residuals": {
            "active_top20_pos": top20_full_pos.to_dict(orient="records"),
            "active_top20_neg": top20_full_neg.to_dict(orient="records"),
            "n100_top20_pos": top20_n100_pos.to_dict(orient="records"),
            "n100_top20_neg": top20_n100_neg.to_dict(orient="records"),
        },
        "claim_tags": {
            "counts_n": "observed fact",
            "var_sigma_lambda_rmse_r2_cv": "empirical finding (estimated variance components / held-out metrics)",
            "residual_stats_correlations": "empirical finding",
            "decision_cases": "model-dependent conclusion / empirical finding comparison",
        },
        "method": "copy-once to scratch/phase2-active; DuckDB SEMI JOIN on n_obs>=100 game list; 4GB/threads3; no full-snapshot rescan; one grouped even/odd pass reused; OLS/WLS as in 31; 5-fold CV deterministic perm 20260824",
    }
    # write json to docs intermediate and reports
    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json_out).write_text(json.dumps(json_summary, indent=2))
    (args.out_dir / "sensitivity_n100_summary.json").write_text(json.dumps(json_summary, indent=2))
    print(f"\nWrote JSON summary to {args.json_out} and {args.out_dir / 'sensitivity_n100_summary.json'}")
    print(f"Wrote CSVs to {args.out_dir}")

    con.close()


if __name__ == "__main__":
    main()

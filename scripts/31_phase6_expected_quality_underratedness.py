"""Phase 6 — expected-quality model and operational underratedness residual.

Dependent variable: Phase 5 primary quality estimand
    adj_mean_g = AVG(rating - delta_u)  (active ALS, mu = 7.144)
with explicit game-level uncertainty SE_g = sigma_e / sqrt(n_g), sigma_e = 1.194
(scripts/26, scripts/30; data/processed/phase2-active/game_adjusted_means_active.parquet).
A 120-rating game (SE .109) and a 12,000-rating game (SE .011) differ by an order
of magnitude in precision; equal-game OLS ignores this.

Part A (steer diagnostic, recorded independently of the model below):
    Re-estimate the rating-volume relationship on the active population under BOTH
    targets, E[raw | volume] and E[adj_quality | volume], quantify how much of the
    original volume-rating gradient remains after severity adjustment, and classify
    among: (a) largely disappears, (b) reduced but remains, (c) unchanged or grows.
    Includes an even/odd rating split as a cheap stability check.

Part B (main):
    Transparent OLS/WLS expected-quality specifications E[adj_mean | characteristics],
    equal-game vs precision-weighted head-to-head:
      - nested specs: volume+year (linear / flexible / banded) -> + weight ->
        + playtime/players/reimplementation -> + category flags -> + mechanic flags
      - weightings: OLS w=1; WLS w_g = n_g (= 1/SE^2 up to the constant sigma_e^2);
        exploratory efficiency weights 1/(sigma_alpha^2 + SE_g^2)
      - 5-fold CV R^2/RMSE predicting adj_mean (unweighted metrics throughout so
        weightings stay comparable), fold coefficient spread, residual stability
        across specs (corr, top-1% Jaccard), corr(residual, log n),
        low-n residual stability via the even/odd halves, adj vs raw target contrast.

underratedness_g = adj_mean_g - expected_quality_g is an operational,
model-dependent residual: not latent quality, not broad appeal, not a final ranking.

Reproduce:
    python scripts/31_phase6_expected_quality_underratedness.py \
        --active-dir scratch/phase2-active \
        --population scratch/phase2-active/bgg_research_population.parquet \
        --out-dir data/processed/phase2-active

Bounded: no sqlite scans; observation-level access is one grouped even/odd
aggregate pass over rating_observations_active.parquet under DuckDB
memory_limit=4GB threads=3 temp_directory=scratch/ducktmp (pattern from scripts/30).
Everything else operates on compact game-level tables.
"""
import argparse
import json
import shutil
from collections import Counter
from pathlib import Path

import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
MEMORY = "4GB"
THREADS = 3
RANDOM_SEED = 20260824
N_FOLDS = 5
TAG_MIN_COUNT = 500
TOP_FRACTION = 0.01
VOL_BAND_EDGES = [0, 100, 200, 500, 1000, 2500, 5000, 10000, 25000, np.inf]
VOL_BAND_LABELS = ["1-99", "100-199", "200-499", "500-999", "1k-2.5k", "2.5k-5k",
                   "5k-10k", "10k-25k", "25k+"]


# ---------------------------------------------------------------------------
# infrastructure
# ---------------------------------------------------------------------------
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
              "rating_observations_active.parquet"]
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
    candidates = [
        REPO / "data/processed/phase2-active/phase5_quality_estimator.json",
        REPO / "docs/phase2-active/phase5_quality_comparison.json",
    ]
    for p in candidates:
        if p.exists():
            j = json.loads(p.read_text())
            evc = j.get("eb_variance_components", {})
            mu = j.get("validation", {}).get("mu_active")
            sigma_e = evc.get("sigma_e_sd")
            sigma_a2 = evc.get("sigma_alpha2_mm")
            print(f"  Phase 5 params from {p.name}: mu={mu:.4f} sigma_e={sigma_e:.4f} "
                  f"sigma_alpha={np.sqrt(sigma_a2):.4f}")
            return float(mu), float(sigma_e), float(sigma_a2)
    raise SystemExit("Phase 5 parameter file not found")


def even_odd_halves(con, active_dir: Path) -> pd.DataFrame:
    """One bounded grouped pass: per game x parity raw/adj half-means and counts."""
    sev = active_dir / "user_severity_active.parquet"
    obs = active_dir / "rating_observations_active.parquet"
    return con.execute(f"""
        WITH j AS (
            SELECT r.game_id,
                   (r.rating_observation_id % 2) AS parity,
                   AVG(r.rating) AS raw_half,
                   AVG(r.rating - s.delta_full) AS adj_half,
                   COUNT(*) AS n_half
            FROM read_parquet('{qpath(obs)}') r
            JOIN read_parquet('{qpath(sev)}') s USING (user_pseudouserid)
            GROUP BY 1, 2
        )
        SELECT game_id,
               MAX(CASE WHEN parity=0 THEN raw_half END) AS raw_even,
               MAX(CASE WHEN parity=1 THEN raw_half END) AS raw_odd,
               MAX(CASE WHEN parity=0 THEN adj_half END) AS adj_even,
               MAX(CASE WHEN parity=1 THEN adj_half END) AS adj_odd,
               MAX(CASE WHEN parity=0 THEN n_half END) AS n_even,
               MAX(CASE WHEN parity=1 THEN n_half END) AS n_odd
        FROM j GROUP BY game_id
    """).df()


# ---------------------------------------------------------------------------
# transparent linear modelling helpers (numpy; explicit formula)
# ---------------------------------------------------------------------------
def fit_wls(X, y, w):
    """Minimise sum_i w_i (y_i - x_i'b)^2 by row-scaling; w=1 reduces to OLS."""
    sw = np.sqrt(w)
    beta, *_ = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)
    pred = X @ beta
    return beta, pred, y - pred


def metrics(y, resid):
    sse = float(np.sum(resid ** 2))
    sst = float(np.sum((y - np.mean(y)) ** 2))
    return {"r2": 1 - sse / sst, "rmse": float(np.sqrt(np.mean(resid ** 2))),
            "mae": float(np.mean(np.abs(resid)))}


def cv_predictions(X, y, w, folds=N_FOLDS, seed=RANDOM_SEED):
    """Deterministic k-fold out-of-fold predictions; WLS fit per training fold."""
    n = len(y)
    rng = np.random.default_rng(seed)
    order = rng.permutation(n)
    pred = np.full(n, np.nan)
    betas, fold_idx = [], []
    for test_idx in np.array_split(order, folds):
        train_mask = np.ones(n, dtype=bool)
        train_mask[test_idx] = False
        beta, _, _ = fit_wls(X[train_mask], y[train_mask], w[train_mask])
        pred[test_idx] = X[test_idx] @ beta
        betas.append(beta)
        fold_idx.append(test_idx)
    return pred, y - pred, np.array(betas), fold_idx


def top_jaccard(a, b, frac=TOP_FRACTION):
    k = max(1, int(frac * len(a)))
    sa, sb = set(np.argsort(a)[-k:]), set(np.argsort(b)[-k:])
    return len(sa & sb) / len(sa | sb)


def ns_basis(x, knots):
    """Restricted (natural) cubic spline basis, Harrell form: K knots -> K columns
    (linear term + K-2 nonlinear terms)."""
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


def ols_slope(x, y):
    xc, yc = x - x.mean(), y - y.mean()
    return float(np.dot(xc, yc) / np.dot(xc, xc))


def fwl_partial_slopes(df, x_col, targets, control_cols):
    """Frisch-Waugh partial slopes of each target on x_col given controls."""
    Z = np.column_stack([np.ones(len(df))] +
                        [df[c].to_numpy(float) for c in control_cols])
    proj = lambda v: v - Z @ np.linalg.lstsq(Z, v, rcond=None)[0]
    lx = proj(df[x_col].to_numpy(float))
    return {t: ols_slope(lx, proj(df[t].to_numpy(float))) for t in targets}


# ---------------------------------------------------------------------------
# Part A — steer diagnostic
# ---------------------------------------------------------------------------
def part_a_volume_diagnostic(gam, pop, halves, out_reports: Path) -> dict:
    print("\n" + "=" * 78)
    print("PART A - VOLUME DIAGNOSTIC: E[raw|volume] vs E[adj|volume] (active)")
    print("=" * 78)

    d = gam.merge(pop[["game_id", "users_rated", "weight", "year"]], on="game_id",
                  how="left")
    d["log_n"] = np.log10(d["n_obs"])
    d["log_ur"] = np.log10(d["users_rated"])
    d["vol_band"] = pd.cut(d["n_obs"], bins=VOL_BAND_EDGES, labels=VOL_BAND_LABELS,
                           right=False)

    band = d.groupby("vol_band", observed=True).agg(
        games=("game_id", "size"),
        mean_n=("n_obs", "mean"),
        raw_mean=("raw_mean", "mean"),
        adj_mean=("adj_mean", "mean"),
    ).reset_index()
    print("\nMean quality by active-rating-volume band:")
    print(band.to_string(index=False, float_format=lambda x: f"{x:.3f}"))

    dec = (d.assign(decile=pd.qcut(d["log_n"], 10, duplicates="drop"))
             .groupby("decile", observed=True)
             .agg(games=("game_id", "size"), median_n=("n_obs", "median"),
                  raw_mean=("raw_mean", "mean"), adj_mean=("adj_mean", "mean"))
             .reset_index())
    gap_raw = float(dec["raw_mean"].iloc[-1] - dec["raw_mean"].iloc[0])
    gap_adj = float(dec["adj_mean"].iloc[-1] - dec["adj_mean"].iloc[0])

    slopes = {
        "raw_on_log_n_active": ols_slope(d["log_n"].to_numpy(), d["raw_mean"].to_numpy()),
        "adj_on_log_n_active": ols_slope(d["log_n"].to_numpy(), d["adj_mean"].to_numpy()),
        "raw_on_log_users_rated": ols_slope(d["log_ur"].to_numpy(), d["raw_mean"].to_numpy()),
        "adj_on_log_users_rated": ols_slope(d["log_ur"].to_numpy(), d["adj_mean"].to_numpy()),
    }
    dd = d.dropna(subset=["weight", "year"]).copy()
    knots = np.quantile(dd["year"].to_numpy(float), [0.05, 0.35, 0.65, 0.95])
    nsy = ns_basis(dd["year"].to_numpy(float), knots)
    dd["nsv0"], dd["nsv1"], dd["nsv2"] = nsy[:, 0], nsy[:, 1], nsy[:, 2]
    part = fwl_partial_slopes(dd, "log_n", ["raw_mean", "adj_mean"],
                              ["weight", "nsv0", "nsv1", "nsv2"])
    slopes["raw_partial_weight_year"] = part["raw_mean"]
    slopes["adj_partial_weight_year"] = part["adj_mean"]

    ratio_simple = slopes["adj_on_log_n_active"] / slopes["raw_on_log_n_active"]
    ratio_part = slopes["adj_partial_weight_year"] / slopes["raw_partial_weight_year"]

    h = halves.dropna(subset=["raw_even", "raw_odd"]).merge(
        d[["game_id", "log_n"]], on="game_id", how="inner")
    eo = {"n_games_both_halves": int(len(h))}
    for tgt in ["raw", "adj"]:
        eo[f"slope_{tgt}_even"] = ols_slope(h["log_n"].to_numpy(), h[f"{tgt}_even"].to_numpy())
        eo[f"slope_{tgt}_odd"] = ols_slope(h["log_n"].to_numpy(), h[f"{tgt}_odd"].to_numpy())

    ar = abs(ratio_simple)
    if ar >= 0.8:
        verdict = ("c) broadly unchanged or grows - severity adjustment does NOT explain "
                   "the volume gradient")
    elif ar >= 0.3:
        verdict = "b) substantially reduced but remains - severity explains part of the gradient"
    else:
        verdict = ("a) largely disappears - original gradient was mostly rater-pool "
                   "severity composition")

    print("\nVolume-gradient slopes (rating points per tenfold ratings):")
    for kk, vv in slopes.items():
        print(f"  {kk:34s} {vv:+.4f}")
    print(f"  {'ratio adj/raw (simple)':34s} {ratio_simple:+.3f}")
    print(f"  {'ratio adj/raw (partial w+y)':34s} {ratio_part:+.3f}")
    print(f"\nTop-vs-bottom log-volume decile gap: raw {gap_raw:+.3f}, adj {gap_adj:+.3f}")
    print("Even/odd split slopes:", {k: round(v, 4) for k, v in eo.items()})
    print(f"Classification: {verdict}")

    out_reports.mkdir(parents=True, exist_ok=True)
    band.to_csv(out_reports / "volume_diagnostic_band_table.csv", index=False)
    dec.to_csv(out_reports / "volume_diagnostic_decile_table.csv", index=False)

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    ax[0].plot(dec["median_n"], dec["raw_mean"], "o-", label="E[raw | volume]")
    ax[0].plot(dec["median_n"], dec["adj_mean"], "s-", label="E[adj_quality | volume]")
    ax[0].set_xscale("log")
    ax[0].set_xlabel("active ratings per game (decile medians)")
    ax[0].set_ylabel("mean quality estimate")
    ax[0].set_title("Volume-quality gradient, raw vs severity-adjusted\n"
                    f"slope raw {slopes['raw_on_log_n_active']:+.3f}, "
                    f"adj {slopes['adj_on_log_n_active']:+.3f} per 10x")
    ax[0].legend(fontsize=8)
    ax[0].grid(alpha=0.3)
    names = ["raw", "adj"]
    vals = [slopes["raw_on_log_n_active"], slopes["adj_on_log_n_active"]]
    bars = ax[1].bar(names, vals, color=["#777", "#36c"])
    ax[1].axhline(0, color="k", lw=0.8)
    for b, v in zip(bars, vals):
        ax[1].text(b.get_x() + b.get_width() / 2, v + 0.01, f"{v:+.3f}", ha="center")
    ax[1].set_ylabel("slope per tenfold increase in n_active")
    ax[1].set_title(f"Gradient after severity adjustment:\n{verdict.split(' - ')[0]}")
    ax[1].grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(out_reports / "volume_diagnostic.png", dpi=140)
    plt.close(fig)

    return {
        "volume_measure_primary": "n_obs = active ratings per game (same n that drives SE; "
                                  "measured in the same active universe as adj_mean)",
        "volume_measure_sensitivity": "users_rated (population scrape)",
        "band_table": band.assign(vol_band=band["vol_band"].astype(str)).to_dict(orient="records"),
        "decile_table": dec.assign(decile=dec["decile"].astype(str),
                                   median_n=dec["median_n"].astype(float)).to_dict(orient="records"),
        "gap_top_bottom_decile": {"raw": gap_raw, "adj": gap_adj},
        "slopes_per_tenfold": slopes,
        "ratio_adj_over_raw": {"simple": ratio_simple, "partial_weight_year": ratio_part},
        "even_odd_split_slopes": eo,
        "classification": verdict,
        "prior_filtered_population_reference":
            "findings.md 2026-08-23 (scripts/22): raw +0.444 -> adj +0.513 per tenfold",
        "claim_tags": {
            "slopes/gaps/band means": "empirical finding (descriptive, not causal)",
            "classification": "empirical finding among pre-stated categories a/b/c",
            "even_odd": "empirical finding (split-sample stability)",
        },
    }


# ---------------------------------------------------------------------------
# Part B — estimation sample and specification grid
# ---------------------------------------------------------------------------
def build_estimation_sample(gam: pd.DataFrame, pop: pd.DataFrame) -> pd.DataFrame:
    links = pd.read_parquet(REPO / "data/processed/phase2-filtered/game_links_filtered.parquet")
    n_impl = (links[links["rel"] == "reimplementation"].groupby("game_id").size()
              .rename("n_implementations").reset_index())
    est = gam.merge(pop, on="game_id", how="left")
    est = est.merge(n_impl, on="game_id", how="left")
    est["n_implementations"] = est["n_implementations"].fillna(0).astype(float)

    est["log_n_active"] = np.log10(est["n_obs"])
    est["year_c"] = est["year"] - 2015
    est["weight_c"] = est["weight"] - est["weight"].median()
    est["log_playtime_c"] = (np.log1p(est["playing_time"])
                             - np.log1p(est["playing_time"]).median())
    est["min_players_c"] = est["min_players"] - est["min_players"].median()
    est["log_max_players_c"] = (np.log1p(est["max_players"])
                                - np.log1p(est["max_players"]).median())
    est["is_reimpl_num"] = est["is_reimplementation"].astype(float)
    est["log_n_impl_c"] = (np.log1p(est["n_implementations"])
                           - np.log1p(est["n_implementations"]).median())
    est["vol_band"] = pd.cut(est["n_obs"], bins=VOL_BAND_EDGES, labels=VOL_BAND_LABELS,
                             right=False)
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
    print(f"\nEstimation sample: {len(est):,} games "
          f"(dropped {before - len(est)} for missing model fields)")
    return est


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
    names = sorted(dummy.columns)[1:]  # omit first level against intercept
    for name in names:
        est[name] = dummy[name]
    return names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--active-dir", type=Path, default=REPO / "scratch/phase2-active")
    ap.add_argument("--population", type=Path,
                    default=REPO / "scratch/phase2-active/bgg_research_population.parquet")
    ap.add_argument("--out-dir", type=Path, default=REPO / "data/processed/phase2-active")
    ap.add_argument("--reports-dir", type=Path, default=REPO / "reports/phase6_underratedness")
    args = ap.parse_args()

    print("Phase 6 - expected-quality model and underratedness residual (active population)")
    ensure_scratch_copy(args.active_dir)
    mu, sigma_e, sigma_a2 = load_phase5_params()
    args.reports_dir.mkdir(parents=True, exist_ok=True)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    gam = pd.read_parquet(args.active_dir / "game_adjusted_means_active.parquet")
    pop = pd.read_parquet(args.population)
    print(f"Adjusted means: {len(gam):,} games; population: {len(pop):,} games")

    con = duckdb.connect()
    configure(con, REPO / "scratch/ducktmp")
    halves = even_odd_halves(con, args.active_dir)
    print(f"Even/odd halves computed for {halves['raw_even'].notna().sum():,} games")

    vol_diag = part_a_volume_diagnostic(gam, pop, halves, args.reports_dir)

    # ------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("PART B - EXPECTED QUALITY E[adj_mean | characteristics]")
    print("=" * 78)
    est = build_estimation_sample(gam, pop)
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
    print(f"Features: {len(cat_cols)} category flags, {len(mech_cols)} mechanic flags "
          f"(>= {TAG_MIN_COUNT} games on sample), {len(band_cols)} volume-band and "
          f"{len(dec_cols)} decade dummies, natural-spline year ({len(ns_year_cols)} cols)")

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
    y_raw = est["avg_rating_current"].to_numpy(float)
    n_obs = est["n_obs"].to_numpy(float)
    log_n = est["log_n_active"].to_numpy(float)
    weightings = {
        "ols": np.ones(len(est)),
        "wls_n": n_obs.copy(),
        "gls_eff": 1.0 / (sigma_a2 + sigma_e ** 2 / n_obs),
    }

    designs = {name: np.column_stack([np.ones(len(est))] +
                                     [est[c].to_numpy(float) for c in cols])
               for name, cols in specs.items()}
    col_names = {name: ["intercept"] + cols for name, cols in specs.items()}

    results, coef_rows, resid_store = [], [], {}

    def run_spec(spec_name, wt_name, y, label):
        X, w = designs[spec_name], weightings[wt_name]
        key = f"{spec_name}|{wt_name}|{label}"
        beta, pred, resid = fit_wls(X, y, w)
        cv_pred, cv_resid, fold_betas, fold_idx = cv_predictions(X, y, w)
        m_in = metrics(y, resid)
        fold_stats = [metrics(y[ix], cv_resid[ix]) for ix in fold_idx]
        fold_r2 = [f["r2"] for f in fold_stats]
        fold_rmse = [f["rmse"] for f in fold_stats]
        cn = col_names[spec_name]
        bi = dict(zip(cn, beta))
        vi = cn.index("log_n_active") if "log_n_active" in cn else None
        band_means = (pd.DataFrame({"b": est["vol_band"].astype(str).to_numpy(),
                                    "r": resid})
                      .groupby("b").r.mean())
        band_flat = float(band_means.abs().max())
        row = {
            "spec": spec_name, "weighting": wt_name, "target": label,
            "n_games": int(len(y)), "n_features": int(X.shape[1]),
            "r2_in": m_in["r2"], "rmse_in": m_in["rmse"], "mae_in": m_in["mae"],
            "cv_r2_mean": float(np.mean(fold_r2)), "cv_r2_sd": float(np.std(fold_r2)),
            "cv_rmse_mean": float(np.mean(fold_rmse)),
            "cv_rmse_sd": float(np.std(fold_rmse)),
            "beta_logn": bi.get("log_n_active"),
            "beta_logn_fold_sd": float(np.std(fold_betas[:, vi])) if vi is not None else None,
            "beta_weight": bi.get("weight_c"),
            "beta_weight_fold_sd": (float(np.std(fold_betas[:, cn.index("weight_c")]))
                                    if "weight_c" in cn else None),
            "corr_resid_logn": float(np.corrcoef(resid, log_n)[0, 1]),
            "corr_cvresid_logn": float(np.corrcoef(cv_resid, log_n)[0, 1]),
            "spearman_resid_logn": float(pd.Series(resid).corr(pd.Series(log_n),
                                                               method="spearman")),
            "max_abs_bandmean_resid": band_flat,
        }
        results.append(row)
        coef_rows.append({"spec": spec_name, "weighting": wt_name, "target": label,
                          **{c: float(bi[c]) for c in
                             ["intercept", "log_n_active", "weight_c", "log_playtime_c",
                              "min_players_c", "log_max_players_c", "is_reimpl_num",
                              "log_n_impl_c"] if c in bi}})
        resid_store[key] = {"resid": resid, "cv_resid": cv_resid, "pred": pred}
        print(f"{spec_name:14s} {wt_name:7s} {label:3s} feat={X.shape[1]:3d} "
              f"R2in={m_in['r2']:.4f} CV_R2={row['cv_r2_mean']:.4f}"
              f"+-{row['cv_r2_sd']:.4f} CV_RMSE={row['cv_rmse_mean']:.4f} "
              f"b_logn={bi.get('log_n_active', np.nan):+.4f} "
              f"corr(resid,logn)={row['corr_resid_logn']:+.4f} "
              f"max|bandmean|={band_flat:.3f}")

    for spec in specs:
        for wt in ["ols", "wls_n"]:
            run_spec(spec, wt, y_adj, "adj")
        if spec in {"Q0_flex_year", "Q1_core", "Q3_categories"}:
            run_spec(spec, "gls_eff", y_adj, "adj")
    for spec in ["Q0_flex_year", "Q3_categories"]:
        for wt in ["ols", "wls_n"]:
            run_spec(spec, wt, y_raw, "raw")
    for spec in ["Q3b_flex_volume"]:
        for wt in ["ols", "wls_n"]:
            run_spec(spec, wt, y_raw, "raw")

    res_df = pd.DataFrame(results)
    coef_df = pd.DataFrame(coef_rows)
    res_df.to_csv(args.reports_dir / "comparative_table.csv", index=False)
    coef_df.to_csv(args.reports_dir / "coefficient_table.csv", index=False)

    # ------------------------------------------------------------------
    # residual stability across specs and weightings (adj target)
    # ------------------------------------------------------------------
    keys_adj = sorted(k for k in resid_store if k.endswith("|adj"))
    stab_rows = []
    for i, ka in enumerate(keys_adj):
        for kb in keys_adj[i + 1:]:
            ra, rb = resid_store[ka]["resid"], resid_store[kb]["resid"]
            stab_rows.append({
                "a": ka, "b": kb,
                "pearson": float(np.corrcoef(ra, rb)[0, 1]),
                "spearman": float(pd.Series(ra).corr(pd.Series(rb), method="spearman")),
                "jaccard_top1": top_jaccard(ra, rb)})
    stab_df = pd.DataFrame(stab_rows)
    stab_df.to_csv(args.reports_dir / "residual_overlap.csv", index=False)
    core_keys = [k for k in keys_adj
                 if k.startswith(("Q0_", "Q1_", "Q2_", "Q3_")) and "|ols|" in k + "|"]
    sub = stab_df[[all(part in set(core_keys) for part in (r.a, r.b))
                   for _, r in stab_df.iterrows()]]
    print("\nAcross core specs (OLS, adj target) residual agreement: "
          f"pearson mean {sub['pearson'].mean():.3f} "
          f"[{sub['pearson'].min():.3f},{sub['pearson'].max():.3f}], "
          f"top1% Jaccard mean {sub['jaccard_top1'].mean():.3f} "
          f"[{sub['jaccard_top1'].min():.3f},{sub['jaccard_top1'].max():.3f}]")

    ols_keys = {s: f"{s}|ols|adj" for s in specs}
    wls_keys = {s: f"{s}|wls_n|adj" for s in specs}
    wls_impact = {}
    for s in specs:
        ro, rw = resid_store[ols_keys[s]]["resid"], resid_store[wls_keys[s]]["resid"]
        bo = res_df[(res_df.spec == s) & (res_df.weighting == "ols")].iloc[0]
        bw = res_df[(res_df.spec == s) & (res_df.weighting == "wls_n")].iloc[0]
        wls_impact[s] = {
            "beta_logn_ols": None if pd.isna(bo.beta_logn) else float(bo.beta_logn),
            "beta_logn_wls": None if pd.isna(bw.beta_logn) else float(bw.beta_logn),
            "beta_logn_shift_pct": (float((bw.beta_logn - bo.beta_logn) / abs(bo.beta_logn))
                                    if bo.beta_logn and not pd.isna(bo.beta_logn) else None),
            "cv_r2_ols": float(bo.cv_r2_mean), "cv_r2_wls": float(bw.cv_r2_mean),
            "resid_spearman_ols_wls": float(pd.Series(ro).corr(pd.Series(rw),
                                                                method="spearman")),
            "jaccard_top1_ols_wls": top_jaccard(ro, rw)}
    print("\nWLS impact by spec:", json.dumps(
        {k: {kk: (round(vv, 3) if isinstance(vv, float) else vv)
             for kk, vv in v.items()} for k, v in wls_impact.items()}, indent=1))

    adj_vs_raw = {}
    for s in ["Q0_flex_year", "Q3_categories", "Q3b_flex_volume"]:
        for wt in ["ols", "wls_n"]:
            ra = resid_store[f"{s}|{wt}|adj"]["resid"]
            rr = resid_store[f"{s}|{wt}|raw"]["resid"]
            ba = res_df[(res_df.spec == s) & (res_df.weighting == wt)
                        & (res_df.target == "adj")].iloc[0]
            br = res_df[(res_df.spec == s) & (res_df.weighting == wt)
                        & (res_df.target == "raw")].iloc[0]
            adj_vs_raw[f"{s}|{wt}"] = {
                "r2_adj": float(ba.r2_in), "r2_raw": float(br.r2_in),
                "beta_logn_adj": None if pd.isna(ba.beta_logn) else float(ba.beta_logn),
                "beta_logn_raw": None if pd.isna(br.beta_logn) else float(br.beta_logn),
                "resid_pearson": float(np.corrcoef(ra, rr)[0, 1]),
                "resid_spearman": float(pd.Series(ra).corr(pd.Series(rr),
                                                           method="spearman")),
                "jaccard_top1": top_jaccard(ra, rr)}

    # ------------------------------------------------------------------
    # preferred specification — explicit documented choice, not a black-box rule.
    # Evidence (printed above): (i) OLS dominates WLS_n on CV for every spec;
    # (ii) gls_eff ~ OLS, so measurement noise is small relative to between-game
    # variance and n-weighting mostly reweights the population rather than
    # correcting noise; (iii) WLS leaves corr(resid, log n) clearly negative and a
    # +0.3 mean residual for sub-100-rating games — volume leaks into its
    # residuals exactly where low-n candidates would live; (iv) Part A shows the
    # volume-quality curve is convex and non-monotonic at the bottom, so a linear
    # log_n term leaves a U-shaped banded residual pattern (max|bandmean| .128
    # for Q3); replacing it with band dummies (Q3b) removes that pattern by
    # construction, gains +0.012 CV R2, and nearly matches the 73-feature
    # mechanics spec with 46 features.
    # => carry Q3b_flex_volume / OLS as expected_quality_g; Q3 (linear volume) is
    #    the compact variant, Q4 (mechanics) the richer sensitivity.
    # ------------------------------------------------------------------
    cand = res_df[res_df.target == "adj"].sort_values(
        ["cv_r2_mean", "cv_rmse_mean"], ascending=[False, True]).reset_index(drop=True)
    pref_spec, pref_wt = "Q3b_flex_volume", "ols"
    pref = res_df[(res_df.spec == pref_spec) & (res_df.weighting == pref_wt)
                  & (res_df.target == "adj")].iloc[0]
    best_row = cand.iloc[0]

    def agree(a_key, b_key):
        ra = resid_store[a_key]["resid"]
        rb = resid_store[b_key]["resid"]
        return (float(pd.Series(ra).corr(pd.Series(rb), method="spearman")),
                top_jaccard(ra, rb))

    s34, j34 = agree("Q3_categories|ols|adj", "Q4_mechanics|ols|adj")
    s3b3, j3b3 = agree("Q3b_flex_volume|ols|adj", "Q3_categories|ols|adj")
    s3b4, j3b4 = agree("Q3b_flex_volume|ols|adj", "Q4_mechanics|ols|adj")
    print(f"\nPreferred specification: {pref_spec} / {pref_wt} "
          f"(CV_R2 {float(pref.cv_r2_mean):.4f}; best-CV variant "
          f"{best_row['spec']}/{best_row['weighting']} at {float(best_row.cv_r2_mean):.4f})")
    print(f"Residual agreement: Q3b vs Q3 spearman {s3b3:.3f} Jaccard {j3b3:.3f}; "
          f"Q3b vs Q4 {s3b4:.3f}/{j3b4:.3f}; Q3 vs Q4 {s34:.3f}/{j34:.3f}")
    print("CV ranking (top 8):")
    print(cand.head(8)[["spec", "weighting", "cv_r2_mean", "cv_r2_sd", "cv_rmse_mean",
                        "beta_logn", "corr_cvresid_logn",
                        "max_abs_bandmean_resid"]].round(4).to_string(index=False))

    # low-n residual stability: residual evaluated at full vs even-half adj_mean
    # ------------------------------------------------------------------
    lown = (est[["game_id", "n_obs"]].merge(halves[["game_id", "adj_even"]], on="game_id",
                                            how="inner").dropna(subset=["adj_even"]))
    keep_idx = np.isin(est["game_id"].to_numpy(), lown["game_id"].to_numpy())
    lown_sorted = lown.set_index("game_id").loc[est.loc[keep_idx, "game_id"]]
    adj_even_vec = lown_sorted["adj_even"].to_numpy(float)
    n_keep = lown_sorted["n_obs"].to_numpy(float)
    bands = pd.qcut(pd.Series(n_keep).rank(method="first"), 4,
                    labels=["n_q1_low", "n_q2", "n_q3", "n_q4_high"]).to_numpy()
    Xp = designs[pref_spec]
    lown_rows = []
    Xk = Xp[keep_idx]
    yk = y_adj[keep_idx]
    for wt in ["ols", "wls_n", "gls_eff"]:
        beta, _, _ = fit_wls(Xp, y_adj, weightings[wt])
        r_full = yk - Xk @ beta
        r_even = adj_even_vec - Xk @ beta
        for b in ["n_q1_low", "n_q2", "n_q3", "n_q4_high"]:
            m = bands == b
            lown_rows.append({
                "weighting": wt, "n_quartile": str(b), "n_games": int(m.sum()),
                "mean_n": float(n_keep[m].mean()),
                "corr_resid_full_vs_even": float(np.corrcoef(r_full[m], r_even[m])[0, 1]),
                "resid_sd_full": float(np.std(r_full[m])),
                "resid_sd_even": float(np.std(r_even[m]))})
    lown_df = pd.DataFrame(lown_rows)
    lown_df.to_csv(args.reports_dir / "low_n_residual_stability.csv", index=False)
    print(f"\nLow-n residual stability, {pref_spec} (corr of residual at full vs "
          "even-half target):")
    print(lown_df.pivot(index="n_quartile", columns="weighting",
                        values="corr_resid_full_vs_even").round(3).to_string())

    # ------------------------------------------------------------------
    beta_pref, pred_pref, resid_pref = fit_wls(designs[pref_spec], y_adj,
                                               weightings[pref_wt])
    cv_pred_pref, cv_resid_pref, _, _ = cv_predictions(designs[pref_spec], y_adj,
                                                       weightings[pref_wt])
    se_pref = sigma_e / np.sqrt(n_obs)

    # residual vs volume diagnostic plot for the preferred spec
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    ax[0].hexbin(log_n, resid_pref, gridsize=40, cmap="Blues", bins="log")
    dm = (pd.DataFrame({"l": log_n, "r": resid_pref})
            .assign(b=lambda x: pd.qcut(x.l, 10, duplicates="drop"))
            .groupby("b", observed=True).agg(l=("l", "mean"), r=("r", "mean")))
    ax[0].plot(dm.l, dm.r, "r-o", ms=4, lw=1.5, label="decile mean")
    ax[0].axhline(0, color="k", lw=0.8)
    ax[0].set_xlabel("log10(active ratings)")
    ax[0].set_ylabel("underratedness residual")
    ax[0].legend(fontsize=8)
    ax[0].set_title(f"{pref_spec}/{pref_wt}: residual vs volume\n"
                    f"corr {np.corrcoef(log_n, resid_pref)[0, 1]:+.4f}")
    ax[0].grid(alpha=0.3)
    width = 0.38
    xs = np.arange(len(VOL_BAND_LABELS))
    for off, (wt_key, color, lab) in enumerate([
            ("Q3_categories|ols|adj", "#777", "Q3 linear log-volume (OLS)"),
            (f"{pref_spec}|ols|adj", "#36c", f"{pref_spec} band-volume (OLS)")]):
        rk = resid_store[wt_key]["resid"]
        bm = (pd.DataFrame({"band": est["vol_band"].astype(str).to_numpy(), "r": rk})
                .groupby("band").r.mean())
        ax[1].bar(xs + (off - 0.5) * width, [bm.get(lbl, np.nan)
                                             for lbl in VOL_BAND_LABELS],
                  width=width, color=color, label=lab)
    ax[1].axhline(0, color="k", lw=0.8)
    ax[1].set_xticks(xs)
    ax[1].set_xticklabels(VOL_BAND_LABELS, rotation=45, fontsize=7)
    ax[1].set_ylabel("mean residual by volume band")
    ax[1].set_title("Mean residual flatness across volume bands")
    ax[1].legend(fontsize=8)
    ax[1].grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(args.reports_dir / "residual_diagnostics.png", dpi=140)
    plt.close(fig)

    # per-game output for downstream phases
    out = pd.DataFrame({
        "game_id": est["game_id"], "title": est["title"], "year": est["year"],
        "n_obs": n_obs.astype(int), "users_rated": est["users_rated"],
        "raw_mean": est["raw_mean"], "adj_mean": y_adj, "se_adj": se_pref,
        "expected_quality_pref": pred_pref,
        "underratedness_pref": resid_pref,
        "underratedness_cv_pref": cv_resid_pref,
        "underratedness_wls_pref": resid_store[f"{pref_spec}|wls_n|adj"]["resid"],
        "underratedness_ols_Q3": resid_store["Q3_categories|ols|adj"]["resid"],
        "underratedness_wls_Q3": resid_store["Q3_categories|wls_n|adj"]["resid"],
    })
    out.to_parquet(args.out_dir / "phase6_residuals_active.parquet", index=False)

    top = out.nlargest(20, "underratedness_pref")
    top.to_csv(args.reports_dir / "top_residuals_preview.csv", index=False)
    top100 = out[out.n_obs >= 100].nlargest(20, "underratedness_pref")
    top100.to_csv(args.reports_dir / "top_residuals_preview_nmin100.csv", index=False)
    print("\nIllustrative top-20 positive residuals (candidate diagnostics, NOT a ranking):")
    print(top[["title", "year", "n_obs", "adj_mean", "se_adj", "expected_quality_pref",
               "underratedness_pref"]].to_string(index=False, float_format=lambda x: f"{x:.3f}"))
    print("\nTop-20 restricted to games with n>=100 (P10 floor), same caveat:")
    print(top100[["title", "year", "n_obs", "adj_mean", "se_adj",
                  "underratedness_pref"]].to_string(index=False,
                                                    float_format=lambda x: f"{x:.3f}"))

    # ------------------------------------------------------------------
    # committed JSON summaries
    # ------------------------------------------------------------------
    vol_json = {**vol_diag,
                "params": {"mu": mu, "sigma_e": sigma_e,
                           "sigma_alpha": float(np.sqrt(sigma_a2))},
                "method_discipline": {
                    "copy_once": "scratch/phase2-active",
                    "bounded": "duckdb 4GB/threads3/temp scratch/ducktmp; single grouped "
                               "even-odd pass over rating_observations_active",
                    "independent": "recorded separately; expected-quality specs do not "
                                   "absorb this diagnostic"}}
    (args.out_dir / "phase6_volume_diagnostic.json").write_text(json.dumps(vol_json, indent=1))

    comp_json = {
        "generated_for": "Phase 6 expected-quality model on Phase 5 adj_mean target",
        "params": {"mu": mu, "sigma_e": sigma_e, "sigma_alpha": float(np.sqrt(sigma_a2)),
                   "wls_note": "w_g = n_g equals 1/SE_g^2 up to the constant "
                               f"1/sigma_e^2 (sigma_e={sigma_e:.3f}); SE range "
                               f"P10-P90 implies order-of-magnitude heteroscedasticity"},
        "estimation_sample": {"n_games": int(len(est)),
                              "features": {"category_flags": len(cat_cols),
                                           "mechanic_flags": len(mech_cols),
                                           "volume_bands": len(band_cols),
                                           "decades": len(dec_cols)},
                              "tag_min_count": TAG_MIN_COUNT},
        "specs": {k: v for k, v in specs.items()},
        "comparative_table": res_df.astype(object).where(res_df.notna(), None).to_dict(orient="records"),
        "coefficients": coef_df.astype(object).where(coef_df.notna(), None).to_dict(orient="records"),
        "wls_vs_ols": wls_impact,
        "adj_vs_raw": adj_vs_raw,
        "low_n_residual_stability": lown_df.to_dict(orient="records"),
        "preferred_specification": {
            "spec": pref_spec, "weighting": pref_wt,
            "justification": "OLS over WLS_n: WLS_n degrades CV for every spec, shifts "
                             "beta_logn +28-48%, and leaves a +0.32 mean residual for "
                             "sub-100-rating games (volume leaks into the residual "
                             "exactly where low-n candidates live); gls_eff ~ OLS shows "
                             "measurement noise is small vs between-game variance, so "
                             "n-weighting reweights the population rather than "
                             "correcting noise. Band-based volume (Q3b) over linear "
                             "log_n: Part A shows the volume-quality curve is convex "
                             "and non-monotonic at the bottom; linear control leaves a "
                             "U-shaped banded residual (max|bandmean| 0.128), bands "
                             "remove it and add +0.012 CV R2. Categories kept, "
                             "mechanics as sensitivity (Q3b vs Q4 agreement printed).",
            "cv_r2": float(pref["cv_r2_mean"]), "cv_rmse": float(pref["cv_rmse_mean"]),
            "beta_logn": None if pd.isna(pref["beta_logn"]) else float(pref["beta_logn"]),
            "corr_resid_logn": float(pref["corr_resid_logn"]),
            "residual_agreement": {"Q3b_vs_Q3": {"spearman": s3b3, "jaccard_top1": j3b3},
                                   "Q3b_vs_Q4": {"spearman": s3b4, "jaccard_top1": j3b4},
                                   "Q3_vs_Q4": {"spearman": s34, "jaccard_top1": j34}}},
        "claim_tags": {
            "cv_metrics_coefficients": "model-dependent empirical findings",
            "residual_overlaps": "empirical findings about model outputs",
            "underratedness": "operational model-dependent measure, not latent quality "
                              "or broad appeal"},
        "limitations": [
            "no external broad-appeal validation; residual screens conditional anomalies only",
            "population metadata complete via bgg_research_population; raw games table "
            "(80.89% coverage) deliberately not used here",
            "tags overlap; indicators estimated as descriptive contrasts, not causal effects",
            "measurement-error-in-X not modeled (e.g., weight measured with noise)",
            "severity adjustment removes additive rater level only; within-game selection "
            "was ~0 in Phase 4 but non-additive forms remain untested"],
    }
    (args.out_dir / "phase6_comparative.json").write_text(json.dumps(comp_json, indent=1))
    docs_dir = REPO / "docs/phase2-active"
    docs_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(args.out_dir / "phase6_volume_diagnostic.json",
                 docs_dir / "phase6_volume_diagnostic.json")
    shutil.copy2(args.out_dir / "phase6_comparative.json",
                 docs_dir / "phase6_comparative.json")
    print(f"\nWrote reports to {args.reports_dir}, JSON summaries to {args.out_dir} "
          f"(docs copies in {docs_dir})")


if __name__ == "__main__":
    main()

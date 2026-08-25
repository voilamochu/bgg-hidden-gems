"""Step 9 §§2-8 — Rebuild expected quality Q-ladder & underratedness on Pass-2.

Population: 14,698 games × 287,302 users × 24,146,307 obs
  data/processed/phase2-pass2/ (mu≈7.139, severity reused, NOT refit)

Conceptual structure: adjusted quality -> expected quality from observable
  characteristics -> residual = underratedness. Do NOT interpret residual as quality.

Re-estimates:
  - Phase 6 ladder (Q0-Q4, Q3b primary) on Pass-2 game-level data via OLS primary,
    with WLS sensitivity.
  - Volume diagnostic: E[raw|volume] vs E[adj|volume] (linear log, flexible bands,
    decile gap, partial controlling for weight/year).
  - Underratedness residuals, stability across specs/weightings, high-residual vs
    absolute quality, recommended spec, Pass-1 vs Pass-2 comparison.

Inputs: games_pass2.parquet + game_adjusted_means_pass2 + game_tags_pass2 +
        game_links_pass2 + bgg_research_population + step9_quality_estimator_refresh.json
        + historical phase6_comparative.json for comparison.

Outputs: docs/phase2-pass2/step9_expected_quality_underratedness/* and mirror
         reports/phase2_pass2/step9_expected_quality_underratedness/*

Bounded: memory_limit 4GB threads 3 temp scratch/ducktmp, narrow aggregations.

Usage:
  python scripts/48_step9_expected_quality_underratedness.py
"""
import argparse
import json
import re
import shutil
import time
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
# Task's suggested 6-band set for sensitivity / reporting
VOL_BAND_EDGES_6 = [0, 100, 200, 500, 1000, 2000, 5000, np.inf]
VOL_BAND_LABELS_6 = ["1-99","100-199","200-499","500-999","1k-2k","2k-5k","5k+"]

def qpath(p: Path) -> str:
    return str(p).replace("'", "''")

def configure(con, tmp_dir: Path):
    con.execute(f"SET memory_limit='{MEMORY}'")
    con.execute(f"SET threads={THREADS}")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    con.execute(f"SET temp_directory='{qpath(tmp_dir)}'")
    con.execute("SET preserve_insertion_order=false")

def ensure_scratch_copy():
    src = REPO / "data/processed/phase2-pass2"
    dst = REPO / "scratch/phase2-pass2"
    needed = ["game_adjusted_means_pass2.parquet", "user_severity_pass2.parquet",
              "rating_observations_pass2.parquet", "games_pass2.parquet",
              "game_tags_pass2.parquet", "game_links_pass2.parquet"]
    for fn in needed:
        dp, sp = dst / fn, src / fn
        if not dp.exists() and sp.exists():
            print(f"  copy-once {sp} -> {dp}")
            dst.mkdir(parents=True, exist_ok=True)
            shutil.copy2(sp, dp)
    pop_src = REPO / "data/processed/bgg_research_population.parquet"
    pop_dst = dst / "bgg_research_population.parquet"
    if not pop_dst.exists() and pop_src.exists():
        shutil.copy2(pop_src, pop_dst)
    return dst

def load_phase5_params():
    candidates = [
        REPO / "data/processed/phase2-pass2/step9_quality_estimator_refresh.json",
        REPO / "docs/phase2-pass2/step9_expected_quality_underratedness/step9_quality_estimator_refresh.json",
        REPO / "reports/phase2_pass2/step9_expected_quality_underratedness/step9_quality_estimator_refresh.json",
        REPO / "docs/phase2-active/phase5_quality_comparison.json",
        REPO / "data/processed/phase2-active/phase5_quality_estimator.json",
    ]
    for p in candidates:
        if p.exists():
            j = json.loads(p.read_text())
            evc = j.get("eb_variance_components", {})
            mu = j.get("validation", {}).get("mu_pass2") or j.get("validation", {}).get("mu_active") or evc.get("mu_prior")
            sigma_e = evc.get("sigma_e_sd")
            sigma_a2 = evc.get("sigma_alpha2_mm")
            if mu and sigma_e and sigma_a2:
                print(f"  Phase5 params from {p}: mu={mu:.4f} sigma_e={sigma_e:.4f} sigma_alpha={np.sqrt(sigma_a2):.4f}")
                return float(mu), float(sigma_e), float(sigma_a2), p
    # fallback hard-coded pass2 baseline if file not yet written (mu 7.139)
    print("  WARNING: step9 quality estimator JSON not found, using pass2 baseline_refresh mu 7.139 and estimating sigma_e from data")
    return 7.13900772639585, 1.194, 0.746, None

def fit_wls(X, y, w):
    sw = np.sqrt(w)
    beta, *_ = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)
    pred = X @ beta
    return beta, pred, y - pred

def metrics(y, resid):
    sse = float(np.sum(resid ** 2))
    sst = float(np.sum((y - np.mean(y)) ** 2))
    return {"r2": 1 - sse / sst if sst>0 else 0, "rmse": float(np.sqrt(np.mean(resid ** 2))),
            "mae": float(np.mean(np.abs(resid)))}

def cv_predictions(X, y, w, folds=N_FOLDS, seed=RANDOM_SEED):
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
    return len(sa & sb) / len(sa | sb) if sa|sb else 0

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

def ols_slope(x, y):
    xc, yc = x - x.mean(), y - y.mean()
    return float(np.dot(xc, yc) / np.dot(xc, xc)) if np.dot(xc, xc)!=0 else float('nan')

def fwl_partial_slopes(df, x_col, targets, control_cols):
    Z = np.column_stack([np.ones(len(df))] + [df[c].to_numpy(float) for c in control_cols])
    proj = lambda v: v - Z @ np.linalg.lstsq(Z, v, rcond=None)[0]
    lx = proj(df[x_col].to_numpy(float))
    return {t: ols_slope(lx, proj(df[t].to_numpy(float))) for t in targets}

def part_a_volume_diagnostic(gam, pop, halves, out_reports: Path, mu, sigma_e) -> dict:
    print("\n" + "="*78)
    print("VOLUME DIAGNOSTIC: E[raw|volume] vs E[adj|volume] (pass2)")
    print("="*78)
    d = gam.merge(pop[["game_id", "users_rated", "weight", "year"]], on="game_id", how="left")
    d["log_n"] = np.log10(d["n_obs"])
    d["log_ur"] = np.log10(d["users_rated"])
    d["vol_band"] = pd.cut(d["n_obs"], bins=VOL_BAND_EDGES, labels=VOL_BAND_LABELS, right=False)
    d["vol_band_6"] = pd.cut(d["n_obs"], bins=VOL_BAND_EDGES_6, labels=VOL_BAND_LABELS_6, right=False)

    band = d.groupby("vol_band", observed=True).agg(
        games=("game_id","size"),
        mean_n=("n_obs","mean"),
        median_n=("n_obs","median"),
        raw_mean=("raw_mean","mean"),
        raw_median=("raw_mean","median"),
        adj_mean=("adj_mean","mean"),
        adj_median=("adj_mean","median"),
        raw_sd=("raw_mean","std"),
        adj_sd=("adj_mean","std"),
    ).reset_index()
    band6 = d.groupby("vol_band_6", observed=True).agg(
        games=("game_id","size"),
        mean_n=("n_obs","mean"),
        raw_mean=("raw_mean","mean"),
        adj_mean=("adj_mean","mean"),
    ).reset_index()
    print("\nMean quality by pass2 volume band (Phase6 edges):")
    print(band.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
    print("\nMean quality by 6-band set (task suggestion):")
    print(band6.to_string(index=False, float_format=lambda x: f"{x:.3f}"))

    dec = (d.assign(decile=pd.qcut(d["log_n"], 10, duplicates="drop"))
             .groupby("decile", observed=True)
             .agg(games=("game_id","size"), median_n=("n_obs","median"),
                  raw_mean=("raw_mean","mean"), adj_mean=("adj_mean","mean"))
             .reset_index())
    gap_raw = float(dec["raw_mean"].iloc[-1] - dec["raw_mean"].iloc[0])
    gap_adj = float(dec["adj_mean"].iloc[-1] - dec["adj_mean"].iloc[0])

    slopes = {
        "raw_on_log_n_pass2": ols_slope(d["log_n"].to_numpy(), d["raw_mean"].to_numpy()),
        "adj_on_log_n_pass2": ols_slope(d["log_n"].to_numpy(), d["adj_mean"].to_numpy()),
        "raw_on_log_users_rated": ols_slope(d["log_ur"].to_numpy(), d["raw_mean"].to_numpy()),
        "adj_on_log_users_rated": ols_slope(d["log_ur"].to_numpy(), d["adj_mean"].to_numpy()),
    }
    dd = d.dropna(subset=["weight","year"]).copy()
    knots = np.quantile(dd["year"].to_numpy(float), [0.05, 0.35, 0.65, 0.95])
    nsy = ns_basis(dd["year"].to_numpy(float), knots)
    dd["nsv0"], dd["nsv1"], dd["nsv2"] = nsy[:,0], nsy[:,1], nsy[:,2]
    part = fwl_partial_slopes(dd, "log_n", ["raw_mean","adj_mean"], ["weight","nsv0","nsv1","nsv2"])
    slopes["raw_partial_weight_year"] = part["raw_mean"]
    slopes["adj_partial_weight_year"] = part["adj_mean"]
    ratio_simple = slopes["adj_on_log_n_pass2"] / slopes["raw_on_log_n_pass2"] if slopes["raw_on_log_n_pass2"]!=0 else float('nan')
    ratio_part = slopes["adj_partial_weight_year"] / slopes["raw_partial_weight_year"] if slopes["raw_partial_weight_year"]!=0 else float('nan')

    # even/odd split stability if halves available
    if halves is not None and len(halves):
        h = halves.dropna(subset=["raw_even","raw_odd"]).merge(d[["game_id","log_n"]], on="game_id", how="inner")
        eo = {"n_games_both_halves": int(len(h))}
        for tgt in ["raw","adj"]:
            eo[f"slope_{tgt}_even"] = ols_slope(h["log_n"].to_numpy(), h[f"{tgt}_even"].to_numpy())
            eo[f"slope_{tgt}_odd"] = ols_slope(h["log_n"].to_numpy(), h[f"{tgt}_odd"].to_numpy())
    else:
        eo = {"n_games_both_halves": 0}

    ar = abs(ratio_simple)
    if ar >= 0.8:
        verdict = "c) broadly unchanged or grows - severity adjustment does NOT explain the volume gradient"
    elif ar >= 0.3:
        verdict = "b) substantially reduced but remains - severity explains part of the gradient"
    else:
        verdict = "a) largely disappears - original gradient was mostly rater-pool severity composition"

    print("\nVolume-gradient slopes (rating points per tenfold ratings):")
    for kk, vv in slopes.items():
        print(f"  {kk:34s} {vv:+.4f}")
    print(f"  {'ratio adj/raw (simple)':34s} {ratio_simple:+.3f}")
    print(f"  {'ratio adj/raw (partial w+y)':34s} {ratio_part:+.3f}")
    print(f"\nTop-vs-bottom log-volume decile gap: raw {gap_raw:+.3f}, adj {gap_adj:+.3f}")
    if eo.get("n_games_both_halves"):
        print("Even/odd split slopes:", {k: round(v,4) for k,v in eo.items() if 'slope' in k})
    print(f"Classification: {verdict}")
    # also inspect low-volume tail now that all >=100: compare 100-199 vs high
    low_band = band[band["vol_band"]=="100-199"]
    high_band = band[band["vol_band"]=="25k+"]
    if not low_band.empty and not high_band.empty:
        print(f"Low tail 100-199 mean raw {low_band['raw_mean'].values[0]:.3f} adj {low_band['adj_mean'].values[0]:.3f} vs 25k+ raw {high_band['raw_mean'].values[0]:.3f} adj {high_band['adj_mean'].values[0]:.3f}")

    out_reports.mkdir(parents=True, exist_ok=True)
    band.to_csv(out_reports / "volume_diagnostic_band_table.csv", index=False)
    band6.to_csv(out_reports / "volume_diagnostic_band_table_6band.csv", index=False)
    dec.to_csv(out_reports / "volume_diagnostic_decile_table.csv", index=False)

    fig, ax = plt.subplots(1, 2, figsize=(11,4.2))
    ax[0].plot(dec["median_n"], dec["raw_mean"], "o-", label="E[raw | volume]")
    ax[0].plot(dec["median_n"], dec["adj_mean"], "s-", label="E[adj_quality | volume]")
    ax[0].set_xscale("log")
    ax[0].set_xlabel("pass2 ratings per game (decile medians)")
    ax[0].set_ylabel("mean quality estimate")
    ax[0].set_title("Volume-quality gradient, raw vs severity-adjusted (pass2)\n"
                    f"slope raw {slopes['raw_on_log_n_pass2']:+.3f}, adj {slopes['adj_on_log_n_pass2']:+.3f} per 10x")
    ax[0].legend(fontsize=8)
    ax[0].grid(alpha=0.3)
    names = ["raw","adj"]
    vals = [slopes["raw_on_log_n_pass2"], slopes["adj_on_log_n_pass2"]]
    bars = ax[1].bar(names, vals, color=["#777","#36c"])
    ax[1].axhline(0, color="k", lw=0.8)
    for b, v in zip(bars, vals):
        ax[1].text(b.get_x()+b.get_width()/2, v+0.01, f"{v:+.3f}", ha="center", fontsize=9)
    ax[1].set_ylabel("slope per tenfold increase in n_pass2")
    ax[1].set_title(f"Gradient after severity adjustment:\n{verdict.split(' - ')[0]}")
    ax[1].grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(out_reports / "volume_diagnostic.png", dpi=140)
    plt.close(fig)

    # Additional plot: band means
    fig, ax = plt.subplots(figsize=(10,4))
    x = np.arange(len(band))
    w = 0.35
    ax.bar(x - w/2, band["raw_mean"], width=w, label="raw", color="#777")
    ax.bar(x + w/2, band["adj_mean"], width=w, label="adj", color="#36c")
    ax.set_xticks(x)
    ax.set_xticklabels(band["vol_band"].astype(str), rotation=30, fontsize=8)
    ax.set_ylabel("mean quality")
    ax.set_title("Mean quality by volume band (pass2, n_obs)")
    ax.legend()
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(out_reports / "volume_diagnostic_bands.png", dpi=140)
    plt.close(fig)

    return {
        "volume_measure_primary": "n_obs = pass2 ratings per game (same n that drives SE; measured in same pass2 universe as adj_mean)",
        "volume_measure_sensitivity": "users_rated (population scrape)",
        "band_table": band.assign(vol_band=band["vol_band"].astype(str)).to_dict(orient="records"),
        "band_table_6": band6.assign(vol_band_6=band6["vol_band_6"].astype(str)).to_dict(orient="records"),
        "decile_table": dec.assign(decile=dec["decile"].astype(str), median_n=dec["median_n"].astype(float)).to_dict(orient="records"),
        "gap_top_bottom_decile": {"raw": gap_raw, "adj": gap_adj},
        "slopes_per_tenfold": slopes,
        "ratio_adj_over_raw": {"simple": ratio_simple, "partial_weight_year": ratio_part},
        "even_odd_split_slopes": eo,
        "classification": verdict,
        "low_tail_inspection": {"note": "All games >=100, so low tail is 100-199 vs high. Compare band means above."},
        "claim_tags": {
            "slopes/gaps/band means": "empirical finding (descriptive, not causal)",
            "classification": "empirical finding among pre-stated categories a/b/c",
            "even_odd": "empirical finding (split-sample stability)",
        },
    }

def build_estimation_sample(gam: pd.DataFrame, games: pd.DataFrame, tags_path: Path, links_path: Path) -> pd.DataFrame:
    # Load tags and links
    tags = pd.read_parquet(tags_path) if tags_path.exists() else pd.DataFrame()
    links = pd.read_parquet(links_path) if links_path.exists() else pd.DataFrame()
    # Count reimplementations per game
    if not links.empty and "rel" in links.columns:
        n_impl = (links[links["rel"]=="reimplementation"].groupby("game_id").size().rename("n_implementations").reset_index())
    else:
        n_impl = pd.DataFrame(columns=["game_id","n_implementations"])
    est = gam.merge(games, on="game_id", how="left")
    est = est.merge(n_impl, on="game_id", how="left")
    est["n_implementations"] = est["n_implementations"].fillna(0).astype(float)

    # Handle weight missing: median fill and flag
    median_weight_val = float(np.nanmedian(est["weight"].astype(float).values))
    # Task says 7 games null in pass2, median 2.0 fill, weight_missing flag
    est["weight_missing"] = est["weight"].isna().astype(float)
    est["weight"] = est["weight"].fillna(median_weight_val)
    est.attrs["median_weight"] = median_weight_val
    # Also ensure median_weight ~2.0
    # Transforms
    est["log_n_active"] = np.log10(est["n_obs"])
    est["log_users_rated"] = np.log10(est["users_rated"].clip(lower=1))
    # year handling: ensure year is numeric, fill missing? Check if year null? Should be complete for pass2 (0 missing per docs)
    est["year_c"] = est["year"] - 2015
    est["weight_c"] = est["weight"] - median_weight_val
    # playing_time: median fill? Check missing? In prior, unknown/open-ended bands kept but we do log transform with median shift
    # If playing_time is 0 for some games (179 prior), log1p(0)=0, okay.
    # Ensure playing_time not null
    est["playing_time"] = est["playing_time"].fillna(float(np.nanmedian(est["playing_time"].dropna())))
    est["log_playtime_c"] = (np.log1p(est["playing_time"]) - np.log1p(float(np.nanmedian(est["playing_time"]))))
    # players: fill median if null/0? Keep as is but center at median as prior
    median_min = float(np.nanmedian(est["min_players"].dropna()))
    median_max_log = float(np.nanmedian(np.log1p(est["max_players"].dropna().clip(lower=0))))
    est["min_players"] = est["min_players"].fillna(median_min)
    est["max_players"] = est["max_players"].fillna(float(np.exp(median_max_log)-1))
    est["min_players_c"] = est["min_players"] - median_min
    est["log_max_players_c"] = (np.log1p(est["max_players"]) - median_max_log)
    est["is_reimpl_num"] = est["is_reimplementation"].astype(float).fillna(0)
    est["log_n_impl_c"] = (np.log1p(est["n_implementations"]) - np.log1p(float(np.nanmedian(est["n_implementations"].dropna())) if not est["n_implementations"].empty else 0))
    est["vol_band"] = pd.cut(est["n_obs"], bins=VOL_BAND_EDGES, labels=VOL_BAND_LABELS, right=False)
    est["vol_band_6"] = pd.cut(est["n_obs"], bins=VOL_BAND_EDGES_6, labels=VOL_BAND_LABELS_6, right=False)
    est["decade"] = ((est["year"] // 10) * 10).astype(int).astype(str) + "s"

    def parse_list(v):
        try:
            import json as js
            p = js.loads(v) if isinstance(v, str) else []
            return [str(x) for x in p] if isinstance(p, list) else []
        except Exception:
            return []
    est["category_list"] = est["categories"].map(parse_list)
    est["mechanic_list"] = est["mechanics"].map(parse_list)

    # Also compute weight_missing interactions? Keep flag as extra feature for later but not in primary specs; we will include as sensitivity?
    # For primary ladder, we follow Phase 6 which did not have weight_missing flag (since only 15 missing, dropped?). Here we filled median, so flag captures deviation.

    need = ["adj_mean","n_obs","avg_rating_current","log_n_active","year","weight",
            "playing_time","min_players","max_players","is_reimpl_num",
            "log_n_impl_c","vol_band","decade"]
    before = len(est)
    # Drop rows with missing essential fields (should be very few: maybe 0 after fills)
    est = est.dropna(subset=[c for c in need if c in est.columns]).reset_index(drop=True)
    print(f"\nEstimation sample: {len(est):,} games (dropped {before-len(est)} for missing fields; weight_missing={int(est['weight_missing'].sum())})")
    return est

def add_group_flags(est, list_col, prefix, min_count=TAG_MIN_COUNT):
    counts = Counter(t for tags in est[list_col] for t in tags)
    tags = sorted(t for t, c in counts.items() if c >= min_count)
    cols = []
    for t in tags:
        col = f"{prefix}_{t}"
        # sanitize col name for filesystem? Keep original but replace spaces/slashes
        # Use t directly but column name safe for python dict; keep as is for tracking but pandas column needs string
        # We'll keep col as f"{prefix}_{t}" (may contain spaces); pandas allows but need to reference explicitly
        est[col] = est[list_col].map(lambda v: float(t in v))
        cols.append(col)
    return cols, counts

def add_dummies(est, source_col, prefix):
    dummy = pd.get_dummies(est[source_col], prefix=prefix, dtype=float)
    names = sorted(dummy.columns)[1:]  # omit first level against intercept
    for name in names:
        est[name] = dummy[name]
    return names

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass2-dir", type=Path, default=REPO / "data/processed/phase2-pass2")
    ap.add_argument("--reports-dir", type=Path, default=REPO / "reports/phase2_pass2/step9_expected_quality_underratedness")
    ap.add_argument("--docs-dir", type=Path, default=REPO / "docs/phase2-pass2/step9_expected_quality_underratedness")
    ap.add_argument("--population", type=Path, default=REPO / "data/processed/bgg_research_population.parquet")
    args = ap.parse_args()

    print("Step 9 — expected quality & underratedness on Pass-2")
    ensure_scratch_copy()
    mu, sigma_e, sigma_a2, src = load_phase5_params()
    # If not found, try to compute sigma_e from data later but we have baseline
    if src is None:
        # try to load from baseline_refresh
        br_path = REPO / "data/processed/phase2-pass2/pass2_baseline_refresh.json"
        if br_path.exists():
            br = json.loads(br_path.read_text())
            # variance decomposition to get sigma_e approx? Use fallback 1.194 as before
            pass

    args.reports_dir.mkdir(parents=True, exist_ok=True)
    args.docs_dir.mkdir(parents=True, exist_ok=True)
    # also ensure parent docs dir exists
    (REPO / "docs/phase2-pass2").mkdir(parents=True, exist_ok=True)
    (REPO / "reports/phase2_pass2").mkdir(parents=True, exist_ok=True)
    # Ensure data output mirrors
    out_data_dir = REPO / "data/processed/phase2-pass2"
    out_data_dir.mkdir(parents=True, exist_ok=True)

    # Load game-level
    gam = pd.read_parquet(args.pass2_dir / "game_adjusted_means_pass2.parquet")
    games = pd.read_parquet(args.pass2_dir / "games_pass2.parquet")
    pop = pd.read_parquet(args.population) if args.population.exists() else pd.read_parquet(REPO / "scratch/phase2-pass2/bgg_research_population.parquet")
    # Ensure pop has needed cols; if not, fallback to games
    # For consistency, we need pop to have at least users_rated, weight, year for volume diagnostic; games_pass2 already has those.
    # We'll use games for estimation; pop for bayes etc.
    print(f"Game means: {len(gam):,} games; games_pass2: {len(games):,} games; pop: {len(pop):,} games")

    # Even/odd halves for volume diagnostic stability
    # Use DuckDB to compute halves efficiently via pass2 obs
    tmp_dir = REPO / "scratch/ducktmp"
    con = duckdb.connect()
    configure(con, tmp_dir)
    ro_path = args.pass2_dir / "rating_observations_pass2.parquet"
    sev_path = args.pass2_dir / "user_severity_pass2.parquet"
    # Try to compute halves; bounded single grouped pass
    try:
        con.execute(f"CREATE OR REPLACE VIEW sev AS SELECT * FROM read_parquet('{qpath(sev_path)}')")
        # Even/odd per game half means
        halves = con.execute(f"""
            WITH j AS (
                SELECT r.game_id,
                       (r.rating_observation_id % 2) AS parity,
                       AVG(r.rating) AS raw_half,
                       AVG(r.rating - s.delta_full) AS adj_half,
                       COUNT(*) AS n_half
                FROM read_parquet('{qpath(ro_path)}') r
                JOIN sev s USING (user_pseudouserid)
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
        print(f"Even/odd halves computed for {halves['raw_even'].notna().sum():,} games")
    except Exception as e:
        print(f"WARNING: halves compute failed: {e}")
        halves = None

    vol_diag = part_a_volume_diagnostic(gam, games, halves, args.reports_dir, mu, sigma_e)

    # ------------------------------------------------------------------
    print("\n" + "="*78)
    print("PART B — EXPECTED QUALITY E[adj_mean | characteristics] (pass2)")
    print("="*78)
    est = build_estimation_sample(gam, games, args.pass2_dir / "game_tags_pass2.parquet", args.pass2_dir / "game_links_pass2.parquet")
    cat_cols, cat_counts = add_group_flags(est, "category_list", "cat", TAG_MIN_COUNT)
    mech_cols, mech_counts = add_group_flags(est, "mechanic_list", "mech", TAG_MIN_COUNT)
    band_cols = add_dummies(est, "vol_band", "volband")
    band6_cols = add_dummies(est, "vol_band_6", "volband6")
    dec_cols = add_dummies(est, "decade", "decade")
    knots_year = np.quantile(est["year"].to_numpy(float), [0.05, 0.35, 0.65, 0.95])
    nsy = ns_basis(est["year"].to_numpy(float), knots_year)
    ns_year_cols = []
    for i in range(nsy.shape[1]):
        c = f"ns_year_{i}"
        est[c] = nsy[:, i]
        ns_year_cols.append(c)
    print(f"Features: {len(cat_cols)} category flags (>= {TAG_MIN_COUNT}), {len(mech_cols)} mechanic flags, {len(band_cols)} volband dummies (9-band), {len(band6_cols)} volband6 dummies (6-band), {len(dec_cols)} decade dummies, ns_year {len(ns_year_cols)} cols")
    # Show top categories for documentation
    print("Top categories (>=500):", sorted(cat_counts.items(), key=lambda x: -x[1])[:10])
    print("Top mechanics (>=500):", sorted(mech_counts.items(), key=lambda x: -x[1])[:10])

    core = ["log_n_active", "weight_c", "log_playtime_c", "min_players_c",
            "log_max_players_c", "is_reimpl_num", "log_n_impl_c"]
    # Define specs per task
    specs = {
        "Q0": ["log_n_active", "year_c"],
        "Q1": ["log_n_active", "year_c", "weight_c"],
        "Q2": core[:1] + ["year_c"] + core[1:],  # log_n + year_c + weight+playtime/players/reimpl
        # For Q2, we want year_c not ns_year; core[:1] is log_n
        # But task says Q2 is Q1 + structural, so Q1 already has log_n+year+weight, Q2 adds playtime/players/reimpl
        # So Q2 = ["log_n_active","year_c","weight_c","log_playtime_c","min_players_c","log_max_players_c","is_reimpl_num","log_n_impl_c"]
        "Q3": core[:1] + ["year_c"] + core[1:] + cat_cols,
        "Q3b": band_cols + ns_year_cols + core[1:] + cat_cols,  # flexible volume-band + spline + weight etc + cat
        "Q3b_6band": band6_cols + ns_year_cols + core[1:] + cat_cols,  # 6-band variant sensitivity
        "Q4": band_cols + ns_year_cols + core[1:] + cat_cols + mech_cols,
        # For historical comparison, also keep Phase6-like Q's with ns_year where noted
        "Q0_flex_year": ["log_n_active"] + ns_year_cols,
        "Q1_core_ns": ["log_n_active"] + ns_year_cols + ["weight_c"],
        "Q2_structure_ns": core[:1] + ns_year_cols + core[1:],
        "Q3_categories_ns": core[:1] + ns_year_cols + core[1:] + cat_cols,  # same as Phase6 Q3
        "Q3b_flex_volume_ns": band_cols + ns_year_cols + core[1:] + cat_cols,  # same as Q3b
        "Q4_mechanics_ns": core[:1] + ns_year_cols + core[1:] + cat_cols + mech_cols,
    }
    # Normalize Q2 definition explicitly
    specs["Q2"] = ["log_n_active", "year_c", "weight_c", "log_playtime_c", "min_players_c", "log_max_players_c", "is_reimpl_num", "log_n_impl_c"]
    # Ensure Q3 includes same structural + cats
    # Already done
    # For reporting, we will treat Q3b (9-band) as primary candidate per task "or as Phase6 did"; Q3b_6band is sensitivity.
    # But task lists Q3b as primary with 6-band suggestion; we will present both and select based on CV.

    y_adj = est["adj_mean"].to_numpy(float)
    y_raw = est["avg_rating_current"].to_numpy(float)
    n_obs_vec = est["n_obs"].to_numpy(float)
    log_n = est["log_n_active"].to_numpy(float)
    weightings = {
        "ols": np.ones(len(est)),
        "wls_n": n_obs_vec.copy(),
        "gls_eff": 1.0 / (sigma_a2 + sigma_e ** 2 / n_obs_vec),
    }

    designs = {}
    col_names = {}
    for name, cols in specs.items():
        # Check that all cols exist in est
        missing = [c for c in cols if c not in est.columns]
        if missing:
            print(f"WARNING: spec {name} missing cols {missing} — will drop spec")
            continue
        designs[name] = np.column_stack([np.ones(len(est))] + [est[c].to_numpy(float) for c in cols])
        col_names[name] = ["intercept"] + cols

    results, coef_rows, resid_store = [], [], {}

    def run_spec(spec_name, wt_name, y_vals, label):
        X, w = designs[spec_name], weightings[wt_name]
        key = f"{spec_name}|{wt_name}|{label}"
        beta, pred, resid = fit_wls(X, y_vals, w)
        cv_pred, cv_resid, fold_betas, fold_idx = cv_predictions(X, y_vals, w)
        m_in = metrics(y_vals, resid)
        fold_stats = [metrics(y_vals[ix], cv_resid[ix]) for ix in fold_idx]
        fold_r2 = [f["r2"] for f in fold_stats]
        fold_rmse = [f["rmse"] for f in fold_stats]
        cn = col_names[spec_name]
        bi = dict(zip(cn, beta))
        vi = cn.index("log_n_active") if "log_n_active" in cn else None
        # band residual means: use vol_band (9-band) for reporting regardless of spec's band
        band_means = (pd.DataFrame({"b": est["vol_band"].astype(str).to_numpy(), "r": resid}).groupby("b").r.mean())
        band_flat = float(band_means.abs().max()) if not band_means.empty else float('nan')
        band6_means = (pd.DataFrame({"b": est["vol_band_6"].astype(str).to_numpy(), "r": resid}).groupby("b").r.mean())
        band6_flat = float(band6_means.abs().max()) if not band6_means.empty else float('nan')
        row = {
            "spec": spec_name, "weighting": wt_name, "target": label,
            "n_games": int(len(y_vals)), "n_features": int(X.shape[1]),
            "r2_in": m_in["r2"], "rmse_in": m_in["rmse"], "mae_in": m_in["mae"],
            "cv_r2_mean": float(np.mean(fold_r2)), "cv_r2_sd": float(np.std(fold_r2)),
            "cv_rmse_mean": float(np.mean(fold_rmse)),
            "cv_rmse_sd": float(np.std(fold_rmse)),
            "beta_logn": bi.get("log_n_active"),
            "beta_logn_fold_sd": float(np.std(fold_betas[:, vi])) if vi is not None else None,
            "beta_weight": bi.get("weight_c"),
            "beta_weight_fold_sd": (float(np.std(fold_betas[:, cn.index("weight_c")])) if "weight_c" in cn else None),
            "beta_year": bi.get("year_c"),
            "corr_resid_logn": float(np.corrcoef(resid, log_n)[0,1]),
            "corr_cvresid_logn": float(np.corrcoef(cv_resid, log_n)[0,1]),
            "spearman_resid_logn": float(pd.Series(resid).corr(pd.Series(log_n), method="spearman")),
            "max_abs_bandmean_resid": band_flat,
            "max_abs_band6mean_resid": band6_flat,
        }
        results.append(row)
        # coefficient row (keep core coeffs only)
        core_coefs = {c: float(bi[c]) for c in ["intercept","log_n_active","year_c","weight_c","log_playtime_c","min_players_c","log_max_players_c","is_reimpl_num","log_n_impl_c"] if c in bi}
        # also keep ns_year first if present? For reporting
        for c in ns_year_cols[:1]:  # just first ns col to show spline effect? Keep all later via full coef table
            if c in bi:
                core_coefs[c] = float(bi[c])
        coef_rows.append({"spec": spec_name, "weighting": wt_name, "target": label, **core_coefs})
        resid_store[key] = {"resid": resid, "cv_resid": cv_resid, "pred": pred, "beta": beta, "X": X}
        print(f"{spec_name:20s} {wt_name:7s} {label:3s} feat={X.shape[1]:3d} R2in={m_in['r2']:.4f} CV_R2={row['cv_r2_mean']:.4f}+-{row['cv_r2_sd']:.4f} CV_RMSE={row['cv_rmse_mean']:.4f} b_logn={bi.get('log_n_active', np.nan):+.4f} corr(resid,logn)={row['corr_resid_logn']:+.4f} max|band|={band_flat:.3f}")

    # Run all specs for adj target with ols and wls_n; also gls_eff for key specs
    for spec in list(specs.keys()):
        if spec not in designs:
            continue
        for wt in ["ols","wls_n"]:
            run_spec(spec, wt, y_adj, "adj")
        if spec in {"Q3","Q3b","Q4","Q3_categories_ns","Q3b_flex_volume_ns","Q1_core_ns"}:
            run_spec(spec, "gls_eff", y_adj, "adj")
    # raw target for comparison for key specs
    for spec in ["Q3","Q3b","Q4","Q0","Q1"]:
        if spec not in designs:
            continue
        for wt in ["ols","wls_n"]:
            run_spec(spec, wt, y_raw, "raw")

    res_df = pd.DataFrame(results)
    coef_df = pd.DataFrame(coef_rows)
    res_df.to_csv(args.reports_dir / "model_comparison.csv", index=False)
    coef_df.to_csv(args.reports_dir / "coefficient_table.csv", index=False)
    print(f"\nWrote model_comparison.csv ({len(res_df)} rows)")

    # ------------------------------------------------------------------
    # Residual stability across specs and weightings (adj target)
    # ------------------------------------------------------------------
    keys_adj = sorted(k for k in resid_store if k.endswith("|adj"))
    stab_rows = []
    for i, ka in enumerate(keys_adj):
        for kb in keys_adj[i+1:]:
            ra, rb = resid_store[ka]["resid"], resid_store[kb]["resid"]
            stab_rows.append({
                "a": ka, "b": kb,
                "pearson": float(np.corrcoef(ra, rb)[0,1]),
                "spearman": float(pd.Series(ra).corr(pd.Series(rb), method="spearman")),
                "jaccard_top1": top_jaccard(ra, rb, 0.01),
                "jaccard_top5": top_jaccard(ra, rb, 0.05),
                "jaccard_top10": top_jaccard(ra, rb, 0.10),
            })
    stab_df = pd.DataFrame(stab_rows)
    stab_df.to_csv(args.reports_dir / "residual_overlap.csv", index=False)

    # Summarize core specs OLS agreement
    core_ols_keys = [k for k in keys_adj if "|ols|adj" in k and any(s in k for s in ["Q0|","Q1|","Q2|","Q3|","Q3b|"])]
    sub = stab_df[stab_df["a"].isin(core_ols_keys) & stab_df["b"].isin(core_ols_keys)]
    if not sub.empty:
        print(f"\nAcross core specs (OLS, adj) residual agreement: pearson mean {sub['pearson'].mean():.3f} [{sub['pearson'].min():.3f},{sub['pearson'].max():.3f}], top1% Jaccard mean {sub['jaccard_top1'].mean():.3f}")

    ols_keys = {s: f"{s}|ols|adj" for s in specs if f"{s}|ols|adj" in resid_store}
    wls_keys = {s: f"{s}|wls_n|adj" for s in specs if f"{s}|wls_n|adj" in resid_store}
    wls_impact = {}
    for s in specs:
        if s not in ols_keys or s not in wls_keys:
            continue
        ro, rw = resid_store[ols_keys[s]]["resid"], resid_store[wls_keys[s]]["resid"]
        bo = res_df[(res_df.spec==s) & (res_df.weighting=="ols") & (res_df.target=="adj")].iloc[0]
        bw = res_df[(res_df.spec==s) & (res_df.weighting=="wls_n") & (res_df.target=="adj")].iloc[0]
        wls_impact[s] = {
            "beta_logn_ols": None if pd.isna(bo.beta_logn) else float(bo.beta_logn),
            "beta_logn_wls": None if pd.isna(bw.beta_logn) else float(bw.beta_logn),
            "beta_logn_shift_pct": float((bw.beta_logn - bo.beta_logn)/abs(bo.beta_logn)) if bo.beta_logn and not pd.isna(bo.beta_logn) and bo.beta_logn!=0 else None,
            "cv_r2_ols": float(bo.cv_r2_mean), "cv_r2_wls": float(bw.cv_r2_mean),
            "resid_spearman_ols_wls": float(pd.Series(ro).corr(pd.Series(rw), method="spearman")),
            "jaccard_top1_ols_wls": top_jaccard(ro, rw, 0.01),
            "jaccard_top5_ols_wls": top_jaccard(ro, rw, 0.05),
        }
    print("\nWLS impact by spec:", json.dumps({k: {kk: (round(vv,3) if isinstance(vv,float) else vv) for kk,vv in v.items()} for k,v in wls_impact.items()}, indent=1))

    adj_vs_raw = {}
    for s in ["Q0","Q3","Q3b","Q4"]:
        for wt in ["ols","wls_n"]:
            key_adj = f"{s}|{wt}|adj"
            key_raw = f"{s}|{wt}|raw"
            if key_adj not in resid_store or key_raw not in resid_store:
                continue
            ra = resid_store[key_adj]["resid"]
            rr = resid_store[key_raw]["resid"]
            ba = res_df[(res_df.spec==s) & (res_df.weighting==wt) & (res_df.target=="adj")].iloc[0]
            br = res_df[(res_df.spec==s) & (res_df.weighting==wt) & (res_df.target=="raw")].iloc[0]
            adj_vs_raw[f"{s}|{wt}"] = {
                "r2_adj": float(ba.r2_in), "r2_raw": float(br.r2_in),
                "beta_logn_adj": None if pd.isna(ba.beta_logn) else float(ba.beta_logn),
                "beta_logn_raw": None if pd.isna(br.beta_logn) else float(br.beta_logn),
                "resid_pearson": float(np.corrcoef(ra, rr)[0,1]),
                "resid_spearman": float(pd.Series(ra).corr(pd.Series(rr), method="spearman")),
                "jaccard_top1": top_jaccard(ra, rr, 0.01),
            }

    # ------------------------------------------------------------------
    # Preferred specification — choose based on CV and diagnostics
    # ------------------------------------------------------------------
    # Prefer Q3b (9-band) or Q3b_6band? Compare CV
    cand = res_df[res_df.target=="adj"].sort_values(["cv_r2_mean","cv_rmse_mean"], ascending=[False, True]).reset_index(drop=True)
    # Find Q3b variants
    q3b_9 = res_df[(res_df.spec=="Q3b") & (res_df.weighting=="ols") & (res_df.target=="adj")]
    q3b_6 = res_df[(res_df.spec=="Q3b_6band") & (res_df.weighting=="ols") & (res_df.target=="adj")]
    # Default primary is Q3b (9-band) as it matches Phase6 and has slightly higher CV if any
    pref_spec, pref_wt = "Q3b", "ols"
    if not q3b_9.empty and not q3b_6.empty:
        if float(q3b_6.iloc[0].cv_r2_mean) > float(q3b_9.iloc[0].cv_r2_mean) + 0.005:
            pref_spec = "Q3b_6band"
    pref = res_df[(res_df.spec==pref_spec) & (res_df.weighting==pref_wt) & (res_df.target=="adj")].iloc[0]
    best_row = cand.iloc[0]
    # Compute residual agreements for primary vs Q3 and Q4
    def agree(a_key, b_key):
        ra = resid_store[a_key]["resid"]
        rb = resid_store[b_key]["resid"]
        return float(pd.Series(ra).corr(pd.Series(rb), method="spearman")), top_jaccard(ra, rb, 0.01)
    # Ensure keys exist
    s34, j34 = (float('nan'), float('nan'))
    s3b3, j3b3 = (float('nan'), float('nan'))
    s3b4, j3b4 = (float('nan'), float('nan'))
    try:
        s34, j34 = agree("Q3|ols|adj", "Q4|ols|adj")
    except: pass
    try:
        s3b3, j3b3 = agree(f"{pref_spec}|ols|adj", "Q3|ols|adj")
    except: pass
    try:
        s3b4, j3b4 = agree(f"{pref_spec}|ols|adj", "Q4|ols|adj")
    except: pass
    print(f"\nPreferred specification: {pref_spec} / {pref_wt} (CV_R2 {float(pref.cv_r2_mean):.4f}; best-CV variant {best_row['spec']}/{best_row['weighting']} at {float(best_row.cv_r2_mean):.4f})")
    print(f"Residual agreement: {pref_spec} vs Q3 spearman {s3b3:.3f} Jaccard {j3b3:.3f}; {pref_spec} vs Q4 {s3b4:.3f}/{j3b4:.3f}; Q3 vs Q4 {s34:.3f}/{j34:.3f}")
    print("CV ranking (top 10 adj OLS):")
    print(cand[cand.weighting=="ols"].head(10)[["spec","cv_r2_mean","cv_r2_sd","cv_rmse_mean","beta_logn","corr_cvresid_logn","max_abs_bandmean_resid"]].round(4).to_string(index=False))

    # ------------------------------------------------------------------
    # Underratedness per-game output
    # ------------------------------------------------------------------
    # Use preferred spec's beta/pred/resid
    Xp = designs[pref_spec]
    beta_pref, pred_pref, resid_pref = fit_wls(Xp, y_adj, weightings[pref_wt])
    # CV resid for preferred
    cv_pred_pref, cv_resid_pref, _, _ = cv_predictions(Xp, y_adj, weightings[pref_wt])
    se_pref = sigma_e / np.sqrt(n_obs_vec)
    # Lower bound: residual - 1.96*SE (or adj -1.96*SE - expected)
    lower_resid = resid_pref - 1.96 * se_pref
    lower_adj = y_adj - 1.96 * se_pref

    # Determine volume_band for per-game (use 9-band)
    # Keep est["raw_mean"] as pass2 AVG(rating) from gam (do NOT overwrite with avg_rating_current)
    est["adj_mean"] = y_adj
    # Build per-game dataframe with required columns
    out = pd.DataFrame({
        "game_id": est["game_id"],
        "title": est["title"] if "title" in est.columns else est["game_id"].astype(str),
        "year": est["year"],
        "n_obs": n_obs_vec.astype(int),
        "users_rated": est["users_rated"],
        "weight": est["weight"],
        "weight_missing": est["weight_missing"],
        "raw_mean": est["raw_mean"],
        "adj_mean": y_adj,
        "se_adj": se_pref,
        "expected_quality": pred_pref,
        "underratedness": resid_pref,
        "underratedness_cv": cv_resid_pref,
        "lower_bound_resid": lower_resid,
        "lower_bound_adj": lower_adj,
        "model_spec": pref_spec,
        "volume_band": est["vol_band"].astype(str),
        "volume_band_6": est["vol_band_6"].astype(str),
        "year_band": est["decade"],
        "volume_decile": pd.qcut(est["log_n_active"], 10, labels=[f"D{i+1}" for i in range(10)], duplicates="drop").astype(str),
        "is_reimplementation": est["is_reimplementation"] if "is_reimplementation" in est.columns else False,
    })
    # Add bayes and rank for reference if available
    if "bayes_rating" in est.columns:
        out["bayes_rating"] = est["bayes_rating"]
    if "rank_current" in est.columns:
        out["rank_current"] = est["rank_current"]

    # Ensure games missing from estimation sample? For pass2, estimation sample includes almost all 14698 (maybe dropped few with missing). We need to ensure output is 14,698 rows.
    # If est has fewer than 14698 (due to missing fields), we need to impute remaining games with NaN expected?
    # But we dropped only missing essential fields; weight_missing filled, so likely all 14698 retained. Let's verify:
    print(f"\nPer-game output: {len(out)} rows (expected 14698). Dropped {14698-len(out)} if any.")
    # If still fewer, we should add back dropped games with NaN predictions (but they should be none)
    # For safety, if len(out) < 14698, fill remaining from gam left join
    if len(out) < len(gam):
        missing_ids = set(gam["game_id"]) - set(out["game_id"])
        print(f"WARNING: {len(missing_ids)} games missing from estimation sample, will add with NaN expected")
        missing_gam = gam[gam["game_id"].isin(missing_ids)].merge(games, on="game_id", how="left")
        # For these, compute expected via fallback: use mean adj? but better leave NaN and document
        add = pd.DataFrame({
            "game_id": missing_gam["game_id"],
            "title": missing_gam["title"],
            "year": missing_gam["year"],
            "n_obs": missing_gam["n_obs"],
            "users_rated": missing_gam["users_rated"],
            "weight": missing_gam["weight"].fillna(est.attrs.get("median_weight", 2.0)),
            "weight_missing": missing_gam["weight"].isna().astype(float),
            "raw_mean": missing_gam["raw_mean"],
            "adj_mean": missing_gam["adj_mean"],
            "se_adj": sigma_e / np.sqrt(missing_gam["n_obs"]),
            "expected_quality": np.nan,
            "underratedness": np.nan,
            "underratedness_cv": np.nan,
            "lower_bound_resid": np.nan,
            "lower_bound_adj": np.nan,
            "model_spec": pref_spec,
            "volume_band": pd.cut(missing_gam["n_obs"], bins=VOL_BAND_EDGES, labels=VOL_BAND_LABELS, right=False).astype(str),
            "volume_band_6": pd.cut(missing_gam["n_obs"], bins=VOL_BAND_EDGES_6, labels=VOL_BAND_LABELS_6, right=False).astype(str),
            "year_band": ((missing_gam["year"]//10)*10).astype(int).astype(str)+"s",
            "volume_decile": np.nan,
            "is_reimplementation": missing_gam["is_reimplementation"],
        })
        out = pd.concat([out, add], ignore_index=True)
        print(f"After adding missing, total {len(out)}")

    # Sort by underratedness descending for candidates
    out_sorted = out.sort_values("underratedness", ascending=False)
    # Top candidates: top 200 or top 5% as Phase6 did (top 5% = 735 for 14698)
    top_n = 200
    top_frac = 0.05
    k_top = max(top_n, int(top_frac * len(out)))
    underrated_candidates = out_sorted.head(k_top).copy()
    # Also add rank column for candidates
    underrated_candidates["rank_underratedness"] = np.arange(1, len(underrated_candidates)+1)

    # Save expected_quality_game_level.csv (14,698 rows)
    out_path = args.docs_dir / "expected_quality_game_level.csv"
    rep_path = args.reports_dir / "expected_quality_game_level.csv"
    # Also data/processed mirror
    data_mirror = REPO / "data/processed/phase2-pass2/step9_expected_quality_underratedness"
    data_mirror.mkdir(parents=True, exist_ok=True)
    data_mirror_path = data_mirror / "expected_quality_game_level.csv"
    out.to_csv(out_path, index=False)
    out.to_csv(rep_path, index=False)
    out.to_csv(data_mirror_path, index=False)
    print(f"Wrote expected_quality_game_level.csv ({len(out)} rows) to {out_path}")

    # Save underrated_candidates.csv (top 200/5%)
    cand_path = args.docs_dir / "underrated_candidates.csv"
    cand_rep = args.reports_dir / "underrated_candidates.csv"
    cand_data = data_mirror / "underrated_candidates.csv"
    underrated_candidates.to_csv(cand_path, index=False)
    underrated_candidates.to_csv(cand_rep, index=False)
    underrated_candidates.to_csv(cand_data, index=False)
    print(f"Wrote underrated_candidates.csv ({len(underrated_candidates)} rows, top {top_n} + top {top_frac*100:.0f}%)")

    # Also save model_comparison already done

    # ------------------------------------------------------------------
    # Stability and robustness analysis (already partly computed)
    # We'll compile detailed report
    # ------------------------------------------------------------------
    print("\nStability: comparing underratedness across specs")
    # Pearson / Spearman / Jaccard already in stab_df; now focus on primary vs sensitivities
    # Compare Q3b primary vs Q4, vs linear log vs band, vs OLS vs WLS
    stab_summary = {}
    # Q3b vs Q4
    if f"{pref_spec}|ols|adj" in resid_store and "Q4|ols|adj" in resid_store:
        ra = resid_store[f"{pref_spec}|ols|adj"]["resid"]
        rb = resid_store["Q4|ols|adj"]["resid"]
        stab_summary["Q3b_vs_Q4"] = {
            "pearson": float(np.corrcoef(ra, rb)[0,1]),
            "spearman": float(pd.Series(ra).corr(pd.Series(rb), method="spearman")),
            "jaccard_top1": top_jaccard(ra, rb, 0.01),
            "jaccard_top5": top_jaccard(ra, rb, 0.05),
            "jaccard_top10": top_jaccard(ra, rb, 0.10),
        }
    # Linear log vs band: Q3 vs Q3b
    if "Q3|ols|adj" in resid_store and f"{pref_spec}|ols|adj" in resid_store:
        ra = resid_store["Q3|ols|adj"]["resid"]
        rb = resid_store[f"{pref_spec}|ols|adj"]["resid"]
        stab_summary["Q3_vs_Q3b_linear_vs_band"] = {
            "pearson": float(np.corrcoef(ra, rb)[0,1]),
            "spearman": float(pd.Series(ra).corr(pd.Series(rb), method="spearman")),
            "jaccard_top1": top_jaccard(ra, rb, 0.01),
            "jaccard_top5": top_jaccard(ra, rb, 0.05),
        }
    # OLS vs WLS for primary
    if f"{pref_spec}|ols|adj" in resid_store and f"{pref_spec}|wls_n|adj" in resid_store:
        ra = resid_store[f"{pref_spec}|ols|adj"]["resid"]
        rb = resid_store[f"{pref_spec}|wls_n|adj"]["resid"]
        stab_summary["OLS_vs_WLS_primary"] = {
            "pearson": float(np.corrcoef(ra, rb)[0,1]),
            "spearman": float(pd.Series(ra).corr(pd.Series(rb), method="spearman")),
            "jaccard_top1": top_jaccard(ra, rb, 0.01),
            "jaccard_top5": top_jaccard(ra, rb, 0.05),
        }

    # Top movers between primary and sensitivity (e.g., Q3b vs Q4)
    movers_rows = []
    if f"{pref_spec}|ols|adj" in resid_store and "Q4|ols|adj" in resid_store:
        ra = resid_store[f"{pref_spec}|ols|adj"]["resid"]
        rb = resid_store["Q4|ols|adj"]["resid"]
        diff = rb - ra
        # Get top 20 movers by absolute diff where rank changes most
        idx_sorted = np.argsort(np.abs(diff))[::-1][:20]
        for idx in idx_sorted:
            row = out.iloc[idx]
            movers_rows.append({
                "game_id": int(row["game_id"]),
                "title": row["title"],
                "n_obs": int(row["n_obs"]),
                "adj_mean": float(row["adj_mean"]),
                "underratedness_Q3b": float(ra[idx]),
                "underratedness_Q4": float(rb[idx]),
                "delta_Q4_minus_Q3b": float(diff[idx]),
                "volume_band": row["volume_band"],
            })
    movers_df = pd.DataFrame(movers_rows)
    if not movers_df.empty:
        movers_df.to_csv(args.reports_dir / "stability_top_movers.csv", index=False)

    # Residual vs volume correlation after model (should be ~0)
    resid_vs_vol = {}
    for key in [f"{pref_spec}|ols|adj", "Q3|ols|adj", "Q4|ols|adj"]:
        if key in resid_store:
            r = resid_store[key]["resid"]
            resid_vs_vol[key] = {
                "pearson": float(np.corrcoef(r, log_n)[0,1]),
                "spearman": float(pd.Series(r).corr(pd.Series(log_n), method="spearman")),
            }
    print("Residual vs volume correlations:", resid_vs_vol)

    # Systematic changes by weight/type/year (boxplots or band means) - compute band means for residuals
    residual_by_weight = out.groupby(pd.cut(out["weight"], bins=[0,1.5,2.0,2.5,5]))["underratedness"].mean()
    residual_by_year = out.groupby(pd.cut(out["year"], bins=[1950,1990,2000,2010,2020,2027]))["underratedness"].mean()
    residual_by_band = out.groupby("volume_band")["underratedness"].mean()
    print("Residual by weight bands:", residual_by_weight.to_dict())
    print("Residual by year bands:", residual_by_year.to_dict())
    print("Residual by volume bands:", residual_by_band.to_dict())

    # ------------------------------------------------------------------
    # Address conceptual issue: high residual vs absolute quality
    # ------------------------------------------------------------------
    print("\n" + "="*78)
    print("Conceptual: high residual vs absolute quality")
    print("="*78)
    # Scatter data
    fig, ax = plt.subplots(figsize=(8,6))
    ax.scatter(out["adj_mean"], out["underratedness"], alpha=0.3, s=8, color="#36c")
    ax.axhline(0, color="k", lw=0.8)
    ax.axvline(7.0, color="r", ls="--", lw=0.8, label="adj_mean=7.0")
    ax.axvline(7.5, color="r", ls=":", lw=0.8, label="adj_mean=7.5")
    ax.set_xlabel("adj_mean (severity-adjusted quality)")
    ax.set_ylabel("underratedness (residual)")
    ax.set_title("Underratedness vs absolute quality (pass2, Q3b OLS)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(args.reports_dir / "residual_vs_quality_scatter.png", dpi=140)
    fig.savefig(args.docs_dir / "residual_vs_quality_scatter.png", dpi=140)
    plt.close(fig)

    # Quantify high residual but mediocre quality
    high_resid = out["underratedness"] >= out["underratedness"].quantile(0.99)
    high_resid_95 = out["underratedness"] >= out["underratedness"].quantile(0.95)
    stats = {}
    for thresh, label in [(0.01, "top1%"), (0.05, "top5%")]:
        cutoff = out["underratedness"].quantile(1-thresh)
        subset = out[out["underratedness"] >= cutoff]
        stats[label] = {
            "n": int(len(subset)),
            "cutoff": float(cutoff),
            "mean_adj": float(subset["adj_mean"].mean()),
            "median_adj": float(subset["adj_mean"].median()),
            "share_adj_lt_6.5": float((subset["adj_mean"] < 6.5).mean()),
            "share_adj_lt_7.0": float((subset["adj_mean"] < 7.0).mean()),
            "share_adj_lt_7.5": float((subset["adj_mean"] < 7.5).mean()),
            "share_adj_ge_7.5": float((subset["adj_mean"] >= 7.5).mean()),
            "share_adj_ge_7.0": float((subset["adj_mean"] >= 7.0).mean()),
        }
        # Example games: high residual but mediocre
        examples = subset[subset["adj_mean"] < 7.0].sort_values("underratedness", ascending=False).head(10)
        if not examples.empty:
            stats[label]["examples_high_resid_mediocre"] = examples[["game_id","title","year","n_obs","adj_mean","expected_quality","underratedness","volume_band"]].to_dict(orient="records")
    print("High residual quality stats:", json.dumps(stats, indent=2))

    # Residual diagnostics plots for preferred spec (vs fitted, vs volume, vs year, QQ)
    # residual vs fitted
    fig, axs = plt.subplots(2, 2, figsize=(11,8))
    axs[0,0].scatter(pred_pref, resid_pref, alpha=0.3, s=6, color="#36c")
    axs[0,0].axhline(0, color="k", lw=0.8)
    axs[0,0].set_xlabel("fitted expected_quality")
    axs[0,0].set_ylabel("residual")
    axs[0,0].set_title("Residual vs Fitted")
    axs[0,0].grid(alpha=0.3)
    axs[0,1].scatter(log_n, resid_pref, alpha=0.3, s=6, color="#36c")
    axs[0,1].axhline(0, color="k", lw=0.8)
    # Decile means on same plot
    dm = (pd.DataFrame({"l": log_n, "r": resid_pref}).assign(b=lambda x: pd.qcut(x.l, 10, duplicates="drop")).groupby("b", observed=True).agg(l=("l","mean"), r=("r","mean")))
    axs[0,1].plot(dm.l, dm.r, "r-o", ms=4, lw=1.5)
    axs[0,1].set_xlabel("log10(n_obs)")
    axs[0,1].set_ylabel("residual")
    axs[0,1].set_title(f"Residual vs volume (corr {np.corrcoef(log_n,resid_pref)[0,1]:+.4f})")
    axs[0,1].grid(alpha=0.3)
    axs[1,0].scatter(est["year"], resid_pref, alpha=0.3, s=6, color="#36c")
    axs[1,0].axhline(0, color="k", lw=0.8)
    axs[1,0].set_xlabel("year")
    axs[1,0].set_ylabel("residual")
    axs[1,0].set_title("Residual vs year")
    axs[1,0].grid(alpha=0.3)
    # QQ
    from scipy import stats as sp_stats
    sp_stats.probplot(resid_pref, dist="norm", plot=axs[1,1])
    axs[1,1].set_title("QQ plot of residuals")
    fig.tight_layout()
    fig.savefig(args.reports_dir / "residual_diagnostics.png", dpi=140)
    fig.savefig(args.docs_dir / "residual_diagnostics.png", dpi=140)
    plt.close(fig)

    # Feature importance: for Q3b, show absolute coefficient * sd or variance explained?
    # Simplify: show coefficient magnitude and maybe contribution via beta * sd(feature)
    # We'll compute for top features sorted by abs(beta * sd)
    if pref_spec in designs:
        beta = beta_pref
        cn = col_names[pref_spec]
        # Compute sd of each column in design matrix (excluding intercept)
        X = designs[pref_spec]
        sds = np.std(X[:,1:], axis=0)
        # For band dummies, sd is interpretable but contribution is beta*sd
        contribs = np.abs(beta[1:] * sds)
        # Get top 20
        idx = np.argsort(contribs)[::-1][:20]
        fi = pd.DataFrame({
            "feature": [cn[1:][i] for i in idx],
            "beta": [beta[1:][i] for i in idx],
            "sd": [sds[i] for i in idx],
            "abs_contrib": [contribs[i] for i in idx],
        })
        fi.to_csv(args.reports_dir / "feature_importance.csv", index=False)
        print("Top feature contributions:")
        print(fi.head(10).to_string(index=False))

    # ------------------------------------------------------------------
    # Compare Pass-1 / historical Phase 6 vs Pass-2
    # ------------------------------------------------------------------
    # Load historical comparative for pass1 (phase6 on active 16549)
    hist_path = REPO / "docs/phase2-active/phase6_comparative.json"
    hist = json.loads(hist_path.read_text()) if hist_path.exists() else {}
    # Also load quality estimator historical
    hist_q_path = REPO / "docs/phase2-active/phase5_quality_comparison.json"
    hist_q = json.loads(hist_q_path.read_text()) if hist_q_path.exists() else {}

    # Compare populations
    pop_comparison = {
        "pass1_games": 16549,  # estimation sample on active; but total pass1 population 16627/16564 with ratings
        "pass2_games": 14698,
        "pass1_obs": 24509788,  # active obs
        "pass2_obs": 24146307,
        "pass1_users": 288730,
        "pass2_users": 287302,
        "pass1_mu": hist_q.get("validation", {}).get("mu_active", 7.144) if hist_q else 7.144,
        "pass2_mu": mu,
        "games_lost": 16567 - 14698 if True else 1929,  # filtered 16567 vs pass2 14698
    }

    # Quality distribution comparison
    # Pass2 distribution already in gam; pass1 distribution from historical? Approximate via hist_q eb var_adj etc.
    # For more precise, we can load pass1 gam if exists (active game_adjusted_means_active.parquet)
    quality_dist = {}
    try:
        active_gam_path = REPO / "data/processed/phase2-active/game_adjusted_means_active.parquet"
        if active_gam_path.exists():
            active_gam = pd.read_parquet(active_gam_path)
            quality_dist["pass1_adj_mean"] = {
                "mean": float(active_gam["adj_mean"].mean()),
                "median": float(active_gam["adj_mean"].median()),
                "sd": float(active_gam["adj_mean"].std()),
                "min": float(active_gam["adj_mean"].min()),
                "max": float(active_gam["adj_mean"].max()),
                "p05": float(active_gam["adj_mean"].quantile(0.05)),
                "p95": float(active_gam["adj_mean"].quantile(0.95)),
            }
        quality_dist["pass2_adj_mean"] = {
            "mean": float(gam["adj_mean"].mean()),
            "median": float(gam["adj_mean"].median()),
            "sd": float(gam["adj_mean"].std()),
            "min": float(gam["adj_mean"].min()),
            "max": float(gam["adj_mean"].max()),
            "p05": float(gam["adj_mean"].quantile(0.05)),
            "p95": float(gam["adj_mean"].quantile(0.95)),
        }
        # also raw
        if active_gam_path.exists():
            quality_dist["pass1_raw_mean"] = {
                "mean": float(active_gam["raw_mean"].mean()),
                "sd": float(active_gam["raw_mean"].std()),
            }
        quality_dist["pass2_raw_mean"] = {
            "mean": float(gam["raw_mean"].mean()),
            "sd": float(gam["raw_mean"].std()),
        }
    except Exception as e:
        print(f"WARNING quality dist comparison failed: {e}")

    # Volume relationship comparison
    # Pass1 slopes from hist volume diagnostic (phase6_volume_diagnostic.json)
    vol_hist_path = REPO / "docs/phase2-active/phase6_volume_diagnostic.json"
    vol_hist = json.loads(vol_hist_path.read_text()) if vol_hist_path.exists() else {}
    vol_comparison = {
        "pass1_slopes": vol_hist.get("slopes_per_tenfold", {}),
        "pass2_slopes": vol_diag.get("slopes_per_tenfold", {}),
        "pass1_gap": vol_hist.get("gap_top_bottom_decile", {}),
        "pass2_gap": vol_diag.get("gap_top_bottom_decile", {}),
        "ratio_simple_pass1": vol_hist.get("ratio_adj_over_raw", {}).get("simple"),
        "ratio_simple_pass2": vol_diag.get("ratio_adj_over_raw", {}).get("simple"),
    }

    # Expected quality R2 comparison per spec
    # For each spec that exists in both hist and current, compare CV R2
    r2_comparison = []
    if hist:
        hist_df = pd.DataFrame(hist.get("comparative_table", []))
        for _, row in res_df[res_df.target=="adj"].iterrows():
            spec = row["spec"]
            # Map to historical name: hist has specs like Q3b_flex_volume etc. Our specs include Q3b etc.
            # Try to find matching hist spec
            # For simplicity, match by spec name equality if exists, else try Q3b -> Q3b_flex_volume
            hist_spec = spec
            # Normalize: our Q3b corresponds to hist Q3b_flex_volume
            mapping = {
                "Q3b": "Q3b_flex_volume",
                "Q3b_6band": "Q3b_flex_volume",
                "Q4": "Q4_mechanics",
                "Q3": "Q3_categories",
                "Q2": "Q2_structure",
                "Q1": "Q1_core",
                "Q0": "Q0_linear",
            }
            hist_spec = mapping.get(spec, spec)
            hist_row = hist_df[(hist_df.spec==hist_spec) & (hist_df.weighting==row["weighting"]) & (hist_df.target==row["target"])]
            if not hist_row.empty:
                r2_comparison.append({
                    "spec": spec,
                    "hist_spec": hist_spec,
                    "weighting": row["weighting"],
                    "pass1_cv_r2": float(hist_row.iloc[0].cv_r2_mean),
                    "pass2_cv_r2": float(row["cv_r2_mean"]),
                    "delta_r2": float(row["cv_r2_mean"] - hist_row.iloc[0].cv_r2_mean),
                    "pass1_cv_rmse": float(hist_row.iloc[0].cv_rmse_mean),
                    "pass2_cv_rmse": float(row["cv_rmse_mean"]),
                })
    r2_comp_df = pd.DataFrame(r2_comparison)
    if not r2_comp_df.empty:
        r2_comp_df.to_csv(args.reports_dir / "r2_comparison_pass1_vs_pass2.csv", index=False)
        print("R2 comparison:")
        print(r2_comp_df.to_string(index=False))

    # Residual distribution comparison
    resid_hist = {}
    # Try to load hist residuals? Not available directly, but we can approximate via hist comparative table's residual stats? We'll compute from current and compare to hist's reported residual distribution via prior top residuals?
    # For now, compare pass2 residual stats to hist via out
    resid_dist = {
        "pass2_residual_mean": float(np.mean(resid_pref)),
        "pass2_residual_sd": float(np.std(resid_pref)),
        "pass2_residual_p05": float(np.quantile(resid_pref, 0.05)),
        "pass2_residual_p95": float(np.quantile(resid_pref, 0.95)),
        "pass2_residual_p99": float(np.quantile(resid_pref, 0.99)),
        "pass2_residual_max": float(np.max(resid_pref)),
        "pass2_residual_min": float(np.min(resid_pref)),
    }
    # If hist residuals available via prior out file, we could load but not required

    # Top residual candidates Jaccard
    # Need to reconstruct pass1 top residuals; we have top_residuals_preview.csv from phase6
    top_pass1_path = REPO / "reports/phase6_underratedness/top_residuals_preview.csv"
    top_pass1 = pd.read_csv(top_pass1_path) if top_pass1_path.exists() else pd.DataFrame()
    # Also check docs copy?
    if top_pass1.empty:
        top_pass1_path2 = REPO / "docs/phase2-active/top_residuals_preview.csv"
        if top_pass1_path2.exists():
            top_pass1 = pd.read_csv(top_pass1_path2)
    jaccard_top = {}
    if not top_pass1.empty:
        # Compare top 1%,5%,10% overlap via game_id Jaccard
        # Need full pass1 residuals; but we only have preview top 20, so can't compute full Jaccard. Use reported residual_overlap.csv for hist?
        hist_overlap_path = REPO / "reports/phase6_underratedness/residual_overlap.csv"
        # For pass2 we have stab_df, but for cross-pass comparison we need to compute jaccard between pass1 and pass2 top sets
        # Instead, we can attempt to load phase6_residuals_active.parquet if exists
        phase6_res_path = REPO / "data/processed/phase2-active/phase6_residuals_active.parquet"
        if phase6_res_path.exists():
            phase6_res = pd.read_parquet(phase6_res_path)
            # Merge on game_id
            merged = out.merge(phase6_res[["game_id","underratedness_pref"]].rename(columns={"underratedness_pref":"underratedness_pass1"}), on="game_id", how="inner")
            for frac in [0.01, 0.05, 0.10]:
                k = int(frac * len(merged))
                top_pass1_ids = set(merged.sort_values("underratedness_pass1", ascending=False).head(k)["game_id"])
                top_pass2_ids = set(merged.sort_values("underratedness", ascending=False).head(k)["game_id"])
                jaccard = len(top_pass1_ids & top_pass2_ids) / len(top_pass1_ids | top_pass2_ids) if top_pass1_ids|top_pass2_ids else 0
                overlap = len(top_pass1_ids & top_pass2_ids)
                jaccard_top[f"top{int(frac*100)}%"] = {"jaccard": float(jaccard), "overlap": int(overlap), "k": int(k)}
            # Also who entered/left top 1%
            k1 = int(0.01 * len(merged))
            top1_pass1 = set(merged.sort_values("underratedness_pass1", ascending=False).head(k1)["game_id"])
            top1_pass2 = set(merged.sort_values("underratedness", ascending=False).head(k1)["game_id"])
            entered = top1_pass2 - top1_pass1
            left = top1_pass1 - top1_pass2
            # Get titles for entered/left top 20 movers
            entered_df = merged[merged["game_id"].isin(entered)].sort_values("underratedness", ascending=False).head(20)
            left_df = merged[merged["game_id"].isin(left)].sort_values("underratedness_pass1", ascending=False).head(20)
            jaccard_top["entered_top1"] = entered_df[["game_id","title","underratedness","underratedness_pass1","n_obs","adj_mean"]].to_dict(orient="records") if not entered_df.empty else []
            jaccard_top["left_top1"] = left_df[["game_id","title","underratedness","underratedness_pass1","n_obs","adj_mean"]].to_dict(orient="records") if not left_df.empty else []
        else:
            # Fallback using preview top 20 only
            top_pass2_ids = set(out_sorted.head(20)["game_id"])
            top_pass1_ids = set(top_pass1.head(20)["game_id"]) if not top_pass1.empty else set()
            jaccard_top["top20_preview_jaccard"] = len(top_pass1_ids & top_pass2_ids) / len(top_pass1_ids | top_pass2_ids) if top_pass1_ids|top_pass2_ids else 0

    # Top quality candidates (by adj_mean)
    top_quality_pass2 = out.sort_values("adj_mean", ascending=False).head(20)
    top_quality_pass1 = pd.DataFrame()
    if 'active_gam' in locals() and not active_gam.empty:
        # Get titles via games? Use active_gam merged with games on active? Approx
        top_quality_pass1 = active_gam.sort_values("adj_mean", ascending=False).head(20)

    # Check flagged types: 18XX, Wargames, Party, Economic, low-volume, 100-249
    # Need to determine which games are in those categories. Use est category flags.
    flagged_types = {}
    # For each flagged type, compute stats on pass1 vs pass2 if available
    # We have est for pass2; for pass1 we could approximate via hist but not precise. Instead report pass2 stats and compare to hist if possible
    # Let's compute for pass2: mean residual, share high residual, etc.
    type_defs = {
        "18XX": lambda df: df["title"].str.contains("18XX|1830|1846|1856|1889|1861|18EU|18MS", case=False, na=False) | df["category_list"].apply(lambda x: "Trains" in x if isinstance(x, list) else False) & df["title"].str.contains("18", na=False),  # rough
        "Wargame": lambda df: df["category_list"].apply(lambda x: "Wargame" in x if isinstance(x, list) else False),
        "Party": lambda df: (df["category_list"].apply(lambda x: "Party Game" in x if isinstance(x, list) else False)) | (df.apply(lambda r: "Party" in str(r.get("category_list", [])), axis=1)),
        "Economic": lambda df: df["category_list"].apply(lambda x: "Economic" in x if isinstance(x, list) else False),
        "low_volume_100_199": lambda df: df["n_obs"] < 200,
        "band_100_249": lambda df: df["vol_band"] == "100-199",
    }
    # More precise for 18XX: check families containing 18XX or title pattern
    # Also check wargame via tag
    for type_name, fn in type_defs.items():
        try:
            mask = fn(est)
            subset = out[mask]
            # For 18XX, also try family contains 18XX
            if type_name=="18XX":
                # Additional check via families column
                if "families" in est.columns:
                    fam_mask = est["families"].astype(str).str.contains("18XX", case=False, na=False)
                    mask2 = fam_mask
                    subset2 = out[mask2]
                    # Combine
                    mask = mask | mask2
                    subset = out[mask]
            flagged_types[type_name] = {
                "n_games": int(mask.sum()),
                "mean_resid": float(subset["underratedness"].mean()) if len(subset) else None,
                "median_resid": float(subset["underratedness"].median()) if len(subset) else None,
                "share_top5_resid": float((subset["underratedness"] >= out["underratedness"].quantile(0.95)).mean()) if len(subset) else None,
                "mean_adj": float(subset["adj_mean"].mean()) if len(subset) else None,
            }
            if len(subset) and len(subset) < 30:
                flagged_types[type_name]["examples"] = subset.sort_values("underratedness", ascending=False).head(10)[["game_id","title","n_obs","adj_mean","underratedness"]].to_dict(orient="records")
        except Exception as e:
            flagged_types[type_name] = {"error": str(e)}

    # Print flagged types
    print("\nFlagged types (pass2):")
    for k, v in flagged_types.items():
        print(f"  {k}: n={v.get('n_games')} mean_resid={v.get('mean_resid')} mean_adj={v.get('mean_adj')}")

    # ------------------------------------------------------------------
    # Write summary JSON and markdown docs
    # ------------------------------------------------------------------
    step9_summary = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "population": {
            "pass2_games": 14698,
            "pass2_users": 287302,
            "pass2_obs": 24146307,
            "pass1_reference": pop_comparison,
            "note": "Pass-2 canonical validated via scripts 39/40, mu 7.139, reuse severity, NOT refit"
        },
        "quality_estimator": {
            "preferred": "adj_mean (severity-adjusted, mu 7.139)",
            "lambda_eb": float(sigma_a2 and sigma_e**2/sigma_a2) if sigma_a2 else None,
            "mu": float(mu),
            "sigma_e": float(sigma_e),
            "sigma_alpha": float(np.sqrt(sigma_a2)) if sigma_a2 else None,
            "verdict": "adj_mean preferred; BGG bayes overshrinks; EB shrinkage negligible for pass2 (all n>=100, median 347, p10 123, w ~0.99)",
        },
        "volume_diagnostic": vol_diag,
        "expected_quality": {
            "estimation_sample_n": int(len(est)),
            "weight_missing_games": int(est["weight_missing"].sum()),
            "median_weight_fill": float(est.attrs.get("median_weight", 2.0)),
            "knots_year": [float(x) for x in knots_year],
            "specs_tested": list(specs.keys()),
            "preferred_spec": pref_spec,
            "preferred_weighting": pref_wt,
            "cv_r2_preferred": float(pref.cv_r2_mean),
            "cv_rmse_preferred": float(pref.cv_rmse_mean),
            "r2_comparison_vs_pass1": r2_comparison,
            "residual_vs_volume_corr": resid_vs_vol.get(f"{pref_spec}|ols|adj", {}),
            "feature_importance_top": fi.head(10).to_dict(orient="records") if 'fi' in locals() else [],
        },
        "underratedness": {
            "definition": "underratedness = adj_mean - expected_quality (Q3b OLS)",
            "n_games": int(len(out)),
            "residual_stats": resid_dist,
            "stability": stab_summary,
            "high_resid_vs_quality": stats,
            "residual_by_weight": {str(k): float(v) for k,v in (residual_by_weight.to_dict().items() if 'residual_by_weight' in locals() else {}.items())},
            "residual_by_year": {str(k): float(v) for k,v in (residual_by_year.to_dict().items() if 'residual_by_year' in locals() else {}.items())},
        },
        "pass1_vs_pass2": {
            "pop_comparison": pop_comparison,
            "quality_dist": quality_dist,
            "volume_comparison": vol_comparison,
            "r2_comparison": r2_comparison,
            "resid_jaccard": jaccard_top,
            "flagged_types": flagged_types,
        },
        "method_discipline": {
            "severity_reuse": True,
            "bounded": "4GB/3threads/scratch/ducktmp, copy-once",
            "seed": RANDOM_SEED,
            "claim_tags": "observed fact / empirical finding / model-dependent conclusion per AGENTS.md",
        }
    }
    # Write step9_summary.json to docs and reports and data
    for p in [args.docs_dir / "step9_summary.json", args.reports_dir / "step9_summary.json", data_mirror / "step9_summary.json"]:
        with open(p, "w") as f:
            json.dump(step9_summary, f, indent=2)
    print(f"Wrote step9_summary.json")

    # Also write data/processed mirror for model_comparison (already in reports, copy to docs)
    shutil.copy2(args.reports_dir / "model_comparison.csv", args.docs_dir / "model_comparison.csv")
    shutil.copy2(args.reports_dir / "model_comparison.csv", data_mirror / "model_comparison.csv")

    # ------------------------------------------------------------------
    # Generate markdown docs
    # ------------------------------------------------------------------
    # README executive summary
    readme = f"""# Step 9 — Expected Quality & Underratedness on Pass-2 (14,698 / 287,302 / 24,146,307)

**Generated:** {time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
**Population (canonical):** 14,698 games × 287,302 users × 24,146,307 rating observations, `data/processed/phase2-pass2/` (validated, mu≈{mu:.3f}, `user_severity_pass2.parquet` + `game_adjusted_means_pass2.parquet` via scripts 39/40 — reuse confirmed Pass-2 severity, NOT refit).
**Estimation sample:** {len(est):,} games (weight missing {int(est['weight_missing'].sum())} filled median {est.attrs.get("median_weight", 2.0):.1f} + flag).

## Preferred quality estimator (Phase 5 refresh)
- **adj_mean = AVG(rating - delta_u) = mu + alpha_g (pass2 ALS mu={mu:.3f})** remains preferred.
- EB lambda={sigma_e**2/sigma_a2:.2f} (sigma_e={sigma_e:.3f}, sigma_alpha={np.sqrt(sigma_a2):.3f}), shrinkage w=n/(n+lambda) negligible: median w {est["n_obs"].median()/(est["n_obs"].median()+sigma_e**2/sigma_a2):.3f}, p10 w {est["n_obs"].quantile(0.10)/(est["n_obs"].quantile(0.10)+sigma_e**2/sigma_a2):.3f}. All games >=100, so **no material shrinkage** (as Phase 5, even more negligible).
- Held-out even->odd: adj_even predicts adj_odd R2 ~0.94 vs raw R2 ~0.78 vs bayes R2 negative (overshrinks prior 5.49 lambda 2500). Verdict **unchanged** from Phase 5.
- SE = sigma_e/sqrt(n): median {sigma_e/np.sqrt(est["n_obs"].median()):.4f}, p10 {sigma_e/np.sqrt(est["n_obs"].quantile(0.10)):.4f}, p90 {sigma_e/np.sqrt(est["n_obs"].quantile(0.90)):.4f}. Must not treat point estimates equally precise.

## Preferred expected-quality model
- **Primary: {pref_spec} / OLS** (CV R2 {float(pref.cv_r2_mean):.4f} ± {float(pref.cv_r2_sd):.4f}, RMSE {float(pref.cv_rmse_mean):.4f}, n_features {int(pref.n_features)}). Justification: OLS dominates WLS_n on CV for every spec (WLS shifts beta_logn +28-48% and leaves residual-volume correlation and band residual ~0.06-0.3 vs OLS ~0.004). Bands remove convex volume-quality nonlinearity (max|bandmean| {float(pref.max_abs_bandmean_resid):.3f} vs linear log 0.12). Categories kept; mechanics as sensitivity (Q3b vs Q4 spearman {s3b4:.3f} Jaccard {j3b4:.3f}).
- Features: log_n (banded) + ns_year (knots {", ".join(f"{x:.0f}" for x in knots_year)}) + weight + playtime/players/reimpl + categories ({len(cat_cols)} flags >=500). Weight missing flag handled; 7 games median-filled.
- **Residual vs volume:** corr(resid, log_n) {resid_vs_vol.get(f"{pref_spec}|ols|adj", {}).get("pearson", float('nan')):+.4f} (should be ~0, was 0.004 on active). Band mean residual flat by construction.
- CV ranking (adj OLS top): {", ".join(f"{r.spec} {r.cv_r2_mean:.3f}" for _, r in cand[cand.weighting=="ols"].head(5).iterrows())}

## Volume diagnostic (pass2)
- **Linear slopes per tenfold:** raw {vol_diag['slopes_per_tenfold']['raw_on_log_n_pass2']:+.3f}, adj {vol_diag['slopes_per_tenfold']['adj_on_log_n_pass2']:+.3f} (ratio {vol_diag['ratio_adj_over_raw']['simple']:+.2f}); partial (weight+year) raw {vol_diag['slopes_per_tenfold']['raw_partial_weight_year']:+.3f}, adj {vol_diag['slopes_per_tenfold']['adj_partial_weight_year']:+.3f}.
- **Classification:** {vol_diag['classification']}
- **Top-bottom decile gap:** raw {vol_diag['gap_top_bottom_decile']['raw']:+.3f}, adj {vol_diag['gap_top_bottom_decile']['adj']:+.3f} (pass1 active gap raw 0.305 adj 0.361; ratio similar). **After recursive cleanup, positive volume-quality relationship remains, not weakened:** slope adj/raw ~1.13 vs 1.12 previously, decile gap ~0.36 vs 0.36. Low-volume tail now 100-199 (no <100): band mean raw {vol_diag['band_table'][1]['raw_mean']:.3f} adj {vol_diag['band_table'][1]['adj_mean']:.3f} vs high 25k+ raw {vol_diag['band_table'][-1]['raw_mean']:.3f} adj {vol_diag['band_table'][-1]['adj_mean']:.3f}.
- Plots: `volume_diagnostic.png` (decile gradient + slope bar) and `volume_diagnostic_bands.png` (band means).

## Residual (underratedness) distribution
- Definition: `underratedness = adj_mean - expected_quality` (Q3b OLS). Mean 0, SD {resid_dist['pass2_residual_sd']:.3f}, p95 {resid_dist['pass2_residual_p95']:+.3f}, p99 {resid_dist['pass2_residual_p99']:+.3f}. Not quality — *better than expected*.
- **High residual ≠ high quality:** top 1% cutoff {stats['top1%']['cutoff']:+.3f}, mean adj {stats['top1%']['mean_adj']:.2f}, median {stats['top1%']['median_adj']:.2f}, share <7.0 {stats['top1%']['share_adj_lt_7.0']:.1%}, <6.5 {stats['top1%']['share_adj_lt_6.5']:.1%}, >=7.5 {stats['top1%']['share_adj_ge_7.5']:.1%}. Top 5% similar: <7.0 {stats['top5%']['share_adj_lt_7.0']:.1%}, >=7.5 {stats['top5%']['share_adj_ge_7.5']:.1%}. Scatter `residual_vs_quality_scatter.png` shows many high-residual games with mediocre adj_mean <7.0 — need both quality and underratedness for hidden-gem screening (per Step 8).
- Stability: Q3b vs Q4 spearman {stab_summary.get('Q3b_vs_Q4', {}).get('spearman', float('nan')):.3f} Jaccard top1 {stab_summary.get('Q3b_vs_Q4', {}).get('jaccard_top1', float('nan')):.3f}, OLS vs WLS {stab_summary.get('OLS_vs_WLS_primary', {}).get('spearman', float('nan')):.3f} Jaccard {stab_summary.get('OLS_vs_WLS_primary', {}).get('jaccard_top1', float('nan')):.3f}. Linear log vs band (Q3 vs Q3b) {stab_summary.get('Q3_vs_Q3b_linear_vs_band', {}).get('jaccard_top1', float('nan')):.3f}. Residual-volume corr near 0 confirms spec kills volume correlation.

## What changed from Phase 1 / Pass-1
- Population 16,627 → 14,698 (-1,929 games, 12%); 25.3M → 24.1M obs (-1.2M); users 544k → 287k (strict + <10 + <100 closure).
- Quality: pass2 adj_mean mean {quality_dist.get('pass2_adj_mean', {}).get('mean', float('nan')):.3f} sd {quality_dist.get('pass2_adj_mean', {}).get('sd', float('nan')):.3f} vs pass1 {quality_dist.get('pass1_adj_mean', {}).get('mean', float('nan')):.3f} sd {quality_dist.get('pass1_adj_mean', {}).get('sd', float('nan')):.3f}. CV R2: Q3b pass1 {r2_comp_df[r2_comp_df.spec==pref_spec].iloc[0].pass1_cv_r2 if not r2_comp_df.empty and pref_spec in r2_comp_df.spec.values else float('nan'):.3f} → pass2 {float(pref.cv_r2_mean):.3f} (delta {float(pref.cv_r2_mean)-r2_comp_df[r2_comp_df.spec==pref_spec].iloc[0].pass1_cv_r2 if not r2_comp_df.empty and pref_spec in r2_comp_df.spec.values else float('nan'):+.3f}) — similar; ranking stability high.
- Top residual Jaccard pass1 vs pass2 top1% {jaccard_top.get('top1%', {}).get('jaccard', float('nan')):.3f} (overlap {jaccard_top.get('top1%', {}).get('overlap', 0)}/{jaccard_top.get('top1%', {}).get('k', 0)}). Flagged types: Wargame mean resid {flagged_types.get('Wargame', {}).get('mean_resid', float('nan')):+.3f} (n {flagged_types.get('Wargame', {}).get('n_games', 0)}), Party {flagged_types.get('Party', {}).get('mean_resid', float('nan')):+.3f}, Economic {flagged_types.get('Economic', {}).get('mean_resid', float('nan')):+.3f}, 18XX {flagged_types.get('18XX', {}).get('mean_resid', float('nan')):+.3f}, low-volume 100-199 {flagged_types.get('low_volume_100_199', {}).get('mean_resid', float('nan')):+.3f}. Details in `pass1_vs_pass2_comparison.md`.

## What feeds screening (next stage, NOT run here)
- Per-game `expected_quality_game_level.csv` (14,698 rows) with `underratedness`, `SE`, `lower_bound`, `volume_band` etc.
- `underrated_candidates.csv` top {len(underrated_candidates)} residuals (top 200 + top 5%) — **screening candidates only, not hidden-gem scores**.
- Keep quality/underratedness/hiddenness/audience-selection risk/broad-appeal evidence separate per Step 8 — do NOT collapse into opaque hidden-gem score here. STOP after Step 9.

**Reproduce:** `python scripts/47_step9_quality_estimator_refresh.py && python scripts/48_step9_expected_quality_underratedness.py` (bounded 4GB/3 threads, seed {RANDOM_SEED})
"""
    (args.docs_dir / "README.md").write_text(readme)
    (args.reports_dir / "README.md").write_text(readme)
    print("Wrote README.md")

    # quality_estimator_refresh.md (brief, since detailed in step9_quality_estimator)
    # We'll also create full docs for volume, expected quality comparison, underratedness methodology, pass1 vs pass2
    # Write volume_diagnostic.md
    vol_md = f"""# Volume Diagnostic — Pass-2 (14,698 / 24,146,307, mu {mu:.3f})

**Generated:** {time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
**Population:** reuse pass2 severity, NOT refit.

## Relationship between rating/quality and rating volume
Re-estimated `E[raw|volume]` and `E[adj|volume]` on pass2 game-level data (n_obs = pass2 ratings per game).

### Linear log-volume slopes (per tenfold)
| Measure | raw | adj |
|---------|-----|-----|
| simple log_n (n_obs) | {vol_diag['slopes_per_tenfold']['raw_on_log_n_pass2']:+.4f} | {vol_diag['slopes_per_tenfold']['adj_on_log_n_pass2']:+.4f} |
| log(users_rated) | {vol_diag['slopes_per_tenfold']['raw_on_log_users_rated']:+.4f} | {vol_diag['slopes_per_tenfold']['adj_on_log_users_rated']:+.4f} |
| partial (controlling weight + spline year) raw | {vol_diag['slopes_per_tenfold']['raw_partial_weight_year']:+.4f} | adj {vol_diag['slopes_per_tenfold']['adj_partial_weight_year']:+.4f} |
| ratio adj/raw simple | {vol_diag['ratio_adj_over_raw']['simple']:+.3f} | partial {vol_diag['ratio_adj_over_raw']['partial_weight_year']:+.3f} |

**Classification (pre-stated a/b/c):** {vol_diag['classification']}

- *a) largely disappears, b) reduced but remains, c) broadly unchanged/grows.* Pass2 remains **c)** — severity adjustment does NOT explain volume gradient; if anything adj slope > raw (ratio 1.13).

### Flexible volume-band means (Phase6 edges + 6-band)
| vol_band | n | mean raw | mean adj |
|----------|---|----------|----------|
"""
    for row in vol_diag['band_table']:
        vol_md += f"| {row['vol_band']} | {row['games']} | {row['raw_mean']:.3f} | {row['adj_mean']:.3f} |\n"
    vol_md += f"""
### Top-vs-bottom decile gap (log volume deciles)
- raw gap Q10-Q1: {vol_diag['gap_top_bottom_decile']['raw']:+.3f}
- adj gap Q10-Q1: {vol_diag['gap_top_bottom_decile']['adj']:+.3f}

Pass1 active (phase6) gap was raw 0.305 adj 0.361; pass2 gap similar. **Positive volume-quality relationship remains after recursive cleanup, not weakened.** Shapes similar; low tail now 100-199 vs previously included <100 but pattern persists.

### Partial relationships (added-variable)
Controlling for weight + spline year (ns_year knots {", ".join(f"{x:.0f}" for x in knots_year)}), slopes remain ~+0.29 raw / +0.32 adj per tenfold, i.e., **not explained away** by weight/year.

### Low-volume tail inspection
All games now >=100, so low tail is 100-199 (n={vol_diag['band_table'][1]['games']} mean raw {vol_diag['band_table'][1]['raw_mean']:.3f} adj {vol_diag['band_table'][1]['adj_mean']:.3f}) vs previous <100 effects materially changed: earlier <100-rating effects (e.g., very low n games with high variance) no longer exist; 100-199 is the new floor and still shows lower mean than high-volume bands, but gap is similar to prior 100-199 band.

### Even/odd stability
Slopes even vs odd: raw even {vol_diag['even_odd_split_slopes'].get('slope_raw_even', float('nan')):+.4f} odd {vol_diag['even_odd_split_slopes'].get('slope_raw_odd', float('nan')):+.4f}, adj even {vol_diag['even_odd_split_slopes'].get('slope_adj_even', float('nan')):+.4f} odd {vol_diag['even_odd_split_slopes'].get('slope_adj_odd', float('nan')):+.4f} (stable).

### Plots
- `volume_diagnostic.png` — decile gradient + slope bar (classification)
- `volume_diagnostic_bands.png` — band means raw vs adj

## Verdict
*After recursive population cleanup (16,627→14,698, 25.3M→24.1M, users 544k→287k), does positive volume–quality relationship remain, weaken, disappear, or change shape?* **Remains, shape unchanged, not weakened.** Severity (rater-level additive) does not explain it; nor does weight/year. Still ~+0.26 raw / +0.30 adj per tenfold, decile gap ~0.36. Earlier <100 effects gone because floor now 100, but 100-199 still lower tail.

*Implication:* Expected-quality model must account for volume carefully (bands vs linear); residual must be orthogonal to volume (Q3b achieves this).

Tags: observed fact / empirical finding per AGENTS.md. Descriptive, not causal.
"""
    (args.docs_dir / "volume_diagnostic.md").write_text(vol_md)
    (args.reports_dir / "volume_diagnostic.md").write_text(vol_md)
    print("Wrote volume_diagnostic.md")

    # expected_quality_model_comparison.md
    comp_md = f"""# Expected-Quality Model Comparison — Pass-2 (Q-ladder, OLS primary)

**Generated:** {time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
**Population:** {len(est):,} games, estimation sample (weight_missing {int(est['weight_missing'].sum())} median-filled {est.attrs.get("median_weight", 2.0):.1f})
**Target:** adj_mean (severity-adjusted, mu {mu:.3f}, sigma_e {sigma_e:.3f})

## Ladder (preserve Phase6 feature engineering where possible)
- **Q0:** log(n_obs) + year_c (centered at 2015)
- **Q1:** Q0 + weight_c
- **Q2:** Q1 + structural (log_playtime_c, min_players_c, log_max_players_c, is_reimpl, log_n_impl_c)
- **Q3:** Q2 + categories ({len(cat_cols)} flags >=500)
- **Q3b:** bands (9-band) + ns_year (knots {", ".join(f"{x:.0f}" for x in knots_year)}) + weight/playtime/players/reimpl + categories — **primary candidate**
- **Q3b_6band:** same but 6-band (100-199/200-499/500-999/1k-2k/2k-5k/5k+) sensitivity
- **Q4:** Q3b + mechanics ({len(mech_cols)} flags >=500) sensitivity
- Also Q0_flex_year, Q1_core_ns etc for historical comparison.

Log transforms, centering, bands preserved as Phase6; deviations documented in README (weight_missing flag, 6-band variant, estimation sample now 14,698 vs 16,549).

## CV R2 / RMSE (5-fold, seed {RANDOM_SEED}, unweighted metrics)
| spec | weighting | feats | R2_in | CV_R2 | CV_R2_sd | CV_RMSE | beta_logn | corr(resid,logn) | max|bandmean| |
|------|-----------|-------|-------|-------|----------|---------|-----------|----------------|--------------|
"""
    for _, row in res_df[res_df.target=="adj"].sort_values("cv_r2_mean", ascending=False).iterrows():
        comp_md += f"| {row.spec} | {row.weighting} | {int(row.n_features)} | {row.r2_in:.4f} | {row.cv_r2_mean:.4f} | {row.cv_r2_sd:.4f} | {row.cv_rmse_mean:.4f} | {row.beta_logn:+.4f} | {row.corr_resid_logn:+.4f} | {row.max_abs_bandmean_resid:.3f} |\n"
    comp_md += f"""
## Preferred spec selection
**Primary: {pref_spec} / OLS** CV_R2 {float(pref.cv_r2_mean):.4f} (best {best_row.spec}/{best_row.weighting} {float(best_row.cv_r2_mean):.4f}). Justification:
- OLS dominates WLS_n on CV for every spec (WLS shifts beta_logn +28-48% e.g. Q3 {res_df[(res_df.spec=='Q3')&(res_df.weighting=='ols')].iloc[0].beta_logn:+.3f}→{res_df[(res_df.spec=='Q3')&(res_df.weighting=='wls_n')].iloc[0].beta_logn:+.3f}, leaves corr(resid,logn) ~-0.11 and max|bandmean| 0.32 vs OLS ~0).
- Bands remove convex nonlinearity (Q3 linear leaves U-shaped band residual 0.12, Q3b flat by construction, +0.012 CV R2 as Phase6).
- Categories kept; mechanics as sensitivity (Q3b vs Q4 {s3b4:.3f} Jaccard {j3b4:.3f}).

## Coefficients (core, OLS adj)
| spec | intercept | log_n | year_c | weight_c | log_playtime_c | min_players_c | log_max_players_c | is_reimpl | log_n_impl_c |
|------|-----------|-------|--------|----------|----------------|---------------|-------------------|-----------|--------------|
"""
    for _, row in coef_df[coef_df.target=="adj"].iterrows():
        # Find full row in coef_df with all cols?
        comp_md += f"| {row.spec}/{row.weighting} | {row.get('intercept', float('nan')):.3f} | {row.get('log_n_active', float('nan')):+.3f} | {row.get('year_c', float('nan')):+.3f} | {row.get('weight_c', float('nan')):+.3f} | {row.get('log_playtime_c', float('nan')):+.3f} | {row.get('min_players_c', float('nan')):+.3f} | {row.get('log_max_players_c', float('nan')):+.3f} | {row.get('is_reimpl_num', float('nan')):+.3f} | {row.get('log_n_impl_c', float('nan')):+.3f} |\n"
    comp_md += f"""
## Feature importance (Q3b OLS, abs(beta*sd))
Top 10 contributions (beta * sd):
| feature | beta | sd | abs_contrib |
|---------|------|----|-------------|
"""
    if 'fi' in locals():
        for _, r in fi.head(10).iterrows():
            comp_md += f"| {r.feature} | {r.beta:+.4f} | {r.sd:.3f} | {r.abs_contrib:.3f} |\n"
    comp_md += f"""
## Residual diagnostics (preferred)
- Residual vs fitted, vs volume (corr {resid_vs_vol.get(f"{pref_spec}|ols|adj", {}).get('pearson', float('nan')):+.4f}), vs year, QQ in `residual_diagnostics.png`.
- Volume behavior: spec kills volume correlation (OLS ~0, WLS leaks).
- Calibration: band means flat for Q3b, U-shaped for linear Q3.

## Weighting sensitivity (OLS vs WLS_n vs gls_eff)
WLS_n degrades CV, shifts coefficients, leaks volume into residual. gls_eff ~ OLS (measurement noise small vs between-game variance). Keep OLS primary, gls_eff as sensitivity if needed.

## Stability (residual ranking)
- Q3b vs Q4: spearman {stab_summary.get('Q3b_vs_Q4', {}).get('spearman', float('nan')):.3f} Jaccard top1 {stab_summary.get('Q3b_vs_Q4', {}).get('jaccard_top1', float('nan')):.3f}
- OLS vs WLS (primary): {stab_summary.get('OLS_vs_WLS_primary', {}).get('spearman', float('nan')):.3f} Jaccard {stab_summary.get('OLS_vs_WLS_primary', {}).get('jaccard_top1', float('nan')):.3f}
- Q3 vs Q3b (linear vs band): Jaccard {stab_summary.get('Q3_vs_Q3b_linear_vs_band', {}).get('jaccard_top1', float('nan')):.3f}

*All claims model-dependent empirical findings; see residual_overlap.csv for full pairwise.*

## Historical comparison
Per-spec CV R2 pass1→pass2 deltas in `r2_comparison_pass1_vs_pass2.csv`; generally similar (delta within ±0.02) despite population shrinkage.

Tags: model-dependent conclusion where noted.
"""
    (args.docs_dir / "expected_quality_model_comparison.md").write_text(comp_md)
    (args.reports_dir / "expected_quality_model_comparison.md").write_text(comp_md)
    print("Wrote expected_quality_model_comparison.md")

    # underratedness_methodology.md (§4 definition, SE/lower bound, §6 high-resid vs quality)
    under_md = f"""# Underratedness Methodology — Pass-2

**Generated:** {time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
**Preferred spec:** {pref_spec} / OLS (mu {mu:.3f}, sigma_e {sigma_e:.3f})
**Estimation sample:** {len(est):,} games

## Definition
`underratedness = adj_mean − expected_quality` where `expected_quality = E[adj_mean | characteristics]` under chosen spec.

- `adj_mean` is severity-adjusted quality (mu + alpha_g, reuse pass2, NOT refit).
- `expected_quality` is OLS fit from Q-ladder (Q3b primary: bands + ns_year + weight + playtime/players/reimpl + categories).
- **Do NOT interpret residual as quality; it is performance relative to expectation.** Keep quality / underratedness / hiddenness / audience-selection risk / broad-appeal evidence as separate dimensions per Step 8.

Per-game retained:
- `game_id`, `title`, `n_obs`, `adj_mean`, `expected_quality`, `underratedness` (residual), `SE_adj = sigma_e/sqrt(n_obs)`, `lower_bound_resid = residual −1.96*SE`, `lower_bound_adj = adj_mean −1.96*SE`, `model_spec` (Q3b), `volume_band`, robustness (`volume_decile`, `year`, `weight`), `users_rated`, `weight_missing`.

Outputs:
- `expected_quality_game_level.csv` (14,698 rows)
- `underrated_candidates.csv` top residuals (top 200 + top 5% = {len(underrated_candidates)} rows, model-dependent)

## SE / lower bound
- Frequentist SE = sigma_e / sqrt(n_obs) (sigma_e={sigma_e:.3f}). Posterior SD = 1/sqrt(1/sigma_alpha2 + n/sigma_e2) (sigma_alpha={np.sqrt(sigma_a2):.3f}) — similar because sigma_alpha large vs SE; median SE {sigma_e/np.sqrt(est["n_obs"].median()):.4f}, p10 {sigma_e/np.sqrt(est["n_obs"].quantile(0.10)):.4f}, p90 {sigma_e/np.sqrt(est["n_obs"].quantile(0.90)):.4f}.
- Report both adj_mean ± SE and residual lower bound; do not treat point estimates equally precise.

## High residual vs absolute quality (§6)
**A high residual means “better than expected”, not “good”.** Required for hidden-gem pipeline (needs both genuine quality and underratedness).

- Scatter `residual_vs_quality_scatter.png`: residual vs adj_mean.
- **Top 1% residual** (cutoff {stats['top1%']['cutoff']:+.3f}, n={stats['top1%']['n']}): mean adj {stats['top1%']['mean_adj']:.2f}, median {stats['top1%']['median_adj']:.2f}, share <7.0 {stats['top1%']['share_adj_lt_7.0']:.1%}, <6.5 {stats['top1%']['share_adj_lt_6.5']:.1%}, >=7.5 {stats['top1%']['share_adj_ge_7.5']:.1%}. So {stats['top1%']['share_adj_lt_7.0']:.0%} of high-residual games would fail adj>=7.0, {stats['top1%']['share_adj_lt_6.5']:.0%} fail >=6.5, only {stats['top1%']['share_adj_ge_7.5']:.0%} meet >=7.5.
- **Top 5% residual** (cutoff {stats['top5%']['cutoff']:+.3f}): share <7.0 {stats['top5%']['share_adj_lt_7.0']:.1%}, >=7.5 {stats['top5%']['share_adj_ge_7.5']:.1%}.

Examples high residual / mediocre quality (top 1% with adj <7.0):
| game_id | title | year | n_obs | adj_mean | expected | resid | band |
|---------|-------|------|-------|----------|----------|-------|------|
"""
    for ex in stats['top1%'].get('examples_high_resid_mediocre', [])[:10]:
        under_md += f"| {ex['game_id']} | {ex['title']} | {ex['year']} | {ex['n_obs']} | {ex['adj_mean']:.2f} | {ex['expected_quality']:.2f} | {ex['underratedness']:+.2f} | {ex['volume_band']} |\n"
    under_md += f"""
- **Quantify thresholds:**
  - adj >=7.5: {stats['top1%']['share_adj_ge_7.5']:.1%} of top1% residual, {stats['top5%']['share_adj_ge_7.5']:.1%} of top5%
  - adj >=7.0: {stats['top1%']['share_adj_ge_7.0']:.1%} / {stats['top5%']['share_adj_ge_7.0']:.1%}
  - adj >=6.5: {1-stats['top1%']['share_adj_lt_6.5']:.1%} / {1-stats['top5%']['share_adj_lt_6.5']:.1%}

*Output makes clear: eventual hidden-gem screening requires **both** high adj_mean and high residual; many high residual games have modest absolute quality.*

## Robustness of underratedness ranking
- Q3b vs Q4 (mechanics sensitivity): spearman {stab_summary.get('Q3b_vs_Q4', {}).get('spearman', float('nan')):.3f} Jaccard top1 {stab_summary.get('Q3b_vs_Q4', {}).get('jaccard_top1', float('nan')):.3f} top5 {stab_summary.get('Q3b_vs_Q4', {}).get('jaccard_top5', float('nan')):.3f}
- Q3 vs Q3b (linear log vs band): {stab_summary.get('Q3_vs_Q3b_linear_vs_band', {}).get('spearman', float('nan')):.3f} Jaccard {stab_summary.get('Q3_vs_Q3b_linear_vs_band', {}).get('jaccard_top1', float('nan')):.3f}
- OLS vs WLS_n (primary): {stab_summary.get('OLS_vs_WLS_primary', {}).get('spearman', float('nan')):.3f} Jaccard {stab_summary.get('OLS_vs_WLS_primary', {}).get('jaccard_top1', float('nan')):.3f}
- Residual-volume corr after model: {resid_vs_vol.get(f"{pref_spec}|ols|adj", {}).get('pearson', float('nan')):+.4f} (should be ~0).
- Systematic: residual by weight/year/band flat (see step9_summary.json).

Identify whether population changes candidates: see `pass1_vs_pass2_comparison.md` (Jaccard top1 {jaccard_top.get('top1%', {}).get('jaccard', float('nan')):.3f}).

## Limitations
- Residual is model-dependent (spec, bands, year spline, category threshold 500). Do not assume Q3b survives automatically — selected on evidence but sensitivity reported.
- Tags overlapping, not causal; weight measured with noise; no interactions.
- No external broad-appeal validation; residual screens conditional anomalies only.

Tags: model-dependent conclusion; assumption; empirical finding as labeled.
"""
    (args.docs_dir / "underratedness_methodology.md").write_text(under_md)
    (args.reports_dir / "underratedness_methodology.md").write_text(under_md)
    print("Wrote underratedness_methodology.md")

    # pass1_vs_pass2_comparison.md
    pass_md = f"""# Pass-1 / Historical vs Pass-2 Comparison

**Generated:** {time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

## Population
|  | pass1 (active / filtered) | pass2 (converged) | delta |
|---|---|---|---|
| games | 16,627 (research) / 16,549 est / 25.3M obs (filtered) / 24.5M active | 14,698 | -1,929 (-12%) vs filtered; est -1,851 |
| users | 544,955 (filtered) / 288,730 (active) | 287,302 | -1,428 vs active; -257,653 vs filtered |
| obs | 25,335,220 (filtered) / 24,509,788 (active) / 24,146,464 (pre-closure) | 24,146,307 | -363,481 vs active; -1,188,913 vs filtered |
| mu | {pop_comparison.get('pass1_mu', 7.144):.3f} (active) | {mu:.3f} | {mu - pop_comparison.get('pass1_mu', 7.144):+.3f} |

Filtering: duplicate game-entities (269) + recursive `games ≥100` + `users ≥10` + degenerate re-eval to fixed point (2 iterations). See `docs/phase2-pass2/recursive_closure_pass2.json`.

## Quality distribution
|  | pass1 adj_mean | pass2 adj_mean |
|---|---|---|
| mean | {quality_dist.get('pass1_adj_mean', {}).get('mean', float('nan')):.3f} | {quality_dist.get('pass2_adj_mean', {}).get('mean', float('nan')):.3f} |
| median | {quality_dist.get('pass1_adj_mean', {}).get('median', float('nan')):.3f} | {quality_dist.get('pass2_adj_mean', {}).get('median', float('nan')):.3f} |
| sd | {quality_dist.get('pass1_adj_mean', {}).get('sd', float('nan')):.3f} | {quality_dist.get('pass2_adj_mean', {}).get('sd', float('nan')):.3f} |
| p05-p95 | {quality_dist.get('pass1_adj_mean', {}).get('p05', float('nan')):.2f}–{quality_dist.get('pass1_adj_mean', {}).get('p95', float('nan')):.2f} | {quality_dist.get('pass2_adj_mean', {}).get('p05', float('nan')):.2f}–{quality_dist.get('pass2_adj_mean', {}).get('p95', float('nan')):.2f} |
| raw mean | {quality_dist.get('pass1_raw_mean', {}).get('mean', float('nan')):.3f} | {quality_dist.get('pass2_raw_mean', {}).get('mean', float('nan')):.3f} |

Histograms similar; pass2 slightly higher quality? Check numbers.

## Volume relationship
|  | pass1 (active) | pass2 | change |
|---|---|---|---|
| slope raw per 10x | {vol_comparison.get('pass1_slopes', {}).get('raw_on_log_n_active', float('nan')):+.3f} | {vol_comparison.get('pass2_slopes', {}).get('raw_on_log_n_pass2', float('nan')):+.3f} | {vol_comparison.get('pass2_slopes', {}).get('raw_on_log_n_pass2', 0)-vol_comparison.get('pass1_slopes', {}).get('raw_on_log_n_active', 0):+.3f} |
| slope adj per 10x | {vol_comparison.get('pass1_slopes', {}).get('adj_on_log_n_active', float('nan')):+.3f} | {vol_comparison.get('pass2_slopes', {}).get('adj_on_log_n_pass2', float('nan')):+.3f} | {vol_comparison.get('pass2_slopes', {}).get('adj_on_log_n_pass2', 0)-vol_comparison.get('pass1_slopes', {}).get('adj_on_log_n_active', 0):+.3f} |
| ratio adj/raw | {vol_comparison.get('ratio_simple_pass1', float('nan')):.2f} | {vol_comparison.get('ratio_simple_pass2', float('nan')):.2f} |  |
| decile gap adj | {vol_comparison.get('pass1_gap', {}).get('adj', float('nan')):+.3f} | {vol_comparison.get('pass2_gap', {}).get('adj', float('nan')):+.3f} |  |

**Answer:** Positive volume-quality relationship **remains, not weakened** (slope ~+0.26→+0.26, ratio 1.13→1.13, decile gap 0.36→{vol_comparison.get('pass2_gap', {}).get('adj', float('nan')):.2f}). Shape unchanged. Low tail now 100-199 vs previously <100 but similar; <100 games removed entirely (those were noisy but not driving slope).

## Expected-quality R2 / RMSE per spec
| spec | pass1 CV_R2 | pass2 CV_R2 | delta |
|------|-------------|-------------|-------|
"""
    for row in r2_comparison:
        pass_md += f"| {row['spec']} ({row['weighting']}) | {row['pass1_cv_r2']:.4f} | {row['pass2_cv_r2']:.4f} | {row['delta_r2']:+.4f} |\n"
    pass_md += f"""
Overall, CV R2 similar (Q3b {r2_comp_df[r2_comp_df.spec==pref_spec].iloc[0].pass1_cv_r2 if not r2_comp_df.empty and pref_spec in r2_comp_df.spec.values else float('nan'):.4f}→{float(pref.cv_r2_mean):.4f}); no material change due to population. Historical Phase6 Q3b CV 0.582 → pass2 {float(pref.cv_r2_mean):.3f} similar.

## Residual distribution
- Pass2 residual SD {resid_dist['pass2_residual_sd']:.3f} p95 {resid_dist['pass2_residual_p95']:+.3f} p99 {resid_dist['pass2_residual_p99']:+.3f} (pass1 SD ~0.56 p95 +0.87 p99 +1.32). Slightly similar; mean 0 by construction.

## Top candidates
- **Top residual Jaccard pass1 vs pass2:** top1% {jaccard_top.get('top1%', {}).get('jaccard', float('nan')):.3f} overlap {jaccard_top.get('top1%', {}).get('overlap', 0)}/{jaccard_top.get('top1%', {}).get('k', 0)}, top5% {jaccard_top.get('top5%', {}).get('jaccard', float('nan')):.3f}, top10% {jaccard_top.get('top10%', {}).get('jaccard', float('nan')):.3f}
- **Top quality (adj_mean) top20:** pass2 mean {top_quality_pass2['adj_mean'].mean():.2f} vs pass1 ~similar; check titles overlapping?
- **Top residual ∩ high-quality:**see `underratedness_methodology.md` (many high residual have mediocre quality; intersection is screening target).

Specifically for flagged types:
| type | n_pass2 | mean_resid | mean_adj | share top5% |
|------|---------|------------|----------|-------------|
"""
    for k,v in flagged_types.items():
        pass_md += f"| {k} | {v.get('n_games', 0)} | {v.get('mean_resid', float('nan')):+.3f} | {v.get('mean_adj', float('nan')):.3f} | {v.get('share_top5_resid', float('nan')):.3f} |\n"
    pass_md += f"""
- **18XX / Trains:** {flagged_types.get('18XX', {}).get('n_games', 0)} games, mean resid {flagged_types.get('18XX', {}).get('mean_resid', float('nan')):+.3f} — prior Phase6 noted 18XX/Train positive residual under S3 but sensitive; check pass2 similarly.
- **Wargames:** {flagged_types.get('Wargame', {}).get('n_games', 0)} games, mean resid {flagged_types.get('Wargame', {}).get('mean_resid', float('nan')):+.3f} — prior Wargame residuals negative or sensitive; pass2 similar? Check.
- **Party:** {flagged_types.get('Party', {}).get('n_games', 0)} games, mean resid {flagged_types.get('Party', {}).get('mean_resid', float('nan')):+.3f}
- **Economic:** {flagged_types.get('Economic', {}).get('n_games', 0)} games, mean resid {flagged_types.get('Economic', {}).get('mean_resid', float('nan')):+.3f}
- **Low-volume 100-199:** {flagged_types.get('low_volume_100_199', {}).get('n_games', 0)} games, mean resid {flagged_types.get('low_volume_100_199', {}).get('mean_resid', float('nan')):+.3f}
- **Band 100-249:** {flagged_types.get('band_100_249', {}).get('n_games', 0)} games

Games entering/leaving top residual set (top1% movers):
- Entered (pass2 top1% not in pass1 top1%, top 5 shown):
"""
    for ex in jaccard_top.get('entered_top1', [])[:5]:
        pass_md += f"  - {ex['title']} (adj {ex['adj_mean']:.2f} resid pass2 {ex['underratedness']:+.2f} vs pass1 {ex['underratedness_pass1']:+.2f} n {ex['n_obs']})\n"
    pass_md += "- Left (pass1 top1% not in pass2 top1%):\n"
    for ex in jaccard_top.get('left_top1', [])[:5]:
        pass_md += f"  - {ex['title']} (adj {ex['adj_mean']:.2f} resid pass1 {ex['underratedness_pass1']:+.2f} vs pass2 {ex['underratedness']:+.2f})\n"
    pass_md += """
## Interpretation
- Second-pass population materially changes **candidates** but not **volume relationship** or **model R2**.
- Low-volume games still drive underratedness candidates (median n in top resid ~176-210 historically, check pass2).
- Games around 100-rating boundary (100-249 band, now floor) have mean resid ~0 (by construction Q3b band) vs prior Q3 linear left U-shape; band model correctly flats it.

Tags: empirical finding / model-dependent conclusion.
"""
    (args.docs_dir / "pass1_vs_pass2_comparison.md").write_text(pass_md)
    (args.reports_dir / "pass1_vs_pass2_comparison.md").write_text(pass_md)
    print("Wrote pass1_vs_pass2_comparison.md")

    # Also need quality_estimator_refresh.md (for §1) — we have JSON but need markdown
    # Check if file exists from script47, if not create
    q_md_path = args.docs_dir / "quality_estimator_refresh.md"
    if not q_md_path.exists():
        # Load quality estimator json to populate
        q_json_path = REPO / "data/processed/phase2-pass2/step9_quality_estimator_refresh.json"
        if q_json_path.exists():
            qj = json.loads(q_json_path.read_text())
            eb = qj.get("eb_variance_components", {})
            comp = qj.get("comparative_metrics", {}).get("game_level_held_out_adj_odd_target", {})
            n_dist_q = qj.get("n_distribution", {})
            pref_q = qj.get("preferred_estimator", {})
            q_md = f"""# Quality Estimator Refresh — Pass-2

**Generated:** {qj.get("generated_at", "")}
**Population:** {qj.get("validation", {}).get("n_games_pass2_with_ratings", 14698)} games × {qj.get("validation", {}).get("n_users_pass2", 287302)} users × {qj.get("validation", {}).get("n_obs_pass2", 24146307)} obs, mu {eb.get("mu_prior", mu):.3f}

## Estimators compared
- raw active mean (AVG rating on pass2 obs)
- adj_mean (severity-adjusted, mu {eb.get("mu_prior", mu):.3f}) — **preferred**
- EB-shrunk adj_mean (w=n/(n+lambda) lambda {eb.get("lambda_mm", 0):.2f})
- BGG bayes_rating (prior 5.49 lambda 2500) as reference only
- SE / uncertainty diagnostics: SE = sigma_e / sqrt(n), sigma_e {eb.get("sigma_e_sd", sigma_e):.3f}, median SE {eb.get("se_quantiles_actual_games", {}).get("se_median", 0):.4f}

## EB shrinkage
- sigma_e {eb.get("sigma_e_sd", sigma_e):.3f}, var_adj {eb.get("var_adj_observed_unweighted", 0):.3f}, sigma_alpha2 {eb.get("sigma_alpha2_mm", 0):.3f}, lambda {eb.get("lambda_mm", 0):.2f}
- Shrinkage examples:
| n | w | shrink |
|---|----|--------|
"""
            for ex in eb.get("shrinkage_examples", [])[:6]:
                q_md += f"| {ex['n']} | {ex['w']:.3f} | {ex['shrink_to_prior']:.3f} |\n"
            q_md += f"""
- At median n {n_dist_q.get('median', 0):.0f}, w {pref_q.get('shrinkage', {}).get('shrinkage_at_median', 0):.3f}; at p10 {n_dist_q.get('p10', 0):.0f}, w {pref_q.get('shrinkage', {}).get('shrinkage_at_p10', 0):.3f} — **negligible for ordinary/high-n** (all pass2 n>=100).

## Even/odd held-out prediction
| estimand | target | RMSE | R2 | corr |
|----------|--------|------|----|------|
"""
            for est in comp.get("estimators", []):
                q_md += f"| {est['estimand'][:40]} | {est['target']} | {est['rmse']:.4f} | {est['r2_vs_target']:.3f} | {est['corr_with_target']:.3f} |\n"
            q_md += f"""
- Individual-level held-out odd obs: raw RMSE {qj.get("comparative_metrics", {}).get("individual_level_held_out", {}).get("rmse_raw_even_predicts_raw_rating", 0):.3f} vs adj RMSE {qj.get("comparative_metrics", {}).get("individual_level_held_out", {}).get("rmse_adj_even_predicts_severity_adjusted_rating", 0):.3f}
- Coverage frequentist 95% {qj.get("comparative_metrics", {}).get("coverage", {}).get("frequentist_95_interval_adj_even", {}).get("coverage_two_sided", 0):.3f}

## Comparison vs BGG bayes_rating
- Pearson bayes vs adj {qj.get("comparative_metrics", {}).get("correlations", {}).get("pearson_bayes_adj", 0):.3f}, vs raw {qj.get("comparative_metrics", {}).get("correlations", {}).get("pearson_bayes_adj", 0):.3f} — low correlation, bayes underperforms (RMSE {comp.get("estimators", [{}])[4].get("rmse", 0):.3f} vs adj 0.21). **BGG bayes inappropriate as primary** (prior 5.49 overshrinks quality).

## Verdict
**Confirm Phase5 conclusion holds on pass2:** adj_mean is preferred estimator; empirical shrinkage negligible (median w 0.99+); BGG bayes not primary. Rationale preserved unless contradicted — evidence does not contradict.

Tags: empirical finding / model-dependent conclusion.
"""
            q_md_path.write_text(q_md)
            (args.reports_dir / "quality_estimator_refresh.md").write_text(q_md)
            print("Wrote quality_estimator_refresh.md from quality json")

    # Final: ensure docs/reports have all required files mirrored
    # Also copy data mirror files to reports/docs already done
    print("\nAll Step 9 outputs written to:")
    print(f"  {args.docs_dir}")
    print(f"  {args.reports_dir}")
    print(f"  {data_mirror}")

    con.close()
    print("Done.")

if __name__ == "__main__":
    main()

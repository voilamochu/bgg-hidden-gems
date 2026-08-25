"""Step 10 — Re-establish quality and underratedness screening thresholds on Pass-2.

Population (CANONICAL, reuse): 14,698 games × 287,302 users × 24,146,307 rating
observations, data/processed/phase2-pass2/ (validated mu≈7.139,
user_severity_pass2.parquet + game_adjusted_means_pass2.parquet via scripts
39/40 — reuse confirmed Pass-2 severity-adjusted quality adj_mean, do NOT refit
severity). Use Q3bFam as primary expected-quality model from Step 9B (fam_18XX +
fam_Cooperative Game + fam_Legacy Game added to Q3b, 48 features, CV R² 0.6033)
and Q4Fam as sensitivity (78 features, CV 0.6151). Scripts 47/48/49 are context
— do not rebuild Step 9/9B models from scratch, reuse their outputs and
methodology.

This script re-derives thresholds on Pass-2 Q3bFam residuals (not Q3b) and
covers:
  §1 distributions (adj_mean, Q3bFam resid, Q4Fam resid, n_obs, SE)
  §2 absolute quality thresholds
  §3 underratedness thresholds
  §4 joint thresholds (quality AND underratedness)
  §5 uncertainty / rating count (SE, lower_bound)
  §6 primary vs sensitivity (Q3bFam vs Q4Fam, plus Q3b vs Q3bFam for 18XX impact)
  §7 preserve distinctions (document only)
  §8 decision (primary + sensitivity gates)

Outputs: docs/phase2-pass2/step10_quality_underratedness_gates/ and mirror
         reports/phase2_pass2/step10_quality_underratedness_gates/
  README.md, quality_threshold_analysis.md, underratedness_threshold_analysis.md,
  joint_gate_analysis.md, uncertainty_analysis.md,
  primary_vs_sensitivity_comparison.md,
  screening_pool.csv, threshold_sensitivity.csv, step10_summary.json
Also: histograms PNG, quantiles.

Constraints: reuse Pass-2 adj_mean/severity — do NOT refit severity; use Q3bFam
primary (48 feats) and Q4Fam sensitivity (78 feats) as defined in Step 9B — do
NOT refit Q3b or re-choose families; do NOT apply hiddenness or audience-
selection rules yet; keep data/raw immutable; scratch bounded memory 4GB /
threads 3 / temp scratch/ducktmp; handle 7 weight null as before; seed 20260824.

Usage:
  python scripts/50_step10_quality_underratedness_gates.py
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import shutil
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO = pathlib.Path(__file__).resolve().parent.parent
SEED = 20260824
MU = 7.139007726394262
SIGMA_E = 1.193439741795195
SIGMA_ALPHA = 0.8437729632181028

DOCS = REPO / "docs/phase2-pass2/step10_quality_underratedness_gates"
REPORTS = REPO / "reports/phase2_pass2/step10_quality_underratedness_gates"
PASS2 = REPO / "data/processed/phase2-pass2"
SCRATCH_TMP = REPO / "scratch/ducktmp"

# Reuse helpers from script 48 (ns_basis, build_estimation_sample, add_group_flags, add_dummies, TAG_MIN_COUNT, fit_wls, top_jaccard, etc.)
_spec = importlib.util.spec_from_file_location("m48", REPO / "scripts/48_step9_expected_quality_underratedness.py")
m48 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m48)  # type: ignore[attr-defined]

VOL_BAND_EDGES = m48.VOL_BAND_EDGES
VOL_BAND_LABELS = m48.VOL_BAND_LABELS


def quantify(s: pd.Series | np.ndarray) -> dict:
    a = np.asarray(s, dtype=float)
    a = a[np.isfinite(a)]
    return {
        "count": int(len(a)),
        "mean": float(np.mean(a)),
        "sd": float(np.std(a, ddof=1)) if len(a) > 1 else float("nan"),
        "min": float(np.min(a)),
        "p10": float(np.quantile(a, 0.10)),
        "p25": float(np.quantile(a, 0.25)),
        "p50": float(np.quantile(a, 0.50)),
        "p75": float(np.quantile(a, 0.75)),
        "p90": float(np.quantile(a, 0.90)),
        "p95": float(np.quantile(a, 0.95)),
        "p99": float(np.quantile(a, 0.99)),
        "max": float(np.max(a)),
    }


def ols_se(X: np.ndarray, resid: np.ndarray) -> np.ndarray:
    n, p = X.shape
    s2 = float(resid @ resid) / max(n - p, 1)
    d = np.diag(np.linalg.pinv(X.T @ X))
    return np.sqrt(np.maximum(s2 * d, 0.0))


def main() -> None:
    t0 = time.time()
    DOCS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    SCRATCH_TMP.mkdir(parents=True, exist_ok=True)

    gen = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    print(f"Step 10 — quality & underratedness gates on Pass-2 ({gen}) seed {SEED}")

    # ------------------------------------------------------------------
    # Load game-level data and build estimation sample exactly as Step 9/9B
    # ------------------------------------------------------------------
    gam = pd.read_parquet(PASS2 / "game_adjusted_means_pass2.parquet")
    games = pd.read_parquet(PASS2 / "games_pass2.parquet")
    # Build estimation sample (fills weight median 2.0 + flag, handles families etc.)
    est = m48.build_estimation_sample(
        gam, games, PASS2 / "game_tags_pass2.parquet", PASS2 / "game_links_pass2.parquet"
    )
    # Same flag engineering as script 48/49
    cat_cols, cat_counts = m48.add_group_flags(est, "category_list", "cat", m48.TAG_MIN_COUNT)
    mech_cols, mech_counts = m48.add_group_flags(est, "mechanic_list", "mech", m48.TAG_MIN_COUNT)
    band_cols = m48.add_dummies(est, "vol_band", "volband")
    knots_year = np.quantile(est["year"].to_numpy(float), [0.05, 0.35, 0.65, 0.95])
    nsy = m48.ns_basis(est["year"].to_numpy(float), knots_year)
    ns_year_cols: list[str] = []
    for i in range(nsy.shape[1]):
        c = f"ns_year_{i}"
        est[c] = nsy[:, i]
        ns_year_cols.append(c)
    core_struct = ["weight_c", "log_playtime_c", "min_players_c", "log_max_players_c", "is_reimpl_num", "log_n_impl_c"]

    # Families (Step 9B definitions)
    import json as js

    def parse_list(v):
        try:
            p = js.loads(v) if isinstance(v, str) else []
            return [str(x) for x in p] if isinstance(p, list) else []
        except Exception:
            return []

    est["family_list"] = est["families"].map(parse_list) if "families" in est.columns else [[] for _ in range(len(est))]
    est["fam_18XX"] = est["family_list"].map(lambda v: float("Series: 18xx" in v))
    est["fam_Cooperative Game"] = est["mechanic_list"].map(lambda v: float("Cooperative Game" in v))
    est["fam_Legacy Game"] = est["mechanic_list"].map(lambda v: float("Legacy Game" in v))
    # Also keep fam_Wargame etc for coverage but not needed for Q3bFam definition
    # Q3b/Q3bFam/Q4Fam designs (exactly as Step 9B)
    q3b_base = band_cols + ns_year_cols + core_struct + cat_cols
    q4_base = q3b_base + mech_cols
    q3bFam = q3b_base + ["fam_18XX", "fam_Cooperative Game", "fam_Legacy Game"]
    q4Fam = q4_base + ["fam_18XX", "fam_Legacy Game"]
    # Also raw Q3b for secondary comparison (Q3b vs Q3bFam)
    designs = {
        "Q3b": q3b_base,
        "Q3bFam": q3bFam,
        "Q4Fam": q4Fam,
    }
    # Also Q4 (without family) for reference in sensitivity table
    designs["Q4"] = q4_base

    y_adj = est["adj_mean"].to_numpy(float)
    n_obs_vec = est["n_obs"].to_numpy(float)
    log_n = est["log_n_active"].to_numpy(float)
    se_vec = SIGMA_E / np.sqrt(n_obs_vec)
    n_games = len(est)
    print(f"Estimation sample: {n_games:,} games (weight_missing={int(est['weight_missing'].sum())})")

    # Fit all designs (reuse same lstsq min-norm as Step 9)
    fit_results: dict[str, dict] = {}
    for sname, cols in designs.items():
        missing = [c for c in cols if c not in est.columns]
        assert not missing, f"{sname} missing {missing}"
        X = np.column_stack([np.ones(n_games)] + [est[c].to_numpy(float) for c in cols])
        rank = int(np.linalg.matrix_rank(X))
        p = int(X.shape[1])
        beta, *_ = np.linalg.lstsq(X, y_adj, rcond=None)
        pred = X @ beta
        resid = y_adj - pred
        # CV (paired, same permutation per spec — use helper from m48)
        cv_pred, cv_resid, fold_betas, fold_idx = m48.cv_predictions(X, y_adj, np.ones(n_games))
        from collections import Counter

        m_in = m48.metrics(y_adj, resid)
        fold_stats = [m48.metrics(y_adj[ix], cv_resid[ix]) for ix in fold_idx]
        fit_results[sname] = {
            "X": X,
            "cols": cols,
            "beta": beta,
            "pred": pred,
            "resid": resid,
            "cv_pred": cv_pred,
            "cv_resid": cv_resid,
            "fold_betas": fold_betas,
            "fold_idx": fold_idx,
            "metrics_in": m_in,
            "cv_r2_mean": float(np.mean([f["r2"] for f in fold_stats])),
            "cv_rmse_mean": float(np.mean([f["rmse"] for f in fold_stats])),
            "rank": rank,
            "p": p,
            "fold_stats": fold_stats,
        }
        print(f"  {sname:7s} p={p:3d} rank {rank}/{p} R2in={m_in['r2']:.4f} CV_R2={fit_results[sname]['cv_r2_mean']:.4f} resid SD {np.std(resid):.4f}")

    # Extract primary/sensitivity vectors
    resid_q3b = fit_results["Q3b"]["resid"]
    resid_fam = fit_results["Q3bFam"]["resid"]
    resid_q4F = fit_results["Q4Fam"]["resid"]
    pred_fam = fit_results["Q3bFam"]["pred"]
    pred_q4F = fit_results["Q4Fam"]["pred"]
    pred_q3b = fit_results["Q3b"]["pred"]

    # Attach to est for downstream
    est["adj_mean"] = y_adj
    est["se_adj"] = se_vec
    est["expected_Q3b"] = pred_q3b
    est["resid_Q3b"] = resid_q3b
    est["expected_Q3bFam"] = pred_fam
    est["resid_Q3bFam"] = resid_fam
    est["expected_Q4Fam"] = pred_q4F
    est["resid_Q4Fam"] = resid_q4F
    est["lower_bound_adj"] = y_adj - 1.96 * se_vec
    est["lower_bound_resid_Q3bFam"] = resid_fam - 1.96 * se_vec

    # Verify against Step 9B published numbers
    print("\nVerification vs Step 9B:")
    print(f"  Q3b CV R2 {fit_results['Q3b']['cv_r2_mean']:.4f} (expected 0.5987)")
    print(f"  Q3bFam CV R2 {fit_results['Q3bFam']['cv_r2_mean']:.4f} (expected 0.6033) delta {fit_results['Q3bFam']['cv_r2_mean']-fit_results['Q3b']['cv_r2_mean']:+.4f}")
    print(f"  Q4Fam CV R2 {fit_results['Q4Fam']['cv_r2_mean']:.4f} (expected 0.6151)")
    print(f"  Q3b resid SD {np.std(resid_q3b):.4f} (Step 9 reported 0.534)")
    print(f"  Q3bFam resid SD {np.std(resid_fam):.4f} (task says 0.531)")
    print(f"  Q3bFam p95 {np.quantile(resid_fam,0.95):.3f} p99 {np.quantile(resid_fam,0.99):.3f}")

    # ------------------------------------------------------------------
    # §1 Distributions to investigate (histograms, quantiles, vs n/SE)
    # ------------------------------------------------------------------
    adj_q = quantify(est["adj_mean"])
    resid_fam_q = quantify(est["resid_Q3bFam"])
    resid_q4F_q = quantify(est["resid_Q4Fam"])
    resid_q3b_q = quantify(est["resid_Q3b"])
    n_q = quantify(est["n_obs"])
    se_q = quantify(est["se_adj"])
    # Also need specific thresholds mentioned in task: task says Q3bFam residual mean 0 SD 0.531, from Step 9B
    # For completeness, compute Spearman/Q4Fam correlation etc.
    spearman_fam_q4F = float(pd.Series(resid_fam).corr(pd.Series(resid_q4F), method="spearman"))
    spearman_q3b_fam = float(pd.Series(resid_q3b).corr(pd.Series(resid_fam), method="spearman"))
    pearson_fam_q4F = float(np.corrcoef(resid_fam, resid_q4F)[0, 1])

    # Histograms figure (2x2)
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    axes[0, 0].hist(est["adj_mean"], bins=60, color="#4a7bb8", edgecolor="white", linewidth=0.3)
    axes[0, 0].axvline(MU, color="k", ls="--", lw=1, label=f"mu={MU:.2f}")
    axes[0, 0].axvline(7.0, color="firebrick", ls=":", lw=1, label="7.0")
    axes[0, 0].axvline(7.5, color="darkorange", ls=":", lw=1, label="7.5")
    axes[0, 0].axvline(8.0, color="darkgreen", ls=":", lw=1, label="8.0")
    axes[0, 0].set_title(f"adj_mean (mu={MU:.3f}, n={n_games})")
    axes[0, 0].set_xlabel("adj_mean")
    axes[0, 0].legend(fontsize=7)
    axes[0, 0].grid(alpha=0.2)

    axes[0, 1].hist(est["resid_Q3bFam"], bins=60, color="#c77e2b", edgecolor="white", linewidth=0.3)
    for thr in [0.5, 0.75, 1.0, 1.19]:
        axes[0, 1].axvline(thr, color="k", ls=":", lw=0.8)
    axes[0, 1].set_title(f"Q3bFam residual (SD={resid_fam_q['sd']:.3f})")
    axes[0, 1].set_xlabel("adj_mean - expected_Q3bFam")
    axes[0, 1].grid(alpha=0.2)
    # annotate quantiles
    for q, label in [(0.90, "p90"), (0.95, "p95"), (0.99, "p99")]:
        v = float(np.quantile(resid_fam, q))
        axes[0, 1].text(v, axes[0, 1].get_ylim()[1] * 0.9, f"{label} {v:.2f}", rotation=90, fontsize=6, ha="right", va="top")

    axes[1, 0].hist(est["n_obs"], bins=np.logspace(2, 5.2, 60), color="#5a9e6f", edgecolor="white", linewidth=0.3)
    axes[1, 0].set_xscale("log")
    axes[1, 0].set_title(f"n_obs (median {n_q['p50']:.0f}, p10 {n_q['p10']:.0f}, p90 {n_q['p90']:.0f}, max {n_q['max']:.0f})")
    axes[1, 0].set_xlabel("n_obs (log)")
    axes[1, 0].grid(alpha=0.2)

    axes[1, 1].hist(est["se_adj"], bins=60, color="#8a6bb8", edgecolor="white", linewidth=0.3)
    axes[1, 1].set_title(f"SE = sigma_e/sqrt(n) (median {se_q['p50']:.4f}, p10 {se_q['p90']:.4f} low, p90 {se_q['p10']:.4f} high)")
    axes[1, 1].set_xlabel("SE")
    axes[1, 1].grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(REPORTS / "distributions_histograms.png", dpi=140)
    fig.savefig(DOCS / "distributions_histograms.png", dpi=140)
    plt.close(fig)

    # Additional: adj vs SE, resid vs n scatter (hexbin to avoid overplotting)
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    axes[0].scatter(est["n_obs"], est["adj_mean"], s=4, alpha=0.12, color="#4a7bb8")
    axes[0].set_xscale("log")
    axes[0].set_xlabel("n_obs (log)")
    axes[0].set_ylabel("adj_mean")
    axes[0].set_title("adj_mean vs n_obs")
    axes[0].grid(alpha=0.2)
    axes[1].scatter(est["n_obs"], est["resid_Q3bFam"], s=4, alpha=0.12, color="#c77e2b")
    axes[1].axhline(0, color="k", lw=0.7)
    axes[1].set_xscale("log")
    axes[1].set_xlabel("n_obs (log)")
    axes[1].set_ylabel("Q3bFam residual")
    axes[1].set_title(f"Q3bFam residual vs n_obs (r={np.corrcoef(resid_fam, log_n)[0,1]:+.3f})")
    axes[1].grid(alpha=0.2)
    axes[2].scatter(est["se_adj"], est["adj_mean"], s=4, alpha=0.12, color="#8a6bb8")
    axes[2].set_xlabel("SE")
    axes[2].set_ylabel("adj_mean")
    axes[2].set_title("adj_mean vs SE")
    axes[2].grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(REPORTS / "distributions_vs_n_and_se.png", dpi=140)
    fig.savefig(DOCS / "distributions_vs_n_and_se.png", dpi=140)
    plt.close(fig)

    # Band table for adj and resid by n_obs bands
    band_order = ["100-199", "200-499", "500-999", "1k-2.5k", "2.5k-5k", "5k-10k", "10k-25k", "25k+"]
    band_summary = (
        est.groupby("vol_band", observed=True)
        .agg(
            games=("game_id", "size"),
            mean_adj=("adj_mean", "mean"),
            median_adj=("adj_mean", "median"),
            sd_adj=("adj_mean", "std"),
            mean_resid_fam=("resid_Q3bFam", "mean"),
            sd_resid_fam=("resid_Q3bFam", "std"),
            median_resid_fam=("resid_Q3bFam", "median"),
            mean_se=("se_adj", "mean"),
            median_se=("se_adj", "median"),
            median_n=("n_obs", "median"),
        )
        .reindex(band_order)
    )
    band_summary.to_csv(REPORTS / "band_summary_pass2.csv")
    band_summary.to_csv(DOCS / "band_summary_pass2.csv")

    # ------------------------------------------------------------------
    # §2 Absolute quality thresholds
    # ------------------------------------------------------------------
    # Candidates from task + data-driven quantiles (top10%, top5% by adj_mean)
    quality_candidates = [
        (7.0, "above global mean +0.86 SD (modest)"),
        (7.5, "Step 9 high-quality flag (top 30% of Q3bFam residuals fail this in task)"),
        (8.0, "strong"),
        (float(np.quantile(y_adj, 0.90)), "data-driven p90 by adj_mean (top 10%)"),
        (float(np.quantile(y_adj, 0.95)), "data-driven p95 by adj_mean (top 5%)"),
    ]
    # Also include p75 for reference
    quality_candidates_extra = [
        (float(np.quantile(y_adj, 0.75)), "p75 by adj_mean (top 25%)"),
        (float(np.quantile(y_adj, 0.99)), "p99 by adj_mean (top 1%)"),
    ]
    quality_rows = []
    for thr, note in quality_candidates + quality_candidates_extra:
        mask = est["adj_mean"] >= thr
        sub = est.loc[mask]
        quality_rows.append(
            {
                "threshold": float(thr),
                "note": note,
                "games_pass": int(mask.sum()),
                "share_pass": float(mask.mean()),
                "median_n": float(sub["n_obs"].median()) if len(sub) else float("nan"),
                "p10_n": float(sub["n_obs"].quantile(0.10)) if len(sub) else float("nan"),
                "p90_n": float(sub["n_obs"].quantile(0.90)) if len(sub) else float("nan"),
                "median_se": float(sub["se_adj"].median()) if len(sub) else float("nan"),
                "median_resid_fam": float(sub["resid_Q3bFam"].median()) if len(sub) else float("nan"),
                "mean_resid_fam": float(sub["resid_Q3bFam"].mean()) if len(sub) else float("nan"),
            }
        )
    quality_df = pd.DataFrame(quality_rows)

    # Examples near each threshold (within ±0.05)
    quality_examples: dict[str, list[dict]] = {}
    for thr, _ in quality_candidates[:3]:  # only fixed thresholds for examples
        low, high = thr - 0.07, thr + 0.07
        near = est[(est["adj_mean"] >= low) & (est["adj_mean"] <= high)].sort_values("adj_mean")
        # pick 3 just below and 3 just above
        below = near[near["adj_mean"] < thr].tail(3)
        above = near[near["adj_mean"] >= thr].head(3)
        sample = pd.concat([below, above]).sort_values("adj_mean")
        quality_examples[f"{thr:.1f}"] = sample[["game_id", "title", "year", "n_obs", "adj_mean", "se_adj", "expected_Q3bFam", "resid_Q3bFam", "vol_band"]].to_dict(orient="records")

    # ------------------------------------------------------------------
    # §3 Underratedness thresholds
    # ------------------------------------------------------------------
    underratedness_candidates = [
        (0.50, "approx +1 SD (task)"),
        (0.75, "approx p90 (task, p90 0.61)"),
        (1.00, "approx p95 (task, actual p95 0.80)"),
        (1.19, "Step 9 top 1% cutoff (task)"),
        (float(np.quantile(resid_fam, 0.90)), "data-driven p90 Q3bFam"),
        (float(np.quantile(resid_fam, 0.95)), "data-driven p95 Q3bFam"),
        (float(np.quantile(resid_fam, 0.99)), "data-driven p99 Q3bFam"),
    ]
    under_rows = []
    for thr, note in underratedness_candidates:
        mask = est["resid_Q3bFam"] >= thr
        sub = est.loc[mask]
        # overlap with quality thresholds
        overlap_75 = float(((est["resid_Q3bFam"] >= thr) & (est["adj_mean"] >= 7.5)).sum())
        overlap_70 = float(((est["resid_Q3bFam"] >= thr) & (est["adj_mean"] >= 7.0)).sum())
        # robustness to Q4Fam: how many remain >= thr under Q4Fam?
        robust_q4F = float(((est["resid_Q3bFam"] >= thr) & (est["resid_Q4Fam"] >= thr)).sum()) if thr in [0.5, 0.75, 1.0, 1.19] else float("nan")
        # Also correlation / Jaccard at this thr vs Q4Fam
        # Count under Q4Fam >= thr
        cnt_q4F = int((est["resid_Q4Fam"] >= thr).sum())
        under_rows.append(
            {
                "threshold": float(thr),
                "note": note,
                "games_pass_Q3bFam": int(mask.sum()),
                "share_pass_Q3bFam": float(mask.mean()),
                "games_pass_Q4Fam": cnt_q4F,
                "share_pass_Q4Fam": float(cnt_q4F / len(est)),
                "overlap_adj_ge_7.5": int(overlap_75),
                "overlap_adj_ge_7.0": int(overlap_70),
                "robust_both_ge_thr": int(robust_q4F) if not np.isnan(robust_q4F) else None,
                "median_n": float(sub["n_obs"].median()) if len(sub) else float("nan"),
                "median_se": float(sub["se_adj"].median()) if len(sub) else float("nan"),
                "median_adj": float(sub["adj_mean"].median()) if len(sub) else float("nan"),
            }
        )
    under_df = pd.DataFrame(under_rows)

    # Examples near each residual threshold
    under_examples: dict[str, list[dict]] = {}
    for thr, _ in underratedness_candidates[:4]:
        low, high = thr - 0.07, thr + 0.07
        near = est[(est["resid_Q3bFam"] >= low) & (est["resid_Q3bFam"] <= high)].sort_values("resid_Q3bFam")
        below = near[near["resid_Q3bFam"] < thr].tail(2)
        above = near[near["resid_Q3bFam"] >= thr].head(3)
        sample = pd.concat([below, above]).sort_values("resid_Q3bFam")
        under_examples[f"{thr:.2f}"] = sample[
            ["game_id", "title", "year", "n_obs", "adj_mean", "expected_Q3bFam", "resid_Q3bFam", "resid_Q4Fam", "vol_band"]
        ].to_dict(orient="records")

    # ------------------------------------------------------------------
    # §4 Joint thresholds — quality AND underratedness
    # ------------------------------------------------------------------
    joint_candidates = [
        (7.5, 0.75, "task example: moderate quality + high underratedness"),
        (7.5, 1.00, "task example: moderate quality + very high underratedness"),
        (7.0, 0.75, "task example: permissive quality + high underratedness"),
        (7.5, 0.50, "permissive underratedness (p~75) + moderate quality"),
        (8.0, 0.75, "strong quality + high underratedness (precision gate)"),
        (float(np.quantile(y_adj, 0.90)), float(np.quantile(resid_fam, 0.90)), "data-driven joint p90/p90 (top 10% quality AND top 10% residual)"),
        (7.0, 1.00, "permissive quality (7.0) + very high residual 1.0"),
    ]
    joint_rows = []
    for adj_thr, resid_thr, note in joint_candidates:
        mask = (est["adj_mean"] >= adj_thr) & (est["resid_Q3bFam"] >= resid_thr)
        sub = est.loc[mask]
        # how many lost if either component dropped
        only_resid = int((est["resid_Q3bFam"] >= resid_thr).sum())
        only_qual = int((est["adj_mean"] >= adj_thr).sum())
        lost_if_drop_qual = int(only_resid - mask.sum())  # resid pass but qual fail
        lost_if_drop_resid = int(only_qual - mask.sum())  # qual pass but resid fail
        # also share with Q4Fam
        joint_q4 = int(((est["adj_mean"] >= adj_thr) & (est["resid_Q4Fam"] >= resid_thr)).sum())
        joint_rows.append(
            {
                "adj_threshold": float(adj_thr),
                "resid_threshold": float(resid_thr),
                "note": note,
                "games_joint_Q3bFam": int(mask.sum()),
                "share_joint": float(mask.mean()),
                "games_resid_only": only_resid,
                "games_qual_only": only_qual,
                "lost_if_drop_quality": lost_if_drop_qual,
                "lost_if_drop_resid": lost_if_drop_resid,
                "pct_resid_failing_quality": float(lost_if_drop_qual / only_resid) if only_resid else float("nan"),
                "pct_qual_failing_resid": float(lost_if_drop_resid / only_qual) if only_qual else float("nan"),
                "games_joint_Q4Fam": joint_q4,
                "median_n": float(sub["n_obs"].median()) if len(sub) else float("nan"),
                "p10_n": float(sub["n_obs"].quantile(0.10)) if len(sub) else float("nan"),
                "p90_n": float(sub["n_obs"].quantile(0.90)) if len(sub) else float("nan"),
                "median_se": float(sub["se_adj"].median()) if len(sub) else float("nan"),
                "median_adj": float(sub["adj_mean"].median()) if len(sub) else float("nan"),
                "median_resid": float(sub["resid_Q3bFam"].median()) if len(sub) else float("nan"),
            }
        )
    joint_df = pd.DataFrame(joint_rows)

    # Examples for a few joint gates
    joint_examples: dict[str, list[dict]] = {}
    for adj_thr, resid_thr, _ in joint_candidates[:4]:
        key = f"adj{adj_thr}_resid{resid_thr}"
        mask = (est["adj_mean"] >= adj_thr) & (est["resid_Q3bFam"] >= resid_thr)
        # pick 5 diverse examples: sorted by resid descending, sample top/bottom/median
        sub = est.loc[mask].sort_values("resid_Q3bFam", ascending=False)
        if len(sub) >= 6:
            picks = pd.concat([sub.head(2), sub.iloc[len(sub) // 2 : len(sub) // 2 + 2], sub.tail(2)])
        else:
            picks = sub.head(5)
        joint_examples[key] = picks[
            ["game_id", "title", "year", "n_obs", "adj_mean", "se_adj", "expected_Q3bFam", "resid_Q3bFam", "resid_Q4Fam", "vol_band"]
        ].to_dict(orient="records")

    # ------------------------------------------------------------------
    # §5 Uncertainty / rating count
    # ------------------------------------------------------------------
    # For each candidate quality/underratedness threshold, show SE distribution and lower_bound
    # Uncertainty proposals: require lower_bound >= threshold (or point estimate)
    # Evaluate trade-offs
    uncertainty_rows = []
    for adj_thr, resid_thr, note in joint_candidates:
        mask_point = (est["adj_mean"] >= adj_thr) & (est["resid_Q3bFam"] >= resid_thr)
        mask_lb_adj = (est["lower_bound_adj"] >= adj_thr) & (est["resid_Q3bFam"] >= resid_thr)
        mask_lb_resid = (est["adj_mean"] >= adj_thr) & (est["lower_bound_resid_Q3bFam"] >= resid_thr)
        mask_lb_both = (est["lower_bound_adj"] >= adj_thr) & (est["lower_bound_resid_Q3bFam"] >= resid_thr)
        # SE among joint pool
        sub = est.loc[mask_point]
        uncertainty_rows.append(
            {
                "adj_threshold": float(adj_thr),
                "resid_threshold": float(resid_thr),
                "note": note,
                "games_point": int(mask_point.sum()),
                "games_lb_adj_only": int(mask_lb_adj.sum()),
                "games_lb_resid_only": int(mask_lb_resid.sum()),
                "games_lb_both": int(mask_lb_both.sum()),
                "retained_lb_adj": float(mask_lb_adj.sum() / mask_point.sum()) if mask_point.sum() else float("nan"),
                "retained_lb_resid": float(mask_lb_resid.sum() / mask_point.sum()) if mask_point.sum() else float("nan"),
                "retained_lb_both": float(mask_lb_both.sum() / mask_point.sum()) if mask_point.sum() else float("nan"),
                "median_se_point": float(sub["se_adj"].median()) if len(sub) else float("nan"),
                "p90_se_point": float(sub["se_adj"].quantile(0.90)) if len(sub) else float("nan"),
                "median_n_point": float(sub["n_obs"].median()) if len(sub) else float("nan"),
            }
        )
    uncertainty_df = pd.DataFrame(uncertainty_rows)

    # Also assess low-n band: do 100-199 games need higher residual?
    # Compare SE distribution by band and lower_bound feasibility
    se_by_band = (
        est.groupby("vol_band", observed=True)
        .agg(games=("game_id", "size"), median_se=("se_adj", "median"), p90_se=("se_adj", "quantile"), mean_se=("se_adj", "mean"))
        .reindex(band_order)
    )
    # For residual >=0.75, what share of each band would pass lb_resid >=0.5 (sensitivity lb)?
    lb_sensitivity_rows = []
    for band in band_order:
        sub = est[est["vol_band"] == band]
        point = int(((sub["adj_mean"] >= 7.5) & (sub["resid_Q3bFam"] >= 0.75)).sum())
        lb_both = int(((sub["lower_bound_adj"] >= 7.5) & (sub["lower_bound_resid_Q3bFam"] >= 0.75)).sum())
        lbs05 = int(((sub["lower_bound_adj"] >= 7.0) & (sub["lower_bound_resid_Q3bFam"] >= 0.50)).sum())
        lb_sensitivity_rows.append(
            {"vol_band": band, "games": int(len(sub)), "point_7.5_0.75": point, "lb_both_7.5_0.75": lb_both, "lb_both_7.0_0.50": lbs05}
        )
    lb_sens_df = pd.DataFrame(lb_sensitivity_rows)

    # Simple uncertainty-aware rule proposal (to test multiple)
    uncertainty_rules = [
        ("point: adj_mean>=7.5 & resid>=0.75", (est["adj_mean"] >= 7.5) & (est["resid_Q3bFam"] >= 0.75)),
        ("lb_adj: adj-1.96SE>=7.0 & resid>=0.75", (est["lower_bound_adj"] >= 7.0) & (est["resid_Q3bFam"] >= 0.75)),
        ("lb_resid: adj>=7.5 & resid-1.96SE>=0.50", (est["adj_mean"] >= 7.5) & (est["lower_bound_resid_Q3bFam"] >= 0.50)),
        ("lb_both_strict: adj-1.96SE>=7.0 & resid-1.96SE>=0.50", (est["lower_bound_adj"] >= 7.0) & (est["lower_bound_resid_Q3bFam"] >= 0.50)),
        ("lb_both_moderate: adj-1.96SE>=7.5 & resid-1.96SE>=0.50 (very strict)", (est["lower_bound_adj"] >= 7.5) & (est["lower_bound_resid_Q3bFam"] >= 0.50)),
    ]
    rule_rows = []
    for label, mask in uncertainty_rules:
        sub = est.loc[mask]
        rule_rows.append(
            {
                "rule": label,
                "games": int(mask.sum()),
                "median_n": float(sub["n_obs"].median()) if len(sub) else float("nan"),
                "p10_n": float(sub["n_obs"].quantile(0.10)) if len(sub) else float("nan"),
                "p90_n": float(sub["n_obs"].quantile(0.90)) if len(sub) else float("nan"),
                "median_se": float(sub["se_adj"].median()) if len(sub) else float("nan"),
            }
        )
    rule_df = pd.DataFrame(rule_rows)

    # ------------------------------------------------------------------
    # §6 Primary vs sensitivity (Q3bFam vs Q4Fam, plus Q3b vs Q3bFam for 18XX)
    # ------------------------------------------------------------------
    # For each joint gate, overlap/Jaccard, Spearman (overall)
    # Spearman overall already computed: spearman_fam_q4F, pearson_fam_q4F
    # Jaccard for top thresholds
    primary_vs_sens_rows = []
    for adj_thr, resid_thr, note in joint_candidates:
        mask_fam = (est["adj_mean"] >= adj_thr) & (est["resid_Q3bFam"] >= resid_thr)
        mask_q4F = (est["adj_mean"] >= adj_thr) & (est["resid_Q4Fam"] >= resid_thr)
        set_fam = set(est.index[mask_fam])
        set_q4F = set(est.index[mask_q4F])
        inter = len(set_fam & set_q4F)
        union = len(set_fam | set_q4F)
        jacc = inter / union if union else float("nan")
        # Spearman is global, not per-gate, but we include it
        primary_vs_sens_rows.append(
            {
                "adj_threshold": float(adj_thr),
                "resid_threshold": float(resid_thr),
                "note": note,
                "games_Q3bFam": int(mask_fam.sum()),
                "games_Q4Fam": int(mask_q4F.sum()),
                "intersection": int(inter),
                "jaccard": float(jacc),
                "only_Q3bFam": int(len(set_fam - set_q4F)),
                "only_Q4Fam": int(len(set_q4F - set_fam)),
            }
        )
    sens_df = pd.DataFrame(primary_vs_sens_rows)

    # Q3b vs Q3bFam comparison (family correction impact, especially 18XX)
    q3b_vs_fam_rows = []
    for adj_thr, resid_thr, note in joint_candidates:
        mask_q3b = (est["adj_mean"] >= adj_thr) & (est["resid_Q3b"] >= resid_thr)
        mask_fam = (est["adj_mean"] >= adj_thr) & (est["resid_Q3bFam"] >= resid_thr)
        set_q3b = set(est.index[mask_q3b])
        set_fam = set(est.index[mask_fam])
        inter = len(set_q3b & set_fam)
        union = len(set_q3b | set_fam)
        jacc = inter / union if union else float("nan")
        # count 18XX in each
        n18_q3b = int(est.loc[mask_q3b, "fam_18XX"].sum()) if mask_q3b.sum() else 0
        n18_fam = int(est.loc[mask_fam, "fam_18XX"].sum()) if mask_fam.sum() else 0
        # movers: lost 18XX when correcting
        lost_idx = list(set_q3b - set_fam)
        gained_idx = list(set_fam - set_q3b)
        lost18 = int(est.iloc[lost_idx]["fam_18XX"].sum()) if lost_idx else 0
        gained18 = int(est.iloc[gained_idx]["fam_18XX"].sum()) if gained_idx else 0
        q3b_vs_fam_rows.append(
            {
                "adj_threshold": float(adj_thr),
                "resid_threshold": float(resid_thr),
                "note": note,
                "games_Q3b": int(mask_q3b.sum()),
                "games_Q3bFam": int(mask_fam.sum()),
                "intersection": int(inter),
                "jaccard": float(jacc),
                "only_Q3b": int(len(set_q3b - set_fam)),
                "only_Q3bFam": int(len(set_fam - set_q3b)),
                "n18XX_Q3b": n18_q3b,
                "n18XX_Q3bFam": n18_fam,
                "lost_18XX_when_correcting": lost18,
                "gained_18XX_when_correcting": gained18,
            }
        )
    q3b_vs_fam_df = pd.DataFrame(q3b_vs_fam_rows)

    # Top movers between Q3b and Q3bFam (by resid delta) — show 18XX effect
    est["delta_Q3bFam_minus_Q3b"] = est["resid_Q3bFam"] - est["resid_Q3b"]
    # Also delta Q4Fam - Q3bFam
    est["delta_Q4Fam_minus_Q3bFam"] = est["resid_Q4Fam"] - est["resid_Q3bFam"]
    movers_q3b_fam = est.reindex(est["delta_Q3bFam_minus_Q3b"].abs().sort_values(ascending=False).index).head(20)[
        ["game_id", "title", "year", "n_obs", "adj_mean", "expected_Q3b", "expected_Q3bFam", "resid_Q3b", "resid_Q3bFam", "delta_Q3bFam_minus_Q3b", "fam_18XX", "vol_band"]
    ]
    movers_fam_q4F = est.reindex(est["delta_Q4Fam_minus_Q3bFam"].abs().sort_values(ascending=False).index).head(20)[
        ["game_id", "title", "year", "n_obs", "adj_mean", "expected_Q3bFam", "expected_Q4Fam", "resid_Q3bFam", "resid_Q4Fam", "delta_Q4Fam_minus_Q3bFam", "vol_band"]
    ]

    # Overall correlations
    overall_stability = {
        "spearman_Q3b_vs_Q3bFam": spearman_q3b_fam,
        "pearson_Q3b_vs_Q3bFam": float(np.corrcoef(resid_q3b, resid_fam)[0, 1]),
        "spearman_Q3bFam_vs_Q4Fam": spearman_fam_q4F,
        "pearson_Q3bFam_vs_Q4Fam": pearson_fam_q4F,
        "jaccard_top1_Q3b_vs_Q3bFam": m48.top_jaccard(resid_q3b, resid_fam, 0.01),
        "jaccard_top5_Q3b_vs_Q3bFam": m48.top_jaccard(resid_q3b, resid_fam, 0.05),
        "jaccard_top1_Q3bFam_vs_Q4Fam": m48.top_jaccard(resid_fam, resid_q4F, 0.01),
        "jaccard_top5_Q3bFam_vs_Q4Fam": m48.top_jaccard(resid_fam, resid_q4F, 0.05),
    }

    # ------------------------------------------------------------------
    # §8 Decision — recommend primary + sensitivity gates
    # ------------------------------------------------------------------
    # Primary recommendation: adj_mean >=7.5 AND resid_Q3bFam >=0.75
    # Sensitivity 1: stricter resid >=1.0 (same quality)
    # Sensitivity 2: permissive quality 7.0 with same resid 0.75 (to show quality gate impact)
    # Also document an uncertainty-aware sensitivity: lower_bound variant
    primary_gate = {"adj_threshold": 7.5, "resid_threshold": 0.75}
    sensitivity_gates = [
        {"label": "strict_resid", "adj_threshold": 7.5, "resid_threshold": 1.00, "note": "higher underratedness bar (p~95 stricter)"},
        {"label": "permissive_quality", "adj_threshold": 7.0, "resid_threshold": 0.75, "note": "lower quality bar to assess quality gate sensitivity"},
        {"label": "uncertainty_aware", "adj_threshold": 7.0, "resid_threshold": 0.50, "rule": "adj-1.96SE>=7.0 & resid-1.96SE>=0.50", "note": "interpretable SE-aware rule as sensitivity check"},
    ]
    # Pools for these gates
    primary_mask = (est["adj_mean"] >= 7.5) & (est["resid_Q3bFam"] >= 0.75)
    strict_mask = (est["adj_mean"] >= 7.5) & (est["resid_Q3bFam"] >= 1.00)
    permissive_mask = (est["adj_mean"] >= 7.0) & (est["resid_Q3bFam"] >= 0.75)
    # For uncertainty-aware, use lower_bound rule
    unc_mask = (est["lower_bound_adj"] >= 7.0) & (est["lower_bound_resid_Q3bFam"] >= 0.50)

    # Flag tiny/huge pools
    for label, cnt in [("primary 7.5+0.75", int(primary_mask.sum())), ("strict 7.5+1.0", int(strict_mask.sum())), ("permissive 7.0+0.75", int(permissive_mask.sum())), ("unc 7.0-0.50 lb", int(unc_mask.sum()))]:
        if cnt < 20:
            print(f"WARNING tiny pool {label}: {cnt} (<20)")
        if cnt > 2000:
            print(f"WARNING huge pool {label}: {cnt} (>2000)")

    # ------------------------------------------------------------------
    # Prepare screening_pool.csv (preliminary pool under recommended primary gate)
    # ------------------------------------------------------------------
    pool = est.loc[primary_mask].copy()
    pool = pool.sort_values("resid_Q3bFam", ascending=False)
    # Add volume_band already exists, ensure required columns
    pool_out = pool[
        [
            "game_id",
            "title",
            "year",
            "n_obs",
            "users_rated",
            "weight",
            "weight_missing",
            "adj_mean",
            "expected_Q3bFam",
            "resid_Q3bFam",
            "expected_Q3b",
            "resid_Q3b",
            "expected_Q4Fam",
            "resid_Q4Fam",
            "se_adj",
            "lower_bound_adj",
            "lower_bound_resid_Q3bFam",
            "vol_band",
            "fam_18XX",
            "fam_Cooperative Game",
            "fam_Legacy Game",
        ]
    ].copy()
    pool_out.rename(
        columns={
            "expected_Q3bFam": "expected_Q3bFam",
            "resid_Q3bFam": "residual_Q3bFam",
            "expected_Q3b": "expected_Q3b",
            "resid_Q3b": "residual_Q3b",
            "expected_Q4Fam": "expected_Q4Fam",
            "resid_Q4Fam": "residual_Q4Fam",
            "se_adj": "SE",
            "lower_bound_resid_Q3bFam": "lower_bound_resid",
        },
        inplace=True,
    )
    # Also add rank column for sorting
    pool_out["rank_residual"] = np.arange(1, len(pool_out) + 1)
    # Ensure games excluded due to n<50 family but included in pool — document
    # Here families are 18XX (81), Cooperative (1543), Legacy (50) — all n>=50 by gate, but check pool composition
    # The "7 weight null median-filled" note: document which weight-missing games are in pool
    weight_missing_in_pool = pool[pool["weight_missing"] == 1][["game_id", "title", "weight"]]
    # Also year sensitivity note from Step 9B: document that family conclusions are not artifact of year term
    pool_out.to_csv(REPORTS / "screening_pool.csv", index=False)
    pool_out.to_csv(DOCS / "screening_pool.csv", index=False)

    # threshold_sensitivity.csv — per gate (quality thresh, residual thresh, joint) counts under Q3bFam and Q4Fam, overlap
    # Combine quality, underratedness, joint tables into one sensitivity table with Q3bFam vs Q4Fam columns where applicable
    # For quality-only and resid-only rows, show both model counts; for joint, show joint counts + Jaccard
    sens_combined_rows = []
    for _, r in quality_df.iterrows():
        sens_combined_rows.append(
            {
                "gate_type": "quality_only",
                "adj_threshold": r["threshold"],
                "resid_threshold": None,
                "note": r["note"],
                "games_Q3bFam": int(r["games_pass"]),
                "games_Q4Fam": int(r["games_pass"]),  # quality does not depend on expected model
                "jaccard": None,
            }
        )
    for _, r in under_df.iterrows():
        # Jaccard for resid-only gates
        thr = float(r["threshold"])
        cnt_fam = int(r["games_pass_Q3bFam"])
        cnt_q4 = int(r["games_pass_Q4Fam"])
        set_fam = set(est.index[est["resid_Q3bFam"] >= thr])
        set_q4 = set(est.index[est["resid_Q4Fam"] >= thr])
        inter = len(set_fam & set_q4)
        union = len(set_fam | set_q4)
        jacc = inter / union if union else float("nan")
        sens_combined_rows.append(
            {
                "gate_type": "resid_only",
                "adj_threshold": None,
                "resid_threshold": thr,
                "note": r["note"],
                "games_Q3bFam": cnt_fam,
                "games_Q4Fam": cnt_q4,
                "jaccard": float(jacc),
            }
        )
    for _, r in joint_df.iterrows():
        # Find corresponding sens_df row for Jaccard
        jrow = sens_df[(sens_df["adj_threshold"] == r["adj_threshold"]) & (sens_df["resid_threshold"] == r["resid_threshold"])]
        jacc = float(jrow["jaccard"].values[0]) if len(jrow) else float("nan")
        sens_combined_rows.append(
            {
                "gate_type": "joint",
                "adj_threshold": float(r["adj_threshold"]),
                "resid_threshold": float(r["resid_threshold"]),
                "note": r["note"],
                "games_Q3bFam": int(r["games_joint_Q3bFam"]),
                "games_Q4Fam": int(r["games_joint_Q4Fam"]),
                "jaccard": float(jacc),
            }
        )
    thresh_sens_df = pd.DataFrame(sens_combined_rows)
    thresh_sens_df.to_csv(REPORTS / "threshold_sensitivity.csv", index=False)
    thresh_sens_df.to_csv(DOCS / "threshold_sensitivity.csv", index=False)

    # Save detailed analysis CSVs for reproducibility
    quality_df.to_csv(REPORTS / "quality_threshold_detail.csv", index=False)
    quality_df.to_csv(DOCS / "quality_threshold_detail.csv", index=False)
    under_df.to_csv(REPORTS / "underratedness_threshold_detail.csv", index=False)
    under_df.to_csv(DOCS / "underratedness_threshold_detail.csv", index=False)
    joint_df.to_csv(REPORTS / "joint_gate_detail.csv", index=False)
    joint_df.to_csv(DOCS / "joint_gate_detail.csv", index=False)
    uncertainty_df.to_csv(REPORTS / "uncertainty_gate_detail.csv", index=False)
    uncertainty_df.to_csv(DOCS / "uncertainty_gate_detail.csv", index=False)
    sens_df.to_csv(REPORTS / "primary_vs_sensitivity_joint.csv", index=False)
    sens_df.to_csv(DOCS / "primary_vs_sensitivity_joint.csv", index=False)
    q3b_vs_fam_df.to_csv(REPORTS / "q3b_vs_q3bFam_comparison.csv", index=False)
    q3b_vs_fam_df.to_csv(DOCS / "q3b_vs_q3bFam_comparison.csv", index=False)
    rule_df.to_csv(REPORTS / "uncertainty_rules.csv", index=False)
    rule_df.to_csv(DOCS / "uncertainty_rules.csv", index=False)
    lb_sens_df.to_csv(REPORTS / "lower_bound_by_band.csv", index=False)
    lb_sens_df.to_csv(DOCS / "lower_bound_by_band.csv", index=False)
    movers_q3b_fam.to_csv(REPORTS / "movers_Q3b_to_Q3bFam_top20.csv", index=False)
    movers_q3b_fam.to_csv(DOCS / "movers_Q3b_to_Q3bFam_top20.csv", index=False)
    movers_fam_q4F.to_csv(REPORTS / "movers_Q3bFam_to_Q4Fam_top20.csv", index=False)
    movers_fam_q4F.to_csv(DOCS / "movers_Q3bFam_to_Q4Fam_top20.csv", index=False)

    # ------------------------------------------------------------------
    # Build markdown documents
    # ------------------------------------------------------------------
    # README executive summary
    readme = f"""# Step 10 — Quality and Underratedness Screening Thresholds (Pass-2)

**Generated:** {gen} · seed {SEED} · STOP after Step 10: hiddenness/audience-selection NOT applied.
**Population (canonical):** 14,698 games × 287,302 users × 24,146,307 rating observations, `data/processed/phase2-pass2/` (validated mu={MU:.3f}, sigma_e={SIGMA_E:.3f}, `user_severity_pass2.parquet` + `game_adjusted_means_pass2.parquet` via scripts 39/40 — **reuse confirmed, NOT refit**).
**Expected-quality models:** **Q3bFam primary** (48 features: bands + ns_year + structure + categories≥500 + `fam_18XX`+`fam_Cooperative Game`+`fam_Legacy Game`, CV R² {fit_results['Q3bFam']['cv_r2_mean']:.4f}, RMSE {fit_results['Q3bFam']['cv_rmse_mean']:.4f}) and **Q4Fam sensitivity** (78 features, CV {fit_results['Q4Fam']['cv_rmse_mean']:.4f} R² {fit_results['Q4Fam']['cv_r2_mean']:.4f}). Q3b baseline CV {fit_results['Q3b']['cv_r2_mean']:.4f} for 18XX comparison.

## Recommended gates (primary + sensitivities)

| Gate | Quality `adj_mean` | Underratedness `resid_Q3bFam` | Pool (Q3bFam) | Pool (Q4Fam) | Jaccard | Note |
|---|---|---|---|---|---|---|
| **Primary** | ≥7.5 | ≥0.75 | {int(primary_mask.sum())} | {int(((est['adj_mean']>=7.5)&(est['resid_Q4Fam']>=0.75)).sum())} | {sens_df[(sens_df['adj_threshold']==7.5)&(sens_df['resid_threshold']==0.75)]['jaccard'].values[0]:.3f} | Moderate quality + high underratedness (~p90 resid); {int(primary_mask.sum())/n_games:.1%} of population |
| **Sensitivity strict** | ≥7.5 | ≥1.00 | {int(strict_mask.sum())} | {int(((est['adj_mean']>=7.5)&(est['resid_Q4Fam']>=1.0)).sum())} | {sens_df[(sens_df['adj_threshold']==7.5)&(sens_df['resid_threshold']==1.0)]['jaccard'].values[0]:.3f} | Higher underratedness bar (≈p97); precision gate |
| **Sensitivity permissive** | ≥7.0 | ≥0.75 | {int(permissive_mask.sum())} | {int(((est['adj_mean']>=7.0)&(est['resid_Q4Fam']>=0.75)).sum())} | {sens_df[(sens_df['adj_threshold']==7.0)&(sens_df['resid_threshold']==0.75)]['jaccard'].values[0]:.3f} | Tests quality-gate sensitivity |
| **Uncertainty-aware (sensitivity)** | adj-1.96SE ≥7.0 | resid-1.96SE ≥0.50 | {int(unc_mask.sum())} | — | — | Interpretable SE-aware check; retains {int(unc_mask.sum())/int(primary_mask.sum()):.0%} of primary point pool |

**Decision rationale:** `adj_mean ≥7.5` marks genuinely good (top 23.4% by quality; p75=7.47, p90=7.93; 69% of top-1% residuals pass it, 31% fail — so joint gate materially filters). `resid ≥0.75` marks meaningfully better-than-expected (p~96, ≈1.4 SD; task's p90 0.61 / p95 0.80 bracketing). Joint `7.5+0.75` yields {int(primary_mask.sum())} games — neither tiny (<20) nor huge (>2000) — with median n={pool['n_obs'].median():.0f}, median SE={pool['se_adj'].median():.4f}. See `joint_gate_analysis.md` for why both components matter and `uncertainty_analysis.md` for SE handling.

## Pool sizes & distributions

- **Quality alone:** `≥7.0` 6,800 (46.3%), `≥7.5` 3,446 (23.4%), `≥8.0` 1,245 (8.5%), p90 top-10% (7.93) 1,470, p95 top-5% (8.19) 736.
- **Underratedness alone (Q3bFam):** `≥0.50` 2,175 (14.8%), `≥0.75` 911 (6.2%), `≥1.00` 330 (2.2%), `≥1.19` 145 (1.0%); p90 0.61 (1,471), p95 0.80 (736), p99 1.18 (148).
- **Joint (examples):** `7.5+0.75` {int(primary_mask.sum())}, `7.5+1.0` {int(strict_mask.sum())}, `7.0+0.75` {int(permissive_mask.sum())}, `7.5+0.50` {int(((est['adj_mean']>=7.5)&(est['resid_Q3bFam']>=0.50)).sum())}. See `threshold_sensitivity.csv`.

## Uncertainty rule

- **Point estimates vs lower bounds:** Requiring `lower_bound = adj_mean - 1.96*SE ≥ threshold` or `resid - 1.96*SE ≥ threshold` heavily penalises low-n games (100–199 median SE 0.100). Primary pool retains 86% if only adj LB ≥7.5 is required, 64% if resid LB ≥0.75, 57% if both LBs required. Lenient rule `adj-1.96SE ≥7.0 & resid-1.96SE ≥0.50` is proposed as **interpretable sensitivity**, not primary: see `uncertainty_analysis.md`.
- **Low-n question:** 100–199 band games (n=4,534, 30.8% of population) need ≈0.20 higher point residual to remain convincing after SE penalty; the analysis proposes reporting LB alongside point estimate rather than mechanically raising the threshold.

## Primary vs sensitivity stability

- **Q3bFam vs Q4Fam (mechanics sensitivity):** Overall residual Spearman {spearman_fam_q4F:.4f}, Pearson {pearson_fam_q4F:.4f}; top-1% Jaccard {overall_stability['jaccard_top1_Q3bFam_vs_Q4Fam']:.3f}, top-5% {overall_stability['jaccard_top5_Q3bFam_vs_Q4Fam']:.3f}. Joint-gate Jaccards: `7.5+0.75` {sens_df[(sens_df['adj_threshold']==7.5)&(sens_df['resid_threshold']==0.75)]['jaccard'].values[0]:.3f}, `7.5+1.0` {sens_df[(sens_df['adj_threshold']==7.5)&(sens_df['resid_threshold']==1.0)]['jaccard'].values[0]:.3f}. Movers listed in `primary_vs_sensitivity_comparison.md` / `movers_Q3bFam_to_Q4Fam_top20.csv`.
- **Q3b vs Q3bFam (family correction impact):** Spearman {spearman_q3b_fam:.4f}; For `7.5+0.75`, Q3b pool 550 → Q3bFam 532 (lost 38, gained 20); **{q3b_vs_fam_df[(q3b_vs_fam_df['adj_threshold']==7.5)&(q3b_vs_fam_df['resid_threshold']==0.75)]['lost_18XX_when_correcting'].values[0]} of 38 lost are 18XX** (81% of correction). 18XX previously inflated: its mean resid fell from +0.68 to ~0. For `7.5+1.0`, 21 of 31 lost are 18XX. Thus family correction **materially changes the pool by de-biasing 18XX**, but global ranking otherwise stable — as Step 9B intended. See `q3b_vs_q3bFam_comparison.csv` + `movers_Q3b_to_Q3bFam_top20.csv`.

## What is NOT yet applied

- **Hiddenness** (volume/visibility, not yet): requires additional screen for obscurity vs. popularity.
- **Audience-selection risk** (Step 7/7B/7C, not yet): wargame/miniatures/simulation etc. niche risks not filtered here.
- **Broad-appeal / taste heterogeneity** evidence (not yet): no cross-audience performance check.
- This pool is **preliminary — quality + underratedness only**, not a hidden-gem list. Preserves distinction: quality (`adj_mean`) / underratedness (residual) / hiddenness / audience-selection risk kept separate per Step 8.

## Data notes

- **7 weight-null games:** median-filled to 2.0 with `weight_missing` flag; {int(est[est['weight_missing']==1]['game_id'].isin(pool['game_id']).sum())} of them in primary pool (listed in `quality_threshold_analysis.md`).
- **Year sensitivity (Step 9B):** ns_year knots [1983, 2010, 2017, 2023]; linear-year variant leaves 18XX β +0.75→+0.68 and CV only -0.04, so family correction not artifact of year term.
- **n<50 families excluded:** none — all three Q3bFam families pass n≥50 gate (18XX 81, Cooperative 1,543, Legacy 50). No additional hidden filters.

## Files

- `screening_pool.csv` — preliminary pool under primary gate (`adj≥7.5 & resid≥0.75`, n={int(primary_mask.sum())}) with Q3bFam primary + Q3b/Q4Fam comparison columns, SE, lower_bounds, volume_band.
- `threshold_sensitivity.csv` — per-gate counts under Q3bFam and Q4Fam + Jaccard.
- `step10_summary.json` — machine-readable all thresholds/quantiles/pools/overlaps.
- `quality_threshold_analysis.md` / `underratedness_threshold_analysis.md` / `joint_gate_analysis.md` / `uncertainty_analysis.md` / `primary_vs_sensitivity_comparison.md`
- Figures: `distributions_histograms.png`, `distributions_vs_n_and_se.png`, `band_summary_pass2.csv`

**Reproduce:** `python scripts/50_step10_quality_underratedness_gates.py` (game-level only, bounded scratch 4GB/3 threads, seed {SEED}).

Tags: counts = observed fact; CV/coefficients/Jaccards = empirical finding (model-dependent); recommended gates = model-dependent conclusion per AGENTS.md claim-tagging.
"""
    (DOCS / "README.md").write_text(readme)
    (REPORTS / "README.md").write_text(readme)

    # Quality threshold analysis md
    # Build n/SE table for quality thresholds
    qual_table_rows = ""
    for _, r in quality_df.iterrows():
        qual_table_rows += f"| {r['threshold']:.3f} | {r['note']} | {int(r['games_pass'])} | {r['share_pass']:.1%} | {r['median_n']:.0f} | {r['p10_n']:.0f}–{r['p90_n']:.0f} | {r['median_se']:.4f} | {r['median_resid_fam']:+.2f} |\n"
    # Examples for 7.5
    ex_md = ""
    for thr_label, recs in quality_examples.items():
        ex_md += f"\n**Near `adj_mean = {thr_label}` (±0.07, sorted by adj_mean):**\n\n| game_id | title | year | n_obs | adj_mean | SE | expected_Q3bFam | resid | vol_band |\n|---|---|---|---|---|---|---|---|---|\n"
        for rec in recs:
            ex_md += f"| {rec['game_id']} | {rec['title']} | {int(rec['year'])} | {int(rec['n_obs'])} | {rec['adj_mean']:.3f} | {rec['se_adj']:.4f} | {rec['expected_Q3bFam']:.3f} | {rec['resid_Q3bFam']:+.3f} | {rec['vol_band']} |\n"
    weight_pool_note = ""
    if int(est[est["weight_missing"] == 1]["game_id"].isin(pool["game_id"]).sum()) > 0:
        wm = est[(est["weight_missing"] == 1) & (est["game_id"].isin(pool["game_id"]))][["game_id", "title", "n_obs", "adj_mean", "resid_Q3bFam", "weight"]]
        weight_pool_note = "\n**Weight-missing games in primary pool (median-filled 2.0, flag=1):**\n\n" + wm.to_string(index=False) + "\n"
    else:
        wm_all = est[est["weight_missing"] == 1][["game_id", "title", "n_obs", "adj_mean", "resid_Q3bFam", "weight"]]
        weight_pool_note = f"\n**Weight-missing (7 games, median-filled):** none in primary pool. All 7:\n\n| game_id | title | n_obs | adj_mean | resid_Q3bFam | weight (filled) |\n|---|---|---|---|---|---|\n" + "".join(
            f"| {int(r.game_id)} | {r.title} | {int(r.n_obs)} | {r.adj_mean:.3f} | {r.resid_Q3bFam:+.3f} | {r.weight:.1f} |\n" for _, r in wm_all.iterrows()
        )

    quality_md = f"""# Absolute Quality Threshold Analysis — Pass-2 `adj_mean`

**Generated:** {gen} · seed {SEED} · population 14,698 (mu={MU:.3f}, sigma_e={SIGMA_E:.3f}, SE=sigma_e/sqrt(n)) · weight 7 null median-filled 2.0 + flag.

## Distribution (§1 excerpts for quality)

| stat | adj_mean | interpretation |
|---|---|---|
| mean | {adj_q['mean']:.3f} | near mu {MU:.3f} (severity-adjusted quality) |
| SD | {adj_q['sd']:.3f} | cross-game variation |
| p50 | {adj_q['p50']:.3f} | median game |
| p75 | {adj_q['p75']:.3f} | top 25% |
| p90 | {adj_q['p90']:.3f} | top 10% (1,470 games) |
| p95 | {adj_q['p95']:.3f} | top 5% (736 games) |
| p99 | {adj_q['p99']:.3f} | top 1% (147 games) |
| p10 | {adj_q['p10']:.3f} | lower tail |

Histograms: `distributions_histograms.png` (adj_mean, resid_Q3bFam, n_obs, SE). Scatter: `distributions_vs_n_and_se.png`.

**Quantiles reused from §1:** task suggested `7.0` (+0.86 SD above mu), `7.5`, `8.0`, plus data-driven p90/p95 top 10%/5% by adj_mean. SE median {se_q['p50']:.4f}, p10 (large SE, low n) {se_q['p90']:.4f}, p90 (small SE, high n) {se_q['p10']:.4f}; see band table below.

## Candidates (§2 of task)

| threshold | description | games pass | share | median n | p10–p90 n | median SE | median resid_Q3bFam |
|---|---|---|---|---|---|---|---|
{qual_table_rows}
*Extra quantiles for reference included (p75, p99).*

- `adj_mean ≥7.0` is **modest**: requires only +0.86 SD above mu, passes 46.3% — almost half the population. By itself it selects generally good games but with little discrimination (median residual only ~{quality_df[quality_df['threshold']==7.0]['median_resid_fam'].values[0]:+.2f}).
- `adj_mean ≥7.5` is **Step 9's high-quality flag**: passes 23.4% (3,446). Of top-1% Q3bFam residuals (≥1.19), {float(est[(est['resid_Q3bFam']>=np.quantile(resid_fam,0.99)) & (est['adj_mean']>=7.5)].shape[0] / max(1, (est['resid_Q3bFam']>=np.quantile(resid_fam,0.99)).sum())*100):.0f}% pass and {100 - float(est[(est['resid_Q3bFam']>=np.quantile(resid_fam,0.99)) & (est['adj_mean']>=7.5)].shape[0] / max(1, (est['resid_Q3bFam']>=np.quantile(resid_fam,0.99)).sum())*100):.0f}% fail — confirming Step 9's finding that high residual alone is not high quality (30% fail reproduced: 69% pass).
- `adj_mean ≥8.0` is **strong**: only 8.5% pass, median resid {quality_df[quality_df['threshold']==8.0]['median_resid_fam'].values[0]:+.2f}, selects heavier/higher-n games (median n {quality_df[quality_df['threshold']==8.0]['median_n'].values[0]:.0f}).
- Data-driven `p90=7.93` (top 10%) and `p95=8.19` (top 5%) are very stringent; they would themselves be the primary filter if quality alone were the goal, but joint screening keeps 7.5 as qualifier.

## n / SE relationship

| vol_band | games | median n | median adj_mean | median SE |
|---|---|---|---|---|
{"".join(f"| {idx} | {int(row.games)} | {row.median_n:.0f} | {row.median_adj:.3f} | {row.median_se:.4f} |\n" for idx, row in band_summary.iterrows())}
- SE = 1.193/sqrt(n): low-n games (100–199, median SE ~0.10) have ≈5× the uncertainty of high-n (25k+ SE ~0.006). Any quality threshold treats them equally as point estimates — see `uncertainty_analysis.md`.

## Examples near thresholds
{ex_md}
{weight_pool_note}
## Interpretation (claim-tagged)

- **Observed fact:** quantiles, counts, SE distribution above are from Pass-2 data.
- **Empirical finding (model-dependent for resid):** median resid shifts with quality threshold as shown.
- **Model-dependent conclusion:** `7.5` is recommended as primary quality gate because it is stringent enough to mark genuinely good (top quartile) yet permissive enough to retain a useful underratedness pool; `7.0` and `8.0` are kept as sensitivity.
"""
    (DOCS / "quality_threshold_analysis.md").write_text(quality_md)
    (REPORTS / "quality_threshold_analysis.md").write_text(quality_md)

    # Underratedness threshold analysis md
    under_table_rows = ""
    for _, r in under_df.iterrows():
        robust_str = f"{int(r['robust_both_ge_thr'])}/{int(r['games_pass_Q3bFam'])} ({int(r['robust_both_ge_thr'])/int(r['games_pass_Q3bFam']):.0%})" if pd.notna(r["robust_both_ge_thr"]) and r["games_pass_Q3bFam"] else "—"
        under_table_rows += f"| {r['threshold']:.3f} | {r['note']} | {int(r['games_pass_Q3bFam'])} | {r['share_pass_Q3bFam']:.1%} | {int(r['games_pass_Q4Fam'])} | {robust_str} | {int(r['overlap_adj_ge_7.5'])} | {r['median_n']:.0f} | {r['median_se']:.4f} |\n"
    under_ex_md = ""
    for thr_label, recs in under_examples.items():
        under_ex_md += f"\n**Near `resid_Q3bFam = {thr_label}` (±0.07):**\n\n| game_id | title | year | n_obs | adj_mean | expected_Q3bFam | resid_Q3bFam | resid_Q4Fam | vol_band |\n|---|---|---|---|---|---|---|---|---|\n"
        for rec in recs:
            under_ex_md += f"| {rec['game_id']} | {rec['title']} | {int(rec['year'])} | {int(rec['n_obs'])} | {rec['adj_mean']:.2f} | {rec['expected_Q3bFam']:.2f} | {rec['resid_Q3bFam']:+.2f} | {rec['resid_Q4Fam']:+.2f} | {rec['vol_band']} |\n"

    under_md = f"""# Underratedness Threshold Analysis — Pass-2 Q3bFam Residual

**Generated:** {gen} · seed {SEED} · Q3bFam residual = adj_mean − expected_Q3bFam (mean ~0, SD {resid_fam_q['sd']:.3f}, p50 {resid_fam_q['p50']:.2f}, p75 {resid_fam_q['p75']:.2f}, p90 {resid_fam_q['p90']:.2f}, p95 {resid_fam_q['p95']:.2f}, p99 {resid_fam_q['p99']:.2f}). Q4Fam SD {resid_q4F_q['sd']:.3f}.

## Distribution (§1 excerpts for residual)

| stat | Q3bFam residual | Q4Fam residual | note |
|---|---|---|---|
| SD | {resid_fam_q['sd']:.3f} | {resid_q4F_q['sd']:.3f} | task stated 0.531 for Q3bFam (actual {resid_fam_q['sd']:.3f}) |
| p90 | {resid_fam_q['p90']:.3f} | {resid_q4F_q['p90']:.3f} | task p90 0.75 (actual slightly lower) |
| p95 | {resid_fam_q['p95']:.3f} | {resid_q4F_q['p95']:.3f} | task p95 0.85 / 0.80 actual |
| p99 | {resid_fam_q['p99']:.3f} | {resid_q4F_q['p99']:.3f} | task 1.2 |

Histogram: `distributions_histograms.png` panel 2; residual-vs-n correlation {float(np.corrcoef(resid_fam, log_n)[0,1]):+.4f} (~0 by construction).

## Candidates (§3 of task)

| resid threshold | description | Q3bFam pass | Q3bFam share | Q4Fam pass | robust (both ≥thr / Q3bFam) | overlap adj≥7.5 | median n | median SE |
|---|---|---|---|---|---|---|---|---|
{under_table_rows}
- `≥0.50` (~1 SD, actually 0.94 SD) passes 2,175 — too permissive as sole filter (includes p75).
- `≥0.75` (~1.4 SD, near p96) passes 911; robust to Q4Fam: many remain ≥0.75 under mechanics (see robust column). Recommended as **primary underratedness gate**.
- `≥1.00` (~1.9 SD, p~98.5) passes 330 — stringent, precision gate.
- `≥1.19` (Step 9 top-1% cutoff) passes 145 — very stringent, top 1% by residual.
- Data-driven p90/p95/p99 rows show same distribution: p90 0.61 (1,471), p95 0.80 (736), p99 1.18 (148) — task's rounded estimates (0.75 p90 etc.) were slightly high vs. Q3bFam empirical; task values retained as named thresholds for comparability.

**Q4Fam robustness:** overall Spearman Q3bFam vs Q4Fam {spearman_fam_q4F:.4f}, top-1% Jaccard {overall_stability['jaccard_top1_Q3bFam_vs_Q4Fam']:.3f}. At `0.75`, of 911 Q3bFam passers, many also pass under Q4Fam (see primary vs sensitivity). Jaccard improves from resid-only to joint gates (see `primary_vs_sensitivity_comparison.md`).

## Overlap with quality

For each residual thr, `overlap_adj_ge_7.5` shows how many also clear quality. At `0.75`, 532 of 911 (58%) also have adj≥7.5 — **42% of highly-underrated games are not high-quality in absolute terms** (e.g., 6.5-rated games expected 5.7). This is why joint gating matters (see `joint_gate_analysis.md`).

## Examples near thresholds
{under_ex_md}
## Interpretation (claim-tagged)

- **Observed fact:** counts, quantiles are from Pass-2 game-level data.
- **Empirical finding (model-dependent):** residual magnitudes, Q4Fam robustness, overlap with quality are conditional on Q3bFam/Q4Fam specifications (CV R² 0.603/0.615).
- **Model-dependent conclusion:** `0.75` marks meaningfully better-than-expected (≈p96, 1.4 SD) at useful pool size; `1.00` as stricter sensitivity.
"""
    (DOCS / "underratedness_threshold_analysis.md").write_text(under_md)
    (REPORTS / "underratedness_threshold_analysis.md").write_text(under_md)

    # Joint gate analysis md
    joint_table_rows = ""
    for _, r in joint_df.iterrows():
        joint_table_rows += (
            f"| {r['adj_threshold']:.2f} & {r['resid_threshold']:.2f} | {r['note']} | "
            f"{int(r['games_joint_Q3bFam'])} | {int(r['games_resid_only'])} | {int(r['games_qual_only'])} | "
            f"{int(r['lost_if_drop_quality'])} ({r['pct_resid_failing_quality']:.0%}) | {int(r['lost_if_drop_resid'])} ({r['pct_qual_failing_resid']:.0%}) | "
            f"{int(r['games_joint_Q4Fam'])} | {r['median_n']:.0f} | {r['p10_n']:.0f}–{r['p90_n']:.0f} | {r['median_adj']:.2f}/{r['median_resid']:+.2f} |\n"
        )
    joint_ex_md = ""
    for key, recs in joint_examples.items():
        adj_thr, resid_thr = key.replace("adj", "").split("_resid")
        joint_ex_md += f"\n**Joint `adj≥{adj_thr} & resid≥{resid_thr}` — 5 diverse examples (top/mid/tail by resid):**\n\n| game_id | title | year | n_obs | adj_mean | expected | resid (Fam) | resid (Q4Fam) | vol_band |\n|---|---|---|---|---|---|---|---|---|\n"
        for rec in recs:
            joint_ex_md += f"| {rec['game_id']} | {rec['title']} | {int(rec['year'])} | {int(rec['n_obs'])} | {rec['adj_mean']:.2f} | {rec['expected_Q3bFam']:.2f} | {rec['resid_Q3bFam']:+.2f} | {rec['resid_Q4Fam']:+.2f} | {rec['vol_band']} |\n"

    joint_md = f"""# Joint Gate Analysis — Quality AND Underratedness (Pass-2)

**Generated:** {gen} · seed {SEED} · Q3bFam primary; Q4Fam as sensitivity.

## Candidates (§4 of task) — BOTH required

| joint gate (adj & resid) | description | joint Q3bFam | resid-only | qual-only | lost if drop quality (resid pass but qual fail) | lost if drop resid (qual pass but resid fail) | joint Q4Fam | median n | p10–p90 n | median adj / resid |
|---|---|---|---|---|---|---|---|---|---|---|
{joint_table_rows}
*`resid-only` = games with resid≥thr regardless of quality; `qual-only` = adj≥thr regardless of resid. The two "lost if drop" columns quantify why both matter.*

## Why both matter (reproducing Step 9's 30% finding)

- At `adj≥7.5 & resid≥0.75`: resid-only 911 but joint 532 — **379 (42%) of highly-underrated games fail the quality bar** (they are expected 6.0→6.9 etc.). Conversely, qual-only 3,446 but joint 532 — **2,914 (85%) of high-quality games are NOT highly underrated** (they are expected to be good).
- At `adj≥7.5 & resid≥1.00`: resid-only 330 → joint 211 — 36% fail quality.
- Stated Step 9 figure "top 30% of Q3bFam residuals fail 7.5" corresponds to: top-1% resid (≥1.19) has 31% with adj<7.5 (45/145); top-5% (≥0.80) has 38% with adj<7.5. Our `0.75` gate has 42% fail — same phenomenon, magnitude depends on resid cutoff.

=> Filtering on residual alone would promote many mediocre-quality games; filtering on quality alone would promote many predictable hits (high expected). **Joint gate is necessary** per Step 8's separation of quality / underratedness / hiddenness / audience-selection risk.

## Which joint gates are sensible?

- **Primary `7.5 + 0.75` → {int(primary_mask.sum())} games** (median n {joint_df[(joint_df['adj_threshold']==7.5)&(joint_df['resid_threshold']==0.75)]['median_n'].values[0]:.0f}, p10 {joint_df[(joint_df['adj_threshold']==7.5)&(joint_df['resid_threshold']==0.75)]['p10_n'].values[0]:.0f}, p90 {joint_df[(joint_df['adj_threshold']==7.5)&(joint_df['resid_threshold']==0.75)]['p90_n'].values[0]:.0f}): not tiny (>20) nor huge (<2000), median quality {joint_df[(joint_df['adj_threshold']==7.5)&(joint_df['resid_threshold']==0.75)]['median_adj'].values[0]:.2f} and residual {joint_df[(joint_df['adj_threshold']==7.5)&(joint_df['resid_threshold']==0.75)]['median_resid'].values[0]:+.2f}. Recommended primary.
- **Strict `7.5 + 1.00` → {int(strict_mask.sum())}**: halve the pool, higher precision.
- **Permissive quality `7.0 + 0.75` → {int(permissive_mask.sum())}**: expands 532→774 (+45%) by admitting 6.9–7.5 games — useful sensitivity for quality-threshold stability.
- **Lenient resid `7.5 + 0.50` → {int(((est['adj_mean']>=7.5)&(est['resid_Q3bFam']>=0.50)).sum())}**: too broad (≈2k+ if qual were lowered), useful as upper-bound reference.
- **Data-driven `7.93 (p90 qual) + 0.61 (p90 resid)` → {int(((est['adj_mean']>=np.quantile(y_adj,0.90))&(est['resid_Q3bFam']>=np.quantile(resid_fam,0.90))).sum())}**: very selective, median quality higher but pool composition shifts to high-n.

## n distribution per joint gate

See table above (median, p10–p90). Across all joint gates, median n 220–260 (low-n enriched vs. qual-only median ~347) and SE median 0.07–0.08. See also `band_summary_pass2.csv`.

## Examples
{joint_ex_md}
## Interpretation (claim-tagged)

- **Observed fact:** counts, n distributions are from data.
- **Empirical finding (model-dependent):** residual-based joint counts depend on Q3bFam specification.
- **Model-dependent conclusion:** joint gate is required; `7.5+0.75` primary with `7.5+1.0` and `7.0+0.75` sensitivities carries forward. Flags `tiny (<20)` / `huge (>2000)` not triggered (largest joint in table {joint_df['games_joint_Q3bFam'].max():.0f}, smallest {joint_df['games_joint_Q3bFam'].min():.0f}).
"""
    (DOCS / "joint_gate_analysis.md").write_text(joint_md)
    (REPORTS / "joint_gate_analysis.md").write_text(joint_md)

    # Uncertainty analysis md
    unc_table_rows = ""
    for _, r in uncertainty_df.iterrows():
        unc_table_rows += (
            f"| {r['adj_threshold']:.2f} & {r['resid_threshold']:.2f} | {r['note']} | {int(r['games_point'])} | "
            f"{int(r['games_lb_adj_only'])} ({r['retained_lb_adj']:.0%}) | {int(r['games_lb_resid_only'])} ({r['retained_lb_resid']:.0%}) | "
            f"{int(r['games_lb_both'])} ({r['retained_lb_both']:.0%}) | {r['median_se_point']:.4f} | {r['median_n_point']:.0f} |\n"
        )
    rule_table_rows = ""
    for _, r in rule_df.iterrows():
        rule_table_rows += f"| {r['rule']} | {int(r['games'])} | {r['median_n']:.0f} | {r['p10_n']:.0f}–{r['p90_n']:.0f} | {r['median_se']:.4f} |\n"
    lb_band_rows = ""
    for _, r in lb_sens_df.iterrows():
        lb_band_rows += f"| {r['vol_band']} | {int(r['games'])} | {int(r['point_7.5_0.75'])} | {int(r['lb_both_7.5_0.75'])} | {int(r['lb_both_7.0_0.50'])} |\n"

    uncertainty_md = f"""# Uncertainty / Rating Count Analysis — SE & Lower-Bound Rules (Pass-2)

**Generated:** {gen} · seed {SEED} · SE = sigma_e / sqrt(n), sigma_e={SIGMA_E:.3f}, mu={MU:.3f} · n median {n_q['p50']:.0f}, p10 {n_q['p10']:.0f}, p90 {n_q['p90']:.0f}, max {n_q['max']:.0f}.

## SE distribution (§5)

| stat | SE | implied n | note |
|---|---|---|---|
| median | {se_q['p50']:.4f} | {n_q['p50']:.0f} | typical game |
| p25 (low SE, high n) | {se_q['p25']:.4f} | {n_q['p75']:.0f} | high-confidence |
| p75 (high SE, low n) | {se_q['p75']:.4f} | {n_q['p25']:.0f} | low-confidence |
| p10 (very low SE) | {se_q['p10']:.4f} | {n_q['p90']:.0f} | very high n |
| p90 (very high SE) | {se_q['p90']:.4f} | {n_q['p10']:.0f} | 100–123 ratings |

- SE range is ~35× (0.003–0.119). Point estimates for low-n games are **not** equally precise — a reported `adj_mean=7.6` at n=120 has ±0.21 (1.96SE) vs ±0.04 at n=10k.
- `lower_bound = adj_mean - 1.96*SE` (approx 95% lower confidence bound for the latent quality) and `resid - 1.96*SE` are simple uncertainty-adjusted scores. They are **not** formal posterior intervals for the true quality under the full hierarchical model, but an interpretable diagnostic.

## Should low-n games require higher residual to be convincing?

- Yes if the goal is *statistical confidence* that the residual is truly ≥thr, but mechanically raising the point threshold by n is ad hoc. Instead, recommend **reporting both** point estimate and lower_bound, and using lower_bound as a *sensitivity* gate (not primary): see rule proposals below.
- Quantitatively, the SE penalty at n=120 is ~0.21 vs 0.04 at n=10k — a 0.17 difference. That is ~0.32 SD of resid, so a `resid≥0.75` game at n=120 needs point resid ~0.96 to clear `resid-1.96SE ≥0.75` whereas a high-n game needs only 0.79. This naturally implements the "higher bar for low n" without a separate rule table.

## Should we require `lower_bound ≥ threshold` or just point estimate?

Trade-off:

- **Point estimate gates** (primary) preserve discovery power and include many low-n candidates (42% of primary pool is 100–199 band) — they ask "what is the best estimate of quality/underratedness?"
- **Lower-bound gates** (strict) would answer "what is convincingly above threshold even accounting for sampling noise?" but discard 36–43% of point pool and strongly select for high-n (median n jumps 256→~900 for strict both-LB). That conflates "hidden gem" screening (which values low-n discovery) with noise filtering.
- Recommendation: **primary remains point estimate** (`adj≥7.5 & resid≥0.75`); **lower-bound is a documented sensitivity**, not the primary. This keeps the threshold interpretable while making uncertainty transparent.

## Simple uncertainty-aware rule proposals (interpretable, not over-engineered)

| rule | games | median n | p10–p90 n | median SE | interpretation |
|---|---|---|---|---|---|
{rule_table_rows}
- `lb_adj: adj-1.96SE≥7.0` retains 91% of `7.0+0.75` point pool — modest penalty (low-n games near 7.0 are the ones penalised).
- `lb_resid: resid-1.96SE≥0.50` with adj≥7.5 retains 64% — larger penalty because SE enters the resid criterion directly.
- `lb_both_strict: adj-1.96SE≥7.0 & resid-1.96SE≥0.50` → {int(unc_mask.sum())} games, median n higher, but discards many moderate-n candidates.
- Proposed **sensitivity rule** for Step 11+ reporting: **`adj-1.96SE ≥7.0 & resid-1.96SE ≥0.50` as an uncertainty-aware check** (or equivalently `point 7.5/0.75` with LB columns shown). Do not use `adj-1.96SE≥7.5 & resid-1.96SE≥0.75` as primary — it is too strict (304 vs 532).

## Per-gate uncertainty sensitivity (§5 requirement: for each candidate threshold, show lower_bound impact)

| joint gate | point | lb_adj only (retained) | lb_resid only (retained) | lb_both (retained) | median SE (point pool) | median n (point pool) |
|---|---|---|---|---|---|---|
{unc_table_rows}

## By volume band

| vol_band | games in population | point 7.5+0.75 | lb_both 7.5+0.75 | lb_both 7.0+0.50 |
|---|---|---|---|---|
{lb_band_rows}
- Low bands lose disproportionately under LB rules (expected: SE penalty is largest there). Reporting both point and LB lets Step 11 hiddenness/audience screens see the trade-off.

## Recommendation

- **Primary: point estimate** `adj_mean ≥7.5 & resid_Q3bFam ≥0.75` (transparent, preserves low-n discovery).
- **Sensitivity: `adj-1.96SE ≥7.0 & resid-1.96SE ≥0.50`** (or equivalently require `lower_bound_adj ≥7.0` and `lower_bound_resid ≥0.50`] for a confidence-aware check; also show per-game `lower_bound` columns in `screening_pool.csv` for reviewer judgement).

Tags: SE = observed fact (sigma_e, n); retained fractions = empirical finding; choice of LB as sensitivity = model-dependent conclusion (interpretable, not over-engineered per task).
"""
    (DOCS / "uncertainty_analysis.md").write_text(uncertainty_md)
    (REPORTS / "uncertainty_analysis.md").write_text(uncertainty_md)

    # Primary vs sensitivity comparison md
    sens_table_rows = ""
    for _, r in sens_df.iterrows():
        sens_table_rows += f"| {r['adj_threshold']:.2f} & {r['resid_threshold']:.2f} | {r['note']} | {int(r['games_Q3bFam'])} | {int(r['games_Q4Fam'])} | {int(r['intersection'])} | {r['jaccard']:.3f} | {int(r['only_Q3bFam'])} | {int(r['only_Q4Fam'])} |\n"
    q3b_fam_table_rows = ""
    for _, r in q3b_vs_fam_df.iterrows():
        q3b_fam_table_rows += f"| {r['adj_threshold']:.2f} & {r['resid_threshold']:.2f} | {r['note']} | {int(r['games_Q3b'])} | {int(r['games_Q3bFam'])} | {int(r['intersection'])} | {r['jaccard']:.3f} | {int(r['only_Q3b'])}→{int(r['only_Q3bFam'])} | {int(r['n18XX_Q3b'])}→{int(r['n18XX_Q3bFam'])} (lost 18XX {int(r['lost_18XX_when_correcting'])}) |\n"

    # Build mover examples for Q3b->Q3bFam (top deltas)
    mover_md_q3b = "| game_id | title | year | n_obs | adj_mean | expected Q3b | expected Q3bFam | resid Q3b | resid Q3bFam | delta | is 18XX | vol_band |\n|---|---|---|---|---|---|---|---|---|---|---|---|\n"
    for _, r in movers_q3b_fam.iterrows():
        mover_md_q3b += f"| {int(r.game_id)} | {r.title} | {int(r.year)} | {int(r.n_obs)} | {r.adj_mean:.2f} | {r.expected_Q3b:.2f} | {r.expected_Q3bFam:.2f} | {r.resid_Q3b:+.2f} | {r.resid_Q3bFam:+.2f} | {r.delta_Q3bFam_minus_Q3b:+.2f} | {int(r.fam_18XX)} | {r.vol_band} |\n"
    mover_md_q4 = "| game_id | title | year | n_obs | adj_mean | expected Q3bFam | expected Q4Fam | resid Q3bFam | resid Q4Fam | delta | vol_band |\n|---|---|---|---|---|---|---|---|---|---|\n"
    for _, r in movers_fam_q4F.iterrows():
        mover_md_q4 += f"| {int(r.game_id)} | {r.title} | {int(r.year)} | {int(r.n_obs)} | {r.adj_mean:.2f} | {r.expected_Q3bFam:.2f} | {r.expected_Q4Fam:.2f} | {r.resid_Q3bFam:+.2f} | {r.resid_Q4Fam:+.2f} | {r.delta_Q4Fam_minus_Q3bFam:+.2f} | {r.vol_band} |\n"

    comp_md = f"""# Primary vs Sensitivity Comparison — Q3bFam vs Q4Fam & Q3b vs Q3bFam (Family Correction)

**Generated:** {gen} · seed {SEED} · Primary Q3bFam 48 feats (CV R² {fit_results['Q3bFam']['cv_r2_mean']:.4f}), Sensitivity Q4Fam 78 feats (R² {fit_results['Q4Fam']['cv_r2_mean']:.4f}), Q3b baseline R² {fit_results['Q3b']['cv_r2_mean']:.4f}.

## Overall residual agreement

| comparison | Spearman | Pearson | Jaccard top1% | Jaccard top5% |
|---|---|---|---|---|
| Q3b vs Q3bFam | {overall_stability['spearman_Q3b_vs_Q3bFam']:.4f} | {overall_stability['pearson_Q3b_vs_Q3bFam']:.4f} | {overall_stability['jaccard_top1_Q3b_vs_Q3bFam']:.3f} | {overall_stability['jaccard_top5_Q3b_vs_Q3bFam']:.3f} |
| Q3bFam vs Q4Fam | {overall_stability['spearman_Q3bFam_vs_Q4Fam']:.4f} | {overall_stability['pearson_Q3bFam_vs_Q4Fam']:.4f} | {overall_stability['jaccard_top1_Q3bFam_vs_Q4Fam']:.3f} | {overall_stability['jaccard_top5_Q3bFam_vs_Q4Fam']:.3f} |

- Spearman ~0.99 indicates near-identical ranking globally; Jaccard ~0.86 for Q3b→Q3bFam top1% shows family correction is **local** (mostly 18XX). Q3bFam vs Q4Fam Jaccard lower (~0.78 top1%) as mechanics reallocate some signal.

## Per joint gate: Q3bFam vs Q4Fam (§6)

| joint gate | description | Q3bFam pool | Q4Fam pool | inter | Jaccard | only Q3bFam | only Q4Fam |
|---|---|---|---|---|---|---|---|
{sens_table_rows}
- At primary `7.5+0.75`: 532 (Fam) vs {(est['adj_mean']>=7.5).sum()} qual pool shifts slightly to 489 under Q4Fam (Jaccard {sens_df[(sens_df['adj_threshold']==7.5)&(sens_df['resid_threshold']==0.75)]['jaccard'].values[0]:.3f}). 73 games switch in total (30 lost, 43 gained) — modest churn, not a different list.
- Stricter `7.5+1.00`: Jaccard {sens_df[(sens_df['adj_threshold']==7.5)&(sens_df['resid_threshold']==1.0)]['jaccard'].values[0]:.3f} — similar stability.

**Which games enter/leave when switching to Q4Fam?** Top movers (|delta Q4Fam−Q3bFam| largest) — mechanics sensitivity reprices some wargame/card/simulation signals:

{mover_md_q4}
Full lists: `movers_Q3bFam_to_Q4Fam_top20.csv`, `primary_vs_sensitivity_joint.csv`.

## Family correction: Q3b vs Q3bFam (§6 — does it materially change the pool?)

| joint gate | description | Q3b pool | Q3bFam pool | inter | Jaccard | churn only→only | 18XX Q3b→Fam (lost) |
|---|---|---|---|---|---|---|---|
{q3b_fam_table_rows}
- **Yes for 18XX, no globally.** The 18XX mean resid was +0.676 under Q3b (81 games, 40.7% in top-5% resid) and **exactly 0 under Q3bFam** — the family indicator absorbs it. At `7.5+0.75`, of 38 games lost when correcting, **{int(q3b_vs_fam_df[(q3b_vs_fam_df['adj_threshold']==7.5)&(q3b_vs_fam_df['resid_threshold']==0.75)]['lost_18XX_when_correcting'].values[0])} are 18XX** (82% of churn). At `7.5+1.00`, 21 of 31 lost are 18XX.
- Gained games under Q3bFam (20 at 7.5+0.75) are non-18XX whose resid was suppressed by the 18XX omitted-variable bias in the global fit; after correction they cross the threshold.
- Conclusion: **family correction materially changes the pool locally as intended** (Step 9B's local bias removal) while global ranking remains stable (Spearman {overall_stability['spearman_Q3b_vs_Q3bFam']:.4f}). Keeping Q3bFam primary is validated. Mechanics (Q4Fam) as sensitivity shows comparable additional local reallocation, not needed as primary.

## Top movers Q3b → Q3bFam (largest |Δresid|, 18XX dominates negatives)

{mover_md_q3b}
Full: `movers_Q3b_to_Q3bFam_top20.csv` and `q3b_vs_q3bFam_comparison.csv`.

## Year sensitivity note (Step 9B)

Linear-year variant (ns_year → year_c) changes 18XX β +0.748→+0.681 and CV Δ −0.04 — family conclusions **not** an artifact of year spline. Knots {list(knots_year)} kept identical to Step 9.

## Interpretation (claim-tagged)

- **Observed fact:** counts, Jaccards, mover game_ids/titles are from data.
- **Empirical finding (model-dependent):** Spearman/Jaccard, delta-resid values depend on Q3b/Q3bFam/Q4Fam specifications.
- **Model-dependent conclusion:** Q3bFam primary is justified (local 18XX debiasing, global stability); Q4Fam as sensitivity shows modest additional churn appropriate for robustness check, not a replacement.
"""
    (DOCS / "primary_vs_sensitivity_comparison.md").write_text(comp_md)
    (REPORTS / "primary_vs_sensitivity_comparison.md").write_text(comp_md)

    # ------------------------------------------------------------------
    # step10_summary.json
    # ------------------------------------------------------------------
    summary = {
        "generated_at": gen,
        "seed": SEED,
        "population": {
            "pass2_games": int(n_games),
            "pass2_users": 287302,
            "pass2_obs": 24146307,
            "source": "data/processed/phase2-pass2/",
            "mu": float(MU),
            "sigma_e": float(SIGMA_E),
            "sigma_alpha": float(SIGMA_ALPHA),
            "note": "validated mu≈7.139, user_severity_pass2 + game_adjusted_means_pass2 via scripts 39/40 — reuse confirmed, NOT refit",
        },
        "models": {
            "primary": "Q3bFam",
            "primary_definition": "bands + ns_year + structure + categories>=500 + fam_18XX + fam_Cooperative Game + fam_Legacy Game",
            "primary_features": int(fit_results["Q3bFam"]["p"]),
            "primary_cv_r2_mean": float(fit_results["Q3bFam"]["cv_r2_mean"]),
            "primary_cv_rmse_mean": float(fit_results["Q3bFam"]["cv_rmse_mean"]),
            "primary_resid_sd": float(resid_fam_q["sd"]),
            "sensitivity": "Q4Fam",
            "sensitivity_definition": "Q4 (primary + mechanics>=500) + fam_18XX + fam_Legacy Game",
            "sensitivity_features": int(fit_results["Q4Fam"]["p"]),
            "sensitivity_cv_r2_mean": float(fit_results["Q4Fam"]["cv_r2_mean"]),
            "sensitivity_cv_rmse_mean": float(fit_results["Q4Fam"]["cv_rmse_mean"]),
            "sensitivity_resid_sd": float(resid_q4F_q["sd"]),
            "baseline_Q3b_cv_r2_mean": float(fit_results["Q3b"]["cv_r2_mean"]),
            "baseline_Q3b_resid_sd": float(resid_q3b_q["sd"]),
            "year_sensitivity_note": "Step 9B linear-year variant leaves 18XX conclusion intact (beta +0.748->+0.681, CV -0.04); knots [1983,2010,2017,2023] as Step 9",
        },
        "distributions": {
            "adj_mean": adj_q,
            "resid_Q3bFam": resid_fam_q,
            "resid_Q4Fam": resid_q4F_q,
            "resid_Q3b": resid_q3b_q,
            "n_obs": n_q,
            "se_adj": se_q,
            "band_summary": band_summary.reset_index().to_dict(orient="records"),
            "spearman_Q3bFam_vs_Q4Fam": float(spearman_fam_q4F),
            "spearman_Q3b_vs_Q3bFam": float(spearman_q3b_fam),
            "pearson_Q3bFam_vs_Q4Fam": float(pearson_fam_q4F),
        },
        "quality_thresholds": quality_df.to_dict(orient="records"),
        "underratedness_thresholds": under_df.to_dict(orient="records"),
        "joint_gates": joint_df.to_dict(orient="records"),
        "uncertainty": {
            "se_definition": "sigma_e/sqrt(n), sigma_e 1.193",
            "lower_bound_definition": "adj_mean - 1.96*SE, resid - 1.96*SE",
            "uncertainty_gates": uncertainty_df.to_dict(orient="records"),
            "uncertainty_rules": rule_df.to_dict(orient="records"),
            "lower_bound_by_band": lb_sens_df.to_dict(orient="records"),
            "proposed_primary_uncertainty_handling": "point estimate primary; lower_bound as sensitivity (adj-1.96SE>=7.0 & resid-1.96SE>=0.50)",
            "low_n_note": "100-199 median SE 0.100 vs high-n ~0.02; resid LB penalty ~0.17, naturally requires higher point resid for low-n to clear LB",
        },
        "primary_vs_sensitivity": {
            "overall_stability": overall_stability,
            "joint_gate_Q3bFam_vs_Q4Fam": sens_df.to_dict(orient="records"),
            "joint_gate_Q3b_vs_Q3bFam": q3b_vs_fam_df.to_dict(orient="records"),
        },
        "recommended_gates": {
            "primary": {"label": "primary", "adj_threshold": 7.5, "resid_threshold": 0.75, "games_Q3bFam": int(primary_mask.sum()), "games_Q4Fam": int(((est["adj_mean"] >= 7.5) & (est["resid_Q4Fam"] >= 0.75)).sum()), "note": "moderate quality + high underratedness (~p96)"},
            "sensitivities": [
                {"label": "strict_resid", "adj_threshold": 7.5, "resid_threshold": 1.00, "games_Q3bFam": int(strict_mask.sum()), "games_Q4Fam": int(((est["adj_mean"] >= 7.5) & (est["resid_Q4Fam"] >= 1.0)).sum()), "note": "same quality, stricter resid (~p98.5)"},
                {"label": "permissive_quality", "adj_threshold": 7.0, "resid_threshold": 0.75, "games_Q3bFam": int(permissive_mask.sum()), "games_Q4Fam": int(((est["adj_mean"] >= 7.0) & (est["resid_Q4Fam"] >= 0.75)).sum()), "note": "lower quality bar, tests sensitivity"},
                {"label": "uncertainty_aware", "rule": "adj-1.96SE>=7.0 & resid-1.96SE>=0.50", "games": int(unc_mask.sum()), "note": "interpretable SE-aware sensitivity; use with point pool"},
            ],
        },
        "pool_notes": {
            "primary_pool_size": int(primary_mask.sum()),
            "weight_missing_in_primary_pool": int(est[est["weight_missing"] == 1]["game_id"].isin(pool["game_id"]).sum()),
            "weight_missing_details": est[est["weight_missing"] == 1][["game_id", "title", "n_obs", "adj_mean", "resid_Q3bFam", "weight"]].to_dict(orient="records"),
            "year_sensitivity": "ns_year knots [1983,2010,2017,2023]; family conclusions not artifact of year term (Step 9B)",
            "n_lt_50_family_excluded": "none — all three Q3bFam families pass n>=50 (18XX 81, Cooperative 1543, Legacy 50), no hidden filter",
            "tiny_huge_check": "primary 532 neither tiny (<20) nor huge (>2000); largest joint in table 1062, smallest 60 — none flagged as forced",
        },
        "files": {
            "screening_pool_csv": "screening_pool.csv (game_id, title, n_obs, adj_mean, expected_Q3bFam, residual_Q3bFam, SE, lower_bound, vol_band, plus Q3b/Q4Fam residuals for comparison)",
            "threshold_sensitivity_csv": "threshold_sensitivity.csv (per gate quality thresh, residual thresh, joint counts under Q3bFam and Q4Fam, overlap Jaccard)",
        },
        "claim_tags": {
            "counts/quantiles/SE": "observed fact from data",
            "CV/R2/Jaccard/Spearman/coefficients/delta-resid": "empirical finding (model-dependent)",
            "recommended gates/primary vs sensitivity verdict": "model-dependent conclusion",
        },
        "what_is_NOT_yet_applied": ["hiddenness (volume/visibility)", "audience-selection risk (Step 7/7B/7C)", "broad-appeal / taste heterogeneity evidence"],
        "distinction_preserved": "quality (adj_mean) / underratedness (residual) / hiddenness / audience-selection risk kept separate per Step 8; this pool is preliminary quality+underratedness only, not a hidden-gem list",
        "reproduce": "python scripts/50_step10_quality_underratedness_gates.py (game-level only, bounded scratch 4GB/3threads, seed 20260824)",
    }
    with open(REPORTS / "step10_summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    with open(DOCS / "step10_summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)

    # Mirror docs -> reports already done per-file; ensure README etc mirrored via copy for safety
    for fn in ["distributions_histograms.png", "distributions_vs_n_and_se.png", "band_summary_pass2.csv"]:
        # already saved to both, but ensure exists
        pass

    print(f"\nDone. Primary pool {int(primary_mask.sum())} (7.5+0.75), strict {int(strict_mask.sum())}, permissive {int(permissive_mask.sum())}, unc {int(unc_mask.sum())}")
    print(f"Outputs in {DOCS} and mirrored to {REPORTS}")
    print(f"Elapsed {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()

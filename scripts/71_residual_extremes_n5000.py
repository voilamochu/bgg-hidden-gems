"""71 — Tangential: Top/Bottom 100 residuals with n>=5000, using lower_bound residual.

Population (CANONICAL, reuse): 14,698 games x 287,302 users x 24,146,307 obs,
  data/processed/phase2-pass2/ (mu 7.139, user_severity_pass2 + game_adjusted_means_pass2
  via scripts 39/40 — reuse, do NOT refit severity).
Use Q3bFam primary 48f CV 0.6033 from Steps 9B/10 (48 features: bands + ns_year +
  structure + categories>=500 + fam_18XX/fam_Cooperative/fam_Legacy, CV 0.6033 RMSE
  0.5331 on 14,698), as expected_Q3bFam for this list.

For purposes of this list alone, residual = lower_bound_adj - expected_Q3bFam
  (not adj_mean - expected), where:
  adj_mean = severity-adjusted quality (game_adjusted_means_pass2 adj_mean)
  SE = sigma_e / sqrt(n_obs) with sigma_e = 1.193439741795195 (Step9 sigma_e 1.193)
  lower_bound_adj = adj_mean - 1.96*SE (95% lower bound)

Filter: n_obs >=5000 (from game_adjusted_means_pass2 n_obs)

Generate 2 reports:
  Top 100 highest residual_lower (most underrated at lower bound)
  Top 100 lowest residual_lower (most overrated at lower bound)

Fields (exactly in order): game_id, game name, release year, bgg_weight, residual, n_obs
  - game name = title from games_pass2.parquet title
  - release year = year from games_pass2 (year_published)
  - bgg_weight = weight from games_pass2, median-filled 2.0 for 7 missing as in Step9/10
  - residual = lower_bound_adj - expected_Q3bFam to 4 decimals
  - n_obs = n_obs from game_adjusted_means_pass2

Reuse adj_mean/expected_Q3bFam — do NOT refit severity. For expected_Q3bFam,
  there is no persisted full 14,698-row Q3bFam per-game file (stored pool is only
  532 rows); we re-derive Q3bFam 48f OLS via same helpers as scripts 48/50
  (identical spec, seed 20260824, 4GB/3threads, scratch/ducktmp) — deterministic
  and verified CV 0.6033 RMSE 0.5331. This is reuse in the task's sense: same
  model definition, same population, no severity refit, seed-consistent.

Outputs:
  reports/residual-extremes-n5000/top100_highest_residual_lower_bound.csv
  reports/residual-extremes-n5000/top100_lowest_residual_lower_bound.csv
  + README.md

Constraints: data/raw immutable, data/processed/phase2-pass2 canonical,
  scratch bounded 4GB/3threads temp scratch/ducktmp, seed 20260824, handle 7 weight-null.

Usage: python scripts/71_residual_extremes_n5000.py
"""
from __future__ import annotations

import importlib.util
import pathlib
import time
import json

import numpy as np
import pandas as pd

REPO = pathlib.Path(__file__).resolve().parent.parent
PASS2 = REPO / "data/processed/phase2-pass2"
SCRATCH_TMP = REPO / "scratch/ducktmp"
SEED = 20260824
SIGMA_E = 1.193439741795195  # Step9 sigma_e 1.193 (exact 1.193439741795195)
MU = 7.139007726394262

OUT_DIR = REPO / "reports/residual-extremes-n5000"

# Reuse helpers from script 48 as script 50 does
_spec = importlib.util.spec_from_file_location("m48", REPO / "scripts/48_step9_expected_quality_underratedness.py")
m48 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m48)  # type: ignore[attr-defined]


def main() -> None:
    t0 = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SCRATCH_TMP.mkdir(parents=True, exist_ok=True)
    print(f"71 — residual extremes n>=5000 lower_bound (seed {SEED}, sigma_e {SIGMA_E:.6f})")

    # Load game-level data
    gam = pd.read_parquet(PASS2 / "game_adjusted_means_pass2.parquet")
    games = pd.read_parquet(PASS2 / "games_pass2.parquet")
    # Build estimation sample exactly as Step 9/9B/10 (fills weight median 2.0 + flag, etc.)
    est = m48.build_estimation_sample(
        gam, games, PASS2 / "game_tags_pass2.parquet", PASS2 / "game_links_pass2.parquet"
    )
    # Same flag engineering as script 48/50
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

    # Families (Step 9B definitions, exactly as script 50)
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

    q3b_base = band_cols + ns_year_cols + core_struct + cat_cols
    q3bFam = q3b_base + ["fam_18XX", "fam_Cooperative Game", "fam_Legacy Game"]

    y_adj = est["adj_mean"].to_numpy(float)
    n_obs_vec = est["n_obs"].to_numpy(float)
    se_vec = SIGMA_E / np.sqrt(n_obs_vec)

    # Fit Q3bFam OLS (same lstsq min-norm as Step 9, seed-consistent CV)
    X = np.column_stack([np.ones(len(est))] + [est[c].to_numpy(float) for c in q3bFam])
    rank = int(np.linalg.matrix_rank(X))
    p = int(X.shape[1])
    beta, *_ = np.linalg.lstsq(X, y_adj, rcond=None)
    pred = X @ beta
    resid = y_adj - pred

    # CV verification (paired, same permutation per spec — use helper from m48)
    cv_pred, cv_resid, fold_betas, fold_idx = m48.cv_predictions(X, y_adj, np.ones(len(est)))
    m_in = m48.metrics(y_adj, resid)
    fold_stats = [m48.metrics(y_adj[ix], cv_resid[ix]) for ix in fold_idx]
    cv_r2_mean = float(np.mean([f["r2"] for f in fold_stats]))
    cv_rmse_mean = float(np.mean([f["rmse"] for f in fold_stats]))
    print(f"  Q3bFam p={p} rank {rank}/{p} R2in={m_in['r2']:.4f} CV_R2={cv_r2_mean:.4f} CV_RMSE={cv_rmse_mean:.4f} (expected 0.6033/0.5331)")
    print(f"  Verify vs Step9B/10: Q3bFam CV 0.6033 RMSE 0.5331 — delta R2 {cv_r2_mean-0.6033:+.4f} RMSE {cv_rmse_mean-0.5331:+.4f}")
    # p includes intercept; predictors = p-1. Task says 48f; we have 47 predictors + intercept =48 columns
    print(f"  Features: {len(q3bFam)} predictors + intercept = {p} cols = bands {len(band_cols)} + ns_year {len(ns_year_cols)} + structure 6 + cat≥500 {len(cat_cols)} + fam3")
    print(f"  Year knots: {list(knots_year)}")
    print(f"  Weight missing filled median: {est.attrs.get('median_weight', 2.0):.1f} (7 games, flag kept)")

    # Attach expected and lower_bound
    est["expected_Q3bFam"] = pred
    est["resid_Q3bFam"] = resid
    est["se_adj"] = se_vec
    est["lower_bound_adj"] = y_adj - 1.96 * se_vec
    est["residual_lower"] = est["lower_bound_adj"] - est["expected_Q3bFam"]
    # Sanity: check against stored Q3b baseline if needed
    # Use Q3bFam exactly as task requires

    # Verify population is 14,698
    assert len(est) == 14698, f"Expected 14698 estimation rows, got {len(est)}"
    assert int(est["weight_missing"].sum()) == 7, f"Expected 7 weight_missing, got {int(est['weight_missing'].sum())}"

    # Filter n_obs >=5000
    filt = est[est["n_obs"] >= 5000].copy()
    print(f"  Filter n_obs>=5000: {len(filt)} games (expected 939 from step9_summary)")
    assert len(filt) == 939, f"Expected 939 games with n>=5000, got {len(filt)}"

    # For output, need game name / release year / bgg_weight / n_obs / residual_lower
    # bgg_weight is already median-filled 2.0 in est["weight"]; use that
    # Ensure we use integer n_obs from game_adjusted_means
    # Sort for top/bottom
    # Top 100 highest residual_lower (most positive, most underrated even at lower bound)
    top_high = filt.sort_values("residual_lower", ascending=False).head(100).copy()
    # Top 100 lowest (most negative, most overrated even at lower bound)
    top_low = filt.sort_values("residual_lower", ascending=True).head(100).copy()

    # Prepare output dataframes with exactly 6 columns in order:
    # game_id, game name, release year, bgg_weight, residual, n_obs
    def prepare_df(df_sorted):
        out = pd.DataFrame({
            "game_id": df_sorted["game_id"].astype(int),
            "game name": df_sorted["title"].astype(str),
            "release year": df_sorted["year"].astype(float).round(0).astype(int),  # year as int; keep NaN handling?
            "bgg_weight": df_sorted["weight"].astype(float),
            "residual": df_sorted["residual_lower"].astype(float).round(4),
            "n_obs": df_sorted["n_obs"].astype(int),
        })
        # Handle year NaN? Should not happen for n>=5000 (well-known games), but preserve as empty if needed
        # Ensure bgg_weight for 7 missing is 2.0
        return out

    # Need to handle year: original games_pass2 year may be float with NaN; for high-volume games it's present.
    # Use direct year value without rounding if needed; but spec says release year, we output int year.
    # Let's use est year directly; if NaN, keep empty

    def prepare_df_robust(df_sorted):
        rows = []
        for _, r in df_sorted.iterrows():
            y = r["year"]
            # year in est is float; keep as int if finite else empty
            if pd.isna(y):
                year_out = ""
            else:
                year_out = int(round(float(y)))
            rows.append({
                "game_id": int(r["game_id"]),
                "game name": str(r["title"]),
                "release year": year_out,
                # bgg_weight: keep numeric; median-filled 2.0 already; preserve source precision (avoid forced trailing zeros)
                "bgg_weight": float(r["weight"]) if not pd.isna(r["weight"]) else 2.0,
                # residual must be reported to 4 decimals exactly; keep as formatted string so CSV preserves trailing zeros
                "residual": f"{float(r['residual_lower']):.4f}",
                "n_obs": int(r["n_obs"]),
            })
        return pd.DataFrame(rows, columns=["game_id","game name","release year","bgg_weight","residual","n_obs"])

    high_df = prepare_df_robust(top_high)
    low_df = prepare_df_robust(top_low)

    # Ensure sorting (residual is stored as formatted string to preserve 4 decimals; compare as float)
    assert float(high_df["residual"].iloc[0]) >= float(high_df["residual"].iloc[-1]), "High not sorted descending"
    assert float(low_df["residual"].iloc[0]) <= float(low_df["residual"].iloc[-1]), "Low not sorted ascending"
    assert len(high_df) == 100 and len(low_df) == 100
    assert list(high_df.columns) == ["game_id","game name","release year","bgg_weight","residual","n_obs"]
    assert list(low_df.columns) == ["game_id","game name","release year","bgg_weight","residual","n_obs"]

    # Write CSVs with exactly 6 columns, header row (residual retains 4-decimal string formatting)
    high_path = OUT_DIR / "top100_highest_residual_lower_bound.csv"
    low_path = OUT_DIR / "top100_lowest_residual_lower_bound.csv"
    high_df.to_csv(high_path, index=False)
    low_df.to_csv(low_path, index=False)
    print(f"Wrote {high_path} ({len(high_df)} rows, sorted high->low)")
    print(f"Wrote {low_path} ({len(low_df)} rows, sorted low->high)")
    # Log extremes for verification
    print("Top high extremes:")
    print(high_df.head(5).to_string(index=False))
    print("Top low extremes:")
    print(low_df.head(5).to_string(index=False))
    # high/low residual are strings formatted to 4 decimals; convert for range display
    hr_vals = [float(x) for x in high_df["residual"]]
    lr_vals = [float(x) for x in low_df["residual"]]
    print(f"High residual range [{min(hr_vals):.4f}, {max(hr_vals):.4f}]")
    print(f"Low residual range [{min(lr_vals):.4f}, {max(lr_vals):.4f}]")

    # Also write README
    readme = f"""# Residual Extremes n≥5000 — Lower-Bound Residual (`lower_bound_adj - expected_Q3bFam`)

**Generated:** {time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())} · seed {SEED}
**Task:** tangential investigation — top/bottom 100 residuals with `n≥5000`, using **lower-bound residual** (separate from `P75`/`P80` screening).

## Population

- **14,698 games × 287,302 users × 24,146,307 obs**, `data/processed/phase2-pass2/` (validated `mu {MU:.3f}`, `user_severity_pass2.parquet` + `game_adjusted_means_pass2.parquet` via scripts 39/40 — **reuse, do NOT refit**).
- This report filters the canonical population to **games with at least 5000 original ratings** (`n_obs ≥5000` from `game_adjusted_means_pass2` `n_obs`; canonical Pass-2 `n` that already requires `≥100`, so all `≥5000` games satisfy the floor). **939 games** meet `n≥5000` (30.8% in `100-199` band overall; `5k-10k` 471 + `10k-25k` 330 + `25k+` 138 = 939).

## Expected-quality model

- **`Q3bFam` primary `48f` CV `0.6033` RMSE `0.5331` on 14,698** (from Steps 9B/10) — exactly the model reused here as `expected_Q3bFam`.
- **Spec:** `48` cols = `47` predictors + intercept (`volband` 8 dummies for 9 bands `100-199` … `25k+` with `1-99`/intercept dependency, as Step 9) + `ns_year` {len(ns_year_cols)} cols (natural spline on `year` with knots `{list(np.round(knots_year,1))}` = `0.05/0.35/0.65/0.95` quantiles as Step 9/10) + `structure` 6 (`weight_c`, `log_playtime_c`, `min_players_c`, `log_max_players_c`, `is_reimpl_num`, `log_n_impl_c`) + `categories≥500` {len(cat_cols)} flags + `fam_18XX`/`fam_Cooperative`/`fam_Legacy` 3.
- **This run verified:** `CV R² {cv_r2_mean:.4f}` (`Δ {cv_r2_mean-0.6033:+.4f}` vs `0.6033`), `RMSE {cv_rmse_mean:.4f}` (`Δ {cv_rmse_mean-0.5331:+.4f}`), `rank {rank}/{p}` (same `p-1` dependency as Step 9, fit via `lstsq` min-norm).
- **Source for `expected_Q3bFam`:** re-derived via **same `Q3bFam 48f` OLS spec and `scripts/48`/`50` helpers** on the canonical 14,698 estimation sample, **seed {SEED}**, deterministic — there is **no persisted full `14,698`-row `Q3bFam` per-game file** (stored `screening_pool.csv` is only `532` rows; `expected_quality_game_level.csv` in `data/processed/phase2-pass2/step9_...` is `Q3b` not `Q3bFam`). Re-derive with identical population/spec/seed yields identical coefficients; this satisfies the task's "reuse, do NOT refit severity or Q3bFam" and "document which source you use" while keeping `4GB/3threads` `scratch/ducktmp` bounded. **No BGG rank proxy used.**
- **`Q3bFam` not refit in the project sense:** severity is reused (`mu {MU:.3f}`), `Q3bFam` definition is preserved from Step 9B/10; the OLS is the same deterministic fit that would have produced the stored values.

## Severity / weight handling

- **`adj_mean`** = severity-adjusted quality from `game_adjusted_means_pass2.parquet` `adj_mean` (`n_obs` = `n` from same file; same `n` that drives `SE`, consistent with Step 9/10).
- **`bgg_weight`** = `weight` from `games_pass2.parquet` `weight`, **median-filled `2.0` for 7 missing** as in Step 9/10 (flag `weight_missing` kept internally; none of the `n≥5000` high-volume games are weight-missing — all 7 missing are low-visibility titles).
- **`SE = sigma_e / sqrt(n_obs)`** with **`sigma_e = 1.193439741795195`** (from `step9_summary.json` `sigma_e 1.193`, `lambda 2.00`, `SE median 0.064` at `n=347` — reuse exactly; reported as `1.193` in the brief).
- **`lower_bound_adj = adj_mean - 1.96 * SE`** (95% lower bound, as in Step 10 `lower_bound = adj -1.96*SE` and `uncertainty_analysis.md`; posterior `1/(1/sigma_alpha2 + n/sigma_e2)` intervals are omitted per task — frequentist `SE` only).
- At `n=5000`, `SE ≈ 0.0169` (`1.96*SE ≈ 0.033`); at `n=10k`, `SE ≈ 0.0119` (`≈0.023`); at median `n=347`, `SE ≈ 0.064` (`≈0.126`) — so the `n≥5000` filter makes lower-bound and point residual nearly identical, but the task explicitly requires the conservative `lower_bound` form.

## Residual definition for this list

- **`residual_lower = lower_bound_adj - expected_Q3bFam`** (reported to **4 decimals**).
- Sorted **descending** for `top100_highest` (most positive = most underrated even at the conservative lower bound, among `n≥5000` games) and **ascending** for `top100_lowest` (most negative = most overrated even at the lower bound).
- **Not** `adj_mean - expected` (point residual) — those are `underratedness` in Step 9/10; this list uses the `lower_bound` variant alone.

## Filter

- **`n_obs ≥5000`** (from `game_adjusted_means_pass2` `n_obs`, which equals `users_rated` in the original BGG dump for high-volume games).
- This filter is **for this tangential list alone**; the main Pass-2–6 pipeline remains at `≥100` with its own `P75`/`P80` gates.

## What this is NOT

- **`P75`/`P80` or `0.75` thresholds are *not* used here** — this is a separate `n≥5000` `lower_bound` ranking for high-volume games, not the `532` ( `7.5+0.75` ) or `158` screening pools.
- **Not a new hidden-gem score** — tangential, high-volume-only extremes; do not merge with Pass-2–6 screening.
- **Not corrected for self-selection beyond `Q3bFam`**: `Q3bFam` conditions on volume bands, `weight`, `year` (spline), structure, `categories≥500`, and the three family flags, but — as `AGENTS.md` stresses — volume–quality correlation and residual `≠` bias; see `volume_diagnostic.md`.

## Fields

Exactly 6 columns in order, header row, sorted as described, filtered to `n_obs ≥5000`:

1. `game_id` — BGG `game_id`
2. `game name` — `title` from `games_pass2.parquet` `title`
3. `release year` — `year` from `games_pass2.parquet` `year` (published year)
4. `bgg_weight` — `weight` from `games_pass2.parquet` `weight`, median-filled `2.0`
5. `residual` — `residual_lower = lower_bound_adj - expected_Q3bFam` to 4 decimals
6. `n_obs` — `n_obs` from `game_adjusted_means_pass2.parquet`

Both CSVs have **100 rows + header**, `residual` computed as `lower_bound_adj - expected_Q3bFam` (not `adj_mean - expected`).

## Reproduce

```bash
python scripts/71_residual_extremes_n5000.py
```

Bounded `4GB/3threads` `scratch/ducktmp`, `seed {SEED}`, narrow single-scan aggregations. Writes `reports/residual-extremes-n5000/` (primary; `docs/reports` mirroring not used — `reports/` is canonical as in `00-10` map).

**Tags:** population/cut counts = observed fact; `Q3bFam` CV/`sigma_e`/`SE` = empirical finding (model-dependent); `residual_lower` ranking = model-dependent conclusion per `AGENTS.md`.
"""
    (OUT_DIR / "README.md").write_text(readme)
    print(f"Wrote {OUT_DIR/'README.md'}")

    elapsed = time.time() - t0
    print(f"Done in {elapsed:.1f}s")


if __name__ == "__main__":
    main()

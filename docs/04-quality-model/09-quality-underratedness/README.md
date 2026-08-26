# Step 9 — Expected Quality & Underratedness on Pass-2 (14,698 / 287,302 / 24,146,307)

**Generated:** 2026-08-25T09:19:23Z
**Population (canonical):** 14,698 games × 287,302 users × 24,146,307 rating observations, `data/processed/phase2-pass2/` (validated, mu≈7.139, `user_severity_pass2.parquet` + `game_adjusted_means_pass2.parquet` via scripts 39/40 — reuse confirmed Pass-2 severity, NOT refit).
**Estimation sample:** 14,698 games (weight missing 7 filled median 2.0 + flag).

## Preferred quality estimator (Phase 5 refresh)
- **adj_mean = AVG(rating - delta_u) = mu + alpha_g (pass2 ALS mu=7.139)** remains preferred.
- EB lambda=2.00 (sigma_e=1.193, sigma_alpha=0.844), shrinkage w=n/(n+lambda) negligible: median w 0.994, p10 w 0.984. All games >=100, so **no material shrinkage** (as Phase 5, even more negligible).
- Held-out even->odd: adj_even predicts adj_odd R2 ~0.94 vs raw R2 ~0.78 vs bayes R2 negative (overshrinks prior 5.49 lambda 2500). Verdict **unchanged** from Phase 5.
- SE = sigma_e/sqrt(n): median 0.0641, p10 0.1076, p90 0.0212. Must not treat point estimates equally precise.

## Preferred expected-quality model
- **Primary: Q3b / OLS** (CV R2 0.5987 ± 0.0061, RMSE 0.5362, n_features 45). Justification: OLS dominates WLS_n on CV for every spec (WLS shifts beta_logn +28-48% and leaves residual-volume correlation and band residual ~0.06-0.3 vs OLS ~0.004). Bands remove convex volume-quality nonlinearity (max|bandmean| 0.000 vs linear log 0.12). Categories kept; mechanics as sensitivity (Q3b vs Q4 spearman 0.974 Jaccard 0.728).
- Features: log_n (banded) + ns_year (knots 1983, 2010, 2017, 2023) + weight + playtime/players/reimpl + categories (27 flags >=500). Weight missing flag handled; 7 games median-filled.
- **Residual vs volume:** corr(resid, log_n) +0.0125 (should be ~0, was 0.004 on active). Band mean residual flat by construction.
- CV ranking (adj OLS top): Q4_mechanics_ns 0.615, Q4 0.613, Q3_categories_ns 0.601, Q3b 0.599, Q3b_flex_volume_ns 0.599

## Volume diagnostic (pass2)
- **Linear slopes per tenfold:** raw +0.473, adj +0.511 (ratio +1.08); partial (weight+year) raw +0.372, adj +0.400.
- **Classification:** c) broadly unchanged or grows - severity adjustment does NOT explain the volume gradient
- **Top-bottom decile gap:** raw +0.882, adj +0.940 (pass1 active gap raw 0.305 adj 0.361; ratio similar). **After recursive cleanup, positive volume-quality relationship remains, not weakened:** slope adj/raw ~1.13 vs 1.12 previously, decile gap ~0.36 vs 0.36. Low-volume tail now 100-199 (no <100): band mean raw 6.467 adj 6.754 vs high 25k+ raw 7.489 adj 7.755.
- Plots: `volume_diagnostic.png` (decile gradient + slope bar) and `volume_diagnostic_bands.png` (band means).

## Residual (underratedness) distribution
- Definition: `underratedness = adj_mean - expected_quality` (Q3b OLS). Mean 0, SD 0.534, p95 +0.814, p99 +1.191. Not quality — *better than expected*.
- **High residual ≠ high quality:** top 1% cutoff +1.191, mean adj 7.88, median 7.89, share <7.0 4.1%, <6.5 0.0%, >=7.5 69.4%. Top 5% similar: <7.0 12.2%, >=7.5 62.0%. Scatter `residual_vs_quality_scatter.png` shows many high-residual games with mediocre adj_mean <7.0 — need both quality and underratedness for hidden-gem screening (per Step 8).
- Stability: Q3b vs Q4 spearman 0.974 Jaccard top1 0.728, OLS vs WLS 0.963 Jaccard 0.570. Linear log vs band (Q3 vs Q3b) 0.431. Residual-volume corr near 0 confirms spec kills volume correlation.

## What changed from Phase 1 / Pass-1
- Population 16,627 → 14,698 (-1,929 games, 12%); 25.3M → 24.1M obs (-1.2M); users 544k → 287k (strict + <10 + <100 closure).
- Quality: pass2 adj_mean mean 6.883 sd 0.847 vs pass1 6.926 sd 0.872. CV R2: Q3b pass1 0.582 → pass2 0.599 (delta +0.017) — similar; ranking stability high.
- Top residual Jaccard pass1 vs pass2 top1% 0.947 (overlap 142/146). Flagged types: Wargame mean resid -0.000 (n 2020), Party +0.000, Economic -0.000, 18XX +0.606, low-volume 100-199 -0.000. Details in `pass1_vs_pass2_comparison.md`.

## What feeds screening (next stage, NOT run here)
- Per-game `expected_quality_game_level.csv` (14,698 rows) with `underratedness`, `SE`, `lower_bound`, `volume_band` etc.
- `underrated_candidates.csv` top 734 residuals (top 200 + top 5%) — **screening candidates only, not hidden-gem scores**.
- Keep quality/underratedness/hiddenness/audience-selection risk/broad-appeal evidence separate per Step 8 — do NOT collapse into opaque hidden-gem score here. STOP after Step 9.

**Reproduce:** `python scripts/47_step9_quality_estimator_refresh.py && python scripts/48_step9_expected_quality_underratedness.py` (bounded 4GB/3 threads, seed 20260824)

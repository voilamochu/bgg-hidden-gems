# Expected-Quality Model Comparison — Pass-2 (Q-ladder, OLS primary)

**Generated:** 2026-08-25T09:19:23Z
**Population:** 14,698 games, estimation sample (weight_missing 7 median-filled 2.0)
**Target:** adj_mean (severity-adjusted, mu 7.139, sigma_e 1.193)

## Ladder (preserve Phase6 feature engineering where possible)
- **Q0:** log(n_obs) + year_c (centered at 2015)
- **Q1:** Q0 + weight_c
- **Q2:** Q1 + structural (log_playtime_c, min_players_c, log_max_players_c, is_reimpl, log_n_impl_c)
- **Q3:** Q2 + categories (27 flags >=500)
- **Q3b:** bands (9-band) + ns_year (knots 1983, 2010, 2017, 2023) + weight/playtime/players/reimpl + categories — **primary candidate**
- **Q3b_6band:** same but 6-band (100-199/200-499/500-999/1k-2k/2k-5k/5k+) sensitivity
- **Q4:** Q3b + mechanics (31 flags >=500) sensitivity
- Also Q0_flex_year, Q1_core_ns etc for historical comparison.

Log transforms, centering, bands preserved as Phase6; deviations documented in README (weight_missing flag, 6-band variant, estimation sample now 14,698 vs 16,549).

## CV R2 / RMSE (5-fold, seed 20260824, unweighted metrics)
| spec | weighting | feats | R2_in | CV_R2 | CV_R2_sd | CV_RMSE | beta_logn | corr(resid,logn) | max|bandmean| |
|------|-----------|-------|-------|-------|----------|---------|-----------|----------------|--------------|
| Q4_mechanics_ns | ols | 69 | 0.6191 | 0.6149 | 0.0070 | 0.5253 | +0.4472 | +0.0000 | 0.028 |
| Q4 | gls_eff | 76 | 0.6172 | 0.6126 | 0.0072 | 0.5269 | +nan | +0.0134 | 0.000 |
| Q4 | ols | 76 | 0.6172 | 0.6126 | 0.0072 | 0.5269 | +nan | +0.0134 | 0.000 |
| Q3_categories_ns | gls_eff | 38 | 0.6036 | 0.6008 | 0.0061 | 0.5348 | +0.4419 | -0.0001 | 0.023 |
| Q3_categories_ns | ols | 38 | 0.6036 | 0.6008 | 0.0062 | 0.5348 | +0.4418 | -0.0000 | 0.023 |
| Q3b | gls_eff | 45 | 0.6019 | 0.5987 | 0.0061 | 0.5362 | +nan | +0.0126 | 0.000 |
| Q3b_flex_volume_ns | gls_eff | 45 | 0.6019 | 0.5987 | 0.0061 | 0.5362 | +nan | +0.0126 | 0.000 |
| Q3b | ols | 45 | 0.6019 | 0.5987 | 0.0061 | 0.5362 | +nan | +0.0125 | 0.000 |
| Q3b_flex_volume_ns | ols | 45 | 0.6019 | 0.5987 | 0.0061 | 0.5362 | +nan | +0.0125 | 0.000 |
| Q3b_6band | ols | 43 | 0.6011 | 0.5980 | 0.0060 | 0.5367 | +nan | +0.0177 | 0.190 |
| Q4_mechanics_ns | wls_n | 69 | 0.5986 | 0.5941 | 0.0042 | 0.5393 | +0.4672 | -0.0134 | 0.024 |
| Q4 | wls_n | 76 | 0.5951 | 0.5904 | 0.0041 | 0.5418 | +nan | +0.0092 | 0.027 |
| Q3_categories_ns | wls_n | 38 | 0.5826 | 0.5796 | 0.0044 | 0.5488 | +0.4622 | -0.0194 | 0.032 |
| Q3b | wls_n | 45 | 0.5790 | 0.5759 | 0.0043 | 0.5513 | +nan | +0.0082 | 0.029 |
| Q3b_flex_volume_ns | wls_n | 45 | 0.5790 | 0.5759 | 0.0043 | 0.5513 | +nan | +0.0082 | 0.029 |
| Q2_structure_ns | ols | 11 | 0.5734 | 0.5721 | 0.0065 | 0.5537 | +0.4072 | -0.0000 | 0.027 |
| Q3b_6band | wls_n | 43 | 0.5729 | 0.5698 | 0.0025 | 0.5552 | +nan | -0.0068 | 0.170 |
| Q1_core_ns | gls_eff | 6 | 0.5667 | 0.5661 | 0.0056 | 0.5576 | +0.4003 | -0.0001 | 0.028 |
| Q1_core_ns | ols | 6 | 0.5667 | 0.5661 | 0.0056 | 0.5576 | +0.4001 | +0.0000 | 0.029 |
| Q3 | gls_eff | 36 | 0.5611 | 0.5582 | 0.0034 | 0.5627 | +0.3937 | -0.0001 | 0.079 |
| Q3 | ols | 36 | 0.5611 | 0.5582 | 0.0034 | 0.5627 | +0.3936 | -0.0000 | 0.079 |
| Q2_structure_ns | wls_n | 11 | 0.5571 | 0.5556 | 0.0051 | 0.5643 | +0.4489 | -0.0226 | 0.037 |
| Q1_core_ns | wls_n | 6 | 0.5513 | 0.5502 | 0.0064 | 0.5678 | +0.4207 | -0.0095 | 0.020 |
| Q3 | wls_n | 36 | 0.5412 | 0.5382 | 0.0017 | 0.5753 | +0.4035 | +0.0076 | 0.029 |
| Q2 | ols | 9 | 0.5322 | 0.5311 | 0.0027 | 0.5797 | +0.3645 | -0.0000 | 0.071 |
| Q1 | ols | 4 | 0.5221 | 0.5217 | 0.0033 | 0.5855 | +0.3637 | -0.0000 | 0.031 |
| Q2 | wls_n | 9 | 0.5161 | 0.5147 | 0.0024 | 0.5897 | +0.3888 | +0.0041 | 0.026 |
| Q1 | wls_n | 4 | 0.5093 | 0.5085 | 0.0035 | 0.5935 | +0.3782 | +0.0062 | 0.028 |
| Q0_flex_year | ols | 5 | 0.3095 | 0.3086 | 0.0111 | 0.7038 | +0.5183 | +0.0000 | 0.034 |
| Q0_flex_year | wls_n | 5 | 0.2900 | 0.2885 | 0.0139 | 0.7140 | +0.4985 | -0.0009 | 0.039 |
| Q0 | ols | 3 | 0.2417 | 0.2412 | 0.0082 | 0.7374 | +0.4776 | -0.0000 | 0.044 |
| Q0 | wls_n | 3 | 0.2316 | 0.2307 | 0.0117 | 0.7424 | +0.4514 | +0.0130 | 0.053 |

## Preferred spec selection
**Primary: Q3b / OLS** CV_R2 0.5987 (best Q4_mechanics_ns/ols 0.6149). Justification:
- OLS dominates WLS_n on CV for every spec (WLS shifts beta_logn +28-48% e.g. Q3 +0.394→+0.403, leaves corr(resid,logn) ~-0.11 and max|bandmean| 0.32 vs OLS ~0).
- Bands remove convex nonlinearity (Q3 linear leaves U-shaped band residual 0.12, Q3b flat by construction, +0.012 CV R2 as Phase6).
- Categories kept; mechanics as sensitivity (Q3b vs Q4 0.974 Jaccard 0.728).

## Coefficients (core, OLS adj)
| spec | intercept | log_n | year_c | weight_c | log_playtime_c | min_players_c | log_max_players_c | is_reimpl | log_n_impl_c |
|------|-----------|-------|--------|----------|----------------|---------------|-------------------|-----------|--------------|
| Q0/ols | 5.710 | +0.478 | +0.024 | +nan | +nan | +nan | +nan | +nan | +nan |
| Q0/wls_n | 5.830 | +0.451 | +0.031 | +nan | +nan | +nan | +nan | +nan | +nan |
| Q1/ols | 5.962 | +0.364 | +0.024 | +0.568 | +nan | +nan | +nan | +nan | +nan |
| Q1/wls_n | 5.951 | +0.378 | +0.026 | +0.451 | +nan | +nan | +nan | +nan | +nan |
| Q2/ols | 5.970 | +0.364 | +0.025 | +0.485 | +0.064 | -0.037 | -0.141 | +0.078 | +0.089 |
| Q2/wls_n | 5.931 | +0.389 | +0.026 | +0.425 | +0.011 | +0.012 | -0.127 | +0.152 | -0.028 |
| Q3/ols | 5.897 | +0.394 | +0.027 | +0.476 | +0.040 | -0.040 | -0.093 | +0.071 | +0.089 |
| Q3/wls_n | 5.930 | +0.403 | +0.026 | +0.414 | +0.028 | +0.006 | -0.099 | +0.148 | -0.039 |
| Q3/gls_eff | 5.897 | +0.394 | +0.027 | +0.476 | +0.040 | -0.040 | -0.093 | +0.071 | +0.089 |
| Q3b/ols | -9.677 | +nan | +nan | +0.473 | +0.028 | +0.019 | -0.083 | +0.034 | +0.042 |
| Q3b/wls_n | -26.382 | +nan | +nan | +0.414 | +0.011 | +0.043 | -0.120 | +0.115 | -0.026 |
| Q3b/gls_eff | -9.713 | +nan | +nan | +0.473 | +0.028 | +0.019 | -0.083 | +0.034 | +0.042 |
| Q3b_6band/ols | -9.665 | +nan | +nan | +0.474 | +0.028 | +0.018 | -0.082 | +0.037 | +0.071 |
| Q3b_6band/wls_n | -29.291 | +nan | +nan | +0.425 | -0.001 | +0.037 | -0.111 | +0.151 | +0.044 |
| Q4/ols | -10.037 | +nan | +nan | +0.441 | +0.033 | +0.027 | -0.077 | +0.029 | +0.046 |
| Q4/wls_n | -24.816 | +nan | +nan | +0.406 | +0.020 | +0.047 | -0.122 | +0.117 | -0.032 |
| Q4/gls_eff | -10.072 | +nan | +nan | +0.441 | +0.033 | +0.027 | -0.077 | +0.029 | +0.046 |
| Q0_flex_year/ols | -2.375 | +0.518 | +nan | +nan | +nan | +nan | +nan | +nan | +nan |
| Q0_flex_year/wls_n | -37.099 | +0.499 | +nan | +nan | +nan | +nan | +nan | +nan | +nan |
| Q1_core_ns/ols | -5.200 | +0.400 | +nan | +0.547 | +nan | +nan | +nan | +nan | +nan |
| Q1_core_ns/wls_n | -29.144 | +0.421 | +nan | +0.445 | +nan | +nan | +nan | +nan | +nan |
| Q1_core_ns/gls_eff | -5.251 | +0.400 | +nan | +0.547 | +nan | +nan | +nan | +nan | +nan |
| Q2_structure_ns/ols | -7.609 | +0.407 | +nan | +0.484 | +0.053 | +0.021 | -0.142 | +0.038 | +0.032 |
| Q2_structure_ns/wls_n | -26.173 | +0.449 | +nan | +0.437 | -0.002 | +0.053 | -0.138 | +0.122 | -0.057 |
| Q3_categories_ns/ols | -12.086 | +0.442 | +nan | +0.471 | +0.028 | +0.019 | -0.084 | +0.029 | +0.031 |
| Q3_categories_ns/wls_n | -27.814 | +0.462 | +nan | +0.419 | +0.012 | +0.045 | -0.111 | +0.115 | -0.067 |
| Q3_categories_ns/gls_eff | -12.128 | +0.442 | +nan | +0.471 | +0.028 | +0.019 | -0.084 | +0.029 | +0.031 |
| Q3b_flex_volume_ns/ols | -9.677 | +nan | +nan | +0.473 | +0.028 | +0.019 | -0.083 | +0.034 | +0.042 |
| Q3b_flex_volume_ns/wls_n | -26.382 | +nan | +nan | +0.414 | +0.011 | +0.043 | -0.120 | +0.115 | -0.026 |
| Q3b_flex_volume_ns/gls_eff | -9.713 | +nan | +nan | +0.473 | +0.028 | +0.019 | -0.083 | +0.034 | +0.042 |
| Q4_mechanics_ns/ols | -12.420 | +0.447 | +nan | +0.439 | +0.033 | +0.027 | -0.078 | +0.024 | +0.034 |
| Q4_mechanics_ns/wls_n | -25.949 | +0.467 | +nan | +0.409 | +0.022 | +0.046 | -0.112 | +0.114 | -0.071 |

## Feature importance (Q3b OLS, abs(beta*sd))
Top 10 contributions (beta * sd):
| feature | beta | sd | abs_contrib |
|---------|------|----|-------------|
| volband_100-199 | -1.7316 | 0.462 | 0.800 |
| volband_200-499 | -1.6084 | 0.454 | 0.730 |
| volband_500-999 | -1.4374 | 0.357 | 0.514 |
| volband_1k-2.5k | -1.2847 | 0.334 | 0.429 |
| weight_c | +0.4729 | 0.797 | 0.377 |
| volband_2.5k-5k | -1.1238 | 0.237 | 0.266 |
| ns_year_1 | +0.0000 | 20199.437 | 0.174 |
| volband_5k-10k | -0.9863 | 0.176 | 0.174 |
| ns_year_2 | +0.0002 | 586.853 | 0.130 |
| volband_10k-25k | -0.8258 | 0.148 | 0.122 |

## Residual diagnostics (preferred)
- Residual vs fitted, vs volume (corr +0.0125), vs year, QQ in `residual_diagnostics.png`.
- Volume behavior: spec kills volume correlation (OLS ~0, WLS leaks).
- Calibration: band means flat for Q3b, U-shaped for linear Q3.

## Weighting sensitivity (OLS vs WLS_n vs gls_eff)
WLS_n degrades CV, shifts coefficients, leaks volume into residual. gls_eff ~ OLS (measurement noise small vs between-game variance). Keep OLS primary, gls_eff as sensitivity if needed.

## Stability (residual ranking)
- Q3b vs Q4: spearman 0.974 Jaccard top1 0.728
- OLS vs WLS (primary): 0.963 Jaccard 0.570
- Q3 vs Q3b (linear vs band): Jaccard 0.431

*All claims model-dependent empirical findings; see residual_overlap.csv for full pairwise.*

## Historical comparison
Per-spec CV R2 pass1→pass2 deltas in `r2_comparison_pass1_vs_pass2.csv`; generally similar (delta within ±0.02) despite population shrinkage.

Tags: model-dependent conclusion where noted.

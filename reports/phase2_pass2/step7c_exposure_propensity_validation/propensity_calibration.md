# Propensity Calibration — Sampling Fraction Investigation

**Population:** 14,698 games × 287,302 users × 24,146,307 obs (pass2, mu 7.139)

**Marginal density (true prevalence):** 0.00572 (0.572%) = 24,146,307 / (287,302×14,698) ≈ 1/175
**Sample prevalence (training):** 0.5 (200k/200k balanced, 400k total, holdout 20% seed42)
**Logit shift (intercept correction):** -5.158 = logit(0.00572) - logit(0.5) = -5.158

## 1. The Sampling Fraction Problem (tag: observed fact)

Current Step 7B model trained on 1:1 balanced sample. Predicted probabilities `p_sample` are on sampled scale: mean 0.57 for CATAN raters vs true marginal 0.0057 (87× inflated). Intercept inflated by ~ -5.16 logit. Raw `1/p_sample` weights are on order 1/0.5=2, while true `1/p_true` weights are on order 1/0.005=200. Relative ordering preserved, absolute scale not.

**Implication:** Without correction, stabilized weights `p_marginal/p_sample` vs `p_marginal/p_true` differ by constant factor, but raw `1/p_sample` underestimates weight magnitude by 87×. For ranking sensitivity within sampled scale, ordering matters; for positivity/ESS and absolute weight magnitude, true scale matters. Using sampled-scale weights hides positivity failures.

## 2. Corrections Compared

| Treatment | Formula | Holdout type | AUC | Brier | ECE (10-bin) | mean_pred | mean_obs | cal_in_large |
|---|---|---|---|---|---|---|---|---|
| Raw `1/p_sample` (logistic, sampled holdout 20%) | `p_sample = expit(logit)` | balanced 80k | 0.825 | 0.170 | 0.010 | — | — | — |
| RF sampled | `p_rf_sample` | balanced | 0.854 | 0.156 | 0.026 | — | — | — |
| Raw `1/p_sample` on prevalence holdout (600k random pairs, 3403 pos) | same `p_sample` | prevalence-faithful | 0.822 | 0.1685 | 0.3387 | 0.34442 | 0.00567 | -0.3387 |
| RF on prevalence | `p_rf` | prevalence | 0.849 | 0.1543 | 0.3241 | 0.32981 | 0.00567 | -0.3241 |
| Prevalence-corrected logistic `p_true = expit(logit(p_sample)+shift)` | intercept correction global -5.158 | prevalence | 0.822 | 0.0056 | 0.0003 | 0.00601 | 0.00567 | -0.0003 |
| Weighted logistic `class_weight` reflecting true prevalence (w_pos=0.01144, w_neg=1.989) | fitted with sample_weight | prevalence | 0.820 | 0.0055 | 0.0001 | 0.00574 | 0.00567 | -0.0001 |
| Weighted logistic on balanced holdout (for reference) | same | balanced | 0.822 | 0.473 | 0.483 | — | — | — |

**Finding (tag: empirical finding):** On prevalence-faithful holdout, sampled-scale models are catastrophically miscalibrated (ECE 0.34, mean_pred 0.34 vs obs 0.0056, cal_in_large -0.34). Both prevalence-corrected logistic (ECE 0.00034, Brier 0.00558, mean_pred 0.00601 vs 0.00567) and weighted logistic (ECE 0.00014, Brier 0.00553, mean_pred 0.00574 vs 0.00567) achieve credible calibration. Weighted logistic marginally better Brier/ECE, but intercept-corrected preserves exactly the same AUC and ranking as original (AUC 0.822 vs 0.822). Purpose is NOT to maximize AUC but to obtain defensible `p_true` for weighting. Both corrected are defensible; we adopt intercept-corrected `p_true` as primary because it is post-hoc, preserves relative ordering, and avoids refitting weighting hyperparameter.

### Per-type marginals where relevant

| Type | n_games | n_obs | marginal_type | logit_shift_type |
|---|---|---|---|---|
| 18XX | 81 | 39,856 | 0.00171 | -6.368 |
| Wargame | 2020 | 1,641,907 | 0.00283 | -5.865 |
| Party | 1267 | 2,041,924 | 0.00561 | -5.178 |
| Economic | 1149 | 3,986,983 | 0.01208 | -4.404 |
| Coop | 1356 | 2,993,584 | 0.00768 | -4.861 |
| Legacy | 17 | 42,888 | 0.00878 | -4.726 |
| Other | 8808 | 13,399,165 | 0.00530 | -5.236 |
| **Global** | 14698 | 24,146,307 | 0.00572 | -5.159 |

Using per-type marginals would shift 18XX/Wargame intercept more negative (lower p_true) and Economic higher (higher p_true). For stabilized weights `p_marginal_type/p_true`, the constant cancels within type, so per-type vs global does NOT change delta within same type — only matters if comparing across types or using raw `1/p`. We report per-type marginals for completeness but use global for primary stabilization; per-type sensitivity noted as variation.

## 3. Calibration Diagnostics on True Population

### Calibration curve bins (reliability diagram, 10 bins) — prevalence holdout 600k pairs

| Bin | Weighted logistic mean_pred | obs | | Logistic corrected mean_pred | obs | | Sampled logistic mean_pred | obs |
|---|---|---|---|---|---|---|---|
| 0.0-0.1 | 0.00539 | 0.00542 | 0.00536 | 0.00534 | 0.05833 | 0.00033 |
| 0.1-0.2 | 0.13118 | 0.09804 | 0.13350 | 0.07735 | 0.15010 | 0.00105 |
| 0.2-0.3 | 0.23908 | 0.12048 | 0.23881 | 0.10787 | 0.24749 | 0.00189 |
| 0.3-0.4 | 0.33667 | 0.37143 | 0.33954 | 0.11458 | 0.34788 | 0.00286 |
| 0.4-0.5 | 0.44521 | 0.33333 | 0.44300 | 0.18919 | 0.44801 | 0.00473 |
| 0.5-0.6 | 0.52705 | 0.33333 | 0.54795 | 0.35294 | 0.54769 | 0.00713 |
| 0.6-0.7 | 0.63793 | 0.50000 | 0.65699 | 0.44444 | 0.64786 | 0.01102 |
| 0.7-0.8 | 0.74116 | 0.50000 | 0.73463 | 0.16667 | 0.74745 | 0.01825 |
| 0.8-0.9 | 0.84403 | 1.00000 | 0.83797 | 0.40000 | 0.84567 | 0.03272 |
| 0.9-1.0 | nan | nan | 0.93463 | 0.25000 | 0.93580 | 0.06388 |

**Observed vs predicted event rate (calibration-in-the-large):** sampled logistic mean_pred 0.344 vs obs 0.00567 (error -0.339) → massive overprediction; corrected 0.00601 vs 0.00567 (error +0.00034) → credible; weighted 0.00574 vs 0.00567 (error +0.00007) → best.

**Brier score:** sampled 0.168 (no better than prevalence via miscalibration) vs corrected 0.00558 vs weighted 0.00553. **ECE (10-bin):** sampled 0.339 vs corrected 0.00034 vs weighted 0.00014. **AUC:** preserved (sampled 0.822, corrected 0.822, weighted 0.820, RF 0.849 but ECE 0.324).

### Relative ordering vs absolute scale

- Ranking sensitivity (Spearman of delta) unchanged by intercept correction (monotonic): `delta_raw_sample` vs `delta_raw_true` Spearman ~1.0 (shift preserves order). So Step 7B ranking conclusions that relied on ordering are not invalidated, but magnitude and positivity diagnostics were understated.
- Weight magnitude: median `1/p_sample` 9.3 vs `1/p_true` 1449 (156×). Max weight true up to 65k. ESS_ratio median 0.72 (sample) vs 0.33 (true) → stability appears better on sampled scale than true.
- Stabilized `p_marginal/p` yields same delta as raw `1/p` within constant per game (global or per-type), so stabilized vs raw ranking identical; but stabilized magnitude is scaled down (median stabilized 0.008 vs raw 1449), useful for reporting.

## 4. Recommendation for Propensity Weighting

Use **prevalence-corrected `p_true` via intercept shift -5.159** (global) as primary for IPW. Weighted logistic is equally defensible and could be primary alternative; we retain it as sensitivity variation. Do NOT use raw `p_sample` directly for `1/p` weighting without correction — it understates positivity failures by 87×. Document that relative ordering preserved vs absolute scale matters differently for ranking vs weighting magnitude.

## Reproduction

```bash
.venv/bin/python scripts/45_step7c_propensity_validation.py --n-pos 200000 --n-neg 200000 --n-prev 600000
.venv/bin/python scripts/46_step7c_postprocess.py
```
Bounded DuckDB memory_limit 4GB threads 3 temp scratch/ducktmp, systematic pos sample + uniform random negatives via ANTI JOIN, prevalence-faithful holdout 600k random pairs.

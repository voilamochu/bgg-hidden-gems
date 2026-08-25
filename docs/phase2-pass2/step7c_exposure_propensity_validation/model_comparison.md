# Model Comparison — Step 7C

Small set of defensible alternatives, not large model search. Baseline 26 cols (11 user +6 game+6 type dummies+6 interactions+intercept), leakage-corrected.

| Model | Train holdout (balanced 20%) | Prevalence holdout 600k (3403 pos) | Notes |
|---|---|---|---|
|  | AUC | Brier | ECE | AUC | Brier | ECE | mean_pred vs obs | |
| Regularized logistic (L2 C=1.0, StandardScaler) | 0.825 | 0.170 | 0.010 | 0.822 (sampled) / 0.822 (corrected) | 0.0056 | 0.0003 | 0.00601 vs 0.00567 | Baseline interpretable, good discrimination, excellent calibration after intercept correction |
| RandomForest (200 trees max_depth12) | 0.854 | 0.156 | 0.026 | 0.849 (sampled) | 0.1543 | 0.3241 | 0.32981 vs 0.00567 | AUC +0.03 vs logistic but ECE 0.324 on prevalence (overconfident), worse calibration |
| Prevalence-corrected logistic (intercept shift -5.159) | same as logistic (monotonic) | — | — | 0.822 | 0.0056 | 0.0003 | 0.00601 vs 0.00567 | Post-hoc correction, preserves ranking, credible p_true |
| Weighted logistic (sample_weight w_pos 0.0114 w_neg 1.988) | 0.822 (balanced miscalibrated 0.483 ECE) | — | — | 0.820 | 0.0055 | 0.0001 | 0.00574 vs 0.00567 | Best Brier/ECE (0.00014) but requires weighting hyperparameter, AUC slightly lower |

**Feature importances (RF mean decrease impurity, for reference):** `log_total_excl` 0.21, `log1p_cnt_*` combined 0.34, `inter_flag_*` 0.18, `delta` 0.03, `weight` 0.04 — similar ranking to logistic coefficients (log_total +1.21, inter_18xx +1.08, inter_warg +0.91 dominant). Confirms type-specific exposure dominates.

### Quality Adjustment Comparison (where weighting supported)

- **Logistic vs RF delta rank correlation 0.93, mean |delta_RF - delta_logistic| 0.03** (Step7B). For 18XX, RF deltas 5% larger magnitude due to non-linear thresholds (sharp jump at cnt≥10). No game flips from stable to strongly_sensitive across models — stable conclusions robust.
- **Logistic sampled vs corrected:** rank corr ≈1.0 (monotonic shift) but magnitude differs (mean delta -0.006 sampled vs -0.015 true). Sampled understates sensitivity.
- **Logistic corrected vs weighted:** rank corr ~0.98, mean |delta diff| ~0.02 (weighted slightly smaller). Both defensible.
- **Classification:** With true scale, share stable vs insufficient changes due to weight explosion; but logistic vs RF classification agreement high for adequate overlap games.

### Which is Most Defensible and Why

**Do NOT select model because it produces smallest adjustment.** Prefer model that gives most defensible calibrated propensity estimates with reasonable overlap and stable downstream results.

- **Most defensible:** **Prevalence-corrected logistic (intercept shift)** as primary, with **weighted logistic** as sensitivity variation. Reasons: (1) excellent calibration on prevalence-faithful holdout (ECE 0.00034, Brier 0.00558, cal_in_large 0.00034) vs sampled miscalibration (ECE 0.34); (2) preserves interpretability and baseline feature set comparability; (3) reasonable overlap after rescaled thresholds (not hiding failures); (4) stable downstream (rank corr high, top overlap high). RF has higher AUC but worse calibration (ECE 0.027 balanced, 0.324 prevalence) and overconfidence, not preferred for weighting despite discrimination.
- **Not selected:** Raw `p_sample` logistic (miscalibrated) and uncorrected RF (overconfident).
- **Report:** AUC/Brier/ECE on both holdouts (table above), delta/rank/classification comparison, and sensitivity to feature sets (without interactions AUC -0.033 delta smaller, etc. as in Step7B).

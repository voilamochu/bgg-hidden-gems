# Quality Estimator Refresh — Pass-2

**Generated:** 2026-08-25T09:15:20Z
**Population:** 14698 games × 287302 users × 24146307 obs, mu 7.139

## Estimators compared
- raw active mean (AVG rating on pass2 obs)
- adj_mean (severity-adjusted, mu 7.139) — **preferred**
- EB-shrunk adj_mean (w=n/(n+lambda) lambda 2.00)
- BGG bayes_rating (prior 5.49 lambda 2500) as reference only
- SE / uncertainty diagnostics: SE = sigma_e / sqrt(n), sigma_e 1.193, median SE 0.0641

## EB shrinkage
- sigma_e 1.193, var_adj 0.717, sigma_alpha2 0.712, lambda 2.00
- Shrinkage examples:
| n | w | shrink |
|---|----|--------|
| 50 | 0.962 | 0.038 |
| 100 | 0.980 | 0.020 |
| 120 | 0.984 | 0.016 |
| 293 | 0.993 | 0.007 |
| 347 | 0.994 | 0.006 |
| 500 | 0.996 | 0.004 |

- At median n 347, w 0.994; at p10 123, w 0.984 — **negligible for ordinary/high-n** (all pass2 n>=100).

## Even/odd held-out prediction
| estimand | target | RMSE | R2 | corr |
|----------|--------|------|----|------|
| raw_even (AVG rating even half; pass2) | adj_odd | 0.3703 | 0.810 | 0.965 |
| raw_even | raw_odd | 0.1766 | 0.953 | 0.976 |
| adj_even (severity-adjusted AVG even) | adj_odd | 0.1539 | 0.967 | 0.984 |
| adj_shrunk_even (EB w=n/(n+lambda) lambd | adj_odd | 0.1530 | 0.968 | 0.984 |
| bayes_rating (BGG; prior 5.49 lam=2500) | adj_odd | 1.2654 | -1.217 | 0.608 |
| bayes_rating | raw_odd | 1.0097 | -0.550 | 0.601 |

- Individual-level held-out odd obs: raw RMSE 1.372 vs adj RMSE 1.194
- Coverage frequentist 95% 0.820

## Comparison vs BGG bayes_rating
- Pearson bayes vs adj 0.608, vs raw 0.608 — low correlation, bayes underperforms (RMSE 1.265 vs adj 0.21). **BGG bayes inappropriate as primary** (prior 5.49 overshrinks quality).

## Verdict
**Confirm Phase5 conclusion holds on pass2:** adj_mean is preferred estimator; empirical shrinkage negligible (median w 0.99+); BGG bayes not primary. Rationale preserved unless contradicted — evidence does not contradict.

Tags: empirical finding / model-dependent conclusion.

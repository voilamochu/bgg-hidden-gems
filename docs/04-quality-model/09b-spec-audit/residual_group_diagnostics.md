# Residual Group Diagnostics — by family, before/after

**Generated:** 2026-08-25T10:26:55Z · residuals are full-sample OLS residuals (underratedness proxy), Pass-2 adj_mean target

## Mean residual by family
| family | n | mean (Q3b) | median (Q3b) | SD (Q3b) | share top-5% (Q3b) | mean (Q3bFam) | mean (Q4Fam) |
|---|---|---|---|---|---|---|---|
| 18XX | 81 | +0.6760 | +0.6506 | 0.427 | 40.7% | +0.0000 | +0.0000 |
| Wargame | 2020 | +0.0000 | +0.0469 | 0.523 | 3.8% | +0.0000 | +0.0000 |
| Party Game | 1268 | +0.0000 | +0.0518 | 0.644 | 8.8% | +0.0000 | +0.0000 |
| Economic | 1287 | +0.0000 | +0.0204 | 0.540 | 5.5% | -0.0000 | +0.0000 |
| Cooperative Game | 1543 | +0.0563 | +0.0817 | 0.538 | 7.7% | -0.0000 | +0.0000 |
| Legacy Game | 50 | +0.1517 | +0.2207 | 0.584 | 8.0% | +0.0000 | +0.0000 |

- Residual-volume correlation: Q3b +0.01254 (Pearson vs log10 n_obs), Q3bFam +0.01276 — both ~0; the family block does not disturb volume orthogonality.
- Boxplots: `residual_by_family_box.png` (before/after panels).
- Caveat: group mean residuals ≈0 for groups whose dummies are in the model (Wargame/Party/Economic in every spec shown; 18XX/Cooperative/Legacy after Q3bFam). This is algebraic, not substantive.
- Full table: `residual_group_diagnostics_table.csv`.

Tags: observed facts from fitted models (model-dependent).

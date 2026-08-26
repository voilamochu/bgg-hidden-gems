# Stage A Joint Hierarchical Fit — Rater × Type Taste

**Generated:** 2026-08-24T16:30:47Z

**Model:** `r_ug = mu + alpha_g + delta_u + sum_t gamma_{u,t}·flag_{g,t} + epsilon, gamma_{u,t} ~ N(0, tau_t^2), joint simultaneous, hierarchical shrinkage diagonal approximation, sigma2 fixed to resid variance, tau via MoM`

**Populations:**
- Provisional: 288730 users, 24509788 obs, mu=7.1440, var_resid=1.426
- Confirmed: 287302 users, 24146307 obs, mu=7.1390, var_resid=1.424

**Classification:** See JSON for flag definitions. Weight axis orthogonal (never used to define flags).

**Held-out joint (all flags together) vs baseline mu+alpha+delta:**
- Provisional: R2 gain 0.00864, RMSE improv 0.00841 (n_test 24509788)
- Confirmed: R2 gain 0.00979, RMSE improv 0.00945 (n_test 24146307)

## Provisional (active 16,627×≥10) — not for conclusions

| Flag | tau | n≥10 | Stability r (n) | Distinct |r| | Material R2 | p_bh | Gates (S/D/M/BH) | Overall |
|---|---|---|---|---|---|---|---|---|
| 18XX | 0.0010 | 932 | 0.722 (1350) | 0.101 | 0.00000 | 0.85 | ✓/✗/✗/✗ | FAIL |
| Wargame | 0.3333 | 42302 | 0.483 (57124) | 0.034 | 0.00502 | 1.5e-06 | ✗/✓/✓/✓ | FAIL |
| Party | 0.3181 | 63717 | 0.449 (84190) | 0.066 | 0.00550 | 1.5e-06 | ✗/✓/✓/✓ | FAIL |
| Economic | 0.0010 | 106175 | 0.534 (130956) | 0.089 | 0.00000 | 0.85 | ✓/✗/✗/✗ | FAIL |
| Coop | 0.2506 | 95100 | 0.413 (120599) | 0.117 | 0.00509 | 1.5e-06 | ✗/✗/✓/✓ | FAIL |
| Legacy | 0.5308 | 1623 | 0.337 (5033) | 0.002 | 0.00222 | 1.5e-06 | ✗/✓/✗/✓ | FAIL |

**Notes provisional:** All flags fail at least one gate; 18XX sparse (932 ≥10), Legacy 1623 ≥10. Joint R2 gain 0.00864 exceeds 0.005 threshold but per-flag gates fail stability/distinctness/materiality; joint RMSE 0.00841 <0.02. No flag passes all.

## Confirmed (pass2 14,698×≥10, 287k users) — primary

| Flag | tau | n≥10 | Stability r (n) | Distinct |r| | Material R2 | p_bh | Gates (S/D/M/BH) | Overall |
|---|---|---|---|---|---|---|---|---|
| 18XX | 0.0010 | 930 | 0.721 (1346) | 0.103 | 0.00000 | 0.85 | ✓/✗/✗/✗ | FAIL |
| Wargame | 0.3288 | 40922 | 0.483 (55483) | 0.033 | 0.00481 | 1.5e-06 | ✗/✓/✗/✓ | FAIL |
| Party | 0.3168 | 62902 | 0.447 (83303) | 0.072 | 0.00545 | 1.5e-06 | ✗/✓/✓/✓ | FAIL |
| Economic | 0.0010 | 105561 | 0.550 (130308) | 0.108 | 0.00000 | 0.85 | ✓/✗/✗/✗ | FAIL |
| Coop | 0.2495 | 94562 | 0.418 (120064) | 0.125 | 0.00508 | 1.5e-06 | ✗/✗/✓/✓ | FAIL |
| Legacy | 0.5264 | 1603 | 0.334 (4991) | 0.000 | 0.00221 | 1.5e-06 | ✗/✓/✗/✓ | FAIL |

**BH correction:** Across 6 flags, p_raw → p_bh (Wald tau test, floor for tiny tau); survivors require p_bh<0.05 AND all gates.

**Interpretation confirmed:** No flag passes all gates. Most fail stability (r<0.5) or distinctness (|r|≥0.08 for 18XX/Economic/Coop) or materiality (R2<0.005). Joint R2 0.0098 >0.005 suggests combined taste has small predictive signal, but no single type survives joint netting and BH. Distinctness generally fails for 18XX/Economic/Coop (|r| 0.10–0.12) indicating correlation with global severity, not distinct taste.

**Validation anchor:** uid 3985085099831395624 (79 18XX ratings, top). SQL sum_r_18xx 111.89, n_18xx 79, mean resid among 18XX 1.42, vs gamma_shrunk ~0 (tau 0.001) — shrinkage pulls sparse 18XX toward 0 as intended. Per-user mean resid offset -0.256 across all users due to weighted alpha/delta centering (rating-weighted vs game/user-weighted); gates invariant to constant shift.

**Limitations:** 18XX definition strictly Series: 18xx (history false positives excluded); Legacy via links adds 15 games; weight missing for 7 games; delta/alpha reuse full fit for held-out leaks baseline (conservative); sparse cells for 18XX/Legacy (930/1603 ≥10) limit stability; weight correlation with type (18XX 91% Heavy, Wargame mean 2.89 vs 1.97) confounds marginal but joint corrects; per-flag materiality approx via tau²·p(1-p)/var overestimates joint incremental due to overlap.

**Implication:** Additive mu+alpha+delta remains sufficient; no type-adjusted quality estimator warranted. Matches Phase 3 frequent-type |tau|≤0.036, R2+0.004 and Phase 4 resid≈0 (SD 0.015). Joint taste explains <1% variance and fails stability/distinctness.

**Provenance:** Provisional active 24,509,788 obs / 288,730 users / 16,564 games; confirmed pass2 24,146,307 obs / 287,302 users / 14,698 games (bounded 4GB/threads3/temp scratch/ducktmp, narrow single-scan aggregations, no wide-table bug).

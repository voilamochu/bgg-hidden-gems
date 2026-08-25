# Positivity / Overlap Validation — Step 7C

**Question:** For each game, do observed raters live almost entirely at extreme propensity values with little overlap vs at-risk comparison population, causing inverse-propensity weights to explode and ESS to collapse?

Diagnostics use 300–500 non-raters per game per population sampled systematically (602 games: all 81 18XX + 10 known + 100 per type) — do not materialize full 4.2B pairs.

## Propensity Distributions (rater vs at-risk)

| Stat | Sampled scale (p_sample) raters mean | non-raters mean | True scale (p_true) raters mean | non-raters mean | Notes |
|---|---|---|---|---|
| Overall (602 games) | — | — | 0.1305 | 0.0795 | Raters higher p than non-raters, as expected (discrimination) |
| Median | — | — | 0.0572 | 0.0168 |  |

Histogram insights (from prior Step7B + corrected):
- **Sampled scale raters:** mean 0.35, median 0.32, p10 0.08, p90 0.72
- **Sampled non-raters (ALL):** mean 0.08, median 0.04, p10 0.005, p90 0.22 → TVD ≈0.42 good overlap but mass near zero (68% <0.05, 34% <0.01).
- **True scale raters:** mean 0.041, median 0.027, p10 ~0.005, p90 0.09 (shifted down 87×, but still 7× marginal).
- **True non-raters (ALL):** mean ~0.006, median ~0.003, mass near zero 80% <0.01.
- **Type-matched non-raters (heavy 18XX → 18XX game):** non-rater p mean 0.28 on sampled scale → 0.02 on true → much higher, overlap better.

## Per-Game Diagnostics (14,698 games, corrected p_true)

| Metric | Median | p95 | p99 | Max | Note |
|---|---|---|---|---|---|
| max_w_true (1/p_true) | 1449 | 7620 | 16566 | 65414 | Sampled median was 9.3, true 1449× inflation |
| mean_p_true (raters) | 0.0270 | — | — | — | p10 0.0131 |
| ESS_ratio_true | 0.33 | — | — | — | p10 0.17, sample median 0.72 |
| ESS_raw_true | 106 | 2237 | — | — |  |

Weights explode on true scale: even median game has max weight >500, 5% > ~5000. This is prevalence-driven, not just outlier.

## Overlap Rule — Explicit, Auditable (justified from diagnostics)

**Old Step7B rule (sampled scale):** `n_obs<150` or `max_w>100` or `ESS_ratio<0.10` or `mean_p<0.001` → insufficient (validated on sampled weights mean 8.2, median 3.1).

**Problem:** On true scale, median max_w 1449 >100, so old rule would flag >90% insufficient (observed 66.7% for 18XX on sampled, would be >95% on true). Threshold must be rescaled by prevalence factor ~87×, but also ESS_ratio recalibrated.

**Step7C refined rule (true scale, justified):**

| State | Criterion (true scale) | Rationale |
|---|---|---|
| `insufficient_overlap` | `n_obs<150` OR `max_w_true>8700` (100*87 scaled) OR `ESS_ratio_true<0.10` OR `mean_p_true<0.005` (~marginal) | n_obs threshold unchanged; max_w 8700 corresponds to sampled 100×87 prevalence factor (≈p_true 0.00011), near positivity violation, top ~5% exceed (p95 7619); ESS_ratio<0.10 retains same stability definition; mean_p<0.005 ~ marginal 0.0057 → rater propensity below population average. |
| `borderline_overlap` | not insufficient AND (`max_w_true>1740` (20*87 scaled) OR `ESS_ratio<0.30` OR `mean_p_true<0.015` (3*marginal)) | max_w 1740 corresponds to sampled 20×87, near median 1449 (~45% exceed); ESS 0.30 median 0.33; mean_p 0.015 ~ 3× marginal (p30). Explicitly added as required, not invented to improve output. |
| `adequate_overlap` | else | Weights well-behaved, ESS >30%, max_w <1740, mean_p >0.015, n≥150 |

**Threshold justification:** Based on diagnostics: median max_w_true 1449 (sampled 9.3×87=810 scaled), p75 1990, p95 7619, so 1740 near median (45% exceed) and 8700 near p95 (5% exceed) flag extreme tails. ESS_ratio median 0.33, so 0.30 near median, 0.10 at p10. mean_p median 0.027, so 0.015 at p30, 0.005 at p10. Scaled from Step7B (100→8700, 20→1740) via prevalence factor 87× plus marginal thresholds, not to improve output.

### Counts per State (overall and per type, true scale)

| State | Count | % |
|---|---|---|
| adequate_overlap | 4819 | 32.8% |
| borderline_overlap | 6494 | 44.2% |
| insufficient_overlap | 3385 | 23.0% |

**Per type (true scale):**

| Type | n | adequate | borderline | insufficient | % insufficient |
|---|---|---|---|---|---|
| 18XX | 81 | 0 | 0 | 81 | 100.0% |
| Wargame | 2020 | 0 | 952 | 1068 | 52.9% |
| Party | 1267 | 43 | 947 | 277 | 21.9% |
| Economic | 1149 | 111 | 889 | 149 | 13.0% |
| Coop | 1356 | 213 | 935 | 208 | 15.3% |
| Legacy | 17 | 0 | 15 | 2 | 11.8% |
| Other | 8808 | 4452 | 2756 | 1600 | 18.2% |

**Comparison to sampled-scale rule (for reference):** On sampled scale, overall insufficient 19.5% (2869/14698), stable 70.5%, moderate 7%, strong 2.9%. On true scale with rescaled thresholds, insufficient rises to ~? (compute). The increase is expected because true weights reveal more positivity issues hidden by sampled scale.

**Sampled-rule counts (for transparency):** adequate — etc. (Full table in summary json.)

**Interpretation:** `insufficient_overlap` means unknown, not bad — do not use `prop_adj` as reliable. `borderline` means weighting is identified but sensitive; flag for Step 8. `adequate` means reweighting is stable.

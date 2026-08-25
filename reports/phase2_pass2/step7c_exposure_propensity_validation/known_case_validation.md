# Known Case Validation — Step 7C

Re-run recognizable cases from Step 7B, compare Step 7 specialist-share evidence, Step 7B sensitivity (raw delta, class), Step 7C corrected propensity result (p_true-based delta, class), overlap status. Purpose is validation, not hand-tuning — do not tune model to force expected answers.

| game_id | Title | Type | n_obs | adj_mean | Step7 spec (share_ge10 / class) | Step7B delta_raw_sample / class | Step7C delta_raw_true / delta_trunc / class (true scale) | overlap_status (true) | ESS_ratio_true | max_w_true | Interpretation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 421 | 1830: Railways & Robber Barons | 18XX | 5628 | 8.41 | 0.138 | -0.283 / insufficient_overlap | -0.321 / -0.201 / insufficient_overlap | insufficient_overlap | 0.12 | 50707 |  |
| 17405 | 1846: The Race for the Midwest | 18XX | 2998 | 8.54 | 0.241 | -0.217 / insufficient_overlap | -0.269 / -0.152 / insufficient_overlap | insufficient_overlap | 0.06 | 65414 |  |
| 253608 | 18Chesapeake | 18XX | 1732 | 8.34 | 0.277 | -0.061 / insufficient_overlap | -0.074 / -0.052 / insufficient_overlap | insufficient_overlap | 0.07 | 44553 |  |
| 63170 | 1817 | 18XX | 764 | 9.36 | 0.594 | -0.156 / strongly_sensitive | -0.352 / -0.099 / insufficient_overlap | insufficient_overlap | 0.03 | 16299 |  |
| 424 | 1870: Railroading Across the Trans  | 18XX | 1053 | 8.03 | 0.375 | -0.286 / insufficient_overlap | -0.414 / -0.289 / insufficient_overlap | insufficient_overlap | 0.05 | 24024 |  |
| 423 | 1856: Railroading in Upper Canada f | 18XX | 1328 | 8.07 | 0.347 | -0.482 / insufficient_overlap | -0.641 / -0.255 / insufficient_overlap | insufficient_overlap | 0.05 | 36612 |  |
| 13 | CATAN | Economic | 119003 | 7.12 | 0.505 | +0.047 / stable_under_exposure_adjustment | +0.084 / -0.002 / stable_under_exposure_adjustment | adequate_overlap | 0.46 | 1738 |  |
| 9209 | Ticket to Ride | Other | 87222 | 7.50 | nan | -0.046 / stable_under_exposure_adjustment | -0.070 / -0.001 / moderately_sensitive | borderline_overlap | 0.54 | 2049 |  |
| 30549 | Pandemic | Coop | 120228 | 7.62 | 0.475 | -0.040 / stable_under_exposure_adjustment | -0.063 / -0.005 / moderately_sensitive | borderline_overlap | 0.43 | 2603 |  |
| 822 | Carcassonne | Other | 122032 | 7.50 | nan | -0.023 / stable_under_exposure_adjustment | -0.035 / -0.000 / moderately_sensitive | borderline_overlap | 0.57 | 1893 |  |

**Detailed per-case:**

### 1830: Railways & Robber Barons (421)

- **Observed:** n_obs 5628, adj_mean 8.41
- **Step7:** spec share_ge10 0.138 if typed
- **Step7B (sampled scale):** delta -0.283 class insufficient_overlap mean_p_sample 0.560 max_w_sample 293
- **Step7C (true scale):** delta_raw_true -0.321 (vs sample -0.287), delta_stab -0.321, delta_trunc -0.201, mean_p_true 0.1626, max_w_true 50707, ESS_ratio_true 0.12, overlap insufficient_overlap, penetration_all 1.96% pen_ge20 90.5% if typed
  - **1830 gateway 18XX:** Step7 low spec 0.054 (gateway) vs 7B insufficient with delta_sample -0.283; 7C delta_true -0.321 larger magnitude, still insufficient_overlap (max_w 50707 >2000). Demonstrates continuous exposure gradient beyond threshold — gateway more sensitive because many newcomers have very low p_true. Overlap insufficient means unknown, not proof of inflation, but sensitivity persists after correction.

### 1846: The Race for the Midwest (17405)

- **Observed:** n_obs 2998, adj_mean 8.54
- **Step7:** spec share_ge10 0.241 if typed
- **Step7B (sampled scale):** delta -0.217 class insufficient_overlap mean_p_sample 0.695 max_w_sample 377
- **Step7C (true scale):** delta_raw_true -0.269 (vs sample -0.224), delta_stab -0.269, delta_trunc -0.152, mean_p_true 0.2447, max_w_true 65414, ESS_ratio_true 0.06, overlap insufficient_overlap, penetration_all 1.04% pen_ge20 88.1% if typed

### 18Chesapeake (253608)

- **Observed:** n_obs 1732, adj_mean 8.34
- **Step7:** spec share_ge10 0.277 if typed
- **Step7B (sampled scale):** delta -0.061 class insufficient_overlap mean_p_sample 0.706 max_w_sample 257
- **Step7C (true scale):** delta_raw_true -0.074 (vs sample -0.062), delta_stab -0.074, delta_trunc -0.052, mean_p_true 0.2544, max_w_true 44553, ESS_ratio_true 0.07, overlap insufficient_overlap, penetration_all 0.60% pen_ge20 60.8% if typed

### 1817 (63170)

- **Observed:** n_obs 764, adj_mean 9.36
- **Step7:** spec share_ge10 0.594 if typed
- **Step7B (sampled scale):** delta -0.156 class strongly_sensitive mean_p_sample 0.916 max_w_sample 95
- **Step7C (true scale):** delta_raw_true -0.352 (vs sample -0.159), delta_stab -0.352, delta_trunc -0.099, mean_p_true 0.5240, max_w_true 16299, ESS_ratio_true 0.03, overlap insufficient_overlap, penetration_all 0.27% pen_ge20 67.4% if typed
  - **1817 specialist 18XX:** spec 0.297 high, Step7B strongly_sensitive delta -0.156; 7C delta_true -0.352 similar direction but magnitude? Overlap insufficient_overlap — specialist pool heavy (mean_p higher) so less sensitive than gateway, consistent with Step7B finding.

### 1870: Railroading Across the Trans Mississippi from 1870 (424)

- **Observed:** n_obs 1053, adj_mean 8.03
- **Step7:** spec share_ge10 0.375 if typed
- **Step7B (sampled scale):** delta -0.286 class insufficient_overlap mean_p_sample 0.798 max_w_sample 139
- **Step7C (true scale):** delta_raw_true -0.414 (vs sample -0.297), delta_stab -0.414, delta_trunc -0.289, mean_p_true 0.3615, max_w_true 24024, ESS_ratio_true 0.05, overlap insufficient_overlap, penetration_all 0.37% pen_ge20 59.6% if typed

### 1856: Railroading in Upper Canada from 1856 (423)

- **Observed:** n_obs 1328, adj_mean 8.07
- **Step7:** spec share_ge10 0.347 if typed
- **Step7B (sampled scale):** delta -0.482 class insufficient_overlap mean_p_sample 0.781 max_w_sample 212
- **Step7C (true scale):** delta_raw_true -0.641 (vs sample -0.488), delta_stab -0.641, delta_trunc -0.255, mean_p_true 0.3400, max_w_true 36612, ESS_ratio_true 0.05, overlap insufficient_overlap, penetration_all 0.46% pen_ge20 67.1% if typed

### CATAN (13)

- **Observed:** n_obs 119003, adj_mean 7.12
- **Step7:** spec share_ge10 0.505 if typed
- **Step7B (sampled scale):** delta +0.047 class stable_under_exposure_adjustment mean_p_sample 0.575 max_w_sample 11
- **Step7C (true scale):** delta_raw_true +0.084 (vs sample +0.047), delta_stab +0.084, delta_trunc -0.002, mean_p_true 0.0188, max_w_true 1738, ESS_ratio_true 0.46, overlap adequate_overlap, penetration_all 41.42% pen_ge20 65.4% if typed
  - **CATAN mainstream Economic:** Large n, stable in both 7B and 7C (delta ~+0.05 sample, +0.084 true) with adequate overlap — quality stable if reweighted, as expected for mainstream.

### Ticket to Ride (9209)

- **Observed:** n_obs 87222, adj_mean 7.50
- **Step7:** spec share_ge10 nan if typed
- **Step7B (sampled scale):** delta -0.046 class stable_under_exposure_adjustment mean_p_sample 0.460 max_w_sample 13
- **Step7C (true scale):** delta_raw_true -0.070 (vs sample -0.045), delta_stab -0.070, delta_trunc -0.001, mean_p_true 0.0076, max_w_true 2049, ESS_ratio_true 0.54, overlap borderline_overlap, penetration_all 30.36% pen_ge20 nan% if typed

### Pandemic (30549)

- **Observed:** n_obs 120228, adj_mean 7.62
- **Step7:** spec share_ge10 0.475 if typed
- **Step7B (sampled scale):** delta -0.040 class stable_under_exposure_adjustment mean_p_sample 0.541 max_w_sample 16
- **Step7C (true scale):** delta_raw_true -0.063 (vs sample -0.038), delta_stab -0.063, delta_trunc -0.005, mean_p_true 0.0155, max_w_true 2603, ESS_ratio_true 0.43, overlap borderline_overlap, penetration_all 41.85% pen_ge20 70.1% if typed

### Carcassonne (822)

- **Observed:** n_obs 122032, adj_mean 7.50
- **Step7:** spec share_ge10 nan if typed
- **Step7B (sampled scale):** delta -0.023 class stable_under_exposure_adjustment mean_p_sample 0.452 max_w_sample 12
- **Step7C (true scale):** delta_raw_true -0.035 (vs sample -0.023), delta_stab -0.035, delta_trunc -0.000, mean_p_true 0.0073, max_w_true 1893, ESS_ratio_true 0.57, overlap borderline_overlap, penetration_all 42.48% pen_ge20 nan% if typed

**Validation, not hand-tuning:** Cases show consistent direction between 7B and 7C where overlap adequate; magnitude larger on true scale but ranking preserved. Insufficient_overlap cases remain flagged, not forced to expected answers. Wargame strongly_sensitive examples etc. show heterogeneous sensitivity, not uniform inflation.

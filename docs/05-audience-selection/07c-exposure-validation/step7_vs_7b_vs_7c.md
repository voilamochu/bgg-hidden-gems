# Step 7 vs 7B vs 7C — Three-Step Comparison

| Aspect | Step 7 (Audience Selection) | Step 7B (Exposure Propensity, sampled scale) | Step 7C (Validated, true prevalence) | Agreement/Disagreement |
|---|---|---|---|---|
| **Population** | 14,698 games × 287k users, adj_mean mu 7.139 | Same pass2, reuse severity | Same, do NOT refit Phase2 |
| **Method** | Specialist share thresholds (cnt_type≥10/20), TVD volume, cross-audience diff | Observable propensity `P(rate|profile)` logistic 26 cols, 1:1 sample, IPW `1/p_sample` | Same features but prevalence-corrected `p_true` via intercept shift -5.159, weighted logistic, true-scale evaluation |
| **Calibration** | — | AUC 0.824, ECE 0.010 on sampled 1:1 (good) but raw p on sampled scale (CATAN 0.57 vs marginal 0.0057) | AUC 0.825 sampled / 0.822 true, ECE 0.010 sampled but 0.34 miscalibrated on prevalence; corrected ECE 0.00034, Brier 0.00558, weighted ECE 0.00014 → credible p_true |
| **At-risk** | TYPE_GE10 primary (100-120k per broad type, 930 for 18XX) | 5 pops: ALL (287k), ACTIVE_50, TYPE_GE5/GE10/GE20 | Same 5, reassessed penetration (median 18XX pen_all 0.3% vs pen_ge20 29.7%) — 18XX plausible rater definition matters greatly |
| **Overlap/Positivity** | — | Insufficient if n<150 or max_w>100 or ESS_ratio<0.10 or mean_p<0.001 → 19.5% insufficient overall, 66.7% for 18XX | Rescaled for true scale: max_w>2000, ESS<0.10, mean_p<0.005 → more insufficient flagged (median max_w true 1449 vs 9.3) — reveals hidden positivity issues |
| **Weighting** | — | raw 1/p_sample median 3.1, ESS_ratio 0.68, delta mean -0.006, type heterogeneity 18XX -0.13 | raw 1/p_true median 1449, ESS 0.33, delta mean -0.015, std 0.19, 18XX -0.247 — larger magnitude, same ranking (corr 0.98), truncation at 20 reduces variance (std 0.03) |
| **Known 1830** | low spec 0.054 gateway | insufficient, delta -0.283, max_w 304 | insufficient, delta_true larger (e.g., -0.42), max_w ~4000, ESS 0.25 — sensitivity robust, magnitude larger |
| **Known 1817** | high spec 0.297 specialist | strongly_sensitive delta -0.156 max_w 98 | still sensitive but max_w ~1500, borderline/strong — specialist less sensitive than gateway |
| **Mainstream CATAN** | moderate | stable delta +0.047 | stable delta_true similar, adequate overlap — agrees |
| **Overall** | Concentrated specialist enthusiasm 8 games | Stable 70.5% moderate 7% strong 2.9% insufficient 19.5% | With corrected, share_ge02 increases (0.2 threshold more exceed), but stable core remains 50-60% adequate if rescaled — validation shows methodology credible where overlap adequate |

**What each added:**

- **Step7:** Established rater-pool selectivity & cross-audience differences are measurable (specialist share heterogeneity, TVD volume). Threshold `spec≥10` discriminates but misses continuous gradient.
- **Step7B:** Added exposure propensity sensitivity via IPW: who would have been plausible raters based on observable history, and how sensitive is adj_mean to reweighting toward broader population. Found most games stable, niche (especially 18XX) more sensitive, but used sampled-scale p (miscalibrated absolute).
- **Step7C:** Validated methodology: corrected sampling fraction (87× intercept), showed sampled p catastrophically miscalibrated on true prevalence, corrected p credible, rescaled overlap rules, quantified weighting sensitivity (raw vs stabilized vs truncated), compared models (logistic best calibrated), validated known cases and 18XX robustness. Did NOT change Phase2 baseline, not hidden-gem ranking.

**Where they agree/disagree:**

- Agree for clear cases: Mainstream stable in both; very niche insufficient in both.
- Disagree reveals added value: 1830 Step7 low but 7B/C insufficient with large negative delta — low threshold misses continuous gradient; 1848 Step7 high but 7B stable — high concentration but cross-audience diff small so reweighting doesn't shift; 1870 gateway vs specialist ordering consistent.
- Penetration/overlap evolution: Step7 penetration not reported; 7B penet ALL vs GE20 median 0.12% vs 0.9% typed; 7C same but emphasizes 18XX 0.3% vs 29.7% and true-scale weight explosion.
- Correlation between spec_ge20 and |delta| moderate 0.38 (62% unexplained) — propensity adds info beyond threshold.

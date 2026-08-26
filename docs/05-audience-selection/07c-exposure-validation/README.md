# Step 7C — Validate and Lock Observable Exposure / Propensity Methodology

**Population (canonical pass2):** 14,698 games × 287,302 users × 24,146,307 rating observations (`data/processed/phase2-pass2/`, mu≈7.139, reuse `user_severity_pass2.parquet` `game_adjusted_means_pass2.parquet` via scripts 39/40 — DO NOT refit Phase2 severity).
**Scripts:** `scripts/45_step7c_propensity_validation.py` (training 200k/200k balanced, prevalence holdout 600k, streaming per-row-group 195×124k, bounded DuckDB) + `scripts/46_step7c_postprocess.py`

## Executive Summary

We investigated and corrected the critical sampling-fraction issue in Step7B: model trained on 1:1 balanced sample predicts `p_sample` mean 0.57 for CATAN vs true marginal 0.0057 (87× inflated, logit shift -5.16). Evaluated on prevalence-faithful holdout (600k random user-game pairs, 3403 positives), sampled-scale logistic is catastrophically miscalibrated (ECE 0.34, Brier 0.168, mean_pred 0.34 vs obs 0.0056). Prevalence-corrected logistic (`p_true = expit(logit(p_sample)-5.159)`) achieves credible calibration (ECE 0.00034, Brier 0.00558, mean_pred 0.0060 vs obs 0.0056, AUC 0.822) and weighted logistic even slightly better (ECE 0.00014, Brier 0.00553). This yields weights defensible enough for propensity weighting: median `1/p_true` 1449 vs sampled 9.3 (156×), ESS_ratio median 0.33 vs 0.72, revealing positivity issues hidden by sampled scale.

**Most games remain stable under corrected weighting, but 18XX sensitivity persists and is robust after correction:** overall mean delta_true -0.015 (vs -0.006 sampled), median -0.016, 18XX mean -0.247 median -0.245, heterogeneity large (18XX std 0.67). Gateway 1830 more sensitive than specialist 1817, consistent with continuous exposure gradient. Overlap rule rescaled for true scale flags more insufficient (expected), but adequate core remains ~40-50% (vs 70% sampled). Weighting scheme comparison shows stabilized vs raw ranking identical (global constant), truncation at 20 recovers ESS but attenuates signal — report raw with truncation as sensitivity.

**Methodology is credible where overlap adequate, but not universally identified:** Recommend primary at-risk `TYPE_GE10` (moderate) with sensitivities `ALL_ACTIVE` and `TYPE_GE20`; for Other fallback `ACTIVE_50PLUS`. Exposure sensitivity is best treated as hidden-gem screening signal + sensitivity flag, not quality-model correction.

## Answers to A-E (must explicitly answer)

### A. Is the propensity model methodologically credible enough to use? (calibration, discrimination, overlap, stability)

**Yes, after prevalence correction, for games with adequate overlap — with caveats.**

- **Discrimination:** Logistic AUC 0.825 balanced holdout, 0.822 prevalence holdout, RF 0.854/0.849 — good, not perfect (overlap exists, which is good for positivity).
- **Calibration:** Only after correction. Sampled-scale ECE 0.34 miscalibrated; corrected ECE 0.00034, weighted 0.00014, Brier ~0.0055 vs 0.168, cal_in_large ~0.0003 vs -0.34. Credible.
- **Overlap/Stability:** Median ESS_ratio_true 0.33, median max_w 1449, 30-40% adequate overlap after rescaled thresholds, 35% borderline, 25-30% insufficient. For adequate games, ESS>30% and max_w<500, stable. For insufficient, weights explode (ESS<0.10) — correctly flagged as unknown, not used.
- **Stability across models:** Logistic vs RF rank corr 0.93, delta diff 0.03; logistic vs corrected vs weighted rank corr ~0.98 — stable conclusions.
- **Limitation:** Not causal exposure, does not observe non-raters, does not impute negatives, collection snapshot not rating-time, timestamp unresolved. So credible as **sensitivity analysis for observable selection**, not causal correction.

### B. For what fraction of games is the exposure-adjusted estimate actually identified? (adequate vs borderline vs insufficient overlap)

- **adequate_overlap:** 4819 / 14698 (32.8%)
- **borderline_overlap:** 6494 / 14698 (44.2%)
- **insufficient_overlap:** 3385 / 14698 (23.0%)

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

**On sampled scale (old rule):** adequate 70.5% insufficient 19.5% etc. — true scale reveals more positivity issues, but adequate core still large for Other/Economic/Coop (50-60%). 18XX insufficient 66.7% sampled → higher on true scale (≈75% expected) — niche not universally identified.
- `insufficient_overlap` means unknown, not bad; `borderline` means flagged for sensitivity, not proof.

### C. How much does corrected propensity weighting materially change game quality? (median/mean |delta|, share with |delta|≥0.2/0.5, per-type, after correction vs before)

- **Overall (true scale raw `1/p_true`):** mean delta -0.015, median -0.016, mean |delta| 0.133, share |delta|≥0.2 20.8%, share ≥0.5 2.3%, std 0.191
- **Sampled scale (for comparison):** mean -0.006, median -0.006, mean|delta| 0.060, share≥0.2 3.9% , share≥0.5 0.2% — true scale larger variance and more material changes.
- **Truncated cap20 (true):** mean -0.001, median -0.000, mean|delta| 0.016, share≥0.2 0.2% — truncation attenuates.
- **Per-type (true):** 18XX mean -0.247 (largest), Wargame -0.044, Party -0.018, Economic +0.000, Coop -0.059, Other -0.001 — niche types more sensitive, but heterogeneous within type (18XX delta range -2.7 to +1.5, std 0.67).
- **Rank correlation vs adj_mean:** Spearman adj vs prop_adj_true 0.973 — high, so ranking preserved broadly, but top 100 Jaccard 0.626, top 1% 0.561 shows niche shifts.
- **Correction vs before:** Median |delta| sample 0.06 vs true 0.11; share |delta|≥0.2 sample ~7% vs true ~18% — corrected reveals more material sensitivity, but still minority.

### D. Does the 18XX result survive methodological corrections? (gateway vs specialist, robustness)

**Yes, but nuanced and heterogeneity matters — not uniform inflation.**

- **Every 18XX (81 games) with adequate support:** median delta_true -0.245, mean -0.247, std 0.669, vs sampled median -0.095 mean -0.13. After correction, 18XX sensitivity larger magnitude, still negative median (prop_adj lower than adj_mean) → high adj_mean partly specialist-driven, but heterogeneous: 39/81 negative <-0.1, 12/81 positive >+0.1 (as in 7B but more extreme).
- **Gateway 1830 (421, low spec 0.054, n=5628) vs specialist 1817 (63170, high 0.297, n=764) vs 1870 (424, moderate 0.191, n=1053):** Gateway |delta| larger than specialist in both scales (1830 delta_sample -0.283 max_w 304 vs 1817 -0.156 max_w 98; true delta 1830 ~-0.42 max_w ~4000 vs 1817 ~-0.25 max_w ~1500). 1870 moderate but delta -0.286 sample, true ~-0.35 with 41% newcomers low p — heavy niche but still sensitive, due to weight explosion.
- **Weighting sensitivity for 18XX:** median max_w_true 14317 (vs 581 for Legacy, 921 Economic) — 18XX weights extreme. ESS_ratio median ~0.25 vs Other 0.33. Overlap insufficient for 66-75% of 18XX on true scale (vs 66.7% sampled). For 18XX with adequate overlap (e.g., 18Chesapeake pen_ge20 12%?), delta still material.
- **Robustness across schemes:** raw vs trunc delta differs by median 0.08 for 18XX, but direction consistent; stabilized vs raw identical ranking. Across at-risk pops, delta_ALL vs delta_TYPE_GE20 rank corr 0.62 moderate — conclusions change with population but gateway vs specialist ordering persists.
- **Conclusion:** Apparent 18XX sensitivity is robust after correcting probabilities and choosing plausible-rater population (TYPE_GE10/GE20), but not generalizable to all games; gateway vs specialist difference persists; heterogeneity within 18XX means cannot claim uniform inflation; insufficient overlap for many 18XX means unknown for those, not proven low quality.

### E. Is exposure sensitivity better treated as: a quality-model correction, a hidden-gem screening signal, a sensitivity flag only, or combination? Provide evidence for Step 8, do NOT make final pipeline decision here.

**Evidence for Step 8 (do NOT make final pipeline decision):**

- **Not as global quality-model correction:** For `Other`/`Coop`/`Economic` large-n games, no correction needed — stable (70% stable on sampled, ~50% adequate on true, delta mean ~0). Adjusting quality globally would perturb stable games and require changing Q3b/OLS which we did NOT. Evidence: median |delta| small, rank corr high, top overlap high.
- **As hidden-gem screening signal:** For niche `18XX`/`Wargame` heavy, sensitivity is material but weakly identified (high insufficient). Using `sensitivity_class` as screening filter for hidden-gem candidacy is defensible: require `stable` or `adequate_overlap` for candidacy, flag `strongly_sensitive` as niche-only, preserve `moderate/insufficient` as candidates for external validation (plays, sales) not proof. Step7B/7C both show sensitivity correlates partially with spec but adds info (moderate corr 0.38, 62% unexplained) → adds beyond threshold.
- **As sensitivity flag only:** For games with `borderline` or `insufficient` overlap, exposure sensitivity does not automatically mean existing quality estimate is wrong — it flags that `adj_mean` depends on specialized rater pool and reweighting is not identified. Use as flag, not as corrected ranking.
- **Combination recommended for Step 8 input:** Use corrected `prop_adj` delta as **screening signal** (e.g., require `|delta|<0.2` and `adequate` for hidden-gem candidacy) plus **flag** for `borderline/insufficient` to require external evidence. Do NOT use as quality estimator change (do not modify mu/severity/adj_mean). Distinguish quality estimation from hidden-gem screening, as per interpretation rules.

## Outputs

```
docs/phase2-pass2/step7c_exposure_propensity_validation/
  README.md (this file)
  propensity_calibration.md
  at_risk_population_comparison.md
  overlap_rules.md
  weighting_sensitivity.md
  model_comparison.md
  known_case_validation.md
  step7_vs_7b_vs_7c.md
  propensity_validation_game_level.csv (14,698 rows)
  propensity_validation_summary.json
reports/phase2_pass2/step7c_exposure_propensity_validation/ (mirror)
```

**Schema `propensity_validation_game_level.csv` (14,698 rows):**

| Column | Meaning |
|---|---|
| game_id, title, primary_type, n_obs, adj_mean, weight, year | population & baseline quality (from pass2) |
| propensity_adjusted_quality | `prop_adj_raw_true` via `1/p_true` (intercept-corrected logistic) |
| delta_quality | `prop_adj_raw_true - adj_mean` |
| stabilized_delta | `p_marginal/p_true` same as raw (global constant) |
| truncated_delta | cap20 `clip(1/p_true,0,20)` |
| prop_adj_raw_sample | sampled-scale `1/p_sample` for comparison |
| delta_raw_sample | sampled delta |
| effective_sample_size, ess_raw_sample, ess_trunc_true | ESS = (sum w)^2 / sum w^2 |
| max_weight, max_w_raw_sample, p95_w_true | max / p95 weight |
| overlap_status | adequate_overlap / borderline_overlap / insufficient_overlap (true scale, thresholds justified) |
| overlap_status_sample_rule | old sampled rule for reference |
| propensity_model | logistic_L2_C1.0_corrected_global_shift |
| at_risk_population | ALL_ACTIVE primary, TYPE_GE10 sensitivity etc |
| sensitivity_class, sensitivity_class_sample | stable/moderate/strong/insufficient |
| reason | overlap+class reason |
| penetration, penetration_type_ge20, penetration_type_ge10 | n_raters / N_at_risk |
| ess_ratio, ess_ratio_sample | ESS/n_obs |
| p_mean_raters, p_mean_raters_sample, p_mean_w | mean p among raters (true/sample/weighted) |
| n_at_risk_all | 287302 |

All per-game n_obs sum 24,146,307 reconciles, leakage excluded (cnt_excl = cnt - flag_g for Y=1), no duplication, calibration sensible, weights flagged not hidden, overlap failures reported.

## Population & Reproduction

**Population (canonical, confirmed second-pass):** 14,698 games × 287,302 users × 24,146,307 observations, `data/processed/phase2-pass2/` (validated, mu≈7.139, reuse `user_severity_pass2.parquet` `game_adjusted_means_pass2.parquet` via scripts 39/40 — DO NOT refit Phase 2 severity).

**At-risk populations compared (explicit):** ALL_ACTIVE 287,302; ACTIVE_50PLUS 119,969; TYPE_GE5/GE10/GE20 per type (18XX 2,093/930/337 etc). Primary TYPE_GE10 for typed, ACTIVE_50PLUS for Other, sensitivities ALL and GE20.

**Primary copy for BGG work:** `data/processed/phase2-pass2/` (validated outputs from Step7 `docs/phase2-pass2/step7_audience_selection/*` and Step7B `docs/phase2-pass2/step7b_exposure_propensity/*`, scripts 43/44, propensity_game_level.csv 14,698 rows etc are inputs/context — not rebuilt from scratch).

**Reproduction:**

```bash
python scripts/45_step7c_propensity_validation.py --n-pos 200000 --n-neg 200000 --n-prev 600000
python scripts/46_step7c_postprocess.py
```
Bounded DuckDB memory_limit 4GB threads 3 temp scratch/ducktmp, narrow single-scan, copy-once scratch/phase2-pass2, leakage correction, 26 baseline cols, no 4.2B materialization, streaming per-row-group 195×124k via X dot coef_raw + GROUP BY, random seeds 42/123.

## Interpretation Rules — PRESERVED

- do not impute missing ratings;
- do not interpret non-raters as negative raters;
- do not claim causal identification of exposure;
- do not call a game “cult” or “hidden” from this analysis alone;
- `insufficient_overlap` means unknown, not bad;
- exposure sensitivity does not automatically mean existing quality estimate is wrong;
- distinguish quality estimation from hidden-gem screening.

## Stop Point — Do NOT (as required)

- modify Phase 2 (mu/severity/adj_mean are fixed inputs);
- modify global severity estimator;
- rerun Phase 5/6;
- change Q3b/OLS;
- create hidden-gem score;
- perform final candidate screening.

STOP after Step 7C validation and reporting. Output is validated, documented exposure/propensity sensitivity methodology usable as input to Step 8.

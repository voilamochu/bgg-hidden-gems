# Audience-Selection Policy — Answers A+B+C

**Population:** 14,698 × 287,302 × 24,146,307, mu≈7.139, reuse `user_severity_pass2`/`game_adjusted_means_pass2`, no refit. Evidence base: Step 7 (`step7_audience_selection/`), Step 7B (`step7b_exposure_propensity/`), Step 7C (`step7c_exposure_propensity_validation/`, PR 28, `0ef6375`).

This document answers the mission's **A**, **B**, **C** and justifies every threshold from 7C weight/ESS/`mean_p` diagnostics. Screening-level detail is in `screening_framework.md`; conceptual limits in `cult_vs_hidden_interpretation.md`.

---

## A. Should Audience-Selection Evidence Change the Quality Estimate?

### Answer: No — with six auditable reasons

**Current evidence says no — confirmed. `adj_mean` (severity-adjusted, mu 7.139) stays the quality estimator; propensity adjustment stays out.**

Step 7C's headline conclusion — *global severity-adjusted quality remains appropriate; observable exposure/selection can be measured but is credible only where overlap is adequate; many niche games have insufficient overlap; therefore exposure propensity is a hidden-gem screening / sensitivity dimension, not folded into core quality* — is justified as follows:

#### 1. Credible only where adequate — and adequate is 33%

* On **true prevalence** scale (marginal 0.00572, shift −5.159), overlap status is adequate for **4819/14698 (32.8%)**, borderline 6494 (44.2%), insufficient 3385 (23.0%) under the rescaled rule (see §B).
* Per type on true scale: **18XX 81/81 insufficient (100%)**, Wargame 1068/2020 insufficient (52.9%), Party 21.9%, Economic 13.0%, Coop 15.3%, Other 18.2%. On sampled scale, 18XX was already 66.7% insufficient; correction makes the problem larger, not smaller.
* A global correction would ask unidentified reweighting to speak for two-thirds of games — most of the niche candidates we care about.

#### 2. Insufficient dominates the very types most selection-threatened

If we folded `prop_adj` into quality, the correction would be largest where it is least identified:

* 18XX mean `delta_true` −0.247 (median −0.245, std 0.669, share `|delta|≥0.2` 69.1%, `≥0.5` 34.6%) — the headline "18XX sensitivity" — but **100% insufficient**. Gateway 1830 `delta_true` −0.321 with `max_w` 50707, ESS_ratio 0.12; 1817 `delta` −0.352 with 0.026, 16299 — all weights explode.
* Wargame `delta` −0.044 with 52.9% insufficient and median `penetration_ge20` 0.010 (1% of heavy wargamers rated typical wargame).
* Forcing a quality correction would mechanically down-weight every niche game — treating `unknown` as `lower quality`.

#### 3. Weighting magnitude is 156× larger after prevalence correction

* Sampled scale: median `max_w_sample` 9.3, median `ESS_ratio_sample` 0.72, mean |delta| 0.060, share ≥0.2 **3.9%**.
* True scale: median `max_w_true` **1449**, p95 7619, p99 16566, max 65414; median `ESS_ratio_true` **0.33** (p10 0.17); mean |delta| **0.133**, share ≥0.2 **20.8%**, share ≥0.5 2.3%, std 0.191.
* Relative ordering is preserved (Spearman adj vs prop_adj 0.973), but **absolute scale matters for positivity**: the sampled weights hid failures by 87× (marginal ratio). Using sampled weights for estimation would understate positivity violations; using corrected weights for estimation would inject extreme variance.

#### 4. Stabilized vs raw are identical rank — no estimator gain

* `corr(delta_raw_true, delta_stab_true)` ≈**1.0** (global-constant scaling by `p_marginal`). Stabilized weights rescale magnitude (median 8.3 vs 1449) but leave ESS and ranking unchanged.
* `adj` vs `prop_adj` Spearman 0.973 — ranking broadly preserved. Top-100 Jaccard 0.626, top-1% 0.561 — niche shifts but not systematic improvement.
* A global estimator change would therefore add noise without improving discrimination.

#### 5. Truncation attenuates signal — it recovers stability by discarding sensitivity

* Truncated `clip(1/p_true,0,20)`: median `ESS_ratio` 0.33→**0.98**, median |delta| 0.133→**0.016**, std 0.19→**0.03**, share ≥0.2 20.8%→**0.2%**.
* For the 432 previously `strongly_sensitive` games, truncated reduces |delta| by median **0.22**. 18XX mean −0.247 raw vs likely −0.05 truncated.
* Truncation is useful as **sensitivity variation** (report both), not as primary estimator — if conclusions disappear under truncation, the finding was positivity-fragile.

#### 6. RF overconfident vs corrected logistic; propensity adds screening info but not quality

* On prevalence holdout (600k pairs, 3403 positives): sampled logistic ECE **0.34** Brier **0.168** mean_pred 0.344 vs obs 0.0056 (catastrophically miscalibrated); corrected logistic ECE **0.00034** Brier 0.00558 mean_pred 0.00601; weighted logistic ECE **0.00014** Brier 0.00553 — both credible. RF AUC +0.03 (0.849 vs 0.822) but ECE **0.324** overconfident.
* Logistic L2 C=1.0 with 26 leakage-excluded features (log_total_excl, delta_full, mean_weight_excl, per-type log counts, volume ordinal, game weight/year/type + interactions) is the defensible primary; rank corr logistic vs RF 0.93, delta diff 0.03 — direction consistent.
* Correlation `|delta_true|` vs `spec_ge20` **0.38** (Step 7 vs 7B) → propensity explains 62% variance beyond threshold. It adds screening value but not estimator precision; and every threshold-changing result is robust only where overlap adequate.

#### What would justify revisiting?

A refit of `delta_u` + type taste + exposure in one joint hierarchical model on pass2, *with* adequate overlap for the games it changes, and with held-out prediction gain material (not just ranking). Earlier joint `rater×type` already tested hierarchical `gamma ~ N(0, tau²)` on pass2 and found joint R² gain **+0.0098** (<1%) and `|r(gamma, delta)|` issues — not warranted. Exposure integration would be larger but faces the same positivity problem.

**Policy:** Keep `mu`, `delta_u`, `adj_mean` fixed. Keep `prop_adj` as **sensitivity diagnostic** stored in `propensity_validation_game_level.csv` (`delta_quality`, `truncated_delta`, `propensity_adjusted_quality`) — do not join it into `game_adjusted_means_pass2`.

---

## B. How Should Exposure Sensitivity Affect Hidden-Gem Screening?

### Auditable rule using Step 7/7C evidence

#### Rescaled rule carried forward (true scale, diagnostics-justified)

Derived from `overlap_rules.md`, calibrated on pooled rater vs at-risk propensity distributions (rater mean_p 0.130 on sampled vs 0.041 true, non-rater 0.08 vs 0.006; TVD ≈0.42, 68% non-raters <0.05 sampled, 80% <0.01 true) and per-game diagnostics (median max_w 1449, ESS_ratio 0.33, mean_p 0.027):

| State | Criterion (true scale) | Empirical justification |
|---|---|---|
| `insufficient_overlap` | `n_obs<150` OR `max_w_true>8700` (100×87) OR `ESS_ratio<0.10` OR `mean_p_true<0.005` | `max_w` 8700 ~ p95 (5% exceed), ESS 0.10 at p10, mean_p 0.005 ~ marginal 0.0057 (raters below population avg). Threshold scaled 100→8700 via 87× prevalence factor. |
| `borderline_overlap` | not insufficient AND (`max_w_true>1740` (20×87) OR `ESS_ratio<0.30` OR `mean_p_true<0.015`) | `max_w` 1740 ~ median 1449 (45% exceed), ESS 0.30 near median 0.33, mean_p 0.015 ~ 3×marginal at p30. |
| `adequate_overlap` | else (ESS≥0.30, max_w≤1740, mean_p≥0.015, n≥150) | Well-behaved weights |

Counts true: adequate **32.8%** (4819), borderline **44.2%** (6494), insufficient **23.0%** (3385). Sampled rule had adequate **70.5%** (10364) / moderate 7% / strong 2.9% / insufficient 19.5% — the drop from 70.5% to 32.8% is the *revealed* positivity problem, not a manipulation to improve output.

#### Sensitivity classes on true scale (from `sensitivity_class` in CSV)

* `stable_under_exposure_adjustment`: `adequate` and `|delta|<0.20` (also ESS>0.30, max_w<1740).
* `moderately_sensitive`: borderline with 0.20≤|delta|<0.50 or ESS 0.20–0.30.
* `strongly_sensitive`: |delta|≥0.50 or ESS<0.20 or extreme max_w.
* `insufficient_overlap`: as above.

Distribution true: stable **5014**, moderate **4711**, strong **1588**, insufficient **3385**. Among adequate, 88.6% are stable (4268/4819); among borderline, 64.2% moderate, 24.3% strong.

#### Screening mapping (derived from research objective, not candidate list)

The objective requires **genuinely good + underrated + hidden + appeal beyond niche**. So:

| Screening bucket | Definition | Effect on hidden-gem candidacy | Rationale |
|---|---|---|---|
| `stable_exposure` | `adequate_overlap` AND `stable` (|delta|<0.20) | **Pass** — quality stable under reweighting toward broader plausible population; standard broad-appeal check (§C) suffices | Most Other/Coop/Economic large-n games live here; reweighting adds little (mean |delta| 0.06 sampled, 0.13 true) |
| `exposure_sensitive` | `borderline` with moderate/strong, OR any `|delta|≥0.20` with adequate overlap | **Downgrade to caution** — do **not** auto-exclude; require **stronger cross-audience evidence** (≥2 splits with `n≥10` per side, `|diff_adj|<0.30`, non-significant, plus `|truncated_delta|<0.20` and direction-consistent). If fails, label `niche_but_high_quality`. | Material sensitivity (20.8% `|delta|≥0.2`) is real but heterogeneous (18XX SD 0.67) — some sensitive games are still broadly liked. Downgrade filters false broad-appeal without discarding them. |
| `insufficient_overlap` | `insufficient_overlap` on true scale | **Unknown** — cannot identify broader counterfactual; exclude from BGG-only hidden-gem claim; preserve as high-quality niche for external validation; do NOT call cult/bad | Weight explosion (median max_w 1449 but p95 7619) and ESS collapse mean `prop_adj` not reliable; 18XX 100% insufficient means we literally cannot tell breadth from this data |

#### Why `exposure_sensitive` downgrades rather than excludes

* **Evidence:** Mean `|delta_true|` 0.133 overall, but Wargame 31.6% ≥0.2, Party 31.8%, 18XX 69.1% — sensitivity is common enough that exclusion would discard ~20% of games, including many with genuine broad appeal that happens to correlate with type exposure.
* **Heterogeneity:** 18XX `delta_true` range −2.7 to +1.5, 39 negative <−0.1 vs 12 positive >+0.1 — not uniform inflation.
* **Cross-audience can adjudicate:** If non-specialists rate similarly (`diff` small) despite `delta` material, sensitivity reflects *who* rates, not *how* non-specialists would rate — breadth is still plausible. Example: 18Chesapeake `delta` −0.07 (small, but still borderline/insufficient by ESS) and specialist diff 0.00, volume diff −0.16 — specialist breadth despite type narrowness.
* **Alternative stricter rule** (exclude all `exposure_sensitive`) is defensible as a "very strict hidden gem" scope — framework documents both but chooses downgrade as primary, with strict variant as sensitivity.

#### Exactly which fields drive the bucket

Per-game: read `docs/phase2-pass2/step7c_exposure_propensity_validation/propensity_validation_game_level.csv`:

* `delta_quality` (`prop_adj_raw_true − adj_mean`), `stabilized_delta` (same rank), `truncated_delta` (cap20)
* `ess_ratio` (`ESS/n_obs`), `effective_sample_size`, `max_weight` (`max_w_true`), `p95_w_true`
* `mean_p` (`p_mean_raters` true), `mean_p_raters_sample` (sampled, for comparison)
* `overlap_status` (adequate/borderline/insufficient on true scale), `overlap_status_sample_rule` (for reference)
* `sensitivity_class` + `reason` (overlap+class), `penetration`/`penetration_type_ge20/ge10`, `propensity_model` (logistic_L2_C1.0_corrected_global_shift, primary)

Do not use `prop_adj_raw_sample` / `delta_raw_sample` for screening — they understate positivity. Keep `truncated_delta` as mandatory second look.

---

## C. Integrate Step 7 and Step 7C Correctly

### What each contributes

**Step 7 (42, audience selection):** observable pool description + realized-rating robustness.

* Concentration: `spec_primary_share_ge10/ge20`, `share_0_4`/`share_5_19`/`share_ge20` (other-count proxy), `herfindahl_volume`, `entropy_volume`, `share_vol_heavy_500plus`, `share_vol_light_10_24`, `share_within_0.5` (weight), `share_own` (collections snapshot).
* Distinctiveness: `TVD_volume_global` mean 0.167 SD 0.101, `TVD_volume_type` 0.152, `TVD_volume_weight` 0.166, `TVD_volume_decile` 0.146 — same-type most informative (global flags all Wargames as distinctive).
* Cross-audience: `cross_audience_results.csv` per split `n_low/n_high`, `mean_low/high_adj`, `diff_adj`, `se_diff`, `z`, `p`, `supported_ge10/ge5` for volume, specialist, ownership, weight splits (66,911 rows; volume ≥10 supported 9227, specialist ≥10 3973).
* Heterogeneity: SE-aware taxonomy `genuine_disagreement` 82.7% inflated by multiple testing — use per-split `z`, not raw SD.
* Penetration proxy: `exposure_proxy_results.csv` (6249 rows) `penetration_ge20/ge10` + `missing_ge20` among heavy enthusiasts; median penetration 18XX 0.297 vs Wargame 0.010.
* Taxonomy: `audience_selectivity_game_level.csv` 14,698 rows, counts low 3936 / moderate 6867 / high 1124 / insufficient 2771, thresholds q75 spec 0.939/TVD 0.231/own 0.664/herf 0.203.

Limitations: specialist share highly type-breadth dependent (mean 0.832 because Party 62k, Economic 105k dominate; 18XX median 0.24); category related mean 0.993 least discriminating; ownership snapshot; timestamp unresolved for other-count; `Other` penetration not globally computed.

**Step 7C (45+46, validated propensity):** plausible-rater reweighting + identification diagnostic.

* Prevalence correction: marginal 0.00572, shift −5.159, model discrimination AUC 0.822 prevalence / 0.825 balanced, calibration corrected ECE 0.00034 Brier 0.00558 vs sampled 0.34/0.168, weighted logistic similar.
* Weighting diagnostics: median max_w 1449 vs 9.3, ESS 0.33 vs 0.72, delta mean −0.015 median −0.016 mean|delta| 0.133 share≥0.2 20.8% share≥0.5 2.3% std 0.19 per-type (18XX −0.247, Wargame −0.044, Other −0.001), rank corr 0.973 top-100 Jaccard 0.626.
* Overlap diagnostics: 300–500 non-raters per game per population (602 games), rescaled thresholds (§B), weighting sensitivity raw vs stabilized identical, trunc recovers ESS but attenuates.

### Primary vs secondary vs diagnostic-only

**Primary (gates — must pass to support hidden-gem claim):**

1. **7C `overlap_status` + `sensitivity_class` / `delta_quality`** — *only* measure that answers "what if raters were reweighted toward broader observable population?" Critique of Step 7 threshold: 1830 Step 7 spec 0.054 (low) but 7C delta −0.321/Ess 0.12/insufficient, gateway more sensitive than specialist 1817 despite lower threshold, proving continuous exposure gradient beyond binary `spec≥10`. Correlation `|delta|` vs `spec_ge20` 0.38 leaves 62% unexplained — propensity adds info. Also penetration `ALL` vs `GE20` correlation for 18XX 0.62 moderate — population choice matters for niche.
2. **7 cross-audience diffs where `n≥10` per side** — *only* direct test of realized breadth (do non-specialists/light raters also rate highly?). ~50% of supported games have |diff|<0.30 non-significant (broadly consistent); ~18% significant specialist advantage; rest insufficient. Volume split 10–24 vs 500+ (9227 ≥10) is severity-purged (median diff 0.08 after adj); specialist 0–4 vs ≥20 (3973) targets type exposure.

**Supporting (corroborate, disambiguate, but not gate alone):**

* 7 composition: `spec_share_ge10/ge20`, `share_ge20`, `TVD_volume_type` (primary distinctiveness), `herfindahl`, `share_within_0.5`, `share_own`, `mean_delta_raters`. Support interpretation of *who* is in pool; e.g., 18XX Catan spec 0.50 but global broad inflates, so read Party/Economic with ≥20.
* 7 penetration: `penetration_ge20` vs `penetration_all` shows within-type selectivity (median 18XX 0.297 vs Wargame 0.010).
* 7C corroboration: `ess_ratio`, `max_weight`, `mean_p`, `truncated_delta`, `p_mean_w`.

**Diagnostic-only (report caveat, do not gate):**

* `share_cat_related` 0.993 (least discriminating, `methodology_comparison.md`), per-game cat for Other not globally computed, weight NULL 7, `RF` vs logistic delta diff 0.03 (shows robustness but RF overconfident).

### Ordering / flow (why 7C is gate, 7 cross-audience is test, 7 composition is支撑)

```
Population (14,698) → 7C overlap/ESS as GATE (identified?)
                          │
                          ├─ insufficient → UNKNOWN (stop, external data needed)
                          │
                          ├─ borderline/sensitive → needs STRONGER 7 cross-audience parity
                          │
                          └─ adequate/stable → standard 7 cross-audience parity
                                            │
                                            └─ 7 composition/penetration as SUPPORTING narrative
                                               (who is the audience, how selective within type)
```

**Justification:** 7C tells us whether any claim about a broader counterfactual is identified at all; if not, no amount of composition detail fixes it. 7 cross-audience tells us whether breadth is *observed* among realized diverse raters; if yes, it can corroborate even sensitive cases. 7 composition tells us *why* a pool is narrow (type specialist vs weight vs volume concentration) — useful for interpretation but not proof of breadth.

### Why not collapse into one opaque score

* Different units and thresholds: `spec` is share (0–1, q75 0.939 inflated by broad types), `TVD` is distance (0–1, mean 0.16), `delta` is rating points (SD 0.19, thresholds 0.2/0.5), `ESS_ratio` is fraction (median 0.33), `diff_adj` is rating points with SE. No principled single weighting; any score would trade interpretability for false precision.
* Threshold sensitivity is real: Catan 0.50 spec moderate not low because Economic broad; 18XX gateway low spec but large delta — single score would hide which piece drove it.
* Framework's promise: keep five separate columns, auditable per game, with each threshold cited and disclosed.

---

## Summary Table for Implementers

| Step | File | Primary fields to join | Role |
|---|---|---|---|
| 7C | `propensity_validation_game_level.csv` 14,698 | `game_id, overlap_status, sensitivity_class, delta_quality, truncated_delta, ess_ratio, max_weight, mean_p, penetration, penetration_type_ge20` | **Gate**: stable/sensitive/insufficient |
| 7 | `cross_audience_results.csv` 66,911 | `game_id, split_type, n_low, n_high, diff_adj, se_diff, z, p, supported_ge10` | **Primary test**: does breadth replicate? (`n≥10` per side) |
| 7 | `audience_selectivity_game_level.csv` 14,698 | `spec_primary_share_ge10/ge20, tvd_volume_type/global, herfindahl_volume, share_own, taxonomy, deviation_count` | **Supporting** composition |
| 7 | `exposure_proxy_results.csv` 6249 | `penetration_ge20, missing_ge20, spec_ge20` | **Supporting** within-type selectivity |
| 7C | `propensity_validation_summary.json` | `marginal, shift_logit, overlap_counts, delta_stats, weighting, known_cases` | **Diagnostics** + thresholds |

Do not use `prop_adj_raw_sample`/`delta_raw_sample` (sampled scale) or `prop_adj` as quality. Always report `truncated_delta` alongside `delta_quality` and `supported_ge10` alongside any claimed parity.

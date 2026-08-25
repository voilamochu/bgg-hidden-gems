# Step 8 — Hidden-Gem Screening Design: Formalizing Observable Audience Selection

**Population (canonical, confirmed):** 14,698 games × 287,302 users × 24,146,307 rating observations, `data/processed/phase2-pass2/` (validated, mu≈7.139, `user_severity_pass2.parquet` + `game_adjusted_means_pass2.parquet` via scripts 39/40 — reuse, do NOT refit). Built on Step 7 (`docs/phase2-pass2/step7_audience_selection/`), Step 7B (`step7b_exposure_propensity/`), and Step 7C (`step7c_exposure_propensity_validation/`, merged as PR 28 at `0ef6375`). Do not rebuild Phase 2/5/6 here.

**Scripts:** No new heavy compute. Reuses 7/7B/7C CSVs/JSONs/MDs on `origin/main`. Any local recomputation keeps bounded DuckDB 4GB/threads 3 and never materializes 4.2B pairs.

**Status:** Framework only — no hidden-gem score, no final candidate list. Outputs auditable rules that will produce the list in a later step.

---

## Executive Summary

Step 7–7C built two observable families of evidence beyond severity-adjusted quality:

* **Step 7 composition & cross-audience** — who rated the game (specialist share, TVD, volume Herfindahl, ownership) and whether non-specialists rate it similarly when support exists (`n≥10` per side).
* **Step 7C propensity sensitivity** — after correcting the 87× sampling-fraction error (marginal 0.572%, logit shift −5.159, `p_true` via `expit(logit(p_sample)−5.159)`), the model discriminates (AUC 0.822 on prevalence holdout) and calibrates (ECE 0.00034, Brier 0.00558) but reveals that **positivity/overlap is only adequate for 32.8% of games** (median `max_w_true` 1449 vs 9.3 sampled, 156×; median `ESS_ratio_true` 0.33 vs 0.72; `max_w` p95 7619, p99 16566).

Because credible reweighting is identified for only one-third of games and `insufficient_overlap` concentrates in niche types (18XX 100%, Wargame 52.9%), **audience-selection evidence belongs in hidden-gem screening, not in the quality estimator**. `adj_mean` (severity-adjusted, mu 7.139) remains the quality estimate; propensity-adjusted `prop_adj` is a **sensitivity diagnostic**. Step 7C overlap/ESS is the primary screening gate; Step 7 cross-audience and composition are supporting evidence.

The framework keeps five dimensions separate — no opaque score:

| # | Dimension | Question | Primary measure (source) | Role in pipeline |
|---|-----------|----------|--------------------------|------------------|
| 1 | **QUALITY** | Is it genuinely good after rater severity? | `adj_mean` from `game_adjusted_means_pass2.parquet` (mu 7.139) | Independent threshold; screening prerequisite |
| 2 | **UNDERRATEDNESS** | Is it better than expected from observable characteristics? | Phase 5/6 residuals / Q3b/OLS vs expected rating (do NOT refit) | Reference baseline; comparative, not corrective |
| 3 | **HIDDENNESS** | Is it sufficiently obscure per project definition? | `n_obs` / `users_rated` / `penetration` (Step 7 exposure_proxy + 7C `penetration`) | Project definition gate |
| 4 | **AUDIENCE-SELECTION RISK** | Does observable selection materially threaten interpretation? | Step 7C `overlap_status` + `sensitivity_class` (`delta_quality`, `ess_ratio`, `max_weight`, `mean_p`) under rescaled rule | Screening gate: `stable_exposure` / `exposure_sensitive` / `insufficient_overlap` |
| 5 | **BROAD-APPEAL EVIDENCE** | Is there positive evidence appeal extends beyond niche? | Step 7 `cross_audience_results.csv` diffs where `n≥10` per side (specialist 0–4 vs ≥20, volume 10–24 vs 500+) + 7C sensitivity as corroboration | Requires positive cross-audience parity |

**Minimum to eventually call hidden gem:** pass QUALITY ∩ UNDERRATEDNESS ∩ HIDDENNESS, plus **either** `stable_exposure` with supporting cross-audience parity **or** `exposure_sensitive` that survives stronger cross-audience evidence and truncated-sensitivity check; `insufficient_overlap` is **unknown** and cannot support a hidden-gem claim without external validation (plays/sales). See `screening_framework.md` for flow, gates, and confidence tiers.

---

## Answers to the 5 Required Questions

### 1. Does audience selection belong in the quality estimator?

**No.** See `audience_selection_policy.md` §A and `quality_vs_underratedness_vs_hiddenness.md`.

Reasoning (6 pieces, all from 7C diagnostics):

1. **Adequate only where 33%** — `adequate_overlap` 4819/14698 (32.8%); `borderline` 44.2%, `insufficient` 23.0%. Global correction would rest on non-identified reweighting for two-thirds of games.
2. **Insufficient dominates niche** — 18XX 81/81 (100%) insufficient, Wargame 1068/2020 (52.9%) insufficient on true scale (vs 66.7% sampled). A global estimator would be most distorted where niche candidates live.
3. **Weighting magnitude 156× larger after correction** — median `max_w_true` 1449 vs sampled 9.3; p95 7619, p99 16566, max 65414. Sampled scale hid positivity failures; true scale shows they are material.
4. **Stabilized vs raw identical rank** — `corr(stabilized, raw) ≈1.0`; stabilizing by `p_marginal` does not change ordering. No gain from folding in.
5. **Truncation at 20 attenuates signal** — median `ESS_ratio` 0.33→0.98 with cap20, std of `delta` 0.19→0.03, share `|delta|≥0.2` 20.8%→0.2%. Truncation recovers stability by discarding the sensitivity we want to measure.
6. **RF overconfident vs corrected logistic** — RF AUC 0.849 but ECE 0.324 on prevalence; corrected logistic ECE 0.00034, weighted 0.00014. The model good enough for sensitivity is not good enough for a quality correction, and `|delta|` correlates only 0.38 with `spec_ge20` (62% unexplained) — it adds screening info but not estimator improvement.

The broader counterfactual (all 287k users exposed) is **not identified** for many niche games. `adj_mean` (additive `mu+alpha+delta`, mu 7.139, R² 0.393, parity r 0.877) remains sufficient; earlier `rater×type` joint test found `<1%` variance from type interactions and no flag warranted type-adjusted quality.

### 2. How should `stable_exposure`, `exposure_sensitive`, `insufficient_overlap` affect screening?

See `audience_selection_policy.md` §B and `screening_framework.md` §3.

**Carry forward rescaled rule (true scale, justified from diagnostics):**

* `insufficient_overlap` if `n_obs<150` OR `max_w_true>8700` (100×87, p95≈7619) OR `ESS_ratio_true<0.10` OR `mean_p_true<0.005` (~marginal 0.0057).
* `borderline_overlap` if not insufficient AND (`max_w_true>1740` (20×87, median 1449) OR `ESS_ratio<0.30` (median 0.33) OR `mean_p<0.015` (≈3×marginal)).
* `adequate_overlap` else.

Thresholds cited from 7C weight/ESS/mean_p diagnostics (`overlap_rules.md`): median `max_w_true` 1449, p95 7619, `ESS_ratio` median 0.33 p10 0.17, `mean_p` median 0.027 p30 0.015.

Mapped to screening classes (from `propensity_validation_game_level.csv` fields `delta_quality`, `ess_ratio`, `max_weight`, `mean_p`, `overlap_status`, `sensitivity_class`):

| Screening class | 7C mapping | Interpretation | Gate effect |
|---|---|---|---|
| `stable_exposure` | `adequate_overlap` AND `sensitivity_class=stable_under_exposure_adjustment` (|delta|<0.20, ESS>0.30, max_w<1740) | Quality stable under observable reweighting | **Pass** — eligible for hidden-gem candidacy if other dimensions pass; cross-audience parity expected |
| `exposure_sensitive` | `borderline_overlap` with `moderately_sensitive` (|delta| 0.20–0.50) OR `borderline` with `strongly_sensitive` (|delta|≥0.50 or ESS<0.20 or max_w>50 on sampled-equivalent) — aggregates 7C moderate+strong | Observable selection materially changes estimate; may be niche-driven | **Downgrade to caution** — requires **stronger cross-audience evidence** (≥2 splits with `n≥10` per side, `|diff|<0.30` and non-significant) **and** truncated sensitivity check (`|truncated_delta|<0.20` or direction consistent); otherwise `niche_but_high_quality` |
| `insufficient_overlap` | `overlap_status=insufficient_overlap` (also `sensitivity_class=insufficient_overlap`) — all 7C insufficient | Broader counterfactual not identified (weights explode, ESS collapses) | **Unknown** — exclude from hidden-gem candidacy on BGG data alone; preserve as high-quality niche candidate for **external validation** (plays/sales). Do **not** call cult/bad. |

`exposure_sensitive` **does not auto-exclude**. Downgrade rationale: 20.8% of games have `|delta|≥0.2` on true scale (mean |delta| 0.133, std 0.191, rank corr adj vs prop_adj 0.973 but top-100 Jaccard 0.626) — sensitive but not uniformly wrong. Requiring stronger cross-audience parity filters false broad-appeal claims without discarding sensitive-but-broad games. `insufficient_overlap` = uncertainty, not evidence of cult: 18XX gateway 1830 `delta_true` −0.321 but ESS 0.12, max_w 50707 — sensitivity exists but not identified.

### 3. Which Step 7/7C measures should be primary vs supporting?

See `audience_selection_policy.md` §C.

**Primary (screening gates):**

* **7C `overlap_status` + `sensitivity_class` / `delta_quality`** — the only measure of what happens if raters were reweighted toward broader plausible population; unique info beyond Step 7 (corr 0.38 with `spec_ge20`).
* **7 cross-audience diffs where `n≥10` per side** — `specialist 0–4 vs ≥20` (rated type exposure `n_flag−1` bins), `volume 10–24 vs 500+`, with `diff_adj`, `se_diff`, `z`, `p`, `supported_ge10`. Direct test: does high quality remain among non-specialists/light raters? 9227 games have volume support ≥10, 3973 specialist.

**Supporting (interpretation, heterogeneity, corroboration):**

* **7 composition:** `spec_primary_share_ge10` / `ge20`, `share_0_4`/`share_ge20` (other-count proxy), `TVD_volume_type` (same-type most informative, mean 0.152 vs global 0.167), `TVD_volume_global`, `herfindahl_volume` (q75 0.203), `share_within_0.5` (weight), `share_own` (q75 0.664, snapshot caveat). Thresholds q75: spec 0.939, TVD 0.231, own 0.664, herf 0.20 — but broad categories inflate spec mean 0.832, so type-specific reading needed.
* **7 penetration proxy:** `penetration_ge20` / `penetration_all` / `penetration_type_ge10` (exposure_proxy_results.csv, Step 7C `penetration`). Median 18XX 0.297 vs Wargame 0.010 — niche selectivity diagnostic.
* **7C corroboration:** `ess_ratio`, `max_weight`, `mean_p`, `truncated_delta` (cap20), `mean_p_raters` weighted.

**Diagnostic-only (do not gate, report for caveat):**

* `share_cat_related` (mean 0.993, least discriminating — 7 `methodology_comparison.md`), `share_cat_or_mech_related`, weight-missing games (7), collection `own` snapshot, `penetration` for `Other` (not globally computed), `ESS_trunc`, `RF` delta variation.

**Ordering justification:** 7C overlap/ESS is gate because it determines whether any reweighting claim is identified; 7C `delta` is sensitivity magnitude; 7 cross-audience is primary broad-appeal evidence because it tests realized ratings across realized diverse raters; 7 composition/penetration are supporting because they describe who is in the pool but not how they rate.

### 4. What evidence is required to distinguish plausible hidden gem from high-quality niche/cult candidate?

See `screening_framework.md` §4 and `cult_vs_hidden_interpretation.md`.

**No dimension alone suffices.** Hidden gem ≡ QUALITY ∧ UNDERRATEDNESS ∧ HIDDENNESS ∧ (AUDIENCE-SELECTION gate passes or is corroborated) ∧ BROAD-APPEAL positive evidence.

| Dimension | Minimum quantitative gate (auditable) | Qualitative judgment remaining |
|---|---|---|
| QUALITY | `adj_mean` ≥ threshold defined from distribution (e.g., ≥7.5 or top-quartile of `game_adjusted_means_pass2`; state choice explicitly; independent of `n_obs`) | Which threshold reflects "genuinely good" vs "excellent for audience" is manual (preserved in `open_manual_judgments`) |
| UNDERRATEDNESS | Residual `observed − expected` vs Phase 5/6 expectation (Q3b/OLS) ≥ declared quantile (e.g., top 10% or ≥+0.5, referencing S3/S5 dispersion SD 0.55, 95th +0.87); do NOT refit; report specification sensitivity (S3 vs S5) | Choice of expectation model (S3 category vs S5 band/decade) and residual cutoff is manual |
| HIDDENNESS | `n_obs` ≤ band declared in project definition (e.g., 100–1500) **and** `penetration_all`<0.05 or `penetration_type_ge10`<0.10; `users_rated` band derived from same | Band boundaries are project definition, not data-driven |
| AUDIENCE-SELECTION | `stable_exposure` (adequate+stable) required for `strong_hidden_gem_evidence`; `exposure_sensitive` requires ≥2 cross-audience splits `supported_ge10` with `|diff|<0.30` and `|z|<2` **and** `|truncated_delta|<0.20` to upgrade to `plausible_hidden_gem`; else `niche_but_high_quality`; `insufficient_overlap` → `insufficient_broad_appeal_evidence` regardless of other dimensions | Downgrade vs exclude for `exposure_sensitive` was methodological; exact `|diff|<0.30` and `|truncated_delta|<0.20` are conventional and disclosed as manual |
| BROAD-APPEAL | Positive evidence: for ≥2 splits, non-specialist / light-rater severity-adjusted mean within 0.30 of specialist/heavy and non-significant, with `n≥10` per side; no split showing `diff≥0.50` with `p<0.05` against broad appeal | What counts as "materially different audiences" and whether volume vs specialist is more probative is interpretive |

**Decision table:**

* `strong_hidden_gem_evidence` — passes all five, with `stable_exposure` and ≥2 cross-audience parities. Interpretation: high quality that is underrated, obscure, and demonstrably not dependent on niche audience in observable data.
* `plausible_hidden_gem` — passes QUALITY/UNDERRATEDNESS/HIDDENNESS, `exposure_sensitive` but **survives** stronger cross-audience test and truncation check. Interpretation: sensitive to observable selection but corroborated breadth; plausible but closer scrutiny needed.
* `niche_but_high_quality` — passes QUALITY (and maybe UNDERRATEDNESS/HIDDENNESS) but `exposure_sensitive` without corroboration, or `borderline` with material `|diff|≥0.30`. Interpretation: excellent within niche, no evidence it generalizes; not a failed game.
* `insufficient_broad_appeal_evidence` — any `insufficient_overlap` (or cross-audience `supported_ge10` false for all splits). Interpretation: unknown — cannot tell broad vs niche; requires external data (plays, sales, time).

All four tiers distinguish **hypotheses about observed evidence**, not facts about the game. `insufficient_overlap` never implies cult.

### 5. Which decisions are methodological rules vs qualitative/manual judgments?

See `screening_framework.md` §5, `step8_decisions.json` `open_manual_judgments`.

**Methodological (derived from evidence, auditable, reuse without re-deriving):**

* Keep `adj_mean` as quality (not `prop_adj`) — justification §A above.
* Do not impute missing ratings; do not interpret non-raters as negative; do not claim causal exposure.
* Exposure is screening/sensitivity, not quality correction (global severity-adjusted estimator remains appropriate — 7C no fold-in).
* Overlap rule thresholds (7C rescaled: `max_w≤1740`/`>8700`, `ESS_ratio≥0.30`/`0.10`, `mean_p≥0.015`/`0.005`) — justified from median `max_w` 1449, p95 7619, ESS median 0.33, mean_p median 0.027.
* Primary vs secondary mapping (§3) — justification via discrimination, overlap, correlation.
* `insufficient_overlap` = unknown (not bad/cult).
* Stabilized vs raw identical rank — report raw with truncation as sensitivity, not selection.

**Manual / qualitative (remain open, must be stated explicitly in any future candidate screen):**

* Numerical cutoffs for QUALITY (`adj_mean≥7.5` vs ≥7.8 vs percentile), UNDERRATEDNESS (residual quantile, which Phase 5/6 model S3 vs S5), HIDDENNESS (`n_obs` band/pene thresholds) — project definitions, not data-identified.
* Whether `exposure_sensitive` should **exclude** vs **downgrade** to caution — framework chooses downgrade+stronger evidence (derived from research objective: "genuinely underrated and broadly appealing" requires corroboration, not auto-exclusion), but a stricter hidden-gem definition could exclude; this is scope choice.
* Exact broad-appeal parity thresholds (`|diff|<0.30`, `z<2`, `n≥10`, ≥2 splits, `|truncated_delta|<0.20`) — conventions disclosed as sensitive; should be sensitivity-analyzed.
* Language: "cult" vs "hidden" — hypotheses, not facts; calling a game cult requires external audience/reception evidence beyond BGG ratings.
* Confidence tier labels themselves — useful for communication but not mechanistic; final candidate list must show which dimension passed/failed.

---

## How to Use This Framework

1. **Start from quality.** Pull `adj_mean` and `n_obs` from `game_adjusted_means_pass2.parquet` + `games_pass2.parquet`. Apply QUALITY gate independent of popularity.
2. **Check underratedness.** Join Phase 5/6 expected model (when refreshed on pass2) — residual as reference, not correction.
3. **Check hiddenness.** Apply `n_obs` band and 7/7C penetration band. This is scope, not quality.
4. **Screen audience-selection risk.** Join `propensity_validation_game_level.csv` fields `overlap_status`, `sensitivity_class`, `delta_quality`, `ess_ratio`, `max_weight`, `mean_p`. Classify `stable_exposure` / `exposure_sensitive` / `insufficient_overlap` via §2 rule. **Do not use `prop_adj` as quality.**
5. **Test broad appeal.** Pull `cross_audience_results.csv` diffs `supported_ge10`; require parity per §4. Cross-check `truncated_delta` from same 7C row.
6. **Assign confidence tier** per decision table §4; report which gates passed, which relied on manual cutoffs. Never collapse to a hidden-gem score — preserve five columns.
7. **Needs external check?** `insufficient_overlap` or `niche_but_high_quality` games need plays/sales/time evidence before any hidden-gem claim.

### Files in This Design

* `screening_framework.md` — full multi-dimensional framework, gates, flow diagram, decision tables.
* `quality_vs_underratedness_vs_hiddenness.md` — why the three are separate, where Phase 5/6 fits, why `adj_mean` stays.
* `audience_selection_policy.md` — §A/B/C: should quality change? how exposure classes gate; primary vs secondary.
* `cult_vs_hidden_interpretation.md` — conceptual interpretation and limits.
* `known_case_examples.md` — per-game table for 1830/1817/1870 (+1846/18Chesapeake) and Catan/Ticket to Ride (+Pandemic/Carcassonne) with Step7 share/TVD, 7B delta, 7C delta_true/overlap/ESS, and disposition buckets 1–5 / confidence tier.
* `step8_decisions.json` — machine-readable decisions, thresholds, and open judgments.

**Mirrored to:** `reports/phase2_pass2/step8_hidden_gem_screening_design/` (review copy).

### Interpretation Rules (carried from 7/7C, still enforced)

* Do not claim self-selection solved.
* Distinguish observable rater-pool selectivity, user×type taste, and unobserved non-rater selection.
* Do not alter quality estimator (`mu`, `delta_u`, `adj_mean` fixed).
* Do not create hidden-gem score in this step (framework only).
* Do not call a game "cult" or "hidden" factually — hypotheses about observed evidence.
* `insufficient_overlap` means unknown, not bad.
* Do not impute missing ratings; non-raters are not negative.
* Tag claims: observed fact / empirical finding / assumption / hypothesis / model-dependent conclusion / speculation.

### Reproduction

No new script required. Reuses:

* `docs/phase2-pass2/step7_audience_selection/audience_selectivity_game_level.csv` (14,698) + `cross_audience_results.csv` (66,911) + `known_case_sanity_check.md`
* `docs/phase2-pass2/step7c_exposure_propensity_validation/propensity_validation_game_level.csv` (14,698) — fields `delta_quality`, `ess_ratio`, `max_weight`, `mean_p`, `overlap_status`, `sensitivity_class`, `penetration`, `truncated_delta`
* `docs/phase2-pass2/step7c_exposure_propensity_validation/overlap_rules.md`, `propensity_calibration.md`, `weighting_sensitivity.md`, `propensity_validation_summary.json`
* `data/processed/phase2-pass2/game_adjusted_means_pass2.parquet` (mu 7.139)

If recomputing: bounded DuckDB 4GB/threads 3, `scratch/phase2-pass2` copy-once pattern from scripts 39/40/43/45, streaming per-row-group 195×124k via `X·coef_raw + GROUP BY`.

### Limitations (preserved)

* Phase 5/6 not yet refreshed on pass2 14,698 — underratedness thresholds reference historical 16,726 S3 findings (SD 0.55, 95th +0.87) and must be re-fit before final screen.
* `Other` games penetration not globally defined (per-game category sets heavy) — hiddenness for Other relies on `n_obs` only until computed.
* Timestamp semantics (`postdate`/`rating_tstamp`) unresolved — `cnt_type` other-count is exposure proxy, not true chronological prior; run time-based results under both readings if revisited.
* `ESS_ratio`/`max_w` thresholds are conventional even when data-justified — disclose and sensitivity-analyze.

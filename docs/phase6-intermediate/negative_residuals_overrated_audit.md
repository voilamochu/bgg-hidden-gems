# INTERMEDIATE / NOT FINAL — Negative residuals ≠ "overrated" without qualification

> **Status:** Intermediate audit of Phase 6 expected-quality residuals (`Q3b/OLS` on active `adj_mean`). Not a hidden-gem ranking and not a final research output. Do not use to produce a hidden-gem score. Preserves the distinction: **underratedness** (conditional anomaly `adj_mean − E[adj_mean|X]`) vs **hidden gems** vs **broad appeal**.

**Task:** Workstream 3 — Evaluate whether large negative Phase 6 residuals can be treated as "overrated" games.

**Provenance (source):**
- Estimand: `adj_mean_g = AVG(rating − delta_u)` with `mu = 7.144`, `sigma_e = 1.194`, `sigma_alpha = 0.864` from `scripts/26_phase2_active_baseline_refresh.py` / `scripts/30` (see `docs/phase2-active/active_baseline_refresh.json`, `docs/phase2-active/phase5_quality_comparison.json`).
- Uncertainty: `SE_g = sigma_e / sqrt(n_active)` with `sigma_e = 1.194`. Observed `n_active` distribution (Phase 5): `P10 100` / `P50 293` / `P90 2795` → `SE` `0.119 → 0.070 → 0.023` (Phase 6 uses same formula; `SE P10 0.023`, `P50 0.070`, `P90 0.119` in `phase5_quality_comparison.json:se_table_n_examples`).
- Population: active **16,627 × ≥10 ¬strict** (≥10 filtered ratings per user within population, minus 667 `degenerate_strict` users/48,573 obs; 24,509,788 obs, 288,730 users, 16,564 games with ratings; see `docs/phase2-active/README.md`, `active_baseline_validation.json`). Estimation sample for Phase 6: **16,549 games** (15 dropped for missing `weight`/`playing_time`; `docs/phase2-active/phase6_comparative.json:estimation_sample`).
- Model: `Q3b_flex_volume / OLS` preferred — 8 volume-band dummies + natural-spline year (knots at .05/.35/.65/.95) + `weight_c` + `log_playtime_c` + `min_players_c` + `log_max_players_c` + `is_reimpl_num` + `log_n_impl_c` + 28 category flags (≥500 games); 46 features; CV R² 0.5822 ±0.0234, RMSE 0.5633 (`docs/phase2-active/phase6_comparative.json`, `reports/phase6_underratedness/comparative_table.csv`). Tags overlap; indicators are descriptive contrasts, not causal.
- **80.89% caveat:** `games` table covers 13,449/16,627 (80.89%); `bgg_research_population.parquet` is complete and preferred (`docs/phase2-active/phase6_comparative.json:limitations`, `PARQUET_CATALOG.md`). Raw `games.parquet` not used for features.
- Residual: `underratedness_g = adj_mean_g − expected_quality_g` (Q3b/OLS pred), stored in `data/processed/phase2-active/phase6_residuals_active.parquet` (gitignored) with `expected_quality_pref`, `underratedness_pref`, `underratedness_cv_pref`, `underratedness_wls_pref`, `underratedness_ols_Q3`, `underratedness_wls_Q3`, `se_adj`. Reports: `reports/phase6_underratedness/{comparative_table.csv,residual_overlap.csv,low_n_residual_stability.csv,coefficient_table.csv,top_residuals_preview*.csv}`. Comparative JSON: `docs/phase2-active/phase6_comparative.json` (and `phase6_volume_diagnostic.json`).
- Method discipline: copy-once to `scratch/phase2-active`, DuckDB 4GB/threads 3, `scratch/ducktmp`, single grouped even/odd pass over `rating_observations_active` (see `scripts/31_phase6_expected_quality_underratedness.py`). No wide-table bug. No external broad-appeal validation.
- Claim tags follow `AGENTS.md`: observed facts / empirical findings / model-dependent conclusions / assumptions / hypotheses / speculation.

---

## 1. What a negative residual literally means — and does not mean

**Observed fact (definition):** For game `g`,

```
resid_g = adj_mean_g − E[adj_mean_g | X_g]
        = adj_mean_g − expected_quality_g
```

where `X_g = {volume band (n_active), spline year, weight, playtime, players, reimplementation, 28 categories}`. `adj_mean_g` itself is `mu + alpha_g` estimated by `AVG(rating − delta_u)` with `delta_u` from `scripts/26` (active ALS). Negative `resid_g` = observed severity-adjusted mean is **lower** than the conditional mean predicted for other games sharing the same volume band, era shape, weight, playtime, player-count, reimplementation status and category mix.

**Model-dependent conclusion:** This is an **operational conditional anomaly** on the active `adj_mean` scale, with `SE_g = 1.194/√n_active` on the `adj_mean` side only (regression uncertainty not included). It is not:

- an estimate of latent "true quality" (no ground truth);
- a measure of broad appeal or rank (volume is on the right side — "expected given popularity");
- a debiased causal effect (tags overlap, measurement error in `X` not modeled, no external validation).

**Hypothesis vs fact:** Whether that anomaly reflects "overratedness" (audience inflated the rating), misspecification, noise, omitted variables, or selection is a **hypothesis** until evidence distinguishes them. The residual alone cannot adjudicate.

---

## 2. Six interpretations examined

| # | Interpretation | Targeted phenomenon | What would support it | What else produces same pattern | Can current data distinguish? |
|---|----------------|---------------------|----------------------|--------------------------------|-------------------------------|
| 1 | **Genuinely overrated** relative to observables | Game's `adj_mean` is low given its `X` because its rater/buyer pool was ex-ante more enthusiastic than typical for those `X` (e.g., IP halo, marketing, edition hype) and experience then disappointed. | Negative resid concentrated at high expected quality / high volume with precise `SE`; stable across specs; not explained by noise/selection diagnostics. | Misspecification (missing `X` that would lower expectation); omitted marketing/IP (Section 4); noise at low `n`; non-additive selection (Section 5). | **Only partially** — residual is descriptive; "genuinely" implies counterfactual broad-audience quality we do not observe. No external broad-appeal validation. |
| 2 | **Model misspecification** | Missing interaction / nonlinear `year`/`weight` / omitted structure not captured by Q3b's additive, linear-in-parameters form. | Systematic residual mean by `X` (weight bin, decade, volume band, category). | Omitted trait (Sec. 4) or genuine overratedness could also load onto `X`. | **Testable within data** — see Section 3. Phase 6 already tested linear vs spline vs bands. |
| 3 | **Noisy estimates (low-n)** | `adj_mean_g` measured with error `SE = 1.194/√n_active` (0.119 at P10 `n=100`, 0.023 at P90 `n=2795`, order-of-magnitude heteroscedasticity; `phase6_comparative.json:wls_note`). Low-`n` extremes may be sampling tails. | Large `|resid|` at small `n`; `|resid|` vs `SE` positive; residual flips sign when using half-sample `adj`. | Genuine quality also varies at low `n`; WLS reweights rather than fixes (see below). | **Directly testable** — see Section 4 + stability. |
| 4 | **Omitted game characteristics** | Publisher, marketing/promo intensity, edition/expansion lineage, art/production, IP, KS exclusivity, duration of availability — none in `bgg_research_population`. | Residuals cluster by omitted trait; spec expansion (Q4 mechanics) moves negatives materially. | Same clustering could be taste/selection. | **Not identified** here — population metadata is complete for included `X` but incomplete for omitted traits; `games` 80.89% coverage deliberately excluded. |
| 5 | **Audience-selection effects beyond `delta`** | Within-game pool differs from population beyond additive rater severity (`delta_u`) in ways that affect `adj_mean`. | Phase 4 pool deviation predicts residual beyond `delta`. | Phase 4 found selection residual `mean ≈ 0`, `SD 0.015` (`phase4_selection.json:layer_b_summary`), i.e. near-zero. | **Near-zero on tested additive form** — see Section 5. Non-additive forms untested. |
| 6 | **Combination** | All above jointly. | Heterogeneous origins across games. | — | **Most plausible as population** — no single mechanism explains all negatives; audit must treat them case-by-case. |

**Verdict:** A large negative residual is **some combination** of (1)–(5). Interpreting it as "overrated" without qualification **overclaims precision** — it conflates the residual with a causal/quality claim that requires external broad-appeal validation. The task's `central problem: self-selection` applies symmetrically: just as `high rating from small group ≠ broad appeal` (positive side), **low residual from small or IP-selected group ≠ objectively overrated for broader audience** without evidence beyond `delta`.

---

## 3. Empirical characterization of negative residuals

### 3.1 Distribution

- **Observed fact (parquet, 16,549 games):** `resid` mean `≈ 0` (−2.9e−12), SD `0.562`, P1 −1.55, median +0.02, P99 +1.30 (`empirical finding` from `scratch/phase6_residuals_active.parquet:describe`). Histogram is roughly symmetric with mild positive skew: 50.2% ≤ 0 (49.8% negative, 50.2% positive+zero); 72 negatives with `resid < −2`, 14 positives with `resid > +2`.
- **`|resid|` vs precision:** `corr(|resid|, SE) = +0.18`; `corr(|resid|, log n) = −0.19` (`empirical finding`). Larger absolute residuals are modestly more common where precision is lower, but the relationship is weak — between-game signal dominates noise (see stability).
- **As negatives:** mean `adj_mean = 6.51`, `expected = 6.94` (`resid ≈ −0.43`); positives: `adj_mean = 7.31`, `expected = 6.91` (`resid ≈ +0.40`). Negatives are **low observed quality given high expectation**, positives the converse. Negative mean `raw_mean = 6.24` vs positive `7.00` — negatives are also low on raw scale (raw−adj shift is mean `−0.293 ±0.177` per `phase4_selection.json`).

### 3.2 Not concentrated by popularity or quality range

- **Volume bands:** `corr(resid, log n) = −0.004` (`comparative_table.csv:Q3b_flex_volume/ols/corr_resid_logn`), `max|band mean| = 3.7e−12` by construction for Q3b (`model-dependent`). Decile-mean `resid`: −0.025 to +0.023 with no monotonic trend; share negative per decile 46–52% (`empirical finding`, see computation in scratch). **Negatives are not a volume artefact** — the band dummies absorb the convex, non-monotonic volume curve documented in `phase6_volume_diagnostic.json:band_table` (sub-100 games adj 7.17 above 100–199 adj 6.64; Section 2.3 of Phase 6).
- **By year:** residual mean by era is near-zero (`−0.06` 1950–70, `+0.06` 1990–2000, `−0.02` 2000–10, `−0.01` 2020–26); SD per era 0.52–0.76. No era is systematically negative after spline year (`empirical finding`). Linear-year specs (Q1/Q3) left decade means of `−0.19` to `+0.43` (`findings.md` Phase 6 Part B), which Q3b's spline remedies — a misspecification check.
- **By weight:** `corr(resid, weight) ≈ 0` (3.5e−14); mean resid light `−0.019`, medium `+0.031`, heavy `−0.011` (`empirical finding`). Negatives are **slightly** lighter than positives (5th percentile weight 1.93 vs 2.04) but not concentrated.
- **By expected quality:** `corr(resid, expected) ≈ 0` by OLS construction (2e−12); `corr(resid, adj_mean) = +0.645`. Large negative `resid` ⇒ low `adj_mean` **relative to** its expectation, not mechanically tied to low or high absolute quality — negatives span the quality range but sit lower on average because disappointment has more room where expectation is high.

### 3.3 Stability across specifications (do negatives stay negative?)

From `residual_overlap.csv` and `phase6_comparative.json:wls_vs_ols,low_n_residual_stability`:

- **OLS Q3b vs OLS Q3 (linear vs band volume):** `spearman 0.985`, `Jaccard top-1% 0.675` (`empirical finding`). Among negatives, **94.2% stay negative** when switching Q3b → Q3; bottom-1% most negative (165 games): **100% stay negative** in Q3.
- **OLS Q3b vs WLS_n Q3b (weighting):** `spearman 0.963`, `Jaccard 0.737`; negatives staying negative: **91.7%**; bottom-1%: **100%**.
- **OLS Q3b vs OLS Q4 (+34 mechanics):** `spearman 0.958`, `Jaccard 0.579`; negatives staying negative at Q3 is lower than weighting but extreme negatives remain stable.
- **OLS Q3 vs WLS Q3:** `spearman 0.951`, `Jaccard 0.642` — weighting shift is +28–48% on `beta_logn` but residual rank `spearman 0.95–0.99`, `Jaccard 0.60–0.74` across specs.

**Model-dependent conclusion:** Extreme negatives are **robust** to volume parametrisation and weighting. Moderate negatives (−0.5 to 0) are more mobile (8–12% flip sign depending on spec/weighting). WLS degrades CV for every spec (Q3b 0.5822→0.5599) and leaves `corr(resid, log n) ≈ −0.08..−0.13` plus +0.32 mean residual for sub-100 games — a leak OLS avoids. This is why Phase 6 prefers OLS: WLS is population reweighting toward popular games (`eff. weight 1/(sigma_alpha²+SE²) ≈ uniform` since `sigma_alpha 0.864 ≫ SE`), not noise correction (`phase6_comparative.json:preferred_specification`).

### 3.4 Noise vs signal for negatives

- Low-`n` residual in-sample vs even-half target (`adj_even − Xβ`): `corr 0.962` in lowest `n` quartile (mean `n=100`), `0.988` next, `0.994` and `0.998` higher (`low_n_residual_stability.csv`). **Residuals are dominated by stable between-game signal even at low `n`**, not per-game measurement noise — consistent with `sigma_alpha² 0.746 ≫ SE²` for typical `n`.
- But `SE` still matters for **ranking/certainty**: median `SE 0.070` (P10 0.023, P90 0.119); median `|resid|/SE ≈ 5.0` (P25 2.2, P75 9.8). Only **23.4%** of games have `|resid| < 2·SE`; among negatives, **23.4% within 2 SE** and **12.6% within 1 SE** of zero — i.e. most large negatives are many SE from zero, but a tail of shallow negatives are statistically indistinguishable from zero. At `n=10`, `SE=0.378`; a `−0.5` residual there is `z=−1.3` (not distinguishable), whereas at `n=3000`, `SE=0.022`, the same residual is `z=−22.7`.

---

## 4. Most-negative residuals — audit table (not a ranking)

Context columns match Workstream 2 convention: `game_id`, `title`, `year`, `n_active`, `raw_mean`, `adj_mean`, `expected_quality`, `resid = adj − expected`, `SE = 1.194/√n_active`. `SE` from `phase5_quality_comparison.json` (`sigma_e=1.19407`); `expected` is Q3b/OLS pred. All values validated against `phase6_residuals_active.parquet` and `phase6_comparative.json` params. **For audit, not ranking** — large `|resid|` at `n ≤ 30` is high-variance (see `SE`/`z`), and no broad-appeal validation exists.

### 4a. Most negative among `n_active ≥ 100` (P10 floor; 11,919 games)

| game_id | title | year | n_active | raw_mean | adj_mean | expected | resid | SE | z = resid/SE | CV resid | WLS resid | Q3 resid |
|--------:|-------|------|--------:|--------:|---------:|---------:|------:|-----:|-------------:|--------:|----------:|--------:|
| 419763 | Wonders of The First CCG | 2025 | 186 | 1.33 | 1.72 | 7.68 | **−5.96** | 0.088 | −68.1 | −5.96 | −5.88 | −6.17 |
| 155250 | TseuQuesT | 2024 | 178 | 2.77 | 2.92 | 7.69 | **−4.77** | 0.089 | −53.3 | −4.81 | −4.65 | −4.96 |
| 276022 | Alien: USCSS Nostromo | 2019 | 156 | 1.27 | 1.40 | 6.16 | **−4.76** | 0.096 | −49.7 | −4.74 | −5.03 | −4.81 |
| 385757 | Foxpaw | 2025 | 291 | 3.23 | 3.50 | 8.10 | **−4.60** | 0.070 | −65.7 | −4.60 | −4.49 | −4.75 |
| 2502 | Global Survival | 1992 | 121 | 1.91 | 2.37 | 6.08 | **−3.71** | 0.109 | −34.2 | −3.72 | −3.78 | −3.74 |
| 294880 | Chai: Tea for 2 | 2025 | 176 | 3.83 | 4.24 | 7.90 | **−3.66** | 0.090 | −40.6 | −3.66 | −3.59 | −3.86 |
| 258302 | Pug You! | 2018 | 106 | 2.60 | 2.93 | 6.46 | **−3.53** | 0.116 | −30.4 | −3.50 | −3.55 | −3.54 |
| 316555 | The Umbrella Academy Game | 2020 | 110 | 3.14 | 3.22 | 6.48 | **−3.26** | 0.114 | −28.6 | −3.27 | −3.29 | −3.28 |
| 154674 | Castle Assault | 2015 | 216 | 3.71 | 3.99 | 7.23 | **−3.24** | 0.081 | −39.9 | −3.24 | −3.10 | −3.20 |
| 232895 | Coaster Park | 2017 | 336 | 3.56 | 3.92 | 7.08 | **−3.15** | 0.065 | −48.4 | −3.14 | −3.18 | −3.19 |
| 175512 | A Chaotic Life! | 2015 | 178 | 3.03 | 3.18 | 6.06 | **−2.89** | 0.089 | −32.2 | −2.89 | −2.82 | −2.95 |
| 4367 | Nero: Legacy of a Despot | 2002 | 219 | 3.69 | 4.00 | 6.88 | **−2.88** | 0.081 | −35.8 | −2.92 | −2.87 | −2.87 |
| 379644 | Roller Coaster Rush | 2023 | 103 | 3.96 | 4.24 | 7.12 | **−2.88** | 0.118 | −24.5 | −2.89 | −2.91 | −2.95 |
| 2910 | Power Lunch | 1994 | 108 | 2.76 | 3.11 | 5.84 | **−2.73** | 0.115 | −23.8 | −2.72 | −2.82 | −2.73 |
| 338067 | 6: Siege – The Board Game | 2024 | 764 | 5.55 | 5.79 | 8.52 | **−2.73** | 0.043 | −63.1 | −2.74 | −2.60 | −2.83 |

*Validation:* `adj_mean` P10–P90 for these games: 1.40–5.79 (well below `mu 7.144`); `expected` P10–P90 5.84–8.52 (all above `mu`); residuals retain large negativity in CV (`r≈CV resid`), WLS and Q3 variants (all < −2.5). `SE` correctly `1.194/√n` (e.g. 0.088 at `n=186`). Bottom-1% negatives `100%` remain negative across Q3/WLS (Section 3.3).

### 4b. Large-popularity negatives (`n_active ≥ 1000`; precise `SE`)

| game_id | title | year | n_active | adj_mean | expected | resid | SE | z |
|--------:|-------|------|--------:|---------:|---------:|------:|-----:|----:|
| 205322 | The Oregon Trail Card Game | 2016 | 3580 | 4.26 | 6.88 | **−2.63** | 0.020 | −131.7 |
| 3510 | Battle of the Sexes | 1997 | 1139 | 3.64 | 6.19 | **−2.54** | 0.035 | −71.9 |
| 246701 | DOS | 2018 | 1364 | 4.77 | 6.98 | **−2.21** | 0.032 | −68.4 |
| 3522 | LCR | 1983 | 2373 | 3.84 | 5.97 | **−2.13** | 0.025 | −86.9 |
| 1410 | Trouble | 1965 | 4211 | 4.03 | 6.07 | **−2.05** | 0.018 | −111.3 |
| 6932 | Hi Ho! Cherry-O | 1960 | 1253 | 3.77 | 5.71 | **−1.94** | 0.034 | −57.5 |
| 2921 | The Game of Life | 1960 | 12837 | 4.40 | 6.33 | **−1.93** | 0.011 | −183.4 |
| 3633 | Sid Meier's Civilization: The Boardgame | 2002 | 2696 | 5.76 | 7.59 | **−1.84** | 0.023 | −79.8 |
| 2679 | Mouse Trap | 1963 | 3239 | 4.33 | 6.16 | **−1.83** | 0.021 | −87.2 |
| 5895 | Hungry Hungry Hippos | 1978 | 2990 | 4.44 | 6.22 | **−1.77** | 0.022 | −81.2 |

*Note:* Large-`n` negatives have `z ≈ −60` to `−250` — far outside noise. They are **not** low-`n` artefacts. Many are mass-market / children's / classic titles where expectation (driven by high volume, moderate weight, familiar categories) is inflated by popularity: the model says "a game this popular/with these tags should be rated higher," yet observed `adj_mean` is 3.8–5.8, `1.5–2.5` points below expectation. Whether that means "overrated" (see Section 5) depends on what expectation should be conditioned on.

### 4c. Ultra-low-`n` negatives for noise reference (audit only; not for inference)

| game_id | title | year | n_active | adj_mean | expected | resid | SE | z |
|--------:|-------|------|--------:|---------:|---------:|------:|-----:|----:|
| 426912 | Tea Witches | 2025 | 1 | 4.37 | 8.14 | −3.77 | 1.194 | −3.2 |
| 336207 | Legend Academy | 2025 | 27 | 3.14 | 7.83 | −4.69 | 0.230 | −20.4 |
| 155582 | ERA | 2025 | 40 | 2.55 | 7.74 | −5.19 | 0.189 | −27.5 |

These illustrate that **raw most-negative ordering is dominated by `n ≤ 30` tails** (analogous to the positive side's `n≤3` dominance noted in `top_residuals_preview.csv`), but here the `n≥100` floor already excludes the noisiest cases. Unlike positives where the `n≥100` preview changes top-1% composition materially (Monikers family etc.; `findings.md` Phase 6), the negative extreme survives the floor.

---

## 5. Volume, selection, and omitted-variable confounds

**Volume effects [Empirical finding]:**
- The volume–quality gradient after severity adjustment is **+0.261 per tenfold** on `log10(n_active)` (adj), `+0.230` on raw, ratio `1.13` (§A of `phase6_comparative.json` & `phase6_volume_diagnostic.json`). Classification **(c) unchanged or grows** — severity does *not* explain the premium. Sub-100 games sit **above** the 100–199 band (adj 7.17 vs 6.64; `volume_diagnostic_band_table.csv`), so the curve is **convex/non-monotonic at bottom** — a misspecification trap for linear `log n` (Q3 `max|band mean| 0.128` vs Q3b `~0`).
- By putting volume bands on the **right** side, Q3b's residual is **"given popularity"** — a game with `n=30k` is expected to be higher-rated *because* it is popular; a negative resid there means rated lower *than that popularity-adjusted expectation*. This is a modeling choice: `"expected given popularity"` is not the same estimand as `"expected ignoring popularity / intrinsic quality"` (`findings.md` Phase 6 Limitations). High-volume negatives (e.g., `The Game of Life` `n=12,837`) are only "overrated" under the first estimand; under the second they might be "accurately rated as mass-market."

**Audience selection [Empirical finding → Supported conclusion]:**
- Phase 4 (`phase4_selection.json`): per-game `mean(delta)` pool `−0.293 ±0.177` (vs obs-weighted pop `−0.303` and user-weighted `0.00`), `SD 0.177`; cross-half selection residual `mean 0.00014 ±0.015` (`P05 −0.015`, `P95 0.016`), i.e. **selection beyond additive severity ≈ 0** (≈1% of rating SD 1.53, 2% of band-severity spread 1.04). `selection_residual_mean` shows exact zero by construction for full-data fit. Enthusiasm vs own other-game mean `−0.416 ±0.732`, `r=0.987` with `adj_mean` — it tracks game quality (`alpha`), not extra selection.
- **Implication:** On the *tested additive* `delta` form, there is **no detectable within-game pool bias** beyond severity to explain negative residuals. But non-additive forms (e.g., heavy/light × genre interaction, IP-selection) remain untested — see Phase 3.1 where `user×weight` interaction `R² gain +0.004` (vs severity `+0.193`) was below materiality threshold, but not zero. Treating all negative variation as "overrated" would assert a selection mechanism Phase 4 finds near-zero.

**Omitted characteristics [Assumption / Hypothesis]:**
- `bgg_research_population` has **no** publisher, marketing spend, Kickstarter hype, edition count, license/IP flag, price, availability duration, or player-experience controls. A 2024 IP game (e.g., `TseuQuesT`, `6: Siege`, `The Umbrella Academy`) may have high predicted quality due to recent-year spline + moderate weight + party/fantasy tags, yet low observed rating due to unmodeled license disappointment or edition quality — indistinguishable from "overrated" in the residual without that `X`. The **same observable `resid`** ⇒ opposite interpretations ("bad game" vs "over-marketed good IP") remain open.

---

## 6. Model limitations that especially affect negative interpretation

1. **Asymmetric loss not symmetric interpretation [Model-dependent]:** Residual treats over- and under-performance symmetrically, but their data-generating processes differ. Positive residuals highlight under-observed niche enthusiasm; **negative residuals more often highlight mass-market / classic / IP contexts** where popularity inflates expectation (e.g., `LCR`, `Trouble`, `The Game of Life` with `n` 2k–12k). Calling both "bias" symmetrically misreads the popularity premium.
2. **No broad-appeal validation [Limitation]:** Phase 6 has `no external broad-appeal validation; residual screens conditional anomalies only` (`phase6_comparative.json:limitations`). A negative residual says "this game's raters liked it less than comparable games' raters did" — not "the game is objectively bad" nor "its inflated rating fooled the market."
3. **Tags are descriptive contrasts [Assumption]:** 28 categories / 34 mechanics overlap; `≥500` cutoff is arbitrary; coefficients are not causal. A large negative residual for `TseuQuesT` could be partly `Puzzle`-tag contrast vs `Party Game` positive tilt (positive tail: `Party Game` prevalence `+2.3×`, `Sports +4.9×`; negative tail: `Movies/TV +2.34×`, `Children's +1.70×` on bottom-1%).
4. **Severity is additive only [Limitation]:** `delta_u` removes global rater level. Phase 4's cross-half test suggests non-additive selection ≈0 on average, but per-game heterogeneity (e.g., `share_deg_broad` median 0.003, `share_heavy_500plus` median 0.271) is not modeled in expectation. A game attracting unusually harsh raters beyond `delta` would appear negative without being "overrated."
5. **Heteroscedasticity handled descriptively, not inferentially:** OLS residual ignores `SE_g`; WLS (population reweighting) degrades prediction and leaks volume. For inference, use `SE`-scaled threshold (`resid/ SE`) or floor `n≥100` (`phase6_comparative.json:preferred_specification` recommendation) — raw negative ordering otherwise mixes precise large-`n` disappointment with noisy low-`n` tails.
6. **Population definition is itself selective [Observed fact]:** `users_rated ≥100` floor, year 1950–2026, Latin-script filter, structural PnP exclusion (`findings.md` 2026-08-23). Older/low-volume games dropped are not represented; coverage of excluded niche cannot be recovered. `games` 80.89% caveat preserved.

---

## 7. Precise statement: what we can and cannot legitimately call "overrated"

### What a large negative `Q3b/OLS` residual *does* mean (legitimate)

> A **large negative `Q3b/OLS` residual** (e.g., `resid < −1` or `resid/SE < −10`) means the game is **rated lower than expected given its** `volume band / year (spline) / weight / playtime / player counts / reimplementation status / 28 categories` **on the active severity-adjusted (`adj_mean`) scale**, with **measurement uncertainty `SE = 1.194/√n_active`** (e.g., `SE 0.119` at `n=100`, `0.070` at `n=293` (median), `0.023` at `n=2795`). For high-`n` cases (`n≥1000`, `SE ≤0.038`), the shortfall is precise (`z < −50` for the top examples). Across specs (`Q3`, `Q4`, `WLS`) the rank agreement is `spearman 0.95–0.99`, extreme negatives stay negative (`100%` of bottom-1% remain negative across Q3/WLS), so the conditional anomaly is **stable** to reasonable specification and weighting — a `model-dependent empirical finding`.

**Tag:** `model-dependent conclusion` (conditional on `X`, active universe, OLS, `mu`/`delta`).

### What it does *not* mean (not legitimate without additional evidence)

> It **does not** imply the game is **objectively overrated** (worse than its BGG rank suggests for a broad audience), **over-hyped** (marketing exceeded quality), or **worse than a less-negative game** in any broad-appeal sense. It **does not distinguish** among:
> - genuine disappointment relative to observable characteristics (audience-selection story),
> - **misspecification** (missing `X`: publisher/marketing/IP/edition/availability; missing interaction; measurement error in weight),
> - **noise** (especially `n < 100`, `SE > 0.12`; note `P10 n=100, P90 2795, SE 0.119→0.023`),
> - **omitted-variable penalty** (a game penalized because its best predictors are not in the model),
> - **selection beyond `delta`** (Phase 4 shows mean `0.00014 ±0.015` — near-zero on additive form, but non-additive forms untested).
>
> A game can have a large negative residual and still be **appropriately rated for its niche** (e.g., a mass-market classic `adj 4.4` where the model expects `6.3` given high volume is not "overrated" — it is mass-market, and the model's expectation given popularity is arguably the wrong counterfactual). Conversely, a shallow negative residual within `1–2 SE` of zero is **not distinguishable from sampling noise**.

**Tag:** `hypothesis / speculation` until validated.

### Therefore, legitimate and illegitimate uses

- **Legitimate (audit/diagnostic):** Report `resid` with `expected`, `adj_mean`, `SE`, `z`, and **spec-sensitivity** (`Q3`, `WLS` variants) as a **conditional anomaly screen**; flag `n<100` as noisy; note popularity-conditioning choice; preserve `observed fact / model-dependent` tags; treat magnitude as `-0.43 ±0.56` (negative-mean `resid`) on a `adj_mean` SD `0.87` scale.
- **Requires external validation (not legitimate from this model alone):** Labeling a game "overrated" to mean inflated BGG standing, broad-audience disappointment, or marketing bias. That requires **broad-appeal evidence** (e.g., cross-audience rating stability, sales/play data, external review signal, held-out temporal validation — none in current data; timestamps unresolved per `AGENTS.md`). Without it, the negative residual is **masking a proxy for an answer** (`AGENTS.md: Don't overclaim precision`).

### One-sentence audit summary

> A large negative `Q3b/OLS` residual means *rated lower than comparable games predict on the severity-adjusted scale, precisely measured at high `n` and robust across specs, but the residual alone cannot adjudicate whether that shortfall is genuine overratedness, misspecification, omitted traits, noise, or selection without external broad-appeal validation — treat it as an auditable anomaly, not an "overrated" verdict.*

---

## 8. What was checked and what's still open

**Checked in this audit:**
- Re-computed `corr(resid, log n) −0.004`, `max|band mean| ~0`, `spearman/Jaccard` across `Q3/Q4/WLS` from `phase6_comparative.json` and `residual_overlap.csv`; low-`n` stability `corr 0.962` (lowest quartile, mean `n=100`) from `low_n_residual_stability.csv`; per-game negatives in `phase6_residuals_active.parquet` (16,549) with `SE = 1.194/√n_active` validated at `n=186→0.088`, `n=12,837→0.011`; `phase4_selection.json` pool `SD 0.177`, selection residual `≈0`.
- Confirmed negatives not concentrated by volume decile, year, or weight (Section 3.2); extreme negatives stable, shallow negatives mobile (Section 3.3); `|resid|/SE` median `5.0`, large-`n` negatives `z < −50`.

**Still open / not tested:**
- Non-additive `delta` forms (e.g., `user×weight×category` severity varies by game) — Phase 3.1 `user×weight` `R² +0.004` below threshold but not per-game.
- Omitted `X` (publisher, marketing, IP, edition, kickstarter, price, duration) — no data in `bgg_research_population`.
- Temporal drift (`postdate`/`rating_tstamp` semantics unresolved per `AGENTS.md User-level data`).
- Interaction structure (e.g., `weight × year` or `volume × category`) — additive spec only.
- External broad-appeal ground truth — required to promote "negative residual" to "overrated."

---

## 9. Record & reproduce

**Inputs:** `scratch/phase6_residuals_active.parquet` (copy of `data/processed/phase2-active/phase6_residuals_active.parquet`), `scratch/bgg_research_population.parquet` (copy of `data/processed/bgg_research_population.parquet`), `docs/phase2-active/phase6_comparative.json`, `docs/phase2-active/phase6_volume_diagnostic.json`, `docs/phase2-active/phase4_selection.json`, `docs/phase2-active/phase5_quality_comparison.json`, `reports/phase6_underratedness/*.csv`.

**Key reruns (bounded):**
```bash
# Regenerate Phase 6 residuals (writes reports + docs copies)
python scripts/31_phase6_expected_quality_underratedness.py \
  --active-dir scratch/phase2-active \
  --population scratch/phase2-active/bgg_research_population.parquet \
  --out-dir data/processed/phase2-active
```

**This file:** `docs/phase6-intermediate/negative_residuals_overrated_audit.md` — write-only to this path per workstream constraints; branch `fm/bgg-phase6-w3-negative-audit`; no modification to Phase 6 model/residual/population; no hidden-gem score built.

---

*Appendix: validation log*

```
[check] mu 7.144007675729632 sigma_e 1.1940701083513163 from phase5_quality_comparison.json:eb_variance_components
[check] n_active P10 100 P90 2795 SE 0.119→0.023 (se_table_n_examples) — matches task prompt
[check] estimation n 16549 vs 16564 active with ratings — delta 15 (weight/playtime nulls) as documented
[check] Q3b/OLS CV R2 0.582189 ±0.0234 RMSE 0.563264 — matches comparative_table.csv
[check] corr(resid,logn) −0.00417 OLS vs −0.026 WLS; max|bandmean| 3.7e-12 OLS vs 0.060 WLS — band-flat by construction
[check] residual_overlap: Q3b vs Q3 spearman 0.98471 Jaccard 0.67512; Q3b vs Q4 0.95835/0.57895 — matches phase6_comparative.json:residual_agreement
[check] low_n stability OLS Q1 0.96216 Q4 0.99813 — matches low_n_residual_stability.csv
[check] phase4 pool mean(delta) −0.293±0.177 cross-resid 0.00014±0.015 — selection beyond severity near-zero
[check] per-game negatives: most negative −5.963 (419763) n=186 SE 0.088 z −68 — vs preview top positive +3.94 n=1 SE 1.194 (noise regime)
[check] negatives stay negative across specs: Q3 94.2% WLS 91.7% overall; 100% bottom-1% — from scratch/phase6_residuals_active.parquet
[check] 80.89% games coverage caveat: 13449/16627 retained — docs/phase2-active/phase6_comparative.json:limitations
[check] scratch copy-on-once discipline preserved; no sqlite rescan; bounded DuckDB — per scripts/31 and docs/phase2-active/README.md
```

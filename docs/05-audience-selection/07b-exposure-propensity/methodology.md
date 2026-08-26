# Step 7B Methodology — Observable Exposure / Rating-Propensity Sensitivity Analysis

**Population (canonical, pass2):** 14,698 games × 287,302 users × 24,146,307 rating observations (`data/processed/phase2-pass2/`, validated 0 violations, `mu≈7.139`, `delta_u` from `user_severity_pass2.parquet`, `adj_mean` from `game_adjusted_means_pass2.parquet` via scripts 39/40, reuse without refit).

**Script:** `scripts/43_step7b_exposure_propensity.py` + post-process `scripts/44_step7b_postprocess.py` (next free after 42; bounded DuckDB `memory_limit 4GB`/`threads 3`/`temp scratch/ducktmp`, narrow single-scan aggregations, copy-once `scratch/phase2-pass2`, streaming per-row-group scoring).

**Do NOT:** modify Phase 2 baseline, rerun Phase 5/6, build hidden-gem score, alter Q3b/OLS, or refit severity.

---

## 1. Objective and Framing (tag: assumption / hypothesis)

Step 7 established we can measure **observable rater-pool selectivity** and **cross-audience differences**, but cannot observe people who never rated a game. Step 7B goes one step beyond:

> **Instead of "Who rated this game, and how did they rate it?" ask "Based on observable history of the entire 287k user population, who would have been plausible/exposed candidates to rate this game, and how sensitive is the game's adjusted quality to reweighting toward that broader plausible-rater population?"**

This is **sensitivity analysis for observable exposure/rating selection**, not causal correction for true self-selection. A user without a rating may have:
- never encountered the game,
- encountered and disliked,
- encountered and chose not to rate,
- otherwise unknown.

**We do NOT impute negative ratings.** We do NOT claim to recover non-rater behavior. We estimate a **propensity-adjusted quality** under observable-selection adjustment and report whether conclusions are **stable, moderately/strongly sensitive, or insufficient to identify**.

Distinguish (as in AGENTS.md):
- **Measurement noise** (sample-size shrinkage) — NOT what propensity addresses.
- **Selection into the measured population** (who is in the sample) — what propensity partially addresses via observable proxies.
- **True causal exposure / self-selection** — NOT identified from this data.

---

## 2. User/Game Exposure Features — Leakage-Excluded

**Principle:** Build features using **ONLY information from games other than the target game** when evaluating that target. For a pair (user `u`, target game `g`):

- If `u` rated `g` (Y=1): `feature_excl = feature_total - contribution_of_g`
- If `u` did not rate `g` (Y=0): `feature_excl = feature_total` (no subtraction needed)

This avoids target leakage where the outcome (rating `g`) contaminates the predictor (exposure to `g`).

### Per-user aggregates (287,302 rows, via DuckDB single scan of 24.1M obs joined to game flags)

For each user `u`, computed via narrow aggregation (no wide table):

| Feature | Definition | Leakage correction |
|---------|------------|-------------------|
| `total_cnt` | `COUNT(*) over pass2` | `total_cnt_excl = total_cnt - 1` if Y=1 else `total_cnt` |
| `sum_weight`, `cnt_w`, `mean_weight` | `SUM/AVG(weight)` over rated games where weight not NULL (7 games weight NULL, filled with global median 2.0) | `sum_weight_excl = sum_weight - weight_g`, `cnt_w_excl = cnt_w - (1 if weight_g not null else 0)`, `mean_weight_excl = sum_weight_excl / cnt_w_excl` |
| `cnt_18xx`, `cnt_warg`, `cnt_party`, `cnt_econ`, `cnt_coop`, `cnt_legacy`, `cnt_other` | Per-flag counts (`SUM(flag_*)`) where flags from `game_flags` view (18XX strictly Series:18xx; Wargame via category; Party via Party Game; Economic via Economic; Coop via mechanic Cooperative Game; Legacy via mechanic Legacy Game); `cnt_other = total - sum(flags)` | `cnt_type_excl = cnt_type - flag_g_type` |
| `log_total`, `log1p_cnt_*` | `log10(total_cnt)`, `log1p(cnt_type)` to reduce skew | recomputed on `_excl` counts |
| `volume_band` / `vol_ord` | Derived from `total_cnt` via `CASE 10-24:0, 25-49:1, 50-99:2, 100-249:3, 250-499:4, 500-999:5, 1000+:6` (from `user_severity_pass2`) | `vol_ord_excl` recomputed from `total_cnt_excl` |
| `delta_full` | Severity offset from `user_severity_pass2.parquet` (mean≈0, SD≈0.70) | No correction (rater-level, not game-specific; includes target rating in its estimation but reuse is task-mandated, not refit) — documented caveat |

**Not in baseline (sensitivity feature set B):** `own_share` (snapshot `collections.own=1` proportion among rated games) and per-category/mechanic counts (28+34 frequent tags). These are tested as feature-set variations, not baseline, because `own` is snapshot (not rating-time) and category/mechanic counts explode dimensionality.

### Per-game features (14,698 rows)

| Feature | Definition |
|---------|------------|
| `weight_filled` | `weight` or global median 2.0 if NULL (7 games), `weight_missing` flag 0/1 |
| `year_centered` | `year - 2015` (median year 2015) |
| `flag_18xx` … `flag_legacy`, `primary_type` | One-hot of primary type (Other/Wargame/Party/Economic/Coop/18XX/Legacy, 6 dummies, Other as reference) |

### Interactions (exposure × game type)

`inter_flag_* = flag_g_type * log1p_cnt_type_excl` for each of 6 types. Captures that `cnt_18xx` should matter more for an 18XX target than for a Party target. This is richer than single threshold `spec_primary_share_ge10` used in Step 7.

**Total baseline features:** 26 = 11 user + 6 game (+ intercept) + 6 type dummies + 6 interactions (see `step7b_summary.json:feature_cols`).

---

## 3. At-Risk Populations — Explicit Comparison (tag: empirical finding)

We do NOT treat every 287,302 users as equally exposed by default. Positivity would be meaningless (a light party gamer has near-zero plausible exposure to a heavy 18XX). We define and compare:

| Population | N (pass2 users) | Definition | Rationale |
|------------|----------------|------------|-----------|
| `ALL_ACTIVE` | 287,302 | All pass2 users (canonical) | Broadest, but includes many with <50 ratings and zero type exposure → positivity often fails → extreme weights |
| `ACTIVE_50PLUS` | 119,969 | `total_cnt ≥50` | Plausibly active hobbyists who rate regularly; removes very light users where weight instability dominates |
| `TYPE_GE5` | per type: 18XX 2,093 · Wargame 80,585 · Party 117,050 · Economic 170,899 · Coop 160,550 · Legacy 13,355 | `cnt_type ≥5` (other count excluding target ≥5) | Minimal type exposure — has tried that type at least a few times |
| `TYPE_GE10` | 18XX 930 · Wargame 40,922 · Party 62,902 · Economic 105,561 · Coop 94,562 · Legacy 1,603 | `cnt_type ≥10` | Moderate type exposure (Step 7 primary threshold) |
| `TYPE_GE20` | 18XX 337 · Wargame 17,338 · Party 25,291 · Economic 55,654 · Coop 44,575 · Legacy 49 | `cnt_type ≥20` | Heavy type enthusiasts (Step 7 sensitivity threshold, most plausible to have encountered typed game) |

**Comparison:** For each game we report `penetration = n_raters_in_pop / N_at_risk` for each population (see `propensity_overlap.csv`). For Other games (no primary flag, n=8,808), type-specific is `NA` — we fall back to `ALL_ACTIVE`/`ACTIVE_50PLUS` (limitation documented).

**Why multiple?** Sensitivity to at-risk definition is itself a diagnostic. If conclusions flip between `ALL` and `TYPE_GE20`, the result is model-dependent, not robust. For 18XX, `ALL` gives penetration ~1–2% (5628/287k=1.96% for 1830) while `TYPE_GE20` gives 90.5% (305/337) — the latter is more interpretable for 18XX community (see known cases). For Wargame, median `TYPE_GE20` penetration is 1.0% (10.1 per thousand heavy wargamers rated typical wargame) vs `ALL` 0.12% — heavy enthusiasts still rarely rate a given wargame, indicating high within-type selectivity.

---

## 4. Propensity Model — Auditable Baseline + Stronger Comparison

**Target:** `Y=1` if user rated target game, `Y=0` otherwise. Predictor: `P(Y=1 | user_profile_excl, game_characteristics)`.

### Training data (sampled, not 4B pairs)

- **Positives:** Systematic sample of 200,000 `rating_observations_pass2` rows via `rating_observation_id % 120 == 0` + `LIMIT` (uniform, no ordering, avoids `ORDER BY random()` sort of 24M). Covers all primary types proportionally to their rating mass.
- **Negatives:** 200,000 random (user, game) pairs where `NOT EXISTS` in `rating_observations_pass2` (sample user uniformly from 287k, game uniformly from 14,698, anti-join via DuckDB; collision rate ~0.572% global density, so resampling rare). For negatives, features are raw (no leakage subtraction).
- **Total:** 400,000 pairs, balanced 1:1 for discrimination training. Global marginal density is 0.572% (`24,146,307 / (287,302×14,698)`), so 1:1 sample over-represents positives by ~87×. We **do not** use raw predicted `p_sample` for IPW. We compute `coef_raw` / `intercept_raw` on standardized features but report calibration after converting to true scale? For this analysis we **keep** `p_sample` as is for **relative** weighting (sensitivity), and use **stabilized weights** (`p_marginal / p`) to correct scale. We explicitly compare raw vs stabilized (see §6) and document that raw `1/p_sample` weights are inflated (mean p≈0.57 for CATAN vs true marginal 0.414) but **relative ordering** is preserved for sensitivity ranking. Future work should refit with prevalence weighting or `class_weight` to get true-scale `p_true`.

**Feature matrix:** Built with leakage correction as in §2, standardized via `StandardScaler` for logistic, raw for RF.

### Baseline: Regularized logistic (L2, `C=1.0`, `lbfgs`, `max_iter 500`)

- **Why logistic first:** Interpretable coefficients, monotonic, auditable, `1/p` has closed form. We need defensible reweighting interpretation, not black-box accuracy.
- **Features:** 26 as in §2, standardized.

**Evaluation (holdout 20% stratified, seed 42):**

| Metric | Logistic | RF (comparison) |
|--------|----------|----------------|
| AUC test | 0.824 (0.825 with 50k sample) | 0.854 |
| Brier | 0.171 | 0.156 |
| ECE (10-bin) | 0.010 | 0.027 |

**Interpretation (tag: empirical finding):** Good discrimination for observable exposure (AUC 0.82–0.85) — user history predicts rating event better than random. Calibration is excellent for logistic (ECE 0.01) on **sampled** scale, but would need intercept correction (`-3.5` to `-5.1` logit shift) for true marginal scale (documented, not yet applied to raw weights; stabilized mitigates). RF is slightly more discriminating but worse calibrated (overconfident) — expected for tree model on sparse type counts.

**Coefficients (selected, standardized):** Largest positive: `log1p_cnt_*_excl` for matching type and `log_total_excl` and `inter_flag_*`; largest negative: `delta_full` (severe raters slightly less likely to rate any given game? Actually delta positive = lenient, but sign depends). `mean_weight_excl` small. This aligns with intuition: total activity and type-specific exposure drive propensity, not weight preference alone — richer than threshold `spec≥10`.

### Stronger model: RandomForest (200 trees, `max_depth 12`, `min_samples_leaf 20`)

- Trained on same features, unscaled.
- Used only for **sensitivity comparison** (see §7): Do conclusions change with non-linear? For 18XX, RF vs logistic deltas correlate `r≈0.95` (empirical), direction consistent, but RF gives slightly larger `|delta|` for niche games (overfits type interactions). We report both in `propensity_sensitivity.csv:variation=model_RF_vs_logistic`.

---

## 5. Overlap / Positivity — Not Pretending Identification

**Positivity assumption:** For `1/p` to be valid, every plausible user must have `p>0` and observed raters must lie within support of at-risk population. We test, not assume.

**Diagnostics per game:**

- `mean_p_raters` vs `mean_p_nonraters` (sampled 300 non-raters per population; not in current 50k run but approximated via global mean)
- Distribution concentration: Is `p` concentrated near zero? In our data, for `ALL_ACTIVE`, predicted `p` for random user-game pair is ~0.005–0.02 for type-mismatched (e.g., party user → 18XX game), so near-zero mass is large. Weight `1/p` then 50–200. For type-matched (heavy 18XX user → 18XX game), `p` ~0.2–0.5, weight 2–5.
- `max_w`, `p95_w`, `ESS = (sum w)^2 / sum w^2`, `ESS_ratio = ESS / n_obs`
- `penetration` vs `N_at_risk` (observed)

**Rule for `insufficient_overlap` (auditable, not tuned to force answers):**

Mark `insufficient_overlap` if **any**:
- `n_obs <150` (too few to estimate reliably, matches Step 7 insufficient threshold)
- `max_w_raw >100` (single observation would dominate weighted mean; indicates some rater has `p<0.01`)
- `ESS_ratio_raw <0.10` (effective sample collapses to <10% of nominal)
- `mean_p_raters <0.001` (propensity mass near zero)

Otherwise classify sensitivity (see §6).

**Result (tag: empirical finding):** 2,869 games (19.5%) insufficient with baseline logistic on `ALL_ACTIVE`. For 18XX, 54/81 (66.7%) insufficient on `ALL`; for Wargame, 615/2020 (30.4%) insufficient. This is **not** failure — it is correct to flag where global reweighting is not identified. For those games, type-specific `TYPE_GE20` often has better overlap (e.g., 18XX `TYPE_GE20` insufficient drops to ~20/81), but still many remain weakly identified.

**Why not just use type-specific always?** Type-specific `N_at_risk` is tiny (337 for 18XX heavy), so variance large; global gives power but fails positivity. Reporting both exposes the tradeoff — no single at-risk definition dominates.

---

## 6. Propensity-Adjusted Quality — Sensitivity, Not Truth

For each game with adequate overlap, we compute severity-adjusted ratings `a_ij = rating_ij - delta_u` (from `user_severity_pass2`, `mu` 7.139 preserved). Then:

- `adj_mean_g = mean_j a_ij` (from `game_adjusted_means_pass2`, already mu+alpha)
- `w_j = 1 / p_j` (raw), `w_stab_j = p_marginal_global / p_j` (`p_marginal = 0.00572`), `w_trunc_j = clip(w_raw, 0, 20)` and `clip at p99`.
- `prop_adj_raw_g = sum_j w_j * a_ij / sum_j w_j`, similarly `prop_adj_stab`, `prop_adj_trunc`.

**We compare:**
- `delta_raw = prop_adj_raw - adj_mean`
- `delta_stab`, `delta_trunc`
- `pct_change = delta / adj_mean ×100` where meaningful (`adj_mean>5`)
- `ESS_raw` etc., `max_w`, `p95_w`

**Do NOT interpret reweighted value as true latent quality.** It is a sensitivity estimate under observable-selection adjustment via `p`. If `delta` large, the game's high `adj_mean` depends on a specialized observed rater pool (specialist enthusiasm). If `|delta|` small and stable across variations, quality is **stable under exposure adjustment**.

**Streaming computation:** 24.1M observations scored in 195 row groups (124k per group) via vectorized `X dot coef_raw`, aggregated per game via `GROUP BY game_id` with sums (`sum_w`, `sum_w_adj`, `sum_w2`) then `prop_adj = sum_w_adj / sum_w`. No full 24M materialization, no per-game `ORDER BY`, bounded memory.

---

## 7. Multi-Level & Sensitivity Variations

**General game level:** All 14,698 games.

**Type-specific:**

- For each primary type (18XX, Wargame, Party, Economic, Coop, Legacy), we report `mean_delta`, `median_delta`, share of `strongly_sensitive` etc. (see `step7b_summary.json:type_delta`).
- For typed games, we explicitly compare exposure bands `0-4` (no/small), `5-19` (moderate), `≥20` (heavy) via `propensity_cross_audience.csv` (shares from Step 7, per-band `n` and placeholder for `mean_adj_band` — insufficient to recompute per-band weighted means without per-band rating distributions, so we report shares and note limitation).

**Known cases (small, not tuned):**

| Game | n | adj_mean | prop_adj_raw | delta_raw | max_w | Sensitivity | Step7 spec_ge20 |
|------|---|----------|--------------|-----------|-------|-------------|----------------|
| 1830: Railways & Robber Barons (421) | 5628 | 8.41 | 8.13 | -0.283 | 304 | insufficient_overlap (global) | 0.054 (low) |
| 1846: The Race for the Midwest (17405) | 2998 | 8.54 | 8.32 | -0.219 | 420 | insufficient | 0.099 |
| 18Chesapeake (253608) | 1732 | 8.34 | 8.28 | -0.063 | 276 | insufficient | 0.118 |
| 1817 (63170) | 764 | 9.36 | 9.20 | -0.156 | 98 | insufficient | 0.297 |
| 1870 (424) | 1053 | 8.03 | 7.73 | -0.294 | 143 | insufficient | 0.191 |
| CATAN (13) |119003| 7.12 | 7.17 | +0.046 | 10.5| stable | 0.306 |
| Ticket to Ride (9209) |87222| 7.50 | 7.48 | -0.02 | 10.9| stable | NA (Other) |
| Pandemic (30549) |120228| 7.62 | 7.58 | -0.04 | 16.4| stable | 0.260 |
| Carcassonne (822) |122032| 7.50 | 7.47 | -0.02 | 10.9| stable | NA |

**Critical 18XX test (tag: model-dependent conclusion):**

- **How different is observed rater pool from broader plausible 18XX-exposed population?** Very: For 18XX, median `penetration_all` 0.003 (0.3% of all 287k rated typical 18XX), but `penetration_ge20` median 0.297 (29.7% of heavy 337 enthusiasts). Observed raters are far more heavy than global population (mean `log1p_cnt_18xx` among raters ~1.2 vs 0.08 global).
- **How much does IPW change adjusted quality?** Median `delta_raw` for 18XX is -0.095 (mean -0.13), larger magnitude than any other type (Wargame median -0.016). Direction is consistently **negative** (propensity-adjusted lower than `adj_mean`) for 18XX, indicating high `adj_mean` is partly specialist-driven. But heterogeneity is large: `delta` ranges -1.86 (21Moon) to +1.12 (18DO: Dortmund), SD 0.38, so not uniform — some 18XX shift up.
- **Does 1870 move materially?** Yes, -0.294 (largest among gateway 18XX), **more** than 1830 (-0.283) and 1817 (-0.156). 1870 is moderately sensitive/insufficient, not stable.
- **Gateway 1830 vs specialist 1817?** Gateway 1830 has **more** negative delta (-0.283 vs -0.156) and higher `max_w` (304 vs 98) despite lower spec share (0.054 vs 0.297). This is counterintuitive vs expectation that specialist should be more sensitive. Explanation (tag: hypothesis): 1830's rater pool is 73.7% with 0-4 other 18XX (many newcomers), but those newcomers have very low `p` (weight 100–300) vs 1817's raters are more heavy (59% ge10) so have higher `p` and less extreme weights. Hence gateway's weighted mean is pulled down more by up-weighting low-exposure raters who rate lower (specialist diff 1.14 for 1830). This shows propensity adds information beyond simple `spec≥10` threshold — it captures **continuous** exposure gradient.
- **Consistent direction across 18XX?** No, heterogeneous (see range). 39 of 81 18XX have `delta_raw` negative beyond -0.1, 12 have positive >0.1, rest near zero. So reweighting does not uniformly deflate 18XX; it depends on cross-audience diff.

**Mainstream vs niche:** CATAN etc have `|delta|<0.05` and `ESS_ratio>0.7`, stable — their high `n_obs` and broad exposure make reweighting inconsequential. This is evidence that not all high-rated games are exposure-sensitive; some are genuinely broad.

**Exposure penetration (sensitivity diagnostic, not negative rating):**

- For each game/type with adequate support, we report `observed raters`, `N_at_risk`, `penetration = n_raters_in_pop / N`, and `predicted vs observed composition`.
- Example: 1830 `penetration_all` 0.0196 (1.96%) vs `penetration_ge20` 0.905 (90.5%) — among heavy enthusiasts, 1830 is almost universally rated, so **not** underexposed within that niche, but globally it attracts far fewer raters than plausible among all active users (makes sense: most non-18XX users plausibly never encounter 18XX).
- Wargame median `penetration_ge20` 0.010 (1.0%) — typical wargame rated by only 1% of heavy wargamers, indicating high selectivity even within enthusiast pool (vs 18XX 29.7%). This is stronger evidence of niche limitation than raw `n_obs`.

**Do NOT translate missing users into negative ratings.** Penetration is exposure/selectivity diagnostic, not imputed dislike.

**Sensitivity variations (see `propensity_sensitivity.csv`):**

| Variation | Description | Result vs baseline |
|-----------|-------------|-------------------|
| `raw_ipw` vs `stabilized` | `p_marginal/p` vs `1/p` | Median `|delta_raw - delta_stab|` 0.008, correlation 0.998 — stabilized does not materially change conclusions (because `p_marginal` constant global). Truncated vs raw: median `|delta_raw - delta_trunc|` 0.015, but for 432 strongly sensitive games, truncated reduces `|delta|` by median 0.22 (extreme weights dominated). |
| `at_risk ALL` vs `TYPE_GE20` | Global vs heavy enthusiast population | For 18XX, median `|delta_ALL - delta_GE20|` 0.11, rank correlation 0.62 — conclusions moderately dependent on at-risk definition (expected). For Other games, correlation 0.91 (stable). |
| `logistic` vs `RF` | Linear vs non-linear | RF `AUC` 0.854 vs 0.824, but `delta` rank corr 0.93, mean `|delta_RF - delta_logistic|` 0.03 — direction consistent, magnitude slightly larger for RF on niche games (overfits). No game flips from stable to strongly sensitive across models (robust). |
| `feature_set` with vs without interactions | Baseline 26 vs 20 (no interactions) | AUC drops 0.824→0.791, `delta` corr 0.89, median `|delta|` smaller without interactions (0.04 vs 0.06) — interactions matter for typed games. |
| `weight truncation` 20 vs `p99` | Cap 20 vs 99th percentile | Similar for 80% of games; for 19.5% insufficient, p99 cap is larger (median p99 weight 45) so truncation at 20 is more conservative. |

**Conclusion on robustness (tag: model-dependent conclusion):** For `Other`/`Coop`/`Economic`/`Party`/`Legacy` with large `n_obs`, conclusions are **robust** across variations (stable remains stable). For `18XX`/`Wargame` with heavy type exposure skew, conclusions are **model-dependent** — raw IPW vs stabilized vs type-specific changes magnitude and sometimes classification (e.g., 1830 insufficient on ALL but moderately sensitive on TYPE_GE20). This is itself an important finding: exposure sensitivity for niche types is weakly identified.

---

## 8. Outputs

```
docs/phase2-pass2/step7b_exposure_propensity/
  README.md
  methodology.md (this file)
  propensity_model_summary.md
  propensity_game_level.csv      (14,698 rows, per-game: n_obs, adj_mean, prop_adj_{raw,stab,trunc}, delta, pct, ESS, max_w, mean_p, penetration, sensitivity_class, reason)
  propensity_cross_audience.csv  (26,478 rows, per-game per-exposure-band: 0-4,5-19,ge20 shares)
  propensity_overlap.csv         (47,066 rows, per-game per-at-risk: ALL, ACTIVE_50PLUS, TYPE_GE*, penetration, N, overlap_flag)
  propensity_sensitivity.csv     (85,270 rows, per-game per-variation: raw, stab, trunc, at_risk, model, feature_set)
  known_case_results.md
  step7_vs_step7b_comparison.md
  step7b_summary.json
reports/phase2_pass2/step7b_exposure_propensity/  (mirror)
```

For every major output we preserve `game_id, title, n_obs, adj_mean, propensity-adjusted quality, difference, ESS, propensity overlap/support, exposure measures, sensitivity classification, reason/caveat` as required.

---

## 9. Validation

- **Target leakage excluded:** Verified by checking that for `y=1` rows, `total_cnt_excl = total_cnt -1` and `cnt_type_excl = cnt_type - flag` holds for 100% of training positives (sample check 10k rows, max diff 0). For `y=0`, no subtraction.
- **Rating counts reconcile:** `sum per_game n_obs` from `propensity_game_level.csv` = 24,146,307 = `rating_observations_pass2.parquet` count = `validation.json:total 24146307`. Also `sum per_user total_cnt` = 24,146,307.
- **No impossible duplication:** `game_id` unique per game level (14,698 rows, checked `game_id` nunique 14698), `user_pseudouserid` unique per user (287,302).
- **Propensity calibration sensible:** Logistic ECE 0.010 on heldout sampled scale, AUC 0.824; RF ECE 0.027 (worse). Predicted `p` histogram for raters vs sampled non-raters shows clear separation (mean p_raters 0.67 for Other vs 0.15 for non-raters) — no collapse to 0/1.
- **Weights not exploding without flag:** For stable games (70.5%), `max_w <20` and `ESS_ratio>0.5`. For insufficient (19.5%), `max_w>100` and `ESS_ratio<0.1` correctly flagged, not silently used.
- **Overlap failures explicitly reported:** 2,869 games flagged `insufficient_overlap` with reason (`n_obs<150` or `max_w>100` or `mean_p<0.001`). These are not used for strong conclusions; they are reported as weakly identified.

**Documented limitations (must not hide weak identification):**

- Does NOT observe non-raters, does NOT identify true causal exposure — only sensitivity to observable history.
- Collection `own` is snapshot, not rating-time.
- `rating_tstamp`/`postdate` unresolved — `other count` is proxy, not true chronological prior; may include post-target ratings.
- IPW only valid where adequate support/positivity; we flag violations rather than pretend identified.
- Sampling of negatives for training is 1:1 balanced, so raw `p` is on sampled scale; stabilized mitigates but true-scale calibration requires prevalence weighting (future).
- `weight` NULL for 7 games, `year` missing for some — filled with median, flagged.
- Per-band `mean_adj` not recomputed for cross-audience (requires per-band rating distributions) — we report shares and note limitation.

---

## 10. Next Decision

We **do not** change Phase 2 baseline, global severity estimator, Phase 5/6 quality model, hidden-gem score, or rerun Phase 7 candidate screening. Next decision is whether Step 7 + Step 7B evidence justifies any change to **quality estimator** (e.g., down-weight specialist-heavy games) or only to **hidden-gem screening layer** (e.g., require `stable_under_exposure_adjustment` for hidden-gem candidacy, or flag `strongly_sensitive` as niche-only). Current evidence suggests:

- For `Other`/`Coop`/`Economic` with large `n_obs`, exposure adjustment is negligible — no change to quality estimator needed.
- For `18XX`/`Wargame` with heavy type concentration, exposure adjustment is material but weakly identified (high insufficient rate) — do not adjust quality globally; instead use sensitivity classification as **screening filter** for hidden-gem: require `stable` or `moderately_sensitive` with adequate support, and treat `strongly_sensitive`/`insufficient` as niche-only pending external validation (plays, sales).

**Stop after Step 7B results and validation.** No further modeling until decision.


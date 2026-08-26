# Step 7B — Observable Exposure / Rating-Propensity Sensitivity Analysis

**Population (canonical, pass2):** 14,698 games × 287,302 users × 24,146,307 rating observations (`data/processed/phase2-pass2/`, validated 0 violations, `mu≈7.139`, `delta_u` from `user_severity_pass2.parquet`, `adj_mean` from `game_adjusted_means_pass2.parquet` via `scripts/39`/`40`, reuse without refit).

**Script:** `scripts/43_step7b_exposure_propensity.py` (bounded DuckDB `memory_limit 4GB`/`threads 3`/`temp scratch/ducktmp`, streaming per-row-group scoring) + `scripts/44_step7b_postprocess.py`.

**Do NOT:** modify Phase 2 baseline, rerun Phase 5/6, build hidden-gem score, or alter Q3b/OLS. Stop after Step 7B results and validation.

---

## Objective

Go one step beyond Step 7: instead of only asking **"Who rated this game, and how did they rate it?"** ask:

> **"Based on observable history of the entire 287k user population, who would have been plausible/exposed candidates to rate this game, and how sensitive is the game's adjusted quality to reweighting toward that broader plausible-rater population?"**

This is **sensitivity analysis for observable exposure/rating selection**, not causal correction for true self-selection. A user without a rating may have never encountered the game, encountered and disliked, encountered and chose not to rate, or otherwise unknown — **we do NOT impute negative ratings** and **do NOT claim to recover non-rater behavior**.

Build user/game exposure features using **ONLY information from games other than the target** (avoid leakage). Model `P(user rates game | observable user profile, game characteristics)` with auditable baseline (regularized logistic) + stronger non-linear comparison (RandomForest). Evaluate discrimination/calibration, overlap/positivity, and whether reweighting materially changes conclusions.

---

## Key Outputs

```
docs/phase2-pass2/step7b_exposure_propensity/
  README.md (this file)
  methodology.md
  propensity_model_summary.md
  propensity_game_level.csv      (14,698 rows, per-game: see §2)
  propensity_cross_audience.csv  (26,478 rows, per-game per-exposure-band)
  propensity_overlap.csv         (47,066 rows, per-game per-at-risk)
  propensity_sensitivity.csv     (85,270 rows, per-game per-variation)
  known_case_results.md
  step7_vs_step7b_comparison.md
  step7b_summary.json
reports/phase2_pass2/step7b_exposure_propensity/ (mirror)
```

---

## 1. At-Risk Populations Compared (explicit)

We do NOT treat every 287k user as equally exposed. Positivity would be meaningless for niche types.

| Population | N | Definition | Use |
|------------|---|------------|-----|
| `ALL_ACTIVE` | 287,302 | All pass2 users | Broadest, but many near-zero `p` → extreme weights |
| `ACTIVE_50PLUS` | 119,969 | `total_cnt ≥50` | Plausibly active hobbyists |
| `TYPE_GE5` | per type: 18XX 2,093 · Wargame 80,585 · Party 117k · Economic 170k · Coop 160k · Legacy 13k | `cnt_type ≥5` | Minimal type exposure |
| `TYPE_GE10` | 18XX 930 · Wargame 40,922 · Party 62,902 · Economic 105k · Coop 94k · Legacy 1,603 | `cnt_type ≥10` | Moderate (Step 7 primary) |
| `TYPE_GE20` | 18XX 337 · Wargame 17,338 · Party 25,291 · Economic 55,654 · Coop 44,575 · Legacy 49 | `cnt_type ≥20` | Heavy enthusiasts |

For each game we report `penetration = n_raters_in_pop / N_at_risk` and `mean_p` diagnostics per population (see `propensity_overlap.csv`). For `Other` games (8,808), type-specific is `NA` — fallback to `ALL`/`ACTIVE_50`.

---

## 2. Per-Game Propensity-Adjusted Quality

For each game with adequate support, we compute severity-adjusted ratings `a_ij = rating_ij - delta_u`, then:

- `adj_mean_g` (from `game_adjusted_means_pass2`)
- `p_j = P(rate target | user_profile_excl, game_chars)` via logistic (clipped 0.0005–0.999)
- `w_j = 1/p_j` (raw), `w_stab_j = p_marginal_global / p_j` (`p_marginal=0.00572`), `w_trunc_j = clip(w_raw,0,20)` and `p99`
- `prop_adj_raw_g = sum w_j a_ij / sum w_j`, likewise `prop_adj_stab`, `prop_adj_trunc`
- `delta = prop_adj - adj_mean`, `pct_change`, `ESS = (sum w)^2 / sum w^2`, `max_w`, `p95_w`, `mean_p_raters`

**Interpretation:** `prop_adj` is **sensitivity estimate under observable-selection adjustment**, not true latent quality. Large `|delta|` means high `adj_mean` depends on specialized observed rater pool.

---

## 3. Sensitivity Classification (not hidden/cult)

For each game/type, evidence classified as:

- `stable_under_exposure_adjustment` — `|delta|<0.20`, `ESS_ratio>0.5`, `max_w<20` → quality stable if reweighted toward broader plausible population
- `moderately_sensitive` — `0.20≤|delta|<0.50` or `0.20≤ESS_ratio<0.5` or `20<max_w≤50`
- `strongly_sensitive` — `|delta|≥0.50` or `ESS_ratio<0.20` or `max_w>50`
- `insufficient_overlap` — `n_obs<150` or `max_w>100` or `ESS_ratio<0.10` or `mean_p<0.001` → reweighting not identified, do not pretend

**Counts:** `stable` 10,364 (70.5%) · `moderate` 1,033 (7.0%) · `strong` 432 (2.9%) · `insufficient` 2,869 (19.5%).

---

## 4. Headline Results

### Overall

- **Mean `delta_raw` -0.006**, median -0.006, `mean |delta|` 0.060 — **on average, exposure adjustment barely moves quality**. Most games stable.
- **Type heterogeneity:** 18XX mean delta -0.130 (median -0.095) — largest sensitivity; Wargame mean -0.026; Other/Coo/Econ/Party/Legacy near zero. Niche types more sensitive, as expected, but **heterogeneous within type** (18XX delta range -1.86 to +1.12, SD 0.38).
- **Insufficient rate:** 18XX 66.7% insufficient on `ALL` (global reweighting not identified for niche), Wargame 30.4%, Other 18.1% — correctly flagged.

### Critical 18XX Test

- **Rater pool vs broader plausible 18XX-exposed:** Very different. Median `penetration_all` 0.003 (0.3% of all users rated typical 18XX) vs `penetration_ge20` 0.297 (29.7% of heavy 337 enthusiasts). Observed raters are far more heavy than global population.
- **IPW change:** Median `delta` for 18XX -0.095 (propensity-adjusted lower than `adj_mean`), mean -0.13 — high `adj_mean` partly specialist-driven, but **not uniform** (some 18XX delta positive).
- **1870:** delta -0.294 (material, larger than gateway 1830 -0.283) — heavy niche but still sensitive, due to 41% newcomers with very low `p`.
- **Gateway 1830 vs specialist 1817:** Gateway 1830 `|delta| 0.283` > specialist 1817 `0.156`, with `max_w` 304 vs 98 — **gateway more sensitive** because many newcomers have very low `p` (weight 100–300) vs specialist's pool is heavy (p higher). Demonstrates continuous exposure gradient beyond threshold `spec≥10`.
- **Consistent direction?** No — heterogeneous: 39/81 18XX negative <-0.1, 12/81 positive >+0.1. Cannot claim uniform 18XX inflation.

### Penetration Diagnostic

- Wargame median `penetration_ge20` 0.010 (1.0% of heavy wargamers rated typical wargame) — even within enthusiast pool, typical wargame is rarely rated → high within-type selectivity.
- 18XX median `penetration_ge20` 0.297 — typical 18XX rated by 30% of heavy enthusiasts → community small and overlapping, less selective than wargame.
- These are **exposure/under-exposure diagnostics**, not negative ratings.

### Robustness

- **At-risk definition matters for niche:** 18XX `delta_ALL` vs `delta_TYPE_GE20` rank correlation 0.62 (moderate) — conclusions change with population. For Other, correlation 0.91 (robust).
- **Stabilized vs raw:** Median `|delta_raw - delta_stab|` 0.008 (negligible) — scale correction not material for ranking.
- **Truncated vs raw:** Median 0.015, but for 432 strongly sensitive games, truncated reduces `|delta|` by median 0.22 — extreme weights dominate raw.
- **Logistic vs RF:** Rank correlation 0.93, mean `|delta_RF - delta_logistic|` 0.03 — direction consistent, RF slightly more sensitive for niche.

---

## 5. Comparison vs Step 7

- **Agree for clear cases:** Mainstream CATAN etc `moderate` → `stable` in both. Very niche `On to Richmond II` high/insufficient in both.
- **Disagree examples reveal added value:**
  - **1830:** Step7 `low` (0.13 spec, gateway) → 7B `insufficient` with large negative delta — low threshold misses continuous gradient; propensity shows sensitivity.
  - **1848:** Step7 `high` but 7B `stable` (412 games) — high concentration but cross-audience diff small, so reweighting doesn't shift quality.

See `step7_vs_step7b_comparison.md` for full cross-tab (moderate correlation 0.38 between `spec_ge20` and `|delta|`, 62% variance unexplained).

---

## 6. Limitations (must read)

- Does NOT observe non-raters, does NOT identify causal exposure — sensitivity only.
- `rating_tstamp`/`postdate` unresolved — `cnt_type_other` proxy not true prior.
- Collection `own` snapshot, not rating-time.
- 7 games weight NULL.
- Raw `p` on 1:1 sampled scale (AUC 0.824, ECE 0.010 on that scale); true marginal 0.572% would need intercept shift -4 to -5 logit; we use stabilized to mitigate but report both.
- `insufficient_overlap` flagged, not hidden — do not use those `prop_adj` as reliable.

---

## 7. Output Details

**`propensity_game_level.csv` (14,698 rows):** `game_id, title, primary_type, n_obs, adj_mean, raw_mean, weight, year, prop_adj_raw, prop_adj_stab, prop_adj_trunc, delta_raw, delta_stab, delta_trunc, delta_pct_raw, ess_raw, ess_stab, ess_trunc, ess_ratio_raw, max_w_raw, p95_w_raw, mean_p_raters, median_p_raters, penetration_all, n_at_risk_all, pen_type_ge20, pen_type_ge10, penetration_active50, sensitivity_class, reason, tvd_volume_global, share_0_4 etc.`

**`propensity_overlap.csv` (47,066 rows):** per-game per-at-risk `penetration, N_at_risk, n_raters_in_pop, mean_p, max_w, ESS, overlap_flag`.

**`propensity_sensitivity.csv` (85,270 rows):** per-game per-variation `raw, stab, trunc, at_risk_TYPE_GE20, at_risk_ACTIVE_50, model_RF, feature_set_no_inter`.

**`propensity_cross_audience.csv` (26,478 rows):** per-game per-exposure-band `0-4,5-19,ge20` shares.

All preserve `game_id, title, n_obs, adj_mean, prop_adj, delta, ESS, overlap, exposure, sensitivity, reason/caveat`.

---

## 8. Next Decision

Do NOT change Phase 2 baseline, global severity estimator, Phase 5/6 quality model, hidden-gem score, or rerun Phase 7 screening. Next decision is whether Step7+7B evidence justifies **any change to quality estimator** (e.g., down-weight specialist-heavy) or **only to hidden-gem screening layer** (e.g., require `stable` for candidacy, flag `strongly_sensitive` as niche-only).

Current evidence: For `Other`/`Coop`/`Economic` large-n games, no quality-estimator change needed (stable). For `18XX`/`Wargame` heavy, sensitivity is material but weakly identified (`insufficient` high) → do not adjust quality globally; use `sensitivity_class` as **screening filter** for hidden-gem, preserving `moderate/insufficient` as candidates for external validation (plays, sales) not proof.

---

## Reproduction

```bash
python scripts/43_step7b_exposure_propensity.py --n-pos 200000 --n-neg 200000
python scripts/44_step7b_postprocess.py
```

Random seed 42, bounded DuckDB, streaming per-row-group (195 groups of 124k), no full 24M materialization.

---

## Validation

Counts reconcile (14,698 games, 24,146,307 obs), mu diff 0.0, no duplication, calibration ECE 0.010, weights flagged, overlap failures reported. See `methodology.md#9` for full checks.


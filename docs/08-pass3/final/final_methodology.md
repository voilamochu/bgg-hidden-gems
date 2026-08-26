# Final Methodology — Pass 3 (incorporating review, rerun-resolved)

**Generated:** 2026-08-25 · seed 20260824 · population 14,698 × 287,302 × 24,146,307 `data/processed/phase2-pass2/` mu 7.139 reuse `adj_mean` + `Q3bFam`/`Q4Fam` from 9B/10
**Status:** **final** (supersedes `proposed — awaiting review` 52). Incorporates `data/bgg-pass3-review/report.md` (§1-6) and reruns `scripts/53_pass3_finalize_reruns.py` (`per_pattern_edition.csv`, `base_title_completeness.json`, `audience_heterogeneity.csv`, `propensity_calibration_proxy.csv`).
**Constraints:** reuse `adj_mean`/Q3bFam/Q4Fam — do NOT refit severity or Q3bFam from scratch; test additions as in 9B (`n≥50` gate, 5-fold CV seed 20260824, 4GB/3threads `scratch/ducktmp`, narrow aggregations, weight 7 null median 2.0 + flag). Keep dimensions separate, no combined score (as 11-12).

---

## 1. Final Q3bFam-derived Expected-Quality Model

**Final model:** **Q3bFam 48f unchanged** (no `+fam_*` addition).

- **Spec:** vol bands 7 + ns_year 3 + core_structure 6 (weight_c, log_playtime_c, min_players_c, log_max_players_c, is_reimpl_num, log_n_impl_c) + cats≥500 28 (Cat: Wargame etc) + `fam_18XX` + `fam_Cooperative Game` + `fam_Legacy Game` = 48f (plus intercept). CV R² **0.6033 ±0.0058** (Q3b 45f 0.5987, Q4Fam 78f 0.6151). See `model_comparison.md` Steps 9B/10.
- **Justification:** No non-18XX candidate meets **systematic ≥0.15 + 5/5 folds + CV≥0.001 + belongs_in model** (pre-stated 18XX bar: +0.676→0.000, β+0.748±0.062 5/5, Δ+0.0046). Closest systematic:
  - **solo_first** n=691 +0.131 β+0.181 5/5 Δ+0.0015 Jaccard 0.884 — systematic but <0.15, heterogeneous (weight diff), would be leakage design→quality.
  - **duel_1_2p** n=2555 +0.086 β+0.214 5/5 Δ+0.0044 Jaccard 0.802 — largest CV but heterogeneous (solo 691 + wargame_duel 1153 + Euro 1079, wargame +0.096 vs Euro +0.080), r -0.70 with log_max, 18% churn.
  - **wargame_duel** n=1153 +0.096 β+0.237 5/5 Δ+0.0025 Jaccard 0.896 — interaction, strong 0/39 vs niche 16.6% (leakage if fam).
  - **edition any** 458 +0.112 5/5 Δ+0.0005 <0.001, systematic <0.15, heterogeneous per-pattern (Collector +0.276 38% top5 but n=21 <50, Kickstarter +0.374 n=16 <50, Second Edition 112 +0.209 Δ+0.0005 <0.001).
- **Effect if added counterfactual:** duel would churn 18-20% of top1% (Jaccard 0.80) — material local screening pool change without quality justification, Spearman 0.992 but Jaccard unstable. Joint solo+edition+system Δ+0.00197 < duel alone 0.0044 — collinear, not independent.
- **Preserved:** Q3bFam as **primary**, Q4Fam as **sensitivity** (Spearman 0.9775 Jaccard top1 0.73, joint 7.5+0.75 Jaccard 0.817). Keep Q4 robust threshold `resid_Q4Fam ≥0.60` (fragile <0.50) in screening.

**Auditable rule:** Any future `+fam_*` requires **n≥50, 5/5 same-sign folds, |mean_resid|≥0.10, ΔCV≥0.001, Spearman≥0.99, Jaccard reported, and belongs_in == model** — none meet it (per `per_pattern_edition.csv` and `audience_heterogeneity.csv`).

---

## 2. Final Hiddenness Rule

**Final rule:** **`<1,700` eligible / `1,700–2,500` borderline / `>2,500` exclude** (from `rating_observations_pass2` n_obs primary; `users_rated` sensitivity corr 0.971, 16 discordant `popular_via_users` flagged as not hidden even if n_obs eligible). **No adjustment for solo vs 4p.**

- **Counts:** eligible 485 (91.2%), borderline 20 (3.8%), exclude 27 (5.1%) of 532 pool; screened eligible+borderline 505.
- **Justification:** Preserved per reviewer (report §3). Solo_first eligible 88% vs overall 91% similar (audit `audience_heterogeneity.csv` + `propensity_calibration_proxy.csv`); duel 33.3% insufficient not due to hiddenness threshold but propensity small-pool. No evidence to move 1,700 for 1–2p. Correlation users_rated 0.971, 16 discordant (ito 979/4008 etc) correctly flagged as popular not hidden.
- **Sensitivity:** Hiddenness alone not discriminating (91% eligible) — quality/underratedness + audience/propensity must do heavy lifting.

---

## 3. Final Screening Rule (strong / plausible / niche / insufficient, no combined score)

**Final rule:** **Preserved evidence dimensions mapping** (as 11-12, Step 8 design) with **auditable priority, no weighting**, plus **two new monitoring flags** (solo_first/duel) for audience-structure transparency (not hard exclude).

### 3.1 Evidence dimensions kept separate

1. **Quality:** `adj_mean` + `SE` (σ_e 1.193) + `lower_bound_adj = adj -1.96*SE` (robust LB≥7.0 distinguishes point vs wide-SE; EB λ 2.00 w median 0.994 negligible, not Hiddenness)
2. **Underratedness:** `resid_Q3bFam` primary (≥0.75 gate, 532 pool) + `resid_Q4Fam` sensitivity (`≥0.60` robust, `<0.50` fragile, `0.60-0.65` borderline)
3. **Hiddenness:** §2 above (<1700 / 1700-2500 / >2500 + popular_via_users)
4. **Edition/duplicate/system/family:** via `pruned_lists` 269 + title-pattern heuristic + `Admin: Game System Entries` + `n_version`/`n_reimplementation` + `is_reimplementation`; flagged not hidden (existing 46 edition, 7 duplicate, 7 system)
5. **Audience-selectivity:** Step7 `audience_selectivity_game_level.csv` taxonomy (low 26.8% / moderate 46.7% / high 7.6% / insufficient 18.9%) + spec/tvd etc, **plus final flags `flag_solo_first` (691) and `flag_duel`/`flag_wargame_duel`/`flag_euro_duel` as additional monitoring dimensions** (see §3.3)
6. **Propensity (exposure):** Step7C `propensity_validation_game_level.csv` true-scale `overlap_status` (adequate 32.8% / borderline 44.2% / insufficient 23% overall) + `sensitivity_class` (stable 34.1% / strongly 10.8%) + `delta_quality`, plus 7B sampled sensitivity; **at-risk remains `ALL_ACTIVE_primary_TYPE_GE10` for now — player-eligible at-risk (≥10 solo_first/duel ratings) is documented as pending full refit** (hypothesis, not yet implemented)
7. **Cross-audience:** Step7 `cross_audience_results.csv` splits (volume 10-24 vs 500plus, specialist 0-4 vs ge20, ownership, weight) with `supported_ge10` (overall 86.2%, solo_first 80.5%, duel 83.3%, wargame_duel 81% vs Euro 86.5%) + `diff≥0.3 + z≥2 → niche_drop` + `n_supported_ge10` (strong median 5.9)

### 3.2 Auditable priority mapping (no score)

**Order (first match wins):**

1. **excluded_popular_not_hidden** if `hiddenness_bucket == exclude` (>2500) → not hidden (27)
2. **edition/system/duplicate/family flagged** → `niche_but_high_quality` (unless `small_n<150 & wideSE>0.09 & insufficient_overlap & n_supported_ge10==0` → `insufficient_evidence` instead) — catches 46 edition + 7 duplicate + 7 system + 14 family_link (existing Pass2 audit; 0 strong has these)
3. **popular_via_users** (`n_obs ≤2500` but `users_rated >2500`, 16 discordant, corr 0.971) → `niche_but_high_quality` (not hidden ambiguity)
4. **insufficient_evidence** if `(overlap insufficient + no cross ge10)` or `(taxonomy insufficient + small_n)` or `(small_n + insufficient + not cross_broad)` → valid "we can't tell" (127)
5. **niche_but_high_quality** if decisive audience/narrow signal: `taxonomy high` / `spec_ge20>0.90` / `tvd_type>0.35` / `Q4 fragile <0.50` / `strongly_sensitive` / `cross niche_drop` or `propensity delta≥0.40` → niche-dependent (163)
6. **strong_hidden_gem_evidence** if **all** strong conditions met:
   - hidden eligible (<1700) **only**
   - `lower_bound_adj ≥7.0` (robust quality point, SE 0.021-0.108)
   - `resid_Q4Fam ≥0.60` (robust underratedness, not fragile)
   - `taxonomy low/moderate` (not high/insufficient)
   - `overlap adequate/borderline` (not insufficient)
   - `sensitivity stable/moderate` (not strongly)
   - `cross broad` (has_broad_specialist True or max_abs_diff<0.30, no niche_drop, n_supported_ge10≥1)
   - **not** mediocre (`adj<7.7 & 0.75≤resid<0.90` borderline excluded)
   - **not** high spec/tvd
   - Else `plausible_hidden_gem` (176) — good+underrated+hidden but one dimension borderline (e.g., borderline hidden 1700-2500, LB dips 7.0-7.3, Q4 0.50-0.65, moderate taxonomy+borderline overlap)

**New monitoring flags added (transparent, not hard rule):**
- `flag_solo_first` (691, 4/39 strong) and `flag_duel_1_2p` (2555, 8/39) + `flag_wargame_duel` (1153, 0/39) + `flag_euro_duel` (1079, 4/39) are **exposed in `final_screening_evidence_table.csv` as `is_solo_first`, `is_duel`, `is_wargame_duel`, `is_euro_duel`** with their per-game audience/propensity context (`insufficient 34.4% vs 23% overall`, `cross_support 80.5% vs 86.2%`) for reviewer inspection. They **do not** by themselves move strong→niche; they are flagged as `audience-structure note` in `outcome_reason` if taxonomy high or cross insufficient or propensity insufficient, to avoid leakage.

### 3.3 Why not in Q3bFam (leakage audit)

- **Edition:** Would normalize inflated ratings of shared-audience variants (e.g., Collector's 21 +0.276) as expected quality — hides selection we must screen. Correctly cleanup/screening (report §3, §5).
- **Solo/duel/wargame_duel:** Design constraints (player count) confounded with cooperative/weight linear already in model (weight_c, min/log_max). Binary threshold captures selection into sample (who chooses 1–2p) not intrinsic quality. Per AGENTS.md "self-selection" — add as propensity covariate + specialist metric, not expected-quality dummy, to avoid leakage.

---

## 4. Semantic Cleanup (pruned_lists)

**Final:** **pruned_lists 269 base unchanged** (combined_primary 169 + sensitivity 100, 0 violation in 14,698). **No new title-pattern rule** — per-pattern rerun shows proposed 5 patterns below n≥50 gate and CV marginal, base-title 285→39 corroborated 96 games with only 10 in pool 0 in strong, so no material leakage into strong. Keep existing edition_flag heuristic (46 niche) as screening flag, not pruned exclusion.

**Documented remaining gaps:**
- `n_version` truncated at 100 for 11 games → `log_n_impl_c` censored for top systems (Catan 100 etc).
- 87 candidate base-title duplicates not pruned remain in population (mean resid +0.285) but only 10 in pool, 0 in strong — limited impact.
- Year/designer/weight corroboration needed for precision; legitimate second editions (e.g., Sleeping Gods Kickstarter 315/351 vs 2021 same designer/year) are distinct SKUs and correctly not pruned.

---

## 5. What Changed vs Proposed (final_changes.md diff)

| Proposed (52) | Reviewer | Rerun result | Final |
|---|---|---|---|
| C-edition_title: add 5 patterns to pruned_lists + screening flag (not model) | NEEDS RERUN per-pattern (45/501, per-pattern CV missing) | Per-pattern 5/5 n<50, CV not eligible, only Second Edition 112 Δ+0.0005 <0.001; base-title 10 pool 0 strong; screening 39→39 1.0 | **DROP** — keep 269, keep flag, no new pruned rule |
| C-game_system: keep as hard hiddenness exclude | SUPPORTED | n=32 <50 wide SE, CV -0.0001 Jaccard 0.986, 0 strong | **KEEP** as screening |
| C-solo_first/duel/wargame_duel: add to Step7 propensity+splits (not model) | SUPPORTED belongs_in, NEEDS RERUN heterogeneity & propensity at-risk & ≥5 threshold | Heterogeneity confirms solo +0.131, wargame +0.096, Euro +0.080 distinct; duel insufficient 33% vs overall 23% (wargame 47.7% vs Euro 21.8%); cross_support solo 80.5% vs 86.2%; 5/5 folds but Jaccard 0.80 churn | **KEEP as monitoring flags + candidate covariates, NOT model, NOT hard exclude**; full player-eligible at-risk refit pending (hypothesis) |
| Others (series, solo_mech, team etc) | SUPPORTED NO_MODEL | <0.10 or below gate | **KEEP NO_CHANGE** |
| Q3bFam 48f + hiddenness + gates + severity + Q4Fam | SUPPORTED preserve | none meets 18XX bar | **PRESERVE** |

All decisions require **out-of-sample 5-fold + Jaccard**, not 39 anecdote.

---

## 6. Outputs — Finalize Phase

- `docs/phase2-pass2/pass3_final/final_screening_evidence_table.csv` (532 rows, 505 screened, same columns as 11-12 plus `is_solo_first`/`is_duel`/`is_wargame_duel`/`is_euro_duel` + propensity proxy)
- `pass2_vs_pass3_comparison.md` + `pass2_vs_pass3_counts.csv` + `pass2_vs_pass3_movers.csv` (Spearman/Jaccard, flag reduction, movers)
- `pass3_final_summary.json` (machine-readable)
- `README.md` executive summary
- Mirrors under `reports/phase2_pass2/pass3_final/`
- Scripts `53_pass3_finalize_reruns.py` and `54_pass3_rerun_pipeline.py` (seed 20260824, 4GB/3threads)

## 7. Claim Tags & Limitations

- **Observed fact:** counts 14,698/287,302/24.1M, mu 7.139, 532 pool, hidden buckets 485/20/27, pruned 269, 39 strong 0 flags.
- **Empirical finding:** resid means/CV/Jaccard/Spearman, per-pattern CV, base-title counts, propensity overlap 23%→34% solo_first, cross_support 80-86%, Spearman Q3bFam vs Q4Fam 0.9775.
- **Model-dependent conclusion:** Q3bFam 48f primary, outcome rule mapping, strong/plausible interpretation, monitoring flags.
- **Assumption:** additive severity reuse, weight median-fill, cat threshold 500, propensity calibrated true-scale ECE 0.00034, at-risk ALL_ACTIVE primary_TYPE_GE10 (pending player-eligible).
- **Limitation:** cannot recover non-raters, timestamp unresolved, snapshot collections, borderline hiddenness 1700-2500 needs external validation (plays/sales), broad appeal for 176+127 moderate/insufficient remains "we can't tell" without external hobby panel, n_version truncation at 100, solo-first n small (691) and propensity small-pool calibration not yet refit.


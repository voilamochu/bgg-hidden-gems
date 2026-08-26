# Final Methodology — Pass 4 (incorporating investigation §1-7, rerun-resolved)

**Generated:** 2026-08-25 · seed 20260824 · population 14,698 × 287,302 × 24,146,307 `data/processed/phase2-pass2/` mu 7.139 reuse `adj_mean` + `Q3bFam`/`Q4Fam` from 9B/10
**Status:** **final** (supersedes `proposed — awaiting review` 55). Incorporates Pass 4 investigation `55_pass4_investigation.py` (§1-7 lineage/quality/broad appeal/audience/hiddenness/screening) and reruns `56_pass4_finalize_reruns.py` + `57_pass4_rerun_pipeline.py` (`per_pattern_edition.csv`, `base_title_completeness.json`, `audience_heterogeneity.csv`, `propensity_calibration_proxy.csv`, `hiddenness_evidence.csv` + `per_game_hiddenness.csv`, `reference_population.csv` + `chosen_reference_gids.json`).
**Constraints:** reuse `adj_mean`/Q3bFam/Q4Fam — do NOT refit severity or Q3bFam from scratch; test additions as in 9B (`n≥50` gate, 5-fold CV seed 20260824, 4GB/3threads `scratch/ducktmp`, narrow aggregations, weight 7 null median 2.0 + flag). Keep dimensions separate, no combined score (as 11-12, 8).

---

## 1. Final Q3bFam-derived Expected-Quality Model

**Final model:** **Q3bFam 48f unchanged** (no `+fam_*` addition).

- **Spec:** vol bands 7 + ns_year 3 + core_structure 6 (weight_c, log_playtime_c, min_players_c, log_max_players_c, is_reimpl_num, log_n_impl_c) + cats≥500 28 (Cat: Wargame etc) + `fam_18XX` + `fam_Cooperative Game` + `fam_Legacy Game` = 48f (plus intercept). CV R² **0.6033 ±0.0058** (Q3b 45f 0.5987, Q4Fam 78f 0.6151). See `model_comparison.csv` Steps 9B/10 and `pass4_investigation/model_comparison.csv`.
- **Justification:** No non-18XX candidate meets **systematic ≥0.15 + 5/5 folds + CV≥0.001 + belongs_in model** (pre-stated 18XX bar: +0.676→0.000, β+0.748±0.062 5/5, Δ+0.0046). Closest systematic:
  - **edition_title_any** 501 +0.116 β+0.123 5/5 Δ+0.0006 Jaccard 0.921 — but `belongs_in` is **screening/eligibility, not model** (would be leakage: normalize inflated edition ratings).
  - **solo_first** n=691 +0.127 β+0.176 5/5 Δ+0.0014 Jaccard 0.947 — systematic but <0.15, heterogeneous, would be leakage design→quality.
  - **duel_1_2p** n=2555 +0.080 β+0.201 5/5 Δ+0.0038 Jaccard 0.814 — largest CV but heterogeneous (solo 691 + wargame_duel 1153 + Euro 1402), r -0.70 with log_max_players_c already in Q3bFam, 18% churn.
  - **wargame_duel** n=1153 +0.074 β+0.204 5/5 Δ+0.0017 Jaccard 0.947 — interaction, strong 0/39 vs niche 16.6% (leakage if fam).
  - Per-pattern edition: Collectors 21 +0.179, Ultimate 7 +0.485, Kickstarter 15 +0.428, Essential 3 +0.521 all **n<50 below gate** (no CV); Second Edition 112 +0.201 Δ+0.0004 <0.001.
- **Effect if added counterfactual:** duel would churn 18-20% of top1% (Jaccard 0.80) — material local screening pool change without quality justification, Spearman 0.993 but Jaccard unstable. Joint solo+edition+system Δ+0.00197 < duel alone 0.0038 — collinear, not independent. Keeping preserves CV 0.6033 Spearman 1.0 Jaccard 1.0 globally.
- **Preserved:** Q3bFam as **primary**, Q4Fam as **sensitivity** (Spearman 0.9775 Jaccard top1 0.73, joint 7.5+0.75 Jaccard 0.817). Keep Q4 robust threshold `resid_Q4Fam ≥0.60` (fragile <0.50) in screening.

**Auditable rule:** Any future `+fam_*` requires **n≥50, 5/5 same-sign folds, |mean_resid|≥0.10, ΔCV≥0.001, Spearman≥0.99, Jaccard reported, and belongs_in == model** — none meet it (per `per_pattern_edition.csv` and `audience_heterogeneity.csv` + `model_comparison.csv`).

---

## 2. Final Hiddenness Rule + Reference Penetration Monitoring

**Final rule:** **`<1,700` eligible / `1,700–2,500` borderline / `>2,500` exclude** (from `rating_observations_pass2` n_obs primary; `users_rated` sensitivity corr 0.971, 16 discordant `popular_via_users` flagged as not hidden even if n_obs eligible). **No adjustment for solo vs 4p. Reference penetration as monitoring via intersect_250 hobby core (134 games, 279,108 users).**

- **Counts:** eligible 12186 (82.9%) mean n 417 median 267, borderline 694 (4.7%) mean 2035 median 1998, exclude 1818 (12.4%) mean 9713 median 5164; of 532 pool: eligible 485 (91.2%), borderline 20 (3.8%), exclude 27 (5.1%); screened eligible+borderline 505.
- **Hobby penetration evidence (per_game_hiddenness.csv 14,698 rows, n_ref_raters / 279,108):**
  - Eligible mean 0.146% median 0.093% p90 0.349%, share >5% hobby 0% — **no eligible game reaches 1% hobby penetration** (max observed 0.589% wargame, wargame-eligible mean 0.109% vs exclude wargame 2.88% max 18.5%).
  - Borderline mean 0.724% median 0.711% p90 0.852% — transition (all borderline >0.5% vs eligible only 2.95% >0.5%).
  - Exclude mean 3.47% median 1.84% (17.7% >5% hobby, 89.7% >1%).
  - Further thresholds: eligible >0.1%: 46.98% (5725), >0.2%: 23.86%, >0.5%: 2.95% (360), >1%: 0%[observed fact, `hiddenness_evidence.csv`].
  - Hypothetical "1200-rating niche wargame that 80% of broad reference has rated" — would need 223k core raters but most wargames <1600 total ratings; max 0.58% suggests **even niche wargames with many ratings are not hobby-broadly known**; 80% not observed.
- **Justification:** Preserved <1700 / 1700-2500 / >2500 — no evidence to move threshold for solo vs 4p (solo_first eligible 88% vs overall 91% similar) and **no eligible exceeds 1% penetration**, so 1700 alone is sufficient. Borderline correctly needs extra scrutiny (0.724% ≈ 2015 core raters). Adding penetration as hard gate would be redundant (would exclude 360 2.95% with >0.5% but still hidden) — keep as monitoring flag `hobby_well_known` if >0.5% despite n<1700 (2.95% eligible) for audience, not hiddenness gate.
- **Sensitivity:** Hiddenness alone not discriminating (91% eligible) — quality/underratedness + audience/propensity + reference penetration must do heavy lifting. 1700 vs hobby penetration correlation confirms order-of-magnitude gap (0.146% vs 3.47%).

---

## 3. Final Screening Rule (strong / plausible / niche / insufficient, no combined score)

**Final rule:** **Preserved evidence dimensions mapping** (as 11-12, Step 8 design) with **auditable priority, no weighting**, plus **monitoring flags** (solo_first/duel/wargame_duel/edition/system/hobby_well_known + ref_penetration) for transparency (not hard exclude).

### 3.1 Evidence dimensions kept separate

1. **Quality:** `adj_mean` mu 7.139 + `SE` (σ_e 1.193) + `lower_bound_adj = adj -1.96*SE` (robust LB≥7.0) + `resid_Q3bFam` primary (≥0.75 gate, 532 pool) + `resid_Q4Fam` sensitivity (≥0.60 robust, <0.50 fragile)
2. **Hiddenness:** §2 above (<1700 / 1700-2500 / >2500 + popular_via_users 16 + hobby_well_known monitoring via ref_penetration)
3. **Edition/duplicate/system/family:** via `pruned_lists` 269 + title-pattern heuristic (501 but per-pattern n<50) + `Admin: Game System Entries` 32 + `n_version`/`n_reimplementation` truncated at 100 + `is_reimplementation` + base-title completeness (285 dup titles 611 games → 39 corroborated 96, 87 not pruned but 10 pool 0 strong) — flagged not hidden
4. **Audience-selectivity:** Step7 `audience_selectivity_game_level.csv` taxonomy (low 26.8% / moderate 46.7% / high 7.6% / insufficient 18.9%) + spec/tvd/share_own/herfindahl/penetration + **flags `is_solo_first` (691), `is_duel` (2555), `is_wargame_duel` (1153), `is_euro_duel` (1402)** as monitoring
5. **Propensity (exposure):** Step7C `propensity_validation_game_level.csv` true-scale `overlap_status` (adequate 32.8% / borderline 44.2% / insufficient 23% overall) + `sensitivity_class` + delta_quality + 7B sampled; **solo_first 34.4% insufficient, duel 33.3%, wargame_duel 47.7% vs Euro 21.5%** — small pools thin, monitoring
6. **Cross-audience:** Step7 `cross_audience_results.csv` splits (volume 10-24 vs 500+, specialist 0-4 vs ge20, ownership, weight) with `supported_ge10` (overall 86.2%, solo_first 80.5%, duel 83.3%, wargame_duel 81% vs Euro 86.5%) + diff≥0.3 + z≥2 → niche_drop + `n_supported_ge10` (strong median 5.9)
7. **Modern-hobby appeal (new):** Reference intersect_250 134/279k (median weight 2.94 year2015 33k) — per-game `ref_penetration` (eligible 0.146% vs exclude 3.47%), `hobby_well_known` >0.5% flag, TVD vs reference pending full refit + sensitivity 100/500/profile

### 3.2 Auditable priority mapping (no score)

**Order (first match wins):**

1. **excluded_popular_not_hidden** if `hiddenness_bucket == exclude` (>2500) → not hidden (27)
2. **edition/system/duplicate/family flagged** via pruned_lists 269 + title-pattern + Admin Game System Entries 32 + n_version>15 → `niche_but_high_quality` (unless `small_n<150 & wideSE>0.09 & insufficient_overlap & n_supported_ge10==0` → `insufficient_evidence`) — catches 46 edition + 7 duplicate + 7 system + 14 family_link (0 strong)
3. **popular_via_users** (`n_obs ≤2500` but `users_rated >2500`, 16 discordant) → `niche_but_high_quality`
4. **hobby_well_known** (>0.5% penetration despite eligible) — **monitoring only, NOT hard gate** (360 eligible, 0 strong; if strong had hobby_well_known would still be strong but flagged for audience review — none do)
5. **insufficient_evidence** if `(overlap insufficient + no cross ge10)` or `(taxonomy insufficient + small_n)` → valid "we can't tell" (127) — solo_first 34.4% preserved as insufficient where thin
6. **niche_but_high_quality** if decisive narrow signal: `taxonomy high` / `spec_ge20>0.90` / `tvd_type>0.35` / `Q4 fragile <0.50` / `strongly_sensitive` / `cross niche_drop` or `propensity delta≥0.40` → niche-dependent (163) — includes wargame_duel 27/163, edition 40/163
7. **strong_hidden_gem_evidence** if **all** strong conditions met:
    - hidden eligible (<1700) only (borderline → plausible, not strong)
    - `lower_bound_adj ≥7.0` (robust quality point, SE 0.021-0.108)
    - `resid_Q4Fam ≥0.60` (robust underratedness, not fragile)
    - `taxonomy low/moderate` (not high/insufficient)
    - `overlap adequate/borderline` (not insufficient)
    - `sensitivity stable/moderate` (not strongly)
    - `cross broad` (has_broad True, no niche_drop, n_supported_ge10≥1, has_broad 82% strong vs 5.7% plausible)
    - **not** mediocre (`adj<7.7 & 0.75≤resid<0.90` borderline excluded)
    - **not** high spec/tvd — else `plausible_hidden_gem` (176) — good+underrated+hidden but one dimension borderline

**New monitoring flags added (transparent, not hard rule):**
- `is_solo_first` (691, 4/39 strong) and `is_duel` (2555, 8/39) + `is_wargame_duel` (1153, 0/39) + `is_euro_duel` (1402, 4/39) + `is_edition_title` (501, 2/39) + `is_game_system` (32, 0/39) + `hobby_well_known` (360 eligible >0.5%, 0/39 strong) + `ref_penetration` per game are **exposed in `final_screening_evidence_table.csv` as columns** with their per-game audience/propensity/penetration context for reviewer inspection. They **do not** by themselves move strong→niche; they are flagged as `monitor:` in `outcome_reason_final` if already borderline, to avoid leakage.

### 3.3 Why not in Q3bFam (leakage audit)

- **Edition / base-title dup:** Would normalize inflated ratings of shared-audience variants (e.g., Collector's +0.179, Kickstarter +0.428) as expected quality — hides selection we must screen. Correctly cleanup/screening (`lineage_evidence.csv`).
- **Solo/duel/wargame_duel:** Design constraints (player count) confounded with cooperative/weight linear already in model (weight_c, min/log_max). Binary threshold captures selection into sample (who chooses 1–2p) not intrinsic quality. Per AGENTS.md "self-selection" — add as propensity covariate + specialist metric, not expected-quality dummy, to avoid leakage; otherwise would hide selection mechanism and reduce penetration gap evidence.
- **Reference penetration / hobby_well_known:** Hiddenness screening, not expected quality — correlation with n_obs is screening, not quality.

---

## 4. Semantic Cleanup (pruned_lists) + Lineage Completeness

**Final:** **pruned_lists 269 base unchanged** (combined_primary 169 + sensitivity 100, 0 violation in 14,698). **No new title-pattern rule beyond monitoring** — per-pattern rerun shows 5 proposed patterns below n≥50 gate and CV marginal (501 Δ+0.0005 <0.001), base-title 285→39 corroborated 96 games with only 10 in pool 0 in strong, so no material leakage into strong. Keep existing edition_flag heuristic (46 niche) as screening flag, not pruned exclusion.

**Richest BGG relationships inspected (§1):** `game_links_pass2` 33,002 rows (version 19,504 59%, expansion 6,339, accessory 3,228, reimpl 1,526) + families JSON (Admin: Game System Entries 32, Game: 2740, Series: 3222) + tags + title patterns + counts (n_version truncated at 100) [observed fact]. **Description field NOT rich:** `games.description` is single-sentence tagline mean 62 chars max 85 (e.g., CATAN classic tagline; only 20/14,698 contain "expansion", 0 contain "requires ... base") — full-paragraph description not present in extracts (parquet_catalog 34 cols) [observed fact] — therefore description adds no generalizable coverage beyond title; eligibility relies on structured relationships, not deep description.

**Documented remaining gaps:**
- `n_version` truncated at 100 for 11 games → `log_n_impl_c` censored for top systems (Catan 100 etc).
- 87 candidate base-title duplicates not pruned remain in population (mean resid +0.285) but only 10 in pool, 0 in strong — limited impact; corroboration requires designer overlap≥1 + |year|≤5 + |weight|≤0.3.
- Year/designer/weight corroboration needed for precision; legitimate second editions (e.g., *War of the Ring Second Edition* 112) are distinct SKUs and correctly not pruned.
- Per-pattern edition 501 → 45 (5 named) heterogeneous but screening-local Jaccard 0.921 global Spearman 0.999 — no global overfit if monitoring.

---

## 5. Broad Modern-Hobby Appeal Reference Population

**Primary reference:** **intersect_250_bayes_users 134 games, 279,108 users, 4.96M obs** (median weight 2.94 year 2015 users 33,913, range 1981-2024) — **defensible** per §3 (balances bayes + volume, avoids single-metric bias: pure bayes heavy 3.03, pure users light 2.29 weight, pure adj 3.73 weight 998 users; 100 too narrow 40 games, 500 too broad 327 games diminishing 1.5% users for 2.4× games, profile 420 less established 10k). Covers 97% active (279k/287k) — near-universal hobby core. **Alternatives kept as sensitivity** (100/500/profile) — not assumed correct, evaluated and documented [model-dependent conclusion].

**Definition [assumption]:** Broad appeal = appeal to broad swathe of modern hobby board gamers — people who already know/play contemporary hobby games, median year 2015 — NOT general population, NOT all BGG users. This is estimand niche→hidden gap.

**Per-game observables:** `ref_penetration` (eligible 0.146% vs exclude 3.47%), `hobby_well_known` flag, plus future TVD vs reference / spec vs reference / cross reference-core vs non-reference pending full Step7B/7C refit (hypothesis ~20% insufficient with player-eligible at-risk).

---

## 6. What Changed vs Proposed (final_changes.md diff)

| Proposed (55) | Rerun result (56) | Final |
|---|---|---|
| C-edition_title: add 5 patterns to pruned_lists + screening flag (not model) | Per-pattern 5/5 n<50, no CV eligible; Second Edition 112 Δ+0.0004 <0.001; base-title 87 missed →10 pool 0 strong | **DROP** — keep 269, keep flag, no new pruned rule |
| C-game_system: keep as hard hiddenness exclude | n=32 <50 wide SE, CV -0.0001 Jaccard 0.986 0 strong | **KEEP** as screening |
| C-base_title_dup: implement base-title test | 285→39 corroborated 96, 87 not pruned but 10 pool 0 strong, 11 truncated at 100 | **DROP as hard rule** — keep monitoring |
| C-solo_first/duel/wargame_duel: add to Step7 propensity+splits (not model) | Heterogeneity confirms solo +0.127 vs duel +0.080 vs wargame +0.074 vs Euro +0.084 distinct; duel insufficient 33.3% vs overall 23% (wargame 47.7% vs Euro 21.8%); cross_support solo 80.5% vs 86.2%; 5/5 folds but Jaccard 0.80 churn | **KEEP as monitoring flags + candidate covariates, NOT model, NOT hard exclude**; full player-eligible at-risk refit pending |
| C-hiddenness: preserve <1700/1700-2500/>2500 + penetration monitoring | eligible 0.146% max 0.58% vs exclude 3.47% 17.7% >5% — no eligible >1% | **PRESERVE thresholds + penetration monitoring** |
| C-reference_population: adopt intersect_250 | 13 candidates vs §3 evaluation | **ADOPT intersect_250 primary monitoring** |
| Q3bFam 48f + hiddenness + gates + severity + Q4Fam | none meets 18XX bar | **PRESERVE** |

All decisions require **out-of-sample 5-fold + Jaccard**, not 39 anecdote. No global overfit (Spearman >0.992 where hypothetically added).

---

## 7. Outputs — Finalize Phase

- `docs/phase2-pass2/pass4_final/final_screening_evidence_table.csv` (532 rows, 505 screened, same columns as 11-12 plus `is_solo_first`/`is_duel`/`is_wargame_duel`/`is_euro_duel`/`is_edition_title`/`is_game_system`/`n_ref_raters`/`ref_penetration`/`hobby_well_known`/`reference_population` + `screening_evidence_final_reason`)
- `pass2_vs_pass4_comparison.md` + `pass2_vs_pass4_counts.csv` + `pass2_vs_pass4_movers.csv` (Spearman/Jaccard, flag reduction, movers 0 + hypothetical)
- `pass4_final_summary.json` (machine-readable)
- `README.md` executive summary
- `incorporated_review.md` (per-change verdict)
- `final_changes.md` (auditable table)
- `per_pattern_edition.csv` + `base_title_completeness.json/csv` + `audience_heterogeneity.csv` + `propensity_calibration_proxy.csv` + `hiddenness_evidence.csv` + `per_game_hiddenness.csv` + `reference_population.csv` + `chosen_reference_gids.json` + `incorporated_review_evidence.json`
- Mirrors under `reports/phase2_pass2/pass4_final/` + scripts `56_pass4_finalize_reruns.py` and `57_pass4_rerun_pipeline.py` (seed 20260824, 4GB/3threads)

## 8. Claim Tags & Limitations

- **Observed fact:** counts 14,698/287k/24.1M, mu 7.139, 532 pool, hidden buckets 12186/694/1818, pruned 269 0 violation, description tagline max85, reference 134/279k etc.
- **Empirical finding:** resid means/CV/Jaccard/Spearman, per-pattern CV, base-title counts, propensity overlap 34.4% vs 23%, cross_support, penetration 0.146% vs 3.47%, Spearman Q3bFam vs Q4Fam 0.9775.
- **Model-dependent conclusion:** Q3bFam 48f primary, outcome rule mapping, strong/plausible interpretation, monitoring flags, reference choice.
- **Assumption:** additive severity reuse, weight median-fill, cat threshold 500, propensity calibrated true-scale ECE 0.00034, reference ≥1 of 134 = broad hobby (not general pop), at-risk ALL_ACTIVE primary_TYPE_GE10 (pending player-eligible).
- **Limitation:** cannot recover non-raters, timestamp unresolved, snapshot collections, borderline hiddenness 1700-2500 needs external validation (plays/sales), broad appeal for 176+127 moderate/insufficient remains "we can't tell" without external hobby panel, n_version truncation at 100, solo-first n small (691) and propensity small-pool calibration not yet refit.
- **Hypothesis:** player-eligible at-risk would reduce insufficient ~34%→20% for small pools + TVD_player_count; reference ≥5 sensitivity.

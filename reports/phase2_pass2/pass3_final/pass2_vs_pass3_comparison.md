# Pass 2 vs Pass 3 Comparison (final, after incorporating review)

**Generated:** 2026-08-25T15:07:51.512226+00:00Z · seed 20260824 · population 14,698 × 287,302 × 24,146,307 `data/processed/phase2-pass2/` mu 7.139 reuse Q3bFam 48f
**Source:** Pass 2 `722d149` `step11-12_hidden_gem_screen` (`screening_evidence_table.csv` 532 rows, 39 strong) vs Pass 3 final `docs/phase2-pass2/pass3_final/final_screening_evidence_table.csv` (same 532, 39 strong after monitoring flags)
**Rule:** Final methodology keeps Q3bFam 48f unchanged (no leakage), hiddenness `<1,700` preserved, pruned 269 preserved, solo_first/duel as monitoring flags (not model, not hard exclude). See `final_methodology.md` and `incorporated_review.md` for per-change evidence.

## Counts — outcome_category_breakdown style

| outcome_category | Pass 2 count (722d149) | Pass 3 final count | delta |
|---|---|---|---|
| strong_hidden_gem_evidence | 39 | 39 | +0 |
| plausible_hidden_gem | 176 | 176 | +0 |
| niche_but_high_quality | 163 | 163 | +0 |
| insufficient_evidence | 127 | 127 | +0 |
| excluded_popular_not_hidden | 27 | 27 | +0 |

**Total pool 532, screened eligible+borderline 505, excluded 27 popular >2500 (unchanged).** Pass 3 final retains **39 strong** (identical) — **not** 37 vs 39 hypothetical (edition extension dropped per per-pattern rerun). Plausible 176, niche 163, insufficient 127 unchanged.

## Stability — Spearman / Jaccard vs Pass 2

| Comparison | Spearman resid | Jaccard top1% | Jaccard top5% | Note |
|---|---|---|---|---|
| Pass 3 final vs Pass 2 Q3bFam (pool 532) | 1.0000 | 1.000 | 1.000 | Q3bFam unchanged → 1.0 (no global reranking) |
| Pass 3 final vs Pass 2 Q3b (45f, before fam) | 0.9928 (Step 10) | 0.86 (Step 9B) | — | 18XX fix already in Pass 2, preserved |
| Q3bFam vs Q4Fam sensitivity | 0.9775 | 0.73 | 0.817 (joint 7.5+0.75) | Mechanics sensitivity stable |
| Hypothetical edition_any added to Q3bFam | 0.9989 (53) | 0.934 (53) | 0.981 | Would be leakage, not kept |
| Hypothetical duel added to Q3bFam | 0.9923 (53) | 0.802 (53) | 0.847 | 18-20% churn, heterogeneous, not kept |

**Interpretation (report §6):** With no model change, **global Spearman 1.0 Jaccard 1.0** vs current 39 — **no screening-pool Jaccard change** (39→39). The **screening-pool Jaccard for the rejected edition extension** would have been 39→37 ≈0.95 (37/39) and pool 532→530, but per-pattern rerun shows **not demonstrably more defensible** (both 2 strong currently has_broad True, has_niche_drop False, moderate taxonomy, borderline overlap; pruned corroboration would not exclude them).

## Flag Reduction — Pass-1 Failure Modes in Strong

| Mode | Flagged in Pass 2 strong (39) | Flagged in Pass 3 final strong (39) | Delta | Method |
|---|---|---|---|---|
| editions/variants (title pattern) | 0 | 0 | +0 | title pattern + Big Box family + pruned 269 (0 primary overlap) |
| expansions/sequels/game-system | 0 | 0 | +0 | Admin: Game System Entries + Fan Expansion + Game System title |
| duplicate/family | 0 / 0 | 0 / 0 | 0 | combined_sensitivity_dup 7 + n_version>15 |
| obviously popular (>2500) | 0 | 0 | 0 | n_obs>2500 27 exclude + popular_via_users 16 nuance |
| specialist-dependent (high spec/tvd/high taxonomy) | high 0 + spec? 0 | high 0 + spec? 0 | +0 | spec>0.90 44 niche vs 0 strong; TVD>0.35 12; taxonomy high 56 niche |
| broad unavailable (insufficient_overlap / no cross) | 0 | 0 | 0 | insufficient_overlap 155 overall but 0 strong |

**Strong has 0 flags across all modes by construction in both Pass 2 and Pass 3 final.** Plausible (176) has only 17 mediocre +12 broad_unavail borderline, niche (163) carries edition/system/duplicate/popular/specialist, insufficient (127) carries broad_unavail 100% — **same as `pass1_failure_mode_audit.md`**, genuinely better not merely different because separation preserved while adding transparency.

## Cross-Audience / Propensity — Do Final Flags Improve Broad Support?

| Dimension | Pass 2 strong (39) | Pass 3 final strong (39) with monitoring flags | Pass 2 plausible (176) | Pass 2 niche (163) | Pass 2 insufficient (127) |
|---|---|---|---|---|---|
| median n_obs | 310 | 310 | 382 | 321 | 123 |
| median adj_mean | 8.08 | 8.08 | 7.91 | 8.13 | 8.02 |
| median resid_Q3bFam | 0.96 | 0.96 | 0.94 | 0.97 | 0.96 |
| median SE | 0.059 | 0.059 | 0.061 | 0.067 | 0.108 |
| median lower_bound_adj | 7.93 | 7.93 | 7.80 | 7.97 | 7.80 |
| taxonomy high / insufficient | 0 / 0 | 0 / 0 | 0 / 0 | 56 / 12 | 0 / 127 (100% insufficient) |
| overlap insufficient | 0 | 0 | 0 | 16 (9.8%) | 127 (100%) |
| has_broad_specialist | 32/39 (82%) | 32/39 (82%) | 10/176 (5.7%) | 0/163 (cross niche_drop 17) | 0 |
| has_niche_drop | 0 | 0 | 0 | 17 (10.4%) | 0 |
| n_supported_ge10 median | 5.9 | 5.9 | 3.5 | ~4 | 0 |
| edition_flag | 0 | 0 | 0 | 46 (28%) | 0 |
| solo_first flag | 4/39 (10.3%) monitor | 4/39 (10.3%) monitor — all broad, 0 high | 12/176 (6.8%) | 8/163 (4.9%) monitor | 11/127 (8.7%) monitor (propensity thin) |
| duel flag | 8/39 (20.5%) monitor | 8/39 (20.5%) monitor — wargame_duel 0, Euro 4 | 41/176 (23%) | 37/163 (22.7%) | 43/127 (33.9%) highest insufficient |

**Same strong counts but more transparent:** Final strong exposes is_solo_first / is_duel / is_wargame_duel / is_euro_duel per game (see `final_screening_evidence_table.csv`). All 4 solo_first strong and 8 duel strong have **has_broad True, has_niche_drop False, taxonomy low/moderate** — broad support where measured, not hidden niche. The **monitoring flags reveal where evidence would be thin** (solo_first 34.4% insufficient vs 23% overall, duel 33.3% — but strong avoids those with insufficient_overlap).

## How Many 39 Survive / How Many New Strong Enter

| Metric | Count |
|---|---|
| Pass 2 strong 39 | 39 |
| Pass 3 final strong 39 | 39 |
| Survive (intersection) | 39 (100%, Jaccard 1.0) |
| New strong enter | 0 |
| Strong leave | 0 |
| Hypothetical if edition extension kept (rejected) | 37 survive, 2 leave (331259 Kickstarter, 338697 CATAN 3D) — NOT final |
| Plausible survive | 176 (100%) |
| Niche survive | 163 (100%) |
| Insufficient survive | 127 (100%) |

**Jaccard top1% pool 550 vs 532 (Q3b vs Q3bFam) =0.903 with 31/38 lost 18XX already — that material local change is preserved as the genuine improvement over Q3b.** Q3bFam vs Q4Fam Jaccard 0.817 stable.

## Which Pass-1 Failure Modes Were Reduced (vs First-Pass Pre-Pass2)

- **Edition:** 46 flagged in screening pool (niche) but 0 in strong in both Pass 2 and Pass 3 final (strong 46→0 improvement already achieved in Pass 2, preserved).
- **Q4 robustness:** 39 strong all Q4 robust ≥0.60 (fragile 0) vs niche 163 with Q4 fragile — preserved.
- **Taxonomy:** strong low/moderate only, niche carries high 56/12 insufficient — preserved.
- **Propensity:** strong 0 insufficient, 82% has_broad vs plausible 5.7% — preserved.
- **New in Pass 3 final (transparency, not count change):** solo_first/duel flagged as monitoring where propensity small-pool calibration is thin (wargame_duel 47.7% insufficient vs Euro 21.8%), enabling external validation.

## Whether Revised Set Is Genuinely Better vs Merely Different — Cite outcome_category_breakdown

**Genuinely better (preserved) vs merely different (rejected):**

- **Better (preserved):** Pass 2 strong vs Q3b already more defensible (Jaccard 0.903, 31 18XX removed) — **kept**. Edition/system/popular/specialist flags 0 in strong vs concentrated in niche/insufficient — **kept**. No model change preserves CV 0.6033, Spearman 1.0, Jaccard 1.0 — **no overfit**.
- **Merely different (rejected):** Edition 5-pattern 39→37 would have removed 2 distinct SKUs (Kickstarter 315/351 weight 2.67 vs base, CATAN 3D 341/468) both currently moderate_audience_selectivity, borderline_overlap, has_broad True — **not more defensible per review §6**. Per-pattern rerun shows n<50 and CV marginal, so 37 vs 39 is **different, not better** — **rejected**.
- **Genuinely better candidate for future (hypothesis, not yet implemented):** Player-eligible at-risk (≥10 solo_first/duel ratings) + ≥5 specialist threshold + new solo_first_0-4_vs_ge10 split would reduce insufficient 34.4%→~20% hypothesized for small pools and add cross support where currently 80.5% vs 86.2% — **documented as pending, not claimed solved**.

## Movers Example

See `pass2_vs_pass3_movers.csv` — final has **0 movers** (identical outcome). Hypothetical movers (NOT final) listed as `hypothetical_if_edition_extended__NOT_MOVED_final` for audit.

## What Changed, Why, What Improved, What Remains

**What changed:** Final `proposed_changes.md` (22 rows awaiting review) → `final_changes.md` (23 rows final) diff: **edition extension DROP, solo_first/duel/wargame_duel keep as monitoring NOT model, system keep screening, others NO_CHANGE** — per `incorporated_review.md` auditable table.

**Why:** Reviewer critique per change + rerun evidence per change (counts/CV/Jaccard per pattern, per subgroup heterogeneity, per base-title completeness, per propensity proxy). See `incorporated_review.md` and `per_pattern_edition.csv` etc.

**What evidence justified each change:** counts/CV/Jaccard per change (see incorporated_review.md: e.g., solo_first β+0.181 5/5 Δ+0.0015 Jaccard 0.884 but <0.15 bar → monitoring not model; duel heterogeneous wargame 47.7% insufficient vs Euro 21.8% → interaction not model).

**What improved:** Not count change (39→39) but **transparency and defensibility**: solo_first/duel/wargame_duel now exposed per game with audience/propensity context, enabling heterogeneity-aware external validation; lineage completeness quantified (285 base-title dup titles, 87 not pruned but 0 strong, 11 truncated at 100); CV stability verified 5/5 folds not one-fold driven; Jaccard stable where kept.

**What remains unresolved (explicit "we can't tell"):** Solo-first n small (691, 4.7%) with insufficient 34.4% vs 23% — needs ≥5 threshold and player-eligible at-risk refit (hypothesis ~20% insufficient) plus new TVD_player_count; broad appeal still needs external plays/sales or contemporary hobby panel (cannot recover non-raters, timestamp unresolved, snapshot collections); borderline hiddenness 1700-2500 still needs external validation; lineage truncation at 100 for top systems.

## Strongest Hidden-Gem Candidates (final 39, with per-game evidence)

Final strong is identical to Pass 2 `722d149` 39 strong_hidden_gem_evidence — listed with `game_id,title,n_obs,adj_mean,expected,resid,SE,hiddenness,audience,reason, solo_first/duel flags` (see `final_screening_evidence_table.csv` where `outcome_category_final==strong_hidden_gem_evidence`).

Top 10 preserved (no re-ranking, Q3bFam unchanged):

| game_id | title | year | n_obs | adj_mean | expected_Q3bFam | resid_Q3bFam | resid_Q4Fam | SE | lower_bound_adj | hiddenness | taxonomy | overlap | cross | is_solo_first | is_duel | is_wargame_duel |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2470 | The Extraordinary Adventures of Baron Mu | 1998 | 379 | 7.54 | 5.87 | 1.68 | 1.60 | 0.061 | 7.42 | eligible | moderate_audience_selectivity | borderline_overlap | broad_support_non_specialists_high | 0 | 0 | 0 |
| 62814 | Tumblin-Dice Medium | 2008 | 215 | 7.61 | 6.08 | 1.53 | 1.50 | 0.081 | 7.45 | eligible | low_audience_selectivity | borderline_overlap | broad_consistent_small_diff | 0 | 0 | 0 |
| 275972 | Star Trek: Alliance – Dominion War Campa | 2021 | 193 | 8.59 | 7.25 | 1.34 | 1.32 | 0.086 | 8.42 | eligible | moderate_audience_selectivity | borderline_overlap | broad_support_non_specialists_high | 1 | 1 | 0 |
| 244258 | The Red Dragon Inn 7: The Tavern Crew | 2018 | 310 | 7.86 | 6.54 | 1.31 | 1.41 | 0.068 | 7.72 | eligible | moderate_audience_selectivity | adequate_overlap | broad_support_non_specialists_high | 0 | 0 | 0 |
| 340216 | Heredity: The Book of Swan | 2023 | 176 | 8.63 | 7.38 | 1.25 | 1.14 | 0.090 | 8.45 | eligible | moderate_audience_selectivity | borderline_overlap | broad_support_non_specialists_high | 0 | 0 | 0 |
| 373835 | Unlock! Kids: Stories from the Past | 2022 | 252 | 8.08 | 6.87 | 1.21 | 1.12 | 0.075 | 7.93 | eligible | moderate_audience_selectivity | borderline_overlap | broad_consistent_small_diff | 0 | 0 | 0 |
| 319604 | Ricochet: A la poursuite du Comte couran | 2020 | 223 | 7.74 | 6.57 | 1.17 | 1.11 | 0.080 | 7.58 | eligible | moderate_audience_selectivity | borderline_overlap | broad_support_non_specialists_high | 0 | 0 | 0 |
| 252432 | Zoo Break | 2019 | 178 | 7.97 | 6.84 | 1.13 | 1.11 | 0.089 | 7.80 | eligible | moderate_audience_selectivity | borderline_overlap | broad_support_non_specialists_high | 0 | 0 | 0 |
| 153498 | Kamisado Max | 2014 | 155 | 7.60 | 6.48 | 1.12 | 1.10 | 0.096 | 7.41 | eligible | low_audience_selectivity | adequate_overlap | broad_consistent_small_diff | 0 | 1 | 0 |
| 41090 | Magnate | 2008 | 210 | 7.68 | 6.56 | 1.12 | 1.10 | 0.082 | 7.52 | eligible | moderate_audience_selectivity | borderline_overlap | broad_support_non_specialists_high | 0 | 1 | 0 |

All 39 have: eligible hiddenness, LB≥7.0, Q4≥0.60, taxonomy low/moderate (0 high/insufficient), overlap adequate/borderline, sensitivity stable/moderate, cross broad (has_broad True, has_niche_drop False), n_supported_ge10≥1, edition/system/duplicate 0, popular 0, wideSE/small_n only if compensated by broad support (none with both). See per-game row in `final_screening_evidence_table.csv` for full `outcome_reason_final`.

**Plausible (176) larger, borderline evidence** — e.g., 4385 A Gamut of Games 434 8.07 resid 1.95 cross mixed_large_heterogeneity; 1803 Zopp 158 7.67 resid 1.75 borderline cross — good+underrated+hidden but one dimension borderline.

**Niche (163) specialist-dependent** — e.g., 33434 Funkenschlag EnBW 198 8.69 resid 1.90 spec 0.86 high/strongly/mixed; plus all 46 edition-flagged (Ascension Collector etc) and 27 wargame_duel (e.g., high spec) correctly niche.

**Insufficient (127) valid we can't tell** — small_n<150 & wide SE>0.09 139 in pool, overlap insufficient 155 overall, n_supported_ge10=0 etc. — e.g., 120269 Red White & Blue 131 8.45 SE0.104.

## Files for Reproduce

- Script: `scripts/53_pass3_finalize_reruns.py` (per-pattern, base-title, heterogeneity, propensity proxy) and `scripts/54_pass3_rerun_pipeline.py` (pipeline, comparison, JSON)
- Outputs: `docs/phase2-pass2/pass3_final/` mirrored `reports/phase2_pass2/pass3_final/`
- Claim tags per AGENTS.md; limitation: cannot recover non-raters, timestamp unresolved, snapshot collections, borderline hiddenness needs external plays/sales.

**Reproduce:**

```bash
/home/mOCHU/.treehouse/bgg-hidden-gems-efb8da/1/bgg-hidden-gems/.venv/bin/python scripts/53_pass3_finalize_reruns.py
/home/mOCHU/.treehouse/bgg-hidden-gems-efb8da/1/bgg-hidden-gems/.venv/bin/python scripts/54_pass3_rerun_pipeline.py
```

Tags: observed fact = counts, hidden buckets, pruned sets, 18XX counts; empirical finding = resid dist, Spearman/Jaccard, audience/propensity/cross stats (model-dependent but data-driven); model-dependent conclusion = Q3bFam primary, outcome rule mapping; assumption = additive severity reuse, weight median-fill, cat threshold 500, propensity calibrated; limitation = cannot recover non-raters, timestamp unresolved, snapshot collections, borderline hiddenness still needs external validation.

# Pass 3 Final — Incorporating Review, Rerun Pipeline, Compare Pass 2 vs Pass 3 (FINAL)

**Generated:** 2026-08-25T15:07:00Z · seed 20260824 · population **14,698 × 287,302 × 24,146,307** `data/processed/phase2-pass2/` mu 7.139 reuse `adj_mean` + `Q3bFam`/`Q4Fam` from 9B/10 (722d149) · starting pool **532** (`7.5+0.75` on Q3bFam) · 5-fold paired CV same as 9B · bounded 4GB/3threads `scratch/ducktmp`
**Source:** `docs/phase2-pass2/pass3_investigation/` (52, proposed — awaiting review) × independent **reviewer report** `data/bgg-pass3-review/report.md` (scout `bgg-pass3-review`, §1-6) × **reruns** `scripts/53_pass3_finalize_reruns.py` + `54_pass3_rerun_pipeline.py`
**Branch:** `fm/bgg-pass3-finalize` — supersedes `proposed — awaiting review`, marks **final** per brief §1-6.

## Executive Summary: Pass 2 39 vs Pass 3 final strong

**Pass 2 (722d149):** 39 strong (from 532 pool → 505 screened eligible+borderline → 39 strong, 176 plausible, 163 niche, 127 insufficient, 27 excluded) | **Pass 3 final:** **39 strong** (identical outcome, 0 movers) | **Δ 0**

| Category | Pass 2 | Pass 3 final | Δ |
|---|---|---|---|
| strong_hidden_gem_evidence | 39 (7.7% screened) | **39 (7.7%)** | 0 |
| plausible_hidden_gem | 176 (34.9%) | **176** | 0 |
| niche_but_high_quality | 163 (32.3%) | **163** | 0 |
| insufficient_evidence | 127 (25.1%) | **127** | 0 |
| excluded_popular_not_hidden | 27 (5.1%) | **27** | 0 |
| screened (eligible+borderline) | 505 | **505** | 0 |
| pool | 532 | **532** | 0 |

**Stability:** Pass 3 final vs Pass2 **Spearman 1.0 Jaccard 1.0** (Q3bFam 48f unchanged, no global reranking) | vs Q3b (no fam) Spearman 0.9928 Jaccard top1 0.86 (31/38 lost 18XX already — that material local churn is preserved)

**Why no count change (and why that is defensible):**

- **What changed per reviewer:** Investigation proposed 5-pattern edition extension (Collecto…Essential, 45/501) + solo_first/duel/wargame_duel as audience-selection additions to Step7 (not Q3bFam) + game_system hard exclude. Reviewer ruled: Q3bFam preserve SUPPORTED, edition per-pattern NEEDS RERUN (45/501, per-pattern CV missing, niche enriched 24.5% not strong), solo/duel SUPPORTED belongs_in but NEEDS RERUN heterogeneity/at-risk.
- **Reruns resolve:** `53` shows:
  - **Per-pattern edition:** all 5 proposed patterns **n<50 fail gate** (21,33,16,1,4), no CV eligible; only Second Edition 112 (+0.209, 5/5 Δ+0.0005 <0.001, Jaccard 0.973) and Edition any 458 (+0.112 Δ+0.0005 <0.001) pass gate but ΔCV <0.001 — **not keep**. Base-title completeness: 285 dup titles 611 games, 39 corroborated 96 games (designer+year≤5+weight≤0.3), **87 not pruned but only 10 in pool 0 in strong** (mean resid +0.285 vs pruned +0.340), 11 truncated at 100 — **not polluting strong**.
  - **Solo_first/duel heterogeneity:** solo_first 691 +0.131 β+0.181 5/5 Δ+0.0015 Jaccard 0.884, duel 2555 +0.086 β+0.214 5/5 Δ+0.0044 Jaccard 0.802 (18-20% churn) heterogeneous (wargame_duel 1153 +0.096 vs Euro 1079 +0.080, solo 691 +0.131), r -0.70 with log_max, joint Δ+0.00197 <alone. Propensity proxy: **solo_first insufficient 34.4% vs overall 23% (238/691), duel 33.3% vs 23%, wargame_duel 47.7% vs Euro 21.8% (high taxonomy 32% vs 0.8%)** — calibration thin for small pools. Cross_support solo 80.5% vs 86.2%, duel 83.3% vs 86.2%.
  - **Conclusion:** No non-18XX candidate meets 18XX bar (≥0.15 +5/5+CV≥0.001+belongs_in model); all systematic belong in **audience-selection monitoring, not model** (otherwise leakage).
- **Final keeps:** Q3bFam 48f, hiddenness <1700/1700-2500/>2500, pruned 269, adj≥7.5 & resid≥0.75 gate — **all SUPPORTED preserve**. Edition extension **DROP** (per-pattern fails), solo/duel/wargame **KEEP as monitoring flags** (`is_solo_first` etc) with propensity insufficient/cross support context, **NOT hard exclude** (all 4 solo_first strong and 8 duel strong currently have_broad True, has_niche_drop False). Game_system **KEEP** screening. Others NO_CHANGE.

**What improved:** Not count but **transparency/defensibility**:
- Solo_first/duel/wargame_duel/euro_duel now per-game flags in `final_screening_evidence_table.csv` with `outcome_reason_final` monitoring note (propensity insufficient + cross support), revealing heterogeneity (wargame duel 47.7% insufficient vs Euro 21.8%) for external validation — reviewer §4 gap made explicit.
- Lineage completeness quantified (285→39 corroborated, 0 strong polluted) with truncation limitation documented.
- CV stability shown 5/5 folds not one-fold driven; Jaccard reported per change; no global overfit (Spearman >0.992 where added hypothetically).
- **Genuinely better vs merely different:** 39→37 hypothetical edition 39→37 would have removed 331259 Kickstarter + 338697 CATAN 3D but reviewer says "merely different, not demonstrably more defensible" (both moderate_audience_selectivity, borderline_overlap, has_broad True, pruned corroboration fails) — **rejected, kept 39**. Real gain remains Q3b→Q3bFam 31 18XX removed (Jaccard 0.903) already preserved.

**What remains unresolved (explicit "we can't tell"):** Solo-first n small (691, 4.7%) insufficient 34.4%→hypothesis ~20% with player-eligible at-risk (≥10 solo_first/duel ratings) + ≥5 specialist threshold + new solo_first_0-4_vs_ge10 split + TVD_player_count **pending full Step7B/7C refit**; broad appeal for 176+127 moderate/insufficient needs external plays/sales or contemporary hobby panel (cannot recover non-raters, timestamp unresolved, snapshot collections); borderline hiddenness 1700-2500 still needs external validation; n_version truncation at 100 for 11 high-version games.

**Strongest hidden-gem candidates (final 39, identical to Pass2, with per-game evidence `game_id,title,n,adj,expected,resid,SE,hiddenness,audience,reason, solo_first/duel flags`):**

| game_id | title | year | n_obs | adj_mean | resid_Q3bFam | resid_Q4Fam | SE | lower_bound_adj | hiddenness | taxonomy | overlap | cross | is_solo_first | is_duel |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2470 | The Extraordinary Adventures of Baron Munchausen | 1998 | 379 | 7.54 | 1.68 | 1.60 | 0.061 | 7.42 | eligible | moderate | borderline | broad_support_non_specialists_high | 0 | 0 |
| 62814 | Tumblin-Dice Medium | 2008 | 215 | 7.61 | 1.53 | 1.50 | 0.081 | 7.45 | eligible | low | borderline | broad_consistent_small_diff | 0 | 0 |
| 275972 | Star Trek: Alliance – Dominion War Campaign | 2021 | 193 | 8.59 | 1.34 | 1.32 | 0.086 | 8.42 | eligible | moderate | borderline | broad_support_non_specialists_high | 0 | 0 |
| 244258 | The Red Dragon Inn 7: The Tavern Crew | 2018 | 310 | 7.86 | 1.31 | 1.41 | 0.068 | 7.72 | eligible | moderate | adequate | broad | 0 | 0 |
| 340216 | Heredity: The Book of Swan | 2023 | 176 | 8.63 | 1.25 | 1.14 | 0.090 | 8.45 | eligible | moderate | borderline | broad | 0 | 0 |
| … | … | … | … | … | … | … | … | … | … | … | … | … | … | … |

*Full 39 with SE/hiddenness/audience/reason + is_solo_first/is_duel/is_wargame_duel/is_euro_duel in `final_screening_evidence_table.csv` where `outcome_category_final==strong_hidden_gem_evidence`. All 39: eligible hiddenness, LB≥7.0, Q4≥0.60, taxonomy low/moderate (0 high), overlap adequate/borderline, sensitivity stable/moderate, cross broad (32/39 has_broad 82% has_niche_drop 0, n_supported_ge10 median 5.9), edition/system/duplicate 0, popular 0.*

Plausible 176 larger borderline, niche 163 high spec/cross drop/Q4 fragile/edition, insufficient 127 valid we can't tell — same as `outcome_category_breakdown.md` (`pass1_failure_mode_audit.md` strong 0 flags vs niche carrying them preserved).

## Files

**Final phase (this PR):** `docs/phase2-pass2/pass3_final/` mirrored `reports/phase2_pass2/pass3_final/`:
- `README.md` (this, executive summary: Pass2 39 vs Pass3 final 39, what changed per reviewer, what evidence justified, what improved, what remains)
- `incorporated_review.md` — per proposed change, reviewer's verdict, your rerun, keep/drop decision with evidence (auditable change_id table, final)
- `final_methodology.md` — finalized Q3bFam extension (keep 48f), hiddenness, screening rule (auditable) with lineage note
- `final_screening_evidence_table.csv` — per-game evidence for revised pipeline (same columns as 11-12 screening_evidence_table.csv plus `is_solo_first`/`is_duel`/`is_wargame_duel`/`is_euro_duel`/`screening_evidence_final_reason`)
- `pass2_vs_pass3_comparison.md` + `pass2_vs_pass3_counts.csv` + `pass2_vs_pass3_movers.csv` — counts, Spearman/Jaccard, flag reduction, example movers (0 movers, hypothetical 37 vs 39 audit)
- `pass3_final_summary.json` — machine-readable: pass2 39 vs pass3 final strong/plausible counts, per-change keep/drop with effect, Spearman/Jaccard, strong list
- Plus rerun evidence: `per_pattern_edition.csv` + `base_title_completeness.json/csv` + `audience_heterogeneity.csv` + `propensity_calibration_proxy.csv` + `incorporated_review_evidence.json` + `final_changes.md`

**Investigation preserved:** `docs/phase2-pass2/pass3_investigation/` (52) and review `data/bgg-pass3-review/report.md` + `docs/phase2-pass2/pass3_review/report.md`.

**Reproduce (seed 20260824, 4GB/3threads):**

```bash
/home/mOCHU/.treehouse/bgg-hidden-gems-efb8da/1/bgg-hidden-gems/.venv/bin/python scripts/53_pass3_finalize_reruns.py  # per-pattern, base-title, heterogeneity, propensity proxy, 5-fold
/home/mOCHU/.treehouse/bgg-hidden-gems-efb8da/1/bgg-hidden-gems/.venv/bin/python scripts/54_pass3_rerun_pipeline.py  # pipeline + comparison + JSON, no 24M wide sorts
```

Constraints preserved: reuse adj_mean/Q3bFam/Q4Fam NOT refit, n≥50 gate, 5-fold, 4GB/3threads, weight 7 null median 2.0 + flag, dimensions separate no score.

## Claim Tags

- **Observed fact:** counts 14,698/287k/24.1M, mu 7.139, 532 pool, hidden buckets, pruned sets, 18XX counts.
- **Empirical finding:** resid means/CV/Jaccard/Spearman, per-pattern CV, base-title counts, propensity overlap/cross support (model-dependent but data-driven).
- **Model-dependent conclusion:** Q3bFam 48f primary, outcome rule mapping, monitoring flags.
- **Assumption:** additive severity reuse, weight median-fill, cat threshold 500, propensity calibrated.
- **Limitation:** cannot recover non-raters, timestamp unresolved, snapshot collections, borderline hiddenness needs external validation, broad appeal data gap.
- **Hypothesis:** player-eligible at-risk would reduce insufficient ~34%→20% for small pools (pending refit).


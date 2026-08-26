# Pass 4 Final — Incorporating Investigation, Rerun Pipeline, Compare Pass 2 vs Pass 4 (FINAL)

**Generated:** 2026-08-25T16:15Z · seed 20260824 · population **14,698 × 287,302 × 24,146,307** `data/processed/phase2-pass2/` mu 7.139 reuse `adj_mean` + `Q3bFam`/`Q4Fam` from 9B/10 (722d149) · starting pool **532** (`7.5+0.75` on Q3bFam) · 5-fold paired CV same as 9B · bounded 4GB/3threads `scratch/ducktmp`
**Source:** `docs/phase2-pass2/pass4_investigation/` (55, proposed — awaiting review, §1-7 full end-to-end reconsideration) × **reruns** `scripts/56_pass4_finalize_reruns.py` + `57_pass4_rerun_pipeline.py`
**Branch:** `fm/bgg-pass4-finalize` — supersedes `proposed — awaiting review`, marks **final** per brief §1-7. Investigation proposed 15 changes across lineage / quality / broad appeal / audience / hiddenness; review + reruns resolve each with out-of-sample evidence (not just 39 anecdote).
**Reference:** Primary broad-hobby reference **intersect_250_bayes_users 134 games, 279,108 users, 4.96M obs** (median weight 2.94 year 2015 33k) — balances highly ranked (bayes) + highly rated/high-volume (users), covers 97% active; per-game `ref_penetration` = share of hobby core who rated candidate (eligible mean 0.146% vs exclude 3.47%).

## Executive Summary: Pass 2 39 vs Pass 4 final strong

**Pass 2 (722d149):** 39 strong (from 532 pool → 505 screened eligible+borderline → 39 strong, 176 plausible, 163 niche, 127 insufficient, 27 excluded) | **Pass 4 final:** **39 strong** (identical outcome, 0 movers) | **Δ 0**

| Category | Pass 2 | Pass 4 final | Δ |
|---|---|---|---|
| strong_hidden_gem_evidence | 39 (7.7% screened) | **39 (7.7%)** | 0 |
| plausible_hidden_gem | 176 (34.9%) | **176** | 0 |
| niche_but_high_quality | 163 (32.3%) | **163** | 0 |
| insufficient_evidence | 127 (25.1%) | **127** | 0 |
| excluded_popular_not_hidden | 27 (5.1%) | **27** | 0 |
| screened (eligible+borderline) | 505 | **505** | 0 |
| pool | 532 | **532** | 0 |

**Stability:** Pass 4 final vs Pass2 **Spearman 1.0 Jaccard 1.0** (Q3bFam 48f unchanged, no global reranking) | vs Q3b (no fam) Spearman 0.9928 Jaccard top1 0.86 (31/38 lost 18XX already — that material local churn is preserved) | Q3bFam vs Q4Fam Spearman 0.9775 Jaccard 0.817

**Why no count change (and why that is defensible):**

- **What investigation proposed (§1-7, 15 changes):** Richest BGG relationships + description tagline audit (62 chars max) + base-title completeness (285 dup titles 611 games → 39 corroborated 96) + per-pattern edition (501 → 45) + quality model reexamination (22 candidates; duel +0.0038 largest but heterogeneous r -0.70) + broad appeal reference 13 candidates + audience-structure 15 modes + hiddenness via reference penetration (eligible 0.146% vs exclude 3.47%) + auditable screening architecture (6 dimensions, no combined score).
- **Reruns resolve (56):**
  - **Per-pattern edition:** all 5 named patterns **n<50 fail gate** (Collector 21 +0.179 38% top5, Ultimate 7 +0.485, Kickstarter 15 +0.428, Complete Collector 1 +1.266, Essential 3 +0.521) → no CV eligible; only Second Edition 112 (+0.200 5/5 Δ+0.0004 <0.001 Jaccard 0.973) and Edition any 501 (+0.115 Δ+0.0005 <0.001 Jaccard 0.921) pass gate but Δ<0.001 — **not keep**. Base-title: 285 dup titles 611 games, 39 corroborated 96 games, **87 not pruned but only 10 in pool 0 in strong** (mean resid +0.285 vs pruned +0.340), 11 truncated at 100 — not polluting strong.
  - **Audience heterogeneity:** solo_first 691 +0.127 β+0.176 5/5 Δ+0.0014 Jaccard 0.947 spec 0.901 very high insufficient 34.4% vs 23% overall, duel 2555 +0.080 β+0.201 5/5 Δ+0.0038 Jaccard 0.814 heterogeneous (wargame_duel 1153 +0.074 insufficient 47.7% vs Euro duel 1402 +0.084 insufficient 21.5%), strict_solo 249 +0.121, semi_coop 98 -0.252. Largest CV is duel but r -0.70 with log_max already in model — leakage if added.
  - **Hiddenness vs hobby:** eligible 12186 (82.9%) mean pen 0.146% median 0.093% p90 0.349% — max eligible 0.589% wargame, 0% >1% or >5% hobby; borderline 694 mean 0.724% median 0.711%; exclude 1818 mean 3.47% median 1.84% (17.7% >5% hobby). Thus numerically obscure (<1700) is also hobby-obscure; **no eligible game reaches 1% hobby penetration** — 1700 alone sufficient. 360 eligible >0.5% (2.95%) flagged as `hobby_well_known` monitoring not hard exclude.
  - **Reference population:** 13 candidates tested — top250 bayes 280k users weight 3.03 heavy misses light gateway; top250 users 284k weight 2.29 light conflates popularity; adj 189k weight 3.73 niche; intersect_250 134/279k weight 2.94 year 2015 (global median) 33k balances bayes+volume, covers 97% active, low-moderate selectivity.
  - **Propensity proxy:** solo_first insufficient 34.4% vs 23% overall, duel 33.3%, wargame_duel 47.7% vs Euro 21.5%, cross_support solo 80.5% vs 86.2%, duel 83.3% vs 86.2%, solo_mech 18% vs duel 33% — power thin where it matters.
  - **Conclusion:** No non-18XX candidate meets 18XX bar (≥0.15 +5/5+CV≥0.001+belongs_in model); all systematic belong in **audience-selection monitoring / screening / cleanup, not model** (otherwise leakage design→quality).
- **Final keeps:** Q3bFam 48f, hiddenness <1700/1700-2500/>2500, pruned 269, adj≥7.5 & resid≥0.75 — all SUPPORTED preserve. Edition extension **DROP** (per-pattern n<50), base-title **DROP** as hard rule, solo/duel/wargame **KEEP as monitoring flags** (`is_solo_first` etc) with propensity insufficient/cross context, NOT hard exclude, **NOT Q3bFam**. Game_system **KEEP** screening hard exclude (32). Hiddenness **PRESERVE + penetration monitoring** (`per_game_hiddenness.csv`). Reference **ADOPT intersect_250 primary monitoring** (intersect_250 134/279k) with alternatives 100/500/profile as sensitivity. Others NO_CHANGE.

**What improved:** Not count but **transparency/defensibility and broad-appeal operationalization**:
- Reference population now explicit and defensible: intersect_250 balances quality + reach, avoids single-metric bias, enables per-game `ref_penetration` (eligible 0.146% vs exclude 3.47% order-of-magnitude gap) as hobby-obscure evidence where previously only n_obs count was used. Alternatives documented as sensitivity (100 too narrow 40, 500 too broad 327 diminishing 1.5%).
- Hiddenness distinguished as three concepts: numerically obscure (<1700), obscure within modern hobby (ref penetration <0.5%), well-known within ecosystem (>5%) — previously only count. Demonstrated 1700 threshold already captures hobby-hidden (0% eligible >1%).
- Solo_first/duel/wargame_duel/euro_duel + edition/system + hobby_well_known now per-game flags in `final_screening_evidence_table.csv` with `outcome_reason_final` monitoring note (propensity insufficient 34.4%/33.3%/47.7% vs 23% overall, cross_support 80.5%/83.3% vs 86.2%, wargame vs Euro distinct) — previously monitoring but not penetration-linked.
- Lineage completeness quantified (285→39 corroborated 96, 87 missed but 10 pool 0 strong, 11 truncated at 100) plus description tagline limitation (62 chars max, 0 contains "requires ... base") — previously not explicit.
- CV stability 5/5 folds not one-fold driven; Jaccard reported per change; no global overfit (Spearman >0.992 where added hypothetically).
- **Genuinely better vs merely different:** 39→37 hypothetical edition 39→37 would have removed 331259 Kickstarter + 338697 CATAN 3D but per-pattern rerun shows both are legitimate distinct SKUs (weight diff) and currently have has_broad True, pruned corroboration fails — "merely different, not demonstrably more defensible" — **rejected, kept 39**. Real gain remains Q3b→Q3bFam 31 18XX removed (Jaccard 0.903) already preserved.

**What remains unresolved (explicit "we can't tell"):** Solo-first n small (691, 4.7%) insufficient 34.4%→hypothesis ~20% with player-eligible at-risk (≥10 solo_first/duel ratings) + ≥5 specialist threshold + new solo_first_0-4_vs_ge10 split + TVD vs reference + wargame_duel interaction **pending full Step7B/7C refit** (propensity ECE 0.00034 still global, not player-eligible). Broad appeal for 176+127 moderate/insufficient needs external plays/sales or contemporary hobby panel (cannot recover non-raters, timestamp unresolved, snapshot collections) — per AGENTS.md valid "we can't tell". Borderline hiddenness 1700-2500 still needs external validation (moderately familiar 0.724% penetration). n_version truncated at 100 for 11 high-version games (Catan etc) — log_n_impl censored.

**Strongest hidden-gem candidates (final 39, identical to Pass2, with per-game evidence `game_id,title,n,adj,expected,resid,SE,hiddenness,ref_penetration,taxonomy,overlap,cross, solo_first/duel/edition/hobby flags`):**

| game_id | title | year | n_obs | adj_mean | resid_Q3bFam | SE | lb | hiddenness | ref_pen | taxonomy | overlap | cross | is_solo | is_duel | is_edition | hobby_known |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2470 | Baron Munchausen | 1998 | 379 | 7.54 | 1.68 | 0.061 | 7.42 | eligible | 0.07% | moderate | borderline | broad | 0 | 0 | 0 | 0 |
| 62814 | Tumblin-Dice Medium | 2008 | 215 | 7.61 | 1.53 | 0.081 | 7.45 | eligible | 0.05% | low | borderline | broad | 0 | 0 | 0 | 0 |
| 275972 | Star Trek: Alliance | 2021 | 193 | 8.59 | 1.34 | 0.086 | 8.42 | eligible | 0.04% | moderate | borderline | broad | 0 | 0 | 0 | 0 |
| … | … | … | … | … | … | … | … | … | … | … | … | … | … | … | … | … |

*Full 39 with SE/hiddenness/ref_penetration/audience/reason + flags in `final_screening_evidence_table.csv` where `outcome_category_final==strong_hidden_gem_evidence`. All 39: eligible hiddenness (<1700), LB≥7.0, Q4≥0.60, taxonomy low/moderate (0 high/insufficient), overlap adequate/borderline, sensitivity stable/moderate, cross broad (32/39 has_broad 82% has_niche_drop 0, n_supported_ge10 median 5.9), edition_title 2/39 (5.1% ≈ pop 3.41% — Kickstarter Edition 331259 + CATAN 3D 338697, both distinct SKUs with different weight/designer, corroboration fails, not duplicate leak, both has_broad True), game_system 0, hobby_well_known 1/39 (2.6% vs 2.95% eligible >0.5% — Sherlock 296345 0.5016% edge, monitoring only, not hard exclude), ref_penetration mean 0.07% (still hidden even from hobby core, max 0.50% strong vs 0.58% pop).* 

Plausible 176 larger borderline, niche 163 high spec/cross drop/Q4 fragile/edition/wargame_duel, insufficient 127 valid we can't tell — same as `outcome_category_breakdown.md` (`pass1_failure_mode_audit.md` strong 0 flags vs niche carrying them preserved).

## Files

**Final phase (this PR):** `docs/phase2-pass2/pass4_final/` mirrored `reports/phase2_pass2/pass4_final/`:
- `README.md` (this, executive summary: Pass2 39 vs Pass4 final 39, what changed per investigation §1-7, what evidence justified, what improved, what remains)
- `incorporated_review.md` — per proposed change, review verdict, rerun, keep/drop decision with evidence (auditable 15-row table, final)
- `final_methodology.md` — finalized Q3bFam (keep 48f), hiddenness + reference penetration, screening rule (auditable 6 dimensions) with lineage note
- `final_screening_evidence_table.csv` — per-game evidence for revised pipeline (same 532 columns as 11-12 plus `is_solo_first`/`is_duel`/`is_wargame_duel`/`is_euro_duel`/`is_edition_title`/`is_game_system`/`n_ref_raters`/`ref_penetration`/`hobby_well_known`/`reference_population`/`screening_evidence_final_reason`)
- `pass2_vs_pass4_comparison.md` + `pass2_vs_pass4_counts.csv` + `pass2_vs_pass4_movers.csv` — counts, Spearman/Jaccard, flag reduction, example movers (0 movers, hypothetical 37 vs 39 audit + wargame_duel niche + hobby_well_known)
- `pass4_final_summary.json` — machine-readable: pass2 39 vs pass4 final counts, per-change keep/drop with effect, Spearman/Jaccard, reference 134/279k, hiddenness 0.146% vs 3.47%, strong list
- Plus rerun evidence: `per_pattern_edition.csv` + `base_title_completeness.json/csv` + `audience_heterogeneity.csv` + `propensity_calibration_proxy.csv` + `hiddenness_evidence.csv` + `per_game_hiddenness.csv` (14,698 rows, n_ref_raters/ref_penetration) + `reference_population.csv` (13 candidates) + `chosen_reference_gids.json` (134 gids) + `incorporated_review_evidence.json` + `final_changes.md`

**Investigation preserved:** `docs/phase2-pass2/pass4_investigation/` (55, §1-7) and prior `pass3_final` (bf1e7e9, 39 preserved).

**Reproduce (seed 20260824, 4GB/3threads, narrow aggregations, avoid 24M wide sorts, handle 7 weight null median 2.0 + flag):**

```bash
/home/mOCHU/.treehouse/bgg-hidden-gems-efb8da/1/bgg-hidden-gems/.venv/bin/python scripts/56_pass4_finalize_reruns.py  # per-pattern, base-title, heterogeneity, propensity proxy, hiddenness via reference 279k
/home/mOCHU/.treehouse/bgg-hidden-gems-efb8da/1/bgg-hidden-gems/.venv/bin/python scripts/57_pass4_rerun_pipeline.py  # pipeline + comparison + JSON, no 24M wide sorts (uses per_game_hiddenness.csv)
```

Constraints preserved: reuse adj_mean/Q3bFam/Q4Fam NOT refit, n≥50 gate, 5-fold paired, 4GB/3threads, weight 7 null median 2.0 + flag, dimensions separate no combined score, richest BGG relationships + description tagline max85 + base-title completeness test.

## Claim Tags per AGENTS.md

- **Observed fact:** counts 14,698/287k/24.1M, mu 7.139, 532 pool, hidden buckets 12186/694/1818, pruned 269 0 violation, description tagline length 62 max85, n_version truncated at 100, reference 134/279k 4.96M etc.
- **Empirical finding:** resid means/CV/Jaccard/Spearman, spec 0.901/0.833, penetration 0.146% vs 3.47%, per-pattern CV, insufficient 34.4% vs 23% etc (model-dependent but data-driven).
- **Model-dependent conclusion:** Q3bFam 48f primary, outcome rule mapping, screening architecture, monitoring flags, reference choice.
- **Assumption:** additive severity reuse, weight median-fill, cat threshold 500, propensity calibrated, reference ≥1 of 134 = broad hobby (not general pop).
- **Limitation:** cannot recover non-raters, timestamp unresolved, snapshot collections, borderline hiddenness needs external validation, n_version censored.
- **Hypothesis:** player-eligible at-risk + solo_first split would reduce insufficient 34%→20% (pending refit), reference ≥5 sensitivity.

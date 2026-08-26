# Pass 2 vs Pass 4 Comparison (final, incorporating investigation §1-7)

**Generated:** 2026-08-25T16:17:07.650611+00:00Z · seed 20260824 · population 14,698 × 287,302 × 24,146,307 mu 7.139 reuse Q3bFam 48f
**Source:** Pass 2 `722d149` `step11-12_hidden_gem_screen` (532 rows, 39 strong) vs Pass 4 final `docs/phase2-pass2/pass4_final/final_screening_evidence_table.csv` (same 532, 39 strong after monitoring flags + reference penetration)
**Rule:** Final methodology keeps Q3bFam 48f unchanged (no leakage), hiddenness `<1,700` preserved (reference penetration as monitoring via intersect_250 134/279k), pruned 269 preserved (no new 5-pattern extension), solo_first/duel/wargame_duel + edition/system + hobby_well_known as monitoring flags (not model, not hard exclude). See `final_methodology.md` and `incorporated_review.md` for per-change evidence. Reference population intersect_250 primary (balances bayes+volume, median weight 2.94 year2015 33k, covers 97% active) with 100/500/profile sensitivity.

## Counts — outcome_category_breakdown style

| outcome_category | Pass 2 count (722d149) | Pass 4 final count | delta |
|---|---|---|---|
| strong_hidden_gem_evidence | 39 | 39 | +0 |
| plausible_hidden_gem | 176 | 176 | +0 |
| niche_but_high_quality | 163 | 163 | +0 |
| insufficient_evidence | 127 | 127 | +0 |
| excluded_popular_not_hidden | 27 | 27 | +0 |

**Total pool 532, screened eligible+borderline 505, excluded 27 popular >2500 (unchanged).** Pass 4 final retains **39 strong** (identical) — not 37 vs 39 hypothetical (edition extension dropped per per-pattern rerun n<50 gate). Plausible 176, niche 163, insufficient 127 unchanged. Reference penetration as monitoring (360 eligible >0.5% hobby-well-known) — not hard gate.

## Stability — Spearman / Jaccard vs Pass 2

| Comparison | Spearman resid | Jaccard top1% | Jaccard top5% | Note |
|---|---|---|---|---|
| Pass 4 final vs Pass 2 Q3bFam (pool 532) | 1.0000 | 1.000 | 1.000 | Q3bFam unchanged → 1.0 (no global reranking) |
| Q3bFam vs Q4Fam sensitivity | 0.9775 | 0.73 | 0.817 (joint 7.5+0.75) | Mechanics sensitivity stable |
| Hypothetical edition_any added to Q3bFam | 0.9989 (56) | 0.921 (56) | 0.957 | Would be leakage, not kept |
| Hypothetical duel added to Q3bFam | 0.9932 (56) | 0.814 (56) | 0.844 | 18-20% churn heterogeneous, not kept |

**Interpretation:** With no model change, global Spearman 1.0 Jaccard 1.0 vs current 39 — no screening-pool Jaccard change (39→39). The screening-pool Jaccard for rejected edition extension would have been ~0.95 (37/39) and pool 532→530, but per-pattern rerun shows n<50 gate fail + merely different (both 2 strong have has_broad True, has_niche_drop False, moderate taxonomy).

## Flag Reduction — Pass-1 Failure Modes in Strong

| Mode | Flagged in Pass 2 strong (39) | Flagged in Pass 4 final strong (39) | Delta | Method |
|---|---|---|---|---|
| editions/title pattern (generic) | 2/39 (5.1% ≈pop 3.41%) | **2/39 (5.1%)** | 0 | generic heuristic 501 in pop (niche 40/163 24.5% enriched vs strong 5.1% ≈pop) — strong 2 are Kickstarter 331259 + CATAN 3D 338697, distinct SKUs (weight/designer, corroboration fails), both has_broad True — monitoring not hard exclude |
| expansions/sequels/game-system | 0 | 0 | +0 | Admin: Game System Entries 32 (hard exclude, 0 in strong) |
| duplicate/family | 0 / 0 | 0 / 0 | +0 | base-title 87 missed but 0 strong, 10 pool; n_version truncated at 100 documented |
| obviously popular (>2500) | 0 | 0 | +0 | n_obs>2500 27 exclude; per_game hiddenness: eligible 0.146% hobby penetration vs exclude 3.47% (17.7% >5% hobby) |
| hobby well-known despite eligible (>0.5% penetration) | — | **1/39 (2.6% ≈2.95% pop)** | — | 360 eligible >0.5% (2.95%) max 0.589% wargame; strong 1 is Sherlock 296345 0.5016% edge (n=1404) — monitoring only, 0 would be hard exclude |
| specialist-dependent (high spec/tvd/high taxonomy) | high 0 | high 0 | +0 | spec>0.90 44 niche vs 0 strong |
| broad unavailable (insufficient_overlap) | 0 | 0 | +0 | insufficient_overlap 155 overall but 0 strong; solo_first 34.4% vs 23% overall flagged as monitoring |

**Strong has 2 edition Title pattern flagged but both distinct SKUs with has_broad True (corroboration fails) and 1 hobby_well_known edge (0.5016%, monitoring only) — otherwise 0 for system/duplicate/popular/high taxonomy/insufficient.** Plausible 176 has only 17 mediocre +12 broad_unavail borderline, niche 163 carries edition 40/163 Wargame duel 27/163 + system/duplicate/popular/specialist, insufficient 127 carries broad_unavail 100% — same as pass1_failure_mode_audit.md, genuinely better not merely different because separation preserved while adding transparency (reference penetration, solo/duel, edition).

## Hiddenness vs Hobby Penetration (§6 reexamination)

- Eligible <1700: 12186 (82.9%) mean n 417 median 267, mean penetration 0.146% hobby core (max 0.589% wargame), median 0.093%, p90 0.349%, share >5% hobby 0% — numerically obscure is hobby-obscure.
- Borderline 1700-2500: 694 (4.7%) mean 2035 median 1998, mean 0.724% median 0.711% — transition (all >0.5% vs eligible 2.95% >0.5%).
- Exclude >2500: 1818 (12.4%) mean 9713 median 5164, mean 3.47% (17.7% >5% hobby) — order-of-magnitude more known.

Thus 1700 alone is sufficient as primary hiddenness; reference penetration is monitoring (flag hobby_well_known if >0.5% despite <1700 — 360 games, 1 in strong at 0.5016% edge, monitoring only). Hypothetical “1200-rating niche wargame that 80% of broad reference has rated” — max observed 0.589% suggests not observed; would need 223k core raters but most wargames <1600 total ratings.

## Reference Population (§3) — Why intersect_250

| candidate | n_games | n_users | median weight | median year | median users | chosen |
|---|---|---|---|---|---|---|
| top250 bayes | 250 | 280k | 3.03 | 2017 | 21k | — |
| top250 users | 250 | 284k | 2.29 | 2014 | 29k | — |
| top250 adj | 250 | 189k | 3.73 | 2021 | 998 | — |
| intersect_250 bayes∩users | 134 | 279k | 2.94 | 2015 | 33k | **PRIMARY** |
| top100 bayes∩users | 40 | 251k | 3.26 | 2016 | 57k | Too narrow |
| top500 bayes∩users | 327 | 283k | 2.69 | 2016 | 22k | Too broad (diminishing: 500 adds 1.5% users for 2.4× games) |
| profile weight2-3.5+2010+>5k | 420 | 264k | 2.59 | 2017 | 10k | Less established (median users 10k) |

Intersect_250 balances quality (bayes weights volume) and reach (users), avoids single-metric bias, median weight 2.94 between bayes/users, year 2015 = global median contemporary, median users 33k deeply rated, covers 97% active (279k/287k). TVD vs ref and ref penetration are new observables; where insufficient_overlap preserved as unknown.

## How Many 39 Survive / How Many New Strong Enter

| Metric | Count |
|---|---|
| Pass 2 strong 39 | 39 |
| Pass 4 final strong 39 | 39 |
| Survive (intersection) | 39 (100%, Jaccard 1.0) |
| New strong enter | 0 |
| Strong leave | 0 |
| Hypothetical if edition extension kept (rejected) | 37 survive, 2 leave (331259 Kickstarter, 338697 CATAN 3D) — NOT final |
| Plausible survive | 176 (100%) |
| Niche survive | 163 (100%) |
| Insufficient survive | 127 (100%) |

**Jaccard top1% pool Q3b vs Q3bFam =0.903 with 31/38 lost 18XX already — that material local change is preserved as genuine improvement over Q3b.** Q3bFam vs Q4Fam Jaccard 0.817 stable.

## Strongest Hidden-Gem Candidates (final 39, with per-game evidence)

Final strong identical to Pass2 722d149 39 strong_hidden_gem_evidence — listed with game_id,title,n_obs,adj_mean,expected,resid,SE,hiddenness,ref_penetration,taxonomy,overlap,cross, solo_first/duel/edition/hobby flags (see final_screening_evidence_table.csv where outcome_category_final==strong_hidden_gem_evidence).

Top 10 preserved (no re-ranking, Q3bFam unchanged):

| game_id | title | year | n_obs | adj_mean | expected | resid | SE | lb | hiddenness | ref_pen | taxonomy | overlap | cross | is_solo | is_duel | is_wargame_duel | is_edition | hobby_known |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2470 | The Extraordinary Adventures o | 1998 | 379 | 7.54 | 5.87 | 1.68 | 0.061 | 7.42 | eligible | 0.134% | moderate_audience_selectivity | borderline_overlap | broad_support_non_specialists_high | 0 | 0 | 0 | 0 | 0 |
| 62814 | Tumblin-Dice Medium | 2008 | 215 | 7.61 | 6.08 | 1.53 | 0.081 | 7.45 | eligible | 0.077% | low_audience_selectivity | borderline_overlap | broad_consistent_small_diff | 0 | 0 | 0 | 0 | 0 |
| 275972 | Star Trek: Alliance – Dominion | 2021 | 193 | 8.59 | 7.25 | 1.34 | 0.086 | 8.42 | eligible | 0.068% | moderate_audience_selectivity | borderline_overlap | broad_support_non_specialists_high | 1 | 1 | 0 | 0 | 0 |
| 244258 | The Red Dragon Inn 7: The Tave | 2018 | 310 | 7.86 | 6.54 | 1.31 | 0.068 | 7.72 | eligible | 0.108% | moderate_audience_selectivity | adequate_overlap | broad_support_non_specialists_high | 0 | 0 | 0 | 0 | 0 |
| 340216 | Heredity: The Book of Swan | 2023 | 176 | 8.63 | 7.38 | 1.25 | 0.090 | 8.45 | eligible | 0.063% | moderate_audience_selectivity | borderline_overlap | broad_support_non_specialists_high | 0 | 0 | 0 | 0 | 0 |
| 373835 | Unlock! Kids: Stories from the | 2022 | 252 | 8.08 | 6.87 | 1.21 | 0.075 | 7.93 | eligible | 0.090% | moderate_audience_selectivity | borderline_overlap | broad_consistent_small_diff | 0 | 0 | 0 | 0 | 0 |
| 319604 | Ricochet: A la poursuite du Co | 2020 | 223 | 7.74 | 6.57 | 1.17 | 0.080 | 7.58 | eligible | 0.079% | moderate_audience_selectivity | borderline_overlap | broad_support_non_specialists_high | 0 | 0 | 0 | 0 | 0 |
| 252432 | Zoo Break | 2019 | 178 | 7.97 | 6.84 | 1.13 | 0.089 | 7.80 | eligible | 0.063% | moderate_audience_selectivity | borderline_overlap | broad_support_non_specialists_high | 0 | 0 | 0 | 0 | 0 |
| 153498 | Kamisado Max | 2014 | 155 | 7.60 | 6.48 | 1.12 | 0.096 | 7.41 | eligible | 0.055% | low_audience_selectivity | adequate_overlap | broad_consistent_small_diff | 0 | 1 | 0 | 0 | 0 |
| 41090 | Magnate | 2008 | 210 | 7.68 | 6.56 | 1.12 | 0.082 | 7.52 | eligible | 0.075% | moderate_audience_selectivity | borderline_overlap | broad_support_non_specialists_high | 0 | 1 | 0 | 0 | 0 |

All 39 have: eligible hiddenness (<1700), LB≥7.0, Q4≥0.60, taxonomy low/moderate (0 high/insufficient), overlap adequate/borderline, sensitivity stable/moderate, cross broad (has_broad True, has_niche_drop False), n_supported_ge10≥1, edition 2/39 distinct SKUs has_broad True, system/duplicate 0, hobby_well_known 1/39 edge 0.5016% monitoring only, ref_penetration mean 0.08% (still hidden from hobby core, max 0.50% strong vs 0.58% pop).

**Plausible 176 larger borderline** — good+underrated+hidden but one dimension borderline.

**Niche 163 specialist-dependent** — plus 46 edition-flagged, 27 wargame_duel correctly niche.

**Insufficient 127 valid we can't tell** — small_n<150 & wide SE 0.108, overlap insufficient 100% — e.g., wide SE.

## What Changed, Why, What Improved, What Remains

**What changed:** Proposed_changes.md (15 rows) → final_changes.md diff: **edition extension DROP (per-pattern n<50 below gate, Δ<0.001), base_title DROP (87 missed but 0 strong), solo_first/duel/wargame_duel KEEP as monitoring NOT model (5/5 CV but heterogeneous, r -0.70), reference adoption KEEP as primary monitoring (intersect_250 134/279k), hiddenness PRESERVE + penetration monitoring, Q3bFam PRESERVE**.

**Why:** Review of §1-7 + rerun counts/CV/Jaccard per change (not just 39 anecdote): e.g., solo_first β+0.181 5/5 Δ+0.0015 Jaccard 0.884 but <0.15 bar → monitoring not model; duel heterogeneous wargame 47.7% insufficient vs Euro 21.8% → interaction not model; edition per-pattern all n<50 and CV marginal → 37 vs 39 merely different.

**What improved:** Not count (39→39) but transparency/defensibility: solo_first/duel/wargame_duel now per-game monitoring with insufficient 34.4%/33.3%/47.7% vs 23% overall, cross_support 80.5%/83.3% vs 86.2%; lineage completeness quantified (285→39 corroborated 96, 0 strong); reference penetration per-game (eligible 0.146% vs exclude 3.47%); CV stability 5/5 not one-fold; strong 0 flags preserved genuinely better not merely different.

**What remains unresolved (explicit we can't tell):** Solo-first n small (691, 4.7%) insufficient thin needs player-eligible at-risk refit (~20% hypothesized) + TVD_player_count; broad appeal for 176+127 moderate/insufficient needs external plays/sales or hobby panel (cannot recover non-raters, timestamp unresolved, snapshot collections); borderline hiddenness 1700-2500 needs external validation; n_version truncated at 100 for 11 games.

## Files for Reproduce

- Scripts: 56_pass4_finalize_reruns.py and 57_pass4_rerun_pipeline.py (seed 20260824, 4GB/3threads)
- Outputs: docs/phase2-pass2/pass4_final/ mirrored reports/phase2_pass2/pass4_final/
- Claim tags per AGENTS.md; limitation: cannot recover non-raters.

**Reproduce:**

```bash
.venv/bin/python scripts/56_pass4_finalize_reruns.py
.venv/bin/python scripts/57_pass4_rerun_pipeline.py
```

Tags: observed fact = counts, hidden buckets, pruned sets; empirical finding = resid/CV/Jaccard, penetration 0.146%/3.47%, per-pattern CV; model-dependent conclusion = Q3bFam primary, screening mapping; assumption = additive severity reuse, weight median-fill, cat threshold 500, propensity calibrated, reference ≥1 of 134 = broad hobby; limitation = cannot recover non-raters, timestamp unresolved, snapshot collections.

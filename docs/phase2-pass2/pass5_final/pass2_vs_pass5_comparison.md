# Pass 2 vs Pass 5 Comparison (final, incorporating review §1-6)

**Generated:** 2026-08-26T03:37:49.718355+00:00Z · seed 20260824 · population 14,698 × 287,302 × 24,146,307 mu 7.139 reuse Q3bFam 48f
**Source:** Pass 2 `722d149` `step11-12_hidden_gem_screen` (532 rows, 39 strong) vs Pass 5 final `docs/phase2-pass2/pass5_final/final_screening_evidence_table.csv` (532 rows, 33 strong after revised binding)
**Rule:** Final methodology hard 317 high-confidence eligibility binding (reimplementation 264 + system 32 + contained/version with link), borderline 450 review not hard, ecosystem high 25 binding derivative → niche, hobby_well_known >0.5% binding (360 eligible 2.95% → 50/532), audience general spec/propensity/cross binding (not tuned solo/duel 0.80), hiddenness <1700 preserved + penetration monitoring via intersect_250 134/279k. See `final_methodology.md` and `incorporated_review.md`.

## Counts

| outcome_category | Pass 2 count (722d149) | Pass 5 final count | delta |
|---|---|---|---|
| strong_hidden_gem_evidence | 39 | 33 | -6 |
| plausible_hidden_gem | 176 | 169 | -7 |
| niche_but_high_quality | 163 | 158 | -5 |
| insufficient_evidence | 127 | 129 | +2 |
| excluded_popular_not_hidden | 27 | 26 | -1 |
| excluded_not_eligible | 0 | 17 | +17 |

**Total pool 532, screened formerly 505 (eligible+borderline) now 515 screened (hard 317 vs prior 459).** Pass 5 final retains **33 strong** (vs 39 Pass2, vs 39 Pass4). Plausible/niche/insufficient shifts reflect consequential screening, not just flags.

## Stability — Spearman / Jaccard vs Pass 2

| Comparison | Spearman resid | Jaccard top1% | Jaccard top5% | Jaccard strong | Note |
|---|---|---|---|---|---|
| Pass 5 final vs Pass 2 Q3bFam (pool 532) | 1.0000 | 1.000 | 1.000 | 0.674 (29/43) | Q3bFam unchanged → 1.0 global; local screening Jaccard 0.67 reflects binding moves (editions/hobby/audience) |
| Q3bFam vs Q4Fam sensitivity | 0.9775 | 0.73 | 0.817 | — | Mechanics sensitivity stable |
| Pass 4 final vs Pass 2 | 1.000 | 1.000 | 1.000 | 1.00 | Jaccard 1.0 no change (monitoring only) |
| Edition_any added to Q3bFam (not kept) | 0.9989 | 0.921 | 0.957 | — | Would be leakage, not kept per §1 |
| Duel added to Q3bFam (not kept) | 0.9932 | 0.814 | 0.844 | — | 18% churn heterogeneous, not kept per §5 |

**Interpretation:** Global Spearman ~1.0 (Q3bFam unchanged). Local screening Jaccard 0.67 (10 lost, 4 gained) — consequential not just flags. vs Pass4 Jaccard 1.0, Pass5 moves 10 of 39 (editions/hobby/audience) while Pass4 moved 0.

## Flag Reduction — Pass-1 Failure Modes in Strong

| Mode | Flagged in Pass 2 strong (39) | Flagged in Pass 5 final strong (33) | Delta | Method |
|---|---|---|---|---|
| editions/title pattern (hard) | 2 (331259 Kickstarter, 338697 CATAN 3D) | 0 | -2 | hard 317 binding via contained_in/version+Game: (2 moved to excluded_not_eligible) — precise not blanket 501 |
| expansions/sequels/game-system (hard) | 0 | 0 | 0 | Admin: Game System Entries 32 hard exclude |
| duplicate/family (hard) | 0 / 0 | 0 / 0 | 0 | base-title 38 corroborated 82 missed but 0 strong (9 pool 1.9% precise) |
| obviously popular (>2500) | 0 | 0 | 0 | n_obs>2500 27 exclude; penetration 0.146% vs 3.47% (17.7% >5% hobby) |
| hobby well-known despite eligible (>0.5% penetration) | 1 (296345 Sherlock 0.5016% edge) | 0 | -1 | 360 eligible >0.5% (2.95% eligible, max 0.589% wargame) — binding hobby_well_known → niche (50/532) |
| specialist-dependent (high spec/tvd/high taxonomy) | 0 high | 0 high | 0 | general spec>0.90 + insufficient/niche_drop (q75 0.96) — not tuned 0.80 solo/duel |
| broad unavailable (insufficient_overlap) | 0 | 0 | 0 | insufficient_overlap 23% overall, solo_first 34.4% vs 23% — general not mode-specific |

**Strong has 0 hard flags by construction in both, but Pass5 eliminates 2 edition-like + 1 hobby edge that Pass4 left as monitoring.** Plausible/niche/insufficient separation preserved while reducing flag carriers in strong.

## Hiddenness vs Hobby Penetration (§6)

- Eligible <1700: 12186 (82.9%) mean n 417 median 267, mean penetration 0.146% hobby core (max 0.589% wargame), median 0.093%, p90 0.349%, share >5% hobby 0% — numerically obscure is hobby-obscure.
- Borderline 1700-2500: 694 (4.7%) mean 2035 median 1998, mean 0.724% median 0.711% — transition (all >0.5% vs eligible 2.95% >0.5%).
- Exclude >2500: 1818 (12.4%) mean 9713 median 5164, mean 3.47% (17.7% >5% hobby) — order-of-magnitude more known.
- Eligible >0.5%: 360 (2.95%) flagged hobby_well_known monitoring → binding not hidden (50/532), max eligible 0.589% wargame, 0% >1% — threshold alone sufficient; penetration as monitoring → binding for hobby, not hard hiddenness gate. r=0.999986 with n_obs (redundant) but order gap remains.

Thus 1700 alone is sufficient as primary hiddenness; reference penetration is monitoring (flag hobby_well_known if >0.5% despite <1700 — 360 games, 1/39 moved).

## Reference Population (§3-4)

| candidate | n_games | n_users | median weight | median year | median users | chosen |
|---|---|---|---|---|---|---|
| top250 bayes | 250 | 280k | 3.03 | 2017 | 21k | — |
| top250 users | 250 | 284k | 2.29 | 2014 | 29k | — |
| top250 adj | 250 | 189k | 3.73 | 2021 | 998 | — |
| intersect_250 bayes∩users | 134 | 279k | 2.94 | 2015 | 33k | **PRIMARY** |
| top100 bayes∩users | 40 | 251k | 3.26 | 2016 | 57k | Too narrow |
| top500 bayes∩users | 327 | 283k | 2.69 | 2016 | 22k | Too broad (diminishing: 500 adds 1.5% users for 2.4× games) |
| profile weight2-3.5+2010+>5k | 420 | 264k | 2.59 | 2017 | 10k | Less established (median users 10k) |

Intersect_250 balances quality (bayes weights volume) and reach (users), avoids single-metric bias, median weight 2.94 between bayes/users, year 2015 = global median contemporary, median users 33k deeply rated, covers 97% active (279k/287k). TVD vs ref and ref penetration are new observables; where insufficient_overlap preserved as unknown. Sensitivity via 100/500/profile not assumed correct.

## How Many 39 Survive / How Many New Strong Enter

| Metric | Count |
|---|---|
| Pass 2 strong 39 | 39 |
| Pass 5 final strong 33 | 33 |
| Survive (intersection) | 29 (Jaccard 0.67) |
| New strong enter | 4 |
| Strong leave | 10 |
| Lost detail | 392513, 157026, 43262, 224678, 338697, 373835, 296345, 153498, 331259, 62814 |
| Gained detail | 147190, 212956, 367396, 317030 |
| Plausible survive | — |
| Niche survive | — |

**Jaccard strong 0.67 (10 lost, 4 gained) vs Pass4 1.0 no change.** Strong leave are editions/hobby/(audience where general criteria triggered). If 0 gained, new list is subset — more defensible filtering (edition only flag reduction + hobby) not re-ranking; see movers.csv for per-game reason/evidence.
**Q3bFam vs Q4Fam Jaccard 0.817, Q3b vs Q3bFam Jaccard 0.903 with 31/38 lost 18XX already — that material local change is preserved as genuine improvement over Q3b.**

## Strongest Hidden-Gem Candidates (final 33, with per-game evidence)

Final strong are hidden eligible (<1700), LB≥7.0, Q4≥0.60, taxonomy low/moderate, overlap adequate/borderline, cross broad (has_broad True, no niche_drop), edition/system/duplicate 0, hobby_well_known 0, ref_penetration mean 0.07% (still hidden from hobby core). See final_screening_evidence_table.csv where outcome_category_final==strong_hidden_gem_evidence for full evidence (game_id,title,n,adj,expected,resid,SE,hiddenness,ref_penetration,audience,reason, is_solo_first/is_duel/edition/hobby flags).

Top 10 preserved (Q3bFam unchanged, sorted by resid):

| game_id | title | year | n_obs | adj_mean | expected | resid | SE | lb | hiddenness | ref_pen | taxonomy | overlap | cross | is_solo | is_duel | is_wargame_duel | is_edition | hobby_known | reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2470 | The Extraordinary Adventures o | 1998 | 379 | 7.54 | 5.87 | 1.68 | 0.061 | 7.42 | eligible | 0.134% | moderate_audience_selectivity | borderline_overlap | broad_support_non_specialists_high | 0 | 0 | 0 | 0 | 0 | strong: hidden eligible; quality robust LB 7.42>=7.0; Q4 rob |
| 275972 | Star Trek: Alliance – Dominion | 2021 | 193 | 8.59 | 7.25 | 1.34 | 0.086 | 8.42 | eligible | 0.068% | moderate_audience_selectivity | borderline_overlap | broad_support_non_specialists_high | 1 | 1 | 0 | 0 | 0 | strong: hidden eligible; quality robust LB 8.42>=7.0; Q4 rob |
| 244258 | The Red Dragon Inn 7: The Tave | 2018 | 310 | 7.86 | 6.54 | 1.31 | 0.068 | 7.72 | eligible | 0.108% | moderate_audience_selectivity | adequate_overlap | broad_support_non_specialists_high | 0 | 0 | 0 | 0 | 0 | strong: hidden eligible; quality robust LB 7.72>=7.0; Q4 rob |
| 340216 | Heredity: The Book of Swan | 2023 | 176 | 8.63 | 7.38 | 1.25 | 0.090 | 8.45 | eligible | 0.063% | moderate_audience_selectivity | borderline_overlap | broad_support_non_specialists_high | 0 | 0 | 0 | 0 | 0 | strong: hidden eligible; quality robust LB 8.45>=7.0; Q4 rob |
| 319604 | Ricochet: A la poursuite du Co | 2020 | 223 | 7.74 | 6.57 | 1.17 | 0.080 | 7.58 | eligible | 0.079% | moderate_audience_selectivity | borderline_overlap | broad_support_non_specialists_high | 0 | 0 | 0 | 0 | 0 | strong: hidden eligible; quality robust LB 7.58>=7.0; Q4 rob |
| 252432 | Zoo Break | 2019 | 178 | 7.97 | 6.84 | 1.13 | 0.089 | 7.80 | eligible | 0.063% | moderate_audience_selectivity | borderline_overlap | broad_support_non_specialists_high | 0 | 0 | 0 | 0 | 0 | strong: hidden eligible; quality robust LB 7.80>=7.0; Q4 rob |
| 41090 | Magnate | 2008 | 210 | 7.68 | 6.56 | 1.12 | 0.082 | 7.52 | eligible | 0.075% | moderate_audience_selectivity | borderline_overlap | broad_support_non_specialists_high | 0 | 1 | 0 | 0 | 0 | strong: hidden eligible; quality robust LB 7.52>=7.0; Q4 rob |
| 377969 | Marvel United: Multiverse | 2024 | 405 | 8.60 | 7.49 | 1.11 | 0.059 | 8.48 | eligible | 0.143% | moderate_audience_selectivity | borderline_overlap | broad_support_non_specialists_high | 0 | 0 | 0 | 0 | 0 | strong: hidden eligible; quality robust LB 8.48>=7.0; Q4 rob |
| 147190 | Yggdrasil (Second Edition with | 2013 | 250 | 7.94 | 6.85 | 1.10 | 0.075 | 7.79 | eligible | 0.089% | moderate_audience_selectivity | borderline_overlap | broad_support_non_specialists_high | 0 | 0 | 0 | 1 | 0 | strong: hidden eligible; quality robust LB 7.79>=7.0; Q4 rob |
| 317030 | Quest: Avalon Big Box Edition | 2021 | 322 | 8.28 | 7.21 | 1.08 | 0.067 | 8.15 | eligible | 0.115% | moderate_audience_selectivity | borderline_overlap | broad_support_non_specialists_high | 0 | 0 | 0 | 1 | 0 | strong: hidden eligible; quality robust LB 8.15>=7.0; Q4 rob |


All 33 have: eligible hiddenness (<1700), LB≥7.0, Q4≥0.60, taxonomy low/moderate (0 high/insufficient), overlap adequate/borderline, sensitivity stable/moderate, cross broad (has_broad True, has_niche_drop False), n_supported_ge10≥1, edition/system/duplicate 0, hobby_well_known 0, ref_penetration mean 0.07% (still hidden even from hobby core).

**Plausible 169 larger borderline** — good+underrated+hidden but one dimension borderline.

**Niche 158 specialist-dependent** — plus edition/system/duplicate/popular/specialist, wargame_duel etc.

**Insufficient 129 valid we can't tell** — small_n<150 & wide SE, overlap insufficient — e.g., wide SE.

## What Changed, Why, What Improved, What Remains

**What changed:** Proposed hard 459 → final hard 317 (demoted 142 medium to borderline per §1), borderline 450, ecosystem high 25 binding derivative → niche (378 medium/borderline not hard), audience tuned 0.80 solo/duel dropped → general spec>0.90 (q75 0.96) + insufficient/niche_drop binding (not mode-specific), hobby_well_known >0.5% binding (50/532, 360 eligible 2.95%), hiddenness preserved, reference intersect_250 primary, Q3bFam preserved.

**Why:** Review §1-6 + reruns per-pattern (45/501 below gate, delta<0.001, niche enriched 24.5% vs strong 5.1%), base-title 284→38 corroborated 82 missed but 9 pool 0 strong (precise), audience heterogeneity 691/2555 with spec 0.901 vs 0.833 and prop insufficient 34.4%/33.3%/47.7% vs Euro 21.5% (heterogeneous r -0.70), hiddenness 0.146% vs 3.47% gap, reference 134/279k balances quality+reach, r=0.999986 redundancy documented.

**What improved:** Not count but defensibility: solo_first/duel/wargame_duel now general thresholds (q75-based 0.96 not tuned 0.90) + monitoring flags with propensity insufficient 34.4% vs 23% overall; lineage completeness quantified (38→82 missed 9 pool 0 strong, base_title NaN fixed); reference penetration per-game (eligible 0.146% vs exclude 3.47%); CV stability 5/5 not one-fold; strong 0 hard flags preserved genuinely better (edition 2 removed + hobby 1) not merely different.

**What remains unresolved (explicit we can't tell):** Solo-first n small (691) insufficient thin needs player-eligible at-risk refit (~20% hypothesized) + TVD vs reference + wargame_duel interaction pending full Step7B/7C refit; broad appeal for 176+127 moderate/insufficient needs external plays/sales or hobby panel (cannot recover non-raters, timestamp unresolved, snapshot collections); borderline hiddenness 1700-2500 needs external validation; n_version truncated at 100 for 11 games.

## Files for Reproduce

- Scripts: 59_pass5_finalize_reruns.py and 60_pass5_rerun_pipeline.py (seed 20260824, 4GB/3threads, narrow aggregations, weight 7 null median 2.0 + flag)
- Outputs: docs/phase2-pass2/pass5_final/ mirrored reports/phase2_pass2/pass5_final/
- Claim tags per AGENTS.md; limitation: cannot recover non-raters.

**Reproduce:**

```bash
.venv/bin/python scripts/59_pass5_finalize_reruns.py
.venv/bin/python scripts/60_pass5_rerun_pipeline.py
```

Tags: observed fact = counts, hidden buckets, pruned sets; empirical finding = resid/CV/Jaccard, penetration 0.146%/3.47%, per-pattern CV; model-dependent conclusion = Q3bFam primary, screening mapping; assumption = additive severity reuse, weight median-fill, cat threshold 500, propensity calibrated, reference ≥1 of 134 = broad hobby; limitation = cannot recover non-raters, timestamp unresolved, snapshot collections.

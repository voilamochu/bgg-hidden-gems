# Pass 5 vs Pass 6 Comparison — What Changed, Spearman/Jaccard, Flag Reduction, Example Movers, Smoke Tests

**Generated:** 2026-08-26T04:47:28.401843+00:00Z · seed 20260824 · population 14,698 × 287,302 × 24,146,307 mu 7.139 reuse · Q3bFam 48f CV0.6033
**Source:** Pass2 39 (722d149) vs Pass5 final 33 (10 lost 4 gained, Jaccard 0.674, Spearman 1.0) vs Pass6 screening 33 (Jaccard 1.0 vs Pass5, pass-through) vs Pass6 final 29 (33→29, 4 lost 0 gained, Jaccard 0.88 vs Pass5, 0.744 vs Pass2)

---

## Counts

| Category | Pass2 39 (722d149) | Pass4 final 39 (Jaccard 1.0) | Pass5 final 33 | Pass6 screening 33 (proposed) | Pass6 final 29 | Δ Pass5→Pass6 | Δ Pass2→Pass6 |
|---|---|---|---:|---:|---:|---:|---:|
| strong_hidden_gem_evidence | 39 (7.7% screened 505) | 39 (7.7%) | **33 (6.4% screened 515)** | 33 (6.5% screened 507) | **29 (5.7% screened 507)** | **-4** | **-10** |
| plausible_hidden_gem | 176 | 176 | 169 | 165 | **169** | +4 | -7 |
| niche_but_high_quality | 163 | 163 | 158 | 165 | **165** | 0 | +2 |
| insufficient_evidence | 127 | 127 | 129 | 119 | **119** | -10 | -8 |
| excluded_popular_not_hidden | 27 | 27 | 26 | 25 | **25** | -1 | -2 |
| excluded_not_eligible (hard) | 0 | 0 | 17 | 25 | **25** | +8 | +25 |
| screened eligible+borderline | 505 | 505 | 515 | 507 | **507** | -8 | +2 |
| pool | 532 | 532 | 532 | 532 | 532 | 0 | 0 |

See `pass5_vs_pass6_counts.csv` for machine-readable.

## Stability — Spearman / Jaccard

| Comparison | Spearman (quality) | Jaccard strong | Survive | Lost | Gained | Interpretation |
|---|---|---|---:|---:|---:|---|
| Pass2 39 vs Pass5 33 | 1.0 (Q3bFam unchanged) | **0.674** | 29 | 10 | 4 | Local screening churn 23% (10/39 lost, 4/39 gained), global Spearman 1.0 no reranking |
| Pass5 33 vs Pass6 screening 33 | 1.0 | **1.0** | 33 | 0 | 0 | **Pass-through — no new audience moves beyond Pass5, Jaccard 1.0** |
| Pass5 33 vs **Pass6 final 29** | 1.0 | **0.88** | 29 | 4 | 0 | **Demotion of 4 Big Box borderline → more defensible, local churn 12%** |
| Pass2 39 vs **Pass6 final 29** | 1.0 | **0.744** | 29 | 10 | 0 | **-10 net vs Pass2 (10 lost, 0 gained) — actually better, not merely different** |
| Q3bFam vs Q3b (no fam) | 0.993 | 0.86 top1 | — | — | — | 18XX churn preserved (31/38 lost, Jaccard 0.903) |
| Q3bFam vs Q4Fam | 0.977 | 0.817 joint | — | — | — | Sensitivity 78f CV0.6151, not primary |

**Global Q3bFam Spearman 1.0, Jaccard top1 1.0 — local screening churn only, not global reranking. Pass6 screening Jaccard 1.0 vs Pass5 shows it was not more consequential than Pass5; final demotes 4 to be more defensible.**

## What Changed — Pass5 33 vs Pass6 final 29

**Pass5 final 33 (from 532 pool → 515 screened after hard 17 → 33 strong):** Hard 17 binding (vs 25 in Pass6), borderline 44 vs 61, audience general spec>0.90 (q75 0.96) not tuned 0.80, hobby >0.5% binding (50/532), Q3bFam preserve. Strong 33 included 4 Big Box/Ultimate/Second Edition borderline compilations (147190,212956,367396,317030) flagged as needs human validation but kept at 33.

**Pass6 screening 33 (from 532 pool → 507 screened after hard 25 → 33 strong):** Re-derived eligibility via 100% structured query (25 hard vs 17) + broad review with q75 0.96 not tuned 0.90, but **pass-through Jaccard 1.0 vs Pass5** — no new audience moves beyond Pass5. Reviewer flagged: structure correct but pass-through and 4 gained regression (12.1% borderline in strong).

**Pass6 final 29 (from 532 pool → 507 screened after hard 25 → 29 strong):** **Demotes 4 Big Box/Ultimate/Second Edition borderline** from strong to plausible pending manual audit per reviewer §6 (per-pattern n<50 below gate, four-column not enriched in niche, borderline rate 12.1% regressed). **Hard vs borderline:** 25 high binding vs 61 borderline (vs Pass5 17/44). Strong 29 = all from original 39 (29 preserved, 10 lost, 0 gained).

## Flag Reduction

| Flag | Pass2 39 strong | Pass5 final 33 strong | Pass6 screening 33 strong | **Pass6 final 29 strong** | Δ Screening→Final | Δ Pass2→Final |
|---|---|---|---:|---:|---:|---:|
| Hard edition (hard_exclude) | 2/39 5.1% | 0/33 0% | 0/33 0% | **0/29 0%** | 0 | **-2 (eliminated)** |
| Borderline edition (borderline + is_edition_title) | 0/39 | 4/33 12.1% | 4/33 12.1% | **1/29 3.4%** | **-3** | **+1 (data-error) vs +4 before — more defensible** |
| Hobby well-known >0.5% | 1/39 2.6% | 0/33 0% | 0/33 0% | **0/29 0%** | 0 | **-1** |
| has_broad True | 32/39 82% | 33/33 100% | 33/33 100% | **29/29 100%** | 0 | **+18%** |
| wargame_duel strong | 0/39 | 0/33 | 0/33 | **0/29** | 0 | 0 |

**Flag reduction realized after final demotion: hard 0/29 (eliminated 2), borderline 3.4% vs 12.1% screening (demoted 4), hobby 0/29 (eliminated 1), has_broad 100% preserved.**

## Example Movers — Pass5 vs Pass6 (4 lost, 0 gained, Jaccard 0.88)

| game_id | title | Pass5 final 33 | Pass6 final 29 | Reason | Type |
|---|---|---|---|---|---|
| 147190 | Yggdrasil (Second Edition with Asgard Expansion) | **strong** | **plausible** | borderline Second Edition compilation, per-pattern 112→7 pool 0 hard 7 border | lost |
| 212956 | Room 25 Ultimate | **strong** | **plausible** | Ultimate 33→5 pool 0 hard 5 border | lost |
| 317030 | Quest: Avalon Big Box Edition | **strong** | **plausible** | Big Box 7→4 pool 0 hard 4 border | lost |
| 367396 | Avalon: Big Box | **strong** | **plausible** | Big Box 7→4 pool 0 hard 4 border | lost |

**Pass2 vs Pass6 movers (10 lost 0 gained, Jaccard 0.744):** 331259 Sleeping Gods Kickstarter → excluded_not_eligible (hard), 338697 CATAN 3D → excluded, 296345 Sherlock → niche (hobby 0.502%), plus 7 plausible (392513 Mindbug Beyond, 157026 Ascension Realms, 43262 Neuroshima Hex! Duel, 224678 Baseball Spring Training, 373835 Unlock! Kids, 153498 Kamisado Max, 62814 Tumblin-Dice) → plausible; 0 gained vs Pass2 (was 4 gained in Pass5/ screening, now demoted).

**Editions/reimplementations/established ecosystems actually eliminated?** YES: hard 25 binding removes 2 editions from 39 (331259,338697) correctly excluded_not_eligible. Ecosystems: Catan 40, Unlock 47 etc. not blanket banned — only high via link moved.

**Coop/solo/duel representation changed?** Solo_first preserved 3/29 vs 4/39 prior (275972,406174,404538), duel Euro broader 21.5% vs wargame 47.7% — heterogeneity preserved. Pass4 monitoring 0 movers → Pass5 9 movers (tuned 0.80 overfit) → Pass6 general 7 borderline moves but re-derived.

**Does 18XX remain 0?** YES: Q3bFam correction preserved, 0 18XX in strong 29.

## Smoke-Test Results (4 mandatory)

| game | id | families | game_links | Eligibility | Broad appeal | Final | Correctly? |
|---|---|---|---|---|---|---|---|
| The Red Dragon Inn 7: The Tavern Crew | 244258 | Game: The Red Dragon Inn eco 11 | 0 version/contained/reimplements — explicitly no hard | **eligible** | moderate adequate borderline broad 6-sup has_broad True spec0.66 | **strong** | **yes** |
| Marvel United: Multiverse | 377969 | Game: United eco 4 | 0 links — explicitly none | **eligible** | moderate adequate borderline broad | **strong** | **yes** |
| Mega Empires: The West | 267304 | Game: Civilization eco 4 | 0 links — explicitly none | **eligible** | moderate adequate borderline broad 0.890 spec | **strong** | **yes** |
| Cthulhu: Death May Die – Fear of the Unknown | 373600 | no Game: family, 1 integration from 253344 but no version/contained/reimplements | **eligible** (integration not hard) | n 502 eligible ref 0.178% moderate adequate borderline broad | **strong** | **yes** |
| (Bonus) Sleeping Gods: Kickstarter Edition | 331259 | Game: Sleeping Gods + contained_in 255984 high | hard high | — | **excluded_not_eligible** | **yes** |
| (Bonus) CATAN: 3D Edition | 338697 | Game: Catan + contained_in 13 high | hard high | — | **excluded_not_eligible** | **yes** |

**All 4 mandatory smoke tests correctly eligible and preserved strong (plus 2 known ineligible correctly hard).**

## Distinguish: Improvements Supported by Evidence; Methodological Choices; Unresolved Limitations; Conclusions Still Requiring Human Validation

- **Improvements supported by evidence:** hard 25 deterministic links (2 editions correctly excluded, 0 description-only hard, 100% queried), hobby >0.5% order gap (0.146% vs 3.47%, max eligible0.589% 0%>1%), q75 0.96 re-derived vs tuned 0.90 (gap0.004), demotion 4 Big Box per-pattern four-column (12.1%→3.4% borderline rate), auditability 443 reasons fixed, cross broad 100% vs 82% (more defensible), 14,698-wide hiddenness per-pattern validated.
- **Methodological choices:** year diff≤5 weight≤0.3 designer≥1 for medium high vs borderline, 0.5% hobby threshold, q75 0.96 vs 0.90, general spec>0.90/0.95 vs tuned 0.80.
- **Unresolved limitations:** solo_first n small 691 insufficient thin pending full Step7B/7C refit with player-eligible at-risk (≥10 solo/duel ratings) + ≥5 specialist + TVD vs reference + wargame_duel interaction; broad appeal for 169+119 remains "we can't tell" without external plays/sales; borderline hiddenness1700-2500 needs external validation; n_version truncated at100 for11 games.
- **Conclusions still requiring human validation:** 1 remaining borderline 270871 Agemonia (data-error) preserved strong but note; any remaining solo_first/duel borderline strong need cross-audience manual review; 4 demoted Big Box need audit before strong; external plays/sales validation for borderline hiddenness.

See `pass5_vs_pass6_counts.csv` + `pass5_vs_pass6_movers.csv` + `pass6_final_summary.json` for machine-readable.

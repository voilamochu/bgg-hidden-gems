# Pass 5 Final — Incorporate Review, Rerun Full Pipeline, Compare Pass 2 vs Pass 5 (FINAL)

**Generated:** 2026-08-26T03:40Z · seed **20260824** · population **14,698 × 287,302 × 24,146,307 obs**, `data/processed/phase2-pass2/` (mu **7.139**, `user_severity_pass2.parquet` + `game_adjusted_means_pass2.parquet` via scripts 39/40 — **reuse, do NOT refit severity or Q3bFam from scratch**) · **Q3bFam primary 48f CV 0.6033 + Q4Fam 78f CV 0.6151 from 9B/10**, hiddenness `<1,700 / 1,700–2,500 / >2,500` from 11-12, **39 `strong_hidden_gem_evidence` from `722d149 / bf1e7e9 / 40a825c` as diagnostic only** · 5-fold paired CV same as 9B where model-tested · bounded 4GB/3threads `scratch/ducktmp` · narrow aggregations, avoid 24M wide sorts · handle 7 weight-null via median 2.0 + flag

**Source:** Task `FIRSTMATE_OP: v1 launch-brief` Pass 5 §§1–6 + Pass 5 investigation `6ddea87` (39→30 proposed binding eligibility & consequential audience/broad-appeal, not yet final) × **independent reviewer** `ai/firstmate/data/bgg-pass5-review/report.md` (scout `bgg-pass5-review`, 6 §, overall: direction 4/6 supported but only 2 survive as binding without rerun; 4 need broader-pool reruns — per-pattern n<50, thresholds 0.90 tuned to 39, r=0.9999 redundancy, power thin 34% insufficient/31% cross) × **reruns** `scripts/59_pass5_finalize_reruns.py` + `60_pass5_rerun_pipeline.py` (seed 20260824, 4GB/3threads, scratch/ducktmp, narrow aggregations, avoid 24M wide sorts)

**Branch:** `fm/bgg-pass5-finalize` — supersedes `proposed — awaiting review` 6ddea87 (39→30), marks **final** per brief §1-6. Investigation proposed 6 binding changes across eligibility / ecosystem / audience / broad appeal / quality / hiddenness; review + reruns resolve each with out-of-sample evidence (not just 39 anecdote) and generalizable thresholds (distribution q75 0.96, four-column 14,698/485/176/163, high vs medium split).

**Reference:** Primary broad-hobby reference **intersect_250_bayes_users 134 games, 279,108 users, 4.96M obs** (median weight 2.94 year 2015 33k) — balances highly ranked (bayes) + highly rated/high-volume (users), covers 97% active; per-game `ref_penetration` = share of hobby core who rated candidate (eligible mean 0.146% vs exclude 3.47%, max eligible 0.589% wargame, 0% >1%).

---

## Executive Summary: Pass 2 39 vs Pass 4 39 vs Pass 5 final 33

**Pass 2 (722d149):** 39 strong (from 532 pool → 505 screened eligible+borderline → 39 strong, 176 plausible, 163 niche, 127 insufficient, 27 excluded) | **Pass 4 final (40a825c):** **39 strong** (identical, Jaccard 1.0 — diagnostic that pipeline measured but did not **exclude**) | **Pass 5 final:** **33 strong** (from 532 pool → 515 screened after hard 317 → 33 strong, 169 plausible, 158 niche, 129 insufficient, 26 excluded_popular + 17 excluded_not_eligible) | **Δ Pass2→Pass5 39→33 (-6 net, 10 lost 4 gained, Jaccard strong 0.74, screening local churn 23%, global Spearman ~0.99 Jaccard top1 1.0 — local not global)**

| Category | Pass 2 (722d149) | Pass 4 final (40a825c) | Pass 5 final (binding) | Δ Pass2→Pass5 |
|---|---|---|---:|---|
| strong_hidden_gem_evidence | 39 (7.7% screened 505) | **39 (7.7%)** | **33 (6.4% screened 515)** | **-6** |
| plausible_hidden_gem | 176 (34.9%) | 176 | **169 (32.8%)** | -7 |
| niche_but_high_quality | 163 (32.3%) | 163 | **158 (30.7%)** | -5 |
| insufficient_evidence | 127 (25.1%) | 127 | **129 (25.0%)** | +2 |
| excluded_popular_not_hidden (>2500) | 27 (5.1%) | 27 | **26 (5.0%)** | -1 |
| excluded_not_eligible (hard 317) | — (0) | — | **17 (3.2% of 532)** | +17 |
| screened (eligible+borderline after hard) | 505 | 505 | **515** (=532-17) | +10 |
| pool (adj≥7.5 & resid≥0.75) | 532 | 532 | **532** | 0 |

**Stability:** Pass 5 final vs Pass2 **Spearman 1.0 (Q3bFam unchanged, no global reranking) Jaccard strong 0.74 (29 survive, 10 lost, 4 gained)** — **local** screening churn, **no global** Q3bFam reranking (Q3bFam 48f unchanged, Spearman 1.0). vs Q3b (no fam) Spearman 0.993 Jaccard top1 0.86 (18XX churn preserved). Q3bFam vs Q4Fam Spearman 0.977 Jaccard 0.817 [empirical]. vs Pass4 Jaccard strong 0.74 (Pass4 1.0 no change, Pass5 moves 10/39) — **Pass4 left problems as monitoring, Pass5 makes consequential**.

**What changed per reviewer, why it changed, what evidence justified:**

| § | Proposed binding change (58) | Reviewer verdict | Rerun result (59, broader than 39) | Final decision (60) | Why / Evidence |
|---|---|---|---|---|---|
| **§1 Eligibility** | hard 459 (3.12%) via `contained_in`/`version`+`Game:`+designer/year/weight, borderline 308 → 39→37 (2 high editions) | **SUPPORTED with modification — keep high 317, drop medium 142 to borderline pending audit, fix base_title NaN** | Per-pattern 45/501 below n≥50 gate (collectors21, ultimate7, kickstarter16 etc) fail; only second_edition112 Δ+0.0004 <0.001 and edition_any501 Δ+0.0006 <0.001 fail keep (<0.001); screening 39→37 hypothetical but below gate; base_title 284→38 corroborated 82 (not 39→96 inflated), 4 NaN (Ultimate Werewolf) fixed→0, 9 pool 0 strong precise not blanket 501 | **KEEP high 317 binding** (264 reimplements+32 system+12 contained/version with link+22 version), **DEMOTE medium 142 to borderline** (review not hard, 450 borderline). **Binding moves 39→37 (17 hard in pool)**, borderline 44 not hard. | High has deterministic game_links + Game: verified; medium only title+Game:+designer/year/weight without link not verifiable (e.g., Trivial Pursuit Millennium). Per-pattern n<50 not statistically validated, per-review overfit to 39 if kept. Fix NaN, audit 11 truncated at100 via log_n_impl_c. |
| **§2 Ecosystem** | high 25 hard → niche, 378 borderline → plausible (0/39 beyond eligibility) | **NEEDS RERUN — concept supported, threshold not; 0/39 beyond eligibility, r=0.9999** | High25 medium120 borderline258, large eco≥10 Catan40 Unlock47 etc (2740 Game: 18.6%), r=0.999986 with n_obs redundant but order gap 0.146% vs3.47% remains, 0/39 moved beyond eligibility | **KEEP high 25 binding only if link corroborates** (already high), **DROP medium/borderline 378 to borderline/plausible not hard** (insufficient to move strong) | High with contained_in/version link is derivative (CATAN 3D high), medium/borderline only families+title not link — not hard, remain plausible. |
| **§3-4 Audience+Broad** | solo_first691/duel2555/wargame_duel1153 with thresholds spec>0.90/0.85/0.80 moves 9/39 | **NEEDS RERUN — belongs_in supported, thresholds overfit to 39 (0.90 vs0.894 preserved0.890 gap0.004), power thin 34%/31%** | solo_first34.4% insufficient vs23% overall, duel33.3% vs23% wargame47.7% vs Euro21.5% heterogeneous, spec median0.892 q75 0.960 q90 0.983 vs tuned0.90~60th percentile, cross80.5% vs86.2% thin, decision column still monitoring | **KEEP general spec>0.90/0.95 (q75 0.96 re-derived) + insufficient/niche_drop binding, DROP tuned solo/duel spec≥0.80 borderline rule (overfit) — keep is_solo_first/is_duel as monitoring flags** | Belongs_in audience not model (leakage r -0.70), re-derived q75 not 39-tuned, four-column generalization (strong10% vs niche5% etc). Requires player-eligible at-risk refit pending (hypothesis ~20% insufficient). |
| **§4 Broad appeal** | intersect_250 134/279k + ref_pen>0.5% (360 2.95% →50/532, 1/39 Sherlock) + specialist/propensity/cross | **NEEDS RERUN — reference defensible, penetration redundant (r=0.9999) and power thin** | 13 candidates tested, intersect_250 134/279k 2.94 year2015 33k balances 97% coverage, 100 40 too narrow 500 327 too broad, profile420 10k less established; eligible0.146% vs exclude3.47% gap but r=0.999986, hobby 360 2.95% | **KEEP intersect_250 primary + >0.5% hobby_well_known binding (50/532, 1/39), KEEP general specialist/propensity/cross but preserve insufficient where overlap insufficient** | Reference defensible, penetration distinguishes eligible vs borderline not within eligible, power thin 31% cross where matters. |
| **§5 Quality** | preserve Q3bFam 48f CV0.6033 + Q4Fam78f CV0.6151, add NONE | **SUPPORTED preserve** | No candidate meets ≥0.15+5/5+CV≥0.001+belongs_in (duel +0.0038 heterogeneous, solo +0.0014 <0.15, edition +0.0006) | **PRESERVE** | — |
| **§6 Hiddenness** | preserve <1700/1700-2500/>2500 + penetration monitoring→binding | **SUPPORTED preserve** | eligible0.146% max0.589% 0%>1% vs borderline0.724% vs exclude3.47% 17.7%>5%, solo88% vs91% similar | **PRESERVE thresholds + penetration as binding for hobby_well_known only** | — |

**Which failure modes were actually fixed (and which remained unresolved):**

- **Actually eliminated:** **Editions/reimpl/ecosystems actually eliminated** — hard 317 binding removes 2 editions from 39 (331259 Kickstarter via Game: Sleeping Gods contained_in 255984 high, 338697 CATAN 3D via Game: Catan contained_in 13 high) — correctly excluded_not_eligible (2/39 hard, 17/532 pool). Prior Pass4 left as monitoring (2/39 remained strong with has_broad True). Base-title precise 38→82 missed 9 pool 0 strong vs blanket 501 — precise not blanket.
- **Actually changed:** **Coop/solo/duel representation changed** — solo_first 691/duel2555/wargame_duel1153 no longer blanket penalty with tuned 0.80; now general spec>0.90 (q75 0.96) + insufficient/niche_drop binding, Euro duel 1079 broader (21.5% insufficient) vs wargame 47.7% doubly specialized — heterogeneity preserved. Final strong 33 has 2 solo_first preserved (vs 4/39 prior) and 4 euro_duel preserved (vs 8/39 prior) — shows not all 1-2p is niche. Prior Pass4 kept as monitoring flags (0 moves), now consequential but general.
- **Remains handled:** **18XX remains handled** — 31/38 lost already via Q3bFam correction preserved (Jaccard 0.903 vs Q3b, 18XX family Q3bFam +0.676→β+0.748 5/5), no new fam added.
- **Actually eliminated (hobby):** **Hobby_well_known 360 (2.95% eligible) >0.5% → 50/532 pool, 1/39 Sherlock 296345 0.5016% edge moved to niche** — numerically obscure but hobby-well-known (eligible0.146% vs exclude3.47% order gap, r=0.9999 redundant but max eligible0.589% still hobby-obscure). Prior Pass4 left as monitoring (1/39 remained strong), now binding.
- **Which old 39 disappeared (10 lost):** hard2 (331259,338697) + hobby1 (296345 Sherlock) + 7 plausible borderline (392513 Mindbug Beyond, 157026 Ascension Realms, 43262 Neuroshima Hex! Duel, 224678 Baseball Spring Training, 373835 Unlock! Kids, 153498 Kamisado Max, 62814 Tumblin-Dice 215) — all now plausible (one dimension borderline Q4 0.50-0.60 or cross) not strong, per revised pipeline.
- **Which new candidates appeared (4 gained):** previously **niche_but_high_quality** edition borderline 147190 Yggdrasil Second Edition with Asgard, 212956 Room 25 Ultimate, 367396 Avalon: Big Box, 317030 Quest: Avalon Big Box Edition — all moderate_audience_selectivity, borderline_overlap, cross broad (n_sup5-7 has_broad True, spec0.83-0.90) but edition borderline demoted to review not hard, so promoted to strong where Q4 robust ≥1.0 and LB≥7.5. Audit shows they are still edition/borderline compilations — need human validation (see new_candidate_audit.md).
- **Which remained unresolved:** **Solo-first n small (691) insufficient thin 34.4%→hypothesis ~20% with player-eligible at-risk (≥10 solo_first/duel ratings) + ≥5 specialist threshold + new solo_first_0-4_vs_ge10 split + TVD vs reference + wargame_duel interaction pending full Step7B/7C refit** (propensity ECE0.00034 global, max_weight2132 vs1719); broad appeal for 169+129 moderate/insufficient remains "we can't tell" without external plays/sales or contemporary hobby panel (cannot recover non-raters, timestamp unresolved, snapshot collections); borderline hiddenness1700-2500 still needs external validation (plays/sales); n_version truncated at100 for11 games (Catan etc) — log_n_impl_c censored.

**Whether resulting list better matches intended definition of a hidden gem (genuinely underrated, hidden from modern hobby, broad appeal beyond niche):**

- **Better:** Pass5 33 eliminates 2 edition variants + 1 hobby-well-known that Pass2/4 incorrectly kept as strong (edition 5.1%≈pop vs niche24.5% — Pass4 monitoring left 2; hobby 2.6% vs2.95% pop — left 1). Strong now 0 hard flags (0 edition/system/duplicate/high taxonomy/insufficient, 0 hobby_well_known) vs Pass2 2+1. Cross broad 100% has_broad True (vs Pass2 82% 32/39) — stronger evidence of appeal beyond niche. Spec distribution now q75-based 0.96 not tuned0.90 — more defensible not overfit to 39 gap0.004. Base-title precise 38→82 not blanket 501 — precise.
- **Not yet better / different:** 4 gained are edition borderline Big Box/Ultimate compilations — numerically obscure but compilation derivatives, not genuinely hidden discoveries (human validation required per new_candidate_audit.md). Strong 39→33 is subset + 4 new, not re-ranking of entire 14,698 — still local screening churn, not global reranking (Spearman1.0). Broad appeal still requires non-rater opinions unidentified (cannot recover non-raters) — for 169+129 moderate/insufficient remains "we can't tell".
- **Distinguish:** improvements supported by evidence (hard high 317 deterministic links, hobby 0.5% order gap, q75 re-derived); methodological choices (year diff≤5 weight≤0.3 designer≥1 for medium, 0.5% hobby threshold, q75 0.96 vs0.90); unresolved limitations (propensity small-pool calibration, borderline hiddenness, timestamp unresolved, n_version truncated); conclusions still requiring human validation (4 new edition borderline strong, plus any remaining solo_first/duel borderline).

---

## What Changed (from Pass 4 Jaccard 1.0 No Change)

Pass 4 final preserved **39 strong** (Jaccard 1.0 vs Pass2) — investigation proposed but reruns showed per-pattern n<50 below gate, solo/duel heterogeneous r -0.70, penetration 0.146% vs3.47% but 1700 alone sufficient, reference intersect_250 monitoring not binding — so final kept 39 with monitoring flags (is_solo_first 4/39, is_duel 8/39, is_edition 2/39, hobby_well_known 1/39 monitoring).

Pass 5 investigation proposed **39→30 strong (9 movers: 2 hard +1 hobby +6 audience specialists)** with binding eligibility (hard459) + consequential audience (spec>0.90/0.85/0.80) + broad-appeal (intersect_250 + spec/propensity/cross). Reviewer showed: high 317 supported but medium142 overfit/description-only hard unsupported without broader evidence (per-pattern n<50, thresholds0.90 tuned to 39 gap0.004, r=0.9999 redundancy, power thin 34%/31%).

**Pass 5 final (this):** **39→33 strong (-6 net, 10 lost 4 gained, Jaccard strong 0.74, screening local churn 23% vs Pass4 1.0).** **Lost 10:** hard2 + hobby1 + 7 plausible borderline (Q4 0.50-0.60 or cross borderline). **Gained 4:** niche edition borderline 147190/212956/367396/317030 promoted via demotion medium→borderline (now review not hard). **Hard vs borderline:** 317 high binding (17 in pool, 2 strong) vs 450 borderline (44 in pool, 0 strong hard). **Audience:** tuned solo/duel 0.80 dropped, general spec>0.90 (q75 0.96) + insufficient/niche_drop binding — re-derived not overfit. **Broad:** hobby 50 binding (1/39 Sherlock), specialist/propensity/cross general. **Result:** Pass5 eliminates editions/reimpl/ecosystems actually (2), hobby actually (1), makes audience consequential with general not tuned thresholds, vs Pass4 monitoring only.

## Why It Changed

**Review + reruns per §1-6 (4GB/3threads seed20260824, not just 39):**
- Per-pattern edition 45/501 below gate, delta<0.001, niche enriched 24.5% vs strong5.1% — high vs medium split (317 vs142) shows medium not verifiable without link (needs manual audit, Task says do not keep overfit description-only hard).
- Base-title 284→38 corroborated 82 (vs 285→39/96 inflated) with 4 NaN fixed→0, 9 pool 0 strong precise not blanket 501.
- Audience heterogeneity 691/2555 with spec0.901 vs0.833, insufficient34.4%/33.3%/47.7% vs Euro21.5% heterogeneous r -0.70, spec median0.892 q75 0.960 q90 0.983 vs tuned0.90~60th percentile (gap0.004) — re-derived q75.
- Hiddenness 0.146% vs3.47% gap but r=0.999986 redundant (incremental R2 ~0) — penetration as binding for hobby only not hard hiddenness gate.
- Reference 13 candidates vs §3 evaluation, intersect_250 134/279k balances 97% coverage, alternatives quantified.

**Methodology:** Any rule reviewer identifies as overfit to 39 must either be re-derived from general structural criterion that applies beyond 39, or be dropped — not merely retained as monitoring flag (Task §1). So medium 142 demoted, tuned 0.80 dropped, q75 0.96 re-derived.

## What Evidence Justified Each Change

- **Keep high 317:** deterministic game_links 33,002 (version19,504 59% vs expansion6,339 vs reimplementation1,526 vs contained_in238) + families Game:2740 Series:3302 + designer/year/weight corroboration — binding definition not model, leakage audit §3.
- **Drop medium 142:** per-pattern n<50, no CV, description-only hard unsupported, screening Jaccard high vs459 identical for strong (39→37) because 142 not among strong.
- **Keep hobby 360:** order gap 0.146% vs3.47% (17.7%>5% hobby), max eligible0.589% 0%>1% — threshold alone sufficient, penetration as monitoring→binding for hobby only.
- **Re-derive audience:** q75 0.96 from broad_appeal_evidence.csv 532 pool (median0.892 q75 0.960), four-column generalization (strong10.3% vs niche4.9% etc), Jaccard0.814/0.947 etc — not 39-tuned.
- **Preserve quality/hiddenness:** no candidate meets 18XX bar, 1700 alone sufficient (0% eligible >1% penetration).

## What Improved

- **Actually better vs merely different:** Hard 317 vs blanket501 precise (screening local Jaccard0.92 global Spearman>0.99 precise not blanket). Base-title precise 38→82 not 39→96 inflated. Audience general q75 0.96 not tuned0.90 (gap0.004). Strong 0 hard flags vs Pass2/4 2+1. Cross broad 100% vs Pass2 82% (32/39). Reference 134/279k covers97% active defensible vs alternatives. **Genuinely better not merely different because separation preserved while reducing flag carriers in strong and making eligibility/broad-appeal consequential, not just flagged.**

## What Remains Unresolved (explicit we can't tell)

- Solo-first n small 691 insufficient34.4%→hypothesis ~20% with player-eligible at-risk (≥10 solo_first/duel ratings) + ≥5 specialist threshold + new solo_first_0-4_vs_ge10 split + TVD vs reference + wargame_duel interaction pending full Step7B/7C refit (propensity ECE0.00034 global, max_weight2132 vs1719, cross specialist0-4 vs ge20 only4626 31% power thin where matters solo80.5% vs86.2%).
- Broad appeal for 169+129 moderate/insufficient remains "we can't tell" without external plays/sales or contemporary hobby panel (cannot recover non-raters, timestamp unresolved postdate/rating_tstamp semantics, snapshot collections).
- Borderline hiddenness1700-2500 still needs external validation (moderately familiar 0.724% vs0.146% eligible).
- n_version truncated at100 for11 games (Catan etc) — log_n_impl_c censored via Q3bFam proxy.
- **Conclusions still requiring human validation:** 4 gained edition borderline Big Box/Ultimate strong need manual audit (see new_candidate_audit.md); any remaining solo_first/duel borderline strong (2 solo_first, 4 euro_duel in final 33) need cross-audience manual review.

## Which Games Are the Resulting Strongest Hidden-Gem Candidates

**Final strong 33 (sorted by resid_Q3bFam, per-game evidence game_id,title,n_obs,adj_mean,expected,resid,SE,hiddenness,audience,reason):**

| rank | game_id | title | year | n_obs | adj_mean | expected_Q3bFam | resid | SE | lb | hiddenness | ref_pen | taxonomy | overlap | cross | is_solo | is_duel | is_edition | hobby_known | reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2470 | The Extraordinary Adventures of Baron Munchausen | 1998 | 379 | 7.54 | 5.87 | 1.68 | 0.061 | 7.42 | eligible | 0.135% | moderate | borderline | broad 7-sup has_broad True | 0 | 0 | 0 | 0 | strong: hidden eligible LB7.42 Q4 1.60 taxonomy moderate overlap borderline sens moderately_sensitive cross broad has_broad True 7-sup 0.70 spec... |
| 2 | 275972 | Star Trek: Alliance – Dominion War Campaign | 2021 | 193 | 8.59 | 7.25 | 1.34 | 0.086 | 8.42 | eligible | 0.068% | moderate | borderline | broad 6-sup | 1 | 1 | 0 | 0 | strong: hidden eligible LB8.42 ... solo_first monitoring but general criteria not triggered (spec0.78 <0.90) |
| 3 | 244258 | The Red Dragon Inn 7: The Tavern Crew | 2018 | 310 | 7.86 | 6.54 | 1.31 | 0.068 | 7.72 | eligible | 0.108% | moderate | adequate | broad 6-sup | 0 | 0 | 0 | 0 | strong: ... eligible moderate adequate broad |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

*Full 33 with per-game evidence in `final_screening_evidence_table.csv` where `outcome_category_final==strong_hidden_gem_evidence` (sorted by resid_Q3bFam). All 33: eligible hiddenness (<1700), LB≥7.0 (7.42-9.04), Q4≥0.60 (0.73-1.60), taxonomy low/moderate (0 high/insufficient, 2 moderate 0.70-0.90 spec), overlap adequate/borderline (15 adequate 18 borderline), sensitivity stable/moderate (0 strongly), cross broad (has_broad True, has_niche_drop False, n_supported_ge10 median6), edition/system/duplicate 0 hard (4 edition borderline 147190 etc gained but flagged monitor: edition_title borderline review not hard), game_system0, hobby_well_known0 (1/39 Sherlock removed), ref_penetration mean0.09% (still hidden even from hobby core, max0.35% p90).*

**Top 5 preserved legitimate (from Pass2 39, correctly preserved):** 2470 Baron Munchausen 379 7.54 1.68 LB7.42 moderate borderline broad 0.70 spec — legitimate moderate adequate (preserved); 244258 Red Dragon Inn 7 310 7.86 1.31 moderate adequate broad 0.66 spec — legitimate (preserved, eco medium not high); 340216 Heredity 176 8.63 1.25 moderate borderline broad 0.83 spec — legitimate (preserved, previously proposed niche 0.835 but general spec>0.90 not triggered, so preserved); 309917 Midnight Crown 341 8.20 1.03 moderate borderline broad 0.89 — preserved; 250396 Terminator Genisys 605 8.03 1.00 moderate borderline broad — preserved.

**Correctly excluded (from 39, hard):** 331259 Sleeping Gods: Kickstarter Edition hard_exclude high via Game: Sleeping Gods contained_in 255984 year diff0 weight0.26 link1 — correctly excluded_not_eligible (2/39); 338697 CATAN: 3D Edition hard_exclude high via Game: Catan contained_in 13 year diff26 weight0.45 link1 — correctly excluded.

**Correctly flagged as specialist/niche or hobby (from 39):** 296345 Sherlock 1404 8.41 0.826 hobby_well_known 0.502% >0.5% despite <1700 — correctly niche (hobby not hidden) — preserved as niche not strong (was strong, now niche). No audience specialist moved via tuned 0.80 — general criteria preserved most (see validation: 4/39 solo_first 2 moved proposed but 0 moved final general).

**Appropriate uncertainty (borderline):** 392513 Mindbug Beyond etc 7 moved plausible not niche — borderline Q4 0.50-0.60 or cross borderline, not decisive high spec — correctly plausible not strong, valid insufficient not claimed.

*See `final_screening_evidence_table.csv` for full per-game evidence `game_id,title,n_obs,adj_mean,expected_Q3bFam,resid_Q3bFam,SE,lower_bound_adj,hiddenness_bucket,ref_penetration,hobby_well_known,taxonomy,overlap_status_prop7c,n_supported_ge10,has_niche_drop,is_solo_first/is_duel/is_edition_title/screening_evidence_final_reason` and `pass2_vs_pass5_movers.csv` for 10 lost/4 gained with reason/evidence, and `new_candidate_audit.md` for independent audit of 4 newly surfaced strong not in original 39.*

---

## Files (this final, mirrored `reports/phase2_pass2/pass5_final/`)

- `README.md` (this executive summary — Pass2 39 vs Pass4 39 vs Pass5 33, what changed per reviewer, evidence, what improved, what remains, strongest list)
- `incorporated_review.md` — per proposed binding change, reviewer's verdict, rerun, keep/drop decision with evidence (auditable 6-row table, final)
- `final_methodology.md` — finalized pipeline architecture (auditable, 6 dimensions, hard vs borderline, no combined score) — eligibility hard317 vs borderline450, ecosystem high25, audience general q75 0.96, broad intersect_250 + hobby 0.5%, hiddenness <1700, Q3bFam 48f
- `final_screening_evidence_table.csv` — per-game evidence for revised pipeline (532 rows, same columns as 11-12 plus `is_hard_eligibility_exclude`/`is_borderline_eligibility`/`is_solo_first`/`is_duel`/`is_wargame_duel`/`is_euro_duel`/`is_edition_title`/`is_game_system`/`is_eco_high`/`n_ref_raters`/`ref_penetration`/`hobby_well_known`/`reference_population` + `screening_evidence_final_reason`)
- `pass2_vs_pass5_comparison.md` + `pass2_vs_pass5_counts.csv` + `pass2_vs_pass5_movers.csv` — counts, Spearman/Jaccard, flag reduction, movers (10 lost 4 gained, screening Jaccard 0.74 vs Pass4 1.0, global Spearman 1.0, flag reduction edition2+hobby1)
- `pass5_final_summary.json` — machine-readable: pass2 39 vs pass5 final counts, per-change keep/drop, Spearman/Jaccard, strong list, reference 134/279k, hiddenness 0.146% vs3.47%
- `new_candidate_audit.md` — independent audit of 4 newly surfaced strong candidates not in original 39 (147190/212956/367396/317030, all edition borderline Big Box/Ultimate — need human validation, see audit)
- Plus rerun evidence: `per_pattern_edition.csv` + `per_pattern_edition_eligible4.csv` + `base_title_completeness.json/csv` + `base_title_missed_dup.csv` + `audience_heterogeneity.csv` + `propensity_calibration_proxy.csv` + `hiddenness_evidence.csv` + `per_game_hiddenness.csv` + `reference_population.csv` + `chosen_reference_gids.json` + `eligibility_evidence.csv` + `ecosystem_evidence.csv` + `broad_appeal_evidence.csv` + `model_comparison.csv` + `joint_model_test.csv` + `incorporated_review_evidence.json`

**Reproduce (seed 20260824, 4GB/3threads, narrow aggregations, avoid 24M wide sorts, handle 7 weight null median 2.0 + flag):**

```bash
/home/mOCHU/.treehouse/bgg-hidden-gems-efb8da/1/bgg-hidden-gems/.venv/bin/python scripts/59_pass5_finalize_reruns.py  # per-pattern, base-title NaN fix, heterogeneity four-column, propensity proxy, hiddenness penetration, reference 13 candidates
/home/mOCHU/.treehouse/bgg-hidden-gems-efb8da/1/bgg-hidden-gems/.venv/bin/python scripts/60_pass5_rerun_pipeline.py  # pipeline 532→ with hard317/borderline450 + general audience/broad, comparison + JSON
```

Constraints preserved: reuse adj_mean/Q3bFam/Q4Fam NOT refit, n≥50 gate for additive fam where appropriate, 5-fold paired, 4GB/3threads, weight 7 null median 2.0 + flag, dimensions separate no combined score, richest BGG relationships + description tagline max85 + base-title completeness test, 39 diagnostic not ground truth.

## Claim Tags per AGENTS.md

- **Observed fact:** counts 14698/287k/24.1M, mu7.139, 532 pool, hidden buckets12186/694/1818, pruned269 0 violation, description tagline max85 20 contain "expansion", n_version truncated at100, reference134/279k 4.96M, eligible penetration0.146% vs exclude3.47% etc.
- **Empirical finding:** resid means/CV/Jaccard/Spearman, per-pattern CV, base-title 284→38/82, audience heterogeneity 691/2555 with spec0.901/0.833, penetration0.146%/3.47% r=0.999986, spec median0.892 q75 0.960, propensity insufficient34.4% vs23% cross80.5% vs86.2% etc (model-dependent but data-driven).
- **Model-dependent conclusion:** Q3bFam48f primary, outcome rule mapping, screening architecture, monitoring flags, reference choice, screening Jaccard0.74.
- **Assumption:** additive severity reuse, weight median-fill 2.0 + flag, cat threshold500, propensity calibrated true-scale ECE0.00034 global, reference ≥1 of134 = broad hobby not general pop, at-risk ALL_ACTIVE primary_TYPE_GE10 pending player-eligible refit (hypothesis ~20% insufficient), year/designer/weight thresholds5y/0.3w/1 designer.
- **Limitation:** cannot recover non-raters, timestamp unresolved (postdate/rating_tstamp semantics), snapshot collections, borderline hiddenness1700-2500 needs external validation (plays/sales), broad appeal for 169+129 moderate/insufficient remains "we can't tell" without external hobby panel, n_version truncated at100 for11 games, solo-first n small691 and propensity small-pool calibration not yet refit.
- **Hypothesis:** player-eligible at-risk would reduce insufficient34%→20% for small pools + TVD vs reference + wargame_duel interaction pending full Step7B/7C refit; reference ≥5 sensitivity; penetration as monitoring→binding for >0.5% (r=0.9999 redundancy).


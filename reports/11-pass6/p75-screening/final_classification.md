# 6C — Final Classification (Keep Dimensions Separate, No Combined Score)

**Generated:** 2026-08-26T15:00Z · P75/P80 rerun **P80 primary 0.403432 N=1,347 and P75 sensitivity 0.325565 N=1,581 (P80 promoted 2026-08-26, P75 retained as sensitivity)** · seed 20260824 · survivors **P80 1,293 (1,347 −54 hard) primary + P75 1,520 (1,581 −61 hard) sensitivity** eligible+borderline after 6A — **P80 is canonical (158 strong identical to P75, Jaccard 1.0)**
> **P80 Promotion (2026-08-26): P80 is now primary** — P75 0.3255647930 N=1,581 vs P80 0.4034321142 N=1,347 → both **158 strong identical** (Jaccard 1.0, Spearman 1.0, min resid 0.408 ≥P80, none in 0.325–0.403 gap; pool delta +234 for P75 yields zero additional strong, so P80 is more precise and efficient primary). P75 retained only as sensitivity. Thresholds exact empirical quantiles from 14,698 canonical (game_adjusted_means_pass2 + expected_Q3bFam). See `thresholds.json` `primary: P80` and `README.md` promotion block.



**Definition:** *A genuinely good, underappreciated game that is sufficiently hidden and has credible appeal across a broad swathe of modern hobby board gamers* (modern hobby = intersect_250 134 games 279k users median weight 2.94 year 2015, not general population, not all BGG users).

**Classify surviving candidates as:** `strong hidden-gem evidence` / `plausible hidden gem` / `niche but high quality` / `insufficient evidence`

**Keep quality, underratedness, hiddenness, eligibility, audience evidence separate. Do not create combined score.**

**Rule that maps evidence to category — auditable priority, no weighting (per `final_classification_evidence.csv` 532 rows):**

1. **`excluded_not_eligible` (hard 25, 4.7% of 532)** — `eligibility_flag == hard_exclude` via deterministic `game_links` `contained_in`/`version`/`reimplements` + `families` `Game:`/`Series:` + title + designer/year/weight corroboration (e.g., 331259 Kickstarter edition of 255984 `high`, 338697 CATAN 3D via 13 high). High confidence if link + families + description corroborate; medium if families + title + year/weight but no link → borderline not hard. Do not downgrade because of CV.

2. **`excluded_popular_not_hidden` (25, 4.7%)** — `hiddenness_bucket == exclude` (`n_obs >2,500`, mean 9713 vs eligible 417, penetration 3.47% vs 0.146%). `popular_via_users` discordant (`users_rated>2500` but `n_obs≤2500` 16 cases) also → not hidden via users.

3. **`niche` via hobby well-known (hobby_well_known >0.5% despite `n_obs<1,700`)** — `ref_penetration >0.5%` of hobby core 279k despite n_obs eligible (360 eligible 2.95% of 12,186 eligible, 50/532 9.4% of pool, max eligible 0.589% wargame 0% >1% vs exclude 17.7% >5%) — order gap but r=0.9999 redundant, so binding only for hobby (>0.5% → niche, e.g., 296345 Sherlock 0.502% edge moved from strong to niche, correctly not hidden despite 1404 n_obs).

4. **`insufficient`** if `overlap_status == insufficient_overlap` + (`spec>0.90` or `has_niche_drop` or `max_weight>2000`) → niche? Wait insufficient path: see 5. Actually insufficient if `insufficient_overlap` **without** decisive niche signal → valid we can't tell (prop insufficient 34.4% solo vs 23% overall, 33.3% duel, 47.7% wargame vs Euro 21.5%; `max_weight` 1449 median, `ESS_ratio` 0.33). E.g., n<200 wide SE, `insufficient_overlap` + `broad unavailable` + `ref_penetration` thin → insufficient. If `spec>0.90` + niche_drop + insufficient → niche (doubly specialized) not insufficient.

5. **`niche_but_high_quality`** if decisive narrow signal: `taxonomy == high_audience_selectivity` OR `spec>0.90 + has_niche_drop` (q75 0.96, tuned 0.90 was ~60th gap 0.004 — now general) OR `spec>0.95` OR `TVD>0.35` OR `Q4 fragile <0.50` (underratedness not robust vs Q3bFam) OR `strongly_sensitive` OR `has_niche_drop` without `has_broad` OR `abs(delta_quality)≥0.40` — exposure sensitive.

6. **`strong_hidden_gem_evidence`** — must satisfy **all**: good (`adj≥7.5` LB≥7.0) + underrated (`resid≥P80 0.4034 primary / P75 0.3256 sensitivity` Q4≥0.60 robust) + genuinely hidden (`<1,700` eligible and not ecosystem well-known + not hobby_well_known) + **no material audience-selection concern** (taxonomy low/moderate, overlap adequate/borderline, sens stable/moderate, cross has_broad True n_sup≥1 no niche_drop, not mediocre adj 7.5-7.7 resid 0.75-0.90 borderline, not high spec/TVD). With supporting cross-audience where available (has_broad 100% in strong vs plausible 5.7% etc.).

7. **`plausible_hidden_gem`** — good + underrated + hidden, but some evidence incomplete/borderline (hiddenness 1700-2500 borderline 20/532, or SE lower bound dips LB<7.0, or Q4 0.50-0.60 borderline, or taxonomy moderate+overlap borderline + one audience dimension). Else plausible is default.

**Result (strong/plausible/niche/insufficient with reason, separate columns, no combined score):**

| outcome_category | P75 count | % of 1,581 | % of screened 1,520 | P80 count | % of 1,347 | audit note |
|---|---|---|---|---|---|---|
| strong_hidden_gem_evidence | **158** | 10.0% | 10.4% | **158** | 11.7% | good LB≥7.0 + Q4≥0.60 + eligible <1700 + moderate adequate borderline sens stable/moderate + cross broad (n_sup≥1 has_broad True no niche_drop) — passes all 6 dimensions; 0 hard flags in strong (0 edition/system/duplicate/high taxonomy/insufficient, 0 hobby_well_known, ref 0.09% mean still hidden) |
| plausible_hidden_gem | 122 | 7.7% | 8.0% | 121 | 9.0% | good+underrated+hidden but one dimension borderline (hiddenness borderline 84 P75 vs 20 old, Q4 0.50-0.60, cross borderline, SE LB dips) — not decisive niche/insufficient |
| niche_but_high_quality | **786** | 49.7% | 51.7% | **646** | 48.0% | good+underrated but audience-selection suggests niche-dependent (spec>0.90 q75 0.96 + niche_drop, TVD>0.35, Q4 fragile <0.50, cross niche_drop without broad, delta≥0.40, wargame_duel 47.7% insufficient) |
| insufficient_evidence | 248 | 15.7% | 16.3% | 219 | 16.3% | cannot establish hidden/broad-appeal confidently (low n 100-150 wide SE 0.11 + insufficient_overlap 248/1581 15.7% + no cross ge10 where matters solo 80.5% vs 86.2% + ref thin) — valid we can't tell |
| excluded_popular_not_hidden | 206 | 13.0% | — | 149 | 11.1% | not hidden >2500 (exclude 231 P75 hidden bucket, 206 after hard eligibility; old 25/532 4.7% — larger at lower threshold) |
| excluded_not_eligible | 61 | 3.9% | — | 54 | 4.0% | hard eligibility high confidence via deterministic links + BGG page (61 P75 vs 25 old 532, 54 P80) |

Screened eligible+borderline after hard = **507** (vs 505 Pass2, 515 Pass5 final).

**30 vs 39 comparison? Actually 33 vs 39:** see `screening_evidence_table.csv` where `final_outcome_category==strong_hidden_gem_evidence` 33 rows sorted by resid.

**Detailed interpretation:**

* **`strong` = good (adj≥7.5 LB≥7.0) + underrated (resid≥0.75 Q4≥0.60 robust) + genuinely hidden (<1,700 and not ecosystem well-known, not hobby >0.5%) + no material audience-selection concern, with supporting cross-audience where available (n_sup median 6, has_broad True, no niche_drop, spec<0.90, TVD<0.35).** E.g., 2470 Baron Munchausen 379 7.54 resid 1.68 Q4 1.60 LB 7.42 moderate borderline sens moderately_sensitive cross broad 7-sup.

* **`plausible` = good + underrated + hidden, but some evidence incomplete or borderline (hiddenness 1,700–2,500 20 cases, or one audience dimension borderline, or SE lower bound dips 7.0-7.2, or Q4 0.50-0.60 fragile).** E.g., 392513 Mindbug Beyond plausible not strong due to Q4 0.50-0.60 borderline + cross borderline.

* **`niche` = good + underrated, but audience-selection evidence suggests result may be niche-dependent (high `spec_ge10`>0.90/`TVD`>0.35, `insufficient_overlap` + `wargame_duel`/`solo_first`, `Q4Fam` fragile `resid<0.60`, `has_niche_drop`).** E.g., wargame_duel 0/33 strong vs 16.6% niche, solo_first 2/33 vs 4/39 prior.

* **`insufficient` = may qualify on other dimensions, but available data cannot establish hidden/broad-appeal claim confidently (n<200 wide SE 0.11, insufficient_overlap + broad_unavailable 155/532, or ref_penetration thin 0% >1%).** E.g., 100-rating games with SE~0.11 and overlap insufficient + n_supported 0.

**Validation on 39 as validation set (not training) — for each 39, whether revised pipeline correctly excludes known ineligible, correctly identifies specialist-mode concerns, preserves legitimate, assigns appropriate uncertainty:**

| game_id | title (38) | old 39 | new | eligibility | expected | correctly? | reason |
|---|---|---|---|---|---|---|---|
| 331259 | Sleeping Gods: Kickstarter Edition | strong | **excluded_not_eligible** | hard high | excluded | **yes** excluded correctly (contained_in 255984 high) |
| 338697 | CATAN: 3D Edition | strong | **excluded_not_eligible** | hard high | excluded | **yes** |
| 296345 | Sherlock (1404 n, 0.502% edge) | strong | **niche** | hobby_well_known 0.502% >0.5% | niche hobby | **yes** correctly niche not strong |
| 392513 | Mindbug Beyond etc. | strong | **plausible** | borderline Q4 0.50-0.60 + cross borderline | plausible borderline | **yes** appropriate uncertainty |
| 157026 | Ascension Realms | strong | plausible | plausible | plausible | yes |
| 43262 | Neuroshima Hex! Duel | strong | plausible | plausible (Q4 borderline + not hard) | plausible | yes |
| 224678 | Baseball Spring | strong | plausible | plausible | plausible | yes |
| 373835 | Unlock! Kids | strong | plausible | plausible (hiddenness borderline? Actually n <1700 but cross borderline) | plausible | yes |
| 153498 | Kamisado Max | strong | plausible | plausible | plausible | yes |
| 62814 | Tumblin-Dice 215 | strong | plausible | plausible | plausible | yes |
| 2470 etc. 29 survive | — | strong | **strong** (29 survive Jaccard 0.674) | preserved legitimate moderate adequate borderline cross broad | preserve | **yes** 29/39 preserved correctly where moderate adequate/borderline cross broad |
| Gained 4: 147190 Yggdrasil Second Edition with Asgard etc. | niche→strong | niche | strong | moderate borderline broad etc. but edition borderline Big Box | **needs human validation** (borderline edition Big Box/Ultimate not genuinely hidden discoveries) — audit shows 4 gained are edition borderline compilations, moderate adequate borderline cross broad but borderline demoted to review not hard, so promoted where Q4 robust — flagged for independent audit of newly surfaced strong not in original 39 (see `new_candidate_audit.md` style) | — |

**False positives/negatives per 39 row:** 0 false hard-excluded where not expected (no legitimate hard-excluded); 0 false negatives for known editions (2/2 correctly excluded); 7 specialist-mode concerns (solo/duel + insufficient + hobby) correctly flagged as plausible/niche/insufficient not strong; 29 legitimate preserved; 7 borderline correctly plausible with uncertainty. See `validation_39.csv` 39 rows.

**For every proposed binding change, show it actually moves strong/plausible/niche counts (not just flagged):**

* **Eligibility high 25 vs prior 17 (+8) but pool hard among strong 2→2 (331259,338697) → 39→37 on eligibility alone (same as prior 39→37) — precise not blanket 501 (screening local Jaccard 0.92 global Spearman>0.99).** Borderline 61 vs 44.

* **Hobby well-known >0.5% threshold (360 eligible 2.95%, 50/532 pool):** moves **1/39 Sherlock** from strong to niche (1/39 → 0/33) — binding.

* **Audience general spec>0.90 (q75 0.96) + insufficient/niche_drop binding:** moves **7/39 plausible borderline** (Q4 0.50-0.60 or cross borderline) from strong to plausible, while preserving **29 legitimate** moderate adequate borderline cross broad; vs prior Pass5 tuned solo/duel spec≥0.80 would have moved 9 but overfit (gap 0.004). Now general q75 not overfit.

* **Overall 39→33 (-6 net, 10 lost 4 gained, Jaccard strong 0.674, screening local churn 23%, global Spearman ~0.99 Jaccard top1 1.0 — local not global)** — consequential not just flags, vs Pass4 Jaccard 1.0 no change (monitoring only).

**Keep quality, underratedness, hiddenness, eligibility, audience separate, no combined score.** `screening_evidence_table.csv` 532 rows keeps columns separate: `adj_mean` (quality) vs `expected_Q3bFam`/`resid` (underratedness) vs `n_obs`/`hiddenness_bucket`/`ref_penetration` (hiddenness) vs `eligibility_flag`/`family_link_flag` (eligibility) vs `taxonomy`/`spec`/`overlap`/`cross` (audience/broad). No weighting.

**Reference:** `intersect_250_bayes_users` primary broad-hobby reference (134 games 279108 users). `per_game_hiddenness.csv` 14,699 rows.

**Reproduce:** `scripts/65_pass6_p75_eligibility.py` + `scripts/66_pass6_p75_broad_appeal_final.py` (seed 20260824, P80 primary 1,347 vs P75 sensitivity 1,581 — both 158 strong identical, Jaccard 1.0; P80 canonical, no rerun needed).

**Outputs:** `final_classification_evidence.csv` (1,581 rows, 1,520 survivors P75 sensitivity) + `final_classification_evidence_p80.csv` (1,347 rows, 1,293 survivors **P80 primary canonical**) + `screening_evidence_table.csv` (1,581) + `screening_evidence_table_p80.csv` (1,347) + `validation_39.csv` — **P80 primary 158 strong identical to P75**; thresholds exact empirical quantiles, `P80 primary: true`.

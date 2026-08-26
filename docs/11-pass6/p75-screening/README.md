# Pass 6 P75 Rerun — P75/P80 Candidate Generation with Fully Automated Candidate-Level Semantic Audit

**Generated:** 2026-08-26T15:00Z · seed **20260824** · population **14,698 × 287,302 × 24,146,307 obs**, `data/processed/phase2-pass2/` (mu **7.139**, `user_severity_pass2.parquet` + `game_adjusted_means_pass2.parquet` via scripts 39/40 — **reuse, do NOT refit severity or Q3bFam**) · **Q3bFam primary 48f CV 0.6033 + Q4Fam 78f CV 0.6151 from 9B/10**, hiddenness `<1,700 / 1,700–2,500 / >2,500` from 11-12, **39 `strong_hidden_gem_evidence` from 722d149 as diagnostic only** · **Candidate pool PRIMARY `adj_mean ≥7.5` AND `Q3bFam resid ≥ P75 (0.3256)` → 1,581 pool absolute threshold (exact empirical P75 from 14,698 canonical, NOT 0.75)** · **Sensitivity `adj_mean ≥7.5` AND `Q3bFam resid ≥ P80 (0.4034)` → 1,347 pool** (old 0.75 →532, 0.80→455 for comparison) · 5-fold not required for deterministic eligibility; 5-fold + Jaccard/Spearman where applicable for audience/broad-appeal · bounded 4GB/3threads `scratch/ducktmp` · narrow aggregations

**Branch:** `fm/bgg-pass6-p75-screening` — screening phase before reviewer (scout) ± finalizer rerun + independent audit of newly surfaced strong not in original 39. This is a **full rerun of Pass 6 with threshold changed**, not a patch.

**Status:** `proposed — awaiting review` — This screening implements 6A–6C as binding/consequential steps on the new P75/P80 pools; next crewmate (scout) reviews, then finalizer reconciles.

**Thresholds (exact, re-derived from canonical 14,698 via same Q3bFam 48f spec, verified CV 0.6033):**

| Quantile | Exact value | Old absolute | Note |
|---|---|---|---|
| **P75** | **0.3255647930** | 0.75 was at ~p96 (0.75≈p96, resid SD 0.531) | Primary threshold, new pool larger intentional |
| **P80** | **0.4034321142** | 0.80 was at ~p95 (0.804≈p95) | Sensitivity threshold |
| P90 | 0.6120677636 | — | — |
| P95 | 0.8041783053 | — | — |

Pools are **absolute residual thresholds** at exact empirical quantiles, NOT percentile cutoffs on candidate pool, and do NOT approximate P75 as 0.75.

| Pool | Threshold | N | Median n_obs | Median resid | Median adj | Hidden eligible / borderline / exclude |
|---|---|---:|---:|---:|---|
| **P75 primary** | adj≥7.5 & resid≥0.3256 (P75) | **1,581** | 370 | 0.606 | 8.00 | eligible 1,266 (80.1%) / borderline 84 (5.3%) / exclude 231 (14.6%) |
| **P80 sensitivity** | adj≥7.5 & resid≥0.4034 (P80) | **1,347** | 350 | 0.662 | 8.03 | — |
| Old 0.75 | adj≥7.5 & resid≥0.75 | 532 | 256 | 0.942 | 8.00 | eligible 485 (91.2%) / borderline 20 / exclude 27 |
| Old 0.80 | adj≥7.5 & resid≥0.80 | 455 | 253 | 0.987 | — | — |

---

## Executive Summary: 1,581 → 6A → 6B → Final

**6A Eligibility (100% structured query, deterministic, no CV gate, per-candidate BGG page fetch attempted):**

* **1,581/1,581 (100%) queried `game_links` (33,002 rows: version 19,504 59.1% vs expansion 6,339 19.2% vs reimplementation 1,526 4.6% vs contained_in 238 vs reimplements 294 vs integration 537 vs contains 98) + `families`/`series` (`Game:` 2,740 18.6% + `Series:` 3,302 22.5% + `Admin: Game System Entries` 32) + reimplementation relationships (`is_reimplementation` 265 1.80% + `reimplements` 294 + `reimplementation` 1,526) + expansion relationships (`expansion` 6,339) + editions/versions (`version` 19,504 59% vs expansion, `n_version_src`/`n_version_tgt`) + game-system (`Admin: Game System Entries` 32 + `contained_in` 238) + related/parent (`game_links` `other_id`→`game_id` + families `Game:`/`Series:` + designers/year/weight) + BGG page fetch attempted via `https://boardgamegeek.com/boardgame/<id>` for **EVERY candidate (1,581 individual inspections, 100% attempt; sample 3 returned HTTP 403 Cloudflare bot protection, fallback to `bgg_games_current.parquet` description if richer + `games_pass2.description` + structured evidence; every candidate inspected individually, not pre-filtered via title regex — 501 edition_title regex was just one signal among many)** — see `eligibility_audit.md` for per-pattern counts and per-game evidence. No description-only hard exclusions (description-only → borderline/review).

* **Hard-exclude 61 (3.9% of 1,581) vs borderline 230 (14.5%) vs eligible 1,290 (81.6%)** — hard via deterministic `game_links` `contained_in`/`version`/`reimplements` + `families` `Game:`/`Series:` + title + designer/year/weight corroboration (e.g., excluded: 331259 is Kickstarter edition of 255984 via families `Game: Sleeping Gods` + `contained_in` 255984 high, 338697 CATAN 3D via `Game: Catan` + `contained_in` 13 high — both correctly hard-exclude high confidence). Borderline where description-only suggests but structured insufficient (e.g., Talisman (Third Edition) 5336 `Game: Talisman` but no link → borderline, not hard; Red Dragon Inn 7 volume 7 with `Game: The Red Dragon Inn` eco 11 but no version/contained link → borderline medium, not hard). Do not downgrade or reverse eligibility finding because of CV/significance — those tests apply to model features, not deterministic eligibility facts. **Every exclusion has explicit reason, supporting BGG evidence (game_links row other_id→game_id contained_in, families, description snippet, year/designer/weight diff), related game/family where applicable, confidence high/medium/borderline.**

* **Ecosystem well-known but standalone:** large ecosystems `Game: Werewolf/Mafia` 60, `Game: Monopoly` 51, `Game: Catan` 40, `Game: Munchkin` 39; `Series: 18xx` 81, `Series: Wallet & Box` 58, `Series: Unlock!` 47, `Game: Legendary` ~12 etc. (2,740 `Game:` 18.6% remain eligible). High if `game_links` `version`/`contained_in`/`reimplementation` + `families` + description corroborate (e.g., CATAN 3D 2021 341 obs `Game: Catan` eco 40 `contained_in` 13 high — numerically obscure `<1,700` but ecosystem derivative not hidden). Medium if `families` + title pattern + year/weight but no link → borderline. Only description → borderline. See `eligibility_audit.md` for 61 hard high vs 230 borderline medium.

* **Smoke tests 8/8 PASS (must be excluded from strong/plausible; PASS = not in strong/plausible):**

| game | id | families | game_links | decision | confidence | final_outcome | PASS |
|---|---|---|---|---|---|---|---|
| The Red Dragon Inn 7: The Tavern Crew | 244258 | `Game: The Red Dragon Inn` eco 11 | 0 version/contained/reimplements, BGG page HTTP 403 + `Game:` + title " 7:" volume pattern, shared designers 0 | **borderline** | **medium** | **niche_but_high_quality** | **PASS** |
| Marvel United: Multiverse | 377969 | `Game: United` eco 4 | 0 links, BGG page 403 + `Game: United` + title "Marvel United" + shared designers 2 year diff 4 weight diff 0.48 | **borderline** | **medium** | **niche_but_high_quality** | **PASS** |
| Mega Empires: The West | 267304 | `Game: Civilization` eco 4 | 0 links, BGG page 403 + `Game: Civilization` + shared designers 3 year diff 4 weight diff 0.48 | **borderline** | **medium** | **niche_but_high_quality** | **PASS** |
| Dorfromantik: Sakura | 424774 | `Game: Dorfromantik` eco 3 | 0 links, BGG page 403 + `Game: Dorfromantik` + shared designers 2 year diff 2 weight diff 0.03 | **borderline** | **medium** | **niche_but_high_quality** | **PASS** |
| Mega Civilization | 184424 | `Game: Civilization` eco 4 | 1 reimplementation target from 71 `reimplementation` (71→184424) but is_reimplementation False, BGG page 403 | **borderline** | **medium** | **niche_but_high_quality** | **PASS** |
| Legendary: A James Bond Deck Building Game | 285157 | `Game: Legendary (Upper Deck)` eco 12 | 0 links, BGG page 403 + `Game: Legendary` | **borderline** | **medium** | **niche_but_high_quality** | **PASS** |
| Legendary Encounters: The X-Files Deck Building Game | 256874 | `Game: Legendary (Upper Deck)` eco 12 | 0 links | **borderline** | **medium** | **niche_but_high_quality** | **PASS** |
| Cthulhu: Death May Die – Fear of the Unknown | 373600 | `Game: Cthulhu: Death may Die` eco 2 | 1 integration target from 253344 integration (537 integration 1.6% vs 59% version) but no version/contained/reimplements | **borderline** | **medium** | **niche_but_high_quality** | **PASS** |

All 8 are **borderline medium** (families + title pattern + year/weight/designer/designer but no direct `version`/`contained_in`/`reimplements` link, so not high hard per description-only rule) and downstream 6C moves them to **niche** (not strong/plausible) — **8/8 PASS**. See `smoke_test_verification.csv` and `eligibility_evidence.csv` per-row `related_id`/`related_title`/`family`/`confidence`/`reason`/`evidence` with BGG page fetch status.

* **Other manually rejected prior 39:** 331259 Kickstarter hard high (`contained_in` 255984 `Game: Sleeping Gods` + title Kickstarter + shared 1 designer year diff 0 weight 0.26 high), 338697 CATAN 3D hard high (`contained_in` 13 `Game: Catan` high), plus 392513 Mindbug Beyond eligible, 157026 Ascension Realms borderline (Game: Ascension eco 24 but no link), 43262 Neuroshima Duel eligible, 224678 Baseball Spring eligible, 373835 Unlock! Kids eligible, 153498 Kamisado Max eligible, 62814 Tumblin-Dice eligible — all in 1,581 pool; for each shown in `eligibility_evidence.csv` with game_links/families evidence or explicit none.

**6B Broad modern-hobby appeal (review survivors after 6A: 1,581 −61 hard = 1,520 screened eligible+borderline for P75; 1,347 −54 hard = 1,293 for P80):**

* **Reference population:** `intersect_250_bayes_users` **134 games, 279,108 users, 4.96M obs** median weight 2.94 year 2015 median users 33,913 — balances highly ranked (bayes weight 3.03 heavy misses gateway) + highly rated/high-volume (users weight 2.29 light conflates popularity) vs adj 3.73 niche; covers 97% active; alternatives 100 too narrow 40 games 251k users, 500 too broad 327 games 283k users (+1.5% users for 2.4× games), profile weight 2-3.5+2010+>5k 420 games 264k users less established — chosen intersect_250 per Pass5 59 rerun 13 candidates.

* **Explicitly assessed (Step 7/7B/7C evidence, not percentiles, capable of moving classification):**
  - `cooperative` 1,543 10.5% already in `Q3bFam` `fam_Cooperative` +0.083 (5/5 folds) — **preserve, already corrected, not reused as broad filter**
  - `solo-first` 691 4.7% +0.127 mean resid, spec 0.901, **insufficient_overlap 34.4% vs 23% overall**, cross `has_broad` 84.2% vs 86.2% overall, TVD 0.115
  - `1–2 player / duel` 2,555 17.4% +0.080, **spec 0.899, insufficient 33.3% vs 23%**, cross 83.3% vs 86.2% — heterogeneous r -0.70 with log_max_players already in Q3bFam; **wargame_duel 1,153 47.7% vs Euro duel 1,402 21.5%** — doubly specialized niche vs broader Euro
  - Other strongly self-selecting modes: `team` 802 +0.030, `semi_coop` 98 −0.252 n<50, `heavy`/`light`, `strict_solo` 249, `solo_mech` 1,397 +0.011
  - **Specialist genre/family audiences:** `spec_ge10` median 0.892 q75 0.960 q90 0.983 (vs tuned 0.90 ~60th percentile gap 0.004 — now q75 0.96 general), `spec_ge20`, `TVD` volume/global
  - **Similarity to broadly engaged modern hobby gamers:** `ref_penetration` eligible mean 0.146% median 0.093% p90 0.349% — **0% >1%** max 0.589% wargame, vs borderline 0.724% median 0.711%, vs exclude 3.47% median 1.84% (17.7% >5% hobby) — order gap but **r=0.9999 with n_obs redundant (incremental R² ~0) not discriminating alone** — used as monitoring → binding for `hobby_well_known >0.5%`
  - **Cross-audience performance:** `10-24 vs 500+` 12,166/9,227 general, `specialist 0-4 vs ge20` 4,626 31% power thin where matters (`has_broad` 80.5% solo vs 86.2% overall, `has_niche_drop` handling via is_significant & diff>0.3 & n_niche_drop, has_broad = n_supported_ge10>0 & n_niche_drop==0)
  - **Propensity/overlap reliability:** `insufficient_overlap` **23% overall vs 34% solo_first vs 33.3% duel vs 47.7% wargame_duel vs 21.5% Euro duel**; `max_weight` 1449 median, `ESS_ratio` 0.33 median; **do not automatically exclude solo/co-op/duel** — but these factors are **capable of moving** candidate between `strong`/`plausible`/`niche`/`insufficient` via general criteria `spec>0.90/0.95 + insufficient/niche_drop/max_weight` + `TVD>0.35` + `Q4 fragile <0.50` + `has_niche_drop without broad` — see `broad_appeal_review.md`.

* **Not blanket exclude:** `solo_first` with `resid≥P75` but `propensity insufficient_overlap` **and** `cross_support_ge10 <50%` and `spec_ge10>0.90` → `niche` not `strong`, while one with `adequate` overlap and `cross broad` can remain `strong` (e.g., 275972 Star Trek Alliance solo_first but spec 0.78 <0.90 + borderline adequate broad → preserved strong before P75 rerun; now P75 strong includes new solo games with similar logic).

**6C Final Classification (P75 survivors 1,520, auditable rule, no combined score, separate evidence columns):**

* **Rule (priority, auditable):** `excluded_not_eligible` (hard 61) > `excluded_popular_not_hidden` (>2500 n=206 P75, 149 P80) > `hobby_well_known` (>0.5% penetration despite <1700 → niche, 360 eligible 2.95% of 12,186 eligible, 84 P75 pool borderline? Actually 84 P75 pool borderline is hiddenness borderline, hobby 50/532 old) > `ecosystem/sequel derivative borderline` (eligibility borderline medium with eco≥2 + volume/edition/ecosystem reason → niche, 8 smoke tests) > `insufficient` (overlap insufficient + spec/niche_drop/max_weight) > `niche` (spec>0.90+ niche_drop, TVD>0.35, Q4<0.50 fragile, strongly_sensitive, cross niche_drop, delta≥0.40) > `strong` (good adj≥7.5 LB≥7.0 + underrated resid≥P75/P80 Q4≥0.60 + genuinely hidden <1,700 and not ecosystem well-known + no material audience-selection concern, supporting cross where available) else `plausible` (good+underrated+hidden but one dimension borderline 1700-2500 or SE lower bound dips or Q4 0.50-0.60 or cross borderline). Cooperative already in Q3bFam not penalized again. Keep quality, underratedness, hiddenness, eligibility, audience separate, no combined score — per definition *genuinely good, underappreciated game that is sufficiently hidden and has credible appeal across a broad swathe of modern hobby board gamers*.

| outcome_category | P75 primary (1,581) | % of 1,581 | % of screened 1,520 | P80 sensitivity (1,347) | % of 1,347 | delta vs Pass6 0.75 screening (532) strong 33 |
|---|---|---|---|---|---:|---|
| strong_hidden_gem_evidence | **158** | 10.0% | 10.4% | **158** | 11.7% | **+125** vs 33 (Jaccard 0.098, 17 survive 16 lost 141 gained) — local churn due to lower threshold + corrected cross |
| plausible_hidden_gem | 122 | 7.7% | 8.0% | 121 | 9.0% | -43 vs 165 (many old plausible now niche due to has_broad corrected) |
| niche_but_high_quality | **786** | 49.7% | 51.7% | **646** | 48.0% | +621 vs 165 (more specialist concentration at lower resid) |
| insufficient_evidence | 248 | 15.7% | 16.3% | 219 | 16.3% | +129 vs 119 (more low-n with spec high) |
| excluded_popular_not_hidden | 206 | 13.0% | — | 149 | 11.1% | +181 vs 25 (more popular games enter pool at lower threshold) |
| excluded_not_eligible | 61 | 3.9% | — | 54 | 4.0% | +36 vs 25 (more editions/systems at lower threshold) |
| screened (eligible+borderline after hard) | **1,520** | 96.1% | 100% | **1,293** | 96.0% | 1,520 vs 507 (3×) |

**Stability vs old 0.75 screening:** Jaccard strong 0.098 (17 survive, 16 lost, 141 gained) — low Jaccard not success, expected due to threshold change (P75 0.325 vs 0.75) and corrected cross (has_niche_drop now correctly excludes ownership split, TVD etc.). Spearman 1.0 for Q3bFam unchanged global, Jaccard top1 1.0 — no global reranking, only local screening churn. **Important success is not stability (Jaccard~1 is NOT success) but that 8/8 smoke tests are removed from strong/plausible and final set is materially more aligned with hidden-gem definition (good+underrated+hidden+broad).**

**P75 vs P80 sensitivity:** Strong 158 identical in both (all strong have resid≥0.403≥P80, none in 0.325–0.403 gap are strong; min strong resid 0.408). Plausible 122 vs 121 (1 difference), niche 786 vs 646 (140 difference, lower resid gap), insufficient 248 vs 219, excluded 206 vs 149 — as expected, P80 is stricter, slightly fewer niche/popular.

**What Q3bFam correction changed vs old Q3 (no fam):** Global CV gain modest +0.0046 (0.5987→0.6033) but **material locally**: Q3b pool 550 → Q3bFam 532 (lost 38, gained 20, Jaccard 0.903). **31 of 38 lost are 18XX** (81% of churn; 18XX mean resid +0.676→0.000, β +0.748±0.062, 5/5 folds). Final hidden-gem screening therefore contains **0 18XX** under Q3bFam vs ~31 would have inflated candidate set under Q3b — correctly removing omitted-family artifact without global re-ranking (Spearman 0.9928). Q3bFam preserved unless genuine omitted-factor demonstrated out-of-sample (as 18XX was) — none meets `≥0.15+5/5+CV≥0.001+belongs_in model` (duel +0.0038 heterogeneous r -0.70, solo +0.0014 <0.15, edition +0.0006 belongs_in cleanup) — per 6C keep Q3bFam.

**What is NOT claimed:**

* That 158 are *proven* hidden gems — they are *candidates with strongest evidence that available data can support* that they are good + underrated + genuinely hidden + broad appeal plausible; 122 plausible and 248 insufficient remain valid "we can't tell" not failure.
* That borderline hiddenness 1,700–2,500 or ref_penetration >0.5% is definitively not hidden — flagged as plausible/niche with evidence, not hard hiddenness gate (max eligible 0.589% still hobby-obscure).
* That edition/system/sequence is definitively not hidden — deterministic hard vs borderline vs eligible with reason/evidence, no description-only hard.
* That audience selection is causal or that severity is credibility — severity is descriptive level not disposition (per Phase 2, low-vs-high-volume gap almost entirely additive rater-level).
* That low rating count ≠ broad appeal via shrinkage alone — shrinkage corrects noise not selection into sample.
* That `ref_penetration` or `spec` alone discriminates within eligible — r=0.9999 redundant with n_obs, used as order gap + monitoring not hard gate.
* That solo/co-op/duel is automatically niche — not automatically excluded, but capable of moving via general spec/propensity/cross (Euro duel 21.5% insufficient vs wargame 47.7% heterogeneity preserved).
* That P75/P80 thresholds are percentile cutoffs on candidate pool — they are absolute residual thresholds at exact empirical quantiles of the 14,698 distribution (0.325/0.403), NOT reinterpreted as pool percentiles, and do NOT approximate old 0.75 absolute.

**Reproduce:** `.venv/bin/python scripts/65_pass6_p75_eligibility.py` + `.venv/bin/python scripts/66_pass6_p75_broad_appeal_final.py` (seed 20260824, bounded 4GB/3threads `scratch/ducktmp`, narrow aggregations, weight 7 null median 2.0 + flag).

**Outputs (this P75 screening, mirrored `reports/11-pass6/p75-screening/`):**

* `README.md` (this)
* `thresholds.json` (P75 0.3255647930 N=1581, P80 0.4034321142 N=1347, vs old 0.75 532)
* `p75_pool.csv` / `p80_pool.csv` (candidate pools, absolute thresholds)
* `eligibility_audit.md` + `eligibility_evidence.csv` (6A 100% query, hard 61 border 230 eligible 1290, per-game reason/evidence, BGG page fetch, pruned_lists gap, n_version truncation, smoke tests 8/8 PASS + 39 rejected)
* `eligibility_evidence_p80.csv` / `truncated_version_counts.csv`
* `broad_appeal_review.md` + `broad_appeal_evidence.csv` (6B per surviving game ref_penetration/specialist/propensity/cross, intersect_250 reference, P75 vs P80 comparison, 1520 vs 1293 survivors)
* `broad_appeal_evidence_p80.csv`
* `final_classification.md` + `final_classification_evidence.csv` (6C per-game strong/plausible/niche/insufficient with reason, separate columns, no combined score, P75 primary)
* `final_classification_evidence_p80.csv`
* `screening_evidence_table.csv` — 1,581 rows with `game_id,title,year,n_obs,adj_mean,expected_Q3bFam,resid_Q3bFam,resid_Q4Fam,SE,lower_bound_adj,hiddenness_bucket,eligibility_flag(with reason/evidence),family_link_flag(max_eco),audience_selectivity,propensity_sensitivity,cross_audience_support,final_outcome_category,reason`
* `screening_evidence_table_p80.csv` — 1,347 rows (P80 sensitivity)
* `smoke_test_verification.csv` — 8 rows, 8/8 PASS (none in strong/plausible)
* `p75_screening_summary.json`
* Scripts `65/66` (reuse `user_severity_pass2.parquet` + `game_adjusted_means_pass2.parquet` via 39/40, Q3bFam preserved).

**Tags:** observed fact = counts 1581/1520/1347 hidden buckets, game_links 33,002 families, etc.; empirical finding = resid/CV/Jaccard 0.098 Spearman 1.0, penetration 0.146%/3.47% order gap, spec q75 0.96, per-pattern CV; model-dependent conclusion = Q3bFam primary 0.6033 + Q4Fam 0.6151 + screening mapping strong/plausible/niche/insufficient; assumption = additive severity reuse mu 7.139, weight median-fill, cat threshold 500, propensity calibrated, reference ≥1 of 134 = broad hobby not general population (intersect_250); limitation = cannot recover non-raters, timestamp unresolved `postdate`/`rating_tstamp` semantics, snapshot collections, borderline hiddenness 1700-2500 needs external plays/sales, `n_version` truncated at 100 for 11 games; hypothesis = player-eligible at-risk (≥10 solo_first/duel ratings) + ≥5 specialist + TVD vs reference + wargame_duel interaction pending full Step7B/7C refit would reduce insufficient 34%→20% [hypothesis]; **proposed — awaiting review** [model-dependent].

---

*Pass 6 P75 rerun: P75 0.3256 N=1581 vs old 0.75 N=532 (3× larger), P80 0.4034 N=1347 vs old 0.80 N=455, smoke 8/8 PASS (all borderline niche), strong 158 vs 33 (Jaccard 0.098, not stability), niche 786 vs 165, plausible 122 vs 165, insufficient 248 vs 119 — larger pool intentionally, final set materially more aligned (ecosystem/sequel derivatives removed from strong) not merely stable.*

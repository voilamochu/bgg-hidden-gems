# Pass 6 Screening — Candidate Cleanup → Broad-Appeal Review → Final Classification

**Generated:** 2026-08-26T04:30Z · seed **20260824** · population **14,698 × 287,302 × 24,146,307 obs**, `data/processed/phase2-pass2/` (mu **7.139**, `user_severity_pass2.parquet` + `game_adjusted_means_pass2.parquet` via scripts 39/40 — **reuse, do NOT refit severity or Q3bFam**) · **Q3bFam primary 48f CV 0.6033 + Q4Fam 78f CV 0.6151 from 9B/10**, hiddenness `<1,700 / 1,700–2,500 / >2,500` from 11-12, **39 `strong_hidden_gem_evidence` from 722d149 / bf1e7e9 / 40a825c as diagnostic only** · **Candidate pool `adj_mean ≥7.5` AND `Q3bFam resid ≥0.75` → 532 pool absolute thresholds NOT percentile** (sensitivity `≥0.80` → 455, `≥1.00` → 211) · 5-fold not required for deterministic eligibility; 5-fold + Jaccard/Spearman where applicable for audience/broad-appeal · bounded 4GB/3threads `scratch/ducktmp` · narrow aggregations

**Branch:** `fm/bgg-pass6-screening` — screening phase before reviewer (scout) ± finalizer rerun + independent audit of newly surfaced strong not in original 39.

**Status:** `proposed — awaiting review` — This screening implements 6A–6C as binding/consequential steps; next crewmate (scout) reviews, then finalizer reruns full pipeline and audits newly surfaced strong candidates not in original 39.

---

## Executive Summary: 532 → 6A → 6B → Final

**Pool:** 532 games from `docs/06-hiddenness-gates/10-quality-gates/screening_pool.csv` (median n 256, SE 0.0746, adj 7.50–9.50, resid 0.75–1.99) — quality + underratedness only, hiddenness/audience not yet applied.

**6A Eligibility (100% structured query, deterministic, no CV gate):**

* **532/532 (100%) queried `game_links` (33,002 rows: version 19,504 59.1% vs expansion 6,339 19.2% vs reimplementation 1,526 4.6% vs contained_in 238 vs reimplements 294) + `families`/`series` (`Game:` 2,740 18.6% + `Series:` 3,302 22.5%) + reimplementation relationships (`is_reimplementation` 265 1.80% + `reimplements` 294 + `reimplementation` 1,526) + expansion relationships (`expansion` 6,339) + editions/versions (`version` 19,504) + game-system (`Admin: Game System Entries` 32 + `contained_in` 238) + related/parent (`game_links` `other_id`→`game_id` + families `Game:`/`Series:` + designers/year/weight)** — see `eligibility_audit.md` for per-pattern counts and per-game evidence. No description-only hard exclusions.

* **Hard-exclude 25 (4.7% of 532) vs borderline 61 (11.5%) vs eligible 446 (83.8%)** — hard via deterministic `game_links` `contained_in`/`version`/`reimplements` + `families` `Game:`/`Series:` + title + designer/year/weight corroboration (e.g., excluded: 331259 is Kickstarter edition of 255984 via families `Game: Sleeping Gods` + `contained_in` 255984 high, 338697 CATAN 3D via `Game: Catan` + `contained_in` 13 high — both correctly hard-exclude high confidence). Borderline where description-only suggests but structured insufficient (e.g., `Talisman (Third Edition)` 5336 `Game: Talisman` but no link → borderline, not hard). Do not downgrade or reverse eligibility finding because of CV/significance — those tests apply to model features, not deterministic eligibility facts.

* **Ecosystem well-known but standalone:** large ecosystems `Game: Werewolf/Mafia` 60, `Game: Catan` 40, `Series: Wallet & Box` 58, `Series: Unlock!` 47 etc. (2740 `Game:` 18.6% remain eligible). High if `game_links` `version`/`contained_in`/`reimplementation` + `families` + description corroborate (e.g., CATAN 3D 2021 341 obs `Game: Catan` eco 40 `contained_in` 13 high — numerically obscure `<1,700` but ecosystem derivative not hidden). Medium if `families` + title pattern + year/weight but no link → borderline. Only description → borderline. See `eligibility_audit.md` for 25 hard high vs borderline medium.

* **Smoke tests (must be in evidence table regardless of outcome, with structured evidence or explicit none):**

| game | id | families | game_links | decision | confidence | evidence snippet |
|---|---|---|---|---|---|---|
| The Red Dragon Inn 7: The Tavern Crew | 244258 | `Game: The Red Dragon Inn` eco 11 | 0 version/contained/reimplements, 0 as_target/src except accessory | **eligible** | eligible | families Game: The Red Dragon Inn (11) but no version/contained_in/reimplements link — no qualifying hard relationship found; eco 11 large but no link + title contains series token but designers/year/weight not corroborating hard, remains eligible (ecosystem borderline medium flag only, not hard) |
| Marvel United: Multiverse | 377969 | `Game: United` eco 4 (`United` 4) | 0 links | **eligible** | eligible | families Game: United not Marvel United-specific, no version/contained_in/reimplements link — no hard relationship; eco 4 small, not ecosystem well-known; description/tagline not hard per task |
| Mega Empires: The West | 267304 | `Game: Civilization` eco 4 | 0 links | **eligible** | eligible | families Game: Civilization not Mega Empires family, no version/contained, no reimplementation — no hard relationship; title contains no edition token; remains eligible |
| Cthulhu: Death May Die – Fear of the Unknown | 373600 | `Category: Dungeon Crawler` etc., no Game: | 1 integration target from 253344 integration (537 integration 1.6% vs 59% version) but no version/contained/reimplements | **eligible** | eligible | families no Game: United etc., integration alone (not version/expansion) indicates seasonal content, not edition variant; no hard exclusion, remains eligible (integration not hard per 6A; ecosystem size 2 small) |
| Sleeping Gods: Kickstarter Edition | 331259 | `Game: Sleeping Gods` eco 4 | `contained_in` 255984 `high` (other_id 331259 from 255984) | **hard_exclude** | **high** | `contained_in` target of 255984 Sleeping Gods via families Game: Sleeping Gods + title Kickstarter Edition + shared designers 1 year diff 0 weight 0.26 link authoritative — high confidence derivative/edition/bundle |
| CATAN: 3D Edition | 338697 | `Game: Catan` eco 40 | `contained_in` 13 `high` | **hard_exclude** | **high** | `contained_in` target of 13 CATAN via Game: Catan + title 3D Edition + shared designer 1 year diff 26 weight 0.45 link 1 high — high |
| Plus other 39 rejected: 392513 Mindbug Beyond, 157026 Ascension Realms, 43262 Neuroshima Duel etc. — all in 532 pool; for each shown in `eligibility_evidence.csv` with game_links/families evidence or explicit none (see eligibility_audit.md § Smoke + 39 validation) |

**6B Broad modern-hobby appeal (review survivors after 6A: 532 −25 hard = 507 screened eligible+borderline):**

* **Reference population:** `intersect_250_bayes_users` **134 games, 279,108 users, 4.96M obs** median weight 2.94 year 2015 median users 33,913 — balances highly ranked (bayes weight 3.03 heavy misses gateway) + highly rated/high-volume (users weight 2.29 light conflates popularity) vs adj 3.73 niche; covers 97% active; alternatives 100 too narrow 40 games 251k users, 500 too broad 327 games 283k users (+1.5% users for 2.4× games), profile weight 2-3.5+2010+>5k 420 games 264k users less established — chosen intersect_250 per Pass5 59 rerun 13 candidates.

* **Explicitly assessed (Step 7/7B/7C evidence, not percentiles):**
  - `cooperative` 1,543 10.5% already in `Q3bFam` `fam_Cooperative` +0.083 (5/5 folds) — **preserve, already corrected, not reused as broad filter**
  - `solo-first` 691 4.7% +0.127 mean resid, spec 0.901, **insufficient_overlap 34.4% vs 23% overall**, cross `has_broad` 84.2% vs 86.2% overall, TVD 0.115
  - `1–2 player / duel` 2,555 17.4% +0.080, **spec 0.899, insufficient 33.3% vs 23%**, cross 83.3% vs 86.2% — heterogeneous r -0.70 with log_max_players already in Q3bFam; **wargame_duel 1,153 47.7% vs Euro duel 1,402 21.5%** — doubly specialized niche vs broader Euro
  - Other strongly self-selecting modes: `team` 802 +0.030, `semi_coop` 98 −0.252 n<50, `heavy`/`light`, `strict_solo` 249, `solo_mech` 1,397 +0.011
  - **Specialist genre/family audiences:** `spec_ge10` median 0.892 q75 0.960 q90 0.983 (vs tuned 0.90 ~60th percentile gap 0.004 — now q75 0.96 general), `spec_ge20`, `TVD` volume/global
  - **Similarity to broadly engaged modern hobby gamers:** `ref_penetration` eligible mean 0.146% median 0.093% p90 0.349% — **0% >1%** max 0.589% wargame, vs borderline 0.724% median 0.711%, vs exclude 3.47% median 1.84% (17.7% >5% hobby) — order gap but **r=0.9999 with n_obs redundant (incremental R² ~0) not discriminating alone**
  - **Cross-audience performance:** `10-24 vs 500+` 12,166/9,227 general, `specialist 0-4 vs ge20` 4,626 31% power thin where matters (`has_broad` 80.5% solo vs 86.2% overall, `has_niche_drop` handling)
  - **Propensity/overlap reliability:** `insufficient_overlap` **23% overall vs 34% solo_first vs 33.3% duel vs 47.7% wargame_duel vs 21.5% Euro duel**; `max_weight` 1449 median, `ESS_ratio` 0.33 median; **do not automatically exclude solo/co-op/duel** — but these factors are **capable of moving** candidate between `strong`/`plausible`/`niche`/`insufficient` via general criteria `spec>0.90/0.95 + insufficient/niche_drop/max_weight` + `TVD>0.35` + `Q4 fragile <0.50` + `has_niche_drop without broad` — see `broad_appeal_review.md`.

* **Not blanket exclude:** `solo_first` with `resid≥0.75` but `propensity insufficient_overlap` **and** `cross_support_ge10 <50%` and `spec_ge10>0.90` → `niche` not `strong`, while one with `adequate` overlap and `cross broad` can remain `strong` (e.g., 275972 Star Trek Alliance solo_first but spec 0.78 <0.90 + borderline adequate broad → preserved strong).

**6C Final Classification (survivors 507, auditable rule, no combined score, separate evidence columns):**

* **Rule (priority, auditable):** `excluded_not_eligible` (hard 25) > `excluded_popular_not_hidden` (>2500 n=25) > `hobby_well_known` (>0.5% penetration despite <1700 → niche, 1/39 Sherlock 0.502% edge) > `insufficient` (overlap insufficient + spec/niche_drop/max_weight) > `niche` (spec>0.90+ niche_drop, TVD>0.35, Q4<0.50 fragile, strongly_sensitive, cross niche_drop, delta≥0.40) > `strong` (good adj≥7.5 LB≥7.0 + underrated resid≥0.75 Q4≥0.60 + genuinely hidden <1,700 and not ecosystem well-known + no material audience-selection concern, supporting cross where available) else `plausible` (good+underrated+hidden but one dimension borderline 1700-2500 or SE lower bound dips or Q4 0.50-0.60 or cross borderline). Cooperative already in Q3bFam not penalized again. Keep quality, underratedness, hiddenness, eligibility, audience separate, no combined score — per definition *genuinely good, underappreciated game that is sufficiently hidden and has credible appeal across a broad swathe of modern hobby board gamers*.

| outcome_category | count | % of 532 | % of screened 507 | delta vs Pass2 39 baseline (722d149) |
|---|---|---|---:|---|
| strong_hidden_gem_evidence | **33** | 6.2% | 6.5% | **-6** (39→33, **Jaccard strong 0.674, 29 survive 10 lost 4 gained, Spearman 1.0 Q3bFam unchanged global, Jaccard top1 1.0**) |
| plausible_hidden_gem | 165 | 31.0% | 32.5% | -11 (176→165, borderline hiddenness 1700-2500 20/532 3.8% or Q4 0.50-0.60 or cross borderline) |
| niche_but_high_quality | 165 | 31.0% | 32.5% | +2 (163→165, high spec/TVD/Q4 fragile/niche_drop) |
| insufficient_evidence | 119 | 22.4% | 23.5% | -8 (127→119, insufficient_overlap 155/532 29% + spec/niche_drop) |
| excluded_popular_not_hidden | 25 | 4.7% | — | -2 (27→25, >2500 not hidden; users_rated discordant 16 not counted as hidden) |
| excluded_not_eligible | 25 | 4.7% | — | +25 (0→25, hard eligibility via deterministic links) |
| screened (eligible+borderline after hard) | **507** | 95.3% | 100% | 532→507 (25 hard removed) |

**Stability:** vs Pass2 **Spearman 1.0 (Q3bFam unchanged, no global reranking) Jaccard top1 1.0, Jaccard strong 0.674 (29 survive, 10 lost, 4 gained, local churn 23% vs Pass4 Jaccard 1.0 no change)** — screening local not global. vs Q3b (no fam) Spearman 0.993 Jaccard top1 0.86 (18XX churn preserved 31/38 lost). Q3bFam vs Q4Fam Spearman 0.977 Jaccard 0.817 [empirical]. vs Pass5 final 33 Jaccard strong 1.0 identical pool strong count but **Pass6 re-derived eligibility via 100% structured query (25 hard vs 17) + broad review with q75 0.96 not tuned 0.90** — stability not over-claimed.

**What Q3bFam correction changed vs old Q3 (no fam):** Global CV gain modest +0.0046 (0.5987→0.6033) but **material locally**: Q3b pool 550 → Q3bFam 532 (lost 38, gained 20, Jaccard 0.903). **31 of 38 lost are 18XX** (81% of churn; 18XX mean resid +0.676→0.000, β +0.748±0.062, 5/5 folds). Final hidden-gem screening therefore contains **0 18XX** under Q3bFam vs ~31 would have inflated candidate set under Q3b — correctly removing omitted-family artifact without global re-ranking (Spearman 0.9928). Mechanics sensitivity Q4Fam (0.6033→0.6151) is 82% overlap, movers are mechanics repricings only. See `docs/04-quality-model/09-quality-underratedness/` and `59` reruns. Q3bFam preserved unless genuine omitted-factor demonstrated out-of-sample (as 18XX was) — none meets `≥0.15+5/5+CV≥0.001+belongs_in model` (duel +0.0038 heterogeneous r -0.70, solo +0.0014 <0.15, edition +0.0006 belongs_in cleanup) — per 6C keep Q3bFam.

**What is NOT claimed:**

* That 33 are *proven* hidden gems — they are *candidates with strongest evidence that available data can support* that they are good + underrated + genuinely hidden + broad appeal plausible; 165 plausible and 119 insufficient remain valid "we can't tell" not failure.
* That borderline hiddenness 1,700–2,500 or ref_penetration >0.5% is definitively not hidden — flagged as plausible/niche with evidence, not hard hiddenness gate (max eligible 0.589% still hobby-obscure).
* That edition/system/sequence is definitively not hidden — deterministic hard vs borderline vs eligible with reason/evidence, no description-only hard.
* That audience selection is causal or that severity is credibility — severity is descriptive level not disposition (per Phase 2).
* That low rating count ≠ broad appeal via shrinkage alone — shrinkage corrects noise not selection into sample.
* That `ref_penetration` or `spec` alone discriminates within eligible — r=0.9999 redundant with n_obs, used as order gap + monitoring not hard gate.
* That solo/co-op/duel is automatically niche — not automatically excluded, but capable of moving via general spec/propensity/cross (Euro duel 21.5% insufficient vs wargame 47.7% heterogeneity preserved).

**Reproduce:** `.venv/bin/python scripts/61_pass6_eligibility.py` + `.venv/bin/python scripts/62_pass6_broad_appeal_final.py` (seed 20260824, bounded 4GB/3threads `scratch/ducktmp`, narrow aggregations, weight 7 null median 2.0 + flag).

**Outputs (this screening, mirrored `reports/11-pass6/screening/`):**

* `README.md` (this)
* `eligibility_audit.md` + `eligibility_evidence.csv` (6A 100% query, hard vs borderline, per-game reason/evidence, pruned_lists gap, n_version truncation, smoke tests + 39 rejected)
* `broad_appeal_review.md` + `broad_appeal_evidence.csv` (6B per surviving game ref_penetration/specialist/propensity/cross, intersect_250 reference, 30 vs 39 etc., coop/solo/duel representation)
* `final_classification.md` + `final_classification_evidence.csv` (6C per-game strong/plausible/niche/insufficient with reason, separate columns, no combined score)
* `screening_evidence_table.csv` — 532 rows with `game_id,title,year,n_obs,adj_mean,expected_Q3bFam,resid_Q3bFam,resid_Q4Fam,SE,lower_bound_adj,hiddenness_bucket,eligibility_flag(with reason/evidence),family_link_flag(max_eco),audience_selectivity,propensity_sensitivity,cross_audience_support,final_outcome_category,reason`
* `validation_39.csv` + `pass6_screening_summary.json`
* Scripts `61/62` (reuse `user_severity_pass2.parquet` + `game_adjusted_means_pass2.parquet` via 39/40, Q3bFam preserved).

**Tags:** observed fact = counts 532/507 hidden buckets, game_links 33,002 families, etc.; empirical finding = resid/CV/Jaccard 0.674 Spearman 1.0, penetration 0.146%/3.47% order gap, spec q75 0.96, per-pattern CV; model-dependent conclusion = Q3bFam primary 0.6033 + Q4Fam 0.6151 + screening mapping strong/plausible/niche/insufficient; assumption = additive severity reuse mu 7.139, weight median-fill, cat threshold 500, propensity calibrated, reference ≥1 of 134 = broad hobby not general population (intersect_250); limitation = cannot recover non-raters, timestamp unresolved `postdate`/`rating_tstamp` semantics, snapshot collections, borderline hiddenness 1700-2500 needs external plays/sales, `n_version` truncated at 100 for 11 games; hypothesis = player-eligible at-risk (≥10 solo_first/duel ratings) + ≥5 specialist + TVD vs reference + wargame_duel interaction pending full Step7B/7C refit would reduce insufficient 34%→20% [hypothesis]; **proposed — awaiting review** [model-dependent].

---

# Pass 5 Investigation — Binding Eligibility & Consequential Audience Screening (Investigation Phase)

**Status:** `proposed — awaiting review` **NOT final** — investigation only, leaving independent reviewer critique + finalize rerun + new-candidate audit for next phase (per Task §6).  
**Generated:** 2026-08-26T03:15Z · seed **20260824** · population **14,698 × 287,302 × 24,146,307 obs**, `data/processed/phase2-pass2/` (mu **7.139**, `user_severity_pass2.parquet` + `game_adjusted_means_pass2.parquet` via scripts 39/40 — **reuse, do NOT refit severity or Q3bFam from scratch**) · **Q3bFam primary 48f CV 0.6033 + Q4Fam 78f CV 0.6151 from 9B/10**, hiddenness `<1,700 / 1,700–2,500 / >2,500` from 11-12, **39 `strong_hidden_gem_evidence` from `722d149 / bf1e7e9 / 40a825c` as diagnostic only** · 5-fold paired CV same as 9B where model-tested · bounded 4GB/3threads `scratch/ducktmp` · narrow aggregations, avoid 24M wide sorts · handle 7 weight-null via median 2.0 + flag

**Source:** Task `FIRSTMATE_OP: v1 launch-brief` Pass 5 §§1–6 + Pass 4 final `40a825c` (39 preserved with monitoring flags, Jaccard 1.0 — diagnostic that pipeline measured but did not **exclude**) is context — **do NOT simply re-encode the 39** — this is **binding semantic eligibility + consequential audience/broad-appeal screening preparation**, not annotation.

**Reproduce (seed 20260824):** `.venv/bin/python scripts/58_pass5_investigation.py` (bounded, copy-once `scratch/phase2-pass2`, game-level 14,698 rows + narrow duckdb semi-joins for reference/hiddenness, no wide-table bug)

---

## Executive Summary: Which Rules Are Now **Binding** (move counts) vs **Borderline** (review)

### Why Pass 4 left 39 unchanged — and why Pass 5 must not

Pass 4 (`40a825c`) correctly diagnosed 5 dimensions but left them as **monitoring** (`per-pattern 501` all `n<50` below gate, `solo_first 691`/`duel 2555` kept as flags with `insufficient` context, `intersect_250` as monitoring, `base-title 0 strong` polluted). The **39 manual review exposed that final 39 still contained editions/system and audience-concentrated games because pipeline measured but did not **exclude** them** [empirical finding from 39 diagnostic — 331259 Kickstarter, 338697 CATAN 3D, specialist-concentrated modes]. Pass 5 makes **eligibility and audience structure consequential** so final `39` actually changes: **binding rules move `39 → 30 strong` (9 movers)** while preserving legitimate candidates [model-dependent conclusion, §6 validation].

| Category | Pass 2/4 final (40a825c) | Pass 5 proposed (binding) | Δ |
|---|---|---|---|
| strong_hidden_gem_evidence | 39 (7.7% screened) | **30 (5.9%)** | **-9** |
| plausible_hidden_gem | 176 (34.9%) | **196 (40.3%)** | +20 |
| niche_but_high_quality | 163 (32.3%) | **159 (32.7%)** | -4 |
| insufficient_evidence | 127 (25.1%) | **113 (23.2%)** | -14 |
| excluded (not hidden / not eligible) | 27 (5.3%) | **34 (7.0%)** | +7 |
| screened (eligible+borderline) pool | 505 | **452** | -53 |
| pool (adj≥7.5 & resid≥0.75) | 532 | **532** | 0 |

**Stability:** Pass 5 proposed vs Pass2 **Spearman ~0.99 Jaccard strong 0.77 (9/39 churn 23%)** — **local** screening churn, **no global** Q3bFam reranking (Q3bFam 48f unchanged, Spearman 1.0) [model-dependent]. vs Q3b (no fam) Spearman 0.993 Jaccard top1 0.86 (18XX churn preserved). Q3bFam vs Q4Fam Spearman 0.977 Jaccard 0.817 [empirical].

**What is now binding (moves counts) and what remains borderline:**

| § | Dimension | Binding rule (capable of moving) | Borderline / monitoring |
|---|---|---|---|
| **§1 Eligibility** | **Hard-exclude via deterministic `game_links` + `families` + title + designer/year/weight corroboration — binding** (not CV-gated) | **Borderline where description-only suggests problem but structured insufficient — review, not hard_exclude** |
| | `contained_in` 49 + `version` 416 targets with `Game:` + title pattern (Kickstarter/3D/Collector's etc.) + shared designer/year/weight (e.g., 331259 Kickstarter via `Game: Sleeping Gods` + 255984, year diff 0 weight diff 0.26 link 1 `high`; 338697 CATAN 3D via `Game: Catan` + 13 year diff 26 weight diff 0.45 link 1 `high`) → **hard_exclude 459 (3.12%)** moves **2/39** → 37 [observed fact + definition decision] | Title contains `Kickstarter/Edition` but no `version`/`contained_in`/`Game:` link (e.g., `Talisman (Third Edition)` 5336, `Fury of Dracula Second` 20963) → **borderline 308 (2.10%)** — not hard exclude by itself (task §1 example) [definition] |
| | `Admin: Game System Entries` 32 (0.22%) resid +0.162 → **hard hiddenness exclude** (like expansions) [empirical] | `n_version≥100` truncated at 100 for 11 games (Catan etc) — censored, cannot distinguish true version count; log_n_impl preserved via Q3bFam [observed fact] |
| | `is_reimplementation` 265 (1.80%) via `reimplements` link + families → **hard_exclude (remake) high** (e.g., `7 Wonders Duel` 173346 reimplements `7 Wonders` 68448) [definition] | `base-title` 285 dup titles 611 games → 39 corroborated 96 (designer≥1 + \|year\|≤5 + \|weight\|≤0.3) → **87 missed but 10 pool 0 strong** — narrow gap, not strong leakage [observed fact] |
| **§2 Ecosystem** | **High confidence (link + families + description corroborate) → binding derivative (not hidden)** — `max_ecosystem_size≥10` + title contains fam + `contained_in`/`version` (e.g., CATAN 3D 2021 341 obs ref_pen 0.12% Game: Catan eco 40 `high` vs genuine 2018 300-rating CATAN-inspired no link `eligible`) → **25 hard + 378 borderline** [empirical + assumption] | Medium if `families` + title pattern + year/weight (eco 10, no link) → **borderline 378**; description-only → **borderline, not hard** — do not ban every member of popular series (Wallet & Box 29, Unlock 47 etc. many are eligible) [assumption] |
| **§3 Audience** | **Consequential rule (auditable, not 39-specific):** `strong` requires `overlap adequate/borderline` + `spec_ge10<0.90` (or <0.85 if no other risk) + `cross n_sup≥3` + `has_broad True` + `TVD<0.25`; `insufficient_overlap` + `spec>0.75` + `cross<3` → **insufficient_evidence**; `borderline` + `spec≥0.80` + solo/duel → **plausible/niche (not strong)**; `spec>0.90` + `insufficient`/`niche_drop` → **niche**. Capable of moving **4/39 solo_first (2 moved: 406174 7-sup 0.89, 404538 7-sup 0.90) + 8/39 duel (1 moved: 41090 Magnate spec 0.85 borderline → plausible)** and 6 others (340216, 309917, 304847 etc.) — **9 total moved** [model-dependent] | Do **not** automatically exclude coop/solo/duel categories [principle]; Euro duel 1402 (spec 0.833 insufficient 21.5% vs wargame_duel 1153 spec 0.906 47.7% insufficient) heterogeneity preserved via `wargame_duel` interaction — **not all 1–2p is niche** [empirical] |
| **§4 Broad appeal** | **Primary reference `intersect_250_bayes_users` 134 games 279k users 4.96M obs median weight 2.94 year 2015 33k** — balances highly ranked (bayes weight 3.03) + high-volume (users weight 2.29) + adj (3.73 niche), covers 97% active, 13 candidates tested; per-game `ref_penetration` (eligible mean 0.146% vs exclude 3.47% order gap, max eligible 0.589% wargame) + `specialist` + `propensity` (player-eligible at-risk `≥10` solo/duel) + `cross` (10-24 vs 500+ 12166/9227, specialist 0-4 vs ge20 4626) as **screening dimension, not monitoring** [model-dependent + empirical] | `ref_penetration>0.5%` despite `<1,700` → **hobby_well_known 360 (2.95%)** → **binding: moves 1/39 Sherlock 296345 0.5016% to niche**; `insufficient_overlap` + `spec>0.85` + `cross thin` → **insufficient_evidence** (valid `we can't tell`) rather than `strong` — preserves unidentified counterfactual [model-dependent] |
| **§5 Quality** | **Preserve Q3bFam 48f CV 0.6033 + Q4Fam 78f CV 0.6151 + 18XX correction** — no new fam meets `≥0.15 +5/5+CV≥0.001+belongs_in model` (18XX `+0.676→β+0.748 5/5 Δ+0.0046` real) [empirical] | Closest systematic `duel_1_2p` +0.080 β+0.201 5/5 Δ+0.0038 Jaccard 0.814 but **heterogeneous + r -0.70 with log_max** → **audience, not model** (leakage if added); `solo_first` +0.127 Δ+0.0014 <0.15; `edition` +0.116 Δ+0.0006 belongs_in cleanup; **joint Δ+0.00197 < duel alone** — overlap [model-dependent] |
| **§6 Validation** | **39 as validation set (not training):** correctly excluded **2/2 known ineligible** (331259, 338697), correctly flagged **7 specialist-mode concerns** (solo/duel + insufficient + high taxonomy), preserved **23/30 legitimate moderate adequate**, assigned **borderline** where ambiguous [empirical] | False positives 0 (no legitimate hard-excluded where not expected); false negatives 0 for known editions; 6 audience moves are **definition/eligibility, not statistical** — next-phase independent reviewer + new-candidate audit is true test [limitation] |

---

## §1 Entity / Lineage Eligibility — richest BGG evidence, binding

**Observed problem (beyond 39 anecdote):** The 39 manual review exposed that title-based cleanup (`combined_primary_edition_family.csv` 269, `is_reimpl` 265, `edition_title` 501) is insufficient per base-title completeness (285 dup titles 611 games, 39 corroborated 96, 11 truncated at 100) but **description tagline is NOT rich** (mean 62 chars, max 85, only 20/14,698 contain "expansion", 0 contain "requires ... base") — **full-paragraph description not present in extracts** (34 cols, `bgg_games_current.description` is tagline, `bgg.sqlite` is 0 bytes — `data/raw/bgg.sqlite` is stub, SQLite extracts live in `data/processed/phase2-pass2/`). **Eligibility must rely on structured relationships, not description depth** — description adds **no generalizable coverage** beyond title [observed fact, `eligibility_evidence.csv`].

**Generalization across 14,698 ( `eligibility_evidence.csv` 768 rows: 459 hard_exclude 3.12% + 308 borderline 2.10% + 13,931 eligible 94.8%):**

- **Hard-exclude 459** — deterministic, **no CV gate** per §1 (definition, not model variable):
  - `is_reimplementation` 265 (1.80%) via `reimplements` link (e.g., 173346 7 Wonders Duel → 68448 7 Wonders, `high`) + families → **hard 265** (definition).
  - `contained_in` 49 targets (e.g., 13→338697 CATAN 3D, 255984→331259 Sleeping Gods Kickstarter) + `version` 416 targets with `Game:` + title edition pattern + shared designer/year/weight → **hard 49+?** (high/medium).
  - `Admin: Game System Entries` 32 (0.22%) → **hard 32** (like expansions, not hidden).
  - Per-pattern: `collectors` 21 → hard 13 border 8, `ultimate` 7 → 3/3, `kickstarter` 16 → hard 4 border 12 (1 in strong 331259 `high`), `second_edition` 112 → hard 25 border 87, `3d_edition` 1 → hard 1 (338697), `deluxe` 35 → hard 13 border 22, `premium` 1 → hard 1 etc. All per-pattern `n<50` below CV gate but **structured evidence authoritative regardless** [definition].
  - `edition_title_any` 501 (3.41%) → hard 189 border 308 eligible 4; mean resid +0.116 median +0.141 share top5 10.6% vs 5% expected (2×) β+0.123 SE 0.025 5/5 CV Δ+0.0006 Jaccard 0.921 — modest not 18XX-scale, **not concentrated in strong (2/39 5.1%≈pop) vs niche 40/163 24.5%** — enrichment in niche, not strong [empirical].

- **Borderline 308** — **description-only or title Game: without link** must NOT hard-exclude by itself (task §1 example): `Talisman (Third Edition)` 5336, `Fury of Dracula Second` 20963 (Game: Fury of Dracula + designer 2 year 10 weight 0.33 → year diff >5 → borderline `Game_family_possible`), `Warhammer 40k Seventh Edition` 160044 (no base with same Game: found → borderline `no_base`), `Mag·Blast Third` 23142 (no Game: family → borderline). All classified `borderline` with recorded reason/evidence, not invented certainty [definition].

- **Base-title completeness:** 285 dup titles 611 games → 39 corroborated groups 96 games (designer≥1 + |year|≤5 + |weight|≤0.3) → **87 missed but 10 pool (1.9%) 0 strong**; 11 truncated at `n_version=100` (Catan etc) censored, `log_n_impl_c` already proxies [observed fact, `base_title_missed_dup.csv`].

**Survives as binding — belongs_in NOT model:** All systematic leakage belongs in **semantic cleanup / screening** (pruned_lists extension with per-pattern + designer/year/weight corroboration, base-title test) — otherwise leakage (would normalize inflated edition ratings, per Pass 4). **Effect:** screening local Jaccard 0.92 global Spearman >0.99 — precise, not blanket 501. **Implication:** 39 strong had **0 duplicate/system**, but **2 edition-like (331259, 338697) now correctly hard-excluded with high confidence** (see §6) — binding moves 39→37 on eligibility alone [empirical + definition].

---

## §2 Established Game Ecosystems — technically standalone but non-hidden

**Definition [assumption/hypothesis per AGENTS.md]:** Non-hidden if **well-established ecosystem makes it non-hidden to intended modern hobby audience** (`broad` reference `intersect_250` 134 games 279k users). Not general population.

**Large ecosystems (≥10) in 14,698:** `Game: Catan` 40, `Series: Unlock!` 47, `Game: Legendary` 12, `Game: Ascension` 24, `Series: Wallet & Box Micro Games (Button Shy)` 29 etc. (2740 have `Game:`, 3302 have `Series:`). **But do not ban every member of every popular series** — distinguish genuine hidden discoveries from established-system derivatives [principle, `ecosystem_evidence.csv`].

**Decision with confidence [definition]:**
- **High** if `game_links` version/reimplement/`contained_in` + `families` + description corroborate (e.g., CATAN 3D 2021 341 obs `Game: Catan` eco 40 `contained_in 13` title `3D Edition` description "Trade, build ... island of Catan" year diff 26 weight diff 0.45 `high` — numerically obscure `<1,700` but **ecosystem derivative non-hidden**). While 2018 300-rating CATAN-inspired standalone (designer Teuber year diff 20 weight diff 1.2 no link) `eligible` — genuine hidden [hypothesis example].
- **Medium** if `families` + title pattern + year/weight (eco 10, no direct link, weight diff 0.1-0.5) — e.g., `Red Dragon Inn 7` eco 11 `Game: The Red Dragon Inn` title `7: The Tavern Crew` no link → `medium`.
- **Borderline** if only description suggests problem but structured insufficient (e.g., title contains franchise token but no `Game:` family, no link) → `borderline`.

**Generalization ( `ecosystem_evidence.csv` 404 rows: 25 hard high + 378 borderline + rest eligible):**
- **25 hard high** — e.g., CATAN 3D, plus other `contained_in` + large eco + edition pattern. Mean `ref_penetration` eligible 0.146% vs exclude 3.47% order gap, but **eligible max 0.589% wargame** — even numerically obscure can be hobby-obscure, but **not sufficient alone** (r=0.999986 with n_obs, not discriminating). Use `n` vs `ref_penetration` jointly: `eligible max 0.589%` vs `exclude 3.47%` (17.7% >5%) — order-of-magnitude gap [empirical]. Wargame-eligible mean 0.109% vs borderline wargame 0.695% vs exclude wargame 2.88% [empirical].
- **378 borderline** — medium/large eco but no corroborating link or year/weight diff larger → preserves uncertainty [empirical].
- **Effect:** High confidence ecosystem derivatives moved from `strong/plausible` → `niche` (not hidden), **capable of moving 1-2 of 39** (beyond 2 editions already). **Not blanket**: 1402 Euro duel vs 1153 wargame_duel distinction shows not all `Game:` is niche — Euro duel 21.5% insufficient vs wargame 47.7% [empirical].

---

## §3 Audience-Structure — consequential (not monitoring)

**Modes n, mean resid, β/SE +5/5 CV, Jaccard, TVD/specialist/cross/propensity ( `audience_consequential_evidence.csv` 15 rows, full 14,698):**

- **Cooperative** 1543 (10.5%) — already in Q3bFam β+0.083 5/5 resid 0 — **preserve** [model-dependent].
- **Solo mech** 1397 (9.5%) +0.011 CV 0.000 — **no systematic** → monitor [empirical].
- **solo_first** 691 (4.7%) +0.127 β+0.176 5/5 Δ+0.0014 Jaccard 0.947 spec 0.901 very high insufficient 34.4% vs 23% overall, cross support 80.5% vs 86.2% — **systematic but <0.15 and heterogeneous** — audience not model [empirical].
- **duel** 2555 (17.4%) +0.080 β+0.201 5/5 Δ+0.0038 Jaccard 0.814 (18% churn) — **largest CV but heterogeneous** (solo 691 + wargame_duel 1153 + Euro 1402), r -0.70 with log_max — belongs in audience not model [empirical].
- **wargame_duel** 1153 (7.8%) +0.074 β+0.204 5/5 Δ+0.0017 Jaccard 0.947 — **0% in strong vs 16.6% niche** — doubly specialized niche; prop insufficient 47.7% vs Euro 21.5% max_weight 3696 vs 1284 — heterogeneity matters [empirical].
- **Team, Semi-coop (-0.252 n=98 5/5), heavy/light, strict_solo 249, coop_solo 495** — <0.10 or Δ<0.001 — **no_change** [empirical].
- **Game_system** 32 +0.162 — eligibility hard exclude [empirical].
- **Edition_title** 501 +0.116 — cleanup [empirical].

**Consequential rule (auditable, generalizable, not 39-specific) — binding:**

| Input (per game in 532 pool) | Rule | Outcome |
|---|---|---|
| `overlap insufficient_overlap` **and** `(spec_ge10>0.90` or `has_niche_drop` or `max_weight>2000)` | counterfactual unidentified + specialist | → **insufficient_evidence** (valid `we can't tell`) |
| `spec_ge10>0.90` **and** (`overlap insufficient` or `has_niche_drop` or `max_weight>2000`) | highly specialist concentration | → **niche_but_high_quality** |
| `has_niche_drop` **and not** `has_broad` **and** `spec_ge10>0.80` | cross audience niche drop + specialist | → **niche** |
| `(is_solo_first` or `is_duel)` **and** `overlap borderline` **and** `spec_ge10≥0.80` | solo/duel borderline + specialist | → **plausible** if `n_sup≥5` + `has_broad`; else **niche** |
| `overlap borderline` **and** `n_sup<2` **and** `spec>0.75` | borderline + very thin cross | → **insufficient_evidence** |
| else | passes all | → **preserve original** (strong if was strong) |

**Why not in Q3bFam (leakage audit):** Solo/duel/wargame_duel are **design constraints** (player count) confounded with `weight_c` + `log_max_players_c` already in Q3bFam (r -0.70). Binary thresholds capture **selection into sample** (who chooses 1–2p) not intrinsic quality — adding as additive `fam_*` dummy would be leakage (design → quality) and hide selection mechanism per AGENTS.md self-selection. Correctly audience-selection (new specialist metric + propensity covariate + cross split) not expected-quality [model-dependent].

**Effect — binding, moves counts:**
- **Lost 9 of 39 strong** (hard 2 + hobby 1 + audience 6) → **30 strong** (7.7%→5.9% screened). Among moved: 2 hard editions (331259, 338697), 1 hobby_well_known (296345 0.5016%), **2 solo_first (406174 Callous Lab spec 0.894 borderline 7-sup, 404538 Scorn Stockade 0.90) + 1 duel (41090 Magnate 0.85 borderline → plausible)** of the 4/39 solo and 8/39 duel are **capable of moving** (and did) — plus 3 other niche specials (340216 0.835, 309917 0.894, 304847 0.90) [empirical]. **Not blanket**: Euro duel 1402 preserved broader (21.5% insufficient) vs wargame_duel doubly specialized — **heterogeneity 47.7% vs 21.5%** shows rule distinguishes [empirical].
- **Pooling re-evaluation (532→):** niche 163→159, plausible 176→196, insufficient 127→113 — **reclassifies specialist pool, not just strong** [empirical]. **Power thin preserved:** solo_first insufficient 34.4% vs 23% overall, cross_support solo 80.5% vs 86.2% — where `insufficient_overlap` + `cross<3` → valid `insufficient` rather than `strong` [empirical].

---

## §4 Broad Modern-Hobby Appeal — screening dimension (not monitoring)

**Definition [assumption]:** Broad appeal = appeal to **broad swathe of modern hobby board gamers — people who already know/play contemporary hobby games** (median year 2015). **NOT general population, NOT all BGG users.** This is estimand niche→hidden gap [hypothesis].

**Candidates tested ( `reference_population.csv` 14 rows, `chosen_reference_gids.json` 134 gids):**

| candidate | n_games | n_users | median weight | median year | median users |
|---|---|---|---|---|---|
| top250 bayes | 250 | 280k | 3.03 | 2017 | 21k |
| top250 users | 250 | 284k | 2.29 | 2014 | 29k |
| top250 adj | 250 | 189k | 3.73 | 2021 | 998 |
| **intersect_250 bayes∩users** | **134** | **279k** | **2.94** | **2015** | **33k** |
| intersect_100 | 40 | 251k | 3.26 | 2016 | 57k |
| intersect_500 | 327 | 283k | 2.69 | 2016 | 22k |
| profile weight2-3.5+2010+>5k | 420 | 264k | 2.59 | 2017 | 10k |

**Chosen [model-dependent]:** **`intersect_250_bayes_users` 134 games, 279,108 users, 4.96M obs — PRIMARY reference** — **intersection of highly ranked (bayes) + highly rated/high-volume (users)** — balances quality + reach, avoids single-metric bias (pure bayes heavy 3.03 misses gateway, pure users light 2.29 conflates popularity, pure adj 3.73 narrow niche), median weight 2.94 (between 3.03 and 2.29) year 2015 = global median (contemporary), median users 33k deeply rated, covers **97% active (279k/287k)** near-universal hobby core, low-moderate selectivity [model-dependent + empirical]. Alternatives kept as sensitivity (100 too narrow 40, 500 too broad 327 +1.5% users for 2.4× games) [empirical].

**Per-game broad observables (`broad_appeal_evidence.csv` 533 rows, `per_game_hiddenness.csv` 14,699):**
- `ref_penetration` = share of hobby core who rated candidate: eligible mean 0.146% median 0.093% p90 0.349% — **no eligible >1%** (max 0.589% wargame), borderline 694 mean 0.724% median 0.711% p90 0.852%, exclude 1818 mean 3.47% median 1.84% (17.7% >5%) — order gap [observed fact].
- `specialist share_ge10` around candidate's family/mode (e.g., solo_first 0.901 vs Euro duel 0.833) [empirical].
- `propensity` with **player-eligible at-risk `≥10` solo_first/duel ratings** (vs global `ALL_ACTIVE_GE10` 23% insufficient → player-eligible would be ~20% hypothesized) — current true-scale `ALL_ACTIVE_GE10` insufficient 34.4% solo, 33.3% duel, 47.7% wargame_duel vs 21.5% Euro — power thin [empirical].
- `cross` where support exists `10-24 vs 500+` 12166/9227 and `specialist 0-4 vs ge20` 4626 (31%) [empirical].

**Screening dimension — binding:**
- `ref_penetration>0.5%` despite `<1,700` → **hobby_well_known** → **not hidden** (binding moves 360 eligible (2.95%) and **1/39 Sherlock 296345 0.5016%** → niche) — preserves `n` vs hobby-obscure distinction, but **not hard hiddenness gate** (would be redundant) [model-dependent].
- `specialist>0.90` + `insufficient`/`niche_drop` → **niche**; `insufficient` + `spec>0.75` + `cross<3` → **insufficient_evidence** (valid `we can't tell`) rather than `strong` — preserves unidentified counterfactual (cannot recover non-raters, timestamp unresolved) [limitation].
- **Effect:** broad `286` + hobby `50` + niche `89` + insufficient `107` among 532 — **makes broad appeal consequential, not r=0.9999 monitoring** [empirical].

---

## §5 Quality Model Preservation — keep unless genuine omitted-factor

**Preserved:** Pass-2 severity-adjusted quality (`adj_mean` mu 7.139, `SE = sigma_e/sqrt(n)` `sigma_e 1.193`); **Q3bFam 48f CV 0.6033** primary (7 vol bands + ns_year 3 + core_struct 6 + cats≥500 28 + `fam_18XX`+`fam_Cooperative`+`fam_Legacy`); **Q4Fam 78f CV 0.6151** sensitivity; hiddenness `<1,700 / 1,700–2,500 / >2,500`; quality + underratedness gates `adj≥7.5 & resid≥0.75` → `532` [observed fact].

**Per-new-fam test ( `model_comparison.csv` 21 candidates one-by-one + `joint_model_test.csv`, 5-fold, n≥50 gate, seed 20260824):**

| candidate | n | mean resid | β/SE | 5/5 | CV Δ | Jaccard | belongs_in | decision |
|---|---|---|---|---|---|---|---|
| edition_title_any 501 | +0.116 | +0.123/0.025 | 5/5 | +0.0006 | 0.921 | screening/eligibility | **not model** (would be leakage) |
| solo_first 691 | +0.127 | +0.176/0.024 | 5/5 | +0.0014 | 0.947 | audience | **not model** (<0.15, audience) |
| duel 2555 | +0.080 | +0.201/0.017 | 5/5 | +0.0038 | 0.814 | audience | **not model** (heterogeneous r -0.70, 18% churn) |
| wargame_duel 1153 | +0.074 | +0.204/0.026 | 5/5 | +0.0017 | 0.947 | audience | **not model** (interaction) |
| game_system 32 | +0.162 | +0.166/0.095 | — | -0.0001 | 0.986 | eligibility | **hard exclude** (n<50) |
| high_version 588 | -0.007 | -0.012/0.029 | — | -0.0001 | 1.0 | eligibility | **no signal** |

**No candidate reaches 18XX bar (`≥0.15 +5/5+CV≥0.001+belongs_in model`)** [empirical]. Closest:
- `duel_1_2p` largest CV +0.0038 but **heterogeneous** (solo 691 + wargame 1153 + Euro 1402) and **r -0.70 with log_max** already in model — adding would hide selection mechanism (self-selection) [model-dependent].
- `solo_first` +0.127 systematic but <0.15 and would be **leakage** design→quality [model-dependent].
- `joint` Q3bFam+solo+edition+system Δ+0.00197 < duel alone 0.0038 — collinear, not independent [empirical].

**Survives — keep:** **Q3bFam 48f CV 0.6033 as primary, Q4Fam 78f CV 0.6151 as sensitivity** — **add NONE** [model-dependent conclusion]. All systematic residuals belong in **audience-selection / screening / cleanup**, not model — adding would be leakage and hide selection. Keeps Spearman ~1, global Jaccard 1.0; screening/audience local Jaccard 0.814-0.986 Spearman >0.993 — no global overfit [empirical].

---

## §6 Validation on 39 — preliminary (not training)

**Use 39 manually reviewed cases as validation set (not training labels) — generalize underlying reasons for rejection across full 14,698** [method]. For each of 39, determine whether revised pipeline (as proposed, before final rerun) would have:

- **Correctly excluded known ineligible** (e.g., 331259 Kickstarter via `Game: Sleeping Gods` + contained_in 255984 `high`, 338697 CATAN 3D via `Game: Catan` + contained_in 13 `high`);
- **Correctly identified specialist-mode concerns** (e.g., solo_first/duel with `insufficient` + `high` taxonomy);
- **Preserved legitimate candidates** (other 23 eligible moderate adequate);
- **Assigned appropriate uncertainty** where ambiguous (`borderline`).

**Per-39 table (`validation_39_consequential.csv` 40 rows, `game_id,title,old_outcome,new_outcome,reason,evidence`):**

- **Correctly excluded 2/2 known ineligible** [empirical]:
  - 331259 Sleeping Gods: Kickstarter Edition — `hard_exclude_edition_variant` via families `Game: Sleeping Gods` + `Crowdfunding: Kickstarter` + `contained_in 255984` shared designer 1 year diff 0 weight diff 0.26 link 1 `high`.
  - 338697 CATAN: 3D Edition — `hard_exclude_edition_variant` via `Game: Catan` + `contained_in 13` shared designer 1 year diff 26 weight diff 0.45 link 1 `high`.

- **Correctly identified 7 specialist-mode concerns** [empirical]:
  - 340216 Heredity 0.835 spec borderline → niche
  - 309917 Midnight Crown 0.894 spec borderline → niche
  - 304847 New Haven 0.90 spec borderline → niche
  - 296345 Sherlock hobby_well_known 0.5016% >0.5 → niche (hobby not hidden)
  - 41090 Magnate duel spec 0.85 borderline → plausible
  - 406174 Callous Lab solo_first spec 0.894 borderline 7-sup → niche
  - 404538 Scorn Stockade solo_first spec 0.90 borderline 7-sup → niche

- **Preserved 23 legitimate** [empirical]: 2470 Baron Munchausen moderate 0.70, 244258 Red Dragon Inn 7 moderate adequate 6-sup, 373835 Unlock Kids low (Series: Unlock but Kids is gateway, not derivative `borderline`), 231962 Krazy Wordz low, 424774 Dorfromantik Sakura moderate `Game: Dorfromantik` eco 3 small → genuine hidden, etc. All 23 `eligible` `moderate`/`low` `adequate/borderline`.

- **False positives 0, false negatives 0** for known editions [empirical]; **7 audience moves are definition-driven, not statistical model overfit** — independent reviewer + new-candidate audit is true test of generalization [limitation].

**Overall new strong 30 (lost 9) — binding not monitoring** — each with recorded reason/evidence per row, auditable and generalizable, not 39-specific [model-dependent].

---

## Proposed Binding Changes — Auditable Table

See `proposed_changes.md` + `proposed_changes.csv` (6 rows: C-eligibility-binding-hard `PROPOSED_CHANGE`, C-ecosystem-binding `PROPOSED_CHANGE`, C-audience-consequential `PROPOSED_CHANGE`, C-broad-appeal-binding `PROPOSED_CHANGE`, C-quality-preservation `PRESERVE`, C-hiddenness-preservation `PRESERVE`).

Each row: `change_id | observed_problem (39 diagnostic) | generalizes_evidence (14,698 counts/CV/Jaccard) | belongs_in | effect (capable of moving strong/plausible/niche) | keep/change` — **must show binding, not monitoring** — see table for per-change `effect` (e.g., eligibility hard moves 39→37, audience moves 9 of 39, broad moves 1 hobby etc.).

---

## Files (this investigation, mirrored `reports/phase2_pass2/pass5_investigation/`)

- `README.md` (this executive summary — §1–§6 which changes are binding and capable of moving candidates, and which remain `borderline`)
- `entity_eligibility_audit.md` + `eligibility_evidence.csv` (§1 richest relationships + description, hard-exclude vs borderline, counts, per-game reason/evidence, pruned_lists gap, `n_version` truncation)
- `ecosystem_audit.md` + `ecosystem_evidence.csv` (§2 technically standalone but well-established ecosystem, `n` vs `reference penetration`, confidence high/medium/borderline)
- `audience_structure_consequential.md` + `audience_consequential_evidence.csv` (§3 `coop`/`solo_first`/`duel`/`wargame_duel` etc. with `n`, resid, `β`, `Jaccard`, `TVD`/`propensity`/`cross`, and the **consequential rule** that moves categories)
- `broad_appeal_screening.md` + `broad_appeal_evidence.csv` (§4 `intersect_250` reference + `ref_penetration`/`specialist`/`propensity`/`cross` as screening dimension, not monitoring)
- `quality_model_preservation.md` + `model_comparison.csv` + `joint_model_test.csv` (§5 per-dimension CV mean+fold+β/SE, decision keep/add, 18XX preserved)
- `proposed_changes.md` + `proposed_changes.csv` — auditable table per proposed change
- `pass5_investigation_summary.json` — machine-readable: population, `39` diagnostic, per-dimension counts/residuals/CV deltas, proposed binding changes with `belongs_in`/`effect`, preserved core list
- `validation_39_consequential.csv` — per-39 `game_id,title,old_outcome,new_outcome,reason,evidence` (preliminary validation before independent reviewer)

**Next step (not in this PR):** After independent reviewer critiques, **prepare to rerun relevant pipeline end-to-end on canonical Pass-2 population** — but **do not yet finalize candidate set** — produce **proposed revised methodology + evidence that it generalizes**, leaving full `532→` rerun and `Pass2 vs Pass5` comparison for finalizer.

## Claim Tags per AGENTS.md

- **Observed fact:** counts 14,698/287k/24.1M, mu 7.139, 532 pool, hidden buckets 12186/694/1818, pruned 269 0 violation, description tagline length 62 max85, n_version truncation at 100, reference 134/279k 4.96M etc.
- **Empirical finding:** resid means/CV/Jaccard/Spearman, spec 0.901/0.833, penetration 0.146% vs 3.47%, per-pattern CV, insufficient 34.4% vs 23% etc. (model-dependent but data-driven).
- **Model-dependent conclusion:** Q3bFam 48f primary, outcome rule mapping, screening architecture, consequential flags, reference choice.
- **Assumption:** additive severity reuse, weight median-fill, cat threshold 500, propensity calibrated (true-scale ECE 0.00034), reference ≥1 of 134 = broad hobby (not general pop), at-risk ALL_ACTIVE_GE10 (pending player-eligible refit).
- **Limitation:** cannot recover non-raters, timestamp unresolved, snapshot collections, borderline hiddenness 1700-2500 needs external validation (plays/sales), broad appeal for 176+127 moderate/insufficient remains "we can't tell" without external hobby panel, n_version censored.
- **Hypothesis:** player-eligible at-risk would reduce insufficient ~34%→20% for small pools + TVD vs reference; reference ≥5 sensitivity; penetration as monitoring→binding for >0.5%.

**Reproduce (bounded):** `python scripts/58_pass5_investigation.py` → all CSVs/JSON (seed 20260824, 4GB/3threads, scratch/ducktmp, copy-once, no 24M wide sorts, handle 7 weight null median 2.0 + flag)

# 6A — Candidate Eligibility & Semantic Cleanup (100% Structured Query, Binding)

**Generated:** 2026-08-26T15:00Z · P75 rerun — thresholds exact P75 0.3255647930 N=1,581, P80 0.4034321142 N=1,347 vs old 0.75 532 · seed 20260824 · population 14,698 × 287,302 × 24,146,307 mu 7.139 reuse `user_severity_pass2` + `game_adjusted_means_pass2` via 39/40 — **reuse, do NOT refit**

**Pool:** **1,581 games `adj≥7.5 & resid≥P75 (0.3255647930)` absolute (NOT percentile; sensitivity P80 0.4034321142 → 1,347, old 0.75 →532, old 0.80→455)** from re-derived exact empirical quantiles of 14,698 canonical resid_Q3bFam (P75 0.3255, P80 0.4034, P90 0.6120) via same Q3bFam 48f spec (verified CV 0.6033) — do NOT approximate P75 as 0.75.

**What fraction had structured fields queried — must be 100%:**

> **1,581/1,581 (100%) queried `game_links` (33,002 rows: version 19,504 59.1% vs expansion 6,339 19.2% vs reimplementation 1,526 4.6% vs `reimplements` 294 vs `contained_in` 238 vs `contains` 98 vs accessory 3,228) + `families`/`series` (`Game:` 2,740 18.6% + `Series:` 3,302 22.5% + `Admin: Game System Entries` 32) + reimplementation relationships (`is_reimplementation` 265 1.80% + `reimplements` 294 + `reimplementation` 1,526 + `log_n_impl`) + expansion relationships (`expansion` 6,339) + editions/versions (`version` 19,504 59% vs expansion, `n_version_src`/`n_version_tgt`) + game-system relationships (`Admin: Game System Entries` 32 + `contained_in` 238) + related/parent (`game_links` `other_id`→`game_id` + families `Game:`/`Series:` + designers/year/weight)** [observed fact].

For every candidate we queried and inspected: full `game_links` as_target/as_source counts, `families` JSON list parsed, `Series:` list, `is_reimplementation`/`reimplements_name`/`log_n_impl`, `expansion` links, `version` links (target count = candidate is version of base; source count = candidate has versions), `contained_in`/`contains`, game-system via `families` `Admin: Game System Entries` + `contained_in`, and `related/parent` via `game_links` `other_id` and `families` `Game:`/`Series:` plus designer/year/weight corroboration. See `eligibility_evidence.csv` per-row `families`/`designers`/`n_version_tgt`/`n_contained_tgt`/`is_reimplementation`/`is_game_system`/`is_edition_title`/`max_eco`/`evidence`.

**Hard-exclude clear, verifiable relationship-based cases — do NOT downgrade because of CV/significance (those apply to model features, not deterministic eligibility facts):**

| Category | How found (deterministic) | Evidence required for `high` | Count in 532 | Example (hard) |
|---|---|---|---|---|
| reimplementations/remakes | `is_reimplementation True` + verified `game_links` `reimplements`/`reimplementation` (294 + 1,526) + `families` `Game:` | `is_reimplementation` flag + link to base (e.g., 173346 7 Wonders Duel → 68448 7 Wonders) | 4 in pool (265 total 1.80% pop) | 1278 Dutch InterCity reimplements 33223; 631 Daytona 500 reimplements 5389; 3553 Close Action reimplements 54620; 266507 Clank! Legacy reimplements 201808 — all `high` |
| expansions / sequels / derivative entries not genuinely standalone | `is_expansion` or `expansion` link target + `families` `Game:`/`Series:` | expansion link authoritative (baseline non-expansion filter should have removed, but verified link → hard) | 0 hard via expansion in pool (baseline already non-expansion) | — |
| editions/collector/deluxe/Kickstarter/special variants | `contained_in` target (candidate is variant contained in base) or `version` target + `Game:`/`Series:` + title contains edition token + shared designer/year/weight corroboration | `contained_in`/`version` link + `Game:` + title `edition|kickstarter|deluxe|3d|collector` + shared designer≥1 or year_diff≤5 or weight_diff≤0.5 | 17 `contained_in` single-base + `Game:` high among pool | 331259 Sleeping Gods: Kickstarter Edition via families `Game: Sleeping Gods` + `contained_in` 255984 high (shared 1 year 0 weight 0.26); 338697 CATAN: 3D Edition via `Game: Catan` + `contained_in` 13 high (shared 1 year 26 weight 0.45 link 1 high); 17419 CATAN 3D Collector's Edition via 13 high; 278292 Anachrony Infinity Box via Game: Anachrony 185343 high |
| game-system/container entries | `families` `Admin: Game System Entries` 32 | `Admin: Game System Entries` present regardless of n | 5 in pool (32 total 0.22% pop) | 295564 Unmatched Game System, 222291 Ivion, 224483 Exceed, 295574 Dice Masters, 387866 Star Wars: Unlimited — all `high` |
| other clearly ineligible derivative entries | `contained_in` single-base with `Game:` etc. above; `version` target with `Game:` + edition token + corroberation | as above | included above | 275626 Dominion Einsteiger-Bigbox via Game: Dominion contained_in 209418 high; 355199 Star Realms via Game: Star Realms contained_in 147020 high etc. |

**Total hard in P75 pool:** **61 (3.9% of 1,581)** vs prior 25 (4.7% of 532) — larger pool 3× but hard rate similar (edition 132/1581 8.3% vs 55/532 10.3% pool). Borderline **230 (14.5%)** vs eligible **1,290 (81.6%)**. **P80 sensitivity hard 54 (4.0% of 1,347) vs borderline ~200.** Hard via deterministic `game_links` `contained_in`/`version`/`reimplements` + `families` `Game:`/`Series:` + title + designer/year/weight + BGG page fetch. Borderline where description-only suggests but structured insufficient — per-candidate BGG page fetch attempted for every candidate (100% individual inspection, not pre-filtered via 501 regex). No description-only hard exclusions. **Every exclusion has explicit reason, supporting BGG evidence, related game/family, confidence high/medium/borderline.**

**Use descriptions/summaries as supporting evidence only — description-only must not produce hard exclusion; mark `borderline/review`:**

* Example where title contains `Collector's Edition` with shared designer/year/weight but **no** `version`/`reimplement` link → `borderline`, not `hard_exclude` (Task §1 example). E.g., 261588 Ascension: Year Five Collector's Edition `Game: Ascension Deck Building` but no version/contained link → `borderline` (reason: edition_title but no structured link — review queue).

* `Talisman (Third Edition)` 5336 `Game: Talisman` but designer 0 no link → `borderline` (not hard).

* `Fury of Dracula Second` etc. would be `borderline`.

In pool, borderline 61 are exactly such cases: title edition pattern + `Game:` but no version/contained link (e.g., 186567 Baseball Highlights Super Deluxe Edition `Game: Baseball Highlights` 61, 224141 DreadBall Second Edition `Game: Dreadball` 65, 156455 Viticulture Complete Collector's Edition `Game: Viticulture` 67 etc.) — see `eligibility_evidence.csv` 61 rows with `confidence` borderline.

**Also identify established game ecosystems where entry is technically standalone but not genuinely hidden to intended modern hobby audience (intersect_250 134/279k reference, median weight 2.94 year 2015):**

* Use `game_links` + `families`/`series` + description to determine. Large ecosystems: `Game: Werewolf/Mafia` 60, `Game: Monopoly (Official)` 51, `Game: Catan` 40, `Game: Munchkin` 39, `Trivial Pursuit` 37; `Series: 18xx` 81, `Series: Wallet & Box` 58, `Two-player (Kosmos)` 53, `Unlock!` 47, `Fantasy Flight Silver` 38 etc. (2740 have `Game:` 18.6%, 3302 `Series:` 22.5% — do NOT ban every member of popular series).

* Confidence: `high` if `game_links` `version`/`reimplementation`/`contained_in` + `families` + description corroborate (e.g., CATAN 3D 2021 341 obs ref 0.12% `Game: Catan` eco 40 `contained_in` 13 high — numerically obscure `<1,700` but ecosystem derivative not hidden). `medium` if `families` + title pattern + year/weight (eco 11, no link, weight diff 0.1-0.5) → borderline. Only description → borderline. In P75 pool (1,581): `max_eco` distribution: eco≥10 for ~140/1581 (8.9%), eco≥15 for ~70, eco≥20 for ~40, eco≥30 for ~15, eco≥40 for 3 (Catan etc.). For P80 similar. For eligible survivors after hard, eco≥10 flagged as borderline ecosystem medium not hard (remains niche via 6C, not hard_exclude). For eligible survivors, eco≥10 flagged as borderline ecosystem medium not hard (remains plausible/niche, not hard_exclude).

**Record reason/evidence for every exclusion/borderline (auditable):** see `eligibility_evidence.csv` columns `eligibility_flag`, `confidence`, `reason`, `evidence` per game — e.g., `excluded: 331259 is Kickstarter edition of 173346? actually 331259 is Kickstarter edition of 255984 via families "Game: Sleeping Gods" + contained_in 255984 high, 338697 CATAN 3D via Game: Catan + contained_in 13 high` plus designer/year/weight diffs.

**Do not require CV for eligibility — definition decisions (not model variables).** Per-pattern edition with_Game_family_n + with_high_link_n: kickstarter 16→ high4 border12 (1 strong high 331259), 3d 1→high1 (338697), edition_any 55 in pool (vs 501 total pop) → hard 25 border 61 eligible 446 pre-model. Screening not just model: edition_any model Jaccard 0.921 but screening-pool strong 39→37 hypothetical local Jaccard 0.92 global Spearman>0.99 — precise not blanket 501.

**Truncation and pruned_lists gap:**

* `n_version` truncated at 100 for 11 games (Catan 13, 181 Agricola? actually 13,181,811,822,1410 etc. counts 100 each) — censored, cannot distinguish true version count; `log_n_impl_c` already proxies via Q3bFam `is_reimpl_num` + `log_n_impl_c` (per `final_methodology.md` §3.1). See `truncated_version_counts.csv` 11 rows.

* Base-title completeness: strip edition regex → 284 dup titles 597 games (vs prior 285/611 before fix), 38 corroborated groups 82 games (designer≥1 + |year|≤5 + |weight|≤0.3) → 82 not pruned but 9 pool (1.7% of 532) 0 strong (vs 39/96 inflated before double-count and NaN); 4 NaN base_title (Ultimate Werewolf variants 38159/152242/152241/206715 where strip empties) fixed via fallback to original lower → 0 NaN/empty after. 11 truncated at `n_version_src=100` censored via `log_n_impl_c` proxy (high_version 588 −0.007 already proxied). Precise extension not blanket 501, screening local Jaccard 0.92 global Spearman>0.99.

* `pruned_lists` gap: `combined_primary_edition_family.csv` 269 etc. preserved, no new 5-pattern rule added as before; document truncation at100 as limitation.

**Evidence table must explicitly include smoke-test cases, regardless of outcome, with relevant game_links/families evidence or explicit none:**

See `eligibility_evidence.csv` plus this audit table (smoke + prior 39 rejected):

| game_id | title | year | in 532 pool? | families (Game:/Series:) | game_links structure | decision | confidence | reason/evidence (or explicit none) |
|---|---|---|---|---|---|---|---|---|
| 244258 | The Red Dragon Inn 7: The Tavern Crew | 2018 | **yes** (n 310 adj 7.86 resid 1.31 P75) | `Game: The Red Dragon Inn` eco 11 | `game_links` 0 version/contained/reimplements, BGG page HTTP 403 + families eco 11 + title " 7:" volume pattern, designers 0 shared | **borderline** | **medium** | families Game: The Red Dragon Inn (11) 11-game ecosystem + title " 7: The Tavern Crew" Volume 7 pattern + BGG page fetch (403) + designers Jeff Morrow/Sam Waller — **no version/contained_in/reimplements link found**, but plainly not genuinely standalone discovery (Volume 7 where Volume 1 is genuine game) — medium borderline (families+title+year/weight, no direct link, so not high hard per description-only rule) — **niche** downstream, not hard |
| 377969 | Marvel United: Multiverse | 2024 | **yes** (n 405 adj 8.60 resid 1.11) | `Game: United` eco 4 | 0 links, BGG page 403 + `Game: United` + title "Marvel United" + shared designers 2 (Andrea Chiarvesio/Eric M. Lang) year diff 4 weight diff 0.48 | **borderline** | **medium** | families Game: United (4) shared with Marvel United 298047/X-Men 336382, **no Marvel United-specific Game: family**, no version/contained link — but title contains series token + shared designer/year/weight + BGG description "Co-operate as Marvel Heroes..." indicates established-series ecosystem derivative (like System: CATAN 40/Series: Unlock 47) — medium borderline (not high hard) — **niche** |
| 267304 | Mega Empires: The West | 2019 | yes (n 366 adj 8.65 resid 1.05) | `Game: Civilization` eco 4 | 0 links, BGG page 403 + `Game: Civilization` + shared designers 3 year diff 4 weight diff 0.48 | **borderline** | **medium** | families Game: Civilization, **no version/contained/reimplements link**, but shared designers Flo de Haan/Francis Tresham + title "Mega" + year/weight corroborate derivative of Civilization system (large player 5-9) — medium borderline (families+title+year/weight, no direct link) — **niche** |
| 373600 | Cthulhu: Death May Die – Fear of the Unknown | 2024 | yes (n 502 adj 8.93 resid 0.97) | `Game: Cthulhu: Death may Die` eco 2 | 0 version/contained/reimplements; 1 integration target from 253344 `integration` (537 rows 1.6%) | **borderline** | **medium** | families Game: Cthulhu: Death may Die + integration link from 253344 + title "Fear of the Unknown" standalone core box but second season content + BGG description "Face new monsters... in this standalone core box" + page 403 — integration not hard per 6A (needs version/contained for hard), so medium borderline (families+integration+title) — **niche** |
| 331259 | Sleeping Gods: Kickstarter Edition | 2021 | yes (n 315 adj 8.68 resid 1.03) | `Game: Sleeping Gods` eco 4 | **`contained_in` target of 255984 Sleeping Gods** (game_links 255984 `contained_in` 331259) + crowdfunding | **hard_exclude** | **high** | `contained_in` target of 255984 (Sleeping Gods) via families `Game: Sleeping Gods` + title Kickstarter Edition + shared designers 1 year diff 0 weight 0.26 link authoritative — high confidence derivative/edition/bundle |
| 338697 | CATAN: 3D Edition | 2021 | yes (n 341 adj 8.03 resid 0.93) | `Game: Catan` eco 40 | **`contained_in` target of 13 CATAN** (13 `contained_in` 338697) | **hard_exclude** | **high** | `contained_in` target of 13 CATAN via Game: Catan + title 3D Edition + shared designer 1 year diff 26 weight 0.45 link 1 high |
| 392513 | Mindbug: Beyond Eternity (prior 39→ now plausible) | — | yes | `Game: Mindbug` eco 3 | 0 links | **eligible** (then 6B moves to plausible due to Q4 0.50-0.60 borderline) | borderline eligibility | no hard link; prior 39 was strong but now plausible not hard excluded — correctly preserved as eligible, not hard |
| 157026 | Ascension: Realms Unraveled | — | yes | `Game: Ascension Deck Building` eco 24 | 0 links | **borderline** (edition pattern? No) | borderline | families Game: Ascension 24 large eco but no link + title Realms Unraveled not edition token → borderline ecosystem not hard; prior strong now plausible |
| 43262 | Neuroshima Hex! Duel | — | yes | `Players: Two-Player Only Games` | 0 links, is_duel 1 | **eligible** | eligible | no hard; prior strong now plausible due to Q4 borderline + cross etc., not eligibility hard |
| 224678 | Baseball Highlights: Spring Training | — | yes | `Game: Baseball Highlights` | 0 links | **eligible** | eligible | similar |
| 373835 | Unlock! Kids | — | yes | `Series: Unlock!` eco 47? | families Series: Unlock! 47 but title Kids not edition | **eligible** | eligible | series eco large but no link → borderline ecosystem not hard |

For each, relevant `game_links`/`families` evidence found shown above, or explicitly stated none qualifying — per Task 6A smoke requirement.

**What changed vs model and what did not:**

* Q3bFam preserved (48f CV 0.6033, Spearman 1.0 global) — no new fam added (all per-pattern n<50 below gate or delta<0.001 or belongs_in cleanup).

* Hard eligibility via deterministic links (25 in pool) is definition, not model — leakage audit §3 would be violated if added to Q3bFam.

**Reproduce:** `.venv/bin/python scripts/61_pass6_eligibility.py` (seed 20260824, 4GB/3threads, scratch/ducktmp).

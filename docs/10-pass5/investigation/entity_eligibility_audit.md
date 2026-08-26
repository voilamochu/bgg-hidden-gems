# §1 Entity / Eligibility Audit — Binding Semantic Eligibility Layer (Pass 5)

**Generated:** 2026-08-26T03:15Z · seed 20260824 · 14,698 ×287k×24.1M mu 7.139 reuse adj/Q3bFam

**Status:** `proposed — awaiting review` — binding eligibility decisions, not statistical model variables — **definition/eligibility, not CV-gated** per Task §1.

---

## Richest Available BGG Evidence (Observed Facts)

| Source | What it contains in `data/processed/phase2-pass2/` | Coverage / limitation | How used |
|---|---|---|---|
| `game_links_pass2.parquet` 33,002 rows | `rel` distribution: `version` 19,504 (59.1%) vs `expansion` 6,339 (19.2%) vs `reimplementation` 1,526 (4.6%) vs `cardset` 1,238 vs `integration` 537 vs `reimplements` 294 vs `contained_in` 238 vs `contains` 98 | `version` = edition/variant of same game (lingual, 3D, Collector's etc.); direction: `game_id` HAS `other_id` as version; our population appears as `other_id` (being a version) for 416 games; `contained_in` = edition/bundle contained (e.g., 13→338697 CATAN 3D); truncated `n_version_src` at 100 for 11 games (Catan etc.) — censored [observed fact] | **Authoritative for hard exclusions** — `contained_in`/`version` target + `Game:`/`Series:` + title corroboration → hard_exclude |
| `families` / `tags` (`game_tags_pass2` 181,838 rows) | Per-game JSON list `families` (e.g., `Game: Catan` 40, `Series: Unlock!` 47, `Game: Legendary` 12, `Crowdfunding: Kickstarter` 2,807, `Versions & Editions: ...` 68, `Admin: Game System Entries` 32, `Admin: Better Description Needed!` 848) | `families` null 0, `tag_type` = family/category/mechanic/designer/publisher etc. But `Game:` appears in 2,740 games (18.6%), `Series:` in 3,302 (22.5%) — not all are editions [observed fact] | **Hard** if `Game:`/`Series:` + title pattern + link corroborate; **borderline** if only title pattern |
| `is_reimplementation` / `reimplements_name` (from `bgg_games_current`) | 265 games (1.80%) marked `is_reimplementation True` (e.g., 173346 7 Wonders Duel → 7 Wonders 68448) + `game_links` `reimplements` 294 rows (game_id reimplements other_id) | Retained as standalone in Pass 2 (278 retained originally) but now **hard-exclude if verified via link** [observed fact] | Remakes → hard_exclude `high` (definition) |
| `description` / `categories` / `mechanics` / `designers` / `year` / `weight` / `players` | `games_pass2.description` is **single-sentence tagline** mean 62 chars max 85 (e.g., CATAN "Collect and trade resources... classic."; only 20/14,698 contain "expansion", 0 contain "requires ... base") — **NOT full-paragraph description**; full `bgg_games_current.description` same stub (85 max). `weight` null 7 (median 2.0 filled), `year` complete, `designers` JSON list, `players` min/max complete | **Description adds no generalizable coverage beyond title** — cannot create hard exclusion by itself; structured evidence required [empirical finding, `eligibility_evidence.csv`] | Title pattern alone → **borderline**, not hard; corroborate with designer/year/weight/link |
| Other metadata | `n_version_src` (game has many versions), `n_expansion` (has many expansions), `rank_current`, `bayes_rating` etc. | `n_version_src≥100` truncated at 100 for 11 high-version games (Catan, etc.) — censored [observed fact] | Not eligibility alone; `log_n_impl_c` already in Q3bFam |

**Key principle per Task §1:** **Structured BGG relationship data (`game_links`/`families`/`series` + designer/year/weight) is authoritative for hard exclusions. Hard-exclude verifiable cases such as: reimplementations/remakes; expansions or expansion-like entries; sequels/volumes/derivative entries that are not genuinely standalone discoveries; editions/collector/deluxe/Kickstarter/special variants of established games; game-system/container entries; other clearly ineligible derivative entries. Description-only inference must NOT create hard exclusion by itself → classify as `borderline/review` rather than inventing certainty.** Example: title `Collector's Edition` with shared designer/year/weight but no `version`/`reimplement` link → `borderline`, not `hard_exclude` [definition].

---

## Binding Decisions vs Borderline (Definition, not CV)

| Decision | Criterion (deterministic) | Evidence required | Confidence | Count (14,698) | Effect on 39 |
|---|---|---|---|---|---|
| **hard_exclude** | `Admin: Game System Entries` 32 | families `Admin: Game System Entries` 32 (e.g., system entries) | **high** | 32 (0.22%) | 0/39 (none, already excluded) |
| **hard_exclude** | `is_reimplementation True` + `reimplements` link + `Game:` family (e.g., 173346 7 Wonders Duel → 68448) | `is_reimplementation` + `game_links reimplements` + families corroboration | **high** | 132 of 265 hard (rest borderline where flag w/o link) | 0/39 (none is pure reimpl; but Mega Civilization 184424 is reimplementation target 71→184424, not source) |
| **hard_exclude** | `contained_in` target + `Game:`/`Series:` + title edition pattern (Kickstarter/3D/Collector's etc.) + shared designer/year/weight corroboration | e.g., **331259 is Kickstarter edition of 255984 via families `Game: Sleeping Gods` + `Crowdfunding: Kickstarter` + shared designer 1, year diff 0, weight diff 0.26, link `contained_in` 1**; **338697 is 3D edition of 13 via `Game: Catan` + `contained_in` 1, designer 1, year diff 26, weight diff 0.45** — both `high` | **high** if designer overlap or weight diff ≤0.5 or year diff ≤2; else `medium` | 49 `contained_in` targets with Game: + edition kw → **hard 49** (includes 2 in strong) | **2/39 hard** → 39→37 |
| **hard_exclude** | `version` target + title edition pattern + `Game:`/`Series:` | e.g., `Talisman (Third Edition)` 5336 is version target 416, title `Third Edition` + `Game: Talisman` but no contained_in link → still `high` if Game: + title corroborate (416 version targets, 1-2 per pattern) | **high** if Game: + title; **medium** if Series: | 416 version targets, subset with edition kw → hard | 0/39 version-target strong (but 338697 not version, it's contained_in) |
| **hard_exclude** | Title `Kickstarter`/`Collector`/`3D`/`Deluxe` + `Game:`/`Series:` + `n_version_src≥5` or `n_contained_tgt>0` or shared designer/year/weight (≤5y + ≤0.3w) | e.g., `Catan 3D Collector's` 17419 `Game: Catan` + designer 1 weight diff 0.45 link 1 → hard | **medium** if families + title + year/weight but no direct link | Part of 501 → **hard 189** (37.7% of 501) | 2/39 (331259, 338697) |
| **borderline** | Title contains edition pattern (`edition|anniversary|deluxe|premium|heritage|big box|collector|ultimate|essential|second edition|kickstarter`) **but no** `version`/`contained_in`/`reimplements` link **and** no `Game:` family **or** designer/year/weight diff > thresholds | e.g., `Talisman (Third Edition)` 5336 `Game: Talisman` but designer overlap 0 year diff 10 → borderline; `Fury of Dracula Second` 20963 `Game: Fury of Dracula` + designer 2 year 10 weight 0.33 → year diff 10 >5 → borderline; `Mag·Blast Third` 23142 no Game: family → borderline | **borderline** | 308 (2.10%) | 0/39 borderline hard (all 39 hard editions had link) |
| **borderline** | `Warhammer 40k Seventh Edition` 160044 `Game: Warhammer 40k (Seventh Edition)` but no other game with same `Game:` found → no base to compare | title + Game: but isolated family | **borderline** | — | — |
| **eligible** | No edition/system/reimplement signal, or only `Versions & Editions: ...` family without title pattern | e.g., `Baron Munchausen` 2470 `[]` no link — genuine standalone | — | 13,931 (94.79%) | 37/39 remain eligible after hard 2 removed |

**Counts (`eligibility_evidence.csv` 768 rows, `hard 459 + borderline 308 + eligible 13,931`):**
- Per-pattern: `collectors` 21→hard13 border8, `ultimate` 7→3/3, `kickstarter` 16→hard4 border12 (1 in strong), `second_edition` 112→hard25 border87, `anniversary` 12→4/8, `deluxe` 35→13/22, `3d_edition` 1→hard1 (338697), `premium` 1→1, `big_box` 8→6/1, `edition_any` 501→hard189 border308 eligible4 (2 in strong). All per-pattern `n<50` below CV gate but **structured evidence authoritative regardless of n** — **definition, not statistical model** [empirical + definition].

**Pruned_lists gap (`base_title_missed_dup.csv`):** Base-title 285 dup titles 611 games → 39 corroborated groups 96 games (designer≥1 + \|year\|≤5 + \|weight\|≤0.3) → **87 not pruned but 10 pool (1.9%) 0 strong**; 11 truncated at `n_version_src=100` (Catan etc.) — log_n_impl censored but Q3bFam already proxies via `is_reimpl_num` + `log_n_impl_c` [observed fact]. No CV required — deterministic cleanup [definition].

---

## Per-Game Reason/Evidence (examples, `eligibility_evidence.csv` 768 rows)

| game_id | title | decision | reason | evidence | confidence |
|---|---|---|---|---|---|
| 331259 | Sleeping Gods: Kickstarter Edition | **hard_exclude** | edition_contained_variant | `contained_in via families Game: Sleeping Gods + shared designer 1 year diff 0 weight diff 0.26 link contained_in 255984` | **high** |
| 338697 | CATAN: 3D Edition | **hard_exclude** | edition_contained_variant | `contained_in via families Game: Catan + shared designer 1 year diff 26 weight diff 0.45 link contained_in 13` | **high** |
| 5336 | Talisman (Third Edition) | borderline | edition_title_Game_family_no_corroboration | `title 'Talisman (Third Edition)' + Game: Talisman but no version/contained link, designer overlap 0` | borderline |
| 20963 | Fury of Dracula (Second Edition) | borderline | edition_Game_family_possible | `families Game: Fury of Dracula + designer 2 year 10 weight 0.33 vs base 181279 but weight/year diff larger or no link` | borderline |
| 104162 | Descent: Journeys in the Dark (Second Edition) | borderline | edition_Game_family_possible | `Game: Descent – ... + designer 1 year 7 weight 0.13 vs base 17226 but year diff >5` | borderline |

**All 768 rows include `game_id,title,year,weight,min/max_players,families,designers,n_obs,adj_mean,resid,n_version_tgt/n_contained_tgt,decision,reason,evidence,confidence`** — auditable, with related `game_id`/`family` where applicable [definition].

---

## What remains borderline (not hard)

- **308 borderline** where title suggests edition but structured insufficient (no link, no designer/year/weight corroboration, or `Versions & Editions:` family without title keyword) → **review queue, not hard_exclude by itself** — preserves "do not invent certainty" per §1 example [definition].
- **`n_version` truncation at 100 for 11 games** (Catan 100, etc.) — true version count censored; cannot use raw `n_version` threshold as hard eligibility alone [observed fact].
- **87 base-title corroborated missed** but only 10 in pool 0 strong — narrow gap, concentrated in niche not strong — **no material leakage into strong** but remains second-tier cleanup [empirical].

**Reproduce:** `python scripts/58_pass5_investigation.py` → `eligibility_evidence.csv` (768) + `base_title_missed_dup.csv` (49 rows corroborated missed) · seed 20260824, handle 7 weight-null median 2.0.

## Claim Tags
- **Observed fact:** 33,002 game_links, 59% version, families counts, description tagline max 85, n_version truncation at 100, pruned 269 etc.
- **Empirical finding:** 501 +0.116, per-pattern n<50, base-title 285→39, 87 missed but 0 strong.
- **Definition/eligibility decision:** hard_exclude via deterministic `contained_in`/`version` + `Game:` + designer/year/weight — not statistical, no CV gate required.
- **Assumption:** `Game:` family indicates established system; designer overlap indicates same lineage.
- **Limitation:** n_version censored at 100; description tagline not rich (cannot be primary); base-title heuristic strips edition suffix heuristically.

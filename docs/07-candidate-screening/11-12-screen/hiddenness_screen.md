# Hiddenness Screen — Step 11-12 (§1)

**Generated:** 2026-08-25T12:00:50.761965+00:00Z  · seed 20260824
**Population:** 14,698 games × 287,302 users × 24,146,307 obs (`data/processed/phase2-pass2/`, mu 7.139, reuse severity)
**Starting pool:** 532 games (`adj_mean ≥7.5` AND `resid_Q3bFam ≥0.75`) from `docs/phase2-pass2/step10_quality_underratedness_gates/screening_pool.csv` (median n 256, SE 0.0746, `step10_summary.json`)

## Rule (exactly as stated)

- `<1,700 ratings` → **eligible** (genuinely hidden candidate if other evidence supports)
- `1,700–2,500` → **borderline** (keep flagged, not excluded, but not strong)
- `>2,500` → **exclude** from hidden-gem consideration (not hidden)

 Ratings = **`n_obs` from `rating_observations_pass2`** (count of rating observations in `data/processed/phase2-pass2/rating_observations_pass2.parquet`). This matches Step 10's `n` definition (median 347 population, 256 in pool). `users_rated` from `games_pass2` is documented as sensitivity (correlation with `n_obs` 0.971) — see mapping note below.

Hiddenness is **necessary but not sufficient** — a low-rating-count game is not automatically a hidden gem, merely eligible for next evidence checks.

## Counts per bucket (primary `n_obs` definition)

| Bucket | n_obs | users_rated (sensitivity) | % of 532 |
|---|---|---|---|
| eligible (<1700) | 485 | 464 | 91.2% |
| borderline (1700–2500) | 20 | 25 | 3.8% |
| exclude (>2500) | 27 | 43 | 5.1% |
| total | 532 | 532 | 100% |

**Primary retained for hidden-gem consideration:** 505 games (eligible + borderline). 27 excluded as not hidden (list below).

`users_rated` vs `n_obs` nuance: 16 games have `n_obs ≤2500` but `users_rated >2500` (up to 4008 for `ito` n=979). These are flagged as **popular_via_users_rated** — they survive the `n_obs` rule but are **not genuinely hidden** by the `users_rated` mapping (see `screening_evidence_table.csv` column `popular_via_users`). No games have `n_obs >2500` but `users_rated ≤2500`.

Documented mapping: Step 10 `screening_pool.csv` provides both `n_obs` and `users_rated`; Step 7/10 used `n_obs` as primary volume measure (see `docs/phase2-pass2/step10_quality_underratedness_gates/README.md` “median n 347”). We keep `n_obs` primary for consistency and report `users_rated` sensitivity per-task (“use both if needed”). The 16 discordant cases are treated as **popular not hidden** in §4 audit (see `pass1_failure_mode_audit.md`).

## Boundary examples

### Near 1,700 threshold (1,500–1,900 n_obs, sorted)

| game_id | title | year | n_obs | users_rated | adj_mean | resid_Q3bFam | vol_band | hiddenness |
|---|---|---|---|---|---|---|---|
| 89952 | Carcassonne: 10 Year Special Edition | 2011.0 | 1698 | 1826 | 7.72 | 0.87 | 1k-2.5k | eligible |
| 281474 | Lands of Galzyr | 2022.0 | 1709 | 2317 | 8.19 | 0.83 | 1k-2.5k | borderline |
| 215471 | Photograph | 2016.0 | 1709 | 2196 | 7.91 | 0.77 | 1k-2.5k | borderline |
| 225482 | Seas of Strife | 2015.0 | 1743 | 2632 | 7.88 | 1.14 | 1k-2.5k | borderline |
| 271615 | The Quest for El Dorado: The Golden Temples | 2019.0 | 1744 | 2236 | 8.00 | 0.79 | 1k-2.5k | borderline |
| 225244 | Ticket to Ride: Germany | 2017.0 | 1783 | 2039 | 7.83 | 0.79 | 1k-2.5k | borderline |
| 158889 | Summoner Wars: Alliances Master Set | 2014.0 | 1794 | 1858 | 8.29 | 0.93 | 1k-2.5k | borderline |
| 297985 | Battle Line: Medieval | 2017.0 | 1829 | 2166 | 8.01 | 0.88 | 1k-2.5k | borderline |

Total in 1500–1900 window: 8 games. The 1,700 cutoff falls inside `1k-2.5k` band; median n in pool is 256, so most pool games are well below threshold (91.2% eligible). Borderline band contains only 20 games.

### Near 2,500 threshold (2,300–2,700 n_obs, sorted)

| game_id | title | year | n_obs | users_rated | adj_mean | resid_Q3bFam | vol_band | hiddenness |
|---|---|---|---|---|---|---|---|
| 27976 | Heroscape Master Set: Swarm of the Marro | 2007.0 | 2332 | 2449 | 7.74 | 0.99 | 1k-2.5k | borderline |
| 82420 | Summoner Wars: Guild Dwarves vs Cave Goblins | 2009.0 | 2362 | 2427 | 7.79 | 0.86 | 1k-2.5k | borderline |
| 1301 | Netrunner | 1996.0 | 2392 | 2527 | 7.78 | 0.77 | 1k-2.5k | borderline |
| 252526 | Pictomania (Second Edition) | 2018.0 | 2397 | 2774 | 7.96 | 0.98 | 1k-2.5k | borderline |
| 38863 | The Rich and the Good | 2008.0 | 2484 | 2747 | 7.67 | 0.84 | 1k-2.5k | borderline |
| 284777 | Unmatched: Jurassic Park – InGen vs Raptors | 2020.0 | 2488 | 2934 | 8.24 | 1.06 | 1k-2.5k | borderline |
| 335764 | Unmatched: Battle of Legends, Volume Two | 2021.0 | 2647 | 3573 | 8.38 | 0.78 | 2.5k-5k | exclude |

Total in 2300–2700 window: 7 games.

### Obviously popular excluded (>2,500) — top examples

| game_id | title | n_obs | users_rated | adj_mean | rank_current | bayes_rating | hiddenness |
|---|---|---|---|---|---|---|---|
| 118 | Modern Art | 23096 | 25690 | 7.89 | 222.0 | 7.3312 | exclude |
| 92828 | Dixit: Odyssey | 21146 | 23119 | 7.59 | 357.0 | 7.1412 | exclude |
| 5 | Acquire | 20432 | 22332 | 7.66 | 367.0 | 7.1287 | exclude |
| 46213 | Telestrations | 18877 | 20944 | 7.65 | 354.0 | 7.1456 | exclude |
| 215 | Tichu | 15687 | 16985 | 7.96 | 251.0 | 7.2747 | exclude |
| 220 | High Society | 14540 | 16848 | 7.57 | 535.0 | 6.9749 | exclude |
| 150 | PitchCar | 11175 | 11831 | 7.62 | 531.0 | 6.9777 | exclude |
| 266507 | Clank! Legacy: Acquisitions Incorporated | 9745 | 11489 | 8.83 | 28.0 | 7.9306 | exclude |
| 397598 | Dune: Imperium – Uprising | 8869 | 19653 | 9.05 | 5.0 | 8.2549 | exclude |
| 3201 | Lord of the Rings: The Confrontation | 6909 | 7238 | 7.55 | 811.0 | 6.7692 | exclude |
| 156546 | Monikers | 6607 | 7906 | 8.08 | 303.0 | 7.2031 | exclude |
| 18833 | Lord of the Rings: The Confrontation | 6420 | 6778 | 7.85 | 556.0 | 6.9560 | exclude |
| 1353 | Time's Up! | 5962 | 6292 | 7.64 | 795.0 | 6.7776 | exclude |
| 108687 | Puerto Rico | 5629 | 6145 | 8.61 | nan | 7.4773 | exclude |
| 16747 | Tumblin' Dice | 4786 | 5252 | 7.62 | 906.0 | 6.7092 | exclude |

Excluded 27 games include clearly popular titles (e.g., Modern Art 23096, Dixit: Odyssey 21146, Acquire 20432) that would dominate any ranking if not excluded — hiddenness filter correctly removes them.

### Popular via users_rated nuance (n_obs ≤2500 but users_rated >2500) — flagged not hidden

| game_id | title | n_obs | users_rated | adj_mean | rank_current | hiddenness n_obs | users_rated bucket |
|---|---|---|---|---|---|---|---|
| 422732 | Agent Avenue | 596 | 7067 | 8.17 | 520.0 | eligible | exclude |
| 327778 | ito | 979 | 4008 | 7.71 | 1051.0 | eligible | exclude |
| 424219 | Zenith | 167 | 3973 | 8.32 | 528.0 | eligible | exclude |
| 371433 | Terrorscape | 1384 | 3573 | 8.44 | 601.0 | eligible | exclude |
| 266722 | Rumble Nation | 1228 | 3426 | 7.97 | 1037.0 | eligible | exclude |
| 387866 | Star Wars: Unlimited | 2151 | 3294 | 8.36 | 632.0 | borderline | exclude |
| 415776 | Kingdom Legacy: Feudal Kingdom | 565 | 3285 | 8.71 | 605.0 | eligible | exclude |
| 380619 | Cyclades: Legendary Edition | 161 | 3147 | 8.64 | 609.0 | eligible | exclude |
| 295564 | Unmatched Game System | 2193 | 3056 | 8.53 | 555.0 | borderline | exclude |
| 284777 | Unmatched: Jurassic Park – InGen vs Raptors | 2488 | 2934 | 8.24 | 679.0 | borderline | exclude |
| 252526 | Pictomania (Second Edition) | 2397 | 2774 | 7.96 | 1101.0 | borderline | exclude |
| 38863 | The Rich and the Good | 2484 | 2747 | 7.67 | 1648.0 | borderline | exclude |
| 355997 | Thunder Road: Vendetta – Maximum Chrome | 1069 | 2687 | 8.91 | nan | eligible | exclude |
| 225482 | Seas of Strife | 1743 | 2632 | 7.88 | 1386.0 | borderline | exclude |
| 219650 | Arydia: The Paths We Dare Tread | 637 | 2581 | 9.39 | 403.0 | eligible | exclude |
| 1301 | Netrunner | 2392 | 2527 | 7.78 | 1433.0 | borderline | exclude |

Count: 16 games (3.0% of pool). All are **flagged** `popular_via_users=True` and treated as **not hidden** (see §4 audit) even though they pass the primary `n_obs` eligible/borderline cut. Example `ito` (n_obs 979, users_rated 4008) and `Unmatched Game System` (2193/3056) illustrate the nuance — `n_obs` counts rating observations in `rating_observations_pass2` (24.1M), while `users_rated` from `games_pass2` reflects dump voters; correlation 0.971 but divergence matters at boundary.

## Implications

- Hiddenness leaves 505 candidates for evidence screening (§2-3), not 532 — the 27 excluded plus 16 popular_nuance flagged reduce genuinely hidden eligible pool to ~476 truly low-visibility games.
- Remaining eligibility is still **large** (485 eligible, 91%), so quality/underratedness + audience/propensity evidence must do the heavy lifting — hiddenness alone is not discriminating.

**Reproduce:** `python scripts/51_step11-12_hidden_gem_screen.py` (loads `screening_pool.csv` 532, games_pass2, links, audience etc.; no 24M wide sort, seed 20260824)

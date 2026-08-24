# Exclusions and Deduplication Log (INTERMEDIATE / NOT FINAL)

> **Status:** INTERMEDIATE — explicit exclusion/dedup decisions with reasons and related game_id where applicable. Preserves information for manual review rather than binary pass/fail. All 16549 estimation games have `screening_disposition` + `reason` in `underrated_candidates.csv`.

## Summary
- `excluded_low_evidence` (`n<100` or weak z): **1272**
- `excluded_unreleased` (`year≥2025`): **361** (population has 361 games 2025+; 211 with positive residual)
- `flagged_duplicate_title` (`title_clean` duplicate, keep most popular): **206**
- `flagged_shadowed_by_more_popular_related` (4× users rule on `game_links` reimplementation/version): **136**
- `flagged_wellknown` (`users_rated≥20000` or `rank<500`): **530** (meeting robust criteria but conflicts with hidden-gem objective; kept for audit)
- `not_underrated` (`resid≤0` with `n≥100`): **6800**

## Method notes (per task)
- Never treat large residual at low n as equivalent to same residual at high n — report `resid, SE, n, z=resid/SE, lb_adj` alongside each other.
- `post_SD = 1/√(1/0.746 + n/1.426)` (EB `sigma_alpha² 0.746`, `sigma_e² 1.426`); at `n=50` SE 0.169 vs `n=3000` SE 0.022 (7.7×).
- Stability: `residual_overlap.csv` Jaccard/spearman Q3b vs Q3 .675/.985, Q3b vs Q4 .579/.958, WLS vs OLS Q3b .737/.963; CV R² .582 Q3b vs .570 Q3 vs .585 Q4.
- Popularity context: `n_active` tertiles/deciles, not arbitrary post-hoc groups (`n_decile` D1-D10 p10 100 median 293 p90 2796; tertiles low <163 mid 163-664 high >664).
- Release: already filtered but flag 2025+ edge cases (396 in 2025, 27 in 2026).
- Duplicates: `game_links` `rel=reimplementation/reimplements/version` (1,538 reimplementation links), `is_reimplementation` flag, `title_clean` duplicates, `families`; example Twilight Struggle 12333 vs Red Sea 300192; Small World 40692 vs Designer Edition 140135.

## Exclusion / dedup table (all flagged/excluded, sorted by disposition then residual desc)

| game_id | title | year | n | resid | SE | z | lb_adj | decile | users | rank | disposition | related_game_id | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 435330 | Pondscape | 2025 | 1 | 3.94 | 1.194 | 3.3 | 9.21 | D1 | 874 | 3684 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 428589 | Thief's Market | 2025 | 3 | 2.88 | 0.689 | 4.2 | 9.11 | D1 | 137 | 9605 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 434131 | Tolleno | 2025 | 1 | 2.22 | 1.194 | 1.9 | 7.50 | D1 | 140 | 17449 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 436804 | Opération Zèbre | 2025 | 1 | 2.16 | 1.194 | 1.8 | 6.97 | D1 | 137 | 10158 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 436591 | Brightcast | 2025 | 2 | 2.15 | 0.844 | 2.5 | 7.72 | D1 | 141 | 10618 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 436038 | Hercules and the 12 Labors | 2025 | 2 | 2.12 | 0.844 | 2.5 | 8.25 | D1 | 546 | 4466 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 428284 | Here Lies | 2025 | 2 | 2.03 | 0.844 | 2.4 | 7.96 | D1 | 240 | 6644 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 428989 | EcoLogic: Europe | 2025 | 2 | 1.92 | 0.844 | 2.3 | 8.23 | D1 | 155 | 9540 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 414927 | Parks & Potions | 2025 | 14 | 1.82 | 0.319 | 5.7 | 8.58 | D1 | 317 | 7641 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 351773 | AVíO      AVíO a game in which every t | 2025 | 1 | 1.76 | 1.194 | 1.5 | 7.14 | D1 | 101 | 11689 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 436936 | No Loose Ends | 2025 | 2 | 1.72 | 0.844 | 2.0 | 7.76 | D1 | 529 | 4076 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 347909 | Rogue Angels: Legacy of the Burning Su | 2026 | 86 | 1.60 | 0.129 | 12.4 | 9.18 | D1 | 135 | 8260 | excluded_unreleased | — | year 2026 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 434283 | Habemus Papam | 2025 | 2 | 1.59 | 0.844 | 1.9 | 7.70 | D1 | 244 | 9270 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 435367 | Survivor: The Tribe Has Spoken | 2025 | 5 | 1.54 | 0.534 | 2.9 | 7.69 | D1 | 227 | 10820 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 421165 | Pantheum: Demigods of Olympia | 2025 | 7 | 1.49 | 0.451 | 3.3 | 8.44 | D1 | 230 | 9823 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 400498 | Light Speed: Arena | 2025 | 72 | 1.48 | 0.141 | 10.5 | 8.52 | D1 | 1666 | 1942 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 364544 | Witchbound | 2025 | 9 | 1.47 | 0.398 | 3.7 | 8.04 | D1 | 222 | 7985 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 375557 | I Made You a Mixtape | 2025 | 16 | 1.46 | 0.299 | 4.9 | 8.05 | D1 | 532 | 5071 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 437919 | Instinkt | 2025 | 2 | 1.45 | 0.844 | 1.7 | 7.47 | D1 | 194 | 8608 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 386166 | Santorini: Pantheon Edition | 2025 | 88 | 1.43 | 0.127 | 11.2 | 8.69 | D1 | 1254 | 1352 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 434848 | Adventurous | 2025 | 1 | 1.43 | 1.194 | 1.2 | 6.36 | D1 | 247 | 7619 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 436907 | Crits & Tricks   (2026)      A tavern  | 2026 | 1 | 1.40 | 1.194 | 1.2 | 6.78 | D1 | 218 | 7272 | excluded_unreleased | — | year 2026 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 436561 | Timber Town | 2025 | 1 | 1.40 | 1.194 | 1.2 | 6.60 | D1 | 552 | 4423 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 396619 | Children of Morta: The Board Game | 2025 | 10 | 1.39 | 0.378 | 3.7 | 8.27 | D1 | 163 | 8436 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 436010 | Crystalla | 2025 | 1 | 1.38 | 1.194 | 1.2 | 6.71 | D1 | 132 | 12151 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 430809 | The DUNGENERATOR: DIE in a Dungeon | 2025 | 7 | 1.37 | 0.451 | 3.0 | 8.10 | D1 | 112 | 8842 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 426355 | Onoda | 2025 | 8 | 1.35 | 0.422 | 3.2 | 8.12 | D1 | 335 | 6989 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 395315 | Sudds & Malone | 2026 | 3 | 1.31 | 0.689 | 1.9 | 7.94 | D1 | 123 | 9016 | excluded_unreleased | — | year 2026 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 429861 | Ace of Spades | 2025 | 6 | 1.29 | 0.487 | 2.6 | 8.05 | D1 | 1266 | 2590 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 433908 | Gatsby | 2025 | 1 | 1.28 | 1.194 | 1.1 | 6.59 | D1 | 652 | 5669 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 401636 | Tacta | 2025 | 4 | 1.27 | 0.597 | 2.1 | 7.43 | D1 | 2331 | 2932 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 386860 | Farm Hand      Pocket-sized farm anima | 2025 | 52 | 1.24 | 0.166 | 7.5 | 8.11 | D1 | 426 | 5551 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 379546 | Grand Central Skyport | 2025 | 4 | 1.23 | 0.597 | 2.1 | 7.66 | D1 | 208 | 8991 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 415181 | Flash Point: Legacy of Flame | 2025 | 3 | 1.14 | 0.689 | 1.7 | 7.35 | D1 | 275 | 6418 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 420033 | Vantage | 2025 | 16 | 1.14 | 0.299 | 3.8 | 8.09 | D1 | 7291 | 191 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 433339 | 6 nimmt! Baron Oxx | 2025 | 7 | 1.13 | 0.451 | 2.5 | 7.39 | D1 | 436 | 5644 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 411033 | Wine Cellar | 2025 | 26 | 1.13 | 0.234 | 4.8 | 8.05 | D1 | 1289 | 3015 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 432811 | Marbleous | 2025 | 2 | 1.12 | 0.844 | 1.3 | 6.68 | D1 | 118 | 15446 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 382894 | The Hunters a.d. 1492 | 2025 | 49 | 1.11 | 0.171 | 6.5 | 8.90 | D1 | 321 | 6114 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 411860 | Unmatched: The Witcher – Steel and Sil | 2025 | 57 | 1.10 | 0.158 | 7.0 | 8.56 | D1 | 806 | 2349 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 437337 | Abroad | 2025 | 3 | 1.08 | 0.689 | 1.6 | 7.69 | D1 | 491 | 4336 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 428308 | Unmatched: Muhammad Ali vs Bruce Lee | 2025 | 5 | 1.08 | 0.534 | 2.0 | 7.40 | D1 | 352 | — | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 423553 | Above and Below: Haunted | 2025 | 6 | 1.08 | 0.487 | 2.2 | 8.09 | D1 | 556 | 3328 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 429438 | Ayar: Children of the Sun | 2025 | 1 | 1.07 | 1.194 | 0.9 | 6.92 | D1 | 997 | 2318 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 438402 | Forest Shuffle: Dartmoor | 2025 | 1 | 1.06 | 1.194 | 0.9 | 6.52 | D1 | 2694 | 1019 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 421529 | Barony (Royal Edition) | 2025 | 10 | 1.06 | 0.378 | 2.8 | 7.93 | D1 | 205 | 6817 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 408828 | Casinopolis | 2025 | 3 | 1.05 | 0.689 | 1.5 | 7.11 | D1 | 227 | 6784 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 431929 | Onward      Draft champions, slay mons | 2025 | 2 | 1.04 | 0.844 | 1.2 | 7.62 | D1 | 382 | 4391 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 430533 | Formaggio   (2026)      Craft Italian  | 2025 | 2 | 1.04 | 0.844 | 1.2 | 7.13 | D1 | 1420 | 1463 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 219650 | Arydia: The Paths We Dare Tread | 2025 | 641 | 1.02 | 0.047 | 21.6 | 9.30 | D7 | 2581 | 403 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 425549 | Moon Colony Bloodbath | 2025 | 17 | 1.01 | 0.290 | 3.5 | 8.07 | D1 | 6435 | 474 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 426513 | Emberleaf | 2025 | 7 | 1.01 | 0.451 | 2.2 | 8.28 | D1 | 2179 | 1371 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 414117 | Wroth | 2025 | 13 | 1.00 | 0.331 | 3.0 | 8.00 | D1 | 1530 | 2095 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 426945 | Baseball Highlights: 2045 – Bases Load | 2025 | 23 | 0.99 | 0.249 | 4.0 | 8.21 | D1 | 318 | — | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 424929 | Burgle Bros 3: Future Flip | 2026 | 2 | 0.95 | 0.844 | 1.1 | 7.20 | D1 | 117 | 10299 | excluded_unreleased | — | year 2026 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 434141 | Flow | 2025 | 19 | 0.93 | 0.274 | 3.4 | 7.21 | D1 | 238 | 12304 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 422008 | Signal | 2025 | 1 | 0.93 | 1.194 | 0.8 | 6.17 | D1 | 188 | 8572 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 388367 | Innovation Ultimate | 2025 | 72 | 0.93 | 0.141 | 6.6 | 8.81 | D1 | 1397 | 1161 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 377041 | Northwest | 2025 | 2 | 0.92 | 0.844 | 1.1 | 6.86 | D1 | 171 | 9117 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 412731 | One-Hit Heroes | 2025 | 6 | 0.92 | 0.487 | 1.9 | 7.45 | D1 | 371 | 5529 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 411861 | Unmatched: The Witcher – Realms Fall | 2025 | 58 | 0.92 | 0.157 | 5.8 | 8.46 | D1 | 642 | 2787 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 396706 | The Massive-Verse Fighting Card Game | 2025 | 15 | 0.91 | 0.308 | 3.0 | 7.80 | D1 | 179 | 12728 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 429849 | Red Carpet | 2025 | 1 | 0.89 | 1.194 | 0.7 | 5.83 | D1 | 265 | 8816 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 419130 | HUTAN: Life in the Rainforest | 2025 | 14 | 0.87 | 0.319 | 2.7 | 7.92 | D1 | 1163 | 3333 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 425276 | Unmatched Adventures: Teenage Mutant N | 2025 | 24 | 0.85 | 0.244 | 3.5 | 7.82 | D1 | 1034 | 1725 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 419645 | Mindbug: Battlefruit Galaxy | 2025 | 3 | 0.84 | 0.689 | 1.2 | 7.11 | D1 | 286 | 4940 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 429851 | Quorum | 2025 | 4 | 0.84 | 0.597 | 1.4 | 7.41 | D1 | 539 | 5703 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 435360 | Waddle | 2025 | 2 | 0.83 | 0.844 | 1.0 | 6.57 | D1 | 748 | 4338 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 404422 | Biathlon Blast | 2025 | 4 | 0.81 | 0.597 | 1.4 | 7.24 | D1 | 116 | 10294 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 429766 | EGO | 2025 | 12 | 0.80 | 0.345 | 2.3 | 7.87 | D1 | 636 | 4260 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 413251 | Echoes of Emperors | 2025 | 6 | 0.79 | 0.487 | 1.6 | 7.84 | D1 | 143 | 8199 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 410628 | Keyside | 2025 | 2 | 0.79 | 0.844 | 0.9 | 7.59 | D1 | 405 | 4743 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 432456 | Revolve! | 2025 | 23 | 0.77 | 0.249 | 3.1 | 7.58 | D1 | 2359 | 1731 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 428638 | Vegas Strip | 2025 | 4 | 0.76 | 0.597 | 1.3 | 7.36 | D1 | 430 | 6887 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 429293 | The Fellowship of the Ring: Trick-Taki | 2025 | 728 | 0.73 | 0.044 | 16.5 | 8.32 | D8 | 10816 | 133 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 415465 | Citizens of the Spark | 2025 | 14 | 0.73 | 0.319 | 2.3 | 7.78 | D1 | 813 | 3378 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 413838 | Sakana Stack | 2025 | 14 | 0.73 | 0.319 | 2.3 | 7.40 | D1 | 110 | 12998 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 425505 | Storyfold: Wildwoods | 2025 | 8 | 0.71 | 0.422 | 1.7 | 7.43 | D1 | 671 | 3331 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 424507 | Aspens | 2025 | 13 | 0.71 | 0.331 | 2.1 | 7.50 | D1 | 426 | 5655 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 437334 | The Hanging Gardens | 2025 | 2 | 0.69 | 0.844 | 0.8 | 6.68 | D1 | 474 | 7049 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 412963 | Regicide Legacy | 2025 | 9 | 0.69 | 0.398 | 1.7 | 7.63 | D1 | 636 | 2680 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 436217 | The Lord of the Rings: Fate of the Fel | 2025 | 12 | 0.69 | 0.345 | 2.0 | 8.13 | D1 | 10913 | 65 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 424219 | Zenith | 2025 | 167 | 0.69 | 0.092 | 7.4 | 8.14 | D4 | 3973 | 528 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 437478 | IYE | 2025 | 6 | 0.65 | 0.487 | 1.3 | 7.25 | D1 | 164 | 14025 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 419378 | Vicious Gardens | 2025 | 3 | 0.65 | 0.689 | 0.9 | 6.79 | D1 | 329 | 6954 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 393871 | Shards of Infinity: Saga Collection | 2025 | 64 | 0.64 | 0.149 | 4.3 | 7.84 | D1 | 301 | — | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 399318 | Joyride Duel: Next Gen | 2025 | 28 | 0.64 | 0.226 | 2.8 | 7.85 | D1 | 154 | 8681 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 402814 | Peaks | 2025 | 12 | 0.63 | 0.345 | 1.8 | 7.81 | D1 | 345 | 5688 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 425765 | Ministry of Lost Things: Case 1 – Lint | 2025 | 1 | 0.63 | 1.194 | 0.5 | 5.99 | D1 | 285 | 5629 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 359288 | TwinStar Valley | 2025 | 14 | 0.62 | 0.319 | 1.9 | 7.80 | D1 | 134 | 11057 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 356080 | The Elder Scrolls: Betrayal of the Sec | 2025 | 205 | 0.61 | 0.083 | 7.4 | 8.94 | D4 | 4079 | 156 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 437356 | Scales of Fate   (2026)      Gods go h | 2025 | 1 | 0.61 | 1.194 | 0.5 | 6.11 | D1 | 552 | 3440 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 420915 | Ichor | 2025 | 19 | 0.60 | 0.274 | 2.2 | 7.76 | D1 | 763 | 3685 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 415025 | Sprocketforge | 2025 | 4 | 0.60 | 0.597 | 1.0 | 7.14 | D1 | 137 | 9658 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 431038 | Azul Duel | 2025 | 22 | 0.59 | 0.255 | 2.3 | 8.01 | D1 | 3114 | 1870 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 407804 | Sibille | 2025 | 15 | 0.59 | 0.308 | 1.9 | 8.06 | D1 | 108 | 11989 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 383037 | Combat Commander: Europe/Med. – 20th A | 2025 | 3 | 0.58 | 0.689 | 0.8 | 7.89 | D1 | 114 | — | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 420498 | Unstoppable | 2025 | 88 | 0.58 | 0.127 | 4.6 | 8.34 | D1 | 2121 | 788 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 412123 | Ape Town | 2025 | 1 | 0.58 | 1.194 | 0.5 | 5.87 | D1 | 203 | 7964 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 405296 | For All Mankind | 2025 | 9 | 0.58 | 0.398 | 1.4 | 7.30 | D1 | 158 | 10426 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 429860 | Transgalactica | 2025 | 5 | 0.56 | 0.534 | 1.1 | 7.85 | D1 | 586 | 7497 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 421872 | Shadow Moon Syndicates | 2026 | 7 | 0.56 | 0.451 | 1.2 | 7.66 | D1 | 139 | 8975 | excluded_unreleased | — | year 2026 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 420914 | Iliad | 2025 | 29 | 0.56 | 0.222 | 2.5 | 7.83 | D1 | 1434 | 1878 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 429446 | Moirai | 2025 | 2 | 0.55 | 0.844 | 0.6 | 6.29 | D1 | 304 | 7796 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 429767 | ORBIT | 2025 | 8 | 0.53 | 0.422 | 1.3 | 7.19 | D1 | 852 | 3127 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 407233 | Tenby | 2025 | 23 | 0.52 | 0.249 | 2.1 | 7.72 | D1 | 1388 | 1984 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 424981 | Eternal Decks | 2025 | 59 | 0.52 | 0.155 | 3.3 | 8.24 | D1 | 2902 | 583 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 431280 | 2 Win | 2025 | 3 | 0.51 | 0.689 | 0.7 | 6.36 | D1 | 342 | 7389 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 433007 | Cascadia Junior | 2025 | 10 | 0.51 | 0.378 | 1.3 | 7.05 | D1 | 398 | 5915 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 381246 | S.T.A.L.K.E.R. The Board Game | 2025 | 180 | 0.50 | 0.089 | 5.7 | 8.50 | D4 | 1210 | 1965 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 421395 | Top Tier | 2025 | 13 | 0.50 | 0.331 | 1.5 | 6.86 | D1 | 100 | 15398 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 393429 | Critter Kitchen | 2025 | 107 | 0.50 | 0.115 | 4.3 | 8.03 | D2 | 3428 | 841 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 423561 | HeroQuest: First Light | 2025 | 8 | 0.50 | 0.422 | 1.2 | 6.99 | D1 | 338 | 5608 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 428636 | Oddland | 2025 | 5 | 0.49 | 0.534 | 0.9 | 6.75 | D1 | 558 | 5190 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 422796 | RA and Write | 2025 | 8 | 0.48 | 0.422 | 1.1 | 6.96 | D1 | 461 | 5081 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 434356 | Micro Hero: Hercules | 2025 | 6 | 0.46 | 0.487 | 0.9 | 6.96 | D1 | 337 | 6707 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 421606 | Knitting Circle | 2025 | 23 | 0.46 | 0.249 | 1.8 | 7.73 | D1 | 1042 | 3064 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 408718 | Spokes | 2026 | 19 | 0.44 | 0.274 | 1.6 | 7.60 | D1 | 216 | 7772 | excluded_unreleased | — | year 2026 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 379761 | Natera: New Beginning | 2025 | 64 | 0.44 | 0.149 | 2.9 | 8.08 | D1 | 543 | 3847 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 410518 | Spire's End: Rangitaki | 2025 | 9 | 0.44 | 0.398 | 1.1 | 7.43 | D1 | 121 | 9633 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 419291 | A Wayfarer's Tale: The Journey Begins | 2025 | 6 | 0.44 | 0.487 | 0.9 | 6.89 | D1 | 271 | 6095 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 428582 | Dark Tomb: The Ice Chasers | 2025 | 2 | 0.43 | 0.844 | 0.5 | 5.93 | D1 | 117 | 12008 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 416232 | Square One | 2025 | 10 | 0.42 | 0.378 | 1.1 | 7.31 | D1 | 354 | 6127 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 345014 | The Bell of Treason: 1938 Munich Crisi | 2025 | 10 | 0.41 | 0.378 | 1.1 | 7.78 | D1 | 132 | 8515 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 421974 | Pirates of the High Teas | 2026 | 5 | 0.41 | 0.534 | 0.8 | 7.10 | D1 | 194 | 7998 | excluded_unreleased | — | year 2026 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 274471 | Malhya: Lands of Legends | 2025 | 85 | 0.41 | 0.130 | 3.2 | 8.47 | D1 | 397 | 6218 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 437705 | Horrified: Dungeons & Dragons | 2025 | 1 | 0.41 | 1.194 | 0.3 | 5.67 | D1 | 1076 | 3090 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 432451 | Symbiose | 2025 | 1 | 0.39 | 1.194 | 0.3 | 5.26 | D1 | 1092 | 3997 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 419642 | Mindbug: Battlefruit Kingdom | 2025 | 6 | 0.39 | 0.487 | 0.8 | 7.28 | D1 | 390 | 4057 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 435423 | Alibis | 2025 | 9 | 0.39 | 0.398 | 1.0 | 6.93 | D1 | 866 | 3429 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 431994 | Propolis | 2025 | 3 | 0.38 | 0.689 | 0.6 | 6.67 | D1 | 1410 | 2890 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 381247 | Dragon Eclipse | 2025 | 147 | 0.38 | 0.098 | 3.9 | 8.12 | D3 | 1509 | 1518 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 432527 | Ethnos: 2nd Edition | 2025 | 135 | 0.37 | 0.103 | 3.6 | 7.83 | D3 | 1226 | 2176 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 399959 | Click A Tree | 2025 | 1 | 0.37 | 1.194 | 0.3 | 5.88 | D1 | 254 | 8026 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 430563 | Popcorn | 2025 | 2 | 0.35 | 0.844 | 0.4 | 6.10 | D1 | 944 | 4177 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 383117 | Cathood | 2025 | 5 | 0.35 | 0.534 | 0.6 | 7.07 | D1 | 295 | 8516 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 377991 | Moon Bunny | 2025 | 9 | 0.34 | 0.398 | 0.9 | 7.19 | D1 | 212 | 8106 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 395834 | Aberration | 2025 | 7 | 0.33 | 0.451 | 0.7 | 7.25 | D1 | 149 | 8514 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 426229 | Overparked | 2025 | 47 | 0.33 | 0.174 | 1.9 | 7.54 | D1 | 287 | 6465 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 422541 | Star Trek: Captain's Chair | 2025 | 73 | 0.33 | 0.140 | 2.3 | 8.27 | D1 | 1985 | 689 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 413303 | Rise of the Wastelands | 2025 | 13 | 0.32 | 0.331 | 1.0 | 7.69 | D1 | 143 | 9283 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 428440 | Shallow Sea | 2025 | 34 | 0.31 | 0.205 | 1.5 | 7.67 | D1 | 1588 | 1521 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 430902 | La Der des Ders: The War to End War | 2025 | 1 | 0.31 | 1.194 | 0.3 | 6.20 | D1 | 100 | 9568 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 437698 | Between Two Castles Essential Edition | 2025 | 3 | 0.31 | 0.689 | 0.4 | 6.75 | D1 | 153 | — | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 433384 | Rival Cities | 2025 | 2 | 0.30 | 0.844 | 0.4 | 6.57 | D1 | 734 | 3564 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 431248 | For a Crown | 2025 | 37 | 0.30 | 0.196 | 1.5 | 7.30 | D1 | 1043 | 3825 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 381248 | Nemesis: Retaliation | 2025 | 114 | 0.30 | 0.112 | 2.7 | 8.32 | D2 | 3950 | 264 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 438481 | Happy Mochi | 2025 | 3 | 0.30 | 0.689 | 0.4 | 6.15 | D1 | 567 | 6789 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 372831 | Potions of Azerland | 2025 | 136 | 0.28 | 0.102 | 2.7 | 7.84 | D3 | 561 | 5135 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 420931 | Spooktacular | 2025 | 16 | 0.28 | 0.299 | 0.9 | 6.76 | D1 | 1301 | 2366 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 415108 | Crisps      Shed your cards as fast as | 2025 | 164 | 0.27 | 0.093 | 2.9 | 7.52 | D4 | 394 | 5585 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 373667 | House of Fado | 2025 | 86 | 0.27 | 0.129 | 2.1 | 7.94 | D1 | 1258 | 2309 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 369897 | Everbloom | 2025 | 5 | 0.26 | 0.534 | 0.5 | 7.19 | D1 | 100 | 11718 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 375459 | Speakeasy | 2025 | 173 | 0.25 | 0.091 | 2.8 | 8.69 | D4 | 4303 | 229 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 432716 | Leaders | 2025 | 1 | 0.24 | 1.194 | 0.2 | 5.56 | D1 | 1098 | 3117 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 431305 | Great Western Trail: El Paso | 2025 | 62 | 0.24 | 0.152 | 1.6 | 7.95 | D1 | 1889 | 2284 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 415815 | Aces & Armor | 2025 | 5 | 0.23 | 0.534 | 0.4 | 7.35 | D1 | 125 | 10938 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 418062 | Railroad Tiles | 2025 | 50 | 0.23 | 0.169 | 1.4 | 7.37 | D1 | 1724 | 1785 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 405994 | New Cold War | 2025 | 16 | 0.22 | 0.299 | 0.7 | 8.14 | D1 | 271 | 6610 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 329534 | In the Shadows: Resistance in France 1 | 2025 | 14 | 0.22 | 0.319 | 0.7 | 7.66 | D1 | 250 | 6921 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 424816 | Jungo | 2025 | 28 | 0.22 | 0.226 | 1.0 | 6.98 | D1 | 1965 | 2287 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 434172 | Excalibur | 2026 | 5 | 0.22 | 0.534 | 0.4 | 6.52 | D1 | 1155 | 2906 | excluded_unreleased | — | year 2026 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 391752 | Steam Power | 2025 | 198 | 0.22 | 0.085 | 2.6 | 7.64 | D4 | 999 | 2851 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 387560 | Perch | 2025 | 60 | 0.22 | 0.154 | 1.4 | 7.63 | D1 | 1110 | 3350 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 396704 | Mayan Curse | 2025 | 36 | 0.22 | 0.199 | 1.1 | 7.34 | D1 | 152 | 10926 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 371330 | Luthier | 2025 | 141 | 0.21 | 0.101 | 2.1 | 8.43 | D3 | 3262 | 522 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 386447 | Storm Raiders | 2025 | 95 | 0.21 | 0.123 | 1.7 | 7.59 | D1 | 339 | 6047 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 415524 | Super Boss Monster | 2025 | 6 | 0.21 | 0.487 | 0.4 | 6.94 | D1 | 528 | 5599 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 434654 | Toy Battle | 2025 | 1 | 0.21 | 1.194 | 0.2 | 5.54 | D1 | 7228 | 305 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 416079 | March of the Ants: Evolved Edition | 2025 | 22 | 0.20 | 0.255 | 0.8 | 7.83 | D1 | 1069 | 2554 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 408840 | Glass Garden | 2025 | 8 | 0.19 | 0.422 | 0.5 | 7.01 | D1 | 177 | 8739 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 402674 | All Aboard! | 2025 | 4 | 0.19 | 0.597 | 0.3 | 6.49 | D1 | 281 | 7506 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 417518 | Floristry | 2025 | 27 | 0.19 | 0.230 | 0.8 | 7.08 | D1 | 455 | 5916 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 396895 | Corps of Discovery: A Game Set in the  | 2025 | 46 | 0.19 | 0.176 | 1.1 | 7.78 | D1 | 1398 | 1986 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 404356 | Little Soldiers | 2025 | 1 | 0.18 | 1.194 | 0.2 | 5.79 | D1 | 208 | 9979 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 327082 | Garden Rush | 2025 | 15 | 0.18 | 0.308 | 0.6 | 7.00 | D1 | 396 | 8641 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 274525 | Soul Raiders | 2025 | 98 | 0.18 | 0.121 | 1.5 | 7.74 | D1 | 209 | 8415 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 430817 | Wraith & The Giants | 2025 | 1 | 0.17 | 1.194 | 0.1 | 5.56 | D1 | 140 | 9468 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 391720 | The String Railway Collection | 2025 | 70 | 0.17 | 0.143 | 1.2 | 7.22 | D1 | 180 | — | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 391137 | Galactic Cruise | 2025 | 270 | 0.17 | 0.073 | 2.3 | 8.55 | D5 | 7742 | 110 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 429845 | Jisogi: Anime Studio Tycoon | 2025 | 9 | 0.16 | 0.398 | 0.4 | 7.02 | D1 | 653 | 3702 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 434906 | Tag Team | 2025 | 2 | 0.16 | 0.844 | 0.2 | 6.17 | D1 | 4379 | 745 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 364356 | Company of Heroes: 2nd Edition | 2025 | 56 | 0.16 | 0.160 | 1.0 | 8.58 | D1 | 518 | 3475 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 413548 | Builders of Sylvan Dale | 2025 | 16 | 0.16 | 0.299 | 0.5 | 7.00 | D1 | 109 | 16673 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 431998 | Point Galaxy | 2025 | 3 | 0.14 | 0.689 | 0.2 | 6.41 | D1 | 1341 | 2832 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 389031 | Fighting Fantasy Adventures | 2025 | 12 | 0.14 | 0.345 | 0.4 | 6.73 | D1 | 183 | 9499 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 408636 | Skara Brae | 2025 | 38 | 0.13 | 0.194 | 0.7 | 7.70 | D1 | 1776 | 1670 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 410238 | Logic & Lore | 2025 | 8 | 0.12 | 0.422 | 0.3 | 6.99 | D1 | 232 | 6753 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 422041 | Aquatica: Duellum | 2025 | 12 | 0.12 | 0.345 | 0.4 | 7.27 | D1 | 137 | 10842 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 419908 | Katmai: The Bears of Brooks River | 2025 | 11 | 0.12 | 0.360 | 0.3 | 7.27 | D1 | 145 | 11482 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 389113 | RIVALS | 2025 | 12 | 0.12 | 0.345 | 0.3 | 7.39 | D1 | 192 | 8950 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 399822 | Fate: Defenders of Grimheim | 2025 | 73 | 0.11 | 0.140 | 0.8 | 7.97 | D1 | 1141 | 2164 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 436516 | Merchants of Andromeda | 2025 | 7 | 0.11 | 0.451 | 0.2 | 7.13 | D1 | 296 | 7914 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 421570 | Misfit Heroes | 2026 | 16 | 0.10 | 0.299 | 0.3 | 7.29 | D1 | 286 | 6629 | excluded_unreleased | — | year 2026 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 394512 | Cargo Empire | 2025 | 40 | 0.09 | 0.189 | 0.5 | 7.43 | D1 | 167 | 9973 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 404204 | Battle Commander: Volume I | 2026 | 9 | 0.09 | 0.398 | 0.2 | 8.23 | D1 | 121 | 9334 | excluded_unreleased | — | year 2026 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 379055 | Thorgal: The Card Game | 2025 | 22 | 0.08 | 0.255 | 0.3 | 7.52 | D1 | 135 | 10415 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 377221 | Timelancers | 2025 | 8 | 0.08 | 0.422 | 0.2 | 7.16 | D1 | 112 | 11164 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 433283 | Daydream | 2025 | 1 | 0.08 | 1.194 | 0.1 | 5.09 | D1 | 523 | 4574 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| 429765 | SILOS | 2025 | 19 | 0.07 | 0.274 | 0.3 | 7.16 | D1 | 658 | 3959 | excluded_unreleased | — | year 2025 >=2025 — upcoming/unreleased edge case (already filtered pop |
| … | *truncated to 200 of 2505 flagged/excluded rows* |  |  |  |  |  |  |  |  |  |  |  |  |

Full 2505 flagged/excluded rows with all columns (including `n, resid, SE, z, lb_adj, decile, users, rank, related_game_id, reason`) are in `underrated_candidates.csv` filtered by `screening_disposition != robust_underrated` and `exclusions_and_deduplication.md` detailed above. See also `underrated_candidates.csv` for `not_underrated` (6800) and `broad_*` pools.

### Illustrative edge-case examples (per task wording)
- excluded `game_id 414927` — `n=14`, `SE 0.319`, `resid 1.82` but `z=5.7` weak evidence (small n dominates `post_SD 0.299`; `lb_adj 8.58`)
- flagged `game_id 140135 Small World Designer Edition` — more popular reimplementation `game_id 40692 Small World` exists with `n 75285` `users 75285` vs `n 246` `users 266` — flagged_shadowed_by_more_popular_related where multiple records represent substantially same underlying game
- flagged `game_id 300192 Twilight Struggle: Red Sea` — more popular reimplementation `game_id 12333 Twilight Struggle` exists with `n 52326` — keep more popular/complete record per hidden-gem objective
- excluded `game_id 435330` — `year 2025` unreleased/upcoming (`unreleased_or_2025plus`) even though `resid 3.94` n=1 — already filtered from population but flagged per task

---
*Preserve enough information for later manual review — keep table with all fields and `screening_disposition` plus `reason`; do not collapse every decision into binary pass/fail.*

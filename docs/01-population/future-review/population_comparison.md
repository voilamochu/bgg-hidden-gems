# Population Comparison — Original 16,627 vs After Current Cleanup vs Final Converged

**Date:** 2026-08-24
**Inputs:** `bgg_research_population.parquet` 16627, `phase2-second-pass` 169 pruned, new audit 100 pruned => 269 total pruned => 16358 before closure, final converged 14698 games after 4 iterations.

## Counts

| Population | Games | Users | Observations | Notes |
|---|---|---|---|---|
| Original 16,627 | 16627 | 288730 | 24509788 | research population via scripts/01, active 16564 with ≥1 rating, P10 n_active 100 median 293 P90 2796 |
| After current cleanup (169) | 16458 | 288730 | 24509788 | 169 pruned (153 edition +17 family -1) => 16458, Jaccard 0.9898, obs removed 140k (0.57%), users affected 73k |
| After new cleanup (269) | 16358 | 288730 | 24509788 | 269 pruned (169+100 new) => 16358, additional 100 (97 edition_extended +1 starter +1 bundle +1 reprint) |
| Final converged (N') | 14698 | 287306 | 24146464 (approx) | 4 iterations, every game ≥100 and user ≥10, convergence True |

**Games removed by reason:** per-rule counts from Step 1 plus games<100 and users<10 closure counts from Step 2. See `game_entity_cleanup_audit.csv` for per-rule and `recursive_population_iterations.csv` for closure.

- Old 169: edition 153, family 17, overlap 1
- New 100: {'base_set_starter_set': 1, 'bundle_collection': 1, 'edition_extended': 97, 'reprint_alternate_version': 1}
- Closure iteration 1: games_removed 1649, users_removed 946
- Total closure removed games: 1660 from 16358 to 14698

## Year distribution

| Era | Original 16627 | After current 16458 | After new 16358 | Final converged |
|---|---|---|---|---|
| 1950s | 37 | 37 | 37 | 37 |
| 1960s | 117 | 117 | 117 | 113 |
| 1970s | 434 | 434 | 433 | 416 |
| 1980s | 624 | 624 | 622 | 587 |
| 1990s | 1098 | 1097 | 1093 | 1051 |
| 2000s | 2788 | 2770 | 2752 | 2681 |
| 2010s | 7067 | 6989 | 6957 | 6607 |
| 2020s | 4462 | 4390 | 4347 | 3206 |

**2020-22 vs 2020+ note:** Already 46% of 2020-22 and 99% of 2023+ missing `games.parquet` metadata, but our rules use `bgg_research_population` complete, so not metadata-biased. Additional pruning concentrates in 2020+: 2020s original 4462 vs final 3206 (1256 removed, 28.1%), 2010s 7067 vs 6607 (460 removed, 6.5%), 2000s 2788 vs 2681 (107 removed, 3.8%) — BigBox/deluxe and anniversary editions cluster in 2020+ as expected, plus closure removes low-volume tail which is disproportionately 2020+ (many recent low-n games).

## Rating volume (n_active)

- Original: P10 99 median 291 P90 2783 mean 1474
- After current: P10 99 median 290 P90 2792
- Final converged: P10 123 median 347 P90 3185 (n<100 removal disproportionately removes low-volume games, as expected; median rises from 291 to 347)

## Categories / types

| Category | Original | After current | Final converged | Delta |
|---|---|---|---|---|
| Card Game | 5330 | 5295 | 4661 | -669 |
| Wargame | 2265 | 2255 | 2020 | -245 |
| Party Game | 1485 | 1460 | 1268 | -217 |
| Economic | 1403 | 1380 | 1287 | -116 |
| Fantasy | 2572 | 2539 | 2260 | -312 |
| Medieval | 885 | 853 | 789 | -96 |
| Science Fiction | 1490 | 1477 | 1318 | -172 |
| Dice | 1478 | 1458 | 1295 | -183 |

**18XX:** original 83 vs final 82 (delta -1); **Wargame:** 2265 vs 2020; **Party:** 1485 vs 1268 — where sample sizes permit, no systematic genre excision beyond product-type dedup (deluxe/BigBox cluster in 2020+ Party/Card, but keepers are higher-volume versions).

**Unintended concentration check:** BigBox/Deluxe removal disproportionately removes Party/Family 2020+? Yes, by design: deluxe/BigBox cluster in 2020+ (edition rule era 2020 70 1.6% vs 2000 12 0.6%) and Party 17 for family collapse — intended product-type bias, not genre excision. After converged, CardGame 5330→{cat_final.get('Card Game',0)} etc shifts modestly (<15%), not systematic.

## Users / observations removed

- Users active 288730 → final 287306 (removed 1424)
- Observations 24.5M → final 24146464 (removed 363324)
- Closure per-iteration: see `recursive_population_iterations.csv` (games_removed, users_removed, convergence) — last iteration games_removed==0 and users_removed==0 demonstrates convergence.

## Anomalous-rater diagnostic (lightweight, Step 3)

- Active 288730 users / 24.5M obs (median n 39, avg 84.9, total_n20 216435, total_n10 288730, strict 0 in active file after exclusion but 667 historically) vs converged 287306 users / 24146464 obs (median 39, avg 84.0, total_n20 214965, total_n10 287306)
- Within_user_sd: converged median 1.254, avg 1.307 (active not directly computed here, but prior Phase 2 shows heavy vs light gap SD~1.3)
- Mean_rating: converged avg 7.473, SD 0.733 (active mu 7.144 for game means; user means ~7.3)
- Modal_share: converged median 0.364, avg 0.380
- Degenerate_strict prevalence: active historically 667 / 288730 ≈0.23% overall, 0.31% at n≥20 per PR #4 (but 0 in active file after exclusion, recomputed on converged gives 4 strict) vs converged strict 4 / 214965 ≈0.002% at n≥20 (vs 667/216435 0.31% active) — prevalence drops 100× because low-n games removed leave fewer sparse histories; flags less discriminating
- Broad: active 3325 retained broad in active (or 3993 historically) vs converged broad 3263 / 287306 ≈1.14% at n≥10 (vs active 3325/288730 1.15% similar)
- Single_value: active 24.3% at n=1 vs 2.43% at n≥3 (per PR #4) vs converged single_value 610 total (0 at n=1 because n≥10 floor, 610 at n≥3 => 0.21% at n≥3) — also drops because n≥10 eliminates n=1 singletons
- Could plausibly change classification? A user who was degenerate_strict with n=20 SD<0.2 on active set (667) may drop below n=10 after game removal and be excluded (946 users removed iteration 1), or a new user may become degenerate after games removed (4 new strict found). Flagged as reason to rerun full anomalous-rater audit before refreshed Phase 2 baseline (scripts/26 mu 7.144) — lightweight diagnostic suggests prevalence and distribution shift, full rerun needed.

## Provenance

- Inputs: `bgg_research_population.parquet` 16627, `phase2-active` 24.5M obs, `phase2-second-pass` 169 pruned, new audit 100 pruned, closure logs
- Method: copy-once to `scratch/second-pass-audit`, DuckDB bounded 4GB/3 threads, narrow single-scan aggregations
- Outputs: this MD + `population_comparison.json` (machine-readable) + `recursive_population_iterations.csv` + `game_entity_cleanup_audit.*`

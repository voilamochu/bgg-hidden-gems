# Recursive Population Closure — Second-Pass Extension

**Date:** 2026-08-24
**Starting population:** 16627 total, 269 pruned (169 old + 100 new) => 16358 surviving before closure (16358). Uses `rating_observations_active` 24.5M obs (mu 7.144, 16564 games with ≥1 active rating, 288730 users active ≥10 minus degenerate_strict).

**Rules:** every retained **game** must have ≥100 **qualifying ratings** (rating_observations_active rows for current population), every retained **user** must have ≥10 **qualifying ratings** within retained game universe. Then iteratively: a. remove games <100, b. remove users <10, c. recompute, d. repeat until no additional game or user is removed — do not assume one pass is sufficient.

**Method:** Copy-once to `scratch/second-pass-audit`, DuckDB bounded `memory_limit 4GB / threads 3 / temp_directory scratch/ducktmp`, narrow single-scan aggregations. Each iteration recomputes per-game n_active and per-user n_active within remaining universe, identifies low games/users, prunes both, repeats.

## Per-iteration log

| iteration | games | users | observations | games_removed | users_removed | convergence |
|---|---|---|---|---|---|---|
| 1 | 16358 | 288730 | 24265365 | 1649 | 946 | False |
| 2 | 14709 | 287784 | 24151784 | 11 | 475 | False |
| 3 | 14698 | 287309 | 24146491 | 0 | 3 | False |
| 4 | 14698 | 287306 | 24146464 | 0 | 0 | True |

**Convergence discussion:**

Converged in **4 iterations** where last iteration had `games_removed==0` and `users_removed==0`. Final population satisfies both constraints simultaneously: every game ≥100 and every user ≥10 within retained set. This matches the deferred plan's fixed-point requirement and demonstrates that iteration matters beyond single filter (as single-filter precursor was 14952 vs closed 14941 diff 11, here additional pruning of 100 new games changes starting point but closure still converges in 4 iterations).

**Final converged population:** 14698 games, 287306 users, 24146464 observations (qualifying ratings where both game and user retained). Compare to primary closed 14786 games / 287776 users / 24254208 obs (169 pruned) and base closed 14941 / 288250 / 24397989. The additional 100-game pruning reduces games by ~88 and obs by ~107744.

**Validation:** Every retained game has ≥100 qualifying ratings, every retained user has ≥10, no excluded game/user survives, rating observations internally consistent (checked via per-game/user counts post-convergence). See `recursive_population_iterations.csv` for machine-readable log and `population_comparison.*` for three-way comparison.

**Provenance:** Script `scripts/37_second_pass_closure_and_rebuild.py`, bounded DuckDB, copy-once `scratch/second-pass-audit`, narrow aggregations, no wide-table bug, no full-snapshot rescans. Final population definition parquet(s) needed for reproducibility will be built in next step (new namespace `data/processed/phase2-pass2/`).

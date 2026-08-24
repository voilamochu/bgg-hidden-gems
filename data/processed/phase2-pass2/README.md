# Phase 2 Pass 2 — Converged Second-Pass Population (`phase2-pass2`)

**Generated:** 2026-08-24T15:05:30Z
**Source inputs:** `bgg_research_population.parquet` 16627, `rating_observations_active.parquet` 24.5M, `pruned 269` (169 old +100 new), closure to 14698 games / 287306 users / 14698 obs
**Filtering logic:** Start from 16627, remove 269 game-entity duplicates (edition/second-edition/anniversary/premium/heritage etc with designer/year/weight/families/game_links corroboration, keep more popular per group), then recursive `games ≥100` + `users ≥10` mutual closure to fixed point (4 iterations, convergence when games_removed==0 and users_removed==0). Final population satisfies both constraints simultaneously.
**Convergence result:** 4 iterations to fixed point (see `../docs/future-methodology-review/recursive_population_iterations.csv` for per-iteration log):

| iter | games | users | obs | games_removed | users_removed | convergence |
|---|---|---|---|---|---|---|
| 1 | 16358 | 288730 | 24265365 | 1649 | 946 | False |
| 2 | 14709 | 287784 | 24151784 | 11 | 475 | False |
| 3 | 14698 | 287309 | 24146491 | 0 | 3 | False |
| 4 | 14698 | 287306 | 24146464 | 0 | 0 | True |

Final 14698 games / 287306 users / 24146464 obs. See `population_comparison.*` for three-way comparison.
**Reproduction command:** `python scripts/37_second_pass_closure_and_rebuild.py` (bounded 4GB/3 threads, `scratch/second-pass-audit`)
**Validation:** every retained `game_id` belongs to final game population (0 violations), every retained `user_id` belongs to final user population (0 violations), every retained user has ≥10 qualifying ratings (0 violations), every retained game has ≥100 qualifying ratings (0 violations), no excluded game/user survives (0 excluded games in rating), rating observations internally consistent: True.
**Catalog:** `parquet_catalog.csv` with row counts full/source → cleaned → final (full 26.9M, filtered 25.3M, active 24.5M, pass2 24146464).
**Namespace:** `data/processed/phase2-pass2/` distinct from `phase2` (26.9M full), `phase2-filtered` (25.3M), `phase2-active` (24.5M), `phase2-second-pass` (14786/16458). Keep new extracts gitignored via `data/processed/` (catalog/validation/README committed, parquets gitignored). Population definition parquet `games_pass2.parquet` is committed for reproducibility (small); large extracts are gitignored but reproducible via script.
**Downstream deferred:** No Phase 2/3/4 statistical refresh yet (no new adj/expected fit) until population stable and convergence demonstrated — this rebuild is final deliverable of this task, downstream reruns remain deferred.

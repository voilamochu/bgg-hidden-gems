# Second-Pass Methodology Review (Deferred → EXECUTED 2026-08-24, Extended 2026-08-24)

**Status:** `EXECUTED` — recursively closed to fixed point (see `docs/future-methodology-review/README.md:1` and `data/processed/phase2-second-pass/` for logs; 4 iterations, base 14941 vs primary 14786, vs single-filter 14952 diff 11, estimation stable per `model_comparison.json`). Requires explicit comparison before adoption — now done.

**Update 2026-08-24 Extension:** After initial 169 pruned (153 edition +17 family), additional **100** game-entity duplicates audited with corroboration (97 second-edition/anniversary/premium/heritage/decennial etc, 1 starter-set component, 1 bundle, 1 reprint) => **269 total pruned** => 16358 before closure => **14698 converged** in 4 iterations (1649+11 games, 946+475+3 users, 24.65M→24.15M obs). New namespace `data/processed/phase2-pass2/` built with validation 0 violations, every game ≥100 and user ≥10. Downstream Phase 2/3/4 refresh remains deferred. See `docs/future-methodology-review/game_entity_cleanup_audit.md`, `recursive_population_iterations.csv`, `population_comparison.*`, `phase2-pass2/README.md`.

**Status (original):** `DEFERRED` — **not part of the current primary pipeline**. To be reconsidered only after the current full Phase 1–7 pass is complete. Requires explicit comparison of the current and recursively cleaned populations before adoption. Do not implement now.

**Date proposed:** 2026-08-24
**Source:** Captain deferred item, recorded per instruction.

## Proposed second-pass population rule to revisit

Recursive mutual filtering, starting from the research game population:

1. Start with the research game population (16,627 games, as defined in `data/processed/bgg_research_population.parquet` via `scripts/01_clean_population.py`).
2. Remove games with fewer than 100 qualifying ratings.
3. Remove users with fewer than 10 qualifying ratings.
4. Recompute qualifying ratings after each filter (counts are within the *remaining* population, not the original).
5. Repeat recursively until no game has <100 qualifying ratings and no user has <10 qualifying ratings — a fixed-point closure where game and user eligibility are mutually consistent.

6. **Also explicitly revisit and potentially rerun the anomalous-rater identification** after the final recursive population is established, because user/game membership changes may alter the rater-distribution diagnostics and therefore the `degenerate_*` set (currently defined on the `16,627 × ≥10` active population, 288,730 users, `scripts/25`, `degenerate_strict` 667 users).

## Rationale

The current Phase 1 game floor (`≥100` ratings) is based on the **original BGG rating count** (`users_rated` at scrape time, `bgg_research_population` population). Later user filtering (`≥10` in-universe ratings, `degenerate_strict` exclusion) can reduce a game's **active rating count** (`n_active` in `data/processed/phase2-active/`, where `P10=100`, `P25=144`, `median 293`, `mean 1,480`) **below 100**, leaving games in the active 16,564 set with `1–99` active ratings. A recursive closure rule would make the **game and user eligibility criteria mutually consistent** — every retained game has ≥100 *active* ratings and every retained user has ≥10 *active* ratings *within the retained set*.

## What a second-pass comparison must show before adoption

- **Population shift:** current `16,627 → 16,564` active games (`1-99` bucket is 1,612 games, 9.7% of active; `P10=100` is the threshold) and `288,730` active users vs recursively closed counts; `n_active` distribution shift; `users_rated` vs `n_active` divergence.
- **Impact on Phase 5 quality estimator** (`adj_mean`, `lambda 1.91`, `SE`, shrunk variant) and **Phase 6 preferred `Q3b/OLS`** (`R² .582`, `beta` stability, residual distribution, `corr(resid, log n)`, top-1%/5% overlap). The sensitivity study `bgg-sensitivity-n100` (active vs `n_active ≥100` for games) is the *non-recursive* precursor to this — compare its results to the recursive closure to see if iteration matters beyond the single `≥100` game filter.
- **Anomalous-rater set change:** `degenerate_strict`/`broad` prevalence before vs after closure (currently `0.31%` at `n≥20` strict, `1.15%` broad in active; `667` strict users) and whether the `SD<0.2` / `modal≥95%` flags become more/less discriminating when low-`n` games are removed.
- **Candidate-screening consequences:** broad pool / robust subset sizes, exclusion counts, `n` distribution of top residuals, and whether the `1–99` games are merely a noisy tail or materially change fitted `expected_quality_g` (Phase 6 residual stability `r .962` in lowest `n`-quartile already suggests measurement noise, not model change — test explicitly).

## Deferred decision criteria

Adopt the recursive population only if the comparison shows the current `1–99` inclusion **materially affects** the fitted expected-quality model or downstream conclusions (e.g. `beta` shift `>10%`, `R²` change `>0.02`, residual rank `Jaccard` `<0.70` for top-1%, or top residuals dominated by `n<100` high-`SE` games). If the effect is confined to **candidate screening noise** (e.g. low-`n` games have large `SE` but don't shift the model), the appropriate fix is an `n≥100` **screening floor** for candidates, not a population redefinition. The current `n≥100` sensitivity study will inform which case holds.

**Do not confuse this with the `n_active ≥100` *sensitivity* study** (`bgg-sensitivity-n100`): that study is a single-filter comparison (`n_active ≥100` for games, users fixed at `≥10`) to test whether `1–99` games matter; this deferred item is the **recursive closure** (`games <100` *and* `users <10` iterated to fixed point).

## Provenance

- Current primary pipeline: `16,627` games × `≥10` active users minus `degenerate_strict` → `24,509,788` obs (`data/processed/phase2-active/`, `scripts/24`, validation `0` violations) → refreshed severity `scripts/26` → taste/informativeness/selection `scripts/27-29` → quality estimator `scripts/30` (`lambda 1.91`) → underratedness `scripts/31` (`Q3b/OLS`).
- This deferred item is **not** the `1–99` sensitivity study; it is the *recursive mutual filter* to be evaluated after that sensitivity and after the full Phase 1–7 pass.
- Recorded here per captain instruction 2026-08-24; not implemented.

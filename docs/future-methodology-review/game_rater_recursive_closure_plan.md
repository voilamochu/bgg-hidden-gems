# Game/Rater Recursive Closure Plan — Second-Pass Population (Deferred → EXECUTED 2026-08-24)

**Status:** `EXECUTED` — recursively closed to fixed point (see `README.md:1` and `data/processed/phase2-second-pass/*_closure_log.csv`). Primary closed 14786 games (4 iterations, 1662+10 pruned, 3 deg, 287,776 users, 24.25M obs); base closed 14941 (1675+11 pruned, 3 deg). Single-filter precursor was 14952 vs closed 14941 diff 11, so iteration adds little beyond single-filter (as sensitivity found). Logs in `data/processed/phase2-second-pass/`.

**Status (original):** `DEFERRED` — not part of the current primary pipeline (`16,627` games × `≥10` per user minus `degenerate_strict` → `24.5M obs`, `scripts/24` + `26`). To be reconsidered only after the current full Phase 1–7 first pass is complete, **jointly** with the game-level pruning in `candidate_pruning_rules_to_investigate.md:1` and `population_second_pass_plan.md:1`. Do not implement now.

**Date proposed:** 2026-08-24
**Source:** Captain instruction, now subsumed into the comprehensive `population_second_pass_plan.md:1`. This file is the detailed closure specification that was previously at `docs/second-pass-methodology-review.md:1`.

## Rule to revisit

Recursive mutual filtering, starting from the candidate game universe (after the game-level pruning in `candidate_pruning_rules_to_investigate.md`, or from the `16,627` base for comparison):

1. Start with the candidate game universe (e.g. `16,627` games, or the pruned `N'` after edition/family dedup).
2. Require games to have `≥100` **qualifying ratings** (active ratings: `rating_observations_active` rows for `16,627 × ≥10` minus `degenerate_strict`; `n_active` per game, `P10=100`, `P90=2,795`, `mean 1,480`, `harmonic mean 106.5` from `scripts/30`).
3. Require users to have `≥10` **qualifying ratings** within that universe (same `n_active` per user, `t=10` primary from `scripts/23`, `289,397` users at `t=10` before strict exclusion → `288,730` after; `t=20` sensitivity `217,102`).
4. Recompute qualifying ratings after each filter (counts are within the *remaining* population, not the original — a game that drops below 100 after users are removed drops, and a user who drops below 10 after games are removed drops).
5. Repeat recursively until **no game has `<100` and no user has `<10`** — a fixed-point closure where game and user eligibility are mutually consistent.
6. Rerun the **anomalous-rater identification** (`scripts/25` `degenerate_*` logic: `n≥20` AND `single_value` OR `SD<0.2` OR `modal≥95%` on ROUND-binned `1..10` for `degenerate_strict`; `n≥10` `k≤2` OR `SD<0.5` OR `modal≥90%` for `broad`) after the final converged population, because user/game membership changes alter the rater-distribution diagnostics and therefore the `degenerate_*` set (currently `667` strict / `3,993` broad on the `16,627 × ≥10` active population, `reports/anomalous_rater_audit/*`).

## Why this was deferred, not rejected

The current Phase 1 game floor (`≥100` ratings) is on the **original BGG rating count** (`users_rated` at scrape time, `bgg_research_population` population). Later user filtering (`≥10` in-universe ratings, `degenerate_strict` exclusion) can reduce a game's **active rating count** (`n_active` in `data/processed/phase2-active/`, where `P10=100` is the threshold) **below 100**, leaving games in the active `16,564` set with `1–99` active ratings (`1,612` games, **9.73%** of active, `P10=100` is the cut). A recursive closure would make the **game and user criteria mutually consistent** — every retained game has `≥100` *active* ratings and every retained user has `≥10` *active* ratings *within the retained set*.

The `1–99` sensitivity study (`bgg-sensitivity-n100`, `docs/phase6-intermediate/sensitivity_n100.md:1`, `reports/sensitivity_n100_games/*`) already showed the *single-filter* (`n_active ≥100` for games, users fixed) effect on the preferred `Q3b/OLS` (`beta +3.0%`, `R² +0.014`, residual `r 0.9995`, but top-20 `55%` `n<100` and cross `Jaccard 0.57`). The **recursive closure** will show whether *iterating* (games `<100` ↔ users `<10`) matters beyond that single filter. Do not confuse the two: the sensitivity study is a *single* game filter; this plan is the *iterated fixed-point*.

## What a second-pass comparison must show before adoption

- **Population shift:** current `16,627` → `16,564` active games (`1–99` bucket is `1,612` games) and `288,730` active users vs recursively closed `N'_games` / `N'_users` / `N'_obs`; `n_active` distribution shift; `users_rated` vs `n_active` divergence.
- **Impact on Phase 5 quality estimator** (`adj_mean`, `lambda 1.91`, `SE`, shrunk variant) and **Phase 6 preferred `Q3b/OLS`** (`R² .582`, `beta` stability, residual distribution, `corr(resid, log n)`, top-1%/5% overlap). The sensitivity study's `beta +3.0%` / `R² +0.014` is the *single-filter* baseline; the recursive closure will show whether iteration changes those beyond the single filter.
- **Anomalous-rater set change:** `degenerate_strict`/`broad` prevalence before vs after closure (currently `0.31%` at `n≥20` strict, `1.15%` broad in active; `667` strict users) and whether the `SD<0.2` / `modal≥95%` flags become more/less discriminating when low-`n` games are removed.
- **Candidate-screening consequences:** broad pool / robust subset sizes, exclusion counts, `n` distribution of top residuals, and whether the `1–99` games are merely a noisy tail or materially change fitted `expected_quality_g` (Phase 6 residual stability `r .962` in lowest `n`-quartile already suggests measurement noise, not model change — test explicitly with the closed population).

## Relation to the game-level pruning

The game-level pruning (`candidate_pruning_rules_to_investigate.md`) and the recursive closure **must be evaluated together** and reported as a **joint** effect vs the current `16,627 × ≥10` active population. Part A's pruning changes which games have `<100` ratings, which changes which users have `<10` ratings, which changes the closure, which changes the anomalous set. Evaluate them in one matrix:

- Current `16,627 × ≥10` active (`24.5M` obs) — primary first pass.
- Single-filter `n_active ≥100` for games only (sensitivity study, `14,952` games) — already done.
- Recursive closure `N'_games × N'_users` (iterated `≥100` / `≥10` to fixed point) — this plan.
- Recursive closure *plus* game-level pruning (family/edition dedup) — combined second-pass `N''`.

Report the **joint** counts and the **marginal** contribution of each part.

## Deferred decision criteria

Adopt the recursively closed population only if the **joint** comparison (current `16,627` vs closed `N'`) shows a material difference that warrants redefinition (e.g. `beta` shift `>10%` in Phase 6 `Q3b/OLS`, `R²` change `>0.02`, residual rank `Jaccard` `<0.70` for top-1%, or top residuals dominated by `n<100` high-`SE` games). If the effect is confined to **candidate-screening noise** (low-`n` games have large `SE` but don't shift the model — as the sensitivity study found with `Jaccard 0.973` overlap and `r 0.9995`), the appropriate fix is an `n≥100` **screening floor** for candidates, not a population redefinition. The sensitivity study is the *single-filter* precursor; the recursive closure will show whether iteration matters beyond that.

## Provenance

- Current primary pipeline: `16,627` games × `≥10` active users minus `degenerate_strict` → `24,509,788` obs (`data/processed/phase2-active/` `scripts/24`, `active_baseline_refresh.json` `scripts/26`).
- This deferred plan is the **iterated fixed-point** version of the `1–99` sensitivity study; it is **not** that study, but its recursive extension.
- Recorded here per captain instruction 2026-08-24; not implemented.


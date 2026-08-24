# Second-Pass Population Methodology Review — Plan (Deferred)

**Status:** `DEFERRED` — **not part of the current primary pipeline**. To be reconsidered only after the current full Phase 1–7 first pass is complete. The current **16,627-game research population** (`data/processed/bgg_research_population.parquet`, `scripts/01_clean_population.py`) remains the **primary first-pass research record**. Requires explicit comparison of the current and second-pass populations before adoption. **Do not label the current population "wrong"** — treat this as a methodological refinement **enabled by newly available data** (the 9 GB BGG SQLite snapshot and its richer `game_links`/`families`/title/metadata relationships).

**Date proposed:** 2026-08-24
**Source:** Captain instruction, Phase 7 candidate-screening context.
**Related deferred item:** `docs/second-pass-methodology-review.md:1` (recursive `games<100` + `users<10` closure) is now **subsumed** by this broader second-pass review — that single-filter closure becomes §3 of this plan. Do not implement either in isolation.

## Why a second pass is now possible

The original 16,627-game population was constructed **before the full BGG SQLite snapshot** (`data/raw/bgg.sqlite`, `data/processed/phase2/*.parquet` via `scripts/13`) was available, so its game-level pruning was necessarily limited to fields present at that time (rating count floor, year, language, reimplementation flag as then defined). We now have substantially richer information for identifying records that **should not represent independent games** for the hidden-gem objective:

- `game_links` (`game_id`, `rel`, `other_id`, `other_name`) — `rel` values include `reimplementation`, `version`, `expansion`, `family`, etc., with 43,196 rows in `data/processed/phase2/game_links.parquet` and 33,483 in `data/processed/phase2-filtered/`.
- `families` / title/metadata relationships (family membership, `title_clean` duplicates, language/version suffixes).
- Reimplementation / version / edition fields, `is_reimplementation`, `num_implementations`, `title` patterns (`Deluxe`, `Anniversary`, `Big Box`, `Special Edition`, language tags).
- Other newly available BGG data (publisher, `families`, `game_tags` where present).

The current Phase 7 screen already surfaces the symptom: **multiple records from families such as Monikers and Time's Up! can appear as separate high-residual candidates** (e.g. `Monikers 255249`, `Monikers: More Monikers 179448`, `Time's Up! Title Recall! 36553` all in `reports/games_metadata_coverage` and `phase7` top lists), and **Small World Designer Edition 140135** can appear as a strong candidate (`resid 2.20`, `n=246`, rank unranked) despite representing a **more-specialized edition of a much more established underlying game** (base `Small World 40692`, `75,285` users, rank 410, `resid -0.17`). These are not errors in the current pipeline, but they show that the *population* contains multiple records for essentially the same underlying product/design that should not count as independent discoveries.

## Scope of the second-pass review

The second-pass population review has **two linked parts** that must be treated as **one population-definition exercise** (not two independent filters):

### Part A — Game-level population pruning (new in this review)

Investigate and potentially exclude from the analytical population game records that should not count as independent games for *this* research objective. See `candidate_pruning_rules_to_investigate.md:1` for the five rule families and the explicit, auditable rule requirement.

### Part B — Recursive game/rater closure (previously deferred, now part of same exercise)

Revisit the previously proposed recursive mutual filtering (see `game_rater_recursive_closure_plan.md:1` and `docs/second-pass-methodology-review.md:1`):

1. Start with the candidate game universe (after Part A pruning, or from the 16,627 base for comparison).
2. Require games to have `≥100` qualifying ratings.
3. Require users to have `≥10` qualifying ratings within that universe.
4. Recompute qualifying ratings after each filter.
5. Repeat recursively until no game has `<100` and no user has `<10`.
6. Rerun the anomalous-rater identification (`scripts/25` `degenerate_*` logic) after the final converged population, because user/game membership changes alter the rater-distribution diagnostics.

**The game-edition/deduplication review (Part A) and the recursive closure (Part B) are one exercise** — Part A's pruning changes which games have `<100` ratings, which changes which users have `<10` ratings, which changes the closure, which changes the anomalous set. Evaluate them together and report their **joint** effect vs the current `16,627 × ≥10` active population (`24.5M obs`, `288,730` users, `16,564` games with `≥1` active rating, `scripts/24`).

## What must be quantified for each proposed pruning rule

For **each** rule in `candidate_pruning_rules_to_investigate.md`, report:

- **Games removed** (count and `game_id` list — committed `missing_ids`-style CSV for reproducibility).
- **Rating observations removed** (active `rating_observations_active` rows for those games).
- **Users affected** (users who lose all ratings vs lose `≥1` rating, change in `n_active` distribution).
- **Categories / eras / volume distributions affected** (e.g. does removing `Big Box` editions disproportionately remove recent years or `party`/`family` games?).
- **Examples of included vs excluded records** (e.g. `Monikers 255249` kept vs `Monikers: More Monikers 179448` excluded under a family rule, with titles/years/ratings).
- **Overlap with the current 16,627-game population** (`Jaccard`, retained `n`, retained `users_rated`).
- **Whether the rule risks systematically removing particular game types or eras** (e.g. deluxe editions cluster in 2020+ — see `games_metadata_coverage` audit: `46%` of 2020–22 and `99%` of 2023+ already missing `games.parquet` metadata, so any metadata-dependent rule must be checked for era bias).

## How to handle the Monikers / Time's Up! / Small World examples

- **Monikers / Time's Up! families:** multiple records (`Monikers`, `More Monikers`, `Shmonikers`, `Time's Up! Title Recall!`, etc.) appear as separate high-residual candidates in the current Phase 7 `underrated_candidates.csv` (16,549 rows, robust `910`). The review must test whether a **family-level dedup rule** (e.g. keep the most popular/complete record per `family` or per `title_clean` root) would collapse these to one candidate without collapsing materially distinct designs elsewhere.
- **Small World Designer Edition 140135** (`n=246`, `resid 2.20`) vs **base Small World 40692** (`n=75,285`, `resid -0.17`): the Designer Edition is a **more-specialized edition of a much more established underlying game**. The review must test whether an **edition / special / deluxe rule** would flag the Designer Edition as shadowed by its more popular base (as `exclusions_and_deduplication.md` already does for `4× users` shadowing in Phase 7, but now at the *population* level, not just candidate screening).

**Important:** do **NOT** simply remove every reimplementation or every edition. Some reimplementations are materially distinct designs (e.g. `Pandemic` vs `Pandemic Legacy`) and should remain separate. The review must establish **explicit, auditable rules for what constitutes the same underlying game *for this research objective*** (hidden-gem discovery — independent game discovery, not product SKU counting).

## Deferred decision criteria

Adopt the second-pass population only if the **joint** comparison (current `16,627` vs second-pass `N'`) shows a material difference that warrants redefinition (e.g. `beta` shift `>10%` in Phase 6 `Q3b/OLS`, `R²` change `>0.02`, residual rank `Jaccard` `<0.70` for top-1%, top residuals dominated by `n<100` high-`SE` games, or candidate-screening `Jaccard` `<0.70`). If the effect is confined to **candidate-screening noise** (low-`n` games have large `SE` but don't shift the model), the fix is an `n≥100` **screening floor** for candidates (already recommended in the `1–99` sensitivity study, case 3), not a population redefinition. The current `n≥100` sensitivity study (`bgg-sensitivity-n100`, `16,564` vs `14,952` games, `beta +3.0%`, `R² +0.014`, overlap `r 0.9995`) is the *single-filter* precursor; the recursive closure will show whether iteration matters beyond that.

**Do not implement or rerun now.** Record this plan, then return to the first-pass pipeline. The final second-pass population must be compared directly against the current `16,627` before adoption.

## Provenance and inputs for the future review

- Current primary pipeline: `16,627` games × `≥10` active users minus `degenerate_strict` → `24,509,788` obs (`data/processed/phase2-active/` `scripts/24`, `active_baseline_refresh.json` `scripts/26`).
- Richer BGG snapshot: `data/processed/phase2/game_links.parquet` (`43,196` rows), `families` (via `bgg_research_population.families` where present), `title`/`title_clean`, `is_reimplementation`, `reimplementation/version` `game_links` `rel`, language/version tags, `bgg_research_population` complete for `16,627`.
- This deferred plan is **not** the `1–99` sensitivity study (`docs/phase6-intermediate/sensitivity_n100.md:1`); that study is a *single-filter* `n_active≥100` for games only, this review is the *iterated fixed-point* plus edition/family dedup.

## Outputs when eventually implemented

- Updated population parquet(s) and `phase2-active` extracts for the second-pass `N'` universe.
- Rerun of `degenerate_*` identification on that universe.
- Comparison table: current `16,627` vs second-pass `N'` (games, obs, users, categories/eras/volume, `degenerate` prevalence, `R²`/`beta`, residual ranks, top residuals).
- Explicit rule file with included/excluded examples and `Jaccard` overlap.

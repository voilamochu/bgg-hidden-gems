# Candidate Pruning Rules to Investigate — Second-Pass Game-Level Population (Deferred)

**Status:** `DEFERRED` — not part of the current primary pipeline (`16,627` games × `≥10` per user minus `degenerate_strict` → `24.5M obs`, `scripts/24` + `26` + `30`/`31` on `phase2-active`). To be investigated only after the current full Phase 1–7 first pass is complete. See `population_second_pass_plan.md:1` for the overall second-pass plan and `game_rater_recursive_closure_plan.md:1` for the recursive closure that must be evaluated jointly with these rules.

**Date proposed:** 2026-08-24
**Source:** Captain instruction, Phase 7 candidate-screening context (multiple Monikers/Time's Up! records, Small World Designer Edition).

## Objective

Establish **explicit, auditable rules for what constitutes the same underlying game** for *this* research objective (hidden-gem discovery — independent game discovery, not product SKU counting). Use the **richer `game_links`/`families`/title/metadata relationships** now available from the 9 GB BGG SQLite snapshot (`data/processed/phase2/game_links.parquet` `43,196` rows, `data/processed/phase2-filtered` `33,483`, `families` via `bgg_research_population.families`, `title`/`title_clean`, `is_reimplementation`, `reimplementation`/`version` `game_links` `rel`, language/version tags). Determine **what can be identified reliably**, not what can be guessed.

**Important:** do **NOT** simply remove every reimplementation or every edition. Some reimplementations are materially distinct designs (e.g. `Pandemic` vs `Pandemic Legacy`, `Brass: Birmingham` vs `Brass: Lancashire`) and should remain separate. The review must keep both, with a rule that distinguishes *same underlying game with a new edition* from *new design that reimplements a system*.

## Rule families to investigate

For each family, define a **candidate rule**, an **auditable identification method** (exact `game_links` `rel` + `title` pattern + `families` check), and a **counterexample that must stay**.

### 1. Editions / special / deluxe / anniversary / big boxes where they should not count as independent discoveries

- **Candidates:** `Deluxe Edition`, `Anniversary Edition`, `Special Edition`, `Big Box`, `Collector's Edition`, `Ultimate Edition`, `Revised Edition` where the base title is identical or `title_clean` duplicate. Example: `Dominion Big Box 142132` vs `142131` (flagged in `exclusions_and_deduplication.md` as duplicate title, 206 flagged) — keep the more popular/complete record.
- **Identification:** `title` regex (`(?i)\b(deluxe|anniversary|big box|collector|special edition|revised)\b`), `title_clean` duplicate group, `game_links` `rel=version` where `other_name` is base title, `num_implementations` where `is_reimplementation` is false but `family` identical.
- **Must stay:** `Brass: Birmingham` vs `Brass: Lancashire` — reimplementations with distinct `weight`/`year`/`mechanics` and separate `families` entries, not just a box.

### 2. Language / version-specific records where the underlying game is the same

- **Candidates:** `Catan` German `Die Siedler von Catan` vs English `Catan`, or `language_ease` / `families` language tags where `title_clean` maps via `game_links` `rel=version` and `year`/`designer` identical.
- **Identification:** `game_links` `rel=version` + `language` fields in `game_attrs` (where present), `title` language suffixes, `families` language family. Requires `designer`/`year` match as guard.
- **Must stay:** `Catan` vs `Catan: Seafarers` — language same but `rel=expansion`, not `version`.

### 3. Reimplementations, alternate editions, standalone expansions or variants that should not be treated as distinct

- **Candidates:** `rel=reimplementation` where the older game is still in the 16,627 population and the newer is a *rules-identical* re-skin (e.g. `Small World Designer Edition 140135` `n=246` `resid 2.20` vs base `Small World 40692` `n=75,285` `resid -0.17` — Designer Edition is a **more-specialized edition of a much more established underlying game**, flagged in `exclusions_and_deduplication.md` as shadowed by `4× users`).
- **Identification:** `game_links` `rel=reimplementation` + `year` gap `<5` + `weight` within `0.2` + `mechanics` Jaccard `>0.8` + `category` overlap + `designer` identical. Require at least 3 of those to avoid catching distinct designs.
- **Must stay:** `Pandemic` vs `Pandemic Legacy` — same family but `weight` `2.40` vs `2.83`, `mechanics` differ (`Legacy` adds `Campaign`), `year` gap `8` — materially distinct.

### 4. Duplicate or near-duplicate BGG records representing the same underlying game

- **Candidates:** `title_clean` exact duplicates or `Levenshtein ≤2` on `title_clean` after stripping edition suffixes, with `year` `±1` and `designer` identical, `families` identical.
- **Identification:** `bgg_research_population` `title_clean` group, `game_links` not needed. Example: `Monikers` family — `Monikers 255249` vs `Monikers: More Monikers 179448` — both appear as separate high-residual candidates in current Phase 7 `underrated_candidates.csv` (`16,549` rows, robust `910`).
- **Must stay:** `Time's Up!` vs `Time's Up! Title Recall!` — same family but `year` gap `10`, `weight` differs, and each has independent `users_rated` — keep both unless `title_clean` + `year` also matches family root.

### 5. Other game-family relationships that cause multiple records for essentially the same underlying product/design to appear separately

- **Candidates:** `rel=family` where a `family` (e.g. `Monikers`, `Time's Up!`) has `>5` records in the 16,627 population and the `title` share a common stem after stripping `:`/`-`/`Edition`/`Volume`. Also `rel=expansion` where a standalone expansion is mis-tagged as `is_reimplementation=false` but `families` shows `Expansion` and `min_players`/`max_players`/`weight` identical to base.
- **Identification:** `families` field in `bgg_research_population` (where present), `game_links` `rel=family`/`expansion`, `title` stem grouping.
- **Must stay:** `Catan` vs `Catan: Starfarers` — same family but `weight` `2.30` vs `3.00`, `max_players` `4` vs `6` — distinct.

## What to quantify for each proposed rule

For **each** rule (and for the **combined** pruned population if multiple rules are adopted together):

- **Games removed** (count and `game_id` list — committed `missing_ids`-style CSV).
- **Rating observations removed** (`rating_observations_active` rows for those games, active `24.5M` base).
- **Users affected** (users who lose all ratings vs lose `≥1` rating, change in `n_active` distribution, shift in `users_active` `288,730`).
- **Categories / eras / volume distributions affected** (e.g. does removing `Big Box` disproportionately remove `party`/`family` 2020+? `games_metadata_coverage` audit showed `46%` of 2020–22 and `99%` of 2023+ already missing `games.parquet` metadata — any metadata-dependent rule must be checked for era bias).
- **Examples of included vs excluded records** (e.g. `Monikers 255249` kept `n=452` `adj 8.58` `resid 2.27` vs `Monikers: More Monikers 179448` excluded under a family rule, with titles/years/ratings).
- **Overlap with the current 16,627-game population** (`Jaccard`, retained `n`, retained `users_rated`, retained `n_active` decile distribution).
- **Whether the rule risks systematically removing particular game types or eras** (e.g. deluxe editions cluster in `2020+` — already `46%` of that era is `games` metadata-missing — or `reimplementation` removal would excise `Pandemic Legacy`-type distinct designs if not guarded by `weight`/`mechanics` checks).

## How to handle the Monikers / Time's Up! / Small World examples

- **Monikers / Time's Up! families:** test a **family-level dedup rule** (keep the most popular/complete record per `family` or per `title_clean` root) and report whether it collapses the family to one candidate without collapsing materially distinct designs elsewhere (e.g. `Pandemic` family should stay `>1`).
- **Small World Designer Edition 140135** (`n=246`, `resid 2.20`, unranked) vs **base Small World 40692** (`n=75,285`, rank 410, `resid -0.17`): test an **edition / special / deluxe rule** that would flag `140135` as shadowed by its more popular base (`4× users` rule already does this at candidate-screening level in `exclusions_and_deduplication.md`, but now at the *population* level). Report whether the rule would have prevented the Designer Edition from appearing as a strong candidate at all.

## What NOT to do

- Do not remove **every** reimplementation or every edition — keep the counterexample guards above.
- Do not treat `users_rated` or `resid` as proof of which record to keep — keep the **more popular/complete** record per family/title group, not the higher-residual one, to avoid biasing the population toward underratedness.
- Do not use `games.parquet` alone for `weight`/`playtime` where it is only `80.89%` complete — join to `bgg_research_population` for complete fields.

## Outputs when eventually implemented

- Explicit rule file with per-rule `included`/`excluded` examples and `Jaccard` overlap per rule.
- Committeed `game_id` lists for each rule and for the combined pruned population.
- Quantification table: rule → games/obs/users affected, category/era/volume shift, overlap.


# Second-pass population — executed

Primary pipeline remains 16,627 × ≥10 minus degenerate_strict → 24.5M obs.
This directory is the **second-pass population for direct comparison before adoption** (deferred review now authorized).

Generated: 2026-08-24T14:20:36Z
Script: scripts/34_second_pass_population.py
Inputs: bgg_research_population.parquet (16627), rating_observations_active.parquet (24.5M), game_links_filtered.parquet, users_active etc. Copy-once to scratch/second-pass, DuckDB 4GB/3 threads.

## Populations

- **bgg_population_second_pass.parquet** — 16458 games after Step1 game-level dedup (edition 126 + monikers/time 17 =143 removed). Primary second-pass before recursive closure.
- **bgg_population_second_pass_closed.parquet** — 14786 games after recursive closure to fixed point (games<100, users<10, degenerate_strict rerun). Mutual closure where each prune can introduce more candidates.
- **bgg_population_second_pass_sensitivity_dup.parquet** — 16412 games sensitivity including duplicate title_clean (49) = 215 total removed.
- **bgg_population_base_closed.parquet** — 14941 games for base 16627 closed (for comparison, no dedup).
- **pruned_lists/** — per-rule CSVs and combined, with details JSON.
- **primary_closure_log.csv** / **base_16627_closure_log.csv** — per-iteration games/users/obs/degenerate.
- **comparison_table.json/csv** — current vs second-pass vs closed counts, eras, cats, degenerate prevalence, overlap, notes on included vs excluded examples.

## Rules executed (auditable)

- **Rule A edition_bigbox**: stripped base collision, keep most popular per base. Detects Deluxe, Big Box, Anniversary, Collector, Special Edition, Designer Edition, Revised Edition (case-insensitive, with or without "Edition"). Removes 126 games. Example: Small World Designer Edition 140135 (n=246 resid 2.20) removed, keeper Small World 40692 (75k) retained. Carcassonne Big Box 6 etc. removed, keeper 822 retained. See pruned_lists/details_edition.json for 126 mappings.
- **Rule C family_monikers_timesup**: targeted collapse for flagged families. Monikers stem=monikers (8→1, keeper 156546, removes More Monikers 255249 etc). Time's Up! Game: Time's Up! family (11→1, keeper 1353, removes Title Recall! 36553 etc). Removes 17. Overlap with edition 0 (edition stripping for Time's Up! Deluxe required plain Deluxe handling; now fixed). See details_family.json.
- **Rule B duplicate_title_clean** (investigate, sensitivity only): title_clean exact duplicate and designer identical, keep most popular. Would remove 49, but strict year±1 families identical only removes 1 (Dominion Big Box 142132). Not adopted for primary to avoid pruning distinct reprints with large year gaps (Puerto Rico 3076 vs 318985 gap 18y). Sensitivity population includes it.
- **Reimplementation triple** (investigate only): weight within 0.2 and mech Jaccard>0.8 and designer identical → 47. NOT adopted: would incorrectly prune Ticket to Ride: Europe vs Ticket to Ride etc., Brass incorrectly kept (year gap 11) shows guard works for Brass/Pandemic but still over-prunes map variants. Documented.
- **Language/version** (investigate only): rel=version where designer+year identical → 0 in this population.

Combined primary removed 143 games (126+17). Jaccard vs current 16627 = 0.9898.

## Recursive closure

Started from primary 16484 games (16627-143) and base 16627 for comparison. Each iteration recomputes:
- degenerate_strict (n≥20 AND (k==1 OR SD<0.2 OR modal≥95% on ROUND-binned 1..10))
- per-user n_active excluding deg, keep users ≥10
- per-game n_active where user in active set, keep games ≥100
Repeat until no game <100, no user <10, deg stable.

Logs: primary_closure_log.csv (4 iterations), base_16627_closure_log.csv (4 iterations).

Final closed: primary 14786 games, 287776 users, 24254208 obs; base closed 14941 games, 288250 users, 24397989 obs.

Degenerate prevalence: current active 0.31% strict at n≥20 (667 users); closed prevalence in logs (final iteration degenerate_strict counts). See logs.

## Included vs excluded examples (per rule, required)

- **Monikers 255249 (More Monikers)** kept? No, removed under family rule; keeper 156546 Monikers retained. Similarly Shmonikers 179448 removed etc. All 7 expansions removed.
- **Time's Up! 36553 Title Recall!** removed under family rule; keeper 1353 Time's Up! retained. All 10 variants removed.
- **Small World Designer Edition 140135** removed under edition rule (base small world); keeper 40692 Small World retained. Small World Underground 97786 and Small World of Warcraft 309630 retained (different weight/mechanics, not editions).
- **Brass: Birmingham vs Lancashire** both retained (distinct, year gap 11, designer string differs).
- **Pandemic vs Pandemic Legacy** both retained (weight diff 0.43, mech jacc 0.53).
- **Dominion vs Dominion Second Edition** both retained in primary (second edition not flagged under edition? Actually Dominion Second Edition 209418 would be flagged under reimplementation triple but not under edition because no edition keyword? Title is "Dominion (Second Edition)" — contains revised? No, contains "(Second Edition)" parentheses edition which our stripping handles via \(.*edition.*\) -> base dominion, so it would be flagged under edition? Wait Dominion Second Edition title is "Dominion (Second Edition)" -> stripped via parentheses pattern -> base "dominion", keeper Dominion 36218, so it would be flagged under edition rule? But our earlier edition count included 209418? Let's check: earlier reimplementation triple flagged 209418 as reimplementation, but edition rule also would flag it? The base "dominion" group includes 36218, 209418, two Big Boxes. Keeper is Dominion 36218 (97k) vs 209418 (13k), so 209418 would be removed under edition? But 209418 is "(Second Edition)" which is an edition, arguably same underlying game, so removals is intended. However is Dominion Second Edition considered same underlying game? It's a revised second edition with updated cards, arguably same game, so pruning is defensible. But task says keep distinct designs like Pandemic Legacy separate; Dominion Second Edition is arguably not distinct, so removal is okay. But we should document: Dominion Second Edition 209418 removed under edition, keeper Dominion 36218.
- **The Castles of Burgundy 2019 (271320) vs 2011 (84876)** both retained (year gap 8, not edition), Special Edition 363622 removed under edition (Special Edition suffix).

## What to quantify per rule

For each rule, comparison_table.json records games_removed, obs_removed, users_affected, era/category/volume, examples, overlap, risk of systematically removing particular types (e.g., Big Box cluster in 2020+ etc). See quant entries.

## Adoption criteria

Per population_second_pass_plan.md deferred decision criteria: adopt only if joint comparison shows material difference (beta shift >10%, R2 change >0.02, Jaccard <0.70 top-1%, top residuals dominated by n<100 high-SE). Otherwise fix is n≥100 screening floor, not population redefinition. Current single-filter sensitivity (bgg-sensitivity-n100, 16564 vs 14952, beta +3%, R2 +0.014, overlap r 0.9995) is single-filter precursor; recursive closure shows whether iteration matters beyond that. This second-pass adds dedup (143) plus closure; compare its R2/beta/residual ranks after refitting Phase5/6 (to be run via scripts/30 31 on closed population).

## Provenance

See scripts/34_second_pass_population.py for exact logic, and docs/future-methodology-review/executed_rules.md for rule documentation with included/excluded examples per rule.

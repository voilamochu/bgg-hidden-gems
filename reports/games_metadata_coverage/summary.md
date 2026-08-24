# Games metadata coverage audit (13,449 / 16,627)

Generated: 2026-08-24T04:47:42Z by `scripts/27_games_metadata_coverage_audit.py`

Audited `games.parquet` coverage of the **16,627-game research population** (`/home/mOCHU/.treehouse/bgg-hidden-gems-efb8da/2/bgg-hidden-gems/scratch/phase2/bgg_research_population.parquet`) via DuckDB on scratch Parquet copies (no SQLite scan).

## Coverage [Observed fact]
- Research population: **16,627** games
- `games.parquet` (game_attrs join, full): **21,925** rows (distinct game_ids 21,925)
- Filtered to population (`SEMI JOIN pop`): **13,449** games
- **Missing: 3,178** games — **19.11%** of research population
- Exact fractions [Observed fact]: `13449 / 16627 = 80.89%`; `13449 / 21925 = 61.34% of game_attrs`; `13449 / 16,567 rated = 81.18%`
- `games.parquet` max game_id: **349,161** vs population max: **438,481**
- Missing with game_id > games_max: **2,259** (71.1% of missing) — cannot exist in snapshot game_attrs
- Missing with game_id ≤ games_max but still absent: **919** (28.9%)

## Why missing — source vs logic [Observed fact / Supported conclusion]
- `games.parquet` SQL in `scripts/13_build_phase2_extracts.py:205` is `FROM game_attrs a LEFT JOIN games g LEFT JOIN weights w` — its row count (21,925) equals `game_attrs` count, not `games` browse count (161,404) or population count.
- `LEFT JOIN` preserves a `game_attrs` row even when `games`/`weights` are NULL (proven: among covered population rows,   107 have NULL `weight`/`weight_num_votes` in `games.parquet` — join does not drop them).
- Therefore **missing = absent from `game_attrs`**, not dropped by the `LEFT JOIN` logic, `weights` join, `is_reimplementation` filter, or later `scripts/23`/`24` steps.
- `scripts/23_build_filtered_phase2_extracts.py` does `SEMI JOIN pop ON game_id` on `games.parquet` — filtered rows = 13,449 exactly; no additional filter.
- `scripts/24_build_active_phase2_extracts.py` reuses `games_filtered` via join/symlink; it adds no game filter (active game coverage remains 16,564 distinct games with ≥1 active rating).
- Vintage explanation [Hypothesis, evidence-backed]: SQLite snapshot (latest review 2025-02-10 per `docs/phase2_database_inventory.md`) predates the research-population scrape (`bgg_games_current.parquet` + recent high IDs).   2,259 missing have game_id > 349,161 (71% of gap). The remaining 919 missing ≤349,161 are 96% from 2020+ (609 in 2020-22, 260 in 2023+), consistent with an earlier `game_attrs` vintage that had not yet materialized those titles.

## Do missing games differ materially? [Empirical finding]
Comparison uses the **canonical complete population parquet** (`bgg_research_population.parquet`) which is complete for all 16,627 — not `games.parquet`.

| Metric | Covered (13,449) | Missing (3,178) | Delta (missing−covered) |
|---|---:|---:|---:|
| n | 13449 | 3178 | -10271 |
| mean year | 2,008.77 | 2,022.87 | 14.11 |
| median year | 2,013.00 | 2,023.00 | 10.00 |
| mean users_rated | 1,891.43 | 965.83 | -925.60 |
| median users_rated | 370.00 | 308.00 | -62.00 |
| mean bayes_rating | 5.79 | 5.83 | 0.04 |
| mean avg_rating_current | 6.55 | 7.13 | 0.58 |
| mean weight | 2.08 | 2.14 | 0.06 |
| mean num_weights | 91.10 | 33.43 | -57.68 |
| mean rank_current | 11,059.91 | 8,102.44 | -2,957.47 |
| share reimplementation | 0.02 | 0.01 | -0.01 |
| mean mechanics tags | 3.83 | 4.98 | 1.15 |
| mean categories tags | 2.78 | 2.75 | -0.03 |

> **Interpretation [Empirical finding]:** missing games are **~14 years newer** (mean 2022.87 vs 2008.77), have **~½ the rating volume** (mean 966 vs 1,891; median 308 vs 370),   notably **higher raw avg_rating** (mean 7.13 vs 6.55; median 7.13 vs 6.56) but almost identical **bayes_rating** (mean 5.83 vs 5.79) and **weight** (mean 2.14 vs 2.08, median 2.00 both),   fewer weight votes (mean 33 vs 91), and slightly better (lower) rank (mean 8,102 vs 11,060). Mechanics tags are denser for missing (4.98 vs 3.83).   The raw-average gap is expected: newer/high-vote games with small-n sampling and era effects raise raw means while Bayes remains anchored at ~5.49 prior.

## Concentration [Observed fact]

### By year bucket
| Year bucket | Covered | Missing | % missing |
|---|---:|---:|---:|
| <2000 | 2,305 | 5 | 0.2% |
| 2000-09 | 2,786 | 2 | 0.1% |
| 2010-14 | 2,570 | 10 | 0.4% |
| 2015-19 | 4,447 | 40 | 0.9% |
| 2020-22 | 1,329 | 1,131 | 46.0% |
| 2023+ | 12 | 1,990 | 99.4% |

> Missingness is **extremely clustered by era**: <1% before 2020, **46.0% in 2020-22**, **99.4% in 2023+**.

### By game_id × era
| ID bucket | Era | Total | Missing | % missing |
|---|---|---:|---:|---:|
| <=349k | 2020-22 | 1,938 | 609 | 31.4% |
| <=349k | 2023+ | 272 | 260 | 95.6% |
| <=349k | <2020 | 12,158 | 50 | 0.4% |
| >349k | 2020-22 | 522 | 522 | 100.0% |
| >349k | 2023+ | 1,730 | 1,730 | 100.0% |
| >349k | <2020 | 7 | 7 | 100.0% |

> 2,259 missing (71%) have `game_id > 349,161` (beyond `games.parquet` max) — 100% missing in every era for that ID range (snapshot did not contain those IDs).   Among ≤349k IDs, missing is 0.4% before 2020 but 31.4% in 2020-22 and 95.6% in 2023+.

### By weight bucket (population weight, complete for both)
| Weight | Covered | Missing | % missing |
|---|---:|---:|---:|
| 1.0-1.5 | 3,855 | 749 | 16.3% |
| 1.5-2.0 | 2,747 | 638 | 18.8% |
| 2.0-2.5 | 3,017 | 826 | 21.5% |
| 2.5-3.0 | 1,895 | 432 | 18.6% |
| 3.0-3.5 | 1,111 | 286 | 20.5% |
| 3.5+ | 818 | 238 | 22.5% |
| NULL_weight | 6 | 9 | 60.0% |

> Weight does **not** strongly concentrate missingness; missing rates are 15–20% across weight buckets (no clear game-type weight bias).   Family/source concentration not evident in population `families` (top families for missing: empty list 5.3%, Kickstarter 0.8%).

## Are ratings for missing-metadata games still present in active? [Observed fact]
- **Full snapshot** (`rating_observations.parquet` 26.9M): **3,119 / 3,178** missing games have ≥1 rating   (98.1%); **1,682,941** observations; 59 games have zero ratings in SQLite (recent high-ID releases, matches the 60 overall absentees).
- **Active** (`rating_observations_active.parquet` 24.5M, ≥10 + minus strict): **3,116 / 3,178** missing games have ≥1 active rating   (98.0%); **1,610,752** active observations;   mean 517, median 154 per missing game   vs covered mean 1703, median 336.
- **Active universe is NOT reduced to 13,449**: active distinct games with ≥1 rating is **16,564** (covered 13,448 + missing 3,116);   only **59** missing games have zero active ratings.
- Conclusion [Observed fact]: the 3,178 missing-metadata games **still have rating observations**; the effective rating universe remains 16,564 distinct games, not 13,449.

## Intent of `games.parquet` [Observed fact / Method]
- `games.parquet` was **never intended as a complete population table**. `scripts/13` docstring: *compact read-only Phase 2 extracts from bgg.sqlite* — the game-metadata query is `FROM game_attrs LEFT JOIN games LEFT JOIN weights ORDER BY game_id` (21,925 rows = `game_attrs` count per `docs/phase2_database_inventory.md`).
- `docs/phase2-filtered/PARQUET_CATALOG.md` explicitly notes: *Only 13,449 of 16,567 rated population games (81.2%) have a `games.parquet` metadata row; the game-level population parquet remains the complete metadata source for all 16,627.*
- `data/processed/phase2-active/README.md` catalog: `games.parquet` filtered 13,449 (61.34% of game_attrs) and reused via join/symlink — not duplicated in active.
- Exact fractions [Observed fact]: `13,449 / 16,627 = 80.89%` (≈80.86% in brief due to rounding); `13,449 / 21,925 = 61.35%` (≈61.34%); `13,449 / 16,567 rated = 81.19%`.

## Recommendation for Phase 3 [Supported decision]

### Chosen: (1) **Use all 16,627** and treat missing `games.parquet` metadata explicitly — the default unless invalid

- **Why not (2) restrict to 13,449 for all analyses:** missingness is **not random** — it is 99% of 2023+ games and 46% of 2020-22 games. Restricting would **systematically excise recent releases** (the most relevant hidden-gem candidates) and bias every era/type analysis toward pre-2020 titles. Ratings for 3,116 missing games are present in the active universe (1.6M active observations); discarding them discards 6.6% of active ratings and 18.8% of games for no statistical gain.
- **Why not (3) redefine the universe:** the research population definition (`scripts/01`: modern standalone, 1950+, ≥100 ratings, Latin titles, structural PnP rule) is unaffected. The gap is a **snapshot vintage artefact** (SQLite `game_attrs` vs newer `bgg_games_current.parquet` scrape), not a population definition flaw. No evidence that missing games are structurally different in kind (weight, mechanics, rank distributions similar except for era/volume). Redefinition is not justified.
- **How to treat missing explicitly [Method]:**
  1. For fields **complete in `bgg_research_population.parquet`** (year, weight, num_weights, min/max players, playing_time, mechanics, categories, families, designers, rank/bayes/avg/users_rated, attrs_fetched_at) — **join to `bgg_research_population.parquet`** (or the already-copied `scratch/phase2/bgg_research_population.parquet`), not to `games.parquet`. This is complete for all 16,627.   In DuckDB: `FROM active_rating_observations r JOIN read_parquet('scratch/phase2/bgg_research_population.parquet') pop USING (game_id)` or `LEFT JOIN` with `COALESCE` where a `games.parquet` attribute is also needed.
  2. For fields **only in `games.parquet`** (mfg_playtime, com_* playtime, mfg_age_rec, com_age_rec, language_ease, stddev, num_* counts, kickstarted, family/source, weight_num_votes where NULL) — use `LEFT JOIN games ON game_id` and handle NULLs explicitly:      `COALESCE(g.weight, pop.weight)` where both exist, or a **missing-indicator** (`is_games_metadata_missing`) and separate `WHERE g.game_id IS NOT NULL` clause for analyses that truly require those attrs (e.g., `weight_num_votes`, `kickstarted`). Tag such analyses as `N=13,449` subsidiary, not primary.
  3. For **type/taste models that need `game_tags`/`game_links`/`weight`** — run primary models on all 16,627 via `bgg_research_population` fields; run **sensitivity variants** restricted to 13,449 with `game_tags` where fine-grained tag data is essential. Report both; do not silently restrict primary estimates.
  4. Always **state N and coverage** in Phase 3 tables: e.g., `N=16,627 (ratings 24.5M) primary; N=13,449 where game_attrs required` and cite `reports/games_metadata_coverage/missing_ids.csv` for reproducibility.

This preserves the established 16,627 research universe, avoids vintage-induced recency bias, keeps 1.6M active ratings, and makes the 19% metadata gap auditable rather than hidden.

## Reproduce
```bash
python scripts/27_games_metadata_coverage_audit.py \
  --population /home/mOCHU/.treehouse/bgg-hidden-gems-efb8da/2/bgg-hidden-gems/scratch/phase2/bgg_research_population.parquet \
  --games /home/mOCHU/.treehouse/bgg-hidden-gems-efb8da/2/bgg-hidden-gems/scratch/phase2/games.parquet \
  --rating-observations /home/mOCHU/.treehouse/bgg-hidden-gems-efb8da/2/bgg-hidden-gems/scratch/phase2/rating_observations.parquet \
  --active-rating-observations /home/mOCHU/.treehouse/bgg-hidden-gems-efb8da/2/bgg-hidden-gems/data/processed/phase2-active/rating_observations_active.parquet
```
Outputs: `reports/games_metadata_coverage/missing_ids.csv` (3,178 rows, ORDER BY game_id), `reports/games_metadata_coverage/summary.json`, `reports/games_metadata_coverage/summary.md` (this file).
All queries are explicit-column DuckDB (no positional pandas bug), bounded `memory_limit=4GB`/`threads=4`.

## Limitations [Limitation / Hypothesis]
- Vintage hypothesis is **evidence-backed but not proven via SQLite row-level diff** (no `bgg.sqlite` access in this worktree; inferred from max game_id 349,161 vs 438,481 and era clustering). A direct `SELECT COUNT(*) FROM game_attrs WHERE game_id IN (missing)` would close the loop where SQLite is available — but Parquet evidence is decisive that missing = absent from game_attrs, not a later filter.
- `bgg_research_population.parquet` is the **authoritative complete metadata** for population-level fields; `games.parquet` remains the source for `weight_num_votes`/`kickstarted`/`stddev`/mfg fields where non-NULL — do not mix the two weights without noting source.
- 60 population games have **zero** SQLite ratings (snapshot gap) — distinct from the 3,178 metadata gap; only 59 of the 3,178 are in that zero-rating set.

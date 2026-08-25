---
name: bgg-analytical-research
description: Conduct efficient, reproducible statistical analysis for the BGG Hidden Gems project using DuckDB and Parquet. Use for dataset exploration, user-level rating analysis, modelling, validation, and research findings.
---

# BGG Analytical Research

## Analytical universe

- The corrected 16,627-game research population is the primary universe for active analysis.
- Full-snapshot extracts are reference data unless a task explicitly requires the broader BGG ecosystem.
- State the analytical universe for every substantive result.
- Never silently change the research population.

## Data workflow

- Treat `data/raw/` as immutable.
- Use Parquet + DuckDB for active analysis; do not routinely query the 9 GB SQLite source.
- Prefer SQL aggregation and compact intermediate tables over large pandas DataFrames.
- Avoid materializing tens of millions of rows unless necessary.
- Build reusable filtered extracts when repeated analysis would otherwise rescan large datasets.
- Prototype expensive queries on a sample before full execution.

## Validation

- Check row counts, join cardinality, nulls, ranges, and other relevant invariants before trusting results.
- For important statistics, independently reproduce or sanity-check the calculation where practical.
- Do not treat a successful query as evidence that the result is correct.
- Stop and fix a correctness problem rather than completing an expensive run with questionable results.

## Statistical discipline

Keep these distinct:

- rater severity;
- rater calibration / informativeness;
- rater taste;
- selection into the population of people who rate a game.

Do not assume low-volume users are fake, generous, or unreliable without evidence.

Do not equate correlation with bias or causation. Prefer the simplest defensible analysis and earn additional complexity through evidence and validation.

## Hidden-gem objective

Keep the three questions separate:

1. What can we estimate about underlying game quality?
2. Which games are higher-rated than expected?
3. Which of those show evidence of appeal beyond their existing niche?

A positive residual is not a hidden gem. Do not collapse quality, underratedness, and broad appeal into one score without evidence.

## Documentation

- Record substantive findings and methodological decisions in `findings.md`.
- Keep analyses reproducible and numbered consistently with the existing series.
- Record important assumptions, analytical universe, coverage, and limitations.
- Update the research roadmap when evidence changes the planned sequence.
# AGENTS.md

## Project
Exploratory analysis of BoardGameGeek (BGG) rating data, investigating whether the data can identify genuine **hidden gems** — see README.md for the full framing.
This is not a project to produce a clever ranking formula. It's a project to understand what the data can support, and only build models once the evidence justifies them. It is acceptable for the final conclusion to be "the data can't answer this reliably" — that's a valid result, not a failure.

## Research questions
1. **Rating estimate** — best estimate of a game's underlying quality given noisy observed ratings.
2. **Underratedness** — which games perform better than expected given popularity, age, genre, complexity, audience?
3. **Hidden gem** — of the underrated games, which show evidence their appeal extends beyond the niche currently rating them?
The gap between #2 and #3 is the whole point of this project. A game can be genuinely excellent and still not be a hidden gem if its appeal is inherently niche.

## The central problem: self-selection
BGG ratings aren't a random sample of people encountering each game — people choose what to buy, back, play, and rate. This means:
- a high rating from a small group ≠ broad appeal
- low rating count ≠ "just needs more data to converge"
- sample-size shrinkage alone cannot fix this — it corrects for *noise*, not for *who's in the sample*

When evaluating any proposed correction (yours or a prior one, e.g. the friend-provided debiased ranking in `data/`), always classify what it actually addresses: measurement noise, or selection into the population being measured. Don't conflate the two. This is the one idea in this file worth re-reading if anything else is unclear.

## Working principles
- **Earn complexity.** Try the simplest approach first. Add weighting schemes, priors, or hierarchical structure only once a simpler baseline has been tried and shown to fall short — and show that comparison, don't just assert it.
- **Don't assume correlation = bias.** For any proposed correction, state what phenomenon it targets, what else could produce the same pattern, and whether the available data can actually distinguish between them. Keep competing explanations open until the data can distinguish between them.
- **A plausible-looking output isn't validation.** "This produced an interesting hidden-gems list" is not evidence the method is right. Use held-out data, stability checks, or prediction where possible.
- **Don't overclaim precision.** If something can't be identified from this data, say so explicitly rather than presenting a proxy as an answer.
- **Tag every claim**: observed fact from the data / empirical finding / assumption / hypothesis / model-dependent conclusion / speculation. Don't let a hypothesis quietly become a fact in the next write-up.

## Data handling
- `data/raw/` is immutable. Never edit in place — transformations live in scripts and write to `data/processed/`.
- Don't assume missing data is random; check before dropping.
- Don't use BGG rank as a proxy for rating unless explicitly justified in that analysis.
- The current data is **game-level**, not individual-rating-level. Don't assume user-level bias, rating drift, or rater credibility can be estimated unless you've confirmed the data actually supports it.
**Starting population — treat as candidate filters to test, not a fixed spec:** one record per game, non-expansion, published, non-future, some minimum rating-count floor. Before applying any of these, inspect their actual effect on the dataset (how many games excluded, any lopsided exclusion by genre/weight/year) and record it. Don't add further filters without a stated reason.

## User-level data (Phase 2)
The user-level layer lives in `data/processed/phase2/` (parquet extracts of `data/raw/bgg.sqlite`, built read-only by `scripts/13`; see its README). Query with DuckDB. Key facts: `rating_observations.parquet` is the canonical 26.9M-row rating table (no deduplication; repeated user-game rows are rare but real); `user_ratings.parquet` does not join to `users`; timestamp semantics for `postdate`/`rating_tstamp` are unresolved — run every time-based result under both readings. Per-user volume bands, severity offsets (`user_severity.parquet`), and severity-adjusted game means (`game_adjusted_means.parquet`) come from `scripts/15`–`16`. Established: the low-vs-high-volume rater gap is almost entirely additive rater-level level differences (see findings.md Phase A entries); treat "severity" as descriptive level, not credibility or causal disposition.

**Filtered universe (primary for quality/taste/hidden-gem work):** `data/processed/phase2-filtered/` (built by `scripts/23`) restricts the rating observations, games/users/tags/links/collections extracts to the 16,627-game research population (25.3M of 26.9M observations; 16,567 games have ratings in the SQLite snapshot). The full-snapshot extracts and the scripts 15–22 fit artifacts are historical reference for that universe — do not mix filtered observations with full-snapshot parameters. Counts, validation, and caveats: `docs/phase2-filtered/PARQUET_CATALOG.md`.

## Baselines
Treat as reference points, not ground truth to be "fixed": raw average rating, BGG Geek/Bayesian rating, rating count, BGG rank. The friend-provided debiased ranking is also a baseline/hypothesis to investigate, not a correct or incorrect prior.

## Stack & repo layout
Assumed Python + pandas (adjust if wrong).

```
data/raw/          immutable source data
data/processed/    derived datasets, reproducible from raw + scripts
scripts/           one script per analysis step, rerunnable
notebooks/          exploratory only — anything worth keeping graduates to scripts/
findings.md         running, dated log of what's been learned (see below)
```
- Prefer scripts over one-off notebook cells once a direction is established — notebooks are fine for exploration, not for anything meant to be rerun or trusted later.
- Set random seeds anywhere sampling/resampling is involved.
- No large analysis framework up front — build the smallest thing that answers the current question.

## Findings log
Agent sessions don't share memory. `findings.md` is a dated lab notebook, not a polished report. Create it if it doesn't exist, then append to it at the end of any session that produces a real result — a few lines: what was tested, what was found, what's still open. Next session reads this first before re-deriving things already established.

## Workflow
Before a substantial change:
1. inspect the relevant data/files
2. state what's known and what's still uncertain
3. make the smallest useful change
4. run appropriate checks
5. report what changed and what was learned — and append it to `findings.md` if it's a real result

## Communication
- Lead with the finding, quantify it.
- Distinguish statistical significance from practical significance.
- State limitations, don't bury them.
- If the data can't answer the question, say that plainly — don't manufacture a proxy and present it as an answer.

## Definition of success
Determining, as rigorously as the data permits: **which games appear genuinely underrated, and which of those show evidence of appeal beyond their existing niche.** A well-supported "we can't tell" beats an elaborate ranking that can't survive scrutiny.

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.

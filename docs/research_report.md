# BGG Hidden Gems: Research Report

## Purpose

This project asks whether BoardGameGeek data can identify games that are not only highly rated relative to expectations, but also have appeal beyond the niche of people who currently rate them.

The questions are deliberately separate:

1. **RQ1 — Rating estimate:** What can the observed ratings support as an estimate of game quality?
2. **RQ2 — Underratedness:** Which games rate higher than expected given their observed popularity and characteristics?
3. **RQ3 — Hidden gem:** Which underrated games show evidence of appeal beyond their existing audience?

The distinction between RQ2 and RQ3 is central. “Higher than expected” is not the same claim as “broadly appealing.”

## Data and process

The raw BGG file contains **161,404 rows and 34 fields**. The current cleaning pipeline produces a research population of **16,627 games** by retaining valid, published, non-expansion records with at least 100 ratings, Latin-script titles, and physical-commercial eligibility under the project’s structural PnP/self-published rule, while excluding explicit BGG `Admin: Upcoming Releases` and `Admin: Unreleased Games` statuses. Standalone reimplementations are retained. The 100-rating floor reduces extreme measurement noise but excludes many genuine niche and newly published games.

The current population is **99 games smaller** than the population used for the earlier numerical summaries in this report because those summaries predate the explicit release-status correction. They should be rerun before being treated as current estimates. The unchanged RQ2 candidate-screening report has been regenerated against the corrected population.

The analyses are game-level and descriptive:

- rating-volume bands compare raw averages, Bayesian ratings, and distributions;
- within-group comparisons examine year, complexity, playtime, player count, reimplementation status, categories, mechanics, and rank;
- nested transparent expected-rating specifications use **16,612 current complete cases** with rating volume, year, weight, structural fields, and selected BGG tags;
- residual robustness compares nine specifications, with seven adjusted variants used for stable-candidate summaries;
- audience-tag and family-field audits test whether existing metadata supplies independent reach evidence.

No user-level debiasing or final ranking model has been built.

## RQ1 — What the ratings can estimate

### Findings

- **[Observed fact]** Rating volume is highly concentrated. The median game has **354 ratings**, and the top 1% of games account for **27.2%** of all ratings.
- **[Empirical finding]** Mean raw rating rises from **6.435** among games with 100–199 ratings to **7.531** among games with 25k+ ratings. Cross-game rating spread declines with volume, but much more slowly than expected from ordinary averaging noise around a common mean.
- **[Supported conclusion]** Sampling noise is present, particularly near the rating floor, but it is not enough to explain the approximately 1.1-point cross-volume shift or the persistent within-group association. Popularity and composition selection are major parts of the observed pattern.
- **[Model-dependent conclusion]** `bayes_rating` is primarily a volume-weighted transformation of the raw average. It is a useful shrinkage and ranking baseline, but the current data do not establish it as the population-wide underlying quality of a game.

The retained population is itself selected. Older, casual, and some niche categories are less likely to reach 100 ratings; expansions show strong fan-survivorship effects and are excluded. High-volume games also differ systematically in weight, era, reimplementation status, and category/mechanic composition.

### What remains unresolved

**[Limitation / unresolved hypothesis]** For an individual low-volume game, the dataset cannot distinguish rating noise, niche self-selection, early evidence of broad appeal, or a combination. Individual-rating distributions, rater identities, rating histories, and exposure/non-rater data are absent.

## RQ2 — Higher than expected / underratedness

### Method

The project defines a descriptive residual as:

> observed average rating − expected average rating under a stated baseline.

The primary S3 baseline uses rating volume, release year, complexity, playtime, player counts, reimplementation status, and frequent BGG category tags. Sensitivity variants add mechanics and replace linear volume/year terms with volume bands and release decades. BGG rank and Bayesian rating are comparison baselines, not model predictors.

### Findings

- **[Empirical finding]** The primary S3 model explains meaningful but incomplete variation (**R²=.5393**, RMSE **.5523**; cross-validated RMSE **.5537**). More flexible volume/year forms improve fit modestly.
- **[Model-dependent conclusion]** A positive residual means that a game’s observed BGG average is higher than expected for comparable games in the retained BGG population under that specification. It is not a recovered latent-quality estimate, a causal effect, or evidence of broad appeal.
- **[Model-dependent conclusion]** The S3 residual is distinct from the reference scores: its correlation with raw average is **.679**, with Bayes **.194**, and with log rating volume approximately zero. It is therefore not simply a re-ranking of BGG Bayes.
- **[Empirical finding]** Residual ordering is moderately to strongly stable across reasonable specifications, but exact top lists are not. Across seven adjusted specifications, the top-1% union contains **325 games**, of which **117** are selected in at least 5/7; the top-5% union contains **1,460 games**, of which **625** are stable by the same convention.
- **[Supported conclusion]** A stable residual is a more reproducible conditional anomaly than a specification-specific residual. This is robustness to shared data and modeling choices, not independent replication.
- **[Empirical finding / interpretation]** Stable candidates are heterogeneous. Social/party/sports, card/fantasy, narrative, miniature, and tactical patterns all occur. Some wargame/WWII/Simulation patterns are more specification-sensitive, while Card/Fantasy/Sports patterns are more reproducible.

### What RQ2 does not establish

**[Limitation]** Residuals use equal game weighting, overlapping metadata tags, and deliberately limited features. A positive residual may reflect genuine quality, niche self-selection, edition or visibility effects, omitted structure, rating noise, or a mixture. Even a stable positive residual says only “higher than expected under these baselines,” not “a hidden gem.”

## RQ3 — Hidden gems and broad appeal

### Identifiability result

- **[Observed fact]** The dataset has no rater segments, ratings by market/language/demographic group, exposure denominator, non-rater information, plays, ownership, sales, external traffic, or independent audience outcome.
- **[Supported conclusion]** `users_rated` measures participation in the selected BGG rating population. It does not measure audience breadth or diversity, and it is already an RQ2 input.
- **[Observed fact / interpretation]** Categories, mechanics, complexity, player counts, family tags, digital implementations, Kickstarter links, tutorials, and related metadata provide product or exposure context, not observed cross-audience response.
- **[Supported conclusion]** RQ3 is not identified by the current game-level dataset. No broad-appeal score or hidden-gem ranking is justified.

The project’s audience-proxy work finds no single breadth pattern among stable RQ2 residuals. Some candidates look socially accessible in ordinary category terms; others occupy recognizable specialist niches. These are descriptive profiles, not evidence that appeal extends beyond existing BGG raters.

The friend-provided debiased-ratings file is available at `data/raw/complete_2025_bgg_debiased_ranks.csv`, including `game_id` and `debiased_rating`. A game-level comparison with the current baselines is documented in the later findings entry; this does not validate the underlying user-level method. The `dump_*` fields remain legacy/current BGG fields, not a substitute; their voter-count differences are consistent with an earlier BGG snapshot, but no dump timestamp exists, so they do not provide leakage-safe temporal validation or user-level method validation.

## Strongest conclusions currently supported

1. **[Supported conclusion]** Rating-volume differences are not explained by sampling noise alone. Popularity and composition selection are clearly involved, although the game-level data cannot identify the rater-pool mechanism for individual games.
2. **[Supported conclusion]** A transparent RQ2 residual can identify games whose observed ratings are higher than expected under explicit, limited baselines. Stability across specifications makes that signal more reproducible, but still model-dependent.
3. **[Supported conclusion]** “Higher than expected” is not equivalent to “broad appeal.” The current dataset cannot establish whether a game’s appeal generalizes beyond the people who selected and rated it on BGG.
4. **[Supported conclusion]** The defensible current endpoint is descriptive RQ1/RQ2 analysis and candidate screening—not a final hidden-gem ranking.

## What requires a richer dataset

Further progress requires data that preserve pseudonymous user-game ratings, rating timestamps, user participation/history context, and an independent exposure or audience-segment outcome. Those data would allow the project to investigate:

- per-game rating uncertainty and underlying quality;
- whether rater composition changes with rating volume;
- whether RQ2 residuals generalize out of time or beyond the retained BGG population;
- whether different audience segments encounter and rate the same games similarly;
- what the newly available friend output actually changes and whether its method targets measurement noise, selection, or both.

Until then, the project can describe conditional underrating signals, but it cannot identify hidden-gem breadth.

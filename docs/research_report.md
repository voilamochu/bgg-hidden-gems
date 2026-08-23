# BGG Hidden Gems: Research Report

## Purpose

This project asks whether BoardGameGeek data can identify games that are not only highly rated relative to expectations, but also have appeal beyond the niche of people who currently rate them.

The questions are deliberately separate:

1. **RQ1 — Rating estimate:** What can the observed ratings support as an estimate of game quality?
2. **RQ2 — Underratedness:** Which games rate higher than expected given their observed popularity and characteristics?
3. **RQ3 — Hidden gem:** Which underrated games show evidence of appeal beyond their existing audience?

The distinction between RQ2 and RQ3 is central. “Higher than expected” is not the same claim as “broadly appealing.”

## Data and process

Two data layers are now available:

- **Game-level snapshot** (`data/raw/bgg_games_current.parquet` → `data/processed/bgg_research_population.parquet`): **16,627 games** after cleaning, including exclusion of explicit BGG unreleased-status records. The RQ2 baseline uses **16,612 complete cases**.
- **User-level SQLite snapshot** (Phase 2, `data/processed/phase2/`): canonical individual-rating extract with **26,924,709 observations**, **571,248 raters**, **95,540 games**, per-user volume bands, and collection status. The two snapshots are different scrapes; raw game means agree across them (Pearson 0.979 on matched games).

Game-level analyses remain descriptive (volume bands, composition, nested RQ2 specifications S0–S6, residual robustness, audience tags). Phase 2 added user-level analyses: same-game volume-band contrasts, two-way additive severity fits, stability and held-out tests, gap decomposition, temporal-drift sensitivities, audience/ownership contrasts, cross-audience consistency, and a comparison of all resulting estimates against the existing baselines and the friend-provided `debiased_rating`.

## RQ1 — What the ratings can estimate

### Findings

- **[Observed fact]** Rating volume is highly concentrated. The median game has 354 ratings, and the top 1% of games account for 27% of all ratings.
- **[Empirical finding]** Mean raw rating rises from ~6.42 among games with 100–199 ratings to 7.53 among games with 25k+ ratings. Cross-game spread declines with volume far more slowly than sampling noise predicts.
- **[Empirical finding — user level]** The low-vs-high lifetime-volume rater gradient (+8.85 to −6.40 pooled means) survives almost unchanged *within the same games*: paired within-game gaps are +2.28 (band '1' vs '1000+') and +1.28 (bands '2–24' vs '500+'); a game-FE regression reproduces the full band curve. Game mix explains only ~18% of the raw gap.
- **[Empirical finding — user level]** Two-way additive fits show stable per-user severity offsets spanning ~2.1 points across volume bands; parity-half reliability reaches ≥0.89 by 50 observations. Nested-model decomposition: game identity explains R²=0.230 of individual-rating variance, rater identity 0.249, additively together 0.438.
- **[Empirical finding — user level]** Standardizing game mix and subtracting severity offsets closes the standardized low-vs-high gap from +1.69 to **+0.01**: the pattern is essentially entirely an additive rater-level level difference, not measurement noise and not which games each group rates.
- **[Empirical finding]** Removing rater-level offsets does not shrink the game-level volume gradient — it increases it (+0.44 raw vs +0.51 adjusted per tenfold ratings). Harsher veteran pools rate the most-popular games, so rater-level composition works against the observed popularity premium.
- **[Supported conclusion]** Sampling noise is not sufficient to explain cross-volume patterns at either level. Popularity/composition selection dominates at game level; rater-level level differences dominate the within-game volume-band differences.

### What remains unresolved

**[Limitation / unresolved hypothesis]** Per-user "severity" is descriptive level. It may partially encode enthusiasm trajectories (fading enthusiasm → more games rated more harshly), which the data cannot separate from dispositional scale anchoring. Adjusted game means remove measured rater composition but do not thereby become better predictors of observed ratings (held-out RMSE worsens for game-only adjusted predictions), nor do they measure broad appeal.

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

### Phase 2 user-level evidence on corrections

- **[Empirical finding]** The friend-provided `debiased_rating` correlates 0.996 (Pearson and Spearman) with the severity-adjusted mean computed from user-level data; its per-game correction regresses on ours as −0.49 + 0.67·our_shift (r=0.836). Its output targets the same phenomenon: rater-level level differences conditioned on games. Magnitude and centering conventions remain undocumented.
- **[Supported conclusion]** Per AGENTS.md's classification, that phenomenon is selection into the rating population expressed as rater-level level differences — not measurement noise (offsets are stable across independent halves) and not game-mix composition (which explains ~18% of the raw gap).
- **[Limitation]** Neither our adjustment nor the friend's addresses within-game self-selection or broad appeal; neither is a validated quality estimate.

## RQ3 — Hidden gems and broad appeal

### Identifiability result

- **[Observed fact]** The user-level snapshot adds rater geography and snapshot-time ownership status, but still has no exposure denominator, non-rater information, plays, sales, external traffic, or independent audience outcome.
- **[Empirical finding]** Geographic audiences agree closely on which games are good (cross-country game-mean correlations r≈0.85–0.87; median |difference| ≈ 0.24) while selecting somewhat different games. Owner vs non-owner raters disagree far more on the same games (median |difference| 0.95): the largest observed audience split is commitment/ownership, not country.
- **[Observed fact / interpretation]** Categories, mechanics, complexity, player counts, family tags, digital implementations, Kickstarter links, tutorials, and related metadata provide product or exposure context, not observed cross-audience response.
- **[Supported conclusion]** RQ3 remains not identified. Ownership status is a promising audience-stratification variable for future work, but it is a snapshot status, not exposure history, and cannot by itself establish appeal beyond an existing niche.

The project’s audience-proxy work finds no single breadth pattern among stable RQ2 residuals. Some candidates look socially accessible in ordinary category terms; others occupy recognizable specialist niches. These are descriptive profiles, not evidence that appeal extends beyond existing BGG raters.

## Strongest conclusions currently supported

1. **[Supported conclusion]** Rating-volume differences are not explained by sampling noise alone at either the game or rater level. Popularity/composition selection is clearly involved.
2. **[Empirical finding → supported conclusion]** The low-vs-high-volume rater gradient is real, within-game, and almost entirely an additive rater-level level difference: stable enough to estimate (reliability ≥0.89 with ≥50 observations), large (~2 points across bands), and not explained by era composition or career hardening.
3. **[Supported conclusion]** Severity-adjusted game estimates are implementable (`data/processed/phase2/game_adjusted_means.parquet`) and change game rankings materially (median shift +0.67 points), but they answer "level net of who rated it," not latent quality, and do not predict observed ratings better than raw averages.
4. **[Model-dependent conclusion]** The friend-provided correction targets the same measured phenomenon and largely reproduces the same ordering; it should be treated as one severity-adjustment variant among others, not as validated debiasing.
5. **[Supported conclusion]** “Higher than expected” is still not equivalent to “broad appeal.” Cross-audience consistency is high for geography and much lower for ownership status, but no available field establishes whether a game’s appeal generalizes beyond the people who selected and rated it on BGG.

## What requires richer data

- **Within-game selection:** separating additive severity from enthusiasm trajectories (users whose interest faded rate more games more harshly) needs longitudinal user activity or external engagement data.
- **RQ3 measurement:** an exposure denominator and/or audience-stratified outcomes independent of the BGG rating process (plays, sales, panels); ownership history rather than snapshot status would be a start.
- **Validation of any correction:** an independent outcome to test whether severity-adjusted estimates predict future ratings or external judgments better than raw averages.

Until such data exist, the defensible endpoint remains transparent descriptive estimation and candidate screening, now extended with reproducible user-level severity adjustments and explicit classification of what each correction does and does not address.

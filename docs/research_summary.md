# BGG Hidden Gems — Research Summary

This project studies whether BGG data can distinguish genuinely underrated games from games that are simply highly rated by a small, self-selected niche.

Source: [findings.md](../findings.md) and [research_handoff.md](research_handoff.md).

## Approach

The raw BGG snapshot is now cleaned into a population of **16,627 published, non-expansion games** with at least 100 ratings, Latin-script titles, explicit BGG upcoming/unreleased statuses excluded, and the project’s structural commercial-product filters. The analyses are game-level and descriptive. Earlier numerical summaries in this document used the pre-correction population of 16,726 games; they should be rerun before being treated as current. The unchanged RQ2 candidate report has been regenerated against the corrected population.

## What the data establish

### Rating estimates (RQ1)

Rating volume is highly skewed: the median game has 354 ratings, while the top 1% account for 27.2% of all ratings. Mean raw rating rises from **6.435** at 100–199 ratings to **7.531** at 25k+ ratings. The spread narrows with volume, but not as fast as ordinary sampling noise alone would predict.

**Current conclusion:** sampling noise matters, especially near the rating floor, but popularity and composition selection are major parts of the pattern. BGG’s Bayesian rating is a useful volume-weighted baseline, not established population-wide truth.

### Higher than expected (RQ2)

The project’s descriptive residual is observed average rating minus expected average rating under a stated baseline using rating volume, year, complexity, structural fields, and BGG category/mechanic tags. The primary baseline explains meaningful but incomplete variation (**R²=.5393**, cross-validated RMSE **.5537**).

Residuals are moderately to strongly stable across reasonable specifications, but exact top lists are not. Among seven adjusted specifications, 117 of the 325 top-1%-union games and 625 of the 1,460 top-5%-union games meet the project’s stability threshold.

**Current conclusion:** a stable positive residual is a more reproducible conditional anomaly. It means “higher than expected under these baselines,” not “true latent quality,” “causal underratedness,” or “broad appeal.” Stable candidates include heterogeneous social, sports, card, fantasy, narrative, miniature, and tactical patterns.

### Hidden gems and broad appeal (RQ3)

The dataset has no rater segments, exposure denominator, non-rater information, plays, ownership, sales, external traffic, or independent audience outcome. `users_rated` measures participation in the selected BGG population, not audience breadth. Categories, mechanics, family tags, and format fields provide context, not cross-audience evidence.

**Current conclusion:** RQ3 is not identifiable from this game-level dataset. A high or stable RQ2 residual cannot be promoted to hidden-gem status, and no broad-appeal score or hidden-gem ranking is justified.

## Main limitations

- The 100-rating floor reduces noise but excludes many genuine niche and newly published games.
- The data contain no individual ratings, rater identities, rating histories, or per-game rating distributions.
- Residuals are model-dependent, equally weight games, and use overlapping/incomplete metadata.
- Audience proxies are descriptive and cannot distinguish broad appeal from strong niche fit.
- The friend-provided dataset is available at `data/raw/complete_2025_bgg_debiased_ranks.csv`, including `game_id` and `debiased_rating`. Its game-level differences from the current baselines are documented in the later findings entry; this is not validation of the underlying user-level method.

The strongest defensible endpoint so far is descriptive RQ1/RQ2 analysis and candidate screening. Establishing hidden-gem breadth requires richer user-level and independent exposure/audience data.

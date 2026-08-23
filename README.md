# BGG Hidden Gems
Investigating whether BGG rating data can identify games that are underrated *and* have broad appeal beyond the niche audience currently rating them — as opposed to games that are simply excellent within a small, self-selected niche.

## The core distinction
A game can be underrated without being a hidden gem.
**Underrated** means it performs better than we would expect given what we know about the game and its audience.
**Hidden gem** means it is underrated *and* there is evidence that its appeal extends beyond the niche that currently knows, plays, and rates it.

Three progressively harder questions:
1. **Rating estimate** — what's the best estimate of a game's underlying quality given the noise in its ratings?  
   Baseline: compare against BGG's own Bayesian rating. Don't assume it's wrong; understand what it gets right and where it may break down.
2. **Underratedness** — does the game perform better than we'd expect given its popularity, age, genre, complexity, and *audience*?
3. **Hidden gem** — among the underrated games, which ones show evidence that their appeal isn't limited to their current niche?

## The central problem: self-selection
People don't encounter or rate games at random. They choose what to buy, back, play, and rate.
A niche wargame rated 9+ by 100 hardcore fans isn't necessarily a broadly underrated game. Those 100 people may be exactly the people who were most likely to love that kind of game in the first place. There isn't a latent pool of random casual players who would have rated it lower, because many of them were never going to seek it out or play it.
Sample-size shrinkage doesn't solve this. It's a **sampling-frame problem, not just a noise problem**.
This is the central issue this project needs to investigate, and one that conventional "debiasing" approaches can easily miss.
Complexity, playtime, genre, and niche appeal are not automatically biases. They may reflect genuine characteristics of the game and its audience. Only treat something as a bias when there is a concrete reason to believe it is distorting the estimate rather than reflecting real signal.

## Approach
Start simple and add complexity only when the data and evidence justify it.

- Establish what the data actually contains and what can realistically be inferred from it before deciding on a model.
- Use BGG's raw average and Geek Rating as baselines rather than assuming either is correct or incorrect.
- Explicitly investigate self-selection and audience effects, even if the first attempts are necessarily crude.
- Treat the existing friend-provided "debiased" ranking as something to analyse and test, not as ground truth.
- Document what cannot be corrected for instead of hiding uncertainty behind increasingly elaborate formulas.
- Let the data determine which corrections are useful. Don't add a correction simply because it sounds statistically sensible.

## Output
The goal is not to produce a single opaque ranked list.

For each candidate, we should eventually be able to distinguish between:

- an estimate of underlying quality;
- how certain that estimate is;
- how it compares with BGG's observed rating/ranking;
- whether the game appears genuinely underrated;
- whether the evidence points toward broad appeal or primarily a well-loved niche.

The exact output structure can wait until we know what the data can actually support.

## Guiding principle
The objective is not to produce the most complicated or novel ranking.
It is to find out whether the data can support a **defensible answer to the hidden-gem question** at all.

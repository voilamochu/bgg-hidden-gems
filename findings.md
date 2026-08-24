# Findings Log

> **Current-data status (2026-08-23):** The current processed research population is **16,627 games**, after excluding explicit BGG `Admin: Upcoming Releases` and `Admin: Unreleased Games` records. The refreshed downstream results are in the final **population-correction refresh** entry. Numerical entries before that entry were generated on the pre-correction 16,726-game population and are retained as historical provenance; use the refresh entry for current figures.

## 2026-08-23: Final Research Population Definition (Structural PnP & Self-Published Rule)

### Context & Goal
Finalized the research population from `data/raw/bgg_games_current.parquet` (161,404 raw rows, 34 columns) to `data/processed/bgg_research_population.parquet` (**16,726 games**, 36 columns). Applied the non-circular structural PnP / self-published exclusion rule based strictly on physical product metadata (`containers`, `components`, `series`, `magazine`, `crowdfunding`) rather than rating volume or digital app implementations.

### Final Sequential Filtering Waterfall
| Step | Filter Criterion | Records Excluded at Step | Retained Population |
| :--- | :--- | :--- | :--- |
| **0. Raw Dataset** | All records in parquet dump | — | **161,404** |
| **1. Valid `game_id`** | Remove null `game_id` (all expansion parse failures) | 942 | **160,462** |
| **2. Non-Expansions** | Union of URL prefix, flag, and category expansion tags (retaining standalone reimplementations) | 34,491 | **125,971** |
| **3. Published 1950–2026** | Remove year=0, null, BGG meta-entries, pre-1950, and year > 2026 | 13,805 | **112,166** |
| **4. Rating Count Floor** | Require `users_rated >= 100` | 95,214 | **16,952** |
| **5. Latin Script Titles** | Exclude non-Latin scripts (CJK, Cyrillic, Hangul, Kana; foreign Latin titles like *Die Macher* retained) | 36 | **16,916** |
| **6. Structural PnP / Self-Pub Exclusion** | Exclude explicit POD/DTP and true DIY PnP lacking physical commercial product metadata | 190 | **16,726** |
| **Final Research Population** | Modern standalone published commercial games | — | **16,726** |

### Key Population Characteristics
- **Total Games**: **16,726**
- **Year Range**: 1950 to 2026 (Median: 2015, Mean: 2011.6)
- **Users Rated**: Min 100, Median 354, Mean 1,731, Max 143,671
- **Average Rating**: Min 1.27, Median 6.54, Mean 6.46, Max 9.28
- **Bayesian Geek Rating**: Min 4.36, Median 5.67, Mean 5.86, Max 8.49
- **Complexity / Weight**: Min 1.00, Median 2.00, Mean 2.09, Max 4.82 (only 15 missing values; 99.91% complete)
- **Standalone Reimplementations**: 278 retained
- **Commercial Boxed / Wallet Games Retained**: 341 games with promotional PnP tags (*The Resistance*, *Secret Hitler*, *Tiny Epic Galaxies*, *Friday*, *Distilled*, *Sprawlopolis*, *Evolution*, *One Deck Dungeon*, *Burgle Bros.*, *18EU*, *Modern Naval Battles*, *Mystery Rummy*, etc.)

---

## 2026-08-23: Selection Bias Audit of the Research Population

### Context & Goal
Audited the composition of the clean research population (`data/processed/bgg_research_population.parquet`, 16,726 games) against the excluded pool (95,440 modern base games with <100 ratings) and raw dataset to quantify selection effects and structural survival biases across release era, complexity, rating variance, categories, and mechanics.

### Key Empirical Findings

1. **Expansion Removal Eliminates Severe Fan Survivorship Bias [Empirical Finding]**:
   - Expansions (35,433 records) have a mean average rating of **7.39** vs **6.19** for base games (+1.20 rating point premium).
   - Expansions are also heavier (mean weight 2.52 vs 1.87).
   - *Mechanism*: Almost exclusively purchased and rated by existing fans who already enjoyed the base game (extreme positive self-selection). Removing expansions is essential to avoid treating fan enthusiasm for add-ons as standalone game quality.

2. **Temporal / Recency Selection from the 100-Rating Floor [Empirical Finding]**:
   - Survival rate increases monotonically with publication decade:
     - 1950s: **3.02%** (37 / 1,227)
     - 1960s: **5.53%** (116 / 2,099)
     - 1970s: **9.13%** (433 / 4,745)
     - 1980s: **7.95%** (618 / 7,772)
     - 1990s: **11.51%** (1,090 / 9,470)
     - 2000s: **13.07%** (2,754 / 21,068)
     - 2010s: **18.05%** (6,902 / 38,238)
     - 2020s: **16.10%** (4,435 / 27,547)
   - Median release year of the retained population is **2015** (mean 2011.6). Older, obscure games suffer from structural rating scarcity on an internet platform founded in 2000.

3. **Complexity & Weight Shift [Empirical Finding]**:
   - In the excluded pool (<100 ratings), **58.7%** of games completely lack a complexity/weight rating.
   - Where weight is present, retained games are noticeably heavier (mean **2.09**, median **2.00**) than excluded games (mean **1.78**, median **1.78**).
   - BGG's user base actively seeks out and rates heavier hobby games, while lighter casual games are dropped due to rating sparsity.

4. **Extreme Noise in Low-Count Ratings [Observed Fact]**:
   - Excluded games (<100 ratings) have a median rating count of only **3 voters** (75th percentile is 13 voters), resulting in double the rating variance (std dev **1.61** vs **0.82** for retained).
   - The 100-rating floor effectively removes raw measurement noise, but at the cost of excluding genuine niche games.

5. **Category & Mechanic Compositional Shifts [Empirical Finding]**:
   - **Disproportionate Survivors (Euro / Hobbyist Archetypes)**:
     - Categories: *City Building* (41.9%), *Civilization* (39.5%), *Territory Building* (35.6%), *Industry/Manufacturing* (34.6%), *Trains* (32.4%), *Exploration* (31.8%).
     - Mechanics: *Contracts* (61.4%), *End Game Bonuses* (51.6%), *Worker Placement* (44.8%), *Network Building* (40.2%), *Variable Set-up* (39.9%), *Variable Player Powers* (36.5%).
   - **Severe Attrition (Casual / Traditional / Mass-Market Archetypes)**:
     - Categories: *Educational* (4.0%), *Trivia* (4.7%), *Math* (5.4%), *Children's Games* (6.7% out of ~16,000 games), *Sports* (6.9%), *Memory* (7.6%), *Word Games* (8.7%).
     - Mechanics: *Roll / Spin and Move* (5.2% out of 13,594 games), *Measurement Movement* (6.0%), *Acting* (7.9%), *Matching* (8.6%), *Player Judge* (9.1%), *Memory* (11.6%).

6. **Niche Self-Selection Case: Wargames [Empirical Finding]**:
- 14,665 wargames exist in the modern base dataset, but only **2,245 (15.31%)** reach 100 ratings.
  - For wargames as a whole, the 75th percentile of rating count is only 50.
  - The wargames that do reach 100 ratings represent an intensely self-selected hobbyist cohort.

## 2026-08-23: Rating-volume behavior — sampling noise versus selection

### Scope and setup
Ran the existing `scripts/03_rating_volume_behavior.py` on the current processed population (**16,726 games**, all with `users_rated >= 100`). This is a descriptive game-level analysis of the association between rating volume, `avg_rating_current`, and `bayes_rating`; it does not fit a new ranking or debiasing model.

### Main empirical findings

1. **Rating volume is extremely concentrated [Observed Fact]**:
   - Median `users_rated` is **354**, while the mean is **1,705.5**; the raw-count distribution is highly right-skewed.
   - The top 1% of games by volume account for **27.2%** of all ratings in the research population. The bottom half account for only **5.6%**.
   - Consequently, a game-level comparison by rating-volume band is not a comparison of equally represented games or raters. High-volume games dominate the rating mass, while low-volume games dominate the number of titles.

2. **The raw average rises substantially with rating volume [Empirical Finding]**:
   - Pearson correlation of `avg_rating_current` with `log10(users_rated)` is **+0.310** (Spearman **+0.301**).
   - Mean average rating rises monotonically from **6.435** in the 100–199 band to **7.531** in the 25k+ band: a **+1.096-point** difference. The median rises from **6.427** to **7.550**.
   - This is a large practical association, not merely a statistically detectable one. It is not evidence that more ratings mechanically improve a game's rating; volume is entangled with which games accumulate attention and which games survive into the high-volume population.

3. **The within-band distributions do not look like a common-mean sampling-noise funnel [Empirical Finding]**:
   - Cross-game SD of the observed average declines from **0.884** in the 100–199 band to **0.550** in the 25k+ band, but this is far slower than the `1/sqrt(n)` decline expected if games shared approximately the same underlying mean.
   - The change is strongly asymmetric. Relative to 100–199 ratings, the 25k+ band's P10 is **+1.60** rating points, while its P90 is only **+0.59**. The share below 6.0 falls from **30.6%** to **2.4%**.
   - The upper tail is not inflated at low volume: the share with average >= 8.0 is **4.3%** at 100–199 ratings, **4.1%** at 200–499, **3.7%** at 500–999, and **4.2%** at 1k–2.5k. It then rises for the highest-volume bands, reaching **18.9%** at 25k+.
   - Under a simple iid-rating benchmark with individual-rating SD of 1.0–1.6, the expected standard error at the 100–199 band's median count (139) is only **0.085–0.136**, versus observed cross-game SD **0.884**. The benchmark is assumption-dependent because this dump has no per-game rating SD, but the order-of-magnitude gap is decisive: ordinary averaging noise is not the dominant explanation for the band means or their broad spread.

4. **The pattern is consistent with volume/popularity selection and composition, not just measurement noise [Empirical Finding / Interpretation]**:
   - Weight and year explain part of the association: mean weight rises from **1.99** in the lowest band to **2.44** in the highest, and average rating is strongly related to weight (**r = +0.562**) and year (**r = +0.372**).
   - The volume slope remains within weight tertiles. For light / medium / heavy games respectively, the lowest-to-highest band means move from **5.94 → 7.02**, **6.49 → 7.34**, and **7.03 → 7.88**.
   - In a descriptive OLS adjustment for weight and year, the rating-volume coefficient is **+0.308 rating points per tenfold increase in ratings**, compared with **+0.446** before adjustment. The partial correlation is **+0.285**. These are associations, not causal effects; remaining genre, audience, visibility, age, and quality composition are still mixed together.
   - The lower-tail compression is consistent with a popularity/selection process in which poorly received games are less likely to accumulate very large audiences, while high-volume games include both genuinely broadly appealing titles and mass-market titles with only moderate ratings. This should not be mislabeled as pure bias: quality-driven popularity is a real data-generating process as well as a source of selection.

5. **`bayes_rating` is primarily a strong volume-weighted transformation of the raw average [Model-dependent conclusion]**:
   - In this snapshot, its overall Spearman correlation with rating volume is **+0.803**, much higher than the raw-average correlation (**+0.301**), because BGG's Bayesian score explicitly gives more weight to the observed average as `users_rated` increases.
   - Reverse-fitting the observed values gives approximately:
     `bayes_rating = (5.49 * 2500 + users_rated * avg_rating_current) / (2500 + users_rated)` with RMSE **0.025** rating points.
   - At 100 ratings, only **3.8%** of the score is data-weighted and **96.2%** is the 5.49 prior. At 354 ratings, the data weight is **12.4%**; at 2,500 it is **50%**.
   - This produces a useful illustration of what the baseline does: the 100–199 band has raw-average mean **6.435** but Bayes mean **5.54**, with Bayes SD only **0.047**; the 25k+ band has raw-average mean **7.531** and Bayes mean **7.35**, with Bayes SD **0.531**. No game with fewer than 500 ratings and raw average >= 8.0 clears Bayes **6.032** in this population.
   - Therefore Bayes is effective at suppressing unstable-looking low-volume extremes and enforcing a popularity threshold, but it does not identify who is absent from a game's rater pool. It addresses a conservative ranking objective / shrinkage convention, not self-selection into the population being measured.

### Noise, selection, or both?

- **Sampling noise of the mean [Supported conclusion]:** present in principle, especially near the 100-rating floor, but not large enough to explain the approximately 1.1-point between-band mean shift, the persistent within-weight slope, or the asymmetric disappearance of the lower tail. The data do not support treating low-volume averages as mostly random fluctuations around a common quality level.
- **Selection and composition [Supported conclusion]:** clearly present at the game/popularity level. Rating volume is related to weight, era, observed quality, and which games accumulate enough attention to enter the research population. This is the dominant explanation for the cross-band pattern among the mechanisms measurable here.
- **Rater-pool selection [Unidentified hypothesis]:** still possible for individual titles. A low-volume 8.5 average may reflect a niche audience that chose the game because it fits their tastes, but it may also be an early, genuinely broad signal from a game that has not yet reached many people. The current data contain no individual ratings, rater identities, exposure/non-rater data, or rating timestamps, so they cannot distinguish those explanations.

The specific hypothesis that *fan-only inflation dominates all low-volume averages* is not supported by the aggregate pattern: the lowest-volume band has the lowest mean and no excess share of 8.0+ games. That does **not** rule out fan selection for particular games, nor does it prove that high-volume games are unbiased measures of broad appeal.

### Important limitations

- This is a cross-sectional, game-level snapshot. There is no rating history, individual-rating distribution, rater overlap, exposure set, or information about people who played but did not rate.
- The sampling-noise calculation uses assumed individual-rating SD values; they are sensitivity benchmarks, not observed quantities. The conclusion is robust because the observed cross-game spread is much larger than the resulting standard errors, but per-game uncertainty cannot be estimated directly from this dump.
- The >=100-rating research floor and the other population filters are themselves selection mechanisms. Results do not generalize directly to the many genuine niche or newly published games excluded below the floor.
- Weight/year adjustment is intentionally minimal and incomplete. Genre, publisher, marketing, availability, language, edition, audience, and true quality remain confounded with volume.
- BGG's Bayesian formula is treated as a baseline. Reverse-fitting it describes the current `bayes_rating` field; it does not establish that the prior mean or 2,500 pseudo-votes are statistically correct for the research question.
- Band comparisons are descriptive. They do not establish that increasing a game's rating count would cause its average to increase.

### Implications for the next research question

1. **For rating estimation (RQ1):** raw averages at the current floor are not mainly noise-dominated, but low-volume extremes remain uncertain and selection-laden. Keep raw average and BGG Bayes as explicit baselines; do not treat either as a recovered population-wide quality parameter.
2. **For underratedness (RQ2):** the next analysis can ask whether a game's rating is high relative to an explicit expectation conditional on popularity, age, weight, genre, and audience proxies. Any residual should be labeled model-dependent and tested for out-of-sample stability; rating volume should not be used as a simple noise correction.
3. **For hidden gems (RQ3):** this dataset alone cannot establish appeal beyond a niche. A candidate list based only on high raw average and low volume would mostly select an unresolved mixture of genuine quality, niche self-selection, and recent/edition effects. Evidence of broad appeal will require additional observable audience/exposure information or carefully stated external proxies, followed by stability checks.

## 2026-08-23: Rating-volume composition — characteristics do not explain the relationship away

### Scope and setup

Ran the new `scripts/04_rating_volume_composition.py` on the same **16,726-game** research population. It compares composition across the existing rating-volume bands and contrasts low volume (**100–499 ratings**) with high volume (**>=2,500 ratings**) within groups. Categories and mechanics are overlapping tags, so their summaries are descriptive rather than mutually exclusive group comparisons. BGG rank is analyzed as a downstream baseline, not as a control.

### Composition across volume bands

1. **Release year is a weak volume correlate inside the retained population [Observed Fact / Empirical Finding]**:
   - Pearson correlation of year with `log10(users_rated)` is **+0.057** and Spearman correlation is **+0.028**.
   - Median year is **2015** in the 100–199 band, **2016** from 500 through 5k ratings, and **2013** in the 25k+ band. The retained population is therefore not simply a sequence of older games becoming more-rated.
   - The rating-volume contrast persists within major recent cohorts: high minus low average rating is **+0.504** for 2000s games, **+0.459** for 2010s games, and **+0.331** for 2020s games. Older decades have smaller and more selective cells; the 1960s contrast is based on only 69 low-volume and 48 high-volume games.
   - Year composition affects the level of ratings, especially because newer games rate higher in this population, but it does not account for the general positive volume association.

2. **Complexity / weight explains a meaningful part, but not the whole, of the association [Empirical Finding]**:
   - Median weight rises from **1.89** in the 100–199 band to **2.31** in the 25k+ band; the full-population correlation with log volume is **+0.145**.
   - Within light, medium, and heavy weight tertiles, high minus low average rating remains **+0.380**, **+0.351**, and **+0.245** respectively. The higher baseline of heavy games is therefore not sufficient to explain the volume pattern.
   - This confirms and extends the prior weight/year adjustment: a descriptive volume coefficient is about **+0.306 rating points per tenfold increase in ratings** after year and weight, versus **+0.443** with volume alone. Adding playtime, player counts, and reimplementation status changes it only to **+0.315**. The corresponding descriptive R² values are **0.096**, **0.491**, and **0.503**. These are explanatory associations, not a debiasing model or causal decomposition.

3. **Playtime and player count are weak general explanations [Empirical Finding]**:
   - Median playtime moves from **45** minutes in low-volume bands to **60** minutes in the highest bands, but the full-population Pearson correlation with log volume is effectively zero (**−0.027**; Spearman **+0.061**), partly because the field is highly skewed.
   - Within 1–30, 31–60, 61–120, and 121–240 minute bands, high minus low average rating is **+0.378**, **+0.443**, **+0.427**, and **+0.356**. The 241+ group has a smaller contrast (**+0.164**) but only 150 high-volume games and already has a high low-volume mean (**7.399**).
   - Player-count medians are almost unchanged: minimum players stays at 2, and maximum players stays at 4 until 25k+, where it is 5. Correlations with log volume are small for minimum players (**−0.048 Pearson; −0.056 Spearman**) and maximum players (**−0.015; +0.038**).
   - The volume contrast remains positive within minimum-player bands 1, 2, and 3+ (**+0.297**, **+0.404**, and **+0.477**) and within maximum-player bands 1–2, 3–4, 5–6, 7–10, and 11+/open (**+0.217**, **+0.504**, **+0.488**, **+0.339**, and **+0.415**). These fields do not behave like the main source of the overall relationship.

4. **Reimplementation status is strongly associated with volume and deserves separate treatment [Empirical Finding / Interpretation]**:
   - Only **278 games** are marked as reimplementations, but their median rating count is **1,180.5**, versus **349** for other games. Their mean raw rating is **6.80** versus **6.66** for other games.
   - Reimplementations are **0.7%** of the 100–199 band but **14.8%** of the 25k+ band. Within reimplementations, high minus low average rating is **+0.959**, compared with **+0.407** among non-reimplementations.
   - This is consistent with established games, refreshed editions, and recognizable systems receiving an inherited audience or visibility advantage. It is not evidence of broader appeal for every reimplementation, and the subgroup is too heterogeneous and small to identify a common mechanism.

### Broad categories and mechanics

5. **The audience mix changes substantially across volume bands [Empirical Finding]**:
   - Within the 100–199 band versus the 25k+ band, category prevalence changes notably for Wargame (**19.2% → 6.5%**), Children's Game (**8.6% → 0.6%**), Economic (**6.1% → 22.5%**), Fantasy (**12.5% → 20.7%**), Science Fiction (**8.1% → 14.8%**), and Fighting (**7.0% → 13.6%**). Card Game is comparatively stable (**31.5% → 33.7%**).
   - Mechanics show similar composition shifts: Hand Management (**19.7% → 52.1%**), Variable Player Powers (**11.8% → 36.1%**), Solo / Solitaire (**7.2% → 27.8%**), and Worker Placement (**3.0% → 11.2%**) are more prevalent at high volume. Simulation moves in the opposite direction (**11.1% → 3.6%**), while Dice Rolling is relatively stable (**29.0% → 27.8%**).
   - These are population-composition differences, not claims that a mechanic causes popularity. Tags overlap and may be assigned differently across eras and product types.

6. **The volume-rating association persists within most common tags [Empirical Finding]**:
   - Within categories, high minus low average rating is **+0.18** for Wargames, **+0.27** for Children's Games, **+0.42** for Card Games, **+0.48** for Science Fiction, **+0.58** for Economic games, and **+0.72** for Movies / TV / Radio themes.
   - Within mechanics, it is **+0.16** for Simulation, **+0.26** for Dice Rolling, **+0.44** for Hand Management, **+0.45** for Worker Placement, **+0.48** for Tile Placement, and **+0.53** for Set Collection.
   - The smaller Wargame and Miniatures contrasts (**+0.18** and **+0.19**) are important: these groups start with high low-volume averages (**7.10** and **7.19**) and show less additional increase with volume, but they do not reverse the overall pattern. This is compatible with strong niche enthusiasm plus limited expansion of the audience, not proof of broad appeal.

### BGG rank

7. **BGG rank is tightly related to both volume and rating, but is not an independent game characteristic [Observed Fact / Model-dependent interpretation]**:
   - Current rank is available for **16,317 of 16,726 games (97.6%)**. Among ranked games, rank has Pearson **−0.627** and Spearman **−0.804** correlations with log volume; lower numerical rank means more popular. Rank also has Pearson **−0.799** correlation with raw average rating.
   - Within rank bands with adequate cells, high-volume games have *lower* raw averages than low-volume games: **−0.607** points within ranks 10k+, **−0.729** within 5k–10k, and **−0.899** within 2.5k–5k.
   - This reversal is expected from rank combining rating and popularity information: a low-volume game needs a high raw average to occupy the same rank as a high-volume game. It is not evidence that more ratings lower a game's quality. Rank should not be used as a rating proxy or as a control for this investigation; doing so would risk conditioning on an outcome that already contains the volume/rating relationship.

### Overall interpretation

- **Composition effects [Supported conclusion]:** weight, release cohort, reimplementation status, and category/mechanic mix are genuinely associated with rating volume. The high-volume population is not a random cross-section of games; it contains more established/reimplemented, heavier, economic, fantasy, science-fiction, hand-management, worker-placement, and solo titles, and fewer wargame, children's-game, and simulation titles.
- **A general within-group volume association [Supported conclusion]:** the positive relationship between `users_rated` and `avg_rating_current` remains within release decades, weight strata, playtime/player-count bands, and most common categories/mechanics. A small descriptive adjustment absorbs much of the association's variance because weight and year predict ratings, but the volume coefficient remains about two-thirds of its raw size.
- **Selection versus broad appeal [Unidentified mechanism]:** these results support popularity/composition selection as a major part of the pattern, but they do not tell us whether high-volume games are broadly appealing because they are intrinsically accessible, more visible/available, promoted more, older, attached to known systems, or selected by a particular audience. The same within-group pattern can arise from genuine quality-driven popularity, audience reach, or remaining unmeasured selection.

### Data limitations

- This remains a cross-sectional game-level snapshot with no individual ratings, rater identities, exposure/non-rater information, rating timestamps, or per-game rating distributions.
- Several fields contain explicit or likely open-ended values: `playing_time == 0` for **179** games, playtimes above 1,440 minutes for **77**, `min_players == 0` for **4**, `max_players == 0` for **33**, and `max_players > 10` for **517**. The analysis keeps these records but uses unknown/open-ended bands; field semantics may still be imperfect.
- Category and mechanic tags are non-exclusive, unevenly assigned, and correlated with one another. Within-tag contrasts do not isolate causal effects and are not adjusted for all other game characteristics.
- Older-decade and very high-volume subgroup comparisons can be small or structurally selective. The >=100 rating floor already excludes many niche games, and the current clean population cannot recover their missing composition.
- BGG rank is likely constructed from popularity and rating-related information. Its strong association is descriptive and should not be interpreted as an independent validation signal for quality.

### Implications for the hidden-gem question

1. **A low-volume, high-rated candidate cannot be interpreted without audience strata [Implication]:** a high average within Wargames, Miniatures, Simulation, or other niche-heavy groups may be genuine quality for that audience while providing little evidence of appeal outside it.
2. **A high-volume game is not automatically a broad hidden gem [Implication]:** volume is associated with broader platform attention, but it is also associated with reimplementation status, established systems, product visibility, and composition shifts. High volume is evidence of reach, not by itself evidence of universally strong appeal.
3. **For the next hidden-gem analysis [Open direction]:** use these characteristics to define transparent comparison strata or expectations, then ask whether any apparent underrating is stable within those strata. Do not treat category, weight, or BGG rank as a universal penalty, and do not treat the residual from a descriptive model as identified broad appeal.
4. **What remains missing [Limitation]:** a defensible RQ3 result needs evidence about audience reach or cross-audience performance—such as user-level ratings, external sales/play data, or validated audience proxies. The current data can identify composition and popularity patterns, but not whether a niche game's appeal would generalize beyond its existing raters.

## 2026-08-23: RQ2 baseline — expected rating and descriptive underratedness

### Objective and methodology

Built and ran `scripts/05_rq2_expected_rating_baseline.py` on the current research population. The target is `avg_rating_current`; a residual is defined as observed average minus the fitted conditional mean. This is an operational baseline for RQ2, not a final hidden-gem ranking and not an estimate of broad appeal.

The models use one transparent feature at a time and are compared on the same **16,711 complete cases** (15 games lack weight):

- **S0:** `log10(users_rated)` only.
- **S0b:** rating-volume band indicators instead of a linear log-volume term.
- **S1:** S0 plus centered release year and centered complexity/weight.
- **S1b:** volume-band indicators plus release-decade indicators and weight.
- **S2:** S1 plus log-transformed playtime, minimum players, log-transformed maximum players, and reimplementation status.
- **S3, primary descriptive baseline:** S2 plus one-hot indicators for the 28 category tags appearing in at least 500 games.
- **S4, sensitivity:** S3 plus 34 mechanic tags appearing in at least 500 games.
- **S5/S6, functional-form sensitivities:** category / category-plus-mechanic versions using volume bands and release-decade indicators instead of linear log volume and year.

Category and mechanic indicators are overlapping BGG tags. No interactions, hand-built audience score, rank, `bayes_rating`, or other downstream popularity measure is used as a predictor. Five-fold cross-validation uses a fixed seed (**20260823**) to check prediction stability; it is not a claim of temporal generalization.

### Baseline fit and what it absorbs

1. **The simple baseline explains meaningful variation, but not most game-to-game variation [Empirical Finding]**:
   - S0 volume-only has **R² = 0.0965**, RMSE **0.7735**, and a log-volume coefficient of **+0.4462 rating points per tenfold increase in ratings**.
   - S1 adds year and weight: **R² = 0.4911**, RMSE **0.5805**, and the volume coefficient falls to **+0.3078**. This confirms that complexity and release cohort explain a large share of the raw association, while leaving a substantial within-characteristic volume association.
   - S2 adds playtime, player counts, and reimplementation status: **R² = 0.5063**, RMSE **0.5718**, volume coefficient **+0.3174**.
   - S3 adds frequent category tags: **R² = 0.5393**, RMSE **0.5523**, volume coefficient **+0.3593**. The coefficient is not a causal effect and rises relative to S2 because category composition is correlated with both volume and the other predictors.
   - S4 adds frequent mechanics: **R² = 0.5593**, RMSE **0.5402**. The cross-validated RMSE is **0.5425**, close to its in-sample RMSE **0.5402**.
   - The binned-volume/decade specification S5 has cross-validated RMSE **0.5413**, showing a modest fit improvement over S3 (**0.5537**) when nonlinear volume and year differences are allowed.

2. **The S3 coefficients are interpretable conditional associations, not corrections [Model-dependent conclusion]**:
   - In S3, the coefficients are approximately **+0.0255 rating points per release year**, **+0.4036 per weight point**, **+0.0546 per unit of centered log-playtime**, **−0.0711 per additional minimum-player unit**, **−0.0781 per unit of centered log maximum players**, and **+0.0749 for reimplementation status**.
   - These coefficients describe the retained BGG population. They do not say that changing a game's weight, playtime, audience, or reimplementation status would cause its rating to change.

3. **Flexible volume and year controls matter for residual interpretation [Empirical Finding]**:
   - S1b, with volume bands and decade indicators, improves fit to **R² = 0.5192** versus S1's **0.4911**. S5 centers residuals within volume bands and decades by construction.
   - Under the linear-year S3 specification, residual means are strongly positive for the 2020s (**+0.166**) and older decades (1960s **+0.433**, 1970s **+0.247**, 1980s **+0.174**) but negative for the 2000s (**−0.188**) and 2010s (**−0.074**). Under S5, those decade residual means are effectively zero.
   - This is a specification warning: apparent “underrated” eras in S3 are mostly evidence that a single linear year term is too rigid, not a substantive result about those decades.

### What the residual is, relative to raw average and Bayes

4. **The residual is a different estimand from both raw average and BGG Bayes [Model-dependent conclusion]**:
   - In the common sample, raw average correlates **0.550** with `bayes_rating`; Bayes correlates **0.857** with log volume because its shrinkage rule explicitly weights volume.
   - S3 residual correlates **0.679** with raw average but only **0.194** with Bayes and approximately **0.000** with log volume. It therefore retains information about unusually high or low observed ratings after conditioning on the baseline, rather than simply reproducing BGG's popularity-weighted score.
   - S3 expected means range from **6.415** in the 100–199 band to **7.452** in the 25k+ band, while Bayes means range from **5.544** to **7.353**. The descriptive model is estimating the observed average expected for comparable games, not applying BGG's strong low-volume shrinkage.
   - S3 residual SD is **0.552**; the 95th and 99th percentiles are **+0.874** and **+1.317** rating points. A positive residual is therefore a meaningful deviation from this baseline, but it remains an unexplained deviation, not identified latent quality.

5. **Residuals are not just in-sample artifacts [Empirical Finding]**:
   - S3 in-sample and five-fold cross-validated residuals have correlation **0.9997** and nearly identical SD (**0.5524** versus **0.5537**). With this sample size and low-dimensional design, fitting on the full data does not materially change the residual signal.
   - This check addresses random train/test instability only. It does not test future releases, future rating changes, or transportability beyond the retained BGG population.

### Stability across reasonable specifications

6. **Broad residual ordering is moderately to strongly stable, but exact top candidates are not [Empirical Finding]**:
   - Pearson residual correlations are **0.951** between S1 and S3, **0.966** between S2 and S3, **0.978** between S3 and S4, **0.952** between S3 and S5, and **0.937** between S3 and S6.
   - Among the top 1% positive residuals, overlap is **56.1%** for S1 versus S3, **72.2%** for S3 versus S4, **54.6%** for S3 versus S5, and **54.6%** for S3 versus S6. The top 1% is therefore a specification-sensitive candidate set, especially when volume/year functional forms change.
   - The volume-only top 1% overlaps only **12.8%** with the S3 top 1%. A residual based only on rating volume should not be treated as the RQ2 baseline once known composition is included.

7. **Some broad type patterns persist after changing functional form [Empirical Finding]**:
   - Under S3, category residual means are highest for Sports (**+0.375**), Word Game (**+0.162**), and Trains (**+0.136**). Under the more flexible S5, they remain positive for Sports (**+0.333**), Trains (**+0.147**), and Word Game (**+0.126**).
   - Categories with negative S3 residuals such as Political (**−0.131**), Novel-based (**−0.130**), and Video Game Theme (**−0.115**) remain negative under S5 (**−0.134**, **−0.115**, and **−0.111** respectively).
   - Mechanic residuals under S3 are highest for Line of Sight (**+0.247**), Zone of Control (**+0.206**), Scenario / Mission / Campaign (**+0.202**), and Communication Limits (**+0.174**). These are descriptive niche/mechanic patterns, not evidence that those mechanics create broad appeal.
   - Reimplementation has near-zero average residual after being included as a predictor. Its raw volume association is therefore mostly absorbed as a level/composition difference in this baseline, while individual reimplementations can still have large residuals.

8. **The largest positive residuals are a heterogeneous diagnostic set [Observed Fact / Interpretation]**:
   - The top S3 residuals include older games with small rating counts, recent edition/marketing-style products, sports and word-game examples, and repeated entries from the same recognizable game family. Several exceed **+2 rating points** over the fitted expectation.
   - This mixture is exactly why the residual should not yet be called a hidden-gem score. It can identify games whose observed average is unusually high conditional on the chosen characteristics, but the deviation may be niche self-selection, edition/visibility effects, omitted category structure, rating noise, or genuinely high quality.

### Important limitations

- The model estimates the conditional mean of observed BGG averages among games that already passed the >=100-rating and other population filters. It does not estimate the mean rating among all people who might encounter a game.
- Each game receives equal weight even though a 100-rating average is less precisely measured than a 100,000-rating average. The prior rating-volume analysis showed that sampling noise is not the dominant explanation for the cross-band pattern, but it remains relevant to individual residuals.
- The response is bounded and potentially heteroskedastic. Ordinary least squares is being used for transparency, not because its residual assumptions have been established.
- Category and mechanic tags are overlapping, potentially inconsistent, and correlated. The >=500-game threshold is transparent but arbitrary; changing it changes coefficients and residuals.
- No interactions are included. A category may matter differently by volume, year, weight, or audience, and the current baseline deliberately does not attempt to model all such interactions.
- The flexible S5/S6 specifications remove average differences by volume band and decade; they are useful sensitivity checks but should not be treated as automatically superior. They can also make residuals less comparable to the simpler S3 interpretation.
- BGG rank and `bayes_rating` are not independent ground truth. Rank was excluded because it is downstream of popularity/rating, and Bayes was retained only as a baseline comparison.
- No residual, including a stable residual, identifies broad appeal. The game-level data still lack rater identities, exposures, non-raters, rating histories, and cross-audience outcomes.

### Implications for the hidden-gem question

1. **RQ2 now has a usable descriptive definition [Implication]:** “underrated” can mean a game whose observed average is higher than expected for its rating volume, release era, complexity, structural characteristics, and broad BGG tags under a stated specification. This is a conditional anomaly, not a recovered truth.
2. **Residuals should be reported with specification sensitivity [Implication]:** a candidate that is positive under S3, S5, and mechanic sensitivity is more interesting than one that appears only under a volume-only or linear-year specification. Exact top-list membership remains too unstable for a final ranking.
3. **RQ3 is still separate [Implication]:** a large positive residual does not show that appeal extends beyond the current niche. Sports, word games, trains, wargames, and specialized mechanics may produce positive residuals for very different audience-selection reasons.
4. **Next step [Open direction]:** use the residual baseline to inspect a small, transparent set of candidates and test their stability within audience strata. Seek separate evidence of reach or cross-audience performance before calling any residual a hidden gem.

## 2026-08-23: RQ2 residual robustness — stable versus specification-sensitive anomalies

### Scope and method

Ran `scripts/06_rq2_residual_robustness.py`, which reuses the unchanged model variants from `scripts/05_rq2_expected_rating_baseline.py`. No new predictors or model family were introduced. There are **9 named specifications** in the current set: S0/S0b volume-only baselines, S1/S1b core year/weight variants, S2 structural, S3 category, S4 category-plus-mechanics, and S5/S6 binned-volume/decade sensitivities.

For every specification, the top 1% contains **167 games** and the top 5% contains **835 games** of the 16,711-game common sample. The main robustness summaries use the seven adjusted variants (**S1, S1b, S2, S3, S4, S5, S6**). “Stable” means selected in at least **5 of 7** adjusted variants; “sensitive” means selected in at most **1 of 7**. These thresholds are descriptive conventions, not statistical cutoffs.

### Consensus at the top 1% and top 5%

1. **The top 1% is substantially more specification-sensitive than the top 5% [Empirical Finding]**:
   - Mean pairwise Jaccard overlap among adjusted specifications is **53.6%** for the top 1% and **56.7%** for the top 5%. Across all nine variants it is lower: **39.3%** and **46.1%**.
   - The adjusted top-1% union contains **325 games**: **117** are stable (selected in >=5/7) and **99** are sensitive (selected in <=1/7). All seven adjusted variants agree on **78** games; all nine variants, including the two volume-only baselines, agree on **24**.
   - The adjusted top-5% union contains **1,460 games**: **625** are stable and **298** are sensitive. All seven adjusted variants agree on **381** games; all nine agree on **206**.
   - Thus the broad upper residual region is reasonably reproducible, but the extreme top 1% contains a large specification-dependent edge. A single top-residual list would conceal that uncertainty.

2. **Volume-only residuals are a distinct and weakly transferable candidate set [Empirical Finding]**:
   - The top 1% from the volume-only baseline overlaps only **12.8%** with the S3 category baseline, consistent with the earlier finding that composition controls materially change which games look unusual.
   - This is why the robustness set should be based on the adjusted variants, while S0/S0b remain useful reference points rather than votes in favor of a candidate.

### Characteristics of stable versus sensitive candidates

3. **Stable candidates have larger and more consistent positive deviations [Observed Fact / Empirical Finding]**:
   - Within the adjusted top-1% union, stable games have median volume **176** versus **205** for sensitive games, mean raw rating **8.008** versus **7.663**, mean Bayes rating **5.737** versus **5.736**, and mean residual **+1.601** versus **+1.084**.
   - Their average residual range across the seven variants is **0.351** rating points versus **0.518** for sensitive games. Mean residual SD is **0.130** versus **0.183**.
   - Within the adjusted top-5% union, stable games have median volume **210** versus **296**, mean raw rating **7.779** versus **7.410**, mean Bayes rating **5.792** versus **5.830**, mean residual **+1.175** versus **+0.673**, and mean residual range **0.363** versus **0.500**.
   - The nearly identical Bayes values despite different raw averages are important: robust positive residuals are not simply the same as BGG's popularity-weighted score. They are mostly high observed averages among relatively low-volume games, conditional on the descriptive baseline.

4. **Stable candidates are somewhat newer, lighter, and shorter than sensitive candidates [Empirical Finding]**:
   - In the top-1% union, stable games average year **2010.4**, median weight **1.96**, and median playtime **45 minutes**; sensitive games average year **2006.9**, median weight **2.18**, and median playtime **60 minutes**.
   - In the top-5% union, the corresponding values are year **2011.4**, weight **2.06**, playtime **45** for stable games versus year **2009.0**, weight **2.16**, playtime **60** for sensitive games.
   - These are compositional descriptions, not evidence that lighter or newer games are more robustly underrated. Older and heavier games are more exposed to changes between linear and binned/decade specifications.

5. **Residual dispersion is associated more with year and weight than with rating volume within the candidate union [Empirical Finding]**:
   - Among top-5%-union games, residual-dispersion correlations are **−0.394 with year**, **+0.218 with weight**, and **+0.136 with playtime**. Correlation with users_rated is essentially zero (**−0.006**).
   - The oldest decade is especially unstable: 1950s candidates have mean residual range **0.961** across specifications, versus **0.327** for the 1990s and **0.359** for the 2010s. The 1950s cell contains only **19** top-5%-union games, so this is a warning about sparse historical coverage rather than a precise era effect.
   - Volume-band dispersion is not monotonic: the 100–199 group has mean residual SD **0.159**, 2.5k–5k **0.130**, and 25k+ **0.185** based on only three top-5%-union games. This does not support interpreting specification sensitivity as a simple proxy for sampling noise.

### Game-type patterns

6. **Stable and sensitive groups have different audience compositions [Empirical Finding]**:
   - In the adjusted top-1% union, Card Game is more common among stable games (**29.1%**) than sensitive games (**17.2%**), while Wargame is much more common among sensitive games (**37.4%**) than stable games (**7.7%**). Dice Rolling is also more common in the sensitive group (**43.4%** versus **25.6%** stable).
   - In the adjusted top-5% union, stable games are enriched for Card Game (**32.0%** versus **20.5%**), Fantasy (**20.5%** versus **11.4%**), Sports (**8.8%** versus **1.7%**), Hand Management (**23.8%** versus **15.8%**), and Variable Player Powers (**23.0%** versus **15.8%**).
   - Sensitive games are enriched for Wargame (**40.9%** versus **16.2%**), World War II (**17.8%** versus **2.2%**), Simulation (**29.5%** versus **9.9%**), Hexagon Grid (**26.5%** versus **8.8%**), and Dice Rolling (**47.3%** versus **29.8%**).
   - These patterns are consistent with specialized/niche categories being more dependent on how the baseline represents year, volume bands, and correlated mechanics. They do not establish that stable categories have broader appeal.

7. **The stable set still contains clustered or edition-related records [Observed Fact / Limitation]**:
   - The consensus-stable examples include multiple entries from the Monikers family and other recognizable/edition-style records, along with sports and older titles. Repeated related records are not independent evidence of a general phenomenon and can make a type appear more robust than a deduplicated game-family analysis would show.
   - The most specification-sensitive examples include older games such as *Flutter*, *Why*, *Eleusis*, and *Wembley*, but also isolated high-volume or modern records that enter only one variant's top 5%. This illustrates that sensitivity can arise from sparse historical support, functional-form changes, or category/mechanic attribution—not one single failure mode.

### Interpretation and limitations

- **Robust residual [Supported conclusion]:** a game selected across most adjusted specifications is a more reproducible conditional anomaly in this dataset than one selected by only one specification.
- **Not broad appeal [Limitation]:** consensus only means the observed average is unusually high relative to several models of the retained BGG population. It does not address who rated the game, who did not encounter it, or whether its appeal extends outside its existing audience.
- **Not independent evidence [Limitation]:** the variants share the same target, data, tags, and many predictors. Agreement across them is robustness to these specific functional-form and feature-set choices, not replication across independent samples.
- **Threshold dependence [Limitation]:** top 1%, top 5%, >=5/7, and <=1/7 are useful review conventions. Different cutoffs would change the counts and should be disclosed in any future candidate review.
- **Equal game weighting [Limitation]:** a 100-rating mean and a 20,000-rating mean are treated as observations of the same target in the residual calculation. Individual residual uncertainty remains unavailable without rating-level data.

### Implications for the hidden-gem question

1. **RQ2 reporting should separate magnitude from robustness [Implication]:** report residual size, consensus count, and specification dispersion together. “Large residual” and “stable residual” are different properties.
2. **Niche-heavy stable versus sensitive patterns need different interpretation [Implication]:** Wargame/WWII/Simulation candidates are disproportionately specification-sensitive, reinforcing the need to treat positive residuals in niche audiences as unresolved rather than broad-appeal evidence. Stable Card/Fantasy/Sports patterns are more reproducible but still do not identify reach beyond the current rater pool.
3. **Do not move directly to RQ3 ranking [Implication]:** the next hidden-gem step should inspect robust RQ2 anomalies with explicit audience context and independent reach evidence. Residual consensus is a screening aid, not an RQ3 model or final ranking.

## 2026-08-23: Audience proxies for stable RQ2 residual candidates

### Scope and method

Ran `scripts/07_rq2_stable_audience_proxies.py` using the existing seven adjusted RQ2 specifications. Stable means selected in at least **5 of 7** adjusted variants, matching the robustness analysis. The comparison is between stable top-1% (**117 games**) or stable top-5% (**625 games**) and the rest of the 16,711-game complete-case research population.

The analysis deliberately keeps audience proxies separate rather than combining them into an RQ3 score:

- number of BGG category and mechanic tags;
- category/mechanic prevalence;
- transparent combinations such as Wargame + Miniatures, Wargame + tactical mechanics, Party Game + Humor, and Card Game + Hand Management;
- weight, playtime, and player-count distributions.

These are metadata and gameplay-style proxies. They are not measures of actual audience size, user diversity, exposure, or appeal beyond the current rater pool.

### Breadth and format characteristics

1. **Tag-count breadth does not show a consistent stable-candidate pattern [Observed Fact]**:
   - Stable top-1% games average **2.63 category tags** and **3.57 mechanic tags**, versus **2.77** and **3.91** in the rest of the population. Their medians are 3 and 3, identical to the rest.
   - Stable top-5% games average **2.96 category tags** and **4.00 mechanic tags**, versus **2.76** and **3.90** in the rest. Their medians are again 3 and 3.
   - The direction changes between top-1% and top-5%, so the number of tags is not a stable proxy for audience breadth. More tags may instead reflect metadata density, complexity, or how BGG describes a game.

2. **Stable residual candidates are not clearly separated by complexity, playtime, or ordinary player counts [Empirical Finding]**:
   - Stable top-1% median weight is **1.96** versus **2.00** in the rest; stable top-5% median weight is **2.06** versus **2.00**.
   - Median playtime is **45 minutes** for stable top-1% and top-5% candidates, the same as the rest. Stable top-1% games have fewer games above 240 minutes (**0.0%** versus **4.1%**), while top-5% games are virtually identical (**4.0%** versus **4.1%**).
   - Median minimum players is 2 and median maximum players is 4 in both stable sets and their complements. Stable top-1% has a higher share with `max_players > 10` (**18.8%** versus **3.0%**); stable top-5% is also higher (**9.4%** versus **2.8%**). Because these values include open-ended/sentinel-style player counts, this is a data-quality signal rather than evidence of genuinely broad player reach.
   - Overall, the robust residual set is not simply a collection of heavier, longer, or more complex games. Its audience interpretation must come from category/mechanic patterns and external evidence, not format fields alone.

### Category and mechanic patterns

3. **Stable top-1% candidates show a recognizable social/sports pattern, not a uniformly specialist pattern [Empirical Finding]**:
   - Sports appears in **19.7%** of stable top-1% games versus **1.8%** of the rest. Party Game appears in **23.1%** versus **8.8%**, and Humor in **16.2%** versus **5.3%**.
   - Mechanics show similar enrichment for Acting (**12.0%** versus **0.8%**), Storytelling (**9.4%** versus **2.9%**), Team-Based Game (**11.1%** versus **5.5%**), Memory (**8.5%** versus **3.8%**), and Communication Limits (**6.8%** versus **1.4%**).
   - Card Game is slightly underrepresented (**29.1%** versus **32.1%**), as are Children's Game (**4.3%** versus **6.4%**) and Wargame (**7.7%** versus **13.6%**). This stable top-1% pattern is more recognizable as social/party/sports-oriented than as a concentration in specialist wargaming.

4. **Stable top-5% candidates are more heterogeneous [Empirical Finding]**:
   - The stable top-5% is enriched for Sports (**8.8%** versus **1.7%**), Party Game (**14.6%** versus **8.7%**), Miniatures (**10.9%** versus **5.2%**), Fighting (**13.8%** versus **8.5%**), Fantasy (**20.5%** versus **15.3%**), and Humor (**9.0%** versus **5.2%**).
   - Wargame is only modestly higher (**16.2%** versus **13.5%**), while Economic games are lower (**4.0%** versus **8.6%**) and Children's Games lower (**4.5%** versus **6.5%**).
   - Mechanically, Variable Player Powers (**23.0%** versus **16.0%**), Team-Based Game (**10.2%** versus **5.3%**), Cooperative Game (**14.6%** versus **10.7%**), Role Playing (**6.6%** versus **2.8%**), Storytelling (**6.6%** versus **2.8%**), and Scenario / Mission / Campaign (**7.8%** versus **4.1%**) are enriched. Set Collection (**7.4%** versus **16.7%**), Tile Placement (**5.6%** versus **10.5%**), and Area Majority / Influence (**6.7%** versus **9.8%**) are less common.
   - This is a mixture of social, narrative, fantasy, miniature, and tactical patterns rather than one coherent audience class.

### Specialist and broad-audience pattern combinations

5. **The stable top-1% is not concentrated in the clearest specialist-wargame combinations [Empirical Finding]**:
   - Wargame + Miniatures occurs in **4.3%** of stable top-1% games versus **1.9%** of the rest; Fantasy + Miniatures occurs in **5.1%** versus **2.2%**; these are small but recognizable specialist/production-style pockets.
   - In contrast, Wargame + World War II occurs in **0.0%** versus **4.1%**, Wargame + Hexagon Grid in **1.7%** versus **6.4%**, Wargame + Simulation mechanic in **0.9%** versus **7.0%**, and the broader Wargame + tactical-mechanic proxy in **5.1%** versus **9.5%**.
   - Party Game + Humor is much more common in stable top-1% games (**13.7%** versus **2.1%**), while Card Game + Hand Management is less common (**12.0%** versus **15.8%**). These are descriptive contrasts, not validated measures of broad appeal.

6. **The stable top-5% contains both social/broad-looking and specialist-looking patterns [Empirical Finding / Interpretation]**:
   - Party Game + Humor appears in **6.9%** of stable top-5% games versus **2.0%** of the rest. Card Game alone is essentially identical (**32.0%** versus **32.1%**), and Card Game + Hand Management is modestly higher (**17.3%** versus **15.7%**).
   - Wargame + Miniatures is notably enriched (**5.3%** versus **1.8%**), as is Fantasy + Miniatures (**5.1%** versus **2.1%**). Wargame + tactical mechanics is modestly higher (**11.7%** versus **9.4%**), while Wargame + World War II is lower (**2.2%** versus **4.1%**).
   - Campaign/RPG specialist is present at **1.6%** versus **0.9%**, while Children's Game + Memory is rare (**0.5%** versus **0.8%**). No single combination dominates the stable set.

### Overall audience-proxy interpretation

- **Systematic narrow-audience concentration [Not supported by these proxies]:** stable residual candidates are not uniformly heavier, longer, more complex, or dominated by wargame/tactical combinations. Stable top-1% candidates lean toward Party/Humor/Sports and stable top-5% candidates are mixed.
- **Recognizable specialist pockets [Supported descriptive finding]:** Miniatures/Fantasy and Wargame/Miniatures patterns are enriched, especially in the stable top-5%, and some narrative/tactical mechanics are more common. These pockets show that robust residuals can include well-loved specialist games.
- **Recognizable broad-audience-looking pockets [Supported descriptive finding, not broad appeal]:** Party Game, Humor, Acting, Storytelling, Team-Based, and Sports tags are enriched in stable candidates. These look more socially accessible in ordinary game-description terms, but the current data cannot establish that their appeal extends beyond their existing BGG audience.
- **No single breadth interpretation [Supported conclusion]:** the stable set combines social/party, sports, fantasy, miniatures, narrative, and tactical profiles. A residual that is robust across rating models does not imply a common audience breadth mechanism.

### Limitations

- BGG category and mechanic tags are overlapping metadata, not observed audience segments. A tag count does not measure how many kinds of people like a game.
- The “broad-looking” and “specialist” combinations are transparent hypotheses chosen from known tags, not validated audience classifications. Party games can be niche; card games can be hobbyist; wargames can vary widely in accessibility.
- The stable candidate sets are selected using residuals from the same population being compared. This is a robustness-conditioned comparison, not an independent test of audience composition.
- Stable top-1% cells are small. Percentages such as 0.0%, 4.3%, or 19.7% can change materially with a few games; related editions/families can also cluster.
- `max_players > 10` is contaminated by open-ended or sentinel values, and playtime/player fields have the data-quality issues documented earlier. These should not be interpreted literally as reach.
- The analysis has no user-level ratings, rater identities, exposure/non-rater data, sales, play counts, or cross-audience outcomes. It cannot measure actual breadth of appeal.

### Implications for defining broad appeal

1. **Broad appeal should remain a separate estimand from RQ2 residual size [Implication]:** robustly high residuals identify reproducible conditional anomalies, not audience breadth.
2. **Use audience proxies as a descriptive profile, not a penalty or score [Implication]:** a future candidate review should report category/mechanic patterns, format characteristics, and specialist combinations alongside the residual, without collapsing them into an “appeal breadth” number.
3. **Require evidence beyond BGG tags for RQ3 [Open direction]:** defining broad appeal will require an exposure or cross-audience proxy that can distinguish “many types of people encountered and liked it” from “a narrow group rated it very highly.”
4. **Do not create the RQ3 ranking yet [Implication]:** the current evidence supports stratifying robust RQ2 anomalies into descriptive audience profiles, but not ordering them by hidden-gem status.

## 2026-08-23: RQ3 identifiability audit — no independent cross-audience outcome

### Scope and method

Ran `scripts/08_rq3_identifiability_audit.py` over the 16,726-game processed research population and the 16,711-game complete-case population used by the RQ2 robustness work. The audit classified all 36 processed fields by provenance, compared current fields with legacy `dump_*` fields, and checked whether `families` contains any exposure or recognition metadata that could serve as an independent audience outcome. The stable top-1% and top-5% RQ2 residual sets were used only for descriptive comparison; no broad-appeal score or new model was created.

### What the fields can and cannot establish

1. **The dataset contains no direct cross-audience outcome [Observed Fact / Supported Conclusion]:** there are no rater identities or audience segments, ratings by country/language/market, counts of people exposed but not rating, plays, ownership, sales, external traffic, or independent audience-level outcomes. `attrs_fetched_at` is a single row-fetch timestamp, not a repeated rating panel. Therefore the dataset does not observe whether a game's appeal extends beyond the people who selected it and rated it on BGG.

2. **`users_rated` is platform participation, not audience breadth [Observed Fact / Interpretation]:** it measures the number of BGG users who supplied ratings and is already an RQ2 predictor. It can describe the size of the observed BGG rating population, but cannot distinguish many kinds of raters from many raters in one niche. The central self-selection problem remains: a small, homogeneous group and a large, heterogeneous group can produce the same game-level count.

3. **The rating and ranking fields are not independent evidence [Observed Fact]:** the paired current/legacy fields are very highly correlated:
   - `users_rated` versus `dump_voters`: **n=16,634, r=0.995**, with median current-minus-legacy difference **+24**;
   - `avg_rating_current` versus `dump_avg_rating`: **r=0.975**;
   - `bayes_rating` versus `dump_geek_rating`: **r=0.983**;
   - `rank_current` versus `dump_rank`: **r=0.988**.
   These appear to be current/legacy or snapshot copies of the same BGG processes, not independent populations. Even if the voter-count difference reflects change over time, it provides within-BGG participation change without identifying who newly rated the game or whether appeal crossed an audience boundary. `avg_rating_current`, `bayes_rating`, `rank_current`, `subranks`, and the legacy copies are therefore downstream rating/popularity measures, not RQ3 outcomes.

4. **RQ2 inputs and descriptive tags provide context, not independent reach [Supported Conclusion]:** release year, complexity, playtime, player count, reimplementation status, categories, mechanics, designers, descriptions, and family links describe the product or its metadata. Categories/mechanics and the structural fields were already used in the expected-rating specifications, so using them to explain RQ2 residuals cannot independently validate RQ3. `best_players` and `good_players` are BGG user-preference metadata, not observations of distinct audiences. Missingness is also material: `description` is present for **70.5%**, `best_players` for **94.8%**, and `subranks` for **64.3%** of the research population.

### Plausible exposure and recognition metadata

5. **Family tags contain opportunity/recognition clues but no audience response [Observed Fact / Interpretation]:** in the common RQ2 population, **20.4%** of games have some digital-implementation family tag, **20.0%** have a Kickstarter tag, **1.8%** have a Watch It Played tutorial tag, **0.6%** have a BGG or Dice Tower Hall of Fame tag, **18.4%** have a `Game:` family link, and **21.9%** have a `Series:` link. These flags may indicate availability, promotion, franchise context, or recognition, but they do not record how many people from different audiences encountered or liked the game.

6. **The stable residual sets do not turn these tags into independent evidence [Empirical Finding]:** compared with the full common population, stable top-1% candidates had digital tags in **6.8%**, Kickstarter in **28.2%**, and `Game:` links in **31.6%**; stable top-5% candidates had **10.7%**, **26.7%**, and **35.5%**, respectively. Tutorial and Hall of Fame tags remained sparse (top-5% **1.0%** and **0.2%**). These differences are descriptive selection patterns among RQ2 residual candidates, not evidence of cross-audience appeal. In particular, Kickstarter or a digital implementation may create exposure opportunities, while the dataset lacks the downstream exposure and response needed to establish reach.

### Identifiability conclusion

7. **RQ3 is not identified by the available game-level dataset [Supported Conclusion]:** the strongest available outcomes (`users_rated`, raw average, Bayesian rating, rank, and legacy copies) all describe or derive from the same self-selected BGG rating ecosystem. The remaining fields are product descriptors, taxonomy, relationships, metadata, or possible exposure opportunities without audience-level outcomes. No field supplies an independent comparison between a game's existing niche and other audiences.

8. **Stable RQ2 residuals therefore cannot be promoted to hidden-gem evidence [Model-Dependent Conclusion]:** robustness across expected-rating specifications supports the narrower claim that a game is a reproducible positive anomaly conditional on the modeled variables. It does not support the claim that the game is broadly appealing, that its raters are diverse, or that it would perform similarly among people who have not selected it. The earlier social/party-looking versus specialist-looking tag patterns remain descriptive hypotheses, not validation of RQ3.

### Limitations and implications

- The provenance of some legacy `dump_*` fields is not fully documented, so their exact timing is uncertain. Their strong correlations nevertheless make them unsuitable as independent audience evidence; a second BGG snapshot is still the same platform and selection process.
- Family tags are overlapping, unevenly populated, and potentially influenced by community/editorial activity. Their presence may be downstream of popularity or promotion and cannot be interpreted as exposure volume or audience diversity.
- Stable top-1% and top-5% groups are selected from the same rating outcomes used to define the residuals. Comparing their metadata with the rest is not an independent validation sample.
- The audit establishes non-identifiability from the present fields; it does not prove that no external data could answer RQ3. It identifies the missing measurement: an exposure denominator and/or audience-stratified outcomes independent of the BGG rating target.

**Implication for the next research question [Implication]:** stop treating RQ3 as a ranking problem within this dataset. If the project continues, the next step should be a data-acquisition/measurement design for independent reach evidence (for example, audience-stratified engagement or exposure data), while retaining robust RQ2 residuals only as candidate-screening context. Without such data, the defensible conclusion is “underratedness may be partially describable, but hidden-gem breadth is not identifiable here.”

## 2026-08-23: Audit of the friend-provided debiased ranking

### Scope and data availability

Ran `scripts/09_friend_ranking_audit.py` against both `data/raw/bgg_games_current.parquet` and the processed research population. The audit is limited to game-level observations. It does **not** attempt to validate the friend's user-level debiasing methodology, because the repository contains no user-rating matrix, rater identities, rating timestamps, or other inputs needed for that exercise.

1. **At the time of this audit, the friend output was not present in the BGG parquet data [Historical observed fact / Blocker]:** neither the raw BGG parquet nor the processed research population contained a `debiased_rating` field or any field with a debias/friend label. The raw parquet had **34 columns** and the processed research population had **36 columns**; the available `dump_*` columns were `dump_rank`, `dump_geek_rating`, `dump_avg_rating`, `dump_voters`, and `dump_year`. `dump_geek_rating` was treated as a legacy BGG field, not substituted for the missing friend result.

   Consequently, the parquet-only dataset could not then answer which games the friend’s result promoted or demoted, how the correction differed from `avg_rating_current` or `bayes_rating`, or whether the correction varied by volume, year, complexity, category, or mechanic. Those comparisons require the friend’s game-level output matched by `game_id`.

### Do the `dump_*` fields support a temporal comparison?

2. **The current scrape has a timestamp, but the dump does not [Observed Fact]:** `attrs_fetched_at` ranges from **2026-08-12 03:28:48 UTC to 2026-08-12 12:02:25 UTC** in the raw file, with **160,167 unique timestamps**. There is no collection date, timestamp, or provenance field for the `dump_*` values. The dump may be an earlier/legacy snapshot, but its date and exact construction are not established.

3. **Voter counts are strongly consistent with an earlier BGG snapshot [Empirical Finding / Qualified Interpretation]:** in the 16,634-game research-population overlap, current `users_rated` and `dump_voters` have correlation **0.995**. Current counts exceed dump counts for **96.3%** of games, with median difference **+24**; the 10th and 90th percentiles are **+3** and **+365**. The direction is especially clear at higher current volumes: median differences are **+7** for games with 100–199 current ratings, **+210.5** for 2.5k–5k, and **+2,591** for 25k+; current counts are higher for **100.0%** of the 5k+ groups. This is strong evidence that `dump_voters` is a prior or legacy count for much of the retained population, but it is not proof without a dump timestamp.

4. **Other paired fields changed in both directions [Observed Fact]:** current average rating is below `dump_avg_rating` for **67.4%** of the overlap, with median current-minus-dump change **−0.0123**; current Bayesian rating is below `dump_geek_rating` for **60.9%**, with median change **−0.0022**. Current numeric rank is higher than `dump_rank` for **86.6%** (a worse rank number), with median change **+631**. These changes are compatible with a later BGG snapshot, but they are ordinary same-platform rating/popularity changes, not an independent evaluation.

5. **Release year is not useful temporal evidence [Observed Fact]:** `year` and `dump_year` agree for **98.8%** of paired research-population records. The remaining differences include implausible large discrepancies (minimum **−27**, maximum **+962** years), indicating parsing, missing-value, or record-quality problems rather than a meaningful release-time series.

6. **The comparison is descriptive, not a leakage-safe temporal validation [Limitation]:** without the dump date and a defined cutoff, we cannot establish that every dump value predates every current value or that the fields were computed from disjoint information. Even if the dump is earlier, it is still the same BGG platform and overlapping selection process. It can show within-platform change in counts or ratings, but not out-of-time generalization, independent audience reach, or causal effect of a correction. Treating `dump_*` as a pre-treatment predictor or validation target would be unsafe until provenance and collection dates are supplied.

### What can be said about the friend's correction?

7. **At the time of this audit, no promoted/demoted games or game-type pattern was identifiable [Historical supported conclusion]:** because `debiased_rating` was absent from the BGG parquet data, there was no observed correction to calculate as `debiased_rating - avg_rating_current` or `debiased_rating - bayes_rating`. Any list of promoted or demoted games, or any claim that the correction favors low-volume, older, complex, reimplemented, card, party, wargame, or other types, would have required inventing an output or incorrectly relabeling `dump_geek_rating`.

8. **`dump_geek_rating` cannot stand in for the friend's score [Supported Conclusion]:** it is highly correlated with current `bayes_rating` (**r=0.983**, n=16,280) and is explicitly named as a legacy Geek Rating field. That makes it useful for the snapshot audit above, but not evidence about a separate debiasing rule. The available data can describe BGG's own current-versus-legacy changes; it cannot characterize the friend's ranking behavior.

### Limitations and implications for a richer dataset

- The exact origin, date, and calculation context of all `dump_*` fields are undocumented. Their value differences support a provisional “earlier/legacy snapshot” interpretation, not a verified temporal panel.
- The processed population has already applied filters and a 100-rating floor. Snapshot changes and field availability may differ outside that population; raw-file comparisons also contain malformed or extreme paired differences.
- Game-level aggregates cannot reveal whether a rating-count increase came from new audiences, existing hobbyist audiences, duplicate accounts, or changes in BGG participation. No user-level debiasing claim is tested here.
- To analyze the friend result later, retain a versioned table keyed by `game_id` containing `debiased_rating`, computation date, method/version metadata, universe and missing-value rules, plus the current and historical BGG fields used for comparison.
- To evaluate the underlying method in a later richer dataset, preserve pseudonymous user-game ratings, rating timestamps, user history/participation context, and—if the hidden-gem question remains in scope—independent exposure or audience-segment information. Those data would enable a separate methodology audit; they are not available now.

**Implication [Historical status]:** at the time of this prior audit, the friend output was available for a separate game-level comparison but had not yet been analyzed. That audit remains limited to a provisional review of the likely legacy BGG snapshot. Do not interpret `dump_geek_rating` as debiased, and do not use current-versus-dump differences as validation of the friend's method.

## 2026-08-23: Friend debiased-ratings artifact available for future analysis

**[Historical observed data-status update]** The file `data/raw/complete_2025_bgg_debiased_ranks.csv` was newly present at that point. It contains **24,695 rows and 26 columns**, including unique non-null `game_id` and non-null `debiased_rating` fields. That update recorded artifact availability and schema only; the subsequent comparison is recorded below.

## 2026-08-23: Game-level comparison of the friend debiased rating

### Method and coverage

**[Observed data / Method]** `scripts/10_friend_debiased_comparison.py` compares the supplied `debiased_rating` output with the processed research population by exact `game_id`. It reuses the existing RQ2 specifications and stable-candidate convention from scripts 05–06; it does not reconstruct or modify the friend's method and does not create a new ranking. The comparison uses the direct population overlap for coverage and correction summaries, and the RQ2 complete-case subset for residual comparisons.

- The friend file has **24,695 rows and 26 columns**. The research population has **16,726 rows and 36 columns**.
- There are **16,144 unique game IDs in common**: this covers **96.5%** of the research population and **65.4%** of the friend file. There are **582 research-population games** and **8,551 friend-file games** outside the direct overlap. This is a universe difference, not evidence that either file is wrong.
- `debiased_rating`, `debiased_rank`, `avg_rating`, and `voters` are complete in the friend file. `geek_rating` is missing for 5 rows, `bgg_rank` for 513 rows, `weight` for 5,062 rows, and `kickstarted` for 4,783 rows. The friend file therefore has a usable score for all matched games, but not complete coverage for every characteristic comparison.
- The residual comparison has **16,129 matched complete cases**, excluding 15 direct-overlap games because the existing RQ2 inputs are incomplete. The RQ2 residuals are therefore not being recomputed on a changed population.

### Relationship to current BGG fields

**[Empirical finding]** The friend score is very close to the current raw average in the matched research population: Pearson and Spearman correlations are both approximately **0.982**. Its relationship with current Bayesian rating is weaker by Pearson (**0.587**) but stronger by Spearman (**0.772**), reflecting the different scale and shrinkage behavior of `bayes_rating`. The friend score has correlations of **0.635** with the RQ2 category-adjusted residual and **0.653** with the mean residual across the existing adjusted specifications. It is not independent of the rating information already used in the simpler baselines.

The direct paired source fields also indicate that the friend file is not simply a copy of the current snapshot:

- Friend `avg_rating` versus current `avg_rating_current`: Pearson **0.996**, median friend-minus-current difference **+0.012**; the friend value is higher in **67.3%** of pairs.
- Friend `geek_rating` versus current `bayes_rating`: Pearson **0.987**, median difference **+0.002**; the friend value is higher in **61.3%** of pairs.
- Friend `voters` versus current `users_rated`: Pearson **0.995**, with a median friend-minus-current difference of **−23**; the friend count is higher in only **1.9%** of pairs.

These are snapshot/field comparisons, not validation of the friend's inputs or calculation.

### Size and direction of the correction

Define the observed corrections as `debiased_rating - avg_rating_current` and `debiased_rating - bayes_rating`.

**[Empirical finding]** Relative to the current raw average, the correction is modest on average but nontrivial for individual games: mean **+0.020**, median **+0.024**, standard deviation **0.152**, 1st–99th percentile range **−0.385 to +0.436**, with **57.9% positive** and **42.1% negative** corrections. Thus the supplied output generally moves scores upward slightly while making substantial two-sided changes for a minority of games; the data do not establish why.

Relative to `bayes_rating`, the friend score is higher for **92.1%** of matched games, with mean difference **+0.861** and median **+0.841**. This is expected to be strongly affected by the Bayesian baseline's shrinkage of low-volume games toward its prior. It should not be described as evidence that the friend method is broadly more favorable or more accurate.

### Dependence on rating volume and game characteristics

**[Empirical finding / Descriptive only]** The raw-average correction has a modest positive monotonic association with log rating volume (Spearman **+0.158**), but it is not monotonic across the observed bands. The mean correction is **−0.004** for 100–199 ratings, rises to **+0.056 to +0.059** for 2,500–10,000 ratings, and returns to approximately zero (**+0.003**) for 25,000 or more ratings. The share of positive corrections follows a similar pattern, from **50.2%** at 100–199 ratings to **76.3%** at 5,000–10,000 and **50.9%** at 25,000+. This is consistent with a volume-dependent adjustment, but the game-level output cannot identify whether it reflects measurement-noise correction, selection correction, composition, snapshot mismatch, or some combination.

The correction relative to Bayes is negatively associated with log volume (Spearman **−0.088**) and is largest in low-volume bands, which is primarily the expected consequence of comparing against a strongly shrunk baseline. Other descriptive associations for the raw correction are small: Spearman correlations are **+0.070** with complexity, **+0.008** with playtime, **+0.121** with minimum players, **+0.043** with maximum players, **+0.039** with release year, and **+0.009** with reimplementation status. These are associations in the supplied output, not evidence of causal rules or broad appeal.

Raw corrections are somewhat larger for heavier games: the mean rises from **+0.015** at weight ≤1.5 to **+0.053** at weight ≥3.5. By release decade, the correction is mixed and small (mean **−0.007** in the 1980s versus **+0.036** in the 1990s and **+0.027** in the 2020s). Tag-level contrasts are more pronounced but composition-sensitive: among tags with at least 100 matched games, Trains (**+0.209**), Transportation (**+0.151**), Industry/Manufacturing (**+0.110**), and Economic (**+0.109**) have the largest mean raw corrections, while Miniatures (**−0.109**), Zombies (**−0.098**), Movies/TV/Radio (**−0.074**), and Adventure (**−0.056**) are among the most negative. These tag results should be treated as descriptive contrasts because tags overlap and correlate with age, volume, edition structure, and audience.

### Largest observed movers

**[Observed examples, diagnostic rather than recommendations]** The largest positive changes versus current raw average include *TseuQuesT* (**+2.143**), *Alien: USCSS Nostromo* (**+1.500**), *6: Siege – The Board Game* (**+1.189**), *Propuh* (**+1.169**), and *Cairo Corridor* (**+0.954**). The largest negative changes include *The Fantasy Trip: Legacy Edition* (**−1.524**), *AFU: Armed Forces of Ukraine* (**−1.523**), *Evil Upheaval* (**−1.215**), *The Supershow* (**−1.000**), and *Zoomaka* (**−0.991**). These extremes include low-volume games and very high or very low raw averages, so they do not by themselves reveal a general debiasing principle.

The largest positive changes versus Bayes are concentrated among high-average, low-volume games—for example *On to Richmond II: The Union Strikes South* (**+3.416**), *Monikers: Monikers-er* (**+3.099**), and *Axis Empires: Ultimate Edition* (**+3.068**). The largest negative changes include *Global Survival* (**−2.931**), *Wonders of The First CCG* (**−2.903**), and *Alien: USCSS Nostromo* (**−2.491**). This again illustrates the baseline difference more directly than it validates either score.

### Comparison with RQ2 residual candidates

**[Empirical finding]** The friend top set overlaps most with raw-average leaders and much less with the existing RQ2 residual leaders:

- In the matched **top 1%** (161 games), friend versus current-average overlap is **110/161** with Jaccard **51.9%**; versus Bayes it is **32/161** (**11.0%** Jaccard); versus the existing category-adjusted residual it is **18/161** (**5.9%** Jaccard).
- The friend top 1% contains **13 of the 99 matched stable RQ2 top-1% candidates** (**13.1% of the stable set**; **8.1% of the friend set**).
- In the matched **top 5%** (806 games), friend versus current-average overlap is **645/806** with Jaccard **66.7%**; versus Bayes it is **229/806** (**16.6%** Jaccard); versus the category-adjusted residual it is **222/806** (**16.0%** Jaccard).
- The friend top 5% contains **181 of the 559 matched stable RQ2 top-5% candidates** (**32.4% of the stable set**; **22.5% of the friend set**).

**[Supported conclusion]** The friend's output supplies a distinct ordering and does not reduce to the existing Bayesian rating or RQ2 residual. At the same time, its very high agreement with raw average and the absence of an independent outcome mean that this dataset cannot establish that the distinct ordering adds useful signal, corrects selection into the BGG rater population, or identifies hidden gems. The overlap results are descriptive stability/relationship evidence only, not predictive validation.

### What this dataset can and cannot establish

- **Can establish [supported]:** the exact overlap and schema differences; how the supplied score numerically differs from current raw and Bayesian baselines; how those differences vary descriptively with volume and recorded game characteristics; the identity of extreme movers; and how the friend's top sets overlap with existing RQ2 candidates.
- **Cannot establish [limitation]:** whether the friend score corrects random rating noise, selection into the observed BGG rater pool, rating-scale drift, or some combination; whether its corrections improve estimates of underlying quality; whether promoted games appeal beyond their existing niche; or whether its top candidates are more likely to be hidden gems. Those questions require the underlying user-level ratings, rater and rating-time context, the friend's method/provenance, and ideally an independent outcome or exposure measure.
- The friend file's different universe, likely snapshot mismatch, missing characteristic fields, overlapping game tags, and the existing 100-rating research floor all limit interpretation. No temporal validation or user-level methodology audit was attempted.

**Implication [Next question]:** treat `debiased_rating` as an additional observed baseline/hypothesis for later comparison, not as validated debiasing. A richer dataset should first document the method and timing, then test whether its game-level corrections predict held-out or independent user-level evidence and whether they address selection rather than only measurement noise.

## 2026-08-23: Provisional RQ2 candidate report generated

**[Reporting decision]** Created `docs/rq2_candidate_report.md` as a candidate-screening artifact, using the unchanged RQ2 robustness convention rather than raw residual rank alone. The report reuses the seven adjusted specifications (S1, S1b, S2, S3, S4, S5, S6) on the existing **16,711-game** complete-case population. Each specification contributes its top **1% (167 games)**; “stable” remains selection in at least **5/7** specifications. The 25 reported records are the stable candidates with the largest mean residual across those seven specifications. All 25 selected records happen to be present in **7/7** top sets.

The report presents the primary S3 expected rating and residual, the seven-specification mean and dispersion, rating count, Bayes rating, friend `debiased_rating` where matched, complexity, playtime, player count, and concise category/mechanic profiles. It is explicitly labeled provisional: residual stability is not independent validation, related editions/family records are not independent discoveries, and no candidate can be called a hidden gem or broad-appeal game from this dataset.

## 2026-08-23: Explicit unreleased/pre-release records removed from the research population

### Audit and rule

**[Observed data / Population issue]** The prior cleaning pipeline treated `year` in the allowed range as sufficient publication evidence, but the BGG `families` metadata contains explicit administrative status tags that identify records still treated as upcoming or unreleased. In the old **16,726-game** processed population, there were **99 such records**: **98** with `Admin: Upcoming Releases` and **1** with `Admin: Unreleased Games`. **Legacy of Eastbrook Hills** (`game_id=422742`, year 2026, 114 ratings) is one of the upcoming records and was incorrectly eligible for the prior research population.

The strongest available status evidence is an exact, case-insensitive match on these two BGG administrative family tags:

- `Admin: Upcoming Releases`
- `Admin: Unreleased Games`

The cleaning rule now excludes a record when either exact tag is present, before the rating-count floor. It does not use title words, a 2025/2026 year alone, rating count, or the presence of crowdfunding/campaign metadata as release-status heuristics. The raw scrape was fetched in August 2026, but it has no field for an exact public-release date.

### Crowdfunding and campaign ambiguity

**[Observed fact / Limitation]** Crowdfunding history is not equivalent to current unreleased status in this dataset. After the new filter, **3,639** retained games still carry a `Crowdfunding:` family tag (including Kickstarter and Gamefound), and **254** carry the `Mechanism: Campaign Games` tag. These tags describe funding or gameplay history and are retained unless an explicit administrative unreleased tag is also present. No distinct `preorder` or `pre-order` family status field was found. This preserves released crowdfunded games while excluding records that BGG explicitly marks as upcoming/unreleased.

The rule remains conservative and imperfect: an administrative tag could be stale, and the game-level dump has no independently verified retail/general-release date, campaign-completion field, or public-availability history. Some upcoming-tagged records have older nominal years or substantial ratings, which could reflect early/crowdfunding ratings or stale metadata. Those cases are documented as ambiguity rather than resolved with title heuristics.

### Resulting population change

**[Observed result]** Running the updated `scripts/01_clean_population.py` removes exactly **99** records from the prior population and produces **16,627 games**. The sequential waterfall changes as follows:

- Publication/status step: **112,166 → 107,246** after excluding explicit unreleased statuses along with the existing year/meta filters.
- Rating-floor step: **16,952 → 16,851**.
- Latin-script step: **16,916 → 16,815**.
- Final structural-filtered population: **16,726 → 16,627**.
- The regenerated population contains **zero** records with either explicit administrative unreleased tag.

No other filter, model, or RQ2 methodology was changed. The existing RQ1/RQ2/friend analyses and reports that quote the former 16,726-game population are historical outputs from the pre-status-cleaning population and should be rerun before being treated as current results. The provisional RQ2 candidate report was regenerated with the unchanged selection rule so that explicitly unreleased records are not presented as current candidates.

**[Observed downstream update]** After regeneration, `docs/rq2_candidate_report.md` uses **16,612** complete cases and a top-1% threshold of **166 games**. Legacy of Eastbrook Hills is absent. The report's selection rule and interpretation remain unchanged; the numerical candidate list is now aligned with the cleaned population.

## 2026-08-23: Population-correction refresh of downstream analyses

### Scope

**[Refresh decision]** Reran the existing `scripts/03_rating_volume_behavior.py`, `04_rating_volume_composition.py`, `05_rq2_expected_rating_baseline.py`, `06_rq2_residual_robustness.py`, `07_rq2_stable_audience_proxies.py`, `08_rq3_identifiability_audit.py`, `09_friend_ranking_audit.py`, `10_friend_debiased_comparison.py`, and `11_rq2_candidate_report.py` against the corrected processed population. No predictors, model specifications, stability thresholds, audience proxies, or comparison definitions were changed. This entry supersedes the pre-correction numerical results above for current use.

### Current population and RQ1 rating-volume results

**[Observed fact]** The processed population has **16,627 games** and the RQ2 complete-case population has **16,612 games** (15 missing weight values). The current population's median rating count is **357** and mean is **1,714.5**. The top 1% of games by rating volume accounts for **27.1%** of all ratings; the bottom half accounts for **5.6%**.

**[Refreshed empirical findings]** Mean raw rating still rises from **6.424** in the 100–199 band to **7.531** in the 25k+ band, a **+1.107-point** shift. Cross-game rating SD falls from **0.878** to **0.550**, while the lower tail moves much more than the upper tail: the 25k+ versus 100–199 P10 shift is **+1.60**, compared with **+0.61** at P90. The share below 6.0 falls from **30.9%** to **2.4%**, while the share at least 8.0 rises from **4.1%** to **18.9%**. These figures continue to support the existing conclusion that sampling noise alone does not explain the volume pattern.

- Pearson/Spearman association of raw average with log rating volume is **+0.316/+0.308**; the corresponding Bayes-volume associations are **+0.857/+0.805**.
- The descriptive raw-average volume coefficient is **+0.453** rating points per tenfold increase in ratings; after weight and year adjustment it is **+0.311**, with partial correlation **+0.288** and R² **0.492**.
- The fitted BGG Bayes relationship remains approximately a **5.49 prior mean with 2,500 pseudo-votes** (fit RMSE **0.0248**). This remains a volume-weighted baseline, not a user-population quality estimate.
- The composition refresh preserves the within-group volume pattern. For low volume (100–499) versus high volume (≥2,500), the raw-rating contrast is **+0.382** for light games, **+0.355** for medium games, and **+0.256** for heavy games; it is also positive in most release-decade, playtime, player-count, category, and mechanic strata.

**[Current supported conclusion]** The release-status correction removes pre-release records but does not change the RQ1 interpretation: rating volume remains entangled with popularity, composition, and selection, not just averaging noise.

### Current RQ2 expected-rating and residual robustness results

**[Refreshed model output]** The unchanged nine specifications now fit 16,612 games. The primary S3 category baseline has **R²=0.5402**, RMSE **0.5505**, and cross-validated RMSE **0.5517**. The existing sensitivity variants give S4 **R²=0.5599**, S5 **R²=0.5610**, and S6 **R²=0.5746**. S3 residual correlation with raw average is **0.678**, with Bayes **0.194**, and with log volume approximately **0.000**; its P95/P99 are **+0.872/+1.318**.

The adjusted-family robustness results are:

- **Top 1%:** 166 games per specification; mean pairwise Jaccard **53.8%**; union **322**; stable (≥5/7) **117**; sensitive (≤1/7) **97**; all-seven intersection **79**.
- **Top 5%:** 830 games per specification; mean pairwise Jaccard **56.8%**; union **1,448**; stable **621**; sensitive **291**; all-seven intersection **380**.

Stable top-1% candidates have mean raw rating **8.003**, mean Bayes **5.745**, median volume **179**, median weight **1.963**, and median playtime **45 minutes**. Stable top-5% candidates have mean raw rating **7.767**, mean Bayes **5.794**, median volume **216**, median weight **2.044**, and median playtime **50 minutes**. These remain descriptive characteristics of robust conditional anomalies, not evidence of broad appeal.

**[Current supported conclusion]** The population correction changes counts and fitted coefficients slightly but leaves the RQ2 interpretation unchanged: stability across related specifications makes a positive residual more reproducible, not independently validated or equivalent to a hidden gem.

### Current audience-proxy and RQ3 refresh

**[Refreshed descriptive finding]** The stable sets remain heterogeneous and the same audience-proxy interpretation applies. Stable top-1% contains **117** games and stable top-5% **621**. Top-1% stable games have mean category-tag count **2.675** and mechanic-tag count **3.496**; top-5% stable games have means **2.936** and **3.968**. Medians remain 3 category tags and 3 mechanic tags in both sets.

The strongest refreshed descriptive contrasts are consistent with the prior patterns: stable top-1% is enriched for Sports (**20.5%**), Party Game (**23.9%**), and Humor (**17.1%**) relative to the rest; stable top-5% is enriched for Sports (**9.0%**), Party Game (**14.5%**), Fantasy (**20.3%**), Miniatures (**10.1%**), and Fighting (**13.2%**). Party Game + Humor occurs in **14.5%** of stable top-1% and **6.9%** of stable top-5%, versus **2.1%** and **2.0%** of their respective complements. Wargame + Miniatures occurs in **5.1%** of stable top-1% and **5.2%** of stable top-5%, versus **1.9%** and **1.8%** of the complements. These are metadata profiles, not independent reach measures.

The refreshed RQ3 audit uses 16,612 common games, with stable top-1% **n=117** and top-5% **n=621**. Coverage and field roles are unchanged: no field directly measures rater segments, exposure, non-raters, plays, ownership, sales, external traffic, or independent audience response. RQ3 therefore remains unidentified.

### Current friend-output comparison

**[Refreshed descriptive finding]** Against the corrected population, the friend file overlaps **16,139** games: **97.1%** of the research population and **65.4%** of the friend file. There are **8,556 friend-only** and **488 research-only** records; the RQ2 complete-case overlap is **16,124**.

The score relationships and correction sizes are effectively unchanged: Pearson/Spearman correlation with current raw average is **0.982/0.982**; the raw correction mean/median is **+0.020/+0.024**, with **57.9%** positive; the Bayes correction mean/median is **+0.861/+0.841**, with **92.1%** positive. The corrected-population top-1% friend set contains **14 of 103** matched stable RQ2 candidates; the top-5% contains **181 of 567**. This remains an output comparison, not validation of the friend's user-level method.

### Current candidate report and handoff

**[Refreshed artifact]** `docs/rq2_candidate_report.md` now uses the corrected **16,612-game** complete-case population and **166-game** top-1% threshold. Its unchanged stable-candidate rule yields a current 25-record screening report; explicitly unreleased records, including Legacy of Eastbrook Hills, are absent.

**[Limitation / next step]** The refreshed figures are still based on the same selected game-level BGG population and the same descriptive models. The release-status correction addresses a concrete population-definition error; it does not address rater self-selection, broad appeal, or the validity of any debiasing method. The richer user-level dataset remains necessary for those questions.

## 2026-08-23: Provisional modern Eurogame-style shortlist

### Method and screening decision

**[Reporting decision]** Created `scripts/12_modern_euro_shortlist.py` and `docs/modern_euro_shortlist.md` as a qualitative screening report over the corrected RQ2 candidate pool. The script reuses the unchanged seven adjusted specifications (S1, S1b, S2, S3, S4, S5, S6), the existing top-1% threshold of **166 games per specification**, and the existing stable threshold of **at least 5/7 selections**. It does not fit a new model, alter residuals, or create a new score.

The screen required year ≥2000 and at least one available BGG category/mechanic associated with strategic/resource-management, economic, engine-building, worker-placement, tile/territory, auction, hand-management, optimization, variable-power, or related designs. It removed records with explicit sports, party, dexterity, wargame, simulation, storytelling/narrative, role-playing, fighting, or dice-oriented profiles; explicit reimplementations; family/edition records identified through BGG family metadata or edition markers; and two remaining campaign/dungeon-crawler or narrative-oriented profiles after metadata review. The release-status exclusion was inherited from the corrected population, not redefined here.

### Result

**[Observed screening result]** Among the **16,612-game** RQ2 complete-case population, the initial modern Euro-associated screen found **21** stable top-1% candidates. Family/edition/reimplementation and clear non-Euro metadata exclusions left **6** records for profile review; one additional campaign/dungeon-crawler record was removed. The resulting provisional shortlist has five games:

- **Brightcast** — 8.10 raw rating, 141 ratings, S3 residual **+1.70**, mean seven-specification residual **+1.67**, stable **7/7**.
- **Evil Upheaval** — 8.51 raw rating, 141 ratings, S3 residual **+1.83**, mean residual **+1.58**, stable **6/7**.
- **Goblin Grapple** — 8.00 raw rating, 213 ratings, S3 residual **+1.66**, mean residual **+1.54**, stable **7/7**.
- **Grasse: Mestres Perfumistas** — 8.05 raw rating, 116 ratings, S3 residual **+1.44**, mean residual **+1.42**, stable **5/7**; this is the clearest conventional economic/worker-placement Euro profile.
- **Abuela Co.** — 8.21 raw rating, 114 ratings, S3 residual **+1.44**, mean residual **+1.33**, stable **5/7**; this is a lighter hand-management/set-collection card-game edge case.

**[Supported interpretation]** These are candidates for being higher-rated than expected under the existing RQ2 baseline, with robustness across related specifications. The screen does not establish that they are genuinely underrated in the population-wide sense, that their ratings are free of selection effects, or that they are hidden gems with broad appeal. The retained set is heterogeneous: Grasse is a conventional Euro-style fit, while the other four are lighter, thematic, two-player, or confrontational card designs retained under the requested mechanism-based definition.

### Limitations and implication

**[Limitation]** BGG categories and mechanics are incomplete, overlapping, and partly subjective. Metadata can remove obvious sports/party/wargame/narrative records and obvious editions, but it cannot reliably identify genre boundaries, audience breadth, or appeal beyond the current rater niche. Family metadata and edition markers can also miss obscure relationships or exclude a legitimate standalone design.

**[Implication / next question]** The shortlist is suitable for manual candidate screening and later comparison with richer audience evidence, but not for declaring hidden gems or for defining an RQ3 ranking. Any next-stage evaluation should test whether these RQ2 candidates show independent cross-audience reach; the current game-level dataset cannot answer that.

## 2026-08-23: Final metadata screening of the modern Euro shortlist

### Audit scope

**[Screening method]** Reviewed the five current shortlist records against the available processed BGG fields and the raw-derived population rule. The audit checked year, `/boardgame/` versus expansion link, `is_expansion`, `expands_name`, `is_reimplementation`, `reimplements_name`, family tags, explicit administrative unreleased tags, BGG rank, rating count, and description/designer completeness. No RQ2 residual, predictor, threshold, or stability definition was changed, and no new score was created.

**[Observed metadata]** All five records have a valid 2018–2025 year, a `/boardgame/` link, `is_expansion=False`, null `expands_name`, `is_reimplementation=False`, null `reimplements_name`, and neither `Admin: Upcoming Releases` nor `Admin: Unreleased Games`. None carries a `Game:` family or explicit edition marker. Crowdfunding tags on Evil Upheaval and Grasse indicate Kickstarter/Catarse history only; they are not evidence that the records are currently unreleased.

### Classifications

**[Screening result]** The classifications below mean `KEEP` = no concrete exclusion is visible and the record remains suitable for provisional follow-up; `UNCERTAIN` = no exclusion is proven, but release visibility, metadata completeness, genre fit, or sample size is too weak for a clean keep decision. No candidate received a metadata-grounded `REMOVE` classification.

- **Brightcast — UNCERTAIN.** It has no expansion, reimplementation, edition, or explicit unreleased marker, but it is a 2025 record with only 141 ratings, no listed designer, and only 5 voters in the older dump snapshot. The available fields cannot establish general/public release visibility or reduce the risk that the +1.70 S3 residual reflects a very small, self-selected audience.
- **Evil Upheaval — UNCERTAIN.** It passes the standalone/reimplementation/edition/status checks and dates to 2021, but has only 141 ratings, no listed designer, and an IP/theme-led profile. Its +1.83 S3 residual may be particularly sensitive to niche selection; the Kickstarter tag does not resolve release timing.
- **Goblin Grapple — KEEP.** It passes the standalone, edition, reimplementation, and status checks and has 213 ratings. Its BGG rank is 21,463, so there is no metadata indication that it is an established high-reach title. Missing designer metadata and a malformed short description reduce confidence, while the high residual remains vulnerable to a small, self-selected card-game audience.
- **Grasse: Mestres Perfumistas — KEEP.** It is the strongest metadata-supported conventional Euro fit: a 2018 standalone record with economic/industry, rondel, trading, and worker-placement metadata, no family/reimplementation/edition/status issue, and BGG rank 9,653. Its 116 ratings, raw 8.05 versus Bayes 5.60, and +1.44 S3 residual still make it a thin-sample RQ2 candidate rather than evidence of broad appeal.
- **Abuela Co. — UNCERTAIN.** It passes the standalone, edition, reimplementation, and status checks, but has only 114 ratings, rank 10,535, and sparse genre metadata (only `Card Game`, with hand management and set collection). Its release visibility and fit as a modern Euro are less strongly evidenced than Grasse's, and the +1.44 residual may reflect a narrow rater pool.

**[Supported conclusion]** Available metadata supports treating Goblin Grapple and Grasse as provisional follow-up candidates, while Brightcast, Evil Upheaval, and Abuela Co. remain screening-uncertain. It does not prove that any record had reached broad/public release at the snapshot date, that any is independent of an unrecorded related design, or that any is broadly appealing. BGG rank is included only as context for apparent established popularity and was not used as an RQ2 predictor or broad-appeal proxy.

**[Implication]** The shortlist should be carried forward as a provisional research list with the three uncertain records flagged, not converted into a final hidden-gem ranking. Resolving release provenance, edition relationships, and audience breadth requires stronger BGG product-history metadata and/or the richer user-level/exposure data; the current game-level dataset cannot resolve those questions.

## 2026-08-23: Phase 2 SQLite database discovery inventory

### Discovery scope

**[Method]** Inspected `data/raw/bgg.sqlite` read-only using SQLite schema queries, `PRAGMA table_info`, `PRAGMA index_list`/`index_info`, `PRAGMA foreign_key_list`, and row/coverage counts. No database table or record was modified, and no substantive rating, user, or audience analysis was performed. The detailed inventory is in `docs/phase2_database_inventory.md`.

### Database structure

**[Observed schema]** The database is approximately **9.0 GB** and contains 11 application tables. The most important tables are:

- `user_ratings`: **18,942,215** compact individual ratings across **21,925 games** and **411,375 usernames**, with no timestamp or user-profile fields.
- `reviews`: **29,618,326** review/rating records across **103,084 games** and **606,497 pseudonymous users**; fields include `rating`, `rating_tstamp`, `comment_tstamp`, `postdate`, and `reviewid`.
- `collections`: **29,618,326** user-game status records with ownership, want-to-play, preorder, previously-owned, wishlist, want, want-to-buy, for-trade, and `status_tstamp` fields.
- `users`: **606,497** pseudonymous user records with state/country and up to five message-board name/description/timestamp fields.
- Game metadata is split across `games` (**161,404** rows), `game_attrs` (**21,925**), `game_links` (**43,196**), `game_ranks` (**34,513**), `game_tags` (**276,045**), `rating_dist` (**485,707**), and `weights` (**22,329**).

No application table declares foreign keys. Primary keys exist for `game_attrs` and `weights` (`game_id`) and composite keys exist for links, ranks, tags, and rating distributions. `games` has a unique non-null `game_id` index but **35,138 null-ID rows**; `reviews`, `collections`, and `user_ratings` have no declared primary key or uniqueness constraint. Relevant game/user indexes exist, but relationships are not database-enforced.

### Key Phase 2 discoveries

**[Observed data]** The database contains the individual-level evidence the game-level phase lacked:

- `reviews` contains **26,924,709 non-null ratings**; `rating_tstamp` is present for **26,924,708** of them and spans **2001-05-29 to 2025-02-10**. `comment_tstamp` is present for **6,264,799** rows, and `postdate` for **29,602,822** rows.
- `collections` has the same row count and the same distinct game/user/review-ID counts as `reviews` (**103,084 games**, **606,497 users**, **29,617,496 review IDs**), suggesting a paired extraction. This is not a proven one-to-one relationship because no foreign key or uniqueness constraint is declared.
- All `reviews.user_pseudouserid` and collection user IDs match the unique `users.user_pseudouserid` table. In contrast, `user_ratings.username` has **zero** matches to those pseudonymous IDs, so the compact rating table is not currently joinable to the user/profile/collection path.
- `users` has **195,460 null country values** and 242 distinct country values. It contains no explicit demographics, play counts, exposure, purchase history, or rater-credibility variable.
- `collections.status_tstamp` is present for **21,061,870** rows and spans **2010-10-26 to 2025-02-10**. The flags are status fields, not a documented history of ownership or play events.

**[Supported implication]** The `reviews`–`users`–`collections` path appears capable of supporting later audits of rating timing, user-level rating behavior, collection/status overlap, and cross-game participation. This makes audience-selection investigation newly possible in principle, subject to key and timestamp validation.

### Important unknowns

**[Limitation]** Discovery did not establish whether `reviews` contains repeated user-game ratings, whether `reviewid` represents a stable review/rating event, or whether the timestamps represent event creation versus scrape/application time. It also did not establish whether `collections` is a current snapshot or longitudinal status history, whether `user_ratings` is a separate snapshot/transformation, or whether all tables share one coherent extraction date. The database still lacks a denominator for people exposed to a game who did not rate it, plus sales, plays, impressions, and direct audience-segment labels.

**[Next step]** Phase 2 should begin with duplicate/cardinality checks, validation of the `reviews`–`collections` join, timestamp semantics and snapshot consistency, and assessment of whether pseudonymous users can be safely used to study rater composition. No substantive audience or debiasing conclusions should be drawn from the new database until those audits are complete.

## 2026-08-23: Phase 2 analytical access layer and Parquet extracts

### Architecture and extraction decision

**[Implementation]** Created `scripts/13_build_phase2_extracts.py` and the read-only analytical layer under `data/processed/phase2/`. DuckDB's SQLite scanner extension was unavailable in the offline environment, so the script uses Python's SQLite driver in `mode=ro` with PyArrow streaming writes. The resulting Zstandard-compressed Parquet files are directly queryable with DuckDB; the raw 9 GB SQLite database was not modified.

The canonical architecture is:

```text
games/game_attrs/weights ── game_id ── ratings/reviews ── user_pseudouserid ── users
                                      │
                                      └── game_id + reviewid + user_pseudouserid ── collections
game_tags/game_links ──────────────── game_id ── games
```

The reusable extracts are:

- `data/processed/phase2/games.parquet` — **21,925** detailed game rows, joining `game_attrs` to browse fields and weights.
- `data/processed/phase2/users.parquet` — **606,497** pseudonymous users with state/country and message-board timestamps; message text is intentionally omitted.
- `data/processed/phase2/user_ratings.parquet` — **18,942,215** compact ratings with source row ID, game ID, rating, and username; it has no timestamps and its username namespace is not joinable to `users`.
- `data/processed/phase2/ratings.parquet` — **29,618,326** review/rating rows with `source_rowid`, game/review/user keys, rating, and timestamps. It preserves rows with null ratings; use `WHERE rating IS NOT NULL` for rating-bearing rows.
- `data/processed/phase2/collections.parquet` — **29,618,326** collection/status rows with `source_rowid`, game/review/user keys, status timestamp, and ownership/wishlist/preorder-related flags.
- `data/processed/phase2/game_tags.parquet` — **276,045** normalized game tags.
- `data/processed/phase2/game_links.parquet` — **43,196** game relationship rows.
- `data/processed/phase2/validation.json` and `extract_counts.json` — extraction checks and row counts. `data/processed/phase2/README.md` documents the layer.

### Validated joins and source semantics

**[Observed validation]** Deterministic representative checks found:

- The five current Euro shortlist IDs yielded **556** review rows; all **556/556** matched a `users` row and all **556/556** matched `collections` on `(game_id, reviewid, user_pseudouserid)`.
- A deterministic cross-table sample of **890** review rows matched both `users` and `collections` on the same keys.
- The sampled game metadata join succeeded for the **2** shortlisted IDs present in `game_attrs` and `games`.
- The exported Parquet row counts match the source counts, and the five shortlisted IDs are present in the ratings extract. Their database snapshot rating-bearing row counts are **5 Brightcast, 140 Evil Upheaval, 209 Goblin Grapple, 111 Grasse, and 66 Abuela Co.** These differ from the later game-level snapshot counts and confirm that the SQLite database is not the same snapshot as the current game-level population.

**[Observed duplicate semantics]** `reviews` and `collections` have no declared primary key. Globally, `reviews` has **29,618,326 rows** but **29,617,496 distinct review IDs**, so `reviewid` is not globally unique. Repeated user-game rows also occur: for Carcassonne (`game_id=822`) there are **137,437 rows**, **137,437 distinct review IDs**, and **136,937 distinct users**. Example repeated user-game records have different review IDs and rating timestamps, sometimes with the same rating, so they must be treated as possible review/rating events or updates—not silently collapsed to one observation. The extracts preserve all source rows and add SQLite `source_rowid` as a snapshot-local unique row key.

**[Observed timestamp semantics]** The timestamp fields are not interchangeable. In sampled rows, `rating_tstamp` can be seconds after `postdate` or several years later; therefore it cannot yet be assumed to be the first rating date or original review date. `comment_tstamp` is sparse and sometimes absent. The access layer stores the original timestamp strings without parsing or imposing an event policy.

### Unresolved ambiguities carried forward

**[Limitation]** The access layer deliberately does not deduplicate review rows, select a latest rating, infer rating-change events, or claim that collection flags are longitudinal exposure/ownership histories. The exact meaning of `reviewid`, the semantics/provenance of each timestamp, snapshot timing across tables, and the relation between `user_ratings.username` and the pseudonymous review users remain unresolved. The next Phase 2 step is a focused cardinality, timestamp, and snapshot audit before any rater-behavior or cross-audience analysis.

## 2026-08-23: Canonical rating observations and descriptive rater behavior

### Canonical source and observation definition

**[Method decision]** Created `scripts/14_phase2_rating_semantics_and_rater_behavior.py` and defined `data/processed/phase2/rating_observations.parquet` as the canonical individual-rating dataset. It contains every row from the review-based `ratings.parquet` extract with a non-null `rating`: **26,924,709 observations**. The retained fields are `rating_observation_id` (the source SQLite row ID), `game_id`, `reviewid`, `user_pseudouserid`, `rating`, `rating_tstamp`, `comment_tstamp`, and `postdate`.

No user-game, review-ID, timestamp, or rating-value deduplication was applied. This preserves potentially meaningful review/rating history while making the source row explicitly addressable. `user_ratings.parquet` is retained as an auxiliary alternate source: it has no timestamp and its `username` identifiers do not join to the pseudonymous `users` table, so it is not the canonical source for user-level behavior.

### Duplicate-record semantics

**[Observed data]** In the canonical non-null-rating data there are **26,922,724 distinct user-game pairs**. **1,795 pairs** repeat, accounting for **1,985 repeated observations** and a maximum of **11 observations** for one pair. Every repeated pair has multiple review IDs; **764 repeated pairs** have more than one distinct rating value. Repeated user-game records are therefore rare (about **0.007%** of observations) but not safely removable: they can represent separate review/rating events or updates, and some contain different rating timestamps even when the rating value is unchanged.

**[Supported decision]** User-level counts are reported in two forms: `rating_observations` counts all retained source observations, while `distinct_games` counts unique games per user. They are nearly identical in aggregate because repeats are rare, but the distinction is preserved for later sensitivity checks. No “latest rating” rule is adopted yet.

### Timestamp semantics

**[Observed data]** `rating_tstamp` parses for **26,924,708 of 26,924,709** canonical ratings. `postdate` parses for **26,910,193**, leaving **26,910,193 rows** with both fields. Among those paired timestamps:

- `rating_tstamp` is later than `postdate` for **18,236,438** rows (**67.8%**);
- the two timestamps are exactly equal for **8,673,740** rows (**32.2%**);
- `rating_tstamp` is earlier for only **15** rows;
- the median `rating_tstamp - postdate` is **1.92 days**, the 90th percentile is **1,081.88 days**, and the maximum is **8,588.63 days**.

**[Supported conclusion]** `rating_tstamp` cannot safely be treated as the original rating/publication timestamp. It is a rating-related timestamp whose provenance is unresolved; the long positive offsets are consistent with later rating updates, review/rating record changes, or extraction semantics. The canonical extract preserves it as a raw field, and the stability check below does not order observations by it.

### Rater-level descriptive results

**[Method]** Computed per-user rating count, distinct-game count, mean, within-user standard deviation, rating quantiles/range, and repeated-observation count in `rater_stats.parquet`. Users were grouped by lifetime canonical rating-observation count. For users with at least 20 observations, a deterministic even/odd `rating_observation_id` split provides an internal partition-consistency measure. This is not temporal stability because the timestamp semantics are unresolved.

The canonical source contains **571,248 users with at least one rating**, with a mean of **47.13** observations per user and median **11**. The mean of user means is **7.981**, the between-user SD of those means is **1.286**, the mean within-user rating SD is **1.248**, and its median is **1.207**.

| Lifetime observations | Users | Mean user rating | Between-user SD | Mean within-user SD | Median split absolute difference | Split users |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 124,374 | 8.854 | 1.737 | — | — | 0 |
| 2–4 | 86,646 | 8.484 | 1.241 | 0.956 | — | 0 |
| 5–9 | 64,786 | 8.062 | 0.965 | 1.224 | — | 0 |
| 10–24 | 96,230 | 7.737 | 0.804 | 1.315 | 0.374 | 23,857 |
| 25–49 | 72,632 | 7.498 | 0.714 | 1.349 | 0.298 | 72,632 |
| 50–99 | 58,743 | 7.347 | 0.673 | 1.350 | 0.210 | 58,743 |
| 100–249 | 45,884 | 7.174 | 0.653 | 1.344 | 0.142 | 45,884 |
| 250–499 | 15,245 | 6.943 | 0.641 | 1.354 | 0.094 | 15,245 |
| 500–999 | 5,364 | 6.731 | 0.642 | 1.355 | 0.067 | 5,364 |
| 1,000+ | 1,344 | 6.435 | 0.708 | 1.372 | 0.043 | 1,344 |

**[Empirical finding]** Rating distributions vary strongly with lifetime rating count. Mean user rating falls from **8.854** among one-rating users to **6.435** among users with 1,000+ observations, a **2.42-point** difference. Between-user variation is much larger among one- and low-count users and settles near **0.64–0.71** at high counts. Within-user spread rises from the small multi-rating bands to approximately **1.35–1.37** among high-volume users, consistent with high-volume users rating a broader or less selectively positive set of games, though this cannot distinguish behavior from composition.

The even/odd partition difference declines with count, from a median **0.374** at 10–24 observations to **0.043** at 1,000+, as expected when averaging more observations. This shows greater numerical consistency of high-count user means, but it is not evidence that high-count users are more accurate, less biased, or more representative.

### Interpretation, limitations, and next implication

**[Supported conclusion]** The data support the premise that users differ systematically in rating level and dispersion, and that lifetime rating count is strongly associated with those differences. However, rating count is not established as a rater-credibility measure. It is simultaneously an activity/exposure measure, is affected by which games users choose to rate, and is entangled with time, game mix, and selection into BGG. Singleton means are especially unstable, while high-count users are more internally precise but may be systematically harsher or more broadly sampled.

**[Limitation]** This is descriptive only. There is no external quality target, repeated independent rating task, user exposure denominator, or non-rater population with which to validate accuracy or separate rater severity from game-selection composition. The split measure is deliberately non-temporal, and duplicate/revision semantics remain unresolved.

**[Implication / next question]** Do not use rating count alone as a credibility weight or rater debiasing rule. The next analysis should examine user-game selection and cross-game participation—especially whether high- and low-volume users rate systematically different game types and whether user-level severity persists after conditioning on overlapping games—before any debiasing model is considered.

## 2026-08-23: Phase A step 1 — the volume-level gap survives within games

### Scope and method

**[Method]** Ran new `scripts/15_phase2_same_game_volume_comparison.py` against the canonical `rating_observations.parquet` extract (26,924,709 observations, 571,248 raters, 95,540 games in the SQLite snapshot). Users were grouped by lifetime rating count into the established volume bands (`rater_behavior_by_volume.parquet`). Four complementary designs, simplest first: (1) raw band means; (2) shared-ground overlap between band rater pools; (3) paired within-game contrasts (games with >=3 distinct raters in each compared group); (4) a game fixed-effects regression `rating ~ band dummies + game FE` on all 26.9M observations (exact within-game demeaning, SEs clustered by game). Timestamps not used. Outputs: `data/processed/phase2/game_band_cells.parquet`, `within_game_diffs_*.parquet`, `same_game_volume_contrast.json`.

### Results

1. **The raw band gradient reproduces on canonical observations [Observed fact]:** pooled mean rating falls monotonically from **8.854** (band '1', 124,374 users) to **6.397** (band '1000+', 1,344 users); restricting to games with >=100 snapshot ratings barely changes it (**8.824 -> 6.448**).

2. **Shared ground exists mainly through popularity [Empirical finding]:** band-'1' users collectively rated 21,297 games; **17,021** of these were also rated by >=1 band-'1000+' user (Jaccard 0.247), and **5,881** games have >=3 distinct raters on each side. Low-band users concentrate heavily on popular games: **95.8%** of band-'2-24' *observations* fall on games having >=3 band-'1000+' raters (per-user shares are bimodal {0,1} because most low-band users rate few games; observation-weighted shares are the informative form).

3. **The gap survives within games almost intact — the central result [Empirical finding]:**
   - Paired contrast band '1' vs '1000+' (>=3 raters each side, **5,881 games**, median 744 total raters/game): mean within-game gap **+2.28** points (median **+2.27**, IQR +1.61 to +2.99), **96.4% of games positive**, precision-weighted pooled **+2.08**. The unconditional gap is **2.42** points.
   - Paired contrast bands '2-24' vs '500+' (**23,664 games**): mean **+1.28** (median +1.20), **93.4% positive**. Not a singleton-user artifact.
   - Sensitivities leave conclusions unchanged: dropping sub-1.0 junk ratings and repeated user-game extras gives +2.28 / +1.28; restricting to >=100-rating games gives **+2.19 / +1.13**.
   - Game-FE regression across all ten bands (reference '1000+'): coefficients decline smoothly **+2.066 (band 1), +1.663 (2-4), +1.343 (5-9), +1.053 (10-24), +0.837 (25-49), +0.679 (50-99), +0.504 (100-249), +0.314 (250-499), +0.173 (500-999)** with cluster SEs 0.002–0.018. Both statistically and practically significant throughout.

### Interpretation

**[Supported conclusion]** Different game mixes explain almost none of the low-vs-high-volume rating-level gap. Conditional on rating the *same game*, lighter BGG participants rate roughly 1–2 points higher, and the conditional gap nearly equals the unconditional one. Under AGENTS.md's classification this behaves like a rater-level level difference (severity/scale anchoring or enthusiasm-state differences), not measurement noise and not primarily composition.

**[Unidentified remaining confounds]** This does NOT prove pure severity:
- *Within-game selection*: among a game's raters, those who go on to become heavy BGG users may differ in enthusiasm-for-that-game from one-shot raters; lifetime volume is itself partly an outcome of enthusiasm trajectories.
- *Timing*: heavy users' ratings may be older or newer on average; platform-era drift could contribute to the same pattern. Untested here (timestamp semantics unresolved; see next steps).
- The paired universe skews toward popular games by construction.

### Implications

- Any correction that treats the low-volume-user mean (e.g., 8.85 for single-rating users) as an unbiased estimate of game quality is unsupported: on identical games these users sit ~2 points above 1,000+-rating users.
- Next: estimate per-user severity conditioned on games and test its stability (even/odd, time periods), then decompose the residual gap into experience/exposure components.

## 2026-08-23: Phase A steps 2-3 — severity offsets are real, stable, and close the gap

### Scope and method

**[Method]** Ran new `scripts/16_phase2_user_severity_stability.py` (two-way additive fit `rating = mu + game_alpha + user_delta` over all 26,924,709 canonical observations by alternating projections; 95,540 games x 571,248 raters) and `scripts/17_phase2_gap_decomposition.py` (game-mix standardization and era-controlled contrasts). Outputs: `user_severity.parquet`, `game_adjusted_means.parquet`, `user_severity_stability.json`, `gap_decomposition.json`, `gap_cells_low_high.parquet`. Timestamps used only as labeled sensitivities because their semantics remain unresolved.

### Severity offsets conditioned on games (step 2)

1. **User severity offsets are large and ordered by lifetime volume [Empirical finding]:** mean delta falls monotonically from **+0.84** (band '1') to **-1.25** (band '1000+') — a **2.09-point** spread conditional on the games each band rates. This matches the within-game FE gradient from script 15 almost exactly.

2. **Severity is a stable rater trait, not fitting noise [Empirical finding]:**
   - Even/odd parity halves (independent observation splits; users with >=20 obs per half, n=223,069): Pearson **r=0.872**, Spearman **0.844**, median |delta_even - delta_odd| = **0.175**, SD of difference 0.356 vs SD of each half ~0.704. A placebo correlation across mismatched users is **~0.003**.
   - Across time periods (median split, >=10 obs per period): postdate reading r=**0.533** (n=110,826), rating_tstamp reading r=**0.478** (n=113,177). Moderately stable under both readings; lower than parity stability, consistent with some genuine drift and/or period-composition differences. Which timestamp field applies barely changes the conclusion.
   - ICC-style reliability by band (script 18, `rater_credibility.json`): **0.74** at 10-24 observations, **0.89** at 50-99, **0.95** at 100-249, **0.995** at 1000+. Signal SD ~0.61-0.70 throughout.

3. **How much rating variance does identity explain? [Empirical finding]** Nested-model R2 on all observations: game identity alone explains **R2=0.230** of rating variance; rater identity alone explains **R2=0.249**; the additive two-way fit explains **R2=0.438**. The two are nearly complementary (sampled corr(alpha, delta) ~ -0.05). Under this data's conditions, *who rates matters about as much as what is rated* for individual rating variation.

### Decomposition of the low-vs-high gap (step 3)

Low group = lifetime bands 1-9 (802,335 observations); high group = bands 500+ (5,594,821).

4. **Game mix explains little; severity explains essentially all the rest [Empirical finding]:**
   - Raw pooled gap: low **8.291** vs high **6.602** = **+1.689**.
   - Standardized to identical game weights (Kitagawa-style over shared games; support overlap is 98.7% of low-group observations): gap **+1.389** — game-mix composition accounts for only ~0.30 points (~18%).
   - After additionally subtracting fitted user severity offsets: gap **+0.012** — statistically and practically indistinguishable from zero. The entire standardized gap is an additive rater-level level difference; no low-volume-x-game-type interaction is needed.

5. **Calendar-era composition cannot produce the gap [Empirical finding / sensitivity]:** mean ratings rise strongly over the snapshot (e.g., 6.39 in 2003 to 7.31 in 2023 by postdate reading). But recomputing paired within-game contrasts inside era windows gives +1.60 (<=2010), +1.77 (2011-2017), +1.70 (2018-2025) under postdate and +1.56/+1.74/+1.69 under rating_tstamp — the gap persists in every window under both readings. Light-volume users actually rate *newer* games on average (mean year 2018.8 vs 2016.6), the opposite direction from what an era-inflation artifact would require.

6. **No experience-hardening within raters [Hypothesis-grade empirical finding]:** among users with >=50 lifetime observations, last-decile ratings sit slightly HIGHER than first-decile (+0.055 by postdate order, +0.234 by rating_tstamp order). If heavy raters became harsher with experience we would see the opposite sign; ordering uses unresolved-semantics timestamps, so this remains hypothesis-grade.

### What severity adjustment does and does not buy (RQ1 relevance)

7. **Adjusted game estimates answer a different question, not a better predictor of observed ratings [Model-dependent conclusion]:** held-out prediction of individual odd-half ratings from even-half fits: raw train game-mean RMSE **1.417**; game-FE-only prediction (mu + alpha) RMSE **1.563**; adding user deltas **1.253** (-11.6% vs raw). Interpretation: severity-adjusted game means deliberately remove who-rated effects, so they predict the *observed* rating stream worse than raw means when rater mixes repeat; knowing the rater helps predict individuals. Adjusted estimates target "level net of rater composition," which must not be marketed as higher-fidelity measurement of the same quantity.

8. **Magnitude of adjustment at game level [Observed fact]:** adjusted minus raw game means have median **+0.67**, P5-P95 [-0.56, +1.47]; shifts are similar across snapshot volume bands (medians 0.64-0.82), i.e., adjustment is not simply a low-volume-game boost.

### Classification per AGENTS.md

- **Measurement noise:** cannot explain these patterns (parity stability, holdout gains, era-window persistence).
- **Selection into what users rate:** accounts for only ~18% of the raw gap (standardization step).
- **Rater-level level differences (severity/scale anchoring):** account for essentially everything that remains, and are stable enough to estimate (reliability >=0.74 with >=10 obs/half).
- **Caveat kept open [Unidentified]:** delta_u itself may partially encode enthusiasm trajectories (users whose enthusiasm faded rate more games and more harshly); "severity" here is descriptive level, not a causal disposition. Distinguishing those requires data this snapshot lacks.

### Implication for the debiasing premise

The friend-style premise that harsh/generous patterns reflect *who rates what* is mostly wrong in this data: who-rates-what explains little once you condition on games, while *who rates them at all* — captured by stable per-user offsets — explains nearly all of it. Any correction aimed only at game-mix or noise will therefore leave a ~1.4-point rater-level gradient untouched.

## 2026-08-23: Phase B — temporal drift, audience/self-selection, cross-audience consistency

### Scope and method

**[Method]** Ran new `scripts/19_phase2_temporal_drift.py` (`temporal_drift.json`), `scripts/20_phase2_audience_selection.py` (`audience_selection.json`), and `scripts/21_phase2_cross_audience_consistency.py` (`cross_audience_consistency.json`). All time questions are run under BOTH timestamp readings (`postdate`, `rating_tstamp`; semantics unresolved). Audiences are geography (top countries; country missing for 195,460 of 606,497 users) and per-observation ownership status from `collections.own`.

### Temporal drift (Phase B item 5)

1. **Aggregate era rise is composition, not within-game inflation [Empirical finding]:** mean ratings rise ~+0.9 points across calendar years under both readings (e.g., 6.39 in 2003 to 7.31 in 2023, postdate). But within fixed games (>=30 observations in own early and late observation terciles, n=16,718 games), later terciles rate **lower**: late-minus-early **-0.143** (postdate) / **-0.256** (rating_tstamp). Newer-rated games and changing rater cohorts drive the aggregate rise.

2. **Game-age effect at rating time [Empirical finding]:** ratings fall monotonically with game age at rating: ~**7.4** at release year, **7.0** at 10 years, **6.8** at 20 years, **5.95** at 40 years (both readings agree). Confounded with which old games still attract raters.

3. **Severity tracks career stage, not join cohort [Empirical finding]:** within lifetime-volume bands, severity deltas are nearly identical across first-activity cohorts (e.g., band 100-249: -0.74 for <=2010 starters vs -0.79 for 2016+ starters). Cohort gaps in script 18 were volume composition, not cohort effects.

### Audience differences and self-selection (Phase B item 6)

4. **Geographic audiences differ only marginally in level [Empirical finding]:** raw country means sit in a narrow 7.00-7.26 band; paired within-game contrasts versus the US (n>=3 raters each side) range from **-0.12** (Poland) to **+0.20** (France) - an order of magnitude smaller than the volume-band gradient (+2.1).

5. **Audiences select different games [Empirical finding]:** Germany's co-rated game universe skews toward Card Game (19.7% vs 13.8% of US-rated games), Strategy (10.2% vs 5.5%), Family, Dice Rolling, Hand Management; the US universe covers more niche wargame publishers (SPI, Decision Games) and uncredited designers. Participation is audience-specific even when rating levels agree.

6. **Ownership is the big audience split [Empirical finding]:** raters whose snapshot collection row does NOT show `own` rate the same games **-0.95 points** lower than owner-raters (44,884 paired games, median -0.93; raw levels 6.53 vs 7.54 across 26.9M observations). This is the largest audience-level gap found in the snapshot. Caveats: status is snapshot-time, not event history; non-owner raters mix wishlist, app/library players, and past owners.

### Cross-audience consistency (Phase B item 7)

7. **Geographic audiences largely agree on which games are good [Empirical finding]:** US-Germany game means correlate r=0.87 (median |diff| 0.23, P90 0.69); other pairs similar (r 0.85-0.86). Divergent extremes exist but are mostly small-sample (examples: an 18xx title rated +1.51 by Germans; a dexterity children's title rated +1.38).

8. **Owner vs non-owner disagreement dwarfs geographic disagreement [Empirical finding]:** same-game means correlate r=0.854, but median |diff| is **0.95** and P90 **1.54** (27,849 games). Where "different audiences disagree," ownership status - a selection/commitment signal - is where it lives, not country.

## 2026-08-23: Phase B item 8 — what each correction targets; friend-method revisit

### Scope and method

**[Method]** Ran new `scripts/22_phase2_baseline_comparison.py`. Added a residual export to `scripts/05_rq2_expected_rating_baseline.py` (unchanged specifications) writing `data/processed/rq2_residuals.parquet` (16,612 complete-case games). Matched 16,552 games between the user-level SQLite snapshot (scripts 15-17 estimates) and the current game-level population; 16,124 also matched the friend file. Raw means agree across snapshots (Pearson 0.979, median diff -0.012), so comparisons are meaningful though snapshot-mismatch noise (~SD 0.17) applies to all correlations as attenuation.

### Findings

1. **Removing rater-level offsets does NOT shrink the volume-rating gradient - it grows [Empirical finding]:** pooled game-level slope on log10(users_rated): raw mean **+0.444**, severity-adjusted mean **+0.513** per tenfold increase; weight/year-adjusted: +0.297 raw vs **+0.361** adjusted. High-volume games' rater pools skew *harsher*, so composition works against the observed popularity premium. The RQ1 volume gradient cannot be explained by who-is-harsher composition; it must reflect selection into which games accumulate volume (including quality-driven popularity) or within-game rater selection - not additive rater-level differences.

2. **The friend's `debiased_rating` behaves like a shrunken version of our severity adjustment [Empirical finding / model-dependent conclusion]:**
   - Levels: friend_debiased correlates **0.996** with our adjusted mean (Pearson and Spearman); top-5% sets overlap Jaccard **0.70**.
   - Corrections: friend_shift = debiased - current_avg regresses on our severity shift as **-0.485 + 0.669 x our_shift**, r=**0.836** (70% of variance explained).
   - Magnitudes/conventions: friend shifts average +0.02 (SD 0.15) vs our +0.75 (SD 0.21) over this population - the friend re-centers near zero and applies roughly two-thirds of the per-game adjustment slope.
   - Classification per AGENTS.md: the friend's output targets the same phenomenon our deltas identify - **rater-level level differences conditioned on games (selection-into-rating severity/scale anchoring)** - not measurement noise (parity stability shows these offsets are real signal, not error) and not game-mix composition (which explains little anywhere).
   - Still unknown: whether the friend's method addresses *within-game* selection (enthusiasm trajectories) or only additive level; its magnitude convention is undocumented; snapshot mismatch adds noise.

3. **Estimate families remain distinct [Observed fact]:** RQ2 S3 residual correlates 0.63 with friend_debiased and Jaccard-overlaps its top-5% by only 0.15; Bayes remains its own shrinkage transform (Jaccard with RQ2 residual 0.02).

### Implications

- A severity-adjusted game estimate is now implementable and reproducible from committed scripts (adj_mean in `game_adjusted_means.parquet`). It removes measured rater-level composition. It does NOT measure broad appeal, does not fix within-game self-selection, and is not a better predictor of observed ratings than raw averages (script 16 holdout).
- For any underratedness analysis, severity adjustment and the RQ2 conditional residual answer different questions (who-vs-what level vs expected-given-characteristics); both remain model-dependent screens rather than quality estimates.

## 2026-08-23: Session summary — Phase 2 user-level program complete through first pass

### What was established this session

Scripts 15-22 built the user-level evidence base (all rerunnable against `data/processed/phase2/` extracts; derived extracts under the same directory; DuckDB engine):

1. The low-vs-high lifetime-volume rating gap (+2.42 pooled) survives within games (+2.28 paired) and is closed to +0.01 by game-mix standardization plus stable per-user severity offsets.
2. Per-user severity is estimable (reliability >=0.89 at >=50 observations), stable across independent halves (r=0.87), only moderately stable across time periods (r~0.5), and not a cohort or career-drift artifact.
3. Rating variance decomposition: game identity R2=0.230, rater identity R2=0.249, additive both 0.438.
4. Severity adjustment raises, not lowers, the game-level volume gradient (+0.44 -> +0.51 per tenfold ratings): rater-level composition works against the popularity premium.
5. Era composition does not produce the gap (persists in all era windows under both timestamp readings); aggregate era rise is composition; within-game era trend is slightly negative.
6. Geographic audiences agree closely (r~0.86); ownership status is the largest audience split found (median same-game gap 0.95).
7. The friend's `debiased_rating` is behaviorally a shrunken severity adjustment of ours (level corr 0.996; shift corr 0.836, slope 0.67): it targets rater-level level differences - selection into rating, not measurement noise.
8. No accuracy criterion exists for raters; volume/severity/tenure/spread are entangled activity measures. "Credibility weighting" is not identifiable from this data.

### Final refit note

The committed `scripts/16` was rerun end-to-end at full convergence (100 alternating-projection iterations, final max change 0.0028). All headline numbers were unchanged from the reported values (R2 decomposition, parity stability, band means identical to 3 decimals; downstream scripts 17/18/22 regenerated with no material diffs).

### Still open / next highest-value questions

1. **Within-game self-selection** remains unidentified: additive deltas capture who-is-harsher, but not whether a game's *rater pool composition within an audience* biases its mean (e.g., only enthusiasts rate niche games at all). This needs exposure-denominator data or panel structure; no proxy in this snapshot identifies it.
2. **Timestamp semantics** still unresolved; temporal results carry both readings but provenance would sharpen drift conclusions.
3. **Ownership history**: snapshot-time `own` flags show a 0.95-point split; longitudinal collection data would turn this into a real selection test.
4. **Validation target for corrections**: whether severity-adjusted estimates predict held-out future ratings or external outcomes better than raw averages is untestable here beyond parity splits; a second time-period scrape would enable true out-of-time validation.

### Deliverables index

- Scripts: `15_phase2_same_game_volume_comparison.py`, `16_phase2_user_severity_stability.py` (`--reuse` mode available), `17_phase2_gap_decomposition.py`, `18_phase2_rater_credibility.py`, `19_phase2_temporal_drift.py`, `20_phase2_audience_selection.py`, `21_phase2_cross_audience_consistency.py`, `22_phase2_baseline_comparison.py`; residual export added to `05`.
- Derived extracts (gitignored, reproducible): `game_band_cells.parquet`, `within_game_diffs_*.parquet`, `user_severity.parquet`, `game_adjusted_means.parquet`, `gap_cells_low_high.parquet`, `era_mix_by_group.parquet`, comparison tables.
- JSON result summaries beside each script's outputs under `data/processed/phase2/`.

## 2026-08-24: Filtered Phase 2 universe built (primary analytical layer going forward)

### Method

**[Method]** New `scripts/23_build_filtered_phase2_extracts.py` restricts the Phase 2 parquet extracts to the 16,627-game research population via explicit DuckDB SEMI JOINs on `game_id` (bounded memory 4GB / 4 threads; EXPLAIN-asserted semi joins; no wide tables, no positional pandas). Canonical observation definition unchanged: every non-null review rating, no deduplication, `rating_observation_id`/`source_rowid` retained. Outputs under `data/processed/phase2-filtered/` (rating observations, games metadata, users with ≥1 filtered rating, collections, tags, links) plus validation.json / extract_counts.json / parquet_catalog.csv. Catalog and caveats: `docs/phase2-filtered/PARQUET_CATALOG.md`.

### Results

1. **94.1% of all rating observations fall on population games [Observed fact]:** 25,335,220 of 26,924,709 observations; the excluded ~79k low-volume snapshot games hold only ~1.59M. The brief's 60–70% guess was wrong in an informative direction — popularity concentration puts almost all rating mass inside the research population.
2. **16,567 of 16,627 population games have ≥1 snapshot rating [Observed fact]:** the 60 absentees are recent high-game_id releases missing from this earlier SQLite scrape (snapshot mismatch, not filter loss).
3. **Only 13,449 of 16,567 rated games (81.2%) carry a `games.parquet` attrs row [Observed fact]:** game_attrs covers 21,925 of 95,540 snapshot games; weight/player-count analyses on filtered data will miss ~19% of rated population games unless supplemented by the game-level population parquet (complete for all 16,627).
4. **Validations passed [Observed fact]:** output rows equal an independent source-restricted count (semi join neither duplicated nor dropped); 100% user match; collection triple-join sample 2,567/2,567; shortlist spot checks reproduce findings.md counts exactly (Brightcast 5, Evil Upheaval 140, Goblin Grapple 209, Grasse 111, Abuela Co. 66); repeated user-game pairs preserved (1,465 pairs).

### Implication

Phase 3 restarts on `data/processed/phase2-filtered/rating_observations_filtered.parquet`. Full-snapshot extracts and scripts 15–22 fit artifacts (`user_severity.parquet`, `game_adjusted_means.parquet`) are historical reference only; re-estimating taste/type quantities on the filtered universe is the next task's deliverable.
## 2026-08-24: Primary analytical user population — minimum lifetime rating-count threshold study

### Scope and method

**[Method]** Ran new `scripts/23_user_threshold_study.py`: compared candidate minimum lifetime rating-count thresholds t ∈ {1, 3, 5, 10, 20, 50, 100} for the primary Phase 3 user population, with the game universe fixed at the corrected **16,627-game research population**. Lifetime counts are computed **within that universe** unless labeled otherwise (canonical `rating_observations` restricted to population games: **25,335,220 observations, 544,955 users; 16,567 of 16,627 games carry ≥1 snapshot rating**). Reused the established even/odd `rating_observation_id` parity design (scripts 14/16) for split-half stability of user means, and the script-18 signal/noise decomposition for ICC-style reliability (`noise_sd(half)=sd(diff)/√2`). Severity stability is proxied by a one-sweep game-adjusted offset (user mean of rating − own-half game mean — step 1 of script 16's alternating projections), not a refit. Duplicates preserved per canonical definition (~0.007% repeated user-game rows); timestamps unused. Outputs: `reports/user_population_thresholds.{csv,json}` (committed).

### Results

| t | users kept | ratings kept | share ratings | ICC-style reliability of user mean | median abs half-diff | severity-proxy r |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 544,955 | 25,335,220 | 100.0% | 0.617* | 0.317 | 0.614 |
| 3 | 399,320 | 25,151,346 | 99.3% | 0.647 | 0.311 | 0.650 |
| 5 | 353,841 | 24,995,190 | 98.7% | 0.699 | 0.285 | 0.710 |
| 10 | 289,397 | 24,558,361 | 96.9% | 0.780 | 0.245 | 0.795 |
| 20 | 217,102 | 23,547,280 | 92.9% | 0.850 | 0.201 | 0.864 |
| 50 | 121,497 | 20,487,136 | 80.9% | 0.918 | 0.150 | 0.928 |
| 100 | 64,411 | 16,478,175 | 65.0% | 0.952 | 0.115 | 0.959 |

*t=1 split statistics come from the 407,932 retained users with ≥2 observations (a parity split needs both halves non-empty); single-rating users contribute scale but no stability information by construction.

1. **Scale [Observed fact]:** rating mass is insensitive up to t=20 (>92.9% retained) because low-volume users hold few ratings each; user count is the binding cost (100% → 53% at t=10 → 22% at t=50). Full-snapshot reference (lifetime = all phase-2 ratings): t=10 keeps 295,442 users / 97.0% of 26.9M ratings; t=20 keeps 223,069 / 93.3%.

2. **Stability rises smoothly, flattening after t≈20–50 [Empirical finding]:** ICC-style reliability of the user mean goes 0.62 → 0.70 (t=5) → 0.78 (t=10) → 0.85 (t=20) → 0.92 (t=50); per-step gains shrink from ~+0.08 to ~+0.03 after t=50. The game-adjusted severity proxy tracks raw means within ±0.02 throughout. These are within-threshold compositional comparisons (higher t also shifts the pool toward high-n users), not causal effects of forcing more ratings.

3. **The low tail is qualitatively different, not just noisier [Empirical finding], recomputed on the filtered universe:** band-'1' users (107,396) average **8.83** (+2.33 vs the 1,000+ band), with between-user SD **1.70** vs 0.63–0.70 at ≥50 ratings; **45.3%** of their ratings are 10s and **69.4%** are ≥9, versus **1.7%** / **6.4%** among 1,000+-rating users — a distribution-shape difference (mass spike at 10), not merely higher variance. Consistent with the Phase A severity gradient; the pattern matches the full-snapshot bands closely, so it is not an artifact of universe filtering.

4. **Game coverage is non-binding at every threshold [Observed fact]:** even at t=100, 16,344 games retain ≥10 raters (vs 16,406 at t=1). The threshold choice affects per-user statistic quality and taste-analysis sample sizes, not which games remain analyzable at coarse granularity.

### Recommendation

**[Supported decision, model-dependent]** Adopt **t = 10 (≥10 lifetime ratings within the 16,627-game universe)** as the primary analytical user population, with **t = 20** as the high-confidence sensitivity tier:

- t=10 matches the established viability floor for severity estimation (script 18: ICC ≈0.74 in the 10–24 band, treated as estimable; strong at ≥50); here ICC(mean)=0.78, severity proxy 0.79.
- It discards exactly the users whose level cannot be split-validated or whose discernment/taste statistics are undefined or noise-dominated (bands '1'/'2-4'/'5-9' plus part of '10-24'; under filtered-universe counts, t≥20 excludes all full-snapshot bands '1', '2-4', '5-9' by construction).
- Cost is minimal: 96.9% of ratings retained; game coverage unchanged (16,390 games with ≥10 raters).
- Going to t=20 buys +0.07 ICC for 26% of remaining users and 1M more ratings; going to t=50 costs another 12 points of rating mass — reserve t=20 (ICC 0.85) and t=50 (ICC 0.92) as sensitivity tiers rather than the primary.

**Phase 3 availability under the recommended primary (t=10, filtered universe): 289,397 users and 24,558,361 ratings (96.9% of the 25.34M in-universe ratings; 16,390 of 16,567 rated games still have ≥10 retained raters). Sensitivity tier t=20: 217,102 users / 23,547,280 ratings.**

**[Limitation / classification]** This threshold defines where *per-user statistics become statistically usable*; it is NOT a credibility finding — excluded users are not worse raters (AGENTS.md: volume is entangled activity/exposure, and the low-volume level gap is stable additive severity, not error). Their ratings still inform game-level aggregates in pooled analyses; the threshold binds only analyses that condition on per-user quantities (severity estimation, calibration/discernment, taste profiles). Thresholds must always be stated with their lifetime-count definition (filtered-universe counts here; full-snapshot counts would be more inclusive for the same numeric t).

## 2026-08-24: Anomalous / low-informative rater audit on the filtered universe (scripts/25)

**Scope.** All 544,955 raters / 25.3M observations of the 16,627-game filtered universe; per-user rating-distribution shape (scale diversity, near-constancy, modal concentration, binary usage) by lifetime *filtered* count thresholds {1,3,5,10,20,50,100} and Phase 2 volume bands. Definitions and full tables: `docs/phase2-anomalous-audit/SUMMARY.md`; outputs in `data/processed/phase2-audit-anomalous/`. Independent of and concurrent with the lifetime-threshold study.

### Findings

1. **Degenerate rating patterns collapse with history length but leave a persistent heavy-rater tail [Empirical finding]:** `degenerate_strict` (n≥20 AND single-value OR SD<0.2 OR modal≥95%) affects 0.31% of n≥20 users, 0.21% at n≥50, 0.15% at n≥100 — versus ≈0% chance under both null models (uniform 1–10; iid empirical, 200k reps). By band it declines to 0.08% at 250–499 then rises to 0.14% (500–999) / 0.28% (1000+); small absolute counts (~3–7 users), suggestive only.
2. **Tiny-n flagging is uninformative [Method note]:** below n≈10 flags are arithmetic artifacts (24.3% of all users are "single-value" only because n=1); observed n≤5 rates are comparable to or BELOW the iid-empirical null (n≥3 single-value 2.43% vs 4.59% null).
3. **Binary usage is mostly honest small-n grading [Empirical finding]:** among 53,945 exact-two-value users, {9,10}+{8,9}+{8,10} = 62%; extreme {1,10} is 1.83% (985 users, median n=3; only 86 with n≥20). "Binary" alone is not an anomaly class.
4. **Flagged heavy raters rate broadly and popularly, near-constant HIGH [Empirical finding]:** the 667 strict users have median 40 distinct games, median host-game volume 7,927 obs (vs 12,821 for other n≥20 raters), 0.8% niche share, mean rating 9.64 vs 7.38. Not a niche-enthusiasm pattern. Whether this is enthusiasm-plus-selection vs automation/identity multi-rating is NOT identifiable from this data [speculation kept open].
5. **Removal would be negligible at the aggregate level, and nearly so per game [Observed fact]:** strict composite = 667 users / 48.6k obs (0.19% of observations); broad composite = 0.61%. Only 85 of 12,593 touched games get ≥5% of their observations from broad-flagged users (p99 share 4.2%, max 100% for a few tiny games).
6. **Filtered-vs-full count basis barely moves users across thresholds [Observed fact]:** corr(filtered n, full-snapshot n)=0.991; 0 of 121,497 filtered-n≥50 users fall below 50 on the full basis.

### Recommendation

- **Flag, don't exclude, by default:** carry `degenerate_broad`/`degenerate_strict` as sensitivity flags into Phase 3 taste analysis; run one variant excluding the strict composite (n≥20) as a shortlist-stability check.
- The flagged-tail signature (near-constant offset) is the additive rater-level effect severity adjustment already absorbs; exclusion or reliability weighting would double-count an existing correction [model-dependent conclusion].
- Patterns are rare enough to ignore at **n≥50**; worth flagging at n=10–50; uninformative below n=10.
- Interaction with the threshold study (merged, `scripts/23_user_threshold_study.py`, t=10 primary / t=20 sensitivity): no exclusion floor needed from this side. The two recommendations are complementary and consistent: their t=10/t=20 floors sit exactly where this audit finds raw flag rates become interpretable (below n≈10 flags are artifacts; 10–50 worth flagging); at their primary t=10 population (289,397 users), `degenerate_strict`-class contamination is ~0.2–0.3% of users and ≤0.19% of ratings — negligible for pooled game means, and the flags should simply travel with the user table as sensitivity markers.

Open: whether the 1000+ uptick is real needs user-level inspection beyond counts; per-game impact for the 15 games with ≥20% flagged share unchecked game-by-game.

## 2026-08-24: Active analytical extracts for the established population (games × users × degenerate exclusion)

**[Method]** Created `scripts/24_build_active_phase2_extracts.py` (rerunnable, bounded `memory_limit=4GB`/`threads=4`/`temp_directory`, explicit `SEMI JOIN`s verified via `EXPLAIN`, no wide-table positional bug, `ORDER BY rating_observation_id`/`user_pseudouserid`). Rebuilds only user/rating-dependent layers on the fixed 16,627-game research population (`data/processed/bgg_research_population.parquet`, `scripts/01`). Copies needed source parquets once into `scratch/phase2` (full snapshot `rating_observations.parquet` 26.9M, `users.parquet`, `collections.parquet`) and runs via DuckDB. Preserves the two reference areas unchanged: `data/processed/phase2/` (full snapshot, 95,540 games, 26.9M obs) and `data/processed/phase2-filtered/` (16,627 games, 25.3M obs) — the latter not present locally in this worktree but logically reused; game-level reference tables `games`/`game_tags`/`game_links` already filtered there are NOT duplicated here (documented join / symlink if `phase2-filtered` exists). New active sibling is `data/processed/phase2-active/` (gitignored via `data/processed/`; `docs/phase2-active/` holds the committed catalog copy).

**Population definition (games × users × exclusion) [Method / Supported decision]:**
- **Games:** 16,627 research population (corrected per `findings.md` refresh; 16,567 have ≥1 rating in this SQLite snapshot [Observed fact]).
- **Users (active):** `cnt_filtered = COUNT(*) WHERE game_id IN population` (canonical `rating_observations`, no dedup, source keys retained) with **t=10 primary** (`cnt_filtered ≥10`). Threshold t=10 comes from `scripts/23_user_threshold_study.py` / `reports/user_population_thresholds.*` (ICC reliability 0.78 at t=10 vs 0.85 at t=20; 289,397 users / 24,558,361 ratings before exclusion [Observed fact from threshold study]).
- **Exclusion:** `degenerate_strict` per `scripts/25_phase2_anomalous_rater_audit.py`: `n≥20` AND (`k==1` single bin OR `SD<0.2` raw OR `modal_share≥0.95` on `ROUND` rating clipped to [1,10]). This is the heavy-rater near-constant/high, low scale-diversity tail — treated as **low-information / degenerate noise, not fake/malicious classification** [Assumption / Method]. Strict = 667 users / 48,573 obs (0.307% at n≥20, 0.19% of filtered obs [Observed fact from audit, recomputed here: 667 / 48,573]).
- **Preserved for sensitivity:** `degenerate_broad` (`n≥10` AND (`k≤2` OR `SD<0.5` OR `modal≥0.90`)) is **NOT excluded**; kept as `is_degenerate_broad` column in the active user table (3,992 broad users total; 3,326 retained in active [Observed fact]). Single parameter change (`is_degenerate_broad` filter) gives the sensitivity variant.

Semi-join logic (canonical, no duplication/drop):
```
-- active observations
SELECT r.* FROM rating_observations r
  SEMI JOIN pop p ON p.game_id = r.game_id
  SEMI JOIN active_users a ON a.user_pseudouserid = r.user_pseudouserid
```

**Outputs [Observed fact]:**
- `data/processed/phase2-active/rating_observations_active.parquet` — 24,509,788 canonical observations (ORDER BY rating_observation_id)
- `data/processed/phase2-active/users_active.parquet` — 288,730 rows, one per retained user: original `users.parquet` fields plus `cnt_filtered`, `is_degenerate_strict` (all FALSE), `is_degenerate_broad`, and binned stats (`filtered_mean_rating`, `filtered_sd_rating`, `filtered_modal_share`, `filtered_n_bins_used`, `filtered_entropy_bits`)
- `data/processed/phase2-active/collections_active.parquet` — 25,889,485 collection/status rows for population games × active users
- `data/processed/phase2-active/validation.json`, `extract_counts.json`, `parquet_catalog.csv`, `README.md` (source-extract/ filter documentation; catalog extends `docs/phase2-filtered/PARQUET_CATALOG.md` style with an “active” column; committed copy at `docs/phase2-active/`)

**Counts and coverage [Observed fact / Empirical finding]:**
- Filtered reference (16,627 games): 25,335,220 obs, 544,955 users with ≥1 filtered rating; 16,567 distinct games with ≥1 rating.
- Before degenerate exclusion (t≥10 on filtered counts): 289,397 users, 24,558,361 ratings (96.93% of filtered ratings [Observed fact]; recomputed exactly here, matches threshold study).
- **Active (t≥10 minus strict): 288,730 users / 24,509,788 observations** [Observed fact] — exactly 667 users / 48,573 obs removed (0.23% of users, 0.20% of pre-exclusion ratings). Shares vs filtered: 96.74% of filtered obs, 52.98% of filtered users; vs full snapshot (26,924,709 obs, 571,248 rating users): 91.03% of full obs, 50.54% of full rating users.
- Game coverage: 16,564 distinct games have ≥1 active rating (99.98% of 16,567 filtered games; **3 games lost** [Observed fact] — essentially none at coarse granularity; even at t=100, 16,344 games retain ≥10 raters, so threshold is not game-binding).
- Collections active retains 93.85% of filtered collections (25,889,485 / 27,584,966) and 87.41% of full.
- Repeated user-game pairs preserved as distinct observations: 1,435 pairs / 2,962 obs, max 4 per pair [Observed fact] (vs 1,465 / 3,022 in filtered).

**Validations passed [Observed fact]:**
- 0 violations: every retained `game_id` is in the 16,627 set (ANTI JOIN pop = 0).
- 0 violations: every retained user has `cnt_filtered ≥10` before exclusion (min 10) and 0 with `cnt_filtered <10` post.
- 0 violations: no retained user is `degenerate_strict`; 0 strict observations in active.
- Flag source validated: degenerate counts recomputed here (667 strict, 3,993 broad) match the committed `reports/anomalous_rater_audit/audit_summary.json` + `removal_sensitivity.csv` (strict 667, broad 3,992/3,993 rounding) [Empirical finding].
- Output rows anchored: filtered anchor `SEMI JOIN pop` = 25,335,220; active rows = filtered t≥10 minus strict by construction.

**Where `degenerate_broad` is kept [Method]:** column `is_degenerate_broad` in `users_active.parquet` (3,326 TRUE among active). Full-snapshot fit artifacts (`rater_stats`, `user_severity`, `game_adjusted_means`, scripts 15–22) remain historical reference for the full universe — not mixed with filtered/active observations; re-estimation on the active universe is the follow-up taste task's deliverable (not done here). `postdate`/`rating_tstamp` semantics remain unresolved — dual readings preserved where applicable.

**No Phase 2 statistical re-analysis, no change to the 16,627-game population** [Method note]. The 60 population games absent from the SQLite snapshot (recent high-game_id releases) remain absent here as well — snapshot mismatch, not a filter loss.

**Reproduce:** `python scripts/24_build_active_phase2_extracts.py --input-dir scratch/phase2 --population scratch/phase2/bgg_research_population.parquet` (bounded memory, rerunnable; `docs/phase2-active/README.md` records exact invocation + source paths).

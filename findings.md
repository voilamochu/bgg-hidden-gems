# Findings Log

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

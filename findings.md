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

1. **The actual friend output is not present in the current repo [Observed Fact / Blocker]:** neither file contains a `debiased_rating` field, any field with a debias/friend label, or a separate friend-ranking file. The raw file has **34 columns** and the processed research population has **36 columns**; the available `dump_*` columns are `dump_rank`, `dump_geek_rating`, `dump_avg_rating`, `dump_voters`, and `dump_year`. `dump_geek_rating` is treated as a legacy BGG rating field, not substituted for the missing friend result.

   Consequently, this dataset cannot currently answer which games the friend’s result promoted or demoted, how the correction differed from `avg_rating_current` or `bayes_rating`, or whether the correction varied by volume, year, complexity, category, or mechanic. Those comparisons require the friend's game-level output matched by `game_id`.

### Do the `dump_*` fields support a temporal comparison?

2. **The current scrape has a timestamp, but the dump does not [Observed Fact]:** `attrs_fetched_at` ranges from **2026-08-12 03:28:48 UTC to 2026-08-12 12:02:25 UTC** in the raw file, with **160,167 unique timestamps**. There is no collection date, timestamp, or provenance field for the `dump_*` values. The dump may be an earlier/legacy snapshot, but its date and exact construction are not established.

3. **Voter counts are strongly consistent with an earlier BGG snapshot [Empirical Finding / Qualified Interpretation]:** in the 16,634-game research-population overlap, current `users_rated` and `dump_voters` have correlation **0.995**. Current counts exceed dump counts for **96.3%** of games, with median difference **+24**; the 10th and 90th percentiles are **+3** and **+365**. The direction is especially clear at higher current volumes: median differences are **+7** for games with 100–199 current ratings, **+210.5** for 2.5k–5k, and **+2,591** for 25k+; current counts are higher for **100.0%** of the 5k+ groups. This is strong evidence that `dump_voters` is a prior or legacy count for much of the retained population, but it is not proof without a dump timestamp.

4. **Other paired fields changed in both directions [Observed Fact]:** current average rating is below `dump_avg_rating` for **67.4%** of the overlap, with median current-minus-dump change **−0.0123**; current Bayesian rating is below `dump_geek_rating` for **60.9%**, with median change **−0.0022**. Current numeric rank is higher than `dump_rank` for **86.6%** (a worse rank number), with median change **+631**. These changes are compatible with a later BGG snapshot, but they are ordinary same-platform rating/popularity changes, not an independent evaluation.

5. **Release year is not useful temporal evidence [Observed Fact]:** `year` and `dump_year` agree for **98.8%** of paired research-population records. The remaining differences include implausible large discrepancies (minimum **−27**, maximum **+962** years), indicating parsing, missing-value, or record-quality problems rather than a meaningful release-time series.

6. **The comparison is descriptive, not a leakage-safe temporal validation [Limitation]:** without the dump date and a defined cutoff, we cannot establish that every dump value predates every current value or that the fields were computed from disjoint information. Even if the dump is earlier, it is still the same BGG platform and overlapping selection process. It can show within-platform change in counts or ratings, but not out-of-time generalization, independent audience reach, or causal effect of a correction. Treating `dump_*` as a pre-treatment predictor or validation target would be unsafe until provenance and collection dates are supplied.

### What can be said about the friend's correction?

7. **No promoted/demoted games or game-type pattern is identifiable yet [Supported Conclusion]:** because `debiased_rating` is absent, there is no observed correction to calculate as `debiased_rating - avg_rating_current` or `debiased_rating - bayes_rating`. Any list of promoted or demoted games, or any claim that the correction favors low-volume, older, complex, reimplemented, card, party, wargame, or other types, would require inventing an output or incorrectly relabeling `dump_geek_rating`.

8. **`dump_geek_rating` cannot stand in for the friend's score [Supported Conclusion]:** it is highly correlated with current `bayes_rating` (**r=0.983**, n=16,280) and is explicitly named as a legacy Geek Rating field. That makes it useful for the snapshot audit above, but not evidence about a separate debiasing rule. The available data can describe BGG's own current-versus-legacy changes; it cannot characterize the friend's ranking behavior.

### Limitations and implications for a richer dataset

- The exact origin, date, and calculation context of all `dump_*` fields are undocumented. Their value differences support a provisional “earlier/legacy snapshot” interpretation, not a verified temporal panel.
- The processed population has already applied filters and a 100-rating floor. Snapshot changes and field availability may differ outside that population; raw-file comparisons also contain malformed or extreme paired differences.
- Game-level aggregates cannot reveal whether a rating-count increase came from new audiences, existing hobbyist audiences, duplicate accounts, or changes in BGG participation. No user-level debiasing claim is tested here.
- To analyze the friend result later, retain a versioned table keyed by `game_id` containing `debiased_rating`, computation date, method/version metadata, universe and missing-value rules, plus the current and historical BGG fields used for comparison.
- To evaluate the underlying method in a later richer dataset, preserve pseudonymous user-game ratings, rating timestamps, user history/participation context, and—if the hidden-gem question remains in scope—independent exposure or audience-segment information. Those data would enable a separate methodology audit; they are not available now.

**Implication [Implication]:** the friend's ranking remains an unobserved baseline in this repository. The defensible result from the current data is limited to a provisional audit of the likely legacy BGG snapshot and a clear record of what is missing. Do not interpret `dump_geek_rating` as debiased, and do not use current-versus-dump differences as validation of the friend's method.

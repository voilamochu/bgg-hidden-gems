# Outcome Category Breakdown — Step 11-12

**Generated:** 2026-08-25T12:00:50.812242+00:00Z · seed 20260824
**Starting:** 532 pool → hiddenness eligible+borderline 505 screened (excluded 27 not hidden) + 16 flagged popular_via_users
**Rule:** No combined hidden-gem score — one column per evidence dimension, auditable mapping (see `screening_evidence_table.csv` and §4 `pass1_failure_mode_audit.md`).

## Counts per outcome (full 532 including excluded)

| outcome_category | count | share of 532 | description |
|---|---|---|---|
| strong_hidden_gem_evidence | 39 | 7.3% | good + underrated + genuinely hidden + no material audience-selection concern, supporting cross-audience where available |
| plausible_hidden_gem | 176 | 33.1% | good + underrated + hidden, but some evidence incomplete/borderline (hiddenness borderline, or one audience dimension borderline, or SE lower bound dips) |
| niche_but_high_quality | 163 | 30.6% | good + underrated but audience-selection suggests niche-dependent (high specialist share, cross drop, propensity sensitivity, or Q4Fam fragility) |
| insufficient_evidence | 127 | 23.9% | may qualify otherwise but cannot establish hidden/broad-appeal confidently (low n wide SE, insufficient_overlap, broad-appeal unavailable) |
| excluded_popular_not_hidden | 27 | 5.1% | hiddenness exclude >2500 (not hidden) — not counted as hidden gem |

**Screened eligible+borderline (505) breakdown (excluding 27 popular):**

| outcome_category | count | share of screened |
|---|---|---|
| strong_hidden_gem_evidence | 39 | 7.7% |
| plausible_hidden_gem | 176 | 34.9% |
| niche_but_high_quality | 163 | 32.3% |
| insufficient_evidence | 127 | 25.1% |

## Distributions per category (screened subset)

| category | median n_obs | median adj_mean | median resid_Q3bFam | median resid_Q4Fam | median SE | median lower_bound_adj |
|---|---|---|---|---|---|
| strong_hidden_gem_evidence | 405 | 8.08 | 0.96 | 0.91 | 0.059 | 7.93 |
| plausible_hidden_gem | 382 | 7.91 | 0.94 | 0.93 | 0.061 | 7.80 |
| niche_but_high_quality | 321 | 8.13 | 0.97 | 0.93 | 0.067 | 7.97 |
| insufficient_evidence | 123 | 8.02 | 0.96 | 0.95 | 0.108 | 7.80 |

## Examples per category

### strong_hidden_gem_evidence (39) — top by resid

| game_id | title | year | n_obs | adj_mean | resid_Q3bFam | resid_Q4Fam | taxonomy | overlap | cross |
|---|---|---|---|---|---|---|---|
| 2470 | The Extraordinary Adventures of Baron Munchau | 1998.0 | 379 | 7.54 | 1.68 | 1.60 | moderate_audience_selectivity | borderline_overlap | broad_support_non_specialists_high |
| 62814 | Tumblin-Dice Medium | 2008.0 | 215 | 7.61 | 1.53 | 1.50 | low_audience_selectivity | borderline_overlap | broad_consistent_small_diff |
| 275972 | Star Trek: Alliance – Dominion War Campaign | 2021.0 | 193 | 8.59 | 1.34 | 1.32 | moderate_audience_selectivity | borderline_overlap | broad_support_non_specialists_high |
| 244258 | The Red Dragon Inn 7: The Tavern Crew | 2018.0 | 310 | 7.86 | 1.31 | 1.41 | moderate_audience_selectivity | adequate_overlap | broad_support_non_specialists_high |
| 340216 | Heredity: The Book of Swan | 2023.0 | 176 | 8.63 | 1.25 | 1.14 | moderate_audience_selectivity | borderline_overlap | broad_support_non_specialists_high |
| 373835 | Unlock! Kids: Stories from the Past | 2022.0 | 252 | 8.08 | 1.21 | 1.12 | moderate_audience_selectivity | borderline_overlap | broad_consistent_small_diff |
| 319604 | Ricochet: A la poursuite du Comte courant | 2020.0 | 223 | 7.74 | 1.17 | 1.11 | moderate_audience_selectivity | borderline_overlap | broad_support_non_specialists_high |
| 252432 | Zoo Break | 2019.0 | 178 | 7.97 | 1.13 | 1.11 | moderate_audience_selectivity | borderline_overlap | broad_support_non_specialists_high |
| 153498 | Kamisado Max | 2014.0 | 155 | 7.60 | 1.12 | 1.10 | low_audience_selectivity | adequate_overlap | broad_consistent_small_diff |
| 41090 | Magnate | 2008.0 | 210 | 7.68 | 1.12 | 1.10 | moderate_audience_selectivity | borderline_overlap | broad_support_non_specialists_high |

### plausible_hidden_gem (176) — sample

| game_id | title | year | n_obs | adj_mean | resid | q4 | hidden | taxonomy | sens | reason |
|---|---|---|---|---|---|---|---|---|---|---|
| 4385 | A Gamut of Games | 1969.0 | 434 | 8.07 | 1.95 | 1.96 | eligible | moderate_audien | stable_under | plausible: passes quality 8.07 resid 1.95 hidden eligible n  |
| 1803 | Zopp | 1997.0 | 158 | 7.67 | 1.75 | 1.72 | eligible | moderate_audien | moderately_s | plausible: passes quality 7.67 resid 1.75 hidden eligible n  |
| 341489 | Carrooka | 2021.0 | 195 | 8.55 | 1.75 | 1.73 | eligible | low_audience_se | moderately_s | plausible: passes quality 8.55 resid 1.75 hidden eligible n  |
| 541 | Das Motorsportspiel | 1995.0 | 381 | 7.88 | 1.67 | 1.86 | eligible | moderate_audien | stable_under | plausible: passes quality 7.88 resid 1.67 hidden eligible n  |
| 6688 | Ninety-Nine | 1974.0 | 554 | 7.89 | 1.60 | 1.61 | eligible | moderate_audien | stable_under | plausible: passes quality 7.89 resid 1.60 hidden eligible n  |
| 156372 | Heart of Crown: Fairy Garden | 2013.0 | 304 | 8.44 | 1.58 | 1.50 | eligible | moderate_audien | stable_under | plausible: passes quality 8.44 resid 1.58 hidden eligible n  |
| 14188 | Bughouse Chess | 1960.0 | 362 | 7.93 | 1.57 | 1.54 | eligible | low_audience_se | stable_under | plausible: passes quality 7.93 resid 1.57 hidden eligible n  |
| 2981 | Breaking Away | 1991.0 | 460 | 7.88 | 1.54 | 1.51 | eligible | moderate_audien | moderately_s | plausible: passes quality 7.88 resid 1.54 hidden eligible n  |
| 161880 | The Quiet Year | 2013.0 | 406 | 7.93 | 1.53 | 1.47 | eligible | low_audience_se | moderately_s | plausible: passes quality 7.93 resid 1.53 hidden eligible n  |
| 165748 | Psycho Raiders | 2014.0 | 197 | 8.27 | 1.52 | 1.41 | eligible | moderate_audien | stable_under | plausible: passes quality 8.27 resid 1.52 hidden eligible n  |
| 207951 | Tintas | 2016.0 | 312 | 8.11 | 1.51 | 1.48 | eligible | moderate_audien | stable_under | plausible: passes quality 8.11 resid 1.51 hidden eligible n  |
| 141067 | History Maker Baseball | 2013.0 | 207 | 8.23 | 1.50 | 1.37 | eligible | moderate_audien | moderately_s | plausible: passes quality 8.23 resid 1.50 hidden eligible n  |

### niche_but_high_quality (163) — sample

| game_id | title | year | n_obs | adj_mean | resid | q4 | spec_ge20 | taxonomy | propensity | cross |
|---|---|---|---|---|---|---|---|---|---|---|
| 33434 | Funkenschlag: EnBW | 2007.0 | 198 | 8.69 | 1.90 | 1.77 | 0.86 | high_audienc | strongly_sen | mixed_large_heteroge |
| 97683 | Age of Rail: South Africa | 2011.0 | 277 | 8.73 | 1.78 | 1.72 | 0.97 | high_audienc | strongly_sen | mixed_large_heteroge |
| 186279 | Finska Mini | 2011.0 | 468 | 7.82 | 1.76 | 1.81 | 0.74 | high_audienc | strongly_sen | broad_support_non_sp |
| 188530 | My Favourite Things | 2015.0 | 375 | 7.90 | 1.65 | 1.65 | 0.79 | high_audienc | strongly_sen | broad_support_non_sp |
| 261588 | Ascension: Year Five Collector's Edition | 2019.0 | 107 | 8.34 | 1.54 | 1.43 | nan | insufficient | insufficient | mixed_large_heteroge |
| 241203 | Ascension: Year Four Collector's Edition | 2017.0 | 122 | 8.18 | 1.53 | 1.43 | nan | insufficient | insufficient | mixed_large_heteroge |
| 2794 | Spinball | 2001.0 | 171 | 7.51 | 1.50 | 1.48 | nan | moderate_aud | strongly_sen | mixed_large_heteroge |
| 275626 | Dominion: Einsteiger-Bigbox | 2019.0 | 114 | 8.36 | 1.50 | 1.43 | nan | insufficient | insufficient | mixed_large_heteroge |
| 383010 | Clank! Legacy 2: Acquisitions Incorporat | 2024.0 | 234 | 9.38 | 1.49 | 1.32 | 0.01 | moderate_aud | strongly_sen | broad_support_non_sp |
| 165332 | Puerto Rico | 2007.0 | 117 | 8.19 | 1.42 | 1.36 | 0.57 | insufficient | insufficient | mixed_large_heteroge |
| 345976 | System Gateway (fan expansion for Androi | 2021.0 | 660 | 9.45 | 1.37 | 1.47 | nan | moderate_aud | stable_under | mixed_moderate |
| 21358 | Savage Worlds | 2003.0 | 173 | 8.25 | 1.34 | 1.37 | 0.51 | moderate_aud | strongly_sen | broad_support_non_sp |

### insufficient_evidence (127) — sample

| game_id | title | year | n_obs | SE | taxonomy | overlap | n_supported_ge10 | cross | reason |
|---|---|---|---|---|---|---|---|---|---|
| 249768 | My First Adventure: Finding the Dragon | 2018.0 | 100 | 0.119 | insufficient | insufficient_overlap | 1 | broad_consistent_s | insufficient_evidence: taxonomy insufficient_evidence + |
| 401168 | nana: Christmas Edition | 2022.0 | 100 | 0.119 | insufficient | insufficient_overlap | 1 | broad_consistent_s | insufficient_evidence: taxonomy insufficient_evidence + |
| 286358 | Commands & Colors Tricorne: Jacobite Ris | 2020.0 | 100 | 0.119 | insufficient | insufficient_overlap | 2 | mixed_large_hetero | insufficient_evidence: taxonomy insufficient_evidence + |
| 26736 | Ukraine '44 | 2006.0 | 100 | 0.119 | insufficient | insufficient_overlap | 2 | mixed_moderate | insufficient_evidence: taxonomy insufficient_evidence + |
| 188885 | Grasse: Mestres Perfumistas | 2018.0 | 101 | 0.119 | insufficient | insufficient_overlap | 5 | niche_drop_signifi | insufficient_evidence: taxonomy insufficient_evidence + |
| 279886 | Iron Forest | 2024.0 | 101 | 0.119 | insufficient | insufficient_overlap | 2 | mixed_large_hetero | insufficient_evidence: taxonomy insufficient_evidence + |
| 295604 | Rangers of Shadow Deep: Standard Edition | 2020.0 | 101 | 0.119 | insufficient | insufficient_overlap | 6 | broad_support_non_ | insufficient_evidence: taxonomy insufficient_evidence + |
| 83283 | Volo | 2010.0 | 101 | 0.119 | insufficient | insufficient_overlap | 2 | mixed_large_hetero | insufficient_evidence: taxonomy insufficient_evidence + |
| 351869 | Adventure Games: Expedition Azcana | 2022.0 | 101 | 0.119 | insufficient | insufficient_overlap | 2 | broad_consistent_s | insufficient_evidence: taxonomy insufficient_evidence + |
| 170472 | Prelude to Rebellion: Mobilization & Unr | 2018.0 | 102 | 0.118 | insufficient | insufficient_overlap | 2 | mixed_moderate | insufficient_evidence: taxonomy insufficient_evidence + |
| 136890 | Hold the Line:  Frederick's War | 2013.0 | 102 | 0.118 | insufficient | insufficient_overlap | 2 | mixed_large_hetero | insufficient_evidence: taxonomy insufficient_evidence + |
| 202265 | Chicago & NorthWestern | 2016.0 | 102 | 0.118 | insufficient | insufficient_overlap | 2 | mixed_large_hetero | insufficient_evidence: taxonomy insufficient_evidence + |

### excluded_popular_not_hidden (27)

| game_id | title | n_obs | users_rated | adj_mean | rank |
|---|---|---|---|---|---|
| 118 | Modern Art | 23096 | 25690 | 7.89 | 222.0 |
| 92828 | Dixit: Odyssey | 21146 | 23119 | 7.59 | 357.0 |
| 5 | Acquire | 20432 | 22332 | 7.66 | 367.0 |
| 46213 | Telestrations | 18877 | 20944 | 7.65 | 354.0 |
| 215 | Tichu | 15687 | 16985 | 7.96 | 251.0 |
| 220 | High Society | 14540 | 16848 | 7.57 | 535.0 |
| 150 | PitchCar | 11175 | 11831 | 7.62 | 531.0 |
| 266507 | Clank! Legacy: Acquisitions Incorporated | 9745 | 11489 | 8.83 | 28.0 |
| 397598 | Dune: Imperium – Uprising | 8869 | 19653 | 9.05 | 5.0 |
| 3201 | Lord of the Rings: The Confrontation | 6909 | 7238 | 7.55 | 811.0 |

## Interpretation

- **Strong** should be few and well-supported — here 39 qualifies under strict rule (eligible + LB>=7.0 + Q4>=0.60 + taxonomy low/moderate + overlap adequate/borderline + cross broad). If this is <10 or >500, flag per task.
- **Plausible** larger (176) allows borderline hiddenness or one dimension borderline — these need further external validation (plays/sales) before claiming broad appeal.
- **Niche** vs **Insufficient** separated: niche has evidence of specialist dependence (high spec, Q4 fragile, propensity strongly sensitive, cross niche_drop); insufficient lacks evidence to judge (small n + insufficient_overlap + no cross).

**Reproduce:** `python scripts/51_step11-12_hidden_gem_screen.py`

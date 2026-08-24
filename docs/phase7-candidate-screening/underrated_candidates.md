# Underrated Candidates (INTERMEDIATE / NOT FINAL RESEARCH OUTPUTS)

> **Status:** INTERMEDIATE screening — not a hidden-gem ranking. Residual is `Q3b/OLS` model-dependent conditional anomaly (`adj − expected`), with `SE=1.194/√n` and `post_SD=1/√(1/0.746+n/1.426)`. Do not treat magnitude without evidence strength. All 16549 estimation games are in `underrated_candidates.csv` with `screening_disposition`.

## Summary counts (see `screening_summary.json`)

- **Broad pool** (`n≥100` & `resid>0`): **7754** (resid>0.2 → 5131; top 5% `≥0.83` → 748; median resid +0.02, P95 +0.86, n median 293 P10 100 P90 2796)
- **Robust subset** (`n≥200 & resid≥0.60 & min_alt≥0.30 & z≥5 & year<2025`): **910** (plus 530 meeting criteria but flagged as widely established; see disposition)
- **Excluded / flagged:** unreleased 361, duplicate title 206, shadowed 136, wellknown 530, low evidence 1272, not underrated 6800
- **Estimation sample:** 16549 games (16,627 population minus 15 with missing weight/playtime; 1,612 sub-100 games retained but excluded from broad/robust per floor)

### How to read disposition
- `robust_underrated` — passes robust rule explicitly above; strong positive conditional anomaly with rating-volume evidence and cross-spec stability; proceed to `broad_appeal_evidence.md` for separate broad-appeal assessment (not scored).
- `flagged_wellknown` — would be robust but `users_rated≥20000` or `rank<500` (widely established/popularity premium territory) — conflicts with hidden-gem objective; keep for audit, separately flag.
- `broad_positive_gt02` / `broad_positive` — `n≥100` & `resid>0.2` / `>0` — positive residual with at-least P10 evidence, but not large+stable enough for robust.
- `flagged_duplicate_title` / `flagged_shadowed_by_more_popular_related` — multiple records same underlying game (title_clean duplicate or reimplementation/version with 4× users); keep more popular, flag less popular.
- `excluded_unreleased` / `excluded_low_evidence` / `not_underrated` — see `exclusions_and_deduplication.md` for per-game reason with `n, SE, z, post_SD`.

## A. Broad pool — top 50 of 7754 by residual (full 7754 in CSV)

Threshold: `n≥100` (P10, SE≤0.119) and `resid>0`. Also reporting tiers: `>0.2` → 5131, top5% `≥0.828` → 748. See `underrated_candidates.csv` for all 7754 rows sorted by `screening_disposition` then residual. Below is top 50 excerpt sorted by `underratedness_pref` desc.

| game_id | title | year | n | SE | post_SD | z | adj | E[adj] | resid | min_alt | decile | users | rank | reimpl | cats | disp |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 255249 | Monikers: More Monikers | 2018 | 452 | 0.056 | 0.056 | 40.5 | 8.58 | 6.30 | 2.27 | 2.18 | D7 | 521 | 3227 | — | Card Game; Humor; Mature / Adult | robust_underrated |
| 140135 | Small World Designer Edition | 2015 | 246 | 0.076 | 0.076 | 28.9 | 9.10 | 6.90 | 2.20 | 2.17 | D5 | 266 | — | — | Civilization; Fantasy; Territory | robust_underrated |
| 179448 | Monikers: Shmonikers | 2015 | 319 | 0.067 | 0.067 | 30.7 | 8.30 | 6.24 | 2.05 | 1.87 | D6 | 326 | 4747 | — | Party Game | robust_underrated |
| 195709 | Monikers: Something Something | 2016 | 246 | 0.076 | 0.076 | 26.6 | 8.33 | 6.30 | 2.03 | 1.86 | D5 | 255 | 5504 | — | Party Game | robust_underrated |
| 221248 | Monikers: The Shut Up & Sit Down Nonsens | 2017 | 465 | 0.055 | 0.055 | 36.0 | 8.36 | 6.36 | 1.99 | 1.75 | D7 | 484 | 3607 | — | Party Game | robust_underrated |
| 120269 | Red White & Blue Racin': Stock Car Actio | 2012 | 133 | 0.104 | 0.103 | 19.2 | 8.45 | 6.46 | 1.99 | 1.88 | D3 | 185 | 7033 | — | Racing; Sports | broad_positive_gt02 |
| 283152 | Monikers: Serious Nonsense | 2019 | 500 | 0.053 | 0.053 | 36.2 | 8.48 | 6.55 | 1.94 | 1.96 | D7 | 609 | 2928 | — | Humor; Mature / Adult; Party Gam | robust_underrated |
| 36553 | Time's Up! Title Recall! | 2008 | 3629 | 0.020 | 0.020 | 97.3 | 8.03 | 6.10 | 1.93 | 1.68 | D10 | 3787 | 731 | — | Humor; Movies / TV / Radio theme | robust_underrated |
| 283151 | Monikers: Classics | 2019 | 263 | 0.074 | 0.073 | 26.1 | 8.45 | 6.52 | 1.92 | 1.79 | D5 | 343 | — | — | Party Game | robust_underrated |
| 4385 | A Gamut of Games | 1969 | 434 | 0.057 | 0.057 | 33.5 | 8.08 | 6.16 | 1.92 | 1.85 | D7 | 445 | — | — | Abstract Strategy; Book; Card Ga | robust_underrated |
| 230262 | Time's Up! Party Edition | 2004 | 553 | 0.051 | 0.051 | 36.7 | 7.91 | 6.05 | 1.86 | 1.83 | D7 | 714 | 3245 | — | Humor; Party Game | robust_underrated |
| 33434 | Funkenschlag: EnBW | 2007 | 198 | 0.085 | 0.084 | 21.8 | 8.70 | 6.85 | 1.85 | 1.71 | D4 | 202 | 6060 | — | Economic; Industry / Manufacturi | broad_positive_gt02 |
| 24996 | Start Player: A Kinda Collectible Card G | 2006 | 181 | 0.089 | 0.088 | 20.8 | 7.04 | 5.19 | 1.84 | 1.76 | D4 | 192 | 11130 | — | Card Game; Collectible Component | broad_positive_gt02 |
| 4657 | Replay Baseball | 1973 | 105 | 0.117 | 0.115 | 15.4 | 7.97 | 6.18 | 1.79 | 1.81 | D2 | 135 | 9064 | — | Card Game; Sports | broad_positive_gt02 |
| 1803 | Zopp | 1997 | 158 | 0.095 | 0.094 | 18.7 | 7.67 | 5.90 | 1.77 | 1.63 | D3 | 160 | 8853 | — | Action / Dexterity | broad_positive_gt02 |
| 57660 | Time's Up! Edición Azul | 2006 | 1365 | 0.032 | 0.032 | 54.4 | 7.68 | 5.92 | 1.76 | 1.50 | D9 | 1463 | 2142 | — | Humor; Movies / TV / Radio theme | robust_underrated |
| 341489 | Carrooka | 2021 | 195 | 0.086 | 0.085 | 20.4 | 8.56 | 6.81 | 1.75 | 1.62 | D4 | 285 | 5331 | — | Action / Dexterity; Sports | broad_positive_gt02 |
| 331953 | Unlock!: Timeless Adventures – Verloren  | 2019 | 132 | 0.104 | 0.103 | 16.7 | 8.39 | 6.66 | 1.73 | 1.69 | D3 | 160 | 7624 | — | Card Game; Exploration; Puzzle;  | broad_positive_gt02 |
| 186279 | Finska Mini | 2011 | 468 | 0.055 | 0.055 | 31.3 | 7.82 | 6.09 | 1.73 | 1.53 | D7 | 566 | 4068 | — | Action / Dexterity; Party Game | robust_underrated |
| 97683 | Age of Rail: South Africa | 2011 | 277 | 0.072 | 0.071 | 24.1 | 8.73 | 7.00 | 1.73 | 1.60 | D5 | 605 | 3481 | — | Economic; Trains; Transportation | robust_underrated |
| 147170 | El Grande Decennial Edition | 2006 | 978 | 0.038 | 0.038 | 45.1 | 8.78 | 7.05 | 1.72 | 1.53 | D8 | 1063 | — | — | Medieval; Political | robust_underrated |
| 8939 | Der wahre Walter | 1989 | 170 | 0.092 | 0.091 | 18.7 | 7.44 | 5.72 | 1.72 | 1.52 | D4 | 182 | 8628 | — | Party Game | broad_positive_gt02 |
| 249768 | My First Adventure: Finding the Dragon | 2018 | 100 | 0.119 | 0.118 | 14.3 | 7.79 | 6.09 | 1.71 | 1.68 | D1 | 128 | 9943 | — | Book; Children's Game; Explorati | broad_positive_gt02 |
| 541 | Das Motorsportspiel | 1995 | 381 | 0.061 | 0.061 | 26.6 | 7.89 | 6.26 | 1.63 | 1.53 | D6 | 399 | 5127 | — | Racing; Real-time; Sports | robust_underrated |
| 351600 | Mortum: Medieval Detective – The Shelter | 2022 | 131 | 0.104 | 0.104 | 15.6 | 8.49 | 6.86 | 1.62 | 1.53 | D3 | 176 | 7116 | — | Adventure; Deduction; Fantasy | broad_positive_gt02 |
| 2470 | The Extraordinary Adventures of Baron Mu | 1998 | 379 | 0.061 | 0.061 | 26.4 | 7.55 | 5.92 | 1.62 | 1.38 | D6 | 402 | 5572 | — | Adventure; Novel-based; Party Ga | robust_underrated |
| 23421 | 1832: The South | 2006 | 125 | 0.107 | 0.106 | 14.9 | 8.77 | 7.18 | 1.60 | 1.55 | D2 | 131 | 8590 | — | Economic; Trains; Transportation | broad_positive_gt02 |
| 188530 | My Favourite Things | 2015 | 375 | 0.062 | 0.062 | 25.8 | 7.90 | 6.31 | 1.59 | 1.53 | D6 | 1039 | 3091 | — | Card Game; Deduction; Humor; Par | robust_underrated |
| 142132 | Dominion: Big Box | 2011 | 106 | 0.116 | 0.115 | 13.7 | 8.26 | 6.67 | 1.59 | 1.44 | D2 | 111 | — | — | Card Game; Medieval | flagged_duplicate_title |
| 6688 | Ninety-Nine | 1974 | 554 | 0.051 | 0.051 | 31.3 | 7.89 | 6.30 | 1.59 | 1.61 | D7 | 616 | 4287 | — | Card Game | robust_underrated |
| 7935 | 1844: Schweiz | 2003 | 212 | 0.082 | 0.082 | 19.2 | 8.94 | 7.37 | 1.57 | 1.53 | D4 | 221 | 5973 | — | Economic; Trains | robust_underrated |
| 14188 | Bughouse Chess | 1960 | 362 | 0.063 | 0.063 | 24.9 | 7.93 | 6.37 | 1.56 | 1.53 | D6 | 377 | 5581 | — | Abstract Strategy | robust_underrated |
| 46158 | Time's Up! Academy | 2009 | 575 | 0.050 | 0.050 | 31.4 | 7.67 | 6.11 | 1.56 | 1.51 | D7 | 630 | 4036 | — | Humor; Party Game | robust_underrated |
| 260234 | Middle-Earth Strategy Battle Game: Rules | 2018 | 144 | 0.100 | 0.099 | 15.7 | 8.85 | 7.29 | 1.56 | 1.53 | D3 | 165 | 6655 | — | Fantasy; Miniatures; Movies / TV | broad_positive_gt02 |
| 62814 | Tumblin-Dice Medium | 2008 | 215 | 0.081 | 0.081 | 19.1 | 7.62 | 6.06 | 1.56 | 1.39 | D4 | 233 | 7196 | — | Action / Dexterity; Dice | robust_underrated |
| 156372 | Heart of Crown: Fairy Garden | 2013 | 305 | 0.068 | 0.068 | 22.8 | 8.43 | 6.88 | 1.56 | 1.53 | D6 | 350 | 4946 | — | Card Game; Fantasy | robust_underrated |
| 38713 | Time's Up! Edición Amarilla | 2008 | 1622 | 0.030 | 0.030 | 52.1 | 7.78 | 6.23 | 1.55 | 1.47 | D9 | 1950 | 1550 | — | Humor; Party Game | robust_underrated |
| 4485 | Hotel Life | 1989 | 139 | 0.101 | 0.101 | 15.2 | 7.71 | 6.17 | 1.54 | 1.49 | D3 | 143 | 9587 | — | Economic; Humor | broad_positive_gt02 |
| 2794 | Spinball | 2001 | 171 | 0.091 | 0.091 | 16.8 | 7.51 | 5.98 | 1.54 | 1.34 | D4 | 183 | 9362 | — | Action / Dexterity | broad_positive_gt02 |
| 261588 | Ascension: Year Five Collector's Edition | 2019 | 107 | 0.115 | 0.114 | 13.3 | 8.34 | 6.81 | 1.53 | 1.52 | D2 | 117 | — | — | Card Game; Fantasy | broad_positive_gt02 |
| 58782 | Bluffer | 1993 | 145 | 0.099 | 0.099 | 15.4 | 7.21 | 5.68 | 1.53 | 1.48 | D3 | 168 | 9852 | — | Bluffing; Trivia | broad_positive_gt02 |
| 241203 | Ascension: Year Four Collector's Edition | 2017 | 122 | 0.108 | 0.107 | 14.1 | 8.18 | 6.65 | 1.53 | 1.51 | D2 | 131 | — | — | Card Game; Fantasy | broad_positive_gt02 |
| 220975 | History Maker Golf | 2017 | 131 | 0.104 | 0.104 | 14.6 | 8.41 | 6.89 | 1.52 | 1.51 | D3 | 179 | 7092 | — | Sports | broad_positive_gt02 |
| 1757 | Yacht Race | 1960 | 120 | 0.109 | 0.108 | 14.0 | 7.32 | 5.79 | 1.52 | 1.55 | D2 | 131 | 11089 | — | Nautical; Racing | broad_positive_gt02 |
| 207951 | Tintas | 2016 | 312 | 0.068 | 0.067 | 22.5 | 8.11 | 6.59 | 1.52 | 1.43 | D6 | 363 | 5082 | — | Abstract Strategy | robust_underrated |
| 172844 | Charms | 2014 | 254 | 0.075 | 0.075 | 20.3 | 8.14 | 6.62 | 1.52 | 1.34 | D5 | 347 | 5832 | — | Card Game | robust_underrated |
| 2981 | Breaking Away | 1991 | 460 | 0.056 | 0.056 | 27.2 | 7.89 | 6.37 | 1.51 | 1.42 | D7 | 472 | 4795 | — | Abstract Strategy; Racing; Sport | robust_underrated |
| 159333 | Fendo | 2014 | 121 | 0.109 | 0.108 | 13.9 | 8.17 | 6.66 | 1.51 | 1.45 | D2 | 154 | 7872 | — | Abstract Strategy | broad_positive_gt02 |
| 161880 | The Quiet Year | 2013 | 407 | 0.059 | 0.059 | 25.5 | 7.93 | 6.43 | 1.51 | 1.38 | D6 | 501 | 4429 | — | Card Game; Print & Play | robust_underrated |
| 383010 | Clank! Legacy 2: Acquisitions Incorporat | 2024 | 234 | 0.078 | 0.078 | 19.3 | 9.39 | 7.88 | 1.51 | 1.41 | D5 | 1126 | 1484 | — | Adventure; Fantasy; Miniatures | robust_underrated |

Full broad pool (7754 rows) plus all 16549 estimation games with all columns (SE/post_SD/z/lb/next) in `underrated_candidates.csv`.

## B. Robust subset — all 910 robust candidates (sorted by residual desc)

Rule: `n≥200 & resid≥0.60 & min_alt≥0.30 & z≥5 & year<2025` (see README §3). Each row reports residual, SE, n, z, lower-bounds, robustness, popularity context, duplicate status. For broad-appeal evidence per candidate (reach / audience composition / cross-audience / proxy caveats) see `broad_appeal_evidence.md` — no combined score.

| game_id | title | year | n | SE | post_SD | z | lb_adj | adj | E[adj] | resid | CV | WLS | Q3 | WLS_Q3 | min_alt | decile | users | rank | wt | cats | share_heavy | meanΔ | disp |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 255249 | Monikers: More Monikers | 2018 | 452 | 0.056 | 0.056 | 40.5 | 8.47 | 8.58 | 6.30 | 2.27 | 2.26 | 2.33 | 2.18 | 2.24 | 2.18 | D7 | 521 | 3227 | 1.0 | Card Game; Humor; Mature / A | 0.17 | -0.31 | robust_underrated |
| 140135 | Small World Designer Edition | 2015 | 246 | 0.076 | 0.076 | 28.9 | 8.95 | 9.10 | 6.90 | 2.20 | 2.19 | 2.17 | 2.20 | 2.23 | 2.17 | D5 | 266 | — | 2.6 | Civilization; Fantasy; Terri | 0.30 | -0.20 | robust_underrated |
| 179448 | Monikers: Shmonikers | 2015 | 319 | 0.067 | 0.067 | 30.7 | 8.17 | 8.30 | 6.24 | 2.05 | 2.05 | 1.88 | 2.03 | 1.87 | 1.87 | D6 | 326 | 4747 | 1.0 | Party Game | 0.19 | -0.29 | robust_underrated |
| 195709 | Monikers: Something Something | 2016 | 246 | 0.076 | 0.076 | 26.6 | 8.18 | 8.33 | 6.30 | 2.03 | 2.06 | 1.86 | 2.04 | 1.90 | 1.86 | D5 | 255 | 5504 | 1.0 | Party Game | 0.19 | -0.29 | robust_underrated |
| 221248 | Monikers: The Shut Up & Sit Down Nonse | 2017 | 465 | 0.055 | 0.055 | 36.0 | 8.25 | 8.36 | 6.36 | 1.99 | 1.99 | 1.84 | 1.91 | 1.75 | 1.75 | D7 | 484 | 3607 | 1.0 | Party Game | 0.16 | -0.31 | robust_underrated |
| 283152 | Monikers: Serious Nonsense | 2019 | 500 | 0.053 | 0.053 | 36.2 | 8.38 | 8.48 | 6.55 | 1.94 | 1.96 | 1.99 | 1.99 | 2.05 | 1.96 | D7 | 609 | 2928 | 1.0 | Humor; Mature / Adult; Party | 0.13 | -0.28 | robust_underrated |
| 36553 | Time's Up! Title Recall! | 2008 | 3629 | 0.020 | 0.020 | 97.3 | 7.99 | 8.03 | 6.10 | 1.93 | 1.93 | 1.69 | 2.01 | 1.68 | 1.68 | D10 | 3787 | 731 | 1.2 | Humor; Movies / TV / Radio t | 0.24 | -0.36 | robust_underrated |
| 283151 | Monikers: Classics | 2019 | 263 | 0.074 | 0.073 | 26.1 | 8.30 | 8.45 | 6.52 | 1.92 | 1.96 | 1.79 | 1.91 | 1.81 | 1.79 | D5 | 343 | — | 1.0 | Party Game | 0.13 | -0.26 | robust_underrated |
| 4385 | A Gamut of Games | 1969 | 434 | 0.057 | 0.057 | 33.5 | 7.97 | 8.08 | 6.16 | 1.92 | 1.91 | 2.18 | 1.85 | 2.07 | 1.85 | D7 | 445 | — | 2.3 | Abstract Strategy; Book; Car | 0.37 | -0.32 | robust_underrated |
| 230262 | Time's Up! Party Edition | 2004 | 553 | 0.051 | 0.051 | 36.7 | 7.81 | 7.91 | 6.05 | 1.86 | 1.87 | 1.83 | 1.91 | 1.86 | 1.83 | D7 | 714 | 3245 | 1.1 | Humor; Party Game | 0.19 | -0.34 | robust_underrated |
| 57660 | Time's Up! Edición Azul | 2006 | 1365 | 0.032 | 0.032 | 54.4 | 7.62 | 7.68 | 5.92 | 1.76 | 1.76 | 1.50 | 1.83 | 1.52 | 1.50 | D9 | 1463 | 2142 | 1.2 | Humor; Movies / TV / Radio t | 0.21 | -0.31 | robust_underrated |
| 186279 | Finska Mini | 2011 | 468 | 0.055 | 0.055 | 31.3 | 7.71 | 7.82 | 6.09 | 1.73 | 1.72 | 1.63 | 1.64 | 1.53 | 1.53 | D7 | 566 | 4068 | 1.2 | Action / Dexterity; Party Ga | 0.42 | -0.39 | robust_underrated |
| 97683 | Age of Rail: South Africa | 2011 | 277 | 0.072 | 0.071 | 24.1 | 8.59 | 8.73 | 7.00 | 1.73 | 1.74 | 1.60 | 1.70 | 1.62 | 1.60 | D5 | 605 | 3481 | 3.0 | Economic; Trains; Transporta | 0.46 | -1.00 | robust_underrated |
| 147170 | El Grande Decennial Edition | 2006 | 978 | 0.038 | 0.038 | 45.1 | 8.70 | 8.78 | 7.05 | 1.72 | 1.71 | 1.60 | 1.68 | 1.53 | 1.53 | D8 | 1063 | — | 2.9 | Medieval; Political | 0.29 | -0.45 | robust_underrated |
| 541 | Das Motorsportspiel | 1995 | 381 | 0.061 | 0.061 | 26.6 | 7.77 | 7.89 | 6.26 | 1.63 | 1.66 | 1.60 | 1.56 | 1.53 | 1.53 | D6 | 399 | 5127 | 2.0 | Racing; Real-time; Sports | 0.45 | -0.44 | robust_underrated |
| 2470 | The Extraordinary Adventures of Baron  | 1998 | 379 | 0.061 | 0.061 | 26.4 | 7.43 | 7.55 | 5.92 | 1.62 | 1.65 | 1.44 | 1.55 | 1.38 | 1.38 | D6 | 402 | 5572 | 1.5 | Adventure; Novel-based; Part | 0.26 | -0.31 | robust_underrated |
| 188530 | My Favourite Things | 2015 | 375 | 0.062 | 0.062 | 25.8 | 7.78 | 7.90 | 6.31 | 1.59 | 1.58 | 1.61 | 1.53 | 1.59 | 1.53 | D6 | 1039 | 3091 | 1.3 | Card Game; Deduction; Humor; | 0.44 | -0.60 | robust_underrated |
| 6688 | Ninety-Nine | 1974 | 554 | 0.051 | 0.051 | 31.3 | 7.79 | 7.89 | 6.30 | 1.59 | 1.61 | 1.70 | 1.66 | 1.71 | 1.61 | D7 | 616 | 4287 | 2.1 | Card Game | 0.50 | -0.71 | robust_underrated |
| 7935 | 1844: Schweiz | 2003 | 212 | 0.082 | 0.082 | 19.2 | 8.78 | 8.94 | 7.37 | 1.57 | 1.58 | 1.53 | 1.58 | 1.59 | 1.53 | D4 | 221 | 5973 | 4.1 | Economic; Trains | 0.41 | -0.82 | robust_underrated |
| 14188 | Bughouse Chess | 1960 | 362 | 0.063 | 0.063 | 24.9 | 7.81 | 7.93 | 6.37 | 1.56 | 1.54 | 1.78 | 1.53 | 1.68 | 1.53 | D6 | 377 | 5581 | 2.8 | Abstract Strategy | 0.28 | -0.62 | robust_underrated |
| 46158 | Time's Up! Academy | 2009 | 575 | 0.050 | 0.050 | 31.4 | 7.57 | 7.67 | 6.11 | 1.56 | 1.55 | 1.51 | 1.60 | 1.54 | 1.51 | D7 | 630 | 4036 | 1.1 | Humor; Party Game | 0.27 | -0.33 | robust_underrated |
| 62814 | Tumblin-Dice Medium | 2008 | 215 | 0.081 | 0.081 | 19.1 | 7.46 | 7.62 | 6.06 | 1.56 | 1.56 | 1.39 | 1.58 | 1.46 | 1.39 | D4 | 233 | 7196 | 1.0 | Action / Dexterity; Dice | 0.37 | -0.34 | robust_underrated |
| 156372 | Heart of Crown: Fairy Garden | 2013 | 305 | 0.068 | 0.068 | 22.8 | 8.30 | 8.43 | 6.88 | 1.56 | 1.56 | 1.54 | 1.53 | 1.54 | 1.53 | D6 | 350 | 4946 | 2.6 | Card Game; Fantasy | 0.21 | -0.42 | robust_underrated |
| 38713 | Time's Up! Edición Amarilla | 2008 | 1622 | 0.030 | 0.030 | 52.1 | 7.72 | 7.78 | 6.23 | 1.55 | 1.54 | 1.48 | 1.58 | 1.47 | 1.47 | D9 | 1950 | 1550 | 1.1 | Humor; Party Game | 0.16 | -0.23 | robust_underrated |
| 207951 | Tintas | 2016 | 312 | 0.068 | 0.067 | 22.5 | 7.98 | 8.11 | 6.59 | 1.52 | 1.53 | 1.43 | 1.50 | 1.44 | 1.43 | D6 | 363 | 5082 | 1.4 | Abstract Strategy | 0.44 | -0.50 | robust_underrated |
| 172844 | Charms | 2014 | 254 | 0.075 | 0.075 | 20.3 | 7.99 | 8.14 | 6.62 | 1.52 | 1.53 | 1.34 | 1.51 | 1.38 | 1.34 | D5 | 347 | 5832 | 2.1 | Card Game | 0.57 | -0.77 | robust_underrated |
| 2981 | Breaking Away | 1991 | 460 | 0.056 | 0.056 | 27.2 | 7.78 | 7.89 | 6.37 | 1.51 | 1.52 | 1.54 | 1.42 | 1.44 | 1.42 | D7 | 472 | 4795 | 2.3 | Abstract Strategy; Racing; S | 0.51 | -0.58 | robust_underrated |
| 161880 | The Quiet Year | 2013 | 407 | 0.059 | 0.059 | 25.5 | 7.82 | 7.93 | 6.43 | 1.51 | 1.52 | 1.43 | 1.45 | 1.38 | 1.38 | D6 | 501 | 4429 | 1.4 | Card Game; Print & Play | 0.15 | -0.37 | robust_underrated |
| 383010 | Clank! Legacy 2: Acquisitions Incorpor | 2024 | 234 | 0.078 | 0.078 | 19.3 | 9.24 | 9.39 | 7.88 | 1.51 | 1.52 | 1.55 | 1.41 | 1.58 | 1.41 | D5 | 1126 | 1484 | 2.8 | Adventure; Fantasy; Miniatur | 0.24 | -0.30 | robust_underrated |
| 37141 | Time's Up! Deluxe | 2008 | 1024 | 0.037 | 0.037 | 40.2 | 7.76 | 7.84 | 6.34 | 1.50 | 1.49 | 1.48 | 1.61 | 1.55 | 1.48 | D8 | 1053 | 2678 | 1.3 | Electronic; Humor; Party Gam | 0.31 | -0.39 | robust_underrated |
| 141067 | History Maker Baseball | 2013 | 208 | 0.083 | 0.082 | 18.0 | 8.06 | 8.23 | 6.73 | 1.49 | 1.48 | 1.39 | 1.53 | 1.48 | 1.39 | D4 | 268 | 5867 | 2.2 | Sports | 0.15 | -0.04 | robust_underrated |
| 33495 | Time's Up! Édition purple | 2007 | 356 | 0.063 | 0.063 | 23.5 | 7.26 | 7.39 | 5.90 | 1.49 | 1.49 | 1.42 | 1.43 | 1.39 | 1.39 | D6 | 374 | 5809 | 1.1 | Humor; Memory; Party Game | 0.26 | -0.21 | robust_underrated |
| 1447 | 1841: Railways in Northern Italy | 1994 | 343 | 0.064 | 0.064 | 22.7 | 8.67 | 8.79 | 7.33 | 1.46 | 1.44 | 1.49 | 1.39 | 1.45 | 1.39 | D6 | 375 | 4571 | 4.4 | Economic; Post-Napoleonic; T | 0.33 | -0.92 | robust_underrated |
| 153016 | Telestrations: 12 Player Party Pack | 2011 | 3141 | 0.021 | 0.021 | 68.5 | 7.92 | 7.96 | 6.51 | 1.46 | 1.44 | 1.42 | 1.56 | 1.44 | 1.42 | D10 | 3505 | 757 | 1.1 | Humor; Party Game; Real-time | 0.17 | -0.24 | robust_underrated |
| 141008 | Carcassonne Big Box 2 | 2008 | 454 | 0.056 | 0.056 | 26.0 | 7.78 | 7.89 | 6.44 | 1.46 | 1.46 | 1.28 | 1.35 | 1.21 | 1.21 | D7 | 503 | — | 2.0 | City Building; Medieval | 0.15 | -0.18 | robust_underrated |
| 13089 | Wie ich die Welt sehe... | 2004 | 366 | 0.062 | 0.062 | 23.2 | 7.11 | 7.23 | 5.78 | 1.45 | 1.43 | 1.44 | 1.38 | 1.40 | 1.38 | D6 | 380 | 6787 | 1.1 | Card Game; Humor; Party Game | 0.34 | -0.44 | robust_underrated |
| 5217 | Eleusis | 1956 | 216 | 0.081 | 0.081 | 17.8 | 7.63 | 7.79 | 6.35 | 1.44 | 1.51 | 1.72 | 1.49 | 1.71 | 1.49 | D5 | 239 | 7241 | 2.9 | Card Game; Deduction; Educat | 0.44 | -0.51 | robust_underrated |
| 237009 | Urbino | 2017 | 207 | 0.083 | 0.083 | 17.4 | 8.28 | 8.44 | 7.00 | 1.44 | 1.44 | 1.44 | 1.46 | 1.53 | 1.44 | D4 | 256 | 5646 | 2.1 | Abstract Strategy; City Buil | 0.39 | -0.49 | robust_underrated |
| 3097 | 1849: The Game of Sicilian Railways | 1998 | 942 | 0.039 | 0.039 | 37.0 | 8.85 | 8.92 | 7.49 | 1.44 | 1.44 | 1.40 | 1.38 | 1.33 | 1.33 | D8 | 1057 | 1865 | 4.2 | Economic; Post-Napoleonic; T | 0.29 | -0.83 | robust_underrated |
| 2251 | Strat-O-Matic Baseball | 1962 | 1074 | 0.036 | 0.036 | 39.2 | 7.85 | 7.92 | 6.49 | 1.43 | 1.40 | 1.64 | 1.57 | 1.65 | 1.40 | D8 | 1279 | 2183 | 2.4 | Sports | 0.16 | -0.24 | robust_underrated |
| 7290 | Dynasty League Baseball Powered by Pur | 1985 | 223 | 0.080 | 0.080 | 17.8 | 7.69 | 7.84 | 6.42 | 1.42 | 1.40 | 1.42 | 1.44 | 1.47 | 1.40 | D5 | 273 | 6585 | 2.5 | Sports | 0.20 | -0.17 | robust_underrated |
| 295260 | It's a Wonderful World: Heritage Editi | 2019 | 921 | 0.039 | 0.039 | 35.7 | 8.57 | 8.65 | 7.24 | 1.40 | 1.40 | 1.40 | 1.36 | 1.35 | 1.35 | D8 | 995 | — | 2.3 | Card Game; Civilization; Sci | 0.22 | -0.28 | robust_underrated |
| 1278 | Dutch InterCity | 1999 | 209 | 0.083 | 0.082 | 16.9 | 7.75 | 7.91 | 6.52 | 1.40 | 1.40 | 1.22 | 1.39 | 1.28 | 1.22 | D4 | 275 | 7383 | 2.5 | Trains | 0.45 | -0.98 | robust_underrated |
| 215946 | Sub Terra: Collector's Edition | 2017 | 333 | 0.065 | 0.065 | 21.0 | 7.75 | 7.87 | 6.50 | 1.38 | 1.35 | 1.36 | 1.34 | 1.34 | 1.34 | D6 | 364 | — | 1.7 | Exploration; Horror | 0.15 | -0.09 | robust_underrated |
| 165595 | JamSumo | 2014 | 350 | 0.064 | 0.064 | 21.3 | 7.61 | 7.74 | 6.38 | 1.36 | 1.37 | 1.24 | 1.32 | 1.22 | 1.22 | D6 | 381 | 5586 | 1.2 | Action / Dexterity; Dice | 0.53 | -0.46 | robust_underrated |
| 322045 | Cartographers Heroes: Collector's Edit | 2021 | 706 | 0.045 | 0.045 | 30.2 | 8.35 | 8.43 | 7.08 | 1.36 | 1.39 | 1.48 | 1.32 | 1.46 | 1.32 | D8 | 819 | — | 2.1 | Fantasy; Territory Building | 0.25 | -0.29 | robust_underrated |
| 252657 | luz | 2014 | 228 | 0.079 | 0.079 | 17.1 | 7.92 | 8.08 | 6.72 | 1.36 | 1.38 | 1.26 | 1.38 | 1.32 | 1.26 | D5 | 283 | 6664 | 2.0 | Card Game | 0.60 | -0.78 | robust_underrated |
| 181289 | Terra Mystica: Big Box | 2015 | 447 | 0.056 | 0.056 | 23.9 | 8.78 | 8.89 | 7.54 | 1.35 | 1.38 | 1.34 | 1.25 | 1.29 | 1.25 | D7 | 480 | — | 4.0 | Civilization; Economic; Fant | 0.17 | -0.37 | robust_underrated |
| 5243 | Montage | 1973 | 209 | 0.083 | 0.082 | 16.3 | 7.55 | 7.71 | 6.37 | 1.35 | 1.37 | 1.42 | 1.39 | 1.45 | 1.37 | D4 | 216 | 7776 | 2.5 | Word Game | 0.64 | -0.51 | robust_underrated |
| 345976 | System Gateway (fan expansion for Andr | 2021 | 660 | 0.046 | 0.046 | 28.9 | 9.36 | 9.46 | 8.11 | 1.34 | 1.35 | 1.47 | 1.31 | 1.45 | 1.31 | D7 | 1025 | 1373 | 3.5 | Bluffing; Card Game; Fan Exp | 0.09 | -0.36 | robust_underrated |
| 223952 | Boast or Nothing | 2017 | 364 | 0.063 | 0.062 | 21.1 | 7.79 | 7.91 | 6.59 | 1.32 | 1.32 | 1.23 | 1.27 | 1.20 | 1.20 | D6 | 481 | 5066 | 1.4 | Card Game | 0.50 | -0.72 | robust_underrated |
| 391288 | Firefly: The Game – 10th Anniversary C | 2024 | 345 | 0.064 | 0.064 | 20.4 | 8.69 | 8.81 | 7.50 | 1.31 | 1.32 | 1.20 | 1.16 | 1.15 | 1.15 | D6 | 722 | — | 2.9 | Adventure; Movies / TV / Rad | 0.13 | -0.13 | robust_underrated |
| 63170 | 1817 | 2010 | 764 | 0.043 | 0.043 | 30.3 | 9.28 | 9.36 | 8.05 | 1.31 | 1.30 | 1.33 | 1.30 | 1.31 | 1.30 | D8 | 890 | 1783 | 4.8 | Economic; Trains; Transporta | 0.28 | -0.80 | robust_underrated |
| 174219 | Time's Up! Kids | 2015 | 254 | 0.075 | 0.075 | 17.4 | 7.29 | 7.43 | 6.13 | 1.30 | 1.33 | 1.23 | 1.32 | 1.26 | 1.23 | D5 | 312 | 6345 | 1.0 | Children's Game; Party Game | 0.26 | -0.24 | robust_underrated |
| 2667 | What Were You Thinking? | 1998 | 257 | 0.074 | 0.074 | 17.5 | 7.11 | 7.25 | 5.95 | 1.30 | 1.31 | 1.10 | 1.26 | 1.16 | 1.10 | D5 | 267 | 7808 | 1.2 | Party Game | 0.37 | -0.37 | robust_underrated |
| 4079 | What's My Word? | 1972 | 375 | 0.062 | 0.062 | 21.1 | 7.39 | 7.51 | 6.21 | 1.30 | 1.34 | 1.44 | 1.22 | 1.39 | 1.22 | D6 | 386 | 5800 | 2.1 | Deduction; Word Game | 0.41 | -0.39 | robust_underrated |
| 14940 | Figure It | 1975 | 245 | 0.076 | 0.076 | 17.0 | 6.89 | 7.04 | 5.74 | 1.30 | 1.32 | 1.33 | 1.32 | 1.35 | 1.32 | D5 | 291 | 8889 | 1.3 | Deduction | 0.33 | -0.51 | robust_underrated |
| 238094 | Mutabo | 2017 | 521 | 0.052 | 0.052 | 24.8 | 7.65 | 7.75 | 6.46 | 1.30 | 1.31 | 1.31 | 1.36 | 1.37 | 1.31 | D7 | 608 | 3978 | 1.0 | Humor; Party Game | 0.15 | -0.29 | robust_underrated |
| 12157 | Unanimo | 1990 | 952 | 0.039 | 0.039 | 33.5 | 7.25 | 7.32 | 6.03 | 1.30 | 1.30 | 1.23 | 1.26 | 1.14 | 1.14 | D8 | 1108 | 3236 | 1.2 | Bluffing; Party Game; Word G | 0.26 | -0.25 | robust_underrated |
| 398162 | MicroMacro: Crime City – Showdown | 2023 | 452 | 0.056 | 0.056 | 22.8 | 8.17 | 8.28 | 7.00 | 1.28 | 1.29 | 1.25 | 1.11 | 1.19 | 1.11 | D7 | 813 | 2737 | 1.0 | Deduction; Murder / Mystery | 0.28 | -0.35 | robust_underrated |
| 194923 | Techno Bowl: Arcade Football Unplugged | 2017 | 262 | 0.074 | 0.074 | 17.3 | 8.42 | 8.56 | 7.29 | 1.28 | 1.29 | 1.25 | 1.28 | 1.28 | 1.25 | D5 | 321 | 4893 | 2.8 | Sports; Video Game Theme | 0.21 | -0.20 | robust_underrated |
| 186567 | Baseball Highlights: 2045 – Super Delu | 2015 | 513 | 0.053 | 0.053 | 24.1 | 8.05 | 8.16 | 6.89 | 1.27 | 1.29 | 1.21 | 1.35 | 1.28 | 1.21 | D7 | 531 | — | 2.1 | Card Game; Science Fiction;  | 0.26 | -0.31 | robust_underrated |
| 515 | 6-Tage Rennen | 1986 | 251 | 0.075 | 0.075 | 16.9 | 7.20 | 7.34 | 6.07 | 1.27 | 1.30 | 1.28 | 1.25 | 1.31 | 1.25 | D5 | 257 | 8191 | 1.8 | Racing; Sports | 0.48 | -0.47 | robust_underrated |
| 70918 | Hanabi & Ikebana | 2010 | 639 | 0.047 | 0.047 | 26.8 | 7.80 | 7.89 | 6.63 | 1.27 | 1.27 | 1.16 | 1.29 | 1.20 | 1.16 | D7 | 645 | — | 1.8 | Card Game; Deduction | 0.43 | -0.49 | robust_underrated |
| 244258 | The Red Dragon Inn 7: The Tavern Crew | 2018 | 311 | 0.068 | 0.068 | 18.6 | 7.72 | 7.86 | 6.59 | 1.26 | 1.25 | 1.37 | 1.22 | 1.37 | 1.22 | D6 | 381 | 5107 | 1.6 | Card Game; Fantasy; Humor; P | 0.09 | 0.05 | robust_underrated |
| 91666 | Crossboule | 2008 | 201 | 0.084 | 0.084 | 15.0 | 7.25 | 7.42 | 6.16 | 1.26 | 1.26 | 1.14 | 1.30 | 1.22 | 1.14 | D4 | 210 | 8207 | 1.1 | Action / Dexterity | 0.49 | -0.32 | robust_underrated |
| 232894 | Escape: The Curse of the Temple – Big  | 2017 | 564 | 0.050 | 0.050 | 25.1 | 7.91 | 8.01 | 6.75 | 1.26 | 1.25 | 1.21 | 1.31 | 1.24 | 1.21 | D7 | 613 | — | 1.9 | Adventure; Dice; Exploration | 0.16 | -0.18 | robust_underrated |
| 99358 | Stonewall Jackson's Way II: Battles of | 2013 | 324 | 0.066 | 0.066 | 19.0 | 8.97 | 9.10 | 7.85 | 1.26 | 1.25 | 1.48 | 1.24 | 1.47 | 1.24 | D6 | 354 | 4039 | 3.7 | American Civil War; Wargame | 0.13 | -0.44 | robust_underrated |
| 216849 | Dominion (Second Edition) Big Box | 2016 | 983 | 0.038 | 0.038 | 33.0 | 8.22 | 8.30 | 7.04 | 1.26 | 1.26 | 1.16 | 1.23 | 1.10 | 1.10 | D8 | 1230 | — | 2.3 | Card Game; Medieval | 0.07 | -0.19 | robust_underrated |
| 4688 | Angola | 1988 | 540 | 0.051 | 0.051 | 24.4 | 8.43 | 8.53 | 7.28 | 1.25 | 1.27 | 1.52 | 1.32 | 1.55 | 1.27 | D7 | 599 | 3270 | 3.2 | Civil War; Modern Warfare; W | 0.27 | -0.54 | robust_underrated |
| 246742 | Château Aventure | 2018 | 243 | 0.077 | 0.076 | 16.3 | 7.17 | 7.32 | 6.07 | 1.25 | 1.29 | 1.13 | 1.25 | 1.16 | 1.13 | D5 | 262 | 7180 | 1.0 | Adventure; Book; Fantasy; Ho | 0.30 | -0.16 | robust_underrated |
| 141007 | Carcassonne Big Box 3 | 2010 | 895 | 0.040 | 0.040 | 31.3 | 7.88 | 7.95 | 6.71 | 1.25 | 1.24 | 1.10 | 1.22 | 1.06 | 1.06 | D8 | 960 | — | 2.1 | City Building; Medieval | 0.10 | -0.10 | robust_underrated |
| 146035 | Eggs of Ostrich | 2012 | 303 | 0.069 | 0.068 | 18.1 | 7.34 | 7.48 | 6.23 | 1.24 | 1.25 | 1.05 | 1.22 | 1.06 | 1.05 | D6 | 319 | 7255 | 1.2 | Card Game | 0.65 | -0.69 | robust_underrated |
| 20295 | WeyKick | 2001 | 524 | 0.052 | 0.052 | 23.8 | 7.32 | 7.42 | 6.17 | 1.24 | 1.21 | 1.07 | 1.30 | 1.13 | 1.07 | D7 | 539 | 5181 | 1.0 | Action / Dexterity; Real-tim | 0.57 | -0.47 | robust_underrated |
| 229130 | Kingdom Builder: Big Box (Second Editi | 2017 | 689 | 0.045 | 0.045 | 27.2 | 8.17 | 8.26 | 7.02 | 1.24 | 1.24 | 1.10 | 1.25 | 1.12 | 1.10 | D8 | 749 | — | 2.2 | Medieval; Territory Building | 0.23 | -0.27 | robust_underrated |
| 209136 | Q.E. | 2017 | 318 | 0.067 | 0.067 | 18.4 | 7.87 | 8.00 | 6.76 | 1.23 | 1.23 | 1.09 | 1.20 | 1.09 | 1.09 | D6 | 342 | 5790 | 1.8 | Economic | 0.56 | -0.72 | robust_underrated |
| 261321 | Ascension: Deliverance | 2018 | 219 | 0.081 | 0.080 | 15.1 | 7.91 | 8.07 | 6.85 | 1.22 | 1.22 | 1.23 | 1.23 | 1.29 | 1.22 | D5 | 252 | 6173 | 2.0 | Card Game; Fantasy | 0.26 | -0.21 | robust_underrated |
| 188076 | Taluva Deluxe | 2015 | 440 | 0.057 | 0.057 | 21.4 | 8.02 | 8.13 | 6.92 | 1.22 | 1.24 | 1.17 | 1.13 | 1.13 | 1.13 | D7 | 474 | — | 2.4 | Abstract Strategy; Territory | 0.39 | -0.51 | robust_underrated |
| 156455 | Viticulture: Complete Collector's Edit | 2014 | 806 | 0.042 | 0.042 | 28.9 | 8.53 | 8.61 | 7.40 | 1.22 | 1.23 | 1.19 | 1.21 | 1.17 | 1.17 | D8 | 836 | — | 3.3 | Economic; Farming | 0.26 | -0.31 | robust_underrated |
| 174458 | Baseball Highlights: 2045 – Deluxe Edi | 2015 | 545 | 0.051 | 0.051 | 23.7 | 8.06 | 8.16 | 6.95 | 1.21 | 1.20 | 1.16 | 1.28 | 1.21 | 1.16 | D7 | 565 | — | 2.3 | Card Game; Science Fiction;  | 0.30 | -0.29 | robust_underrated |
| 216798 | Telestrations: 6 Player Family Pack | 2014 | 509 | 0.053 | 0.053 | 22.9 | 7.37 | 7.48 | 6.27 | 1.21 | 1.20 | 1.16 | 1.28 | 1.22 | 1.16 | D7 | 641 | 4143 | 1.0 | Humor; Party Game | 0.16 | -0.17 | robust_underrated |
| 319604 | Ricochet: A la poursuite du Comte cour | 2020 | 223 | 0.080 | 0.080 | 15.2 | 7.58 | 7.74 | 6.53 | 1.21 | 1.23 | 1.26 | 1.21 | 1.29 | 1.21 | D5 | 254 | 6693 | 1.4 | Word Game | 0.22 | -0.21 | robust_underrated |
| 39336 | Mégawatts | 2008 | 441 | 0.057 | 0.057 | 21.3 | 8.04 | 8.15 | 6.94 | 1.21 | 1.21 | 1.11 | 1.11 | 1.04 | 1.04 | D7 | 463 | 4116 | 3.0 | Economic; Industry / Manufac | 0.26 | -0.35 | robust_underrated |
| 158976 | Ascension: Year One Collector's Editio | 2015 | 434 | 0.057 | 0.057 | 21.1 | 7.86 | 7.97 | 6.76 | 1.21 | 1.22 | 1.21 | 1.13 | 1.15 | 1.13 | D7 | 460 | — | 2.3 | Card Game; Fantasy | 0.15 | -0.15 | robust_underrated |
| 295564 | Unmatched Game System | 2019 | 2194 | 0.025 | 0.025 | 47.5 | 8.48 | 8.53 | 7.32 | 1.21 | 1.20 | 1.30 | 1.18 | 1.24 | 1.18 | D9 | 3056 | 555 | 1.9 | Card Game; Fantasy; Fighting | 0.20 | -0.34 | robust_underrated |
| 84464 | Animal Upon Animal: Balancing Bridge | 2010 | 452 | 0.056 | 0.056 | 21.5 | 7.27 | 7.38 | 6.17 | 1.21 | 1.20 | 1.20 | 1.12 | 1.11 | 1.11 | D7 | 467 | 5552 | 1.1 | Action / Dexterity; Animals; | 0.42 | -0.38 | robust_underrated |
| 248878 | FlickFleet | 2019 | 214 | 0.082 | 0.081 | 14.8 | 7.99 | 8.15 | 6.95 | 1.20 | 1.21 | 1.10 | 1.22 | 1.17 | 1.10 | D4 | 295 | 6013 | 1.7 | Action / Dexterity; Print &  | 0.28 | -0.36 | robust_underrated |
| 18057 | Anno Domini: Natur | 1998 | 257 | 0.074 | 0.074 | 16.0 | 6.84 | 6.99 | 5.79 | 1.19 | 1.21 | 1.28 | 1.17 | 1.29 | 1.17 | D5 | 277 | 8540 | 1.2 | Bluffing; Card Game; Humor;  | 0.27 | -0.31 | robust_underrated |
| 185257 | Innovation Deluxe | 2017 | 826 | 0.042 | 0.041 | 28.7 | 8.66 | 8.74 | 7.55 | 1.19 | 1.19 | 1.22 | 1.18 | 1.18 | 1.18 | D8 | 894 | — | 3.1 | Card Game; Civilization | 0.32 | -0.46 | robust_underrated |
| 4550 | 1000 Blank White Cards | 1996 | 524 | 0.052 | 0.052 | 22.7 | 6.93 | 7.04 | 5.85 | 1.19 | 1.18 | 1.29 | 1.24 | 1.32 | 1.18 | D7 | 561 | 6195 | 1.4 | Card Game; Comic Book / Stri | 0.24 | -0.39 | robust_underrated |
| 88126 | Time's Up! Family | 2010 | 969 | 0.038 | 0.038 | 30.7 | 7.39 | 7.46 | 6.28 | 1.18 | 1.18 | 0.94 | 1.15 | 0.88 | 0.88 | D8 | 1164 | 2768 | 1.1 | Memory; Party Game | 0.23 | -0.24 | robust_underrated |
| 324157 | Hidden Games Crime Scene: Green Poison | 2020 | 254 | 0.075 | 0.075 | 15.7 | 8.29 | 8.43 | 7.26 | 1.17 | 1.20 | 1.22 | 1.14 | 1.27 | 1.14 | D5 | 349 | 4780 | 2.2 | Deduction; Murder / Mystery | 0.24 | -0.33 | robust_underrated |
| 64897 | Formule Dé | 1991 | 299 | 0.069 | 0.069 | 17.0 | 7.30 | 7.44 | 6.27 | 1.17 | 1.19 | 1.16 | 1.15 | 1.14 | 1.14 | D6 | 333 | 6266 | 2.2 | Racing; Sports | 0.17 | -0.18 | robust_underrated |
| 177877 | SiXeS | 2016 | 321 | 0.067 | 0.066 | 17.6 | 7.38 | 7.51 | 6.34 | 1.17 | 1.17 | 1.01 | 1.14 | 1.01 | 1.01 | D6 | 399 | 5898 | 1.0 | Card Game; Party Game; Trivi | 0.33 | -0.42 | robust_underrated |
| 324711 | Schadenfreude | 2020 | 821 | 0.042 | 0.042 | 28.0 | 8.25 | 8.34 | 7.17 | 1.17 | 1.17 | 1.12 | 1.13 | 1.08 | 1.08 | D8 | 1488 | 1768 | 1.8 | Card Game | 0.40 | -0.67 | robust_underrated |
| 7104 | Ace of Aces: Powerhouse Series | 1981 | 485 | 0.054 | 0.054 | 21.4 | 7.39 | 7.50 | 6.33 | 1.16 | 1.17 | 1.32 | 1.08 | 1.21 | 1.08 | D7 | 558 | 4578 | 1.8 | Aviation / Flight; Wargame;  | 0.21 | -0.25 | robust_underrated |
| 332230 | Unlock!: Heroic Adventures – Insert Co | 2018 | 229 | 0.079 | 0.079 | 14.7 | 7.83 | 7.99 | 6.83 | 1.16 | 1.16 | 1.23 | 1.17 | 1.28 | 1.16 | D5 | 283 | 6067 | 1.8 | Card Game; Exploration; Puzz | 0.40 | -0.43 | robust_underrated |
| 32424 | 1848: Australia | 2007 | 577 | 0.050 | 0.050 | 23.3 | 8.56 | 8.66 | 7.50 | 1.16 | 1.17 | 1.10 | 1.19 | 1.14 | 1.10 | D7 | 652 | 3136 | 3.8 | Economic; Trains; Transporta | 0.36 | -0.78 | robust_underrated |
| 130705 | Super Big Boggle | 2012 | 215 | 0.081 | 0.081 | 14.2 | 7.26 | 7.42 | 6.26 | 1.16 | 1.16 | 1.10 | 1.18 | 1.16 | 1.10 | D4 | 241 | 7713 | 1.3 | Dice; Party Game; Puzzle; Re | 0.20 | -0.30 | robust_underrated |
| 151 | Piratenbillard | 1989 | 441 | 0.057 | 0.057 | 20.3 | 6.97 | 7.08 | 5.92 | 1.16 | 1.15 | 1.05 | 1.07 | 0.97 | 0.97 | D7 | 461 | 7066 | 1.2 | Action / Dexterity; Pirates | 0.58 | -0.53 | robust_underrated |
| 3119 | Haste Worte? | 1997 | 412 | 0.059 | 0.059 | 19.6 | 7.08 | 7.19 | 6.03 | 1.16 | 1.13 | 1.02 | 1.01 | 1.01 | 1.01 | D6 | 447 | 6466 | 1.4 | Party Game; Word Game | 0.39 | -0.41 | robust_underrated |
| 213788 | Ascension: Year Three Collector's Edit | 2016 | 218 | 0.081 | 0.081 | 14.3 | 7.91 | 8.07 | 6.92 | 1.15 | 1.14 | 1.18 | 1.18 | 1.24 | 1.14 | D5 | 232 | — | 2.5 | Card Game; Fantasy | 0.15 | -0.14 | robust_underrated |
| 147190 | Yggdrasil (Second Edition with Asgard  | 2013 | 250 | 0.076 | 0.075 | 15.3 | 7.80 | 7.94 | 6.79 | 1.15 | 1.15 | 1.11 | 1.17 | 1.15 | 1.11 | D5 | 261 | — | 2.4 | Mythology | 0.21 | -0.27 | robust_underrated |
| 25314 | Bowling Solitaire | 1969 | 365 | 0.063 | 0.062 | 18.5 | 6.89 | 7.01 | 5.86 | 1.15 | 1.17 | 1.25 | 1.12 | 1.17 | 1.12 | D6 | 401 | 7087 | 1.5 | Card Game; Print & Play; Spo | 0.37 | -0.35 | robust_underrated |
| 17923 | Anno Domini: Flopps | 2001 | 429 | 0.058 | 0.058 | 20.0 | 6.98 | 7.10 | 5.94 | 1.15 | 1.14 | 1.24 | 1.05 | 1.15 | 1.05 | D7 | 446 | 6335 | 1.4 | Bluffing; Card Game; Humor;  | 0.25 | -0.30 | robust_underrated |
| 119866 | Wings of Glory: WW1 Rules and Accessor | 2012 | 591 | 0.049 | 0.049 | 23.4 | 7.90 | 7.99 | 6.84 | 1.15 | 1.15 | 1.34 | 1.21 | 1.36 | 1.15 | D7 | 692 | 3366 | 2.0 | Aviation / Flight; Card Game | 0.14 | -0.11 | robust_underrated |
| 23540 | Shikoku 1889 | 2004 | 2196 | 0.025 | 0.025 | 45.1 | 8.66 | 8.71 | 7.56 | 1.15 | 1.15 | 1.10 | 1.13 | 1.04 | 1.04 | D9 | 2733 | 719 | 3.8 | Economic; Trains; Transporta | 0.26 | -0.73 | robust_underrated |
| 264476 | Rangers of Shadow Deep | 2018 | 493 | 0.054 | 0.054 | 21.3 | 8.40 | 8.51 | 7.36 | 1.14 | 1.14 | 1.41 | 1.04 | 1.32 | 1.04 | D7 | 638 | 3338 | 2.3 | Book; Dice; Fantasy; Fightin | 0.10 | -0.12 | robust_underrated |
| 1942 | Foppen | 1995 | 429 | 0.058 | 0.058 | 19.9 | 7.12 | 7.24 | 6.09 | 1.14 | 1.15 | 1.06 | 1.03 | 1.01 | 1.01 | D7 | 435 | 6984 | 1.6 | Card Game | 0.62 | -0.63 | robust_underrated |
| 32944 | Neue Heimat | 2007 | 793 | 0.042 | 0.042 | 27.0 | 7.94 | 8.02 | 6.88 | 1.14 | 1.15 | 1.02 | 1.11 | 1.01 | 1.01 | D8 | 815 | 3409 | 2.6 | City Building; Economic | 0.56 | -0.75 | robust_underrated |
| 249552 | Ascension: Delirium | 2018 | 280 | 0.071 | 0.071 | 16.0 | 7.86 | 8.00 | 6.85 | 1.14 | 1.16 | 1.15 | 1.12 | 1.17 | 1.12 | D5 | 309 | 5607 | 2.0 | Card Game; Fantasy | 0.26 | -0.29 | robust_underrated |
| 313 | Big Boss | 1994 | 917 | 0.039 | 0.039 | 29.0 | 7.60 | 7.68 | 6.53 | 1.14 | 1.14 | 1.08 | 1.05 | 1.08 | 1.05 | D8 | 1190 | 2974 | 2.4 | Economic; Industry / Manufac | 0.41 | -0.45 | robust_underrated |
| 225482 | Seas of Strife | 2015 | 1743 | 0.029 | 0.029 | 39.9 | 7.82 | 7.88 | 6.74 | 1.14 | 1.12 | 0.97 | 1.19 | 0.95 | 0.95 | D9 | 2632 | 1386 | 1.3 | American West; Card Game; Na | 0.46 | -0.57 | robust_underrated |
| 38429 | Cornerstone | 2008 | 231 | 0.079 | 0.078 | 14.5 | 7.43 | 7.58 | 6.44 | 1.14 | 1.14 | 1.03 | 1.15 | 1.09 | 1.03 | D5 | 241 | 7838 | 1.7 | Action / Dexterity | 0.42 | -0.46 | robust_underrated |
| 29140 | Tumblin-Dice Jr. | 2006 | 265 | 0.073 | 0.073 | 15.5 | 6.97 | 7.12 | 5.98 | 1.14 | 1.15 | 1.02 | 1.13 | 1.04 | 1.02 | D5 | 266 | 8248 | 1.0 | Action / Dexterity; Children | 0.44 | -0.37 | robust_underrated |
| 171905 | Orléans: Deluxe Edition | 2015 | 1666 | 0.029 | 0.029 | 38.9 | 8.64 | 8.70 | 7.56 | 1.14 | 1.14 | 1.07 | 1.19 | 1.06 | 1.06 | D9 | 1725 | — | 3.1 | Medieval; Religious; Travel | 0.26 | -0.35 | robust_underrated |
| 111081 | Animal Upon Animal: Crest Climbers | 2011 | 363 | 0.063 | 0.063 | 18.2 | 7.20 | 7.32 | 6.18 | 1.14 | 1.16 | 1.13 | 1.09 | 1.09 | 1.09 | D6 | 381 | 6504 | 1.1 | Action / Dexterity; Animals; | 0.37 | -0.41 | robust_underrated |
| 909 | Saturn | 1997 | 210 | 0.082 | 0.082 | 13.8 | 7.02 | 7.18 | 6.04 | 1.14 | 1.16 | 1.00 | 1.16 | 1.06 | 1.00 | D4 | 224 | 9084 | 1.2 | Action / Dexterity | 0.55 | -0.47 | robust_underrated |
| 373835 | Unlock! Kids: Stories from the Past | 2022 | 252 | 0.075 | 0.075 | 15.1 | 7.94 | 8.08 | 6.95 | 1.14 | 1.12 | 1.15 | 1.06 | 1.19 | 1.06 | D5 | 401 | 4639 | 1.5 | Adventure; American West; An | 0.26 | -0.30 | robust_underrated |
| 1353 | Time's Up! | 1999 | 5962 | 0.015 | 0.015 | 73.4 | 7.61 | 7.64 | 6.51 | 1.13 | 1.18 | 1.28 | 1.16 | 1.39 | 1.16 | D10 | 6292 | 795 | 1.2 | Humor; Party Game | 0.24 | -0.37 | robust_underrated |
| … | *truncated to 120 of 910 robust rows for markdown readability* |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

Full 910 robust rows (all columns including SE/post_SD/z/lb/resid variants/decile/users/rank/duplicate/category/audience composition/disposition) are in `underrated_candidates.csv` filtered by `screening_disposition=robust_underrated`.

### Also flagged as well-known but meeting robust criteria (separate flag, not in robust table above): 530 games

| game_id | title | year | n | resid | min_alt | users | rank | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 156546 | Monikers | 2015 | 6609 | 1.27 | 1.31 | 7906 | 303 | well-known/widely established — users_rated 7906 rank 303 (p |
| 270633 | Aeon's End: The New Age | 2019 | 2860 | 0.97 | 0.97 | 3492 | 302 | well-known/widely established — users_rated 3492 rank 302 (p |
| 552 | Bus | 1999 | 4136 | 0.96 | 0.86 | 5558 | 452 | well-known/widely established — users_rated 5558 rank 452 (p |
| 46213 | Telestrations | 2009 | 18881 | 0.88 | 0.78 | 20944 | 354 | well-known/widely established — users_rated 20944 rank 354 ( |
| 215 | Tichu | 1991 | 15688 | 0.81 | 0.77 | 16985 | 251 | well-known/widely established — users_rated 16985 rank 251 ( |
| 92828 | Dixit: Odyssey | 2011 | 21163 | 0.80 | 0.73 | 23119 | 357 | well-known/widely established — users_rated 23119 rank 357 ( |
| 5 | Acquire | 1963 | 20439 | 0.78 | 0.78 | 22332 | 367 | well-known/widely established — users_rated 22332 rank 367 ( |
| 41 | Can't Stop | 1980 | 19430 | 0.78 | 0.70 | 22018 | 771 | well-known/widely established — users_rated 22018 rank 771 ( |
| 165722 | KLASK | 2014 | 10899 | 0.76 | 0.65 | 12459 | 261 | well-known/widely established — users_rated 12459 rank 261 ( |
| 118 | Modern Art | 1992 | 23104 | 0.76 | 0.63 | 25690 | 222 | well-known/widely established — users_rated 25690 rank 222 ( |
| 335764 | Unmatched: Battle of Legends, Volume Two | 2021 | 2649 | 0.75 | 0.76 | 3573 | 476 | well-known/widely established — users_rated 3573 rank 476 (p |
| 172 | For Sale | 1997 | 31917 | 0.75 | 0.56 | 34640 | 358 | well-known/widely established — users_rated 34640 rank 358 ( |
| 218417 | Aeon's End: War Eternal | 2017 | 5892 | 0.73 | 0.75 | 6753 | 151 | well-known/widely established — users_rated 6753 rank 151 (p |
| 182631 | Star Realms: Colony Wars | 2015 | 8218 | 0.73 | 0.66 | 8871 | 268 | well-known/widely established — users_rated 8871 rank 268 (p |
| 146652 | Legendary Encounters: An Alien Deck Buil | 2014 | 12925 | 0.71 | 0.58 | 13796 | 200 | well-known/widely established — users_rated 13796 rank 200 ( |
| 397598 | Dune: Imperium – Uprising | 2023 | 8879 | 0.71 | 0.53 | 19653 | 5 | well-known/widely established — users_rated 19653 rank 5 (po |
| 291453 | SCOUT | 2019 | 19707 | 0.71 | 0.60 | 29080 | 109 | well-known/widely established — users_rated 29080 rank 109 ( |
| 19777 | Indonesia | 2005 | 4761 | 0.70 | 0.60 | 5450 | 306 | well-known/widely established — users_rated 5450 rank 306 (p |
| 244271 | Dice Throne: Season Two – Battle Chest | 2019 | 4633 | 0.70 | 0.71 | 5559 | 327 | well-known/widely established — users_rated 5559 rank 327 (p |
| 315767 | Cartographers Heroes | 2021 | 4853 | 0.68 | 0.66 | 6090 | 460 | well-known/widely established — users_rated 6090 rank 460 (p |
| … | *and 510 more flagged_wellknown in CSV* |  |  |  |  |  |  |  |

---
*All candidates include `screening_disposition` + `reason` for later manual review; see `exclusions_and_deduplication.md` for explicit exclusion/dedup log with related_game_id.*

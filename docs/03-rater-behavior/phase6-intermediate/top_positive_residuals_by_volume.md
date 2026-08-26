# INTERMEDIATE / NOT FINAL — Top positive residuals by popularity bucket

> **Exploratory screening only — NOT a final hidden-gem ranking.**
> Strong positive residuals (`underratedness_g`) flag games whose severity-adjusted quality is unusually high *relative to expectation from observable characteristics*. This does **not** imply broad appeal. The gap between *underratedness* (conditional model residual) and *hidden gem* (evidence of appeal beyond current niche) or *broad appeal* (validated out-of-sample audience) is the whole point; low rating count does not imply “needs more data to converge” and sample-size shrinkage alone does not fix self-selection into the rater pool. See AGENTS.md central problem.

## Provenance

| field | value |
|---|---|
| source residual | `underratedness_g = adj_mean_g − expected_quality_g` from **preferred Q3b/OLS specification** (`scripts/31`, `data/processed/phase2-active/phase6_residuals_active.parquet`) |
| preferred spec | `Q3b_flex_volume / OLS` (OLS over WLS_n; band-based volume) — `docs/phase2-active/phase6_comparative.json` — CV R² 0.582, CV RMSE 0.563, `corr(resid,log_n)` −0.004, `max\|bandmean\|` ≈0 |
| active population | **16,627 × ≥10, ¬strict** research games (`bgg_research_population.parquet`); **16,564** have ≥1 active rating; estimation sample **16,549** (15 dropped for missing weight) |
| mu (ALS prior) | **7.144** (`docs/phase2-active/phase5_quality_comparison.json` `mu_active`; `active_baseline_refresh.json`; `phase6_comparative.json` `params.mu`) |
| sigma_e | **1.194** (`phase5_quality_comparison.json` `eb_variance_components.sigma_e_sd`; `sigma_e2` 1.426) |
| sigma_alpha | **0.864** (`sigma_alpha2` 0.746) — between-game SD |
| SE formula | `SE_g = sigma_e / √n_active = 1.194 / √n_active` (frequentist; `data/processed/phase2-active/game_adjusted_means_active.parquet`) — order-of-magnitude heteroscedasticity (SE p10 0.023 → p90 0.119, median 0.070) |
| post_SD (EB) | `post_SD_g = 1/√(1/sigma_alpha² + n/sigma_e²)` — shrunk posterior SD (λ=sigma_e²/sigma_alpha²≈1.91; `w=n/(n+λ)` 8.7%→0.02% shrinkage). For n≥50 difference SE vs post_SD ≤1.5% (n=1 SE 1.194 post 0.700) |
| SE range in this table | 0.0039 (n≈93k, 25k+) → 1.194 (n=1, 1–99) |
| residual columns | `residual = adj_mean − expected_quality`; `residual_cv` = 5-fold CV out-of-fold residual; `residual_lb_95 = residual −1.96·SE` and `adj_lb_95 = adj_mean −1.96·SE` as sensitivity lower bounds (post_SD variant also in CSV) |
| category/mechanic | from `bgg_research_population.parquet` (complete for 16,627; handles `data/processed/phase2-filtered/games` 80.89% gap via population join — `docs/phase2-active/PARQUET_CATALOG.md` 13,449/16,627) |
| scripts | `scripts/31_phase6_expected_quality_underratedness.py` (VOL_BAND_EDGES `[0,100,200,500,1000,2500,5000,10000,25000,inf)`; 28 cat + 8 vol-bands + 7 decade + ns(year) + structure); `scripts/30_phase5_quality_estimator.py`; `scripts/26_phase2_active_baseline_refresh.py` ALS |
| input artifacts | `scratch/phase2-active/` (copy-once from `data/processed/phase2-active/` per task, DuckDB bounded 4 GB/3 threads, `scratch/ducktmp`) — `rating_observations_active.parquet` (24.5M, 288,730 users), `user_severity_active.parquet`, `game_adjusted_means_active.parquet`, `bgg_research_population.parquet`; validation `docs/phase2-active/active_baseline_refresh.json`, `phase6_comparative.json`, `phase6_volume_diagnostic.json`, `reports/phase6_underratedness/*` |
| validation | `mu 7.144` and `sigma_e 1.194` agree across `phase6_comparative.json` `params`, `phase5_quality_comparison.json` `eb_variance_components`, and `phase6_volume_diagnostic.json` `params`; estimation n 16,549 matches comparative_table; volume band means/gaps reproduced within rounding (e.g., band 1–99 mean_n 65.99, adj_mean 7.17; decile median_n 82, adj 7.14); top-residual spot-check vs `reports/phase6_underratedness/top_residuals_preview.csv` — rank-1 Pondscape residual 3.937, n=1, adj 11.55, expected 7.62 matches row 1 below |

## Bucketing choice (transparent, predefined)

We use **nine rating-volume bands defined by `n_active` (active rating count, same `n` that drives `SE_g` and measured in the same active universe as `adj_mean_g`)**:

| band | `n_active` range | games in estimation sample | mean `n` | median `n` |
|---|---|---:|---:|---:|
| **1–99** | 1–99 | 1,604 | 66 | 80 |
| **100–199** | 100–199 | 4,610 | 142 | 139 |
| **200–499** | 200–499 | 4,325 | 316 | 301 |
| **500–999** | 500–999 | 2,252 | 704 | 679 |
| **1k–2.5k** | 1,000–2,499 | 1,919 | 1569 | 1492 |
| **2.5k–5k** | 2,500–4,999 | 893 | 3496 | 3378 |
| **5k–10k** | 5,000–9,999 | 476 | 6934 | 6620 |
| **10k–25k** | 10,000–24,999 | 332 | 15649 | 14736 |
| **25k+** | 25,000–122,168 | 138 | 44659 | 36996 |

**Justification:** these are **exactly the `VOL_BAND_EDGES = [0,100,200,500,1000,2500,5000,10000,25000,inf)` / `VOL_BAND_LABELS` used as the preferred Q3b flex-volume controls and as the diagnostic bands in `docs/phase2-active/phase6_volume_diagnostic.json`** (`scripts/31` `VOL_BAND_EDGES` / `VOL_BAND_LABELS`). They are *predefined from population structure*, not post-hoc: P10 `n_active`=100 and P90=2,796 bracket the bands, handling the convex non-monotonic volume-quality curve (classification **(c) broadly unchanged** — severity adjustment does not explain the gradient, slope adj +0.261 vs raw +0.230 per tenfold, ratio 1.13; `max|bandmean|` 0.148 linear → ≈0 with bands, +0.012 CV R²). Using identical bands keeps the residual screen and its volume diagnostic on the same scale, prevents leakage of unmodelled non-linearity into residuals, and **prevents a single popularity stratum dominating** the table (rank *within* each band, not globally). Alternatives (log10 bands `<100,100–299,300–999,1000–4999,5000+` or tertiles/quartiles/deciles) produce nearly identical cut-points; decile medians shown in provenance table above confirm no empty or degenerate band (smallest still 138 games at 25k+).

> **Why not tertiles/quartiles?** Equal-count tertiles would lump the extremes (n=1 and n≈12k) into different thirds while hiding the non-monotonic bottom (1–99 vs 100–199 dip). Log bands would merge 100–199/200–499 where the gradient curvature is steepest. The nine-band scheme preserves diagnostic interpretability while staying practical: each bucket holds ≥138 games, median SE spans 0.60 (1–99) → 0.006 (25k+), and `corr(resid,log_n)` is flat (−0.004 preferred, vs −0.13 under WLS) — evidence the bands did their job.

## Reading the tables

- **Rank *within* each band by `residual` (primary).** Sensitivity column `residual_lb_95 = residual −1.96·SE` (≈ lower 95% bound treating `expected_quality` fixed) is shown; re-ranking by this bound leaves top-10 unchanged in **8 of 9 bands (overlap 10/10)** and **5/10 overlap only in 1–99** where SE dominates (median SE 0.17 vs 0.07 overall). CSV also provides `residual_lb_95_post` (using `post_SD`) for EB shrinkage sensitivity.
- `n_active` is the `n` that drives `SE`; `raw_active_mean = AVG(rating)` on active obs (24.5M) — check raw vs adj gap is `mean(delta_pool)` by construction (`corr raw-adj 0.979`).
- `adj_mean_g` = `AVG(rating − delta_u)` with `delta` from active ALS (mu 7.144); `expected_quality_g` = fitted Q3b/OLS (intercept + vol-band + ns(year, knots p5/35/65/95) + weight + log(playtime) + players + reimpl + 28 categories). Do **not** read category coefficients causally (tags overlap).
- `SE` and `post_SD` differ only at very low n (n=1: 1.194 vs 0.700; n=81: 0.133 vs 0.131); we sort by SE-based bound to stay conservative at the bottom where uncertainty matters most.
- **Not validated for broad appeal.** High residual ≠ hidden gem. Exposure unobserved; collection `own` snapshot-time; `games` scrape 80.89% gap handled via population; timestamp semantics unresolved — any temporal reading needs dual check. Underratedness is **operational, model-dependent**, not latent quality (`claim_tags.underratedness`).

## Top positive residuals — per volume band (Q3b/OLS residual, active population)

_Each sub-table shows the 10 strongest positive residuals **within that `n_active` bucket**, sorted by `residual` descending. Global ranking would be dominated by low-n tail (Pondscape n=1 residual 3.94 vs 25k+ max 0.75); within-band ranking is the design._

### Band `1–99` — `n_active` 1–99 — 10 of 1,604 games shown

_Band diagnostics: mean `n` 66, median 80; residual mean +0.000, SD 0.732, max +3.94, min -5.19; SE median 0.134 (post_SD 0.132). Within-band `corr(resid,log_n)` ≈0 by band construction._

| # | game_id | title | year | n | raw | adj | expected | residual | SE | post_SD | resid_lb_95 | adj_lb | weight | play | categories | mechanics |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 435330 | Pondscape | 2025 | 1 | 10.000 | 11.553 | 7.616 | **3.937** | 1.194 | 0.700 | 1.597 | 9.213 | 2.00 | 35 | Animals, Card Game, Environmental | Grid Coverage, Hand Management |
| 2 | 428589 | Thief's Market | 2025 | 3 | 10.000 | 10.461 | 7.585 | **2.877** | 0.689 | 0.539 | 1.525 | 9.110 | 2.00 | 60 | Card Game, Dice, Fantasy | Dice Rolling, Die Icon Resolution, I Cut, You Choose, Open … |
| 3 | 434131 | Tolleno | 2025 | 1 | 9.000 | 9.844 | 7.626 | **2.218** | 1.194 | 0.700 | -0.122 | 7.504 | 2.00 | 48 | City Building | Area Majority / Influence, Area Movement, Contracts, Map Ad… |
| 4 | 404462 | Monikers: Monikers-er | 2023 | 61 | 8.746 | 9.112 | 6.914 | **2.198** | 0.153 | 0.151 | 1.898 | 8.812 | 1.00 | 60 | Party Game | — |
| 5 | 436804 | Opération Zèbre | 2025 | 1 | 9.000 | 9.310 | 7.149 | **2.162** | 1.194 | 0.700 | -0.179 | 6.970 | 1.00 | 45 | Deduction, Party Game, Spies / Secret Agents, Trivia | Communication Limits, Cooperative Game, Line Drawing, Paper… |
| 6 | 436591 | Brightcast | 2025 | 2 | 9.500 | 9.374 | 7.222 | **2.152** | 0.844 | 0.604 | 0.497 | 7.719 | 1.20 | 15 | Card Game, Fantasy | Hand Management, Interrupts, Set Collection, Take That |
| 7 | 436038 | Hercules and the 12 Labors | 2025 | 2 | 10.000 | 9.907 | 7.782 | **2.125** | 0.844 | 0.604 | 0.470 | 8.252 | 2.35 | 60 | Card Game, Dice, Fantasy, Mythology | Dice Rolling, Events, Solo / Solitaire Game, Storytelling |
| 8 | 127333 | Schnipp & Weg | 2012 | 81 | 7.740 | 8.271 | 6.148 | **2.124** | 0.133 | 0.131 | 1.864 | 8.011 | 1.00 | 15 | Action / Dexterity, Children's Game | Flicking |
| 9 | 203560 | Fall of Magic | 2015 | 86 | 8.129 | 8.320 | 6.243 | **2.077** | 0.129 | 0.127 | 1.824 | 8.067 | 1.50 | 0 | Fantasy | Storytelling |
| 10 | 428284 | Here Lies | 2025 | 2 | 10.000 | 9.616 | 7.583 | **2.032** | 0.844 | 0.604 | 0.378 | 7.961 | 1.86 | 50 | Deduction, Murder / Mystery | Acting, Cooperative Game, Deduction, Drawing, Hand Manageme… |

> **Sensitivity (1–99):** ranking by `residual_lb_95` (residual −1.96·SE) reshuffles this band to: `Monikers: Monikers-er` (1.90), `Schnipp & Weg` (1.86), `Fall of Magic` (1.82), `Abstratus` (1.51), `The Headlines Game` (1.43) top-5; only 5/10 overlap with residual top-10. This is **not a defect** — it is the SE gradient (1.19 at n=1 vs 0.13 at n≈80) making low-n residuals fragile. At n≥100 overlap is 10/10. Treat 1–99 candidates as high-variance screens needing further validation.

### Band `100–199` — `n_active` 100–199 — 10 of 4,610 games shown

_Band diagnostics: mean `n` 142, median 139; residual mean -0.000, SD 0.618, max +1.99, min -5.96; SE median 0.101 (post_SD 0.101). Within-band `corr(resid,log_n)` ≈0 by band construction._

| # | game_id | title | year | n | raw | adj | expected | residual | SE | post_SD | resid_lb_95 | adj_lb | weight | play | categories | mechanics |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 120269 | Red White & Blue Racin': Stock Car Action Game | 2012 | 133 | 8.473 | 8.454 | 6.462 | **1.992** | 0.104 | 0.103 | 1.789 | 8.251 | 1.92 | 45 | Racing, Sports | Dice Rolling |
| 2 | 33434 | Funkenschlag: EnBW | 2007 | 198 | 8.215 | 8.696 | 6.847 | **1.849** | 0.085 | 0.084 | 1.682 | 8.529 | 3.17 | 120 | Economic, Industry / Manufacturing | Auction / Bidding, Network and Route Building |
| 3 | 24996 | Start Player: A Kinda Collectible Card Game | 2006 | 181 | 6.517 | 7.036 | 5.192 | **1.843** | 0.089 | 0.088 | 1.669 | 6.862 | 1.00 | 1 | Card Game, Collectible Components, Comic Book / Strip,… | — |
| 4 | 4657 | Replay Baseball | 1973 | 105 | 7.890 | 7.968 | 6.178 | **1.791** | 0.117 | 0.115 | 1.562 | 7.740 | 2.50 | 30 | Card Game, Sports | — |
| 5 | 1803 | Zopp | 1997 | 158 | 7.247 | 7.670 | 5.896 | **1.774** | 0.095 | 0.094 | 1.588 | 7.484 | 1.18 | 40 | Action / Dexterity | — |
| 6 | 341489 | Carrooka | 2021 | 195 | 8.249 | 8.557 | 6.811 | **1.746** | 0.086 | 0.085 | 1.578 | 8.389 | 1.10 | 60 | Action / Dexterity, Sports | Flicking, Slide / Push |
| 7 | 331953 | Unlock!: Timeless Adventures – Verloren im Zeitstrudel! | 2019 | 132 | 7.912 | 8.394 | 6.659 | **1.735** | 0.104 | 0.103 | 1.531 | 8.190 | 1.67 | 60 | Card Game, Exploration, Puzzle, Real-time, Science Fic… | Cooperative Game, Storytelling |
| 8 | 8939 | Der wahre Walter | 1989 | 170 | 7.100 | 7.438 | 5.723 | **1.715** | 0.092 | 0.091 | 1.536 | 7.259 | 1.20 | 60 | Party Game | Betting and Bluffing, Voting |
| 9 | 249768 | My First Adventure: Finding the Dragon | 2018 | 100 | 7.540 | 7.793 | 6.087 | **1.705** | 0.119 | 0.118 | 1.471 | 7.559 | 1.00 | 20 | Book, Children's Game, Exploration, Fantasy, Medieval | Cooperative Game, Storytelling |
| 10 | 351600 | Mortum: Medieval Detective – The Shelter | 2022 | 131 | 8.057 | 8.490 | 6.865 | **1.625** | 0.104 | 0.104 | 1.420 | 8.285 | 1.40 | 240 | Adventure, Deduction, Fantasy | Cooperative Game, Storytelling |

### Band `200–499` — `n_active` 200–499 — 10 of 4,325 games shown

_Band diagnostics: mean `n` 316, median 301; residual mean -0.000, SD 0.557, max +2.27, min -4.60; SE median 0.069 (post_SD 0.069). Within-band `corr(resid,log_n)` ≈0 by band construction._

| # | game_id | title | year | n | raw | adj | expected | residual | SE | post_SD | resid_lb_95 | adj_lb | weight | play | categories | mechanics |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 255249 | Monikers: More Monikers | 2018 | 452 | 8.260 | 8.575 | 6.303 | **2.272** | 0.056 | 0.056 | 2.162 | 8.465 | 1.00 | 60 | Card Game, Humor, Mature / Adult, Party Game | Acting, Open Drafting, Role Playing |
| 2 | 140135 | Small World Designer Edition | 2015 | 246 | 8.900 | 9.100 | 6.898 | **2.202** | 0.076 | 0.076 | 2.053 | 8.951 | 2.58 | 80 | Civilization, Fantasy, Territory Building | Area Majority / Influence, Area Movement, Dice Rolling, Var… |
| 3 | 179448 | Monikers: Shmonikers | 2015 | 319 | 8.005 | 8.298 | 6.243 | **2.055** | 0.067 | 0.067 | 1.924 | 8.167 | 1.00 | 60 | Party Game | Acting, Open Drafting, Role Playing |
| 4 | 195709 | Monikers: Something Something | 2016 | 246 | 8.038 | 8.326 | 6.298 | **2.029** | 0.076 | 0.076 | 1.879 | 8.177 | 1.00 | 60 | Party Game | Acting, Open Drafting, Role Playing |
| 5 | 221248 | Monikers: The Shut Up & Sit Down Nonsense Box | 2017 | 465 | 8.042 | 8.356 | 6.362 | **1.994** | 0.055 | 0.055 | 1.886 | 8.247 | 1.00 | 60 | Party Game | Acting, Open Drafting, Role Playing |
| 6 | 283151 | Monikers: Classics | 2019 | 263 | 8.188 | 8.448 | 6.524 | **1.924** | 0.074 | 0.073 | 1.779 | 8.304 | 1.00 | 60 | Party Game | — |
| 7 | 4385 | A Gamut of Games | 1969 | 434 | 7.760 | 8.078 | 6.157 | **1.921** | 0.057 | 0.057 | 1.809 | 7.965 | 2.32 | 30 | Abstract Strategy, Book, Card Game, Deduction, Dice, S… | — |
| 8 | 186279 | Finska Mini | 2011 | 468 | 7.432 | 7.818 | 6.089 | **1.730** | 0.055 | 0.055 | 1.621 | 7.710 | 1.15 | 30 | Action / Dexterity, Party Game | Player Elimination |
| 9 | 97683 | Age of Rail: South Africa | 2011 | 277 | 7.736 | 8.732 | 7.005 | **1.727** | 0.072 | 0.071 | 1.587 | 8.591 | 3.00 | 60 | Economic, Trains, Transportation | Action Drafting, Alliances, Auction / Bidding, Stock Holdin… |
| 10 | 541 | Das Motorsportspiel | 1995 | 381 | 7.444 | 7.887 | 6.258 | **1.629** | 0.061 | 0.061 | 1.509 | 7.768 | 2.00 | 120 | Racing, Real-time, Sports | Roll / Spin and Move, Simulation, Track Movement |

### Band `500–999` — `n_active` 500–999 — 10 of 2,252 games shown

_Band diagnostics: mean `n` 704, median 679; residual mean -0.000, SD 0.503, max +1.94, min -2.73; SE median 0.046 (post_SD 0.046). Within-band `corr(resid,log_n)` ≈0 by band construction._

| # | game_id | title | year | n | raw | adj | expected | residual | SE | post_SD | resid_lb_95 | adj_lb | weight | play | categories | mechanics |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 283152 | Monikers: Serious Nonsense | 2019 | 500 | 8.205 | 8.484 | 6.549 | **1.935** | 0.053 | 0.053 | 1.831 | 8.380 | 1.00 | 60 | Humor, Mature / Adult, Party Game | Acting, Open Drafting, Role Playing |
| 2 | 230262 | Time's Up! Party Edition | 2004 | 553 | 7.575 | 7.914 | 6.051 | **1.863** | 0.051 | 0.051 | 1.764 | 7.814 | 1.13 | 90 | Humor, Party Game | Acting, Memory, Team-Based Game |
| 3 | 147170 | El Grande Decennial Edition | 2006 | 978 | 8.328 | 8.776 | 7.053 | **1.722** | 0.038 | 0.038 | 1.648 | 8.701 | 2.95 | 90 | Medieval, Political | Area Majority / Influence, Auction / Bidding, Auction: Mult… |
| 4 | 6688 | Ninety-Nine | 1974 | 554 | 7.180 | 7.888 | 6.302 | **1.585** | 0.051 | 0.051 | 1.486 | 7.788 | 2.08 | 60 | Card Game | Hand Management, Predictive Bid, Trick-taking |
| 5 | 46158 | Time's Up! Academy | 2009 | 575 | 7.341 | 7.671 | 6.109 | **1.562** | 0.050 | 0.050 | 1.464 | 7.573 | 1.09 | 30 | Humor, Party Game | Acting, Communication Limits, Memory, Team-Based Game |
| 6 | 1770 | Aliens | 1989 | 713 | 7.217 | 7.418 | 5.952 | **1.467** | 0.045 | 0.045 | 1.379 | 7.331 | 2.23 | 90 | Fighting, Horror, Movies / TV / Radio theme, Science F… | Cooperative Game, Dice Rolling, Scenario / Mission / Campai… |
| 7 | 3097 | 1849: The Game of Sicilian Railways | 1998 | 942 | 8.091 | 8.924 | 7.486 | **1.438** | 0.039 | 0.039 | 1.362 | 8.848 | 4.16 | 180 | Economic, Post-Napoleonic, Trains, Transportation | Auction / Bidding, Investment, Network and Route Building, … |
| 8 | 295260 | It's a Wonderful World: Heritage Edition | 2019 | 921 | 8.373 | 8.648 | 7.245 | **1.403** | 0.039 | 0.039 | 1.326 | 8.571 | 2.33 | 60 | Card Game, Civilization, Science Fiction | Open Drafting, Scenario / Mission / Campaign Game, Set Coll… |
| 9 | 322045 | Cartographers Heroes: Collector's Edition | 2021 | 706 | 8.140 | 8.433 | 7.077 | **1.356** | 0.045 | 0.045 | 1.268 | 8.345 | 2.09 | 45 | Fantasy, Territory Building | Bingo, Grid Coverage, Line Drawing, Paper-and-Pencil, Solo … |
| 10 | 345976 | System Gateway (fan expansion for Android: Netrunner) | 2021 | 660 | 9.091 | 9.455 | 8.112 | **1.343** | 0.046 | 0.046 | 1.251 | 9.364 | 3.50 | 45 | Bluffing, Card Game, Fan Expansion, Science Fiction, T… | Action Points, Deck Construction, Hand Management, Race, Se… |

### Band `1k–2.5k` — `n_active` 1,000–2,499 — 10 of 1,919 games shown

_Band diagnostics: mean `n` 1569, median 1492; residual mean -0.000, SD 0.450, max +1.76, min -2.54; SE median 0.031 (post_SD 0.031). Within-band `corr(resid,log_n)` ≈0 by band construction._

| # | game_id | title | year | n | raw | adj | expected | residual | SE | post_SD | resid_lb_95 | adj_lb | weight | play | categories | mechanics |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 57660 | Time's Up! Edición Azul | 2006 | 1365 | 7.370 | 7.683 | 5.923 | **1.759** | 0.032 | 0.032 | 1.696 | 7.620 | 1.22 | 45 | Humor, Movies / TV / Radio theme, Party Game | Acting, Communication Limits, Memory, Team-Based Game |
| 2 | 38713 | Time's Up! Edición Amarilla | 2008 | 1622 | 7.545 | 7.776 | 6.230 | **1.546** | 0.030 | 0.030 | 1.488 | 7.718 | 1.07 | 30 | Humor, Party Game | Acting, Communication Limits, Memory, Team-Based Game |
| 3 | 37141 | Time's Up! Deluxe | 2008 | 1024 | 7.450 | 7.836 | 6.336 | **1.501** | 0.037 | 0.037 | 1.428 | 7.763 | 1.31 | 60 | Electronic, Humor, Party Game | Acting, Communication Limits, Memory, Team-Based Game |
| 4 | 2251 | Strat-O-Matic Baseball | 1962 | 1074 | 7.678 | 7.917 | 6.490 | **1.427** | 0.036 | 0.036 | 1.356 | 7.846 | 2.39 | 45 | Sports | Dice Rolling, Simulation, Solo / Solitaire Game |
| 5 | 295564 | Unmatched Game System | 2019 | 2194 | 8.189 | 8.528 | 7.317 | **1.210** | 0.025 | 0.025 | 1.160 | 8.478 | 1.93 | 40 | Card Game, Fantasy, Fighting | Action Points, Card Play Conflict Resolution, Hand Manageme… |
| 6 | 23540 | Shikoku 1889 | 2004 | 2196 | 7.976 | 8.710 | 7.562 | **1.149** | 0.025 | 0.025 | 1.099 | 8.660 | 3.82 | 240 | Economic, Trains, Transportation | Auction / Bidding, Hexagon Grid, Market, Network and Route … |
| 7 | 225482 | Seas of Strife | 2015 | 1743 | 7.308 | 7.880 | 6.739 | **1.141** | 0.029 | 0.029 | 1.085 | 7.824 | 1.31 | 45 | American West, Card Game, Nautical | Hand Management, Trick-taking |
| 8 | 171905 | Orléans: Deluxe Edition | 2015 | 1666 | 8.343 | 8.695 | 7.556 | **1.139** | 0.029 | 0.029 | 1.082 | 8.638 | 3.08 | 90 | Medieval, Religious, Travel | Deck, Bag, and Pool Building, Open Drafting, Point to Point… |
| 9 | 157820 | Escape: The Curse of the Temple – Big Box | 2014 | 1654 | 7.512 | 7.695 | 6.575 | **1.121** | 0.029 | 0.029 | 1.063 | 7.638 | 1.53 | 10 | Adventure, Dice, Exploration, Real-time | Cooperative Game, Dice Rolling, Grid Movement, Modular Boar… |
| 10 | 294693 | Nokosu Dice | 2016 | 1222 | 7.587 | 8.260 | 7.152 | **1.107** | 0.034 | 0.034 | 1.040 | 8.193 | 2.07 | 60 | Card Game, Dice | Auction / Bidding, Dice Rolling, Hand Management, Open Draf… |

### Band `2.5k–5k` — `n_active` 2,500–4,999 — 10 of 893 games shown

_Band diagnostics: mean `n` 3496, median 3378; residual mean -0.000, SD 0.451, max +1.93, min -2.63; SE median 0.021 (post_SD 0.021). Within-band `corr(resid,log_n)` ≈0 by band construction._

| # | game_id | title | year | n | raw | adj | expected | residual | SE | post_SD | resid_lb_95 | adj_lb | weight | play | categories | mechanics |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 36553 | Time's Up! Title Recall! | 2008 | 3629 | 7.669 | 8.027 | 6.098 | **1.929** | 0.020 | 0.020 | 1.890 | 7.988 | 1.19 | 60 | Humor, Movies / TV / Radio theme, Party Game | Acting, Communication Limits, Memory, Team-Based Game |
| 2 | 153016 | Telestrations: 12 Player Party Pack | 2011 | 3141 | 7.723 | 7.965 | 6.505 | **1.459** | 0.021 | 0.021 | 1.418 | 7.923 | 1.06 | 30 | Humor, Party Game, Real-time | Drawing, Line Drawing, Paper-and-Pencil |
| 3 | 16747 | Tumblin' Dice | 2004 | 4787 | 7.239 | 7.622 | 6.515 | **1.107** | 0.017 | 0.017 | 1.073 | 7.588 | 1.05 | 45 | Action / Dexterity, Dice, Party Game | Dice Rolling, Flicking |
| 4 | 270633 | Aeon's End: The New Age | 2019 | 2860 | 8.484 | 8.769 | 7.797 | **0.972** | 0.022 | 0.022 | 0.928 | 8.725 | 2.91 | 60 | Card Game, Fantasy, Science Fiction | Cooperative Game, Deck, Bag, and Pool Building, Hand Manage… |
| 5 | 552 | Bus | 1999 | 4136 | 7.650 | 8.285 | 7.326 | **0.959** | 0.019 | 0.019 | 0.923 | 8.249 | 3.04 | 120 | Transportation | Action Points, Action Queue, Network and Route Building, Pi… |
| 6 | 121288 | Dixit: Journey | 2012 | 4551 | 7.376 | 7.582 | 6.627 | **0.955** | 0.018 | 0.018 | 0.920 | 7.547 | 1.26 | 30 | Card Game, Humor, Party Game | Acting, Simultaneous Action Selection, Storytelling, Target… |
| 7 | 140068 | Galaxy Trucker: Anniversary Edition | 2012 | 2868 | 8.137 | 8.402 | 7.464 | **0.938** | 0.022 | 0.022 | 0.895 | 8.359 | 2.83 | 120 | Real-time, Science Fiction, Space Exploration, Transpo… | Dice Rolling, Events, Memory, Real-Time, Relative Movement,… |
| 8 | 171908 | El Grande Big Box | 2015 | 3320 | 8.192 | 8.530 | 7.598 | **0.933** | 0.021 | 0.021 | 0.892 | 8.490 | 2.80 | 90 | Renaissance | Area Majority / Influence, Area Movement, Auction / Bidding… |
| 9 | 354 | Stick 'Em | 1993 | 3781 | 7.041 | 7.555 | 6.678 | **0.878** | 0.019 | 0.019 | 0.840 | 7.517 | 1.90 | 60 | Card Game | Hand Management, Take That, Trick-taking |
| 10 | 230914 | Carcassonne Big Box 6 | 2017 | 4395 | 8.010 | 8.061 | 7.214 | **0.847** | 0.018 | 0.018 | 0.811 | 8.026 | 1.95 | 35 | City Building, Medieval, Territory Building | Area Majority / Influence, Pattern Building, Tile Placement |

### Band `5k–10k` — `n_active` 5,000–9,999 — 10 of 476 games shown

_Band diagnostics: mean `n` 6934, median 6620; residual mean -0.000, SD 0.381, max +1.27, min -1.48; SE median 0.015 (post_SD 0.015). Within-band `corr(resid,log_n)` ≈0 by band construction._

| # | game_id | title | year | n | raw | adj | expected | residual | SE | post_SD | resid_lb_95 | adj_lb | weight | play | categories | mechanics |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 156546 | Monikers | 2015 | 6609 | 7.767 | 8.084 | 6.815 | **1.269** | 0.015 | 0.015 | 1.240 | 8.055 | 1.09 | 60 | Card Game, Humor, Mature / Adult, Party Game, Print & … | Acting, Communication Limits, Open Drafting, Role Playing, … |
| 2 | 1353 | Time's Up! | 1999 | 5962 | 7.273 | 7.641 | 6.506 | **1.134** | 0.015 | 0.015 | 1.104 | 7.611 | 1.20 | 90 | Humor, Party Game | Acting, Communication Limits, Memory, Team-Based Game |
| 3 | 160069 | Ticket to Ride: 10th Anniversary | 2014 | 5355 | 8.219 | 8.343 | 7.251 | **1.092** | 0.016 | 0.016 | 1.060 | 8.311 | 1.89 | 60 | Trains, Travel | Connections, End Game Bonuses, Hand Management, Network and… |
| 4 | 18833 | Lord of the Rings: The Confrontation | 2005 | 6423 | 7.478 | 7.849 | 6.794 | **1.055** | 0.015 | 0.015 | 1.025 | 7.820 | 2.19 | 30 | Adventure, Bluffing, Deduction, Fantasy, Movies / TV /… | Area Movement, Card Play Conflict Resolution, Hand Manageme… |
| 5 | 363622 | The Castles of Burgundy: Special Edition | 2023 | 7544 | 9.135 | 9.374 | 8.376 | **0.998** | 0.014 | 0.014 | 0.971 | 9.347 | 2.84 | 120 | Dice, Medieval, Territory Building | Dice Rolling, End Game Bonuses, Grid Movement, Set Collecti… |
| 6 | 266507 | Clank! Legacy: Acquisitions Incorporated | 2019 | 9746 | 8.507 | 8.834 | 7.951 | **0.883** | 0.012 | 0.012 | 0.859 | 8.810 | 2.74 | 120 | Adventure, Fantasy | Deck, Bag, and Pool Building, Delayed Purchase, End Game Bo… |
| 7 | 327 | Loopin' Louie | 1992 | 9546 | 6.727 | 7.056 | 6.185 | **0.871** | 0.012 | 0.012 | 0.847 | 7.032 | 1.05 | 10 | Action / Dexterity, Animals, Aviation / Flight, Childr… | Player Elimination, Real-Time |
| 8 | 108687 | Puerto Rico | 2011 | 5631 | 8.298 | 8.614 | 7.751 | **0.863** | 0.016 | 0.016 | 0.832 | 8.583 | 3.22 | 150 | City Building, Economic, Farming | Action Drafting, End Game Bonuses, Follow, Hidden Victory P… |
| 9 | 3201 | Lord of the Rings: The Confrontation | 2002 | 6911 | 7.196 | 7.555 | 6.754 | **0.801** | 0.014 | 0.014 | 0.773 | 7.527 | 2.15 | 30 | Adventure, Bluffing, Card Game, Deduction, Fantasy, Mo… | Area Movement, Card Play Conflict Resolution, Hand Manageme… |
| 10 | 904 | Nightmare Productions | 2000 | 5808 | 7.063 | 7.471 | 6.674 | **0.796** | 0.016 | 0.016 | 0.766 | 7.440 | 2.10 | 60 | Movies / TV / Radio theme | Auction / Bidding, Auction: Turn Order Until Pass, Closed E… |

### Band `10k–25k` — `n_active` 10,000–24,999 — 10 of 332 games shown

_Band diagnostics: mean `n` 15649, median 14736; residual mean -0.000, SD 0.346, max +0.94, min -1.93; SE median 0.010 (post_SD 0.010). Within-band `corr(resid,log_n)` ≈0 by band construction._

| # | game_id | title | year | n | raw | adj | expected | residual | SE | post_SD | resid_lb_95 | adj_lb | weight | play | categories | mechanics |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 150 | PitchCar | 1995 | 11177 | 7.262 | 7.618 | 6.678 | **0.941** | 0.011 | 0.011 | 0.918 | 7.596 | 1.12 | 30 | Action / Dexterity, Children's Game, Party Game, Racin… | Flicking, Modular Board, Race |
| 2 | 46213 | Telestrations | 2009 | 18881 | 7.364 | 7.650 | 6.769 | **0.882** | 0.009 | 0.009 | 0.865 | 7.633 | 1.07 | 30 | Humor, Party Game, Real-time | Drawing, Paper-and-Pencil |
| 3 | 215 | Tichu | 1991 | 15688 | 7.548 | 7.959 | 7.151 | **0.808** | 0.010 | 0.010 | 0.789 | 7.941 | 2.35 | 90 | Card Game | Hand Management, Ladder Climbing, Predictive Bid, Team-Base… |
| 4 | 92828 | Dixit: Odyssey | 2011 | 21163 | 7.371 | 7.590 | 6.791 | **0.800** | 0.008 | 0.008 | 0.784 | 7.574 | 1.16 | 30 | Card Game, Humor, Party Game | Storytelling, Targeted Clues, Voting |
| 5 | 5 | Acquire | 1963 | 20439 | 7.320 | 7.658 | 6.882 | **0.777** | 0.008 | 0.008 | 0.760 | 7.642 | 2.49 | 90 | Economic, Territory Building | Connections, End Game Bonuses, Hand Management, Hidden Vict… |
| 6 | 41 | Can't Stop | 1980 | 19430 | 6.915 | 7.290 | 6.514 | **0.775** | 0.009 | 0.009 | 0.759 | 7.273 | 1.14 | 30 | Dice, Number | Dice Rolling, Push Your Luck, Race, Roll / Spin and Move, T… |
| 7 | 220 | High Society | 1995 | 14542 | 7.173 | 7.575 | 6.802 | **0.773** | 0.010 | 0.010 | 0.753 | 7.555 | 1.48 | 30 | Card Game | Auction / Bidding, Auction: Turn Order Until Pass, Constrai… |
| 8 | 165722 | KLASK | 2014 | 10899 | 7.619 | 7.953 | 7.191 | **0.762** | 0.011 | 0.011 | 0.740 | 7.931 | 1.04 | 10 | Action / Dexterity, Real-time | Real-Time, Score-and-Reset Game |
| 9 | 118 | Modern Art | 1992 | 23104 | 7.497 | 7.894 | 7.132 | **0.762** | 0.008 | 0.008 | 0.746 | 7.879 | 2.28 | 45 | Card Game, Economic | Auction / Bidding, Auction: English, Auction: Once Around, … |
| 10 | 146652 | Legendary Encounters: An Alien Deck Building Game | 2014 | 12925 | 7.723 | 7.996 | 7.282 | **0.714** | 0.011 | 0.011 | 0.693 | 7.975 | 2.71 | 60 | Card Game, Fighting, Horror, Movies / TV / Radio theme… | Cooperative Game, Deck, Bag, and Pool Building, Delayed Pur… |

### Band `25k+` — `n_active` 25,000–122,168 — 10 of 138 games shown

_Band diagnostics: mean `n` 44659, median 36996; residual mean -0.000, SD 0.357, max +0.75, min -1.62; SE median 0.006 (post_SD 0.006). Within-band `corr(resid,log_n)` ≈0 by band construction._

| # | game_id | title | year | n | raw | adj | expected | residual | SE | post_SD | resid_lb_95 | adj_lb | weight | play | categories | mechanics |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 172 | For Sale | 1997 | 31917 | 7.253 | 7.586 | 6.840 | **0.746** | 0.007 | 0.007 | 0.733 | 7.573 | 1.25 | 30 | Card Game, Economic | Auction / Bidding, Auction: Sealed Bid, Auction: Turn Order… |
| 2 | 161936 | Pandemic Legacy: Season 1 | 2015 | 51174 | 8.496 | 8.741 | 8.096 | **0.645** | 0.005 | 0.005 | 0.635 | 8.731 | 2.83 | 60 | Environmental, Medical | Action Points, Cooperative Game, Hand Management, Legacy Ga… |
| 3 | 12 | Ra | 1999 | 27545 | 7.653 | 8.043 | 7.423 | **0.620** | 0.007 | 0.007 | 0.606 | 8.029 | 2.30 | 60 | Ancient, Mythology | Auction / Bidding, Auction: Once Around, Closed Economy Auc… |
| 4 | 316554 | Dune: Imperium | 2020 | 46981 | 8.383 | 8.694 | 8.127 | **0.567** | 0.006 | 0.006 | 0.556 | 8.683 | 3.08 | 120 | Movies / TV / Radio theme, Novel-based, Political, Sci… | Card Play Conflict Resolution, Deck, Bag, and Pool Building… |
| 5 | 2653 | Survive: Escape from Atlantis! | 1982 | 26110 | 7.290 | 7.504 | 6.972 | **0.532** | 0.007 | 0.007 | 0.518 | 7.490 | 1.69 | 60 | Adventure, Animals, Bluffing, Nautical | Area Majority / Influence, Dice Rolling, Grid Movement, Hex… |
| 6 | 93 | El Grande | 1995 | 29944 | 7.752 | 8.129 | 7.621 | **0.508** | 0.007 | 0.007 | 0.494 | 8.115 | 2.93 | 120 | Medieval | Action Drafting, Area Majority / Influence, Auction / Biddi… |
| 7 | 54043 | Jaipur | 2009 | 52322 | 7.467 | 7.697 | 7.192 | **0.505** | 0.005 | 0.005 | 0.495 | 7.687 | 1.46 | 30 | Arabian, Card Game, Economic | End Game Bonuses, Hand Management, Hidden Victory Points, M… |
| 8 | 12942 | No Thanks! | 2004 | 28146 | 7.070 | 7.380 | 6.896 | **0.484** | 0.007 | 0.007 | 0.470 | 7.366 | 1.13 | 20 | Card Game | Auction / Bidding, Closed Economy Auction, Push Your Luck, … |
| 9 | 173346 | 7 Wonders Duel | 2015 | 93399 | 8.054 | 8.257 | 7.796 | **0.461** | 0.004 | 0.004 | 0.453 | 8.250 | 2.23 | 30 | Ancient, Card Game, City Building, Civilization, Econo… | End Game Bonuses, Income, Melding and Splaying, Modular Boa… |
| 10 | 124361 | Concordia | 2013 | 41255 | 8.075 | 8.455 | 7.999 | **0.457** | 0.006 | 0.006 | 0.445 | 8.444 | 2.99 | 100 | Ancient, Economic, Nautical | Action Retrieval, Advantage Token, Auction: Dutch, Deck, Ba… |

> **Scale note:** even at 25k+ residual max is **0.746** (For Sale, n=31,917, SE 0.007) — far smaller than low-n tail (3.94) because shrinkage is negligible (w≈1) and residual variance narrows (SD 0.357 vs 0.732 at 1–99). A 0.4–0.7 residual at 25k+ is **more precisely estimated** than 1.5–2.0 at 1–99 and survives the SE bound (SE ≈0.006, so residual ≈ residual_lb).

## Caveats & limitations

- **15 games excluded from estimation** (missing `weight`): Museum Heist (220541), Gloomier: A Night at Hemlock Hall (316850), Abducktion: Base + Expansion (405877), Rory's Story Cubes: Medic (165521), Roulette-Taking Game (362830), Nuts a GoGo! (374212), Holiday Hijinks #4: The Cupid Crisis (345046), Mythic Mischief: Headmaster's Box (347747), Under My Bed (194640), Unlock!: Timeless Adventures – Arsène Lupin… (327913), Marvel Dice Masters: Iron Man… (202096), Dia de los Muertos (210937), Too Many Cooks (368045), Murray the A**hole Frog (416494), Mind Map (401409). They appear in population but not in residuals — band counts above reflect 16,549, not 16,564.
- **Measurement-error-in-X not modeled** (e.g., weight with noise); tags overlap; category/mechanic indicators are descriptive contrasts, not causal effects (`phase6_comparative.json` limitations).
- **Severity adjustment removes additive rater level only**; within-game selection beyond global severity was ~0 in Phase 4 (`phase4_selection.json`) but non-additive forms remain untested.
- **No external broad-appeal validation**; residual screens conditional anomalies only. Do not build a hidden-gem score from residuals alone — this task explicitly preserves underratedness vs hidden gems vs broad appeal.
- **Do not modify Phase 6 model/residual/population**: this file re-presents the current `Q3b/OLS` residual unchanged; no new population filters or re-weightings applied.

## Files & reproducibility

- `docs/phase6-intermediate/top_positive_residuals_by_volume.csv` — machine-readable (same 90 rows, 22 columns, committed alongside this md; `vol_band` uses hyphen `1-99` for CSV compatibility).
- Rerun: `python scripts/31_phase6_expected_quality_underratedness.py --active-dir scratch/phase2-active --population scratch/phase2-active/bgg_research_population.parquet --out-dir scratch/phase2-active` regenerates `phase6_residuals_active.parquet` (this table's source) under bounded DuckDB (`memory_limit 4gb`, `threads 3`, `temp_directory scratch/ducktmp`, copy-once to `scratch/phase2-active`).
- Also validated against `docs/phase2-active/phase6_comparative.json`, `reports/phase6_underratedness/*`, `data/processed/phase2-active/game_adjusted_means_active.parquet` (see Provenance).

---
_Generated 2026-08-24 from `scratch/phase2-active/phase6_residuals_active.parquet` (n=16,549, mu 7.144, sigma_e 1.194) via `scripts/31` Q3b/OLS; buckets are VOL_BAND_EDGES as above. Intermediate / not final._
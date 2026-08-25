# Absolute Quality Threshold Analysis — Pass-2 `adj_mean`

**Generated:** 2026-08-25T11:20:29Z · seed 20260824 · population 14,698 (mu=7.139, sigma_e=1.193, SE=sigma_e/sqrt(n)) · weight 7 null median-filled 2.0 + flag.

## Distribution (§1 excerpts for quality)

| stat | adj_mean | interpretation |
|---|---|---|
| mean | 6.883 | near mu 7.139 (severity-adjusted quality) |
| SD | 0.847 | cross-game variation |
| p50 | 6.925 | median game |
| p75 | 7.466 | top 25% |
| p90 | 7.931 | top 10% (1,470 games) |
| p95 | 8.185 | top 5% (736 games) |
| p99 | 8.628 | top 1% (147 games) |
| p10 | 5.782 | lower tail |

Histograms: `distributions_histograms.png` (adj_mean, resid_Q3bFam, n_obs, SE). Scatter: `distributions_vs_n_and_se.png`.

**Quantiles reused from §1:** task suggested `7.0` (+0.86 SD above mu), `7.5`, `8.0`, plus data-driven p90/p95 top 10%/5% by adj_mean. SE median 0.0641, p10 (large SE, low n) 0.1076, p90 (small SE, high n) 0.0212; see band table below.

## Candidates (§2 of task)

| threshold | description | games pass | share | median n | p10–p90 n | median SE | median resid_Q3bFam |
|---|---|---|---|---|---|---|---|
| 7.000 | above global mean +0.86 SD (modest) | 6800 | 46.3% | 595 | 136–6014 | 0.0489 | +0.21 |
| 7.500 | Step 9 high-quality flag (top 30% of Q3bFam residuals fail this in task) | 3446 | 23.4% | 706 | 136–8788 | 0.0449 | +0.28 |
| 8.000 | strong | 1245 | 8.5% | 614 | 132–10492 | 0.0482 | +0.38 |
| 7.931 | data-driven p90 by adj_mean (top 10%) | 1470 | 10.0% | 615 | 133–10307 | 0.0481 | +0.37 |
| 8.185 | data-driven p95 by adj_mean (top 5%) | 735 | 5.0% | 580 | 132–11292 | 0.0496 | +0.42 |
| 7.466 | p75 by adj_mean (top 25%) | 3675 | 25.0% | 691 | 136–8505 | 0.0454 | +0.27 |
| 8.628 | p99 by adj_mean (top 1%) | 147 | 1.0% | 571 | 141–8080 | 0.0499 | +0.55 |

*Extra quantiles for reference included (p75, p99).*

- `adj_mean ≥7.0` is **modest**: requires only +0.86 SD above mu, passes 46.3% — almost half the population. By itself it selects generally good games but with little discrimination (median residual only ~+0.21).
- `adj_mean ≥7.5` is **Step 9's high-quality flag**: passes 23.4% (3,446). Of top-1% Q3bFam residuals (≥1.19), 68% pass and 32% fail — confirming Step 9's finding that high residual alone is not high quality (30% fail reproduced: 69% pass).
- `adj_mean ≥8.0` is **strong**: only 8.5% pass, median resid +0.38, selects heavier/higher-n games (median n 614).
- Data-driven `p90=7.93` (top 10%) and `p95=8.19` (top 5%) are very stringent; they would themselves be the primary filter if quality alone were the goal, but joint screening keeps 7.5 as qualifier.

## n / SE relationship

| vol_band | games | median n | median adj_mean | median SE |
|---|---|---|---|---|
| 100-199 | 4534 | 139 | 6.645 | 0.1012 |
| 200-499 | 4263 | 300 | 6.758 | 0.0689 |
| 500-999 | 2208 | 679 | 6.985 | 0.0458 |
| 1k-2.5k | 1875 | 1492 | 7.174 | 0.0309 |
| 2.5k-5k | 879 | 3376 | 7.385 | 0.0205 |
| 5k-10k | 471 | 6636 | 7.535 | 0.0147 |
| 10k-25k | 330 | 14724 | 7.674 | 0.0098 |
| 25k+ | 138 | 36966 | 7.809 | 0.0062 |

- SE = 1.193/sqrt(n): low-n games (100–199, median SE ~0.10) have ≈5× the uncertainty of high-n (25k+ SE ~0.006). Any quality threshold treats them equally as point estimates — see `uncertainty_analysis.md`.

## Examples near thresholds

**Near `adj_mean = 7.0` (±0.07, sorted by adj_mean):**

| game_id | title | year | n_obs | adj_mean | SE | expected_Q3bFam | resid | vol_band |
|---|---|---|---|---|---|---|---|---|
| 17925 | Anno Domini: Im Namen des Gesetzes | 2003 | 132 | 6.999 | 0.1039 | 5.848 | +1.151 | 100-199 |
| 113401 | Timeline: Events | 2011 | 5070 | 6.999 | 0.0168 | 6.729 | +0.270 | 5k-10k |
| 175088 | Pharaoh's Gulo Gulo | 2015 | 346 | 7.000 | 0.0642 | 6.279 | +0.720 | 200-499 |
| 279720 | Streets | 2021 | 1767 | 7.000 | 0.0284 | 7.474 | -0.474 | 1k-2.5k |
| 195180 | Universal Rule | 2017 | 148 | 7.000 | 0.0981 | 6.839 | +0.161 | 100-199 |
| 22398 | 10 Days in Asia | 2007 | 1185 | 7.000 | 0.0347 | 6.506 | +0.494 | 1k-2.5k |

**Near `adj_mean = 7.5` (±0.07, sorted by adj_mean):**

| game_id | title | year | n_obs | adj_mean | SE | expected_Q3bFam | resid | vol_band |
|---|---|---|---|---|---|---|---|---|
| 354669 | Break the Cube | 2022 | 228 | 7.500 | 0.0790 | 7.117 | +0.383 | 200-499 |
| 380134 | Orion Duel | 2023 | 493 | 7.500 | 0.0537 | 7.250 | +0.250 | 200-499 |
| 6719 | Liberty: The American Revolution 1775-83 | 2003 | 494 | 7.500 | 0.0537 | 7.035 | +0.465 | 200-499 |
| 182082 | Carcassonne: Over Hill and Dale | 2015 | 802 | 7.500 | 0.0421 | 6.833 | +0.668 | 500-999 |
| 254683 | Dodos Riding Dinos | 2021 | 1280 | 7.500 | 0.0334 | 7.190 | +0.310 | 1k-2.5k |
| 166859 | Web of Spies | 2014 | 184 | 7.500 | 0.0880 | 6.520 | +0.981 | 100-199 |

**Near `adj_mean = 8.0` (±0.07, sorted by adj_mean):**

| game_id | title | year | n_obs | adj_mean | SE | expected_Q3bFam | resid | vol_band |
|---|---|---|---|---|---|---|---|---|
| 416851 | Castle Combo | 2024 | 3104 | 7.999 | 0.0214 | 7.837 | +0.162 | 2.5k-5k |
| 347218 | Dickory | 2021 | 160 | 8.000 | 0.0943 | 7.062 | +0.938 | 100-199 |
| 302098 | Chronicles of Crime: 1900 | 2021 | 1809 | 8.000 | 0.0281 | 7.509 | +0.491 | 1k-2.5k |
| 234167 | Masters of Mutanite | 2022 | 103 | 8.001 | 0.1176 | 7.327 | +0.673 | 100-199 |
| 271615 | The Quest for El Dorado: The Golden Temples | 2019 | 1744 | 8.001 | 0.0286 | 7.212 | +0.789 | 1k-2.5k |
| 3416 | Fallschirmjaeger: The Airborne Assault on Fortress Holland | 2001 | 192 | 8.001 | 0.0861 | 7.147 | +0.855 | 100-199 |


**Weight-missing games in primary pool (median-filled 2.0, flag=1):**

 game_id                                                                   title  n_obs  adj_mean  resid_Q3bFam  weight
  347747                                       Mythic Mischief: Headmaster's Box    157  8.074593      0.876252     2.0
  327913 Unlock!: Timeless Adventures – Arsène Lupin und der große weiße Diamant    138  7.835265      0.912356     2.0

## Interpretation (claim-tagged)

- **Observed fact:** quantiles, counts, SE distribution above are from Pass-2 data.
- **Empirical finding (model-dependent for resid):** median resid shifts with quality threshold as shown.
- **Model-dependent conclusion:** `7.5` is recommended as primary quality gate because it is stringent enough to mark genuinely good (top quartile) yet permissive enough to retain a useful underratedness pool; `7.0` and `8.0` are kept as sensitivity.

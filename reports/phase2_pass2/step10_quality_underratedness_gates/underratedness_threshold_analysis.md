# Underratedness Threshold Analysis — Pass-2 Q3bFam Residual

**Generated:** 2026-08-25T11:20:29Z · seed 20260824 · Q3bFam residual = adj_mean − expected_Q3bFam (mean ~0, SD 0.531, p50 0.03, p75 0.33, p90 0.61, p95 0.80, p99 1.18). Q4Fam SD 0.522.

## Distribution (§1 excerpts for residual)

| stat | Q3bFam residual | Q4Fam residual | note |
|---|---|---|---|
| SD | 0.531 | 0.522 | task stated 0.531 for Q3bFam (actual 0.531) |
| p90 | 0.612 | 0.600 | task p90 0.75 (actual slightly lower) |
| p95 | 0.804 | 0.797 | task p95 0.85 / 0.80 actual |
| p99 | 1.178 | 1.164 | task 1.2 |

Histogram: `distributions_histograms.png` panel 2; residual-vs-n correlation +0.0128 (~0 by construction).

## Candidates (§3 of task)

| resid threshold | description | Q3bFam pass | Q3bFam share | Q4Fam pass | robust (both ≥thr / Q3bFam) | overlap adj≥7.5 | median n | median SE |
|---|---|---|---|---|---|---|---|---|
| 0.500 | approx +1 SD (task) | 2175 | 14.8% | 2096 | 1896/2175 (87%) | 1062 | 270 | 0.0726 |
| 0.750 | approx p90 (task, p90 0.61) | 911 | 6.2% | 865 | 775/911 (85%) | 532 | 235 | 0.0779 |
| 1.000 | approx p95 (task, actual p95 0.80) | 330 | 2.2% | 315 | 276/330 (84%) | 211 | 204 | 0.0836 |
| 1.190 | Step 9 top 1% cutoff (task) | 145 | 1.0% | 135 | 116/145 (80%) | 98 | 193 | 0.0859 |
| 0.612 | data-driven p90 Q3bFam | 1470 | 10.0% | 1394 | — | 780 | 254 | 0.0750 |
| 0.804 | data-driven p95 Q3bFam | 735 | 5.0% | 710 | — | 450 | 223 | 0.0799 |
| 1.178 | data-driven p99 Q3bFam | 147 | 1.0% | 140 | — | 100 | 193 | 0.0859 |

- `≥0.50` (~1 SD, actually 0.94 SD) passes 2,175 — too permissive as sole filter (includes p75).
- `≥0.75` (~1.4 SD, near p96) passes 911; robust to Q4Fam: many remain ≥0.75 under mechanics (see robust column). Recommended as **primary underratedness gate**.
- `≥1.00` (~1.9 SD, p~98.5) passes 330 — stringent, precision gate.
- `≥1.19` (Step 9 top-1% cutoff) passes 145 — very stringent, top 1% by residual.
- Data-driven p90/p95/p99 rows show same distribution: p90 0.61 (1,471), p95 0.80 (736), p99 1.18 (148) — task's rounded estimates (0.75 p90 etc.) were slightly high vs. Q3bFam empirical; task values retained as named thresholds for comparability.

**Q4Fam robustness:** overall Spearman Q3bFam vs Q4Fam 0.9775, top-1% Jaccard 0.728. At `0.75`, of 911 Q3bFam passers, many also pass under Q4Fam (see primary vs sensitivity). Jaccard improves from resid-only to joint gates (see `primary_vs_sensitivity_comparison.md`).

## Overlap with quality

For each residual thr, `overlap_adj_ge_7.5` shows how many also clear quality. At `0.75`, 532 of 911 (58%) also have adj≥7.5 — **42% of highly-underrated games are not high-quality in absolute terms** (e.g., 6.5-rated games expected 5.7). This is why joint gating matters (see `joint_gate_analysis.md`).

## Examples near thresholds

**Near `resid_Q3bFam = 0.50` (±0.07):**

| game_id | title | year | n_obs | adj_mean | expected_Q3bFam | resid_Q3bFam | resid_Q4Fam | vol_band |
|---|---|---|---|---|---|---|---|---|
| 940 | Karawane | 1990 | 172 | 6.38 | 5.88 | +0.50 | +0.41 | 100-199 |
| 123239 | Wits & Wagers Party | 2012 | 2554 | 7.11 | 6.61 | +0.50 | +0.44 | 2.5k-5k |
| 150294 | COGZ | 2015 | 194 | 7.13 | 6.63 | +0.50 | +0.55 | 100-199 |
| 400617 | Mythic Mischief Vol. II | 2024 | 112 | 8.13 | 7.63 | +0.50 | +0.46 | 100-199 |
| 96672 | TieBreaker | 2011 | 131 | 6.15 | 5.65 | +0.50 | +0.45 | 100-199 |

**Near `resid_Q3bFam = 0.75` (±0.07):**

| game_id | title | year | n_obs | adj_mean | expected_Q3bFam | resid_Q3bFam | resid_Q4Fam | vol_band |
|---|---|---|---|---|---|---|---|---|
| 268665 | Suzume-Jong | 2018 | 188 | 7.42 | 6.67 | +0.75 | +0.77 | 100-199 |
| 310067 | Scooby-Doo! The Board Game | 2022 | 407 | 7.28 | 6.53 | +0.75 | +0.66 | 200-499 |
| 264295 | Fabulantica | 2018 | 165 | 7.27 | 6.52 | +0.75 | +0.64 | 100-199 |
| 296164 | Yura Yura Penguin | 2019 | 211 | 7.39 | 6.64 | +0.75 | +0.73 | 200-499 |
| 40529 | Cosmic Encounter | 1991 | 1047 | 7.57 | 6.82 | +0.75 | +0.75 | 1k-2.5k |

**Near `resid_Q3bFam = 1.00` (±0.07):**

| game_id | title | year | n_obs | adj_mean | expected_Q3bFam | resid_Q3bFam | resid_Q4Fam | vol_band |
|---|---|---|---|---|---|---|---|---|
| 208428 | No Thank You, Evil! | 2016 | 326 | 7.48 | 6.48 | +1.00 | +0.92 | 200-499 |
| 367432 | On to Richmond II: The Union Strikes South | 2023 | 102 | 9.50 | 8.50 | +1.00 | +1.00 | 100-199 |
| 250396 | Terminator Genisys: Rise of the Resistance | 2018 | 605 | 8.03 | 7.03 | +1.00 | +0.98 | 500-999 |
| 147884 | Ore: The Mining Game | 2013 | 116 | 7.57 | 6.57 | +1.00 | +1.03 | 100-199 |
| 336755 | King of Tokyo: Monster Box | 2021 | 1226 | 7.81 | 6.81 | +1.00 | +1.01 | 1k-2.5k |

**Near `resid_Q3bFam = 1.19` (±0.07):**

| game_id | title | year | n_obs | adj_mean | expected_Q3bFam | resid_Q3bFam | resid_Q4Fam | vol_band |
|---|---|---|---|---|---|---|---|---|
| 32944 | Neue Heimat | 2007 | 793 | 8.02 | 6.84 | +1.18 | +1.11 | 500-999 |
| 295694 | Catchy! | 2019 | 106 | 7.67 | 6.48 | +1.18 | +1.16 | 100-199 |
| 248878 | FlickFleet | 2019 | 214 | 8.14 | 6.95 | +1.19 | +1.14 | 200-499 |
| 32129 | Taktika | 2007 | 193 | 7.38 | 6.19 | +1.19 | +1.16 | 100-199 |
| 386906 | Bohnanza: Dahlias | 2023 | 140 | 8.05 | 6.86 | +1.19 | +1.27 | 100-199 |

## Interpretation (claim-tagged)

- **Observed fact:** counts, quantiles are from Pass-2 game-level data.
- **Empirical finding (model-dependent):** residual magnitudes, Q4Fam robustness, overlap with quality are conditional on Q3bFam/Q4Fam specifications (CV R² 0.603/0.615).
- **Model-dependent conclusion:** `0.75` marks meaningfully better-than-expected (≈p96, 1.4 SD) at useful pool size; `1.00` as stricter sensitivity.

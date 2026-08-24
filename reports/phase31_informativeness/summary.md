# Phase 3.1 — Rater informativeness beyond global severity

**Population:** 16,627 research-population games × users with ≥10 in-universe ratings, excluding `degenerate_strict` (`data/processed/phase2-active/`, 24,509,788 obs, 288,730 users, 16,564 games). Reuses refreshed baseline `user_severity_active.parquet` (`mu=7.144`, `delta_full/even/odd`) and `game_adjusted_means_active.parquet` from `scripts/26` — no refit. Bounded DuckDB `memory_limit 4GB`/`threads 3`/`temp_directory scratch/ducktmp`; one even/odd `rating_observation_id %2` split; `scratch/phase2-active` copies.

Question: after global severity `delta_u`, does lifetime rating experience predict more **informative or discriminating** individual ratings? Five severity-adjusted tests across bands `10-24..1000+` and cumulative `t=10,20,50,100`.

## Tiered summary (severity-adjusted lens)

Full per-band tables in `tiered_summary.csv` and `phase31_informativeness.json`.

| Band | n_users | mean SD raw | mean SD resid | entropy | share10 raw→adj | mean r vs consensus | within RMSE x | LOO RMSE x |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| 10-24 | 95,343 | 1.289 | 1.150 | 1.961 | 11.77%→4.98% | 0.441 | 1.630 | 1.204 |
| 25-49 | 71,545 | 1.323 | 1.155 | 2.171 | 8.01%→5.34% | 0.480 | 1.657 | 1.206 |
| 50-99 | 56,925 | 1.319 | 1.142 | 2.245 | 5.97%→5.26% | 0.497 | 1.665 | 1.195 |
| 100-249 | 44,002 | 1.309 | 1.132 | 2.280 | 4.10%→4.88% | 0.502 | 1.669 | 1.187 |
| 250-499 | 14,410 | 1.313 | 1.139 | 2.312 | 2.66%→4.35% | 0.501 | 1.686 | 1.195 |
| 500-999 | 4,844 | 1.308 | 1.140 | 2.320 | 1.85%→3.73% | 0.495 | 1.678 | 1.190 |
| 1000+ | 1,059 | 1.324 | 1.164 | 2.328 | 1.44%→3.07% | 0.484 | 1.704 | 1.212 |

*Residual* `r = rating - adj_mean - delta` (rating SD 1.53, severity spread 1.04). `x = rating - delta` (severity-adjusted). Threshold `t=10→100`: mean SD resid `1.146→1.134` flat; mean r `0.475→0.501` flat; LOO `ge50 1.193 vs lt50 1.206` diff 0.013.

## Five dimensions

### 1. Scale discrimination — no advantage for heavy raters [Empirical finding]
- Within-user SD raw `1.29→1.32`, resid `1.15→1.16` flat within 0.03 points across 7 bands; threshold 1.308→1.310 raw, 1.146→1.134 resid.
- Entropy 1.96→2.33 bits then plateau; bins 4.8→9.2; modal 0.412→0.357.
- Raw spike at 10: 10-24 11.77% vs 1000+ 1.44% collapses after severity to 4.98% vs 3.07% (≥9: 29.9% vs 6.1% →22.9% vs 15.7%). Heavy "tightness" is severity, not discrimination.

### 2. Stability of own ratings — x rises with n as expected, taste does not [Empirical finding]
- `x = rating - delta` mean parity `r` (`x_even` vs `x_odd`, ≥5 per half): 0.285 (10-24) →0.931 (1000+), overall 0.455; `t10 0.455 →t100 0.787`. Rises because heavier have ~700 per half vs ~7, less noise — expected.
- Half-specific `r = rating - adj_mean - delta_half` parity: -0.001 to -0.071 across all bands — no stable taste beyond game+severity, replicating Phase 3 (`0.355` vs severity `0.877`).

### 3. Ordering vs consensus — flat [Empirical finding]
- Within-user `r(x, adj_mean)` (severity-invariant): 0.441/0.491 (10-24) →0.502/0.522 (100-249) →0.484/0.497 (1000+); overall 0.475/0.513; `t10 0.475 →t100 0.501`. Heavy does not order more like consensus.

### 4. Agreement with others — heavy not tighter [Empirical finding]
- Within-band pairwise RMSE `x`: 1.630 (10-24) →1.704 (1000+) — higher for heavy.
- Cross-band `x` RMSE: 10-24 vs 1000+ 1.79, vs 250-499 1.70 — cross > within.
- Raw anchor 1.86→1.96 → severity lowers ~0.23 but experience still not predictive.

### 5. Held-out predictive — flat after severity [Empirical finding]
- LOO RMSE `x`: 1.204→1.212 range 0.025 vs raw U-shape 1.33–1.49. Threshold ge50 1.193 vs lt50 1.206; ge100 1.192 vs lt100 1.201.
- Even→odd holdout: overall 1.372 raw→1.195 adj (severity gain 0.177) vs 1.20→1.21 across bands.

## Implication for estimator

**Severity adjustment is sufficient; do not weight by experience.** Game-level estimator `adj_mean = AVG(rating - delta)` with `mu=7.144` (scripts/26) needs no experience weighting or credibility score. LOO gain from experience 0.01 vs severity 0.23; R² taste +0.004 vs severity +0.193. No credible cutoff beyond `t=10 + degenerate_strict` warranted.

## Artefacts

- Script: `scripts/28_phase31_rater_informativeness.py` (bounded, scratch copies, rerunnable)
- Outputs: `data/processed/phase2-active/phase31_informativeness.json` + committed `docs/phase2-active/phase31_informativeness.json` + `reports/phase31_informativeness/phase31_informativeness.json` + `tiered_summary.csv` + `threshold_sensitivity.csv`
- Reproduce:
```bash
python scripts/28_phase31_rater_informativeness.py --active-dir scratch/phase2-active --population scratch/phase2-active/bgg_research_population.parquet --out-dir data/processed/phase2-active
```

## Limitations

- One even/odd split; `x` vs half-specific resid distinction needed due to full-data mean constraint.
- Within-sample holdout, not external broad-appeal validation.
- `degenerate_strict` excluded (667 users), `degenerate_broad` retained but not re-weighted.

## Claim tags per AGENTS.md

Observed facts (counts, shares, RMSE), empirical findings (band means, correlations, LOO), model-dependent (LOO/holdout with ALS adj_mean), supported conclusions (no weighting, no cutoff).


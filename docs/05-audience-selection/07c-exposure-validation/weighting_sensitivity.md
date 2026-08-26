# Weighting Sensitivity — Step 7C

Compare raw inverse propensity `1/p`, stabilized `p_marginal/p`, truncated (cap 20, and p95/p99) for corrected `p_true` (and sampled `p_sample` for reference). Do not materialize full 4.2B pairs.

## Weight Quantiles (per-game max_w, but also pooled rater-level? Here per-game aggregated)

| Scheme | median max_w | p95 max_w | p99 max_w | max max_w | median ESS | median ESS_ratio | Note |
|---|---|---|---|---|---|---|---|
| raw `1/p_sample` (sampled, for ref) | 9.3 | 44.8 | 96.3 | 377.2 | 231 | 0.72 |  |
| raw `1/p_true` (corrected, global shift) | 1449.4 | 7619.7 | 16565.6 | 65414.4 | 106 | 0.33 |  |
| stabilized `p_marginal/p_true` (global 0.00572) | 8.3 | 43.6 | 94.7 | 374.0 | 106 | 0.33 | stabilized scaled down by 0.0057, same ESS |
| truncated cap20 (on `1/p_true`) | 20 (capped) | 20 | 20 | 20 | 330 | 0.98 | truncation reduces max to 20, ESS recovers to 0.98 vs 0.33 |

**Finding:** Raw `1/p_true` weights are ~156× larger than sampled (median 1449 vs 9.3). Stabilized weights rescale to sampled magnitude (median 8.3) but ESS unchanged. Truncation at 20 caps extreme tails and recovers ESS_ratio from 0.33 to 0.55 median (approx sampled level).

### Sensitivity of adjusted quality `delta = prop_adj - adj_mean`

| Scheme | mean delta | median delta | mean |delta| | share |delta|≥0.2 | share ≥0.5 | std delta |
|---|---|---|---|---|---|---|
| sample raw | -0.006 | -0.006 | 0.060 | 3.9% | 0.2% | 0.091 |
| true raw | -0.015 | -0.016 | 0.133 | 20.8% | 2.3% | 0.191 |
| true stab | -0.015 | -0.016 | 0.133 | 20.8% | 2.3% | 0.191 |
| true trunc cap20 | -0.001 | -0.000 | 0.016 | 0.2% | 0.0% | 0.030 |

**Per-type (true raw):**

| Type | mean delta_true | median | share |≥0.2 | share |≥0.5 |
|---|---|---|---|---|
| 18XX | -0.247 | -0.245 | 69.1% | 34.6% |
| Wargame | -0.044 | -0.028 | 31.6% | 4.7% |
| Party | -0.018 | -0.023 | 31.8% | 3.7% |
| Economic | +0.000 | -0.008 | 19.4% | 2.3% |
| Coop | -0.059 | -0.047 | 27.8% | 3.3% |
| Legacy | +0.025 | -0.003 | 11.8% | 0.0% |
| Other | -0.001 | -0.010 | 15.4% | 1.1% |

**Rank correlation (Spearman) vs adj_mean and between schemes:**

- `adj_mean` vs `prop_adj_raw_true`: Spearman 0.973 (high, but not 1 — reweighting preserves ranking broadly but niche shifts)
- `delta_raw_true` vs `delta_stab_true`: 1.000 (≈1.0, as expected constant scaling) — ranking identical.
- `delta_raw_true` vs `delta_trunc_true`: 0.455 — moderate, truncation reduces extreme deltas.
- `delta_raw_sample` vs `delta_raw_true`: high but not perfect (~0.85, estimated from earlier diff 0.01 median) — ordering preserved but magnitude differs.

**Top-percentile overlap (Jaccard):**

- Top 100 by `adj_mean` vs top 100 by `prop_adj_true`: Jaccard 0.626
- Top 1% (147 games) overlap: 0.561
- Top 100 `prop_adj_sample` vs `prop_adj_true`: 0.739 — sampled vs true top overlap high, indicating ranking robustness.

### Truncation Impact — Is it Needed for Stability?

- Median |delta_raw_true - delta_trunc| 0.016, but for 432 previously strongly sensitive games median reduction 0.22 (as in Step7B) — extreme weights dominate raw.
- With true scale, raw delta std 0.19 vs trunc std 0.03 — truncation dramatically reduces variance, but also attenuates signal (18XX mean -0.247 raw vs likely -0.05 trunc).
- **Recommendation:** Report raw `1/p_true` as primary sensitivity, but always show truncated cap20 (and p95/p99 variants) as sensitivity variation. If truncation materially changes conclusions (e.g., 18XX sensitivity disappears), flag as positivity issue, not as robust finding. Make explicit rather than hiding.

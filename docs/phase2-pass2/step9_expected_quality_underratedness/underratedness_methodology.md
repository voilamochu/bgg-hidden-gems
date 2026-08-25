# Underratedness Methodology — Pass-2

**Generated:** 2026-08-25T09:19:23Z
**Preferred spec:** Q3b / OLS (mu 7.139, sigma_e 1.193)
**Estimation sample:** 14,698 games

## Definition
`underratedness = adj_mean − expected_quality` where `expected_quality = E[adj_mean | characteristics]` under chosen spec.

- `adj_mean` is severity-adjusted quality (mu + alpha_g, reuse pass2, NOT refit).
- `expected_quality` is OLS fit from Q-ladder (Q3b primary: bands + ns_year + weight + playtime/players/reimpl + categories).
- **Do NOT interpret residual as quality; it is performance relative to expectation.** Keep quality / underratedness / hiddenness / audience-selection risk / broad-appeal evidence as separate dimensions per Step 8.

Per-game retained:
- `game_id`, `title`, `n_obs`, `adj_mean`, `expected_quality`, `underratedness` (residual), `SE_adj = sigma_e/sqrt(n_obs)`, `lower_bound_resid = residual −1.96*SE`, `lower_bound_adj = adj_mean −1.96*SE`, `model_spec` (Q3b), `volume_band`, robustness (`volume_decile`, `year`, `weight`), `users_rated`, `weight_missing`.

Outputs:
- `expected_quality_game_level.csv` (14,698 rows)
- `underrated_candidates.csv` top residuals (top 200 + top 5% = 734 rows, model-dependent)

## SE / lower bound
- Frequentist SE = sigma_e / sqrt(n_obs) (sigma_e=1.193). Posterior SD = 1/sqrt(1/sigma_alpha2 + n/sigma_e2) (sigma_alpha=0.844) — similar because sigma_alpha large vs SE; median SE 0.0641, p10 0.1076, p90 0.0212.
- Report both adj_mean ± SE and residual lower bound; do not treat point estimates equally precise.

## High residual vs absolute quality (§6)
**A high residual means “better than expected”, not “good”.** Required for hidden-gem pipeline (needs both genuine quality and underratedness).

- Scatter `residual_vs_quality_scatter.png`: residual vs adj_mean.
- **Top 1% residual** (cutoff +1.191, n=147): mean adj 7.88, median 7.89, share <7.0 4.1%, <6.5 0.0%, >=7.5 69.4%. So 4% of high-residual games would fail adj>=7.0, 0% fail >=6.5, only 69% meet >=7.5.
- **Top 5% residual** (cutoff +0.814): share <7.0 12.2%, >=7.5 62.0%.

Examples high residual / mediocre quality (top 1% with adj <7.0):
| game_id | title | year | n_obs | adj_mean | expected | resid | band |
|---------|-------|------|-------|----------|----------|-------|------|
| 7487 | Flutter | 1950.0 | 103 | 6.89 | 5.44 | +1.45 | 100-199 |
| 34450 | Bluff | 1973.0 | 160 | 6.84 | 5.40 | +1.44 | 100-199 |
| 9539 | Beat the 8 Ball | 1975.0 | 196 | 6.94 | 5.53 | +1.41 | 100-199 |
| 9300 | Clay-O-Rama | 1987.0 | 134 | 6.88 | 5.64 | +1.24 | 100-199 |
| 18057 | Anno Domini: Natur | 1998.0 | 257 | 6.98 | 5.76 | +1.22 | 200-499 |
| 3262 | The Powerpuff Girls: Villains at Large Game | 2000.0 | 169 | 6.70 | 5.49 | +1.22 | 100-199 |

- **Quantify thresholds:**
  - adj >=7.5: 69.4% of top1% residual, 62.0% of top5%
  - adj >=7.0: 95.9% / 87.8%
  - adj >=6.5: 100.0% / 99.5%

*Output makes clear: eventual hidden-gem screening requires **both** high adj_mean and high residual; many high residual games have modest absolute quality.*

## Robustness of underratedness ranking
- Q3b vs Q4 (mechanics sensitivity): spearman 0.974 Jaccard top1 0.728 top5 0.750
- Q3 vs Q3b (linear log vs band): 0.928 Jaccard 0.431
- OLS vs WLS_n (primary): 0.963 Jaccard 0.570
- Residual-volume corr after model: +0.0125 (should be ~0).
- Systematic: residual by weight/year/band flat (see step9_summary.json).

Identify whether population changes candidates: see `pass1_vs_pass2_comparison.md` (Jaccard top1 0.947).

## Limitations
- Residual is model-dependent (spec, bands, year spline, category threshold 500). Do not assume Q3b survives automatically — selected on evidence but sensitivity reported.
- Tags overlapping, not causal; weight measured with noise; no interactions.
- No external broad-appeal validation; residual screens conditional anomalies only.

Tags: model-dependent conclusion; assumption; empirical finding as labeled.

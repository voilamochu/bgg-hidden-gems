# Pass-2 Baseline Comparison — vs First-Pass Active and Historical Full Snapshot

**Generated:** 2026-08-24T15:54:07Z

**Populations:**
- Pass-1 Active: 16,627 games × ≥10 (minus degenerate_strict) → 24,509,788 obs / 288,730 users / 16,564 games with ≥1 rating (mu 7.144, R2 both 0.394) — `docs/phase2-active/active_baseline_refresh.json` @ bb2e991
- Pass-2 Final: 14,698 games × ≥10 × ≥100 × degenerate 0 → 24,146,307 obs / 287,302 users / 14,698 games (mu 7.139, R2 both 0.393) — `data/processed/phase2-pass2/pass2_baseline_refresh.json`
- Historical Full Snapshot: 95,540 games × all users → 26,924,709 obs / 571,248 users / 95,540 games (R2 both 0.438) — `data/processed/phase2/`

| Metric | Unit | Pass-1 Active | Pass-2 Final | Abs Change | % Change | Interpretation |
|---|---|---|---|---|---|---|
| mu (global mean rating) | rating points | 7.144 | 7.139 | -0.005 | -0.07% | Grand mean rating; -0.005 shift negligible vs SD 1.53 |
| pooled_gap_10-24_vs_1000+ | rating points | 1.2552 | 1.2521 | -0.0031 | -0.25% | Raw volume gap; -0.003 change <0.3% — stable |
| within_game_gap_10-24_vs_1000+ (paired) | rating points | 1.1081 | 1.0984 | -0.0097 | -0.88% | Within-game low vs high; -0.01 (-0.9%) stable, still +1.10 |
| within_game_gap_10-49_vs_500plus | rating points | 0.8287 | 0.8176 | -0.0111 | -1.34% | Broader low vs high; -0.011 (-1.3%) stable |
| game_FE_beta_10-24_vs_1000+ | rating points | 1.0578 | 1.0555 | -0.0024 | -0.23% | Fixed-effects regression; -0.002 (-0.23%) stable |
| severity_mean_10-24 | rating points | 0.268 | 0.2672 | -0.0008 | -0.30% | Low-volume rater generosity; stable +0.27 |
| severity_mean_1000+ | rating points | -0.7751 | -0.7726 | 0.0025 | -0.32% | High-volume severity; stable -0.77 |
| severity_spread (max-min mean_delta) | rating points | 1.0431 | 1.0398 | -0.0033 | -0.31% | Severity spread 1.04 → 1.04 stable; confirms additive severity not removed by improved population |
| R2_game_identity_only | variance explained | 0.2014 | 0.1997 | -0.0017 | -0.85% | Game explains ~20% variance; -0.0017 (-0.85%) stable |
| R2_rater_identity_only | variance explained | 0.2181 | 0.2182 | 0.0 | 0.02% | Rater explains ~22% variance; +0.0000 stable |
| R2_additive_both | variance explained | 0.3943 | 0.3931 | -0.0012 | -0.32% | Joint explains 39.4% → 39.3% stable |
| total_var | rating variance | 2.3541 | 2.3467 | -0.0073 | -0.31% | Total rating variance 2.35 → 2.35 stable |
| parity_pearson_min10_each_half | correlation | 0.8772 | 0.8768 | -0.0004 | -0.04% | Even/odd stability r 0.877 → 0.877 stable |
| median_abs_delta_diff | rating points | 0.167 | 0.1672 | 0.0002 | 0.15% | Parity noise median |diff| 0.167 → 0.167 stable |
| raw_gap_low_vs_high (500plus) | rating points | 1.055 | 1.0529 | -0.0022 | -0.21% | Gap decomposition raw gap 1.055 → 1.053 stable |
| std_gap_raw (common game weights) | rating points | 0.8916 | 0.8887 | -0.0029 | -0.32% | Standardized raw gap 0.892 → 0.889 stable |
| std_gap_severity_adjusted | rating points | -0.0343 | -0.0351 | -0.0008 | 2.28% | After severity gap closes to -0.03 → -0.035 stable; confirms gap is severity not game mix |
| holdout_RMSE_game_only | rating points | 1.4724 | 1.4841 | 0.0117 | 0.79% | Game-only holdout RMSE 1.472 → 1.484 (+0.8%) tiny increase, not material |
| holdout_RMSE_with_severity | rating points | 1.2378 | 1.244 | 0.0062 | 0.50% | With severity 1.238 → 1.244 (+0.5%) stable; severity still improves 0.23 RMSE |
| holdout_RMSE_raw_train_game_mean | rating points | 1.3724 | 1.3715 | -0.0009 | -0.06% | Raw train game mean RMSE stable |
| pearson_raw_vs_adj (game means) | correlation | 0.9794 | 0.9835 | 0.0041 | 0.42% | Raw vs adj game means r 0.979 → 0.983 stable; severity adjustment preserves ranking |
| spearman_raw_vs_adj | correlation | 0.98 | 0.9822 | 0.0022 | 0.22% | Rank correlation stable |
| corr_n_vs_shift (game) | correlation | 0.0171 | 0.0149 | -0.0022 | -12.68% | Correlation between n_obs and severity shift near zero; stable |
| n_observations | count | 24509788 | 24146307 | -363481 | -1.48% | Total observations 24.5M → 24.1M (-363k, -1.5%) due to 269 game prune + 4 users |
| n_users | count | 288730 | 287302 | -1428 | -0.49% | Users 288730 → 287302 (-1428, -0.49%) due to closure |
| n_games_with_ratings | count | 16564 | 14698 | -1866 | -11.27% | Games 16564 → 14698 (-1866, -11.3%) due to edition dedup + <100 filter |

**Historical full-snapshot reference (where useful):**

| Metric | Historical 95k | Pass-1 Active | Pass-2 Final |
|---|---|---|---|
| R2_game_identity_only_historical_full_snapshot | 0.23 | 0.20137406712911587 | 0.19966004821164895 |
| R2_both_historical | 0.438 | 0.3943211541852414 | 0.39307501512048915 |

**Interpretation — does improved population definition materially change empirical conclusions?**

- **Same-game volume gap remains additive severity:** pooled +1.255 → +1.252, within-game +1.108 → +1.098, FE beta +1.058 → +1.055 — all within 1% and still large vs rating SD 1.53. Share positive ~94% stable.
- **Global severity stable:** mu 7.144 → 7.139 (-0.07%), severity spread 1.04 → 1.04, 10-24 +0.27 → +0.27, 1000+ -0.78 → -0.77. Even/odd parity r 0.877 → 0.877 (median |diff| 0.167 stable).
- **R2 decomposition stable:** game 0.201 → 0.200 (-0.85%), rater 0.218 → 0.218, both 0.394 → 0.393. Historical full-snapshot 0.230/0.249/0.438 shows same ordering but slightly higher due to including 1-9 tail; pass2 shift is not toward historical, it's invariant.
- **Severity-adjusted game quality stable:** pearson raw vs adj 0.979 → 0.983, spearman 0.980 → 0.982, corr n vs shift ~0.01 stable. Shift quantiles p5 median p95: active (0.024, 0.293, 0.563) → pass2 (0.043, 0.295, 0.542) — tiny increase at p5 due to removing low-volume tail.
- **Gap decomposition stable:** raw gap 1.055 → 1.053, standardized raw 0.892 → 0.889, severity-adjusted -0.034 → -0.035 (gap still closed by severity, not game mix).
- **Holdout stable:** RMSE game-only 1.472 → 1.484 (+0.8%), with severity 1.238 → 1.244 (+0.5%); the 0.23 RMSE gain from severity remains.
- **Population change not material to conclusions:** -11% games, -0.5% users, -1.5% obs, but the underlying severity structure is invariant. The improved population definition removes edition duplicates and low-volume <100 games, but does not alter the volume-band gap or severity distribution.

**Conclusion:** Earlier Phase 2 empirical conclusions remain stable on the improved Pass-2 population. The only material population change is the -1866 game reduction (mostly low-volume editions) which does not shift R2 or severity. Use Pass-2 baseline (mu 7.139, R2 both 0.393, parity r 0.877) as definitive for Phase 3+ reruns.

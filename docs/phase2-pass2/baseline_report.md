# Phase 2 Pass-2 Statistical Baseline — Final Converged Population (14,698 / 287,302 / 24,146,307)

**Generated:** 2026-08-24T15:54:07Z
**Population:** 14,698 games / 287,302 users / 24,146,307 observations (converged 2 iterations, 4 degenerate removed, 0 violations). SEMI JOIN final_games × final_users on `rating_observations_pass2.parquet` (24,146,307) with `games_pass2.parquet` (14,698) and `users_pass2.parquet` (287,302, is_degenerate flags recomputed). Reproduction: `python scripts/40_phase2_pass2_baseline_refresh.py --pass2-dir data/processed/phase2-pass2` (bounded 4GB/3 threads, temp scratch/ducktmp).

**Methodology reference:** scripts/26 → 30 → 31 lineage (mu/delta/alpha, R2 decomposition, gap decomposition) as methodological reference, but all inputs pointed to `data/processed/phase2-pass2/` (24.1M obs, 14,698 games). No mixing of first-pass 24.5M or historical 26.9M into primary Pass-2 baseline.

## 1. Same-game rater-volume comparison

- Raw band means (pass2): 10-24 7.720 → 1000+ 6.468 (vs active 7.726→6.471)
- Pooled gap 10-24 vs 1000+ : 1.252 (active 1.255) — absolute change -0.0031
- Paired within-game 10-24 vs 1000+ : mean +1.098 (active +1.108), median +1.081, share positive 94.1% (active 93.7%)
- Game FE regression beta 10-24 vs 1000+ : +1.055 (SE 0.0095) vs active +1.058
- Interpretation: +1.10 within-game gap persists and is additive severity, not game mix; pass2 change -0.01 (-0.9%) is not material.

## 2. Global rater severity (mu / delta_u)

- Mu (grand mean): 7.1390 (active 7.1440) diff -0.0050 (-0.07%)
- Severity by band (mean delta): 10-24 0.267 (active 0.268) → 1000+ -0.773 (active -0.775); spread 1.040 vs 1.043
- Stability even/odd parity r: 0.877 (active 0.877) median |diff| 0.167
- Distribution: see `severity_by_band_pass2` in baseline.json; total var 2.347
- Interpretation: severity spread 1.04 stable; r 0.877 stable; the low-vs-high volume gap remains almost entirely additive rater-level level differences.

## 3. Game/rater variance decomposition (R2)

- R2 game identity only: 0.200 (active 0.201) historical full 0.230
- R2 rater identity only: 0.218 (active 0.218) historical 0.249
- R2 additive both (mu+alpha+delta): 0.393 (active 0.394) historical 0.438
- Interpretation: R2_game moves 0.201→0.200 (-0.85%) not material; decomposition stable.

## 4. Severity-adjusted game quality

- adj_mean = AVG(rating - delta_u); raw vs adj pearson 0.983 (active 0.979), spearman 0.982
- Corr n_obs with shift: 0.0149 (active 0.0171) near zero
- Shift quantiles p5 median p95: pass2 [0.04278976955555587, 0.2948761815662979, 0.5422259191332787] vs active [0.02430806888336129, 0.29305642074567295, 0.5626250384255147]
- Note: Var(adj) / sigma_alpha / lambda are Phase 5 quantities (not recomputed in baseline refresh); baseline provides adj_mean distribution for Phase 5 rerun.

## 5. Gap decomposition

- Raw volume gap (10-24 vs 500plus standardized): 0.889 (active 0.892)
- Severity-adjusted gap: -0.035 (active -0.034) — gap closed to -0.03 remains
- Unweighted cellmean gaps and support overlap: see baseline.json `standardized_decomposition_pass2` and `support_overlap_pass2`
- Interpretation: raw gap still severity-driven, not game mix; improved population does not change conclusion.

## 6. Other baseline outputs (holdout)

- Holdout RMSE game-only: 1.484 (active 1.472)
- Holdout RMSE with severity: 1.244 (active 1.238) — improvement 0.23 stable
- Improvement by test user band: see `holdout_improvement_by_test_user_band_pass2` in baseline.json

## Comparison vs First-Pass and Historical

See `comparison_vs_first_pass.json` and `comparison.md` for full table with absolute/percentage change per metric and interpretation. Historical full-snapshot (26.9M, 95,540, R2 both 0.438) provided for reference; Pass-2 R2 0.393 vs active 0.394 vs historical 0.438 — Pass-2 does not move toward historical, it remains stable, confirming that the 100/10 + degenerate filtering already removed the 1-9 tail effect.

## Provenance / Reproduction

- Population: `data/processed/phase2-pass2/final_games.csv` (14,698) + `final_users.csv` (287,302) as authoritative membership lists
- SEMI JOIN logic: `SELECT r.* FROM read_parquet('rating_observations_pass2.parquet') r SEMI JOIN final_games ON game_id SEMI JOIN final_users ON user_pseudouserid`
- Baseline command: `python scripts/40_phase2_pass2_baseline_refresh.py --pass2-dir data/processed/phase2-pass2 --population data/processed/bgg_research_population.parquet --phase2-dir data/processed/phase2 --out-dir data/processed/phase2-pass2` (bounded 4GB/threads 3/temp scratch/ducktmp, narrow single-scan aggregations)
- Also: `python scripts/39_phase2_pass2_audit_closure_rebuild.py` for audit+closure+rebuild (2 iterations, 4 degenerate removed)
- Validation: see `validation.json` (Parquet layer, 7 checks, 0 violations) and `pass2_baseline_validation.json` (baseline, 0 violations)
- Artefacts: `data/processed/phase2-pass2/` (parquets) + `docs/phase2-pass2/` (baseline.json, comparison, README) + `reports/phase2_pass2/` (mirrors) — distinct from `docs/phase2-active/` (first-pass)

## Stability summary

**Which earlier conclusions remain stable?** All Phase 2 empirical conclusions remain stable: +1.10 within-game gap → still additive severity, R2 both 0.394→0.393, r 0.877 stable, severity spread 1.04 stable, gap closed to -0.03 after severity. No conclusion changes.

**Which conclusions changed?** None materially; R2_game moves 0.201→0.200 (-0.85%) is trivial. The only nominal change is holdout RMSE +0.01 (+0.8%) due to slightly smaller training set (24.1M vs 24.5M) — not a substantive shift.

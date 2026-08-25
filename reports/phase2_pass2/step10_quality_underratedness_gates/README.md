# Step 10 — Quality and Underratedness Screening Thresholds (Pass-2)

**Generated:** 2026-08-25T11:20:29Z · seed 20260824 · STOP after Step 10: hiddenness/audience-selection NOT applied.
**Population (canonical):** 14,698 games × 287,302 users × 24,146,307 rating observations, `data/processed/phase2-pass2/` (validated mu=7.139, sigma_e=1.193, `user_severity_pass2.parquet` + `game_adjusted_means_pass2.parquet` via scripts 39/40 — **reuse confirmed, NOT refit**).
**Expected-quality models:** **Q3bFam primary** (48 features: bands + ns_year + structure + categories≥500 + `fam_18XX`+`fam_Cooperative Game`+`fam_Legacy Game`, CV R² 0.6033, RMSE 0.5331) and **Q4Fam sensitivity** (78 features, CV 0.5251 R² 0.6151). Q3b baseline CV 0.5987 for 18XX comparison.

## Recommended gates (primary + sensitivities)

| Gate | Quality `adj_mean` | Underratedness `resid_Q3bFam` | Pool (Q3bFam) | Pool (Q4Fam) | Jaccard | Note |
|---|---|---|---|---|---|---|
| **Primary** | ≥7.5 | ≥0.75 | 532 | 489 | 0.817 | Moderate quality + high underratedness (~p90 resid); 3.6% of population |
| **Sensitivity strict** | ≥7.5 | ≥1.00 | 211 | 194 | 0.792 | Higher underratedness bar (≈p97); precision gate |
| **Sensitivity permissive** | ≥7.0 | ≥0.75 | 774 | 732 | 0.799 | Tests quality-gate sensitivity |
| **Uncertainty-aware (sensitivity)** | adj-1.96SE ≥7.0 | resid-1.96SE ≥0.50 | 1057 | — | — | Interpretable SE-aware check; retains 199% of primary point pool |

**Decision rationale:** `adj_mean ≥7.5` marks genuinely good (top 23.4% by quality; p75=7.47, p90=7.93; 69% of top-1% residuals pass it, 31% fail — so joint gate materially filters). `resid ≥0.75` marks meaningfully better-than-expected (p~96, ≈1.4 SD; task's p90 0.61 / p95 0.80 bracketing). Joint `7.5+0.75` yields 532 games — neither tiny (<20) nor huge (>2000) — with median n=256, median SE=0.0746. See `joint_gate_analysis.md` for why both components matter and `uncertainty_analysis.md` for SE handling.

## Pool sizes & distributions

- **Quality alone:** `≥7.0` 6,800 (46.3%), `≥7.5` 3,446 (23.4%), `≥8.0` 1,245 (8.5%), p90 top-10% (7.93) 1,470, p95 top-5% (8.19) 736.
- **Underratedness alone (Q3bFam):** `≥0.50` 2,175 (14.8%), `≥0.75` 911 (6.2%), `≥1.00` 330 (2.2%), `≥1.19` 145 (1.0%); p90 0.61 (1,471), p95 0.80 (736), p99 1.18 (148).
- **Joint (examples):** `7.5+0.75` 532, `7.5+1.0` 211, `7.0+0.75` 774, `7.5+0.50` 1062. See `threshold_sensitivity.csv`.

## Uncertainty rule

- **Point estimates vs lower bounds:** Requiring `lower_bound = adj_mean - 1.96*SE ≥ threshold` or `resid - 1.96*SE ≥ threshold` heavily penalises low-n games (100–199 median SE 0.100). Primary pool retains 86% if only adj LB ≥7.5 is required, 64% if resid LB ≥0.75, 57% if both LBs required. Lenient rule `adj-1.96SE ≥7.0 & resid-1.96SE ≥0.50` is proposed as **interpretable sensitivity**, not primary: see `uncertainty_analysis.md`.
- **Low-n question:** 100–199 band games (n=4,534, 30.8% of population) need ≈0.20 higher point residual to remain convincing after SE penalty; the analysis proposes reporting LB alongside point estimate rather than mechanically raising the threshold.

## Primary vs sensitivity stability

- **Q3bFam vs Q4Fam (mechanics sensitivity):** Overall residual Spearman 0.9775, Pearson 0.9830; top-1% Jaccard 0.728, top-5% 0.767. Joint-gate Jaccards: `7.5+0.75` 0.817, `7.5+1.0` 0.792. Movers listed in `primary_vs_sensitivity_comparison.md` / `movers_Q3bFam_to_Q4Fam_top20.csv`.
- **Q3b vs Q3bFam (family correction impact):** Spearman 0.9928; For `7.5+0.75`, Q3b pool 550 → Q3bFam 532 (lost 38, gained 20); **31 of 38 lost are 18XX** (81% of correction). 18XX previously inflated: its mean resid fell from +0.68 to ~0. For `7.5+1.0`, 21 of 31 lost are 18XX. Thus family correction **materially changes the pool by de-biasing 18XX**, but global ranking otherwise stable — as Step 9B intended. See `q3b_vs_q3bFam_comparison.csv` + `movers_Q3b_to_Q3bFam_top20.csv`.

## What is NOT yet applied

- **Hiddenness** (volume/visibility, not yet): requires additional screen for obscurity vs. popularity.
- **Audience-selection risk** (Step 7/7B/7C, not yet): wargame/miniatures/simulation etc. niche risks not filtered here.
- **Broad-appeal / taste heterogeneity** evidence (not yet): no cross-audience performance check.
- This pool is **preliminary — quality + underratedness only**, not a hidden-gem list. Preserves distinction: quality (`adj_mean`) / underratedness (residual) / hiddenness / audience-selection risk kept separate per Step 8.

## Data notes

- **7 weight-null games:** median-filled to 2.0 with `weight_missing` flag; 2 of them in primary pool (listed in `quality_threshold_analysis.md`).
- **Year sensitivity (Step 9B):** ns_year knots [1983, 2010, 2017, 2023]; linear-year variant leaves 18XX β +0.75→+0.68 and CV only -0.04, so family correction not artifact of year term.
- **n<50 families excluded:** none — all three Q3bFam families pass n≥50 gate (18XX 81, Cooperative 1,543, Legacy 50). No additional hidden filters.

## Files

- `screening_pool.csv` — preliminary pool under primary gate (`adj≥7.5 & resid≥0.75`, n=532) with Q3bFam primary + Q3b/Q4Fam comparison columns, SE, lower_bounds, volume_band.
- `threshold_sensitivity.csv` — per-gate counts under Q3bFam and Q4Fam + Jaccard.
- `step10_summary.json` — machine-readable all thresholds/quantiles/pools/overlaps.
- `quality_threshold_analysis.md` / `underratedness_threshold_analysis.md` / `joint_gate_analysis.md` / `uncertainty_analysis.md` / `primary_vs_sensitivity_comparison.md`
- Figures: `distributions_histograms.png`, `distributions_vs_n_and_se.png`, `band_summary_pass2.csv`

**Reproduce:** `python scripts/50_step10_quality_underratedness_gates.py` (game-level only, bounded scratch 4GB/3 threads, seed 20260824).

Tags: counts = observed fact; CV/coefficients/Jaccards = empirical finding (model-dependent); recommended gates = model-dependent conclusion per AGENTS.md claim-tagging.

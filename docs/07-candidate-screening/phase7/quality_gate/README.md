# Quality Gate — Absolute-Quality Floor for Robust Underrated Candidates (INTERMEDIATE / NOT FINAL RESEARCH OUTPUTS)

> **Status:** INTERMEDIATE / NOT FINAL RESEARCH OUTPUTS — screening stage, not a final hidden-gem ranking. This folder imposes a minimum absolute-quality requirement on the existing Phase 7 robust subset. It does not modify the Phase 7 population, residual definition, robustness rules, deduplication, or `n≥100` floor, and it does not score broad appeal.

## 1. What this gate is and why it exists

Phase 7 robust identifies games **strongly and robustly better than expected** (`resid = adj − expected`, `Q3b/OLS`, 910 games with `n≥200`, `resid≥0.60`, `min_alt≥0.30`, `z≥5`, `year<2025`, not duplicate-shadowed; see `docs/phase7-candidate-screening/README.md` §3). But a `resid 0.6` at `adj 6.2` vs `resid 0.6` at `adj 8.2` are not equivalent as hidden-gem candidates — the former is robustly underrated yet still **below-population-median quality**, the latter is robustly underrated **and actually good**.

This gate answers: *“What does ‘actually good enough to be a hidden-gem candidate’ mean operationally in this research?”* It does so on the `adj_mean` scale with an interpretable empirical anchor and with uncertainty baked in, so low-`n` high-`adj` games do not pass on noise.

**What it does not do:** it does not build a hidden-gem score, does not perform broad-appeal / manual candidate selection, and keeps `underratedness` (conditional anomaly, `resid`) vs `broad appeal` distinct — this gate is about **absolute quality**, not broad appeal.

## 2. Population and inputs

- **Starting set:** 910 robust underrated candidates from `../underrated_candidates.csv` (`16,549` estimation games; `16,627` population minus 15 missing weight/playtime). Robust definition reproduced for provenance — do not rerun Phase 5/6:

```
robust_underrated :=
  n_obs ≥200                        // P40≈215, P10=100; ensures SE ≤0.084 (vs 0.119 at 100)
  AND underratedness_pref ≥0.60     // ≈1.07 SD of resid SD 0.562; p91 among n≥200
  AND min_alt_resid ≥0.30           // stable positive across cv_pref, wls_pref, ols_Q3, wls_Q3
  AND z = resid/SE ≥5               // at n=200, 0.60 → z 7.1; min robust z is 7.2
  AND year <2025                    // exclude unreleased edge cases
  AND NOT duplicate-shadowed        // not flagged as less-popular edition/reimplementation (4× users rule)
```

  Full counts and n distribution in `../screening_summary.json`; n deciles: P10 100, median 293, P90 2796, mean 1480; robust n median 474, mean 913, P10 234, P90 2150.

- **Primary inputs (copy-once into `scratch/phase2-active` where applicable; DuckDB bounded `memory_limit 4GB / threads 3 / temp_directory scratch/ducktmp`):**
  - `docs/phase7-candidate-screening/underrated_candidates.csv` — 16,549 rows, 910 robust (this gate’s starting set)
  - `data/processed/phase2-active/game_adjusted_means_active.parquet` — `game_id, game_alpha, n_obs, raw_mean, adj_mean` (16,564 active games with ratings; `mu 7.144`)
  - `docs/phase2-active/phase5_quality_comparison.json` — adj quantiles, SE table, `sd_adj`, `sigma_e`, `sigma_alpha²`, held-out validation (adj beats raw/bayes)
  - `scratch/phase2-active/bgg_research_population.parquet` — complete 16,627 population for joins (complete where `games.parquet` is 80.89%)

## 3. Definitions carried from Phases 5–7

- **Quality estimator:** `adj_mean_g = AVG(rating − delta_u) = mu + alpha_g` (active ALS from `scripts/26`/`30`/`31`, `data/processed/phase2-active/game_adjusted_means_active.parquet`). Preferred per `phase5_quality_comparison.json` (held-out even→odd `RMSE adj 0.217` vs raw `0.410` vs bayes `1.338`; `R² adj 0.938` vs raw `0.779`). `bayes_rating` (prior 5.49, lambda 2500) correlates only 0.56 with adj and is not used as `y`. Report `adj` plus uncertainty, not point estimate alone.

- **Uncertainty:**
  - Frequentist `SE_g = sigma_e / sqrt(n_g)`, `sigma_e = 1.19407` (residual SD after `mu+alpha+delta`, `phase5_quality_comparison.json:eb_variance_components`).
  - Empirical Bayes `post_SD_g = 1 / sqrt(1/sigma_alpha² + n_g/sigma_e²)`, `sigma_alpha² = 0.746`, `lambda 1.91` (`post_SD` vs `SE` differ by <0.002 at `n≥200`; median robust `SE 0.055` vs `post 0.055`).
  - Lower bounds: `lower_1_96 = adj − 1.96·SE` (95% frequentist), `lower_1 = adj − 1·SE`, `lower_post1_96 = adj − 1.96·post_SD`. At `n=200` offset `1.96·SE 0.165`; at `n=474` (robust median) `0.108`; at `n=100` `0.234`. Robust `SE` table: median `0.055`, P10 (high n) `0.026`, P90 (low n among robust) `0.078`.
  - EB shrinkage `w = n/(n+lambda)` median `0.994` at `n=293` — negligible at robust n; no shrinkage gate needed.

- **Expected quality and residual:** `expected = Q3b/OLS` fitted mean (`X` as above, 46 features), `resid = adj − expected` (`phase6_residuals_active.parquet`, `docs/phase2-active/phase6_comparative.json`; CV `R² Q3b/OLS .582` vs Q3 `.570` vs Q4 `.585`; Q3b vs Q3 spearman `.985` Jaccard top1% `.675`; Q3b vs Q4 `.958/.579`; WLS degrades CV and is not used).

- **Active adj distribution (empirical anchor — DuckDB `quantile_cont` on 16,564 active `adj_mean`):**

| Quantile | adj | Share ≥ threshold | `adj − mu` (mu 7.144) | SD units (sd 0.872) |
|---|---|---|---|---|
| P10 | 5.80 | 90% | −1.34 | −1.54 |
| P25 | 6.39 | 75% | −0.75 | −0.86 |
| **P50** | **6.96** | **51.9%** | **−0.18** | **−0.21** |
| **P75** | **7.515** | **25.7%** | **+0.37** | **+0.43** |
| P90 | 8.01 | 10.2% | +0.86 | +0.99 |
| P95 | 8.28 | 5% | +1.13 | +1.30 |
| P99 | 8.77 | 1% | +1.63 | +1.86 |

  Active `adj` mean `6.926`, SD `0.872`. Active `lower_1_96 = adj −1.96·SE` quantiles: P10 `5.62`, P25 `6.23`, P50 `6.82`, P75 `7.38`, P90 `7.87` (median lower is 0.14 below median adj, as expected from median SE `0.070`).

## 4. Gates compared

All gates applied to the 910 robust (no change to population/residual). Each reported with N retained, adj/resid distributions among retained/excluded, sensitivity, overlap, empirical basis in `quality_gate_comparison.md` and machine-readable `quality_gate_summary.json`.

### A. Absolute adjusted-quality thresholds

`adj_mean ≥ 7.0, 7.3, 7.5, 7.6, 7.8, 8.0`

- 7.0 = P52, `mu−0.17SD` (barely above median; 48.1% of active ≥7.0) — very lenient floor.
- 7.3 = P66, `mu+0.18SD` — modest above-average.
- **7.5 = P74 (≈P75=7.515), `mu+0.41SD` (+0.36 above mu) — top quartile of active quality.**
- 7.6 = P77, `mu+0.52SD` — slightly stricter than 7.5.
- 7.8 = P85, `mu+0.75SD` — top 15%, clearly good.
- 8.0 = P90, `mu+0.98SD` — top decile, very good, stringent.

Sensitivity: `7.0→786, 7.3→654, 7.5→544, 7.6→492, 7.8→382, 8.0→274` (each 0.1 adj above 7.0 removes ~45–55 games).

### B. Adjusted-quality percentile thresholds

`adj ≥ P50 (6.959) → 799, P75 (7.515) → 534, P90 (8.009) → 265`

Mapping to A: P50 ≈ 7.0 (799 vs 786, +13), P75 ≈ 7.5 (534 vs 544, −10, 0.015 adj difference), P90 ≈ 8.0 (265 vs 274, −9). Either form is valid; percentile form has cleaner quantile anchor, round-number form is more readable.

### C. Lower-confidence-bound thresholds

`lower = adj − k·SE`, `k=1, 1.96` (and `post_SD` variant)

- `lower_1_96 ≥ 6.8 → 813`, `≥7.0 → 740`, `≥7.2 → 654`
- `lower_1 ≥ 7.0 → 760`, `≥7.2 → 679`
- `lower_post1_96 ≥7.0 → 740` (identical to `lower1.96≥7.0` at `n≥200` — EB adds nothing here)

Each lower threshold translates to an adj requirement that depends on n: at robust median `n=474 SE0.055`, `lower1.96≥7.0` requires `adj≥7.14`; at `n=200 SE0.084` requires `adj≥7.16`; at `n=3000 SE0.022` requires `adj≥7.04`. This bakes uncertainty so `adj 7.10 n220 SE0.081 lb6.94` fails while `adj 7.10 n4000` would pass.

### D. Reasonable combinations

`adj≥7.5 AND lower1.96≥7.0 → 544; adj≥7.3 AND lower1.96≥7.0 → 654; adj≥P75 AND lower1.96≥7.0 → 534`

**Empirical overlap finding:** for every adj threshold `≥7.3`, conjunction with `lower1.96≥7.0` retains exactly the same set as adj alone (`adj≥7.5 ∩ lower≥7.0 = adj≥7.5` with 0 additional exclusions; at worst case `n=200`, `adj≥7.5` implies `lb1.96≥7.335` >7.0). Lower’s value is guarding lenient floors: `adj≥7.0 ∩ lower1.96≥7.0` screens 46 borderline `adj 7.0–7.13` low-n games.

## 5. How to read the outputs

### `quality_gate_candidates.csv` (910 rows, one per robust candidate)

Sorted by `underratedness_pref` descending. Columns:

- `game_id, title, year, n_obs, users_rated_pop, rank_current, weight, cat_str` — identity (from `underrated_candidates.csv`).
- `adj_mean, se, post_sd, z, lb_adj (=adj−1.96·SE), lb_adj_post, lower_1 (=adj−SE), lower_1_96 (=adj−1.96·SE), lower_post_1_96` — quality and uncertainty.
- `expected_quality_pref, underratedness_pref, min_alt_resid, n_decile, vol_band_label` — residual and provenance.
- 20 gate flags (0/1 integers): `gate_adj_ge_7_0 … gate_adj_ge_8_0, gate_adj_ge_p50/p75/p90, gate_lower196_ge_6_8/7_0/7_2, gate_lower1_ge_7_0/7_2, gate_lower_post196_ge_7_0, gate_adj75_and_lower196_70, gate_adj73_and_lower196_70, gate_adj_p75_and_lower196_70, gate_adj75_and_lower1_70`.

### `quality_gate_summary.json`

Per-gate: `N_retained`, `retention_rate`, `adj_retained/excluded` (mean/median/p10/p25/p75/p90/min/max/sd), `resid_retained/excluded`, `lower196_retained/excluded`, `n_retained/excluded`, `se_retained`. Top-level: `sensitivity` grids (`adj_thresholds` 6.8–8.0; `lower196`/`lower1` 6.8–7.5), `empirical_basis` per gate (anchor string), `recommendation_preview`, `provenance`.

### `quality_gate_comparison.md`

Markdown tables per gate family (§1–4), sensitivity grids (§1 §3), retained vs excluded deltas (§5), anchor ranking (§6), and “what this gate does not do” (§7). Read §6 for the basis on which to choose a floor.

## 6. Interpretation — what “actually good enough” means operationally

No threshold is discovered ground truth; every cut is a method choice and must state its anchor. Among those compared, **top-quartile quality on the active adj distribution is the most defensible “good” standard**:

- **Recommended primary floor: `adj_mean ≥ 7.5` (equivalently `≥ P75 = 7.515`, 10-game difference).** Basis: P74–P75 of active quality, `+0.36` above `mu 7.144` (`+0.41 SD` of `sd 0.872`). Retains 544 of 910 (59.8%); excluded 366 have median adj 7.14 (still below P75) and include all `resid>1` at adj<7.5 with max excluded resid 1.49 — precisely the “underrated but mediocre” cases (e.g. `adj 6.19–6.48` with `resid 0.67–0.84`). Each 0.1 adj around 7.5 moves ~52–55 games, so sensitivity is smooth, not knife-edge.

- **Lenient alternative 7.3** (P66, `mu+0.18SD`, 654 retained) is possible if the next phase wants a larger starting set, but it keeps 110 games with `7.3≤adj<7.5` still below top quartile — weaker “good” claim.

- **Stringent alternative 7.8** (P85, `mu+0.75SD`, 382 retained) is clearly “good” (top 15%) but discards 162 more than 7.5 with only +0.19 median adj gain — useful only if the next phase needs a small, high-quality set.

- **Lower-bound companion: `lower_1_96 ≥ 7.0`.** Basis: 95% lower bound ≥ median-like 7.0 ensures the estimate is **confidently** not mediocre; at median n requires `adj≥7.14`. At `adj≥7.5` this adds no extra exclusion (544=544) given `n≥200`, so it need not be conjoined there; at a lenient `adj≥7.0` it screens 46 borderline low-n `adj 7.0–7.13` cases (e.g. `NFL Strategy adj7.02 n217 SE0.081 lb6.86` fails safely). Use `lower1.96≥7.0` as the uncertainty-aware floor when the adj floor is lenient, or report it alongside `adj≥7.5` for transparency without changing N.

All of this is **screening, not ranking** — the later broad-appeal screen (Phase 7B, `broad_appeal_evidence.md` taxonomy) starts from actually-good candidates; it does not combine residual and adj into a score here.

## 7. Limitations and open issues

- **Residual and adj are both model-dependent.** `adj` is the preferred quality estimator (held-out validation) but still `AVG(rating−delta)` under additive severity (`delta_u`); non-additive forms untested. `resid` is `Q3b/OLS` conditional anomaly; Q3b vs Q4 spearman .958, top1% Jaccard .579 — broad ordering stable but exact top list moves. `min_alt≥0.30` already guards cross-spec stability.

- **Low adj ≠ uninteresting — it signals niche appeal.** Excluded `adj 6.2–7.3` robust games (e.g. `Grave Robbers II 6.19, Magnificent Race 6.38`) are not “bad games”; they are robustly better-than-expected **for their characteristics** (often low-expected eras/genres) but below-good on the absolute scale. A different research question (niche excellence) would keep them; hidden-gem question does not.

- **Self-selection caveat** (`AGENTS.md` central problem): adj corrects additive rater-level level differences (`delta`) and sampling noise (`SE`), not who is in the sample. High resid + high adj can still reflect niche self-selection into the rater pool, not broad appeal — that distinction is Phase B’s job. Do not interpret passing the quality gate as broad-appeal evidence.

- **Threshold choice is not identified.** No method here estimates the population-wide counterfactual quality distribution; 7.5/P75 is chosen for its interpretable “top quartile” anchor and smooth sensitivity, not because the data reveal a natural break at 7.5. Report sensitivity (786→544→382→274) alongside any chosen N.

- **Coverage:** `adj` uses `bgg_research_population` (complete 16,627); `n_obs` is active `t≥10 minus degenerate_strict` (24.5M obs, 288,730 users, 16,564 active games). Games with `n<200` are already excluded from robust; within-robust `n` differences (417 vs 536 median) remain but `SE` handles them.

## 8. Provenance and rerun

- **Script/logic:** no new Phase 5/6 rerun; this gate is a filtering/comparison layer over `../underrated_candidates.csv` (generated by `scripts/32_phase7_candidate_screening.py`, bounded 4GB/3 threads, `temp_directory scratch/ducktmp`, `scratch/phase2-active` copy-once). Gate CSV+JSON built by bounded Python over the 910 robust (single scan, no wide-table bug, no full-snapshot rescan).
- **Computed ancillaries:** active `adj`/`lower` quantiles via DuckDB `quantile_cont` on `game_adjusted_means_active.parquet` (16,564 rows); `SE` formula from `phase5_quality_comparison.json`; gate flags as integer booleans.
- **Rerun:** re-derive `quality_gate_candidates.csv` + `quality_gate_summary.json` from `../underrated_candidates.csv` + `game_adjusted_means_active.parquet` using the gate definitions in §4; Markdown tables are views of `quality_gate_summary.json:sensitivity` + per-gate distributions.

*Tagging per `AGENTS.md`: retained/excluded counts and distributions are observed facts; threshold labels (“good”, “top quartile”) are method choices with stated empirical anchors; all `resid`/`adj`/`expected` values are model-dependent (Q3b/OLS, additive severity); broad-appeal implications are hypotheses, explicitly out of scope for this gate.*

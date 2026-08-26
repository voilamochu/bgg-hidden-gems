# Quality Gate Comparison (INTERMEDIATE / NOT FINAL RESEARCH OUTPUTS)

> **Status:** INTERMEDIATE screening — not a hidden-gem ranking. This document compares defensible ways to impose a minimum absolute-quality requirement on the **910 robust underrated candidates** (Phase 7). Residual alone does not establish that a game is actually good. Do not build a hidden-gem score from these tables.

## 0. Population and notation

- **Starting set:** 910 robust underrated candidates from `docs/phase7-candidate-screening/underrated_candidates.csv` — definition: `n≥200` (`SE≤0.084`, median `SE 0.055`), `resid≥0.60` (`Q3b/OLS` `adj − expected`), `min_alt≥0.30`, `z≥5`, `year<2025`, not duplicate-shadowed. Full provenance in `docs/phase7-candidate-screening/README.md`.
- **Quality estimator:** `adj_mean` = severity-adjusted mean `AVG(rating − delta_u)` from `data/processed/phase2-active/game_adjusted_means_active.parquet` (`mu 7.144`, `sigma_e 1.194`, `sd_adj 0.872`, 16,564 games with ratings; see `docs/phase2-active/phase5_quality_comparison.json`). All adj values use this estimator, not `bayes_rating` (overshrinks) or raw mean (confounds rater-pool severity).
- **Uncertainty:** `SE = 1.194 / sqrt(n_obs)` (frequentist), `post_SD = 1/sqrt(1/0.746 + n/1.426)` (EB, `sigma_alpha² 0.746`, `lambda 1.91`). `lower_1_96 = adj − 1.96·SE` (95% lower bound), `lower_1 = adj − 1·SE`. At `n=200` `SE 0.084` → `1.96·SE 0.165`; at `n=474` (robust median) `SE 0.055` → `1.96·SE 0.108`; at `n=100` `SE 0.119` → `1.96·SE 0.234`. Robust gate already restricts to `n≥200`, so lower offsets are small (median 0.108).
- **Residual:** `resid = underratedness_pref = adj − expected` (`Q3b/OLS`, `X = 8 volume-band dummies + spline year + weight + log playtime + min/max players + reimplementation + 28 categories`, 46 features). Distribution among 910 robust: mean 0.86, median 0.79, P10 0.62, P90 1.33, max 2.27. Robust adj vs resid correlation `r=+0.32` (modest; higher adj tends to have larger resid but they are not interchangeable — `r² 0.10`).
- **Active quality distribution (empirical anchor, 16,564 games):**

| Quantile | adj threshold | Share ≥ threshold | Distance from mu 7.144 | SD units (sd 0.872) |
|---|---|---|---|---|
| P10 | 5.80 | 90% | −1.34 | −1.54 |
| P25 | 6.39 | 75% | −0.75 | −0.86 |
| P50 | 6.96 | 51.9% | −0.18 | −0.21 |
| **P75** | **7.515** | **25.7%** | **+0.37** | **+0.43** |
| P90 | 8.01 | 10.2% | +0.86 | +0.99 |
| P95 | 8.28 | 5% | +1.13 | +1.30 |

Active lower-bound quantiles (for context): `adj −1.96·SE` median `6.82` (P50), `7.38` (P75), `7.87` (P90); `adj −1·SE` median `6.89`.

---

## 1. Absolute adjusted-quality thresholds

Single cut on `adj_mean`. Empirical basis column anchors each threshold to active distribution and distance from `mu`.

| Gate | Empirical basis | N retained / 910 | Retained % | Excluded | adj median (retained / excluded) | resid median (retained / excluded) | lower_1_96 median (ret) | n median (ret / exc) | Overlap note |
|---|---|---|---|---|---|---|---|---|---|
| `adj ≥ 7.0` | P52, `mu −0.14` (−0.17 SD), 48.1% of active ≥7.0 — barely above median | 786 | 86.4% | 124 | 7.77 / 6.80 | 0.81 / 0.70 | 7.69 | 502 / 412 | Most lenient “good” — essentially median floor; retains games still below population median quality |
| `adj ≥ 7.3` | P66, `mu +0.16` (+0.18 SD), 34.1% of active ≥7.3 — modest above-average | 654 | 71.9% | 256 | 7.91 / 7.01 | 0.83 / 0.72 | 7.80 | 512 / 434 | Modest filter; still below top quartile |
| **`adj ≥ 7.5`** | **P74 (≈P75=7.515), `mu +0.36` (+0.41 SD), 25.7% of active ≥7.5 — top quartile** | **544** | **59.8%** | **366** | **8.00 / 7.14** | **0.84 / 0.73** | **7.90** | **536 / 417** | **Defensible “good” floor — top quartile of active quality** |
| `adj ≥ 7.6` | P77, `mu +0.46` (+0.52 SD), ~23% of active ≥7.6 | 492 | 54.1% | 418 | 8.06 / 7.20 | 0.85 / 0.73 | 7.94 | 524 / 440 | Slightly stricter than 7.5; moves 52 games (544→492) |
| `adj ≥ 7.8` | P85, `mu +0.66` (+0.75 SD), 15.2% of active ≥7.8 — top 15% | 382 | 42.0% | 528 | 8.19 / 7.32 | 0.88 / 0.75 | 8.08 | 488 / 468 | Clearly “good”; discards 58% of robust |
| `adj ≥ 8.0` | P90, `mu +0.86` (+0.98 SD), 10.2% of active ≥8.0 — top decile | 274 | 30.1% | 636 | 8.33 / 7.42 | 0.88 / 0.76 | 8.22 | 494 / 468 | Very good — stringent; retains only top-decile quality |

**Distribution detail (retained vs excluded) for primary candidate `adj ≥ 7.5`:**

- Retained (544): `adj` mean 8.05 median 8.00 P10 7.56 P90 8.59; `resid` mean 0.92 median 0.84 P10 0.63 P90 1.31; `n` mean 1018 median 536 P10 234 P90 2283; `SE` median 0.052 P90 0.078.
- Excluded (366): `adj` mean 7.14 median 7.14 P10 6.69 P90 7.42; `resid` mean 0.79 median 0.73 P10 0.61 P90 1.01; `n` mean 758 median 417 P10 235 P90 1708.
- Excluded examples (lowest adj robust): `6584 Grave Robbers II adj 6.19 resid 0.84 n314 SE0.067 lb6.06; 2256 The Magnificent Race adj6.38 resid0.76 n292; 4934 Battling Tops adj6.42 resid0.67 n388` — robustly underrated (`z 8–13`) yet below-median absolute quality. These are the “underrated but mediocre” cases the gate is meant to screen.

**Sensitivity across plausible adj thresholds (N retained):**

| adj threshold | 6.8 | 7.0 | 7.2 | 7.3 | 7.5 | 7.6 | 7.8 | 8.0 |
|---|---|---|---|---|---|---|---|---|
| N retained | 849 | 786 | 701 | 654 | 544 | 492 | 382 | 274 |
| Retention | 93.3% | 86.4% | 77.0% | 71.9% | 59.8% | 54.1% | 42.0% | 30.1% |
| Δ N per 0.1 adj | — | −63 (6.8→7.0, 31 per 0.1) | −85 (7.0→7.2, 42 per 0.1) | −47 (7.2→7.3, 47 per 0.1) | −110 (7.3→7.5, 55 per 0.1) | −52 (7.5→7.6, 52 per 0.1) | −110 (7.6→7.8, 55 per 0.1) | −108 (7.8→8.0, 54 per 0.1) |

Each 0.1 adj above 7.0 removes ~45–55 games. Choice between 7.3/7.5/7.8 is the material decision (654 vs 544 vs 382).

---

## 2. Adjusted-quality percentile thresholds

Percentile gates are the same adj cuts restated at active quantiles. Included to show mapping explicitly (no additional filtering beyond §1).

| Gate | Equivalent adj | N retained | Retained % | Empirical basis |
|---|---|---|---|---|
| `adj ≥ P50 (6.959)` | 6.959 | 799 | 87.8% | Active median — 48.1% of active ≥7.0 is similar; very lenient |
| `adj ≥ P75 (7.515)` | 7.515 | 534 | 58.7% | **Top quartile — 10 games stricter than 7.5 (534 vs 544); essentially identical gate** |
| `adj ≥ P90 (8.009)` | 8.009 | 265 | 29.1% | Top decile — 9 games stricter than 8.0 (265 vs 274); stringent |

P75 vs 7.5 differ by 0.015 adj — negligible. Either form is defensible; `adj ≥ P75` has the cleaner percentile anchor, `adj ≥ 7.5` the rounder number.

---

## 3. Lower-confidence-bound thresholds

Gates on `lower = adj − k·SE` (frequentist `k=1, 1.96`) and `adj − 1.96·post_SD`. These bake uncertainty so a borderline `adj 7.10` at `n=220 SE 0.081 lb1.96 6.94` fails while same `adj` at `n=4000 SE 0.019 lb1.96 7.06` passes. Relevant comparison is `adj` vs `lower` at same nominal level.

| Gate | N retained | Retained % | Adj median (retained / excluded) | Resid median (ret / exc) | Lower median (ret) | n median (ret / exc) | Empirical basis | Comparison to adj gate |
|---|---|---|---|---|---|---|---|---|
| `lower_1_96 ≥ 6.8` | 813 | 89.3% | 7.75 / 6.75 | 0.81 / 0.69 | 7.65 | 501 / 352 | Lenient: requires `adj ≥ 6.94` at median n (6.88 at P90 n) — barely above median | More lenient than `adj≥7.0` (813 vs 786; lower keeps 27 more games with `6.8≤adj<7.0` but high n) |
| `lower_1_96 ≥ 7.0` | 740 | 81.3% | 7.83 / 6.87 | 0.82 / 0.71 | 7.73 | 520 / 362 | Uncertainty-aware median+ : requires `adj ≥ 7.14` at median n (7.08 at high n, 7.16 at low n) — `mu` minus `1×` median SE | Stricter than `adj≥7.0` by 46 games (740 vs 786); those 46 have `7.0≤adj<7.14` and low-median n where SE pushes lb below 7.0 |
| `lower_1_96 ≥ 7.2` | 654 | 71.9% | 7.91 / 7.01 | 0.83 / 0.72 | 7.80 | 534 / 379 | Stricter: requires `adj ≥ 7.34` at median n — between `adj≥7.3` and `adj≥7.5` | Numerically identical N to `adj≥7.3` (both 654) but not same set: 10 games differ each way (adj=7.30–7.33 high-n pass lower but fail adj; adj≥7.30 low-n fail lower) |
| `lower_1 ≥ 7.0` (`k=1`) | 760 | 83.5% | 7.81 / 6.84 | 0.82 / 0.70 | 7.72 | 513 / 358 | `k=1` (~68% one-sided) requires `adj ≥ 7.07` at median n — between `lower1.96≥6.8` and `lower1.96≥7.0` | 20 more than `lower1.96≥7.0` (760 vs 740); captures borderline `adj 7.05–7.13` at moderate n |
| `lower_1 ≥ 7.2` | 679 | 74.6% | 7.89 / 6.97 | 0.83 / 0.72 | 7.78 | 521 / 379 | Requires `adj ≥ 7.27` at median n | Between `adj≥7.2` (701) and `adj≥7.3` (654) |
| `lower_post1_96 ≥ 7.0` | 740 | 81.3% | same as `lower1.96≥7.0` | — | — | — | Posterior `post_SD` differs from `SE` by <0.002 at `n≥200` (median `SE 0.055` vs `post 0.055`) — no material difference at this n floor | Identical N to `lower1.96≥7.0` (740=740) — EB shrinkage irrelevant at robust n |

**Sensitivity across lower thresholds:**

| lower_1_96 threshold | 6.8 | 7.0 | 7.2 | 7.3 | 7.5 |
|---|---|---|---|---|---|
| N retained | 813 | 740 | 654 | 596 | 496 |
| lower_1 threshold | 6.8 | 7.0 | 7.2 | 7.3 | 7.5 |
| N retained | 831 | 760 | 679 | 625 | 519 |

Lower gates move ~60–80 per 0.2 threshold, similar to adj sensitivity but with SE baked in.

**Illustrative borderline examples (adj 6.90–7.60, how lower separates):**

| adj | n | SE | lb1.96 | Pass adj≥7.0? | Pass lb1.96≥7.0? | Title |
|---|---|---|---|---|---|---|
| 7.02 | 217 | 0.081 | 6.86 | yes (borderline) | **no** — SE pushes below 7.0 | NFL Strategy |
| 7.02 | 2144 | 0.026 | 6.97 | yes | **no** but closer | Excape |
| 7.05 | 831 | 0.041 | 6.97 | yes | **no** | Bring Your Own Book |
| 7.14 | 777 | 0.043 | 7.06 | yes | **yes** (just passes) | Dance of Ibexes |
| 7.30 | 221 | 0.080 | 7.14 | yes | yes | Ultimate Werewolf |
| 7.31 | 214 | 0.082 | 7.15 | yes | yes | similar low-n passes only if adj well above 7.0 |

At `n≥200`, the adj-vs-lower gap is `0.05–0.17` (median 0.11). The lower gate’s bite is concentrated in `7.0 ≤ adj < 7.15` with below-median n.

---

## 4. Reasonable combinations

Conjunctions of an absolute floor and an uncertainty floor.

| Gate | N retained | Retained % | Adj median | Resid median | lb median | N median | Empirical basis | vs single adj |
|---|---|---|---|---|---|---|---|---|
| `adj ≥ 7.5 AND lower1.96 ≥ 7.0` | 544 | 59.8% | 8.00 | 0.84 | 7.90 | 536 | Top quartile + confident not below median-like 7.0 | **Identical to `adj≥7.5` alone (544=544) — lower is redundant at this adj with n≥200** |
| `adj ≥ 7.3 AND lower1.96 ≥ 7.0` | 654 | 71.9% | 7.91 | 0.83 | 7.80 | 512 | Modest above-average + uncertainty guard | Identical to `adj≥7.3` alone (654=654) — lower adds nothing at ≥7.3 |
| `adj ≥ P75 AND lower1.96 ≥ 7.0` | 534 | 58.7% | 8.01 | 0.84 | 7.91 | 534 | Top quartile (exact P75) + uncertainty guard | Identical to `adj≥P75` alone (534=534) |
| `adj ≥ 7.5 AND lower1 ≥ 7.0` | 544 | 59.8% | 8.00 | 0.84 | 7.90 | 536 | Same as 7.5+1.96 at this floor | Identical to adj≥7.5 |

**Key overlap finding (empirical, not assumption):** For every adj threshold `≥7.3`, the conjunction with `lower1.96≥7.0` retains exactly the same set as the adj threshold alone (e.g. `adj≥7.5 ∩ lower≥7.0 = adj≥7.5`; `adj≥7.3 ∩ lower≥7.0 = adj≥7.3`). The only conjunctions where lower matters are lenient floors:

| Pair | adj alone | lower alone | Intersection | adj \ lower | lower \ adj |
|---|---|---|---|---|---|
| `adj≥7.0 ∩ lower1.96≥7.0` | 786 | 740 | **740** | **46** (adj 7.0–7.13 low-n) | 0 |
| `adj≥7.0 ∩ lower1≥7.0` | 786 | 760 | 760 | 26 | 0 |
| `adj≥7.3 ∩ lower1.96≥7.2` | 654 | 654 | 644 | 10 | 10 |
| `adj≥7.5 ∩ lower1.96≥7.2` | 544 | 654 | 544 | 0 | 110 |

Thus: **at the recommended `adj≥7.5` level, adding a `lower≥7.0` uncertainty condition is logically redundant given `n≥200`** (all `adj≥7.5` have `lb1.96 ≥ 7.5−0.165 = 7.335` at worst-case `n=200`, well above 7.0). Its value is as a guard for lenient floors (`adj≥7.0`) where it screens 46 borderline low-n games (e.g. `adj 7.02 n217`).

---

## 5. Retained vs excluded — full comparison for each gate

Columns show retained / excluded medians; `Δ = retained − excluded`.

| Gate | Δ adj | Δ resid | Δ n | Interpretation of excluded set |
|---|---|---|---|---|
| `adj≥7.0` | +0.97 | +0.11 | +90 | Excluded: below-median quality (median 6.80, max 6.99), mean resid 0.70 — underrated but mediocre |
| `adj≥7.3` | +0.90 | +0.11 | +78 | Excluded: at/just below median (median 7.01, 25th 6.88), resid 0.72 |
| `adj≥7.5` | +0.86 | +0.11 | +119 | Excluded: median 7.14 (still below P75), resid 0.73 — includes all `resid>1` at adj<7.5 (max excluded resid 1.49) |
| `adj≥7.8` | +0.87 | +0.13 | +20 | Excluded median 7.32, resid 0.75 — discards many moderately good games |
| `lower1.96≥7.0` | +0.96 | +0.11 | +158 | Excluded median adj 6.87, n median 362 — lower preferentially screens low-n borderline (Δn larger than adj gates) |
| `lower1.96≥7.2` | +0.90 | +0.11 | +155 | Similar to lower≥7.0 but stricter |

In every gate, excluded robust have **lower adj (Δ 0.86–0.97), lower resid (Δ 0.11–0.13), and lower n (Δ 20–158)** than retained. The gate does not preferentially discard high-resid gems — excluded resid median never exceeds 0.76 vs retained 0.81–0.88 — but it does discard games whose high resid comes with below-good absolute quality.

---

## 6. How to choose — empirical basis ranking of thresholds

| Threshold | Anchor clarity | Separation | Stringency | Recommendation |
|---|---|---|---|---|
| **7.0** | P52, mu−0.17SD — “above median” — weakest anchor for “good” | Low | Lenient (86% retained) | Too lenient as hidden-gem floor; keeps many adj 7.0–7.3 games still below top quartile |
| **7.3** | P66, mu+0.18SD — “modest above average” | Modest | Moderate (72% retained) | Possible but not strong separation — still below top quartile |
| **7.5 / P75** | **P74–P75, mu+0.41SD — “top quartile”** — **strongest natural anchor** | **High** | **Moderate-strict (59–60% retained)** | **Recommended primary floor** — top quartile is an interpretable “good” standard; 7.5 is round and within 0.015 of exact P75 (7.515) |
| 7.8 | P85, mu+0.75SD — “top 15%” | High | Strict (42%) | Good but stringent; discards 162 more than 7.5 with only +0.19 median adj gain |
| 8.0 / P90 | P90, mu+0.98SD — “top decile, very good” | Very high | Very strict (29–30%) | Too strict for screening — keeps only 274 of 910 |

**Lower-bound gates:** best paired with lenient adj floors. `lower1.96≥7.0` is the defensible uncertainty companion (requires adj ≥ ~7.14 at median n), analogous to “confidently above median-like 7.0”. At `adj≥7.5` it is redundant; at `adj≥7.0` it screens the 46 borderline low-n `adj 7.0–7.13` cases that pass a lenient floor on point estimate alone. `post_SD` variant adds nothing at `n≥200` (median `SE` vs `post_SD` differ by 0.001–0.003).

---

## 7. What this gate does not do

- **Not a hidden-gem score.** It screens on absolute quality (`adj`), keeping conditional overperformance (`resid`) already established by Phase 7. It does not assess broad appeal (audience breadth, cross-audience consistency) — that remains Phase B (`broad_appeal_evidence.md` taxonomy, four evidence types, no combined score).
- **Not a new population or residual definition.** Phase 7 `910` robust, `Q3b/OLS` residual, `SE=1.194/sqrt(n)`, deduplication, and `n≥100` evidence floor (robust `n≥200`) are unchanged.
- **Tagging:** retained/excluded counts are observed facts; threshold labels (“good”, “top quartile”) are method choices with stated empirical anchors; all resid/adj values are model-dependent (Q3b/OLS); broad-appeal implications are explicitly out of scope.

---

## 8. Files and reproduction

- **Machine-readable:** `quality_gate_candidates.csv` (910 rows, `adj/se/lower/resid` + 20 gate flags per threshold), `quality_gate_summary.json` (per-gate retained N, adj/resid/lower/n distributions, sensitivity grids, empirical basis, provenance).
- **Inputs:** `docs/phase7-candidate-screening/underrated_candidates.csv`, `data/processed/phase2-active/game_adjusted_means_active.parquet`, `docs/phase2-active/phase5_quality_comparison.json` (`mu 7.144`, `sd_adj 0.872`, `sigma_e 1.194`, `sigma_alpha² 0.746`), `scratch/phase2-active/bgg_research_population.parquet`.
- **Computation:** copy-once into `scratch/phase2-active` where applicable; DuckDB `quantile_cont` for active adj/lower quantiles; `SE = sigma_e/sqrt(n)`; per-row lower bounds; gate flags as boolean integers.

*See `README.md` in this folder for methodology narrative and `quality_gate_summary.json:empirical_basis` for per-gate anchor strings.*

# Sensitivity study: `n_active ≥ 100` versus active `≥ 1` (single-filter, not recursive closure)

> **Status:** sensitivity study only — primary results remain `data/processed/phase2-active/` `24.5M obs, mu 7.144, game_adjusted_means_active, phase6_residuals_active` on `16,564` games. This filters **games** on `n_active` (active ratings per game, from `game_adjusted_means_active` / `rating_observations_active` group-by); users remain `≥10` minus `degenerate_strict` (no recursive closure; see `docs/second-pass-methodology-review.md:1` deferred item).

## Summary — which case holds [Model-dependent conclusion]

**Case 3 holds: the answer differs between model estimation and candidate screening.**

- **Estimation is harmlessly stable:** preferred `Q3b/OLS` (band-volume) coefficients, `R²`, and residuals are essentially unchanged when the `1–99` bucket (`1,612` games, `9.7%` of active `GM`, `P10=100` threshold; `1,604` in the `16,549`-game Phase 6 complete-case sample) is excluded.
- **Screening is materially noisy at low `n`:** the strongest positive residuals (top-1% / top-5% and top-20) under `active≥1` are dominated by very high-`SE` `n<100` games, despite model stability on the retained population.

**Implication:** keep the primary pipeline as is (no `n≥100` population redefinition, no rerun); add an `n≥100` **screening floor for Phase 7 candidate lists** (or equivalently an `SE`/`lower-bound` filter), not an estimation filter. This matches the existing Phase 6 preview practice (`reports/phase6_underratedness/top_residuals_preview_nmin100.csv`) and the standard lower-bound display (`adj − 1.96·SE`).

All numbers below are **empirical findings / model-dependent conclusions** per `AGENTS.md`; counts are **observed facts**. Machine-readable details: `reports/sensitivity_n100_games/` (CSV/JSON) and `docs/phase6-intermediate/sensitivity_n100.json`.

---

## 1. Population accounting [Observed fact]

| Layer | `n` | Note |
|---|---:|---|
| `game_adjusted_means_active` (games with ≥1 active rating) | **16,564** | median `293`, `P10 100`, `P90 2,795`, mean `1,480` |
| — `n_active` in `1–99` | **1,612** (`9.73%` of `16,564`) | mean `n` 66.0, mean `SE` 0.216, median `SE` 0.134 |
| — `n_active ≥100` | **14,952** (`90.27%`) | mean `n` 1,632, median `347.5`, mean `SE` 0.064 |
| Rating observations `ro` (active) | **24,509,788** | |
| — restricted to `n≥100` games | **24,403,408** (`99.57%` retained, `106,380` obs removed) | tiny obs share; tail is games, not ratings |
| Phase 6 complete-case estimation sample | **16,549** (active) / **14,945** (`n≥100`) | `15` / `7` dropped for null `weight`/`playtime`; excluded `1,604` low-`n` in est |
| `harmonic mean n` | `106.5` → `280.0` | `mean 1/n` falls `0.00939 → 0.00357` |

Single-filter: games filtered on `n_active` via `SEMI JOIN` on the `≥100` game list; users fixed at `≥10` (no user closure).

---

## 2. Phase 5 quality-estimator sensitivity [Empirical finding]

| Quantity | Active `≥1` | `n≥100` | Delta | % change | Material? |
|---|---:|---:|---:|---:|---|
| `Var(adj)` | `0.7596` | `0.7275` | `−0.0321` | `−4.22%` | modest (low-`n` excess variance) |
| `sigma_e` | `1.19407` | `1.19335` | `−0.00072` | `−0.06%` | no |
| `sigma_alpha (MM)` | `0.8638` | `0.8500` | `−0.0139` | `−1.60%` | no |
| `lambda_MM = sigma_e²/sigma_alpha²` | `1.9107` | `1.9712` | `+0.0605` | `+3.17%` | no |
| `lambda_cov` (even/odd cross-check) | `1.9229` | `1.9735` | `+0.0506` | `+2.63%` | no |
| `SE` median / P10 / P90 | `0.0698 / 0.0226 / 0.1194` | `0.0640 / 0.0212 / 0.1076` | — | — | — |
| `harmonic mean n` | `106.5` | `280.0` | — | — | — |

Held-out even/odd `adj_odd` prediction (primary; `n_games_both_halves` `16,512 → 14,952`):

| Estimand → `adj_odd` | Active RMSE | `n≥100` RMSE | Active R² | `n≥100` R² |
|---|---:|---:|---:|---:|
| `adj_even` | `0.2166` | `0.1539` | `0.9385` | `0.9677` |
| `shrunk_even` (EB `w=n/(n+lambda)`) | `0.2052` | `0.1529` | `0.9448` | `0.9681` |
| `raw_even → adj_odd` | `0.4104` | `0.3711` | `0.7793` | `0.8120` |
| `bayes → adj_odd` | `1.338` | `1.280` | `−1.346` | `−1.236` |

Shrinkage table (`w=n/(n+lambda)`, `mu=7.144`):

| `n` | `w` active (`λ=1.91`) | `w` n≥100 (`λ=1.97`) | shift |
|---:|---:|---:|---:|
| 50 | 0.9632 | 0.9621 | −0.0011 |
| 100 | 0.9813 | 0.9807 | −0.0006 |
| 293 | 0.9935 | 0.9933 | −0.0002 |
| 2,795 | 0.9993 | 0.9993 | −0.0000 |

**Interpretation [Supported conclusion]:** `1–99` games are just a noisy tail: `Var(adj)` falls `4.2%` and held-out RMSE falls by sampling-noise reduction (`0.217 → 0.154`) when they are removed, but `sigma_e`, `sigma_alpha`, and `lambda` move `<4%` — the EB shrinkage itself is essentially unchanged (`<0.2%` at median `n`). No case-2 trigger here (all `<5%`).

---

## 3. Phase 6 expected-quality model sensitivity [Empirical finding; Model-dependent]

All specs use the same designs as `scripts/31` (OLS `w=1`; `5-fold CV` `seed 20260824`; unweighted CV metrics so `w=n` stays comparable). Preferred is `Q3b_flex_volume/OLS` (band-volume + spline year + weight + structure + 28 cat flags; `46` feat; `corr(resid, log n)` should be `≈0` for `Q3b` by band construction).

### 3a. Preferred `Q3b/OLS` — changes are below materiality thresholds

| | Active | `n≥100` | Delta | Threshold (case 2) | Hit? |
|---|---:|---:|---:|---|---:|
| `CV R²` mean | **0.5819** | **0.5958** | **+0.0139** | `>0.02` | no |
| `R²` in-sample | 0.5844 | 0.5989 | +0.0145 | — | — |
| `beta_weight` | **0.461346** | **0.475010** | **+2.96%** | `>10%` | no |
| `corr(resid, log n)` | −0.0042 | +0.0128 | — | — | no (both `≈0`) |
| `max |band mean resid|` | ~`0` (by bands) | ~`0` | — | — |
| Residual `SD` | 0.5620 | 0.5403 | −0.0217 | — | — |

Linear-volume specs for contrast (not preferred): `Q3/OLS beta_logn +25.6%` (`0.352 → 0.442`) and `CV R² +0.028` — this larger shift is **functional-form dependence on the bottom tail** (Part A convex/non-monotonic `n` curve: `1–99` mean `adj 7.169` > `100–199` `6.637`), which `Q3b` absorbs exactly via band dummies. `Q1/OLS beta_logn +24.0%` is similar. For the preferred band-volume spec, the shift is `<3%`.

Residual stability of the preferred spec **on the overlap population** (`14,945` `n≥100` games, i.e. how the 14,945 retained games are ranked under the two fits):

| Stability (overlap only) | Pearson | Spearman | `Jaccard top-1%` (k=149) | `Jaccard top-5%` (k=747) |
|---|---:|---:|---:|---:|
| `Q3b/OLS` resid (`n≥100` games ranked by each fit) | **0.9995** | **0.9992** | **0.974** | **0.948** |

Cross-universe candidate overlap (`full top-1%` vs `n≥100 top-1%` as sets of `game_id` — includes `n<100` games that cannot appear in the `n≥100` set):

| Comparison | `Jaccard top-1%` | `Jaccard top-5%` | Interpretation |
|---|---:|---:|---|
| Full `165` top-1% vs `n100` `149` top-1% | **0.57** | — | `97` shared of `165+149−97=217` |
| Full `827` top-5% vs `n100` `747` top-5% | **0.747** | — | — |
| On-overlap (above) | 0.974 | 0.948 | model is stable where both exist |

**[Empirical finding]** The `CV R² +0.014` gain is below `0.02` and is mechanical: removing the `7.169`-mean `1–99` hump (above `100–199`) flattens the curve and makes linear controls fit better. Band-volume `Q3b` was introduced precisely to neutralise this shape; after bands, the gain shrinks to `+0.014`.

### 3b. Per-spec residual stability on overlap [Empirical finding]

| Spec | Wtg | Pearson | Spearman | `Jaccard top-1%` |
|---|---:|---:|---:|---:|
| Q3b flex | OLS | 0.9995 | 0.9992 | 0.974 |
| Q3 categories | OLS | 0.9928 | 0.9887 | 0.862 |
| Q1 core | OLS | 0.9942 | 0.9911 | 0.851 |
| Q0 flex_year | OLS | 0.9959 | 0.9939 | 0.886 |
| Q3b | WLS_n | 0.9999 | 0.9999 | 0.974 |

WLS variants are included for completeness; they are `≈1.0` because WLS reweights toward high-`n`, which is already the overlap.

---

## 4. Residual distribution [Empirical finding]

| Stat | Active `Q3b/OLS` (`16,549`) | `n≥100` `Q3b/OLS` (`14,945`) | Interpretation |
|---|---:|---:|---|
| Mean | ~`0` | ~`0` | by OLS |
| SD | **0.5620** | **0.5403** | −`3.9%` (low-`n` tail variance) |
| P05 / P95 | −0.922 / +0.856 | −0.896 / +0.825 | −2–3% tighter |
| P01 / P99 | −1.552 / +1.298 | −1.522 / +1.219 | — |
| Max abs | 5.963 | 5.907 | — |
| Max positive | **3.937** (Pondscape, `n=1`, `SE=1.19`) | **2.276** (Monikers: More Monikers, `n=452`) | max dominated by `n=1` noise |
| Median | 0.0219 | 0.0213 | — |

Histogram: identical shape; low-`n` tail fattens extremes and slightly inflates `SD` (0.022 points).

---

## 5. Strongest residuals [Observed fact]

### Top 20 positive — active `≥1` (`Q3b/OLS`) — 11 of 20 are `n<100`

| # | Title | n | SE | adj | expected | resid |
|---:|---|---:|---:|---:|---:|---:|
| 1 | Pondscape | 1 | 1.194 | 11.553 | 7.616 | **3.937** |
| 2 | Thief's Market | 3 | 0.689 | 10.461 | 7.585 | 2.877 |
| 3 | Monikers: More Monikers | 452 | 0.056 | 8.575 | 6.303 | 2.272 |
| 4 | Tolleno | 1 | 1.194 | 9.844 | 7.626 | 2.218 |
| 5 | Small World Designer Edition | 246 | 0.076 | 9.100 | 6.898 | 2.202 |
| … | … | … | … | … | … | … |

### Top 20 positive — `n≥100` (`Q3b/OLS`) — none are `n<100` by construction

Top is Monikers: More Monikers `2.276` (`n=452`, `SE 0.056`), then Small World `2.180` (`n=246`), Shmonikers `2.047` (`n=319`), Something Something `2.018` (`n=246`), Red White & Blue Racin' `1.984` (`n=133`) — the party-game series remains on top in both universes, but the extreme `>2.5` tail vanishes.

### Bottom 20 negative — largely `n≥100` in both universes

Most negative under both: Wonders of The First CCG `−5.96 → −5.91` (`n=186`, stable), ERA `−5.19` (`n=40`, disappears in `n≥100`), TseuQuesT `−4.77` (`n=178`, stable). Low-`n` amplification is asymmetric: only ERA among the top negatives is `n<100`; the very largest negatives are reliably estimated mid-`n` failures.

**[Empirical finding]** Top-1% (`165` games, active) contains `51` low-`n` (`31%`); top-5% (`827`) contains `153` (`18.5%`) — `3.2×` and `1.9×` their population share (`9.7%`). Cross-universe `Jaccard top-1%` is `0.57` (<`0.70` case-2 screening trigger) precisely because the `1–99` candidates are structurally absent from the `n≥100` ranking — not because the model re-ranked the retained games (overlap `Jaccard` `0.97`).

---

## 6. Decision — explicit conclusion among three cases

| Case | Criterion | Observed | Met? |
|---|---:|---|---:|
| **1 (harmless)** | `beta` shift `≤10%` **and** `R²` change `≤0.02` **and** `Jaccard ≥0.70` **and** top not dominated by `n<100` | beta `+3%`, R² `+0.014`, **overlap Jaccard 0.97** but **cross Jaccard 0.57**, **top-20 55% low-`n`** | no (screening fails) |
| **2 (material → rerun)** | `beta >10%` **or** `R² >0.02` **or** `Jaccard <0.70` for `top-1%` **or** top dominated — then `n≥100` floor for estimation | pref fails `R²`/`beta`; `Q3` linear-`log n` would hit (`beta +25.6%`, `R² +0.028`) but pref is banded and immune | no for pref model |
| **3 (split)** | **Model stable, candidate lists noisy at low `n` → `n≥100` screening floor for candidates, not population redefinition** | pref model stable (`beta +3%`, `R² +0.014`, residual corr `>0.999`, `Jaccard_overlap 0.97`) but candidate lists **dominated by `n=1–3` noise** (`SE 0.69–1.19`, `55%` of top-20, `31%` of top-1%, cross `Jaccard 0.57`) | **YES** |

**Conclusion [Model-dependent conclusion / Supported conclusion]: Case 3 — estimation vs screening split.**

- **Do not redefine the research population or rerun Phases 5/6 with `n≥100` for estimation.** The preferred `Q3b/OLS` band-volume specification already neutralises the `1–99` hump; its `beta_weight (+3%)`, `CV R² (+0.014 < 0.02)`, `corr(resid, log n) ≈0`, and residual rank stability (`pearson 0.9995`, `Jaccard 0.97`) show `1–99` games are a noisy tail with large `SE`, not a bias source for the fit.
- **Add an `n≥100` (equivalently `SE ≤ 0.119`) screening floor for Phase 7 candidate lists** — or rank by lower-bound `adj − 1.96·SE` / `expected` lower bound. Without this, candidate screening is high-`SE` lottery: `SE>0.15` for `n<61`, `SE>0.38` for `n<10`, `11/20` of the illustrated top residuals are `n<100` high-`SE` noise (including `n=1,2,3` with `resid >2.1` and `SE 0.69–1.19`).
- **Linear-volume specs (`Q3`, `Q1`, `Q0`) are more sensitive** (`beta_logn +18–26%`) — retain `Q3b` bands as preferred precisely because bands remove the bottom-tail sensitivity `Q3` suffers; for any linear-volume sensitivity analysis, flag the dependence.

### What this does not establish [Limitation]

- Single-filter study only; the deferred recursive closure (`games<100 ∧ users<10` iterated) is not tested here.
- No external broad-appeal validation; residual remains an operational conditional anomaly (`underratedness_g = adj − expected | X`), not latent quality or hidden-gem status.
- `n≥100` is a discovery screen (Phase 7 entry), not a truth claim — lower-`n` games may contain genuine signal with very wide uncertainty; an `SE`-aware display can retain them as "uncertain" rather than hard-excluding.

*Reproduce:* `python scripts/32_sensitivity_n100_games.py` (bounded `4GB/threads3/temp scratch/ducktmp`, copy-once `scratch/phase2-active`, `SEMI JOIN` on `n≥100` game list, single grouped even/odd pass reused; outputs `reports/sensitivity_n100_games/*.csv/*.json` + `docs/phase6-intermediate/sensitivity_n100.{md,json}`).


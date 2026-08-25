# Quality vs Underratedness vs Hiddenness — Why They Are Three Separate Dimensions

**Population:** 14,698 × 287,302 × 24,146,307, mu≈7.139. Phase 2 baseline via `user_severity_pass2.parquet` + `game_adjusted_means_pass2.parquet`.

This note explains why the hidden-gem question needs **three** of the five dimensions treated as distinct before audience-selection even enters, where Phase 5/6 sits, and why `adj_mean` stays as the quality estimator.

---

## 1. The central conflation to avoid

A common shortcut is to collapse "good, underrated, hidden" into one number such as `bayes_rating` or a residual that already includes popularity. That shortcut mixes together **three different estimands**:

| Label | Estimand | What varies | What is held constant |
|---|---|---|---|
| **QUALITY** | `E[ rating − severity \| game ]` — how well the game is liked by those who chose to rate it, after removing rater leniency | Game | Rater severity (`delta_u`) removed; popularity, age, genre, weight are free to vary |
| **UNDERRATEDNESS** | `observed quality − expected quality \| observable characteristics` — residual vs a stated expectation model | Game, conditional on `log10(n_obs)`, year, weight, playtime, categories/mechanics | The expectation is descriptive, not causal |
| **HIDDENNESS** | `how many / who has rated it` — `n_obs`, `users_rated`, `penetration` among enthusiasts | Exposure/awareness/popularity | Quality is not part of the definition |

A game can be:

* **High quality but not hidden** — Catan `adj_mean` 7.12 with 119k ratings, penetration 41% (all) / 65% (heavy Economic): genuinely liked and broadly known.
* **High quality and underrated but not hidden** — a popular game that exceeds even high expectations (not hidden because it is visible).
* **High quality and hidden but not underrated** — a niche game whose rating matches what its characteristics predict (e.g., heavy 18XX games are expected to be high).
* **Underrated but not high quality** — exceeds expectation but still modest absolute level (e.g., `adj_mean` 6.8 where expectation 6.2).
* **High quality, underrated, and hidden** — the conjunction the project seeks.

No single number can carry these three without loss. Keeping them separate lets us say, for one game, "it's good and obscure, but not surprising given its weight/categories" and for another "it's surprisingly good for its obscurity, but we can't tell if that generalizes".

---

## 2. Where Phase 2, Phase 5, Phase 6 sit

**Phase 2 (baseline, pass2 refreshed)** estimated severity and quality:

* Method: `r_ug = mu + alpha_g + delta_u + epsilon`, with `mu` 7.139, `alpha_g` game effect, `delta_u` user severity. No type interaction needed — joint `rater×type` test explained `<1%` variance (R² 0.393→0.403) and no flag met stability/distinctness/materiality.
* Quality is `adj_mean = mean(rating − delta_u)` per game (stored in `game_adjusted_means_pass2.parquet`). Properties on pass2: `corr(adj, raw)=0.983`, `corr(n_obs, shift)=0.015`, severity spread 1.04 (band 10–24 +0.27 vs 1000+ −0.77), parity r 0.877, R² both 0.393, within-game gap +1.10 entirely severity.
* **Tag:** empirical finding — additive severity removes essentially all pooled volume gap (−0.035 remaining).

**Phase 5/6 (underratedness)** built an **expected quality** baseline:

* Method (historical on 16,726, not yet refreshed on pass2 14,698): OLS of `avg_rating` on `log10(users_rated)`, year, weight, playtime, player counts, reimplementation, categories/mechanics (S3 primary, R² 0.539 RMSE 0.552; S4 0.559; S5 band/decade R² 0.519). Residual = underratedness.
* Findings that carry forward as reference (do NOT refit here):
  * Residual SD 0.55, 95th +0.87, 99th +1.32; volume coefficient +0.36 per 10× after controls.
  * Top-1% overlap S3 vs S5/S4 ~54–72% — exact membership sensitive; stable vs sensitive candidates differed on weight/year and Wargame vs Card/Hand Management.
  * No residual, stable or not, identifies broad appeal — RQ3 still separate.
* **Role in screening:** Phase 5/6 provides the expectation against which "better than expected" is measured. It is **not** a quality correction — it does not change `adj_mean`. It conditions on observable characteristics to make "surprisingly good" precise, but the expectation is descriptive (no causal claim) and threshold-dependent.

**Why not fold underratedness into quality:** A game that is genuinely excellent and popular can be high quality without being underrated (expectation already high). A mediocre game in a niche with low expectation can be underrated without being high quality. The project asks for **both** ("genuinely underrated" meaning high `adj_mean` *and* high residual, per Research Question 2), so we keep them separate and later intersect.

---

## 3. Why popularity / rating count is not quality

Game-level data show that popularity and quality are empirically associated but not interchangeable:

* **Observed fact:** Pearson `avg_rating` vs `log10(users_rated)` +0.31 on 16,726, rising from 6.44 (100–199 band) to 7.53 (25k+). This is ~1.1 points, with within-weight slopes +0.24 to +0.38 and asymmetric lower-tail compression (P10 +1.60). SD declines 0.88→0.55, slower than `1/√n` — not pure noise.
* **Model-dependent conclusion:** After OLS on weight/year/categories, volume residual ~+0.36 per 10× remains — composition plus selection, not just noise.
* **No per-game rating variance available** at low `n` in this dump, but median `SE` at 139 ratings is 0.09–0.14 vs cross-game SD 0.88 — noise not dominant.

Consequences:

* A raw high rating with low `n` is not automatically "inflated noise" — the overall pattern shows low-volume band has **lowest** mean and no excess 8.0+ share (4.3% vs 4.2% mid-volume), contradicting "fan-only inflation dominates all low-volume averages" as a universal claim.
* It is also not automatically "true broad quality" — a high rating can be genuine within niche but not generalize.
* **`bayes_rating` is not quality:** Reverse-fit `bayes = (5.49×2500 + n·avg)/(2500+n)` RMSE 0.025. At 100 ratings it is 96% prior (mean 5.54 SD 0.05); at 2500 it is 50% (mean 7.35). It suppresses low-volume extremes and enforces a popularity threshold; it does not identify who is absent.

So we treat `n_obs` and `penetration` as **hiddenness**, not as quality, and we do not infer badness from low `n`.

---

## 4. Why `adj_mean` stays (and `prop_adj` does not replace it)

Six reasons (expanded in `audience_selection_policy.md` §A, summarized here):

1. **Identified only for 33%** — adequate overlap `32.8%`. Global replacement would rely on unidentified reweighting for two-thirds.
2. **Niche non-identification** — 18XX 100% insufficient, Wargame 52.9%. The most selection-threatened games are least identified.
3. **Weight explosion** — median `max_w_true` 1449 (sampled 9.3) 156×, p95 7619, p99 16566. Sampled scale hid failures.
4. **No rank gain** — stabilized vs raw identical rank (corr≈1); `adj` vs `prop_adj` Spearman 0.973 but top-100 Jaccard 0.626 — ranking broadly preserved, niche shifts but not systematically better.
5. **Truncation discards signal** — cap20 recovers ESS 0.33→0.98 but attenuates `|delta|≥0.2` from 20.8% to 0.2% and std 0.19→0.03.
6. **Model not good enough for quality correction** — AUC 0.822 good for sensitivity, but calibration required 87× correction and RF remained overconfident (ECE 0.324). No rater×type interaction warranted quality change earlier.

The severity-adjusted `adj_mean` already removes the one effect that is large, stable, and identified: additive rater severity (gap closed from +1.25 pooled to −0.035). Observable `type` taste was explicitly tested jointly and failed all materiality gates. Replacing `adj_mean` with `prop_adj` would add weighting noise where overlap is weak and change little where it is adequate.

**Tag for this claim:** model-dependent conclusion / empirical finding — strong for pass2, conditional on observable features available.

---

## 5. How the three interact in the ledger

In the final per-game ledger (not built here, but defined here), each game will have:

```
quality_flag      : pass/fail on adj_mean ≥ T_q
underrated_flag   : pass/fail on residual ≥ T_u (and stability S3 vs S5)
hidden_flag       : pass/fail on n_obs ≤ T_h and penetration ≤ T_p
```

Only games with all three `pass` enter audience-selection screening at all — otherwise they are high quality but not underrated/hidden, and need no broad-appeal adjudication.

Example placements (actual numbers, see `known_case_examples.md`):

* **Catan** (119k, adj 7.12, penetration 41%) — QUALITY pass (moderate), HIDDENNESS fail (not obscure) → **bucket 5: high quality + obvious popularity, not hidden** — no selection adjudication needed.
* **18Chesapeake** (1732, adj 8.34, penetration 0.6% all / 60.8% heavy) — QUALITY pass, HIDDENNESS pass, but `insufficient_overlap` → **bucket 4: high quality + insufficient overlap / unknown** — excellent candidate for external validation, not a cult claim.

This separation prevents three failure modes:

* **Treating popularity as quality** (e.g., promoting `bayes_rating` top list as "best").
* **Treating obscurity as underratedness** (e.g., calling every low-`n` high-rating game a hidden gem).
* **Treating niche excellence as broad appeal** without evidence (the core distinction between Research Questions 2 and 3).

---

## 6. What remains open (manual)

* Which `T_q` reflects "genuinely good" — absolute (≥7.5) vs percentile vs type-conditional — is scope, disclosed.
* Which expectation (S3 vs S5) and residual quantile is "underrated" — sensitivity must be shown (history: S3 vs S5 top-1% overlap 54.6%).
* Which hiddenness band (100–999 vs 100–3000) matches the project's "hidden" intent — scope.
* Phase 5/6 on pass2 not yet refit — when it is, residual thresholds may shift slightly; framework stands.

---

## References (pointers, not copies)

* Phase 2 pass2 baseline: `docs/phase2-pass2/baseline_report.md`, `baseline.json`, `README.md` (mu 7.139, R² 0.393, parity 0.877)
* `rater×type taste v2`: `docs/raterxgenre_taste_v2/` (joint `<1%` variance, no flag warranted)
* Phase 5/6 historical: `findings.md` §2026-08-23 RQ2 baseline + residual robustness (R² 0.54, SD 0.55, 95th 0.87)
* Step 7C weight docs: `docs/phase2-pass2/step7c_exposure_propensity_validation/propensity_calibration.md` (marginal 0.00572, shift −5.159, ECE/Brier), `overlap_rules.md`, `weighting_sensitivity.md`

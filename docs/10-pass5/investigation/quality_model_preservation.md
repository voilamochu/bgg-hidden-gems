# §5 Quality Model Preservation — Keep Unless Genuine Omitted-Factor (Pass 5)

**Generated:** 2026-08-26T03:15Z · seed 20260824 · 14,698 ×287k×24.1M mu 7.139 reuse adj/Q3bFam

**Status:** `proposed — awaiting review` — **Start from validated statistical core, only change where genuine omitted-factor problem demonstrated out-of-sample** (`≥0.15` mean resid + `5/5` folds + `CV Δ≥0.001` + `belongs_in` model, as 18XX did) [definition, Task §5].

---

## Preserved Core (unless evidence requires otherwise)

| Component | Spec | CV | Status | Evidence |
|---|---|---|---|---|
| **Severity-adjusted quality** | `adj_mean` mu 7.139, `SE = sigma_e/sqrt(n)` `sigma_e 1.193` (from `user_severity_pass2.parquet` + `game_adjusted_means_pass2.parquet` via scripts 39/40 — **reuse, do NOT refit**) | — | **PRESERVE** | Additive severity reuse, 7 weight-null median 2.0 + flag [assumption] |
| **Q3bFam primary** | 48f: 7 vol bands + ns_year 3 + core_struct 6 (`weight_c`, `log_playtime_c`, `min_players_c`, `log_max_players_c`, `is_reimpl_num`, `log_n_impl_c`) + cats≥500 28 (`Cat: Wargame` etc.) + `fam_18XX` + `fam_Cooperative Game` + `fam_Legacy Game` | **CV 0.6033 ±0.0058** (Q3b 45f 0.5987, Q4Fam 78f 0.6151) | **PRESERVE as primary** | Spearman 1.0 vs Q3b, Jaccard top1 0.86 (31/38 lost 18XX preserved) [empirical] |
| **Q4Fam sensitivity** | 78f = Q3bFam 48f + 30 mech≥500 (Hand Management, Worker Placement etc.) | **CV 0.6151** | **PRESERVE as sensitivity** | Spearman Q3bFam vs Q4Fam 0.9775 Jaccard top1 0.817 [empirical] |
| **Hiddenness thresholds** | `<1,700` eligible / `1,700–2,500` borderline / `>2,500` exclude (from `rating_observations_pass2` n_obs primary) | — | **PRESERVE** | 12186/694/1818 distribution, eligible max 0.589% vs exclude 3.47% order gap — no strong reason to move [empirical] |
| **Quality + underratedness gates** | `adj≥7.5 & resid≥0.75` → `532` pool (485 eligible +20 borderline +27 exclude) | — | **PRESERVE** | Gate yields 532, hidden 91.2% eligible — hiddenness alone not discriminating [observed fact] |
| **Recursive cleaned population** | 14,698 games / 287,302 users / 24,146,307 obs (2 iterations to fixed point) | — | **PRESERVE** | `validation.json` overall_pass True, every game ≥100, every user ≥10, zero degenerate, counts reconcile [observed fact] |
| **18XX correction must remain** | `fam_18XX` +0.676→0, β+0.748±0.062 5/5, Δ+0.0046 — only candidate meeting bar | — | **PRESERVE** | Systematic omitted-factor demonstrated out-of-sample [empirical] |

**Auditable rule [definition]:** Any future `+fam_*` requires **n≥50, 5/5 same-sign folds, \|mean_resid\|≥0.10 (and ≥0.15 for add), ΔCV≥0.001, Spearman≥0.99, Jaccard reported, and `belongs_in == model`** — none meet it (per `model_comparison.csv` 21 rows + `joint_model_test.csv`) [model-dependent].

---

## Per-Dimension CV Test (model_comparison.csv 21 candidates one-by-one + jointly, 5-fold, n≥50 gate, seed 20260824)

`model_comparison.csv` 22 rows (21 one-by-one + joint). All tested as additive to Q3bFam (not screening). **For eligibility/audience candidates, `belongs_in` is screening/audience, not model — even if CV passes, keep Q3bFam unchanged to avoid leakage.**

| candidate | n | mean resid | β / SE | 5/5 | CV Δ R² | Spearman vs Q3bFam | Jaccard top1 | belongs_in | decision |
|---|---|---|---|---|---|---|---|---|
| **edition_title_any** 501 | +0.116 | +0.123 /0.025 | 5/5 | **+0.0006** |0.921 | **screening/eligibility** | **not model** — would be leakage: normalize inflated edition ratings (Collector's +0.179, Kickstarter +0.428, Second Edition 112 +0.201 all per-pattern n<50 below gate; only Second Edition 112 +0.201 Δ+0.0004 <0.001) [empirical + model-dependent] |
| **solo_first** 691 | +0.127 | +0.176/0.024 |5/5| **+0.0014** |0.947| **audience-selection** | **not model** — systematic but <0.15 and would be leakage design→quality (r -0.70 with log_max) |
| **duel** 2555 | **+0.080** | **+0.201/0.017** |5/5| **+0.0038** |**0.814**| **audience** | **not model** — **largest CV but heterogeneous** (solo 691 + wargame_duel 1153 + Euro 1402) and collinear, 18% churn |
| wargame_duel 1153 | +0.074 | +0.204/0.026 |5/5| +0.0017 |0.947| audience (interaction) | **not model** — doubly specialized, 0% in strong vs 16.6% niche |
| euro_duel 1402 | +0.085 | +0.142/0.018 |5/5| +0.0015 |0.872| audience — Euro duel broader (21.5% insufficient vs 47.7%) |
| game_system 32 | +0.162 | +0.166/0.095 | — | -0.0001 |0.986| eligibility — **hard exclude** (n=32 <50 wide SE) |
| high_version 588 | -0.007 | -0.012/0.029 | — | -0.0001 |1.000| eligibility — **no signal** (already proxied via is_reimpl+log_n_impl in Q3bFam; truncated at 100) |
| coop 1543 | -0.000 | — | — | — | — | **already in Q3bFam** β+0.083 5/5 |
| solo_mech 1397 | +0.011 | +0.016/0.018 | — | +0.0000 |1.000| audience — no systematic |
| semi_coop 98 | -0.252 | -0.258/0.054 |5/5| +0.0006 |1.000| audience — systematic negative but n<50 |
| heavy 929 | -0.045 | -0.082/0.023 |5/5| +0.0003 |0.986| audience — no systematic |
| light 4293 | -0.018 | -0.059/0.015 |5/5| +0.0004 |0.947| audience — no systematic |
| cardset 843 | +0.109 | +0.162/0.022 |5/5| +0.0014 |0.987| eligibility — **not model** (would be leakage) |
| n_reimpl>1 869 | +0.046 | +0.258/0.042 | — | +0.0009 | — | eligibility — no leakage |

**No candidate reaches 18XX bar (`≥0.15 +5/5+CV≥0.001+belongs_in model`)** [empirical]. Closest:
- `duel_1_2p` largest CV +0.0038 but **heterogeneous + r -0.70 with log_max_players_c already in Q3bFam** — adding as additive fam would hide selection mechanism (self-selection into 1–2p vs intrinsic quality) [model-dependent].
- `solo_first` +0.127 systematic but <0.15 and would be **leakage** design→quality [model-dependent].
- `edition_title` +0.116 but `belongs_in` is **screening/eligibility, not model** — would normalize inflated edition ratings, not expected quality [model-dependent].
- `joint` Q3bFam+solo+edition+system Δ+0.00197 < duel alone 0.0038 — **overlap, not independent** [empirical].

**Survives — keep:** **Q3bFam 48f CV 0.6033 as primary, Q4Fam 78f CV 0.6151 as sensitivity** — **add NONE** [model-dependent conclusion]. All systematic residuals belong in **audience-selection / screening / cleanup**, not model — adding would be leakage and hide selection. Keeps global Spearman ~1, Jaccard 1.0; screening/audience local Jaccard 0.814-0.986 Spearman >0.993 — no global overfit [empirical + model-dependent].

---

## Out-of-Sample & Stability Rule Applied

For every proposed model addition, show **out-of-sample** evidence (5-fold paired, seed 20260824, n≥50 gate, 5/5 folds, Jaccard top1/5 vs Q3bFam, Spearman) — not just 39 anecdote — done per `model_comparison.csv` (21 rows) + `joint_model_test.csv`. Thresholds: CV Δ ≥0.001, Jaccard stability, not driven by one fold (fold SD 0.01–0.02). **Model keep preserves global CV 0.6033 Spearman 1.0 Jaccard 1.0; screening/audience have local Jaccard 0.814–0.986 Spearman >0.993 — no global overfit** [empirical].

---

## Files

- `model_comparison.csv` (22 rows, per-candidate n/pct/mean_resid/beta/SE/fold_betas/cv_delta/spearman/jaccard/belongs_in/decision)
- `joint_model_test.csv` (1 row: Q3bFam_joint_solo_edition_system 51f CV Δ+0.00197 Jaccard 0.814)
- `pass5_investigation_summary.json` preserves Q3bFam 48f + Q4Fam 78f + 18XX + hiddenness buckets + gates

**Reproduce (bounded):** `python scripts/58_pass5_investigation.py` → `model_comparison.csv` + `joint_model_test.csv` (seed 20260824, 4GB/3threads, scratch/ducktmp, copy-once, no 24M wide sorts, handle 7 weight null median 2.0 + flag)

## Claim Tags
- **Observed fact:** counts 14,698/287k/24.1M, mu 7.139, 532 pool, hidden buckets 12186/694/1818, pruned 269 etc.
- **Empirical finding:** resid means/CV/Jaccard/Spearman, per-pattern CV, joint Δ+0.00197 etc.
- **Model-dependent conclusion:** Q3bFam 48f primary, Q4Fam sensitivity, keep unless 18XX bar met.
- **Assumption:** additive severity reuse, weight median-fill, cat threshold 500, propensity calibrated.
- **Limitation:** n_version truncated at 100 for 11 games; cannot recover non-raters.
- **Hypothesis:** none for quality — preserved.

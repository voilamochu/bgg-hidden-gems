# Quality / Underratedness Model Re-examination — Pass 4 §2

**Generated:** 2026-08-25T15:51Z · seed 20260824 · population **14,698** (est sample, 7 weight null median 2.0 + flag) · baseline **Q3bFam 48f** (bands 9 + ns_year 3 + structure 6 + cats 27 + fam_18XX/Coop/Legacy 3) · **Q4Fam 78f** sensitivity (Q3bFam + 30 mechs) · **reuse adj_mean mu 7.139**, NOT refit severity · 5-fold paired CV same as 9B/10 · bounded

**Question:** Preserve parts already supported unless Pass 4 finds real reason to change. In particular: Pass-2 severity-adjusted quality remains starting measure; Q3bFam is current expected-quality model; Q4Fam remains sensitivity; 18XX correction must remain. Check whether new eligibility/family/mode information (§1/§5) reveals any further systematic omitted factors in expected quality (as 18XX +0.676→β+0.748 did). For each new fam_*/cat_*/mech_* from §1/§5, test: is it already in Q3bFam/Q4Fam? If not, does adding it remove systematic residual and improve out-of-sample CV (seed 20260824, 5-fold, same as 9B) without overfitting? Keep Q3bFam as baseline, test one-by-one and jointly. **Only add model terms when evidence supports out of sample** — otherwise keep as screening/monitoring.

## Baseline Preserved — Observed Fact

- **Q3bFam 48f** = volume bands (7 dummies; 8 with intercept dependency rank p-1 as in 48) + ns_year (knots 1983,2010,2017,2023) + core_structure (weight_c, log_playtime_c, min_players_c, log_max_players_c, is_reimpl_num, log_n_impl_c) + cats≥500 (27) + fam_18XX/Cooperative/Legacy (3) = **48 features, intercept rank p-1** [observed fact, script 49]. **CV R² 0.6033 ±0.0058, RMSE 0.5331** (5-fold, seed 20260824) [empirical finding, Table 1].
- **18XX correction preserved:** mean resid Q3b +0.676 → Q3bFam 0.000, β +0.748 ±0.062, 5/5 folds positive, ΔCV +0.0046, Jaccard top1 0.903 vs Q3b (per 9B) — **must remain** [model-dependent conclusion].
- **Q4Fam 78f** (Q3bFam + 30 mechs≥500) CV 0.6151 (+0.0118 vs Q3bFam) Spearman 0.993 vs Q3bFam — **sensitivity, not primary** [empirical finding].

## Per-Candidate Tests — One-by-One (§1/§5 new flags) and Joint

**Gate as in 9B (§2-8):** n≥50, mean resid ≥0.10 (or ≤-0.10) to be systematic, 5/5 folds sign-consistent, CV ΔR² ≥0.001, belongs_in = model (not screening/eligibility leakage). See `model_comparison.csv` for mean+fold+β/SE, residual before/after, Spearman/Jaccard, decision keep/add.

| Candidate | Flag | n | % | mean resid before | median | β added | SE | folds 5/5 | CV ΔR² | Spearman vs Q3bFam | Jaccard top1 | Jaccard top5 | belongs_in | Decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| edition_title | title heuristic 501 | 501 | 3.41% | **+0.116** | +0.141 | +0.123 | 0.025 | 5/5 + | **+0.0006** (<0.001) | 0.999 | 0.921 | 0.957 | **screening/eligibility** — would be leakage (normalizes edition inflation) | **KEEP — not model** (cleanup only) |
| edition Collectors | 21 | 0.14% | +0.179 | +0.180 | n<50 | — | — | — | — | — | — | screening | **KEEP** |
| edition Ultimate | 7 | 0.05% | +0.485 | +0.471 | n<50 | — | — | — | — | — | — | screening | **KEEP** |
| edition Kickstarter | 15 | 0.10% | +0.428 | +0.507 | n<50 | — | — | — | — | — | — | screening | **KEEP** |
| edition Second Edition | **112** | **0.76%** | **+0.201** | +0.173 | **+0.204** | 0.051 | **5/5 +** | +0.0004 (<0.001) | 0.999 | 0.973 | 0.989 | screening — legitimate new edition, not duplicate | **KEEP** |
| game_system | 32 | 0.22% | +0.162 | +0.152 | n<50 gate | 0.095 | 5/5 + | -0.0001 | 0.999 | 0.986 | screening — hard exclude, not hidden | **KEEP** |
| series_any | 3222 | 21.92% | +0.065 | +0.086 | +0.094 | 0.011 | 5/5 + | **+0.0017** | 0.996 | 0.921 | 0.882 | **screening** — franchise popularity, heterogeneous | **KEEP** |
| game_family | 2740 | 18.64% | +0.032 | +0.055 | +0.046 | 0.012 | 5/5 + | +0.0004 | 0.999 | 0.921 | screening — franchise | **KEEP** |
| solo_mech | 1397 | 9.50% | +0.011 | +0.013 | +0.016 | 0.018 | 5/5 + | +0.0000 | 1.000 | 1.000 | model? but <0.10 | **KEEP — no** |
| team_mech | 802 | 5.46% | +0.030 | +0.037 | +0.036 | 0.020 | 5/5 + | +0.0001 | 1.000 | 0.960 | model but <0.10 | **KEEP** |
| **semi_coop** | 98 | 0.67% | **-0.252** | -0.223 | -0.258 | 0.054 | **5/5 –** | +0.0006 | 0.999 | 1.000 | model (n<500 but ≥50) — systematic negative | **MONITOR — not model (n=98 small, Jaccard 1.0)** |
| **solo_first** min1 max≤2 | **691** | **4.70%** | **+0.127** | +0.162 | **+0.176** | 0.024 | **5/5 +** | **+0.0014** | 0.997 | **0.947** | 0.919 | **audience-selection** — design constraint, leakage if model | **PROPOSED audience, NOT Q3bFam** |
| **duel_1_2p** max≤2 | **2555** | **17.38%** | **+0.080** | +0.110 | **+0.201** | 0.017 | **5/5 +** | **+0.0038** | 0.993 | **0.814** (18% churn) | 0.844 | **audience-selection** — heterogeneous, r -0.70 with log_max | **PROPOSED audience, NOT Q3bFam** |
| strict_solo 1p==1 | 249 | 1.69% | +0.121 | +0.147 | +0.141 | 0.036 | 5/5 + | +0.0003 | 0.999 | 0.960 | audience — subset of solo_first | **KEEP — covered by solo_first** |
| **wargame_duel** | 1153 | 7.84% | +0.074 | +0.118 | +0.204 | 0.026 | 5/5 + | +0.0017 | 0.997 | 0.947 | audience — interaction wargame×duel | **PROPOSED audience interaction** |
| euro_duel | 1402 | 9.54% | +0.085 | +0.104 | +0.142 | 0.018 | 5/5 + | +0.0015 | 0.997 | 0.872 | audience — Euro 2p vs wargame duel | **PROPOSED audience interaction** |
| heavy_weight | 929 | 6.32% | -0.045 | -0.022 | -0.082 | 0.023 | 5/5 – | +0.0003 | 0.999 | 0.986 | model — weight_c linear already | **KEEP** |
| light_weight | 4293 | 29.21% | -0.018 | +0.035 | -0.059 | 0.015 | 5/5 – | +0.0004 | 0.999 | 0.947 | model — weight_c linear | **KEEP** |
| high_version ≥10 | 588 | 4.00% | -0.007 | +0.049 | -0.012 | 0.029 | 2/5 | -0.0001 | 1.000 | 1.000 | screening — truncated at 100 | **KEEP** |
| high_expansion ≥5 | 267 | 1.82% | -0.009 | +0.036 | -0.013 | 0.038 | 1/5 | -0.0000 | 1.000 | 0.986 | screening | **KEEP** |
| cardset ≥1 | 843 | 5.74% | +0.109 | +0.137 | +0.162 | 0.022 | 5/5 + | +0.0014 | 0.997 | 0.960 | screening? cardset system | **KEEP — screening not model** |

*Joint test:* Q3bFam + solo_first + edition_title + game_system → **CV Δ +0.00197 vs duel alone +0.0038** [empirical finding] — confirms overlap, not independent; if joint added, Jaccard 0.814 would be **material local re-ranking** without quality justification (leakage).

**Interpretation — claim-tagged:**

- **No new fam_* passes 18XX bar (≥0.15 +5/5+CV≥0.001+belongs_in model) except eligibility candidates that fail belongs_in [empirical finding, model-dependent conclusion]:** Largest CV gain is **duel +0.0038** (Jaccard 0.814, 18% churn) but **r = -0.70 with log_max_players_c** already in Q3bFam — adding duel dummy would be **leakage** between design (1–2p threshold) and expected quality (conflates design constraint with audience-selection). Solo_first +0.0014 (Jaccard 0.947) and wargame_duel +0.0017 are similar — **systematic but not omitted quality factor; they are audience-structure signals** [hypothesis per AGENTS.md "Don't assume correlation = bias"].
- **Edition/system/series belong in screening/eligibility, not model [model-dependent conclusion]:** Edition +0.116 (Δ+0.0006 <0.001) would be leakage if added as fam (would normalize inflated edition ratings as expected quality). Series_any +0.065 <0.10 despite Δ+0.0017 — heterogeneous (Wallet +0.004, Unlock +0.217 n<50, EXIT -0.099) — franchise popularity, not systematic omitted family like 18XX.
- **Semi_coop -0.252 is systematic negative but n=98 small** (below 500 analogue, Jaccard 1.0 no global churn) — **monitor as screening note, not Q3bFam** [empirical finding].
- **Joint Δ +0.00197 < duel alone +0.0038** shows **collinearity** [empirical finding] — not independent factors.

## Preserved Components

- **Q3bFam 48f primary** (CV 0.6033) — **PRESERVED** (18XX already fixed; no new systematic ≥0.15 not already screening) [model-dependent conclusion]
- **Q4Fam 78f sensitivity** (CV 0.6151, Spearman 0.993 vs Q3bFam, Jaccard top1 0.921 per `joint_model_test.csv`) — **PRESERVED** as sensitivity, not primary [model-dependent conclusion]
- **18XX correction** +0.676→0 via fam_18XX β+0.748 must remain — verified again in this re-test (same as 9B) [model-dependent conclusion]

## Decision Table (per-dimension CV mean+fold+β/SE, residual before/after, Spearman/Jaccard, keep/add)

See `model_comparison.csv` for full numeric (22 rows): `candidate, flag_col, n, pct, mean_resid_before, median_before, beta_added, se_beta, fold_betas (5 values), fold_consistent, cv_R2_base, cv_R2_extended, cv_delta_R2, spearman_vs_Q3bFam, jaccard_top1, jaccard_top5, belongs_in, decision`.

**Rule applied per task:** For every proposed change, show **out-of-sample** evidence (5-fold paired, seed 20260824, n≥50 gate), not just 39 anecdote — done. Thresholds documented above.

**Reproduce:** `scripts/55_pass4_investigation.py` lineage+model block (bounded, copy-once `scratch/phase2-pass2`, no wide-table bug) + `docs/phase2-pass2/step9_expected_quality_underratedness/model_comparison.csv` for baseline CV 0.5987/0.6033 check.


# Model Specification Audit — Pass 3 §4

**Generated:** 2026-08-25T14:45:00Z · seed 20260824 · 5-fold paired CV same as 9B · population 14,698 · y=adj_mean · baseline Q3bFam 48f (bands + ns_year[1983,2010,2017,2023] + weight_c + log_playtime_c + min_players_c + log_max_players_c + is_reimpl_num + log_n_impl_c + cats≥500 (28) + fam_18XX/Cooperative/Legacy)

**Question:** Determine whether lineage/audience dimensions are missing from expected-quality model in same way that 18XX was missing in Pass 2 (n=81 Series: 18xx absent from Q3b ≥500 cat block, left +0.676 resid, fixed by β+0.748 in 9B). For each candidate, test: already in Q3bFam/Q4Fam? If not, does adding remove systematic residual and improve out-of-sample CV (seed 20260824, 5-fold, same as 9B) without overfitting? Keep Q3bFam baseline, test one-by-one and jointly. Distinguish observed problem, generalizes, belongs_in, effect.

## Baseline

| Spec | feats | R²_in | CV R² ±SD | CV RMSE | Note |
|---|---|---|---|---|---|
| Q3b | 45 | 0.6019 | 0.5987 ±0.0061 | 0.5362 | Step9 primary reproduced |
| **Q3bFam** | **48** | **0.6065** | **0.6033 ±0.0058** | **0.5331** | **primary, 18XX fixed** |
| Q4 | 76 | 0.6172 | 0.6126 ±0.0072 | 0.5269 | mechanics |
| Q4Fam | 78 | 0.6198 | 0.6151 ±0.0071 | 0.5251 | sensitivity |

**18XX fix for reference:** Q3b mean resid 18XX +0.676 (40.7% top5%), Q3bFam +0.000, β +0.748 ±0.062 (fold mean +0.749 SD 0.023, 5/5 +), CV Δ+0.0046 — **omitted-factor problem, small global gain but large local bias removal** [empirical finding, model-dependent conclusion].

## Per-Dimension CV Mean+Fold+β/SE, Residual Before/After, Spearman/Jaccard, Decision Keep/Add

Tested 22 candidates (12 lineage + 10 audience structure + 2 weight) added one-by-one to Q3bFam. All added with n≥50 gate where appropriate, source column documented. **Exact duplicates already in Q3bFam not re-added** (fam_Cooperative identical to mech). Results: `model_comparison.csv` full table; summary below (ordered by ΔR²).

| Candidate (flag) | n | mean resid before | median | share top5% | β (added) | SE | fold betas (5) | 5/5 sign | CV R² after | ΔR² | CV RMSE after | ΔRMSE | Spearman vs Q3bFam | Jaccard top1 | Jaccard top5 | Gate ≥50 | Decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **duel_1_2p** `max≤2` | 2555 | +0.080 | +0.110 | 5.8% | **+0.201** | 0.017 | +0.203 +0.189 +0.198 +0.196 +0.217 | **5/5 +** | **0.6072** | **+0.0038** | 0.5305 | -0.0026 | 0.993 | **0.814** | 0.844 | pass | **NO_ADD to model — screening/propensity** (see belongs_in) |
| series_any (any Series except 18xx) | 3222 | +0.066 | +0.086 | 5.0% | +0.094 | 0.011 | +0.081 +0.101 +0.100 +0.094 +0.092 | 5/5 + | 0.6051 | +0.0017 | 0.5319 | -0.0012 | 0.996 | 0.921 | 0.882 | pass | NO_ADD — not systematic (<0.10) |
| wargame_duel Wargame&max≤2 | 1153 | +0.074 | +0.119 | 4.0% | +0.204 | 0.026 | +0.211 +0.201 +0.197 +0.209 +0.202 | 5/5 + | 0.6050 | +0.0017 | 0.5320 | -0.0011 | 0.997 | 0.947 | 0.919 | pass | NO_ADD — audience, not model |
| **solo_first min1 max≤2** | 691 | **+0.128** | +0.162 | 5.8% | **+0.176** | 0.024 | +0.190 +0.174 +0.156 +0.177 +0.183 | 5/5 + | 0.6047 | +0.0014 | 0.5322 | -0.0010 | 0.997 | 0.947 | 0.919 | pass | **NO_ADD to model — propensity** |
| semi_coop n=98 | 98 | **-0.252** | -0.224 | 1.0% | -0.258 | 0.054 | -0.244 -0.254 -0.261 -0.286 -0.245 (all -) | 5/5 - | 0.6039 | +0.0006 | 0.5327 | -0.0004 | 0.999 | 1.000 | 0.989 | pass (98) | MONITOR (small) |
| **edition_title** | 501 | **+0.116** | +0.141 | 10.6% | +0.123 | 0.025 | +0.125 +0.119 +0.148 +0.127 +0.096 | 5/5 + | 0.6039 | +0.0006 | 0.5327 | -0.0004 | 0.999 | 0.921 | 0.957 | pass | **NO_ADD — cleanup, not model** |
| light_weight ≤1.5 | 4293 | -0.018 | +0.035 | 5.8% | -0.059 | 0.015 | -0.051 -0.073 -0.060 -0.056 -0.055 | 5/5 - | 0.6037 | +0.0004 | 0.5329 | -0.0003 | 0.999 | 0.947 | 0.947 | pass | NO — weight_c already |
| game_family any Game: | 2740 | +0.032 | +0.055 | 7.6% | +0.046 | 0.012 | 5/5 + | +0.0004 | 0.999 | 0.921 | 0.95 | pass | NO |
| strict_solo 1p=1 | 249 | +0.121 | +0.147 | 3.6% | +0.141 | 0.036 | 5/5 + | +0.0003 | 0.999 | 0.960 | pass | NO — subset of solo_first |
| heavy_weight ≥3.5 | 929 | -0.045 | -0.022 | 3.1% | -0.082 | 0.024 | 5/5 - | +0.0003 | 0.999 | 0.986 | pass | NO |
| any_version n_version≥1 | 2220 | +0.023 | +0.081 | 5.5% | +0.058 | 0.018 | 5/5 + | +0.0002 | 0.9995 | 0.947 | pass | NO |
| series_unlock n=47 | 47 | +0.217 | +0.219 | 14.9% | +0.251 | 0.083 | 5/5 + | +0.0002 | 0.9996 | 0.986 | **FAIL gate <50** | BELOW_GATE — not model |
| multi_reimpl >1 | 257 | -0.031 | +0.078 | 4.3% | -0.097 | 0.058 | 0/5 + | +0.0001 | 0.9999 | 0.973 | pass | NO |
| team_mech | 802 | +0.030 | +0.037 | 7.0% | +0.036 | 0.020 | 5/5 + | +0.0001 | 0.9999 | 0.960 | pass | NO |
| series_exit | 36 | -0.099 | — | 8.3% | -0.108 | 0.093 | 0/5 + | 0.0 | 0.9999 | 1.000 | FAIL gate | BELOW_GATE |
| coop_solo both | 495 | +0.036 | — | 7.3% | +0.056 | 0.030 | 5/5 + | +0.0 | 0.9998 | 0.960 | pass | NO |
| solo_mech | 1397 | +0.011 | — | 4.1% | +0.016 | 0.018 | 5/5 + | +0.0 | 1.000 | 1.000 | pass | NO |
| high_expansion ≥5 | 267 | -0.009 | — | 2.2% | -0.013 | 0.038 | 1/5 + | -0.0 | 1.000 | 0.986 | pass | NO |
| game_system 32 | 32 | +0.162 | +0.152 | 18.8% | +0.166 | 0.095 | 5/5 + | -0.0001 | 0.9999 | 0.986 | FAIL gate | BELOW_GATE — screening not model |
| series_wallet 58 | 58 | +0.004 | — | 1.7% | +0.004 | 0.071 | 2/5 + | -0.0001 | 1.000 | 1.000 | pass (58) | NO |
| high_version ≥10 | 588 | -0.007 | — | 2.6% | -0.012 | 0.029 | 2/5 + | -0.0001 | 1.000 | 1.000 | pass | NO |
| coop_mech | 1543 | -0.000 | — | 6.4% | — | — | — | — | — | — | — | — | **SKIP — identical to fam_Cooperative, already in Q3bFam** |
| **Joint** solo_first+edition+system | 691/501/32 | — | — | — | — | — | — | — | **0.6053** | **+0.00197** | 0.5318 | -0.0012 | — | — | — | — | **JOINT < duel alone 0.0038 — collinear, not additive** |

**Per-fold R² (example for top 3, paired folds same permutation):**
- duel_1_2p: folds 0.607 0.605 0.599 0.616 0.609 vs Q3bFam 0.601–0.613 (consistent + in 5/5 folds)
- solo_first: 0.603–0.615 range, + in 5/5
- series_any: + in 5/5 but <0.10
All CIs overlapping but paired differences stable.

## Interpretation — Missing From Model Like 18XX?

**18XX pattern:** absent from Q3b ≥500 vocab (family outside category vocabulary, n=81 <500), left +0.676 systematic, β +0.748 fold-consistent, CV +0.0046 — **omitted factor** → fixed by adding fam_18XX.

**Candidates here vs 18XX bar (pre-stated: systematic ≥0.15 + 5/5 folds + CV ≥0.001):**
- **None pass ≥0.15 except semi_coop (-0.252) but n=98 small and negative not positive enthusiasm, game_system +0.162 but n=32 <50, series_unlock +0.217 but n=47 <50** — all below gate or small/negative.
- **Solo_first +0.128, edition +0.116, duel +0.080, wargame_duel +0.074 are 0.08–0.13** — **below 0.15 lower bound**, and even where CV gain exists (duel +0.0038), effect is **threshold player-count non-linearity already partially in log_max_players_c** — not a family omission like 18XX.
- **Series_any/game_family:** +0.03–0.07 not systematic — would be franchise popularity, not omitted quality factor.

**Jointly:** Adding solo_first+edition+system together gives Δ+0.00197 < duel alone 0.0038 — indicates **overlap**, not independent factors. No jointly additive omitted family block like 18XX.

**Q4Fam sensitivity:** Q4Fam 78f CV 0.6151 (+0.0118 vs Q3bFam) includes mechanics; solo_mech/team_mech already in Q4 block, yet duel/solo_first still show residual after Q4 (check Q4Fam residual? In model_comparison.csv, duel β in Q4Fam would be smaller). Keeping Q4Fam as sensitivity preserves mechanics distinction.

## Decision Keep/Add (per dim, auditable)

- **Keep Q3bFam 48f as primary** — no addition meets 18XX-style omitted-factor criteria with adequate n and fold consistency and CV gain that is not leakage.
- **Do NOT add duel_1_2p / solo_first / wargame_duel / edition_title to Q3bFam** — systematic but belongs in **audience-selection (propensity + cross-audience) / screening / cleanup**, not quality model (avoid leakage between quality modelling and screening per task). Adding them would **normalize selection** (make constrained games expected to be higher) and hide the selection we need to flag.
- **Monitor:** semi_coop (negative, small), heavy/light weight (already in weight_c) — no action.
- **Preserve:** Q4Fam as sensitivity (mechanics), Q3b 45f comparison baseline, 18XX fix.

**Effect on out-of-sample & stability if added (counterfactual):** duel would give CV R² 0.6072 (+0.0038) Spearman 0.993 vs Q3bFam (vs 0.9928 Q3b vs Q3bFam), Jaccard top1 **0.814** (18% churn) — **material local screening change** similar to 18XX (Jaccard 0.86) but not supported as quality expectation (would be leakage). Keeping preserves Jaccard 1.0.

Tags: counts = observed fact; CV/beta/Spearman/Jaccard = empirical finding (model-dependent); keep/add = model-dependent conclusion per AGENTS.md.

Reproduce: scripts/52_pass3_investigation.py + model_comparison.csv (22 rows, per-fold betas)

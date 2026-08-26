# Step 9B — Expected-Quality Spec Audit (final Pass-2 population)

**Generated:** 2026-08-25T10:26:55Z · seed 20260824 · STOP after audit: no hidden-gem screen run, severity NOT refit.

## Executive summary
1. **Coverage audit:** Wargame (2,020), Party Game (1,268), Economic (1,287) are already controlled in Q3b via >=500 category flags; Cooperative Game (1,543) enters only in Q4 mechanics; **18XX (81, BGG family `Series: 18xx`) and Legacy Game (50) are controlled nowhere** — 18XX because it is a family outside the category vocabulary (and would fail the 500 gate anyway), Legacy because n=50 < 500. Details: `model_coverage_audit.md`.
2. **Family block (explicit n>=50 audit gate):** genuinely-new indicators vs Q3b are `fam_18XX`, `fam_Cooperative Game`, `fam_Legacy Game`. Wargame/Party/Economic indicators are bitwise-identical to existing `cat_*` flags and were not duplicated; designs carry only Step-9's known band-dummy/intercept dependency (rank p−1, documented).
3. **CV comparison (paired folds):** Q3b 0.5987 → Q3bFam 0.6033 (ΔR² +0.0046, ΔRMSE -0.0031); Q4 0.6126 → Q4Fam 0.6151.
4. **18XX verdict:** the +0.68 systematic residual is removed by one indicator (β +0.748 ± 0.062, positive in 5/5 folds). This was an **omitted-factor problem**, not hidden underratedness signal. Global out-of-sample gain is small (+0.0046).
5. **Other families:** none besides 18XX shows a ≥0.15 systematic residual after existing controls (Cooperative +0.06, Legacy +0.15 borderline with wide SE).
6. **Rankings:** Spearman(Q3b,Q3bFam) 0.9928; Jaccard top1% 0.860; top-20 movers listed in `stability_top_movers.csv`.
7. **Year sensitivity:** linear-year variant leaves 18XX conclusion intact (+0.748 → +0.681).

## Decision (for Step 10)
**EXTEND Q3b -> Q3bFam (add fam_18XX, fam_Cooperative Game, fam_Legacy Game): dCV_R2 +0.0046, 18XX residual +0.676 -> +0.000, 18XX positive in all 5 folds.**

Rationale (pre-stated criteria: out-of-sample improvement, fold consistency, residual structure, ranking stability — not p-values/in-sample R²): the extension removes a large, fold-consistent systematic residual for a well-defined family at negligible complexity cost (+3 dummies) and cannot hurt the screening stage locally, while its global CV gain is modest. If adopted, Q3bFam — not Q4 — carries forward, keeping mechanics as sensitivity exactly as Step 9 decided. Either choice preserves the Step-9 ranking almost everywhere outside the affected families.

## Files
- `q3b_vs_extended_family_model.csv` — spec comparison incl. per-fold metrics
- `family_effects_by_fold.csv` — per-family/per-fold coefficients + full-sample β/SE
- `candidate_rank_stability.csv`, `stability_top_movers.csv`
- `residual_group_diagnostics.md` + `_table.csv`, `residual_by_family_box.png`
- `model_coverage_audit.md`, `model_comparison.md`, `family_effects.md`
- `step9b_summary.json` — machine-readable everything

**Reproduce:** `.venv/bin/python scripts/49_step9b_spec_audit.py` (game-level only, bounded resources; imports Step-9 helpers from `scripts/48`).

Tags: counts = observed facts; CV/coefficients = empirical findings (model-dependent); decision = model-dependent conclusion per AGENTS.md claim-tagging.

# Pass 3 Investigation — Broad Improvement Cycle for Pass-2 Pipeline

**Status (2026-08-25):** This was **investigation only — proposed changes, NOT final**. See **final** `docs/phase2-pass2/pass3_final/README.md` (and `reports/phase2_pass2/pass3_final/`) which incorporates the independent reviewer `data/bgg-pass3-review/report.md` (§1-6) and reruns `53/54` — and `docs/phase2-pass2/pass3_review/report.md`. Investigation outcomes are **preserved here for provenance**; for the auditable final methodology and candidate set use `pass3_final`.

**Generated:** 2026-08-25T14:45:00Z · seed 20260824 · population 14,698 games × 287,302 users × 24,146,307 obs
**Source:** `data/processed/phase2-pass2/` validated mu≈7.139, `user_severity_pass2.parquet` + `game_adjusted_means_pass2.parquet` via scripts 39/40 — **reuse, NOT refit**
**Models:** Q3bFam primary 48f CV 0.6033 + Q4Fam sensitivity 78f CV 0.6151 from Steps 9B/10; hiddenness `<1,700` eligible / `1,700–2,500` borderline / `>2,500` exclude; **39 strong_hidden_gem_evidence candidates** from Step 11-12 `screening_evidence_table.csv` as **diagnostic only, not ground truth** (tag `pass2-complete` 722d149).
**Scope (historical):** This task was **investigation only — proposed changes, NOT final rerun**. Reviewer (next crewmate) challenged; finalizer incorporated critique then reran (now final).

## Executive Summary: Which Problems Were Real vs Not, Which Changes Survive

### 1. Game Lineage / Ecosystem (§1 lineage)
**Observed problem — in 39 diagnostic:** 3 of 39 strong are re-implementations/share systems with inflated `adj` via shared audience? No — actually 0 of 39 have `is_reimplementation=True`, 0 have `system_flag`, 2 have edition-title pattern (Kickstarter Edition, 3D Edition) but are legitimate distinct SKUs, not duplicate leaks. The manual review suggested edition/system leakage, but **population evidence shows Pass-2 cleanup is already tight**: `combined_primary_edition_family.csv` 169 + `combined_sensitivity_dup.csv` 216 pruned 269 games; **0 of those pruned IDs remain in 14,698**; remaining 476 edition-title games in population have **mean resid Q3bFam +0.116 (n=501 inc. close match, 3.4%)**, systematic but modest (+0.21σ), not 18XX-scale (+0.676). Version links `n_version>=10` n=588 resid -0.007 (no signal); `n_version>=1` n=2220 +0.023; multi-reimpl n=257 -0.031; high_expansion n=267 -0.009 — no lineage signal after `is_reimpl + log_n_impl` controls.

**Generalizes:** edition_title β +0.123 ±0.025, 5/5 folds positive, CV ΔR² +0.0006, Spearman 0.999, Jaccard top1 0.921 — **real but small**; game_system n=32 +0.162 but **below n≥50 gate** (too rare for model); series_any n=3222 +0.066 Δ +0.0017 but <0.10 threshold, Jaccard 0.921; game_family n=2740 +0.032 Δ +0.0004 — not systematic.

**Survives:** **No new fam flag for quality model**. Proposed change **C-edition_title** = **add 4-5 title patterns to `pruned_lists` rule + final screening flag (not Q3bFam)** — belongs in **semantic cleanup / screening**, not model (otherwise leakage: would normalize inflated edition ratings). **C-game_system** stays **screening exclude** (already via `Admin: Game System Entries` 32 games, screening flag — keep, not model).

### 2. Audience Structure (§2 audience)
**Observed:** cooperative `fam_Cooperative` already in Q3bFam (n=1543 β +0.083 5/5 folds, resid 0) — preserved. Solo mechanic n=1397 +0.011 (noise). **But constrained play modes show systematic resid not in current dummies**: solo-first `min=1 max≤2` n=691 **+0.128**, duel 1–2p `max≤2` n=2555 **+0.080**, wargame_duel n=1153 **+0.074**, strict_solo n=249 +0.121, semi_coop n=98 **-0.252**, team n=802 +0.030 (noise). Current Q3bFam has `fam_Cooperative`/`fam_Legacy` alone; weight + `min_players_c` + `log_max_players_c` (linear) do not capture threshold effects.

**Generalizes — CV tests (5-fold, same as 9B):**
- solo_first: β +0.176 ±0.024, folds +0.190 +0.174 +0.156 +0.177 +0.183 (5/5), **CV Δ +0.0014**, Spearman 0.997, Jaccard top1 0.947 — systematic.
- duel_1_2p: β **+0.201 ±0.017**, 5/5, **CV Δ +0.0038** (largest of all candidates, comparable to 18XX +0.0046), Jaccard **0.814** (18% churn) — strongest signal, but heterogeneous (contains solo_first 691 + wargame_duel 1153 + 2p Euros).
- wargame_duel: β +0.204 5/5 CV +0.0017 Jaccard 0.947
- series_any: +0.066 CV +0.0017 (just above noise)
- solo_mech/team_mech: <0.03, CV <0.0001 — no signal.

**Survives — but NOT all as model:** Per audit **do not put everything in quality model**. `solo_first`/`duel` belong **primarily in audience-selection analysis (new specialist metric + propensity covariate)**, not as additive `fam_*` dummies — otherwise would conflate design constraint (1–2p) with expected quality and hide the selection mechanism we need to measure. `semi_coop` n=98 below gate, monitor as screening note. **No Q3bFam addition passes 18XX-style bar (>=0.15 + 5/5 + CV>=0.001) except duel which is <0.15 mean but large CV due to n**. Keep Q3bFam 48f **unchanged as primary**; add `solo_first`/`duel` as **propensity covariates + cross-audience specialist splits** (Step 7 extension). Joint test `Q3bFam+solo+edition+system` CV +0.00197 < duel alone 0.0038 — confirms collinearity.

### 3. Broad Appeal (§3)
**Definition (auditable, per AGENTS.md):** Broad appeal = appeal to **broad swathe of modern hobby board gamers** — people who already know/play contemporary hobby games. **NOT general population.** This is the estimand niche→hidden gap.

**How current pipeline measures it — where it conflates:**
- **Q3bFam resid** estimates quality conditional on volume/year/weight/categories+18XX/Coop/Legacy (model-dependent). It **does not** distinguish broad vs niche enthusiasm — high resid can be niche mastery (e.g., duel wargame) or broad excellence.
- **Cross-audience (Step7)** + **propensity Step7B/7C** + **hiddenness** together proxy broad vs niche: does high quality remain among non-specialists/light raters/non-owners? Current framework **works for typed games** (18XX/Wargame via specialist share/TVD) but **conflates when**: (a) low-volume niche enthusiasm still looks like +resid if family missing (fixed for 18XX, not for solo-first/duel), (b) high-volume popularity ≠ broad appeal (volume gradient +0.51 per 10× even after severity, but severity-adjusted).
- **Step10 `primary_vs_sensitivity`**: resid_Q3bFam Spearman 0.978 vs Q4Fam, Jaccard top1 0.73, top5 0.77 — stable; but `resid_Q3bFam` vs cross-audience drop distinction is thin for 1–2p where specialist_ge20 threshold ≥20 is too stringent (heavy specialists median 0.27 for 18XX vs 0.01 for Wargame, 0.006 Party — global threshold not discriminating).

**Gap:** `insufficient_overlap` 23% overall (3385/14698), **34% for solo_first (238/691)** and 33% for duel (851/2555) vs 18% for solo_mech — **propensity framework misses very small eligible pools** (1–2p needs smaller thresholds or solo-specific at-risk population). Weight_within_05 mean 0.48 SD 0.34 not type-specific; ownership share_own 0.57 p75 0.66 conflated with snapshot.

**Survives:** **Keep definitions**, but **extend audience-selectivity with solo_first/duel-specific specialist metrics + small-pool propensity**.

### 4. Model Specification (§4)
**Baseline Q3bFam 48f CV 0.6033 ±0.0058** (Q3b 45f 0.5987, Q4Fam 78f 0.6151). Tested **22 candidates one-by-one + jointly** (5-fold paired, seed 20260824, same as 9B, n≥50 gate documented).

**Per-dimension CV mean+fold+β/SE, residual before/after, Spearman/Jaccard (model_comparison.csv):**
- No candidate reaches **18XX bar** (+0.676→0.000, β +0.748 ±0.062, 5/5, Δ+0.0046). Closest: duel +0.080→beta +0.201, Δ+0.0038, Jaccard 0.814; solo_first +0.128→+0.176 Δ+0.0014 Jaccard 0.947; game_system +0.162 but n=32 <50; edition +0.116 Δ+0.0006.
- Joint `Q3bFam+solo+edition+system` Δ+0.00197 < duel alone, confirming overlap.

**Decision keep/add:** **Keep Q3bFam as primary, add none to quality model**. All systematic residuals belong in **audience-selection / screening / cleanup**, not model — adding them would be **leakage** (design → quality). Keep Q4Fam as sensitivity (Spearman 0.993–0.999 vs extended).

### 5. Audience-Selection Methodology (§5)
**Existing Step7/7B/7C framework:**
- **Adequate:** specialist share + TVD correctly distinguishes narrow (duel wargame high spec) vs broad (4p Euro low) where primary_type defined; volume/ownership/weight splits have support where n≥10 (≥10: 9227 volume, 4626 specialist; ≥5: 12166/ ~5600). Propensity overlap adequate for n≥100 (32.8% adequate, 44% borderline overall).
- **Thin:**
  - **Specialist threshold global q75 (0.94)** not type-specific: broad categories (Economic 0.76, Party) need ≥20 not ≥10; narrow 18XX median 0.24 flagged as low incorrectly.
  - **Solo-first/mode-constrained selection not captured**: primary_type has only 6 types (18XX/Wargame/Party/Econ/Coop/Legacy); solo_first/duel/strict_solo have **no dedicated specialist metric** (solo_mech spec share_ge20 global but weight-driven, not player-count-driven). Result: solo_first insufficient 26.2% vs overall 18.9% and duel insufficient 25.8% (high).
  - **Very small eligible pools (1–2p)**: propensity uses `ALL_ACTIVE_primary_TYPE_GE10` at-risk; for max≤2 the at-risk denominator should be **constrained by player-count eligibility** (e.g., users who rated ≥10 games with max≤2). Current denominator inflates missing and understates overlap → **insufficient_overlap 33–34% vs 23% overall**; ESS ratio low, max_weight inflated.
  - **Cross-audience insufficient**: solo_first cross_support_ge10 80.5% vs overall 86.2%; duel 83.3%; specialist_0-4_vs_ge20 has only 4626 games ≥5 (vs 12166 volume) — power limited for niche.

**Proposed:** **Add solo_first/duel-specific propensity covariates + at-risk defined by player-count eligibility + lower specialist threshold (≥5) for small pools + new weight-within-type specialist flag**.

## Preserved Components (evidence-supported)
- Q3bFam 48f + hiddenness <1,700 / 1,700–2,500 / >2,500 + adj≥7.5 & resid≥0.75 (532 prelim, 39 strong) — **preserved** (no threshold evidence).
- Severity-adjusted adj_mean mu 7.139 (EB w median 0.994, λ 2.00) — preserved, NOT refit.
- Q4Fam 78f sensitivity (CV 0.6151, Spearman 0.9775) — preserved.
- Step7/7B/7C framework (with extensions above) — preserved.
- pruned_lists 269 cleanup — preserved, plus edition-title extensions (below).

## Proposed Changes Summary (auditable, per change)
See `proposed_changes.md` for full table (22 rows: change_id | observed_problem | generalizes_evidence (counts/CV/Jaccard) | belongs_in | effect | keep/change).

**Model:** **NONE added to Q3bFam** — keep 48f primary (18XX already fixed). Rationale: no non-18XX candidate meets omitted-family bar; largest CV gain (duel) is leakage between design and quality.

**Cleanup / Screening (proposed, awaiting review):**
- **C-edition_title** (`flag_edition_title` n=501, +0.116, β +0.123 5/5 Δ+0.0006 Jaccard 0.921) → **add 5 title patterns ("Collector's Edition","Ultimate Edition","Kickstarter Edition","Complete Collector" etc) to pruned_lists + final screening `niche_vs_strong` rule** — **PROPOSED_CLEANUP — not model**.
- **C-game_system** (n=32 +0.162, below gate) → **keep `Admin: Game System Entries` as hard hiddenness exclude (not hidden, like expansions) + screening flag** — **PROPOSED_SCREEN**.
- **C-semi_coop** (n=98 -0.252 5/5) → **monitor as screening note (negative resid, small)**.

**Audience-selection (proposed):**
- **C-solo_first** (n=691 +0.128 β +0.176 5/5 Δ+0.0014) + **C-duel_1_2p** (n=2555 +0.080 β +0.201 5/5 Δ+0.0038) + **C-wargame_duel** (n=1153 +0.074 Δ+0.0017) → **add solo_first/duel-specific specialist metrics (≥5 threshold) + propensity covariate `is_solo_first`/`is_duel` + player-count-eligible at-risk population + cross-audience split `solo_first_0-4_vs_ge10`** — **PROPOSED_ADD to Step 7, not Q3bFam**.

**No change:** solo_mech, team_mech, coop_solo, light/heavy weight, series_any/game_family etc (<0.10 resid or no CV) — **PRESERVE**.

**Effect on out-of-sample & stability:** No model change preserves **CV R² 0.6033, Spearman≈1, Jaccard 1.0 vs Q3bFam** (by definition). Screening additions would remove ~2 edition-leak games from strong (5.1% → 0%) and flag ~15 duel wargames as niche if cross drops — Jaccard top1 0.921 for edition, 0.814 for duel shows **material local screening change without global re-ranking** (Spearman >0.993).

All claims tagged per AGENTS.md; proposed not final.

## Files
- `game_lineage_audit.md` + `lineage_evidence.csv` (§1)
- `audience_structure_audit.md` + `audience_evidence.csv` (§2)
- `broad_appeal_audit.md` (§3)
- `model_spec_audit.md` + `model_comparison.csv` (§4)
- `audience_selection_methodology_audit.md` (§5)
- `proposed_changes.md` (auditable per-change table)
- `pass3_investigation_summary.json` (machine-readable)

## Reproduce
```bash
.venv/bin/python scripts/52_pass3_investigation.py  # game-level only, bounded
```

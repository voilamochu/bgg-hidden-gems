# Pass 3 Independent Review — Scout Report

**Reviewer:** `bgg-pass3-review` (scout, no branch, no PR)  
**Reviews:** `bgg-pass3-investigation` branch `fm/bgg-pass3-investigation` (commit `ce16ecb`) — investigation outputs under `docs/phase2-pass2/pass3_investigation/` + `reports/phase2_pass2/pass3_investigation/` + `scripts/52_pass3_investigation.py` + `findings.md` entry `proposed — awaiting review`  
**Population audited:** Pass-2 canonical `14,698` games × `287,302` users × `24,146,307` obs (`data/processed/phase2-pass2/`, mu `7.139`, Q3bFam 48f CV `0.6033`, Q4Fam 78f CV `0.6151`)  
**Diagnostic sample audited:** `39` strong / `176` plausible / `163` niche / `127` insufficient / `27` excluded_popular (`docs/phase2-pass2/step11-12_hidden_gem_screen/screening_evidence_table.csv`)  
**Generated:** 2026-08-25 · reviewer seed independent (re-ran counts via `.venv/bin/python` against same parquets)

---

## Executive Summary: Which Proposed Changes Survive Review

**Overall verdict:** The investigation is **substantially sound in logic and belongs_in separation** — it correctly keeps `Q3bFam 48f` unchanged (no leakage), correctly classes `solo_first`/`duel`/`edition` as **screening / propensity** not quality-model, and correctly gates on `n≥50` / 5-fold. **No proposed Q3bFam addition survives** — and the investigation itself proposes none, which is the right call.

**What survives as proposed (with caveat “needs broader test before finalizer rerun”):**
- **`Q3bFam 48f primary + hiddenness <1,700 / 1,700–2,500 / >2,500 + adj≥7.5 & resid≥0.75 + severity mu 7.139 + Q4Fam sensitivity` — SUPPORTED (preserve).** No evidence to move thresholds.
- **`pruned_lists 269` base — SUPPORTED (preserve).** 0 pruned IDs remain in `14,698` (verified).
- **`C-game_system` (n=32, `+0.162`) as screening hard-exclude, NOT model — SUPPORTED** as `screening / semantic cleanup` but correctly below `n≥50` gate; no model change.

**What is UNSUPPORTED or NEEDS RERUN with broader test (do not finalize as proposed):**

| Change | Proposed | Review | Action for finalizer |
|---|---|---|---|
| **C-edition_title** (501, `+0.116`, β `+0.123` 5/5, Δ `+0.0006`, Jaccard `0.921`) — add 5 patterns to `pruned_lists` + screening | `PROPOSED_CLEANUP` — not model | **NEEDS RERUN — pattern-specific evidence missing** (see §1, §5). The 501-signal is real but heterogeneous and concentrated in `niche` (40/163 `24.5%`) not `strong` (2/39 `5.1%` ≈ pop `3.4%`). The 5 named patterns cover only **45** of the **501** (`Collector's 19`, `Ultimate 7`, `Kickstarter 15`, `Complete Collector 1`, `Essential 3`); their per-pattern resid/CV not shown. Finalizer must test **per-pattern** mean resid + β + CV with designer/year/weight corroboration, and report **sensitivity of strong 39 → 37** vs **niche 40 → ?** before adding. | Rerun with per-pattern breakdown (n, mean resid, β/SE, 5-fold, CV) + base-title duplicate completeness test (§5). Keep Q3bFam unchanged. |
| **C-solo_first** (691, `+0.128`, β `+0.176` 5/5, Δ `+0.0014`, Jaccard `0.947`) + **C-duel_1_2p** (2555, `+0.080`, β `+0.201` 5/5, Δ `+0.0038`, Jaccard `0.814`) + **C-wargame_duel** (1153, `+0.074`, β `+0.204` 5/5, Δ `+0.0017`) as **audience-selection** (propensity covariate + specialist metric + player-eligible at-risk + `≥5` threshold + cross split) | `PROPOSED_ADD to Step7, NOT Q3bFam` | **SUPPORTED in belongs_in, but NEEDS RERUN — heterogeneity and small-pool calibration not yet validated.** `duel` is composite (solo_first 691 + wargame_duel 1153 + Euro 2p ≈ 711) with **r = −0.70** to `log_max_players` (already in model) and **Jaccard `0.814`** (18% churn) — largest of all candidates. Investigation notes heterogeneity but does not test interaction (`wargame_duel` vs Euro 2p) or solo_mech overlap (≈400). Propensity at-risk redefinition (player-eligible ≥10 max≤2) and `≥5` threshold are **hypotheses** (not refit) that would change `insufficient` from `34.4%` solo_first / `33.3%` duel to hypothesized `~20%` — must be measured. | Rerun Step7B/7C with new covariates: test `is_solo_first` + `is_duel` + `wargame_duel` interaction in propensity (report overlap/insufficient/ESS/max_weight delta), and add `solo_first_0-4_vs_ge10` cross split (report support `80.5%`→? and niche_drop calibration). Use same 5-fold. Do **not** add to Q3bFam. |
| **C-series_any** (3222, `+0.066`, Δ `+0.0017`, Jaccard `0.921`), **C-game_family** (2740, `+0.032`), **C-team_mech**, **C-solo_mech**, etc. | `NO_MODEL` | **SUPPORTED as NO_CHANGE.** Resid `<0.10` not systematic; `series_any` CV `+0.0017` is franchise popularity, not omitted family like 18XX (`+0.676` → β `+0.748`). Correctly not added. | Keep. |
| **C-semi_coop** (98, `−0.252`, 5/5, Δ `+0.0006`, Jaccard `1.0`) | `MONITOR` | **SUPPORTED as no model** (n=98 borderline even for n≥50; negative resid distinct). | Keep as screening note only. |
| **C-game_system** (32, `+0.162`, Δ `−0.0001`, Jaccard `0.986`) + **C-series_unlock** (47, `+0.217`) etc. | `BELOW_GATE` | **SUPPORTED — correctly not model.** n<50, wide SE (`0.095`, `0.083`). | Keep as screening. |

**Leakage:** None proposed — investigation correctly avoids putting screening concerns into `Q3bFam`. **Do not revert** (see §3).

**Broad appeal:** Current pipeline (resid + hiddenness + specialist/TVD + propensity + cross) **measures the right kind of risk when type defined** (18XX/Wargame/Coop) but **misses duel/solo-specific selection** and **conflates** low-volume niche resid (`+0.128` solo_first remains in resid) with broad signal. Fix is the Step7 extension above, not a Q3bFam dummy (see §4).

**Lineage cleanup completeness:** Pruned 269 is validated, but title-pattern heuristic misses many duplicates (570 high-version not-ed, 275 base-title duplicates like `7 Wonders`/`7 Wonders Second Edition`, 254 reimpl>1 not-ed). Proposed 5-pattern extension is **incomplete** without a base-title + designer/year/weight corroboration test (see §5).

**Revised vs current strong 39:** With no model change, global Spearman `1.0` Jaccard `1.0`; screening-only edition change would be **37 vs 39** (remove `331259` Kickstarter and `338697` CATAN 3D) — **not demonstrably more defensible** (both currently `moderate_audience_selectivity`, `borderline_overlap`, `has_broad True`, `has_niche_drop False`; see §6). A true “better” set must be judged on **plausible 176 → niche 163 → insufficient 127** separation and **pass-rate of Q4 robust / taxonomy / cross** — not just different because tuned to 39.

---

## §1 Overfitting to the 39 Manually Reviewed Games

**Question:** Did investigation memorize the 39 `strong_hidden_gem_evidence` anecdotes, or does each proposed change generalize to wider `14,698` / `1,700`-eligible / `176` plausible / `163` niche?

**Evidence cited:** `model_comparison.csv:1-23`, `lineage_evidence.csv`, `audience_evidence.csv`, `proposed_changes.md:11-32`, `pass3_investigation_summary.json:13-19,161-360`, underlying `screening_evidence_table.csv` (532→39).

**Finding: SUPPORTED with caveat — investigation does test generalization, but the edition rule's generalization is *away* from the 39, and the solo/duel rules' generalization is *toward insufficient* not strong.**

- **Method is not memorization:** Script `52_pass3_investigation.py:248-391` computes per-candidate `n`, `mean_resid_Q3bFam`, `share_top5`, `β/SE`, `fold_betas` (5-fold paired, seed `20260824`), `Δ CV R² / RMSE`, `Spearman`, `Jaccard top1/5` **across the full `14,698`** (not 39-only). It also reports `overlap_strong_n / pct` explicitly. This is the correct generalization test per task.
- **Counts do generalize beyond 39** (verified by re-run, see commands §1):
  - `C-edition_title` n=`501` (`3.41%`) mean resid `+0.116` (median `+0.141`, SD `0.568`, share top5 `10.6%` vs `5%` expected) — **enriched 2× in top5**. But enrichment is **not in strong**: strong `2/39` (`5.1%`) ≈ pop `3.41%`; plausible `6/176` (`3.4%`) = pop; **niche `40/163` (`24.5%`)** is the enriched group (verified via `games`+`screening_evidence_table.csv` join). So the systematic resid is real **population-wide**, but its *screening consequence* is concentrated in niche, not strong. Proposed change that moves `2/39` to `0` while moving `40` niche is **not overfit to 39**, but its *defensibility gain* must be judged on niche vs plausible separation, not just strong.
  - `C-solo_first` n=`691` (`4.7%`) mean `+0.128`, share top5 `5.8%`: strong `4/39` (`10.3%` ≈ 2× pop), plausible `12/176` (`6.8%`), niche `8/163` (`4.9%`) ≈ pop, insufficient `11/127` (`8.7%`). Pattern generalizes but **not monotonically** (strong > plausible > niche). Taxonomy for strong is `0` high (all 39 low/moderate) while niche has `27/163` (`16.6%`) wargame_duel — indicates solo_first not the driver of niche.
  - `C-duel_1_2p` n=`2555` (`17.4%`) mean `+0.080`, share `5.8%`: strong `8/39` (`20.5%`) slight > pop, plausible `41/176` (`23.3%`), niche `37/163` (`22.7%`), **insufficient `43/127` (`33.9%`) >> pop**. So duel enrichment is **strongest in insufficient** (where propensity `insufficient_overlap` already `33.3%` vs `23%` overall). Proposed propensity extension is therefore **not overfit to 39** — it would help where evidence is thin, not just strong.
  - `C-wargame_duel` n=`1153` (`7.84%`) mean `+0.074`: strong `0/39` (`0%` — under-represented), plausible `4/176` (`2.3%`), niche `27/163` (`16.6%`), insufficient `20/127` (`15.7%`). Again niche/insufficient carry the signal, strong avoids it. **Rule that “moves the 39 but not the 176” would be overfit — this does not; it moves niche/insufficient more than strong.** Investigation notes this (`audience_structure_audit.md:40-43`).

- **Residual means and CV deltas are population:** All `Δ CV R²` in `model_comparison.csv` are **paired 5-fold means across 14,698** (same permutation as Step 9B). E.g., `duel_1_2p` Δ `+0.0038` (fold `+0.203 +0.189 +0.198 +0.196 +0.217`, SD `0.010`, SE `0.017`), `solo_first` Δ `+0.0014` (5/5), `edition` Δ `+0.0006` (5/5), `series_any` Δ `+0.0017`. **None driven by single fold** (SD `0.01–0.02`). `Jaccard top1` for duel `0.814` (18% churn), solo_first `0.947` (5% churn), edition `0.921` (8% churn) — all population-wide, not 39-only.

- **What investigation got right:** It explicitly labels diagnostic `39` as `diagnostic only, not ground truth` (`README.md:5`, `pass3_investigation_summary.json:14`) and tests `176 plausible / 163 niche / 127 insufficient` explicitly in `audience_structure_audit.md`.

- **Gap — still needs rerun:** `Jaccard` reported for *model addition* (`Q3bFam+flag`), but **proposed changes are screening/propensity, not model addition**. For edition, screening Jaccard `0.921` is actually the *model* Jaccard; the *screening* Jaccard (strong `39→37`, pool `532→?`) is not computed. Finalizer must compute **screening-pool Jaccard** and **outcome-category transition matrix** (strong/plausible/niche/insufficient) before claiming improved defensibility. Also need `14,698` counts for `1,700-eligible` hiddenness vs `plausible` — investigation preserves hiddenness `<1,700` without testing hiddenness sensitivity for solo vs 4p (correctly, but should report `solo_first` hiddenness eligible `88%` vs overall `91%` — similar).

**Recommendation for finalizer (§1):** For each `PROPOSED` change, report **four-column generalization** (`strong 39`, `plausible 176`, `niche 163`, `insufficient 127`, `14,698` pop, `1,700`-eligible `485` of pool) with **counts, mean resid, share top5, and Jaccard on screening outcome**, not just on resid ranking. A rule that only moves `2/39` but not `6/176` and `40/163` is overfit — current edition rule is *not* that, but per-pattern evidence is missing.

---

## §2 Unsupported Penalties for Cooperative / Solo / Other Modes

**Question:** For each proposed penalty or new `fam_*`/`mech_*` for `Cooperative`/`Solo`/`1-2p`/`duel`, did investigation show systematic residual + 5/5 CV gain, or assume mode needs penalty without evidence? Flag `n<50`, wide SE, fold-inconsistent `β`.

**Finding: SUPPORTED — investigation correctly shows evidence where it exists, and correctly *does not* propose a Q3bFam penalty. Where it proposes Step7 extension, evidence is systematic but needs interaction test.**

Evidence per `audience_evidence.csv` + `model_comparison.csv:13-23` (seed `20260824`, 5-fold):

| Mode | n | mean resid | β (added) | SE | fold 5/5 | Δ CV R² | Jaccard top1 | Proposed belongs_in | Verdict |
|---|---|---|---|---|---|---|---|---|
| **Cooperative** (`mech`) | 1543 (`10.5%`) | `−0.000` (by construction) | `+0.083` in Q3bFam (`SE 0.017`, 5/5) | — | — | — | — | **Already in Q3bFam** `fam_Cooperative Game` (`model_spec_audit.md:44-45`, `audience_structure_audit.md:11`). Correctly **no duplicate**. Enrichment in strong `22/39` (`56.4%`) vs pop `10.5%` persists *after* correction — not a missing penalty. |
| **Solo / Solitaire mech** | 1397 (`9.5%`) | `+0.011` | `+0.016` `SE 0.018` | 5/5 + | `+0.0` | `1.000` | `NO_CHANGE — preserve` | **Correct: not systematic** (`<0.03`, CV `0`). |
| **Team-Based mech** | 802 (`5.5%`) | `+0.030` | `+0.036` `SE 0.020` | 5/5 + | `+0.0001` | `0.96` | `NO_CHANGE` | **Correct: <0.10.** |
| **Semi-Coop** | **98** (`0.67%`) | **`−0.252`** | `−0.258` `SE 0.054` | 5/5 − (all −) | `+0.0006` | `1.00` | `MONITOR — screening note, not model` | **Correct: systematic but n small (below 500-analogue; passes n≥50 gate but Jaccard `1.0` means no global churn).** Not a penalty in model. |
| **solo_first** `min1 max≤2` | **691** (`4.7%`) | **`+0.128`** | **`+0.176` `SE 0.024`** | **5/5 +** (`+0.190 +0.174 +0.156 +0.177 +0.183`, SD `0.013`) | **`+0.0014`** | `0.947` | **Step7 propensity + specialist, NOT Q3bFam** | **Systematic + CV pass but `<0.15` bar; correctly not model.** Homogeneity concern: `solo_first` weight mean `2.43` vs non `2.08`; `r` with `log_max` `−0.41`. |
| **duel 1–2p** `max≤2` | **2555** (`17.4%`) | **`+0.080`** | **`+0.201` `SE 0.017`** | **5/5 +** (`+0.203 +0.189 +0.198 +0.196 +0.217`, SD `0.010`) | **`+0.0038`** (largest) | **`0.814`** (18% churn) | **Step7 propensity + cross, NOT Q3bFam** | **Systematic but heterogeneous** — contains `solo_first 691` + `wargame_duel 1153` + Euro 2p. `r` with `log_max` `−0.70` (collinear with existing `log_max_players_c`). Joint `solo+edition+system` Δ `+0.00197` < duel alone `0.0038` → collinear. Correctly not model. |
| **strict_solo** `1p==1` | 249 (`1.7%`) | `+0.121` | `+0.141` `SE 0.036` | 5/5 + | `+0.0003` | `0.96` | `NO — covered by solo_first` | Correct — subset of solo_first (redundant). |
| **wargame_duel** | 1153 (`7.8%`) | `+0.074` | `+0.204` `SE 0.026` | 5/5 + | `+0.0017` | `0.947` | **Interaction in propensity, not model** | **Systematic but `<0.10` before, CV `0.0017` after — audience structure. Correctly not model.** Strong `0/39` while niche `16.6%` — would be leakage if added as fam. |
| **Light/Heavy weight** | 4293/929 | `−0.018`/`−0.045` | `−0.059`/`−0.082` | 5/5 − | `+0.0004`/`+0.0003` | `0.947`/`0.986` | `NO_CHANGE — weight_c linear already` | Correct. |

**No “assumed penalty” exists.** Investigation does not propose `fam_*` dummies for these modes in `Q3bFam`; all `PROPOSED_ADD` are **audience-selection** (`proposed_changes.md:26-27`, `audience_structure_audit.md:52-55`). This matches the AGENTS.md warning: *“Do not assume correlation = bias … keep competing explanations open”* — the +0.128/+0.080 could be design constraint or selection, and investigation flags it for **specialist metric** rather than normalizing it as expected quality.

**Specific call-outs (per task):**
- **Cooperative:** Already correct (`fam_Cooperative` β `+0.083±0.017` in Q3bFam). No new penalty. Correct.
- **Solo mech, Team mech:** `n≥50` pass but SE `0.018`/`0.020` and resid `<0.04` and Δ `0` — **no penalty, supported.**
- **Game_system (32, `+0.162`, SE `0.095` wide, fold SD `0.08`, CV `−0.0001`)** — **correctly below gate**, not model (`proposed_changes.md:12`, `game_lineage_audit.md:21`). Wide SE correctly noted.
- **Series_unlock (47, `+0.217`, SE `0.083`, but `n<50`)** — correctly below gate, not model (`model_spec_audit.md:35`, `lineage_evidence.csv:8`).
- **Duel_1_2p:** `n≥50` gate pass, tight SE, 5/5, large CV — but **Jaccard `0.814` indicates material local re-ranking** (vs Q3b→Q3bFam Jaccard `0.898`). Investigation correctly labels this as *screening churn* and keeps it out of model to avoid leakage (`model_spec_audit.md:24`).

**Needs rerun (§2):** Propensity additions (`is_solo_first`/`is_duel` as covariates, player-eligible at-risk, `≥5` specialist threshold, `solo_first_0-4_vs_ge10` split) have **no CV yet** — they are hypotheses in `audience_selection_methodology_audit.md:35-41`. Finalizer must run **propensity refit** with those covariates and report **overlap_status delta** (solo_first `34.4%`→?, duel `33.3%`→?, overall `23%`) + **ESS ratio / max_weight** + **cross_support_ge10** (`80.5%` solo_first, `83.3%` duel vs `86.2%` overall) + **sensitivity_class stability**.

---

## §3 Leakage Between Quality Modelling and Screening

**Question:** Is any proposed change putting a screening concern (edition, hiddenness, audience risk) into `Q3bFam`, leaking screening target into `expected_quality` and inflating `R²` while hurting `Jaccard`?

**Finding: SUPPORTED — investigation correctly avoids leakage; no proposed Q3bFam addition. Flag for finalizer: do not regress screening on itself.**

- **Baseline:** `Q3bFam 48f` = `vol bands (7)` + `ns_year (3)` + `core_structure (6: weight_c, log_playtime_c, min_players_c, log_max_players_c, is_reimpl_num, log_n_impl_c)` + `cats≥500 (28)` + `fam_18XX/Coop/Legacy (3)` (see `model_spec_audit.md:3-4`, `scripts/52_pass3_investigation.py:58-83`). It **does not contain** edition_title, game_system, solo_first, duel, wargame_duel, series_any, etc.
- **Proposed Q3bFam change: NONE** (`README.md:8-15`, `proposed_changes.md:9`, `model_spec_audit.md:69-72`, `pass3_investigation_summary.json:54-57`). This is explicitly **not leakage**. `joint_model_test.csv` shows `Q3bFam+joint_solo_edition_system` Δ `+0.00197` vs duel alone `+0.0038` — overlap, not independent — and investigation **rejects** it (`model_spec_audit.md:62-64`).
- **Belongs_in audit is explicit** (`proposed_changes.md:5-6`, `scripts/52_pass3_investigation.py:515-627`):
  - `C-edition_title` → `semantic cleanup (pruned_lists) + final screening (not model)` — **correct: would be leakage** (“would normalize inflated edition ratings as expected quality” `proposed_changes.md:11`, `game_lineage_audit.md:43`). Adding edition dummy would set mean resid `0` for those `501` but hide the shared-audience inflation we need to screen.
  - `C-solo_first`/`C-duel_1_2p`/`C-wargame_duel` → `audience-selection (specialist + propensity)` — **correct: otherwise would conflate design constraint (1–2p) with expected quality** (`audience_structure_audit.md:48`). Current `min_players_c` + `log_max_players_c` linear already captures part of this (`β −0.07`/`−0.08`); binary threshold is non-linear but still design.
  - `C-game_system` → `screening / hiddenness — hard exclude as not hidden (like expansions)` — **correct: 32 entries are collectible systems (Magic, Pokémon) not hidden gems by design** (`game_lineage_audit.md:44`).
  - `C-series_any`/`C-game_family` → `screening check, not model` — **correct: franchise popularity, not omitted family** (heterogeneous: Wallet `+0.004`, Unlock `+0.217` but `n<50`, EXIT `−0.099` `game_lineage_audit.md:25-26`).

- **Effect on metrics if leakage were introduced (counterfactual):** `duel_1_2p` added to model gives **CV `0.6072` (Δ `+0.0038`)** and **Spearman `0.993` vs Q3bFam** but **Jaccard top1 `0.814`** (`model_comparison.csv:18`). That is **material local re-ranking** (≈`0.186` churn) comparable to 18XX fix (`Jaccard 0.86`, Δ `+0.0046` `model_spec_audit.md:16`). Investigation correctly notes this would be **screening pool churn without quality justification** (`model_spec_audit.md:74-75`). Keeping `Q3bFam` preserves `CV 0.6033`, `Spearman 1.0`, `Jaccard 1.0` globally.

- **Risk — hiddenness:** Hiddenness `<1,700` is screening, not model (correlation with `users_rated` `0.971`, `16` discordant `popular_via_users` `broad_appeal_audit.md:18`). Investigation **preserves** `<1,700`/`1,700–2,500`/`>2,500` (`README.md:62`, `broad_appeal_audit.md:18`) and correctly does not put hiddenness into `expected_quality`. No evidence to adjust hiddenness by player count (solo_first eligible `88%` vs overall `91%` similar — `audience_selection_methodology_audit.md:54`).

**Recommendation:** Finalizer must keep `Q3bFam 48f` as primary and **audit any new covariate for leakage**: does it describe **game design** (mechanics/player count/weight) that should be in `expected_quality`, or **audience self-selection** (who rates it) that belongs in screening/propensity? The investigation’s taxonomy (`model` vs `screening` vs `cleanup` vs `hiddenness` per `proposed_changes.md:4-5`) is the right gate; require `n≥50`, `5/5` folds, `Δ CV ≥0.001` **and** `belongs_in == model` before any Q3bFam add — none meet it.

---

## §4 Whether “Broad Appeal” Is Actually Being Measured

**Question:** Target is broad appeal among **modern hobby board gamers** (knows/plays contemporary hobby games, median year `2015`), not general population. Does investigation’s cross-audience evidence (`cross_audience_results.csv`, `audience_selectivity`, `propensity`) actually measure that, or conflating low-volume niche enthusiasm with high-volume popularity, or using `TVD`/specialist share that misses duel/solo-specific selection? Where would true broad-appeal test need different data?

**Finding: SUPPORTED with explicit gap — investigation correctly defines hobby broad (not general pop) and shows where current pipeline measures vs conflates vs is thin.**

- **Definition audited** (`broad_appeal_audit.md:5-9`, `README.md:29-33`): *“Broad appeal = appeal to broad swathe of modern hobby board gamers — people who already know/play contemporary hobby games. NOT general population.”* Tag: `assumption/hypothesis` per AGENTS.md — not inferred. **Correct scope** (vs friend-provided debiased ranking that may conflate with general pop).

- **How pipeline measures it (kept separate per Step 8):** `broad_appeal_audit.md:15-21` lists 6 components:
  1. `adj_mean` (severity-adjusted mu `7.139`, EB λ `2.00` w `~0.99`) — corrects noise, not selection (`reports/phase2_pass2/step7_*`).
  2. `resid_Q3bFam` — quality conditional on vol/year/weight etc. **Does not** distinguish broad vs niche (`broad_appeal_audit.md:17`: “high resid can be niche mastery or broad excellence”).
  3. Hiddenness `<1,700` — obscurity, not appeal.
  4. Audience-selectivity (specialist `share_ge10/ge20`, TVD, `share_own`, herfindahl, penetration, taxonomy `low 26.8%` / `moderate 46.7%` / `high 7.6%` / `insufficient 18.9%`) — **directly measures pool narrowness** (observable selectivity).
  5. Propensity (`overlap_status` adequate `32.8%` / borderline `44.2%` / insufficient `23.0%`, `sensitivity_class` stable `34.1%` / strongly `10.8%`, `delta_quality`) — exposure-selection risk via at-risk `ALL_ACTIVE primary_TYPE_GE10`.
  6. Cross-audience (volume `10-24 vs 500plus` `12166/9227` ≥5/≥10, specialist `0-4 vs ge20` `4626`, ownership, weight; `diff ≥0.3 + z≥2 → niche_drop`) — tests if quality remains among non-specialists where supported.

- **Where it conflates (correctly flagged):**
  - **Low-volume niche conflation:** If family/mode omitted from `Q3bFam`, high rating among narrow audience appears as **high resid** (18XX `+0.676` before fix, now `0` via `fam_18XX` β `+0.748` 5/5 Δ `+0.0046`; solo_first `+0.128` and duel `+0.080` remain unfixed — would appear as underrated if not flagged via audience-selection `broad_appeal_audit.md:25`). Current pipeline **keeps Q3bFam without solo_first/duel dummies**, so these remain as resid inflation flagged downstream as audience-structure, not quality — **correct not to conflate** (vs putting them in Q3bFam would hide selection `model_spec_audit.md:70`).
  - **High-volume popularity conflation:** Volume gradient after severity still `+0.51` per `10×` (raw `+0.47`, partial weight/year `+0.40` `broad_appeal_audit.md:26`). Pipeline uses `n_obs` band dummies, so volume not conflated as quality (resid vs log_n `0.012` `model_spec_audit.md:9-14`), but `popular_via_users 16` discordant cases show hiddenness ambiguity (users_rated `>2,500` but `n_obs ≤2,500`).
  - **Residual alone ≠ broad appeal:** Even with Q3bFam, `resid≥0.75` top `6.2%` (`911` games) vs Q4Fam Jaccard `0.817` — stable, but **resid not calibrated to cross-audience**. Strong `39` have `0` niche_drop by construction; niche `163` have `17` niche_drop (`10.4%`) and plausible `0` — **resid alone would not separate them** (`broad_appeal_audit.md:27,43`). Pipeline’s separate dimensions correctly preserve this.

- **What cross-audience evidence would be needed — gaps (correctly documented):**
  - **Specialist/TVD miss duel/solo-specific selection:** Current `primary_type` has only 6 types (`18XX/Wargame/Party/Econ/Coop/Legacy`); solo_first/duel have **no dedicated specialist metric** (solo_mech spec `share_ge20` is weight-driven, not player-count-driven `audience_selection_methodology_audit.md:35`). Result: solo_first cross_support_ge10 `80.5%` vs overall `86.2%`; duel `83.3%` — evidence thinner; `spec_ge20` median `0.27` for 18XX vs `0.01` for Wargame vs `0.006` Party — **global threshold `0.94` (q75) not type-specific** (`audience_selection_methodology_audit.md:25-28`).
  - **Propensity small-pool thin:** At-risk `ALL_ACTIVE_primary_TYPE_GE10` for `max≤2` overstates missing and understates overlap → **insufficient_overlap `33–34%` for duel/solo_first vs `23%` overall**; ESS ratio low, max_weight inflated (`audience_selection_methodology_audit.md:18-20`, `pass3_investigation_summary.json:73-101`). Need **player-count-eligible at-risk** (e.g., users with `≥10` ratings of `max≤2` games).
  - **Cross-audience power thin where it matters:** Specialist `0-4 vs ge20` has only `4626` games (`31%` pop) with support — where niche detection matters, `155` are `broad_unavailable` (`broad_appeal_audit.md:41`).
  - **True broad-appeal test would need:** Same rater pool as modern hobby gamers random encounter → **exposure/under-exposure data** (who saw game but didn’t rate) — unavailable (snapshot collections, timestamp unresolved) `broad_appeal_audit.md:33`. Propensity provides exposure proxy via at-risk enthusiasts (e.g., `17338` heavy wargamers, median penetration `1%` per wargame) but **missing ≠ dislike** (identification limit).

- **Recommendation for finalizer (§4):** Do not claim broad appeal from `resid≥0.75` alone. Keep `hiddenness` + `audience_selectivity` + `propensity` + `cross` together. Validate any solo/duel extension with **new `solo_first_0-4_vs_ge10` split** and **player-eligible at-risk**; report **cross broad vs niche_drop calibration** (strong currently `32/39` `82%` has_broad, `0` niche_drop; plausible `10/176` `5.7%` has_broad — gap). For external validation of moderate/insufficient (`176+127`), note **data can’t answer reliably** (“we can’t tell” per AGENTS.md) without **external plays/sales or contemporary hobby panel**.

---

## §5 Whether Lineage Cleanup Is Complete

**Question:** Check `game_links_pass2`, `games_pass2.families`, `pruned_lists` coverage — are editions/reimplementations/expansions/sequels/system entries fully caught, or do title-pattern heuristics still miss cases that would pollute `39` or `532` pool? Propose completeness test.

**Finding: NEEDS RERUN — pruned 269 is validated but incomplete; title-pattern heuristic misses many duplicates; version truncation and family coverage are thin. Proposed 5-pattern extension is directionally right but insufficient without a base-title + designer/year/weight test.**

**What is caught (validated):**
- **Pruned 269** (`combined_primary_edition_family.csv` `169` + new `100`): **0 pruned IDs remain in `14,698`** (verified via `set(games_pass2.game_id) ∩ set(combined_primary) = 0` `game_lineage_audit.md:9-10`, re-verified above).
- **Expansions:** Correctly excluded at population definition (`34,491` via URL/flag/category `findings.md:15`); `n_expansion≥5` `n=267` mean resid `−0.009` (`model_comparison.csv:12`) — no sequel leakage. **Caught.**
- **Reimplementations:** Already in Q3bFam via `is_reimpl_num` + `log_n_impl_c` (β `+0.07`); `n>1` `n=257` `−0.031`, `high_version≥10` `588` `−0.007` — no resid after controls **if** `log_n_impl` correct. **Mostly caught** vis-à-vis expected quality, but `game_links_pass2` **truncates at 100** (`Catan 100`, `Carcassonne 100`, `Pandemic 87` — all capped) so `log_n_impl` is censored for top systems.
- **System entries:** `32` via `Admin: Game System Entries` (Magic, Pokémon, Summoner Wars) correctly flagged; current screening treats `system_flag` `True` as not hidden (`screening_evidence_table.csv`: strong `0/39` system, niche `7/163` system `7`, plausible `0` `lineage_evidence.csv:5`). **Caught for screening**, but resid `+0.162` remains in pop — correctly not in Q3bFam.

**Where it leaks (population evidence):**
- **Edition-title heuristic finds `501` (`3.41%`) remain** with systematic `+0.116` (β `+0.123` 5/5 Δ `+0.0006`, Jaccard `0.921` `lineage_evidence.csv:1`). Of `532` screening pool, **`55` (`9–10%`) have edition title** (pool `532` ed `55` verified); **of strong `39`, `2` (`5.1%`)** are edition-like (`331259` Kickstarter, `338697` CATAN 3D) — both legit distinct SKUs per investigation (`game_lineage_audit.md:17`), not duplicate leaks, but heuristic matches `476` edition-like titles still present vs `269` removed. **~15 edition-like titles in pool were not caught by primary pruned rule** (e.g., `Complete Collector`, `Ultimate`, `Essential` — `game_lineage_audit.md:30`). Strong diagnostic has `0` duplicate_flag true, so pipeline not currently letting duplicate editions into strong, but `476` remaining indicate rule is narrow (only `169` primary pruned vs many version-heavy games with `≤100` version links each via truncation).
- **Version count not signal due to truncation:** `n_version≥10` `588` `−0.007` (`1.0` Jaccard) and `n_version≥1` `2220` `+0.023` — not systematic **because** truncated at `100` and already proxied via `is_reimpl`. But `588` high-version games are **570 not-edition** (`Catan 100`, `Pandemic 87`, `Azul 59`, etc. — verified). Many are *not* edition titles but still duplicate systems (e.g., `7 Wonders` vs `7 Wonders Second Edition` `n_version 71` — not flagged as edition? actually is, but many aren’t). Heuristic misses **non-edition-title duplicates** like `A Dog's Life` `2940` vs `205101` (same title, different year `2001`/`2017`), `Puerto Rico` 4 variants, `Dominion` 2, etc.
- **Series/Game families not systematic but heterogeneous:** `series_any` `3222` `+0.066` Δ `+0.0017` (but Wallet `+0.004`, Unlock `+0.217` `n<50`, EXIT `−0.099` `game_lineage_audit.md:25`). `game_family` `2740` `+0.032`. Not omitted like 18XX, but **franchise popularity** would be leakage if added.
- **System entries still `32` with `+0.162` resid** (`18.8%` top5) — rare but elevated via shared collectible audience; correctly screened, not modeled.

**Proposed change audit:**
- **C-edition_title: add 5 patterns** (`Collector's`, `Ultimate`, `Kickstarter`, `Complete Collector`, `Essential` `proposed_changes.md:11`) to `pruned_lists` with designer/year/weight corroboration — **directionally correct but incomplete**: those 5 patterns cover only **`45` of `501`** (`Collector 19`, `Ultimate 7`, `Kickstarter 15`, `Complete 1`, `Essential 3` verified). Per-pattern resid/CV not shown; e.g., `Collector's Edition` may be enriched in `Ascension` family (`5` of `40` niche ed are `Ascension: Year X Collector's` with resid `1.17–1.54` but taxonomy `insufficient` or `moderate` — not all duplicates). Need per-pattern test.

**Completeness test proposed (not just new rule):**

For each `game_id` in `14,698`, compute **base title** = strip edition regex `(?i)\s*\(?((edition|anniversary|deluxe|premium|heritage|big box|collector|ultimate|essential|revised|second edition).*)$` and lower-case. Then for each base-title group with `≥2` games, **candidate duplicate** if:
- `designers` overlap (`≥1` shared) **and** `|year diff| ≤5` **and** `|weight diff| ≤0.3` **and** (`families` overlap via `Game:` or `Series:` or `game_links_pass2` version/reimpl link **or** title Levenshtein `≤3`).
- Flag groups where **not already** in `combined_primary_edition_family.csv` or `combined_sensitivity_dup.csv`.

**Re-ran quick base-title check:** `275` base titles have `≥2` games (e.g., `7 Wonders` `2`, `A Dog's Life` `2` `2001`/`2017`, `A Game of Thrones: The Card Game` `2` `2008`/`2015 Second Edition` — see §5 evidence). Of `588` high-version (`n_version≥10`), `570` are not edition-title — many would be caught by this base-title + designer/year/weight test but **not by current 5-pattern heuristic** (e.g., `Catan` `33` reimpl, `Pandemic` `13` reimpl). Report **count of missed candidate duplicates** and **how many of those are in `532` pool or `39` strong** (currently `0` in strong, but `48/532` edition-like indicates pool pollution; test would quantify missed non-edition duplicates).

**Recommendation for finalizer (§5):**
- **Keep** `pruned_lists 269` + `is_reimpl_num`/`log_n_impl_c` in Q3bFam.
- **Rerun completeness test** above (base-title + designer/year/weight + links) and report **missed duplicate count** + **resid for missed vs caught**.
- **Per-pattern, not blanket:** For the 5 proposed patterns, report **per-pattern `n`, mean resid, β/SE, 5-fold, CV, Jaccard**, and **designer/year/weight corroboration pass rate**. Do **not** add all `501` edition-title as `fam_*`; only those passing corroboration should enter `pruned_lists` (semantic cleanup) and become `screening` flag (like `edition_flag`), not Q3bFam.
- **Address truncation:** Note `n_version` capped at `100` and `n_implementations` truncated — lineage completeness for top systems (Catan, Carcassonne) is censored; document as limitation.

---

## §6 Whether Revised Candidate Set Is Genuinely Better Rather Than Merely Different

**Question:** Compare proposed revised pipeline’s `strong` set vs current Pass-2 `39` (and vs `Q3b` without `Q3bFam`): is it more defensible per evidence dimensions, or just different because tuned to `39`? Check `Spearman`/`Jaccard` and whether new `strong` still has `0` Pass-1 flags vs `niche` carrying them.

**Finding: SUPPORTED as “no model change = no global reranking” — but screening-only revised set (37 vs 39) is *merely different*, not demonstrably more defensible, until finalizer runs screening calibration.**

- **Current Pass-2 39 defensibility (baseline):**
  - `strong 39` all `eligible` (`n<1,700`, `100%` `1.0`), `quality_robust_LB7 True` (`100%`, LB `7.41–9.04`), `taxonomy` `moderate 35` (`89.7%`) / `low 4` (`10.3%`) / **`high 0` / `insufficient 0`**, `overlap` `borderline 30` (`76.9%`) / `adequate 9` (`23.1%`) / **`insufficient 0`**, `sensitivity` `moderately 29` / `stable 10`, `has_broad_specialist True 32/39` (`82%`), **`has_niche_drop False 0/39`**, `n_supported_ge10` mean `5.9` (`5–7`).
  - `niche 163` by contrast: `high 56` (`34.4%`), `insufficient 12` (`7.4%`), `has_niche_drop 17` (`10.4%`), `overlap insufficient 16` (`9.8%`), `edition_flag 46` (`28%`), `system_flag 7` (`4%`). **`strong has 0 Pass-1 flags (edition/system/family) vs niche carrying them`** (`screening_evidence_table.csv` verified: strong `0`/`0`/`0`, niche `46`/`7`/`0`, plausible `0`/`0`/`0`) — **current screening correctly separates**.
  - `plausible 176`: `high 0`, `insufficient 0`, `low 40` (`22.7%`), `has_broad 10/176` (`5.7%`), `n_supported 3.5` — **less cross support** than strong; `insufficient 127`: `insufficient 100%`, `n_supported 2.6` — **thin evidence**.

- **Q3b (without fam) vs Q3bFam 48f:** `q3b_vs_q3bFam_comparison.csv` shows `7.5+0.75` gate `Q3b 550` vs `Q3bFam 532`, intersection `512`, **Jaccard `0.898`**; `18XX` `35→4` (`31` lost when correcting). Q3bFam is **more defensible** (removes 18XX inflation). `Q3bFam` vs `Q4Fam` `Spearman 0.9775`, `Jaccard top1 0.73`, `joint 7.5+0.75` `Jaccard 0.817` (`broad_appeal_audit.md:42-43`) — stable.

- **Proposed revised pipeline (investigation’s proposal):** **Keeps Q3bFam 48f unchanged** → **global Spearman `1.0`, Jaccard `1.0`** vs current `39` (no reranking). The only change that would affect `strong` is **screening** `C-edition_title`: `2/39` edition strong (`331259` Kickstarter, `338697` CATAN 3D) would become `0/39` (niche already `40/163` `24.5%` ed, so niche would be `38/163` after). **37 vs 39** — `Jaccard` on strong `≈0.95` (`37/39`), on pool `532→?` (`55` ed pool → `~53` after removing 2 strong). **Spearman of resid unchanged** (`0.999` `model_comparison.csv:2`).
  - Are those 2 more defensible to exclude? Both are `moderate_audience_selectivity`, `borderline_overlap`, `has_broad True`, `has_niche_drop False`, `quality_robust True` — **defensible as strong** (see §6 evidence). Their base titles (`Sleeping Gods` `16201` vs Kickstarter `351`; `Catan` `143k` vs 3D `468`) are **distinct products** (different year/designer same but weight diff?) — pruned rule with designer/year/weight corroboration **would not necessarily prune them** (year same `2021`, designer same, but weight `3.0` vs `?` — need check). Investigation itself notes “both legit distinct SKUs, not duplicate leak” (`game_lineage_audit.md:16-17`, `README.md:10`). **Removing them is merely different, not more defensible**, unless new evidence shows shared-audience inflation (e.g., `share_own` `0.73`/`0.81` vs pop `≈0.57`).
  - Similarly, `solo_first`/`duel` propensity extension would **not change resid** (Jaccard `1.0` if not in model) but would **flag ~15 duel wargames as niche if cross drops** (investigation hypothesis `README.md:82-83`). Current duel strong `8/39` all have `has_broad True` or `low` taxonomy, so **no strong would move**; plausible/niche with `high` or `insufficient` would. That would **preserve strong 0 vs niche high** separation but make plausible more conservative — **potentially more defensible if cross calibration improves**, but not yet measured.

- **Is it tuned to 39?** No — `duel` is **not enriched in strong** (`20.5%` ≈ pop `17.4%`), `wargame_duel` is **`0%` in strong** vs `16.6%` niche (strong avoids it), `edition 5.1%` ≈ pop. So proposed changes are **not** chasing the 39’s idiosyncrasies; they are population-wide. Conversely, `cooperative` is `56%` in strong vs `10%` pop but **no new penalty** — correctly not tuned.

- **What finalizer must check before claiming “better”:**
  - **Spearman/Jaccard** of *screening outcome* (not just resid): `strong 39` vs `revised 37` (or with propensity, `38–40`); `plausible 176` vs revised; `niche 163` vs revised. Report **transition matrix** and whether **new strong still `0` Pass-1 flags** and **`0` high/insufficient taxonomy** while **niche still carries them** (`46→?` edition, `7→?` system).
  - **Evidence dimensions:** For new strong, report `taxonomy`, `overlap`, `sensitivity`, `has_broad`, `has_niche_drop`, `n_supported_ge10`, `lower_bound_adj` vs current strong — must be **≥ as stringent** (e.g., `≥80%` has_broad, `0` niche_drop, `≥5` support).
  - **Vs Q3b without Q3bFam:** Q3b→Q3bFam already more defensible (Jaccard `0.898`, loses `31` 18XX). Any revised that adds duel to Q3bFam would be **less defensible** (Jaccard `0.814`, leakage) — correctly not proposed.

**Recommendation:** Finalizer should **keep Q3bFam** and **treat screening/propensity changes as hypotheses to be validated**, not as “better” until **screening calibration** (edition per-pattern, solo/duel propensity refit) shows **new strong is ≥ as broad-supported and new niche still concentrates high/insufficient/edition**. Until then, `39` vs `37` is **different, not better**.

---

## Specific Recommendations for Finalizer: Keep / Drop / Rerun

### Keep (evidence-supported, preserve as is)
- **Q3bFam 48f + hiddenness + gates + severity + Q4Fam sensitivity.** (`pass3_investigation_summary.json:24-31`, `model_spec_audit.md:8-14`)
- **pruned_lists 269 base, 0 violation.** (`game_lineage_audit.md:9`)
- **No Q3bFam addition.** All `22` candidates fail `≥0.15 + 5/5 + CV≥0.001` 18XX bar or belong elsewhere (`model_spec_audit.md:58-60`). `duel` Δ `+0.0038` is largest but is design, not quality — **drop as model.**
- **Coop already in Q3bFam; solo_mech/team_mech/light/heavy — no change.** (`audience_evidence.csv:1-3`)

### Drop (do not finalize as proposed without rerun)
- **Do not add `fam_*` for `duel`/`solo_first`/`wargame_duel`/`edition` to Q3bFam** — leakage, heterogeneous, collinear (`r −0.70` duel vs `log_max` `§2`).
- **Do not blanket-add all `501` edition-title as fam** — would normalize inflation.

### Rerun with broader test (required before finalization)
For each, require **`n≥50` gate, 5-fold CV (seed `20260824` paired), `Jaccard` stability, and counts across `39/176/163/127/14,698/1,700-eligible`**. Tag claims per AGENTS.md.

1. **C-edition_title — per-pattern, not blanket:**
   - Script: `scripts/52_pass3_investigation.py` lineage block, but split `flag_edition_title` into 5 flags (`Collector's`, `Ultimate`, `Kickstarter`, `Complete Collector`, `Essential`) + rest `501−45=456`. For each, report `n`, `mean/median resid`, `share_top5`, `β/SE`, `fold 5/5`, `Δ CV`, `Spearman`, `Jaccard`, `strong/plausible/niche/insufficient overlap`. Also run **base-title + designer/year/weight completeness test** (§5) and report missed duplicates vs caught.
   - Criterion: Only patterns with `mean resid ≥0.10`, `5/5`, `Δ CV≥0.0005`, and **corroboration pass** (designer overlap + year `≤5` + weight `≤0.3`) enter `pruned_lists`; others stay screening only. Report **strong `39→?` and pool `532→?`** transition.

2. **C-solo_first / C-duel / C-wargame_duel — propensity + specialist, not model:**
   - Script: Extend `scripts/46` Step7B/7C propensity + `scripts/42` Step7 audience. Add covariates `is_solo_first`, `is_duel`, `is_wargame_duel` (test interaction vs additive), at-risk `ALL_ACTIVE_solo_first_GE10` / `duel_GE10` (player-eligible), threshold `≥5` vs `≥10`/`≥20`, and cross split `solo_first_0-4_vs_ge10` / `wargame_duel_0-4_vs_ge20`.
   - Report: **overlap** `insufficient 34.4%→?` / `33.3%→?`, `adequate 15.8%→?` / `25.2%→?`; **sensitivity** `strongly 22.7%→?` / `18.6%→?`; **ESS ratio / max_weight**; **cross_support_ge10** `80.5%→?` / `83.3%→?`; **taxonomy high** `19.1%→?` / `15.4%→?`; and **heterogeneity** `solo_first` vs `duel` vs `wargame_duel` vs Euro 2p residuals (e.g., `wargame_duel` `+0.074` vs Euro 2p `?`).
   - Keep Q3bFam `48f` unchanged; report **screening Jaccard** for outcome categories (strong/plausible/niche/insufficient) not just resid.

3. **C-game_system (32) — keep as screening, but document wide SE:**
   - No CV needed (below gate). Keep `Admin: Game System Entries` as hard hiddenness exclude (like expansions `game_lineage_audit.md:44`). Report `n=32`, `+0.162`, `SE 0.095`, `CV −0.0001`.

4. **Broad appeal calibration:**
   - For any revised strong, report **has_broad, has_niche_drop, n_supported_ge10, taxonomy, overlap, lower_bound_adj** vs current `39` (`82%` has_broad, `0` niche_drop, `5.9` support). Require **new strong ≥ current on these** to claim more defensible.
   - Note **external validation gap** for `176+127` moderate/insufficient — state “we can’t tell” without **external plays/sales or contemporary hobby panel** (`broad_appeal_audit.md:50`).

5. **Lineage cleanup completeness — report, not just rule:**
   - Run base-title duplicate test (§5) and report **missed count**, **resid of missed vs pruned**, and **how many in `532` pool / `39` strong** (currently `0` strong, `55` pool). Document `n_version` truncation at `100` as limitation.

### What must be in finalizer’s rerun output (auditable)
- Updated `model_comparison.csv` (per-pattern edition + solo/duel interaction) with `n, β, SE, fold_betas, CV Δ, Spearman, Jaccard`.
- Updated `audience_selection_methodology_evidence.csv` with new at-risk + `≥5` + solo_first split.
- `screening_pool.csv` transition matrix (old vs revised strong/plausible/niche/insufficient, with edition/system flags).
- Machine-readable `pass3_investigation_summary.json`-style delta with claim tags (`observed fact` / `empirical finding` / `model-dependent conclusion` / `hypothesis`).

---

## Evidence & Reproducibility

**Commands run (reviewer, read-only, bounded):**
```bash
.venv/bin/python -c "import pandas as pd; games=pd.read_parquet('data/processed/phase2-pass2/games_pass2.parquet'); print(games.shape)"  # 14698
cat docs/phase2-pass2/pass3_investigation/model_comparison.csv  # 22 rows, duel Δ+0.0038 Jaccard 0.814 etc.
cat docs/phase2-pass2/pass3_investigation/proposed_changes.md  # 22 rows auditable
cat docs/phase2-pass2/pass3_investigation/pass3_investigation_summary.json | python -m json.tool | head -n 100
.venv/bin/python scripts/52_pass3_investigation.py  # not rerun (reviewer read-only); inspected source
.venv/bin/python -c "import pandas as pd,re; games=pd.read_parquet(...); edition_pat=...; print((games['title'].str.contains(edition_pat,na=False)).sum())"  # 501
.venv/bin/python -c "import pandas as pd; se=pd.read_csv('docs/phase2-pass2/step11-12_hidden_gem_screen/screening_evidence_table.csv'); print(se['outcome_category'].value_counts())"  # 39/176/163/127/27
# Join checks for §1/§6 (strong vs niche edition/duel/solo_first) — see §1 code in analysis pane
```

**File:line references:**
- Population def: `scripts/52_pass3_investigation.py:54-99` builds baseline `14,698` from `data/processed/phase2-pass2/*` (reuses `scripts/48`, `scripts/49`).
- Candidate flags: `scripts/52:154-211` (edition `159-160`, version `161-168`, solo_first `193-194`, duel `195`, wargame_duel `204-205`).
- CV logic: `scripts/52:101-108` `cv_for_spec` + `248-391` per-candidate (5-fold paired, seed `20260824`).
- Belongs_in: `scripts/52:515-627` + `proposed_changes.md:5-32`.
- Baseline Q3bFam: `docs/phase2-pass2/step9_expected_quality_underratedness/model_comparison.csv:9-12` (Q3bFam CV `0.6033±0.0058`) + `docs/phase2-pass2/step9b_expected_quality_spec_audit/model_comparison.md:8-14`.
- Strong vs niche flags: `docs/phase2-pass2/step11-12_hidden_gem_screen/screening_evidence_table.csv:1` (83 cols) — verified strong `0` edition/system, niche `46`/`7`.
- Lineage pruned: `data/processed/phase2-second-pass/pruned_lists/combined_primary_edition_family.csv` (`169`) + `scripts/52:9-10`.
- Audience methodology: `docs/phase2-pass2/step7_audience_selection/audience_selectivity_game_level.csv`, `…/step7c_exposure_propensity_validation/propensity_validation_game_level.csv` (used in `scripts/52:426-481`).
- Broad appeal def: `docs/phase2-pass2/step8_hidden_gem_screening_design/*` + `broad_appeal_audit.md:5-50`.

**Limitations (per AGENTS.md, tag every claim):**
- Game-level only; no individual rating time series; `postdate`/`rating_tstamp` unresolved — time-based results run under both readings (not used here).
- Edition heuristic and base-title test are **proxies** for semantic duplicate; need designer/year/weight + manual audit for precision (some second editions are legitimate distinct games).
- `n_version` truncated at `100` — censored for top systems; `log_n_impl` partially corrects but lineage completeness for those is understated.
- `n≥50` gate is convention (investigation) and `≥0.15` 18XX bar is pre-stated but arbitrary; `semi_coop` `n=98` is borderline — keep as monitoring, not model, is conservative and correct.
- Propensity at-risk redefinition is **hypothesis** (not refit in this review) — must be validated before claiming reduced `insufficient_overlap`.

---

## Conclusion for Finalizer (`bgg-pass3-finalize`)

**Do not rerun full pipeline yet.** Incorporate this critique, then rerun **targeted** extensions:

1. **Keep Q3bFam 48f primary** (no leakage).  
2. **Rerun lineage per-pattern** (5 patterns + base-title test) and **audience propensity + specialist** (solo_first/duel/wargame_duel interaction, player-eligible at-risk, `≥5` threshold, new cross split) with 5-fold CV and screening transition matrix.  
3. **Report whether revised strong is genuinely more defensible** (≥ current on `taxonomy low/moderate`, `0` high, `0` edition/system, `≥80%` has_broad, `0` niche_drop, `≥5` support) vs merely different (`37` vs `39`).  
4. State where **“we can’t tell”** (moderate `176` + insufficient `127` + `23%` overall insufficient_overlap) without external data.

*— Scout review complete. No branch, no PR. Report written to `data/bgg-pass3-review/report.md` (primary) and mirrored to `docs/phase2-pass2/pass3_review/report.md`.*

# BGG Hidden Gems — Documentation Map

**Canonical population:** `14,698` games × `287,302` users × `24,146,307` obs (`data/processed/phase2-pass2/`, `mu 7.139`) — all docs below are built on this population unless noted.

This `docs/` was reorganized on `2026-08-26` from a flat `phase2-pass2`-heavy layout into **10 numbered top-level folders**, each with a clear purpose. Old `phase2-pass2/*` sub-reports are now top-level peers, not nested.

## Map

- **`00-overview/`** — project-level entry points: `research_report.md`, `research_summary.md`, `research_handoff.md`, `phase2_database_inventory.md`, `modern_euro_shortlist.md`, `second-pass-methodology-review.md`, `rq2_candidate_report.md`.
- **`01-population/`** — what counts as a game. `baseline/` (`baseline.json`, `baseline_report.md`, `comparison.md`), `recursive-closure/` (`RECURSIVE_CLOSURE_PASS2.md`, `recursive_closure_*.json/csv`), `anomalous-audit/` (`ANOMALOUS_AUDIT_PASS2.md`), `second-pass/` (`pruned_lists/` with `combined_primary_edition_family.csv` etc.), `future-review/` (population comparison, closure plan, iterations), and `comparison/` (`POPULATION_COMPARISON`, `ANOMALOUS_AUDIT`).
- **`02-extracts/`** — canonical extracts and validation: `phase2-active/`, `phase2-filtered/`, plus `parquet_catalog.csv`, `validation.json`, `extract_counts.json`.
- **`03-rater-behavior/`** — rater-level and selection-bias audits: `raterxgenre/` (`stage_a_joint_fit`, `stage_b`), `phase6-intermediate/` (`findings_and_conclusions_to_date.md`, `sensitivity_n100.md`).
- **`04-quality-model/`** — expected-quality modelling: `09-quality-underratedness/` (`step9` `Q-ladder` `Q3b primary 0.599` `Q4 0.613`, `volume_diagnostic.md`, `underratedness_methodology.md`), `09b-spec-audit/` (`Q3b` `+fam_18XX` `+0.748` `Jaccard 0.86`).
- **`05-audience-selection/`** — who rates what and how: `07-audience-selection/` (`audience_selectivity_*`, `cross_audience`, `step7_summary.json`), `07b-exposure-propensity/` (`propensity_*`, `step7b_summary.json`), `07c-exposure-validation/` (`propensity_validation_*`, `overlap_rules.md`), `08-screening-design/` (`screening_framework.md`, `audience_selection_policy.md`, `step8_decisions.json`).
- **`06-hiddenness-gates/`** — hiddenness definition and thresholds: `10-quality-gates/` (`threshold_sensitivity.csv` `532` `7.5+0.75`, `joint_gate_analysis.md`, `uncertainty_analysis.md`, `distributions_histograms.png`).
- **`07-candidate-screening/`** — Pass-2 screening on the thresholds: `11-12-screen/` (`532 → 485+20+27 → 39` strong `screening_evidence_table.csv`, `hiddenness_screen.md`, `outcome_category_breakdown.md`, `pass1_failure_mode_audit.md`), plus legacy `phase7/` (`phase7-candidate-screening`).
- **`08-pass3/`** — Pass 3 broad tune-up on the 39: `investigation/` (`52` `22` proposed changes, `5` dims), `review/` (`report.md` `30` sections, `Q3bFam` preserve, `37 vs 39` merely different), `final/` (`53/54` reruns, `39` preserved `Jaccard 1.0`, `pass3_final_summary.json`).
- **`09-pass4/`** — Pass 4 full redesign preparation (§1-7) that left `39` as monitoring (`per-pattern 501` `45` below gate, `solo_first 691`/`duel 2555` as monitoring, `intersect_250` `134/279k` as monitoring): `investigation/` (`55` `42` files), `final/` (`56/57` `39` preserved `per_pattern` `base-title` `heterogeneity` reruns).
- **`10-pass5/`** — Pass 5 binding eligibility & consequential screening (`459` hard + `308` borderline via deterministic `game_links`+`families`+`contained_in`+designer/year/weight, `ecosystem 25` hard, `audience` `691`/`2555` as screening not model, `intersect_250` reference as screening dimension, `Q3bFam` preserved): `investigation/` (`58` `44` files `39→30` proposed `9` movers), `final/` (`59/60` `33` strong `29` survive `10` lost `4` gained `Jaccard 0.67`).

## Where to start

- **New to the project:** `00-overview/research_report.md` → `01-population/README.md` → `04-quality-model/09-quality-underratedness/README.md`.
- **Hidden-gem pipeline:** `05-audience-selection/08-screening-design/screening_framework.md` → `06-hiddenness-gates/10-quality-gates/README.md` → `07-candidate-screening/11-12-screen/README.md` → `08-pass3/README.md` → `09-pass4/README.md` → `10-pass5/README.md`.
- **Population:** `01-population/baseline/baseline_report.md` + `01-population/recursive-closure/RECURSIVE_CLOSURE_PASS2.md` + `01-population/second-pass/README.md`.

## Conventions

- Every `README.md` in a numbered folder is the executive summary for that step, with `Population`, `CV R²`/`Jaccard`/`β` where applicable, and a `Reproduce:` line (`seed 20260824`, `4GB/3 threads`).
- `reports/phase2_pass2/` mirrors the old `docs/phase2-pass2/` layout for backwards compatibility; new `docs/` numbered folders are canonical.
- `findings.md` at the repo root is the dated, claim-tagged log (observed fact / empirical finding / model-dependent conclusion per `AGENTS.md`).
- `scripts/` are numbered sequentially (`47` Step 9 → `60` Pass 5 final) and are the single source of truth for each figure/table.

## Migration note (2026-08-26)

Old `docs/phase2-pass2/step*` and `docs/phase2-pass2/pass*` paths were `git mv`'d to the numbered folders above. Old paths no longer exist. `reports/phase2_pass2/` retains the old mirrored layout for external consumers. If you have a hard-coded `docs/phase2-pass2/step9_...` link, replace it with `docs/04-quality-model/09-...` (or `05-`/`06-`/`07-`/`08-`/`09-`/`10-` per the map). `docs/phase2-pass2/` now only holds the single `pass5_final` file that was permission-locked during the move — it will be removed on the next clean checkout.

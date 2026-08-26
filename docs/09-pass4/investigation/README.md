# Pass 4 Investigation — Full End-to-End Pipeline Reconsideration (Investigation Phase)

**Status:** `proposed — awaiting review` **NOT final** — this is **investigation only**, leaving full `532→` rerun and `Pass2 vs Pass4` comparison for finalizer after independent reviewer critiques (per Task §8).

**Generated:** 2026-08-25T15:58Z · seed **20260824** · population **14,698 × 287,302 × 24,146,307 obs**, `data/processed/phase2-pass2/` (mu **7.139**, `user_severity_pass2.parquet` + `game_adjusted_means_pass2.parquet` via scripts 39/40 — **reuse, do NOT refit severity or Q3bFam from scratch**) · **Q3bFam primary 48f CV 0.6033 + Q4Fam 78f CV 0.6151 from 9B/10**, hiddenness `<1,700 / 1,700–2,500 / >2,500` from 11-12, **39 `strong_hidden_gem_evidence` from `722d149 / bf1e7e9` as diagnostic only** · 5-fold paired CV same as 9B · bounded 4GB/3threads `scratch/ducktmp` · narrow aggregations, avoid 24M wide sorts

**Source:** Task `FIRSTMATE_OP: v1 launch-brief` Pass 4 §§1–8 + Pass3 final `bf1e7e9` (39 preserved, per-pattern/propensity documented as monitoring) is context — **do NOT simply re-encode the 39** — this is **full end-to-end redesign and rerun preparation**, not annotation.

**Reproduce (seed 20260824):** `.venv/bin/python scripts/55_pass4_investigation.py` (bounded, copy-once `scratch/phase2-pass2`, game-level 14,698 rows + narrow duckdb semi-joins for reference/hiddenness, no wide-table bug, handle 7 weight null as before via median 2.0 + flag)

---

## Executive Summary: Which Problems Are Real vs Not, Which Changes Survive 14,698 Generalization, Which Are Left for Screening

### §1 Entity / Lineage Eligibility — Revisit What Counts

**Observed problem (beyond 39 anecdote):** The 39 manual review exposed concern that title-based cleanup (`combined_primary_edition_family.csv` 269, `is_reimpl`, `edition_title` 501) is insufficient per Pass3 base-title completeness (285 dup titles 611 games, 39 corroborated 96, truncation at 100) [empirical finding]. Pass4 asked to use **richest BGG relationships + actual descriptions where useful** to distinguish genuine standalone games — not statistically predictive requirement.

**What's richest? — Observed fact:** BGG description in this dump is **NOT rich** — `games.description` is a single-sentence tagline (mean 62 chars, max 85, e.g., CATAN tagline; only 20/14,698 contain "expansion", 0 contain "requires ... base") — **full-paragraph description not present in extracts** (parquet_catalog confirms 34 cols). **Eligibility must rely on structured relationships (game_links, families, tags, title, counts) not description depth** — description adds **no generalizable coverage** beyond title [empirical finding].

**Generalization across 14,698 (per `lineage_evidence.csv` 21 candidates, 5-fold CV, n≥50 gate):**

- **edition_title_any** 501 (3.41%) mean resid **+0.116** (median +0.141, share top5 10.6% vs 5% expected, 2× enriched) β +0.123 SE 0.025 5/5 + CV Δ+0.0006 Jaccard 0.921 — **real but modest (0.20σ), not 18XX-scale (+0.676)**. **But per-pattern 45 of 501** (Collector's 21, Ultimate 7, Kickstarter 15, Complete Collector 1, Essential 3) are **all n<50 below gate** — blanket 501 as fam would be overfit. **Second Edition 112** is only n≥50 per-pattern (+0.201 β+0.204 5/5 Δ+0.0004 Jaccard 0.973 <0.001) — legitimate new editions, not duplicates. **Not concentrated in 39 (2/39 5.1% ≈ pop 3.41%)** — enrichment is in **niche 40/163 24.5%**, not strong [empirical finding, Pass3 Review §1].
- **base-title completeness:** 285 dup titles 611 games → **39 corroborated groups 96 games** (designer overlap ≥1 + |year|≤5 + |weight|≤0.3) → **87 not pruned but only 10 in 532 pool (1.9%), 0 in 39 strong**; 11 truncated at n_version=100 [observed fact, `base_title_missed_dup.csv`]. **Gap is narrow, concentrated in niche, not strong.**
- **game_system** 32 (0.22%) +0.162 median +0.152 18.8% top5, but **n=32 <50 below gate**, wide SE 0.095 CV -0.0001 — **hard hiddenness exclude, not model** [empirical finding].
- **n_version ≥10** 588 -0.007 (no signal) — truncated at 100 and already proxied via is_reimpl+log_n_impl in Q3bFam; **n_reimpl>1** 869 +0.046 — no leakage [empirical finding].

**Survives as proposed — belongs_in NOT model:** **No new fam flag for quality model** — all systematic leakage belongs in **semantic cleanup / screening** (pruned_lists extension with per-pattern + designer/year/weight corroboration, base-title test) — otherwise leakage (would normalize inflated edition ratings). **C-game_system stays screening hard exclude** (already via `Admin: Game System Entries`). *Effect:* screening local Jaccard 0.814–0.986, global Spearman >0.993 — **no global overfit, precise extension** (87 missed, 10 poll) not blanket 501. **Implication:** 39 strong still **0 duplicate/system**, but **476 remaining indicate rule is narrow** — second-tier cleanup needed.

### §2 Re-examine Quality / Underratedness Model

**Preserved:** Pass-2 severity-adjusted quality; Q3bFam as primary; Q4Fam sensitivity; **18XX correction must remain (+0.676→0 via β+0.748 5/5)** — **all preserved** unless real reason [model-dependent conclusion].

**Per-new-fam test (model_comparison.csv 22 candidates one-by-one + jointly, 5-fold, n≥50 gate):**

- **No candidate reaches 18XX bar (≥0.15 +5/5+CV≥0.001+belongs_in model)** [empirical finding]. Closest:
  - **duel_1_2p** n=2555 +0.080 → β+0.201 5/5 Δ+0.0038 Jaccard 0.814 (18% churn, largest, comparable to 18XX +0.0046) — but **r -0.70 with log_max already in model**, heterogeneous (solo_first 691 + wargame_duel 1153 + Euro 2p) — **would be leakage**.
  - **solo_first** n=691 +0.127 → β+0.176 5/5 Δ+0.0014 Jaccard 0.947 — systematic but <0.15 and design constraint.
  - **edition_title** +0.116 Δ+0.0006 <0.001 — not systematic enough, and **belongs in cleanup, not model**.
  - **series_any** +0.065 Δ+0.0017 Jaccard 0.921 but <0.10 and heterogeneous (Wallet +0.004, Unlock +0.217 n<50, EXIT -0.099) — franchise popularity, not omitted family.
- **Joint** Q3bFam+solo+edition+system Δ+0.00197 < duel alone 0.0038 — **overlap, not independent**.

**Survives:** **Keep Q3bFam 48f CV 0.6033 as primary, Q4Fam 78f CV 0.6151 as sensitivity** — **add NONE to quality model** [model-dependent conclusion]. All systematic residuals belong in **audience-selection / screening / cleanup**, not model — adding would be leakage (design → quality) and would hide selection mechanism. Keeps Spearman ~1, Jaccard 1.0 globally.

### §3 Rebuild Broad Modern-Hobby Appeal — Main Conceptual Change

**Definition [assumption/hypothesis per AGENTS.md]:** Broad appeal = appeal to **broad swathe of modern hobby board gamers — people who already know/play contemporary hobby games**. **NOT general population, NOT all BGG users.** This is the estimand niche→hidden gap.

**Candidates tested (reference_population.csv 13 candidates, n_games/n_users via duckdb distinct users):**

| candidate | n_games | n_users | median weight | median year | median users |
|---|---|---|---|---|---|
| top250 bayes | 250 | 280k | 3.03 | 2017 | 21k |
| top250 users | 250 | 284k | 2.29 | 2014 | 29k |
| top250 adj | 250 | 189k | 3.73 | 2021 | 998 |
| **intersect_250 bayes∩users** | **134** | **279k** | **2.94** | **2015** | **33k** |
| intersect_100 | 40 | 251k | 3.26 | 2016 | 57k |
| intersect_500 | 327 | 283k | 2.69 | 2016 | 22k |
| profile weight2-3.5+2010+>5k | 420 | 264k | 2.59 | 2017 | 10k |

**Evaluation per Step7 audience_selectivity/cross logic [empirical finding]:**

- **Pure bayes** median weight 3.03 heavy — selects heavy Euro, misses light gateway.
- **Pure users** median weight 2.29 light — includes mass-market, conflates popularity (volume slope +0.51 per 10×) with modern hobby.
- **Pure adj** median users 998 low — narrow niche high-quality bias (adj is low-n niche like 18XX).
- **Top100 intersection 40 games too narrow** (ultra-popular only), **500 327 games too broad** (includes 1963-1990 classics, diminishing returns: 500 adds only 1.5% more users for 2.4× more games).
- **Profile 420 games 264k users** median users 10k less established than intersect 33k, TVD low but not strongly established.

**Survives — chosen [model-dependent conclusion]:** **`intersect_250_bayes_users` 134 games, 279,108 users, 4.96M obs — PRIMARY reference** — **intersection of highly ranked (bayes, which weights volume) and highly rated/high-volume (users)** — balances quality and reach, avoids single-metric bias, median weight 2.94 (between bayes 3.03 and users 2.29) and year 2015 = global median (contemporary), median users 33k deeply rated, covers **97% of active 287k** (near-universal hobby core). **Why defensible:** per Step7, its games have **moderate selectivity** (not high), cross support >90% (have power), and it is **externally defined (rank+volume) not model-dependent (not adj)**. **Alternatives kept as sensitivity** (100/500/profile). **n_games/n_users documented** per task.

### §4 Rework Audience-Selection Analysis Around That Reference

**Revised question (separates encounter/rate/rate-how/resemble-broad) [hypothesis]:**

| Dimension | Step7 asked | Pass4 asks with §3 ref | Can answer? |
|---|---|---|---|
| Likely to encounter | all 287k active as at-risk `ALL_ACTIVE_*_GE10` | **broad hobby core 279k (≥1 of 134)** — modern hobby encounter, not any BGG | penetration 0.146% eligible mean observable; missing≠dislike remains unidentified |
| Who rates | concentration TVD/spec/share_own → taxonomy | **vs REFERENCE pool, not global** — global TVD 0.167 high because global includes 1950s; reference TVD should be smaller for broad | Observable where type defined; **solo_first/duel have no dedicated specialist metric** (thin) |
| How raters rate | cross volume/specialist/own/weight | **plus solo_first_0-4_vs_ge10, wargame_duel split, reference-core vs non-reference** | Observable where ≥10 per side (86% overall, 80.5% solo_first) — thin for niche |
| Resemble broad? | not asked | **ref penetration, TVD vs ref, spec vs ref, cross ref-core vs non-ref** | New observables; where insufficient_overlap, preserve as unknown |

**Where Step7/7B/7C is adequate vs thin:**

- **Adequate:** specialist share + TVD correctly distinguishes narrow (duel wargame 0.906) vs broad (Euro duel 0.833) where primary_type defined; volume/ownership/weight splits have support where n≥10 (9227 volume, 4626 specialist); propensity calibrated (ECE 0.00034, AUC 0.822) — **keep** [empirical finding].
- **Thin:** global q75 0.94 not type-specific (Economic 0.76 vs 18XX 0.24); solo_first/duel have no dedicated specialist metric → insufficient 34.4%/33.3% vs overall 23% (small pools inflated); cross specialist 0-4 vs ≥20 only 4626 games (31%) — **power thin where it matters** [empirical finding].

**Survives as proposed (not yet rerun):** Keep taxonomy/propensity/cross core, **extend** with solo_first/duel-specific covariates (`is_solo_first`, `is_duel`, `is_wargame_duel` interaction), **player-eligible at-risk** (≥10 max≤2 ratings), threshold ≥5 for small pools, new cross splits + **reference-core vs non-reference** — all as **audience-selection, NOT Q3bFam** (otherwise leakage). **Uncertainty preserved** where counterfactual unidentified (insufficient_overlap, wide SE, max_weight 2132 for solo_first).

### §5 Explicitly Investigate Audience-Structure Effects

**Modes n, mean resid, β/SE +5/5 CV, Jaccard, TVD/specialist/cross/propensity (audience_structure_evidence.csv 15 modes) — full 14,698, not 39:**

- **Cooperative** n=1543 — already in Q3bFam β+0.083 5/5 resid 0 — **PRESERVE** [model-dependent].
- **Solo mech** 1397 +0.011 CV 0.000 — **no systematic, NO_CHANGE**.
- **solo_first** 691 +0.127 β+0.176 5/5 Δ+0.0014 Jaccard 0.947 — **systematic but not 18XX bar** — **audience not model** — spec 0.901 very high, insufficient 34.4% vs 23%, cross support 80.5% vs 86.2% — **very small eligible pool, propensity thin** — heterogeneity: wargame_duel vs Euro duel.
- **duel** 2555 +0.080 β+0.201 5/5 Δ+0.0038 (largest) Jaccard 0.814 (18% churn) — **heterogeneous** (solo_first 691 + wargame_duel 1153 + Euro 2p), r -0.70 with log_max — **belongs in audience, not model**.
- **wargame_duel** 1153 +0.074 β+0.204 5/5 Δ+0.0017 Jaccard 0.947 — **0% in 39 strong vs 16.6% niche** — strong avoids it, niche carries it; prop insufficient **47.7% vs Euro duel 21.5%**, max_weight 3696 vs 1284 — **doubly specialized niche**.
- **Team, Semi-coop (-0.252 n=98 5/5), heavy/light** — <0.10 or Δ<0.001 — **NO_CHANGE**.
- **Game_system** 32 +0.162 — **eligibility hard exclude**.
- **Edition_title** 501 +0.116 — **cleanup**.

**Decision:** **Do NOT impose blanket penalty** (Euro duel 1402 is broader, 8/39 strong include Euro duel) — workflow would wrongly penalize *7 Wonders Duel*-type broad 2p. **But do NOT treat harmless merely because fails Q3bFam gate** — solo_first +0.128 and duel +0.080 were systematic in Pass3 but kept as monitoring, now confirmed out-of-sample 5/5 but still **monitoring as audience, not model dummy** (otherwise leakage). **Per-mode evidence shows heterogeneity matters**: wargame_duel 47.7% insufficient vs Euro 21.5% — **not all 1–2p is niche**.

**Belongs_in:** All systematic 1-2p belong **primarily in audience-selection (new specialist metric + propensity covariate + cross)**, not as additive fam_* dummy [model-dependent].

### §6 Re-examine Hiddenness

**Preserved thresholds** `<1,700 / 1,700–2,500 / >2,500` [observed fact, 12186/694/1818 distribution] unless strong reason — **no strong reason found** [empirical finding].

**Distinction tested via §3 reference penetration** (`per_game_hiddenness.csv` 14,698 rows: n_ref_raters / 279,108):

| Bucket | n | mean n_obs | mean penetration | median | p90 | share >5% |
|---|---|---|---|---|---|
| eligible <1,700 | 12186 (82.91%) | 417 | **0.146%** | 0.093% | 0.349% | **0%** |
| borderline | 694 | 2035 | 0.724% | 0.711% | 0.852% | 0% |
| exclude >2,500 | 1818 | 9713 | 3.467% | 1.843% | 7.572% | **17.7%** |

*Further thresholds:* eligible >0.1% penetration: **46.98% (5725/12186)**; >0.2%: **23.86%**; >0.5%: **2.95% (360/12186)**; **>1%: 0%** [observed fact, `hiddenness_evidence.csv`]. **No eligible game reaches 1% hobby penetration** — max among eligible is **0.589%** (a wargame). Wargame-eligible mean is even lower: 0.109% vs borderline wargame 0.695% vs exclude wargame 2.88% [empirical finding].

**Investigation of "1,200-rating niche wargame that 80% of broad reference has rated" — hypothetical not observed:** Max observed 0.58% suggests **even niche wargames with many ratings are not hobby-broadly known** — 80% would be 223k core raters, but most wargames have <1,600 total ratings. **Numerically obscure (<1,700) is also hobby-obscure** — no need to condition on reference penetration for primary hiddenness [model-dependent conclusion]. **Borderline is transition** (mean 0.724% ≈ 2,015 core raters) — borderline captures **moderately familiar** (all borderline >0.5% vs eligible only 2.9% >0.5%) — **correctly needs extra scrutiny**.

**Survives:** **Preserve <1,700 / 1,700–2,500 / >2,500 as primary**; add **ref_penetration as monitoring column** (`per_game_hiddenness.csv`: n_ref_raters, ref_penetration) — flag `hobby_well_known` if >0.5% despite n<1,700 (360 games) for audience, not hard hiddenness gate.

### §7 Rebuild Final Screening Architecture — No Opaque Combined Score

**Proposed auditable flowchart/table per dimension, `belongs_in` and `effect`:** See `proposed_screening_architecture.md` — **six separate dimensions** (eligibility → quality → underratedness → hiddenness → audience selection → modern-hobby appeal), each gated, **no weighted sum**, preserve `insufficient_evidence` as valid `we can't tell` per AGENTS.md.

**Final outcome categories (from screened 505, no combined score):** strong 39 (7.7%) — all six pass with supporting cross-audience where available; plausible 176 (34.9%) — borderline (hiddenness borderline, SE LB dips, one audience dimension borderline); niche 163 (32.3%) — high spec/TVD/cross niche_drop/prop strongly/Q4 fragile/edition; insufficient 127 (25.1%) — cannot establish (wide SE, insufficient_overlap); excluded 27 (5.1%) — not hidden (>2,500) [observed fact from Step11-12].

**Preserved:** Q3bFam 48f, hiddenness buckets, pruned 269, adj≥7.5 & resid≥0.75 gate, taxonomy, propensity — **all SUPPORTED preserve** [model-dependent].

---

## Proposed Changes — Auditable Table per Change (15 rows)

| change_id | observed_problem | generalizes_evidence | belongs_in | effect | keep/change |
|---|---|---|---|---|---|
| C-edition_title | 501 remain, modest +0.116 but per-pattern only 45 of 501 (Kickstarter 15 etc n<50) — not concentrated in 39 (5%≈pop) vs niche 24.5% | n=501 3.4%, +0.116 beta +0.123 5/5 CV+0.0006 Jaccard 0.921, niche enriched | semantic cleanup + screening — NOT model | Per-pattern corroboration → exclude if corroborated (87 missed →10 pool) | PROPOSED_CHANGE — per-pattern with corroboration |
| C-game_system | 32 system 0.22% +0.162 0/39 but 32 remain elevated | n=32 <50 wide SE CV-0.0001 | hard hiddenness exclude (like expansions) | Keep explicit | PROPOSED_KEEP |
| C-base_title_dup | 285 dup titles 611 →39 corroborated 96 →87 missed →10 pool 0 strong, 11 truncated | 87 missed 1.9% poll, 0 strong | cleanup — NOT model | Base-title + designer/year/weight test → exclude | PROPOSED_CLEANUP |
| C-solo_first | 691 +0.127 systematic but <0.15, heterogeneous | n=691 beta +0.176 5/5 CV+0.0014 Jaccard 0.947 spec 0.901 insufficient 34.4% | audience-selection — NOT model | Add is_solo_first + player-eligible at-risk + cross solo_first_0-4_vs_ge10 | PROPOSED_ADD to Step7 |
| C-duel_1_2p | 2555 +0.080 largest CV +0.0038 but r -0.70 heterogeneous | n=2555 beta +0.201 5/5 CV+0.0038 Jaccard 0.814 — 18% churn | audience-selection — NOT model | Add is_duel + wargame_duel interaction + player-eligible | PROPOSED_ADD to Step7 |
| C-wargame_duel | 1153 +0.074 0% in strong vs 16.6% niche, insufficient 47.7% vs Euro 21.5% | beta +0.204 5/5 CV+0.0017 Jaccard 0.947 — doubly specialized | audience interaction | As interaction in propensity | PROPOSED — interaction |
| C-semi_coop | 98 -0.252 systematic negative but n small | n=98 beta -0.258 5/5 CV+0.0006 Jaccard 1.0 | screening note — monitor | Flag as niche type, not model | MONITOR |
| C-hiddenness | <1700 / 1700–2500 / >2500 preserved; no eligible >1% penetration, max 0.58% — 1700 alone sufficient | eligible 0.146% mean, 2.9% >0.5%, exclude 3.47% 17.7% >5% — order-of-magnitude gap | hiddenness — screening | Preserve buckets; add penetration as monitoring | PRESERVE + monitoring |
| C-reference_population | Need broad hobby reference — test 13 candidates | chosen intersect_250 134 games 279k users median weight 2.94 year 2015 33k — balances bayes+volume, covers 97% active | broad modern-hobby appeal | Define ref users ≥1 (sensitivity ≥5) of 134; compute ref_penetration, TVD vs ref | PROPOSED_CHANGE — adopt intersect_250 |
| C-quality_preserve | Q3bFam 48f CV 0.6033 + Q4Fam 78f CV 0.6151 + 18XX must remain | No new fam passes 18XX bar (≥0.15+5/5+CV≥0.001+belongs_in model); joint Δ+0.00197 < duel alone | quality — model | Keep Q3bFam unchanged; Spearman 1.0 Jaccard 1.0 | PRESERVE |

*Full 15-row auditable CSV:* `proposed_changes.csv`; *per-dimension CV:* `model_comparison.csv` (22 rows) + `joint_model_test.csv`; *lineage per-pattern:* `lineage_evidence.csv` (21 rows) + `base_title_missed_dup.csv`; *audience per-mode:* `audience_structure_evidence.csv` (15 rows); *hiddenness:* `hiddenness_evidence.csv` + `per_game_hiddenness.csv` (14,698 rows); *reference:* `reference_population.csv` (13 candidates) + `chosen_reference_gids.json` (134 gids).

**Out-of-sample & stability rule applied:** For every proposed change, show **out-of-sample** evidence (5-fold paired, seed 20260824, n≥50 gate, 5/5 folds, Jaccard top1/5 vs Q3bFam, Spearman) — not just 39 anecdote — done per §1/2/5/6. Thresholds: CV Δ ≥0.001, Jaccard stability, not driven by one fold (fold SD 0.01–0.02). **Model keep preserves global CV 0.6033 Spearman 1.0 Jaccard 1.0; screening/audience have local Jaccard 0.814–0.986 Spearman >0.993 — no global overfit.**

## Files (this investigation, mirrored `reports/phase2_pass2/pass4_investigation/`)

- `README.md` (this executive summary — §1–7 real vs not, which changes survive 14,698 generalization, which left for screening)
- `entity_lineage_audit.md` + `lineage_evidence.csv` + `base_title_missed_dup.csv` (§1 richest relationships + description, eligibility vs model, counts/residual/CV per candidate, pruned_lists gap, truncation at 100)
- `quality_model_reexamination.md` + `model_comparison.csv` + `joint_model_test.csv` (§2 per-dimension CV mean+fold+β/SE, residual before/after, Spearman/Jaccard, decision keep/add, 18XX preserved)
- `broad_appeal_reference_population.md` + `reference_population.csv` + `chosen_reference_gids.json` (§3 candidate modern-hobby reference populations tested, n games/users, definition, audience_selectivity vs reference, chosen + why + alternatives)
- `audience_selection_rework.md` (§4 revised question, separation encounter/rate/rate-how/resemble-broad, where Step7/7B/7C adequate vs thin, uncertainty preserved)
- `audience_structure_investigation.md` + `audience_structure_evidence.csv` (§5 coop/solo/1-2p/duel/mode counts, resid, β, cross/propensity, belongs_in)
- `hiddenness_reexamination.md` + `hiddenness_evidence.csv` + `per_game_hiddenness.csv` (§6 <1,700 vs hobby obscure vs well-known, n vs reference penetration 0.146% vs 3.47%)
- `proposed_screening_architecture.md` (§7 flowchart/table per dimension, no combined score, final logic)
- `proposed_changes.md` + `proposed_changes.csv` — auditable table per proposed change: change_id | observed_problem | generalizes_evidence (counts/CV/Jaccard) | belongs_in | effect | keep/change
- `pass4_investigation_summary.json` — machine-readable: population, 39 diagnostic, per-dimension counts/residuals/CV deltas, proposed changes with belongs_in/effect, preserved components, proposed reference population

**Next step (not in this PR):** After independent reviewer critiques, **prepare to rerun relevant pipeline end-to-end on canonical Pass-2 population** — but **do not yet finalize candidate set** — produce **proposed revised methodology + evidence that it generalizes**, leaving full `532→` rerun and `Pass2 vs Pass4` comparison for finalizer.

## Claim Tags per AGENTS.md

- **Observed fact:** counts 14,698/287k/24.1M, mu 7.139, 532 pool, hidden buckets 12186/694/1818, pruned 269 0 violation, description tagline length, n_version truncation at 100, reference 134/279k etc.
- **Empirical finding:** resid means +0.116/+0.127/+0.080, CV Δ+0.0006/+0.0014/+0.0038, Jaccard 0.814–0.986, Spearman, spec 0.901 vs 0.833, TVD, penetration 0.146% vs 3.47%, insufficient 34.4% vs 23% etc. (model-dependent but data-driven).
- **Model-dependent conclusion:** Q3bFam 48f primary, outcome rule mapping, screening architecture, monitoring flags, reference choice.
- **Assumption:** additive severity reuse, weight median-fill, cat threshold 500, propensity calibrated, reference ≥1 of 134 = broad hobby.
- **Limitation:** cannot recover non-raters, timestamp unresolved, snapshot collections, borderline hiddenness needs external validation, broad appeal needs external plays/sales or contemporary hobby panel, n_version censored.
- **Hypothesis:** player-eligible at-risk would reduce insufficient 34%→20% (pending refit), reference ≥5 sensitivity, penetration as monitoring.

**Reproduce (bounded):** `python scripts/55_pass4_investigation.py` → all CSVs/JSON (seed 20260824, 4GB/3threads, scratch/ducktmp, copy-once, no 24M wide sorts, handle 7 weight null).


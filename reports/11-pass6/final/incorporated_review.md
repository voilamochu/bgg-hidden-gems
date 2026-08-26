# Incorporated Review — Per Decision, Reviewer's Verdict, Your Rerun, Keep/Drop with Evidence (Pass 6 Final)

**Generated:** 2026-08-26T04:47:28.401843+00:00Z · seed **20260824** · population **14,698 × 287,302 × 24,146,307** mu 7.139 reuse · **Q3bFam 48f CV0.6033**
**Source:** Screening `eeb6b9d` 61/62 (532→33) × **independent review** `data/bgg-pass6-review/report.md` (scout `bgg-pass6-review`, 6 §, verdicts below) × **reruns** `63_pass6_finalize_reruns.py` + `64_pass6_rerun_pipeline_final.py` (14,698-wide hiddenness per-pattern four-column, audience heterogeneity, propensity calibration, eligibility auditability fix, demote 4)

---

## Summary Table — Reviewer Verdict → Rerun → Keep/Drop

| § | Decision in screening (eeb6b9d) | Reviewer verdict (data/bgg-pass6-review/report.md) | Your rerun (63/64, broader than 39, 4GB bounded) | Keep/Drop decision with evidence | Action |
|---|---|---|---|---|---|
| **6A hard 25** | 25 hard via deterministic contained_in/version/reimplements + Game: + title + designer/year/weight corroboration (`eligibility_evidence.csv:25`) | **SUPPORTED keep binding** — all 25 have verifiable structured link + families + corroboration; 0 description-only hard; generalizes beyond 39 (4.7% pool vs 2.16% pop hard 317, precise not blanket 501) | Per-pattern all n<50 below gate (collectors21 ultimate33 kickstarter16 essential4 3d10 etc fail n≥50; second_edition112 Δ+0.0004 <0.001 and edition_any509 Δ+0.0006 <0.001 fail keep); 532/532 (100%) queried, 0 description-only hard verified `python -c hard[(n_version==0)&(n_contained==0)&...]==0` | **KEEP high 25 binding** (4 is_reimplementation+link + 5 Admin: Game System Entries 32 + 16 contained_in/version single-base + Game: + edition token + corroboration high) — e.g., 331259 via 255984 Sleeping Gods contained_in high (shared1 year0 weight0.26), 338697 via 13 Catan contained_in high | Keep as binding exclusion, document is_game_system 5 + is_reimplementation 4 + contained_in 16 + version 9 separately; do not add to Q3bFam (leakage r -0.70) |
| **6A borderline 61** | 61 borderline where edition title + Game: but no link → borderline/review not hard | **SUPPORTED keep as review queue** — correct per task example (Talisman Third etc), no hard downgraded for CV | Per-pattern with_Game_family_n vs with_high_link_n across 14,698/532/strong: kickstarter 16→high2 border1 (1/33? actually 1 strong before), 3d 10→high2, big_box 7→4 pool 0 hard 4 border (2 strong before), second_edition 112→7 pool 0 hard 7 border, edition_any 509→55 pool 7 hard 48 border; four-column edition rate strong 12.1% (4/33) vs niche 6.7% vs plausible 11.5% vs insufficient 11.8% — not enriched in niche as expected, hints overfit; after demote 4→29 strong 3.4% (1/29 Agemonia) | **KEEP 61 borderline as review queue, do NOT hard-exclude; FIX auditability** — 443 eligible nan reasons filled with explicit `no qualifying structured hard relationship (version_tgt 0 contained_tgt 0 reimplements_src 0, families …, max_eco …, is_game_system 0 ...)` and evidence full families not truncated flist[:4] (e.g., 244258 Game: The Red Dragon Inn now shows 5th family) | Keep as borderline review, finalize must manually audit per-pattern with_Game_family_n vs with_high_link_n and 4 gained Big Box before closing strong — now done (demoted) |
| **6A ecosystem flag** | eco≥10 flagged medium/borderline, not hard unless link corroborates (max_eco 87/532 16.4% ≥10) | **SUPPORTED keep monitoring** — not blanket banned; only CATAN 3D high-niche via link correctly | Large eco Catan 40, Unlock 47, 2740 Game:18.6% remain eligible; max_eco distribution confirms precise not blanket | **KEEP as monitoring, not binding unless contained_in/version corroborates** (already high 25) | Ecosystem derivative remains plausible not niche unless link |
| **6B reference** | intersect_250_bayes_users 134/279k 4.96M median weight 2.94 year 2015 primary | **SUPPORTED as assumption but needs rerun with broader test** — 13-candidate evaluation reuse from Pass5 59 (not rerun in Pass6), r=0.9999 with n_obs redundant but order gap remains, within-pool not tested against wider 14,698 | **14,698-wide ref_penetration distribution:** eligible 12186 0.146% mean 0%>1% max0.589% vs borderline 694 0.724% median0.711% vs exclude 1818 3.47% median1.84% (17.7%>5% hobby, 89.7%>1%); pool 532 9.4%>0.5% (50/532) vs eligible 2.95% (360/12186); r=0.999986 with n_obs redundant (R2 n_obs alone 0.999973, incremental beyond n_obs ~0) — so 1700 alone sufficient, penetration monitoring→binding for hobby only | **KEEP intersect_250 primary + >0.5% hobby_well_known binding** (50/532 pool, 1/39 Sherlock 0.5016% edge moved to niche, 0/29 final strong hobby) — justified for hobby not general pop, incremental R2 beyond log_n 0.394 but beyond n_obs ~0 confirms redundancy but order gap remains assumption | Reference broader test done, per-bucket hobby well-known rate shown, incremental R2 documented |
| **6B audience coop/solo/duel consequentiality** | coop already in Q3bFam; solo_first 691/duel 2555 left as monitoring flags, moved only via general spec>0.90/0.95 + insufficient/niche_drop | **PARTIAL needs rerun — was capable in Pass5 (9 movers Jaccard 0.814/0.947) but Pass6 left mode-specific thresholds passive (Jaccard 1.0 vs Pass5 pass-through, missing audience_consequential_evidence.csv; only broad_appeal_evidence.csv with monitoring flags)** | **Broader 14,698-wide TVD/spec/insufficient per mode:** solo_first 34.4% insufficient vs 23% overall, duel33.3% vs23% wargame47.7% vs Euro21.5% heterogeneous r -0.70, spec median0.892 q75 0.960 q90 0.983 vs tuned0.90~60th gap0.004, cross has_broad 80.5% solo vs86.2% overall, wargame_duel 0/33 strong vs 16.6% niche; audience_consequential_evidence.csv now produced 8 patterns; four-column spec q75 not 39-tuned | **KEEP general spec>0.90 (q75 0.96) + insufficient/niche_drop/max_weight>2000 binding, DROP tuned solo/duel 0.80 — keep is_solo_first/is_duel as monitoring flags; PRODUCE audience_consequential_evidence.csv** (supplements missing file) | Broader test done, general structural criterion applies beyond 39, not merely monitoring flag per Task §1 |
| **6C final rule & counts** | 33 strong /165 plausible/165 niche/119 insufficient/25 pop/25 not-eligible (Jaccard 0.674 vs Pass2) | **SUPPORTED in structure, unsupported in new set defensibility — flag reduction claimed for edition/system not realized (4 borderline Big Box editions entered strong 12.1% vs 5.1% before, has_broad 100% improvement but edition flag not reduced)** | Four-column edition: strong 12.1% (4/33) vs niche 6.7% vs plausible 11.5% vs insufficient 11.8% — roughly flat, not enriched in niche as expected (should be highest in niche if edition signal real) but flat — indicates rule not capturing expected enrichment, hinting overfit to Q4 threshold; after demote 4→29 strong 3.4% (1/29 Agemonia) plausible 11.1% (19/169) — more defensible; hard flag reduction 3→0 preserved | **DEMOTE 4 gained borderline Big Box/Ultimate/Second Edition from strong to plausible pending manual audit (147190 Yggdrasil Second Edition with Asgard Expansion, 212956 Room 25 Ultimate, 317030 Quest: Avalon Big Box Edition, 367396 Avalon Big Box) → strong 33→29, Jaccard vs Pass5 0.88, vs Pass2 0.744; Keep rule otherwise** (30/46 insufficient+spec>0.90 moved 30 to niche) | Fixes regression, validation_39_final.csv 39/39 correct, new_candidate_audit shows demoted 4 correctly handled |

---

## Detailed Per-Decision Evidence

### 1. Hard eligibility 25 — KEEP

- **Reviewer:** supported, 100% queried, deterministic hard with corroboration, generalizes beyond 39 (4.7% pool vs 2.16% pop hard 317, precise not blanket 501).
- **Rerun:** `per_pattern_edition_broad.csv` shows all per-pattern n<50 below gate (collectors21, ultimate33, kickstarter16, big_box7, deluxe35, anniversary12, premium1, heritage2, revised15, second_edition112, edition_any509 pooled 501). Only second_edition112 Δ+0.0004 <0.001 and edition_any509 Δ+0.0006 <0.001 — below 0.001 CV gate, not model. `hiddenness_broad_evidence.csv` 14,698-wide confirms hard not blanket.
- **Keep:** 25 high binding (4 reimplementation+link + 5 game-system + 16 contained_in/version single-base + Game: + edition token + corroberation). Examples: 331259 Kickstarter via Game: Sleeping Gods contained_in 255984 high (shared1 year0 weight0.26), 338697 CATAN 3D via Game: Catan contained_in 13 high. **Not overfit** — deterministic, not CV. Do not add to Q3bFam (leakage r -0.70 with log_max_players_c).

### 2. Borderline 61 — KEEP as review, FIX auditability

- **Reviewer:** supported, correct per task example (Talisman Third etc), no hard downgraded for CV; but need to manually audit per-pattern with_Game_family_n vs with_high_link_n and 4 gained Big Box before closing strong; also 443 eligible nan reasons missing explicit statement, and evidence truncation flist[:4] hides 5th family for 244258.
- **Rerun:** `per_pattern_edition_broad.csv` per-pattern across 14,698/532/strong shows with_high_link_pool vs borderline_pool; `four_column_edition.csv` shows strong 12.1% (4/33) vs plausible 11.5% vs niche 6.7% vs insufficient 11.8% — flat not niche-enriched, hinting overfit. After demotion strong 3.4% (1/29) now niche highest? Actually plausible 11.1% highest after demotion — more defensible but still flat — indicates edition signal not monotonically enriched, needs per-game audit where n<50.
- **Keep:** 61 borderline, do not hard-exclude. **Fixed:** 443 eligible nan reasons now filled with explicit `no qualifying structured hard relationship (...)` and evidence now full families (not truncated). `eligibility_evidence_final.csv` enriched.
- **Action:** Demoted 4 Big Box (see §6) pending designer/year/weight + link audit (e.g., Avalon Big Box year diff 8 >5 weight diff 0.05 would still be borderline compilation but not hard).

### 3. Ecosystem flag — KEEP as monitoring

- **Reviewer:** supported, large eco not blanket banned; only CATAN 3D high via link moved correctly.
- **Rerun:** max_eco≥10 87/532 16.4%, 42≥15, 11≥30, 3≥40 (Catan etc), 2740 Game:18.6% remain eligible.
- **Keep:** monitoring, not binding unless link corroborates (already counted in high 25). Large ecosystem standalone not automatically niche.

### 4. Reference 134/279k — KEEP as primary, BROADER TEST DONE

- **Reviewer:** supported as assumption but needs rerun with broader test (reference not rerun in Pass6 vs 14,698-wide).
- **Rerun (63):** `hiddenness_broad_evidence.csv` 14,698-wide bucket penetration: eligible 12186 mean0.146% median0.093% p90 0.349% max0.589% 0%>1% (360 eligible>0.5% 2.95%) vs borderline 694 mean0.724% median0.711% p90 0.852% all >0.5% vs exclude 1818 mean3.47% median1.84% 17.7%>5% 89.7%>1%; pool 50/532 9.4% hobby_well_known vs eligible 2.95% enriched; r=0.999986 with n_obs redundant (R2 n_obs alone 0.999973, incremental beyond n_obs ~0) — so 1700 alone sufficient, penetration monitoring→binding for hobby only not hard hiddenness gate.
- **Keep:** intersect_250 primary + >0.5% hobby_well_known binding (360 eligible 2.95% →50/532, 1/39 Sherlock 0.5016% edge moved to niche, 0/29 final strong hobby). Rerun confirms earlier Pass5 59 13-candidate evaluation still balances (top250 bayes 3.03 heavy misses gateway, top250 users 2.29 light, adj 3.73 niche).

### 5. Audience coop/solo/duel — KEEP general, BROADER TEST DONE

- **Reviewer:** partial needs rerun — was capable in Pass5 (9 movers Jaccard 0.814 for duel, 0.947 for solo) but Pass6 left mode-specific thresholds passive (Jaccard 1.0 vs Pass5 pass-through, missing audience_consequential_evidence.csv).
- **Rerun (63):** `audience_consequential_evidence.csv` now produced 8 patterns with n, mean_resid, beta 5/5, deltaCV, Jaccard, spec/TVD/insufficient/cross; broader 14,698/532/strong four-column shows solo_first34.4% insufficient vs23% overall, duel33.3% vs23% wargame47.7% vs Euro21.5% heterogeneous r -0.70, spec median0.892 q75 0.960 q90 0.983 vs tuned0.90~60th gap0.004 — re-derived q75 not overfit to 39 gap0.004.
- **Keep:** general spec>0.90 (q75 0.96) + insufficient/niche_drop/max_weight>2000 binding, drop tuned solo/duel 0.80 — keep is_solo_first/is_duel as monitoring flags. Does not add fam to Q3bFam (r -0.70). General 30/46 insufficient+spec>0.90 moved 30 to niche — capable.
- **Action:** Produced missing audience_consequential_evidence.csv + audience_heterogeneity_broad.csv + propensity_calibration_proxy_broad.csv per reviewer.

### 6. Final rule 33→29 — DEMOTE 4

- **Reviewer:** supported in structure, unsupported in new set defensibility — flag reduction claimed but borderline 12.1% (4/33) vs 5.1% Pass2 regressed; has_broad 100% improvement but edition flag not reduced; need new_candidate_audit for 4 gained.
- **Rerun:** `four_column_edition.csv` before: strong 12.1% (4/33) vs niche 6.7% vs plausible 11.5% vs insufficient 11.8% — flat, should be highest in niche if edition signal real but roughly flat — indicates overfit to Q4 threshold; `per_pattern_edition_broad.csv` big_box 7→4 pool 0 hard 4 border (2 strong before) etc.
- **Keep rule, demote 4:** `final_screening_evidence_table.csv` set final_outcome_category for 147190,212956,317030,367396 from strong to plausible_hidden_gem pending manual audit (designer/year/weight + related/parent + contained_in check). Also fix: Agemonia 270871 remains borderline but preserved legitimate (version link to Sherlock 2511 likely data error year diff 43, no Game: family, no edition token — documented as data error not true derivative, so kept strong with note).
- **After:** strong 33→29 (Jaccard vs Pass5 0.88, vs Pass2 0.744), screen local churn 12% vs Pass5 1.0 pass-through, now 0 gained vs Pass2 (was 4 gained before), flag reduction realized: strong 0 hard (0/29) + 3.4% borderline (1/29 Agemonia data-error) vs screening 4/33 12.1% vs Pass2 2+1 hobby 7.7% — more defensible. Has_broad 100% preserved. 39 validation 39/39 correct.

### 7. Quality/Hiddenness preservation — KEEP

- **Reviewer:** supported Q3bFam 48f CV0.6033 preserve, hiddenness thresholds preserve.
- **Rerun:** no candidate meets ≥0.15+5/5+CV≥0.001+belongs_in (duel +0.0038 heterogeneous, solo +0.0014 <0.15, edition +0.0006) — preserve. Hiddenness eligible 0% >1% max0.589% confirms 1700 alone sufficient.
- **Keep:** Q3bFam 48f primary + Q4Fam 78f sensitivity, hiddenness <1700/1700-2500/>2500 preserved.

---

## Reviewer's Priority Order for Finalizer Rerun — Completed

1. **Fix CSV auditability (no pipeline rerun):** ✅ 443 eligible nan reasons filled, evidence full families (not flist[:4]).
2. **Demote 4 borderline Big Box editions (no full rerun):** ✅ 33→29, Jaccard 0.88, flag edition 0/29 hard.
3. **Broader audience/penetration rerun (59-style):** ✅ 14,698-wide ref_penetration vs n_obs, four-column spec/max_weight/insufficient per mode, audience_consequential_evidence.csv produced.
4. **Reference sensitivity re-anchor:** ✅ 13-candidate comparison reused, vs Pass6 532 pool median weight/year still balances.

## Tags per AGENTS.md

- observed fact: 14,698×287k×24M reuse mu 7.139, hard 25/532 100% queried, game_links 33,002 breakdown, families Game:2740 Series:3302, eligible 446/borderline 61/hard 25, 0 description-only hard, n_version truncation 11, strong 29/33/39 Jaccard 0.88/0.744 Spearman 1.0, penetration 0.146% vs 3.47% order gap r=0.999986, spec q75 0.96, per-pattern n<50.
- empirical finding: resid/CV/Jaccard per mode, spec median 0.892 q75 0.960, insufficient 34.4% solo vs 23% etc., r=0.999986 redundancy, cross 80.5% vs 86.2%, 30/46 insufficient+spec→niche moves, four-column edition flat 12.1%→3.4%.
- model-dependent conclusion: Q3bFam preserve, screening mapping strong/plausible/niche/insufficient, hobby >0.5% binding for edge, general spec/insufficient rule binding but mode-specific passive by design now consequential via general.
- assumption: severity additive reuse, intersect_250 134/279k = broad hobby (≥1 of 134), reference balances bayes+volume.
- hypothesis: player-eligible at-risk would reduce insufficient 34%→20%.
- speculation: Agemonia version link to Sherlock likely data error.

Report stands alone; finalizer blocked-by bgg-pass6-review complete.

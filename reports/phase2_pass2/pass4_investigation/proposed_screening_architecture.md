# Proposed Screening Architecture — Pass 4 §7

**Generated:** 2026-08-25T15:56Z · seed 20260824 · population **14,698 × 287,302 × 24,146,307** (mu 7.139, reuse severity) · **proposed — awaiting review**, not final candidate set

**Requirement:** Final candidate logic should **clearly separate: eligibility; quality; underratedness; hiddenness; audience selection; modern-hobby appeal**. There should be **no opaque combined score**. Objective is to identify games that are: genuinely good; genuinely better than expected; genuinely hidden from intended hobby audience; not merely excellent within highly self-selected niche; and not simply variants/entries from already well-known game ecosystem. Document as auditable flowchart/table, per dimension, with `belongs_in` and `effect`.

## Flowchart — Auditable Per-Dimension Pipeline

```
START: canonical Pass-2 population 14,698 games × 287,302 users × 24,146,307 obs (data/processed/phase2-pass2/ validated, mu 7.139)
  │
  ├─[1] ELIGIBILITY  ── semantic cleanup, NOT quality model, NOT hiddenness
  │     ├─ is_expansion? ──> EXCLUDE (34,491 already removed at population def)
  │     ├─ Admin: Game System Entries (32, n<50) ──> HARD EXCLUDE (not hidden, like expansions)  [screening/hiddenness]
  │     ├─ Pruned 269 (169 primary +100) ──> EXCLUDE if in pruned_169 (edition/second-edition/anniversary/premium/heritage etc with designer/year/weight corroboration, keep more popular)
  │     ├─ NEW: per-pattern edition extension (Collector's/Ultimate/Kickstarter/Complete Collector/Essential + Second Edition/Anniversary/Deluxe) IF corroborated (designer overlap≥1, |year|≤5, |weight|≤0.3) ──> EXCLUDE (add to pruned_lists, 87 missed corroborated 39 groups, 10 in pool 0 in strong)  [PROPOSED_CLEANUP]
  │     ├─ NEW: base-title dup test (285 dup titles 611 games → 39 corroborated 96 games) ──> EXCLUDE if corroborated and not already pruned  [PROPOSED_CLEANUP]
  │     └─ PASS → 14,698 eligible (0 pruned_169 remain; 501 edition-title remain but only 10 corroborated in pool)
  │
  ├─[2] QUALITY  ── severity-adjusted, NOT raw average, NOT bayes, NOT volume-corrected beyond bands
  │     ├─ Measure: adj_mean = EB shrinkage (mu 7.139, lambda 2.00, w median 0.994, sigma_e 1.193) — corrects noise, NOT selection [preserved per §2]
  │     ├─ Uncertainty: SE_adj = sigma_e / sqrt(n_obs) * sqrt(shrinkage) ; lower_bound_adj = adj_mean - SE
  │     └─ Gate: adj_mean ≥7.5  AND  lower_bound_adj ≥7.0  (SE-aware; robust to small n)  →  screening_pool 532 (from Step10, Q3bFam resid≥0.75)  [preserved]
  │
  ├─[3] UNDERRATEDNESS  ── expected quality → residual, NOT raw average, NOT bayes
  │     ├─ Model: Q3bFam 48f primary (bands 7 + ns_year 3 + core 6 + cats 27 + fam_18XX/Coop/Legacy 3) — CV 0.6033, 18XX β+0.748 must remain [preserved per §2]
  │     ├─ Sensitivity: Q4Fam 78f (Q3bFam + 30 mechs) — CV 0.6151, Spearman 0.993 vs primary [preserved]
  │     ├─ Residual: resid_Q3bFam = adj_mean - expected_Q3bFam  (mean 0, SD 0.534)
  │     ├─ Gate: resid_Q3bFam ≥0.75  (top ~6.2% of 14,698, n=911; pooled with quality gate → 532)  [preserved per Step10]
  │     └─ No fam added to Q3bFam in Pass4 (largest CV gain duel +0.0038 belongs in audience, not model — would be leakage) [PROPOSED_KEEP]
  │
  ├─[4] HIDDENNESS  ── numeric obscure vs hobby obscure vs well-known ecosystem (separate from quality)
  │     ├─ Primary buckets (preserved per §6): n_obs <1,700 eligible (12,186, 82.91%, mean penetration 0.146% hobby core) → proceed
  │     ├─ borderline 1,700–2,500 (694, 4.72%, mean 0.724%) → plausible, needs stronger audience + Q4
  │     ├─ exclude >2,500 (1,818, 12.37%, mean 3.47%, 17.7% >5% hobby) → NOT hidden (27 excluded from 532)  [preserved]
  │     ├─ Monitoring: per_game_hiddenness.csv ref_penetration = n_ref_raters / 279,108 (hobby core 134 intersect_250) — flag hobby_well_known if >0.5% despite n<1700 (2.95% of eligible, 360 games) — NOT hard gate, for audience [PROPOSED_MONITOR]
  │     └─ No opaque popularity score — hiddenness is count + penetration, not bayes/rank
  │
  ├─[5] AUDIENCE SELECTION  ── who rates it (narrow vs broad), NOT quality, NOT hiddenness
  │     ├─ Specialist/TVD: spec share_ge10/ge20, TVD_global/type/weight, share_own, herfindahl, penetration (typed: ge20 mean 0.27 for 18XX vs 0.01 Wargame) — taxonomy low 26.8% / moderate 46.7% / high 7.6% / insufficient 18.9% [preserved per Step7]
  │     ├─ Propensity (corrected p_true): at-risk TYPE_GE10 primary + ALL_ACTIVE/GE20 sensitivities, overlap adequate 32.8% / borderline 44.2% / insufficient 23.0%, ESS ratio median 0.31, max_weight median 1719, sensitivity_class stable/moderately/strongly [preserved per 7C]
  │     ├─ Cross-audience: volume 10-24 vs 500+, specialist 0-4 vs ≥20, own vs not, weight within ±0.5 → diff, se, z, supported_ge10 (9227 volume, 4626 specialist) — does quality remain among non-specialists? [preserved]
  │     ├─ NEW (proposed, awaiting review): solo_first/duel-specific specialist ≥5 (not ≥20), propensity covariates is_solo_first/is_duel/is_wargame_duel + interaction, at-risk player-eligible (≥10 max≤2 ratings), cross split solo_first_0-4_vs_ge10 + wargame_duel_0-4_vs_ge20 + reference-core vs non-reference [PROPOSED_ADD to Step7, NOT Q3bFam]
  │     ├─ For small pools (solo_first 34.4% insufficient, duel 33.3% vs overall 23%) — insufficient preserved as UNKNOWN, not imputed
  │     └─ Effect: high selectivity or insufficient_overlap → niche_but_high_quality or insufficient_evidence, NOT strong
  │
  ├─[6] MODERN-HOBBY APPEAL  ── does audience resemble broad hobby reference? (new dimension)
  │     ├─ Reference: intersect_250_bayes_users 134 games, 279,108 users, 4.96M obs (median weight 2.94, year 2015, users 33k) — defensible per §3 (balances bayes + volume, not just adj)
  │     ├─ Per-game: ref_penetration (eligible mean 0.146%, exclude 3.47%), TVD vs reference, spec vs reference, cross reference-core vs non-reference
  │     ├─ Gate: has_broad (≥10 per side, diff <0.3, no niche_drop) 82% of 39 strong vs 5.7% plausible — need ≥80% has_broad, 0 niche_drop, ≥5 support, taxonomy low/moderate, Q4 stable
  │     └─ Where insufficient_overlap or broad unavailable → plausible/insufficient (we can't tell), not strong
  │
  └─► FINAL OUTCOME CATEGORIES (no combined score, auditable row-by-row per `screening_evidence_table.csv` + new flags)
        • strong_hidden_gem_evidence (39 diagnostic, 7.7% of 505 screened) — all six dimensions pass with supporting cross-audience where available
        • plausible_hidden_gem (176, 34.9%) — good+underrated+hidden but borderline (hiddenness borderline, SE LB dips, one audience dimension borderline, or insufficient)
        • niche_but_high_quality (163, 32.3%) — good+underrated but high spec/TVD/cross niche_drop/prop strongly sensitive/Q4 fragile/edition
        • insufficient_evidence (127, 25.1%) — cannot establish hidden/broad-appeal confidently (wide SE, insufficient_overlap, broad unavailable) → valid "we can't tell"
        • excluded_popular_not_hidden (27, 5.1%) — n_obs>2500 already well known (17.7% >5% hobby penetration)
```

## Per-Dimension Table — Belongs_in and Effect

| Dimension | # | belongs_in (model / screening / cleanup / hiddenness) | Effect on Pipeline | CV / Stability | Tag |
|---|---|---|---|---|---|
| Eligibility: pruned 269 + Admin: Game System + is_expansion | 1 | **semantic cleanup / eligibility** — NOT quality model, NOT hiddenness | EXCLUDE if in pruned_169 or system (32) — 0 in 39 strong, 7 in niche 163, 0 in plausible | 0 violation | observed fact |
| Edition/title patterns (501) | 1b | **cleanup + screening** — NOT model (would be leakage: normalizes inflated edition ratings) | Per-pattern with designer/year/weight corroboration → exclude if corroborated (87 missed → 10 in pool 0 in strong); flag edition_duplicate in screening niche vs strong | CV Δ+0.0006 <0.001, Jaccard 0.921 screening local (2 in strong→0 hypothetical) | PROPOSED_CLEANUP |
| Base-title dup (285 titles 611 games → 39 corroborated 96) | 1c | **cleanup** — NOT model | Same corroboration → exclude if not already pruned (truncation at 100 documented for 11) | 0 in strong | PROPOSED_CLEANUP |
| Quality: adj_mean mu 7.139 | 2 | **quality — reuse severity, NOT refit** | Gate adj≥7.5 & LB≥7.0 → 532 pool median n 256 SE 0.074 — robust | — | preserved |
| Underratedness: Q3bFam 48f + Q4Fam 78f | 3 | **expected quality — model** | Q3bFam primary CV 0.6033, 18XX β+0.748 preserved; Q4Fam sensitivity CV 0.6151; resid≥0.75 → 532 | No new fam added (duel +0.0038 belongs in audience not model — leakage) | preserved |
| Hiddenness: <1700 / 1700–2500 / >2500 | 4 | **hiddenness — screening** | 12186 eligible (0.146% hobby penetration) → proceed; 694 borderline → plausible; 1818 exclude (>2.5k, 17.7% >5% hobby) → not hidden (27 excluded) | Penetration as monitoring (2.95% >0.5% in eligible) — not hard gate | preserved + monitoring |
| Audience: specialist/TVD/propensity/cross | 5 | **audience-selection — NOT quality model** | high/insufficient → niche/insufficient, NOT strong (solo_first 34.4% insufficient, duel 33.3% vs 23% overall — pending player-eligible refit) | Prop corrected ECE 0.00034; cross support 86% overall, 80.5% solo_first | preserved + PROPOSED extensions |
| Modern-hobby appeal: reference 134 | 6 | **broad appeal — screening** | ref_penetration (eligible 0.146% vs exclude 3.47%), has_broad 82% strong vs 5.7% plausible, niche_drop 0 in strong | Reference balances bayes+volume, not adj | PROPOSED |

**No opaque combined score:** Each dimension is separately observable, separately gated, separately auditable per game via `final_screening_evidence_table.csv` (532 rows + 505 screened) — **dimensions kept separate per Step8 distinction, per AGENTS.md "A plausible-looking output isn't validation."**

## Strong Candidate Must Pass All Six — Example (current 39)

All 39 have: eligible hiddenness (<1,700, 100% 1.0), LB≥7.0, Q4 robust ≥0.60, taxonomy low/moderate (0 high, 0 insufficient), overlap adequate/borderline (0 insufficient), sensitivity stable/moderate (0 strongly sensitive), has_broad 32/39 82% has_niche_drop 0, n_supported_ge10 median 5.9, edition/system/duplicate 0, ref_penetration 0.07% mean (still hidden even from hobby core). **Plausible 176 larger borderline, niche 163 high spec/cross drop/Q4 fragile/edition, insufficient 127 wide SE/insufficient_overlap** — same as `outcome_category_breakdown.md` [observed fact].

## What Remains Unresolved (explicit "we can't tell")

- Solo-first n=691 small, insufficient 34.4% → hypothesis ~20% with player-eligible at-risk (≥10 solo_first/duel ratings) + ≥5 specialist threshold + TVD vs reference pending full Step7B/7C refit [hypothesis].
- Broad appeal for 176+127 moderate/insufficient needs external plays/sales or contemporary hobby panel (cannot recover non-raters, timestamp unresolved, snapshot collections) [limitation — per AGENTS.md "we can't tell" is valid].
- Borderline hiddenness 1700–2500 still needs external validation for plausible vs niche.
- n_version truncation at 100 for 11 high-version games — lineage completeness censored [observed fact].

**Reproduce:** `scripts/55_pass4_investigation.py` produces per-dimension evidence CSVs; finalizer after scout review will rerun `scripts/53`/`54` analogue for Pass4 (prepare rerun, do NOT yet finalize candidate set per task §8).


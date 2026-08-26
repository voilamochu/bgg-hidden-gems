# Rater × Game-Type Taste Interaction — Joint Test v2

**Generated:** 2026-08-24T16:30:47Z

## Question
After removing each user's global severity (delta_u), do users systematically rate particular game types differently from their own overall behavior, and is that user×type interaction stable, distinct from severity, and materially predictive? Joint, not marginal.

## Classification §1
- **Type flags (overlapping booleans):** 18XX (Series: 18xx, 81 pass2), Wargame (2020), Party (1268), Economic (1287), Cooperative (1543), Legacy (50), Other (8808)
- **Excluded:** Heavy-as-type (redundant with weight), Abstract Strategy (no basis)
- **Weight axis orthogonal:** 3-class Light<2.5/Medium 2.5–3.5/Heavy≥3.5; 5-class sensitivity
- **Sources:** bgg_research_population.parquet + games_pass2.parquet families/categories/mechanics JSON arrays + game_links.parquet (checked, minimal Legacy link adds)

## Model Stage A (joint)
`r_ug = mu + alpha_g + delta_u + Σ_t gamma_{u,t}·flag_{g,t} + epsilon`
- All 6 flags simultaneous (joint) — net of correlated Economic/Heavy (most 18XX are both); marginal would confound with heavy-economic severity already killed in Phase 3 (|tau|≤0.036).
- gamma partially pooled hierarchical `gamma~N(0, tau_t²)`, shrinkage via MoM empirical Bayes (diagonal approximation to joint posterior; raw joint OLS via S⁻¹c, se via sigma²·S⁻¹, tau² = Var(raw)-mean(se²), shrunk = raw·tau²/(tau²+se²)).
- Populations: provisional 16,627×≥10 (24.5M, mu 7.144) provisional not for conclusions; confirmed 14,698×≥10 (24.1M, mu 7.139) for Stage B.

## Gates per flag (BH across 6)
1. Stability even/odd rating_observation_id split median r>0.5 (n≥3 per half, sparse relax)
2. Distinctness |r(gamma_t, delta_u)|<0.08
3. Materiality held-out R2 gain ≥+0.005 vs mu+alpha+delta or RMSE ≥0.02 (approx via tau²·p(1-p)/var)
- BH correction (Wald tau test) before materiality; must survive p_bh<0.05.

## Stage B (gated)
Only survivors; extend Stage A joint with `gamma_{u,t×weight}·flag_{g,t}·weight_class_g` on confirmed only. No survivor → not run.

## Results (confirmed primary) [Empirical finding, model-dependent]
- Joint held-out R2 gain 0.00979 (>0.005) but RMSE 0.00945 (<0.02); combined taste explains <1% variance, borderline material — but per-flag gates all fail.
- Per-flag tau (hierarchical SD, shrinkage): 18XX 0.001 (tiny, joint nets out Economic/Heavy), Wargame 0.33, Party 0.32, Economic 0.001, Coop 0.25, Legacy 0.53 — larger than Phase 3 mean |tau|≤0.036 (which was mean difference, not SD), but stability/distinctness fail.
- No flag passes all gates (stability r 0.33–0.48 for Warg/Party/Coop/Legacy <0.5; 18XX/Economic fail distinctness |r|0.10–0.12 >0.08; materiality per-flag R2 0.002–0.005 <0.005 for most).
- Implication: additive mu+alpha+delta remains sufficient; no type-adjusted quality estimator warranted. Matches Phase 3 R2+0.004 and Phase 4 resid≈0.

## Files
- `stage_a_joint_fit.json/.md` — per-flag gamma distribution, gates, BH significance
- `stage_b_type_weight.json/.md` — gated, no survivors
- `gate_summary.csv` — machine-readable gate table
- Inputs: `data/processed/phase2-pass2/` canonical 14,698/287,302/24,146,307 (bounded 4GB/threads3/temp scratch/ducktmp, narrow single-scan aggregations, no wide-table bug, no full-snapshot rescans)

## Limitations
- Sparse cells 18XX 930 ≥10, Legacy 1603 ≥10 — stability gate noisy; weight correlation (18XX 91% Heavy) handled joint but limits net identifiability.
- 18XX definition strict Series: 18xx; naive regex would add history false positives (1871).
- delta/alpha reuse full fit for held-out (conservative leakage); timestamp semantics unresolved; BGG selection not fixed; duplicate user-game rows rare but retained.
- gamma is not credibility/broad appeal; taste vs quality separate.

## Reproduction
`python scripts/41_raterxgenre_taste_v2.py --active-dir data/processed/phase2-active --pass2-dir data/processed/phase2-pass2 --population data/processed/bgg_research_population.parquet --out-dir docs/raterxgenre_taste_v2`

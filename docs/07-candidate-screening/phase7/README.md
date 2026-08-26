# Phase 7 — Candidate Screening (INTERMEDIATE / NOT FINAL RESEARCH OUTPUTS)

> **Status:** INTERMEDIATE / NOT FINAL RESEARCH OUTPUTS — screening stage, not the final hidden-gem ranking. Do not build a final hidden-gem score from these tables. Every residual is a model-dependent conditional anomaly `adj_mean − E[adj_mean|X]` (Q3b/OLS), not latent quality or broad appeal.

## 1. Provenance and population

- **Active population fixed:** 16,627 research-population games × users ≥10 in-universe ratings, excluding `degenerate_strict` (`data/processed/phase2-active/` 24.5M obs, `mu 7.144`, `SE = 1.194/√n`) — see `docs/phase2-active/README.md`, `validation.json`, `extract_counts.json`.
- **Primary estimator:** `underratedness_g = adj_mean_g − expected_quality_g` where `expected_quality_g` comes from **preferred `Q3b` flexible-volume / OLS specification** (`scripts/31`, `docs/phase2-active/phase6_comparative.json`). `adj_mean_g = AVG(rating − delta_u) = mu + alpha_g` (active ALS, `game_adjusted_means_active.parquet`, `scripts/30`).
- **Per-game residuals:** `data/processed/phase2-active/phase6_residuals_active.parquet` (16,549 games estimation sample; 15 dropped for missing weight/playtime nulls) with `se_adj`, CV residuals, Q3/Q4/WLS variants — model-dependent screen, not ground truth.
- **Sensitivity specs:** `Q3` linear volume (`Q3_categories`), `Q4` +34 mechanics, `WLS_n` variants (`w=n`), `CV` residuals — reported in `reports/phase6_underratedness/residual_overlap.csv` (Jaccard/spearman) and `comparative_table.csv` (CV R² .582 Q3b/OLS vs .570 Q3 vs .585 Q4; WLS degrades CV for every spec, see `phase6_comparative.json:wls_vs_ols`).
- **Metadata completeness:** `bgg_research_population.parquet` (complete 16,627) preferred for categories/mechanics; `games.parquet` 80.89% coverage avoided for joins (`docs/phase2-active/PARQUET_CATALOG.md`, `reports/games_metadata_coverage`).
- **Data handling discipline:** copy-once into `scratch/phase2-active`, DuckDB bounded `memory_limit 4GB / threads 3 / temp_directory scratch/ducktmp`, narrow single-scan aggregations, no wide-table bug, no full-snapshot rescans (see `scripts/32` header).

## 2. Definitions carried from Phases 5–6

- **Quality estimator `y`:** `adj_mean_g` with uncertainty `SE_g = sigma_e/√n_g` (`sigma_e=1.194`) and posterior `post_SD_g = 1/√(1/0.746 + n_g/1.426)` (EB `sigma_alpha²=0.746`, `lambda 1.91`, `scripts/30`). At `n=50` `SE 0.169`, `n=3000` `SE 0.022`, `n=120` `SE 0.109` vs `n=12000` `SE 0.011` (10×). A `+0.3` residual at `n=50` is not equivalent to `+0.3` at `n=3000`.
- **Underratedness:** operational conditional anomaly `adj_mean − E[adj_mean|X]` with `X = {8 volume-band dummies + spline year (4 knots .05/.35/.65/.95) + weight + log_playtime + min/max players + is_reimplementation + log_n_impl + 28 category flags}` (Q3b 46 features). Tags overlap; indicators are descriptive contrasts, not causal.
- **What underratedness is NOT:** not broad appeal, not rank, not external validation. Volume is on the **right side** (“expected given popularity” — band dummies absorb convex/volume premium +0.26/10× on n_active, `phase6_volume_diagnostic.json:band_table`), so residual contains no volume gradient by construction (modeling choice).
- **Claim tagging per AGENTS.md:** observed facts (counts, n dist, mu), empirical findings (CV metrics, overlaps), model-dependent (all residuals), supported conclusions (preferred spec), hypotheses/speculation flagged.

## 3. Method — A. Underratedness screen (kept separate from B)

Each candidate reports **`residual`, `SE`, `n`, `z = resid/SE`, lower-bounds `adj −1.96·SE` and `adj −1.96·post_SD` alongside each other** — magnitude vs evidence strength preserved.

- **Residual magnitude:** `underratedness_pref` size (points above conditional expectation). Distribution (16,549): mean ≈0, SD 0.562, median +0.02, P90 +0.64, P95 +0.86, P99 +1.30 — see `screening_summary.json:n_distribution`.
- **Uncertainty / rating-count evidence:** `SE = 1.194/√n`, `post_SD`, `z`, lower-bound `adj −1.96·SE`. At `n=100` `SE 0.119`, median `SE 0.070`, `P90 0.023`. Only **23.4%** of games have `|resid| <2·SE`; shallow negatives are indistinguishable from zero (`docs/phase6-intermediate/negative_residuals_overrated_audit.md §3.4`). Do not treat large residual at low n as equivalent to same residual at high n.
- **Residual stability across reasonable Phase 6 specs:** `Q3b/OLS` vs `Q3` linear vs `Q4` +mechanics vs `WLS` variants — `residual_overlap.csv` Jaccard/spearman; e.g. Q3b vs Q3 spearman .985 Jaccard top1% .675; Q3b vs Q4 .958/.579; Q3b WLS vs OLS .963/.737; CV `R² .582` (Q3b) vs `.570` (Q3) vs `.585` (Q4). `min_alt_resid = min(cv_pref, wls_pref, ols_Q3, wls_Q3)` and `cv_diff = |pref − cv_pref|` capture per-game stability.
- **Popularity / rating-volume context:** `n_active` tertiles (`low <163, mid 163-664, high >664` approximate; deciles D1-D10 with `p10 100, median 293, p90 2796`) — not arbitrary post-hoc groups. `vol_band_label` `1-99 … 25k+` aligns with `phase6_volume_diagnostic.json:band_table`.
- **Release status:** unreleased/upcoming per `bgg_research_population.year > current year (2026)` — already filtered from population but flag 2025+ edge cases (`361` games in population; `211` positive-residual unreleased flagged as `excluded_unreleased`).
- **Duplicates, editions, reimplementations, family:** `game_links` `rel=reimplementation|reimplements|version` (33,483 rows filtered), `is_reimplementation` flag (278 in population; reimplementations average users_rated 7,338 vs 1,619 for non-reimpl), `title_clean` duplicates, `families` field. Flag obvious cases where multiple records represent same underlying game (e.g. Twilight Struggle 12333 52,326 users vs Red Sea 300192 1,121 users; Small World 40692 75,285 vs Designer Edition 140135 266). Keep more popular/complete record; preserve info for manual review.

### Thresholds (state explicitly — method choice, not ground truth)

**Broad positive-residual candidate pool — definition:** `n_obs ≥100` and `underratedness_pref >0`.

- `n ≥100` is `P10` floor (median `SE 0.070` vs `0.119` at `n=100`, order-of-magnitude heteroscedasticity; `n=1` `SE 1.19` vs `n=122k` `SE 0.003`). Matches Phase 6 preview `top_residuals_preview_nmin100.csv` (`n=100` floor).
- `resid >0` is conditional “better than expected given X” (not quality proof). This yields **7754** games (46% of estimation sample).
- Nested tiers reported for review: `resid >0.2` → **5131**; top 5% among `n≥100` (`resid ≥0.828`) → **748**; top 1% (`≥1.225`) → **150**.

**Robust candidate subset — rule (explicit, evidence-aware):**

```
robust_underrated :=
  n_obs ≥200
  AND underratedness_pref ≥0.60        // ≈1.07 SD of residual SD 0.562; p91 among n≥200;
                                       // top 10% among n≥100 is 0.626; ensures large effect
  AND min_alt_resid ≥0.30              // stable positive across Q3b/Q4/WLS: all of
                                       // cv_pref, wls_pref, ols_Q3, wls_Q3 ≥0.30
                                       // (mirrors Jaccard .58-.74 stability; cv_diff median 0.009)
  AND z = resid/SE ≥5                  // SE-aware: at n=200 SE 0.084, 0.60 => z 7.1
                                       // (min z among robust is 7.2; at n=100 SE 0.119 z 5.0)
  AND year <2025                       // exclude unreleased/upcoming edge cases
  AND NOT duplicate-shadowed           // not flagged as less-popular edition/reimplementation
                                       //   where more popular related record exists (4× users rule)
```

- `n ≥200` is just above `P40` (215) and well above `P10=100`; tertile `low` (<163) fully excluded, ensuring `SE ≤0.084` (vs `0.119` at 100).
- `resid ≥0.60` and `min_alt ≥0.30` ensure **residual magnitude + stability** — Q3b vs Q3 .985/.675 and Q3b vs Q4 .958/.579, WLS leak (`corr resid, log n −0.08..−0.13`) avoided by OLS preference.
- `z ≥5` preserves **magnitude vs evidence distinction** — reported alongside `SE`, `post_SD`, `lb_adj`, `resid_lb` in every row.
- Yields **910 robust candidates** (`flagged_wellknown` separately **530** that meet robust criteria but are widely established — see disposition handling).

**Explicit exclusion / deduplication decisions (examples, full log in `exclusions_and_deduplication.md`):**

- `n=12, SE 0.345, resid 0.45, z=1.3` → `excluded_low_evidence` (weak evidence despite moderate resid)
- `game_id 140135 Small World Designer Edition n=246 SE 0.076 resid 2.20` — more popular reimplementation `game_id 40692 Small World n 75,285` exists → `flagged_shadowed_by_more_popular_related` (keep 40692)
- `Twilight Struggle 12333 vs Red Sea 300192` — Red Sea flagged similarly where multiple records same underlying game
- `year 2025+` (396 games 2025, 27 games 2026) → `excluded_unreleased` even if resid positive
- `is_reimplementation` family reach noted but not proof of broad appeal (see §4)

All decisions preserve `screening_disposition` plus `reason` in the CSV for manual review — not collapsed to binary pass/fail.

## 4. Method — B. Hidden-gem / broad-appeal screen (separate, no combined score)

For the **910 robust underrated candidates** from A, **separately** assess what evidence exists that appeal extends beyond the niche currently rating it. **Do not invent an RQ3 score. Do not combine signals into a hidden-gem score.** For each candidate in `broad_appeal_evidence.md`, state separately:

**Evidence of reach / recognition** — `users_rated` (popularity, not broad appeal), `num_weights` (attention proxy — median 20, up to 8660; `bgg_research_population.num_weights`), `is_reimplementation` family reach (mean users 7,338 vs 1,619), `rank_current` — but *not* proof of broad appeal (`R² game 0.201` includes popularity premium; `docs/phase2-active/phase6_volume_diagnostic.json` + `reports/phase4_selection`).

**Evidence about audience composition** — `rater-pool` `share_heavy` (`share_heavy_500plus` median 0.271, `share_heavy_250plus` 0.496) / `mean(delta)` (`mean_delta_pool` `−0.293 ±0.177`) from `reports/phase4_selection/pool_composition_summary.json`, `country` where non-missing (209,753/288,730 =72.7% have country; 27.3% missing — do not overinterpret), `collections` `own` snapshot caveat (`share_own` `0.570 ±0.145`, 15M `own=1` / 10.8M NaN, snapshot-time, `PR #4` — ownership prevalence not broad appeal, snapshot not longitudinal).

**Evidence of cross-audience consistency** — heavy vs light rater means on same game where available (`within_game_diffs_active_*` `10-24 vs 1000+` / `10-49 vs 500+` / `25-49 vs 1000+`), `game_tags` category breadth (`cat_count` mean 2.77, `cat_str`) — but low volume is *less* evidence, not more; `corr(|resid|, SE) +0.18` ( `docs/phase6-intermediate`).

**Evidence that is merely a proxy and cannot establish broad appeal** — high `raw` rating, `adj` itself, low `n` (small n is *less* evidence), ownership prevalence (`own 58%` everywhere, snapshot-time, `PR #4`), category breadth (tag overlap, not audience diversity), `users_rated` (popularity, not breadth), high residual (underratedness, not broad appeal).

For each candidate provide the four evidence types distinguished with caveats and raw values; no combined hidden-gem score. A niche game can remain an excellent underrated candidate without being promoted to hidden-gem status.

## 5. How to read the tables

**`underrated_candidates.csv` / `underrated_candidates.md`** (all 16549 estimation games with `screening_disposition`):

- `game_id`, `title`, `year`, active rating count `n_obs`, `users_rated_pop` (scrape), `rank_current`, `bayes_rating`, `raw_mean` (active), `adj_mean_g` (`mu+alpha`), `expected_quality_g` (`Q3b/OLS`), **Phase 6 residual** `underratedness_pref` (primary) + variants `cv_pref`, `wls_pref`, `ols_Q3`, `wls_Q3`, **uncertainty** `SE` (=1.194/√n), `post_SD` (=1/√(1/0.746+n/1.426)), `z`=resid/SE, `lb_adj`=adj−1.96·SE, `resid_lb`, **robustness** `min_alt_resid`, `cv_diff`, **popularity context** `n_decile`/`n_tertile`/`vol_band_label`, **release** `year_flag`, **duplicate/family** `is_reimplementation`, `reimplements_name`, `num_weights`, `weight`, **categories/mechanics** `cat_str`/`mech_str` (`bgg_research_population` complete, handle `games` 80.89% gap via that population join), **audience composition** `mean_delta_pool`, `share_heavy_*`, `share_own`, `chi2_volume_band`, **disposition** `screening_disposition` + `reason`.

- Grouped/sorted for review: robust_underrated sorted by resid desc then z; broad pools next; exclusions at bottom. Preserve all fields for later manual review.

**`broad_appeal_evidence.md`** — per robust candidate (§4 taxonomy, four evidence types per candidate, no score, caveats explicit).

**`exclusions_and_deduplication.md`** — explicit log: `game_id`, `title`, `year`, `n_obs`, `resid`, `SE`, `z`, `disposition`, `related_game_id` where applicable, `reason` (e.g. “excluded n=12 SE 0.345 resid 0.45 z=1.3 weak evidence” or “flagged shadowed by more popular reimplementation game_id 40692 n 75,285”).

**`screening_summary.json`** — machine-readable counts (broad pool size, robust size, excluded/dedup counts, n distribution, stability Jaccard, broad-appeal tallies).

## 6. Popularity vs broad appeal — explicit caution (per AGENTS.md central problem)

- `users_rated` is **popularity**, not broad appeal (`R² game 0.201` includes popularity premium).
- High residual is **underratedness** (conditional anomaly), not broad appeal.
- High `raw`/`adj` rating is **quality estimate**, not audience breadth.
- Ownership prevalence (`own 58%` everywhere, snapshot-time, `PR #4`) is not broad appeal.
- Category breadth is tag overlap, not audience diversity.
- Low rating volume is *less* evidence, not more (small n → large SE/post_SD, `z` small).
- Self-selection: BGG ratings aren't random sample — people choose what to buy/play/rate. Sample-size shrinkage corrects *noise*, not *who's in the sample*. Do not conflate measurement noise (SE) with selection into population.

## 7. Limitations and unresolved issues

- No external broad-appeal validation (sales, plays, non-BGG exposure) — residual and broad-appeal evidence are **within-BGG** and cannot establish counterfactual broad-audience quality.
- Tags overlap; indicators are descriptive contrasts, not causal effects. Measurement error in X (weight) not modeled.
- Severity adjustment removes additive rater level only (`delta_u`; Phase 4 beyond-additive selection ≈0 `SD 0.015`); non-additive forms untested.
- Timestamps unresolved (`postdate`/`rating_tstamp` semantics dual readings per AGENTS.md) — no temporal split validation.
- Country 27.3% missing; `own` is snapshot-time; `collections` not longitudinal.
- Even/odd stability is within-snapshot; residual stability `corr .962` at lowest n-quartile (mean n=100) reflects between-game signal dominance, not per-game noise-free.
- For Phase 7 screening: thresholds (`n≥100`/`n≥200`/`resid≥0.60`/`min_alt≥0.30`) are **method choices for auditable screen**, not inferred hidden-gem truth. Different reasonable thresholds move counts substantially (sensitivity tables in `screening_summary.json`).

## 8. Provenance and rerun

- Script: `scripts/32_phase7_candidate_screening.py` (bounded 4GB/3 threads, `temp_directory scratch/ducktmp`, `scratch/phase2-active` copy-once, single-scan DuckDB where needed, no wide-table bug).
- Inputs: `data/processed/phase2-active/phase6_residuals_active.parquet` (16,549), `bgg_research_population.parquet`, `game_adjusted_means_active.parquet` (`mu 7.144`, `sigma_e 1.194`), `selection_diagnostic.csv` (`share_heavy`, `mean_delta`), `within_game_diffs_active*` (heavy vs light), `game_tags_filtered`/`game_links_filtered` (33k links, reused via filtered).
- Outputs: this folder (`docs/phase7-candidate-screening/`) + `reports/phase7_candidate_screening/` (same JSON).
- Rerun: `python scripts/32_phase7_candidate_screening.py --active-dir scratch/phase2-active --population scratch/phase2-active/bgg_research_population.parquet --out-dir docs/phase7-candidate-screening`

*Tagging per AGENTS.md:* observed facts (counts, n dist, mu, SE table, Jaccard), empirical findings (CV R² .582 vs .570, overlaps, band flatness), model-dependent (all residuals, specs, robust rule), supported conclusions (preferred spec, WLS not material), assumptions (severity descriptive level), limitations as above, hypothesis/speculation flagged.

*Next phase implications:* Phase 7 is screening stage, not final hidden-gem ranking. Robust candidates are conditional anomalies with strong rating-volume evidence and cross-spec stability; broad-appeal evidence (B) is **reported separately, not scored**. Manual review should treat `underrated` (A) and `hidden-gem` (broad appeal beyond niche, B) as distinct — a game can remain excellent underrated without hidden-gem promotion.

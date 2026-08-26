# Step 7 — Audience Selection / Cult-vs-Hidden Evidence

**Population (fixed, canonical, pass2):** 14,698 games × 287,302 users × 24,146,307 rating observations (`data/processed/phase2-pass2/`, validated 0 violations, `mu 7.139`, `delta_u` from `user_severity_pass2.parquet`, `adj_mean` from `game_adjusted_means_pass2.parquet` via `scripts/39`/`40`).

**Script:** `scripts/42_phase7_audience_selection.py` (next free after 41; bounded DuckDB `memory_limit 4GB`/`threads 3`/`temp scratch/ducktmp`, narrow single-scan aggregations, copy-once `scratch/phase2-pass2`, no wide-table bug, no full-snapshot rescans, reuse `bgg_research_population.parquet` for metadata joins, reuse baseline `user_severity_pass2`/`game_adjusted_means_pass2` without refitting).

**Do NOT:** modify Phase 2 baseline, rerun Phase 5/6, build hidden-gem score, or alter Q3b/OLS `underratedness = adj - expected`.

## Objective

Investigate whether observable rating histories and rater/game characteristics provide evidence that a game's rater pool is unusually narrow/self-selected, to help distinguish:

1. Genuinely under-recognized game whose high quality is seen across different rater kinds
2. Cult/niche game whose high rating is driven primarily by highly self-selected audience

This is **not** recovery of unobserved non-raters — data cannot tell who encountered a game and chose not to rate. Instead, quantify how much evidence about missing-selection can be extracted from observable histories.

## Outputs

```
docs/phase2-pass2/step7_audience_selection/
  README.md (this file)
  audience_selectivity_summary.md (human-readable findings)
  audience_selectivity_game_level.csv (14,698 rows, per-game selectivity metrics)
  cross_audience_results.csv (per-game per-split cross-audience performance, 66911 rows)
  exposure_proxy_results.csv (per-flag per-game missing-non-rater proxy, 6249 rows)
  methodology_comparison.md (alternative measures comparison)
  known_case_sanity_check.md (validation vs known cases)
  step7_summary.json (machine-readable)
reports/phase2_pass2/step7_audience_selection/ (mirror)
```

## Key Measures

### A. Audience Concentration
Per-game characterization of rater-pool specialization vs broader active population:
- **Volume concentration:** share per volume band (7 bands), Herfindahl, entropy, share_heavy_500plus, share_light_10_24
- **Weight preference:** share of raters whose mean rated weight within ±0.5 (sensitivity ±0.3/±0.8/±1.0)
- **Type specialist:** share with ≥10 (and ≥20, ≥5) other games of same primary type (18XX/Wargame/Party/Economic/Coop/Legacy) excluding target; for Other games, NaN (not applicable, use cat related)
- **Category/mechanic related:** share with ≥1 other game sharing ≥1 category (binary, via active cats ≥2 overlap; mean 0.993 indicates most users have ≥1 other sharing — least discriminating)
- **Ownership:** share_own (collections.own=1 / n_raters, snapshot caveat)
- **Mean rater severity:** mean_delta_raters, sd_delta

Do not assume one measure correct; compare alternatives (see methodology_comparison.md).

### B. Prior Exposure / Specialist Status
Per-rating proxy "other games of same type excluding target" (avoid look-ahead, document timestamp limitation: postdate/rating_tstamp unresolved, so other count proxy not true chronological prior):
- Bins: 0–4 (no/small), 5–19 (moderate), ≥20 (heavy); also ≥10 sensitivity
- Per-game shares: share_0_4, share_5_19, share_ge20, mean_other, median_other
- For flagged types, use n_flag-1; for Other, not applicable (cat tiers not computed due to memory, document limitation)

Temporal limitation: other count includes ratings that may have occurred after target rating; without reliable timestamps, cannot establish true prior. Interpret as observable type exposure, not causal prior.

### C. Cross-Audience Performance
For sufficiently supported games (≥10 per side preferred, ≥5 minimum, report both), compare severity-adjusted ratings (`rating - delta_u`) across splits:
- **Volume:** 10-24 vs 500+ (and 1000+), heavy 500-999+1000+ vs light 10-24
- **Specialist vs non-specialist:** 0–4 vs ≥20 (and vs ≥10) for primary type (flagged only)
- **Ownership:** own=1 vs not own (snapshot caveat)
- **Weight preference:** within ±0.5 vs outside

Per-game per-split: n_low/high, mean_low/high_adj, sd, se, diff = high-low, se_diff, z, p, supported_ge10/ge5, is_significant. Key question: does high quality remain among non-specialists / light raters / non-owners?

Do not assume one split sufficient; evaluate thresholds sensitivity.

### D. Rating Heterogeneity
Distinguish:
- Ordinary noise (SE-aware, |z|<2)
- Genuine disagreement (between-segment diff exceeding sampling noise, |z|≥2 and |diff|≥0.3)
- Concentrated specialist enthusiasm (high adj_mean ≥7.5 + low diff <0.3 but narrow pool spec>0.4)

Do not use raw SD alone; use SE-aware diff tests. Preserve insufficient_evidence where no split has ≥5 per side.

### E. Rater-Pool Distinctiveness
Compare game's rater-pool composition to reference populations:
- **Global:** all 24.1M ratings
- **Same type:** all ratings of games sharing primary type (e.g., all Wargames)
- **Same weight class:** Light/Medium/Heavy
- **Same volume decile:** D1-D5 by n_obs

Metric: total variation distance (TVD) for volume distribution, delta_diff and weight_diff vs reference. Report all; same-type most informative for typed games (global would flag all wargames as distinctive). Compare constructions (see methodology_comparison.md).

### F. Missing-Non-Rater Proxy ("Dog That Didn't Bark")
Observable histories allow identifying plausible under-exposure, not imputed negative ratings:
- For each typed game, `penetration = n_raters Among enthusiasts / total_enthusiasts`, where enthusiasts = users with ≥20 (and ≥10) total ratings of that type (and variant other ≥20). Missing = total - n_raters.
- Example: what fraction of users who rated ≥20 Wargames have also rated this specific wargame?
- For Other, generic enthusiasts via category-sharing not computed globally (per-game varying, heavy) — limitation, use rater share proxy.

Identification limit: missing rating could mean never encountered, encountered and disliked, encountered but did not rate, unknown. Do not interpret missing as negative preference. This output is exposure/selectivity proxy, not imputed negative ratings. Report both ge20 and ge10 sensitivity and other vs total thresholds.

### G. Cult-vs-Hidden Evidence Taxonomy
Auditable taxonomy (not binary classifier), preserving underlying measurements, not calling game "cult"/"hidden" as fact:

- **low_audience_selectivity:** rater pool resembles comparable baseline across measured dimensions (deviations < q75, TVD low)
- **moderate_audience_selectivity:** 1–2 dimensions deviate (spec, TVD, own, herf, penetration)
- **high_audience_selectivity:** ≥3 dimensions deviate (multiple unusual concentrations)
- **insufficient_evidence:** n_obs <150 or no cross-audience support and n<250 → too few to measure reliably

Thresholds based on empirical quantiles (q75: spec 0.94, tvd 0.23, own 0.66, herf 0.20, pen <0.05). For each game, preserve deviation_count, deviation_details, heterogeneity_category, and reason. Do not infer low selectivity = broadly appealing (could be niche but not captured), nor high selectivity = bad (could be excellent within niche).

Taxonomy counts: {'moderate_audience_selectivity': 6867, 'low_audience_selectivity': 3936, 'insufficient_evidence': 2771, 'high_audience_selectivity': 1124}

### H. Known Case Sanity Check
Small recognizable sets to sanity-check measures, not hand-tune:
- 18XX examples (1830, 1846, 18Chesapeake, 1817) → expect high specialist (but data shows varied: 1830 low, 1817 high)
- Mainstream (Catan, Ticket to Ride, Pandemic, Carcassonne) → low selectivity expected but data shows moderate due to Economic broad category
- Niche specialist (Monikers, On to Richmond II, System Gateway) → higher selectivity expected
- 55 likely_hidden_gem_candidate pool (variable)
- Monikers/Time's Up! family (single Monikers in pass2 after cleanup)

Validation exercise; do not tune methodology to force expected answers.

## Interpretation Rules (from Task)

1. Do not claim self-selection solved.
2. Distinguish observable rater-pool selectivity, user×type taste, and unobserved non-rater selection.
3. Do not alter quality estimator.
4. Do not create combined hidden-gem score.
5. Do not infer low diversity = bad; high diversity ≠ proven broad appeal.
6. Preserve uncertainty and insufficient-evidence cases.

Final question answered: "Given data we actually have, how much can we tell whether highly rated game is broadly appreciated versus primarily highly rated by specialized/self-selected audience?" → See audience_selectivity_summary.md.

## Data Handling (as specified)

- Copy once into `scratch/phase2-pass2` (DuckDB bounded 4GB/3 threads/temp scratch/ducktmp), narrow single-scan aggregations, no wide-table bug, no full-snapshot rescans.
- Use `bgg_research_population.parquet` for complete metadata joins (categories/mechanics/families JSON arrays) via `game_flags` view (LEFT JOIN preserve 14,698 rows, weight NULL 7).
- Reuse refreshed baseline `user_severity_pass2` / `game_adjusted_means_pass2` (mu 7.139) without refitting.

## Reproduction

```bash
python scripts/42_phase7_audience_selection.py
# Options: --pass2-dir data/processed/phase2-pass2 --population data/processed/bgg_research_population.parquet --out-docs docs/phase2-pass2/step7_audience_selection
```

**Validation:** counts reconcile (14,698 games, 24,146,307 obs), mu diff -0.000000, no degenerate_strict, all joins SEMI JOIN validated via earlier validation.json.

## Limitations (must read)

- Timestamp semantics unresolved → prior exposure is other count proxy, not true chronological prior.
- Collections own is snapshot, not rating-time ownership → share_own caveat.
- 18XX definition strictly Series:18xx (21 history false positives excluded); Legacy via mechanic only (50 games).
- Per-user mean_weight unstable for low-volume raters; weight NULL 7 games excluded.
- Specialist thresholds category-breadth dependent (Party/Coop/Economic broad need ≥20 not ≥10); global q75 threshold not type-specific, hence 18XX low spec not flagged.
- Penetration denominator per-game for Other not computed (limitation).
- Self-selection not solved; observable pool selectivity ≠ unobserved non-rater selection.
- No combined hidden-gem score; taxonomy is evidence, not classification.

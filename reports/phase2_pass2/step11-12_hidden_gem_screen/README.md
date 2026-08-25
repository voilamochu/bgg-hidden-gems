# Step 11-12 — Hidden-Gem Screening Pass on Final Pass-2 (Combined)

**Generated:** 2026-08-25T12:00:50.861027+00:00Z · seed 20260824 · STOP after combined Step 11-12 (no further screens)
**Population (canonical, reuse):** 14,698 games × 287,302 users × 24,146,307 rating observations, `data/processed/phase2-pass2/` (validated mu 7.139, `user_severity_pass2.parquet` + `game_adjusted_means_pass2.parquet` via scripts 39/40 — **reuse confirmed Pass-2 severity-adjusted quality `adj_mean` and Q3bFam expected-quality `expected_Q3bFam` / residual `resid_Q3bFam` from Step 9B/10, do NOT refit severity or Q3bFam**)
**Models:** Q3bFam primary (48f, bands+ns_year+structure+cats≥500+fam_18XX+fam_Cooperative+fam_Legacy, CV R² 0.6033) + Q4Fam sensitivity (78f, CV 0.6151, Spearman 0.9775 vs primary)
**Starting pool — Step 10 primary:** `adj_mean ≥7.5` AND `Q3bFam resid ≥0.75` → **532 games** (`screening_pool.csv` under `docs/phase2-pass2/step10_quality_underratedness_gates/`, median n 256, SE 0.0746, `step10_summary.json`). Sensitivities `7.5+1.00 (211)`, `7.0+0.75 (774)` are context, not the starting gate. This pool is **quality + underratedness only** — hiddenness and audience-selection not yet applied, exactly as Step 10 left it.

## Executive summary

**Starting 532 → hiddenness → final categories (screened eligible+borderline 505; 27 excluded as not hidden):**

| Stage | count | % of 532 |
|---|---|---|
| Starting pool (quality+underratedness) | 532 | 100% |
| Hiddenness eligible (<1700 n_obs) | 485 | 91.2% |
| Hiddenness borderline (1700-2500) | 20 | 3.8% |
| Hiddenness exclude (>2500, not hidden) | 27 | 5.1% |
| **Screened (eligible+borderline)** | 505 | 94.9% |

**Final outcome categories (from screened 505, no combined score, auditable rule):**

| outcome_category | count | % screened | % of 532 | headline |
|---|---|---|---|---|
| strong_hidden_gem_evidence | 39 | 7.7% | 7.3% | good + underrated + genuinely hidden + no material audience-selection concern, supporting cross-audience where available |
| plausible_hidden_gem | 176 | 34.9% | 33.1% | good + underrated + hidden but some evidence incomplete/borderline (hiddenness borderline, SE LB dips, one audience dimension borderline) |
| niche_but_high_quality | 163 | 32.3% | 30.6% | good + underrated but audience-selection suggests niche-dependent (high spec share, cross drop, propensity sensitive, Q4Fam fragile) |
| insufficient_evidence | 127 | 25.1% | 23.9% | cannot establish hidden/broad-appeal confidently (low n wide SE, insufficient_overlap, broad-appeal unavailable) |
| excluded_popular_not_hidden | 27 | — | 5.1% | not hidden (>2500) — listed separately |

**If hiddenness leaves <10 strong candidates or >500 plausible, flagged:** Strong = 39 → OK ≥10; Plausible = 176 → OK <500. Goal is genuine auditable set, not fixed size — here strong is larger; plausible larger; niche/insufficient clearly separated, as intended.

## Top examples

**Strong (39) — all eligible, LB≥7.0, Q4 robust, taxonomy low/moderate, propensity adequate/borderline, cross broad:**

| game_id | title | year | n_obs | adj_mean | resid | q4 | taxonomy | overlap |
|---|---|---|---|---|---|---|---|
| 2470 | The Extraordinary Adventures of Baron Munc | 1998.0 | 379 | 7.54 | 1.68 | 1.60 | moderate_audience_selectivity | borderline_overlap |
| 62814 | Tumblin-Dice Medium | 2008.0 | 215 | 7.61 | 1.53 | 1.50 | low_audience_selectivity | borderline_overlap |
| 275972 | Star Trek: Alliance – Dominion War Campaig | 2021.0 | 193 | 8.59 | 1.34 | 1.32 | moderate_audience_selectivity | borderline_overlap |
| 244258 | The Red Dragon Inn 7: The Tavern Crew | 2018.0 | 310 | 7.86 | 1.31 | 1.41 | moderate_audience_selectivity | adequate_overlap |
| 340216 | Heredity: The Book of Swan | 2023.0 | 176 | 8.63 | 1.25 | 1.14 | moderate_audience_selectivity | borderline_overlap |

**Plausible (176) — sample:**

| game_id | title | n_obs | adj | resid | hidden | reason |
|---|---|---|---|---|---|---|
| 4385 | A Gamut of Games | 434 | 8.07 | 1.95 | eligible | plausible: passes quality 8.07 resid 1.95 hidden eligible n 434 but bo |
| 1803 | Zopp | 158 | 7.67 | 1.75 | eligible | plausible: passes quality 7.67 resid 1.75 hidden eligible n 158 but bo |
| 341489 | Carrooka | 195 | 8.55 | 1.75 | eligible | plausible: passes quality 8.55 resid 1.75 hidden eligible n 195 but bo |
| 541 | Das Motorsportspiel | 381 | 7.88 | 1.67 | eligible | plausible: passes quality 7.88 resid 1.67 hidden eligible n 381 but bo |
| 6688 | Ninety-Nine | 554 | 7.89 | 1.60 | eligible | plausible: passes quality 7.89 resid 1.60 hidden eligible n 554 but bo |

**Niche (163) — why niche, not hidden gem:**

- High specialist share / TVD / taxonomy high, or Q4Fam fragile, or propensity strongly_sensitive, or cross niche_drop. Example: 33434 Funkenschlag: EnBW (n 198 adj 8.69 resid 1.90) etc. See `pass1_failure_mode_audit.md` and `screening_evidence_table.csv` for per-row citation.

**Insufficient (127) — why insufficient:**

- Low n (100-150) + wide SE + propensity insufficient_overlap + no cross ge10 support. Example: 100-rating games with SE ~0.11 and overlap insufficient (e.g., 120269 Red White & Blue Racin': Stock (n 131 adj 8.45 resid 1.99)). Broad appeal cannot be established from available data — valid "we can't tell", not failure.

## Pass-1 failure modes how handled

| Mode | flagged | how checked (source) |
|---|---|---|
| editions/variants | 46 | title pattern + families Big Box + `combined_primary_edition_family.csv` (0 in pool primary, but 36 title-pattern flagged) |
| expansions/sequels/game-system | 7 | families Admin: Game System Entries + categories Fan Expansion + title Game System/Infinity Box |
| duplicate/family-related | dup 7 family_link 14 | `combined_sensitivity_dup.csv` (7 in pool) + n_version>15 / n_reimpl>1 |
| obviously popular | exclude 27 nuance 16 | `n_obs>2500` (27) + `users_rated>2500` but `n_obs≤2500` (16) + rank<500 |
| mediocre large resid | 49 | adj 7.5-7.7 resid 0.75-0.90 borderline |
| specialist-audience-dependent | 95 | spec>0.90, TVD>0.35, taxonomy high, cross niche_drop, propensity strongly |
| broad-appeal unavailable | 155 | insufficient_overlap (155) + n_supported_ge10==0 |

All flagged via **existing Pass-2 cleanup/relationship evidence** — see `pass1_failure_mode_audit.md` for per-source citation and per-category breakdown. A game that survives 1,700 rule but is edition/variant/expansion/sequel/system per that evidence is **flagged as not hidden**.

## What Q3bFam correction changed vs old Q3b

- Global CV gain modest (+0.0046, 0.5987→0.6033) but **material locally**: Q3b pool 550 → Q3bFam 532 (lost 38, gained 20, Jaccard 0.903). **31 of 38 lost are 18XX** (81% of churn; 18XX mean resid +0.676→0.000, β +0.748±0.062, 5/5 folds). Final hidden-gem screening therefore contains **0 18XX** under Q3bFam vs ~31 18XX would have inflated candidate set under Q3b — correctly removing the omitted-family artifact without global re-ranking (Spearman 0.9928). Mechanics sensitivity Q4Fam (0.6033→0.6151) is 82% overlap, movers are mechanics repricings only. See `comparison_q3b_vs_q3bFam_pool.md`.

## What is NOT claimed

- Not a ranking — categorized evidence table, auditable row by row (see `screening_evidence_table.csv`).
- Not broad-appeal proof — strong candidates have supporting cross-audience where available (≥10 per side), but observable data cannot recover non-raters; moderate/insufficient remain candidates for external validation (plays/sales), not proof (per Step 7/7B/7C limitations).
- Not hidden-gem score — dimensions kept separate (quality / underratedness / hiddenness / audience-selectivity / propensity / cross-audience), no weighted sum, per Step 8 distinction.
- Sampling noise ≠ selection: shrinkage/SE addresses noise (EB λ 2.00, w median 0.994, negligible), not who is in sample. Low n ≠ just needs more data to converge.
- If data can't answer, say so — `insufficient_evidence` is a valid result, not failure (here 127 of 505 screened).

## Files

- `hiddenness_screen.md` + `hiddenness_counts.csv` (§1 counts, boundary examples, users_rated nuance)
- `screening_evidence_table.csv` — one row per screened game (532 rows, or 505 eligible+borderline documented) with columns: game_id, title, year, n_obs, adj_mean, expected_Q3bFam, resid_Q3bFam, resid_Q4Fam, SE, lower_bound_adj, lower_bound_resid, volume_band, hiddenness_bucket, edition_duplicate_flag (with source), family_link_flag, audience_selectivity_metrics (Step7), propensity_sensitivity (Step7B/7C), cross_audience_support, outcome_category, reason
- `outcome_category_breakdown.md` + `outcome_counts.csv` (per-category counts, distributions, examples)
- `pass1_failure_mode_audit.md` (how each Pass-1 mode checked, how many flagged, examples, per-outcome breakdown)
- `comparison_q3b_vs_q3bFam_pool.md` (whether Step 9B correction materially changes final hidden-gem pool, count and 18XX impact as Step 10 did)
- `step11-12_summary.json` (machine-readable)
- Mirrors under `reports/phase2_pass2/step11-12_hidden_gem_screen/`

**Reproduce:** `python scripts/51_step11-12_hidden_gem_screen.py` (loads screening_pool.csv 532 + games_pass2 + links + step7/7b/7c outputs, no 24M wide sorts, seed 20260824, handles 7 weight null as before via flags).

Tags: observed fact = counts, hidden buckets, edition pruned sets; empirical finding = residual distributions, audience/propensity/cross stats (model-dependent but data-driven); model-dependent conclusion = Q3bFam primary, outcome rule mapping, strong/plausible interpretation; assumption = additive severity reuse correct, weight median-fill, category threshold 500, propensity model calibrated; limitation = cannot recover non-raters, timestamp unresolved, snapshot collections, borderline hiddenness still needs external validation.

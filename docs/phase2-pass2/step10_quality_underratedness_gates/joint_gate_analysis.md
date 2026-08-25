# Joint Gate Analysis — Quality AND Underratedness (Pass-2)

**Generated:** 2026-08-25T11:20:29Z · seed 20260824 · Q3bFam primary; Q4Fam as sensitivity.

## Candidates (§4 of task) — BOTH required

| joint gate (adj & resid) | description | joint Q3bFam | resid-only | qual-only | lost if drop quality (resid pass but qual fail) | lost if drop resid (qual pass but resid fail) | joint Q4Fam | median n | p10–p90 n | median adj / resid |
|---|---|---|---|---|---|---|---|---|---|---|
| 7.50 & 0.75 | task example: moderate quality + high underratedness | 532 | 911 | 3446 | 379 (42%) | 2914 (85%) | 489 | 256 | 118–1255 | 8.00/+0.94 |
| 7.50 & 1.00 | task example: moderate quality + very high underratedness | 211 | 330 | 3446 | 119 (36%) | 3235 (94%) | 194 | 223 | 116–917 | 8.05/+1.17 |
| 7.00 & 0.75 | task example: permissive quality + high underratedness | 774 | 911 | 6800 | 137 (15%) | 6026 (89%) | 732 | 252 | 119–1198 | 7.76/+0.94 |
| 7.50 & 0.50 | permissive underratedness (p~75) + moderate quality | 1062 | 2175 | 3446 | 1113 (51%) | 2384 (69%) | 1012 | 315 | 118–2488 | 7.97/+0.75 |
| 8.00 & 0.75 | strong quality + high underratedness (precision gate) | 266 | 911 | 1245 | 645 (71%) | 979 (79%) | 249 | 234 | 117–1150 | 8.34/+0.96 |
| 7.93 & 0.61 | data-driven joint p90/p90 (top 10% quality AND top 10% residual) | 441 | 1470 | 1470 | 1029 (70%) | 1029 (70%) | 426 | 282 | 118–1709 | 8.23/+0.87 |
| 7.00 & 1.00 | permissive quality (7.0) + very high residual 1.0 | 297 | 330 | 6800 | 33 (10%) | 6503 (96%) | 279 | 219 | 116–810 | 7.86/+1.17 |

*`resid-only` = games with resid≥thr regardless of quality; `qual-only` = adj≥thr regardless of resid. The two "lost if drop" columns quantify why both matter.*

## Why both matter (reproducing Step 9's 30% finding)

- At `adj≥7.5 & resid≥0.75`: resid-only 911 but joint 532 — **379 (42%) of highly-underrated games fail the quality bar** (they are expected 6.0→6.9 etc.). Conversely, qual-only 3,446 but joint 532 — **2,914 (85%) of high-quality games are NOT highly underrated** (they are expected to be good).
- At `adj≥7.5 & resid≥1.00`: resid-only 330 → joint 211 — 36% fail quality.
- Stated Step 9 figure "top 30% of Q3bFam residuals fail 7.5" corresponds to: top-1% resid (≥1.19) has 31% with adj<7.5 (45/145); top-5% (≥0.80) has 38% with adj<7.5. Our `0.75` gate has 42% fail — same phenomenon, magnitude depends on resid cutoff.

=> Filtering on residual alone would promote many mediocre-quality games; filtering on quality alone would promote many predictable hits (high expected). **Joint gate is necessary** per Step 8's separation of quality / underratedness / hiddenness / audience-selection risk.

## Which joint gates are sensible?

- **Primary `7.5 + 0.75` → 532 games** (median n 256, p10 118, p90 1255): not tiny (>20) nor huge (<2000), median quality 8.00 and residual +0.94. Recommended primary.
- **Strict `7.5 + 1.00` → 211**: halve the pool, higher precision.
- **Permissive quality `7.0 + 0.75` → 774**: expands 532→774 (+45%) by admitting 6.9–7.5 games — useful sensitivity for quality-threshold stability.
- **Lenient resid `7.5 + 0.50` → 1062**: too broad (≈2k+ if qual were lowered), useful as upper-bound reference.
- **Data-driven `7.93 (p90 qual) + 0.61 (p90 resid)` → 441**: very selective, median quality higher but pool composition shifts to high-n.

## n distribution per joint gate

See table above (median, p10–p90). Across all joint gates, median n 220–260 (low-n enriched vs. qual-only median ~347) and SE median 0.07–0.08. See also `band_summary_pass2.csv`.

## Examples

**Joint `adj≥7.5 & resid≥0.75` — 5 diverse examples (top/mid/tail by resid):**

| game_id | title | year | n_obs | adj_mean | expected | resid (Fam) | resid (Q4Fam) | vol_band |
|---|---|---|---|---|---|---|---|---|
| 120269 | Red White & Blue Racin': Stock Car Action Game | 2012 | 131 | 8.45 | 6.45 | +1.99 | +1.98 | 100-199 |
| 4385 | A Gamut of Games | 1969 | 434 | 8.07 | 6.12 | +1.95 | +1.96 | 200-499 |
| 124839 | Hoplomachus: The Lost Cities | 2012 | 555 | 7.98 | 7.04 | +0.94 | +0.72 | 500-999 |
| 373105 | Legendary Encounters: The Matrix | 2023 | 245 | 8.41 | 7.47 | +0.94 | +0.88 | 200-499 |
| 3097 | 1849: The Game of Sicilian Railways | 1998 | 942 | 8.92 | 8.17 | +0.75 | +0.76 | 500-999 |
| 40529 | Cosmic Encounter | 1991 | 1047 | 7.57 | 6.82 | +0.75 | +0.75 | 1k-2.5k |

**Joint `adj≥7.5 & resid≥1.0` — 5 diverse examples (top/mid/tail by resid):**

| game_id | title | year | n_obs | adj_mean | expected | resid (Fam) | resid (Q4Fam) | vol_band |
|---|---|---|---|---|---|---|---|---|
| 120269 | Red White & Blue Racin': Stock Car Action Game | 2012 | 131 | 8.45 | 6.45 | +1.99 | +1.98 | 100-199 |
| 4385 | A Gamut of Games | 1969 | 434 | 8.07 | 6.12 | +1.95 | +1.96 | 200-499 |
| 59335 | Wherewolf | 2009 | 164 | 7.51 | 6.33 | +1.17 | +1.21 | 100-199 |
| 315048 | Survive: Escape from Atlantis! | 2010 | 384 | 7.55 | 6.38 | +1.17 | +1.08 | 200-499 |
| 147884 | Ore: The Mining Game | 2013 | 116 | 7.57 | 6.57 | +1.00 | +1.03 | 100-199 |
| 250396 | Terminator Genisys: Rise of the Resistance | 2018 | 605 | 8.03 | 7.03 | +1.00 | +0.98 | 500-999 |

**Joint `adj≥7.0 & resid≥0.75` — 5 diverse examples (top/mid/tail by resid):**

| game_id | title | year | n_obs | adj_mean | expected | resid (Fam) | resid (Q4Fam) | vol_band |
|---|---|---|---|---|---|---|---|---|
| 120269 | Red White & Blue Racin': Stock Car Action Game | 2012 | 131 | 8.45 | 6.45 | +1.99 | +1.98 | 100-199 |
| 4385 | A Gamut of Games | 1969 | 434 | 8.07 | 6.12 | +1.95 | +1.96 | 200-499 |
| 292811 | American Bookshop | 2019 | 537 | 7.86 | 6.92 | +0.94 | +0.92 | 500-999 |
| 367396 | Avalon: Big Box | 2022 | 398 | 8.35 | 7.41 | +0.94 | +0.86 | 200-499 |
| 296164 | Yura Yura Penguin | 2019 | 211 | 7.39 | 6.64 | +0.75 | +0.73 | 200-499 |
| 264295 | Fabulantica | 2018 | 165 | 7.27 | 6.52 | +0.75 | +0.64 | 100-199 |

**Joint `adj≥7.5 & resid≥0.5` — 5 diverse examples (top/mid/tail by resid):**

| game_id | title | year | n_obs | adj_mean | expected | resid (Fam) | resid (Q4Fam) | vol_band |
|---|---|---|---|---|---|---|---|---|
| 120269 | Red White & Blue Racin': Stock Car Action Game | 2012 | 131 | 8.45 | 6.45 | +1.99 | +1.98 | 100-199 |
| 4385 | A Gamut of Games | 1969 | 434 | 8.07 | 6.12 | +1.95 | +1.96 | 200-499 |
| 40529 | Cosmic Encounter | 1991 | 1047 | 7.57 | 6.82 | +0.75 | +0.75 | 1k-2.5k |
| 326937 | Unmatched: For King and Country | 2023 | 633 | 8.27 | 7.52 | +0.75 | +0.74 | 500-999 |
| 68076 | Conflict of Heroes: Guadalcanal – The Pacific 1942 | 2016 | 489 | 8.16 | 7.66 | +0.50 | +0.59 | 200-499 |
| 400617 | Mythic Mischief Vol. II | 2024 | 112 | 8.13 | 7.63 | +0.50 | +0.46 | 100-199 |

## Interpretation (claim-tagged)

- **Observed fact:** counts, n distributions are from data.
- **Empirical finding (model-dependent):** residual-based joint counts depend on Q3bFam specification.
- **Model-dependent conclusion:** joint gate is required; `7.5+0.75` primary with `7.5+1.0` and `7.0+0.75` sensitivities carries forward. Flags `tiny (<20)` / `huge (>2000)` not triggered (largest joint in table 1062, smallest 211).

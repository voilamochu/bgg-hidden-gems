# Known Case Sanity Check — Step 7 (Corrected)

**Generated:** 2026-08-24T17:36:36Z
**Population:** 14,698 games × 287,302 users × 24,146,307 obs (pass2, mu 7.139)
**Purpose:** Validation exercise (not hand-tuned classifier) to check whether concentration/distinctiveness/cross-audience measures behave as expected on recognizable cases.

## Cases Defined

| Game | ID | Category | Expectation |
| CATAN | 13 | mainstream |  |
| Ticket to Ride | 9209 | mainstream |  |
| Pandemic | 30549 | mainstream |  |
| Carcassonne | 822 | mainstream |  |
| 1830: Railways & Robber Barons | 421 | 18XX niche |  |
| 1846: The Race for the Midwest | 17405 | 18XX niche |  |
| 18Chesapeake | 253608 | 18XX niche |  |
| 1817 | 63170 | 18XX niche |  |
| Monikers | 156546 | niche high-own |  |
| On to Richmond II: The Union Strikes South | 367432 | niche heavy warg |  |
| System Gateway (fan expansion for Android: Netrunner) | 345976 | niche fan expansion |  |

**Definitions:** `spec_primary_share_ge10` = share of raters with ≥10 other games of same primary type (excluding target). `tvd_volume_global` = TVD vs all ratings. `share_within_05` = weight preference overlap. `share_own` = ownership snapshot. `volume_diff_adj` = severity-adjusted mean difference high(500+) vs low(10-24). `specialist_diff_adj` = 0-4 vs ≥20 exposure.

## Observed Metrics (severity-adjusted where applicable)

| Game | n | adj | Weight | Spec≥10 | TVD glob | Wt±0.5 | Own | Cat/Mech | Mean Δ | Taxonomy | Het | Vol diff | Spec diff |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CATAN | 119003 | 7.12 | 2.3 | 0.50 | 0.31 | 0.85 | 0.70 | 0.98 | -0.13 | moderate_audience_selectivity | genuine_disagreement | -0.10 | -0.17 |
| Ticket to Ride | 87222 | 7.50 | 1.8 | NA | 0.25 | 0.60 | 0.63 | 0.71 | -0.16 | moderate_audience_selectivity | genuine_disagreement | 0.40 | NA |
| Pandemic | 120228 | 7.62 | 2.4 | 0.48 | 0.29 | 0.83 | 0.69 | 0.74 | -0.14 | moderate_audience_selectivity | genuine_disagreement | 0.19 | 0.27 |
| Carcassonne | 122032 | 7.50 | 1.9 | NA | 0.29 | 0.65 | 0.72 | 0.98 | -0.14 | moderate_audience_selectivity | genuine_disagreement | 0.22 | NA |
| 1830: Railways & Robber B | 5628 | 8.41 | 4.2 | 0.14 | 0.09 | 0.00 | 0.57 | 1.00 | -0.56 | low_audience_selectivity | genuine_disagreement | 0.11 | 1.14 |
| 1846: The Race for the Mi | 2998 | 8.54 | 4.0 | 0.24 | 0.15 | 0.02 | 0.57 | 1.00 | -0.64 | moderate_audience_selectivity | genuine_disagreement | -0.12 | 0.60 |
| 18Chesapeake | 1732 | 8.34 | 3.8 | 0.28 | 0.17 | 0.03 | 0.50 | 1.00 | -0.71 | moderate_audience_selectivity | genuine_disagreement | -0.16 | 0.00 |
| 1817 | 764 | 9.36 | 4.8 | 0.59 | 0.16 | 0.00 | 0.54 | 1.00 | -0.80 | moderate_audience_selectivity | genuine_disagreement | -0.10 | 0.35 |
| Monikers | 6607 | 8.08 | 1.1 | 0.76 | 0.10 | 0.03 | 0.67 | 1.00 | -0.32 | moderate_audience_selectivity | genuine_disagreement | -0.14 | -0.04 |
| On to Richmond II: The Un | 102 | 9.50 | 3.8 | 0.97 | 0.13 | 0.39 | 0.94 | 1.00 | -0.33 | insufficient_evidence | genuine_disagreement | 0.68 | NA |
| System Gateway (fan expan | 660 | 9.45 | 3.5 | NA | 0.13 | 0.06 | 0.81 | 1.00 | -0.36 | moderate_audience_selectivity | genuine_disagreement | 0.15 | NA |

## Validation Against Expectations (Corrected for Broad Category Inflation)

**Mainstream (Catan, Ticket to Ride, Pandemic, Carcassonne) — expected low selectivity but observed moderate:**
- Catan spec 0.50 (Economic broad, median 0.86) — 0.50 is actually below median for Economic, indicating *more* diverse than typical Economic game. So moderate taxonomy reflects that Catan is not as specialist as typical Economic game, but still 50% of its raters have ≥10 other Economic games because Economic is broad. **Threshold ≥10 too permissive for broad categories.**
- Ticket to Ride spec NaN (Other, trains not flagged) → fallback cat related not discriminating.
- Pandemic Coop 0.47 similarly below median 0.86 → moderate.
- **Lesson: For broad categories, use ≥20 threshold or type-specific quantiles. Global q75 0.939 is dominated by broad categories and not sensitive for narrow 18XX.**

**18XX niche (1830 0.13 low, 1846 0.24 moderate, 18Chesapeake 0.27 moderate, 1817 0.59 moderate) — varied, not uniformly high:**
- 1830 is gateway 18XX with many non-specialist raters (only 13% heavy 18XX), so low selectivity correctly indicates gateway breadth. 1817 is more niche (59% heavy). **Not all 18XX are equally niche; measures correctly show variation.**

**Monikers Party 0.76 moderate (Party median 0.86, so 0.76 slightly below median) — moderate, not high as earlier expected for high-own niche. Party is broad (62k users ≥10), so 0.76 is not distinctive.**

**On to Richmond II Wargame 0.97 high but n=102 insufficient → correctly insufficient, not mislabeled as broad. Shows narrow pool + small n → insufficient for heterogeneity.**

**System Gateway Other NaN moderate.**

## Overall Validation Verdict (Corrected)

- **Measures show plausible variation but threshold sensitivity is high due to broad categories inflating spec mean to 0.83.** Global q75 0.939 not appropriate for narrow types. Recommend type-specific thresholds.
- **TVD and ownership more stable for mainstream vs niche separation than spec for broad categories.**
- **Do not tune thresholds to force expected answers; current global thresholds are documented and show limitation.**

## Caveats

- Small N per category, broad category inflation, trains not flagged, etc.

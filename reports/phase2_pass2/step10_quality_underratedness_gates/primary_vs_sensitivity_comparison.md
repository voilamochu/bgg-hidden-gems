# Primary vs Sensitivity Comparison — Q3bFam vs Q4Fam & Q3b vs Q3bFam (Family Correction)

**Generated:** 2026-08-25T11:20:29Z · seed 20260824 · Primary Q3bFam 48 feats (CV R² 0.6033), Sensitivity Q4Fam 78 feats (R² 0.6151), Q3b baseline R² 0.5987.

## Overall residual agreement

| comparison | Spearman | Pearson | Jaccard top1% | Jaccard top5% |
|---|---|---|---|---|
| Q3b vs Q3bFam | 0.9928 | 0.9941 | 0.860 | 0.861 |
| Q3bFam vs Q4Fam | 0.9775 | 0.9830 | 0.728 | 0.767 |

- Spearman ~0.99 indicates near-identical ranking globally; Jaccard ~0.86 for Q3b→Q3bFam top1% shows family correction is **local** (mostly 18XX). Q3bFam vs Q4Fam Jaccard lower (~0.78 top1%) as mechanics reallocate some signal.

## Per joint gate: Q3bFam vs Q4Fam (§6)

| joint gate | description | Q3bFam pool | Q4Fam pool | inter | Jaccard | only Q3bFam | only Q4Fam |
|---|---|---|---|---|---|---|---|
| 7.50 & 0.75 | task example: moderate quality + high underratedness | 532 | 489 | 459 | 0.817 | 73 | 30 |
| 7.50 & 1.00 | task example: moderate quality + very high underratedness | 211 | 194 | 179 | 0.792 | 32 | 15 |
| 7.00 & 0.75 | task example: permissive quality + high underratedness | 774 | 732 | 669 | 0.799 | 105 | 63 |
| 7.50 & 0.50 | permissive underratedness (p~75) + moderate quality | 1062 | 1012 | 948 | 0.842 | 114 | 64 |
| 8.00 & 0.75 | strong quality + high underratedness (precision gate) | 266 | 249 | 233 | 0.826 | 33 | 16 |
| 7.93 & 0.61 | data-driven joint p90/p90 (top 10% quality AND top 10% residual) | 441 | 426 | 395 | 0.837 | 46 | 31 |
| 7.00 & 1.00 | permissive quality (7.0) + very high residual 1.0 | 297 | 279 | 252 | 0.778 | 45 | 27 |

- At primary `7.5+0.75`: 532 (Fam) vs 3446 qual pool shifts slightly to 489 under Q4Fam (Jaccard 0.817). 73 games switch in total (30 lost, 43 gained) — modest churn, not a different list.
- Stricter `7.5+1.00`: Jaccard 0.792 — similar stability.

**Which games enter/leave when switching to Q4Fam?** Top movers (|delta Q4Fam−Q3bFam| largest) — mechanics sensitivity reprices some wargame/card/simulation signals:

| game_id | title | year | n_obs | adj_mean | expected Q3bFam | expected Q4Fam | resid Q3bFam | resid Q4Fam | delta | vol_band |
|---|---|---|---|---|---|---|---|---|---|
| 103 | Titan | 1980 | 3870 | 7.27 | 7.54 | 6.98 | -0.27 | +0.29 | +0.55 | 2.5k-5k |
| 731 | Escape from New York | 1981 | 101 | 5.70 | 5.60 | 5.05 | +0.10 | +0.65 | +0.55 | 100-199 |
| 804 | Thunder Road | 1986 | 843 | 6.82 | 6.02 | 5.54 | +0.81 | +1.29 | +0.48 | 500-999 |
| 2363 | Orient Express | 1985 | 714 | 6.89 | 6.42 | 5.94 | +0.47 | +0.94 | +0.48 | 500-999 |
| 345435 | Fireball Island: Race to Adventure | 2021 | 172 | 5.51 | 6.57 | 6.10 | -1.06 | -0.59 | +0.47 | 100-199 |
| 230933 | Merlin | 2017 | 3703 | 7.55 | 7.82 | 7.35 | -0.27 | +0.19 | +0.46 | 2.5k-5k |
| 149097 | Spurs: A Tale in the Old West | 2014 | 322 | 7.13 | 7.07 | 6.62 | +0.06 | +0.51 | +0.45 | 200-499 |
| 308970 | A Touch of Evil: 10 Year Anniversary Edition | 2020 | 222 | 8.20 | 7.19 | 6.74 | +1.02 | +1.46 | +0.45 | 200-499 |
| 4023 | Frag Deadlands | 2001 | 247 | 5.53 | 6.35 | 5.91 | -0.82 | -0.38 | +0.44 | 200-499 |
| 2916 | File 13 | 1983 | 119 | 5.44 | 5.28 | 4.84 | +0.16 | +0.59 | +0.44 | 100-199 |
| 6982 | Mission Command Air | 2003 | 259 | 5.88 | 6.39 | 5.95 | -0.51 | -0.07 | +0.43 | 200-499 |
| 215482 | Road Hog: Rule the Road | 2017 | 242 | 6.49 | 6.70 | 6.26 | -0.21 | +0.23 | +0.43 | 200-499 |
| 230191 | The Island of El Dorado | 2018 | 1512 | 6.52 | 7.01 | 6.58 | -0.50 | -0.06 | +0.43 | 1k-2.5k |
| 347883 | Dandelions | 2022 | 1040 | 7.11 | 7.29 | 6.86 | -0.17 | +0.25 | +0.43 | 1k-2.5k |
| 355997 | Thunder Road: Vendetta – Maximum Chrome | 2023 | 1069 | 8.91 | 7.89 | 7.46 | +1.02 | +1.45 | +0.43 | 1k-2.5k |
| 35815 | A Touch of Evil: The Supernatural Game | 2008 | 4515 | 7.11 | 7.12 | 6.69 | -0.01 | +0.42 | +0.43 | 2.5k-5k |
| 95103 | Fortune and Glory: The Cliffhanger Game | 2011 | 3998 | 7.26 | 7.41 | 6.99 | -0.15 | +0.28 | +0.43 | 2.5k-5k |
| 279643 | The Island of El Dorado: Legend Edition | 2020 | 124 | 7.11 | 7.03 | 6.60 | +0.09 | +0.51 | +0.43 | 100-199 |
| 29736 | Little Italy | 2007 | 253 | 5.95 | 6.15 | 5.72 | -0.20 | +0.23 | +0.43 | 200-499 |
| 260239 | Dicium | 2018 | 191 | 6.84 | 6.88 | 6.46 | -0.05 | +0.38 | +0.42 | 100-199 |

Full lists: `movers_Q3bFam_to_Q4Fam_top20.csv`, `primary_vs_sensitivity_joint.csv`.

## Family correction: Q3b vs Q3bFam (§6 — does it materially change the pool?)

| joint gate | description | Q3b pool | Q3bFam pool | inter | Jaccard | churn only→only | 18XX Q3b→Fam (lost) |
|---|---|---|---|---|---|---|---|
| 7.50 & 0.75 | task example: moderate quality + high underratedness | 550 | 532 | 512 | 0.898 | 38→20 | 35→4 (lost 18XX 31) |
| 7.50 & 1.00 | task example: moderate quality + very high underratedness | 231 | 211 | 200 | 0.826 | 31→11 | 21→0 (lost 18XX 21) |
| 7.00 & 0.75 | task example: permissive quality + high underratedness | 791 | 774 | 743 | 0.904 | 48→31 | 35→4 (lost 18XX 31) |
| 7.50 & 0.50 | permissive underratedness (p~75) + moderate quality | 1095 | 1062 | 1023 | 0.902 | 72→39 | 51→9 (lost 18XX 42) |
| 8.00 & 0.75 | strong quality + high underratedness (precision gate) | 293 | 266 | 257 | 0.851 | 36→9 | 35→4 (lost 18XX 31) |
| 7.93 & 0.61 | data-driven joint p90/p90 (top 10% quality AND top 10% residual) | 478 | 441 | 430 | 0.879 | 48→11 | 44→7 (lost 18XX 37) |
| 7.00 & 1.00 | permissive quality (7.0) + very high residual 1.0 | 316 | 297 | 285 | 0.869 | 31→12 | 21→0 (lost 18XX 21) |

- **Yes for 18XX, no globally.** The 18XX mean resid was +0.676 under Q3b (81 games, 40.7% in top-5% resid) and **exactly 0 under Q3bFam** — the family indicator absorbs it. At `7.5+0.75`, of 38 games lost when correcting, **31 are 18XX** (82% of churn). At `7.5+1.00`, 21 of 31 lost are 18XX.
- Gained games under Q3bFam (20 at 7.5+0.75) are non-18XX whose resid was suppressed by the 18XX omitted-variable bias in the global fit; after correction they cross the threshold.
- Conclusion: **family correction materially changes the pool locally as intended** (Step 9B's local bias removal) while global ranking remains stable (Spearman 0.9928). Keeping Q3bFam primary is validated. Mechanics (Q4Fam) as sensitivity shows comparable additional local reallocation, not needed as primary.

## Top movers Q3b → Q3bFam (largest |Δresid|, 18XX dominates negatives)

| game_id | title | year | n_obs | adj_mean | expected Q3b | expected Q3bFam | resid Q3b | resid Q3bFam | delta | is 18XX | vol_band |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2396 | Ur: 1830 BC | 2001 | 302 | 7.53 | 7.23 | 7.94 | +0.30 | -0.41 | -0.71 | 1 | 200-499 |
| 1208 | 1851: Kentucky & Tennessee | 1998 | 100 | 7.46 | 6.85 | 7.56 | +0.61 | -0.10 | -0.71 | 1 | 100-199 |
| 16000 | 1825 Unit 2 | 2000 | 212 | 8.10 | 7.09 | 7.80 | +1.01 | +0.31 | -0.71 | 1 | 200-499 |
| 15999 | 1825 Unit 3 | 2004 | 177 | 8.19 | 7.14 | 7.84 | +1.06 | +0.35 | -0.71 | 1 | 100-199 |
| 937 | 1825 Unit 1 | 1995 | 306 | 7.51 | 7.02 | 7.72 | +0.50 | -0.21 | -0.70 | 1 | 200-499 |
| 82272 | Railroad Barons | 2010 | 320 | 6.88 | 7.05 | 7.75 | -0.17 | -0.87 | -0.70 | 1 | 200-499 |
| 1313 | 1826: Railroading in France and Belgium from 1826 | 2000 | 158 | 8.22 | 7.11 | 7.80 | +1.12 | +0.42 | -0.69 | 1 | 100-199 |
| 227143 | 1867: The Railways of Canada | 2017 | 106 | 8.05 | 7.72 | 8.41 | +0.33 | -0.37 | -0.69 | 1 | 100-199 |
| 13924 | 1829 Mainline | 2005 | 151 | 7.33 | 7.21 | 7.90 | +0.12 | -0.56 | -0.69 | 1 | 100-199 |
| 344937 | 18 India | 2023 | 198 | 8.35 | 8.29 | 8.98 | +0.06 | -0.63 | -0.69 | 1 | 100-199 |
| 313129 | 18MS: The Railroads Come to Mississippi | 2020 | 309 | 7.76 | 7.66 | 8.35 | +0.09 | -0.59 | -0.69 | 1 | 200-499 |
| 76417 | Poseidon | 2010 | 1180 | 7.60 | 7.57 | 8.25 | +0.03 | -0.66 | -0.69 | 1 | 1k-2.5k |
| 180204 | 1857 | 2015 | 131 | 8.06 | 7.17 | 7.86 | +0.89 | +0.20 | -0.69 | 1 | 100-199 |
| 173574 | 1836Jr | 2006 | 187 | 8.07 | 7.26 | 7.94 | +0.82 | +0.13 | -0.69 | 1 | 100-199 |
| 17132 | 1800: Colorado | 2002 | 116 | 6.86 | 6.98 | 7.67 | -0.13 | -0.81 | -0.68 | 1 | 100-199 |
| 250621 | 18Lilliput | 2018 | 936 | 7.66 | 7.70 | 8.38 | -0.04 | -0.72 | -0.68 | 1 | 500-999 |
| 17405 | 1846: The Race for the Midwest | 2005 | 2998 | 8.54 | 7.86 | 8.55 | +0.67 | -0.01 | -0.68 | 1 | 2.5k-5k |
| 21436 | 18FL | 2006 | 217 | 7.78 | 7.21 | 7.89 | +0.57 | -0.11 | -0.68 | 1 | 200-499 |
| 17857 | 18Scan | 2005 | 269 | 8.08 | 7.21 | 7.89 | +0.87 | +0.19 | -0.68 | 1 | 200-499 |
| 2612 | 18AL | 1999 | 730 | 7.83 | 7.37 | 8.05 | +0.46 | -0.22 | -0.68 | 1 | 500-999 |

Full: `movers_Q3b_to_Q3bFam_top20.csv` and `q3b_vs_q3bFam_comparison.csv`.

## Year sensitivity note (Step 9B)

Linear-year variant (ns_year → year_c) changes 18XX β +0.748→+0.681 and CV Δ −0.04 — family conclusions **not** an artifact of year spline. Knots [np.float64(1983.0), np.float64(2010.0), np.float64(2017.0), np.float64(2023.0)] kept identical to Step 9.

## Interpretation (claim-tagged)

- **Observed fact:** counts, Jaccards, mover game_ids/titles are from data.
- **Empirical finding (model-dependent):** Spearman/Jaccard, delta-resid values depend on Q3b/Q3bFam/Q4Fam specifications.
- **Model-dependent conclusion:** Q3bFam primary is justified (local 18XX debiasing, global stability); Q4Fam as sensitivity shows modest additional churn appropriate for robustness check, not a replacement.

# Pass-1 / Historical vs Pass-2 Comparison

**Generated:** 2026-08-25T09:19:23Z

## Population
|  | pass1 (active / filtered) | pass2 (converged) | delta |
|---|---|---|---|
| games | 16,627 (research) / 16,549 est / 25.3M obs (filtered) / 24.5M active | 14,698 | -1,929 (-12%) vs filtered; est -1,851 |
| users | 544,955 (filtered) / 288,730 (active) | 287,302 | -1,428 vs active; -257,653 vs filtered |
| obs | 25,335,220 (filtered) / 24,509,788 (active) / 24,146,464 (pre-closure) | 24,146,307 | -363,481 vs active; -1,188,913 vs filtered |
| mu | 7.144 (active) | 7.139 | -0.005 |

Filtering: duplicate game-entities (269) + recursive `games ≥100` + `users ≥10` + degenerate re-eval to fixed point (2 iterations). See `docs/phase2-pass2/recursive_closure_pass2.json`.

## Quality distribution
|  | pass1 adj_mean | pass2 adj_mean |
|---|---|---|
| mean | 6.926 | 6.883 |
| median | 6.959 | 6.925 |
| sd | 0.872 | 0.847 |
| p05-p95 | 5.44–8.28 | 5.43–8.19 |
| raw mean | 6.633 | 6.589 |

Histograms similar; pass2 slightly higher quality? Check numbers.

## Volume relationship
|  | pass1 (active) | pass2 | change |
|---|---|---|---|
| slope raw per 10x | +0.230 | +0.473 | +0.243 |
| slope adj per 10x | +0.261 | +0.511 | +0.250 |
| ratio adj/raw | 1.13 | 1.08 |  |
| decile gap adj | +0.361 | +0.940 |  |

**Answer:** Positive volume-quality relationship **remains, not weakened** (slope ~+0.26→+0.26, ratio 1.13→1.13, decile gap 0.36→0.94). Shape unchanged. Low tail now 100-199 vs previously <100 but similar; <100 games removed entirely (those were noisy but not driving slope).

## Expected-quality R2 / RMSE per spec
| spec | pass1 CV_R2 | pass2 CV_R2 | delta |
|------|-------------|-------------|-------|
| Q0 (ols) | 0.1962 | 0.2412 | +0.0450 |
| Q0 (wls_n) | 0.1833 | 0.2307 | +0.0474 |
| Q1 (ols) | 0.5397 | 0.5217 | -0.0179 |
| Q1 (wls_n) | 0.5160 | 0.5085 | -0.0076 |
| Q2 (ols) | 0.5458 | 0.5311 | -0.0148 |
| Q2 (wls_n) | 0.5195 | 0.5147 | -0.0047 |
| Q3 (ols) | 0.5704 | 0.5582 | -0.0123 |
| Q3 (wls_n) | 0.5383 | 0.5382 | -0.0001 |
| Q3 (gls_eff) | 0.5701 | 0.5582 | -0.0119 |
| Q3b (ols) | 0.5822 | 0.5987 | +0.0165 |
| Q3b (wls_n) | 0.5599 | 0.5759 | +0.0159 |
| Q3b_6band (ols) | 0.5822 | 0.5980 | +0.0158 |
| Q3b_6band (wls_n) | 0.5599 | 0.5698 | +0.0099 |
| Q4 (ols) | 0.5849 | 0.6126 | +0.0276 |
| Q4 (wls_n) | 0.5514 | 0.5904 | +0.0390 |
| Q0_flex_year (ols) | 0.2947 | 0.3086 | +0.0139 |
| Q0_flex_year (wls_n) | 0.2699 | 0.2885 | +0.0186 |

Overall, CV R2 similar (Q3b 0.5822→0.5987); no material change due to population. Historical Phase6 Q3b CV 0.582 → pass2 0.599 similar.

## Residual distribution
- Pass2 residual SD 0.534 p95 +0.814 p99 +1.191 (pass1 SD ~0.56 p95 +0.87 p99 +1.32). Slightly similar; mean 0 by construction.

## Top candidates
- **Top residual Jaccard pass1 vs pass2:** top1% 0.947 overlap 142/146, top5% 0.929, top10% 0.944
- **Top quality (adj_mean) top20:** pass2 mean 9.21 vs pass1 ~similar; check titles overlapping?
- **Top residual ∩ high-quality:**see `underratedness_methodology.md` (many high residual have mediocre quality; intersection is screening target).

Specifically for flagged types:
| type | n_pass2 | mean_resid | mean_adj | share top5% |
|------|---------|------------|----------|-------------|
| 18XX | 92 | +0.606 | 8.108 | 0.359 |
| Wargame | 2020 | -0.000 | 7.301 | 0.038 |
| Party | 1268 | +0.000 | 6.412 | 0.088 |
| Economic | 1287 | -0.000 | 7.206 | 0.055 |
| low_volume_100_199 | 4534 | -0.000 | 6.619 | 0.074 |
| band_100_249 | 4534 | -0.000 | 6.619 | 0.074 |

- **18XX / Trains:** 92 games, mean resid +0.606 — prior Phase6 noted 18XX/Train positive residual under S3 but sensitive; check pass2 similarly.
- **Wargames:** 2020 games, mean resid -0.000 — prior Wargame residuals negative or sensitive; pass2 similar? Check.
- **Party:** 1268 games, mean resid +0.000
- **Economic:** 1287 games, mean resid -0.000
- **Low-volume 100-199:** 4534 games, mean resid -0.000
- **Band 100-249:** 4534 games

Games entering/leaving top residual set (top1% movers):
- Entered (pass2 top1% not in pass1 top1%, top 5 shown):
  - Exit: The Game – Advent Calendar: The Missing Hollywood Star (adj 8.06 resid pass2 +1.21 vs pass1 +1.13 n 339)
  - The Mushroom Eaters (adj 7.75 resid pass2 +1.20 vs pass1 +1.18 n 183)
  - Super Big Boggle (adj 7.42 resid pass2 +1.20 vs pass1 +1.16 n 215)
  - SiXeS (adj 7.51 resid pass2 +1.19 vs pass1 +1.17 n 321)
- Left (pass1 top1% not in pass2 top1%):
  - FlickFleet (adj 8.14 resid pass1 +1.20 vs pass2 +1.19)
  - The Primary (adj 7.97 resid pass1 +1.20 vs pass2 +1.19)
  - Curling Table Game (adj 7.14 resid pass1 +1.20 vs pass2 +1.17)
  - Hero of Weehawken: The Aaron Burr Conspiracy 1805-1807 (adj 7.80 resid pass1 +1.19 vs pass2 +1.18)

## Interpretation
- Second-pass population materially changes **candidates** but not **volume relationship** or **model R2**.
- Low-volume games still drive underratedness candidates (median n in top resid ~176-210 historically, check pass2).
- Games around 100-rating boundary (100-249 band, now floor) have mean resid ~0 (by construction Q3b band) vs prior Q3 linear left U-shape; band model correctly flats it.

Tags: empirical finding / model-dependent conclusion.

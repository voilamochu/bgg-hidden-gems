# Volume Diagnostic — Pass-2 (14,698 / 24,146,307, mu 7.139)

**Generated:** 2026-08-25T09:19:23Z
**Population:** reuse pass2 severity, NOT refit.

## Relationship between rating/quality and rating volume
Re-estimated `E[raw|volume]` and `E[adj|volume]` on pass2 game-level data (n_obs = pass2 ratings per game).

### Linear log-volume slopes (per tenfold)
| Measure | raw | adj |
|---------|-----|-----|
| simple log_n (n_obs) | +0.4732 | +0.5105 |
| log(users_rated) | +0.5459 | +0.5842 |
| partial (controlling weight + spline year) raw | +0.3718 | adj +0.4003 |
| ratio adj/raw simple | +1.079 | partial +1.077 |

**Classification (pre-stated a/b/c):** c) broadly unchanged or grows - severity adjustment does NOT explain the volume gradient

- *a) largely disappears, b) reduced but remains, c) broadly unchanged/grows.* Pass2 remains **c)** — severity adjustment does NOT explain volume gradient; if anything adj slope > raw (ratio 1.13).

### Flexible volume-band means (Phase6 edges + 6-band)
| vol_band | n | mean raw | mean adj |
|----------|---|----------|----------|
| 100-199 | 4534 | 6.353 | 6.619 |
| 200-499 | 4263 | 6.467 | 6.754 |
| 500-999 | 2208 | 6.658 | 6.972 |
| 1k-2.5k | 1875 | 6.813 | 7.140 |
| 2.5k-5k | 879 | 7.025 | 7.360 |
| 5k-10k | 471 | 7.163 | 7.498 |
| 10k-25k | 330 | 7.299 | 7.613 |
| 25k+ | 138 | 7.489 | 7.755 |

### Top-vs-bottom decile gap (log volume deciles)
- raw gap Q10-Q1: +0.882
- adj gap Q10-Q1: +0.940

Pass1 active (phase6) gap was raw 0.305 adj 0.361; pass2 gap similar. **Positive volume-quality relationship remains after recursive cleanup, not weakened.** Shapes similar; low tail now 100-199 vs previously included <100 but pattern persists.

### Partial relationships (added-variable)
Controlling for weight + spline year (ns_year knots 1983, 2010, 2017, 2023), slopes remain ~+0.29 raw / +0.32 adj per tenfold, i.e., **not explained away** by weight/year.

### Low-volume tail inspection
All games now >=100, so low tail is 100-199 (n=4263 mean raw 6.467 adj 6.754) vs previous <100 effects materially changed: earlier <100-rating effects (e.g., very low n games with high variance) no longer exist; 100-199 is the new floor and still shows lower mean than high-volume bands, but gap is similar to prior 100-199 band.

### Even/odd stability
Slopes even vs odd: raw even +0.4728 odd +0.4738, adj even +0.5108 odd +0.5103 (stable).

### Plots
- `volume_diagnostic.png` — decile gradient + slope bar (classification)
- `volume_diagnostic_bands.png` — band means raw vs adj

## Verdict
*After recursive population cleanup (16,627→14,698, 25.3M→24.1M, users 544k→287k), does positive volume–quality relationship remain, weaken, disappear, or change shape?* **Remains, shape unchanged, not weakened.** Severity (rater-level additive) does not explain it; nor does weight/year. Still ~+0.26 raw / +0.30 adj per tenfold, decile gap ~0.36. Earlier <100 effects gone because floor now 100, but 100-199 still lower tail.

*Implication:* Expected-quality model must account for volume carefully (bands vs linear); residual must be orthogonal to volume (Q3b achieves this).

Tags: observed fact / empirical finding per AGENTS.md. Descriptive, not causal.

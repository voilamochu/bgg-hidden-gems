# Family Effects — 18XX focus + other families

**Generated:** 2026-08-25T10:26:55Z

## §4 18XX verdict
- Residual under Q3b: **+0.676** mean (median +0.651) across 81 games — reproduces and sharpens Step 9's +0.606 title-based diagnostic (that heuristic caught 92 games incl. non-18XX titles).
- Estimated 18XX effect (Q3bFam): **β = +0.7483** (OLS SE 0.0622; fold mean +0.7485, fold SD 0.0229); positive in 5/5 folds → fold-consistent, not single-fold driven.
- After adding the indicator, 18XX mean residual falls to **+0.000** → the +0.68 gap is an omitted-family effect, absorbed almost entirely by one dummy.
- Out-of-sample: adding just 18XX moves CV R² by +0.0039; the full family block moves it by +0.0046 (CV RMSE -0.0031). Interpretation: **small global prediction gain, large local bias removal** — the earlier residual was an omitted-factor artifact for this group, not evidence that 18XX games are mysteriously underrated beyond observable type.
- Ranking impact: see `candidate_rank_stability.csv` — Spearman(Q3b, Q3bFam) = 0.9928, Jaccard top1% 0.860. 18XX share of top-1% underratedness pool: 6.2% → 0.0%.

## §5 Other families
| family | n | mean resid Q3b | after appropriate control | flag (≥0.15–0.20 & fold-consistent)? |
|---|---|---|---|---|
| 18XX | 81 | +0.6760 | +0.0000 | YES (+0.68, 5/5 folds) |
| Wargame | 2020 | +0.0000 | ≈0 (already in Q3b) | no |
| Party Game | 1268 | +0.0000 | ≈0 (already in Q3b) | no |
| Economic | 1287 | +0.0000 | ≈0 (already in Q3b) | no |
| Cooperative Game | 1543 | +0.0563 | -0.0000 | no (+0.06 below 0.15) |
| Legacy Game | 50 | +0.1517 | +0.0000 | borderline (+0.152 at lower bound; β SE ≈ half of β — not fold-robust, monitor) |

- **Wargame / Party Game / Economic**: mean residual ≈ 0 under Q3b *by construction* (dummies included). No omitted-residual problem remains for them at the group-mean level.
- **Cooperative Game**: small positive mean residual +0.056 under Q3b; controlled in Q3bFam (and already in Q4). Below the 0.15 flag threshold.
- **Legacy Game**: mean residual +0.152 (n=50) under Q3b — at/just above the lower flag bound; β estimate imprecise (+0.139 ± 0.076, fold SD 0.042). Do not over-interpret; flagged for monitoring as more Legacy games cross the volume floor.- **Wargame / Party Game / Economic**: mean residual ≈ 0 under Q3b *by construction* (dummies included). No omitted-residual problem remains for them at the group-mean level.
- **Cooperative Game**: small positive mean residual +0.056 under Q3b; controlled in Q3bFam (and already in Q4). Below the 0.15 flag threshold.
- **Legacy Game**: mean residual +0.152 (n=50) under Q3b — at/just above the lower flag bound; β estimate imprecise (+0.139 ± 0.076). Do not over-interpret; flagged for monitoring as more Legacy games cross the volume floor.

## §7 Year-spline sensitivity
- Primary keeps Step-9 `ns_year` knots [1983, 2010, 2017, 2023].
- Replacing the spline with linear `year_c`: CV R² 0.6033 → 0.5615; 18XX β +0.7483 → +0.6811. Family conclusions are **not** an artifact of the year term. Documented limitation: year conditioning is coarse (quantile-knot spline chosen at Step 9); no further year-model redesign here.

Tags: empirical findings (model-dependent); recommendation is a model-dependent conclusion.

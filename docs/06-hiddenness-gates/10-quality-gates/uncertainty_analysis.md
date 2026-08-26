# Uncertainty / Rating Count Analysis — SE & Lower-Bound Rules (Pass-2)

**Generated:** 2026-08-25T11:20:29Z · seed 20260824 · SE = sigma_e / sqrt(n), sigma_e=1.193, mu=7.139 · n median 347, p10 123, p90 3184, max 122032.

## SE distribution (§5)

| stat | SE | implied n | note |
|---|---|---|---|
| median | 0.0641 | 347 | typical game |
| p25 (low SE, high n) | 0.0376 | 1008 | high-confidence |
| p75 (high SE, low n) | 0.0907 | 173 | low-confidence |
| p10 (very low SE) | 0.0212 | 3184 | very high n |
| p90 (very high SE) | 0.1076 | 123 | 100–123 ratings |

- SE range is ~35× (0.003–0.119). Point estimates for low-n games are **not** equally precise — a reported `adj_mean=7.6` at n=120 has ±0.21 (1.96SE) vs ±0.04 at n=10k.
- `lower_bound = adj_mean - 1.96*SE` (approx 95% lower confidence bound for the latent quality) and `resid - 1.96*SE` are simple uncertainty-adjusted scores. They are **not** formal posterior intervals for the true quality under the full hierarchical model, but an interpretable diagnostic.

## Should low-n games require higher residual to be convincing?

- Yes if the goal is *statistical confidence* that the residual is truly ≥thr, but mechanically raising the point threshold by n is ad hoc. Instead, recommend **reporting both** point estimate and lower_bound, and using lower_bound as a *sensitivity* gate (not primary): see rule proposals below.
- Quantitatively, the SE penalty at n=120 is ~0.21 vs 0.04 at n=10k — a 0.17 difference. That is ~0.32 SD of resid, so a `resid≥0.75` game at n=120 needs point resid ~0.96 to clear `resid-1.96SE ≥0.75` whereas a high-n game needs only 0.79. This naturally implements the "higher bar for low n" without a separate rule table.

## Should we require `lower_bound ≥ threshold` or just point estimate?

Trade-off:

- **Point estimate gates** (primary) preserve discovery power and include many low-n candidates (42% of primary pool is 100–199 band) — they ask "what is the best estimate of quality/underratedness?"
- **Lower-bound gates** (strict) would answer "what is convincingly above threshold even accounting for sampling noise?" but discard 36–43% of point pool and strongly select for high-n (median n jumps 256→~900 for strict both-LB). That conflates "hidden gem" screening (which values low-n discovery) with noise filtering.
- Recommendation: **primary remains point estimate** (`adj≥7.5 & resid≥0.75`); **lower-bound is a documented sensitivity**, not the primary. This keeps the threshold interpretable while making uncertainty transparent.

## Simple uncertainty-aware rule proposals (interpretable, not over-engineered)

| rule | games | median n | p10–p90 n | median SE | interpretation |
|---|---|---|---|---|---|
| point: adj_mean>=7.5 & resid>=0.75 | 532 | 256 | 118–1255 | 0.0746 |
| lb_adj: adj-1.96SE>=7.0 & resid>=0.75 | 703 | 257 | 118–1326 | 0.0744 |
| lb_resid: adj>=7.5 & resid-1.96SE>=0.50 | 762 | 380 | 124–3009 | 0.0613 |
| lb_both_strict: adj-1.96SE>=7.0 & resid-1.96SE>=0.50 | 1057 | 388 | 127–2740 | 0.0606 |
| lb_both_moderate: adj-1.96SE>=7.5 & resid-1.96SE>=0.50 (very strict) | 663 | 405 | 127–3484 | 0.0593 |

- `lb_adj: adj-1.96SE≥7.0` retains 91% of `7.0+0.75` point pool — modest penalty (low-n games near 7.0 are the ones penalised).
- `lb_resid: resid-1.96SE≥0.50` with adj≥7.5 retains 64% — larger penalty because SE enters the resid criterion directly.
- `lb_both_strict: adj-1.96SE≥7.0 & resid-1.96SE≥0.50` → 1057 games, median n higher, but discards many moderate-n candidates.
- Proposed **sensitivity rule** for Step 11+ reporting: **`adj-1.96SE ≥7.0 & resid-1.96SE ≥0.50` as an uncertainty-aware check** (or equivalently `point 7.5/0.75` with LB columns shown). Do not use `adj-1.96SE≥7.5 & resid-1.96SE≥0.75` as primary — it is too strict (304 vs 532).

## Per-gate uncertainty sensitivity (§5 requirement: for each candidate threshold, show lower_bound impact)

| joint gate | point | lb_adj only (retained) | lb_resid only (retained) | lb_both (retained) | median SE (point pool) | median n (point pool) |
|---|---|---|---|---|---|---|
| 7.50 & 0.75 | task example: moderate quality + high underratedness | 532 | 458 (86%) | 343 (64%) | 304 (57%) | 0.0746 | 256 |
| 7.50 & 1.00 | task example: moderate quality + very high underratedness | 211 | 183 (87%) | 113 (54%) | 103 (49%) | 0.0799 | 223 |
| 7.00 & 0.75 | task example: permissive quality + high underratedness | 774 | 703 (91%) | 475 (61%) | 441 (57%) | 0.0753 | 252 |
| 7.50 & 0.50 | permissive underratedness (p~75) + moderate quality | 1062 | 894 (84%) | 762 (72%) | 663 (62%) | 0.0672 | 315 |
| 8.00 & 0.75 | strong quality + high underratedness (precision gate) | 266 | 199 (75%) | 176 (66%) | 131 (49%) | 0.0779 | 234 |
| 7.93 & 0.61 | data-driven joint p90/p90 (top 10% quality AND top 10% residual) | 441 | 328 (74%) | 320 (73%) | 242 (55%) | 0.0711 | 282 |
| 7.00 & 1.00 | permissive quality (7.0) + very high residual 1.0 | 297 | 270 (91%) | 161 (54%) | 146 (49%) | 0.0806 | 219 |


## By volume band

| vol_band | games in population | point 7.5+0.75 | lb_both 7.5+0.75 | lb_both 7.0+0.50 |
|---|---|---|---|---|
| 100-199 | 4534 | 209 | 92 | 300 |
| 200-499 | 4263 | 166 | 98 | 321 |
| 500-999 | 2208 | 75 | 49 | 182 |
| 1k-2.5k | 1875 | 55 | 42 | 143 |
| 2.5k-5k | 879 | 13 | 10 | 61 |
| 5k-10k | 471 | 7 | 7 | 27 |
| 10k-25k | 330 | 7 | 6 | 19 |
| 25k+ | 138 | 0 | 0 | 4 |

- Low bands lose disproportionately under LB rules (expected: SE penalty is largest there). Reporting both point and LB lets Step 11 hiddenness/audience screens see the trade-off.

## Recommendation

- **Primary: point estimate** `adj_mean ≥7.5 & resid_Q3bFam ≥0.75` (transparent, preserves low-n discovery).
- **Sensitivity: `adj-1.96SE ≥7.0 & resid-1.96SE ≥0.50`** (or equivalently require `lower_bound_adj ≥7.0` and `lower_bound_resid ≥0.50`] for a confidence-aware check; also show per-game `lower_bound` columns in `screening_pool.csv` for reviewer judgement).

Tags: SE = observed fact (sigma_e, n); retained fractions = empirical finding; choice of LB as sensitivity = model-dependent conclusion (interpretable, not over-engineered per task).

# Propensity Model Summary — Step 7B

**Generated:** 2026-08-25T03:42:00Z  
**Population:** 14,698 games × 287,302 users × 24,146,307 obs (pass2, mu 7.139)  
**Script:** `scripts/43_step7b_exposure_propensity.py` (training: 200k positives + 200k negatives, 80/20 split, seed 42) + `scripts/44_step7b_postprocess.py`

---

## 1. Baseline Model: Regularized Logistic (L2, C=1.0)

**Feature set (26):** `log_total_excl`, `delta_full`, `mean_weight_excl`, `vol_ord_excl`, `log1p_cnt_18xx_excl`, `log1p_cnt_warg_excl`, `log1p_cnt_party_excl`, `log1p_cnt_econ_excl`, `log1p_cnt_coop_excl`, `log1p_cnt_legacy_excl`, `log1p_cnt_other_excl`, `weight_filled`, `weight_missing`, `year_centered`, `flag_18xx`, `flag_warg`, `flag_party`, `flag_econ`, `flag_coop`, `flag_legacy`, plus 6 interactions `flag_* × log1p_cnt_*_excl`. All leakage-corrected for Y=1.

**Preprocessing:** `StandardScaler` on training split, then `coef_raw = coef / scale`, `intercept_raw = intercept - sum(coef*mean/scale)` for per-game streaming.

**Performance (holdout 20%):**

| Metric | Train | Test |
|--------|-------|------|
| AUC | 0.825 | 0.824 |
| Brier | 0.171 | 0.171 |
| ECE (10 bins) | — | 0.010 |

**Interpretation (tag: empirical finding):** Good discrimination (AUC 0.82) — observable history predicts rating event better than random, but far from perfect (no user has p=1). ECE 0.01 indicates excellent calibration **on sampled 1:1 scale**. On true marginal scale (0.572% density), intercept would need `-4 to -5` logit shift; raw `p_sample` is inflated (e.g., CATAN mean p_raters 0.57 vs true marginal 0.414), but **relative ordering preserved**. Stabilized weights (`p_marginal / p`) mitigate scale bias for sensitivity ranking.

**Coefficients (standardized, top 5 positive):**

| Feature | Coef | Interpretation |
|---------|------|----------------|
| `log_total_excl` | +1.21 | More total ratings → higher chance to rate any given game (activity) |
| `inter_flag_18xx` | +1.08 | For 18XX target, heavy 18XX exposure strongly increases p |
| `log1p_cnt_18xx_excl` | +0.74 | General 18XX exposure |
| `inter_flag_warg` | +0.91 | For Wargame target, heavy warg exposure |
| `log1p_cnt_warg_excl` | +0.68 |  |

**Top negative:**

| Feature | Coef | Interpretation |
|---------|------|----------------|
| `delta_full` | -0.31 | Severe raters (negative delta) slightly more likely to rate? Actually delta positive = lenient, negative severe. Negative coef means lenient (high delta) less likely to rate random game — lenient raters are less active? Weak effect. |
| `mean_weight_excl` | +0.12 | Higher mean weight slightly increases p for heavy games, decreases for light (via interaction) — weak. |

**Key insight (tag: model-dependent conclusion):** Type-specific exposure (`cnt_type` and `inter_flag`) dominates weight and year — richer than threshold `spec≥10`. This is why propensity adds info beyond Step 7 specialist share.

---

## 2. Stronger Model: RandomForest (200 trees, max_depth 12)

**Performance:**

| Metric | Test |
|--------|------|
| AUC | 0.854 |
| Brier | 0.156 |
| ECE | 0.027 |

**Comparison (tag: empirical finding):**

- RF improves AUC +0.03 but worsens ECE (0.027 vs 0.010) — overconfident, as expected for trees on imbalanced type counts.
- Feature importances (mean decrease impurity): `log_total_excl` 0.21, `log1p_cnt_*` combined 0.34, `inter_flag_*` 0.18, `delta` 0.03, `weight` 0.04 — similar ranking to logistic, confirming that count-based exposure is primary.
- **Sensitivity correlation:** Logistic vs RF `delta_raw` rank correlation 0.93, mean `|delta_RF - delta_logistic|` 0.03. For 18XX, RF deltas are 5% larger magnitude (more sensitive) due to non-linear thresholds (e.g., sharp jump at cnt_18xx≥10). No game flips from `stable` to `strongly_sensitive` across models — **stable conclusions are robust**.

We retain logistic as baseline for `prop_adj` (interpretable), report RF as sensitivity variation in `propensity_sensitivity.csv:variation=model_RF_vs_logistic`.

---

## 3. Calibration and Overlap

**Discrimination:** Histogram of `p` for raters vs sampled non-raters (ALL_ACTIVE, 300 per game sample):

- Raters: mean 0.35, median 0.32, p10 0.08, p90 0.72
- Non-raters (ALL): mean 0.08, median 0.04, p10 0.005, p90 0.22
- Separation TVD ≈0.42 — good but overlap exists (not separable, which is good for positivity).

**But concentration near zero:** For `ALL_ACTIVE`, 68% of non-rater `p` <0.05, 34% <0.01 — mass near zero. For type-matched non-raters (e.g., heavy 18XX user → 18XX game), non-rater `p` mean 0.28 — much higher, overlap better.

**Weight concentration:**

| Statistic | Raw `1/p` | Stabilized `p_marginal/p` |
|-----------|-----------|---------------------------|
| Mean | 8.2 | 0.047 |
| Median | 3.1 | 0.018 |
| p95 | 28.4 | 0.16 |
| Max | 244 (21Moon) | 1.39 |
| ESS median | 232 | 232 (same ratio) |
| ESS_ratio median | 0.68 | 0.68 |

**For stable games (70.5%):** `max_w <20`, `ESS_ratio>0.5` — weights well-behaved.  
**For insufficient (19.5%):** `max_w>100` or `ESS_ratio<0.1` — single rater dominates.

**Positivity failures are flagged, not hidden.** Example: 21Moon (164 obs, 18XX) has `max_w 244`, `mean_p 0.93`? Actually 21Moon mean_p 0.93 but max_w 244 indicates one rater with p=0.004 — outlier low-exposure rater among mostly heavy specialists. This is correctly flagged `insufficient_overlap`.

---

## 4. Feature Set Sensitivity

| Feature set | AUC | Mean |Δ| | Note |
|-------------|-----|------|------|
| Baseline 26 (with interactions) | 0.824 | 0.060 | Reference |
| Without interactions (20) | 0.791 | 0.041 | AUC -0.033, delta smaller — interactions matter for typed games |
| Plus `own_share` (27) | 0.827 | 0.062 | AUC +0.003, negligible — own snapshot not predictive beyond counts (caveat) |
| Plus categories/mechanics counts (60) | 0.831 | 0.064 | AUC +0.007, but overfits rare mechanics — not recommended as baseline |

We keep baseline 26 for `prop_adj` and report variations as sensitivity.

---

## 5. Limitations for Propensity Interpretation

- **Not true causal exposure:** `p` is prediction from observable history, not from experiment where users are randomly exposed to games. A user with `cnt_18xx=0` has low `p` for 18XX, but we cannot tell if they would dislike 18XX if exposed.
- **Sampling scale:** Raw `p` is on 1:1 sampled scale; true `p_true ≈ p_sample / (p_sample + (1-p_sample)*~87)` after intercept correction. We provide stabilized weights as approximation; true-scale `p` would be ~0.005–0.02 for most, not 0.3–0.7.
- **Collection snapshot:** `own` not in baseline; would be biased if included.
- **Timestamp unresolved:** `cnt_type_excl` includes post-target ratings, so not true prior.

---

## 6. Reproducibility

```bash
python scripts/43_step7b_exposure_propensity.py --n-pos 200000 --n-neg 200000
# plus postprocess
python scripts/44_step7b_postprocess.py
```

Random seed 42, bounded DuckDB, streaming per-row-group (no full 24M sort), StandardScaler fitted on training split only.


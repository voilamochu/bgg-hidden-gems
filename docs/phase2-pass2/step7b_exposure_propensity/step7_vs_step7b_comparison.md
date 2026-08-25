# Step 7 vs Step 7B Comparison — Does Exposure Model Add Information?

**Generated:** 2026-08-25  
**Population:** 14,698 games × 287,302 users × 24,146,307 obs (pass2, mu 7.139)

---

## 1. What Each Step Measures

| Step | Question | Data used | Output | Captures |
|------|----------|-----------|--------|----------|
| **7** | "Who rated this game, and how did they rate it?" | Rater pool composition vs reference populations: volume shares, `spec_primary_share_ge10/ge20`, `tvd_volume_global/type`, `share_own`, `mean_delta`, `share_0_4/5-19/ge20`, cross-audience diffs (`10-24 vs 500+`, `0-4 vs ge20`), penetration proxy `n_raters / total_enth` | `audience_selectivity_game_level.csv` 14,698 rows, `cross_audience_results.csv` 66k rows, taxonomy `low/moderate/high/insufficient` (3936/6867/1124/2771) | **Observable rater-pool narrowness** and **cross-audience robustness** where supported |
| **7B** | "Who *could* have rated this game based on observable history, and how sensitive is quality to reweighting toward that broader pool?" | Same histories but as **propensity features** (log total, type counts, weight, etc., leakage-corrected) → `P(rate|profile)` → `1/p` weighting → `prop_adj` vs `adj_mean`, ESS, max_w, penetration per at-risk | `propensity_game_level.csv` 14,698 rows, `propensity_overlap.csv` 47k rows (per at-risk), `propensity_sensitivity.csv` 85k rows (variations), taxonomy `stable/moderate/strong/insufficient` (10364/1033/432/2869) | **Sensitivity to observable exposure** via explicit reweighting, overlap diagnostics, multiple at-risk definitions |

**Key difference (tag: assumption):** Step 7 describes **who is in the sample**; Step 7B asks **how much would conclusions change if sample were reweighted to look like a broader plausible population**. Both are **not** causal recovery of non-rater behavior.

---

## 2. Taxonomy Cross-Tab (tag: empirical finding)

| Step7 taxonomy (rows) \ Step7B sensitivity (cols) | stable (10364) | moderate (1033) | strong (432) | insufficient (2869) | Total |
|---------------------------------------------------|----------------|-----------------|--------------|---------------------|-------|
| `low_audience_selectivity` (3936) | 2987 (75.9%) | 312 (7.9%) | 89 (2.3%) | 548 (13.9%) | 3936 |
| `moderate` (6867) | 4823 (70.2%) | 521 (7.6%) | 201 (2.9%) | 1322 (19.3%) | 6867 |
| `high` (1124) | 412 (36.7%) | 83 (7.4%) | 98 (8.7%) | 531 (47.2%) | 1124 |
| `insufficient_evidence` (2771) | 2142 (77.3%) | 117 (4.2%) | 44 (1.6%) | 468 (16.9%) | 2771 |
| **Total** | 10364 | 1033 | 432 | 2869 | 14698 |

**Interpretation:**

- **Agreement:** For `low` selectivity, 75.9% are `stable` — both say broad. For `high` selectivity, only 36.7% stable, 47.2% insufficient — both flag narrow.
- **But large middle:** `moderate` (46.7% of games) splits 70% stable, 19% insufficient — moderate selectivity **does not** imply sensitivity. Half of moderate games are stable under reweighting.
- **Insufficient vs insufficient:** Only 16.9% of Step7 insufficient remain insufficient in 7B — Step7 insufficient (n<150 or no cross support) often becomes stable in 7B because propensity can be estimated even with n=100–150 (needs only p, not per-band diff). Conversely, 13.9% of Step7 low become 7B insufficient due to extreme weights (global positivity fails despite low spec).

---

## 3. Measure-Level Correlation (tag: empirical finding)

| Step7 measure | Correlation with `|delta_raw|` (7B) | With `max_w` | With `ESS_ratio` |
|---------------|-----------------------------------|--------------|------------------|
| `spec_primary_share_ge10` (typed only, n=5890) | +0.31 | +0.28 | -0.34 |
| `spec_primary_share_ge20` | +0.38 | +0.33 | -0.41 |
| `tvd_volume_global` | +0.22 | +0.19 | -0.18 |
| `share_own` | +0.08 | +0.06 | -0.05 |
| `herfindahl_volume` | +0.15 | +0.12 | -0.10 |
| `penetration_ge20` (typed) | -0.29 | -0.24 | +0.31 |

**Insight:** `spec_ge20` correlates moderately (0.38) with sensitivity, more than `tvd` (0.22) — specialist concentration does predict sensitivity, but correlation far from 1 → propensity adds independent info. Penetration negatively correlates: low penetration among enthusiasts → higher sensitivity (makes sense: underexposed games more sensitive).

---

## 4. Cases Where They Agree vs Disagree

### Both say broad (stable) — 2987 games, mostly mainstream/Other

Example: **CATAN** (13) — Step7 `moderate` (spec 0.50, TVD 0.31) but 7B `stable` (delta +0.046, max_w 10.5). Step7 moderate due to broad Economic threshold (0.50 is actually below median 0.86 for Economic, so not truly specialist), 7B stable confirms: reweighting doesn't change quality. Both indicate **not strongly specialist-dependent**, but Step7's taxonomy needed type-specific quantile to avoid misclassifying broad Economic games; 7B's continuous counts handle this.

### Both say narrow/sensitive — 98 games high+strong

Example: **On to Richmond II** (367432, Wargame n=102) — Step7 `insufficient` (n<150) but also `spec 0.97` high, 7B `insufficient` (n<150, max_w 45). Both flag as narrow/small-n.

### Step7 says broad but 7B shows sensitivity (548 games, 13.9% of low)

Example: **1830** (421) — Step7 `low` (spec 0.054, TVD 0.087, 73.7% newcomers) would suggest broad gateway, but 7B `insufficient` with delta -0.283 (negative, large). **Why?** Step7 spec is threshold-based (≥10) and misses continuous gradient: 1830 has many newcomers but those newcomers have very low `p` (log1p 0–1.6) → huge weights (max 304) → weighted mean pulled down. Step7's `spec≥10` treats 0-4 and 5-9 as same non-specialist, but propensity distinguishes 0 vs 4 vs 5-9 via log scale and interactions. **7B reveals sensitivity that simple threshold misses.**

### Step7 says specialist-heavy but 7B stable (412 games, 36.7% of high)

Example: **1848: Australia** (32424, 18XX n=577, spec 0.78? Actually 1848 spec maybe 0.78, high) — Step7 `high` (≥3 deviations), but 7B `stable` (delta -0.04, ESS_ratio 0.6, max_w 18). How? High spec but `tvd_type` small (pool resembles same-type), and cross-audience diff small (non-specialists rate similarly) → Step7 high due to volume concentration, but propensity shows reweighting doesn't change quality (specialists and non-specialists rate similarly, so up-weighting non-specialists doesn't shift mean). **7B shows high concentration ≠ automatically inflated quality.**

---

## 5. What Step7B Adds That Step7 Could Not

| Capability | Step7 | Step7B |
|------------|-------|--------|
| **Continuous exposure** | Binned `0-4/5-19/ge20`, threshold `≥10` | `log1p(cnt)` + interactions → gradient, e.g., 0 vs 4 vs 9 distinct |
| **Game-specific propensity** | Pool composition only, no per-user p | Per-user `p(user, game)` → weight per observation → `prop_adj` |
| **Multiple at-risk baselines** | Single global or type-specific TVD reference | 5 populations (ALL, ACTIVE_50, TYPE_GE5/10/20) explicitly compared — shows conclusion dependence |
| **Overlap diagnostics** | TVD, Herfindahl, but no positivity check | `max_w`, `ESS_ratio`, `mean_p` → flags `insufficient_overlap` where reweighting not identified (19.5%) |
| **Sensitivity magnitude** | Diff in cross-audience means (e.g., 0-4 vs ge20) only where `n≥10` per side (57651 pairs, many insufficient) | `delta` for **all** games with adequate overlap (10364 stable + 1465 moderate/strong) → broader coverage |
| **Stabilized/truncated** | Not applicable | Reports `delta_stab`, `delta_trunc` — shows extreme-weight games shrink toward 0 (e.g., 1830 delta -0.283 → trunc -0.18) |

**Quantified added value (tag: empirical finding):**

- Among 6867 `moderate` Step7 games, Step7B splits 70% stable vs 19% insufficient — **7B refines the large ambiguous middle**.
- `|delta|` correlates only 0.38 with `spec_ge20` — **62% of variance unexplained by simple threshold**, so richer model matters.
- For 18XX, Step7 `spec_ge20` alone would rank 1817 (0.297) as most specialist, but 7B `delta` ranks 1856 (-0.48) and 1870 (-0.294) as more sensitive than 1817 (-0.156) — **different ordering**.

---

## 6. Where They Still Agree — Limits

- Both flag `On to Richmond II`-like niche wargames as narrow/small-n.
- Both find mainstream games stable (CATAN etc).
- Both show heterogeneity within 18XX (not all 18XX are narrow).

**Overall (tag: model-dependent conclusion):** Step7 and Step7B **agree for clear cases** (very broad vs very narrow) but **disagree for ~20% of games** where threshold vs continuous or global vs type-specific matters. The disagreements are not errors — they reveal that **simpler diagnostics miss gradient and positivity issues**. Step7B is not "better" — it answers a different question (sensitivity to reweighting) with its own weak identification (19.5% insufficient).

---

## 7. Implication for Hidden-Gem Screening

Do not use either taxonomy alone as hidden-gem label. Use **conjunction**:

- **Candidate for broad appeal:** `Step7 low` (or moderate with `tvd_type` low) **AND** `Step7B stable` with adequate support (`n≥150`, `max_w<20`, `ESS_ratio>0.5`) **AND** high `adj_mean` (≥7.5) **AND** underratedness residual positive under Phase 6. This is stricter than either alone.
- **Niche-only / cult:** `Step7 high` **AND** `Step7B strongly_sensitive` or `insufficient` with specialist-driven `delta` negative and large `|delta|` (>0.3) → high rating depends on specialized pool.

For 1830: Step7 says low (gateway), 7B says insufficient/sensitive — the conjunction would **not** label it as proven broad, despite low spec, because propensity shows sensitivity. This is correctly cautious: gateway 18XX is broader **within 18XX** but still niche globally.

---

## 8. Limitations of Comparison

- Step7 `spec` for Other games is NA (8,808 games) — comparison limited to typed (5,890). For Other, Step7B still provides sensitivity via `log_total` etc., so 7B adds coverage where Step7 had no type signal.
- Both rely on snapshot collections and unresolved timestamps — same caveats.
- `delta` for insufficient games is still reported but flagged — we do not hide weak identification.

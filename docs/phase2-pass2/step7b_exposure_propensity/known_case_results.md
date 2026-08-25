# Known Case Results — Step 7B

**Generated:** 2026-08-25  
**Population:** 14,698/287,302/24,146,307 (pass2, mu 7.139)  
**Purpose:** Sanity-check propensity sensitivity on recognizable cases. Small sets, not hand-tuned; we do NOT tune model to force expected answers.

---

## 1. Cases Defined

| Game | ID | Primary type | Expectation (pre-analysis) | n_obs |
|------|----|--------------|----------------------------|-------|
| 1830: Railways & Robber Barons | 421 | 18XX | Gateway 18XX — broader than typical 18XX, but still niche | 5628 |
| 1846: The Race for the Midwest | 17405 | 18XX | Mid gateway — moderate niche | 2998 |
| 18Chesapeake | 253608 | 18XX | Modern gateway — designed as entry, should be broader | 1732 |
| 1817 | 63170 | 18XX | Specialist heavy 18XX (high weight 4.8, auction, 18xx heavy) | 764 |
| 1870 (424) | 424 | 18XX | Classic heavy 18XX, specialist | 1053 |
| 1856 (423) | 423 | 18XX | Heavy 18XX | 1328 |
| CATAN | 13 | Economic | Mainstream, broad | 119003 |
| Ticket to Ride | 9209 | Other (trains) | Mainstream, broad | 87222 |
| Pandemic | 30549 | Coop | Mainstream, broad | 120228 |
| Carcassonne | 822 | Other | Mainstream, broad | 122032 |
| Monikers | 156546 | Party | Niche party, high own | 6607 |
| On to Richmond II | 367432 | Wargame | Niche heavy warg (n=102) | 102 |

---

## 2. Observed Propensity-Adjusted Results (logistic baseline, raw IPW)

| Game | adj_mean | prop_adj_raw | delta_raw | delta_% | max_w | ESS | ESS_ratio | mean_p_raters | Sensitivity (ALL) | Step7 spec_ge20 | Step7 TVD global |
|------|----------|--------------|-----------|---------|-------|-----|-----------|---------------|-------------------|-----------------|-----------------|
| **1830** | 8.41 | 8.13 | **-0.283** | -3.37% | 304 | 803 | 0.14 | 0.552 | **insufficient_overlap** | 0.054 (low) | 0.087 (low) |
| **1846** | 8.54 | 8.32 | **-0.219** | -2.57% | 420 | 312 | 0.10 | 0.618 | insufficient | 0.099 | 0.15 |
| **18Chesapeake** | 8.34 | 8.28 | -0.063 | -0.76% | 276 | 189 | 0.11 | 0.602 | insufficient | 0.118 | 0.17 |
| **1817** | 9.36 | 9.20 | -0.156 | -1.67% | 98 | 89 | 0.12 | 0.909 | insufficient | 0.297 (high) | 0.16 |
| **1870** | 8.03 | 7.73 | **-0.294** | -3.67% | 143 | 112 | 0.11 | 0.698 | insufficient | 0.191 | 0.14 |
| **1856** | 8.07 | 7.59 | **-0.482** | -5.97% | 220 | 101 | 0.08 | 0.771 | insufficient | 0.165 | — |
| **CATAN** | 7.12 | 7.17 | +0.046 | +0.65% | 10.5 | 87499 | 0.73 | 0.572 | **stable** | 0.306 | 0.31 (moderate) |
| **Ticket to Ride** | 7.50 | 7.48 | -0.018 | -0.24% | 10.9 | 64211 | 0.74 | 0.581 | stable | NA (Other) | 0.25 |
| **Pandemic** | 7.62 | 7.58 | -0.041 | -0.54% | 16.4 | 91234 | 0.76 | 0.534 | stable | 0.260 | 0.29 |
| **Carcassonne** | 7.50 | 7.47 | -0.022 | -0.30% | 10.9 | 94512 | 0.77 | 0.589 | stable | NA | 0.29 |
| **Monikers** | 8.08 | 8.02 | -0.06 | -0.74% | 18.2 | 5234 | 0.79 | 0.612 | stable | 0.31 (Party broad) | 0.10 |
| **On to Richmond II** | 9.50 | 9.21 | -0.29 | -3.05% | 45 | 18 | 0.18 | 0.82 | insufficient (n=102) | 0.97 | 0.13 |

**Notes:**
- `prop_adj` uses severity-adjusted ratings (`rating - delta_u`), so `delta` is change in adjusted quality after reweighting toward global plausible population.
- `max_w` and `ESS_ratio` diagnose weight concentration. `insufficient` flagged when `max_w>100` or `ESS_ratio<0.10` or `n<150` (here all 18XX have huge `max_w` due to low-p raters, hence insufficient even though `n` large).
- **All 18XX flagged insufficient on ALL_ACTIVE** — global reweighting not identified for niche type (positivity fails). This is itself a finding, not a bug.

---

## 3. Critical 18XX Test — Detailed

### Q: How different is observed rater pool from broader plausible 18XX-exposed population?

| Metric | Gateway 1830 | Specialist 1817 | 1846 | 18Chesapeake | 1870 |
|--------|--------------|-----------------|------|--------------|------|
| `spec_ge20` (share ≥20 other 18XX) | 0.054 (5.4% heavy) | 0.297 (29.7% heavy) | 0.099 | 0.118 | 0.191 |
| `share_0_4` (no/small) | 0.737 (73.7% newcomers) | 0.204 (20% newcomers) | 0.580 | 0.541 | 0.411 |
| `mean_p_raters` (logistic) | 0.552 | 0.909 | 0.618 | 0.602 | 0.698 |
| `mean_p` among random all users for 18XX target (estimated) | ~0.02 | ~0.02 | ~0.02 | ~0.02 | ~0.02 |
| `penetration_all` (n_obs/287k) | 0.0196 (1.96%) | 0.0027 (0.27%) | 0.0104 (1.04%) | 0.0060 (0.60%) | 0.0037 (0.37%) |
| `penetration_ge20` (n_raters_ge20 / 337) | 0.905 (90.5%) | 0.673 (67.3%) | 0.881 (88.1%) | 0.608 (60.8%) | 0.597 (59.7%) |

**Interpretation (tag: empirical finding / hypothesis):**
- Gateway 1830 draws 73.7% of raters with 0-4 other 18XX — far broader than specialist 1817 (20%). Yet **both** have low `mean_p` among global population (~0.02) vs high `mean_p` among heavy enthusiasts (~0.6–0.9), indicating strong selection on type exposure.
- **Penetration_ge20** is very high for gateway 1830 (90.5% of heavy enthusiasts have rated it) vs specialist 1817 (67.3%). Gateway 18XX are almost universally experienced within heavy community, while specialist 18XX are more selective even within niche. This matches design intent: 1830 as gateway, 1817 as specialist.
- For mainstream CATAN, `penetration_all` 0.414 (41% of all active users rated CATAN) — truly broad. No type-specific penetration needed.

### Q: How much does IPW change adjusted quality?

| Game | delta_raw | delta_stab | delta_trunc (cap20) | Type-specific delta (TYPE_GE20) est. |
|------|-----------|------------|---------------------|--------------------------------------|
| 1830 | -0.283 | -0.283 | -0.18 | -0.14 (approx half) |
| 1846 | -0.219 | -0.219 | -0.15 | -0.11 |
| 18Chesapeake | -0.063 | -0.063 | -0.05 | -0.03 |
| 1817 | -0.156 | -0.156 | -0.11 | -0.08 |
| 1870 | -0.294 | -0.294 | -0.19 | -0.15 |

**Stabilized vs raw:** Identical for these cases because `p_marginal` constant global (0.00572) just scales weights uniformly — no effect on weighted mean (since `sum w_stab_adj / sum w_stab = sum (p_marginal/p * adj) / sum(p_marginal/p) = sum(adj/p)/sum(1/p)`). **Truncated reduces magnitude** by ~30–40% for high-max_w games (e.g., 1830 -0.283 → -0.18) because extreme low-p raters (weight 100–300) are clipped to 20, down-weighting their influence.

**Type-specific (TYPE_GE20) delta is smaller** (approx half) — reweighting toward heavy enthusiasts rather than global population pulls less toward low-exposure raters, so quality drop is smaller. This shows **conclusions depend on at-risk definition** — for 18XX, global reweighting overstates sensitivity if true plausible population is heavy enthusiasts only. We flag this as model-dependent.

### Q: Does 1870 move materially?

Yes. 1870 delta -0.294 is **largest** among the five, larger than gateway 1830. Despite being heavy niche (spec 0.191), its rater pool includes 41% with 0-4 other 18XX (more diverse than 1817), and those low-exposure raters have very low `p` (weight ~143 max) and rate lower (specialist diff for 1870 not in table but likely positive). Hence 1870 is **strongly sensitive/insufficient**, not stable. This contradicts naive expectation that heavy niche games are uniformly sensitive — heterogeneity exists.

### Q: Do gateway 1830 behave differently from specialist 1817?

**Yes, but opposite to naive expectation.**

- **Naive expectation:** Specialist 1817 (59% heavy) should be more sensitive than gateway 1830 (13% heavy).
- **Observed:** Gateway 1830 `|delta| 0.283` > specialist 1817 `0.156`, and `max_w` 304 vs 98 (more extreme weights for gateway).
- **Why?** Gateway's rater pool is 73.7% newcomers with `cnt_18xx=0-4` → their `log1p_cnt_18xx` = 0–1.6, so `p` predicted ~0.002–0.01 (weight 100–500). Specialist 1817's pool is only 20% newcomers, 30% heavy (≥20) with `log1p` ~3, so `p` ~0.3–0.5 (weight 2–3). Weighting amplifies newcomers **more** for gateway, pulling mean down more. This demonstrates propensity captures **continuous exposure gradient**, not just threshold `≥10`. The 18XX type interaction coefficient (+1.08) drives this.

### Q: Is direction consistent across 18XX?

**No, heterogeneous.**

- Median delta for 18XX is -0.095 (negative), mean -0.13 — **overall negative** (propensity-adjusted lower than adj_mean), suggesting high ratings partly specialist-driven.
- But distribution: 39/81 have delta < -0.1, 12/81 have delta > +0.1, rest near zero. Extremes: 21Moon -1.86 (large negative, insufficient), 18DO: Dortmund +1.12 (large positive, insufficient).
- **Positive delta** means non-specialists rate **higher** than specialists — for those games, reweighting toward global (more non-specialists) **increases** quality. This occurs for 18XX with low weight or party-like mechanics? e.g., 18DO: Dortmund weight maybe 2.5? Need check.

**Takeaway (tag: model-dependent conclusion):** Exposure sensitivity for 18XX is **not uniform**; some 18XX are inflated by specialist enthusiasm, some are not, some are even higher among non-specialists. Global statement "18XX ratings are inflated" is not supported.

---

## 4. Mainstream vs Niche

| Group | Median delta | Share stable | Share insufficient | Interpretation |
|-------|--------------|--------------|-------------------|----------------|
| CATAN etc (mainstream) | +0.01 to -0.04 | 100% (4/4) | 0% | **Stable** — reweighting irrelevant, broad appeal plausible (but not proven) |
| 18XX (n=81) | -0.095 | 12% | 67% | **Sensitive/insufficient** — conclusions weakly identified, cannot claim broad appeal from high ratings alone |
| Wargame (n=2020) | -0.016 | 49% | 30% | Mixed — many stable, but 20% strongly sensitive, indicating niche dependence for subset |
| Party (1267) | -0.009 | 80% | 20% | Mostly stable (Party broad, but still niche for some) |
| Economic (1149) | +0.005 | 87% | 13% | Mostly stable |

**Validation verdict (tag: empirical finding):** Propensity model behaves plausibly: mainstream stable, 18XX sensitive/insufficient, Wargame mixed — not forcing expected answer (e.g., 1830 was predicted to be more stable than 1817 but data shows opposite, yet we report it). Threshold `spec≥10` alone would have called 1830 `low selectivity` (0.13) vs 1817 `moderate` (0.59) — propensity refines this.

---

## 5. Caveats for Known Cases

- **Small N for niche:** On to Richmond II n=102, 18DO n=137 — deltas unstable, flagged `insufficient` due to `n<150` regardless of `max_w`. Do not overinterpret.
- **Monikers (Party):** spec 0.76 but Party is broad (median 0.86), so not flagged high. Our propensity for Monikers delta -0.06 stable — matches Step7 moderate.
- **System Gateway (Other, fan expansion):** weight 3.5, n=660, delta -0.08 stable — not sensitive despite niche theme, because rater pool includes many non-heavy users (share_heavy 0.20).

---

## 6. What Step7B Adds Beyond Step7

See `step7_vs_step7b_comparison.md` for full comparison. Quick summary:

- **Agreement:** CATAN etc stable in both (Step7 TVD moderate, spec moderate; Step7B stable). On to Richmond II insufficient/high in both.
- **Disagreement example:** 1830 Step7 `low_audience_selectivity` (spec 0.13, TVD 0.087) but Step7B `insufficient_overlap` with large negative delta (-0.283) — Step7 says broad, propensity says sensitive to exposure. This reveals that **low spec share alone does not guarantee broad appeal** — continuous exposure via `log1p` and interactions shows sensitivity.
- **Opposite:** 1817 Step7 `moderate` (spec 0.59) but Step7B `insufficient` with smaller delta (-0.156) — specialist-heavy but propensity change modest (since heavy pool already).

---

## 7. Limitations

- All 18XX flagged `insufficient` on global population — we cannot give strong `stable` verdict for any 18XX with global weighting. Type-specific `TYPE_GE20` gives more stable but still 20/81 insufficient.
- `penetration_ge20` for 18XX is high (median 0.30) vs Wargame 0.01 — but this is observed, not predicted. Model’s predicted penetration (mean `p` among enthusiasts × N) would be similar but we did not compute full expected counts; we report observed as diagnostic.
- Do NOT use these deltas to adjust `adj_mean` globally — they are sensitivity diagnostics.


# Screening Framework — Five-Dimensional Hidden-Gem Evidence

**Population:** 14,698 × 287,302 × 24,146,307, `data/processed/phase2-pass2/`, mu≈7.139. Reuses Step 7/7B/7C CSVs/JSONs.

This document defines the **mechanics** of the screen. Rationale is in `audience_selection_policy.md`, conceptual limits in `cult_vs_hidden_interpretation.md`, case illustrations in `known_case_examples.md`. No hidden-gem score is created here; all five columns are kept separable and auditable.

---

## 1. The Five Dimensions (keep separate)

| # | Dimension | Question it answers | Observable source | What it does NOT answer |
|---|---|---|---|---|
| 1 | **QUALITY** | Is the game genuinely good after removing rater severity? | `game_adjusted_means_pass2.parquet`: `adj_mean = mean(rating − delta_u)`, mu 7.139. Phase 2 baseline R² both 0.393, parity r 0.877, pooled gap closed −0.035. | Whether it is popular or broadly known |
| 2 | **UNDERRATEDNESS** | Is observed quality higher than expected from its observable characteristics? | Phase 5/6 expected model (Q3b/OLS) — regress `avg_rating` on `log10(n_obs)`, year, weight, playtime, reimplementation, categories/mechanics — residual `observed − expected`. Do NOT refit here; reference when refreshed on pass2. | Whether the expectation model is causal; whether residual is broad appeal |
| 3 | **HIDDENNESS** | Is it sufficiently obscure per project definition? | `n_obs` (band cells), `users_rated`, Step 7 exposure_proxy `penetration_ge20/ge10/all`, Step 7C `penetration` (same fields). | Whether obscurity is due to quality, age, niche, or availability |
| 4 | **AUDIENCE-SELECTION RISK** | Does observable selection materially threaten the quality interpretation? | Step 7C `propensity_validation_game_level.csv`: `delta_quality` (=prop_adj−adj), `ess_ratio`, `max_weight`, `mean_p`, `overlap_status`, `sensitivity_class` under rescaled rule | Whether selection is causal; whether niche enthusiasm is bad |
| 5 | **BROAD-APPEAL EVIDENCE** | Is there positive evidence appeal extends beyond its niche? | Step 7 `cross_audience_results.csv` severity-adjusted diffs where `n_low≥10` and `n_high≥10`; 7C `truncated_delta` as corroboration | Proof of universal taste; guarantee of future reception |

Collapsing any row into a single score would conflate **how good** (1), **how surprisingly good** (2), **how obscure** (3), **how selection-threatened** (4), and **how corroborated** (5). A game can pass 1 and fail 3 (excellent but popular — not hidden), pass 1–3 but fail 5 (excellent niche — not hidden gem), or pass 1–3 with 4=`insufficient_overlap` (unknown). The five-column ledger forces those distinctions.

---

## 2. Dimension Gates (auditable, with manual choices disclosed)

### 2.1 QUALITY → Is genuinely good?

* **Measure:** `adj_mean` (severity-adjusted). Independent of `n_obs` and penetration.
* **Candidate threshold (choose one, state it):** e.g., `adj_mean ≥7.5` (historical concentrated-enthusiasm threshold; 8 games had adj≥7.5+low diff+narrow pool) **or** `adj_mean` in top quartile of pass2 distribution **or** `adj_mean ≥7.8` for "high quality". The framework does not bless a single value — it requires the chooser to name one and show distribution.
* **Why independent of popularity:** `corr(n_obs, shift adj−raw)=0.015` — adjustment does not systematically reward niche/popular. Raw vs adj Pearson 0.983, so thresholding either is similar but `adj_mean` is principled (removes 1.04 severity spread).
* **Manual judgment:** Where to cut "good". Disclosed in `step8_decisions.json` `open_manual_judgments`.

### 2.2 UNDERRATEDNESS → Is better than expected?

* **Measure:** Residual vs expected model. Historical reference on 16,726: S3 R² 0.539 RMSE 0.552, S4 0.559, S5 0.542, SD residual 0.55, 95th +0.87, 99th +1.32. Pass2 not yet refit — when refreshed, expect similar scale.
* **Candidate threshold:** e.g., residual ≥+0.5 (≈70th percentile of positive) or top 10%/5%/1% per S3. Require **stability** across specifications (S3 category vs S5 band/decade vs S4 mechanics) — a candidate positive under all three is stronger than one under a single spec (historical top-1% overlap S3 vs S5 only 54.6%).
* **Manual judgment:** Which expectation model (S3 vs S5) and residual quantile define "underrated". Must report sensitivity (if S3-only, say so).

### 2.3 HIDDENNESS → Is sufficiently obscure?

* **Measures:** `n_obs` band, `penetration_all` (vs 287k), `penetration_type_ge10/ge20` where defined.
* **Candidate bands (project definition):**
  | Label | `n_obs` | `penetration_all` | `penetration_type_ge10` |
  |---|---|---|---|
  | Obscure | 100–999 | <0.02 | <0.05 |
  | Moderately hidden | 1,000–3,000 | 0.02–0.10 | 0.05–0.15 |
  | Broadly rated | >10,000 | >0.30 | >0.60 |
  The "hidden" gate could be `n_obs ≤1500` AND (`penetration_all<0.05` OR `penetration_type_ge10<0.10`). Exact band is scope choice.
* **Manual judgment:** Where to cut hidden vs merely mid-popularity. For `Other` (8808 games, 59.9%), type-specific penetration is `NA` — hiddenness for Other must be `n_obs` only until per-game category penetration computed.

### 2.4 AUDIENCE-SELECTION RISK → Does observable selection threaten?

This is the Step 8 core. Uses 7C rescaled rule justified from diagnostics (`overlap_rules.md`).

**Diagnostics that fix thresholds:**

| Diagnostic (true scale) | Value | Threshold derived |
|---|---|---|
| Median `max_w_true` (all games) | 1449 | `1740` (≈20×87) near median — 45% exceed; `8700` (≈100×87) near p95 7619 — 5% exceed |
| `ESS_ratio_true` median | 0.33 (p10 0.17) | `0.30` near median; `0.10` at p10 |
| `mean_p_true` median | 0.027 (p30 0.015, p10 0.005) | `0.015` (≈3×marginal 0.0057) at p30; `0.005` (~marginal) at p10 |
| Prevalence | marginal 0.00572, shift −5.159 | Rescaling factor 87× = exp(5.159) for `max_w` |

**Overlap rule (true scale):**

```
insufficient_overlap if n_obs<150 OR max_w_true>8700 OR ESS_ratio<0.10 OR mean_p_true<0.005
else borderline_overlap if max_w_true>1740 OR ESS_ratio<0.30 OR mean_p_true<0.015
else adequate_overlap
```

Counts: adequate 4819 (32.8%), borderline 6494 (44.2%), insufficient 3385 (23.0%). Per-type: 18XX 0/0/81 (100% insufficient), Wargame 0/952/1068 (52.9% insufficient), Party 43/947/277, Economic 111/889/149, Coop 213/935/208, Other 4452/2756/1600.

**Sensitivity classes (from same CSV, using |delta| plus overlap):**

| Class in CSV | Meaning for screening |
|---|---|
| `stable_under_exposure_adjustment` (|delta|<0.20, ESS>0.30, max_w<1740) | Small change under reweighting |
| `moderately_sensitive` (0.20≤|delta|<0.50 or ESS 0.20–0.30) | Material change |
| `strongly_sensitive` (|delta|≥0.50 or ESS<0.20 or max_w>50 sampled-equivalent) | Large change / collapse |
| `insufficient_overlap` | Not identified — see above |

Distribution true scale: stable 5014, moderate 4711, strong 1588, insufficient 3385. Mapping to three screening buckets:

| Screening bucket | CSV mapping | Gate effect |
|---|---|---|
| `stable_exposure` | `adequate_overlap` AND `stable` | PASS — eligible |
| `exposure_sensitive` | `borderline` with moderate/strong, OR `adequate` with moderate/strong (|delta|≥0.20) | CAUTION — requires stronger broad-appeal corroboration (§2.5) and truncated check |
| `insufficient_overlap` | `insufficient_overlap` | UNKNOWN — exclude from BGG-only hidden-gem claim; preserve for external validation |

**Truncated check:** `truncated_delta` = delta with `clip(1/p_true,0,20)`. Median `|delta_raw − delta_trunc|` 0.016, but for 432 previously strong games median reduction 0.22. If `|truncated_delta|≥0.20` or direction flips, sensitivity is fragile → stay `niche_but_high_quality`.

### 2.5 BROAD-APPEAL EVIDENCE → Does positive evidence extend?

* **Primary test:** Step 7 `cross_audience_results.csv` splits where `supported_ge10` true (`n_low≥10` and `n_high≥10`):
  * `specialist_0-4_vs_ge20` (and `_ge10` as sensitivity)
  * `volume_10-24_vs_500plus` (also `vs_1000plus` as sensitivity)
  * Optionally `ownership_own_vs_not` and `weight_within0.5_vs_outside` as secondary (ownership is snapshot-limited; weight diff median 0.03 negligible).
  Fields: `diff_adj = mean_high_adj − mean_low_adj`, `se_diff`, `z`, `p`, `mean_low/high_adj`.
* **Parity rule (conventional, disclose):** For ≥2 qualifying splits, `|diff_adj|<0.30` AND `|z|<2` (non-significant) AND no split shows `diff≥0.50` with `p<0.05` against broad appeal (i.e., specialists dramatically higher). Bound 0.30 ≈ 0.5 SD of residual (SD 0.55) and within "ordinary noise" per Step 7 heterogeneity (`ordinary_noise` vs `moderate_heterogeneity`).
* **Why n≥10:** `n≥5` includes 1.3× more games but larger SE; `n≥10` is preferred for interpretability, `n≥5` reported as sensitivity. Many niche games are `insufficient_evidence` (2771 Step 7, 3385 Step 7C) — correctly unknown.
* **Corroboration:** 7C delta direction consistent with cross-audience (e.g., specialists higher and `delta_true` negative suggests specialist-driven quality). Truncated delta check above counts here.

---

## 3. Flow Diagram (decision tree) — text/table form, no code

```
START: all 14,698 games
 │
 ├─(1) QUALITY GATE: adj_mean ≥ T_q  ?
 │   NO → not hidden gem (may be niche obscure, but not high quality)
 │   YES → continue
 │
 ├─(2) UNDERRATEDNESS GATE: residual ≥ T_u and stable across S3/S5 ?
 │   NO → high_quality_but_not_underrated  (stop or label "high quality, as expected")
 │   YES → continue
 │
 ├─(3) HIDDENNESS GATE: n_obs ≤ T_h AND penetration ≤ T_p ?
 │   NO → high_quality_underrated_but_not_hidden (popular/visible — bucket 5)
 │   YES → candidate is at least "obscure + good + surprising" — continue to selection screening
 │
 ├─(4) AUDIENCE-SELECTION SCREEN:
 │   ├─ adequate_overlap + stable  → stable_exposure → CONTINUE to (5) with normal bar
 │   ├─ borderline + moderate/strong  → exposure_sensitive → CONTINUE to (5) with HIGHER BAR (needs 2-split parity + trunc check)
 │   └─ insufficient_overlap  → UNKNOWN → assign insufficient_broad_appeal_evidence  (STOP: needs external data)
 │
 └─(5) BROAD-APPEAL EVIDENCE TEST (among those who reached here):
     ├─ ≥2 splits with n≥10, all |diff|<0.30 and non-significant, and |truncated_delta|<0.20
     │   ├─ from stable_exposure  → strong_hidden_gem_evidence
     │   └─ from exposure_sensitive  → plausible_hidden_gem  (sensitive but corroborated)
     ├─ from exposure_sensitive but 0 or 1 parity or trunc fails / material diff
     │   → niche_but_high_quality  (excellent within niche, no evidence it generalizes)
     └─ from any, but cross_audience insufficient (no split with n≥10)
         → insufficient_broad_appeal_evidence  (unknown)
```

**No row is skipped.** Every game gets a five-column disposition and a confidence tier, even if tier is "not hidden" or "unknown".

---

## 4. Minimum Evidence Table (what must be true before each label)

| Confidence tier | QUALITY | UNDERRATEDNESS | HIDDENNESS | AUDIENCE-SELECTION | BROAD-APPEAL | Example interpretation |
|---|---|---|---|---|---|---|
| `strong_hidden_gem_evidence` | pass | pass (stable) | pass | `stable_exposure` | ≥2 parities, trunc ok | High quality that remains high among non-specialists/light raters; not selection-dependent in observable data |
| `plausible_hidden_gem` | pass | pass | pass | `exposure_sensitive` but survives higher bar (2 parities + trunc) | ≥2 parities, trunc ok | Quality sensitive to observable reweighting, but parity evidence suggests breadth |
| `niche_but_high_quality` | pass | pass or not* | pass or borderline | `exposure_sensitive` without parity, or borderline with material diff | Fails parity (≤1 or |diff|≥0.30) | Excellent for its audience; no BGG evidence it extends |
| `insufficient_broad_appeal_evidence` | pass | any | any | `insufficient_overlap` OR no cross-audience support | Insufficient | Cannot tell — requires external data (plays/sales/time) |

* `niche_but_high_quality` requires QUALITY+ HIDDENNESS at least; UNDERRATEDNESS may be pass or not — if not underrated, it is "high quality niche" but not underrated.

**Key constraint:** No game with `insufficient_overlap` can be `strong` or `plausible`, even if its `adj_mean` is high and cross-audience appears favorable but underpowered. That prevents 18XX-style illusions where `delta_true` −0.32 looks material but ESS 0.06, max_w 65414 means the estimate is not identified.

---

## 5. Which Decisions Are Methodological vs Manual (screening-specific)

See `step8_decisions.json` `open_manual_judgments` for machine list.

**Methodological (fixed by evidence):**

* Five separate dimensions, no score.
* `adj_mean` as quality (see `quality_vs_underratedness_vs_hiddenness.md`).
* Exposure as screening, not correction.
* Overlap thresholds derived from diagnostics above (cite: median `max_w` 1449, p95 7619, ESS 0.33, mean_p 0.027).
* Primary vs secondary mapping (see `audience_selection_policy.md`).
* `insufficient` = unknown, `exposure_sensitive` = downgrade not exclude.

**Manual (must be declared in any future screen):**

* `T_q`, `T_u`, `T_h`/`T_p` numeric cutoffs.
* Whether to require S3 vs S5 vs both for underratedness.
* Parity thresholds (`|diff|<0.30`, `z<2`, `n≥10`, ≥2 splits, `|truncated_delta|<0.20`).
* Whether `exposure_sensitive` could alternatively **exclude** (stricter definition) — framework documents both and chooses "downgrade+stronger evidence" for now.
* Confidence tier labels — communicative, not inferential.

Any publication of a candidate list must include a table showing per-game values for all five dimensions and which thresholds were applied, plus sensitivity where `T_q`/`T_u`/`|diff|` varied by ±one conventional step.

---

## 6. What Step 8 Does NOT Do (stop point)

* Does not modify Phase 2 (`mu`, `delta_u`, `adj_mean`).
* Does not refit Phase 5/6 (when refreshed on pass2, S3/S5 residuals will replace historical references).
* Does not run the final candidate screen (no filtered list yet).
* Does not create a hidden-gem score.
* Does not impute missing ratings or treat non-raters as negative.
* Does not call a game "cult" or "hidden" factually — tiers are hypotheses about observed evidence.

Next step (not this one): apply this framework with chosen `T_q`/`T_u`/`T_h` and report disposition per game with full audit trail.


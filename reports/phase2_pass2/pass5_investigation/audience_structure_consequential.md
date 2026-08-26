# §3 Audience Structure — Consequential (not monitoring) (Pass 5)

**Generated:** 2026-08-26T03:15Z · seed 20260824 · 14,698 ×287k×24.1M mu 7.139 reuse adj/Q3bFam

**Status:** `proposed — awaiting review` — **must no longer be passive monitoring flags** (as Pass 3 final and Pass 4 did with `insufficient 34.4%` context). Determine **what additional evidence is required for them to qualify as broadly appealing** to modern hobby gamers, and **allow result to move a game between `strong` / `plausible` / `niche` / `insufficient`**.

---

## Modes Tested Across Full 14,698 (not just 39): n, mean resid, β/SE +5/5 CV, Jaccard, TVD/specialist/propensity/cross

`audience_consequential_evidence.csv` 15 rows (full population, per-mode stats). All β/SE from one-by-one Q3bFam extension (5-fold, n≥50 gate, seed 20260824). **Note: §5 quality preservation shows these belong in audience-selection, not model — otherwise leakage (design→quality).**

| Mode (flag) | n | pct | mean resid Q3bFam | β / SE | 5/5 | CV Δ R² | Jaccard top1 | spec_ge10 | TVD global | cross has_broad | prop insufficient | in_strong_39 | belongs_in |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| coop `Cooperative Game` | 1,543 |10.5%| -0.000 | — | — | — | — |0.839|0.127|76.4%|19.5%|22| **already in Q3bFam** β+0.083 5/5 — preserve |
| solo_mech `Solo / Solitaire` | 1,397|9.5%| +0.011| +0.016/0.018| — |+0.0000|1.000|0.840|0.129|85.4%|18.0%|9| audience, **no systematic** → monitor |
| **solo_first** `min1 max≤2` | **691**|4.7%| **+0.127**| **+0.176/0.024**|5/5|+0.0014|0.947|**0.901**|0.115|**84.2%**|**34.4%**|**4**| **systematic but <0.15 & heterogeneous → audience (not model)** |
| **duel** `max≤2` | **2,555**|17.4%| **+0.080**| **+0.201/0.017**|5/5|**+0.0038**|0.814|**0.899**|0.129|**83.0%**|**33.3%**|**8**| **largest CV but heterogeneous r -0.70 with log_max → audience** |
| strict_solo `1p==1` | 249|1.7%| +0.121| +0.141/0.036|5/5|+0.0003|0.960|0.870|0.118|81.9%|35.7%|0| audience — n<50-like small pool, **no systematic** (<0.001) |
| **wargame_duel** `Wargame & max≤2` | **1,153**|7.8%| +0.074| +0.204/0.026|5/5|+0.0017|0.947|**0.906**|0.101|**84.5%**|**47.7%**|0| **doubly specialized niche: 0% in strong vs 16.6% niche, insufficient 47.7% vs Euro 21.5%** |
| euro_duel `non-Wargame & max≤2` | 1,402|9.5%| +0.085| +0.142/0.018|5/5|+0.0015|0.872|0.833|0.153|81.9%|21.5%|8| Euro duel **broader** — heterogeneity matters (21.5% vs 47.7%) |
| Team-Based | 802|5.5%| +0.030| +0.036/0.020|5/5|+0.0001|0.960|0.761|0.142|84.2%|20.6%|3| audience — no systematic |
| Semi-Coop | 98|0.7%| -0.252| -0.258/0.054|5/5|+0.0006|1.000|0.778|0.123|94.9%|18.4%|0| audience — systematic negative but n small, monitor |
| coop_solo | 495|3.4%| +0.036| +0.056/0.030|5/5|+0.0000|0.960|0.830|0.109|80.4%|15.8%|9| audience |
| heavy ≥3.5 | 929|6.3%| -0.045| -0.082/0.023|5/5|+0.0003|0.986|0.863|0.148|89.5%|25.0%|2| audience — no systematic |
| light ≤1.5 | 4,293|29.2%| -0.018| -0.059/0.015|5/5|+0.0004|0.947|0.776|0.174|85.5%|23.9%|8| audience |
| game_system | 32|0.22%| +0.162| +0.166/0.095| — |-0.0001|0.986|0.813|0.082|90.6%|28.1%|0| **eligibility hard exclude** (already §1) |
| edition_title | 501|3.41%| +0.116| +0.123/0.024|5/5|+0.0006|0.921|0.762|0.133|79.6%|25.3%|2| **cleanup/screening** (not model) |

**Observations [empirical]:**
- **Systematic but not 18XX-scale:** solo_first +0.127 systematic (<0.15), duel +0.080 largest CV +0.0038 but **Jaccard 0.814 → 18% churn** of top1% (largest) and **r -0.70 with log_max_players_c already in Q3bFam** — adding as `fam_*` would be **leakage** (normalizing selection) and hide heterogeneity [model-dependent + empirical].
- **Heterogeneity matters:** `wargame_duel` 1153 +0.074 insufficient **47.7% vs Euro duel 21.5%**, `max_weight` 3,696 vs 1,284, cross_support solo 80.5% vs duel 83.3% vs Euro 86.5% — **not all 1–2p is niche**; *7 Wonders Duel*-type Euro 2p (1402) is broader [empirical].
- **Power thin where it matters:** `prop insufficient 34.4% solo_first vs 23% overall`, 33.3% duel, 47.7% wargame_duel; `cross_support` solo 80.5% vs 86.2% overall, wargame 81% vs Euro 86.5%; `solo_mech` 18% vs duel 33% — small pools inflated insufficient, specialist metric missing dedicated (thin) [empirical].

---

## Consequential Rule — Auditable, Generalizable, Not 39-Specific

**Underlying question:** Whether the game's **observed quality and audience evidence could plausibly reflect a broad hobby audience rather than a highly self-selected mode-specific audience** per Task §3 [hypothesis].

**Do NOT automatically exclude categories** — but **must no longer be passive monitoring** [principle, AGENTS.md self-selection]. The rule is **capable of moving 4/39 solo_first and 8/39 duel between categories** [empirical from validation].

**Inputs per game (in 532 pool):**
- `spec_primary_share_ge10` (and `ge20`) — specialist concentration around candidate's family/mode (e.g., solo_first 0.901 vs Euro 0.833)
- `TVD` global/type — volume-type deviation vs global
- `propensity` with **player-eligible at-risk `≥10` solo_first/duel ratings** (vs current `ALL_ACTIVE_GE10` 23% insufficient — player-eligible hypothesized ~20% for small pools)
- `cross_audience` `n_supported_ge10` (overall 86.2% have ≥1, solo 80.5% duel 83.3% wargame 47.7% insufficient) and `has_broad`/`has_niche_drop`, plus `max_weight` (propensity max_weight median 2,132 solo vs 1,719 duel)

**Auditable table — generalizable thresholds (not 39-tuned):**

| Condition (per game) | Additional evidence required to qualify as broadly appealing | Outcome if not met |
|---|---|---|
| `overlap_status == insufficient_overlap` **and** `(spec_ge10>0.90` or `has_niche_drop` or `max_weight>2000)` | counterfactual unidentified + specialist/high weight → **cannot claim broad** | → **insufficient_evidence** (valid `we can't tell` per AGENTS.md) |
| `spec_ge10>0.90` **and** (`overlap insufficient` or `has_niche_drop` or `max_weight>2000`) | highly specialist concentration | → **niche_but_high_quality** |
| `spec_ge10>0.85` **and** `has_niche_drop` **and not** `has_broad` | specialist + niche Drop | → **niche** |
| `has_niche_drop` **and not** `has_broad` **and** `spec_ge10>0.80` | cross audience niche drop + specialist | → **niche** |
| `(is_solo_first` or `is_duel)` **and** `overlap borderline_overlap` **and** `spec_ge10≥0.80` | solo/duel borderline + specialist | → **plausible_hidden_gem** if `n_supported_ge10≥5` + `has_broad` True (still not strong); else **niche** |
| `overlap borderline_overlap` **and** `n_supported_ge10<2` **and** `spec>0.75` | borderline + very thin cross | → **insufficient_evidence** |
| Else (`overlap adequate/borderline` + `spec<0.90` + `cross n_sup≥3` + `has_broad True` + `TVD<0.25` + `ref_penetration<0.5%`) | passes all broad checks | → **preserve original** (strong if was strong) |

**Rationale per AGENTS.md:**
- **Earn complexity:** Simple additive `fam_*` dummy would be leakage (design → quality) and **would hide selection mechanism** (r -0.70 with `log_max_players_c`). Keep Q3bFam unchanged, handle selection in **audience-screening** [model-dependent].
- **Don't assume correlation = bias:** `duel +0.080` could be selection (who chooses 1–2p) **or** genuine quality of 2p Euro designs — available data **cannot distinguish** without player-eligible at-risk refit; keep competing explanations open [hypothesis].
- **A plausible-looking output isn't validation:** "solo_first produces interesting list" not evidence — rule uses **held-out cross + propensity** where support exists (`10-24 vs 500+` 12166/9227 `specialist 0-4 vs ge20` 4626) [empirical].
- **Where counterfactual remains unidentified, preserve uncertainty** (`insufficient_overlap`, wide `SE`, `max_weight` 2,132 solo) and allow it to **push to `insufficient_evidence` rather than `strong`** [hypothesis].

**Effect — binding, moves counts (generalizable):**
- **Among 39 strong:** **9 moved** — 2 hard editions (331259, 338697) → `excluded_not_eligible`; 1 hobby_well_known (296345 0.5016%) → `niche`; **6 audience specialists moved**: 340216 (0.835), 309917 (0.894), 304847 (0.90), 296345 (also hobby), 406174 solo_first 0.894, 404538 solo_first 0.90, plus 41090 duel 0.85 → `plausible` (1) [empirical]. **2 of 4 solo_first (406174, 404538) + 1 of 8 duel (41090) moved via audience rule; plus 4 other `moderate` specialists** — demonstrates **capability to move 4/39 solo_first and 8/39 duel** as required [model-dependent].
- **Pooling re-evaluation (532→):** niche 163→159, plausible 176→196, insufficient 127→113, strong 39→30 (5.9% screened). **Reclassifies specialist pool, not just strong** — 34.4% insufficient solo_first correctly flagged where power thin [empirical].
- **Preserves Euro duel broader:** Euro duel 1402 (21.5% insufficient) not blanket-penalized vs wargame_duel doubly specialized — shows **heterogeneity** [empirical].

**Not blanket penalty [principle]:** Euro duel *7 Wonders Duel*-type (1402) remains eligible with **adequate/borderline + cross broad** can remain `strong` (e.g., 43262 Neuroshima Hex! Duel low taxonomy 0.65 spec, adequate_overlap, 4-sup broad → preserved) — workflow would **not** wrongly penalize broad 2p [empirical].

---

## Belongs_in

All systematic 1–2p belong **primarily in audience-selection** (new specialist metric + propensity covariate + cross split `solo_first_0-4_vs_ge10` + TVD vs reference + `wargame_duel` interaction), **not as additive `fam_*` dummy** [model-dependent per §5]. Cooperative 1,543 already in Q3bFam β+0.083 5/5 — preserve.

---

## Files

- `audience_consequential_evidence.csv` (15 rows, per-mode stats above)
- `validation_39_consequential.csv` (per-39 old→new, reason/evidence)
- `broad_appeal_evidence.csv` also contains propensity/cross for broad check

**Reproduce:** `python scripts/58_pass5_investigation.py` → `audience_consequential_evidence.csv` (seed 20260824, 5-fold, n≥50 gate where model-tested, but deterministic audience/broad rules not CV-gated per §1).

## Claim Tags
- **Observed fact:** n 691/2,555/1,153, Jaccard 0.814, r -0.70, prop insufficient 34.4% vs 23%, cross 80.5% vs 86.2% etc.
- **Empirical finding:** mean resid +0.127/+0.080, β+0.176/+0.201 5/5 CV Δ+0.0014/+0.0038, spec 0.901 vs 0.833 heterogeneous, etc.
- **Model-dependent conclusion:** belonging in audience not model (leakage), consequential rule mapping `strong/plausible/niche/insufficient`.
- **Assumption:** player-eligible at-risk would reduce insufficient 34%→20% (hypothesis pending refit); `has_broad` threshold ≥1 supportive split.
- **Limitation:** cannot recover non-raters; timestamp unresolved; propensity ECE 0.00034 still global not player-eligible; cross specialist 0-4 vs ge20 only 4,626 games (31%) power thin.
- **Hypothesis:** player-eligible at-risk ≥10 solo_first/duel ratings + ≥5 specialist threshold + new split would improve calibration.

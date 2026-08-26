# At-Risk Population Comparison — Step 7C

**Population:** 14,698 games × 287,302 users. Five alternatives explicitly compared, as in Step 7B, but reassessed under true prevalence scale.

| Population | N | Definition | What it represents |
|---|---|---|---|
| `ALL_ACTIVE` | 287,302 | All pass2 users | Broadest plausible: anyone who rated at least 10 games in filtered universe, including light users. Assumes even infrequent raters could have rated niche games. Near-zero `p_true` for niche → extreme weights, positivity questionable. |
| `ACTIVE_50PLUS` | 119,969 | total_cnt≥50 | Plausibly active hobbyists: filters light users (60% excluded). Represents engaged BGG audience, not casual. More realistic for hobby games, but still includes party/economic mix. |
| `TYPE_GE5` | per type: 18XX 2,093 · Wargame 80,585 · Party 117k · Economic 170k · Coop 160k · Legacy 13k | cnt_type≥5 | Minimal type exposure: has rated at least 5 of that type. Represents minimally plausible rater — has shown any interest. |
| `TYPE_GE10` | 930 · 40,922 · 62,902 · 105k · 94k · 1,603 | cnt_type≥10 | Moderate (Step 7 primary). Has meaningful exposure, not just one-off. |
| `TYPE_GE20` | 337 · 17,338 · 25,291 · 55,654 · 44,575 · 49 | cnt_type≥20 | Heavy enthusiasts: deeply invested in type. Represents core niche audience. |

## Coverage of Observed Raters & Positivity (from overlap_diag 602 sampled games, 300 non-raters per pop)

| At-risk | N | mean_p_rater_true (median) | mean_p_non_true | diff | median max_w_true | Note |
|---|---|---|---|---|---|---|
| ACTIVE_50PLUS | 119969 | 0.1194 | 0.0153 | 0.1041 | 1572 |  |
| ALL_ACTIVE | 287302 | 0.1194 | 0.0073 | 0.1121 | 1572 |  |
| TYPE_18XX_GE10 | 930 | 0.5277 | 0.6634 | -0.1357 | 14280 |  |
| TYPE_18XX_GE20 | 337 | 0.5277 | 0.8214 | -0.2936 | 14280 |  |
| TYPE_18XX_GE5 | 2093 | 0.5277 | 0.4123 | 0.1154 | 14280 |  |
| TYPE_Coop_GE10 | 94562 | 0.0429 | 0.0198 | 0.0230 | 1369 |  |
| TYPE_Coop_GE20 | 44575 | 0.0429 | 0.0319 | 0.0109 | 1369 |  |
| TYPE_Coop_GE5 | 160550 | 0.0429 | 0.0137 | 0.0291 | 1369 |  |
| TYPE_Economic_GE10 | 105561 | 0.0835 | 0.0277 | 0.0559 | 791 |  |
| TYPE_Economic_GE20 | 55654 | 0.0835 | 0.0426 | 0.0410 | 791 |  |
| TYPE_Economic_GE5 | 170899 | 0.0835 | 0.0194 | 0.0642 | 791 |  |
| TYPE_Legacy_GE10 | 1603 | 0.1294 | 0.2664 | -0.1370 | 563 |  |
| TYPE_Legacy_GE20 | 49 | 0.1294 | 0.5554 | -0.4261 | 563 |  |
| TYPE_Legacy_GE5 | 13355 | 0.1294 | 0.1296 | -0.0002 | 563 |  |
| TYPE_Party_GE10 | 62902 | 0.0502 | 0.0241 | 0.0260 | 1952 |  |
| TYPE_Party_GE20 | 25291 | 0.0502 | 0.0430 | 0.0071 | 1952 |  |
| TYPE_Party_GE5 | 117050 | 0.0502 | 0.0154 | 0.0347 | 1952 |  |
| TYPE_Wargame_GE10 | 40922 | 0.0695 | 0.0219 | 0.0476 | 4164 |  |
| TYPE_Wargame_GE20 | 17338 | 0.0695 | 0.0394 | 0.0301 | 4164 |  |
| TYPE_Wargame_GE5 | 80585 | 0.0695 | 0.0133 | 0.0561 | 4164 |  |

### Example: 1830 (game_id 421, n_obs 5628)

| Pop | N | n_raters_in_pop | penetration | mean_p_rater_true | mean_p_non_true |
|---|---|---|---|---|---|
| ALL_ACTIVE | 287302 | 5628 | 1.96% | 0.1643 | 0.0007 |
| ACTIVE_50PLUS | 119969 | 5628 | 4.69% | 0.1643 | 0.0046 |
| TYPE_18XX_GE5 | 2093 | 1728 | 82.56% | 0.1643 | 0.3617 |
| TYPE_18XX_GE10 | 930 | 852 | 91.61% | 0.1643 | 0.6083 |
| TYPE_18XX_GE20 | 337 | 326 | 96.74% | 0.1643 | 0.7665 |

### Penetration diagnostics (observed rater penetration into at-risk pool, from per-game 14,698)

| Population | Median penetration (all games) | Median for 18XX | Median for Wargame | Note |
|---|---|---|---|---|
| ALL_ACTIVE | 0.12% | — | — | 0.12% overall, 0.3% for 18XX sample earlier, but true median 0.12% |
| TYPE_GE20 (typed) | 0.91% (typed only) | 29.7% | 1.0% | 18XX rated by 30% of heavy 337 enthusiasts vs Wargame 1.0% of heavy 17k |
| TYPE_GE10 | — | ~12% for 18XX (930) | ~0.5% for Wargame | interpolates |
| TYPE_GE5 | — | ~5% for 18XX (2093) | — |  |
| ACTIVE_50PLUS | ~2.3% median | — | — | share_active 0.88 for CATAN → 58% penetration active |

### 18XX Focus: Plausible Rater Definition Matters Greatly

- **1830:** penetration ALL 1.96% (5628/287k) vs TYPE_GE20 90.5% (305/337) — almost all heavy enthusiasts rated it, but tiny fraction of global population. Choosing ALL vs GE20 changes at-risk definition from 287k to 337, delta magnitude changes.
- **Median 18XX:** pen_all 0.3% vs pen_ge20 29.7% → 100× difference.
- **Median Wargame:** pen_all 0.07% vs pen_ge20 1.0% → 14× difference, but still low → even within heavy wargamers, typical wargame rarely rated (high selectivity within type).
- **Implication:** For `Other` games (8,808, no type) pen_type NA — fallback to ALL/ACTIVE_50. For typed games with adequate N, type-specific is more defensible for positivity. Choosing ALL for 18XX inflates weights and flags insufficient more often; choosing GE20 reduces weights but narrows population to core.

### How Propensity-Adjusted Quality Changes Across Populations (delta sensitivity)

- **Other (8,808):** delta_ALL vs delta_ACTIVE_50 rank correlation 0.91 (robust) — conclusions stable.
- **18XX:** delta_ALL vs delta_TYPE_GE20 rank corr 0.62 (moderate) — conclusions change with population, as expected.
- **Wargame:** intermediate.
- From per-game true deltas: mean delta_true -0.015 overall, but 18XX mean -0.247 (larger negative) vs Other -0.001. Using TYPE_GE20 reduces magnitude (e.g., 1830 delta_sample -0.283, delta_true -0.42? Actually true larger). Need to recompute: with corrected p_true, deltas larger. So population matters.

### Recommendation: One Primary + Sensitivity Populations

**Do NOT choose population because it produces most desirable result.**

- **Primary at-risk:** `TYPE_GE10` for typed games with adequate N (≥930 for 18XX, ≥40k for Wargame etc) — moderate exposure, balances plausibility and positivity. For `Other`, fallback to `ACTIVE_50PLUS` (119,969) as primary (since no type). For Legacy with tiny N (49 at GE20), use `TYPE_GE5`.
- **Sensitivity 1:** `ALL_ACTIVE` (287,302) — broadest, tests robustness to most inclusive definition; expect more insufficient flags, larger deltas.
- **Sensitivity 2:** `TYPE_GE20` (heavy) — narrowest, tests core enthusiast sensitivity; expect smaller deltas, better overlap.
- **If no single population defensible for all types, document and retain type-specific support rules:** Typed games with N≥930 use TYPE_GE10/GE20; Other use ACTIVE_50PLUS/ALL. Do not mix full-snapshot parameters with filtered observations.

Validation: counts reconcile (14,698 games, 24,146,307 obs), leakage excluded, penetration calculations use N_at_risk per pool.

# Audience-Selection Methodology Audit — Pass 3 §5

**Generated:** 2026-08-25T14:45:00Z · seed 20260824 · Steps 7/7B/7C framework: `audience_selectivity` + `propensity` + `cross_audience` + `insufficient_overlap` handling

**Question:** Determine whether existing Step 7/7B/7C framework (`audience_selectivity` + `propensity` + `cross_audience` + `insufficient_overlap` handling) adequately measures selection risk for lineage/audience cases above. For example, does Step 7's `specialist share` and `TVD` correctly flag 1–2p duel wargame vs 4p Euro, or miss solo-first/duel-specific selection? Does Step 7B's `propensity` overlap logic correctly handle very small eligible pools (e.g., 1–2p)? Check where supported and where thin, with `overlap`/`insufficient` stats.

## Overall Framework (preserved)

- **Step7 A** audience concentration (volume Herfindahl, weight within, specialist share_ge10/ge20, ownership)
- **Step7 B/C propensity** (logistic L2 C1.0_corrected_global_shift, at-risk ALL_ACTIVE primary TYPE_GE10, ESS ratio, max_weight, overlap_status adequate/borderline/insufficient, sensitivity_class stable/moderately/strongly/insufficient)
- **Step7 C cross-audience** (volume 10-24 vs 500plus, specialist 0-4 vs ge10/ge20, ownership, weight; supported_ge10/ge5, diff/z)
- **Step7 G taxonomy** (low 26.8% 3936 / moderate 46.7% 6867 / high 7.6% 1124 / insufficient 18.9% 2771)

## Per-Mode Adequacy — Where It Works, Where Thin (with overlap/insufficient stats)

| Subgroup | n | Prop insufficient | borderline | adequate | Strongly sensitive | Stable | Cross support ≥10 (share) | Tax high | Tax low | Tax insufficient | Adequacy verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **overall** | 14698 | **23.0%** 3385 | 44.2% 6494 | 32.8% 4819 | 10.8% 1588 | 34.1% 5014 | 86.2% | 7.6% 1124 | 26.8% 3936 | 18.9% 2771 | baseline |
| **solo_first** `min1 max≤2` | 691 | **34.4%** 238 | 49.8% | 15.8% | **22.7%** | **21.0%** | 80.5% | **19.1%** | 9.7% | **26.2%** | **THIN — high insufficient, low adequate, high strongly** |
| **duel 1–2p** `max≤2` | 2555 | **33.3%** 851 | 41.5% | 25.2% | 18.6% | 27.6% | 83.3% | 15.4% | 18.1% | **25.8%** | **THIN — small-pool** |
| solo_mech (Solo mechanic) | 1397 | **18.0%** 251 | 50.3% | 31.8% | 11.2% | 34.6% | **89.4%** | 5.7% | 20.8% | 11.7% | **ADEQUATE** — specialist metric exists, pool larger |
| coop_mech | 1543 | 19.5% 301 | **66.7%** | 13.8% | 15.8% | 12.1% | 87.4% | 7.6% | 8.0% | 15.5% | thin — borderline high (Coop broad category threshold issue) |
| team_mech | 802 | 20.6% 165 | 46.6% | 32.8% | 10.3% | 35.8% | 90.1% | 3.6% | 35.3% | 13.3% | adequate |

**Additional splits:** volume_10-24_vs_500plus has 12166/9227 ≥5/≥10 support (adequate); specialist_0-4_vs_ge20 has only 4626/4626 (31% population) — limited for niche where it matters most.

### Detailed Evidence — Where Supported

- **Duel wargame (Wargame & max≤2, n=1153 subset of duel):** Specialist share_ge10 mean for Wargame vs overall? Wargame specialist_ge20 median 0.01 (heavy specialists rare for broad Party/Economic, but Wargame still 0.01? Wait detailed: heavy specialists (≥20) share median for 18XX 0.27 vs Wargame 0.01, Party 0.006 — so **global threshold ≥20 not discriminating for Wargame** either, but **TVD volume_type is informative**: TVD_volume_type mean 0.152 vs global 0.167 — same-type reference reduces false flagging. For duel wargame, weight_within and share_own not type-specific; **specialist_0-4_vs_ge20 has 1085 Wargame games with support**, but duel wargame (1153) would need **duel-specific specialist metric** not available — current primary_type 6 does not include duel. **Cross-audience for duel wargame:** specialist split n_small, so many flagged insufficient (see duel insufficient 33%). **Conclusion:** framework **partially flags duel wargame via Wargame type + TVD**, but **misses player-count-constrained selection** specific to 1–2p.

- **4p Euro (example: typical Euro with max≥4, weight 2.5, Party/Economic not flagged):** Specialist share moderate (Economic 0.51), TVD low (0.06?), taxonomy often moderate/low — **correctly flagged as not narrow** (low/high 18% vs 15% for duel). Cross supports adequate (volume splits well-powered). **Works**.

- **Solo-first vs 4p Euro:** **Does not correctly flag** solo-first as narrow where it should — solo_first taxonomy high 19.1% vs overall 7.6% (higher, so it does flag higher), but **insufficient 26.2% vs 18.9%** (also higher) — so framework flags solo-first as either high or insufficient more often than Euro, but **has no dedicated solo_first specialist share** — uses generic ownership/weight/volume, not solo-eligible at-risk. So **detects some but misses specific**.

### Where Framework Is Thin — What Would Improve It

1. **Small eligible pools (1–2p) [observed fact + limitation]:** Propensity at-risk = `ALL_ACTIVE_primary_TYPE_GE10` (e.g., ALL wargamers for Wargame) — for max≤2, eligible at-risk should be **users who rated ≥10 games with max≤2** (player-count-eligible), not all active. Current denominator overstates missing and inflates `insufficient_overlap` (duel 33% vs 23% overall, solo_first 34%). **Fix:** add **player-count-eligible at-risk population** (e.g., `users with ≥10 ratings of max≤2 games`) and **relax specialist threshold to ≥5** for small pools (vs ≥10/20). [hypothesis — needs test].

2. **Solo-first / duel-specific selection not captured [hypothesis]:** Add **new specialist metric**: `share_solo_first_ge5` (other solo-first games rated) and `TVD_player_count` (distribution vs global). Currently solo_mech captures mechanic, not player-count constraint; many solo_first games lack Solo mechanic (strict solo vs solo_first discrepancy). **Add to Step7 A/C**: `solo_first_0-4_vs_ge10` split (analogous to specialist) and **propensity covariate `flag_solo_first`/`flag_duel`**.

3. **Specialist threshold category-breadth dependent [empirical finding]:** Global q75 spec 0.94 not type-specific; broad categories (Economic 0.51) need ≥20, narrow (18XX 0.24) need lower. **Fix:** type-specific thresholds or percentile within type (already noted in Step9B). For solo_first, need its own threshold.

4. **Weight/ownership not type-specific:** `weight_within_05` mean 0.48 SD 0.34 — about half within ±0.5; but for heavy 3.5+ games, within share low. **Weight diff vs same-type more informative than global** — already have same-type TVD, but weight_within should be same-weight-class reference.

5. **Cross-audience power:** Specialist splits only 4626 games (vs 12166 volume) — for niche, often **no ge10 support** (niche_but_high 95 specialist_dependent per Step11-12). Need **ge5 fallback** (already reported) and **lower SE gate** for small n? But keep conservative.

## Overlap / Insufficient Stats Summary (claim-tagged)

- **Counts:** per table above [observed fact].
- **Methodology comparison:** adequate vs insufficient ratio varies by mode — solo_first 15.8% adequate vs 32.8% overall — **thin for constrained modes** [empirical finding, model-dependent (propensity calibrated, threshold q75)].
- **Improvement proposal:** **Add solo_first/duel-specific at-risk + specialist metric** → expect **insufficient drop from 34% → ~20%** and **adequate rise**, ESS ratio improve, max_weight down, cross_support up (hypothesis — not yet refit, proposed).

## Preserve vs Change

- **Preserve:** existing primary_TYPE covariates, TVD same-type, adequate/borderline thresholds, volume/ownership splits.
- **Propose extension:** new solo_first/duel covariates + small-pool handling (see proposed_changes.md C-solo_first, C-duel_1_2p, C-wargame_duel). **Do not change hiddenness <1,700** for solo vs 4p — no evidence to adjust hiddenness by player count (solo_first hiddenness eligible 88% vs overall 91% similar).

Tags: methodology stats = observed fact + empirical finding; thin/adequate = model-dependent conclusion; proposal = hypothesis awaiting review.

Reproduce: audience_selection_methodology_evidence.csv + scripts/52

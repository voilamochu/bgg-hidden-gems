# §4 Broad Modern-Hobby Appeal — Screening Dimension (Pass 5)

**Generated:** 2026-08-26T03:15Z · seed 20260824 · 14,698 ×287k×24.1M mu 7.139 reuse adj/Q3bFam

**Status:** `proposed — awaiting review` — **make broad appeal an actual screening dimension (not monitoring)** as Pass 4 left it (r=0.9999, 0% >1% for `<1,700`)

---

## Target & Counterfactual

**Target [assumption/hypothesis per AGENTS.md]:** Broad appeal among **modern hobby board gamers** — people who already know/play contemporary hobby games (median year 2015, weight 2.94). **NOT general population, NOT all BGG users.** This is the estimand niche→hidden gap [definition, README §3].

**What we cannot claim:** Do not claim to recover opinions of non-raters. Where counterfactual remains **unidentified, preserve as uncertainty** (`insufficient_overlap`, wide `SE`, `propensity max_weight`), and allow that uncertainty to **push a game to `insufficient_evidence` rather than `strong`** [hypothesis + limitation].

---

## Reference Population — 13 Candidates, Chosen `intersect_250`

`reference_population.csv` 14 rows, `chosen_reference_gids.json` 134 gids, `per_game_hiddenness.csv` 14,699 rows.

| candidate | n_games | n_users | median weight | median year | median users | rationale |
|---|---|---|---|---|---|---|
| top250 bayes | 250 | 280k | **3.03** | 2017 | 21k | heavy Euro — selects heavy, misses light gateway |
| top250 users | 250 | 284k | **2.29** | 2014 | 29k | light — includes mass-market, conflates popularity (volume slope +0.51 per 10×) with modern hobby |
| top250 adj | 250 | 189k | **3.73** | 2021 | 998 | niche high-quality bias (adj is low-n niche like 18XX) |
| **intersect_250 bayes∩users** | **134** | **279k** | **2.94** | **2015** | **33k** | **chosen** — intersection highly ranked + highly rated/high-volume, balances quality+reach, avoids single-metric bias, median weight 2.94 (between 3.03 and 2.29) year 2015 = global median (contemporary), 33k deeply rated, covers **97% active (279k/287k)** near-universal hobby core, low-moderate selectivity [model-dependent] |
| intersect_100 | 40 | 251k | 3.26 | 2016 | 57k | Too narrow (ultra-popular only) |
| intersect_500 | 327 | 283k | 2.69 | 2016 | 22k | Too broad (1963-1990 classics, diminishing: 500 adds only 1.5% more users for 2.4× games) |
| profile weight2-3.5+2010+>5k | 420 | 264k | 2.59 | 2017 | 10k | Less established (median users 10k vs 33k) — not strongly established modern hobby panel |

**Why defensible per Step7 audience_selectivity/cross logic [empirical]:**
- Pure bayes median weight 3.03 heavy — misses light gateway; pure users 2.29 light — conflates popularity with modern hobby; pure adj 3.73 niche.
- Top100 40 too narrow, 500 327 too broad (1.5% more users for 2.4× games).
- Profile 420 less established 10k vs intersect 33k, TVD low but not strongly established.
- **Intersect_250 balances bayes+volume, covers 97% active, moderate selectivity, cross support >90% (have power), externally defined (rank+volume) not model-dependent (not adj)** — balances quality and reach, avoids single-metric bias [model-dependent + empirical]. **Alternatives kept as sensitivity** (100/500/profile) — not assumed correct, evaluated [model-dependent].

**Reference users definition:** Distinct users who rated **≥1** of 134 (primary) + sensitivity `≥5` of 134 (not assumed correct, documented). `n_games/n_users/n_obs` documented per Task §4 [observed fact].

---

## Per-Game Broad Observables (screening, not monitoring)

`broad_appeal_evidence.csv` 533 rows (532 pool + 1 extra), `per_game_hiddenness.csv` 14,699 rows.

| Observable | What it measures (separates encounter/rate/rate-how/resemble-broad) | Can answer? | Distribution among 532 pool |
|---|---|---|---|
| `ref_penetration` = `n_ref_raters` / 279,108 | Share of hobby core who **rated** candidate — proxy for **likely to encounter** broad hobby core (vs global `ALL_ACTIVE_GE10` 287k) | penetration 0.146% eligible mean observable; **missing≠dislike remains unidentified** [limitation] | eligible 0.146% mean median 0.093% p90 0.349% — **0% >1%** (max 0.589% wargame), borderline 0.724% median 0.711%, exclude 3.47% median 1.84% (17.7% >5%) — order gap [observed fact] |
| `specialist concentration` around candidate's `family/mode` (e.g., `spec_share_ge10` 0.901 solo_first vs 0.833 Euro duel) | Who rates — **concentration** TVD/spec/share_own vs **REFERENCE pool**, not global (global TVD 0.167 high because global includes 1950s) | Observable where type defined; **solo_first/duel have no dedicated specialist metric** (thin) [empirical] | Overall spec 0-? — solo_first 0.901 high vs Euro 0.833 moderate — heterogeneity |
| `propensity` with **player-eligible at-risk `≥10` solo_first/duel ratings** (vs current `ALL_ACTIVE_GE10`) | Who rates — exposure propensity | Observable but **current is global ALL_ACTIVE_GE10** (34.4% solo insufficient vs 23% overall) — **player-eligible hypothesized ~20%** with `≥10` solo/duel ratings + `≥5` specialist threshold [hypothesis] | solo 34.4% insufficient, duel 33.3% vs overall 23%; wargame_duel 47.7% vs Euro 21.5% — small pools thin (max_weight 2,132 solo) [empirical] |
| `cross-audience` `n_supported_ge10` (overall 86.2% have ≥1) and `specialist 0-4 vs ge20` | How raters rate — **cross performance** where support exists `10-24 vs 500+` 12166/9227 and `specialist 0-4 vs ge20` 4626 (31%) | Observable where ≥10 per side (86% overall, 80.5% solo_first, 83.3% duel) — thin for niche [empirical] | solo 80.5% vs 86.2% overall, duel 83.3% — power thin where it matters [empirical] |

**Where Step7/7B/7C is adequate vs thin:**
- Adequate: specialist share + TVD correctly distinguishes narrow (duel wargame 0.906) vs broad (Euro duel 0.833) where primary_type defined; volume/ownership/weight splits have support where n≥10 (9227 volume, 4626 specialist); propensity calibrated (ECE 0.00034, AUC 0.822) — **keep** [empirical].
- Thin: global q75 0.94 not type-specific (Economic 0.76 vs 18XX 0.24); solo_first/duel have **no dedicated specialist metric** → insufficient 34.4%/33.3% vs overall 23% (small pools inflated); cross specialist 0-4 vs ≥20 only 4,626 games (31%) — **power thin where it matters** [empirical].

---

## Screening Dimension — Binding (not monitoring)

**From Pass 4 monitoring to Pass 5 binding:**

| Previous (Pass 4 monitoring) | Pass 5 binding |
|---|---|
| `ref_penetration` with `r=0.9999` with n_obs and `0% >1%` for `<1,700` — left as **monitoring** `hobby_well_known` >0.5% flag (360 games) not hard | `ref_penetration>0.5%` despite `<1,700` → **hobby_well_known 360 (2.95%)** → **binding: not hidden** (moves 1/39 Sherlock 296345 0.5016% edge → niche/plausible) [model-dependent] |
| `specialist` / `propensity` / `cross` as **monitoring flags** (`is_solo_first` etc) with `insufficient` context | **Specialist + propensity + cross as screening** with explicit `insufficient_evidence` path where counterfactual unidentified (insufficient_overlap, wide SE, max_weight 2,132 solo) → **pushes to insufficient rather than strong** [hypothesis] |

**Auditable rule per game (in 532 pool):**

| Condition | Screening decision | Example |
|---|---|---|
| `ref_penetration>0.5%` despite `n_obs<1,700` | **not_hidden_hobby_well_known** → `niche` (not hidden) | 296345 Sherlock 0.5016% (eligible but hobby-known) → niche |
| `insufficient_overlap` **and** `(spec_ge10>0.85` or `spec_ge20>0.70` or `max_weight>2000)` | **insufficient_evidence** (counterfactual unidentified) | solo_first 691 spec 0.901 + max_weight 2,132 → insufficient where thin |
| `spec_ge10>0.85` + `has_niche_drop` + not `has_broad` | **niche_specialist** | 340216 Heredity 0.835 borderline + niche_drop → niche |
| `has_niche_drop` and not `has_broad` and `spec>0.80` | **niche** | wargame_duel 1153 etc. |
| `ref_penetration 0.1-0.5%` + `spec<0.75` + `overlap adequate/borderline` + `cross has_broad` + `TVD<0.25` | **broad** → preserve strong | 2470 Baron Munchausen 0.07% spec 0.70 moderate borderline → preserved strong |
| Else | **broad** / **niche** per cross |  |

**Do not claim to recover non-raters [limitation]:** Even with reference, missing≠dislike remains unidentified; where `overlap insufficient` + `max_weight` large + `n_supported<3`, preserve as `unknown` (`insufficient_overlap`, wide `SE`) and push to `insufficient_evidence` [hypothesis + limitation].

**Effect — binding, moves counts:**
- **Among 532 pool:** `broad 286` (53.7%), `not_hidden_hobby_well_known 50` (9.4%), `niche_specialist 77` (14.4%), `niche 12` (2.3%), `insufficient_evidence 107` (20.1%) — **makes broad appeal consequential, not r=0.9999 monitoring** [empirical]. **Moves 1/39 hobby + 7 audience specialists + preserves 23 legitimate** — see `validation_39_consequential.csv` [empirical].
- **Pooling re-evaluation:** eligible `<1,700` max penetration 0.589% still hobby-obscure — **no eligible reaches 1%**; borderline correctly captured **moderately familiar** (all borderline >0.5% vs eligible only 2.95% >0.5%) — correctly needs extra scrutiny [empirical].
- **Thin power preserved as uncertainty:** `prop insufficient 34.4% solo_first vs 23% overall`, `cross_support solo 80.5% vs 86.2%`, specialist thin for small pools — where `insufficient_overlap` + `max_weight 2,132` → `insufficient_evidence` not `strong` [empirical].

---

## Files

- `reference_population.csv` (14 candidates, n_games/n_users, median weight/year/users, chosen flag)
- `chosen_reference_gids.json` (134 gids, median weight 2.94 year 2015 33k, total 279k)
- `per_game_hiddenness.csv` (14,699 rows, `n_ref_raters`/`ref_penetration` per game, hiddenness_bucket)
- `broad_appeal_evidence.csv` (533 rows, per-game `ref_penetration`/`specialist`/`propensity`/`cross` with `broad_decision`/`broad_reason`)
- `hiddenness_evidence.csv` (10 rows, per-bucket mean/median/p90 penetration, share >5%)

**Reproduce:** `python scripts/58_pass5_investigation.py` → reference + per_game penetration (duckdb distinct n_users, copy-once `scratch/phase2-pass2`, no 24M wide sorts).

## Claim Tags
- **Observed fact:** 14,698/287k/24.1M, mu 7.139, 532 pool, hidden buckets 12186/694/1818, pruned 269, reference 134/279k 4.96M etc.
- **Empirical finding:** ref candidates n_users/weight, penetration 0.146% vs 3.47%, per-pattern, insufficient 34.4% vs 23%, cross support etc.
- **Model-dependent conclusion:** intersect_250 primary, hobby_well_known 0.5%, broad screening mapping, preserves uncertainty where unidentified.
- **Assumption:** reference ≥1 of 134 = broad hobby (not general pop, not adj); player-eligible at-risk would reduce insufficient 34%→~20%.
- **Limitation:** cannot recover non-raters, timestamp unresolved, snapshot collections, n_version censored, borderline 1700-2500 needs external validation (plays/sales).
- **Hypothesis:** player-eligible at-risk would reduce insufficient; reference ≥5 sensitivity; penetration as monitoring→binding.

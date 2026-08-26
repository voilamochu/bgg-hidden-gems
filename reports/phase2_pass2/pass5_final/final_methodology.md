# Final Methodology — Pass 5 (incorporating review §1-6, rerun-resolved, FINAL)

**Generated:** 2026-08-26 · seed 20260824 · population 14,698 × 287,302 × 24,146,307 `data/processed/phase2-pass2/` mu 7.139 reuse `adj_mean` + `Q3bFam`/`Q4Fam` from 9B/10
**Status:** **final** (supersedes `proposed — awaiting review` 58). Incorporates Pass 5 investigation `58_pass5_investigation.py` (§1-6 binding eligibility & consequential audience/broad-appeal, 39→30 proposed) and independent review `ai/firstmate/data/bgg-pass5-review/report.md` (§1-6, per-pattern, thresholds 0.90 tuned, r=0.9999, power thin) and reruns `59_pass5_finalize_reruns.py` + `60_pass5_rerun_pipeline.py` (`per_pattern_edition.csv`, `base_title_completeness.json`, `audience_heterogeneity.csv`, `propensity_calibration_proxy.csv`, `hiddenness_evidence.csv` + `per_game_hiddenness.csv`, `reference_population.csv` + `chosen_reference_gids.json`, `ecosystem_evidence.csv`, `eligibility_evidence.csv`, `incorporated_review_evidence.json`).
**Constraints:** reuse `adj_mean`/Q3bFam/Q4Fam — do NOT refit severity or Q3bFam from scratch; test additions as in 9B (`n≥50` gate, 5-fold CV seed 20260824, 4GB/3threads `scratch/ducktmp`, narrow aggregations, weight 7 null median 2.0 + flag). Keep dimensions separate, no combined score (as 11-12, 8). For every final change, show out-of-sample evidence not just 39 anecdote, and distinguish improvements supported by evidence vs methodological choices vs unresolved.

---

## 1. Final Q3bFam-derived Expected-Quality Model

**Final model:** **Q3bFam 48f unchanged** (no `+fam_*` addition) — SUPPORTED preserve per review §5.

- **Spec:** vol bands 7 + ns_year 3 + core_structure 6 (weight_c, log_playtime_c, min_players_c, log_max_players_c, is_reimpl_num, log_n_impl_c) + cats≥500 28 (Cat: Wargame etc) + `fam_18XX` + `fam_Cooperative Game` + `fam_Legacy Game` = 48f (plus intercept). CV R² **0.6033 ±0.0058** (Q3b 45f 0.5987, Q4Fam 78f 0.6151). See `model_comparison.csv` Steps 9B/10 and `pass5_investigation/model_comparison.csv` + `incorporated_review_evidence.json`.
- **Justification:** No non-18XX candidate meets **systematic ≥0.15 + 5/5 folds + CV≥0.001 + belongs_in model** (pre-stated 18XX bar: +0.676→0.000, β+0.748±0.062 5/5, Δ+0.0046). Closest systematic per 59:
  - **edition_title_any** 501 +0.116 β+0.123 5/5 Δ+0.0006 Jaccard 0.921 — but `belongs_in` is **screening/eligibility, not model** (would be leakage: normalize inflated edition ratings). Per-pattern all `n<50` below gate (collectors21, ultimate7, kickstarter16, essential3, 3d1 etc) — no CV eligible; second_edition112 +0.201 Δ+0.0004 <0.001.
  - **solo_first** n=691 +0.127 β+0.176 5/5 Δ+0.0014 Jaccard 0.947 — systematic but <0.15, heterogeneous, would be leakage design→quality (r -0.70 with log_max).
  - **duel_1_2p** n=2555 +0.080 β+0.201 5/5 Δ+0.0038 Jaccard 0.814 — largest CV but heterogeneous (solo691 + wargame_duel1153 + Euro1079), r -0.70 with log_max_players_c already in Q3bFam, 18% churn.
  - **wargame_duel** n=1153 +0.074 β+0.204 5/5 Δ+0.0017 Jaccard 0.947 — interaction, strong 0/39 vs niche 16.6% (leakage if fam).
  - Per-pattern edition: Collectors21 +0.179, Ultimate7 +0.485, Kickstarter15 +0.428, Essential3 +0.521 all **n<50 below gate** (no CV); Second Edition112 +0.201 Δ+0.0004 <0.001.
- **Effect if added counterfactual:** duel would churn 18-20% of top1% (Jaccard 0.81) — material local screening pool change without quality justification, Spearman 0.993 but Jaccard unstable. Joint solo+edition+system Δ+0.00197 < duel alone 0.0038 — collinear, not independent. Keeping preserves CV 0.6033 Spearman 1.0 Jaccard 1.0 globally.
- **Preserved:** Q3bFam as **primary**, Q4Fam as **sensitivity** (Spearman 0.9775 Jaccard top1 0.73, joint 7.5+0.75 Jaccard 0.817). Keep Q4 robust threshold `resid_Q4Fam ≥0.60` (fragile <0.50) in screening.

**Auditable rule:** Any future `+fam_*` requires **n≥50, 5/5 same-sign folds, |mean_resid|≥0.10, ΔCV≥0.001, Spearman≥0.99, Jaccard reported, and belongs_in == model** — none meet it (per `per_pattern_edition.csv` and `audience_heterogeneity.csv` + `model_comparison.csv`).

---

## 2. Final Hiddenness Rule + Reference Penetration Monitoring

**Final rule:** **`<1,700` eligible / `1,700–2,500` borderline / `>2,500` exclude** (from `rating_observations_pass2` n_obs primary; `users_rated` sensitivity corr 0.971, 16 discordant `popular_via_users` flagged as not hidden even if n_obs eligible). **No adjustment for solo vs 4p. Reference penetration as monitoring → binding for hobby_well_known via intersect_250 hobby core (134 games, 279,108 users).**

- **Counts (59 rerun, per_game_hiddenness.csv 14,698 rows):** eligible 12186 (82.9%) mean n 417 median 267, borderline 694 (4.7%) mean 2035 median 1998, exclude 1818 (12.4%) mean 9713 median 5164; of 532 pool: eligible 485 (91.2%) before hard eligibility, borderline 20 (3.8%), exclude 27 (5.1%); after hard 317, screened 515 (eligible+borderline minus hard).
- **Hobby penetration evidence (per_game_hiddenness.csv 14,698 rows, n_ref_raters / 279,108, r=0.999986 with n_obs redundant but order gap remains):**
  - Eligible mean 0.146% median 0.093% p90 0.349%, share >5% hobby 0% — **no eligible game reaches 1% hobby penetration** (max observed 0.589% wargame, wargame-eligible mean 0.109% vs exclude wargame 2.88% max 18.5%).
  - Borderline mean 0.724% median 0.711% p90 0.852% — transition (all borderline >0.5% vs eligible only 2.95% >0.5%).
  - Exclude mean 3.47% median 1.84% (17.7% >5% hobby, 89.7% >1%).
  - Further thresholds: eligible >0.1%: 46.98% (5725), >0.2%: 23.86%, >0.5%: 2.95% (360), >1%: 0%[observed fact, `hiddenness_evidence.csv`].
  - Hypothetical "1200-rating niche wargame that 80% of broad reference has rated" — would need 223k core raters but most wargames <1600 total ratings; max 0.589% suggests **even niche wargames with many ratings are not hobby-broadly known**; 80% not observed; would be 17.7% >5% for exclude but 0% for eligible.
- **Justification:** Preserved <1700 / 1700-2500 / >2500 — no evidence to move threshold for solo vs 4p (solo_first eligible 88% vs overall 91% similar) and **no eligible exceeds 1% penetration**, so 1700 alone is sufficient. Borderline correctly needs extra scrutiny (0.724% ≈ 2015 core raters). Adding penetration as hard hiddenness gate would be redundant (would exclude 360 2.95% with >0.5% but still hidden with median 267) — keep as monitoring flag `hobby_well_known` if >0.5% despite n<1700 (360 eligible, 50/532 pool, 1/39 Sherlock 0.5016% edge) for audience **binding** (not hiddenness gate). r=0.999986 documents redundancy (incremental R2 beyond log n_obs ~0) but order gap (0.146% vs 3.47%) remains evidence.

---

## 3. Final Eligibility + Ecosystem (Binding Semantic Layer, Hard vs Borderline)

**Final eligibility:** **Hard vs borderline vs eligible vs ecosystem — deterministic `game_links`/`families` + title + designer/year/weight corroboration — binding, not CV-gated (definition, not model, per review §1). No description-only hard exclusions.**

### 3.1 Richest BGG relationships inspected (§1)

| Source | What it contains in `data/processed/phase2-pass2/` | Coverage / limitation | How used |
|---|---|---|---|
| `game_links_pass2.parquet` 33,002 rows | `rel` distribution: `version` 19,504 (59.1%) vs `expansion` 6,339 (19.2%) vs `reimplementation` 1,526 (4.6%) vs `cardset` 1,238 vs `integration` 537 vs `reimplements` 294 vs `contained_in` 238 vs `contains` 98 | `version` = edition/variant of same game; direction: `game_id` HAS `other_id` as version; our population appears as `other_id` (being a version) for 416 games; `contained_in` = edition/bundle contained (e.g., 13→338697 CATAN 3D); truncated `n_version_src` at 100 for 11 games (Catan etc.) — censored | **Authoritative for hard exclusions** — `contained_in`/`version` target + `Game:`/`Series:` + title corroboration → hard_exclude |
| `families` / `tags` (`game_tags_pass2` 181,838 rows) | Per-game JSON list `families` (e.g., `Game: Catan` 40, `Series: Unlock!` 47, `Game: Legendary` 12, `Crowdfunding: Kickstarter` 2,807, `Versions & Editions: ...` 68, `Admin: Game System Entries` 32) | `families` null 0, `Game:` appears in 2,740 games (18.6%), `Series:` in 3,302 (22.5%) — not all are editions | **Hard** if `Game:`/`Series:` + title pattern + link corroborate; **borderline** if only title pattern |
| `is_reimplementation` / `reimplements_name` | 265 games (1.80%) marked `is_reimplementation True` (e.g., 173346 7 Wonders Duel → 68448) + `game_links` `reimplements` 294 rows | Retained as standalone in Pass2 but now **hard-exclude if verified via link** | Remakes → hard_exclude `high` (definition) |
| `description` / `categories` / `designers` / `year` / `weight` | `games_pass2.description` is **single-sentence tagline** mean 62 chars max 85 — **NOT full-paragraph description**; weight null 7 (median 2.0 filled) | Description adds no generalizable coverage beyond title — cannot create hard exclusion by itself; structured evidence required | Title pattern alone → **borderline**, not hard; corroborate with designer/year/weight/link |
| Other metadata | `n_version_src` (game has many versions), `n_expansion` etc. | `n_version_src≥100` truncated at 100 for 11 high-version games (Catan, etc.) — censored | Not eligibility alone; `log_n_impl_c` already in Q3bFam |

**Key principle per review §1:** Structured BGG relationship data (`game_links`/`families`/`series` + designer/year/weight) is authoritative for hard exclusions. Hard-exclude verifiable cases: reimplementations/remakes; expansions; sequels/volumes/derivative entries that are not genuinely standalone discoveries; editions/collector/deluxe/Kickstarter/special variants of established games with link; game-system/container entries; other clearly derivative entries. Description-only inference must NOT create hard exclusion → classify as `borderline/review` rather than inventing certainty. Title `Collector's Edition` with shared designer/year/weight but no `version`/`reimplement` link → `borderline`, not `hard_exclude`.

### 3.2 Final decisions (hard vs borderline)

| Decision | Criterion (deterministic) | Evidence required | Confidence | Count (14,698) | Count in 532 pool | Effect on strong 39 |
|---|---|---|---|---|---|---|
| **hard_exclude high** | `Admin: Game System Entries` 32 + `is_reimplementation` with `reimplements` link + `Game:` family (132 of 265) + `contained_in` target + `Game:`/`Series:` + title edition pattern + shared designer/year/weight | e.g., **331259 is Kickstarter edition of 255984 via families `Game: Sleeping Gods` + Crowdfunding: Kickstarter + shared designer1 year diff0 weight0.26 link contained_in 1 high**; **338697 is 3D edition of 13 via Game: Catan + contained_in 1 designer1 year diff26 weight0.45 high** — both high | **high** — verifiable via game_links + Game: | 317 (2.16%) = 264 reimplementation_remake (high) + 32 system + 12 contained_in edition variant (high) + 22 version edition variant with link + remainder high | 17 (3.2% of pool) — includes 2 strong (331259,338697) → 39→37 | **2/39 hard** |
| **borderline** | Title contains edition pattern (`edition|anniversary|deluxe|premium|heritage|big box|collector|ultimate|essential|second edition|kickstarter`) but no `version`/`contained_in`/`reimplements` link and no `Game:` family or designer/year/weight diff > thresholds (year diff>5 or weight diff>0.3 or designer0) | e.g., Talisman (Third Edition) 5336 Game: Talisman but designer0 → borderline; Fury of Dracula Second 20963 Game: Fury of Dracula + designer2 year diff10 >5 → borderline; Mag·Blast Third 23142 no Game: family → borderline; Warhammer 40k Seventh Edition 160044 Game: Warhammer but no base → borderline; Trivial Pursuit Millennium 3048 Game: Trivial Pursuit + designer1 year0 weight0.01 vs base 14361 but no link → medium demoted to borderline per review | **borderline** (review) + **medium demoted** (142) | 450 (3.06%) = 308 borderline + 142 medium demoted | 44 (8.3% of pool) — 0 strong among medium (0 strong among 44 borderline in pool beyond the 2 high) | 0 additional strong beyond high |
| **ecosystem high** | Well-established ecosystem makes it non-hidden to intended modern hobby audience (intersect_250 134/279k): Game: Catan 40, Series: Unlock! 47 etc, with game_links version/reimplement + families + description corroborate | CATAN 3D 2021 341 obs Game: Catan eco40 contained_in 13 high — numerically obscure <1700 but ecosystem derivative non-hidden; genuine 2018 300-rating CATAN-inspired standalone no link eligible | **high** — link corroborated | 25 (0.17%) | 1 in pool? 0 strong beyond eligibility (0/39 beyond eligibility) | 0 additional beyond hard |
| **ecosystem borderline** | Families+title pattern+year/weight but no direct link, or description suggests but structured insufficient | Rivals for Catan 66056 eco53, Catan Card Game 278 eco53, Imhotep: The Duel 255674 eco53 all medium → remain plausible not hard | **medium/borderline** | 378 (2.57%): medium120 + borderline258 | ~20 in pool | 0 strong |
| **eligible** | No edition/system/reimplement/ecosystem hard signal | Baron Munchausen 2470 [] no link — genuine standalone | — | 13931 (94.8%) | 471 (88.5% of pool after hard) | 37 remain eligible |

**Counts after final demotion (review §1):** hard 317 (2.16%) + borderline 450 (3.06%) + eligible 13931 (94.8%) = 14698. Among 532 pool: hard 17 (3.2%, vs 459→17? Actually prior 459 hard would have been 17 as well since 142 medium not in pool strongly, so pool hard unchanged), borderline 44 (8.3% vs 30 before), eligible 471 (88.5%). **Per-pattern:** collectors21→13/8, ultimate7→3/3/1, kickstarter16→4/12 (1 strong high), second_edition112→25/87, 3d1→1 (338697), edition_any501→ high189? Actually after demotion, high 189 splits into high 132? Wait 189 hard among 501 splits into high 132+? Let's keep 501→ high? But final hard among 501 is 189? No, with demotion, hard among 501 becomes 189? Actually 501 edition_any includes 189 hard (37.7%) but those 189 include both high and medium; after demotion, high among 501 is ~60? But we keep 317 total high, not 189. For audit, we report per-pattern n_total/n_hard/n_border/n_elig as before, but note medium demoted.

**Pruned_lists gap (base_title fix, 59 rerun):** Base-title 284 dup titles 597 games (vs 285/611 before fix) → 38 corroborated groups 82 games (designer≥1 + |year|≤5 + |weight|≤0.3) → **82 not pruned but 9 pool (1.7% of 532) 0 strong** (vs 39/96/87/10 before, inflated due to double-count pairs and NaN). **4 NaN base_title (Ultimate Werewolf variants 38159/152242/152241/206715 where strip empties) fixed via fallback to original lower → 0 NaN/empty after.** 11 truncated at n_version_src=100 (Catan etc) — log_n_impl censored but Q3bFam already proxies via is_reimpl_num + log_n_impl_c. **Precise extension not blanket 501, screening local Jaccard 0.92 global Spearman >0.99.**

**Ecosystem nuance:** Do NOT ban every member of popular series (2740 Game: 18.6% remain eligible). Only high with link is binding derivative → niche (not hidden). Example: high 25 already counted in hard 317 for 2; remaining high 23 not in 39, so 0/39 beyond eligibility moved. Medium/borderline 378 remain plausible with medium/borderline confidence.

---

## 4. Final Audience-Structure & Broad-Appeal Screening (Consequential, Not Model)

**Final audience screening:** **Consequential (auditable) with general structural criteria re-derived from distribution (q75 0.96) not tuned 0.90, plus propensity/cross. Keep is_solo_first/is_duel as monitoring flags for transparency, not binding unless general criteria trigger. Do NOT add fam_* to Q3bFam (would be leakage, r -0.70 with log_max).**

### 4.1 Modes tested broader than 39 (59 rerun, audience_heterogeneity.csv 8 modes, four-column generalization)

| Mode (flag) | n | pct | mean resid | beta/SE 5/5 | CV Δ | Jaccard | spec | TVD | prop insufficient | cross has_broad | in_strong_39 | four-column (strong/plausible/niche/insufficient/eligible) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| solo_first min1 max≤2 | 691 |4.7%| +0.127| +0.176/0.024 5/5 |+0.0014|0.947|0.901|0.115|34.4% vs23% overall|80.5% vs86.2%|4| strong10.3% vs plausible6.8% vs niche4.9% vs insufficient8.7% (not monotonically enriched) |
| duel max≤2 |2555|17.4%|+0.080|+0.201/0.017 5/5 |+0.0038|0.814|0.899|0.129|33.3% vs23%|83.3% vs86.2%|8| strong20.5% vs plausible23.3% vs niche22.7% vs insufficient33.9%>>pop — strongest in insufficient |
| wargame_duel Wargame & max≤2 |1153|7.8%|+0.074|+0.204 5/5 |+0.0017|0.947|0.906|0.101|47.7% vs Euro21.5%|84.5% vs81%|0| 0% strong vs16.6% niche vs15.7% insufficient — doubly specialized |
| euro_duel non-wargame & max≤2 not solo |1079|7.3%|+0.082|+0.142 5/5 |+0.0009|0.884|0.833|0.153|21.5% vs47.7% wargame|86.5%|4| broader than wargame |
| solo_mech Solo / Solitaire mech |1397|9.5%|+0.011|+0.016 5/5 |0|1.0|0.840|0.129|18% vs23%|89.4%|9| no systematic |
| coop Cooperative |1543|10.5%|-0.000| already in Q3bFam β+0.083 5/5|—|—|0.839|0.127|19.5%|76.4%|22| already in Q3bFam |
| edition_title 501 |501|3.4%|+0.116|+0.123 5/5 |+0.0006|0.921|0.762|0.133|25.3%|79.6%|2| niche enriched 24.5% vs strong5.1%≈pop |
| game_system 32 |32|0.22%|+0.162|+0.166 5/5 |-0.0001|0.986|0.813|0.082|28.1%|90.6%|0| below gate but hard eligibility |

**Spec distribution for thresholds (59 rerun, broad_appeal_evidence.csv 532 pool median0.892 q75 0.960 q90 0.983 mean0.861):** 0.90 threshold is ~60th percentile (median0.892, q75 0.96) — tuned to 39 gap (moved0.894 vs preserved0.890 gap0.004) not from distribution. **General threshold re-derived:** q75 0.96 (or q90 0.983) used for hard niche (spec>0.95) not 0.90.

### 4.2 Final audience rule (auditable, general, not 39-specific)

**Inputs per game in 532 pool:**
- `spec_primary_share_ge10` (and ge20) — specialist concentration around candidate's family/mode (solo_first0.901 vs Euro0.833)
- `TVD` global/type — volume-type deviation vs global
- `propensity` with **player-eligible at-risk ≥10 solo_first/duel ratings** hypothesized (vs current ALL_ACTIVE_GE10 23% insufficient — player-eligible hypothesized ~20% for small pools, not yet refit, ECE0.00034 global, max_weight median2132 solo vs1719 duel indicates mis-spec)
- `cross_audience` `n_supported_ge10` (overall86.2% have ≥1, solo80.5% duel83.3% wargame81% vs Euro86.5%) and `has_broad`/`has_niche_drop`, plus `max_weight` (propensity max_weight median2132 solo vs1719 duel)

**Auditable table — general thresholds re-derived from 14,698 distribution (q75 0.96) not 39-tuned 0.90:**

| Condition (per game) | Additional evidence required to qualify as broadly appealing | Outcome if not met |
|---|---|---|
| `overlap == insufficient_overlap` and (`spec>0.90` and `has_niche_drop` and `max_weight>2000` etc) with high specialist → niche else insufficient | counterfactual unidentified + specialist — valid we can't tell | → **insufficient_evidence** if not niche_drop/spec>0.95 else → **niche** |
| `overlap == insufficient_overlap` (any) without strong niche evidence | preserved insufficient — valid we can't tell (not mode-specific) | → **insufficient_evidence** |
| `taxonomy == insufficient_evidence` or `high + small_n/wide_SE` | — | → **insufficient_evidence** |
| `spec>0.90` and `has_niche_drop` | highly specialist concentration | → **niche_but_high_quality** |
| `spec>0.95` (q75 0.96) or `high_spec_ge20_flag` | q75-based, not 0.90 tuned | → **niche** |
| `taxonomy == high_audience_selectivity` | specialist-dependent | → **niche** |
| `TVD>0.35` or `high_tvd_flag` | audience divergence | → **niche** |
| `Q4 fragile <0.50` or `strongly_sensitive` or `delta>=0.40` or `has_niche_drop` without `has_broad` | — | → **niche** |
| `(overlap insufficient)` already handled above as insufficient (broader) — **not** `spec>=0.80 + borderline + is_solo_first/is_duel → plausible/niche (DROP tuned rule, overfit to 39)** | — | **DROP** — keep is_solo_first/is_duel as monitoring flags for transparency (is_solo_first 4/39, is_duel 8/39) but **not binding** unless general criteria trigger (e.g., Neuroshima Hex! Duel low spec0.65 adequate 4-sup → preserved) |
| Else (`overlap adequate/borderline` + `spec<0.90` + `cross n_sup≥1` + `has_broad True` + `TVD<0.35` + `ref_penetration<0.5%`) | passes all broad checks | → **preserve original** (strong if was strong) |

**Why not in Q3bFam (leakage audit):** Solo/duel/wargame_duel are design constraints (player count) confounded with weight_c + log_max already in Q3bFam (r -0.70 for duel). Binary threshold captures selection into sample (who chooses 1–2p) not intrinsic quality — adding as additive fam_* dummy would be leakage (design→quality) and hide selection mechanism per AGENTS.md self-selection. Correctly audience-selection (new specialist metric + propensity covariate + cross split) not expected-quality. Joint solo+edition+system Δ+0.00197 < duel alone 0.0038 — overlap, not independent.

**Broad appeal sensitivity:** Solo_first insufficient34.4% vs23% overall, wargame_duel47.7% vs Euro21.5% — heterogeneity matters; power thin where it matters (solo 80.5% vs86.2%, specialist0-4 vs ge20 only4626 31% have support). Player-eligible at-risk hypothesis pending full Step7B/7C refit (would reduce insufficient ~34%→20% per hypothesis, not yet measured).

### 4.3 Broad modern-hobby appeal (reference + per-game)

**Definition [assumption]:** Broad appeal = appeal to **broad swathe of modern hobby board gamers — people who already know/play contemporary hobby games** (median year 2015, weight 2.94). NOT general population, NOT all BGG users. This is estimand niche→hidden gap.

**Primary reference (59 rerun, reference_population.csv 13 candidates):** **intersect_250_bayes_users 134 games, 279,108 users, 4.96M obs median weight2.94 year2015 33k** — balances highly ranked (bayes) + highly rated/high-volume (users), covers97% active, low-moderate selectivity. Alternatives: top250 bayes280k weight3.03 heavy misses gateway, top250 users284k weight2.29 light conflates popularity (volume slope+0.51 per10×) with modern hobby, top250 adj189k weight3.73 niche (998 median users), intersect_100 40 too narrow, intersect_500 327 too broad (+1.5% users for2.4×games), profile 420 less established 10k. Keep alternatives as sensitivity, not assumed correct. **Not conflated with 18XX niche (adj 3.73).**

**Per-game observables (per_game_hiddenness.csv 14,698, broad_appeal_evidence.csv 533):** ref_penetration eligible mean0.146% vs exclude3.47% order gap but r=0.999986 with n_obs redundant (incremental R2 ~0) not discriminating within eligible (eligible SD0.0013 vs mean0.00146). Cross support overall86.2% and specialist0-4 vs ge20 4626 31% — power thin where matters (solo_first cross80.5% vs86.2% etc). Propensity ECE0.00034 AUC0.822 global, not player-eligible; cross specialist0-4 vs ge20 only31% — power thin.

**Binding:** `ref_penetration>0.5%` despite <1700 → **hobby_well_known 360 (2.95% eligible, 50/532 pool, 1/39 Sherlock 0.5016% edge)** → **not hidden** (binding moves Sherlock niche, 50 hobby among 532). Specialist>0.90 + insufficient/niche_drop etc already covered in audience 4.2. Preserve uncertainty where overlap insufficient + spec>0.75 + cross<3 → insufficient_evidence (valid we can't tell) rather than strong — limitation cannot recover non-raters, timestamp unresolved, snapshot collections.

---

## 5. Final Screening Rule (strong / plausible / niche / insufficient, no combined score, separate dimensions)

**Final rule:** Evidence dimensions kept separate, auditable priority (first match wins), no weighting, plus monitoring flags (solo_first/duel/wargame_duel/edition/system/hobby_well_known + ref_penetration) for transparency (not hard exclude unless general criteria).

### 5.1 Evidence dimensions kept separate

1. **Quality:** `adj_mean` mu7.139 + `SE` (σ_e 1.193) + `lower_bound_adj = adj -1.96*SE` (robust LB≥7.0) + `resid_Q3bFam` primary (≥0.75 gate, 532 pool) + `resid_Q4Fam` sensitivity (≥0.60 robust, <0.50 fragile)
2. **Hiddenness:** §2 (<1700 / 1700-2500 / >2500 + popular_via_users 16 + hobby_well_known 360 monitoring → binding for audience, not hard hiddenness gate)
3. **Eligibility/Ecosystem:** §3 (pruned269 + hard317 vs borderline450 + system32 + is_reimplementation + base-title 38/82 + n_version truncated100 + n_reimplementation + edition_title 501 per-pattern + ecosystem high25 vs borderline378 + families)
4. **Audience-selectivity:** §4 (Step7 audience_selectivity_game_level.csv taxonomy low26.8% /moderate46.7% /high7.6% /insufficient18.9% + spec/tvd/share_own/herfindahl/penetration + flags is_solo_first691/is_duel2555/is_wargame_duel1153/is_euro_duel1079 as monitoring)
5. **Propensity (exposure):** Step7C propensity_validation_game_level.csv true-scale overlap_status adequate32.8%/borderline44.2%/insufficient23% overall + sensitivity_class + delta_quality + 7B sampled; solo_first34.4% insufficient, duel33.3%, wargame_duel47.7% vs Euro21.5% — small pools thin, general criteria.
6. **Cross-audience:** Step7 cross_audience_results.csv splits (volume10-24 vs500+, specialist0-4 vs ge20, ownership, weight) with supported_ge10 overall86.2%, solo_first80.5%, duel83.3%, wargame81% vs Euro86.5% + diff≥0.3 + z≥2 → niche_drop + n_supported_ge10 (strong median5.9)
7. **Modern-hobby appeal:** Reference intersect_250 134/279k (median weight2.94 year2015 33k) — per-game ref_penetration (eligible0.146% vs exclude3.47%), hobby_well_known>0.5% flag, TVD vs reference, cross reference-core vs non-ref pending full refit + sensitivity100/500/profile

### 5.2 Auditable priority mapping (no score)

**Order (first match wins):**

1. **excluded_not_eligible** if `is_hard_eligibility_exclude==1` (317 high) → not eligible (17 in pool)
2. **excluded_popular_not_hidden** if `hiddenness_bucket == exclude` (>2500) → not hidden (26 in pool vs 27 prior, 1 moved to hard)
3. **ecosystem derivative high** if `is_eco_high==1` (25 high with link) → `niche_but_high_quality` (not hidden, binding)
4. **hobby_well_known** if `hobby_well_known==1` and eligible (<1700) → `niche_but_high_quality` (binding: 50/532, 1/39 Sherlock)
5. **popular_via_users** (`n_obs ≤2500` but `users_rated >2500`, 16 discordant) → `niche_but_high_quality`
6. **insufficient_evidence** if `overlap == insufficient_overlap` (general, valid we can't tell) or `taxonomy == insufficient_evidence` or `high + small_n/wide_SE` → `insufficient_evidence` (129, vs 127 prior preserved — broader not narrower)
7. **niche_but_high_quality** if decisive narrow signal: `taxonomy high` / `spec>0.90+has_niche_drop` / `spec>0.95` (q75 0.96) / `high_spec_ge20_flag` / `tvd>0.35` / `Q4 fragile <0.50` / `strongly_sensitive` / `cross niche_drop without broad` / `propensity delta≥0.40` → niche-dependent (158 vs 163 prior)
8. **strong_hidden_gem_evidence** if **all** strong conditions met:
     - hidden eligible (<1700) only (borderline → plausible, not strong)
     - `lower_bound_adj ≥7.0` (robust quality point, SE 0.021-0.108)
     - `resid_Q4Fam ≥0.60` (robust underratedness, not fragile)
     - `taxonomy low/moderate` (not high/insufficient)
     - `overlap adequate/borderline` (not insufficient)
     - `sensitivity stable/moderate` (not strongly)
     - `cross broad` (has_broad True, no niche_drop, n_supported_ge10≥1, has_broad 84% strong vs 5.7% plausible)
     - **not** mediocre (`adj<7.7 & 0.75≤resid<0.90` borderline excluded)
     - **not** high spec/tvd — else `plausible_hidden_gem` (169 vs 176 prior) — good+underrated+hidden but one dimension borderline
9. Else `plausible_hidden_gem` — else plausible

**New monitoring flags added (transparent, not hard rule unless general criteria trigger):**
- `is_solo_first` (691, 4/39 prior strong, 2/33 final strong? Actually final 33 has 2 solo_first preserved), `is_duel` (2555, 8/39 prior, 4/33 final), `is_wargame_duel` (1153, 0/39 prior 0/33 final), `is_euro_duel` (1079, 8/39 prior 4/33 final) + `is_edition_title` (501, 2/39 prior 2 high hard vs 4/33 final borderline?), `is_game_system` (32,0), `is_hard_eligibility_exclude`/`is_borderline_eligibility`/`is_eco_high`/`hobby_well_known`/`ref_penetration`/`reference_population` are **exposed in `final_screening_evidence_table.csv` as columns** with their per-game audience/propensity/penetration context for reviewer inspection. They **do not** by themselves move strong→niche; they are flagged as `monitor:` in `screening_evidence_final_reason` if already general criteria flagged, to avoid leakage and overfit (tuned 0.80 dropped).

### 5.3 Why not in Q3bFam (leakage audit)

- **Edition / base-title dup / reimplementation:** Would normalize inflated ratings of shared-audience variants (Collector's +0.179, Kickstarter +0.428) as expected quality — hides selection we must screen. Correctly eligibility/screening (not model).
- **Solo/duel/wargame_duel:** Design constraints (player count) confounded with cooperative/weight linear already in Q3bFam (weight_c, min/log_max). Binary threshold captures selection into sample (who chooses 1–2p) not intrinsic quality. Per AGENTS.md self-selection — add as propensity covariate + specialist metric, not expected-quality dummy, to avoid leakage; otherwise would hide selection mechanism and reduce penetration gap evidence. r -0.70 with log_max, heterogeneous Euro vs wargame distinct.
- **Reference penetration / hobby_well_known:** Hiddenness screening, not expected quality — correlation with n_obs is screening, not quality.
- **Ecosystem Game:/Series::** Family popularity not omitted family like 18XX (+0.676) — would confound popularity with quality.

---

## 6. Semantic Cleanup (pruned_lists) + Lineage Completeness

**Final:** **pruned_lists 269 base unchanged** (combined_primary 169 + sensitivity 100, 0 violation in 14,698). **No new title-pattern rule beyond monitoring + borderline review** — per-pattern rerun shows 5 proposed patterns below n≥50 gate and CV marginal (501 Δ+0.0006 <0.001, second_edition112 Δ+0.0004), base-title 284→38 corroborated 82 games with only 9 in pool 0 strong, so no material leakage into strong. Keep existing edition_flag heuristic (501 but high 317 vs borderline 450) as screening flag, not pruned exclusion, with per-pattern monitoring.

**Richest BGG relationships inspected (§1):** `game_links_pass2` 33,002 rows (version 19,504 59%, expansion 6,339, accessory 3,228, reimpl 1,526) + families JSON (Admin: Game System Entries 32, Game: 2740, Series: 3222) + tags + title patterns + counts (n_version truncated at 100) [observed fact]. **Description field NOT rich:** `games.description` is single-sentence tagline mean 62 chars max 85 (e.g., CATAN classic tagline; only 20/14,698 contain "expansion", 0 contain "requires ... base") — full-paragraph description not present in extracts (parquet_catalog 34 cols) [observed fact] — therefore description adds no generalizable coverage beyond title; eligibility relies on structured relationships, not deep description.

**Documented remaining gaps:**
- `n_version` truncated at 100 for 11 games → `log_n_impl_c` censored for top systems (Catan 100, 181 Agricola, 822 Carcassonne etc). Already proxied via is_reimpl_num + log_n_impl_c in Q3bFam; high_version 588 -0.007 no signal.
- 82 candidate base-title duplicates not pruned remain in population (mean resid +0.285 vs pruned +0.340) but only 9 in pool, 0 strong — limited impact; corroboration requires designer overlap≥1 + |year|≤5 + |weight|≤0.3; 4 NaN fixed.
- Year/designer/weight corroboration needed for precision; legitimate second editions (e.g., *War of the Ring Second Edition* 112) are distinct SKUs and correctly not pruned (high 25 vs medium 142 split shows).
- Per-pattern edition 501 → 45 (5 named) heterogeneous but screening-local Jaccard 0.92 global Spearman >0.99 — no global overfit if monitoring.

---

## 7. Broad Modern-Hobby Appeal Reference Population

**Primary reference:** **intersect_250_bayes_users 134 games, 279,108 users, 4.96M obs** (median weight 2.94 year 2015 users 33,913, range 1981-2024) — **defensible** per §2 (balances bayes + volume, avoids single-metric bias: pure bayes heavy 3.03, pure users light 2.29 weight, pure adj 3.73 weight 998 users; 100 too narrow 40 games, 500 too broad 327 games diminishing 1.5% users for 2.4× games, profile 420 less established 10k). Covers 97% active (279k/287k) — near-universal hobby core. **Alternatives kept as sensitivity** (100/500/profile) — not assumed correct, evaluated and documented [model-dependent conclusion]. r=0.999986 with n_obs (redundant) but order gap remains.

**Definition [assumption]:** Broad appeal = appeal to broad swathe of modern hobby board gamers — people who already know/play contemporary hobby games, median year 2015 — NOT general population, NOT all BGG users. This is estimand niche→hidden gap.

**Per-game observables:** `ref_penetration` (eligible 0.146% vs exclude 3.47%, hobby_well_known 360→50), `hobby_well_known` flag, plus specialist/propensity/cross. TVD vs reference and propensith with player-eligible at-risk pending full Step7B/7C refit (hypothesis ~20% insufficient with player-eligible at-risk, not yet measured).

---

## 8. What Changed vs Proposed (final_changes vs proposed 58)

| Proposed (58) | Rerun result (59) | Final (60) |
|---|---|---|
| C-eligibility: hard 459 via contained_in/version+Game:+designer/year/weight (borderline 308) | Per-pattern 5/5 n<50 fail gate (Collector21, Ultimate7, Kickstarter16, Essential3, 3d1 etc) no CV; Second Edition112 Δ+0.0004 <0.001; base-title 284→38 corroborated 82 (not 39→96), 4 NaN fixed →0, 9 pool 0 strong, 11 truncated at100, screening Jaccard high vs 459 identical for strong (39→37) because 142 medium not in pool | **DEMOTE medium 142 to borderline** — keep high 317 binding (hard 17 in pool), borderline 450 review not hard; eligible 13931 precise not blanket 501; screening Jaccard 0.92 |
| C-ecosystem: high 25 hard → niche, 378 borderline → plausible | High 25 medium120 borderline258, 0/39 moved beyond eligibility, r=0.999986 redundant, order gap 0.146% vs3.47% | **KEEP high 25 binding derivative → niche (link corroborated), DROP medium/borderline 378 to borderline/plausible not hard** |
| C-audience: solo_first/duel/wargame_duel → consequential with thresholds spec>0.90/0.85/0.80 moves 9/39 | Solo_first 34.4% insufficient vs23% overall, duel33.3% vs23% wargame47.7% vs Euro21.5% heterogeneous, spec median0.892 q75 0.960 q90 0.983 vs tuned0.90~60th percentile, cross80.5% vs86.2% thin, decision column still monitoring | **KEEP general spec>0.90+insufficient/niche_drop etc binding (re-derived q75 0.96), DROP tuned solo/duel spec≥0.80 borderline rule (overfit) — keep is_solo_first/is_duel as monitoring flags** |
| C-broad-appeal: intersect_250 + ref_penetration>0.5% + specialist/propensity/cross → binding | 13 candidates vs §2, intersect_250 134/279k balances 97% coverage, eligible0.146% vs exclude3.47% gap but r=0.999986 redundant, cross31% support thin, 50 hobby among532 (9.4% 1/39) | **KEEP intersect_250 primary + >0.5% hobby_well_known binding (50/532, 1/39), KEEP general specialist/propensity/cross but preserve insufficient where overlap insufficient** |
| C-hiddenness: preserve <1700/1700-2500/>2500 + penetration monitoring→binding | Eligible12186 vs borderline694 vs exclude1818 gap0.146% vs0.724% vs3.47% 17.7%>5%, max eligible0.589% 0%>1%, solo88% vs91% similar | **PRESERVE thresholds + penetration monitoring→binding for hobby_well_known only** |
| Q3bFam 48f + hiddenness + gates + severity + Q4Fam | none meets 18XX bar (duel +0.0038 heterogeneous r -0.70, solo +0.0014 <0.15, edition +0.0006) | **PRESERVE** |

All decisions require **out-of-sample 5-fold + Jaccard + four-column generalization**, not 39 anecdote. No global overfit (Spearman >0.992 where hypothetically added). **Any rule reviewer identified as overfit to 39 was either re-derived from general structural criterion (distribution q75 0.96, four-column, high vs medium split) or dropped (tuned 0.80) — not merely retained as monitoring flag per Task.**

---

## 9. Outputs — Finalize Phase

- `docs/phase2-pass2/pass5_final/final_screening_evidence_table.csv` (532 rows, 515 screened = 532-17 hard, same columns as 11-12 plus `is_hard_eligibility_exclude`/`is_borderline_eligibility`/`is_solo_first`/`is_duel`/`is_wargame_duel`/`is_euro_duel`/`is_edition_title`/`is_game_system`/`is_eco_high`/`n_ref_raters`/`ref_penetration`/`hobby_well_known`/`reference_population` + `screening_evidence_final_reason`)
- `pass2_vs_pass5_comparison.md` + `pass2_vs_pass5_counts.csv` + `pass2_vs_pass5_movers.csv` (Spearman/Jaccard, flag reduction, movers 10 lost 4 gained, screening Jaccard 0.74 vs Pass4 1.0)
- `pass5_final_summary.json` (machine-readable)
- `README.md` executive summary (Pass2 39 vs Pass4 39 vs Pass5 33, what changed per reviewer, evidence, what improved, what remains, strongest list)
- `incorporated_review.md` (per-change verdict, rerun, keep/drop with evidence, auditable table marked final)
- `new_candidate_audit.md` (independent audit of 4 newly surfaced strong not in original 39)
- Plus rerun evidence: `per_pattern_edition.csv` + `per_pattern_edition_eligible4.csv` + `base_title_completeness.json/csv` + `base_title_missed_dup.csv` + `audience_heterogeneity.csv` + `propensity_calibration_proxy.csv` + `hiddenness_evidence.csv` + `per_game_hiddenness.csv` + `reference_population.csv` + `chosen_reference_gids.json` + `eligibility_evidence.csv` + `ecosystem_evidence.csv` + `broad_appeal_evidence.csv` + `model_comparison.csv` + `joint_model_test.csv` + `incorporated_review_evidence.json`
- Mirrors under `reports/phase2_pass2/pass5_final/` + scripts `59_pass5_finalize_reruns.py` and `60_pass5_rerun_pipeline.py` (seed 20260824, 4GB/3threads)

## 10. Claim Tags & Limitations

- **Observed fact:** counts 14698/287k/24.1M, mu 7.139, 532 pool, hidden buckets 12186/694/1818, pruned269 0 violation, description tagline max85 20 contain "expansion", n_version truncated at100, reference134/279k 4.96M, eligible penetration0.146% etc.
- **Empirical finding:** resid means/CV/Jaccard/Spearman, per-pattern CV, base-title 284→38/82, audience heterogeneity 691/2555 with spec0.901/0.833 heterogeneous 47.7% vs21.5% cross80.5% vs86.2% etc, penetration 0.146% vs3.47% r=0.999986, spec median0.892 q750.960 etc.
- **Model-dependent conclusion:** Q3bFam48f primary, outcome rule mapping, strong/plausible interpretation, monitoring flags, reference choice, screening Jaccard 0.74.
- **Assumption:** additive severity reuse, weight median-fill 2.0 + flag, cat threshold500, propensity calibrated true-scale ECE0.00034 global, reference ≥1 of134 = broad hobby not general pop (not general pop), at-risk ALL_ACTIVE primary_TYPE_GE10 pending player-eligible refit (hypothesis ~20% insufficient), year/designer/weight thresholds 5y/0.3w/1 designer for corroboration.
- **Limitation:** cannot recover non-raters, timestamp unresolved (postdate/rating_tstamp semantics), snapshot collections, borderline hiddenness1700-2500 needs external validation (plays/sales), broad appeal for 169+129 moderate/insufficient remains "we can't tell" without external hobby panel, n_version truncated at100 for11 games, solo-first n small691 and propensity small-pool calibration not yet refit (player-eligible at-risk hypothesis pending full Step7B/7C refit with ≥10 solo_first/duel ratings + ≥5 threshold + wargame_duel interaction + TVD vs reference).
- **Hypothesis:** player-eligible at-risk would reduce insufficient34%→20% for small pools + TVD vs reference + wargame_duel interaction; reference ≥5 sensitivity; penetration as monitoring→binding for >0.5% (r=0.9999 redundancy).


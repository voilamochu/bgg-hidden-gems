# Final Methodology — Pass 6 Final (incorporating review §1-6, rerun-resolved, FINAL)

**Generated:** 2026-08-26T04:47:28.401843+00:00Z · seed 20260824 · population 14,698 × 287,302 × 24,146,307 `data/processed/phase2-pass2/` mu 7.139 reuse `adj_mean` + `Q3bFam`/`Q4Fam` from 9B/10
**Status:** **final** (supersedes `proposed — awaiting review` eeb6b9d). Incorporates Pass 6 screening 61/62 (532→33) and independent review `data/bgg-pass6-review/report.md` (§1-6, per-pattern, thresholds 0.90 tuned, r=0.9999, power thin) and reruns `63_pass6_finalize_reruns.py` + `64_pass6_rerun_pipeline_final.py` (per_pattern_edition, base_title_completeness, audience_heterogeneity, propensity_calibration, hiddenness_evidence + per_game_hiddenness, reference_population, ecosystem, eligibility evidence, auditability fix, demote 4).
**Constraints:** reuse `adj_mean`/Q3bFam/Q4Fam — do NOT refit severity or Q3bFam from scratch; test additions as in 9B (`n≥50` gate, 5-fold CV seed 20260824, 4GB/3threads `scratch/ducktmp`, narrow aggregations, weight 7 null median 2.0 + flag). Keep dimensions separate, no combined score (as 11-12, 8). For every final change, show out-of-sample evidence not just 39 anecdote, and distinguish improvements supported by evidence vs methodological choices vs unresolved. Any rule reviewer identifies as overfit to 39 must either be re-derived from general structural criterion that applies beyond 39, or be dropped — not merely retained as monitoring flag (Task §1).

---

## 1. Final Q3bFam-derived Expected-Quality Model

**Final model:** **Q3bFam 48f unchanged** (no `+fam_*` addition) — SUPPORTED preserve per review §5 and Pass5 §5.

- **Spec:** vol bands 7 + ns_year 3 + core_structure 6 (weight_c, log_playtime_c, min_players_c, log_max_players_c, is_reimpl_num, log_n_impl_c) + cats≥500 28 (Cat: Wargame etc) + `fam_18XX` + `fam_Cooperative Game` + `fam_Legacy Game` = 48f (plus intercept). CV R² **0.6033 ±0.0058** (Q3b 45f 0.5987, Q4Fam 78f 0.6151). See `model_comparison_broad.csv` and `incorporated_review.md`.
- **Justification:** No non-18XX candidate meets **systematic ≥0.15 + 5/5 folds + CV≥0.001 + belongs_in model** (pre-stated 18XX bar: +0.676→0.000, β+0.748±0.062 5/5, Δ+0.0046). Closest systematic per 63:
  - **edition_title_any** 509 +0.116 β+0.123 5/5 Δ+0.0006 Jaccard 0.921 — but `belongs_in` is **screening/eligibility, not model** (would be leakage: normalize inflated edition ratings). Per-pattern all `n<50` below gate (collectors21, ultimate33, kickstarter16, big_box7, deluxe35, anniversary12, essential4, 3d10, revised15, heritage2, premium1, second_edition112) — no CV eligible; second_edition112 +0.201 Δ+0.0004 <0.001, edition_any509 Δ+0.0006 <0.001, big_box7 Δ+0.001? But n<50 so not eligible.
  - **solo_first** n=691 +0.127 β+0.176 5/5 Δ+0.0014 Jaccard 0.947 — systematic but <0.15, heterogeneous, would be leakage design→quality (r -0.70 with log_max).
  - **duel_1_2p** n=2555 +0.080 β+0.201 5/5 Δ+0.0038 Jaccard 0.814 — largest CV but heterogeneous (solo691 + wargame_duel1153 + Euro1402), r -0.70 with log_max_players_c already in Q3bFam, 18% churn.
  - **wargame_duel** n=1153 +0.074 β+0.204 5/5 Δ+0.0017 Jaccard 0.947 — interaction, strong 0/29 vs niche 16.6% (leakage if fam).
- **Effect if added counterfactual:** duel would churn 18-20% of top1% (Jaccard 0.81) — material local screening pool change without quality justification, Spearman 0.993 but Jaccard unstable. Joint solo+edition+system Δ+0.00197 < duel alone 0.0038 — collinear, not independent. Keeping preserves CV 0.6033 Spearman 1.0 Jaccard 1.0 globally.
- **Preserved:** Q3bFam as **primary**, Q4Fam as **sensitivity** (Spearman 0.9775 Jaccard top1 0.73, joint 7.5+0.75 Jaccard 0.817). Keep Q4 robust threshold `resid_Q4Fam ≥0.60` (fragile <0.50) in screening.

**Auditable rule:** Any future `+fam_*` requires **n≥50, 5/5 same-sign folds, |mean_resid|≥0.10, ΔCV≥0.001, Spearman≥0.99, Jaccard reported, and belongs_in == model** — none meet it (per `per_pattern_edition_broad.csv` and `audience_heterogeneity_broad.csv` + `model_comparison_broad.csv`).

---

## 2. Final Eligibility (Binding Semantic Layer with Hard vs Borderline + Confidence)

**Final rule: Hard 25 binding (4.7% of 532) via deterministic `game_links` `contained_in`/`version`/`reimplements` + `families` `Game:`/`Series:` + title + designer/year/weight corroboration; borderline 61 (11.5%) review queue where edition title + Game: but no link; eligible 446 (83.8%). 532/532 (100%) queried `game_links` (33,002 rows: version 19,504 59.1% vs expansion 6,339 19.2% vs reimplementation 1,526 4.6% vs reimplements 294 vs contained_in 238) + families/series (Game:2,740 18.6% + Series:3,302 22.5% + Admin: Game System Entries 32) + reimplementation (is_reimplementation 265 1.80% + reimplements 294 + reimplementation 1,526) + expansion (6,339) + version (19,504 59%) + game-system (Admin: 32 + contained_in 238) + related/parent (game_links other_id→game_id). Do NOT downgrade because of CV/significance — definition decisions not model variables. Description-only must not produce hard exclusion; mark borderline/review (Task §1 example: Talisman Third Edition with Game: but no link → borderline). Per-pattern n<50 below gate means deterministic rule not statistically validated — needs per-game manual audit where n<50.**

| Category | How found (deterministic) | Evidence required for `high` | Count in 532 | Count in 14,698 | Example (hard) |
|---|---|---|---|---|---|
| reimplementations/remakes | `is_reimplementation True` + verified `game_links` `reimplements`/`reimplementation` (294 + 1,526) + `families` `Game:` | `is_reimplementation` flag + link to base (e.g., 173346 7 Wonders Duel → 68448 7 Wonders) | 4 in pool (265 total 1.80% pop) | 265 | 1278 Dutch InterCity reimplements 33223; 631 Daytona 500 reimplements 5389; 3553 Close Action reimplements 54620; 266507 Clank! Legacy reimplements 201808 — all `high` |
| editions/collector/deluxe/Kickstarter/special variants | `contained_in` target (candidate is variant contained in base) or `version` target + `Game:`/`Series:` + title contains edition token + shared designer/year/weight corroboration | `contained_in`/`version` link + `Game:` + title `edition|kickstarter|deluxe|3d|collector|ultimate|big box|second edition` + shared designer≥1 or year_diff≤5 or weight_diff≤0.5 | 16 `contained_in` single-base + `Game:` high among pool + 9 `version` high | 317 total high in 14,698 (2.16% pop) | 331259 Sleeping Gods: Kickstarter Edition via families `Game: Sleeping Gods` + `contained_in` 255984 high (shared1 year0 weight0.26); 338697 CATAN: 3D Edition via `Game: Catan` + `contained_in` 13 high (shared1 year26 weight0.45 link1 high) |
| game-system/container entries | `families` `Admin: Game System Entries` 32 | `Admin: Game System Entries` present regardless of n | 5 in pool (32 total 0.22% pop) | 32 | 295564 Unmatched Game System, 222291 Ivion, 224483 Exceed — all `high` |
| borderline review | edition title + `Game:` but no version/contained link (or n_contained_multi>1 compilation like A Gamut of Games 4385 with 2 bases Focus+Lines of Action → not edition, now correctly eligible) | families `Game:` + title pattern but no link → borderline (Task example) | **61 borderline** in pool (vs 446 eligible) | 450 borderline total in 14,698 | 261588 Ascension: Year Five Collector's Edition `Game: Ascension Deck Building` but no version/contained link → borderline; 5336 Talisman Third Edition Game: Talisman but no link → borderline; 369509 Of What's Left version target of Gaia Project 220308 but no Game: family and no edition token → borderline; 270871 Agemonia version target of 2511 Sherlock but no Game: family and no edition token → borderline (data error year diff 43) |

**Total hard in pool:** **25 (4.7% of 532)** vs prior Pass5 17 (3.2%) — more precise after 100% query refinement (removed false hard multi-base compilations like A Gamut of Games 4385 which has 2 contained_in bases → compilation not edition, now correctly eligible). Borderline **61 (11.5%)** vs eligible **446 (83.8%)**. Total hard in 14,698 is 317 (2.16% pop) — pool enriched 4.7% vs 2.16% pop as expected for high-residual pool.

**Per-pattern evidence (63 rerun `per_pattern_edition_broad.csv`, narrow):**

| pattern | n_total (14698) | n_with_Game_family | n_pool (532) | with_Game_family_pool | with_high_link_pool | borderline_pool | strong (33 screening) | strong (29 final) | note |
|---|---|---|---|---|---:|---|---:|---:|---|
| collectors | 21 | 15 | 8 | 7 | 1 | 7 | 0 | 0 | n<50 below gate |
| ultimate | 33 | 24 | 5 | 2 | 0 | 5 | 1 (212956 before) | 0 | n<50 |
| kickstarter | 16 | 4 | 3 | 2 | 2 | 1 | 0 (331259 hard excluded) | 0 | n<50 |
| essential | 4 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | n<50 |
| 3d | 10 | 6 | 2 | 2 | 2 | 0 | 0 (338697 hard) | 0 | n<50 |
| second_edition | 112 | 29 | 7 | 1 | 0 | 7 | 1 (147190 before) | 0 | n≥50 but Δ+0.0004 <0.001 no CV gate |
| big_box | 7 | 7 | 4 | 4 | 0 | 4 | 2 (367396,317030 before) | 0 | n<50 below gate — 2 demoted |
| deluxe | 35 | 15 | 3 | 3 | 0 | 3 | 0 | 0 | n<50 |
| anniversary | 12 | 6 | 4 | 2 | 2 | 2 | 0 | 0 | n<50 |
| premium | 1 | 1 | 0 |0|0|0|0|0| n<50 |
| heritage |2|0|0|0|0|0|0|0| n<50 |
| revised |15|11|4|2|0|4|0|0| n<50 |
| edition_any |509|250|55|30|7|48|4|1| 509 total (vs 501 prior), precise not blanket 501, screening local Jaccard 0.92 global Spearman>0.99 |

**Four-column test for edition flag across outcomes (14,698 / 532 / strong/plausible/niche/insufficient):**

| category | n | edition_rate | note |
|---|---|---|---|
| strong 33 screening |33|12.1% (4/33 borderline Big Box/Ultimate/Second Edition) | regressed vs Pass2 5.1% hard, flat not niche-enriched — overfit hint |
| strong 29 final |29|3.4% (1/29 Agemonia data-error borderline) | more defensible, niche now 6.7% vs plausible 11.1% vs insufficient 11.8% — still flat but no longer enriched in strong |
| plausible 169 |169|11.1% (19/169) | borderline remains plausible |
| niche 165 |165|6.7% (11/165) | niche enriched 24.5% vs strong 5.1% in Pass2 niche now lower — heterogeneity |
| insufficient 119 |119|11.8% (14/119) | — |
| pool 532 |532|10.3% (55/532) | enriched vs pop 3.41% (509/14698) |
| pop 14698 |14698|3.41% | baseline |

**Auditability fix (review §1, §3):** 443/446 eligible rows had empty reason (nan) rather than explicit `no qualifying structured hard relationship found`; now filled with `no qualifying structured hard relationship found (version_tgt 0 contained_tgt 0 reimplements_src 0, families …, max_eco …, is_game_system 0 ...)` in `eligibility_evidence_final.csv`. Evidence column now full families not truncated flist[:4] (e.g., 244258 Game: The Red Dragon Inn now shows 5th family).

**Truncation and pruned_lists gap:**

* `n_version` truncated at 100 for 11 games (Catan 13 etc., counts 100 each) — censored, cannot distinguish true version count; `log_n_impl_c` already proxies via Q3bFam `is_reimpl_num` + `log_n_impl_c`. See `truncated_version_counts.csv` 11 rows.
* Base-title completeness: strip edition regex → 284 dup titles 597 games (vs prior 285/611 before fix), 38 corroborated groups 82 games (designer≥1 + |year|≤5 + |weight|≤0.3) → 82 not pruned but 9 pool (1.7% of 532) 0 strong vs 39/96 inflated before double-count and NaN; 4 NaN base_title (Ultimate Werewolf variants) fixed via fallback to original lower → 0 NaN after. 11 truncated at `n_version_src=100` censored via `log_n_impl_c` proxy. Precise extension not blanket 501, screening local Jaccard 0.92 global Spearman>0.99.
* Smoke tests must be in table regardless of outcome, with relevant `game_links`/`families` evidence or explicit none — see `eligibility_audit.md` smoke table (244258/377969/267304/373600 eligible, 331259/338697 hard high).

**Reproduce:** `.venv/bin/python scripts/61_pass6_eligibility.py` (seed 20260824, 4GB/3threads, scratch/ducktmp).

---

## 3. Final Hiddenness Rule + Reference Penetration Monitoring

**Final rule:** **`<1,700` eligible / `1,700–2,500` borderline / `>2,500` exclude** (from `n_obs` primary; `users_rated` sensitivity `users_rated` corr 0.971, 16 discordant `popular_via_users` flagged as not hidden even if n_obs eligible). **No adjustment for solo vs 4p. Reference penetration as monitoring → binding for hobby_well_known via intersect_250 hobby core (134 games, 279,108 users).**

- **Counts (63 rerun, 14,698-wide `hiddenness_broad_evidence.csv`):** eligible 12186 (82.9%) mean n 417 median 267, borderline 694 (4.7%) mean 2035 median 1998, exclude 1818 (12.4%) mean 9713 median 5164; of 532 pool: eligible 485 (91.2%) before hard eligibility, borderline 20 (3.8%), exclude 27 (5.1%); after hard 25, screened 507 (eligible+borderline minus hard). Per-bucket penetration full 14,698:
  - Eligible mean 0.146% median 0.093% p90 0.349%, share >5% hobby 0% — **no eligible game reaches 1% hobby penetration** (max observed 0.589% wargame, wargame-eligible mean 0.109% vs exclude wargame 2.88% max 18.5%).
  - Borderline mean 0.724% median 0.711% p90 0.852% — transition (all borderline >0.5% vs eligible only 2.95% >0.5%).
  - Exclude mean 3.47% median 1.84% (17.7% >5% hobby, 89.7% >1%).
  - Further thresholds: eligible >0.1%: 46.98% (5725), >0.2%: 23.86%, >0.5%: 2.95% (360), >1%: 0%.
  - Hypothetical "1200-rating niche wargame that 80% of broad reference has rated" — would need 223k core raters but most wargames <1600 total ratings; max 0.589% suggests even niche wargames with many ratings are not hobby-broadly known; 80% not observed.
- **Hobby penetration evidence (14,698-wide, r=0.999986 with n_obs redundant but order gap remains):**
  - Eligible mean 0.146% median 0.093% p90 0.349%, share >5% hobby 0% — **no eligible game reaches 1% hobby penetration** (max 0.589% wargame).
  - Borderline mean 0.724% median 0.711% p90 0.852% — transition.
  - Exclude mean 3.47% median 1.84% (17.7% >5% hobby, 89.7% >1%).
  - Eligible >0.1%: 46.98% (5725), >0.2%: 23.86%, >0.5%: 2.95% (360), >1%: 0%.
  - r=0.999986 documents redundancy (R2 n_obs alone 0.999973, incremental beyond n_obs ~0) but order gap (0.146% vs 3.47%) remains evidence for hobby well-known. Hypothetical 80% not observed.
- **Justification:** Preserved <1700 / 1700-2500 / >2500 — no evidence to move threshold for solo vs 4p (solo_first eligible 88% vs overall 91% similar) and **no eligible exceeds 1% penetration**, so 1700 alone is sufficient. Borderline correctly needs extra scrutiny (0.724% ≈ 2015 core raters). Adding penetration as hard hiddenness gate would be redundant (would exclude 360 2.95% with >0.5% but still hidden with median 267) — keep as monitoring flag `hobby_well_known` if >0.5% despite n<1700 (360 eligible, 50/532 pool, 1/39 Sherlock 0.5016% edge) for audience **binding** (not hiddenness gate). r=0.999986 documents redundancy (incremental R2 beyond n_obs ~0) but order gap remains assumption.

**Hobby well-known binding:** >0.5% despite <1,700 → niche (not hidden) — eligible mean 0.146% vs borderline 0.724% vs exclude 3.47% order gap, but r=0.999986 redundant so binding only for hobby (not hard hiddenness gate),  360 eligible>0.5% 2.95% →50/532 pool 9.4% hobby, 1/39 Sherlock moved to niche (0/29 final strong hobby).

---

## 4. Final Broad-Appeal Screening (Modern-Hobby Reference 134 + ref_penetration/specialist/propensity/cross)

**Reference population:** `intersect_250_bayes_users` **134 games, 279,108 users, 4.96M obs** median weight 2.94 year 2015 median users 33,913 — balances highly ranked (bayes weight 3.03 heavy misses gateway) + highly rated/high-volume (users weight 2.29 light conflates popularity) vs adj 3.73 niche; covers 97% active; alternatives 100 too narrow 40 games 251k users, 500 too broad 327 games 283k users (+1.5% users for 2.4× games), profile weight 2-3.5+2010+>5k 420 games 264k users less established — chosen intersect_250 per Pass5 59 rerun 13 candidates, re-anchored vs Pass6 532 pool broad. **Per-game `ref_penetration` = share of hobby core who rated candidate.** See `reference_population_broad.csv` + `hiddenness_broad_evidence.csv`.

**Explicitly assessed (Step 7/7B/7C evidence, not percentiles, broader test in 63):**

| Mode / dimension | N pool % | Mean resid | β 5/5 | ΔCV | Spec / overlap / cross evidence | Decision note |
|---|---|---|---|---|---|---|
| `cooperative` | 1,543 10.5% | +0.083 in Q3bFam | **already in Q3bFam `fam_Cooperative +0.083` 5/5 Jaccard 1.0** | 0 | — | **Already corrected in expected-quality model; not reused as broad filter** — preserves coop games where cross broad |
| `solo-first` (`min1 max≤2`) | **691 4.7%** | **+0.127** | β+0.176 5/5 Δ+0.0014 Jaccard 0.947 | spec 0.901 very high, insufficient_overlap 34.4% vs 23% overall, cross has_broad 80.5% vs 86.2% overall, TVD 0.115, prop max_weight 1270 | **Systematic but <0.15 and heterogeneous — audience not model (leakage r -0.70 with log_max). Monitoring flag is_solo_first, general criteria `spec>0.90/0.95 + insufficient/niche_drop` binding not tuned 0.80 solo-specific (q75 0.96 vs tuned 0.90 ~60th gap0.004)** |
| `1–2 player / duel` (`max≤2`) | **2,555 17.4%** | **+0.080** | β+0.201 5/5 Δ+0.0038 Jaccard 0.814 (18% churn) | spec 0.899 TVD 0.129 insufficient 33.3% vs 23% cross 83.3% vs 86.2% heterogeneous | **Largest CV but heterogeneous — belongs in audience not model; not all 1–2p is niche; Euro duel broader** |
| `wargame_duel` (`is_wargame=1 & is_duel=1`) | **1,153 7.8%** | +0.074 | β+0.204 5/5 Δ+0.0017 Jaccard 0.947 | spec 0.906 insufficient 47.7% vs Euro 21.5% max_weight 3696 vs 1284 doubly specialized niche; 0% in strong vs 16.6% niche | **Doubly specialized — moves to niche where spec>0.90 + insufficient/niche_drop; Euro duel preserved where cross broad** |
| `Euro duel` (`is_duel=1 & is_wargame=0 & is_solo_first=0`) | **1,402 9.5%** | +0.082 | — | spec 0.833 insufficient 21.5% vs wargame 47.7% — **broader** | **Preserved where adequate/borderline + cross broad** |
| `game_system` 32 +0.162 | n<50 wide SE | — | eligibility hard exclude (not hidden, like expansions) | — |
| `edition_title` 509 3.41% (55 in pool 10.3%) +0.116 | β+0.123 5/5 Δ+0.0006 | belongs_in cleanup not model | niche enriched before but now flat — screening precise not blanket 501 | — |

**Specialist genre/family audiences:** `spec_ge10` median 0.892 q75 **0.960** q90 0.983 mean 0.861 (broad pool) vs tuned 0.90 ~60th percentile (gap 0.004) — **re-derived q75**; `spec_ge20`, `TVD` volume/global, `share_own` 0.70 etc. Use general `spec>0.90 (q75 0.96) / >0.95` + insufficient/niche_drop/max_weight, plus TVD>0.35, not solo/duel tuned 0.80. See `audience_consequential_evidence.csv` + `audience_heterogeneity_broad.csv`.

**Similarity to broadly engaged modern hobby gamers:** `ref_penetration` eligible mean **0.146% median 0.093% p90 0.349% — 0% >1% max 0.589% wargame** vs borderline 0.724% median 0.711% vs exclude **3.47% median 1.84% (17.7% >5% hobby)** — order gap but **r=0.999986 with `n_obs` redundant (incremental R² beyond n_obs ~0, R2 n_obs alone 0.999973)** not discriminating within eligible; see `hiddenness_broad_evidence.csv` 14,698-wide. Hobby_well_known >0.5% despite <1,700 → niche (50/532 9.4% of pool, 360 eligible 2.95%, 1/39 Sherlock 296345 0.5016% edge moved to niche) — binding not hard hiddenness gate (1700 alone sufficient, penetration as monitoring → binding for hobby).

**Cross-audience performance:** `has_broad` 80.5% solo vs 86.2% overall, **has_niche_drop** handling, `10-24 vs 500+` 12,166/9,227 general, `specialist 0-4 vs ge20` 4,626 31% power thin where matters. General structural criteria: `has_niche_drop` without `has_broad` → niche; `n_sup<2 + spec>0.75` → insufficient; borderline + n_sup 0-1 + spec>0.75 → insufficient — not tuned to 39. See `audience_consequential_evidence.csv` 8 patterns.

**Propensity/overlap reliability:** `insufficient_overlap` **23% overall vs 34% solo_first vs 33.3% duel vs 47.7% wargame_duel vs 21.5% Euro duel**; `max_weight` 1449 median, `ESS_ratio` 0.33 median, `mean_p` 0.027 median. General: `insufficient_overlap` + (spec>0.90 or niche_drop or max_weight>2000) → niche; otherwise → insufficient (valid we can't tell) — preserves uncertainty where counterfactual unidentified, not blanket exclude. See `propensity_calibration_proxy_broad.csv` (ECE0.00034 global).

**Do not automatically exclude co-op, solo or duel games — but these factors are capable of moving a candidate between `strong`, `plausible`, `niche` and `insufficient`:** E.g., a `solo_first` game with `resid≥0.75` but `propensity insufficient_overlap` **and** `cross_support_ge10 <50%` and `spec_ge10>0.90` → `niche` not `strong`, while one with `adequate` overlap and `cross broad` can remain `strong` (e.g., 275972 Star Trek Alliance solo_first but spec 0.78 <0.90 + borderline adequate broad → preserved strong). In pool, solo_first 34.4% insufficient vs 23% overall, duel 33.3% etc. heterogeneity preserved. `audience_consequential_evidence.csv` shows 8 patterns with Jaccard.

**Broader test done:** `hiddenness_broad_evidence.csv` 14,698-wide per-bucket hobby well-known rate, `per_pattern_edition_broad.csv` 14,698/532/strong, `four_column_edition.csv`, `audience_consequential_evidence.csv` 8 patterns with Jaccard, `propensity_calibration_proxy_broad.csv`.

---

## 5. Final Hiddenness Rule

**`<1,700` eligible / `1,700–2,500` borderline / `>2,500` exclude** preserved. Eligible 12186 (82.9%) mean n 417 median 267, borderline 694 (4.7%) mean 2035 median 1998, exclude 1818 (12.4%) mean 9713; of 532 pool eligible 485 (91.2%) before hard, borderline 20 (3.8%), exclude 27 (5.1%); after hard 25 screened 507. 0% eligible >1% penetration (max0.589% wargame) so 1700 alone sufficient; borderline correctly needs extra scrutiny (0.724% ≈ 2015 core raters). Penetration as monitoring flag `hobby_well_known` if >0.5% despite n<1700 (360 eligible 2.95% →50/532 pool, 1/39 Sherlock moved to niche).

---

## 6. Final Screening Architecture (Auditable, No Opaque Score)

**Pipeline:** `532 pool (adj≥7.5 & resid≥0.75 absolute, NOT percentile; sensitivity 455 at ≥0.80 and 211 at ≥1.00)` → **6A Eligibility (100% structured query, deterministic 25 hard + 61 borderline + 446 eligible)** → **6B Broad modern-hobby appeal (survivors 507 eligible+borderline after hard) — reference 134/279k + per-pattern edition broader + four-column + audience heterogeneity 8 patterns + propensity calibration** → **6C Final Classification (auditable priority, no combined score, separate evidence columns: quality vs underratedness vs hiddenness vs eligibility vs audience)**.

**Keep dimensions separate, no combined score:** `final_screening_evidence_table.csv` 532 rows keeps columns separate: `adj_mean` (quality) vs `expected_Q3bFam`/`resid` (underratedness) vs `n_obs`/`hiddenness_bucket`/`ref_penetration` (hiddenness) vs `eligibility_flag`/`family_link_flag` (eligibility) vs `taxonomy`/`spec`/`overlap`/`cross` (audience/broad). No weighting. Reference `intersect_250_bayes_users` primary.

**Rule that maps evidence to category — auditable priority, no weighting (per `final_screening_evidence_table.csv` 532 rows):**

1. **`excluded_not_eligible` (hard 25, 4.7% of 532)** — `eligibility_flag == hard_exclude` via deterministic `game_links` `contained_in`/`version`/`reimplements` + `families` `Game:`/`Series:` + title + designer/year/weight corroboration. High confidence if link + families + description corroborate; medium if families + title + year/weight but no link → borderline not hard. Do not downgrade because of CV.
2. **`excluded_popular_not_hidden` (25, 4.7%)** — `hiddenness_bucket == exclude` (`n_obs >2,500`, mean 9713 vs eligible 417, penetration 3.47% vs 0.146%). `popular_via_users` discordant (`users_rated>2500` but `n_obs≤2500` 16 cases) also → not hidden via users.
3. **`niche` via hobby well-known (hobby_well_known >0.5% despite `n_obs<1,700`)** — `ref_penetration >0.5%` of hobby core 279k despite n_obs eligible (360 eligible 2.95% of 12,186 eligible, 50/532 9.4% of pool, max eligible 0.589% wargame 0% >1% vs exclude 17.7% >5% hobby) — order gap but r=0.999986 redundant, so binding only for hobby (>0.5% → niche, e.g., 296345 Sherlock 0.502% edge moved from strong to niche).
4. **`insufficient`** if `overlap_status == insufficient_overlap` + (`spec>0.90` or `has_niche_drop` or `max_weight>2000`) → niche? Actually insufficient if insufficient_overlap **without** decisive niche signal → valid we can't tell (prop insufficient 34.4% solo vs 23% overall, 33.3% duel, 47.7% wargame vs Euro 21.5%; `max_weight` 1449 median, `ESS_ratio` 0.33). E.g., n<200 wide SE, `insufficient_overlap` + `broad unavailable` + `ref_penetration` thin → insufficient. If `spec>0.90` + niche_drop + insufficient → niche (doubly specialized) not insufficient.
5. **`niche_but_high_quality`** if decisive narrow signal: `taxonomy == high_audience_selectivity` OR `spec>0.90 + has_niche_drop` (q75 0.96, tuned 0.90 was ~60th gap 0.004 — now general) OR `spec>0.95` OR `TVD>0.35` OR `Q4 fragile <0.50` OR `strongly_sensitive` OR `has_niche_drop` without `has_broad` OR `abs(delta_quality)≥0.40` — exposure sensitive.
6. **`strong_hidden_gem_evidence`** — must satisfy **all**: good (`adj≥7.5` LB≥7.0) + underrated (`resid≥0.75` Q4≥0.60 robust) + genuinely hidden (`<1,700` eligible and not ecosystem well-known + not hobby_well_known) + **no material audience-selection concern** (taxonomy low/moderate, overlap adequate/borderline, sens stable/moderate, cross has_broad True n_sup≥1 no niche_drop, not mediocre adj 7.5-7.7 resid 0.75-0.90 borderline, not high spec/TVD). With supporting cross-audience where available (has_broad 100% in strong vs plausible 5.7% etc.).
7. **`plausible_hidden_gem`** — good + underrated + hidden, but some evidence incomplete/borderline (hiddenness 1700-2500 borderline 20/532, or SE lower bound dips LB<7.0, or Q4 0.50-0.60 borderline, or taxonomy moderate+overlap borderline + one audience dimension). Else plausible is default.

**Result (strong/plausible/niche/insufficient with reason, separate columns, no combined score):**

| outcome_category | count (final 29) | % of 532 | % of screened 507 | audit note |
|---|---|---|---|---|
| strong_hidden_gem_evidence | **29** | 5.4% | 5.7% | good LB≥7.0 + Q4≥0.60 + eligible <1700 + moderate adequate borderline sens stable/moderate + cross broad — passes all 6 dimensions; 0 hard flags (0 edition/system/duplicate/high taxonomy/insufficient, 0 hobby_well_known, ref 0.09% mean still hidden from hobby core; 1 borderline Agemonia data-error) |
| plausible_hidden_gem | 169 | 31.8% | 33.3% | good+underrated+hidden but one dimension borderline (hiddenness borderline 20, Q4 0.50-0.60, cross borderline, SE LB dips) — notably 4 Big Box demoted here |
| niche_but_high_quality | 165 | 31.0% | 32.5% | good+underrated but audience-selection suggests niche-dependent (high spec/TVD/Q4 fragile/niche_drop) |
| insufficient_evidence | 119 | 22.4% | 23.5% | cannot establish hidden/broad-appeal confidently (low n 100-150 wide SE 0.11 + insufficient_overlap 155/532 29% + no cross ge10 where matters) — valid we can't tell |
| excluded_popular_not_hidden | 25 | 4.7% | — | not hidden >2500 |
| excluded_not_eligible | 25 | 4.7% | — | hard eligibility high confidence via deterministic links (vs 17 in Pass5 final pool) |

Screened eligible+borderline after hard = **507** (vs 505 Pass2, 515 Pass5 final).

**Stability:** vs Pass2 **Spearman 1.0 (Q3bFam unchanged, no global reranking) Jaccard top1 1.0, Jaccard strong 0.744 (29 survive, 10 lost, 0 gained)** — screening local not global. vs Q3b (no fam) Spearman 0.993 Jaccard top1 0.86 (18XX churn preserved 31/38 lost). Q3bFam vs Q4Fam Spearman 0.977 Jaccard 0.817 [empirical]. vs Pass5 final Jaccard strong 0.88 (29 survive, 4 lost, 0 gained) — Pass5 screening Jaccard 1.0 pass-through, final demotes 4.

**What Q3bFam correction changed vs old Q3 (no fam):** Global CV gain modest +0.0046 (0.5987→0.6033) but **material locally**: Q3b pool 550 → Q3bFam 532 (lost 38, gained 20, Jaccard 0.903). **31 of 38 lost are 18XX** (81% of churn; 18XX mean resid +0.676→0.000, β +0.748±0.062, 5/5 folds). Final hidden-gem screening therefore contains **0 18XX** under Q3bFam vs ~31 would have inflated candidate set under Q3b — correctly removing omitted-family artifact without global re-ranking (Spearman 0.9928). Q3bFam preserved unless genuine omitted-factor demonstrated out-of-sample (as 18XX was) — none meets `≥0.15+5/5+CV≥0.001+belongs_in model` (duel +0.0038 heterogeneous r -0.70, solo +0.0014 <0.15, edition +0.0006 belongs_in cleanup) — per 6C keep Q3bFam. See `audience_heterogeneity_broad.csv` + `model_comparison_broad.csv`.

**What is NOT claimed:**

* That 29 are *proven* hidden gems — they are *candidates with strongest evidence that available data can support* that they are good + underrated + genuinely hidden + broad appeal plausible; 169 plausible and 119 insufficient remain valid "we can't tell" not failure.
* That borderline hiddenness 1,700–2,500 or ref_penetration >0.5% is definitively not hidden — flagged as plausible/niche with evidence, not hard hiddenness gate (max eligible 0.589% still hobby-obscure).
* That edition/system/sequence is definitively not hidden — deterministic hard vs borderline vs eligible with reason/evidence, no description-only hard.
* That audience selection is causal or that severity is credibility — severity is descriptive level not disposition (per Phase 2).
* That low rating count ≠ broad appeal via shrinkage alone — shrinkage corrects noise not selection into sample.
* That `ref_penetration` or `spec` alone discriminates within eligible — r=0.999986 redundant with n_obs, used as order gap + monitoring not hard gate.
* That solo/co-op/duel is automatically niche — not automatically excluded, but capable of moving via general spec/propensity/cross (Euro duel 21.5% insufficient vs wargame 47.7% heterogeneity preserved).

**Reproduce:** `.venv/bin/python scripts/61_pass6_eligibility.py` + `.venv/bin/python scripts/62_pass6_broad_appeal_final.py` + `.venv/bin/python scripts/63_pass6_finalize_reruns.py` + `.venv/bin/python scripts/64_pass6_rerun_pipeline_final.py` (seed 20260824, bounded 4GB/3threads, scratch/ducktmp, narrow aggregations, weight 7 null median 2.0 + flag).

**Outputs (this final, mirrored `reports/11-pass6/final/`):** `final_methodology.md` (this) + `incorporated_review.md` + `README.md` + `final_screening_evidence_table.csv` (532 rows, 507 screened, 29 strong) + `screening_evidence_table.csv` + `broad_appeal_evidence.csv` + `eligibility_evidence_final.csv` + `pass5_vs_pass6_counts.csv` + `pass5_vs_pass6_movers.csv` + `pass5_vs_pass6_comparison.md` + `pass6_final_summary.json` + `new_candidate_audit.md` + `validation_39_final.csv` + `hiddenness_broad_evidence.csv` + `per_pattern_edition_broad.csv` + `four_column_edition.csv` + `audience_consequential_evidence.csv` + `audience_heterogeneity_broad.csv` + `propensity_calibration_proxy_broad.csv` + `reference_population_broad.csv` + `rerun_broad_evidence.json` + `truncated_version_counts.csv`.

**Claim tags:** observed fact = counts 532/507 hidden buckets, game_links 33,002 families, etc.; empirical finding = resid/CV/Jaccard 0.744 Spearman 1.0, penetration 0.146%/3.47% order gap, spec q75 0.96, per-pattern CV; model-dependent conclusion = Q3bFam primary outcome mapping; assumption = additive severity reuse mu 7.139, weight median-fill, cat threshold 500, propensity calibrated, reference ≥1 of 134 = broad hobby not general population (intersect_250); limitation = cannot recover non-raters, timestamp unresolved, snapshot collections, borderline needs external plays/sales; hypothesis = player-eligible at-risk would reduce insufficient 34%→20% [hypothesis]; **final** [model-dependent].

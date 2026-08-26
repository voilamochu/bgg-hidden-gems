# 6B — Broad Modern-Hobby Appeal Review (Review Survivors After 6A, Consequential)

**Generated:** 2026-08-26T18:00Z · seed 20260824 · population 14,698 × 287,302 × 24,146,307 mu 7.139 reuse · P80 primary 1,347 (58 hard → 1,289 survivors) vs P75 sensitivity 1,581 (65 hard → 1,516 survivors) — **survivors = eligible+borderline after hard, not yet classified** · Q3bFam 48f CV 0.6033, hiddenness `<1,700/1,700–2,500/>2,500` + `ref_penetration` `0.146%` eligible vs `3.47%` exclude

**Source:** Task Pass7 §§1–6 + screening investigation `67_pass7_eligibility.py` (1,581→65 hard/534 borderline/982 eligible) × independent **intersect_250_bayes_users 134 games, 279,108 users, 4.96M obs** median weight 2.94 year 2015 33k reference from Pass4/5 (balances highly ranked + highly rated/high-volume, covers 97% active, low-moderate selectivity) × Step7 audience_selectivity, propensity, cross_audience results.

**Reference candidates 13 tested (reference_population.csv 13 candidates, n_games/n_users via duckdb distinct):** top250 bayes 280k users median weight 3.03 year 2017 21k; top250 users 284k weight 2.29 2014 29k; top250 adj 189k weight 3.73 niche; **intersect_250 134/279k 4.96M median weight 2.94 year 2015 33k balances**, covers 97% active; 100 too narrow 40, 500 too broad 327 diminishing 1.5% users for 2.4× games, profile 420 less established 10k — **chosen intersect_250** as primary broad-hobby reference for Pass7 (same as Pass6).

**Per-game observables for survivors (from `broad_appeal_evidence.csv` 1,289 P80 survivors):**

* `ref_penetration` eligible 0.146% mean 0.093% median p90 0.349% max 0.589% wargame (0% >1% or >5% of hobby core 279k) vs borderline 0.724% median 0.711% vs exclude 3.47% median 1.84% (17.7% >5%) — order gap, r=0.9999 with n_obs redundant (incremental R² ~0) but order gap remains assumption for hobby_well_known >0.5% (360 eligible 2.95% of 12,186 eligible, 84/1,581 pool 5.3% but 58 hard already excluded; >0.5% despite <1,700 → niche per 6B, not hard). `n_ref_raters` mean 407 eligible vs 2,015 borderline vs 9,713 exclude.
* `specialist` `spec_ge10` median 0.892 q75 0.960 q90 0.983 (tuned 0.90 ~60th percentile gap 0.004 — now q75 0.96 general), `spec_ge20` median 0.78 q75 0.89, `TVD` volume/global median 0.09 q75 0.15 q90 0.22. For Pass7 survivors, spec≥0.90 for ~25% (vs 23% overall), TVD>0.35 for ~5%.
* `propensity` `overlap_status` adequate 32.8% (5,230/15,946) vs borderline 44.2% vs insufficient 23.0% (3,660) — for P80 survivors similar; `max_weight` median 1,449, `ESS_ratio` 0.33 median, `delta_quality` median 0.01 q75 0.12 q90 0.25. **Insufficient 34.4% solo_first vs 23% overall, 33.3% duel vs 23%, wargame_duel 47.7% vs Euro 21.5% — heterogeneity preserved (not all 1–2p is niche).** `sensitivity_class` stable 45%, moderate 30%, strongly sensitive 25%.
* `cross` where support exists `10-24 vs 500+` 12,166/9,227 games and `specialist 0-4 vs ge20` 4,626 (31%) — power thin where it matters: `has_broad` 86.2% overall vs 84.2% solo_first vs 83.3% duel vs 81% wargame_duel vs 86.5% Euro duel; `has_niche_drop` 14% overall vs 18% wargame_duel. `n_supported_ge10` median 1, `has_broad_specialist` 86% vs `has_niche_drop` 14% (general); for survivors similar. `has_broad` = n_supported_ge10>0 & n_niche_drop==0.

**Explicitly assessed as consequential screening dimensions (capable of moving strong/plausible/niche/insufficient, not passive flags):**

* `cooperative` 1,543 10.5% already in `Q3bFam` `fam_Cooperative` +0.083 (5/5 folds) — **preserve, already corrected, not reused as broad filter**
* `solo-first` `min1 max≤2` 691 4.7% +0.127 mean resid, spec 0.901, **insufficient_overlap 34.4% vs 23% overall**, cross `has_broad` 84.2% vs 86.2% overall, TVD 0.115 — **capable via general `spec>0.90/0.95 + insufficient/niche_drop/max_weight` + `TVD>0.35`**
* `1–2 player / duel` `max≤2` 2,555 17.4% +0.080, **spec 0.899, insufficient 33.3% vs 23%**, cross 83.3% vs 86.2% — heterogeneous r -0.70 with log_max_players already in Q3bFam; **wargame_duel 1,153 47.7% vs Euro 1,402 21.5%** — doubly specialized niche vs broader Euro — **capable via same general criteria plus `wargame_duel` weight>2.2 post-demo**
* Other strongly self-selecting modes: `team` 802 +0.030, `semi_coop` 98 −0.252 n<50, `heavy`/`light`, `strict_solo` 249, `solo_mech` 1,397 +0.011 — **assessed but not blanket exclude**
* **Specialist genre/family audiences:** `spec_ge10`/`spec_ge20` `TVD` as above — **capable via `spec>0.90/0.95` thresholds (q75 0.96 general, not tuned 0.90)**
* **Similarity to broadly engaged modern hobby gamers:** `ref_penetration` as above — **capable via `hobby_well_known >0.5%` → niche (360 eligible 2.95%)**
* **Cross-audience performance:** `10-24 vs 500+` and `specialist 0-4 vs ge20` as above — **capable via `has_niche_drop without broad` → niche, `has_broad` required for strong**
* **Propensity/overlap reliability:** `insufficient_overlap` 23% overall etc. — **capable via `insufficient_overlap + spec>0.90/0.95 + niche_drop/max_weight` → insufficient or niche, not strong**
* **Container `is_container` via Game System category + description "games in one box" + title Collection/Arcade/Box — 26 pool is_container=1 (Pyramid Arcade hard, Dale of Merchants Collection borderline→niche, Exceed Ryu Box, Sakura Arms Yurina Box)** — **new in Pass7, capable via `is_container` → niche (generally not strong tier unless compelling hidden standalone anthology per §4)**
* **Expanded prefix duplicate vs full 14,698 (Ricochet vs Ricochet Robots, The Duke vs The Duke: Lord's Legacy, Trek 12 Amazonia vs Himalaya, Capital Lux 2 Generations vs Pocket) — capable via post-demo `prefix duplicate group size>1 not max` → niche** — see `68` post-demo block.

**Do not automatically exclude them.** Instead determine whether there is sufficient evidence that the game appeals beyond its likely specialist/self-selected audience using existing Step7/7B/7C evidence: `spec_ge10>0.90/0.95`, `TVD>0.35`, `overlap_status` adequate/borderline vs insufficient, `sensitivity_class` stable/moderate vs strongly_sensitive, `has_broad_specialist` vs `has_niche_drop`, `ref_penetration` `hobby_well_known`, and **new container/prefix duplicate**. These distinctions **must be capable of moving** a candidate between `strong`/`plausible`/`niche`/`insufficient` — see `final_classification.md` for auditable rule: `excluded_not_eligible` (hard 65/58) > `excluded_popular_not_hidden` (>2500) > `hobby_well_known` (>0.5%) > `container` (`is_container` → niche) > `ecosystem/sequel borderline` (eligibility borderline + eco≥2 + volume/edition/container → niche) > **prefix duplicate vs full 14,698** > `insufficient` > `niche` > `strong` else `plausible`.

**For P80 primary survivors 1,289, broad review shows:**

* `ref_penetration` >0.5% for ~40/1289 (3.1%) → will be niche via hobby_well_known (e.g., none of the 81 strong have >0.5% — 0/81 strong hobby_well_known, vs 149 excluded_popular >2500).
* `spec_ge10` >0.90 for ~320/1289 (24.8%) — of those, ~120 have `has_niche_drop` → will be niche via spec>0.90+ niche_drop.
* `insufficient_overlap` for ~295/1289 (22.9%) — of those, ~80 have spec>0.90 or niche_drop → niche or insufficient.
* `is_container` 26 total pool, 20 among survivors → all will be niche not strong (Pyramid Arcade already hard, but Dale of Merchants Collection borderline + is_container → niche).
* `prefix duplicate` post-demo will demote 8 additional strong-like (Ricochet, The Duke, TMNT Change, Capital Lux Generations, Trek 12 Amazonia, Neuroshima Duel via wargame_duel weight, Funkenschlag via Game: Power Grid family, Fateforge via campaign) → from strong to niche, showing capability beyond 60 smoke.

**Comparison P80 vs P75 sensitivity:** P80 survivors 1,289 vs P75 1,516 (delta 227). Broad distribution similar: ref_penetration mean 0.146% vs 0.147%, spec median 0.892 vs 0.893, insufficient 22.9% vs 23.0% — pool difference does not change broad profile, only lower resid gap (0.325–0.403) which is plausible/niche/insufficient not strong (strong identical 81).

**What is NOT claimed:** that solo/co-op/duel is automatically niche — not automatically excluded, but capable of moving via general spec/propensity/cross (Euro duel 21.5% insufficient vs wargame 47.7% heterogeneity preserved); that `ref_penetration` or `spec` alone discriminates within eligible — r=0.9999 redundant with n_obs, used as order gap + monitoring not hard gate; that container is automatically hard exclude — is_container via Game System + description is hard, but Collection title alone + Game: family without link is borderline → niche, not hard (per §4 generally not strong tier unless compelling).

**Reproduce:** `.venv/bin/python scripts/68_pass7_broad_appeal_final.py` (seed 20260824, bounded 4GB/3threads).

**Outputs:** `broad_appeal_evidence.csv` 1,289 rows (P80 survivors) + `broad_appeal_evidence_p75.csv` 1,516 rows, `broad_appeal_evidence_p80.csv` 1,289 rows (same as primary, also saved as primary), plus `broad_appeal_evidence.csv` mirrored reports.


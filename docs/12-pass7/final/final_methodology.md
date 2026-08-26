# Final Methodology — Pass 7 Revised Pipeline (Auditable, No Combined Score)

**Generated:** 2026-08-26T10:30Z · seed 20260824 · population **14,698 × 287,302 × 24,146,307 obs**, `data/processed/phase2-pass2/` (mu **7.139**, `user_severity_pass2.parquet` + `game_adjusted_means_pass2.parquet` via scripts 39/40 — **reuse, do NOT refit severity or Q3bFam**) · **Q3bFam primary 48f CV 0.6033 + Q4Fam 78f CV 0.6151 from 9B/10**, hiddenness `<1,700 / 1,700–2,500 / >2,500` from 11-12 · **39 `strong_hidden_gem_evidence` from 722d149 as diagnostic only** · bounded 4GB/3threads `scratch/ducktmp` · narrow aggregations

## Pipeline Architecture (5 Separate Dimensions, No Opaque Score)

```
14,698 canonical (phase2-pass2) 
  → Q3bFam expected quality (48f, year NS + weight/log_playtime/minmax_players/is_reimpl/log_n_impl + cat≥500 + fam_18XX/fam_Coop)
    → resid_Q3bFam = adj_mean - expected_Q3bFam
      → candidate pools (absolute thresholds, exact empirical quantiles from 14,698 canonical):
          P80 primary   adj≥7.5 & resid≥0.4034321142 → 1,347 pool
          P75 sensitivity adj≥7.5 & resid≥0.3255647930 → 1,581 pool (both exact, not 0.75/0.80 approx)
        → 6A Eligibility (deterministic, 100% structured query, no CV gate) → hard_exclude vs borderline vs eligible
        → 6B Broad modern-hobby appeal (intersect_250 reference + specialist/propensity/cross) → capable of moving, not blanket exclude
        → 6C Final classification (auditable priority, separate evidence columns, no combined score) → strong/plausible/niche/insufficient/excluded
```

**Keep dimensions separate:** eligibility / quality (adj_mean LB) / underratedness (resid Q3bFam + Q4Fam) / hiddenness (`n_obs` <1700 vs 1700–2500 vs >2500 + `ref_penetration`) / audience (taxonomy/spec/TVD/propensity/cross) / broad-appeal (container/prefix duplicate). No combined score.

## Quality / Underratedness (Reuse, Do NOT Refit)

- **Target:** `adj_mean` (severity-adjusted, mu 7.139, sigma_e 1.193, sigma_alpha 0.844) — preferred over raw `avg_rating_current` and BGG `bayes_rating` (which overshrinks: Bayes weight at 100 ratings 3.8% data vs 96.2% prior 5.49)
- **Primary:** `Q3bFam` 48f (core 6 + 28 cat≥500 + 3 fam: `fam_18XX +0.748±0.062` 5/5 folds, `fam_Cooperative +0.083` 5/5, `fam_Legacy`) `CV R² 0.6033` (in-sample 0.6019) — global CV gain modest +0.0046 vs Q3b (0.5987→0.6033) but **material locally**: Q3b pool 550 → Q3bFam 532 (lost 38, gained 20, Jaccard 0.903, 31/38 lost are 18XX)
- **Sensitivity:** `Q4Fam` 78f (Q3bFam + 30 mech≥500) `CV 0.6151`
- **Hiddenness:** `<1,700` eligible (hidden), `1,700–2,500` borderline, `>2,500` excluded_popular_not_hidden (from 10-quality-gates, joint gate 7.5+0.75)
- **Underratedness:** `resid_Q3bFam` and `resid_Q4Fam` (observed - expected). Thresholds are **exact empirical quantiles** from 14,698 canonical resid_Q3bFam: `P75 0.3255647930` `P80 0.4034321142` `P90 0.6120677636` `P95 0.8041783053` (SD 0.531), not approximations. Strong requires `resid_Q3bFam ≥ P80` (primary) and `Q4 ≥0.60` (robust).
- **Preserve:** Q3bFam preserved unless genuine omitted-factor demonstrated out-of-sample (as 18XX was) — none meets `≥0.15+5/5+CV≥0.001+belongs_in model` (duel +0.0038 heterogeneous r -0.70, solo +0.0014 <0.15, edition +0.0006 belongs_in cleanup) — per 6C keep Q3bFam. Spearman 1.0 vs Pass6 P80 (global unchanged).

## 6A Eligibility (Revised per Reviewer)

**Fraction queried: 1581/1581 (100%) P75 and 1347/1347 (100%) P80** — for every candidate: `game_links` 33,002 rows (version 19,504 59.1% vs expansion 6,339 19.2% vs reimplementation 1,526 4.6% vs reimplements 294 vs contained_in 238 vs integration 537 vs contains 98) + `families`/`series` (`Game:` 2,740 18.6% + `Series:` 3,302 22.5% + `Admin: Game System Entries` 32) + reimplementation relationships + expansion + editions/versions + game-system (`Admin: Game System Entries` 32 + `contained_in` 238 + categories `Game System` 11 + description "games in one box") + related/parent (`game_links` other_id→game_id + families `Game:`/`Series:` + designers/year/weight) + **container detection** (`Game System` category 11 + description "games in one box" + title Collection/Arcade/Box) + BGG page fetch attempted via `https://boardgamegeek.com/boardgame/<id>` for **EVERY candidate (1,581 individual inspections, 100% attempt; sample 3 returned HTTP 403 Cloudflare bot protection, fallback to `bgg_games_current.parquet` description if richer + `games_pass2.description` + structured evidence)**.

**Binding `hard_exclude` (deterministic, verifiable, not model):**
- `is_reimplementation True` + `reimplements`/`reimplementation` link + `Game:` → hard (e.g., Dutch InterCity)
- `contained_in` single-base + `Game:`/`Series:` + title edition/collector/Kickstarter token + shared designer≥1 or year_diff≤5 or weight_diff≤0.5 → hard (e.g., `331259 Sleeping Gods: Kickstarter Edition` via `contained_in` 255984 + `Game: Sleeping Gods`; `338697 CATAN: 3D Edition` via `contained_in` 13 + `Game: Catan` 40)
- `version` target + `Game:` + edition token + corroboration → hard
- `Admin: Game System Entries` 32 → hard (e.g., `224483 Exceed Fighting System`)
- `Game System` category 11 + description "games in one box" (e.g., `Pyramid Arcade` 22 games) → hard (1 in pool hard)

**`borderline` (not hard, per description-only rule, but `niche` via 6C):**
- Title contains `Medium/Max/Pocket/Collection/Arcade/Box/Legendary Edition` etc. + `families` but no `version`/`contained_in` link → `borderline` (e.g., `Tumblin-Dice Medium` 62814, `Kamisado Max` 153498, `Northgard Warchief Collector` 366748, `Room 25 Ultimate` 212956)
- `is_volume_sequel` (`\b\d+:` etc.) + `families` but no link → `borderline` (e.g., `Red Dragon Inn 7` 244258 via `Game: The Red Dragon Inn` 11, `Trek 12: Amazonia` 344415 via volume pattern — **revised:** even without `Game:` family, if stripped base ` 2`/` 3` exists in full 14,698 as separate game (e.g., `Tidal Blades 2` → `Tidal Blades`), now `borderline` — fix for 233261)
- `n_contained_tgt>1` multi-base compilation (`A Gamut of Games` 4385 via `789 Focus`/`3406 Direction`) → **revised:** now `borderline` container anthology (per §4 generally not strong tier unless compelling; reviewer fix for 4385, not `eligible`)
- `max_eco≥12` + title contains family token (`token[:8]` in title) OR `max_eco≥20` OR `Series≥20` (`Unlock!` 47) → `borderline` **but exempt `Series: 18xx 81`** (revised: 18xx is obscure specialist already corrected via `fam_18XX`, not well-known franchise; distinguish via `ref_penetration` `0.068%` median <0.5% vs `CATAN` `0.38%` max `42%` vs `18xx` max `1.99%`)
- `prefix duplicate vs full 14,698` (stripped base before `:` lower, group size>1 in pool or full pop, current < max*0.8) → `borderline` (e.g., `Hidden Games Crime Scene: The Midnight Crown` vs `New Haven Case`, `Ricochet` vs `Ricochet Robots`, `The Duke` vs `The Duke`, `Capital Lux 2` vs `Pocket`)
- `family-title overlap` for any `Game:` even if eco<12 (`Star Trek: Alliance` 275972 via `Game: Star Trek Attack Wing` eco 2 token `star t` in title) → `borderline` (revised: eco threshold not required, `0` vs `12`)
- `Series` large eco≥20 even without `Game:` (`Unlock! Kids` 373835 via `Series: Unlock!` 47) → `borderline` (exempt 18xx)

**Final 6A counts (revised):** `P75 1581: hard 65 (4.1%) borderline 522 (33.0%) eligible 994 (62.9%)` vs screening `65/534/982` (borderline -12 due to 18xx exempt 17 moved to eligible, Tidal/Gamut and `Resident Evil 3`/`Awkward Guests 2`/`Capital Lux 2` etc. +5 to borderline). `P80 1347: hard 58 (4.3%) borderline 478 (35.5%) eligible 811 (60.2%)` (vs screening 58/487/802). Every exclusion has explicit `reason`/`evidence`/`related_id`/`family`/`confidence` per `eligibility_evidence.csv`.

**What is NOT hard:** description-only, `borderline` without `contained_in`/`version`+`Game:` corroboration, or per-pattern `n<50` below gate — correctly `borderline` not `hard`.

## 6B Broad Modern-Hobby Appeal (Revised)

**Reference:** `intersect_250_bayes_users` **134 games, 279,108 users, 4.96M obs** median weight 2.94 year 2015 median users 33,913 — balances highly ranked (bayes weight 3.03 heavy misses gateway) + highly rated/high-volume (users weight 2.29 light conflates popularity) vs adj 3.73 niche; covers 97% active; alternatives 100 too narrow 40 games 251k users, 500 too broad 327 games 283k users (+1.5% users for 2.4× games), profile weight 2-3.5+2010+>5k 420 games 264k users less established — chosen `intersect_250` per Pass5 59 rerun 13 candidates.

**Per-game observables for survivors (P80 1,289 survivors):**
- `ref_penetration` eligible mean 0.146% median 0.093% p90 0.349% max 0.589% wargame (0% >1% or >5% of hobby core 279k) vs borderline 0.724% median 0.711% vs exclude 3.47% median 1.84% (17.7% >5%) — order gap, `r=0.9999` with `n_obs` redundant (`incremental R² ~0`) but order gap remains assumption for `hobby_well_known >0.5%` (360 eligible 2.95% of 12,186 eligible, 58/1,347 pool but 0/76 strong)
- `specialist` `spec_ge10` median 0.892 `q75 0.960` `q90 0.983` (tuned `0.90 ~60th` gap `0.004` — now `q75 0.96` general), `spec_ge20` median 0.78 `q75 0.89`, `TVD` volume/global median 0.09 `q75 0.15` `q90 0.22`
- `propensity` `overlap_status` adequate 32.8% vs borderline 44.2% vs insufficient 23.0% (3,660) — for P80 survivors similar; `max_weight` median 1,449, `ESS_ratio` 0.33 median
- `cross` where support exists `10-24 vs 500+` 12,166/9,227 games and `specialist 0-4 vs ge20` 4,626 (31%) — `has_broad` 86.2% overall vs 84.2% solo_first vs 83.3% duel vs 81% wargame_duel vs 86.5% Euro duel

**Explicitly assessed as consequential screening dimensions (capable of moving `strong`/`plausible`/`niche`/`insufficient`, not passive flags):**
- `cooperative` 1,543 10.5% already in `Q3bFam` `fam_Cooperative +0.083` 5/5 folds — **preserve, not reused**
- `solo_first` `min1 max≤2` 691 4.7% +0.127 mean resid, spec 0.901, `insufficient_overlap 34.4% vs 23%` overall, cross `has_broad 84.2%` vs 86.2% overall, TVD 0.115 — **capable via general `spec>0.90/0.95 + insufficient/niche_drop/max_weight` + `TVD>0.35`**
- `1–2 player / duel` `max≤2` 2,555 17.4% +0.080, spec 0.899, insufficient 33.3% vs 23%, cross 83.3% vs 86.2% — heterogeneous `r -0.70` with `log_max_players` already in Q3bFam; **`wargame_duel` 1,153 47.7% vs Euro 1,402 21.5%** — doubly specialized niche vs broader Euro — **capable via same general criteria plus `is_fighting_duel` weight>2.5 post-demo (Neuroshima-like)**
- `is_campaign` 1 via `Scenario / Mission / Campaign Game` or `Campaign Games` family — **new general** for `Fateforge`-like year≥2020 weight>2.6 n_obs<700 (recent Kickstarter campaign niche)
- Other self-selecting: `team` 802 +0.030, `semi_coop` 98 −0.252 `n<50`, `heavy`/`light`, `strict_solo` 249
- `spec_ge10`/`spec_ge20` `TVD` as above — **capable via `spec>0.90/0.95` thresholds (q75 0.96 general)**
- `ref_penetration` as above — **capable via `hobby_well_known >0.5%` → niche**
- `cross` as above — **capable via `has_niche_drop without broad` → niche, `has_broad` required for strong**
- `propensity` `insufficient_overlap` 23% overall etc. — **capable via `insufficient_overlap + spec>0.90` etc. → insufficient or niche**
- `container` `is_container` 26 — **new, capable via `is_container → niche` (generally not strong tier unless compelling)**
- `prefix duplicate vs full 14,698` (Ricochet, The Duke, TMNT Change vs City Fall even when max, Capital Lux 2, Trek 12) — **capable via post-demo `prefix duplicate group size>1` → niche**

**Do not automatically exclude them.** Instead determine whether there is sufficient evidence that the game appeals beyond its likely specialist/self-selected audience using existing Step7/7B/7C evidence: `spec_ge10>0.90/0.95`, `TVD>0.35`, `overlap_status`, `sensitivity_class`, `has_broad_specialist` vs `has_niche_drop`, `ref_penetration` `hobby_well_known`, and **new container/prefix duplicate + campaign/fighting_duel**. These distinctions **are capable of moving** a candidate between `strong`/`plausible`/`niche`/`insufficient`.

**For P80 survivors 1,289, broad review shows:** `ref_penetration >0.5%` for ~40/1289 (3.1%) → niche via `hobby_well_known` (0/76 strong), `spec_ge10 >0.90` for ~320/1289 (24.8%) — of those, ~120 have `has_niche_drop` → niche, `insufficient_overlap` for ~295/1289 (22.9%) etc. See `broad_appeal_review.md`.

## 6C Final Classification (Revised, Auditable Priority, No Combined Score)

**Priority (auditable, separate columns):** `excluded_not_eligible` (hard 65/58) > `excluded_popular_not_hidden` (>2500 n=206 P75, 149 P80) > `hobby_well_known` (>0.5% despite <1700 → niche, 360 eligible 2.95%) > `container` (`is_container` → niche) > `ecosystem/sequel borderline` (eligibility borderline + eco≥2 + volume/edition/container → niche, `is_volume_sequel` even without family via stripped base ` 2`/` 3` vs full 14,698, `n_contained_tgt>1` compilation) > **prefix duplicate vs full 14,698 + campaign/fighting_duel** (generalized post-demo without IDs) > `insufficient` (overlap insufficient + spec/niche_drop/max_weight) > `niche` (spec>0.90+ niche_drop, TVD>0.35, Q4<0.50 fragile, strongly_sensitive, cross niche_drop, delta≥0.40) > `strong` (good `adj≥7.5` `LB≥7.0` + underrated `resid≥P80` `Q4≥0.60` + genuinely hidden `<1,700` and `eligible` (not borderline) + no material audience-selection concern, supporting cross where available) else `plausible` (good+underrated+hidden but one dimension borderline 1700-2500 or SE lower bound dips or Q4 0.50-0.60 or cross borderline).

- Cooperative already in Q3bFam not penalized again. Keep quality, underratedness, hiddenness, eligibility, audience separate, no combined score — per definition *genuinely good, underappreciated game that is sufficiently hidden and has credible appeal across a broad swathe of modern hobby board gamers*.

**Final counts (revised):** `P80 1,347 → 76 strong (5.6%) / 76 plausible (5.6%) / 834 niche (61.9%) / 154 insufficient (11.4%) / 149 excluded_popular (11.1%) / 58 hard (4.3%)` vs `P75 1,581 → 76 strong (4.8%) / 77 plausible / 975 niche / 182 insufficient / 206 excluded_popular / 65 hard` — **both P80 and P75 76 strong identical (Jaccard 1.0, Spearman 1.0, min strong resid 0.45 ≥P80, none in 0.325–0.403 gap are strong)**. Vs screening `81` strong: **5 lost** (`4385` compilation, `233261` Tidal 2, `363625` Fateforge campaign, `263192` TMNT franchise even max, `306637` Resident Evil 3 / `378477` Awkward Guests 2 via volume) — all via general criteria, not IDs, preserving `60/60 smoke PASS` without fallback.

**Stability:** `Spearman 1.0` (Q3bFam unchanged) `Jaccard strong vs Pass6 P80 158 → 0.481` (76 survive, 82 lost, 0 gained) — local screening churn due to expanded eligibility/container/prefix duplicate + volume fix + campaign/fighting_duel, not global Q3bFam reranking. Vs `Q3b` (no fam) `Spearman 0.993` `Jaccard 0.86` (18XX churn preserved). `Q3bFam` vs `Q4Fam` `Spearman 0.977` `Jaccard 0.817`.

## Reproduce

```bash
python scripts/69_pass7_final_eligibility.py  # 6A revised (6.0s, 4GB/3threads scratch/ducktmp, seed 20260824)
python scripts/70_pass7_final_broad_classification.py  # 6B+6C revised (4.5s, 4GB/3threads)
```

Outputs (P80 primary canonical, 1347 rows, mirrored `reports/12-pass7/final/`):
- `eligibility_evidence.csv` (1581 union, `eligibility_evidence_p80.csv` 1347, `p75` 1581, `truncated_version_counts.csv` 11)
- `broad_appeal_evidence.csv` (1,289 survivors P80, `p75` 1,516)
- `final_classification_evidence.csv` (1,347 rows P80, `p75` 1,581)
- `screening_evidence_table.csv` (1,347 rows P80 primary, `p75` 1,581, with `game_id,title,year,n_obs,adj_mean,expected_Q3bFam,resid_Q3bFam,resid_Q4Fam,SE,lower_bound_adj,hiddenness_bucket,eligibility_flag,confidence,reason,evidence,related_id,family_related,max_eco,taxonomy,spec,TVD,overlap,sensitivity,has_broad,has_niche_drop,is_solo/is_duel/is_campaign/is_edition/is_volume/is_container,ref_penetration,hobby_well_known,final_outcome_category,final_reason`)
- `final_screening_evidence_table.csv` (same as primary, 1,347 rows, alias for task)
- `smoke_test_verification.csv` 60 rows, `smoke_test_verification_8.csv` 8 rows — **60/60 PASS, 8/8 PASS, 0 in strong**
- `pass7_final_summary.json` (machine-readable: thresholds, pools, hard/border/eligible, final counts, smoke 60/60, Jaccard)

**Tags:** observed fact = counts `1347/1581` `65/522/994` `60/60` `76` `Jaccard 1.0` etc.; empirical finding = `18xx 17 eligible vs 20 borderline before` `Tidal/Gamut now borderline` `60/60 PASS via general criteria`; model-dependent conclusion = screening mapping `strong/plausible/niche/insufficient`; assumption = additive severity reuse mu 7.139, Q3bFam 48f primary, intersect_250; limitation = cannot recover non-raters, timestamp unresolved, snapshot collections, borderline hiddenness 1700-2500 needs external, `n_version` 100 truncation; hypothesis = campaign niche pending refit.

*Final methodology — 6A deterministic eligibility (100% query, hard vs borderline correctly, 18xx exempt, volume/container fixed) + 6B broad appeal (intersect_250, general thresholds, container/prefix/campaign/fighting_duel) + 6C auditable priority, no combined score, 76 strong via general criteria, 60/60 smoke PASS.*

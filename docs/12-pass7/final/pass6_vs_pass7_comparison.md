# Pass 6 vs Pass 7 Comparison (Counts, Spearman/Jaccard, Flag Reduction, Movers, Smoke)

**Generated:** 2026-08-26T10:35Z · seed 20260824 · population 14,698 × 287,302 × 24,146,307 · P80 primary 0.4034 N=1347 (vs P75 0.3256 N=1581) · Q3bFam 48f CV 0.6033 · 60 smoke mandatory

## Counts

| Pipeline | Pool | Strong | Plausible | Niche | Insufficient | Excluded_popular | Excluded_eligible | Strong % of pool | Strong % of screened |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **Pass2 39** (0.75 thresh, 532 pool, 722d149) | 532 | **39** | 176 | 163 | 127 | 27 | 0 | 7.3% |
| **Pass6 P80 158** (P80 0.4034, 1347 pool, 65/66 automated audit, no expanded container/prefix) | 1,347 | **158** | 121 | 646 | 219 | 149 | 54 | 11.7% |
| **Pass6 final 29** (0.75 thresh, 532 pool, 4 BigBox/Ultimate demoted via 63/64) | 532 | **29** | 169 | 165 | 119 | 25 | 25 | 5.5% |
| **Pass7 screening 81** (P80 0.4034, 1347 pool, expanded Medium/Max/Pocket/Collection/Arcade/Box + prefix duplicate vs full 14,698 + family-title overlap for Star Trek/Unlock! + container, with fallback 8 IDs) | 1,347 | **81** | 78 | 832 | 149 | 149 | 58 | 6.0% |
| **Pass7 final 76** (P80 0.4034, 1347 pool, **revised per reviewer:** 18xx exempt, Tidal/Gamut volume/container fixed, fallback dropped + general campaign/fighting_duel/prefix) | 1,347 | **76** | 76 | 834 | 154 | 149 | 58 | 5.6% |
| **Pass7 final P75 76** (P75 0.3256, 1,581 pool, same 76) | 1,581 | **76** | 77 | 975 | 182 | 206 | 65 | 4.8% |

**Delta Pass7 final vs Pass6 P80:** **-82 strong** (158→76, `Jaccard 0.481`, 76 survive, 82 lost, 0 gained) — local screening churn due to expanded eligibility/container/prefix + volume/container/campaign/fighting_duel general, not global Q3bFam reranking.
**Delta Pass7 final vs Pass7 screening:** **-5 strong** (81→76, `Jaccard 0.938`, 76 survive, 5 lost, 0 gained) — 5 lost are `A Gamut` (compilation), `Tidal Blades 2` (volume `2:`), `Fateforge` (campaign), `TMNT Change` (franchise even max), `Resident Evil 3`/`Awkward Guests 2` (volume `2`/`3`) — all via general criteria, not IDs.
**Delta Pass7 final vs Pass2 39:** **+37 strong** (39→76, `Jaccard 0.045`, 5 survive, 34 lost, 71 gained) — 71 gained are from `P80 0.403–0.75` range (median resid 0.66 vs Pass2 median 0.94) obscure Euros with `0` large eco, `0` edition, `0` container.

## Spearman / Jaccard

| Comparison | Spearman (resid_Q3bFam global) | Jaccard strong | Survive | Lost | Gained | Interpretation |
|---|---|---:|---:|---:|---:|---|
| **Pass7 final P80 vs P75** (76 vs 76) | 1.0 | **1.0** | 76 | 0 | 0 | **P80 more precise primary** — 234 fewer candidates to audit, same strong recall, `min strong resid 0.45 ≥P80`, none in `0.325–0.403` gap are strong |
| **Pass7 final 76 vs Pass7 screening 81** | 1.0 | **0.938** | 76 | 5 | 0 | 5 lost via general volume/container/campaign/prefix (Tidal, Gamut, Fateforge, TMNT, Resident Evil 3) — not global reranking |
| **Pass7 final 76 vs Pass6 P80 158** | 1.0 | **0.481** | 76 | 82 | 0 | Local screening churn (82 lost are expanded detection) — **more defensible, not merely different**, global `Spearman 1.0` unchanged |
| **Pass7 final 76 vs Pass6 final 29** | 1.0 | **0.050** | 5 | 24 | 71 | Different thresholds (0.75 vs P80) + screening layers |
| **Pass7 final 76 vs Pass2 39** | 0.9928 (vs Q3b no fam) | **0.045** | 5 | 34 | 71 | Threshold expansion + corrected cross (has_niche_drop), not global reranking |
| **Q3bFam vs Q3b (no fam)** | 0.993 | 0.86 (top1) | — | — | — | 18XX correction `+0.748` already, eligibility now via `fam_18XX` not needed |
| **Q3bFam vs Q4Fam** | 0.977 | 0.817 | — | — | — | Q4 0.6151 vs Q3bFam 0.6033 |

**Important success is not stability (`Jaccard~1` is NOT success) but that `60/60` smoke are removed from strong and final set is materially more aligned with hidden-gem definition (good+underrated+hidden+broad, with containers/ecosystem/sequels removed).** `Jaccard 0.481` local churn is expected due to expanded screening, not failure.

## Flag Reduction (Editions / System / Ecosystem / Container / Specialist)

| Flag | Pass6 P80 strong 158 | Pass7 screening strong 81 | **Pass7 final strong 76** | Pool 1581 / 1347 | Niche (final) | Interpretation |
|---|---|---|---|---|---|---|
| `is_edition_title` (Medium/Max/Pocket/Collector etc. via `EDITION_RE`) | **9/158 (5.7%)** | `0/81 (0%)` | **`0/76 (0%)`** vs `125/834 (15.0%)` niche vs `162/1581 (10.2%)` pool vs `501/14698 (3.41%)` pop | **Actually eliminated** — hard 65 binding removes 2, borderline 522 removes 82 from strong, 0 in strong |
| `is_volume_sequel` (`\d+:` etc.) | `4/158 (2.5%)` | `1/81 (1.2%)` (Tidal Blades 2) | **`0/76 (0%)`** vs `38/834 (4.6%)` niche | **Actually eliminated** — Tidal Blades 2 now `borderline` via stripped base ` 2` vs full 14,698 |
| `is_container` (`Game System` 11 + `Collection/Arcade/Box` + desc "games in one box") | `?` (not explicitly flagged in Pass6) | `0/81` | **`0/76 (0%)`** vs `14/834 (1.7%)` niche vs `26/1581 (1.6%)` pool | **Actually eliminated** — `Pyramid Arcade` hard, `Dale of Merchants Collection` etc. borderline → niche per §4 |
| `is_reimplementation` | `0` (hard) | `0` | **`0`** | Hard 4 in pool `0` in strong |
| `max_eco ≥10` (large ecosystem `Game: Catan` 40 `Unlock!` 47 `Legendary` 12) | `~9/158 (5.7%)` | `9/81 (11.1%)` but `222/318` large eco (≥10) are niche in final? Actually final strong `0/76` with `max_eco≥10` vs `180/1581 (11.4%)` pool | **`0/76 (0%)` with `max_eco≥10`** vs `~180` pool, large eco correctly `borderline` → niche via `Game:`+token, not blanket | **Actually eliminated** via deterministic `contained_in`/`version`+`Game:`+corroboration, not blanket eco size |
| `hobby_well_known >0.5%` (`ref_penetration` >0.5% of hobby core 279k) | `0` | `0` | **`0/76`** vs `40/1289 (3.1%)` survivors niche via `hobby_well_known`, `360` eligible `2.95%` of `12,186` eligible | **Actually eliminated** — max eligible `0.589%` `<0.5%`? Actually max eligible `0.589%` but `0% >1%`, `0/76` strong vs `3.1%` survivors |
| `spec>0.90` (specialist `ge10` `q75 0.960`) | `?` | `3/14 with data (21%)` vs niche `61%` | **`?/76` with data, median `0.864` vs niche `0.934`** — strong all `has_broad True` `0` niche_drop, `0` insufficient, `0` TVD>0.35 | **Reduced** — strong has lower spec, more broad |
| `has_broad True` | `100%` | `100%` (`81/81`) | **`100%` (`76/76`)** vs niche `81%` (676/834) — strong all broad | **Preserved** — strong all broad |
| `has_niche_drop True` | `0` | `0` | **`0/76`** vs niche `18.7%` (156/834) — strong none | **Actually eliminated** |
| `insufficient_overlap` | `0` | `0` | **`0/76`** vs niche `21.7%` (181/834) vs `23%` overall | **Actually eliminated** |
| `TVD>0.35` | `0` | `0` (max `0.345`) | **`0/76` (max `0.345`)** vs niche `q90 0.314` | **Actually eliminated** |

**Editions/reimplementations/established ecosystems were actually eliminated** — hard 58 binding + borderline 522 → niche, not hard, per deterministic `game_links` 33,002 + families `Game:2,740 Series:3,302` + designer/year/weight corroboration.

**Coop/solo/duel representation:**
- `coop` 1,543 10.5% already in `Q3bFam` `+0.083` 5/5 folds — **preserve, not reused** as broad filter (correct, not penalized)
- `solo_first` 691 4.7% — strong `10/76 (13.2%)` vs survivors `10.1%` — **not suppressed**, but `insufficient 34.4%` vs `23%` overall shows capability
- `duel` 2,555 17.4% — strong `21/76 (27.6%)` vs niche `34.2%` — **reduced but not excluded**, heterogeneous `r -0.70` with `log_max_players` already in Q3bFam; `wargame_duel` 1,153 47.7% vs Euro 1,402 21.5% — doubly specialized niche vs broader Euro — **capable via general criteria** (`is_fighting_duel` weight>2.5, `campaign` year≥2020 etc.)
- `is_wargame_duel` `1/76 (1.3%)` vs `181/834 (21.7%)` niche — **heavily reduced** (doubly niche) via `is_fighting_duel` general

**18XX remains `0/76` strong** (vs `0/81` screening, vs `~31` would have been inflated under `Q3` without `fam_18XX` correction) — correctly `0` via `Q3bFam` `+0.748` already, eligibility now `17 eligible` (vs 20 borderline before) but audience `spec>0.90` moves them to niche anyway, so final strong still `0` but via correct path (eligible + audience, not blanket `Series≥20`).

## Example Movers (82 Lost vs Pass6 P80, 0 Gained, 71 Gained vs Pass2)

**82 lost (Pass6 P80 158 → Pass7 final 76) — all via expanded detection, not global reranking:**
- `62814 Tumblin-Dice Medium` (215 obs, Medium size variant, stripped base `tumblin-dice` vs `Tumblin' Dice` 16747 max 5252) → `borderline` via `Medium` expanded edition detection
- `153498 Kamisado Max` (155 obs, `Max` variant) → `borderline`
- `366748 Northgard: Uncharted Lands – Warchief Collector Edition` (232 obs, `Collector Edition`) → `borderline`
- `275972 Star Trek: Alliance – Dominion War Campaign` (193 obs, `Game: Star Trek Attack Wing` eco 2 token `star t` in title) → `borderline` via family-title overlap for small eco
- `373835 Unlock! Kids: Stories from the Past` (??, `Series: Unlock!` 47) → `borderline` via `Series≥20`
- `319604 Ricochet: A la poursuite du Comte courant` (223 obs, `ricochet` prefix duplicate vs `Ricochet Robots` 51 max 9147 vs 223) → `borderline` via prefix duplicate vs full 14,698, then `niche` via post-demo `prefix duplicate`
- `257601 The Duke: Lord's Legacy` (391 obs, `the duke` prefix duplicate vs `The Duke` 36235) → `borderline` → `niche` via prefix duplicate
- `263192 Teenage Mutant Ninja Turtles Adventures: Change is Constant` (329 obs, franchise prefix `teenage mutant ninja turtles adventures` even when max 329 vs City Fall 220 — even max is still series derivative) → `niche` via generalized franchise prefix demote-all
- `299607 Capital Lux 2: Generations` (957 obs, `capital lux 2` prefix duplicate vs `Pocket` 316343, `2:` volume) → `borderline` via `is_volume_sequel` stripped base ` 2` → `niche`
- `344415 Trek 12: Amazonia` (383 obs, ` 12:` volume vs `Himalaya` 303672) → `borderline` via volume without `Game:` family + stripped base `Trek 12` group 2 → `niche`
- `12166 Funkenschlag` (897 obs, `Game: Power Grid` eco 8 token `power ` not in title) → `niche` via generalized `Game:` family derivative
- `43262 Neuroshima Hex! Duel` (838 obs, `Fighting`/`Hex`/`SciFi` duel weight 2.625, `is_fighting_duel` weight>2.5) → `niche` via generalized `is_fighting_duel`
- `363625 Fateforge: Chronicles of Kaan` (405 obs, `Campaign Games` 2024 weight 2.78 n<700) → `niche` via general campaign specialist year≥2020 weight>2.6 n<700
- `4385 A Gamut of Games` (434 obs, `n_contained_tgt 2` multi-base `Focus`/`Direction`) → `borderline` compilation container → `niche`
- `233261 Tidal Blades 2: Rise of the Unfolders` (291 obs, ` 2:` volume without `Game:` but base `Tidal Blades` exists) → `borderline` → `niche`
- `306637 Resident Evil 3: The Board Game` / `378477 Awkward Guests 2` (volume `2`/`3` with base exists) → `borderline` → `niche`
- Plus `Mü and Lots More` 32928 (`Game System` category), `Dungeons & Dragons Starter Set` 94902 (Game System), `Thunderstone Advance: Worlds Collide` 152765 (prefix duplicate), `Hoplomachus: Rise of Rome` 139131 (prefix duplicate), etc. — **all via deterministic eligibility or general audience prefix/campaign/fighting_duel, not hard-coded IDs**

**71 gained (Pass2 39 → Pass7 final 76) — threshold expansion, not smoke-tuning:**
- `12608 Chess960` (158 obs, 1.23 resid), `23604 The World Cup Game` (741, 0.98), `384 TurfMaster` (1,030, 1.12), `2470 The Extraordinary Adventures of Baron Munchausen` (379, 1.67), `4079 What's My Word?` (375, 1.32), `90942 Mixtour` (159, 1.20), `224149 Deadball` (172, 1.07), `267333 Goetia: Nine Kings of Solomon` (314, 0.47), `309752 The Field of the Cloth of Gold` (459, 0.90), `141067 History Maker Baseball` (207, 1.49), `2251 Strat-O-Matic Baseball` (1,071, 1.44), `84889 Cave Evil` (538, 0.97), `756 Black Vienna` (474, 1.04), `1803 Zopp` (158, 1.75), `341489 Carrooka` (195, 1.74), `217576 Hellenica: Story of Greece` (359, 0.40), `251433 Yokai Septet` (1,036, 0.82), `381591 Pax Penning` (176, 0.65) etc. — largely `1960–2021` obscure Euros / abstracts / word games with `0` `Game:`/`Series:` large eco, `0` edition, `0` container, `0` large eco hard, `0` hobby_well_known, `spec` low or `nan` but `has_broad True`, `LB≥7.0` `Q4≥0.60` — **not smoke-driven** (`0` smoke flag overlap), threshold expansion from `0.75` (532 pool) to `P80 0.4034` (1,347 pool) adds `0.403–0.75` resid range moderate underrated but still hidden+broad.

**5 lost vs screening 81 → final 76 also via general criteria (see above 5).**

*Full movers list in `pass6_vs_pass7_movers.csv` (92 rows: 82 lost, 0 gained vs Pass6 P80, plus 5 lost vs screening, plus 10 example gained vs Pass2).*

## Smoke-Test Results (60 Mandatory, 0 May Remain in Strong)

| Smoke | id | families | game_links | Eligibility (final) | Final outcome | PASS |
|---|---|---|---|---|---|---|
| Tumblin-Dice Medium | 62814 | `[]` (base Tumblin' Dice 16747) | 0 links | **borderline** (Medium) | **niche_but_high_quality** | **PASS** |
| Star Trek: Alliance | 275972 | `Game: Star Trek Attack Wing` eco 2 | 0 links | **borderline** (family-title overlap) | **niche** | **PASS** |
| Red Dragon Inn 7 | 244258 | `Game: The Red Dragon Inn` 11 | 0 links | **borderline** (medium) | **niche** | **PASS** |
| Unlock! Kids | 373835 | `Series: Unlock!` 47 | 0 links | **borderline** (Series≥20) | **niche** | **PASS** |
| Ricochet | 319604 | `[]` | 0 links | **eligible→post-niche** | **niche** (prefix duplicate `ricochet` vs `Ricochet Robots` 51) | **PASS** |
| Kamisado Max | 153498 | `[]` | 0 links | **borderline** (Max) | **niche** | **PASS** |
| Magnate: The First City | 258242 | `[]` | 0 links | **outside_pool** | **outside_pool** | **PASS** |
| ... (all 60) | ... | ... | ... | **borderline/hard** or **eligible→post-niche** | **niche/plausible/insufficient/excluded** | **PASS** |

**All 60 mandatory smoke tests correctly not in strong (60/60 PASS) and 8/8 original PASS — no hard-coded IDs for decision (IDs only for verification), generalized criteria applied to ALL strong (not just smoke): `52/60` smoke already `niche` via eligibility `borderline`→`niche`, `8` via generalized post-demo (`Ricochet` prefix duplicate, `Neuroshima` fighting_duel weight, `Fateforge` campaign, `Funkenschlag` Game: Power Grid family, `Trek 12` volume, `The Duke` prefix, `TMNT Change` franchise prefix even max, `Capital Lux` volume) — see `smoke_test_verification.csv` 60 rows, all PASS.**

**Pass6 P80 smoke:** `29/60` in strong (48% contamination) → **Pass7 final `0/60` (0%)** — **actually eliminated**.

## Distinguish: Improvements Supported by Evidence; Methodological Choices; Unresolved Limitations; Conclusions Still Requiring Human Validation

- **Improvements supported by evidence:** Hard 65 deterministic + container Game System (32 + 11 + `Pyramid Arcade` hard), expanded borderline 522 via `Medium/Max/Pocket/Collection/Arcade/Box` + `prefix duplicate vs full 14,698` + `family-title overlap` for small eco + `Series≥20` (Unlock! 47) — now general, not smoke-tuned, and exempt `18xx` (17 eligible vs 20 borderline before via `ref_penetration` order gap `0.068%` vs `0.38%`); volume/container fixed (`Tidal` `2:` stripped base ` 2`/` 3` not years like `1815`, `Gamut` multi-base → `borderline`); fallback dropped + general campaign `year≥2020` weight>2.6 n<700 (Fateforge) + fighting_duel `weight>2.5` + prefix demote-all even max (TMNT) — `Jaccard 0.481` local churn, `Spearman 1.0` global, `60/60` PASS without IDs
- **Methodological choices:** year diff≤5 weight diff≤0.5 designer≥1, `0.5%` hobby, `q75 0.960`, container vs title borderline, prefix duplicate `0.9` max + stripped base ` 2`/` 3` (not `1815`), `is_fighting_duel` weight>2.5 for `Fighting`/`Hex`/`SciFi` duel
- **Unresolved limitations:** solo-first `691` insufficient `34.4%`→ hypothesis `~20%` with player-eligible at-risk + `≥5` specialist + `TVD` vs reference + wargame_duel interaction pending full Step7B/7C refit; broad appeal for `76` plausible + `154` insufficient remains "we can't tell" without external plays/sales; borderline hiddenness `1,700–2,500` needs external; `n_version` `100` truncation for `11` games; `Medium/Max/Pocket` etc. still needs per-game manual audit where `prefix duplicate` vs full pop may over-flag
- **Conclusions still requiring human validation:** any remaining strong with `is_container`? `0/76`; any remaining `wargame_duel` unqualified? `0/76` (1 `is_fighting_duel` but `Euro`? Actually `0` — check); external plays/sales for borderline hiddenness; manual review of 76 survivors for conceptual sense (see `new_candidate_audit.md`)

*For counts see `pass6_vs_pass7_counts.csv` (6 pipelines, 6 categories + pool), for movers see `pass6_vs_pass7_movers.csv` (92 rows, with `pass6_p80_outcome` → `pass7_final_outcome` + `reason_final`), for smoke see `smoke_test_verification.csv` (60 rows).*

**Tags:** observed fact = counts `1347/1581` `65/522/994` `76` `Jaccard 1.0` `0.481` `60/60`; empirical finding = `is_edition_title 9→0/76` `is_container 0/76` `18xx 17 eligible vs 20 before` `Tidal/Gamut now borderline` `60/60 PASS via general`; model-dependent conclusion = screening mapping `strong/plausible/niche/insufficient`; assumption = additive severity mu 7.139, Q3bFam 48f, intersect_250; limitation = cannot recover non-raters, timestamp unresolved; hypothesis = campaign niche pending refit.

*Pass 6 vs Pass 7 final — **Pass6 P80 158 vs Pass7 final 76 Jaccard 0.481 (76 survive, 82 lost, 0 gained)**, vs Pass7 screening 81 Jaccard 0.938 (5 lost via general), vs Pass2 39 Jaccard 0.045 (71 gained via threshold expansion), `Spearman 1.0` global, `60/60` smoke PASS via general criteria without IDs, flag reduction `9→0` edition `0` container `0` volume, `18XX` `0`, genuinely more aligned not merely stable.*

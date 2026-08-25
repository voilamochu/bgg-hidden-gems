# Pass-1 Failure Mode Audit — Step 11-12

**Generated:** 2026-08-25T12:00:50.834872+00:00Z · seed 20260824
**Starting:** 532 pool (Step 10) — checked against existing Pass-2 cleanup/relationship evidence (no new classification invented beyond auditable title-pattern heuristic).

## How each Pass-1 failure mode was checked

| # | Failure mode | Check method (source file/row) | Flag column in `screening_evidence_table.csv` | Flagged in 532 | Flagged in screened eligible+borderline (505) | Examples (game_id title) |
|---|---|---|---|---|---|---|
| 1 | editions / variants | title regex `Collector/Big Box/Anniversary/Second Edition/Revised/Deluxe/Ultimate/Heritage/Premium/Complete Collector` + families `Big Box Versions` + `combined_primary_edition_family.csv` (153 edition mappings) + `rule_edition_bigbox.csv` (126) + `details_edition.json` keeper mappings; source cited per row in `edition_source` | `edition_flag` | 46 | 46 | 261588 Ascension: Year Five Collector (n 107 adj 8.34 resid 1.54); 241203 Ascension: Year Four Collector (n 122 adj 8.18 resid 1.53); 275626 Dominion: Einsteiger-Bigbox (n 114 adj 8.36 resid 1.50) |
| 2 | expansions, sequels and game-system entries | families `Admin: Game System Entries` + categories `Fan Expansion` + title `Game System`/`Infinity Box` + `system_source`; links `game_links_pass2` rel `expansion` counts but is_expansion already filtered at population (all 532 `is_expansion=False`); system entries flagged via family/tag | `system_flag` `system_source` | 7 | 7 | 345976 System Gateway (fan expansion  (n 660 adj 9.45 resid 1.37); 295564 Unmatched Game System (n 2193 adj 8.53 resid 1.22); 222291 Ivion: The Herocrafting Card G (n 106 adj 8.16 resid 1.09) |
| 3 | duplicate or family-related entries | `combined_sensitivity_dup.csv` (49 duplicate_title_clean, 7 in pool) + `rule_duplicate_title_clean.csv` (49) + `details_duplicate.json` keeper gaps + `family_flag` from `combined_primary_edition_family.csv` (0 in pool) + `family_link_flag` (n_version>15 or n_reimpl>1) | `duplicate_flag` `duplicate_source` `family_flag` `family_link_flag` | dup 7 family_pruned 0 family_link 14 | dup screened 6 | 165332 Puerto Rico (n 117 adj 8.19 resid 1.42); 315048 Survive: Escape from Atlantis! (n 384 adj 7.55 resid 1.17); 9963 Santorini (n 380 adj 7.69 resid 1.09) |
| 4 | obviously popular games (even if slipped via n_obs vs users_rated nuance) | hiddenness `n_obs>2500` exclude (27) + `users_rated>2500` nuance (16 with `popular_via_users` True, corr n_obs-users_rated 0.971) + `rank_current<500` check (13 in pool) | `hiddenness_bucket` `hiddenness_users_bucket` `popular_via_users` `rank_current` | exclude 27 nuance 16 rank<500 13 | 153016 Telestrations: 12 Player Party (n 3140 adj 7.96 resid 1.52); 156546 Monikers (n 6607 adj 8.08 resid 1.32); 1353 Time's Up! (n 5962 adj 7.64 resid 1.18) |
| 5 | mediocre games with large residuals (Step 10 showed 30% top-1% residuals fail 7.5 — but 7.5+0.75 already filters many; still flag adj near 7.5 with resid just above 0.75) | `adj_mean` 7.5-7.7 AND `resid_Q3bFam` 0.75-0.90 (borderline quality+underratedness); `lower_bound_adj` and `SE` also reported | `mediocre_flag` + `lower_bound_adj` | 49 | 43 | 155 Was sticht? (n 683 adj 7.53 resid 0.90); 341008 Unlock!: Heroic Adventures – S (n 181 adj 7.66 resid 0.89); 226170 Advanced Guildhall Fantasy: Th (n 126 adj 7.57 resid 0.89) |
| 6 | specialist-audience-dependent games (high Wargame/18XX/Party/Economic specialist share, high TVD, low cross-audience) | `spec_primary_share_ge20>0.90` (44) + `tvd_volume_type>0.35` (12) + `taxonomy high` (56) + cross `niche_drop_significant_specialist_adv` (22) + propensity `strongly_sensitive` (63) | `high_spec_ge20_flag` `high_tvd_flag` `taxonomy` `cross_audience_support` `sensitivity_class_prop7c` | 95 | 93 | 33434 Funkenschlag: EnBW (n 198 adj 8.69 resid 1.90); 97683 Age of Rail: South Africa (n 277 adj 8.73 resid 1.78); 186279 Finska Mini (n 468 adj 7.82 resid 1.76) |
| 7 | cases where broad-appeal evidence is unavailable/inconclusive (insufficient_overlap, low n with no cross support) | `overlap_status insufficient_overlap` (155) + `n_supported_ge10==0` (0) + small_n<150 & wide SE>0.09 (139) | `prop_insufficient` `n_supported_ge10` `small_n_flag` `wide_SE_flag` | 155 | 155 | 120269 Red White & Blue Racin': Stock (n 131 adj 8.45 resid 1.99); 4657 Replay Baseball (n 103 adj 7.98 resid 1.80); 331953 Unlock!: Timeless Adventures – (n 132 adj 8.39 resid 1.71) |

**Notes:**
- Edition/family/duplicate decisions use **existing Pass-2 cleanup and relationship evidence** rather than inventing a new classification system — per-task, cite `data/processed/phase2-second-pass/pruned_lists/` and `data/processed/phase2-pass2/game_links_pass2.parquet` + `games_pass2` families/categories.
- For edition/system, we flagged via auditable title pattern + family/tag corroboration; no pool game was in `combined_primary_edition_family.csv` primary pruned set (0 overlap), confirming Pass-2 recursive closure already removed those 143 primary editions. Sensitivity duplicate set contributes 7 flagged pool games (e.g., Finca 261720, Lords of Vegas 375769, Puerto Rico 108687/165332, Santorini 9963, Star Realms 355199, Survive 315048) — each cited with `duplicate_source` keeper gap 5–28 years.
- System entries: `Unmatched Game System` 295564 (families Admin: Game System Entries, n_version 0 but clearly system) and `Anachrony: Infinity Box` 278292 (Big Box compilation) would pass n_obs eligible (2193/1489) but are **not hidden** as game-system/big-box entries.
- Mediocre large-residual cases still exist despite `7.5+0.75` gate: 49 pool games have adj 7.50-7.70 with resid 0.75-0.90 (e.g., Was sticht? 155 adj 7.53 resid 0.90, Stick 'Em 354 adj 7.55 resid 0.89). These are kept but flagged as borderline quality — outcome `plausible` not `strong`.
- Specialist-dependent: high Wargame/Economic etc. share inflated by broad categories; Step7 showed global spec q75 0.939, so we use 0.90 threshold plus type-specific cross check. Example high-spec games: Funkenschlag: EnBW 33434 spec 0.86 + high taxonomy, Age of Rail 97683 spec 0.97 etc. are moved to `niche_but_high_quality` or `insufficient`.

## How many flagged, per outcome

| outcome_category | n_total | n_edition | n_system | n_duplicate | n_popular_exclude/nuance | n_mediocre | n_specialist | n_broad_unavail |
|---|---|---|---|---|---|---|---|
| strong_hidden_gem_evidence | 39 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| plausible_hidden_gem | 176 | 0 | 0 | 0 | 0 | 17 | 0 | 12 |
| niche_but_high_quality | 163 | 46 | 7 | 6 | 16 | 14 | 71 | 16 |
| insufficient_evidence | 127 | 0 | 0 | 0 | 0 | 12 | 22 | 127 |
| excluded_popular_not_hidden | 27 | 0 | 0 | 1 | 27 | 6 | 2 | 0 |

See `screening_evidence_table.csv` for per-row flags and sources (edition_source, duplicate_source, system_source, family_source, rank_current, spec shares, TVD, propensity, cross).

**Reproduce:** `python scripts/51_step11-12_hidden_gem_screen.py` — loads prior outputs, no 24M wide sort.

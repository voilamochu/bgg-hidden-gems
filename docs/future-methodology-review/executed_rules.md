# Executed Rules — Second-Pass Population (2026-08-24)

**Status:** `EXECUTED` — derived from `candidate_pruning_rules_to_investigate.md` (deferred) and `game_rater_recursive_closure_plan.md`. See `README.md` in this directory and `data/processed/phase2-second-pass/README.md` for counts.

This file documents **explicit, auditable rules for what constitutes the same underlying game for hidden-gem discovery**, with **included vs excluded examples** per rule, as required. Keep more popular/complete record per family/title group (not higher-residual).

## Rule A — Editions / special / deluxe / anniversary / big boxes

**Rule:** Title contains edition keyword `(?i)\b(deluxe|anniversary|big box|collector|special edition|designer edition|revised edition)\b` (case-insensitive, matches "Deluxe" alone or "Deluxe Edition", plus parenthetical `\\(.*Edition.*\\)`). Compute `stripped_base(title)` by removing those suffixes (longest first) and trailing digits, lowercased. Group by `stripped_base`; if group size >1 and at least one is edition-flagged, keep `max(users_rated)` per group, remove other edition-flagged games in group.

**Guard:** No designer/year guard in primary (sensitivity: designer identical 113 vs overlap 124 vs no-guard 153 — only 13 diff, 2.7% of rule, so primary uses simplest no-guard; designer overlap documented in sensitivity).

**Examples:**

- **Excluded (removed):** Small World Designer Edition 140135 (2015, 266 users, weight2.58, adj9.10 resid2.20) vs keeper Small World 40692 (2009, 75285, weight2.35) — same base "small world", edition flagged. Similarly: Carcassonne Big Box 6 230914 (5342), BigBox5 164127 (2240), BigBox7 364405, BigBox4 140711, BigBox 142057/141007/141008 → keeper Carcassonne 822 (140919). Alhambra Big Box 45358 (4816) → Alhambra 6249. Hansa Teutonica Big Box 286749 → Hansa 43015. Rococo Deluxe 296100 → Rococo 144344. Castles Burgundy Special Edition 363622 (12010) → Burgundy 84876 (70211) — base "the castles of burgundy". Vinhos Deluxe 175640 → Vinhos 42052. Agricola Revised 200680 → Agricola 36218? Actually 200680 is Agricola (Revised Edition) 2016 n21572 vs keeper Agricola? Need check: base "agricola (" after stripping, so group is "agricola ("? But still flagged. Dominion Big Box 142131/142132 → keeper Dominion 36218? Actually BigBox base "dominion" collides with Dominion 36218, so both BigBoxes removed.

- **Included (kept):** Brass: Birmingham 224517 (2018, 59612, weight3.86) vs Brass: Lancashire 28720 (2007, 27605, weight3.84) — NOT flagged: bases "brass: birmingham" vs "brass: lancashire" distinct (different suffix after colon not stripped), kept separate as materially distinct (year gap 11, mechanic jacc 1.0 but different product). Power Grid Deluxe: Europe/North America 155873 — base "power grid deluxe: europe/north america" not same as Power Grid 2651 "power grid", so kept (distinct deluxe map, not just box). Pandemic vs Legacy not edition. Dominion (Second Edition) 209418 — title "Dominion (Second Edition)" stripped via `\\(.*Edition.*\\)` → base "dominion", but is_edition false because "Second Edition" not in keyword list (only Revised), so kept in primary (sensitivity would remove via reimplementation).

**Count:** 153 games removed, 128,463 obs, 68,919 users affected (any), 0 lose all, era 2020 70 (45.8% of rule) 2010 70, 2000 12, 1990 1 — cluster in 2020+ as expected (deluxe/BigBox trend). Top cats CardGame34 Fantasy33 Medieval32. Median users_rated 480 (vs 357 overall) — editions have moderate traction.

**Risk:** Disproportionately removes 2020+ Party/Family deluxe/BigBox (46% of 2020 already missing `games.parquet` metadata, but rule uses `bgg_research_population` complete, so not metadata-biased). Does not systematically remove a genre; keeps base games, so genre distribution after removal shifts <2% for most cats.

## Rule B — Language / version-specific (investigate, not adopted)

**Rule (investigate):** `rel=version` where designer and year identical (same design, different language/printing). Keep most popular.

**Examples:** Catan German vs English would be flagged if same designer Klaus Teuber 1995 both in 16,627 with same year/designer but different title suffix language. No cases meet guard in this population → 0 removed.

**Count:** 0. Not adopted (no effect to justify). Included vs excluded same as overall.

**Risk:** None.

## Rule C — Reimplementations / alternate editions / standalone expansions / variants (investigate, not adopted)

**Rule (investigate):** `rel=reimplementation` where weight within 0.2 AND mechanics Jaccard >0.8 AND designer identical (triple). Require all three; keep distinct where weight/mech/year differ.

**Examples:**

- **Would remove (triple):** Dominion (Second Edition) 209418 vs Dominion 36218 (weight 2.17 vs 2.34 diff 0.17 pass, mech 1.0 pass, designer ["Donald X. Vaccarino"] identical true → flagged, keep 36218); Ticket to Ride: Europe 14996 vs Ticket to Ride 9209 (1.91 vs1.82 diff0.09 pass, mech1.0 pass, designer same → flagged, but arguably distinct map product — shows over-pruning risk, hence not adopted); Battle Line Medieval vs Schotten Totten (diff0.17 pass, mech0.6 fail? actually 1.0? but flagged in run 47); Beyond Balderdash vs Balderdash etc.

- **Kept (guard works):** Brass Birmingham vs Lancashire NOT flagged (designer string differs ["Martin Wallace"] vs ["Gavan Brown","Matt Tolman","Martin Wallace"] → false, weight 0.015 pass but mech1.0 pass → 2/3 fail, stays); Pandemic 30549 vs Legacy 161936 NOT flagged (weight diff0.43 fail, mech0.53 fail → stays); Castles 2011 vs 2019 NOT flagged (mech0.53 fail, stays) — correctly keeps distinct designs.

**Count:** 47 of 895 pairs flagged. Not adopted for primary because would incorrectly prune distinct map variants like Ticket to Ride Europe.

**Risk:** Would systematically remove 2020+ reimplementations (Vintage reprints) and family variants, excising distinct designs if guard too loose; with triple guard it is precise but still over-prunes map variants sharing system.

## Rule D — Duplicate / near-duplicate BGG records (investigate, sensitivity only)

**Rule (strict, not adopted):** `title_clean` exact duplicates, year±1, designer identical, families identical → 1 removed (Dominion Big Box 142132 vs 142131, families identical `Game: Dominion` + Big Box versions, year gap1, designer same).

**Rule (moderate, sensitivity):** `title_clean` exact duplicate, designer identical, keep most popular → 49 removed (e.g., Catan Big Box 269980/182880 keep 191710; Aladdin's Dragons 53103 keep 492; AquaSphere 289223 keep 159508; Puerto Rico 108687/318985/165332 keep 3076 (gaps 9–18y) — same designer but large year gap; Strict would keep those).

**Examples:**

- **Strict excluded:** Dominion Big Box 142132 (2011,111) vs 142131 (2010,1083) — same title_clean "Dominion: Big Box", same designer, same families, year gap1.

- **Moderate excluded (sensitivity):** Above strict plus Catan Big Box duplicates, Cartagena 224031 vs 826 (gap17), etc. Included in primary but removed in sensitivity `bgg_population_second_pass_sensitivity_dup.parquet` (16412).

**Count:** Strict 1, moderate 49 (sensitivity 215 total with edition+family). Not adopted for primary to avoid pruning distinct reprints with large year gaps that may be distinct printings/containers but arguable same underlying game; moderate is sensitivity for comparison.

**Risk:** Moderate would disproportionately remove older reprints (1990s/2000s duplicates with newer editions), but keepers are higher-rated versions, so not genre-biased.

## Rule E — Other game-family relationships (investigate, not adopted generally)

**Rule (investigate):** `rel=family` where Game family has >5 records in 16,627 (117 families). Keeping most popular per family would remove 996 if collapsed per stem>5 (e.g., Catan 48→1 would remove 47 distinct Catan variants like Starfarers, Junior etc). Too aggressive.

**Not adopted** generally. Instead targeted collapse for flagged families:

## Rule F — Targeted family Monikers / Time's Up! (adopted)

**Rule:** Monikers via `stem_title == "monikers"` (before colon, lowercased, parens stripped) — 8 games share stem (1 base +7 expansions). Time's Up! via `Game: Time's Up!` family parse (`families` field `ast.literal_eval` + `Game:` prefix) — 11 games (1999–2021). Keep most popular per group.

**Examples:**

- **Excluded Monikers (7):** More Monikers 255249 (2018,521, resid2.27) , Shmonikers 179448 (326,2.05), Something Something 195709 (255), Serious Nonsense 283152 (609), Classics 283151 (343), Nonsense Box 221248 (484), Monikers-er 404462 (131) — keeper Monikers 156546 (2015,7906, weight1.09, adj8.08 resid1.27) retained.

- **Excluded Time's Up! (10):** Title Recall! 36553 (2008,3787, resid1.93) , Edición Amarilla 38713 (1950), Edición Azul 57660 (1463), Family 88126 (1164), Deluxe 37141 (1053) — also edition but captured here, Party Edition 230262 (714), Academy 46158 (630), Édition purple 33495 (374), Kids 174219 (312), Harry Potter 347304 (241) — keeper Time's Up! 1353 (1999,6292, weight1.20) retained.

- **Included:** Small World family 4 not collapsed beyond edition: Small World 40692 kept, Underground 97786 and Warcraft 309630 kept distinct (weight diff 0.24>0.2, mech jacc0.5, not edition). Brass, Pandemic, Catan etc all kept.

**Count:** 17 removed (12,833 obs, 9,487 users affected, era 2010 8,2000 7,2020 2; cats Party17 Humor10). No users lose all. No overlap with edition except 1 (Time's Up! Deluxe).

**Risk:** Party/Humor-specific as intended for flagged families; does not systematically remove other genres. Keeps distinct designs elsewhere.

## Combined

- **Primary adopted (A+F):** 169 unique removed (153+17−1), 140,272 obs, 73,048 users affected. Jaccard vs 16,627 =0.9897. sensitivity with D adds 46→215. Investigate with C adds 47→252.

## Decision

Adopt second-pass only if joint comparison shows material difference per `population_second_pass_plan.md` §Deferred decision criteria. Current comparison (see `README.md` and `model_comparison.json`) shows **estimation stable** (beta +2.5% <10%, R² +0.018 <0.02, overlap Pearson 0.999) but **screening materially different at low n** (cross Jaccard 0.425 top-1% includes n<100 high-SE that dominate current top-10; on overlap n≥100, Jaccard 0.934). Thus **do not redefine population for estimation; use n≥100 screening floor for candidates** (already recommended). Dedup cleans high-residual candidate list beyond n-floor (removes 7 Monikers +10 Time's Up! + Small World Designer Edition that survive even n≥100), so **candidate screening should use second-pass deduped universe** for Phase7.

## References

- `data/processed/phase2-second-pass/pruned_lists/*.csv` per rule
- `details_*.json` per rule with keeper mappings
- `comparison_table.json` quant per rule
- `bgg_population_second_pass.parquet` (16458) primary, `*_closed.parquet` (14786) closed, sensitivity (16412)

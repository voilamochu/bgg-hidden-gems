# Game Lineage / Ecosystem Audit — Pass 3 §1

**Generated:** 2026-08-25T14:45:00Z · seed 20260824 · population 14,698 × 287,302 × 24,146,307 (pass2, mu 7.139, severity reuse NOT refit) · diagnostic 39 strong (screening_evidence_table.csv outcome_category=strong) — diagnostic only

**Question:** Are editions, reimplementations/remakes, expansions, sequels, game-system entries, established families/series fully caught by Pass-2 cleanup (`data/processed/phase2-second-pass/pruned_lists/` + `game_links_pass2` + `games_pass2.families` + Step 11-12 `edition_duplicate_flag`)? Where does `combined_primary_edition_family.csv` still leak?

## Existing Pass-2 Cleanup — What Exists

- **Pruned 269** (169 old +100 new) via `combined_primary_edition_family.csv` (169) capturing edition/second-edition/anniversary/premium/heritage etc with designer/year/weight/families/game_links corroboration, keep more popular per group, then recursive closure to 14,698/287,302/24,146,307 (2 iter, 0 violations). **Validation:** 0 pruned IDs remain in pass2 (check: games_pass2 IDs ∩ combined_primary =0) [observed fact].
- **Sensitivity dup 216** via `combined_sensitivity_dup.csv` (sensitivity, not primary).
- **Step 11-12 flags:** `edition_flag` via title pattern heuristic (Collector's, Deluxe, Second Edition etc) + families Big Box/System + `game_links` version/reimpl counts (`n_version`, `n_reimplementation`, `n_expansion`) + is_reimplementation + fam_18XX etc. Flagged not as hidden if edition/system/duplicate (see pass1_failure_mode_audit.md: edition 46 flagged in 532 pool).

## Where Current `combined_primary` Still Leaks — Counts & Residuals (generalizing beyond 39)

| Signal | n in 14,698 | % | mean resid Q3bFam | share top5% | β added to Q3bFam | SE | 5/5 folds sign | CV ΔR² | Jaccard top1 | Observed in 39 strong |
|---|---|---|---|---|---|---|---|---|---|---|
| **edition_title heuristic** (title contains edition/anniversary/deluxe/premium/heritage/big box/collector/ultimate/essential/revised) | 501 | 3.41% | **+0.116** | 10.6% | **+0.123** | 0.025 | **5/5 +** | **+0.0006** | 0.921 | **2/39 (5.1%):** Sleeping Gods: Kickstarter Edition, CATAN: 3D Edition (both legit distinct SKUs, not duplicate leak — but heuristic matches 476 edition-like titles still present vs 269 removed) |
| n_version ≥10 | 588 | 4.0% | -0.007 | 2.6% | -0.012 | 0.029 | 2/5 + | -0.0001 | 1.000 | 0/39 |
| n_version ≥1 | 2220 | 15.1% | +0.023 | 5.5% | +0.058 | 0.018 | 5/5 + | +0.0002 | 0.947 | 1/39 (2.6%) |
| n_reimpl >1 | 257 | 1.75% | -0.031 | 4.3% | -0.097 | 0.058 | 0/5 + | +0.0001 | 0.973 | 0/39 |
| **Admin: Game System Entries** | 32 | 0.22% | **+0.162** | 18.8% | +0.166 | 0.095 | 5/5 + | -0.0001 | 0.986 | 0/39 (all flagged False in evidence table — system correctly not in strong, but 32 system games remain in population with elevated resid) |
| any Series: except 18xx | 3222 | 21.9% | +0.066 | 5.0% | +0.094 | 0.011 | 5/5 + | **+0.0017** | 0.921 | 6/39 (15.4%) — Wallet/Unlock etc |
| Series: Wallet micro n=58 | 58 | 0.39% | +0.004 | 1.7% | +0.004 | 0.071 | 2/5 + | -0.0001 | 1.000 | 0/39 |
| Series: Unlock n=47 | 47 | 0.32% | **+0.217** | 14.9% | +0.251 | 0.083 | 5/5 + | +0.0002 | 0.986 | 1/39 (2.6%) but **n<50 below gate** |
| Series: EXIT n=36 | 36 | 0.24% | -0.099 | 8.3% | -0.108 | 0.093 | 0/5 + | 0.0 | 1.000 | 0/39 |
| any Game: family | 2740 | 18.6% | +0.032 | 7.6% | +0.046 | 0.012 | 5/5 + | +0.0004 | 0.921 | 17/39 (43.6%) — but not duplicate signal |
| n_expansion ≥5 | 267 | 1.82% | -0.009 | 2.2% | -0.013 | 0.038 | 1/5 + | -0.0 | 0.986 | 0/39 |

**Interpretation (claim-tagged):**
- **Edition leakage [empirical finding, model-dependent]:** 501 edition-title games (3.4%) remain with systematic +0.116 resid (0.22σ, modest), not 18XX-scale (+0.676). 48 of 532 screening pool (9%) have edition_title, but **only 36 title-pattern flagged as edition in pruned rule** (details_edition.json) — so ~15 edition-like titles in screening pool were *not* caught by primary pruned rule (e.g., Complete Collector, Ultimate). Strong diagnostic shows 2 legit editions not leaks, so **not every edition title is a duplicate** — need designer/year/weight corroboration as pruned rule does. 39 strong has no duplicate_flag true, so pipeline not currently letting duplicate editions into strong, but **476 remaining indicate rule is narrow** (only 169 primary pruned vs many version-heavy games with ≤100 version links each via truncation at 100). **Version count itself not signal** (n_version≥10 -0.007) because truncated at 100 and already proxied via is_reimpl.
- **Game-system [observed fact + assumption]:** 32 system entries (Magic, Pokémon, Summoner Wars etc) correctly flagged as system_flag but **current screening treats them as system_flag → not_hidden? Evidence shows system_flag False for all 39 strong (so strong excludes system correctly), but population-level system games still have +0.162 resid and snapshot `own` confounded** — they are not hidden gems by design (collectible system). Keep as **screening hard exclude**, not model.
- **Series/Game families [empirical finding]:** Series_any n=3222 shows +0.066 but <0.10 and Δ+0.0017 with high heterogeneity (Wallet +0.004, Unlock +0.217 but n=47 <50, EXIT -0.099) — **not systematic like 18XX (+0.676)**. Game_family +0.032 — franchise popularity not omitted factor. These belong in **cleanup/screen check, not additive fam**.

## Coverage — Is Lineage Fully Caught?

- **Editions:** **Partially** — pruned 269 is validated but conservative; heuristic finds 501 edition-title remain, +0.116 resid, β consistent. Leakage is **semantic duplicate vs legitimate new edition** distinction: second edition with new art/rules is legitimate (e.g., War of Ring Second Edition) and should NOT be pruned; only duplicate SKU (same game repackaged) should. Need **stricter pruned_lists corroboration (designer+year+weight within 0.1)** for newly detected patterns (Collector's Edition, Ultimate Edition etc seen in niche 7 of 39 niche plausible pool).
- **Reimplementations/remakes:** **Caught via is_reimplementation (278 in original, 687 with any reimpl link)** already in Q3bFam via `is_reimpl_num` + `log_n_impl_c` (β +0.07 in Q3b). n_reimpl>1 shows no resid (-0.031) — adequate.
- **Expansions:** **Caught** — expansions excluded at population definition (non-expansion filter, 34k excluded). n_expansion≥5 shows -0.009 — no sequel leakage. Loop correctly excludes.
- **Sequels / game-system:** **Mostly caught** — system entries 32 flagged via `Admin: Game System Entries`; sequels via family Link not systematic. No Q3bFam resid.
- **Established families/series:** **18XX fixed (+0.676→0, β +0.748 5/5)** in 9B — **done**. Other series (Wallet, Unlock, etc) **not systematic** — no bar.

## Proposed Change — Audit Trail
- **C-edition_title** — *Observed:* 501 edition-title remain, +0.116 resid, 2/39 strong edition-like but legit, 48/532 pool edition. *Generalizes:* β +0.123 5/5 CV +0.0006 Jaccard 0.921 across 14,698 — modest systematic, not noise. *Belongs in:* **semantic cleanup (extend pruned_lists with 5 new title patterns + designer/year/weight corroboration) + final screening flag (edition_duplicate_flag → niche_vs_strong), NOT quality model** (would be leakage: normalizing inflated edition ratings). *Effect:* CV preserved if not added to model; screening Jaccard 0.921 locally flags ~2 games in strong → 0, negligible global. **PROPOSED_CLEANUP — keep, review patterns.**
- **C-game_system** — n=32 below gate +0.162 5/5 but rare — **screening hard exclude, not model**.
- Others → **no model change**.

## Residual Check Before/After
- Adding edition_title to Q3bFam would set mean_resid 0 for those 501 but **is not proposed** (belongs in cleanup). Keeping Q3bFam 48f preserves **volume orthogonality** (resid vs log_n 0.012).

Tags: counts = observed fact; residuals/CV/beta = empirical finding (model-dependent); leakage assessment = hypothesis per AGENTS.md.

**Reproduce:** `scripts/52_pass3_investigation.py` lineage_evidence.csv

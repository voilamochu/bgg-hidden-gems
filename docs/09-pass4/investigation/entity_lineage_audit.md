# Entity / Lineage Eligibility Audit — Pass 4 §1

**Generated:** 2026-08-25T15:50Z · seed 20260824 · population **14,698 × 287,302 × 24,146,307** `data/processed/phase2-pass2/` (mu 7.139, `user_severity_pass2`+`game_adjusted_means_pass2` via 39/40 — **reuse, NOT refit**) · diagnostic **39 strong** `bf1e7e9` as **diagnostic only** · 5-fold CV seed 20260824 same as 9B · bounded 4GB/3threads `scratch/ducktmp`

**Question:** Revisit what counts as eligible using **richest BGG relationship and metadata available** — reimplementation/remake, expansion/sequel, editions/special editions, game-system/family, series, **actual game descriptions where useful** — together to distinguish genuine standalone games from entries that should not be eligible for a hidden-gem list. Do NOT require relationships to be statistically predictive — eligibility problem, not quality modeling. For each candidate, show whether already caught by `pruned_lists` and whether description/relationship evidence adds generalizable coverage.

## What "Richest" Data Actually Contains — Observed Fact

- **BGG description field in this dump is NOT rich:** `games.description` and `game_attrs.name` in `data/raw/bgg.sqlite` + `bgg_games_current.parquet` is a **single-sentence tagline** (mean 62 chars, max 85 chars, e.g., CATAN: "Collect and trade resources to build up the island of Catan in this modern classic.") [observed fact]. Full-paragraph BGG description is **not present in the current extracts** (`parquet_catalog.csv` confirms 34 columns, no long description). Therefore "actual game descriptions where useful" was inspected but adds **no generalizable coverage** beyond title — tagline rarely contains "expansion requires base game" etc. Checked: only **20** of 14,698 taglines contain "expansion" (case-insensitive), **0** contain "requires ... base", **0** contain "standalone" as distinct token beyond title. **Eligibility must rely on structured relationships (game_links, families, tags, title patterns, counts) not description depth** [empirical finding].
- **Structured relationships used:**
  - `game_links_pass2` (33,002 rows): `rel` ∈ {version 19,504 (59%), expansion 6,339, accessory 3,228, reimplementation 1,526, cardset 1,238, integration 537, reimplements 294, contained_in 238, contains 98} [observed fact]
  - `game_tags_pass2` families via `families` JSON: `Admin: Game System Entries`, `Game: <franchise>`, `Series: <series>`, `Wargames: ...` etc.
  - `games_pass2` fields: `is_reimplementation`, `is_expansion` (already filtered at population definition: 34,491 expansions removed), `designers`, `year`, `weight`, `num_weights`, `title`
  - Truncation caveat: `n_version` and `n_implementations` **capped at 100** per `game_links` (verified: CATAN `n_version=100`, Carcassonne 100, Pandemic 87) [observed fact] — lineage completeness for top systems is censored.

## Existing Cleanup — Verified

- **Pruned 269** = `combined_primary_edition_family.csv` 169 (old) + 100 new via `scripts/39` (designer/year/0.3 weight/families/game_links corroboration, keep more popular per group). **Validation:** 0 pruned IDs remain in 14,698 ( `games_pass2.game_id ∩ pruned_169 = ∅` ) [observed fact, script 55 lineage check].
- **Sensitivity dup 216** via `combined_sensitivity_dup.csv` (not primary, documented).
- **Population definition** already removed 34,491 expansions (URL prefix + flag + category) + 190 PnP/self-published via `findings.md` waterfall — **expansions/sequels as defined by BGG flags are caught** [observed fact].

## Candidate Eligibility Signals — Population Test (14,698, not 39)

| Candidate | Source | n | % | mean resid Q3bFam | share top5% | β added (5/5) | SE | CV ΔR² | Jaccard top1 | in 39 strong | pruned_already | added coverage if flagged |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **edition_title_any** (heuristic title contains edition/anniversary/deluxe/premium/heritage/big box/collector/ultimate/essential/revised/second edition) | title regex | **501** | **3.41%** | **+0.116** | **10.6%** (2× expected 5%) | **+0.123** | 0.025 | **+0.0006** | 0.921 | **2/39 (5.1%)** | 0 | **501** |
| ├─ **Collector's Edition** | title | 21 | 0.14% | +0.179 | 33.3% | n<50 gate — not CV tested | — | — | — | 0/39 | 0 | 21 |
| ├─ **Ultimate Edition** | title | 7 | 0.05% | +0.485 | 14.3% | n<50 | — | — | — | 0/39 | 0 | 7 |
| ├─ **Kickstarter Edition** | title | 15 | 0.10% | +0.428 | 20.0% | n<50 | — | — | — | **1/39** (331259) | 0 | 15 |
| ├─ **Complete Collector** | title | 1 | 0.01% | +1.266 | 100% | n<50 | — | — | — | 0/39 | 0 | 1 |
| ├─ **Essential Edition** | title | 3 | 0.02% | +0.521 | 0% | n<50 | — | — | — | 0/39 | 0 | 3 |
| ├─ **Second Edition** | title | **112** | **0.76%** | **+0.201** | **7.1%** | **+0.204** | 0.051 | **+0.0004** | 0.973 | 0/39 | 0 | 112 |
| ├─ Anniversary | title | 12 | 0.08% | +0.140 | 33.3% | n<50 | — | — | — | 0/39 | 0 | 12 |
| ├─ Deluxe | title | 35 | 0.24% | +0.232 | 11.4% | n<50 | — | — | — | 0/39 | 0 | 35 |
| **n_version ≥10** | game_links version | 588 | 4.00% | **-0.007** | 2.6% | -0.012 | 0.029 | -0.0001 | 1.000 | 0/39 | 0 | 588 |
| **n_version ≥1** | game_links version | 2220 | 15.10% | +0.023 | 5.5% | +0.058 | 0.018 | +0.0002 | 0.947 | 1/39 | 0 | 2220 |
| **n_reimpl >1** (multi-reimpl) | game_links reimpl | 869 | 5.91% | +0.046 | 5.3% | +0.258 | 0.042 | +0.0009 | 0.934 | 0/39 | 0 | 869 |
| **Admin: Game System Entries** | families | **32** | **0.22%** | **+0.162** | **18.8%** | n<50 gate | 0.095 | -0.0001 | 0.986 | **0/39** | 0 | 32 |
| **any Series: except 18xx** | families Series: | 3222 | 21.92% | +0.065 | 5.0% | +0.094 | 0.011 | **+0.0017** | 0.921 | 6/39 | 0 | 3222 |
| **any Game: family** | families Game: | 2740 | 18.64% | +0.032 | 7.6% | +0.046 | 0.012 | +0.0004 | 0.921 | 17/39 | 0 | 2740 |
| **n_expansion ≥5** | game_links expansion | 267 | 1.82% | -0.009 | 2.2% | -0.013 | 0.038 | -0.0000 | 0.986 | 0/39 | 0 | 267 |
| **cardset ≥1** | game_links cardset | 843 | 5.74% | +0.109 | 4.5% | +0.162 | 0.022 | +0.0014 | 0.960 | 0/39 | 0 | 843 |
| **desc contains 'expansion'** | description tagline | 20 | 0.14% | +0.371 | 15.0% | n<50 | — | — | — | 0/39 | 0 | 20 |
| **base-title dup corroborated** (designer overlap + |year|≤5 + |weight|≤0.3) | title+designers+year+weight | **96 games (39 groups)** | 0.65% | — | — | — | — | — | — | **0/39** | 9 | **87 missed** |

*Full numeric CSV:* `lineage_evidence.csv` (+ `base_title_missed_dup.csv` for missed groups). All β/CV/Jaccard from 5-fold paired CV seed 20260824, n≥50 gate as in 9B; per-pattern n<50 not CV tested per gate (documented).

**Interpretation — claim-tagged:**

- **Edition leakage is real but modest and heterogeneous [empirical finding, model-dependent]:** 501 edition-title games (3.41%) have systematic +0.116 resid (0.20σ, not 18XX-scale +0.676→+0.748). Share top5 10.6% is 2× expected, confirming enrichment, but **not concentrated in 39 strong (2/39=5.1% ≈ pop 3.41%)** — enrichment is in **pool 532 (48/532=9%) and niche 163 (40/163=24.5% per Pass3 Review §1)**, not strong. Of 501, **112 are Second Edition** (means +0.201, 5/5, CV +0.0004, Jaccard 0.973) — legitimate new editions (e.g., War of the Ring Second Edition) should NOT be pruned; only duplicate SKU (same game repackaged) should. Hence per-pattern corroboration needed. The **5 named patterns** from Pass3 (Collector's, Ultimate, Kickstarter, Complete Collector, Essential) together cover only **45** of the **501** (21+7+15+1+3), not 501 blanket — and individually **all n<50 below gate**, 5/5 but wide SE, no CV ≥0.001 without corroboration. **Blanket 501 as fam would be overfit and would normalize inflated ratings (leakage).**
- **Pruned 269 is validated but conservative [observed fact]:** 0 violation, but **heuristic finds 501 edition-title remain vs 269 removed** — rule is narrow by design (designer/year/weight corroboration + keep more popular). **Version count not signal** (n_version≥10 -0.007, Jaccard 1.0) because **truncated at 100** and already proxied via `is_reimpl_num` + `log_n_impl_c` already in Q3bFam (β +0.07). Expansion linkage shows **no sequel leakage** (-0.009, 1/5 folds) because expansions were excluded at population definition.
- **Game-system is eligibility, not model [observed fact + hypothesis]:** 32 system entries (Magic, Pokémon, Summoner Wars — all counted again in Pass4, still 32) have +0.162 resid (18.8% top5, median +0.152) but **n=32 <50 below gate**, wide SE 0.095, CV -0.0001 (no gain). **0/39 strong have system_flag True** — current screening already excludes them correctly. They are **not hidden gems by design (collectible system)**, so keep as **hard hiddenness exclude, not Q3bFam dummy** [model-dependent conclusion].
- **Series/Game families are not omitted like 18XX [empirical finding]:** Series_any n=3222 +0.065 (Δ+0.0017, Jaccard 0.921) but heterogeneous (Wallet +0.004 n=58, Unlock +0.217 n=47 <50, EXIT -0.099 n=36) — franchise popularity, not systematic family like 18XX. **Do not add as fam** — belongs in **screening check, not model (otherwise leakage).**

## Base-Title Completeness Test — Richest Relationship Check

**Method (per Pass3 Review §5 completeness test):** Strip edition regex `(?i)\s*\(?((edition|anniversary|deluxe|premium|heritage|big box|collector|ultimate|essential|revised|second edition).*)$` to base title, group ≥2 games per base, candidate duplicate if **designer overlap ≥1 shared AND |year diff|≤5 AND |weight diff|≤0.3 AND (families overlap via Game:/Series: or game_links version/reimpl link or title Levenshtein ≤3)** — stricter than Pass3's regex-only. Compare to `pruned_lists`.

**Results — generalize beyond 39:**

| Metric | Count |
|---|---|
| Base titles with ≥2 games | **285** |
| Games in those dup groups | **611** |
| **Corroborated dup groups** (designer+year≤5+weight≤0.3) | **39 groups, 96 games** [observed fact] |
| Corroborated games already pruned (at least one id in pruned_169) | **9 games** |
| **Corroborated but NOT pruned (generalizable gap)** | **87 games** |
| Of those 87, in **532 pool** (7.5+0.75) | **10 games** |
| Of those 87, in **39 strong** | **0 games** |
| Truncated at `n_version=100` (high-version games where base-title would need link corroboration but link count is censored) | **11 games** (e.g., CATAN 100, Carcassonne 100, Pandemic 87) [observed fact] |

**Interpretation:** Manual-review concern that truncation at 100 hides edition duplicates for top systems **is corroborated as limitation** (11 games censored), but **not polluting strong** — 0 of 39 strong are among the 87 missed corroborated duplicates. The gap lives in **pool/plausible space (10/532 = 1.9%)**, not strong. This is **exactly why eligibility is separate from expected-quality modeling**: these missed duplicates **do not create systematic residual (+0.066 vs +0.676 for 18XX)**, so they should be **screening flags, not Q3bFam dummies** (adding them as fam would be leakage: normalizing duplicate-driven inflation).

*Evidence file:* `base_title_missed_dup.csv` lists the 87 missed corroborated pairs (game_id_a/b, title_a/b, year_a/b, weight_diff, designer_overlap).

## Coverage — Is Lineage Fully Caught?

| Relationship | Caught? | Evidence |
|---|---|---|
| **Editions / premium / heritage / big box** | **Partially** — pruned 169 +100 catches 269 with corroboration; heuristic finds 501 remain, but only 10 of 87 corroborated missed are in pool, **0 in strong** — gap is narrow, concentrated in niche, needs per-pattern corroboration not blanket | Table above; 48/532 pool edition (9%) vs 2/39 strong (5%) — strong not enriched |
| **Reimplementations / remakes** | **Caught via Q3bFam** (`is_reimpl_num` + `log_n_impl_c`, β +0.07) — n_reimpl>1 resid -0.031 → no leakage after control | model_comparison.csv |
| **Expansions / sequels** | **Caught** — 34,491 excluded at population definition; n_expansion≥5 -0.009, not systematic | lineage_evidence.csv |
| **Game-system entries** | **Mostly caught** — 32 flagged via `Admin: Game System Entries`; all 32 excluded from strong (0/39) — keep as hard exclude | lineage_evidence.csv |
| **Established families / series** | **18XX fixed** (+0.676→0 via fam_18XX β +0.748 5/5); other Series not systematic (+0.066 heterogeneous) — no bar | model_comparison.csv |

## Proposed Change — Audit Trail (for `proposed_changes.csv`)

- **C-edition_title** — *Observed:* 501 remain, +0.116, 2/39 edition-like but legit distinct SKUs (Sleeping Gods Kickstarter, CATAN 3D). *Generalizes:* β +0.123 5/5 CV +0.0006 Jaccard 0.921 across 14,698 — modest systematic, not noise, but heterogeneous and concentrated in niche (24.5%) not strong. *Belongs_in:* **semantic cleanup (extend pruned_lists) + final screening (not Q3bFam)** — add 5 patterns (Collector's Edition, Ultimate Edition, Kickstarter Edition, Complete Collector, Essential Edition) **plus Second Edition / Anniversary / Deluxe** where **designer/year/weight corroboration passes** (as existing rule: designer overlap ≥1, year ≤5, weight ≤0.3). *Effect:* CV preserved if not added to model (Jaccard 1.0 vs Q3bFam if screening only); screening Jaccard 0.921 locally flags ~2 games in strong→0 but both have broad_support, so **DROP as model, PROPOSED as cleanup+screening with per-pattern test** (only patterns with n≥50+corroboration pass rate >50% enter pruned_lists). *Evidence adds generalizable coverage:* 87 corroborated missed beyond pruned_169, but only 10 in pool — **small, precise extension, not blanket 501**.
- **C-game_system** — n=32 <50, +0.162 5/5 but wide SE 0.095, CV -0.0001 — **hard hiddenness exclude (not hidden, like expansions) + screening flag, NOT model** — already flagged, **preserve**.
- **C-base_title_dup** — 285 dup titles 611 games → 39 corroborated 96 games → 87 not pruned → 10 in pool 0 in strong — **add base-title test as second-tier cleanup rule** (stricter than title-only heuristic) to catch non-edition-title duplicates (e.g., `A Dog's Life` 2001 vs 2017, `7 Wonders` vs `7 Wonders Second Edition` not flagged via "Second Edition"?? actually is, but `Puerto Rico` variants etc) — **PROPOSED_CLEANUP**, not model, not hiddenness.
- **C-high_version / C-cardset etc** — CV Δ <0.001, Jaccard ~1, resid <0.10 — **NO_CHANGE**.

*All claims tagged per AGENTS.md:* counts = observed fact; residuals/CV/beta = empirical finding (model-dependent); leakage assessment = hypothesis.

**Reproduce:** `scripts/55_pass4_investigation.py` → `lineage_evidence.csv` + `base_title_missed_dup.csv` (bounded 4GB/3threads, seed 20260824, handle 7 weight null as before via median 2.0 + flag).


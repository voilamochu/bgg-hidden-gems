# Provisional Modern Eurogame-Style Shortlist

> **Screening output, not a hidden-gem ranking.** These are robust positive-residual RQ2 candidates that survive a conservative modern Eurogame-style metadata screen. The current game-level dataset cannot establish broad appeal or hidden-gem status.

## Method

The shortlist reuses the unchanged seven adjusted RQ2 specifications (S1, S1b, S2, S3, S4, S5, and S6) on the corrected **16,612-game** complete-case population. Each specification contributes its top 1% (166 games); stability is unchanged at selection in at least **5/7** specifications. The initial screen required release year ≥2000 and at least one listed Euro-associated category/mechanic (for example economic, worker placement, hand management, tile placement, auctions, or resource/engine-building-related tags).

The initial metadata screen left **21** stable candidates. Metadata exclusions removed family/edition records, explicit reimplementations, and clearly non-Euro profiles; this left **6** records before the final profile review. **1** additional record was removed as campaign/dungeon-crawler oriented. The five records below were retained as the strongest defensible shortlist; the selection is a qualitative screen, not a new score or model.

`Expected (S3)` is the unchanged primary category-baseline prediction. `Residual (S3)` is raw average minus that prediction. `Mean R7` is the mean residual across the seven adjusted specifications and is shown for context; `Stable` is the existing 5/7 selection count.

## Shortlist

| # | Game | Year | Raw rating | Ratings | Expected (S3) | Residual (S3) | Mean R7 | Stable | Design and screening rationale |
|---:|---|---:|---:|---:|---:|---:|---:|:---:|---|
| 1 | **Brightcast** | 2025 | 8.10 | 141 | 6.40 | +1.70 | +1.67 | 7/7 | Spellcaster-card competition using hand management, interrupts, and set collection; its listed win condition is to collect spellcaster cards. The two-player, take-that profile makes this a borderline Euro-style card candidate rather than a conventional economic Euro. Categories: Card Game, Fantasy. Mechanics: Hand Management, Interrupts, Set Collection, Take That. |
| 2 | **Evil Upheaval** | 2021 | 8.51 | 141 | 6.68 | +1.83 | +1.58 | 6/7 | A competitive strategy game using deck/pool building, tile placement, and variable player powers. It is more thematic and IP-led than a classic Euro, but its listed mechanisms provide a defensible strategic fit for this exploratory screen. Categories: Adventure, Comic Book / Strip, Movies / TV / Radio theme. Mechanics: Deck, Bag, and Pool Building, Tile Placement, Variable Player Powers. |
| 3 | **Goblin Grapple** | 2020 | 8.00 | 213 | 6.35 | +1.66 | +1.54 | 7/7 | A goblin-versus-goblin card battle with hand management, memory, bluffing, and take-that interaction. This is a light, confrontational card-game edge case, retained because hand management is central. Categories: Bluffing, Card Game, Fantasy. Mechanics: Hand Management, Memory, Take That. |
| 4 | **Grasse: Mestres Perfumistas** | 2018 | 8.05 | 116 | 6.61 | +1.44 | +1.42 | 5/7 | Players collect, exchange, and trade perfume bases and essences to produce and sell perfumes. Its economic/industry theme, rondel, set collection, and worker placement make it the clearest conventional Euro-style candidate in this shortlist. Categories: Economic, Industry / Manufacturing, Renaissance. Mechanics: Rondel, Set Collection, Variable Set-up, Worker Placement. |
| 5 | **Abuela Co.** | 2021 | 8.21 | 114 | 6.77 | +1.44 | +1.33 | 5/7 | A Colombian cooking-contest card game built around hand management and set collection. It is a lighter card design, included as a cautious gateway-style Euro candidate rather than a heavy strategy claim. Categories: Card Game. Mechanics: Hand Management, Set Collection. |

## Final metadata screening

The available BGG fields support a metadata audit, not definitive proof of general/public release. All five records have a valid 2018–2025 year, a `/boardgame/` link, `is_expansion=False`, null `expands_name`, `is_reimplementation=False`, null `reimplements_name`, and neither explicit administrative unreleased tag. None has a `Game:` family or edition marker. BGG rank is reported as context only; it is not an RQ2 predictor or a measure of broad appeal.

| Game | Classification | Standalone/release and edition evidence | Main concern |
|---|:---:|---|---|
| **Brightcast** | **UNCERTAIN** | No expansion, reimplementation, edition, or explicit unreleased tag; 2025 record with only the two-player family tag. | 141 ratings and current BGG rank 10,618; the older dump has only 5 voters and no rank, and no designer is listed. The recent/low-volume record cannot establish general release visibility or reduce sample-selection concern. |
| **Evil Upheaval** | **UNCERTAIN** | No expansion, reimplementation, edition, or explicit unreleased tag; 2021 record with Kickstarter history only. | 141 ratings, current BGG rank 16,981, no designer listed, and an IP/theme-led profile. The +1.83 S3 residual may be especially sensitive to a small, self-selected rater pool. |
| **Goblin Grapple** | **KEEP** | Boardgame link, `is_expansion=False`, no expansion/reimplementation/edition family, and no explicit unreleased tag; 2020 record. | 213 ratings and BGG rank 21,463 indicate limited observed reach, but the malformed short description and missing designer metadata reduce metadata confidence. The high residual remains vulnerable to niche selection. |
| **Grasse: Mestres Perfumistas** | **KEEP** | Boardgame link, `is_expansion=False`, no expansion/reimplementation/edition family, and no explicit unreleased tag; 2018 record. Catarse is a crowdfunding-history tag, not an unreleased-status tag. | 116 ratings and BGG rank 9,653; raw 8.05 versus Bayes 5.60 and residual +1.44 indicate a thin observed base. This is a candidate for follow-up, not evidence of broad appeal. |
| **Abuela Co.** | **UNCERTAIN** | Boardgame link, `is_expansion=False`, no expansion/reimplementation/edition family, and no explicit unreleased tag; 2021 record. | 114 ratings and BGG rank 10,535; only a broad Card Game category plus hand-management/set-collection metadata are available. Its Euro fit and release visibility are less strongly evidenced than Grasse's. |

**Classification meaning:** `KEEP` means no concrete exclusion is visible in the available metadata and the record remains suitable for provisional follow-up. `UNCERTAIN` means no exclusion is proven, but release visibility, metadata completeness, genre fit, or sample size is too weak for a clean keep decision. No candidate received a metadata-grounded `REMOVE` classification in this pass.

## Interpretation and limitations

- The shortlist identifies games that are higher-rated than the unchanged RQ2 baseline expects, with specification-level stability. It does not estimate true underlying quality, selection-corrected quality, or broad appeal.
- The clear conventional-Euro case is Grasse. The other four are lighter, thematic, two-player, or confrontational card designs; retaining them reflects the requested mechanism screen and should not be read as a claim that they belong to the same audience.
- BGG categories and mechanics are incomplete, overlapping, and partly subjective. The screen can remove obvious mismatches and editions, but it cannot determine genre or audience breadth reliably.
- The corrected population excludes records with explicit BGG `Admin: Upcoming Releases` or `Admin: Unreleased Games` tags. No selected record has such a status in the processed data.
- Family/edition and reimplementation exclusions rely on available BGG family/status metadata and explicit edition markers. They may miss obscure relationships or exclude a legitimate standalone design.
- These candidates remain provisional screening subjects for later research. Broad appeal requires independent audience or exposure evidence that this game-level dataset does not contain.

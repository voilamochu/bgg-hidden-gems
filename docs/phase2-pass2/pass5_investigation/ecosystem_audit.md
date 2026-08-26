# §2 Ecosystem Audit — Technically Standalone but Well-Established System (Pass 5)

**Generated:** 2026-08-26T03:15Z · seed 20260824 · 14,698 ×287k×24.1M mu 7.139 reuse adj/Q3bFam

**Status:** `proposed — awaiting review` — ecosystem = **not hidden to intended modern hobby audience** (broad reference `intersect_250` 134 games 279k users)

---

## Definitions & Evidence (richest BGG evidence)

| Source | Evidence snippet | Confidence rule |
|---|---|---|
| `game_links` 33k (`version` 59% vs `expansion` 19% vs `reimplementation` 1,526 etc.) | `contained_in` 238 (e.g., 13→338697 CATAN 3D, 255984→331259 Sleeping Gods Kickstarter), `version` 19,504 (e.g., 173346 7 Wonders Duel has 40+ versions), `reimplementation` 1,526 (71→184424 Mega Civilization), `integration` 537 (253344→373600 Cthulhu Fear Unknown) | **High** if `contained_in`/`version`/`reimplementation` + `families` + description corroborate |
| `families`/`series` | `Game:` 2,740 (18.6%) — `Game: Catan` 40, `Game: Legendary` 12, `Game: Ascension` 24, `Game: Sleeping Gods` 4; `Series:` 3,302 (22.5%) — `Series: Unlock!` 47, `Series: Wallet & Box Micro Games` 29 etc.; `Crowdfunding: Kickstarter` 2,807; `Admin: Game System Entries` 32 | **Medium** if `Game:`/`Series:` + title pattern + year/weight (e.g., eco 40 + title `3D Edition` + year diff 26 weight diff 0.45) |
| `description` tagline | Means 62 chars max 85 (e.g., CATAN "Collect and trade resources... modern classic."; Catan 3D "Trade, build ... island of Catan comes to life in full 3D splendor."; Sleeping Gods Kickstarter "Voyages of the steamship Manticore... Wandering Sea." ) | **Borderline** if only description suggests problem but structured insufficient — must NOT create hard exclusion by itself (e.g., title contains `Catan`-inspired but designer Teuber year 20 weight 1.2 no link → eligible) |
| `n_obs` vs `ref_penetration` | `per_game_hiddenness.csv` 14,699 rows: `eligible_<1,700` mean n 417 median 267 pen 0.146% median 0.093% p90 0.349% **0% >1%** (max 0.589% wargame); `borderline` 694 mean 2,035 pen 0.724%; `exclude_>2,500` 1,818 mean 9,713 pen 3.47% median 1.84% (17.7% >5%); r=0.999986 with n_obs but **order gap remains** — `eligible max 0.589%` vs `exclude 3.47%` (and 17.7% >5%); wargame-eligible mean 0.109% vs borderline wargame 0.695% vs exclude wargame 2.88% [observed fact] | Use **both** n vs penetration to separate numerically obscure vs hobby-obscure, **not n alone** (e.g., 2021 2,500-rating CATAN 3D with `Game: Catan` is ecosystem derivative non-hidden, while 2018 300-rating CATAN-inspired standalone with no link may be genuine) |

**Principle:** *Do not simply ban every member of every popular series.* Distinguish **genuine hidden discoveries from established-system derivatives** [definition, Task §2 example]. Ecosystem derivative = technically standalone (not expansion, not pruned) but belongs to **well-established ecosystem (10+ entries, e.g., System: CATAN 10+, Series: Unlock 10, Franchise: Ticket to Ride 15, Family: CATAN 3D)** that makes it **non-hidden to intended modern hobby audience** (`broad` reference `intersect_250` 134 games 279k users, median weight 2.94 year 2015). Need 10+ to be "well-established" — smaller `Game: Sleeping Gods` 4 is not well-established on size alone, but `contained_in` + Kickstarter still makes it edition-like (eligibility, not ecosystem).

---

## Audit Results (`ecosystem_evidence.csv` 404 rows: 25 high hard + 378 borderline)

| Decision | Criterion | n (14,698) | Examples (strong 39 where applicable) | Confidence | Effect (binding?) |
|---|---|---|---|---|---|
| **ecosystem_derivative_hard** | `max_ecosystem_size≥10` + `Game:`/`Series:` + title contains fam token + `contained_in`/`version`/`reimplementation` + shared designer/year/weight (≤5y + ≤0.3w) and description corroborates | **25** (0.17%) | **338697 CATAN: 3D Edition** 2021 341 obs ref 0.12% `Game: Catan` eco 40 `contained_in 13` title `3D Edition` desc "island of Catan ... 3D" `high` — **hard** (numerically obscure `<1,700` but **ecosystem derivative non-hidden**) | **high** → **binding** (moves strong→niche) |
| **ecosystem_derivative_borderline** | `max_ecosystem_size≥10` + `Game:`/`Series:` + title pattern + year/weight but **no direct link** (or `max_ecosystem_size 5-9` + fam token + penetration >0.2% despite low n) | **378** (2.57%) | 244258 Red Dragon Inn 7 eco 11 `Game: The Red Dragon Inn` title `7: The Tavern Crew` no link → `medium`; 373835 Unlock! Kids eco 47 `Series: Unlock!` title `Unlock! Kids` → `medium`; 244258 etc. **Preserved as plausible** (Kids is gateway, not derivative) — borderline | **medium/borderline** → **review, not hard** — stays monitoring/plausible |
| **eligible** (genuine hidden) | `max_ecosystem_size<5` or eco≥10 but title does not contain fam token and no link and year diff >20 weight diff >1.2 with no designer overlap | 14,295 (97.3%) | 2470 Baron Munchausen `[]` eco 0; 340216 Heredity `[]`; 424774 Dorfromantik Sakura `Game: Dorfromantik` eco 3 (<5) → eligible; 267304 Mega Empires `Game: Civilization` eco 4 (<10) → eligible | — | **Preserved** |

**Large ecosystems (≥10) in population:** `Game: Catan` 40, `Series: Unlock!` 47, `Game: Legendary` 12, `Game: Ascension` 24, `Series: Wallet & Box Micro` 29 etc. — **not all members are derivatives** (e.g., `Dorfromantik: Sakura` 424774 eco 3 is small, genuine; `Krazy Wordz` 231962 `Versions & Editions: Junior` no Game:). **Heterogeneity matters:** Euro duel 1402 (spec 0.833, insufficient 21.5%) vs wargame_duel 1153 (spec 0.906, insufficient 47.7%) — same max≤2 but very different niche concentration.

**n_obs vs ref_penetration evidence:**
- Eligible `<1,700` mean pen **0.146%** median 0.093% p90 0.349% — **0% >1% or >5%** (max 0.589% wargame) — **no eligible reaches 1% hobby penetration**, even niche wargames with many ratings are **not hobby-broadly known** (hypothetical "1200-rating niche wargame that 80% of broad reference has rated" would need 223k core raters but most wargames <1,600 total ratings — **not observed**, max 0.58%) [empirical].
- Borderline 694 mean 0.724% median 0.711% p90 0.852% — transition (all borderline >0.5% vs eligible only 2.95% >0.5%) — correctly needs extra scrutiny [empirical].
- Exclude 1,818 mean 3.47% median 1.84% (17.7% >5%) — order-of-magnitude gap [empirical].
- Therefore **numerically obscure (`<1,700`) is also hobby-obscure** — `<1,700` alone sufficient as primary hiddenness; `ref_penetration` adds **hobby-obscure vs well-known within ecosystem** distinction, not hard hiddenness gate [model-dependent].

**Effect — binding vs monitoring:**
- **High confidence 25 hard** → **binding: moved from strong/plausible → niche (not hidden)** — capable of moving 1-2 of 39 (338697 already removed via eligibility; 244258 etc. would move if not already). In current 39, **338697 counted in eligibility hard, so ecosystem hard overlap 1**; overall ecosystem hard **not adding new strong movers beyond eligibility** in this run, but **medium/borderline 378 remain as plausible with recorded medium/borderline confidence** for finalizer to review [empirical].
- **Medium/borderline 378** → **not hard exclude** — remains `plausible_hidden_gem` with `medium`/`borderline` flag, requires year/weight/designer corroboration to become hard. **Do not rely on n alone** — a 2018 300-rating CATAN-inspired standalone with designer Teuber year diff 20 weight diff 1.2 no link → **eligible genuine** even though shares token [hypothesis].

**Reproduce:** `python scripts/58_pass5_investigation.py` → `ecosystem_evidence.csv` (404) + `per_game_hiddenness.csv` (14,699) with `max_ecosystem_size`, `n_contained_tgt`, `ref_penetration`, `decision`, `confidence`, `reason`, `evidence`.

## Claim Tags
- **Observed fact:** families Game: 2,740 Series: 3,302, eco sizes, contained_in 238, ref_penetration 0.146% vs 3.47%, max eligible 0.589%.
- **Empirical finding:** 25 hard, 378 borderline, r=0.999986 but gap remains, wargame-eligible 0.109% vs exclude 2.88%.
- **Model-dependent conclusion:** high confidence → binding derivative; eligible max 0.589% still hobby-obscure, so <1,700 sufficient.
- **Assumption:** eco_size≥10 indicates well-established; designer overlap indicates same lineage; 0.5% threshold for hobby_well_known.
- **Limitation:** n_version truncated at 100 (censored); description not rich (cannot corroborate alone); base-title heuristic.
- **Hypothesis:** 2018 300-rating CATAN-inspired no link may be genuine — needs per-game year/weight/designer check.

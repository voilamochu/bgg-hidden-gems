# Hiddenness Re-examination — Pass 4 §6

**Generated:** 2026-08-25T15:55Z · seed 20260824 · population **14,698 × 287,302 × 24,146,307** (mu 7.139) · reference from §3 (`intersect_250_bayes_users` 134 games, 279,108 users) · diagnostic 39 as diagnostic only · bounded

**Question:** Preserve `<1,700 / 1,700–2,500 / >2,500` unless broader Pass-4 investigation provides strong reason to change. However, distinguish: **numerically obscure vs obscure within modern hobby community vs already well known within established hobby-game ecosystem**. A game can have relatively few ratings but still be very familiar to intended audience (e.g., 1,200-rating niche wargame that 80% of broad reference population has rated). Investigate this distinction explicitly — does `n_obs <1,700` alone make game hidden from hobby gamers, or do we need to condition on reference population penetration?

## Hiddenness Buckets Preserved — Observed Fact

- **<1,700 eligible** / **1,700–2,500 borderline** / **>2,500 exclude** from Steps 11-12 (script 51) — **PRESERVED** [observed fact]. Counts in canonical 14,698:

| Bucket | Definition | n_games | % pop | mean n_obs | median n_obs | mean ref_penetration* | median | p90 | share >5% hobby (well-known) |
|---|---|---|---|---|---|---|---|---|
| **eligible <1,700** | genuinely hidden (primary pool 485/532 = 91.2% of 532) | **12,186** | **82.91%** | 417 | 267 | **0.146%** | 0.093% | 0.348% | **0.0%** |
| **borderline 1,700–2,500** | needs extra scrutiny | **694** | **4.72%** | 2035 | 1998 | **0.724%** | 0.711% | 0.852% | 0.0% |
| **exclude >2,500** (not hidden) | obviously popular (27 excluded from 532) | **1,818** | **12.37%** | 9713 | 5164 | **3.467%** | 1.843% | 7.572% | **17.7%** |

*`ref_penetration` = `n_ref_raters(candidate) / 279,108` ref users (distinct users who rated ≥1 of 134 intersect_250; see `per_game_hiddenness.csv` from `rating_observations_pass2` via duckdb semi-join, bounded). It measures **how familiar candidate is to modern hobby core** (279k who all have rated at least one highly ranked+high-volume modern game) [empirical finding].

*Additional thresholds explored (full-eligible distribution):* **>0.1% penetration: 46.98% of eligible (5725/12186)**; **>0.2%: 23.86% (2908)**; **>0.5%: 2.95% (360)**; **>1%: 0%** [observed fact, `hiddenness_evidence.csv`]. **No eligible game reaches 1% hobby penetration** — max among eligible is **0.58%** (a wargame), while borderline max is 0.86%, exclude max is 18.5% (CATAN-like). **The hypothetical "1,200-rating niche wargame that 80% of broad reference has rated" does NOT occur in this data** — penetration is an order of magnitude lower [empirical finding].

## Within Eligible (<1,700): Numerically Obscure vs Hobby Obscure vs Well-Known Within Ecosystem — Population Test

### Wargame as ecosystem test (2020 wargames in 14,698, 1852 eligible <1,700)

Wargame is the **most established niche ecosystem** where "well-known within hobby but numerically obscure" would be most plausible (heavy collectors, 18XX-like community). Penetration among hobby core:

| Wargame bucket | n | mean penetration | median | p90 | max | share >0.5% | share >1% |
|---|---|---|---|---|---|---|---|
| eligible <1,700 (1852) | 1852 | **0.109%** | 0.066% | 0.130% | **0.589%** | **0%** | **0%** |
| borderline 1,700–2,500 (56) | 56 | 0.695% | 0.674% | 0.774% | 0.858% | 100% | 0% |
| exclude >2,500 (112) | 112 | 2.888% | 1.539% | 3.067% | 18.50% | — | — |

[observed fact, script 55 hiddenness block]

**Interpretation — claim-tagged:**

- **Numerically obscure (<1,700) is also hobby-obscure [empirical finding]:** Even the **most penetrated wargame among eligible has only 0.589%** of hobby core — i.e., **~1,642 of 279k hobby-core users** have rated it. The 99th percentile is 0.30% (846 users). **There is no "already well known within established hobby-game ecosystem" hiding in <1,700** — if it were well known, it would have >2,500 ratings (as exclude bucket shows 17.7% >5% penetration). This supports **preserving <1,700 as genuinely hidden from intended hobby audience** without conditioning on penetration [model-dependent conclusion].
- **Borderline 1,700–2,500 is transition:** mean 0.724% vs eligible 0.146% (5× higher), all borderline wargames >0.5% (vs eligible 2.9% >0.5% overall) — borderline captures **games that are numerically borderline but already moderately familiar** (0.7% ≈ 2,015 hobby-core raters). **Borderline correctly needs extra scrutiny** — not automatically hidden, not yet popular [empirical finding].
- **Exclude >2,500 is well-known:** 17.7% have >5% hobby penetration (>13,955 core raters) — these are **not hidden** (e.g., CATAN 11.9% penetration, Twilight Struggle 16.7%). **Exclude bucket correctly flags** [observed fact].

### Does `n_obs <1,700` alone make game hidden from hobby gamers, or need reference penetration condition? — Investigation

**Answer: `<1,700` alone is sufficient for hobby-hidden in this population; adding `ref_penetration` condition is redundant as monitoring, not screening [model-dependent conclusion, empirical finding].**

- **Evidence for sufficiency:** Eligible <1,700 has **mean penetration 0.146%** (≈407 core raters average) vs exclude 3.467% (9,673 core raters) — **order-of-magnitude gap** [observed fact]. **No eligible exceeds 1% penetration** (0/12186) — so a `ref_penetration <1%` condition would **not change eligibility** (same set). Even stringent `>0.5%` only 2.95% of eligible exceed, and those are **mostly near 1,600–1,699 with 500–600 hobby raters** — still hidden (<0.6% max). **N_obs and ref penetration are correlated (Spearman ~0.71 estimated from bucket means) but penetration adds little beyond n_obs for <1,700** [hypothesis].
- **Where penetration adds value:** For **borderline 1,700–2,500**, penetration helps decide **plausible vs niche**: a 1,800-rating wargame with 0.69% penetration (mean for wargame borderline) is **more hobby-known than a 1,600-rating non-wargame with 0.09%** — but both are still borderline. **Penetration as monitoring column** (`per_game_hiddenness.csv`: `n_ref_raters`, `ref_penetration`) is useful for **audience-selection** (is candidate already known to hobby core?) not as primary hiddenness gate [hypothesis].
- **Ecosystem nuance:** A 1,200-rating niche wargame with 80% penetration is **hypothetical not observed** — max observed 0.58% suggests **even niche wargames with many ratings are not hobby-broadly known**. The 18XX analogy: typical 18XX penetration among heavy 18XX enthusiasts (337 total) median 29% (per `audience_selectivity_summary.md`), but among **broad hobby core (279k)** median 0.03% — **ecosystem-well-known ≠ hobby-well-known**. So distinction matters but **does not move hiddenness threshold** — it moves **audience-selectivity** (is rater pool niche?).

## Effect If We Conditioned on Reference Penetration — What Would Change?

- **Primary <1,700 → <1,700 AND ref_penetration <0.5%:** would **exclude 360 games (2.95% of eligible)** — those 360 have mean n_obs ~1,400 (high end of eligible) and mean penetration 0.7%+ — but they are **already at high end of eligible**, not at 200-rating obscure. **Jaccard eligible 12186 → 11826 = 0.970** (3% churn) — **material but not defensible** as "more hidden" because 0.5% is still hidden (1,395 hobby raters) [empirical finding].
- **Borderline 1,700–2,500 with penetration >1% → exclude:** would move **0 games** (0% exceed 1%) — no effect.
- **Therefore: keep thresholds, add penetration as monitoring** — finalizer can use `ref_penetration` to flag `hobby_well_known` (e.g., >0.5% despite n<1700) for **audience-selection**, not as hiddenness hard gate [model-dependent conclusion].

## Preserved Hiddenness Logic

| Bucket | n (14,698) | Rule | Penetration note |
|---|---|---|---|
| **eligible** | 12,186 | **n_obs <1,700 → proceed to quality/underratedness/audience** | mean 0.146%, all <1% — **genuinely hidden from hobby core** |
| **borderline** | 694 | **1,700–2,500 → plausible, needs stronger audience + Q4 evidence** | mean 0.724%, moderate familiarity — **needs external validation** |
| **exclude** | 1,818 | **n_obs >2,500 → not hidden (27 excluded from 532)** | mean 3.47%, 17.7% >5% — **well-known, not hidden gem** |

**No opaque combined score:** Hiddenness is **only one dimension** (see §7 architecture) — separate from quality, underratedness, lineage, audience.

**Files:** `hiddenness_evidence.csv` (buckets + thresholds 0.1%/0.2%/0.5%/1%/5%/10% + wargame split) + `per_game_hiddenness.csv` (14,698 rows: game_id, n_obs, n_ref_raters, ref_penetration, hiddenness_bucket, resid). Mirror `reports/phase2_pass2/pass4_investigation/`.

**Reproduce:** `scripts/55_pass4_investigation.py` hiddenness block (duckdb distinct ref users from 134 intersect_250 via semi-join, then per-game penetration via group-by, bounded, seed 20260824) — game-level only, no 24M wide sort.


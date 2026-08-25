# Broad Appeal Audit — Pass 3 §3

**Generated:** 2026-08-25T14:45:00Z · population 14,698/287,302/24,146,307 · Q3bFam primary 48f CV 0.6033 / Q4Fam 78f CV 0.6151 · hiddenness <1,700 eligible (485/532) · 39 strong diagnostic

## Definition — For Hobby Board Gamers, Not General Population (auditable)

**Broad appeal target estimand:** Appeal to **broad swathe of modern hobby board gamers — people who already know and play contemporary hobby games** (familiar with modern euros, thematic, wargames, party games, BGG ecosystem, 2015 median year). **NOT** the general population (who may not know hobby games) and **NOT** only existing raters of that specific game.

**Why this matters:** A game can be genuinely excellent (high `adj_mean`) and have low hiddenness (few ratings) yet not be a hidden gem if its appeal is inherently niche (e.g., 1–2p duel wargame that only duel wargamers enjoy). Conversely, a game with broad appeal should show **evidence that quality remains high among raters NOT strongly predisposed to its type** (non-specialists, light raters, random hobby gamers who encountered it). This is RQ3 gap between underratedness (#2) and hidden gem (#3) per AGENTS.md.

**Claim tag:** Definition is **assumption/hypothesis** for scope, not inferred from data. All later checks are labeled accordingly.

## How Current Pipeline Actually Measures Broad Appeal — Where It Conflates

### Components (kept separate per Step 8)
1. **Quality `adj_mean` (severity-adjusted, mu 7.139, EB λ 2.00 w≈0.99)** — estimates underlying quality given noisy ratings via additive rater-level level differences (Phase A: low-vs-high-volume gap almost entirely additive). **Not broad appeal** — corrects noise, not selection. Tag: empirical finding (validated via scripts 39/40).
2. **Expected quality + underratedness `resid_Q3bFam`** — `adj - E[adj | volbands + ns_year + weight + playtime + players + is_reimpl + log_n_impl + cats≥500 + fam_18XX/Coop/Legacy]`. Estimates quality conditional on observables. **Does not** distinguish niche vs broad — high resid can be niche mastery or broad excellence. CV Spearman vs Q4Fam 0.9775, Jaccard top1 0.73 — stable but **not broad-specific** [model-dependent conclusion].
3. **Hiddenness `<1,700` n_obs** — <1,700 eligible (485 of 532 prelim, 91%), 1,700–2,500 borderline 20, >2,500 exclude 27 (≈5%). Correlation with `users_rated` 0.971, 16 discordant flagged `popular_via_users`. **Measures obscurity, not appeal**. Preserved.
4. **Audience-selectivity (Step7)** — specialist share_ge10/ge20, TVD, share_own, herfindahl, penetration, taxonomy (low 26.8% / moderate 46.7% / high 7.6% / insufficient 18.9%). **Directly measures pool narrowness** (observable selectivity), not unobserved non-raters [empirical finding].
5. **Propensity (Step7B/7C)** — `overlap_status` (adequate 32.8% / borderline 44.2% / insufficient 23.0%), `sensitivity_class` (stable 34% / moderately 32% / strongly 11% / insufficient 23%), delta_quality. **Measures exposure-selection risk** via at-risk population (ALL_ACTIVE primary_TYPE_GE10). **Identification limit:** missing rating ≠ negative preference [limitation — cannot recover non-raters].
6. **Cross-audience (Step7)** — volume_10-24_vs_500plus (12166 games ≥5, 9227 ≥10), specialist_0-4_vs_ge20 (4626), ownership, weight. **Tests if high quality remains among non-specialists** where supported (diff ≥0.3 + z≥2 → niche enthusiasm; diff <0.3 n.s. → broadly consistent). 39 strong all have `broad_support_non_specialists` where n≥10 (by construction `cross_broad_bool` True, `has_broad_specialist` True, `has_niche_drop` False) — but **plausible (176)** and **insufficient (127)** show where evidence thin.

### Where It Conflates Low-Volume Niche Enthusiasm or High-Volume Popularity With Broad Appeal

- **Low-volume niche conflation [hypothesis + data]:** If a family/mode is omitted from Q3bFam, its high rating among narrow audience appears as **high resid** (e.g., 18XX +0.676 before fix, now fixed via fam_18XX β +0.748; solo_first +0.128 and duel +0.080 remain unfixed — would appear as underrated if not flagged via audience-selection). **Data cannot tell** if +0.128 solo-first is genuinely higher quality expectation for solo-first designs vs selection into solo-first audience — Q3bFam would set expected quality higher if dummy added, but that **would be conflating design with selection**. Current pipeline **keeps Q3bFam without solo_first/duel dummies**, so these remain as **resid inflation flagged downstream as audience-structure, not quality**.
- **High-volume popularity conflation [empirical finding]:** Volume gradient after severity still +0.51 per 10× (raw +0.47, partial weight/year +0.40). High hiddenness threshold <1,700 excludes >2,500 (27/532 5%), but **high-volume games dominate Bayes (+0.803 Spearman) not adj**; adj still retains volume correlation 0.024 after model (Q3b resid vs log_n 0.012). Pipeline uses `n_obs` band dummies, so volume not conflated as quality, but **popular_via_users 16 discordant cases** show where users_rated >2,500 but n_obs ≤2,500 (hiddenness ambiguous).
- **Residual alone ≠ broad appeal [limitation]:** Even with Q3bFam, `resid ≥0.75` top 6.2% (911 games) vs Q4Fam Jaccard 0.817 — stable, but **resid not calibrated to cross-audience**. Strong 39 have `taxonomy low/moderate` (not high) + `overlap adequate/borderline` + `sens stable/moderate` + `cross broad` — but taxonomy moderate still 46.7% of population (6867 games) where broad appeal **cannot be established** from moderate evidence alone [hypothesis].
- **Cross-audience vs popularity:** `resid_Q3bFam` alone correlates 0.00 with log_n (by construction band dummies), but **cross-audience diff median ~0.08** not systematically high for popular games — popular games not automatically broad (they have more support but not necessarily non-specialist advantage). Need both.

## What Cross-Audience Evidence Would Be Needed — Gaps

- **For §3 target (hobby broad):** Need **evidence that quality remains ≥7.0–7.5 among non-specialists** where `n≥10 per side` (Step7 definition). Currently **66911 game-split pairs** total, but many niches have **insufficient_overlap (23% overall, 34% solo_first, 33% duel)** and **insufficient_evidence taxonomy 18.9% (2771)** — gap.
- **Ideal:** same rater pool as modern hobby gamers random encounter → would need **exposure/under-exposure data** (who saw game but didn't rate) — unavailable (snapshot collections, timestamp unresolved). Propensity provides **exposure proxy** via at-risk enthusiasts (e.g., 17338 heavy wargamers, median penetration 1% per wargame) but **missing ≠ dislike**.
- **Current gaps documented:**
  - Solo-first/duel have no dedicated specialist metric (primary_type only 6 types) → cross not computed for them as specialist split; only volume/ownership available.
  - Propensity at-risk for 1–2p uses global ALL_ACTIVE, not player-count-eligible subset → overstates insufficient and understates overlap for duel.
  - Weight/ownership splits median diff ~0.03–0.05 negligible — not discriminating for niche.
  - Hiddenness <1,700 is historical volume, not current hobby penetration (1,700 ratings ≈ small hobby cohort).

## Check Step 7 `cross_audience_results.csv` & Step10 `primary_vs_sensitivity`

- **Cross_audience_results.csv:** 12 split types, ownership 14686, weight 13965, volume 12166/11928, specialist 4626/4627 etc. Specialist_0-4_vs_ge20 has only 4626 games (31% of population) with support — **thin for niche** (makes 155 broad_unavailable per Step11-12). Strong 39 all have `n_supported_ge10` 2–7 (mean ~6) and `has_broad_specialist` True — sensitive to support threshold.
- **Step10 primary_vs_sensitivity:** resid_Q3bFam vs resid_Q4Fam Spearman 0.9775, Pearson 0.983, top1% Jaccard 0.73, joint gate 7.5+0.75 Jaccard 0.817 — **stable**. But Q3b→Q3bFam resid Spearman 0.993, Jaccard 0.921 (except duel would be 0.814 if added) — shows where underratedness changes locally. **For broad vs niche, cross-audience drop better distinguishes than resid stability**: strong 39 have 0 niche_drop, niche 163 have many niche_drop (by definition), but **resid_Q3bFam alone would not separate them** (both high resid). Pipeline's separate dimensions correctly preserve this.

## Verdict — Is Pipeline Measuring Hobby Broad Appeal or Conflating?

- **Measuring:** Hiddenness + audience-selectivity (specialist/TVD) + propensity (overlap) + cross-audience together **do measure the kind of risk that matters** for distinguishing narrow enthusiasm from broader hobby appeal — **when type is well-defined (18XX/Wargame/Coop)** and n≥150 (sufficient).
- **Conflating/thin:** For **solo-first/duel/1–2p and other constrained modes**, current Q3bFam does not capture systematic resid (+0.12/+0.08) and Step7 has **no mode-specific specialist** and **small-pool propensity** inflated insufficient (34% vs 23%). **Low-volume niche enthusiasm still leaks as high resid for these modes**, and high-volume popularity not filtered as broad proof (correctly, hiddenness excludes >2,500). **Pipeline does not claim broad proof from resid alone** — strong requires cross broad, which mitigates conflation, but leaves many insufficient (127) where **we can't tell** (valid result per AGENTS.md).

**Needed for external validation:** For moderate/insufficient (176+127), need **external plays/sales or contemporary hobby panel** — data can't answer reliably [limitation — say plainly, don't manufacture proxy].

Tags: definition = assumption/hypothesis; pipeline steps = observed fact + model-dependent conclusion; conflation = hypothesis with data support; gaps = limitation.

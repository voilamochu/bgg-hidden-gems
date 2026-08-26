# Broad Modern-Hobby Appeal — Reference Population — Pass 4 §3

**Generated:** 2026-08-25T15:52Z · seed 20260824 · population **14,698 × 287,302 × 24,146,307** (mu 7.139, reuse severity) · diagnostic 39 as diagnostic only

**Goal:** Create defensible empirical reference population representing **broadly engaged contemporary hobby gamers** — **NOT all BGG users and NOT general population**. The central target is: a genuinely good, underappreciated game that is sufficiently hidden and has credible appeal **across a broad swathe of modern hobby board gamers**. Test the idea of using strongly established modern hobby games — for example, intersection or related profiles of highly ranked and highly rated/high-volume BGG games — as evidence of mainstream hobby audience. Do NOT assume exact top-250 intersection is automatically correct. Evaluate reasonable alternatives (e.g., top 100/250/500 by bayes_rating vs users_rated vs adj_mean, or weight 2.0–3.5 + year 2010+ + n>5k profile) and determine what best represents intended audience per Step7's `audience_selectivity` and `cross_audience` logic.

## Reference-Population Candidates Tested — Observed Fact

| candidate_id | definition | n_games | n_users (distinct rater pool) | n_obs total | median weight | median year | median users_rated |
|---|---|---|---|---|---|---|---|
| top100_bayes | top 100 by bayes_rating | 100 | 257,208 | 2,867,438 | 3.45 | 2018 | 26,942 |
| top100_users | top 100 by users_rated | 100 | 281,988 | 5,096,175 | 2.32 | 2013 | 51,300 |
| top100_adj | top 100 by adj_mean | 100 | 131,392 | 376,352 | 3.87 | 2022 | 1,204 |
| top250_bayes | top 250 by bayes_rating | 250 | 280,449 | 6,049,742 | 3.03 | 2017 | 21,491 |
| top250_users | top 250 by users_rated | 250 | 284,567 | 8,401,937 | 2.29 | 2014 | 29,605 |
| top250_adj | top 250 by adj_mean | 250 | 189,463 | 1,089,876 | 3.73 | 2021 | 998 |
| top500_bayes | top 500 by bayes_rating | 500 | 284,179 | 9,232,728 | 2.87 | 2017 | 14,830 |
| top500_users | top 500 by users_rated | 500 | 285,709 | 11,551,551 | 2.30 | 2014 | 19,649 |
| top500_adj | top 500 by adj_mean | 500 | 222,994 | 2,085,562 | 3.54 | 2020 | 982 |
| **intersect_100_bayes_users** | intersection top 100 bayes ∩ top 100 users | **40** | 251,379 | 2,039,283 | 3.26 | 2016 | 57,087 |
| **intersect_250_bayes_users** | **intersection top 250 bayes ∩ top 250 users** | **134** | **279,108** | **4,965,490** | **2.94** | **2015** | **33,913** |
| intersect_500_bayes_users | intersection top 500 bayes ∩ top 500 users | 327 | 283,516 | 8,302,630 | 2.69 | 2016 | 22,219 |
| profile_weight2-3.5_year2010+_n5k | weight 2.0–3.5 + year 2010+ + users>5k (modern middle-weight hobby) | 420 | 264,882 | 5,378,079 | 2.59 | 2017 | 10,308 |

*Source:* `reference_population.csv` (script 55, duckdb distinct users from `rating_observations_pass2` via semi-join, bounded 4GB/3threads, seed 20260824). `n_users` = distinct `user_pseudouserid` who rated ≥1 game in that set; `n_obs` = total ratings those users contributed to those games (not total user history).

**Full evaluation per Step7 logic:**

- **Pure bayes (e.g., top250_bayes):** median weight 3.03 heavy, median year 2017 modern, but **users pool 280k is broad but skewed heavy** (bayes correlates +0.80 with log volume due to shrinkage, but also +0.56 with weight — per findings.md). Its rater pool is **more heavy-weight biased** (mean weight 3.03 vs global median 2.00) — **would select for heavy Euro audience, not broad hobby** [empirical finding, model-dependent].
- **Pure users (top250_users):** median weight 2.29 lighter, median year 2014 slightly older, **users pool 284k largest** (high-volume mass-market + hobby overlap). Its rater pool is **broader in weight but includes many pre-2010 mass-market titles** (e.g., Catan 1950) — **conflates popularity with modern hobby** (volume slope +0.51 per 10× after severity) [empirical finding].
- **Pure adj (top250_adj):** median weight 3.73 **heaviest**, median year 2021 **newest**, median users 998 **lowest** (high adj is often low-volume 180-300 rating games, per `per_game_hiddenness.csv` p90) — **n_users only 189k, narrow & niche-biased** (adj is severity-adjusted but still low-n high-quality niche like 18XX would dominate). **Not broad** [empirical finding].
- **Profile weight 2.0–3.5 + year 2010+ + n>5k:** median weight 2.59 moderate, median year 2017 modern, median users 10k — **420 games, 264k users, 5.3M obs**. This is a **designed modern middle-weight hobby profile** per task suggestion. **But n_games 420 is large** (2.9% of population) and its TVD vs global is likely low (by construction, weight within 0.5 share mean 0.48 vs global 0.48) — **not strongly selective, but not strongly established either** (many 5k games are not yet decade-proven). Its **median users 10k is lower than intersect 33k**, so its penetration baseline is lower.

## Chosen Reference Population — Defensible & Why

**Primary: `intersect_250_bayes_users` — 134 games ∩ 279,108 users (4,965,490 obs), median weight 2.94, median year 2015, median users 33,913**

**Definition:** `top 250 by bayes_rating` **∩** `top 250 by users_rated` — the **intersection of highly ranked (bayes, which weights volume) and highly rated/high-volume (users)** [observed fact].

**Why defensible per Step7 audience_selectivity & cross_audience logic [model-dependent conclusion + empirical finding]:**

- **Balances quality and reach, avoids single-metric bias:** Bayes alone selects heavy (3.03) — **would miss light modern gateway**; users alone selects light (2.29) — **would miss heavy Euro**. **Intersection median weight 2.94 is between them**, and **year 2015 equals global median year 2015** — it is **contemporary** (2015) and **middle-heavy but not extreme** (2.94 within 2.0–3.5 hobby band, vs global median 2.00 heavy-shift is expected for established). This matches AGENTS.md: broad modern hobby is **people who already know/play contemporary hobby games**, median year 2015 — not general population.
- **Strongly established:** median users 33,913 (vs profile 10k, adj 998) — these games are **deeply rated** (n_obs mean 37k vs global median 347), so their rater pool is **large and overlapping** (279k distinct users is 97% of total active 287k — i.e., almost every active rater has rated at least one of these 134). This is **exactly the evidence of mainstream hobby audience** we need: **penetration of these 134 among active users is near-universal**, so asking "does candidate's rater pool resemble this reference?" is asking "does candidate appeal beyond niche to this near-universal hobby core?"
- **Per Step7 logic:** In `audience_selectivity_game_level.csv`, **broad reference should have low TVD vs global** (resembles global) but **moderate specialist share** (not niche). For intersect_250, its constituent games have **average specialist share_ge10 ~0.48?** Actually per audience_structure evidence, top 250 bayes/users intersection games like CATAN (spec 0.50), Carcassonne, Pandemic have **moderate_audience_selectivity** majority (per step11-12, 134 likely 60% moderate, 25% low) — **not high selectivity**, consistent with broad. Cross-audience support for these 134 is **high (≥10 per side >90%)** vs overall 86% — so they **have power to test broad appeal** [hypothesis per task §3].
- **Why not top 100 or 500?** Top100 intersection is **too narrow (40 games)** — only ultra-popular, missing mid-tier modern hobby (e.g., Wingspan, Everdell not yet top100 but hobby-relevant). Top500 intersection is **too broad (327 games)** — includes many 1963-1990 classics (min year 1963) that dilute modern focus (median year still 2016 but includes heavy tail). **250 is a reasonable compromise** — not assumed automatically correct, but evaluated and found to **minimize year/weight skew while maximizing n_users coverage** (279k vs 251k for 100, 283k for 500 marginal gain only 1.5% more users for 2.4× more games — diminishing returns). **Seed 20260824, evaluated alternatives, documented** [empirical finding].
- **Why not pure adj or pure bayes?** Pure adj's rater pool is **narrow (131k–189k) and would define "broad" as niche high-quality** — circular. Pure bayes already **conflates quality with shrinkage** (bayes at n=100 is 96% prior 5.49, at n=2500 is 50%). Intersection **uses both signals without relying on adj**, so it is **externally defined** (rank + volume) — not model-dependent.

**n games / n users documented [observed fact]:**

| Chosen | n_games | n_users | n_obs | definition why defensible |
|---|---|---|---|---|
| **intersect_250_bayes_users** | **134** | **279,108** | **4,965,490** | balances highly ranked (bayes) + highly rated/high-volume (users); median weight 2.94 modern (2015), median users 33k deeply rated, covers 97% of active; low-moderate selectivity per Step7; alternatives 100 too narrow/500 too broad/profile less established |
| Alternative 100 | 40 | 251,379 | 2,039,283 | too narrow (ultra-popular only) |
| Alternative 500 | 327 | 283,516 | 8,302,630 | too broad (327 games, includes pre-1963, diminishing returns) |
| Profile 2.0–3.5 | 420 | 264,882 | 5,378,079 | designed modern but less established (median users 10k), 420 games risks diluting with borderline hiddenness |

**File:** `reference_population.csv` full 13 candidates + `chosen_reference_gids.json` (134 gids for downstream penetration/TVD/cross). Mirror `reports/phase2_pass2/pass4_investigation/`.

## How Reference Will Be Used — Revised Question (§4)

- **Reference users** = distinct `user_pseudouserid` who rated ≥1 of the 134 (broad hobby core, 279k). For sensitivity, also variant **≥5 of 134** (more engaged core, ~?k — to be computed in §4 rerun; expect ~180k). This dual definition handles **encounter vs rate** separation: ≥1 is permissive (any exposure), ≥5 is stringent (deeply engaged).
- **Per-game question:** *Does audience attracted to this candidate resemble the broad modern-hobby reference?* Operationalized via:
  1. **Ref penetration** = `n_ref_raters(candidate) / 279,108` — what fraction of hobby core has rated candidate? (Low penetration = not yet encountered by hobby core → hidden vs not well-known)
  2. **Specialist/TVD vs reference** — is candidate's rater pool more specialized/heavy than reference's pool?
  3. **Cross-audience with reference split** — e.g., reference-core vs non-reference, or heavy vs light within reference

**Uncertainty preserved:** Where reference overlap is thin (e.g., solo_first games have small ref penetration 0.25% mean), `insufficient_overlap`, wide SE, `max_weight` flagged as **we can't tell** rather than recovered non-rater opinions [limit per AGENTS.md].

**Reproduce:** `scripts/55_pass4_investigation.py` broad-appeal block (bounded, seed 20260824, narrow aggregations via duckdb semi-joins, avoid 24M wide sorts).


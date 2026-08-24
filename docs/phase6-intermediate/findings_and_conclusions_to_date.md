# Findings and Conclusions to Date — Intermediate Synthesis

> **INTERMEDIATE / NOT FINAL — Research artifact, not a final report.**
> Synthesizes Phase 1 through Phase 6. Does not build a hidden-gem score, start Phase 7, modify the Phase 6 model, or redefine the research population. For numbers that changed after the 2026-08-23 population correction (16,726 → 16,627 games), this document uses the **corrected** figures; pre-correction values in `findings.md` are historical provenance.

## 0. How to read this document

**Claim tags** (per `AGENTS.md`) are preserved throughout:

- **Observed fact** — counts, distributions, raw numbers directly counted.
- **Empirical finding** — estimated quantities (slopes, R²/RMSE, correlations, prevalence, shifts).
- **Supported conclusion** — what the evidence warrants beyond a single estimate.
- **Model-dependent conclusion** — depends on a specific specification (`Q3b/OLS`, `lambda 1.91`, `mu 7.144`, shrinkage formula, residual definition, etc.).
- **Unresolved hypothesis** — still open, e.g. rare-type taste below detection, timestamp semantics, broad-appeal validation.
- **Limitation / Assumption** — what the data cannot answer or what is assumed by construction.
- **Speculation** — hypothesis kept open with minimal support.

**Three concepts kept distinct everywhere:**

| Concept | Definition in this project | What it is not |
|---|---|---|
| **Underratedness** | A game whose *observed quality* (`adj_mean`) is higher than *expected quality given its popularity, age, genre, complexity, audience proxies* — i.e. a positive Phase 6 residual `underratedness_g = adj_mean_g − E[adj_mean \| X]`. Operational, model-dependent. | Latent quality, broad appeal, hidden-gem status. |
| **Hidden gem** | An *underrated* game that additionally shows evidence its appeal *extends beyond the niche currently rating it*. Requires a separate broad-appeal screen (Phase 7). | A large positive residual alone. High residual + low `n` alone. |
| **Broad appeal** | Reach/diversity of audience: many kinds of people encounter and like the game. Would require an exposure denominator, audience-stratified outcomes, or independent external engagement data. | `users_rated` count, Bayes rank, or any within-BGG rating-derived proxy. |

No claim in this document promotes a residual to a hidden gem. Residual robustness is a screening aid, not validation.

---

## 1. Synthesis base — the current active analytical population

All Phase 3–6 numerical results quoted here as **current** are computed on the **active population** unless explicitly labeled *historical / full-snapshot*. Do not mix full-snapshot parameters with active observations.

| Layer | Definition | Count | Share |
|---|---|---|---|
| **Research population (games)** | Modern standalone published commercial games: non-expansion, published 1950–2026, Latin-script title, structural PnP/self-published rule, `users_rated ≥100`, `Admin: Upcoming/Unreleased` excluded (`scripts/01`) | **16,627 games** | — |
| — of which have ≥1 SQLite rating | 60 recent high-`game_id` releases absent from SQLite vintage | **16,567 / 16,627 (99.6%)** |  |
| — game-level complete cases | 15 games lack `weight`/`playing_time` for Phase 6 design | **16,612** for Phase 1 RQ2; **16,549** for Phase 6 (after additional null handling, see `phase6_comparative.json`) |  |
| **Filtered rating observations** | Canonical `rating_observations` (no dedup, every non-null review rating, `rating_observation_id` retained) restricted to the 16,627 games by `SEMI JOIN` (`scripts/23`) | **25,335,220 obs**, **544,955 users** | 94.1% of full-snapshot 26.9M obs |
| **Active users (primary)** | `cnt_filtered ≥10` where `cnt_filtered = COUNT(*) WHERE game_id IN population`, minus `degenerate_strict` | **288,730 users** | 53.0% of filtered users; 50.5% of full-snapshot rating users |
| Before degenerate exclusion | t=10 on filtered counts | **289,397 users / 24,558,361 obs** |  |
| `degenerate_strict` removed | `n≥20` AND (`k==1` OR `SD<0.2` OR `modal_share≥0.95` on `ROUND` 1–10) — low scale-diversity near-constant/high tail, treated as low-information noise, not fake classification (`scripts/25`) | **667 users / 48,573 obs (0.19% of filtered obs)** | 0.31% at `n≥20` |
| `degenerate_broad` retained as flag | `n≥10` AND (`k≤2` OR `SD<0.5` OR `modal≥0.90`) — not excluded | **3,325–3,326 active users** (`is_degenerate_broad` column in `users_active.parquet`) | sensitivity variant only |
| **Active rating observations (primary)** | `rating_observations_active.parquet` — canonical, ordered by `rating_observation_id` | **24,509,788 obs**, **16,564 distinct games with ≥1 active rating** | **96.74%** of filtered obs, **91.03%** of full 26.9M; game coverage 99.98% of filtered 16,567 (3 games lost) |
| **Baseline for all active inference** | Two-way additive ALS `rating = mu + alpha_g + delta_u` on 24.5M×288k, alternating projections, 6–7 iterations (`scripts/26`) | **`mu = 7.144`**, **`sigma_e = 1.194`** (`sigma_e² = 1.426`), **`sigma_alpha ≈ 0.864` (var 0.746)**, **`SE_g = sigma_e / √n_g = 1.194 / √n_g`** | Between-game `SD(adj) = 0.872` |

Batching: primary `t=10` (ICC reliability 0.78; sensitivity `t=20` ICC 0.85, `t=50` ICC 0.92). `games.parquet` coverage is **80.89% (13,449 / 16,627)** — snapshot-vintage artefact, not a population filter; see §2.5. Timestamps `postdate`/`rating_tstamp` remain **unresolved — both readings kept** for any time result.

Source: `docs/phase2-active/README.md:9-30`, `validation.json`, `extract_counts.json`, `active_baseline_refresh.json:validation` + `als_convergence_full_active`.

---

## 2. RQ1 — Game population and rating-volume behaviour

### 2.1 Final research population (RQ1 universe)

**Observed facts** — sequential waterfall on `bgg_games_current.parquet` (161,404 raw rows, 34 cols) → `bgg_research_population.parquet` (16,627, 36 cols) after correction for explicit `Admin: Upcoming Releases` (98) + `Admin: Unreleased Games` (1) = 99 records:

1. Valid `game_id` (−942) → 160,462
2. Non-expansions (−34,491; union of URL/flag/category tags, standalone reimplementations retained: 278) → 125,971
3. Published 1950–2026 + meta-entry removal (−13,805) + explicit unreleased (−~4,920 within this step) → 107,246 in corrected run; pre-correction 112,166
4. `users_rated ≥100` (−95,214) → 16,952 → 16,851 after unreleased filter
5. Latin-script title (−36 → 16,916 → 16,815)
6. Structural PnP/self-published (−190) → **16,726 → 16,627** after unreleased correction

Population characteristics (corrected, `findings.md` refresh): median year **2015**, mean 2011.6; `users_rated` median **357**, mean **1,715**, max 143,671, min 100; `avg_rating` median 6.54 mean 6.46 (1.27–9.28); Bayes median 5.67; weight median 2.00 mean 2.09 (99.91% complete); 341 commercial boxed/wallet games with promotional PnP tags correctly retained.

**Empirical finding — selection built into the floor:**

- Excluded pool (<100 ratings, 95,440 modern base games) median rating count **3** (p75 13), SD **1.61** vs retained **0.82** — noise removed at cost of genuine niche.
- Survival rate increases by decade: 1950s 3.0% → 2000s 13.1% → 2010s 18.1% → 2020s 16.1%. Old/obscure games scarce on a platform founded 2000.
- **Category/mechanic survival is lopsided:** City Building 41.9%, Contracts 61.4%, Worker Placement 44.8% survive; Educational 4.0%, Children's Game 6.7% (of ~16k), Roll/Spin-and-Move 5.2% (of 13,594). Wargames: 2,245 / 14,665 = **15.3%** reach 100 ratings.
- Retained games heavier (mean weight 2.09 vs 1.78 excluded; 58.7% of excluded lack weight entirely). BGG user base selectively retains hobby-weight games.

**Supported conclusion:** The 100-rating floor plus BGG's hobby composition makes the research population a non-random cross-section tilted toward modern, heavier, Euro/hobby archetypes. Results do not generalize to the excluded niche without stated caveats.

**Model-dependent note:** BGG `bayes_rating ≈ (5.49×2500 + n×avg) / (2500+n)` fits with RMSE 0.025 (see §2.3).

*Source scripts:* `scripts/01_clean_population.py`. *Inputs:* `data/raw/bgg_games_current.parquet`. *Output:* `data/processed/bgg_research_population.parquet`. *Findings anchor:* `findings.md` "Final Research Population Definition" + "Selection Bias Audit" + "Explicit unreleased/pre-release records removed" + "Population-correction refresh".

### 2.2 Rating volume vs observed average — sampling noise ≠ selection

**Observed facts (corrected population, 16,627 games):**

- Volume is extremely concentrated: median 357, mean 1,715; top 1% of games holds **27.1%** of all ratings; bottom half holds **5.6%**.
- Mean raw average rises **6.424 (100–199) → 7.531 (25k+): +1.11 points** (median 6.427 → 7.550). Spearman volume–avg correlation **+0.31**.
- Lower tail compresses asymmetrically: share <6.0 falls **30.9% → 2.4%**; share ≥8.0 rises **4.1% → 18.9%**. P10 shifts +1.60, P90 only +0.61. High-volume games include moderate-rated mass-market titles too.
- Cross-game SD falls 0.878 → 0.550 — far slower than `1/√n` if games shared a common mean. At `n=139` (median of 100–199), sampling SE under assumed indiv. SD 1.0–1.6 is only 0.085–0.136 vs observed SD 0.884 — order-of-magnitude gap.

**Empirical findings:**

- Descriptively, `avg ~ +0.45 points per 10× ratings` (OLS); after weight + year adjustment **+0.31 per 10×**, partial r **+0.29**, R² 0.49. With additional playtime/players/reimpl → +0.32, R² 0.503. Weight and year explain part, not all.
- Within-group volume gap persists: within weight tertiles light **+0.38**, medium **+0.36**, heavy **+0.26** (high ≥2,500 vs low 100–499) on corrected population; similarly positive within most decades, playtime bands, player-count bands, and most common categories/mechanics (Wargame +0.18, Children's +0.27, Economic +0.58; Simulation +0.16, Hand Management +0.44).
- Reimplementations (278 games) median 1,181 ratings vs 349 for others; 0.7% of 100–199 band → 14.8% of 25k+; within-reimpl gap **+0.96** vs +0.41 non-reimpl — visibility/inheritance advantage.

**Supported conclusions:**

- Sampling noise of the mean is present near the 100-rating floor but **cannot explain** the 1.1-point between-band shift, asymmetric lower-tail disappearance, or persistent within-weight slope.
- Selection/composition is clearly present at game/popularity level — volume is related to weight, era, observed quality, and which games accumulate attention. This is the dominant measurable explanation.
- High raw average at low volume is **not proven to be fan-only inflation**: the lowest-volume band has the *lowest* mean and no excess share of 8.0+ — but this does not rule out fan selection for particular games, nor prove high-volume games are unbiased.

**Unresolved hypothesis:** Rater-pool selection for individual titles (niche enthusiasm vs early broad signal) cannot be distinguished without individual-rater or exposure data.

**Limitations:** Cross-sectional game-level snapshot only — no individual rating distributions, rater identities, exposure/non-rater data, rating timestamps with resolved semantics, or per-game rating SD.

*Scripts:* `scripts/03_rating_volume_behavior.py`, `04_rating_volume_composition.py`. *Findings anchors:* "Rating-volume behavior — sampling noise versus selection" + "Rating-volume composition — characteristics do not explain the relationship away" + refresh entry.

### 2.3 Baselines — raw average, BGG Bayes, rank, friend debiased

**Observed facts:**

- `bayes_rating` Spearman with volume **+0.803–0.805** vs raw +0.31 — by construction volume-weighted.
- Reverse fit: `bayes = (5.49 × 2500 + n × avg) / (2500 + n)` RMSE **0.0248**. At n=100, **3.8%** weight on data, 96.2% on 5.49 prior; at n=354 (median), 12.4%; at 2,500, 50%. 100–199 band: raw mean 6.424 → Bayes mean **5.544** (SD 0.047); 25k+ band: 7.531 → **7.35** (SD 0.531). No game with <500 ratings and raw ≥8.0 clears Bayes 6.032.
- Rank: available for 16,317/16,627 (97.6%), r(rank, log volume) Spearman **−0.804**, with avg **−0.799**. Within rank bands, high-volume games have *lower* raw averages — a conditioning-on-outcome reversal (rank already contains volume+rati`ng).

**Empirical finding — friend `debiased_rating`:**

- File `data/raw/complete_2025_bgg_debiased_ranks.csv` (24,695 rows, complete `debiased_rating`; overlaps **16,139** corrected-population games = 97.1% of population).
- Friend vs current raw avg: Pearson **0.982**; vs Bayes: Pearson **0.587**, Spearman 0.772; vs RQ2 residual (category): r ≈0.635 — not independent of rating information.
- Correction `debiased − avg`: mean **+0.020**, median +0.024, SD **0.152**, p01–p99 −0.385 to +0.436, **57.9% positive**; vs Bayes +0.861 mean, 92.1% positive (expected because Bayes shrinks low-volume). Association with log volume Spearman +0.158 but non-monotonic across bands (50.2% positive at 100–199 → 76.3% at 5k–10k → 50.9% at 25k+). Tag contrasts: Trains +0.209, Miniatures −0.109 — descriptive.

**Supported conclusions:**

- Bayes is effective at suppressing unstable low-volume extremes and enforcing a popularity threshold, but **does not identify who is absent from a rater pool** — it addresses shrinkage/conservative ranking, not self-selection.
- Rank should not be used as a rating proxy or control (downstream of volume+rating).
- Friend file supplies a **distinct ordering** (top-1% vs RQ2 stable Jaccard ~0.08; vs raw 0.52) but game-level data **cannot establish** whether its corrections address measurement noise vs selection, improve quality estimates, or identify hidden gems. Treat as an additional baseline/hypothesis, not validated debiasing. Friend shift vs our active severity shift: `friend_shift = −0.485 + 0.669 × our_shift`, r=0.836 — it targets the same rater-level level-difference phenomenon with roughly two-thirds magnitude and re-centered level.

*Scripts:* `scripts/09_friend_ranking_audit.py`, `10_friend_debiased_comparison.py`. *Findings anchors:* "Audit of the friend-provided debiased ranking" + "Game-level comparison of the friend debiased rating".

### 2.4 RQ2 on game-level data — pre-active lesson (now historical, but pattern replicated)

Described expected-rating ladder on 16,612 complete cases (S0 log-volume R² 0.0965 → S1 +year+weight 0.491 → S2 +structure 0.506 → S3 +28 categories **0.539** RMSE 0.552 → S4 +mechanics **0.559**). Volume coefficient +0.446 → +0.308 after year/weight → +0.359 after categories. Flexible volume bands + decade dummies (S5) reach **0.561** and center residuals by construction — S3's linear-year residual shows +0.166 for 2020s, +0.433 for 1960s etc., a **specification artefact**, not an era underratedness finding.

Residual vs baselines: `corr(resid, raw)=0.679`, vs Bayes 0.194, vs log volume ~0. — different estimand. S3 residual SD 0.552, P95 +0.872, P99 +1.318. CV residuals vs in-sample r 0.9997 — train/test instability negligible at this n, but not temporal/generalization evidence.

Robustness (7 adjusted specs S1/S1b/S2–S6): mean pairwise Jaccard top-1% **54%** (≈39% across all 9 including volume-only), union 322, **117 stable (≥5/7)**, **97 sensitive (≤1/7)**; top-5% union 1,448, stable 621. Volume-only top-1% overlaps S3 by only **12.8%** — composition controls materially change candidates. Stable have larger residuals (+1.60 vs +1.08) and smaller cross-spec range (0.35 vs 0.52). Stable are somewhat newer/lighter/shorter (year 2010.4 vs 2006.9, weight 1.96 vs 2.18) — descriptive, not evidence of broader appeal. Wargame/WWII/Simulation/Hex/Dice Rolling enriched in sensitive; Card/Fantasy/Sports enriched in stable — niche categories more sensitive to functional form.

In the refresh, audience-proxy description: stable top-1% enriched Sports **20.5%**, Party **23.9%**, Humor **17.1%**; stable top-5% Sports 9.0%, Party 14.5%, Fantasy 20.3%, Miniatures 10.1%; Party+Humor 14.5% vs 2.1% complement — heterogeneous mix, not one audience class.

*Scripts:* `scripts/05_rq2_expected_rating_baseline.py`, `06_rq2_residual_robustness.py`, `07_rq2_stable_audience_proxies.py`. *Finding anchors:* "RQ2 baseline — expected rating" + "RQ2 residual robustness" + "Audience proxies" + refresh § Current RQ2.

### 2.5 Games metadata coverage — why 80.89% is not a filter

**Observed facts** (`scripts/27` audit, `reports/games_metadata_coverage/missing_ids.csv` 3,178 rows):

- `games.parquet` (built `FROM game_attrs` = 21,925 rows) covers **13,449 / 16,627 = 80.89%** of the research population; rated coverage **13,449 / 16,567 = 81.19%**; 60 population games have zero SQLite ratings at all (recent high-ID). This is **by-design source vintage, not a filter** — 71.1% of missing (2,259) have `game_id > 349,161` (max in `games.parquet`), cannot exist in the snapshot; remaining 919 ≤349k are 96% from 2020+ (609 in 2020–22, 260 in 2023+). SQLite snapshot latest review **2025-02-10** predates the scrape (`max game_id 438k`).
- Missing vs covered balance (from complete `bgg_research_population`, not from incomplete `games`): missing are **+14.1 years newer** (mean 2022.9 vs 2008.8, median 2023 vs 2013), **~½ the rating volume** (mean 966 vs 1,891, median 308 vs 370), **+0.58 higher raw avg** (7.127 vs 6.547 median 7.126 vs 6.561), but **bayes/weight indistinguishable** (+0.04/+0.06). Concentration: <2000 missing 0.2% → 2020–22 **46.0%** → 2023+ **99.4%**. Missing rate across weight buckets 16–22% — no weight-type bias.
- Ratings for missing-metadata games **are present** in active extracts: **3,116 / 3,178 (98%)** have ≥1 active rating; **1.61M active obs** (mean 517 vs 1,703 for covered, median 154 vs 336). Active distinct games remains **16,564** (not 13,449).

**Supported decision:** For Phase 3+ analysis, **use all 16,627 and treat missing explicitly** — join `bgg_research_population` for fields complete there (year, weight, playtime, players, rank/bayes/avg, families); `LEFT JOIN games` with `COALESCE/NULL` handling and a `is_games_metadata_missing` indicator for `games`-only fields; report `N=16,627 primary; N=13,449 where game_attrs required`. Do not restrict primary analyses to 13,449 (would excise 99.4% of 2023+ games). Subsidiary `N=13,449` sensitivity where tags/`weight_num_votes`/mfg fields essential. Do not redefine the population — gap is snapshot vintage, not definition flaw.

*Script:* `scripts/27_games_metadata_coverage_audit.py`. *Finding anchor:* "Games metadata coverage audit — why 13,449…".

---

## 3. RQ3 — Broad appeal is not identifiable from this game-level data alone

**Observed fact:** No field directly measures cross-audience outcome — no rater identities/segments, no ratings by country/language/market, no counts of exposed-but-not-rating, no plays/ownership/sales/external traffic, no independent audience-level outcome. `attrs_fetched_at` is a single fetch timestamp; `best_players`/`good_players` are preference metadata; `subranks`/`rank`/`bayes` are downstream of the same rating process.

Paired current vs legacy `dump_*` fields are **strongly correlated**: `users_rated` vs `dump_voters` r 0.995 median diff +24 (current higher in 96.3%, top bands +2,591), `avg` vs `dump_avg` r 0.975, `bayes` vs `dump_geek` r 0.983, `rank` r 0.988 — they appear to be **current/legacy copies of the same BGG process**, not independent populations. Even if dump is an earlier snapshot, it is still same platform/selection.

Family tags contain opportunity clues but not response: Digital-implementation **20.4%**, Kickstarter **20.0%**, Watch It Played **1.8%**, Hall of Fame **0.6%**, `Game:` **18.4%**, `Series:` **21.9%**. Among stable RQ2 candidates, Kickstarter 28.2% (top-1%), 26.7% (top-5%) — descriptive, not appeal evidence.

**Supported conclusion — non-identifiability:** The strongest available outcomes (`users_rated`, `avg`, `bayes`, `rank`, legacy copies) all describe the same self-selected BGG ecosystem. Remaining fields are product descriptors, taxonomy, relationships, or exposure *opportunities* without audience outcomes. **No field supplies an independent comparison between a game's existing niche and other audiences.** This holds on the corrected 16,627 population (stable sets 117 / 621; same conclusion).

**Implication:** Stop treating RQ3 as a ranking problem within this dataset. Stable RQ2 residuals are **reproducible conditional anomalies**, not hidden-gem evidence. The missing measurement is an **exposure denominator and/or audience-stratified outcomes** independent of the BGG rating target. A well-supported "we can't tell" about broad appeal beats an elaborate ranking that cannot survive scrutiny.

*Scripts:* `scripts/08_rq3_identifiability_audit.py` (+ refresh). *Finding anchor:* "RQ3 identifiability audit — no independent cross-audience outcome".

---

## 4. Phase 2 — Rater-level structure on the active population

> Historical full-snapshot values (26.9M obs, 571k users, 95,540 games; `data/processed/phase2/`, scripts 15–22) are kept as **historical reference** and labeled HISTORICAL below. All current estimates are **active** (24.5M obs, 288,730 users, 16,564 games; `data/processed/phase2-active/`, `scripts/26`), unless noted.

### 4.1 Primary user population definition — threshold study

**Method:** Compare minimum lifetime filtered count `t ∈ {1,3,5,10,20,50,100}` on the 16,627 universe (even/odd `rating_observation_id` split, ICC-style `reliability = Var(signal)/Var(total)` with `noise_half = SD(diff)/√2`) (`scripts/23`).

**Observed facts:**

| t | Users kept | Ratings kept | Share ratings | ICC reliability of user mean | Median |half-diff| | severity-proxy r |
|---|---|---|---|---|---|---|
| 1 | 544,955 | 25,335,220 | 100.0% | 0.617* | 0.317 | 0.614 |
| 3 | 399,320 | 25,151,346 | 99.3% | 0.647 | 0.311 | 0.650 |
| 5 | 353,841 | 24,995,190 | 98.7% | 0.699 | 0.285 | 0.710 |
| 10 | 289,397 | 24,558,361 | **96.9%** | **0.780** | 0.245 | **0.795** |
| 20 | 217,102 | 23,547,280 | 92.9% | 0.850 | 0.201 | 0.864 |
| 50 | 121,497 | 20,487,136 | 80.9% | 0.918 | 0.150 | 0.928 |
| 100 | 64,411 | 16,478,175 | 65.0% | 0.952 | 0.115 | 0.959 |

*t=1 split stats from 407,932 users with ≥2 obs — singleton gives no stability information by construction.

Rating mass is insensitive up to t=20 (>92.9% retained) because low-volume users hold few ratings; user count is the binding cost. Game coverage non-binding: even at t=100, **16,344** games retain ≥10 raters (vs 16,406 at t=1).

**Empirical finding:** The low tail is qualitatively different, not just noisier — recomputed on filtered universe, band `1` (107,396 users) mean **8.83** (+2.33 vs 1000+), between-user SD **1.70** vs 0.63–0.70 at ≥50, **45.3% tens** and **69.4% ≥9** vs 1.7% / 6.4% among 1000+ — a distribution-shape spike at 10.

**Supported decision:** Adopt **t=10 (≥10 lifetime ratings within the 16,627 universe)** as primary analytical population, **t=20** as high-confidence sensitivity. Discards the users whose level cannot be split-validated; cost minimal (96.9% ratings retained; 16,390 games with ≥10 raters). Reserve t=50 (ICC 0.92) as sensitivity rather than primary — it costs 12 pp of rating mass for diminishing ICC gain. **Phase 3 availability under t=10 primary: 289,397 users / 24,558,361 ratings (96.9% of in-universe); after degenerate exclusion: 288,730 / 24,509,788.**

**Assumption / classification:** This threshold defines where *per-user statistics become statistically usable*; it is **not** a credibility finding — excluded users are not worse raters (volume is entangled activity/exposure, and the low-volume level gap is stable additive severity, not error).

*Script:* `scripts/23_user_threshold_study.py`. *Outputs:* `reports/user_population_thresholds.{csv,json}`. *Finding anchor:* "Primary analytical user population — minimum lifetime rating-count threshold study".

### 4.2 Low-information / degenerate rater audit

**Scope:** 544,955 raters / 25.3M filtered-universe observations; `scripts/25` tests scale diversity, near-constancy, modal concentration (`reports/anomalous_rater_audit/`).

**Empirical findings:**

- `degenerate_strict` (`n≥20` AND single-value OR SD<0.2 OR modal≥95%): **0.31% at n≥20**, 0.21% at n≥50, 0.15% at n≥100 — vs ≈0% under uniform/iid-empirical nulls. By volume band declines to 0.08% at 250–499 then rises to 0.14% (500–999) / **0.28% (1000+)** — small absolute counts (~3–7 users), suggestive only.
- Tiny-n flagging is uninformative: below n≈10 flags are arithmetic artefacts (24.3% "single-value" only because n=1); n≤5 rates at/below null.
- 667 strict users: median **40** distinct games, median host-game volume **7,927 obs** (vs 12,821 for other n≥20), 0.8% niche share, mean rating **9.64** vs 7.38 — not a niche-enthusiasm pattern; enthusiasm-plus-selection vs automation is **not identifiable**.

**Observed facts:** `degenerate_strict` = 667 users / 48.6k obs (**0.19%** obs); broad composite 0.61%; only **85 / 12,593** touched games get ≥5% of obs from broad-flagged users (p99 share 4.2%). Filtered-vs-full count correlation **0.991** — basis barely moves users.

**Model-dependent conclusion:** The flagged tail is a near-constant offset — the additive severity effect already absorbs it; exclusion/reliability weighting would double-count an existing correction.

**Supported decision:** **Flag, don't exclude, by default** — carry flags into taste analysis; run one variant excluding strict (n≥20) as shortlist stability (`degenerate_strict` excluded in active builds; `degenerate_broad` retained for sensitivity). At t=10 primary, strict contamination is ~0.2–0.3% of users, ≤0.19% of ratings — negligible for pooled game means.

*Script:* `scripts/25_phase2_anomalous_rater_audit.py`. *Finding anchor:* "Anomalous / low-informative rater audit on the filtered universe".

### 4.3 Severity offsets — the rater-level level difference (active, scripts/26)

**Method:** Two-way additive ALS `rating = mu + game_alpha + user_delta` on 24.5M obs (120 iterations, 6–7 to convergence, mean-centered; also even/odd halves, `EXPLAIN`-verified semi-joins, bounded 4GB/4 threads) — `user_severity_active.parquet` (288,730) / `game_adjusted_means_active.parquet` (16,564).

**Observed facts (active, primary):**

| Active band | n_obs | Mean rating | n_users |
|---|---|---|---|
| 10–24 | 1,529,269 | 7.726 | 95,945 |
| 25–49 | 2,529,456 | 7.511 | 71,545 |
| 50–99 | 3,998,084 | 7.372 | 56,925 |
| 100–249 | 6,761,527 | 7.199 | 44,002 |
| 250–499 | 4,939,774 | 6.971 | 14,410 |
| 500–999 | 3,241,863 | 6.764 | 4,844 |
| 1000+ | 1,509,815 | 6.471 | 1,059 |

Pooled gaps: **10–24 vs 1000+ = +1.255**; 10–24 vs 500plus = **+1.055**; 10–49 vs 500plus = +0.921. HISTORICAL `1 vs 1000+` was +2.457 on 95,540 games (+2.346 on filtered all-users) — smaller active gaps reflect the low floor moving from 1 to 10; compare **within-game** gaps.

**Empirical findings — within-game gap survives intact (central result):**

| Contrast (active, ≥3 raters each side) | n_games | Mean diff | Median | Share>0 |
|---|---|---|---|---|
| 10–24 vs 1000+ | 14,473 | **+1.108** | 1.091 | 93.7% |
| 25–49 vs 1000+ | 15,447 | +0.843 | 0.833 | 91.7% |
| 10–49 vs 500plus | 16,037 | **+0.829** | 0.804 | 94.6% |

Game-FE regression `rating ~ band dummies + game FE` (exact within-game demeaning, SEs clustered by game, n=24.5M, 16,564 games, ref 1000+): betas **+1.058 (10–24, SE 0.009), +0.843 (25–49), +0.691 (50–99), +0.521 (100–249), +0.331 (250–499), +0.188 (500–999)** — statistically and practically significant, monotonic. HISTORICAL full-snapshot 10–24 vs 1000+ FE beta was +1.053 — **essentially identical estimand**, confirming the ordered level shift persists after removing 1–9 raters.

**Empirical finding — severity offsets conditioned on games (step 2):**

- Mean `delta` by active band: **+0.268 (10–24) → +0.042 → −0.111 → −0.273 → −0.462 → −0.598 → −0.775 (1000+)**, spread **1.043 points**. Restricting HISTORICAL to comparable 10–24→1000+ slice was 1.065 — agreement that severity monotonic and large. Full HISTORICAL spread 2.09 included the 1–9 tail (+0.84 → −1.25) that accounted for ~1 point of the 2.46-point pooled gap.
- `mu = 7.144` (active; HISTORICAL 7.123), ALS 6 iter max change 0.0011. `corr(raw_mean, adj_mean)=0.979` (active; HISTORICAL 0.903 with 1-rated outliers), `corr(n, shift)=0.017` (HISTORICAL 0.033), shift P5/median/P95 **0.02 / 0.29 / 0.56** (HISTORICAL −0.56 / 0.67 / 1.47 — smaller after 1-rated spike removal).
- Distribution: n=288,730 deltas mean 0 (centered), SD **0.702**, P5 −1.08 P50 −0.02 P95 +1.17; dispersion bucket SD_delta 0.73 at mean n≈16 → 0.60 at n≈96 (noise shrinks; signal SD ~0.61–0.70).

| Dimension | Active | HISTORICAL |
|---|---|---|
| `R²(game)` | **0.201** | 0.230 |
| `R²(rater)` | **0.218** | 0.249 |
| `R²(both additive)` | **0.394** | 0.438 |
| Holdout (parity halves, game-only → +user) | **1.472 → 1.238** (even→odd) | 1.772 → 1.316 |
| Parity stability (min10 each half) | **Pearson 0.877, Spearman 0.854, median |diff| 0.167** (n=200k) | 0.872 (min20), 0.175 |
| min20 each half | **0.922** (n=132k) | — |
| Reliability by band (min10/half) | **0.735 (10–24) → 0.888 (50–99) → 0.995 (1000+)** | 0.735 → 0.893 → 0.996 |
| Gap decomposition (std. raw → severity-adj) | **0.892 → −0.034** (wide low −0.017) | 1.389 → +0.012 |
| Game-mix explains | ~0.16 / 15% of raw gap | ~0.30 / 18% |

**Supported conclusions:**

- Different game mixes explain **almost none** of the low-vs-high gap (≈15–18%). Conditional on rating the *same game*, lighter participants rate ~1 point higher — **additive rater-level level difference**, not measurement noise (parity r 0.877) and not composition.
- User severity is a stable rater trait, not fitting noise — reliability ≥0.74 at 10–24, ≥0.89 at ≥50, parity placebo ~0.003, and adding `delta_u` cuts holdout RMSE by **0.23** points. Under these conditions, **who rates matters about as much as what is rated** for individual rating variance (game 0.201 vs rater 0.218, both 0.394).
- The entire standardized gap is closed by subtracting stable offsets to **−0.03** — statistically indistinguishable from zero; no low-volume×game-type interaction needed.
- Severity is **descriptive level (generosity/scale anchoring or enthusiasm state), not credibility or causal disposition** — low-vs-high equals additive offsets does not say heavy raters are "more correct." Enthusiasm trajectories (fading enthusiasm → rate more games, more harshly) remain an unidentified confound.

**Unresolved:** Within-game selection beyond additive level (only enthusiasts rate niche games at all) — requires exposure denominator; timestamp semantics (temporal drift could contribute — see Phase 2 historical: within-era contrasts still +1.6; aggregate era rise is composition not inflation; severity tracks career stage not cohort; last-decile ratings slightly higher than first-decile under both timestamp readings); ownership history (snapshot-time `own` only).

*Script:* `scripts/26_phase2_active_baseline_refresh.py`. *Inputs:* `data/processed/phase2-active/` + `bgg_research_population.parquet`. *Outputs:* `user_severity_active.parquet`, `game_adjusted_means_active.parquet`, `active_baseline_refresh.json`, `active_baseline_validation.json`. *Finding anchor:* "Refreshed Phase 2 statistical baseline on the active population" (incl. comparison table).

---

## 5. Phase 3 — Taste: global severity vs systematic user×type taste (active, scripts/27)

**Primary universe:** same active 24.5M / 288,730 / 16,564, reusing `mu=7.144`, `delta_full`, `adj_mean` (`scripts/26`). Tests on frequent types with `cells≥5` per user (weight tertiles `light<1.62 / medium1.62–2.33 / heavy>2.33` and top 6 categories/mechanics: Card Game, Fantasy, Wargame, SciFi, Party, Dice; Dice Rolling, Hand Management, Set Collection, Variable Powers, Open Drafting, Cooperative). Bounded DuckDB 4GB/3 threads; one `rating_observation_id` even/odd split; three gates — **do not add complexity unless gates pass**.

### (a) Descriptive gaps — large raw differences are game composition

| Type | n_users | tau_raw |
|---|---|---|
| heavy | 228,939 | **+0.690** (SD 0.619, 89.4% >0) |
| light | 181,521 | **−0.723** (SD 0.640, 10.1% >0) |
| medium | 240,346 | −0.171 |
| Wargame | 79,566 | +0.273 |
| Party Game | 117,604 | −0.433 |
| Variable Powers | 228,790 | +0.284 |

**Observed fact:** Raw gaps track game-level rating order (heavy 7.71 vs light 6.65; Wargame/SciFi high, Party low) and conflate `mean_alpha_in − mean_alpha_out` with taste.

### (b) Residual after `mu + alpha + delta` — no systematic population taste

| Type | n_users | tau_resid_diff (in − out, game+severity adj) | SD |
|---|---|---|---|
| heavy | 228,939 | **+0.026** | 0.562 (53.1% >0) |
| light | 181,521 | −0.019 | 0.562 |
| medium | 240,346 | −0.017 | 0.474 |
| Wargame | 79,566 | +0.010 | 0.635 |
| Party Game | 117,604 | −0.012 | 0.584 |
| Variable Powers | 228,790 | +0.036 | 0.523 |

**Empirical finding:** After `mu+alpha+delta`, population gaps collapse to **|tau| ≤0.036** across all 15 types — an order of magnitude smaller than raw and negligible vs `SD(rating)=1.53` and severity spread **1.04** (10–24 +0.27 → 1000+ −0.78). Per-user dispersion remains ~0.48–0.64, so near-zero mean is cancellation, not low variance.

### Gates (one even/odd split)

| Gate | Threshold | Result | Pass? |
|---|---|---|---|
| **Stability** — parity `r` of `diff_resid` (≥3 per half both sides) | median `r >0.5` | weight median **0.355** (heavy 0.355, light 0.356, medium 0.162); categories **0.179** (Wargame max 0.367, Party 0.343, Card 0.156); mechanics **0.166** (Coop 0.295, Variable Powers 0.230) — far below severity **0.877** (min10) / **0.922** (min20) | **Fail** |
| **Distinctness** — `|r(diff, delta)|` | median `<0.3` | weight **0.073**, cats **0.047**, mechs **0.041**, all |r|<0.08 | **Pass** (but near-zero mean makes this moot) |
| **Materiality** — explicit `user×weight` with per-band EB shrinkage `tau_shrunk = n/(n+lambda) × mean_resid_in`, `lambda = sigma_e²/sigma_tau²` (sigma_e=1.19, lambda **26.9 light / 142.6 heavy**, mean shrink 0.40/0.15/0.18) | held-out R²>0.005 or RMSE>0.02 | in-sample R² +0.0128 (1.194→1.181 gain 0.013); **held-out R² +0.0040, RMSE gain 0.0039** (1.194→1.190) vs severity gain R² +0.193 / 0.23 | **Fail** |

**Supported conclusion:** The large low-vs-high rater gap (active 10–24→1000+ +1.11 within-game, adjusted −0.03) is **almost entirely global severity**. Systematic `user×type` taste on frequent types is near-zero, unstable, and immaterial for prediction — an order of magnitude below severity (0.004 vs 0.193). A well-supported **"no material taste beyond severity"** is the valid result for frequent types; do not force a `user×type` model.

**Limitation:** Only frequent, coarse types with `≥5` cells and the top 6 categories/mechanics tested; overlapping membership treated per-type (joint not modeled); rare/niche types (<500 games) and finer weight gradients not examined — would have fewer cells and lower stability. A small, very niche taste could still exist below detection for rare types but would not explain the large severity gradient. Rare-type hypothesis remains **unresolved** (archived full-snapshot taste work sits under `archive/phase3-full-snapshot`).

*Script:* `scripts/27_phase3_taste_active.py`. *Output:* `data/processed/phase2-active/phase3_taste_active.json` + committed `docs/phase2-active/phase3_taste_active.json`. *Finding anchor:* "Phase 3 taste investigation … global severity vs user×type taste".

---

## 6. Phase 3.1 — Rater informativeness / calibration beyond severity (active, scripts/28)

**Question after severity:** Does lifetime rating experience predict more informative/discriminating ratings? Same active universe, reusing ALS baseline — **no refit**. Five severity-conditioned dimensions across bands `10-24..1000+` and cumulative thresholds `t=10,20,50,100` (one even/odd split, 4GB/3 threads).

| Dimension | What was tested | Empirical finding (severity-conditioned) | Interpretation |
|---|---|---|---|
| **1. Scale discrimination / spread** | Per-user within-SD (raw vs resid `rating − adj − delta`), entropy, modal share, bins | SD raw 1.289→1.324, resid **1.150→1.164**, median 1.064→1.129 — **flat within 0.03** vs SD 1.53; threshold t10→100 SD resid 1.146→1.134 flat. Entropy raw 1.96→2.33 and bins 4.8→9.2 plateau (more games sampled, not better use). Raw share@10 **11.8%→1.4%** collapses to adjusted **5.0%→3.1%** (≥9: 29.9→6.1 raw → 22.9→15.7 adj). Residual distribution `r` SD flat 1.204→1.210, p10 −1.38→−1.47, p90 1.39 flat. | Heavy-rater "tightness" is largely **severity level, not discrimination**. No evidence heavy use the scale more informatively. |
| **2. Stability of own ratings** | Parity correlation of severity-adjusted `x = rating − delta` vs half-specific resid `r_half = rating − adj − delta_half` (isolates taste) | `x` parity **0.285 (10–24) → 0.931 (1000+)**, threshold t10 0.455→t100 0.787 — rises as n rises (expected noise reduction). Half-specific resid parity **−0.001 to −0.071** across all bands — no stable taste beyond game+severity, replicating Phase 3. | Stabilization is noise-reduction, not excess informativeness. |
| **3. Relative ordering vs consensus** | Within-user Pearson `r(x, adj_mean)` (delta-invariant per user) | **0.441 (10–24) med 0.491 → 0.484 (1000+) med 0.497**, overall 0.475/0.513; threshold t10 0.475→t100 0.501 **flat within 0.03** | Heavy do not order games more like consensus after severity. |
| **4. Agreement with others** | Pairwise RMSE of `x` on same game (no enumeration: `n·sumsq − sum²`), ICC within-game | Within-band RMSE `x` **1.630→1.704** — heavy **higher**, not lower; cross-band 1.70–1.79 > within; raw anchor 1.86→1.96 severity lowers ~0.23 but experience still not predictive. ICC `x` 0.126→0.195 slightly higher for heavy only because within variance mis-read. | Two heavy raters do **not** agree more than two light. |
| **5. Held-out usefulness** | LOO game-mean RMSE of `x` (`√mean(x_i − loo_mean_g)²`), even→odd holdout | LOO `x` **1.204→1.212** across bands (range **0.025**) vs raw U-shape 1.33–1.49. Threshold ge20 1.195 vs lt20 1.202 (Δ 0.007); ge50 1.193 vs lt50 1.206; even→odd 1.204 vs 1.212 vs overall 1.195 adj vs 1.372 raw — severity gain **0.177**, experience Δ ~0.01. | Heavy-rated `x` does not help predict others better; ~**0.01** experience gain is immaterial vs **0.177** severity gain and **0.23** Phase 2 holdout. |

**Supported conclusion — "no informativeness beyond severity":** After `delta_u` (spread 1.04, r 0.877, R² both 0.394, holdout 1.472→1.238), **none** of the five dimensions shows material experience gradient. Do **not** weight game-level estimates by experience beyond `delta`. The thresholds t=10,20,50 show no jump at t=50/100 warranting a new cutoff; strict tail (667) already handled.

**Limitations:** Even/odd split is one deterministic split; LOO/holdout within-sample (same BGG population) with ALS `adj_mean` — not external/broad-appeal validation; degenerate_broad sensitivity not re-weighted (strict already excluded); ICC of pure resid ~0 by construction.

*Script:* `scripts/28_phase31_rater_informativeness.py`. *Output:* `data/processed/phase2-active/phase31_informativeness.json` + committed `docs/phase2-active/phase31_informativeness.json` + `reports/phase31_informativeness/{tiered_summary.csv,threshold_sensitivity.csv}`. *Finding anchor:* "Phase 3.1 rater informativeness …".

---

## 7. Phase 4 — Within-game rater-pool self-selection (active, scripts/29)

**Threat to `adj_mean_g = mu+alpha_g = AVG(rating − delta)`:** Which active raters happen to rate which games — if a game's raters are unusually enthusiastic for *that* game beyond their global harshness, `adj_mean` remains biased. Two linked layers on active, reusing `mu=7.144` baseline — **no new credibility score**.

### Layer A — Pool composition vs population (heterogeneous but captured by severity)

- **Population baselines (active):** Unweighted mean delta **0.00** (SD 0.702, p10 −0.81 p90 0.85) vs obs-weighted **−0.303** (SD 0.683) — 0.30 shift reflects light (10–24 +0.27, 33.2% of users / 6.2% obs) vs heavy (1000+ −0.78, 0.37% users / 6.2% obs). Volume-band shares user 32.3/24.8/19.7/15.2/5.0/1.7/0.37 vs obs 6.2/10.3/16.3/27.6/20.2/13.2/6.2. `degenerate_broad` 1.15% users /0.43% obs. Collections snapshot: `own 58.0%`, `want 0.43%`, `preordered 0.31%` — **snapshot-time caveat** (at dump, not at rating).

- **Per-game pool (16,564 games, n_obs median 293 p10 100 p90 2,795 mean 1,480):**
  - `mean(delta_pool)` distribution: mean **−0.293**, **SD 0.177** (`P05 −0.563`, `P95 −0.024`, range −2.03 → 1.99). Variation is 25% of user-level SD(0.702) and 12% of rating SD 1.53 — non-trivial but modest. `corr(log n, mean_delta) = −0.109` (heavier slightly more negative, weak).
  - Volume concentration: `χ²(df6)` median **50.3** (p10 6.9 p90 454) vs critical 12.6; `KL` median **0.070** (p90 0.324) — almost all diverge vs population, but this is inflated by large n (median 293); share differences are the auditable metric. `share_heavy_500plus` median **0.271** (p90 0.478, mean 0.289) vs obs-pop 0.194; `share_light_10-24` median 0.039 (p90 0.103) vs 0.062; `share_heavy_250plus` median 0.496 (p90 0.712). `share_deg_broad` median 0.000 (p90 0.012).
  - Collection `share_own` median **0.575** (p10 0.404 p90 0.748 mean 0.571) — high everywhere, not a discriminating lens; snapshot-time vs event history unresolved.

**Supported conclusion:** Pools **do vary** modestly in heavy share and generosity, but the mapping heavy↔mean_delta is severity itself.

### Layer B — Do this game's raters like *it* more than expected?

Per-observation residual `r_ug = rating − (mu+alpha_g+delta_u) = rating − adj_mean_g − delta_u`:

| Test | Per-game distribution | Meaning |
|---|---|---|
| **Full-data `mean(r_g)`** | **3.8e−17 ± 7.4e−15** (median −5e−17, maxabs 2e−13) — **exact zero by construction** (`alpha_g = AVG(rating − mu − delta)` on same 24.5M) | **Cannot measure selection** — fit identity, reported to justify held-out alternatives. |
| **Cross-half `rating − adj_mean − delta_cross`** (delta_odd for even obs, one even/odd split; `adj_mean` still from full data) | mean **0.00014 ± 0.0153** (p05 −0.015 p95 0.016, range −0.417 → 0.512), 1% of rating SD and 2% of band spread; half |…|<0.004 | Small; leakage remains via full-data `adj`. Low-power for homogeneous enthusiasm (cancels across halves). |
| **Enthusiasm vs own other-game mean** `enth = x − other_mean` (`x=rating−delta`, other_mean over ≥10 other games) | mean **−0.416 ± 0.732**, **r(enth, adj)=0.987**, mean_other 7.34 ±0.20 vs adj SD 0.60, adjusted `enth−alpha = mu−mean_other ≈ −0.20` varies little | Enthusiasm is essentially **game quality**, not selection; uniformity of other-game quality suggests no selection lens beyond `alpha+delta`. |

**Material movement:**

- `raw − adj = mean(delta_pool)` (`r=0.984`); `corr(adj,raw)=0.979`, rank top-100 overlap **62/100** (Jaccard 0.449) — severity correction **does move candidates** (38% turnover) via `SD 0.177`.
- `adj vs adj+selection_residual` **r=1.00**, overlap **100/100** for k=50/100/250/500 — residual adds nothing.
- `adj vs cross` similarly **r≈1.0**; enthusiasm rank `r 0.987` not distinct.

**Supported conclusion:** Within-game selection **beyond global severity** is not measurably distinct or material. `adj_mean` remains sufficient; **do not condition a ranking on the near-zero residual**. Optionally report `mean_delta_pool` / `share_heavy` as a sensitivity column (drives raw↔adj shift). Broad-appeal gap (exposure denominator) stays open — Phase 4 tests only *within-pool* among raters who chose to rate some game.

**Limitations:** No exposure/non-rater denominator — `P(rate g | user)` unidentified without encounter data (propensity model not introduced); collection snapshot-time; game metadata 80.89% coverage; 60 games absent from SQLite snapshot; large-n χ² inflated; circularity of fitted `alpha`; timestamps unresolved.

*Script:* `scripts/29_phase4_within_game_selection.py`. *Output:* `reports/phase4_selection/selection_diagnostic.csv` (16,564 rows, per-game `raw_mean, adj_mean, mean_delta_pool, selection_residual_mean, selection_z, share_heavy_…`) + `selection_diagnostic.json` + committed `docs/phase2-active/phase4_selection.json`. *Finding anchor:* "Phase 4 — within-game rater-pool self-selection".

---

## 8. Phase 5 — Most defensible game-quality estimator (active, scripts/30)

**Estimands compared** (all on active, same design, `mu=7.144`):

| # | Estimand | Definition | Status |
|---|---|---|---|
| 1 | Raw active mean | `AVG(rating)` on active | Primary for n-consistent comparison; close to pop `avg_rating_current` (Pearson 0.975, median diff −0.017, n corr 0.994) |
| 2 | `bayes_rating` | `bgg_research_population.bayes_rating` (5.49 prior, lam ~2500); games.parquet 80.89% not used | Secondary |
| 3 | **Severity-adjusted** | `adj_mean_g = AVG(rating − delta_u) = mu+alpha_g` | **Preferred** |
| 4 | EB shrunk | `adj_shrunk = w·adj + (1−w)·mu`, `w=n/(n+lambda)`, `lambda=sigma_e²/sigma_alpha² = 1.91` (MM) vs `1.92` (Cov check — agreement) | Sensitivity |
| 4b | Interval | `adj ±1.96·SE` or posterior `shrunk ±1.96·post_SD` | Reported |

Active `n_g` distribution: mean **1,480**, median **293**, p10 **100**, p25 144, p75 872, p90 **2,795**, harmonic mean 106.5. `n=120` vs `12,000` differ **10×** in SE.

### EB variance — shrinkage is negligible for typical n

`sigma_e² = Var(rating−adj−delta)=1.426`, `sigma_e=1.194`; `Var(adj)=0.760` (SD 0.872, mean 6.926); `E[1/n]=0.00939` → `sigma_alpha² = 0.746`; **`lambda=1.91`** (vs BGG 2500 → **~1,300× stronger** overshrinkage).

| n_g | w = n/(n+1.91) | SE=1.194/√n | post_SD | 95% width |
|---|---|---|---|---|
| 50 | 0.963 (3.7% prior) | 0.169 | 0.166 | 0.662 |
| 100 (p10) | 0.981 (1.9%) | **0.119** | 0.118 | 0.468 |
| 120 (task) | 0.984 (1.6%) | **0.109** | 0.108 | 0.427 |
| 293 (median) | 0.994 (0.65%) | **0.070** | 0.070 | 0.273 |
| 2,795 (p90) | 0.9993 (0.07%) | **0.023** | 0.023 | 0.089 |
| 12,000 | 0.9998 (0.02%) | **0.011** | 0.011 | 0.043 — **10× more precise** than n=120 |

### Held-out validation (even/odd `rating_observation_id`, n=16,512 games both halves)

Game-level predicting held-out **`adj_odd`** (Var 0.763, SD 0.874):

| Estimand (from even) | Target | RMSE | R² | Corr | Bias |
|---|---|---|---|---|---|
| raw_even | adj_odd | **0.410** | **0.779** | 0.945 | −0.294 |
| **adj_even** | **adj_odd** | **0.217** | **0.938** | **0.969** | −0.001 |
| **adj_shrunk_even (lam 1.91)** | adj_odd | **0.205** | **0.945** | **0.972** | +0.001 |
| **bayes_rating** | adj_odd | **1.338** | **−1.35** | 0.563 | **−1.125** |
| bayes | raw_odd | 1.090 | −0.67 | 0.549 | −0.831 |

Stratified by `n_even`: shrunk helps only for `n<50` (mean 33.9, 1,560 games RMSE **0.519→0.470, gain 0.049 = 9%**); at 50–99 (4,593 games) gain **0.002**, 100+ <0.001.

Individual-level odd-rating: raw `RMSE 1.372→ `adj-predicts `rating−delta` **1.195** (gain 0.177, mirrors Phase 2 holdout 1.372→1.238). Interval coverage frequentist 81.8% / posterior 81.6% predicting other half's noisy mean — valid for latent theta, not for noisy target.

**Preferred estimator [Supported, model-dependent]:**

> **Primary: `adj_mean_g` with `SE = sigma_e/√n_g`** (sigma_e=1.194, lambda 1.91, mu=7.144). **`adj_shrunk` as optional sensitivity for low-n display (n<50–100), not replacement — BGG bayes (prior 5.49, lam 2500) is not a defensible quality estimate.**

Rationale: adj predicts held-out adj_odd **R² 0.938 RMSE 0.217** vs raw **0.779/0.410** — raw is biased by pool `mean(delta)` (SD 0.177) and predicts quality far worse (its R² 0.91 predicting `raw_odd` is irrelevant — confounded). EB shrinkage negligible for median game (w=0.994); only 9.4% of games have n<50 where 0.05-point gain appears. **Report `adj_mean` plus `SE` and lower bound `adj −1.96·SE`; do not treat 120- and 12,000-rating games as equally precise.** Weight RQ2 regression by `w_g = n_g/sigma_e²` or `1/SE²` (heteroscedasticity is order-of-magnitude).

**Limitations:** Within-BGG held-out only (even/odd split predicts severity-adjusted BGG mean, not external broad appeal); small-game caveat (n<50 noisy even after EB); timestamp unresolved; games 80.89% coverage respected via `bgg_research_population` complete join; interval under-coverage for noisy target under normal EB assumptions not validated.

*Script:* `scripts/30_phase5_quality_estimator.py`. *Output:* `data/processed/phase2-active/phase5_quality_estimator.json` + committed `docs/phase2-active/phase5_quality_comparison.json` + `reports/phase5_quality_estimator/{comparative_table.csv,stratified_rmse_by_n.csv,se_table.csv}`. *Finding anchor:* "Phase 5 — most defensible game-quality estimator".

---

## 9. Phase 6 — Expected-quality model and operational underratedness (active, scripts/31)

**Scope:** Two parts on active 16,549 complete-case games (same `mu=7.144, sigma_e=1.194`): (A) steer diagnostic — volume gradient under **both** targets, independently recorded; (B) transparent OLS/WLS expected-quality specs for `adj_mean` (5-fold CV, residual robustness, adj-vs-raw contrast). Features from complete `bgg_research_population`: `log10(n_active)` or band dummies, natural-spline year (4 knots .05/.35/.65/.95), weight, log playtime, min/max players, is_reimplementation, log times-reimplemented, **28 category + 34 mechanic flags (≥500 games)**. Explicit numpy WLS `min Σ w_i (y − x'b)²`.

### 9.1 Part A — volume gradient after severity [Empirical findings]

Volume predictors tested: **primary `n_active` (same n that drives `adj` SE, same universe)** and sensitivity `users_rated` (scrape, includes excluded users).

| Slope per 10× volume | Raw target | **Adj target** | adj/raw |
|---|---:|---:|---:|
| on `log10(n_active)` | +0.230 | **+0.261** | 1.13 |
| partial (weight + spline year) | +0.288 | **+0.323** | 1.12 |
| on `log10(users_rated)` | +0.473 | **+0.515** | 1.09 |

Top-vs-bottom log-volume decile gap: raw **+0.305 → adj +0.361**. Even/odd split slopes stable (raw .266/.265, adj .298/.295).

**Classification (pre-stated a/b/c):** **(c) broadly unchanged or grows** — removing severity **grows** the gradient by ~9–13% on active, replicating filtered-population `+0.444→+0.513` (scripts/22). High-volume pools skew harsher, so composition works *against* the premium; the gradient is **selection into volume (quality-driven popularity + visibility), not who-rates composition**.

**New nuance:** Curve is **non-monotonic at the bottom** — sub-100-rating games (1,612; 65 mean n) average raw 6.899 / **adj 7.169**, **above** 100–199 band 6.369/6.637; convex shape (top-decade slope ~+0.5 vs +0.23 avg). Band table (`phase6_volume_diagnostic.json`):

| Band | Games | mean n | adj_mean |
|---|---|---|---|
| 1–99 | 1,612 | 66 | 7.169 |
| 100–199 | 4,617 | 142 | 6.637 |
| 500–999 | 2,252 | 704 | 6.990 |
| 2.5k–5k | 893 | 3,496 | 7.375 |
| 10k–25k | 332 | 15,649 | 7.619 |
| 25k+ | 138 | 44,659 | 7.757 |

### 9.2 Part B — expected-quality specifications [Model-dependent empirical findings]

CV = 5-fold out-of-fold, **unweighted** metrics predicting `adj_mean` (seed 20260824):

| Spec ladder | CV R² | CV RMSE | Note |
|---|---|---|---|
| Q0 linear vol+year | .196 | 0.781 | — |
| +flexible year (spline) | .295 | 0.732 | +0.099; year non-linearity matters |
| **Q1 +weight** | **.540** | 0.591 | **+0.245 — weight is the single largest control** |
| +structure (playtime/players/reimpl) | .546 | 0.587 | — |
| +28 categories | .570 | 0.571 | — |
| **Q3b band-volume (preferred)** | **.582** ±.023 | **0.563** | 8 volume-band dummies + spline year + weight + structure + 28 cats; 46 features |
| Q4 +34 mechanics | .585 | 0.561 | +0.003 over Q3b at 1.6× features — kept as sensitivity |

Preferred **Q3b_flex_volume / OLS**: CV R² **0.5822**, RMSE 0.5633, `corr(CV resid, log n) = −0.004`, **band-flat residuals by construction** (linear log_n leaves U-shaped banded mean, max |band mean| **0.128** — bottom high, mid −0.05, top +0.10–0.13). Q3 (linear vol, 39 feat) 0.5704; Q4 (73 feat) 0.5849. Residual agreement Q3b vs Q3 Spearman **0.985** / top-1% Jaccard **0.675**; Q3b vs Q4 **0.958 / 0.579**.

**Weighting comparison — WLS is NOT material as a noise correction, and is harmful for the residual [Supported conclusion]:**

| Comparison | OLS (preferred) | `WLS w=n_g` (=1/SE²) | `GLS efficiency` `1/(sigma_alpha²+SE²)` |
|---|---|---|---|
| CV R² Q3b | .5822 | .5599 (−0.022) | .5701 (≈ OLS) |
| CV R² Q4 | .5849 | .5514 (−0.03) | — |
| beta_logn Q3 | 0.352 | 0.450 (+28–48% across specs) | 0.373 (≈ OLS) |
| Resid `corr(log n)` | ~0 | **−0.08 to −0.13** | ~−0.02 |
| Resid mean sub-100 | ~0 | **+0.32** | — |
| Rank-resid Spearman OLS↔WLS | .95–.99 | — | — |
| Top-1% Jaccard OLS↔WLS | .60–.74 | — | — |

Why: `SE² ≪ sigma_alpha² (0.746)` — efficiency weights are ≈ uniform (measurement noise ≪ between-game variance) and match OLS exactly; `w=n` is mostly **population reweighting toward popular games**, not noise correction. WLS residuals **leak volume** (−0.08..−0.13) and inflate the low-n tail — exactly where low-n candidates would live. **OLS carried forward**.

Low-n residual stability (full vs even-half `adj`): **corr 0.962 even in lowest n-quartile (mean n=100)**, 0.988+ elsewhere, identical across weightings — residuals dominated by stable between-game signal, not per-game noise (why weighting can't help).

**adj vs raw target (same design, OLS):** R² .584 (adj) vs .574 (raw) at Q3b; `beta_logn` adj 0.352 vs raw 0.318; residual Spearman **0.92–0.95** but **top-1% Jaccard only 0.36–0.42** — switching to adj **materially changes the candidate set (≈60% turnover at top 1%)**.

### 9.3 Operational output — `underratedness_g` [Method / Supported conclusion]

> **`underratedness_g = adj_mean_g − expected_quality_g`** (Q3b/OLS fit). Per-game parquet `data/processed/phase2-active/phase6_residuals_active.parquet` (16,549 rows: `se_adj` = `1.194/√n`, CV residuals, Q3/Q4/WLS variants; gitignored). `underratedness_pref = Q3b/OLS`, `underratedness_cv_pref` for robustness; use `se_adj`/lower-bound `adj − 1.96·SE` or `n≥100` floor for screening — raw top residuals otherwise dominated by n≤3 noise. **Model-dependent screen, not latent quality or broad appeal.** Top-1% sets 65–75% Jaccard-stable across reasonable variants (Q3b↔Q3 0.675, Q3b↔Q4 0.579, OLS↔WLS 0.74); `n≥100` preview dominated by party-game series (Monikers, Time's Up!) — highly rated well beyond characteristics, pending Phase 7 broad-appeal screen.

**Limitations:** No external broad-appeal validation; volume on the **right side** (expected given popularity) — band flexibility now absorbs the convex shape so the residual no longer contains volume gradient by construction (modeling choice); tags overlap (descriptive contrasts, not causal); measurement error in X (weight) not modeled; severity removes additive level only (Phase 4 beyond-additive ~0 but non-additive forms untested); even/odd stability within-snapshot (timestamps unresolved); metadata from complete population (games 80.89% caveat respected).

*Script:* `scripts/31_phase6_expected_quality_underratedness.py`. *Outputs:* `reports/phase6_underratedness/{comparative_table.csv,coefficient_table.csv,residual_overlap.csv,low_n_residual_stability.csv,volume_diagnostic_{band,decile}_table.csv,top_residuals_preview.csv}` + committed `docs/phase2-active/phase6_comparative.json` + `docs/phase2-active/phase6_volume_diagnostic.json` + gitignored `data/processed/phase2-active/phase6_residuals_active.parquet`. *Finding anchor:* "Phase 6 — expected-quality model and operational underratedness".

---

## 10. Cross-cutting numerical synthesis (current active base)

| Question | Quantity | Value (active primary) | Contrast / historical |
|---|---|---|---|
| **N** | Games / ratings / users | **16,627** research pop; **24,509,788** active obs (**91.0%** of full 26.9M, **96.7%** of filtered 25.3M); **288,730** users; **16,564** games with active ratings | Filtered 25.3M: 16,627×all users pre-t=10 |
| **Volume gradient** | Slope per 10× `n_active` (adj) | **+0.261** adj vs +0.230 raw (partial +0.323 vs +0.288) | Filtered HIST `+0.513` adj vs +0.444 raw — replication (c) grows after severity |
| | `users_rated` slope adj | **+0.515** vs raw +0.473 | — |
| **Quality baseline** | mu / sigma_e / SE | **mu 7.144**, **sigma_e 1.194**, **SE=1.194/√n**; median n 293 → SE 0.070; p10 100 → 0.119; p90 2795 → 0.023; 120 vs 12k is **10×** | — |
| | EB lambda | **1.91** (cov 1.92); w(100)=0.981, w(293)=0.994 | BGG bayes 2500, prior 5.49 → 1,300× stronger |
| | Held-out adj vs bayes | **adj R² 0.938 RMSE 0.217** vs **bayes R² −1.35 RMSE 1.34 bias −1.12** | — |
| | Adj shrunk gain | +0.012 overall, **0.049 (9%) only at n<50** | — |
| **Rater-level** | Band means / severity spread | Raw **7.726 (10–24) → 6.471 (1000+)**; delta **+0.27 → −0.78** spread **1.04** | Full HIST spread 2.09 inc. 1-band tail |
| | Within-game gap | **+1.11** (10–24 vs 1000+, 93.7% >0) ; FE beta +1.06 (SE 0.009) | HIST 10–24 beta +1.05 — identical |
| | R² game / rater / both | **0.201 / 0.218 / 0.394** | HIST 0.230/0.249/0.438 |
| | Parity severity | **r 0.877 (min10), 0.922 (min20)**; reliability ≥0.74 at 10–24 → ≥0.92 at ≥50 | HIST identical |
| | Gap decomposition | Standardized raw **0.892 → −0.034** after severity (~15% game-mix) | HIST 1.389→+0.01 |
| **Taste** | Residual tau | **|tau| ≤0.036** across 15 types (heavy +0.026, Variable Powers +0.036 max) | Raw tau up to +0.69 / −0.72 (composition) |
| | Stability | median r **0.355 weight / 0.179 cat / 0.166 mech** vs severity 0.877 | Threshold 0.5 **fail** |
| | Materiality | held-out **R² +0.0040, RMSE +0.0039** vs severity +0.193/+0.23 | Threshold 0.005/0.02 **fail** |
| **Informativeness** | 5 dimensions post-severity | SD resid flat 1.150→1.164 (0.03); share10 raw 11.8→1.4 → adj 5.0→3.1; ordering r 0.441→0.484 flat 0.03; pairwise RMSE 1.630→1.704 (heavy higher); LOO RMSE 1.187–1.212 (0.025) vs raw U 1.33–1.49 — **all flat** | Severity gain 0.177, experience Δ ~0.01 |
| **Selection** | Pool `mean(delta)` | Mean **−0.293**, **SD 0.177** (P05 −0.563 P95 −0.024) | User SD 0.702 for scale |
| | Selection resid | **~0 by construction** (SD 7e−15); cross-half **SD 0.015** (p05 −0.015 p95 0.016) = 1% of rating SD | 2% of severity spread |
| | Rank movement | raw↔adj **Jaccard top-100 0.45** (38% turnover); adj↔adj+resid **1.00** | adj↔raw corr 0.979 |
| **Expected quality** | CV R² / RMSE | **Q3b/OLS R² 0.582 RMSE 0.563**; Q1 weight alone 0.540; Q3 0.570; Q4 +mechanics 0.585 | Weight explains +0.245 alone |
| | WLS harmful | **OLS 0.582 → WLS 0.560**, resid corr −0.08..−0.13, sub-100 bias +0.32 | GLS eff ≈ OLS (noise ≪ between-game var) |
| | Underratedness | **Q3b/OLS residual** `adj − E[adj|X]`; low-n stability 0.962 at n≈100 | Overlap OLS↔raw ~0.36–0.42 (60% turnover) |

---

## 11. Key limitations — what the data still cannot answer

1. **No external broad-appeal ground truth.** All held-out checks are **within-Snapshot even/odd** of the same BGG population. No external audience, plays, sales, impressions, or cross-platform outcomes. The underratedness residual answers *"which games exceed a statistical expectation given BGG observables"* — not *"which would appeal broadly if seen"*.

2. **Games 80.89% coverage, `n_active` heteroscedasticity, internal validity of even/odd splits.** `games.parquet` covers 13,449/16,627 — seen only via `bgg_research_population` completeness in current analyses (limitation respected). Per-game precision varies **10×** — must be carried via `SE` or `1/SE²` weighting / intervals, not ignored. Even/odd splits test internal stability, not out-of-time or out-of-platform transport.

3. **No exposure denominator.** Number of people who saw/owned/played-but-did-not-rate is unobserved. Pool-composition tests are among raters who self-selected to rate *some* game — not versus the population who encountered the game and declined to rate. Propensity `P(rate g | user)` not identified.

4. **Snapshot vintage artefacts.** SQLite snapshot (latest review 2025-02-10) predates the scrape (`game_id` up to 438k vs 349k in `game_attrs`) — explains 19% `games` miss. `60` population games absent from SQLite at all (recent releases). `users_rated` vs `n_active` differ only slightly (r 0.994, median −0.02) but are conceptually distinct (scrape all-users vs active).

5. **Timestamp semantics unresolved.** `postdate` vs `rating_tstamp` meaning (event creation vs update/scrape) not validated — every temporal claim carries both readings where tested. Temporal drift, within-rater hardening, prior-exposure ordering, and longitudinal ownership all await semantics resolution.

6. **Degenerate / rare-type / metadata caveats.** `degenerate_strict` tail already excluded but its `degenerate_broad` flag travels for sensitivity; tiny-n flags uninformative below n≈10. Taste tested only on **frequent** types (≥5 cells, top categories/mechanics) — rare-type taste below detection remains open (archive). Tags overlap and are editorially assigned; categories/mechanics treated as descriptive contrasts, not causal effects; measurement error in X (weight) not modeled; severity is additive only (beyond-additive ≈0 in Phase 4 but non-additive forms untested); collections `own/want/preordered` are snapshot-time, not at rating.

7. **Historical game-level RQ2 underratedness is superseded.** Pre-active game-level residuals (16,612 cases) are retained as provenance but not as the primary — active severity-adjusted `adj_mean` + Phase 6 expected-quality model now define `underratedness_g`.

---

## 12. Supported roadmap — what to keep, what to stop, what remains open

**Keep (warranted by evidence):**

- `adj_mean_g = AVG(rating − delta_u)` (`mu=7.144`) as the defensible game-quality baseline for any underratedness question; always report with `SE` / lower bound and `n_active` (weight RQ2 by `1/SE²` or `n_g`).
- `underratedness_pref = Q3b/OLS residual` (8 band-volume dummies + spline year + weight + structure + 28 cats) as the **operational underratedness screen**; CV residual and Q3/Q4/WLS variants as robustness columns; `se_adj` / `n≥100` floor for candidate triage.
- Population choice: **t=10 primary / t=20 sensitivity**, `degenerate_strict` excluded, `degenerate_broad` flag for sensitivity only, all 16,627 games retained via `bgg_research_population` join discipline.

**Stop / do not add (earned-complexity failures):**

- Do **not** add `user×type` taste correction — stable taste does not exist for frequent types (|tau|≤0.036, held-out +0.004, stability ~0.35 vs 0.877).
- Do **not** weight game-level estimates by rater experience/volum`e` or invent a credibility score beyond `delta` — five post-severity informativeness dimensions are flat.
- Do **not** condition ranking on the within-game selection residual (~0, cross-half SD 0.015) — it is not a distinct signal after severity.
- Do **not** use `WLS w=n` for expected-quality fitting — it reweights toward popularity and leaks volume into the residual (+0.32 for sub-100).
- Do **not** use BGG `bayes_rating` (R² −1.35 vs 0.938, lambda 2500 vs 1.91, bias −1.12, corr 0.56 with adj) as a quality estimator — keep it only as a reference popularity rank.
- Do **not** treat a large residual as a hidden gem — volume is on the **right side** of Phase 6 (`expected given popularity`); residual tradeoff between quality and popularity remains confounded; broad-appeal screen is still to be built.

**Unresolved hypotheses (carried forward, not promoted):**

- Rare/niche taste on types <500 games below detection for the `cells≥5` design (archived full-snapshot taste is below-detection, not proof of absence).
- Timestamp-semantics dependents: temporal drift, experience hardening, user-split held-out `alpha` (non-circular game-level residual), prior-exposure taste, longitudinal `own` at rating time.
- Broad-appeal validation: no external reach outcome yet; Phase 6 `n≥100` preview's party-game concentration (Monikers, Time's Up!) shows a highly-rated anomaly that **still needs** the independent audience screen.

---

## 13. Reproducibility — how to rerun the active program

```bash
# Phase 1 population (already built; verify only)
# python scripts/01_clean_population.py

# Active extracts (prerequisite; prerequisite dataset bgg.sqlite must be present as scratch/phase2)
python scripts/24_build_active_phase2_extracts.py \
  --input-dir scratch/phase2 \
  --population scratch/phase2/bgg_research_population.parquet

# Refreshed baseline on active (Phase 2 active)
python scripts/26_phase2_active_baseline_refresh.py \
  --active-dir data/processed/phase2-active \
  --population scratch/phase2/bgg_research_population.parquet \
  --phase2-dir data/processed/phase2

# Phase 3 taste + 3.1 informativeness (reuse baseline, no refit)
python scripts/27_phase3_taste_active.py \
  --active-dir scratch/phase2-active \
  --population scratch/phase2-active/bgg_research_population.parquet \
  --out-dir data/processed/phase2-active

python scripts/28_phase31_rater_informativeness.py \
  --active-dir scratch/phase2-active \
  --population scratch/phase2-active/bgg_research_population.parquet \
  --out-dir data/processed/phase2-active

# Phase 4 selection (reuse baseline, no refit)
python scripts/29_phase4_within_game_selection.py \
  --active-dir scratch/phase2-active \
  --out-dir reports/phase4_selection

# Phase 5 quality estimator
python scripts/30_phase5_quality_estimator.py \
  --active-dir scratch/phase2-active \
  --population scratch/phase2-active/bgg_research_population.parquet \
  --out-dir data/processed/phase2-active

# Phase 6 expected quality + underratedness
python scripts/31_phase6_expected_quality_underratedness.py
```

Bounded invocations: `memory_limit=4GB` / `threads=3–4` / `temp_directory scratch/ducktmp`, explicit `SEMI JOIN`s, `EXPLAIN`-verified, `COPY` only for small outputs, deterministic `rating_observation_id` even/odd splits, `ORDER BY rating_observation_id` / `user_pseudouserid`. See `docs/phase2-active/README.md:188-219`.

---

## 14. Provenance table

| Phase / RQ | Source scripts (runnable) | Key input artifacts (read-only unless built) | Derived outputs quoted here (gitignored =再生) | Primary `findings.md` anchor (claim-tagged) |
|---|---|---|---|---|
| **RQ1 — Population** | `01_clean_population.py` | `data/raw/bgg_games_current.parquet` (161,404 rows) | `data/processed/bgg_research_population.parquet` (16,627) | 2026-08-23 Final Research Population Definition; Selection Bias Audit; Explicit unreleased/pre-release records removed; Population-correction refresh (§ Current population and RQ1 rating-volume results) |
| **RQ1 — Rating-volume & composition** | `03_rating_volume_behavior.py`, `04_rating_volume_composition.py` | `bgg_research_population.parquet` | — (descriptive tables; no derived parquet quoted) | Rating-volume behavior — sampling noise versus selection; Rating-volume composition — characteristics…; Composition across volume bands |
| **RQ2 — Game-level baseline (historical)** | `05_rq2_expected_rating_baseline.py` (+ residual export), `06_rq2_residual_robustness.py`, `07_rq2_stable_audience_proxies.py`, `11_rq2_candidate_report.py`, `12_modern_euro_shortlist.py` | `bgg_research_population.parquet`; `data/processed/rq2_residuals.parquet` | `docs/rq2_candidate_report.md`, `docs/modern_euro_shortlist.md` | RQ2 baseline — expected rating…; RQ2 residual robustness; Audience proxies; Provisional RQ2 candidate report; Population-correction refresh § Current RQ2… |
| **RQ3 — Non-identifiability** | `08_rq3_identifiability_audit.py` | All 36 processed fields + `dump_*` legacy + `families` | — | RQ3 identifiability audit — no independent cross-audience outcome |
| **Baselines — Bayes / rank / friend** | `09_friend_ranking_audit.py`, `10_friend_debiased_comparison.py` | `bgg_games_current.parquet`, `bgg_research_population.parquet`, `data/raw/complete_2025_bgg_debiased_ranks.csv` (24,695 rows) | — | Audit of the friend-provided debiased ranking; Friend debiased-ratings artifact; Game-level comparison… |
| **Phase 2 — SQLite inventory & extracts (historical)** | `13_build_phase2_extracts.py`, `14_phase2_rating_semantics_and_rater_behavior.py` | `data/raw/bgg.sqlite` (9 GB, 11 tables) | `data/processed/phase2/{games,users,ratings,rating_observations,collections,…}.parquet`, `rater_stats.parquet`, `rater_behavior_by_volume.parquet`, `validation.json` | Phase 2 SQLite database discovery inventory; Phase 2 analytical access layer…; Canonical rating observations… |
| **Phase 2 — Full-snapshot rater effects (historical)** | `15_phase2_same_game_volume_comparison.py`, `16_phase2_user_severity_stability.py` (`--reuse`), `17_phase2_gap_decomposition.py`, `18_phase2_rater_credibility.py`, `19_phase2_temporal_drift.py`, `20_phase2_audience_selection.py`, `21_phase2_cross_audience_consistency.py`, `22_phase2_baseline_comparison.py` | `data/processed/phase2/rating_observations.parquet` (26.9M), `user_severity.parquet`, `game_adjusted_means.parquet` | `data/processed/phase2/{user_severity,game_adjusted_means,gap_cells_…}.parquet` (historical) + JSONs | Phase A step 1 — the volume-level gap…; Phase A steps 2-3 — severity offsets…; Phase B — temporal drift…; Phase B item 8…; Session summary — Phase 2 complete |
| **Populations — Filtered & thresholds** | `23_build_filtered_phase2_extracts.py`, `23_user_threshold_study.py`, `25_phase2_anomalous_rater_audit.py`, `27_games_metadata_coverage_audit.py` | `bgg.sqlite` + `bgg_research_population.parquet`; `reports/user_population_thresholds.*`; `reports/anomalous_rater_audit/*`; `reports/games_metadata_coverage/*` | `data/processed/phase2-filtered/*` (25.3M obs), `reports/user_population_thresholds.{csv,json}`, `reports/anomalous_rater_audit/*`, `reports/games_metadata_coverage/{missing_ids.csv,summary.json}` | Filtered Phase 2 universe built; Primary analytical user population — threshold study; Anomalous / low-informative rater audit; Games metadata coverage audit (80.89%) |
| **Active population (current)** | `24_build_active_phase2_extracts.py` | `scratch/phase2/{rating_observations,users,collections}.parquet` + `bgg_research_population.parquet` + degenerate flag definitions cloned from `scripts/25` | `data/processed/phase2-active/{rating_observations_active,users_active,collections_active}.parquet` + `validation.json`/`extract_counts.json` + committed `docs/phase2-active/{validation,extract_counts,README}.parquet/json` | Active analytical extracts for the established population |
| **Phase 2-active — Refreshed baseline (current primary)** | `26_phase2_active_baseline_refresh.py` | `data/processed/phase2-active/*` + `bgg_research_population.parquet` | `data/processed/phase2-active/{user_severity_active,game_adjusted_means_active,active_baseline_…}.parquet/json` + committed `docs/phase2-active/active_baseline_refresh.json` | Refreshed Phase 2 statistical baseline on the active population |
| **Phase 3 — Taste (current)** | `27_phase3_taste_active.py` | `data/processed/phase2-active/{user_severity_active,game_adjusted_means_active}.parquet` (mu=7.144) + `bgg_research_population.parquet` (weight tertiles, flags) | `data/processed/phase2-active/phase3_taste_active.json` + committed `docs/phase2-active/phase3_taste_active.json` | Phase 3 taste investigation … global severity vs user×type taste |
| **Phase 3.1 — Informativeness (current)** | `28_phase31_rater_informativeness.py` | Same active baseline; one even/odd split | `data/processed/phase2-active/phase31_informativeness.json` + committed `docs/phase2-active/phase31_informativeness.json` + `reports/phase31_informativeness/*` | Phase 3.1 rater informativeness … beyond global severity |
| **Phase 4 — Within-game selection (current)** | `29_phase4_within_game_selection.py` | `data/processed/phase2-active/*` + `collections_active.parquet` (snapshot-time) | `reports/phase4_selection/{selection_diagnostic.csv/.json,pool_composition_summary.json}` + committed `docs/phase2-active/phase4_selection.json` | Phase 4 — within-game rater-pool self-selection |
| **Phase 5 — Quality estimator (current)** | `30_phase5_quality_estimator.py` | `data/processed/phase2-active/*` + `bgg_research_population.parquet` (bayes) | `data/processed/phase2-active/phase5_quality_estimator.json` + committed `docs/phase2-active/phase5_quality_comparison.json` + `reports/phase5_quality_estimator/*` | Phase 5 — most defensible game-quality estimator |
| **Phase 6 — Expected quality & underratedness (current)** | `31_phase6_expected_quality_underratedness.py` | `data/processed/phase2-active/{rating_observations_active,user_severity_active,game_adjusted_means_active}.parquet` + `bgg_research_population.parquet` (28+34 flags, band/decade dummies) | `data/processed/phase2-active/phase6_residuals_active.parquet` (16,549 rows, `underratedness_g`, `se_adj`, CV residuals) + `reports/phase6_underratedness/*` + committed `docs/phase2-active/{phase6_comparative,phase6_volume_diagnostic}.json` | Phase 6 — expected-quality model and operational underratedness |

**Validation contract for this synthesis:**

- Any number quoted as *active* was checked against the current Phase 6 artifacts listed above (`docs/phase2-active/*.json`, `reports/*`, `active_baseline_refresh.json` ALS convergence). Spot-checks used only file reads — no new DuckDB estimation beyond the validation reads required for the provenance rows.
- Game-level `bgg_research_population.parquet` is the **complete** join source for Phase 3–6 features; `games.parquet` 80.89% coverage is respected and stated as `N=16,627 primary`.
- Full-snapshot `data/processed/phase2/` extracts and scripts 15–22 fit artefacts are **historical reference only** — not mixed with filtered/active observations. Counts, validation, and caveats for the filtered layer: `docs/phase2-filtered/PARQUET_CATALOG.md` and `docs/phase2-active/README.md` / `PARQUET_CATALOG.md`.

---

## 15. Provenance of this document itself

- **Produced by:** synthesis of the existing research record (`findings.md` 1,815 lines at 2026-08-24, `docs/phase2-active/README.md`, `docs/phase2-active/*.json` ×7, `extract_counts.json`, `validation.json`, selected `reports/` CSVs for spot-checks). No new DuckDB estimation beyond the bounded validation reads listed in `scripts/26–31`.
- **Protected invariants:** Did not modify the Phase 6 model, residual definition (`adj − E[adj|X]`), candidate selection rules, or research population (16,627 × ≥10 minus strict). Did not build a hidden-gem score or start Phase 7.
- **General requirements followed:** `INTERMEDIATE / NOT FINAL` header; organized by phase/RQ with claim tags; active population base (`16,627`, `≥10`, `degenerate_strict` excluded, `24.5M`, `mu 7.144`, `SE 1.194/√n`) and Phase 6 `adj_mean` / `Q3b/OLS` residual base throughout; provenance / source scripts / input artifacts recorded; numbers validated against current Phase 6 artifacts.

<sub>Branch `fm/bgg-phase6-w4-consolidated` — single-file deliverable `docs/phase6-intermediate/findings_and_conclusions_to_date.md`. Historical `findings.md` retained as dated lab notebook; this file is the readable inventory, not a replacement.</sub>

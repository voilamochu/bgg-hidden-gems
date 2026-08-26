# Research Handoff

Source of truth: [findings.md](../findings.md), through **2026-08-24** (including **Phase 3 taste** `docs/phase2-active/phase3_taste_active.json`, **Phase 3.1 informativeness** `docs/phase2-active/phase31_informativeness.json`, and **Phase 4 within-game selection** `docs/phase2-active/phase4_selection.json` on the refreshed active baseline `docs/phase2-active/active_baseline_refresh.json`). The active 16,627 × ≥10 minus strict universe (`data/processed/phase2-active/`, 24.5M obs, `reports/phase4_selection/selection_diagnostic.csv` 16,564 games) is now the **primary** for quality/taste/hidden-gem work; full-snapshot 95,540×all-users artefacts are historical reference. Phase 4 completes the within-game selection threat test reusing the refreshed `user_severity_active.parquet` baseline (scripts/26→27→28→29), not older deltas.

## Dataset status

Two layers:

- **Game-level snapshot:** research population of **16,627 games** (`data/processed/bgg_research_population.parquet`); RQ2 complete cases **16,612**.
- **User-level SQLite snapshot (Phase 2):** canonical extract `data/processed/phase2/rating_observations.parquet` with **26,924,709 individual ratings**, **571,248 raters**, **95,540 games**, plus per-user volume bands/severity offsets and collection status. Different scrape from the game-level file; raw means agree (Pearson 0.979 matched). Timestamp semantics remain unresolved; all time-based conclusions are sensitivity-tested across `postdate` and `rating_tstamp`.

The earlier central limitation (no rater identities) is resolved for additive level effects: scripts 15–22 quantify them. Remaining limitations: no exposure denominator, no plays/sales, no longitudinal ownership, unresolved timestamp provenance.

## RQ1 — Rating estimate

### Established

- **[Observed fact]** Rating volume is highly skewed: the median game has 354 ratings, while the top 1% of games account for 27.2% of all ratings.
- **[Empirical finding]** Raw average rating increases from **6.435** in the 100–199-rating band to **7.531** in the 25k+ band. The within-band spread declines with volume, but much more slowly than a common-mean sampling-noise model would predict.
- **[Supported conclusion]** Sampling noise exists, especially near the 100-rating floor, but it is not sufficient to explain the cross-volume pattern. Popularity/composition selection is a major part of the association: volume remains positively related to ratings within weight, year, playtime, player-count, and many category/mechanic strata.
- **[Model-dependent conclusion]** `bayes_rating` is primarily a volume-weighted transformation of raw average. It is a useful shrinkage/ranking baseline, not a demonstrated estimate of population-wide underlying quality.
- **[Supported conclusion]** Neither raw average nor BGG Bayes should be treated as recovered broad-population quality. They answer different descriptive questions and both remain affected by the BGG selection process.

### Unresolved

- **[Unresolved hypothesis]** For an individual low-volume game, the data cannot distinguish ordinary rating noise, niche self-selection, early evidence of broad appeal, or a mixture of these.
- **[Limitation]** Per-game rating uncertainty cannot be estimated directly because individual-rating distributions and rater histories are absent.
- **[Limitation]** The 100-rating floor removes substantial noise but also excludes many genuine niche and newly published games.

## RQ2 — Underratedness / expected rating

### Established

- **[Method]** The transparent baseline predicts `avg_rating_current` from rating volume, release year, complexity, structural fields, frequent categories, and—only in sensitivity variants—frequent mechanics. It does not use BGG rank or Bayes as predictors.
- **[Empirical finding]** The primary S3 specification explains meaningful but incomplete variation (**R²=.5393**, RMSE **.5523**; cross-validated RMSE **.5537**). More flexible volume/year specifications improve fit modestly.
- **[Model-dependent conclusion]** A residual means observed average minus the model’s expected average for comparable retained BGG games. It is a conditional anomaly, not latent quality, causal underratedness, or broad appeal.
- **[Model-dependent conclusion]** The S3 residual is distinct from both baselines: it correlates **.679** with raw average, **.194** with Bayes, and approximately zero with log rating volume. This indicates that it is not simply a re-ranking of BGG Bayes.
- **[Empirical finding]** Residual ordering is moderately to strongly correlated across reasonable specifications, but exact top lists are unstable. Among seven adjusted specifications, the top-1% union has **325 games**, with **117 stable** in at least 5/7; the top-5% union has **1,460 games**, with **625 stable**.
- **[Supported conclusion]** A stable residual is more reproducible as a conditional anomaly than a specification-specific residual. Stable candidates tend to have larger, less dispersed positive residuals, but this is robustness to shared data and modeling choices—not independent replication.
- **[Empirical finding / interpretation]** Stable candidates are heterogeneous. Social/party/sports, card/fantasy, narrative, miniature, and tactical patterns all occur. Wargame/WWII/Simulation patterns are more specification-sensitive, while stable Card/Fantasy/Sports patterns are more reproducible.

### Unresolved and model-dependent

- **[Model-dependent conclusion]** Coefficients and residuals describe associations within the retained BGG population. They do not say that changing a game’s characteristics would change its rating.
- **[Limitation]** The models use equal game weighting and cannot account for per-game rating precision. Category/mechanic tags overlap and may be inconsistent; interactions are omitted.
- **[Unresolved hypothesis]** A positive residual may reflect genuine quality, niche self-selection, edition/visibility effects, omitted structure, rating noise, or some combination.
- **[Supported limitation]** Robust residuals do not establish broad appeal. Audience-proxy comparisons remain descriptive: tag counts, categories, mechanics, playtime, complexity, and player count do not observe audience diversity or cross-audience performance.
- **[Implication]** RQ2 can support transparent candidate screening and robustness reporting, but not a final hidden-gem ranking.

## RQ3 — Audience reach / hidden-gem identifiability

### Established

- **[Observed fact]** No field directly measures cross-audience reach or appeal. The dataset lacks rater segments, ratings by market/language/demographic group, exposure denominators, non-raters, plays, ownership, sales, external traffic, or independent audience outcomes.
- **[Supported conclusion]** `users_rated` measures participation in the selected BGG rating population. It is not a measure of audience breadth, and it is already an RQ2 input.
- **[Observed fact / interpretation]** Family tags such as digital implementations, Kickstarter, tutorials, Hall of Fame, `Game:`, and `Series:` links provide possible exposure or recognition context, but no exposure volume or audience response. They cannot validate broad appeal.
- **[Supported conclusion]** RQ3 is not identified by the current game-level dataset. Stable RQ2 residuals cannot be promoted to hidden-gem evidence.
- **[Supported conclusion]** No broad-appeal score or RQ3 ranking should be built from these fields.

### Friend-provided ranking status

- **[Observed fact / status]** The friend-provided file is available at `data/raw/complete_2025_bgg_debiased_ranks.csv` and contains `game_id` and `debiased_rating` fields. Its game-level comparison with current baselines is now recorded in the later findings entry; the underlying user-level method remains unevaluated. The `dump_*` fields remain legacy/current BGG fields and are not a substitute for the friend output.
- **[Empirical finding / qualified interpretation]** `dump_voters` is consistent with an earlier BGG snapshot: current counts exceed dump counts for 96.3% of paired research-population games, with median difference +24. However, no dump timestamp or provenance date exists.
- **[Limitation]** Current-versus-dump differences are descriptive same-platform changes, not leakage-safe temporal validation, independent audience evidence, or validation of the friend’s user-level method.

## What remains unresolved

1. The underlying quality of individual games after separating measurement noise from selected-rater composition.
2. Whether any low-volume positive residual reflects broad latent appeal or a well-matched niche audience.
3. Whether robust residual candidates would perform similarly among people who did not select them on BGG.
4. Within-game self-selection beyond global severity: tested in Phase 4 (scripts/29, 16,564 games, `mean(delta)` pool `SD 0.177`, selection residual `≈0` by construction, cross-half `SD 0.015`, enthusiasm `r 0.987` with quality) — no material game-specific enthusiasm beyond `alpha+delta` is detectable with these data; the material composition shift is already in `mean(delta)` (`raw` vs `adj` rank overlap `62/100`). Candidate for revisit only with a truly held-out `alpha` (user-split) or resolved collection timestamps.
5. Timestamp semantics: `postdate` and `rating_tstamp` provenance is still unresolved; all temporal results carry both readings, and collection `own` remains snapshot-time.

These are unresolved questions, not conclusions that the current results failed to find an effect.

## Second-pass methodology review — EXECUTED 2026-08-24 (comparison before adoption)

**Status: EXECUTED — deferred review now authorized and built for comparison** (`data/processed/phase2-second-pass/`, `docs/future-methodology-review/README.md:1` `executed_rules.md:1`, `findings.md:2026-08-24 second-pass`). Primary remains **16,627 × ≥10 minus strict → 24.5M obs (16,564 active)**; second-pass is `N'` for direct comparison. **Do not label current 16,627 "wrong"** — refinement enabled by 9 GB SQLite snapshot.

**Executed rule — game-level dedup (169 games, 1.0%):** edition/BigBox/deluxe/anniversary/collector/special/designer/revised where `stripped_base` collides (keep `max(users_rated)`) →153, plus targeted Monikers stem 7 + Time's Up! Game family 10 →17 (1 overlap), total 169 removed (140,272 obs, Jaccard 0.9897). Example: Small World Designer Edition 140135 n246 resid2.20 removed vs base 40692 n75285 kept; Monikers More Monikers 255249 etc 7 removed vs Monikers 156546 kept; Time's Up! Title Recall! 36553 etc 10 removed vs Time's Up! 1353 kept. Brass Birmingham vs Lancashire and Pandemic vs Legacy correctly kept separate. Reimplementation triple (47), broad family (996), language (0), duplicate moderate (49) investigated but NOT adopted (over-prunes map variants / distinct reprints) — sensitivity `bgg_population_second_pass_sensitivity_dup.parquet` (16412) for comparison.

**Recursive mutual closure (4 iterations):** primary closed **14,786 games** (pruned 1662+10, 287,776 users, 24.25M obs) vs base closed **14,941** (pruned 1675+11, 288,250 users, 24.40M obs); single-filter 14,952 vs closed 14,941 diff 11 — iteration adds little beyond single filter (as `bgg-sensitivity-n100` found). Rerun degenerate: closed strict **3 /287k 0.001%** vs active 0 (667 excluded) / 0.31% historically.

**Comparison before adoption (Phase5/6 preferred Q3b/OLS 46-feat, 5-fold CV):** Var(adj) 0.7596→0.7198 (−5%), lambda 1.91→1.99 (+4%), held-out RMSE 0.217→0.154 (noise), R² in 0.584→0.602 (+0.018 <0.02), beta_weight 0.461→0.473 (+2.5% <10%), corr(resid,log n) −0.004→+0.013, Jaccard top1% on overlap 0.934 (>0.70) Pearson 0.999, cross Jaccard 0.425 (includes n<100 high-SE, not model change). Current top-10 includes n1 resid3.94 + Monikers/Time/Small World duplicates (55% of top-20 are n<100); primary closed top-10 are all n≥100 SE≤0.084 (e.g., Red White & Blue Racin' n133 resid1.98). Base closed top still polluted with Monikers/Small World duplicates — dedup cleans screen beyond n-floor. **Decision: estimation stable → do NOT redefine primary population for estimation; add `n_active≥100` screening floor for Phase7 candidates; dedup cleans screening beyond n-floor, so Phase7 should use second-pass deduped universe (16458 before closure or 14786 closed) for screening.**

**Original deferred proposal (retained):** recursive mutual filtering — start from research population, iteratively remove games <100 and users <10, recomputing until closure, then rerun anomalous-rater identification. Rationale: Phase1 floor is on original `users_rated`, later user filtering can reduce `n_active` below 100; closure makes criteria mutually consistent. Requires comparison before adoption. Do not confuse with `n_active≥100` sensitivity (single-filter); this item is iterated fixed-point.

## Phase 2 user-level results — refreshed active baseline is now PRIMARY (scripts 26; details in findings.md 2026-08-24)

**Active primary (16,627 games × ≥10 active users minus strict, 24.5M obs, 288,730 users, 16,564 games; `data/processed/phase2-active/`, scripts/26):**
- **[Empirical finding]** Pooled gap `10-24` vs `1000+` is **+1.255** (raw band means 7.73→6.47); within games `10-24` vs `1000+` **+1.108** (94% >0), `10-49` vs `500plus` +0.83; game-FE betas +1.06→+0.19 vs `1000+`. The ordered rating-level shift survives on the same games (game-mix standardization removes only ~0.16 of the 1.06 gap; severity-adjusted gap closes to **-0.03**).
- **[Empirical finding]** Severity offsets re-estimated on active are stable (parity-half r=**0.877** min10, **0.922** min20; reliability ≥0.89 at ≥50 obs), ordered by lifetime volume (**+0.27** at `10-24` → **-0.78** at `1000+`, spread **1.04**; HISTORICAL spread 2.09 included the now-excluded `1`..`9` tail — comparable `10-24`→`1000+` slice was 1.07 historically). Nested-model R²: game **0.201**, rater **0.218**, both additive **0.394** (HISTORICAL 0.230/0.249/0.438); holdout RMSE game-only 1.472 → with severity **1.238**.
- **[Empirical finding / model-dependent]** The pattern replicates the full-snapshot conclusion: the low-vs-high-volume rating gap on the active set is almost entirely an additive rater-level level difference (severity), not game composition.

**Phase 3 taste — no material taste beyond severity (scripts/27; `docs/phase2-active/phase3_taste_active.json`):**
- **[Empirical finding]** Descriptive within-type gaps are large (heavy +0.69, light -0.72, Wargame +0.27, Party -0.43) but collapse after `mu+alpha+delta` to |tau|≤0.036 across 15 frequent types (weight tertiles and top categories/mechanics), vs rating SD 1.53 and severity spread 1.04.
- **[Empirical finding / Supported conclusion]** Taste is not a stable rater trait for frequent types (median even/odd parity r 0.355 weight, 0.179 cats, 0.166 mechs vs severity 0.877; threshold >0.5 fails), is distinct from severity (|r|≤0.08), and adds no material prediction (explicit `user×weight` with shrinkage: in-sample R² +0.0128, held-out R² +0.0040, RMSE +0.0039; vs severity gain R² +0.193, RMSE -0.23). Do not build `user×type` correction.

**Phase 3.1 informativeness — no calibration beyond severity predicts experience [Empirical findings; scripts/28 `docs/phase2-active/phase31_informativeness.json`]:**
- **[Empirical finding]** Scale discrimination: within-user SD raw 1.289→1.324, resid 1.150→1.164 flat across `10-24..1000+` (threshold `t10→100` 1.308→1.310 raw, 1.146→1.134 resid); entropy 1.96→2.33 then plateau. Raw share at 10 11.77%→1.44% collapses to 4.98%→3.07% after severity — heavy-rater "tightness" is severity, not informativeness.
- **[Empirical finding]** Stability: severity-adjusted rating `x = rating - delta` mean parity r 0.285 (10-24) →0.931 (1000+) rises with n as expected from noise (overall 0.455); half-specific resid `r = rating - adj_mean - delta_half` parity -0.001→-0.071 (no stable taste beyond game+severity).
- **[Empirical finding]** Ordering vs consensus: within-user `r(x, adj_mean)` 0.441 mean /0.491 med (10-24) →0.502/0.522 (100-249) →0.484/0.497 (1000+); overall 0.475/0.513; threshold `t10 0.475 →t100 0.501` — flat within 0.03; heavy does not order more like consensus.
- **[Empirical finding]** Agreement on same game: within-band pairwise RMSE `x` 1.630 (10-24) →1.704 (1000+) (higher for heavy); cross 10-24 vs 1000+ 1.79; raw anchor 1.86→1.96 severity reduces ~0.23 but experience still not predictive.
- **[Empirical finding / Model-dependent]** Predictive usefulness: LOO RMSE `x` 1.204 (10-24)→1.212 (1000+) range 0.025 vs raw U-shape 1.33–1.49; threshold ge50 1.193 vs lt50 1.206; even→odd holdout overall 1.372 raw→1.195 adj (severity gain 0.177) vs 1.20→1.21 across bands. No weighting advantage beyond delta.
- **[Supported conclusion]** Severity adjustment is sufficient; do **not** weight game-level estimates by rater experience beyond `delta_u`. No credible cutoff beyond `t=10` active + `degenerate_strict` exclusion is warranted; `t=20,50,100` sensitivities show no material jump.

**Phase 4 within-game selection — no material game-specific enthusiasm beyond severity (scripts/29; `docs/phase2-active/phase4_selection.json`, 16,564 games):**
- **[Empirical finding]** Pool composition: `mean(delta)` per game `-0.293 ±0.177` (`P05 -0.563`, `P95 -0.024`) vs obs-pop `-0.303`; `χ²(df6)` median `50.3` (`P90 454.5`), `KL 0.07` (`P90 0.324`); `share_heavy_500plus` median `0.271` vs `0.194` pop; `share_light_10-24` median `0.039` vs `0.062`; `share_own` median `0.575` vs `0.581`; exposure unobserved, collection snapshot-time, `80.89%` games metadata coverage.
- **[Empirical finding / Model-dependent]** Game surprise `r = rating - adj_mean - delta` mean per game `≈0 ±7e-15` (fit identity, `maxabs 2e-13`); cross-half (`delta_cross`) `0.00014 ±0.015` (`P05 -0.015`, `P95 0.016`) = 1% of rating SD `1.53`; enthusiasm vs own other-game mean `-0.416 ±0.732`, `r 0.987` with `adj_mean` — captures quality (`alpha`), not selection. No stable shared enthusiasm beyond `alpha+delta`.
- **[Empirical finding / Model-dependent]** Material movement: `raw - adj = mean(delta)` (`r 0.984`), `corr(adj,raw)=0.979`, rank top100 `62/100` (`J 0.45`) — severity correction does move candidates. `adj` vs `adj+resid` `r 1.0` overlap `100/100` — residual adds nothing.
- **[Supported conclusion]** Keep `adj_mean` (`mu=7.144`) as primary quality estimator; report `mean_delta_pool`/`share_heavy` as sensitivity where useful, do **not** condition downstream hidden-gem ranking on near-zero `selection_residual`; unobserved exposure denominator remains the RQ3 gap.

**Historical reference (full snapshot 95,540 games × all users, 26.9M obs, `data/processed/phase2/`; scripts 15–22 — do not mix with active observations):**
- Pooled gap `1` vs `1000+` +2.46; within games `1` vs `1000+` +2.28 (96% >0); game-mix removes only ~18%; severity-adjusted standardized gap +0.01.
- Severity: parity r=0.87, reliability ≥0.89 at ≥50, spread 2.09 (`1` +0.84 → `1000+` -1.25), R² 0.230/0.249/0.438.
- Geographic audiences agree closely (r≈0.86); owner vs non-owner raters disagree hugely (median gap 0.95) — not re-estimated on active (audience analysis unchanged).
- The friend's `debiased_rating` correlates 0.996 with the HISTORICAL severity-adjusted means; its shifts align (r=0.836, slope 0.67) — targets rater-level level differences, not noise. Not re-validated on active in this pass.

## Baselines

Compare any game estimate against: raw BGG average, BGG Bayesian rating, the RQ2 residual family (`data/processed/rq2_residuals.parquet`, regenerated by `scripts/05`), **refreshed** severity-adjusted means (`data/processed/phase2-active/game_adjusted_means_active.parquet`, scripts/26 — **primary for active-population work**), HISTORICAL severity-adjusted means (`data/processed/phase2/game_adjusted_means.parquet`, script 16 — reference only), and the friend's `debiased_rating`. These are baselines/hypotheses, not ground truth; see `scripts/22_phase2_baseline_comparison.py` (HISTORICAL) and `scripts/26` (active) for the comparison harness.

## Handoff recommendation

**Phases 3–4 complete taste, informativeness, and within-game selection on the refreshed active baseline** (`data/processed/phase2-active/`, scripts/26→27→28→29). Next work should **not** build a `user×type` taste model, an experience-weighted/credibility-weighted game estimator, **nor a game-specific selection residual ranking** — all add complexity without explanatory or predictive benefit on this active population (`|tau|≤0.036`, `R²+0.004`, LOO `+0.01`, selection residual `≈0` `SD 7e-15`, cross-half `SD 0.015` vs `1.53`).

Treat the current state as: **RQ1 volume patterns are not sampling noise alone, and the active re-estimate confirms the low-vs-high-volume gap is stable additive severity (within-game 10-24 vs 1000+ +1.11, severity-adjusted -0.03, parity 0.877, R² both 0.394); RQ2 provides a transparent residual signal (population-agnostic); Phase 3 taste shows no material `user×type` taste for frequent types (residual |tau|≤0.036, parity ≤0.35, held-out R² +0.004); Phase 3.1 shows no informativeness gradient beyond severity (scale SD flat, ordering flat 0.44→0.50, agreement not tighter for heavy, LOO flat 1.19–1.21, half-specific resid parity ~0); Phase 4 shows no material game-specific selection beyond `alpha+delta` (pool `mean(delta) SD 0.177` drives `raw` vs `adj` rank `62/100` but residual `≈0`, cross `SD 0.015`, enthusiasm `r 0.987` with quality) — the material adjustment is already `adj_mean`; RQ3 remains not identified — no field measures appeal beyond existing raters, and the next substantive step is exposure denominator / external validation, not a ranking formula.** Continue to treat residuals and adjusted means as descriptive screens only; optionally surface `mean_delta_pool`/`share_heavy` as sensitivity columns for candidate review.

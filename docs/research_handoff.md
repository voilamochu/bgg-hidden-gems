# Research Handoff

Source of truth: [findings.md](../findings.md), through **2026-08-24** (including **Phase 3 taste** `docs/phase2-active/phase3_taste_active.json` and **Phase 3.1 informativeness** `docs/phase2-active/phase31_informativeness.json` on the refreshed active baseline `docs/phase2-active/active_baseline_refresh.json`). The active 16,627 × ≥10 minus strict universe (`data/processed/phase2-active/`, 24.5M obs) is now the **primary** for quality/taste/hidden-gem work; full-snapshot 95,540×all-users artefacts are historical reference. Phase 3.1 completes the rater-level calibration sequence reusing the refreshed `user_severity_active.parquet` baseline (scripts/26→27→28), not older deltas.

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
4. Within-game self-selection: additive user severity explains the volume-band gradient almost exactly, but "severity" may partially encode enthusiasm trajectories that this snapshot cannot separate from scale anchoring.
5. Timestamp semantics: `postdate` and `rating_tstamp` provenance is still unresolved; all temporal results carry both readings.

These are unresolved questions, not conclusions that the current results failed to find an effect.

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

**Historical reference (full snapshot 95,540 games × all users, 26.9M obs, `data/processed/phase2/`; scripts 15–22 — do not mix with active observations):**
- Pooled gap `1` vs `1000+` +2.46; within games `1` vs `1000+` +2.28 (96% >0); game-mix removes only ~18%; severity-adjusted standardized gap +0.01.
- Severity: parity r=0.87, reliability ≥0.89 at ≥50, spread 2.09 (`1` +0.84 → `1000+` -1.25), R² 0.230/0.249/0.438.
- Geographic audiences agree closely (r≈0.86); owner vs non-owner raters disagree hugely (median gap 0.95) — not re-estimated on active (audience analysis unchanged).
- The friend's `debiased_rating` correlates 0.996 with the HISTORICAL severity-adjusted means; its shifts align (r=0.836, slope 0.67) — targets rater-level level differences, not noise. Not re-validated on active in this pass.

## Baselines

Compare any game estimate against: raw BGG average, BGG Bayesian rating, the RQ2 residual family (`data/processed/rq2_residuals.parquet`, regenerated by `scripts/05`), **refreshed** severity-adjusted means (`data/processed/phase2-active/game_adjusted_means_active.parquet`, scripts/26 — **primary for active-population work**), HISTORICAL severity-adjusted means (`data/processed/phase2/game_adjusted_means.parquet`, script 16 — reference only), and the friend's `debiased_rating`. These are baselines/hypotheses, not ground truth; see `scripts/22_phase2_baseline_comparison.py` (HISTORICAL) and `scripts/26` (active) for the comparison harness.

## Handoff recommendation

**Phase 3 completes taste and informativeness on the refreshed active baseline** (`data/processed/phase2-active/`, scripts/26→27→28). Next work should **not** build a `user×type` taste model nor an experience-weighted/credibility-weighted game estimator — both add complexity without explanatory or predictive benefit on this active population.

Treat the current state as: **RQ1 volume patterns are not sampling noise alone, and the active re-estimate confirms the low-vs-high-volume gap is stable additive severity (within-game 10-24 vs 1000+ +1.11, severity-adjusted -0.03, parity 0.877, R² both 0.394); RQ2 provides a transparent residual signal (population-agnostic); Phase 3 taste shows no material `user×type` taste for frequent types (residual |tau|≤0.036, parity ≤0.35, held-out R² +0.004); Phase 3.1 shows no informativeness gradient beyond severity (scale SD flat, ordering flat 0.44→0.50, agreement not tighter for heavy, LOO flat 1.19–1.21, half-specific resid parity ~0); the refreshed severity-adjusted game estimates (`mu=7.144`, `adj_mean = AVG(rating - delta)`, reliability ≥0.89 at ≥50) are sufficient and reproducible without experience weighting; RQ3 remains not identified — no field measures appeal beyond existing raters, and the next substantive step is within-game enthusiasm vs anchoring and exposure denominator, not a ranking formula.** Continue to treat residuals and adjusted means as descriptive screens only.

# Research Handoff

Source of truth: [findings.md](../findings.md), through **2026-08-24** (including the refreshed **active-population Phase 2 baseline** in `docs/phase2-active/active_baseline_refresh.json`). The active 16,627 × ≥10 minus strict universe (`data/processed/phase2-active/`, 24.5M obs) is now the **primary** for quality/taste/hidden-gem work; full-snapshot 95,540×all-users artefacts are historical reference. Phase 3 resumes from the paused point using the **refreshed** `user_severity_active.parquet` baseline (scripts/26), not the older `phase2/user_severity.parquet` deltas.

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

**Historical reference (full snapshot 95,540 games × all users, 26.9M obs, `data/processed/phase2/`; scripts 15–22 — do not mix with active observations):**
- Pooled gap `1` vs `1000+` +2.46; within games `1` vs `1000+` +2.28 (96% >0); game-mix removes only ~18%; severity-adjusted standardized gap +0.01.
- Severity: parity r=0.87, reliability ≥0.89 at ≥50, spread 2.09 (`1` +0.84 → `1000+` -1.25), R² 0.230/0.249/0.438.
- Geographic audiences agree closely (r≈0.86); owner vs non-owner raters disagree hugely (median gap 0.95) — not re-estimated on active (audience analysis unchanged).
- The friend's `debiased_rating` correlates 0.996 with the HISTORICAL severity-adjusted means; its shifts align (r=0.836, slope 0.67) — targets rater-level level differences, not noise. Not re-validated on active in this pass.

## Baselines

Compare any game estimate against: raw BGG average, BGG Bayesian rating, the RQ2 residual family (`data/processed/rq2_residuals.parquet`, regenerated by `scripts/05`), **refreshed** severity-adjusted means (`data/processed/phase2-active/game_adjusted_means_active.parquet`, scripts/26 — **primary for active-population work**), HISTORICAL severity-adjusted means (`data/processed/phase2/game_adjusted_means.parquet`, script 16 — reference only), and the friend's `debiased_rating`. These are baselines/hypotheses, not ground truth; see `scripts/22_phase2_baseline_comparison.py` (HISTORICAL) and `scripts/26` (active) for the comparison harness.

## Handoff recommendation

**Phase 3 resumes from the paused point on the refreshed active baseline** (`data/processed/phase2-active/`, scripts/26). The held `bgg-phase3-taste-filtered` task must use the refreshed `user_severity_active.parquet` deltas — not the older `phase2-filtered` or full-snapshot deltas.

Treat the current state as: **RQ1 volume patterns are not sampling noise alone, and the refreshed active-population re-estimate confirms the low-vs-high-volume rater gap remains almost entirely stable additive rater-level level differences (active within-game `10-24` vs `1000+` +1.11, severity-adjusted gap -0.03); RQ2 provides a transparent, model-dependent residual signal (population-agnostic, unchanged); the refreshed severity-adjusted game estimates (mu=7.144, R² both=0.394, reliability ≥0.89 at ≥50) are implementable and reproducible on the active population; RQ3 remains not identified — geographic/ownership audience agreements were established on the full snapshot and not refit here, and no field measures appeal beyond the existing rater pool.** Continue to treat residuals and adjusted means as descriptive screens only. The next substantive step is within-game selection identification (enthusiasm trajectories vs scale anchoring) and acquisition of exposure/audience-stratified evidence — not a more complex ranking formula.

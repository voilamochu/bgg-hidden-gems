# Broad-Appeal Evidence Assessment — Robust Underrated Candidates (INTERMEDIATE / NOT FINAL)

> **Status:** INTERMEDIATE / NOT FINAL — screening stage, not the final hidden-gem ranking. **Do not treat as proof of broad appeal:** `users_rated` is popularity, not breadth; high residual is underratedness, not broad appeal; high `raw`/`adj` is quality estimate, not audience breadth; `own 58%` is snapshot-time (`PR #4`); category breadth is tag overlap; low `n` is *less* evidence.
> **Method:** For each of the **910** robust underrated candidates from A (`n≥200 & resid≥0.60 & min_alt≥0.30 & z≥5 & year<2025`), separately report four evidence types with caveats (see README §4). No RQ3 hidden-gem score is built. A niche game can remain an excellent underrated candidate without being promoted to hidden-gem status.
> **Evidence taxonomy (per AGENTS.md central problem):** (1) reach/recognition (users_rated, num_weights, rank, is_reimplementation reach) — *not* proof of broad appeal; (2) audience composition (share_heavy / mean(delta), country where non-missing, collections own snapshot); (3) cross-audience consistency (heavy vs light rater means where available, category breadth) — low volume is not broad appeal; (4) proxy caveats (raw/adj, residual, low n, own, categories cannot establish broad appeal).

Generated: 2026-08-24T10:51:41.735635+00:00Z  •  Population: 16,627 ×≥10 ¬strict (24.5M obs, mu 7.144)  •  Residual: Q3b/OLS `adj − expected`  •  Candidates: robust 910 (broad pool 7754 for reference)

## 1. Monikers: More Monikers — `game_id 255249` (2018; n=452 decile D7)
**Underratedness (A):** `resid 2.27` = `adj 8.58` − `E[adj] 6.30`; `SE 0.056` `post_SD 0.056` `z=40.5` `lb_adj 8.47` `resid_lb 2.16`; stability `CV 2.26` `WLS 2.33` `Q3 2.18` `WLS_Q3 2.24` `min_alt 2.18` `cv_diff 0.014` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 2.27 n=452 SE 0.056 z=40.5 min_alt 2.18 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Card Game; Humor; Mature / Adult; Party Game` (`n_cats 4`) / `Acting; Open Drafting; Role Playing` (`n_mechs 3`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **521** (rank 3227) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D7` vol_band `200-499`
- `num_weights` (attention proxy) **2** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.00` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.315** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.170** (`share_heavy_250plus 0.394`, `share_light_10-24 0.024`, `mean_cnt_pool 319`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.845** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 21.3` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.940** (`11` low-mean 8.60 vs `19` high-mean 7.66; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.851** (`47` low-mean 8.57 vs `76` high-mean 7.72; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.905** (`36` low-mean 8.56 vs `19` high-mean 7.66; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **4** categories `Card Game; Humor; Mature / Adult; Party Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **8.26**, `adj_mean` **8.58** themselves are quality estimates, not breadth; residual **2.27** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 452` `SE 0.056` `post_SD 0.056` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.845` everywhere, snapshot-time, `PR #4` caveat; `categories` 4 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 2. Small World Designer Edition — `game_id 140135` (2015; n=246 decile D5)
**Underratedness (A):** `resid 2.20` = `adj 9.10` − `E[adj] 6.90`; `SE 0.076` `post_SD 0.076` `z=28.9` `lb_adj 8.95` `resid_lb 2.05`; stability `CV 2.19` `WLS 2.17` `Q3 2.20` `WLS_Q3 2.23` `min_alt 2.17` `cv_diff 0.014` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 2.20 n=246 SE 0.076 z=28.9 min_alt 2.17 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Civilization; Fantasy; Territory Building` (`n_cats 3`) / `Area Majority / Influence; Area Movement; Dice Rolling; Variable Player Powers` (`n_mechs 4`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **266** (unranked) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D5` vol_band `200-499`
- `num_weights` (attention proxy) **12** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.58` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.200** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.301** (`share_heavy_250plus 0.516`, `share_light_10-24 0.037`, `mean_cnt_pool 509`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.695** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 41.2` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.586** (`9` low-mean 9.09 vs `37` high-mean 8.50; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.604** (`24` low-mean 9.21 vs `74` high-mean 8.61; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.786** (`15` low-mean 9.29 vs `37` high-mean 8.50; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **3** categories `Civilization; Fantasy; Territory Building` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **8.90**, `adj_mean` **9.10** themselves are quality estimates, not breadth; residual **2.20** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 246` `SE 0.076` `post_SD 0.076` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.695` everywhere, snapshot-time, `PR #4` caveat; `categories` 3 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 3. Monikers: Shmonikers — `game_id 179448` (2015; n=319 decile D6)
**Underratedness (A):** `resid 2.05` = `adj 8.30` − `E[adj] 6.24`; `SE 0.067` `post_SD 0.067` `z=30.7` `lb_adj 8.17` `resid_lb 1.92`; stability `CV 2.05` `WLS 1.88` `Q3 2.03` `WLS_Q3 1.87` `min_alt 1.87` `cv_diff 0.005` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 2.05 n=319 SE 0.067 z=30.7 min_alt 1.87 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Party Game` (`n_cats 1`) / `Acting; Open Drafting; Role Playing` (`n_mechs 3`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **326** (rank 4747) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D6` vol_band `200-499`
- `num_weights` (attention proxy) **3** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.00` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.294** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.194** (`share_heavy_250plus 0.404`, `share_light_10-24 0.025`, `mean_cnt_pool 328`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.871** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 9.5` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.090** (`8` low-mean 8.50 vs `16` high-mean 7.41; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.907** (`39` low-mean 8.39 vs `62` high-mean 7.48; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.953** (`31` low-mean 8.36 vs `16` high-mean 7.41; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **1** categories `Party Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **8.00**, `adj_mean` **8.30** themselves are quality estimates, not breadth; residual **2.05** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 319` `SE 0.067` `post_SD 0.067` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.871` everywhere, snapshot-time, `PR #4` caveat; `categories` 1 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 4. Monikers: Something Something — `game_id 195709` (2016; n=246 decile D5)
**Underratedness (A):** `resid 2.03` = `adj 8.33` − `E[adj] 6.30`; `SE 0.076` `post_SD 0.076` `z=26.6` `lb_adj 8.18` `resid_lb 1.88`; stability `CV 2.06` `WLS 1.86` `Q3 2.04` `WLS_Q3 1.90` `min_alt 1.86` `cv_diff 0.034` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 2.03 n=246 SE 0.076 z=26.6 min_alt 1.86 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Party Game` (`n_cats 1`) / `Acting; Open Drafting; Role Playing` (`n_mechs 3`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **255** (rank 5504) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D5` vol_band `200-499`
- `num_weights` (attention proxy) **1** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.00` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.288** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.191** (`share_heavy_250plus 0.411`, `share_light_10-24 0.024`, `mean_cnt_pool 337`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.870** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 15.9` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.436** (`6` low-mean 8.67 vs `13` high-mean 7.23; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.969** (`20` low-mean 8.50 vs `47` high-mean 7.53; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.198** (`14` low-mean 8.43 vs `13` high-mean 7.23; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **1** categories `Party Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **8.04**, `adj_mean` **8.33** themselves are quality estimates, not breadth; residual **2.03** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 246` `SE 0.076` `post_SD 0.076` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.870` everywhere, snapshot-time, `PR #4` caveat; `categories` 1 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 5. Monikers: The Shut Up & Sit Down Nonsense Box — `game_id 221248` (2017; n=465 decile D7)
**Underratedness (A):** `resid 1.99` = `adj 8.36` − `E[adj] 6.36`; `SE 0.055` `post_SD 0.055` `z=36.0` `lb_adj 8.25` `resid_lb 1.89`; stability `CV 1.99` `WLS 1.84` `Q3 1.91` `WLS_Q3 1.75` `min_alt 1.75` `cv_diff 0.009` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.99 n=465 SE 0.055 z=36.0 min_alt 1.75 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Party Game` (`n_cats 1`) / `Acting; Open Drafting; Role Playing` (`n_mechs 3`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **484** (rank 3607) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D7` vol_band `200-499`
- `num_weights` (attention proxy) **4** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.00` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.314** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.159** (`share_heavy_250plus 0.374`, `share_light_10-24 0.024`, `mean_cnt_pool 318`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.824** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 26.0` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.173** (`11` low-mean 8.36 vs `21` high-mean 7.19; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.921** (`49` low-mean 8.39 vs `74` high-mean 7.47; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.204** (`38` low-mean 8.39 vs `21` high-mean 7.19; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **1** categories `Party Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **8.04**, `adj_mean` **8.36** themselves are quality estimates, not breadth; residual **1.99** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 465` `SE 0.055` `post_SD 0.055` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.824` everywhere, snapshot-time, `PR #4` caveat; `categories` 1 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 6. Monikers: Serious Nonsense — `game_id 283152` (2019; n=500 decile D7)
**Underratedness (A):** `resid 1.94` = `adj 8.48` − `E[adj] 6.55`; `SE 0.053` `post_SD 0.053` `z=36.2` `lb_adj 8.38` `resid_lb 1.83`; stability `CV 1.96` `WLS 1.99` `Q3 1.99` `WLS_Q3 2.05` `min_alt 1.96` `cv_diff 0.026` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.94 n=500 SE 0.053 z=36.2 min_alt 1.96 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Humor; Mature / Adult; Party Game` (`n_cats 3`) / `Acting; Open Drafting; Role Playing` (`n_mechs 3`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **609** (rank 2928) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D7` vol_band `500-999`
- `num_weights` (attention proxy) **8** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.00` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.279** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.126** (`share_heavy_250plus 0.370`, `share_light_10-24 0.020`, `mean_cnt_pool 286`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.868** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 37.8` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.833** (`10` low-mean 9.20 vs `15` high-mean 7.37; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.849** (`60` low-mean 8.60 vs `63` high-mean 7.76; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.119** (`50` low-mean 8.49 vs `15` high-mean 7.37; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **3** categories `Humor; Mature / Adult; Party Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **8.21**, `adj_mean` **8.48** themselves are quality estimates, not breadth; residual **1.94** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 500` `SE 0.053` `post_SD 0.053` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.868` everywhere, snapshot-time, `PR #4` caveat; `categories` 3 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 7. Time's Up! Title Recall! — `game_id 36553` (2008; n=3629 decile D10)
**Underratedness (A):** `resid 1.93` = `adj 8.03` − `E[adj] 6.10`; `SE 0.020` `post_SD 0.020` `z=97.3` `lb_adj 7.99` `resid_lb 1.89`; stability `CV 1.93` `WLS 1.69` `Q3 2.01` `WLS_Q3 1.68` `min_alt 1.68` `cv_diff 0.002` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.93 n=3629 SE 0.020 z=97.3 min_alt 1.68 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Humor; Movies / TV / Radio theme; Party Game` (`n_cats 3`) / `Acting; Communication Limits; Memory; Team-Based Game` (`n_mechs 4`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **3787** (rank 731) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D10` vol_band `2.5k-5k`
- `num_weights` (attention proxy) **95** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.19` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.358** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.242** (`share_heavy_250plus 0.487`, `share_light_10-24 0.020`, `mean_cnt_pool 382`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.633** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 251.9` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.822** (`72` low-mean 7.99 vs `262` high-mean 7.16; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.583** (`310` low-mean 7.96 vs `880` high-mean 7.38; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.785** (`238` low-mean 7.95 vs `262` high-mean 7.16; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **3** categories `Humor; Movies / TV / Radio theme; Party Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.67**, `adj_mean` **8.03** themselves are quality estimates, not breadth; residual **1.93** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 3629` `SE 0.020` `post_SD 0.020` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.633` everywhere, snapshot-time, `PR #4` caveat; `categories` 3 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 8. Monikers: Classics — `game_id 283151` (2019; n=263 decile D5)
**Underratedness (A):** `resid 1.92` = `adj 8.45` − `E[adj] 6.52`; `SE 0.074` `post_SD 0.073` `z=26.1` `lb_adj 8.30` `resid_lb 1.78`; stability `CV 1.96` `WLS 1.79` `Q3 1.91` `WLS_Q3 1.81` `min_alt 1.79` `cv_diff 0.036` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.92 n=263 SE 0.074 z=26.1 min_alt 1.79 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Party Game` (`n_cats 1`) / `—` (`n_mechs 0`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **343** (unranked) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D5` vol_band `200-499`
- `num_weights` (attention proxy) **4** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.00` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.260** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.129** (`share_heavy_250plus 0.346`, `share_light_10-24 0.034`, `mean_cnt_pool 265`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.882** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 17.3` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.733** (`9` low-mean 8.90 vs `6` high-mean 8.17; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +1.087** (`32` low-mean 8.69 vs `34` high-mean 7.60; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.441** (`23` low-mean 8.61 vs `6` high-mean 8.17; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **1** categories `Party Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **8.19**, `adj_mean` **8.45** themselves are quality estimates, not breadth; residual **1.92** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 263` `SE 0.074` `post_SD 0.073` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.882` everywhere, snapshot-time, `PR #4` caveat; `categories` 1 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 9. A Gamut of Games — `game_id 4385` (1969; n=434 decile D7)
**Underratedness (A):** `resid 1.92` = `adj 8.08` − `E[adj] 6.16`; `SE 0.057` `post_SD 0.057` `z=33.5` `lb_adj 7.97` `resid_lb 1.81`; stability `CV 1.91` `WLS 2.18` `Q3 1.85` `WLS_Q3 2.07` `min_alt 1.85` `cv_diff 0.009` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.92 n=434 SE 0.057 z=33.5 min_alt 1.85 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Abstract Strategy; Book; Card Game; Deduction; Dice; Sports` (`n_cats 6`) / `—` (`n_mechs 0`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **445** (unranked) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D7` vol_band `200-499`
- `num_weights` (attention proxy) **34** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.32` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.317** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.369** (`share_heavy_250plus 0.604`, `share_light_10-24 0.023`, `mean_cnt_pool 587`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.788** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 127.8` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.829** (`10` low-mean 8.95 vs `68` high-mean 7.12; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +1.260** (`34` low-mean 8.68 vs `160` high-mean 7.42; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.441** (`24` low-mean 8.56 vs `68` high-mean 7.12; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **6** categories `Abstract Strategy; Book; Card Game; Deduction; Dice; Sports` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.76**, `adj_mean` **8.08** themselves are quality estimates, not breadth; residual **1.92** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 434` `SE 0.057` `post_SD 0.057` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.788` everywhere, snapshot-time, `PR #4` caveat; `categories` 6 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 10. Time's Up! Party Edition — `game_id 230262` (2004; n=553 decile D7)
**Underratedness (A):** `resid 1.86` = `adj 7.91` − `E[adj] 6.05`; `SE 0.051` `post_SD 0.051` `z=36.7` `lb_adj 7.81` `resid_lb 1.76`; stability `CV 1.87` `WLS 1.83` `Q3 1.91` `WLS_Q3 1.86` `min_alt 1.83` `cv_diff 0.010` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.86 n=553 SE 0.051 z=36.7 min_alt 1.83 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Humor; Party Game` (`n_cats 2`) / `Acting; Memory; Team-Based Game` (`n_mechs 3`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **714** (rank 3245) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D7` vol_band `500-999`
- `num_weights` (attention proxy) **15** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.13` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.339** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.186** (`share_heavy_250plus 0.353`, `share_light_10-24 0.033`, `mean_cnt_pool 306`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.731** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 19.7` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.750** (`18` low-mean 7.86 vs `28` high-mean 7.11; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.433** (`81` low-mean 7.75 vs `103` high-mean 7.32; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.609** (`63` low-mean 7.72 vs `28` high-mean 7.11; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `Humor; Party Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.57**, `adj_mean` **7.91** themselves are quality estimates, not breadth; residual **1.86** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 553` `SE 0.051` `post_SD 0.051` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.731` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 11. Time's Up! Edición Azul — `game_id 57660` (2006; n=1365 decile D9)
**Underratedness (A):** `resid 1.76` = `adj 7.68` − `E[adj] 5.92`; `SE 0.032` `post_SD 0.032` `z=54.4` `lb_adj 7.62` `resid_lb 1.70`; stability `CV 1.76` `WLS 1.50` `Q3 1.83` `WLS_Q3 1.52` `min_alt 1.50` `cv_diff 0.003` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.76 n=1365 SE 0.032 z=54.4 min_alt 1.50 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Humor; Movies / TV / Radio theme; Party Game` (`n_cats 3`) / `Acting; Communication Limits; Memory; Team-Based Game` (`n_mechs 4`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **1463** (rank 2142) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D9` vol_band `1k-2.5k`
- `num_weights` (attention proxy) **59** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.22` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.313** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.214** (`share_heavy_250plus 0.433`, `share_light_10-24 0.039`, `mean_cnt_pool 358`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.629** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 21.1` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.328** (`53` low-mean 7.22 vs `87` high-mean 6.89; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.288** (`172` low-mean 7.42 vs `292` high-mean 7.13; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.618** (`119` low-mean 7.51 vs `87` high-mean 6.89; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **3** categories `Humor; Movies / TV / Radio theme; Party Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.37**, `adj_mean` **7.68** themselves are quality estimates, not breadth; residual **1.76** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 1365` `SE 0.032` `post_SD 0.032` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.629` everywhere, snapshot-time, `PR #4` caveat; `categories` 3 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 12. Finska Mini — `game_id 186279` (2011; n=468 decile D7)
**Underratedness (A):** `resid 1.73` = `adj 7.82` − `E[adj] 6.09`; `SE 0.055` `post_SD 0.055` `z=31.3` `lb_adj 7.71` `resid_lb 1.62`; stability `CV 1.72` `WLS 1.63` `Q3 1.64` `WLS_Q3 1.53` `min_alt 1.53` `cv_diff 0.012` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.73 n=468 SE 0.055 z=31.3 min_alt 1.53 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Action / Dexterity; Party Game` (`n_cats 2`) / `Player Elimination` (`n_mechs 1`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **566** (rank 4068) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D7` vol_band `200-499`
- `num_weights` (attention proxy) **13** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.15` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.387** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.423** (`share_heavy_250plus 0.682`, `share_light_10-24 0.013`, `mean_cnt_pool 631`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.628** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 236.5` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.283** (`6` low-mean 7.51 vs `83` high-mean 7.22; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.607** (`18` low-mean 7.83 vs `198` high-mean 7.22; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.764** (`12` low-mean 7.99 vs `83` high-mean 7.22; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `Action / Dexterity; Party Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.43**, `adj_mean` **7.82** themselves are quality estimates, not breadth; residual **1.73** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 468` `SE 0.055` `post_SD 0.055` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.628` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 13. Age of Rail: South Africa — `game_id 97683` (2011; n=277 decile D5)
**Underratedness (A):** `resid 1.73` = `adj 8.73` − `E[adj] 7.00`; `SE 0.072` `post_SD 0.071` `z=24.1` `lb_adj 8.59` `resid_lb 1.59`; stability `CV 1.74` `WLS 1.60` `Q3 1.70` `WLS_Q3 1.62` `min_alt 1.60` `cv_diff 0.009` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.73 n=277 SE 0.072 z=24.1 min_alt 1.60 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Economic; Trains; Transportation` (`n_cats 3`) / `Action Drafting; Alliances; Auction / Bidding; Stock Holding; Victory Points as a Resource` (`n_mechs 5`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **605** (rank 3481) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D5` vol_band `200-499`
- `num_weights` (attention proxy) **23** (mean 20, up to 8660) — counts attention, not audience breadth; weight `3.00` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.996** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.458** (`share_heavy_250plus 0.776`, `share_light_10-24 0.011`, `mean_cnt_pool 718`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.513** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 198.1` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +2.232** (`3` low-mean 9.33 vs `43` high-mean 7.10; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.817** (`6` low-mean 8.25 vs `127` high-mean 7.43; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.066** (`3` low-mean 7.17 vs `43` high-mean 7.10; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **3** categories `Economic; Trains; Transportation` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.74**, `adj_mean` **8.73** themselves are quality estimates, not breadth; residual **1.73** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 277` `SE 0.072` `post_SD 0.071` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.513` everywhere, snapshot-time, `PR #4` caveat; `categories` 3 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 14. El Grande Decennial Edition — `game_id 147170` (2006; n=978 decile D8)
**Underratedness (A):** `resid 1.72` = `adj 8.78` − `E[adj] 7.05`; `SE 0.038` `post_SD 0.038` `z=45.1` `lb_adj 8.70` `resid_lb 1.65`; stability `CV 1.71` `WLS 1.60` `Q3 1.68` `WLS_Q3 1.53` `min_alt 1.53` `cv_diff 0.014` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.72 n=978 SE 0.038 z=45.1 min_alt 1.53 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Medieval; Political` (`n_cats 2`) / `Area Majority / Influence; Auction / Bidding; Auction: Multiple Lot; Hand Management; Secret Unit Deployment; Simultaneous Action Selection; Turn Order: Auction; Variable Phase Order; Variable Player Powers` (`n_mechs 9`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **1063** (unranked) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D8` vol_band `500-999`
- `num_weights` (attention proxy) **39** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.95` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.448** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.293** (`share_heavy_250plus 0.533`, `share_light_10-24 0.035`, `mean_cnt_pool 419`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.708** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 118.5` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.933** (`34` low-mean 8.86 vs `79` high-mean 7.93; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.583** (`86` low-mean 8.72 vs `287` high-mean 8.13; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.695** (`52` low-mean 8.62 vs `79` high-mean 7.93; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `Medieval; Political` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **8.33**, `adj_mean` **8.78** themselves are quality estimates, not breadth; residual **1.72** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 978` `SE 0.038` `post_SD 0.038` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.708` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 15. Das Motorsportspiel — `game_id 541` (1995; n=381 decile D6)
**Underratedness (A):** `resid 1.63` = `adj 7.89` − `E[adj] 6.26`; `SE 0.061` `post_SD 0.061` `z=26.6` `lb_adj 7.77` `resid_lb 1.51`; stability `CV 1.66` `WLS 1.60` `Q3 1.56` `WLS_Q3 1.53` `min_alt 1.53` `cv_diff 0.029` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.63 n=381 SE 0.061 z=26.6 min_alt 1.53 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Racing; Real-time; Sports` (`n_cats 3`) / `Roll / Spin and Move; Simulation; Track Movement` (`n_mechs 3`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **399** (rank 5127) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D6` vol_band `200-499`
- `num_weights` (attention proxy) **41** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.00` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.443** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.446** (`share_heavy_250plus 0.690`, `share_light_10-24 0.024`, `mean_cnt_pool 697`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.564** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 218.2` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.966** (`9` low-mean 7.89 vs `77` high-mean 6.92; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.670** (`27` low-mean 7.78 vs `170` high-mean 7.11; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.805** (`18` low-mean 7.73 vs `77` high-mean 6.92; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **3** categories `Racing; Real-time; Sports` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.44**, `adj_mean` **7.89** themselves are quality estimates, not breadth; residual **1.63** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 381` `SE 0.061` `post_SD 0.061` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.564` everywhere, snapshot-time, `PR #4` caveat; `categories` 3 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 16. The Extraordinary Adventures of Baron Munchausen — `game_id 2470` (1998; n=379 decile D6)
**Underratedness (A):** `resid 1.62` = `adj 7.55` − `E[adj] 5.92`; `SE 0.061` `post_SD 0.061` `z=26.4` `lb_adj 7.43` `resid_lb 1.50`; stability `CV 1.65` `WLS 1.44` `Q3 1.55` `WLS_Q3 1.38` `min_alt 1.38` `cv_diff 0.024` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.62 n=379 SE 0.061 z=26.4 min_alt 1.38 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Adventure; Novel-based; Party Game` (`n_cats 3`) / `Auction / Bidding; Role Playing; Storytelling` (`n_mechs 3`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **402** (rank 5572) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D6` vol_band `200-499`
- `num_weights` (attention proxy) **28** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.46` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.311** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.259** (`share_heavy_250plus 0.472`, `share_light_10-24 0.042`, `mean_cnt_pool 411`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.731** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 23.3` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.241** (`16` low-mean 8.00 vs `27` high-mean 6.76; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +1.229** (`37` low-mean 8.09 vs `98` high-mean 6.86; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.398** (`21` low-mean 8.16 vs `27` high-mean 6.76; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **3** categories `Adventure; Novel-based; Party Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.23**, `adj_mean` **7.55** themselves are quality estimates, not breadth; residual **1.62** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 379` `SE 0.061` `post_SD 0.061` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.731` everywhere, snapshot-time, `PR #4` caveat; `categories` 3 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 17. My Favourite Things — `game_id 188530` (2015; n=375 decile D6)
**Underratedness (A):** `resid 1.59` = `adj 7.90` − `E[adj] 6.31`; `SE 0.062` `post_SD 0.062` `z=25.8` `lb_adj 7.78` `resid_lb 1.47`; stability `CV 1.58` `WLS 1.61` `Q3 1.53` `WLS_Q3 1.59` `min_alt 1.53` `cv_diff 0.019` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.59 n=375 SE 0.062 z=25.8 min_alt 1.53 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Card Game; Deduction; Humor; Party Game` (`n_cats 4`) / `Trick-taking` (`n_mechs 1`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **1039** (rank 3091) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D6` vol_band `200-499`
- `num_weights` (attention proxy) **21** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.29` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.597** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.443** (`share_heavy_250plus 0.707`, `share_light_10-24 0.011`, `mean_cnt_pool 649`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.533** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 203.7` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.411** (`4` low-mean 7.25 vs `64` high-mean 6.84; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +1.184** (`20` low-mean 8.23 vs `166` high-mean 7.05; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.638** (`16` low-mean 8.48 vs `64` high-mean 6.84; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **4** categories `Card Game; Deduction; Humor; Party Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.31**, `adj_mean` **7.90** themselves are quality estimates, not breadth; residual **1.59** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 375` `SE 0.062` `post_SD 0.062` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.533` everywhere, snapshot-time, `PR #4` caveat; `categories` 4 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 18. Ninety-Nine — `game_id 6688` (1974; n=554 decile D7)
**Underratedness (A):** `resid 1.59` = `adj 7.89` − `E[adj] 6.30`; `SE 0.051` `post_SD 0.051` `z=31.3` `lb_adj 7.79` `resid_lb 1.49`; stability `CV 1.61` `WLS 1.70` `Q3 1.66` `WLS_Q3 1.71` `min_alt 1.61` `cv_diff 0.020` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.59 n=554 SE 0.051 z=31.3 min_alt 1.61 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Card Game` (`n_cats 1`) / `Hand Management; Predictive Bid; Trick-taking` (`n_mechs 3`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **616** (rank 4287) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D7` vol_band `500-999`
- `num_weights` (attention proxy) **38** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.08` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.708** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.496** (`share_heavy_250plus 0.751`, `share_light_10-24 0.011`, `mean_cnt_pool 717`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.226** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 421.6` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +2.147** (`6` low-mean 8.83 vs `115` high-mean 6.69; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.777** (`23` low-mean 7.62 vs `275` high-mean 6.85; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.508** (`17` low-mean 7.19 vs `115` high-mean 6.69; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **1** categories `Card Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.18**, `adj_mean` **7.89** themselves are quality estimates, not breadth; residual **1.59** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 554` `SE 0.051` `post_SD 0.051` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.226` everywhere, snapshot-time, `PR #4` caveat; `categories` 1 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 19. 1844: Schweiz — `game_id 7935` (2003; n=212 decile D4)
**Underratedness (A):** `resid 1.57` = `adj 8.94` − `E[adj] 7.37`; `SE 0.082` `post_SD 0.082` `z=19.2` `lb_adj 8.78` `resid_lb 1.41`; stability `CV 1.58` `WLS 1.53` `Q3 1.58` `WLS_Q3 1.59` `min_alt 1.53` `cv_diff 0.009` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.57 n=212 SE 0.082 z=19.2 min_alt 1.53 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Economic; Trains` (`n_cats 2`) / `Auction / Bidding; Network and Route Building; Stock Holding; Tile Placement` (`n_mechs 4`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **221** (rank 5973) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D4` vol_band `200-499`
- `num_weights` (attention proxy) **21** (mean 20, up to 8660) — counts attention, not audience breadth; weight `4.10` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.816** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.410** (`share_heavy_250plus 0.675`, `share_light_10-24 0.019`, `mean_cnt_pool 649`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.420** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 85.9` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.077** (`4` low-mean 8.25 vs `31` high-mean 7.17; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.609** (`12` low-mean 8.25 vs `87` high-mean 7.64; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.077** (`8` low-mean 8.25 vs `31` high-mean 7.17; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `Economic; Trains` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **8.13**, `adj_mean` **8.94** themselves are quality estimates, not breadth; residual **1.57** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 212` `SE 0.082` `post_SD 0.082` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.420` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 20. Bughouse Chess — `game_id 14188` (1960; n=362 decile D6)
**Underratedness (A):** `resid 1.56` = `adj 7.93` − `E[adj] 6.37`; `SE 0.063` `post_SD 0.063` `z=24.9` `lb_adj 7.81` `resid_lb 1.44`; stability `CV 1.54` `WLS 1.78` `Q3 1.53` `WLS_Q3 1.68` `min_alt 1.53` `cv_diff 0.024` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.56 n=362 SE 0.063 z=24.9 min_alt 1.53 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Abstract Strategy` (`n_cats 1`) / `Grid Movement; Real-Time; Team-Based Game` (`n_mechs 3`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **377** (rank 5581) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D6` vol_band `200-499`
- `num_weights` (attention proxy) **41** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.78` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.618** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.285** (`share_heavy_250plus 0.544`, `share_light_10-24 0.039`, `mean_cnt_pool 484`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.315** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 37.3` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.146** (`14` low-mean 7.71 vs `29` high-mean 6.57; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +1.131** (`46` low-mean 8.03 vs `103` high-mean 6.90; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.607** (`32` low-mean 8.18 vs `29` high-mean 6.57; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **1** categories `Abstract Strategy` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.31**, `adj_mean` **7.93** themselves are quality estimates, not breadth; residual **1.56** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 362` `SE 0.063` `post_SD 0.063` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.315` everywhere, snapshot-time, `PR #4` caveat; `categories` 1 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 21. Time's Up! Academy — `game_id 46158` (2009; n=575 decile D7)
**Underratedness (A):** `resid 1.56` = `adj 7.67` − `E[adj] 6.11`; `SE 0.050` `post_SD 0.050` `z=31.4` `lb_adj 7.57` `resid_lb 1.46`; stability `CV 1.55` `WLS 1.51` `Q3 1.60` `WLS_Q3 1.54` `min_alt 1.51` `cv_diff 0.007` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.56 n=575 SE 0.050 z=31.4 min_alt 1.51 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Humor; Party Game` (`n_cats 2`) / `Acting; Communication Limits; Memory; Team-Based Game` (`n_mechs 4`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **630** (rank 4036) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D7` vol_band `500-999`
- `num_weights` (attention proxy) **22** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.09` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.330** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.270** (`share_heavy_250plus 0.473`, `share_light_10-24 0.035`, `mean_cnt_pool 433`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.673** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 31.0` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.441** (`20` low-mean 7.33 vs `55` high-mean 6.88; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.448** (`69` low-mean 7.60 vs `155` high-mean 7.15; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.828** (`49` low-mean 7.71 vs `55` high-mean 6.88; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `Humor; Party Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.34**, `adj_mean` **7.67** themselves are quality estimates, not breadth; residual **1.56** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 575` `SE 0.050` `post_SD 0.050` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.673` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 22. Tumblin-Dice Medium — `game_id 62814` (2008; n=215 decile D4)
**Underratedness (A):** `resid 1.56` = `adj 7.62` − `E[adj] 6.06`; `SE 0.081` `post_SD 0.081` `z=19.1` `lb_adj 7.46` `resid_lb 1.40`; stability `CV 1.56` `WLS 1.39` `Q3 1.58` `WLS_Q3 1.46` `min_alt 1.39` `cv_diff 0.002` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.56 n=215 SE 0.081 z=19.1 min_alt 1.39 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Action / Dexterity; Dice` (`n_cats 2`) / `Dice Rolling` (`n_mechs 1`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **233** (rank 7196) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D4` vol_band `200-499`
- `num_weights` (attention proxy) **13** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.00` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.344** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.372** (`share_heavy_250plus 0.600`, `share_light_10-24 0.028`, `mean_cnt_pool 542`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.581** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 74.7` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.902** (`6` low-mean 8.67 vs `36` high-mean 6.76; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.758** (`12` low-mean 7.79 vs `80` high-mean 7.03; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.152** (`6` low-mean 6.92 vs `36` high-mean 6.76; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `Action / Dexterity; Dice` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.27**, `adj_mean` **7.62** themselves are quality estimates, not breadth; residual **1.56** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 215` `SE 0.081` `post_SD 0.081` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.581` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 23. Heart of Crown: Fairy Garden — `game_id 156372` (2013; n=305 decile D6)
**Underratedness (A):** `resid 1.56` = `adj 8.43` − `E[adj] 6.88`; `SE 0.068` `post_SD 0.068` `z=22.8` `lb_adj 8.30` `resid_lb 1.42`; stability `CV 1.56` `WLS 1.54` `Q3 1.53` `WLS_Q3 1.54` `min_alt 1.53` `cv_diff 0.003` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.56 n=305 SE 0.068 z=22.8 min_alt 1.53 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Card Game; Fantasy` (`n_cats 2`) / `Deck, Bag, and Pool Building; Hand Management; Open Drafting; Variable Player Powers` (`n_mechs 4`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **350** (rank 4946) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D6` vol_band `200-499`
- `num_weights` (attention proxy) **14** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.57` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.421** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.213** (`share_heavy_250plus 0.439`, `share_light_10-24 0.056`, `mean_cnt_pool 479`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.702** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 19.8` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.340** (`17` low-mean 8.41 vs `32` high-mean 7.07; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +1.027** (`43` low-mean 8.54 vs `65` high-mean 7.52; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.559** (`26` low-mean 8.63 vs `32` high-mean 7.07; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `Card Game; Fantasy` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **8.01**, `adj_mean` **8.43** themselves are quality estimates, not breadth; residual **1.56** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 305` `SE 0.068` `post_SD 0.068` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.702` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 24. Time's Up! Edición Amarilla — `game_id 38713` (2008; n=1622 decile D9)
**Underratedness (A):** `resid 1.55` = `adj 7.78` − `E[adj] 6.23`; `SE 0.030` `post_SD 0.030` `z=52.1` `lb_adj 7.72` `resid_lb 1.49`; stability `CV 1.54` `WLS 1.48` `Q3 1.58` `WLS_Q3 1.47` `min_alt 1.47` `cv_diff 0.008` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.55 n=1622 SE 0.030 z=52.1 min_alt 1.47 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Humor; Party Game` (`n_cats 2`) / `Acting; Communication Limits; Memory; Team-Based Game` (`n_mechs 4`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **1950** (rank 1550) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D9` vol_band `1k-2.5k`
- `num_weights` (attention proxy) **54** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.07` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.231** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.162** (`share_heavy_250plus 0.352`, `share_light_10-24 0.052`, `mean_cnt_pool 286`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.720** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 29.6` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.060** (`85` low-mean 7.85 vs `62` high-mean 6.78; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.492** (`258` low-mean 7.71 vs `263` high-mean 7.22; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.854** (`173` low-mean 7.64 vs `62` high-mean 6.78; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `Humor; Party Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.55**, `adj_mean` **7.78** themselves are quality estimates, not breadth; residual **1.55** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 1622` `SE 0.030` `post_SD 0.030` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.720` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 25. Tintas — `game_id 207951` (2016; n=312 decile D6)
**Underratedness (A):** `resid 1.52` = `adj 8.11` − `E[adj] 6.59`; `SE 0.068` `post_SD 0.067` `z=22.5` `lb_adj 7.98` `resid_lb 1.39`; stability `CV 1.53` `WLS 1.43` `Q3 1.50` `WLS_Q3 1.44` `min_alt 1.43` `cv_diff 0.008` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.52 n=312 SE 0.068 z=22.5 min_alt 1.43 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Abstract Strategy` (`n_cats 1`) / `—` (`n_mechs 0`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **363** (rank 5082) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D6` vol_band `200-499`
- `num_weights` (attention proxy) **12** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.42` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.505** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.442** (`share_heavy_250plus 0.663`, `share_light_10-24 0.029`, `mean_cnt_pool 729`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.567** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 167.3` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.888** (`9` low-mean 8.17 vs `62` high-mean 7.28; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.757** (`24` low-mean 8.04 vs `138` high-mean 7.29; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.688** (`15` low-mean 7.97 vs `62` high-mean 7.28; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **1** categories `Abstract Strategy` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.60**, `adj_mean` **8.11** themselves are quality estimates, not breadth; residual **1.52** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 312` `SE 0.068` `post_SD 0.067` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.567` everywhere, snapshot-time, `PR #4` caveat; `categories` 1 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 26. Charms — `game_id 172844` (2014; n=254 decile D5)
**Underratedness (A):** `resid 1.52` = `adj 8.14` − `E[adj] 6.62`; `SE 0.075` `post_SD 0.075` `z=20.3` `lb_adj 7.99` `resid_lb 1.37`; stability `CV 1.53` `WLS 1.34` `Q3 1.51` `WLS_Q3 1.38` `min_alt 1.34` `cv_diff 0.011` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.52 n=254 SE 0.075 z=20.3 min_alt 1.34 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Card Game` (`n_cats 1`) / `Predictive Bid; Trick-taking` (`n_mechs 2`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **347** (rank 5832) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D5` vol_band `200-499`
- `num_weights` (attention proxy) **11** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.09` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.775** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.571** (`share_heavy_250plus 0.850`, `share_light_10-24 0.000`, `mean_cnt_pool 794`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.555** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 298.8` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- Heavy vs light rater means on same game — **no overlapping heavy/light groups available** for this game in the three `within_game_diffs_active*` slices (requires ≥30? per band). Absence is not evidence of niche; Low volume is *less* evidence, not more.
- `game_tags` category breadth **1** categories `Card Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.36**, `adj_mean` **8.14** themselves are quality estimates, not breadth; residual **1.52** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 254` `SE 0.075` `post_SD 0.075` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.555` everywhere, snapshot-time, `PR #4` caveat; `categories` 1 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 27. Breaking Away — `game_id 2981` (1991; n=460 decile D7)
**Underratedness (A):** `resid 1.51` = `adj 7.89` − `E[adj] 6.37`; `SE 0.056` `post_SD 0.056` `z=27.2` `lb_adj 7.78` `resid_lb 1.40`; stability `CV 1.52` `WLS 1.54` `Q3 1.42` `WLS_Q3 1.44` `min_alt 1.42` `cv_diff 0.010` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.51 n=460 SE 0.056 z=27.2 min_alt 1.42 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Abstract Strategy; Racing; Sports` (`n_cats 3`) / `—` (`n_mechs 0`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **472** (rank 4795) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D7` vol_band `200-499`
- `num_weights` (attention proxy) **59** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.27` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.578** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.511** (`share_heavy_250plus 0.750`, `share_light_10-24 0.013`, `mean_cnt_pool 760`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.461** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 411.9` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff -1.414** (`6` low-mean 5.75 vs `111` high-mean 7.16; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.034** (`20` low-mean 7.36 vs `235` high-mean 7.32; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.882** (`14` low-mean 8.05 vs `111` high-mean 7.16; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **3** categories `Abstract Strategy; Racing; Sports` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.31**, `adj_mean` **7.89** themselves are quality estimates, not breadth; residual **1.51** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 460` `SE 0.056` `post_SD 0.056` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.461` everywhere, snapshot-time, `PR #4` caveat; `categories` 3 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 28. The Quiet Year — `game_id 161880` (2013; n=407 decile D6)
**Underratedness (A):** `resid 1.51` = `adj 7.93` − `E[adj] 6.43`; `SE 0.059` `post_SD 0.059` `z=25.5` `lb_adj 7.82` `resid_lb 1.39`; stability `CV 1.52` `WLS 1.43` `Q3 1.45` `WLS_Q3 1.38` `min_alt 1.38` `cv_diff 0.013` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.51 n=407 SE 0.059 z=25.5 min_alt 1.38 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Card Game; Print & Play` (`n_cats 2`) / `Drawing; Open Drafting; Role Playing; Storytelling` (`n_mechs 4`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **501** (rank 4429) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D6` vol_band `200-499`
- `num_weights` (attention proxy) **13** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.38` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.365** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.150** (`share_heavy_250plus 0.337`, `share_light_10-24 0.088`, `mean_cnt_pool 296`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.658** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 12.2` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.593** (`36` low-mean 8.33 vs `16` high-mean 6.74; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.866** (`88` low-mean 7.97 vs `61` high-mean 7.11; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.986** (`52` low-mean 7.73 vs `16` high-mean 6.74; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `Card Game; Print & Play` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.57**, `adj_mean` **7.93** themselves are quality estimates, not breadth; residual **1.51** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 407` `SE 0.059` `post_SD 0.059` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.658` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 29. Clank! Legacy 2: Acquisitions Incorporated – Darkest Magic — `game_id 383010` (2024; n=234 decile D5)
**Underratedness (A):** `resid 1.51` = `adj 9.39` − `E[adj] 7.88`; `SE 0.078` `post_SD 0.078` `z=19.3` `lb_adj 9.24` `resid_lb 1.35`; stability `CV 1.52` `WLS 1.55` `Q3 1.41` `WLS_Q3 1.58` `min_alt 1.41` `cv_diff 0.008` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.51 n=234 SE 0.078 z=19.3 min_alt 1.41 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Adventure; Fantasy; Miniatures` (`n_cats 3`) / `Deck, Bag, and Pool Building; Legacy Game; Push Your Luck; Scenario / Mission / Campaign Game` (`n_mechs 4`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **1126** (rank 1484) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D5` vol_band `200-499`
- `num_weights` (attention proxy) **16** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.75` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.305** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.239** (`share_heavy_250plus 0.526`, `share_light_10-24 0.047`, `mean_cnt_pool 367`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.782** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 20.7` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.752** (`11` low-mean 9.64 vs `13` high-mean 8.88; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.858** (`26` low-mean 9.60 vs `56` high-mean 8.75; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.695** (`15` low-mean 9.58 vs `13` high-mean 8.88; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **3** categories `Adventure; Fantasy; Miniatures` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **9.08**, `adj_mean` **9.39** themselves are quality estimates, not breadth; residual **1.51** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 234` `SE 0.078` `post_SD 0.078` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.782` everywhere, snapshot-time, `PR #4` caveat; `categories` 3 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 30. Time's Up! Deluxe — `game_id 37141` (2008; n=1024 decile D8)
**Underratedness (A):** `resid 1.50` = `adj 7.84` − `E[adj] 6.34`; `SE 0.037` `post_SD 0.037` `z=40.2` `lb_adj 7.76` `resid_lb 1.43`; stability `CV 1.49` `WLS 1.48` `Q3 1.61` `WLS_Q3 1.55` `min_alt 1.48` `cv_diff 0.011` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.50 n=1024 SE 0.037 z=40.2 min_alt 1.48 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Electronic; Humor; Party Game` (`n_cats 3`) / `Acting; Communication Limits; Memory; Team-Based Game` (`n_mechs 4`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **1053** (rank 2678) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D8` vol_band `1k-2.5k`
- `num_weights` (attention proxy) **42** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.31` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.386** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.313** (`share_heavy_250plus 0.557`, `share_light_10-24 0.022`, `mean_cnt_pool 482`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.578** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 160.0` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.282** (`23` low-mean 8.21 vs `114` high-mean 6.93; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.666** (`69` low-mean 7.85 vs `321` high-mean 7.18; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.739** (`46` low-mean 7.67 vs `114` high-mean 6.93; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **3** categories `Electronic; Humor; Party Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.45**, `adj_mean` **7.84** themselves are quality estimates, not breadth; residual **1.50** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 1024` `SE 0.037` `post_SD 0.037` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.578` everywhere, snapshot-time, `PR #4` caveat; `categories` 3 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 31. History Maker Baseball — `game_id 141067` (2013; n=208 decile D4)
**Underratedness (A):** `resid 1.49` = `adj 8.23` − `E[adj] 6.73`; `SE 0.083` `post_SD 0.082` `z=18.0` `lb_adj 8.06` `resid_lb 1.33`; stability `CV 1.48` `WLS 1.39` `Q3 1.53` `WLS_Q3 1.48` `min_alt 1.39` `cv_diff 0.012` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.49 n=208 SE 0.083 z=18.0 min_alt 1.39 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Sports` (`n_cats 1`) / `Dice Rolling; Paper-and-Pencil; Simulation; Solo / Solitaire Game` (`n_mechs 4`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **268** (rank 5867) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D4` vol_band `200-499`
- `num_weights` (attention proxy) **15** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.20` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.043** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.149** (`share_heavy_250plus 0.327`, `share_light_10-24 0.154`, `mean_cnt_pool 330`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.861** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 44.1` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.132** (`32` low-mean 8.33 vs `14` high-mean 8.20; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.789** (`63` low-mean 8.37 vs `31` high-mean 7.58; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.223** (`31` low-mean 8.42 vs `14` high-mean 8.20; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **1** categories `Sports` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **8.18**, `adj_mean` **8.23** themselves are quality estimates, not breadth; residual **1.49** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 208` `SE 0.083` `post_SD 0.082` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.861` everywhere, snapshot-time, `PR #4` caveat; `categories` 1 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 32. Time's Up! Édition purple — `game_id 33495` (2007; n=356 decile D6)
**Underratedness (A):** `resid 1.49` = `adj 7.39` − `E[adj] 5.90`; `SE 0.063` `post_SD 0.063` `z=23.5` `lb_adj 7.26` `resid_lb 1.36`; stability `CV 1.49` `WLS 1.42` `Q3 1.43` `WLS_Q3 1.39` `min_alt 1.39` `cv_diff 0.006` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.49 n=356 SE 0.063 z=23.5 min_alt 1.39 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Humor; Memory; Party Game` (`n_cats 3`) / `Acting; Communication Limits; Memory; Team-Based Game` (`n_mechs 4`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **374** (rank 5809) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D6` vol_band `200-499`
- `num_weights` (attention proxy) **23** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.09` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.208** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.256** (`share_heavy_250plus 0.441`, `share_light_10-24 0.053`, `mean_cnt_pool 408`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.697** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 10.3` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.060** (`19` low-mean 6.88 vs `30` high-mean 6.82; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff -0.042** (`47` low-mean 7.00 vs `91` high-mean 7.05; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.261** (`28` low-mean 7.08 vs `30` high-mean 6.82; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **3** categories `Humor; Memory; Party Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.18**, `adj_mean` **7.39** themselves are quality estimates, not breadth; residual **1.49** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 356` `SE 0.063` `post_SD 0.063` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.697` everywhere, snapshot-time, `PR #4` caveat; `categories` 3 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 33. 1841: Railways in Northern Italy — `game_id 1447` (1994; n=343 decile D6)
**Underratedness (A):** `resid 1.46` = `adj 8.79` − `E[adj] 7.33`; `SE 0.064` `post_SD 0.064` `z=22.7` `lb_adj 8.67` `resid_lb 1.34`; stability `CV 1.44` `WLS 1.49` `Q3 1.39` `WLS_Q3 1.45` `min_alt 1.39` `cv_diff 0.021` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.46 n=343 SE 0.064 z=22.7 min_alt 1.39 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Economic; Post-Napoleonic; Trains; Transportation` (`n_cats 4`) / `Network and Route Building; Stock Holding; Tile Placement; Victory Points as a Resource` (`n_mechs 4`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **375** (rank 4571) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D6` vol_band `200-499`
- `num_weights` (attention proxy) **46** (mean 20, up to 8660) — counts attention, not audience breadth; weight `4.39` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.920** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.332** (`share_heavy_250plus 0.630`, `share_light_10-24 0.020`, `mean_cnt_pool 590`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.455** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 108.4` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.925** (`7` low-mean 9.00 vs `50` high-mean 7.07; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.891** (`23` low-mean 8.39 vs `114` high-mean 7.50; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.050** (`16` low-mean 8.12 vs `50` high-mean 7.07; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **4** categories `Economic; Post-Napoleonic; Trains; Transportation` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.87**, `adj_mean` **8.79** themselves are quality estimates, not breadth; residual **1.46** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 343` `SE 0.064` `post_SD 0.064` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.455` everywhere, snapshot-time, `PR #4` caveat; `categories` 4 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 34. Telestrations: 12 Player Party Pack — `game_id 153016` (2011; n=3141 decile D10)
**Underratedness (A):** `resid 1.46` = `adj 7.96` − `E[adj] 6.51`; `SE 0.021` `post_SD 0.021` `z=68.5` `lb_adj 7.92` `resid_lb 1.42`; stability `CV 1.44` `WLS 1.42` `Q3 1.56` `WLS_Q3 1.44` `min_alt 1.42` `cv_diff 0.021` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.46 n=3141 SE 0.021 z=68.5 min_alt 1.42 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Humor; Party Game; Real-time` (`n_cats 3`) / `Drawing; Line Drawing; Paper-and-Pencil` (`n_mechs 3`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **3505** (rank 757) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D10` vol_band `2.5k-5k`
- `num_weights` (attention proxy) **52** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.06` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.242** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.172** (`share_heavy_250plus 0.384`, `share_light_10-24 0.048`, `mean_cnt_pool 308`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.696** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 29.6` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.172** (`151` low-mean 8.29 vs `152` high-mean 7.12; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.762** (`464` low-mean 8.10 vs `539` high-mean 7.33; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.878** (`313` low-mean 8.00 vs `152` high-mean 7.12; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **3** categories `Humor; Party Game; Real-time` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.72**, `adj_mean` **7.96** themselves are quality estimates, not breadth; residual **1.46** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 3141` `SE 0.021` `post_SD 0.021` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.696` everywhere, snapshot-time, `PR #4` caveat; `categories` 3 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 35. Carcassonne Big Box 2 — `game_id 141008` (2008; n=454 decile D7)
**Underratedness (A):** `resid 1.46` = `adj 7.89` − `E[adj] 6.44`; `SE 0.056` `post_SD 0.056` `z=26.0` `lb_adj 7.78` `resid_lb 1.35`; stability `CV 1.46` `WLS 1.28` `Q3 1.35` `WLS_Q3 1.21` `min_alt 1.21` `cv_diff 0.003` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.46 n=454 SE 0.056 z=26.0 min_alt 1.21 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `City Building; Medieval` (`n_cats 2`) / `Area Majority / Influence; Tile Placement` (`n_mechs 2`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **503** (unranked) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D7` vol_band `200-499`
- `num_weights` (attention proxy) **19** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.00` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.179** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.148** (`share_heavy_250plus 0.275`, `share_light_10-24 0.115`, `mean_cnt_pool 263`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.811** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 54.3` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.507** (`52` low-mean 7.97 vs `25` high-mean 7.46; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.649** (`120` low-mean 7.99 vs `67` high-mean 7.34; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.545** (`68` low-mean 8.01 vs `25` high-mean 7.46; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `City Building; Medieval` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.72**, `adj_mean` **7.89** themselves are quality estimates, not breadth; residual **1.46** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 454` `SE 0.056` `post_SD 0.056` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.811` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 36. Wie ich die Welt sehe... — `game_id 13089` (2004; n=366 decile D6)
**Underratedness (A):** `resid 1.45` = `adj 7.23` − `E[adj] 5.78`; `SE 0.062` `post_SD 0.062` `z=23.2` `lb_adj 7.11` `resid_lb 1.32`; stability `CV 1.43` `WLS 1.44` `Q3 1.38` `WLS_Q3 1.40` `min_alt 1.38` `cv_diff 0.011` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.45 n=366 SE 0.062 z=23.2 min_alt 1.38 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Card Game; Humor; Party Game; Word Game` (`n_cats 4`) / `—` (`n_mechs 0`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **380** (rank 6787) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D6` vol_band `200-499`
- `num_weights` (attention proxy) **23** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.13` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.436** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.344** (`share_heavy_250plus 0.598`, `share_light_10-24 0.005`, `mean_cnt_pool 532`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.598** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 98.4` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-49_vs_500plus` **diff +0.349** (`15` low-mean 6.90 vs `126` high-mean 6.55; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.102** (`13` low-mean 6.81 vs `52` high-mean 6.71; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **4** categories `Card Game; Humor; Party Game; Word Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **6.79**, `adj_mean` **7.23** themselves are quality estimates, not breadth; residual **1.45** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 366` `SE 0.062` `post_SD 0.062` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.598` everywhere, snapshot-time, `PR #4` caveat; `categories` 4 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 37. Eleusis — `game_id 5217` (1956; n=216 decile D5)
**Underratedness (A):** `resid 1.44` = `adj 7.79` − `E[adj] 6.35`; `SE 0.081` `post_SD 0.081` `z=17.8` `lb_adj 7.63` `resid_lb 1.28`; stability `CV 1.51` `WLS 1.72` `Q3 1.49` `WLS_Q3 1.71` `min_alt 1.49` `cv_diff 0.061` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.44 n=216 SE 0.081 z=17.8 min_alt 1.49 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Card Game; Deduction; Educational` (`n_cats 3`) / `Induction; Pattern Recognition` (`n_mechs 2`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **239** (rank 7241) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D5` vol_band `200-499`
- `num_weights` (attention proxy) **16** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.88` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.506** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.435** (`share_heavy_250plus 0.685`, `share_light_10-24 0.023`, `mean_cnt_pool 702`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.426** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 110.6` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.575** (`5` low-mean 8.14 vs `39` high-mean 6.57; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +1.231** (`11` low-mean 8.25 vs `94` high-mean 7.01; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.768** (`6` low-mean 8.33 vs `39` high-mean 6.57; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **3** categories `Card Game; Deduction; Educational` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.28**, `adj_mean` **7.79** themselves are quality estimates, not breadth; residual **1.44** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 216` `SE 0.081` `post_SD 0.081` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.426` everywhere, snapshot-time, `PR #4` caveat; `categories` 3 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 38. Urbino — `game_id 237009` (2017; n=207 decile D4)
**Underratedness (A):** `resid 1.44` = `adj 8.44` − `E[adj] 7.00`; `SE 0.083` `post_SD 0.083` `z=17.4` `lb_adj 8.28` `resid_lb 1.28`; stability `CV 1.44` `WLS 1.44` `Q3 1.46` `WLS_Q3 1.53` `min_alt 1.44` `cv_diff 0.001` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.44 n=207 SE 0.083 z=17.4 min_alt 1.44 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Abstract Strategy; City Building` (`n_cats 2`) / `Area Majority / Influence; Pattern Building; Square Grid` (`n_mechs 3`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **256** (rank 5646) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D4` vol_band `200-499`
- `num_weights` (attention proxy) **9** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.11` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.488** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.386** (`share_heavy_250plus 0.638`, `share_light_10-24 0.019`, `mean_cnt_pool 758`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.662** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 114.4` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.087** (`4` low-mean 8.25 vs `46` high-mean 7.16; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.781** (`14` low-mean 8.18 vs `80` high-mean 7.40; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.987** (`10` low-mean 8.15 vs `46` high-mean 7.16; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `Abstract Strategy; City Building` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.96**, `adj_mean` **8.44** themselves are quality estimates, not breadth; residual **1.44** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 207` `SE 0.083` `post_SD 0.083` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.662` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 39. 1849: The Game of Sicilian Railways — `game_id 3097` (1998; n=942 decile D8)
**Underratedness (A):** `resid 1.44` = `adj 8.92` − `E[adj] 7.49`; `SE 0.039` `post_SD 0.039` `z=37.0` `lb_adj 8.85` `resid_lb 1.36`; stability `CV 1.44` `WLS 1.40` `Q3 1.38` `WLS_Q3 1.33` `min_alt 1.33` `cv_diff 0.001` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.44 n=942 SE 0.039 z=37.0 min_alt 1.33 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Economic; Post-Napoleonic; Trains; Transportation` (`n_cats 4`) / `Auction / Bidding; Investment; Network and Route Building; Stock Holding; Tile Placement` (`n_mechs 5`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **1057** (rank 1865) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D8` vol_band `500-999`
- `num_weights` (attention proxy) **43** (mean 20, up to 8660) — counts attention, not audience breadth; weight `4.16` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.833** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.288** (`share_heavy_250plus 0.584`, `share_light_10-24 0.016`, `mean_cnt_pool 469`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.588** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 191.9` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.658** (`15` low-mean 7.98 vs `74` high-mean 7.32; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.503** (`49` low-mean 8.27 vs `271` high-mean 7.77; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.075** (`34` low-mean 8.40 vs `74` high-mean 7.32; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **4** categories `Economic; Post-Napoleonic; Trains; Transportation` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **8.09**, `adj_mean` **8.92** themselves are quality estimates, not breadth; residual **1.44** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 942` `SE 0.039` `post_SD 0.039` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.588` everywhere, snapshot-time, `PR #4` caveat; `categories` 4 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 40. Strat-O-Matic Baseball — `game_id 2251` (1962; n=1074 decile D8)
**Underratedness (A):** `resid 1.43` = `adj 7.92` − `E[adj] 6.49`; `SE 0.036` `post_SD 0.036` `z=39.2` `lb_adj 7.85` `resid_lb 1.36`; stability `CV 1.40` `WLS 1.64` `Q3 1.57` `WLS_Q3 1.65` `min_alt 1.40` `cv_diff 0.032` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.43 n=1074 SE 0.036 z=39.2 min_alt 1.40 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Sports` (`n_cats 1`) / `Dice Rolling; Simulation; Solo / Solitaire Game` (`n_mechs 3`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **1279** (rank 2183) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D8` vol_band `1k-2.5k`
- `num_weights` (attention proxy) **110** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.39` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.239** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.160** (`share_heavy_250plus 0.345`, `share_light_10-24 0.120`, `mean_cnt_pool 302`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.723** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 70.3` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.950** (`129` low-mean 8.44 vs `57` high-mean 6.49; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +1.443** (`255` low-mean 8.29 vs `172` high-mean 6.85; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.648** (`126` low-mean 8.14 vs `57` high-mean 6.49; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **1** categories `Sports` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.68**, `adj_mean` **7.92** themselves are quality estimates, not breadth; residual **1.43** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 1074` `SE 0.036` `post_SD 0.036` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.723` everywhere, snapshot-time, `PR #4` caveat; `categories` 1 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 41. Dynasty League Baseball Powered by Pursue the Pennant — `game_id 7290` (1985; n=223 decile D5)
**Underratedness (A):** `resid 1.42` = `adj 7.84` − `E[adj] 6.42`; `SE 0.080` `post_SD 0.080` `z=17.8` `lb_adj 7.69` `resid_lb 1.27`; stability `CV 1.40` `WLS 1.42` `Q3 1.44` `WLS_Q3 1.47` `min_alt 1.40` `cv_diff 0.019` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.42 n=223 SE 0.080 z=17.8 min_alt 1.40 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Sports` (`n_cats 1`) / `Simulation` (`n_mechs 1`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **273** (rank 6585) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D5` vol_band `200-499`
- `num_weights` (attention proxy) **28** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.54` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.172** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.197** (`share_heavy_250plus 0.381`, `share_light_10-24 0.094`, `mean_cnt_pool 349`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.682** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 6.2` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.310** (`21` low-mean 8.52 vs `14` high-mean 7.21; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +1.758** (`48` low-mean 8.61 vs `44` high-mean 6.85; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.460** (`27` low-mean 8.67 vs `14` high-mean 7.21; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **1** categories `Sports` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.67**, `adj_mean` **7.84** themselves are quality estimates, not breadth; residual **1.42** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 223` `SE 0.080` `post_SD 0.080` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.682` everywhere, snapshot-time, `PR #4` caveat; `categories` 1 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 42. It's a Wonderful World: Heritage Edition — `game_id 295260` (2019; n=921 decile D8)
**Underratedness (A):** `resid 1.40` = `adj 8.65` − `E[adj] 7.24`; `SE 0.039` `post_SD 0.039` `z=35.7` `lb_adj 8.57` `resid_lb 1.33`; stability `CV 1.40` `WLS 1.40` `Q3 1.36` `WLS_Q3 1.35` `min_alt 1.35` `cv_diff 0.005` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.40 n=921 SE 0.039 z=35.7 min_alt 1.35 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Card Game; Civilization; Science Fiction` (`n_cats 3`) / `Open Drafting; Scenario / Mission / Campaign Game; Set Collection` (`n_mechs 3`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **995** (unranked) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D8` vol_band `500-999`
- `num_weights` (attention proxy) **40** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.33` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.275** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.219** (`share_heavy_250plus 0.469`, `share_light_10-24 0.038`, `mean_cnt_pool 374`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.800** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 38.8` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.450** (`35` low-mean 9.16 vs `72` high-mean 7.71; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.909** (`101` low-mean 8.84 vs `202` high-mean 7.93; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.956** (`66` low-mean 8.66 vs `72` high-mean 7.71; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **3** categories `Card Game; Civilization; Science Fiction` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **8.37**, `adj_mean` **8.65** themselves are quality estimates, not breadth; residual **1.40** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 921` `SE 0.039` `post_SD 0.039` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.800` everywhere, snapshot-time, `PR #4` caveat; `categories` 3 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 43. Dutch InterCity — `game_id 1278` (1999; n=209 decile D4)
**Underratedness (A):** `resid 1.40` = `adj 7.91` − `E[adj] 6.52`; `SE 0.083` `post_SD 0.082` `z=16.9` `lb_adj 7.75` `resid_lb 1.23`; stability `CV 1.40` `WLS 1.22` `Q3 1.39` `WLS_Q3 1.28` `min_alt 1.22` `cv_diff 0.009` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.40 n=209 SE 0.083 z=16.9 min_alt 1.22 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Trains` (`n_cats 1`) / `Auction / Bidding; Simultaneous Action Selection; Stock Holding` (`n_mechs 3`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **275** (rank 7383) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D4` vol_band `200-499`
- `num_weights` (attention proxy) **11** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.45` if weighed
- `is_reimplementation` **True** → Santa Claus Takes the Intercity — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.979** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.450** (`share_heavy_250plus 0.794`, `share_light_10-24 0.005`, `mean_cnt_pool 777`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.459** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 160.2` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-49_vs_500plus` **diff +1.238** (`3` low-mean 8.00 vs `94` high-mean 6.76; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **1** categories `Trains` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **6.93**, `adj_mean` **7.91** themselves are quality estimates, not breadth; residual **1.40** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 209` `SE 0.083` `post_SD 0.082` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.459` everywhere, snapshot-time, `PR #4` caveat; `categories` 1 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 44. Sub Terra: Collector's Edition — `game_id 215946` (2017; n=333 decile D6)
**Underratedness (A):** `resid 1.38` = `adj 7.87` − `E[adj] 6.50`; `SE 0.065` `post_SD 0.065` `z=21.0` `lb_adj 7.75` `resid_lb 1.25`; stability `CV 1.35` `WLS 1.36` `Q3 1.34` `WLS_Q3 1.34` `min_alt 1.34` `cv_diff 0.026` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.38 n=333 SE 0.065 z=21.0 min_alt 1.34 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Exploration; Horror` (`n_cats 2`) / `Action Points; Cooperative Game; Grid Movement; Modular Board; Network and Route Building; Pick-up and Deliver; Push Your Luck; Variable Player Powers` (`n_mechs 8`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **364** (unranked) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D6` vol_band `200-499`
- `num_weights` (attention proxy) **7** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.71` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.094** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.147** (`share_heavy_250plus 0.297`, `share_light_10-24 0.060`, `mean_cnt_pool 296`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.760** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 18.0` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.242** (`20` low-mean 8.32 vs `19` high-mean 7.08; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +1.040** (`53` low-mean 8.35 vs `49` high-mean 7.31; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.289** (`33` low-mean 8.37 vs `19` high-mean 7.08; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `Exploration; Horror` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.78**, `adj_mean` **7.87** themselves are quality estimates, not breadth; residual **1.38** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 333` `SE 0.065` `post_SD 0.065` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.760` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 45. JamSumo — `game_id 165595` (2014; n=350 decile D6)
**Underratedness (A):** `resid 1.36` = `adj 7.74` − `E[adj] 6.38`; `SE 0.064` `post_SD 0.064` `z=21.3` `lb_adj 7.61` `resid_lb 1.24`; stability `CV 1.37` `WLS 1.24` `Q3 1.32` `WLS_Q3 1.22` `min_alt 1.22` `cv_diff 0.011` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.36 n=350 SE 0.064 z=21.3 min_alt 1.22 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Action / Dexterity; Dice` (`n_cats 2`) / `Flicking` (`n_mechs 1`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **381** (rank 5586) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D6` vol_band `200-499`
- `num_weights` (attention proxy) **6** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.17` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.456** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.526** (`share_heavy_250plus 0.791`, `share_light_10-24 0.011`, `mean_cnt_pool 781`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.540** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 344.2` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.980** (`4` low-mean 7.75 vs `84` high-mean 6.77; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +1.155** (`13` low-mean 8.15 vs `184` high-mean 7.00; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.564** (`9` low-mean 8.33 vs `84` high-mean 6.77; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `Action / Dexterity; Dice` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.28**, `adj_mean` **7.74** themselves are quality estimates, not breadth; residual **1.36** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 350` `SE 0.064` `post_SD 0.064` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.540` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 46. Cartographers Heroes: Collector's Edition — `game_id 322045` (2021; n=706 decile D8)
**Underratedness (A):** `resid 1.36` = `adj 8.43` − `E[adj] 7.08`; `SE 0.045` `post_SD 0.045` `z=30.2` `lb_adj 8.35` `resid_lb 1.27`; stability `CV 1.39` `WLS 1.48` `Q3 1.32` `WLS_Q3 1.46` `min_alt 1.32` `cv_diff 0.031` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.36 n=706 SE 0.045 z=30.2 min_alt 1.32 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Fantasy; Territory Building` (`n_cats 2`) / `Bingo; Grid Coverage; Line Drawing; Paper-and-Pencil; Solo / Solitaire Game` (`n_mechs 5`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **819** (unranked) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D8` vol_band `500-999`
- `num_weights` (attention proxy) **11** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.09` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.293** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.249** (`share_heavy_250plus 0.472`, `share_light_10-24 0.027`, `mean_cnt_pool 397`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.851** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 47.8` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.942** (`19` low-mean 8.48 vs `62` high-mean 7.54; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.368** (`70` low-mean 8.25 vs `176` high-mean 7.89; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.626** (`51` low-mean 8.17 vs `62` high-mean 7.54; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `Fantasy; Territory Building` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **8.14**, `adj_mean` **8.43** themselves are quality estimates, not breadth; residual **1.36** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 706` `SE 0.045` `post_SD 0.045` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.851` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 47. luz — `game_id 252657` (2014; n=228 decile D5)
**Underratedness (A):** `resid 1.36` = `adj 8.08` − `E[adj] 6.72`; `SE 0.079` `post_SD 0.079` `z=17.1` `lb_adj 7.92` `resid_lb 1.20`; stability `CV 1.38` `WLS 1.26` `Q3 1.38` `WLS_Q3 1.32` `min_alt 1.26` `cv_diff 0.021` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.36 n=228 SE 0.079 z=17.1 min_alt 1.26 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Card Game` (`n_cats 1`) / `Predictive Bid; Trick-taking` (`n_mechs 2`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **283** (rank 6664) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D5` vol_band `200-499`
- `num_weights` (attention proxy) **2** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.00` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.780** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.596** (`share_heavy_250plus 0.825`, `share_light_10-24 0.009`, `mean_cnt_pool 874`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.469** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 310.1` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-49_vs_500plus` **diff +0.710** (`6` low-mean 7.92 vs `136` high-mean 7.21; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.602** (`4` low-mean 7.88 vs `64` high-mean 7.27; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **1** categories `Card Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.30**, `adj_mean` **8.08** themselves are quality estimates, not breadth; residual **1.36** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 228` `SE 0.079` `post_SD 0.079` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.469` everywhere, snapshot-time, `PR #4` caveat; `categories` 1 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 48. Terra Mystica: Big Box — `game_id 181289` (2015; n=447 decile D7)
**Underratedness (A):** `resid 1.35` = `adj 8.89` − `E[adj] 7.54`; `SE 0.056` `post_SD 0.056` `z=23.9` `lb_adj 8.78` `resid_lb 1.24`; stability `CV 1.38` `WLS 1.34` `Q3 1.25` `WLS_Q3 1.29` `min_alt 1.25` `cv_diff 0.027` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.35 n=447 SE 0.056 z=23.9 min_alt 1.25 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Civilization; Economic; Fantasy; Territory Building` (`n_cats 4`) / `Network and Route Building; Variable Player Powers` (`n_mechs 2`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **480** (unranked) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D7` vol_band `200-499`
- `num_weights` (attention proxy) **24** (mean 20, up to 8660) — counts attention, not audience breadth; weight `4.00` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.370** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.170** (`share_heavy_250plus 0.387`, `share_light_10-24 0.045`, `mean_cnt_pool 320`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.723** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 7.9` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.816** (`20` low-mean 8.96 vs `22` high-mean 8.15; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.201** (`69` low-mean 8.78 vs `76` high-mean 8.58; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.555** (`49` low-mean 8.70 vs `22` high-mean 8.15; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **4** categories `Civilization; Economic; Fantasy; Territory Building` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **8.52**, `adj_mean` **8.89** themselves are quality estimates, not breadth; residual **1.35** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 447` `SE 0.056` `post_SD 0.056` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.723` everywhere, snapshot-time, `PR #4` caveat; `categories` 4 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 49. Montage — `game_id 5243` (1973; n=209 decile D4)
**Underratedness (A):** `resid 1.35` = `adj 7.71` − `E[adj] 6.37`; `SE 0.083` `post_SD 0.082` `z=16.3` `lb_adj 7.55` `resid_lb 1.19`; stability `CV 1.37` `WLS 1.42` `Q3 1.39` `WLS_Q3 1.45` `min_alt 1.37` `cv_diff 0.021` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.35 n=209 SE 0.083 z=16.3 min_alt 1.37 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Word Game` (`n_cats 1`) / `Area Majority / Influence; Pattern Recognition; Real-Time; Spelling; Team-Based Game; Tile Placement` (`n_mechs 6`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **216** (rank 7776) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D4` vol_band `200-499`
- `num_weights` (attention proxy) **13** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.54` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.515** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.641** (`share_heavy_250plus 0.833`, `share_light_10-24 0.024`, `mean_cnt_pool 962`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.474** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 357.2` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff -0.530** (`5` low-mean 6.73 vs `68` high-mean 7.26; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.121** (`8` low-mean 7.21 vs `134` high-mean 7.09; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.736** (`3` low-mean 8.00 vs `68` high-mean 7.26; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **1** categories `Word Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.20**, `adj_mean` **7.71** themselves are quality estimates, not breadth; residual **1.35** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 209` `SE 0.083` `post_SD 0.082` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.474` everywhere, snapshot-time, `PR #4` caveat; `categories` 1 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 50. System Gateway (fan expansion for Android: Netrunner) — `game_id 345976` (2021; n=660 decile D7)
**Underratedness (A):** `resid 1.34` = `adj 9.46` − `E[adj] 8.11`; `SE 0.046` `post_SD 0.046` `z=28.9` `lb_adj 9.36` `resid_lb 1.25`; stability `CV 1.35` `WLS 1.47` `Q3 1.31` `WLS_Q3 1.45` `min_alt 1.31` `cv_diff 0.011` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.34 n=660 SE 0.046 z=28.9 min_alt 1.31 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Bluffing; Card Game; Fan Expansion; Science Fiction; Third-party Expansion` (`n_cats 5`) / `Action Points; Deck Construction; Hand Management; Race; Secret Unit Deployment; Take That; Variable Player Powers` (`n_mechs 7`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **1025** (rank 1373) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D7` vol_band `500-999`
- `num_weights` (attention proxy) **26** (mean 20, up to 8660) — counts attention, not audience breadth; weight `3.50` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.364** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.091** (`share_heavy_250plus 0.265`, `share_light_10-24 0.086`, `mean_cnt_pool 246`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.806** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 59.1` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.413** (`57` low-mean 9.39 vs `22` high-mean 7.98; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +1.094** (`140` low-mean 9.39 vs `60` high-mean 8.29; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.398** (`83` low-mean 9.38 vs `22` high-mean 7.98; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **5** categories `Bluffing; Card Game; Fan Expansion; Science Fiction; Third-party Expansion` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **9.09**, `adj_mean` **9.46** themselves are quality estimates, not breadth; residual **1.34** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 660` `SE 0.046` `post_SD 0.046` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.806` everywhere, snapshot-time, `PR #4` caveat; `categories` 5 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 51. Boast or Nothing — `game_id 223952` (2017; n=364 decile D6)
**Underratedness (A):** `resid 1.32` = `adj 7.91` − `E[adj] 6.59`; `SE 0.063` `post_SD 0.062` `z=21.1` `lb_adj 7.79` `resid_lb 1.20`; stability `CV 1.32` `WLS 1.23` `Q3 1.27` `WLS_Q3 1.20` `min_alt 1.20` `cv_diff 0.005` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.32 n=364 SE 0.063 z=21.1 min_alt 1.20 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Card Game` (`n_cats 1`) / `Increase Value of Unchosen Resources; Trick-taking` (`n_mechs 2`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **481** (rank 5066) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D6` vol_band `200-499`
- `num_weights` (attention proxy) **12** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.42` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.716** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.500** (`share_heavy_250plus 0.780`, `share_light_10-24 0.008`, `mean_cnt_pool 698`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.385** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 293.8` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.985** (`3` low-mean 8.67 vs `67` high-mean 6.68; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +1.225** (`7` low-mean 8.11 vs `182` high-mean 6.89; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.019** (`4` low-mean 7.70 vs `67` high-mean 6.68; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **1** categories `Card Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.20**, `adj_mean` **7.91** themselves are quality estimates, not breadth; residual **1.32** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 364` `SE 0.063` `post_SD 0.062` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.385` everywhere, snapshot-time, `PR #4` caveat; `categories` 1 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 52. Firefly: The Game – 10th Anniversary Collector's Edition — `game_id 391288` (2024; n=345 decile D6)
**Underratedness (A):** `resid 1.31` = `adj 8.81` − `E[adj] 7.50`; `SE 0.064` `post_SD 0.064` `z=20.4` `lb_adj 8.69` `resid_lb 1.18`; stability `CV 1.32` `WLS 1.20` `Q3 1.16` `WLS_Q3 1.15` `min_alt 1.15` `cv_diff 0.011` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.31 n=345 SE 0.064 z=20.4 min_alt 1.15 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Adventure; Movies / TV / Radio theme; Science Fiction; Space Exploration; Travel` (`n_cats 5`) / `Area Movement; Dice Rolling; Open Drafting; Pick-up and Deliver; Solo / Solitaire Game; Take That; Trading; Variable Player Powers` (`n_mechs 8`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **722** (unranked) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D6` vol_band `200-499`
- `num_weights` (attention proxy) **19** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.95` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.131** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.133** (`share_heavy_250plus 0.310`, `share_light_10-24 0.096`, `mean_cnt_pool 264`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.870** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 23.1` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.328** (`33` low-mean 9.02 vs `14` high-mean 7.69; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +1.154** (`84` low-mean 9.04 vs `46` high-mean 7.89; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.369** (`51` low-mean 9.06 vs `14` high-mean 7.69; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **5** categories `Adventure; Movies / TV / Radio theme; Science Fiction; Space Exploration; Travel` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **8.68**, `adj_mean` **8.81** themselves are quality estimates, not breadth; residual **1.31** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 345` `SE 0.064` `post_SD 0.064` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.870` everywhere, snapshot-time, `PR #4` caveat; `categories` 5 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 53. 1817 — `game_id 63170` (2010; n=764 decile D8)
**Underratedness (A):** `resid 1.31` = `adj 9.36` − `E[adj] 8.05`; `SE 0.043` `post_SD 0.043` `z=30.3` `lb_adj 9.28` `resid_lb 1.23`; stability `CV 1.30` `WLS 1.33` `Q3 1.30` `WLS_Q3 1.31` `min_alt 1.30` `cv_diff 0.008` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.31 n=764 SE 0.043 z=30.3 min_alt 1.30 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Economic; Trains; Transportation` (`n_cats 3`) / `Auction / Bidding; Loans; Market; Network and Route Building; Ownership; Stock Holding; Tile Placement; Victory Points as a Resource` (`n_mechs 8`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **890** (rank 1783) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D8` vol_band `500-999`
- `num_weights` (attention proxy) **115** (mean 20, up to 8660) — counts attention, not audience breadth; weight `4.80` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.804** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.281** (`share_heavy_250plus 0.560`, `share_light_10-24 0.027`, `mean_cnt_pool 462`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.542** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 116.3` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.136** (`21` low-mean 8.98 vs `61` high-mean 7.84; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +1.131** (`55` low-mean 9.15 vs `215` high-mean 8.01; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.410** (`34` low-mean 9.25 vs `61` high-mean 7.84; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **3** categories `Economic; Trains; Transportation` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **8.56**, `adj_mean` **9.36** themselves are quality estimates, not breadth; residual **1.31** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 764` `SE 0.043` `post_SD 0.043` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.542` everywhere, snapshot-time, `PR #4` caveat; `categories` 3 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 54. Time's Up! Kids — `game_id 174219` (2015; n=254 decile D5)
**Underratedness (A):** `resid 1.30` = `adj 7.43` − `E[adj] 6.13`; `SE 0.075` `post_SD 0.075` `z=17.4` `lb_adj 7.29` `resid_lb 1.16`; stability `CV 1.33` `WLS 1.23` `Q3 1.32` `WLS_Q3 1.26` `min_alt 1.23` `cv_diff 0.023` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.30 n=254 SE 0.075 z=17.4 min_alt 1.23 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Children's Game; Party Game` (`n_cats 2`) / `Acting; Communication Limits; Memory; Team-Based Game` (`n_mechs 4`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **312** (rank 6345) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D5` vol_band `200-499`
- `num_weights` (attention proxy) **7** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.00` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.242** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.256** (`share_heavy_250plus 0.516`, `share_light_10-24 0.028`, `mean_cnt_pool 457`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.697** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 27.8` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.905** (`7` low-mean 7.93 vs `30` high-mean 7.03; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff -0.148** (`25` low-mean 7.14 vs `65` high-mean 7.29; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff -0.193** (`18` low-mean 6.83 vs `30` high-mean 7.03; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `Children's Game; Party Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.19**, `adj_mean` **7.43** themselves are quality estimates, not breadth; residual **1.30** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 254` `SE 0.075` `post_SD 0.075` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.697` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 55. What Were You Thinking? — `game_id 2667` (1998; n=257 decile D5)
**Underratedness (A):** `resid 1.30` = `adj 7.25` − `E[adj] 5.95`; `SE 0.074` `post_SD 0.074` `z=17.5` `lb_adj 7.11` `resid_lb 1.16`; stability `CV 1.31` `WLS 1.10` `Q3 1.26` `WLS_Q3 1.16` `min_alt 1.10` `cv_diff 0.010` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.30 n=257 SE 0.074 z=17.5 min_alt 1.10 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Party Game` (`n_cats 1`) / `Single Loser Game; Voting` (`n_mechs 2`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **267** (rank 7808) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D5` vol_band `200-499`
- `num_weights` (attention proxy) **15** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.20` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.365** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.374** (`share_heavy_250plus 0.603`, `share_light_10-24 0.027`, `mean_cnt_pool 672`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.444** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 75.2` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.609** (`7` low-mean 8.14 vs `38` high-mean 6.53; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.914** (`19` low-mean 7.58 vs `96` high-mean 6.66; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.716** (`12` low-mean 7.25 vs `38` high-mean 6.53; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **1** categories `Party Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **6.89**, `adj_mean` **7.25** themselves are quality estimates, not breadth; residual **1.30** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 257` `SE 0.074` `post_SD 0.074` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.444` everywhere, snapshot-time, `PR #4` caveat; `categories` 1 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 56. What's My Word? — `game_id 4079` (1972; n=375 decile D6)
**Underratedness (A):** `resid 1.30` = `adj 7.51` − `E[adj] 6.21`; `SE 0.062` `post_SD 0.062` `z=21.1` `lb_adj 7.39` `resid_lb 1.18`; stability `CV 1.34` `WLS 1.44` `Q3 1.22` `WLS_Q3 1.39` `min_alt 1.22` `cv_diff 0.040` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.30 n=375 SE 0.062 z=21.1 min_alt 1.22 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Deduction; Word Game` (`n_cats 2`) / `Paper-and-Pencil; Spelling` (`n_mechs 2`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **386** (rank 5800) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D6` vol_band `200-499`
- `num_weights` (attention proxy) **35** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.11` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.389** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.411** (`share_heavy_250plus 0.648`, `share_light_10-24 0.032`, `mean_cnt_pool 686`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.624** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 192.5` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.644** (`12` low-mean 7.38 vs `75` high-mean 6.73; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.621** (`19` low-mean 7.53 vs `154` high-mean 6.91; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.069** (`7` low-mean 7.80 vs `75` high-mean 6.73; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `Deduction; Word Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.13**, `adj_mean` **7.51** themselves are quality estimates, not breadth; residual **1.30** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 375` `SE 0.062` `post_SD 0.062` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.624` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 57. Figure It — `game_id 14940` (1975; n=245 decile D5)
**Underratedness (A):** `resid 1.30` = `adj 7.04` − `E[adj] 5.74`; `SE 0.076` `post_SD 0.076` `z=17.0` `lb_adj 6.89` `resid_lb 1.15`; stability `CV 1.32` `WLS 1.33` `Q3 1.32` `WLS_Q3 1.35` `min_alt 1.32` `cv_diff 0.024` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.30 n=245 SE 0.076 z=17.0 min_alt 1.32 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Deduction` (`n_cats 1`) / `—` (`n_mechs 0`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **291** (rank 8889) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D5` vol_band `200-499`
- `num_weights` (attention proxy) **20** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.30` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.512** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.331** (`share_heavy_250plus 0.596`, `share_light_10-24 0.024`, `mean_cnt_pool 577`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.596** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 72.7` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.975** (`6` low-mean 7.17 vs `38` high-mean 6.19; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.324** (`14` low-mean 6.75 vs `81` high-mean 6.43; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.245** (`8` low-mean 6.44 vs `38` high-mean 6.19; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **1** categories `Deduction` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **6.53**, `adj_mean` **7.04** themselves are quality estimates, not breadth; residual **1.30** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 245` `SE 0.076` `post_SD 0.076` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.596` everywhere, snapshot-time, `PR #4` caveat; `categories` 1 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 58. Mutabo — `game_id 238094` (2017; n=521 decile D7)
**Underratedness (A):** `resid 1.30` = `adj 7.75` − `E[adj] 6.46`; `SE 0.052` `post_SD 0.052` `z=24.8` `lb_adj 7.65` `resid_lb 1.19`; stability `CV 1.31` `WLS 1.31` `Q3 1.36` `WLS_Q3 1.37` `min_alt 1.31` `cv_diff 0.012` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.30 n=521 SE 0.052 z=24.8 min_alt 1.31 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Humor; Party Game` (`n_cats 2`) / `Command Cards; Cooperative Game; Paper-and-Pencil; Real-Time; Storytelling` (`n_mechs 5`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **608** (rank 3978) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D7` vol_band `500-999`
- `num_weights` (attention proxy) **23** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.04` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.286** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.152** (`share_heavy_250plus 0.382`, `share_light_10-24 0.025`, `mean_cnt_pool 333`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.714** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 34.1` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.624** (`13` low-mean 8.34 vs `35` high-mean 6.71; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.744** (`55` low-mean 7.89 vs `79` high-mean 7.15; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.039** (`42` low-mean 7.75 vs `35` high-mean 6.71; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `Humor; Party Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.46**, `adj_mean` **7.75** themselves are quality estimates, not breadth; residual **1.30** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 521` `SE 0.052` `post_SD 0.052` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.714` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 59. Unanimo — `game_id 12157` (1990; n=952 decile D8)
**Underratedness (A):** `resid 1.30` = `adj 7.32` − `E[adj] 6.03`; `SE 0.039` `post_SD 0.039` `z=33.5` `lb_adj 7.25` `resid_lb 1.22`; stability `CV 1.30` `WLS 1.23` `Q3 1.26` `WLS_Q3 1.14` `min_alt 1.14` `cv_diff 0.003` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.30 n=952 SE 0.039 z=33.5 min_alt 1.14 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Bluffing; Party Game; Word Game` (`n_cats 3`) / `Connections; Paper-and-Pencil` (`n_mechs 2`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **1108** (rank 3236) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D8` vol_band `500-999`
- `num_weights` (attention proxy) **33** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.15` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.251** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.263** (`share_heavy_250plus 0.508`, `share_light_10-24 0.016`, `mean_cnt_pool 437`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.625** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 95.2` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.521** (`15` low-mean 7.22 vs `81` high-mean 6.70; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.300** (`67` low-mean 7.12 vs `248` high-mean 6.82; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.392** (`52` low-mean 7.09 vs `81` high-mean 6.70; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **3** categories `Bluffing; Party Game; Word Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.07**, `adj_mean` **7.32** themselves are quality estimates, not breadth; residual **1.30** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 952` `SE 0.039` `post_SD 0.039` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.625` everywhere, snapshot-time, `PR #4` caveat; `categories` 3 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 60. MicroMacro: Crime City – Showdown — `game_id 398162` (2023; n=452 decile D7)
**Underratedness (A):** `resid 1.28` = `adj 8.28` − `E[adj] 7.00`; `SE 0.056` `post_SD 0.056` `z=22.8` `lb_adj 8.17` `resid_lb 1.17`; stability `CV 1.29` `WLS 1.25` `Q3 1.11` `WLS_Q3 1.19` `min_alt 1.11` `cv_diff 0.013` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.28 n=452 SE 0.056 z=22.8 min_alt 1.11 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Deduction; Murder / Mystery` (`n_cats 2`) / `Cooperative Game; Deduction; Scenario / Mission / Campaign Game; Solo / Solitaire Game` (`n_mechs 4`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **813** (rank 2737) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D7` vol_band `200-499`
- `num_weights` (attention proxy) **15** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.00` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.351** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.283** (`share_heavy_250plus 0.520`, `share_light_10-24 0.031`, `mean_cnt_pool 444`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.777** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 44.2` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.449** (`14` low-mean 7.80 vs `49` high-mean 7.35; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.654** (`41` low-mean 8.38 vs `128` high-mean 7.73; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.331** (`27` low-mean 8.69 vs `49` high-mean 7.35; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `Deduction; Murder / Mystery` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.93**, `adj_mean` **8.28** themselves are quality estimates, not breadth; residual **1.28** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 452` `SE 0.056` `post_SD 0.056` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.777` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 61. Techno Bowl: Arcade Football Unplugged — `game_id 194923` (2017; n=262 decile D5)
**Underratedness (A):** `resid 1.28` = `adj 8.56` − `E[adj] 7.29`; `SE 0.074` `post_SD 0.074` `z=17.3` `lb_adj 8.42` `resid_lb 1.13`; stability `CV 1.29` `WLS 1.25` `Q3 1.28` `WLS_Q3 1.28` `min_alt 1.25` `cv_diff 0.013` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.28 n=262 SE 0.074 z=17.3 min_alt 1.25 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Sports; Video Game Theme` (`n_cats 2`) / `Action Queue; Dice Rolling; Grid Movement; Hand Management; Simultaneous Action Selection` (`n_mechs 5`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **321** (rank 4893) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D5` vol_band `200-499`
- `num_weights` (attention proxy) **21** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.81` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.199** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.214** (`share_heavy_250plus 0.363`, `share_light_10-24 0.080`, `mean_cnt_pool 364`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.752** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 6.7` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.871** (`21` low-mean 9.25 vs `21` high-mean 7.38; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +1.332** (`50` low-mean 9.01 vs `56` high-mean 7.68; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.469** (`29` low-mean 8.84 vs `21` high-mean 7.38; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `Sports; Video Game Theme` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **8.37**, `adj_mean` **8.56** themselves are quality estimates, not breadth; residual **1.28** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 262` `SE 0.074` `post_SD 0.074` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.752` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 62. Baseball Highlights: 2045 – Super Deluxe Edition — `game_id 186567` (2015; n=513 decile D7)
**Underratedness (A):** `resid 1.27` = `adj 8.16` − `E[adj] 6.89`; `SE 0.053` `post_SD 0.053` `z=24.1` `lb_adj 8.05` `resid_lb 1.17`; stability `CV 1.29` `WLS 1.21` `Q3 1.35` `WLS_Q3 1.28` `min_alt 1.21` `cv_diff 0.014` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.27 n=513 SE 0.053 z=24.1 min_alt 1.21 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Card Game; Science Fiction; Sports` (`n_cats 3`) / `Deck, Bag, and Pool Building; Hand Management; Open Drafting; Take That` (`n_mechs 4`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **531** (unranked) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D7` vol_band `500-999`
- `num_weights` (attention proxy) **16** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.12` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.312** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.255** (`share_heavy_250plus 0.511`, `share_light_10-24 0.031`, `mean_cnt_pool 389`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.673** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 41.8` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.678** (`16` low-mean 7.91 vs `42` high-mean 7.23; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.493** (`44` low-mean 8.00 vs `131` high-mean 7.51; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.832** (`28` low-mean 8.06 vs `42` high-mean 7.23; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **3** categories `Card Game; Science Fiction; Sports` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.84**, `adj_mean` **8.16** themselves are quality estimates, not breadth; residual **1.27** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 513` `SE 0.053` `post_SD 0.053` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.673` everywhere, snapshot-time, `PR #4` caveat; `categories` 3 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 63. 6-Tage Rennen — `game_id 515` (1986; n=251 decile D5)
**Underratedness (A):** `resid 1.27` = `adj 7.34` − `E[adj] 6.07`; `SE 0.075` `post_SD 0.075` `z=16.9` `lb_adj 7.20` `resid_lb 1.12`; stability `CV 1.30` `WLS 1.28` `Q3 1.25` `WLS_Q3 1.31` `min_alt 1.25` `cv_diff 0.023` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.27 n=251 SE 0.075 z=16.9 min_alt 1.25 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Racing; Sports` (`n_cats 2`) / `Race` (`n_mechs 1`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **257** (rank 8191) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D5` vol_band `200-499`
- `num_weights` (attention proxy) **25** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.76` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.473** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.478** (`share_heavy_250plus 0.681`, `share_light_10-24 0.024`, `mean_cnt_pool 754`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.510** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 248.9` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.979** (`6` low-mean 7.50 vs `72` high-mean 6.52; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.909** (`15` low-mean 7.47 vs `120` high-mean 6.56; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.929** (`9` low-mean 7.45 vs `72` high-mean 6.52; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `Racing; Sports` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **6.87**, `adj_mean` **7.34** themselves are quality estimates, not breadth; residual **1.27** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 251` `SE 0.075` `post_SD 0.075` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.510` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 64. Hanabi & Ikebana — `game_id 70918` (2010; n=639 decile D7)
**Underratedness (A):** `resid 1.27` = `adj 7.89` − `E[adj] 6.63`; `SE 0.047` `post_SD 0.047` `z=26.8` `lb_adj 7.80` `resid_lb 1.17`; stability `CV 1.27` `WLS 1.16` `Q3 1.29` `WLS_Q3 1.20` `min_alt 1.16` `cv_diff 0.004` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.27 n=639 SE 0.047 z=26.8 min_alt 1.16 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Card Game; Deduction` (`n_cats 2`) / `Cooperative Game; Hand Management; Memory; Set Collection` (`n_mechs 4`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **645** (unranked) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D7` vol_band `500-999`
- `num_weights` (attention proxy) **59** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.76` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.489** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.429** (`share_heavy_250plus 0.668`, `share_light_10-24 0.016`, `mean_cnt_pool 608`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.496** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 334.4` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.806** (`10` low-mean 7.75 vs `122` high-mean 6.94; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.722** (`26` low-mean 7.88 vs `274` high-mean 7.16; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.025** (`16` low-mean 7.97 vs `122` high-mean 6.94; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `Card Game; Deduction` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.40**, `adj_mean` **7.89** themselves are quality estimates, not breadth; residual **1.27** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 639` `SE 0.047` `post_SD 0.047` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.496` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 65. The Red Dragon Inn 7: The Tavern Crew — `game_id 244258` (2018; n=311 decile D6)
**Underratedness (A):** `resid 1.26` = `adj 7.86` − `E[adj] 6.59`; `SE 0.068` `post_SD 0.068` `z=18.6` `lb_adj 7.72` `resid_lb 1.13`; stability `CV 1.25` `WLS 1.37` `Q3 1.22` `WLS_Q3 1.37` `min_alt 1.22` `cv_diff 0.013` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.26 n=311 SE 0.068 z=18.6 min_alt 1.22 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Card Game; Fantasy; Humor; Party Game` (`n_cats 4`) / `Betting and Bluffing; Hand Management; Player Elimination; Variable Player Powers` (`n_mechs 4`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **381** (rank 5107) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D6` vol_band `200-499`
- `num_weights` (attention proxy) **5** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.60` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **0.055** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.087** (`share_heavy_250plus 0.190`, `share_light_10-24 0.125`, `mean_cnt_pool 229`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.830** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 87.5` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.474** (`39` low-mean 8.64 vs `6` high-mean 7.17; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +1.616** (`89` low-mean 8.50 vs `27` high-mean 6.89; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.231** (`50` low-mean 8.40 vs `6` high-mean 7.17; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **4** categories `Card Game; Fantasy; Humor; Party Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.91**, `adj_mean` **7.86** themselves are quality estimates, not breadth; residual **1.26** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 311` `SE 0.068` `post_SD 0.068` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.830` everywhere, snapshot-time, `PR #4` caveat; `categories` 4 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 66. Crossboule — `game_id 91666` (2008; n=201 decile D4)
**Underratedness (A):** `resid 1.26` = `adj 7.42` − `E[adj] 6.16`; `SE 0.084` `post_SD 0.084` `z=15.0` `lb_adj 7.25` `resid_lb 1.10`; stability `CV 1.26` `WLS 1.14` `Q3 1.30` `WLS_Q3 1.22` `min_alt 1.14` `cv_diff 0.003` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.26 n=201 SE 0.084 z=15.0 min_alt 1.14 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Action / Dexterity` (`n_cats 1`) / `Area Majority / Influence` (`n_mechs 1`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **210** (rank 8207) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D4` vol_band `200-499`
- `num_weights` (attention proxy) **17** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.12` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.322** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.493** (`share_heavy_250plus 0.736`, `share_light_10-24 0.015`, `mean_cnt_pool 764`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.761** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 165.2` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.071** (`3` low-mean 8.00 vs `46` high-mean 6.93; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.487** (`7` low-mean 7.43 vs `99` high-mean 6.94; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.071** (`4` low-mean 7.00 vs `46` high-mean 6.93; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **1** categories `Action / Dexterity` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.10**, `adj_mean` **7.42** themselves are quality estimates, not breadth; residual **1.26** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 201` `SE 0.084` `post_SD 0.084` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.761` everywhere, snapshot-time, `PR #4` caveat; `categories` 1 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 67. Escape: The Curse of the Temple – Big Box Second Edition — `game_id 232894` (2017; n=564 decile D7)
**Underratedness (A):** `resid 1.26` = `adj 8.01` − `E[adj] 6.75`; `SE 0.050` `post_SD 0.050` `z=25.1` `lb_adj 7.91` `resid_lb 1.16`; stability `CV 1.25` `WLS 1.21` `Q3 1.31` `WLS_Q3 1.24` `min_alt 1.21` `cv_diff 0.013` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.26 n=564 SE 0.050 z=25.1 min_alt 1.21 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Adventure; Dice; Exploration; Real-time` (`n_cats 4`) / `Cooperative Game; Dice Rolling; Modular Board; Real-Time; Tile Placement` (`n_mechs 5`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **613** (unranked) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D7` vol_band `500-999`
- `num_weights` (attention proxy) **9** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.89` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.184** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.160** (`share_heavy_250plus 0.379`, `share_light_10-24 0.044`, `mean_cnt_pool 320`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.810** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 20.6` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.210** (`25` low-mean 8.13 vs `18` high-mean 6.92; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.620** (`72` low-mean 8.21 vs `90` high-mean 7.59; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.330** (`47` low-mean 8.25 vs `18` high-mean 6.92; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **4** categories `Adventure; Dice; Exploration; Real-time` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.83**, `adj_mean` **8.01** themselves are quality estimates, not breadth; residual **1.26** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 564` `SE 0.050` `post_SD 0.050` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.810` everywhere, snapshot-time, `PR #4` caveat; `categories` 4 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 68. Stonewall Jackson's Way II: Battles of Bull Run — `game_id 99358` (2013; n=324 decile D6)
**Underratedness (A):** `resid 1.26` = `adj 9.10` − `E[adj] 7.85`; `SE 0.066` `post_SD 0.066` `z=19.0` `lb_adj 8.97` `resid_lb 1.13`; stability `CV 1.25` `WLS 1.48` `Q3 1.24` `WLS_Q3 1.47` `min_alt 1.24` `cv_diff 0.004` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.26 n=324 SE 0.066 z=19.0 min_alt 1.24 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `American Civil War; Wargame` (`n_cats 2`) / `Dice Rolling; Hexagon Grid; Ratio / Combat Results Table; Zone of Control` (`n_mechs 4`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **354** (rank 4039) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D6` vol_band `200-499`
- `num_weights` (attention proxy) **30** (mean 20, up to 8660) — counts attention, not audience breadth; weight `3.67` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.440** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.130** (`share_heavy_250plus 0.302`, `share_light_10-24 0.077`, `mean_cnt_pool 341`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.855** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 13.7` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.763** (`25` low-mean 9.21 vs `16` high-mean 7.45; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.812** (`63` low-mean 8.95 vs `42` high-mean 8.14; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.324** (`38` low-mean 8.77 vs `16` high-mean 7.45; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `American Civil War; Wargame` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **8.66**, `adj_mean` **9.10** themselves are quality estimates, not breadth; residual **1.26** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 324` `SE 0.066` `post_SD 0.066` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.855` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 69. Dominion (Second Edition) Big Box — `game_id 216849` (2016; n=983 decile D8)
**Underratedness (A):** `resid 1.26` = `adj 8.30` − `E[adj] 7.04`; `SE 0.038` `post_SD 0.038` `z=33.0` `lb_adj 8.22` `resid_lb 1.18`; stability `CV 1.26` `WLS 1.16` `Q3 1.23` `WLS_Q3 1.10` `min_alt 1.10` `cv_diff 0.004` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.26 n=983 SE 0.038 z=33.0 min_alt 1.10 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Card Game; Medieval` (`n_cats 2`) / `Deck, Bag, and Pool Building; Hand Management; Open Drafting` (`n_mechs 3`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **1230** (unranked) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D8` vol_band `500-999`
- `num_weights` (attention proxy) **23** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.26` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.188** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.070** (`share_heavy_250plus 0.180`, `share_light_10-24 0.120`, `mean_cnt_pool 179`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.835** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 290.2` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.413** (`118` low-mean 8.48 vs `24` high-mean 8.07; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.364** (`317` low-mean 8.29 vs `69` high-mean 7.92; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.104** (`199` low-mean 8.17 vs `24` high-mean 8.07; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `Card Game; Medieval` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **8.11**, `adj_mean` **8.30** themselves are quality estimates, not breadth; residual **1.26** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 983` `SE 0.038` `post_SD 0.038` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.835` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 70. Angola — `game_id 4688` (1988; n=540 decile D7)
**Underratedness (A):** `resid 1.25` = `adj 8.53` − `E[adj] 7.28`; `SE 0.051` `post_SD 0.051` `z=24.4` `lb_adj 8.43` `resid_lb 1.15`; stability `CV 1.27` `WLS 1.52` `Q3 1.32` `WLS_Q3 1.55` `min_alt 1.27` `cv_diff 0.015` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.25 n=540 SE 0.051 z=24.4 min_alt 1.27 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Civil War; Modern Warfare; Wargame` (`n_cats 3`) / `Area Majority / Influence; Campaign / Battle Card Driven; Communication Limits; Movement Points; Secret Unit Deployment; Simulation; Team-Based Game` (`n_mechs 7`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **599** (rank 3270) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D7` vol_band `500-999`
- `num_weights` (attention proxy) **50** (mean 20, up to 8660) — counts attention, not audience breadth; weight `3.18` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.537** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.270** (`share_heavy_250plus 0.519`, `share_light_10-24 0.031`, `mean_cnt_pool 492`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.600** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 50.8` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.108** (`17` low-mean 8.59 vs `48` high-mean 7.48; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +1.031** (`53` low-mean 8.52 vs `146` high-mean 7.49; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.010** (`36` low-mean 8.49 vs `48` high-mean 7.48; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **3** categories `Civil War; Modern Warfare; Wargame` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **8.00**, `adj_mean` **8.53** themselves are quality estimates, not breadth; residual **1.25** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 540` `SE 0.051` `post_SD 0.051` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.600` everywhere, snapshot-time, `PR #4` caveat; `categories` 3 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 71. Château Aventure — `game_id 246742` (2018; n=243 decile D5)
**Underratedness (A):** `resid 1.25` = `adj 7.32` − `E[adj] 6.07`; `SE 0.077` `post_SD 0.076` `z=16.3` `lb_adj 7.17` `resid_lb 1.10`; stability `CV 1.29` `WLS 1.13` `Q3 1.25` `WLS_Q3 1.16` `min_alt 1.13` `cv_diff 0.037` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.25 n=243 SE 0.077 z=16.3 min_alt 1.13 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Adventure; Book; Fantasy; Horror; Medieval; Science Fiction` (`n_cats 6`) / `Cooperative Game; Role Playing; Storytelling` (`n_mechs 3`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **262** (rank 7180) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D5` vol_band `200-499`
- `num_weights` (attention proxy) **4** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.00` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.160** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.305** (`share_heavy_250plus 0.551`, `share_light_10-24 0.025`, `mean_cnt_pool 512`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.584** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 38.2` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.404** (`6` low-mean 7.50 vs `25` high-mean 7.10; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.087** (`19` low-mean 7.34 vs `74` high-mean 7.26; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.173** (`13` low-mean 7.27 vs `25` high-mean 7.10; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **6** categories `Adventure; Book; Fantasy; Horror; Medieval; Science Fiction` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.16**, `adj_mean` **7.32** themselves are quality estimates, not breadth; residual **1.25** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 243` `SE 0.077` `post_SD 0.076` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.584` everywhere, snapshot-time, `PR #4` caveat; `categories` 6 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 72. Carcassonne Big Box 3 — `game_id 141007` (2010; n=895 decile D8)
**Underratedness (A):** `resid 1.25` = `adj 7.95` − `E[adj] 6.71`; `SE 0.040` `post_SD 0.040` `z=31.3` `lb_adj 7.88` `resid_lb 1.17`; stability `CV 1.24` `WLS 1.10` `Q3 1.22` `WLS_Q3 1.06` `min_alt 1.06` `cv_diff 0.007` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.25 n=895 SE 0.040 z=31.3 min_alt 1.06 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `City Building; Medieval` (`n_cats 2`) / `Area Majority / Influence; Tile Placement` (`n_mechs 2`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **960** (unranked) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D8` vol_band `500-999`
- `num_weights` (attention proxy) **35** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.09` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.099** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.096** (`share_heavy_250plus 0.235`, `share_light_10-24 0.103`, `mean_cnt_pool 209`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.830** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 144.0` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.786** (`92` low-mean 8.02 vs `26` high-mean 7.23; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.714** (`234` low-mean 8.07 vs `86` high-mean 7.35; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.863** (`142` low-mean 8.10 vs `26` high-mean 7.23; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `City Building; Medieval` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.86**, `adj_mean` **7.95** themselves are quality estimates, not breadth; residual **1.25** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 895` `SE 0.040` `post_SD 0.040` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.830` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 73. Eggs of Ostrich — `game_id 146035` (2012; n=303 decile D6)
**Underratedness (A):** `resid 1.24` = `adj 7.48` − `E[adj] 6.23`; `SE 0.069` `post_SD 0.068` `z=18.1` `lb_adj 7.34` `resid_lb 1.11`; stability `CV 1.25` `WLS 1.05` `Q3 1.22` `WLS_Q3 1.06` `min_alt 1.05` `cv_diff 0.009` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.24 n=303 SE 0.069 z=18.1 min_alt 1.05 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Card Game` (`n_cats 1`) / `Hand Management; Simultaneous Action Selection` (`n_mechs 2`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **319** (rank 7255) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D6` vol_band `200-499`
- `num_weights` (attention proxy) **11** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.18` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.692** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.650** (`share_heavy_250plus 0.851`, `share_light_10-24 0.000`, `mean_cnt_pool 953`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.370** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 510.9` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- Heavy vs light rater means on same game — **no overlapping heavy/light groups available** for this game in the three `within_game_diffs_active*` slices (requires ≥30? per band). Absence is not evidence of niche; Low volume is *less* evidence, not more.
- `game_tags` category breadth **1** categories `Card Game` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **6.79**, `adj_mean` **7.48** themselves are quality estimates, not breadth; residual **1.24** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 303` `SE 0.069` `post_SD 0.068` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.370` everywhere, snapshot-time, `PR #4` caveat; `categories` 1 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 74. WeyKick — `game_id 20295` (2001; n=524 decile D7)
**Underratedness (A):** `resid 1.24` = `adj 7.42` − `E[adj] 6.17`; `SE 0.052` `post_SD 0.052` `z=23.8` `lb_adj 7.32` `resid_lb 1.14`; stability `CV 1.21` `WLS 1.07` `Q3 1.30` `WLS_Q3 1.13` `min_alt 1.07` `cv_diff 0.037` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.24 n=524 SE 0.052 z=23.8 min_alt 1.07 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Action / Dexterity; Real-time; Sports` (`n_cats 3`) / `Team-Based Game` (`n_mechs 1`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **539** (rank 5181) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D7` vol_band `500-999`
- `num_weights` (attention proxy) **39** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.03` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.467** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.569** (`share_heavy_250plus 0.811`, `share_light_10-24 0.006`, `mean_cnt_pool 799`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.281** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 642.5` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff -0.453** (`3` low-mean 6.33 vs `142` high-mean 6.79; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.818** (`12` low-mean 7.62 vs `298` high-mean 6.81; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.269** (`9` low-mean 8.06 vs `142` high-mean 6.79; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **3** categories `Action / Dexterity; Real-time; Sports` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **6.95**, `adj_mean` **7.42** themselves are quality estimates, not breadth; residual **1.24** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 524` `SE 0.052` `post_SD 0.052` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.281` everywhere, snapshot-time, `PR #4` caveat; `categories` 3 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 75. Kingdom Builder: Big Box (Second Edition) — `game_id 229130` (2017; n=689 decile D8)
**Underratedness (A):** `resid 1.24` = `adj 8.26` − `E[adj] 7.02`; `SE 0.045` `post_SD 0.045` `z=27.2` `lb_adj 8.17` `resid_lb 1.15`; stability `CV 1.24` `WLS 1.10` `Q3 1.25` `WLS_Q3 1.12` `min_alt 1.10` `cv_diff 0.002` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.24 n=689 SE 0.045 z=27.2 min_alt 1.10 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Medieval; Territory Building` (`n_cats 2`) / `Area Majority / Influence; Chaining; Enclosure; Grid Movement; Hexagon Grid; Modular Board; Network and Route Building; Variable Set-up` (`n_mechs 8`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **749** (unranked) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D8` vol_band `500-999`
- `num_weights` (attention proxy) **18** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.17` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.273** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.228** (`share_heavy_250plus 0.472`, `share_light_10-24 0.032`, `mean_cnt_pool 389`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.768** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 36.9` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.410** (`22` low-mean 8.41 vs `44` high-mean 8.00; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.376** (`71` low-mean 8.18 vs `157` high-mean 7.80; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.074** (`49` low-mean 8.07 vs `44` high-mean 8.00; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `Medieval; Territory Building` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.99**, `adj_mean` **8.26** themselves are quality estimates, not breadth; residual **1.24** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 689` `SE 0.045` `post_SD 0.045` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.768` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 76. Q.E. — `game_id 209136` (2017; n=318 decile D6)
**Underratedness (A):** `resid 1.23` = `adj 8.00` − `E[adj] 6.76`; `SE 0.067` `post_SD 0.067` `z=18.4` `lb_adj 7.87` `resid_lb 1.10`; stability `CV 1.23` `WLS 1.09` `Q3 1.20` `WLS_Q3 1.09` `min_alt 1.09` `cv_diff 0.007` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.23 n=318 SE 0.067 z=18.4 min_alt 1.09 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Economic` (`n_cats 1`) / `Auction / Bidding` (`n_mechs 1`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **342** (rank 5790) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D6` vol_band `200-499`
- `num_weights` (attention proxy) **6** (mean 20, up to 8660) — counts attention, not audience breadth; weight `1.83` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.719** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.560** (`share_heavy_250plus 0.833`, `share_light_10-24 0.009`, `mean_cnt_pool 808`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.355** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 369.3` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +2.529** (`3` low-mean 9.33 vs `79` high-mean 6.80; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +1.239** (`8` low-mean 8.31 vs `178` high-mean 7.07; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.896** (`5` low-mean 7.70 vs `79` high-mean 6.80; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **1** categories `Economic` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.28**, `adj_mean` **8.00** themselves are quality estimates, not breadth; residual **1.23** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 318` `SE 0.067` `post_SD 0.067` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.355` everywhere, snapshot-time, `PR #4` caveat; `categories` 1 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 77. Ascension: Deliverance — `game_id 261321` (2018; n=219 decile D5)
**Underratedness (A):** `resid 1.22` = `adj 8.07` − `E[adj] 6.85`; `SE 0.081` `post_SD 0.080` `z=15.1` `lb_adj 7.91` `resid_lb 1.06`; stability `CV 1.22` `WLS 1.23` `Q3 1.23` `WLS_Q3 1.29` `min_alt 1.22` `cv_diff 0.005` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.22 n=219 SE 0.081 z=15.1 min_alt 1.22 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Card Game; Fantasy` (`n_cats 2`) / `Deck, Bag, and Pool Building; Hand Management; Open Drafting` (`n_mechs 3`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **252** (rank 6173) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D5` vol_band `200-499`
- `num_weights` (attention proxy) **2** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.00` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.213** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.260** (`share_heavy_250plus 0.461`, `share_light_10-24 0.059`, `mean_cnt_pool 502`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.689** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 14.0` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.323** (`13` low-mean 8.62 vs `26` high-mean 7.29; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +1.003** (`36` low-mean 8.42 vs `57` high-mean 7.42; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +1.021** (`23` low-mean 8.31 vs `26` high-mean 7.29; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `Card Game; Fantasy` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.86**, `adj_mean` **8.07** themselves are quality estimates, not breadth; residual **1.22** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 219` `SE 0.081` `post_SD 0.080` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.689` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 78. Taluva Deluxe — `game_id 188076` (2015; n=440 decile D7)
**Underratedness (A):** `resid 1.22` = `adj 8.13` − `E[adj] 6.92`; `SE 0.057` `post_SD 0.057` `z=21.4` `lb_adj 8.02` `resid_lb 1.11`; stability `CV 1.24` `WLS 1.17` `Q3 1.13` `WLS_Q3 1.13` `min_alt 1.13` `cv_diff 0.025` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.22 n=440 SE 0.057 z=21.4 min_alt 1.13 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Abstract Strategy; Territory Building` (`n_cats 2`) / `Layering; Modular Board; Team-Based Game; Tile Placement` (`n_mechs 4`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **474** (unranked) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D7` vol_band `200-499`
- `num_weights` (attention proxy) **8** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.38` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.514** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.386** (`share_heavy_250plus 0.634`, `share_light_10-24 0.014`, `mean_cnt_pool 602`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.550** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 143.3` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.197** (`6` low-mean 8.67 vs `60` high-mean 7.47; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.593** (`22` low-mean 7.95 vs `170` high-mean 7.36; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.218** (`16` low-mean 7.69 vs `60` high-mean 7.47; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `Abstract Strategy; Territory Building` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.62**, `adj_mean` **8.13** themselves are quality estimates, not breadth; residual **1.22** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 440` `SE 0.057` `post_SD 0.057` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.550` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 79. Viticulture: Complete Collector's Edition — `game_id 156455` (2014; n=806 decile D8)
**Underratedness (A):** `resid 1.22` = `adj 8.61` − `E[adj] 7.40`; `SE 0.042` `post_SD 0.042` `z=28.9` `lb_adj 8.53` `resid_lb 1.13`; stability `CV 1.23` `WLS 1.19` `Q3 1.21` `WLS_Q3 1.17` `min_alt 1.17` `cv_diff 0.011` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.22 n=806 SE 0.042 z=28.9 min_alt 1.17 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Economic; Farming` (`n_cats 2`) / `Contracts; Hand Management; Turn Order: Auction; Victory Points as a Resource; Worker Placement; Worker Placement, Different Worker Types` (`n_mechs 6`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **836** (unranked) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D8` vol_band `500-999`
- `num_weights` (attention proxy) **50** (mean 20, up to 8660) — counts attention, not audience breadth; weight `3.32` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.309** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.261** (`share_heavy_250plus 0.524`, `share_light_10-24 0.027`, `mean_cnt_pool 437`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.763** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 99.9` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +1.028** (`22` low-mean 8.86 vs `82` high-mean 7.83; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.693** (`59` low-mean 8.71 vs `210` high-mean 8.02; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.796** (`37` low-mean 8.63 vs `82` high-mean 7.83; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **2** categories `Economic; Farming` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **8.30**, `adj_mean` **8.61** themselves are quality estimates, not breadth; residual **1.22** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 806` `SE 0.042` `post_SD 0.042` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.763` everywhere, snapshot-time, `PR #4` caveat; `categories` 2 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

## 80. Baseball Highlights: 2045 – Deluxe Edition — `game_id 174458` (2015; n=545 decile D7)
**Underratedness (A):** `resid 1.21` = `adj 8.16` − `E[adj] 6.95`; `SE 0.051` `post_SD 0.051` `z=23.7` `lb_adj 8.06` `resid_lb 1.11`; stability `CV 1.20` `WLS 1.16` `Q3 1.28` `WLS_Q3 1.21` `min_alt 1.16` `cv_diff 0.011` — **model-dependent conditional anomaly, not latent quality**
**Disposition:** `robust_underrated` — robust underrated candidate — resid 1.21 n=545 SE 0.051 z=23.7 min_alt 1.16 (stable across Q3b/Q4/WLS; >=100 floor passed, >=200, >=0.60, min_alt>=0.30, z>=5)
**Categories/Mechanics:** `Card Game; Science Fiction; Sports` (`n_cats 3`) / `Deck, Bag, and Pool Building; Hand Management; Open Drafting; Take That` (`n_mechs 4`) — tag overlap descriptive contrasts, not causal (handle `games` 80.89% gap via `bgg_research_population` complete)

### Evidence (1) — Reach / recognition (not proof of broad appeal)
- `users_rated` (scrape) **565** (unranked) — popularity, not broad appeal; `R² game 0.201` includes popularity premium; n_active decile `D7` vol_band `500-999`
- `num_weights` (attention proxy) **25** (mean 20, up to 8660) — counts attention, not audience breadth; weight `2.28` if weighed
- `is_reimplementation` **False**  — family reach: reimplementations avg users 7,338 vs 1,619 non-reimpl; reach ≠ broad appeal (self-selection)
- Caveat: **popularity premium** `+0.26/10×` on `n_active` (`+0.51` on `users_rated`) survives severity adjustment (`phase6_volume_diagnostic.json`); reach is confounded with quality-driven popularity and visibility.

### Evidence (2) — Audience composition (who rated it)
- `mean(delta)_pool` **-0.286** (`SD 0.177` across games; pool vs population z via `share_heavy`) — rater-pool severity level; low-vs-high-volume gap is almost entirely additive severity (`findings.md` Phase A, `r 0.877`, `gap −0.03`), treat as descriptive level not credibility.
- `share_heavy_500plus` **0.301** (`share_heavy_250plus 0.549`, `share_light_10-24 0.022`, `mean_cnt_pool 459`) — heavy/light composition; selection residual mean ≈0 (`phase4_selection.json` SD 0.015) after severity.
- `country` (where non-missing) — 209,753/288,730 =72.7% have country (27.3% missing); US 77k Canada 14.7k Germany 13.5k — available only where `users_active.country` non-null; do not overinterpret as broad geographic appeal without coverage check (`docs/phase2-active/PARQUET_CATALOG.md`).
- `collections` `share_own` **0.653** (if avail; population mean 0.571±0.145; 15M own=1 /10.8M NaN) — **snapshot-time** collection status (`PR #4`), 58% everywhere, not longitudinal broad-appeal proof (ownership ≠ appeal). `share_heavy`/`mean(delta)` as above; `chi2_volume_band 75.9` vs population volume shares.

### Evidence (3) — Cross-audience consistency (does quality hold across audiences?)
- `10-24_vs_1000plus` **diff +0.576** (`12` low-mean 8.29 vs `56` high-mean 7.72; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `10-49_vs_500plus` **diff +0.561** (`39` low-mean 8.37 vs `164` high-mean 7.81; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `25-49_vs_1000plus` **diff +0.691** (`27` low-mean 8.41 vs `56` high-mean 7.72; n_total illustrative) — where both heavy and light rater groups rated same game (rare; only games with ≥30? in both bands); positive diff means light raters rated higher (severity level, not taste).
- `game_tags` category breadth **3** categories `Card Game; Science Fiction; Sports` — tag overlap descriptive, not audience diversity; category breadth is proxy, not broad appeal (see README §6). Correlation `|resid| vs SE +0.18` shows larger absolute residuals modestly more common where precision low.

### Evidence (4) — What is merely a proxy and cannot establish broad appeal (caveats)
- `raw_mean` **7.87**, `adj_mean` **8.16** themselves are quality estimates, not breadth; residual **1.21** is underratedness (conditional anomaly), not hidden-gem proof.
- `n_obs 545` `SE 0.051` `post_SD 0.051` — **low n is less evidence**; high residual at `n=50` `SE 0.169` not equivalent to same at `n=3000` `SE 0.022`; report `z`/`lb_adj` alongside magnitude.
- `own 0.653` everywhere, snapshot-time, `PR #4` caveat; `categories` 3 tags — both proxies, not audience breadth.
- No external broad-appeal validation (sales/plays/non-BGG) — all evidence **within-BGG**; broad appeal beyond niche cannot be established from internal data alone (see `docs/phase6-intermediate/findings_and_conclusions_to_date.md`).
- **A niche game can remain excellent underrated without hidden-gem promotion** — underrated (A) and hidden-gem (broad appeal beyond niche, B) are distinct.

---
*Showing 80 of 910 robust candidates in this markdown for readability; full 910 candidates with four evidence types per candidate are reproducible from `underrated_candidates.csv` plus the evidence taxonomy above and `selection_diagnostic.csv` / `within_game_diffs_active*` / `game_tags_filtered`. To view all, filter CSV by `screening_disposition=robust_underrated`.*
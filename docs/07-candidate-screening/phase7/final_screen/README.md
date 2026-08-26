# Final Screen — 544 Quality-Gated Robust Underrated Candidates (INTERMEDIATE / NOT FINAL RESEARCH OUTPUTS)

> **Status:** INTERMEDIATE / NOT FINAL RESEARCH OUTPUTS — screening stage, not the final hidden-gem ranking. **Do not build a final hidden-gem score from these tables.** Every residual is a model-dependent conditional anomaly `adj_mean − E[adj_mean|X]` (Q3b/OLS), not latent quality or broad appeal. Do not treat as proof of broad appeal.

## 1. Population and gate

- **Starting population:** 16,627 research-population games × users ≥10 in-universe ratings, excluding `degenerate_strict` (24.5M obs, `mu 7.144`, `SE = 1.194/√n`, `sigma_alpha² 0.746`; `docs/phase2-active/README.md`).
- **Phase 7 robust:** 910 robust underrated candidates from `underrated_candidates.csv` (16,549 estimation sample; 15 missing weight/playtime) with:
  ```
  robust := n≥200 & resid≥0.60 Q3b/OLS & min_alt≥0.30 (all of cv_pref,wls_pref,ols_Q3,wls_Q3 ≥0.30)
           & z≥5 & year<2025 & not duplicate-shadowed (4× users rule; title_clean duplicate 206, shadowed 136)
  ```
  `resid = adj − expected` where expected is Q3b/OLS (46 features: 8 volume-band dummies + spline year 4 knots + weight + log_playtime + min/max players + is_reimplementation + log_n_impl + 28 category flags; CV R² .582 vs Q3 .570 vs Q4 .585; WLS degrades CV and leaks volume).
- **Quality gate (Phase 7A):** `adj_mean ≥7.5` where `adj_mean = mu + alpha_g = AVG(rating − delta_u)` (active ALS, `game_adjusted_means_active.parquet`, held-out R² .938 vs raw .779). Gate at P74≈P75 (=7.515, `mu+0.41SD`, top quartile, 25.7% ≥7.5, P90 8.01). Retains **544 of 910 (59.8%)**; excluded 366 have median `adj 7.14` (below P75) and max resid 1.49 — precisely “underrated but mediocre” cases (e.g. Grave Robbers II 6.19/0.84, Magnificent Race 6.38/0.76). Sensitivity around gate is smooth (~52 per 0.1 adj): `7.0→786, 7.3→654, 7.5→544, 7.6→492, 7.8→382, 8.0→274`. Lower-bound `lb = adj −1.96·SE` at 7.5 is redundant given `n≥200` (worst-case `n=200 lb 7.335>7.0`); at lenient `adj≥7.0` it screens 46 borderline `adj 7.0–7.13` low-n. `SE = 1.194/√n`: at `n=200 0.084`, `n=544 median 0.051`, `n=3000 0.022` (10× span; 23.4% of games have `|resid|<2·SE`).
- **Do NOT modify** Phase 5/6 models, residual definitions, population, or the `7.5` gate.

## 2. Four dimensions kept separate (no combined score)

Per `docs/phase7-candidate-screening/broad_appeal_evidence.md:1` taxonomy, for every candidate report separately:

1. **Quality** — `adj_mean ≥7.5` already established (from `game_adjusted_means_active.parquet`, `mu 7.144`, `SE 1.194/√n`, `post_SD =1/√(1/0.746+n/1.426)`, `lower=adj−1.96·SE`, `z=resid/SE`). Report `adj`, `n`, `SE`, `lb`, `z` together — `resid 0.6 at n=200 SE0.084 z7.1 ≠ resid 0.6 at n=50 SE0.169 z3.5`.
2. **Underratedness** — robust `Q3b/OLS` `underratedness = adj − expected` (`resid` 0.60–2.27 among gated, `min_alt≥0.30` stable across Q3b/Q4/WLS; `R² .582`, WLS harmful `corr(resid,log n) −0.08..−0.13` vs OLS ≈0; Q3b vs Q3 spearman .985 Jaccard .675, Q3b vs Q4 .958/.579). Both `resid` and `min_alt`/`z`/`n decile` preserved.
3. **Hiddenness / recognition** — whether the game is sufficiently obscure to plausibly qualify as hidden gem: `users_rated` (popularity, not breadth), `rank_current` (available 446/544, 98 null unranked), `num_weights` (attention proxy median 20 population, 29 gated), `is_reimplementation` family reach (reimpl avg users 7,338 vs 1,619 non-reimpl) — but *not* proof; low `n` alone is not hiddenness per central problem (self-selection, not noise).
4. **Audience breadth / niche transcendence** — whether any evidence appeal extends beyond narrow audience currently rating it: `share_heavy_500plus` (median 0.271 population, 0.219 gated), `mean(delta)_pool` (−0.293±0.177), `share_own` snapshot-time (58% everywhere, `PR #4`, 0.571±0.145, 15M own=1/10.8M NaN), `country` where non-missing (72.7% have country, 27.3% missing — do not overinterpret), `game_tags` category breadth (mean 2.77), and heavy vs light rater means on same game where both rated it — 902/910 robust had overlap (three slices 14k–16k rows; here 526/541/539 of 544 gated have diff with any n, 421/521/485 with n≥10 both sides). Light-vs-heavy gap is almost entirely additive severity (`r 0.877`, gap −0.03), treat as descriptive level not credibility or taste; low volume ≠ broad appeal.

**Proxy caveats (cannot establish broad appeal):** high `raw`/`adj` rating, low `n`, ownership prevalence (`own 58%` snapshot-time), category breadth (tag overlap not audience diversity), `users_rated` (popularity not breadth), high residual (underratedness not broad appeal), single-band `share_heavy` alone. No external sales/plays/non-BGG validation exists.

## 3. Dispositions (single-label priority for counts; four dimensions still reported separately)

A niche game can remain a strong candidate if genuinely obscure and highly regarded; however make the niche limitation explicit. Do not automatically exclude niche games.

| Priority | Disposition | N (of 544) | Rule (method choice, not ground truth) |
|---|---|---:|---|
| 1 | `high_quality_but_well_known` | 0 | `users_rated ≥20000` or `rank<500` — widely established, conflicts with hidden-gem objective (530 flagged wellknown in Phase 7, 67 met robust criteria; all 544 gated are below this strict threshold) |
| 2 | `insufficient_hiddenness_evidence` | 40 | `users_rated ≥5000` or `rank<1000` and not well-known — not obscure (e.g. High Society 16848 rank535, Las Vegas 12523 rank631, Burgundy Special Edition 12010 unranked, PitchCar 11831 rank531) |
| 3 | `high_quality_but_niche_only` | 19 | `share_own ≥0.78` & `share_light_10_24 ≤0.04` & `users<1500` — high owner concentration + limited light reach (e.g. Monikers variants 0.84–0.87, share_light 0.02–0.03, users 255–609; Gamut of Games 0.79; strict 0.84–0.87 captures 6) |
| 4 | `duplicate_or_edition_related` | 104 | title contains edition keyword `['edition','anniversary','big box','collector','deluxe','decennial','heritage','premium','reprint','box set','nonsense','shmonikers','more monikers','classics','party edition','special edition','kickstarter edition']` and not in 1–3 — special/deluxe/anniversary/big-box/collector variant or family (e.g. Small World Designer Edition 140135 n246 resid2.20 vs base Small World 40692 n75285; Terra Mystica Big Box vs base 51256; Monikers family 7 of 8 in gated vs base Monikers 7906; game_links reimplementation/version; 4× users shadowing 136 flagged pre-gate, 206 title_clean duplicates) |
| 5 | `other_exclusion` | 9 | `n<260` & `resid<0.70` — lower tail moderate SE, less evidence (illustrative; n median 217 vs 544 likely median 544) |
| 6 | `likely_hidden_gem_candidate` | 55 | hidden (`users<5000` & `rank≥1000` or null) + quality + underratedness + **suggestive broad evidence**: heavy mean≥7.5 with n≥10 both sides and moderate ownership 0.45–0.78, or fallback moderate ownership 0.45–0.78 + moderate heavy share 0.12–0.45 + num_weights≥15 + n≥300 + resid≥0.65 where no heavy/light diff with n≥10 both sides available; not niche/edition/other |
| 7 | `insufficient_broad_appeal_evidence` | 317 | hidden but audience evidence is proxy-only; 902/910 robust had overlap but gap is severity not taste; heavy mean <7.5 or ownership outside moderate or categories proxy-only; no external validation |

Raw tallies independent of priority: wellknown strict 0, insufficient hiddenness 40, edition keyword 122 (23.3%), niche high-own 19, other 9, likely 55, insufficient broad 317. Single-label priority is for auditable counts; **every candidate still reports the four dimensions separately** in `candidate_review.md/csv` — disposition is summary label, not combined score.

## 4. How to read the outputs

### `candidate_review.csv` (544 rows, machine-readable; `candidate_review.md` is human-readable view)

Sorted by disposition priority then `underratedness_pref` desc then `z`. Columns:

- **Identity:** `game_id, title, year, n_obs, users_rated, rank_current, weight, cat_str, is_reimplementation, num_weights`
- **Quality (dim 1):** `adj_mean, se (=1.194/√n), post_sd (=1/√(1/0.746+n/1.426)), z (=resid/se), lb_adj (=adj−1.96·SE), lower_1 (=adj−SE), lower_post_1_96`
- **Underratedness (dim 2):** `expected_quality_pref, underratedness_pref (Q3b/OLS), min_alt_resid, n_decile, vol_band_label`
- **Recognition / hiddenness (dim 3):** `users_rated, rank_current, num_weights, is_reimplementation` (family reach 7,338 vs 1,619)
- **Audience evidence (dim 4):** `share_heavy_500plus, share_heavy_250plus, share_light_10_24, share_own, mean_delta_pool, has_heavy_light_diff, mean_low/high/diff (10-49 vs 500+ and 10-24 vs 1000+)`
- **Disposition:** `disposition, disposition_reason, edition_flag, wellknown_flag, insuf_hidden_flag, niche_flag` (single-label priority above plus boolean flags for independent tallies)

### `candidate_review.md`

Human-readable tables: disposition summary + per-disposition distributions, then full 544-row compact table (same order), plus **detailed per-candidate 4-dimension evidence blocks for the 55 `likely_hidden_gem_candidate`** (quality / underratedness / hiddenness / audience + caveats). Well-known/niche/edition/insufficient sections are summarized in tables; full CSV retains every field.

### `candidate_dispositions.md`

Disposition counts, `n`/`adj`/`resid` distributions per disposition, and explicit raw tallies (`wellknown 0`, `edition raw 122`, `niche 19`, etc.) independent of priority. See §3 for definitions.

### `screening_summary.json`

Machine-readable counts (`broad 910 → quality-gated 544 → plausible hidden gems 55`), plus per-disposition `count, n_median/mean/p10/p90, adj_median/mean, resid_median/mean/min/max`, thresholds, provenance, claim tags.

## 5. Limitations and open issues

- **Model-dependent:** `adj` is preferred quality estimator (active held-out R² .938 vs raw .779 vs bayes −1.35) but assumes additive `delta_u` (global severity r 0.877 gap −0.03; beyond-additive SD 0.015 per Phase 4 — non-additive forms untested); `resid` is Q3b/OLS 46-feature conditional anomaly (tags overlap descriptive contrasts not causal, measurement error in X not modeled); `min_alt≥0.30` guards cross-spec stability.
- **No external broad-appeal validation** — all evidence within-BGG; volume premium (+0.26/10× on n_active, +0.51 on users_rated) survives severity adjustment; self-selection (people choose what to buy/play/rate) confounds popularity and broad appeal; do not conflate measurement noise (SE correction) with selection into measured population.
- **Hiddenness is proxy, not proof:** `users_rated` is popularity, not breadth; low `n` is less evidence, not more; `rank` is downstream of popularity/rating and should not be used as control; `is_reimplementation` family reach (7,338 vs 1,619) is reach, not broad appeal.
- **Audience evidence caveats:** `share_own` is snapshot-time collection status (`PR #4`, 58% everywhere, not longitudinal; 0.571±0.145); `country` 27.3% missing; heavy vs light overlap is rare for very niche games (18/544 missing any diff, 123 missing n≥10 both sides) and where present gap ≈+0.6–0.9 is severity level, not taste; category breadth is tag overlap not audience diversity; no validated audience proxies or external sales/plays.
- **Thresholds not identified:** no natural break at 7.5, 5000 users, 0.78 share_own, or 7.5 heavy mean; choices are interpretable anchors (top quartile, median lower bound ≥7.0, +1.4 SD ownership) with smooth sensitivity. Different reasonable thresholds move counts substantially — report sensitivity (§1 gate: 786→544→382) alongside any chosen N.
- **Coverage:** `bgg_research_population` complete 16,627 used for categories/mechanics where `games.parquet` is 80.89%; `n_obs` is active t≥10 minus `degenerate_strict` (24.5M obs, 288,730 users, 16,564 active games); robust `n≥200` already restricts SE≤0.084 (median likely 0.051 vs insufficient_hiddenness median 0.018 at n~4300).

## 6. Provenance and rerun

- **Script:** `scripts/33_phase7_final_screen.py` (bounded 4GB/3 threads, `temp_directory scratch/ducktmp`, `scratch/phase2-active` copy-once, single-scan DuckDB where needed, no wide-table bug, no full-snapshot rescans).
- **Inputs:** `docs/phase7-candidate-screening/quality_gate/quality_gate_candidates.csv` (910 robust with gate flags, adj≥7.5 is 544), `docs/phase7-candidate-screening/underrated_candidates.csv` (16,549 rows, 910 robust), `data/processed/phase2-active/game_adjusted_means_active.parquet` (`adj_mean`, `n`, `SE`), `data/processed/phase2-active/phase6_residuals_active.parquet` (`resid`), `scratch/phase2-active/bgg_research_population.parquet` (complete 16,627, for `year`/`rank`/`users_rated`/`weight`/`is_reimplementation`/`num_weights`/`categories`), plus `game_links_filtered`/`within_game_diffs_active_*.parquet` via `data/processed/phase2-active/` join, `reports/phase7_candidate_screening/*` for broad-appeal taxonomy.
- **Outputs:** this folder (`docs/phase7-candidate-screening/final_screen/`) — `candidate_review.csv` (544×~35), `candidate_review.md` (human table + 55 detailed blocks), `candidate_dispositions.md` (counts & distributions), `screening_summary.json` (machine-readable), `README.md` (this file).
- **Rerun:** `python scripts/33_phase7_final_screen.py` — regenerates CSV/JSON/dispositions; `candidate_review.md` and `README.md` are views of CSV/JSON.

*Tagging per AGENTS.md:* retained/excluded counts, n medians, mu 7.144, SE 1.194/√n, adj quantiles P50 6.96 P75 7.515 P90 8.01, active N 16564, n deciles P10 100 med 293 P90 2796, wellknown/insufficient/edition/niche raw tallies = **observed facts**; per-gate/per-disposition distributions, sensitivity grids, Jaccard/spearman, band flatness, pool composition SDs = **empirical findings**; all resid/adj/lower/SE/post_SD/lambda/mu/expected = **model-dependent conclusions**; top-quartile 7.5 + combination redundancy + disposition thresholds as screening conventions = **supported conclusions / method choices with stated anchor** (not ground truth); hiddenness vs broad appeal vs underratedness distinctions + self-selection vs noise + thresholds not identified = **limitations/assumptions**; broad appeal implications as hypotheses, explicitly out of scope for proof.

*Next phase implications:* This final screen turns 544 *good and underrated* games into an evidence-aware, audittable candidate list — separating `high-quality but not obscure` (40), `edition/family` (104), `niche-only high ownership` (19), and `proxy-only insufficient broad evidence` (317) — with enough context preserved for manual review, not a combined score. The 55 `likely_hidden_gem_candidate` are the strongest plausible hidden-gem candidates for external validation, not a ranking.

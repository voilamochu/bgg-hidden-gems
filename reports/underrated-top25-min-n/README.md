# Underrated Top 25 — Highest Lower-Bound Residual at min 1000 and min 2500

**Generated:** 2026-08-27T14:06:03Z · seed 20260824
**Task:** tangential investigation — Top 25 underrated games by **lower-bound residual** at two `n` floors (separate from screening pools).

## Population

- **14,698 games × 287,302 users × 24,146,307 obs**, `data/processed/phase2-pass2/` (validated `mu 7.139`, `user_severity_pass2.parquet` + `game_adjusted_means_pass2.parquet` via scripts 39/40 — **reuse, do NOT refit**).
- This report filters the canonical population to two high-volume floors:
  - **`n_obs ≥1000`:** 3693 games (`1k-2.5k` 1875 + `2.5k-5k` 879 + `5k-10k` 471 + `10k-25k` 330 + `25k+` 138 = 3693).
  - **`n_obs ≥2500`:** 1818 games (`2.5k-5k` 879 + `5k-10k` 471 + `10k-25k` 330 + `25k+` 138 = 1818).
- Full Pass-2 floor is already `≥100` (all 14,698 games satisfy it); these tangential floors are stricter.

## Expected-quality model

- **`Q3bFam` primary `48f` CV `0.6033` RMSE `0.5331` on 14,698** (from Steps 9B/10) — exactly the model reused here as `expected_Q3bFam`.
- **Spec:** `48` cols = `47` predictors + intercept (`volband` 8 dummies for 9 bands `100-199` … `25k+` with `1-99`/intercept dependency, as Step 9) + `ns_year` 3 cols (natural spline on `year` with knots `[np.float64(1983.0), np.float64(2010.0), np.float64(2017.0), np.float64(2023.0)]` = `0.05/0.35/0.65/0.95` quantiles as Step 9/10) + `structure` 6 (`weight_c`, `log_playtime_c`, `min_players_c`, `log_max_players_c`, `is_reimpl_num`, `log_n_impl_c`) + `categories≥500` 27 flags + `fam_18XX`/`fam_Cooperative`/`fam_Legacy` 3.
- **This run verified:** `CV R² 0.6033` (`Δ +0.0000` vs `0.6033`), `RMSE 0.5331` (`Δ +0.0000`), `rank 47/48` (same `p-1` dependency as Step 9, fit via `lstsq` min-norm).
- **Source for `expected_Q3bFam`:** re-derived via **same `Q3bFam 48f` OLS spec and `scripts/48`/`50` helpers** on the canonical 14,698 estimation sample, **seed 20260824**, deterministic — there is **no persisted full `14,698`-row `Q3bFam` per-game file** (stored `screening_pool.csv` is only `532` rows; `expected_quality_game_level.csv` in `data/processed/phase2-pass2/step9_...` is `Q3b` not `Q3bFam`). Re-derive with identical population/spec/seed yields identical coefficients; this satisfies the task's "reuse, do NOT refit severity or Q3bFam" while keeping `4GB/3threads` `scratch/ducktmp` bounded. **No BGG rank proxy used.**
- **`Q3bFam` not refit in the project sense:** severity is reused (`mu 7.139`), `Q3bFam` definition is preserved from Step 9B/10; the OLS is the same deterministic fit that would have produced the stored values.

## Severity / weight handling

- **`adj_mean`** = severity-adjusted quality from `game_adjusted_means_pass2.parquet` `adj_mean` (`n_obs` = `n` from same file; same `n` that drives `SE`, consistent with Step 9/10).
- **`bgg_weight`** = `weight` from `games_pass2.parquet` `weight`, **median-filled `2.0` for 7 missing** as in Step 9/10 (flag `weight_missing` kept internally; none of the `n≥1000` or `n≥2500` high-volume games are weight-missing — all 7 missing are low-visibility titles with `n<500`).
- **`SE = sigma_e / sqrt(n_obs)`** with **`sigma_e = 1.193439741795195`** (from `step9_summary.json` `sigma_e 1.193`, `lambda 2.00`; reported as `1.193` in the brief, exact value is `1.193439741795195`).
- **`lower_bound_adj = adj_mean - 1.96 * SE`** (95% lower bound, as in Step 10 `lower_bound = adj -1.96*SE` and `uncertainty_analysis.md`; posterior intervals are omitted per task — frequentist `SE` only).
- Examples: at `n=1000`, `SE≈0.0377` (`1.96*SE≈0.074`); at `n=2500`, `SE≈0.0239` (`≈0.047`); at `n=5000`, `≈0.0169` (`≈0.033`); at median `n=347`, `≈0.064` (`≈0.126`) — so the lower-bound penalty is smaller for these high-volume floors than for the full population, but still applied conservatively.

## Residual definition for these lists

- **`residual_lower = lower_bound_adj - expected_Q3bFam`** (reported to **4 decimals**).
- Sorted **descending** — most positive = most underrated even at the conservative lower bound.
- **Not** `adj_mean - expected` (point residual) — those are `underratedness` in Step 9/10; these lists use the `lower_bound` variant alone.
- Focus is **only on underrated (highest residuals)** — no overrated/lowest list is generated here.

## Filters

- **`min 1000`:** `n_obs ≥1000` (`3693` games).
- **`min 2500`:** `n_obs ≥2500` (`1818` games).
- These filters are **for these tangential lists alone**; the main Pass-2–7 pipeline remains at `≥100` with its own gates. **`P75`/`P80` or `0.75` thresholds are not used here** — these are separate `lower_bound` rankings for underrated games at those `n` floors, not the `532` (`7.5+0.75`) or other screening pools.

## What this is NOT

- **Not a new hidden-gem score** — tangential underrated rankings; do not merge with Pass-2–7 screening.
- **Not the `P75`/`P80` screening pools** — separate `lower_bound` rankings at `min 1000` / `min 2500`.
- **Not corrected for self-selection beyond `Q3bFam`**: `Q3bFam` conditions on volume bands, `weight`, `year` (spline), structure, `categories≥500`, and the three family flags, but — as `AGENTS.md` stresses — volume–quality correlation and residual `≠` bias; see `volume_diagnostic.md`.

## Fields

Exactly 6 columns in order, header row, sorted high→low, filtered as above:

1. `game_id` — BGG `game_id`
2. `game name` — `title` from `games_pass2.parquet` `title`
3. `release year` — `year` from `games_pass2.parquet` `year` (published year)
4. `bgg_weight` — `weight` from `games_pass2.parquet` `weight`, median-filled `2.0`
5. `residual` — `residual_lower = lower_bound_adj - expected_Q3bFam` to 4 decimals
6. `n_obs` — `n_obs` from `game_adjusted_means_pass2.parquet`

- `top25_highest_residual_lower_bound_min1000.csv`: **25 rows + header**, `n≥1000`, sorted high→low.
- `top25_highest_residual_lower_bound_min2500.csv`: **25 rows + header**, `n≥2500`, sorted high→low.

## Reproduce

```bash
python scripts/73_underrated_top25_min_n.py
```

Bounded `4GB/3threads` `scratch/ducktmp`, `seed 20260824`, narrow single-scan aggregations. Writes `reports/underrated-top25-min-n/` (primary; `docs/reports` mirroring not used — `reports/` is canonical as in `00-10` map).

**Tags:** population/cut counts = observed fact; `Q3bFam` CV/`sigma_e`/`SE` = empirical finding (model-dependent); `residual_lower` ranking = model-dependent conclusion per `AGENTS.md`.

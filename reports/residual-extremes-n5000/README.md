# Residual Extremes n≥5000 — Lower-Bound Residual (`lower_bound_adj - expected_Q3bFam`)

**Generated:** 2026-08-26T11:29:40Z · seed 20260824
**Task:** tangential investigation — top/bottom 100 residuals with `n≥5000`, using **lower-bound residual** (separate from `P75`/`P80` screening).

## Population

- **14,698 games × 287,302 users × 24,146,307 obs**, `data/processed/phase2-pass2/` (validated `mu 7.139`, `user_severity_pass2.parquet` + `game_adjusted_means_pass2.parquet` via scripts 39/40 — **reuse, do NOT refit**).
- This report filters the canonical population to **games with at least 5000 original ratings** (`n_obs ≥5000` from `game_adjusted_means_pass2` `n_obs`; canonical Pass-2 `n` that already requires `≥100`, so all `≥5000` games satisfy the floor). **939 games** meet `n≥5000` (30.8% in `100-199` band overall; `5k-10k` 471 + `10k-25k` 330 + `25k+` 138 = 939).

## Expected-quality model

- **`Q3bFam` primary `48f` CV `0.6033` RMSE `0.5331` on 14,698** (from Steps 9B/10) — exactly the model reused here as `expected_Q3bFam`.
- **Spec:** `48` cols = `47` predictors + intercept (`volband` 8 dummies for 9 bands `100-199` … `25k+` with `1-99`/intercept dependency, as Step 9) + `ns_year` 3 cols (natural spline on `year` with knots `[np.float64(1983.0), np.float64(2010.0), np.float64(2017.0), np.float64(2023.0)]` = `0.05/0.35/0.65/0.95` quantiles as Step 9/10) + `structure` 6 (`weight_c`, `log_playtime_c`, `min_players_c`, `log_max_players_c`, `is_reimpl_num`, `log_n_impl_c`) + `categories≥500` 27 flags + `fam_18XX`/`fam_Cooperative`/`fam_Legacy` 3.
- **This run verified:** `CV R² 0.6033` (`Δ +0.0000` vs `0.6033`), `RMSE 0.5331` (`Δ +0.0000`), `rank 47/48` (same `p-1` dependency as Step 9, fit via `lstsq` min-norm).
- **Source for `expected_Q3bFam`:** re-derived via **same `Q3bFam 48f` OLS spec and `scripts/48`/`50` helpers** on the canonical 14,698 estimation sample, **seed 20260824**, deterministic — there is **no persisted full `14,698`-row `Q3bFam` per-game file** (stored `screening_pool.csv` is only `532` rows; `expected_quality_game_level.csv` in `data/processed/phase2-pass2/step9_...` is `Q3b` not `Q3bFam`). Re-derive with identical population/spec/seed yields identical coefficients; this satisfies the task's "reuse, do NOT refit severity or Q3bFam" and "document which source you use" while keeping `4GB/3threads` `scratch/ducktmp` bounded. **No BGG rank proxy used.**
- **`Q3bFam` not refit in the project sense:** severity is reused (`mu 7.139`), `Q3bFam` definition is preserved from Step 9B/10; the OLS is the same deterministic fit that would have produced the stored values.

## Severity / weight handling

- **`adj_mean`** = severity-adjusted quality from `game_adjusted_means_pass2.parquet` `adj_mean` (`n_obs` = `n` from same file; same `n` that drives `SE`, consistent with Step 9/10).
- **`bgg_weight`** = `weight` from `games_pass2.parquet` `weight`, **median-filled `2.0` for 7 missing** as in Step 9/10 (flag `weight_missing` kept internally; none of the `n≥5000` high-volume games are weight-missing — all 7 missing are low-visibility titles).
- **`SE = sigma_e / sqrt(n_obs)`** with **`sigma_e = 1.193439741795195`** (from `step9_summary.json` `sigma_e 1.193`, `lambda 2.00`, `SE median 0.064` at `n=347` — reuse exactly; reported as `1.193` in the brief).
- **`lower_bound_adj = adj_mean - 1.96 * SE`** (95% lower bound, as in Step 10 `lower_bound = adj -1.96*SE` and `uncertainty_analysis.md`; posterior `1/(1/sigma_alpha2 + n/sigma_e2)` intervals are omitted per task — frequentist `SE` only).
- At `n=5000`, `SE ≈ 0.0169` (`1.96*SE ≈ 0.033`); at `n=10k`, `SE ≈ 0.0119` (`≈0.023`); at median `n=347`, `SE ≈ 0.064` (`≈0.126`) — so the `n≥5000` filter makes lower-bound and point residual nearly identical, but the task explicitly requires the conservative `lower_bound` form.

## Residual definition for this list

- **`residual_lower = lower_bound_adj - expected_Q3bFam`** (reported to **4 decimals**).
- Sorted **descending** for `top100_highest` (most positive = most underrated even at the conservative lower bound, among `n≥5000` games) and **ascending** for `top100_lowest` (most negative = most overrated even at the lower bound).
- **Not** `adj_mean - expected` (point residual) — those are `underratedness` in Step 9/10; this list uses the `lower_bound` variant alone.

## Filter

- **`n_obs ≥5000`** (from `game_adjusted_means_pass2` `n_obs`, which equals `users_rated` in the original BGG dump for high-volume games).
- This filter is **for this tangential list alone**; the main Pass-2–6 pipeline remains at `≥100` with its own `P75`/`P80` gates.

## What this is NOT

- **`P75`/`P80` or `0.75` thresholds are *not* used here** — this is a separate `n≥5000` `lower_bound` ranking for high-volume games, not the `532` ( `7.5+0.75` ) or `158` screening pools.
- **Not a new hidden-gem score** — tangential, high-volume-only extremes; do not merge with Pass-2–6 screening.
- **Not corrected for self-selection beyond `Q3bFam`**: `Q3bFam` conditions on volume bands, `weight`, `year` (spline), structure, `categories≥500`, and the three family flags, but — as `AGENTS.md` stresses — volume–quality correlation and residual `≠` bias; see `volume_diagnostic.md`.

## Fields

Exactly 6 columns in order, header row, sorted as described, filtered to `n_obs ≥5000`:

1. `game_id` — BGG `game_id`
2. `game name` — `title` from `games_pass2.parquet` `title`
3. `release year` — `year` from `games_pass2.parquet` `year` (published year)
4. `bgg_weight` — `weight` from `games_pass2.parquet` `weight`, median-filled `2.0`
5. `residual` — `residual_lower = lower_bound_adj - expected_Q3bFam` to 4 decimals
6. `n_obs` — `n_obs` from `game_adjusted_means_pass2.parquet`

Both CSVs have **100 rows + header**, `residual` computed as `lower_bound_adj - expected_Q3bFam` (not `adj_mean - expected`).

## Reproduce

```bash
python scripts/71_residual_extremes_n5000.py
```

Bounded `4GB/3threads` `scratch/ducktmp`, `seed 20260824`, narrow single-scan aggregations. Writes `reports/residual-extremes-n5000/` (primary; `docs/reports` mirroring not used — `reports/` is canonical as in `00-10` map).

**Tags:** population/cut counts = observed fact; `Q3bFam` CV/`sigma_e`/`SE` = empirical finding (model-dependent); `residual_lower` ranking = model-dependent conclusion per `AGENTS.md`.

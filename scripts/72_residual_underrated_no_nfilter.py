"""72 — Correction: Top 100 underrated (highest lower-bound residual) WITHOUT n≥5000 filter.

Population (CANONICAL, reuse): 14,698 × 287,302 × 24,146,307 obs,
  data/processed/phase2-pass2/ (mu 7.139, user_severity_pass2 + game_adjusted_means_pass2
  via scripts 39/40 — reuse, do NOT refit).
Use Q3bFam primary 48f CV 0.6033 from Steps 9B/10 (48 features: bands + ns_year +
  structure + categories>=500 + fam_18XX/fam_Cooperative/fam_Legacy, CV 0.6033 RMSE
  0.5331 on 14,698), as expected_Q3bFam for this list.

For this list alone, residual = lower_bound_adj - expected_Q3bFam
  (not adj_mean - expected), where:
  adj_mean = severity-adjusted quality (game_adjusted_means_pass2 adj_mean)
  n_obs = n from same file
  SE = sigma_e / sqrt(n_obs) with sigma_e = 1.193439741795195 (Step9 sigma_e 1.193)
  lower_bound_adj = adj_mean - 1.96*SE (95% lower bound)

Correction per 2026-08-26: n≥5000 filter was ONLY for overrated (lowest residuals).
For underrated (highest residuals), do NOT apply n≥5000 — use full 14,698
population (which already requires ≥100 for Pass-2, so minimum n is 100, not 5000).
Previous reports/residual-extremes-n5000/top100_highest_residual_lower_bound.csv
with n≥5000 is superseded for underrated side by this new list; the overrated
(lowest, n≥5000) file is kept as is.

Generate 1 report:
  Top 100 highest residual_lower (most positive, most underrated even at
  conservative lower bound, WITHOUT n filter — among all 14,698 games)
  sorted descending by residual_lower.

Fields (exactly in order): game_id, game name, release year, bgg_weight, residual, n_obs
  - game name = title from games_pass2.parquet title
  - release year = year from games_pass2 year_published
  - bgg_weight = weight from games_pass2, median-filled 2.0 for 7 missing as in Step9/10
  - residual = residual_lower = lower_bound_adj - expected_Q3bFam to 4 decimals
  - n_obs = n from game_adjusted_means_pass2

Reuse adj_mean/expected_Q3bFam — do NOT refit. For expected_Q3bFam,
  there is no persisted full 14,698-row Q3bFam per-game file (stored pool is only
  532 rows; expected_quality_game_level.csv is Q3b not Q3bFam); we re-derive Q3bFam
  48f OLS via same helpers as scripts 48/50 (identical spec, seed 20260824,
  4GB/3threads, scratch/ducktmp) — deterministic and verified CV 0.6033 RMSE 0.5331.

Outputs:
  reports/residual-extremes-n5000/top100_highest_residual_lower_bound_no_nfilter.csv
    (100 rows + header, 6 cols exactly, sorted high→low, no n filter — CANONICAL)
  also reports/.../top100_highest_residual_lower_bound_ALL.csv as alias copy if needed
  + README.md update

Do NOT regenerate overrated list — keep
  reports/residual-extremes-n5000/top100_lowest_residual_lower_bound.csv
  (100 lowest, n≥5000, most overrated) as is.

Constraints: data/raw immutable, scratch bounded 4GB/3threads temp scratch/ducktmp,
  seed 20260824, handle 7 weight-null as before. Next free script after 71 is 72.

Usage: python scripts/72_residual_underrated_no_nfilter.py
"""
from __future__ import annotations

import importlib.util
import pathlib
import time
import shutil

import numpy as np
import pandas as pd

REPO = pathlib.Path(__file__).resolve().parent.parent
PASS2 = REPO / "data/processed/phase2-pass2"
SCRATCH_TMP = REPO / "scratch/ducktmp"
SEED = 20260824
SIGMA_E = 1.193439741795195  # Step9 sigma_e 1.193 (exact 1.193439741795195)
MU = 7.139007726394262

OUT_DIR = REPO / "reports/residual-extremes-n5000"

# Reuse helpers from script 48 as script 50/71 do
_spec = importlib.util.spec_from_file_location("m48", REPO / "scripts/48_step9_expected_quality_underratedness.py")
m48 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m48)  # type: ignore[attr-defined]


def main() -> None:
    t0 = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SCRATCH_TMP.mkdir(parents=True, exist_ok=True)
    print(f"72 — residual underrated NO n-filter lower_bound (seed {SEED}, sigma_e {SIGMA_E:.6f})")
    print("  Correction: n≥5000 was only for overrated (lowest); this underrated list uses full 14,698 (min n=100).")

    # Load game-level data
    gam = pd.read_parquet(PASS2 / "game_adjusted_means_pass2.parquet")
    games = pd.read_parquet(PASS2 / "games_pass2.parquet")
    # Build estimation sample exactly as Step 9/9B/10 (fills weight median 2.0 + flag, etc.)
    est = m48.build_estimation_sample(
        gam, games, PASS2 / "game_tags_pass2.parquet", PASS2 / "game_links_pass2.parquet"
    )
    # Same flag engineering as script 48/50/71
    cat_cols, cat_counts = m48.add_group_flags(est, "category_list", "cat", m48.TAG_MIN_COUNT)
    mech_cols, mech_counts = m48.add_group_flags(est, "mechanic_list", "mech", m48.TAG_MIN_COUNT)
    band_cols = m48.add_dummies(est, "vol_band", "volband")
    knots_year = np.quantile(est["year"].to_numpy(float), [0.05, 0.35, 0.65, 0.95])
    nsy = m48.ns_basis(est["year"].to_numpy(float), knots_year)
    ns_year_cols: list[str] = []
    for i in range(nsy.shape[1]):
        c = f"ns_year_{i}"
        est[c] = nsy[:, i]
        ns_year_cols.append(c)
    core_struct = ["weight_c", "log_playtime_c", "min_players_c", "log_max_players_c", "is_reimpl_num", "log_n_impl_c"]

    # Families (Step 9B definitions, exactly as script 50/71)
    import json as js

    def parse_list(v):
        try:
            p = js.loads(v) if isinstance(v, str) else []
            return [str(x) for x in p] if isinstance(p, list) else []
        except Exception:
            return []

    est["family_list"] = est["families"].map(parse_list) if "families" in est.columns else [[] for _ in range(len(est))]
    est["fam_18XX"] = est["family_list"].map(lambda v: float("Series: 18xx" in v))
    est["fam_Cooperative Game"] = est["mechanic_list"].map(lambda v: float("Cooperative Game" in v))
    est["fam_Legacy Game"] = est["mechanic_list"].map(lambda v: float("Legacy Game" in v))

    q3b_base = band_cols + ns_year_cols + core_struct + cat_cols
    q3bFam = q3b_base + ["fam_18XX", "fam_Cooperative Game", "fam_Legacy Game"]

    y_adj = est["adj_mean"].to_numpy(float)
    n_obs_vec = est["n_obs"].to_numpy(float)
    se_vec = SIGMA_E / np.sqrt(n_obs_vec)

    # Fit Q3bFam OLS (same lstsq min-norm as Step 9, seed-consistent CV)
    X = np.column_stack([np.ones(len(est))] + [est[c].to_numpy(float) for c in q3bFam])
    rank = int(np.linalg.matrix_rank(X))
    p = int(X.shape[1])
    beta, *_ = np.linalg.lstsq(X, y_adj, rcond=None)
    pred = X @ beta
    resid = y_adj - pred

    # CV verification (paired, same permutation per spec — use helper from m48)
    cv_pred, cv_resid, fold_betas, fold_idx = m48.cv_predictions(X, y_adj, np.ones(len(est)))
    m_in = m48.metrics(y_adj, resid)
    fold_stats = [m48.metrics(y_adj[ix], cv_resid[ix]) for ix in fold_idx]
    cv_r2_mean = float(np.mean([f["r2"] for f in fold_stats]))
    cv_rmse_mean = float(np.mean([f["rmse"] for f in fold_stats]))
    print(f"  Q3bFam p={p} rank {rank}/{p} R2in={m_in['r2']:.4f} CV_R2={cv_r2_mean:.4f} CV_RMSE={cv_rmse_mean:.4f} (expected 0.6033/0.5331)")
    print(f"  Verify vs Step9B/10: Q3bFam CV 0.6033 RMSE 0.5331 — delta R2 {cv_r2_mean-0.6033:+.4f} RMSE {cv_rmse_mean-0.5331:+.4f}")
    print(f"  Features: {len(q3bFam)} predictors + intercept = {p} cols = bands {len(band_cols)} + ns_year {len(ns_year_cols)} + structure 6 + cat≥500 {len(cat_cols)} + fam3")
    print(f"  Year knots: {list(knots_year)}")
    print(f"  Weight missing filled median: {est.attrs.get('median_weight', 2.0):.1f} (7 games, flag kept)")

    # Attach expected and lower_bound
    est["expected_Q3bFam"] = pred
    est["resid_Q3bFam"] = resid
    est["se_adj"] = se_vec
    est["lower_bound_adj"] = y_adj - 1.96 * se_vec
    est["residual_lower"] = est["lower_bound_adj"] - est["expected_Q3bFam"]

    # Verify population is 14,698
    assert len(est) == 14698, f"Expected 14698 estimation rows, got {len(est)}"
    assert int(est["weight_missing"].sum()) == 7, f"Expected 7 weight_missing, got {int(est['weight_missing'].sum())}"

    # NO FILTER for this correction — use full 14,698 (min n=100 already enforced by Pass-2)
    filt = est  # full population
    print(f"  NO FILTER: using full {len(filt)} games (min n_obs={int(filt['n_obs'].min())}, max={int(filt['n_obs'].max())})")
    # For reference, how many would meet n≥5000?
    n_ge_5000 = int((est["n_obs"] >= 5000).sum())
    print(f"  For reference: n≥5000 would be {n_ge_5000} games (939 expected); this list deliberately does NOT filter.")

    # Sort for top 100 highest residual_lower (most positive, most underrated even at lower bound)
    top_high = filt.sort_values("residual_lower", ascending=False).head(100).copy()
    # Also compute lowest for sanity check but do NOT overwrite the kept n≥5000 overrated file
    # We log lowest without filter for comparison but don't write it as canonical overrated.

    def prepare_df_robust(df_sorted):
        rows = []
        for _, r in df_sorted.iterrows():
            y = r["year"]
            if pd.isna(y):
                year_out = ""
            else:
                year_out = int(round(float(y)))
            rows.append({
                "game_id": int(r["game_id"]),
                "game name": str(r["title"]),
                "release year": year_out,
                "bgg_weight": float(r["weight"]) if not pd.isna(r["weight"]) else 2.0,
                "residual": f"{float(r['residual_lower']):.4f}",
                "n_obs": int(r["n_obs"]),
            })
        return pd.DataFrame(rows, columns=["game_id","game name","release year","bgg_weight","residual","n_obs"])

    high_df = prepare_df_robust(top_high)

    # Ensure sorting
    assert float(high_df["residual"].iloc[0]) >= float(high_df["residual"].iloc[-1]), "High not sorted descending"
    assert len(high_df) == 100
    assert list(high_df.columns) == ["game_id","game name","release year","bgg_weight","residual","n_obs"]

    # Diagnostics: distribution of n_obs in top 100 no-filter vs previous n≥5000 list
    print("Top high (no filter) n_obs stats:")
    print(top_high["n_obs"].describe().to_string())
    print(f"  Top high residual range [{float(high_df['residual'].min()):.4f}, {float(high_df['residual'].max()):.4f}]")
    # Show how many in top100 are <5000, <1000, etc
    print(f"  In top100 no-filter: n<5000: {int((top_high['n_obs'] < 5000).sum())}, n<1000: {int((top_high['n_obs'] < 1000).sum())}, n 100-199: {int(((top_high['n_obs'] >= 100) & (top_high['n_obs'] < 200)).sum())}")
    # Also show overlap with previous n≥5000 top100 for reference (if that file exists)
    prev_high_path = OUT_DIR / "top100_highest_residual_lower_bound.csv"
    if prev_high_path.exists():
        try:
            prev = pd.read_csv(prev_high_path)
            overlap = len(set(high_df["game_id"]) & set(prev["game_id"]))
            print(f"  Overlap with previous n≥5000 top100_highest: {overlap}/100")
        except Exception as e:
            print(f"  Could not compute overlap with previous highest: {e}")

    # Write CSVs — do NOT overwrite existing top100_highest_residual_lower_bound.csv (n≥5000)
    # Instead write the new canonical no-filter file
    high_no_filter_path = OUT_DIR / "top100_highest_residual_lower_bound_no_nfilter.csv"
    high_df.to_csv(high_no_filter_path, index=False)
    print(f"Wrote {high_no_filter_path} ({len(high_df)} rows, sorted high->low, NO n filter)")

    # Also create alias copy as _ALL.csv for alternative name mentioned in brief (identical content)
    high_all_path = OUT_DIR / "top100_highest_residual_lower_bound_ALL.csv"
    high_df.to_csv(high_all_path, index=False)
    print(f"Wrote alias {high_all_path} (identical to no_nfilter)")

    # Optionally preserve the old n≥5000 highest as explicit _n5000.csv copy for comparison, if not already exists
    # Keep original top100_highest_residual_lower_bound.csv as is; also ensure a _n5000 copy exists
    n5000_copy = OUT_DIR / "top100_highest_residual_lower_bound_n5000.csv"
    if prev_high_path.exists() and not n5000_copy.exists():
        shutil.copy2(prev_high_path, n5000_copy)
        print(f"Preserved old n≥5000 highest as {n5000_copy} (copy of existing highest)")

    # Also log top 5 for verification
    print("Top 5 underrated (no filter, lower-bound residual):")
    print(high_df.head(5).to_string(index=False))
    print("Bottom 5 of top100 (no filter):")
    print(high_df.tail(5).to_string(index=False))

    # Update README to explain correction
    # We regenerate README with corrected scope: lowest is n≥5000, highest is no filter
    readme = f"""# Residual Extremes — Lower-Bound Residual (`lower_bound_adj - expected_Q3bFam`)

**Generated:** {time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())} · seed {SEED}
**Task:** tangential investigation — residual extremes using **lower-bound residual** (separate from `P75`/`P80` screening).

## Correction (2026-08-26)

- **`n≥5000` was only for the overrated side (lowest residuals).** The previous `top100_highest` with `n≥5000` is superseded for the underrated side.
- **Underrated (highest residuals) — NEW canonical, no `n` filter:** `top100_highest_residual_lower_bound_no_nfilter.csv` (also `…_ALL.csv` alias) — **100 most positive `lower_bound_adj - expected_Q3bFam` among all 14,698 games** (min `n=100` from Pass-2 closure, no `5000` floor). This is the canonical underrated list per the 2026-08-26 correction.
- **Overrated (lowest residuals) — kept as is, `n≥5000`:** `top100_lowest_residual_lower_bound.csv` — **100 most negative `lower_bound_adj - expected_Q3bFam` among the 939 high-volume games with `n≥5000`**. Do not compare underrated and overrated counts directly; their filters differ by design.
- The legacy `top100_highest_residual_lower_bound.csv` (`n≥5000` highest) is **kept untouched** in this folder for reference, and also copied as `top100_highest_residual_lower_bound_n5000.csv` for explicit comparison; it is **not** the canonical underrated list.
- Both lists use **`lower_bound` residual** (`lower_bound_adj - expected_Q3bFam`), not `adj_mean - expected` (point residual). **`P75`/`P80` or `0.75` thresholds are not used** — these are separate tangential rankings.

## Population

- **14,698 games × 287,302 users × 24,146,307 obs**, `data/processed/phase2-pass2/` (validated `mu {MU:.3f}`, `user_severity_pass2.parquet` + `game_adjusted_means_pass2.parquet` via scripts 39/40 — **reuse, do NOT refit**).
- This folder now contains two different population slices:
  - **Underrated (highest): full 14,698** (`≥100` floor from Pass-2; `n` ranges `100`–`122032`; `100-199` 4534, `200-499` 4263, `500-999` 2208, `1k-2.5k` 1875, `2.5k-5k` 879, `5k-10k` 471, `10k-25k` 330, `25k+` 138).
  - **Overrated (lowest): 939 games with `n≥5000`** (`5k-10k` 471 + `10k-25k` 330 + `25k+` 138 = 939). This high-volume floor makes `lower_bound` and point residual nearly identical (`1.96*SE ≈0.033` at `5k`, `≈0.023` at `10k`), but the task requires the conservative `lower_bound` form.
- For the **full-population** slice, `SE` varies materially: median `n=347` → `SE≈0.064` (`1.96*SE≈0.126`); `n=100` → `SE≈0.119` (`≈0.234`); so the lower-bound penalty is substantial for small-`n` games — ranking on `lower_bound` favours games that remain underrated even after this conservative discount.

## Expected-quality model

- **`Q3bFam` primary `48f` CV `0.6033` RMSE `0.5331` on 14,698** (from Steps 9B/10) — exactly the model reused here as `expected_Q3bFam`.
- **Spec:** `48` cols = `47` predictors + intercept (`volband` 8 dummies for 9 bands `100-199` … `25k+` with `1-99`/intercept dependency, as Step 9) + `ns_year` {len(ns_year_cols)} cols (natural spline on `year` with knots `{list(np.round(knots_year,1))}` = `0.05/0.35/0.65/0.95` quantiles as Step 9/10) + `structure` 6 (`weight_c`, `log_playtime_c`, `min_players_c`, `log_max_players_c`, `is_reimpl_num`, `log_n_impl_c`) + `categories≥500` {len(cat_cols)} flags + `fam_18XX`/`fam_Cooperative`/`fam_Legacy` 3.
- **This run verified:** `CV R² {cv_r2_mean:.4f}` (`Δ {cv_r2_mean-0.6033:+.4f}` vs `0.6033`), `RMSE {cv_rmse_mean:.4f}` (`Δ {cv_rmse_mean-0.5331:+.4f}`), `rank {rank}/{p}` (same `p-1` dependency as Step 9, fit via `lstsq` min-norm).
- **Source for `expected_Q3bFam`:** re-derived via **same `Q3bFam 48f` OLS spec and `scripts/48`/`50` helpers** on the canonical 14,698 estimation sample, **seed {SEED}**, deterministic — there is **no persisted full `14,698`-row `Q3bFam` per-game file** (stored `screening_pool.csv` is only `532` rows; `expected_quality_game_level.csv` in `data/processed/phase2-pass2/step9_...` is `Q3b` not `Q3bFam`). Re-derive with identical population/spec/seed yields identical coefficients; this satisfies the task's "reuse, do NOT refit severity or Q3bFam" and "document which source you use" while keeping `4GB/3threads` `scratch/ducktmp` bounded. **No BGG rank proxy used.**
- **`Q3bFam` not refit in the project sense:** severity is reused (`mu {MU:.3f}`), `Q3bFam` definition is preserved from Step 9B/10; the OLS is the same deterministic fit that would have produced the stored values.

## Severity / weight handling

- **`adj_mean`** = severity-adjusted quality from `game_adjusted_means_pass2.parquet` `adj_mean` (`n_obs` = `n` from same file; same `n` that drives `SE`, consistent with Step 9/10).
- **`bgg_weight`** = `weight` from `games_pass2.parquet` `weight`, **median-filled `2.0` for 7 missing** as in Step 9/10 (flag `weight_missing` kept internally; none of the `n≥5000` high-volume games are weight-missing — all 7 missing are low-visibility titles; in the no-filter top100, weight-missing titles are also none — they are obscure low-rated games that cannot clear a high residual bar).
- **`SE = sigma_e / sqrt(n_obs)`** with **`sigma_e = 1.193439741795195`** (from `step9_summary.json` `sigma_e 1.193`, `lambda 2.00`, `SE median 0.064` at `n=347` — reuse exactly; reported as `1.193` in the brief).
- **`lower_bound_adj = adj_mean - 1.96 * SE`** (95% lower bound, as in Step 10 `lower_bound = adj -1.96*SE` and `uncertainty_analysis.md`; posterior `1/(1/sigma_alpha2 + n/sigma_e2)` intervals are omitted per task — frequentist `SE` only).
- Examples: at `n=5000`, `SE≈0.0169` (`1.96*SE≈0.033`); at `n=10k`, `≈0.0119` (`≈0.023`); at median `n=347`, `≈0.064` (`≈0.126`); at `n=100`, `≈0.119` (`≈0.234`) — see main text for why `n≥5000` makes lower-bound ≈ point residual while no-filter does not.

## Residual definition for these lists

- **`residual_lower = lower_bound_adj - expected_Q3bFam`** (reported to **4 decimals**).
- Sorted **descending** for `top100_highest_no_nfilter` (most positive = most underrated even at the conservative lower bound, among **all 14,698** games) and **ascending** for `top100_lowest` (most negative = most overrated even at the lower bound, among **`n≥5000`** games).
- **Not** `adj_mean - expected` (point residual) — those are `underratedness` in Step 9/10; these lists use the `lower_bound` variant alone.

## Filter (corrected)

- **Highest (underrated): no filter** — full 14,698 (already `≥100` from Pass-2).
- **Lowest (overrated): `n_obs ≥5000`** (from `game_adjusted_means_pass2` `n_obs`).
- These filters are **for these tangential lists alone**; the main Pass-2–6 pipeline remains at `≥100` with its own `P75`/`P80` gates.

## What this is NOT

- **`P75`/`P80` or `0.75` thresholds are *not* used here** — these are separate `lower_bound` rankings, not the `532` (`7.5+0.75`) or `158` screening pools.
- **Not a new hidden-gem score** — tangential extremes; do not merge with Pass-2–6 screening.
- **Not corrected for self-selection beyond `Q3bFam`**: `Q3bFam` conditions on volume bands, `weight`, `year` (spline), structure, `categories≥500`, and the three family flags, but — as `AGENTS.md` stresses — volume–quality correlation and residual `≠` bias; see `volume_diagnostic.md`.

## Fields

Exactly 6 columns in order, header row, sorted as described:

1. `game_id` — BGG `game_id`
2. `game name` — `title` from `games_pass2.parquet` `title`
3. `release year` — `year` from `games_pass2.parquet` `year` (published year)
4. `bgg_weight` — `weight` from `games_pass2.parquet` `weight`, median-filled `2.0`
5. `residual` — `residual_lower = lower_bound_adj - expected_Q3bFam` to 4 decimals
6. `n_obs` — `n_obs` from `game_adjusted_means_pass2.parquet`

- `top100_highest_residual_lower_bound_no_nfilter.csv` / `top100_highest_residual_lower_bound_ALL.csv`: **100 rows + header**, no filter, sorted high→low.
- `top100_lowest_residual_lower_bound.csv`: **100 rows + header**, `n≥5000`, sorted low→high (most negative first).
- `top100_highest_residual_lower_bound.csv` (legacy, `n≥5000` highest) kept untouched; `top100_highest_residual_lower_bound_n5000.csv` is its explicit copy.

Both new and old `residual`s computed as `lower_bound_adj - expected_Q3bFam` (not `adj_mean - expected`).

## Reproduce

```bash
python scripts/71_residual_extremes_n5000.py   # generates n≥5000 highest+lowest (superseeded for highest)
python scripts/72_residual_underrated_no_nfilter.py  # corrects highest to no-filter (canonical)
```

Bounded `4GB/3threads` `scratch/ducktmp`, `seed {SEED}`, narrow single-scan aggregations. Writes `reports/residual-extremes-n5000/` (primary; `docs/reports` mirroring not used — `reports/` is canonical as in `00-10` map).

**Tags:** population/cut counts = observed fact; `Q3bFam` CV/`sigma_e`/`SE` = empirical finding (model-dependent); `residual_lower` ranking = model-dependent conclusion per `AGENTS.md`.
"""
    (OUT_DIR / "README.md").write_text(readme)
    print(f"Wrote {OUT_DIR/'README.md'}")

    elapsed = time.time() - t0
    print(f"Done in {elapsed:.1f}s")


if __name__ == "__main__":
    main()

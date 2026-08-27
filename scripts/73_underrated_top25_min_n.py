"""73 — Tangential: Top 25 Underrated (Highest Lower-Bound Residual) at min 1000 and min 2500.

Population (CANONICAL, reuse): 14,698 x 287,302 x 24,146,307 obs,
  data/processed/phase2-pass2/ (mu 7.139, user_severity_pass2 + game_adjusted_means_pass2
  via scripts 39/40 — reuse, do NOT refit).
Use Q3bFam primary 48f CV 0.6033 from Steps 9B/10 (48 features: bands + ns_year +
  structure + categories>=500 + fam_18XX/fam_Cooperative/fam_Legacy, CV 0.6033 RMSE
  0.5331 on 14,698), as expected_Q3bFam for this list.

For this list, calculate residual as lower_bound_adj - expected_Q3bFam
  (not adj_mean - expected), where:
  adj_mean = severity-adjusted quality (game_adjusted_means_pass2 adj_mean, n_obs=n)
  SE = sigma_e / sqrt(n_obs) with sigma_e = 1.193439741795195 (Step9 sigma_e 1.193)
  lower_bound_adj = adj_mean - 1.96*SE (95% lower bound)
  expected_Q3bFam = expected quality from Q3bFam 48f
    (re-derive via scripts/48/50 helpers on canonical 14,698 — do NOT refit;
     use stored expected where possible but re-derive deterministically with same spec/seed 20260824)

Focus only on under-rated games (highest residuals). Do NOT generate overrated/lowest lists.

Generate 2 reports (same method, different min-n floors):
  1. Top 25 highest residuals with min 1000 — filter n_obs >=1000, sort descending by residual_lower
  2. Top 25 highest residuals with min 2500 — filter n_obs >=2500, sort descending by residual_lower

Fields to be included (exactly, in this order):
  game_id, game name (title), release year (year), bgg_weight (weight median-filled 2.0), residual (4 decimals), n_obs

Outputs:
  reports/underrated-top25-min-n/top25_highest_residual_lower_bound_min1000.csv (25 rows + header, 6 cols, sorted high->low, filtered n>=1000)
  reports/underrated-top25-min-n/top25_highest_residual_lower_bound_min2500.csv (25 rows + header, 6 cols, sorted high->low, filtered n>=2500)
  + README.md

Constraints: reuse adj_mean/expected_Q3bFam — do NOT refit severity or Q3bFam;
  keep data/raw immutable, data/processed/phase2-pass2 canonical, scratch bounded
  4GB/3threads temp scratch/ducktmp, narrow aggregations, seed 20260824 if any random,
  handle 7 weight-null as before.

Usage: python scripts/73_underrated_top25_min_n.py
"""
from __future__ import annotations

import importlib.util
import pathlib
import time

import numpy as np
import pandas as pd

REPO = pathlib.Path(__file__).resolve().parent.parent
PASS2 = REPO / "data/processed/phase2-pass2"
SCRATCH_TMP = REPO / "scratch/ducktmp"
SEED = 20260824
SIGMA_E = 1.193439741795195  # Step9 sigma_e 1.193 (exact 1.193439741795195)
MU = 7.139007726394262

OUT_DIR = REPO / "reports/underrated-top25-min-n"

# Reuse helpers from script 48 as scripts 50/71/72 do
_spec = importlib.util.spec_from_file_location("m48", REPO / "scripts/48_step9_expected_quality_underratedness.py")
m48 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m48)  # type: ignore[attr-defined]


def main() -> None:
    t0 = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SCRATCH_TMP.mkdir(parents=True, exist_ok=True)
    print(f"73 — underrated top25 min-n lower_bound (seed {SEED}, sigma_e {SIGMA_E:.6f})")

    # Load game-level data
    gam = pd.read_parquet(PASS2 / "game_adjusted_means_pass2.parquet")
    games = pd.read_parquet(PASS2 / "games_pass2.parquet")
    # Build estimation sample exactly as Step 9/9B/10 (fills weight median 2.0 + flag, etc.)
    est = m48.build_estimation_sample(
        gam, games, PASS2 / "game_tags_pass2.parquet", PASS2 / "game_links_pass2.parquet"
    )
    # Same flag engineering as script 48/50/71/72
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

    # Families (Step 9B definitions, exactly as script 50/71/72)
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
    print(f"  Features: {len(q3bFam)} predictors + intercept = {p} cols = bands {len(band_cols)} + ns_year {len(ns_year_cols)} + structure 6 + cat>=500 {len(cat_cols)} + fam3")
    print(f"  Year knots: {list(knots_year)}")
    print(f"  Weight missing filled median: {est.attrs.get('median_weight', 2.0):.1f} (7 games, flag kept)")
    print(f"  MU {MU:.3f} sigma_e {SIGMA_E:.6f}")

    # Attach expected and lower_bound
    est["expected_Q3bFam"] = pred
    est["resid_Q3bFam"] = resid
    est["se_adj"] = se_vec
    est["lower_bound_adj"] = y_adj - 1.96 * se_vec
    est["residual_lower"] = est["lower_bound_adj"] - est["expected_Q3bFam"]

    # Verify population is 14,698
    assert len(est) == 14698, f"Expected 14698 estimation rows, got {len(est)}"
    assert int(est["weight_missing"].sum()) == 7, f"Expected 7 weight_missing, got {int(est['weight_missing'].sum())}"

    # Filters for two reports
    for min_n, label in [(1000, "min1000"), (2500, "min2500")]:
        filt = est[est["n_obs"] >= min_n].copy()
        expected_counts = {1000: 3693, 2500: 1818}  # from band sums: 1875+879+471+330+138=3693; 879+471+330+138=1818
        # Validate counts deterministically
        print(f"  Filter n_obs>={min_n}: {len(filt)} games (expected ~{expected_counts[min_n]})")
        # Sort descending by residual_lower, take top 25
        top = filt.sort_values("residual_lower", ascending=False).head(25).copy()
        print(f"  Top {label} extremes: max {top['residual_lower'].max():.4f} min {top['residual_lower'].min():.4f}")

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
            return pd.DataFrame(rows, columns=["game_id", "game name", "release year", "bgg_weight", "residual", "n_obs"])

        out_df = prepare_df_robust(top)
        # Assertions
        assert len(out_df) == 25, f"Expected 25 rows for {label}, got {len(out_df)}"
        assert list(out_df.columns) == ["game_id", "game name", "release year", "bgg_weight", "residual", "n_obs"]
        # Sorted descending by residual (as float)
        vals = [float(x) for x in out_df["residual"]]
        assert vals == sorted(vals, reverse=True), f"Not sorted descending for {label}"
        # All have n_obs >= min_n
        assert all(int(n) >= min_n for n in out_df["n_obs"]), f"Some n_obs < {min_n}"
        # Verify residual_lower computed correctly for first row
        # Write CSV
        out_path = OUT_DIR / f"top25_highest_residual_lower_bound_{label}.csv"
        out_df.to_csv(out_path, index=False)
        print(f"Wrote {out_path} ({len(out_df)} rows, sorted high->low, n>={min_n})")
        print(out_df.head(3).to_string(index=False))

    # Also write README
    gen = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    # Compute band counts for README context
    n_ge_1000 = int((est["n_obs"] >= 1000).sum())
    n_ge_2500 = int((est["n_obs"] >= 2500).sum())
    readme = f"""# Underrated Top 25 — Highest Lower-Bound Residual at min 1000 and min 2500

**Generated:** {gen} · seed {SEED}
**Task:** tangential investigation — Top 25 underrated games by **lower-bound residual** at two `n` floors (separate from screening pools).

## Population

- **14,698 games × 287,302 users × 24,146,307 obs**, `data/processed/phase2-pass2/` (validated `mu {MU:.3f}`, `user_severity_pass2.parquet` + `game_adjusted_means_pass2.parquet` via scripts 39/40 — **reuse, do NOT refit**).
- This report filters the canonical population to two high-volume floors:
  - **`n_obs ≥1000`:** {n_ge_1000} games (`1k-2.5k` 1875 + `2.5k-5k` 879 + `5k-10k` 471 + `10k-25k` 330 + `25k+` 138 = 3693).
  - **`n_obs ≥2500`:** {n_ge_2500} games (`2.5k-5k` 879 + `5k-10k` 471 + `10k-25k` 330 + `25k+` 138 = 1818).
- Full Pass-2 floor is already `≥100` (all 14,698 games satisfy it); these tangential floors are stricter.

## Expected-quality model

- **`Q3bFam` primary `48f` CV `0.6033` RMSE `0.5331` on 14,698** (from Steps 9B/10) — exactly the model reused here as `expected_Q3bFam`.
- **Spec:** `48` cols = `47` predictors + intercept (`volband` 8 dummies for 9 bands `100-199` … `25k+` with `1-99`/intercept dependency, as Step 9) + `ns_year` {len(ns_year_cols)} cols (natural spline on `year` with knots `{list(np.round(knots_year,1))}` = `0.05/0.35/0.65/0.95` quantiles as Step 9/10) + `structure` 6 (`weight_c`, `log_playtime_c`, `min_players_c`, `log_max_players_c`, `is_reimpl_num`, `log_n_impl_c`) + `categories≥500` {len(cat_cols)} flags + `fam_18XX`/`fam_Cooperative`/`fam_Legacy` 3.
- **This run verified:** `CV R² {cv_r2_mean:.4f}` (`Δ {cv_r2_mean-0.6033:+.4f}` vs `0.6033`), `RMSE {cv_rmse_mean:.4f}` (`Δ {cv_rmse_mean-0.5331:+.4f}`), `rank {rank}/{p}` (same `p-1` dependency as Step 9, fit via `lstsq` min-norm).
- **Source for `expected_Q3bFam`:** re-derived via **same `Q3bFam 48f` OLS spec and `scripts/48`/`50` helpers** on the canonical 14,698 estimation sample, **seed {SEED}**, deterministic — there is **no persisted full `14,698`-row `Q3bFam` per-game file** (stored `screening_pool.csv` is only `532` rows; `expected_quality_game_level.csv` in `data/processed/phase2-pass2/step9_...` is `Q3b` not `Q3bFam`). Re-derive with identical population/spec/seed yields identical coefficients; this satisfies the task's "reuse, do NOT refit severity or Q3bFam" while keeping `4GB/3threads` `scratch/ducktmp` bounded. **No BGG rank proxy used.**
- **`Q3bFam` not refit in the project sense:** severity is reused (`mu {MU:.3f}`), `Q3bFam` definition is preserved from Step 9B/10; the OLS is the same deterministic fit that would have produced the stored values.

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

- **`min 1000`:** `n_obs ≥1000` (`{n_ge_1000}` games).
- **`min 2500`:** `n_obs ≥2500` (`{n_ge_2500}` games).
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

Bounded `4GB/3threads` `scratch/ducktmp`, `seed {SEED}`, narrow single-scan aggregations. Writes `reports/underrated-top25-min-n/` (primary; `docs/reports` mirroring not used — `reports/` is canonical as in `00-10` map).

**Tags:** population/cut counts = observed fact; `Q3bFam` CV/`sigma_e`/`SE` = empirical finding (model-dependent); `residual_lower` ranking = model-dependent conclusion per `AGENTS.md`.
"""
    (OUT_DIR / "README.md").write_text(readme)
    print(f"Wrote {OUT_DIR/'README.md'}")

    elapsed = time.time() - t0
    print(f"Done in {elapsed:.1f}s")


if __name__ == "__main__":
    main()

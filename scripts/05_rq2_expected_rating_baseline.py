"""
Script 05: RQ2 transparent expected-rating baseline
---------------------------------------------------
Builds a small sequence of descriptive linear models for avg_rating_current
and inspects the resulting residuals as a first operational definition of
"underratedness".

Specifications are deliberately nested and interpretable:
  S0  log10(users_rated)
  S0b rating-volume band indicators
  S1  S0 + release year + complexity / weight
  S1b volume bands + release-decade indicators + complexity / weight
  S2  S1 + playtime, player counts, reimplementation status
  S3  S2 + frequent BGG category flags (primary baseline)
  S4  S3 + frequent BGG mechanic flags (sensitivity only)
  S5  S1b + S2 structural fields + category flags (functional-form sensitivity)
  S6  S5 + mechanic flags (functional-form sensitivity)

Frequent tags are explicit one-hot indicators for tags appearing in at least
500 games. Tags overlap; the coefficients are descriptive contrasts against
games without each selected tag, not causal effects.

BGG rank and bayes_rating are not model predictors. Both are retained as
comparison baselines because they are related to popularity and/or rating and
could otherwise leak the outcome being studied.

This script does not produce a final ranking or debiasing model. Residuals
are candidate "higher than expected under this baseline" signals, not broad
appeal or population-wide causal quality estimates.
"""

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

REPO_DIR = Path(__file__).resolve().parent.parent
PROCESSED_PATH = REPO_DIR / "data" / "processed" / "bgg_research_population.parquet"
RANDOM_SEED = 20260823
TAG_MIN_COUNT = 500
TOP_FRACTION = 0.01


def parse_json_list(value):
    if pd.isna(value) or not isinstance(value, str):
        return []
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [str(x) for x in parsed]
        if isinstance(parsed, dict):
            return [str(x) for x in parsed.keys()]
    except Exception:
        pass
    return []


def make_design(df, columns):
    """Build an intercept-plus-numeric design matrix from named columns."""
    return np.column_stack([np.ones(len(df))] + [df[c].to_numpy(dtype=float) for c in columns])


def fit_model(df, columns, target="avg_rating_current"):
    X = make_design(df, columns)
    y = df[target].to_numpy(dtype=float)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    pred = X @ beta
    resid = y - pred
    sse = np.sum(resid**2)
    sst = np.sum((y - y.mean())**2)
    return {
        "beta": beta,
        "pred": pred,
        "resid": resid,
        "r2": 1 - sse / sst,
        "rmse": np.sqrt(np.mean(resid**2)),
        "n": len(df),
    }


def cross_validated_predictions(df, columns, folds=5):
    """Deterministic K-fold predictions using a fixed design matrix."""
    X = make_design(df, columns)
    y = df["avg_rating_current"].to_numpy(dtype=float)
    rng = np.random.default_rng(RANDOM_SEED)
    order = rng.permutation(len(df))
    pred = np.full(len(df), np.nan)
    for test_idx in np.array_split(order, folds):
        train_mask = np.ones(len(df), dtype=bool)
        train_mask[test_idx] = False
        beta, *_ = np.linalg.lstsq(X[train_mask], y[train_mask], rcond=None)
        pred[test_idx] = X[test_idx] @ beta
    resid = y - pred
    return pred, resid, np.sqrt(np.mean(resid**2))


def summarize_group_residuals(df, residual_col, group_col, title, min_count=100, top_n=12):
    rows = []
    for group, sub in df.groupby(group_col, dropna=False, observed=True):
        if len(sub) >= min_count:
            rows.append(
                {
                    "group": group,
                    "n": len(sub),
                    "mean_resid": sub[residual_col].mean(),
                    "median_resid": sub[residual_col].median(),
                    "share_positive": (sub[residual_col] > 0).mean(),
                    "avg_mean": sub["avg_rating_current"].mean(),
                    "median_ratings": sub["users_rated"].median(),
                }
            )
    table = pd.DataFrame(rows)
    print(f"\n{title}")
    if not len(table):
        print("  No groups meet the minimum size.")
        return table
    print(
        table.sort_values("mean_resid", ascending=False).head(top_n).to_string(
            index=False,
            formatters={
                "mean_resid": lambda x: f"{x:+.3f}",
                "median_resid": lambda x: f"{x:+.3f}",
                "share_positive": lambda x: f"{x:.1%}",
                "avg_mean": lambda x: f"{x:.2f}",
                "median_ratings": lambda x: f"{x:.0f}",
            },
        )
    )
    return table


def tag_residual_table(df, list_col, residual_col, title, min_count=200):
    counts = Counter(tag for tags in df[list_col] for tag in tags)
    rows = []
    for tag, count in counts.items():
        if count < min_count:
            continue
        mask = df[list_col].map(lambda tags: tag in tags)
        sub = df[mask]
        rows.append(
            {
                "tag": tag,
                "n": len(sub),
                "mean_resid": sub[residual_col].mean(),
                "median_resid": sub[residual_col].median(),
                "share_top1pct": (sub[residual_col] >= df[residual_col].quantile(1 - TOP_FRACTION)).mean(),
                "avg_mean": sub["avg_rating_current"].mean(),
                "median_ratings": sub["users_rated"].median(),
            }
        )
    table = pd.DataFrame(rows).sort_values("mean_resid", ascending=False)
    print(f"\n{title} (tags with >= {min_count} games)")
    if not len(table):
        print("  No tags meet the minimum prevalence.")
        return table
    fmt = {
        "mean_resid": lambda x: f"{x:+.3f}",
        "median_resid": lambda x: f"{x:+.3f}",
        "share_top1pct": lambda x: f"{x:.1%}",
        "avg_mean": lambda x: f"{x:.2f}",
        "median_ratings": lambda x: f"{x:.0f}",
    }
    print(table.head(12).to_string(index=False, formatters=fmt))
    print("\nLowest-residual tags:")
    print(table.tail(8).to_string(index=False, formatters=fmt))
    return table


def add_context_features(df):
    out = df.copy()
    out["logn"] = np.log10(out["users_rated"])
    out["year_c"] = out["year"] - 2015
    out["weight_c"] = out["weight"] - out["weight"].median()
    # Log scale is a transparent response to highly skewed playtime values.
    out["log_playtime"] = np.log1p(out["playing_time"])
    out["log_playtime_c"] = out["log_playtime"] - out["log_playtime"].median()
    out["min_players_c"] = out["min_players"] - out["min_players"].median()
    # 999/open-ended values are retained but compressed by log1p.
    out["log_max_players"] = np.log1p(out["max_players"])
    out["log_max_players_c"] = out["log_max_players"] - out["log_max_players"].median()
    out["is_reimplementation_num"] = out["is_reimplementation"].astype(int)
    out["vol_bin"] = pd.cut(
        out["users_rated"],
        bins=[100, 200, 500, 1000, 2500, 5000, 10000, 25000, 200000],
        labels=["100-199", "200-499", "500-999", "1k-2.5k", "2.5k-5k", "5k-10k", "10k-25k", "25k+"],
        right=False,
    )
    out["vol_group"] = np.where(out["users_rated"] < 500, "100-499", ">=2.5k")
    out["decade"] = ((out["year"] // 10) * 10).astype(int).astype(str) + "s"
    out["category_list"] = out["categories"].map(parse_json_list)
    out["mechanic_list"] = out["mechanics"].map(parse_json_list)
    return out


def add_tag_features(df, list_col, prefix, min_count=TAG_MIN_COUNT):
    counts = Counter(tag for tags in df[list_col] for tag in tags)
    tags = sorted([tag for tag, count in counts.items() if count >= min_count])
    added = []
    for tag in tags:
        col = f"{prefix}_{tag}"
        df[col] = df[list_col].map(lambda values: float(tag in values))
        added.append(col)
    return added, tags


def add_dummy_features(df, source_col, prefix, omit_first=True):
    """Add transparent one-hot indicators, omitting the first level with an intercept."""
    dummy = pd.get_dummies(df[source_col], prefix=prefix, dtype=float)
    names = sorted(dummy.columns)
    if omit_first and names:
        names = names[1:]
    for name in names:
        df[name] = dummy[name].to_numpy()
    return names


def prepare_model_data():
    """Build the shared data frame and unchanged S0-S6 specification map."""
    df = add_context_features(pd.read_parquet(PROCESSED_PATH))
    category_cols, category_tags = add_tag_features(df, "category_list", "cat")
    mechanic_cols, mechanic_tags = add_tag_features(df, "mechanic_list", "mech")
    volume_band_cols = add_dummy_features(df, "vol_bin", "volband")
    decade_cols = add_dummy_features(df, "decade", "decade")

    # Use one common complete-case population for fair residual comparisons.
    common_cols = [
        "avg_rating_current",
        "logn",
        "year_c",
        "weight_c",
        "log_playtime_c",
        "min_players_c",
        "log_max_players_c",
        "is_reimplementation_num",
    ] + category_cols + mechanic_cols + volume_band_cols + decade_cols
    common = df.dropna(subset=common_cols).reset_index(drop=True).copy()

    specs = {
        "S0_volume": ["logn"],
        "S0b_volume_bands": volume_band_cols,
        "S1_core": ["logn", "year_c", "weight_c"],
        "S1b_bands_decades": volume_band_cols + decade_cols + ["weight_c"],
        "S2_structure": [
            "logn",
            "year_c",
            "weight_c",
            "log_playtime_c",
            "min_players_c",
            "log_max_players_c",
            "is_reimplementation_num",
        ],
        "S3_categories": [
            "logn",
            "year_c",
            "weight_c",
            "log_playtime_c",
            "min_players_c",
            "log_max_players_c",
            "is_reimplementation_num",
        ] + category_cols,
        "S4_categories_mechanics": [
            "logn",
            "year_c",
            "weight_c",
            "log_playtime_c",
            "min_players_c",
            "log_max_players_c",
            "is_reimplementation_num",
        ] + category_cols + mechanic_cols,
        "S5_binned_categories": volume_band_cols
        + decade_cols
        + [
            "weight_c",
            "log_playtime_c",
            "min_players_c",
            "log_max_players_c",
            "is_reimplementation_num",
        ]
        + category_cols,
        "S6_binned_categories_mechanics": volume_band_cols
        + decade_cols
        + [
            "weight_c",
            "log_playtime_c",
            "min_players_c",
            "log_max_players_c",
            "is_reimplementation_num",
        ]
        + category_cols
        + mechanic_cols,
    }
    return df, common, specs, category_tags, mechanic_tags


def main():
    print(f"Loading clean research population from: {PROCESSED_PATH}")
    if not PROCESSED_PATH.exists():
        print(f"Error: processed dataset not found at {PROCESSED_PATH}")
        sys.exit(1)
    df, common, specs, category_tags, mechanic_tags = prepare_model_data()
    print(f"Loaded {len(df):,} games.")
    print(f"Frequent category tags (>= {TAG_MIN_COUNT} games): {len(category_tags)}")
    print(f"Frequent mechanic tags (>= {TAG_MIN_COUNT} games): {len(mechanic_tags)}")
    print(f"Volume-band indicators: {sum(c.startswith('volband_') for c in common.columns)}; release-decade indicators: {sum(c.startswith('decade_') for c in common.columns)}")
    print(f"Common complete-case population for model comparisons: {len(common):,} games.")

    print("\n" + "=" * 78)
    print("1. NESTED DESCRIPTIVE EXPECTED-RATING SPECIFICATIONS")
    print("=" * 78)
    results = {}
    for name, columns in specs.items():
        fit = fit_model(common, columns)
        cv_pred, cv_resid, cv_rmse = cross_validated_predictions(common, columns)
        common[f"pred_{name}"] = fit["pred"]
        common[f"resid_{name}"] = fit["resid"]
        common[f"cv_pred_{name}"] = cv_pred
        common[f"cv_resid_{name}"] = cv_resid
        results[name] = fit
        volume_beta = f"{fit['beta'][columns.index('logn') + 1]:+.4f}" if "logn" in columns else "n/a"
        print(
            f"{name:28s} features={len(columns):3d}  n={fit['n']:,}  "
            f"R2={fit['r2']:.4f}  RMSE={fit['rmse']:.4f}  CV_RMSE={cv_rmse:.4f}  "
            f"log10(n) beta={volume_beta}"
        )

    print("\nS3 category-baseline coefficient summary (rating points per unit)")
    s3 = results["S3_categories"]
    for col, beta in zip(["intercept"] + specs["S3_categories"], s3["beta"]):
        if col in {"intercept", "logn", "year_c", "weight_c", "log_playtime_c", "min_players_c", "log_max_players_c", "is_reimplementation_num"}:
            print(f"  {col:28s} {beta:+.4f}")

    # ------------------------------------------------------------------
    # 2. Stability of residuals across specifications
    # ------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("2. RESIDUAL STABILITY ACROSS SPECIFICATIONS")
    print("=" * 78)
    names = list(specs)
    print("Pairwise Pearson correlations of in-sample residuals:")
    corr = common[[f"resid_{name}" for name in names]].corr()
    print(corr.round(3).to_string())

    top_k = max(1, int(TOP_FRACTION * len(common)))
    print(f"\nOverlap among top positive residuals (top {TOP_FRACTION:.0%}, k={top_k})")
    for i, left in enumerate(names):
        parts = []
        left_set = set(common.nlargest(top_k, f"resid_{left}").index)
        for right in names[i + 1 :]:
            right_set = set(common.nlargest(top_k, f"resid_{right}").index)
            union = len(left_set | right_set)
            parts.append(f"{right}={len(left_set & right_set)/union:.1%}")
        if parts:
            print(f"  {left:28s} " + ", ".join(parts))

    print("\nS3 in-sample versus cross-validated residual correlation")
    print(common[["resid_S3_categories", "cv_resid_S3_categories"]].corr().iloc[0, 1])

    # ------------------------------------------------------------------
    # 3. Comparison with raw average and BGG Bayesian rating
    # ------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("3. COMPARISON WITH RAW AVERAGE AND BGG BAYESIAN RATING")
    print("=" * 78)
    compare_cols = ["avg_rating_current", "bayes_rating", "users_rated", "logn", "resid_S3_categories", "cv_resid_S3_categories"]
    print(common[compare_cols].corr(method="pearson").round(3).to_string())
    common["raw_minus_bayes"] = common["avg_rating_current"] - common["bayes_rating"]
    for label, col in [("S3 in-sample", "resid_S3_categories"), ("S3 cross-validated", "cv_resid_S3_categories")]:
        print(
            f"{label}: mean={common[col].mean():+.4f}, SD={common[col].std():.4f}, "
            f"P95={common[col].quantile(.95):+.3f}, P99={common[col].quantile(.99):+.3f}, "
            f"share positive={(common[col] > 0).mean():.1%}"
        )
    print("\nS3 expected-rating comparison for volume bands")
    by_vol = common.groupby("vol_bin", observed=True).agg(
        games=("avg_rating_current", "size"),
        avg_mean=("avg_rating_current", "mean"),
        bayes_mean=("bayes_rating", "mean"),
        expected_mean=("pred_S3_categories", "mean"),
        residual_mean=("resid_S3_categories", "mean"),
        residual_sd=("resid_S3_categories", "std"),
    )
    print(by_vol.to_string(float_format=lambda x: f"{x:.3f}"))

    # ------------------------------------------------------------------
    # 4. Which types generate positive residuals?
    # ------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("4. TYPES ASSOCIATED WITH LARGE POSITIVE S3 RESIDUALS")
    print("=" * 78)
    common["resid_decile"] = pd.qcut(common["resid_S3_categories"], 10, labels=False, duplicates="drop") + 1
    summarize_group_residuals(common, "resid_S3_categories", "vol_bin", "Residuals by rating-volume band", min_count=30)
    summarize_group_residuals(common, "resid_S3_categories", "decade", "Residuals by release decade", min_count=100)
    summarize_group_residuals(common, "resid_S3_categories", "resid_decile", "Residual decile sanity check", min_count=100)
    summarize_group_residuals(common, "resid_S3_categories", "is_reimplementation", "Residuals by reimplementation status", min_count=30)
    tag_residual_table(common, "category_list", "resid_S3_categories", "Category residual means")
    tag_residual_table(common, "mechanic_list", "resid_S3_categories", "Mechanic residual means")

    print("\nS3 versus S5 residual means for key grouping variables")
    for group_col in ["vol_bin", "decade", "is_reimplementation"]:
        table = common.groupby(group_col, dropna=False, observed=True).agg(
            n=("avg_rating_current", "size"),
            s3_mean=("resid_S3_categories", "mean"),
            s5_mean=("resid_S5_binned_categories", "mean"),
            s3_top1=("resid_S3_categories", lambda s: (s >= common["resid_S3_categories"].quantile(1 - TOP_FRACTION)).mean()),
            s5_top1=("resid_S5_binned_categories", lambda s: (s >= common["resid_S5_binned_categories"].quantile(1 - TOP_FRACTION)).mean()),
        )
        print(f"\n  {group_col}")
        print(table.to_string(float_format=lambda x: f"{x:+.3f}"))
    tag_residual_table(common, "category_list", "resid_S5_binned_categories", "Category residual means under binned-volume/decade sensitivity")

    top = common.nlargest(20, "resid_S3_categories")
    print("\nIllustrative top 20 positive S3 residuals (candidate diagnostics, not a ranking)")
    cols = ["title", "year", "users_rated", "avg_rating_current", "bayes_rating", "pred_S3_categories", "resid_S3_categories", "weight", "is_reimplementation"]
    print(top[cols].to_string(index=False, float_format=lambda x: f"{x:.3f}"))

    # ------------------------------------------------------------------
    # 5. Explicit interpretation guardrails
    # ------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("5. INTERPRETATION GUARDRAILS")
    print("=" * 78)
    print(
        "A positive residual means only that observed average rating exceeds the fitted "
        "conditional mean under the selected descriptive specification. It can reflect "
        "quality, omitted audience selection, edition/marketing effects, tag error, "
        "or noise. It is not evidence of broad appeal and is not a final hidden-gem score."
    )


if __name__ == "__main__":
    main()

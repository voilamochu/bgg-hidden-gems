"""
Script 06: RQ2 residual robustness and specification sensitivity
----------------------------------------------------------------
Reuses the existing S0-S6 expected-rating variants from
05_rq2_expected_rating_baseline.py. It does not fit a new model.

For the top 1% and top 5% positive residuals, this script measures:
  - how often each game is selected across specifications;
  - consensus versus specification-sensitive candidate sets;
  - residual/rank dispersion across specifications; and
  - characteristics and category/mechanic enrichment of stable versus
    unstable candidate groups.

The output is a robustness audit, not a ranking. A candidate selected by
many specifications is more robust as a conditional anomaly, but is still
not thereby a broad-appeal or hidden-gem candidate.
"""

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_DIR = Path(__file__).resolve().parent.parent
BASELINE_PATH = REPO_DIR / "scripts" / "05_rq2_expected_rating_baseline.py"


def load_baseline_module():
    spec = importlib.util.spec_from_file_location("rq2_expected_rating_baseline", BASELINE_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load baseline module from {BASELINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def selection_sets(df, spec_names, fraction):
    k = max(1, int(fraction * len(df)))
    selected = {}
    for name in spec_names:
        selected[name] = set(df.nlargest(k, f"resid_{name}").index)
    counts = pd.Series(0, index=df.index, dtype=int)
    for members in selected.values():
        counts.loc[list(members)] += 1
    return selected, counts, k


def jaccard_summary(selected, title):
    names = list(selected)
    values = []
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            union = len(selected[left] | selected[right])
            values.append(len(selected[left] & selected[right]) / union)
    print(f"{title}: mean pairwise Jaccard={np.mean(values):.1%}, min={np.min(values):.1%}, max={np.max(values):.1%}")


def candidate_characteristics(df, mask, label, residual_cols):
    sub = df[mask].copy()
    print(f"\n{label}: n={len(sub)}")
    if not len(sub):
        return
    table = pd.Series(
        {
            "median_users_rated": sub["users_rated"].median(),
            "mean_avg_rating": sub["avg_rating_current"].mean(),
            "mean_bayes_rating": sub["bayes_rating"].mean(),
            "mean_year": sub["year"].mean(),
            "median_weight": sub["weight"].median(),
            "median_playtime": sub["playing_time"].median(),
            "median_min_players": sub["min_players"].median(),
            "median_max_players": sub["max_players"].median(),
            "reimplementation_share": sub["is_reimplementation"].mean(),
            "median_rank": sub["rank_current"].median(),
            "mean_residual": sub[residual_cols].mean(axis=1).mean(),
            "mean_residual_sd": sub[residual_cols].std(axis=1).mean(),
            "mean_residual_range": (sub[residual_cols].max(axis=1) - sub[residual_cols].min(axis=1)).mean(),
        }
    )
    print(table.to_string(float_format=lambda x: f"{x:.3f}"))


def tag_enrichment(df, stable_mask, unstable_mask, list_col, title, min_pool=30):
    rows = []
    tags = sorted({tag for values in df[list_col] for tag in values})
    for tag in tags:
        stable = df[stable_mask & df[list_col].map(lambda values: tag in values)]
        unstable = df[unstable_mask & df[list_col].map(lambda values: tag in values)]
        if len(stable) < min_pool and len(unstable) < min_pool:
            continue
        stable_share = len(stable) / max(int(stable_mask.sum()), 1)
        unstable_share = len(unstable) / max(int(unstable_mask.sum()), 1)
        rows.append(
            {
                "tag": tag,
                "stable_n": len(stable),
                "unstable_n": len(unstable),
                "stable_share": stable_share,
                "unstable_share": unstable_share,
                "difference": stable_share - unstable_share,
            }
        )
    table = pd.DataFrame(rows)
    print(f"\n{title}")
    if not len(table):
        print("  No tags meet the minimum pool size.")
        return
    fmt = {
        "stable_share": lambda x: f"{x:.1%}",
        "unstable_share": lambda x: f"{x:.1%}",
        "difference": lambda x: f"{x:+.1%}",
    }
    print("Most enriched in stable group:")
    print(table.sort_values("difference", ascending=False).head(10).to_string(index=False, formatters=fmt))
    print("Most enriched in unstable group:")
    print(table.sort_values("difference", ascending=True).head(10).to_string(index=False, formatters=fmt))


def print_consensus_distribution(counts, n_specs, fraction):
    dist = counts.value_counts().sort_index()
    print(f"\nConsensus count distribution for top {fraction:.0%} (out of {n_specs} specifications)")
    for count, n_games in dist.items():
        print(f"  selected in {count:2d}/{n_specs}: {n_games:4d} games")


def main():
    if not BASELINE_PATH.exists():
        print(f"Baseline script not found: {BASELINE_PATH}")
        sys.exit(1)
    baseline = load_baseline_module()
    df, common, specs, _, _ = baseline.prepare_model_data()
    spec_names = list(specs)
    adjusted_names = [name for name in spec_names if name not in {"S0_volume", "S0b_volume_bands"}]

    print(f"Loaded {len(common):,} common complete-case games and reused {len(spec_names)} existing specifications.")
    print(f"Adjusted specification family: {', '.join(adjusted_names)}")

    for name, columns in specs.items():
        fit = baseline.fit_model(common, columns)
        common[f"resid_{name}"] = fit["resid"]

    print("\n" + "=" * 78)
    print("1. RESIDUAL CONSENSUS AT TOP 1% AND TOP 5%")
    print("=" * 78)
    all_results = {}
    adjusted_results = {}
    for fraction in (0.01, 0.05):
        all_selected, all_counts, k = selection_sets(common, spec_names, fraction)
        adjusted_selected, adjusted_counts, _ = selection_sets(common, adjusted_names, fraction)
        all_results[fraction] = (all_selected, all_counts, k)
        adjusted_results[fraction] = (adjusted_selected, adjusted_counts, k)
        print(f"\nTop {fraction:.0%}: k={k} games per specification")
        jaccard_summary(all_selected, "  All variants")
        jaccard_summary(adjusted_selected, "  Adjusted variants")
        print_consensus_distribution(all_counts, len(spec_names), fraction)
        print_consensus_distribution(adjusted_counts, len(adjusted_names), fraction)
        print(f"  All-variant intersection: {sum(all_counts == len(spec_names))}")
        print(f"  Adjusted-family intersection: {sum(adjusted_counts == len(adjusted_names))}")
        print(f"  Adjusted stable (>=5/{len(adjusted_names)}): {sum(adjusted_counts >= 5)}")
        print(f"  Adjusted unstable (<=1/{len(adjusted_names)}): {sum(adjusted_counts <= 1)}")

    # ------------------------------------------------------------------
    # 2. Stable versus specification-sensitive candidate groups
    # ------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("2. STABLE VERSUS SPECIFICATION-SENSITIVE CANDIDATES")
    print("=" * 78)
    residual_cols = [f"resid_{name}" for name in adjusted_names]
    common["adjusted_mean_resid"] = common[residual_cols].mean(axis=1)
    common["adjusted_resid_sd"] = common[residual_cols].std(axis=1)
    common["adjusted_resid_range"] = common[residual_cols].max(axis=1) - common[residual_cols].min(axis=1)

    for fraction in (0.01, 0.05):
        _, counts, k = adjusted_results[fraction]
        common[f"top{int(fraction * 100)}_count"] = counts
        selected_any = counts > 0
        stable = selected_any & (counts >= 5)
        unstable = selected_any & (counts <= 1)
        label = f"top {fraction:.0%} adjusted-family union"
        candidate_characteristics(common, selected_any, label, residual_cols)
        candidate_characteristics(common, stable, f"  Stable subset (>=5/{len(adjusted_names)})", residual_cols)
        candidate_characteristics(common, unstable, f"  Sensitive subset (<=1/{len(adjusted_names)})", residual_cols)
        tag_enrichment(common, stable, unstable, "category_list", f"{label}: category enrichment")
        tag_enrichment(common, stable, unstable, "mechanic_list", f"{label}: mechanic enrichment")

        union = common[selected_any].copy()
        union["consensus_count"] = counts[selected_any]
        union = union.sort_values(["consensus_count", "adjusted_mean_resid"], ascending=[False, False])
        print(f"\n{label}: most consensus-stable examples (diagnostic, not a ranking)")
        print(
            union[["title", "consensus_count", "users_rated", "avg_rating_current", "bayes_rating", "adjusted_mean_resid", "adjusted_resid_sd", "adjusted_resid_range", "year", "weight", "is_reimplementation"]]
            .head(15)
            .to_string(index=False, float_format=lambda x: f"{x:.3f}")
        )
        print(f"\n{label}: most specification-sensitive examples among the union")
        sensitive = union.sort_values(["adjusted_resid_range", "adjusted_resid_sd"], ascending=False)
        print(
            sensitive[["title", "consensus_count", "users_rated", "avg_rating_current", "bayes_rating", "adjusted_mean_resid", "adjusted_resid_sd", "adjusted_resid_range", "year", "weight", "is_reimplementation"]]
            .head(15)
            .to_string(index=False, float_format=lambda x: f"{x:.3f}")
        )

    # ------------------------------------------------------------------
    # 3. What is driving sensitivity?
    # ------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("3. CHARACTERISTICS ASSOCIATED WITH RESIDUAL DISPERSION")
    print("=" * 78)
    top5_mask = common["top5_count"] > 0
    for group_col in ["vol_bin", "decade", "is_reimplementation"]:
        table = common[top5_mask].groupby(group_col, dropna=False, observed=True).agg(
            n=("adjusted_resid_sd", "size"),
            mean_sd=("adjusted_resid_sd", "mean"),
            median_sd=("adjusted_resid_sd", "median"),
            mean_range=("adjusted_resid_range", "mean"),
            stable_share=("top5_count", lambda s: (s >= 5).mean()),
        )
        print(f"\n{group_col} among top-5%-union games")
        print(table.to_string(float_format=lambda x: f"{x:.3f}"))

    print("\nCorrelation of residual dispersion with numeric characteristics (top-5%-union)")
    numeric = common.loc[top5_mask, ["adjusted_resid_sd", "adjusted_resid_range", "users_rated", "year", "weight", "playing_time", "min_players", "max_players", "avg_rating_current", "bayes_rating"]]
    print(numeric.corr()[["adjusted_resid_sd", "adjusted_resid_range"]].round(3).to_string())


if __name__ == "__main__":
    main()

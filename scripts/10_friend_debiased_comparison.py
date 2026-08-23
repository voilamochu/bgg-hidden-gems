"""
Script 10: Descriptive comparison of the friend-provided debiased rating
-------------------------------------------------------------------------
Compares the observed friend output with the current game-level BGG research
population and the existing RQ2 baselines. It reuses the unchanged RQ2 model
specifications from script 05 and the stable-candidate convention from script
06.

This is an output audit, not a validation of the friend's user-level method.
It does not reconstruct, correct, or redesign the debiasing procedure and
does not create a new ranking.
"""

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

REPO_DIR = Path(__file__).resolve().parent.parent
PROCESSED_PATH = REPO_DIR / "data" / "processed" / "bgg_research_population.parquet"
FRIEND_PATH = REPO_DIR / "data" / "raw" / "complete_2025_bgg_debiased_ranks.csv"
BASELINE_PATH = REPO_DIR / "scripts" / "05_rq2_expected_rating_baseline.py"


def load_baseline_module():
    spec = importlib.util.spec_from_file_location("rq2_expected_rating_baseline", BASELINE_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load baseline module from {BASELINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def pair_summary(df, left, right):
    paired = df[[left, right]].dropna()
    if not len(paired):
        return None
    delta = paired[left] - paired[right]
    return {
        "left": left,
        "right": right,
        "n": len(paired),
        "pearson": paired[left].corr(paired[right]),
        "spearman": paired[left].corr(paired[right], method="spearman"),
        "median_delta": delta.median(),
        "p10_delta": delta.quantile(.10),
        "p90_delta": delta.quantile(.90),
        "share_left_higher": (delta > 0).mean(),
    }


def correction_summary(df, delta_col, label):
    delta = df[delta_col].dropna()
    print(f"\n{label}: n={len(delta):,}")
    print(
        pd.Series(
            {
                "mean": delta.mean(),
                "median": delta.median(),
                "sd": delta.std(),
                "p01": delta.quantile(.01),
                "p10": delta.quantile(.10),
                "p90": delta.quantile(.90),
                "p99": delta.quantile(.99),
                "share_positive": (delta > 0).mean(),
                "share_negative": (delta < 0).mean(),
            }
        ).to_string(float_format=lambda x: f"{x:.4f}")
    )


def print_group_table(df, group_col, label):
    table = df.groupby(group_col, dropna=False, observed=True).agg(
        n=("delta_raw", "size"),
        mean_delta_raw=("delta_raw", "mean"),
        median_delta_raw=("delta_raw", "median"),
        share_raw_positive=("delta_raw", lambda s: (s > 0).mean()),
        mean_delta_bayes=("delta_bayes", "mean"),
        mean_debiased=("debiased_rating", "mean"),
        mean_avg=("avg_rating_current", "mean"),
    )
    print(f"\nCorrection by {label}")
    print(table.to_string(float_format=lambda x: f"{x:.4f}"))
    return table


def print_tag_tables(df, list_col, label, minimum=100):
    rows = []
    tags = sorted({tag for values in df[list_col] for tag in values})
    for tag in tags:
        mask = df[list_col].map(lambda values: tag in values)
        sub = df[mask]
        if len(sub) < minimum:
            continue
        rows.append(
            {
                "tag": tag,
                "n": len(sub),
                "mean_delta_raw": sub["delta_raw"].mean(),
                "median_delta_raw": sub["delta_raw"].median(),
                "mean_delta_bayes": sub["delta_bayes"].mean(),
                "mean_debiased": sub["debiased_rating"].mean(),
                "mean_avg": sub["avg_rating_current"].mean(),
            }
        )
    table = pd.DataFrame(rows)
    print(f"\n{label} correction (tags with >= {minimum} matched games)")
    if not len(table):
        print("  No tags meet the minimum count.")
        return table
    print("Most positive raw-average corrections:")
    print(table.sort_values("mean_delta_raw", ascending=False).head(12).to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print("Most negative raw-average corrections:")
    print(table.sort_values("mean_delta_raw", ascending=True).head(12).to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    return table


def add_rq2_residuals(common, specs, baseline):
    adjusted_names = [name for name in specs if name not in {"S0_volume", "S0b_volume_bands"}]
    for name, columns in specs.items():
        common[f"resid_{name}"] = baseline.fit_model(common, columns)["resid"]
    residual_cols = [f"resid_{name}" for name in adjusted_names]
    common["adjusted_mean_resid"] = common[residual_cols].mean(axis=1)
    stable_masks = {}
    for fraction in (.01, .05):
        k = max(1, int(fraction * len(common)))
        counts = pd.Series(0, index=common.index, dtype=int)
        for name in adjusted_names:
            selected = set(common.nlargest(k, f"resid_{name}").index)
            counts.loc[list(selected)] += 1
        common[f"stable_top{int(fraction * 100)}"] = counts >= 5
        common[f"consensus_top{int(fraction * 100)}"] = counts
        stable_masks[fraction] = common[f"stable_top{int(fraction * 100)}"]
    return common, adjusted_names, stable_masks


def compare_top_sets(df, fraction, stable_col):
    k = max(1, int(fraction * len(df)))
    friend_set = set(df.nlargest(k, "debiased_rating").game_id)
    measures = {
        "avg_rating_current": set(df.nlargest(k, "avg_rating_current").game_id),
        "bayes_rating": set(df.nlargest(k, "bayes_rating").game_id),
        "resid_S3_categories": set(df.nlargest(k, "resid_S3_categories").game_id),
        "all_stable_RQ2": set(df[df[stable_col]].game_id),
    }
    print(f"\nTop {fraction:.0%} comparisons among matched games (k={k})")
    for label, members in measures.items():
        intersection = len(friend_set & members)
        union = len(friend_set | members)
        print(
            f"  friend vs {label:25s}: intersection={intersection:4d} "
            f"({intersection / k:.1%} of friend set), Jaccard={intersection / union:.1%}"
        )
    stable_members = set(df[df[stable_col]].game_id)
    print(
        f"  friend top set contains {len(friend_set & stable_members):,} stable-RQ2 games "
        f"({len(friend_set & stable_members) / k:.1%}); "
        f"stable set contains {len(friend_set & stable_members):,} of {len(stable_members):,} "
        f"stable games ({len(friend_set & stable_members) / max(len(stable_members), 1):.1%})."
    )

    display_cols = [
        "title_current",
        "game_id",
        "debiased_rating",
        "avg_rating_current",
        "bayes_rating",
        "resid_S3_categories",
        "adjusted_mean_resid",
        "users_rated",
        stable_col,
    ]
    print("  Highest friend scores (diagnostic, not a new ranking):")
    print(df.nlargest(15, "debiased_rating")[display_cols].to_string(index=False, float_format=lambda x: f"{x:.4f}"))


def print_movers(df, delta_col, label):
    cols = [
        "title_current",
        "game_id",
        "year_current",
        "users_rated",
        "avg_rating_current",
        "bayes_rating",
        "debiased_rating",
        "delta_raw",
        "delta_bayes",
        "resid_S3_categories",
    ]
    print(f"\nLargest positive {label} (diagnostic, not a ranking)")
    print(df.nlargest(15, delta_col)[cols].to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print(f"\nLargest negative {label} (diagnostic, not a ranking)")
    print(df.nsmallest(15, delta_col)[cols].to_string(index=False, float_format=lambda x: f"{x:.4f}"))


def main():
    if not PROCESSED_PATH.exists() or not FRIEND_PATH.exists():
        raise FileNotFoundError("Processed research population or friend CSV is missing")

    baseline = load_baseline_module()
    research = pd.read_parquet(PROCESSED_PATH)
    friend = pd.read_csv(FRIEND_PATH)
    if not friend["game_id"].is_unique:
        raise ValueError("Friend game_id is not unique")

    _, common, specs, _, _ = baseline.prepare_model_data()
    common, adjusted_names, stable_masks = add_rq2_residuals(common, specs, baseline)
    friend_renamed = friend.rename(columns={column: f"friend_{column}" for column in friend.columns if column != "game_id"})
    population_overlap = research.merge(friend_renamed, on="game_id", how="inner", suffixes=("_current", "_friend_duplicate"))
    common_subset = common[["game_id", "resid_S3_categories", "adjusted_mean_resid", "stable_top1", "stable_top5", "consensus_top1", "consensus_top5"]]
    comparison = population_overlap.merge(common_subset, on="game_id", how="left")
    print(f"Friend rows: {len(friend):,}; research rows: {len(research):,}; direct population overlap: {len(population_overlap):,}")
    print(
        f"Research coverage={len(population_overlap) / len(research):.1%}; friend-file coverage={len(population_overlap) / len(friend):.1%}; "
        f"friend-only={len(friend) - len(population_overlap):,}; research-only={len(research) - len(population_overlap):,}."
    )
    merged = comparison
    merged["title_current"] = merged["title"]
    merged["year_current"] = merged["year"]
    merged["debiased_rating"] = merged["friend_debiased_rating"]
    merged["delta_raw"] = merged["debiased_rating"] - merged["avg_rating_current"]
    merged["delta_bayes"] = merged["debiased_rating"] - merged["bayes_rating"]
    merged["log_users"] = np.log10(merged["users_rated"])
    merged["category_list"] = merged["categories"].map(parse_json_list)
    merged["mechanic_list"] = merged["mechanics"].map(parse_json_list)
    merged["volume_band"] = pd.cut(
        merged["users_rated"],
        bins=[100, 200, 500, 1000, 2500, 5000, 10000, 25000, np.inf],
        labels=["100-199", "200-499", "500-999", "1k-2.5k", "2.5k-5k", "5k-10k", "10k-25k", "25k+"],
        right=False,
    )
    merged["decade"] = ((merged["year"] // 10) * 10).astype("Int64").astype(str) + "s"
    merged["weight_band"] = pd.cut(
        merged["weight"],
        bins=[0, 1.5, 2.0, 2.5, 3.0, 3.5, np.inf],
        labels=["<=1.5", "1.5-2.0", "2.0-2.5", "2.5-3.0", "3.0-3.5", "3.5+"],
        include_lowest=True,
    )
    merged["playtime_band"] = pd.cut(
        merged["playing_time"],
        bins=[-np.inf, 30, 60, 120, 240, np.inf],
        labels=["<=30", "31-60", "61-120", "121-240", ">240"],
    )
    rq2_overlap = merged.dropna(subset=["resid_S3_categories", "adjusted_mean_resid"]).copy()
    print(
        f"RQ2 complete-case overlap for residual comparisons: {len(rq2_overlap):,}; "
        f"overlap records excluded from RQ2 residual comparisons: {len(population_overlap) - len(rq2_overlap):,}."
    )

    coverage = pd.DataFrame(
        {
            "field": ["friend_debiased_rating", "friend_debiased_rank", "friend_avg_rating", "friend_geek_rating", "friend_voters", "friend_bgg_rank", "friend_weight", "friend_kickstarted"],
            "friend_non_null": [friend[column].notna().sum() for column in ["debiased_rating", "debiased_rank", "avg_rating", "geek_rating", "voters", "bgg_rank", "weight", "kickstarted"]],
            "population_overlap_non_null": [population_overlap[column].notna().sum() for column in ["friend_debiased_rating", "friend_debiased_rank", "friend_avg_rating", "friend_geek_rating", "friend_voters", "friend_bgg_rank", "friend_weight", "friend_kickstarted"]],
        }
    )
    print("\nFriend-field coverage")
    print(coverage.to_string(index=False))

    print("\nCurrent versus friend-file comparison fields")
    pairs = [
        ("friend_voters", "users_rated"),
        ("friend_avg_rating", "avg_rating_current"),
        ("friend_geek_rating", "bayes_rating"),
        ("friend_bgg_rank", "rank_current"),
        ("friend_year", "year"),
        ("friend_weight", "weight"),
    ]
    pair_table = pd.DataFrame([pair_summary(population_overlap, left, right) for left, right in pairs])
    print(pair_table.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    print("\nDebiased rating correlations with existing measures")
    measure_cols = ["debiased_rating", "avg_rating_current", "bayes_rating", "resid_S3_categories", "adjusted_mean_resid", "log_users"]
    print(rq2_overlap[measure_cols].corr(method="pearson").round(4).to_string())
    print("\nSpearman correlations")
    print(rq2_overlap[measure_cols].corr(method="spearman").round(4).to_string())
    correction_summary(merged, "delta_raw", "Debiased rating minus current raw average")
    correction_summary(merged, "delta_bayes", "Debiased rating minus current Bayes rating")

    print("\nCorrection correlations with characteristics")
    characteristic_cols = ["delta_raw", "delta_bayes", "log_users", "year", "weight", "playing_time", "min_players", "max_players", "is_reimplementation"]
    print(merged[characteristic_cols].corr(method="spearman")[['delta_raw', 'delta_bayes']].round(4).to_string())
    print_group_table(merged, "volume_band", "current rating-volume band")
    print_group_table(merged, "decade", "release decade")
    print_group_table(merged, "weight_band", "complexity/weight band")
    print_group_table(merged, "playtime_band", "playtime band")
    print_group_table(merged, "is_reimplementation", "current reimplementation status")
    print_tag_tables(merged, "category_list", "Category")
    print_tag_tables(merged, "mechanic_list", "Mechanic")

    print_movers(merged, "delta_raw", "correction versus current raw average")
    print_movers(merged, "delta_bayes", "correction versus current Bayes rating")

    compare_top_sets(rq2_overlap, .01, "stable_top1")
    compare_top_sets(rq2_overlap, .05, "stable_top5")

    print("\nInterpretation guardrail")
    print(
        "All comparisons describe the supplied game-level output. They do not establish whether "
        "the friend's underlying method corrects measurement noise, selection into the BGG rater pool, "
        "or both; that requires the user-level inputs and method provenance."
    )


if __name__ == "__main__":
    main()

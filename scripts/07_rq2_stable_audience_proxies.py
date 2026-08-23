"""
Script 07: Descriptive audience proxies for stable RQ2 residuals
----------------------------------------------------------------
Reuses the existing RQ2 model variants and stable-candidate definition from
the residual robustness work. It compares stable top-1% and top-5% residual
sets with the rest of the research population using separate, descriptive
audience proxies:

  - number of BGG category and mechanic tags;
  - category/mechanic prevalence;
  - transparent specialist and broad-audience pattern combinations;
  - complexity, playtime, and player count.

This script does not fit a model, create an audience-breadth score, or rank
games. Tag counts and combinations are metadata/audience proxies only; they
do not measure actual reach, user diversity, or appeal outside an existing
rater niche.
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


def tag_present(values, tag):
    return tag in values


def any_tag(values, tags):
    return any(tag in values for tag in tags)


def describe_sample(df, mask, label):
    sub = df[mask]
    print(f"\n{label}: n={len(sub):,}")
    if not len(sub):
        return
    rows = {
        "avg_rating_mean": sub["avg_rating_current"].mean(),
        "bayes_rating_mean": sub["bayes_rating"].mean(),
        "users_rated_median": sub["users_rated"].median(),
        "year_median": sub["year"].median(),
        "weight_median": sub["weight"].median(),
        "playtime_median": sub["playing_time"].replace(0, np.nan).median(),
        "min_players_median": sub["min_players"].replace(0, np.nan).median(),
        "max_players_median": sub["max_players"].replace(0, np.nan).median(),
        "category_tags_mean": sub["category_count"].mean(),
        "category_tags_median": sub["category_count"].median(),
        "mechanic_tags_mean": sub["mechanic_count"].mean(),
        "mechanic_tags_median": sub["mechanic_count"].median(),
        "reimplementation_share": sub["is_reimplementation"].mean(),
    }
    print(pd.Series(rows).to_string(float_format=lambda x: f"{x:.3f}"))
    print("  category tag quantiles:", sub["category_count"].quantile([.1, .25, .5, .75, .9]).round(2).to_dict())
    print("  mechanic tag quantiles:", sub["mechanic_count"].quantile([.1, .25, .5, .75, .9]).round(2).to_dict())


def prevalence_table(df, stable_mask, rest_mask, list_col, title, min_stable_n):
    tags = sorted({tag for values in df[list_col] for tag in values})
    stable_n_total = int(stable_mask.sum())
    rest_n_total = int(rest_mask.sum())
    rows = []
    for tag in tags:
        stable_n = int((stable_mask & df[list_col].map(lambda values: tag_present(values, tag))).sum())
        rest_n = int((rest_mask & df[list_col].map(lambda values: tag_present(values, tag))).sum())
        if stable_n < min_stable_n:
            continue
        stable_share = stable_n / stable_n_total
        rest_share = rest_n / rest_n_total
        rows.append(
            {
                "tag": tag,
                "stable_n": stable_n,
                "rest_n": rest_n,
                "stable_share": stable_share,
                "rest_share": rest_share,
                "difference": stable_share - rest_share,
                "ratio": stable_share / rest_share if rest_share else np.inf,
            }
        )
    table = pd.DataFrame(rows)
    print(f"\n{title} (minimum stable count={min_stable_n})")
    if not len(table):
        print("  No tags meet the minimum count.")
        return table
    fmt = {
        "stable_share": lambda x: f"{x:.1%}",
        "rest_share": lambda x: f"{x:.1%}",
        "difference": lambda x: f"{x:+.1%}",
        "ratio": lambda x: f"{x:.2f}",
    }
    print("Most prevalent/enriched among stable candidates:")
    print(table.sort_values("difference", ascending=False).head(15).to_string(index=False, formatters=fmt))
    print("Most enriched among the rest:")
    print(table.sort_values("difference", ascending=True).head(15).to_string(index=False, formatters=fmt))
    return table


def profile_table(df, profiles, stable_mask, rest_mask, label):
    rows = []
    for profile_name, mask in profiles.items():
        stable_n = int((stable_mask & mask).sum())
        rest_n = int((rest_mask & mask).sum())
        stable_share = stable_n / max(int(stable_mask.sum()), 1)
        rest_share = rest_n / max(int(rest_mask.sum()), 1)
        rows.append(
            {
                "profile": profile_name,
                "stable_n": stable_n,
                "rest_n": rest_n,
                "stable_share": stable_share,
                "rest_share": rest_share,
                "difference": stable_share - rest_share,
                "ratio": stable_share / rest_share if rest_share else np.inf,
            }
        )
    table = pd.DataFrame(rows).sort_values("difference", ascending=False)
    print(f"\n{label}")
    fmt = {
        "stable_share": lambda x: f"{x:.1%}",
        "rest_share": lambda x: f"{x:.1%}",
        "difference": lambda x: f"{x:+.1%}",
        "ratio": lambda x: f"{x:.2f}",
    }
    print(table.to_string(index=False, formatters=fmt))
    return table


def main():
    if not BASELINE_PATH.exists():
        print(f"Baseline script not found: {BASELINE_PATH}")
        sys.exit(1)
    baseline = load_baseline_module()
    df, common, specs, _, _ = baseline.prepare_model_data()
    adjusted_names = [
        name
        for name in specs
        if name not in {"S0_volume", "S0b_volume_bands"}
    ]
    for name, columns in specs.items():
        fit = baseline.fit_model(common, columns)
        common[f"resid_{name}"] = fit["resid"]

    # Stable means selected in >=5 of the 7 adjusted specifications.
    top_sets = {}
    for fraction in (0.01, 0.05):
        k = max(1, int(fraction * len(common)))
        counts = pd.Series(0, index=common.index, dtype=int)
        for name in adjusted_names:
            selected = set(common.nlargest(k, f"resid_{name}").index)
            counts.loc[list(selected)] += 1
        top_sets[fraction] = counts >= 5

    common["category_count"] = common["category_list"].map(len)
    common["mechanic_count"] = common["mechanic_list"].map(len)
    common["playtime_long"] = common["playing_time"] > 240
    common["playtime_unknown_zero"] = common["playing_time"] == 0
    common["max_players_open"] = common["max_players"] > 10

    print(f"Loaded {len(common):,} common games; stable threshold is >=5/{len(adjusted_names)} adjusted specifications.")
    print("This is a descriptive audience-proxy comparison, not an RQ3 model.")

    for fraction in (0.01, 0.05):
        stable = top_sets[fraction]
        rest = ~stable
        describe_sample(common, stable, f"Stable top-{fraction:.0%} residual candidates")
        describe_sample(common, rest, f"Rest of research population (not stable top-{fraction:.0%})")

        prevalence_table(
            common,
            stable,
            rest,
            "category_list",
            f"Category prevalence: stable top-{fraction:.0%} versus rest",
            min_stable_n=5 if fraction == 0.01 else 15,
        )
        prevalence_table(
            common,
            stable,
            rest,
            "mechanic_list",
            f"Mechanic prevalence: stable top-{fraction:.0%} versus rest",
            min_stable_n=5 if fraction == 0.01 else 15,
        )

        categories = common["category_list"]
        mechanics = common["mechanic_list"]
        cat = lambda tag: categories.map(lambda values: tag_present(values, tag))
        mech = lambda tag: mechanics.map(lambda values: tag_present(values, tag))
        any_mech = lambda tags: mechanics.map(lambda values: any_tag(values, tags))
        any_cat = lambda tags: categories.map(lambda values: any_tag(values, tags))

        # These combinations are pre-specified descriptive patterns. They are
        # not asserted to measure actual audience breadth.
        profiles = {
            "Wargame": cat("Wargame"),
            "Miniatures": cat("Miniatures"),
            "Wargame + Miniatures": cat("Wargame") & cat("Miniatures"),
            "Wargame + World War II": cat("Wargame") & cat("World War II"),
            "Wargame + Simulation mechanic": cat("Wargame") & mech("Simulation"),
            "Wargame + Hexagon Grid": cat("Wargame") & mech("Hexagon Grid"),
            "Wargame + tactical mechanic": cat("Wargame") & any_mech(["Hexagon Grid", "Simulation", "Line of Sight", "Zone of Control"]),
            "Campaign/RPG specialist": mech("Scenario / Mission / Campaign Game") & any_mech(["Role Playing", "Campaign / Battle Card Driven"]),
            "Fantasy + Miniatures": cat("Fantasy") & cat("Miniatures"),
            "Abstract + grid movement": cat("Abstract Strategy") & any_mech(["Hexagon Grid", "Grid Movement"]),
            "Card Game + Hand Management": cat("Card Game") & mech("Hand Management"),
            "Party Game + Humor": cat("Party Game") & cat("Humor"),
            "Children's + Memory": cat("Children's Game") & mech("Memory"),
            "Word + Party": cat("Word Game") & cat("Party Game"),
            "Card Game only proxy": cat("Card Game"),
            "Party Game only proxy": cat("Party Game"),
            "Children's Game only proxy": cat("Children's Game"),
        }
        profile_table(
            common,
            profiles,
            stable,
            rest,
            f"Pre-specified audience-pattern proxies: stable top-{fraction:.0%} versus rest",
        )

        print(f"\nFormat distributions: stable top-{fraction:.0%} versus rest")
        for name, series in [
            ("weight", common["weight"]),
            ("playtime", common["playing_time"]),
            ("min_players", common["min_players"]),
            ("max_players", common["max_players"]),
        ]:
            print(f"\n{name}")
            table = pd.DataFrame({"stable": series[stable], "rest": series[rest]}).describe(percentiles=[.1, .25, .5, .75, .9]).T
            print(table[["count", "mean", "25%", "50%", "75%", "90%"]].to_string(float_format=lambda x: f"{x:.2f}"))
        print(
            f"  stable/rest shares: playtime>240={common.loc[stable, 'playtime_long'].mean():.1%}/{common.loc[rest, 'playtime_long'].mean():.1%}; "
            f"playtime==0={common.loc[stable, 'playtime_unknown_zero'].mean():.1%}/{common.loc[rest, 'playtime_unknown_zero'].mean():.1%}; "
            f"max_players>10={common.loc[stable, 'max_players_open'].mean():.1%}/{common.loc[rest, 'max_players_open'].mean():.1%}"
        )


if __name__ == "__main__":
    main()

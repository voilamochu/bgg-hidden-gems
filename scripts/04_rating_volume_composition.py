"""
Script 04: Rating-volume composition and within-group comparisons
-----------------------------------------------------------------
Investigates which game characteristics are associated with users_rated and
whether the strong users_rated--avg_rating_current relationship persists
within broad characteristic groups.

This is a descriptive RQ1 diagnostic. It does not produce a score, ranking,
or debiasing correction. In particular, BGG rank is treated as a downstream
popularity/ranking variable for description, not as an explanatory control.

Fields examined:
  - release year
  - complexity / weight
  - playtime
  - player count
  - broad categories and mechanics
  - reimplementation status
  - current BGG rank

The script reports both:
  1. composition across rating-volume bands; and
  2. low-volume (100--499) versus high-volume (>=2,500) rating contrasts
     within groups, where group sizes permit.

Several BGG fields contain zero, very large, or otherwise open-ended values.
Those are retained and assigned explicit "unknown/unbounded" bands where
needed instead of being silently discarded.
"""

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

REPO_DIR = Path(__file__).resolve().parent.parent
PROCESSED_PATH = REPO_DIR / "data" / "processed" / "bgg_research_population.parquet"

VOL_BINS = [100, 200, 500, 1000, 2500, 5000, 10000, 25000, 200000]
VOL_LABELS = ["100-199", "200-499", "500-999", "1k-2.5k", "2.5k-5k", "5k-10k", "10k-25k", "25k+"]
LOW_LABEL = "100-499"
HIGH_LABEL = ">=2.5k"


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


def band_summary(df, group_col, order=None, min_count=1):
    """Return composition and rating summaries by a categorical group."""
    rows = []
    groups = order if order is not None else list(df[group_col].dropna().unique())
    for group in groups:
        sub = df[df[group_col] == group]
        if len(sub) < min_count:
            continue
        rows.append(
            {
                "group": group,
                "n": len(sub),
                "median_ratings": sub["users_rated"].median(),
                "median_year": sub["year"].median(),
                "avg_mean": sub["avg_rating_current"].mean(),
                "bayes_mean": sub["bayes_rating"].mean(),
                "avg_low": sub.loc[sub["vol_group"] == LOW_LABEL, "avg_rating_current"].mean(),
                "avg_high": sub.loc[sub["vol_group"] == HIGH_LABEL, "avg_rating_current"].mean(),
                "n_low": (sub["vol_group"] == LOW_LABEL).sum(),
                "n_high": (sub["vol_group"] == HIGH_LABEL).sum(),
                "within_r": sub["avg_rating_current"].corr(sub["logn"]),
            }
        )
    out = pd.DataFrame(rows)
    if len(out):
        out["high_minus_low"] = out["avg_high"] - out["avg_low"]
    return out


def print_composition_table(df, characteristics):
    print("\nComposition by rating-volume band (medians are used for skewed fields)")
    rows = []
    for label in VOL_LABELS:
        sub = df[df["vol_bin"] == label]
        rows.append(
            {
                "volume": label,
                "games": len(sub),
                "year_med": sub["year"].median(),
                "weight_med": sub["weight"].median(),
                "playtime_med": sub["playing_time_valid"].median(),
                "min_players_med": sub["min_players_valid"].median(),
                "max_players_med": sub["max_players_valid"].median(),
                "reimpl": sub["is_reimplementation"].mean(),
                "rank_med": sub["rank_current"].median(),
            }
        )
    table = pd.DataFrame(rows)
    print(table.to_string(index=False, formatters={"reimpl": lambda x: f"{x:.1%}"}))

    print("\nCharacteristic associations with log10(users_rated) in the full population")
    for name, col in characteristics:
        x = df[col]
        print(f"  {name:22s} r={x.corr(df['logn']):+.3f}  rho={x.corr(df['logn'], method='spearman'):+.3f}")


def print_group_contrast(df, group_col, title, order=None, min_group=30, show=30):
    table = band_summary(df, group_col, order=order, min_count=min_group)
    eligible = table[(table["n_low"] >= min_group) & (table["n_high"] >= min_group)].copy()
    print(f"\n{title}")
    print(f"Low volume = {LOW_LABEL}; high volume = {HIGH_LABEL}; groups require >= {min_group} games in each contrast band.")
    if not len(eligible):
        print("  No groups meet the minimum cell size.")
        return table
    if order is None:
        eligible = eligible.sort_values("high_minus_low", ascending=False)
    cols = ["group", "n", "n_low", "n_high", "avg_low", "avg_high", "high_minus_low", "within_r"]
    print(eligible[cols].head(show).to_string(index=False, float_format=lambda x: f"{x:.3f}"))
    return table


def category_or_mechanic_table(df, list_col, title, min_total=200, top_n=20):
    counts = Counter(tag for tags in df[list_col] for tag in tags)
    common = [tag for tag, count in counts.most_common() if count >= min_total][:top_n]
    records = []
    for tag in common:
        has_tag = df[list_col].map(lambda tags: tag in tags)
        sub = df[has_tag]
        low = sub[sub["vol_group"] == LOW_LABEL]
        high = sub[sub["vol_group"] == HIGH_LABEL]
        records.append(
            {
                "tag": tag,
                "all_games": len(sub),
                "tag_in_100-199": (sub["vol_bin"] == "100-199").mean(),
                "tag_in_25k+": (sub["vol_bin"] == "25k+").mean(),
                "prevalence_100-199": has_tag[df["vol_bin"] == "100-199"].mean(),
                "prevalence_25k+": has_tag[df["vol_bin"] == "25k+"].mean(),
                "median_ratings": sub["users_rated"].median(),
                "avg_mean": sub["avg_rating_current"].mean(),
                "low_n": len(low),
                "high_n": len(high),
                "avg_low": low["avg_rating_current"].mean(),
                "avg_high": high["avg_rating_current"].mean(),
                "high_minus_low": high["avg_rating_current"].mean() - low["avg_rating_current"].mean(),
                "within_r": sub["avg_rating_current"].corr(sub["logn"]),
            }
        )
    table = pd.DataFrame(records)
    print(f"\n{title}: most prevalent tags")
    if not len(table):
        print("  No tags meet the minimum prevalence.")
        return table
    fmt = {
        "tag_in_100-199": lambda x: f"{x:.1%}",
        "tag_in_25k+": lambda x: f"{x:.1%}",
        "prevalence_100-199": lambda x: f"{x:.1%}",
        "prevalence_25k+": lambda x: f"{x:.1%}",
        "avg_mean": lambda x: f"{x:.2f}",
        "avg_low": lambda x: f"{x:.2f}",
        "avg_high": lambda x: f"{x:.2f}",
        "high_minus_low": lambda x: f"{x:.2f}",
        "within_r": lambda x: f"{x:.3f}",
    }
    print(table.to_string(index=False, formatters=fmt))
    eligible = table[(table["low_n"] >= 30) & (table["high_n"] >= 30)]
    print(f"\n{title}: within-tag low/high contrast for tags with >=30 games in each band")
    if len(eligible):
        print(
            eligible.sort_values("high_minus_low", ascending=False)[
                ["tag", "all_games", "low_n", "high_n", "avg_low", "avg_high", "high_minus_low", "within_r"]
            ].to_string(index=False, formatters=fmt)
        )
    else:
        print("  No tags meet the minimum cell size.")
    return table


def descriptive_adjustment(df):
    """Quantify remaining association after non-downstream numeric controls."""
    cols = [
        "logn",
        "year_c",
        "weight_c",
        "log_playtime_c",
        "min_players_valid_c",
        "max_players_valid_c",
        "is_reimplementation_num",
    ]
    sub = df.dropna(subset=["avg_rating_current"] + cols).copy()
    y = sub["avg_rating_current"].to_numpy()

    def fit(predictors):
        X = np.column_stack([np.ones(len(sub))] + [sub[c].to_numpy() for c in predictors])
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        resid = y - X @ beta
        sse = np.sum(resid**2)
        sst = np.sum((y - y.mean())**2)
        return 1 - sse / sst, beta

    print("\nDescriptive adjustment (not a debiasing/ranking model)")
    print("Controls exclude BGG rank because rank is downstream of popularity and rating; categories/mechanics are summarized separately.")
    for label, predictors in [
        ("A: volume only", ["logn"]),
        ("B: + year + weight", ["logn", "year_c", "weight_c"]),
        ("C: + playtime + player counts + reimplementation", cols),
    ]:
        r2, beta = fit(predictors)
        idx = predictors.index("logn") + 1
        print(f"  {label:52s} n={len(sub):,}  R2={r2:.4f}  log10(n) beta={beta[idx]:+.4f}")


def main():
    print(f"Loading clean research population from: {PROCESSED_PATH}")
    if not PROCESSED_PATH.exists():
        print(f"Error: processed dataset not found at {PROCESSED_PATH}")
        sys.exit(1)
    df = pd.read_parquet(PROCESSED_PATH).copy()
    print(f"Loaded {len(df):,} games.")

    df["logn"] = np.log10(df["users_rated"])
    df["vol_bin"] = pd.cut(df["users_rated"], bins=VOL_BINS, labels=VOL_LABELS, right=False)
    df["vol_group"] = np.where(df["users_rated"] < 500, LOW_LABEL, HIGH_LABEL)

    # Explicitly separate zero/sentinel values from usable numeric bands.
    df["playing_time_valid"] = df["playing_time"].where(df["playing_time"] > 0)
    df["min_players_valid"] = df["min_players"].where(df["min_players"] > 0)
    df["max_players_valid"] = df["max_players"].where(df["max_players"] > 0)

    # ------------------------------------------------------------------
    # 1. Composition across volume bands
    # ------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("1. COMPOSITION ACROSS RATING-VOLUME BANDS")
    print("=" * 78)
    print_composition_table(
        df,
        [
            ("year", "year"),
            ("weight", "weight"),
            ("playtime", "playing_time_valid"),
            ("min players", "min_players_valid"),
            ("max players", "max_players_valid"),
            ("reimplementation", "is_reimplementation"),
            ("rank (lower=better)", "rank_current"),
        ],
    )
    print("\nField-quality notes used for banding")
    print(f"  playing_time == 0: {(df['playing_time'] == 0).sum():,}; >1440 minutes: {(df['playing_time'] > 1440).sum():,}")
    print(f"  min_players == 0: {(df['min_players'] == 0).sum():,}; max_players == 0: {(df['max_players'] == 0).sum():,}; max_players >10: {(df['max_players'] > 10).sum():,}")
    print(f"  weight missing: {df['weight'].isna().sum():,}; rank missing: {df['rank_current'].isna().sum():,}")

    for col, label in [("playing_time_valid", "Playtime bands (minutes)"), ("max_players_valid", "Maximum-player bands")]:
        if col == "playing_time_valid":
            bins = [0, 30, 60, 120, 240, np.inf]
            labels = ["1-30", "31-60", "61-120", "121-240", "241+"]
        else:
            bins = [0, 2, 4, 6, 10, np.inf]
            labels = ["1-2", "3-4", "5-6", "7-10", "11+ / open"]
        df[label] = pd.cut(df[col], bins=bins, labels=labels, right=True).astype(object)
        df.loc[df[col].isna(), label] = "unknown/zero"
        print_group_contrast(df, label, label, order=labels + ["unknown/zero"], min_group=30)

    # ------------------------------------------------------------------
    # 2. Numeric / structural within-group contrasts
    # ------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("2. WITHIN-GROUP RATING-VOLUME CONTRASTS")
    print("=" * 78)
    df["year_decade"] = ((df["year"] // 10) * 10).astype(int).astype(str) + "s"
    df["weight_tertile"] = pd.qcut(df["weight"], 3, labels=["light", "medium", "heavy"])
    df["min_player_band"] = pd.cut(
        df["min_players_valid"], bins=[0, 1, 2, np.inf], labels=["1", "2", "3+"], right=True
    ).astype(object)
    df.loc[df["min_players_valid"].isna(), "min_player_band"] = "unknown/zero"

    print_group_contrast(df, "year_decade", "Release decade", min_group=30)
    print_group_contrast(df, "weight_tertile", "Complexity / weight tertile", order=["light", "medium", "heavy"], min_group=30)
    print_group_contrast(df, "min_player_band", "Minimum-player band", order=["1", "2", "3+", "unknown/zero"], min_group=30)
    print_group_contrast(df, "is_reimplementation", "Reimplementation status", order=[False, True], min_group=30)

    # ------------------------------------------------------------------
    # 3. Categories and mechanics
    # ------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("3. BROAD CATEGORY AND MECHANIC COMPOSITION")
    print("=" * 78)
    df["category_list"] = df["categories"].map(parse_json_list)
    df["mechanic_list"] = df["mechanics"].map(parse_json_list)
    category_or_mechanic_table(df, "category_list", "Categories", min_total=200, top_n=20)
    category_or_mechanic_table(df, "mechanic_list", "Mechanics", min_total=200, top_n=20)

    # ------------------------------------------------------------------
    # 4. Rank: describe, do not control for it
    # ------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("4. BGG RANK AS A DOWNSTREAM POPULARITY BASELINE")
    print("=" * 78)
    rank = df.dropna(subset=["rank_current"]).copy()
    rank["rank_band"] = pd.cut(
        rank["rank_current"],
        bins=[0, 100, 500, 1000, 2500, 5000, 10000, np.inf],
        labels=["1-100", "101-500", "501-1k", "1k-2.5k", "2.5k-5k", "5k-10k", "10k+"],
        right=True,
    )
    print(f"Rank available for {len(rank):,}/{len(df):,} games ({len(rank)/len(df):.1%}).")
    print(
        f"Among ranked games: rank vs log10(users_rated) Pearson r={rank['rank_current'].corr(rank['logn']):+.3f}, "
        f"Spearman rho={rank['rank_current'].corr(rank['logn'], method='spearman'):+.3f}; "
        f"rank vs avg Pearson r={rank['rank_current'].corr(rank['avg_rating_current']):+.3f}."
    )
    print_group_contrast(rank, "rank_band", "Rating-volume contrast within BGG rank bands", min_group=30)
    print("Rank is not included in the adjustment below: it is a popularity/rating outcome and would risk controlling away the phenomenon under investigation.")

    # ------------------------------------------------------------------
    # 5. Compact descriptive adjustment
    # ------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("5. HOW MUCH DOES A SMALL SET OF CHARACTERISTICS ABSORB?")
    print("=" * 78)
    for col, center in [("year", 2015), ("weight", df["weight"].median()), ("playing_time_valid", df["playing_time_valid"].median()), ("min_players_valid", df["min_players_valid"].median()), ("max_players_valid", df["max_players_valid"].median())]:
        df[f"{col}_c"] = df[col] - center
    df["log_playtime_c"] = np.log1p(df["playing_time_valid"]) - np.log1p(df["playing_time_valid"].median())
    df["log_playtime_c"] = df["log_playtime_c"].replace([np.inf, -np.inf], np.nan)
    df["is_reimplementation_num"] = df["is_reimplementation"].astype(int)
    descriptive_adjustment(df)


if __name__ == "__main__":
    main()

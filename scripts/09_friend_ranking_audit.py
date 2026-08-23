"""
Script 09: Audit of the friend-provided debiased ranking
----------------------------------------------------------
This audit is deliberately limited to what the current game-level files can
support. It reports whether the friend-provided CSV is present and records its
schema, then examines whether current and dump_* fields are consistent with an
earlier BGG snapshot.

It does not validate the friend's user-level method, reconstruct a ranking, or
treat dump_geek_rating as the friend's debiased result. This script inspects
the friend file for availability/schema only; game-level comparison is
implemented separately in 10_friend_debiased_comparison.py.
"""

from pathlib import Path

import numpy as np
import pandas as pd

REPO_DIR = Path(__file__).resolve().parent.parent
RAW_PATH = REPO_DIR / "data" / "raw" / "bgg_games_current.parquet"
PROCESSED_PATH = REPO_DIR / "data" / "processed" / "bgg_research_population.parquet"
FRIEND_PATH = REPO_DIR / "data" / "raw" / "complete_2025_bgg_debiased_ranks.csv"


def pair_summary(df, left, right):
    paired = df[[left, right]].dropna()
    if not len(paired):
        return None
    delta = paired[left] - paired[right]
    return {
        "left": left,
        "right": right,
        "n": len(paired),
        "corr": paired[left].corr(paired[right]),
        "same_share": (delta == 0).mean(),
        "left_greater_share": (delta > 0).mean(),
        "left_lower_share": (delta < 0).mean(),
        "median_delta": delta.median(),
        "p10_delta": delta.quantile(.10),
        "p90_delta": delta.quantile(.90),
        "min_delta": delta.min(),
        "max_delta": delta.max(),
    }


def print_snapshot_audit(df, label):
    print(f"\n{label}: n={len(df):,}")
    pairs = [
        ("users_rated", "dump_voters"),
        ("avg_rating_current", "dump_avg_rating"),
        ("bayes_rating", "dump_geek_rating"),
        ("rank_current", "dump_rank"),
        ("year", "dump_year"),
    ]
    rows = [pair_summary(df, left, right) for left, right in pairs]
    table = pd.DataFrame([row for row in rows if row is not None])
    print(table.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    paired = df[["users_rated", "dump_voters", "year", "weight"]].dropna().copy()
    paired["rating_count_delta"] = paired["users_rated"] - paired["dump_voters"]
    paired["volume_band"] = pd.cut(
        paired["users_rated"],
        bins=[100, 200, 500, 1000, 2500, 5000, 10000, 25000, np.inf],
        labels=["100-199", "200-499", "500-999", "1k-2.5k", "2.5k-5k", "5k-10k", "10k-25k", "25k+"],
        right=False,
    )
    paired["decade"] = ((paired["year"] // 10) * 10).astype(int).astype(str) + "s"
    paired["weight_band"] = pd.qcut(paired["weight"], 5, duplicates="drop")
    for group in ["volume_band", "decade", "weight_band"]:
        summary = paired.groupby(group, observed=True).agg(
            n=("rating_count_delta", "size"),
            median_count_delta=("rating_count_delta", "median"),
            share_current_higher=("rating_count_delta", lambda s: (s > 0).mean()),
            p10_count_delta=("rating_count_delta", lambda s: s.quantile(.10)),
            p90_count_delta=("rating_count_delta", lambda s: s.quantile(.90)),
        )
        print(f"\nRating-count current minus dump by {group}")
        print(summary.to_string(float_format=lambda x: f"{x:.3f}"))


def main():
    if not RAW_PATH.exists() or not PROCESSED_PATH.exists():
        raise FileNotFoundError("Required raw or processed parquet file is missing")

    raw = pd.read_parquet(RAW_PATH)
    research = pd.read_parquet(PROCESSED_PATH)
    possible_friend_fields = [
        column for column in sorted(set(raw.columns) | set(research.columns))
        if any(token in column.lower() for token in ["debiased", "debias", "friend"])
    ]

    print(f"Raw rows: {len(raw):,}; processed research rows: {len(research):,}")
    print(f"Possible friend/debiased fields: {possible_friend_fields or 'NONE'}")
    if FRIEND_PATH.exists():
        friend = pd.read_csv(FRIEND_PATH)
        print(
            f"Friend dataset is available at {FRIEND_PATH}: {len(friend):,} rows, "
            f"{len(friend.columns)} columns; game_id unique={friend['game_id'].is_unique}, "
            f"debiased_rating non-null={friend['debiased_rating'].notna().sum():,}."
        )
        print("Availability/schema only: the friend result is not analyzed by this audit.")
    else:
        print(
            "No debiased_rating field or separate friend-ranking file is present in the current repo. "
            "dump_geek_rating is retained as a legacy BGG field and is not substituted for it."
        )

    timestamps = pd.to_datetime(raw["attrs_fetched_at"], unit="s", utc=True).dropna()
    print(
        "Current scrape timestamp range: "
        f"{timestamps.min().isoformat()} to {timestamps.max().isoformat()}; "
        f"unique timestamps={timestamps.nunique():,}."
    )
    print(
        "There is no dump timestamp or field-level provenance date. Snapshot status can therefore "
        "only be assessed indirectly from paired values."
    )

    print_snapshot_audit(research, "Research population paired-field audit")
    print(
        "\nInterpretation: a mostly positive current-minus-dump voter-count change is consistent with "
        "dump_* being an earlier/legacy BGG snapshot, but it does not prove the snapshot date. "
        "The same-platform fields are not an independent audience or user-level validation sample."
    )
    if FRIEND_PATH.exists():
        print(
            "\nFriend-result comparison status: available. This audit records availability/schema only; "
            "see 10_friend_debiased_comparison.py for the separate game-level comparison."
        )
    else:
        print(
            "\nFriend-result comparison status: unavailable. Promoted/demoted games and variation of the "
            "friend's correction by volume, year, complexity, or game type cannot be characterized "
            "until the actual debiased output is supplied."
        )


if __name__ == "__main__":
    main()

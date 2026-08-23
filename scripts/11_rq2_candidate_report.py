"""
Script 11: Generate a provisional RQ2 candidate-screening report.
------------------------------------------------------------------
Reuses the unchanged RQ2 specifications from script 05 and the stability
convention from script 06. This is report generation only: it does not fit a
new model, change the candidate definition, or produce an RQ3 score.
"""

import importlib.util
import json
from pathlib import Path

import pandas as pd

REPO_DIR = Path(__file__).resolve().parent.parent
BASELINE_PATH = REPO_DIR / "scripts" / "05_rq2_expected_rating_baseline.py"
FRIEND_PATH = REPO_DIR / "data" / "raw" / "complete_2025_bgg_debiased_ranks.csv"
REPORT_PATH = REPO_DIR / "docs" / "rq2_candidate_report.md"
STABILITY_MIN = 5
TOP_FRACTION = 0.01
REPORT_N = 25


def load_baseline_module():
    spec = importlib.util.spec_from_file_location("rq2_expected_rating_baseline", BASELINE_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load baseline module from {BASELINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_tags(value):
    if pd.isna(value) or not isinstance(value, str):
        return []
    try:
        parsed = json.loads(value)
    except Exception:
        return []
    return [str(item) for item in parsed] if isinstance(parsed, list) else []


def compact_tags(tags, limit=4):
    if not tags:
        return "not listed"
    shown = ", ".join(tags[:limit])
    remaining = len(tags) - limit
    return f"{shown}; +{remaining} more" if remaining > 0 else shown


def format_number(value, digits=2):
    return "—" if pd.isna(value) else f"{value:.{digits}f}"


def format_playtime(value):
    if pd.isna(value) or value <= 0:
        return "not stated"
    return f"{int(value)} min"


def format_players(row):
    if pd.isna(row["min_players"]) or pd.isna(row["max_players"]):
        return "not stated"
    return f"{int(row['min_players'])}–{int(row['max_players'])}"


def build_candidates():
    baseline = load_baseline_module()
    _, common, specs, _, _ = baseline.prepare_model_data()
    adjusted_names = [
        name for name in specs if name not in {"S0_volume", "S0b_volume_bands"}
    ]

    for name, columns in specs.items():
        fit = baseline.fit_model(common, columns)
        common[f"pred_{name}"] = fit["pred"]
        common[f"resid_{name}"] = fit["resid"]

    residual_cols = [f"resid_{name}" for name in adjusted_names]
    common["mean_resid_7"] = common[residual_cols].mean(axis=1)
    common["resid_sd_7"] = common[residual_cols].std(axis=1)
    top_k = max(1, int(TOP_FRACTION * len(common)))
    counts = pd.Series(0, index=common.index, dtype=int)
    for name in adjusted_names:
        selected = common.nlargest(top_k, f"resid_{name}").index
        counts.loc[list(selected)] += 1
    common["stable_count_7"] = counts

    candidates = common[common["stable_count_7"] >= STABILITY_MIN].copy()
    candidates = candidates.sort_values(
        ["mean_resid_7", "stable_count_7"], ascending=[False, False]
    ).head(REPORT_N)

    if FRIEND_PATH.exists():
        friend = pd.read_csv(FRIEND_PATH, usecols=["game_id", "debiased_rating"])
        candidates = candidates.merge(friend, on="game_id", how="left")
    else:
        candidates["debiased_rating"] = pd.NA
    return candidates, len(common), top_k, len(adjusted_names)


def render_profile(row):
    categories = compact_tags(parse_tags(row["categories"]), limit=4)
    mechanics = compact_tags(parse_tags(row["mechanics"]), limit=4)
    return (
        f"Categories: {categories}. Mechanics: {mechanics}. "
        f"Audience format: {format_players(row)} players; "
        f"{format_number(row['weight'], 1)} weight; {format_playtime(row['playing_time'])}."
    )


def render_report(candidates, common_n, top_k, adjusted_n):
    lines = [
        "# Provisional RQ2 Candidate Report",
        "",
        "> **Screening output, not a hidden-gem ranking.** These games are robust positive residual candidates under the current game-level BGG baseline. Broad appeal cannot be established from this dataset.",
        "",
        "## Method",
        "",
        f"The report uses the existing **{adjusted_n} adjusted RQ2 specifications** (S1, S1b, S2, S3, S4, S5, and S6) on the unchanged **{common_n:,}-game complete-case population**. For each specification, the top 1% means the {top_k} largest positive residuals. A candidate is called stable when it appears in at least **{STABILITY_MIN}/{adjusted_n}** of those seven top sets, matching the existing robustness work. The 25 records below are the stable candidates with the largest mean residual across the seven adjusted specifications; no new model or feature was introduced.",
        "",
        "`Expected (S3)` is the fitted expected raw rating from the existing primary category baseline. `Residual (S3)` is `avg_rating_current - Expected (S3)`. `Mean R7` is the mean residual across the seven adjusted specifications and is used only to order this provisional shortlist. `SD R7` shows dispersion across those specifications. `Friend` is the supplied `debiased_rating` matched by `game_id`, where available.",
        "",
        "## Candidate shortlist",
        "",
        "| # | Candidate | Stable | Mean R7 | SD R7 | Raw | Expected (S3) | Residual (S3) | Ratings | Bayes | Friend | Weight | Playtime | Profile |",
        "|---:|---|:---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for number, (_, row) in enumerate(candidates.iterrows(), start=1):
        title = str(row["title"]).replace("|", "\\|")
        profile = render_profile(row).replace("|", "\\|")
        lines.append(
            f"| {number} | **{title}** ({int(row['year'])}) | "
            f"{int(row['stable_count_7'])}/7 | {row['mean_resid_7']:.2f} | "
            f"{row['resid_sd_7']:.2f} | {row['avg_rating_current']:.2f} | "
            f"{row['pred_S3_categories']:.2f} | {row['resid_S3_categories']:+.2f} | "
            f"{int(row['users_rated']):,} | {row['bayes_rating']:.2f} | "
            f"{format_number(row['debiased_rating'])} | {row['weight']:.1f} | "
            f"{format_playtime(row['playing_time'])} | {profile} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation and limitations",
            "",
            "- These are **higher-than-expected** games under explicit descriptive baselines, not proven underrated games and not latent-quality estimates.",
            "- The stability count measures reuse of the same observed game-level ratings under related specifications. It is not independent replication, statistical significance, or temporal validation.",
            "- The list contains related records, editions, and family entries—especially several Monikers records—so the 25 rows should not be interpreted as 25 independent discoveries.",
            "- The 100-rating floor, equal game weighting, incomplete and overlapping BGG tags, omitted interactions, and specification dependence limit interpretation. Some playtime fields are zero/not stated and some player-count values may be open-ended metadata.",
            "- `bayes_rating` and `debiased_rating` are comparison baselines only. The friend score is included where matched but has not been validated against user-level data.",
            "- The dataset has no rater identities, audience segments, exposure denominator, non-raters, or independent reach outcome. Nothing in this report establishes broad appeal or hidden-gem status.",
        ]
    )
    return "\n".join(lines) + "\n"


def main():
    candidates, common_n, top_k, adjusted_n = build_candidates()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        render_report(candidates, common_n, top_k, adjusted_n), encoding="utf-8"
    )
    print(f"Wrote {REPORT_PATH} with {len(candidates)} candidates.")


if __name__ == "__main__":
    main()

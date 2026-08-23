"""
Script 08: RQ3 audience-reach identifiability audit
-----------------------------------------------------
Audits whether the game-level BGG dataset contains an independent outcome
that can identify appeal beyond a game's existing rater niche.

This script deliberately does not fit a model, construct an audience score,
or rank games. It:

  - inventories field coverage and provenance categories;
  - quantifies redundancy among current and legacy BGG rating fields;
  - checks whether family tags contain exposure/opportunity metadata; and
  - compares those descriptive flags with the already-defined stable RQ2
    residual sets without treating them as evidence of broad appeal.

The output is an identifiability audit. A field can be useful context without
being an independent measure of cross-audience reach.
"""

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_DIR = Path(__file__).resolve().parent.parent
BASELINE_PATH = REPO_DIR / "scripts" / "05_rq2_expected_rating_baseline.py"
RAW_PATH = REPO_DIR / "data" / "raw" / "bgg_games_current.parquet"
PROCESSED_PATH = REPO_DIR / "data" / "processed" / "bgg_research_population.parquet"


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


FIELD_AUDIT = [
    ("game_id", "identifier", "No audience evidence"),
    ("title", "identifier/content label", "No audience evidence"),
    ("title_clean", "derived identifier", "No audience evidence"),
    ("link", "source link", "No audience evidence"),
    ("thumbnail", "image metadata", "No audience evidence"),
    ("attrs_fetched_at", "single scrape timestamp", "No longitudinal evidence"),
    ("has_non_latin_script", "derived title metadata", "No audience evidence"),
    ("year", "release context / RQ2 input", "Context; not reach evidence"),
    ("weight", "complexity / RQ2 input", "Context; not reach evidence"),
    ("num_weights", "metadata count", "Context; not reach evidence"),
    ("min_players", "format / RQ2 input", "Context; not reach evidence"),
    ("max_players", "format / RQ2 input", "Context; not reach evidence"),
    ("best_players", "BGG user preference metadata", "Selected consensus; not independent reach"),
    ("good_players", "BGG user preference metadata", "Selected consensus; not independent reach"),
    ("min_playtime", "format / RQ2 input", "Context; not reach evidence"),
    ("max_playtime", "format / RQ2 input", "Context; not reach evidence"),
    ("playing_time", "format / RQ2 input", "Context; not reach evidence"),
    ("categories", "BGG descriptive taxonomy", "Audience-style context; no observed audience"),
    ("mechanics", "BGG descriptive taxonomy", "Audience-style context; no observed audience"),
    ("families", "BGG taxonomy / linked metadata", "Possible exposure context; no reach outcome"),
    ("designers", "credit / identity metadata", "Possible recognition context; no reach outcome"),
    ("description", "editorial text", "Content context; no reach outcome"),
    ("is_expansion", "population filter", "Selection variable; not reach evidence"),
    ("expands_name", "relationship metadata", "Selection/context; not reach evidence"),
    ("is_reimplementation", "product relationship / RQ2 input", "Context; not independent reach"),
    ("reimplements_name", "relationship metadata", "Context; not reach evidence"),
    ("users_rated", "current BGG rating participation", "Outcome for one selected platform; RQ2 input"),
    ("avg_rating_current", "current BGG rating outcome", "RQ2 target; downstream of selected raters"),
    ("bayes_rating", "BGG shrinkage/ranking statistic", "Derived from rating outcome and volume"),
    ("rank_current", "BGG popularity/rating rank", "Downstream of BGG rating/popularity"),
    ("subranks", "BGG rank subdivisions", "Downstream of BGG taxonomy/ranking"),
    ("dump_rank", "legacy BGG rank field", "Same-platform downstream measure"),
    ("dump_geek_rating", "legacy BGG Bayesian-like field", "Same-platform derived measure"),
    ("dump_avg_rating", "legacy BGG average field", "Same-platform rating outcome"),
    ("dump_voters", "legacy BGG voter-count field", "Same-platform participation outcome"),
    ("dump_year", "legacy release-year field", "Context; no audience evidence"),
]


def family_flags(series):
    values = series.map(parse_json_list)
    return pd.DataFrame(
        {
            "has_digital_implementation_tag": values.map(lambda xs: any(x.startswith("Digital Implementations:") for x in xs)),
            "has_tabletop_arena_or_sim": values.map(lambda xs: any(x in xs for x in ["Digital Implementations: Tabletopia", "Digital Implementations: Board Game Arena", "Digital Implementations: TableTop Simulator Mod", "Digital Implementations: VASSAL", "Digital Implementations: Yucata"])),
            "has_steam_or_mobile": values.map(lambda xs: any(x in xs for x in ["Digital Implementations: Steam", "Digital Implementations: Apple App Store", "Digital Implementations: Google Play"])),
            "has_kickstarter": values.map(lambda xs: "Crowdfunding: Kickstarter" in xs),
            "has_watch_it_played": values.map(lambda xs: "Misc: Watch It Played How To Videos" in xs),
            "has_hall_of_fame_tag": values.map(lambda xs: any(x in xs for x in ["Misc: BGG Hall of Fame", "Misc: Dice Tower Hall of Fame"])),
            "has_game_family_link": values.map(lambda xs: any(x.startswith("Game:") for x in xs)),
            "has_series_link": values.map(lambda xs: any(x.startswith("Series:") for x in xs)),
        }
    ).astype(bool)


def compare_field_pairs(df):
    pairs = [
        ("users_rated", "dump_voters"),
        ("avg_rating_current", "dump_avg_rating"),
        ("bayes_rating", "dump_geek_rating"),
        ("rank_current", "dump_rank"),
    ]
    rows = []
    for left, right in pairs:
        paired = df[[left, right]].dropna()
        if not len(paired):
            continue
        delta = paired[left] - paired[right]
        rows.append(
            {
                "left": left,
                "right": right,
                "n": len(paired),
                "corr": paired[left].corr(paired[right]),
                "exact_same": int((delta == 0).sum()),
                "median_delta": delta.median(),
                "p10_delta": delta.quantile(.10),
                "p90_delta": delta.quantile(.90),
                "max_abs_delta": delta.abs().max(),
            }
        )
    return pd.DataFrame(rows)


def stable_masks(common, specs, baseline):
    adjusted = [name for name in specs if name not in {"S0_volume", "S0b_volume_bands"}]
    masks = {}
    for name, columns in specs.items():
        common[f"resid_{name}"] = baseline.fit_model(common, columns)["resid"]
    for fraction in (.01, .05):
        k = max(1, int(fraction * len(common)))
        counts = pd.Series(0, index=common.index, dtype=int)
        for name in adjusted:
            selected = set(common.nlargest(k, f"resid_{name}").index)
            counts.loc[list(selected)] += 1
        masks[f"stable_top{int(fraction * 100)}"] = counts >= 5
    return masks


def print_field_audit(df):
    rows = []
    for field, role, interpretation in FIELD_AUDIT:
        if field not in df:
            continue
        rows.append(
            {
                "field": field,
                "non_null": int(df[field].notna().sum()),
                "coverage": df[field].notna().mean(),
                "role": role,
                "interpretation": interpretation,
            }
        )
    table = pd.DataFrame(rows)
    print("\nFIELD INVENTORY AND PROVENANCE CLASSIFICATION")
    print(table.to_string(index=False, formatters={"coverage": lambda x: f"{x:.1%}"}))
    print(f"\nFields audited: {len(table)}; fields with any non-null value: {sum(table['non_null'] > 0)}")


def print_family_coverage(df, flags, masks):
    print("\nFAMILY-TAG EXPOSURE/RECOGNITION CONTEXT (DESCRIPTIVE ONLY)")
    groups = {"all common games": pd.Series(True, index=df.index)}
    groups.update(masks)
    for name, mask in groups.items():
        sub = flags[mask]
        values = {column: sub[column].mean() for column in flags}
        print(f"\n{name}: n={int(mask.sum()):,}")
        print(pd.Series(values).map(lambda x: f"{x:.1%}").to_string())


def main():
    if not PROCESSED_PATH.exists() or not RAW_PATH.exists():
        print("Required raw/processed data not found.")
        sys.exit(1)

    population = pd.read_parquet(PROCESSED_PATH)
    raw = pd.read_parquet(RAW_PATH)
    print(f"Processed research population: {len(population):,} rows; raw fields: {len(raw.columns)}")
    print_field_audit(population)

    print("\nSAME-PLATFORM FIELD REDUNDANCY")
    pairs = compare_field_pairs(population)
    print(pairs.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print(
        "\nInterpretation: paired dump/current fields are redundant BGG outcomes or legacy copies; "
        "their availability does not create an independent audience outcome."
    )

    baseline = load_baseline_module()
    _, common, specs, _, _ = baseline.prepare_model_data()
    masks = stable_masks(common, specs, baseline)
    flags = family_flags(common["families"])
    print_family_coverage(common, flags, masks)

    print("\nMISSING AUDIENCE OUTCOME FIELDS")
    missing_concepts = [
        "rater identity or audience segment",
        "ratings by country/language/market or demographic group",
        "number of people exposed but not rating",
        "plays, ownership, sales, crowdfunding conversion, or external traffic",
        "independent review/award outcome with audience-level coverage",
        "repeated rating observations tied to a known time series",
    ]
    for concept in missing_concepts:
        print(f"- {concept}")
    print(
        "\nConclusion: no available field directly observes cross-audience reach or appeal beyond "
        "the selected BGG rating population. RQ3 is not identified by this game-level dataset."
    )


if __name__ == "__main__":
    main()

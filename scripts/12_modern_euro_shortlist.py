"""Generate the provisional modern Euro-style RQ2 shortlist.

This is a screening/reporting step only.  It imports the unchanged RQ2
specifications from script 05, applies the existing seven-specification
stability convention, and then applies explicit metadata and qualitative
screens.  It does not fit a new model or create a new score.
"""

import importlib.util
import json
import re
from pathlib import Path

import pandas as pd


REPO_DIR = Path(__file__).resolve().parent.parent
BASELINE_PATH = REPO_DIR / "scripts" / "05_rq2_expected_rating_baseline.py"
REPORT_PATH = REPO_DIR / "docs" / "modern_euro_shortlist.md"
STABILITY_MIN = 5
TOP_FRACTION = 0.01

# These are deliberately hand-screened records from the stable top-1% pool.
# The notes describe the metadata-based interpretation used for this report;
# they are not a new ranking feature.
SELECTED_IDS = {
    436591: (
        "Spellcaster-card competition using hand management, interrupts, and "
        "set collection; its listed win condition is to collect spellcaster "
        "cards. The two-player, take-that profile makes this a borderline "
        "Euro-style card candidate rather than a conventional economic Euro."
    ),
    336323: (
        "A competitive strategy game using deck/pool building, tile placement, "
        "and variable player powers. It is more thematic and IP-led than a "
        "classic Euro, but its listed mechanisms provide a defensible strategic "
        "fit for this exploratory screen."
    ),
    245240: (
        "A goblin-versus-goblin card battle with hand management, memory, "
        "bluffing, and take-that interaction. This is a light, confrontational "
        "card-game edge case, retained because hand management is central."
    ),
    188885: (
        "Players collect, exchange, and trade perfume bases and essences to "
        "produce and sell perfumes. Its economic/industry theme, rondel, set "
        "collection, and worker placement make it the clearest conventional "
        "Euro-style candidate in this shortlist."
    ),
    350108: (
        "A Colombian cooking-contest card game built around hand management and "
        "set collection. It is a lighter card design, included as a cautious "
        "gateway-style Euro candidate rather than a heavy strategy claim."
    ),
}

SCREENING_AUDIT = {
    436591: (
        "UNCERTAIN",
        "No expansion, reimplementation, edition, or explicit unreleased tag; 2025 record with only the two-player family tag.",
        "141 ratings and current BGG rank 10,618; the older dump has only 5 voters and no rank, and no designer is listed. The recent/low-volume record cannot establish general release visibility or reduce sample-selection concern.",
    ),
    336323: (
        "UNCERTAIN",
        "No expansion, reimplementation, edition, or explicit unreleased tag; 2021 record with Kickstarter history only.",
        "141 ratings, current BGG rank 16,981, no designer listed, and an IP/theme-led profile. The +1.83 S3 residual may be especially sensitive to a small, self-selected rater pool.",
    ),
    245240: (
        "KEEP",
        "Boardgame link, `is_expansion=False`, no expansion/reimplementation/edition family, and no explicit unreleased tag; 2020 record.",
        "213 ratings and BGG rank 21,463 indicate limited observed reach, but the malformed short description and missing designer metadata reduce metadata confidence. The high residual remains vulnerable to niche selection.",
    ),
    188885: (
        "KEEP",
        "Boardgame link, `is_expansion=False`, no expansion/reimplementation/edition family, and no explicit unreleased tag; 2018 record. Catarse is a crowdfunding-history tag, not an unreleased-status tag.",
        "116 ratings and BGG rank 9,653; raw 8.05 versus Bayes 5.60 and residual +1.44 indicate a thin observed base. This is a candidate for follow-up, not evidence of broad appeal.",
    ),
    350108: (
        "UNCERTAIN",
        "Boardgame link, `is_expansion=False`, no expansion/reimplementation/edition family, and no explicit unreleased tag; 2021 record.",
        "114 ratings and BGG rank 10,535; only a broad Card Game category plus hand-management/set-collection metadata are available. Its Euro fit and release visibility are less strongly evidenced than Grasse's.",
    ),
}

EURO_TAGS = {
    "economic",
    "city building",
    "civilization",
    "industry / manufacturing",
    "trains",
    "transportation",
    "farming",
    "worker placement",
    "hand management",
    "engine building",
    "tile placement",
    "area majority / influence",
    "auction / bidding",
    "variable player powers",
    "network and route building",
    "market",
    "income",
    "ownership",
    "commodity speculation",
    "set collection",
    "open drafting",
    "deck, bag, and pool building",
    "modular board",
    "contracts",
    "resource management",
    "stock holding",
    "pattern building",
    "territory building",
    "route building",
    "trading",
    "tableau building",
}

EXCLUDED_TAGS = {
    "sports",
    "party game",
    "action / dexterity",
    "wargame",
    "simulation",
    "storytelling",
    "narrative choice / paragraph",
    "role playing",
    "murder / mystery",
    "fighting",
    "dice rolling",
}

EDITION_MARKERS = re.compile(
    r"collector|deluxe|big\s*box|anniversary|ultimate edition|special edition|"
    r"heritage edition|mega box|decennial|maximus edition|epic edition|"
    r"complete collector|gamefound edition|kickstarter edition|second edition|"
    r"premium|fan expansion|third-party expansion|bundle|essentials",
    re.IGNORECASE,
)


def load_baseline_module():
    spec = importlib.util.spec_from_file_location("rq2_baseline", BASELINE_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load baseline from {BASELINE_PATH}")
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


def build_pool():
    baseline = load_baseline_module()
    _, common, specs, _, _ = baseline.prepare_model_data()
    adjusted = [
        name for name in specs if name not in {"S0_volume", "S0b_volume_bands"}
    ]

    for name, columns in specs.items():
        fit = baseline.fit_model(common, columns)
        common[f"pred_{name}"] = fit["pred"]
        common[f"resid_{name}"] = fit["resid"]

    residual_cols = [f"resid_{name}" for name in adjusted]
    common["mean_r7"] = common[residual_cols].mean(axis=1)
    common["sd_r7"] = common[residual_cols].std(axis=1)
    top_k = max(1, int(TOP_FRACTION * len(common)))
    counts = pd.Series(0, index=common.index, dtype=int)
    for name in adjusted:
        counts.loc[list(common.nlargest(top_k, f"resid_{name}").index)] += 1
    common["stable_count_7"] = counts

    # First-pass metadata screen.  The explicit status filter is redundant
    # after cleaning, but keeps this report auditable if run on a bad input.
    stable = common[(common["stable_count_7"] >= STABILITY_MIN) & (common["year"] >= 2000)].copy()
    stable["category_list"] = stable["categories"].map(parse_tags)
    stable["mechanic_list"] = stable["mechanics"].map(parse_tags)
    stable["family_list"] = stable["families"].map(parse_tags)
    stable["all_tags_lower"] = stable.apply(
        lambda row: {tag.lower() for tag in row["category_list"] + row["mechanic_list"]},
        axis=1,
    )
    euro_screen = stable[stable["all_tags_lower"].map(lambda tags: bool(tags & EURO_TAGS))]
    euro_screen = euro_screen[
        ~euro_screen["all_tags_lower"].map(lambda tags: bool(tags & EXCLUDED_TAGS))
    ]

    def excluded_record(row):
        families = row["family_list"]
        family_text = "; ".join(families)
        family_lower = [value.lower() for value in families]
        family_variant = any(
            value.startswith("game:")
            or "versions & editions:" in value
            or "fan expansion" in value
            or "third-party expansion" in value
            for value in family_lower
        )
        return bool(row["is_reimplementation"]) or family_variant or bool(
            EDITION_MARKERS.search(str(row["title"]))
            or EDITION_MARKERS.search(family_text)
        )

    generic_survivors = euro_screen[~euro_screen.apply(excluded_record, axis=1)].copy()

    # Two metadata survivors are removed after reading the recorded profile:
    # one is explicitly campaign/dungeon-crawler oriented and the other is
    # explicitly narrative-choice/solo oriented.  These are not model rules.
    manual_exclusions = {
        430809: "campaign/dungeon-crawler profile",
        389593: "narrative-choice/solo profile",
    }
    manual_removed_n = int(generic_survivors.game_id.isin(manual_exclusions).sum())
    final = generic_survivors[~generic_survivors.game_id.isin(manual_exclusions)].copy()
    if set(SELECTED_IDS) != set(final.game_id.astype(int)):
        raise AssertionError(
            "The hand-screened shortlist no longer matches the current stable pool: "
            f"expected {sorted(SELECTED_IDS)}, got {sorted(final.game_id.astype(int))}"
        )

    final["screen_note"] = final["game_id"].map(SELECTED_IDS)
    final = final.sort_values(["mean_r7", "stable_count_7"], ascending=[False, False])
    return (
        final,
        len(common),
        top_k,
        len(adjusted),
        len(euro_screen),
        len(generic_survivors),
        manual_removed_n,
    )


def fmt(value, digits=2):
    return "—" if pd.isna(value) else f"{value:.{digits}f}"


def render_report(final, common_n, top_k, adjusted_n, euro_n, generic_n, manual_removed_n):
    lines = [
        "# Provisional Modern Eurogame-Style Shortlist",
        "",
        "> **Screening output, not a hidden-gem ranking.** These are robust positive-residual RQ2 candidates that survive a conservative modern Eurogame-style metadata screen. The current game-level dataset cannot establish broad appeal or hidden-gem status.",
        "",
        "## Method",
        "",
        f"The shortlist reuses the unchanged seven adjusted RQ2 specifications (S1, S1b, S2, S3, S4, S5, and S6) on the corrected **{common_n:,}-game** complete-case population. Each specification contributes its top 1% ({top_k} games); stability is unchanged at selection in at least **{STABILITY_MIN}/{adjusted_n}** specifications. The initial screen required release year ≥2000 and at least one listed Euro-associated category/mechanic (for example economic, worker placement, hand management, tile placement, auctions, or resource/engine-building-related tags).",
        "",
        f"The initial metadata screen left **{euro_n}** stable candidates. Metadata exclusions removed family/edition records, explicit reimplementations, and clearly non-Euro profiles; this left **{generic_n}** records before the final profile review. **{manual_removed_n}** additional record was removed as campaign/dungeon-crawler oriented. The five records below were retained as the strongest defensible shortlist; the selection is a qualitative screen, not a new score or model.",
        "",
        "`Expected (S3)` is the unchanged primary category-baseline prediction. `Residual (S3)` is raw average minus that prediction. `Mean R7` is the mean residual across the seven adjusted specifications and is shown for context; `Stable` is the existing 5/7 selection count.",
        "",
        "## Shortlist",
        "",
        "| # | Game | Year | Raw rating | Ratings | Expected (S3) | Residual (S3) | Mean R7 | Stable | Design and screening rationale |",
        "|---:|---|---:|---:|---:|---:|---:|---:|:---:|---|",
    ]
    for number, (_, row) in enumerate(final.iterrows(), start=1):
        categories = ", ".join(row["category_list"])
        mechanics = ", ".join(row["mechanic_list"])
        profile = (
            f"{row['screen_note']} Categories: {categories}. "
            f"Mechanics: {mechanics}."
        ).replace("|", "\\|")
        title = str(row["title"]).replace("|", "\\|")
        lines.append(
            f"| {number} | **{title}** | {int(row['year'])} | "
            f"{row['avg_rating_current']:.2f} | {int(row['users_rated']):,} | "
            f"{row['pred_S3_categories']:.2f} | {row['resid_S3_categories']:+.2f} | "
            f"{row['mean_r7']:+.2f} | {int(row['stable_count_7'])}/{adjusted_n} | {profile} |"
        )
    lines.extend(
        [
            "",
            "## Final metadata screening",
            "",
            "The available BGG fields support a metadata audit, not definitive proof of general/public release. All five records have a valid 2018–2025 year, a `/boardgame/` link, `is_expansion=False`, null `expands_name`, `is_reimplementation=False`, null `reimplements_name`, and neither explicit administrative unreleased tag. None has a `Game:` family or edition marker. BGG rank is reported as context only; it is not an RQ2 predictor or a measure of broad appeal.",
            "",
            "| Game | Classification | Standalone/release and edition evidence | Main concern |",
            "|---|:---:|---|---|",
        ]
    )
    for _, row in final.iterrows():
        classification, evidence, concern = SCREENING_AUDIT[int(row["game_id"])]
        lines.append(
            f"| **{str(row['title']).replace('|', '\\|')}** | **{classification}** | "
            f"{evidence} | {concern} |"
        )
    lines.extend(
        [
            "",
            "**Classification meaning:** `KEEP` means no concrete exclusion is visible in the available metadata and the record remains suitable for provisional follow-up. `UNCERTAIN` means no exclusion is proven, but release visibility, metadata completeness, genre fit, or sample size is too weak for a clean keep decision. No candidate received a metadata-grounded `REMOVE` classification in this pass.",
            "",
            "## Interpretation and limitations",
            "",
            "- The shortlist identifies games that are higher-rated than the unchanged RQ2 baseline expects, with specification-level stability. It does not estimate true underlying quality, selection-corrected quality, or broad appeal.",
            "- The clear conventional-Euro case is Grasse. The other four are lighter, thematic, two-player, or confrontational card designs; retaining them reflects the requested mechanism screen and should not be read as a claim that they belong to the same audience.",
            "- BGG categories and mechanics are incomplete, overlapping, and partly subjective. The screen can remove obvious mismatches and editions, but it cannot determine genre or audience breadth reliably.",
            "- The corrected population excludes records with explicit BGG `Admin: Upcoming Releases` or `Admin: Unreleased Games` tags. No selected record has such a status in the processed data.",
            "- Family/edition and reimplementation exclusions rely on available BGG family/status metadata and explicit edition markers. They may miss obscure relationships or exclude a legitimate standalone design.",
            "- These candidates remain provisional screening subjects for later research. Broad appeal requires independent audience or exposure evidence that this game-level dataset does not contain.",
        ]
    )
    return "\n".join(lines) + "\n"


def main():
    final, common_n, top_k, adjusted_n, euro_n, generic_n, manual_removed_n = build_pool()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        render_report(
            final,
            common_n,
            top_k,
            adjusted_n,
            euro_n,
            generic_n,
            manual_removed_n,
        ),
        encoding="utf-8",
    )
    print(f"Wrote {REPORT_PATH} with {len(final)} candidates.")


if __name__ == "__main__":
    main()

"""
Script 01: Clean Research Population Builder
--------------------------------------------
Processes raw BoardGameGeek data (data/raw/bgg_games_current.parquet) to construct
a clean, reproducible research population stored in data/processed/bgg_research_population.parquet.

Population criteria:
1. Valid Unique game_id (deduplication / drop missing IDs)
2. Non-expansions (filtering boardgame expansions by link, category, expands_name, and flag)
   - Standalone reimplementations are explicitly retained.
3. Published games from 1950 onwards (excluding unreleased prototypes, meta-entries, year=0/null, and pre-1950 releases)
4. Non-future games (published <= 2026)
5. Minimum rating count threshold (users_rated >= 100)
6. Latin-script titles only (excluding non-Latin scripts such as Cyrillic, CJK, Hangul, Kana; foreign Latin titles like 'Die Macher' are retained)
7. Structural exclusion of primarily Print & Play and Self-Published / POD / DTP games:
   - Excludes explicit POD / DTP / Game Crafter tags
   - Excludes games tagged with Print & Play that lack physical commercial product metadata (containers, components, publisher series, magazines, or commercial crowdfunding)
"""

import sys
import re
import json
import unicodedata
from pathlib import Path
import pandas as pd
import numpy as np

# Set paths
REPO_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = REPO_DIR / "data" / "raw" / "bgg_games_current.parquet"
PROCESSED_DATA_PATH = REPO_DIR / "data" / "processed" / "bgg_research_population.parquet"
PROCESSED_DATA_DIR = REPO_DIR / "data" / "processed"


def clean_title(title: str) -> str:
    """
    Cleans browse-scrape artifacts from BGG titles.
    BGG browse scrapes occasionally concatenate '<title>   (<year>)      <short description>'.
    Splits on 4+ spaces, tabs, or 2+ spaces followed by an ancient BCE/CE year in parens.
    Preserves valid double spaces in titles like 'Axis & Allies:  Guadalcanal'.
    """
    if not isinstance(title, str):
        return ""
    cleaned = re.split(r'\s{4,}|\t|\s{2,}(?=\(-?\d{1,4}\))', title)[0].strip()
    return cleaned


def has_non_latin_script(title: str) -> bool:
    """
    Identifies whether a title contains characters from non-Latin scripts
    (e.g., CJK, Cyrillic, Hangul, Kana, Arabic, Thai, Greek, Hebrew),
    while ignoring common punctuation, symbols (e.g. hearts, superscripts),
    spaces, and Latin diacritics/accents.
    """
    if not isinstance(title, str):
        return False
    for c in title:
        if c.isascii() or c.isspace():
            continue
        cat = unicodedata.category(c)
        if cat.startswith('P') or cat.startswith('S') or cat.startswith('Z') or cat.startswith('N'):
            continue
        name = unicodedata.name(c, '')
        if 'LATIN' not in name:
            return True
    return False


def is_primarily_pnp_or_self_published(categories_str: str, families_str: str) -> bool:
    """
    Identifies games whose primary product/distribution model is Print & Play,
    Print-on-Demand (POD), Desktop Publishing (DTP), or Self-Published,
    while retaining physical commercial releases that merely carry a promotional PnP tag.
    """
    cats_str = categories_str if isinstance(categories_str, str) else ""
    fams_str = families_str if isinstance(families_str, str) else ""
    
    fams_list = []
    if fams_str.startswith("["):
        try:
            fams_list = json.loads(fams_str)
        except Exception:
            fams_list = []
    fams_lower = [f.lower() for f in fams_list]

    # 1. Explicit POD / DTP / Game Crafter flags -> ALWAYS EXCLUDE
    is_pod_dtp = any(k in fams_lower for k in [
        "category: print-on-demand",
        "components: dtp (desktop publishing)",
        "crowdfunding: game crafter crowd sale"
    ])
    if is_pod_dtp:
        return True

    # 2. Check if tagged with Print & Play
    has_pnp_tag = (
        "print & play" in cats_str.lower() or
        "print and play" in cats_str.lower() or
        any(f.startswith("contests:") and "pnp" in f for f in fams_lower) or
        any(f.startswith("contests:") and "print & play" in f for f in fams_lower)
    )
    if not has_pnp_tag:
        return False

    # 3. Disambiguate PnP using physical commercial metadata
    has_containers = any(f.startswith("containers:") for f in fams_lower)
    has_physical_components = any(
        f.startswith("components:") and not any(k in f for k in ["dtp", "print & play", "traditional playing cards", "paper", "calendars"])
        for f in fams_lower
    )
    has_commercial_series = any(
        f.startswith("series:") and not any(k in f for k in ["pnp", "free pnp", "contest", "print and play"])
        for f in fams_lower
    )
    has_magazine = any(f.startswith("magazine:") for f in fams_lower)
    has_commercial_crowdfunding = any(
        f.startswith("crowdfunding:") and "game crafter" not in f
        for f in fams_lower
    )

    is_physical_commercial = (
        has_containers or
        has_physical_components or
        has_commercial_series or
        has_magazine or
        has_commercial_crowdfunding
    )

    # Exclude only if tagged PnP and lacking all physical commercial metadata
    return not is_physical_commercial


def main():
    print(f"Loading raw BGG data from: {RAW_DATA_PATH}")
    if not RAW_DATA_PATH.exists():
        print(f"Error: Raw data file not found at {RAW_DATA_PATH}")
        sys.exit(1)

    raw_df = pd.read_parquet(RAW_DATA_PATH)
    n_raw = len(raw_df)
    print(f"Loaded raw dataset with {n_raw:,} rows and {raw_df.shape[1]} columns.\n")

    # Step-by-step audit and filtering
    print("=" * 65)
    print("STEP-BY-STEP FILTERING WATERFALL AUDIT")
    print("=" * 65)

    # 1. game_id audit & dedup
    null_gid = raw_df['game_id'].isna()
    dup_gid = raw_df['game_id'].duplicated(keep=False) & ~null_gid
    print(f"[Step 1] Unique valid game_id:")
    print(f"  - Missing game_id: {null_gid.sum():,} rows ({null_gid.mean():.2%})")
    print(f"  - Duplicate non-null game_id: {dup_gid.sum():,} rows")
    df_step1 = raw_df[~null_gid].copy()
    df_step1['game_id'] = df_step1['game_id'].astype(int)

    # 2. Expansion identification (retaining reimplementations)
    c_link_exp = df_step1['link'].str.startswith('/boardgameexpansion/')
    c_flag_exp = df_step1['is_expansion'] == True
    c_cat_exp = df_step1['categories'].fillna('').str.contains('Expansion for Base-game')
    c_expands_name = df_step1['expands_name'].notna()
    all_exp = c_link_exp | c_flag_exp | c_cat_exp | c_expands_name

    print(f"\n[Step 2] Non-expansions filter (standalone games & reimplementations retained):")
    print(f"  - Total expansions excluded: {all_exp.sum():,} ({all_exp.mean():.2%})")
    df_step2 = df_step1[~all_exp].copy()
    print(f"  - Remaining base/standalone games: {len(df_step2):,}")

    # 3. Publication Year filter (1950 <= year <= 2026, published, non-meta)
    meta_game_ids = {18291, 23953, 5985} # Unpublished Prototype, Outside BGG Scope, Game Accessory
    meta_mask = df_step2['game_id'].isin(meta_game_ids)
    year_null = df_step2['year'].isna()
    year_zero = df_step2['year'] == 0
    year_valid_mask = (df_step2['year'] >= 1950) & (df_step2['year'] <= 2026) & ~meta_mask & ~year_zero & ~year_null
    df_step3 = df_step2[year_valid_mask].copy()
    print(f"\n[Step 3] Publication Status & Year Range (1950 - 2026):")
    print(f"  - Dropped pre-1950, unreleased (year=0/null), meta, and future: {len(df_step2) - len(df_step3):,}")
    print(f"  - Remaining games published 1950-2026: {len(df_step3):,}")

    # 4. Rating count threshold (users_rated >= 100)
    rc_keep = df_step3['users_rated'].fillna(0) >= 100
    df_step4 = df_step3[rc_keep].copy()
    print(f"\n[Step 4] Minimum rating-count threshold (users_rated >= 100):")
    print(f"  - Excluded games with <100 ratings: {len(df_step3) - len(df_step4):,}")
    print(f"  - Remaining games with >= 100 ratings: {len(df_step4):,}")

    # 5. Title cleaning and Latin script filter
    df_step4['title_clean'] = df_step4['title'].apply(clean_title)
    df_step4['has_non_latin_script'] = df_step4['title_clean'].apply(has_non_latin_script)
    non_latin_cnt = df_step4['has_non_latin_script'].sum()
    df_step5 = df_step4[~df_step4['has_non_latin_script']].copy()
    print(f"\n[Step 5] Script filtering (Latin scripts only):")
    print(f"  - Non-Latin script titles excluded: {non_latin_cnt:,}")
    print(f"  - Remaining games with Latin script titles: {len(df_step5):,}")

    # 6. Structural PnP and Self-Published / POD exclusions
    pnp_pod_mask = df_step5.apply(lambda r: is_primarily_pnp_or_self_published(r['categories'], r['families']), axis=1)
    print(f"\n[Step 6] Structural PnP & Self-Published / POD exclusion:")
    print(f"  - Primarily PnP or POD/DTP excluded: {pnp_pod_mask.sum():,}")
    df_step6 = df_step5[~pnp_pod_mask].copy()
    print(f"  - Remaining qualified research population: {len(df_step6):,}")

    # Final population
    pop_df = df_step6.sort_values('users_rated', ascending=False).reset_index(drop=True)

    print("\n" + "=" * 65)
    print("FINAL RESEARCH POPULATION SUMMARY")
    print("=" * 65)
    print(f"Total games in research population: {len(pop_df):,}")
    print(f"Year range: {int(pop_df['year'].min())} to {int(pop_df['year'].max())}")
    print(f"Users rated range: {int(pop_df['users_rated'].min()):,} to {int(pop_df['users_rated'].max()):,}")
    print(f"Average rating range: {pop_df['avg_rating_current'].min():.2f} to {pop_df['avg_rating_current'].max():.2f}")
    print(f"Bayesian Geek rating range: {pop_df['bayes_rating'].min():.2f} to {pop_df['bayes_rating'].max():.2f}")
    print(f"Weight range: {pop_df['weight'].min():.2f} to {pop_df['weight'].max():.2f} (null weights: {pop_df['weight'].isna().sum()})")
    print(f"Standalone reimplementations: {pop_df['is_reimplementation'].sum():,}")

    # Save output
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    pop_df.to_parquet(PROCESSED_DATA_PATH, index=False)
    print(f"\nSaved processed population dataset to: {PROCESSED_DATA_PATH}")

    # Sequential impact summary table
    print("\n" + "=" * 65)
    print("SEQUENTIAL FILTER IMPACT TABLE")
    print("=" * 65)
    seq_table = [
        {"Step": "0. Raw Dataset", "Excluded at Step": 0, "Retained Records": n_raw},
        {"Step": "1. Valid game_id", "Excluded at Step": null_gid.sum(), "Retained Records": len(df_step1)},
        {"Step": "2. Non-expansions", "Excluded at Step": all_exp.sum(), "Retained Records": len(df_step2)},
        {"Step": "3. Published 1950-2026", "Excluded at Step": len(df_step2) - len(df_step3), "Retained Records": len(df_step3)},
        {"Step": "4. Rating count floor (users_rated >= 100)", "Excluded at Step": len(df_step3) - len(df_step4), "Retained Records": len(df_step4)},
        {"Step": "5. Latin script titles only", "Excluded at Step": non_latin_cnt, "Retained Records": len(df_step5)},
        {"Step": "6. Structural PnP / Self-Pub / POD", "Excluded at Step": pnp_pod_mask.sum(), "Retained Records": len(pop_df)},
    ]
    summary_df = pd.DataFrame(seq_table)
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()

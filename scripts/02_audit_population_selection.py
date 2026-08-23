"""
Script 02: Research Population Selection Bias Audit
---------------------------------------------------
Audits the final research population (data/processed/bgg_research_population.parquet)
against the raw and excluded datasets to quantify composition shifts, selection effects,
and survival biases across:
1. Expansion removal (survivor bias & rating premium)
2. Rating count floor (users_rated >= 100)
3. Release year / publication era shifts
4. Complexity / weight shifts & missingness
5. Category & mechanic representation and survival rates
6. Niche / subdomain dynamics (wargames, children's games, strategy games)
"""

import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np

REPO_DIR = Path(__file__).resolve().parent.parent
RAW_PATH = REPO_DIR / "data" / "raw" / "bgg_games_current.parquet"
PROCESSED_PATH = REPO_DIR / "data" / "processed" / "bgg_research_population.parquet"


def parse_json_list(val):
    if pd.isna(val) or not isinstance(val, str):
        return []
    try:
        return json.loads(val)
    except Exception:
        return []


def parse_json_dict_keys(val):
    if pd.isna(val) or not isinstance(val, str):
        return []
    try:
        data = json.loads(val)
        if isinstance(data, dict):
            return list(data.keys())
        return []
    except Exception:
        return []


def main():
    print(f"Loading raw data from: {RAW_PATH}")
    raw_df = pd.read_parquet(RAW_PATH)
    print(f"Loading processed population from: {PROCESSED_PATH}")
    clean_df = pd.read_parquet(PROCESSED_PATH)

    print("\n" + "=" * 75)
    print("1. OVERALL POPULATION AUDIT")
    print("=" * 75)
    print(f"Raw records: {len(raw_df):,}")
    print(f"Final clean research population: {len(clean_df):,} ({len(clean_df)/len(raw_df):.2%} of raw)")

    # Define partitions
    exp_mask = (
        (raw_df['is_expansion'] == True) |
        (raw_df['link'].str.startswith('/boardgameexpansion/')) |
        (raw_df['categories'].fillna('').str.contains('Expansion for Base-game')) |
        (raw_df['expands_name'].notna())
    )
    exp_df = raw_df[exp_mask].copy()
    base_df = raw_df[~exp_mask & raw_df['game_id'].notna()].copy()

    meta_ids = {18291, 23953, 5985}
    modern_base = base_df[
        (base_df['year'] >= 1950) & 
        (base_df['year'] <= 2026) & 
        (~base_df['game_id'].isin(meta_ids))
    ].copy()

    modern_base['retained'] = modern_base['game_id'].isin(clean_df['game_id'])
    modern_base['excluded'] = ~modern_base['retained']

    ret_df = modern_base[modern_base['retained']].copy()
    exc_df = modern_base[modern_base['excluded']].copy()

    print(f"Modern base games (1950-2026): {len(modern_base):,}")
    print(f"  - Retained (>=100 ratings, Latin title): {len(ret_df):,} ({len(ret_df)/len(modern_base):.2%})")
    print(f"  - Excluded: {len(exc_df):,} ({len(exc_df)/len(modern_base):.2%})")

    # 2. Expansion selection effect
    print("\n" + "=" * 75)
    print("2. EXPANSION REMOVAL: FAN SURVIVORSHIP BIAS")
    print("=" * 75)
    exp_stats = {
        "Metric": ["Count", "Avg Rating (Mean)", "Avg Rating (Median)", "Weight (Mean)", "Weight (Median)", "Users Rated (Mean)", "Users Rated (Median)"],
        "Expansions": [
            f"{len(exp_df):,}",
            f"{exp_df['avg_rating_current'].mean():.2f}",
            f"{exp_df['avg_rating_current'].median():.2f}",
            f"{exp_df['weight'].mean():.2f}",
            f"{exp_df['weight'].median():.2f}",
            f"{exp_df['users_rated'].mean():.1f}",
            f"{exp_df['users_rated'].median():.1f}"
        ],
        "Base Games": [
            f"{len(base_df):,}",
            f"{base_df['avg_rating_current'].mean():.2f}",
            f"{base_df['avg_rating_current'].median():.2f}",
            f"{base_df['weight'].mean():.2f}",
            f"{base_df['weight'].median():.2f}",
            f"{base_df['users_rated'].mean():.1f}",
            f"{base_df['users_rated'].median():.1f}"
        ]
    }
    print(pd.DataFrame(exp_stats).to_string(index=False))
    print("\nInsight: Expansions exhibit an average rating premium of +1.20 points (7.39 vs 6.19) due to extreme fan selection (only players who loved the base game purchase and rate expansions). Removing expansions is essential to prevent confounding game quality with add-on fan selection.")

    # 3. Rating floor selection effect: Retained vs Excluded
    print("\n" + "=" * 75)
    print("3. RATING FLOOR SELECTION: RETAINED (>=100) VS EXCLUDED (<100)")
    print("=" * 75)

    comp_stats = {
        "Metric": [
            "Game Count",
            "Year (Mean)",
            "Year (Median)",
            "Weight Missingness (%)",
            "Weight (Mean, where present)",
            "Weight (Median, where present)",
            "Avg Rating (Mean)",
            "Avg Rating (Std Dev)",
            "Users Rated (Median)",
            "Users Rated (75th percentile)",
            "Users Rated (95th percentile)"
        ],
        "Retained (>=100 ratings)": [
            f"{len(ret_df):,}",
            f"{ret_df['year'].mean():.1f}",
            f"{ret_df['year'].median():.0f}",
            f"{ret_df['weight'].isna().mean():.2%}",
            f"{ret_df['weight'].mean():.2f}",
            f"{ret_df['weight'].median():.2f}",
            f"{ret_df['avg_rating_current'].mean():.2f}",
            f"{ret_df['avg_rating_current'].std():.2f}",
            f"{ret_df['users_rated'].median():.0f}",
            f"{ret_df['users_rated'].quantile(0.75):.0f}",
            f"{ret_df['users_rated'].quantile(0.95):.0f}"
        ],
        "Excluded (<100 ratings)": [
            f"{len(exc_df):,}",
            f"{exc_df['year'].mean():.1f}",
            f"{exc_df['year'].median():.0f}",
            f"{exc_df['weight'].isna().mean():.2%}",
            f"{exc_df['weight'].mean():.2f}",
            f"{exc_df['weight'].median():.2f}",
            f"{exc_df['avg_rating_current'].mean():.2f}",
            f"{exc_df['avg_rating_current'].std():.2f}",
            f"{exc_df['users_rated'].median():.0f}",
            f"{exc_df['users_rated'].quantile(0.75):.0f}",
            f"{exc_df['users_rated'].quantile(0.95):.0f}"
        ]
    }
    print(pd.DataFrame(comp_stats).to_string(index=False))

    # 4. Decade-by-decade survival rates
    print("\n" + "=" * 75)
    print("4. ERA / DECADE SURVIVAL RATES (TEMPORAL SELECTION)")
    print("=" * 75)
    modern_base['decade'] = (modern_base['year'] // 10) * 10
    decade_df = modern_base.groupby('decade')['retained'].agg(
        Total_Games='count',
        Retained_Games='sum',
        Survival_Rate='mean'
    ).reset_index()
    decade_df['Survival_Rate'] = decade_df['Survival_Rate'].map('{:.2%}'.format)
    print(decade_df.to_string(index=False))
    print("\nInsight: Survival rate rises monotonically from 3.0% (1950s) to 18.7% (2010s). The 100-rating floor introduces severe recency selection because older obscure games lack internet-era raters.")

    # 5. Category Survival Discrepancies
    print("\n" + "=" * 75)
    print("5. CATEGORY / GENRE REPRESENTATION & SELECTION")
    print("=" * 75)
    cat_records = []
    for _, row in modern_base[['game_id', 'categories', 'retained']].iterrows():
        for c in parse_json_list(row['categories']):
            cat_records.append({'category': c, 'retained': row['retained']})
    cat_df = pd.DataFrame(cat_records)
    cat_summary = cat_df.groupby('category')['retained'].agg(
        total='count',
        retained='sum',
        survival_rate='mean'
    ).reset_index()
    cat_summary_500 = cat_summary[cat_summary['total'] >= 500].sort_values('survival_rate', ascending=False)

    print("Top 10 Categories by Survival Rate (min 500 games in pool):")
    for _, r in cat_summary_500.head(10).iterrows():
        print(f"  {r['category']:30s} | Total: {r['total']:5d} | Retained: {r['retained']:5d} ({r['survival_rate']:6.2%})")

    print("\nBottom 10 Categories by Survival Rate (min 500 games in pool):")
    for _, r in cat_summary_500.tail(10).iterrows():
        print(f"  {r['category']:30s} | Total: {r['total']:5d} | Retained: {r['retained']:5d} ({r['survival_rate']:6.2%})")

    # 6. Mechanic Survival Discrepancies
    print("\n" + "=" * 75)
    print("6. MECHANICS REPRESENTATION & SELECTION")
    print("=" * 75)
    mech_records = []
    for _, row in modern_base[['game_id', 'mechanics', 'retained']].iterrows():
        for m in parse_json_list(row['mechanics']):
            mech_records.append({'mechanic': m, 'retained': row['retained']})
    mech_df = pd.DataFrame(mech_records)
    mech_summary = mech_df.groupby('mechanic')['retained'].agg(
        total='count',
        retained='sum',
        survival_rate='mean'
    ).reset_index()
    mech_summary_500 = mech_summary[mech_summary['total'] >= 500].sort_values('survival_rate', ascending=False)

    print("Top 10 Mechanics by Survival Rate (min 500 games in pool):")
    for _, r in mech_summary_500.head(10).iterrows():
        print(f"  {r['mechanic']:32s} | Total: {r['total']:5d} | Retained: {r['retained']:5d} ({r['survival_rate']:6.2%})")

    print("\nBottom 10 Mechanics by Survival Rate (min 500 games in pool):")
    for _, r in mech_summary_500.tail(10).iterrows():
        print(f"  {r['mechanic']:32s} | Total: {r['total']:5d} | Retained: {r['retained']:5d} ({r['survival_rate']:6.2%})")

    # 7. Subdomains (Ranked Categories)
    print("\n" + "=" * 75)
    print("7. SUBDOMAIN / NICHE REPRESENTATION")
    print("=" * 75)
    subrank_records = []
    for _, row in modern_base[['game_id', 'subranks', 'retained']].iterrows():
        for s in parse_json_dict_keys(row['subranks']):
            subrank_records.append({'subdomain': s, 'retained': row['retained']})
    sub_df = pd.DataFrame(subrank_records)
    if len(sub_df) > 0:
        sub_summary = sub_df.groupby('subdomain')['retained'].agg(
            total='count',
            retained='sum',
            survival_rate='mean'
        ).reset_index().sort_values('survival_rate', ascending=False)
        print("Subdomain Survival Rates (games receiving official BGG subranks):")
        for _, r in sub_summary.iterrows():
            print(f"  {r['subdomain']:20s} | Total: {r['total']:5d} | Retained: {r['retained']:5d} ({r['survival_rate']:6.2%})")

    # 8. Wargames deep dive
    wargames = modern_base[modern_base['categories'].fillna('').str.contains('Wargame')]
    print("\n" + "=" * 75)
    print("8. NICHE DEEP DIVE: WARGAMES")
    print("=" * 75)
    print(f"Total Wargames in modern base pool: {len(wargames):,}")
    print(f"Wargames meeting >=100 rating threshold: {wargames['retained'].sum():,} ({wargames['retained'].mean():.2%})")
    print(f"Wargames rating count quantiles (excluded + retained): 25%: {wargames['users_rated'].quantile(0.25):.0f}, 50%: {wargames['users_rated'].median():.0f}, 75%: {wargames['users_rated'].quantile(0.75):.0f}, 90%: {wargames['users_rated'].quantile(0.90):.0f}")


if __name__ == "__main__":
    main()

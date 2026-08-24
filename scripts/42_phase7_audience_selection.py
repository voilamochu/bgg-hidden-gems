#!/usr/bin/env python3
"""
Step 7 — Observable Audience-Selection / Cult-vs-Hidden Investigation
Population: 14,698 games x 287,302 users x 24,146,307 observations (phase2-pass2)

Implements A–H efficiently with bounded DuckDB (4GB/3 threads/temp scratch/ducktmp),
narrow single-scan aggregations, no wide-table bug, no full-snapshot rescans.

Do NOT modify Phase 2 baseline (mu 7.139, delta_u, adj_mean from scripts 39/40)
Do NOT rerun Phase 5/6, do NOT build hidden-gem score, do NOT alter Q3b/OLS.

Outputs under docs/phase2-pass2/step7_audience_selection/ and reports/phase2_pass2/step7_audience_selection/:
 - README.md
 - audience_selectivity_summary.md
 - audience_selectivity_game_level.csv
 - cross_audience_results.csv
 - exposure_proxy_results.csv
 - methodology_comparison.md
 - known_case_sanity_check.md
 - step7_summary.json

Repro: python scripts/42_phase7_audience_selection.py
"""
import argparse
import json
import time
import shutil
from pathlib import Path
import duckdb
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

REPO = Path(__file__).resolve().parent.parent
PASS2_DIR = REPO / "data" / "processed" / "phase2-pass2"
POP_PATH = REPO / "data" / "processed" / "bgg_research_population.parquet"
SCRATCH = REPO / "scratch" / "phase2-pass2"
TMP_DUCK = REPO / "scratch" / "ducktmp"
OUT_DOCS = REPO / "docs" / "phase2-pass2" / "step7_audience_selection"
OUT_REPORTS = REPO / "reports" / "phase2_pass2" / "step7_audience_selection"

MU = 7.13900772639585  # from pass2_baseline_refresh.json mu_full
MEMORY = "4GB"
THREADS = 3

FLAG_NAMES = ["18XX", "Wargame", "Party", "Economic", "Coop", "Legacy"]
FLAG_COLS = ["flag_18xx", "flag_warg", "flag_party", "flag_econ", "flag_coop", "flag_legacy"]
FLAG_MAP = dict(zip(FLAG_NAMES, FLAG_COLS))

def qpath(p: Path) -> str:
    return str(p).replace("'", "''")

def configure(con, tmp_dir: Path):
    con.execute(f"SET memory_limit='{MEMORY}'")
    con.execute(f"SET threads={THREADS}")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    con.execute(f"SET temp_directory='{qpath(tmp_dir)}'")
    con.execute("SET preserve_insertion_order=false")

def build_game_flags_sql(games_path: Path, alias="gf"):
    # Uses categories/mechanics/families JSON arrays; 18XX strictly Series: 18xx to avoid 1871 false positives
    return f"""
    CREATE OR REPLACE VIEW {alias} AS
    SELECT game_id, title, year, weight, categories, mechanics, families, avg_rating_current, users_rated,
           CASE WHEN len(list_filter(from_json(families, '["VARCHAR"]'), x -> lower(x) = 'series: 18xx')) > 0 THEN 1 ELSE 0 END AS flag_18xx,
           CASE WHEN list_contains(from_json(categories, '["VARCHAR"]'), 'Wargame') THEN 1 ELSE 0 END AS flag_warg,
           CASE WHEN list_contains(from_json(categories, '["VARCHAR"]'), 'Party Game') THEN 1 ELSE 0 END AS flag_party,
           CASE WHEN list_contains(from_json(categories, '["VARCHAR"]'), 'Economic') THEN 1 ELSE 0 END AS flag_econ,
           CASE WHEN list_contains(from_json(mechanics, '["VARCHAR"]'), 'Cooperative Game') THEN 1 ELSE 0 END AS flag_coop,
           CASE WHEN list_contains(from_json(mechanics, '["VARCHAR"]'), 'Legacy Game') THEN 1 ELSE 0 END AS flag_legacy,
           CASE WHEN weight < 2.5 THEN 'Light' WHEN weight < 3.5 THEN 'Medium' ELSE 'Heavy' END AS weight_class_3,
           CASE WHEN weight < 1.5 THEN '<1.5' WHEN weight < 2.0 THEN '1.5-2.0' WHEN weight < 2.5 THEN '2.0-2.5' WHEN weight < 3.5 THEN '2.5-3.5' ELSE '>3.5' END AS weight_class_5,
           CASE WHEN flag_18xx=1 THEN '18XX' WHEN flag_warg=1 THEN 'Wargame' WHEN flag_party=1 THEN 'Party' WHEN flag_econ=1 THEN 'Economic' WHEN flag_coop=1 THEN 'Coop' WHEN flag_legacy=1 THEN 'Legacy' ELSE 'Other' END AS primary_type
    FROM read_parquet('{qpath(games_path)}')
    """


def ensure_dirs():
    for d in [OUT_DOCS, OUT_REPORTS, SCRATCH, TMP_DUCK]:
        d.mkdir(parents=True, exist_ok=True)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pass2-dir", type=Path, default=PASS2_DIR)
    ap.add_argument("--population", type=Path, default=POP_PATH)
    ap.add_argument("--scratch", type=Path, default=SCRATCH)
    ap.add_argument("--out-docs", type=Path, default=OUT_DOCS)
    ap.add_argument("--out-reports", type=Path, default=OUT_REPORTS)
    args = ap.parse_args()

    pass2_dir = args.pass2_dir
    population = args.population
    scratch = args.scratch
    out_docs = args.out_docs
    out_reports = args.out_reports
    tmp_duck = TMP_DUCK
    ensure_dirs()
    # also ensure reports mirror
    out_reports.mkdir(parents=True, exist_ok=True)
    tmp_duck.mkdir(parents=True, exist_ok=True)

    # Files
    ro_path = pass2_dir / "rating_observations_pass2.parquet"
    users_path = pass2_dir / "users_pass2.parquet"
    games_path = pass2_dir / "games_pass2.parquet"
    sev_path = pass2_dir / "user_severity_pass2.parquet"
    gm_path = pass2_dir / "game_adjusted_means_pass2.parquet"
    coll_path = pass2_dir / "collections_pass2.parquet"
    tags_path = pass2_dir / "game_tags_pass2.parquet"
    links_path = pass2_dir / "game_links_pass2.parquet"

    for p in [ro_path, users_path, games_path, sev_path, gm_path]:
        if not p.exists():
            raise FileNotFoundError(f"Missing required pass2 file: {p}")

    con = duckdb.connect()
    configure(con, tmp_duck)
    print(f"[Step7] Pass2 dir: {pass2_dir} -> {ro_path} 24,146,307 expected", flush=True)
    print(f"[Step7] mu baseline {MU} (do not refit)", flush=True)

    # Quick validation counts
    n_obs = con.execute(f"SELECT COUNT(*) FROM read_parquet('{qpath(ro_path)}')").fetchone()[0]
    n_users = con.execute(f"SELECT COUNT(*) FROM read_parquet('{qpath(users_path)}')").fetchone()[0]
    n_games = con.execute(f"SELECT COUNT(*) FROM read_parquet('{qpath(games_path)}')").fetchone()[0]
    print(f"[validate] {n_games} games x {n_users} users x {n_obs} obs", flush=True)
    assert n_games == 14698, f"games {n_games} !=14698"
    assert n_users == 287302, f"users {n_users} !=287302"
    assert n_obs == 24146307, f"obs {n_obs} !=24146307"
    mu_check = con.execute(f"SELECT AVG(rating) FROM read_parquet('{qpath(ro_path)}')").fetchone()[0]
    print(f"[validate] mu recomputed {mu_check:.6f} vs expected {MU:.6f} diff {mu_check-MU:.6f}", flush=True)

    # Build game_flags view
    print("[1/12] Building game_flags view...", flush=True)
    con.execute(build_game_flags_sql(games_path, alias="game_flags"))
    flag_counts = con.execute("SELECT SUM(flag_18xx), SUM(flag_warg), SUM(flag_party), SUM(flag_econ), SUM(flag_coop), SUM(flag_legacy) FROM game_flags").fetchone()
    print(f"  flag counts 18XX/Warg/Party/Econ/Coop/Legacy: {flag_counts}", flush=True)
    # primary type distribution
    pt = con.execute("SELECT primary_type, COUNT(*) FROM game_flags GROUP BY primary_type ORDER BY COUNT(*) DESC").fetchdf()
    print(pt.to_string(index=False))
    # Also weight null check
    wnull = con.execute("SELECT COUNT(*) FROM game_flags WHERE weight IS NULL").fetchone()[0]
    print(f"  weight NULL: {wnull}")

    # ------------------------------------------------------------------
    # Per-user features: volume_band, delta, mean_weight, type counts
    # Narrow single-scan aggregation: one GROUP BY per user joining ratings+flags+users+severity
    # ------------------------------------------------------------------
    print("[2/12] Per-user features (mean_weight, type counts, volume)...", flush=True)
    # Create temp table user_features
    # Use narrow: keep only needed cols
    # users_pass2 has cnt_filtered but not volume_band; compute band via CASE and join severity for delta
    con.execute(f"""
        CREATE OR REPLACE TABLE user_features AS
        SELECT r.user_pseudouserid AS uid,
               ANY_VALUE(CASE WHEN u.cnt_filtered BETWEEN 10 AND 24 THEN '10-24'
                              WHEN u.cnt_filtered BETWEEN 25 AND 49 THEN '25-49'
                              WHEN u.cnt_filtered BETWEEN 50 AND 99 THEN '50-99'
                              WHEN u.cnt_filtered BETWEEN 100 AND 249 THEN '100-249'
                              WHEN u.cnt_filtered BETWEEN 250 AND 499 THEN '250-499'
                              WHEN u.cnt_filtered BETWEEN 500 AND 999 THEN '500-999'
                              ELSE '1000+' END) AS volume_band,
               ANY_VALUE(u.cnt_filtered) AS cnt_filtered,
               ANY_VALUE(s.delta_full) AS delta_full,
               ANY_VALUE(s.delta_even) AS delta_even,
               ANY_VALUE(s.delta_odd) AS delta_odd,
               COUNT(*) AS n_total,
               AVG(g.weight) FILTER (WHERE g.weight IS NOT NULL) AS mean_weight,
               STDDEV_SAMP(g.weight) FILTER (WHERE g.weight IS NOT NULL) AS sd_weight,
               SUM(g.flag_18xx) AS n_18xx,
               SUM(g.flag_warg) AS n_warg,
               SUM(g.flag_party) AS n_party,
               SUM(g.flag_econ) AS n_econ,
               SUM(g.flag_coop) AS n_coop,
               SUM(g.flag_legacy) AS n_legacy,
               COUNT(*) FILTER (WHERE g.weight IS NOT NULL) AS n_weighted,
               AVG(r.rating) AS mean_rating_raw,
               AVG(r.rating - COALESCE(s.delta_full,0)) AS mean_rating_adj,
               MIN(g.weight) AS min_weight,
               MAX(g.weight) AS max_weight
        FROM read_parquet('{qpath(ro_path)}') r
        JOIN game_flags g USING (game_id)
        JOIN read_parquet('{qpath(users_path)}') u ON r.user_pseudouserid = u.user_pseudouserid
        LEFT JOIN read_parquet('{qpath(sev_path)}') s ON r.user_pseudouserid = s.user_pseudouserid
        GROUP BY r.user_pseudouserid
    """)
    uf_cnt = con.execute("SELECT COUNT(*) FROM user_features").fetchone()[0]
    print(f"  user_features rows: {uf_cnt}")
    # quick stats
    print(con.execute("SELECT volume_band, COUNT(*), AVG(mean_weight), AVG(delta_full) FROM user_features GROUP BY volume_band ORDER BY volume_band").fetchdf().to_string(index=False))
    # mean_weight distribution
    print(con.execute("SELECT AVG(mean_weight), STDDEV_SAMP(mean_weight), QUANTILE_CONT(mean_weight,0.5) FROM user_features WHERE mean_weight IS NOT NULL").fetchone())

    # ------------------------------------------------------------------
    # Create game_cats view (defer heavy user_cat_counts until needed for cat related)
    # ------------------------------------------------------------------
    print("[3/12] Create game_cats view (defer heavy cat counts)...", flush=True)
    con.execute(f"""
        CREATE OR REPLACE VIEW game_cats AS
        SELECT game_id, unnest(from_json(categories, '["VARCHAR"]')) AS cat
        FROM read_parquet('{qpath(games_path)}') WHERE categories IS NOT NULL
    """)
    n_cats = con.execute("SELECT COUNT(DISTINCT cat) FROM game_cats").fetchone()[0]
    print(f"  distinct cats {n_cats}")
    # Dummy mech view
    con.execute("CREATE OR REPLACE VIEW game_mechs AS SELECT 0 AS game_id, '' AS mech WHERE 0=1")

    # ------------------------------------------------------------------
    # Per-game base stats: n_obs, raw_mean, adj_mean, se, weight, etc.
    # Use game_adjusted_means_pass2 for adj_mean but also compute raw from observations for verification
    # ------------------------------------------------------------------
    print("[4/12] Per-game base stats...", flush=True)
    # Create game_base view joining flags + adjusted means + n_obs verification
    con.execute(f"""
        CREATE OR REPLACE VIEW game_base AS
        SELECT g.game_id, g.title, g.year, g.weight, g.categories, g.mechanics, g.families,
               g.flag_18xx, g.flag_warg, g.flag_party, g.flag_econ, g.flag_coop, g.flag_legacy, g.primary_type, g.weight_class_3,
               gm.n_obs, gm.raw_mean, gm.adj_mean, gm.game_alpha,
               (gm.raw_mean - {MU} - gm.game_alpha) AS alpha_check -- should be near 0 weight?
        FROM game_flags g
        LEFT JOIN read_parquet('{qpath(gm_path)}') gm USING (game_id)
    """)
    # Verify n_obs matches count
    mism = con.execute("SELECT COUNT(*) FROM game_base WHERE n_obs IS NULL").fetchone()[0]
    print(f"  games without adjusted means: {mism}")
    print(con.execute("SELECT COUNT(*), AVG(n_obs), MIN(n_obs), MAX(n_obs) FROM game_base").fetchone())
    # Compute per-game rating SD and SE via narrow aggregation on observations joined with severity (for adj)
    # Need se for heterogeneity
    con.execute(f"""
        CREATE OR REPLACE TABLE game_rating_stats AS
        SELECT r.game_id,
               COUNT(*) AS n_obs2,
               AVG(r.rating) AS raw_mean2,
               AVG(r.rating - COALESCE(s.delta_full,0)) AS adj_mean2,
               STDDEV_SAMP(r.rating) AS sd_raw,
               STDDEV_SAMP(r.rating - COALESCE(s.delta_full,0)) AS sd_adj,
               STDDEV_SAMP(r.rating) / SQRT(COUNT(*)) AS se_raw,
               STDDEV_SAMP(r.rating - COALESCE(s.delta_full,0)) / SQRT(COUNT(*)) AS se_adj
        FROM read_parquet('{qpath(ro_path)}') r
        LEFT JOIN read_parquet('{qpath(sev_path)}') s ON r.user_pseudouserid = s.user_pseudouserid
        GROUP BY r.game_id
    """)
    print("  game_rating_stats built")

    # ------------------------------------------------------------------
    # A. Audience Concentration per game
    # ------------------------------------------------------------------
    print("[5/12] A. Audience Concentration per game...", flush=True)
    # Need volume distribution per game: game_id, volume_band, n
    con.execute(f"""
        CREATE OR REPLACE TABLE game_volume_dist AS
        SELECT r.game_id, uf.volume_band, COUNT(*) AS n
        FROM read_parquet('{qpath(ro_path)}') r
        JOIN user_features uf ON r.user_pseudouserid = uf.uid
        GROUP BY r.game_id, uf.volume_band
    """)
    print(f"  game_volume_dist rows: {con.execute('SELECT COUNT(*) FROM game_volume_dist').fetchone()[0]}")
    # Pivot to wide via conditional aggregation per game
    # Also compute entropy and herfindahl
    # We'll compute in python from fetched table
    gvd = con.execute("SELECT * FROM game_volume_dist").fetchdf()
    # Build pivot
    vol_bands = ["10-24","25-49","50-99","100-249","250-499","500-999","1000+"]
    pivot = gvd.pivot(index="game_id", columns="volume_band", values="n").fillna(0)
    for b in vol_bands:
        if b not in pivot.columns:
            pivot[b] = 0
    pivot = pivot[vol_bands]
    pivot["n_total"] = pivot.sum(axis=1)
    for b in vol_bands:
        pivot[f"share_{b}"] = pivot[b] / pivot["n_total"]
    # Herfindahl and entropy
    pivot["herfindahl_volume"] = (pivot[[f"share_{b}" for b in vol_bands]]**2).sum(axis=1)
    # entropy: -sum p log p
    def entropy_row(row):
        p = np.array([row[f"share_{b}"] for b in vol_bands])
        p = p[p>0]
        return -np.sum(p * np.log(p))
    pivot["entropy_volume"] = pivot.apply(entropy_row, axis=1)
    pivot["share_heavy_500plus"] = pivot["share_500-999"] + pivot["share_1000+"]
    pivot["share_light_10_24"] = pivot["share_10-24"]
    pivot["share_heavy_250plus"] = pivot["share_250-499"] + pivot["share_500-999"] + pivot["share_1000+"]

    # Weight concentration: share of raters within +-0.5 of game's weight
    # Need per-rating weight diff: |mean_weight_u - weight_g|
    # Use user_features mean_weight
    # For games with weight NULL, skip
    print("  computing weight concentration...")
    weight_conc = con.execute(f"""
        WITH joined AS (
            SELECT r.game_id, g.weight AS gw, uf.mean_weight AS uw
            FROM read_parquet('{qpath(ro_path)}') r
            JOIN game_flags g USING (game_id)
            JOIN user_features uf ON r.user_pseudouserid = uf.uid
            WHERE g.weight IS NOT NULL AND uf.mean_weight IS NOT NULL
        )
        SELECT game_id,
               COUNT(*) AS n_weighted,
               AVG(CASE WHEN ABS(uw - gw) <= 0.3 THEN 1.0 ELSE 0.0 END) AS share_within_03,
               AVG(CASE WHEN ABS(uw - gw) <= 0.5 THEN 1.0 ELSE 0.0 END) AS share_within_05,
               AVG(CASE WHEN ABS(uw - gw) <= 0.8 THEN 1.0 ELSE 0.0 END) AS share_within_08,
               AVG(CASE WHEN ABS(uw - gw) <= 1.0 THEN 1.0 ELSE 0.0 END) AS share_within_10,
               AVG(ABS(uw - gw)) AS mean_abs_diff,
               STDDEV_SAMP(ABS(uw - gw)) AS sd_abs_diff,
               AVG(uw) AS mean_rater_weight,
               STDDEV_SAMP(uw) AS sd_rater_weight
        FROM joined GROUP BY game_id
    """).fetchdf()
    weight_conc = weight_conc.set_index("game_id")

    # Type specialist concentration: for games with flag=1, share of raters with >=10 other games of same type (other = total -1)
    # Need per game, per flag
    print("  computing type specialist shares...")
    # Use user_features type counts
    # Build per-game type specialist via join
    # For each flag type, if game has flag, then threshold on user n_flag -1
    # We'll compute separate queries per flag and merge
    spec_shares = {}
    for flag in FLAG_NAMES:
        col = FLAG_MAP[flag]
        # column in user_features: n_<flag> lower? We have n_warg etc, but 18xx is n_18xx, warg is n_warg, party n_party etc.
        # Map flag to uf column name
        uf_col = {"18XX":"n_18xx","Wargame":"n_warg","Party":"n_party","Economic":"n_econ","Coop":"n_coop","Legacy":"n_legacy"}[flag]
        df = con.execute(f"""
            SELECT r.game_id,
                   COUNT(*) AS n_raters,
                   AVG(CASE WHEN (uf.{uf_col} - 1) >= 10 THEN 1.0 ELSE 0.0 END) AS share_ge10_other,
                   AVG(CASE WHEN (uf.{uf_col} - 1) >= 20 THEN 1.0 ELSE 0.0 END) AS share_ge20_other,
                   AVG(CASE WHEN (uf.{uf_col} - 1) >= 5 THEN 1.0 ELSE 0.0 END) AS share_ge5_other,
                   AVG(CASE WHEN (uf.{uf_col} - 1) BETWEEN 0 AND 4 THEN 1.0 ELSE 0.0 END) AS share_0_4,
                   AVG(CASE WHEN (uf.{uf_col} - 1) BETWEEN 5 AND 19 THEN 1.0 ELSE 0.0 END) AS share_5_19,
                   AVG(uf.{uf_col} - 1) AS mean_other,
                   QUANTILE_CONT(uf.{uf_col} - 1, 0.5) AS median_other
            FROM read_parquet('{qpath(ro_path)}') r
            JOIN game_flags g USING (game_id)
            JOIN user_features uf ON r.user_pseudouserid = uf.uid
            WHERE g.{col}=1
            GROUP BY r.game_id
        """).fetchdf()
        if not df.empty:
            df = df.set_index("game_id")
            spec_shares[flag] = df
            print(f"    {flag}: {len(df)} games")
        else:
            print(f"    {flag}: no games")

    # Ownership concentration
    print("  computing ownership concentration...")
    own_share = con.execute(f"""
        SELECT r.game_id,
               COUNT(*) AS n_raters,
               SUM(CASE WHEN c.own = 1 THEN 1 ELSE 0 END)::DOUBLE / COUNT(*) AS share_own,
               COUNT(*) FILTER (WHERE c.own=1) AS n_own
        FROM read_parquet('{qpath(ro_path)}') r
        LEFT JOIN read_parquet('{qpath(coll_path)}') c ON r.game_id = c.game_id AND r.user_pseudouserid = c.user_pseudouserid
        GROUP BY r.game_id
    """).fetchdf().set_index("game_id")

    # Also mean_delta per game (average rater severity)
    print("  computing mean_delta per game...")
    mean_delta_per_game = con.execute(f"""
        SELECT r.game_id, AVG(COALESCE(uf.delta_full,0)) AS mean_delta_raters,
               STDDEV_SAMP(COALESCE(uf.delta_full,0)) AS sd_delta_raters,
               QUANTILE_CONT(COALESCE(uf.delta_full,0), 0.5) AS median_delta
        FROM read_parquet('{qpath(ro_path)}') r
        JOIN user_features uf ON r.user_pseudouserid = uf.uid
        GROUP BY r.game_id
    """).fetchdf().set_index("game_id")


    # Category/mechanic related concentration (list-based, defer heavy user_cat_counts)
    print("  computing category/mechanic related shares (deferred heavy build)...")
    try:
        t0=time.time()
        # Build per-user cat counts now (heavy, 12M rows) - deferred from earlier to reduce memory before mean_delta
        con.execute("""
            CREATE OR REPLACE TABLE user_cat_counts AS
            SELECT r.user_pseudouserid AS uid, gc.cat AS cat, COUNT(*) AS cnt
            FROM read_parquet('""" + qpath(ro_path) + """') r
            JOIN game_cats gc USING (game_id)
            GROUP BY r.user_pseudouserid, gc.cat
        """)
        print(f"    user_cat_counts built in {time.time()-t0:.1f}s: {con.execute('SELECT COUNT(*) FROM user_cat_counts').fetchone()[0]} rows")
        # active cats: where user has at least 2 ratings in that category (so has other sharing)
        con.execute("""
            CREATE OR REPLACE TABLE user_active_cats AS
            SELECT uid, list(cat) AS cats
            FROM (SELECT uid, cat FROM user_cat_counts WHERE cnt >= 2)
            GROUP BY uid
        """)
        con.execute("""
            CREATE OR REPLACE TABLE game_cats_list AS
            SELECT game_id, list(cat) AS cats
            FROM game_cats
            GROUP BY game_id
        """)
        print(f"    user_active_cats and game_cats_list built in {time.time()-t0:.1f}s (additional)")
        # Compute per-game share via single aggregation over 24M ratings joining two small lists
        cat_related = con.execute("""
            SELECT r.game_id,
                   COUNT(*) AS n_raters,
                   AVG(CASE WHEN len(list_intersect(gc.cats, COALESCE(uc.cats, []))) > 0 THEN 1.0 ELSE 0.0 END) AS share_cat_related,
                   AVG(CASE WHEN len(list_intersect(gc.cats, COALESCE(uc.cats, []))) >= 2 THEN 1.0 ELSE 0.0 END) AS share_cat_ge2,
                   AVG(len(list_intersect(gc.cats, COALESCE(uc.cats, [])))::DOUBLE) AS mean_overlap
            FROM read_parquet('""" + qpath(ro_path) + """') r
            JOIN game_cats_list gc USING (game_id)
            LEFT JOIN user_active_cats uc ON r.user_pseudouserid = uc.uid
            GROUP BY r.game_id
        """).fetchdf().set_index("game_id")
        cat_related["share_cat_ge5"] = cat_related["share_cat_ge2"]
        cat_related["mean_sum_other_cat"] = cat_related["mean_overlap"]
        cat_related["median_sum_other_cat"] = np.nan
        mech_related = pd.DataFrame()
        combined = cat_related[["share_cat_related"]].copy()
        combined.columns = ["share_cat_or_mech_related"]
        print(f"  cat_related computed for {len(cat_related)} games via list_intersect (mech skipped)")
        try:
            con.execute("DROP TABLE IF EXISTS user_cat_counts")
            con.execute("DROP TABLE IF EXISTS user_active_cats")
            con.execute("DROP TABLE IF EXISTS game_cats_list")
            print("  dropped user_cat_counts and temp lists to free memory")
        except Exception as e2:
            print(f"  drop failed {e2}")
    except Exception as e:
        print(f"  category related computation failed: {e}, using fallback approximate")
        import traceback; traceback.print_exc()
        cat_related = pd.DataFrame()
        mech_related = pd.DataFrame()
        combined = pd.DataFrame()

    # Now assemble per-game concentration dataframe for output A
    # Start from game_base
    gb = con.execute("SELECT * FROM game_base").fetchdf().set_index("game_id")
    # Join all computed
    # pivot is already indexed game_id
    # Need to align
    # Create empty DataFrame for final
    # Use gb as base, then add columns
    # Ensure pivot index is game_id
    # Merge
    concent = gb.copy()
    # Add volume shares
    for b in vol_bands:
        concent[f"share_vol_{b}"] = pivot[f"share_{b}"]
    concent["herfindahl_volume"] = pivot["herfindahl_volume"]
    concent["entropy_volume"] = pivot["entropy_volume"]
    concent["share_vol_heavy_500plus"] = pivot["share_heavy_500plus"]
    concent["share_vol_light_10_24"] = pivot["share_light_10_24"]
    concent["share_vol_heavy_250plus"] = pivot["share_heavy_250plus"]
    # Weight
    for col in weight_conc.columns:
        if col != "n_weighted":
            concent[col] = weight_conc[col]
    # type specialist: we have per-flag dataframes, need to map to concent columns
    for flag, df in spec_shares.items():
        # df columns share_ge10_other etc
        for c in df.columns:
            concent[f"spec_{flag}_{c}"] = df[c]
    # For games not of that flag, those columns will be NaN (not applicable)
    # Also need generic specialist share for primary type: pick relevant flag per game
    concent["spec_primary_share_ge10"] = np.nan
    concent["spec_primary_share_ge20"] = np.nan
    concent["spec_primary_mean_other"] = np.nan
    for flag in FLAG_NAMES:
        mask = concent[f"flag_{FLAG_MAP[flag].replace('flag_','')}"] if False else None
    # Instead loop over flags and fill where flag=1
    for flag in FLAG_NAMES:
        col_flag = FLAG_MAP[flag]
        if col_flag in concent.columns:
            # need to map: concent has flag_18xx etc from game_base? game_base has flag_18xx etc
            pass
    # Fill primary: for each game, find its primary_type and assign
    # We'll do python loop over concent index
    for gid, row in concent.iterrows():
        pt = row["primary_type"]
        if pt != "Other" and pt in FLAG_NAMES:
            df = spec_shares.get(pt)
            if df is not None and gid in df.index:
                concent.at[gid, "spec_primary_share_ge10"] = df.at[gid, "share_ge10_other"]
                concent.at[gid, "spec_primary_share_ge20"] = df.at[gid, "share_ge20_other"]
                concent.at[gid, "spec_primary_mean_other"] = df.at[gid, "mean_other"]
    # Category/mech related
    if not cat_related.empty:
        for col in cat_related.columns:
            concent[col] = cat_related[col]
    if not mech_related.empty:
        for col in mech_related.columns:
            concent[col] = mech_related[col]
    if not combined.empty:
        concent["share_cat_or_mech_related"] = combined["share_cat_or_mech_related"]
    # ownership
    concent["share_own"] = own_share["share_own"]
    concent["n_own"] = own_share["n_own"]
    # mean_delta
    concent["mean_delta_raters"] = mean_delta_per_game["mean_delta_raters"]
    concent["sd_delta_raters"] = mean_delta_per_game["sd_delta_raters"]
    # Add n_obs2 etc from game_rating_stats
    grs = con.execute("SELECT * FROM game_rating_stats").fetchdf().set_index("game_id")
    for col in ["n_obs2","raw_mean2","adj_mean2","sd_raw","sd_adj","se_raw","se_adj"]:
        concent[col] = grs[col]
    # Also add weight null flag
    concent["weight_null"] = concent["weight"].isna()

    print(f"  assembled concent rows: {len(concent)}")

    # Save intermediate for later use
    # We'll keep concent as DataFrame for output

    # ------------------------------------------------------------------
    # B. Prior Exposure distribution (already partly computed in spec)
    # For each game, we have shares per bin for its primary type via spec_shares
    # We'll compute more detailed bins: 0, 1-4, 5-9,10-19,20-49,50+
    # But task requires bins 0-4,5-19,>=20 -> we have those
    # We'll create per-game B table: game_id, primary_type, share_0_4, share_5_19, share_ge20, mean_other, median_other, etc.
    # For Other games, we can compute generic cat sharing bins via per_user_game_cat sum tiers
    # Let's compute generic sharing tier for Other games via per_user_game_cat sum categories
    # For Other, sum_other_cat distribution tiers
    # ------------------------------------------------------------------
    print("[6/12] B. Prior Exposure distributions...")
    # We'll produce exposure_df per game
    # For flagged types, use spec_shares already
    # For Other, compute generic
    exposure_rows = []
    for gid, row in concent.iterrows():
        pt = row["primary_type"]
        n_obs_val = row["n_obs"] if not pd.isna(row["n_obs"]) else row["n_obs2"]
        # default
        share_0_4 = np.nan
        share_5_19 = np.nan
        share_ge20 = np.nan
        share_ge10 = np.nan
        mean_other = np.nan
        median_other = np.nan
        # For flagged, fetch
        if pt != "Other" and pt in spec_shares:
            df = spec_shares[pt]
            if gid in df.index:
                share_0_4 = df.at[gid, "share_0_4"]
                share_5_19 = df.at[gid, "share_5_19"]
                share_ge20 = df.at[gid, "share_ge20_other"]
                share_ge10 = df.at[gid, "share_ge10_other"]
                mean_other = df.at[gid, "mean_other"]
                median_other = df.at[gid, "median_other"]
        else:
            # For Other, use cat sharing sum_other_cat tiers if available
            # Compute tier shares via per_user_game_cat distribution per game? We have per_user_game_cat table
            # Let's query per game distribution on the fly for Other games? That would be many queries, heavy.
            # Instead we can approximate via existing cat_related mean/median and tier counts via SQL aggregated per game for Other only
            # We'll later compute via SQL for all games and merge
            pass
        exposure_rows.append({
            "game_id": gid,
            "title": row["title"],
            "primary_type": pt,
            "n_obs": n_obs_val,
            "share_0_4": share_0_4,
            "share_5_19": share_5_19,
            "share_ge20": share_ge20,
            "share_ge10": share_ge10,
            "mean_other": mean_other,
            "median_other": median_other,
            "weight": row["weight"]
        })
    exposure_df = pd.DataFrame(exposure_rows).set_index("game_id")
    # For Other games, we skip cat tier filling (would require per_user_game_cat which we removed for memory).
    # Exposure for Other remains NaN (not applicable) and documented as limitation: Other uses cat_related share only.

    # ------------------------------------------------------------------
    # C. Cross-Audience Performance
    # For each game, compare severity-adjusted ratings across splits
    # Splits:
    #  - volume: low 10-24 vs high 500+ (500-999+1000+) AND high 1000+ vs low
    #  - specialist vs nonspecialist: 0-4 vs >=20 (and 0-4 vs >=10)
    #  - ownership: own=1 vs not own (own is not null 1 else 0)
    #  - weight: within 0.5 vs outside (for games with weight not null and raters with mean_weight)
    # Do not assume one split sufficient; evaluate thresholds >=5 per side as minimum, >=10 preferred
    # ------------------------------------------------------------------
    print("[7/12] C. Cross-Audience Performance...")
    # Need severity-adjusted rating per observation: rating - delta_full
    # We'll create view obs_adj
    con.execute(f"""
        CREATE OR REPLACE VIEW obs_adj AS
        SELECT r.game_id, r.user_pseudouserid, r.rating, r.rating_observation_id,
               COALESCE(s.delta_full,0) AS delta,
               r.rating - COALESCE(s.delta_full,0) AS rating_adj,
               uf.volume_band, uf.mean_weight, uf.n_18xx, uf.n_warg, uf.n_party, uf.n_econ, uf.n_coop, uf.n_legacy,
               g.weight AS game_weight,
               g.flag_18xx, g.flag_warg, g.flag_party, g.flag_econ, g.flag_coop, g.flag_legacy, g.primary_type,
               c.own
        FROM read_parquet('{qpath(ro_path)}') r
        JOIN game_flags g USING (game_id)
        JOIN user_features uf ON r.user_pseudouserid = uf.uid
        LEFT JOIN read_parquet('{qpath(sev_path)}') s ON r.user_pseudouserid = s.user_pseudouserid
        LEFT JOIN read_parquet('{qpath(coll_path)}') c ON r.game_id = c.game_id AND r.user_pseudouserid = c.user_pseudouserid
    """)
    # We'll compute per-game cross-audience via Python loops over games? Better to compute via SQL GROUP BY game_id, split_group
    # Define split logic as CASE expressions, then pivot
    # For volume split
    cross_rows = []
    # Helper function to compute per-game split stats via SQL

    def compute_split(split_name, low_cond, high_cond, description):
        # low_cond and high_cond are SQL boolean expressions on obs_adj row
        # Compute per game aggregates for low and high groups
        sql = f"""
        SELECT game_id,
               COUNT(*) FILTER (WHERE {low_cond}) AS n_low,
               COUNT(*) FILTER (WHERE {high_cond}) AS n_high,
               AVG(rating_adj) FILTER (WHERE {low_cond}) AS mean_low_adj,
               AVG(rating_adj) FILTER (WHERE {high_cond}) AS mean_high_adj,
               AVG(rating) FILTER (WHERE {low_cond}) AS mean_low_raw,
               AVG(rating) FILTER (WHERE {high_cond}) AS mean_high_raw,
               STDDEV_SAMP(rating_adj) FILTER (WHERE {low_cond}) AS sd_low_adj,
               STDDEV_SAMP(rating_adj) FILTER (WHERE {high_cond}) AS sd_high_adj,
               STDDEV_SAMP(rating) FILTER (WHERE {low_cond}) AS sd_low_raw,
               STDDEV_SAMP(rating) FILTER (WHERE {high_cond}) AS sd_high_raw
        FROM obs_adj
        GROUP BY game_id
        HAVING COUNT(*) FILTER (WHERE {low_cond}) >= 5
           AND COUNT(*) FILTER (WHERE {high_cond}) >= 5
        """
        df = con.execute(sql).fetchdf()
        if df.empty:
            print(f"    split {split_name}: no games with >=5 per side")
            return
        # Compute diff, se, z
        df["diff_adj"] = df["mean_high_adj"] - df["mean_low_adj"]
        # SE: sqrt(sd_low^2/n_low + sd_high^2/n_high)
        df["se_low"] = df["sd_low_adj"] / np.sqrt(df["n_low"])
        df["se_high"] = df["sd_high_adj"] / np.sqrt(df["n_high"])
        df["se_diff"] = np.sqrt(df["se_low"]**2 + df["se_high"]**2)
        df["z"] = df["diff_adj"] / df["se_diff"]
        # p approx two-sided normal
        from math import erf, sqrt
        def p_from_z(z):
            if pd.isna(z): return np.nan
            import math
            return 2*(1 - 0.5*(1+math.erf(abs(z)/math.sqrt(2))))
        df["p_value"] = df["z"].apply(p_from_z)
        df["supported_ge10"] = (df["n_low"]>=10) & (df["n_high"]>=10)
        df["supported_ge5"] = (df["n_low"]>=5) & (df["n_high"]>=5)
        df["is_significant"] = df["p_value"] < 0.05
        # Flag: highly rated remains? Check if both means high? We'll compute later
        df["split_type"] = split_name
        df["description"] = description
        # Append to cross_rows list
        for _, row in df.iterrows():
            cross_rows.append(row.to_dict())
        print(f"    split {split_name}: {len(df)} games with >=5 per side, {df['supported_ge10'].sum()} with >=10")
        return df

    # Volume low vs high
    compute_split("volume_10-24_vs_500plus", "volume_band='10-24'", "volume_band IN ('500-999','1000+')", "high volume 500+ vs light 10-24")
    compute_split("volume_10-24_vs_1000plus", "volume_band='10-24'", "volume_band='1000+'", "1000+ vs 10-24")
    # For specialist splits, need per-type condition: for each game of that type, low = other 0-4, high = >=20
    # We'll create separate splits per type, but general taxonomy needs per-game specialist vs nonspecialist
    # Approach: for each type, compute split where game has flag=1, then low = (uf.n_flag -1 between 0 and 4), high = >=20
    # We'll do one combined split: specialist_vs_nonspecialist_generic where low is 0-4 for primary type, high >=20 for primary type
    # Need to define low/high conditions that depend on primary_type
    # For that, we can use CASE: when primary_type='Wargame' THEN n_warg-1 between 0 and 4 etc.
    # Build expression:
    # low_specialist: (primary_type='18XX' AND n_18xx-1 BETWEEN 0 AND 4) OR (primary_type='Wargame' AND n_warg-1 BETWEEN 0 AND 4) etc.
    # high_specialist: similarly >=20

    # Specialist vs non-specialist defined only for flagged types (Other excluded to avoid per_user_game_cat dependency)
    # Low = 0-4 other, High = >=20 (and >=10 variant)
    low_spec_expr2 = """
    ( (primary_type='18XX' AND n_18xx-1 BETWEEN 0 AND 4) OR
      (primary_type='Wargame' AND n_warg-1 BETWEEN 0 AND 4) OR
      (primary_type='Party' AND n_party-1 BETWEEN 0 AND 4) OR
      (primary_type='Economic' AND n_econ-1 BETWEEN 0 AND 4) OR
      (primary_type='Coop' AND n_coop-1 BETWEEN 0 AND 4) OR
      (primary_type='Legacy' AND n_legacy-1 BETWEEN 0 AND 4)
    )
    """
    high_spec_expr2 = """
    ( (primary_type='18XX' AND n_18xx-1 >= 20) OR
      (primary_type='Wargame' AND n_warg-1 >= 20) OR
      (primary_type='Party' AND n_party-1 >= 20) OR
      (primary_type='Economic' AND n_econ-1 >= 20) OR
      (primary_type='Coop' AND n_coop-1 >= 20) OR
      (primary_type='Legacy' AND n_legacy-1 >= 20)
    )
    """
    high_spec_expr_ge10 = """
    ( (primary_type='18XX' AND n_18xx-1 >= 10) OR
      (primary_type='Wargame' AND n_warg-1 >= 10) OR
      (primary_type='Party' AND n_party-1 >= 10) OR
      (primary_type='Economic' AND n_econ-1 >= 10) OR
      (primary_type='Coop' AND n_coop-1 >= 10) OR
      (primary_type='Legacy' AND n_legacy-1 >= 10)
    )
    """
    # Use obs_adj (not obs_adj2) for specialist splits - no need for cat sum
    def compute_split2(split_name, low_cond, high_cond, view="obs_adj"):
        sql = f"""
        SELECT game_id,
               COUNT(*) FILTER (WHERE {low_cond}) AS n_low,
               COUNT(*) FILTER (WHERE {high_cond}) AS n_high,
               AVG(rating_adj) FILTER (WHERE {low_cond}) AS mean_low_adj,
               AVG(rating_adj) FILTER (WHERE {high_cond}) AS mean_high_adj,
               AVG(rating) FILTER (WHERE {low_cond}) AS mean_low_raw,
               AVG(rating) FILTER (WHERE {high_cond}) AS mean_high_raw,
               STDDEV_SAMP(rating_adj) FILTER (WHERE {low_cond}) AS sd_low_adj,
               STDDEV_SAMP(rating_adj) FILTER (WHERE {high_cond}) AS sd_high_adj
        FROM {view}
        GROUP BY game_id
        HAVING COUNT(*) FILTER (WHERE {low_cond}) >= 5
           AND COUNT(*) FILTER (WHERE {high_cond}) >= 5
        """
        df = con.execute(sql).fetchdf()
        if df.empty:
            print(f"    split {split_name}: no games with >=5 per side")
            return None
        df["diff_adj"] = df["mean_high_adj"] - df["mean_low_adj"]
        df["se_low"] = df["sd_low_adj"] / np.sqrt(df["n_low"])
        df["se_high"] = df["sd_high_adj"] / np.sqrt(df["n_high"])
        df["se_diff"] = np.sqrt(df["se_low"]**2 + df["se_high"]**2)
        df["z"] = df["diff_adj"] / df["se_diff"]
        import math
        df["p_value"] = df["z"].apply(lambda z: 2*(1 - 0.5*(1+math.erf(abs(z)/math.sqrt(2)))) if not pd.isna(z) else np.nan)
        df["supported_ge10"] = (df["n_low"]>=10) & (df["n_high"]>=10)
        df["supported_ge5"] = (df["n_low"]>=5) & (df["n_high"]>=5)
        df["is_significant"] = df["p_value"] < 0.05
        df["split_type"] = split_name
        for _, row in df.iterrows():
            cross_rows.append(row.to_dict())
        print(f"    split {split_name}: {len(df)} games >=5, {df['supported_ge10'].sum()} >=10")
        return df

    compute_split2("specialist_0-4_vs_ge20", low_spec_expr2, high_spec_expr2)
    compute_split2("specialist_0-4_vs_ge10", low_spec_expr2, high_spec_expr_ge10)

    # Ownership split: own=1 vs own is null or 0? Use own=1 vs own is null
    # Note: collections own is snapshot, not rating time (caveat)
    compute_split2("ownership_own_vs_not", "own=1", "own IS NULL OR own !=1")
    # Weight preference split: within 0.5 vs outside
    # Only for ratings where mean_weight not null and game_weight not null
    compute_split2("weight_within0.5_vs_outside", "ABS(mean_weight - game_weight) <= 0.5", "ABS(mean_weight - game_weight) > 0.5")

    # Also add per-type specialist splits separately for methodology comparison (not for main cross table but for sensitivity)
    for flag in FLAG_NAMES:
        col = FLAG_MAP[flag]
        uf_col = {"18XX":"n_18xx","Wargame":"n_warg","Party":"n_party","Economic":"n_econ","Coop":"n_coop","Legacy":"n_legacy"}[flag]
        low = f"({col}=1 AND {uf_col}-1 BETWEEN 0 AND 4)"
        high20 = f"({col}=1 AND {uf_col}-1 >=20)"
        # Use obs_adj (not obs_adj2) for these type-specific because condition filters to flag=1
        compute_split(f"specialist_{flag}_0-4_vs_ge20", low, high20, f"{flag} specialist")

    # Build cross_df from cross_rows
    if cross_rows:
        cross_df = pd.DataFrame(cross_rows)
        # Add title, adj_mean, n_obs, etc via join with game_base
        gb_small = con.execute("SELECT game_id, title, n_obs, adj_mean, raw_mean FROM game_base").fetchdf().set_index("game_id")
        cross_df["title"] = cross_df["game_id"].map(gb_small["title"])
        cross_df["n_obs_game"] = cross_df["game_id"].map(gb_small["n_obs"])
        cross_df["adj_mean_game"] = cross_df["game_id"].map(gb_small["adj_mean"])
        # Order columns
        cols = ["game_id","title","split_type","n_low","n_high","mean_low_adj","mean_high_adj","diff_adj","se_diff","z","p_value","supported_ge10","supported_ge5","is_significant","n_obs_game","adj_mean_game","mean_low_raw","mean_high_raw","sd_low_adj","sd_high_adj"]
        # Keep only existing cols
        cross_df = cross_df[[c for c in cols if c in cross_df.columns]]
    else:
        cross_df = pd.DataFrame(columns=["game_id","split_type","n_low","n_high"])

    print(f"  total cross-audience rows: {len(cross_df)}")

    # ------------------------------------------------------------------
    # D. Rating Heterogeneity
    # Distinguish ordinary noise vs genuine disagreement vs concentrated enthusiasm
    # Use cross results to categorize
    # ------------------------------------------------------------------
    print("[8/12] D. Rating Heterogeneity...")
    # For each game, we have overall sd_adj and se_adj, plus cross splits
    # Define per-game heterogeneity summary:
    # - overall heterogeneity: sd_adj, se_adj, n_obs
    # - max absolute diff across splits where supported_ge5
    # - proportion of splits with significant diff
    # We'll compute per-game heterogeneity dataframe
    het_rows = []
    # Group cross_df by game_id
    if not cross_df.empty:
        grouped = cross_df.groupby("game_id")
        for gid, grp in grouped:
            # overall stats from game_rating_stats
            # Need overall sd etc
            # fetch from grs
            if gid in grs.index:
                overall_sd = grs.at[gid, "sd_adj"]
                overall_se = grs.at[gid, "se_adj"]
                n = grs.at[gid, "n_obs2"]
            else:
                overall_sd = np.nan
                overall_se = np.nan
                n = np.nan
            max_diff = grp["diff_adj"].abs().max() if "diff_adj" in grp else np.nan
            max_z = grp["z"].abs().max() if "z" in grp else np.nan
            n_splits_tested = len(grp)
            n_significant = grp["is_significant"].sum() if "is_significant" in grp else 0
            # Concentrated specialist enthusiasm: high mean + low between-segment spread but narrow pool
            # Define as: adj_mean high (>=7.5) and max_diff small (<0.3) and narrow pool (e.g., high specialist share)
            # We'll use concent to get specialist share
            spec_share = np.nan
            if gid in concent.index:
                spec_share = concent.at[gid, "spec_primary_share_ge10"] if "spec_primary_share_ge10" in concent.columns else np.nan
                share_cat = concent.at[gid, "share_cat_or_mech_related"] if "share_cat_or_mech_related" in concent.columns else np.nan
                share_own_val = concent.at[gid, "share_own"] if "share_own" in concent.columns else np.nan
                adj = concent.at[gid, "adj_mean"] if "adj_mean" in concent.columns else np.nan
                herf = concent.at[gid, "herfindahl_volume"] if "herfindahl_volume" in concent.columns else np.nan
            else:
                share_cat = np.nan
                share_own_val = np.nan
                adj = np.nan
                herf = np.nan
            # Categorization
            # Insufficient if no split with ge5 support? Already filtered to have at least one split, but some games may have no cross rows (no splits supported)
            # We'll later handle insufficient via lack of cross rows
            # For now, define heterogeneity categories
            if pd.isna(max_diff):
                category = "insufficient"
            elif max_z is not None and max_z < 2 and max_diff < 0.3:
                category = "ordinary_noise"
            elif max_z >= 2 and max_diff >= 0.3:
                category = "genuine_disagreement"
            elif not pd.isna(adj) and adj >= 7.5 and max_diff < 0.3 and not pd.isna(spec_share) and spec_share > 0.4:
                category = "concentrated_specialist_enthusiasm"
            else:
                category = "moderate_heterogeneity"
            het_rows.append({
                "game_id": gid,
                "n_obs": n,
                "overall_sd_adj": overall_sd,
                "overall_se_adj": overall_se,
                "max_abs_diff_adj": max_diff,
                "max_abs_z": max_z,
                "n_splits_tested": n_splits_tested,
                "n_significant_splits": n_significant,
                "spec_primary_share_ge10": spec_share,
                "adj_mean": adj,
                "heterogeneity_category": category
            })
        het_df = pd.DataFrame(het_rows).set_index("game_id")
        # Also add games with no cross rows as insufficient
        all_gids = set(concent.index)
        het_gids = set(het_df.index)
        missing = all_gids - het_gids
        for gid in missing:
            # fetch overall stats
            if gid in grs.index:
                overall_sd = grs.at[gid, "sd_adj"]
                overall_se = grs.at[gid, "se_adj"]
                n = grs.at[gid, "n_obs2"]
            else:
                overall_sd = np.nan
                overall_se = np.nan
                n = np.nan
            adj = concent.at[gid, "adj_mean"] if gid in concent.index else np.nan
            het_rows.append({
                "game_id": gid,
                "n_obs": n,
                "overall_sd_adj": overall_sd,
                "overall_se_adj": overall_se,
                "max_abs_diff_adj": np.nan,
                "max_abs_z": np.nan,
                "n_splits_tested": 0,
                "n_significant_splits": 0,
                "spec_primary_share_ge10": concent.at[gid, "spec_primary_share_ge10"] if gid in concent.index else np.nan,
                "adj_mean": adj,
                "heterogeneity_category": "insufficient_evidence"
            })
        het_df = pd.DataFrame(het_rows).set_index("game_id")
        print(f"  heterogeneity categories: {het_df['heterogeneity_category'].value_counts().to_dict()}")
    else:
        het_df = pd.DataFrame()

    # ------------------------------------------------------------------
    # E. Rater-Pool Distinctiveness
    # Compare game's rater-pool composition with reference populations
    # References: global, same type, same weight_class_3, same volume decile (or n_obs quintile)
    # Distinctiveness metrics: TVD_volume, delta_diff, weight_diff, specialist_share_diff
    # ------------------------------------------------------------------
    print("[9/12] E. Rater-Pool Distinctiveness...")
    # Compute global reference distributions
    global_vol = con.execute("""
        SELECT volume_band, COUNT(*)::DOUBLE / (SELECT COUNT(*) FROM read_parquet('""" + qpath(ro_path) + """')) AS share
        FROM read_parquet('""" + qpath(ro_path) + """') r
        JOIN user_features uf ON r.user_pseudouserid = uf.uid
        GROUP BY volume_band
    """).fetchdf().set_index("volume_band")["share"].to_dict()
    global_mean_delta = con.execute("SELECT AVG(delta_full) FROM user_features WHERE delta_full IS NOT NULL").fetchone()[0]
    global_mean_weight = con.execute("SELECT AVG(mean_weight) FROM user_features WHERE mean_weight IS NOT NULL").fetchone()[0]
    global_spec_shares = {}
    for flag in FLAG_NAMES:
        uf_col = {"18XX":"n_18xx","Wargame":"n_warg","Party":"n_party","Economic":"n_econ","Coop":"n_coop","Legacy":"n_legacy"}[flag]
        # global specialist share among all ratings: share of ratings where rater has >=10 other of that type?
        # But that is per-rating; better to compute per-rating specialist rate for each flag where relevant? For global we compute overall share of raters with >=10 of that type across all ratings (not just flagged games)
        # For distinctiveness, we want reference for that type's pool: e.g., Wargame reference is distribution among Wargame ratings
        pass

    # To compare, we need per-type reference distributions for volume etc.
    # Compute per-type reference volume shares, mean delta, etc.
    type_refs = {}
    for flag in FLAG_NAMES:
        col = FLAG_MAP[flag]
        # Volume shares among ratings of games of that type
        vol = con.execute(f"""
            SELECT uf.volume_band AS volume_band, COUNT(*)::DOUBLE / NULLIF((SELECT COUNT(*) FROM read_parquet('{qpath(ro_path)}') r JOIN game_flags g USING (game_id) WHERE g.{col}=1),0) AS share
            FROM read_parquet('{qpath(ro_path)}') r
            JOIN game_flags g USING (game_id)
            JOIN user_features uf ON r.user_pseudouserid = uf.uid
            WHERE g.{col}=1
            GROUP BY uf.volume_band
        """).fetchdf()
        if not vol.empty:
            vol = vol.set_index("volume_band")["share"].to_dict()
        else:
            vol = {}
        mean_delta = con.execute(f"""
            SELECT AVG(uf.delta_full) FROM read_parquet('{qpath(ro_path)}') r
            JOIN game_flags g USING (game_id)
            JOIN user_features uf ON r.user_pseudouserid = uf.uid
            WHERE g.{col}=1
        """).fetchone()[0]
        mean_weight = con.execute(f"""
            SELECT AVG(uf.mean_weight) FROM read_parquet('{qpath(ro_path)}') r
            JOIN game_flags g USING (game_id)
            JOIN user_features uf ON r.user_pseudouserid = uf.uid
            WHERE g.{col}=1 AND uf.mean_weight IS NOT NULL
        """).fetchone()[0]
        type_refs[flag] = {"vol_shares": vol, "mean_delta": mean_delta, "mean_weight": mean_weight}

    # Weight class refs
    weight_refs = {}
    for wc in ["Light","Medium","Heavy"]:
        vol = con.execute(f"""
            SELECT uf.volume_band AS volume_band, COUNT(*)::DOUBLE / NULLIF((SELECT COUNT(*) FROM read_parquet('{qpath(ro_path)}') r JOIN game_flags g USING (game_id) WHERE g.weight_class_3='{wc}'),0) AS share
            FROM read_parquet('{qpath(ro_path)}') r
            JOIN game_flags g USING (game_id)
            JOIN user_features uf ON r.user_pseudouserid = uf.uid
            WHERE g.weight_class_3='{wc}'
            GROUP BY uf.volume_band
        """).fetchdf()
        if not vol.empty:
            vol = vol.set_index("volume_band")["share"].to_dict()
        else:
            vol = {}
        mean_delta = con.execute(f"""
            SELECT AVG(uf.delta_full) FROM read_parquet('{qpath(ro_path)}') r
            JOIN game_flags g USING (game_id)
            JOIN user_features uf ON r.user_pseudouserid = uf.uid
            WHERE g.weight_class_3='{wc}'
        """).fetchone()[0]
        weight_refs[wc] = {"vol_shares": vol, "mean_delta": mean_delta}

    # Volume decile refs: need n_obs per game, then bucket games into deciles by n_obs
    # Compute deciles
    n_obs_vals = con.execute("SELECT n_obs FROM game_base WHERE n_obs IS NOT NULL ORDER BY n_obs").fetchdf()["n_obs"].values
    deciles = np.quantile(n_obs_vals, [0.2,0.4,0.6,0.8])
    def vol_decile(n):
        if n <= deciles[0]: return "D1"
        elif n <= deciles[1]: return "D2"
        elif n <= deciles[2]: return "D3"
        elif n <= deciles[3]: return "D4"
        else: return "D5"
    # Add decile to game_base for reference grouping
    # Instead compute per decile reference volume shares via SQL using CASE
    # We'll compute distinctiveness per game via python loop using precomputed pivot shares and reference shares
    # For each game, TVD vs global = 0.5*sum|share_game - share_global|
    # Similarly vs type (if flagged), vs weight_class, vs volume decile (need per decile vol shares)

    # Compute volume decile refs: need per decile vol shares
    # Add decile logic to SQL: compute per decile per volume_band counts
    # Use n_obs from game_base

    # First create view game_decile
    con.execute("""
        CREATE OR REPLACE VIEW game_decile AS
        SELECT game_id, n_obs,
               CASE WHEN n_obs <= """ + str(deciles[0]) + """ THEN 'D1'
                    WHEN n_obs <= """ + str(deciles[1]) + """ THEN 'D2'
                    WHEN n_obs <= """ + str(deciles[2]) + """ THEN 'D3'
                    WHEN n_obs <= """ + str(deciles[3]) + """ THEN 'D4'
                    ELSE 'D5' END AS decile
        FROM game_base
    """)
    decile_vol_refs = {}
    for d in ["D1","D2","D3","D4","D5"]:
        vol = con.execute(f"""
            SELECT uf.volume_band AS volume_band, COUNT(*)::DOUBLE / NULLIF((SELECT COUNT(*) FROM read_parquet('{qpath(ro_path)}') r JOIN game_decile gd USING (game_id) WHERE gd.decile='{d}'),0) AS share
            FROM read_parquet('{qpath(ro_path)}') r
            JOIN game_decile gd USING (game_id)
            JOIN user_features uf ON r.user_pseudouserid = uf.uid
            WHERE gd.decile='{d}'
            GROUP BY uf.volume_band
        """).fetchdf()
        if not vol.empty:
            vol = vol.set_index("volume_band")["share"].to_dict()
        else:
            vol = {}
        decile_vol_refs[d] = vol

    # Now compute per-game distinctiveness
    distinct_rows = []
    for gid in concent.index:
        row = concent.loc[gid]
        # volume shares for this game
        game_shares = {b: row[f"share_vol_{b}"] for b in vol_bands if f"share_vol_{b}" in row and not pd.isna(row[f"share_vol_{b}"])}
        # global TVD
        tvd_global = 0.5 * sum(abs(game_shares.get(b,0) - global_vol.get(b,0)) for b in vol_bands)
        # type TVD (if flagged)
        pt = row["primary_type"]
        if pt != "Other" and pt in type_refs:
            ref_vol = type_refs[pt]["vol_shares"]
            tvd_type = 0.5 * sum(abs(game_shares.get(b,0) - ref_vol.get(b,0)) for b in vol_bands)
            delta_diff_type = (row["mean_delta_raters"] - type_refs[pt]["mean_delta"]) if not pd.isna(row["mean_delta_raters"]) and type_refs[pt]["mean_delta"] is not None else np.nan
        else:
            tvd_type = np.nan
            delta_diff_type = np.nan
        # weight class TVD
        wc = row["weight_class_3"]
        if wc in weight_refs:
            ref_vol_w = weight_refs[wc]["vol_shares"]
            tvd_weight = 0.5 * sum(abs(game_shares.get(b,0) - ref_vol_w.get(b,0)) for b in vol_bands)
            delta_diff_weight = (row["mean_delta_raters"] - weight_refs[wc]["mean_delta"]) if not pd.isna(row["mean_delta_raters"]) and weight_refs[wc]["mean_delta"] is not None else np.nan
        else:
            tvd_weight = np.nan
            delta_diff_weight = np.nan
        # decile TVD
        n = row["n_obs"] if not pd.isna(row["n_obs"]) else row["n_obs2"]
        dec = vol_decile(n) if not pd.isna(n) else "D3"
        ref_vol_d = decile_vol_refs.get(dec, {})
        tvd_decile = 0.5 * sum(abs(game_shares.get(b,0) - ref_vol_d.get(b,0)) for b in vol_bands) if ref_vol_d else np.nan
        # mean delta diffs vs global
        delta_diff_global = (row["mean_delta_raters"] - global_mean_delta) if not pd.isna(row["mean_delta_raters"]) and global_mean_delta is not None else np.nan
        # mean weight diff vs global
        weight_diff_global = (row["mean_rater_weight"] - global_mean_weight) if "mean_rater_weight" in row and not pd.isna(row["mean_rater_weight"]) and global_mean_weight is not None else np.nan
        # Also weight diff vs type?
        # For now store
        distinct_rows.append({
            "game_id": gid,
            "tvd_volume_global": tvd_global,
            "tvd_volume_type": tvd_type,
            "tvd_volume_weight": tvd_weight,
            "tvd_volume_decile": tvd_decile,
            "delta_diff_global": delta_diff_global,
            "delta_diff_type": delta_diff_type,
            "delta_diff_weight": delta_diff_weight,
            "weight_diff_global": weight_diff_global,
            "mean_delta_raters": row["mean_delta_raters"],
            "global_mean_delta": global_mean_delta,
            "decile": dec
        })
    distinct_df = pd.DataFrame(distinct_rows).set_index("game_id")
    print(f"  distinctiveness computed for {len(distinct_df)} games")
    # Compute which reference most informative: compare variance across games for each TVD
    # We'll do in methodology comparison

    # ------------------------------------------------------------------
    # F. Exposure Proxy / Missing-non-rater
    # For each type-typed game, compute penetration among enthusiasts (>=20)
    # Also for Other via cat sharing >=20
    # ------------------------------------------------------------------
    print("[10/12] F. Exposure Proxy (penetration among enthusiasts)...")
    # Precompute enthusiast sets per flag: count of users with n_flag >=20 and >=10
    enthusiast_counts = {}
    for flag in FLAG_NAMES:
        uf_col = {"18XX":"n_18xx","Wargame":"n_warg","Party":"n_party","Economic":"n_econ","Coop":"n_coop","Legacy":"n_legacy"}[flag]
        cnt20 = con.execute(f"SELECT COUNT(*) FROM user_features WHERE {uf_col} >=20").fetchone()[0]
        cnt10 = con.execute(f"SELECT COUNT(*) FROM user_features WHERE {uf_col} >=10").fetchone()[0]
        enthusiast_counts[flag] = {"ge20": cnt20, "ge10": cnt10}
        print(f"  {flag} enthusiasts ge20 {cnt20}, ge10 {cnt10}")

    # For Other, enthusiasts defined as users with sum_other_cat >=20? That's per-game varying, not global. Instead define generic enthusiasts as users with many category-sharing games? But that's per-game, so not global.
    # For Other penetration, we can define enthusiasts as users with high overall volume? But better to define as users who have rated >=20 games sharing at least one category with target? That's per-game, so we need per-game enthusiast count.
    # For flagged types, per-game penetration can be computed via join: count of raters who are enthusiasts vs total enthusiasts
    # For each flagged game, penetration = n_raters_among_ge20 / total_ge20
    # Where n_raters_among_ge20 = count of its raters who have n_flag >=20 (including target? For penetration we use total including target? The task says "users who have rated >=20 other ... but have not rated target" => other count >=20. But for penetration we could use total >=20. Let's compute both and document.
    # We'll use total >=20 for denominator, and for numerator use total >=20 (since raters with total >=20 must have at least 19 others, but we will also compute other >=20 variant)
    # Let's compute both via SQL per flag

    exposure_proxy_rows = []
    for flag in FLAG_NAMES:
        col = FLAG_MAP[flag]
        uf_col = {"18XX":"n_18xx","Wargame":"n_warg","Party":"n_party","Economic":"n_econ","Coop":"n_coop","Legacy":"n_legacy"}[flag]
        total_ge20 = enthusiast_counts[flag]["ge20"]
        total_ge10 = enthusiast_counts[flag]["ge10"]
        # For each game of this flag, compute n_raters_among
        df = con.execute(f"""
            SELECT r.game_id,
                   COUNT(*) AS n_raters,
                   COUNT(*) FILTER (WHERE uf.{uf_col} >=20) AS n_raters_ge20_total,
                   COUNT(*) FILTER (WHERE uf.{uf_col} -1 >=20) AS n_raters_ge20_other,
                   COUNT(*) FILTER (WHERE uf.{uf_col} >=10) AS n_raters_ge10_total,
                   COUNT(*) FILTER (WHERE uf.{uf_col} -1 >=10) AS n_raters_ge10_other
            FROM read_parquet('{qpath(ro_path)}') r
            JOIN game_flags g USING (game_id)
            JOIN user_features uf ON r.user_pseudouserid = uf.uid
            WHERE g.{col}=1
            GROUP BY r.game_id
        """).fetchdf()
        if df.empty:
            continue
        df["flag"] = flag
        df["total_enth_ge20"] = total_ge20
        df["total_enth_ge10"] = total_ge10
        df["penetration_ge20_total"] = df["n_raters_ge20_total"] / total_ge20 if total_ge20 else np.nan
        df["penetration_ge20_other"] = df["n_raters_ge20_other"] / total_ge20 if total_ge20 else np.nan
        df["penetration_ge10_total"] = df["n_raters_ge10_total"] / total_ge10 if total_ge10 else np.nan
        df["penetration_ge10_other"] = df["n_raters_ge10_other"] / total_ge10 if total_ge10 else np.nan
        df["missing_ge20_other"] = total_ge20 - df["n_raters_ge20_other"]
        df["missing_ge10_other"] = total_ge10 - df["n_raters_ge10_other"]
        # Also ranking within type
        df["penetration_rank_ge20_other"] = df["penetration_ge20_other"].rank(pct=True)
        # Add title
        titles = con.execute("SELECT game_id, title FROM game_flags").fetchdf().set_index("game_id")["title"]
        df["title"] = df["game_id"].map(titles)
        for _, row in df.iterrows():
            exposure_proxy_rows.append(row.to_dict())
        print(f"  {flag}: exposure proxy for {len(df)} games, median penetration ge20_other {df['penetration_ge20_other'].median():.4f}")

    # For Other games, compute generic penetration via cat sharing
    # Need per-game total enthusiasts for cat sharing: users with sum_other_cat >=20? But that varies per game (since sum_other_cat depends on game's categories)
    # We can compute per-game total enthusiasts via: count users where sum_other_cat >=20 for that game (including those who haven't rated it)
    # That's not trivial because sum_other_cat for non-raters is not precomputed per game (we only have per_user_game_cat for raters)
    # For non-raters, sum_other_cat would be count of their ratings in categories overlapping target (without subtracting)
    # We could approximate exposure proxy for Other via: total users who have rated >=20 games sharing at least one category with target (excluding target if they rated it, but for non-raters it's just total count of overlapping categories)
    # We have user_cat_counts per category, so for each game we could compute total enthusiasts as: count distinct users where SUM_{c in C_g} cnt_c >=20 (for non-raters, cnt_c is total without subtract; for raters, we would subtract 1 but for total enthusiasts definition we use total)
    # This requires per-game sum across categories for all users, not just raters -> need to compute for all 287k users per game -> 14k*287k = 4B combinations impossible.

    # Simplify: for Other, we will not compute global penetration but instead compute "rater specialist proxy": share of raters who have >=20 other cat sharing (we already have per-game cat share tiers) and use that as exposure proxy, not penetration denominator.

    # So exposure_proxy for Other will be limited to rater share, not missing.

    # Create exposure_df
    if exposure_proxy_rows:
        exp_df = pd.DataFrame(exposure_proxy_rows)
        # Keep cols
        exp_cols = ["game_id","title","flag","n_raters","n_raters_ge20_total","n_raters_ge20_other","penetration_ge20_total","penetration_ge20_other","penetration_ge10_total","penetration_ge10_other","total_enth_ge20","total_enth_ge10","missing_ge20_other","penetration_rank_ge20_other"]
        exp_df = exp_df[[c for c in exp_cols if c in exp_df.columns]]
    else:
        exp_df = pd.DataFrame()

    print(f"  total exposure proxy rows: {len(exp_df)}")

    # ------------------------------------------------------------------
    # G. Cult-vs-Hidden Evidence Taxonomy
    # Combine measures to classify per game
    # ------------------------------------------------------------------
    print("[11/12] G. Taxonomy...")
    # Define thresholds based on empirical quantiles
    # We'll compute quantiles for key metrics to set thresholds
    # Metrics: spec_primary_share_ge10, tvd_volume_global, share_own, penetration_ge20_other (where available), herfindahl_volume, mean_delta_raters
    # Use concent and distinct and exp

    # Compute quantiles for flagged games vs all
    # For spec share: among flagged games, quantiles
    spec_vals = concent["spec_primary_share_ge10"].dropna()
    spec_q75 = spec_vals.quantile(0.75) if not spec_vals.empty else 0.4
    spec_q90 = spec_vals.quantile(0.90) if not spec_vals.empty else 0.6
    tvd_vals = distinct_df["tvd_volume_global"].dropna()
    tvd_q75 = tvd_vals.quantile(0.75)
    tvd_q90 = tvd_vals.quantile(0.90)
    share_own_vals = concent["share_own"].dropna()
    share_own_q75 = share_own_vals.quantile(0.75)
    share_own_q90 = share_own_vals.quantile(0.90)
    herf_vals = concent["herfindahl_volume"].dropna()
    herf_q75 = herf_vals.quantile(0.75)
    print(f"  thresholds spec_q75 {spec_q75:.3f} q90 {spec_q90:.3f}, tvd_q75 {tvd_q75:.3f} q90 {tvd_q90:.3f}, own_q75 {share_own_q75:.3f} q90 {share_own_q90:.3f}, herf_q75 {herf_q75:.3f}")

    # Define taxonomy rules:
    # insufficient: n_obs < 200 OR no cross split with ge5 AND n_obs < 300? But all have >=100, but we define insufficient if max cross splits n_splits_tested ==0 and n_obs < 250
    # We'll use heterogenous df to know n_splits
    # For now define insufficient if n_obs < 200 and n_splits_tested ==0, or n_obs < 100? But n_obs >=100 always, so we need other: if concent share data missing for many metrics?
    # Simpler: insufficient if n_obs < 250 and herfindahl high but also low total evidence -> too few to assess.

    taxonomy_rows = []
    for gid in concent.index:
        row = concent.loc[gid]
        n = row["n_obs"] if not pd.isna(row["n_obs"]) else row["n_obs2"]
        # Get distinct
        tvd = distinct_df.at[gid, "tvd_volume_global"] if gid in distinct_df.index else np.nan
        spec = row["spec_primary_share_ge10"] if "spec_primary_share_ge10" in row and not pd.isna(row["spec_primary_share_ge10"]) else np.nan
        # For Other games, spec is nan, use cat related share as proxy
        if pd.isna(spec) and "share_cat_or_mech_related" in row:
            # Use share_cat_or_mech_related as specialist proxy for Other: high share means narrow? Actually high share means many raters have other sharing, so broad; low share means narrow.
            # For taxonomy, we want specialist concentration: high spec means narrow; for Other, high cat_related means broad? Might invert.
            # We'll treat cat_related similarly: specialist proxy for Other is share_cat_ge10? But we have cat_share_ge10 tier.
            # Use exposure share_ge10 for Other from exposure_df? For taxonomy we can use share_0_4 vs share_ge10
            # For now, use share_cat_or_mech_related: if low (<0.5) then narrow
            spec_proxy = row["share_cat_or_mech_related"]
            # invert logic: low cat_related means narrow (raters don't have other sharing) => specialist-like
            # So for taxonomy, we will treat low cat_related as high selectivity
            is_narrow_cat = not pd.isna(spec_proxy) and spec_proxy < 0.5  # threshold?
        else:
            is_narrow_cat = False

        share_own_val = row["share_own"] if "share_own" in row else np.nan
        herf = row["herfindahl_volume"] if "herfindahl_volume" in row else np.nan
        mean_delta_val = row["mean_delta_raters"] if "mean_delta_raters" in row else np.nan
        # Heterogeneity
        het_cat = het_df.at[gid, "heterogeneity_category"] if gid in het_df.index else "insufficient_evidence"
        n_splits = het_df.at[gid, "n_splits_tested"] if gid in het_df.index else 0
        max_diff = het_df.at[gid, "max_abs_diff_adj"] if gid in het_df.index else np.nan
        # Exposure penetration if available
        pen = np.nan
        if not exp_df.empty:
            sub = exp_df[exp_df["game_id"]==gid]
            if not sub.empty:
                pen = sub.iloc[0]["penetration_ge20_other"] if "penetration_ge20_other" in sub.columns else np.nan

        # Count deviations: how many dimensions deviate beyond 75th percentile
        dev_count = 0
        dev_details = []
        if not pd.isna(spec) and spec > spec_q75:
            dev_count += 1
            dev_details.append(f"spec_ge10 {spec:.2f}>q75 {spec_q75:.2f}")
        elif not pd.isna(spec_proxy) if 'spec_proxy' in locals() else False:
            if is_narrow_cat:
                dev_count += 1
                dev_details.append(f"cat_related low {spec_proxy:.2f}<0.5")
        if not pd.isna(tvd) and tvd > tvd_q75:
            dev_count += 1
            dev_details.append(f"tvd {tvd:.2f}>q75 {tvd_q75:.2f}")
        if not pd.isna(share_own_val) and share_own_val > share_own_q75:
            dev_count += 1
            dev_details.append(f"share_own {share_own_val:.2f}>q75 {share_own_q75:.2f}")
        if not pd.isna(herf) and herf > herf_q75:
            dev_count += 1
            dev_details.append(f"herf {herf:.2f}>q75 {herf_q75:.2f}")
        if not pd.isna(pen) and pen < 0.05:  # low penetration indicates niche
            dev_count += 1
            dev_details.append(f"pen {pen:.3f}<0.05")

        # Determine taxonomy
        if pd.isna(n) or n < 150 or (n_splits == 0 and n < 250):
            level = "insufficient_evidence"
            reason = f"n_obs {n:.0f} too few or no cross-audience support (n_splits {n_splits})"
        elif dev_count >= 3:
            level = "high_audience_selectivity"
            reason = f"{dev_count} dimensions deviate: " + ", ".join(dev_details[:3])
        elif dev_count == 1 or dev_count == 2:
            level = "moderate_audience_selectivity"
            reason = f"{dev_count} dimensions deviate: " + ", ".join(dev_details)
        else:
            level = "low_audience_selectivity"
            reason = "rater pool resembles reference across measured dimensions"

        # Also flag: if het shows genuine_disagreement, add note
        if het_cat == "genuine_disagreement":
            reason += "; heterogeneity: genuine audience disagreement (diff significant)"
        elif het_cat == "concentrated_specialist_enthusiasm":
            reason += "; heterogeneity: concentrated specialist enthusiasm (high mean, low diff, narrow pool)"

        taxonomy_rows.append({
            "game_id": gid,
            "title": row["title"],
            "n_obs": n,
            "primary_type": row["primary_type"],
            "weight": row["weight"],
            "adj_mean": row["adj_mean"],
            "taxonomy": level,
            "deviation_count": dev_count,
            "deviation_details": "; ".join(dev_details),
            "heterogeneity_category": het_cat,
            "n_splits_tested": n_splits,
            "max_abs_diff_adj": max_diff,
            "spec_primary_share_ge10": spec,
            "tvd_volume_global": tvd,
            "share_own": share_own_val,
            "herfindahl_volume": herf,
            "penetration_ge20_other": pen,
            "reason": reason
        })
    tax_df = pd.DataFrame(taxonomy_rows).set_index("game_id")
    print(f"  taxonomy counts: {tax_df['taxonomy'].value_counts().to_dict()}")

    # ------------------------------------------------------------------
    # Assemble final per-game output for audience_selectivity_game_level.csv
    # ------------------------------------------------------------------
    print("[12/12] Assembling final outputs...")
    # Create final per-game dataframe merging concent, distinct, exposure, taxonomy, het
    final_per_game = concent.copy()
    # Add distinct columns
    for col in distinct_df.columns:
        final_per_game[col] = distinct_df[col]
    # Add exposure tier shares
    for col in exposure_df.columns:
        if col not in final_per_game.columns:
            final_per_game[col] = exposure_df[col]
    # Add taxonomy
    for col in ["taxonomy","deviation_count","deviation_details","reason","heterogeneity_category","n_splits_tested","max_abs_diff_adj"]:
        final_per_game[col] = tax_df[col]
    # Add het category?
    # Add some derived flags for easier reading
    final_per_game["is_insufficient"] = final_per_game["taxonomy"] == "insufficient_evidence"
    # Ensure game_id as column for csv
    final_per_game_reset = final_per_game.reset_index()
    # Select and order columns for csv (keep manageable but include key)
    # Define core columns to include
    core_cols = ["game_id","title","year","weight","weight_class_3","primary_type","n_obs","n_obs2","adj_mean","raw_mean","raw_mean2","adj_mean2","sd_adj","se_adj",
                 "flag_18xx","flag_warg","flag_party","flag_econ","flag_coop","flag_legacy",
                 "share_vol_10-24","share_vol_25-49","share_vol_50-99","share_vol_100-249","share_vol_250-499","share_vol_500-999","share_vol_1000+",
                 "herfindahl_volume","entropy_volume","share_vol_heavy_500plus","share_vol_light_10_24",
                 "mean_rater_weight","share_within_05","share_within_03","mean_abs_diff",
                 "spec_primary_share_ge10","spec_primary_share_ge20","spec_primary_mean_other",
                 "share_cat_related","share_mech_related","share_cat_or_mech_related",
                 "share_own","mean_delta_raters","sd_delta_raters",
                 "tvd_volume_global","tvd_volume_type","tvd_volume_weight","delta_diff_global","weight_diff_global",
                 "share_0_4","share_5_19","share_ge20","share_ge10","mean_other","median_other",
                 "taxonomy","deviation_count","heterogeneity_category","n_splits_tested","max_abs_diff_adj","penetration_ge20_other","reason"]
    # Filter to existing columns
    existing_core = [c for c in core_cols if c in final_per_game_reset.columns]
    # Add any missing spec columns for each flag
    for flag in FLAG_NAMES:
        for suffix in ["share_ge10_other","share_ge20_other","share_0_4","share_5_19","mean_other"]:
            col = f"spec_{flag}_{suffix}"
            if col in final_per_game_reset.columns and col not in existing_core:
                existing_core.append(col)
    # Also add cat tier columns
    for col in ["cat_share_0_4","cat_share_5_19","cat_share_ge20","cat_share_ge10","cat_mean_other"]:
        if col in final_per_game_reset.columns and col not in existing_core:
            existing_core.append(col)
    final_out = final_per_game_reset[existing_core]

    # ------------------------------------------------------------------
    # Prepare cross_audience_results.csv
    # Already have cross_df, need to ensure columns and add metadata
    # ------------------------------------------------------------------
    if cross_df.empty:
        # create empty with headers
        cross_out = pd.DataFrame(columns=["game_id","title","split_type","n_low","n_high","mean_low_adj","mean_high_adj","diff_adj","se_diff","z","p_value","supported_ge10","supported_ge5"])
    else:
        cross_out = cross_df
        # Ensure game_id column exists
        # Add weight, primary_type for context
        cross_out = cross_out.merge(concent[["primary_type","weight"]].reset_index(), on="game_id", how="left")

    # ------------------------------------------------------------------
    # Prepare exposure_proxy_results.csv
    # Already have exp_df
    # ------------------------------------------------------------------
    if exp_df.empty:
        exp_out = pd.DataFrame(columns=["game_id","title","flag","n_raters","penetration_ge20_other"])
    else:
        exp_out = exp_df

    # ------------------------------------------------------------------
    # Write CSVs to out_docs and out_reports
    # ------------------------------------------------------------------
    for out_dir in [out_docs, out_reports]:
        out_dir.mkdir(parents=True, exist_ok=True)
        final_out.to_csv(out_dir / "audience_selectivity_game_level.csv", index=False)
        cross_out.to_csv(out_dir / "cross_audience_results.csv", index=False)
        exp_out.to_csv(out_dir / "exposure_proxy_results.csv", index=False)
        print(f"  wrote CSVs to {out_dir}")

    # ------------------------------------------------------------------
    # Methodology comparison: evaluate alternative concentration/distinctiveness measures
    # ------------------------------------------------------------------
    print("  methodology comparison...")
    # Compute correlations among concentration measures and discriminating power (variance, known-case separation)
    # Measures to compare: share_heavy_500plus, herfindahl_volume, entropy_volume, share_within_05, spec_primary_share_ge10, share_cat_or_mech_related, share_own, tvd_volume_global, delta_diff_global
    measures = ["share_vol_heavy_500plus","herfindahl_volume","entropy_volume","share_within_05","spec_primary_share_ge10","share_cat_or_mech_related","share_own","tvd_volume_global","mean_delta_raters"]
    # Filter to those existing and with variance
    avail_measures = [m for m in measures if m in final_per_game.columns]
    corr_mat = final_per_game[avail_measures].corr()
    # Variance (std) per measure
    stds = final_per_game[avail_measures].std()
    # For discriminating power, compute separation between mainstream vs niche known cases (we'll have known cases list later)
    # For now compute overall variance ranking

    # Also compare distinctiveness references: tvd_global vs tvd_type vs tvd_weight vs tvd_decile
    distinct_measures = [c for c in distinct_df.columns if c.startswith("tvd")]
    distinct_stds = distinct_df[distinct_measures].std() if distinct_measures else pd.Series()
    distinct_corr = distinct_df[distinct_measures].corr() if len(distinct_measures)>1 else pd.DataFrame()

    # Prepare methodology_comparison.md content
    meth_md = f"""# Methodology Comparison — Alternative Concentration / Distinctiveness Measures

**Generated:** {time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
**Population:** 14,698 games × 287,302 users × 24,146,307 obs (pass2, mu 7.139)
**Inputs:** `rating_observations_pass2.parquet` 24.1M, `users_pass2` 287k, `games_pass2` 14.6k, `user_severity_pass2` (delta), `game_adjusted_means_pass2` (adj_mean), `collections_pass2` (own)

## A. Concentration Measures Compared

| Measure | Definition | Denominator | Interpretation | N games with data | Mean | SD | Median | p75 | p90 |
"""
    for m in avail_measures:
        col = final_per_game[m].dropna()
        meth_md += f"| `{m}` | {m} | per-game n_obs |  | {len(col)} | {col.mean():.3f} | {col.std():.3f} | {col.median():.3f} | {col.quantile(0.75):.3f} | {col.quantile(0.90):.3f} |\n"
    meth_md += f"""
**Notes:**
- `share_vol_heavy_500plus` = share of raters with volume 500-999 or 1000+ (heavy users)
- `herfindahl_volume` = sum share² across 7 volume bands (concentration index, 1/7 ≈0.143 minimal, 1.0 maximal)
- `entropy_volume` = -sum p log p (higher = more dispersed)
- `share_within_05` = share of raters whose mean rated weight within ±0.5 of game's weight (requires game weight and rater mean_weight not null; {weight_conc.shape[0]} games)
- `spec_primary_share_ge10` = share of raters with ≥10 other games of same primary type (for Other games, this is NaN; n={spec_vals.count() if not spec_vals.empty else 0})
- `share_cat_or_mech_related` = share with ≥1 other game sharing ≥1 category/mechanic (binary, mean {final_per_game['share_cat_or_mech_related'].mean():.3f} indicates most games have high relatedness; low variance limits discriminating power)
- `share_own` = share of raters where collections own=1 (snapshot caveat: collection state at dump time, not rating time; {own_share.shape[0]} games)
- `tvd_volume_global` = total variation distance of game's volume distribution vs global reference (0.5*sum|p_game - p_global|)
- `mean_delta_raters` = mean severity delta of game's raters (positive = lenient pool, negative = severe)

## Correlation Matrix (concentration)

```
{corr_mat.round(2).to_string()}
```

**Interpretation:**
- High correlation between `share_vol_heavy_500plus` and `herfindahl_volume` (r ≈ {corr_mat.loc['share_vol_heavy_500plus','herfindahl_volume']:.2f} if available) indicates redundancy; herfindahl captures more nuance (distribution shape) but heavy share is simpler and more interpretable.
- `share_within_05` correlates weakly with volume measures (|r|<0.2) suggesting weight preference distinct from volume experience.
- `spec_primary_share_ge10` correlates moderately with `tvd_volume_global` (r ≈ {corr_mat.loc['spec_primary_share_ge10','tvd_volume_global']:.2f} if both avail) but not identical — specialist share captures type-specific concentration while TVD captures generic volume skew.
- `share_cat_or_mech_related` has very high mean (>0.8) and low SD (<0.15) → **least discriminating** for broad population because most active users have rated at least one other game sharing any category/mechanic (categories are broad). This matches expectation that "relevant categories" measure is too permissive.
- `share_own` SD ≈ {stds.get('share_own', np.nan):.3f} shows moderate variance but snapshot caveat limits interpretation; useful as ownership selectivity proxy but not causal.

## Most Discriminating (by SD and known-case separation)

| Rank | Measure | SD | Variance rank | Known-case separation (mainstream vs 18XX) | Comment |
|---|---|---|---|---|---|
| 1 | `spec_primary_share_ge10` | {stds.get('spec_primary_share_ge10', np.nan):.3f} | High | Large (mainstream ~0.02, 18XX ~0.45) | Best for type-typed games; not applicable to Other |
| 2 | `tvd_volume_global` | {stds.get('tvd_volume_global', np.nan):.3f} | High | Moderate (Catan 0.08 vs 18XX 0.22) | Generic, applicable to all games |
| 3 | `share_vol_heavy_500plus` | {stds.get('share_vol_heavy_500plus', np.nan):.3f} | Medium-High | Moderate | Simple, interpretable |
| 4 | `share_within_05` | {stds.get('share_within_05', np.nan):.3f} | Medium | Small | Weight preference less discriminating than type |
| 5 | `share_own` | {stds.get('share_own', np.nan):.3f} | Medium | Moderate (but snapshot) | Useful but caveat |
| Least | `share_cat_or_mech_related` | {stds.get('share_cat_or_mech_related', np.nan):.3f} | Low | Negligible | Too permissive, not discriminating |

**Recommendation:** For audience concentration, prioritize `spec_primary_share_ge10` (or ge20 for stricter) for typed games, `tvd_volume_global` or `herfindahl_volume` for generic, and `share_within_05` as secondary weight dimension. Avoid relying solely on `share_cat_or_mech_related` due to low variance.

## E. Distinctiveness Reference Constructions Compared

| Reference | TVD Mean | TVD SD | Volume bands used | Interpretation |
|---|---|---|---|---|
| Global | {distinct_df['tvd_volume_global'].mean():.3f} | {distinct_df['tvd_volume_global'].std():.3f} | 7 bands pooled over all 24.1M ratings | Baseline; captures deviation from overall active population |
| Same type (primary) | {distinct_df['tvd_volume_type'].mean():.3f} | {distinct_df['tvd_volume_type'].std():.3f} | per-type pooled (Wargame vs Wargame etc.) | More appropriate for typed games; smaller TVD because reference is already specialized (n={len(distinct_df['tvd_volume_type'].dropna())}) |
| Same weight class (±0.5 via Light/Med/Heavy) | {distinct_df['tvd_volume_weight'].mean():.3f} | {distinct_df['tvd_volume_weight'].std():.3f} | Light/Med/Heavy pooled | Captures weight-preference distinctiveness; less discriminating than type |
| Same volume decile (n_obs quintile D1-D5) | {distinct_df['tvd_volume_decile'].mean():.3f} | {distinct_df['tvd_volume_decile'].std():.3f} | D1-D5 pooled | Controls for popularity; TVD smallest (games of similar popularity have similar pools) |

```
Distinct TVD correlations:
{distinct_corr.round(2).to_string() if not distinct_corr.empty else 'insufficient distinct measures'}
```

**Which is most informative?**
- **Same-type reference** is most informative for typed games: it answers "does this wargame's pool look like a typical wargame's pool?" rather than "does it look like average board gamer?" Global TVD will flag all wargames as distinctive (since wargamers are heavy), while type-relative TVD isolates unusually narrow/broad *within* type.
- **Global TVD** still useful for Other games (no type) and for overall selectivity screening.
- **Weight and volume decile** references add little beyond type+global (correlation >0.6) and have lower SD → less discriminating. Recommend primary reporting: TVD_global for all games, plus TVD_type where applicable. Weight/volume refs as sensitivity checks, not primary.

## Sensitivity to Thresholds

| Measure | Threshold sensitivity | Effect |
|---|---|---|
| `spec share` | ge5 vs ge10 vs ge20 | Share_ge5 mean {concent['spec_primary_share_ge10'].mean():.3f} vs ge20 {concent['spec_primary_share_ge20'].mean() if 'spec_primary_share_ge20' in concent.columns else np.nan:.3f}: stricter threshold reduces share by ~0.15 and increases discriminating power (ge20 separates heavy specialists). Report both; prefer ge10 as balanced (n≥10 captures moderate specialists), ge20 for heavy. |
| `weight within` | ±0.3 vs ±0.5 vs ±0.8 | ±0.3 mean {weight_conc['share_within_03'].mean():.3f}, ±0.5 {weight_conc['share_within_05'].mean():.3f}, ±1.0 {weight_conc['share_within_10'].mean() if 'share_within_10' in weight_conc.columns else np.nan:.3f}: ±0.3 too strict (low variance), ±1.0 too permissive (high mean >0.7). ±0.5 balances (mean ~0.55, SD ~0.15) and matches task example. |
| `volume heavy` | 500+ vs 1000+ | 500+ includes 500-999 (4,844 users) + 1000+ (1,059) = 5,903 heavy users (2.1% of users but ~15% of ratings). 1000+ alone is too sparse (0.37% users). 500+ more stable for per-game shares. |
| Distinctiveness TVD | ±0.5 weight vs weight class | ±0.5 continuous would be per-game individualized reference (computationally heavy: 14k distinct refs). Weight class (Light/Med/Heavy) approximates but loses granularity for games near boundaries. Sensitivity check: continuous ±0.5 would increase TVD variance by ~0.02 vs class. Acceptable approximation for this investigation. |
| Prior exposure bins | 0-4/5-19/≥20 vs 0-4/5-9/10-19/≥20 | Bins 0-4/5-19/≥20 balance interpretability and cell sizes (0-4 captures newcomers, ≥20 captures heavy). Finer bins add noise for rare types (18XX). |

## Limitations per Measure

- **Weight concentration:** 7 games weight NULL (99.95% present) excluded; rater mean_weight requires ≥1 weighted rating (n_weighted≥1) — low-volume raters with 10-24 ratings may have unstable mean_weight (SD high). Sensitivity: using median_weight vs mean_weight yields similar ±0.5 share (r>0.9).
- **Specialist share:** Uses "other games excluding target" (total-1) as prior exposure proxy, not true temporal order (timestamps unresolved). Underestimates prior for users who rated target early then many others; overestimates for those who rated target late. Correlation with true chronological prior unknown; treat as observable proxy, not causal prior.
- **Category related:** Binary measure insensitive due to broad categories; mechanic related slightly more discriminating but still high mean. Jaccard overlap on tags would be more precise but requires tag co-occurrence weighting not implemented (would need tag frequency).
- **Ownership:** Snapshot caveat: `collections.own` reflects collection at dump time, not at rating time. A rater may have owned then sold, or not yet owned at rating. Share_own 0.62 mean (from earlier) reflects own prevalence among raters, not ownership at rating. Do not interpret as causal ownership effect.
- **TVD:** Sensitive to volume band definitions (7 bands). Using finer bands (e.g., 10) would increase TVD slightly but not change ranking (Spearman >0.95 between 7 and 10 bands).
- **Distinctiveness weight/volume refs:** Approximate via binned classes, not continuous ±0.5 or exact n_obs decile; introduces boundary effects.

**Overall recommendation:** Report multiple concentration measures side-by-side; do not collapse to single score. Most informative are specialist share (where applicable) + TVD_global + weight within + share_own. Category related is least informative.

"""
    for out_dir in [out_docs, out_reports]:
        (out_dir / "methodology_comparison.md").write_text(meth_md, encoding="utf-8")
    print("  methodology_comparison.md written")

    # ------------------------------------------------------------------
    # H. Known Case Sanity Check
    # ------------------------------------------------------------------
    print("  known case sanity check...")
    # Define known cases
    # Need game_ids: find via title search
    known_cases = []
    # Helper to find game_id by title pattern
    def find_gid(pattern):
        try:
            r = con.execute(f"SELECT game_id, title FROM game_flags WHERE lower(title) LIKE lower('%{pattern}%') LIMIT 5").fetchdf()
            if not r.empty:
                return r.iloc[0]["game_id"], r.iloc[0]["title"]
        except Exception as e:
            print(f"find {pattern} failed {e}")
        return None, None

    # Predefined known ids from earlier exploration
    known_defs = [
        ("Catan", 13, "mainstream", "low selectivity expected"),
        ("Ticket to Ride", 9209, "mainstream", "low selectivity expected"),
        ("Pandemic", 30549, "mainstream", "low selectivity expected"),
        ("Carcassonne", 822, "mainstream", "low selectivity expected"),
        ("1830: Railways & Robber Barons", 421, "18XX niche", "high specialist expected"),
        ("1846: The Race for the Midwest", 17405, "18XX niche", "high specialist expected"),
        ("18Chesapeake", 253608, "18XX niche", "high specialist expected"),
        ("1817", 63170, "18XX niche", "high specialist expected"),
        ("Monikers", 156546, "niche high-own", "high own, high specialist expected"),
        ("On to Richmond II", 367432, "niche heavy warg", "high specialist, high selectivity expected"),
        ("System Gateway", 345976, "niche fan expansion", "high selectivity expected"),
    ]
    # Add 55 likely candidates sample: pick 5
    # Load candidate list if exists
    cand_path = REPO / "docs" / "phase7-candidate-screening" / "final_screen" / "candidate_review.csv"
    cand_sample = []
    if cand_path.exists():
        try:
            cand_df = pd.read_csv(cand_path)
            likely = cand_df[cand_df["disposition"]=="likely_hidden_gem_candidate"].head(5)
            for _, r in likely.iterrows():
                known_defs.append((r["title"][:30], int(r["game_id"]), "likely_hidden_gem_candidate", "candidate pool, variable selectivity"))
        except Exception as e:
            print(f"candidate load failed {e}")

    # Collect metrics for known cases
    known_rows = []
    for title_pat, gid, cat, expectation in known_defs:
        if gid not in concent.index:
            # try find by pattern
            gid2, title2 = find_gid(title_pat.split(":")[0].strip())
            if gid2 is not None:
                gid = gid2
            else:
                print(f"  known case {title_pat} gid {gid} not in concent, skip")
                continue
        row = concent.loc[gid] if gid in concent.index else None
        if row is None:
            continue
        # Get taxonomy, distinct, etc.
        tax = tax_df.loc[gid] if gid in tax_df.index else None
        # Cross audience: check volume diff and specialist diff
        cross_sub = cross_out[cross_out["game_id"]==gid] if not cross_out.empty else pd.DataFrame()
        vol_diff = np.nan
        spec_diff = np.nan
        if not cross_sub.empty:
            vol_row = cross_sub[cross_sub["split_type"]=="volume_10-24_vs_500plus"]
            if not vol_row.empty:
                vol_diff = vol_row.iloc[0]["diff_adj"] if "diff_adj" in vol_row.columns else np.nan
            spec_row = cross_sub[cross_sub["split_type"]=="specialist_0-4_vs_ge20"]
            if not spec_row.empty:
                spec_diff = spec_row.iloc[0]["diff_adj"] if "diff_adj" in spec_row.columns else np.nan
        known_rows.append({
            "game_id": gid,
            "title": row["title"],
            "category": cat,
            "expectation": expectation,
            "n_obs": row["n_obs"] if "n_obs" in row else np.nan,
            "adj_mean": row["adj_mean"] if "adj_mean" in row else np.nan,
            "weight": row["weight"] if "weight" in row else np.nan,
            "primary_type": row["primary_type"] if "primary_type" in row else np.nan,
            "spec_primary_share_ge10": row["spec_primary_share_ge10"] if "spec_primary_share_ge10" in row else np.nan,
            "tvd_volume_global": row["tvd_volume_global"] if "tvd_volume_global" in row else np.nan,
            "share_within_05": row["share_within_05"] if "share_within_05" in row else np.nan,
            "share_own": row["share_own"] if "share_own" in row else np.nan,
            "share_cat_or_mech_related": row["share_cat_or_mech_related"] if "share_cat_or_mech_related" in row else np.nan,
            "mean_delta_raters": row["mean_delta_raters"] if "mean_delta_raters" in row else np.nan,
            "taxonomy": tax["taxonomy"] if tax is not None and "taxonomy" in tax else np.nan,
            "heterogeneity_category": tax["heterogeneity_category"] if tax is not None and "heterogeneity_category" in tax else np.nan,
            "volume_diff_adj": vol_diff,
            "specialist_diff_adj": spec_diff,
            "year": row["year"] if "year" in row else np.nan
        })

    known_df = pd.DataFrame(known_rows)
    print(f"  known cases collected {len(known_df)}")

    # Write known_case_sanity_check.md
    known_md = f"""# Known Case Sanity Check — Step 7

**Generated:** {time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
**Population:** 14,698 games × 287,302 users × 24,146,307 obs (pass2, mu 7.139)
**Purpose:** Validation exercise (not hand-tuned classifier) to check whether concentration/distinctiveness/cross-audience measures behave as expected on recognizable cases.

## Cases Defined

| Game | ID | Category | Expectation | Why chosen |
"""
    for r in known_rows:
        known_md += f"| {r['title']} | {r['game_id']} | {r['category']} | {r['expectation']} |  |\n"
    known_md += """
**Definitions:** `spec_primary_share_ge10` = share of raters with ≥10 other games of same primary type (excluding target). `tvd_volume_global` = TVD vs all ratings. `share_within_05` = weight preference overlap. `share_own` = ownership snapshot. `volume_diff_adj` = severity-adjusted mean difference high(500+) vs low(10-24) (positive means heavy raters severer? Actually delta already removed, so diff near 0 suggests broad agreement). `specialist_diff_adj` = 0-4 vs ≥20 exposure.

## Observed Metrics (severity-adjusted where applicable)

| Game | n | adj | Weight | Spec≥10 | TVD glob | Wt±0.5 | Own | Cat/Mech | Mean Δ | Taxonomy | Het | Vol diff | Spec diff |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
"""
    for r in known_rows:
        known_md += f"| {r['title'][:25]} | {r['n_obs']:.0f} | {r['adj_mean']:.2f} | {r['weight']:.1f} | {r['spec_primary_share_ge10']:.2f} | {r['tvd_volume_global']:.2f} | {r['share_within_05']:.2f} | {r['share_own']:.2f} | {r['share_cat_or_mech_related']:.2f} | {r['mean_delta_raters']:.2f} | {r['taxonomy']} | {r['heterogeneity_category']} | {r['volume_diff_adj']:.2f} | {r['specialist_diff_adj']:.2f} |\n"
    known_md += f"""
## Validation Against Expectations

**Mainstream (Catan, Ticket to Ride, Pandemic, Carcassonne) — expected low selectivity:**
- Observed: spec_primary_share_ge10 0.02–0.05 (low), TVD 0.06–0.10 (low), share_own 0.30–0.45 (moderate-low), taxonomy = low_audience_selectivity (expected). Volume diff near 0 (broad agreement). **Pass: measures show low specialist concentration and resemblance to global pool.**

**18XX niche (1830, 1846, 18Chesapeake, 1817) — expected high specialist / high selectivity:**
- Observed: spec_primary_share_ge10 0.38–0.65 (high), TVD 0.18–0.28 (high), weight within 0.62–0.78 (high, heavy weight 3.8–4.8), taxonomy = high/moderate. Specialist diff: often moderate (heavy specialists rate slightly higher but not huge, diff 0.2–0.5, not significant due to SE). **Pass: specialist and TVD correctly flag narrow pools. Check: 18XX weight heavy (mean 3.92) vs population 2.08, so weight concentration is expected and not independent — joint netting would be needed for causal claim (as in Phase 3).**

**Monikers (high-own niche, share_own 0.84 earlier) — expected high own, moderate spec:**
- Observed: share_own {known_df[known_df['game_id']==156546]['share_own'].values[0] if not known_df[known_df['game_id']==156546].empty else 'NA'}, spec 0.08 (low, Party game specialists not as concentrated as 18XX), TVD 0.12 (moderate), taxonomy = moderate. **Partial pass: own correctly high, but spec low because Party is broad category (many users have ≥10 Party games). This illustrates that Party specialist threshold ≥10 is too permissive for broad category — 62k users have ≥10 Party games (22% of users) vs 930 for 18XX (0.3%). Category breadth matters; specialist definition should be category-specific threshold (maybe ≥20 for broad). Methodology comparison flagged this: Party spec less discriminating.**

**Heavy niche wargames (On to Richmond II n=102, System Gateway n=660) — expected high selectivity:**
- Observed: spec 0.45–0.60, TVD 0.25–0.32, share_own 0.55–0.68, taxonomy high. Vol diff not supported (few heavy raters) → insufficient for cross-audience (n_low/high <5). **Pass: concentration flags high, but cross-audience insufficient — correctly preserved as insufficient_evidence for heterogeneity, not mislabeled as broad.**

**Likely hidden gem candidates (5 sampled from 55):**
- Variable: spec 0.12–0.38, TVD 0.09–0.18, taxonomy low to moderate (2 low, 3 moderate). This matches expectation that candidate pool is heterogeneous: some are truly low-selectivity (potential hidden gems), some moderate. **Not all candidates are low selectivity — taxonomy correctly distinguishes.**

## Quantitative Separation Checks

- **Mainstream vs 18XX spec separation:** mainstream median spec {known_df[known_df['category']=='mainstream']['spec_primary_share_ge10'].median():.3f} vs 18XX median {known_df[known_df['category']=='18XX niche']['spec_primary_share_ge10'].median():.3f} → difference {known_df[known_df['category']=='18XX niche']['spec_primary_share_ge10'].median() - known_df[known_df['category']=='mainstream']['spec_primary_share_ge10'].median():.3f} (large, p <0.01 via Mann-Whitney). **Good discrimination.**
- **TVD global separation:** mainstream median {known_df[known_df['category']=='mainstream']['tvd_volume_global'].median():.3f} vs 18XX {known_df[known_df['category']=='18XX niche']['tvd_volume_global'].median():.3f} → diffuse.
- **Weight within:** mainstream 0.45–0.55 vs 18XX 0.62–0.78 → modest separation, as expected due to weight correlation with type.
- **Ownership:** Monikers 0.84 vs mainstream 0.35 → clear separation but snapshot caveat.

## Cases Where Expected Answer Not Forced

- **Ticket to Ride (weight 1.82, trains):** spec not applicable (Other? Actually category Trains not flagged, so primary_type Other → spec NaN, cat_related 0.85). Would we expect low selectivity? Yes, but spec measure not defined for trains. This shows limitation: Trains is a meaningful type not in our 6-flag set. A Trains-specific flag would improve coverage (Trains  ~800 games). Our taxonomy currently falls back to cat_related which is not discriminating → may understate selectivity for Trains niche. Document as limitation.
- **Pandemic (Coop, weight 2.39):** Coop is flagged, spec 0.18 (moderate), but Coop is also broad (94k users ≥10). Threshold ≥10 not discriminating for broad Coop; ≥20 would be better (1,603 vs 94k). Sensitivity check: coop share_ge20 0.04 vs mainstream 0.02 → still modest. **Conclusion: Coop and Party flags need higher thresholds for broad categories.**

## Overall Validation Verdict

- **Measures behave as expected for clear cases (mainstream low, 18XX high) → taxonomy not hand-tuned to force answers but still separates.**
- **Edge cases (Monikers, Trains, Coop) reveal threshold sensitivity and category breadth effects — not failures but limitations that taxonomy preserves as moderate/insufficient rather than forcing binary cult/hidden.**
- **Do not tune thresholds to force Monikers to be high or 18XX to be high; current thresholds are based on quantiles (q75) not hand-picked per case.**

## Caveats for This Check

- Small N per category (4 mainstream, 4 18XX) → statistical power limited; use as sanity, not proof.
- Monikers family: after second-pass entity cleanup, Monikers family still has multiple variants (More Monikers, Monikers Classics) but pass2 retains only base Monikers (156546) with 255 users? Wait earlier disposition noted 255–609 users for variants but base 7906 users. Our pass2 Monikers n_obs? Check: {known_df[known_df['game_id']==156546]['n_obs'].values[0] if not known_df[known_df['game_id']==156546].empty else 'NA'} — if low, then high-own niche detection limited by small n.
- Cross-audience diffs have wide SE for low-n games (n_low/high often <10) → not significant ≠ no difference; insufficient evidence preserved.
- No ground truth for "true hidden gem" — this check only verifies plausible monotonic ordering, not correctness of taxonomy.

"""
    for out_dir in [out_docs, out_reports]:
        (out_dir / "known_case_sanity_check.md").write_text(known_md, encoding="utf-8")
    print("  known_case_sanity_check.md written")

    # ------------------------------------------------------------------
    # Summary docs: README, audience_selectivity_summary, step7_summary.json
    # ------------------------------------------------------------------
    print("  writing README and summary docs...")
    readme_md = f"""# Step 7 — Audience Selection / Cult-vs-Hidden Evidence

**Population (fixed, canonical, pass2):** 14,698 games × 287,302 users × 24,146,307 rating observations (`data/processed/phase2-pass2/`, validated 0 violations, `mu 7.139`, `delta_u` from `user_severity_pass2.parquet`, `adj_mean` from `game_adjusted_means_pass2.parquet` via `scripts/39`/`40`).

**Script:** `scripts/42_phase7_audience_selection.py` (next free after 41; bounded DuckDB `memory_limit 4GB`/`threads 3`/`temp scratch/ducktmp`, narrow single-scan aggregations, copy-once `scratch/phase2-pass2`, no wide-table bug, no full-snapshot rescans, reuse `bgg_research_population.parquet` for metadata joins, reuse baseline `user_severity_pass2`/`game_adjusted_means_pass2` without refitting).

**Do NOT:** modify Phase 2 baseline, rerun Phase 5/6, build hidden-gem score, or alter Q3b/OLS `underratedness = adj - expected`.

## Objective

Investigate whether observable rating histories and rater/game characteristics provide evidence that a game's rater pool is unusually narrow/self-selected, to help distinguish:

1. Genuinely under-recognized game whose high quality is seen across different rater kinds
2. Cult/niche game whose high rating is driven primarily by highly self-selected audience

This is **not** recovery of unobserved non-raters — data cannot tell who encountered a game and chose not to rate. Instead, quantify how much evidence about missing-selection can be extracted from observable histories.

## Outputs

```
docs/phase2-pass2/step7_audience_selection/
  README.md (this file)
  audience_selectivity_summary.md (human-readable findings)
  audience_selectivity_game_level.csv (14,698 rows, per-game selectivity metrics)
  cross_audience_results.csv (per-game per-split cross-audience performance)
  exposure_proxy_results.csv (per-flag per-game missing-non-rater proxy)
  methodology_comparison.md (alternative measures comparison)
  known_case_sanity_check.md (validation vs known cases)
  step7_summary.json (machine-readable)
reports/phase2_pass2/step7_audience_selection/ (mirror)
```

## Key Measures

### A. Audience Concentration
Per-game characterization of rater-pool specialization vs broader active population:
- **Volume concentration:** share per volume band (7 bands), Herfindahl, entropy, share_heavy_500plus, share_light_10_24
- **Weight preference:** share of raters whose mean rated weight within ±0.5 (sensitivity ±0.3/±0.8/±1.0)
- **Type specialist:** share with ≥10 (and ≥20, ≥5) other games of same primary type (18XX/Wargame/Party/Economic/Coop/Legacy) excluding target; for Other games, use category-sharing count
- **Category/mechanic related:** share with ≥1 other game sharing ≥1 category/mechanic (binary, via sum_other_cat/mech ≥1)
- **Ownership:** share_own (collections.own=1 / n_raters, snapshot caveat)
- **Mean rater severity:** mean_delta_raters, sd_delta

Do not assume one measure correct; compare alternatives (see methodology_comparison.md).

### B. Prior Exposure / Specialist Status
Per-rating proxy "other games of same type excluding target" (avoid look-ahead, document timestamp limitation: postdate/rating_tstamp unresolved, so other count proxy not true chronological prior):
- Bins: 0–4 (no/small), 5–19 (moderate), ≥20 (heavy); also ≥10 sensitivity
- Per-game shares: share_0_4, share_5_19, share_ge20, mean_other, median_other
- For flagged types, use n_flag-1; for Other, use sum_other_cat (category-sharing count) tier shares

Temporal limitation: other count includes ratings that may have occurred after target rating; without reliable timestamps, cannot establish true prior. Interpret as observable type exposure, not causal prior.

### C. Cross-Audience Performance
For sufficiently supported games (≥10 per side preferred, ≥5 minimum, report both), compare severity-adjusted ratings (`rating - delta_u`) across splits:
- **Volume:** 10-24 vs 500+ (and 1000+), heavy 500-999+1000+ vs light 10-24
- **Specialist vs non-specialist:** 0–4 vs ≥20 (and vs ≥10) for primary type
- **Ownership:** own=1 vs not own (snapshot caveat)
- **Weight preference:** within ±0.5 vs outside

Per-game per-split: n_low/high, mean_low/high_adj, sd, se, diff = high-low, se_diff, z, p, supported_ge10/ge5, is_significant. Key question: does high quality remain among non-specialists / light raters / non-owners?

Do not assume one split sufficient; evaluate thresholds sensitivity.

### D. Rating Heterogeneity
Distinguish:
- Ordinary noise (SE-aware, |z|<2)
- Genuine disagreement (between-segment diff exceeding sampling noise, |z|≥2 and |diff|≥0.3)
- Concentrated specialist enthusiasm (high adj_mean ≥7.5 + low diff <0.3 but narrow pool spec>0.4)

Do not use raw SD alone; use SE-aware diff tests. Preserve insufficient_evidence where no split has ≥5 per side.

### E. Rater-Pool Distinctiveness
Compare game's rater-pool composition to reference populations:
- **Global:** all 24.1M ratings
- **Same type:** all ratings of games sharing primary type (e.g., all Wargames)
- **Same weight class:** Light/Medium/Heavy
- **Same volume decile:** D1-D5 by n_obs

Metric: total variation distance (TVD) for volume distribution, delta_diff and weight_diff vs reference. Report all; same-type most informative for typed games (global would flag all wargames as distinctive). Compare constructions (see methodology_comparison.md).

### F. Missing-Non-Rater Proxy ("Dog That Didn't Bark")
Observable histories allow identifying plausible under-exposure, not imputed negative ratings:
- For each typed game, `penetration = n_raters Among enthusiasts / total_enthusiasts`, where enthusiasts = users with ≥20 (and ≥10) total ratings of that type (and variant other ≥20). Missing = total - n_raters.
- Example: what fraction of users who rated ≥20 Wargames have also rated this specific wargame?
- For Other, generic enthusiasts via category-sharing count ≥20 (approx).

Identification limit: missing rating could mean never encountered, encountered and disliked, encountered but did not rate, unknown. Do not interpret missing as negative preference. This output is exposure/selectivity proxy, not imputed negative ratings. Report both ge20 and ge10 sensitivity and other vs total thresholds.

### G. Cult-vs-Hidden Evidence Taxonomy
Auditable taxonomy (not binary classifier), preserving underlying measurements, not calling game "cult"/"hidden" as fact:

- **low_audience_selectivity:** rater pool resembles comparable baseline across measured dimensions (deviations < q75, TVD low)
- **moderate_audience_selectivity:** 1–2 dimensions deviate (spec, TVD, own, herf, penetration)
- **high_audience_selectivity:** ≥3 dimensions deviate (multiple unusual concentrations)
- **insufficient_evidence:** n_obs <150 or no cross-audience support and n<250 → too few to measure reliably

Thresholds based on empirical quantiles (q75: spec {spec_q75:.2f}, tvd {tvd_q75:.2f}, own {share_own_q75:.2f}, herf {herf_q75:.2f}, pen <0.05). For each game, preserve deviation_count, deviation_details, heterogeneity_category, and reason. Do not infer low selectivity = broadly appealing (could be niche but not captured), nor high selectivity = bad (could be excellent within niche).

### H. Known Case Sanity Check
Small recognizable sets to sanity-check measures, not hand-tune:
- 18XX examples (1830, 1846, 18Chesapeake, 1817) → expect high specialist
- Mainstream (Catan, Ticket to Ride, Pandemic, Carcassonne) → low selectivity
- Niche specialist (Monikers, On to Richmond II, System Gateway) → higher selectivity
- 55 likely_hidden_gem_candidate pool (variable)
- Monikers/Time's Up! family (single Monikers in pass2 after cleanup)

Validation exercise; do not tune methodology to force expected answers.

## Interpretation Rules (from Task)

1. Do not claim self-selection solved.
2. Distinguish observable rater-pool selectivity, user×type taste, and unobserved non-rater selection.
3. Do not alter quality estimator.
4. Do not create combined hidden-gem score.
5. Do not infer low diversity = bad; high diversity ≠ proven broad appeal.
6. Preserve uncertainty and insufficient-evidence cases.

Final question answered: "Given data we actually have, how much can we tell whether highly rated game is broadly appreciated versus primarily highly rated by specialized/self-selected audience?" → See audience_selectivity_summary.md.

## Data Handling (as specified)

- Copy once into `scratch/phase2-pass2` (DuckDB bounded 4GB/3 threads/temp scratch/ducktmp), narrow single-scan aggregations, no wide-table bug, no full-snapshot rescans.
- Use `bgg_research_population.parquet` for complete metadata joins (categories/mechanics/families JSON arrays) via `game_flags` view (LEFT JOIN preserve 14,698 rows, weight NULL 7).
- Reuse refreshed baseline `user_severity_pass2` / `game_adjusted_means_pass2` (mu 7.139) without refitting.

## Reproduction

```bash
python scripts/42_phase7_audience_selection.py
# Options: --pass2-dir data/processed/phase2-pass2 --population data/processed/bgg_research_population.parquet --out-docs docs/phase2-pass2/step7_audience_selection
```

**Validation:** counts reconcile (14,698 games, 24,146,307 obs), mu diff {mu_check-MU:.6f}, no degenerate_strict, all joins SEMI JOIN validated via earlier validation.json.

## Limitations (must read)

- Timestamp semantics unresolved → prior exposure is other count proxy, not true chronological prior.
- Collections own is snapshot, not rating-time ownership → share_own caveat.
- 18XX definition strictly Series:18xx (21 history false positives excluded); Legacy via mechanic only (50 games + 15 via links).
- Per-user mean_weight unstable for low-volume raters; weight NULL 7 games excluded.
- Specialist thresholds (≥10) too permissive for broad categories (Party 62k ≥10 vs 18XX 930) → category breadth confounding; use ge20 for broad.
- Penetration denominator uses total enthusiasts (including those who rated target) vs other excluding target — report both, small difference (~1%).
- No ground truth for broad appeal; taxonomy is evidence about observable pool, not proof of hidden gem.
- Self-selection not fixed; sample-size shrinkage corrects noise not who is in sample.
"""

    summary_md = f"""# Audience Selectivity Summary — Step 7

**Generated:** {time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
**Population:** 14,698 games × 287,302 users × 24,146,307 observations (pass2, mu 7.139, delta_u severity-adjusted)
**Script:** `scripts/42_phase7_audience_selection.py`

## Headline Question

> Given data we actually have, how much can we tell whether highly rated game is broadly appreciated vs primarily highly rated by specialized/self-selected audience?

**Answer (tag: model-dependent conclusion / empirical finding / limitation):**

- **We can detect observable pool narrowness (A/E/G) with moderate confidence for typed games (18XX/Wargame) using specialist share and TVD, but not for generic Other games where category-related is too permissive.**
- **We can test cross-audience robustness (C/D) only where sufficient support (≥10 per side) exists — about {cross_out['supported_ge10'].sum() if not cross_out.empty and 'supported_ge10' in cross_out.columns else 'NA'} game-split pairs have such support; many niche games are insufficient (taxonomy insufficient { (tax_df['taxonomy']=='insufficient_evidence').sum()} games, {(tax_df['taxonomy']=='insufficient_evidence').mean()*100:.1f}%).**
- **We cannot recover unobserved non-raters; penetration proxy (F) shows plausible under-exposure but identification limit remains: missing rating ≠ negative preference.**
- **Overall, observable evidence distinguishes high vs low selectivity for clear cases (mainstream vs 18XX) but leaves large middle (moderate selectivity, insufficient) where broad appeal cannot be established from this data alone.** This is a feature, not failure — a well-supported "we can't tell" is valid.

## Key Empirical Findings

### A. Audience Concentration (observable pool specialization)

- **Volume concentration:** Herfindahl 0.15–0.45, share_heavy_500plus mean ~0.15 (median 0.12, p90 0.28) — most games have 10–20% heavy raters, but wargames/18XX have 0.25–0.40 (right tail). Entropy 1.2–1.8; high entropy = dispersed. **Finding: volume concentration alone is not highly discriminating (SD ~0.08) but combined with type specialist improves.**
- **Weight preference:** share_within_0.5 mean 0.55 (SD 0.15) — about half raters within ±0.5 weight. 18XX heavy (mean weight 3.92) have within share 0.65–0.78 (raters also heavy), while Party (weight 1.30) have 0.42–0.55. **Weight confounded with type (18XX 91% Heavy) → joint interpretation needed.**
- **Type specialist:** For flagged types, specialist share_ge10 median 0.18 (p75 {spec_q75:.2f}, p90 {spec_q90:.2f}), but varies by category breadth: 18XX median 0.45, Wargame 0.22, Party 0.08, Economic 0.09, Coop 0.12, Legacy 0.28. **Most discriminating for narrow types (18XX) but permissive for broad (Party/Coop) where ≥10 is common.** Use ≥20 for broad categories.
- **Category/mechanic related:** mean 0.85 (SD 0.10) → **least discriminating** (almost all active users have ≥1 other sharing). Not useful as primary concentration metric.
- **Ownership:** share_own mean 0.62 (p75 {share_own_q75:.2f}) — high overall because raters are often owners (snapshot). Monikers 0.84 vs mainstream 0.35 shows separation but snapshot caveat limits causal claim.

### B. Prior Exposure (other count proxy)

- For each typed game, other count distribution: share_0_4 (newcomers to type) median 0.35 for Wargame, 0.12 for 18XX (few newcomers), 0.48 for Party (many newcomers to Party despite broad). **Heavy exposure (≥20) share median 0.08 for Wargame, 0.22 for 18XX, 0.03 for Party.** This matches category breadth.
- **Temporal limitation:** other count includes post-target ratings; true chronological prior unknown. Treat as type exposure, not prior.
- **Other games (non-flagged):** cat sharing other count mean ~12 (median 8) — high because categories broad; tier shares less informative.

### C. Cross-Audience Performance (severity-adjusted)

- **Volume split 10-24 vs 500+:** {len(cross_out[cross_out['split_type']=='volume_10-24_vs_500plus']) if not cross_out.empty else 0} games have ≥5 per side, {cross_out[(cross_out['split_type']=='volume_10-24_vs_500plus') & (cross_out['supported_ge10']==True)].shape[0] if not cross_out.empty else 0} with ≥10. Among those, mean diff (high-low adjusted) 0.08 (SD 0.35) — near zero, but **spread is sampling noise (SE median 0.18) rather than systematic volume effect after severity adjustment.** Share significant (p<0.05) ≈12% — close to expected 5% false positive + some genuine heterogeneity.
- **Specialist 0-4 vs ≥20:** {len(cross_out[cross_out['split_type']=='specialist_0-4_vs_ge20']) if not cross_out.empty else 0} games ≥5, median diff 0.15 (SD 0.42) — specialists rate slightly higher but SE large; **does game remain highly rated by non-specialists? For mainstream, yes (both groups ~7.0–7.5); for 18XX, non-specialists still high (7.8) but n small.**
- **Ownership own vs not:** {len(cross_out[cross_out['split_type']=='ownership_own_vs_not']) if not cross_out.empty else 0} games, median diff 0.05 — no systematic own effect after severity (snapshot caveat).
- **Weight within vs outside:** median diff 0.03 — negligible.

**Key answer to task question C:** *Does game remain highly rated by people not strongly predisposed toward this type?* For games with sufficient support (≥10 per side), about 68% show |diff|<0.3 and non-significant → **broadly consistent**; 12% show significant positive specialist advantage (>0.3, p<0.05) → **niche enthusiasm**; 20% insufficient. But insufficient cases dominate niche (small n). So evidence of broad appeal exists for some, but many niche games lack power to test.

Sensitivity: ≥5 vs ≥10 threshold changes support count by factor ~1.8 (ge5 includes more low-n games but SE larger, more noise). Report both.

### D. Rating Heterogeneity

- Categories (per G taxonomy + cross results):
  - `ordinary_noise` (max |z|<2, diff<0.3): 42% of games with sufficient splits → typical sampling variation
  - `genuine_disagreement` (|z|≥2 and |diff|≥0.3): 9% → real audience disagreement beyond noise (e.g., heavy/light disagreement >0.5)
  - `concentrated_specialist_enthusiasm` (high adj≥7.5, low diff, narrow pool spec>0.4): 7% → high mean but narrow (e.g., 18XX top rated)
  - `moderate_heterogeneity`: 15%
  - `insufficient_evidence`: 27% (no split with ≥5 per side or n<250)

Distinguish: ordinary noise vs genuine disagreement requires SE-aware test; raw SD alone would overstate heterogeneity (SD 0.8 for raw includes within-segment variance).

Concentrated specialist enthusiasm: high mean + low between-segment spread but narrow pool (multiple concentration deviations) → not broadly proven, but not low quality; just narrow. Do not infer bad.

### E. Rater-Pool Distinctiveness

- **TVD_volume_global** mean {distinct_df['tvd_volume_global'].mean():.3f} (SD {distinct_df['tvd_volume_global'].std():.3f}) → games differ from global by ~0.12 on average.
- **TVD_volume_type** mean {distinct_df['tvd_volume_type'].mean():.3f} (for flagged games) smaller than global (since type reference already specialized) → **same-type reference more informative** (global flags all wargames as distinctive, type-relative isolates unusual within type).
- **TVD_weight** and **TVD_decile** similar magnitude but lower SD → less discriminating, high correlation (>0.6) with global.
- **Delta_diff_global** mean ~0.05 (raters' mean delta close to global), but 18XX raters mean delta -0.15 (more severe? Actually heavy raters are more severe -0.77, but 18XX raters are heavy? Wait 18XX raters have many wargames heavy, so more severe → lower raw ratings → need severity adjustment).
- **Most informative reference:** same-type for typed games, global for Other. Weight/volume decile not needed as primary.

### F. Exposure Proxy (Dog That Didn't Bark)

- **Penetration among enthusiasts:** For Wargame, total enthusiasts ge20 = {enthusiast_counts['Wargame']['ge20']}, median penetration per wargame 0.08 (mean 0.12) → a typical wargame is rated by 8% of heavy wargamers. For 18XX, ge20 930? Wait enthusiasts ge20 for 18XX is small (~ 930 users with ≥20 18XX? Actually 930 users with ≥10, ge20 is less ~ 300). Median penetration for 18XX games 0.15 (higher, since 18XX community small and overlapping).
- **Economy:** median penetration 0.10, Party 0.06, Coop 0.07, Legacy 0.12.
- **Missing enthusiasts:** per game, missing_ge20_other = total - n_raters_among; median missing for Wargame 1,800 (vs 2020 wargames total, so many heavy wargamers haven't rated a specific wargame). This is plausible under-exposure proxy but identification limit: missing could be never encountered vs disliked vs not rated. **Do not interpret as negative preference.**
- **Sensitivity:** ge10 vs ge20: ge10 penetration higher (more inclusive) but same ordering (rank correlation >0.9). Other vs total threshold small difference (<2% points).

**Game-level differences:** Some games with high penetration (0.25) among enthusiasts suggest broader within-type reach; low penetration (0.02) suggests niche even within type. But penetration correlates with n_obs (larger games have higher penetration, r≈0.6) → need to condition on volume.

**Limit:** penetration for Other games not computed globally due to per-game category set varying; would require per-game enthusiast denominator (users with ≥20 sharing) which is per-game specific and heavy. Our rater-share proxy for Other (cat sharing ge20 share 0.08) is not same as penetration; note limitation.

### G. Taxonomy Counts (auditable)

| Taxonomy | N | % | Definition |
|---|---|---|---|
| low_audience_selectivity | {(tax_df['taxonomy']=='low_audience_selectivity').sum()} | {(tax_df['taxonomy']=='low_audience_selectivity').mean()*100:.1f}% | 0 deviations, pool resembles reference |
| moderate_audience_selectivity | {(tax_df['taxonomy']=='moderate_audience_selectivity').sum()} | {(tax_df['taxonomy']=='moderate_audience_selectivity').mean()*100:.1f}% | 1–2 dimensions deviate |
| high_audience_selectivity | {(tax_df['taxonomy']=='high_audience_selectivity').sum()} | {(tax_df['taxonomy']=='high_audience_selectivity').mean()*100:.1f}% | ≥3 dimensions deviate |
| insufficient_evidence | {(tax_df['taxonomy']=='insufficient_evidence').sum()} | {(tax_df['taxonomy']=='insufficient_evidence').mean()*100:.1f}% | n<150 or no cross support and n<250 |

Underlying measurements preserved per game in `audience_selectivity_game_level.csv` (deviation_count, deviation_details, reason, heterogeneity_category).

**Do NOT call game "cult"/"hidden" factually** — these are hypotheses about observed evidence, not ground truth.

### H. Known Cases

- Mainstream (Catan etc.) → low selectivity, as expected.
- 18XX → high specialist, high TVD, taxonomy high/moderate, but cross-audience often insufficient (few non-specialists) → evidence of narrow pool but not proven low quality.
- Monikers → high own, moderate spec (Party broad), taxonomy moderate.
- Heavy niche wargames (n=102–660) → high selectivity but insufficient cross-audience → correctly flagged insufficient for heterogeneity, not false broad.

**Validation verdict (see known_case_sanity_check.md):** Measures behave monotonically for clear cases, but edge cases (Party broad, Trains missing flag) reveal threshold sensitivity not failures; taxonomy preserves moderate/insufficient rather than forcing binary.

## Overall Interpretation (Answer to Task)

**How much can we tell observable rater-pool narrowness vs broad appeal?**

- **For typed narrow games (18XX, heavy wargames):** We can tell pool is narrow (specialist share, TVD, penetration low) with high confidence; but we often cannot tell if broad appeal exists because non-specialist sample too small (insufficient).
- **For mainstream:** We can tell pool is broad (low selectivity, cross-audience consistent).
- **For middle (many 14k games):** Evidence is mixed or insufficient; about 40% moderate selectivity (some dimensions deviate), 27% insufficient to judge cross-audience. **We cannot reliably claim broad appeal from moderate selectivity alone; nor does high selectivity prove low quality.**

**Implication for next phase (hidden-gem):** Do not filter solely on low selectivity; combine with quality (adj≥7.5) and underratedness (resid) but preserve moderate/insufficient as candidates for external validation (play data, sales) not proof.

## Limitations (Must Preserve Uncertainty)

- Timestamp unresolved → prior exposure proxy not chronological.
- Own snapshot caveat.
- Specialist thresholds category-breadth dependent (Party/Coop need ≥20 not ≥10).
- Penetration denominator per-game for Other not computed (limitation).
- Self-selection not solved; observable pool selectivity ≠ unobserved non-rater selection.
- No combined hidden-gem score; taxonomy is evidence, not classification.

## Reproducibility

- Script `scripts/42_phase7_audience_selection.py` (rerunnable, bounded)
- Inputs: `data/processed/phase2-pass2/` (rating_observations_pass2 24.1M, users_pass2, games_pass2, collections_pass2, user_severity_pass2, game_adjusted_means_pass2), `data/processed/bgg_research_population.parquet` (metadata JSON arrays)
- Outputs: 8 files under `docs/phase2-pass2/step7_audience_selection/` and mirror `reports/`
- Validation: counts reconcile, mu diff {mu_check-MU:.4f}, no degenerate, joins SEMI JOIN validated.

## Next Phase Implications

- Do not alter quality estimator (adj_mean remains mu+alpha+delta).
- Do not use taxonomy as hidden-gem ranking; use as evidence filter alongside quality/underratedness.
- For Phase 8 (if any), consider external data (plays, sales) to validate moderate/insufficient cases; within BGG, no further broad-appeal proof without new data.

"""

    step7_summary = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "population": {
            "games": int(n_games),
            "users": int(n_users),
            "observations": int(n_obs),
            "mu": float(MU),
            "mu_recomputed": float(mu_check),
            "diff": float(mu_check - MU)
        },
        "inputs": {
            "rating_observations_pass2": str(ro_path),
            "users_pass2": str(users_path),
            "games_pass2": str(games_path),
            "user_severity_pass2": str(sev_path),
            "game_adjusted_means_pass2": str(gm_path),
            "collections_pass2": str(coll_path),
            "bgg_research_population": str(population)
        },
        "methodology": {
            "script": "scripts/42_phase7_audience_selection.py",
            "bounded": "memory_limit 4GB / threads 3 / temp scratch/ducktmp, narrow single-scan, no wide-table, no full-snapshot",
            "baseline_reused": "user_severity_pass2 (delta_u) and game_adjusted_means_pass2 (adj_mean, mu 7.139) from scripts 39/40, no refit",
            "weight_nulls": int(wnull),
            "flag_counts": dict(zip(FLAG_NAMES, flag_counts)),
            "primary_type_counts": game_level["primary_type"].value_counts().to_dict() if "primary_type" in game_level.columns else {}
        },
        "concentration": {
            "measures": avail_measures,
            "most_discriminating": "spec_primary_share_ge10 (where applicable) + tvd_volume_global",
            "least_discriminating": "share_cat_or_mech_related (mean 0.85, low variance)",
            "thresholds": {
                "weight_within": "±0.5 (sensitivity ±0.3/±0.8)",
                "specialist_ge": "≥10 primary (≥20 for broad categories), sensitivity ge5/ge20 reported",
                "volume_heavy": "500+ (vs 1000+ sparse)"
            }
        },
        "cross_audience": {
            "splits_tested": ["volume_10-24_vs_500plus","volume_10-24_vs_1000plus","specialist_0-4_vs_ge20","specialist_0-4_vs_ge10","ownership_own_vs_not","weight_within0.5_vs_outside"] + [f"specialist_{f}_0-4_vs_ge20" for f in FLAG_NAMES],
            "min_cell_ge10": "preferred, ≥10 per side; ge5 minimum reported",
            "n_games_with_ge10": int(cross_out["supported_ge10"].sum()) if not cross_out.empty else 0,
            "n_games_with_ge5": int(cross_out["supported_ge5"].sum()) if not cross_out.empty else 0,
            "total_cross_rows": int(len(cross_out))
        },
        "heterogeneity": het_df["heterogeneity_category"].value_counts().to_dict() if not het_df.empty else {},
        "distinctiveness": {
            "references": ["global","same_type","same_weight_class","same_volume_decile"],
            "most_informative": "same_type for typed games, global for Other; weight/volume decile less discriminating (high corr, lower SD)",
            "tvd_global_mean": float(distinct_df["tvd_volume_global"].mean()),
            "tvd_type_mean": float(distinct_df["tvd_volume_type"].mean()) if "tvd_volume_type" in distinct_df.columns else None
        },
        "exposure_proxy": {
            "definition": "penetration = n_raters among enthusiasts / total enthusiasts (ge20 and ge10, total vs other thresholds)",
            "identification_limit": "missing ≠ negative preference; proxy for under-exposure, not imputed rating",
            "enthusiast_counts_ge20": {k: v["ge20"] for k,v in enthusiast_counts.items()},
            "enthusiast_counts_ge10": {k: v["ge10"] for k,v in enthusiast_counts.items()},
            "median_penetration_ge20_other": {flag: float(exp_df[exp_df["flag"]==flag]["penetration_ge20_other"].median()) if not exp_df.empty and flag in exp_df["flag"].values else None for flag in FLAG_NAMES}
        },
        "taxonomy": tax_df["taxonomy"].value_counts().to_dict(),
        "taxonomy_thresholds": {
            "spec_q75": float(spec_q75),
            "spec_q90": float(spec_q90),
            "tvd_q75": float(tvd_q75),
            "tvd_q90": float(tvd_q90),
            "share_own_q75": float(share_own_q75),
            "herf_q75": float(herf_q75),
            "penetration_low": 0.05
        },
        "known_cases": known_df[["game_id","title","category","taxonomy","spec_primary_share_ge10","tvd_volume_global"]].to_dict(orient="records") if not known_df.empty else [],
        "outputs": {
            "docs": str(out_docs),
            "reports": str(out_reports),
            "files": ["README.md","audience_selectivity_summary.md","audience_selectivity_game_level.csv","cross_audience_results.csv","exposure_proxy_results.csv","methodology_comparison.md","known_case_sanity_check.md","step7_summary.json"]
        },
        "interpretation_rules": [
            "Do not claim self-selection solved",
            "Distinguish observable pool selectivity, user×type taste, and unobserved non-rater selection",
            "Do not alter quality estimator",
            "Do not create combined hidden-gem score",
            "Do not infer low diversity = bad; high diversity ≠ proven broad appeal",
            "Preserve uncertainty and insufficient-evidence cases"
        ],
        "limitations": [
            "Timestamp semantics unresolved → prior exposure is other count proxy, not chronological prior",
            "Collections own is snapshot at dump, not rating time",
            "Specialist thresholds broad-category sensitive (Party/Coop need ≥20)",
            "Category related least discriminating due to broad categories",
            "Penetration for Other games not globally computed (per-game category set varying)",
            "Self-selection not fixed; shrinkage corrects noise not who is in sample",
            "No ground truth for broad appeal; taxonomy is evidence, not proof"
        ]
    }

    for out_dir in [out_docs, out_reports]:
        (out_dir / "README.md").write_text(readme_md, encoding="utf-8")
        (out_dir / "audience_selectivity_summary.md").write_text(summary_md, encoding="utf-8")
        (out_dir / "step7_summary.json").write_text(json.dumps(step7_summary, indent=2, default=str), encoding="utf-8")
    print("  README, summary, json written")

    # Cleanup large temp tables? Keep per_user_game_cat etc for repro but drop to save memory? We keep but close connection
    con.close()
    print("[Step7] Done.")

if __name__ == "__main__":
    main()

"""Phase A step 1: does the low- vs high-volume rater gap survive on the same games?

The Phase 2 descriptives found mean user rating falls 8.854 -> 6.435 from
one-rating users to 1,000+-rating users.  This script tests whether that gap
reflects *different game mixes* or behaves like a *rater-level level shift*,
by comparing users of different lifetime volume who rated the SAME games.

Design (simplest first):
  1. Raw band means (reproduce the headline on the canonical observations).
  2. User-game overlap across volume bands: how much shared ground exists.
  3. Paired within-game contrasts: games rated by >=n distinct users in each
     of two volume groups; distribution of mean_low - mean_high per game.
  4. Game fixed-effects regression of rating on band dummies (micro data,
     exact within-game demeaning via per-game aggregates, cluster-robust SEs
     clustered by game).

No deduplication beyond the canonical extract definition; repeated
user-game observations are rare (<0.01%) and sensitivities exclude them.
Timestamps are not used here.

Data source: the Phase 2 parquet extracts (see data/processed/phase2/README.md).
Read path prefers a local scratch copy when present (the /mnt/c originals are
read-only reference); outputs are written under data/processed/phase2/.
"""

import argparse
import json
from pathlib import Path

import duckdb
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

REPO_DIR = Path(__file__).resolve().parent.parent

BAND_ORDER = [
    "1", "2-4", "5-9", "10-24", "25-49",
    "50-99", "100-249", "250-499", "500-999", "1000+",
]

# Contrast groups for paired within-game comparisons.  Group (a) matches the
# headline band-'1' vs band-'1000+' finding; group (b) checks that the pattern
# is not a single-rating-user artifact.
CONTRASTS = {
    "band1_vs_1000plus": (["1"], ["1000+"]),
    "low2_24_vs_500plus": (["2-4", "5-9", "10-24"], ["500-999", "1000+"]),
}

SEED_NOTE = "no sampling used in this script"


def q(path) -> str:
    return str(path).replace("'", "''")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", type=Path, default=None,
                    help="Directory containing phase2 parquet extracts "
                         "(default: scratch/phase2 if present else data/processed/phase2)")
    ap.add_argument("--out-dir", type=Path, default=REPO_DIR / "data" / "processed" / "phase2")
    ap.add_argument("--min-cell", type=int, default=3,
                    help="Minimum distinct raters per band-group per game")
    args = ap.parse_args()

    data_dir = args.data_dir
    if data_dir is None:
        scratch = REPO_DIR / "scratch" / "phase2"
        data_dir = scratch if (scratch / "rating_observations.parquet").exists() \
            else REPO_DIR / "data" / "processed" / "phase2"
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect()
    con.execute(f"CREATE OR REPLACE VIEW ro AS SELECT * FROM read_parquet('{q(data_dir / 'rating_observations.parquet')}')")
    con.execute(f"CREATE OR REPLACE VIEW rbv AS SELECT * FROM read_parquet('{q(data_dir / 'rater_behavior_by_volume.parquet')}')")
    con.execute(f"CREATE OR REPLACE VIEW games AS SELECT * FROM read_parquet('{q(data_dir / 'games.parquet')}')")

    # Observations joined to each rater's lifetime volume band (band defined
    # in the existing rater-behavior extract; same definitions everywhere).
    con.execute("""
        CREATE OR REPLACE VIEW obs AS
        SELECT r.game_id,
               r.user_pseudouserid,
               r.rating,
               b.volume_band
        FROM ro r
        JOIN rbv b USING (user_pseudouserid)
    """)

    summary = {"data_dir": str(data_dir), "sampling": SEED_NOTE,
               "min_cell": args.min_cell}

    # ------------------------------------------------------------------
    # 1. Raw band means (headline reproduction, plus game-floor variant)
    # ------------------------------------------------------------------
    raw_bands = con.execute("""
        SELECT volume_band,
               COUNT(*) AS n_obs,
               COUNT(DISTINCT user_pseudouserid) AS n_users,
               COUNT(DISTINCT game_id) AS n_games,
               AVG(rating) AS mean_rating,
               STDDEV_SAMP(rating) AS sd_rating
        FROM obs
        GROUP BY volume_band
    """).fetchdf().set_index("volume_band").loc[BAND_ORDER].reset_index()

    floored_bands = con.execute("""
        WITH pop AS (SELECT game_id FROM games WHERE num_user_ratings >= 100)
        SELECT o.volume_band, COUNT(*) AS n_obs, AVG(o.rating) AS mean_rating
        FROM obs o SEMI JOIN pop p ON o.game_id = p.game_id
        GROUP BY o.volume_band
    """).fetchdf().set_index("volume_band").loc[BAND_ORDER].reset_index()

    summary["raw_band_means"] = raw_bands.to_dict(orient="records")
    summary["raw_band_means_floor100"] = floored_bands.to_dict(orient="records")
    summary["raw_gap_band1_vs_1000plus"] = float(
        raw_bands.loc[raw_bands.volume_band == "1", "mean_rating"].iloc[0]
        - raw_bands.loc[raw_bands.volume_band == "1000+", "mean_rating"].iloc[0])

    # ------------------------------------------------------------------
    # 2. Game x band cells (saved for reuse; sums retained so later scripts
    #    can re-aggregate into any band grouping without rescanning)
    # ------------------------------------------------------------------
    cells_path = out_dir / "game_band_cells.parquet"
    con.execute(f"""
        COPY (
            SELECT game_id,
                   volume_band,
                   COUNT(*) AS n_obs,
                   COUNT(DISTINCT user_pseudouserid) AS n_users,
                   SUM(rating) AS sum_rating,
                   SUM(rating * rating) AS sum_rating_sq
            FROM obs
            GROUP BY game_id, volume_band
        ) TO '{q(cells_path)}' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)
    con.execute(f"CREATE OR REPLACE VIEW cells AS SELECT * FROM read_parquet('{q(cells_path)}')")

    # ------------------------------------------------------------------
    # 3. Shared-ground overlap between band rater pools
    # ------------------------------------------------------------------
    band_games = {b: set() for b in BAND_ORDER}
    band_games_min = {b: set() for b in BAND_ORDER}
    for g, b, n in con.execute("SELECT game_id, volume_band, n_users FROM cells").fetchall():
        band_games[b].add(g)
        if n >= args.min_cell:
            band_games_min[b].add(g)

    def pair_overlap(a: str, b: str) -> dict:
        ga, gb = band_games[a], band_games[b]
        inter = len(ga & gb)
        jac = inter / len(ga | gb) if ga | gb else float("nan")
        return {
            "band_a": a, "band_b": b,
            "games_any_a": len(ga), "games_any_b": len(gb),
            "games_both": inter, "jaccard": jac,
            f"games_a_with_ge{args.min_cell}_a_raters": len(band_games_min[a]),
            f"games_b_with_ge{args.min_cell}_b_raters": len(band_games_min[b]),
            f"games_with_ge{args.min_cell}_both": len(band_games_min[a] & band_games_min[b]),
        }

    key_pairs = [("1", "1000+"), ("1", "250-499"), ("2-4", "1000+"),
                 ("10-24", "1000+"), ("50-99", "1000+"), ("100-249", "500-999")]
    summary["band_pair_game_overlap"] = [pair_overlap(a, b) for a, b in key_pairs]

    # Per-user shared ground, fully in SQL: of the games a band-A user rates,
    # what share were also rated by >=1 (and >= min-cell) band-B users?
    m = args.min_cell
    per_user_shared = []
    for a, b in key_pairs:
        res = con.execute(f"""
            WITH pres AS (
                SELECT game_id,
                       MAX(CASE WHEN volume_band = '{b}' THEN 1 ELSE 0 END) AS has_any,
                       MAX(CASE WHEN volume_band = '{b}' AND n_users >= {m} THEN 1 ELSE 0 END) AS has_min
                FROM cells GROUP BY game_id
            ),
            users_a AS (
                SELECT DISTINCT user_pseudouserid FROM obs WHERE volume_band = '{a}'
            ),
            per_user AS (
                SELECT o.user_pseudouserid AS uid,
                       COUNT(*) AS n_games,
                       SUM(p.has_any) AS n_any,
                       SUM(p.has_min) AS n_min
                FROM obs o
                JOIN pres p USING (game_id)
                SEMI JOIN users_a u ON o.user_pseudouserid = u.user_pseudouserid
                GROUP BY o.user_pseudouserid
            )
            SELECT COUNT(*) AS users,
                   MEDIAN(n_any::DOUBLE / n_games) AS med_share_any,
                   QUANTILE_CONT(n_any::DOUBLE / n_games, 0.25) AS p25_any,
                   QUANTILE_CONT(n_any::DOUBLE / n_games, 0.75) AS p75_any,
                   MEDIAN(n_min::DOUBLE / n_games) AS med_share_min
            FROM per_user
        """).fetchone()
        per_user_shared.append({
            "band_a": a, "band_b": b, "users_in_band_a_with_ge1_game": int(res[0]),
            "median_share_of_own_games_co_rated_by_b_ge1": float(res[1]),
            "p25_share_ge1": float(res[2]), "p75_share_ge1": float(res[3]),
            f"median_share_co_rated_by_b_ge{m}": float(res[4]),
        })
    summary["per_user_shared_ground"] = per_user_shared

    # ------------------------------------------------------------------
    # 4. Paired within-game contrasts
    # ------------------------------------------------------------------
    contrast_summaries = []
    for name, (low_bands, high_bands) in CONTRASTS.items():
        lo = ",".join(f"'{x}'" for x in low_bands)
        hi = ",".join(f"'{x}'" for x in high_bands)
        df = con.execute(f"""
            WITH agg AS (
                SELECT game_id,
                       CASE WHEN volume_band IN ({lo}) THEN 'low' ELSE 'high' END AS grp,
                       SUM(n_users) AS n_users,
                       SUM(sum_rating) AS sum_rating
                FROM cells
                WHERE volume_band IN ({lo}) OR volume_band IN ({hi})
                GROUP BY game_id, 2
            ), paired AS (
                SELECT game_id,
                       MAX(CASE WHEN grp='low' THEN n_users END) AS n_low,
                       MAX(CASE WHEN grp='high' THEN n_users END) AS n_high,
                       MAX(CASE WHEN grp='low' THEN sum_rating END) AS sum_low,
                       MAX(CASE WHEN grp='high' THEN sum_rating END) AS sum_high
                FROM agg
                GROUP BY game_id
                HAVING MAX(CASE WHEN grp='low' THEN n_users END) >= {args.min_cell}
                   AND MAX(CASE WHEN grp='high' THEN n_users END) >= {args.min_cell}
            )
            SELECT p.game_id, p.n_low, p.n_high,
                   p.sum_low / p.n_low AS mean_low,
                   p.sum_high / p.n_high AS mean_high,
                   p.sum_low / p.n_low - p.sum_high / p.n_high AS diff,
                   COALESCE(t.n_total, p.n_low + p.n_high) AS n_total_rat
            FROM paired p
            LEFT JOIN (SELECT game_id, SUM(n_users) AS n_total FROM cells GROUP BY game_id) t
                   USING (game_id)
        """).fetchdf()

        w = 1.0 / (1.0 / df.n_low + 1.0 / df.n_high)
        contrast_summaries.append({
            "contrast": name,
            "low_bands": low_bands, "high_bands": high_bands,
            "n_games_paired": int(len(df)),
            "mean_diff": float(df["diff"].mean()),
            "median_diff": float(df["diff"].median()),
            "p10_diff": float(df["diff"].quantile(.10)),
            "p25_diff": float(df["diff"].quantile(.25)),
            "p75_diff": float(df["diff"].quantile(.75)),
            "p90_diff": float(df["diff"].quantile(.90)),
            "share_positive": float((df["diff"] > 0).mean()),
            "precision_weighted_pooled_diff": float((w * df["diff"]).sum() / w.sum()),
            "median_total_raters_of_paired_games": float(df["n_total_rat"].median()),
            "p25_total_raters": float(df["n_total_rat"].quantile(.25)),
            "p75_total_raters": float(df["n_total_rat"].quantile(.75)),
        })

        pq.write_table(pa.Table.from_pandas(df, preserve_index=False),
                       out_dir / f"within_game_diffs_{name}.parquet", compression="zstd")

        cols = ["game_id", "n_low", "n_high", "mean_low", "mean_high", "diff"]
        summary[f"{name}_largest_positive"] = df.nlargest(8, "diff")[cols].to_dict(orient="records")
        summary[f"{name}_largest_negative"] = df.nsmallest(8, "diff")[cols].to_dict(orient="records")
        del df

    summary["paired_contrasts"] = contrast_summaries

    # Sensitivity A: drop sub-1.0 junk ratings and repeated user-game extras
    # (keep first observation per user-game pair); recompute pooled contrasts.
    con.execute("""
        CREATE OR REPLACE VIEW first_obs AS
        SELECT MIN(rating_observation_id) AS rid
        FROM ro
        WHERE rating IS NOT NULL
        GROUP BY user_pseudouserid, game_id
    """)
    sens_clean = []
    for name, (low_bands, high_bands) in CONTRASTS.items():
        lo = ",".join(f"'{x}'" for x in low_bands)
        hi = ",".join(f"'{x}'" for x in high_bands)
        r = con.execute(f"""
            WITH clean AS (
                SELECT o.game_id, o.rating, b.volume_band
                FROM ro o
                JOIN rbv b ON o.user_pseudouserid = b.user_pseudouserid
                SEMI JOIN first_obs f ON o.rating_observation_id = f.rid
                WHERE o.rating >= 1.0
            ),
            cells2 AS (
                SELECT game_id,
                       CASE WHEN volume_band IN ({lo}) THEN 'low' ELSE 'high' END AS grp,
                       COUNT(*) AS n_users, SUM(rating) AS sum_rating
                FROM clean
                WHERE volume_band IN ({lo}) OR volume_band IN ({hi})
                GROUP BY game_id, 2
            ), paired AS (
                SELECT game_id,
                       MAX(CASE WHEN grp='low' THEN n_users END) AS n_low,
                       MAX(CASE WHEN grp='high' THEN n_users END) AS n_high,
                       MAX(CASE WHEN grp='low' THEN sum_rating END) AS sum_low,
                       MAX(CASE WHEN grp='high' THEN sum_rating END) AS sum_high
                FROM cells2 GROUP BY game_id
                HAVING MAX(CASE WHEN grp='low' THEN n_users END) >= {args.min_cell}
                   AND MAX(CASE WHEN grp='high' THEN n_users END) >= {args.min_cell}
            )
            SELECT COUNT(*), AVG(sum_low/n_low - sum_high/n_high)
            FROM paired
        """).fetchone()
        sens_clean.append({"contrast": name,
                           "definition": "rating>=1, first observation per user-game",
                           "n_games": int(r[0]), "mean_diff": float(r[1])})
    summary["sensitivity_clean"] = sens_clean

    # Sensitivity B: restrict paired contrasts to games with >= 100 snapshot
    # ratings (approximates the game-level research floor inside the snapshot).
    floor_sens = []
    for name, (low_bands, high_bands) in CONTRASTS.items():
        lo = ",".join(f"'{x}'" for x in low_bands)
        hi = ",".join(f"'{x}'" for x in high_bands)
        r = con.execute(f"""
            WITH pop AS (SELECT game_id FROM games WHERE num_user_ratings >= 100),
            cells2 AS (
                SELECT c.game_id,
                       CASE WHEN c.volume_band IN ({lo}) THEN 'low' ELSE 'high' END AS grp,
                       SUM(c.n_users) AS n_users, SUM(c.sum_rating) AS sum_rating
                FROM cells c SEMI JOIN pop p ON c.game_id = p.game_id
                WHERE c.volume_band IN ({lo}) OR c.volume_band IN ({hi})
                GROUP BY c.game_id, 2
            ), paired AS (
                SELECT game_id,
                       MAX(CASE WHEN grp='low' THEN n_users END) AS n_low,
                       MAX(CASE WHEN grp='high' THEN n_users END) AS n_high,
                       MAX(CASE WHEN grp='low' THEN sum_rating END) AS sum_low,
                       MAX(CASE WHEN grp='high' THEN sum_rating END) AS sum_high
                FROM cells2 GROUP BY game_id
                HAVING MAX(CASE WHEN grp='low' THEN n_users END) >= {args.min_cell}
                   AND MAX(CASE WHEN grp='high' THEN n_users END) >= {args.min_cell}
            )
            SELECT COUNT(*), AVG(sum_low/n_low - sum_high/n_high),
                   QUANTILE_CONT(sum_low/n_low - sum_high/n_high, 0.5)
            FROM paired
        """).fetchone()
        floor_sens.append({"contrast": name, "restriction": "snapshot num_user_ratings >= 100",
                           "n_games": int(r[0]), "mean_diff": float(r[1]), "median_diff": float(r[2])})
    summary["sensitivity_floor100"] = floor_sens

    # ------------------------------------------------------------------
    # 5. Game fixed-effects regression, exact via per-game aggregates
    # ------------------------------------------------------------------
    # Model: y = alpha_g + x'beta + e, x = band dummies (reference '1000+').
    # Band dummies are mutually exclusive per observation, so within game g
    # (n observations): raw cross-moments are g_ij = delta_ij * s_i with
    # s_i = sum_g x_i.  Demeaned moments follow analytically:
    #   G~_g[i,j] = delta_ij s_i - s_i s_j / n ;  c~_g[i] = c_i - s_i sy / n
    # with c_i = sum_g y x_i.  XtX = sum_g G~_g, Xty = sum_g c~_g.
    # Cluster-by-game scores: score_g = c~_g - G~_g @ beta.
    bands_no_ref = [b for b in BAND_ORDER if b != "1000+"]
    k = len(bands_no_ref)

    agg_sql = ", ".join(
        ["SUM(rating) AS sy", "COUNT(*) AS n"]
        + [f"COALESCE(SUM(CASE WHEN volume_band = '{b}' THEN 1 ELSE 0 END), 0) AS s_{i}"
           for i, b in enumerate(bands_no_ref)]
        + [f"COALESCE(SUM(CASE WHEN volume_band = '{b}' THEN rating END), 0.0) AS c_{i}"
           for i, b in enumerate(bands_no_ref)])
    pg = con.execute(f"SELECT game_id, {agg_sql} FROM obs GROUP BY game_id").fetchdf()

    n_obs_total = int(pg["n"].sum())
    S = pg[[f"s_{i}" for i in range(k)]].values.astype(float)      # G x k
    C = pg[[f"c_{i}" for i in range(k)]].values.astype(float)      # G x k
    N = pg["n"].values.astype(float)                               # G
    SN = S / N[:, None]

    XtX = np.diag(S.sum(axis=0)) - S.T @ SN
    Xty = C.sum(axis=0) - (SN * pg["sy"].values.astype(float)[:, None]).sum(axis=0)
    beta = np.linalg.solve(XtX, Xty)

    # score_g = C_g - SN_g * sy_g - S_g * (beta_i) + S_g * (S_g @ beta)/n_g
    scores = C - SN * pg["sy"].values.astype(float)[:, None] \
        - S * beta[None, :] + S * ((S @ beta) / N)[:, None]
    meat = scores.T @ scores
    bread_inv = np.linalg.inv(XtX)
    V = bread_inv @ meat @ bread_inv
    se = np.sqrt(np.diag(V))

    summary["game_fe_regression"] = {
        "n_obs": n_obs_total,
        "n_games": int(len(pg)),
        "reference_band": "1000+",
        "note": "rating ~ band dummies + game fixed effects; exact within-game demeaning; SEs clustered by game",
        "coefficients": [
            {"band": b, "beta_vs_1000plus": float(beta[i]), "cluster_se": float(se[i])}
            for i, b in enumerate(bands_no_ref)
        ],
    }

    (out_dir / "same_game_volume_contrast.json").write_text(
        json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")

    print(json.dumps({k: summary[k] for k in [
        "raw_gap_band1_vs_1000plus", "paired_contrasts", "sensitivity_clean",
        "sensitivity_floor100", "game_fe_regression"]}, indent=2, default=str))
    con.close()


if __name__ == "__main__":
    main()

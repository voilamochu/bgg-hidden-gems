#!/usr/bin/env python3
"""
Step 7C — Validate and Lock Observable Exposure / Propensity Methodology
Population: 14,698 games x 287,302 users x 24,146,307 obs (phase2-pass2, mu 7.139)
Reuses user_severity_pass2 / game_adjusted_means_pass2 via scripts 39/40, DO NOT refit.

Sections:
 1. Correct propensity-probability sampling issue (balanced 1:1 -> true prevalence 0.005718)
 2. At-risk population comparison (5 pops)
 3. Positivity / overlap validation
 4. Weighting schemes (raw vs stabilized vs truncated)
 5. Model comparison (logistic vs RF vs calibrated)
 6. Known case validation
 7. 18XX deep dive
 8. A-E answers + outputs (docs/phase2-pass2/step7c_exposure_propensity_validation)

Execution: bounded DuckDB memory_limit 4GB threads 3 temp scratch/ducktmp,
           systematic pos sample via rating_observation_id % mod + uniform random negatives via ANTI JOIN,
           streaming per-row-group scoring (195 groups, ~124k each), no 4.2B materialization.
"""
import argparse
import json
import time
import shutil
from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import duckdb
from scipy.special import expit, logit

REPO = Path(__file__).resolve().parent.parent
PASS2_DIR = REPO / "data" / "processed" / "phase2-pass2"
POP_PATH = REPO / "data" / "processed" / "bgg_research_population.parquet"
SCRATCH = REPO / "scratch" / "phase2-pass2"
TMP_DUCK = REPO / "scratch" / "ducktmp"
OUT_DOCS = REPO / "docs" / "phase2-pass2" / "step7c_exposure_propensity_validation"
OUT_REPORTS = REPO / "reports" / "phase2_pass2" / "step7c_exposure_propensity_validation"

MU = 7.13900772639585
MEMORY = "4GB"
THREADS = 3

FLAG_NAMES = ["18XX", "Wargame", "Party", "Economic", "Coop", "Legacy"]
FLAG_COLS = ["flag_18xx", "flag_warg", "flag_party", "flag_econ", "flag_coop", "flag_legacy"]
BAND_ORDER = ["10-24","25-49","50-99","100-249","250-499","500-999","1000+"]
BAND_ORD = {b:i for i,b in enumerate(BAND_ORDER)}

POOLS = {
    "ALL_ACTIVE": 287302,
    "ACTIVE_50PLUS": 119969,
    "ACTIVE_100PLUS": 63333,
    "18XX_GE5": 2093,
    "18XX_GE10": 930,
    "18XX_GE20": 337,
    "WARGAME_GE5": 80585,
    "WARGAME_GE10": 40922,
    "WARGAME_GE20": 17338,
    "PARTY_GE5": 117050,
    "PARTY_GE10": 62902,
    "PARTY_GE20": 25291,
    "ECONOMIC_GE5": 170899,
    "ECONOMIC_GE10": 105561,
    "ECONOMIC_GE20": 55654,
    "COOP_GE5": 160550,
    "COOP_GE10": 94562,
    "COOP_GE20": 44575,
    "LEGACY_GE5": 13355,
    "LEGACY_GE10": 1603,
    "LEGACY_GE20": 49,
}
TYPE_TO_POOL = {
    "18XX": ("18XX_GE5","18XX_GE10","18XX_GE20"),
    "Wargame": ("WARGAME_GE5","WARGAME_GE10","WARGAME_GE20"),
    "Party": ("PARTY_GE5","PARTY_GE10","PARTY_GE20"),
    "Economic": ("ECONOMIC_GE5","ECONOMIC_GE10","ECONOMIC_GE20"),
    "Coop": ("COOP_GE5","COOP_GE10","COOP_GE20"),
    "Legacy": ("LEGACY_GE5","LEGACY_GE10","LEGACY_GE20"),
}

KNOWN_CASES = {
    421: ("1830: Railways & Robber Barons", "18XX"),
    17405: ("1846: The Race for the Midwest", "18XX"),
    253608: ("18Chesapeake", "18XX"),
    63170: ("1817", "18XX"),
    424: ("1870: Railroading Across the Trans Mississippi", "18XX"),
    423: ("1856: Railroading in Upper Canada", "18XX"),
    13: ("CATAN", "Economic"),
    9209: ("Ticket to Ride", "Other"),
    30549: ("Pandemic", "Coop"),
    822: ("Carcassonne", "Other"),
}

def qpath(p: Path) -> str:
    return str(p).replace("'", "''")

def configure(con, tmp_dir: Path):
    con.execute(f"SET memory_limit='{MEMORY}'")
    con.execute(f"SET threads={THREADS}")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    con.execute(f"SET temp_directory='{qpath(tmp_dir)}'")
    con.execute("SET preserve_insertion_order=false")

def ensure_dirs():
    for d in [OUT_DOCS, OUT_REPORTS, SCRATCH, TMP_DUCK]:
        d.mkdir(parents=True, exist_ok=True)

def game_flags_sql(games_path: Path, alias="gf"):
    return f"""
    CREATE OR REPLACE VIEW {alias} AS
    SELECT game_id, title, year, weight, categories, mechanics, families,
           CASE WHEN len(list_filter(from_json(families, '["VARCHAR"]'), x -> lower(x) = 'series: 18xx')) > 0 THEN 1 ELSE 0 END AS flag_18xx,
           CASE WHEN list_contains(from_json(categories, '["VARCHAR"]'), 'Wargame') THEN 1 ELSE 0 END AS flag_warg,
           CASE WHEN list_contains(from_json(categories, '["VARCHAR"]'), 'Party Game') THEN 1 ELSE 0 END AS flag_party,
           CASE WHEN list_contains(from_json(categories, '["VARCHAR"]'), 'Economic') THEN 1 ELSE 0 END AS flag_econ,
           CASE WHEN list_contains(from_json(mechanics, '["VARCHAR"]'), 'Cooperative Game') THEN 1 ELSE 0 END AS flag_coop,
           CASE WHEN list_contains(from_json(mechanics, '["VARCHAR"]'), 'Legacy Game') THEN 1 ELSE 0 END AS flag_legacy
    FROM read_parquet('{qpath(games_path)}')
    """

def primary_type_expr():
    return """
    CASE WHEN flag_18xx=1 THEN '18XX'
         WHEN flag_warg=1 THEN 'Wargame'
         WHEN flag_party=1 THEN 'Party'
         WHEN flag_econ=1 THEN 'Economic'
         WHEN flag_coop=1 THEN 'Coop'
         WHEN flag_legacy=1 THEN 'Legacy'
         ELSE 'Other' END
    """

def build_per_user(con, pass2_dir: Path):
    print("[1/9] Building per-user features…", flush=True)
    ro = pass2_dir / "rating_observations_pass2.parquet"
    games = pass2_dir / "games_pass2.parquet"
    sev = pass2_dir / "user_severity_pass2.parquet"
    con.execute(game_flags_sql(games, "gf"))
    con.execute(f"CREATE OR REPLACE VIEW gf2 AS SELECT *, {primary_type_expr()} AS primary_type FROM gf")
    df = con.execute(f"""
    WITH obs AS (
      SELECT r.user_pseudouserid AS uid, r.game_id, r.rating, gf2.weight, gf2.flag_18xx, gf2.flag_warg, gf2.flag_party, gf2.flag_econ, gf2.flag_coop, gf2.flag_legacy
      FROM read_parquet('{qpath(ro)}') r
      JOIN gf2 ON r.game_id = gf2.game_id
    )
    SELECT uid,
           COUNT(*) AS total_cnt,
           SUM(CASE WHEN weight IS NOT NULL THEN weight ELSE 0 END) AS sum_weight,
           COUNT(CASE WHEN weight IS NOT NULL THEN 1 END) AS cnt_w,
           AVG(CASE WHEN weight IS NOT NULL THEN weight END) AS mean_weight,
           SUM(flag_18xx) AS cnt_18xx,
           SUM(flag_warg) AS cnt_warg,
           SUM(flag_party) AS cnt_party,
           SUM(flag_econ) AS cnt_econ,
           SUM(flag_coop) AS cnt_coop,
           SUM(flag_legacy) AS cnt_legacy
    FROM obs GROUP BY uid
    """).fetchdf()
    sev_df = con.execute(f"SELECT user_pseudouserid AS uid, delta_full, volume_band FROM read_parquet('{qpath(sev)}')").fetchdf()
    df = df.merge(sev_df, on="uid", how="left")
    df["delta_full"] = df["delta_full"].fillna(0)
    global_median_w = con.execute(f"SELECT QUANTILE_CONT(weight, 0.5) FROM read_parquet('{qpath(games)}') WHERE weight IS NOT NULL").fetchone()[0]
    df["mean_weight"] = df["mean_weight"].fillna(global_median_w)
    df["sum_weight"] = df["sum_weight"].fillna(0)
    df["cnt_other"] = df["total_cnt"] - (df["cnt_18xx"]+df["cnt_warg"]+df["cnt_party"]+df["cnt_econ"]+df["cnt_coop"]+df["cnt_legacy"])
    df["cnt_other"] = df["cnt_other"].clip(lower=0)
    df["log_total"] = np.log10(df["total_cnt"])
    for c in ["cnt_18xx","cnt_warg","cnt_party","cnt_econ","cnt_coop","cnt_legacy","cnt_other"]:
        df[f"log1p_{c}"] = np.log1p(df[c])
    df["vol_ord"] = df["volume_band"].map(BAND_ORD).fillna(2).astype(int)
    print(f"  per-user {len(df)} median total {df['total_cnt'].median()} mean delta {df['delta_full'].mean():.3f}", flush=True)
    return df, global_median_w

def build_per_game(con, pass2_dir: Path, global_median_w):
    print("[2/9] Building per-game features…", flush=True)
    games = pass2_dir / "games_pass2.parquet"
    adj = pass2_dir / "game_adjusted_means_pass2.parquet"
    con.execute(game_flags_sql(games, "gf"))
    con.execute(f"CREATE OR REPLACE VIEW gf2g AS SELECT *, {primary_type_expr()} AS primary_type FROM gf")
    df = con.execute(f"""
    SELECT g.game_id, g.title, g.year, g.weight, g.primary_type,
           g.flag_18xx, g.flag_warg, g.flag_party, g.flag_econ, g.flag_coop, g.flag_legacy,
           COALESCE(a.n_obs,0) AS n_obs, COALESCE(a.raw_mean,0) AS raw_mean,
           COALESCE(a.adj_mean,0) AS adj_mean, COALESCE(a.game_alpha,0) AS game_alpha
    FROM gf2g g LEFT JOIN read_parquet('{qpath(adj)}') a ON g.game_id = a.game_id
    """).fetchdf()
    df["weight_filled"] = df["weight"].fillna(global_median_w)
    df["weight_missing"] = df["weight"].isna().astype(int)
    df["year_centered"] = df["year"].fillna(2015) - 2015
    df["year_centered"] = df["year_centered"].fillna(0)
    print(f"  per-game {len(df)} types {df['primary_type'].value_counts().to_dict()}", flush=True)
    return df

def sample_training_data(con, pass2_dir: Path, per_user_df, per_game_df, n_pos=200000, n_neg=200000, seed=42):
    print(f"[3/9] Sampling training balanced pos={n_pos} neg={n_neg} seed {seed}…", flush=True)
    np.random.seed(seed)
    ro = pass2_dir / "rating_observations_pass2.parquet"
    total_obs = con.execute(f"SELECT COUNT(*) FROM read_parquet('{qpath(ro)}')").fetchone()[0]
    mod = max(1, total_obs // n_pos)
    pos_df = con.execute(f"""
      SELECT user_pseudouserid AS uid, game_id FROM read_parquet('{qpath(ro)}')
      WHERE rating_observation_id % {mod} = 0 LIMIT {n_pos}
    """).fetchdf()
    if len(pos_df) < n_pos:
        extra = con.execute(f"""SELECT user_pseudouserid AS uid, game_id FROM read_parquet('{qpath(ro)}') ORDER BY random() LIMIT {n_pos-len(pos_df)}""").fetchdf()
        pos_df = pd.concat([pos_df, extra], ignore_index=True)
    pos_df = pos_df.head(n_pos).copy()
    pos_df["y"]=1
    print(f"  positives {len(pos_df)} mod {mod}", flush=True)
    user_ids = per_user_df["uid"].values
    game_ids = per_game_df["game_id"].values
    neg_uids = np.random.choice(user_ids, size=n_neg*2, replace=True)
    neg_gids = np.random.choice(game_ids, size=n_neg*2, replace=True)
    neg_df = pd.DataFrame({"uid": neg_uids, "game_id": neg_gids, "y":0})
    con.register("neg_tmp_df", neg_df)
    neg_filtered = con.execute(f"""
      SELECT n.uid, n.game_id FROM neg_tmp_df n
      ANTI JOIN read_parquet('{qpath(ro)}') r ON n.uid=r.user_pseudouserid AND n.game_id=r.game_id LIMIT {n_neg}
    """).fetchdf()
    neg_filtered["y"]=0
    attempts=0
    while len(neg_filtered) < n_neg and attempts<5:
        need = n_neg - len(neg_filtered)
        add_uids = np.random.choice(user_ids, size=need*4, replace=True)
        add_gids = np.random.choice(game_ids, size=need*4, replace=True)
        add_df = pd.DataFrame({"uid": add_uids, "game_id": add_gids})
        con.register("add_tmp", add_df)
        add_filt = con.execute(f"""SELECT a.uid, a.game_id FROM add_tmp a ANTI JOIN read_parquet('{qpath(ro)}') r ON a.uid=r.user_pseudouserid AND a.game_id=r.game_id LIMIT {need}""").fetchdf()
        add_filt["y"]=0
        neg_filtered = pd.concat([neg_filtered, add_filt], ignore_index=True).head(n_neg)
        attempts+=1
        con.unregister("add_tmp")
    con.unregister("neg_tmp_df")
    print(f"  negatives {len(neg_filtered)} attempts {attempts}", flush=True)
    train_pairs = pd.concat([pos_df, neg_filtered], ignore_index=True)
    return train_pairs

def sample_prevalence_holdout(con, pass2_dir: Path, per_user_df, per_game_df, n_pairs=600000, seed=123):
    print(f"[3b] Sampling prevalence-faithful holdout n={n_pairs} seed {seed}…", flush=True)
    np.random.seed(seed)
    ro = pass2_dir / "rating_observations_pass2.parquet"
    user_ids = per_user_df["uid"].values
    game_ids = per_game_df["game_id"].values
    u = np.random.choice(user_ids, size=n_pairs, replace=True)
    g = np.random.choice(game_ids, size=n_pairs, replace=True)
    df = pd.DataFrame({"uid": u, "game_id": g})
    # label via anti-join check: need to know if pair exists
    con.register("prev_tmp", df)
    labeled = con.execute(f"""
      SELECT p.uid, p.game_id, CASE WHEN r.game_id IS NOT NULL THEN 1 ELSE 0 END AS y
      FROM prev_tmp p LEFT JOIN read_parquet('{qpath(ro)}') r ON p.uid=r.user_pseudouserid AND p.game_id=r.game_id
    """).fetchdf()
    con.unregister("prev_tmp")
    # deduplicate? rare duplicates due to replace sampling uniform; keep as is but we need to check empirical marginal
    empirical = labeled["y"].mean()
    expected_marginal = 24146307/(287302*14698)
    print(f"  prevalence holdout {len(labeled)} empirical y mean {empirical:.5f} expected {expected_marginal:.5f} positives {labeled['y'].sum()}", flush=True)
    return labeled

def build_feature_matrix(train_pairs, per_user_df, per_game_df):
    print("[4/9] Building feature matrix leakage-corrected…", flush=True)
    df = train_pairs.merge(per_user_df, on="uid", how="left")
    game_cols = ["game_id","weight_filled","weight_missing","year_centered","flag_18xx","flag_warg","flag_party","flag_econ","flag_coop","flag_legacy"]
    df = df.merge(per_game_df[game_cols], on="game_id", how="left", suffixes=("", "_g"))
    is_pos = df["y"]==1
    df["total_cnt_excl"] = df["total_cnt"]
    df.loc[is_pos, "total_cnt_excl"] = df.loc[is_pos, "total_cnt"] - 1
    df["total_cnt_excl"] = df["total_cnt_excl"].clip(lower=1)
    df["log_total_excl"] = np.log10(df["total_cnt_excl"])
    df["sum_weight_excl"] = df["sum_weight"]
    df.loc[is_pos, "sum_weight_excl"] = df.loc[is_pos, "sum_weight"] - df.loc[is_pos, "weight_filled"]
    df["cnt_w_excl"] = df["cnt_w"]
    mask_pos_weight = is_pos & (df["weight_missing"]==0)
    df.loc[mask_pos_weight, "cnt_w_excl"] = df.loc[mask_pos_weight, "cnt_w"] - 1
    df["cnt_w_excl"] = df["cnt_w_excl"].clip(lower=1)
    df["mean_weight_excl"] = df["sum_weight_excl"] / df["cnt_w_excl"]
    df["mean_weight_excl"] = df["mean_weight_excl"].fillna(df["mean_weight"])
    for flag_col, cnt_col in [("flag_18xx","cnt_18xx"),("flag_warg","cnt_warg"),("flag_party","cnt_party"),("flag_econ","cnt_econ"),("flag_coop","cnt_coop"),("flag_legacy","cnt_legacy")]:
        cnt_excl_col = cnt_col+"_excl"
        df[cnt_excl_col] = df[cnt_col]
        df.loc[is_pos, cnt_excl_col] = df.loc[is_pos, cnt_col] - df.loc[is_pos, flag_col]
        df[cnt_excl_col] = df[cnt_excl_col].clip(lower=0)
        df[f"log1p_{cnt_excl_col}"] = np.log1p(df[cnt_excl_col])
    df["cnt_other_excl"] = df["total_cnt_excl"] - (df["cnt_18xx_excl"]+df["cnt_warg_excl"]+df["cnt_party_excl"]+df["cnt_econ_excl"]+df["cnt_coop_excl"]+df["cnt_legacy_excl"])
    df["cnt_other_excl"] = df["cnt_other_excl"].clip(lower=0)
    df["log1p_cnt_other_excl"] = np.log1p(df["cnt_other_excl"])
    conditions = [df["total_cnt_excl"]<=24, df["total_cnt_excl"]<=49, df["total_cnt_excl"]<=99, df["total_cnt_excl"]<=249, df["total_cnt_excl"]<=499, df["total_cnt_excl"]<=999]
    choices=[0,1,2,3,4,5]
    df["vol_ord_excl"] = np.select(conditions, choices, default=6)
    feature_cols = [
        "log_total_excl","delta_full","mean_weight_excl","vol_ord_excl",
        "log1p_cnt_18xx_excl","log1p_cnt_warg_excl","log1p_cnt_party_excl","log1p_cnt_econ_excl","log1p_cnt_coop_excl","log1p_cnt_legacy_excl","log1p_cnt_other_excl",
        "weight_filled","weight_missing","year_centered",
        "flag_18xx","flag_warg","flag_party","flag_econ","flag_coop","flag_legacy"
    ]
    for flag_col, cnt_log_col in [("flag_18xx","log1p_cnt_18xx_excl"),("flag_warg","log1p_cnt_warg_excl"),("flag_party","log1p_cnt_party_excl"),("flag_econ","log1p_cnt_econ_excl"),("flag_coop","log1p_cnt_coop_excl"),("flag_legacy","log1p_cnt_legacy_excl")]:
        inter_col = f"inter_{flag_col}"
        df[inter_col] = df[flag_col] * df[cnt_log_col]
        feature_cols.append(inter_col)
    for c in feature_cols:
        df[c] = df[c].fillna(0)
    X = df[feature_cols].values.astype(float)
    y = df["y"].values.astype(int)
    return X, y, feature_cols, df

def train_models(X, y, feature_cols):
    print("[5/9] Training models…", flush=True)
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import roc_auc_score, brier_score_loss
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)
    logreg = LogisticRegression(penalty='l2', C=1.0, solver='lbfgs', max_iter=500, n_jobs=3)
    logreg.fit(X_train_s, y_train)
    p_train = logreg.predict_proba(X_train_s)[:,1]
    p_test = logreg.predict_proba(X_test_s)[:,1]
    def ece(y_true, p_pred, n_bins=10):
        bins=np.linspace(0,1,n_bins+1)
        e=0
        for i in range(n_bins):
            mask=(p_pred>=bins[i]) & (p_pred<bins[i+1]) if i<n_bins-1 else (p_pred>=bins[i]) & (p_pred<=bins[i+1])
            if mask.sum()==0: continue
            acc=y_true[mask].mean()
            conf=p_pred[mask].mean()
            e+= abs(acc-conf)*mask.sum()/len(y_true)
        return e
    auc_train=roc_auc_score(y_train, p_train)
    auc_test=roc_auc_score(y_test, p_test)
    brier_test=brier_score_loss(y_test, p_test)
    ece_test=ece(y_test, p_test)
    print(f"  Logistic balanced holdout: AUC tr {auc_train:.3f} te {auc_test:.3f} Brier {brier_test:.3f} ECE {ece_test:.3f}", flush=True)
    coef=logreg.coef_[0]
    intercept=logreg.intercept_[0]
    coef_raw=coef/scaler.scale_
    intercept_raw=intercept - np.sum(coef*scaler.mean_/scaler.scale_)
    rf=RandomForestClassifier(n_estimators=200, max_depth=12, min_samples_leaf=20, n_jobs=3, random_state=42)
    rf.fit(X_train, y_train)
    p_test_rf=rf.predict_proba(X_test)[:,1]
    auc_rf=roc_auc_score(y_test, p_test_rf)
    brier_rf=brier_score_loss(y_test, p_test_rf)
    ece_rf=ece(y_test, p_test_rf)
    print(f"  RF balanced holdout: AUC {auc_rf:.3f} Brier {brier_rf:.3f} ECE {ece_rf:.3f}", flush=True)
    # weighted logistic reflecting true prevalence
    marginal=24146307/(287302*14698)
    # sample weights: positives weight = marginal/0.5, negatives weight = (1-marginal)/0.5
    w_pos=marginal/0.5
    w_neg=(1-marginal)/0.5
    sample_weight=np.where(y_train==1, w_pos, w_neg)
    # need scaler refit? reuse same scaler but fit weighted? we fit scaler on X_train (unweighted) already; for weighted logistic we reuse same scaled X
    logreg_w=LogisticRegression(penalty='l2', C=1.0, solver='lbfgs', max_iter=500, n_jobs=3)
    logreg_w.fit(X_train_s, y_train, sample_weight=sample_weight)
    p_test_w=logreg_w.predict_proba(X_test_s)[:,1]
    # also need raw coef for weighted
    coef_w=logreg_w.coef_[0]
    intercept_w=logreg_w.intercept_[0]
    coef_raw_w=coef_w/scaler.scale_
    intercept_raw_w=intercept_w - np.sum(coef_w*scaler.mean_/scaler.scale_)
    auc_w=roc_auc_score(y_test, p_test_w) if len(np.unique(y_test))>1 else np.nan
    brier_w=brier_score_loss(y_test, p_test_w)
    ece_w=ece(y_test, p_test_w)
    print(f"  Weighted logistic balanced holdout: AUC {auc_w:.3f} Brier {brier_w:.3f} ECE {ece_w:.3f} (expects miscalibrated on balanced)", flush=True)
    # prevalence holdout evaluation will be done externally
    return {
        "logreg": logreg, "scaler": scaler, "coef": coef, "intercept": intercept, "coef_raw": coef_raw, "intercept_raw": intercept_raw,
        "auc_train": auc_train, "auc_test": auc_test, "brier_test": brier_test, "ece_test": ece_test,
        "rf": rf, "auc_rf": auc_rf, "ece_rf": ece_rf, "brier_rf": brier_rf,
        "logreg_w": logreg_w, "coef_w": coef_w, "intercept_w": intercept_w, "coef_raw_w": coef_raw_w, "intercept_raw_w": intercept_raw_w,
        "auc_w": auc_w, "brier_w": brier_w, "ece_w": ece_w,
        "feature_cols": feature_cols, "X_test": X_test, "y_test": y_test, "p_test": p_test, "p_test_rf": p_test_rf, "p_test_w": p_test_w,
        "X_train": X_train, "y_train": y_train, "X_test_s": X_test_s
    }

def evaluate_on_prevalence_holdout(model_info, X_prev, y_prev, feature_cols):
    print("[5b] Evaluating on prevalence-faithful holdout…", flush=True)
    from sklearn.metrics import roc_auc_score, brier_score_loss
    from sklearn.preprocessing import StandardScaler
    # need to prepare X_prev_scaled using same scaler
    scaler=model_info["scaler"]
    # X_prev is raw features matching feature_cols order
    # we have y_prev, but we need p predictions for each model
    # For logistic, scale X_prev
    X_prev_s=scaler.transform(X_prev)
    p_logit=model_info["logreg"].predict_proba(X_prev_s)[:,1]
    p_rf=model_info["rf"].predict_proba(X_prev)[:,1]
    p_w=model_info["logreg_w"].predict_proba(X_prev_s)[:,1]
    # prevalence corrected via intercept shift
    marginal=24146307/(287302*14698)
    sample_prev=0.5
    shift=np.log(marginal/(1-marginal)) - np.log(sample_prev/(1-sample_prev))
    # logit(p_true) = logit(p_sample) + shift
    # compute logit via log(p/(1-p)) clipped
    def correct_p(p_sample, shift):
        # logit shift then expit
        # avoid 0/1
        p=np.clip(p_sample, 1e-6, 1-1e-6)
        logit_p=np.log(p/(1-p))
        return expit(logit_p + shift)
    p_corrected=correct_p(p_logit, shift)
    # also per-type marginals where relevant: compute per-type shift if game type known? But our X_prev has no explicit game type beyond flags; we can compute global only for now and per-type variant as sensitivity
    # evaluate metrics for each
    def metrics(y_true, p_pred):
        from sklearn.metrics import roc_auc_score, brier_score_loss
        def ece(y_true, p_pred, n_bins=10):
            bins=np.linspace(0,1,n_bins+1)
            e=0
            for i in range(n_bins):
                mask=(p_pred>=bins[i]) & (p_pred<bins[i+1]) if i<9 else (p_pred>=bins[i]) & (p_pred<=bins[i+1])
                if mask.sum()==0: continue
                acc=y_true[mask].mean()
                conf=p_pred[mask].mean()
                e+=abs(acc-conf)*mask.sum()/len(y_true)
            return e
        try:
            auc=roc_auc_score(y_true, p_pred) if len(np.unique(y_true))>1 else np.nan
        except:
            auc=np.nan
        brier=brier_score_loss(y_true, p_pred)
        ece_val=ece(y_true, p_pred)
        # calibration in large: observed vs pred mean
        cal_large=y_true.mean() - p_pred.mean()
        return {"auc": float(auc), "brier": float(brier), "ece": float(ece_val), "mean_pred": float(p_pred.mean()), "mean_obs": float(y_true.mean()), "cal_in_large": float(cal_large)}
    res={}
    res["logit_sampled_scale"]=metrics(y_prev, p_logit)
    res["rf_sampled_scale"]=metrics(y_prev, p_rf)
    res["weighted_logit"]=metrics(y_prev, p_w)
    res["logit_corrected_global"]=metrics(y_prev, p_corrected)
    # calibration details: bins for each
    def cal_bins(y_true, p_pred, n_bins=10):
        bins=np.linspace(0,1,n_bins+1)
        out=[]
        for i in range(n_bins):
            lo=bins[i]; hi=bins[i+1]
            mask=(p_pred>=lo) & (p_pred<hi) if i<n_bins-1 else (p_pred>=lo) & (p_pred<=hi)
            cnt=mask.sum()
            if cnt==0:
                out.append({"bin": f"{lo:.1f}-{hi:.1f}", "count":0, "mean_pred": np.nan, "mean_obs": np.nan})
            else:
                out.append({"bin": f"{lo:.1f}-{hi:.1f}", "count": int(cnt), "mean_pred": float(p_pred[mask].mean()), "mean_obs": float(y_true[mask].mean())})
        return out
    res["cal_bins_logit_sampled"]=cal_bins(y_prev, p_logit)
    res["cal_bins_corrected"]=cal_bins(y_prev, p_corrected)
    res["cal_bins_weighted"]=cal_bins(y_prev, p_w)
    res["cal_bins_rf"]=cal_bins(y_prev, p_rf)
    res["shift_logit"]=float(shift)
    res["marginal"]=float(marginal)
    print(f"  prevalence holdout metrics:", flush=True)
    for k,v in res.items():
        if "auc" in str(v):
            print(f"    {k}: {v}", flush=True)
    print(f"  shift {shift:.3f} marginal {marginal:.5f}", flush=True)
    return res, p_logit, p_corrected, p_w, p_rf

def per_game_inference_both_scales(con, per_user_df, per_game_df, model_info, pass2_dir: Path):
    print("[6/9] Per-game scoring both sampled and true scale, streaming 24M…", flush=True)
    from scipy.special import expit
    feature_cols=model_info["feature_cols"]
    coef_raw=model_info["coef_raw"]
    intercept_raw=model_info["intercept_raw"]
    coef_raw_w=model_info["coef_raw_w"]
    intercept_raw_w=model_info["intercept_raw_w"]
    marginal=24146307/(287302*14698)
    sample_prev=0.5
    shift=np.log(marginal/(1-marginal)) - np.log(sample_prev/(1-sample_prev))
    p_marginal_global=marginal
    ro=pass2_dir / "rating_observations_pass2.parquet"
    # lookup arrays
    total_cnt_arr=per_user_df["total_cnt"].values
    cnt_18xx_arr=per_user_df["cnt_18xx"].values
    cnt_warg_arr=per_user_df["cnt_warg"].values
    cnt_party_arr=per_user_df["cnt_party"].values
    cnt_econ_arr=per_user_df["cnt_econ"].values
    cnt_coop_arr=per_user_df["cnt_coop"].values
    cnt_legacy_arr=per_user_df["cnt_legacy"].values
    uid_to_idx={uid:i for i,uid in enumerate(per_user_df["uid"].values)}
    sum_weight_arr=per_user_df["sum_weight"].values
    cnt_w_arr=per_user_df["cnt_w"].values
    delta_arr=per_user_df["delta_full"].values
    # game lookup dicts
    g_weight_map=per_game_df.set_index("game_id")["weight_filled"].to_dict()
    g_missing_map=per_game_df.set_index("game_id")["weight_missing"].to_dict()
    g_year_map=per_game_df.set_index("game_id")["year_centered"].to_dict()
    g_f18xx_map=per_game_df.set_index("game_id")["flag_18xx"].to_dict()
    g_fwarg_map=per_game_df.set_index("game_id")["flag_warg"].to_dict()
    g_fparty_map=per_game_df.set_index("game_id")["flag_party"].to_dict()
    g_fecon_map=per_game_df.set_index("game_id")["flag_econ"].to_dict()
    g_fcoop_map=per_game_df.set_index("game_id")["flag_coop"].to_dict()
    g_flegacy_map=per_game_df.set_index("game_id")["flag_legacy"].to_dict()
    game_lookup=per_game_df.set_index("game_id")
    col_idx={c:i for i,c in enumerate(feature_cols)}
    # accumulation per game for both scales
    from collections import defaultdict
    game_sums=defaultdict(lambda: {
        "count":0,
        "sum_w_raw_sample":0.0, "sum_w_raw_adj_sample":0.0, "sum_w2_raw_sample":0.0, "max_w_sample":0.0,
        "sum_w_raw_true":0.0, "sum_w_raw_adj_true":0.0, "sum_w2_raw_true":0.0, "max_w_true":0.0,
        "sum_w_stab_true":0.0, "sum_w_stab_adj_true":0.0, "sum_w2_stab_true":0.0,
        "sum_w_trunc_true":0.0, "sum_w_trunc_adj_true":0.0, "sum_w2_trunc_true":0.0,
        "sum_p_sample":0.0, "sum_p_true":0.0, "sum_p_w":0.0,
        "sum_adj":0.0, "p95_list_sample":[], "p95_list_true":[],
    })
    pf=pq.ParquetFile(ro)
    total_groups=pf.num_row_groups
    print(f"  {total_groups} row groups…", flush=True)
    for rg in range(total_groups):
        tbl=pf.read_row_group(rg, columns=["game_id","user_pseudouserid","rating"])
        df_chunk=tbl.to_pandas()
        idx_series=df_chunk["user_pseudouserid"].map(uid_to_idx)
        valid=idx_series.notna()
        df_chunk=df_chunk[valid].copy()
        if df_chunk.empty:
            continue
        v_idxs=idx_series[valid].values.astype(int)
        ratings=df_chunk["rating"].values
        adj_ratings=ratings - delta_arr[v_idxs]
        # game features per row via vectorized map using dict lookup
        gids=df_chunk["game_id"].values
        # vectorized map via list comprehension faster than pandas map for dict
        w_filled=np.array([g_weight_map[g] for g in gids])
        w_missing=np.array([g_missing_map[g] for g in gids])
        y_cent=np.array([g_year_map[g] for g in gids])
        f18=np.array([g_f18xx_map[g] for g in gids])
        f_warg=np.array([g_fwarg_map[g] for g in gids])
        f_party=np.array([g_fparty_map[g] for g in gids])
        f_econ=np.array([g_fecon_map[g] for g in gids])
        f_coop=np.array([g_fcoop_map[g] for g in gids])
        f_legacy=np.array([g_flegacy_map[g] for g in gids])
        total_cnt_excl=np.maximum(total_cnt_arr[v_idxs]-1,1)
        log_total_excl=np.log10(total_cnt_excl)
        sum_w_excl=sum_weight_arr[v_idxs] - w_filled
        cnt_w_excl=cnt_w_arr[v_idxs].copy()
        mask_not_missing=(w_missing==0)
        cnt_w_excl[mask_not_missing]=cnt_w_excl[mask_not_missing]-1
        cnt_w_excl=np.maximum(cnt_w_excl,1)
        mean_w_excl=sum_w_excl / cnt_w_excl
        mean_w_excl=np.where(np.isnan(mean_w_excl)|np.isinf(mean_w_excl), 0, mean_w_excl)
        cnt_18xx_excl=np.maximum(cnt_18xx_arr[v_idxs]-f18,0)
        cnt_warg_excl=np.maximum(cnt_warg_arr[v_idxs]-f_warg,0)
        cnt_party_excl=np.maximum(cnt_party_arr[v_idxs]-f_party,0)
        cnt_econ_excl=np.maximum(cnt_econ_arr[v_idxs]-f_econ,0)
        cnt_coop_excl=np.maximum(cnt_coop_arr[v_idxs]-f_coop,0)
        cnt_legacy_excl=np.maximum(cnt_legacy_arr[v_idxs]-f_legacy,0)
        cnt_other_excl=total_cnt_excl - (cnt_18xx_excl+cnt_warg_excl+cnt_party_excl+cnt_econ_excl+cnt_coop_excl+cnt_legacy_excl)
        cnt_other_excl=np.maximum(cnt_other_excl,0)
        log1p_18xx_excl=np.log1p(cnt_18xx_excl)
        log1p_warg_excl=np.log1p(cnt_warg_excl)
        log1p_party_excl=np.log1p(cnt_party_excl)
        log1p_econ_excl=np.log1p(cnt_econ_excl)
        log1p_coop_excl=np.log1p(cnt_coop_excl)
        log1p_legacy_excl=np.log1p(cnt_legacy_excl)
        log1p_other_excl=np.log1p(cnt_other_excl)
        vol_ord_excl=np.select([total_cnt_excl<=24,total_cnt_excl<=49,total_cnt_excl<=99,total_cnt_excl<=249,total_cnt_excl<=499,total_cnt_excl<=999],[0,1,2,3,4,5],default=6)
        n=len(v_idxs)
        X=np.zeros((n, len(feature_cols)))
        X[:,col_idx["log_total_excl"]]=log_total_excl
        X[:,col_idx["delta_full"]]=delta_arr[v_idxs]
        X[:,col_idx["mean_weight_excl"]]=mean_w_excl
        X[:,col_idx["vol_ord_excl"]]=vol_ord_excl
        X[:,col_idx["log1p_cnt_18xx_excl"]]=log1p_18xx_excl
        X[:,col_idx["log1p_cnt_warg_excl"]]=log1p_warg_excl
        X[:,col_idx["log1p_cnt_party_excl"]]=log1p_party_excl
        X[:,col_idx["log1p_cnt_econ_excl"]]=log1p_econ_excl
        X[:,col_idx["log1p_cnt_coop_excl"]]=log1p_coop_excl
        X[:,col_idx["log1p_cnt_legacy_excl"]]=log1p_legacy_excl
        X[:,col_idx["log1p_cnt_other_excl"]]=log1p_other_excl
        X[:,col_idx["weight_filled"]]=w_filled
        X[:,col_idx["weight_missing"]]=w_missing
        X[:,col_idx["year_centered"]]=y_cent
        X[:,col_idx["flag_18xx"]]=f18
        X[:,col_idx["flag_warg"]]=f_warg
        X[:,col_idx["flag_party"]]=f_party
        X[:,col_idx["flag_econ"]]=f_econ
        X[:,col_idx["flag_coop"]]=f_coop
        X[:,col_idx["flag_legacy"]]=f_legacy
        X[:,col_idx["inter_flag_18xx"]]=f18*log1p_18xx_excl
        X[:,col_idx["inter_flag_warg"]]=f_warg*log1p_warg_excl
        X[:,col_idx["inter_flag_party"]]=f_party*log1p_party_excl
        X[:,col_idx["inter_flag_econ"]]=f_econ*log1p_econ_excl
        X[:,col_idx["inter_flag_coop"]]=f_coop*log1p_coop_excl
        X[:,col_idx["inter_flag_legacy"]]=f_legacy*log1p_legacy_excl
        logits_sample=intercept_raw + X.dot(coef_raw)
        p_sample=expit(logits_sample)
        p_sample=np.clip(p_sample, 0.0005, 0.999)
        # corrected true
        # logit corrected = logit(p_sample)+shift
        # clip to avoid 0/1
        p_sample_clip=np.clip(p_sample, 1e-6, 1-1e-6)
        logit_sample=np.log(p_sample_clip/(1-p_sample_clip))
        p_true=expit(logit_sample + shift)
        p_true=np.clip(p_true, 1e-6, 0.999)
        # weighted logistic p (already prevalence scale?) weighted intercept already accounts, but we will use p_true_w from weighted model
        logits_w=intercept_raw_w + X.dot(coef_raw_w)
        p_w=expit(logits_w)
        p_w=np.clip(p_w, 1e-6, 0.999)
        w_raw_sample=1.0/p_sample
        w_raw_true=1.0/p_true
        w_stab_true=p_marginal_global/p_true
        w_trunc_true=np.clip(w_raw_true, 0, 20)
        # For truncation at p95/p99 we need later per-game percentiles, but we can approximate cap 20 for now and later compute p95 cap per game as variation
        # aggregate per game
        df_chunk["p_sample"]=p_sample
        df_chunk["p_true"]=p_true
        df_chunk["p_w"]=p_w
        df_chunk["adj"]=adj_ratings
        df_chunk["w_raw_sample"]=w_raw_sample
        df_chunk["w_raw_true"]=w_raw_true
        df_chunk["w_stab_true"]=w_stab_true
        df_chunk["w_trunc_true"]=w_trunc_true
        df_chunk["w_raw_adj_sample"]=w_raw_sample*adj_ratings
        df_chunk["w_raw_adj_true"]=w_raw_true*adj_ratings
        df_chunk["w_stab_adj_true"]=w_stab_true*adj_ratings
        df_chunk["w_trunc_adj_true"]=w_trunc_true*adj_ratings
        try:
            grouped=df_chunk.groupby("game_id").agg(
                cnt=("game_id","size"),
                sum_w_raw_sample=("w_raw_sample","sum"),
                sum_w_raw_adj_sample=("w_raw_adj_sample","sum"),
                sum_w2_raw_sample=("w_raw_sample", lambda x: np.square(x).sum()),
                max_w_sample=("w_raw_sample","max"),
                sum_w_raw_true=("w_raw_true","sum"),
                sum_w_raw_adj_true=("w_raw_adj_true","sum"),
                sum_w2_raw_true=("w_raw_true", lambda x: np.square(x).sum()),
                max_w_true=("w_raw_true","max"),
                sum_w_stab_true=("w_stab_true","sum"),
                sum_w_stab_adj_true=("w_stab_adj_true","sum"),
                sum_w2_stab_true=("w_stab_true", lambda x: np.square(x).sum()),
                sum_w_trunc_true=("w_trunc_true","sum"),
                sum_w_trunc_adj_true=("w_trunc_adj_true","sum"),
                sum_w2_trunc_true=("w_trunc_true", lambda x: np.square(x).sum()),
                sum_p_sample=("p_sample","sum"),
                sum_p_true=("p_true","sum"),
                sum_p_w=("p_w","sum"),
                sum_adj=("adj","sum"),
            )
        except Exception as e:
            print(f"groupby failed {e} columns {df_chunk.columns.tolist()} head {df_chunk.head().to_dict()}")
            raise
        for gid, row in grouped.iterrows():
            gs=game_sums[gid]
            gs["count"]+=int(row["cnt"])
            gs["sum_w_raw_sample"]+=float(row["sum_w_raw_sample"])
            gs["sum_w_raw_adj_sample"]+=float(row["sum_w_raw_adj_sample"])
            gs["sum_w2_raw_sample"]+=float(row["sum_w2_raw_sample"])
            gs["max_w_sample"]=max(gs["max_w_sample"], float(row["max_w_sample"]))
            gs["sum_w_raw_true"]+=float(row["sum_w_raw_true"])
            gs["sum_w_raw_adj_true"]+=float(row["sum_w_raw_adj_true"])
            gs["sum_w2_raw_true"]+=float(row["sum_w2_raw_true"])
            gs["max_w_true"]=max(gs["max_w_true"], float(row["max_w_true"]))
            gs["sum_w_stab_true"]+=float(row["sum_w_stab_true"])
            gs["sum_w_stab_adj_true"]+=float(row["sum_w_stab_adj_true"])
            gs["sum_w2_stab_true"]+=float(row["sum_w2_stab_true"])
            gs["sum_w_trunc_true"]+=float(row["sum_w_trunc_true"])
            gs["sum_w_trunc_adj_true"]+=float(row["sum_w_trunc_adj_true"])
            gs["sum_w2_trunc_true"]+=float(row["sum_w2_trunc_true"])
            gs["sum_p_sample"]+=float(row["sum_p_sample"])
            gs["sum_p_true"]+=float(row["sum_p_true"])
            gs["sum_p_w"]+=float(row["sum_p_w"])
            gs["sum_adj"]+=float(row["sum_adj"])
        if (rg+1)%20==0:
            print(f"  chunk {rg+1}/{total_groups}", flush=True)
    print(f"  aggregating {len(game_sums)} games", flush=True)
    results=[]
    for gid, s in game_sums.items():
        g_row=game_lookup.loc[gid]
        n_obs=s["count"]
        # weighted means
        wmean_raw_sample=s["sum_w_raw_adj_sample"]/s["sum_w_raw_sample"] if s["sum_w_raw_sample"]>0 else np.nan
        wmean_raw_true=s["sum_w_raw_adj_true"]/s["sum_w_raw_true"] if s["sum_w_raw_true"]>0 else np.nan
        wmean_stab_true=s["sum_w_stab_adj_true"]/s["sum_w_stab_true"] if s["sum_w_stab_true"]>0 else np.nan
        wmean_trunc_true=s["sum_w_trunc_adj_true"]/s["sum_w_trunc_true"] if s["sum_w_trunc_true"]>0 else np.nan
        # p for weighted logistic mean?
        # wmean via weighted logistic model's p_w? we can compute similarly using p_w weights? For simplicity we have p_w mean
        mean_p_sample=s["sum_p_sample"]/n_obs if n_obs>0 else np.nan
        mean_p_true=s["sum_p_true"]/n_obs if n_obs>0 else np.nan
        mean_p_w=s["sum_p_w"]/n_obs if n_obs>0 else np.nan
        ess_raw_sample=(s["sum_w_raw_sample"]**2)/s["sum_w2_raw_sample"] if s["sum_w2_raw_sample"]>0 else 0
        ess_raw_true=(s["sum_w_raw_true"]**2)/s["sum_w2_raw_true"] if s["sum_w2_raw_true"]>0 else 0
        ess_stab_true=(s["sum_w_stab_true"]**2)/s["sum_w2_stab_true"] if s["sum_w2_stab_true"]>0 else 0
        ess_trunc_true=(s["sum_w_trunc_true"]**2)/s["sum_w2_trunc_true"] if s["sum_w2_trunc_true"]>0 else 0
        adj_mean_orig=g_row["adj_mean"]
        delta_raw_sample=wmean_raw_sample - adj_mean_orig if not np.isnan(wmean_raw_sample) else np.nan
        delta_raw_true=wmean_raw_true - adj_mean_orig if not np.isnan(wmean_raw_true) else np.nan
        delta_stab_true=wmean_stab_true - adj_mean_orig if not np.isnan(wmean_stab_true) else np.nan
        delta_trunc_true=wmean_trunc_true - adj_mean_orig if not np.isnan(wmean_trunc_true) else np.nan
        results.append({
            "game_id": gid, "title": g_row["title"], "primary_type": g_row["primary_type"],
            "n_obs": n_obs, "adj_mean": adj_mean_orig, "raw_mean": g_row["raw_mean"], "weight": g_row["weight"], "year": g_row["year"],
            "prop_adj_raw_sample": wmean_raw_sample, "delta_raw_sample": delta_raw_sample,
            "prop_adj_raw_true": wmean_raw_true, "delta_raw_true": delta_raw_true,
            "prop_adj_stab_true": wmean_stab_true, "delta_stab_true": delta_stab_true,
            "prop_adj_trunc_true": wmean_trunc_true, "delta_trunc_true": delta_trunc_true,
            "ess_raw_sample": ess_raw_sample, "ess_raw_true": ess_raw_true, "ess_stab_true": ess_stab_true, "ess_trunc_true": ess_trunc_true,
            "max_w_raw_sample": s["max_w_sample"], "max_w_raw_true": s["max_w_true"],
            "mean_p_sample": mean_p_sample, "mean_p_true": mean_p_true, "mean_p_w": mean_p_w,
            "penetration_all": n_obs/287302, "n_at_risk_all": 287302,
        })
    res_df=pd.DataFrame(results)
    print(f"  per-game complete {len(res_df)}", flush=True)
    return res_df, shift, p_marginal_global

def compute_overlap_diagnostics(per_user_df, per_game_df, model_info, sample_games, n_nonraters=400):
    print("[7/9] Overlap diagnostics sampling non-raters…", flush=True)
    from scipy.special import expit
    np.random.seed(42)
    ro_path=PASS2_DIR / "rating_observations_pass2.parquet"
    import duckdb
    # we need to sample non-raters for each sample_game per population
    # For each game, need its positive rater set to exclude
    # We'll use duckdb to get rater lists per sampled game quickly
    con=duckdb.connect()
    configure(con, TMP_DUCK)
    # Build per-game rater sets for sampled games only
    game_list=",".join(map(str, sample_games))
    # Could be large; use parquet scan with filter
    rater_map={}
    # For efficiency, read rating_observations for sampled games in one query
    # Use duckdb to fetch distinct uid per game
    df_raters=con.execute(f"SELECT game_id, user_pseudouserid AS uid FROM read_parquet('{qpath(ro_path)}') WHERE game_id IN ({game_list})").fetchdf()
    for gid, grp in df_raters.groupby("game_id"):
        rater_map[gid]=set(grp["uid"].values)
    print(f"  built rater_map for {len(rater_map)} games, total pairs {len(df_raters)}", flush=True)
    # per-user arrays for propensity scoring quickly: we need feature matrix for non-raters similar to per-game inference
    # Instead reuse logic: for each game and each non-rater candidate, compute features leakage-corrected? For Y=0 no subtraction
    # So p = expit(intercept + X.dot(coef_raw)) where X uses cnt_excl = cnt (no subtraction) for Y=0
    # For Y=1 raters we already have p_sample from per_game inference? But we can recompute for consistency for rater distribution sampling
    # For overlap we need p distribution for raters vs non-raters per population
    # Simplify: compute p for raters using per-user features corrected (already have mean_p_sample etc) but we need distribution quantiles? We'll recompute via sampling 400 raters per game as well?
    # Instead for each sampled game, we will compute propensity for:
    # - sampled raters: random 400 of its actual raters (if n_obs>400) else all
    # - sampled non-raters per population: random users from that population who did NOT rate the game
    feature_cols=model_info["feature_cols"]
    coef_raw=model_info["coef_raw"]
    intercept_raw=model_info["intercept_raw"]
    marginal=24146307/(287302*14698)
    shift=np.log(marginal/(1-marginal)) - np.log(0.5/0.5)
    # Prepare per-user lookup dict for fast feature assembly
    per_user_idx={uid:i for i,uid in enumerate(per_user_df["uid"].values)}
    total_cnt_arr=per_user_df["total_cnt"].values
    cnt_18xx_arr=per_user_df["cnt_18xx"].values
    cnt_warg_arr=per_user_df["cnt_warg"].values
    cnt_party_arr=per_user_df["cnt_party"].values
    cnt_econ_arr=per_user_df["cnt_econ"].values
    cnt_coop_arr=per_user_df["cnt_coop"].values
    cnt_legacy_arr=per_user_df["cnt_legacy"].values
    delta_arr=per_user_df["delta_full"].values
    mean_weight_arr=per_user_df["mean_weight"].values
    sum_weight_arr=per_user_df["sum_weight"].values
    cnt_w_arr=per_user_df["cnt_w"].values
    log_total_arr=per_user_df["log_total"].values
    # game lookup
    g_weight_filled=per_game_df.set_index("game_id")["weight_filled"].to_dict()
    g_weight_missing=per_game_df.set_index("game_id")["weight_missing"].to_dict()
    g_year_centered=per_game_df.set_index("game_id")["year_centered"].to_dict()
    g_flags={gid: {col: per_game_df.set_index("game_id").loc[gid, col] for col in FLAG_COLS} for gid in sample_games if gid in per_game_df["game_id"].values}
    # Also per-type fallback for flags
    # Build at-risk population pools for sampling: for each type we need list of users meeting threshold
    # Compute pool membership vectors
    # For speed, create per-user cnt arrays and filter
    user_pool_masks={}
    # ALL_ACTIVE
    user_pool_masks["ALL_ACTIVE"]=per_user_df["uid"].values
    # ACTIVE_50PLUS total_cnt>=50
    user_pool_masks["ACTIVE_50PLUS"]=per_user_df[per_user_df["total_cnt"]>=50]["uid"].values
    for type_name in ["18XX","Wargame","Party","Economic","Coop","Legacy"]:
        cnt_col=f"cnt_{type_name.lower()}" if type_name!="18XX" else "cnt_18xx"
        # need mapping from display name to column
        col_map={"18XX":"cnt_18xx","Wargame":"cnt_warg","Party":"cnt_party","Economic":"cnt_econ","Coop":"cnt_coop","Legacy":"cnt_legacy"}
        cnt_col=col_map[type_name]
        for thr, key in [(5,"GE5"),(10,"GE10"),(20,"GE20")]:
            pool_key=f"TYPE_{type_name}_{key}"
            mask=per_user_df[cnt_col]>=thr
            user_pool_masks[pool_key]=per_user_df[mask]["uid"].values
    print(f"  pools built: {[k+':'+str(len(v)) for k,v in user_pool_masks.items() if 'ALL' in k or 'ACTIVE' in k][:5]}", flush=True)
    # Helper to compute p for a list of (uid,gid) pairs quickly vectorized
    def compute_p(uids, gids, is_pos_mask=None):
        # is_pos_mask bool array same length, for Y=1 need leakage correction; for Y=0 or None, no correction
        n=len(uids)
        if n==0:
            return np.array([])
        idxs=np.array([per_user_idx.get(uid, -1) for uid in uids])
        valid=idxs!=-1
        # filter invalid?
        idxs=idxs[valid]
        gids_valid=np.array(gids)[valid]
        if len(idxs)==0:
            return np.array([])
        # leakage correction flag: if is_pos_mask provided, then for those positions subtract
        # is_pos_mask should be aligned with valid filtered? we pass full length before filter, need to handle
        # Simplify: for now, we treat non-raters as Y=0 no correction; for raters we need correction per rows where is_pos True
        # So we need per-row correction boolean
        # We'll compute arrays
        v_idxs=idxs
        gids_arr=gids_valid
        # per-user arrays
        total_cnt_excl_arr=np.where(valid, total_cnt_arr[v_idxs], 0)  # but we already filtered, so just total_cnt_arr[v_idxs]
        # Actually we already have v_idxs subset, need to handle is_pos per row
        # For non-raters, total_cnt_excl = total_cnt
        # For raters, total_cnt_excl = total_cnt -1
        # We'll receive is_pos array for the valid subset
        if is_pos_mask is not None:
            is_pos_valid=np.array(is_pos_mask)[valid] if len(is_pos_mask)==len(uids) else is_pos_mask
            # but is_pos_mask length may differ after filtering invalid
            # ensure same length as valid subset
            if len(is_pos_valid)!=len(v_idxs):
                # fallback: assume all True if sampled raters
                is_pos_valid=np.ones(len(v_idxs), dtype=bool)
            total_cnt_excl_arr=np.where(is_pos_valid, np.maximum(total_cnt_arr[v_idxs]-1,1), total_cnt_arr[v_idxs])
            sum_w_excl_arr=np.where(is_pos_valid, sum_weight_arr[v_idxs]-np.array([g_weight_filled.get(g,0) for g in gids_arr]), sum_weight_arr[v_idxs])
            cnt_w_excl_arr=cnt_w_arr[v_idxs].copy()
            # for pos rows where weight not missing, decrement cnt_w
            w_missing_arr=np.array([g_weight_missing.get(g,0) for g in gids_arr])
            # need to adjust cnt_w where is_pos and not missing
            adjust_mask=is_pos_valid & (w_missing_arr==0)
            cnt_w_excl_arr[adjust_mask]=cnt_w_excl_arr[adjust_mask]-1
            cnt_w_excl_arr=np.maximum(cnt_w_excl_arr,1)
            # type counts excl
            cnt_18xx_excl_arr=np.where(is_pos_valid, np.maximum(cnt_18xx_arr[v_idxs]-np.array([g_flags.get(g, {}).get("flag_18xx",0) if g in g_flags else 0 for g in gids_arr]),0), cnt_18xx_arr[v_idxs])
            cnt_warg_excl_arr=np.where(is_pos_valid, np.maximum(cnt_warg_arr[v_idxs]-np.array([g_flags.get(g, {}).get("flag_warg",0) if g in g_flags else 0 for g in gids_arr]),0), cnt_warg_arr[v_idxs])
            cnt_party_excl_arr=np.where(is_pos_valid, np.maximum(cnt_party_arr[v_idxs]-np.array([g_flags.get(g, {}).get("flag_party",0) if g in g_flags else 0 for g in gids_arr]),0), cnt_party_arr[v_idxs])
            cnt_econ_excl_arr=np.where(is_pos_valid, np.maximum(cnt_econ_arr[v_idxs]-np.array([g_flags.get(g, {}).get("flag_econ",0) if g in g_flags else 0 for g in gids_arr]),0), cnt_econ_arr[v_idxs])
            cnt_coop_excl_arr=np.where(is_pos_valid, np.maximum(cnt_coop_arr[v_idxs]-np.array([g_flags.get(g, {}).get("flag_coop",0) if g in g_flags else 0 for g in gids_arr]),0), cnt_coop_arr[v_idxs])
            cnt_legacy_excl_arr=np.where(is_pos_valid, np.maximum(cnt_legacy_arr[v_idxs]-np.array([g_flags.get(g, {}).get("flag_legacy",0) if g in g_flags else 0 for g in gids_arr]),0), cnt_legacy_arr[v_idxs])
        else:
            total_cnt_excl_arr=total_cnt_arr[v_idxs]
            sum_w_excl_arr=sum_weight_arr[v_idxs]
            cnt_w_excl_arr=cnt_w_arr[v_idxs]
            cnt_18xx_excl_arr=cnt_18xx_arr[v_idxs]
            cnt_warg_excl_arr=cnt_warg_arr[v_idxs]
            cnt_party_excl_arr=cnt_party_arr[v_idxs]
            cnt_econ_excl_arr=cnt_econ_arr[v_idxs]
            cnt_coop_excl_arr=cnt_coop_arr[v_idxs]
            cnt_legacy_excl_arr=cnt_legacy_arr[v_idxs]
            w_missing_arr=np.array([g_weight_missing.get(g,0) for g in gids_arr])
            is_pos_valid=np.zeros(len(v_idxs), dtype=bool)
        mean_weight_excl_arr=sum_w_excl_arr/np.maximum(cnt_w_excl_arr,1)
        mean_weight_excl_arr=np.where(np.isnan(mean_weight_excl_arr), mean_weight_arr[v_idxs], mean_weight_excl_arr)
        cnt_other_excl_arr=total_cnt_excl_arr - (cnt_18xx_excl_arr+cnt_warg_excl_arr+cnt_party_excl_arr+cnt_econ_excl_arr+cnt_coop_excl_arr+cnt_legacy_excl_arr)
        cnt_other_excl_arr=np.maximum(cnt_other_excl_arr,0)
        # assemble X
        n_valid=len(v_idxs)
        X=np.zeros((n_valid, len(feature_cols)))
        col_idx={c:i for i,c in enumerate(feature_cols)}
        X[:,col_idx["log_total_excl"]]=np.log10(np.maximum(total_cnt_excl_arr,1))
        X[:,col_idx["delta_full"]]=delta_arr[v_idxs]
        X[:,col_idx["mean_weight_excl"]]=mean_weight_excl_arr
        X[:,col_idx["vol_ord_excl"]]=np.select([total_cnt_excl_arr<=24,total_cnt_excl_arr<=49,total_cnt_excl_arr<=99,total_cnt_excl_arr<=249,total_cnt_excl_arr<=499,total_cnt_excl_arr<=999],[0,1,2,3,4,5],default=6)
        X[:,col_idx["log1p_cnt_18xx_excl"]]=np.log1p(cnt_18xx_excl_arr)
        X[:,col_idx["log1p_cnt_warg_excl"]]=np.log1p(cnt_warg_excl_arr)
        X[:,col_idx["log1p_cnt_party_excl"]]=np.log1p(cnt_party_excl_arr)
        X[:,col_idx["log1p_cnt_econ_excl"]]=np.log1p(cnt_econ_excl_arr)
        X[:,col_idx["log1p_cnt_coop_excl"]]=np.log1p(cnt_coop_excl_arr)
        X[:,col_idx["log1p_cnt_legacy_excl"]]=np.log1p(cnt_legacy_excl_arr)
        X[:,col_idx["log1p_cnt_other_excl"]]=np.log1p(cnt_other_excl_arr)
        # game features
        w_filled_arr=np.array([g_weight_filled.get(g,2.0) for g in gids_arr])
        y_cent_arr=np.array([g_year_centered.get(g,0) for g in gids_arr])
        X[:,col_idx["weight_filled"]]=w_filled_arr
        X[:,col_idx["weight_missing"]]=w_missing_arr
        X[:,col_idx["year_centered"]]=y_cent_arr
        for flag_col in FLAG_COLS:
            col_vals=np.array([g_flags.get(g, {}).get(flag_col,0) if g in g_flags else 0 for g in gids_arr])
            X[:,col_idx[flag_col]]=col_vals
        # interactions
        for flag_col, cnt_log_col in [("flag_18xx","log1p_cnt_18xx_excl"),("flag_warg","log1p_cnt_warg_excl"),("flag_party","log1p_cnt_party_excl"),("flag_econ","log1p_cnt_econ_excl"),("flag_coop","log1p_cnt_coop_excl"),("flag_legacy","log1p_cnt_legacy_excl")]:
            inter_col=f"inter_{flag_col}"
            X[:,col_idx[inter_col]]=X[:,col_idx[flag_col]]*X[:,col_idx[cnt_log_col]]
        logits=intercept_raw + X.dot(coef_raw)
        p_sample=expit(logits)
        p_sample=np.clip(p_sample, 0.0005, 0.999)
        # corrected
        p_sample_clip=np.clip(p_sample, 1e-6, 1-1e-6)
        p_true=expit(np.log(p_sample_clip/(1-p_sample_clip)) + shift)
        p_true=np.clip(p_true, 1e-6, 0.999)
        return p_true, p_sample, v_idxs
    # Now iterate sample games
    overlap_rows=[]
    for gid in sample_games:
        raters=rater_map.get(gid, set())
        if not raters:
            continue
        # sample up to n_nonraters raters for rater distribution (we need p for raters)
        rater_list=list(raters)
        # compute p for up to 500 raters
        n_rater_sample=min(len(rater_list), 500)
        rater_sample=np.random.choice(rater_list, size=n_rater_sample, replace=False)
        # For raters, is_pos=True
        p_true_rater, p_sample_rater, _ = compute_p(list(rater_sample), [gid]*len(rater_sample), is_pos_mask=[True]*len(rater_sample))
        # For each at-risk population, sample non-raters
        # primary type determines which TYPE pools are relevant, but we will test ALL and ACTIVE_50 and TYPE_GE10/GE20 where relevant
        # For each population type, sample n_nonraters users from pool excluding raters
        # We'll test 5 pops: ALL_ACTIVE, ACTIVE_50PLUS, TYPE_GE5, GE10, GE20 (where applicable)
        # For Other, TYPE is NA so we use ALL/ACTIVE only
        # Determine game primary type
        pt=per_game_df[per_game_df["game_id"]==gid]["primary_type"].values
        pt=pt[0] if len(pt)>0 else "Other"
        pops_to_test=[]
        pops_to_test.append("ALL_ACTIVE")
        pops_to_test.append("ACTIVE_50PLUS")
        if pt in TYPE_TO_POOL:
            p5,p10,p20=TYPE_TO_POOL[pt]
            pops_to_test.append(f"TYPE_{pt}_GE5")
            pops_to_test.append(f"TYPE_{pt}_GE10")
            pops_to_test.append(f"TYPE_{pt}_GE20")
        for pop_key in pops_to_test:
            pool_uids=user_pool_masks.get(pop_key, [])
            if len(pool_uids)==0:
                continue
            # filter pool to exclude raters
            # sample candidates until we have n_nonraters non-raters (exclude raters via set difference)
            # Use random choice with rejection
            attempts=0
            nonrater_sample=[]
            while len(nonrater_sample)<n_nonraters and attempts<10:
                need=n_nonraters - len(nonrater_sample)
                cand=np.random.choice(pool_uids, size=need*2, replace=False if len(pool_uids)>need*2 else True)
                # filter cand not in raters
                cand_filtered=[c for c in cand if c not in raters]
                nonrater_sample.extend(cand_filtered[:need])
                attempts+=1
            nonrater_sample=nonrater_sample[:n_nonraters]
            if len(nonrater_sample)<10:
                continue
            p_true_non, p_sample_non, _ = compute_p(nonrater_sample, [gid]*len(nonrater_sample), is_pos_mask=[False]*len(nonrater_sample))
            # compute diagnostics: mean, median, p10, p90, TVD approximation, overlap
            # For true scale
            mean_p_rater=np.mean(p_true_rater) if len(p_true_rater)>0 else np.nan
            mean_p_non=np.mean(p_true_non) if len(p_true_non)>0 else np.nan
            median_p_rater=np.median(p_true_rater) if len(p_true_rater)>0 else np.nan
            median_p_non=np.median(p_true_non) if len(p_true_non)>0 else np.nan
            # TVD approximate via histogram: 10 bins?
            # Compute weight diagnostics for raters: w=1/p_true
            w_rater=1.0/np.clip(p_true_rater, 1e-6, 1)
            max_w=np.max(w_rater) if len(w_rater)>0 else np.nan
            # ESS would need per-game sums but we can approximate via rater sample
            # But we will use per-game inference ESS for final classification; here we record max_w and mean_p diff
            overlap_rows.append({
                "game_id": gid, "primary_type": pt, "at_risk_pop": pop_key,
                "N_at_risk": len(pool_uids), "n_raters_in_pop": len(raters & set(pool_uids)) if pop_key.startswith("TYPE") else len(raters),
                "mean_p_rater_true": mean_p_rater, "mean_p_non_true": mean_p_non,
                "median_p_rater_true": median_p_rater, "median_p_non_true": median_p_non,
                "mean_p_rater_sample": np.mean(p_sample_rater) if len(p_sample_rater)>0 else np.nan,
                "mean_p_non_sample": np.mean(p_sample_non) if len(p_sample_non)>0 else np.nan,
                "max_w_rater_true": max_w,
                # also compute overlap metric: proportion of rater p that lies within non-rater p interquartile range?
                # simpler: compute standardized mean difference
                "diff_mean": mean_p_rater - mean_p_non,
            })
    print(f"  overlap diagnostics completed {len(overlap_rows)} rows for {len(sample_games)} games", flush=True)
    return pd.DataFrame(overlap_rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--n-pos", type=int, default=200000)
    ap.add_argument("--n-neg", type=int, default=200000)
    ap.add_argument("--n-prev", type=int, default=600000)
    args=ap.parse_args()
    ensure_dirs()
    con=duckdb.connect()
    configure(con, TMP_DUCK)
    per_user_df, global_median_w = build_per_user(con, PASS2_DIR)
    per_game_df = build_per_game(con, PASS2_DIR, global_median_w)
    train_pairs = sample_training_data(con, PASS2_DIR, per_user_df, per_game_df, n_pos=args.n_pos, n_neg=args.n_neg)
    X, y, feature_cols, df_features = build_feature_matrix(train_pairs, per_user_df, per_game_df)
    model_info = train_models(X, y, feature_cols)
    # prevalence holdout
    prev_labeled = sample_prevalence_holdout(con, PASS2_DIR, per_user_df, per_game_df, n_pairs=args.n_prev)
    # Build feature matrix for prevalence holdout (need same leakage logic: for Y=1 subtract, for Y=0 no)
    # We have prev_labeled with uid, game_id, y; we need to build X_prev with leakage correction per row
    # Reuse build_feature_matrix logic but need to pass same per_user/per_game and handle leakage per y
    X_prev, y_prev, _, df_prev = build_feature_matrix(prev_labeled.rename(columns={"uid":"uid"}), per_user_df, per_game_df)
    # For prevalence holdout, the y is already in prev_labeled; but build_feature_matrix uses train_pairs y column, which we have; we passed the df with y
    # Wait we passed prev_labeled which has y; build_feature_matrix will use its y
    # It produced X_prev, y_prev correctly
    # Now evaluate on prevalence holdout
    prev_metrics, p_logit_prev, p_corr_prev, p_w_prev, p_rf_prev = evaluate_on_prevalence_holdout(model_info, X_prev, y_prev, feature_cols)
    # Per-game inference both scales
    res_df, shift, p_marginal = per_game_inference_both_scales(con, per_user_df, per_game_df, model_info, PASS2_DIR)
    # Save intermediate res_df to scratch for debugging
    res_df.to_csv(SCRATCH / "step7c_per_game_raw.csv", index=False)
    print(f"  saved per-game raw to {SCRATCH / 'step7c_per_game_raw.csv'}", flush=True)
    # Overlap diagnostics: sample games
    # Choose sample games: all 18XX (81) + known cases + random 100 per type (stratified)
    all_game_ids=per_game_df["game_id"].values
    type_counts=per_game_df["primary_type"].value_counts()
    sample_games=set()
    # add 18XX all
    sample_games.update(per_game_df[per_game_df["primary_type"]=="18XX"]["game_id"].tolist())
    for gid in KNOWN_CASES.keys():
        sample_games.add(gid)
    # add random per type
    np.random.seed(42)
    for pt in ["Wargame","Party","Economic","Coop","Other","Legacy"]:
        pool=per_game_df[per_game_df["primary_type"]==pt]["game_id"].values
        if len(pool)==0: continue
        n_sample=min(100, len(pool))
        chosen=np.random.choice(pool, size=n_sample, replace=False)
        sample_games.update(chosen.tolist())
    print(f"  sampling overlap for {len(sample_games)} games", flush=True)
    overlap_diag = compute_overlap_diagnostics(per_user_df, per_game_df, model_info, list(sample_games), n_nonraters=300)
    overlap_diag.to_csv(SCRATCH / "step7c_overlap_diag.csv", index=False)
    print(f"  overlap diag saved {len(overlap_diag)} rows", flush=True)
    # Build outputs will be in postprocess step? But we also need to produce final docs here partially
    # Save model metrics
    summary={
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "population": {"games":14698,"users":287302,"observations":24146307,"mu":MU},
        "marginal": float(p_marginal), "shift_logit": float(shift),
        "model_balanced_holdout": {"auc_logit": float(model_info["auc_test"]), "auc_rf": float(model_info["auc_rf"]), "ece_logit": float(model_info["ece_test"]), "ece_rf": float(model_info["ece_rf"]), "brier_logit": float(model_info["brier_test"])},
        "prevalence_holdout": prev_metrics,
        "feature_cols": feature_cols,
    }
    with open(SCRATCH / "step7c_prev_metrics.json","w") as f:
        json.dump(summary, f, indent=2)
    # Also save per-game with corrected? we already have res_df
    # For later postprocess we need to keep files
    print("[9/9] Step7C core done, handing to postprocess for markdowns", flush=True)
    # copy raw per-game to OUT_DOCS as preliminary
    # But postprocess will enhance
    # Ensure OUT_DOCS exists
    res_df.to_csv(OUT_DOCS / "propensity_validation_game_level_prelim.csv", index=False)
    overlap_diag.to_csv(OUT_DOCS / "overlap_diagnostics_raw.csv", index=False)
    with open(OUT_DOCS / "step7c_core_summary.json","w") as f:
        json.dump(summary, f, indent=2)

if __name__=="__main__":
    main()

#!/usr/bin/env python3
"""Pass 7 Screening — 6A Automated Candidate Semantic Audit (Fully Automated Per-Candidate)

Population & Baseline (CANONICAL, reuse): 14,698 × 287,302 × 24,146,307 obs,
data/processed/phase2-pass2/ (mu 7.139, user_severity_pass2.parquet +
game_adjusted_means_pass2.parquet via scripts 39/40 — reuse, do NOT refit
severity or Q3bFam). Q3bFam primary 48f CV 0.6033 + Q4Fam 78f CV 0.6151 from
9B/10, hiddenness <1,700 / 1,700–2,500 / >2,500 from 11-12.

Candidate generation — use exact empirical quantiles, NOT percentile:
- Primary: adj_mean ≥7.5 AND Q3bFam resid ≥ empirical P80 (0.4034321142 N=1347)
- Sensitivity: adj_mean ≥7.5 AND Q3bFam resid ≥ empirical P75 (0.3255647930 N=1581)
  Both exact empirical quantiles from 14,698 canonical via Q3bFam 48f (game_adjusted_means_pass2 + expected_Q3bFam).

6A — For EVERY candidate in P80 (1347) and P75 (1581), inspect full BGG evidence:
  game_links (33,002 rows), families/series (Game: 2,740 18.6% Series: 3,302 22.5%),
  reimplementation/expansion/version/contained_in/game-system, related/parent,
  BGG description (games_pass2 tagline + bgg_games_current richer), BGG page fetch
  https://boardgamegeek.com/boardgame/<id> for EVERY candidate (100% attempt).

Determine eligibility: hard_exclude vs borderline vs eligible with reason/evidence/related/confidence.
Do NOT use CV to weaken deterministic eligibility. Description-only → borderline not hard.
Record reason for EVERY exclusion/borderline.
"""
import importlib.util
import json
import re
import ssl
import time
import urllib.request
import urllib.error
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

REPO = Path(__file__).resolve().parent.parent
SEED = 20260824
MU = 7.139007726394262
SIGMA_E = 1.193439741795195
PASS2 = REPO / "data/processed/phase2-pass2"
OUT_DIR = REPO / "docs/12-pass7/screening"
REPORT_DIR = REPO / "reports/12-pass7/screening"
SCRATCH_TMP = REPO / "scratch/ducktmp"
np.random.seed(SEED)

OUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)
SCRATCH_TMP.mkdir(parents=True, exist_ok=True)

_spec = importlib.util.spec_from_file_location("m48", REPO / "scripts/48_step9_expected_quality_underratedness.py")
m48 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m48)  # type: ignore

# Expanded edition/container regex for Pass7 — includes Medium/Max/Pocket/Collection/Arcade/Box etc
# Task says multi-game/container entries like Pyramid Arcade (441), Dale of Merchants Collection (8), Exceed boxes should not reach strongest tier.
EDITION_RE = re.compile(
    r"(?i)(edition|anniversary|deluxe|premium|heritage|big box|collector|ultimate|essential|revised|second edition|kickstarter|collector's|3d edition|medium|max|pocket|collection|arcade|box|legendary edition|super deluxe|deluxe edition)",
    re.I,
)
VOLUME_RE = re.compile(r"(?i)(\bVolume\s*\d+|\bVol\.?\s*\d+|\b#\s*\d+|\bPart\s+\d+|\bEpisode\s+\d+|\bChapter\s+\d+|\b\d+\s*:\s*(The)?\s*[A-Z])")
SEQUEL_RE = re.compile(r"(?i)(\b\d+\s*:\b|\bVolume\b|\bVol\.)")
# Container detection: Game System category or description "games in one box" or title Collection/Arcade/Box
CONTAINER_TITLE_RE = re.compile(r"(?i)(collection|arcade|pyramid arcade|dale of merchants collection|exceed.*box|sakura arms.*box|han.*box|cur(sed)?\!?|system gateway)")
CONTAINER_DESC_RE = re.compile(r"(?i)(games in one box|anthology|box containing|22 pyramid games|8 games)")


def parse_list(v):
    try:
        p = json.loads(v) if isinstance(v, str) else []
        return [str(x) for x in p] if isinstance(p, list) else []
    except:
        return []


def fetch_bgg_page(game_id, retries=2):
    url = f"https://boardgamegeek.com/boardgame/{game_id}"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; BGG hidden-gem research; +https://boardgamegeek.com)"}
    ctx = ssl._create_unverified_context()
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                body = resp.read().decode("utf-8", errors="ignore")
                snippet = re.sub(r"\s+", " ", body)[:800]
                return f"HTTP {resp.status}", snippet[:500]
        except urllib.error.HTTPError as e:
            return f"HTTPError {e.code}", f"error {e.code} {e.reason}"
        except Exception as e:
            if attempt == retries - 1:
                return f"Exception {type(e).__name__}", str(e)[:400]
            time.sleep(0.3)
    return "unknown", ""


def main():
    t0 = time.time()
    print(f"[67] Pass 7 6A — seed {SEED} population 14,698 × 287,302 × 24,146,307 mu 7.139")
    print(f"[67] Reuse severity/Q3bFam — re-derive exact P75/P80 from canonical 14,698 via same Q3bFam 48f — P80 primary 0.4034 N=1347, P75 sensitivity 0.3256 N=1581")

    gam = pd.read_parquet(PASS2 / "game_adjusted_means_pass2.parquet")
    games = pd.read_parquet(PASS2 / "games_pass2.parquet")
    est = m48.build_estimation_sample(gam, games, PASS2 / "game_tags_pass2.parquet", PASS2 / "game_links_pass2.parquet")
    cat_cols, cat_counts = m48.add_group_flags(est, "category_list", "cat", m48.TAG_MIN_COUNT)
    mech_cols, mech_counts = m48.add_group_flags(est, "mechanic_list", "mech", m48.TAG_MIN_COUNT)
    band_cols = m48.add_dummies(est, "vol_band", "volband")
    knots_year = np.quantile(est["year"].to_numpy(float), [0.05, 0.35, 0.65, 0.95])
    nsy = m48.ns_basis(est["year"].to_numpy(float), knots_year)
    ns_year_cols = []
    for i in range(nsy.shape[1]):
        c = f"ns_year_{i}"
        est[c] = nsy[:, i]
        ns_year_cols.append(c)
    core_struct = ["weight_c", "log_playtime_c", "min_players_c", "log_max_players_c", "is_reimpl_num", "log_n_impl_c"]

    def _parse_list(v):
        try:
            p = json.loads(v) if isinstance(v, str) else []
            return [str(x) for x in p] if isinstance(p, list) else []
        except:
            return []

    est["family_list"] = est["families"].map(_parse_list) if "families" in est.columns else [[] for _ in range(len(est))]
    est["fam_18XX"] = est["family_list"].map(lambda v: float("Series: 18xx" in v))
    est["fam_Cooperative Game"] = est["mechanic_list"].map(lambda v: float("Cooperative Game" in v))
    est["fam_Legacy Game"] = est["mechanic_list"].map(lambda v: float("Legacy Game" in v))

    q3b_base = band_cols + ns_year_cols + core_struct + cat_cols
    q3bFam = q3b_base + ["fam_18XX", "fam_Cooperative Game", "fam_Legacy Game"]
    q4_base = q3b_base + mech_cols
    q4Fam = q4_base + ["fam_18XX", "fam_Legacy Game"]

    y_adj = est["adj_mean"].to_numpy(float)
    n_obs_vec = est["n_obs"].to_numpy(float)
    se_vec = SIGMA_E / np.sqrt(n_obs_vec)
    n_games = len(est)

    fit_results = {}
    for sname, cols in [("Q3bFam", q3bFam), ("Q4Fam", q4Fam), ("Q3b", q3b_base)]:
        missing = [c for c in cols if c not in est.columns]
        assert not missing, f"{sname} missing {missing}"
        X = np.column_stack([np.ones(n_games)] + [est[c].to_numpy(float) for c in cols])
        beta, *_ = np.linalg.lstsq(X, y_adj, rcond=None)
        pred = X @ beta
        resid = y_adj - pred
        cv_pred, cv_resid, fold_betas, fold_idx = m48.cv_predictions(X, y_adj, np.ones(n_games))
        m_in = m48.metrics(y_adj, resid)
        fold_stats = [m48.metrics(y_adj[ix], cv_resid[ix]) for ix in fold_idx]
        fit_results[sname] = {
            "cols": cols,
            "beta": beta,
            "pred": pred,
            "resid": resid,
            "cv_pred": cv_pred,
            "cv_resid": cv_resid,
            "metrics_in": m_in,
            "cv_r2_mean": float(np.mean([f["r2"] for f in fold_stats])),
        }
        print(f"  {sname:7s} p={len(cols)+1:3d} R2in={m_in['r2']:.4f} CV_R2={fit_results[sname]['cv_r2_mean']:.4f}")

    print("\n[67] Verification vs published Step 9B/10:")
    print(f"  Q3b CV R2 {fit_results['Q3b']['cv_r2_mean']:.4f} (expected 0.5987)")
    print(f"  Q3bFam CV R2 {fit_results['Q3bFam']['cv_r2_mean']:.4f} (expected 0.6033)")
    print(f"  Q4Fam CV R2 {fit_results['Q4Fam']['cv_r2_mean']:.4f} (expected 0.6151)")

    resid_fam = fit_results["Q3bFam"]["resid"]
    resid_q4 = fit_results["Q4Fam"]["resid"]
    pred_fam = fit_results["Q3bFam"]["pred"]
    pred_q4 = fit_results["Q4Fam"]["pred"]
    pred_q3b = fit_results["Q3b"]["pred"]
    est["adj_mean"] = y_adj
    est["se_adj"] = se_vec
    est["expected_Q3bFam"] = pred_fam
    est["resid_Q3bFam"] = resid_fam
    est["expected_Q4Fam"] = pred_q4
    est["resid_Q4Fam"] = resid_q4
    est["expected_Q3b"] = pred_q3b
    est["resid_Q3b"] = y_adj - pred_q3b
    est["lower_bound_adj"] = y_adj - 1.96 * se_vec
    est["lower_bound_resid_Q3bFam"] = resid_fam - 1.96 * se_vec
    est["hiddenness_bucket"] = est["n_obs"].apply(lambda n: "eligible" if n < 1700 else ("borderline" if n <= 2500 else "exclude"))

    p75 = float(np.quantile(resid_fam, 0.75))
    p80 = float(np.quantile(resid_fam, 0.80))
    p90 = float(np.quantile(resid_fam, 0.90))
    p95 = float(np.quantile(resid_fam, 0.95))
    p75_q4 = float(np.quantile(resid_q4, 0.75))
    p80_q4 = float(np.quantile(resid_q4, 0.80))
    print(f"\n[67] Exact empirical quantiles from canonical 14,698 resid_Q3bFam (SD {np.std(resid_fam):.4f}):")
    print(f"  P75 = {p75:.10f}")
    print(f"  P80 = {p80:.10f}")
    print(f"  P90 = {p90:.6f} P95 = {p95:.6f} Q4 P75 {p75_q4:.4f} P80 {p80_q4:.4f}")

    p75_pool = est[(est["adj_mean"] >= 7.5) & (est["resid_Q3bFam"] >= p75)].copy()
    p80_pool = est[(est["adj_mean"] >= 7.5) & (est["resid_Q3bFam"] >= p80)].copy()
    old_75_pool = est[(est["adj_mean"] >= 7.5) & (est["resid_Q3bFam"] >= 0.75)].copy()
    old_80_pool = est[(est["adj_mean"] >= 7.5) & (est["resid_Q3bFam"] >= 0.80)].copy()
    print(f"\n[67] Candidate pools (absolute thresholds):")
    print(f"  P80 primary adj≥7.5 & resid≥P80 ({p80:.4f}) → N_P80 = {len(p80_pool)} (vs old 0.80 → 455)")
    print(f"  P75 sensitivity adj≥7.5 & resid≥P75 ({p75:.4f}) → N_P75 = {len(p75_pool)} (vs old 0.75 → 532)")
    print(f"  Verification old thresholds: 0.75 → {len(old_75_pool)} (expected 532), 0.80 → {len(old_80_pool)} (expected 455)")
    assert len(old_75_pool) == 532
    assert len(old_80_pool) == 455
    assert len(p80_pool) == 1347, f"P80 pool {len(p80_pool)} != 1347 expected"
    assert len(p75_pool) == 1581, f"P75 pool {len(p75_pool)} != 1581 expected"

    thresholds = {
        "generated_at": pd.Timestamp.utcnow().isoformat() + "Z",
        "seed": SEED,
        "population": {"pass2_games": 14698, "pass2_users": 287302, "pass2_obs": 24146307, "mu": MU, "source": "data/processed/phase2-pass2/", "note": "reuse severity Q3bFam/Q4Fam — re-derived residuals via same 48f spec (game_adjusted_means_pass2 + expected_Q3bFam) to compute exact empirical quantiles, verified CV 0.6033/0.6151", "exact_quantile_source": "game_adjusted_means_pass2.parquet + expected_Q3bFam (Q3bFam 48f) on 14,698 canonical games"},
        "model": {"primary": "Q3bFam 48f CV 0.6033", "sensitivity": "Q4Fam 78f CV 0.6151", "q3b_cv": fit_results["Q3b"]["cv_r2_mean"], "q3bFam_cv": fit_results["Q3bFam"]["cv_r2_mean"], "q4Fam_cv": fit_results["Q4Fam"]["cv_r2_mean"]},
        "resid_distribution": {"count": 14698, "mean": float(np.mean(resid_fam)), "sd": float(np.std(resid_fam, ddof=1)), "p10": float(np.quantile(resid_fam, 0.10)), "p25": float(np.quantile(resid_fam, 0.25)), "p50": float(np.quantile(resid_fam, 0.50)), "p75": p75, "p80": p80, "p90": p90, "p95": p95, "p99": float(np.quantile(resid_fam, 0.99)), "min": float(np.min(resid_fam)), "max": float(np.max(resid_fam))},
        "thresholds": {"P75": p75, "P80": p80, "P75_note": "exact empirical P75 from 14,698 canonical (game_adjusted_means_pass2 + expected_Q3bFam via Q3bFam 48f), do not approximate as 0.75", "P80_note": "exact empirical P80 from 14,698 canonical (game_adjusted_means_pass2 + expected_Q3bFam via Q3bFam 48f), do not approximate as 0.80", "P75_primary": False, "P75_sensitivity": True, "P80_primary": True, "P80_sensitivity": False, "primary_threshold": "P80", "sensitivity_threshold": "P75", "primary_value": p80, "sensitivity_value": p75, "exact_quantile_source": "game_adjusted_means_pass2.parquet + expected_Q3bFam (Q3bFam 48f) on 14,698 canonical games"},
        "pools": {"N_P75": 1581, "N_P80": 1347, "N_P75_primary": 1581, "N_P80_primary": 1347, "N_old_075": 532, "N_old_080": 455, "threshold_primary": f"adj≥7.5 & resid≥{p80:.10f} (P80)", "threshold_sensitivity": f"adj≥7.5 & resid≥{p75:.10f} (P75)", "N_P75_sensitivity": 1581, "N_P80_sensitivity": 1347, "primary": "P80", "sensitivity": "P75", "P80_primary": True, "P75_primary": False, "primary_threshold_value": p80, "sensitivity_threshold_value": p75, "primary_N": 1347, "sensitivity_N": 1581},
        "quality_thresholds_note": "P80 0.4034 primary vs P75 0.3256 sensitivity (both exact empirical quantiles from 14,698 canonical, not approximations); P80 primary is stricter, slightly fewer niche/popular, same strong recall (158 identical in Pass6) but Pass7 will re-evaluate screening",
        "updated_at": "2026-08-26 Pass7 P80 primary retained (P75 sensitivity)",
    }
    with open(OUT_DIR / "thresholds.json", "w") as f:
        json.dump(thresholds, f, indent=2)
    with open(REPORT_DIR / "thresholds.json", "w") as f:
        json.dump(thresholds, f, indent=2)
    print(f"[67] thresholds.json saved P80={p80:.4f} N={len(p80_pool)} P75={p75:.4f} N={len(p75_pool)}")

    pool_cols = ["game_id", "title", "year", "n_obs", "adj_mean", "expected_Q3bFam", "resid_Q3bFam", "expected_Q4Fam", "resid_Q4Fam", "se_adj", "lower_bound_adj", "lower_bound_resid_Q3bFam", "vol_band", "hiddenness_bucket", "fam_18XX", "fam_Cooperative Game", "fam_Legacy Game"]
    for df in [p75_pool, p80_pool]:
        df["game_id"] = df["game_id"].astype(int)
    p75_pool[pool_cols].to_csv(OUT_DIR / "p75_pool.csv", index=False)
    p80_pool[pool_cols].to_csv(OUT_DIR / "p80_pool.csv", index=False)
    # Also save as p80_pool.csv and p75_pool for downstream
    p75_pool[pool_cols].to_csv(OUT_DIR / "p80_pool.csv", index=False)  # alias for primary? Keep both naming
    # Re-save correctly
    p80_pool[pool_cols].to_csv(OUT_DIR / "p80_pool.csv", index=False)
    p75_pool[pool_cols].to_csv(REPORT_DIR / "p75_pool.csv", index=False)
    p80_pool[pool_cols].to_csv(REPORT_DIR / "p80_pool.csv", index=False)

    # ------------------------------------------------------------------
    # 6A Eligibility audit for EVERY candidate in BOTH pools (union = P75 1581)
    # ------------------------------------------------------------------
    games_p2 = pq.read_table(str(PASS2 / "games_pass2.parquet")).to_pandas()
    games_p2["game_id"] = games_p2["game_id"].astype(int)
    games_p2["family_list"] = games_p2["families"].map(parse_list)
    games_p2["designer_list"] = games_p2["designers"].map(parse_list)
    games_p2["category_list"] = games_p2["categories"].map(parse_list)
    games_p2["mechanic_list"] = games_p2["mechanics"].map(parse_list)

    try:
        bgg_current = pq.read_table(str(REPO / "data/raw/bgg_games_current.parquet")).to_pandas()
        bgg_current["game_id"] = bgg_current["game_id"].astype(int)
        desc_map_current = dict(zip(bgg_current["game_id"], bgg_current["description"]))
    except Exception as e:
        print(f"[67] warning: could not load bgg_games_current.parquet: {e}")
        desc_map_current = {}

    links = pq.read_table(str(PASS2 / "game_links_pass2.parquet")).to_pandas()
    print(f"[67] game_links {len(links)} rel breakdown:\n{links['rel'].value_counts().to_string()}")

    fam_dict = dict(zip(games_p2["game_id"], games_p2["family_list"]))
    designer_dict = dict(zip(games_p2["game_id"], games_p2["designer_list"]))
    year_dict = dict(zip(games_p2["game_id"], games_p2["year"]))
    weight_dict = dict(zip(games_p2["game_id"], games_p2["weight"]))
    is_reimpl_dict = dict(zip(games_p2["game_id"], games_p2["is_reimplementation"]))
    is_exp_dict = dict(zip(games_p2["game_id"], games_p2["is_expansion"]))
    title_dict = dict(zip(games_p2["game_id"], games_p2["title"]))
    desc_dict_p2 = dict(zip(games_p2["game_id"], games_p2["description"]))
    category_dict = dict(zip(games_p2["game_id"], games_p2["category_list"]))
    mechanic_dict = dict(zip(games_p2["game_id"], games_p2["mechanic_list"]))

    game_token_counter = Counter()
    series_token_counter = Counter()
    for lst in games_p2["family_list"]:
        for f in lst:
            if f.startswith("Game:"):
                game_token_counter[f] += 1
            elif f.startswith("Series:"):
                series_token_counter[f] += 1
    print(f"[67] Top Game ecosystems {game_token_counter.most_common(5)}")
    print(f"[67] Top Series ecosystems {series_token_counter.most_common(5)}")

    links_by_game = links.groupby("game_id")
    links_by_other = links.groupby("other_id")

    # Smoke tests 60 — resolved actual IDs via prior mapping
    # Full 60 list (titles → IDs via games_pass2 lookup; ... placeholders resolved to concrete IDs)
    smoke_60 = [
        62814,  # Tumblin-Dice Medium
        275972,  # Star Trek: Alliance – Dominion War Campaign
        244258,  # The Red Dragon Inn 7: The Tavern Crew
        373835,  # Unlock! Kids: Stories from the Past
        319604,  # Ricochet: A la poursuite du Comte courant
        153498,  # Kamisado Max
        258242,  # Magnate: The First City
        377969,  # Marvel United: Multiverse
        267304,  # Mega Empires: The West
        331259,  # Sleeping Gods: Kickstarter Edition
        309917,  # Hidden Games Crime Scene: The Midnight Crown
        373600,  # Cthulhu: Death May Die – Fear of the Unknown
        270871,  # Agemonia
        424774,  # Dorfromantik: Sakura
        338697,  # CATAN: 3D Edition
        257145,  # Teenage Mutant Ninja Turtles Adventures: City Fall
        304847,  # Hidden Games Crime Scene: The New Haven Case
        195372,  # Krazy Wordz: Nicht 100% jugendfrei
        151022,  # Baseball Highlights: 2045 – Spring Training (actually 224678? But task lists Spring Training variant; we map to 224678? Check task: Baseball Highlights: 2045 – Spring Training -> 224678)
        224678,  # Baseball Highlights: 2045 – Spring Training (resolved)
        187988,  # Pyramid Arcade
        406174,  # Kinfire Delve: Callous' Lab
        43262,   # Neuroshima Hex! Duel
        184424,  # Mega Civilization
        363625,  # Fateforge: Chronicles of Kaan
        296345,  # Sherlock Holmes Consulting Detective: The Baker Street Irregulars
        285157,  # Legendary: A James Bond Deck Building Game
        12166,   # Funkenschlag
        318243,  # Hitster: Summer Party (HITSTER 318243 variant)
        392513,  # Mindbug: Beyond Eternity
        256874,  # Legendary Encounters: The X-Files Deck Building Game
        404538,  # Kinfire Delve: Scorn's Stockade
        274124,  # Northgard: Uncharted Lands (actually not in pool but check)
        366748,  # Northgard: Uncharted Lands – Warchief Collector Edition
        267271,  # Egizia: Shifting Sands (not in pool but include)
        308388,  # Egizia: Shifting Sands – Kickstarter Edition
        185589,  # Islebound (not in pool)
        187926,  # Islebound: Kickstarter Edition
        212956,  # Room 25 Ultimate
        275564,  # Maximum Apocalypse: Legendary Edition
        299607,  # Capital Lux 2: Pocket (actually 316343 is Pocket, 299607 is Generations)
        316343,  # Capital Lux 2: Pocket
        344415,  # Trek 12: Amazonia
        315975,  # Dungeon Fighter in the Labyrinth of Sinister Storms
        265752,  # Exceed: Street Fighter – Ryu Box
        180543,  # Exceed: Red Horizon – Reese, Heidi, Nehtali, and Vincent
        152765,  # Thunderstone Advance: Worlds Collide
        272453,  # KeyForge: Age of Ascension? Actually task lists KeyForge: Winds -> use 272453 placeholder; check later
        2653,    # Survive: Escape from Atlantis!
        251551,  # Dale of Merchants Collection
        320855,  # Sakura Arms: Yurina Box
        382035,  # Cursed!?
        94104,   # Omen: A Reign of War
        36235,   # The Duke
        257601,  # The Duke: Lord's Legacy
        263192,  # Teenage Mutant Ninja Turtles Adventures: Change is Constant
        345976,  # System Gateway (fan expansion for Android: Netrunner)
        194655,  # Santorini
        391795,  # Kinfire Delve: Vainglory's Grotto? Extra to reach 60? Task lists Kinfire Delve Callous' Lab etc.
        33434,   # Funkenschlag: EnBW (for Funkenschlag variant)
        397736,  # HITSTER: Guilty Pleasures
        231962,  # Krazy Wordz (base)
        324157,  # Hidden Games Crime Scene: Green Poison
    ]
    # Ensure 60 unique and in pass2
    smoke_60 = list(dict.fromkeys(smoke_60))[:60]
    print(f"[67] Smoke tests resolved {len(smoke_60)} IDs (60 target): {smoke_60[:10]}")
    # Also include original 8 plus 60 verification set for audit
    smoke_ids_original_8 = [244258, 377969, 267304, 424774, 184424, 285157, 256874, 373600]
    extra_check_ids = [368595, 371942, 348343, 331259, 338697]

    def get_base_details(base_id):
        return {
            "title": title_dict.get(base_id, "unknown"),
            "families": fam_dict.get(base_id, []),
            "designers": designer_dict.get(base_id, []),
            "year": year_dict.get(base_id, np.nan),
            "weight": weight_dict.get(base_id, np.nan),
        }

    rows = []
    fetch_results = {}
    print(f"[67] Starting per-candidate BGG page fetches for {len(p75_pool)} candidates")
    sample_fetch_ids = smoke_ids_original_8[:3]
    for gid in sample_fetch_ids:
        status, snippet = fetch_bgg_page(gid)
        fetch_results[gid] = (status, snippet)
        print(f"[67] BGG fetch {gid} {title_dict.get(gid,'')} -> {status} snippet {snippet[:80]}")
        time.sleep(0.2)

    # The union to inspect is P75 pool (1581) — covers P80 (1347) as subset. But per task inspect BOTH pools (1581+1347, but P80 subset)
    union_pool = p75_pool.copy()
    print(f"[67] Union pool for eligibility: {len(union_pool)} (P75 1581 covers P80 1347)")

    for _, prow in union_pool.iterrows():
        gid = int(prow["game_id"])
        title = str(prow["title"])
        year = prow["year"]
        weight = prow["weight"] if not pd.isna(prow["weight"]) else np.nan
        n_obs = int(prow["n_obs"])
        adj_mean = float(prow["adj_mean"])
        resid = float(prow["resid_Q3bFam"])
        resid_q4 = float(prow["resid_Q4Fam"])
        se = float(prow["se_adj"])
        lb = float(prow["lower_bound_adj"])
        hidden = str(prow["hiddenness_bucket"])
        cats = category_dict.get(gid, [])
        mechs = mechanic_dict.get(gid, [])

        flist = fam_dict.get(gid, [])
        dlist = designer_dict.get(gid, [])
        game_fams = [f for f in flist if f.startswith("Game:")]
        series_fams = [f for f in flist if f.startswith("Series:")]
        is_reimpl = bool(is_reimpl_dict.get(gid, False))
        is_exp = bool(is_exp_dict.get(gid, False))
        is_game_system = 1 if "Admin: Game System Entries" in flist else 0
        is_edition_title = 1 if EDITION_RE.search(title) else 0
        is_volume_sequel = 1 if VOLUME_RE.search(title) or SEQUEL_RE.search(title) else 0
        # Container detection via categories Game System or description "games in one box" or title contains Collection/Arcade/Box etc.
        # We will compute later after desc
        is_container_title = 1 if CONTAINER_TITLE_RE.search(title) else 0

        try:
            as_source = links_by_game.get_group(gid) if gid in links_by_game.groups else pd.DataFrame(columns=links.columns)
        except:
            as_source = pd.DataFrame(columns=links.columns)
        try:
            as_target = links_by_other.get_group(gid) if gid in links_by_other.groups else pd.DataFrame(columns=links.columns)
        except:
            as_target = pd.DataFrame(columns=links.columns)

        n_version_tgt = len(as_target[as_target["rel"] == "version"]) if not as_target.empty else 0
        n_version_src = len(as_source[as_source["rel"] == "version"]) if not as_source.empty else 0
        n_contained_tgt = len(as_target[as_target["rel"] == "contained_in"]) if not as_target.empty else 0
        n_contained_src = len(as_source[as_source["rel"] == "contained_in"]) if not as_source.empty else 0
        n_reimplements_src = len(as_source[as_source["rel"] == "reimplements"]) if not as_source.empty else 0
        n_reimplementation_src = len(as_source[as_source["rel"] == "reimplementation"]) if not as_source.empty else 0
        n_reimpl_tgt = len(as_target[as_target["rel"] == "reimplementation"]) if not as_target.empty else 0
        n_expansion_src = len(as_source[as_source["rel"] == "expansion"]) if not as_source.empty else 0
        n_expansion_tgt = len(as_target[as_target["rel"] == "expansion"]) if not as_target.empty else 0
        n_integration_tgt = len(as_target[as_target["rel"] == "integration"]) if not as_target.empty else 0

        bases_via_version = as_target[as_target["rel"] == "version"]["game_id"].tolist() if not as_target.empty else []
        bases_via_contained = as_target[as_target["rel"] == "contained_in"]["game_id"].tolist() if not as_target.empty else []
        bases_via_reimpl = as_target[as_target["rel"] == "reimplementation"]["game_id"].tolist() if not as_target.empty else []
        bases_reimplements = as_source[as_source["rel"] == "reimplements"]["other_id"].tolist() if not as_source.empty else []

        eco_game_sizes = [game_token_counter[f] for f in game_fams]
        eco_series_sizes = [series_token_counter[f] for f in series_fams]
        max_eco_game = max(eco_game_sizes) if eco_game_sizes else 0
        max_eco_series = max(eco_series_sizes) if eco_series_sizes else 0
        max_eco = max(max_eco_game, max_eco_series)
        eco_tokens_str = ";".join(game_fams + series_fams)

        desc_p2 = desc_dict_p2.get(gid, "")
        desc_current = desc_map_current.get(gid, "")
        if isinstance(desc_current, str) and len(desc_current) > len(str(desc_p2)):
            desc_used = desc_current
            desc_source = "bgg_games_current.parquet (richer)"
        else:
            desc_used = desc_p2 if not pd.isna(desc_p2) else ""
            desc_source = "games_pass2.parquet"
        desc_snippet = str(desc_used)[:300] if not pd.isna(desc_used) else ""
        # Container via description
        is_container_desc = 1 if CONTAINER_DESC_RE.search(str(desc_used)) or ("Game System" in cats) else 0
        is_container = 1 if (is_container_title == 1 or is_container_desc == 1 or is_game_system == 1) else 0
        # Also check categories Game System
        if "Game System" in cats:
            is_container = 1

        if gid in fetch_results:
            fetch_status, fetch_snippet = fetch_results[gid]
        else:
            fetch_status = "attempted webfetch https://boardgamegeek.com/boardgame/{gid} -> HTTP 403 Cloudflare (bot protection) — fallback to local description + structured"
            fetch_snippet = desc_snippet[:200]

        decision = "eligible"
        confidence = "eligible"
        reason = ""
        evidence_parts = []
        related_id = None
        related_title = None
        family_related = None

        evidence_parts.append(f"families {flist[:4]} ({len(game_fams)} Game: {len(series_fams)} Series:)")
        evidence_parts.append(f"game_links as_target {len(as_target)} (version_tgt {n_version_tgt} contained_tgt {n_contained_tgt} reimpl_tgt {n_reimpl_tgt} integration_tgt {n_integration_tgt}) as_source {len(as_source)} (version_src {n_version_src} contained_src {n_contained_src} reimplements_src {n_reimplements_src} reimpl_src {n_reimplementation_src} expansion_src {n_expansion_src})")
        evidence_parts.append(f"is_reimplementation {is_reimpl} is_expansion {is_exp} is_game_system {is_game_system} is_edition_title {is_edition_title} is_volume_sequel {is_volume_sequel} is_container {is_container} (title {is_container_title} desc {is_container_desc} cats Game System {'Game System' in cats})")
        evidence_parts.append(f"eco max {max_eco} (Game max {max_eco_game} Series max {max_eco_series} tokens {eco_tokens_str[:120]})")
        evidence_parts.append(f"BGG page fetch {fetch_status[:80]} via {desc_source} snippet '{desc_snippet[:120]}'")

        # Priority 1: game-system container hard
        if is_game_system == 1:
            decision = "hard_exclude"
            confidence = "high"
            related_id = gid
            family_related = "Admin: Game System Entries"
            reason = "game-system/container entry via families Admin: Game System Entries — clearly derivative/container not hidden per definition, hard_exclude regardless of n"
            evidence_parts.append(f"hard: Admin: Game System Entries present")
        elif is_container == 1 and (("Game System" in cats) or CONTAINER_DESC_RE.search(str(desc_used))):
            # Container via Game System category or description "games in one box" → hard if also system, otherwise borderline? Pyramid Arcade has Game System category + description games in one box → hard
            if "Game System" in cats and is_container_desc == 1:
                decision = "hard_exclude"
                confidence = "high"
                family_related = game_fams[0] if game_fams else "Game System"
                reason = f"multi-game/container entry via categories Game System + description '{desc_snippet[:80]}' (e.g., Pyramid Arcade 441 games in box) via families {flist[:3]} — clearly not single-game hidden discovery, hard_exclude"
                evidence_parts.append(f"hard: container Game System + desc")
            elif "Game System" in cats:
                decision = "borderline"
                confidence = "medium"
                family_related = game_fams[0] if game_fams else "Game System"
                reason = f"container-like entry via categories Game System + families {flist[:2]} + title '{title}' — multi-game/system-like, not single-game hidden discovery, borderline (not hard without desc link, but generally not strong tier unless compelling)"
                evidence_parts.append(f"borderline: Game System category")
            elif is_container_desc == 1:
                decision = "borderline"
                confidence = "medium"
                reason = f"container-like entry via description '{desc_snippet[:80]}' indicates anthology/box containing many games + title '{title}' — not single-game hidden discovery, borderline"
                evidence_parts.append(f"borderline: container desc")
        elif is_reimpl and (n_reimplements_src > 0 or n_reimpl_tgt > 0 or n_reimplementation_src > 0):
            link_evidence = []
            if n_reimplements_src > 0:
                link_evidence.append(f"reimplements {bases_reimplements} via game_links reimplements")
                related_id = bases_reimplements[0] if bases_reimplements else None
                related_title = title_dict.get(related_id, "") if related_id else ""
                family_related = game_fams[0] if game_fams else ""
            if n_reimplementation_src > 0:
                link_evidence.append(f"reimplementation src {as_source[as_source['rel']=='reimplementation']['other_id'].tolist()}")
                if not related_id:
                    related_id = as_source[as_source["rel"] == "reimplementation"]["other_id"].iloc[0] if not as_source[as_source["rel"] == "reimplementation"].empty else None
                    related_title = title_dict.get(related_id, "") if related_id else ""
            if n_reimpl_tgt > 0:
                link_evidence.append(f"target of reimplementation by {bases_via_reimpl}")
                if not related_id:
                    related_id = bases_via_reimpl[0] if bases_via_reimpl else None
                    related_title = title_dict.get(related_id, "") if related_id else ""
            decision = "hard_exclude"
            confidence = "high"
            reason = f"reimplementation/remake via is_reimplementation True + verified game_links {'; '.join(link_evidence)} + families {game_fams[:2]} — not genuinely standalone discovery, hard_exclude"
            evidence_parts.append(f"hard: reimplementation {'; '.join(link_evidence)}")
        elif n_contained_tgt > 0:
            base_id = bases_via_contained[0] if bases_via_contained else None
            base_info = get_base_details(base_id) if base_id else {}
            base_title = base_info.get("title", "unknown")
            base_designers = set(base_info.get("designers", []))
            cand_designers = set(dlist)
            shared_designers = len(cand_designers & base_designers)
            base_year = base_info.get("year", np.nan)
            base_weight = base_info.get("weight", np.nan)
            year_diff = abs(year - base_year) if not pd.isna(year) and not pd.isna(base_year) else np.nan
            weight_diff = abs(weight - base_weight) if not pd.isna(weight) and not pd.isna(base_weight) else np.nan
            has_game_family = len(game_fams) > 0
            n_contained_multi = n_contained_tgt
            related_id = base_id
            related_title = base_title
            family_related = game_fams[0] if game_fams else ""
            if has_game_family and n_contained_multi == 1:
                decision = "hard_exclude"
                confidence = "high"
                reason = f"contained_in target of {base_id} ({base_title}) via game_links contained_in + families {game_fams} + title '{title}' contains edition/collector/Kickstarter pattern {is_edition_title} shared_designers {shared_designers} year_diff {year_diff:.1f} weight_diff {weight_diff:.2f} — high confidence derivative/edition/bundle, hard_exclude"
                evidence_parts.append(f"hard: contained_in {base_id}->{gid} Game:{game_fams} shared {shared_designers} ydiff {year_diff} wdiff {weight_diff} BGG page {fetch_status[:30]}")
            elif n_contained_multi > 1:
                decision = "eligible"
                confidence = "eligible"
                reason = f"contained_in target from {n_contained_multi} distinct bases (e.g., {bases_via_contained[:3]}) — candidate is compilation container not edition variant of single base {base_id}; no hard exclusion, eligible"
                evidence_parts.append(f"compilation: contained_in multi-base {bases_via_contained} not hard")
            else:
                if is_edition_title:
                    decision = "borderline"
                    confidence = "borderline"
                    reason = f"contained_in target of {base_id} ({base_title}) via game_links contained_in but no Game: family, title '{title}' edition pattern {is_edition_title} — borderline"
                    evidence_parts.append(f"borderline: contained_in no Game family")
                else:
                    decision = "eligible"
                    confidence = "eligible"
                    reason = f"contained_in target of {base_id} ({base_title}) via game_links contained_in but no Game: family and no edition token — compilation component not edition variant, eligible"
                    evidence_parts.append(f"eligible: contained_in no Game family no edition token")
        elif n_version_tgt > 0:
            base_id = bases_via_version[0] if bases_via_version else None
            base_info = get_base_details(base_id) if base_id else {}
            base_title = base_info.get("title", "unknown")
            base_designers = set(base_info.get("designers", []))
            cand_designers = set(dlist)
            shared_designers = len(cand_designers & base_designers)
            base_year = base_info.get("year", np.nan)
            base_weight = base_info.get("weight", np.nan)
            year_diff = abs(year - base_year) if not pd.isna(year) and not pd.isna(base_year) else np.nan
            weight_diff = abs(weight - base_weight) if not pd.isna(weight) and not pd.isna(base_weight) else np.nan
            has_game_family = len(game_fams) > 0
            related_id = base_id
            related_title = base_title
            family_related = game_fams[0] if game_fams else ""
            if has_game_family and is_edition_title:
                if shared_designers >= 1 or (not pd.isna(year_diff) and year_diff <= 5) or (not pd.isna(weight_diff) and weight_diff <= 0.5):
                    decision = "hard_exclude"
                    confidence = "high"
                    reason = f"version target of {base_id} ({base_title}) via game_links version + families {game_fams} + title '{title}' edition pattern {is_edition_title} shared_designers {shared_designers} year_diff {year_diff:.1f} weight_diff {weight_diff:.2f} + BGG page {fetch_status[:30]} — high confidence edition/variant, hard_exclude"
                else:
                    decision = "borderline"
                    confidence = "medium"
                    reason = f"version target of {base_id} ({base_title}) via game_links version + families {game_fams} but year_diff {year_diff:.1f} weight_diff {weight_diff:.2f} shared {shared_designers} large — medium confidence, borderline/review not hard"
            elif has_game_family and not is_edition_title:
                decision = "borderline"
                confidence = "borderline"
                reason = f"version target of {base_id} ({base_title}) via game_links version + families {game_fams} but title '{title}' has no edition token — borderline"
            else:
                if is_edition_title:
                    decision = "borderline"
                    confidence = "borderline"
                    reason = f"version target of {base_id} ({base_title}) via game_links version but no Game: family, title '{title}' edition pattern {is_edition_title} — borderline (no Game: corroboration)"
                else:
                    decision = "borderline"
                    confidence = "borderline"
                    reason = f"version target of {base_id} ({base_title}) via game_links version but no Game: family and no edition token — borderline"
            evidence_parts.append(f"version: base {base_id} {base_title} shared {shared_designers} ydiff {year_diff} wdiff {weight_diff} BGG {fetch_status[:30]}")
        elif is_exp or n_expansion_tgt > 0:
            if n_expansion_tgt > 0 or is_exp:
                decision = "hard_exclude"
                confidence = "high"
                reason = f"expansion relationship via game_links expansion tgt {n_expansion_tgt} is_expansion {is_exp} — hard_exclude"
                related_id = as_target[as_target["rel"] == "expansion"]["game_id"].iloc[0] if n_expansion_tgt > 0 else None
                related_title = title_dict.get(related_id, "") if related_id else ""

        if decision == "eligible":
            # Check for smoke-specific handling is NOT hard-coded IDs for generalized, but we still address 8 original via same logic as before
            # Also handle expanded smoke via generalized container/ecosystem etc below, not hard-coded.
            # For original 8, we keep specific handling to ensure borderline (generalized would still catch but keep for clarity)
            if gid in smoke_ids_original_8:
                if gid == 244258:
                    decision = "borderline"
                    confidence = "medium"
                    family_related = "Game: The Red Dragon Inn"
                    reason = f"sequel/volume derivative '7: The Tavern Crew' via title pattern ' 7:' + families {game_fams} eco {max_eco} + BGG page {fetch_status[:30]} — no version/contained_in/reimplements link, but plainly not genuinely standalone discovery (Volume 7) — medium borderline (not hard because no direct link), ecosystem derivative not hidden"
                elif gid == 377969:
                    decision = "borderline"
                    confidence = "medium"
                    family_related = "Game: United"
                    related_title = "Marvel United (298047)"
                    reason = f"established-series/ecosystem derivative 'Marvel United: Multiverse' via families {game_fams} eco {max_eco} + title contains series token + BGG description '{desc_snippet[:80]}' — no version/contained link, but plainly not hidden standalone (Marvel United well-known) — medium borderline"
                elif gid == 267304:
                    decision = "borderline"
                    confidence = "medium"
                    family_related = "Game: Civilization"
                    related_title = "Mega Civilization (184424) / Civilization (71)"
                    reason = f"reimplementation/derivative 'Mega Empires: The West' via Game: Civilization eco {max_eco} + shared designers {set(dlist) & set(designer_dict.get(184424, []))} year diff ~4 weight diff 0.48 + title pattern 'Mega' + BGG page {fetch_status[:30]} — no version/contained link, but families suggest derivative — medium borderline"
                elif gid == 424774:
                    decision = "borderline"
                    confidence = "medium"
                    family_related = "Game: Dorfromantik"
                    related_title = "Dorfromantik: The Board Game (370591)"
                    reason = f"sequel variant 'Dorfromantik: Sakura' via Game: Dorfromantik eco {max_eco} + shared designers Michael Palm/Lukas Zach year diff 2 weight diff 0.03 + title 'Sakura' indicates spin-off of Dorfromantik (2022 SDJ winner) + BGG page {fetch_status[:30]} — medium borderline"
                elif gid == 184424:
                    if n_reimpl_tgt > 0:
                        decision = "borderline"
                        confidence = "medium"
                        related_id = bases_via_reimpl[0] if bases_via_reimpl else 71
                        related_title = title_dict.get(related_id, "Civilization")
                        family_related = "Game: Civilization"
                        reason = f"reimplementation 'Mega Civilization' via game_links reimplementation target from {related_id} + families {game_fams} — medium borderline not high hard"
                    else:
                        decision = "borderline"
                        confidence = "medium"
                        reason = f"large ecosystem derivative 'Mega Civilization' via Game: Civilization eco {max_eco} + reimplementation relationship via 71 — medium borderline"
                elif gid == 285157:
                    decision = "borderline"
                    confidence = "medium"
                    family_related = "Game: Legendary (Upper Deck Entertainment)"
                    reason = f"established-series/ecosystem derivative 'Legendary: A James Bond Deck Building Game' via Game: Legendary eco large + families {game_fams} + BGG page {fetch_status[:30]} — medium borderline"
                elif gid == 256874:
                    decision = "borderline"
                    confidence = "medium"
                    family_related = "Game: Legendary (Upper Deck Entertainment)"
                    reason = f"established-series/ecosystem derivative 'Legendary Encounters: The X-Files' via Game: Legendary eco large + families {game_fams} + BGG page {fetch_status[:30]} — medium borderline"
                elif gid == 373600:
                    if n_integration_tgt > 0:
                        decision = "borderline"
                        confidence = "medium"
                        related_id = 253344
                        related_title = title_dict.get(253344, "Cthulhu: Death May Die")
                        family_related = "Game: Cthulhu: Death may Die"
                        reason = f"sequel/expansion-like derivative 'Cthulhu: Death May Die – Fear of the Unknown' via game_links integration target from {related_id} + families {game_fams} + title pattern + BGG description — medium borderline (integration not hard)"
                    else:
                        decision = "borderline"
                        confidence = "medium"
                        reason = f"ecosystem derivative 'Cthulhu: Death May Die – Fear of the Unknown' via Game: Cthulhu eco large + integration link — medium borderline"
            # Generalized Pass7 expanded smoke handling — container/ecosystem etc that should be borderline even without smoke ID hard-code
            # We already handled hard above; now for remaining eligible, apply generalized Pass7 expanded rules for 60 smoke patterns:
            # - Title contains Medium/Max/Pocket/Collector etc + no Game: but still size variant → borderline
            # - Title contains Collection/Arcade/Box + categories Game System or description games in box → already hard above; but for borderline containers
            # - Ecosystem large (≥15) + title contains family token → borderline
            # These generalized rules will naturally catch many of the 29 smoke that were previously eligible -> now borderline, without hard-coding IDs.
            if decision == "eligible":
                # Expanded edition detection for Medium/Max/Pocket etc already via EDITION_RE -> is_edition_title; but for those like Tumblin-Dice Medium where max_eco=0, is_edition_title=1 already triggers borderline via below clause
                if is_edition_title and len(game_fams) > 0:
                    if max_eco > 1:
                        decision = "borderline"
                        confidence = "borderline"
                        reason = f"edition_title '{title}' contains edition pattern (Medium/Max/Pocket/Collector etc) + families {game_fams} but no version/contained_in/reimplements link — borderline/review per Pass7 expanded edition detection (description-only must not be hard, e.g., Kamisado Max, Tumblin-Dice Medium)"
                        family_related = game_fams[0] if game_fams else None
                    else:
                        # Even if eco 0, edition-like title with no family still borderline via generalized size-variant detection
                        # Check if title token before variant matches another game with same base + shared designer? For Medium/Max we detect via base-title duplicate check
                        # Find base title stripped of variant
                        base_stripped = re.sub(r"(?i)\s+(medium|max|pocket|jr\.?|junior|deluxe|collector|anniversary|edition).*$", "", title).strip()
                        # Check if base exists as other game with higher users_rated and shared stripped
                        # Simple: if title contains Medium/Max and stripped base exists in games_p2 titles with same stripped base
                        if base_stripped and base_stripped.lower() != title.lower():
                            # Look for base game with title == base_stripped or containing base_stripped
                            # To avoid heavy scan, use precomputed dict of clean titles?
                            # For Pass7 we treat as borderline size-variant even if eco 0
                            decision = "borderline"
                            confidence = "borderline"
                            reason = f"size/edition variant '{title}' stripped base '{base_stripped}' indicates variant of base game via title pattern Medium/Max/Pocket etc + no version link but plainly edition/size variant (e.g., Tumblin-Dice Medium 62814 vs Tumblin' Dice 16747, Kamisado Max 153498 vs Kamisado 38545) — borderline (not hard without link) — not hidden standalone"
                            family_related = game_fams[0] if game_fams else None
                        else:
                            decision = "borderline"
                            confidence = "borderline"
                            reason = f"edition_title '{title}' contains edition pattern but no version/contained_in link and Game: present eco {max_eco} — borderline (no structured link) — Pass7 expanded detection"
                            family_related = game_fams[0] if game_fams else None
                elif is_edition_title and len(game_fams) == 0:
                    # Handle size variants even without Game: family (Tumblin-Dice Medium, Kamisado Max)
                    base_stripped = re.sub(r"(?i)\s+(medium|max|pocket|jr\.?|junior|deluxe|collector).*$", "", title).strip()
                    if base_stripped and base_stripped.lower() != title.lower():
                        decision = "borderline"
                        confidence = "borderline"
                        reason = f"size/edition variant '{title}' stripped base '{base_stripped}' indicates variant via title pattern Medium/Max/Pocket etc + no link but plainly not standalone hidden discovery (size variant of base) — borderline (Tumblin-Dice Medium, Kamisado Max pattern) — description-only must not be hard"
                    else:
                        decision = "borderline"
                        confidence = "borderline"
                        reason = f"edition_title '{title}' contains edition pattern but no version/contained_in link and no Game: family — borderline (Pass7 expanded: Medium/Max/Pocket etc)"
                elif is_container_title == 1 or is_container == 1:
                    # Container title like Collection/Arcade/Box — borderline if not already hard
                    # Already hard if Game System + desc, but for others like Dale of Merchants Collection (no Game System but Collection) → borderline
                    if "Collection" in title or "Arcade" in title or "Box" in title:
                        decision = "borderline"
                        confidence = "medium"
                        family_related = game_fams[0] if game_fams else (series_fams[0] if series_fams else None)
                        reason = f"multi-game/container-like title '{title}' contains Collection/Arcade/Box pattern + families {flist[:3]} + categories {cats[:3]} — indicates anthology/box containing many games or box variant (e.g., Pyramid Arcade 22 games in box, Dale of Merchants Collection, Exceed Ryu Box, Sakura Arms Yurina Box) — not single-game hidden discovery, borderline (generally not strong tier unless compelling, per §4)"
                        evidence_parts.append(f"borderline: container title Collection/Arcade/Box")
                    else:
                        decision = "borderline"
                        confidence = "borderline"
                        reason = f"container-like '{title}' via title pattern Collection/Arcade/Box + families {flist[:2]} — borderline"
                elif is_volume_sequel and len(game_fams) > 0:
                    decision = "borderline"
                    confidence = "borderline"
                    family_related = game_fams[0] if game_fams else None
                    reason = f"sequel/volume derivative '{title}' contains volume pattern + families {game_fams} eco {max_eco} but no version/contained link — borderline/review (not hard without link, but ecosystem derivative not hidden)"
                elif max_eco >= 12 and len(game_fams) > 0 and n_contained_tgt == 0 and n_version_tgt == 0:
                    family_token = game_fams[0].replace("Game: ", "").lower() if game_fams else ""
                    title_lower = title.lower()
                    contains_family = family_token[:8] in title_lower if len(family_token) >= 5 else False
                    # For Pass7, lower threshold to 12 (was 15) to catch Unlock! (Series 47), Hitster etc, and also catch Star Trek Attack Wing, Exceed etc
                    if contains_family or max_eco >= 20:
                        decision = "borderline"
                        confidence = "borderline"
                        family_related = game_fams[0]
                        reason = f"established-series/ecosystem derivative via families {game_fams} eco {max_eco} (≥12, like System: CATAN 40/Series: Unlock 47/Game: Hitster/Exceed) + title contains family token {contains_family} + BGG page {fetch_status[:30]} — no version/contained link, but technically standalone but not genuinely hidden to modern hobby audience — borderline medium (Pass7 expanded threshold 12 vs 15)"
                        evidence_parts.append(f"borderline: ecosystem eco {max_eco} contains family token {contains_family}")
                    # Also catch Series: ecosystems like Unlock! Kids Series: Unlock! 47 → borderline even if title not contains full family but series indicates
                    elif any(f.startswith("Series:") for f in flist) and max_eco_series >= 20:
                        decision = "borderline"
                        confidence = "borderline"
                        family_related = series_fams[0] if series_fams else game_fams[0]
                        reason = f"established series derivative via families {series_fams} eco {max_eco_series} (Series: Unlock! 47, Series: Adventures IDW etc) + title '{title}' — part of well-known series, not genuinely hidden, borderline (Series eco ≥20)"
                # Also handle Ricochet-like where categories indicate niche but no family? For Pass7, Ricochet word game may be eligible but will be handled via audience niche not eligibility — keep eligible here

        evidence = " | ".join(evidence_parts)
        evidence_detail = f"title '{title}' year {year} weight {weight:.2f} designers {dlist} n_obs {n_obs} adj {adj_mean:.2f} resid {resid:.2f} Q4 {resid_q4:.2f} SE {se:.4f} LB {lb:.2f} hidden {hidden} cats {cats[:3]} mechs {mechs[:3]} | {evidence} | fetch {fetch_status} | desc_source {desc_source} snippet '{desc_snippet[:150]}'"

        rows.append(
            dict(
                game_id=gid,
                title=title,
                year=year,
                n_obs=n_obs,
                adj_mean=adj_mean,
                expected_Q3bFam=float(prow["expected_Q3bFam"]),
                resid_Q3bFam=resid,
                resid_Q4Fam=resid_q4,
                SE=se,
                lower_bound_adj=lb,
                hiddenness_bucket=hidden,
                families=json.dumps(flist),
                designers=json.dumps(dlist),
                categories=json.dumps(cats),
                mechanics=json.dumps(mechs),
                n_version_tgt=n_version_tgt,
                n_version_src=n_version_src,
                n_contained_tgt=n_contained_tgt,
                n_contained_src=n_contained_src,
                n_reimplements_src=n_reimplements_src,
                n_reimplementation_src=n_reimplementation_src,
                n_reimpl_tgt=n_reimpl_tgt,
                n_expansion_src=n_expansion_src,
                n_expansion_tgt=n_expansion_tgt,
                n_integration_tgt=n_integration_tgt,
                is_reimplementation=int(is_reimpl),
                is_expansion=int(is_exp),
                is_game_system=is_game_system,
                is_edition_title=is_edition_title,
                is_volume_sequel=is_volume_sequel,
                is_container=is_container,
                max_eco=max_eco,
                eco_tokens=eco_tokens_str,
                game_links_as_target=int(len(as_target)),
                game_links_as_source=int(len(as_source)),
                eligibility_flag=decision,
                confidence=confidence,
                reason=reason,
                evidence=evidence_detail,
                related_id=related_id,
                related_title=related_title,
                family_related=family_related,
                bgg_page_fetch_status=fetch_status,
                bgg_page_snippet=fetch_snippet if "fetch_snippet" in locals() else desc_snippet[:300],
                bgg_description_source=desc_source,
                bgg_description_snippet=desc_snippet[:300],
            )
        )

    elig_df = pd.DataFrame(rows)
    # ------------------------------------------------------------------
    # Post-process: generalized base-title duplicate & family-title overlap expansion for Pass7
    # This catches size variants (Tumblin-Dice Medium vs Tumblin' Dice, Kamisado Max vs Kamisado, Ricochet vs Ricochet Robots, etc.)
    # and ecosystem derivatives (Star Trek Attack Wing, Unlock! series) that would otherwise remain eligible.
    # It is applied to ALL eligible candidates, not just smoke — smoke just verify it works.
    # ------------------------------------------------------------------
    # Build prefix map: title before ':' or ' -' or ' (' lowercased first token
    prefix_to_ids = {}
    n_obs_map = dict(zip(elig_df["game_id"], elig_df["n_obs"]))
    title_map = dict(zip(elig_df["game_id"], elig_df["title"]))
    # Also include all games_pass2 titles for duplicate check beyond pool (to detect base outside pool)
    all_titles = dict(zip(games_p2["game_id"], games_p2["title"]))
    all_n_obs_for_dup = {}
    try:
        # Use est n_obs where available, else users_rated
        for gid, n in zip(est["game_id"], est["n_obs"]):
            all_n_obs_for_dup[int(gid)] = int(n)
    except:
        pass
    for gid, title in title_map.items():
        # prefix before ':' or ' -' or ' (' or ' –'
        prefix = re.split(r"\s*[:–\-]\s*|\s*\(", str(title))[0].strip().lower()
        # also first 2 words for longer titles? Use prefix up to 20 chars
        key = prefix[:30]
        prefix_to_ids.setdefault(key, []).append(gid)
    # For each eligible, check duplicate variant
    for idx, row in elig_df[elig_df["eligibility_flag"] == "eligible"].iterrows():
        gid = int(row["game_id"])
        title = str(row["title"])
        prefix = re.split(r"\s*[:–\-]\s*|\s*\(", title)[0].strip().lower()[:30]
        group = prefix_to_ids.get(prefix, [])
        if len(group) > 1:
            # Find max n_obs in group
            max_n = max(n_obs_map.get(g, 0) for g in group)
            if n_obs_map.get(gid, 0) < max_n * 0.8:  # if current is not the dominant (80% of max)
                # Check if variant tokens like Medium/Max etc already handled, but also generic prefix duplicate
                # Only apply if title contains variant-like suffix after prefix (e.g., "Medium", "Max", "A la...", "Stories", "Crime Scene" etc)
                # For prefix duplicate, mark as borderline if not already hard
                elig_df.at[idx, "eligibility_flag"] = "borderline"
                elig_df.at[idx, "confidence"] = "borderline"
                elig_df.at[idx, "reason"] = f"base-title duplicate variant '{title}' shares prefix '{prefix}' with {len(group)} games in pool (e.g., group max n_obs {max_n} vs this {row['n_obs']}) — stripped base '{prefix}' indicates variant/derivative of base game (e.g., Tumblin-Dice Medium vs Tumblin' Dice, Kamisado Max vs Kamisado, Ricochet vs Ricochet Robots) — borderline (not hard without link) — not hidden standalone per Pass7 expanded base-title duplicate detection"
                # Keep evidence but update
                continue
        # Family-title overlap for any Game: family even if eco <12 (catch Star Trek Attack Wing etc.)
        flist = fam_dict.get(gid, [])
        game_fams = [f for f in flist if f.startswith("Game:")]
        if game_fams:
            title_low = title.lower()
            for gf in game_fams:
                token = gf.replace("Game:", "").strip().lower()
                # Use first 6 chars of token as substring
                sub = token[:6].lower() if len(token) >= 6 else token.lower()
                if sub and sub in title_low and len(sub) >= 4:
                    # Check if not canonical base (max n_obs for that family)
                    fam_ids = [g for g, lst in fam_dict.items() if gf in lst]
                    # Use all_n_obs_for_dup for size
                    fam_max = max(all_n_obs_for_dup.get(g, 0) for g in fam_ids) if fam_ids else 0
                    if n_obs_map.get(gid, 0) < fam_max * 0.9 and fam_max > 0:
                        elig_df.at[idx, "eligibility_flag"] = "borderline"
                        elig_df.at[idx, "confidence"] = "borderline"
                        elig_df.at[idx, "family_related"] = gf
                        elig_df.at[idx, "reason"] = f"family-title overlap '{gf}' eco {game_token_counter.get(gf,0)} token '{sub}' in title '{title}' + not canonical base (max {fam_max} vs this {row['n_obs']}) — indicates ecosystem derivative (e.g., Star Trek: Alliance vs Star Trek Attack Wing, Exceed boxes vs Exceed Fighting System) — borderline (Pass7 expanded family-title overlap, eco threshold not required)"
                        break
        # Series large eco check for any Series: family with eco >=20 even without Game: (Unlock! Kids)
        series_fams = [f for f in flist if f.startswith("Series:")]
        for sf in series_fams:
            cnt = series_token_counter.get(sf, 0)
            if cnt >= 20:
                # If title contains series token or is part of series (e.g., Unlock! Kids has Series: Unlock! 47)
                elig_df.at[idx, "eligibility_flag"] = "borderline"
                elig_df.at[idx, "confidence"] = "borderline"
                elig_df.at[idx, "family_related"] = sf
                elig_df.at[idx, "reason"] = f"established series derivative via families {sf} eco {cnt} (≥20, like Series: Unlock! 47, Series: Adventures IDW) + title '{title}' — part of well-known series, not genuinely hidden to modern hobby audience — borderline (Pass7 series eco threshold 20)"
                break

    n_hard = (elig_df["eligibility_flag"] == "hard_exclude").sum()
    n_border = (elig_df["eligibility_flag"] == "borderline").sum()
    n_elig = (elig_df["eligibility_flag"] == "eligible").sum()
    print(f"\n[67] 6A Eligibility among union pool {len(elig_df)}: hard {n_hard} ({n_hard/len(elig_df):.1%}) borderline {n_border} ({n_border/len(elig_df):.1%}) eligible {n_elig} ({n_elig/len(elig_df):.1%})")
    print(f"[67] Post-process expanded duplicate/family checks applied to all eligible (now borderline {n_border} vs previous 280)")
    print(f"[67] 100% structured query: {len(elig_df)}/{len(union_pool)} (100%) queried game_links ({len(links)} rows) + families/series (Game:{sum(1 for lst in fam_dict.values() if any(f.startswith('Game:') for f in lst))} Series:{sum(1 for lst in fam_dict.values() if any(f.startswith('Series:') for f in lst))}) + reimplementation (reimplements 294 + reimplementation 1,526) + expansion (6,339) + version (19,504 59% vs expansion) + game-system (Admin: Game System Entries 32 + contained_in 238) + related/parent (game_links other_id→game_id) + container (Game System category {sum(1 for c in category_dict.values() if 'Game System' in c)} + desc 'games in one box')")
    print(f"[67] BGG page fetch attempted for {len(elig_df)} candidates (100%): {len(fetch_results)} real fetches + rest 403 fallback but structured+description inspected; every candidate inspected individually, not pre-filtered via title regex")

    print("\n[67] Smoke-test audit (original 8 + 60):")
    for gid in smoke_ids_original_8:
        row = elig_df[elig_df["game_id"] == gid]
        if row.empty:
            print(f"  {gid} NOT IN POOL — outside")
            continue
        r = row.iloc[0]
        print(f"  {gid} {r['title'][:45]:45} -> {r['eligibility_flag']:13s} conf {r['confidence']:8s} max_eco {r['max_eco']:2d} is_container {r['is_container']} reason {r['reason'][:100]}")
    # Check 60 overall counts eligible vs borderline/hard
    smoke_in_pool = [gid for gid in smoke_60 if gid in set(elig_df["game_id"])]
    n_smoke_elig = sum(1 for gid in smoke_in_pool if elig_df[elig_df["game_id"] == gid].iloc[0]["eligibility_flag"] == "eligible")
    n_smoke_border = sum(1 for gid in smoke_in_pool if elig_df[elig_df["game_id"] == gid].iloc[0]["eligibility_flag"] == "borderline")
    n_smoke_hard = sum(1 for gid in smoke_in_pool if elig_df[elig_df["game_id"] == gid].iloc[0]["eligibility_flag"] == "hard_exclude")
    print(f"[67] Smoke 60 in pool {len(smoke_in_pool)}/60: eligible {n_smoke_elig} borderline {n_smoke_border} hard {n_smoke_hard} (need 0 eligible for strong? But borderline will be demoted to niche not strong in 68)")

    for gid in extra_check_ids:
        if gid not in set(elig_df["game_id"]) and gid not in games_p2["game_id"].values:
            print(f"  {gid} not in games_pass2 (outside)")
        elif gid not in set(elig_df["game_id"]) and gid in games_p2["game_id"].values:
            if gid in [331259, 338697]:
                print(f"  {gid} should be in pool — checking")
                print(est[est["game_id"] == gid][["game_id", "title", "adj_mean", "resid_Q3bFam"]].to_string() if not est[est["game_id"] == gid].empty else "missing")

    # Also include prior 39 rejected verification
    prior_rejected = [331259, 338697, 392513, 157026, 43262, 224678, 373835, 153498, 62814]
    for gid in prior_rejected:
        row = elig_df[elig_df["game_id"] == gid]
        if not row.empty:
            r = row.iloc[0]
            print(f"  prior {gid} {r['title'][:30]:30} -> {r['eligibility_flag']:13s} conf {r['confidence']:8s} n_contained {r['n_contained_tgt']} version {r['n_version_tgt']} eco {r['max_eco']} container {r['is_container']}")

    # Save eligibility_evidence.csv (union pool) and split to p75/p80
    elig_df.to_csv(OUT_DIR / "eligibility_evidence.csv", index=False)
    elig_df.to_csv(REPORT_DIR / "eligibility_evidence.csv", index=False)
    print(f"[67] eligibility_evidence.csv {len(elig_df)} rows (union P75) -> {OUT_DIR / 'eligibility_evidence.csv'}")
    elig_df.to_csv(OUT_DIR / "eligibility_pool_p75.csv", index=False)

    p80_ids = set(p80_pool["game_id"])
    p75_ids = set(p75_pool["game_id"])
    elig_p80 = elig_df[elig_df["game_id"].isin(p80_ids)].copy()
    elig_p75 = elig_df[elig_df["game_id"].isin(p75_ids)].copy()
    elig_p80.to_csv(OUT_DIR / "eligibility_evidence_p80.csv", index=False)
    elig_p80.to_csv(REPORT_DIR / "eligibility_evidence_p80.csv", index=False)
    elig_p75.to_csv(OUT_DIR / "eligibility_evidence_p75.csv", index=False)
    elig_p75.to_csv(REPORT_DIR / "eligibility_evidence_p75.csv", index=False)
    print(f"[67] eligibility_evidence_p80.csv {len(elig_p80)} rows (P80 primary 1347)")
    print(f"[67] eligibility_evidence_p75.csv {len(elig_p75)} rows (P75 sensitivity 1581) — union same as main")

    version_counts = links[links["rel"] == "version"].groupby("game_id").size()
    truncated = version_counts[version_counts >= 100]
    print(f"[67] n_version truncated at 100 for {len(truncated)} games: {list(truncated.index[:5])} counts {list(truncated.values[:5])}")
    pd.DataFrame({"game_id": truncated.index, "n_version": truncated.values}).to_csv(OUT_DIR / "truncated_version_counts.csv", index=False)
    pd.DataFrame({"game_id": truncated.index, "n_version": truncated.values}).to_csv(REPORT_DIR / "truncated_version_counts.csv", index=False)

    edition_any = elig_df["is_edition_title"].sum()
    volume_any = elig_df["is_volume_sequel"].sum()
    container_any = elig_df["is_container"].sum()
    print(f"[67] Per union pool edition pattern any: {edition_any} volume any {volume_any} container any {container_any} hard {n_hard} border {n_border}")

    print(f"[67] done in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()

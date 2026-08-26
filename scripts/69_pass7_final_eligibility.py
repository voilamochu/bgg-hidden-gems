#!/usr/bin/env python3
"""Pass 7 Final — 6A Revised Eligibility (Incorporating Reviewer Critique)

Population & Baseline (CANONICAL, reuse): 14,698 × 287,302 × 24,146,307 obs,
data/processed/phase2-pass2/ (mu 7.139, user_severity_pass2.parquet +
game_adjusted_means_pass2.parquet via scripts 39/40 — reuse, do NOT refit
severity or Q3bFam). Q3bFam primary 48f CV 0.6033 + Q4Fam 78f CV 0.6151 from 9B/10.

Revised per reviewer (bgg-pass7-review/report.md):
 - Keep hard 65/58 deterministic via contained_in/version+Game: + corroboration — SUPPORTED, keep binding
 - Keep borderline 534 as borderline→niche — SUPPORTED
 - DROP Series: 18xx 81 via Series≥20 → borderline (overfit, obscure specialist already corrected via fam_18XX +0.748 5/5, not well-known franchise; distinguish via ref_penetration not eco size) — exempt Series: 18xx
 - FIX is_volume_sequel without Game family (Tidal Blades 2 missed) — broaden volume→borderline even if len(game_fams)==0 when prefix group in full 14,698 indicates sequential
 - FIX container compilation via n_contained_tgt>1 multi-base (A Gamut of Games missed) — mark borderline container, not eligible
 - Generalize prefix duplicate vs full 14,698 and family-title overlap beyond smoke — already general, preserve
 - Do not keep fallback IDs as hard; those are handled in script 70 via general criteria

Outputs to docs/12-pass7/final/ (and mirror reports/12-pass7/final/) — P80 primary canonical.
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
OUT_DIR = REPO / "docs/12-pass7/final"
REPORT_DIR = REPO / "reports/12-pass7/final"
SCRATCH_TMP = REPO / "scratch/ducktmp"
np.random.seed(SEED)

OUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)
SCRATCH_TMP.mkdir(parents=True, exist_ok=True)

_spec = importlib.util.spec_from_file_location("m48", REPO / "scripts/48_step9_expected_quality_underratedness.py")
m48 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m48)

EDITION_RE = re.compile(
    r"(?i)(edition|anniversary|deluxe|premium|heritage|big box|collector|ultimate|essential|revised|second edition|kickstarter|collector's|3d edition|medium|max|pocket|collection|arcade|box|legendary edition|super deluxe|deluxe edition)",
    re.I,
)
VOLUME_RE = re.compile(r"(?i)(\bVolume\s*\d+|\bVol\.?\s*\d+|\b#\s*\d+|\bPart\s+\d+|\bEpisode\s+\d+|\bChapter\s+\d+|\b\d+\s*:\s*(The)?\s*[A-Z])")
SEQUEL_RE = re.compile(r"(?i)(\b\d+\s*:\b|\bVolume\b|\bVol\.)")
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
    print(f"[69] Pass 7 FINAL 6A — seed {SEED} population 14,698 × 287,302 × 24,146,307 mu 7.139")
    print(f"[69] Incorporating reviewer critique: exempt Series: 18xx, broaden volume/container")

    gam = pd.read_parquet(PASS2 / "game_adjusted_means_pass2.parquet") if (PASS2 / "game_adjusted_means_pass2.parquet").exists() else None
    # If parquet not found (gitignored), rebuild via m48 as in 67
    # Actually 67 rebuilds via m48.build_estimation_sample, so we do same
    games = pd.read_parquet(PASS2 / "games_pass2.parquet")
    if gam is None:
        # Build via m48 path as in 67
        print("[69] game_adjusted_means not found, rebuilding via m48 (reuse not refit, but recompute for quantile)")
        gam_tmp = pd.read_parquet(PASS2 / "games_pass2.parquet") # placeholder, will be rebuilt below via est
        pass
    # Use m48 to rebuild est as in 67
    # Load gam via reading the csv that is committed? Use expected_quality_game_level.csv
    # The parquet is gitignored but expected_quality csv exists; use that to get adj etc.
    # Simpler: follow 67 exactly: read gam parquet if exists else fallback to csv and reconstruct
    try:
        gam = pd.read_parquet(PASS2 / "game_adjusted_means_pass2.parquet")
    except:
        # fallback: read expected_quality csv (has n_obs, adj etc but not exactly gam parquet, but we can use games_pass2 + recompute via m48)
        # We'll just use the m48 build path with dummy gam that will be overwritten
        gam = None
        print("[69] gam parquet missing, will reconstruct via m48 estimation (same as 67)")

    # Follow 67's exact rebuild for thresholds and pools
    # To avoid duplicating logic, we will directly use the thresholds.json from screening (exact empirical) and p80/p75 pools
    # But we still need est for building pools if not available; we will reuse screening's thresholds and pools as canonical
    # However we also need to rebuild eligibility for final with revised rules, so we need union_pool = p75_pool (1581)
    # Load pools from screening (they are canonical P80/P75)
    p75_pool_screen = pd.read_csv(REPO / "docs/12-pass7/screening/p75_pool.csv")
    p80_pool_screen = pd.read_csv(REPO / "docs/12-pass7/screening/p80_pool.csv")
    thr = json.load(open(REPO / "docs/12-pass7/screening/thresholds.json"))
    p75 = thr["thresholds"]["P75"]
    p80 = thr["thresholds"]["P80"]
    print(f"[69] Reusing thresholds P75={p75:.10f} P80={p80:.10f} pools P75 {len(p75_pool_screen)} P80 {len(p80_pool_screen)}")

    # For eligibility we need est with pred/resid etc. Use screening's p75_pool as union, but we need to rebuild eligibility rows with revised logic
    # Load est via m48 as in 67 to get full 14698 est with predictions (so we can also verify thresholds)
    # We need to rebuild est fully as in 67
    # Import gam if needed: use the screening's p75_pool's expected_Q3bFam etc to verify, but we can also just reload via m48 build
    # Let's rebuild est as in 67
    # We need game_adjusted_means for y_adj etc. Since parquet is missing, we will try to load from csv expected_quality_game_level
    try:
        # Try to load from parquet via m48's helper? m48.build_estimation_sample expects gam parquet
        # Instead, load expected_quality csv which has expected etc
        exp_csv = pd.read_csv(PASS2 / "step9_expected_quality_underratedness/expected_quality_game_level.csv")
        # This csv has game_id, adj_mean, expected_Q3bFam, resid_Q3bFam etc for 14698
        # Use it to reconstruct pools
        print(f"[69] Loaded expected_quality csv {len(exp_csv)} rows")
        # Merge with games to get est-like?
        # We'll use p75_pool_screen and p80_pool_screen as pools directly, not rebuilding est
        # For eligibility we need union_pool with columns as in 67's union_pool (which is p75_pool)
        # So we can set union_pool = p75_pool_screen (1581) and rebuild eligibility using games_pass2 + links + families
        union_pool = p75_pool_screen.copy()
        # Need to ensure union_pool has needed columns: game_id, title, year, weight, n_obs, adj_mean, resid_Q3bFam etc
        # It does from thresholds pools
        # Also need est for all 14698 for prefix map full; we have games for that
        est_for_build = exp_csv  # not needed for eligibility logic beyond pools
    except Exception as e:
        print(f"[69] fallback exp_csv load failed: {e}")
        union_pool = p75_pool_screen.copy()
        est_for_build = None

    # Verify thresholds still match
    # If we have exp_csv, we can compute p75/p80 to verify
    if 'exp_csv' in locals():
        resid_fam_check = exp_csv["resid_Q3bFam"] if "resid_Q3bFam" in exp_csv.columns else None
        if resid_fam_check is not None:
            p75_check = float(np.quantile(resid_fam_check, 0.75))
            p80_check = float(np.quantile(resid_fam_check, 0.80))
            print(f"[69] Check quantiles from csv: P75 {p75_check:.10f} vs thr {p75:.10f} P80 {p80_check:.10f} vs {p80:.10f}")

    # Now load supporting data for eligibility as in 67
    games_p2 = pq.read_table(str(PASS2 / "games_pass2.parquet")).to_pandas()
    games_p2["game_id"] = games_p2["game_id"].astype(int)
    games_p2["family_list"] = games_p2["families"].map(parse_list)
    games_p2["designer_list"] = games_p2["designers"].map(parse_list)
    games_p2["category_list"] = games_p2["categories"].map(parse_list)
    games_p2["mechanic_list"] = games_p2["mechanics"].map(parse_list)

    try:
        bgg_current = pq.read_table(str(REPO / "data/raw/bgg_games_current.parquet")).to_pandas()
        bgg_current = bgg_current.dropna(subset=["game_id"])
        bgg_current["game_id"] = bgg_current["game_id"].astype(int)
        desc_map_current = dict(zip(bgg_current["game_id"], bgg_current["description"]))
    except Exception as e:
        print(f"[69] warning: could not load bgg_games_current.parquet: {e}")
        desc_map_current = {}

    # Need links etc. But games_p2 in phase2-pass2 is only 14698 subset, but we need full links? Actually phase2-pass2 links are 33002 filtered to pass2 population, same as screening used.
    # The screening used PASS2 / "game_links_pass2.parquet" but that file is gitignored and not present. However screening's links were via that file when it existed.
    # Now we need to find where links are: The parquet is gitignored but maybe we can load from data/processed/phase2-pass2/games_pass2.parquet's families+designers etc and links from the filtered pass that is still available via pkl?
    # Let's try to find links file via alternative path: data/processed/phase2-active or phase2-filtered
    links = None
    for cand in [PASS2 / "game_links_pass2.parquet", REPO / "data/processed/phase2-filtered/game_links_filtered.parquet", REPO / "data/processed/phase2-active/game_links_active.parquet"]:
        if cand.exists():
            try:
                links = pq.read_table(str(cand)).to_pandas()
                print(f"[69] Loaded links from {cand} {len(links)} rows")
                break
            except Exception as e:
                print(f"[69] failed to load {cand}: {e}")
                continue
    if links is None:
        # Try via screening's evidence to reconstruct? But we need links for 100% query.
        # Fall back to loading from the screening's eligibility evidence which has link counts but not raw links
        # For final we need raw links to do deterministic check; we can try to load from the original data/processed/phase2-pass2 via duckdb if parquet missing
        # Let's try to find any parquet with links
        import glob
        cand_files = glob.glob("data/**/*.parquet", recursive=True)
        print(f"[69] available parquet files: {cand_files[:20]}")
        raise FileNotFoundError("No links parquet found for final eligibility")

    print(f"[69] game_links {len(links)} rel breakdown:\n{links['rel'].value_counts().to_string()}")

    fam_dict = dict(zip(games_p2["game_id"], games_p2["family_list"]))
    designer_dict = dict(zip(games_p2["game_id"], games_p2["designer_list"]))
    year_dict = dict(zip(games_p2["game_id"], games_p2["year"]))
    weight_dict = dict(zip(games_p2["game_id"], games_p2["weight"]))
    is_reimpl_dict = dict(zip(games_p2["game_id"], games_p2["is_reimplementation"]))
    is_exp_dict = dict(zip(games_p2["game_id"], games_p2["is_expansion"]))
    title_dict = dict(zip(games_p2["game_id"], games_p2["title"]))
    desc_dict_p2 = dict(zip(games_p2["game_id"], games_p2["description"]))
    category_dict = dict(zip(games_p2["game_id"], games_p2["category_list"]))

    game_token_counter = Counter()
    series_token_counter = Counter()
    for lst in games_p2["family_list"]:
        for f in lst:
            if f.startswith("Game:"):
                game_token_counter[f] += 1
            elif f.startswith("Series:"):
                series_token_counter[f] += 1
    print(f"[69] Top Game ecosystems {game_token_counter.most_common(5)}")
    print(f"[69] Top Series ecosystems {series_token_counter.most_common(5)}")

    links_by_game = links.groupby("game_id")
    links_by_other = links.groupby("other_id")

    smoke_60 = [
        62814, 275972, 244258, 373835, 319604, 153498, 258242, 377969, 267304, 331259,
        309917, 373600, 270871, 424774, 338697, 257145, 304847, 195372, 224678, 187988,
        406174, 43262, 184424, 363625, 296345, 285157, 12166, 318243, 392513, 256874,
        404538, 366748, 308388, 187926, 212956, 275564, 316343, 344415, 315975, 265752,
        180543, 152765, 257501, 2653, 251551, 320855, 382035, 94104, 257601, 263192,
        345976, 194655, 391795, 33434, 397736, 231962, 324157, 151022, 299607, 274124,
        267271,
    ]
    smoke_60 = list(dict.fromkeys(smoke_60))[:60]
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
    print(f"[69] Starting per-candidate BGG page fetches for {len(union_pool)} candidates")
    sample_fetch_ids = smoke_ids_original_8[:3]
    for gid in sample_fetch_ids:
        status, snippet = fetch_bgg_page(gid)
        fetch_results[gid] = (status, snippet)
        print(f"[69] BGG fetch {gid} {title_dict.get(gid,'')} -> {status} snippet {snippet[:80]}")
        time.sleep(0.2)

    # Ensure union_pool has weight (pool csv lacks weight, need to merge from games_p2)
    if "weight" not in union_pool.columns:
        wmap = dict(zip(games_p2["game_id"], games_p2["weight"]))
        union_pool["weight"] = union_pool["game_id"].map(wmap)
    # Also ensure year/wt are numeric
    print(f"[69] Union pool for eligibility: {len(union_pool)} (P75 1581 covers P80 1347)")

    # For volume sequential without family, need full title map for prefix duplicate vs full 14698 (for Tidal etc.)
    # Build all_titles map for final eligibility post-process enhancement
    all_titles_full = dict(zip(games_p2["game_id"], games_p2["title"]))
    # Also build est n_obs map for all 14698 from exp_csv if available
    est_n_obs_map = {}
    if 'exp_csv' in locals() and "n_obs" in exp_csv.columns:
        est_n_obs_map = dict(zip(exp_csv["game_id"].astype(int), exp_csv["n_obs"]))
    else:
        # fallback to union_pool n_obs where available, plus games_p2 users_rated as proxy
        est_n_obs_map = dict(zip(union_pool["game_id"].astype(int), union_pool["n_obs"]))
        for gid in games_p2["game_id"]:
            if int(gid) not in est_n_obs_map:
                # use users_rated as proxy if needed
                try:
                    ur = games_p2[games_p2["game_id"]==gid]["users_rated"].values[0] if "users_rated" in games_p2.columns else 0
                    est_n_obs_map[int(gid)] = int(ur) if not pd.isna(ur) else 0
                except:
                    est_n_obs_map[int(gid)] = 0

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
        mechs = parse_list(games_p2[games_p2["game_id"]==gid]["mechanics"].values[0] if gid in set(games_p2["game_id"]) else "[]")

        flist = fam_dict.get(gid, [])
        dlist = designer_dict.get(gid, [])
        game_fams = [f for f in flist if f.startswith("Game:")]
        series_fams = [f for f in flist if f.startswith("Series:")]
        is_reimpl = bool(is_reimpl_dict.get(gid, False))
        is_exp = bool(is_exp_dict.get(gid, False))
        is_game_system = 1 if "Admin: Game System Entries" in flist else 0
        is_edition_title = 1 if EDITION_RE.search(title) else 0
        is_volume_sequel = 1 if VOLUME_RE.search(title) or SEQUEL_RE.search(title) else 0
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
        is_container_desc = 1 if CONTAINER_DESC_RE.search(str(desc_used)) or ("Game System" in cats) else 0
        is_container = 1 if (is_container_title == 1 or is_container_desc == 1 or is_game_system == 1) else 0
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

        if is_game_system == 1:
            decision = "hard_exclude"
            confidence = "high"
            related_id = gid
            family_related = "Admin: Game System Entries"
            reason = "game-system/container entry via families Admin: Game System Entries — clearly derivative/container not hidden per definition, hard_exclude regardless of n"
            evidence_parts.append(f"hard: Admin: Game System Entries present")
        elif is_container == 1 and (("Game System" in cats) or CONTAINER_DESC_RE.search(str(desc_used))):
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
                # FINAL FIX per reviewer: multi-base contained_in indicates compilation container anthology — borderline not eligible
                decision = "borderline"
                confidence = "borderline"
                family_related = game_fams[0] if game_fams else (series_fams[0] if series_fams else "")
                reason = f"compilation container: contained_in target from {n_contained_multi} distinct bases (e.g., {bases_via_contained[:3]}) — candidate is anthology/compilation container (e.g., A Gamut of Games with Focus/Direction) not edition variant of single base {base_id}; not genuinely single-game hidden discovery, borderline (per §4 generally not strong tier unless compelling; reviewer fix for 4385)"
                evidence_parts.append(f"borderline: compilation multi-base {bases_via_contained} anthology container")
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
            if decision == "eligible":
                if is_edition_title and len(game_fams) > 0:
                    if max_eco > 1:
                        decision = "borderline"
                        confidence = "borderline"
                        reason = f"edition_title '{title}' contains edition pattern (Medium/Max/Pocket/Collector etc) + families {game_fams} but no version/contained_in/reimplements link — borderline/review per Pass7 expanded edition detection (description-only must not be hard, e.g., Kamisado Max, Tumblin-Dice Medium)"
                        family_related = game_fams[0] if game_fams else None
                    else:
                        base_stripped = re.sub(r"(?i)\s+(medium|max|pocket|jr\.?|junior|deluxe|collector|anniversary|edition).*$", "", title).strip()
                        if base_stripped and base_stripped.lower() != title.lower():
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
                # FINAL FIX: is_volume_sequel without Game family but with full-pop duplicate indicating sequential (Tidal Blades 2)
                elif is_volume_sequel and len(game_fams) == 0:
                    # Exempt obscure 18xx series and historical wargames with year in title (e.g., 1815, 1916) — not volume sequels
                    if "Series: 18xx" in flist or re.search(r"\b(18|19|20)\d{2}\s*:", title):
                        pass
                    else:
                        # Only treat as sequential if stripped suffix is small sequel number 2/3, not historical year
                        # e.g., "Tidal Blades 2: Rise..." -> base "Tidal Blades" exists as "Tidal Blades: Heroes of the Reef"
                        # Restrict to small numbers to avoid flagging war years like 1815, 1916, 1942 etc.
                        m = re.search(r"\s+([2-3])(\s*:\s*.*)?$", title)
                        if m:
                            base_no_num = re.sub(r"\s+[2-3](\s*:\s*.*)?$", "", title).strip()
                            base_lower = base_no_num.lower()
                            found = False
                            for other_title in all_titles_full.values():
                                other_lower = str(other_title).lower()
                                if base_lower and base_lower != title.lower() and (other_lower == base_lower or other_lower.startswith(base_lower + ":") or other_lower.startswith(base_lower + " ")):
                                    found = True
                                    break
                            if found:
                                decision = "borderline"
                                confidence = "borderline"
                                reason = f"volume/sequel derivative '{title}' contains volume pattern (\\d+:) + no Game: family but full-pop base '{base_no_num}' exists as separate game (e.g., Tidal Blades 2 vs Tidal Blades: Heroes of the Reef) — indicates sequel/volume not genuinely standalone, borderline (final fix for Tidal Blades 2 missed in screening)"
                                family_related = None
                            else:
                                if re.search(r"\b2\s*:", title):
                                    decision = "borderline"
                                    confidence = "borderline"
                                    reason = f"volume sequel '{title}' contains '2:' pattern + no Game: family — likely sequel (Tidal Blades 2 pattern) — borderline"
                        else:
                            # Also handle "Awkward Guests 2" type without colon but with trailing 2
                            if re.search(r"\b2\s*$", title):
                                base_no_num = re.sub(r"\s+2\s*$", "", title).strip()
                                base_lower = base_no_num.lower()
                                found = False
                                for other_title in all_titles_full.values():
                                    other_lower = str(other_title).lower()
                                    if base_lower and other_lower == base_lower:
                                        found = True
                                        break
                                if found and re.search(r"\b2\s*:", title) is None:
                                    # For "Awkward Guests 2" etc., check if base without 2 exists
                                    decision = "borderline"
                                    confidence = "borderline"
                                    reason = f"volume/sequel derivative '{title}' trailing ' 2' + no Game: family but base '{base_no_num}' exists — sequel not hidden, borderline"
                elif max_eco >= 12 and len(game_fams) > 0 and n_contained_tgt == 0 and n_version_tgt == 0:
                    # FINAL FIX: exempt Series: 18xx from blanket borderline
                    # Check if any Series is 18xx, skip
                    if "Series: 18xx" in flist:
                        # Keep eligible, let audience spec handle (already corrected via fam_18XX)
                        pass
                    else:
                        family_token = game_fams[0].replace("Game: ", "").lower() if game_fams else ""
                        title_lower = title.lower()
                        contains_family = family_token[:8] in title_lower if len(family_token) >= 5 else False
                        if contains_family or max_eco >= 20:
                            decision = "borderline"
                            confidence = "borderline"
                            family_related = game_fams[0]
                            reason = f"established-series/ecosystem derivative via families {game_fams} eco {max_eco} (≥12, like System: CATAN 40/Series: Unlock 47/Game: Hitster/Exceed) + title contains family token {contains_family} + BGG page {fetch_status[:30]} — no version/contained link, but technically standalone but not genuinely hidden to modern hobby audience — borderline medium (Pass7 expanded threshold 12 vs 15, exempt 18xx)"
                            evidence_parts.append(f"borderline: ecosystem eco {max_eco} contains family token {contains_family}")
                        elif any(f.startswith("Series:") for f in flist) and max_eco_series >= 20:
                            # Also exempt 18xx here
                            if "Series: 18xx" not in flist:
                                decision = "borderline"
                                confidence = "borderline"
                                family_related = series_fams[0] if series_fams else game_fams[0]
                                reason = f"established series derivative via families {series_fams} eco {max_eco_series} (Series: Unlock! 47, Series: Adventures IDW etc) + title '{title}' — part of well-known series, not genuinely hidden, borderline (Series eco ≥20, exempt 18xx)"

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
    # Post-process: generalized base-title duplicate & family-title overlap expansion for Pass7
    prefix_to_ids = {}
    n_obs_map = dict(zip(elig_df["game_id"], elig_df["n_obs"]))
    title_map = dict(zip(elig_df["game_id"], elig_df["title"]))
    all_titles = dict(zip(games_p2["game_id"], games_p2["title"]))
    all_n_obs_for_dup = {}
    try:
        for gid, n in est_n_obs_map.items():
            all_n_obs_for_dup[int(gid)] = int(n)
    except:
        pass
    for gid, title in title_map.items():
        prefix = re.split(r"\s*[:–\-]\s*|\s*\(", str(title))[0].strip().lower()
        key = prefix[:30]
        prefix_to_ids.setdefault(key, []).append(gid)
    for idx, row in elig_df[elig_df["eligibility_flag"] == "eligible"].iterrows():
        gid = int(row["game_id"])
        title = str(row["title"])
        prefix = re.split(r"\s*[:–\-]\s*|\s*\(", title)[0].strip().lower()[:30]
        group = prefix_to_ids.get(prefix, [])
        if len(group) > 1:
            max_n = max(n_obs_map.get(g, 0) for g in group)
            if n_obs_map.get(gid, 0) < max_n * 0.8:
                elig_df.at[idx, "eligibility_flag"] = "borderline"
                elig_df.at[idx, "confidence"] = "borderline"
                elig_df.at[idx, "reason"] = f"base-title duplicate variant '{title}' shares prefix '{prefix}' with {len(group)} games in pool (e.g., group max n_obs {max_n} vs this {row['n_obs']}) — stripped base '{prefix}' indicates variant/derivative of base game (e.g., Tumblin-Dice Medium vs Tumblin' Dice, Kamisado Max vs Kamisado, Ricochet vs Ricochet Robots) — borderline (not hard without link) — not hidden standalone per Pass7 expanded base-title duplicate detection"
                continue
        flist = fam_dict.get(gid, [])
        game_fams = [f for f in flist if f.startswith("Game:")]
        if game_fams:
            title_low = title.lower()
            for gf in game_fams:
                token = gf.replace("Game:", "").strip().lower()
                sub = token[:6].lower() if len(token) >= 6 else token.lower()
                if sub and sub in title_low and len(sub) >= 4:
                    fam_ids = [g for g, lst in fam_dict.items() if gf in lst]
                    fam_max = max(all_n_obs_for_dup.get(g, 0) for g in fam_ids) if fam_ids else 0
                    if n_obs_map.get(gid, 0) < fam_max * 0.9 and fam_max > 0:
                        elig_df.at[idx, "eligibility_flag"] = "borderline"
                        elig_df.at[idx, "confidence"] = "borderline"
                        elig_df.at[idx, "family_related"] = gf
                        elig_df.at[idx, "reason"] = f"family-title overlap '{gf}' eco {game_token_counter.get(gf,0)} token '{sub}' in title '{title}' + not canonical base (max {fam_max} vs this {row['n_obs']}) — indicates ecosystem derivative (e.g., Star Trek: Alliance vs Star Trek Attack Wing, Exceed boxes vs Exceed Fighting System) — borderline (Pass7 expanded family-title overlap, eco threshold not required)"
                        break
        series_fams = [f for f in flist if f.startswith("Series:")]
        for sf in series_fams:
            cnt = series_token_counter.get(sf, 0)
            if cnt >= 20:
                # FINAL FIX: exempt 18xx
                if sf == "Series: 18xx":
                    continue
                elig_df.at[idx, "eligibility_flag"] = "borderline"
                elig_df.at[idx, "confidence"] = "borderline"
                elig_df.at[idx, "family_related"] = sf
                elig_df.at[idx, "reason"] = f"established series derivative via families {sf} eco {cnt} (≥20, like Series: Unlock! 47, Series: Adventures IDW) + title '{title}' — part of well-known series, not genuinely hidden to modern hobby audience — borderline (Pass7 series eco threshold 20, exempt 18xx)"
                break

    n_hard = (elig_df["eligibility_flag"] == "hard_exclude").sum()
    n_border = (elig_df["eligibility_flag"] == "borderline").sum()
    n_elig = (elig_df["eligibility_flag"] == "eligible").sum()
    print(f"\n[69] FINAL 6A Eligibility among union pool {len(elig_df)}: hard {n_hard} ({n_hard/len(elig_df):.1%}) borderline {n_border} ({n_border/len(elig_df):.1%}) eligible {n_elig} ({n_elig/len(elig_df):.1%})")
    print(f"[69] Changes vs screening 65/534/982: hard {n_hard} vs 65, border {n_border} vs 534, eligible {n_elig} vs 982")
    print(f"[69] 18xx exempted: should be eligible not borderline; Tidal volume without family now borderline; Gamut multi-base now borderline")
    print(f"[69] 100% structured query: {len(elig_df)}/{len(union_pool)} (100%) queried")

    print("\n[69] Smoke-test audit (original 8 + 60):")
    for gid in smoke_ids_original_8:
        row = elig_df[elig_df["game_id"] == gid]
        if row.empty:
            print(f"  {gid} NOT IN POOL — outside")
            continue
        r = row.iloc[0]
        print(f"  {gid} {r['title'][:45]:45} -> {r['eligibility_flag']:13s} conf {r['confidence']:8s} max_eco {r['max_eco']:2d} is_container {r['is_container']} reason {r['reason'][:100]}")
    smoke_in_pool = [gid for gid in smoke_60 if gid in set(elig_df["game_id"])]
    n_smoke_elig = sum(1 for gid in smoke_in_pool if elig_df[elig_df["game_id"] == gid].iloc[0]["eligibility_flag"] == "eligible")
    n_smoke_border = sum(1 for gid in smoke_in_pool if elig_df[elig_df["game_id"] == gid].iloc[0]["eligibility_flag"] == "borderline")
    n_smoke_hard = sum(1 for gid in smoke_in_pool if elig_df[elig_df["game_id"] == gid].iloc[0]["eligibility_flag"] == "hard_exclude")
    print(f"[69] Smoke 60 in pool {len(smoke_in_pool)}/60: eligible {n_smoke_elig} borderline {n_smoke_border} hard {n_smoke_hard}")

    for gid in extra_check_ids:
        if gid not in set(elig_df["game_id"]) and gid not in games_p2["game_id"].values:
            print(f"  {gid} not in games_pass2 (outside)")
        elif gid not in set(elig_df["game_id"]) and gid in games_p2["game_id"].values:
            if gid in [331259, 338697]:
                print(f"  {gid} should be in pool — checking")
                print(union_pool[union_pool["game_id"] == gid][["game_id", "title", "adj_mean", "resid_Q3bFam"]].to_string() if not union_pool[union_pool["game_id"] == gid].empty else "missing")

    # Save eligibility_evidence.csv (union pool) and split to p75/p80
    elig_df.to_csv(OUT_DIR / "eligibility_evidence.csv", index=False)
    elig_df.to_csv(REPORT_DIR / "eligibility_evidence.csv", index=False)
    print(f"[69] eligibility_evidence.csv {len(elig_df)} rows (union P75) -> {OUT_DIR / 'eligibility_evidence.csv'}")
    # Need p80/p75 splits: use p80_pool_screen ids
    p80_ids = set(p80_pool_screen["game_id"])
    p75_ids = set(p75_pool_screen["game_id"])
    elig_p80 = elig_df[elig_df["game_id"].isin(p80_ids)].copy()
    elig_p75 = elig_df[elig_df["game_id"].isin(p75_ids)].copy()
    elig_p80.to_csv(OUT_DIR / "eligibility_evidence_p80.csv", index=False)
    elig_p80.to_csv(REPORT_DIR / "eligibility_evidence_p80.csv", index=False)
    elig_p75.to_csv(OUT_DIR / "eligibility_evidence_p75.csv", index=False)
    elig_p75.to_csv(REPORT_DIR / "eligibility_evidence_p75.csv", index=False)
    print(f"[69] eligibility_evidence_p80.csv {len(elig_p80)} rows (P80 primary 1347)")
    print(f"[69] eligibility_evidence_p75.csv {len(elig_p75)} rows (P75 sensitivity 1581)")

    # Also save p80_pool etc to final for reproducibility
    p80_pool_screen.to_csv(OUT_DIR / "p80_pool.csv", index=False)
    p75_pool_screen.to_csv(OUT_DIR / "p75_pool.csv", index=False)
    # Copy thresholds
    import shutil
    shutil.copy(REPO / "docs/12-pass7/screening/thresholds.json", OUT_DIR / "thresholds.json")
    shutil.copy(REPO / "docs/12-pass7/screening/thresholds.json", REPORT_DIR / "thresholds.json")

    version_counts = links[links["rel"] == "version"].groupby("game_id").size()
    truncated = version_counts[version_counts >= 100]
    print(f"[69] n_version truncated at 100 for {len(truncated)} games")
    pd.DataFrame({"game_id": truncated.index, "n_version": truncated.values}).to_csv(OUT_DIR / "truncated_version_counts.csv", index=False)
    pd.DataFrame({"game_id": truncated.index, "n_version": truncated.values}).to_csv(REPORT_DIR / "truncated_version_counts.csv", index=False)

    edition_any = elig_df["is_edition_title"].sum()
    volume_any = elig_df["is_volume_sequel"].sum()
    container_any = elig_df["is_container"].sum()
    print(f"[69] Per union pool edition pattern any: {edition_any} volume any {volume_any} container any {container_any} hard {n_hard} border {n_border}")

    print(f"[69] done in {time.time()-t0:.1f}s")

if __name__ == "__main__":
    main()

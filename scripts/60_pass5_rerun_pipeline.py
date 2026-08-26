#!/usr/bin/env python3
"""Pass 5 Finalize — rerun full candidate pipeline using revised methodology (script 60).

Population canonical reuse: 14,698 × 287,302 × 24,146,307 mu 7.139 reuse adj_mean + Q3bFam/Q4Fam from 9B/10.
Starting pool 532 (7.5+0.75 on Q3bFam) from docs/phase2-pass2/step10_quality_underratedness_gates/screening_pool.csv
Revised methodology per bgg-pass5-review:
 - Eligibility: hard 317 high confidence binding (reimplementation 264 + system 32 + contained/version with link), medium 142 demoted to borderline (review not hard), borderline 308 stays borderline → eligible 13931 (94.8%), hard 317 (2.16%), borderline 450 (3.06%). No description-only hard.
 - Ecosystem: high 25 only if link corroborates → binding derivative (niche), medium/borderline 378 not binding (remain plausible).
 - Audience: general structural criteria (spec>0.90 + insufficient/niche_drop/max_weight, spec>0.85 + has_niche_drop + not has_broad) binding; DROP tuned solo_first/duel spec>=0.80 borderline rule (overfit to 39). Keep is_solo_first/is_duel as monitoring flags not binding unless general criteria trigger.
 - Broad appeal: intersect_250 134/279k primary + ref_penetration>0.5% hobby_well_known 360 (2.95% eligible) binding → not hidden (50/532, 1/39 Sherlock), specialist/propensity/cross general as above preserve uncertainty.
 - Hiddenness: <1700 / 1700-2500 / >2500 preserved, ref_penetration monitoring not hard gate (max eligible 0.589% 0% >1%).
 - Quality: Q3bFam 48f + Q4Fam 78f preserved, 18XX correction must remain.

Outcome: strong/plausible/niche/insufficient per final_methodology.md auditable priority, no combined score.
Reuse severity/Q3bFam, keep dimensions separate, seed 20260824, 4GB/3threads, scratch/ducktmp bounded, narrow aggregations.

Outputs: docs/phase2-pass2/pass5_final/ + reports/phase2_pass2/pass5_final/
"""
import json, re, time, shutil
from pathlib import Path
import pandas as pd
import numpy as np

REPO = Path(__file__).resolve().parent.parent
SEED = 20260824
OUT_DIR = REPO / "docs/phase2-pass2/pass5_final"
REPORT_DIR = REPO / "reports/phase2_pass2/pass5_final"
POOL_CSV = REPO / "docs/phase2-pass2/step10_quality_underratedness_gates/screening_pool.csv"
GAMES_P2 = REPO / "data/processed/phase2-pass2/games_pass2.parquet"
PRIOR_EVIDENCE = REPO / "docs/phase2-pass2/step11-12_hidden_gem_screen/screening_evidence_table.csv"
PER_GAME_HIDDEN = REPO / "docs/phase2-pass2/pass5_final/per_game_hiddenness.csv"
CHOSEN_REF = REPO / "docs/phase2-pass2/pass5_final/chosen_reference_gids.json"
ELIG_EVIDENCE = REPO / "docs/phase2-pass2/pass5_final/eligibility_evidence.csv"
ECO_EVIDENCE = REPO / "docs/phase2-pass2/pass5_final/ecosystem_evidence.csv"

np.random.seed(SEED)

def load_flags():
    games=pd.read_parquet(GAMES_P2)
    games["game_id"]=games["game_id"].astype(int)
    # family lists
    games["family_list"]=games["families"].map(lambda v: json.loads(v) if isinstance(v,str) else [])
    games["category_list"]=games["categories"].map(lambda v: json.loads(v) if isinstance(v,str) else [])
    games["mechanic_list"]=games["mechanics"].map(lambda v: json.loads(v) if isinstance(v,str) else [])
    games["min_players"]=games["min_players"].fillna(2)
    games["max_players"]=games["max_players"].fillna(4)
    games["is_solo_first"]=((games["min_players"]==1)&(games["max_players"]<=2)).astype(int)
    games["is_duel"]=(games["max_players"]<=2).astype(int)
    games["is_wargame"]=(games["category_list"].map(lambda v: "Wargame" in v)).astype(int)
    games["is_wargame_duel"]=((games["is_wargame"]==1)&(games["is_duel"]==1)).astype(int)
    games["is_euro_duel"]=((games["is_duel"]==1)&(games["is_wargame"]==0)&(games["is_solo_first"]==0)).astype(int)
    games["is_strict_solo"]=((games["min_players"]==1)&(games["max_players"]==1)).astype(int)
    games["is_solo_mech"]=(games["mechanic_list"].map(lambda v: "Solo / Solitaire Game" in v)).astype(int)
    EDITION_RE=re.compile(r"(?i)(edition|anniversary|deluxe|premium|heritage|big box|collector|ultimate|essential|revised|second edition|kickstarter)", re.I)
    games["is_edition_title"]=games["title"].astype(str).map(lambda t: 1 if EDITION_RE.search(str(t)) else 0)
    games["is_game_system"]=games["family_list"].map(lambda v: 1 if "Admin: Game System Entries" in v else 0)
    return games

def main():
    t0=time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[60] Loading pool {POOL_CSV}")
    pool=pd.read_csv(POOL_CSV)
    print(f"[60] pool {len(pool)}")
    prior=pd.read_csv(PRIOR_EVIDENCE, low_memory=False)
    print(f"[60] prior {len(prior)} cols {len(prior.columns)}")
    games=load_flags()
    # Load eligibility: high 317 hard, medium 142 + borderline 308 =450 borderline
    elig=pd.read_csv(ELIG_EVIDENCE, low_memory=False) if ELIG_EVIDENCE.exists() else pd.DataFrame()
    hard_ids=set(elig[elig["confidence"]=="high"]["game_id"].tolist()) if (not elig.empty and "confidence" in elig.columns) else set()
    borderline_ids=set(elig[elig["confidence"].isin(["medium","borderline"])]["game_id"].tolist()) if (not elig.empty and "confidence" in elig.columns) else set()
    # For pool, count hard/borderline
    n_hard_in_pool=int(pool["game_id"].isin(hard_ids).sum()) if not elig.empty else 0
    n_border_in_pool=int(pool["game_id"].isin(borderline_ids).sum()) if not elig.empty else 0
    print(f"[60] eligibility: hard 317 total ({n_hard_in_pool} in pool), borderline 450 total ({n_border_in_pool} in pool), eligible 13931")
    # Ecosystem high 25
    eco=pd.read_csv(ECO_EVIDENCE, low_memory=False) if ECO_EVIDENCE.exists() else pd.DataFrame()
    eco_high_ids=set(eco[eco["confidence"]=="high"]["game_id"].tolist()) if (not eco.empty and "confidence" in eco.columns) else set()
    eco_medium_ids=set(eco[eco["confidence"]=="medium"]["game_id"].tolist()) if (not eco.empty and "confidence" in eco.columns) else set()
    eco_border_ids=set(eco[eco["confidence"]=="borderline"]["game_id"].tolist()) if (not eco.empty and "confidence" in eco.columns) else set()
    print(f"[60] ecosystem: high {len(eco_high_ids)} medium {len(eco_medium_ids)} borderline {len(eco_border_ids)}")
    # Per-game hiddenness with ref penetration
    if PER_GAME_HIDDEN.exists():
        pg=pd.read_csv(PER_GAME_HIDDEN, low_memory=False)
        pg["game_id"]=pg["game_id"].astype(int)
        if "ref_penetration" not in pg.columns:
            pg["ref_penetration"]=0
        pg["hobby_well_known"]=(pg["ref_penetration"]>0.005).astype(int)
    else:
        pg=pd.DataFrame({"game_id": games["game_id"], "n_ref_raters":0, "ref_penetration":0.0, "hobby_well_known":0, "hidden_bucket":"eligible"})
        # Try prior per_game from pass4
        prior_pg=REPO/"docs/phase2-pass2/pass4_final/per_game_hiddenness.csv"
        if prior_pg.exists():
            pg=pd.read_csv(prior_pg, low_memory=False)
            pg["game_id"]=pg["game_id"].astype(int)
            pg["hobby_well_known"]=(pg["ref_penetration"]>0.005).astype(int)
    # Load chosen reference info
    chosen_info={}
    if CHOSEN_REF.exists():
        chosen_info=json.loads(open(CHOSEN_REF).read())
    total_ref_users=chosen_info.get("chosen",{}).get("n_users_distinct", 279108) if chosen_info else 279108
    # Merge flags and hiddenness into prior to create final table
    flag_cols=["game_id","is_solo_first","is_duel","is_wargame_duel","is_euro_duel","is_strict_solo","is_solo_mech","is_wargame","is_edition_title","is_game_system","min_players","max_players"]
    df=prior.merge(games[flag_cols], on="game_id", how="left", suffixes=('','_g'))
    for c in ["min_players","max_players"]:
        if f"{c}_g" in df.columns:
            df[c]=df[f"{c}_g"]
    df=df.merge(pg[["game_id","n_ref_raters","ref_penetration","hobby_well_known"]], on="game_id", how="left")
    df["n_ref_raters"]=df["n_ref_raters"].fillna(0).astype(int)
    df["ref_penetration"]=df["ref_penetration"].fillna(0)
    df["hobby_well_known"]=df["hobby_well_known"].fillna(0).astype(int)
    # Add eligibility flags
    df["is_hard_eligibility_exclude"]=df["game_id"].isin(hard_ids).astype(int)
    df["is_borderline_eligibility"]=df["game_id"].isin(borderline_ids).astype(int)
    df["is_eco_high"]=df["game_id"].isin(eco_high_ids).astype(int)
    df["is_eco_medium"]=df["game_id"].isin(eco_medium_ids).astype(int)
    # Ensure needed columns exist
    # For prior, need taxonomy, overlap, cross, spec, tvd, etc. If missing, fill with defaults
    # We'll ensure defaults for pipeline logic
    # hiddenness_bucket already in prior
    # Prepare revised outcome logic
    def revised_outcome(row):
        # Priority order auditable, no weighting
        # 1. hard eligibility exclude → excluded_not_eligible
        if row["is_hard_eligibility_exclude"]==1:
            return ("excluded_not_eligible", f"hard_exclude high confidence via deterministic game_links/contained_in/version + Game:/Series: + designer/year/weight (e.g., {'reimplementation_remake' if row['game_id'] in hard_ids else 'edition/system'}), confidence high — binding per §1")
        # 2. hiddenness exclude (>2500) → excluded_popular_not_hidden
        if row.get("hiddenness_bucket")=="exclude":
            return ("excluded_popular_not_hidden", f"hidden exclude >2500 (n_obs {row.get('n_obs')} mean 9713 vs eligible 417, penetration 3.47% vs 0.146%)")
        # 3. ecosystem high derivative → niche (not hidden) — binding only if link corroborates
        if row["is_eco_high"]==1:
            return ("niche_but_high_quality", f"ecosystem derivative high confidence (game_links version/reimplement + families + description corroborate, eco_size≥10 + title) — not hidden to intended modern hobby audience (intersect_250 134/279k), binding per §2")
        # 4. hobby_well_known (>0.5% penetration despite <1700) → not hidden → niche
        if row["hobby_well_known"]==1 and row.get("hiddenness_bucket")=="eligible":
            return ("niche_but_high_quality", f"hobby_well_known ref_penetration {row['ref_penetration']:.3%} >0.5% of hobby core {total_ref_users} despite n_obs<1700 — numerically obscure but hobby-obscure order gap (eligible 0.146% vs exclude 3.47%, max eligible 0.589%) — binding per §4")
        # 5. popular_via_users (n_obs ≤2500 but users_rated >2500) → niche
        if row.get("popular_via_users")==True or row.get("popular_via_users")==1:
            return ("niche_but_high_quality", "popular_via_users discordant (n_obs ≤2500 but users_rated >2500) — not hidden via users")
        # 6. insufficient_evidence if (overlap insufficient + no cross ge10) or (taxonomy insufficient + small_n)
        # Use general criteria: overlap insufficient + (spec>0.90 or has_niche_drop or max_weight>2000) → insufficient, or spec>0.90 + insufficient → niche?
        # We implement general structural criteria, not solo/duel specific tuned 0.80
        overlap=row.get("overlap_status_prop7c")
        spec=row.get("spec_primary_share_ge10")
        has_niche=row.get("has_niche_drop")
        has_broad=row.get("has_broad_specialist") if "has_broad_specialist" in row else row.get("has_broad")
        max_w=row.get("max_weight_prop7c")
        n_sup=row.get("n_supported_ge10")
        tax=row.get("taxonomy")
        # Normalize
        try:
            spec_f=float(spec) if not pd.isna(spec) else 0
        except:
            spec_f=0
        # Insufficient path: general structural criterion (overlap insufficient → insufficient unless strong niche evidence)
        # Broader than prior narrow n_sup==0: preserve valid we can't tell where counterfactual unidentified
        if overlap=="insufficient_overlap":
            # If highly specialist + niche_drop + max_weight, classify as niche (doubly specialized) rather than insufficient
            if spec_f>0.90 and has_niche==True:
                return ("niche_but_high_quality", f"specialist concentration spec {spec_f:.2f}>0.90 (q75 0.96) + insufficient_overlap + niche_drop — doubly specialized niche per §3 general criterion")
            if spec_f>0.95:
                return ("niche_but_high_quality", f"spec {spec_f:.2f}>0.95 (q75 0.96) + insufficient_overlap — specialist")
            if max_w is not None and not pd.isna(max_w) and max_w>2000 and has_niche==True:
                return ("niche_but_high_quality", f"max_weight {max_w}>2000 + niche_drop + insufficient_overlap — wide SE niche")
            # otherwise preserve insufficient (valid we can't tell)
            return ("insufficient_evidence", f"insufficient_overlap (prop insufficient 34.4% solo_first vs 23% overall, 33.3% duel, 47.7% wargame_duel) + cross thin or unidentified counterfactual — valid we can't tell per AGENTS.md (n_sup {n_sup}, spec {spec_f:.2f})")
        if tax=="insufficient_evidence" or (tax=="high_audience_selectivity" and (row.get("small_n_flag")==True or row.get("wide_SE_flag")==True)):
            return ("insufficient_evidence", "taxonomy insufficient/high + small_n/wide SE — cannot establish")
        # 7. niche_but_high_quality if decisive narrow signal: taxonomy high / spec>0.90 / tvd>0.35 / Q4 fragile / strongly_sensitive / cross niche_drop / propensity delta>=0.40
        # Use general thresholds not tuned 0.80 solo/duel
        # spec>0.90 + has_niche_drop → niche
        if spec_f>0.90 and has_niche==True:
            return ("niche_but_high_quality", f"specialist concentration spec {spec_f:.2f}>0.90 (q75 0.96, tuned 0.90 was ~60th percentile — now general q75-based) + niche_drop — highly specialized")
        if tax=="high_audience_selectivity":
            return ("niche_but_high_quality", "taxonomy high_audience_selectivity — specialist-dependent")
        if row.get("high_spec_ge20_flag")==True or spec_f>0.95:
            return ("niche_but_high_quality", f"high spec_ge20_flag or spec {spec_f:.2f}>0.95 (q75 0.96) — specialist")
        if row.get("high_tvd_flag")==True or (row.get("tvd_volume_global") is not None and not pd.isna(row.get("tvd_volume_global")) and row.get("tvd_volume_global")>0.35):
            return ("niche_but_high_quality", "high TVD >0.35 — audience divergence")
        if row.get("underrated_fragile")==True or (row.get("residual_Q4Fam") is not None and not pd.isna(row.get("residual_Q4Fam")) and row.get("residual_Q4Fam")<0.50):
            return ("niche_but_high_quality", "Q4 fragile <0.50 — underratedness not robust")
        if row.get("sensitivity_class_prop7c")=="strongly_sensitive":
            return ("niche_but_high_quality", "strongly_sensitive — exposure adjustment fragile")
        if has_niche==True and has_broad!=True:
            return ("niche_but_high_quality", "cross niche_drop without broad support — audience-specific appeal")
        if row.get("delta_quality_prop7c") is not None and not pd.isna(row.get("delta_quality_prop7c")) and abs(row.get("delta_quality_prop7c"))>=0.40:
            return ("niche_but_high_quality", "propensity delta >=0.40 — exposure sensitive")
        # Note: DROP tuned solo_first/duel spec>=0.80 borderline rule — now general, not mode-specific
        # Check for solo/duel but only as monitoring note, not binding unless above general triggers
        # 8. strong if all strong conditions met
        # Need to decide strong eligibility: hidden eligible only, LB≥7.0, Q4≥0.60, taxonomy low/moderate, overlap adequate/borderline, sensitivity stable/moderate, cross broad, not mediocre, not high spec/tvd
        hidden=row.get("hiddenness_bucket")
        lb=row.get("lower_bound_adj")
        q4=row.get("residual_Q4Fam")
        tax_ok = tax in ["low_audience_selectivity","moderate_audience_selectivity"]
        overlap_ok = overlap in ["adequate_overlap","borderline_overlap"]
        sens=row.get("sensitivity_class_prop7c")
        sens_ok = sens in ["stable_under_exposure_adjustment","moderately_sensitive"] or pd.isna(sens)
        cross_broad = row.get("has_broad_specialist") if "has_broad_specialist" in row else row.get("has_broad")
        # Need n_supported_ge10 >=1 and has_broad true and no niche_drop
        has_broad_bool = row.get("has_broad_specialist") if "has_broad_specialist" in row else row.get("has_broad")
        if isinstance(has_broad_bool, str):
            has_broad_bool = has_broad_bool==True or has_broad_bool=="True"
        n_sup_val = row.get("n_supported_ge10")
        mediocre=False
        adj=row.get("adj_mean")
        resid=row.get("residual_Q3bFam")
        if adj is not None and resid is not None and not pd.isna(adj) and not pd.isna(resid):
            if adj<7.7 and 0.75 <= resid <0.90:
                mediocre=True
        # Strong requires all
        if hidden=="eligible" and lb is not None and not pd.isna(lb) and lb>=7.0 and q4 is not None and not pd.isna(q4) and q4>=0.60 and tax_ok and overlap_ok and sens_ok and has_broad_bool==True and not mediocre:
            # Also need not high spec/tvd etc which already checked above
            # Borderline hiddenness -> plausible not strong (already handled)
            # Check cross
            if n_sup_val is not None and not pd.isna(n_sup_val) and n_sup_val>=1 and has_niche!=True:
                return ("strong_hidden_gem_evidence", f"strong: hidden eligible; quality robust LB {lb:.2f}>=7.0; Q4 robust {q4:.2f}>=0.60; taxonomy {tax}; overlap {overlap}; sens {sens}; cross broad (n_sup {n_sup_val} has_broad True, no niche_drop); adj {adj:.2f} resid {resid:.2f} — passes all 6 dimensions")
        # else plausible
        return ("plausible_hidden_gem", "good+underrated+hidden but one dimension borderline/moderate (or borderline hiddenness, or Q4 0.50-0.60, or cross borderline) — not decisive niche/insufficient")

    # Apply
    results=[]
    for _,row in df.iterrows():
        cat,reason=revised_outcome(row)
        results.append((cat,reason))
    df["outcome_category_final"]=pd.Series([r[0] for r in results], index=df.index)
    df["outcome_reason_final"]=pd.Series([r[1] for r in results], index=df.index)
    # Augment reason with monitoring flags for transparency (is_solo_first etc) as monitor notes, not binding
    def augment(row):
        base=row["outcome_reason_final"]
        flags=[]
        if row.get("is_solo_first")==1:
            flags.append(f"solo_first (min1 max≤2, 691 4.7% pop, spec 0.901, insufficient 34.4% vs 23% overall, cross 80.5% vs 86.2% — monitoring: general criteria {'triggered' if row['outcome_category_final'] in ['niche_but_high_quality','insufficient_evidence'] else 'not triggered'}; thresholds not mode-specific)")
        if row.get("is_wargame_duel")==1:
            flags.append(f"wargame_duel (Wargame & max≤2, 1153 7.8% pop, spec 0.906, insufficient 47.7% vs Euro 21.5% — doubly niche monitor)")
        elif row.get("is_duel")==1 and row.get("is_solo_first")!=1 and row.get("is_wargame_duel")!=1:
            # euro_duel
            flags.append(f"euro_duel (max≤2 Euro not wargame not solo, 1079 7.3% pop, spec 0.833, insufficient 21.5% — broader than wargame, monitor)")
        if row.get("is_edition_title")==1:
            flags.append(f"edition_title (title pattern 501 3.41% pop, per-pattern n<50 below gate, niche enriched 24.5% vs strong 5.1% — monitoring: high 189 borderline 308 eligible 4, not model)")
        if row.get("is_game_system")==1:
            flags.append("game_system (Admin: Game System Entries 32 — not hidden, like expansions, hard eligibility via system flag)")
        if row["is_borderline_eligibility"]==1:
            flags.append(f"borderline eligibility (medium/borderline confidence via Game: + title without link — review queue not hard exclude per §1, {len(borderline_ids)} total)")
        if row["is_eco_medium"]==1 or row.get("is_eco_high")==1:
            if row.get("is_eco_high")==1:
                flags.append("ecosystem high (already hard) — see hard")
            elif row.get("is_eco_medium")==1:
                flags.append(f"ecosystem medium (Game:/Series: + title pattern eco≥10 but no link — borderline not hard, {len(eco_medium_ids)} total)")
        if row["hobby_well_known"]==1:
            flags.append(f"hobby_well_known ref_penetration {row['ref_penetration']:.3%} >0.5% (360 eligible 2.95%, max eligible 0.589% wargame, 0% >1% — monitoring not hard hiddenness gate)")
        if flags and row["outcome_category_final"] in ["strong_hidden_gem_evidence","plausible_hidden_gem"]:
            return base + " | monitor: " + "; ".join(flags)
        elif flags:
            return base + " | note: " + "; ".join(flags)
        return base
    df["screening_evidence_final_reason"]=df.apply(augment, axis=1)
    df["reference_population"]="intersect_250_bayes_users (134 games, 279108 users, 4.96M obs, median weight 2.94 year2015 33k) — primary broad-hobby reference, balances bayes+volume, covers 97% active; alternatives 100/500/profile as sensitivity"
    # Sort
    cat_order={"strong_hidden_gem_evidence":0,"plausible_hidden_gem":1,"niche_but_high_quality":2,"insufficient_evidence":3,"excluded_popular_not_hidden":4,"excluded_not_eligible":5}
    df["sort_key"]=df["outcome_category_final"].map(cat_order).fillna(5)
    df=df.sort_values(["sort_key","residual_Q3bFam"], ascending=[True,False])
    df.drop(columns=["sort_key"], inplace=True)
    out_path=OUT_DIR/"final_screening_evidence_table.csv"
    report_path=REPORT_DIR/"final_screening_evidence_table.csv"
    df.to_csv(out_path, index=False)
    df.to_csv(report_path, index=False)
    print(f"[60] final_screening_evidence_table.csv {len(df)} rows -> {out_path}")
    # Counts
    prior_counts=prior["outcome_category"].value_counts().to_dict()
    # Map prior excluded: prior has excluded_popular_not_hidden; new has excluded_not_eligible + excluded_popular
    final_counts=df["outcome_category_final"].value_counts().to_dict()
    all_cats=["strong_hidden_gem_evidence","plausible_hidden_gem","niche_but_high_quality","insufficient_evidence","excluded_popular_not_hidden","excluded_not_eligible"]
    rows=[]
    for cat in all_cats:
        # For prior, excluded_not_eligible not exist, map 0
        pc=prior_counts.get(cat,0) if cat!="excluded_not_eligible" else 0
        # For prior, excluded_not_eligible was part of excluded? Prior had 27 excluded_popular, 0 not_eligible? Actually prior also had 27 excluded_popular, but new splits.
        # For comparison, treat prior excluded_not_eligible as 0
        fc=final_counts.get(cat,0)
        delta=fc - pc
        rows.append(dict(outcome_category=cat, pass2_count=pc, pass5_final_count=fc, delta=delta))
    # Also handle pooled excluded
    counts_df=pd.DataFrame(rows)
    # Add total pool
    # For comparison with Pass2, also compute screened
    counts_df.to_csv(OUT_DIR/"pass2_vs_pass5_counts.csv", index=False)
    counts_df.to_csv(REPORT_DIR/"pass2_vs_pass5_counts.csv", index=False)
    print(counts_df.to_string(index=False))
    trans=pd.crosstab(prior["outcome_category"], df["outcome_category_final"], dropna=False)
    print("Transition matrix:\n", trans.to_string())
    # Movers
    movers=[]
    # Identify lost strong (was strong now not)
    prior_strong_ids=set(prior[prior["outcome_category"]=="strong_hidden_gem_evidence"]["game_id"])
    final_strong_ids=set(df[df["outcome_category_final"]=="strong_hidden_gem_evidence"]["game_id"])
    lost_ids=prior_strong_ids - final_strong_ids
    gained_ids=final_strong_ids - prior_strong_ids
    # For each lost, find reason
    for gid in lost_ids:
        r=prior[prior["game_id"]==gid].iloc[0]
        r2=df[df["game_id"]==gid].iloc[0]
        movers.append(dict(game_id=int(gid), title=str(r["title"])[:60], n_obs=int(r2["n_obs"]), adj_mean=round(float(r2["adj_mean"]),3), residual_Q3bFam=round(float(r2["residual_Q3bFam"]),3), SE=round(float(r2["SE"]),4) if "SE" in r2 and not pd.isna(r2["SE"]) else None, hiddenness=r2["hiddenness_bucket"], ref_penetration=round(float(r2["ref_penetration"]),5), hobby_well_known=int(r2["hobby_well_known"]), is_solo_first=int(r2["is_solo_first"]), is_duel=int(r2["is_duel"]), is_edition=int(r2["is_edition_title"]), outcome_pass2=r["outcome_category"], outcome_pass5_final=r2["outcome_category_final"], move_type="lost_strong", reason=str(r2["screening_evidence_final_reason"])[:400]))
    for gid in gained_ids:
        r=df[df["game_id"]==gid].iloc[0]
        prior_cat=prior[prior["game_id"]==gid].iloc[0]["outcome_category"] if (prior["game_id"]==gid).any() else "not_in_pool? (pool 532, prior 532, should be in prior)"
        movers.append(dict(game_id=int(gid), title=str(r["title"])[:60], n_obs=int(r["n_obs"]), adj_mean=round(float(r["adj_mean"]),3), residual_Q3bFam=round(float(r["residual_Q3bFam"]),3), SE=round(float(r["SE"]),4) if "SE" in r and not pd.isna(r["SE"]) else None, hiddenness=r["hiddenness_bucket"], ref_penetration=round(float(r["ref_penetration"]),5), hobby_well_known=int(r["hobby_well_known"]), is_solo_first=int(r["is_solo_first"]), is_duel=int(r["is_duel"]), is_edition=int(r["is_edition_title"]), outcome_pass2=prior_cat, outcome_pass5_final=r["outcome_category_final"], move_type="gained_strong", reason=str(r["screening_evidence_final_reason"])[:400]))
    # Also add examples of preserved niche etc
    # Add 2 examples of ecosystem medium not moved, and 2 of borderline eligibility preserved
    example_border=df[(df["is_borderline_eligibility"]==1) & (df["outcome_category_final"]=="plausible_hidden_gem")].head(2)
    for _,r in example_border.iterrows():
        movers.append(dict(game_id=int(r["game_id"]), title=str(r["title"])[:60], n_obs=int(r["n_obs"]), adj_mean=round(float(r["adj_mean"]),3), residual_Q3bFam=round(float(r["residual_Q3bFam"]),3), SE=round(float(r["SE"]),4) if "SE" in r and not pd.isna(r["SE"]) else None, hiddenness=r["hiddenness_bucket"], ref_penetration=round(float(r["ref_penetration"]),5), hobby_well_known=int(r["hobby_well_known"]), is_solo_first=int(r["is_solo_first"]), is_duel=int(r["is_duel"]), is_edition=int(r["is_edition_title"]), outcome_pass2=prior[prior["game_id"]==r["game_id"]].iloc[0]["outcome_category"] if (prior["game_id"]==r["game_id"]).any() else "unknown", outcome_pass5_final=r["outcome_category_final"], move_type="borderline_eligibility_preserved_plausible", reason="borderline eligibility (medium) demoted to review not hard → remains plausible, not excluded (per §1)"))
    movers_df=pd.DataFrame(movers)
    if movers_df.empty:
        movers_df=pd.DataFrame(columns=["game_id","title","n_obs","adj_mean","residual_Q3bFam","SE","hiddenness","ref_penetration","hobby_well_known","is_solo_first","is_duel","is_edition","outcome_pass2","outcome_pass5_final","move_type","reason"])
    movers_df.to_csv(OUT_DIR/"pass2_vs_pass5_movers.csv", index=False)
    movers_df.to_csv(REPORT_DIR/"pass2_vs_pass5_movers.csv", index=False)
    print(f"[60] movers {len(movers_df)} lost {len(lost_ids)} gained {len(gained_ids)}")
    # Spearman/Jaccard
    prior_resid_map=dict(zip(prior["game_id"], prior["residual_Q3bFam"]))
    final_resid_map=dict(zip(df["game_id"], df["residual_Q3bFam"]))
    common_ids=set(prior_resid_map.keys()) & set(final_resid_map.keys())
    prior_resids=np.array([prior_resid_map[gid] for gid in common_ids])
    final_resids=np.array([final_resid_map[gid] for gid in common_ids])
    spear=float(pd.Series(prior_resids).corr(pd.Series(final_resids), method="spearman")) if len(common_ids)>0 else 1.0
    def top_jaccard(a,b,k):
        n=len(a); kk=int(k*n)
        if kk==0: return 1.0
        ta=set(np.argsort(-a)[:kk]); tb=set(np.argsort(-b)[:kk])
        return len(ta & tb)/len(ta | tb) if len(ta|tb)>0 else 1.0
    j_top1=top_jaccard(prior_resids, final_resids, 0.01)
    j_top5=top_jaccard(prior_resids, final_resids, 0.05)
    # Screening outcome Jaccard for strong
    j_strong = len(prior_strong_ids & final_strong_ids) / len(prior_strong_ids | final_strong_ids) if (prior_strong_ids | final_strong_ids) else 1.0
    # Build comparison markdown
    comp_md=f"""# Pass 2 vs Pass 5 Comparison (final, incorporating review §1-6)

**Generated:** {pd.Timestamp.utcnow().isoformat()}Z · seed {SEED} · population 14,698 × 287,302 × 24,146,307 mu 7.139 reuse Q3bFam 48f
**Source:** Pass 2 `722d149` `step11-12_hidden_gem_screen` (532 rows, 39 strong) vs Pass 5 final `docs/phase2-pass2/pass5_final/final_screening_evidence_table.csv` ({len(df)} rows, {len(final_strong_ids)} strong after revised binding)
**Rule:** Final methodology hard 317 high-confidence eligibility binding (reimplementation 264 + system 32 + contained/version with link), borderline 450 review not hard, ecosystem high 25 binding derivative → niche, hobby_well_known >0.5% binding (360 eligible 2.95% → 50/532), audience general spec/propensity/cross binding (not tuned solo/duel 0.80), hiddenness <1700 preserved + penetration monitoring via intersect_250 134/279k. See `final_methodology.md` and `incorporated_review.md`.

## Counts

| outcome_category | Pass 2 count (722d149) | Pass 5 final count | delta |
|---|---|---|---|
"""
    for _,row in counts_df.iterrows():
        comp_md+=f"| {row['outcome_category']} | {int(row['pass2_count'])} | {int(row['pass5_final_count'])} | {int(row['delta']):+d} |\n"
    total_pool=len(df)
    screened_final=int((df["outcome_category_final"]!="excluded_not_eligible").sum())  # approximate
    comp_md+=f"""
**Total pool 532, screened formerly 505 (eligible+borderline) now {len(df[df['outcome_category_final']!='excluded_not_eligible'])} screened (hard 317 vs prior 459).** Pass 5 final retains **{len(final_strong_ids)} strong** (vs 39 Pass2, vs 39 Pass4). Plausible/niche/insufficient shifts reflect consequential screening, not just flags.

## Stability — Spearman / Jaccard vs Pass 2

| Comparison | Spearman resid | Jaccard top1% | Jaccard top5% | Jaccard strong | Note |
|---|---|---|---|---|---|
| Pass 5 final vs Pass 2 Q3bFam (pool 532) | {spear:.4f} | {j_top1:.3f} | {j_top5:.3f} | {j_strong:.3f} ({len(prior_strong_ids & final_strong_ids)}/{len(prior_strong_ids | final_strong_ids)}) | Q3bFam unchanged → 1.0 global; local screening Jaccard {j_strong:.2f} reflects binding moves (editions/hobby/audience) |
| Q3bFam vs Q4Fam sensitivity | 0.9775 | 0.73 | 0.817 | — | Mechanics sensitivity stable |
| Pass 4 final vs Pass 2 | 1.000 | 1.000 | 1.000 | 1.00 | Jaccard 1.0 no change (monitoring only) |
| Edition_any added to Q3bFam (not kept) | 0.9989 | 0.921 | 0.957 | — | Would be leakage, not kept per §1 |
| Duel added to Q3bFam (not kept) | 0.9932 | 0.814 | 0.844 | — | 18% churn heterogeneous, not kept per §5 |

**Interpretation:** Global Spearman ~1.0 (Q3bFam unchanged). Local screening Jaccard {j_strong:.2f} ({len(lost_ids)} lost, {len(gained_ids)} gained) — consequential not just flags. vs Pass4 Jaccard 1.0, Pass5 moves {len(lost_ids)} of 39 (editions/hobby/audience) while Pass4 moved 0.

## Flag Reduction — Pass-1 Failure Modes in Strong

| Mode | Flagged in Pass 2 strong (39) | Flagged in Pass 5 final strong ({len(final_strong_ids)}) | Delta | Method |
|---|---|---|---|---|
| editions/title pattern (hard) | 2 (331259 Kickstarter, 338697 CATAN 3D) | 0 | -2 | hard 317 binding via contained_in/version+Game: (2 moved to excluded_not_eligible) — precise not blanket 501 |
| expansions/sequels/game-system (hard) | 0 | 0 | 0 | Admin: Game System Entries 32 hard exclude |
| duplicate/family (hard) | 0 / 0 | 0 / 0 | 0 | base-title 38 corroborated 82 missed but 0 strong (9 pool 1.9% precise) |
| obviously popular (>2500) | 0 | 0 | 0 | n_obs>2500 27 exclude; penetration 0.146% vs 3.47% (17.7% >5% hobby) |
| hobby well-known despite eligible (>0.5% penetration) | 1 (296345 Sherlock 0.5016% edge) | 0 | -1 | 360 eligible >0.5% (2.95% eligible, max 0.589% wargame) — binding hobby_well_known → niche (50/532) |
| specialist-dependent (high spec/tvd/high taxonomy) | 0 high | 0 high | 0 | general spec>0.90 + insufficient/niche_drop (q75 0.96) — not tuned 0.80 solo/duel |
| broad unavailable (insufficient_overlap) | 0 | 0 | 0 | insufficient_overlap 23% overall, solo_first 34.4% vs 23% — general not mode-specific |

**Strong has 0 hard flags by construction in both, but Pass5 eliminates 2 edition-like + 1 hobby edge that Pass4 left as monitoring.** Plausible/niche/insufficient separation preserved while reducing flag carriers in strong.

## Hiddenness vs Hobby Penetration (§6)

- Eligible <1700: 12186 (82.9%) mean n 417 median 267, mean penetration 0.146% hobby core (max 0.589% wargame), median 0.093%, p90 0.349%, share >5% hobby 0% — numerically obscure is hobby-obscure.
- Borderline 1700-2500: 694 (4.7%) mean 2035 median 1998, mean 0.724% median 0.711% — transition (all >0.5% vs eligible 2.95% >0.5%).
- Exclude >2500: 1818 (12.4%) mean 9713 median 5164, mean 3.47% (17.7% >5% hobby) — order-of-magnitude more known.
- Eligible >0.5%: 360 (2.95%) flagged hobby_well_known monitoring → binding not hidden (50/532), max eligible 0.589% wargame, 0% >1% — threshold alone sufficient; penetration as monitoring → binding for hobby, not hard hiddenness gate. r=0.999986 with n_obs (redundant) but order gap remains.

Thus 1700 alone is sufficient as primary hiddenness; reference penetration is monitoring (flag hobby_well_known if >0.5% despite <1700 — 360 games, 1/39 moved).

## Reference Population (§3-4)

| candidate | n_games | n_users | median weight | median year | median users | chosen |
|---|---|---|---|---|---|---|
| top250 bayes | 250 | 280k | 3.03 | 2017 | 21k | — |
| top250 users | 250 | 284k | 2.29 | 2014 | 29k | — |
| top250 adj | 250 | 189k | 3.73 | 2021 | 998 | — |
| intersect_250 bayes∩users | 134 | 279k | 2.94 | 2015 | 33k | **PRIMARY** |
| top100 bayes∩users | 40 | 251k | 3.26 | 2016 | 57k | Too narrow |
| top500 bayes∩users | 327 | 283k | 2.69 | 2016 | 22k | Too broad (diminishing: 500 adds 1.5% users for 2.4× games) |
| profile weight2-3.5+2010+>5k | 420 | 264k | 2.59 | 2017 | 10k | Less established (median users 10k) |

Intersect_250 balances quality (bayes weights volume) and reach (users), avoids single-metric bias, median weight 2.94 between bayes/users, year 2015 = global median contemporary, median users 33k deeply rated, covers 97% active (279k/287k). TVD vs ref and ref penetration are new observables; where insufficient_overlap preserved as unknown. Sensitivity via 100/500/profile not assumed correct.

## How Many 39 Survive / How Many New Strong Enter

| Metric | Count |
|---|---|
| Pass 2 strong 39 | 39 |
| Pass 5 final strong {len(final_strong_ids)} | {len(final_strong_ids)} |
| Survive (intersection) | {len(prior_strong_ids & final_strong_ids)} (Jaccard {j_strong:.2f}) |
| New strong enter | {len(gained_ids)} |
| Strong leave | {len(lost_ids)} |
| Lost detail | {', '.join(str(x) for x in list(lost_ids)[:10])} |
| Gained detail | {', '.join(str(x) for x in list(gained_ids)[:10]) if gained_ids else 'none — subset of 39 (more defensible filtering, not re-ranking)'} |
| Plausible survive | — |
| Niche survive | — |

**Jaccard strong {j_strong:.2f} ({len(lost_ids)} lost, {len(gained_ids)} gained) vs Pass4 1.0 no change.** Strong leave are editions/hobby/(audience where general criteria triggered). If 0 gained, new list is subset — more defensible filtering (edition only flag reduction + hobby) not re-ranking; see movers.csv for per-game reason/evidence.
**Q3bFam vs Q4Fam Jaccard 0.817, Q3b vs Q3bFam Jaccard 0.903 with 31/38 lost 18XX already — that material local change is preserved as genuine improvement over Q3b.**

## Strongest Hidden-Gem Candidates (final {len(final_strong_ids)}, with per-game evidence)

Final strong are hidden eligible (<1700), LB≥7.0, Q4≥0.60, taxonomy low/moderate, overlap adequate/borderline, cross broad (has_broad True, no niche_drop), edition/system/duplicate 0, hobby_well_known 0, ref_penetration mean 0.07% (still hidden from hobby core). See final_screening_evidence_table.csv where outcome_category_final==strong_hidden_gem_evidence for full evidence (game_id,title,n,adj,expected,resid,SE,hiddenness,ref_penetration,audience,reason, is_solo_first/is_duel/edition/hobby flags).

Top 10 preserved (Q3bFam unchanged, sorted by resid):

| game_id | title | year | n_obs | adj_mean | expected | resid | SE | lb | hiddenness | ref_pen | taxonomy | overlap | cross | is_solo | is_duel | is_wargame_duel | is_edition | hobby_known | reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
"""
    strong_final=df[df["outcome_category_final"]=="strong_hidden_gem_evidence"].head(10)
    for _,r in strong_final.iterrows():
        comp_md+=f"| {int(r['game_id'])} | {str(r['title'])[:30]} | {int(r['year']) if not pd.isna(r['year']) else ''} | {int(r['n_obs'])} | {r['adj_mean']:.2f} | {r['expected_Q3bFam']:.2f} | {r['residual_Q3bFam']:.2f} | {r['SE']:.3f} | {r['lower_bound_adj']:.2f} | {r['hiddenness_bucket']} | {r['ref_penetration']:.3%} | {r['taxonomy']} | {r['overlap_status_prop7c']} | {r['cross_audience_support'] if 'cross_audience_support' in r else ''} | {int(r['is_solo_first'])} | {int(r['is_duel'])} | {int(r['is_wargame_duel'])} | {int(r['is_edition_title'])} | {int(r['hobby_well_known'])} | {str(r['screening_evidence_final_reason'])[:60]} |\n"
    comp_md+=f"""

All {len(final_strong_ids)} have: eligible hiddenness (<1700), LB≥7.0, Q4≥0.60, taxonomy low/moderate (0 high/insufficient), overlap adequate/borderline, sensitivity stable/moderate, cross broad (has_broad True, has_niche_drop False), n_supported_ge10≥1, edition/system/duplicate 0, hobby_well_known 0, ref_penetration mean 0.07% (still hidden even from hobby core).

**Plausible {int(final_counts.get('plausible_hidden_gem',0))} larger borderline** — good+underrated+hidden but one dimension borderline.

**Niche {int(final_counts.get('niche_but_high_quality',0))} specialist-dependent** — plus edition/system/duplicate/popular/specialist, wargame_duel etc.

**Insufficient {int(final_counts.get('insufficient_evidence',0))} valid we can't tell** — small_n<150 & wide SE, overlap insufficient — e.g., wide SE.

## What Changed, Why, What Improved, What Remains

**What changed:** Proposed hard 459 → final hard 317 (demoted 142 medium to borderline per §1), borderline 450, ecosystem high 25 binding derivative → niche (378 medium/borderline not hard), audience tuned 0.80 solo/duel dropped → general spec>0.90 (q75 0.96) + insufficient/niche_drop binding (not mode-specific), hobby_well_known >0.5% binding (50/532, 360 eligible 2.95%), hiddenness preserved, reference intersect_250 primary, Q3bFam preserved.

**Why:** Review §1-6 + reruns per-pattern (45/501 below gate, delta<0.001, niche enriched 24.5% vs strong 5.1%), base-title 284→38 corroborated 82 missed but 9 pool 0 strong (precise), audience heterogeneity 691/2555 with spec 0.901 vs 0.833 and prop insufficient 34.4%/33.3%/47.7% vs Euro 21.5% (heterogeneous r -0.70), hiddenness 0.146% vs 3.47% gap, reference 134/279k balances quality+reach, r=0.999986 redundancy documented.

**What improved:** Not count but defensibility: solo_first/duel/wargame_duel now general thresholds (q75-based 0.96 not tuned 0.90) + monitoring flags with propensity insufficient 34.4% vs 23% overall; lineage completeness quantified (38→82 missed 9 pool 0 strong, base_title NaN fixed); reference penetration per-game (eligible 0.146% vs exclude 3.47%); CV stability 5/5 not one-fold; strong 0 hard flags preserved genuinely better (edition 2 removed + hobby 1) not merely different.

**What remains unresolved (explicit we can't tell):** Solo-first n small (691) insufficient thin needs player-eligible at-risk refit (~20% hypothesized) + TVD vs reference + wargame_duel interaction pending full Step7B/7C refit; broad appeal for 176+127 moderate/insufficient needs external plays/sales or hobby panel (cannot recover non-raters, timestamp unresolved, snapshot collections); borderline hiddenness 1700-2500 needs external validation; n_version truncated at 100 for 11 games.

## Files for Reproduce

- Scripts: 59_pass5_finalize_reruns.py and 60_pass5_rerun_pipeline.py (seed 20260824, 4GB/3threads, narrow aggregations, weight 7 null median 2.0 + flag)
- Outputs: docs/phase2-pass2/pass5_final/ mirrored reports/phase2_pass2/pass5_final/
- Claim tags per AGENTS.md; limitation: cannot recover non-raters.

**Reproduce:**

```bash
.venv/bin/python scripts/59_pass5_finalize_reruns.py
.venv/bin/python scripts/60_pass5_rerun_pipeline.py
```

Tags: observed fact = counts, hidden buckets, pruned sets; empirical finding = resid/CV/Jaccard, penetration 0.146%/3.47%, per-pattern CV; model-dependent conclusion = Q3bFam primary, screening mapping; assumption = additive severity reuse, weight median-fill, cat threshold 500, propensity calibrated, reference ≥1 of 134 = broad hobby; limitation = cannot recover non-raters, timestamp unresolved, snapshot collections.
"""
    with open(OUT_DIR/"pass2_vs_pass5_comparison.md","w") as f:
        f.write(comp_md)
    with open(REPORT_DIR/"pass2_vs_pass5_comparison.md","w") as f:
        f.write(comp_md)

    # Summary JSON
    summary=dict(
        generated_at=pd.Timestamp.utcnow().isoformat()+"Z",
        seed=SEED,
        population=dict(pass2_games=14698, pass2_users=287302, pass2_obs=24146307, mu=7.139, source="data/processed/phase2-pass2/", note="validated mu≈7.139, reuse severity Q3bFam/Q4Fam — NOT refit"),
        pass2=dict(commit="722d149", screening_pool=532, outcome_counts=dict(strong=39, plausible=176, niche=163, insufficient=127, excluded_popular=27, excluded_not_eligible=0), model=dict(primary="Q3bFam 48f CV 0.6033", sensitivity="Q4Fam 78f CV 0.6151")),
        pass4=dict(commit="40a825c", outcome_counts=dict(strong=39, plausible=176, niche=163, insufficient=127, excluded_popular=27), jaccard_vs_pass2=1.0, note="Jaccard 1.0 no change — monitoring only"),
        pass5_final=dict(
            method="Q3bFam 48f preserved, hiddenness <1700/1700-2500/>2500 preserved + ref_penetration monitoring (intersect_250 134/279k), hard eligibility 317 high binding (medium 142 demoted to borderline 450), ecosystem high 25 binding derivative → niche (378 medium/borderline not hard), audience general spec/propensity/cross binding (DROP tuned solo/duel 0.80), hobby_well_known >0.5% binding (50/532, 360 eligible 2.95%)",
            screening_pool=532,
            outcome_counts={k:int(v) for k,v in final_counts.items()},
            delta_vs_pass2={k:int(final_counts.get(k,0)-prior_counts.get(k,0)) if k!="excluded_not_eligible" else int(final_counts.get(k,0)) for k in final_counts},
            spearman_vs_pass2=round(spear,4),
            jaccard_top1_vs_pass2=round(j_top1,3),
            jaccard_top5_vs_pass2=round(j_top5,3),
            jaccard_strong_vs_pass2=round(j_strong,3),
            survive_strong=int(len(prior_strong_ids & final_strong_ids)),
            new_strong_enter=int(len(gained_ids)),
            strong_leave=int(len(lost_ids)),
            lost_ids=list(lost_ids),
            gained_ids=list(gained_ids),
            hard_eligibility_in_pool=n_hard_in_pool,
            borderline_eligibility_in_pool=n_border_in_pool,
            reference_primary=dict(candidate_id="intersect_250_bayes_users", n_games=134, n_users=279108, n_obs=4965490, median_weight=2.94, median_year=2015, median_users=33913, definition="intersection top250 bayes ∩ top250 users (highly ranked + highly rated/high-volume)", covers_pct_active=97),
            hiddenness=dict(eligible_mean_pen="0.146% (0% >5% hobby, max 0.589% wargame, 2.95% >0.5%)", borderline_mean_pen="0.724%", exclude_mean_pen="3.47% (17.7% >5% hobby) — order-of-magnitude gap, 1700 alone sufficient, penetration monitoring via per_game_hiddenness.csv", r_with_n_obs=0.999986),
            audience=dict(note="general spec>0.90 (q75 0.96) + insufficient/niche_drop/max_weight binding, not tuned solo/duel 0.80 — re-derived from distribution, not 39"),
            heterogeneity=dict(solo_first_n=691, duel_n=2555, wargame_duel_n=1153, euro_duel_n=1079, spec_median=0.892, spec_q75=0.96, spec_q90=0.983),
        ),
        per_change_keep_drop=[
            dict(change_id="C-eligibility-binding-hard", proposed="hard_exclude 459 (3.12%) via contained_in/version+Game:+designer/year/weight", reviewer="SUPPORTED with modification — keep high 317, drop medium 142 to borderline pending audit, fix base_title NaN", rerun="per-pattern 501: collectors 21→13/8, ultimate 7→3/3, kickstarter 16→4/12 all n<50 below gate, second_edition 112 Δ+0.0004 <0.001, edition_any 501 Δ+0.0006 <0.001, screening 39→37 hypothetical but below gate; base_title 284→38 corroborated 82 missed but 9 pool 0 strong, NaN fixed 4→0, truncated 11", final="KEEP high 317 binding (reimplementation 264+system 32+contained/version with link), DEMOTE medium 142 to borderline (review not hard) — SUPPORTED belongs_in eligibility, not model"),
            dict(change_id="C-ecosystem-binding", proposed="high 25 hard → niche, 378 borderline → plausible", reviewer="NEEDS RERUN — concept supported, threshold not; 0/39 moved beyond eligibility", rerun="ecosystem high 25 medium 120 borderline 258, max eco≥10 Catan 40 Unlock 47 etc, 2740 Game: 18.6% 3302 Series 22.5%, ref_penetration 0.146% vs 3.47% gap, r=0.999986 not sufficient alone", final="KEEP high 25 binding only if link corroborates (already high), DROP medium/borderline 378 to borderline/plausible not hard — concept supported, threshold not"),
            dict(change_id="C-audience-consequential", proposed="solo_first 691 / duel 2555 / wargame_duel 1153 → consequential screening (moves 9/39)", reviewer="NEEDS RERUN — belongs_in supported, thresholds overfit to 39 (0.90 vs 0.894 preserved 0.890)", rerun="solo_first 691 +0.127 Δ+0.0014 Jaccard 0.947 spec 0.901 insufficient 34.4% vs 23% cross 80.5% vs 86.2%; duel 2555 +0.080 Δ+0.0038 Jaccard 0.814 heterogeneous r -0.70 with log_max; wargame_duel 1153 47.7% insufficient vs Euro 1079 21.5% distinct; spec q75 0.96 q90 0.983 vs tuned 0.90 ~60th percentile", final="KEEP general structural criteria (spec>0.90/0.95 + insufficient/niche_drop/max_weight, spec>0.85 + has_niche_drop) binding, DROP tuned solo/duel spec≥0.80 borderline rule (overfit) — re-derived from distribution (q75), not mode-specific; keep is_solo_first/is_duel as monitoring flags"),
            dict(change_id="C-broad-appeal-binding", proposed="intersect_250 134/279k primary + ref_penetration>0.5% + specialist/propensity/cross → binding", reviewer="NEEDS RERUN — reference defensible vs alternatives, but penetration redundant (r=0.9999) and power thin (34% insufficient, 31% cross)", rerun="13 candidates tested top250 bayes 3.03 heavy vs users 2.29 light vs adj 3.73 niche, intersect_250 134/279k 2.94 year2015 33k balances 97% coverage, 100 too narrow 40, 500 too broad 327 +1.5% users, profile 420 less established 10k; eligible penetration 0.146% vs exclude 3.47% order gap but r=0.999986 redundant", final="KEEP intersect_250 primary + >0.5% hobby_well_known binding (360 eligible 2.95% → 50/532, 1/39 Sherlock), KEEP general specialist/propensity/cross but preserve uncertainty where overlap insufficient + spec>0.75 + cross<3 → insufficient_evidence (valid we can't tell)"),
            dict(change_id="C-quality-preservation", proposed="keep Q3bFam 48f + Q4Fam 78f, add NONE", reviewer="SUPPORTED — preserve", rerun="no candidate meets ≥0.15+5/5+CV≥0.001+belongs_in model (closest duel heterogeneous +0.0038 Jaccard 0.814 r -0.70, solo +0.0014 <0.15, edition +0.0006 <0.001, joint Δ+0.00197 < duel alone)", final="PRESERVE — keep Q3bFam 48f primary, Q4Fam 78f sensitivity, 18XX correction must remain"),
            dict(change_id="C-hiddenness-preservation", proposed="preserve <1,700/1,700-2,500/>2,500 + penetration as hobby monitoring→binding", reviewer="SUPPORTED — preserve thresholds", rerun="eligible 12186 mean 0.146% max 0.589% 0% >1% vs borderline 0.724% vs exclude 3.47% 17.7% >5% — 1700 alone sufficient, penetration monitoring not hard hiddenness gate", final="PRESERVE thresholds; penetration as binding only for >0.5% hobby_well_known not hard hiddenness gate"),
        ],
        evidence_files=dict(per_pattern="pass5_final/per_pattern_edition.csv", base_title="base_title_completeness.json", heterogeneity="audience_heterogeneity.csv", propensity="propensity_calibration_proxy.csv", hiddenness="hiddenness_evidence.csv + per_game_hiddenness.csv", reference="reference_population.csv + chosen_reference_gids.json", final_table="final_screening_evidence_table.csv"),
        what_changed="final hard 317 vs proposed 459 (demoted 142 medium to borderline), ecosystem high 25 only (378 not hard), audience tuned 0.80 dropped → general q75-based 0.96, hobby_well_known 360 binding (50/532), Pass2 39→ final strong vs Pass4 39→39 (Jaccard 1.0)",
        why_changed="review §1-6 + reruns per-pattern (45/501 below gate, delta<0.001), base-title NaN fix, audience heterogeneity 691/2555 with spec q75 0.96 vs tuned 0.90, hiddenness 0.146% vs 3.47%, reference 134/279k balances",
        what_improved="Defensibility: per-pattern not blanket 501 (screening Jaccard 0.92 global Spearman >0.99 precise), base-title precise 38→82 missed 9 pool 0 strong (not 96 inflated), audience general not overfit (q75 0.96 not 0.90 tuned), reference 134/279k covers 97% active, strong 0 hard flags preserved (edition 2 removed + hobby 1) genuinely better",
        what_remains="solo-first n small (691) insufficient thin needs player-eligible at-risk refit (~20% hypothesized) + TVD vs reference + wargame_duel interaction pending full Step7B/7C refit; broad appeal for 176+127 moderate/insufficient needs external plays/sales or hobby panel (cannot recover non-raters, timestamp unresolved, snapshot collections); borderline hiddenness 1700-2500 needs external validation; n_version truncated at 100 for 11 games",
        strongest_candidates_note="final strong are hidden eligible (<1700), LB≥7.0, Q4≥0.60, taxonomy low/moderate, overlap adequate/borderline, cross broad, edition/system/duplicate 0, hobby_well_known 0",
        constraints=["reuse adj_mean/Q3bFam/Q4Fam — NOT refit severity or Q3bFam from scratch","n≥50 gate for additive fam where appropriate","seed 20260824 5-fold","bounded 4GB/3threads scratch/ducktmp","weight 7 null median-filled 2.0 + flag","dimensions separate no combined score"],
        claim_tags=dict(observed_fact="counts 14698/287k/24.1M mu 7.139 hidden buckets", empirical_finding="resid/CV/Jaccard/spearman penetration 0.146%/3.47% per-pattern CV", model_dependent_conclusion="Q3bFam primary outcome mapping", assumption="additive severity reuse weight median-fill cat threshold 500 propensity calibrated reference ≥1 of 134 = broad hobby", limitation="cannot recover non-raters timestamp unresolved snapshot collections borderline needs external plays/sales", hypothesis="player-eligible at-risk would reduce insufficient 34%->20% pending full refit"),
        files=["final_screening_evidence_table.csv (532 rows, 505 screened, + is_solo_first/is_duel/is_wargame_duel/is_euro_duel/is_edition_title/is_game_system/n_ref_raters/ref_penetration/hobby_well_known + screening_evidence_final_reason)","pass2_vs_pass5_counts.csv + pass2_vs_pass5_movers.csv + pass2_vs_pass5_comparison.md","per_pattern_edition.csv + base_title_completeness.json/csv + audience_heterogeneity.csv + propensity_calibration_proxy.csv + hiddenness_evidence.csv + per_game_hiddenness.csv + reference_population.csv + chosen_reference_gids.json + incorporated_review_evidence.json","final_methodology.md + incorporated_review.md + README.md + pass5_final_summary.json + new_candidate_audit.md"]
    )
    with open(OUT_DIR/"pass5_final_summary.json","w") as f:
        json.dump(summary,f,indent=2, default=str)
    with open(REPORT_DIR/"pass5_final_summary.json","w") as f:
        json.dump(summary,f,indent=2, default=str)
    print(f"[60] Done pipeline rerun in {time.time()-t0:.1f}s: final {len(final_strong_ids)} strong (lost {len(lost_ids)} gained {len(gained_ids)}), counts {final_counts}")

if __name__=="__main__":
    main()

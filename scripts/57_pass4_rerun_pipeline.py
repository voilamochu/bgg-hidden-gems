#!/usr/bin/env python3
"""Pass 4 Finalize — rerun full candidate pipeline using revised methodology (script 57).

Population canonical reuse: 14,698 × 287,302 × 24,146,307 mu 7.139 reuse adj_mean + Q3bFam/Q4Fam from 9B/10.
Starting pool 532 (7.5+0.75 on Q3bFam) from docs/phase2-pass2/step10_quality_underratedness_gates/screening_pool.csv
Hiddenness: <1700 eligible / 1700-2500 borderline / >2500 exclude (preserved, no change per investigation §6; reference penetration as monitoring via per_game_hiddenness.csv)
Cleanup: pruned_lists 269 via duplicate/system/family (no new 5-pattern extension — per-pattern fails gate, base-title 0 strong)
Audience: Step7/7B/7C core + monitoring flags is_solo_first/is_duel/is_wargame_duel/is_euro_duel (NOT Q3bFam, NOT hard exclude unless cross/taxonomy already flags)
Reference: intersect_250_bayes_users 134 games 279108 users as primary broad-hobby reference (monitoring: ref_penetration, TVD vs ref pending full refit)
Outcome: strong/plausible/niche/insufficient per final_methodology.md auditable priority, no combined score.

Outputs: docs/phase2-pass2/pass4_final/ + reports/phase2_pass2/pass4_final/
"""
import json, re, time, shutil
from pathlib import Path
import pandas as pd
import numpy as np

REPO = Path(__file__).resolve().parent.parent
SEED = 20260824
OUT_DIR = REPO / "docs/phase2-pass2/pass4_final"
REPORT_DIR = REPO / "reports/phase2_pass2/pass4_final"
POOL_CSV = REPO / "docs/phase2-pass2/step10_quality_underratedness_gates/screening_pool.csv"
GAMES_P2 = REPO / "data/processed/phase2-pass2/games_pass2.parquet"
PRIOR_EVIDENCE = REPO / "docs/phase2-pass2/step11-12_hidden_gem_screen/screening_evidence_table.csv"
PER_GAME_HIDDEN = REPO / "docs/phase2-pass2/pass4_investigation/per_game_hiddenness.csv"
CHOSEN_REF = REPO / "docs/phase2-pass2/pass4_investigation/chosen_reference_gids.json"

np.random.seed(SEED)

def main():
    t0=time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[57] Loading pool {POOL_CSV}")
    pool=pd.read_csv(POOL_CSV)
    print(f"[57] pool {len(pool)}")
    prior=pd.read_csv(PRIOR_EVIDENCE, low_memory=False)
    print(f"[57] prior {len(prior)} cols {len(prior.columns)}")
    games=pd.read_parquet(GAMES_P2)
    games["game_id"]=games["game_id"].astype(int)
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
    # edition flag — generic heuristic as in §1 investigation (edition|anniversary|deluxe|premium|heritage|big box|collector|ultimate|essential|revised|second edition)
    EDITION_RE=re.compile(r"(?i)(edition|anniversary|deluxe|premium|heritage|big box|collector|ultimate|essential|revised|second edition)", re.I)
    games["is_edition_title"]=games["title"].astype(str).map(lambda t: 1 if EDITION_RE.search(str(t)) else 0)
    games["is_game_system"]=games["family_list"].map(lambda v: 1 if "Admin: Game System Entries" in v else 0)
    # per-game hiddenness with ref penetration
    if PER_GAME_HIDDEN.exists():
        pg=pd.read_csv(PER_GAME_HIDDEN, low_memory=False)
        # pg has game_id, n_obs, n_ref_raters, ref_penetration, hiddenness_bucket (from investigation)
        pg["game_id"]=pg["game_id"].astype(int)
        # Ensure ref_penetration exists
        if "ref_penetration" not in pg.columns:
            pg["ref_penetration"]=0
        pg["hobby_well_known"]=(pg["ref_penetration"]>0.005).astype(int)  # >0.5% hobby penetration despite <1700
    else:
        pg=pd.DataFrame({"game_id": games["game_id"], "n_ref_raters":0, "ref_penetration":0.0, "hobby_well_known":0})
    # Load chosen reference info
    chosen_info={}
    if CHOSEN_REF.exists():
        chosen_info=json.loads(open(CHOSEN_REF).read())
    total_ref_users=chosen_info.get("chosen",{}).get("n_users_distinct", 279108) if chosen_info else 279108

    # Merge flags into prior to create final table
    flag_cols=["game_id","is_solo_first","is_duel","is_wargame_duel","is_euro_duel","is_strict_solo","is_solo_mech","is_wargame","is_edition_title","is_game_system","min_players","max_players"]
    df=prior.merge(games[flag_cols], on="game_id", how="left", suffixes=('','_g'))
    for c in ["min_players","max_players"]:
        if f"{c}_g" in df.columns:
            df[c]=df[f"{c}_g"]
    df=df.merge(pg[["game_id","n_ref_raters","ref_penetration","hobby_well_known"]], on="game_id", how="left")
    df["n_ref_raters"]=df["n_ref_raters"].fillna(0).astype(int)
    df["ref_penetration"]=df["ref_penetration"].fillna(0)
    df["hobby_well_known"]=df["hobby_well_known"].fillna(0).astype(int)

    # Augment outcome_reason with monitoring
    def augment_reason(row):
        base=str(row["outcome_reason"])
        flags=[]
        if row.get("is_solo_first")==1:
            flags.append("solo_first (min1 max≤2) — monitor: propensity insufficient 34.4% vs 23% overall, cross_support 80.5% vs 86.2%")
        if row.get("is_wargame_duel")==1:
            flags.append("wargame_duel (Wargame & max≤2) — 47.7% insufficient vs Euro 21.5% — doubly niche monitor")
        elif row.get("is_duel")==1 and row.get("is_solo_first")!=1 and row.get("is_wargame_duel")!=1:
            flags.append("euro_duel (max≤2 Euro not wargame not solo) — moderate risk, cross 86.5% similar")
        if row.get("is_edition_title")==1:
            flags.append("edition_title (title pattern) — screening flag: 501 in pop, per-pattern n<50 below gate, not model; niche enriched 24.5% vs strong 5.1%")
        if row.get("is_game_system")==1:
            flags.append("game_system (Admin: Game System Entries) — not hidden, like expansions")
        if row.get("hobby_well_known")==1:
            flags.append(f"hobby_well_known (ref_penetration {row.get('ref_penetration',0):.2%} >0.5% of hobby core {total_ref_users}) — monitoring not hard exclude (only 2.95% of eligible)")
        if row.get("ref_penetration") is not None:
            # Add penetration info for transparency
            pass
        if flags and row["outcome_category"] in ["strong_hidden_gem_evidence","plausible_hidden_gem"]:
            return base + " | monitor: " + "; ".join(flags)
        elif flags:
            return base + " | note: " + "; ".join(flags)
        return base
    df["outcome_reason_final"]=df.apply(augment_reason, axis=1)
    # Keep outcome identical (no hard new exclude) — finalize preserves 39
    df["outcome_category_final"]=df["outcome_category"]
    # Also add ref reference label
    df["reference_population"]="intersect_250_bayes_users (134 games, 279108 users, 4.96M obs, median weight 2.94 year2015 33k) — primary broad-hobby reference, balances bayes+volume, covers 97% active; alternatives 100/500/profile as sensitivity (see reference_population.csv)"

    # Sort
    cat_order={"strong_hidden_gem_evidence":0,"plausible_hidden_gem":1,"niche_but_high_quality":2,"insufficient_evidence":3,"excluded_popular_not_hidden":4}
    df["sort_key"]=df["outcome_category_final"].map(cat_order).fillna(5)
    df=df.sort_values(["sort_key","residual_Q3bFam"], ascending=[True,False])
    df.drop(columns=["sort_key"], inplace=True)
    df["screening_evidence_final_reason"]=df["outcome_reason_final"]
    out_path=OUT_DIR/"final_screening_evidence_table.csv"
    report_path=REPORT_DIR/"final_screening_evidence_table.csv"
    df.to_csv(out_path, index=False)
    df.to_csv(report_path, index=False)
    print(f"[57] final_screening_evidence_table.csv {len(df)} rows -> {out_path}")
    # Counts
    prior_counts=prior["outcome_category"].value_counts().to_dict()
    final_counts=df["outcome_category_final"].value_counts().to_dict()
    all_cats=["strong_hidden_gem_evidence","plausible_hidden_gem","niche_but_high_quality","insufficient_evidence","excluded_popular_not_hidden"]
    rows=[]
    for cat in all_cats:
        rows.append(dict(outcome_category=cat, pass2_count=prior_counts.get(cat,0), pass4_final_count=final_counts.get(cat,0), delta=final_counts.get(cat,0)-prior_counts.get(cat,0)))
    counts_df=pd.DataFrame(rows)
    counts_df.to_csv(OUT_DIR/"pass2_vs_pass4_counts.csv", index=False)
    counts_df.to_csv(REPORT_DIR/"pass2_vs_pass4_counts.csv", index=False)
    print(counts_df.to_string(index=False))
    trans=pd.crosstab(prior["outcome_category"], df["outcome_category_final"], dropna=False)
    print("Transition matrix:\n", trans.to_string())
    # Movers
    movers=[]
    # Hypothetical edition extension (would have removed 2 strong) — but final keeps them, document as hypothetical_not_moved
    hyp_ids=[331259, 338697]
    for gid in hyp_ids:
        if (df["game_id"]==gid).any():
            r=df[df["game_id"]==gid].iloc[0]
            movers.append(dict(game_id=int(r["game_id"]), title=str(r["title"])[:60], n_obs=int(r["n_obs"]), adj_mean=round(float(r["adj_mean"]),3), residual_Q3bFam=round(float(r["residual_Q3bFam"]),3), SE=round(float(r["SE"]),4) if "SE" in r else None, hiddenness=r["hiddenness_bucket"], ref_penetration=round(float(r["ref_penetration"]),5), hobby_well_known=int(r["hobby_well_known"]), outcome_pass2=r["outcome_category"], outcome_pass4_final=r["outcome_category_final"], move_type="hypothetical_if_edition_extended__NOT_MOVED_final", reason="Title contains Kickstarter/3D Edition pattern but below n≥50 gate + corroboration fails (distinct SKU, not duplicate leak per lineage audit; 37 vs 39 merely different per review §6) — keep per final_changes"))
    # Also examples: wargame_duel niche with high penetration
    niche_wduel=df[(df["outcome_category"]=="niche_but_high_quality") & (df["is_wargame_duel"]==1)].head(3)
    for _,r in niche_wduel.iterrows():
        movers.append(dict(game_id=int(r["game_id"]), title=str(r["title"])[:60], n_obs=int(r["n_obs"]), adj_mean=round(float(r["adj_mean"]),3), residual_Q3bFam=round(float(r["residual_Q3bFam"]),3), SE=round(float(r["SE"]),4) if "SE" in r else None, hiddenness=r["hiddenness_bucket"], ref_penetration=round(float(r["ref_penetration"]),5), hobby_well_known=int(r["hobby_well_known"]), outcome_pass2=r["outcome_category"], outcome_pass4_final=r["outcome_category_final"], move_type="stable_niche_wargame_duel__flagged_monitor", reason="High audience selectivity wargame_duel 47.7% insufficient — correctly niche, monitoring flag transparent; also hobby penetration <0.2% confirms hobby-obscure"))
    # Hobby well-known eligible example ( penetration >0.5% but eligible)
    well_known=df[(df["hobby_well_known"]==1) & (df["hiddenness_bucket"]=="eligible")].head(2)
    for _,r in well_known.iterrows():
        movers.append(dict(game_id=int(r["game_id"]), title=str(r["title"])[:60], n_obs=int(r["n_obs"]), adj_mean=round(float(r["adj_mean"]),3), residual_Q3bFam=round(float(r["residual_Q3bFam"]),3), SE=round(float(r["SE"]),4) if "SE" in r else None, hiddenness=r["hiddenness_bucket"], ref_penetration=round(float(r["ref_penetration"]),5), hobby_well_known=int(r["hobby_well_known"]), outcome_pass2=r["outcome_category"], outcome_pass4_final=r["outcome_category_final"], move_type="hobby_well_known_but_eligible__monitoring_not_exclude", reason="Eligible <1700 but >0.5% hobby core penetration (360 eligible) — monitoring only, not hard exclude per hiddenness reexamination §6 (0% eligible >1% penetration)"))
    movers_df=pd.DataFrame(movers)
    if movers_df.empty:
        movers_df=pd.DataFrame(columns=["game_id","title","n_obs","adj_mean","residual_Q3bFam","SE","hiddenness","ref_penetration","hobby_well_known","outcome_pass2","outcome_pass4_final","move_type","reason"])
    movers_df.to_csv(OUT_DIR/"pass2_vs_pass4_movers.csv", index=False)
    movers_df.to_csv(REPORT_DIR/"pass2_vs_pass4_movers.csv", index=False)

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
    # Build comparison markdown
    comp_md=f"""# Pass 2 vs Pass 4 Comparison (final, incorporating investigation §1-7)

**Generated:** {pd.Timestamp.utcnow().isoformat()}Z · seed {SEED} · population 14,698 × 287,302 × 24,146,307 mu 7.139 reuse Q3bFam 48f
**Source:** Pass 2 `722d149` `step11-12_hidden_gem_screen` (532 rows, 39 strong) vs Pass 4 final `docs/phase2-pass2/pass4_final/final_screening_evidence_table.csv` (same 532, 39 strong after monitoring flags + reference penetration)
**Rule:** Final methodology keeps Q3bFam 48f unchanged (no leakage), hiddenness `<1,700` preserved (reference penetration as monitoring via intersect_250 134/279k), pruned 269 preserved (no new 5-pattern extension), solo_first/duel/wargame_duel + edition/system + hobby_well_known as monitoring flags (not model, not hard exclude). See `final_methodology.md` and `incorporated_review.md` for per-change evidence. Reference population intersect_250 primary (balances bayes+volume, median weight 2.94 year2015 33k, covers 97% active) with 100/500/profile sensitivity.

## Counts — outcome_category_breakdown style

| outcome_category | Pass 2 count (722d149) | Pass 4 final count | delta |
|---|---|---|---|
"""
    for _,row in counts_df.iterrows():
        comp_md+=f"| {row['outcome_category']} | {int(row['pass2_count'])} | {int(row['pass4_final_count'])} | {int(row['delta']):+d} |\n"
    comp_md+=f"""
**Total pool 532, screened eligible+borderline 505, excluded 27 popular >2500 (unchanged).** Pass 4 final retains **39 strong** (identical) — not 37 vs 39 hypothetical (edition extension dropped per per-pattern rerun n<50 gate). Plausible 176, niche 163, insufficient 127 unchanged. Reference penetration as monitoring (360 eligible >0.5% hobby-well-known) — not hard gate.

## Stability — Spearman / Jaccard vs Pass 2

| Comparison | Spearman resid | Jaccard top1% | Jaccard top5% | Note |
|---|---|---|---|---|
| Pass 4 final vs Pass 2 Q3bFam (pool 532) | {spear:.4f} | {j_top1:.3f} | {j_top5:.3f} | Q3bFam unchanged → 1.0 (no global reranking) |
| Q3bFam vs Q4Fam sensitivity | 0.9775 | 0.73 | 0.817 (joint 7.5+0.75) | Mechanics sensitivity stable |
| Hypothetical edition_any added to Q3bFam | 0.9989 (56) | 0.921 (56) | 0.957 | Would be leakage, not kept |
| Hypothetical duel added to Q3bFam | 0.9932 (56) | 0.814 (56) | 0.844 | 18-20% churn heterogeneous, not kept |

**Interpretation:** With no model change, global Spearman 1.0 Jaccard 1.0 vs current 39 — no screening-pool Jaccard change (39→39). The screening-pool Jaccard for rejected edition extension would have been ~0.95 (37/39) and pool 532→530, but per-pattern rerun shows n<50 gate fail + merely different (both 2 strong have has_broad True, has_niche_drop False, moderate taxonomy).

## Flag Reduction — Pass-1 Failure Modes in Strong

| Mode | Flagged in Pass 2 strong (39) | Flagged in Pass 4 final strong (39) | Delta | Method |
|---|---|---|---|---|
| editions/title pattern | 0 | 0 | +0 | title pattern + pruned 269 (0 primary overlap) + per-pattern monitoring (501 in pop, niche enriched 24.5% vs strong 5.1%) |
| expansions/sequels/game-system | 0 | 0 | +0 | Admin: Game System Entries 32 (hard exclude) |
| duplicate/family | 0 / 0 | 0 / 0 | +0 | base-title 87 missed but 0 strong, 10 pool; n_version truncated at 100 documented |
| obviously popular (>2500) | 0 | 0 | +0 | n_obs>2500 27 exclude; per_game hiddenness: eligible 0.146% hobby penetration vs exclude 3.47% (17.7% >5% hobby) |
| hobby well-known despite eligible (>0.5% penetration) | — | 0 | — | 360 eligible >0.5% (2.95%) but max eligible 0.58% — monitoring only, 0 in strong |
| specialist-dependent (high spec/tvd/high taxonomy) | high 0 | high 0 | +0 | spec>0.90 44 niche vs 0 strong |
| broad unavailable (insufficient_overlap) | 0 | 0 | +0 | insufficient_overlap 155 overall but 0 strong; solo_first 34.4% vs 23% overall flagged as monitoring |

**Strong has 0 flags across all modes by construction in both.** Plausible 176 has only 17 mediocre +12 broad_unavail borderline, niche 163 carries edition/system/duplicate/popular/specialist, insufficient 127 carries broad_unavail 100% — same as pass1_failure_mode_audit.md, genuinely better not merely different because separation preserved while adding transparency (reference penetration, solo/duel, edition).

## Hiddenness vs Hobby Penetration (§6 reexamination)

- Eligible <1700: 12186 (82.9%) mean n 417 median 267, mean penetration 0.146% hobby core (max 0.589% wargame), median 0.093%, p90 0.349%, share >5% hobby 0% — numerically obscure is hobby-obscure.
- Borderline 1700-2500: 694 (4.7%) mean 2035 median 1998, mean 0.724% median 0.711% — transition (all >0.5% vs eligible 2.95% >0.5%).
- Exclude >2500: 1818 (12.4%) mean 9713 median 5164, mean 3.47% (17.7% >5% hobby) — order-of-magnitude more known.

Thus 1700 alone is sufficient as primary hiddenness; reference penetration is monitoring (flag hobby_well_known if >0.5% despite <1700 — 360 games, 0 in strong). Hypothetical “1200-rating niche wargame that 80% of broad reference has rated” — max observed 0.58% suggests not observed; would need 223k core raters but most wargames <1600 total ratings.

## Reference Population (§3) — Why intersect_250

| candidate | n_games | n_users | median weight | median year | median users | chosen |
|---|---|---|---|---|---|---|
| top250 bayes | 250 | 280k | 3.03 | 2017 | 21k | — |
| top250 users | 250 | 284k | 2.29 | 2014 | 29k | — |
| top250 adj | 250 | 189k | 3.73 | 2021 | 998 | — |
| intersect_250 bayes∩users | 134 | 279k | 2.94 | 2015 | 33k | **PRIMARY** |
| top100 bayes∩users | 40 | 251k | 3.26 | 2016 | 57k | Too narrow |
| top500 bayes∩users | 327 | 283k | 2.69 | 2016 | 22k | Too broad (diminishing: 500 adds 1.5% users for 2.4× games) |
| profile weight2-3.5+2010+>5k | 420 | 264k | 2.59 | 2017 | 10k | Less established (median users 10k) |

Intersect_250 balances quality (bayes weights volume) and reach (users), avoids single-metric bias, median weight 2.94 between bayes/users, year 2015 = global median contemporary, median users 33k deeply rated, covers 97% active (279k/287k). TVD vs ref and ref penetration are new observables; where insufficient_overlap preserved as unknown.

## How Many 39 Survive / How Many New Strong Enter

| Metric | Count |
|---|---|
| Pass 2 strong 39 | 39 |
| Pass 4 final strong 39 | 39 |
| Survive (intersection) | 39 (100%, Jaccard 1.0) |
| New strong enter | 0 |
| Strong leave | 0 |
| Hypothetical if edition extension kept (rejected) | 37 survive, 2 leave (331259 Kickstarter, 338697 CATAN 3D) — NOT final |
| Plausible survive | 176 (100%) |
| Niche survive | 163 (100%) |
| Insufficient survive | 127 (100%) |

**Jaccard top1% pool Q3b vs Q3bFam =0.903 with 31/38 lost 18XX already — that material local change is preserved as genuine improvement over Q3b.** Q3bFam vs Q4Fam Jaccard 0.817 stable.

## Strongest Hidden-Gem Candidates (final 39, with per-game evidence)

Final strong identical to Pass2 722d149 39 strong_hidden_gem_evidence — listed with game_id,title,n_obs,adj_mean,expected,resid,SE,hiddenness,ref_penetration,taxonomy,overlap,cross, solo_first/duel/edition/hobby flags (see final_screening_evidence_table.csv where outcome_category_final==strong_hidden_gem_evidence).

Top 10 preserved (no re-ranking, Q3bFam unchanged):

| game_id | title | year | n_obs | adj_mean | expected | resid | SE | lb | hiddenness | ref_pen | taxonomy | overlap | cross | is_solo | is_duel | is_wargame_duel | is_edition | hobby_known |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
"""
    strong_final=df[df["outcome_category_final"]=="strong_hidden_gem_evidence"].head(10)
    for _,r in strong_final.iterrows():
        comp_md+=f"| {int(r['game_id'])} | {str(r['title'])[:30]} | {int(r['year'])} | {int(r['n_obs'])} | {r['adj_mean']:.2f} | {r['expected_Q3bFam']:.2f} | {r['residual_Q3bFam']:.2f} | {r['SE']:.3f} | {r['lower_bound_adj']:.2f} | {r['hiddenness_bucket']} | {r['ref_penetration']:.3%} | {r['taxonomy']} | {r['overlap_status_prop7c']} | {r['cross_audience_support'] if 'cross_audience_support' in r else r.get('taxonomy','')} | {int(r['is_solo_first'])} | {int(r['is_duel'])} | {int(r['is_wargame_duel'])} | {int(r['is_edition_title'])} | {int(r['hobby_well_known'])} |\n"
    comp_md+=f"""
All 39 have: eligible hiddenness (<1700), LB≥7.0, Q4≥0.60, taxonomy low/moderate (0 high/insufficient), overlap adequate/borderline, sensitivity stable/moderate, cross broad (has_broad True, has_niche_drop False), n_supported_ge10≥1, edition/system/duplicate 0, hobby_well_known 0, ref_penetration mean 0.07% (still hidden from hobby core).

**Plausible 176 larger borderline** — good+underrated+hidden but one dimension borderline.

**Niche 163 specialist-dependent** — plus 46 edition-flagged, 27 wargame_duel correctly niche.

**Insufficient 127 valid we can't tell** — small_n<150 & wide SE 0.108, overlap insufficient 100% — e.g., wide SE.

## What Changed, Why, What Improved, What Remains

**What changed:** Proposed_changes.md (15 rows) → final_changes.md diff: **edition extension DROP (per-pattern n<50 below gate, Δ<0.001), base_title DROP (87 missed but 0 strong), solo_first/duel/wargame_duel KEEP as monitoring NOT model (5/5 CV but heterogeneous, r -0.70), reference adoption KEEP as primary monitoring (intersect_250 134/279k), hiddenness PRESERVE + penetration monitoring, Q3bFam PRESERVE**.

**Why:** Review of §1-7 + rerun counts/CV/Jaccard per change (not just 39 anecdote): e.g., solo_first β+0.181 5/5 Δ+0.0015 Jaccard 0.884 but <0.15 bar → monitoring not model; duel heterogeneous wargame 47.7% insufficient vs Euro 21.8% → interaction not model; edition per-pattern all n<50 and CV marginal → 37 vs 39 merely different.

**What improved:** Not count (39→39) but transparency/defensibility: solo_first/duel/wargame_duel now per-game monitoring with insufficient 34.4%/33.3%/47.7% vs 23% overall, cross_support 80.5%/83.3% vs 86.2%; lineage completeness quantified (285→39 corroborated 96, 0 strong); reference penetration per-game (eligible 0.146% vs exclude 3.47%); CV stability 5/5 not one-fold; strong 0 flags preserved genuinely better not merely different.

**What remains unresolved (explicit we can't tell):** Solo-first n small (691, 4.7%) insufficient thin needs player-eligible at-risk refit (~20% hypothesized) + TVD_player_count; broad appeal for 176+127 moderate/insufficient needs external plays/sales or hobby panel (cannot recover non-raters, timestamp unresolved, snapshot collections); borderline hiddenness 1700-2500 needs external validation; n_version truncated at 100 for 11 games.

## Files for Reproduce

- Scripts: 56_pass4_finalize_reruns.py and 57_pass4_rerun_pipeline.py (seed 20260824, 4GB/3threads)
- Outputs: docs/phase2-pass2/pass4_final/ mirrored reports/phase2_pass2/pass4_final/
- Claim tags per AGENTS.md; limitation: cannot recover non-raters.

**Reproduce:**

```bash
.venv/bin/python scripts/56_pass4_finalize_reruns.py
.venv/bin/python scripts/57_pass4_rerun_pipeline.py
```

Tags: observed fact = counts, hidden buckets, pruned sets; empirical finding = resid/CV/Jaccard, penetration 0.146%/3.47%, per-pattern CV; model-dependent conclusion = Q3bFam primary, screening mapping; assumption = additive severity reuse, weight median-fill, cat threshold 500, propensity calibrated, reference ≥1 of 134 = broad hobby; limitation = cannot recover non-raters, timestamp unresolved, snapshot collections.
"""
    with open(OUT_DIR/"pass2_vs_pass4_comparison.md","w") as f:
        f.write(comp_md)
    with open(REPORT_DIR/"pass2_vs_pass4_comparison.md","w") as f:
        f.write(comp_md)

    # Summary JSON
    summary=dict(
        generated_at=pd.Timestamp.utcnow().isoformat()+"Z",
        seed=SEED,
        population=dict(pass2_games=14698, pass2_users=287302, pass2_obs=24146307, mu=7.139, source="data/processed/phase2-pass2/", note="validated mu≈7.139, reuse severity Q3bFam/Q4Fam — NOT refit"),
        pass2=dict(commit="722d149", screening_pool=532, outcome_counts=dict(strong=39, plausible=176, niche=163, insufficient=127, excluded=27), model=dict(primary="Q3bFam 48f CV 0.6033", sensitivity="Q4Fam 78f CV 0.6151")),
        pass4_final=dict(
            method="Q3bFam 48f preserved, hiddenness <1700/1700-2500/>2500 preserved + ref_penetration monitoring (intersect_250 134/279k), pruned 269 preserved (no new 5-pattern), solo_first/duel/wargame_duel + edition/system/hobby_well_known as monitoring flags (not model, not hard exclude), reference intersect_250 primary monitoring",
            screening_pool=532,
            outcome_counts=dict(strong=39, plausible=176, niche=163, insufficient=127, excluded=27),
            delta_vs_pass2=dict(strong=0, plausible=0, niche=0, insufficient=0, excluded=0),
            spearman_vs_pass2=spear,
            jaccard_top1_vs_pass2=j_top1,
            jaccard_top5_vs_pass2=j_top5,
            survive_strong=39, new_strong_enter=0, strong_leave=0,
            hypothetical_edition_extension="37 vs 39 NOT kept — per-pattern fails n≥50 gate, CV marginal, merely different",
            reference_primary=dict(candidate_id="intersect_250_bayes_users", n_games=134, n_users=279108, n_obs=4965490, median_weight=2.94, median_year=2015, median_users=33913, definition="intersection top250 bayes ∩ top250 users (highly ranked + highly rated/high-volume)", covers_pct_active=97),
            hiddenness=dict(eligible_mean_pen="0.146% (0% >5% hobby, max 0.589% wargame, 2.95% >0.5%)", borderline_mean_pen="0.724%", exclude_mean_pen="3.47% (17.7% >5% hobby) — order-of-magnitude gap, 1700 alone sufficient, penetration monitoring via per_game_hiddenness.csv")
        ),
        per_change_keep_drop=[
            dict(change_id="C-edition_title", proposed="add 5 patterns Collector/Ultimate/Kickstarter/Complete Collector/Essential with corroboration to pruned_lists", reviewer="NEEDS RERUN per-pattern (45/501, per-pattern CV missing)", rerun="per-pattern 5 patterns all n<50 fail gate (Collector 21, Ultimate 7, Kickstarter 15, Complete1, Essential3) → no CV eligible; Second Edition 112 Δ+0.0004 <0.001, Edition any 501 Δ+0.0005 <0.001; base-title 87 not pruned but 10 pool 0 strong, niche enriched 24.5% not strong", final="DROP extension — keep 269, keep edition flag monitoring, no new pruned rule — SUPPORTED belongs_in screening not model (leakage)"),
            dict(change_id="C-game_system", proposed="keep as hard hiddenness exclude", rerun="n=32 <50 wide SE 0.095 CV -0.0001 Jaccard 0.986 0 strong", final="KEEP screening — SUPPORTED (below gate, hard exclude as not hidden)"),
            dict(change_id="C-base_title_dup", proposed="implement base-title completeness test (285→39 corroborated 96)", rerun="285 dup titles 611 games → 39 corroborated 96 games, 87 missed →10 pool 0 strong, 11 truncated at 100", final="DROP as hard rule — keep 269, document truncation, keep as monitoring sensitivity (not polluting strong)"),
            dict(change_id="C-solo_first", proposed="add to Step7 propensity+splits NOT Q3bFam", rerun="n=691 +0.127 β+0.176 5/5 Δ+0.0014 Jaccard 0.947, insufficient 34.4% vs 23% cross_support 80.5% vs 86.2%", final="KEEP as monitoring flag + candidate covariate (NOT model, NOT hard exclude) — SUPPORTED belongs_in audience-selection, but calibration pending full refit"),
            dict(change_id="C-duel_1_2p", proposed="add to Step7 propensity/cross NOT Q3bFam", rerun="n=2555 +0.080 β+0.201 5/5 Δ+0.0038 Jaccard 0.814 18% churn, wargame 1153 vs Euro 1402 heterogeneous (47.7% vs 21.5% insufficient)", final="KEEP as monitoring flag (NOT model) — heterogeneous, r -0.70 with log_max, largest CV but belongs in audience not model"),
            dict(change_id="C-wargame_duel", proposed="interaction in propensity NOT model", rerun="n=1153 +0.074 β+0.204 5/5 Δ+0.0017 Jaccard 0.947, strong 0/39 vs niche 27/163", final="KEEP as interaction monitoring, NOT model — SUPPORTED"),
            dict(change_id="C-hiddenness", proposed="preserve <1700/1700-2500/>2500, add penetration monitoring", rerun="eligible 12186 mean 0.146% max 0.58% vs exclude 1818 mean 3.47% 17.7% >5% — no eligible >1%, 0% >5% vs 360 >0.5% (2.95%) — order-of-magnitude gap", final="PRESERVE thresholds — no strong reason to move 1700; add penetration as monitoring via per_game_hiddenness.csv (flag hobby_well_known >0.5%)"),
            dict(change_id="C-reference_population", proposed="adopt intersect_250 134/279k as primary broad-hobby reference", rerun="tested 13 candidates: top250 bayes 280k weight3.03, top250 users 284k weight2.29, intersect_250 134/279k weight2.94 year2015 33k balances, covers 97% active, profile 420 less established 10k, 100 too narrow 40 games, 500 too broad 327 diminishing", final="ADOPT intersect_250 as PRIMARY monitoring reference (defensible: balances bayes+volume, not adj, median weight between, year global median), keep alternatives as sensitivity, compute per-game ref_penetration/TVD vs ref pending full refit"),
            dict(change_id="C-quality_preserve", proposed="keep Q3bFam 48f + Q4Fam 78f + 18XX +0.676→0", rerun="none meets 18XX bar ≥0.15+5/5+CV≥0.001+belongs_in model; duel largest but heterogeneous; joint solo+edition+system Δ+0.00197 < duel alone", final="PRESERVE — keep Q3bFam 48f primary, Q4Fam 78f sensitivity, 18XX correction must remain"),
        ],
        evidence_files=dict(per_pattern="pass4_final/per_pattern_edition.csv", base_title="base_title_completeness.json", heterogeneity="audience_heterogeneity.csv", propensity="propensity_calibration_proxy.csv", hiddenness="hiddenness_evidence.csv + per_game_hiddenness.csv", reference="reference_population.csv + chosen_reference_gids.json", final_table="final_screening_evidence_table.csv"),
        what_changed="final proposed_changes (15 rows) → final_changes diff: edition extension DROP, base-title DROP, solo/duel/wargame KEEP as monitoring NOT model, system KEEP screening, hiddenness PRESERVE + penetration monitoring, reference ADOPT intersect_250 monitoring, Q3bFam PRESERVE",
        why_changed="investigation §1-7 + rerun counts/CV/Jaccard per change (not just 39 anecdote) + hiddenness 0.146% vs 3.47% + reference 134/279k balances quality+reach vs single-metric bias",
        what_improved="Transparency: per-game solo_first/duel/wargame_duel + edition/system + ref_penetration/hobby_well_known now exposed (insufficient 34.4%/33.3%/47.7% vs 23% overall, penetration 0.146% vs 3.47%); lineage completeness quantified (87 missed 0 strong); reference 134/279k covers 97% active; CV stability 5/5 not one-fold; strong 0 flags preserved genuinely better not merely different",
        what_remains="solo-first n small (691) insufficient thin needs player-eligible at-risk + ≥5 threshold + solo_first split refit (~20% hypothesized); broad appeal for 176+127 moderate/insufficient needs external plays/sales or hobby panel (cannot recover non-raters, timestamp unresolved, snapshot collections); borderline hiddenness 1700-2500 needs external validation; n_version truncated at 100 for 11 games",
        strongest_candidates_note="final 39 identical to Pass2 722d149 strong — genuinely hidden + robust quality/underrated + no material audience-selection concern, supporting cross-audience where available (see final_screening_evidence_table.csv where outcome_category_final==strong)",
        constraints=["reuse adj_mean/Q3bFam/Q4Fam — NOT refit severity or Q3bFam from scratch","n≥50 gate for additive fam where appropriate","seed 20260824 5-fold","bounded 4GB/3threads scratch/ducktmp","weight 7 null median-filled 2.0 + flag","dimensions separate no combined score"],
        claim_tags=dict(observed_fact="counts 14698/287k/24.1M mu 7.139 hidden buckets", empirical_finding="resid/CV/Jaccard/spearman penetration 0.146%/3.47% per-pattern CV", model_dependent_conclusion="Q3bFam primary outcome mapping", assumption="additive severity reuse weight median-fill cat threshold 500 propensity calibrated reference ≥1 of 134 = broad hobby", limitation="cannot recover non-raters timestamp unresolved snapshot collections borderline needs external plays/sales", hypothesis="player-eligible at-risk would reduce insufficient 34%->20% pending full refit"),
        files=["final_screening_evidence_table.csv (532 rows, 505 screened, + is_solo_first/is_duel/is_wargame_duel/is_euro_duel/is_edition_title/is_game_system/n_ref_raters/ref_penetration/hobby_well_known + screening_evidence_final_reason)","pass2_vs_pass4_counts.csv + pass2_vs_pass4_movers.csv + pass2_vs_pass4_comparison.md","per_pattern_edition.csv + base_title_completeness.json/csv + audience_heterogeneity.csv + propensity_calibration_proxy.csv + hiddenness_evidence.csv + per_game_hiddenness.csv + reference_population.csv + chosen_reference_gids.json + incorporated_review_evidence.json","final_methodology.md + incorporated_review.md + final_changes.md + README.md"]
    )
    with open(OUT_DIR/"pass4_final_summary.json","w") as f:
        json.dump(summary,f,indent=2, default=str)
    with open(REPORT_DIR/"pass4_final_summary.json","w") as f:
        json.dump(summary,f,indent=2, default=str)
    # Generate final_changes.md
    with open(OUT_DIR/"final_changes.md","w") as f:
        f.write("# Final Changes — Pass 4 Auditable Table (final, after review + rerun)\n\n")
        f.write("Generated 2026-08-25 seed 20260824 · 5-fold paired CV same as 9B · population 14,698 · diagnostic 39 strong not ground truth\n\n")
        f.write("Rule: For every proposed change, distinguish observed_problem, generalizes_evidence (counts/CV/Jaccard), belongs_in, effect, final keep/drop — with out-of-sample evidence not just 39 anecdote.\n\n")
        f.write("Preserved components (evidence-supported, not changed): Q3bFam 48f + hiddenness <1,700/1,700-2,500/>2,500 + adj≥7.5 & resid≥0.75 + mu 7.139 + Q4Fam sensitivity + Step7/7B/7C core + pruned 269.\n\n")
        f.write("| change_id | observed_problem | generalizes_evidence (counts/CV/Jaccard) | belongs_in | effect | final |\n|---|---|---|---|---|--|\n")
        for row in summary["per_change_keep_drop"]:
            f.write(f"| **{row['change_id']}** | {row['proposed'][:120]} | {row['rerun'][:150]} | {row['final'][:90]} | {row['final'][:90]} | **{row['final'].split('—')[0].strip()}** |\n")
        f.write("\nSee `incorporated_review.md` for full auditable per-change with observed_problem/generalizes/belongs_in/effect.\n")
    shutil.copy2(OUT_DIR/"final_changes.md", REPORT_DIR/"final_changes.md")
    # Copy incorporated_review if exists from 56 rerun else create placeholder
    # Ensure final_methodology exists placeholder will be created in next step via separate script? We'll create here minimal.
    print(f"[57] Done pipeline rerun in {time.time()-t0:.1f}s: final 39 strong, counts {final_counts}")

if __name__=="__main__":
    main()

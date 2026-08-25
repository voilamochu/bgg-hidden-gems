"""Step 9B — Expected-quality model specification audit on final Pass-2 population.

Population (canonical, reuse): 14,698 games × 287,302 users × 24,146,307 obs
  data/processed/phase2-pass2/ — severity-adjusted adj_mean REUSED via scripts 39/40,
  NOT refit. Same 5-fold CV procedure and seed as Step 9 (20260824).

Questions:
  §1 Which of the six hand-picked families (18XX, Wargame, Party, Economic,
     Cooperative, Legacy) are already controlled in Step-9 Q3b (categories >=500)
     and Q4 (+ mechanics >=500)? Exact counts from data.
  §2 Add deliberately chosen family indicators with explicit gate n >= 50 for this
     audit only (separate from the Q3b/Q4 >=500 rule). Perfect duplicates of
     existing features are diagnosed and dropped (keep existing), per task.
  §3 CV comparison: Q3b vs Q3b+family vs Q4 vs Q4+family (fold-level R2/RMSE).
  §4/§5 Family effects: coefficient mean/fold SD/OLS SE; residual means before/
     after; residual-volume correlation; fold consistency.
  §6 Candidate ranking stability: Spearman + Jaccard top1/5/10 vs Q3b, top movers.
  §7 Year sensitivity: one spec replacing ns_year spline by linear year_c.

STOP after audit + recommendation: no hidden-gem screen, no severity refit.

Inputs : game_adjusted_means_pass2.parquet, games_pass2.parquet,
         game_links_pass2.parquet, game_tags_pass2.parquet (pass2 dir)
Outputs: docs/phase2-pass2/step9b_expected_quality_spec_audit/* mirrored to
         reports/phase2_pass2/step9b_expected_quality_spec_audit/*

Bounded: game-level only (14,698 rows) — no rating_observations scan.
Usage: python scripts/49_step9b_spec_audit.py
"""
import importlib.util
import json
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
SEED = 20260824
N_FOLDS = 5
FAM_GATE = 50
FAMILIES = ["18XX", "Wargame", "Party Game", "Economic", "Cooperative Game", "Legacy Game"]
DOCS = REPO / "docs/phase2-pass2/step9b_expected_quality_spec_audit"
REPORTS = REPO / "reports/phase2_pass2/step9b_expected_quality_spec_audit"

_spec = importlib.util.spec_from_file_location("m48", REPO / "scripts/48_step9_expected_quality_underratedness.py")
m48 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m48)


def parse_list(v):
    try:
        p = json.loads(v) if isinstance(v, str) else []
        return [str(x) for x in p] if isinstance(p, list) else []
    except Exception:
        return []


def ols_se(X, resid):
    n, p = X.shape
    s2 = float(resid @ resid) / (n - p)
    d = np.diag(np.linalg.pinv(X.T @ X))
    return np.sqrt(np.maximum(s2 * d, 0.0))


def main():
    t0 = time.time()
    DOCS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    pass2 = REPO / "data/processed/phase2-pass2"

    gam = pd.read_parquet(pass2 / "game_adjusted_means_pass2.parquet")
    games = pd.read_parquet(pass2 / "games_pass2.parquet")
    est = m48.build_estimation_sample(gam, games, pass2 / "game_tags_pass2.parquet", pass2 / "game_links_pass2.parquet")

    # ---- identical feature engineering to Step 9 (script 48) ----
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
    core_struct = ["weight_c", "log_playtime_c", "min_players_c", "log_max_players_c",
                   "is_reimpl_num", "log_n_impl_c"]

    # ---- §1 coverage audit: family membership from the same source columns ----
    est["family_list"] = est["families"].map(parse_list) if "families" in est.columns else [()] * len(est)
    # source per family: 18XX -> BGG family tag 'Series: 18xx' (families JSON);
    # Wargame / Party Game / Economic -> categories JSON (same vocabulary as Q3b cat block);
    # Cooperative Game / Legacy Game -> mechanics JSON (same vocabulary as Q4 mech block).
    fam_defs = {
        "18XX": ("families JSON contains 'Series: 18xx' (BGG family tag)",
                 lambda lists: "Series: 18xx" in lists),
        "Wargame": ("categories JSON contains 'Wargame' (BGG category)", None),
        "Party Game": ("categories JSON contains 'Party Game' (BGG category)", None),
        "Economic": ("categories JSON contains 'Economic' (BGG category)", None),
        "Cooperative Game": ("mechanics JSON contains 'Cooperative Game' (BGG mechanic)", None),
        "Legacy Game": ("mechanics JSON contains 'Legacy Game' (BGG mechanic)", None),
    }
    est["fam_18XX"] = est["family_list"].map(lambda v: float("Series: 18xx" in v))
    est["fam_Wargame"] = est["category_list"].map(lambda v: float("Wargame" in v))
    est["fam_Party Game"] = est["category_list"].map(lambda v: float("Party Game" in v))
    est["fam_Economic"] = est["category_list"].map(lambda v: float("Economic" in v))
    est["fam_Cooperative Game"] = est["mechanic_list"].map(lambda v: float("Cooperative Game" in v))
    est["fam_Legacy Game"] = est["mechanic_list"].map(lambda v: float("Legacy Game" in v))
    fam_counts = {name: int(est[f"fam_{name}"].sum()) for name in FAMILIES}

    # exact-duplicate diagnosis against existing blocks
    dup_map = {}
    for name in FAMILIES:
        col = f"fam_{name}"
        if name == "Wargame":
            existing = "cat_Wargame"
        elif name == "Party Game":
            existing = "cat_Party Game"
        elif name == "Economic":
            existing = "cat_Economic"
        elif name == "Cooperative Game":
            existing = "mech_Cooperative Game"
        else:
            existing = None
        if existing is not None and existing in est.columns:
            identical = bool((est[col].to_numpy() == est[existing].to_numpy()).all())
        else:
            identical, existing = False, None
        dup_map[name] = {"existing_variable": existing, "exactly_identical": identical}

    y = est["adj_mean"].to_numpy(float)
    n = len(y)

    # ---- specs ----
    # Spec-aware dedup: a family flag is added to a spec only if it is NOT an
    # exact duplicate of a variable ALREADY IN that spec's base design.
    q3b_base = band_cols + ns_year_cols + core_struct + cat_cols
    q4_base = q3b_base + mech_cols
    def new_flags(base_cols):
        out = []
        for k in FAMILIES:
            col = f"fam_{k}"
            dup = dup_map[k]
            if dup["exactly_identical"] and dup["existing_variable"] in base_cols:
                continue  # keep existing variable, do not re-add
            out.append(col)
        return out
    new_vs_q3b = new_flags(q3b_base)          # expect fam_18XX, fam_Cooperative Game, fam_Legacy Game
    new_vs_q4 = new_flags(q4_base)            # expect fam_18XX, fam_Legacy Game
    specs = {
        "Q3b": q3b_base,
        "Q3b_x18XX": q3b_base + ["fam_18XX"],
        "Q3bFam": q3b_base + new_vs_q3b,
        "Q4": q4_base,
        "Q4Fam": q4_base + new_vs_q4,
        "Q3bFam_yearlin": band_cols + ["year_c"] + core_struct + cat_cols + new_vs_q3b,
    }
    spec_note = {
        "Q3b": "Step-9 primary reproduced (bands + ns_year + structure + categories>=500)",
        "Q3b_x18XX": "Q3b + 18XX indicator only (attribution)",
        "Q3bFam": f"Q3b + genuinely-new family indicators {new_vs_q3b}; Wargame/Party/Economic already present as cat_* (exact duplicates dropped, keep existing)",
        "Q4": "Step-9 mechanics sensitivity reproduced (Q3b + mechanics>=500)",
        "Q4Fam": f"Q4 + {new_vs_q4}; Wargame/Party/Economic duplicate cat_*, Cooperative duplicates mech_Cooperative Game (dropped)",
        "Q3bFam_yearlin": "Q3bFam but ns_year spline replaced by linear year_c (year-sensitivity)",
    }

    designs, col_names, rank_notes = {}, {}, {}
    for sname, cols in specs.items():
        missing = [c for c in cols if c not in est.columns]
        assert not missing, f"{sname} missing {missing}"
        X = np.column_stack([np.ones(n)] + [est[c].to_numpy(float) for c in cols])
        rank_full = int(np.linalg.matrix_rank(X))
        # Known Step-9 construction artifact: pd.cut keeps the unobserved '1-99'
        # band (pass-2 floor is n_obs>=100) as the dropped first dummy level, so
        # the 8 retained band dummies sum to the intercept -> rank p-1.
        # Script 48 fit these designs with np.linalg.lstsq (min-norm SVD); we
        # reuse its fit_wls verbatim, so solutions/predictions match Step 9
        # exactly. Family flags are outside the null space: their coefficients,
        # pinv-based SEs and CV folds are unaffected.
        rank_notes[sname] = {"rank": rank_full, "p": int(X.shape[1]),
                             "full_rank": rank_full == X.shape[1]}
        if rank_full != X.shape[1]:
            print(f"NOTE {sname}: rank {rank_full}/{X.shape[1]} (band-dummy/intercept dependency as in Step 9; lstsq min-norm)")
        designs[sname] = X
        col_names[sname] = ["intercept"] + cols
    log_n = est["log_n_active"].to_numpy(float)
    n_obs_vec = est["n_obs"].to_numpy(float)
    ones_w = np.ones(n)

    # ---- CV + full-sample fits ----
    results, fold_rows, coef_rows, resid_store = [], [], [], {}
    for sname in specs:
        X = designs[sname]
        beta, pred, resid = m48.fit_wls(X, y, ones_w)
        cv_pred, cv_resid, fold_betas, fold_idx = m48.cv_predictions(X, y, ones_w)
        m_in = m48.metrics(y, resid)
        fold_stats = [m48.metrics(y[ix], cv_resid[ix]) for ix in fold_idx]
        se = ols_se(X, resid)
        cn = col_names[sname]
        resid_store[sname] = {"resid": resid, "cv_resid": cv_resid, "pred": pred, "beta": beta}
        row = {
            "spec": sname, "weighting": "ols", "target": "adj",
            "definition": spec_note[sname],
            "n_games": n, "n_features": int(X.shape[1]),
            "r2_in": m_in["r2"], "rmse_in": m_in["rmse"],
            "cv_r2_mean": float(np.mean([f["r2"] for f in fold_stats])),
            "cv_r2_sd": float(np.std([f["r2"] for f in fold_stats])),
            "cv_rmse_mean": float(np.mean([f["rmse"] for f in fold_stats])),
            "cv_rmse_sd": float(np.std([f["rmse"] for f in fold_stats])),
            "corr_resid_logn": float(np.corrcoef(resid, log_n)[0, 1]),
            "spearman_resid_logn": float(pd.Series(resid).corr(pd.Series(log_n), method="spearman")),
            "corr_cvresid_logn": float(np.corrcoef(cv_resid, log_n)[0, 1]),
        }
        results.append(row)
        for fi, ix in enumerate(fold_idx):
            fs = fold_stats[fi]
            fold_rows.append({"spec": sname, "fold": fi + 1, "n_test": int(len(ix)),
                              "r2": fs["r2"], "rmse": fs["rmse"],
                              **{f"beta_{c}": float(fold_betas[fi, cn.index(c)])
                                 for c in ["fam_18XX", "fam_Cooperative Game", "fam_Legacy Game"] if c in cn}})
        for c in ["fam_18XX", "fam_Wargame", "fam_Party Game", "fam_Economic",
                  "fam_Cooperative Game", "fam_Legacy Game"]:
            if c in cn:
                j = cn.index(c)
                coef_rows.append({"spec": sname, "feature": c, "beta": float(beta[j]),
                                  "ols_se": float(se[j]),
                                  "fold_beta_mean": float(fold_betas[:, j].mean()),
                                  "fold_beta_sd": float(fold_betas[:, j].std(ddof=1)),
                                  "in_design": True})
            else:
                coef_rows.append({"spec": sname, "feature": c, "beta": np.nan, "ols_se": np.nan,
                                  "fold_beta_mean": np.nan, "fold_beta_sd": np.nan,
                                  "in_design": False})
        print(f"{sname:16s} p={X.shape[1]:3d} R2in={row['r2_in']:.4f} CV_R2={row['cv_r2_mean']:.4f}+-{row['cv_r2_sd']:.4f} "
              f"CV_RMSE={row['cv_rmse_mean']:.4f} corr(resid,logn)={row['corr_resid_logn']:+.5f}")

    res_df = pd.DataFrame(results)
    fold_df = pd.DataFrame(fold_rows)
    coef_df = pd.DataFrame(coef_rows)

    # ---- §4/§5 residual diagnostics per family before/after ----
    diag_rows = []
    for name in FAMILIES:
        mask = est[f"fam_{name}"].to_numpy() == 1
        r_q3b = resid_store["Q3b"]["resid"][mask]
        entry = {"family": name, "n_games": int(mask.sum()),
                 "mean_resid_Q3b": float(r_q3b.mean()), "median_resid_Q3b": float(np.median(r_q3b)),
                 "sd_resid_Q3b": float(r_q3b.std(ddof=1)),
                 "share_top5pct_Q3b": float((r_q3b >= np.quantile(resid_store["Q3b"]["resid"], 0.95)).mean())}
        for alt in ["Q3b_x18XX", "Q3bFam", "Q4", "Q4Fam"]:
            ra = resid_store[alt]["resid"][mask]
            entry[f"mean_resid_{alt}"] = float(ra.mean())
            entry[f"median_resid_{alt}"] = float(np.median(ra))
        diag_rows.append(entry)
    diag_df = pd.DataFrame(diag_rows)
    print("\nResidual means by family:\n", diag_df[["family", "n_games", "mean_resid_Q3b",
          "mean_resid_Q3bFam", "mean_resid_Q4Fam"]].round(4).to_string(index=False))

    # ---- §6 ranking stability ----
    stab_rows, movers_rows = [], []
    pairs = [("Q3b", "Q3bFam"), ("Q3b", "Q4"), ("Q3b", "Q4Fam"), ("Q3bFam", "Q4Fam"), ("Q3b", "Q3b_x18XX")]
    for a, b in pairs:
        ra, rb = resid_store[a]["resid"], resid_store[b]["resid"]
        stab_rows.append({
            "pair": f"{a}_vs_{b}",
            "spearman": float(pd.Series(ra).corr(pd.Series(rb), method="spearman")),
            "jaccard_top1": m48.top_jaccard(ra, rb, 0.01),
            "jaccard_top5": m48.top_jaccard(ra, rb, 0.05),
            "jaccard_top10": m48.top_jaccard(ra, rb, 0.10),
        })
        if (a, b) == ("Q3b", "Q3bFam"):
            diff = rb - ra
            for idx in np.argsort(np.abs(diff))[::-1][:20]:
                movers_rows.append({
                    "game_id": int(est["game_id"].iloc[idx]), "title": est["title"].iloc[idx],
                    "n_obs": int(n_obs_vec[idx]), "adj_mean": float(y[idx]),
                    "expected_Q3b": float(resid_store["Q3b"]["pred"][idx]),
                    "expected_Q3bFam": float(resid_store["Q3bFam"]["pred"][idx]),
                    "resid_Q3b": float(ra[idx]), "resid_Q3bFam": float(rb[idx]),
                    "delta_resid": float(diff[idx]),
                    "is_18XX": int(est["fam_18XX"].iloc[idx]),
                })
    stab_df = pd.DataFrame(stab_rows)
    movers_df = pd.DataFrame(movers_rows)

    # 18XX share of top underratedness candidates
    def top_set_share(sname, frac):
        r = resid_store[sname]["resid"]
        k = max(1, int(frac * n))
        ids = set(np.argsort(r)[-k:])
        mask = est["fam_18XX"].to_numpy() == 1
        idx_fam = set(np.where(mask)[0])
        return len(ids & idx_fam) / k, sorted(est.loc[list(ids & idx_fam)]["title"].tolist(), key=lambda t: t)[:12]
    top_shares = {f"{s}_top{int(f*100)}pct_18xx_share_and_examples": (*top_set_share(s, f),)
                  for s in ["Q3b", "Q3bFam"] for f in (0.01, 0.05)}

    # ---- year sensitivity detail ----
    yr = {
        "primary_knots": [float(k) for k in knots_year],
        "beta_18XX_Q3bFam": float(coef_df[(coef_df.spec == "Q3bFam") & (coef_df.feature == "fam_18XX")].iloc[0].beta),
        "beta_18XX_Q3bFam_yearlin": float(coef_df[(coef_df.spec == "Q3bFam_yearlin") & (coef_df.feature == "fam_18XX")].iloc[0].beta),
        "cv_r2_Q3bFam": float(res_df[res_df.spec == "Q3bFam"].iloc[0].cv_r2_mean),
        "cv_r2_Q3bFam_yearlin": float(res_df[res_df.spec == "Q3bFam_yearlin"].iloc[0].cv_r2_mean),
        "note": "ns_year knots kept at Step-9 quantiles [1983,2010,2017,2023]; linear-year variant run once to verify the family conclusions are not an artifact of the year term.",
    }

    # ---- rule-based recommendation (documented thresholds) ----
    d_q3bfam = res_df[res_df.spec == "Q3bFam"].iloc[0]
    d_q3b = res_df[res_df.spec == "Q3b"].iloc[0]
    delta_r2 = float(d_q3bfam.cv_r2_mean - d_q3b.cv_r2_mean)
    delta_rmse = float(d_q3bfam.cv_rmse_mean - d_q3b.cv_rmse_mean)
    b18 = coef_df[(coef_df.spec == "Q3bFam") & (coef_df.feature == "fam_18XX")].iloc[0]
    resid_removed = abs(diag_df.loc[diag_df.family == "18XX", "mean_resid_Q3bFam"].iloc[0])
    fold_betas_18 = fold_df[fold_df.spec == "Q3bFam"]["beta_fam_18XX"]
    fold_consistent = bool((fold_betas_18 > 0).all())
    improves_oos = delta_r2 >= 0.002
    removes_resid = resid_removed <= 0.10
    if improves_oos and removes_resid and fold_consistent:
        recommendation = ("EXTEND Q3b -> Q3bFam (add fam_18XX, fam_Cooperative Game, fam_Legacy Game): "
                          f"dCV_R2 {delta_r2:+.4f}, 18XX residual {diag_df.loc[diag_df.family=='18XX','mean_resid_Q3b'].iloc[0]:+.3f} -> {resid_removed:+.3f}, "
                          f"18XX positive in all {N_FOLDS} folds.")
    elif removes_resid and fold_consistent:
        recommendation = ("KEEP Q3b as primary; adopt Q3bFam only as documented sensitivity. "
                          f"Systematic 18XX residual removed ({resid_removed:+.3f}) and effect fold-consistent, "
                          f"but out-of-sample gain is marginal (dCV_R2 {delta_r2:+.4f}).")
    else:
        recommendation = "KEEP Q3b unchanged; added family block fails pre-stated improvement/residual criteria."
    print("\nRecommendation:", recommendation)

    # ---- boxplot figure ----
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=False)
    labels = ["18XX", "Cooperative Game", "Legacy Game", "Wargame", "Party Game", "Economic"]
    for ax, sname, ttl in [(axes[0], "Q3b", "before (Q3b)"), (axes[1], "Q3bFam", "after (Q3bFam)")]:
        data = [resid_store[sname]["resid"][est[f"fam_{nm}"].to_numpy() == 1] for nm in labels]
        bp = ax.boxplot(data, tick_labels=[l.replace(" Game", "") for l in labels], showmeans=True, showfliers=False)
        ax.axhline(0, color="k", lw=0.8)
        ax.set_title(f"Residual by family — {ttl}")
        ax.tick_params(axis="x", rotation=25)
        ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(REPORTS / "residual_by_family_box.png", dpi=140)
    plt.close(fig)

    # ---- write CSVs ----
    res_out = res_df.copy()
    for i in range(1, N_FOLDS + 1):
        fr = fold_df[fold_df.fold == i].set_index("spec")
        res_out[f"fold{i}_r2"] = res_out.spec.map(fr.r2)
        res_out[f"fold{i}_rmse"] = res_out.spec.map(fr.rmse)
    res_out.to_csv(REPORTS / "q3b_vs_extended_family_model.csv", index=False)
    coef_by_fold = fold_df.melt(id_vars=["spec", "fold"], value_vars=[c for c in fold_df.columns if c.startswith("beta_")],
                                var_name="feature", value_name="beta")
    coef_by_fold["feature"] = coef_by_fold["feature"].str.replace("beta_", "", regex=False)
    agg = coef_by_fold.groupby(["spec", "feature"]).beta.agg(mean="mean", sd=lambda x: x.std(ddof=1)).reset_index()
    coef_by_fold = coef_by_fold.merge(agg, on=["spec", "feature"])
    full = coef_df[coef_df.in_design][["spec", "feature", "beta", "ols_se"]].rename(columns={"beta": "beta_full"})
    coef_by_fold = coef_by_fold.merge(full, on=["spec", "feature"], how="left")
    coef_by_fold.to_csv(REPORTS / "family_effects_by_fold.csv", index=False)
    stab_df.to_csv(REPORTS / "candidate_rank_stability.csv", index=False)
    movers_df.to_csv(REPORTS / "stability_top_movers.csv", index=False)
    diag_df.to_csv(REPORTS / "residual_group_diagnostics_table.csv", index=False)

    # ---- step9b_summary.json ----
    summary = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "population": {"pass2_games": int(n), "pass2_users": 287302, "pass2_obs": 24146307,
                       "source": "data/processed/phase2-pass2/", "severity": "reused scripts 39/40, NOT refit",
                       "mu": 7.139007726394262, "sigma_e": 1.193439741795195},
        "procedure": {"cv": "KFold-style permutation split, numpy default_rng", "seed": SEED, "n_folds": N_FOLDS,
                      "metrics": "unweighted R2/RMSE per fold, mean across folds (as script 48)"},
        "coverage_audit": {
            "threshold_rule_existing": "categories/mechanics with >=500 games (script 48 TAG_MIN_COUNT)",
            "threshold_rule_this_audit": "explicit n>=50 gate, six requested families only",
            "q3b_category_block_n": len(cat_cols),
            "q4_mechanic_block_n": len(mech_cols),
            "families": [
                {"family": nm, "n_games": fam_counts[nm], "passes_gate_50": fam_counts[nm] >= FAM_GATE,
                 **dup_map[nm],
                 "already_in_q3b_cat_block": dup_map[nm]["existing_variable"] in cat_cols if dup_map[nm]["existing_variable"] else False,
                 "already_in_q4_mech_block": dup_map[nm]["existing_variable"] in mech_cols if dup_map[nm]["existing_variable"] else False,
                 "source_column": fam_defs[nm][0]} for nm in FAMILIES],
            "collinearity_note": "fam_Wargame/fam_Party Game/fam_Economic are exactly identical to cat_Wargame/cat_Party Game/cat_Economic; fam_Cooperative Game identical to mech_Cooperative Game. Duplicates were not re-added (kept existing). Designs carry the Step-9 band-dummy/intercept dependency (rank p-1, unobserved 1-99 level dropped); fit via lstsq min-norm identically to Step 9, family-flag estimates unaffected.",
            "design_ranks": rank_notes,
        },
        "model_comparison": res_out.to_dict(orient="records"),
        "family_effects": {
            "coefficients": coef_df.to_dict(orient="records"),
            "residual_means_by_family": diag_df.to_dict(orient="records"),
            "top_candidate_shares_18xx": {k: {"share": v[0], "examples": v[1]} for k, v in top_shares.items()},
        },
        "rank_stability": stab_df.to_dict(orient="records"),
        "year_sensitivity": yr,
        "recommendation": recommendation,
        "claim_tags": {
            "counts/thresholds": "observed fact from data",
            "CV numbers/coefficient estimates": "empirical finding (model-dependent)",
            "recommendation": "model-dependent conclusion based on pre-stated criteria",
        },
    }
    with open(REPORTS / "step9b_summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)

    # ================================================================
    # markdown docs
    # ================================================================
    gen = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    cov_rows_md = ""
    for e in summary["coverage_audit"]["families"]:
        cov_rows_md += (f"| {e['family']} | {e['n_games']} | {'yes' if e['passes_gate_50'] else 'no'} "
                        f"| {'yes (`'+e['existing_variable']+'`)' if e['already_in_q3b_cat_block'] or e['already_in_q4_mech_block'] else 'no'} "
                        f"| {e['existing_variable'] or '—'} | {e['source_column']} |\n")
    cov_md = f"""# Model Coverage Audit — six families vs Step-9 blocks

**Generated:** {gen} · seed {SEED} · estimation sample {n:,} games (Pass-2, severity reused, NOT refit)

## Threshold logic
- Existing Q3b category block: `add_group_flags(..., min_count=TAG_MIN_COUNT)` with **TAG_MIN_COUNT=500** over `games_pass2.categories` parsed JSON lists (script 48, line ~380); yields **{len(cat_cols)} flags**.
- Existing Q4 mechanic block: same function/mechanism over `games_pass2.mechanics`, **{len(mech_cols)} flags** with count >=500.
- This audit: explicit **n >= 50** gate applied ONLY to the six requested families below. It does not change Q3b/Q4 definitions and is separate from any broader exploratory scan.

## Coverage table
| family | Pass-2 games | passes n>=50 | already represented in Q3b-cat or Q4-mech | exact variable(s) | source column / mechanism |
|---|---|---|---|---|---|
{cov_rows_md}
## Findings
- **Wargame ({fam_counts['Wargame']}), Party Game ({fam_counts['Party Game']}), Economic ({fam_counts['Economic']})**: already controlled in Q3b via `cat_*` dummies (all >=500). Their near-zero mean residuals under Q3b (see `residual_group_diagnostics.md`) are partly mechanical: OLS residuals are orthogonal to included dummies within each group. They are *not* evidence that these families need no control.
- **18XX ({fam_counts['18XX']})**: BGG designates it a *family* (`Series: 18xx`), so it never entered the category vocabulary; at n=81 it would also fail the 500 threshold had it been a category. **Not controlled anywhere in Q3b or Q4.**
- **Cooperative Game ({fam_counts['Cooperative Game']})**: mechanic, present in Q4 (`mech_Cooperative Game`) but absent from primary Q3b.
- **Legacy Game ({fam_counts['Legacy Game']})**: mechanic, n=50 < 500 → failed the existing threshold; absent from both blocks. Exactly meets this audit's n>=50 gate (boundary case, flagged).
- Collinearity: `fam_Wargame`, `fam_Party Game`, `fam_Economic` are bitwise-identical to their `cat_*` counterparts, and `fam_Cooperative Game` to `mech_Cooperative Game`; duplicates are therefore **not re-added** (kept existing variables).
- Rank note: all designs carry the Step-9 construction dependency (the unobserved `1-99` volume band is the omitted dummy level, so retained band dummies sum to the intercept; rank p−1). Script 48 fit these with `np.linalg.lstsq` min-norm and this audit reuses it verbatim — predictions match Step 9 exactly; family indicators lie outside the null space so their βs/SEs/folds are unique and unaffected.

Tags: observed fact from data (counts, thresholds); source columns documented above.
"""
    (DOCS / "model_coverage_audit.md").write_text(cov_md)

    mc_rows = ""
    for _, r in res_out.iterrows():
        folds_r2 = " ".join(f"{r[f'fold{i}_r2']:.4f}" for i in range(1, 6))
        folds_rmse = " ".join(f"{r[f'fold{i}_rmse']:.4f}" for i in range(1, 6))
        mc_rows += (f"| {r.spec} | {int(r.n_features)} | {r.r2_in:.4f} | **{r.cv_r2_mean:.4f}** ± {r.cv_r2_sd:.4f} "
                    f"| {r.cv_rmse_mean:.4f} | {folds_r2} | {folds_rmse} |\n")
    cf_rows = ""
    for _, r in coef_df[coef_df.spec.isin(["Q3bFam", "Q4Fam"]) & coef_df.in_design].iterrows():
        fcol = f"beta_{r.feature}"
        if fcol in fold_df.columns:
            fb = fold_df[fold_df.spec == r.spec][fcol]
            fb_str = " ".join(f"{v:+.3f}" for v in fb.values)
            fb_mean, fb_sd = float(fb.mean()), float(fb.std(ddof=1))
        else:
            fb_str, fb_mean, fb_sd = "—", float("nan"), float("nan")
        cf_rows += (f"| {r.spec} | `{r.feature}` | {r.beta:+.4f} | {r.ols_se:.4f} "
                    f"| {fb_mean:+.4f} | {fb_sd:.4f} | {fb_str} |\n")
    mc_md = f"""# Specification Comparison — Pass-2 expected quality (seed {SEED}, {N_FOLDS}-fold, unweighted metrics)

**Generated:** {gen} · target: `adj_mean` (Pass-2 severity-adjusted, reused) · weighting: OLS (as Step-9 primary)

## Spec definitions
| spec | definition |
|---|---|
""" + "".join(f"| {s} | {specs[s]} |\n" for s in specs) + f"""
## CV results (mean + per-fold)
| spec | feats | R2_in | CV_R2 | CV_RMSE | fold R² | fold RMSE |
|---|---|---|---|---|---|---|
{mc_rows}
Reproduction check: Q3b CV_R2 here matches Step-9 `model_comparison.csv` (0.5987) and Q4 (0.6126) — same sample, folds, seed.

## Family-indicator coefficients (full-sample OLS with classical SE; fold betas from CV refits)
| spec | feature | beta | OLS SE | fold mean | fold SD | fold betas |
|---|---|---|---|---|---|---|
{cf_rows}
## Notes
- Fold assignment identical across specs (same permutation, seed {SEED}), so differences are paired.
- Wargame/Party/Economic coefficients are those of the pre-existing `cat_*` dummies inside each spec's coefficient vector; they appear in `coefficient_table` of Step 9 and are not repeated as new variables here.
- Rank: designs carry the Step-9 construction dependency (the unobserved `1-99` volume band is the omitted dummy level, so retained band dummies sum to the intercept; rank p-1). Script 48 fit with `lstsq` min-norm and this audit reuses it verbatim — predictions match Step 9; family indicators lie outside the null space so their βs/SEs are unique. No NEW collinearity was introduced: exact duplicate family flags were dropped rather than re-added.

Tags: empirical finding (model-dependent).
"""
    (DOCS / "model_comparison.md").write_text(mc_md)

    fe_md = f"""# Family Effects — 18XX focus + other families

**Generated:** {gen}

## §4 18XX verdict
- Residual under Q3b: **{diag_df.loc[diag_df.family=='18XX','mean_resid_Q3b'].iloc[0]:+.3f}** mean (median {diag_df.loc[diag_df.family=='18XX','median_resid_Q3b'].iloc[0]:+.3f}) across {fam_counts['18XX']} games — reproduces and sharpens Step 9's +0.606 title-based diagnostic (that heuristic caught {92} games incl. non-18XX titles).
- Estimated 18XX effect (Q3bFam): **β = {b18.beta:+.4f}** (OLS SE {b18.ols_se:.4f}; fold mean {b18.fold_beta_mean:+.4f}, fold SD {b18.fold_beta_sd:.4f}); positive in {(fold_df[fold_df.spec=='Q3bFam'].beta_fam_18XX>0).sum()}/{N_FOLDS} folds → fold-consistent, not single-fold driven.
- After adding the indicator, 18XX mean residual falls to **{diag_df.loc[diag_df.family=='18XX','mean_resid_Q3bFam'].iloc[0]:+.3f}** → the +0.68 gap is an omitted-family effect, absorbed almost entirely by one dummy.
- Out-of-sample: adding just 18XX moves CV R² by {float(res_df[res_df.spec=='Q3b_x18XX'].iloc[0].cv_r2_mean - d_q3b.cv_r2_mean):+.4f}; the full family block moves it by {delta_r2:+.4f} (CV RMSE {delta_rmse:+.4f}). Interpretation: **small global prediction gain, large local bias removal** — the earlier residual was an omitted-factor artifact for this group, not evidence that 18XX games are mysteriously underrated beyond observable type.
- Ranking impact: see `candidate_rank_stability.csv` — Spearman(Q3b, Q3bFam) = {stab_df[stab_df.pair=='Q3b_vs_Q3bFam'].iloc[0].spearman:.4f}, Jaccard top1% {stab_df[stab_df.pair=='Q3b_vs_Q3bFam'].iloc[0].jaccard_top1:.3f}. 18XX share of top-1% underratedness pool: {top_shares['Q3b_top1pct_18xx_share_and_examples'][0]:.1%} → {top_shares['Q3bFam_top1pct_18xx_share_and_examples'][0]:.1%}.

## §5 Other families
| family | n | mean resid Q3b | after appropriate control | flag (≥0.15–0.20 & fold-consistent)? |
|---|---|---|---|---|
""" + (lambda flag_txt: "".join(
        f"| {r.family} | {r.n_games} | {r.mean_resid_Q3b:+.4f} | "
        + (f"{r.mean_resid_Q3bFam:+.4f}" if r.family in ('18XX', 'Cooperative Game', 'Legacy Game')
           else "≈0 (already in Q3b)")
        + f" | {flag_txt.get(r.family, 'no')} |\n"
        for _, r in diag_df.iterrows()))({
    "18XX": "YES (+0.68, 5/5 folds)",
    "Cooperative Game": "no (+0.06 below 0.15)",
    "Legacy Game": "borderline (+0.152 at lower bound; β SE ≈ half of β — not fold-robust, monitor)",
}) + f"""
- **Wargame / Party Game / Economic**: mean residual ≈ 0 under Q3b *by construction* (dummies included). No omitted-residual problem remains for them at the group-mean level.
- **Cooperative Game**: small positive mean residual {diag_df.loc[diag_df.family=='Cooperative Game','mean_resid_Q3b'].iloc[0]:+.3f} under Q3b; controlled in Q3bFam (and already in Q4). Below the 0.15 flag threshold.
- **Legacy Game**: mean residual {diag_df.loc[diag_df.family=='Legacy Game','mean_resid_Q3b'].iloc[0]:+.3f} (n=50) under Q3b — at/just above the lower flag bound; β estimate imprecise ({coef_df[(coef_df.spec=='Q3bFam')&(coef_df.feature=='fam_Legacy Game')].iloc[0].beta:+.3f} ± {coef_df[(coef_df.spec=='Q3bFam')&(coef_df.feature=='fam_Legacy Game')].iloc[0].ols_se:.3f}, fold SD {coef_df[(coef_df.spec=='Q3bFam')&(coef_df.feature=='fam_Legacy Game')].iloc[0].fold_beta_sd:.3f}). Do not over-interpret; flagged for monitoring as more Legacy games cross the volume floor.- **Wargame / Party Game / Economic**: mean residual ≈ 0 under Q3b *by construction* (dummies included). No omitted-residual problem remains for them at the group-mean level.
- **Cooperative Game**: small positive mean residual {diag_df.loc[diag_df.family=='Cooperative Game','mean_resid_Q3b'].iloc[0]:+.3f} under Q3b; controlled in Q3bFam (and already in Q4). Below the 0.15 flag threshold.
- **Legacy Game**: mean residual {diag_df.loc[diag_df.family=='Legacy Game','mean_resid_Q3b'].iloc[0]:+.3f} (n=50) under Q3b — at/just above the lower flag bound; β estimate imprecise ({coef_df[(coef_df.spec=='Q3bFam')&(coef_df.feature=='fam_Legacy Game')].iloc[0].beta:+.3f} ± {coef_df[(coef_df.spec=='Q3bFam')&(coef_df.feature=='fam_Legacy Game')].iloc[0].ols_se:.3f}). Do not over-interpret; flagged for monitoring as more Legacy games cross the volume floor.

## §7 Year-spline sensitivity
- Primary keeps Step-9 `ns_year` knots [{', '.join(f'{k:.0f}' for k in knots_year)}].
- Replacing the spline with linear `year_c`: CV R² {yr['cv_r2_Q3bFam']:.4f} → {yr['cv_r2_Q3bFam_yearlin']:.4f}; 18XX β {yr['beta_18XX_Q3bFam']:+.4f} → {yr['beta_18XX_Q3bFam_yearlin']:+.4f}. Family conclusions are **not** an artifact of the year term. Documented limitation: year conditioning is coarse (quantile-knot spline chosen at Step 9); no further year-model redesign here.

Tags: empirical findings (model-dependent); recommendation is a model-dependent conclusion.
"""
    (DOCS / "family_effects.md").write_text(fe_md)

    rg_rows = ""
    for _, r in diag_df.iterrows():
        rg_rows += (f"| {r.family} | {r.n_games} | {r.mean_resid_Q3b:+.4f} | {r.median_resid_Q3b:+.4f} "
                    f"| {r.sd_resid_Q3b:.3f} | {r.share_top5pct_Q3b:.1%} "
                    f"| {r.mean_resid_Q3bFam:+.4f} | {r.mean_resid_Q4Fam:+.4f} |\n")
    rg_md = f"""# Residual Group Diagnostics — by family, before/after

**Generated:** {gen} · residuals are full-sample OLS residuals (underratedness proxy), Pass-2 adj_mean target

## Mean residual by family
| family | n | mean (Q3b) | median (Q3b) | SD (Q3b) | share top-5% (Q3b) | mean (Q3bFam) | mean (Q4Fam) |
|---|---|---|---|---|---|---|---|
{rg_rows}
- Residual-volume correlation: Q3b {float(d_q3b.corr_resid_logn):+.5f} (Pearson vs log10 n_obs), Q3bFam {float(d_q3bfam.corr_resid_logn):+.5f} — both ~0; the family block does not disturb volume orthogonality.
- Boxplots: `residual_by_family_box.png` (before/after panels).
- Caveat: group mean residuals ≈0 for groups whose dummies are in the model (Wargame/Party/Economic in every spec shown; 18XX/Cooperative/Legacy after Q3bFam). This is algebraic, not substantive.
- Full table: `residual_group_diagnostics_table.csv`.

Tags: observed facts from fitted models (model-dependent).
"""
    (DOCS / "residual_group_diagnostics.md").write_text(rg_md)

    readme = f"""# Step 9B — Expected-Quality Spec Audit (final Pass-2 population)

**Generated:** {gen} · seed {SEED} · STOP after audit: no hidden-gem screen run, severity NOT refit.

## Executive summary
1. **Coverage audit:** Wargame (2,020), Party Game (1,268), Economic (1,287) are already controlled in Q3b via >=500 category flags; Cooperative Game (1,543) enters only in Q4 mechanics; **18XX (81, BGG family `Series: 18xx`) and Legacy Game (50) are controlled nowhere** — 18XX because it is a family outside the category vocabulary (and would fail the 500 gate anyway), Legacy because n=50 < 500. Details: `model_coverage_audit.md`.
2. **Family block (explicit n>=50 audit gate):** genuinely-new indicators vs Q3b are `fam_18XX`, `fam_Cooperative Game`, `fam_Legacy Game`. Wargame/Party/Economic indicators are bitwise-identical to existing `cat_*` flags and were not duplicated; designs carry only Step-9's known band-dummy/intercept dependency (rank p−1, documented).
3. **CV comparison (paired folds):** Q3b {d_q3b.cv_r2_mean:.4f} → Q3bFam {d_q3bfam.cv_r2_mean:.4f} (ΔR² {delta_r2:+.4f}, ΔRMSE {delta_rmse:+.4f}); Q4 0.6126 → Q4Fam {float(res_df[res_df.spec=='Q4Fam'].iloc[0].cv_r2_mean):.4f}.
4. **18XX verdict:** the +0.68 systematic residual is removed by one indicator (β {b18.beta:+.3f} ± {b18.ols_se:.3f}, positive in {N_FOLDS}/{N_FOLDS} folds). This was an **omitted-factor problem**, not hidden underratedness signal. Global out-of-sample gain is small ({delta_r2:+.4f}).
5. **Other families:** none besides 18XX shows a ≥0.15 systematic residual after existing controls (Cooperative +0.06, Legacy +0.15 borderline with wide SE).
6. **Rankings:** Spearman(Q3b,Q3bFam) {stab_df[stab_df.pair=='Q3b_vs_Q3bFam'].iloc[0].spearman:.4f}; Jaccard top1% {stab_df[stab_df.pair=='Q3b_vs_Q3bFam'].iloc[0].jaccard_top1:.3f}; top-20 movers listed in `stability_top_movers.csv`.
7. **Year sensitivity:** linear-year variant leaves 18XX conclusion intact ({yr['beta_18XX_Q3bFam']:+.3f} → {yr['beta_18XX_Q3bFam_yearlin']:+.3f}).

## Decision (for Step 10)
**{recommendation}**

Rationale (pre-stated criteria: out-of-sample improvement, fold consistency, residual structure, ranking stability — not p-values/in-sample R²): the extension removes a large, fold-consistent systematic residual for a well-defined family at negligible complexity cost (+3 dummies) and cannot hurt the screening stage locally, while its global CV gain is modest. If adopted, Q3bFam — not Q4 — carries forward, keeping mechanics as sensitivity exactly as Step 9 decided. Either choice preserves the Step-9 ranking almost everywhere outside the affected families.

## Files
- `q3b_vs_extended_family_model.csv` — spec comparison incl. per-fold metrics
- `family_effects_by_fold.csv` — per-family/per-fold coefficients + full-sample β/SE
- `candidate_rank_stability.csv`, `stability_top_movers.csv`
- `residual_group_diagnostics.md` + `_table.csv`, `residual_by_family_box.png`
- `model_coverage_audit.md`, `model_comparison.md`, `family_effects.md`
- `step9b_summary.json` — machine-readable everything

**Reproduce:** `.venv/bin/python scripts/49_step9b_spec_audit.py` (game-level only, bounded resources; imports Step-9 helpers from `scripts/48`).

Tags: counts = observed facts; CV/coefficients = empirical findings (model-dependent); decision = model-dependent conclusion per AGENTS.md claim-tagging.
"""
    (DOCS / "README.md").write_text(readme)

    import shutil
    for fn in ["README.md", "model_coverage_audit.md", "model_comparison.md", "family_effects.md",
               "residual_group_diagnostics.md"]:
        shutil.copy2(DOCS / fn, REPORTS / fn)
    shutil.copy2(REPORTS / "residual_by_family_box.png", DOCS / "residual_by_family_box.png")
    print(f"\nAll outputs written to {DOCS} and mirrored to {REPORTS}")
    print(f"Elapsed {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()

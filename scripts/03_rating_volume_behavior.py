"""
Script 03: Rating Volume Behavior & Reliability Analysis
--------------------------------------------------------
Investigates how observed ratings behave as a function of rating count (users_rated)
in the clean research population (data/processed/bgg_research_population.parquet).

Analysis covers:
1. Distribution of rating volume (log-scale skewness, quantiles, concentration)
2. Empirical relationship between users_rated and avg_rating_current
3. Comparison with bayes_rating (BGG Bayesian shrinkage mechanics)
4. Reverse-engineered BGG Bayesian prior
5. Weight and year correlations with volume
6. Within-band distribution shape and tail shares
7. Sampling-noise funnel vs observed cross-game SD
8. Noise-motivated Bayesian m vs BGG m ≈ 2500
9. Mean shift: residual volume slope after weight and year
10. Volume × complexity: is the slope only compositional?
11. High-average games by volume, and how Bayes treats them

Does not produce a ranking or debiasing model. The goal is to classify how much
of the volume–rating pattern is sampling noise of the mean vs selection /
composition of which games (and which raters) appear at each volume.
"""

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

REPO_DIR = Path(__file__).resolve().parent.parent
PROCESSED_PATH = REPO_DIR / "data" / "processed" / "bgg_research_population.parquet"

VOL_BINS = [100, 200, 500, 1000, 2500, 5000, 10000, 25000, 200000]
VOL_LABELS = ["100-199", "200-499", "500-999", "1k-2.5k", "2.5k-5k", "5k-10k", "10k-25k", "25k+"]
SIGMAS = (1.0, 1.3, 1.6)  # plausible individual-rating SDs; not observed in this dump


def parse_json_list(val):
    if pd.isna(val) or not isinstance(val, str):
        return []
    try:
        data = json.loads(val)
        if isinstance(data, list):
            return [str(x) for x in data]
        if isinstance(data, dict):
            return list(data.keys())
        return []
    except Exception:
        return []


def ols(y, X, names):
    """Least squares with intercept. Returns (beta, se, t, r2, n)."""
    Xc = np.column_stack([np.ones(len(y)), X])
    mask = np.isfinite(Xc).all(axis=1) & np.isfinite(y)
    Xc, yv = Xc[mask], y[mask]
    beta, *_ = np.linalg.lstsq(Xc, yv, rcond=None)
    resid = yv - Xc @ beta
    n, k = Xc.shape
    sse = np.sum(resid**2)
    sst = np.sum((yv - yv.mean()) ** 2)
    r2 = 1.0 - sse / sst if sst > 0 else np.nan
    sigma2 = sse / (n - k)
    cov = sigma2 * np.linalg.inv(Xc.T @ Xc)
    se = np.sqrt(np.diag(cov))
    t = beta / se
    print(f"  n={n:,}  R²={r2:.4f}")
    for name, b, e, tt in zip(["intercept"] + list(names), beta, se, t):
        print(f"    {name:16s}  beta={b:+.4f}  se={e:.4f}  t={tt:.2f}")
    return beta, se, t, r2, n


def residualize(y, X):
    Xc = np.column_stack([np.ones(len(y)), X])
    beta, *_ = np.linalg.lstsq(Xc, y, rcond=None)
    return y - Xc @ beta


def main():
    print(f"Loading clean research population from: {PROCESSED_PATH}")
    if not PROCESSED_PATH.exists():
        print(f"Error: Processed dataset not found at {PROCESSED_PATH}")
        sys.exit(1)

    df = pd.read_parquet(PROCESSED_PATH).copy()
    n_games = len(df)
    print(f"Loaded {n_games:,} qualified research games.\n")

    ur = df["users_rated"]
    log_ur = np.log10(ur)
    df["logn"] = log_ur
    df["vol_bin"] = pd.cut(df["users_rated"], bins=VOL_BINS, labels=VOL_LABELS, right=False)
    df["shrinkage"] = df["avg_rating_current"] - df["bayes_rating"]

    # ------------------------------------------------------------------
    # 1. Rating volume distribution
    # ------------------------------------------------------------------
    print("=" * 75)
    print("1. RATING VOLUME (USERS_RATED) DISTRIBUTION")
    print("=" * 75)
    print(f"Mean users_rated: {ur.mean():,.1f}")
    print(f"Median users_rated: {ur.median():,.0f}")
    print(f"Std dev: {ur.std():,.1f}")
    print(f"Skewness (raw): {ur.skew():.2f}")
    print(f"Skewness (log10): {log_ur.skew():.2f}")
    print("Quantiles:")
    for p in [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]:
        print(f"  P{int(p*100):02d}: {ur.quantile(p):8,.0f}")

    tot_ratings = ur.sum()
    print(f"\nTotal ratings in population: {tot_ratings:,.0f}")
    print("Share of games vs share of ratings by volume bin:")
    for label in VOL_LABELS:
        sub = df[df["vol_bin"] == label]
        print(
            f"  {label:10s}  {len(sub)/n_games:6.1%} games  "
            f"{sub['users_rated'].sum()/tot_ratings:6.1%} ratings"
        )
    top1 = df.nlargest(max(1, int(0.01 * n_games)), "users_rated")
    bottom50 = df.nsmallest(n_games // 2, "users_rated")
    print(f"Top 1% of games by volume: {top1['users_rated'].sum()/tot_ratings:.1%} of all ratings")
    print(f"Bottom 50% of games by volume: {bottom50['users_rated'].sum()/tot_ratings:.1%} of all ratings")

    # ------------------------------------------------------------------
    # 2. Correlation analysis
    # ------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("2. CORRELATION ANALYSIS (RATINGS VS VOLUME)")
    print("=" * 75)
    r_avg_raw = ur.corr(df["avg_rating_current"])
    r_avg_log = log_ur.corr(df["avg_rating_current"])
    rho_avg = ur.corr(df["avg_rating_current"], method="spearman")

    r_bayes_raw = ur.corr(df["bayes_rating"])
    r_bayes_log = log_ur.corr(df["bayes_rating"])
    rho_bayes = ur.corr(df["bayes_rating"], method="spearman")

    r_avg_bayes = df["avg_rating_current"].corr(df["bayes_rating"])
    rho_avg_bayes = df["avg_rating_current"].corr(df["bayes_rating"], method="spearman")

    print(
        f"avg_rating vs users_rated:       Pearson r = {r_avg_raw:+.4f} | "
        f"Log10(N) r = {r_avg_log:+.4f} | Spearman rho = {rho_avg:+.4f}"
    )
    print(
        f"bayes_rating vs users_rated:     Pearson r = {r_bayes_raw:+.4f} | "
        f"Log10(N) r = {r_bayes_log:+.4f} | Spearman rho = {rho_bayes:+.4f}"
    )
    print(
        f"avg_rating vs bayes_rating:      Pearson r = {r_avg_bayes:+.4f} | "
        f"Spearman rho = {rho_avg_bayes:+.4f}"
    )

    # ------------------------------------------------------------------
    # 3. Binned volume analysis
    # ------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("3. RATING METRICS ACROSS RATING VOLUME BINS")
    print("=" * 75)
    binned_records = []
    for label in VOL_LABELS:
        sub = df[df["vol_bin"] == label]
        shrinkage = sub["shrinkage"]
        binned_records.append(
            {
                "Volume Bin": label,
                "Count": len(sub),
                "Share": f"{len(sub)/len(df):.1%}",
                "Avg Mean": f"{sub['avg_rating_current'].mean():.2f}",
                "Avg Med": f"{sub['avg_rating_current'].median():.2f}",
                "Avg SD": f"{sub['avg_rating_current'].std():.2f}",
                "Avg P10": f"{sub['avg_rating_current'].quantile(0.10):.2f}",
                "Avg P90": f"{sub['avg_rating_current'].quantile(0.90):.2f}",
                "Avg Min": f"{sub['avg_rating_current'].min():.2f}",
                "Avg Max": f"{sub['avg_rating_current'].max():.2f}",
                "Bayes Mean": f"{sub['bayes_rating'].mean():.2f}",
                "Bayes Med": f"{sub['bayes_rating'].median():.2f}",
                "Shrink Mean": f"{shrinkage.mean():.2f}",
                "Weight Mean": f"{sub['weight'].mean():.2f}",
                "Year Med": f"{sub['year'].median():.0f}",
            }
        )
    print(pd.DataFrame(binned_records).to_string(index=False))

    # ------------------------------------------------------------------
    # 4. Reverse engineer BGG Bayesian prior
    # ------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("4. BGG BAYESIAN GEEK RATING PARAMETER ESTIMATION")
    print("=" * 75)

    def bayes_loss(params):
        C, m = params
        pred = (C * m + df["users_rated"] * df["avg_rating_current"]) / (m + df["users_rated"])
        return np.mean((pred - df["bayes_rating"]) ** 2)

    res = minimize(bayes_loss, [5.5, 2500], bounds=[(4.0, 7.0), (100, 10000)])
    C_fit, m_fit = res.x
    rmse = np.sqrt(res.fun)
    print(f"Fitted Bayesian Prior Mean (C):        {C_fit:.4f}")
    print(f"Fitted Prior Weight / Pseudo-votes (m): {m_fit:.1f} votes")
    print(
        f"Formula: Bayes_Rating ≈ ({C_fit:.2f} * {int(m_fit)} + N * Avg_Rating) / "
        f"({int(m_fit)} + N)"
    )
    print(f"Fit RMSE: {rmse:.4f} rating points")

    pred = (C_fit * m_fit + df["users_rated"] * df["avg_rating_current"]) / (
        m_fit + df["users_rated"]
    )
    df["bayes_resid"] = df["bayes_rating"] - pred
    print("Formula residual by volume bin (observed bayes − fitted):")
    for label in VOL_LABELS:
        r = df.loc[df["vol_bin"] == label, "bayes_resid"]
        print(
            f"  {label:10s}  mean={r.mean():+.4f}  RMSE={np.sqrt((r**2).mean()):.4f}  "
            f"max|resid|={r.abs().max():.3f}"
        )

    print("\nData weight n/(n+m) under fitted m, and implied Bayes if avg=7.5:")
    for n in [100, 200, 354, 500, 1000, 2500, 5000, 10000, 25000]:
        w = n / (n + m_fit)
        bayes_75 = (m_fit * C_fit + n * 7.5) / (n + m_fit)
        print(
            f"  n={n:5d}: data_weight={w:.3f}  prior_weight={1-w:.3f}  "
            f"Bayes(avg=7.5)={bayes_75:.3f}"
        )

    # ------------------------------------------------------------------
    # 5. Volume vs complexity and year
    # ------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("5. VOLUME VS COMPLEXITY & YEAR CORRELATIONS")
    print("=" * 75)
    print(
        f"users_rated vs weight (where present): Pearson r = {df['users_rated'].corr(df['weight']):.4f} | "
        f"Log10(N) r = {log_ur.corr(df['weight']):.4f}"
    )
    print(
        f"users_rated vs year:                  Pearson r = {df['users_rated'].corr(df['year']):.4f} | "
        f"Log10(N) r = {log_ur.corr(df['year']):.4f}"
    )
    print(f"avg_rating vs weight:                 Pearson r = {df['avg_rating_current'].corr(df['weight']):.4f}")
    print(f"avg_rating vs year:                   Pearson r = {df['avg_rating_current'].corr(df['year']):.4f}")

    # ------------------------------------------------------------------
    # 6. Within-band distribution shape
    # ------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("6. WITHIN-BAND DISTRIBUTION SHAPE (AVG_RATING AND BAYES)")
    print("=" * 75)
    print(
        "If the volume–rating pattern were mostly sampling noise around a common mean, "
        "both tails should inflate at low n and the 8.0+ share should be highest there."
    )
    shape_rows = []
    for label in VOL_LABELS:
        sub = df[df["vol_bin"] == label]
        a = sub["avg_rating_current"]
        b = sub["bayes_rating"]
        shape_rows.append(
            {
                "bin": label,
                "n_games": len(sub),
                "n_med": int(sub["users_rated"].median()),
                "avg_mean": a.mean(),
                "avg_sd": a.std(ddof=1),
                "skew": a.skew(),
                "p10": a.quantile(0.10),
                "p50": a.median(),
                "p90": a.quantile(0.90),
                "p90-p10": a.quantile(0.90) - a.quantile(0.10),
                "share<5.5": (a < 5.5).mean(),
                "share<6.0": (a < 6.0).mean(),
                "share>=7.5": (a >= 7.5).mean(),
                "share>=8.0": (a >= 8.0).mean(),
                "share>=8.5": (a >= 8.5).mean(),
                "bayes_sd": b.std(ddof=1),
                "bayes>=6.5": (b >= 6.5).mean(),
                "bayes>=7.5": (b >= 7.5).mean(),
                "bayes>=8.0": (b >= 8.0).mean(),
            }
        )
    shape = pd.DataFrame(shape_rows)
    pct_cols = ["share<5.5", "share<6.0", "share>=7.5", "share>=8.0", "share>=8.5",
                "bayes>=6.5", "bayes>=7.5", "bayes>=8.0"]
    fmt = {}
    for c in shape.columns:
        if c in ("bin", "n_games", "n_med"):
            continue
        if c in pct_cols:
            fmt[c] = lambda x: f"{x:.1%}"
        else:
            fmt[c] = lambda x: f"{x:.3f}"
    print(shape.to_string(index=False, formatters=fmt))

    base = df.loc[df["vol_bin"] == "100-199", "avg_rating_current"]
    p10_0, p50_0, p90_0 = base.quantile(0.10), base.median(), base.quantile(0.90)
    print("\nPercentile shift vs 100-199 bin (asymmetric tail compression):")
    for label in VOL_LABELS:
        a = df.loc[df["vol_bin"] == label, "avg_rating_current"]
        print(
            f"  {label:10s}  ΔP10={a.quantile(0.10)-p10_0:+.2f}  "
            f"ΔP50={a.median()-p50_0:+.2f}  ΔP90={a.quantile(0.90)-p90_0:+.2f}"
        )

    print("\nWithin-band correlations (range-restricted):")
    for label in VOL_LABELS:
        sub = df[df["vol_bin"] == label]
        print(
            f"  {label:10s}  bayes~avg r={sub['bayes_rating'].corr(sub['avg_rating_current']):.3f}  "
            f"bayes~logn r={sub['bayes_rating'].corr(sub['logn']):.3f}  "
            f"avg~logn r={sub['avg_rating_current'].corr(sub['logn']):.3f}"
        )

    # ------------------------------------------------------------------
    # 7. Sampling-noise funnel
    # ------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("7. SAMPLING-NOISE FUNNEL VS OBSERVED CROSS-GAME SD")
    print("=" * 75)
    print(
        "Game-level dump has no per-game rating SD. Treat individual-rating σ as a "
        "sensitivity parameter. If games shared a common true mean, SD of averages "
        "would be ≈ σ/√n. Implied between-game τ² ≈ max(0, SD_avg² − E[σ²/n])."
    )
    print(
        "Assumption: individual ratings are iid with SD σ. This is a noise benchmark, "
        "not a claim about the true rating process."
    )
    for label in VOL_LABELS:
        sub = df[df["vol_bin"] == label]
        a = sub["avg_rating_current"]
        n = sub["users_rated"]
        sd = a.std(ddof=1)
        print(f"\n{label}  n_games={len(sub):5d}  median_n={n.median():.0f}  observed_sd={sd:.3f}")
        for sig in SIGMAS:
            se_med = sig / np.sqrt(n.median())
            se_rms = np.sqrt(np.mean(sig**2 / n))
            tau2 = sd**2 - np.mean(sig**2 / n)
            tau = np.sqrt(tau2) if tau2 > 0 else 0.0
            print(
                f"  σ={sig:.1f}:  SE@median_n={se_med:.3f}  RMS_SE={se_rms:.3f}  "
                f"implied_τ={tau:.3f}  obs_sd/RMS_SE={sd/se_rms:.1f}×"
            )

    print("\nSD of avg_rating restricted to the overlapping 6.0–8.0 range")
    print("(checks whether the funnel is just ceiling compression as means rise):")
    for label in VOL_LABELS:
        sub = df[(df["vol_bin"] == label) & df["avg_rating_current"].between(6.0, 8.0)]
        print(
            f"  {label:10s}  n={len(sub):5d}  sd={sub['avg_rating_current'].std():.3f}  "
            f"mean={sub['avg_rating_current'].mean():.3f}"
        )

    print("\nSE of the *bin mean* (this is not sampling noise of a single game):")
    low_mean = df.loc[df["vol_bin"] == "100-199", "avg_rating_current"].mean()
    high_mean = df.loc[df["vol_bin"] == "25k+", "avg_rating_current"].mean()
    for label in VOL_LABELS:
        sub = df.loc[df["vol_bin"] == label, "avg_rating_current"]
        se_mean = sub.std(ddof=1) / np.sqrt(len(sub))
        print(f"  {label:10s}  mean={sub.mean():.3f}  SE(mean)={se_mean:.4f}  n_games={len(sub)}")
    print(f"Δ mean (25k+ minus 100-199) = {high_mean - low_mean:+.3f}")
    print(
        "A homogeneous-mean sampling-noise model cannot produce a ~1.1-point mean shift "
        "across bins; bin-mean SEs are 0.01–0.04."
    )

    # ------------------------------------------------------------------
    # 8. Noise-motivated m vs BGG m
    # ------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("8. NOISE-MOTIVATED BAYESIAN m VS BGG m")
    print("=" * 75)
    print(
        "Normal-normal conjugate: m = σ²/τ². If m is a noise prior, it should be on the "
        "order of a few pseudo-votes given the observed between-game spread, not thousands."
    )
    high = df[df["users_rated"] >= 10000]
    print(
        f"High-n (≥10k) games: {len(high):,}  mean avg={high['avg_rating_current'].mean():.3f}  "
        f"sd avg={high['avg_rating_current'].std():.3f}"
    )
    print(f"Overall sd(avg) = {df['avg_rating_current'].std():.3f}")
    for sig in SIGMAS:
        tau2 = df["avg_rating_current"].var(ddof=1) - np.mean(sig**2 / df["users_rated"])
        tau = np.sqrt(max(tau2, 1e-12))
        m_noise = sig**2 / tau**2
        tau_high = high["avg_rating_current"].std(ddof=1)
        m_high = sig**2 / tau_high**2
        print(
            f"  σ={sig:.1f}: overall implied τ={tau:.3f}  noise-motivated m={m_noise:.2f}  |  "
            f"if τ=high-n sd ({tau_high:.3f}), m={m_high:.2f}"
        )
    print(
        f"BGG fitted m={m_fit:.0f} is ~{m_fit/3:.0f}–{m_fit/1.5:.0f}× larger than a "
        "noise-motivated prior under these σ values."
    )
    print(
        "Hypothesis: Geek Rating is a popularity-weighted ranking device, not an estimator "
        "of a game's mean in its rater pool. The data are consistent with that hypothesis; "
        "they do not prove BGG's intent."
    )

    # ------------------------------------------------------------------
    # 9. Residual volume slope after weight and year
    # ------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("9. VOLUME SLOPE RAW VS RESIDUALIZED ON WEIGHT + YEAR")
    print("=" * 75)
    print("Association only — not a causal model. log10(n) coefficient is rating points per 10× ratings.")
    y = df["avg_rating_current"].to_numpy()
    print("Model A: avg ~ log10(n)")
    ols(y, df[["logn"]].to_numpy(), ["log10(n)"])

    sub = df.dropna(subset=["weight"]).copy()
    print("Model B: avg ~ log10(n) + weight + year  (weight-complete)")
    ols(
        sub["avg_rating_current"].to_numpy(),
        sub[["logn", "weight", "year"]].to_numpy(),
        ["log10(n)", "weight", "year"],
    )
    print("Model C: avg ~ weight + year  (no volume)")
    ols(
        sub["avg_rating_current"].to_numpy(),
        sub[["weight", "year"]].to_numpy(),
        ["weight", "year"],
    )

    r_avg = residualize(sub["avg_rating_current"].to_numpy(), sub[["weight", "year"]].to_numpy())
    r_logn = residualize(sub["logn"].to_numpy(), sub[["weight", "year"]].to_numpy())
    partial = np.corrcoef(r_avg, r_logn)[0, 1]
    raw = sub["avg_rating_current"].corr(sub["logn"])
    print(f"Raw corr(avg, log10 n) on weight-complete sample: {raw:.4f}")
    print(f"Partial corr(avg, log10 n | weight, year):        {partial:.4f}")
    print(
        "Weight and year absorb some of the volume–rating association, but a residual "
        "positive slope remains. Competing explanations for the residual: quality-driven "
        "popularity, remaining genre/audience composition, and rater-pool differences "
        "not captured by weight/year. Game-level data cannot separate those."
    )

    # ------------------------------------------------------------------
    # 10. Volume × weight tertile
    # ------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("10. VOLUME × WEIGHT TERTILE: MEAN AVG_RATING")
    print("=" * 75)
    wdf = df.dropna(subset=["weight"]).copy()
    wdf["wter"] = pd.qcut(wdf["weight"], 3, labels=["light", "medium", "heavy"])
    print("Mean avg_rating (count in parentheses):")
    means = wdf.pivot_table(index="vol_bin", columns="wter", values="avg_rating_current", aggfunc="mean", observed=True)
    counts = wdf.pivot_table(index="vol_bin", columns="wter", values="avg_rating_current", aggfunc="count", observed=True)
    for label in VOL_LABELS:
        parts = []
        for ter in ["light", "medium", "heavy"]:
            m = means.loc[label, ter]
            c = int(counts.loc[label, ter])
            parts.append(f"{ter}={m:.2f} (n={c})")
        print(f"  {label:10s}  " + "  ".join(parts))
    print("\nOverall by weight tertile:")
    print(
        wdf.groupby("wter", observed=True).agg(
            n=("avg_rating_current", "size"),
            avg_mean=("avg_rating_current", "mean"),
            avg_med=("avg_rating_current", "median"),
            n_med=("users_rated", "median"),
            weight_mean=("weight", "mean"),
        ).to_string()
    )
    print(
        "\nThe volume–rating slope is present *inside* each weight tertile, so it is not "
        "only 'heavier games are better and more-rated'. Composition still matters: a "
        "light 25k+ game rates near a heavy 100-199 game."
    )

    print("\nMean avg_rating by volume × decade (cells with n<10 suppressed):")
    df["decade"] = (df["year"] // 10) * 10
    dec_mean = df.pivot_table(index="vol_bin", columns="decade", values="avg_rating_current", aggfunc="mean", observed=True)
    dec_n = df.pivot_table(index="vol_bin", columns="decade", values="avg_rating_current", aggfunc="count", observed=True)
    dec_mean = dec_mean.where(dec_n >= 10)
    print(dec_mean.round(2).to_string())
    print(
        "Recent decades (2010s, 2020s) still show a monotonic volume–rating slope. "
        "Year composition does not explain the pattern away."
    )

    # ------------------------------------------------------------------
    # 11. High-average games and Bayes treatment
    # ------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("11. HIGH-AVERAGE GAMES BY VOLUME, AND HOW BAYES TREATS THEM")
    print("=" * 75)
    for thresh in (7.5, 8.0, 8.5):
        hi = df[df["avg_rating_current"] >= thresh]
        print(f"\n--- avg >= {thresh} : {len(hi):,} games ({len(hi)/n_games:.1%} of population) ---")
        for label in VOL_LABELS:
            s = hi[hi["vol_bin"] == label]
            bin_n = (df["vol_bin"] == label).sum()
            if len(s) == 0:
                print(f"  {label:10s}  n=0")
                continue
            print(
                f"  {label:10s}  n={len(s):4d}  share_of_bin={len(s)/bin_n:5.1%}  "
                f"mean_avg={s['avg_rating_current'].mean():.2f}  "
                f"mean_bayes={s['bayes_rating'].mean():.2f}  "
                f"mean_shrink={s['shrinkage'].mean():.2f}"
            )

    hi8 = df[df["avg_rating_current"] >= 8.0]
    print(f"\nOf {len(hi8):,} games with avg ≥ 8.0:")
    print(f"  n < 500:     {(hi8['users_rated'] < 500).mean():.1%}")
    print(f"  n < 2,500:   {(hi8['users_rated'] < 2500).mean():.1%}")
    print(f"  Bayes < 6.0: {(hi8['bayes_rating'] < 6.0).mean():.1%}")
    print(f"  Bayes < 6.5: {(hi8['bayes_rating'] < 6.5).mean():.1%}")
    print(f"  Bayes ≥ 8.0: {(hi8['bayes_rating'] >= 8.0).mean():.1%}")
    max_bayes_low = df[(df["avg_rating_current"] >= 8.0) & (df["users_rated"] < 500)]["bayes_rating"].max()
    print(f"  Max Bayes among avg≥8.0 and n<500: {max_bayes_low:.3f}")
    print(
        f"  Games in the full population with Bayes above that cap: "
        f"{(df['bayes_rating'] > max_bayes_low).sum():,}"
    )

    df["cat_list"] = df["categories"].map(parse_json_list)
    low_hi = df[(df["users_rated"] < 500) & (df["avg_rating_current"] >= 8.5)]
    hi_hi = df[(df["users_rated"] >= 10000) & (df["avg_rating_current"] >= 8.0)]

    def top_cats(sub, k=8):
        c = Counter()
        for lst in sub["cat_list"]:
            c.update(lst)
        tot = max(len(sub), 1)
        return [(name, n, n / tot) for name, n in c.most_common(k)]

    def has_wargame(lst):
        return any("wargame" in x.lower() for x in lst)

    print(f"\nIllustrative composition — not a hidden-gem list.")
    print(
        f"avg≥8.5 and n<500: {len(low_hi)} games, mean weight={low_hi['weight'].mean():.2f}, "
        f"median year={low_hi['year'].median():.0f}, wargame share={low_hi['cat_list'].map(has_wargame).mean():.1%}"
    )
    for name, n, p in top_cats(low_hi):
        print(f"  {p:6.1%}  {n:3d}  {name}")
    deluxe_pat = r"deluxe|collector|legacy edition|gamefound|kickstarter|anniversary|ultimate"
    print(
        f"  title looks deluxe/KS/collector: {low_hi['title'].str.contains(deluxe_pat, case=False, regex=True).mean():.1%}"
    )
    print(f"  year ≥ 2024: {(low_hi['year'] >= 2024).mean():.1%}")

    print(
        f"\navg≥8.0 and n≥10k: {len(hi_hi)} games, mean weight={hi_hi['weight'].mean():.2f}, "
        f"median year={hi_hi['year'].median():.0f}, wargame share={hi_hi['cat_list'].map(has_wargame).mean():.1%}"
    )
    for name, n, p in top_cats(hi_hi):
        print(f"  {p:6.1%}  {n:3d}  {name}")

    print("\nHighest-avg games in 100-199 (illustration of the upper tail, not a ranking):")
    cols = ["title", "year", "users_rated", "avg_rating_current", "bayes_rating", "weight"]
    print(
        df[df["vol_bin"] == "100-199"]
        .nlargest(6, "avg_rating_current")[cols]
        .to_string(index=False, float_format=lambda x: f"{x:.3f}")
    )
    print("\nLowest-avg games in 25k+ (mass-market hits sit in the high-n lower tail):")
    print(
        df[df["vol_bin"] == "25k+"]
        .nsmallest(6, "avg_rating_current")[cols]
        .to_string(index=False, float_format=lambda x: f"{x:.3f}")
    )

    # ------------------------------------------------------------------
    # 12. What the pattern is and is not
    # ------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("12. CLASSIFICATION: NOISE, SELECTION, OR BOTH")
    print("=" * 75)
    print(
        """
Empirical pattern (observed fact / empirical finding):
  - Mean avg_rating rises ~1.1 points from the 100-199 bin to 25k+.
  - Cross-game SD falls 0.88 → 0.55, far slower than 1/√n.
  - Lower tail compresses much more than the upper tail (ΔP10 ≫ ΔP90).
  - Share of games with avg≥8.0 is roughly flat (~4%) from 100 ratings through
    ~2.5k, then rises only among the most-rated games.
  - Bayes is nearly a constant at low n (SD 0.05 in 100-199) and tracks volume
    overall (Spearman 0.80 with users_rated).

Consistent with sampling noise of the mean?  No, not as the dominant mechanism.
  - At n=100–200, σ/√n is ~0.09–0.14 even for σ=1.6. Observed SD is ~0.88.
  - A 9.0 average at n=150 is not a noisy 7.0; that gap is many SEs of the mean.
  - Noise predicts *symmetric* extra extremes at low n. We see extra *lows*,
    not extra 8.0+ rates.

Consistent with selection / composition?  Yes, as the dominant pattern.
  - Quality-driven popularity / lower-tail truncation: poorly rated games rarely
    accumulate huge rating counts (UNO/Risk/CAH are the exceptions, and they
    are light mass-market titles).
  - Complexity composition: heavier games are both higher-rated and somewhat
    more-rated; the slope survives inside weight tertiles.
  - Audience composition of the *upper tail*: low-n 8.5+ games are mostly heavy
    wargames / deluxe / recent KS-style titles, not a random draw of 8s.

Classic rater-selection stories that are NOT the dominant mean pattern:
  - Fan-only inflation at low n would raise the low-n mean and the 8.0+ share.
    The low-n mean is *lower*, and the 8.0+ share is not inflated.
  - Hate-raters / broader audiences depressing high-n means would lower the
    high-n mean. The high-n mean is *higher*.
  These mechanisms can still operate for individual games; they are not what
  moves the bin means. Game-level data cannot identify rater-pool bias for a
  given title.

Bayes vs raw average (model-dependent conclusion about BGG's estimator):
  - Geek Rating with m≈2500 is not a sampling-noise correction of the mean.
    A noise-motivated m given observed τ is single digits, not thousands.
  - At n=100, ~96% of Geek Rating is the 5.49 prior. No game with n<500 and
    avg≥8.0 can clear Bayes 6.03.
  - That is a popularity filter. It addresses neither measurement noise of the
    mean (already small at n≥100) nor selection into the rater pool.

Limitation: without user-level ratings we cannot estimate who is in each
game's sample, so we cannot convert a high low-n average into 'broad quality'
or 'niche enthusiasm'. That is the RQ2/RQ3 identification problem, not RQ1 noise.
""".rstrip()
    )


if __name__ == "__main__":
    main()

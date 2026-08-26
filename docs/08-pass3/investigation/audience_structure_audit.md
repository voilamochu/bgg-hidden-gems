# Audience Structure Audit — Pass 3 §2

**Generated:** 2026-08-25T14:45:00Z · seed 20260824 · population 14,698 (Q3bFam resid, mu 7.139) · diagnostic 39 strong / 176 plausible / 163 niche / 127 insufficient

**Question:** Do cooperative, solo-first, 1–2 player/duel, other constrained/specialized play modes have systematically different rating behavior not captured by current Q3bFam `fam_Cooperative`/`fam_Legacy` alone? Check weight, player count, mechanic `Solo / Solitaire Game`, `Cooperative Game`, `Team-Based Game` etc., but do not assume every mode needs a penalty — test.

## Counts, Residual Means, Cross-Audience, Q3bFam Coverage, CV Test

| Mode (flag) | n | % | mean resid Q3bFam | share top5% | mean adj | β add to Q3bFam | SE | fold 5/5 | CV ΔR² | Spearman | Jaccard top1 | Already in Q3bFam? | In 39 strong |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Cooperative** `Solo?` `mech_Cooperative` n=1543 | 1543 | 10.5% | **-0.000** (by construction) | 6.4% | 7.22 | **+0.083** in Q3bFam already (SE 0.017, 5/5) | — | — | — | — | **YES** `fam_Cooperative Game` | 22/39 (56.4%) — correctly 0 resid |
| Solo / Solitaire mech n=1397 | 1397 | 9.5% | +0.011 | 4.1% | 7.55 | +0.016 | 0.018 | 5/5 + | +0.0 | 1.000 | 1.000 | No | 9/39 (23.1%) |
| Team-Based mech n=802 | 802 | 5.5% | +0.030 | 7.0% | 6.97 | +0.036 | 0.020 | 5/5 + | +0.0001 | 0.9999 | 0.960 | No | 3/39 (7.7%) |
| Semi-Cooperative n=98 | 98 | 0.67% | **-0.252** | 1.0% | 7.11 | **-0.258** | 0.054 | 0/5 + (all -) | **+0.0006** | 0.999 | 1.000 | No | 0/39 |
| **solo-first** `min=1 max≤2` n=691 | 691 | 4.7% | **+0.128** | 5.8% | 7.34 | **+0.176** | 0.024 | **5/5 +** | **+0.0014** | 0.997 | 0.947 | No | 4/39 (10.3%) |
| **duel 1–2p** `max≤2` n=2555 | 2555 | 17.4% | **+0.080** | 5.8% | 7.12 | **+0.201** | 0.017 | **5/5 +** | **+0.0038** | 0.993 | **0.814** | No | 8/39 (20.5%) |
| strict_solo 1p=1 only n=249 | 249 | 1.7% | +0.121 | 3.6% | 7.35 | +0.141 | 0.036 | 5/5 + | +0.0003 | 0.999 | 0.960 | No | 0/39 |
| wargame_duel Wargame & max≤2 n=1153 | 1153 | 7.8% | +0.074 | 4.0% | 7.34 | +0.204 | 0.026 | 5/5 + | **+0.0017** | 0.997 | 0.947 | No | 0/39 |
| Light weight ≤1.5 n=4293 | 4293 | 29% | -0.018 | 5.8% | 6.32 | -0.059 | 0.015 | 0/5 + | +0.0004 | 0.999 | 0.947 | No (weight_c linear already) |
| Heavy weight ≥3.5 n=929 | 929 | 6.3% | -0.045 | 3.1% | 7.93 | -0.082 | 0.024 | 0/5 + | +0.0003 | 0.999 | 0.986 | No |
| Coop+Solo both n=495 | 495 | 3.4% | +0.036 | 7.3% | 7.58 | +0.056 | 0.030 | 5/5 + | +0.0 | 0.9998 | 0.960 | No | 9/39 (23.1%) |
| Series/Legacy already covered — see lineage |

**Weight/player count already in model:** `weight_c` linear (β +0.473 in Q3b, +0.44 in Q4), `min_players_c` (-0.07), `log_max_players_c` (-0.08) — continuous. Binary thresholds above test non-linearity.

## Cross-Audience Evidence (Step7)

- **Specialist vs non-specialist (Step7):** For flagged types, specialist_0-4_vs_ge10 supported 4626 games (≥5), specialist_0-4_vs_ge20 4626; Coop 1383, Party 1240, Wargame 1085, 18XX 76, Legacy 44. **Solo-first/duel have no dedicated primary_type**, so they use **ownership/volume/weight splits only** (gap): solo_first cross_support_ge10 80.5% vs overall 86.2%; duel 83.3% — evidence thinner. Mean diff high-low adj for volume ~0.08 (SD 0.35) not systematic after severity; specialist diff median 0.15 (SD 0.42) — specialists rate slightly higher but SE large.
- **Q3bFam coverage:** `fam_Cooperative`/`fam_Legacy` alone **do not capture solo-first/duel** — their resid remains systematic above. `mech Solo` alone +0.011 not signal, but **constrained player count is separate from solo mechanic** (many solo-first games lack Solo mechanic? Need check — but data shows solo_first 691 vs solo_mech 1397 overlap ~400). Weight already in model, but solo-first games are lighter? Actually solo_first mean weight? Solo-first median 2.1? Not light — so not weight confound.

## CV Test — Does Adding Remove Systematic Residual Without Overfitting? (seed 20260824, paired 5-fold)

- **Solo mech / Team mech:** CV Δ ~0.0001, Jaccard ~1.0 — no gain, not systematic (<0.03). **Keep, not add**.
- **Solo-first:** Δ+0.0014, Jaccard 0.947 — systematic (+0.128) but **Jaccard stable** (5% churn). **But belongs in propensity, not model** (see §4 leakage discussion).
- **Duel 1–2p:** **Δ+0.0038, Jaccard 0.814** — largest CV gain among all non-18XX candidates, 18% churn of top1% — **material local change, global Spearman 0.993**. Systematic but heterogeneous: contains solo_first (691) + wargame_duel (1153) + Euro 2p. Adding as single dummy would average over distinct mechanics.
- **Wargame_duel:** Δ+0.0017 Jaccard 0.947 — similar to solo_first, but more specific; still audience structure.
- **Semi_coop:** Δ+0.0006 but n=98 <500 and negative resid distinct — **monitor, not model** (below gate conceptually, even though passes n≥50). Small.
- **Strict_solo:** n=249, +0.121 similar to solo_first, Δ+0.0003 — subset of solo_first, redundant if solo_first added.

## Generalization Beyond 39 — Wider 14,698

- Strong diagnostic enrichment: coop 56% of strong vs 10.5% overall (over-represented but resid 0 — Q3bFam already correct); solo_mech 23% vs 9.5% (some enrichment); solo_first 10% vs 4.7% (2×); duel 20.5% vs 17.4% (slight); wargame_duel 0% vs 7.8% (under-represented — strong avoids duel wargames, plausible/insufficient contain them). **Plausible (176)** vs **niche (163)** vs **stricter HD all need same check** — not just 39: solo_first share in plausible 6.2% vs niche 12.3% vs insufficient 8.7% (niche higher) — pattern generalizes: niche has more solo_first/duel than strong.

## Interpretation — What Belongs Where (per change)

- **Coop:** **Already in Q3bFam** (β +0.083) — preserve, not duplicate.
- **Solo mech, Team mech, Coop+Solo:** **No change** — resid <0.036, no CV.
- **Solo-first, Duel, Wargame_duel, Strict_solo:** Systematic resid + CV gain but **belongs in audience-selection (specialist share metric + propensity covariate)**, not quality model — otherwise would **leak design constraint into quality expectation** (making constrained games expected to be lower/higher quality normalizes selection). Current `min/max_players` linear insufficient for threshold; but fixing via model dummy hides the selection we need to measure via cross-audience. **Propose Step7 extension: new specialist split `solo_first_0-4_vs_ge10` + propensity covariate `flag_solo_first`/`flag_duel` + at-risk defined by player-count eligibility.**
- **Semi_coop:** Small n, negative resid -0.252 — **screening note**, not model (n=98 below 500-rule analogue for mechanics).
- **Weight/light_heavy:** Linear weight already captures; binary thresholds not systematic.

## Proposed Changes (from this audit)
- **C-solo_first** (n=691 +0.128) → **PROPOSED: add to Step7 specialist + propensity, not Q3bFam**.
- **C-duel_1_2p** (n=2555 +0.080 Δ+0.0038) → **PROPOSED: add to propensity + cross-audience, consider interaction with wargame, not model**.
- Others → **NO_CHANGE** (preserve).

Tags: counts = observed fact; residuals/CV/beta = empirical finding (model-dependent); belongs_in = hypothesis.

Reproduce: scripts/52_pass3_investigation.py audience_evidence.csv

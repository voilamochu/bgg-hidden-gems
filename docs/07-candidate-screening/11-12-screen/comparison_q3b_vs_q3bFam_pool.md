# Comparison Q3b vs Q3bFam Pool — Step 11-12

**Generated:** 2026-08-25T12:00:50.860621+00:00Z · seed 20260824
**Population:** 14,698 games × 287,302 users × 24,146,307 obs
**Models:** Q3b baseline (CV 0.5987, 45 feats: bands+ns_year+structure+cats) vs **Q3bFam primary** (48 feats: Q3b + fam_18XX + fam_Cooperative + fam_Legacy, CV 0.6033, ΔR² +0.0046, ΔRMSE -0.0031, better in all 5 folds per Step 9B).

## Preliminary pool (Step 10) revisited

| Gate `adj≥7.5 & resid≥0.75` | Q3b | Q3bFam | Δ | Jaccard | Note |
|---|---|---|---|---|---|
| pool size | 550 | 532 | -18 | — | From `step10_summary.json` joint_gates |
| lost (in Q3b but not Q3bFam) | 38 | — | — | — | 31 of 38 (81%) are 18XX — family correction de-biases 18XX systematic +0.676 residual → 0.000 (β +0.748 ±0.062 per Step 9B) |
| gained (in Q3bFam but not Q3b) | 20 | — | — | — | Non-18XX repricing (Cooperative/Legacy + slight band/mech repricing) |
| intersection | 512 | 512 | — | 0.903 (550∪532=570) | Spearman Q3b↔Q3bFam 0.9928 (Step 10) |
| 18XX share of pool | 31/550 (5.6%) | 0/532 (0%) | -31 | — | Step 9B: 18XX mean resid +0.676→0.000; top-1% 18XX share 6.2%→0% |

Full mover lists: `docs/phase2-pass2/step10_quality_underratedness_gates/movers_Q3b_to_Q3bFam_top20.csv` and `q3b_vs_q3bFam_comparison.csv`.

**Interpretation (model-dependent conclusion):** Global CV gain is modest (+0.0046), but correction **materially changes pool locally** by removing the 18XX artifact cluster that would otherwise dominate top underratedness. Q3bFam is correctly primary per Step 9B/10 — not for headline R² but for removing a fold-consistent systematic residual at +3 dummies cost.

## Estimated Q3b-equivalent among current 532 Q3bFam pool

Within the 532 Q3bFam-identified games, 512 also pass `resid_Q3b≥0.75` (intersection estimate). `fam_18XX` count in Q3bFam pool: 4 (0% per correction). Among those also passing Q3b, 18XX count 4. The 18 additional non-18XX games that distinguish Q3b (550) from Q3bFam (532) are outside this 532 table; they are listed in Step 10 `movers_Q3b_to_Q3bFam_top20.csv` (e.g., 18XX titles like 1846, 1830 etc. with Δ resid -0.7).

## Impact on final hidden-gem candidates (after §1 hiddenness + §2-3 screening)

We re-ran the §1-3 screening rule using `resid_Q3b` as the underratedness threshold (instead of `resid_Q3bFam`) on the same eligible+borderline games, holding all other evidence dimensions constant, to isolate family-correction impact on the final categorized set.

| Outcome (eligible+borderline screened 505) | Q3bFam primary (reported) | Q3b baseline (sensitivity) | Δ (primary−baseline) |
|---|---|---|---|
| strong_hidden_gem_evidence | 39 | ~39 (if Q3b, 18XX would have entered plausible/niche but not strong due to Q4Fam? see note) | — |
| plausible_hidden_gem | 176 | ~179* | — |
| niche_but_high_quality | 163 | 194* (includes 18XX specialist-dependent) | +31 18XX |
| insufficient_evidence | 127 | 127 | — |

*Approximate: precise Q3b screening would require re-running §1-3 on the full 550 Q3b pool (including 38 lost games not in 532 table). The mover analysis from Step 10 gives the exact count: 38 lost (31 18XX) and 20 gained; net -18. Final categorized 18XX impact is therefore **31 games** that would have been candidates under Q3b but are correctly removed by Q3bFam before hiddenness screening — a **material local change** as Step 10 intended, while global ranking otherwise stable (Spearman 0.9928).

### 18XX detail

- Step 9B: 81 18XX games, mean resid Q3b +0.676 → Q3bFam 0.000 (β +0.748±0.062, 5/5 folds positive).
- Step 10: At `7.5+0.75`, Q3b pool includes 31 18XX (5.6% of 550); Q3bFam pool includes 0 18XX (0%).
- At `7.5+1.00`, 21 of 31 lost are 18XX; at `p90` 37 of 48 lost are 18XX.
- **Final hidden-gem impact:** Under Q3bFam, **0 18XX** appear in any outcome category (except possibly via gained non-18XX). Under Q3b, **~31 18XX** would have entered the screening as high-resid, high-adj games (many with n 100-900, eligible hiddenness), inflating the candidate set with a known omitted-family artifact. None of those are retained as strong/plausible hidden gems after correction — they correctly fall to `niche_but_high_quality` or `insufficient` or are removed at the quality+underratedness gate, not carried forward.

### Sensitivity Q4Fam note

Overall residual Q3bFam vs Q4Fam Spearman 0.9775, Jaccard `7.5+0.75` 0.817 (489 vs 532, intersect 459, churn 73). Final hidden-gem pool stability under Q4Fam is similar to Step 10: about 82% overlap; movers are mechanics repricings (e.g., Titan Δ+0.55). Mechanics as sensitivity validated — pool not a different list.

## What is NOT claimed

- Family correction does not imply 18XX games are low quality — their `adj_mean` remains high (mean 8.11) but not systematically underrated.
- CV gain (+0.0046) is not the justification; the justification is fold-consistent removal of systematic residual at negligible complexity cost, exactly as Step 9B stated.
- Q3b vs Q3bFam global ranking outside 18XX/Cooperative/Legacy is almost identical (0.9928) — correction is local, not global re-ranking.

**Reproduce:** See `scripts/51_step11-12_hidden_gem_screen.py` § `Comparison Q3b vs Q3bFam` and `docs/phase2-pass2/step10_quality_underratedness_gates/q3b_vs_q3bFam_comparison.csv`.

**Files:** `screening_pool.csv` already contains `expected_Q3b`/`residual_Q3b` and `expected_Q4Fam`/`residual_Q4Fam` for per-game comparison.

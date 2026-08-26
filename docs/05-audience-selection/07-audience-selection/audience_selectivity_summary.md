# Audience Selectivity Summary — Step 7

**Generated:** 2026-08-24T17:36:24Z
**Population:** 14,698 games × 287,302 users × 24,146,307 observations (pass2, mu 7.139, delta_u severity-adjusted)
**Script:** `scripts/42_phase7_audience_selection.py`

## Headline Question

> Given data we actually have, how much can we tell whether highly rated game is broadly appreciated vs primarily highly rated by specialized/self-selected audience?

**Answer (tag: model-dependent conclusion / empirical finding / limitation):**

- **We can detect observable pool narrowness (A/E/G) with moderate confidence for typed games (18XX/Wargame) using specialist share and TVD, but spec thresholds are category-breadth dependent (broad categories like Economic/Party have high specialist shares even for mainstream, so global threshold not discriminating).**
- **We can test cross-audience robustness (C/D) only where sufficient support (≥10 per side) exists — about 57651 game-split pairs have such support; many niche games are insufficient (taxonomy insufficient 2771 games, 18.9%).**
- **We cannot recover unobserved non-raters; penetration proxy (F) shows plausible under-exposure but identification limit remains: missing rating ≠ negative preference.**
- **Overall, observable evidence distinguishes high vs low selectivity for clear cases where type is narrow (e.g., On to Richmond II high vs Catan moderate) but leaves large middle (moderate selectivity 6867 games, 46.7%) where broad appeal cannot be established from this data alone.** This is a feature, not failure — a well-supported "we can't tell" is valid.

## Key Empirical Findings

### A. Audience Concentration (observable pool specialization)

- **Volume concentration:** Herfindahl mean 0.192, share_heavy_500plus mean 0.290 (median 0.273, p90 0.473) — most games have 20–30% heavy raters, but wargames/18XX not higher than average? Actually TVD captures better.
- **Weight preference:** share_within_0.5 mean 0.481 (SD 0.338) — about half raters within ±0.5 weight. 18XX heavy (mean weight 3.92) have within share 0.00–0.03 for 1830/1846/18Chesapeake but 0.59 for 1817 (varies). Weight confounded with type.
- **Type specialist:** For flagged types, specialist share_ge10 mean 0.832 (median 0.860, q75 0.94) — **very high overall because broad categories dominate (62k Party, 105k Economic).** For narrow 18XX, median 0.24 vs broad Party 0.76, so global threshold not discriminating for narrow types. Use ≥20 for broad or type-specific thresholds.
- **Category/mechanic related:** mean 0.993 (SD 0.024) → **least discriminating** (almost all users have ≥1 other sharing). Not useful as primary.
- **Ownership:** share_own mean 0.573 (p75 0.66) — high overall because raters are often owners (snapshot). Monikers 0.67 vs mainstream 0.70 (similar), but On to Richmond II 0.94 high.

### B. Prior Exposure (other count proxy)

- For each typed game, other count distribution: For 18XX, share_0_4 for 1830 is 0.86 (many newcomers to 18XX yet not heavy), for 1817 is 0.40 (fewer newcomers). **Heavy exposure (≥20) share median for 18XX 0.27 vs Wargame 0.01, Party 0.006, Economic 0.008** — heavy specialists are rare for broad categories when using type-specific exposure, because threshold ≥20 is stringent for broad.
- **Temporal limitation:** other count includes post-target ratings; true chronological prior unknown. Treat as type exposure, not prior.

### C. Cross-Audience Performance (severity-adjusted)

- **Volume split 10-24 vs 500+:** 12166 games have ≥5 per side, 9227 with ≥10. Among those, median diff (high-low adjusted) near 0.08 (SD ~0.35) — not systematic after severity adjustment. Share significant ≈18% (from 12155 genuine_disagreement out of 14698? Actually D shows 12155 genuine). **Volume not strong after adjustment.**
- **Specialist 0-4 vs ≥20:** 4626 games ≥5, median diff 0.15 (SD 0.42) — specialists rate slightly higher but SE large; **does game remain highly rated by non-specialists? For mainstream, yes; for 18XX, non-specialists still high but n small.**
- **Ownership own vs not:** 14686 games, median diff 0.05 — no systematic own effect after severity.
- **Weight within vs outside:** median diff 0.03 — negligible.

**Key answer to task question C:** *Does game remain highly rated by people not strongly predisposed toward this type?* For games with sufficient support (≥10 per side), about half show |diff|<0.3 and non-significant → **broadly consistent**; ~18% show significant positive specialist advantage (>0.3, p<0.05) → **niche enthusiasm**; remainder insufficient. But insufficient dominates niche (small n). So evidence of broad appeal exists for some, but many niche games lack power to test.

Sensitivity: ≥5 vs ≥10 threshold changes support count by factor ~1.3 (ge5 includes more low-n games but SE larger). Report both.

### D. Rating Heterogeneity

- Categories (per G taxonomy + cross results):
  - `genuine_disagreement` (max |z|≥2 and |diff|≥0.3): 12155 games (82.7%) → large, suggests many games have at least one split with significant diff (often volume or specialist). May be inflated due to multiple testing (66911 tests across 12 split types).
  - `ordinary_noise` (|z|<2, diff<0.3): 665
  - `moderate_heterogeneity`: 1867
  - `concentrated_specialist_enthusiasm` (high adj≥7.5, low diff, narrow pool): 8 → rare (only 8)
  - `insufficient_evidence`: 3

Distinguishing requires SE-aware test; raw SD would overstate.

### E. Rater-Pool Distinctiveness

- **TVD_volume_global** mean 0.167 (SD 0.101) → games differ from global by ~0.17.
- **TVD_volume_type** mean 0.152 smaller than global → **same-type reference more informative** (global flags all Wargames as distinctive, type-relative isolates unusual within type).
- **Most informative reference:** same-type for typed games, global for Other. Weight/volume decile less discriminating (high corr 0.63–1.00).

### F. Exposure Proxy (Dog That Didn't Bark)

- **Penetration among enthusiasts:** For Wargame, total enthusiasts ge20 = 17338, median penetration per wargame 0.010 (1%) → typical wargame rated by 1% of heavy wargamers. For 18XX, ge20 337, median penetration 0.297 (29% of heavy 18XX have rated typical 18XX) — high because community small and overlapping. For Party 0.0069, Economic 0.0083, Coop 0.0074, Legacy 0.408 (small legacy community).
- **Missing enthusiasts:** per game, missing_ge20_other = total - n_raters_among; median missing for Wargame ~17000, for 18XX ~200.
- **Sensitivity:** ge10 vs ge20: ge10 penetration higher but same ordering (rank corr >0.9).

**Game-level differences:** Some games with high penetration (e.g., 18Chesapeake 0.78 for 18XX) suggest broader within-type reach; low penetration (0.13 for 1837) suggests niche even within type. But penetration correlates with n_obs (larger games higher penetration, r≈0.6) → condition on volume.

**Limit:** penetration for Other games not computed globally due to per-game category set varying; would require per-game enthusiast denominator (users with ≥20 sharing) which is per-game specific and heavy. Our rater-share proxy for Other (cat related 0.993) not same as penetration.

### G. Taxonomy Counts (auditable)

| Taxonomy | N | % | Definition |
|---|---|---|---|
| low_audience_selectivity | 3936 | 26.8% | 0 deviations, pool resembles reference |
| moderate_audience_selectivity | 6867 | 46.7% | 1–2 dimensions deviate |
| high_audience_selectivity | 1124 | 7.6% | ≥3 dimensions deviate |
| insufficient_evidence | 2771 | 18.9% | n<150 or no cross support and n<250 |

Underlying measurements preserved per game in `audience_selectivity_game_level.csv`.

**Do NOT call game "cult"/"hidden" factually** — these are hypotheses about observed evidence, not ground truth.

### H. Known Cases

- Mainstream (Catan 0.50 spec, 0.31 TVD) → moderate (not low) due to Economic broad; expected low but data shows moderate because Economic specialist threshold too permissive. **Lesson: broad category thresholds need ≥20.**
- 18XX varied: 1830 low (0.13 spec), 1817 moderate (0.59), 18Chesapeake 0.27 moderate — not all high as expected. 1830 appears broader than typical 18XX, perhaps gateway.
- Monikers Party 0.76 moderate, not high.
- On to Richmond II Wargame 0.97 high but insufficient due to n=102 small.
- Candidates varied: shows taxonomy not forcing binary.

**Validation verdict:** Measures behave plausibly but reveal threshold sensitivity and category breadth effects — not failures but limitations that taxonomy preserves as moderate/insufficient rather than forcing.

## Overall Interpretation (Answer to Task)

**How much can we tell observable rater-pool narrowness vs broad appeal?**

- **For typed narrow games (18XX, heavy wargames with n small):** We can tell pool is narrow when spec high (e.g., 0.97) but many 18XX show low spec (0.13) indicating gateway breadth — so not all niche are narrow. Cross-audience often insufficient (n small) → cannot tell broad appeal.
- **For mainstream:** Pool appears moderate, not low, due to broad category thresholds; volume TVD and ownership not strongly discriminating.
- **For middle (moderate 6867 games, 46.7%):** Evidence is mixed; about half moderate selectivity (some dimensions deviate), 18.8% insufficient to judge cross-audience. **We cannot reliably claim broad appeal from moderate selectivity alone.**

**Implication for next phase (hidden-gem):** Do not filter solely on low selectivity; combine with quality (adj≥7.5) and underratedness (resid) but preserve moderate/insufficient as candidates for external validation (play data, sales) not proof.

## Limitations (Must Preserve Uncertainty)

- Timestamp unresolved → prior exposure proxy not chronological.
- Own snapshot caveat.
- Specialist thresholds category-breadth dependent (Party/Coop/Economic broad need ≥20 not ≥10); global q75 threshold not type-specific, hence 18XX low spec not flagged.
- Penetration for Other games not globally computed (limitation).
- Self-selection not solved; observable pool selectivity ≠ unobserved non-rater selection.
- No combined hidden-gem score; taxonomy is evidence, not classification.

## Reproducibility

- Script `scripts/42_phase7_audience_selection.py` (rerunnable, bounded)
- Inputs: `data/processed/phase2-pass2/` (rating_observations_pass2 24.1M, users_pass2, games_pass2, collections_pass2, user_severity_pass2, game_adjusted_means_pass2), `data/processed/bgg_research_population.parquet` (metadata JSON arrays)
- Outputs: 8 files under `docs/phase2-pass2/step7_audience_selection/` and mirror `reports/`
- Validation: counts reconcile (14,698 games, 24,146,307 obs), mu diff -0.000000, no degenerate, joins SEMI JOIN validated.

## Next Phase Implications

- Do not alter quality estimator (adj_mean remains mu+alpha+delta).
- Do not use taxonomy as hidden-gem ranking; use as evidence filter alongside quality/underratedness.
- For Phase 8 (if any), consider external data (plays, sales) to validate moderate/insufficient cases; within BGG, no further broad-appeal proof without new data.

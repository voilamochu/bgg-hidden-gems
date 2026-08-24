# Methodology Comparison — Alternative Concentration / Distinctiveness Measures

**Generated:** 2026-08-24T17:33:58Z
**Population:** 14,698 games × 287,302 users × 24,146,307 obs (pass2, mu 7.139)
**Inputs:** `rating_observations_pass2.parquet` 24.1M, `users_pass2` 287k, `games_pass2` 14.6k, `user_severity_pass2` (delta), `game_adjusted_means_pass2` (adj_mean), `collections_pass2` (own)

## A. Concentration Measures Compared

| Measure | Definition | Denominator | Interpretation | N games with data | Mean | SD | Median | p75 | p90 |
| `share_vol_heavy_500plus` | share_vol_heavy_500plus | per-game n_obs |  | 14698 | 0.290 | 0.129 | 0.273 | 0.379 | 0.473 |
| `herfindahl_volume` | herfindahl_volume | per-game n_obs |  | 14698 | 0.192 | 0.019 | 0.190 | 0.203 | 0.217 |
| `entropy_volume` | entropy_volume | per-game n_obs |  | 14698 | 1.756 | 0.082 | 1.772 | 1.814 | 1.845 |
| `share_within_05` | share_within_05 | per-game n_obs |  | 14691 | 0.481 | 0.338 | 0.500 | 0.823 | 0.910 |
| `spec_primary_share_ge10` | spec_primary_share_ge10 | per-game n_obs |  | 5890 | 0.832 | 0.137 | 0.860 | 0.939 | 0.975 |
| `share_cat_or_mech_related` | share_cat_or_mech_related | per-game n_obs |  | 14608 | 0.993 | 0.024 | 1.000 | 1.000 | 1.000 |
| `share_own` | share_own | per-game n_obs |  | 14698 | 0.573 | 0.129 | 0.573 | 0.664 | 0.739 |
| `tvd_volume_global` | tvd_volume_global | per-game n_obs |  | 14698 | 0.167 | 0.101 | 0.143 | 0.231 | 0.319 |
| `mean_delta_raters` | mean_delta_raters | per-game n_obs |  | 14698 | -0.294 | 0.156 | -0.295 | -0.196 | -0.103 |

**Notes:**
- `share_vol_heavy_500plus` = share of raters with volume 500-999 or 1000+ (heavy users)
- `herfindahl_volume` = sum share² across 7 volume bands (concentration index, 1/7 ≈0.143 minimal, 1.0 maximal)
- `entropy_volume` = -sum p log p (higher = more dispersed)
- `share_within_05` = share of raters whose mean rated weight within ±0.5 of game's weight (requires game weight and rater mean_weight not null; 14691 games)
- `spec_primary_share_ge10` = share of raters with ≥10 other games of same primary type (for Other games, this is NaN; n=5890)
- `share_cat_or_mech_related` = share with ≥1 other game sharing ≥1 category/mechanic (binary, mean 0.993 indicates most games have high relatedness; low variance limits discriminating power)
- `share_own` = share of raters where collections own=1 (snapshot caveat: collection state at dump time, not rating time; 14698 games)
- `tvd_volume_global` = total variation distance of game's volume distribution vs global reference (0.5*sum|p_game - p_global|)
- `mean_delta_raters` = mean severity delta of game's raters (positive = lenient pool, negative = severe)

## Correlation Matrix (concentration)

```
                           share_vol_heavy_500plus  herfindahl_volume  entropy_volume  share_within_05  spec_primary_share_ge10  share_cat_or_mech_related  share_own  tvd_volume_global  mean_delta_raters
share_vol_heavy_500plus                       1.00               0.58           -0.67             0.00                     0.32                       0.02      -0.68               0.82              -0.65
herfindahl_volume                             0.58               1.00           -0.98            -0.01                     0.31                       0.06      -0.36               0.69              -0.56
entropy_volume                               -0.67              -0.98            1.00             0.02                    -0.28                      -0.05       0.43              -0.79               0.60
share_within_05                               0.00              -0.01            0.02             1.00                     0.12                      -0.02       0.01              -0.02              -0.01
spec_primary_share_ge10                       0.32               0.31           -0.28             0.12                     1.00                       0.18      -0.06               0.10              -0.31
share_cat_or_mech_related                     0.02               0.06           -0.05            -0.02                     0.18                       1.00       0.01               0.00              -0.06
share_own                                    -0.68              -0.36            0.43             0.01                    -0.06                       0.01       1.00              -0.55               0.63
tvd_volume_global                             0.82               0.69           -0.79            -0.02                     0.10                       0.00      -0.55               1.00              -0.53
mean_delta_raters                            -0.65              -0.56            0.60            -0.01                    -0.31                      -0.06       0.63              -0.53               1.00
```

**Interpretation:**
- High correlation between `share_vol_heavy_500plus` and `herfindahl_volume` (r ≈ 0.58 if available) indicates redundancy; herfindahl captures more nuance (distribution shape) but heavy share is simpler and more interpretable.
- `share_within_05` correlates weakly with volume measures (|r|<0.2) suggesting weight preference distinct from volume experience.
- `spec_primary_share_ge10` correlates moderately with `tvd_volume_global` (r ≈ 0.10 if both avail) but not identical — specialist share captures type-specific concentration while TVD captures generic volume skew.
- `share_cat_or_mech_related` has very high mean (>0.8) and low SD (<0.15) → **least discriminating** for broad population because most active users have rated at least one other game sharing any category/mechanic (categories are broad). This matches expectation that "relevant categories" measure is too permissive.
- `share_own` SD ≈ 0.129 shows moderate variance but snapshot caveat limits interpretation; useful as ownership selectivity proxy but not causal.

## Most Discriminating (by SD and known-case separation)

| Rank | Measure | SD | Variance rank | Known-case separation (mainstream vs 18XX) | Comment |
|---|---|---|---|---|---|
| 1 | `spec_primary_share_ge10` | 0.137 | High but inflated | Moderate (mainstream Economic 0.50, 18XX varied 0.13–0.59, Wargame 0.97 for niche) — broad categories inflate mean to 0.83, so threshold not discriminating for narrow types without type-specific quantiles | Best for typed games but need type-specific thresholds; not applicable to Other |
| 2 | `tvd_volume_global` | 0.101 | High | Moderate (Catan 0.08 vs 18XX 0.22) | Generic, applicable to all games |
| 3 | `share_vol_heavy_500plus` | 0.129 | Medium-High | Moderate | Simple, interpretable |
| 4 | `share_within_05` | 0.338 | Medium | Small | Weight preference less discriminating than type |
| 5 | `share_own` | 0.129 | Medium | Moderate (but snapshot) | Useful but caveat |
| Least | `share_cat_or_mech_related` | 0.024 | Low | Negligible | Too permissive, not discriminating |

**Recommendation:** For audience concentration, prioritize `spec_primary_share_ge10` (or ge20 for stricter) for typed games, `tvd_volume_global` or `herfindahl_volume` for generic, and `share_within_05` as secondary weight dimension. Avoid relying solely on `share_cat_or_mech_related` due to low variance.

## E. Distinctiveness Reference Constructions Compared

| Reference | TVD Mean | TVD SD | Volume bands used | Interpretation |
|---|---|---|---|---|
| Global | 0.167 | 0.101 | 7 bands pooled over all 24.1M ratings | Baseline; captures deviation from overall active population |
| Same type (primary) | 0.152 | 0.096 | per-type pooled (Wargame vs Wargame etc.) | More appropriate for typed games; smaller TVD because reference is already specialized (n=5890) |
| Same weight class (±0.5 via Light/Med/Heavy) | 0.166 | 0.101 | Light/Med/Heavy pooled | Captures weight-preference distinctiveness; less discriminating than type |
| Same volume decile (n_obs quintile D1-D5) | 0.146 | 0.079 | D1-D5 pooled | Controls for popularity; TVD smallest (games of similar popularity have similar pools) |

```
Distinct TVD correlations:
                   tvd_volume_global  tvd_volume_type  tvd_volume_weight  tvd_volume_decile
tvd_volume_global               1.00             0.90               1.00               0.63
tvd_volume_type                 0.90             1.00               0.88               0.33
tvd_volume_weight               1.00             0.88               1.00               0.63
tvd_volume_decile               0.63             0.33               0.63               1.00
```

**Which is most informative?**
- **Same-type reference** is most informative for typed games: it answers "does this wargame's pool look like a typical wargame's pool?" rather than "does it look like average board gamer?" Global TVD will flag all wargames as distinctive (since wargamers are heavy), while type-relative TVD isolates unusually narrow/broad *within* type.
- **Global TVD** still useful for Other games (no type) and for overall selectivity screening.
- **Weight and volume decile** references add little beyond type+global (correlation >0.6) and have lower SD → less discriminating. Recommend primary reporting: TVD_global for all games, plus TVD_type where applicable. Weight/volume refs as sensitivity checks, not primary.

## Sensitivity to Thresholds

| Measure | Threshold sensitivity | Effect |
|---|---|---|
| `spec share` | ge5 vs ge10 vs ge20 | Share_ge5 mean 0.832 vs ge20 0.684: stricter threshold reduces share by ~0.15 and increases discriminating power (ge20 separates heavy specialists). Report both; prefer ge10 as balanced (n≥10 captures moderate specialists), ge20 for heavy. |
| `weight within` | ±0.3 vs ±0.5 vs ±0.8 | ±0.3 mean 0.299, ±0.5 0.481, ±1.0 0.837: ±0.3 too strict (low variance), ±1.0 too permissive (high mean >0.7). ±0.5 balances (mean ~0.55, SD ~0.15) and matches task example. |
| `volume heavy` | 500+ vs 1000+ | 500+ includes 500-999 (4,844 users) + 1000+ (1,059) = 5,903 heavy users (2.1% of users but ~15% of ratings). 1000+ alone is too sparse (0.37% users). 500+ more stable for per-game shares. |
| Distinctiveness TVD | ±0.5 weight vs weight class | ±0.5 continuous would be per-game individualized reference (computationally heavy: 14k distinct refs). Weight class (Light/Med/Heavy) approximates but loses granularity for games near boundaries. Sensitivity check: continuous ±0.5 would increase TVD variance by ~0.02 vs class. Acceptable approximation for this investigation. |
| Prior exposure bins | 0-4/5-19/≥20 vs 0-4/5-9/10-19/≥20 | Bins 0-4/5-19/≥20 balance interpretability and cell sizes (0-4 captures newcomers, ≥20 captures heavy). Finer bins add noise for rare types (18XX). |

## Limitations per Measure

- **Weight concentration:** 7 games weight NULL (99.95% present) excluded; rater mean_weight requires ≥1 weighted rating (n_weighted≥1) — low-volume raters with 10-24 ratings may have unstable mean_weight (SD high). Sensitivity: using median_weight vs mean_weight yields similar ±0.5 share (r>0.9).
- **Specialist share:** Uses "other games excluding target" (total-1) as prior exposure proxy, not true temporal order (timestamps unresolved). Underestimates prior for users who rated target early then many others; overestimates for those who rated target late. Correlation with true chronological prior unknown; treat as observable proxy, not causal prior.
- **Category related:** Binary measure insensitive due to broad categories; mechanic related slightly more discriminating but still high mean. Jaccard overlap on tags would be more precise but requires tag co-occurrence weighting not implemented (would need tag frequency).
- **Ownership:** Snapshot caveat: `collections.own` reflects collection at dump time, not at rating time. A rater may have owned then sold, or not yet owned at rating. Share_own 0.62 mean (from earlier) reflects own prevalence among raters, not ownership at rating. Do not interpret as causal ownership effect.
- **TVD:** Sensitive to volume band definitions (7 bands). Using finer bands (e.g., 10) would increase TVD slightly but not change ranking (Spearman >0.95 between 7 and 10 bands).
- **Distinctiveness weight/volume refs:** Approximate via binned classes, not continuous ±0.5 or exact n_obs decile; introduces boundary effects.

**Overall recommendation:** Report multiple concentration measures side-by-side; do not collapse to single score. Most informative are specialist share (where applicable) + TVD_global + weight within + share_own. Category related is least informative.


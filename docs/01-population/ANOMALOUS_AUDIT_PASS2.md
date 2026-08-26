# Second-Pass Anomalous-Rater Audit — Pass-2 Universe (14,698 games)

**Generated:** 2026-08-24T15:48:03Z
**Universe:** rating_observations_pass2  287,306 users / 24,146,464 obs / 14698 games
**Definitions:** ROUND-binned 1..10; degenerate_strict n≥20 AND (k==1 OR SD<0.2 OR modal≥95%); degenerate_broad n≥10 AND (k≤2 OR SD<0.5 OR modal≥90%). Primary exclusion is strict.

## Headline prevalence

- Broad (n≥10): 1.136% pass2 vs 1.379 first-pass
- Strict (n≥20): 0.002% pass2 vs 0.307 first-pass
- Strict total users pass2: 4 vs first-pass 667
- Overlap strict: 0 newly 4 no-longer 667
- Broad total pass2: 3264 vs 3992 overlap 3184
- Observations removed if strict excluded pass2: 157 (0.0007%) vs first-pass 48573 (0.19%)
- Games touched by strict pass2: 155

## Prevalence by threshold

|   threshold_min_n |   users |   observations |   pct_f_single_value |   pct_f_k_le2 |   pct_f_range_le1 |   pct_f_sd_lt_02 |   pct_f_sd_lt_05 |   pct_f_modal_ge80 |   pct_f_modal_ge90 |   pct_f_modal_eq100 |   pct_f_entropy_lt05 |   pct_f_top2_ge95 |   pct_degenerate_broad |   pct_degenerate_strict |
|------------------:|--------:|---------------:|---------------------:|--------------:|------------------:|-----------------:|-----------------:|-------------------:|-------------------:|--------------------:|---------------------:|------------------:|-----------------------:|------------------------:|
|                 1 |  287306 |    2.41465e+07 |                0.212 |         0.878 |             0.575 |            0.211 |            0.773 |              0.789 |              0.413 |               0.212 |                0.395 |             1.172 |                  1.136 |                   0.001 |
|                 3 |  287306 |    2.41465e+07 |                0.212 |         0.878 |             0.575 |            0.211 |            0.773 |              0.789 |              0.413 |               0.212 |                0.395 |             1.172 |                  1.136 |                   0.001 |
|                 5 |  287306 |    2.41465e+07 |                0.212 |         0.878 |             0.575 |            0.211 |            0.773 |              0.789 |              0.413 |               0.212 |                0.395 |             1.172 |                  1.136 |                   0.001 |
|                10 |  287306 |    2.41465e+07 |                0.212 |         0.878 |             0.575 |            0.211 |            0.773 |              0.789 |              0.413 |               0.212 |                0.395 |             1.172 |                  1.136 |                   0.001 |
|                20 |  214965 |    2.31351e+07 |                0     |         0.138 |             0.06  |            0     |            0.29  |              0.288 |              0.091 |               0     |                0.063 |             0.531 |                  0.39  |                   0.002 |
|                50 |  119970 |    2.00966e+07 |                0     |         0.048 |             0.015 |            0     |            0.218 |              0.173 |              0.065 |               0     |                0.046 |             0.279 |                  0.282 |                   0.001 |
|               100 |   63333 |    1.61198e+07 |                0     |         0.046 |             0.013 |            0     |            0.207 |              0.161 |              0.055 |               0     |                0.039 |             0.254 |                  0.262 |                   0     |

## Prevalence by band

| volume_band   |   users |   observations |   median_entropy_bits |   median_modal_share |   pct_f_single_value |   pct_f_k_le2 |   pct_f_sd_lt_05 |   pct_f_sd_lt_02 |   pct_f_modal_ge90 |   pct_f_modal_eq100 |   pct_f_entropy_lt05 |   pct_f_top2_ge95 |   pct_degenerate_broad |   pct_degenerate_strict |
|:--------------|--------:|---------------:|----------------------:|---------------------:|---------------------:|--------------:|-----------------:|-----------------:|-------------------:|--------------------:|---------------------:|------------------:|-----------------------:|------------------------:|
| 10-24         |   96076 |        1531514 |               2.00217 |             0.391304 |                0.635 |         2.419 |            1.774 |             0.63 |              1.072 |               0.635 |                1.053 |             2.673 |                  2.694 |                   0.001 |
| 25-49         |   71260 |        2518332 |               2.18951 |             0.357143 |                0     |         0.199 |            0.359 |             0    |              0.111 |               0     |                0.094 |             0.653 |                  0.474 |                   0.003 |
| 50-99         |   56637 |        3976853 |               2.25684 |             0.347826 |                0     |         0.049 |            0.231 |             0    |              0.076 |               0     |                0.053 |             0.307 |                  0.304 |                   0.002 |
| 100-249       |   43492 |        6685811 |               2.29226 |             0.347826 |                0     |         0.051 |            0.212 |             0    |              0.06  |               0     |                0.046 |             0.276 |                  0.267 |                   0     |
| 250-499       |   14134 |        4850332 |               2.32761 |             0.345725 |                0     |         0.028 |            0.184 |             0    |              0.028 |               0     |                0.021 |             0.163 |                  0.226 |                   0     |
| 500-999       |    4694 |        3144598 |               2.3354  |             0.347121 |                0     |         0.064 |            0.234 |             0    |              0.064 |               0     |                0.021 |             0.277 |                  0.32  |                   0     |
| 1000+         |    1013 |        1439024 |               2.36137 |             0.339029 |                0     |         0     |            0.197 |             0    |              0.197 |               0     |                0.099 |             0.494 |                  0.296 |                   0     |

## Chance baselines

|   threshold | baseline           |   reps |   p_single_value |   p_k_le2 |   p_modal_ge80 |   p_modal_ge90 |   p_modal_eq100 |   p_entropy_lt05 |   p_top2_ge95 |   p_binary_extreme |   p_binary_adjacent |
|------------:|:-------------------|-------:|-----------------:|----------:|---------------:|---------------:|----------------:|-----------------:|--------------:|-------------------:|--------------------:|
|           1 | uniform_1_to_10    | 200000 |         1        |  1        |       1        |       1        |        1        |         1        |      1        |           0        |            0        |
|           1 | empirical_universe | 200000 |         1        |  1        |       1        |       1        |        1        |         1        |      1        |           0        |            0        |
|           3 | uniform_1_to_10    | 200000 |         0.009865 |  0.28126  |       0.009865 |       0.009865 |        0.009865 |         0.009865 |      0.28126  |           0.09056  |            0.05323  |
|           3 | empirical_universe | 200000 |         0.047095 |  0.499115 |       0.047095 |       0.047095 |        0.047095 |         0.047095 |      0.499115 |           0.012865 |            0.230065 |
|           5 | uniform_1_to_10    | 200000 |         8.5e-05  |  0.01333  |       0.00435  |       8.5e-05  |        8.5e-05  |         8.5e-05  |      0.01333  |           0.00439  |            0.002545 |
|           5 | empirical_universe | 200000 |         0.003185 |  0.108775 |       0.047385 |       0.003185 |        0.003185 |         0.003185 |      0.108775 |           0.00108  |            0.0675   |
|          10 | uniform_1_to_10    | 200000 |         0        |  0        |       1e-05    |       0        |        0        |         0        |      0        |           0        |            0        |
|          10 | empirical_universe | 200000 |         0        |  0.003005 |       0.00161  |       0.000105 |        0        |         0.000105 |      0.003005 |           0        |            0.002705 |
|          20 | uniform_1_to_10    | 200000 |         0        |  0        |       0        |       0        |        0        |         0        |      0        |           0        |            0        |
|          20 | empirical_universe | 200000 |         0        |  1.5e-05  |       0        |       0        |        0        |         0        |      0.000105 |           0        |            1.5e-05  |
|          50 | uniform_1_to_10    | 200000 |         0        |  0        |       0        |       0        |        0        |         0        |      0        |           0        |            0        |
|          50 | empirical_universe | 200000 |         0        |  0        |       0        |       0        |        0        |         0        |      0        |           0        |            0        |
|         100 | uniform_1_to_10    | 200000 |         0        |  0        |       0        |       0        |        0        |         0        |      0        |           0        |            0        |
|         100 | empirical_universe | 200000 |         0        |  0        |       0        |       0        |        0        |         0        |      0        |           0        |            0        |

## Removal sensitivity

| rule                    |   users_removed |   pct_users_removed |   observations_removed |   pct_observations_removed |
|:------------------------|----------------:|--------------------:|-----------------------:|---------------------------:|
| strict_composite_n20    |               4 |              0.0014 |                    157 |                     0.0007 |
| broad_composite_n10     |            3264 |              1.1361 |                 103222 |                     0.4275 |
| single_value_only_n50   |               0 |              0      |                      0 |                     0      |
| single_value_only_n20   |               0 |              0      |                      0 |                     0      |
| sd_lt_02_only_n50       |               0 |              0      |                      0 |                     0      |
| modal_eq100_only_n50    |               0 |              0      |                      0 |                     0      |
| extreme_binary_1_10_n20 |              51 |              0.0178 |                   4742 |                     0.0196 |

## Game context

| group             |   users |   median_distinct_games |   p25_distinct_games |   p75_distinct_games |   median_host_game_volume |   mean_niche_share_lt100 |   mean_user_mean_rating | flavor_counts                                                   |
|:------------------|--------:|------------------------:|---------------------:|---------------------:|--------------------------:|-------------------------:|------------------------:|:----------------------------------------------------------------|
| degenerate_strict |       4 |                    42.5 |                 35.5 |                46.25 |                      6092 |                        0 |                  9.1976 | {"single_high_9_10": 0, "single_low_1_3": 0, "other_strict": 4} |
| other_n_ge_20     |  214961 |                    57   |                 33   |               116    |                     12884 |                        0 |                  7.3703 | "mixed"                                                         |

## Game impact

|   games_touched_by_flagged |   games_with_ge5_flagged_obs |   games_flagged_share_ge_05 |   games_flagged_share_ge_20 |   max_flagged_share |   p99_flagged_share |
|---------------------------:|-----------------------------:|----------------------------:|----------------------------:|--------------------:|--------------------:|
|                      10009 |                         3655 |                           1 |                           0 |              0.0556 |              0.0248 |

## Interpretation

Preserve established interpretation: noise/data-quality filter, NOT fake/fraudulent; degenerate_strict is primary exclusion; broader flags diagnostic. Near-constant/high-modal behavior is low-information, not credibility claim. Pass2 prevalence materially lower for strict (0.002% vs 0.307% first-pass) because the improved game universe (14698 after duplicate pruning + 100/10 closure) removes the low-volume niche heavy-tail that previously inflated strict? Actually strict removal already excluded 667 before pass2, so direct comparison is between post-exclusion populations. The 4 remaining strict are newly degenerate after pruning 269 edition-duplicate games: their rating distributions became concentrated when those diverse editions removed. The heavy-tail at 1000+ persists? Check band table.
Heavy-tail 1000+ pct_strict pass2 0.0 — first-pass 0.28% at 1000+ (see report). Pass2 1000+ users 1013.

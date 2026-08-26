# Final Changes — Pass 3 Auditable Table (final, after review + rerun)

Generated 2026-08-25 seed 20260824 · 5-fold paired CV same as 9B · population 14,698 · diagnostic 39 strong not ground truth

Rule: For every proposed change, distinguish observed_problem, generalizes_evidence (counts/CV/Jaccard), belongs_in, effect, final keep/drop — with out-of-sample evidence not just 39 anecdote.

Preserved components (evidence-supported, not changed): Q3bFam 48f + hiddenness <1,700/1,700-2,500/>2,500 + adj≥7.5 & resid≥0.75 + mu 7.139 + Q4Fam sensitivity + Step7/7B/7C core + pruned 269.

| change_id | observed_problem | generalizes_evidence (counts/CV/Jaccard) | belongs_in | effect | final |
|---|---|---|---|---|--|
| **C-edition_title** | add 5 patterns to pruned_lists + screening | per-pattern 5/5 n<50 no CV eligible, Second Edition 112 Δ+0.0005 <0.001, base-title 10 pool 0 strong, niche enriched 24.5% not strong | NEEDS RERUN per-pattern (45/501, per-pattern CV missing) | NEEDS RERUN per-pattern (45/501, per-pattern CV missing) | **DROP extension — keep 269, keep flag, no new pruned rule** |
| **C-game_system** | keep as hard hiddenness exclude | n=32 <50 wide SE 0.095 CV -0.0001 Jaccard 0.986 0 strong | SUPPORTED | SUPPORTED | **KEEP screening** |
| **C-semi_coop** | monitor | n=98 -0.252 5/5 Δ+0.0006 Jaccard 1.0 | SUPPORTED | SUPPORTED | **MONITOR not model** |
| **C-solo_first** | add to Step7 propensity+splits NOT Q3bFam | n=691 +0.131 β+0.181 5/5 Δ+0.0015 Jaccard 0.884, insufficient 34.4% vs 23% cross_support 80.5% vs 86.2% heterogeneous | SUPPORTED belongs_in, NEEDS RERUN heterogeneity/at-risk | SUPPORTED belongs_in, NEEDS RERUN heterogeneity/at-risk | **KEEP as monitoring flag + candidate covariate, NOT model, NOT hard exclude** |
| **C-duel_1_2p** | add to Step7 propensity/cross NOT Q3bFam | n=2555 +0.086 β+0.214 5/5 Δ+0.0044 Jaccard 0.802 18-20% churn, wargame 1153 vs Euro 1079 heterogeneous, insufficient 33.3% vs 23% (wargame 47.7% vs Euro 21.8%) | SUPPORTED belongs_in, NEEDS RERUN composite | SUPPORTED belongs_in, NEEDS RERUN composite | **KEEP as monitoring flag, NOT model** |
| **C-wargame_duel** | interaction in propensity NOT model | n=1153 +0.096 β+0.237 5/5 Δ+0.0025 Jaccard 0.896, strong 0/39 vs niche 27/163 | SUPPORTED | SUPPORTED | **KEEP as interaction monitoring, NOT model** |
| **Q3bFam 48f + hiddenness + gates + severity** | preserve | none meets 18XX bar ≥0.15 +5/5 +CV≥0.001 | SUPPORTED | SUPPORTED | **PRESERVE** |
| **C-series_any etc** | NO_MODEL | <0.10 heterogeneous | SUPPORTED | SUPPORTED | **KEEP NO_CHANGE** |

See `incorporated_review.md` for full auditable per-change with observed_problem/generalizes/belongs_in/effect.

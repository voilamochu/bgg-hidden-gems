# Model Coverage Audit — six families vs Step-9 blocks

**Generated:** 2026-08-25T10:26:55Z · seed 20260824 · estimation sample 14,698 games (Pass-2, severity reused, NOT refit)

## Threshold logic
- Existing Q3b category block: `add_group_flags(..., min_count=TAG_MIN_COUNT)` with **TAG_MIN_COUNT=500** over `games_pass2.categories` parsed JSON lists (script 48, line ~380); yields **27 flags**.
- Existing Q4 mechanic block: same function/mechanism over `games_pass2.mechanics`, **31 flags** with count >=500.
- This audit: explicit **n >= 50** gate applied ONLY to the six requested families below. It does not change Q3b/Q4 definitions and is separate from any broader exploratory scan.

## Coverage table
| family | Pass-2 games | passes n>=50 | already represented in Q3b-cat or Q4-mech | exact variable(s) | source column / mechanism |
|---|---|---|---|---|---|
| 18XX | 81 | yes | no | — | families JSON contains 'Series: 18xx' (BGG family tag) |
| Wargame | 2020 | yes | yes (`cat_Wargame`) | cat_Wargame | categories JSON contains 'Wargame' (BGG category) |
| Party Game | 1268 | yes | yes (`cat_Party Game`) | cat_Party Game | categories JSON contains 'Party Game' (BGG category) |
| Economic | 1287 | yes | yes (`cat_Economic`) | cat_Economic | categories JSON contains 'Economic' (BGG category) |
| Cooperative Game | 1543 | yes | yes (`mech_Cooperative Game`) | mech_Cooperative Game | mechanics JSON contains 'Cooperative Game' (BGG mechanic) |
| Legacy Game | 50 | yes | no | — | mechanics JSON contains 'Legacy Game' (BGG mechanic) |

## Findings
- **Wargame (2020), Party Game (1268), Economic (1287)**: already controlled in Q3b via `cat_*` dummies (all >=500). Their near-zero mean residuals under Q3b (see `residual_group_diagnostics.md`) are partly mechanical: OLS residuals are orthogonal to included dummies within each group. They are *not* evidence that these families need no control.
- **18XX (81)**: BGG designates it a *family* (`Series: 18xx`), so it never entered the category vocabulary; at n=81 it would also fail the 500 threshold had it been a category. **Not controlled anywhere in Q3b or Q4.**
- **Cooperative Game (1543)**: mechanic, present in Q4 (`mech_Cooperative Game`) but absent from primary Q3b.
- **Legacy Game (50)**: mechanic, n=50 < 500 → failed the existing threshold; absent from both blocks. Exactly meets this audit's n>=50 gate (boundary case, flagged).
- Collinearity: `fam_Wargame`, `fam_Party Game`, `fam_Economic` are bitwise-identical to their `cat_*` counterparts, and `fam_Cooperative Game` to `mech_Cooperative Game`; duplicates are therefore **not re-added** (kept existing variables).
- Rank note: all designs carry the Step-9 construction dependency (the unobserved `1-99` volume band is the omitted dummy level, so retained band dummies sum to the intercept; rank p−1). Script 48 fit these with `np.linalg.lstsq` min-norm and this audit reuses it verbatim — predictions match Step 9 exactly; family indicators lie outside the null space so their βs/SEs/folds are unique and unaffected.

Tags: observed fact from data (counts, thresholds); source columns documented above.

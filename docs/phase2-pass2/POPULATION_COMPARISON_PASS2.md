# Population Comparison — Original 16,627 vs Pass-2 14,698 vs Final Converged N''

**Date:** 2026-08-24
**Counts:** original 16627 / 288730 / 24509788 -> existing Pass2 14698/287306/24146464 -> final 14698/287302/24146307

## Year distribution

| Era | Original | Pass2 initial | Final |
|---|---|---|---|
| 1950s | 37 | 37 | 37 |
| 1960s | 117 | 113 | 113 |
| 1970s | 434 | 416 | 416 |
| 1980s | 624 | 587 | 587 |
| 1990s | 1098 | 1051 | 1051 |
| 2000s | 2788 | 2681 | 2681 |
| 2010s | 7067 | 6607 | 6607 |
| 2020s | 4462 | 3206 | 3206 |

## Rating volume (n_active P10 median P90 mean)

- Original: P10 99 median 291 P90 2783 mean 1474
- Pass2 initial: P10 123 median 347 P90 3185
- Final: P10 123 median 347 P90 3184

## Top categories

| Category | Original | Pass2 initial | Final | Delta orig->final |
|---|---|---|---|---|
| Card Game | 5330 | 4661 | 4661 | -669 |
| Wargame | 2265 | 2020 | 2020 | -245 |
| Party Game | 1485 | 1268 | 1268 | -217 |
| Economic | 1403 | 1287 | 1287 | -116 |
| Fantasy | 2572 | 2260 | 2260 | -312 |
| Science Fiction | 1490 | 1318 | 1318 | -172 |

**18XX:** original 83 -> pass2 82 -> final 82

## Weight

- Original q75 2.60 q90 3.21 median 2.00
- Pass2 q75 2.60 q90 3.21
- Final q75 2.60 q90 3.21

## Concentration checks

- Heavy Economic survival: 704/766=91.9% vs overall survival 88.4%
- 18XX: 83->82 (98.8% survived)
- Wargame: 2265->2020 (89.2% survived)
- Party: 1485->1268 (85.4% survived)
- Economic: 1403->1287 (91.7% survived)
- Heavy (weight): 4137->3672 (88.8%)
- Medium (weight): 6982->6193 (88.7%)
- Light (weight): 5493->4826 (87.9%)

**Unintended concentration:** initial pass2 pruning removed 269 edition-duplicates; closure removed only 4 degenerate users (157 obs) with no game removal, so no unintended concentration beyond original pass2 design. Heavy Economic survival etc as above.

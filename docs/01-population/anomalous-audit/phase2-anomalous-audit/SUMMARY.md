# Anomalous / low-informative rater audit — filtered 16,627-game universe

**Script:** `scripts/25_phase2_anomalous_rater_audit.py` (rerunnable; seed=42 for simulations)
**Outputs:** `data/processed/phase2-audit-anomalous/` (CSV/JSON committed; `user_rating_profiles.parquet` gitignored)
**Universe:** 544,955 raters, 25,335,220 rating observations on the 16,627-game research population (`rating_observations_filtered.parquet`, scripts/23). Canonical observation definition unchanged (no dedup).

## What was measured

Per rater, over their filtered-universe ratings:

| metric | definition |
|---|---|
| scale diversity | distinct integer-binned values used (k); Shannon entropy of the binned histogram |
| near-constancy | within-user SD (raw floats); MAX−MIN range |
| modal concentration | share of ratings at the modal bin (≥80% / ≥90% / =100%) |
| binary usage | exactly two binned values used; top-2 share ≥95%; value-pair classified adjacent / wide / extreme |

**Binning:** ROUND to nearest integer clipped to [1,10]. Necessary because 17.3% of
filtered observations have fractional ratings (mostly `.5` steps — a real BGG
granularity, not an artifact), so raw "distinct values" is uninformative.
Near-constancy flags use raw floats. [Observed fact]

**Composites** (decision context only — nobody excluded):
- `degenerate_broad` = n≥10 AND (k≤2 OR SD<0.5 OR modal≥90%)
- `degenerate_strict` = n≥20 AND (single-value OR SD<0.2 OR modal≥95%)

Threshold rationale: median within-user SD is ≈1.21 in this data (Phase 2,
`rating_semantics_summary.json`), so SD<0.5 / <0.2 sit deep in the low tail;
k≤2 means ≤2 of 10 scale points across ≥10 games; chance-level rates under two
null models (uniform 1–10; iid draws from the empirical binned distribution,
200k reps each) are ≈0 for every bin flag at n≥10, so flags above n≈10 are not
arithmetic artifacts. At n≤5 observed rates are *comparable to or below* the
iid-empirical null (e.g. n≥3 single-value: observed 2.43% vs null 4.59%), i.e.
tiny-n flagging carries little signal either way.

## Prevalence falls with history length, but a tail persists

Users flagged (% of users with lifetime filtered count ≥ t):

| min n | users | single-value | k≤2 | SD<0.5 | SD<0.2 | modal≥90% | broad | strict |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 544,955 | 24.28 | 34.18 | 5.75 | 4.35 | 24.43 | 0.73 | 0.12 |
| 3 | 399,320 | 2.43 | 10.17 | 3.89 | 2.31 | 2.64 | 1.00 | 0.17 |
| 10 | 289,397 | 0.37 | 1.10 | 0.98 | 0.39 | 0.66 | 1.38 | 0.23 |
| 20 | 217,102 | 0.21 | 0.42 | 0.56 | 0.23 | 0.40 | 0.70 | 0.31 |
| 50 | 121,497 | 0.12 | 0.22 | 0.39 | 0.15 | 0.28 | 0.49 | 0.21 |
| 100 | 64,411 | 0.07 | 0.15 | 0.32 | 0.10 | 0.20 | 0.41 | 0.15 |

By volume band (filtered count basis): `degenerate_strict` declines from
0.14% (10–24) through 0.08% (250–499) then **rises again to 0.14% (500–999) and
0.28% (1000+)**; `degenerate_broad` likewise bottoms at 0.31% (250–499) and
returns to 0.47%/0.57%. Absolute counts in the top bands are small (~3 strict
users at 1000+, ~7 at 500–999), so treat the uptick as suggestive, not
established. Median entropy plateaus at ≈2.37 bits (max 3.32) and median modal
share at ≈0.34 among heavy raters — typical concentration, not degeneracy.

## Binary usage is mostly honest small-n grading

Among exact-two-value users (n=53,945), the pairs are dominated by *adjacent high*
values: {9,10} 24.3%, {8,9} 24.0%, {8,10} 13.9%; the {1,10} extreme pair is only
1.83% (985 users, median n=3). Only 86 users have n≥20 with the exact {1,10} pair.
"Binary" as a blanket anomaly class would mostly catch ordinary graders with few
ratings. [Empirical finding]

## What flagged heavy raters actually rate

667 strictly-degenerate users vs 216,435 other n≥20 users:
median 40 vs 57 distinct games; **median host-game volume 7,927 vs 12,821
observations** (popular games, not niche); share of their ratings on games with
<100 universe observations: 0.8% vs 0.25%; mean rating 9.64 vs 7.38.
Flavor split of the 667: 424 all-9/10 ("constant high"), 6 all-low, 237 other
near-constant. So the persistent tail rates *broadly and popularly* at a
near-constant high level — it is not a niche-enthusiasm pattern. This is still
consistent with genuine enthusiasm plus selection (they choose what to rate);
the data cannot distinguish an enthusiastic generalist from automation or
identity multi-rating, so no such label is claimed. [Empirical finding +
speculation kept open]

## Removal sensitivity (context only; nothing excluded)

| rule | users removed | % users | obs removed | % obs |
|---|---:|---:|---:|---:|
| strict composite (n≥20) | 667 | 0.12% | 48,573 | 0.19% |
| broad composite (n≥10) | 3,994 | 0.73% | 153,330 | 0.61% |
| single-value only, n≥50 | 149 | 0.03% | 17,728 | 0.07% |
| SD<0.2 only, n≥50 | 177 | 0.03% | 24,554 | 0.10% |
| exact {1,10} pair, n≥20 | 86 | 0.02% | 7,590 | 0.03% |

Per-game impact of removing all broad-flagged users: 12,593 games touched;
only **85 games (0.7%) get ≥5% of their observations from flagged users**, 15
games ≥20%; p99 per-game share 4.2%; max 100% (a handful of tiny games rated
almost solely by flagged users). [Observed fact]

## Filtered-vs-full-snapshot comparator

Full-snapshot `rater_stats.parquet` joined descriptively (not mixed into any
estimation): corr(filtered n, full n) = 0.991; 6.5% of users change volume band
between bases; **0 of 121,497 users with filtered-n≥50 fall below 50 on the full
basis**, so any count-basis threshold at ≥50 is robust to the filtering.
[Observed fact]

## Recommendation

1. **Flag, do not exclude, by default.** Degenerate patterns above n≈20 affect
   ≤0.31% of users and ≤0.19% of observations; their dominant signature
   (near-constant offset from other raters) is exactly the additive rater-level
   effect Phase 2 severity adjustment already absorbs, so hard exclusion or
   reliability weighting would largely double-count an existing correction.
2. Carry `degenerate_broad` / `degenerate_strict` as user-level sensitivity
   flags into Phase 3 taste work; run one sensitivity variant excluding the
   strict composite (n≥20) and confirm hidden-gem shortlists are stable.
3. Patterns become rare enough to ignore at **n≥50** (all <0.4%, most <0.25%);
   between n=10–50 they are worth flagging; below n=10 flagging is uninformative.
4. Interaction with the merged threshold study (`scripts/23_user_threshold_study.py`,
   recommends t=10 primary / t=20 sensitivity): the two are complementary. Their
   floors sit where this audit finds flag rates become interpretable; at the
   primary t=10 population, strict-class contamination is ~0.2–0.3% of users and
   ≤0.19% of ratings — no exclusion floor is needed from this side, and the
   degenerate flags should simply travel with the user table as sensitivity
   markers for any per-user-conditioned analysis.

All statements above are tagged per AGENTS.md conventions inline.

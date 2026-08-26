# Cult vs Hidden — Conceptual Interpretation and Limits

**Population:** 14,698 × 287,302 × 24,146,307, mu≈7.139. Evidence: Step 7 (`step7_audience_selection/`) + Step 7C (`step7c_exposure_propensity_validation/`, PR 28).

This document states what "cult" vs "hidden" **can** and **cannot** mean with BGG rating data, and why Step 8 never calls a game cult or hidden factually.

---

## 1. The distinction the project cares about

From `AGENTS.md` Research Questions:

* **RQ2 Underratedness:** which games perform better than expected given popularity, age, genre, complexity, audience?
* **RQ3 Hidden gem:** of the underrated, which show evidence their appeal extends beyond the niche currently rating them?

The gap between RQ2 and RQ3 **is the whole point**:

> A game can be genuinely excellent and still not be a hidden gem if its appeal is inherently niche.

"Cult" and "hidden" are hypotheses about **audience breadth conditional on excellence**, not synonyms for "niche" or "obscure":

| Concept | Hypothesis | What would make it true | What evidence would support it | What evidence would undermine it |
|---|---|---|---|---|
| **Cult candidate** (hypothesis) | High quality is driven primarily by highly self-selected audience who sought it because it fits their existing tastes; non-specialists would rate it meaningfully lower | High `adj_mean` + high specialist share + significant positive `diff_adj` (specialists higher) + material negative `delta_true` (reweighting toward broader lowers quality) | Step 7 specialist 0–4 vs ≥20 `diff` large positive (≥0.50, p<0.05) with n≥10 per side, plus 7C `exposure_sensitive` or `strongly_sensitive` with large negative delta, plus high `TVD_type` / high penetration only within heavy enthusiasts | Parity across audiences (|diff|<0.30) despite high specialist share — suggests breadth even with niche audience |
| **Hidden-gem candidate** (hypothesis) | High quality would also be liked by materially different observable audiences who haven't yet rated it; current obscurity is exposure/visibility, not taste mismatch | High `adj_mean` + underrated vs expectation + obscure (`n_obs` band, penetration low) + **stable_exposure** (quality not selection-dependent) + **parity across audiences** (non-specialists light raters rate similarly) | `adj_mean` high, residual high, `n_obs` low, 7C `stable_exposure` with small |delta|, 2+ cross-audience parities | `insufficient_overlap` or exposure-sensitive without parity — suggests we simply don't know breadth |
| **Niche but high quality** (evidence label) | Excellent for its audience; no evidence it generalizes — neither cult nor hidden proven | High `adj_mean`, hiddenness true, but audience-selection sensitive without parity, or penetration only within heavy types | `exposure_sensitive` without parity, or specialist share high and cross-audience parity fails | Would need parity to upgrade |
| **Unknown / insufficient evidence** | Cannot tell breadth from available data | Any `insufficient_overlap` on 7C, or no cross-audience support with n≥10 | `max_w` explosion, `ESS_ratio`<0.10, `mean_p` below marginal, `n_obs`<150 | Not applicable — absence of evidence is not evidence of narrowness |

**Do NOT call a game "cult" or "hidden" as fact.** Those are conclusions about counterfactual taste that BGG data do not identify. The framework labels evidence tiers (`strong_hidden_gem_evidence`, `plausible_hidden_gem`, `niche_but_high_quality`, `insufficient_broad_appeal_evidence`) — all explicitly hypotheses about observed evidence.

---

## 2. What the data can and cannot tell

### Can tell (observable, with caveats)

* **Who rated it:** Volume distribution, weight preference, type specialization (`spec_ge10/ge20`), ownership (snapshot), severity. Herfindahl mean 0.192, heavy-share 0.29, specialist mean 0.832 (inflated by broad categories), etc. Compare to same-type reference (TVD_type mean 0.152) for interpretability.
* **How differently they rated:** Severity-adjusted `diff_adj` across realized diverse raters, SE-aware, where support exists (volume 9227 ≥10, specialist 3973). Median diff specialist 0.15, volume 0.08 — not systematically large, but some games show material gaps.
* **How sensitive quality is to observable reweighting:** Propensity `P(rate|profile)` with AUC 0.822, calibrated `p_true`, per-game `delta_quality`, `ESS`, `max_w`. Reveals dependence on observable rater profile.
* **Within-type selectivity:** Penetration among heavy enthusiasts: median 18XX 0.297 (30% of heavy 18XX rated typical 18XX) vs Wargame 0.010 (1%) — typical wargame is far more selective even within enthusiasts.

### Cannot tell (identification limits, preserved uncertainty)

* **Who encountered but did not rate, and why:** A missing rating could be never encountered, encountered and disliked but not rated, encountered and liked but not rated, not yet released/accessible, language/availability barrier — unknown. We do NOT impute negatives and do NOT interpret missing as negative. Penetration proxy is exposure/under-exposure description, not negative preference.
* **Causal exposure:** Propensity `p` is prediction from observable history (26 features), not randomized exposure. Not causal.
* **Temporal order:** `cnt_type_excl` (other count) includes ratings after target; `postdate`/`rating_tstamp` semantics unresolved — treat as type exposure proxy, not true prior. Collections `own` is snapshot, not rating-time ownership.
* **Out-of-distribution taste:** Whether a non-enthusiast who has never rated any game of that type would like *this* game is not observed for many niche games — that's exactly `insufficient_overlap` (18XX 100%). Even `adequate` only means observable-profile reweighting is identified, not that unobservable taste is identified.
* **External popularity:** Sales, plays,convention presence, language editions, marketing spend — not in BGG ratings. A game with `insufficient_overlap` may be broadly appealing in the world but not among BGG observable enthusiasts.

### Consequence for tagging claims

Every claim in findings must be tagged: observed fact / empirical finding / assumption / hypothesis / model-dependent conclusion / speculation. Examples:

* "1830 `spec_ge20` 0.054" — **observed fact** from histories.
* "1830 `delta_true` −0.321 with `max_w` 50707" — **model-dependent conclusion** (logistic `p_true` via −5.159 shift, leakage-excluded).
* "1830 would be rated lower by broader 18XX enthusiasts" — **hypothesis** (not identified; `insufficient_overlap` means we cannot tell).
* "Catan `stable_exposure` suggests broad observable appeal" — **empirical finding + hypothesis** (adequate+stable+small delta is consistency, not proof of universal taste).
* "`insufficient_overlap` means cult" — **forbidden inference** — unknown, not bad.

---

## 3. Why `insufficient_overlap` is unknown, not cultish

Three distinctions:

* **Statistical:** `insufficient` flags where inverse-propensity weights explode (median max_w true 1449, insufficient threshold 8700 at p95; ESS_ratio 0.10 at p10; mean_p 0.005 at p10). The estimator's variance is too large to claim *any* magnitude, positive or negative. Calling it "cult" would be drawing a conclusion from variance.
* **Substantive:** Many `insufficient` games have **gateway** characteristics or low specialist share — 1830 spec 0.054 low, but delta −0.321/Ess 0.12/insufficient — its sensitivity comes from many light newcomers with very low `p`, not from being ultra-niche. 1846 spec 0.24 also insufficient. Insufficient reflects small heavy-enthusiast denominator (18XX GE20 only 337 users) and global population size (287k) — not inherent cultishness.
* **Ethical/research:** The project's definition of success is "which games appear genuinely underrated, and which of those show evidence of appeal beyond niche — a well-supported 'we can't tell' beats an elaborate ranking." Treating unknown as negative would manufacture a ranking that cannot survive scrutiny.

So: `insufficient_overlap` games are set aside as **`insufficient_broad_appeal_evidence`** — high quality is genuine for raters, but breadth is **unidentified** on BGG alone. Next evidence should be external (plays/sales/time) or broader at-risk definition (TYPE_GE10 vs ALL sensitivity) — reported separately.

---

## 4. Why thresholded composition alone cannot settle cult vs hidden

Step 7 taxonomy used q75 thresholds (spec 0.939, TVD 0.231, own 0.664, herf 0.203) to define `low/moderate/high_audience_selectivity` (3936/6867/1124/2771 insufficient). Problems:

* Broad categories inflate `spec` mean to 0.832 (Party 62k ≥10, Economic 105k) — a Party game with spec 0.76 (Monikers) looks "moderate" but is not distinctive vs Party baseline. Narrow 18XX median 0.24 vs broad — same numeric threshold means different things. So 7 composition is **supporting**, not gating.
* Category `share_cat_related` 0.993 is least discriminating.
* TVD_global flags all Wargames as distinctive vs global; TVD_type corrects.
* Ownership `share_own` mean 0.573 snapshot-limited.

Propensity adds continuous exposure gradient (log1p counts, weight, delta) beyond binary `spec≥10`. The gateway 1830 vs specialist 1817 case shows threshold 0.054 vs 0.297 misses sensitivity difference revealed by delta −0.321 vs −0.352 (both large but gateway more on sampled scale). But propensity alone also collapses heterogeneity if forced into one score — hence primary is overlap+delta plus cross-audience parity, composition corroborates which dimension drives narrowness.

---

## 5. What would make a cult vs hidden claim stronger (future work, not this step)

Not for this step, but to show where evidence could come from without overclaiming now:

* **External reach:** BoardGameGeek plays (`numplays`), collections `own`/`wishlist` at rating time (not snapshot), publisher sales/geography, convention demo counts.
* **Time:** Rating trajectory since release (does non-specialist share grow? does diff shrink?). Requires resolving `postdate`/`rating_tstamp`.
* **Network:** Who influenced whom (ratings after friend ratings), beyond volume/specialist bins.
* **Content:** Weight, mechanics, language dependence — test whether cross-audience parity holds within low-weight vs heavy subgroups, etc.

Until such data are validated and joined to pass2, single-source BGG rating claims stay at hypothesis level.

---

## 6. Language discipline for any future list

Use only these:

| Allowed | Forbidden |
|---|---|
| "Shows `stable_exposure` and parity across non-specialists (specialist diff 0.00, ESS 0.46) — *strong hidden-gem evidence* on observable BGG data" | "Is a hidden gem" |
| "Shows `exposure_sensitive` (delta −0.41) without parity — *niche but high quality*" | "Is a cult hit" |
| "Has `insufficient_overlap` (max_w 50707, ESS 0.06) — *insufficient broad-appeal evidence*, unknown; often gateway, not cult" | "Is cult / fan-inflated / overrated due to selection" |
| "Underrated vs S3 by +0.8 but `moderate_audience_selectivity` — candidate for external check" | "Hidden gem score 8.7" |

Every disposition must cite fields: `spec_ge10/ge20`, `TVD_type`, `delta_quality`, `ess_ratio`, `max_weight`, `mean_p`, `overlap_status`, `sensitivity_class`, `diff_adj` (specialist/volume), `supported_ge10`.

---

## 7. Summary for Step 8

* Cult vs hidden is a hypothesis about breadth conditional on quality, not a fact the data can certify.
* Observable evidence can be **auditable and separable** (who rated, how differently, how sensitive to reweighting) while remaining **hypothesis** about unobserved reception.
* `insufficient_overlap` = unknown — the framework's most important guard against overclaiming.
* No game is labeled cult or hidden factually; tiers are `strong`/`plausible`/`niche`/`insufficient` **evidence** on BGG observables.

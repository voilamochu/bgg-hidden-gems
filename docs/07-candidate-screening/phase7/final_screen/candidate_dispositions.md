# Candidate Dispositions — 544 Quality-Gated Robust Underrated (INTERMEDIATE / NOT FINAL)

> **Status:** INTERMEDIATE / NOT FINAL RESEARCH OUTPUTS — screening stage, not the final hidden-gem ranking. **Do not treat as proof of broad appeal.**

**Population:** 544 quality-gated candidates (`adj_mean ≥7.5`, P74≈P75 top quartile, `mu 7.144`) from 910 robust (Q3b/OLS resid 0.60–2.27, min_alt≥0.30, z≥5, n≥200, year<2025, not duplicate-shadowed, SE 1.194/√n). See `quality_gate/README.md` for gate methodology.

## Disposition counts (single-label priority: wellknown → insufficient_hiddenness → niche → edition → other → likely → insufficient_broad)

| Disposition | N | % of 544 | Definition (method choice) |
|---|---|---:|---|
| `likely_hidden_gem_candidate` | 55 | 10.1% | Hidden (users<5000 & rank≥1000 or null) + quality + underratedness + suggestive broad evidence (heavy mean≥7.5 with moderate share_own 0.45–0.78 or fallback moderate ownership/heavy share)
 |
| `high_quality_but_well_known` | 0 | 0.0% | users≥20000 or rank<500 — widely established, conflicts with hidden-gem objective (530 flagged wellknown in Phase 7, 67 met robust criteria)
 |
| `high_quality_but_niche_only` | 19 | 3.5% | share_own≥0.78 & share_light≤0.04 & users<1500 — high owner concentration, limited light reach (e.g. Monikers 0.84–0.87, share_light 0.02–0.03, users 255–609)
 |
| `duplicate_or_edition_related` | 104 | 19.1% | title contains edition keyword ['edition', 'anniversary', 'big box', 'collector', 'deluxe', 'decennial', 'heritage', 'premium', 'reprint', 'box set', 'nonsense', 'shmonikers', 'more monikers', 'classics', 'party edition', 'special edition', 'kickstarter edition'] — special/deluxe/anniversary/big-box/collector variant or family (e.g. Small World Designer Edition vs base Small World 40692 n 75285; Monikers family 255249/179448/140135; game_links reimplementation/version; 4× users shadowing 136 flagged pre-gate)
 |
| `insufficient_hiddenness_evidence` | 40 | 7.4% | users≥5000 or rank<1000 — not obscure (e.g. users>5000 or rank<1000; 40 among gated)
 |
| `insufficient_broad_appeal_evidence` | 317 | 58.3% | hidden but audience evidence is proxy-only; 902/910 robust had heavy/light overlap but gap is severity not taste; category breadth/share_own/mean(delta) are proxies; no external sales/plays; heavy mean <7.5 or ownership still high
 |
| `other_exclusion` | 9 | 1.7% | n<260 & resid<0.7 — lower tail moderate SE, less evidence (illustrative)
 |

**Priority note:** a game matching multiple rules takes the earliest in priority above; four dimensions (quality/underratedness/hiddenness/audience) are reported separately per candidate in `candidate_review.md/csv` — disposition is summary label, not combined score.

## Distributions per disposition

| Disposition | N | n median (mean) | adj median (mean) | resid median (mean) | resid min–max |
|---|---|---:|---:|---:|---|
| `likely_hidden_gem_candidate` | 55 | 544 (692) | 8.53 (8.50) | 0.85 (0.91) | 0.60–1.56 |
| `high_quality_but_well_known` | 0 | — | — | — | — |
| `high_quality_but_niche_only` | 19 | 452 (463) | 8.39 (8.37) | 1.05 (1.31) | 0.63–2.27 |
| `duplicate_or_edition_related` | 104 | 549 (824) | 8.11 (8.16) | 0.89 (0.93) | 0.60–2.20 |
| `insufficient_hiddenness_evidence` | 40 | 4310 (4642) | 8.04 (8.08) | 0.76 (0.85) | 0.61–1.93 |
| `insufficient_broad_appeal_evidence` | 317 | 483 (737) | 7.89 (7.96) | 0.84 (0.90) | 0.60–1.76 |
| `other_exclusion` | 9 | 217 (219) | 7.98 (8.00) | 0.65 (0.65) | 0.61–0.68 |

## Key tallies

- **Well-known strict (users≥20k or rank<500) among gated:** 0 (0 — robust already excluded 67 wellknown meeting criteria; 530 flagged wellknown total pre-gate; quality gate left 544 all below strict threshold)
- **Insufficient hiddenness (users≥5k or rank<1000):** 40 (raw 40 with users≥5k or rank<1000; 7 of those are also edition and counted as `duplicate_or_edition_related` under this priority — see CSV flags for independent tallies)
- **Raw tallies independent of priority:** wellknown strict 0, insufficient hiddenness (users≥5k or rank<1000) 40, edition keyword 122, niche high-own 19, other low-n/low-resid 9
- **Edition/duplicate/family attention:** 122 of 544 (22.4%) contain edition keywords; 4 is_reimplementation among gated (e.g. Dutch InterCity, Daytona 500); Monikers family 7 of 8 in population are in gated (all variants 255–609 users vs base Monikers 7906 users 14.8% reimplementation reach vs 1619 non-reimpl)
- **Niche-only signal:** 19 with share_own≥0.78 share_light≤0.04 users<1500; strict 0.84–0.87 example captures 6 of those (Monikers editions + Gamut etc)
- **Plausible hidden gems vs insufficient broad appeal:** 55 likely vs 317 insufficient_broad — remaining 504 hidden (users<5k rank≥1000) split into 55 with suggestive cross-audience (heavy mean≥7.5 + moderate ownership) vs 317 proxy-only

## How to use

- Sort `candidate_review.md/csv` by disposition (likely first) then resid desc then z — manual review starts with 55 plausible, then checks niche/edition/insufficient for caveats.
- Every row keeps four dimensions separate: quality (adj,n,SE,lb,z), underratedness (resid,min_alt,z,n decile), recognition/hiddenness (users,rank,num_weights,is_reimplementation), audience breadth (share_heavy,mean(delta),share_own,heavy vs light diff, category breadth) + major caveats (share_own snapshot-time 58% everywhere, 27.3% missing country, SE at n=200 vs 3000).
- Do not claim broad appeal established where data cannot; treat plausible as **candidates for external validation**, not proof.

*Tagging per AGENTS.md:* counts are observed facts; thresholds are method choices; resid/adj/expected are model-dependent Q3b/OLS; hiddenness is popularity proxy not broad appeal; audience evidence is severity-level not taste.

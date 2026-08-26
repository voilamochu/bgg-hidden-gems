# Known Case Examples — Step 7/7B/7C under Step 8 Framework

**Population:** 14,698 × 287,302 × 24,146,307, mu≈7.139. Fields from `propensity_validation_game_level.csv` (7C, `p_true` via −5.159 shift) and `audience_selectivity_game_level.csv` + `cross_audience_results.csv` (7). Dispositions use `screening_framework.md` tiers; none are factual "cult"/"hidden" — hypotheses about observed evidence.

Reference tasks: distinguish 5 buckets — (1) high quality+broad audience, (2) high quality+specialized but stable cross-audience, (3) high quality+strong exposure sensitivity, (4) high quality+insufficient/unknown, (5) high quality+popular not hidden. Confidence tiers `strong`/`plausible`/`niche`/`insufficient` defined in `screening_framework.md` §4.

---

## 1. Master Table (one row per game, auditable)

| game_id | Title | Type | n_obs | adj_mean | Step 7 spec_ge10 / spec_ge20 / TVD_type / TVD_global / taxonomy | 7B delta_sample / class (sampled) | 7C delta_true / trunc / overlap_status / ESS_ratio / max_w_true / mean_p_true / penetration_all / pen_ge20 | Cross-audience (adj diff, n≥10): volume 10–24 vs 500+ (diff/z); specialist 0–4 vs ≥20 (diff/z) | Framework bucket (1–5) | Confidence tier | One-line interpretation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 421 | 1830: Railways & Robber Barons | 18XX | 5628 | 8.41 | 0.138 / 0.054 / 0.134 / 0.087 / **low_audience_selectivity** (0 deviations) | −0.283 / insufficient_overlap (max_w 293) | **−0.321 / −0.201 / insufficient_overlap / 0.12 / 50707 / 0.163 / 0.0196 / 0.905** | vol 0.112/1.1 (221 vs 1224); spec **1.136/12.8** (4146 vs 305) | **4** high quality + insufficient/unknown | `insufficient_broad_appeal_evidence` | High quality gateway 18XX with low specialist share, but sensitivity exists (−0.32) and is **not identified** (ESS 0.12, max 50k); large specialist gap (+1.14) suggests niche enthusiasm among heavy vs newcomers; **unknown**, not cult. Needs external plays/sales. |
| 63170 | 1817 | 18XX | 764 | **9.36** | 0.594 / **0.297** / 0.042 / 0.165 / moderate | −0.156 / strongly_sensitive (max 95) | **−0.352 / −0.099 / insufficient_overlap / 0.03 / 16299 / 0.524 / 0.0027 / 0.674** | vol −0.102/−0.3 (21 vs 215); spec **0.355/2.3** (156 vs 227) | **4** | `insufficient_broad_appeal_evidence` | Highest adj among cases but smallest heavy-enthusiast base (764 obs); specialist 0.594 high, delta large (−0.35) but ESS 0.03 — unidentified; specialist diff small (+0.35, marginal) — breadth not disproven but not identified. |
| 424 | 1870: Railroading … Trans Mississippi | 18XX | 1053 | 8.03 | 0.375 / 0.191 / 0.084 / 0.116 / **low** | −0.286 / insufficient (max 139) | **−0.414 / −0.289 / insufficient_overlap / 0.05 / 24024 / 0.362 / 0.0037 / 0.596** | vol −0.262/−1.3 (45 vs 289); spec **0.87/7.6** (433 vs 201) | **4** | `insufficient_broad_appeal_evidence` | High quality with moderate specialist share; largest negative delta (−0.41) among trio but again insufficient (Ess 0.05) — sensitivity real but not identified; specialist diff large (+0.87) — enthusiast vs newcomer gap material. |
| 17405 | 1846: The Race for the Midwest | 18XX | 2998 | 8.54 | 0.241 / 0.099 / 0.057 / 0.151 / moderate | −0.217 / insufficient (max 377) | **−0.269 / −0.152 / insufficient_overlap / 0.06 / 65414 / 0.245 / 0.0104 / 0.881** | vol −0.122/−0.9 (70 vs 798); spec **0.597/7.3** (1738 vs 297) | **4** | `insufficient_broad_appeal_evidence` | Broad moderate spec but delta −0.27; penetration 88% among heavy — high within-18XX reach but still insufficient globally; specialist diff +0.60 large. |
| 253608 | 18Chesapeake | 18XX | 1732 | 8.34 | 0.277 / 0.118 / 0.065 / 0.170 / moderate | −0.061 / insufficient (max 257) | **−0.074 / −0.052 / insufficient_overlap / 0.07 / 44553 / 0.254 / 0.0060 / 0.608** | vol −0.163/−0.9 (29 vs 460); spec **0.004/0.0** (937 vs 205) | **4** | `insufficient_broad_appeal_evidence` | Smallest delta (−0.07) among 18XX — least sensitive — but still insufficient by weight/ESS; specialist diff **0.00** is the only 18XX with specialist parity — suggests relatively broader within-18XX appeal, still unknown globally. |
| 423 | 1856: Railroading in Upper Canada | 18XX | 1328 | 8.07 | 0.347 / — / — / — / (from 7C summary) | −0.482 / insufficient (max 212) | **−0.641 / −0.255 / insufficient_overlap / 0.05 / 36612 / 0.340 / 0.0046 / 0.671** | (not in cross table but analogous) | **4** | `insufficient_broad_appeal_evidence` | Most sensitive 18XX raw delta (−0.64) and trunc still −0.26; illustrates heterogeneity within 18XX not uniform. |
| 13 | CATAN (added per brief) | Economic | 119003 | 7.12 | 0.505 / 0.306 / 0.311 / 0.311 / moderate (2 deviations) | **+0.047** / stable (max 11) | **+0.084 / −0.002 / adequate_overlap / 0.46 / 1738 / 0.019 / 0.414 / 0.654** | vol −0.104/−5.0 (23346 vs 5210); spec **−0.17/−17.6** (34418 vs 36413) — **non-specialists slightly higher** | **5** high quality + obvious popularity, therefore not hidden | `not_hidden` (popular) | Large-n mainstream, **adequate+stable** — quality stable after reweighting, penetration 41% all; no evidence of selection threat; fails HIDDENNESS, so not hidden gem but **bucket 1** broad-audience high quality. |
| 9209 | Ticket to Ride (added) | Other | 87222 | 7.50 | NA (Other, TVD 0.245) / moderate (1 dev) | −0.046 / stable (max 13) | **−0.070 / −0.001 / borderline_overlap / 0.54 / 2049 / 0.008 / 0.304 / NA** | vol **0.399/20.8** (13368 vs 5016) | **5 + caution** | `plausible_hidden` if hidden else `exposure_sensitive` but popular — actually **not hidden** (87k); stable then borderline/moderate — quality sensitive only mildly (+0.01 trunc) but volume diff shows **light raters higher** (+0.40) — breadth evidence exists but obscured by Other type handling. |
| 30549 | Pandemic | Coop | 120228 | 7.62 | 0.475 / 0.260 / 0.227 / 0.286 / moderate | −0.040 / stable (max 16) | **−0.063 / −0.005 / borderline_overlap / 0.43 / 2603 / 0.015 / 0.418 / 0.701** | vol 0.194/10.1; spec 0.27/30.3 (36902 vs 31250) | **5** | `not_hidden` | Mainstream Coop, borderline/moderate after correction but delta small (−0.06, trunc −0.005) and large n — stable in substance; penetration 42% — not hidden. |
| 822 | Carcassonne | Other | 122032 | 7.50 | NA / TVD 0.292 / moderate | −0.023 / stable (max 12) | **−0.035 / −0.000 / borderline_overlap / 0.57 / 1893 / 0.007 / 0.425 / NA** | vol 0.223/12.7 (21079 vs 5770) | **5** | `not_hidden` | Same as above — borderline/moderate after correction but trivial delta/trunc; not hidden. |

**Notes on 7B vs 7C comparability:** 7B sampled rule used `max_w>100` / `ESS<0.10` etc.; 7C rescaled to `8700/1740` via 87× factor, so `adequate` drops from 70.5% to 32.8%. Direction of delta is preserved (Spearman ~1 across correction), but magnitude is larger on true scale (≈0.06→0.13 mean|delta|). All 18XX remain insufficient on both, just more extreme on true. Truncated delta shown as fragility check — for 18XX it attenuates by 0.12–0.38 (e.g., 1830 −0.32→−0.20) but remains material for 1870 (−0.41→−0.29).

---

## 2. Per-Game Narratives (what we can say and cannot)

### 1830: Railways & Robber Barons (421)

* **Observed facts:** n=5628, adj 8.41 (highest-observed among low-spec 18XX), spec_ge10 0.138 (low vs 18XX median 0.24), spec_ge20 0.054 (many newcomers, share_0_4 0.86), TVD_type 0.134 not extreme, taxonomy **low_audience_selectivity** (0 deviations), herfindahl 0.20, own 0.57 near mean. Penetration 1.96% of all users but **90.5% of heavy 18XX enthusiasts** (337 GE20) — high within-type reach.
* **Cross-audience (severity-adjusted):** Volume 10–24 (221) vs 500+ (1224) diff +0.11 (z 1.1, not significant) — light and heavy rate similarly. Specialist 0–4 (4146) vs ≥20 (305) diff **+1.14** (z 12.8, p ~0) — non-specialists rate **lower** by more than a point? Wait sign is high−low, so high (≥20) higher by 1.14 — meaning **non-specialists (0–4) rate lower** than heavy 18XX specialists. But 1830's spec_ge20 low means many non-specialists exist; yet heavy specialists rate it ~1.14 higher (severity-adjusted). Also vs ≥10 diff +1.04 (4146 vs 778, z 18.5). Ownership diff −0.87 (owners lower? 3209 vs 2419). This split suggests strong enthusiast vs newcomer gap — the very gradient propensity captures.
* **Propensity:** delta_true −0.321 (−0.42 in summary with ALL population vs TYPE_GE10 variant), truncated −0.201, ESS 0.12, max_w 50707, mean_p 0.163 (higher than Other because heavy pool). **insufficient_overlap** — cannot identify broader counterfactual. Even truncated remains −0.20 (material).
* **What we can say:** High quality among its rater pool, unusually broadly reached within 18XX (90% heavy penetration) for an 18XX, but rating is materially higher among heavy 18XX fans than among non-specialists; observable reweighting lowers quality by ~0.3 but estimate not identified. **What we cannot say:** That it is cult or that its true broader appeal is lower — insufficient means unknown; gateway breadth (low spec) and high within-type penetration argue against dismissing as ultra-niche, but BGG alone cannot resolve.
* **Disposition:** **Bucket 4** (`high quality + insufficient_overlap / unknown`), confidence `insufficient_broad_appeal_evidence`. Would need external plays/sales or wait for more heavy-enthusiast ratings to adjudicate.

### 1817 (63170) — specialist contrast

* **Facts:** n=764 (small), adj 9.36 (top of distribution, but small-n), spec 0.594 (high, 0.297 on ge20), TVD small vs type (0.042) — distinctive within 18XX but not vs global 0.165, moderate taxonomy (1 dev). Penetration only 0.27% all but **67% heavy**.
* **Cross:** Volume −0.10 (21 vs 215, irrelevant small n_low), specialist +0.355 (156 vs 227, z2.3 p0.023) — specialists higher by 0.35, significant but smaller than 1830's 1.14. So specialist gap exists but less dramatic; light-rater parity inconclusive due to small n_low=21.
* **Propensity:** delta −0.352 (sample −0.156, so correction doubled), **ESS 0.03** smallest among cases, max 16299, mean_p 0.524 (heavy pool mostly). **insufficient** — even less identified than 1830 despite higher specialist share.
* **Can say:** Highest adjusted mean but on 764 ratings, heavily specialist audience, sensitivity large but not identified; breadth evidence weak (small volume support). **Cannot:** Call hidden gem (insufficient) or cult (parity not strongly negative).
* **Disposition:** **Bucket 4**, `insufficient_broad_appeal_evidence`.

### 1870 (424) — second specialist, large sensitivity

* **Facts:** n=1053, adj 8.03, spec 0.375/0.191, low taxonomy (0 dev), penetration 0.37% all / 59.6% heavy.
* **Cross:** spec +0.87 (433 vs 201, z7.6) — specialists rate **0.87 higher** (like 1830). Volume −0.26 (45 vs 289, n_low small).
* **Propensity:** delta **−0.414** largest among main 18XX, trunc −0.289 still large, ESS 0.05, max 24024. **insufficient**.
* **Can say:** Material sensitivity with clear specialist advantage; breadth not identified. Illustrates that even moderate-spec 18XX can be strongly sensitive due to newcomer low-p mass (41% newcomers with very low p in 7B analysis).
* **Disposition:** **Bucket 4**, `insufficient`.

### 1846 (17405) and 18Chesapeake (253608)

* **1846** is gateway-like but moderate spec (0.24), penetration 88% heavy, specialist diff +0.597 (1738 vs 297, z7.3). Delta −0.269 (insufficient). Similar narrative to 1830 but less extreme trunk (−0.152).
* **18Chesapeake** is the **most informative 18XX counterexample**: spec 0.277 moderate but **specialist diff 0.004** (937 vs 205, z0.0) — **non-specialists rate identically** to heavy specialists, despite being 18XX. Volume diff −0.16 also parity. Delta −0.074 small. Yet still **insufficient** by ESS 0.07, max 44553 — the reweighting not identified because global 287k includes many near-zero p users. **Could be** modest within-18XX breadth, but cannot generalize beyond 18XX community on BGG.
* **Disposition:** Both **bucket 4**, `insufficient`. 18Chesapeake would be the only 18XX that *could* be bucket 2 (high quality+specialized but stable cross-audience) if it had adequate overlap — but it doesn't.

### Catan (13) / Ticket to Ride (9209) / Pandemic (30549) / Carcassonne (822) — mainstream controls

* **Catan**: adj 7.12 (moderate high), spec 0.505/0.306 (inflated because Economic broad — 105k Economic ≥10), TVD 0.31 high vs both global/type (distinctive heavy/Economic pool but large n). Penetration 41% all / 65% heavy. Delta **+0.084** (slight increase after reweighting), **adequate_overlap**, **stable**, ESS 0.46, max 1738 (threshold). Cross: volume diff −0.10 (23346 vs 5210, many), specialist **−0.17** (34418 vs 36413) — **non-specialists rate higher** than heavy Economic fans (opposite of 18XX). **Bucket 5** — high quality, broadly rated, not hidden, adequate+stable is **bucket 1** subtype (broad observed audience). Demonstrates that `stable_exposure` + parity does correspond to mainstream breadth.
* **Ticket to Ride**: adj 7.50, 87222 ratings, Other (no spec), TVD 0.245, penetration 30% all. On sampled scale stable, on true **borderline/moderately_sensitive** with delta −0.070 (small), trunc −0.001 — mild sensitivity but ESS 0.54 adequate in substance; volume diff +0.399 (13368 vs 5016, z20) — **light raters rate higher** (+0.40). So parity holds and direction opposite to niche (light higher). Would be plausible broad if it were hidden, but it's popular → **bucket 5** (high quality-popular).
* **Pandemic** (Coop) and **Carcassonne** (Other) analogous: large n, borderline/moderate after correction but trivial delta/trunc (<−0.06), penetration 42%/42%, volume diff +0.19/+0.22 (light higher). Show that correction moved many large-n Other/Coop from `stable` to `moderate`/`borderline` **without material delta** — because ESS 0.43/0.57 and mean_p near marginal push them to borderline by `mean_p`/`ESS` even when `|delta|<0.07`. This is why framework requires **both** overlap and |delta|: borderline alone does not mean sensitive.
* **Disposition:** All **bucket 5** (popular, not hidden). Among them, Catan is clean `stable_exposure`; the bidirectional Others illustrate `borderline` does not equal "cult".

---

## 3. What the Framework Distinguishes (using these cases)

| Bucket | Description | Which case | What we can say | What we cannot say |
|---|---|---|---|---|
| **1. High quality + broad observed audience** | High adj, adequate+stable, parity across audiences | Catan (adequate stable, volume −0.10, specialist −0.17) | Quality generalizes across observable volume/specialist splits; selection not threatening | Not proof of universal taste; just no observable selection threat |
| **2. High quality + specialized audience but stable cross-audience ratings** | High adj, spec moderate/high but specialist diff small | 18Chesapeake **would be** this if adequate (diff 0.00) — but remains insufficient, so cannot demonstrate | IF adequate: specialist concentration does not imply rating gap — breadth within type | Without adequate, cannot generalize beyond 18XX community |
| **3. High quality + strong exposure sensitivity** | High adj, delta large (|delta|≥0.2), borderline/strong | 1830, 1870, 1817 (if they were borderline not insufficient) — gateway more sensitive (+1.14 specialist gap) | Rating depends on specialized rater pool in observable data; needs stronger parity evidence; label `exposure_sensitive` → `niche_but_high_quality` unless parity survives | Cannot quantify how much lower true broader quality would be — `truncated` shows fragility |
| **4. High quality + insufficient overlap / unknown** | High adj, but max_w>8700 or ESS<0.10 or mean_p<0.005 or n<150 | **All 18XX (81/81)** including 1830/1817/1870/1846/18Chesapeake | High quality for raters, breadth **unidentified**; must be `insufficient_broad_appeal_evidence`, not cult/bad | Any claim about cult vs hidden is unfounded — requires external data |
| **5. High quality + obvious popularity, not hidden** | High adj, large n/penetration | Catan, Ticket to Ride, Pandemic, Carcassonne (87k–122k, penetration 30–42%) | Good and visible; hiddenness fails regardless of audience selection | Not a hidden-gem candidate even if selection stable |

**Key takeaway per task E:** Among the five 18XX, only **18Chesapeake** shows specialist parity (diff 0.00) that could hint at within-type breadth — but BGG's global propensity still flags insufficient, so even the best 18XX cannot be bucket 2 on BGG alone. Catan shows the clean bucket-1 pattern (stable + parity reversed). Ticket to Ride/Pandemic/Carcassonne show that after correction, large-n Other/Coop often become borderline/moderate by mean_p/ESS without material delta — so `exposure_sensitive` must be read with |delta|, not just overlap. All 18XX stay in bucket 4 (unknown) — the correct label is `insufficient_broad_appeal_evidence`, and no 18XX on BGG alone can be `strong` or `plausible` hidden gem under this framework.

---

## 4. Data Sources per Column

* Specialist share, TVD, taxonomy: `docs/phase2-pass2/step7_audience_selection/audience_selectivity_game_level.csv` fields `spec_primary_share_ge10`, `spec_primary_share_ge20`, `tvd_volume_global/type`, `taxonomy`, `deviation_count`.
* Delta, overlap, ESS: `docs/phase2-pass2/step7c_exposure_propensity_validation/propensity_validation_game_level.csv` fields `delta_quality`, `truncated_delta`, `overlap_status`, `ess_ratio`, `max_weight`, `p_mean_raters`, `penetration`, `penetration_type_ge20`, `sensitivity_class`.
* Cross-audience diffs: `docs/phase2-pass2/step7_audience_selection/cross_audience_results.csv` fields `diff_adj`, `se_diff`, `z`, `supported_ge10`, `n_low/high`.

Every disposition above cites those fields; no invented numbers. Weight year NULL 7 games excluded (99.95% present). Ownership snapshot caveat preserved.

# Stage B — Type × Weight Interaction (gated)

**Generated:** 2026-08-24T16:30:47Z
**Population:** Confirmed pass2 only (14,698 games, 24.1M obs)

**Model:** `r_ug = [Stage A] + gamma_{u,t×weight}·flag_{g,t}·weight_class_g + epsilon (would be fit on confirmed population only)`

**Survivors from Stage A:** None — Stage B not run

**Result:**
{
  "survivors": [],
  "note": "No flags passed Stage A BH-corrected gates; Stage B not run per spec (gated). This is the expected outcome given prior Phase 3 |tau|\u22640.036 and R2+0.004.",
  "model": "r_ug = [Stage A] + gamma_{u,t\u00d7weight}\u00b7flag_{g,t}\u00b7weight_class_g + epsilon (would be fit on confirmed population only)",
  "weight_axes": {
    "primary_3class": [
      "Light <2.5",
      "Medium 2.5\u20133.5",
      "Heavy \u22653.5"
    ],
    "sensitivity_5class": [
      "<1.5",
      "1.5\u20132.0",
      "2.0\u20132.5",
      "2.5\u20133.5",
      ">3.5"
    ]
  }
}

**Interpretation:** Since no flag passed Stage A BH-corrected gates, Stage B is gated and not run per spec §3. This is confirmatory, not exploratory, and correctly stops. If any survivor had emerged, we would extend joint model with weight-class interactions (3-class primary, 5-class sensitivity) on confirmed data and evaluate analogous gates.

**Weight axes (orthogonal):**
- Primary: Light <2.5 / Medium 2.5–3.5 / Heavy ≥3.5
- Sensitivity: <1.5 / 1.5–2.0 / 2.0–2.5 / 2.5–3.5 / >3.5

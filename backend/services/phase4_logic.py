"""
Phase-4 Deterministic Logic
Maps (scale, productionHealth, trailer_features) → (audienceType, audienceInterestScore).
Pure business rules — no DB access, no AI, no randomness.

Scoring philosophy
──────────────────
Base score from scale provides a *baseline expectation* (~40-50), NOT
the dominant factor.  Trailer-derived features contribute ±10-25 points
through five continuous signals:

  Signal                  Range     Weight rationale
  ─────────────────────   ────────  ─────────────────────────────
  Pacing fit              ±8 pts   Core editorial quality signal
  Scene density bonus     0-6 pts  Engagement / energy indicator
  Brightness balance      ±5 pts   Visual quality / readability
  Audio energy bonus      0-6 pts  Sound design quality (optional)
  Production health       −8 / −4  Risk penalty (context, not trailer)

Typical resulting ranges by scale:
  INDIE  → ~45-75      MID → ~52-82      LARGE → ~58-88
"""

from typing import Any, Dict


# ── Scale → audience type mapping ──────────────────────────
_SCALE_TO_AUDIENCE: Dict[str, str] = {
    "indie":  "niche",
    "mid":    "regional",
    "large":  "mass",
}

# ── Scale → baseline score (lowered so trailer features matter) ──
_SCALE_TO_BASE: Dict[str, float] = {
    "indie":  45.0,   # was 60 — now leaves room for trailer to push to 70+
    "mid":    52.0,   # was 70
    "large":  58.0,   # was 80
}

# ── Ideal pacing by audience type (seconds per shot) ───────
# Niche audiences prefer deliberate pacing; mass audiences prefer fast cuts.
_IDEAL_AVG_SHOT: Dict[str, float] = {
    "niche":    5.0,   # artsy, slower
    "regional": 3.5,   # balanced
    "mass":     2.0,   # fast, high-energy
}

# Maximum points each signal can contribute
_MAX_PACING_PTS     = 8.0    # ± (penalty for poor pacing, bonus for ideal)
_MAX_DENSITY_PTS    = 6.0    # 0-6 (more cuts per sec = more engaging, up to a cap)
_MAX_BRIGHTNESS_PTS = 5.0    # ± (penalty for extremes, bonus for midrange)
_MAX_AUDIO_PTS      = 6.0    # 0-6 (audio energy bonus, optional)


def compute_phase4(
    scale: str,
    production_health: str,
    trailer_features: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Deterministic Phase-4 scoring.

    Parameters
    ----------
    scale : str
        One of "indie", "mid", "large" (case-insensitive).
    production_health : str
        One of "good", "atRisk", "critical" (case-insensitive).
    trailer_features : dict
        Output of `extract_trailer_features()`.

    Returns
    -------
    dict with:
        - audienceType : str   ("niche" | "regional" | "mass")
        - audienceInterestScore : int  (0–100)
    """
    scale_lower = scale.strip().lower()
    health_lower = production_health.strip().lower()

    # ── 1. Audience type (unchanged) ───────────────────────
    audience_type = _SCALE_TO_AUDIENCE.get(scale_lower, "niche")

    # ── 2. Reduced base score ──────────────────────────────
    score = _SCALE_TO_BASE.get(scale_lower, 45.0)

    # ── 3. Pacing fit (±8 pts) ─────────────────────────────
    # How close is the trailer's avg shot length to the ideal for this audience?
    avg_shot = trailer_features.get("average_shot_length_sec", 0.0)
    ideal_shot = _IDEAL_AVG_SHOT.get(audience_type, 3.5)

    if avg_shot > 0:
        # Deviation ratio: 0 = perfect match, 1 = 100% off
        deviation = abs(avg_shot - ideal_shot) / ideal_shot
        # Linearly interpolate: 0 deviation → +MAX, ≥1.0 deviation → −MAX
        pacing_pts = _MAX_PACING_PTS * (1.0 - min(deviation, 2.0))
        # Result range: +8 (perfect) down to -8 (very far from ideal)
        score += pacing_pts

    # ── 4. Scene density bonus (0–6 pts) ───────────────────
    # Higher scene-change frequency signals more dynamic editing.
    # Cap at 1.0 cuts/sec to avoid rewarding chaos.
    scene_freq = trailer_features.get("scene_change_frequency_per_sec", 0.0)
    if scene_freq > 0:
        # Linear ramp: 0 cuts/s → 0 pts, ≥1.0 cuts/s → 6 pts
        density_pts = _MAX_DENSITY_PTS * min(scene_freq / 1.0, 1.0)
        score += density_pts

    # ── 5. Brightness balance (±5 pts) ─────────────────────
    # Midrange brightness (100-160) is ideal; extremes are penalised.
    brightness = trailer_features.get("average_brightness", -1.0)
    if brightness >= 0:
        # Sweet spot: 130 (centre of 100-160 range)
        bright_dev = abs(brightness - 130.0) / 130.0
        # 0 deviation → +5, ≥1.0 → −5
        brightness_pts = _MAX_BRIGHTNESS_PTS * (1.0 - min(bright_dev, 2.0))
        score += brightness_pts

    # ── 6. Audio energy bonus (0–6 pts, optional) ──────────
    # Audio is a bonus, never a penalty — missing audio just means 0 pts.
    if trailer_features.get("audio_available", False):
        energy = trailer_features.get("audio_energy_mean", 0.0)
        # Linear ramp: 0 energy → 0 pts, ≥0.15 → 6 pts
        audio_pts = _MAX_AUDIO_PTS * min(energy / 0.15, 1.0)
        score += audio_pts

    # ── 7. Production health penalty ───────────────────────
    if health_lower in ("atrisk", "at_risk"):
        score -= 8   # noticeable but not crushing
    elif health_lower == "critical":
        score -= 4   # critical is actually a smaller penalty here because
                      # we assume critical projects would have been caught
                      # earlier; the main signal comes from the trailer itself

    # ── 8. Clamp 0–100 ────────────────────────────────────
    final_score = max(0, min(100, round(score)))

    return {
        "audienceType": audience_type,
        "audienceInterestScore": final_score,
    }
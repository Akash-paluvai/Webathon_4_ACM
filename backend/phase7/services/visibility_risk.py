"""
Algorithm Visibility Risk Detector.

Detects if the film may be suppressed by platform algorithms.
Uses competition spike, engagement velocity, genre saturation,
platform overcrowding, and weak early CTR signals.
"""

import hashlib
from typing import Dict, List


def detect_visibility_risk(intel: Dict) -> Dict:
    """
    Detect algorithm suppression risk.

    Returns: {visibility_risk, risk_score, primary_causes, suggested_fix}
    """
    cdi = intel.get("cdi", 0.5)
    velocity = intel.get("avg_engagement_velocity", 0.5)
    hype = intel.get("hype_momentum", 0.5)
    platform_fit = intel.get("platform_fit", 0.5)
    genre = intel.get("genre", "Drama")
    release_mode = intel.get("release_mode", "ott")

    causes: List[str] = []
    fixes: List[str] = []

    # Genre saturation on OTT
    genre_saturation = 0.0
    saturated_genres = {"Drama": 0.7, "Thriller": 0.6, "Horror": 0.5, "Comedy": 0.55}
    if release_mode == "ott" and genre in saturated_genres:
        genre_saturation = saturated_genres[genre]
        if genre_saturation > 0.5:
            causes.append(f"Genre saturation on OTT ({genre}: {genre_saturation:.0%})")
            fixes.append("Differentiate with unique selling angle or cross-genre positioning")

    # Low engagement velocity
    if velocity < 0.4:
        causes.append(f"Low early engagement velocity ({velocity:.0%})")
        fixes.append("Increase influencer push in Week 1")

    # Competition spike
    if cdi > 0.6:
        causes.append(f"High competition density ({cdi:.0%})")
        fixes.append("Shift release by 1 week to avoid peak competition")

    # Weak hype
    if hype < 0.35:
        causes.append(f"Weak hype momentum ({hype:.0%})")
        fixes.append("Drop trailer teaser or viral content before release")

    # Platform overcrowding
    if platform_fit < 0.5 and release_mode == "ott":
        causes.append("Platform overcrowding — low fit score")
        fixes.append("Consider hybrid release or different platform")

    # Weak CTR proxy (low sentiment + low velocity)
    sentiment = intel.get("avg_sentiment", 0.5)
    if sentiment < 0.4 and velocity < 0.45:
        causes.append("Weak early CTR signal (low sentiment + velocity)")
        fixes.append("Re-cut trailer with stronger hook in first 5 seconds")

    # Risk score
    risk_score = round(min(1.0,
        0.25 * cdi
        + 0.25 * (1.0 - velocity)
        + 0.20 * genre_saturation
        + 0.15 * (1.0 - hype)
        + 0.15 * (1.0 - platform_fit)
    ), 4)

    if risk_score >= 0.65:
        level = "HIGH"
    elif risk_score >= 0.45:
        level = "MODERATE"
    else:
        level = "LOW"

    if not fixes:
        fixes.append("No immediate action required — visibility risk is low")

    return {
        "visibility_risk": level,
        "risk_score": risk_score,
        "primary_causes": causes if causes else ["No significant risk factors detected"],
        "suggested_fix": fixes,
    }

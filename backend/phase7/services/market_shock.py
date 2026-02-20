"""
Market Shock Detection Engine.

Detects sudden changes that affect discoverability:
- Surprise competitor release
- Viral trend shift
- Genre fatigue signals
- Social backlash indicators
- Major event disruption

Auto-adjusts optimization recommendations.
"""

from typing import Dict, List


def detect_market_shocks(intel: Dict) -> Dict:
    """
    Detect market shocks and recommend adjustments.

    Returns: {shocks_detected, shock_list, overall_risk, auto_adjustments}
    """
    cdi = intel.get("cdi", 0.5)
    hype = intel.get("hype_momentum", 0.5)
    velocity = intel.get("avg_engagement_velocity", 0.5)
    sentiment = intel.get("avg_sentiment", 0.5)
    genre = intel.get("genre", "Drama")
    competition_intel = intel.get("competition_intel", {})

    shocks: List[Dict] = []
    adjustments: List[str] = []

    # 1. Competitor surge (CDI > 0.7)
    if cdi > 0.7:
        shocks.append({
            "type": "COMPETITOR_SURGE",
            "severity": "HIGH",
            "description": f"Competition density at {cdi:.0%} — major releases saturating the market",
            "impact_on_discoverability": round(-0.15 * cdi, 4),
        })
        adjustments.append("Shift campaign focus to underserved regions")
        adjustments.append("Consider delaying release by 1-2 weeks")

    # 2. Engagement drop (velocity below threshold while hype was decent)
    if velocity < 0.3 and hype > 0.4:
        shocks.append({
            "type": "ENGAGEMENT_DROP",
            "severity": "MODERATE",
            "description": "Engagement velocity dropped despite healthy hype — possible audience fatigue",
            "impact_on_discoverability": round(-0.08, 4),
        })
        adjustments.append("Release fresh content (BTS, interviews, fan challenges)")
        adjustments.append("Reduce ad frequency to avoid audience fatigue")

    # 3. Sentiment crash
    if sentiment < 0.30:
        shocks.append({
            "type": "SENTIMENT_CRASH",
            "severity": "HIGH",
            "description": f"Audience sentiment critically low ({sentiment:.0%}) — possible backlash or controversy",
            "impact_on_discoverability": round(-0.12 * (1 - sentiment), 4),
        })
        adjustments.append("Monitor social media for specific complaints")
        adjustments.append("Prepare PR response if backlash detected")
        adjustments.append("Shift messaging strategy to highlight positive aspects")

    # 4. Genre fatigue
    genre_fatigue_risk = {
        "Horror": 0.6, "Thriller": 0.5, "Drama": 0.4, "Comedy": 0.3, "Action": 0.35,
        "Romance": 0.55, "Sci-Fi": 0.3, "Documentary": 0.2, "Animation": 0.25,
    }
    fatigue = genre_fatigue_risk.get(genre, 0.3)
    if fatigue > 0.45 and cdi > 0.5:
        shocks.append({
            "type": "GENRE_FATIGUE",
            "severity": "MODERATE",
            "description": f"{genre} genre showing fatigue signals ({fatigue:.0%} risk) combined with high competition",
            "impact_on_discoverability": round(-0.06 * fatigue, 4),
        })
        adjustments.append("Emphasize unique differentiators in marketing")
        adjustments.append("Cross-promote with adjacent genre audiences")

    # 5. Viral trend shift (high velocity but dropping sentiment = trend moving away)
    if velocity > 0.6 and sentiment < 0.45:
        shocks.append({
            "type": "TREND_SHIFT",
            "severity": "LOW",
            "description": "High velocity but declining sentiment — trend may be shifting to competitor content",
            "impact_on_discoverability": round(-0.04, 4),
        })
        adjustments.append("Analyze trending topics and align content")

    # Overall risk
    if not shocks:
        overall_risk = "STABLE"
    elif any(s["severity"] == "HIGH" for s in shocks):
        overall_risk = "HIGH"
    elif any(s["severity"] == "MODERATE" for s in shocks):
        overall_risk = "MODERATE"
    else:
        overall_risk = "LOW"

    if not adjustments:
        adjustments.append("Market conditions stable — no adjustments needed")

    return {
        "shocks_detected": len(shocks) > 0,
        "shock_count": len(shocks),
        "shock_list": shocks,
        "overall_risk": overall_risk,
        "auto_adjustments": adjustments,
    }

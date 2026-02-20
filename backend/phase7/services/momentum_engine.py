"""
Momentum Forecast Engine — Pre-release growth prediction.

Predicts hype trajectory, viral potential, and organic growth.
Considers: actor fanbase, trailer momentum, influencer impact,
sports/events clashes, political attention spikes.
"""

import hashlib
from typing import Dict, List


# Event clash calendar (simplified, deterministic)
MAJOR_EVENTS = {
    1: ["NFL Playoffs"], 2: ["Super Bowl", "Valentine's Day"],
    3: ["March Madness", "IPL Start"], 4: ["IPL", "Elections"],
    5: ["IPL Finals", "Summer Blockbusters"], 6: ["FIFA (if applicable)", "Wimbledon"],
    7: ["4th of July"], 8: ["Olympics (if applicable)"],
    9: ["Football Season Start"], 10: ["Cricket World Cup", "Halloween"],
    11: ["Thanksgiving", "Diwali"], 12: ["Christmas", "Year-End"],
}


def _talent_factor(intel: Dict) -> float:
    """Estimate talent pull factor."""
    talent = intel.get("project", None)
    strategy = "star_led"
    if talent:
        strategy = getattr(talent, "talent_strategy", "star_led")
    return {"star_led": 0.7, "ensemble": 0.5, "newcomer": 0.25, "director_driven": 0.55}.get(strategy, 0.4)


def forecast_momentum(intel: Dict) -> Dict:
    """
    4-week pre-release momentum forecast.

    Returns: {momentum_curve, viral_probability, organic_growth, suggestions, event_clashes}
    """
    hype = intel.get("hype_momentum", 0.5)
    velocity = intel.get("avg_engagement_velocity", 0.5)
    sentiment = intel.get("avg_sentiment", 0.5)
    platform_fit = intel.get("platform_fit", 0.5)
    cdi = intel.get("cdi", 0.5)
    talent = _talent_factor(intel)

    # Base growth rate
    base_growth = 0.15 * hype + 0.20 * velocity + 0.15 * sentiment + 0.10 * talent

    # 4-week momentum curve (each week builds on previous)
    curve = []
    val = max(0.1, hype * 0.6)
    for week in range(4):
        growth = base_growth * (1 + 0.15 * week)
        # Competition dampening
        growth *= (1 - 0.3 * cdi)
        val = min(1.0, val + growth)
        curve.append(round(val, 4))

    # Viral probability
    viral_prob = round(min(1.0,
        0.30 * velocity
        + 0.25 * sentiment
        + 0.20 * hype
        + 0.15 * (1 - cdi)
        + 0.10 * talent
    ), 4)

    # Organic growth
    organic = round(min(1.0,
        0.35 * sentiment
        + 0.30 * hype
        + 0.20 * velocity
        + 0.15 * talent
    ), 4)

    # Suggestions
    suggestions: List[str] = []
    if velocity < 0.4:
        suggestions.append("Drop trailer in Week 2 to spike velocity")
    if talent < 0.4:
        suggestions.append("Start influencer push 10 days before release")
    if cdi > 0.6:
        suggestions.append("Avoid clash with major competitor releases")
    if sentiment < 0.45:
        suggestions.append("Engage fan communities with BTS content")
    if hype > 0.6 and velocity > 0.5:
        suggestions.append("Capitalize on existing momentum — increase ad spend in Week 3")

    # Release month from timing
    best_month = intel.get("release_timing", {}).get("best_month", 6)
    events = MAJOR_EVENTS.get(best_month, [])
    if events:
        suggestions.append(f"Watch for event clashes in release month: {', '.join(events)}")

    return {
        "momentum_curve": curve,
        "viral_probability": viral_prob,
        "organic_growth": organic,
        "talent_factor": round(talent, 2),
        "suggestions": suggestions if suggestions else ["Momentum looks healthy — maintain current strategy"],
        "event_clashes": events,
    }

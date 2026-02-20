"""
Budget Efficiency Optimizer — Marginal ROI Engine.

Maximizes audience reach per ₹ by evaluating marginal gain
of each campaign channel: influencers, ads, festivals, regional push, trailer.
"""

from typing import Dict


def optimize_budget(intel: Dict, total_budget_lakhs: float = 100.0) -> Dict:
    """
    Compute optimal budget allocation across channels.

    Returns: {optimal_allocation, expected_reach_gain, channel_details, efficiency_score}
    """
    hype = intel.get("hype_momentum", 0.5)
    velocity = intel.get("avg_engagement_velocity", 0.5)
    sentiment = intel.get("avg_sentiment", 0.5)
    regional = intel.get("regional_strength", 0.5)
    cdi = intel.get("cdi", 0.5)
    platform_fit = intel.get("platform_fit", 0.5)
    release_mode = intel.get("release_mode", "ott")
    budget_level = intel.get("budget_level", "medium")

    # Marginal ROI per channel (higher = more efficient)
    influencer_roi = 0.35 * (1 - hype) + 0.25 * velocity + 0.20 * sentiment
    ads_roi = 0.30 * platform_fit + 0.25 * (1 - cdi) + 0.15 * hype
    festival_roi = 0.25 * regional + 0.20 * (1 - cdi)
    regional_roi = 0.30 * regional + 0.20 * (1 - hype) + 0.15
    trailer_roi = 0.25 * (1 - velocity) + 0.20 * (1 - sentiment) + 0.15

    # Theatrical boost for festivals
    if release_mode in ("theatre", "hybrid"):
        festival_roi *= 1.3
        ads_roi *= 1.1

    # Low budget = prioritize organic
    if budget_level == "low":
        influencer_roi *= 1.2
        trailer_roi *= 1.2
        ads_roi *= 0.7

    # Normalize to allocation percentages
    total = influencer_roi + ads_roi + festival_roi + regional_roi + trailer_roi
    if total == 0:
        total = 1.0

    allocation = {
        "influencer": round(influencer_roi / total, 4),
        "ads": round(ads_roi / total, 4),
        "festivals": round(festival_roi / total, 4),
        "regional": round(regional_roi / total, 4),
        "trailer": round(trailer_roi / total, 4),
    }

    # Expected reach gain
    expected_reach = round(min(1.0,
        allocation["influencer"] * 0.35
        + allocation["ads"] * 0.30
        + allocation["festivals"] * 0.15
        + allocation["regional"] * 0.25
        + allocation["trailer"] * 0.20
    ), 4)

    # Channel details
    channels = [
        {"channel": "Influencer Push", "allocation_pct": allocation["influencer"],
         "budget_lakhs": round(total_budget_lakhs * allocation["influencer"], 1),
         "marginal_roi": round(influencer_roi, 4),
         "rationale": "High impact for low-hype films, builds authentic engagement"},
        {"channel": "Digital Ads", "allocation_pct": allocation["ads"],
         "budget_lakhs": round(total_budget_lakhs * allocation["ads"], 1),
         "marginal_roi": round(ads_roi, 4),
         "rationale": "Best when platform fit is high and competition is low"},
        {"channel": "Festival Circuit", "allocation_pct": allocation["festivals"],
         "budget_lakhs": round(total_budget_lakhs * allocation["festivals"], 1),
         "marginal_roi": round(festival_roi, 4),
         "rationale": "Strong for regional audiences and theatrical releases"},
        {"channel": "Regional Push", "allocation_pct": allocation["regional"],
         "budget_lakhs": round(total_budget_lakhs * allocation["regional"], 1),
         "marginal_roi": round(regional_roi, 4),
         "rationale": "Targets underserved high-demand regions"},
        {"channel": "Trailer Promotion", "allocation_pct": allocation["trailer"],
         "budget_lakhs": round(total_budget_lakhs * allocation["trailer"], 1),
         "marginal_roi": round(trailer_roi, 4),
         "rationale": "Critical for low-velocity, low-sentiment films"},
    ]

    efficiency = round(expected_reach / max(0.01, 1 - cdi), 4)

    return {
        "optimal_allocation": allocation,
        "expected_reach_gain": expected_reach,
        "efficiency_score": min(1.0, efficiency),
        "total_budget_lakhs": total_budget_lakhs,
        "channel_details": channels,
    }

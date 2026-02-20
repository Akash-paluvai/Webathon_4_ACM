"""
Failure Recovery Engine.

If discoverability drops post-release, suggests recovery actions:
emergency campaign shift, region pivot, platform promotion request,
trailer re-cut, dubbing acceleration.
"""

from typing import Dict, List


def compute_recovery(intel: Dict, current_discoverability: float = 0.0) -> Dict:
    """
    Suggest recovery actions when discoverability is low.

    Returns: {recovery_trigger, severity, actions, expected_recovery_gain}
    """
    hype = intel.get("hype_momentum", 0.5)
    velocity = intel.get("avg_engagement_velocity", 0.5)
    regional = intel.get("regional_strength", 0.5)
    cdi = intel.get("cdi", 0.5)
    dubbing_gain = intel.get("dubbing_gain", 0.0)
    sentiment = intel.get("avg_sentiment", 0.5)
    platform_fit = intel.get("platform_fit", 0.5)

    # Trigger recovery if discoverability is below threshold
    trigger = current_discoverability < 0.45
    severity = (
        "CRITICAL" if current_discoverability < 0.25 else
        "HIGH" if current_discoverability < 0.35 else
        "MODERATE" if current_discoverability < 0.45 else
        "LOW"
    )

    actions: List[Dict] = []
    total_gain = 0.0

    # Region pivot — find underserved high-demand regions
    regions = intel.get("normalized_regions", [])
    secondary = [r for r in regions[1:4] if r.get("normalized_score", 0) > 0.4]
    if secondary:
        gain = 0.04 * len(secondary)
        total_gain += gain
        actions.append({
            "action": f"Boost {', '.join(r['region'] for r in secondary)} with targeted ads",
            "expected_gain": round(gain, 4),
            "priority": "HIGH",
            "cost": "medium",
        })

    # Influencer push
    if velocity < 0.45:
        gain = 0.05
        total_gain += gain
        actions.append({
            "action": "Emergency influencer push — micro-influencers for authentic engagement",
            "expected_gain": round(gain, 4),
            "priority": "HIGH",
            "cost": "medium",
        })

    # Trailer re-cut
    if sentiment < 0.45:
        gain = 0.03
        total_gain += gain
        actions.append({
            "action": "Release alternate trailer cut with stronger emotional hook",
            "expected_gain": round(gain, 4),
            "priority": "MODERATE",
            "cost": "low",
        })

    # Dubbing acceleration
    if dubbing_gain > 0.1:
        gain = 0.04
        total_gain += gain
        actions.append({
            "action": "Accelerate dubbing for high-demand language markets",
            "expected_gain": round(gain, 4),
            "priority": "HIGH",
            "cost": "high",
        })

    # Platform promotion request
    if platform_fit > 0.55:
        gain = 0.06
        total_gain += gain
        actions.append({
            "action": "Request homepage banner placement from platform",
            "expected_gain": round(gain, 4),
            "priority": "MODERATE",
            "cost": "negotiation",
        })

    # Competition avoidance
    if cdi > 0.6:
        gain = 0.03
        total_gain += gain
        actions.append({
            "action": "Shift promotion timing to avoid peak competition window",
            "expected_gain": round(gain, 4),
            "priority": "MODERATE",
            "cost": "low",
        })

    if not actions:
        actions.append({
            "action": "Maintain current strategy — no critical recovery needed",
            "expected_gain": 0.0,
            "priority": "LOW",
            "cost": "none",
        })

    return {
        "recovery_trigger": trigger,
        "severity": severity,
        "current_discoverability": current_discoverability,
        "actions": actions,
        "expected_recovery_gain": round(min(0.30, total_gain), 4),
    }

"""
Discovery Barrier Analyzer — Diagnosis Engine.

Identifies WHY discoverability is low by analyzing competition barrier,
audience mismatch, platform saturation, weak trailer hook, low hype momentum.
"""

from typing import Dict, List


def analyze_barriers(intel: Dict, discoverability_score: float) -> Dict:
    """
    Diagnose barriers to discoverability.

    Returns: {barriers, barrier_details, overall_barrier_score}
    """
    barriers: List[str] = []
    details: List[Dict] = []

    cdi = intel.get("cdi", 0.5)
    hype = intel.get("hype_momentum", 0.5)
    velocity = intel.get("avg_engagement_velocity", 0.5)
    sentiment = intel.get("avg_sentiment", 0.5)
    platform_fit = intel.get("platform_fit", 0.5)
    regional = intel.get("regional_strength", 0.5)
    release_mode = intel.get("release_mode", "ott")

    # Competition barrier
    if cdi > 0.55:
        barriers.append("High competition density")
        details.append({
            "barrier": "High competition density",
            "severity": round(cdi, 2),
            "impact": "Reduces visibility in platform algorithms and audience attention",
            "fix": "Shift release date or narrow target to niche audience",
        })

    # Weak engagement
    if velocity < 0.40:
        barriers.append("Weak early engagement")
        details.append({
            "barrier": "Weak early engagement",
            "severity": round(1 - velocity, 2),
            "impact": "Platform algorithms deprioritize low-engagement content",
            "fix": "Increase social media presence, run engagement campaigns",
        })

    # Low hype
    if hype < 0.35:
        barriers.append("Low hype momentum")
        details.append({
            "barrier": "Low hype momentum",
            "severity": round(1 - hype, 2),
            "impact": "Content doesn't appear in trending/recommended sections",
            "fix": "Drop viral clip, engage influencers, create challenge content",
        })

    # Platform genre saturation
    if platform_fit < 0.50 and release_mode == "ott":
        barriers.append("Platform genre saturation")
        details.append({
            "barrier": "Platform genre saturation",
            "severity": round(1 - platform_fit, 2),
            "impact": "Too many similar titles compete for the same recommendation slots",
            "fix": "Consider alternative platform or hybrid release",
        })

    # Audience mismatch
    if regional < 0.40:
        barriers.append("Audience-market mismatch")
        details.append({
            "barrier": "Audience-market mismatch",
            "severity": round(1 - regional, 2),
            "impact": "Target audience is not in the regions with highest platform activity",
            "fix": "Expand dubbing, localize marketing, adjust target regions",
        })

    # Weak trailer hook
    if sentiment < 0.40 and velocity < 0.45:
        barriers.append("Weak trailer hook")
        details.append({
            "barrier": "Weak trailer hook",
            "severity": round((1 - sentiment + 1 - velocity) / 2, 2),
            "impact": "Trailer fails to convert impressions into engagement",
            "fix": "Re-cut trailer with stronger first 5 seconds, A/B test thumbnails",
        })

    overall = round(sum(d["severity"] for d in details) / max(1, len(details)), 4) if details else 0.0

    if not barriers:
        barriers = ["No significant barriers detected"]
        details = [{"barrier": "Clear path", "severity": 0, "impact": "Discoverability channel is healthy", "fix": "Maintain current strategy"}]

    return {
        "barriers": barriers,
        "barrier_details": details,
        "overall_barrier_score": overall,
        "discoverability_score": discoverability_score,
    }

"""
Dubbing Engine — determines whether dubbing is needed and recommends target languages.
"""

from typing import Dict, List


# Dubbing cost tiers (relative)
DUBBING_COSTS = {
    "hindi": {"cost": "low", "market_size": 0.9},
    "telugu": {"cost": "low", "market_size": 0.6},
    "tamil": {"cost": "low", "market_size": 0.55},
    "spanish": {"cost": "medium", "market_size": 0.85},
    "portuguese": {"cost": "medium", "market_size": 0.5},
    "french": {"cost": "medium", "market_size": 0.45},
    "german": {"cost": "medium", "market_size": 0.4},
    "korean": {"cost": "high", "market_size": 0.5},
    "japanese": {"cost": "high", "market_size": 0.55},
    "mandarin": {"cost": "high", "market_size": 0.95},
    "arabic": {"cost": "medium", "market_size": 0.4},
    "english": {"cost": "medium", "market_size": 1.0},
}

# Language families (languages that don't need dubbing for each other)
LANGUAGE_FAMILIES = {
    "hindi": {"hindi", "urdu"},
    "english": {"english"},
    "korean": {"korean"},
    "spanish": {"spanish"},
    "tamil": {"tamil"},
    "telugu": {"telugu"},
}


def _get_candidate_languages(original_language: str) -> List[str]:
    """Return languages that the film could be dubbed into (excluding original)."""
    original_lower = original_language.lower()
    skip = LANGUAGE_FAMILIES.get(original_lower, {original_lower})
    return [lang for lang in DUBBING_COSTS if lang not in skip]


def _compute_roi_uplift(
    target_lang: str,
    audience_type: str,
    scale: str,
    budget_level: str,
) -> float:
    """Estimate revenue uplift % from dubbing into a target language."""
    market_size = DUBBING_COSTS[target_lang]["market_size"]

    audience_multiplier = {"niche": 0.3, "broad": 0.7, "mainstream": 1.0}.get(audience_type, 0.5)
    scale_multiplier = {"indie": 0.4, "studio": 0.7, "blockbuster": 1.0}.get(scale, 0.5)
    budget_multiplier = {"low": 0.5, "medium": 0.8, "high": 1.0}.get(budget_level, 0.5)

    uplift = market_size * audience_multiplier * scale_multiplier * budget_multiplier * 25  # max ~25%
    return round(uplift, 2)


def _prioritize(roi_uplift: float) -> str:
    """Assign priority based on ROI uplift."""
    if roi_uplift >= 12:
        return "high"
    elif roi_uplift >= 5:
        return "medium"
    return "low"


def analyze_dubbing_need(
    original_language: str,
    audience_type: str,
    scale: str,
    budget_level: str,
    distribution_confidence: str,
) -> Dict:
    """
    Analyze whether dubbing is needed and generate recommendations.

    Returns dict with needs_dubbing, recommendations, estimated_total_cost_tier.
    """
    candidates = _get_candidate_languages(original_language)

    recommendations = []
    for lang in candidates:
        uplift = _compute_roi_uplift(lang, audience_type, scale, budget_level)
        priority = _prioritize(uplift)

        if priority in ("high", "medium"):
            cost_info = DUBBING_COSTS[lang]["cost"]
            recommendations.append({
                "target_language": lang,
                "priority": priority,
                "estimated_roi_uplift": uplift,
                "rationale": (
                    f"{lang.capitalize()} market has {DUBBING_COSTS[lang]['market_size']:.0%} "
                    f"relative size. {cost_info.capitalize()} dubbing cost with estimated "
                    f"{uplift}% revenue uplift."
                ),
            })

    # Sort by ROI uplift
    recommendations.sort(key=lambda x: x["estimated_roi_uplift"], reverse=True)

    needs_dubbing = len(recommendations) > 0

    # Estimate total cost tier
    if not recommendations:
        total_cost = "low"
    elif len(recommendations) <= 2:
        total_cost = "low"
    elif len(recommendations) <= 5:
        total_cost = "medium"
    else:
        total_cost = "high"

    # Override: if distribution confidence is low, dubbing may not be worth it
    if distribution_confidence == "low" and not any(r["priority"] == "high" for r in recommendations):
        needs_dubbing = False
        recommendations = []
        total_cost = "low"

    return {
        "needs_dubbing": needs_dubbing,
        "recommendations": recommendations,
        "estimated_total_cost_tier": total_cost,
    }

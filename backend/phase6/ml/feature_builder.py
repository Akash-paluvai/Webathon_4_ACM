"""
Feature Builder — builds a feature vector from a FilmProject model for ML inference.
"""

from typing import Dict


# Categorical → numeric encodings
SCALE_MAP = {"indie": 0, "studio": 1, "blockbuster": 2}
BUDGET_MAP = {"low": 0, "medium": 1, "high": 2}
TALENT_MAP = {"unknown": 0, "emerging": 1, "established": 2, "starDriven": 3}
AUDIENCE_MAP = {"niche": 0, "broad": 1, "mainstream": 2}
RELEASE_MAP = {"theatre": 0, "ott": 1, "hybrid": 2}
CONFIDENCE_MAP = {"low": 0, "medium": 1, "high": 2}
HEALTH_MAP = {"good": 2, "atRisk": 1, "critical": 0}
MARKETING_BUDGET_MAP = {"unassigned": 0, "low": 1, "medium": 2, "high": 3}
MARKETING_CHANNEL_MAP = {"undefined": 0, "influencer": 1, "festival": 2, "digitalAds": 3, "pr": 4}


def build_feature_vector(project: Dict) -> Dict[str, float]:
    """
    Build a flat feature dict from a FilmProject.

    Args:
        project: dict with FilmProject fields (camelCase keys from the API).

    Returns:
        Feature vector as {feature_name: numeric_value}.
    """
    features = {
        "scale": float(SCALE_MAP.get(project.get("scale", ""), 1)),
        "budget_level": float(BUDGET_MAP.get(project.get("budgetLevel", ""), 1)),
        "talent_strategy": float(TALENT_MAP.get(project.get("talentStrategy", ""), 1)),
        "planned_shoot_days": float(project.get("plannedShootDays", 30)),
        "audience_type": float(AUDIENCE_MAP.get(project.get("audienceType", ""), 1)),
        "release_model": float(RELEASE_MAP.get(project.get("releaseModel", ""), 1)),
        "distribution_confidence": float(CONFIDENCE_MAP.get(project.get("distributionConfidence", ""), 1)),
        "production_health": float(HEALTH_MAP.get(project.get("productionHealth", ""), 2)),
        "marketing_budget_level": float(MARKETING_BUDGET_MAP.get(project.get("marketingBudgetLevel", ""), 0)),
        "marketing_channel": float(MARKETING_CHANNEL_MAP.get(project.get("primaryMarketingChannel", ""), 0)),
        "current_phase": float(project.get("currentPhase", 1)),
    }

    # Derived features
    if project.get("actualShootDays") and project.get("plannedShootDays"):
        features["shoot_day_ratio"] = float(project["actualShootDays"]) / max(1, float(project["plannedShootDays"]))
    else:
        features["shoot_day_ratio"] = 1.0

    return features

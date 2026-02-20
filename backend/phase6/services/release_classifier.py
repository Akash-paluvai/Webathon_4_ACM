"""
Release Classifier — classifies the optimal release mode for a film project.

Returns both the recommended mode AND probability distribution across all modes.
"""

from typing import Dict
from phase6.utils.scoring_utils import weighted_score


def classify_release_mode(
    scale: str,
    budget_level: str,
    audience_type: str,
    talent_strategy: str,
    release_model: str,
    distribution_confidence: str,
    top_platform: str,
) -> str:
    """
    Classify the recommended release mode.
    Returns one of: "theatre", "ott", "hybrid", "festival_circuit".
    """
    result = classify_release_mode_with_probabilities(
        scale, budget_level, audience_type, talent_strategy,
        release_model, distribution_confidence, top_platform,
    )
    return result["mode"]


def classify_release_mode_with_probabilities(
    scale: str,
    budget_level: str,
    audience_type: str,
    talent_strategy: str,
    release_model: str,
    distribution_confidence: str,
    top_platform: str,
) -> Dict:
    """
    Classify the recommended release mode with full probability distribution.

    Returns:
        {mode, probabilities: {theatre, ott, hybrid, festival_circuit}, features}
    """
    mode_scores = {}

    # Feature extraction
    features = {
        "scale": scale,
        "budget": budget_level,
        "audience": audience_type,
        "talent": talent_strategy,
        "confidence": distribution_confidence,
        "user_preference": release_model,
        "top_platform": top_platform,
    }

    # ── Theatre score ──
    theatre_factors = {
        "scale": {"indie": 0.1, "studio": 0.6, "blockbuster": 1.0}.get(scale, 0.4),
        "budget": {"low": 0.1, "medium": 0.5, "high": 0.9}.get(budget_level, 0.4),
        "audience": {"niche": 0.1, "broad": 0.5, "mainstream": 0.9}.get(audience_type, 0.4),
        "talent": {"unknown": 0.1, "emerging": 0.3, "established": 0.7, "starDriven": 1.0}.get(talent_strategy, 0.3),
        "confidence": {"low": 0.2, "medium": 0.5, "high": 0.9}.get(distribution_confidence, 0.4),
    }
    weights = {"scale": 0.25, "budget": 0.20, "audience": 0.20, "talent": 0.20, "confidence": 0.15}
    mode_scores["theatre"] = weighted_score(theatre_factors, weights)

    # ── OTT score ──
    ott_factors = {
        "scale": {"indie": 0.7, "studio": 0.5, "blockbuster": 0.3}.get(scale, 0.5),
        "budget": {"low": 0.8, "medium": 0.6, "high": 0.3}.get(budget_level, 0.5),
        "audience": {"niche": 0.7, "broad": 0.6, "mainstream": 0.5}.get(audience_type, 0.5),
        "talent": {"unknown": 0.6, "emerging": 0.6, "established": 0.5, "starDriven": 0.4}.get(talent_strategy, 0.5),
        "confidence": {"low": 0.6, "medium": 0.6, "high": 0.5}.get(distribution_confidence, 0.5),
    }
    mode_scores["ott"] = weighted_score(ott_factors, weights)

    # ── Hybrid score ──
    mode_scores["hybrid"] = (mode_scores["theatre"] + mode_scores["ott"]) / 2 + 0.05

    # ── Festival circuit score ──
    festival_factors = {
        "scale": {"indie": 0.9, "studio": 0.2, "blockbuster": 0.05}.get(scale, 0.3),
        "budget": {"low": 0.8, "medium": 0.3, "high": 0.05}.get(budget_level, 0.3),
        "audience": {"niche": 0.9, "broad": 0.3, "mainstream": 0.1}.get(audience_type, 0.3),
        "talent": {"unknown": 0.7, "emerging": 0.8, "established": 0.3, "starDriven": 0.1}.get(talent_strategy, 0.4),
        "confidence": {"low": 0.7, "medium": 0.4, "high": 0.2}.get(distribution_confidence, 0.4),
    }
    mode_scores["festival_circuit"] = weighted_score(festival_factors, weights)

    # User preference boost
    user_pref_boost = 0.08
    if release_model in mode_scores:
        mode_scores[release_model] += user_pref_boost

    # Softmax-like normalization to get probabilities summing to ~1
    # Use exponential scaling for sharper probabilities
    import math
    temperature = 3.0
    exp_scores = {m: math.exp(s * temperature) for m, s in mode_scores.items()}
    total_exp = sum(exp_scores.values())
    probabilities = {m: round(e / total_exp, 4) for m, e in exp_scores.items()}

    best = max(mode_scores, key=mode_scores.get)

    return {
        "mode": best,
        "probabilities": probabilities,
        "features": features,
    }


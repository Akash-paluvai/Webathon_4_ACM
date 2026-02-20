"""
Audience Conversion Probability Engine.

Predicts: who watches vs ignores, engagement depth, word-of-mouth probability.
"""

from typing import Dict


def predict_conversion(intel: Dict) -> Dict:
    """
    Predict audience conversion metrics.

    Returns: {conversion_probability, engagement_depth, word_of_mouth,
              conversion_breakdown, audience_quality}
    """
    hype = intel.get("hype_momentum", 0.5)
    sentiment = intel.get("avg_sentiment", 0.5)
    velocity = intel.get("avg_engagement_velocity", 0.5)
    platform_fit = intel.get("platform_fit", 0.5)
    regional = intel.get("regional_strength", 0.5)
    cdi = intel.get("cdi", 0.5)

    # Talent factor
    talent = intel.get("project", None)
    strategy = "star_led"
    if talent:
        strategy = getattr(talent, "talent_strategy", "star_led")
    talent_pull = {"star_led": 0.7, "ensemble": 0.5, "newcomer": 0.25, "director_driven": 0.55}.get(strategy, 0.4)

    # Conversion probability: who actually clicks and watches
    conversion = round(min(1.0,
        0.25 * hype
        + 0.20 * sentiment
        + 0.20 * platform_fit
        + 0.15 * velocity
        + 0.10 * talent_pull
        + 0.10 * regional
    ), 4)

    # Engagement depth: how deeply they engage (watch full, rate, etc.)
    engagement_depth = round(min(1.0,
        0.30 * sentiment
        + 0.25 * velocity
        + 0.20 * (1 - cdi)  # Less competition = more attention
        + 0.15 * hype
        + 0.10 * talent_pull
    ), 4)

    # Word of mouth: organic sharing
    word_of_mouth = round(min(1.0,
        0.35 * sentiment
        + 0.25 * velocity
        + 0.20 * hype
        + 0.10 * (1 - cdi)
        + 0.10 * talent_pull
    ), 4)

    # Quality grade
    avg = (conversion + engagement_depth + word_of_mouth) / 3
    quality = (
        "Excellent" if avg >= 0.7 else
        "Good" if avg >= 0.55 else
        "Average" if avg >= 0.40 else
        "Below Average" if avg >= 0.25 else
        "Poor"
    )

    return {
        "conversion_probability": conversion,
        "engagement_depth": engagement_depth,
        "word_of_mouth": word_of_mouth,
        "audience_quality": quality,
        "conversion_breakdown": {
            "hype_influence": round(0.25 * hype, 4),
            "sentiment_influence": round(0.20 * sentiment, 4),
            "platform_match": round(0.20 * platform_fit, 4),
            "velocity_signal": round(0.15 * velocity, 4),
            "talent_pull": round(0.10 * talent_pull, 4),
            "regional_match": round(0.10 * regional, 4),
        },
    }

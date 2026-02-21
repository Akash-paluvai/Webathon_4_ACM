"""
Demand Forecast Model — Feature Engineering & Scoring.

Lightweight scoring heuristics for demand forecasting.
No external ML dependencies — pure Python computation.
"""

from typing import Dict, List, Tuple
import math


# ── Revenue class thresholds ─────────────────────────────────

REVENUE_CLASSES = [
    (0.80, "blockbuster"),
    (0.60, "hit"),
    (0.40, "average"),
    (0.0, "underperformer"),
]


def extract_features(intel: Dict, sentiment_data: Dict, piracy_data: Dict) -> Dict[str, float]:
    """
    Build a feature vector from intel + sentiment + piracy signals.
    All features are normalized 0–1.
    """
    return {
        "social_score": sentiment_data.get("social_score", 0.5),
        "search_score": sentiment_data.get("search_score", 0.5),
        "engagement_score": sentiment_data.get("engagement_score", 0.5),
        "hype_momentum": intel.get("hype_momentum", 0.5),
        "platform_fit": intel.get("platform_fit", 0.5),
        "regional_strength": intel.get("regional_strength", 0.5),
        "cdi": intel.get("cdi", 0.5),
        "leverage": intel.get("leverage", 0.5),
        "release_timing_score": intel.get("release_timing_score", 0.5),
        "dubbing_gain": min(1.0, intel.get("dubbing_gain", 0.0)),
        "piracy_demand_signal": piracy_data.get("demand_signal", 0.5),
        "avg_sentiment": intel.get("avg_sentiment", 0.5),
        "avg_velocity": intel.get("avg_engagement_velocity", 0.5),
    }


def compute_demand_score(features: Dict[str, float]) -> float:
    """
    Compute raw demand score (0–1) from feature vector.

    Weighted combination tuned for pre-release prediction:
      Social (0.20) + Search (0.15) + Engagement (0.15) +
      Hype (0.12) + Platform (0.10) + Regional (0.08) +
      Timing (0.07) + Leverage (0.05) + Piracy (0.05) + Sentiment (0.03)
    """
    weights = {
        "social_score": 0.20,
        "search_score": 0.15,
        "engagement_score": 0.15,
        "hype_momentum": 0.12,
        "platform_fit": 0.10,
        "regional_strength": 0.08,
        "release_timing_score": 0.07,
        "leverage": 0.05,
        "piracy_demand_signal": 0.05,
        "avg_sentiment": 0.03,
    }

    score = sum(weights.get(k, 0) * features.get(k, 0.5) for k in weights)
    return round(max(0.0, min(1.0, score)), 4)


def classify_revenue(demand_score: float) -> Tuple[str, float]:
    """
    Map demand score to revenue class with confidence.
    """
    for threshold, label in REVENUE_CLASSES:
        if demand_score >= threshold:
            # Confidence is higher when score is further from the threshold
            margin = demand_score - threshold
            confidence = round(min(1.0, 0.6 + margin * 2), 4)
            return label, confidence
    return "underperformer", 0.6


def generate_demand_curve(
    features: Dict[str, float],
    days: int = 30
) -> List[Dict]:
    """
    Generate a 30-day demand projection curve.

    Uses momentum-based growth model with competition dampening
    and sentiment-driven peaks.
    """
    base = compute_demand_score(features)
    hype = features.get("hype_momentum", 0.5)
    velocity = features.get("avg_velocity", 0.5)
    cdi = features.get("cdi", 0.5)
    sentiment = features.get("avg_sentiment", 0.5)

    curve = []
    val = base * 0.6  # Start at 60% of predicted demand

    for day in range(1, days + 1):
        # Growth rate: faster early, plateaus later
        growth_rate = (hype * 0.3 + velocity * 0.2) * (1 - day / (days * 1.5))

        # Mid-campaign spike (around day 15–20) from trailer/promo effects
        spike = 0.0
        if 14 <= day <= 20:
            spike = sentiment * 0.08 * math.sin((day - 14) * math.pi / 6)

        # Competition dampening
        dampen = cdi * 0.15 * (day / days)

        val = val + growth_rate * 0.03 + spike - dampen * 0.01
        val = max(0.05, min(1.0, val))

        curve.append({
            "day": day,
            "demand": round(val, 4),
            "label": f"Day {day}",
        })

    return curve


def estimate_opening_week(features: Dict[str, float]) -> Dict:
    """
    Estimate opening week engagement metrics.
    """
    demand = compute_demand_score(features)
    social = features.get("social_score", 0.5)
    hype = features.get("hype_momentum", 0.5)

    # Opening week engagement is amplified by social buzz and hype
    engagement = round(min(1.0, demand * 0.5 + social * 0.3 + hype * 0.2), 4)

    # Day-by-day opening week
    daily = []
    for d in range(1, 8):
        # Day 1 strongest, gradual decay
        decay = 1.0 - (d - 1) * 0.08
        day_val = round(engagement * decay * (0.9 + 0.2 * (1 if d <= 2 else 0)), 4)
        daily.append({"day": d, "engagement": min(1.0, day_val)})

    return {
        "opening_week_engagement": engagement,
        "daily_projection": daily,
        "strength": (
            "Explosive opening" if engagement >= 0.75 else
            "Strong opening" if engagement >= 0.55 else
            "Moderate opening" if engagement >= 0.35 else
            "Slow build"
        ),
    }

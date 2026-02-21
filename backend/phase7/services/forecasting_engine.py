"""
Forecasting Engine — Demand Forecasting & Projections.

Orchestrates the demand_forecast_model to produce:
  - 30-day demand projection curve
  - Opening week engagement estimate
  - Revenue class prediction
  - Confidence intervals
"""

from typing import Dict
from phase7.services.sentiment_engine import analyze_sentiment
from phase7.services.piracy_signal import compute_piracy_signal
from phase7.ml.demand_forecast_model import (
    extract_features, compute_demand_score, classify_revenue,
    generate_demand_curve, estimate_opening_week,
)


def _compute_confidence(features: Dict[str, float], demand_score: float) -> float:
    """
    Confidence in forecast based on signal coverage and consistency.
    Higher when multiple signals agree, lower when signals diverge.
    """
    scores = [
        features.get("social_score", 0.5),
        features.get("search_score", 0.5),
        features.get("engagement_score", 0.5),
        features.get("hype_momentum", 0.5),
    ]

    # Measure consistency (lower std = higher confidence)
    mean = sum(scores) / len(scores)
    variance = sum((s - mean) ** 2 for s in scores) / len(scores)
    std = variance ** 0.5

    # Confidence: high when signals agree and demand is clear
    base_confidence = 0.5
    consistency_bonus = max(0, 0.3 - std)  # Up to 0.3 bonus
    signal_strength = min(0.2, demand_score * 0.25)  # Stronger signals = more confident

    confidence = round(min(1.0, base_confidence + consistency_bonus + signal_strength), 4)
    return confidence


def forecast_demand(intel: Dict) -> Dict:
    """
    Full demand forecast pipeline.

    Returns:
        {
            demand_score: float,
            demand_curve_30d: [...],
            opening_week: {...},
            revenue_class: str,
            revenue_confidence: float,
            forecast_confidence: float,
            features_used: {...},
        }
    """
    try:
        # Get upstream signals
        sentiment = analyze_sentiment(intel)
        piracy = compute_piracy_signal(intel)

        # Extract features
        features = extract_features(intel, sentiment, piracy)

        # Compute demand score
        demand_score = compute_demand_score(features)

        # Revenue classification
        revenue_class, revenue_confidence = classify_revenue(demand_score)

        # 30-day demand curve
        curve = generate_demand_curve(features, days=30)

        # Opening week
        opening = estimate_opening_week(features)

        # Forecast confidence
        confidence = _compute_confidence(features, demand_score)

        return {
            "demand_score": demand_score,
            "demand_curve_30d": curve,
            "opening_week": opening,
            "revenue_class": revenue_class,
            "revenue_confidence": revenue_confidence,
            "forecast_confidence": confidence,
            "features_used": features,
            "interpretation": (
                "Very strong demand predicted" if demand_score >= 0.75 else
                "Good demand trajectory" if demand_score >= 0.55 else
                "Moderate demand expected" if demand_score >= 0.35 else
                "Weak demand signals"
            ),
        }

    except Exception:
        # Fallback
        return {
            "demand_score": 0.5,
            "demand_curve_30d": [{"day": d, "demand": 0.5, "label": f"Day {d}"} for d in range(1, 31)],
            "opening_week": {
                "opening_week_engagement": 0.5,
                "daily_projection": [{"day": d, "engagement": 0.5} for d in range(1, 8)],
                "strength": "Moderate opening",
            },
            "revenue_class": "average",
            "revenue_confidence": 0.5,
            "forecast_confidence": 0.4,
            "features_used": {},
            "interpretation": "Fallback forecast — insufficient signals",
        }

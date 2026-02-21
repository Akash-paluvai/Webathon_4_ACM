"""
Demand Engine — DSI Orchestrator.

Computes the Demand Strength Index (DSI) by combining:
  - SocialScore (0.30)
  - SearchScore (0.25)
  - EngagementScore (0.20)
  - Momentum (0.15)
  - PiracySignal (0.10)

Also produces DemandTrend, HypeQuality, RegionalDemand, and recommendations.
"""

from typing import Dict, List
from phase7.services.sentiment_engine import analyze_sentiment
from phase7.services.piracy_signal import compute_piracy_signal
from phase7.services.forecasting_engine import forecast_demand


# ── DSI Grading ──────────────────────────────────────────────

def _grade_dsi(score: int) -> str:
    if score >= 85:
        return "A+"
    if score >= 75:
        return "A"
    if score >= 65:
        return "B+"
    if score >= 55:
        return "B"
    if score >= 45:
        return "C"
    if score >= 30:
        return "D"
    return "F"


# ── Demand Trend ─────────────────────────────────────────────

def _compute_demand_trend(intel: Dict, momentum_score: float) -> Dict:
    """Classify demand trajectory as rising / stable / declining."""
    hype = intel.get("hype_momentum", 0.5)
    velocity = intel.get("avg_engagement_velocity", 0.5)

    # Trend is based on momentum direction
    trend_score = (hype * 0.5 + velocity * 0.3 + momentum_score * 0.2)

    if trend_score >= 0.6:
        trend = "rising"
        description = "Demand is accelerating — audience interest is growing"
    elif trend_score >= 0.4:
        trend = "stable"
        description = "Demand is holding steady — consistent audience interest"
    else:
        trend = "declining"
        description = "Demand signals are weakening — consider engagement boosts"

    return {
        "trend": trend,
        "trend_score": round(trend_score, 4),
        "description": description,
    }


# ── Hype Quality ─────────────────────────────────────────────

def _compute_hype_quality(intel: Dict, social_score: float, engagement_score: float) -> Dict:
    """
    Classify hype as genuine vs manufactured.

    Genuine hype: high sentiment + high engagement + moderate social
    Manufactured: high social but low engagement or low sentiment
    """
    sentiment = intel.get("avg_sentiment", 0.5)

    # Divergence between social buzz and actual engagement
    divergence = abs(social_score - engagement_score)

    # Sentiment alignment
    sentiment_alignment = sentiment * 0.5 + engagement_score * 0.5

    if divergence < 0.15 and sentiment_alignment >= 0.5:
        classification = "genuine"
        confidence = round(min(1.0, 0.7 + sentiment_alignment * 0.3), 4)
        description = "Organic audience interest backed by real engagement"
    elif divergence < 0.25:
        classification = "mixed"
        confidence = round(0.5 + (0.25 - divergence), 4)
        description = "Some organic interest with promotional amplification"
    else:
        classification = "manufactured"
        confidence = round(min(1.0, 0.5 + divergence), 4)
        description = "Social buzz outpacing real engagement — likely promotional"

    return {
        "classification": classification,
        "confidence": confidence,
        "description": description,
        "metrics": {
            "social_engagement_divergence": round(divergence, 4),
            "sentiment_alignment": round(sentiment_alignment, 4),
        },
    }


# ── Regional Demand ──────────────────────────────────────────

def _compute_regional_demand(intel: Dict, dsi_score: int) -> List[Dict]:
    """
    Per-region demand strengths from Phase 6 normalized regions.
    """
    regions = intel.get("top_regions", [])
    normalized = intel.get("normalized_regions", [])

    if not regions and not normalized:
        # Fallback with basic regional estimate
        return [
            {"region": "Primary Market", "demand_strength": round(dsi_score / 100, 4), "tier": "high"},
        ]

    regional_demand = []
    for region in (normalized if normalized else regions):
        if isinstance(region, dict):
            name = region.get("region", region.get("name", "Unknown"))
            score = region.get("normalized_score", region.get("score", 0.5))

            # Adjust by DSI
            adjusted = round(min(1.0, score * (0.7 + 0.3 * dsi_score / 100)), 4)

            tier = (
                "high" if adjusted >= 0.65 else
                "medium" if adjusted >= 0.40 else
                "low"
            )

            regional_demand.append({
                "region": name,
                "demand_strength": adjusted,
                "tier": tier,
            })

    # Sort by demand strength descending
    regional_demand.sort(key=lambda r: r["demand_strength"], reverse=True)
    return regional_demand[:10]  # Top 10


# ── Recommendations ──────────────────────────────────────────

def _generate_recommendations(
    dsi: int,
    trend: str,
    hype_quality: str,
    piracy_level: str,
    forecast: Dict,
) -> List[Dict]:
    """Generate strategic recommendations based on demand intelligence."""
    recs = []

    # DSI-based
    if dsi >= 75:
        recs.append({
            "priority": "high",
            "category": "monetization",
            "action": "Strong demand — maximize pricing and premium release windows",
        })
    elif dsi >= 50:
        recs.append({
            "priority": "medium",
            "category": "audience_reach",
            "action": "Moderate demand — invest in targeted marketing to push into strong territory",
        })
    else:
        recs.append({
            "priority": "high",
            "category": "audience_reach",
            "action": "Weak demand — pivot strategy or delay release for better positioning",
        })

    # Trend-based
    if trend == "rising":
        recs.append({
            "priority": "medium",
            "category": "timing",
            "action": "Momentum is building — maintain cadence and release on schedule",
        })
    elif trend == "declining":
        recs.append({
            "priority": "high",
            "category": "timing",
            "action": "Demand declining — drop new trailer/content to reignite interest",
        })

    # Hype quality-based
    if hype_quality == "manufactured":
        recs.append({
            "priority": "high",
            "category": "discoverability",
            "action": "Hype is promotional-driven — invest in organic engagement (BTS, fan events)",
        })

    # Piracy-based
    if piracy_level == "high":
        recs.append({
            "priority": "medium",
            "category": "monetization",
            "action": "High piracy risk — prioritize day-1 global digital availability",
        })

    # Forecast-based
    revenue = forecast.get("revenue_class", "average")
    if revenue == "blockbuster":
        recs.append({
            "priority": "high",
            "category": "negotiation",
            "action": "Blockbuster projections — use demand data to negotiate premium platform deals",
        })
    elif revenue == "underperformer":
        recs.append({
            "priority": "high",
            "category": "strategy",
            "action": "Below-average forecast — consider repackaging or niche-market positioning",
        })

    return recs


# ══════════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════════

def compute_demand_intelligence(intel: Dict) -> Dict:
    """
    Full Demand Intelligence pipeline.

    Returns:
        {
            dsi: { score, grade, breakdown },
            demand_trend: { trend, trend_score, description },
            hype_quality: { classification, confidence, ... },
            regional_demand: [...],
            piracy_risk: { level, score, ... },
            forecast: { ... },
            recommendations: [...],
        }
    """
    try:
        # ── Upstream signals ──
        sentiment = analyze_sentiment(intel)
        piracy = compute_piracy_signal(intel)
        forecast = forecast_demand(intel)

        social_score = sentiment.get("social_score", 0.5)
        search_score = sentiment.get("search_score", 0.5)
        engagement_score = sentiment.get("engagement_score", 0.5)
        momentum = intel.get("hype_momentum", 0.5)
        piracy_signal = piracy.get("demand_signal", 0.5)

        # ── DSI calculation ──
        raw_dsi = (
            0.30 * social_score
            + 0.25 * search_score
            + 0.20 * engagement_score
            + 0.15 * momentum
            + 0.10 * piracy_signal
        )
        dsi_score = round(max(0, min(100, raw_dsi * 100)))
        dsi_grade = _grade_dsi(dsi_score)

        # ── Sub-analyses ──
        trend = _compute_demand_trend(intel, momentum)
        hype_quality = _compute_hype_quality(intel, social_score, engagement_score)
        regional = _compute_regional_demand(intel, dsi_score)

        # ── Recommendations ──
        recs = _generate_recommendations(
            dsi_score, trend["trend"], hype_quality["classification"],
            piracy["level"], forecast,
        )

        return {
            "dsi": {
                "score": dsi_score,
                "grade": dsi_grade,
                "breakdown": {
                    "social_buzz": round(0.30 * social_score * 100, 2),
                    "search_intent": round(0.25 * search_score * 100, 2),
                    "engagement_depth": round(0.20 * engagement_score * 100, 2),
                    "momentum": round(0.15 * momentum * 100, 2),
                    "piracy_signal": round(0.10 * piracy_signal * 100, 2),
                },
                "raw_signals": {
                    "social_score": social_score,
                    "search_score": search_score,
                    "engagement_score": engagement_score,
                    "momentum": momentum,
                    "piracy_signal": piracy_signal,
                },
            },
            "demand_trend": trend,
            "hype_quality": hype_quality,
            "regional_demand": regional,
            "piracy_risk": piracy,
            "forecast": {
                "demand_curve_30d": forecast.get("demand_curve_30d", []),
                "opening_week_engagement": forecast.get("opening_week", {}).get("opening_week_engagement", 0.5),
                "opening_week_detail": forecast.get("opening_week", {}),
                "revenue_class": forecast.get("revenue_class", "average"),
                "revenue_confidence": forecast.get("revenue_confidence", 0.5),
                "forecast_confidence": forecast.get("forecast_confidence", 0.5),
                "interpretation": forecast.get("interpretation", ""),
            },
            "recommendations": recs,
            "sentiment_detail": sentiment,
        }

    except Exception as e:
        # Full fallback
        return _fallback_response(str(e))


def _fallback_response(error_detail: str = "") -> Dict:
    """Graceful fallback when the pipeline fails."""
    return {
        "dsi": {
            "score": 50,
            "grade": "C",
            "breakdown": {
                "social_buzz": 15.0,
                "search_intent": 12.5,
                "engagement_depth": 10.0,
                "momentum": 7.5,
                "piracy_signal": 5.0,
            },
            "raw_signals": {
                "social_score": 0.5,
                "search_score": 0.5,
                "engagement_score": 0.5,
                "momentum": 0.5,
                "piracy_signal": 0.5,
            },
        },
        "demand_trend": {"trend": "stable", "trend_score": 0.5, "description": "Fallback estimate"},
        "hype_quality": {"classification": "mixed", "confidence": 0.5, "description": "Fallback estimate", "metrics": {}},
        "regional_demand": [{"region": "Primary Market", "demand_strength": 0.5, "tier": "medium"}],
        "piracy_risk": {"score": 0.5, "level": "medium", "demand_signal": 0.5, "factors": {}, "mitigations": []},
        "forecast": {
            "demand_curve_30d": [{"day": d, "demand": 0.5, "label": f"Day {d}"} for d in range(1, 31)],
            "opening_week_engagement": 0.5,
            "opening_week_detail": {},
            "revenue_class": "average",
            "revenue_confidence": 0.5,
            "forecast_confidence": 0.4,
            "interpretation": "Fallback forecast",
        },
        "recommendations": [{"priority": "medium", "category": "strategy", "action": "Insufficient data for detailed recommendations — gather more signals"}],
        "sentiment_detail": {},
        "_fallback": True,
        "_error": error_detail,
    }

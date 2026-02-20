"""
Release Timing Engine — Predicts optimal release windows.

Uses:
  - Hype momentum (from signal aggregator)
  - Seasonal audience demand (from calendar engine)
  - Festival peaks (from calendar engine)
  - Competition density (from competition engine)
  - Genre seasonality (from calendar engine)
  - Historical release performance (heuristic)

ReleaseScore(month) =
    0.35 * AudienceDemand +
    0.25 * LowCompetition +
    0.20 * HypeMomentum +
    0.10 * FestivalBoost +
    0.10 * GenreSeasonality

Returns:
  - Best release month and date
  - Top 3 alternate windows
  - Best season
  - Festival advantage
  - Risk level per month
"""

from typing import Dict, List, Optional
from phase6.services.calendar_engine import (
    get_festival_boost,
    get_seasonal_demand,
    get_genre_seasonality,
    get_monthly_engagement_index,
    MONTH_NAMES,
    SEASONS,
)

# ── Risk thresholds ──────────────────────────────────────────
RISK_LEVELS = {
    (0.7, 1.01): "low",
    (0.5, 0.7): "moderate",
    (0.3, 0.5): "high",
    (0.0, 0.3): "very_high",
}


def _risk_label(score: float) -> str:
    for (lo, hi), label in RISK_LEVELS.items():
        if lo <= score < hi:
            return label
    return "moderate"


def compute_release_scores(
    genre: str,
    language: str,
    target_regions: List[str],
    hype_momentum: float,
    competition_by_month: Optional[Dict[int, float]] = None,
) -> Dict:
    """
    Score every month of the year for release potential.

    Args:
        genre: Film genre
        language: Primary language
        target_regions: Target market regions
        hype_momentum: Current hype momentum (0–1) from signal aggregator
        competition_by_month: Optional {month: cdi_score} from competition engine

    Returns:
        {
            best_month, best_date, best_season, best_score,
            alternate_windows, festival_advantage,
            monthly_scores, risk_level
        }
    """
    if competition_by_month is None:
        competition_by_month = {}

    monthly_scores: List[Dict] = []

    for month in range(1, 13):
        # Component 1: Audience Demand (seasonal)
        audience_demand = get_seasonal_demand(month, target_regions)

        # Component 2: Low Competition (inverted CDI)
        cdi = competition_by_month.get(month, 0.5)
        low_competition = round(1.0 - cdi, 4)

        # Component 3: Hype Momentum (current, slightly decayed for future months)
        # Hype decays ~5% per month from now
        from datetime import datetime
        current_month = datetime.now().month
        months_ahead = (month - current_month) % 12
        hype_factor = round(max(0.1, hype_momentum * (0.95 ** months_ahead)), 4)

        # Component 4: Festival Boost
        festival_data = get_festival_boost(month, genre, target_regions)
        festival_boost = festival_data["boost_score"]

        # Component 5: Genre Seasonality
        genre_season = get_genre_seasonality(month, genre)

        # Release Score
        release_score = round(
            0.35 * audience_demand
            + 0.25 * low_competition
            + 0.20 * hype_factor
            + 0.10 * festival_boost
            + 0.10 * genre_season,
            4,
        )

        risk = _risk_label(release_score)

        monthly_scores.append({
            "month": month,
            "month_name": MONTH_NAMES[month],
            "season": SEASONS[month],
            "release_score": release_score,
            "audience_demand": audience_demand,
            "low_competition": low_competition,
            "hype_factor": hype_factor,
            "festival_boost": festival_boost,
            "genre_seasonality": genre_season,
            "festival_name": festival_data.get("best_festival"),
            "risk": risk,
        })

    # Sort by score
    monthly_scores.sort(key=lambda x: x["release_score"], reverse=True)

    best = monthly_scores[0]
    alternates = monthly_scores[1:4]

    # Best date: pick mid-month or festival date
    best_day = 15
    if best.get("festival_name"):
        # Align to festival window
        from phase6.services.calendar_engine import FESTIVALS
        for fest in FESTIVALS:
            if fest["name"] == best["festival_name"] and fest["month"] == best["month"]:
                best_day = max(1, fest["day"] - 2)  # Release just before festival
                break

    # Festival advantage summary
    festival_months = [s for s in monthly_scores if s["festival_boost"] > 0]
    festival_advantage = {
        "has_festival_window": len(festival_months) > 0,
        "best_festival": best.get("festival_name"),
        "festival_boost": best["festival_boost"],
        "festival_months": [
            {"month_name": s["month_name"], "festival": s["festival_name"], "boost": s["festival_boost"]}
            for s in festival_months[:5]
        ],
    }

    return {
        "best_month": best["month"],
        "best_month_name": best["month_name"],
        "best_date": f"{best['month_name']} {best_day}",
        "best_season": best["season"],
        "best_score": best["release_score"],
        "risk_level": best["risk"],
        "alternate_windows": [
            {
                "month": s["month"],
                "month_name": s["month_name"],
                "season": s["season"],
                "score": s["release_score"],
                "risk": s["risk"],
                "festival": s.get("festival_name"),
            }
            for s in alternates
        ],
        "festival_advantage": festival_advantage,
        "monthly_scores": sorted(monthly_scores, key=lambda x: x["month"]),
    }


def simulate_release_shift(
    current_month: int,
    new_month: int,
    genre: str,
    target_regions: List[str],
    hype_momentum: float,
    competition_by_month: Optional[Dict[int, float]] = None,
) -> Dict:
    """
    Simulate the impact of shifting release from one month to another.

    Returns: {original_score, new_score, delta, recommendation}
    """
    result = compute_release_scores(
        genre=genre,
        language="",
        target_regions=target_regions,
        hype_momentum=hype_momentum,
        competition_by_month=competition_by_month,
    )

    scores_by_month = {s["month"]: s for s in result["monthly_scores"]}
    original = scores_by_month.get(current_month, {"release_score": 0.5})
    new = scores_by_month.get(new_month, {"release_score": 0.5})

    delta = round(new["release_score"] - original["release_score"], 4)

    if delta > 0.1:
        rec = "Strongly recommended — significant improvement"
    elif delta > 0.03:
        rec = "Recommended — moderate improvement"
    elif delta > -0.03:
        rec = "Neutral — marginal difference"
    elif delta > -0.1:
        rec = "Not recommended — moderate decline"
    else:
        rec = "Strongly discouraged — significant decline"

    return {
        "original_month": MONTH_NAMES[current_month],
        "original_score": original["release_score"],
        "original_risk": original.get("risk", "moderate"),
        "new_month": MONTH_NAMES[new_month],
        "new_score": new["release_score"],
        "new_risk": new.get("risk", "moderate"),
        "delta": delta,
        "recommendation": rec,
    }

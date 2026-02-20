"""
Calendar Engine — Festival, seasonal, and monthly engagement data.

Provides:
  - Major Indian + global festival windows with boost scores
  - Seasonal audience demand indices
  - Monthly engagement levels
  - Festival proximity scoring
"""

from typing import Dict, List, Tuple
from datetime import date, timedelta

# ── Festival Calendar ────────────────────────────────────────
# Each festival: (name, month, day, duration_days, boost_score, regions)
FESTIVALS: List[Dict] = [
    # Indian festivals
    {"name": "Sankranti / Pongal", "month": 1, "day": 14, "duration": 5, "boost": 0.85, "regions": ["South Asia"], "genre_affinity": ["Drama", "Action", "Comedy"]},
    {"name": "Republic Day", "month": 1, "day": 26, "duration": 3, "boost": 0.60, "regions": ["South Asia"], "genre_affinity": ["Drama", "Action"]},
    {"name": "Holi", "month": 3, "day": 14, "duration": 3, "boost": 0.70, "regions": ["South Asia"], "genre_affinity": ["Comedy", "Romance"]},
    {"name": "Ugadi / Gudi Padwa", "month": 4, "day": 2, "duration": 3, "boost": 0.65, "regions": ["South Asia"], "genre_affinity": ["Drama", "Romance"]},
    {"name": "Eid al-Fitr", "month": 4, "day": 10, "duration": 4, "boost": 0.80, "regions": ["South Asia", "Middle East"], "genre_affinity": ["Action", "Drama", "Comedy"]},
    {"name": "Summer Holidays", "month": 5, "day": 1, "duration": 45, "boost": 0.90, "regions": ["South Asia", "North America", "Europe"], "genre_affinity": ["Action", "Comedy", "Animation", "Sci-Fi"]},
    {"name": "Independence Day (India)", "month": 8, "day": 15, "duration": 4, "boost": 0.75, "regions": ["South Asia"], "genre_affinity": ["Drama", "Action", "Thriller"]},
    {"name": "Ganesh Chaturthi", "month": 9, "day": 7, "duration": 10, "boost": 0.65, "regions": ["South Asia"], "genre_affinity": ["Drama", "Comedy"]},
    {"name": "Navratri / Dussehra", "month": 10, "day": 12, "duration": 10, "boost": 0.80, "regions": ["South Asia"], "genre_affinity": ["Action", "Drama", "Horror"]},
    {"name": "Diwali", "month": 11, "day": 1, "duration": 7, "boost": 0.95, "regions": ["South Asia", "Middle East"], "genre_affinity": ["Action", "Drama", "Comedy", "Romance"]},
    {"name": "Christmas", "month": 12, "day": 25, "duration": 10, "boost": 0.90, "regions": ["North America", "Europe", "Latin America", "Africa"], "genre_affinity": ["Comedy", "Animation", "Romance", "Drama"]},
    # Global
    {"name": "Valentine's Day", "month": 2, "day": 14, "duration": 3, "boost": 0.65, "regions": ["North America", "Europe", "South Asia"], "genre_affinity": ["Romance", "Comedy"]},
    {"name": "Memorial Day (US)", "month": 5, "day": 27, "duration": 4, "boost": 0.80, "regions": ["North America"], "genre_affinity": ["Action", "Thriller", "Sci-Fi"]},
    {"name": "4th of July (US)", "month": 7, "day": 4, "duration": 5, "boost": 0.85, "regions": ["North America"], "genre_affinity": ["Action", "Comedy"]},
    {"name": "Halloween", "month": 10, "day": 31, "duration": 5, "boost": 0.80, "regions": ["North America", "Europe"], "genre_affinity": ["Horror", "Thriller"]},
    {"name": "Thanksgiving (US)", "month": 11, "day": 28, "duration": 5, "boost": 0.85, "regions": ["North America"], "genre_affinity": ["Comedy", "Drama", "Animation"]},
    {"name": "Chinese New Year", "month": 1, "day": 29, "duration": 7, "boost": 0.90, "regions": ["East Asia"], "genre_affinity": ["Action", "Comedy", "Drama"]},
    {"name": "Golden Week (Japan)", "month": 5, "day": 3, "duration": 7, "boost": 0.75, "regions": ["East Asia"], "genre_affinity": ["Animation", "Drama", "Action"]},
    {"name": "Chuseok", "month": 9, "day": 17, "duration": 4, "boost": 0.70, "regions": ["East Asia"], "genre_affinity": ["Drama", "Comedy"]},
]

# ── Seasonal Demand Index (0–1) ──────────────────────────────
#                       Jan   Feb   Mar   Apr   May   Jun   Jul   Aug   Sep   Oct   Nov   Dec
SEASONAL_DEMAND = {
    "North America":   [0.55, 0.50, 0.45, 0.50, 0.70, 0.75, 0.85, 0.65, 0.50, 0.55, 0.75, 0.90],
    "Europe":          [0.50, 0.45, 0.45, 0.50, 0.60, 0.70, 0.80, 0.75, 0.50, 0.50, 0.55, 0.85],
    "South Asia":      [0.80, 0.55, 0.50, 0.55, 0.85, 0.70, 0.55, 0.65, 0.60, 0.75, 0.90, 0.70],
    "East Asia":       [0.85, 0.70, 0.50, 0.50, 0.70, 0.55, 0.65, 0.60, 0.65, 0.55, 0.50, 0.60],
    "Latin America":   [0.50, 0.55, 0.45, 0.50, 0.55, 0.65, 0.75, 0.60, 0.50, 0.50, 0.55, 0.80],
    "Middle East":     [0.55, 0.50, 0.55, 0.70, 0.60, 0.55, 0.60, 0.55, 0.55, 0.55, 0.65, 0.60],
    "Africa":          [0.45, 0.45, 0.45, 0.50, 0.55, 0.55, 0.60, 0.55, 0.50, 0.50, 0.50, 0.70],
}

# ── Genre Seasonality (which months favor which genres) ──────
GENRE_SEASONALITY = {
    "Action":      [0.5, 0.5, 0.5, 0.6, 0.8, 0.9, 0.9, 0.7, 0.5, 0.5, 0.6, 0.8],
    "Drama":       [0.7, 0.6, 0.6, 0.6, 0.5, 0.5, 0.4, 0.5, 0.7, 0.8, 0.9, 0.8],
    "Comedy":      [0.5, 0.6, 0.5, 0.6, 0.7, 0.8, 0.8, 0.7, 0.5, 0.5, 0.8, 0.9],
    "Horror":      [0.4, 0.4, 0.5, 0.5, 0.5, 0.6, 0.6, 0.6, 0.7, 0.9, 0.5, 0.4],
    "Thriller":    [0.6, 0.5, 0.5, 0.6, 0.6, 0.7, 0.7, 0.6, 0.7, 0.8, 0.6, 0.6],
    "Romance":     [0.5, 0.9, 0.5, 0.5, 0.5, 0.6, 0.5, 0.5, 0.5, 0.5, 0.6, 0.7],
    "Sci-Fi":      [0.5, 0.5, 0.5, 0.5, 0.8, 0.8, 0.9, 0.7, 0.5, 0.5, 0.5, 0.7],
    "Documentary": [0.6, 0.5, 0.5, 0.5, 0.5, 0.6, 0.5, 0.5, 0.7, 0.7, 0.7, 0.5],
    "Animation":   [0.5, 0.5, 0.6, 0.6, 0.8, 0.9, 0.9, 0.7, 0.5, 0.5, 0.8, 0.9],
}

SEASONS = {
    1: "Winter", 2: "Winter", 3: "Spring", 4: "Spring", 5: "Spring",
    6: "Summer", 7: "Summer", 8: "Summer", 9: "Fall", 10: "Fall",
    11: "Fall", 12: "Winter",
}

MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def get_festival_boost(month: int, genre: str, target_regions: List[str]) -> Dict:
    """
    Get festival boost for a given month, genre, and target regions.

    Returns: {boost_score, matching_festivals, best_festival}
    """
    matching = []
    for fest in FESTIVALS:
        if fest["month"] == month or (fest["month"] == month - 1 and fest["day"] + fest["duration"] > 28):
            region_match = any(r in target_regions for r in fest["regions"])
            genre_match = genre in fest.get("genre_affinity", [])
            if region_match:
                score = fest["boost"]
                if genre_match:
                    score = min(1.0, score * 1.15)
                matching.append({
                    "name": fest["name"],
                    "boost": round(score, 4),
                    "genre_match": genre_match,
                    "regions": fest["regions"],
                })

    if not matching:
        return {"boost_score": 0.0, "matching_festivals": [], "best_festival": None}

    matching.sort(key=lambda x: x["boost"], reverse=True)
    return {
        "boost_score": round(matching[0]["boost"], 4),
        "matching_festivals": matching,
        "best_festival": matching[0]["name"],
    }


def get_seasonal_demand(month: int, regions: List[str]) -> float:
    """Average seasonal demand across target regions for a month."""
    idx = month - 1
    demands = [SEASONAL_DEMAND.get(r, [0.5] * 12)[idx] for r in regions]
    return round(sum(demands) / max(1, len(demands)), 4) if demands else 0.5


def get_genre_seasonality(month: int, genre: str) -> float:
    """Genre-specific seasonal affinity for a month."""
    idx = month - 1
    return GENRE_SEASONALITY.get(genre, [0.5] * 12)[idx]


def get_monthly_engagement_index(regions: List[str]) -> List[Dict]:
    """
    Monthly engagement index across all 12 months for target regions.

    Returns: [{month, month_name, season, demand, index}]
    """
    result = []
    for m in range(1, 13):
        demand = get_seasonal_demand(m, regions)
        result.append({
            "month": m,
            "month_name": MONTH_NAMES[m],
            "season": SEASONS[m],
            "demand": demand,
        })
    return result


def get_festival_calendar(regions: List[str], genre: str = "") -> List[Dict]:
    """Get all festivals relevant to the given regions and genre."""
    result = []
    for fest in FESTIVALS:
        region_match = any(r in regions for r in fest["regions"])
        if region_match:
            entry = {
                "name": fest["name"],
                "month": fest["month"],
                "day": fest["day"],
                "duration_days": fest["duration"],
                "boost": fest["boost"],
                "genre_match": genre in fest.get("genre_affinity", []) if genre else False,
                "regions": fest["regions"],
            }
            result.append(entry)
    result.sort(key=lambda x: (x["month"], x["day"]))
    return result

"""
Festival & Award Impact Predictor.

Predicts festival acceptance probability, discoverability boost,
and optimal festival timing window.
"""

from typing import Dict


# Festival profiles (deterministic)
FESTIVALS = {
    "Cannes": {"prestige": 0.95, "months": [5], "genre_fit": ["Drama", "Thriller", "Documentary"], "region": "Europe", "audience_boost": 0.25},
    "Venice": {"prestige": 0.90, "months": [8, 9], "genre_fit": ["Drama", "Thriller"], "region": "Europe", "audience_boost": 0.22},
    "TIFF": {"prestige": 0.85, "months": [9], "genre_fit": ["Drama", "Comedy", "Thriller", "Documentary"], "region": "North America", "audience_boost": 0.20},
    "Sundance": {"prestige": 0.80, "months": [1], "genre_fit": ["Drama", "Documentary", "Horror"], "region": "North America", "audience_boost": 0.18},
    "Berlin": {"prestige": 0.85, "months": [2], "genre_fit": ["Drama", "Documentary"], "region": "Europe", "audience_boost": 0.19},
    "IFFI Goa": {"prestige": 0.55, "months": [11], "genre_fit": ["Drama", "Documentary"], "region": "South Asia", "audience_boost": 0.10},
    "Busan": {"prestige": 0.75, "months": [10], "genre_fit": ["Drama", "Action", "Thriller"], "region": "East Asia", "audience_boost": 0.15},
    "MAMI": {"prestige": 0.50, "months": [10], "genre_fit": ["Drama", "Documentary", "Comedy"], "region": "South Asia", "audience_boost": 0.08},
}


def predict_festival_impact(intel: Dict) -> Dict:
    """
    Predict festival acceptance probability and discoverability boost.

    Returns: {festival_probability, discoverability_boost, best_festival_window,
              festival_recommendations, award_potential}
    """
    genre = intel.get("genre", "Drama")
    sentiment = intel.get("avg_sentiment", 0.5)
    hype = intel.get("hype_momentum", 0.5)
    readiness = intel.get("readiness", 0.5)
    budget_level = intel.get("budget_level", "medium")
    release_mode = intel.get("release_mode", "ott")

    # Talent factor
    talent = intel.get("project", None)
    strategy = "star_led"
    if talent:
        strategy = getattr(talent, "talent_strategy", "star_led")

    director_factor = {"director_driven": 0.8, "ensemble": 0.5, "newcomer": 0.6, "star_led": 0.3}.get(strategy, 0.4)

    recommendations = []
    best_prob = 0.0
    best_festival = None
    best_window = None

    for name, profile in FESTIVALS.items():
        # Genre match
        genre_match = 1.0 if genre in profile["genre_fit"] else 0.3

        # Acceptance probability
        prob = round(min(1.0,
            0.30 * genre_match
            + 0.25 * sentiment
            + 0.20 * director_factor
            + 0.15 * readiness
            + 0.10 * (1 - hype)  # Counter-intuitive: less mainstream = more festival-worthy
        ), 4)

        boost = round(profile["audience_boost"] * prob, 4)

        if prob > best_prob:
            best_prob = prob
            best_festival = name
            best_window = f"{['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][profile['months'][0]-1]}"

        recommendations.append({
            "festival": name,
            "acceptance_probability": prob,
            "discoverability_boost": boost,
            "prestige": profile["prestige"],
            "window": ", ".join([['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][m-1] for m in profile["months"]]),
            "genre_match": genre in profile["genre_fit"],
        })

    recommendations.sort(key=lambda x: x["acceptance_probability"], reverse=True)

    # Award potential
    award_potential = round(min(1.0,
        0.30 * sentiment
        + 0.25 * director_factor
        + 0.20 * readiness
        + 0.15 * (1 - hype)
        + 0.10 * (0.7 if budget_level != "high" else 0.3)
    ), 4)

    return {
        "festival_probability": best_prob,
        "discoverability_boost": round(recommendations[0]["discoverability_boost"], 4) if recommendations else 0.0,
        "best_festival_window": best_window,
        "best_festival": best_festival,
        "award_potential": award_potential,
        "festival_recommendations": recommendations[:5],
    }

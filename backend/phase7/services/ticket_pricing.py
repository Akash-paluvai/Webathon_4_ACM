"""
Ticket Pricing Intelligence Engine.

Computes optimal ticket price by region, demand elasticity,
revenue vs reach tradeoff, festival pricing vs regular.
"""

from typing import Dict, List


# Regional income proxy (relative purchasing power index, 1.0 = baseline)
REGIONAL_INCOME = {
    "North America": 1.6, "Europe": 1.4, "East Asia": 1.3,
    "Latin America": 0.7, "Middle East": 1.1, "South Asia": 0.5,
    "Africa": 0.4,
}

# Base ticket prices (INR) by region
BASE_PRICES = {
    "North America": 800, "Europe": 700, "East Asia": 650,
    "Latin America": 350, "Middle East": 550, "South Asia": 180,
    "Africa": 200,
}


def compute_ticket_pricing(intel: Dict) -> Dict:
    """
    Compute optimal ticket pricing strategy.

    Returns: {recommended_price, elasticity, revenue_gain, reach_loss,
              strategy, regional_prices, festival_pricing}
    """
    genre = intel.get("genre", "Drama")
    hype = intel.get("hype_momentum", 0.5)
    cdi = intel.get("cdi", 0.5)
    regional = intel.get("regional_strength", 0.5)
    sentiment = intel.get("avg_sentiment", 0.5)
    release_mode = intel.get("release_mode", "ott")

    # Only relevant for theatrical / hybrid
    if release_mode == "ott":
        return {
            "recommended_price": None,
            "elasticity": 0.0,
            "revenue_gain": 0.0,
            "reach_loss": 0.0,
            "strategy": "OTT release — ticket pricing not applicable. Revenue comes from licensing deals.",
            "regional_prices": [],
            "festival_pricing": None,
        }

    # Demand elasticity (negative = demand drops when price rises)
    elasticity = round(-0.8 - 0.4 * (1 - hype) - 0.3 * cdi + 0.2 * sentiment, 2)

    # Genre premium
    genre_premium = {"Action": 1.15, "Sci-Fi": 1.2, "Animation": 1.1,
                     "Horror": 0.95, "Documentary": 0.85, "Drama": 1.0,
                     "Comedy": 1.05, "Romance": 1.0, "Thriller": 1.05}.get(genre, 1.0)

    # Hype premium (high hype = can charge more)
    hype_premium = 1.0 + 0.15 * hype

    # Competition discount (high competition = lower price wins)
    comp_discount = 1.0 - 0.1 * cdi

    # Regional pricing
    regional_prices: List[Dict] = []
    regions = intel.get("normalized_regions", [])
    primary_region = regions[0]["region"] if regions else "South Asia"

    for region_name, base in BASE_PRICES.items():
        optimal = round(base * genre_premium * hype_premium * comp_discount)
        # Round to nearest 10
        optimal = round(optimal / 10) * 10

        income_factor = REGIONAL_INCOME.get(region_name, 0.5)
        affordability = round(min(1.0, income_factor * 0.6), 2)

        regional_prices.append({
            "region": region_name,
            "base_price": base,
            "optimal_price": optimal,
            "affordability_index": affordability,
            "is_primary": region_name == primary_region,
        })

    # Primary region recommended price
    primary_price_entry = next((p for p in regional_prices if p["is_primary"]), regional_prices[0])
    recommended_price = primary_price_entry["optimal_price"]

    # Revenue gain vs reach loss at recommended price
    price_ratio = recommended_price / max(1, primary_price_entry["base_price"])
    revenue_gain = round(max(-0.3, (price_ratio - 1.0) * 0.5), 4)
    reach_loss = round(max(0, (price_ratio - 1.0) * abs(elasticity) * 0.3), 4)

    # Strategy
    if hype > 0.65 and cdi < 0.4:
        strategy = "Premium pricing — high demand, low competition allows higher margins"
    elif hype < 0.35:
        strategy = "Discount pricing — lower price to maximize reach and build word-of-mouth"
    elif cdi > 0.6:
        strategy = "Competitive pricing — match or undercut competitor pricing to win attention"
    else:
        strategy = "Standard pricing — balanced approach for moderate demand and competition"

    # Festival pricing
    festival_pricing = {
        "festival_premium": round(recommended_price * 1.2 / 10) * 10,
        "regular_price": recommended_price,
        "premium_justification": "Festival windows allow 15-20% premium due to higher audience willingness to pay",
    }

    return {
        "recommended_price": recommended_price,
        "elasticity": elasticity,
        "revenue_gain": revenue_gain,
        "reach_loss": reach_loss,
        "strategy": strategy,
        "regional_prices": regional_prices,
        "festival_pricing": festival_pricing,
    }

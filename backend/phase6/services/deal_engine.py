"""
Deal Engine — generates deal terms and computes negotiation leverage.
"""

from typing import Dict, List
from phase6.utils.scoring_utils import weighted_score


def compute_negotiation_leverage(
    scale: str,
    talent_strategy: str,
    audience_type: str,
    budget_level: str,
    distribution_confidence: str,
    platform_fit_score: float,
) -> Dict:
    """
    Compute overall negotiation leverage based on project attributes
    and the best platform fit score.

    Returns dict with leverage label and numeric score.
    """
    scores = {
        "scale": {"indie": 0.2, "studio": 0.6, "blockbuster": 1.0}.get(scale, 0.4),
        "talent": {"unknown": 0.1, "emerging": 0.3, "established": 0.7, "starDriven": 1.0}.get(talent_strategy, 0.3),
        "audience": {"niche": 0.3, "broad": 0.6, "mainstream": 0.9}.get(audience_type, 0.5),
        "budget": {"low": 0.3, "medium": 0.6, "high": 0.9}.get(budget_level, 0.5),
        "confidence": {"low": 0.2, "medium": 0.5, "high": 0.9}.get(distribution_confidence, 0.5),
        "platform_fit": platform_fit_score,
    }

    weights = {
        "scale": 0.15,
        "talent": 0.25,
        "audience": 0.15,
        "budget": 0.10,
        "confidence": 0.15,
        "platform_fit": 0.20,
    }

    leverage_score = weighted_score(scores, weights)

    if leverage_score >= 0.7:
        leverage = "strong"
    elif leverage_score >= 0.4:
        leverage = "moderate"
    else:
        leverage = "weak"

    return {
        "leverage": leverage,
        "leverage_score": round(leverage_score, 4),
    }


def generate_deal_terms(
    platforms: List[Dict],
    leverage_score: float,
    budget_level: str,
    release_model: str,
) -> List[Dict]:
    """
    Generate deal term options for the top platforms.

    Args:
        platforms: Ranked platform fit results (from platform_fit service).
        leverage_score: Overall negotiation leverage (0-1).
        budget_level: Project budget level.
        release_model: theatre / ott / hybrid.

    Returns a list of deal term dicts.
    """
    budget_base = {"low": 50, "medium": 200, "high": 800}.get(budget_level, 200)

    deal_options = []
    top_platforms = platforms[:3]  # top 3 platforms

    for platform_info in top_platforms:
        platform_name = platform_info["platform"]
        fit_score = platform_info["fit_score"]

        # MG range scales with leverage and fit
        mg_multiplier = (leverage_score + fit_score) / 2
        mg_low = round(budget_base * mg_multiplier * 0.6, 1)
        mg_high = round(budget_base * mg_multiplier * 1.4, 1)

        # Revenue share: stronger leverage → better share
        base_share = 20  # platform takes 20% baseline
        share_adjustment = leverage_score * 15  # up to 15% less for strong leverage
        rev_share = round(base_share - share_adjustment, 1)

        # Exclusivity window
        if release_model == "ott":
            exclusivity = 12
        elif release_model == "theatre":
            exclusivity = 3
        else:
            exclusivity = 6

        # Adjust exclusivity by leverage
        if leverage_score > 0.7:
            exclusivity = max(1, exclusivity - 3)
        elif leverage_score < 0.3:
            exclusivity += 3

        # Strategy recommendation
        if leverage_score > 0.7 and fit_score > 0.7:
            strategy = "Push for upfront MG with revenue share kicker"
        elif leverage_score > 0.5:
            strategy = "Balanced MG + revenue share deal"
        elif fit_score > 0.6:
            strategy = "Revenue share focused — platform has strong fit"
        else:
            strategy = "Volume licensing or multi-platform split"

        deal_options.append({
            "platform": platform_name,
            "minimum_guarantee_range": (mg_low, mg_high),
            "revenue_share_pct": max(5, rev_share),
            "exclusivity_window_months": exclusivity,
            "recommended_strategy": strategy,
        })

    return deal_options

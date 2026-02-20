"""
Leverage Engine — computes Negotiation Leverage Score from composite factors.

Formula:
    Leverage = 0.40 * PlatformFit
             + 0.25 * HypeMomentum
             + 0.20 * RegionalDominance
             + 0.15 * DubbingExpansionPotential

This replaces the simpler leverage calculation in deal_engine.py for the
full-analysis pipeline.  deal_engine.py's compute_negotiation_leverage()
still works for the standalone /deal endpoint.
"""

from typing import Dict, List, Optional


# ── Strategy Hints ───────────────────────────────────────────
STRATEGY_HINTS = {
    "very_high": "Push for higher revenue share instead of higher advance — your hype gives you runway",
    "high": "Push for higher revenue share instead of higher advance",
    "moderate_high": "Negotiate balanced deal — request performance bonuses tied to opening weekend metrics",
    "moderate": "Accept standard MG but negotiate for shorter exclusivity windows",
    "moderate_low": "Consider multi-platform split to reduce single-platform dependency",
    "low": "Focus on volume licensing — the leverage gap means aggressive terms won't stick",
    "very_low": "Accept platform terms but negotiate marketing spend commitment from distributor",
}


def _classify_level(score: float) -> str:
    """Map score to leverage level label."""
    if score >= 0.75:
        return "VERY_HIGH"
    elif score >= 0.60:
        return "HIGH"
    elif score >= 0.45:
        return "MODERATE"
    elif score >= 0.30:
        return "LOW"
    else:
        return "VERY_LOW"


def _pick_strategy_hint(score: float) -> str:
    """Select the most appropriate strategy hint for the leverage score."""
    if score >= 0.75:
        return STRATEGY_HINTS["very_high"]
    elif score >= 0.65:
        return STRATEGY_HINTS["high"]
    elif score >= 0.55:
        return STRATEGY_HINTS["moderate_high"]
    elif score >= 0.45:
        return STRATEGY_HINTS["moderate"]
    elif score >= 0.35:
        return STRATEGY_HINTS["moderate_low"]
    elif score >= 0.25:
        return STRATEGY_HINTS["low"]
    else:
        return STRATEGY_HINTS["very_low"]


def compute_leverage(
    platform_fit_score: float,
    hype_momentum: float,
    regional_dominance: float,
    dubbing_expansion_potential: float,
) -> Dict:
    """
    Compute Negotiation Leverage Score.

    Args:
        platform_fit_score: Best platform's fit score (0-1).
        hype_momentum: Aggregate hype from top-3 region signals (0-1).
        regional_dominance: Normalized score of the top region (0-1).
        dubbing_expansion_potential: Proportion of high/medium dubbing recommendations (0-1).

    Returns:
        {leverage_score, level, strategy_hint, breakdown}
    """
    # Weighted formula
    leverage = (
        0.40 * platform_fit_score
        + 0.25 * hype_momentum
        + 0.20 * regional_dominance
        + 0.15 * dubbing_expansion_potential
    )
    leverage = round(min(1.0, max(0.0, leverage)), 4)

    level = _classify_level(leverage)
    strategy = _pick_strategy_hint(leverage)

    return {
        "leverage_score": leverage,
        "level": level,
        "strategy_hint": strategy,
        "breakdown": {
            "platform_fit_contribution": round(0.40 * platform_fit_score, 4),
            "hype_momentum_contribution": round(0.25 * hype_momentum, 4),
            "regional_dominance_contribution": round(0.20 * regional_dominance, 4),
            "dubbing_expansion_contribution": round(0.15 * dubbing_expansion_potential, 4),
        },
    }


def compute_dubbing_expansion_potential(dubbing_result: Dict) -> float:
    """
    Derive dubbing expansion potential from dubbing engine output.
    Returns 0-1 based on how many high/medium priority dubs exist.
    """
    recs = dubbing_result.get("recommendations", [])
    if not recs:
        return 0.0

    high_count = sum(1 for r in recs if r["priority"] == "high")
    med_count = sum(1 for r in recs if r["priority"] == "medium")
    total = len(recs)

    # Weighted: high counts more
    potential = (high_count * 1.0 + med_count * 0.5) / max(1, total)
    return round(min(1.0, potential), 4)

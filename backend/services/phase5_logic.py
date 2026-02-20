"""
Phase-5 Marketing Strategy Logic
Simulated campaign allocation optimizer + discoverability scoring.
Deterministic, heuristic-based — no ML, no external APIs, no historical data.

Channels: ADS, INFLUENCER, FESTIVAL, ORGANIC
Outputs: budgetAllocation, discoverabilityScore, primaryMarketingChannel,
         marketingRisk, riskFlags, explanation
"""

from typing import Any, Dict, List, Tuple


# ── Channel bounds (min%, max%) ────────────────────────────
# Every channel must stay within these bounds.
_CHANNEL_BOUNDS: Dict[str, Tuple[int, int]] = {
    "ADS":        (5, 60),
    "INFLUENCER": (5, 50),
    "FESTIVAL":   (0, 40),
    "ORGANIC":    (5, 30),
}

# ── Audience ↔ channel affinity (0-1 scale) ────────────────
# How well each channel drives discoverability for each audience.
_AFFINITY: Dict[str, Dict[str, float]] = {
    "niche": {
        "ADS": 0.3, "INFLUENCER": 0.5, "FESTIVAL": 0.8, "ORGANIC": 0.6,
    },
    "regional": {
        "ADS": 0.6, "INFLUENCER": 0.7, "FESTIVAL": 0.4, "ORGANIC": 0.5,
    },
    "mass": {
        "ADS": 0.9, "INFLUENCER": 0.6, "FESTIVAL": 0.2, "ORGANIC": 0.3,
    },
}

# ── Budget multiplier (how much budget amplifies channel effect) ──
_BUDGET_MULTIPLIER: Dict[str, float] = {
    "low":    0.6,
    "medium": 1.0,
    "high":   1.4,
}

_CHANNELS = ["ADS", "INFLUENCER", "FESTIVAL", "ORGANIC"]


def compute_phase5(
    audience_type: str,
    audience_interest_score: int,
    scale: str,
    budget_level: str,
    marketing_budget_level: str,
) -> Dict[str, Any]:
    """
    Deterministic Phase-5 marketing strategy computation.

    Returns dict with:
      - budgetAllocation: {channel: pct}
      - discoverabilityScore: int (0-100)
      - primaryMarketingChannel: str
      - marketingRisk: str (LOW|MEDIUM|HIGH)
      - riskFlags: list[str]
      - explanation: str
    """
    aud = audience_type.strip().lower()
    mkt_budget = marketing_budget_level.strip().lower()
    scale_lower = scale.strip().lower()

    # ── 1. Compute raw channel weights ─────────────────────
    affinities = _AFFINITY.get(aud, _AFFINITY["regional"])
    budget_mult = _BUDGET_MULTIPLIER.get(mkt_budget, 1.0)

    # Weighted score = affinity × budget multiplier
    # Apply diminishing returns: w^0.7 (concave curve, no randomness)
    raw_weights: Dict[str, float] = {}
    for ch in _CHANNELS:
        w = affinities[ch] * budget_mult
        raw_weights[ch] = w ** 0.7   # diminishing returns

    # ── 2. Allocate budget proportionally, respecting bounds ─
    allocation = _allocate(raw_weights)

    # ── 3. Primary channel = highest allocation ────────────
    primary_channel = max(allocation, key=lambda c: allocation[c])

    # ── 4. Discoverability score ───────────────────────────
    disc_score = _discoverability(allocation, affinities, budget_mult,
                                  audience_interest_score)

    # ── 5. Risk assessment ─────────────────────────────────
    risk, risk_flags = _assess_risk(
        aud, mkt_budget, scale_lower, allocation,
        audience_interest_score, disc_score,
    )

    # ── 6. Explanation ─────────────────────────────────────
    explanation = _build_explanation(
        aud, mkt_budget, primary_channel, allocation,
        disc_score, risk, audience_interest_score,
    )

    return {
        "budgetAllocation": allocation,
        "discoverabilityScore": disc_score,
        "primaryMarketingChannel": primary_channel,
        "marketingRisk": risk,
        "riskFlags": risk_flags,
        "explanation": explanation,
    }


# ── Budget allocation with bounds ──────────────────────────

def _allocate(raw_weights: Dict[str, float]) -> Dict[str, int]:
    """
    Convert raw weights to integer percentages summing to 100,
    respecting per-channel min/max bounds.
    """
    total_w = sum(raw_weights.values()) or 1.0

    # Initial proportional split
    alloc: Dict[str, float] = {}
    for ch in _CHANNELS:
        pct = (raw_weights[ch] / total_w) * 100
        lo, hi = _CHANNEL_BOUNDS[ch]
        alloc[ch] = max(lo, min(hi, pct))

    # Normalize to sum=100
    total = sum(alloc.values()) or 1.0
    for ch in _CHANNELS:
        alloc[ch] = alloc[ch] / total * 100

    # Round to integers that still sum to 100
    floored = {ch: int(alloc[ch]) for ch in _CHANNELS}
    remainder = 100 - sum(floored.values())

    # Distribute remainder by largest fractional part
    fracs = sorted(_CHANNELS, key=lambda c: alloc[c] - floored[c], reverse=True)
    for i in range(remainder):
        floored[fracs[i]] += 1

    return floored


# ── Discoverability score ──────────────────────────────────

def _discoverability(
    allocation: Dict[str, int],
    affinities: Dict[str, float],
    budget_mult: float,
    interest_score: int,
) -> int:
    """
    Score = weighted sum of (allocation% × affinity × budget_multiplier)
    + interest bonus, minus over-concentration penalty.
    Clamped 0-100.
    """
    # Base: weighted channel contribution (max ~70 pts)
    base = 0.0
    for ch in _CHANNELS:
        pct = allocation[ch] / 100.0
        base += pct * affinities[ch] * budget_mult * 70.0

    # Interest bonus: up to 20 pts (interest_score / 100 * 20)
    interest_bonus = (interest_score / 100.0) * 20.0

    # Over-concentration penalty: if any channel > 50%, penalise
    max_alloc = max(allocation.values())
    concentration_penalty = 0.0
    if max_alloc > 50:
        concentration_penalty = (max_alloc - 50) * 0.5  # -0.5 pts per % over 50

    score = base + interest_bonus - concentration_penalty
    return max(0, min(100, round(score)))


# ── Risk assessment ────────────────────────────────────────

def _assess_risk(
    aud: str,
    mkt_budget: str,
    scale: str,
    allocation: Dict[str, int],
    interest_score: int,
    disc_score: int,
) -> Tuple[str, List[str]]:
    """Determine marketing risk level and collect risk flags."""
    flags: List[str] = []
    risk_points = 0

    # MASS audience + LOW budget = high risk
    if aud == "mass" and mkt_budget == "low":
        flags.append("MASS audience with LOW marketing budget limits reach")
        risk_points += 3

    # Large scale + LOW budget
    if scale == "large" and mkt_budget == "low":
        flags.append("LARGE-scale project with LOW budget creates visibility gap")
        risk_points += 2

    # Over-concentration (any channel > 55%)
    max_ch = max(allocation, key=lambda c: allocation[c])
    if allocation[max_ch] > 55:
        flags.append(f"Over-concentration in {max_ch} ({allocation[max_ch]}%) reduces resilience")
        risk_points += 2

    # Low interest score
    if interest_score < 50:
        flags.append(f"Low audience interest score ({interest_score}/100) may limit campaign effectiveness")
        risk_points += 2

    # Low discoverability
    if disc_score < 40:
        flags.append(f"Simulated discoverability is low ({disc_score}/100)")
        risk_points += 1

    # Budget-audience mismatch
    if aud == "niche" and mkt_budget == "high":
        flags.append("HIGH budget for NICHE audience risks inefficient spend")
        risk_points += 1

    if risk_points >= 4:
        return "HIGH", flags
    elif risk_points >= 2:
        return "MEDIUM", flags
    else:
        return "LOW", flags


# ── Explanation builder ────────────────────────────────────

def _build_explanation(
    aud: str,
    mkt_budget: str,
    primary_channel: str,
    allocation: Dict[str, int],
    disc_score: int,
    risk: str,
    interest_score: int,
) -> str:
    aud_label = aud.upper()
    budget_label = mkt_budget.upper()

    # Build the channel breakdown string
    parts = [f"{ch} {pct}%" for ch, pct in sorted(allocation.items(), key=lambda x: -x[1])]
    breakdown = ", ".join(parts)

    return (
        f"For a {aud_label} audience with {budget_label} marketing budget, "
        f"the optimizer recommends {primary_channel} as the primary channel "
        f"({breakdown}). "
        f"The simulated discoverability score is {disc_score}/100, "
        f"reflecting the marginal efficiency of each channel under "
        f"budget-constrained optimization. "
        f"With an audience interest score of {interest_score}/100, "
        f"marketing risk is assessed as {risk}."
    )

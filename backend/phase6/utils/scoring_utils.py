"""
Reusable scoring utilities for Phase 6 computations.
"""

import math
from typing import Dict, List, Tuple


def normalize(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """
    Normalize a value to the [min_val, max_val] range.
    Clamps the result to avoid out-of-range values.
    """
    if max_val == min_val:
        return min_val
    clamped = max(min_val, min(value, max_val))
    return (clamped - min_val) / (max_val - min_val)


def weighted_score(scores: Dict[str, float], weights: Dict[str, float]) -> float:
    """
    Compute a weighted average score.

    Args:
        scores: Mapping of factor name → score (0.0 to 1.0).
        weights: Mapping of factor name → weight.

    Returns:
        Weighted score in [0.0, 1.0].
    """
    total_weight = sum(weights.get(k, 0.0) for k in scores)
    if total_weight == 0:
        return 0.0

    result = sum(scores[k] * weights.get(k, 0.0) for k in scores)
    return result / total_weight


def confidence_interval(
    score: float,
    sample_size: int = 100,
    z: float = 1.96,
) -> Tuple[float, float]:
    """
    Compute an approximate confidence interval for a proportion / score.

    Uses the normal approximation:
        CI = score ± z * sqrt(score * (1 - score) / n)

    Args:
        score: Point estimate in [0, 1].
        sample_size: Effective sample size (higher → tighter interval).
        z: Z-score for desired confidence level (1.96 = 95%).

    Returns:
        (lower_bound, upper_bound) clamped to [0, 1].
    """
    if sample_size <= 0:
        return (0.0, 1.0)

    se = math.sqrt(score * (1.0 - score) / sample_size)
    margin = z * se
    lower = max(0.0, score - margin)
    upper = min(1.0, score + margin)
    return (round(lower, 4), round(upper, 4))


def bucket_label(score: float) -> str:
    """Return a human-readable bucket label for a 0-1 score."""
    if score >= 0.8:
        return "very_high"
    elif score >= 0.6:
        return "high"
    elif score >= 0.4:
        return "medium"
    elif score >= 0.2:
        return "low"
    else:
        return "very_low"


def rank_items(items: List[Dict], key: str, descending: bool = True) -> List[Dict]:
    """
    Rank a list of dicts by a numeric key, adding a 'rank' field.
    """
    sorted_items = sorted(items, key=lambda x: x.get(key, 0), reverse=descending)
    for idx, item in enumerate(sorted_items, start=1):
        item["rank"] = idx
    return sorted_items

"""
Platform Fit Service — evaluates how well a film project fits each distribution platform.

Supports two modes:
  1. Legacy: calculate_platform_fit() — static feature scoring
  2. Signal-enhanced: calculate_platform_fit_v2() — adds signal data + platform metadata
"""

from typing import Dict, List, Optional
from phase6.utils.scoring_utils import normalize, weighted_score, confidence_interval, rank_items


# ── Platform Profiles ─────────────────────────────────────────
PLATFORM_PROFILES: Dict[str, Dict[str, float]] = {
    "Netflix": {
        "genre_breadth": 0.8, "ott_affinity": 1.0, "star_power": 0.6,
        "indie_affinity": 0.5, "mainstream_affinity": 0.9, "niche_affinity": 0.6,
        "global_reach": 0.95,
    },
    "Amazon Prime": {
        "genre_breadth": 0.7, "ott_affinity": 0.9, "star_power": 0.5,
        "indie_affinity": 0.6, "mainstream_affinity": 0.8, "niche_affinity": 0.7,
        "global_reach": 0.85,
    },
    "Theatrical": {
        "genre_breadth": 0.5, "ott_affinity": 0.1, "star_power": 0.9,
        "indie_affinity": 0.2, "mainstream_affinity": 0.95, "niche_affinity": 0.2,
        "global_reach": 0.7,
    },
    "Hotstar": {
        "genre_breadth": 0.6, "ott_affinity": 0.85, "star_power": 0.7,
        "indie_affinity": 0.4, "mainstream_affinity": 0.8, "niche_affinity": 0.5,
        "global_reach": 0.4,
    },
    "Festival Circuit": {
        "genre_breadth": 0.3, "ott_affinity": 0.2, "star_power": 0.2,
        "indie_affinity": 0.95, "mainstream_affinity": 0.1, "niche_affinity": 0.9,
        "global_reach": 0.3,
    },
    "YouTube Premium": {
        "genre_breadth": 0.5, "ott_affinity": 0.7, "star_power": 0.3,
        "indie_affinity": 0.7, "mainstream_affinity": 0.5, "niche_affinity": 0.8,
        "global_reach": 0.9,
    },
}

# ── Platform Metadata (Layer 2) ──────────────────────────────
PLATFORM_METADATA: Dict[str, Dict] = {
    "Netflix": {
        "demographic_match": {"18-34": 0.9, "25-44": 0.85, "35-54": 0.6, "family": 0.7},
        "genre_success_index": {
            "Action": 0.85, "Thriller": 0.90, "Drama": 0.80, "Horror": 0.75,
            "Comedy": 0.70, "Romance": 0.65, "Sci-Fi": 0.80, "Documentary": 0.60,
        },
        "region_penetration": {
            "North America": 0.95, "Europe": 0.85, "South Asia": 0.40,
            "East Asia": 0.50, "Latin America": 0.75, "Middle East": 0.35, "Africa": 0.20,
        },
        "label": "global OTT leader",
    },
    "Amazon Prime": {
        "demographic_match": {"18-34": 0.7, "25-44": 0.85, "35-54": 0.8, "family": 0.75},
        "genre_success_index": {
            "Action": 0.70, "Thriller": 0.75, "Drama": 0.80, "Horror": 0.55,
            "Comedy": 0.75, "Romance": 0.60, "Sci-Fi": 0.70, "Documentary": 0.65,
        },
        "region_penetration": {
            "North America": 0.80, "Europe": 0.70, "South Asia": 0.55,
            "East Asia": 0.35, "Latin America": 0.45, "Middle East": 0.30, "Africa": 0.15,
        },
        "label": "premium OTT with strong retail integration",
    },
    "Theatrical": {
        "demographic_match": {"18-34": 0.6, "25-44": 0.7, "35-54": 0.8, "family": 0.9},
        "genre_success_index": {
            "Action": 0.95, "Thriller": 0.70, "Drama": 0.55, "Horror": 0.65,
            "Comedy": 0.60, "Romance": 0.45, "Sci-Fi": 0.85, "Documentary": 0.25,
        },
        "region_penetration": {
            "North America": 0.85, "Europe": 0.75, "South Asia": 0.70,
            "East Asia": 0.80, "Latin America": 0.50, "Middle East": 0.45, "Africa": 0.25,
        },
        "label": "theatrical distribution",
    },
    "Hotstar": {
        "demographic_match": {"18-34": 0.85, "25-44": 0.80, "35-54": 0.5, "family": 0.7},
        "genre_success_index": {
            "Action": 0.80, "Thriller": 0.75, "Drama": 0.85, "Horror": 0.50,
            "Comedy": 0.70, "Romance": 0.80, "Sci-Fi": 0.45, "Documentary": 0.40,
        },
        "region_penetration": {
            "North America": 0.10, "Europe": 0.08, "South Asia": 0.90,
            "East Asia": 0.05, "Latin America": 0.02, "Middle East": 0.15, "Africa": 0.05,
        },
        "label": "South Asia dominant OTT",
    },
    "Festival Circuit": {
        "demographic_match": {"18-34": 0.5, "25-44": 0.7, "35-54": 0.8, "family": 0.2},
        "genre_success_index": {
            "Action": 0.10, "Thriller": 0.30, "Drama": 0.95, "Horror": 0.40,
            "Comedy": 0.35, "Romance": 0.50, "Sci-Fi": 0.25, "Documentary": 0.90,
        },
        "region_penetration": {
            "North America": 0.30, "Europe": 0.50, "South Asia": 0.10,
            "East Asia": 0.25, "Latin America": 0.15, "Middle East": 0.10, "Africa": 0.10,
        },
        "label": "festival + limited release",
    },
    "YouTube Premium": {
        "demographic_match": {"18-34": 0.95, "25-44": 0.6, "35-54": 0.3, "family": 0.5},
        "genre_success_index": {
            "Action": 0.55, "Thriller": 0.45, "Drama": 0.50, "Horror": 0.60,
            "Comedy": 0.85, "Romance": 0.40, "Sci-Fi": 0.50, "Documentary": 0.70,
        },
        "region_penetration": {
            "North America": 0.85, "Europe": 0.70, "South Asia": 0.60,
            "East Asia": 0.55, "Latin America": 0.50, "Middle East": 0.40, "Africa": 0.35,
        },
        "label": "digital-first with young skew",
    },
}

# ── Feature Weights ──────────────────────────────────────────
FIT_WEIGHTS = {
    "genre_match": 0.20,
    "scale_match": 0.15,
    "audience_match": 0.20,
    "release_model_match": 0.25,
    "talent_match": 0.10,
    "budget_match": 0.10,
}

FIT_WEIGHTS_V2 = {
    "genre_match": 0.15,
    "scale_match": 0.10,
    "audience_match": 0.15,
    "release_model_match": 0.15,
    "talent_match": 0.08,
    "budget_match": 0.07,
    "signal_momentum": 0.15,
    "region_penetration": 0.10,
    "genre_success": 0.05,
}


# ── Scoring Functions ────────────────────────────────────────

def _score_genre_match(platform_profile: Dict, genre: str) -> float:
    genre_lower = genre.lower()
    art_genres = {"drama", "art-house", "documentary", "indie", "experimental"}
    if genre_lower in art_genres:
        return platform_profile.get("indie_affinity", 0.5)
    return platform_profile.get("genre_breadth", 0.5)


def _score_scale_match(platform_profile: Dict, scale: str) -> float:
    scale_map = {
        "indie": "indie_affinity",
        "studio": "mainstream_affinity",
        "blockbuster": "mainstream_affinity",
    }
    key = scale_map.get(scale, "mainstream_affinity")
    return platform_profile.get(key, 0.5)


def _score_audience_match(platform_profile: Dict, audience_type: str) -> float:
    audience_map = {
        "niche": "niche_affinity",
        "broad": "mainstream_affinity",
        "mainstream": "mainstream_affinity",
    }
    key = audience_map.get(audience_type, "mainstream_affinity")
    return platform_profile.get(key, 0.5)


def _score_release_model_match(platform_profile: Dict, release_model: str) -> float:
    if release_model == "ott":
        return platform_profile.get("ott_affinity", 0.5)
    elif release_model == "theatre":
        return 1.0 - platform_profile.get("ott_affinity", 0.5)
    else:  # hybrid
        return 0.6 + 0.2 * platform_profile.get("ott_affinity", 0.5)


def _score_talent_match(platform_profile: Dict, talent_strategy: str) -> float:
    talent_map = {"unknown": 0.3, "emerging": 0.5, "established": 0.7, "starDriven": 1.0}
    talent_val = talent_map.get(talent_strategy, 0.5)
    platform_star = platform_profile.get("star_power", 0.5)
    return 1.0 - abs(talent_val - platform_star)


def _score_budget_match(platform_profile: Dict, budget_level: str) -> float:
    budget_multiplier = {"low": 0.3, "medium": 0.6, "high": 1.0}.get(budget_level, 0.5)
    reach = platform_profile.get("global_reach", 0.5)
    return 1.0 - abs(budget_multiplier - reach) * 0.5


# ── Detailed Reasoning Generator (Layer 2) ───────────────────

def _build_detailed_reasoning(
    platform_name: str,
    scores: Dict[str, float],
    metadata: Dict,
    genre: str,
    audience_type: str,
    top_regions: Optional[List[str]] = None,
    engagement_velocity: float = 0.0,
) -> List[str]:
    """Build actionable negotiation-intelligence reasoning strings."""
    reasons = []
    meta = metadata.get(platform_name, {})
    label = meta.get("label", platform_name)

    # Audience overlap
    audience_score = scores.get("audience_match", 0)
    if audience_score > 0.6:
        pct = int(audience_score * 100)
        viewer_type = "OTT digital" if scores.get("release_model_match", 0) > 0.5 else "theatrical"
        reasons.append(f"{pct}% audience overlap with {viewer_type} viewers on {label}")

    # Genre success on platform
    genre_success = meta.get("genre_success_index", {}).get(genre, 0)
    if genre_success > 0.7:
        reasons.append(f"High {genre.lower()} engagement — {genre_success:.0%} genre success index on {platform_name}")
    elif genre_success > 0.5:
        reasons.append(f"Moderate {genre.lower()} traction on {platform_name} ({genre_success:.0%} success index)")

    # Region penetration alignment
    if top_regions:
        penetration = meta.get("region_penetration", {})
        strong_regions = [r for r in top_regions if penetration.get(r, 0) > 0.5]
        if strong_regions:
            regions_str = ", ".join(strong_regions[:2])
            avg_pen = sum(penetration[r] for r in strong_regions) / len(strong_regions)
            reasons.append(f"Strong penetration in {regions_str} ({avg_pen:.0%} coverage)")

    # Engagement velocity
    if engagement_velocity > 0.5:
        reasons.append(f"High engagement velocity ({engagement_velocity:.0%}) — early buzz favours {platform_name}")

    # Release model fit
    if scores.get("release_model_match", 0) > 0.7:
        reasons.append(f"Release model well-suited for {label}")

    # Competition window
    if genre_success > 0.6 and audience_score > 0.5:
        reasons.append(f"Low competition expected in chosen window for {genre.lower()} on {platform_name}")

    # Talent match
    if scores.get("talent_match", 0) > 0.7:
        reasons.append(f"Talent profile aligns with {platform_name}'s acquisition strategy")

    return reasons


# ── Legacy API (unchanged signature) ─────────────────────────

def calculate_platform_fit(
    genre: str,
    scale: str,
    audience_type: str,
    release_model: str,
    talent_strategy: str,
    budget_level: str,
) -> List[Dict]:
    """Legacy: calculate fit score from static features only."""
    results = []

    for platform_name, profile in PLATFORM_PROFILES.items():
        scores = {
            "genre_match": _score_genre_match(profile, genre),
            "scale_match": _score_scale_match(profile, scale),
            "audience_match": _score_audience_match(profile, audience_type),
            "release_model_match": _score_release_model_match(profile, release_model),
            "talent_match": _score_talent_match(profile, talent_strategy),
            "budget_match": _score_budget_match(profile, budget_level),
        }

        fit = weighted_score(scores, FIT_WEIGHTS)
        ci = confidence_interval(fit, sample_size=80)

        reasoning = _build_detailed_reasoning(
            platform_name, scores, PLATFORM_METADATA,
            genre, audience_type,
        )

        results.append({
            "platform": platform_name,
            "fit_score": round(fit, 4),
            "confidence": ci,
            "reasoning": reasoning,
        })

    return results


# ── Signal-Enhanced API (Layer 2) ────────────────────────────

def calculate_platform_fit_v2(
    genre: str,
    scale: str,
    audience_type: str,
    release_model: str,
    talent_strategy: str,
    budget_level: str,
    signals: Optional[List[Dict]] = None,
    top_regions: Optional[List[str]] = None,
) -> List[Dict]:
    """
    Enhanced platform fit scoring with signal data and platform metadata.

    Adds three new scoring factors:
      - signal_momentum: aggregate engagement from signals
      - region_penetration: match between top audience regions and platform reach
      - genre_success: platform-specific genre performance
    """
    # Pre-compute signal aggregate
    hype_momentum = 0.0
    avg_velocity = 0.0
    if signals:
        top3 = signals[:3]
        weights_momentum = [0.50, 0.30, 0.20]
        hype_momentum = sum(s["RIS"] * w for s, w in zip(top3, weights_momentum[:len(top3)]))
        avg_velocity = sum(s.get("engagement_velocity", 0) for s in signals) / max(1, len(signals))

    results = []

    for platform_name, profile in PLATFORM_PROFILES.items():
        meta = PLATFORM_METADATA.get(platform_name, {})

        # Base feature scores
        scores = {
            "genre_match": _score_genre_match(profile, genre),
            "scale_match": _score_scale_match(profile, scale),
            "audience_match": _score_audience_match(profile, audience_type),
            "release_model_match": _score_release_model_match(profile, release_model),
            "talent_match": _score_talent_match(profile, talent_strategy),
            "budget_match": _score_budget_match(profile, budget_level),
        }

        # Signal-derived scores
        scores["signal_momentum"] = min(1.0, hype_momentum)

        # Region penetration match
        region_pen = meta.get("region_penetration", {})
        if top_regions:
            pen_scores = [region_pen.get(r, 0.2) for r in top_regions]
            scores["region_penetration"] = sum(pen_scores) / max(1, len(pen_scores))
        else:
            scores["region_penetration"] = profile.get("global_reach", 0.5)

        # Genre success index
        scores["genre_success"] = meta.get("genre_success_index", {}).get(genre, 0.5)

        fit = weighted_score(scores, FIT_WEIGHTS_V2)
        ci = confidence_interval(fit, sample_size=120 if signals else 80)

        reasoning = _build_detailed_reasoning(
            platform_name, scores, PLATFORM_METADATA,
            genre, audience_type,
            top_regions=top_regions,
            engagement_velocity=avg_velocity,
        )

        results.append({
            "platform": platform_name,
            "fit_score": round(fit, 4),
            "confidence": ci,
            "reasoning": reasoning,
        })

    return results


def rank_platforms(platform_scores: List[Dict]) -> List[Dict]:
    """Rank platforms by fit score, best first."""
    return rank_items(platform_scores, key="fit_score", descending=True)


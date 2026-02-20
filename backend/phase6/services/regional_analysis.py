"""
Regional Analysis Service — computes regional audience interest for a film project.

Supports two modes:
  1. Legacy: static profile lookup (compute_regional_interest)
  2. Signal-enhanced: uses signal_aggregator output (compute_regional_interest_with_signals)
"""

from typing import Dict, List, Optional
from phase6.utils.scoring_utils import normalize, bucket_label, rank_items


# Regional profiles: base interest multipliers by language/culture affinity
REGIONAL_PROFILES: Dict[str, Dict[str, float]] = {
    "North America": {
        "english": 1.0, "hindi": 0.3, "korean": 0.5, "spanish": 0.6,
        "mainstream": 0.9, "niche": 0.4, "broad": 0.7,
        "blockbuster": 0.95, "studio": 0.8, "indie": 0.4,
    },
    "Europe": {
        "english": 0.9, "hindi": 0.2, "korean": 0.4, "spanish": 0.5,
        "mainstream": 0.7, "niche": 0.6, "broad": 0.7,
        "blockbuster": 0.7, "studio": 0.7, "indie": 0.7,
    },
    "South Asia": {
        "english": 0.5, "hindi": 1.0, "korean": 0.3, "spanish": 0.1,
        "mainstream": 0.9, "niche": 0.5, "broad": 0.8,
        "blockbuster": 0.9, "studio": 0.8, "indie": 0.5,
    },
    "East Asia": {
        "english": 0.5, "hindi": 0.2, "korean": 1.0, "spanish": 0.1,
        "mainstream": 0.8, "niche": 0.5, "broad": 0.7,
        "blockbuster": 0.85, "studio": 0.7, "indie": 0.4,
    },
    "Latin America": {
        "english": 0.5, "hindi": 0.1, "korean": 0.4, "spanish": 1.0,
        "mainstream": 0.8, "niche": 0.3, "broad": 0.7,
        "blockbuster": 0.7, "studio": 0.6, "indie": 0.4,
    },
    "Middle East": {
        "english": 0.6, "hindi": 0.5, "korean": 0.3, "spanish": 0.1,
        "mainstream": 0.7, "niche": 0.4, "broad": 0.6,
        "blockbuster": 0.7, "studio": 0.6, "indie": 0.3,
    },
    "Africa": {
        "english": 0.7, "hindi": 0.3, "korean": 0.3, "spanish": 0.2,
        "mainstream": 0.6, "niche": 0.4, "broad": 0.6,
        "blockbuster": 0.5, "studio": 0.5, "indie": 0.5,
    },
}


def compute_regional_interest(
    language: str,
    audience_type: str,
    scale: str,
    genre: str,
) -> List[Dict]:
    """Legacy: compute raw interest score from static profiles."""
    lang_key = language.lower()
    results = []

    for region, profile in REGIONAL_PROFILES.items():
        lang_score = profile.get(lang_key, 0.3)
        audience_score = profile.get(audience_type, 0.5)
        scale_score = profile.get(scale, 0.5)
        interest = (lang_score * 0.45) + (audience_score * 0.30) + (scale_score * 0.25)

        results.append({
            "region": region,
            "interest_score": round(interest, 4),
        })

    return results


def compute_regional_interest_with_signals(
    signals: List[Dict],
    language: str,
    audience_type: str,
    scale: str,
) -> List[Dict]:
    """
    Signal-enhanced regional interest.

    Blends the signal aggregator's RIS (70%) with the static profile base (30%)
    to produce a robust interest score per region.
    """
    lang_key = language.lower()
    results = []

    # Build signal lookup
    signal_by_region = {s["region"]: s for s in signals}

    for region, profile in REGIONAL_PROFILES.items():
        # Static base
        lang_score = profile.get(lang_key, 0.3)
        audience_score = profile.get(audience_type, 0.5)
        scale_score = profile.get(scale, 0.5)
        base = (lang_score * 0.45) + (audience_score * 0.30) + (scale_score * 0.25)

        sig = signal_by_region.get(region)
        if sig:
            # Blend: 70% signal RIS + 30% static base
            interest = sig["RIS"] * 0.70 + base * 0.30
            entry = {
                "region": region,
                "lat": sig.get("lat"),
                "lon": sig.get("lon"),
                "interest_score": round(interest, 4),
                "youtube": sig["youtube"],
                "twitter": sig["twitter"],
                "trends": sig["trends"],
                "imdb": sig["imdb"],
                "spotify": sig["spotify"],
                "sentiment": sig["sentiment"],
                "engagement_velocity": sig["engagement_velocity"],
                "trend_direction": sig.get("trend_direction"),
                "source": sig.get("source"),
            }
        else:
            entry = {
                "region": region,
                "lat": None,
                "lon": None,
                "interest_score": round(base, 4),
                "youtube": 0.0, "twitter": 0.0, "trends": 0.0,
                "imdb": 0.0, "spotify": 0.0, "sentiment": 0.0,
                "engagement_velocity": 0.0,
                "trend_direction": None,
                "source": None,
            }
        results.append(entry)

    return results


def normalize_scores(region_scores: List[Dict]) -> List[Dict]:
    """
    Normalize interest scores across regions and add tier labels.
    Preserves any signal fields already present on each entry.
    """
    if not region_scores:
        return []

    max_score = max(r["interest_score"] for r in region_scores)
    min_score = min(r["interest_score"] for r in region_scores)

    for region in region_scores:
        raw = region["interest_score"]
        norm = normalize(raw, min_score, max_score) if max_score != min_score else 0.5
        region["normalized_score"] = round(norm, 4)
        region["tier"] = bucket_label(norm)

    return rank_items(region_scores, key="normalized_score", descending=True)


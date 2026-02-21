"""
Sentiment Engine — Social Buzz & Search Intent Scoring.

Produces SocialScore and SearchScore proxy signals from Phase 6 intel
without external API calls. All values normalized to 0–1.
"""

from typing import Dict, Optional
import hashlib
import time

# ── In-memory cache ──────────────────────────────────────────
_cache: Dict[str, Dict] = {}
_CACHE_TTL = 300  # 5 minutes


def _cache_key(project_id: int) -> str:
    return f"sentiment_{project_id}"


def _deterministic_seed(title: str, salt: str = "") -> float:
    """Generate a deterministic 0–1 float from a string."""
    h = hashlib.sha256(f"{title}:{salt}".encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


# ── Social Score ─────────────────────────────────────────────

def compute_social_score(intel: Dict) -> Dict:
    """
    Social Buzz Score (0–1).

    Derived from:
      - hype_momentum (Phase 6)
      - avg_engagement_velocity (Phase 6)
      - avg_sentiment (Phase 6)
      - talent/audience factors

    Formula:
      SocialScore = 0.35 * hype + 0.25 * velocity + 0.25 * sentiment + 0.15 * audience_factor
    """
    hype = intel.get("hype_momentum", 0.5)
    velocity = intel.get("avg_engagement_velocity", 0.5)
    sentiment = intel.get("avg_sentiment", 0.5)

    # Audience type factor
    audience_type = intel.get("audience_type", "mass")
    audience_factor = {
        "mass": 0.7, "youth": 0.8, "niche": 0.35,
        "family": 0.6, "premium": 0.45, "urban": 0.65,
    }.get(audience_type, 0.5)

    score = (
        0.30 * hype
        + 0.20 * velocity
        + 0.20 * sentiment
        + 0.15 * audience_factor
        + 0.15 * intel.get("reddit_score", 0.0)  # Live Reddit signal
    )
    score = round(max(0.0, min(1.0, score)), 4)

    return {
        "social_score": score,
        "components": {
            "hype_momentum": round(hype, 4),
            "engagement_velocity": round(velocity, 4),
            "sentiment": round(sentiment, 4),
            "audience_factor": round(audience_factor, 4),
            "reddit": round(intel.get("reddit_score", 0.0), 4),
        },
        "interpretation": (
            "Very high social buzz" if score >= 0.75 else
            "Strong social presence" if score >= 0.55 else
            "Moderate social activity" if score >= 0.35 else
            "Low social visibility"
        ),
    }


# ── Search Score ─────────────────────────────────────────────

def compute_search_score(intel: Dict) -> Dict:
    """
    Search Intent Score (0–1).

    Proxy derived from genre popularity, scale,
    language reach, and platform fit.

    Formula:
      SearchScore = 0.30 * genre_heat + 0.25 * platform_fit + 0.20 * scale_factor + 0.25 * language_reach
    """
    # Genre heat map
    genre = (intel.get("genre") or "drama").lower()
    genre_heat = {
        "action": 0.8, "thriller": 0.75, "comedy": 0.7, "horror": 0.72,
        "romance": 0.6, "drama": 0.55, "sci-fi": 0.78, "fantasy": 0.7,
        "documentary": 0.3, "animation": 0.65, "crime": 0.68,
        "mystery": 0.62, "adventure": 0.72, "musical": 0.45,
    }.get(genre, 0.5)

    platform_fit = intel.get("platform_fit", 0.5)

    # Scale factor
    scale = (intel.get("scale") or "medium").lower()
    scale_factor = {
        "tentpole": 0.9, "big_budget": 0.8, "mid_budget": 0.6, "indie": 0.35,
        "large": 0.85, "medium": 0.6, "small": 0.35, "micro": 0.2,
    }.get(scale, 0.5)

    # Language reach
    language = (intel.get("language") or "hindi").lower()
    language_reach = {
        "hindi": 0.8, "english": 0.9, "tamil": 0.55, "telugu": 0.55,
        "malayalam": 0.4, "kannada": 0.35, "bengali": 0.45,
        "marathi": 0.35, "punjabi": 0.3, "spanish": 0.75,
        "korean": 0.6, "japanese": 0.55, "mandarin": 0.7,
    }.get(language, 0.4)

    score = (
        0.30 * genre_heat
        + 0.25 * platform_fit
        + 0.20 * scale_factor
        + 0.25 * language_reach
    )
    score = round(max(0.0, min(1.0, score)), 4)

    return {
        "search_score": score,
        "components": {
            "genre_heat": round(genre_heat, 4),
            "platform_fit": round(platform_fit, 4),
            "scale_factor": round(scale_factor, 4),
            "language_reach": round(language_reach, 4),
        },
        "interpretation": (
            "High search intent" if score >= 0.7 else
            "Moderate search interest" if score >= 0.45 else
            "Low search visibility"
        ),
    }


# ── Engagement Score ─────────────────────────────────────────

def compute_engagement_score(intel: Dict) -> Dict:
    """
    Engagement Depth Score (0–1) — YouTube/platform engagement proxy.

    Formula:
      EngagementScore = 0.35 * velocity + 0.30 * sentiment + 0.20 * regional_strength + 0.15 * dubbing_gain
    """
    velocity = intel.get("avg_engagement_velocity", 0.5)
    sentiment = intel.get("avg_sentiment", 0.5)
    regional = intel.get("regional_strength", 0.5)
    dubbing = min(1.0, intel.get("dubbing_gain", 0.0))

    score = (
        0.35 * velocity
        + 0.30 * sentiment
        + 0.20 * regional
        + 0.15 * dubbing
    )
    score = round(max(0.0, min(1.0, score)), 4)

    return {
        "engagement_score": score,
        "components": {
            "engagement_velocity": round(velocity, 4),
            "sentiment": round(sentiment, 4),
            "regional_strength": round(regional, 4),
            "dubbing_expansion": round(dubbing, 4),
        },
        "interpretation": (
            "Deep audience engagement" if score >= 0.7 else
            "Healthy engagement" if score >= 0.45 else
            "Surface-level engagement"
        ),
    }


# ── Combined Sentiment Analysis ─────────────────────────────

def analyze_sentiment(intel: Dict) -> Dict:
    """
    Full sentiment analysis combining all three scores.
    Uses caching to avoid recomputation within TTL.
    """
    project_id = intel.get("project_id", 0)
    key = _cache_key(project_id)

    # Check cache
    if key in _cache:
        cached = _cache[key]
        if time.time() - cached.get("_ts", 0) < _CACHE_TTL:
            return cached["data"]

    try:
        social = compute_social_score(intel)
        search = compute_search_score(intel)
        engagement = compute_engagement_score(intel)

        result = {
            "social": social,
            "search": search,
            "engagement": engagement,
            "social_score": social["social_score"],
            "search_score": search["search_score"],
            "engagement_score": engagement["engagement_score"],
        }
    except Exception:
        # Fallback
        result = {
            "social": {"social_score": 0.5, "components": {}, "interpretation": "Fallback"},
            "search": {"search_score": 0.5, "components": {}, "interpretation": "Fallback"},
            "engagement": {"engagement_score": 0.5, "components": {}, "interpretation": "Fallback"},
            "social_score": 0.5,
            "search_score": 0.5,
            "engagement_score": 0.5,
        }

    # Cache
    _cache[key] = {"data": result, "_ts": time.time()}
    return result

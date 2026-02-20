"""
YouTube Signal Service — Fetches video engagement metrics via YouTube Data API v3.

Uses YOUTUBE_API_KEY from .env.
Falls back to deterministic dummy signals on any failure.

Returns normalized values (0–1).
"""

import os
import time
import random
import hashlib
from typing import Dict, List, Optional

# ── Cache ──
_cache: Dict[str, Dict] = {}
_cache_ts: Dict[str, float] = {}
CACHE_TTL = 900  # 15 minutes


def _get_api_key() -> Optional[str]:
    return os.environ.get("YOUTUBE_API_KEY", "").strip() or None


def _dummy_signal(seed: str) -> Dict:
    """Deterministic fallback using hash-based seeding."""
    h = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
    rng = random.Random(h)
    return {
        "view_count": rng.randint(50000, 5000000),
        "like_count": rng.randint(1000, 100000),
        "comment_count": rng.randint(100, 10000),
        "engagement_ratio": round(rng.uniform(0.01, 0.08), 4),
        "growth_delta": round(rng.uniform(0.0, 0.3), 4),
        "normalized_score": round(rng.uniform(0.4, 0.8), 4),
        "source": "fallback",
    }


def _search_video_id(film_title: str, api_key: str) -> Optional[str]:
    """Search YouTube for a trailer and return video ID."""
    try:
        import httpx
        resp = httpx.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part": "snippet",
                "q": f"{film_title} official trailer",
                "type": "video",
                "maxResults": 1,
                "key": api_key,
            },
            timeout=10,
        )
        if resp.status_code == 200:
            items = resp.json().get("items", [])
            if items:
                return items[0]["id"]["videoId"]
    except Exception:
        pass
    return None


def _get_video_stats(video_id: str, api_key: str) -> Optional[Dict]:
    """Fetch video statistics from YouTube Data API v3."""
    try:
        import httpx
        resp = httpx.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "part": "statistics",
                "id": video_id,
                "key": api_key,
            },
            timeout=10,
        )
        if resp.status_code == 200:
            items = resp.json().get("items", [])
            if items:
                return items[0].get("statistics", {})
    except Exception:
        pass
    return None


def fetch_youtube_signal(film_title: str, region: str = "global") -> Dict:
    """
    Fetch YouTube engagement signal for a film.

    Returns: {view_count, like_count, comment_count, engagement_ratio,
              growth_delta, normalized_score, source}
    """
    cache_key = f"youtube:{film_title}:{region}"
    now = time.time()

    if cache_key in _cache and (now - _cache_ts.get(cache_key, 0)) < CACHE_TTL:
        return _cache[cache_key]

    api_key = _get_api_key()
    if not api_key:
        result = _dummy_signal(f"{film_title}:{region}")
        _cache[cache_key] = result
        _cache_ts[cache_key] = now
        return result

    try:
        video_id = _search_video_id(film_title, api_key)
        if not video_id:
            result = _dummy_signal(f"{film_title}:{region}")
            _cache[cache_key] = result
            _cache_ts[cache_key] = now
            return result

        stats = _get_video_stats(video_id, api_key)
        if not stats:
            result = _dummy_signal(f"{film_title}:{region}")
            _cache[cache_key] = result
            _cache_ts[cache_key] = now
            return result

        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))

        engagement = round(likes / max(1, views), 4)
        # Normalize: views capped at 10M for normalization
        view_norm = round(min(1.0, views / 10_000_000), 4)
        like_norm = round(min(1.0, likes / 500_000), 4)
        comment_norm = round(min(1.0, comments / 50_000), 4)
        engagement_norm = round(min(1.0, engagement * 20), 4)  # 0.05 engagement = 1.0

        growth_delta = round(min(1.0, (views + likes * 10 + comments * 50) / 15_000_000), 4)

        normalized = round(
            0.30 * view_norm
            + 0.25 * like_norm
            + 0.20 * engagement_norm
            + 0.15 * comment_norm
            + 0.10 * growth_delta,
            4,
        )

        result = {
            "view_count": views,
            "like_count": likes,
            "comment_count": comments,
            "engagement_ratio": engagement,
            "growth_delta": growth_delta,
            "normalized_score": round(min(1.0, normalized), 4),
            "source": "live",
            "video_id": video_id,
        }
    except Exception:
        result = _dummy_signal(f"{film_title}:{region}")

    _cache[cache_key] = result
    _cache_ts[cache_key] = now
    return result


def fetch_youtube_signals_batch(
    film_title: str,
    regions: List[str],
) -> Dict[str, Dict]:
    """Fetch one global YouTube signal and distribute with region weights."""
    global_signal = fetch_youtube_signal(film_title, "global")

    # Same video stats, but region modifiers based on language/geography affinity
    region_weights = {
        "North America": 1.0, "Europe": 0.9, "East Asia": 0.85,
        "South Asia": 0.7, "Latin America": 0.65, "Middle East": 0.6, "Africa": 0.5,
    }
    results = {}
    for region in regions:
        weight = region_weights.get(region, 0.6)
        results[region] = {
            **global_signal,
            "normalized_score": round(global_signal["normalized_score"] * weight, 4),
        }
    return results

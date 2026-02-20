"""
Popularity Signal Service — Fetches trending & popularity data from TMDB API.

Uses TMDB_API_KEY from .env.
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

# ── Genre name → TMDB genre ID mapping ──
GENRE_IDS = {
    "Action": 28, "Drama": 18, "Comedy": 35, "Horror": 27,
    "Thriller": 53, "Romance": 10749, "Sci-Fi": 878,
    "Documentary": 99, "Animation": 16,
}


def _get_api_key() -> Optional[str]:
    return os.environ.get("TMDB_API_KEY", "").strip() or None


def _dummy_signal(seed: str) -> Dict:
    """Deterministic fallback using hash-based seeding."""
    h = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
    rng = random.Random(h)
    return {
        "trending_score": round(rng.uniform(5, 50), 2),
        "genre_popularity": round(rng.uniform(0.3, 0.9), 4),
        "similar_demand": round(rng.uniform(0.2, 0.7), 4),
        "normalized_score": round(rng.uniform(0.4, 0.8), 4),
        "source": "fallback",
    }


def _fetch_trending(api_key: str) -> List[Dict]:
    """Fetch trending movies from TMDB."""
    try:
        import httpx
        resp = httpx.get(
            "https://api.themoviedb.org/3/trending/movie/week",
            params={"api_key": api_key},
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get("results", [])
    except Exception:
        pass
    return []


def _fetch_genre_movies(api_key: str, genre_id: int) -> List[Dict]:
    """Fetch popular movies by genre from TMDB."""
    try:
        import httpx
        resp = httpx.get(
            "https://api.themoviedb.org/3/discover/movie",
            params={
                "api_key": api_key,
                "sort_by": "popularity.desc",
                "with_genres": genre_id,
                "page": 1,
            },
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get("results", [])
    except Exception:
        pass
    return []


def fetch_popularity_signal(film_title: str, genre: str = "Drama") -> Dict:
    """
    Fetch TMDB popularity signal for a film.

    Returns: {trending_score, genre_popularity, similar_demand, normalized_score, source}
    """
    cache_key = f"tmdb:{film_title}:{genre}"
    now = time.time()

    if cache_key in _cache and (now - _cache_ts.get(cache_key, 0)) < CACHE_TTL:
        return _cache[cache_key]

    api_key = _get_api_key()
    if not api_key:
        result = _dummy_signal(f"{film_title}:{genre}")
        _cache[cache_key] = result
        _cache_ts[cache_key] = now
        return result

    try:
        # Trending movies
        trending = _fetch_trending(api_key)
        trending_scores = [m.get("popularity", 0) for m in trending]
        max_trend = max(trending_scores) if trending_scores else 100
        avg_trend = sum(trending_scores) / len(trending_scores) if trending_scores else 50

        # Check if our film is trending
        film_match = next(
            (m for m in trending if film_title.lower() in m.get("title", "").lower()),
            None,
        )
        film_trend = film_match.get("popularity", 0) if film_match else avg_trend * 0.3
        trending_score = round(film_trend, 2)

        # Genre popularity
        genre_id = GENRE_IDS.get(genre, 18)
        genre_movies = _fetch_genre_movies(api_key, genre_id)
        genre_pops = [m.get("popularity", 0) for m in genre_movies]
        avg_genre_pop = sum(genre_pops) / len(genre_pops) if genre_pops else 50
        genre_popularity = round(min(1.0, avg_genre_pop / max(1, max_trend)), 4)

        # Similar film demand proxy
        similar_demand = round(min(1.0, len(genre_movies) / 20), 4)

        # Normalize
        normalized = round(
            0.40 * min(1.0, trending_score / max(1, max_trend))
            + 0.35 * genre_popularity
            + 0.25 * similar_demand,
            4,
        )

        result = {
            "trending_score": trending_score,
            "genre_popularity": genre_popularity,
            "similar_demand": similar_demand,
            "normalized_score": round(min(1.0, normalized), 4),
            "source": "live" if film_match else "genre_proxy",
        }
    except Exception:
        result = _dummy_signal(f"{film_title}:{genre}")

    _cache[cache_key] = result
    _cache_ts[cache_key] = now
    return result


def fetch_popularity_signals_batch(
    film_title: str,
    genre: str,
    regions: List[str],
) -> Dict[str, Dict]:
    """Fetch one global TMDB signal and distribute with region weights."""
    global_signal = fetch_popularity_signal(film_title, genre)

    region_weights = {
        "North America": 1.0, "Europe": 0.9, "East Asia": 0.85,
        "South Asia": 0.7, "Latin America": 0.65, "Middle East": 0.6, "Africa": 0.5,
    }
    results = {}
    for region in regions:
        w = region_weights.get(region, 0.6)
        results[region] = {
            **global_signal,
            "normalized_score": round(global_signal["normalized_score"] * w, 4),
        }
    return results

"""
Google Trends Signal Service — Fetches search interest data via pytrends.

Uses pytrends library (no API key needed).
Falls back to deterministic dummy signals on any failure / rate limit.

Returns normalized values (0–1).
"""

import time
import random
import hashlib
from typing import Dict, List

# ── Cache ──
_cache: Dict[str, Dict] = {}
_cache_ts: Dict[str, float] = {}
CACHE_TTL = 900  # 15 minutes

# ── Region → pytrends geo code mapping ──
REGION_GEO = {
    "North America": "US",
    "Europe": "GB",
    "East Asia": "JP",
    "South Asia": "IN",
    "Latin America": "BR",
    "Middle East": "AE",
    "Africa": "ZA",
}


def _dummy_signal(seed: str) -> Dict:
    """Deterministic fallback using hash-based seeding."""
    h = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
    rng = random.Random(h)
    return {
        "interest": rng.randint(20, 90),
        "trend_delta": round(rng.uniform(-0.1, 0.3), 4),
        "search_velocity": round(rng.uniform(0.05, 0.5), 4),
        "normalized_score": round(rng.uniform(0.4, 0.8), 4),
        "source": "fallback",
    }


def fetch_trends_signal(film_title: str, region: str = "global") -> Dict:
    """
    Fetch Google Trends signal for a film in a given region.

    Returns: {interest, trend_delta, search_velocity, normalized_score, source}
    """
    cache_key = f"trends:{film_title}:{region}"
    now = time.time()

    if cache_key in _cache and (now - _cache_ts.get(cache_key, 0)) < CACHE_TTL:
        return _cache[cache_key]

    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 25))

        geo = REGION_GEO.get(region, "")
        pytrends.build_payload(
            [film_title],
            cat=0,
            timeframe="now 7-d",
            geo=geo,
        )

        interest_df = pytrends.interest_over_time()

        if interest_df is not None and not interest_df.empty and film_title in interest_df.columns:
            values = interest_df[film_title].tolist()
            current = values[-1] if values else 50
            avg = sum(values) / len(values) if values else 50
            peak = max(values) if values else 100

            interest = current
            trend_delta = round((current - avg) / max(1, avg), 4)
            search_velocity = round(min(1.0, current / max(1, peak)), 4)
            normalized = round(
                0.40 * min(1.0, interest / 100)
                + 0.35 * max(0, min(1.0, (trend_delta + 0.5)))
                + 0.25 * search_velocity,
                4,
            )

            result = {
                "interest": interest,
                "trend_delta": trend_delta,
                "search_velocity": search_velocity,
                "normalized_score": round(min(1.0, normalized), 4),
                "source": "live",
            }
        else:
            result = _dummy_signal(f"{film_title}:{region}")
    except Exception:
        result = _dummy_signal(f"{film_title}:{region}")

    _cache[cache_key] = result
    _cache_ts[cache_key] = now
    return result


def fetch_trends_signals_batch(
    film_title: str,
    regions: List[str],
) -> Dict[str, Dict]:
    """Fetch Google Trends signals for multiple regions."""
    results = {}
    for region in regions:
        results[region] = fetch_trends_signal(film_title, region)
    return results

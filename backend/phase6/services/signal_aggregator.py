"""
Signal Aggregator — produces Regional Interest Scores (RIS) from
live multi-platform audience signals with heuristic fallback.

Live signal sources (with graceful fallback):
  - Twitter/X  (snscrape + sentiment)
  - YouTube    (Data API v3)
  - Google Trends (pytrends)
  - TMDB       (trending + genre popularity)
  - Reddit     (OAuth API)
  - Heuristic  (genre/language/scale-based historical proxy)

Each signal is computed per-region, then combined into a composite RIS.
All values normalized to 0–1. Geo coordinates attached.

RIS = 0.25 * Twitter + 0.20 * YouTube + 0.15 * Trends + 0.15 * Reddit + 0.15 * Popularity + 0.10 * GenreHistorical
"""

import time
from typing import Dict, List, Optional
from phase6.utils.scoring_utils import weighted_score, normalize

# ── Live Signal Services ─────────────────────────────────────
from phase6.services.twitter_signal import fetch_twitter_signal
from phase6.services.youtube_signal import fetch_youtube_signals_batch
from phase6.services.trends_signal import fetch_trends_signal
from phase6.services.popularity_signal import fetch_popularity_signals_batch
from phase6.services.reddit_signal import fetch_reddit_signals_batch
from phase6.services.geo_service import fetch_coordinates

# ── Signal Weights (updated per spec) ────────────────────────
SIGNAL_WEIGHTS = {
    "twitter": 0.25,
    "youtube": 0.20,
    "trends": 0.15,
    "reddit": 0.15,
    "popularity": 0.15,
    "genre_historical": 0.10,
}

# ── Regional Digital Penetration ─────────────────────────────
DIGITAL_PENETRATION: Dict[str, float] = {
    "North America": 0.95,
    "Europe": 0.90,
    "South Asia": 0.70,
    "East Asia": 0.88,
    "Latin America": 0.65,
    "Middle East": 0.72,
    "Africa": 0.45,
}

# ── Genre affinity (historical baseline) ─────────────────────
GENRE_SIGNAL_BOOST: Dict[str, Dict[str, float]] = {
    "Action":      {"youtube": 0.9, "twitter": 0.8, "trends": 0.7, "imdb": 0.6, "spotify": 0.3},
    "Drama":       {"youtube": 0.5, "twitter": 0.6, "trends": 0.5, "imdb": 0.8, "spotify": 0.5},
    "Comedy":      {"youtube": 0.7, "twitter": 0.7, "trends": 0.6, "imdb": 0.5, "spotify": 0.3},
    "Horror":      {"youtube": 0.8, "twitter": 0.9, "trends": 0.8, "imdb": 0.5, "spotify": 0.4},
    "Thriller":    {"youtube": 0.75, "twitter": 0.85, "trends": 0.7, "imdb": 0.7, "spotify": 0.4},
    "Romance":     {"youtube": 0.5, "twitter": 0.6, "trends": 0.5, "imdb": 0.6, "spotify": 0.7},
    "Sci-Fi":      {"youtube": 0.85, "twitter": 0.7, "trends": 0.65, "imdb": 0.7, "spotify": 0.5},
    "Documentary": {"youtube": 0.4, "twitter": 0.5, "trends": 0.4, "imdb": 0.7, "spotify": 0.2},
    "Animation":   {"youtube": 0.8, "twitter": 0.6, "trends": 0.6, "imdb": 0.6, "spotify": 0.6},
}
DEFAULT_GENRE_BOOST = {"youtube": 0.5, "twitter": 0.5, "trends": 0.5, "imdb": 0.5, "spotify": 0.3}

# ── Language → region affinity ───────────────────────────────
LANGUAGE_REGION_BUZZ: Dict[str, Dict[str, float]] = {
    "english":  {"North America": 1.0, "Europe": 0.85, "South Asia": 0.45, "East Asia": 0.40, "Latin America": 0.40, "Middle East": 0.50, "Africa": 0.65},
    "hindi":    {"North America": 0.25, "Europe": 0.15, "South Asia": 1.0,  "East Asia": 0.10, "Latin America": 0.05, "Middle East": 0.40, "Africa": 0.20},
    "korean":   {"North America": 0.45, "Europe": 0.40, "South Asia": 0.25, "East Asia": 1.0,  "Latin America": 0.30, "Middle East": 0.20, "Africa": 0.15},
    "spanish":  {"North America": 0.50, "Europe": 0.45, "South Asia": 0.05, "East Asia": 0.05, "Latin America": 1.0,  "Middle East": 0.05, "Africa": 0.10},
    "telugu":   {"North America": 0.15, "Europe": 0.08, "South Asia": 0.80, "East Asia": 0.05, "Latin America": 0.02, "Middle East": 0.20, "Africa": 0.05},
    "tamil":    {"North America": 0.15, "Europe": 0.10, "South Asia": 0.75, "East Asia": 0.05, "Latin America": 0.02, "Middle East": 0.15, "Africa": 0.05},
}
DEFAULT_LANG_BUZZ = {"North America": 0.3, "Europe": 0.3, "South Asia": 0.3, "East Asia": 0.3, "Latin America": 0.3, "Middle East": 0.3, "Africa": 0.3}

# ── Scale / talent multipliers ───────────────────────────────
SCALE_VELOCITY = {"indie": 0.3, "studio": 0.65, "blockbuster": 1.0}
TALENT_VELOCITY = {"unknown": 0.15, "emerging": 0.35, "established": 0.70, "starDriven": 1.0}
BUDGET_MARKETING_POWER = {"low": 0.3, "medium": 0.6, "high": 1.0}

# ── Aggregated signal cache ──────────────────────────────────
_agg_cache: Dict[str, List[Dict]] = {}
_agg_cache_ts: Dict[str, float] = {}
AGG_CACHE_TTL = 900  # 15 minutes


def _genre_historical_score(genre: str, region: str, language: str) -> float:
    """Genre-based historical interest (baseline signal)."""
    genre_boost = GENRE_SIGNAL_BOOST.get(genre, DEFAULT_GENRE_BOOST)
    lang_buzz = LANGUAGE_REGION_BUZZ.get(language.lower(), DEFAULT_LANG_BUZZ).get(region, 0.3)
    raw = sum(genre_boost.values()) / len(genre_boost)
    return round(min(1.0, (raw * 0.5 + lang_buzz * 0.5)), 4)


def compute_signals(
    genre: str,
    language: str,
    scale: str,
    talent_strategy: str,
    budget_level: str,
    audience_type: str,
    film_title: str = "",
    use_live: bool = True,
) -> List[Dict]:
    """
    Compute multi-platform audience signals for every region.

    Tries live API calls first (YouTube, Twitter, Trends, TMDB).
    Falls back to heuristic engine on any failure.
    Attaches geo coordinates (lat/lon) to each region.

    Returns a list of per-region dicts:
        {region, lat, lon, youtube, twitter, trends, sentiment, RIS,
         engagement_velocity, trend_direction, popularity, imdb, spotify, source}
    """
    # Cache check
    cache_key = f"{film_title or genre}:{language}:{scale}:{talent_strategy}:{budget_level}"
    now = time.time()
    if cache_key in _agg_cache and (now - _agg_cache_ts.get(cache_key, 0)) < AGG_CACHE_TTL:
        return _agg_cache[cache_key]

    title = film_title or genre  # Use genre as search term if no title
    regions = list(DIGITAL_PENETRATION.keys())

    # ── Fetch live signals (batch where possible) ────────────
    live_youtube = {}
    live_trends = {}
    live_popularity = {}
    live_twitter = {}

    if use_live and title:
        try:
            live_youtube = fetch_youtube_signals_batch(title, regions)
        except Exception:
            pass

        try:
            live_popularity = fetch_popularity_signals_batch(title, genre, regions)
        except Exception:
            pass

        for region in regions:
            try:
                live_twitter[region] = fetch_twitter_signal(title, region)
            except Exception:
                pass
            try:
                live_trends[region] = fetch_trends_signal(title, region)
            except Exception:
                pass

        try:
            live_reddit = fetch_reddit_signals_batch(title, regions)
        except Exception:
            live_reddit = {}

    # ── Heuristic engine (always available) ──────────────────
    genre_boost = GENRE_SIGNAL_BOOST.get(genre, DEFAULT_GENRE_BOOST)
    lang_key = language.lower()
    lang_buzz_map = LANGUAGE_REGION_BUZZ.get(lang_key, DEFAULT_LANG_BUZZ)
    velocity_base = (SCALE_VELOCITY.get(scale, 0.5) * 0.5
                     + TALENT_VELOCITY.get(talent_strategy, 0.3) * 0.5)
    marketing_power = BUDGET_MARKETING_POWER.get(budget_level, 0.5)

    results: List[Dict] = []

    for region in regions:
        penetration = DIGITAL_PENETRATION[region]
        lang_buzz = lang_buzz_map.get(region, 0.3)

        # ── Combine live + heuristic for each signal ─────────
        # YouTube
        yt_live = live_youtube.get(region, {}).get("normalized_score")
        yt_heuristic = round(min(1.0, (genre_boost["youtube"] * 0.35 + lang_buzz * 0.30
                                       + velocity_base * 0.20 + marketing_power * 0.15) * penetration), 4)
        yt = _blend(yt_live, yt_heuristic)

        # Twitter
        tw_live = live_twitter.get(region, {}).get("normalized_score")
        tw_heuristic = round(min(1.0, (genre_boost["twitter"] * 0.40 + lang_buzz * 0.30
                                       + velocity_base * 0.30) * penetration), 4)
        tw = _blend(tw_live, tw_heuristic)

        # Google Trends
        tr_live = live_trends.get(region, {}).get("normalized_score")
        tr_heuristic = round(min(1.0, (genre_boost["trends"] * 0.35 + lang_buzz * 0.35
                                       + velocity_base * 0.30) * penetration), 4)
        tr = _blend(tr_live, tr_heuristic)

        # Popularity (TMDB)
        pop_live = live_popularity.get(region, {}).get("normalized_score")
        pop_heuristic = _genre_historical_score(genre, region, language)
        pop = _blend(pop_live, pop_heuristic)

        # Genre historical baseline
        genre_hist = _genre_historical_score(genre, region, language)

        # IMDb (kept as heuristic — no live source specified)
        audience_mod = {"niche": 0.7, "broad": 0.5, "mainstream": 0.4}.get(audience_type, 0.5)
        imdb = round(min(1.0, genre_boost["imdb"] * 0.50 + lang_buzz * 0.25 + audience_mod * 0.25), 4)

        # Spotify (heuristic)
        spotify = round(min(1.0, genre_boost["spotify"] * 0.60 + lang_buzz * 0.40), 4)

        # Reddit
        rd_live = live_reddit.get(region, {}).get("normalized_score") if 'live_reddit' in dir() else None
        rd_heuristic = round(min(1.0, (lang_buzz * 0.40 + velocity_base * 0.30
                                       + genre_boost.get("twitter", 0.5) * 0.30) * penetration), 4)
        rd = _blend(rd_live, rd_heuristic)

        # ── Composite RIS (updated formula with Reddit) ──────
        ris = round(
            SIGNAL_WEIGHTS["twitter"] * tw
            + SIGNAL_WEIGHTS["youtube"] * yt
            + SIGNAL_WEIGHTS["trends"] * tr
            + SIGNAL_WEIGHTS["reddit"] * rd
            + SIGNAL_WEIGHTS["popularity"] * pop
            + SIGNAL_WEIGHTS["genre_historical"] * genre_hist,
            4,
        )

        # Sentiment
        tw_sentiment = live_twitter.get(region, {}).get("sentiment")
        sentiment = tw_sentiment if tw_sentiment is not None else round(tw * 0.3 + yt * 0.2 + imdb * 0.3 + spotify * 0.2, 4)

        # Velocity / trend direction
        tw_velocity = live_twitter.get(region, {}).get("velocity", 0)
        tr_delta = live_trends.get(region, {}).get("trend_delta", 0)
        eng_velocity = round(velocity_base * penetration, 4)
        trend_direction = "up" if (tw_velocity > 0.2 or tr_delta > 0.05 or eng_velocity > 0.4) else "down"

        # Geo coordinates
        lat, lon = fetch_coordinates(region)

        # Source tracking
        has_live = any([
            live_youtube.get(region, {}).get("source") == "live",
            live_twitter.get(region, {}).get("source") == "live",
            live_trends.get(region, {}).get("source") == "live",
            live_popularity.get(region, {}).get("source") == "live",
            live_reddit.get(region, {}).get("source") == "live" if 'live_reddit' in dir() else False,
        ])

        results.append({
            "region": region,
            "lat": lat,
            "lon": lon,
            "youtube": yt,
            "twitter": tw,
            "trends": tr,
            "reddit": rd,
            "imdb": imdb,
            "spotify": spotify,
            "sentiment": sentiment,
            "RIS": ris,
            "engagement_velocity": eng_velocity,
            "trend_direction": trend_direction,
            "source": "live" if has_live else "heuristic",
        })

    # Sort by RIS descending
    results.sort(key=lambda x: x["RIS"], reverse=True)

    # Cache
    _agg_cache[cache_key] = results
    _agg_cache_ts[cache_key] = now
    return results


def _blend(live_val: Optional[float], heuristic_val: float, live_weight: float = 0.7) -> float:
    """Blend live and heuristic signals. Live gets higher weight when available."""
    if live_val is not None and 0 <= live_val <= 1:
        return round(live_weight * live_val + (1 - live_weight) * heuristic_val, 4)
    return heuristic_val


def get_top_regions(signals: List[Dict], threshold: float = 0.45) -> List[str]:
    """Return regions with RIS above threshold."""
    return [s["region"] for s in signals if s["RIS"] >= threshold]


def compute_hype_momentum(signals: List[Dict]) -> float:
    """
    Aggregate hype momentum across all regions.
    Weighted average of top-3 region RIS values.
    """
    top3 = signals[:3]  # already sorted by RIS
    if not top3:
        return 0.0
    weights = [0.50, 0.30, 0.20]
    momentum = sum(s["RIS"] * w for s, w in zip(top3, weights[:len(top3)]))
    return round(momentum, 4)


def compute_region_dominance(signals: List[Dict]) -> float:
    """
    How dominant is the top region relative to others.
    High value = concentrated interest. Low = spread evenly.
    """
    if not signals:
        return 0.0
    top_ris = signals[0]["RIS"]
    avg_ris = sum(s["RIS"] for s in signals) / len(signals)
    return round(min(1.0, top_ris / max(0.01, avg_ris) - 0.5), 4)


def compute_cross_language_demand(signals: List[Dict], native_language: str) -> float:
    """
    How much interest exists in non-native-language regions.
    High value = strong dubbing / subtitle opportunity.
    """
    lang_buzz = LANGUAGE_REGION_BUZZ.get(native_language.lower(), DEFAULT_LANG_BUZZ)
    native_regions = [r for r, v in lang_buzz.items() if v >= 0.7]
    total_ris = sum(s["RIS"] for s in signals)
    non_native_ris = sum(s["RIS"] for s in signals if s["region"] not in native_regions)
    return round(non_native_ris / max(0.01, total_ris), 4)


def compute_signals_from_db(film_id: int, db=None) -> List[Dict]:
    """
    Read latest cached signals from the signal_cache table.
    Fast path for user-facing endpoints — no API calls.
    Falls back to empty list if no cached signals exist.
    """
    if db is None:
        return []

    try:
        from signal_models import SignalCache
        from phase6.services.geo_service import fetch_coordinates

        cached = db.query(SignalCache).filter_by(film_id=film_id).all()
        if not cached:
            return []

        results = []
        for row in cached:
            lat, lon = fetch_coordinates(row.region)
            results.append({
                "region": row.region,
                "lat": lat,
                "lon": lon,
                "youtube": row.youtube,
                "twitter": row.twitter,
                "trends": row.trends,
                "reddit": row.reddit,
                "tmdb": row.tmdb,
                "imdb": 0.5,  # kept as heuristic
                "spotify": 0.5,
                "sentiment": row.sentiment,
                "RIS": row.composite_ris,
                "engagement_velocity": abs(row.velocity),
                "trend_direction": "up" if row.momentum > 0.02 else "down",
                "momentum": row.momentum,
                "velocity": row.velocity,
                "source": row.source,
                "piracy": row.piracy,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None,
            })

        results.sort(key=lambda x: x["RIS"], reverse=True)
        return results
    except Exception:
        return []

"""
Reddit Signal Service — Fetches discussion metrics via Reddit OAuth API.

Uses REDDIT_CLIENT_ID + REDDIT_CLIENT_SECRET from .env.
Searches relevant subreddits for film mentions and computes engagement.
Falls back to deterministic heuristic on any failure.

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

# ── Auth token cache ──
_token: Optional[str] = None
_token_expiry: float = 0

# ── Subreddits to search ──
SEARCH_SUBREDDITS = [
    "movies", "bollywood", "boxoffice", "entertainment",
    "indiancinema", "tollywood", "kollywood",
]


def _get_credentials():
    client_id = os.environ.get("REDDIT_CLIENT_ID", "").strip()
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "").strip()
    return client_id or None, client_secret or None


def _get_access_token() -> Optional[str]:
    """Get Reddit OAuth access token (application-only flow)."""
    global _token, _token_expiry

    now = time.time()
    if _token and now < _token_expiry:
        return _token

    client_id, client_secret = _get_credentials()
    if not client_id or not client_secret:
        return None

    try:
        import httpx
        resp = httpx.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=(client_id, client_secret),
            data={"grant_type": "client_credentials"},
            headers={"User-Agent": "FilmDSP/1.0"},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            _token = data.get("access_token")
            _token_expiry = now + data.get("expires_in", 3600) - 60
            return _token
    except Exception:
        pass
    return None


def _dummy_signal(seed: str) -> Dict:
    """Deterministic fallback using hash-based seeding."""
    h = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
    rng = random.Random(h)
    return {
        "mention_count": rng.randint(5, 200),
        "comment_depth": round(rng.uniform(2, 15), 1),
        "upvote_ratio": round(rng.uniform(0.5, 0.95), 4),
        "sentiment": round(rng.uniform(0.4, 0.8), 4),
        "normalized_score": round(rng.uniform(0.3, 0.7), 4),
        "source": "fallback",
    }


def _search_subreddit(token: str, subreddit: str, query: str, limit: int = 25) -> List[Dict]:
    """Search a subreddit for posts matching query."""
    try:
        import httpx
        resp = httpx.get(
            f"https://oauth.reddit.com/r/{subreddit}/search",
            params={
                "q": query,
                "sort": "relevance",
                "t": "week",
                "limit": limit,
                "restrict_sr": "true",
            },
            headers={
                "Authorization": f"Bearer {token}",
                "User-Agent": "FilmDSP/1.0",
            },
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get("data", {}).get("children", [])
    except Exception:
        pass
    return []


def _compute_sentiment_from_posts(posts: List[Dict]) -> float:
    """Simple keyword-based sentiment from post titles and text."""
    positive = {"amazing", "great", "love", "best", "excited", "awesome", "hit",
                "blockbuster", "brilliant", "masterpiece", "fantastic", "excellent"}
    negative = {"bad", "worst", "flop", "terrible", "boring", "disappointing",
                "overrated", "disaster", "mediocre", "cringe"}

    pos_count = 0
    neg_count = 0
    for post in posts:
        data = post.get("data", {})
        text = f"{data.get('title', '')} {data.get('selftext', '')}".lower()
        pos_count += sum(1 for w in positive if w in text)
        neg_count += sum(1 for w in negative if w in text)

    total = pos_count + neg_count
    if total == 0:
        return 0.6  # slightly positive default
    return round(0.5 + (pos_count - neg_count) / (total * 2), 4)


def fetch_reddit_signal(film_title: str, region: str = "global") -> Dict:
    """
    Fetch Reddit engagement signal for a film.

    RedditScore = mentions × engagement_depth × sentiment (normalized 0–1)

    Returns: {mention_count, comment_depth, upvote_ratio, sentiment,
              normalized_score, source}
    """
    cache_key = f"reddit:{film_title}:{region}"
    now = time.time()

    if cache_key in _cache and (now - _cache_ts.get(cache_key, 0)) < CACHE_TTL:
        return _cache[cache_key]

    token = _get_access_token()
    if not token:
        result = _dummy_signal(f"{film_title}:{region}")
        _cache[cache_key] = result
        _cache_ts[cache_key] = now
        return result

    try:
        all_posts = []
        query = f'"{film_title}" OR {film_title.replace(" ", "")}'

        for sub in SEARCH_SUBREDDITS:
            posts = _search_subreddit(token, sub, query, limit=10)
            all_posts.extend(posts)

        if not all_posts:
            result = _dummy_signal(f"{film_title}:{region}")
            _cache[cache_key] = result
            _cache_ts[cache_key] = now
            return result

        # Aggregate metrics
        mention_count = len(all_posts)
        total_comments = sum(p.get("data", {}).get("num_comments", 0) for p in all_posts)
        avg_comments = total_comments / max(1, mention_count)
        upvote_ratios = [p.get("data", {}).get("upvote_ratio", 0.5) for p in all_posts]
        avg_upvote = sum(upvote_ratios) / max(1, len(upvote_ratios))
        sentiment = _compute_sentiment_from_posts(all_posts)

        # Normalize components
        mention_norm = round(min(1.0, mention_count / 100), 4)
        depth_norm = round(min(1.0, avg_comments / 50), 4)
        upvote_norm = round(avg_upvote, 4)

        # Composite: RedditScore = mentions * depth * sentiment
        normalized = round(min(1.0,
            0.35 * mention_norm
            + 0.25 * depth_norm
            + 0.20 * upvote_norm
            + 0.20 * sentiment
        ), 4)

        result = {
            "mention_count": mention_count,
            "comment_depth": round(avg_comments, 1),
            "upvote_ratio": round(avg_upvote, 4),
            "sentiment": sentiment,
            "normalized_score": normalized,
            "source": "live",
        }
    except Exception:
        result = _dummy_signal(f"{film_title}:{region}")

    _cache[cache_key] = result
    _cache_ts[cache_key] = now
    return result


def fetch_reddit_signals_batch(
    film_title: str,
    regions: List[str],
) -> Dict[str, Dict]:
    """Fetch one global Reddit signal and distribute with region weights."""
    global_signal = fetch_reddit_signal(film_title, "global")

    region_weights = {
        "North America": 1.0, "Europe": 0.85, "East Asia": 0.6,
        "South Asia": 0.75, "Latin America": 0.5, "Middle East": 0.4, "Africa": 0.35,
    }
    results = {}
    for region in regions:
        w = region_weights.get(region, 0.5)
        results[region] = {
            **global_signal,
            "normalized_score": round(global_signal["normalized_score"] * w, 4),
        }
    return results

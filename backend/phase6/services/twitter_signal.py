"""
Twitter/X Signal Service — Fetches social buzz metrics.

Attempts to use snscrape for tweet scraping.
Falls back to deterministic dummy signals on any failure.

Returns normalized values (0–1).
"""

import os
import random
import hashlib
from typing import Dict, List, Optional

# ── Cache ──
_cache: Dict[str, Dict] = {}
_cache_ts: Dict[str, float] = {}
CACHE_TTL = 900  # 15 minutes


def _dummy_signal(seed: str) -> Dict:
    """Deterministic fallback using hash-based seeding."""
    h = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
    rng = random.Random(h)
    return {
        "tweet_volume": rng.randint(200, 5000),
        "sentiment": round(rng.uniform(0.35, 0.85), 4),
        "velocity": round(rng.uniform(0.05, 0.45), 4),
        "normalized_score": round(rng.uniform(0.4, 0.8), 4),
        "source": "fallback",
    }


def _try_scrape(query: str, max_tweets: int = 100) -> Optional[List[str]]:
    """Attempt snscrape. Returns None on failure."""
    try:
        import snscrape.modules.twitter as sntwitter
        tweets = []
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
            if i >= max_tweets:
                break
            tweets.append(tweet.rawContent)
        return tweets if tweets else None
    except Exception:
        return None


def _compute_sentiment(texts: List[str]) -> float:
    """Sentiment analysis using transformers, or simple heuristic."""
    try:
        from transformers import pipeline
        classifier = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment",
            top_k=None,
            truncation=True,
        )
        scores = []
        for text in texts[:50]:  # limit for speed
            result = classifier(text[:512])[0]
            label_scores = {r["label"]: r["score"] for r in result}
            # Map to 0-1 scale (negative=0, neutral=0.5, positive=1)
            score = (
                label_scores.get("LABEL_2", 0) * 1.0
                + label_scores.get("LABEL_1", 0) * 0.5
                + label_scores.get("LABEL_0", 0) * 0.0
            )
            scores.append(score)
        return round(sum(scores) / len(scores), 4) if scores else 0.5
    except Exception:
        # Simple keyword heuristic fallback
        positive_words = {"amazing", "great", "love", "best", "excited", "awesome", "hit", "blockbuster"}
        negative_words = {"bad", "worst", "flop", "terrible", "boring", "disappointing"}
        pos_count = sum(1 for t in texts for w in positive_words if w in t.lower())
        neg_count = sum(1 for t in texts for w in negative_words if w in t.lower())
        total = pos_count + neg_count
        return round(0.5 + (pos_count - neg_count) / max(1, total * 2), 4)


def fetch_twitter_signal(
    film_title: str,
    region: str = "global",
) -> Dict:
    """
    Fetch Twitter/X signal for a film in a given region.

    Returns: {tweet_volume, sentiment, velocity, normalized_score, source}
    """
    import time

    cache_key = f"twitter:{film_title}:{region}"
    now = time.time()

    # Check cache
    if cache_key in _cache and (now - _cache_ts.get(cache_key, 0)) < CACHE_TTL:
        return _cache[cache_key]

    try:
        query = f'"{film_title}" OR #{film_title.replace(" ", "")}'
        if region and region != "global":
            query += f" near:{region}"

        tweets = _try_scrape(query)

        if tweets and len(tweets) >= 5:
            tweet_volume = len(tweets)
            sentiment = _compute_sentiment(tweets)
            # Velocity: simple proxy — how many tweets are "recent"
            velocity = round(min(1.0, tweet_volume / 500), 4)
            normalized = round(
                0.4 * min(1.0, tweet_volume / 2000)
                + 0.35 * sentiment
                + 0.25 * velocity,
                4,
            )
            result = {
                "tweet_volume": tweet_volume,
                "sentiment": sentiment,
                "velocity": velocity,
                "normalized_score": normalized,
                "source": "live",
            }
        else:
            result = _dummy_signal(f"{film_title}:{region}")
    except Exception:
        result = _dummy_signal(f"{film_title}:{region}")

    _cache[cache_key] = result
    _cache_ts[cache_key] = now
    return result


def fetch_twitter_signals_batch(
    film_title: str,
    regions: List[str],
) -> Dict[str, Dict]:
    """Fetch Twitter signals for multiple regions."""
    return {region: fetch_twitter_signal(film_title, region) for region in regions}

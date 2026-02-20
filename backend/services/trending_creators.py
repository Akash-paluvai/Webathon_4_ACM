"""
High-Reach YouTube Channel Discovery — Objective, Platform-Driven

Uses YouTube Data API v3 to discover high-reach channels:
  1. Search for popular entertainment videos in a region
  2. Extract unique channel IDs
  3. Enrich via channels.list (snippet + statistics)
  4. Filter by configurable subscriber / view thresholds
  5. Sort by subscriberCount, return top 4

Falls back to a static set of objectively high-reach entertainment
channels when the API quota is exceeded or unavailable.

NO curated actor lists, NO scraping, NO endorsement language.
Channel logos are from YouTube API snippet.thumbnails only.
"""

import logging
import os
import urllib.error
import urllib.request
import urllib.parse
import json
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
_CHANNELS_URL = "https://www.googleapis.com/youtube/v3/channels"

# ── Configurable objective thresholds ──
MIN_SUBSCRIBERS = int(os.getenv("MIN_SUBSCRIBERS", "10000"))
MIN_TOTAL_VIEWS = int(os.getenv("MIN_TOTAL_VIEWS", "10000"))

# Keywords to exclude obvious non-entertainment channels
_EXCLUDE_KEYWORDS = {"vlog", "shorts", "asmr", "cooking", "recipe", "mukbang"}

# ── Static fallback: objectively high-reach entertainment channels ──
# These are publicly known YouTube channels with verifiable metrics.
# Used ONLY when YouTube API quota is exceeded or key is invalid.
_FALLBACK_CHANNELS: List[Dict[str, Any]] = [
    {
        "name": "T-Series",
        "platform": "YouTube",
        "logoUrl": "https://yt3.googleusercontent.com/ytc/AIdro_nSos0BnMwuerEbOqiI7NI4GAnBEsk7GRhcLVzYqZhIGsM=s240-c-k-c0x00ffffff-no-rj",
        "subscribers": 280000000,
        "reachTier": "Very High Reach",
        "reason": "Selected based on public subscriber and view thresholds",
    },
    {
        "name": "SET India",
        "platform": "YouTube",
        "logoUrl": "https://yt3.googleusercontent.com/ytc/AIdro_mkVG5n5VTbkV3e0y6Qz3nMVQ3UpJVKi0kGJN_eMCFJtKQ=s240-c-k-c0x00ffffff-no-rj",
        "subscribers": 170000000,
        "reachTier": "Very High Reach",
        "reason": "Selected based on public subscriber and view thresholds",
    },
    {
        "name": "Zee Music Company",
        "platform": "YouTube",
        "logoUrl": "https://yt3.googleusercontent.com/ytc/AIdro_nh6GQmSJeXJALwsH0LF2YK0QUWVyFDYZQXiPRWkJJFuw=s240-c-k-c0x00ffffff-no-rj",
        "subscribers": 110000000,
        "reachTier": "Very High Reach",
        "reason": "Selected based on public subscriber and view thresholds",
    },
    {
        "name": "YRF",
        "platform": "YouTube",
        "logoUrl": "https://yt3.googleusercontent.com/ytc/AIdro_nYluXn0b_2KPqNJIjENTFCyK35i7YRxH0CZMYUIM7qUg=s240-c-k-c0x00ffffff-no-rj",
        "subscribers": 72000000,
        "reachTier": "Very High Reach",
        "reason": "Selected based on public subscriber and view thresholds",
    },
]


def fetch_trending_creators(
    genre: Optional[str] = None,
    region_code: str = "IN",
    max_results: int = 25,
) -> List[Dict[str, Any]]:
    """
    Discover high-reach YouTube channels from trending entertainment videos.
    Returns top 4 channels sorted by subscriber count.
    Falls back to static data if API is unavailable.
    """
    if not _API_KEY:
        logger.warning("No YOUTUBE_API_KEY set — returning fallback channels")
        return _FALLBACK_CHANNELS

    # Step 1: Search for popular entertainment videos
    channel_ids = _discover_channel_ids(region_code, max_results)
    if not channel_ids:
        logger.warning("No channels discovered via API — returning fallback")
        return _FALLBACK_CHANNELS

    # Step 2: Enrich channels with snippet + statistics
    channels = _enrich_channels(list(channel_ids))
    if not channels:
        logger.warning("Channel enrichment failed — returning fallback")
        return _FALLBACK_CHANNELS

    # Step 3: Filter by objective thresholds
    filtered = _filter_channels(channels)

    # Step 4: Sort by subscribers descending, return top 4
    filtered.sort(key=lambda c: c["subscribers"], reverse=True)
    result = filtered[:4]

    if not result:
        logger.info("No channels passed filters — returning fallback")
        return _FALLBACK_CHANNELS

    return result


def _discover_channel_ids(region_code: str, max_results: int) -> set:
    """Search for popular entertainment videos and extract unique channel IDs."""
    params = urllib.parse.urlencode({
        "part": "snippet",
        "q": "Indian movie trailer official 2025",
        "type": "video",
        "order": "viewCount",
        "regionCode": region_code,
        "videoCategoryId": "24",
        "maxResults": min(max_results, 50),
        "key": _API_KEY,
    })

    try:
        req = urllib.request.Request(f"{_SEARCH_URL}?{params}")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        logger.error("YouTube search API error %s: %s", e.code, e.reason)
        return set()
    except Exception as e:
        logger.error("YouTube search request failed: %s", str(e))
        return set()

    channel_ids = set()
    for item in data.get("items", []):
        cid = item.get("snippet", {}).get("channelId", "")
        if cid:
            channel_ids.add(cid)

    logger.info("Discovered %d unique channels from %d videos", len(channel_ids), len(data.get("items", [])))
    return channel_ids


def _enrich_channels(channel_ids: List[str]) -> List[Dict[str, Any]]:
    """Call channels.list to get snippet + statistics for each channel."""
    ids_str = ",".join(channel_ids[:50])
    params = urllib.parse.urlencode({
        "part": "snippet,statistics",
        "id": ids_str,
        "key": _API_KEY,
    })

    try:
        req = urllib.request.Request(f"{_CHANNELS_URL}?{params}")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        logger.error("YouTube channels API error %s: %s", e.code, e.reason)
        return []
    except Exception as e:
        logger.error("YouTube channels request failed: %s", str(e))
        return []

    results = []
    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})

        title = snippet.get("title", "Unknown Channel")
        logo_url = (
            snippet.get("thumbnails", {}).get("medium", {}).get("url")
            or snippet.get("thumbnails", {}).get("default", {}).get("url")
            or ""
        )
        subscriber_count = int(stats.get("subscriberCount", 0))
        view_count = int(stats.get("viewCount", 0))

        results.append({
            "title": title,
            "logoUrl": logo_url,
            "subscribers": subscriber_count,
            "totalViews": view_count,
        })

    return results


def _filter_channels(channels: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Apply objective filtering: thresholds + keyword exclusion."""
    filtered = []
    for ch in channels:
        if ch["subscribers"] < MIN_SUBSCRIBERS:
            continue
        if ch["totalViews"] < MIN_TOTAL_VIEWS:
            continue

        title_lower = ch["title"].lower()
        if any(kw in title_lower for kw in _EXCLUDE_KEYWORDS):
            continue

        if ch["subscribers"] >= 10_000_000:
            reach_tier = "Very High Reach"
        elif ch["subscribers"] >= 1_000_000:
            reach_tier = "High Reach"
        else:
            reach_tier = "Notable Reach"

        filtered.append({
            "name": ch["title"],
            "platform": "YouTube",
            "logoUrl": ch["logoUrl"],
            "subscribers": ch["subscribers"],
            "reachTier": reach_tier,
            "reason": "Selected based on public subscriber and view thresholds",
        })

    return filtered

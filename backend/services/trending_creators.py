"""
Indian Film Actors Service — Curated List + YouTube Validation

Uses a STATIC curated list of Indian film actors.
For each actor, queries YouTube Search API to:
  - validate recent activity
  - fetch a public content thumbnail
  - compute an activity score based on views + recency

NO open-ended discovery, NO scraping, NO endorsement claims.
Thumbnails are from publicly available YouTube content only.
"""

import math
import os
import urllib.request
import urllib.parse
import json
from datetime import datetime, timezone
from typing import Any, Dict, List

_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"

# ── Curated list of Indian film actors ──
_ACTORS = [
    "Ranbir Kapoor",
    "Alia Bhatt",
    "Prabhas",
    "Allu Arjun",
    "Rajinikanth",
    "Amitabh Bachchan",
    "Shah Rukh Khan",
    "Deepika Padukone",
    "Ranveer Singh",
    "Vijay Thalapathy",
    "Ram Charan",
    "Jr NTR",
]


def fetch_trending_creators(
    genre: str = None,
    region_code: str = "IN",
    max_results: int = 20,
) -> List[Dict[str, Any]]:
    """
    For each curated Indian film actor, search YouTube for recent
    activity and return the top 3-4 by activity score.
    """
    if not _API_KEY:
        return []

    scored: List[Dict[str, Any]] = []

    for actor in _ACTORS:
        result = _search_actor(actor, region_code)
        if result:
            scored.append(result)

    # Sort by activity score, return top 4
    scored.sort(key=lambda x: x["activityScore"], reverse=True)
    return scored[:4]


def _search_actor(actor_name: str, region_code: str) -> Dict[str, Any] | None:
    """
    Search YouTube for a single actor's recent interview/trailer/official
    content. Returns actor info with thumbnail and activity score, or None.
    """
    query = f"{actor_name} interview OR official OR trailer"
    params = urllib.parse.urlencode({
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": "date",
        "regionCode": region_code,
        "maxResults": 1,
        "videoCategoryId": "24",
        "key": _API_KEY,
    })

    try:
        req = urllib.request.Request(f"{_SEARCH_URL}?{params}")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
    except Exception:
        return None

    items = data.get("items", [])
    if not items:
        return None

    item = items[0]
    snippet = item.get("snippet", {})
    video_id = item.get("id", {}).get("videoId", "")

    # Get thumbnail
    thumbnails = snippet.get("thumbnails", {})
    thumb_url = (
        thumbnails.get("medium", {}).get("url")
        or thumbnails.get("default", {}).get("url")
        or ""
    )

    # Parse publish date for recency
    publish_str = snippet.get("publishedAt", "")
    days_ago = _days_since(publish_str)

    # Fetch view count for this video
    view_count = _fetch_view_count(video_id) if video_id else 0

    # Compute activity score
    activity_score = _compute_activity_score(view_count, days_ago)

    return {
        "name": actor_name,
        "category": "Indian Film Actor",
        "platform": "YouTube",
        "thumbnailUrl": thumb_url,
        "activityScore": activity_score,
        "reason": "High-reach Indian film actor with active digital presence",
    }


def _fetch_view_count(video_id: str) -> int:
    """Fetch view count for a single video."""
    if not _API_KEY or not video_id:
        return 0

    params = urllib.parse.urlencode({
        "part": "statistics",
        "id": video_id,
        "key": _API_KEY,
    })

    try:
        req = urllib.request.Request(f"{_VIDEOS_URL}?{params}")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
    except Exception:
        return 0

    items = data.get("items", [])
    if not items:
        return 0

    return int(items[0].get("statistics", {}).get("viewCount", 0))


def _days_since(iso_date: str) -> int:
    """Calculate days since an ISO 8601 date string."""
    if not iso_date:
        return 999
    try:
        pub = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - pub
        return max(0, delta.days)
    except Exception:
        return 999


def _compute_activity_score(view_count: int, days_ago: int) -> int:
    """
    Activity score (0-100) based on:
      - log10(viewCount): 0-50 pts
      - recency bonus: 0-50 pts (higher = more recent)
    """
    # View score: log10 scaled
    if view_count > 0:
        view_score = min(50, max(0, (math.log10(view_count) - 3) * 10))
    else:
        view_score = 0

    # Recency: full points if < 7 days, decays over 90 days
    if days_ago <= 7:
        recency_score = 50
    elif days_ago <= 30:
        recency_score = 40
    elif days_ago <= 90:
        recency_score = 25
    elif days_ago <= 180:
        recency_score = 10
    else:
        recency_score = 5

    return max(0, min(100, round(view_score + recency_score)))

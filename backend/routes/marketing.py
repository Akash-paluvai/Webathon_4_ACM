"""
Marketing Routes — Trending Creators
GET /api/marketing/trending-creators

Returns trending YouTube creators with public content thumbnails.
"""

from fastapi import APIRouter, Query
from services.trending_creators import fetch_trending_creators

router = APIRouter(prefix="/api/marketing", tags=["Marketing"])


@router.get("/trending-creators")
def get_trending_creators(
    genre: str = Query(default="", description="Film genre for topic matching"),
    region: str = Query(default="IN", description="YouTube region code"),
):
    creators = fetch_trending_creators(
        genre=genre if genre else None,
        region_code=region,
        max_results=20,
    )
    return {"creators": creators}

"""
Phase 8 FastAPI sub-router.
Mounted at /api/phase8 — completely isolated from existing endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from phase8.config import TMDB_API_KEY, OMDB_API_KEY, YOUTUBE_API_KEY, REDDIT_CLIENT_ID
from phase8.schemas import HealthResponse, Phase8Report
from phase8.service import build_report
from phase8.kaggle_data import dataset_size, all_titles

phase8_router = APIRouter()


@phase8_router.get("/health", response_model=HealthResponse)
async def phase8_health():
    """Health-check for Phase 8 module and adapter readiness."""
    adapters = {
        "tmdb": "ready" if TMDB_API_KEY else "no_key",
        "omdb": "ready" if OMDB_API_KEY else "no_key",
        "youtube": "ready" if YOUTUBE_API_KEY else "no_key",
        "reddit": "ready" if REDDIT_CLIENT_ID else "no_key",
        "kaggle_dataset": "loaded",
    }
    return HealthResponse(
        status="ok",
        module="phase8",
        adapters=adapters,
        dataset_loaded=dataset_size(),
    )


@phase8_router.get("/titles")
async def get_available_titles():
    """Return all movie titles available in the Kaggle dataset."""
    titles = all_titles()
    return {"count": len(titles), "titles": titles}


@phase8_router.get("/report/{movie_title}", response_model=Phase8Report)
async def get_report(movie_title: str):
    """
    Generate a Phase 8 report with hybrid revenue:
    Kaggle → TMDb → Reddit fallback.
    Any movie can be queried — no dataset restriction.
    """
    title = movie_title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Movie title cannot be empty")
    try:
        report = await build_report(title)
        return report
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(exc)}",
        )

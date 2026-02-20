"""
Competition Engine — Live competition intelligence.

Upgrades the existing competition_density.py with:
  - Monthly CDI breakdown
  - Competitor timeline
  - Competition by genre/language
  - Risk by timing
  - TMDB upcoming releases (live, with fallback)
"""

import os
import time
import hashlib
import random
from typing import Dict, List, Optional
from datetime import datetime, date

from sqlalchemy.orm import Session

# ── Cache ──
_tmdb_cache: Dict[str, List] = {}
_tmdb_cache_ts: Dict[str, float] = {}
CACHE_TTL = 900


def _fetch_tmdb_upcoming(api_key: str) -> List[Dict]:
    """Fetch upcoming movies from TMDB."""
    try:
        import httpx
        results = []
        for page in [1, 2]:
            resp = httpx.get(
                "https://api.themoviedb.org/3/movie/upcoming",
                params={"api_key": api_key, "page": page, "region": "US"},
                timeout=10,
            )
            if resp.status_code == 200:
                results.extend(resp.json().get("results", []))
        return results
    except Exception:
        return []


def _get_db_competitors(db: Optional[Session], genre: str, language: str) -> List[Dict]:
    """Get competitors from DB."""
    try:
        from phase6_models import CompetitionRelease
        if db is None:
            return []
        query = db.query(CompetitionRelease)
        competitors = query.all()
        return [
            {
                "title": c.title,
                "genre": c.genre,
                "language": c.language,
                "release_month": c.release_month,
                "budget_tier": c.budget_tier,
                "star_power": c.star_power,
                "platform": c.platform,
            }
            for c in competitors
        ]
    except Exception:
        return []


def _dummy_competitors(genre: str, language: str) -> List[Dict]:
    """Generate deterministic fallback competitors."""
    h = int(hashlib.sha256(f"{genre}:{language}".encode()).hexdigest(), 16)
    rng = random.Random(h)
    titles = [
        f"{genre} Rising", f"The {genre} Legend", f"{language.title()} Thunder",
        f"Project {genre[0]}", f"Untitled {genre} Film", f"The Final {genre}",
        f"Code {rng.randint(100,999)}", f"Operation {genre}",
    ]
    competitors = []
    for i, title in enumerate(titles[:rng.randint(5, 8)]):
        competitors.append({
            "title": title,
            "genre": genre if rng.random() > 0.3 else rng.choice(["Action", "Drama", "Comedy", "Thriller"]),
            "language": language if rng.random() > 0.4 else "English",
            "release_month": rng.randint(1, 12),
            "budget_tier": rng.choice(["low", "medium", "high"]),
            "star_power": round(rng.uniform(0.2, 0.9), 2),
            "platform": rng.choice(["Theatrical", "Netflix", "Amazon Prime", "Hotstar"]),
        })
    return competitors


def compute_competition_intel(
    genre: str,
    language: str,
    budget_level: str = "medium",
    db: Optional[Session] = None,
) -> Dict:
    """
    Comprehensive competition intelligence.

    Returns:
        {
            cdi, genre_density, language_density, budget_crowd,
            total_competitors, competitors,
            competition_by_month, risk_by_month,
            competition_heatmap, safest_months
        }
    """
    # Fetch competitors from multiple sources
    competitors = _get_db_competitors(db, genre, language)

    # Try TMDB live
    api_key = os.environ.get("TMDB_API_KEY", "").strip()
    if api_key:
        cache_key = "tmdb_upcoming"
        now = time.time()
        if cache_key in _tmdb_cache and (now - _tmdb_cache_ts.get(cache_key, 0)) < CACHE_TTL:
            tmdb_movies = _tmdb_cache[cache_key]
        else:
            tmdb_movies = _fetch_tmdb_upcoming(api_key)
            _tmdb_cache[cache_key] = tmdb_movies
            _tmdb_cache_ts[cache_key] = now

        # Map TMDB genre IDs
        genre_ids = {28: "Action", 18: "Drama", 35: "Comedy", 27: "Horror",
                     53: "Thriller", 10749: "Romance", 878: "Sci-Fi",
                     99: "Documentary", 16: "Animation"}
        for movie in tmdb_movies:
            movie_genres = [genre_ids.get(gid, "") for gid in movie.get("genre_ids", [])]
            release_date = movie.get("release_date", "")
            month = int(release_date.split("-")[1]) if release_date and len(release_date) >= 7 else 6
            competitors.append({
                "title": movie.get("title", "Unknown"),
                "genre": movie_genres[0] if movie_genres else "Unknown",
                "language": movie.get("original_language", "en").title(),
                "release_month": month,
                "budget_tier": "high" if movie.get("popularity", 0) > 50 else "medium",
                "star_power": round(min(1.0, movie.get("popularity", 0) / 100), 2),
                "platform": "Theatrical",
            })

    # Fallback if no data
    if not competitors:
        competitors = _dummy_competitors(genre, language)

    # ── Compute CDI ──────────────────────────────────────────
    same_genre = [c for c in competitors if c["genre"].lower() == genre.lower()]
    same_language = [c for c in competitors if c["language"].lower() == language.lower()]
    high_budget = [c for c in competitors if c["budget_tier"] == "high"]

    genre_density = round(min(1.0, len(same_genre) / max(1, len(competitors))), 4)
    language_density = round(min(1.0, len(same_language) / max(1, len(competitors))), 4)
    budget_crowd = round(min(1.0, len(high_budget) / max(1, len(competitors))), 4)

    cdi = round(
        0.40 * genre_density
        + 0.30 * language_density
        + 0.30 * budget_crowd,
        4,
    )

    # ── Competition by Month ─────────────────────────────────
    competition_by_month: Dict[int, float] = {}
    competition_heatmap: List[Dict] = []

    for month in range(1, 13):
        month_comps = [c for c in competitors if c.get("release_month") == month]
        monthly_density = min(1.0, len(month_comps) / max(1, 5))  # 5+ competitors = max density
        avg_star = sum(c.get("star_power", 0.5) for c in month_comps) / max(1, len(month_comps)) if month_comps else 0
        month_cdi = round(0.6 * monthly_density + 0.4 * avg_star, 4)
        competition_by_month[month] = month_cdi

        from phase6.services.calendar_engine import MONTH_NAMES
        competition_heatmap.append({
            "month": month,
            "month_name": MONTH_NAMES[month],
            "density": round(monthly_density, 4),
            "avg_star_power": round(avg_star, 4),
            "cdi": month_cdi,
            "competitor_count": len(month_comps),
            "competitors": [c["title"] for c in month_comps[:5]],
        })

    # ── Risk by Month ────────────────────────────────────────
    risk_by_month = []
    for hm in competition_heatmap:
        risk = "low" if hm["cdi"] < 0.3 else "moderate" if hm["cdi"] < 0.6 else "high"
        risk_by_month.append({
            "month": hm["month"],
            "month_name": hm["month_name"],
            "risk": risk,
            "cdi": hm["cdi"],
        })

    # Safest months (lowest CDI)
    safest = sorted(competition_heatmap, key=lambda x: x["cdi"])[:3]
    safest_months = [s["month_name"] for s in safest]

    return {
        "cdi": cdi,
        "genre_density": genre_density,
        "language_density": language_density,
        "budget_crowd": budget_crowd,
        "total_competitors": len(competitors),
        "same_genre_count": len(same_genre),
        "competitors": [
            {"title": c["title"], "genre": c["genre"], "month": c.get("release_month"),
             "star_power": c.get("star_power", 0), "platform": c.get("platform", "")}
            for c in competitors[:15]
        ],
        "competition_by_month": competition_by_month,
        "competition_heatmap": competition_heatmap,
        "risk_by_month": risk_by_month,
        "safest_months": safest_months,
    }

"""
Competition Density Index (CDI) — measures competitive pressure in the release window.

Uses CompetitionRelease table data + heuristic fallback.
CDI penalizes platform fit when the market is crowded.
"""

from typing import Dict, Optional
from sqlalchemy.orm import Session


# ── Heuristic competition data (fallback when DB is empty) ───
GENRE_COMPETITION: Dict[str, float] = {
    "Action": 0.75,     # very crowded
    "Thriller": 0.55,
    "Drama": 0.50,
    "Comedy": 0.45,
    "Horror": 0.40,
    "Romance": 0.35,
    "Sci-Fi": 0.55,
    "Documentary": 0.20,
    "Animation": 0.45,
}

LANGUAGE_COMPETITION: Dict[str, float] = {
    "english": 0.80,
    "hindi": 0.60,
    "korean": 0.45,
    "spanish": 0.40,
    "telugu": 0.35,
    "tamil": 0.35,
}

BUDGET_CROWD: Dict[str, float] = {
    "low": 0.3,
    "medium": 0.5,
    "high": 0.8,
}


def compute_cdi(
    genre: str,
    language: str,
    budget_level: str,
    release_quarter: str = "2026-Q1",
    db: Optional[Session] = None,
) -> Dict:
    """
    Compute Competition Density Index.

    CDI = 0.40 * genre_density + 0.30 * language_density + 0.30 * budget_crowd_factor

    Returns:
        {cdi, genre_density, language_density, budget_crowd, same_genre_count, total_competitors}
    """
    same_genre_count = 0
    same_lang_count = 0
    big_budget_count = 0
    total_competitors = 0

    # Try DB first
    if db is not None:
        try:
            from phase6_models import CompetitionRelease
            competitors = (
                db.query(CompetitionRelease)
                .filter(CompetitionRelease.release_quarter == release_quarter)
                .all()
            )
            total_competitors = len(competitors)
            same_genre_count = sum(1 for c in competitors if c.genre.lower() == genre.lower())
            same_lang_count = sum(1 for c in competitors if c.language.lower() == language.lower())
            big_budget_count = sum(1 for c in competitors if c.budget_level == "high")
        except Exception:
            pass

    # Compute densities
    if total_competitors > 0:
        genre_density = min(1.0, same_genre_count / max(1, total_competitors) * 2.5)
        language_density = min(1.0, same_lang_count / max(1, total_competitors) * 2.5)
        budget_crowd = min(1.0, big_budget_count / max(1, total_competitors) * 2.0)
    else:
        # Heuristic fallback
        genre_density = GENRE_COMPETITION.get(genre, 0.4)
        language_density = LANGUAGE_COMPETITION.get(language.lower(), 0.4)
        budget_crowd = BUDGET_CROWD.get(budget_level, 0.5)

    cdi = round(0.40 * genre_density + 0.30 * language_density + 0.30 * budget_crowd, 4)

    return {
        "cdi": cdi,
        "genre_density": round(genre_density, 4),
        "language_density": round(language_density, 4),
        "budget_crowd": round(budget_crowd, 4),
        "same_genre_count": same_genre_count,
        "total_competitors": total_competitors,
    }


def cdi_penalty(cdi: float) -> float:
    """Convert CDI to a penalty multiplier (higher CDI = lower fit)."""
    return round(max(0.0, 1.0 - cdi * 0.4), 4)

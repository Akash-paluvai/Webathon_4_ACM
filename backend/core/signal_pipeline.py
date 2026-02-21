"""
Signal Pipeline — Background ingestion loop for live audience signals.

Runs every CYCLE_INTERVAL seconds:
  1. Loads all active film projects from DB
  2. For each project: fetches signals from all sources
  3. Writes SignalTimeseries row (append-only history)
  4. Upserts SignalCache row (latest values for fast reads)
  5. Computes momentum/velocity from previous vs current

Never crashes. Every source call is wrapped in try/except.
"""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

logger = logging.getLogger("signal_pipeline")
logger.setLevel(logging.INFO)

CYCLE_INTERVAL = 600  # 10 minutes
INITIAL_DELAY = 5     # seconds before first run


def _fetch_all_signals(film_title: str, genre: str, language: str,
                       scale: str, talent_strategy: str, budget_level: str,
                       audience_type: str, release_model: str, regions: List[str]) -> Dict[str, Dict]:
    """
    Fetch signals from all sources for a film across regions.
    Each source is independently wrapped — failures don't cascade.
    """
    from phase6.services.youtube_signal import fetch_youtube_signals_batch
    from phase6.services.twitter_signal import fetch_twitter_signals_batch
    from phase6.services.trends_signal import fetch_trends_signals_batch
    from phase6.services.popularity_signal import fetch_popularity_signals_batch
    from phase6.services.reddit_signal import fetch_reddit_signals_batch
    from phase7.services.piracy_signal import compute_piracy_signal

    results = {}

    for region in regions:
        results[region] = {
            "twitter": 0.0, "reddit": 0.0, "youtube": 0.0,
            "trends": 0.0, "tmdb": 0.0, "sentiment": 0.5,
            "piracy": 0.0, "source": "fallback",
        }

    # YouTube
    try:
        yt = fetch_youtube_signals_batch(film_title, regions)
        for region in regions:
            if region in yt:
                results[region]["youtube"] = yt[region].get("normalized_score", 0.0)
                if yt[region].get("source") == "live":
                    results[region]["source"] = "live"
    except Exception as e:
        logger.warning(f"YouTube fetch failed for '{film_title}': {e}")

    # Twitter
    try:
        tw = fetch_twitter_signals_batch(film_title, regions)
        for region in regions:
            if region in tw:
                results[region]["twitter"] = tw[region].get("normalized_score", 0.0)
                results[region]["sentiment"] = tw[region].get("sentiment", 0.5)
                if tw[region].get("source") == "live":
                    results[region]["source"] = "live"
    except Exception as e:
        logger.warning(f"Twitter fetch failed for '{film_title}': {e}")

    # Reddit
    try:
        rd = fetch_reddit_signals_batch(film_title, regions)
        for region in regions:
            if region in rd:
                results[region]["reddit"] = rd[region].get("normalized_score", 0.0)
                # Blend Reddit sentiment with Twitter sentiment
                rd_sentiment = rd[region].get("sentiment", 0.5)
                tw_sentiment = results[region]["sentiment"]
                results[region]["sentiment"] = round(tw_sentiment * 0.6 + rd_sentiment * 0.4, 4)
                if rd[region].get("source") == "live":
                    results[region]["source"] = "live"
    except Exception as e:
        logger.warning(f"Reddit fetch failed for '{film_title}': {e}")

    # Google Trends
    try:
        tr = fetch_trends_signals_batch(film_title, regions)
        for region in regions:
            if region in tr:
                results[region]["trends"] = tr[region].get("normalized_score", 0.0)
                if tr[region].get("source") == "live":
                    results[region]["source"] = "live"
    except Exception as e:
        logger.warning(f"Trends fetch failed for '{film_title}': {e}")

    # TMDB
    try:
        pop = fetch_popularity_signals_batch(film_title, genre, regions)
        for region in regions:
            if region in pop:
                results[region]["tmdb"] = pop[region].get("normalized_score", 0.0)
                if pop[region].get("source") == "live":
                    results[region]["source"] = "live"
    except Exception as e:
        logger.warning(f"TMDB fetch failed for '{film_title}': {e}")

    # Piracy signal (heuristic, per-film not per-region)
    try:
        piracy_intel = {
            "genre": genre, "language": language, "scale": scale,
            "release_mode": release_model, "hype_momentum": 0.5,
        }
        piracy = compute_piracy_signal(piracy_intel)
        for region in regions:
            results[region]["piracy"] = piracy.get("demand_signal", 0.0)
    except Exception as e:
        logger.warning(f"Piracy signal failed for '{film_title}': {e}")

    return results


def _compute_composite(signals: Dict) -> float:
    """Compute composite RIS from individual signals."""
    return round(min(1.0,
        0.25 * signals.get("twitter", 0)
        + 0.15 * signals.get("reddit", 0)
        + 0.20 * signals.get("youtube", 0)
        + 0.15 * signals.get("trends", 0)
        + 0.10 * signals.get("tmdb", 0)
        + 0.10 * signals.get("sentiment", 0.5)
        + 0.05 * signals.get("piracy", 0)
    ), 4)


def _run_cycle(db: Session):
    """Execute one full pipeline cycle for all active projects."""
    from models import FilmProject
    from signal_models import SignalTimeseries, SignalCache

    regions = ["North America", "Europe", "South Asia", "East Asia",
               "Latin America", "Middle East", "Africa"]

    projects = db.query(FilmProject).all()
    if not projects:
        logger.info("No projects found — skipping cycle")
        return

    now = datetime.now(timezone.utc)
    cycle_count = 0

    for project in projects:
        try:
            signals_by_region = _fetch_all_signals(
                film_title=project.title,
                genre=project.genre or "Drama",
                language=project.language or "english",
                scale=project.scale or "medium",
                talent_strategy=project.talent_strategy or "emerging",
                budget_level=project.budget_level or "medium",
                audience_type=project.audience_type or "broad",
                release_model=project.release_model or "ott",
                regions=regions,
            )

            for region, signals in signals_by_region.items():
                composite = _compute_composite(signals)

                # ── Write time-series row (append-only) ──
                ts_row = SignalTimeseries(
                    film_id=project.id,
                    timestamp=now,
                    region=region,
                    twitter_score=signals["twitter"],
                    reddit_score=signals["reddit"],
                    youtube_score=signals["youtube"],
                    trend_score=signals["trends"],
                    tmdb_score=signals["tmdb"],
                    sentiment=signals["sentiment"],
                    piracy_score=signals["piracy"],
                    composite_ris=composite,
                )
                db.add(ts_row)

                # ── Upsert signal cache ──
                existing = db.query(SignalCache).filter_by(
                    film_id=project.id, region=region
                ).first()

                if existing:
                    # Compute momentum & velocity
                    prev_ris = existing.composite_ris or 0.0
                    momentum = round(composite - prev_ris, 4)
                    velocity = round(momentum / max(0.01, prev_ris), 4) if prev_ris > 0 else 0.0

                    existing.twitter = signals["twitter"]
                    existing.reddit = signals["reddit"]
                    existing.youtube = signals["youtube"]
                    existing.trends = signals["trends"]
                    existing.tmdb = signals["tmdb"]
                    existing.sentiment = signals["sentiment"]
                    existing.piracy = signals["piracy"]
                    existing.composite_ris = composite
                    existing.momentum = momentum
                    existing.velocity = velocity
                    existing.source = signals["source"]
                    existing.updated_at = now
                else:
                    cache_row = SignalCache(
                        film_id=project.id,
                        region=region,
                        twitter=signals["twitter"],
                        reddit=signals["reddit"],
                        youtube=signals["youtube"],
                        trends=signals["trends"],
                        tmdb=signals["tmdb"],
                        sentiment=signals["sentiment"],
                        piracy=signals["piracy"],
                        composite_ris=composite,
                        momentum=0.0,
                        velocity=0.0,
                        source=signals["source"],
                        updated_at=now,
                    )
                    db.add(cache_row)

            cycle_count += 1
        except Exception as e:
            logger.error(f"Pipeline failed for project {project.id} ({project.title}): {e}")
            continue

    try:
        db.commit()
        logger.info(f"✅ Pipeline cycle complete: {cycle_count} projects, {now.isoformat()}")
    except Exception as e:
        db.rollback()
        logger.error(f"DB commit failed: {e}")


async def run_signal_pipeline():
    """
    Async background loop. Runs _run_cycle every CYCLE_INTERVAL seconds.
    Never exits, never crashes.
    """
    await asyncio.sleep(INITIAL_DELAY)
    logger.info(f"🚀 Signal pipeline started (interval={CYCLE_INTERVAL}s)")

    while True:
        try:
            from database import SessionLocal
            db = SessionLocal()
            try:
                _run_cycle(db)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Pipeline loop error: {e}")

        await asyncio.sleep(CYCLE_INTERVAL)

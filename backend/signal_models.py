"""
Signal Models — Time-series & cache tables for the dynamic signal pipeline.

SignalTimeseries: append-only rows capturing each ingestion cycle.
SignalCache: latest composite signal per film/region for fast endpoint reads.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, Float, String, DateTime, Index, UniqueConstraint,
)
from database import Base


class SignalTimeseries(Base):
    """
    Immutable time-series rows — one per film × region × ingestion cycle.
    Never overwrite: enables momentum, velocity, and trend analysis.
    """
    __tablename__ = "signal_timeseries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    film_id = Column(Integer, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False,
                       default=lambda: datetime.now(timezone.utc))
    region = Column(String(60), nullable=False, default="global")

    # ── Per-source normalized scores (0–1) ──
    twitter_score = Column(Float, nullable=False, default=0.0)
    reddit_score = Column(Float, nullable=False, default=0.0)
    youtube_score = Column(Float, nullable=False, default=0.0)
    trend_score = Column(Float, nullable=False, default=0.0)
    tmdb_score = Column(Float, nullable=False, default=0.0)
    sentiment = Column(Float, nullable=False, default=0.5)
    piracy_score = Column(Float, nullable=False, default=0.0)

    # ── Composite ──
    composite_ris = Column(Float, nullable=False, default=0.0)

    __table_args__ = (
        Index("ix_signal_ts_film_time", "film_id", "timestamp"),
    )


class SignalCache(Base):
    """
    Latest processed composite signals per film × region.
    Overwritten each pipeline cycle. User endpoints read ONLY from here.
    """
    __tablename__ = "signal_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    film_id = Column(Integer, nullable=False, index=True)
    region = Column(String(60), nullable=False, default="global")
    updated_at = Column(DateTime(timezone=True), nullable=False,
                        default=lambda: datetime.now(timezone.utc))

    # ── Latest scores ──
    twitter = Column(Float, nullable=False, default=0.0)
    reddit = Column(Float, nullable=False, default=0.0)
    youtube = Column(Float, nullable=False, default=0.0)
    trends = Column(Float, nullable=False, default=0.0)
    tmdb = Column(Float, nullable=False, default=0.0)
    sentiment = Column(Float, nullable=False, default=0.5)
    piracy = Column(Float, nullable=False, default=0.0)
    composite_ris = Column(Float, nullable=False, default=0.0)

    # ── Momentum & velocity (current − previous) ──
    momentum = Column(Float, nullable=False, default=0.0)
    velocity = Column(Float, nullable=False, default=0.0)

    # ── Source tracking ──
    source = Column(String(20), nullable=False, default="heuristic")

    __table_args__ = (
        UniqueConstraint("film_id", "region", name="uq_signal_cache_film_region"),
    )

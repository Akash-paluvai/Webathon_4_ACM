"""
Phase 6 Data Models — Historical films, deal benchmarks, competition releases.
Additive only — does NOT modify existing models.py.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from database import Base


class HistoricalFilm(Base):
    """Historical film performance data for benchmarking and ML training."""
    __tablename__ = "historical_films"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    genre = Column(String(50), nullable=False)
    language = Column(String(50), nullable=False)
    cast_tier = Column(String(20), nullable=False)  # unknown, emerging, established, starDriven
    budget_usd = Column(Float, nullable=False)  # in millions
    budget_level = Column(String(20), nullable=False)  # low, medium, high
    revenue_usd = Column(Float, nullable=False)  # in millions
    roi = Column(Float, nullable=False)
    release_mode = Column(String(20), nullable=False)  # theatre, ott, hybrid
    ott_revenue_pct = Column(Float, nullable=True)  # % of revenue from OTT
    theatre_revenue_pct = Column(Float, nullable=True)
    # Regional revenue distribution (top regions by %)
    region_north_america_pct = Column(Float, default=0)
    region_europe_pct = Column(Float, default=0)
    region_south_asia_pct = Column(Float, default=0)
    region_east_asia_pct = Column(Float, default=0)
    region_latin_america_pct = Column(Float, default=0)
    region_middle_east_pct = Column(Float, default=0)
    region_africa_pct = Column(Float, default=0)
    was_dubbed = Column(Integer, default=0)  # 0 or 1
    dubbed_revenue_uplift_pct = Column(Float, default=0)
    year = Column(Integer, nullable=False)


class DealBenchmark(Base):
    """Industry deal benchmarks by platform and genre."""
    __tablename__ = "deal_benchmarks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    platform_name = Column(String(50), nullable=False, index=True)
    genre = Column(String(50), nullable=False, index=True)
    avg_advance_pct = Column(Float, nullable=False)  # % of budget as advance
    avg_rev_share = Column(Float, nullable=False)  # platform rev share %
    min_guarantee_usd_k = Column(Float, nullable=False)  # minimum guarantee $K
    exclusive_window_days = Column(Integer, nullable=False)
    sample_count = Column(Integer, nullable=False)


class CompetitionRelease(Base):
    """Upcoming/recent releases for competition density computation."""
    __tablename__ = "competition_releases"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    genre = Column(String(50), nullable=False)
    language = Column(String(50), nullable=False)
    budget_level = Column(String(20), nullable=False)
    release_mode = Column(String(20), nullable=False)
    release_quarter = Column(String(10), nullable=False)  # e.g. "2026-Q1"
    star_power = Column(Float, default=0.5)  # 0-1

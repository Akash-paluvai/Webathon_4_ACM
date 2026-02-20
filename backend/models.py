from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base


class FilmProject(Base):
    __tablename__ = "film_projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    current_phase = Column(Integer, nullable=False, default=1)
    genre = Column(String(100), nullable=False)
    language = Column(String(100), nullable=False)
    theme = Column(String(200), nullable=False)
    scale = Column(String(20), nullable=False)  # indie, studio, blockbuster
    budget_level = Column(String(20), nullable=False)  # low, medium, high
    talent_strategy = Column(String(20), nullable=False)  # unknown, emerging, established, starDriven
    planned_shoot_days = Column(Integer, nullable=False)
    actual_shoot_days = Column(Integer, nullable=True)
    production_health = Column(String(20), nullable=False, default="good")  # good, atRisk, critical
    audience_type = Column(String(20), nullable=False)  # niche, broad, mainstream
    marketing_budget_level = Column(String(20), nullable=False, default="unassigned")  # low, medium, high, unassigned
    primary_marketing_channel = Column(String(20), nullable=False, default="undefined")  # influencer, festival, digitalAds, pr, undefined
    release_model = Column(String(20), nullable=False)  # theatre, ott, hybrid
    distribution_confidence = Column(String(20), nullable=False)  # low, medium, high
    last_updated = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    insights = relationship("Insight", back_populates="project", cascade="all, delete-orphan", order_by="Insight.timestamp")


class Insight(Base):
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("film_projects.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    project = relationship("FilmProject", back_populates="insights")

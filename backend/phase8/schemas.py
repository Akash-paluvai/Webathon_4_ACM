"""
Phase 8 Pydantic schemas — response envelope with source-type tagging.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class DataSourceResult(BaseModel):
    """Single tagged data point with provenance metadata."""
    value: Any
    source_type: str = Field(
        ..., description="One of: actual, estimated, fallback"
    )
    source_name: str = Field(
        ..., description="e.g. tmdb, omdb, youtube, estimation_engine"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="0.0–1.0 confidence in accuracy"
    )
    methodology: Optional[str] = Field(
        None, description="Explanation string for estimated values"
    )


class ComparableFilm(BaseModel):
    """A comparable film used for benchmarking."""
    title: str
    tmdb_id: int
    year: int
    genre: str
    budget: int
    revenue: int
    lifetime_multiplier: Optional[float] = None


class MovieIdentity(BaseModel):
    """Basic identity of the queried movie."""
    title: str
    tmdb_id: int
    release_date: Optional[str] = None
    genre: Optional[str] = None
    budget: Optional[int] = None
    revenue: Optional[int] = None


class DiagnosticOutput(BaseModel):
    """Diagnostic info showing what data was used."""
    kaggle_row: Optional[dict] = Field(
        None, description="The Kaggle dataset row used for this movie"
    )
    comparables_count: int = Field(
        0, description="Number of comparable films selected"
    )
    computed_multiplier: Optional[float] = Field(
        None, description="Revenue / budget multiplier"
    )
    avg_comparable_multiplier: Optional[float] = Field(
        None, description="Average multiplier from comparable films"
    )
    dataset_size: int = Field(0, description="Total records in Kaggle dataset")


class PerformanceInsights(BaseModel):
    """Dynamic percentile-based insights computed from dataset."""
    revenue_percentile_in_genre: int = 50
    budget_percentile_in_year: int = 50
    multiplier_percentile_overall: int = 50
    revenue_classification: str = "Average Performer"
    multiplier_classification: str = "Average Performer"
    genre_peer_count: int = 0
    year_peer_count: int = 0
    dataset_total: int = 0


class Phase8Report(BaseModel):
    """Full Phase 8 report envelope."""
    movie: MovieIdentity
    generated_at: datetime
    sections: dict[str, DataSourceResult]
    comparables_used: list[ComparableFilm] = Field(default_factory=list)
    diagnostics: Optional[DiagnosticOutput] = None
    insights: Optional[PerformanceInsights] = None


class HealthResponse(BaseModel):
    """Health-check response."""
    status: str
    module: str
    adapters: dict[str, str]
    dataset_loaded: int = 0

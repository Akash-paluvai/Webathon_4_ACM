"""
Phase 6 — Distribution Strategy & Negotiation
Isolated Pydantic response schemas.  Does NOT modify existing schemas.py.
"""

from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


# ── Signal Data (Layer 1) ────────────────────────────────────

class SignalData(BaseModel):
    region: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    youtube: float = Field(..., ge=0, le=1)
    twitter: float = Field(..., ge=0, le=1)
    trends: float = Field(..., ge=0, le=1)
    imdb: float = Field(..., ge=0, le=1)
    spotify: float = Field(..., ge=0, le=1)
    sentiment: float = Field(..., ge=0, le=1)
    RIS: float = Field(..., ge=0, le=1, description="Regional Interest Score")
    engagement_velocity: float = Field(..., ge=0, le=1)
    trend_direction: Optional[str] = Field(None, description="up | down")
    source: Optional[str] = Field(None, description="live | heuristic | fallback")


# ── Platform Fit ──────────────────────────────────────────────

class PlatformScore(BaseModel):
    platform: str
    fit_score: float = Field(..., ge=0, le=1, description="0-1 fit score")
    confidence: Tuple[float, float] = Field(..., description="(lower, upper) 95% CI")
    reasoning: List[str] = Field(default_factory=list)


class PlatformFitResponse(BaseModel):
    project_id: int
    rankings: List[PlatformScore]
    recommended_platform: str
    recommended_score: float
    distribution_model: str = Field(
        ..., description="theatre | ott | hybrid | festival"
    )


# ── Regional Hype ────────────────────────────────────────────

class RegionScore(BaseModel):
    region: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    interest_score: float = Field(..., ge=0, le=1)
    normalized_score: float = Field(..., ge=0, le=1)
    tier: str = Field(..., description="very_high | high | medium | low | very_low")
    youtube: Optional[float] = None
    twitter: Optional[float] = None
    trends: Optional[float] = None
    imdb: Optional[float] = None
    spotify: Optional[float] = None
    sentiment: Optional[float] = None
    engagement_velocity: Optional[float] = None
    trend_direction: Optional[str] = None
    source: Optional[str] = None


class RegionalHypeResponse(BaseModel):
    project_id: int
    regions: List[RegionScore]
    signals: Optional[List[SignalData]] = None
    top_region: str
    hype_summary: str


# ── Dubbing ──────────────────────────────────────────────────

class DubbingRecommendation(BaseModel):
    target_language: str
    priority: str = Field(..., description="high | medium | low")
    estimated_roi_uplift: float = Field(
        ..., description="Estimated percentage revenue uplift from dubbing"
    )
    rationale: str


class DubbingResponse(BaseModel):
    project_id: int
    needs_dubbing: bool
    recommendations: List[DubbingRecommendation]
    estimated_total_cost_tier: str = Field(
        ..., description="low | medium | high"
    )


# ── Leverage (Layer 3) ───────────────────────────────────────

class LeverageBreakdown(BaseModel):
    platform_fit_contribution: float
    hype_momentum_contribution: float
    regional_dominance_contribution: float
    dubbing_expansion_contribution: float


class LeverageResponse(BaseModel):
    leverage_score: float = Field(..., ge=0, le=1)
    level: str = Field(..., description="VERY_HIGH | HIGH | MODERATE | LOW | VERY_LOW")
    strategy_hint: str
    breakdown: LeverageBreakdown


# ── Deal Terms ───────────────────────────────────────────────

class DealTerms(BaseModel):
    platform: str
    minimum_guarantee_range: Tuple[float, float] = Field(
        ..., description="(low, high) in USD thousands"
    )
    revenue_share_pct: float = Field(..., ge=0, le=100)
    exclusivity_window_months: int
    recommended_strategy: str


class DealResponse(BaseModel):
    project_id: int
    negotiation_leverage: str = Field(
        ..., description="strong | moderate | weak"
    )
    leverage_score: float = Field(..., ge=0, le=1)
    leverage_detail: Optional[LeverageResponse] = None
    deal_options: List[DealTerms]
    benchmarks: Optional[List[Dict]] = None


# ── Full Phase 6 Analysis ────────────────────────────────────

class Phase6AnalysisResponse(BaseModel):
    project_id: int
    platform_fit: PlatformFitResponse
    regional_hype: RegionalHypeResponse
    dubbing: DubbingResponse
    deal: DealResponse
    leverage: Optional[LeverageResponse] = None
    release_mode: str = Field(
        ..., description="theatre | ott | hybrid | festival_circuit"
    )
    release_probabilities: Optional[Dict[str, float]] = None
    competition: Optional[Dict] = None
    overall_readiness_score: float = Field(..., ge=0, le=1)
    summary: str


from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# --- Enums as string literals (matching frontend) ---

class FilmProjectCreate(BaseModel):
    title: str = Field(..., max_length=100)
    genre: str
    language: str
    theme: str
    scale: str  # indie, studio, blockbuster
    budget_level: str = Field(..., alias="budgetLevel")
    talent_strategy: str = Field(..., alias="talentStrategy")
    planned_shoot_days: int = Field(..., alias="plannedShootDays")
    audience_type: str = Field(..., alias="audienceType")
    marketing_budget_level: str = Field(..., alias="marketingBudgetLevel")
    primary_marketing_channel: str = Field(..., alias="primaryMarketingChannel")
    release_model: str = Field(..., alias="releaseModel")
    distribution_confidence: str = Field(..., alias="distributionConfidence")

    model_config = {"populate_by_name": True}


class FilmProjectUpdate(BaseModel):
    title: str = Field(..., max_length=100)
    phase: int
    genre: str
    language: str
    theme: str
    scale: str
    budget_level: str = Field(..., alias="budgetLevel")
    talent_strategy: str = Field(..., alias="talentStrategy")
    planned_shoot_days: int = Field(..., alias="plannedShootDays")
    actual_shoot_days: Optional[int] = Field(None, alias="actualShootDays")
    production_health: str = Field(..., alias="productionHealth")
    audience_type: str = Field(..., alias="audienceType")
    marketing_budget_level: str = Field(..., alias="marketingBudgetLevel")
    primary_marketing_channel: str = Field(..., alias="primaryMarketingChannel")
    release_model: str = Field(..., alias="releaseModel")
    distribution_confidence: str = Field(..., alias="distributionConfidence")

    model_config = {"populate_by_name": True}


class PhaseUpdate(BaseModel):
    new_phase: int = Field(..., alias="newPhase")

    model_config = {"populate_by_name": True}


class InsightCreate(BaseModel):
    content: str


class InsightResponse(BaseModel):
    id: int
    content: str
    timestamp: datetime

    model_config = {"from_attributes": True}


class FilmProjectResponse(BaseModel):
    id: int
    title: str
    currentPhase: int
    genre: str
    language: str
    theme: str
    scale: str
    budgetLevel: str
    talentStrategy: str
    plannedShootDays: int
    actualShootDays: Optional[int] = None
    productionHealth: str
    audienceType: str
    marketingBudgetLevel: str
    primaryMarketingChannel: str
    releaseModel: str
    distributionConfidence: str
    lastUpdated: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_model(cls, project) -> "FilmProjectResponse":
        return cls(
            id=project.id,
            title=project.title,
            currentPhase=project.current_phase,
            genre=project.genre,
            language=project.language,
            theme=project.theme,
            scale=project.scale,
            budgetLevel=project.budget_level,
            talentStrategy=project.talent_strategy,
            plannedShootDays=project.planned_shoot_days,
            actualShootDays=project.actual_shoot_days,
            productionHealth=project.production_health,
            audienceType=project.audience_type,
            marketingBudgetLevel=project.marketing_budget_level,
            primaryMarketingChannel=project.primary_marketing_channel,
            releaseModel=project.release_model,
            distributionConfidence=project.distribution_confidence,
            lastUpdated=project.last_updated,
        )


class FilmProjectWithInsights(BaseModel):
    project: FilmProjectResponse
    insights: List[InsightResponse]

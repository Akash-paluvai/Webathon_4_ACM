"""
Phase-5 Route — Marketing Strategy Planning
POST /api/projects/{project_id}/phase/5

Accepts JSON: { marketingBudgetLevel: "LOW"|"MEDIUM"|"HIGH" }
Reads project context, computes marketing plan, persists what the schema allows.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import FilmProject
from services.phase5_logic import compute_phase5

router = APIRouter(prefix="/api/projects", tags=["Phase 5"])


class Phase5Request(BaseModel):
    marketingBudgetLevel: str   # LOW | MEDIUM | HIGH


@router.post("/{project_id}/phase/5")
def run_phase5(
    project_id: int,
    data: Phase5Request,
    db: Session = Depends(get_db),
):
    # 1. Load project
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Film project not found")

    # 2. Compute marketing strategy
    result = compute_phase5(
        audience_type=project.audience_type,
        audience_interest_score=getattr(project, "audience_interest_score", 60),
        scale=project.scale,
        budget_level=project.budget_level,
        marketing_budget_level=data.marketingBudgetLevel,
    )

    # 3. Persist fields that exist on the model
    project.marketing_budget_level = data.marketingBudgetLevel.lower()
    project.primary_marketing_channel = result["primaryMarketingChannel"].lower()
    project.last_updated = datetime.now(timezone.utc)

    db.commit()
    db.refresh(project)

    # 4. Return full results (including non-persisted fields)
    return {
        "projectId": project.id,
        "marketingBudgetLevel": data.marketingBudgetLevel,
        "primaryMarketingChannel": result["primaryMarketingChannel"],
        "budgetAllocation": result["budgetAllocation"],
        "discoverabilityScore": result["discoverabilityScore"],
        "marketingRisk": result["marketingRisk"],
        "riskFlags": result["riskFlags"],
        "explanation": result["explanation"],
    }

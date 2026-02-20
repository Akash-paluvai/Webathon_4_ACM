"""
Phase-4 Route — Post-Production & Market Testing
POST /api/projects/{project_id}/phase/4

Accepts multipart form:
  - trailer_video: UploadFile (MP4)
  - testStrategy: str (FESTIVAL | PRIVATE | DIGITAL)

Calls trailer_analysis + phase4_logic, updates the FilmProject,
and returns the computed results.  No AI insights generated here.
"""

import os
import tempfile
from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import FilmProject
from services.trailer_analysis import extract_trailer_features
from services.phase4_logic import compute_phase4
from services.phase4_insights import generate_phase4_insights

router = APIRouter(prefix="/api/projects", tags=["Phase 4"])


@router.post("/{project_id}/phase/4")
def run_phase4(
    project_id: int,
    trailer_video: UploadFile = File(...),
    testStrategy: str = Form(...),
    db: Session = Depends(get_db),
):
    # 1. Look up the project
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Film project not found")

    # 2. Save the uploaded trailer to a temp file
    suffix = os.path.splitext(trailer_video.filename or "video.mp4")[1] or ".mp4"
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=suffix)
    try:
        os.close(tmp_fd)
        with open(tmp_path, "wb") as f:
            # Stream in 1 MB chunks to avoid loading the whole file into RAM
            while chunk := trailer_video.file.read(1024 * 1024):
                f.write(chunk)

        # 3. Extract trailer features (no ML training, no DB writes)
        trailer_features = extract_trailer_features(tmp_path)

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    # 4. Deterministic scoring
    result = compute_phase4(
        scale=project.scale,
        production_health=project.production_health,
        trailer_features=trailer_features,
    )

    # 5. Update the project record
    project.audience_type = result["audienceType"]
    project.last_updated = datetime.now(timezone.utc)

    db.commit()
    db.refresh(project)

    # 6. Return the computed results
    return {
        "projectId": project.id,
        "testStrategy": testStrategy,
        "audienceType": result["audienceType"],
        "audienceInterestScore": result["audienceInterestScore"],
        "trailerFeatures": trailer_features,
    }


# ── Phase-4 Insight generation (rule-based, no LLM) ───────

class Phase4InsightRequest(BaseModel):
    audienceType: str
    audienceInterestScore: int
    testStrategy: str
    trailerFeatures: dict = {}


@router.post("/{project_id}/phase/4/insights")
def get_phase4_insights(
    project_id: int,
    data: Phase4InsightRequest,
    db: Session = Depends(get_db),
):
    # Read-only DB access for project context
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Film project not found")

    insights = generate_phase4_insights(
        scale=project.scale,
        production_health=project.production_health,
        audience_type=data.audienceType,
        audience_interest_score=data.audienceInterestScore,
        test_strategy=data.testStrategy,
        trailer_features=data.trailerFeatures,
    )

    return {"insights": insights}
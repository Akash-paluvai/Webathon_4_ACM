"""
Phase-4 Route — Post-Production & Market Testing
POST /api/projects/{project_id}/phase/4
POST /api/projects/{project_id}/phase/4/insights

Accepts multipart form:
  - trailer_video: UploadFile (MP4)
  - testStrategy: str (FESTIVAL | PRIVATE | DIGITAL)

Calls trailer_analysis + phase4_logic, updates the FilmProject,
and returns the computed results.
"""

import os
import tempfile
from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, UploadFile, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import FilmProject
from services.trailer_analysis import extract_trailer_features
from services.phase4_logic import compute_phase4, derive_enhanced_signals
from services.cerebras_insights import generate_cerebras_insights
from services.movinet_service import analyze_video_movinet

router = APIRouter(prefix="/api/projects", tags=["Phase 4"])

# Simple in-memory storage for enhanced signals (since we won't refactor DB schema)
_ENHANCED_CACHE = {}

def background_movinet_analysis(project_id: int, video_path: str, deterministic_features: dict):
    """Run MoViNet in background and store results."""
    try:
        movinet_results = analyze_video_movinet(video_path)
        enhanced_signals = derive_enhanced_signals(deterministic_features, movinet_results)
        _ENHANCED_CACHE[project_id] = {
            "movinet": movinet_results,
            "enhancedSignals": enhanced_signals
        }
    except Exception as e:
        print(f"Background MoViNet failed for project {project_id}: {e}")
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)

@router.post("/{project_id}/phase/4")
def run_phase4(
    project_id: int,
    background_tasks: BackgroundTasks,
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
    # We'll need a second temp file for background task because the first one might be deleted
    # Or we can just manage the deletion in the background task.
    
    try:
        os.close(tmp_fd)
        with open(tmp_path, "wb") as f:
            while chunk := trailer_video.file.read(1024 * 1024):
                f.write(chunk)

        # 3. Extract trailer features (baseline)
        trailer_features = extract_trailer_features(tmp_path)

        # 4. Deterministic scoring
        result = compute_phase4(
            scale=project.scale,
            production_health=project.production_health,
            trailer_features=trailer_features,
        )

        # Initial derivation without MoViNet
        initial_enhanced = derive_enhanced_signals(trailer_features)

        # 5. Update the project record
        project.audience_type = result["audienceType"]
        project.last_updated = datetime.now(timezone.utc)
        db.commit()
        db.refresh(project)

        # 6. Trigger MoViNet background task (pass a copy of the video path)
        # We move/copy the file to a safer place for background processing
        bg_tmp_path = tmp_path + ".bg.mp4"
        import shutil
        shutil.copy2(tmp_path, bg_tmp_path)
        background_tasks.add_task(background_movinet_analysis, project_id, bg_tmp_path, trailer_features)

        # 7. Return the computed results
        return {
            "projectId": project.id,
            "testStrategy": testStrategy,
            "audienceType": result["audienceType"],
            "audienceInterestScore": result["audienceInterestScore"],
            "trailerFeatures": trailer_features,
            "enhancedSignals": initial_enhanced,
            "enhancedAnalysisAvailable": False # Initially false, will be true in insights call
        }

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# ── Phase-4 AI Insight generation (Cerebras) ──────────────

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

    # Check for enhanced signals in cache
    enhanced_data = _ENHANCED_CACHE.get(project_id)
    enhanced_signals = data.trailerFeatures.get("enhancedSignals")
    
    if enhanced_data:
        # Override with background task results if they are ready
        enhanced_signals = enhanced_data["enhancedSignals"]

    ai_insights = generate_cerebras_insights(
        audience_type=data.audienceType,
        test_strategy=data.testStrategy,
        audience_interest_score=data.audienceInterestScore,
        trailer_features=data.trailerFeatures,
        enhanced_signals=enhanced_signals
    )

    return {
        "marketRead": ai_insights["marketRead"],
        "riskSignals": ai_insights["riskSignals"],
        "strategicRecommendations": ai_insights["strategicRecommendations"],
        "enhancedAnalysisAvailable": True if enhanced_data else False,
        "enhancedSignals": enhanced_signals
    }

from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()

from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models import FilmProject, Insight
from schemas import (
    FilmProjectCreate, FilmProjectUpdate, PhaseUpdate,
    InsightCreate, InsightResponse,
    FilmProjectResponse, FilmProjectWithInsights,
)

# Phase 1
from partA.script_analysis_model import analyze_script_text
from partA.phase1_confirm_engine import confirm_phase1

# Phase 2
from partA.feasibility import compute_feasibility
from partA.package_ing import evaluate_packaging
from partA.confirm import confirm_phase2

# Phase 3
from partA.phase3_ai_engine import analyze_phase3
from partA.phase3_explain import explain_phase3
from partA.phase3_confirm import confirm_phase3

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Film Producer Decision Support Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════
# PROJECT CRUD  (required by frontend)
# ═══════════════════════════════════

@app.get("/api/projects", response_model=List[FilmProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(FilmProject).order_by(FilmProject.last_updated.desc()).all()
    return [FilmProjectResponse.from_orm_model(p) for p in projects]


@app.post("/api/projects", response_model=FilmProjectResponse)
def create_project(payload: FilmProjectCreate, db: Session = Depends(get_db)):
    project = FilmProject(
        title=payload.title,
        genre=payload.genre,
        language=payload.language,
        theme=payload.theme,
        scale=payload.scale,
        budget_level=payload.budget_level,
        talent_strategy=payload.talent_strategy,
        planned_shoot_days=payload.planned_shoot_days,
        audience_type=payload.audience_type,
        marketing_budget_level=payload.marketing_budget_level,
        primary_marketing_channel=payload.primary_marketing_channel,
        release_model=payload.release_model,
        distribution_confidence=payload.distribution_confidence,
        current_phase=1,
        production_health="good",
        last_updated=datetime.now(timezone.utc),
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return FilmProjectResponse.from_orm_model(project)


@app.get("/api/projects/{project_id}", response_model=FilmProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return FilmProjectResponse.from_orm_model(project)


@app.put("/api/projects/{project_id}", response_model=FilmProjectResponse)
def update_project(project_id: int, payload: FilmProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.title = payload.title
    project.current_phase = payload.phase
    project.genre = payload.genre
    project.language = payload.language
    project.theme = payload.theme
    project.scale = payload.scale
    project.budget_level = payload.budget_level
    project.talent_strategy = payload.talent_strategy
    project.planned_shoot_days = payload.planned_shoot_days
    project.actual_shoot_days = payload.actual_shoot_days
    project.production_health = payload.production_health
    project.audience_type = payload.audience_type
    project.marketing_budget_level = payload.marketing_budget_level
    project.primary_marketing_channel = payload.primary_marketing_channel
    project.release_model = payload.release_model
    project.distribution_confidence = payload.distribution_confidence
    project.last_updated = datetime.now(timezone.utc)

    db.commit()
    db.refresh(project)
    return FilmProjectResponse.from_orm_model(project)


@app.patch("/api/projects/{project_id}/phase", response_model=FilmProjectResponse)
def update_project_phase(project_id: int, payload: PhaseUpdate, db: Session = Depends(get_db)):
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.current_phase = payload.new_phase
    project.last_updated = datetime.now(timezone.utc)
    db.commit()
    db.refresh(project)
    return FilmProjectResponse.from_orm_model(project)


# ═══════════════════════════════════
# INSIGHTS CRUD  (required by frontend)
# ═══════════════════════════════════

@app.get("/api/projects/{project_id}/insights", response_model=List[InsightResponse])
def list_insights(project_id: int, db: Session = Depends(get_db)):
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project.insights


@app.post("/api/projects/{project_id}/insights", response_model=InsightResponse)
def add_insight(project_id: int, payload: InsightCreate, db: Session = Depends(get_db)):
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    insight = Insight(
        project_id=project_id,
        content=payload.content,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(insight)
    db.commit()
    db.refresh(insight)
    return insight


@app.get("/api/projects/{project_id}/with-insights", response_model=FilmProjectWithInsights)
def get_project_with_insights(project_id: int, db: Session = Depends(get_db)):
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return FilmProjectWithInsights(
        project=FilmProjectResponse.from_orm_model(project),
        insights=[InsightResponse.model_validate(i, from_attributes=True) for i in project.insights],
    )


# ═══════════════════════════════════
# PHASE 1 — Concept Intelligence
# ═══════════════════════════════════

@app.post("/api/phase1/analyze")
def analyze_phase1(payload: dict):
    if not payload.get("scriptText"):
        raise HTTPException(status_code=400, detail="Script text required")
    try:
        return analyze_script_text(
            script_text=payload["scriptText"],
            genre=payload.get("genre", "Drama"),
            theme=payload.get("theme", ""),
            scale=payload.get("scale", "studio"),
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/phase1/confirm", response_model=FilmProjectResponse)
def phase1_confirm(payload: dict, db: Session = Depends(get_db)):
    return confirm_phase1(payload, db)


@app.post("/api/script/analyze")
def script_analyze(payload: dict):
    """Standalone script analysis via Groq LLM."""
    script_text = payload.get("scriptText", "")
    if not script_text or not script_text.strip():
        raise HTTPException(status_code=400, detail="scriptText is required")
    try:
        return analyze_script_text(script_text)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


# ═══════════════════════════════════
# PHASE 2 — Packaging & Feasibility
# ═══════════════════════════════════

@app.post("/api/phase2/feasibility/{project_id}")
def phase2_feasibility(project_id: int, payload: dict, db: Session = Depends(get_db)):
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return compute_feasibility(project, payload, db)


@app.post("/api/phase2/packaging/{project_id}")
def phase2_packaging(project_id: int, payload: dict, db: Session = Depends(get_db)):
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return evaluate_packaging(project, payload, db)


@app.post("/api/phase2/confirm/{project_id}")
def phase2_confirm_route(project_id: int, payload: dict, db: Session = Depends(get_db)):
    return confirm_phase2(project_id, payload, db)


# ═══════════════════════════════════
# PHASE 3 — Production Intelligence
# ═══════════════════════════════════

@app.post("/api/phase3/analyze")
def phase3_analyze(payload: dict, db: Session = Depends(get_db)):
    # Try to load project context if project_id is provided
    project = None
    project_id = payload.get("projectId")
    if project_id:
        project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    analysis = analyze_phase3(payload, project, db)
    explanation = explain_phase3(payload, analysis, project)
    return {"analysis": analysis, "explainability": explanation}


@app.post("/api/phase3/confirm/{project_id}")
def phase3_confirm_route(project_id: int, payload: dict, db: Session = Depends(get_db)):
    project = confirm_phase3(project_id, payload, db)
    return FilmProjectResponse.from_orm_model(project)


# ═══════════════════════════════════
# HEALTH
# ═══════════════════════════════════

@app.get("/api/health")
def health():
    return {"status": "ok"}
from datetime import datetime, timezone
from typing import List
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models import FilmProject, Insight
import phase6_models  # noqa — registers Phase 6 tables
from schemas import (
    FilmProjectCreate,
    FilmProjectUpdate,
    FilmProjectResponse,
    FilmProjectWithInsights,
    PhaseUpdate,
    InsightCreate,
    InsightResponse,
)

# 🔹 Phase 1 engine (Part A)
from partA.concept_engine import analyze_script


# ──────────────────────────────────────────────
# Application lifespan (startup / shutdown)
# ──────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    App startup tasks:
    - Create DB tables
    - Seed Phase 6 reference data
    """
    Base.metadata.create_all(bind=engine)

    from database import SessionLocal
    db = SessionLocal()
    try:
        from phase6.services.seed_data import seed_all
        seed_all(db)
    finally:
        db.close()

    yield


# ──────────────────────────────────────────────
# App init
# ──────────────────────────────────────────────

app = FastAPI(
    title="Film Producer Decision Support Platform API",
    lifespan=lifespan,
)

# ──────────────────────────────────────────────
# CORS
# ──────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────
# Phase Routers
# ──────────────────────────────────────────────

from routes.phase4 import router as phase4_router
app.include_router(phase4_router)

from routes.phase5 import router as phase5_router
app.include_router(phase5_router)

from routes.marketing import router as marketing_router
app.include_router(marketing_router)

from phase6.routes import router as phase6_router
app.include_router(phase6_router, prefix="/phase6", tags=["Phase 6"])

from phase7.routes import router as phase7_router
app.include_router(phase7_router, prefix="/phase7", tags=["Phase 7"])


# ──────────────────────────────────────────────
# Phase 1 — Concept Exploration (NO DB WRITE)
# ──────────────────────────────────────────────

@app.post("/api/phase1/analyze")
def analyze_phase1(payload: dict):
    """
    Analyze script concept.
    Stateless analysis — does NOT write to DB.
    """
    if not payload.get("scriptText"):
        raise HTTPException(status_code=400, detail="Script text required")

    return analyze_script(payload)


# ──────────────────────────────────────────────
# Film Project endpoints
# ──────────────────────────────────────────────

@app.post("/api/projects", response_model=FilmProjectResponse)
def create_project(data: FilmProjectCreate, db: Session = Depends(get_db)):
    project = FilmProject(
        title=data.title,
        genre=data.genre,
        language=data.language,
        theme=data.theme,
        scale=data.scale,
        budget_level=data.budget_level,
        talent_strategy=data.talent_strategy,
        planned_shoot_days=data.planned_shoot_days,
        audience_type=data.audience_type,
        marketing_budget_level=data.marketing_budget_level,
        primary_marketing_channel=data.primary_marketing_channel,
        release_model=data.release_model,
        distribution_confidence=data.distribution_confidence,
        current_phase=1,
        production_health="good",
        last_updated=datetime.now(timezone.utc),
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return FilmProjectResponse.from_orm_model(project)


@app.get("/api/projects", response_model=List[FilmProjectResponse])
def get_all_projects(db: Session = Depends(get_db)):
    projects = db.query(FilmProject).all()
    return [FilmProjectResponse.from_orm_model(p) for p in projects]


@app.get("/api/projects/{project_id}", response_model=FilmProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Film project not found")
    return FilmProjectResponse.from_orm_model(project)


@app.put("/api/projects/{project_id}", response_model=FilmProjectResponse)
def update_project(project_id: int, data: FilmProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Film project not found")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(project, field, value)

    project.last_updated = datetime.now(timezone.utc)
    db.commit()
    db.refresh(project)
    return FilmProjectResponse.from_orm_model(project)


@app.patch("/api/projects/{project_id}/phase", response_model=FilmProjectResponse)
def update_project_phase(project_id: int, data: PhaseUpdate, db: Session = Depends(get_db)):
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Film project not found")

    if not 1 <= data.new_phase <= 8:
        raise HTTPException(status_code=400, detail="Phase must be between 1 and 8")

    project.current_phase = data.new_phase
    project.last_updated = datetime.now(timezone.utc)
    db.commit()
    db.refresh(project)
    return FilmProjectResponse.from_orm_model(project)


# ──────────────────────────────────────────────
# Insight endpoints
# ──────────────────────────────────────────────

@app.post("/api/projects/{project_id}/insights", response_model=InsightResponse)
def add_insight(project_id: int, data: InsightCreate, db: Session = Depends(get_db)):
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Film project not found")

    insight = Insight(
        project_id=project_id,
        content=data.content,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(insight)
    db.commit()
    db.refresh(insight)
    return insight


@app.get("/api/projects/{project_id}/insights", response_model=List[InsightResponse])
def get_project_insights(project_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Insight)
        .filter(Insight.project_id == project_id)
        .order_by(Insight.timestamp)
        .all()
    )


@app.get("/api/projects/{project_id}/with-insights", response_model=FilmProjectWithInsights)
def get_project_with_insights(project_id: int, db: Session = Depends(get_db)):
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Film project not found")

    insights = (
        db.query(Insight)
        .filter(Insight.project_id == project_id)
        .order_by(Insight.timestamp)
        .all()
    )

    return FilmProjectWithInsights(
        project=FilmProjectResponse.from_orm_model(project),
        insights=insights,
    )


# ──────────────────────────────────────────────
# Health check
# ──────────────────────────────────────────────

@app.get("/api/health")
def health_check():
    return {"status": "ok"}


# ──────────────────────────────────────────────
# Local dev runner
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
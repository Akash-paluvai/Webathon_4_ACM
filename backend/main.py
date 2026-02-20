from datetime import datetime, timezone
from typing import List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models import FilmProject, Insight
import phase6_models  # noqa — registers Phase 6 tables with Base.metadata
from schemas import (
    FilmProjectCreate,
    FilmProjectUpdate,
    FilmProjectResponse,
    FilmProjectWithInsights,
    PhaseUpdate,
    InsightCreate,
    InsightResponse,
)

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Film Producer Decision Support Platform API")

# Seed Phase 6 reference data
@app.on_event("startup")
def _seed_phase6_data():
    from database import SessionLocal
    db = SessionLocal()
    try:
        from phase6.services.seed_data import seed_all
        seed_all(db)
    finally:
        db.close()

# CORS — allow the Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Phase 6 router
from phase6.routes import router as phase6_router
app.include_router(phase6_router, prefix="/phase6", tags=["Phase 6"])


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

    project.title = data.title
    project.current_phase = data.phase
    project.genre = data.genre
    project.language = data.language
    project.theme = data.theme
    project.scale = data.scale
    project.budget_level = data.budget_level
    project.talent_strategy = data.talent_strategy
    project.planned_shoot_days = data.planned_shoot_days
    project.actual_shoot_days = data.actual_shoot_days
    project.production_health = data.production_health
    project.audience_type = data.audience_type
    project.marketing_budget_level = data.marketing_budget_level
    project.primary_marketing_channel = data.primary_marketing_channel
    project.release_model = data.release_model
    project.distribution_confidence = data.distribution_confidence
    project.last_updated = datetime.now(timezone.utc)

    db.commit()
    db.refresh(project)
    return FilmProjectResponse.from_orm_model(project)


@app.patch("/api/projects/{project_id}/phase", response_model=FilmProjectResponse)
def update_project_phase(project_id: int, data: PhaseUpdate, db: Session = Depends(get_db)):
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Film project not found")

    if data.new_phase < 1 or data.new_phase > 8:
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
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Film project not found")

    insights = (
        db.query(Insight)
        .filter(Insight.project_id == project_id)
        .order_by(Insight.timestamp)
        .all()
    )
    return insights


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

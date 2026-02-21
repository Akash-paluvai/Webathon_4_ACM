from datetime import datetime, timezone
from typing import List
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models import FilmProject, Insight
import phase6_models  # registers Phase 6 tables

from schemas import (
    FilmProjectCreate, FilmProjectUpdate, PhaseUpdate,
    InsightCreate, InsightResponse,
    FilmProjectResponse, FilmProjectWithInsights,
)

# ──────────────────────────────────────────────
# Phase 1–3 Engines (Part A)
# ──────────────────────────────────────────────

from partA.script_analysis_model import analyze_script_text
from partA.phase1_confirm_engine import confirm_phase1

from partA.feasibility import compute_feasibility
from partA.package_ing import evaluate_packaging
from partA.confirm import confirm_phase2

from partA.phase3_ai_engine import analyze_phase3
from partA.phase3_explain import explain_phase3
from partA.phase3_confirm import confirm_phase3

from services.assistant import chat_with_assistant

# ──────────────────────────────────────────────
# Application lifespan
# ──────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
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
from routes.phase5 import router as phase5_router
from routes.marketing import router as marketing_router
from phase6.routes import router as phase6_router
from phase7.routes import router as phase7_router

@app.get("/api/projects", response_model=List[FilmProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(FilmProject).order_by(FilmProject.last_updated.desc()).all()
    return [FilmProjectResponse.from_orm_model(p) for p in projects]


@app.post("/api/projects", response_model=FilmProjectResponse)
def create_project(payload: FilmProjectCreate, db: Session = Depends(get_db)):
    project = FilmProject(
        **payload.model_dump(),
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

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)

    project.last_updated = datetime.now(timezone.utc)
    db.commit()
    db.refresh(project)
    return FilmProjectResponse.from_orm_model(project)


@app.patch("/api/projects/{project_id}/phase", response_model=FilmProjectResponse)
def update_project_phase(project_id: int, payload: PhaseUpdate, db: Session = Depends(get_db)):
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not 1 <= payload.new_phase <= 8:
        raise HTTPException(status_code=400, detail="Phase must be between 1 and 8")

    project.current_phase = payload.new_phase
    project.last_updated = datetime.now(timezone.utc)
    db.commit()
    db.refresh(project)
    return FilmProjectResponse.from_orm_model(project)


app.include_router(phase4_router)
app.include_router(phase5_router)
app.include_router(marketing_router)
app.include_router(phase6_router, prefix="/phase6", tags=["Phase 6"])
app.include_router(phase7_router, prefix="/phase7", tags=["Phase 7"])

# ──────────────────────────────────────────────
# Phase 1 — Concept Exploration
# ──────────────────────────────────────────────

@app.post("/api/phase1/analyze")
def phase1_analyze(payload: dict):
    if not payload.get("scriptText"):
        raise HTTPException(status_code=400, detail="Script text required")

    return analyze_script_text(
        script_text=payload["scriptText"],
        genre=payload.get("genre", "Drama"),
        theme=payload.get("theme", ""),
        scale=payload.get("scale", "studio"),
    )


@app.post("/api/phase1/confirm", response_model=FilmProjectResponse)
def phase1_confirm(payload: dict, db: Session = Depends(get_db)):
    return confirm_phase1(payload, db)

# ──────────────────────────────────────────────
# Insights
# ──────────────────────────────────────────────

@app.get("/api/projects", response_model=List[FilmProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(FilmProject).order_by(FilmProject.last_updated.desc()).all()
    return [FilmProjectResponse.from_orm_model(p) for p in projects]


@app.post("/api/projects", response_model=FilmProjectResponse)
def create_project(payload: FilmProjectCreate, db: Session = Depends(get_db)):
    project = FilmProject(
        **payload.model_dump(),
        current_phase=1,
        production_health="good",
        last_updated=datetime.now(timezone.utc),
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return FilmProjectResponse.from_orm_model(project)


@app.put("/api/projects/{project_id}", response_model=FilmProjectResponse)
def update_project(project_id: int, payload: FilmProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)

    project.last_updated = datetime.now(timezone.utc)
    db.commit()
    db.refresh(project)
    return FilmProjectResponse.from_orm_model(project)


@app.patch("/api/projects/{project_id}/phase", response_model=FilmProjectResponse)
def update_project_phase(project_id: int, payload: PhaseUpdate, db: Session = Depends(get_db)):
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not 1 <= payload.new_phase <= 8:
        raise HTTPException(status_code=400, detail="Phase must be between 1 and 8")

    project.current_phase = payload.new_phase
    project.last_updated = datetime.now(timezone.utc)
    db.commit()
    db.refresh(project)
    return FilmProjectResponse.from_orm_model(project)


# ──────────────────────────────────────────────
# Phase 2 — Packaging & Feasibility
# ──────────────────────────────────────────────

@app.post("/api/phase2/feasibility/{project_id}")
def phase2_feasibility(project_id: int, payload: dict, db: Session = Depends(get_db)):
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return compute_feasibility(project, payload, db=db)


@app.post("/api/phase2/packaging/{project_id}")
def phase2_packaging(project_id: int, payload: dict, db: Session = Depends(get_db)):
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return evaluate_packaging(project, payload, db=db)


@app.post("/api/phase2/confirm/{project_id}")
def phase2_confirm(project_id: int, payload: dict, db: Session = Depends(get_db)):
    result = confirm_phase2(project_id, payload, db)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


# ──────────────────────────────────────────────
# Phase 3 — Production Intelligence
# ──────────────────────────────────────────────

@app.post("/api/phase3/analyze")
def phase3_analyze(payload: dict, db: Session = Depends(get_db)):
    project_id = payload.get("projectId")
    if not project_id:
        raise HTTPException(status_code=400, detail="projectId required in payload")
    
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return analyze_phase3(payload, project=project, db=db)


@app.post("/api/phase3/confirm/{project_id}")
def phase3_confirm(project_id: int, payload: dict, db: Session = Depends(get_db)):
    try:
        project = confirm_phase3(project_id, payload, db)
        return FilmProjectResponse.from_orm_model(project)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# ──────────────────────────────────────────────
# Insights
# ──────────────────────────────────────────────

@app.get("/api/projects/{project_id}/insights", response_model=List[InsightResponse])
def list_insights(project_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Insight)
        .filter(Insight.project_id == project_id)
        .order_by(Insight.timestamp)
        .all()
    )


@app.post("/api/projects/{project_id}/insights", response_model=InsightResponse)
def add_insight(project_id: int, payload: InsightCreate, db: Session = Depends(get_db)):
    insight = Insight(
        project_id=project_id,
        content=payload.content,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(insight)
    db.commit()
    db.refresh(insight)
    return insight

# ──────────────────────────────────────────────
# Assistant
# ──────────────────────────────────────────────

@app.post("/api/assistant/chat")
def assistant_chat(payload: dict):
    message = payload.get("message")
    if not message:
        raise HTTPException(status_code=400, detail="Message required")
    
    phase = payload.get("phase")
    history = payload.get("history", [])
    
    response_text = chat_with_assistant(message, phase, history)
    return {"text": response_text}

# ──────────────────────────────────────────────
# Health
# ──────────────────────────────────────────────

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

# ──────────────────────────────────────────────
# Local dev
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models import FilmProject
from schemas import FilmProjectResponse

# Phase 1
from partA.analysis_engine import analyze_script_and_audience
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
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────
# PHASE 1
# ─────────────────────────────
@app.post("/api/phase1/analyze")
def analyze_phase1(payload: dict):
    if not payload.get("scriptText"):
        raise HTTPException(status_code=400, detail="Script text required")

    return analyze_script_and_audience(payload)


@app.post("/api/phase1/confirm", response_model=FilmProjectResponse)
def phase1_confirm(payload: dict, db: Session = Depends(get_db)):
    return confirm_phase1(payload, db)


# ─────────────────────────────
# PHASE 2
# ─────────────────────────────
@app.post("/api/phase2/feasibility/{project_id}")
def phase2_feasibility(project_id: int, payload: dict, db: Session = Depends(get_db)):

    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return compute_feasibility(project, payload)


@app.post("/api/phase2/packaging/{project_id}")
def phase2_packaging(project_id: int, payload: dict, db: Session = Depends(get_db)):

    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return evaluate_packaging(project, payload)


@app.post("/api/phase2/confirm/{project_id}", response_model=FilmProjectResponse)
def phase2_confirm(project_id: int, payload: dict, db: Session = Depends(get_db)):
    return confirm_phase2(project_id, payload, db)


# ─────────────────────────────
# PHASE 3 ANALYSIS
# ─────────────────────────────
@app.post("/api/phase3/analyze")
def phase3_analyze(payload: dict):

    analysis = analyze_phase3(payload)
    explanation = explain_phase3(payload, analysis)

    return {
        "analysis": analysis,
        "explainability": explanation
    }


# ─────────────────────────────
# PHASE 3 CONFIRM
# ─────────────────────────────
@app.post("/api/phase3/confirm/{project_id}", response_model=FilmProjectResponse)
def phase3_confirm_route(project_id: int, payload: dict, db: Session = Depends(get_db)):

    project = confirm_phase3(project_id, payload, db)
    return FilmProjectResponse.from_orm_model(project)


# ─────────────────────────────
# HEALTH
# ─────────────────────────────
@app.get("/api/health")
def health():
    return {"status": "ok"}
from datetime import datetime, timezone
from typing import List

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models import FilmProject, Insight
from schemas import (
    FilmProjectCreate,
    FilmProjectUpdate,
    FilmProjectResponse,
    FilmProjectWithInsights,
    PhaseUpdate,
    InsightCreate,
    InsightResponse,
)

# Phase-1
from partA.analysis_engine import analyze_script_and_audience

# Phase-2
from partA.feasibility import compute_feasibility
from partA.package_ing import evaluate_packaging
from partA.confirm import confirm_phase2


# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Film Producer Decision Support Platform API")


# ─────────────────────────────
# CORS CONFIG
# ─────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────
# PHASE 1 — SCRIPT ANALYSIS
# Stores concept/audience data in DB
# ─────────────────────────────
@app.post("/api/phase1/analyze")
def analyze_phase1(payload: dict):
    if not payload.get("scriptText"):
        raise HTTPException(status_code=400, detail="Script text required")

    return analyze_script_and_audience(payload)


# ─────────────────────────────
# PHASE 2 — STEP 5
# FEASIBILITY ANALYSIS
# Reads Phase-1 data from DB
# ─────────────────────────────
@app.post("/api/phase2/feasibility/{project_id}")
def phase2_feasibility(
    project_id: int,
    payload: dict,
    db: Session = Depends(get_db)
):
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return compute_feasibility(project, payload)


# ─────────────────────────────
# PHASE 2 — STEP 6
# PACKAGING EVALUATION
# Uses Phase-1 DB info
# ─────────────────────────────
@app.post("/api/phase2/packaging/{project_id}")
def phase2_packaging(
    project_id: int,
    payload: dict,
    db: Session = Depends(get_db)
):
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return evaluate_packaging(project, payload)


# ─────────────────────────────
# PHASE 2 — STEP 7
# FINAL CONFIRMATION + DB UPDATE
# ─────────────────────────────
@app.post("/api/phase2/confirm/{project_id}")
def phase2_confirm_route(
    project_id: int,
    payload: dict,
    db: Session = Depends(get_db)
):
    return confirm_phase2(project_id, payload, db)


# ─────────────────────────────
# HEALTH CHECK
# ─────────────────────────────
@app.get("/api/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
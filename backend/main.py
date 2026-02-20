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

from partA.analysis_engine import analyze_script_and_audience
from partA.confirm import confirm_phase2

# Create tables
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
# Phase 1 Analysis Endpoint
# ─────────────────────────────
@app.post("/api/phase1/analyze")
def analyze_phase1(payload: dict):
    if not payload.get("scriptText"):
        raise HTTPException(status_code=400, detail="scriptText required")

    return analyze_script_and_audience(payload)


# ─────────────────────────────
# Health Check
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


# ─────────────────────────────
# RUN SERVER
# ─────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
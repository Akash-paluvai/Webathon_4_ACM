"""
Phase 1 — Confirmation Engine (DB write)
=========================================
On user confirmation after script analysis, write minimal fields
to the existing DB schema. No schema changes. No new columns.
"""

from datetime import datetime, timezone
from fastapi import HTTPException
from models import FilmProject, Insight
from schemas import FilmProjectResponse


def confirm_phase1(payload: dict, db) -> FilmProjectResponse:
    """
    Persist Phase 1 analysis results to DB.

    Expected payload keys:
        title, genre, language, theme, scale,
        feasibilityScore, riskScore, audienceMatch,
        goDecision, summary (optional)
    """
    required = [
        "title", "genre", "language", "theme", "scale",
        "feasibilityScore", "riskScore", "audienceMatch",
        "goDecision",
    ]
    for field in required:
        if field not in payload:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

    # ── Map riskScore → production_health ──
    risk_map = {"LOW": "good", "MEDIUM": "atRisk", "HIGH": "critical"}
    production_health = risk_map.get(
        str(payload["riskScore"]).upper(), "good"
    )

    # ── Create project (existing schema only) ──
    project = FilmProject(
        title=payload["title"],
        genre=payload["genre"],
        language=payload["language"],
        theme=payload["theme"],
        scale=payload["scale"],

        # Phase 1 computed fields mapped to existing columns
        audience_type=payload["audienceMatch"],
        production_health=production_health,
        current_phase=2,

        # Required non-null fields — sensible defaults for Phase 2
        budget_level="low",
        talent_strategy="unknown",
        planned_shoot_days=30,
        marketing_budget_level="unassigned",
        primary_marketing_channel="undefined",
        release_model="ott",
        distribution_confidence="low",

        last_updated=datetime.now(timezone.utc),
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    # ── Store insight with analysis results ──
    summary_text = payload.get("summary", "")
    insight_content = (
        f"Phase 1 Analysis — Go Decision: {payload['goDecision']}\n"
        f"Feasibility Score: {payload['feasibilityScore']}/100\n"
        f"Risk Level: {payload['riskScore']}\n"
        f"Audience Segment: {payload['audienceMatch']}\n"
        f"---\n"
        f"{summary_text}"
    )

    insight = Insight(
        project_id=project.id,
        content=insight_content.strip(),
        timestamp=datetime.now(timezone.utc),
    )
    db.add(insight)
    db.commit()

    return FilmProjectResponse.from_orm_model(project)
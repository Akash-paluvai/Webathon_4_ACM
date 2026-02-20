from datetime import datetime, timezone
from fastapi import HTTPException
from models import FilmProject, Insight
from schemas import FilmProjectResponse


def confirm_phase1(payload: dict, db):

    required = [
        "title",
        "genre",
        "language",
        "theme",
        "scale",
        "conceptRisk",
        "targetAudience",
        "goDecision",
    ]

    for r in required:
        if r not in payload:
            raise HTTPException(status_code=400, detail=f"{r} missing")

    # Map Phase-1 outputs into existing columns
    risk_map = {
        "LOW": "good",
        "MEDIUM": "atRisk",
        "HIGH": "critical"
    }

    production_health = risk_map.get(
        payload["conceptRisk"].upper(),
        "good"
    )

    project = FilmProject(
        title=payload["title"],
        genre=payload["genre"],
        language=payload["language"],
        theme=payload["theme"],
        scale=payload["scale"],

        # Required non-null fields from schema
        budget_level="low",
        talent_strategy="unknown",
        planned_shoot_days=30,
        audience_type=payload["targetAudience"],

        marketing_budget_level="unassigned",
        primary_marketing_channel="undefined",
        release_model="ott",
        distribution_confidence="low",

        production_health=production_health,
        current_phase=2,
        last_updated=datetime.now(timezone.utc),
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    # Store decision summary as insight (no schema change)
    insight_text = f"""
    Phase 1 Decision Summary:
    Concept Risk: {payload['conceptRisk']}
    Target Audience: {payload['targetAudience']}
    Go Decision: {payload['goDecision']}
    """

    insight = Insight(
        project_id=project.id,
        content=insight_text,
        timestamp=datetime.now(timezone.utc)
    )

    db.add(insight)
    db.commit()

    return FilmProjectResponse.from_orm_model(project)
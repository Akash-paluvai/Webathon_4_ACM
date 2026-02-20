"""
Phase 2 — Confirm & Persist (DB write + Insight)
==================================================
Writes Phase 2 decisions to project, stores Insight record
for Phase 3 to read.
"""

from datetime import datetime, timezone
from models import FilmProject, Insight


def confirm_phase2(project_id: int, payload: dict, db):

    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()

    if not project:
        return {"error": "Project not found"}

    project.budget_level = payload.get("budgetLevel", project.budget_level)
    project.talent_strategy = payload.get("talentStrategy", project.talent_strategy)

    # Advance lifecycle
    project.current_phase = 3
    project.last_updated = datetime.now(timezone.utc)

    db.commit()
    db.refresh(project)

    # Store Phase 2 Insight for downstream phases
    insight_content = (
        f"Phase 2 — Packaging & Feasibility Confirmed\n"
        f"Budget Level: {project.budget_level}\n"
        f"Talent Strategy: {project.talent_strategy}\n"
        f"Genre: {project.genre} | Scale: {project.scale} | Audience: {project.audience_type}\n"
        f"---\n"
        f"Project is cleared for Phase 3 production planning."
    )

    insight = Insight(
        project_id=project.id,
        content=insight_content,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(insight)
    db.commit()

    return {
        "status": "phase2_confirmed",
        "project_id": project.id,
        "next_phase": 3,
    }
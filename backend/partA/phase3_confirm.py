"""
Phase 3 — Confirm & Persist (DB write + Insight)
==================================================
Writes Phase 3 production data to project, stores Insight record.
"""

from datetime import datetime, timezone
from models import FilmProject, Insight


def confirm_phase3(project_id: int, payload: dict, db):

    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()

    if not project:
        raise Exception("Project not found")

    project.planned_shoot_days = payload.get("plannedShootDays", project.planned_shoot_days)
    project.actual_shoot_days = payload.get("actualShootDays", project.actual_shoot_days)
    project.production_health = payload.get("productionHealth", project.production_health)

    project.current_phase = 4  # unlock Part-B
    project.last_updated = datetime.now(timezone.utc)

    db.commit()
    db.refresh(project)

    # Store Phase 3 Insight for downstream (Part-B) phases
    insight_content = (
        f"Phase 3 — Production Intelligence Confirmed\n"
        f"Planned Shoot Days: {project.planned_shoot_days}\n"
        f"Actual Shoot Days: {project.actual_shoot_days or 'Not started'}\n"
        f"Production Health: {project.production_health}\n"
        f"Budget: {project.budget_level} | Talent: {project.talent_strategy}\n"
        f"Genre: {project.genre} | Scale: {project.scale}\n"
        f"---\n"
        f"Project is cleared for Phase 4."
    )

    insight = Insight(
        project_id=project.id,
        content=insight_content,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(insight)
    db.commit()

    return project
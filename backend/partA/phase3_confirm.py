# backend/partA/phase3_confirm.py

from datetime import datetime, timezone
from models import FilmProject


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

    return project
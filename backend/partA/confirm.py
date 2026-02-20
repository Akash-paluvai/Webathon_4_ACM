from datetime import datetime, timezone
from models import FilmProject


def confirm_phase2(project_id: int, payload: dict, db):
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()

    if not project:
        return {"error": "Project not found"}

    project.budget_level = payload.get("budgetLevel")
    project.talent_strategy = payload.get("talentStrategy")
    project.productionFeasibility = payload.get("productionFeasibility")
    project.current_phase = 3
    project.last_updated = datetime.now(timezone.utc)

    db.commit()
    db.refresh(project)

    return {
        "status": "phase2_confirmed",
        "project_id": project.id,
        "next_phase": 3
    }
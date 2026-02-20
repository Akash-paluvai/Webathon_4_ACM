from .feasibility import compute_feasibility
from .roi import compute_roi


def evaluate_packaging(project, payload: dict):

    scale = project.scale

    scenarios = [
        {"budgetLevel": "Low", "talentStrategy": "Newcomers"},
        {"budgetLevel": "Mid", "talentStrategy": "Mixed"},
        {"budgetLevel": "High", "talentStrategy": "Stars"},
    ]

    results = []

    for s in scenarios:
        feasibility = compute_feasibility(project, s)

        roi = compute_roi(
            feasibility["feasibility_score"],
            s["talentStrategy"]
        )

        results.append({
            "budgetLevel": s["budgetLevel"],
            "talentStrategy": s["talentStrategy"],
            "feasibility_score": feasibility["feasibility_score"],
            "risk_indicator": feasibility["risk_indicator"],
            "roi_probability": roi["roi_probability"]
        })

    best_option = max(results, key=lambda x: x["roi_probability"])

    return {
        "scenarios": results,
        "recommended_option": best_option
    }
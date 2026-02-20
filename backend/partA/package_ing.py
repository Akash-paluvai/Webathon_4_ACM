from .feasibility import compute_feasibility
from .roi import compute_roi


def evaluate_packaging(payload: dict):
    """
    Step-6:
    Compare packaging options.
    """

    scale = payload.get("scale")

    scenarios = [
        {"budgetLevel": "Low", "talentStrategy": "Newcomers"},
        {"budgetLevel": "Mid", "talentStrategy": "Mixed"},
        {"budgetLevel": "High", "talentStrategy": "Stars"},
    ]

    results = []

    for s in scenarios:
        feasibility = compute_feasibility({
            "budgetLevel": s["budgetLevel"],
            "talentStrategy": s["talentStrategy"],
            "scale": scale
        })

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

    notes = []
    if best_option["risk_indicator"] == "High":
        notes.append("High execution risk")
    if best_option["roi_probability"] < 60:
        notes.append("Limited ROI upside")
    if best_option["budgetLevel"] == "High":
        notes.append("High budget pressure")

    return {
        "scenarios": results,
        "recommended_option": best_option,
        "risk_notes": notes
    }
# backend/partA/phase3_explain.py

def explain_phase3(payload: dict, analysis_result: dict):

    planned = payload.get("plannedShootDays", 40)
    days_week = payload.get("daysPerWeek", 5)
    crew = payload.get("crewSize", 30)
    complexity = payload.get("complexityLevel", 2)

    importance = {}

    # simple interpretable weighting logic
    importance["plannedShootDays"] = planned * 0.4
    importance["crewSize"] = crew * 0.2
    importance["complexityLevel"] = complexity * 0.3
    importance["daysPerWeek"] = days_week * 0.1

    total = sum(importance.values())

    normalized = {
        k: round((v / total), 2)
        for k, v in importance.items()
    }

    explanation_text = f"""
Schedule prediction is mainly influenced by:
- Planned Shoot Days ({normalized['plannedShootDays']*100}% impact)
- Complexity Level ({normalized['complexityLevel']*100}% impact)
- Crew Size ({normalized['crewSize']*100}% impact)

Delay probability is elevated due to:
- Complexity and resource distribution imbalance.
"""

    return {
        "featureImportance": normalized,
        "explanation": explanation_text.strip()
    }
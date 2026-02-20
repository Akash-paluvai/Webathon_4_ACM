def compute_feasibility(project, payload: dict):
    """
    Step-5:
    Budget + Talent vs Scale feasibility analysis.
    Uses Phase-1 DB data + Phase-2 inputs.
    """

    # Phase-1 data from DB
    genre = project.genre
    audience = project.audience_type
    scale = project.scale

    # Phase-2 input
    budget = payload.get("budgetLevel")
    talent = payload.get("talentStrategy")

    # Base scoring
    budget_score = {"Low": 40, "Mid": 65, "High": 85}.get(budget, 50)
    talent_score = {"Newcomers": 50, "Mixed": 70, "Stars": 85}.get(talent, 60)
    scale_score = {"Small": 50, "Mid": 70, "Large": 90}.get(scale, 60)

    # Combined logic (now influenced by Phase-1)
    feasibility_score = int((budget_score + talent_score - scale_score + 100) / 2)

    # Audience boost logic
    if audience == "Gen-Z" and genre in ["Thriller", "Sci-Fi"]:
        feasibility_score += 5

    feasibility_score = max(0, min(100, feasibility_score))

    # Alignment
    gap = abs(budget_score - scale_score)

    if gap <= 15:
        alignment = "Aligned"
    elif gap <= 30:
        alignment = "Moderate mismatch"
    else:
        alignment = "High mismatch"

    # Risk
    if feasibility_score >= 80:
        risk = "Low"
    elif feasibility_score >= 60:
        risk = "Medium"
    else:
        risk = "High"

    return {
        "project_id": project.id,
        "genre": genre,
        "audience": audience,
        "scale": scale,
        "feasibility_score": feasibility_score,
        "cost_alignment": alignment,
        "risk_indicator": risk,
        "metrics": {
            "budget_score": budget_score,
            "talent_score": talent_score,
            "scale_score": scale_score
        }
    }
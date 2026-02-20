def compute_roi(feasibility_score: int, talent_strategy: str):
    """
    ROI probability for visualization charts.
    """

    roi = feasibility_score

    if talent_strategy == "Stars":
        roi += 10
    elif talent_strategy == "Newcomers":
        roi -= 10

    roi = max(25, min(95, roi))

    return {"roi_probability": roi}
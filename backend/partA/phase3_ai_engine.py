# backend/partA/phase3_ai_engine.py

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression


# ----- TRAIN LIGHTWEIGHT MODELS ONCE -----

# fake training data for hackathon realism
X_train = np.array([
    [40, 5, 8, 30, 2],
    [60, 6, 8, 50, 3],
    [30, 5, 6, 20, 1],
    [90, 6, 10, 80, 4],
])

y_days = np.array([42, 70, 28, 110])
y_delay = np.array([0, 1, 0, 1])

schedule_model = GradientBoostingRegressor()
schedule_model.fit(X_train, y_days)

delay_model = LogisticRegression()
delay_model.fit(X_train, y_delay)


# ----- MAIN ANALYSIS FUNCTION -----

def analyze_phase3(payload: dict):

    planned = payload.get("plannedShootDays", 40)
    days_week = payload.get("daysPerWeek", 5)
    hours_day = payload.get("hoursPerDay", 8)
    crew = payload.get("crewSize", 30)
    complexity = payload.get("complexityLevel", 2)
    progress = payload.get("currentProgressPercent", 0)
    actual = payload.get("actualShootDays")

    features = np.array([[planned, days_week, hours_day, crew, complexity]])

    # ---- predicted total schedule ----
    predicted_total = int(schedule_model.predict(features)[0])

    # ---- delay probability ----
    delay_prob = float(delay_model.predict_proba(features)[0][1])

    if delay_prob < 0.3:
        risk = "LOW"
    elif delay_prob < 0.6:
        risk = "MEDIUM"
    else:
        risk = "HIGH"

    # ---- production health ----
    health = "good"
    variance = 0

    if actual:
        variance = actual - planned

        if variance <= 0:
            health = "good"
        elif variance < 5:
            health = "atRisk"
        else:
            health = "critical"

    # ---- weekly plan ----
    weeks_needed = predicted_total / days_week
    weekly_target = predicted_total / max(1, weeks_needed)

    return {
        "recommendedTotalDays": predicted_total,
        "delayProbability": round(delay_prob, 2),
        "scheduleRisk": risk,
        "variance": variance,
        "productionHealth": health,
        "weeklyPlan": round(weekly_target, 1),
    }
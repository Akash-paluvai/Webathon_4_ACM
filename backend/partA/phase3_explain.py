"""
Phase 3 — Explainability (Groq-powered)
========================================
Generates AI explanation + feature importance for production decisions.
"""

import os
import re
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def explain_phase3(payload: dict, analysis_result: dict, project=None):
    """
    Groq-powered explainability for Phase 3 production analysis.
    """
    planned = payload.get("plannedShootDays", 40)
    days_week = payload.get("daysPerWeek", 5)
    crew = payload.get("crewSize", 30)
    complexity = payload.get("complexityLevel", 2)
    hours_day = payload.get("hoursPerDay", 8)

    project_info = ""
    if project:
        project_info = f"Film: {project.title} ({project.genre}), Scale: {project.scale}, Budget: {project.budget_level}, Talent: {project.talent_strategy}"

    prompt = f"""You are an AI production consultant explaining schedule predictions.

{project_info}

PRODUCTION INPUTS:
- Planned Shoot Days: {planned}
- Days Per Week: {days_week}
- Hours Per Day: {hours_day}
- Crew Size: {crew}
- Complexity Level: {complexity}/5

ANALYSIS RESULTS:
- Recommended Total Days: {analysis_result.get('recommendedTotalDays', planned)}
- Delay Probability: {analysis_result.get('delayProbability', 0.3)}
- Schedule Risk: {analysis_result.get('scheduleRisk', 'MEDIUM')}
- Production Health: {analysis_result.get('productionHealth', 'good')}

Return ONLY a valid JSON object:

{{
  "explanation": "<3-4 sentence paragraph explaining WHY the schedule prediction is what it is. Reference specific factors like complexity, crew size, genre demands. Be specific to this project.>",
  "featureImportance": {{
    "plannedShootDays": <float 0.0-1.0, how much this factor influenced the prediction>,
    "complexityLevel": <float 0.0-1.0>,
    "crewSize": <float 0.0-1.0>,
    "daysPerWeek": <float 0.0-1.0>,
    "hoursPerDay": <float 0.0-1.0>
  }}
}}

RULES:
1. Feature importance values must sum to approximately 1.0
2. The explanation must reference actual project details
3. Higher complexity = higher importance weight
4. Return ONLY the JSON"""

    try:
        response = _client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=400,
        )
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = re.sub(r'^```(?:json)?\s*', '', raw)
            raw = re.sub(r'\s*```$', '', raw)

        result = json.loads(raw)

        result.setdefault("explanation", "Analysis complete.")
        result.setdefault("featureImportance", {
            "plannedShootDays": 0.35,
            "complexityLevel": 0.30,
            "crewSize": 0.15,
            "daysPerWeek": 0.10,
            "hoursPerDay": 0.10,
        })

        # Clamp feature importance values
        fi = result["featureImportance"]
        for k in fi:
            fi[k] = round(max(0.0, min(1.0, float(fi[k]))), 2)

        return result

    except Exception as e:
        print(f"Groq phase3 explain error: {e}")
        return {
            "explanation": (
                f"The schedule prediction for this {complexity}/5 complexity production "
                f"is based on {planned} planned shoot days with a crew of {crew}. "
                f"Higher complexity increases delay risk and extends the timeline."
            ),
            "featureImportance": {
                "plannedShootDays": 0.35,
                "complexityLevel": 0.30,
                "crewSize": 0.15,
                "daysPerWeek": 0.10,
                "hoursPerDay": 0.10,
            },
        }
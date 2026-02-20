"""
Phase 3 — Production Intelligence (Groq-powered)
==================================================
Reads full project context (Phase 1 script analysis + Phase 2 packaging)
plus production parameters, sends to Groq for schedule prediction
and production health analysis.
"""

import os
import re
import json
from dotenv import load_dotenv
from groq import Groq
from models import Insight

load_dotenv()
_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def analyze_phase3(payload: dict, project=None, db=None):
    """
    Groq-powered production intelligence analysis.

    Args:
        payload: Production parameters (plannedShootDays, crewSize, etc.)
        project: FilmProject ORM object (Phase 1+2 data)
        db: DB session to read previous insights
    """
    planned = payload.get("plannedShootDays", 40)
    days_week = payload.get("daysPerWeek", 5)
    hours_day = payload.get("hoursPerDay", 8)
    crew = payload.get("crewSize", 30)
    complexity = payload.get("complexityLevel", 2)
    progress = payload.get("currentProgressPercent", 0)
    actual = payload.get("actualShootDays")

    # Gather all previous insights
    previous_insights = ""
    project_context = ""
    if project:
        project_context = f"""
- Title: {project.title}
- Genre: {project.genre}
- Theme: {project.theme}
- Scale: {project.scale}
- Budget Level: {project.budget_level}
- Talent Strategy: {project.talent_strategy}
- Audience Type: {project.audience_type}
- Production Health: {project.production_health}"""

        if db:
            insights = db.query(Insight).filter(
                Insight.project_id == project.id
            ).order_by(Insight.timestamp).all()
            previous_insights = "\n".join([i.content for i in insights])

    prompt = f"""You are an expert film production schedule analyst and production manager.

PROJECT CONTEXT (from Phase 1 & 2):
{project_context or 'No project context available'}

PREVIOUS PHASE INSIGHTS:
{previous_insights or 'No previous insights'}

PRODUCTION PARAMETERS:
- Planned Shoot Days: {planned}
- Days Per Week: {days_week}
- Hours Per Day: {hours_day}
- Crew Size: {crew}
- Complexity Level: {complexity}/5
- Current Progress: {progress}%
- Actual Shoot Days So Far: {actual or 'Not started'}

Analyze the production schedule considering the genre complexity, budget constraints, talent strategy, and these production parameters.

Return ONLY a valid JSON object:

{{
  "recommendedTotalDays": <integer, predicted total shoot days needed>,
  "delayProbability": <float 0.0-1.0, probability of schedule delay>,
  "scheduleRisk": "<LOW or MEDIUM or HIGH>",
  "productionHealth": "<good or atRisk or critical>",
  "variance": <integer, difference between actual and planned (0 if not started)>,
  "weeklyPlan": <float, recommended shoot days per week>
}}

RULES:
1. For a {project.genre if project else 'general'} film at complexity {complexity}/5:
   - Higher complexity = more days needed, higher delay probability
2. If actual shoot days > planned, production health should be atRisk or critical
3. Consider budget level and scale when predicting schedule
4. Large crew + high complexity = higher delay risk
5. Return ONLY the JSON"""

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

        # Validate and clamp
        result.setdefault("recommendedTotalDays", planned)
        result.setdefault("delayProbability", 0.3)
        result.setdefault("scheduleRisk", "MEDIUM")
        result.setdefault("productionHealth", "good")
        result.setdefault("variance", (actual - planned) if actual else 0)
        result.setdefault("weeklyPlan", days_week)

        result["recommendedTotalDays"] = max(1, int(result["recommendedTotalDays"]))
        result["delayProbability"] = round(max(0.0, min(1.0, float(result["delayProbability"]))), 2)
        result["weeklyPlan"] = round(max(1.0, float(result["weeklyPlan"])), 1)
        result["variance"] = int(result["variance"])

        return result

    except Exception as e:
        print(f"Groq phase3 error: {e}")
        variance = (actual - planned) if actual else 0
        health = "good" if variance <= 0 else ("atRisk" if variance < 5 else "critical")
        return {
            "recommendedTotalDays": planned,
            "delayProbability": 0.3,
            "scheduleRisk": "MEDIUM",
            "productionHealth": health,
            "variance": variance,
            "weeklyPlan": float(days_week),
        }
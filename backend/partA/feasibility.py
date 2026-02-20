"""
Phase 2 — Feasibility Analysis (Groq-powered)
===============================================
Reads project data (from Phase 1 DB) + Phase 1 insights,
sends everything to Groq for genuine feasibility analysis.
"""

import os
import re
import json
from dotenv import load_dotenv
from groq import Groq
from models import Insight

load_dotenv()
_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def compute_feasibility(project, payload: dict, db=None):
    """
    Groq-powered feasibility analysis using Phase 1 data + Phase 2 inputs.

    Args:
        project: FilmProject ORM object (has Phase 1 data)
        payload: dict with budgetLevel, talentStrategy
        db: optional DB session to read insights
    """
    budget = payload.get("budgetLevel", "Mid")
    talent = payload.get("talentStrategy", "Mixed")

    # Gather Phase 1 insights from DB
    phase1_insights = ""
    if db and project.id:
        insights = db.query(Insight).filter(
            Insight.project_id == project.id
        ).order_by(Insight.timestamp).all()
        phase1_insights = "\n".join([i.content for i in insights])

    prompt = f"""You are an expert film production feasibility analyst.

PROJECT CONTEXT (from Phase 1 Script Analysis):
- Title: {project.title}
- Genre: {project.genre}
- Language: {project.language}
- Theme: {project.theme}
- Scale: {project.scale}
- Audience Type: {project.audience_type}
- Production Health: {project.production_health}

PHASE 1 INSIGHTS:
{phase1_insights or 'No previous insights available'}

PHASE 2 INPUTS:
- Budget Level: {budget}
- Talent Strategy: {talent}

Analyze the feasibility of producing this film given the budget and talent strategy.
Consider how the Phase 1 script analysis (genre, audience, scale) affects production feasibility.

Return ONLY a valid JSON object with this EXACT structure:

{{
  "feasibility_score": <integer 0-100, overall production feasibility>,
  "risk_indicator": "<Low or Medium or High>",
  "cost_alignment": "<Aligned or Moderate mismatch or High mismatch — how well budget matches the scale>",
  "genre": "{project.genre}",
  "audience": "{project.audience_type}",
  "scale": "{project.scale}",
  "summary": "<2-3 sentence analysis of feasibility considering budget vs scale vs genre demands>",
  "metrics": {{
    "budget_score": <integer 0-100>,
    "talent_score": <integer 0-100>,
    "scale_score": <integer 0-100>
  }}
}}

RULES:
1. Scores must reflect THIS specific project's genre, scale, and budget combination
2. A Low budget + blockbuster scale = High mismatch, low feasibility
3. Stars talent + Thriller genre = higher audience pull, boost feasibility
4. Consider Phase 1 audience insights when scoring
5. Return ONLY the JSON"""

    try:
        response = _client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500,
        )
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = re.sub(r'^```(?:json)?\s*', '', raw)
            raw = re.sub(r'\s*```$', '', raw)

        result = json.loads(raw)

        # Ensure required fields
        result.setdefault("feasibility_score", 50)
        result.setdefault("risk_indicator", "Medium")
        result.setdefault("cost_alignment", "Moderate mismatch")
        result.setdefault("genre", project.genre)
        result.setdefault("audience", project.audience_type)
        result.setdefault("scale", project.scale)
        result.setdefault("summary", "Analysis completed.")
        result.setdefault("metrics", {"budget_score": 50, "talent_score": 50, "scale_score": 50})
        result["project_id"] = project.id

        # Clamp scores
        result["feasibility_score"] = max(0, min(100, int(result["feasibility_score"])))
        for k in ("budget_score", "talent_score", "scale_score"):
            if k in result.get("metrics", {}):
                result["metrics"][k] = max(0, min(100, int(result["metrics"][k])))

        return result

    except Exception as e:
        print(f"Groq feasibility error: {e}")
        return {
            "project_id": project.id,
            "feasibility_score": 50,
            "risk_indicator": "Medium",
            "cost_alignment": "Moderate mismatch",
            "genre": project.genre,
            "audience": project.audience_type,
            "scale": project.scale,
            "summary": "Analysis temporarily unavailable.",
            "metrics": {"budget_score": 50, "talent_score": 50, "scale_score": 50},
        }
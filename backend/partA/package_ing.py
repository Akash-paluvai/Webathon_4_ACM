"""
Phase 2 — Packaging Scenarios (Groq-powered)
==============================================
Compares Low/Mid/High budget × Newcomers/Mixed/Stars scenarios
using Groq for genuine analysis of each combination.
"""

import os
import re
import json
from dotenv import load_dotenv
from groq import Groq
from models import Insight

load_dotenv()
_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def evaluate_packaging(project, payload: dict, db=None):
    """
    Groq-powered packaging scenario comparison.
    """
    # Gather Phase 1 insights
    phase1_insights = ""
    if db and project.id:
        insights = db.query(Insight).filter(
            Insight.project_id == project.id
        ).order_by(Insight.timestamp).all()
        phase1_insights = "\n".join([i.content for i in insights])

    prompt = f"""You are an expert film packaging and investment analyst.

PROJECT CONTEXT:
- Title: {project.title}
- Genre: {project.genre}
- Theme: {project.theme}
- Scale: {project.scale}
- Audience Type: {project.audience_type}
- Production Health: {project.production_health}

PHASE 1 INSIGHTS:
{phase1_insights or 'No previous insights available'}

Compare these 3 production packaging scenarios for this film:

Scenario 1: Low Budget + Newcomers talent
Scenario 2: Mid Budget + Mixed talent
Scenario 3: High Budget + Stars talent

For each scenario, consider the genre, scale, audience, and Phase 1 analysis.

Return ONLY a valid JSON object:

{{
  "scenarios": [
    {{
      "budgetLevel": "Low",
      "talentStrategy": "Newcomers",
      "feasibility_score": <int 0-100>,
      "risk_indicator": "<Low or Medium or High>",
      "roi_probability": <int 0-100, return on investment probability>
    }},
    {{
      "budgetLevel": "Mid",
      "talentStrategy": "Mixed",
      "feasibility_score": <int 0-100>,
      "risk_indicator": "<Low or Medium or High>",
      "roi_probability": <int 0-100>
    }},
    {{
      "budgetLevel": "High",
      "talentStrategy": "Stars",
      "feasibility_score": <int 0-100>,
      "risk_indicator": "<Low or Medium or High>",
      "roi_probability": <int 0-100>
    }}
  ],
  "recommended_option": {{
    "budgetLevel": "<the best budget level>",
    "talentStrategy": "<the best talent strategy>",
    "feasibility_score": <matching score>,
    "risk_indicator": "<matching risk>",
    "roi_probability": <matching roi>
  }}
}}

RULES:
1. Scores must be specific to THIS project's genre and audience
2. For a {project.genre} film at {project.scale} scale targeting {project.audience_type}:
   - Consider which budget+talent combo works best
3. recommended_option should be the scenario with best ROI
4. Return ONLY the JSON"""

    try:
        response = _client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=600,
        )
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = re.sub(r'^```(?:json)?\s*', '', raw)
            raw = re.sub(r'\s*```$', '', raw)

        result = json.loads(raw)

        # Clamp all scores
        for s in result.get("scenarios", []):
            for k in ("feasibility_score", "roi_probability"):
                if k in s:
                    s[k] = max(0, min(100, int(s[k])))

        rec = result.get("recommended_option", {})
        for k in ("feasibility_score", "roi_probability"):
            if k in rec:
                rec[k] = max(0, min(100, int(rec[k])))

        return result

    except Exception as e:
        print(f"Groq packaging error: {e}")
        # Fallback
        scenarios = [
            {"budgetLevel": "Low", "talentStrategy": "Newcomers", "feasibility_score": 45, "risk_indicator": "High", "roi_probability": 40},
            {"budgetLevel": "Mid", "talentStrategy": "Mixed", "feasibility_score": 65, "risk_indicator": "Medium", "roi_probability": 60},
            {"budgetLevel": "High", "talentStrategy": "Stars", "feasibility_score": 80, "risk_indicator": "Low", "roi_probability": 75},
        ]
        return {"scenarios": scenarios, "recommended_option": scenarios[2]}
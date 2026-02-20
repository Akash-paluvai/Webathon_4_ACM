"""
Script Analysis Model - Groq LLM-powered script evaluation.
=============================================================
Accepts movie script text, sends it to Groq (llama-3.3-70b-versatile),
and returns structured JSON analysis matching the frontend field names.

No static data. Every script is individually analyzed by the LLM.
"""

import os
import re
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# -- Groq client (singleton) --
_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

_ANALYSIS_PROMPT = """You are an expert film industry analyst and script evaluator.

Analyze the following movie script/synopsis text. Consider the given genre, theme, and production scale.

SCRIPT:
{script_text}

METADATA:
- Genre: {genre}
- Theme: {theme}
- Scale: {scale}

Return ONLY a valid JSON object with this EXACT structure. No markdown, no explanation, no extra text:

{{
  "summary": "<3-4 sentence executive summary: describe the core concept, emotional/thematic strengths, market viability, and a clear recommendation. Be specific to THIS script.>",
  "feasibility_score": <integer 0-100, based on story quality, market potential, production complexity>,
  "risk_level": "<Low or Medium or High>",
  "genre_demand_band": "<High or Medium or Low, current market demand for this genre>",
  "audience": {{
    "recommended_segment": "<target audience description, e.g. Gen-Z mainstream commercial audience, Young adult entertainment audience, Niche festival audience, Family-friendly audience>",
    "generation": "<Gen-Z, Millennial, Gen-X, Mixed>",
    "audience_match_score": <integer 0-100>,
    "engagement_potential": <integer 0-100>,
    "sentiment_label": "<POSITIVE or NEGATIVE or MIXED>",
    "dominant_emotion": "<joy, fear, anger, sadness, surprise, disgust, anticipation, trust, neutral>",
    "sentiment_score": <float 0.0-1.0, how positive the overall tone is>
  }},
  "metrics": {{
    "confidence_score": <integer 0-100>,
    "top_themes": ["<theme1>", "<theme2>", "<theme3>"]
  }}
}}

RULES:
1. ALL scores must be specific to THIS script content - no generic defaults
2. Analyze the actual story, characters, themes, and narrative structure
3. Be honest - if the script is weak, reflect that in lower scores
4. The summary must reference actual content from the script
5. Return ONLY the JSON object, nothing else"""


def analyze_script_text(script_text: str, genre: str = "Drama", theme: str = "", scale: str = "studio") -> dict:
    """
    Analyze a movie script using Groq LLM and return structured JSON
    matching the exact field names the frontend expects.

    Args:
        script_text: Raw movie script or synopsis text
        genre: Film genre
        theme: Film theme
        scale: Production scale (indie/studio/blockbuster)

    Returns:
        dict matching frontend field expectations
    """
    if not script_text or not script_text.strip():
        raise ValueError("Script text cannot be empty")

    prompt = _ANALYSIS_PROMPT.format(
        script_text=script_text[:4000],
        genre=genre,
        theme=theme or "Not specified",
        scale=scale,
    )

    try:
        response = _client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=700,
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = re.sub(r'^```(?:json)?\s*', '', raw)
            raw = re.sub(r'\s*```$', '', raw)

        # Parse JSON
        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r'\{[\s\S]*\}', raw)
            if match:
                result = json.loads(match.group())
            else:
                raise ValueError(f"AI returned invalid JSON. Raw: {raw[:300]}")

        # Validate and clamp scores
        _validate_and_fix(result)
        return result

    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse AI response as JSON: {e}")
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Groq API error: {e}")


def _validate_and_fix(result: dict):
    """Ensure all required fields exist and scores are clamped."""
    # Top-level defaults
    result.setdefault("summary", "Analysis completed.")
    result.setdefault("feasibility_score", 50)
    result.setdefault("risk_level", "Medium")
    result.setdefault("genre_demand_band", "Medium")

    # Clamp feasibility
    if isinstance(result["feasibility_score"], (int, float)):
        result["feasibility_score"] = max(0, min(100, int(result["feasibility_score"])))

    # Audience defaults
    audience = result.setdefault("audience", {})
    audience.setdefault("recommended_segment", "General audience")
    audience.setdefault("generation", "Mixed")
    audience.setdefault("audience_match_score", 50)
    audience.setdefault("engagement_potential", 50)
    audience.setdefault("sentiment_label", "MIXED")
    audience.setdefault("dominant_emotion", "neutral")
    audience.setdefault("sentiment_score", 0.5)

    # Clamp audience scores
    for field in ("audience_match_score", "engagement_potential"):
        if isinstance(audience[field], (int, float)):
            audience[field] = max(0, min(100, int(audience[field])))

    # Ensure sentiment_score is float 0-1
    if isinstance(audience["sentiment_score"], (int, float)):
        audience["sentiment_score"] = round(max(0.0, min(1.0, float(audience["sentiment_score"]))), 2)

    # Metrics defaults
    metrics = result.setdefault("metrics", {})
    metrics.setdefault("confidence_score", result["feasibility_score"])
    metrics.setdefault("top_themes", [])

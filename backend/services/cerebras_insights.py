"""
Cerebras AI Strategic Insights for Phase 4

Calls the Cerebras API (OpenAI-compatible chat/completions endpoint)
to generate AI-driven marketing insights from trailer analysis data.

Uses ONLY the provided input context — no external data, no DB writes.
"""

import json
import os
import urllib.request
from typing import Any, Dict, Optional

_API_KEY = os.getenv("CEREBRAS_API_KEY", "")
_API_URL = "https://api.cerebras.ai/v1/chat/completions"

_SYSTEM_PROMPT = (
    "You are a senior film marketing strategist advising a producer before release. "
    "Respond in valid JSON only. No markdown, no code blocks, no extra text."
)

_USER_PROMPT_TEMPLATE = """Based ONLY on the following trailer analysis data, generate strategic insights.
Do not assume facts not present in the input.
Do not mention actors, budget numbers, or platforms unless implied by strategy.

INPUT DATA:
- Audience Type: {audience_type}
- Test Strategy: {test_strategy}
- Audience Interest Score: {interest_score}/100
- Trailer Features:
  - Pacing Score (avg shot length): {avg_shot_length} seconds
  - Scene Density (scene changes/sec): {scene_density}
  - Brightness Level: {brightness}/255
  - Audio Energy: {audio_energy}
  - Face Presence Ratio: {face_ratio}
  - Color Warmth: {color_warmth}
- VIDEO DYNAMICS (Derived):
  - Behavioral Dynamics: {behavioral_dynamics}
  - Violence Likelihood: {violence_likelihood}
  - Emotional Tone: {emotional_tone}
  - Genre Inclination: {genre_inclination}
- Risk Flags: {risk_flags}

Return EXACTLY this JSON structure:
{{
  "marketRead": "How audiences are likely to perceive this trailer (2-3 sentences)",
  "riskSignals": "Potential weaknesses that may affect market response (2-3 sentences)",
  "strategicRecommendations": "How to refine testing or positioning before release (2-3 sentences)"
}}"""


def generate_cerebras_insights(
    audience_type: str,
    test_strategy: str,
    audience_interest_score: int,
    trailer_features: Dict[str, Any],
    risk_flags: Optional[list] = None,
    enhanced_signals: Optional[Dict[str, Any]] = None,
) -> Dict[str, str]:
    """
    Call Cerebras API to generate AI-driven strategic insights.
    Returns dict with marketRead, riskSignals, strategicRecommendations.
    Falls back to error message on failure.
    """
    if not _API_KEY:
        return _fallback("Cerebras API key not configured")

    # Extract trailer feature values with safe defaults
    avg_shot = trailer_features.get("average_shot_length_sec", "N/A")
    scene_density = trailer_features.get("scene_change_frequency_per_sec", "N/A")
    brightness = trailer_features.get("average_brightness", "N/A")
    face_ratio = trailer_features.get("face_presence_ratio", "N/A")
    color_warmth = trailer_features.get("color_warmth", "N/A")

    audio_energy = "N/A"
    if trailer_features.get("audio_available", False):
        audio_energy = str(trailer_features.get("audio_energy_mean", "N/A"))

    # Extract enhanced signals
    enhanced = enhanced_signals or {}
    behavioral_dynamics = enhanced.get("behavioralDynamics", "Unknown")
    violence_likelihood = enhanced.get("violenceLikelihood", "LOW")
    emotional_tone = enhanced.get("emotionalTone", "NEUTRAL")
    genre_inclination = enhanced.get("genreInclination", "MIXED")

    user_prompt = _USER_PROMPT_TEMPLATE.format(
        audience_type=audience_type.upper(),
        test_strategy=test_strategy.upper(),
        interest_score=audience_interest_score,
        avg_shot_length=avg_shot,
        scene_density=scene_density,
        brightness=brightness,
        audio_energy=audio_energy,
        face_ratio=face_ratio,
        color_warmth=color_warmth,
        behavioral_dynamics=behavioral_dynamics,
        violence_likelihood=violence_likelihood,
        emotional_tone=emotional_tone,
        genre_inclination=genre_inclination,
        risk_flags=", ".join(risk_flags) if risk_flags else "None identified",
    )

    payload = json.dumps({
        "model": "llama-4-scout-17b-16e-instruct",
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": 500,
        "temperature": 0.4,
    }).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {_API_KEY}",
    }

    try:
        req = urllib.request.Request(_API_URL, data=payload, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        return _fallback(f"Cerebras API request failed: {str(e)}")

    # Parse the response
    try:
        content = data["choices"][0]["message"]["content"]
        # Strip any markdown code fences if present
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1] if "\n" in content else content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        parsed = json.loads(content)
        return {
            "marketRead": parsed.get("marketRead", "No market read available."),
            "riskSignals": parsed.get("riskSignals", "No risk signals identified."),
            "strategicRecommendations": parsed.get(
                "strategicRecommendations", "No recommendations available."
            ),
        }
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        return _fallback(f"Failed to parse Cerebras response: {str(e)}")


def _fallback(reason: str) -> Dict[str, str]:
    """Return a graceful fallback when AI generation fails."""
    return {
        "marketRead": f"AI insight generation unavailable ({reason}). Please retry later.",
        "riskSignals": "Unable to assess risk signals at this time.",
        "strategicRecommendations": "Unable to generate recommendations at this time.",
    }

import json
from .llm import generate_script_analysis
from .retriever import retrieve_similar


def analyze_script_and_audience(payload: dict):
    script_text = payload.get("scriptText", "")

    if not script_text:
        return {"error": "No script text provided"}

    # 🔎 STEP 1: RAG retrieval (similar films)
    similar_films = retrieve_similar(script_text)

    # 🧠 STEP 2: LLM reasoning
    llm_output = generate_script_analysis(script_text)

    try:
        data = json.loads(llm_output)
    except Exception:
        return {"error": "LLM returned invalid JSON", "raw": llm_output}

    # 🔎 attach RAG results
    data["similar_films"] = similar_films

    # ─────────────────────────────────────────
    # 🎯 STEP-2: CONCEPT EXPLORATION METRICS
    # ─────────────────────────────────────────

    feasibility = data.get("feasibility_score", 5)
    audience_affinity = data.get("audience_affinity", 5)
    risk_level = data.get("risk_level", "Medium")

    # genre demand band
    if feasibility >= 8:
        genre_band = "High"
    elif feasibility >= 5:
        genre_band = "Medium"
    else:
        genre_band = "Low"

    data["genre_demand_band"] = genre_band

    # numeric scoring for visuals
    risk_map = {
        "Low": 30,
        "Medium": 55,
        "Medium-High": 75,
        "High": 90
    }

    risk_score = risk_map.get(risk_level, 60)

    metrics = {
        "feasibility_score": feasibility * 10,
        "risk_score": risk_score,
        "genre_demand_score": feasibility * 10,
        "audience_score": audience_affinity * 10,
        "confidence_score": min(95, 60 + feasibility * 4)
    }

    data["metrics"] = metrics

    return data
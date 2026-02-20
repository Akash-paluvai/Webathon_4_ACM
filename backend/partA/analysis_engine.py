import json
from .retriever import retrieve_similar
from .socio_model import analyze_society
from .audience_model import compute_audience_metrics


def analyze_script_and_audience(payload: dict):
    script_text = payload.get("scriptText", "")

    if not script_text:
        return {"error": "No script text provided"}

    # ─────────────────────────────
    # 1️⃣ RAG RETRIEVAL
    # ─────────────────────────────
    similar_films = retrieve_similar(script_text)

    # ─────────────────────────────
    # 2️⃣ SOCIOLOGY MODEL
    # ─────────────────────────────
    socio_data = analyze_society(script_text)

    # ─────────────────────────────
    # 3️⃣ AUDIENCE MODEL
    # ─────────────────────────────
    audience_data = compute_audience_metrics(socio_data, similar_films)

    audience_score = audience_data["audience_score"]
    engagement = audience_data["engagement_potential"]

    # ─────────────────────────────
    # 4️⃣ CONCEPT SCORING
    # ─────────────────────────────
    feasibility_score = min(9, 5 + len(similar_films))

    if feasibility_score >= 8:
        risk_level = "Low"
    elif feasibility_score >= 6:
        risk_level = "Medium"
    else:
        risk_level = "High"

    genre_band = "High" if feasibility_score >= 8 else "Medium"

    # ─────────────────────────────
    # 5️⃣ GENERATION MAPPING
    # ─────────────────────────────
    generation = audience_data["generation"]

    generation_score_map = {
        "Gen-Z": 90,
        "Millennial": 70,
        "Gen-X": 50,
        "Mixed": 65
    }

    generation_score = generation_score_map.get(generation, 60)

    # ─────────────────────────────
    # 6️⃣ CLUSTER VISUALIZATION DATA
    # ─────────────────────────────
    cluster_data = {
        "x": audience_score,
        "y": feasibility_score * 10,
        "label": audience_data["recommended_segment"]
    }

    # ─────────────────────────────
    # 7️⃣ FINAL OUTPUT
    # ─────────────────────────────
    result = {
        "summary": "Concept + audience analysis complete",
        "genre": payload.get("genre", "Unknown"),
        "feasibility_score": feasibility_score,
        "risk_level": risk_level,
        "genre_demand_band": genre_band,
        "similar_films": similar_films,

        # 🎯 Step-3 Audience Output
        "audience": {
            "recommended_segment": audience_data["recommended_segment"],
            "audience_match_score": audience_score,
            "generation": generation,
            "generation_score": generation_score,
            "engagement_potential": engagement,
            "cluster": cluster_data
        },

        # 📊 Visualization Metrics
        "metrics": {
            "risk_score": 90 if risk_level == "High" else 60,
            "audience_score": audience_score,
            "engagement_score": engagement,
            "genre_demand_score": feasibility_score * 10,
            "confidence_score": 70 + feasibility_score * 2
        }
    }

    return result
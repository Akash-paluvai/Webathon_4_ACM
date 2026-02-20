import numpy as np

def compute_audience_metrics(socio_data, similar_films):
    sentiment = socio_data["sentiment"]
    emotion = socio_data["emotion"]

    base_score = 50

    if sentiment == "POSITIVE":
        base_score += 10

    if emotion in ["suspense", "fear"]:
        base_score += 15

    if len(similar_films) >= 3:
        base_score += 10

    audience_score = min(95, base_score)

    if audience_score > 80:
        segment = "Urban Gen-Z thriller audience"
    elif audience_score > 60:
        segment = "Young adults"
    else:
        segment = "Niche audience"

    return {
        "audience_score": audience_score,
        "recommended_segment": segment,
        "engagement_potential": int(audience_score * 0.8),
        "generation": "Gen-Z" if audience_score > 70 else "Millennial"
    }
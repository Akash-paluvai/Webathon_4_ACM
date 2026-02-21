"""
Piracy Signal Engine — Safe Proxy Estimation.

Estimates piracy exposure risk from project metadata heuristics.
No scraping of illegal sites. Purely deterministic, no external APIs.
"""

from typing import Dict


# ── Piracy risk factor tables ────────────────────────────────

_GENRE_PIRACY_RISK = {
    "action": 0.8, "thriller": 0.7, "comedy": 0.5, "horror": 0.65,
    "romance": 0.35, "drama": 0.4, "sci-fi": 0.75, "fantasy": 0.7,
    "documentary": 0.2, "animation": 0.55, "crime": 0.65,
    "mystery": 0.5, "adventure": 0.7, "musical": 0.3,
}

_SCALE_PIRACY_RISK = {
    "tentpole": 0.9, "big_budget": 0.8, "large": 0.8,
    "mid_budget": 0.55, "medium": 0.55,
    "indie": 0.25, "small": 0.3, "micro": 0.15,
}

_LANGUAGE_PIRACY_RISK = {
    "hindi": 0.8, "english": 0.7, "tamil": 0.65, "telugu": 0.65,
    "malayalam": 0.5, "kannada": 0.45, "bengali": 0.5,
    "marathi": 0.4, "punjabi": 0.35, "spanish": 0.6,
    "korean": 0.55, "japanese": 0.5, "mandarin": 0.6,
}

_RELEASE_MODE_PIRACY = {
    "theatre": 0.5, "ott": 0.75, "hybrid": 0.65,
    "festival_circuit": 0.3,
}


def compute_piracy_signal(intel: Dict) -> Dict:
    """
    Estimate piracy exposure risk (0–1).

    Formula:
      PiracySignal = 0.30 * genre_risk + 0.25 * scale_risk
                   + 0.20 * language_risk + 0.15 * release_mode_risk
                   + 0.10 * hype_factor

    Higher values → higher piracy risk → paradoxically may indicate
    higher demand (popular content gets pirated more).

    Returns:
        {
            score: float,         # 0–1
            level: str,           # low / medium / high
            factors: {...},       # contributing risk factors
            demand_signal: float, # piracy-as-demand-proxy (inverted)
        }
    """
    genre = (intel.get("genre") or "drama").lower()
    scale = (intel.get("scale") or "medium").lower()
    language = (intel.get("language") or "hindi").lower()
    release_mode = (intel.get("release_mode") or "ott").lower()
    hype = intel.get("hype_momentum", 0.5)

    genre_risk = _GENRE_PIRACY_RISK.get(genre, 0.5)
    scale_risk = _SCALE_PIRACY_RISK.get(scale, 0.5)
    language_risk = _LANGUAGE_PIRACY_RISK.get(language, 0.5)
    release_risk = _RELEASE_MODE_PIRACY.get(release_mode, 0.5)

    # Hype increases piracy risk (popular → pirated)
    hype_factor = min(1.0, hype * 1.2)

    score = (
        0.30 * genre_risk
        + 0.25 * scale_risk
        + 0.20 * language_risk
        + 0.15 * release_risk
        + 0.10 * hype_factor
    )
    score = round(max(0.0, min(1.0, score)), 4)

    level = (
        "high" if score >= 0.65 else
        "medium" if score >= 0.40 else
        "low"
    )

    # As a demand signal, piracy risk is actually a positive indicator
    # (popular things get pirated more). We invert for DSI contribution.
    demand_signal = round(score * 0.8, 4)  # slightly dampened

    factors = {
        "genre_risk": round(genre_risk, 4),
        "scale_risk": round(scale_risk, 4),
        "language_risk": round(language_risk, 4),
        "release_mode_risk": round(release_risk, 4),
        "hype_factor": round(hype_factor, 4),
    }

    # Risk mitigation suggestions
    mitigations = []
    if release_risk >= 0.7:
        mitigations.append("OTT-first release increases piracy window — consider staggered release")
    if genre_risk >= 0.7:
        mitigations.append(f"High-piracy genre ({genre}) — invest in early digital availability")
    if scale_risk >= 0.7:
        mitigations.append("Big-budget films attract more piracy — prioritize day-1 global availability")
    if hype_factor >= 0.7:
        mitigations.append("High hype increases piracy incentive — ensure strong anti-cam measures")
    if not mitigations:
        mitigations.append("Piracy risk is manageable — standard protections sufficient")

    return {
        "score": score,
        "level": level,
        "demand_signal": demand_signal,
        "factors": factors,
        "mitigations": mitigations,
    }

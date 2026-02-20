"""
Phase 6 → Phase 7 Data Bridge.

Consumes the Phase 6 pipeline output and normalizes all values to 0–1
for downstream Phase 7 engines. This is the SINGLE integration point
so Phase 7 never duplicates Phase 6 logic.
"""

from typing import Dict
from sqlalchemy.orm import Session


def fetch_phase6_intel(project_id: int, db: Session) -> Dict:
    """
    Run the Phase 6 pipeline and normalize everything into
    the Phase 7 data contract.
    """
    from models import FilmProject
    from phase6.routes import _run_full_pipeline

    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise ValueError(f"Project {project_id} not found")

    pipeline = _run_full_pipeline(project, db)

    top = pipeline["top"]
    top_region = pipeline["top_region"]
    leverage = pipeline["leverage_result"]
    release = pipeline["release_result"]
    dubbing = pipeline["dubbing_result"]
    signals = pipeline["signals"]
    cdi = pipeline["cdi_result"]
    competition_intel = pipeline.get("competition_intel", {})
    release_timing = pipeline.get("release_timing", {})

    # Dubbing gain
    recs = dubbing.get("recommendations", [])
    dubbing_gain = round(
        sum(r.get("estimated_roi_uplift", 0) for r in recs) / max(1, len(recs)), 4
    ) if recs else 0.0

    # Release mode bias → algorithm exposure proxy
    mode = release.get("mode", "ott")
    release_mode_bias = {
        "theatre": 0.4, "ott": 0.75, "hybrid": 0.6, "festival_circuit": 0.3,
    }.get(mode, 0.5)

    # Regional strength = top region's normalized score
    regional_strength = top_region.get("normalized_score", 0.5)

    # Engagement velocity from signals
    per_region = signals.get("per_region", []) if isinstance(signals, dict) else (signals if isinstance(signals, list) else [])
    velocities = [s.get("engagement_velocity", 0.5) for s in per_region if isinstance(s, dict)]
    avg_velocity = round(sum(velocities) / max(1, len(velocities)), 4) if velocities else 0.5

    # Sentiment
    sentiments = [s.get("sentiment", 0.5) for s in per_region if isinstance(s, dict)]
    avg_sentiment = round(sum(sentiments) / max(1, len(sentiments)), 4) if sentiments else 0.5

    return {
        "project_id": project_id,
        "project": project,
        "genre": project.genre,
        "language": project.language,
        "scale": project.scale,
        "budget_level": project.budget_level,
        "audience_type": project.audience_type,
        "release_model": project.release_model,
        "title": project.title,

        # Normalized signals (0–1)
        "platform_fit": round(top["fit_score"], 4),
        "top_platform": top["platform"],
        "regional_strength": regional_strength,
        "hype_momentum": pipeline["hype_momentum"],
        "cdi": cdi.get("cdi", 0.5),
        "release_mode_bias": release_mode_bias,
        "dubbing_gain": min(1.0, dubbing_gain),
        "leverage": leverage["leverage_score"],
        "leverage_level": leverage["level"],

        # Extended data
        "release_timing": release_timing,
        "release_timing_score": release_timing.get("best_score", 0.5),
        "competition_intel": competition_intel,
        "competition_by_month": competition_intel.get("competition_by_month", {}),
        "avg_engagement_velocity": avg_velocity,
        "avg_sentiment": avg_sentiment,
        "release_mode": mode,
        "readiness": pipeline["readiness"],
        "signals": {"per_region": per_region} if isinstance(signals, list) else signals,
        "normalized_regions": pipeline["normalized_regions"],
        "top_regions": pipeline["top_regions"],
        "ranked_platforms": pipeline["ranked"],
        "dubbing_result": dubbing,
        "deals": pipeline["deals"],
    }

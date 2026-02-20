"""
Trust & Confidence Layer.

Provides decision reliability: confidence band, data quality,
sensitivity to parameter change, worst-case discoverability.
"""

from typing import Dict


def compute_confidence(intel: Dict, discoverability_score: float, sensitivity_total: float) -> Dict:
    """
    Assess confidence in the discoverability prediction.

    Returns: {confidence, data_quality, sensitivity, worst_case_discoverability,
              confidence_band, reliability_grade}
    """
    # Data quality = how many live signals vs heuristic
    signals = intel.get("signals", {})
    per_region = signals.get("per_region", [])
    live_count = sum(1 for s in per_region if s.get("source") == "live")
    total_signals = max(1, len(per_region))
    data_quality = round(0.4 + 0.6 * (live_count / total_signals), 4)

    # Sensitivity (lower = more confident)
    sensitivity = min(1.0, sensitivity_total)

    # Confidence = data quality weighted against sensitivity
    confidence = round(min(1.0,
        0.50 * data_quality
        + 0.30 * (1.0 - sensitivity)
        + 0.20 * intel.get("readiness", 0.5)
    ), 4)

    # Worst case = score minus 2x sensitivity band
    worst_case = round(max(0.0, discoverability_score - 2 * sensitivity), 4)

    # Confidence band
    band_low = round(max(0.0, discoverability_score - sensitivity), 4)
    band_high = round(min(1.0, discoverability_score + sensitivity), 4)

    grade = (
        "A" if confidence >= 0.75 else
        "B" if confidence >= 0.60 else
        "C" if confidence >= 0.45 else
        "D"
    )

    return {
        "confidence": confidence,
        "data_quality": data_quality,
        "sensitivity": round(sensitivity, 4),
        "worst_case_discoverability": worst_case,
        "confidence_band": {"low": band_low, "high": band_high},
        "reliability_grade": grade,
    }

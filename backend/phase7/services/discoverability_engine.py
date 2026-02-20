"""
Core Discoverability Engine.

Discoverability =
    0.20 * PlatformFit
  + 0.18 * HypeMomentum
  + 0.15 * RegionalReach
  + 0.14 * ReleaseTiming
  + 0.10 * AlgorithmExposure
  + 0.08 * DubbingExpansion
  + 0.07 * CampaignIntensity
  − 0.18 * CompetitionSuppression
"""

import hashlib
from typing import Dict


def compute_discoverability(intel: Dict, campaign_intensity: float = 0.5) -> Dict:
    """
    Core discoverability score from Phase 6 normalized intel.

    Args:
        intel: Phase 6 bridge output.
        campaign_intensity: 0-1, how aggressively the campaign is being run.

    Returns: {score, breakdown, confidence, grade}
    """
    pf = intel.get("platform_fit", 0.5)
    hm = intel.get("hype_momentum", 0.5)
    rr = intel.get("regional_strength", 0.5)
    rt = intel.get("release_timing_score", 0.5)
    ae = intel.get("release_mode_bias", 0.5)
    de = min(1.0, intel.get("dubbing_gain", 0.0))
    ci = campaign_intensity
    cs = intel.get("cdi", 0.5)

    score = (
        0.20 * pf
        + 0.18 * hm
        + 0.15 * rr
        + 0.14 * rt
        + 0.10 * ae
        + 0.08 * de
        + 0.07 * ci
        - 0.18 * cs
    )
    score = round(max(0.0, min(1.0, score)), 4)

    grade = (
        "A+" if score >= 0.80 else
        "A" if score >= 0.70 else
        "B+" if score >= 0.60 else
        "B" if score >= 0.50 else
        "C" if score >= 0.40 else
        "D" if score >= 0.30 else "F"
    )

    return {
        "score": score,
        "grade": grade,
        "breakdown": {
            "platform_fit": round(0.20 * pf, 4),
            "hype_momentum": round(0.18 * hm, 4),
            "regional_reach": round(0.15 * rr, 4),
            "release_timing": round(0.14 * rt, 4),
            "algorithm_exposure": round(0.10 * ae, 4),
            "dubbing_expansion": round(0.08 * de, 4),
            "campaign_intensity": round(0.07 * ci, 4),
            "competition_suppression": round(-0.18 * cs, 4),
        },
    }


def compute_sensitivity(intel: Dict, campaign_intensity: float = 0.5) -> Dict:
    """
    Sensitivity analysis: how much does discoverability change
    when each input shifts ±10%.
    """
    base = compute_discoverability(intel, campaign_intensity)["score"]
    fields = [
        ("platform_fit", "platform_fit"),
        ("hype_momentum", "hype_momentum"),
        ("regional_strength", "regional_strength"),
        ("release_timing_score", "release_timing"),
        ("release_mode_bias", "algorithm_exposure"),
        ("dubbing_gain", "dubbing_expansion"),
        ("cdi", "competition"),
    ]
    sensitivities = {}
    for field, label in fields:
        modified = dict(intel)
        original = modified.get(field, 0.5)
        modified[field] = min(1.0, original * 1.1)
        up = compute_discoverability(modified, campaign_intensity)["score"]
        modified[field] = max(0.0, original * 0.9)
        down = compute_discoverability(modified, campaign_intensity)["score"]
        sensitivities[label] = round(abs(up - down), 4)

    # Campaign sensitivity
    up_c = compute_discoverability(intel, min(1.0, campaign_intensity * 1.1))["score"]
    dn_c = compute_discoverability(intel, max(0.0, campaign_intensity * 0.9))["score"]
    sensitivities["campaign"] = round(abs(up_c - dn_c), 4)

    most_sensitive = max(sensitivities, key=sensitivities.get)
    total_sensitivity = round(sum(sensitivities.values()), 4)

    return {
        "base_score": base,
        "sensitivities": sensitivities,
        "most_sensitive_factor": most_sensitive,
        "total_sensitivity": total_sensitivity,
    }


def simulate_scenario(intel: Dict, overrides: Dict) -> Dict:
    """
    Simulate discoverability with parameter overrides.

    overrides: {field: new_value} for any Phase 6 bridge fields.
    """
    base = compute_discoverability(intel)
    modified = dict(intel)
    modified.update(overrides)
    campaign = overrides.get("campaign_intensity", 0.5)
    new = compute_discoverability(modified, campaign)

    delta = round(new["score"] - base["score"], 4)
    return {
        "original_score": base["score"],
        "original_grade": base["grade"],
        "simulated_score": new["score"],
        "simulated_grade": new["grade"],
        "delta": delta,
        "impact": (
            "Strong positive" if delta > 0.08 else
            "Positive" if delta > 0.03 else
            "Neutral" if delta > -0.03 else
            "Negative" if delta > -0.08 else
            "Strong negative"
        ),
        "overrides_applied": overrides,
    }

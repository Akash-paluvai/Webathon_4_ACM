"""
Phase-4 Rule-Based Insight Generator
Deterministic, template-driven insights — no LLM, no API keys.
Uses expert-system reasoning over trailer features + project context.
"""

from typing import Any, Dict, List


def generate_phase4_insights(
    scale: str,
    production_health: str,
    audience_type: str,
    audience_interest_score: int,
    test_strategy: str,
    trailer_features: Dict[str, Any],
) -> List[str]:
    """
    Generate 3-5 actionable insights for Phase-4 based on deterministic rules.
    All inputs are plain values — no DB access, no AI.
    """
    insights: List[str] = []

    # ── 1. Audience-fit assessment ──────────────────────────
    _audience_fit(insights, scale, audience_type, audience_interest_score)

    # ── 2. Trailer pacing analysis ─────────────────────────
    _trailer_pacing(insights, audience_type, trailer_features)

    # ── 3. Visual tone — brightness ────────────────────────
    _visual_tone(insights, trailer_features)

    # ── 4. Audio energy check ──────────────────────────────
    _audio_energy(insights, audience_type, trailer_features)

    # ── 5. Production health warning ───────────────────────
    _health_warning(insights, production_health, audience_interest_score)

    # ── 6. Test strategy recommendation ────────────────────
    _test_strategy_rec(insights, test_strategy, audience_type, audience_interest_score)

    return insights


# ── Helper rule functions ──────────────────────────────────

def _audience_fit(
    out: List[str], scale: str, audience_type: str, score: int
) -> None:
    scale_l = scale.strip().lower()
    label = audience_type.upper()

    if score >= 80:
        out.append(
            f"Strong audience fit ({label}, score {score}/100). "
            f"The project's {scale_l} scale aligns well with the target audience — "
            f"consider accelerating marketing ramp-up."
        )
    elif score >= 60:
        out.append(
            f"Moderate audience fit ({label}, score {score}/100). "
            f"The {scale_l}-scale project has reasonable market potential, but "
            f"targeted positioning will be important to close the gap."
        )
    else:
        out.append(
            f"Weak audience fit ({label}, score {score}/100). "
            f"Consider revisiting the target audience definition or re-editing "
            f"the trailer to better align with {label} viewer expectations."
        )


def _trailer_pacing(
    out: List[str], audience_type: str, features: Dict[str, Any]
) -> None:
    avg_shot = features.get("average_shot_length_sec", 0.0)
    scene_freq = features.get("scene_change_frequency_per_sec", 0.0)
    aud = audience_type.lower()

    if aud == "mass" and avg_shot > 4.0:
        out.append(
            f"Trailer pacing may be too slow for a MASS audience "
            f"(avg shot {avg_shot:.1f}s). Consider tightening edits to under "
            f"3 seconds per shot to increase engagement."
        )
    elif aud == "niche" and scene_freq > 0.8:
        out.append(
            f"High scene-change frequency ({scene_freq:.2f}/s) could feel "
            f"frenetic for a NICHE audience. Longer, more deliberate shots "
            f"tend to resonate better with this segment."
        )
    elif scene_freq > 0:
        out.append(
            f"Trailer pacing is within expected range for {aud.upper()} viewers "
            f"(avg shot {avg_shot:.1f}s, {scene_freq:.2f} cuts/s). "
            f"The editing rhythm should hold audience attention effectively."
        )


def _visual_tone(out: List[str], features: Dict[str, Any]) -> None:
    brightness = features.get("average_brightness", -1.0)
    if brightness < 0:
        return

    if brightness < 80:
        out.append(
            f"The trailer has a dark visual tone (avg brightness {brightness:.0f}/255). "
            f"This works well for thrillers and dramas, but verify it's not "
            f"hindering readability on mobile screens."
        )
    elif brightness > 180:
        out.append(
            f"The trailer is quite bright (avg brightness {brightness:.0f}/255). "
            f"Bright visuals suit comedies and family films — ensure key "
            f"dramatic moments still carry visual weight."
        )
    else:
        out.append(
            f"The trailer maintains a balanced visual tone (avg brightness {brightness:.0f}/255), "
            f"which supports comfortable viewing and broad audience accessibility."
        )


def _audio_energy(
    out: List[str], audience_type: str, features: Dict[str, Any]
) -> None:
    if not features.get("audio_available", False):
        out.append(
            "Audio analysis unavailable — ensure ffmpeg is installed and the "
            "trailer contains an audio track for a complete assessment."
        )
        return

    energy = features.get("audio_energy_mean", 0.0)
    aud = audience_type.lower()

    if energy > 0.1 and aud == "mass":
        out.append(
            f"High audio energy (mean RMS {energy:.4f}) supports the "
            f"high-impact feel expected by MASS audiences. "
            f"The soundtrack intensity should translate well to theatrical release."
        )
    elif energy < 0.02:
        out.append(
            f"Low audio energy detected (mean RMS {energy:.4f}). "
            f"Consider boosting the trailer's sound design — a punchier mix "
            f"typically improves audience retention in test screenings."
        )


def _health_warning(
    out: List[str], production_health: str, score: int
) -> None:
    health = production_health.strip().lower()
    if health in ("atrisk", "at_risk"):
        out.append(
            f"⚠ Production health is AT RISK (interest score penalised to {score}/100). "
            f"Address outstanding production issues before committing to a wide "
            f"test strategy — unresolved risks will erode audience confidence."
        )
    elif health == "critical":
        out.append(
            f"🚨 Production health is CRITICAL. Market testing results may not "
            f"be reliable until core production issues are resolved. "
            f"Recommend pausing audience testing until health improves."
        )


def _test_strategy_rec(
    out: List[str],
    strategy: str,
    audience_type: str,
    score: int,
) -> None:
    strat = strategy.strip().upper()
    aud = audience_type.lower()

    if strat == "FESTIVAL" and aud == "mass":
        out.append(
            "Festival screenings are an unusual choice for a MASS audience project. "
            "Consider adding a DIGITAL pre-release test to gauge broader appeal "
            "before committing to the festival circuit."
        )
    elif strat == "DIGITAL" and aud == "niche":
        out.append(
            "Digital-first testing may dilute the exclusivity that NICHE audiences value. "
            "A PRIVATE screening or festival premiere could generate stronger "
            "word-of-mouth within the target community."
        )
    elif strat == "PRIVATE" and score >= 80:
        out.append(
            f"Strong interest score ({score}/100) suggests the trailer is ready "
            f"for a wider test. Consider supplementing the PRIVATE screening "
            f"with a DIGITAL campaign to maximise early buzz."
        )
    else:
        out.append(
            f"The selected {strat} test strategy aligns reasonably with the "
            f"film's current {aud.upper()} audience profile and market readiness."
        )

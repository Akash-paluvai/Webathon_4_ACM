"""
Pitch Pack Generator — creates a structured exportable pitch pack JSON.

Contains all essential information a producer needs for deal presentations:
  - Audience match analysis
  - 30-day predicted reach
  - Regional heatmap data
  - Dubbing expansion insights
  - Competitive advantage summary
  - Trailer tone recommendation
  - Deal recommendation
"""

from typing import Dict, List, Optional


# ── Trailer tone recommendations by genre/audience ──────────
TRAILER_TONES = {
    "Action": "High-energy, fast cuts, bass-heavy soundtrack — focus on spectacle and star power",
    "Drama": "Emotional, slow-burn reveal, character-driven with award-season positioning",
    "Comedy": "Punchy, quotable moments, bright palette — lean into social shareability",
    "Horror": "Tension-building, minimal dialogue, jump-scare teaser — let mystery sell",
    "Thriller": "Dark, suspenseful, unreliable narrator vibe — don't reveal the twist",
    "Romance": "Warm tones, chemistry-focused, feel-good music — target date-night audience",
    "Sci-Fi": "Visual spectacle, world-building reveals, epic score — sell the universe",
    "Documentary": "Powerful real footage, subject-driven, social impact messaging",
    "Animation": "Vibrant, family-friendly, humor + heart balance — show broad appeal",
}


def generate_pitch_pack(
    project_title: str,
    genre: str,
    language: str,
    platform_fit_result: Dict,
    regional_hype_result: Dict,
    dubbing_result: Dict,
    leverage_result: Dict,
    release_mode_result: Dict,
    deal_options: List[Dict],
    readiness_score: float,
    signals: Optional[List[Dict]] = None,
) -> Dict:
    """
    Generate a comprehensive pitch pack for the film project.

    Returns a structured dict ready for PDF/JSON export.
    """
    top_platform = platform_fit_result.get("recommended_platform", "N/A")
    top_score = platform_fit_result.get("recommended_score", 0)
    top_region = regional_hype_result.get("top_region", "N/A")
    regions = regional_hype_result.get("regions", [])
    rankings = platform_fit_result.get("rankings", [])

    # Audience match %
    audience_match_pct = round(top_score * 100, 1)

    # Predicted 30-day reach (millions)
    reach_30day = round(top_score * 120, 1)

    # Top 3 regions
    top_regions = [r["region"] for r in regions[:3]] if regions else []

    # Dubbing expansion
    dub_languages = []
    dubbing_gain_pct = 0
    if dubbing_result.get("needs_dubbing"):
        recs = dubbing_result.get("recommendations", [])
        dub_languages = [r["target_language"] for r in recs if r["priority"] == "high"]
        dubbing_gain_pct = round(
            sum(r.get("estimated_roi_uplift", 0) for r in recs) / max(1, len(recs)), 1
        )

    # Competitive advantage
    advantages = []
    if leverage_result.get("leverage_score", 0) > 0.5:
        advantages.append(f"Strong negotiation leverage ({leverage_result['level']})")
    if top_score > 0.65:
        advantages.append(f"High platform fit for {top_platform} ({audience_match_pct}%)")
    if len(top_regions) >= 2:
        advantages.append(f"Multi-region demand: {', '.join(top_regions[:3])}")
    if dubbing_gain_pct > 10:
        advantages.append(f"Dubbing expansion potential (+{dubbing_gain_pct}% reach)")
    if signals:
        avg_ris = sum(s.get("RIS", 0) for s in signals) / max(1, len(signals))
        if avg_ris > 0.5:
            advantages.append(f"Strong digital signals (avg RIS: {round(avg_ris * 100)}%)")

    # Deal recommendation
    best_deal = deal_options[0] if deal_options else {}
    deal_summary = {}
    if best_deal:
        mg = best_deal.get("minimum_guarantee_range", [0, 0])
        deal_summary = {
            "platform": best_deal.get("platform", "N/A"),
            "minimum_guarantee": f"${mg[0]:.0f}K – ${mg[1]:.0f}K",
            "revenue_share": f"{best_deal.get('revenue_share_pct', 0):.1f}%",
            "exclusivity": f"{best_deal.get('exclusivity_window_months', 0)} months",
            "strategy": best_deal.get("recommended_strategy", ""),
        }

    # Trailer tone
    trailer_tone = TRAILER_TONES.get(genre, "Customize based on target demographic and platform")

    # Release mode probabilities
    probabilities = release_mode_result.get("probabilities", {})

    return {
        "title": project_title,
        "genre": genre,
        "language": language,
        "generated_at": "auto",

        "executive_summary": {
            "audience_match_pct": audience_match_pct,
            "predicted_30day_reach_millions": reach_30day,
            "recommended_platform": top_platform,
            "recommended_release_mode": release_mode_result.get("mode", "N/A"),
            "readiness_score": round(readiness_score * 100, 1),
            "leverage_level": leverage_result.get("level", "N/A"),
        },

        "platform_analysis": {
            "top_platform": top_platform,
            "fit_score": top_score,
            "all_rankings": [
                {
                    "platform": r.get("platform", ""),
                    "fit_score": r.get("fit_score", 0),
                    "reasoning": r.get("reasoning", []),
                }
                for r in rankings[:4]
            ],
        },

        "regional_demand": {
            "top_regions": top_regions,
            "region_scores": [
                {"region": r["region"], "score": r.get("interest_score", 0), "tier": r.get("tier", "")}
                for r in regions
            ],
        },

        "dubbing_expansion": {
            "recommended": dubbing_result.get("needs_dubbing", False),
            "priority_languages": dub_languages,
            "avg_roi_uplift_pct": dubbing_gain_pct,
            "cost_tier": dubbing_result.get("estimated_total_cost_tier", "N/A"),
        },

        "release_mode": {
            "recommended": release_mode_result.get("mode", "N/A"),
            "probabilities": probabilities,
        },

        "competitive_advantage": advantages,
        "trailer_tone": trailer_tone,

        "deal_recommendation": deal_summary,

        "leverage": {
            "score": leverage_result.get("leverage_score", 0),
            "level": leverage_result.get("level", "N/A"),
            "strategy_hint": leverage_result.get("strategy_hint", ""),
        },
    }

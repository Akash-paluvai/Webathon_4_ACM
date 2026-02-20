"""
Phase 6 Routes — Distribution Strategy & Negotiation

Endpoints:
    POST /phase6/analyze                  — Full Phase 6 analysis (signal-enhanced)
    POST /phase6/platform-fit             — Platform fit rankings only
    POST /phase6/regional-demand          — Regional interest + signals
    POST /phase6/dubbing-analysis         — Dubbing recommendations
    POST /phase6/deal-benchmark           — Deal terms + industry benchmarks
    POST /phase6/pitch-pack              — Exportable pitch pack JSON
    POST /phase6/intelligence            — Normalized intelligence feed for Phase 7
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import FilmProject
from phase6_schemas import (
    PlatformFitResponse,
    PlatformScore,
    RegionalHypeResponse,
    RegionScore,
    SignalData,
    DubbingResponse,
    DubbingRecommendation,
    DealResponse,
    DealTerms,
    LeverageResponse,
    LeverageBreakdown,
    Phase6AnalysisResponse,
)
from phase6.services.signal_aggregator import compute_signals, get_top_regions, compute_hype_momentum
from phase6.services.platform_fit import calculate_platform_fit, calculate_platform_fit_v2, rank_platforms
from phase6.services.regional_analysis import (
    compute_regional_interest,
    compute_regional_interest_with_signals,
    normalize_scores,
)
from phase6.services.dubbing_engine import analyze_dubbing_need
from phase6.services.deal_engine import compute_negotiation_leverage, generate_deal_terms
from phase6.services.release_classifier import classify_release_mode, classify_release_mode_with_probabilities
from phase6.services.leverage_engine import compute_leverage, compute_dubbing_expansion_potential
from phase6.services.competition_density import compute_cdi, cdi_penalty
from phase6.services.competition_engine import compute_competition_intel
from phase6.services.release_timing_engine import compute_release_scores, simulate_release_shift
from phase6.services.calendar_engine import get_festival_calendar, get_monthly_engagement_index
from phase6.services.pitch_pack import generate_pitch_pack
from phase6.ml.feature_builder import build_feature_vector
from phase6.ml.model_loader import predict, rule_based_readiness

router = APIRouter()


# ── Helpers ───────────────────────────────────────────────────

def _get_project(project_id: int, db: Session) -> FilmProject:
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Film project not found")
    return project


def _project_to_dict(project: FilmProject) -> dict:
    return {
        "id": project.id,
        "title": project.title,
        "currentPhase": project.current_phase,
        "genre": project.genre,
        "language": project.language,
        "theme": project.theme,
        "scale": project.scale,
        "budgetLevel": project.budget_level,
        "talentStrategy": project.talent_strategy,
        "plannedShootDays": project.planned_shoot_days,
        "actualShootDays": project.actual_shoot_days,
        "productionHealth": project.production_health,
        "audienceType": project.audience_type,
        "marketingBudgetLevel": project.marketing_budget_level,
        "primaryMarketingChannel": project.primary_marketing_channel,
        "releaseModel": project.release_model,
        "distributionConfidence": project.distribution_confidence,
    }


def _run_full_pipeline(project: FilmProject, db: Session) -> dict:
    """
    Run the entire Phase 6 pipeline and return raw results.
    Shared by /analyze, /pitch-pack, /intelligence.
    """
    project_dict = _project_to_dict(project)

    # Layer 1: Signal Aggregation
    signals = compute_signals(
        genre=project.genre, language=project.language, scale=project.scale,
        talent_strategy=project.talent_strategy, budget_level=project.budget_level,
        audience_type=project.audience_type, film_title=project.title,
    )
    top_regions = get_top_regions(signals)
    hype_momentum = compute_hype_momentum(signals)

    # Competition Density
    cdi_result = compute_cdi(
        genre=project.genre, language=project.language,
        budget_level=project.budget_level, db=db,
    )

    # Competition Intelligence (full)
    competition_intel = compute_competition_intel(
        genre=project.genre, language=project.language,
        budget_level=project.budget_level, db=db,
    )

    # Layer 2: Regional hype (signal-enhanced)
    raw_regions = compute_regional_interest_with_signals(
        signals=signals, language=project.language,
        audience_type=project.audience_type, scale=project.scale,
    )
    normalized_regions = normalize_scores(raw_regions)
    top_region = normalized_regions[0] if normalized_regions else {"region": "Unknown", "tier": "low", "normalized_score": 0}

    # Layer 2: Platform fit (signal-enhanced)
    raw_scores = calculate_platform_fit_v2(
        genre=project.genre, scale=project.scale, audience_type=project.audience_type,
        release_model=project.release_model, talent_strategy=project.talent_strategy,
        budget_level=project.budget_level, signals=signals, top_regions=top_regions,
    )
    ranked = rank_platforms(raw_scores)
    top = ranked[0]

    # Dubbing
    dubbing_result = analyze_dubbing_need(
        original_language=project.language, audience_type=project.audience_type,
        scale=project.scale, budget_level=project.budget_level,
        distribution_confidence=project.distribution_confidence,
    )

    # Release Timing
    release_timing = compute_release_scores(
        genre=project.genre,
        language=project.language,
        target_regions=[s["region"] for s in normalized_regions[:3]],
        hype_momentum=hype_momentum,
        competition_by_month=competition_intel.get("competition_by_month"),
    )
    release_strength = release_timing.get("best_score", 0.5)

    # Layer 3: Leverage (now includes release_strength)
    dubbing_potential = compute_dubbing_expansion_potential(dubbing_result)
    regional_dominance = top_region.get("normalized_score", 0.5)
    leverage_result = compute_leverage(
        platform_fit_score=top["fit_score"], hype_momentum=hype_momentum,
        regional_dominance=regional_dominance, dubbing_expansion_potential=dubbing_potential,
        release_strength=release_strength,
    )

    # Release mode with probabilities
    release_result = classify_release_mode_with_probabilities(
        scale=project.scale, budget_level=project.budget_level,
        audience_type=project.audience_type, talent_strategy=project.talent_strategy,
        release_model=project.release_model, distribution_confidence=project.distribution_confidence,
        top_platform=top["platform"],
    )

    # Deal terms
    lev_score = leverage_result["leverage_score"]
    deals = generate_deal_terms(
        platforms=ranked, leverage_score=lev_score,
        budget_level=project.budget_level, release_model=project.release_model,
    )

    # Overall readiness
    features = build_feature_vector(project_dict)
    ml_score = predict(features)
    readiness = ml_score if ml_score is not None else rule_based_readiness(features)

    # Deal benchmark data
    benchmarks = _get_deal_benchmarks(project.genre, db)

    return {
        "project": project,
        "project_dict": project_dict,
        "signals": signals,
        "top_regions": top_regions,
        "hype_momentum": hype_momentum,
        "cdi_result": cdi_result,
        "competition_intel": competition_intel,
        "release_timing": release_timing,
        "release_strength": release_strength,
        "normalized_regions": normalized_regions,
        "top_region": top_region,
        "ranked": ranked,
        "top": top,
        "dubbing_result": dubbing_result,
        "dubbing_potential": dubbing_potential,
        "leverage_result": leverage_result,
        "release_result": release_result,
        "deals": deals,
        "readiness": readiness,
        "benchmarks": benchmarks,
        "lev_score": lev_score,
    }


def _get_deal_benchmarks(genre: str, db: Session) -> list:
    """Fetch industry deal benchmarks for comparison."""
    try:
        from phase6_models import DealBenchmark
        rows = (
            db.query(DealBenchmark)
            .filter(DealBenchmark.genre == genre)
            .all()
        )
        return [
            {
                "platform": r.platform_name,
                "avg_advance_pct": r.avg_advance_pct,
                "avg_rev_share": r.avg_rev_share,
                "min_guarantee_usd_k": r.min_guarantee_usd_k,
                "exclusive_window_days": r.exclusive_window_days,
                "sample_count": r.sample_count,
            }
            for r in rows
        ]
    except Exception:
        return []


# ══════════════════════════════════════════════════════════════
# 1. PLATFORM FIT
# ══════════════════════════════════════════════════════════════

@router.post("/platform-fit", response_model=PlatformFitResponse)
def platform_fit_endpoint(project_id: int, db: Session = Depends(get_db)):
    project = _get_project(project_id, db)
    raw_scores = calculate_platform_fit(
        genre=project.genre, scale=project.scale, audience_type=project.audience_type,
        release_model=project.release_model, talent_strategy=project.talent_strategy,
        budget_level=project.budget_level,
    )
    ranked = rank_platforms(raw_scores)
    top = ranked[0]
    return PlatformFitResponse(
        project_id=project.id,
        rankings=[PlatformScore(**p) for p in ranked],
        recommended_platform=top["platform"],
        recommended_score=top["fit_score"],
        distribution_model=project.release_model,
    )


# ══════════════════════════════════════════════════════════════
# 2. REGIONAL DEMAND
# ══════════════════════════════════════════════════════════════

@router.post("/regional-demand", response_model=RegionalHypeResponse)
@router.post("/regional-hype", response_model=RegionalHypeResponse)
def regional_demand_endpoint(project_id: int, db: Session = Depends(get_db)):
    project = _get_project(project_id, db)
    signals = compute_signals(
        genre=project.genre, language=project.language, scale=project.scale,
        talent_strategy=project.talent_strategy, budget_level=project.budget_level,
        audience_type=project.audience_type, film_title=project.title,
    )
    raw = compute_regional_interest_with_signals(
        signals=signals, language=project.language,
        audience_type=project.audience_type, scale=project.scale,
    )
    normalized = normalize_scores(raw)
    top_region = normalized[0] if normalized else {"region": "Unknown", "normalized_score": 0, "tier": "low"}
    return RegionalHypeResponse(
        project_id=project.id,
        regions=[RegionScore(**r) for r in normalized],
        signals=[SignalData(**s) for s in signals],
        top_region=top_region["region"],
        hype_summary=f"Strongest interest in {top_region['region']} ({top_region['tier']} tier)",
    )


# ══════════════════════════════════════════════════════════════
# 3. DUBBING ANALYSIS
# ══════════════════════════════════════════════════════════════

@router.post("/dubbing-analysis")
def dubbing_analysis_endpoint(project_id: int, db: Session = Depends(get_db)):
    project = _get_project(project_id, db)

    dubbing_result = analyze_dubbing_need(
        original_language=project.language, audience_type=project.audience_type,
        scale=project.scale, budget_level=project.budget_level,
        distribution_confidence=project.distribution_confidence,
    )

    # Compute cross-region interest ratio from signals
    signals = compute_signals(
        genre=project.genre, language=project.language, scale=project.scale,
        talent_strategy=project.talent_strategy, budget_level=project.budget_level,
        audience_type=project.audience_type, film_title=project.title,
    )

    # Cross-region interest: non-native regions vs total
    from phase6.services.signal_aggregator import LANGUAGE_REGION_BUZZ
    lang_key = project.language.lower()
    lang_buzz = LANGUAGE_REGION_BUZZ.get(lang_key, {})
    native_regions = [r for r, v in lang_buzz.items() if v >= 0.7]
    non_native_ris = sum(s["RIS"] for s in signals if s["region"] not in native_regions)
    total_ris = sum(s["RIS"] for s in signals)
    cross_region_ratio = round(non_native_ris / max(0.01, total_ris), 4)

    # Predicted reach increase from dubbing
    recs = dubbing_result.get("recommendations", [])
    total_roi_uplift = sum(r.get("estimated_roi_uplift", 0) for r in recs)
    predicted_reach_increase_pct = round(total_roi_uplift / max(1, len(recs)) * 1.5, 1) if recs else 0

    return {
        "project_id": project.id,
        "needs_dubbing": dubbing_result["needs_dubbing"],
        "cross_region_interest_ratio": cross_region_ratio,
        "recommendations": dubbing_result["recommendations"],
        "estimated_total_cost_tier": dubbing_result["estimated_total_cost_tier"],
        "predicted_reach_increase_pct": predicted_reach_increase_pct,
        "confidence": round(min(1.0, cross_region_ratio + 0.3), 4) if dubbing_result["needs_dubbing"] else 0.0,
    }


# ══════════════════════════════════════════════════════════════
# 4. DEAL BENCHMARK
# ══════════════════════════════════════════════════════════════

@router.post("/deal-benchmark")
@router.post("/deal", response_model=DealResponse)
def deal_benchmark_endpoint(project_id: int, db: Session = Depends(get_db)):
    project = _get_project(project_id, db)

    raw_scores = calculate_platform_fit(
        genre=project.genre, scale=project.scale, audience_type=project.audience_type,
        release_model=project.release_model, talent_strategy=project.talent_strategy,
        budget_level=project.budget_level,
    )
    ranked = rank_platforms(raw_scores)
    best_fit_score = ranked[0]["fit_score"] if ranked else 0.5

    leverage_info = compute_negotiation_leverage(
        scale=project.scale, talent_strategy=project.talent_strategy,
        audience_type=project.audience_type, budget_level=project.budget_level,
        distribution_confidence=project.distribution_confidence,
        platform_fit_score=best_fit_score,
    )

    deals = generate_deal_terms(
        platforms=ranked, leverage_score=leverage_info["leverage_score"],
        budget_level=project.budget_level, release_model=project.release_model,
    )

    benchmarks = _get_deal_benchmarks(project.genre, db)

    return DealResponse(
        project_id=project.id,
        negotiation_leverage=leverage_info["leverage"],
        leverage_score=leverage_info["leverage_score"],
        deal_options=[DealTerms(**d) for d in deals],
        benchmarks=benchmarks,
    )


# ══════════════════════════════════════════════════════════════
# 5. PITCH PACK
# ══════════════════════════════════════════════════════════════

@router.post("/pitch-pack")
def pitch_pack_endpoint(project_id: int, db: Session = Depends(get_db)):
    project = _get_project(project_id, db)
    pipeline = _run_full_pipeline(project, db)

    pack = generate_pitch_pack(
        project_title=project.title,
        genre=project.genre,
        language=project.language,
        platform_fit_result={
            "recommended_platform": pipeline["top"]["platform"],
            "recommended_score": pipeline["top"]["fit_score"],
            "rankings": pipeline["ranked"],
        },
        regional_hype_result={
            "top_region": pipeline["top_region"]["region"],
            "regions": pipeline["normalized_regions"],
        },
        dubbing_result=pipeline["dubbing_result"],
        leverage_result=pipeline["leverage_result"],
        release_mode_result=pipeline["release_result"],
        deal_options=pipeline["deals"],
        readiness_score=pipeline["readiness"],
        signals=pipeline["signals"],
    )

    return pack


# ══════════════════════════════════════════════════════════════
# 6. INTELLIGENCE (normalized feed for Phase 7)
# ══════════════════════════════════════════════════════════════

@router.post("/intelligence")
def intelligence_endpoint(project_id: int, db: Session = Depends(get_db)):
    project = _get_project(project_id, db)
    pipeline = _run_full_pipeline(project, db)

    top = pipeline["top"]
    top_region = pipeline["top_region"]
    leverage = pipeline["leverage_result"]
    release = pipeline["release_result"]
    dubbing = pipeline["dubbing_result"]

    # Compute dubbing gain
    recs = dubbing.get("recommendations", [])
    dubbing_gain = round(
        sum(r.get("estimated_roi_uplift", 0) for r in recs) / max(1, len(recs)),
        4,
    ) if recs else 0.0

    return {
        "project_id": project.id,
        "platform_fit": round(top["fit_score"], 4),
        "top_platform": top["platform"],
        "top_regions": pipeline["top_regions"],
        "release_mode": release["mode"],
        "release_probabilities": release["probabilities"],
        "dubbing_recommended": dubbing.get("needs_dubbing", False),
        "dubbing_gain": dubbing_gain,
        "leverage_score": leverage["leverage_score"],
        "leverage_level": leverage["level"],
        "leverage_strategy": leverage["strategy_hint"],
        "hype_momentum": pipeline["hype_momentum"],
        "cdi": pipeline["cdi_result"]["cdi"],
        "overall_readiness": pipeline["readiness"],
        "competition": pipeline["cdi_result"],
    }


# ══════════════════════════════════════════════════════════════
# FULL ANALYSIS (orchestrates all layers)
# ══════════════════════════════════════════════════════════════

@router.post("/analyze", response_model=Phase6AnalysisResponse)
def full_analysis_endpoint(project_id: int, db: Session = Depends(get_db)):
    project = _get_project(project_id, db)
    pipeline = _run_full_pipeline(project, db)

    top = pipeline["top"]
    top_region = pipeline["top_region"]
    signals = pipeline["signals"]
    normalized_regions = pipeline["normalized_regions"]
    ranked = pipeline["ranked"]
    dubbing_result = pipeline["dubbing_result"]
    leverage_result = pipeline["leverage_result"]
    release_result = pipeline["release_result"]
    deals = pipeline["deals"]
    lev_score = pipeline["lev_score"]
    readiness = pipeline["readiness"]

    # Build response objects
    regional_hype = RegionalHypeResponse(
        project_id=project.id,
        regions=[RegionScore(**r) for r in normalized_regions],
        signals=[SignalData(**s) for s in signals],
        top_region=top_region["region"],
        hype_summary=f"Strongest interest in {top_region['region']} ({top_region['tier']} tier)",
    )

    platform_fit = PlatformFitResponse(
        project_id=project.id,
        rankings=[PlatformScore(**p) for p in ranked],
        recommended_platform=top["platform"],
        recommended_score=top["fit_score"],
        distribution_model=project.release_model,
    )

    dubbing = DubbingResponse(
        project_id=project.id,
        needs_dubbing=dubbing_result["needs_dubbing"],
        recommendations=[DubbingRecommendation(**r) for r in dubbing_result["recommendations"]],
        estimated_total_cost_tier=dubbing_result["estimated_total_cost_tier"],
    )

    leverage_response = LeverageResponse(
        leverage_score=leverage_result["leverage_score"],
        level=leverage_result["level"],
        strategy_hint=leverage_result["strategy_hint"],
        breakdown=LeverageBreakdown(**leverage_result["breakdown"]),
    )

    deal_leverage_label = "strong" if lev_score >= 0.6 else ("moderate" if lev_score >= 0.4 else "weak")
    deal = DealResponse(
        project_id=project.id,
        negotiation_leverage=deal_leverage_label,
        leverage_score=lev_score,
        leverage_detail=leverage_response,
        deal_options=[DealTerms(**d) for d in deals],
        benchmarks=pipeline["benchmarks"],
    )

    release_mode = release_result["mode"]

    summary = (
        f"Recommended release: {release_mode}. "
        f"Best platform: {top['platform']} (fit: {top['fit_score']:.0%}). "
        f"Top market: {top_region['region']}. "
        f"Leverage: {leverage_result['level']} ({lev_score:.0%}) — {leverage_result['strategy_hint']}. "
        f"Readiness: {readiness:.0%}."
    )

    return Phase6AnalysisResponse(
        project_id=project.id,
        platform_fit=platform_fit,
        regional_hype=regional_hype,
        dubbing=dubbing,
        deal=deal,
        leverage=leverage_response,
        release_mode=release_mode,
        release_probabilities=release_result["probabilities"],
        competition=pipeline["cdi_result"],
        competition_intel=pipeline.get("competition_intel"),
        release_timing=pipeline.get("release_timing"),
        overall_readiness_score=readiness,
        summary=summary,
    )


# ── Release Timing ────────────────────────────────────────────

@router.post("/release-timing")
def release_timing_endpoint(project_id: int, db: Session = Depends(get_db)):
    project = _get_project(project_id, db)
    pipeline = _run_full_pipeline(project, db)
    return {
        "project_id": project.id,
        **pipeline["release_timing"],
    }


# ── Competition Intelligence ──────────────────────────────────

@router.post("/competition-intel")
def competition_intel_endpoint(project_id: int, db: Session = Depends(get_db)):
    project = _get_project(project_id, db)
    pipeline = _run_full_pipeline(project, db)
    return {
        "project_id": project.id,
        **pipeline["competition_intel"],
    }


# ── Simulate Release Shift ────────────────────────────────────

@router.post("/simulate-release")
def simulate_release_endpoint(
    project_id: int,
    current_month: int,
    new_month: int,
    db: Session = Depends(get_db),
):
    project = _get_project(project_id, db)
    pipeline = _run_full_pipeline(project, db)

    result = simulate_release_shift(
        current_month=current_month,
        new_month=new_month,
        genre=project.genre,
        target_regions=[s["region"] for s in pipeline["normalized_regions"][:3]],
        hype_momentum=pipeline["hype_momentum"],
        competition_by_month=pipeline["competition_intel"].get("competition_by_month"),
    )
    return {"project_id": project.id, **result}

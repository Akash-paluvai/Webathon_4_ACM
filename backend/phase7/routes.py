"""
Phase 7 Routes — Release & Discoverability Engine.

15 Endpoints:
    POST /phase7/discoverability/{film_id}
    POST /phase7/sensitivity/{film_id}
    POST /phase7/simulate
    POST /phase7/timeline/{film_id}
    POST /phase7/optimize/{film_id}
    POST /phase7/visibility-risk/{film_id}
    POST /phase7/momentum/{film_id}
    POST /phase7/budget-optimize/{film_id}
    POST /phase7/recovery/{film_id}
    POST /phase7/barriers/{film_id}
    POST /phase7/conversion/{film_id}
    POST /phase7/festival-impact/{film_id}
    POST /phase7/ticket-pricing/{film_id}
    POST /phase7/market-shock/{film_id}
    POST /phase7/demand/{film_id}        ← NEW: Demand Intelligence
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Optional

from database import get_db
from phase7.services.phase6_bridge import fetch_phase6_intel
from phase7.services.discoverability_engine import (
    compute_discoverability, compute_sensitivity, simulate_scenario,
)
from phase7.services.visibility_risk import detect_visibility_risk
from phase7.services.momentum_engine import forecast_momentum
from phase7.services.budget_optimizer import optimize_budget
from phase7.services.recovery_engine import compute_recovery
from phase7.services.confidence_layer import compute_confidence
from phase7.services.barrier_analyzer import analyze_barriers
from phase7.services.conversion_engine import predict_conversion
from phase7.services.festival_impact import predict_festival_impact
from phase7.services.ticket_pricing import compute_ticket_pricing
from phase7.services.market_shock import detect_market_shocks
from phase7.services.demand_engine import compute_demand_intelligence

router = APIRouter()


# ── Helpers ──────────────────────────────────────────────────

def _get_intel(film_id: int, db: Session) -> Dict:
    try:
        return fetch_phase6_intel(film_id, db)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Project {film_id} not found")


# ══════════════════════════════════════════════════════════════
# 1. DISCOVERABILITY
# ══════════════════════════════════════════════════════════════

@router.post("/discoverability/{film_id}")
def discoverability_endpoint(film_id: int, db: Session = Depends(get_db)):
    intel = _get_intel(film_id, db)
    disco = compute_discoverability(intel)
    sensitivity = compute_sensitivity(intel)
    confidence = compute_confidence(intel, disco["score"], sensitivity["total_sensitivity"])
    shocks = detect_market_shocks(intel)

    return {
        "project_id": film_id,
        **disco,
        "confidence": confidence,
        "market_status": shocks["overall_risk"],
    }


# ══════════════════════════════════════════════════════════════
# 2. SENSITIVITY
# ══════════════════════════════════════════════════════════════

@router.post("/sensitivity/{film_id}")
def sensitivity_endpoint(film_id: int, db: Session = Depends(get_db)):
    intel = _get_intel(film_id, db)
    return {"project_id": film_id, **compute_sensitivity(intel)}


# ══════════════════════════════════════════════════════════════
# 3. SIMULATE
# ══════════════════════════════════════════════════════════════

@router.post("/simulate")
def simulate_endpoint(
    film_id: int,
    platform_fit: Optional[float] = None,
    hype_momentum: Optional[float] = None,
    cdi: Optional[float] = None,
    campaign_intensity: Optional[float] = None,
    regional_strength: Optional[float] = None,
    db: Session = Depends(get_db),
):
    intel = _get_intel(film_id, db)
    overrides = {}
    if platform_fit is not None: overrides["platform_fit"] = platform_fit
    if hype_momentum is not None: overrides["hype_momentum"] = hype_momentum
    if cdi is not None: overrides["cdi"] = cdi
    if campaign_intensity is not None: overrides["campaign_intensity"] = campaign_intensity
    if regional_strength is not None: overrides["regional_strength"] = regional_strength

    return {"project_id": film_id, **simulate_scenario(intel, overrides)}


# ══════════════════════════════════════════════════════════════
# 4. TIMELINE (full Phase 7 intelligence feed)
# ══════════════════════════════════════════════════════════════

@router.post("/timeline/{film_id}")
def timeline_endpoint(film_id: int, db: Session = Depends(get_db)):
    intel = _get_intel(film_id, db)

    disco = compute_discoverability(intel)
    sensitivity = compute_sensitivity(intel)
    visibility = detect_visibility_risk(intel)
    momentum = forecast_momentum(intel)
    budget = optimize_budget(intel)
    barriers = analyze_barriers(intel, disco["score"])
    conversion = predict_conversion(intel)
    festival = predict_festival_impact(intel)
    pricing = compute_ticket_pricing(intel)
    shocks = detect_market_shocks(intel)
    recovery = compute_recovery(intel, disco["score"])
    confidence = compute_confidence(intel, disco["score"], sensitivity["total_sensitivity"])

    # Demand intelligence summary (non-breaking addition)
    try:
        demand = compute_demand_intelligence(intel)
        demand_summary = {
            "dsi_score": demand["dsi"]["score"],
            "dsi_grade": demand["dsi"]["grade"],
            "demand_trend": demand["demand_trend"]["trend"],
            "revenue_class": demand["forecast"]["revenue_class"],
        }
    except Exception:
        demand_summary = None

    return {
        "project_id": film_id,
        "discoverability": disco,
        "confidence": confidence,
        "visibility_risk": visibility,
        "momentum": momentum,
        "budget_allocation": budget,
        "barriers": barriers,
        "conversion": conversion,
        "festival_impact": festival,
        "ticket_pricing": pricing,
        "market_shocks": shocks,
        "recovery": recovery,
        "sensitivity": sensitivity,
        "demand_intelligence": demand_summary,
    }


# ══════════════════════════════════════════════════════════════
# 5. OPTIMIZE
# ══════════════════════════════════════════════════════════════

@router.post("/optimize/{film_id}")
def optimize_endpoint(film_id: int, budget_lakhs: float = 100.0, db: Session = Depends(get_db)):
    intel = _get_intel(film_id, db)
    disco = compute_discoverability(intel)
    budget = optimize_budget(intel, budget_lakhs)
    barriers = analyze_barriers(intel, disco["score"])
    recovery = compute_recovery(intel, disco["score"])

    return {
        "project_id": film_id,
        "current_discoverability": disco["score"],
        "optimization": budget,
        "barriers": barriers,
        "recovery_plan": recovery,
    }


# ══════════════════════════════════════════════════════════════
# 6. VISIBILITY RISK
# ══════════════════════════════════════════════════════════════

@router.post("/visibility-risk/{film_id}")
def visibility_risk_endpoint(film_id: int, db: Session = Depends(get_db)):
    intel = _get_intel(film_id, db)
    return {"project_id": film_id, **detect_visibility_risk(intel)}


# ══════════════════════════════════════════════════════════════
# 7. MOMENTUM
# ══════════════════════════════════════════════════════════════

@router.post("/momentum/{film_id}")
def momentum_endpoint(film_id: int, db: Session = Depends(get_db)):
    intel = _get_intel(film_id, db)
    return {"project_id": film_id, **forecast_momentum(intel)}


# ══════════════════════════════════════════════════════════════
# 8. BUDGET OPTIMIZE
# ══════════════════════════════════════════════════════════════

@router.post("/budget-optimize/{film_id}")
def budget_optimize_endpoint(film_id: int, budget_lakhs: float = 100.0, db: Session = Depends(get_db)):
    intel = _get_intel(film_id, db)
    return {"project_id": film_id, **optimize_budget(intel, budget_lakhs)}


# ══════════════════════════════════════════════════════════════
# 9. RECOVERY
# ══════════════════════════════════════════════════════════════

@router.post("/recovery/{film_id}")
def recovery_endpoint(film_id: int, db: Session = Depends(get_db)):
    intel = _get_intel(film_id, db)
    disco = compute_discoverability(intel)
    return {"project_id": film_id, **compute_recovery(intel, disco["score"])}


# ══════════════════════════════════════════════════════════════
# 10. BARRIERS
# ══════════════════════════════════════════════════════════════

@router.post("/barriers/{film_id}")
def barriers_endpoint(film_id: int, db: Session = Depends(get_db)):
    intel = _get_intel(film_id, db)
    disco = compute_discoverability(intel)
    return {"project_id": film_id, **analyze_barriers(intel, disco["score"])}


# ══════════════════════════════════════════════════════════════
# 11. CONVERSION
# ══════════════════════════════════════════════════════════════

@router.post("/conversion/{film_id}")
def conversion_endpoint(film_id: int, db: Session = Depends(get_db)):
    intel = _get_intel(film_id, db)
    return {"project_id": film_id, **predict_conversion(intel)}


# ══════════════════════════════════════════════════════════════
# 12. FESTIVAL IMPACT
# ══════════════════════════════════════════════════════════════

@router.post("/festival-impact/{film_id}")
def festival_impact_endpoint(film_id: int, db: Session = Depends(get_db)):
    intel = _get_intel(film_id, db)
    return {"project_id": film_id, **predict_festival_impact(intel)}


# ══════════════════════════════════════════════════════════════
# 13. TICKET PRICING
# ══════════════════════════════════════════════════════════════

@router.post("/ticket-pricing/{film_id}")
def ticket_pricing_endpoint(film_id: int, db: Session = Depends(get_db)):
    intel = _get_intel(film_id, db)
    return {"project_id": film_id, **compute_ticket_pricing(intel)}


# ══════════════════════════════════════════════════════════════
# 14. MARKET SHOCK
# ══════════════════════════════════════════════════════════════

@router.post("/market-shock/{film_id}")
def market_shock_endpoint(film_id: int, db: Session = Depends(get_db)):
    intel = _get_intel(film_id, db)
    return {"project_id": film_id, **detect_market_shocks(intel)}


# ══════════════════════════════════════════════════════════════
# 15. DEMAND INTELLIGENCE
# ══════════════════════════════════════════════════════════════

@router.post("/demand/{film_id}")
def demand_endpoint(film_id: int, db: Session = Depends(get_db)):
    intel = _get_intel(film_id, db)
    demand = compute_demand_intelligence(intel)
    return {"project_id": film_id, **demand}

import json
from sqlalchemy.orm import Session
from models import FilmProject, Insight
from services.phase4_logic import compute_phase4
from services.phase5_logic import compute_phase5
from phase6.routes import _run_full_pipeline
from phase7.routes import timeline_endpoint

def get_project_summary(project_id: int, db: Session) -> str:
    """
    Aggregates all project data, scores, and decisions across all 8 phases.
    Returns a formatted string suitable for AI context.
    """
    project = db.query(FilmProject).filter(FilmProject.id == project_id).first()
    if not project:
        return "Project not found."

    # 1. Core Project Metadata
    summary = f"--- PROJECT OVERVIEW ---\n"
    summary += f"Title: {project.title}\n"
    summary += f"Genre: {project.genre}\n"
    summary += f"Theme: {project.theme}\n"
    summary += f"Language: {project.language}\n"
    summary += f"Scale: {project.scale}\n"
    summary += f"Budget Level: {project.budget_level}\n"
    summary += f"Talent Strategy: {project.talent_strategy}\n"
    summary += f"Production Health: {project.production_health}\n"
    summary += f"Current Phase: {project.current_phase}\n"
    
    # 2. Phase 4 Insights (Trailer & Audience)
    # Since trailer features aren't persisted, we use saved audience_type
    # and re-compute a baseline interest score if we have to.
    p4_result = compute_phase4(
        scale=project.scale,
        production_health=project.production_health,
        trailer_features={"average_shot_length_sec": 3.0, "scene_change_frequency_per_sec": 0.5} # Neutral defaults
    )
    summary += f"\n--- PHASE 4: MARKET FIT ---\n"
    summary += f"Target Audience: {project.audience_type} (Validated: {p4_result['audienceType']})\n"
    summary += f"Baseline Audience Interest: {p4_result['audienceInterestScore']}/100\n"

    # 3. Phase 5 Insights (Marketing)
    if project.marketing_budget_level != "unassigned":
        p5_result = compute_phase5(
            audience_type=project.audience_type,
            audience_interest_score=p4_result['audienceInterestScore'],
            scale=project.scale,
            budget_level=project.budget_level,
            marketing_budget_level=project.marketing_budget_level
        )
        summary += f"\n--- PHASE 5: MARKETING STRATEGY ---\n"
        summary += f"Marketing Budget: {project.marketing_budget_level}\n"
        summary += f"Primary Channel: {project.primary_marketing_channel}\n"
        summary += f"Discoverability Score: {p5_result['discoverabilityScore']}/100\n"
        summary += f"Marketing Risk: {p5_result['marketingRisk']}\n"
        if p5_result.get('riskFlags'):
            summary += f"Risk Flags: {', '.join(p5_result['riskFlags'])}\n"

    # 4. Phase 6 Insights (Distribution)
    try:
        p6_pipeline = _run_full_pipeline(project, db)
        summary += f"\n--- PHASE 6: DISTRIBUTION ---\n"
        summary += f"Recommended Platform: {p6_pipeline['platform_fit']['recommended_platform']}\n"
        summary += f"Distribution Model: {p6_pipeline['release_mode']}\n"
        summary += f"Negotiation Leverage: {p6_pipeline['leverage']['level']} ({int(p6_pipeline['leverage']['leverage_score']*100)}%)\n"
        summary += f"Overall Readiness: {int(p6_pipeline['overall_readiness_score']*100)}%\n"
        summary += f"Top Market: {p6_pipeline['regional_hype']['top_region']}\n"
    except Exception as e:
        summary += f"\n--- PHASE 6: DISTRIBUTION ---\nStatus: Pending or Error in computation.\n"

    # 5. Phase 7 Insights (Release Engine)
    try:
        p7_result = timeline_endpoint(project_id, db)
        summary += f"\n--- PHASE 7: RELEASE ENGINE ---\n"
        summary += f"Final Discoverability: {int(p7_result['discoverability']['score']*100)}% (Grade: {p7_result['discoverability']['grade']})\n"
        summary += f"Visibility Risk: {p7_result['visibility_risk']['visibility_risk']}\n"
        summary += f"Market Status: {p7_result['market_shocks']['overall_risk']}\n"
        summary += f"Predicted Conversion: {int(p7_result['conversion']['conversion_probability']*100)}%\n"
    except Exception as e:
        summary += f"\n--- PHASE 7: RELEASE ENGINE ---\nStatus: Not yet calculated.\n"

    # 6. Phase 8 Insights (Post-Release)
    if project.audience_response or project.learning_summary:
        summary += f"\n--- PHASE 8: POST-RELEASE PERFORMANCE ---\n"
        summary += f"Audience Response: {project.audience_response}\n"
        if project.monetization_options:
            summary += f"Monetization Strategy: {project.monetization_options}\n"
        if project.learning_summary:
            summary += f"Learning Summary: {project.learning_summary[:500]}...\n"

    # 6. Historical Insights & Decisions
    insights = db.query(Insight).filter(Insight.project_id == project_id).order_by(Insight.timestamp).all()
    if insights:
        summary += f"\n--- HISTORICAL DECISIONS & NOTES ---\n"
        for i in insights:
            summary += f"- [{i.timestamp.strftime('%Y-%m-%d')}] {i.content}\n"

    return summary

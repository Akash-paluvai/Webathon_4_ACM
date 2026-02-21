"""
FilmFlow Assistant Service
Handles phase-aware chat logic using Groq.
"""

import os
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from partA.script_analysis_model import get_groq_client
from services.project_summarizer import get_project_summary

# ... (imports) ...

def chat_with_assistant(
    message: str,
    phase: Optional[str] = None,
    history: List[Dict[str, str]] = None,
    project_id: Optional[int] = None,
    db: Optional[Session] = None
) -> str:
    """
    Generate a response from the FilmFlow Assistant using Groq, infused with project context.
    """
    client = get_groq_client()
    
    # Base system prompt
    system_prompt = (
        "You are the FilmFlow Assistant, an expert AI film producer and consultant. "
        "Your goal is to help users navigate the professional film production pipeline. "
        "Be concise, insightful, and professional. Use data-driven reasoning where possible."
    )
    
    # Project-specific context
    project_context = ""
    if project_id and db:
        project_context = get_project_summary(project_id, db)
    
    # Phase-specific context enhancement
    phase_contexts = {
        "phase-1": "The user is currently in Phase 1 (Script Selection). Focus on script evaluation, genre trends, and concept viability.",
        "phase-2": "The user is currently in Phase 2 (Pre-Production). Focus on packaging strategy, budget planning, and talent acquisition.",
        "phase-3": "The user is currently in Phase 3 (Production). Focus on production health, shoot schedules, and risk management.",
        "phase-4": "The user is currently in Phase 4 (Post-Production). Focus on edit analysis, market testing, and audience feedback.",
        "phase-5": "The user is currently in Phase 5 (Marketing). Focus on campaign planning, budget allocation, and target audiences.",
        "phase-6": "The user is currently in Phase 6 (Distribution). Focus on distribution strategies, platform negotiations, and release timing.",
        "phase-7": "The user is currently in Phase 7 (Release). Focus on release day monitoring and audience engagement.",
        "phase-8": "The user is currently in Phase 8 (Post-Release). Focus on revenue tracking, monetization, and sequel potential.",
    }
    
    context_addon = ""
    if phase and phase in phase_contexts:
        context_addon = f"\n\nCURRENT PHASE CONTEXT: {phase_contexts[phase]}"
    
    full_system_prompt = (
        f"{system_prompt}\n\n"
        f"You have deep memory of the project. Here is the current state of the production:\n\n"
        f"{project_context}"
        f"{context_addon}\n\n"
        f"When answering, reference specific scores (e.g., 'Your 72% discoverability score') or decisions "
        f"from previous phases to provide integrated advice."
    )
    
    messages = [{"role": "system", "content": full_system_prompt}]
    
    # Add history if provided (limit to last 8 messages for context)
    if history:
        messages.extend(history[-8:]) 
        
    messages.append({"role": "user", "content": message})
    
    try:
        response = client.chat.completions.create(
            model=_ASSISTANT_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=800,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Assistant Error: {e}")
        return f"I'm sorry, I'm having trouble connecting to my brain right now. Please try again in a moment. (Error: {str(e)})"

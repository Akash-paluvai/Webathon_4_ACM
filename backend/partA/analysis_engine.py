from .llm import generate_script_analysis

def analyze_script_and_audience(payload: dict):
    script_text = payload.get("scriptText", "")

    if not script_text:
        return {"error": "Script text required"}

    analysis = generate_script_analysis(script_text)

    return {
        "analysis": analysis
    }
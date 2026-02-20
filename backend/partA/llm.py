import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_script_analysis(script_text: str):
    try:
        prompt = f"""
You are a professional film analyst.

Return JSON:
{{
 "summary": "",
 "theme": "",
 "target_audience": "",
 "feasibility_score": 0,
 "risk_level": "",
 "audience_affinity": 0
}}

Script:
{script_text[:1200]}
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",   # ← WORKING FREE MODEL
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=300,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI error: {str(e)}"
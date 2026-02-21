import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.getcwd())

load_dotenv()

from services.cerebras_insights import generate_cerebras_insights

def test_groq_insights():
    print("Testing Groq-powered Phase 4 insights...")
    
    dummy_features = {
        "average_shot_length_sec": 2.5,
        "scene_change_frequency_per_sec": 0.4,
        "average_brightness": 120,
        "audio_available": True,
        "audio_energy_mean": 0.05,
        "face_presence_ratio": 0.3,
        "color_warmth": 0.6
    }
    
    dummy_enhanced = {
        "behavioralDynamics": "Active/Dynamic",
        "violenceLikelihood": "LOW",
        "emotionalTone": "UPBEAT",
        "genreInclination": "ACTION-COMEDY"
    }
    
    result = generate_cerebras_insights(
        audience_type="MASS",
        test_strategy="DIGITAL",
        audience_interest_score=75,
        trailer_features=dummy_features,
        risk_flags=["Pacing mismatch"],
        enhanced_signals=dummy_enhanced
    )
    
    print("\nResult Components:")
    for k, v in result.items():
        print(f"\n[{k}]:\n{v}")
    
    if "API error" in str(result) or "unavailable" in str(result):
        print("\n❌ TEST FAILED: API Error detected.")
        sys.exit(1)
    else:
        print("\n✅ TEST PASSED: Insights generated successfully.")

if __name__ == "__main__":
    test_groq_insights()

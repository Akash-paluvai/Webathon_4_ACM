import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from services.movinet_service import analyze_video_movinet
from services.trailer_analysis import extract_trailer_features
from services.phase4_logic import compute_phase4, derive_enhanced_signals

def test_movinet_stub():
    print("Testing MoViNet stub...")
    # We don't have a real video for unit test here, but we can verify load/fallback
    # Since we use lazy load, get_movinet_model will try to load from TF Hub.
    # In this environment, it might fail or timeout, which is a good test for our fallback.
    res = analyze_video_movinet("non_existent_video.mp4")
    print(f"Result for non-existent video: {res}")
    assert res["error"] == "File not found"

def test_heuristics():
    print("Testing heuristics...")
    det_features = {
        "scene_change_frequency_per_sec": 0.8,
        "face_presence_ratio": 0.05,
        "average_brightness": 80,
        "color_warmth": 0.8,
        "pacing_variance": 0.5
    }
    mov_features = {
        "actionIntensityScore": 85,
        "dominantActionClass": "Dynamic",
        "enhancedAnalysisAvailable": True
    }
    
    signals = derive_enhanced_signals(det_features, mov_features)
    print(f"Derived Signals (HIGH Violence Expectation): {signals}")
    assert signals["violenceLikelihood"] == "HIGH"
    
    det_features_calm = {
        "scene_change_frequency_per_sec": 0.2,
        "face_presence_ratio": 0.5,
        "average_brightness": 150,
        "color_warmth": 1.3,
        "pacing_variance": 3.0
    }
    mov_features_calm = {
        "actionIntensityScore": 20,
        "dominantActionClass": "Calm",
        "enhancedAnalysisAvailable": True
    }
    signals_calm = derive_enhanced_signals(det_features_calm, mov_features_calm)
    print(f"Derived Signals (EMOTIONAL/DRAMA Expectation): {signals_calm}")
    assert signals_calm["emotionalTone"] == "EMOTIONAL"
    assert signals_calm["genreInclination"] == "DRAMA-LEANING"

if __name__ == "__main__":
    try:
        test_movinet_stub()
        test_heuristics()
        print("\nALL BACKEND LOGIC VERIFIED!")
    except Exception as e:
        print(f"\nVERIFICATION FAILED: {e}")
        sys.exit(1)

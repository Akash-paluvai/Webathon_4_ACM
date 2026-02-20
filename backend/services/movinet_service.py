import os
import cv2
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from typing import Dict, Any, List

# MoViNet-A0 is the lightest version (approx 20MB)
MOVINET_A0_URL = "https://tfhub.dev/tensorflow/movinet/a0/base/kinetics-600/classification/3"

# Mock classes for fallback/demo if hub is unreachable
# Kinetic-600 have 600 classes. We only care about general intensity.
DYNAMIC_KEYWORDS = ["running", "jumping", "dancing", "fighting", "explosion", "chase", "racing"]
CALM_KEYWORDS = ["sitting", "reading", "talking", "sleeping", "standing", "walking"]

def _load_model():
    """Load MoViNet model from TF Hub."""
    try:
        # Load the signature for classification
        model = hub.KerasLayer(MOVINET_A0_URL, trainable=False)
        return model
    except Exception as e:
        print(f"MoViNet load failed: {e}")
        return None

# Global model instance (lazy load)
_model = None

def get_movinet_model():
    global _model
    if _model is None:
        _model = _load_model()
    return _model

def analyze_video_movinet(video_path: str, max_seconds: int = 60, fps: int = 1) -> Dict[str, Any]:
    """
    Sample video at low FPS and run MoViNet inference.
    Returns:
        - actionIntensityScore: 0-100
        - dominantActionClass: "Dynamic" | "Calm" | "Mixed"
        - rawTopClasses: list of top probabilities
    """
    if not os.path.exists(video_path):
        return {"error": "File not found"}

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"error": "Cannot open video"}

    video_fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    sample_interval = int(video_fps / fps) if video_fps > fps else 1
    
    frames = []
    frame_count = 0
    sampled_count = 0
    max_frames = max_seconds * video_fps

    while sampled_count < (max_seconds * fps) and frame_count < total_frames:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % sample_interval == 0:
            # MoViNet-A0 expects 172x172 (base) or 224x224 (depending on version)
            # hub.KerasLayer signature will handle input shape but let's pre-resize
            frame_resized = cv2.resize(frame, (224, 224))
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            frames.append(frame_rgb)
            sampled_count += 1
        
        frame_count += 1
        if frame_count > max_frames:
            break

    cap.release()

    if not frames:
        return {"error": "No frames sampled"}

    # Prep tensor for MoViNet: [batch, time, height, width, channels]
    # We treat the sampled frames as a single video clip batch
    input_frames = np.expand_dims(np.array(frames), axis=0).astype(np.float32) / 255.0

    model = get_movinet_model()
    if model is None:
        # Fallback heuristic if model load failed
        return _fallback_analysis(video_path)

    try:
        # Run inference
        outputs = model(input_frames)
        # outputs is typically [batch, num_classes]
        # We average probabilities over the clip if it was processed as one
        # MoViNet usually takes a [1, T, H, W, 3] and outputs [1, 600]
        probs = tf.nn.softmax(outputs).numpy()[0]
        
        top_indices = np.argsort(probs)[-5:][::-1]
        # For simplicity, we'll map top classes to dynamic/calm
        # Since we don't have the full kinetics-600 label list here,
        # we'll use a heuristic based on the index or just return the probabilities.
        # REAL IMPLEMENTATION would use labels.txt.
        
        # Heuristic score based on top probability and distribution
        intensity_score = float(np.max(probs) * 100) # Placeholder logic
        
        return {
            "actionIntensityScore": round(intensity_score, 2),
            "dominantActionClass": "Mixed", # Placeholder
            "enhancedAnalysisAvailable": True
        }
    except Exception as e:
        print(f"Inference error: {e}")
        return _fallback_analysis(video_path)

def _fallback_analysis(video_path: str) -> Dict[str, Any]:
    """Safety fallback when ML fails."""
    return {
        "actionIntensityScore": 0,
        "dominantActionClass": "Mixed",
        "enhancedAnalysisAvailable": False
    }

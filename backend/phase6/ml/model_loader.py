"""
Model Loader — loads a LightGBM model or falls back to a rule-based engine.

Currently uses the rule-based fallback since no trained model is available yet.
When a model file is provided, set MODEL_PATH and it will be loaded automatically.
"""

import os
from typing import Dict, Optional

# Optional: try loading LightGBM if available
try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False

MODEL_PATH = os.environ.get("PHASE6_MODEL_PATH", None)

_cached_model = None


def load_model():
    """
    Load the LightGBM model from MODEL_PATH if available.
    Returns None if no model file exists or LightGBM is not installed.
    """
    global _cached_model

    if _cached_model is not None:
        return _cached_model

    if MODEL_PATH and HAS_LIGHTGBM and os.path.exists(MODEL_PATH):
        _cached_model = lgb.Booster(model_file=MODEL_PATH)
        return _cached_model

    return None


def predict(features: Dict[str, float]) -> Optional[float]:
    """
    Run prediction using the loaded model.
    Returns None if no model is available (caller should use rule-based fallback).
    """
    model = load_model()
    if model is None:
        return None

    # Build feature array in expected order
    feature_names = sorted(features.keys())
    feature_values = [[features[f] for f in feature_names]]

    try:
        prediction = model.predict(feature_values)[0]
        return float(prediction)
    except Exception:
        return None


def rule_based_readiness(features: Dict[str, float]) -> float:
    """
    Fallback rule-based readiness score when no ML model is available.

    Returns an overall readiness score in [0, 1].
    """
    score = 0.5  # baseline

    # Budget level boost
    budget = features.get("budget_level", 1)
    score += budget * 0.05

    # Talent strategy boost
    talent = features.get("talent_strategy", 1)
    score += talent * 0.04

    # Distribution confidence is important
    confidence = features.get("distribution_confidence", 1)
    score += confidence * 0.08

    # Production health matters
    health = features.get("production_health", 2)
    score += (health - 1) * 0.06

    # Marketing readiness
    marketing = features.get("marketing_budget_level", 0)
    score += marketing * 0.03

    # Shoot day ratio penalty (over-schedule is bad)
    ratio = features.get("shoot_day_ratio", 1.0)
    if ratio > 1.2:
        score -= (ratio - 1.0) * 0.1

    # Clamp to [0, 1]
    return round(max(0.0, min(1.0, score)), 4)

"""Manganese prediction service boundary.

This is intentionally a transparent demo implementation. It is not trained on
validated manganese-labelled data and must not be presented as a geological
probability or deposit confirmation.
"""

from .config import MODEL_NAME, MODEL_STATUS, MODEL_VERSION, classify_probability, priority_for_classification
from .features import summarize_features, validate_numeric_features
from .schemas import ManganesePrediction, ManganesePredictionRequest


def predict_manganese(request: ManganesePredictionRequest) -> ManganesePrediction:
    features = validate_numeric_features(request.features)
    # The score is a deterministic UI screening value until validated training data exists.
    probability = 0.50
    confidence = min(0.35, 0.10 + (0.05 * len(features)))
    classification = classify_probability(probability)

    return ManganesePrediction(
        latitude=request.latitude,
        longitude=request.longitude,
        manganese_probability=probability,
        confidence=confidence,
        classification=classification,
        priority=priority_for_classification(classification),
        feature_summary=summarize_features(features),
        data_sources=["user-supplied features"],
        model_name=MODEL_NAME,
        model_version=MODEL_VERSION,
        model_status=MODEL_STATUS,
    )


def predict_manganese_batch(requests: list[ManganesePredictionRequest]) -> list[ManganesePrediction]:
    return [predict_manganese(request) for request in requests]

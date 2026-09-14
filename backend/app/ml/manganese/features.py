"""Feature validation and metadata for future manganese training data."""

from math import isfinite
from typing import Any

SUPPORTED_FEATURES = {
    "mn_concentration",
    "fe_concentration",
    "sio2",
    "al2o3",
    "elevation",
    "slope",
    "aspect",
    "magnetic_value",
    "sar_vv",
    "sar_vh",
    "distance_to_fault",
    "distance_to_lineament",
}


def validate_numeric_features(features: dict[str, Any]) -> dict[str, float]:
    cleaned: dict[str, float] = {}
    for name, value in features.items():
        numeric = float(value)
        if not isfinite(numeric):
            raise ValueError(f"Feature '{name}' must be finite")
        cleaned[name] = numeric
    return cleaned


def summarize_features(features: dict[str, float]) -> list[str]:
    return sorted(features)

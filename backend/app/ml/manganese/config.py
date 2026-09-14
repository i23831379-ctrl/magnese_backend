"""Central configuration for manganese prospectivity classification."""

from dataclasses import dataclass


MINERAL = "manganese"
MODEL_STATUS = "demo"
MODEL_NAME = "Manganese demo screening model"
MODEL_VERSION = "0.1-demo"


@dataclass(frozen=True)
class ProspectivityThresholds:
    very_high: float = 0.80
    high: float = 0.65
    medium: float = 0.45
    low: float = 0.25


THRESHOLDS = ProspectivityThresholds()


def classify_probability(probability: float) -> str:
    """Classify a model score; thresholds are scoring settings, not deposit proof."""
    if probability >= THRESHOLDS.very_high:
        return "VERY_HIGH"
    if probability >= THRESHOLDS.high:
        return "HIGH"
    if probability >= THRESHOLDS.medium:
        return "MEDIUM"
    if probability >= THRESHOLDS.low:
        return "LOW"
    return "VERY_LOW"


def priority_for_classification(classification: str) -> str:
    return {
        "VERY_HIGH": "P1",
        "HIGH": "P1",
        "MEDIUM": "P2",
        "LOW": "P3",
        "VERY_LOW": "P3",
    }[classification]

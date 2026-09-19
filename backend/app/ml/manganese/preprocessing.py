"""Feature matrix preparation for manganese model training."""

from collections.abc import Sequence
from typing import Any

from .training import ManganeseTrainingRecord

DEFAULT_FEATURES = (
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
)


def build_feature_matrix(
    records: Sequence[ManganeseTrainingRecord],
    feature_names: Sequence[str] = DEFAULT_FEATURES,
) -> tuple[list[list[float]], list[int]]:
    if not records:
        raise ValueError("at least one manganese training record is required")

    matrix: list[list[float]] = []
    labels: list[int] = []
    for record in records:
        values: dict[str, Any] = record.model_dump()
        matrix.append([float(values.get(name) or 0.0) for name in feature_names])
        labels.append(record.label)
    return matrix, labels

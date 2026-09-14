"""Validation boundary for future manganese-labelled training data."""

import csv
import io
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ManganeseTrainingRecord(BaseModel):
    model_config = ConfigDict(extra="allow")

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    mn_concentration: float | None = None
    fe_concentration: float | None = None
    sio2: float | None = None
    al2o3: float | None = None
    elevation: float | None = None
    slope: float | None = None
    aspect: float | None = None
    magnetic_value: float | None = None
    sar_vv: float | None = None
    sar_vh: float | None = None
    distance_to_fault: float | None = None
    distance_to_lineament: float | None = None
    lithology: str | None = None
    label: int

    @field_validator("label")
    @classmethod
    def validate_label(cls, value: int) -> int:
        if value not in (0, 1):
            raise ValueError("label must be 0 for background or 1 for validated manganese occurrence")
        return value

    @field_validator(
        "mn_concentration", "fe_concentration", "sio2", "al2o3", "elevation",
        "slope", "aspect", "magnetic_value", "sar_vv", "sar_vh",
        "distance_to_fault", "distance_to_lineament",
    )
    @classmethod
    def validate_numeric_value(cls, value: float | None) -> float | None:
        if value is not None and value != value:
            raise ValueError("numeric feature cannot be NaN")
        return value


class TrainingDataValidation(BaseModel):
    mineral: str = "manganese"
    record_count: int
    feature_columns: list[str]
    records: list[ManganeseTrainingRecord]
    status: str = "validated-for-ingestion"


def validate_training_records(records: list[dict[str, Any]]) -> TrainingDataValidation:
    if not records:
        raise ValueError("training data must contain at least one record")

    validated = [ManganeseTrainingRecord.model_validate(record) for record in records]
    locations = [(record.latitude, record.longitude) for record in validated]
    if len(locations) != len(set(locations)):
        raise ValueError("training data contains duplicate coordinates")

    feature_columns = sorted(
        key for key in validated[0].model_dump(exclude={"latitude", "longitude", "label"})
        if any(record.model_dump().get(key) is not None for record in validated)
    )
    return TrainingDataValidation(
        record_count=len(validated),
        feature_columns=feature_columns,
        records=validated,
    )


def validate_training_csv(csv_text: str) -> TrainingDataValidation:
    reader = csv.DictReader(io.StringIO(csv_text))
    if not reader.fieldnames:
        raise ValueError("CSV must include a header row")
    records = [{key: (value if value != "" else None) for key, value in row.items()} for row in reader]
    return validate_training_records(records)

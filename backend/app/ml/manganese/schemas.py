"""Validated API contracts for manganese prospectivity."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ManganesePredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    features: dict[str, Any] = Field(min_length=1)

    @field_validator("features")
    @classmethod
    def validate_features(cls, value: dict[str, Any]) -> dict[str, Any]:
        for name, feature in value.items():
            if isinstance(feature, bool) or not isinstance(feature, (int, float)):
                raise ValueError(f"Feature '{name}' must be numeric")
        return value


class ManganeseBatchPredictionRequest(BaseModel):
    requests: list[ManganesePredictionRequest] = Field(min_length=1, max_length=1000)


class TrainingDataUploadRequest(BaseModel):
    csv_text: str = Field(min_length=1)


class ManganesePrediction(BaseModel):
    mineral: str = "manganese"
    latitude: float
    longitude: float
    manganese_probability: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    classification: str
    priority: str
    feature_summary: list[str]
    data_sources: list[str]
    model_name: str
    model_version: str
    model_status: str = "demo"


class ModelStatus(BaseModel):
    mineral: str = "manganese"
    model_name: str
    version: str
    training_date: str | None = None
    feature_list: list[str] = Field(default_factory=list)
    status: str
    training_dataset: str
    record_count: int | None = None
    metrics: dict[str, float] | None
    message: str

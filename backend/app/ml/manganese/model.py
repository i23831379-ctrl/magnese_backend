"""Model metadata and registry boundary for manganese models."""

from datetime import date

from pydantic import BaseModel, Field

from .config import MODEL_NAME, MODEL_VERSION
from .preprocessing import DEFAULT_FEATURES


class ModelMetadata(BaseModel):
    mineral: str = "manganese"
    model_name: str
    version: str
    training_date: str | None = None
    feature_list: list[str] = Field(default_factory=list)
    training_dataset: str
    record_count: int | None = None
    metrics: dict[str, float] | None = None
    status: str


DEMO_MODEL_METADATA = ModelMetadata(
    model_name=MODEL_NAME,
    version=MODEL_VERSION,
    training_date=None,
    feature_list=list(DEFAULT_FEATURES),
    training_dataset="none - validated manganese-labelled data is not available",
    record_count=None,
    metrics=None,
    status="demo",
)


def metadata_from_training_result(result: object, dataset_name: str) -> ModelMetadata:
    """Convert a measured training result into serializable model metadata."""
    return ModelMetadata(
        model_name=result.model_name,
        version=result.version,
        training_date=result.training_date or date.today().isoformat(),
        feature_list=result.feature_list,
        training_dataset=dataset_name,
        record_count=result.record_count,
        metrics=result.metrics,
        status=result.status,
    )

from fastapi import APIRouter, HTTPException

from ..ml.manganese.model import DEMO_MODEL_METADATA
from ..ml.manganese.predict import predict_manganese, predict_manganese_batch
from ..ml.manganese.schemas import (
    ModelStatus,
    ManganeseBatchPredictionRequest,
    ManganesePrediction,
    ManganesePredictionRequest,
    TrainingDataUploadRequest,
)
from ..ml.manganese.training import TrainingDataValidation, validate_training_csv
from .maps import prospectivity as legacy_prospectivity
from .targets import TARGETS, manganese_target

router = APIRouter(prefix="/manganese", tags=["Manganese"])


@router.get("/targets")
def manganese_targets() -> list[dict]:
    return [manganese_target(target) for target in TARGETS]


@router.get("/targets/{target_id}")
def manganese_target_by_id(target_id: int) -> dict:
    for target in TARGETS:
        if target["id"] == target_id:
            return manganese_target(target)
    raise HTTPException(status_code=404, detail="Manganese target not found")


@router.get("/prospectivity")
def manganese_prospectivity() -> dict:
    return legacy_prospectivity()


@router.post("/predict", response_model=ManganesePrediction)
def predict(request: ManganesePredictionRequest) -> ManganesePrediction:
    return predict_manganese(request)


@router.post("/predict-batch", response_model=list[ManganesePrediction])
def predict_batch(request: ManganeseBatchPredictionRequest) -> list[ManganesePrediction]:
    return predict_manganese_batch(request.requests)


@router.post("/upload-data", response_model=TrainingDataValidation)
def upload_data(request: TrainingDataUploadRequest) -> TrainingDataValidation:
    try:
        return validate_training_csv(request.csv_text)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.get("/model/status", response_model=ModelStatus)
def model_status() -> ModelStatus:
    return ModelStatus(
        **DEMO_MODEL_METADATA.model_dump(),
        message="Demo screening interface only; requires a validated manganese training dataset.",
    )

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.target import ExplorationTarget
from app.schemas.ml import PredictionResponse
from pydantic import BaseModel
from app.services.ml_service import ml_predictor

router = APIRouter()

class PredictionRequest(BaseModel):
    latitude: float
    longitude: float

@router.post("/predict", response_model=PredictionResponse)
def predict_prospectivity(req: PredictionRequest):
    """
    Run the ML model (simulator) on a specific coordinate.
    """
    prediction = ml_predictor.predict(req.latitude, req.longitude)
    return {
        "latitude": req.latitude,
        "longitude": req.longitude,
        **prediction
    }

@router.get("/target/{target_id}/explanation", response_model=PredictionResponse)
def get_target_explanation(target_id: int, db: Session = Depends(get_db)):
    """
    Fetch SHAP explanation for an existing target.
    """
    target = db.query(ExplorationTarget).filter(ExplorationTarget.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
        
    prediction = ml_predictor.predict(target.latitude, target.longitude)
    return {
        "target_id": target.id,
        "latitude": target.latitude,
        "longitude": target.longitude,
        **prediction
    }

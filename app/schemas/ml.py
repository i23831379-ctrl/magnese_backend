from pydantic import BaseModel
from typing import List

class ShapFeature(BaseModel):
    feature_name: str
    feature_value: float
    shap_value: float

class PredictionResponse(BaseModel):
    target_id: int | None = None
    latitude: float
    longitude: float
    prospectivity_score: float
    base_value: float
    shap_features: List[ShapFeature]
    model_version: str

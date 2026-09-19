import random
import math

# A deterministic pseudo-random generator based on coordinates
def pseudo_random(lat: float, lon: float, seed: int = 42) -> float:
    # Very simple hash based on lat, lon, and seed
    val = math.sin(lat * 12.9898 + lon * 78.233 + seed) * 43758.5453
    return val - math.floor(val)

class ProspectivityPredictor:
    def __init__(self):
        self.base_value = 0.35
        self.model_version = "rf-v1.0.demo"
        
    def predict(self, latitude: float, longitude: float):
        """
        Simulates an ML model prediction and calculates mock SHAP values
        based deterministically on the provided coordinates.
        """
        # Simulate feature values based on location
        band4_refl = 0.1 + (pseudo_random(latitude, longitude, 1) * 0.4)
        elevation = 200 + (pseudo_random(latitude, longitude, 2) * 800)
        dist_to_fault = pseudo_random(latitude, longitude, 3) * 5000
        gravity_anomaly = -20 + (pseudo_random(latitude, longitude, 4) * 40)
        
        # Calculate impact/SHAP values (positive pushes score up, negative pushes down)
        # Higher band4 reflectance -> positive
        shap_band4 = (band4_refl - 0.25) * 0.8
        
        # Specific elevation band (e.g. 400-600) -> positive
        shap_elev = 0.15 - abs(elevation - 500) / 1000.0
        
        # Closer to fault -> positive
        shap_fault = (2500 - dist_to_fault) / 10000.0
        
        # Positive gravity anomaly -> positive
        shap_grav = gravity_anomaly / 100.0
        
        features = [
            {"feature_name": "Band 4 Reflectance", "feature_value": round(band4_refl, 3), "shap_value": round(shap_band4, 3)},
            {"feature_name": "Elevation (m)", "feature_value": round(elevation, 1), "shap_value": round(shap_elev, 3)},
            {"feature_name": "Dist to Fault (m)", "feature_value": round(dist_to_fault, 1), "shap_value": round(shap_fault, 3)},
            {"feature_name": "Gravity Anomaly (mGal)", "feature_value": round(gravity_anomaly, 2), "shap_value": round(shap_grav, 3)}
        ]
        
        # Ensure sum of SHAP + base_value = prediction
        total_shap = sum(f["shap_value"] for f in features)
        score = self.base_value + total_shap
        score = max(0.01, min(0.99, score)) # clamp between 0 and 1
        
        return {
            "prospectivity_score": round(score, 3),
            "base_value": self.base_value,
            "shap_features": features,
            "model_version": self.model_version
        }

ml_predictor = ProspectivityPredictor()

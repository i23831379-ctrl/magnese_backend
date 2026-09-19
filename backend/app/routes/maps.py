from math import cos, radians

from fastapi import APIRouter

from ..ml.manganese.config import classify_probability
from .targets import TARGETS, manganese_target

router = APIRouter(tags=["Maps"])

ZONE_RADIUS_KM = 5.0
ZONE_SHAPE = ((1.00, 0.00), (0.72, 0.68), (0.08, 1.00), (-0.78, 0.62), (-1.00, -0.10), (-0.58, -0.82), (0.14, -1.00), (0.86, -0.58))


def target_zone(target: dict) -> dict:
    probability = target["score"] / 100
    classification = classify_probability(probability)
    radius_latitude = ZONE_RADIUS_KM / 111.0
    radius_longitude = radius_latitude / cos(radians(target["latitude"]))
    coordinates = [
        [
            target["longitude"] + x * radius_longitude,
            target["latitude"] + y * radius_latitude,
        ]
        for x, y in ZONE_SHAPE
    ]
    coordinates.append(coordinates[0])
    return {
        "type": "Feature",
        "properties": {
            "zone_id": f"MNG-ZONE-{target['id']:03d}",
            "target_id": target["code"],
            "latitude": target["latitude"],
            "longitude": target["longitude"],
            "mineral": "manganese",
            "probability": probability,
            "confidence": target["confidence"] / 100,
            "zone": target["zone"],
            "score": target["score"],
            "manganese_probability": probability,
            "classification": classification,
            "priority": manganese_target(target)["priority"],
            "model_status": "demo",
        },
        "geometry": {"type": "Polygon", "coordinates": [coordinates]},
    }

@router.get("/maps/prospectivity")
def prospectivity():
    # Deterministic demo geometry, local to each target; not reserve boundaries.
    features = [target_zone(target) for target in TARGETS]
    return {"type":"FeatureCollection","features":features}

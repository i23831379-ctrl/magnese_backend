from fastapi import APIRouter, HTTPException
from typing import Any

from ..ml.manganese.config import MODEL_NAME, MODEL_STATUS, MODEL_VERSION, classify_probability, priority_for_classification

router = APIRouter(tags=["Targets"])

TARGETS: list[dict[str, Any]] = [
    {"id":1,"code":"MN-001","name":"Keonjhar North","latitude":21.68,"longitude":85.58,"score":92,"confidence":88,"zone":"HIGH","geology":"Banded iron formation","status":"Pending","factors":["Fe-Mn spectral response","Structural proximity","Favorable terrain"]},
    {"id":2,"code":"MN-002","name":"Sundargarh East","latitude":22.02,"longitude":84.78,"score":87,"confidence":84,"zone":"HIGH","geology":"Metasedimentary sequence","status":"Needs review","factors":["Alteration signature","Lineament density","Known occurrence proximity"]},
    {"id":3,"code":"MN-003","name":"Balaghat Ridge","latitude":21.86,"longitude":80.15,"score":81,"confidence":79,"zone":"HIGH","geology":"Mafic to metasedimentary contact","status":"Pending","factors":["Spectral ratio","Lithological contact","Slope pattern"]},
    {"id":4,"code":"MN-004","name":"Nagpur South","latitude":20.85,"longitude":79.25,"score":74,"confidence":73,"zone":"HIGH","geology":"Metamorphic terrain","status":"Validated","factors":["Geological structure","Terrain context","Spectral anomaly"]},
    {"id":5,"code":"MN-005","name":"Singhbhum West","latitude":22.52,"longitude":85.25,"score":68,"confidence":71,"zone":"MEDIUM","geology":"Iron formation corridor","status":"Needs review","factors":["Lineament density","Occurrence proximity"]},
    {"id":6,"code":"MN-006","name":"Bastar North","latitude":19.45,"longitude":81.82,"score":61,"confidence":65,"zone":"MEDIUM","geology":"Granite-greenstone terrain","status":"Pending","factors":["Spectral response","Terrain similarity"]},
    {"id":7,"code":"MN-007","name":"Gadchiroli East","latitude":20.18,"longitude":80.15,"score":55,"confidence":61,"zone":"MEDIUM","geology":"Metasedimentary rocks","status":"Pending","factors":["Lithology","Slope context"]},
    {"id":8,"code":"MN-008","name":"Jajpur Corridor","latitude":20.82,"longitude":86.15,"score":38,"confidence":48,"zone":"LOW","geology":"Mixed alluvial terrain","status":"Needs review","factors":["Weak spectral evidence"]},
    {"id":9,"code":"MN-009","name":"Koraput South","latitude":18.82,"longitude":82.72,"score":31,"confidence":43,"zone":"LOW","geology":"High-grade metamorphic terrain","status":"Pending","factors":["Limited training similarity"]},
    {"id":10,"code":"MN-010","name":"Raipur West","latitude":21.25,"longitude":81.95,"score":27,"confidence":39,"zone":"LOW","geology":"Sedimentary basin margin","status":"Pending","factors":["Low spectral response"]},
]


def manganese_target(target: dict[str, Any]) -> dict[str, Any]:
    probability = target["score"] / 100
    classification = classify_probability(probability)
    return {
        **target,
        "mineral": "manganese",
        "manganese_probability": probability,
        "classification": classification,
        "priority": priority_for_classification(classification),
        "feature_summary": target["factors"],
        "data_sources": ["demo target metadata"],
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "model_status": MODEL_STATUS,
    }

@router.get("/targets")
def list_targets():
    return [manganese_target(target) for target in TARGETS]

@router.get("/targets/{target_id}")
def get_target(target_id: int):
    for target in TARGETS:
        if target["id"] == target_id:
            return manganese_target(target)
    raise HTTPException(status_code=404, detail="Target not found")

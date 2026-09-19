from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.target import ExplorationTarget
from app.schemas.target import ExplorationTargetCreate, ExplorationTargetResponse
import random
from app.services.ml_service import ml_predictor

router = APIRouter()

@router.get("/", response_model=List[ExplorationTargetResponse])
def get_targets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)): 
    targets = db.query(ExplorationTarget).offset(skip).limit(limit).all()
    return targets

@router.post("/", response_model=ExplorationTargetResponse, status_code=status.HTTP_201_CREATED)
def create_target(target: ExplorationTargetCreate, db: Session = Depends(get_db)):
    db_target = ExplorationTarget(**target.model_dump())
    db.add(db_target)
    db.commit()
    db.refresh(db_target)
    return db_target

@router.get("/{target_id}", response_model=ExplorationTargetResponse)
def get_target(target_id: int, db: Session = Depends(get_db)):
    target = db.query(ExplorationTarget).filter(ExplorationTarget.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    return target

@router.put("/{target_id}/verify", response_model=ExplorationTargetResponse)
def verify_target(target_id: int, db: Session = Depends(get_db)):
    target = db.query(ExplorationTarget).filter(ExplorationTarget.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    target.is_verified = True
    db.commit()
    db.refresh(target)
    return target

@router.post("/generate", response_model=List[ExplorationTargetResponse])
def generate_targets(db: Session = Depends(get_db)):
    # Generate a couple of random targets near the central area
    base_lat, base_lon = 21.2, 79.3
    new_targets = []
    
    for i in range(3):
        lat = base_lat + (random.random() - 0.5) * 0.5
        lon = base_lon + (random.random() - 0.5) * 0.5
        score_data = ml_predictor.predict(lat, lon)
        score = score_data["prospectivity_score"]
        
        target = ExplorationTarget(
            name=f"Generated Zone {random.randint(100, 999)}",
            description="AI-generated target based on structural analysis.",
            latitude=lat,
            longitude=lon,
            prospectivity_score=score,
            is_verified=False
        )
        db.add(target)
        new_targets.append(target)
        
    db.commit()
    for t in new_targets:
        db.refresh(t)
    return new_targets

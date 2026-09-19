from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter()

@router.post("/", response_model=schemas.study_area.StudyAreaRead, status_code=status.HTTP_201_CREATED)
def create_study_area(study_area: schemas.study_area.StudyAreaCreate, db: Session = Depends(get_db)):
    db_obj = models.StudyArea(**study_area.model_dump(exclude_unset=True))
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/", response_model=list[schemas.study_area.StudyAreaRead])
def list_study_areas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.StudyArea).offset(skip).limit(limit).all()

@router.get("/{study_area_id}", response_model=schemas.study_area.StudyAreaRead)
def get_study_area(study_area_id: int, db: Session = Depends(get_db)):
    obj = db.query(models.StudyArea).filter(models.StudyArea.id == study_area_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="StudyArea not found")
    return obj

@router.put("/{study_area_id}", response_model=schemas.study_area.StudyAreaRead)
def update_study_area(study_area_id: int, updates: schemas.study_area.StudyAreaUpdate, db: Session = Depends(get_db)):
    obj = db.query(models.StudyArea).filter(models.StudyArea.id == study_area_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="StudyArea not found")
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{study_area_id}", response_model=schemas.study_area.StudyAreaRead)
def delete_study_area(study_area_id: int, db: Session = Depends(get_db)):
    obj = db.query(models.StudyArea).filter(models.StudyArea.id == study_area_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="StudyArea not found")
    db.delete(obj)
    db.commit()
    return obj

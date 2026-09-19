from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.dataset import Dataset
from app.schemas.dataset import DatasetCreate, DatasetRead, DatasetUpdate

router = APIRouter()

@router.post("/", response_model=DatasetRead, status_code=status.HTTP_201_CREATED)
def create_dataset(dataset: DatasetCreate, db: Session = Depends(get_db)):
    # Verify project exists (simplified, assume foreign key constraint will raise)
    db_dataset = Dataset(**dataset.model_dump(exclude_unset=True))
    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)
    return db_dataset

@router.get("/", response_model=List[DatasetRead])
def list_datasets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Dataset).offset(skip).limit(limit).all()

@router.get("/{dataset_id}", response_model=DatasetRead)
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return ds

@router.patch("/{dataset_id}", response_model=DatasetRead)
def update_dataset(dataset_id: int, updates: DatasetUpdate, db: Session = Depends(get_db)):
    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(ds, field, value)
    db.commit()
    db.refresh(ds)
    return ds

@router.delete("/{dataset_id}", response_model=DatasetRead)
def delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    # Soft delete
    ds.status = "archived"
    db.commit()
    db.refresh(ds)
    return ds

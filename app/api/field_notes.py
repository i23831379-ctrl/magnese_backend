from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db

router = APIRouter()

# Create a new field note
@router.post("/", response_model=schemas.field_note.FieldNoteRead, status_code=status.HTTP_201_CREATED)
def create_field_note(note: schemas.field_note.FieldNoteCreate, db: Session = Depends(get_db)):
    # Validate target exists
    target = db.query(models.target.ExplorationTarget).filter(models.target.ExplorationTarget.id == note.target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    db_note = models.field_note.FieldNote(
        target_id=note.target_id,
        user_id=getattr(note, "user_id", None),
        note_text=getattr(note, "note_text", None),
        verification_status=getattr(note, "verification_status", False),
        # legacy fields
        geologist_name=note.geologist_name,
        visit_date=note.visit_date,
        rock_sample=note.rock_sample,
        access_difficulty=note.access_difficulty,
        gps_accuracy_m=note.gps_accuracy_m,
        observations=note.observations,
        photo_filename=note.photo_filename,
        confidence_delta=note.confidence_delta,
        submitted_at=note.submitted_at,
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

# Get all field notes (admin view)
@router.get("/", response_model=List[schemas.field_note.FieldNoteRead])
def list_field_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    notes = db.query(models.field_note.FieldNote).offset(skip).limit(limit).all()
    return notes

# Get a single field note by ID
@router.get("/{note_id}", response_model=schemas.field_note.FieldNoteRead)
def get_field_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(models.field_note.FieldNote).filter(models.field_note.FieldNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Field note not found")
    return note

# Get notes for a specific target
@router.get("/targets/{target_id}", response_model=List[schemas.field_note.FieldNoteRead])
def get_notes_by_target(target_id: int, db: Session = Depends(get_db)):
    target = db.query(models.target.ExplorationTarget).filter(models.target.ExplorationTarget.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    notes = db.query(models.field_note.FieldNote).filter(models.field_note.FieldNote.target_id == target_id).all()
    return notes

# Update a field note (partial)
@router.patch("/{note_id}", response_model=schemas.field_note.FieldNoteRead)
def update_field_note(note_id: int, note_update: schemas.field_note.FieldNoteUpdate, db: Session = Depends(get_db)):
    note = db.query(models.field_note.FieldNote).filter(models.field_note.FieldNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Field note not found")
    update_data = note_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(note, key, value)
    db.commit()
    db.refresh(note)
    return note

# Delete a field note
@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_field_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(models.field_note.FieldNote).filter(models.field_note.FieldNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Field note not found")
    db.delete(note)
    db.commit()
    return

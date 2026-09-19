from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FieldNoteBase(BaseModel):
    geologist_name: str = Field(..., min_length=1)
    visit_date: datetime
    rock_sample: Optional[str] = None
    access_difficulty: str
    gps_accuracy_m: int
    observations: str
    photo_filename: Optional[str] = None
    confidence_delta: int

    class Config:
        from_attributes = True

class FieldNoteCreate(FieldNoteBase):
    target_id: int
    submitted_at: Optional[datetime] = None

class FieldNoteRead(FieldNoteBase):
    id: int
    target_id: int
    submitted_at: datetime

class FieldNoteUpdate(BaseModel):
    note_text: Optional[str] = None
    verification_status: Optional[bool] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

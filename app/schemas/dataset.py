from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator

class DatasetBase(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    project_id: int
    study_area_id: Optional[int] = None
    dataset_type: Optional[str] = None
    source: Optional[str] = None
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    format: Optional[str] = None
    # New fields for ingestion
    layer_type: str
    safe_filename: str
    processing_status: str = Field(default='uploaded')
    metadata_json: Optional[Any] = None
    crs: Optional[str] = None
    bounds: Optional[Any] = None
    width: Optional[int] = None
    height: Optional[int] = None
    band_count: Optional[int] = None
    resolution: Optional[float] = None
    nodata: Optional[float] = None
    is_active: int = 1
    status: Optional[str] = Field(default='uploaded')
    validation_status: Optional[str] = None
    extra_metadata: Optional[Any] = None

    @validator("status")
    def validate_status(cls, v):
        allowed = {"uploaded", "validating", "ready", "failed", "archived"}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v

class DatasetCreate(DatasetBase):
    pass

class DatasetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    study_area_id: Optional[int] = None
    dataset_type: Optional[str] = None
    source: Optional[str] = None
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    format: Optional[str] = None
    status: Optional[str] = None
    validation_status: Optional[str] = None
    extra_metadata: Optional[Any] = None

    @validator("status")
    def validate_status(cls, v):
        if v is None:
            return v
        allowed = {"uploaded", "validating", "ready", "failed", "archived"}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v

class DatasetRead(DatasetBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

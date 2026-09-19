from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field
from geojson_pydantic import MultiPolygon as GeoJSONMultiPolygon

class StudyAreaBase(BaseModel):
    name: str = Field(..., description="Name of the study area")
    description: Optional[str] = Field(None, description="Optional description")
    # Geometry as GeoJSON MultiPolygon
    geom: Optional[GeoJSONMultiPolygon] = Field(None, description="Geometry in GeoJSON MultiPolygon format")
    project_id: int = Field(..., description="ID of the related project")

class StudyAreaCreate(StudyAreaBase):
    pass

class StudyAreaUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    geom: Optional[GeoJSONMultiPolygon] = None
    project_id: Optional[int] = None

class StudyAreaRead(StudyAreaBase):
    id: int = Field(..., description="Primary key")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        orm_mode = True

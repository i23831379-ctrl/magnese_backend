from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ExplorationTargetBase(BaseModel):
    name: str
    description: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    ranking: Optional[int] = None  # NEW: ranking column
    is_verified: bool = False

class ExplorationTargetCreate(ExplorationTargetBase):
    pass

class ExplorationTargetResponse(ExplorationTargetBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

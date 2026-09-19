from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app.database import Base

# Use Text for geometry placeholder in SQLite
location_type = Text

class ExplorationTarget(Base):
    __tablename__ = "exploration_targets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    prospectivity_score = Column(Float, nullable=False)
    ranking = Column(Integer, nullable=True)  # NEW: target ranking
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    # Geometry column – stored as Text WKT in SQLite
    location = Column(location_type, nullable=True)

    # Optional foreign key to Project (nullable for demo data)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    project = relationship('Project', back_populates='exploration_targets')
    field_notes = relationship('FieldNote', back_populates='target', cascade='all, delete-orphan')

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app.database import Base

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    # Optional association to StudyArea
    study_area_id = Column(Integer, ForeignKey('study_areas.id'), nullable=True)

    # Phase‑3 fields
    dataset_type = Column(String, nullable=True)
    source = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    format = Column(String, nullable=True)
    status = Column(String, nullable=False, default="uploaded")
    validation_status = Column(String, nullable=True)
    extra_metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    project = relationship('Project', back_populates='datasets')
    study_area = relationship('StudyArea', back_populates='datasets')

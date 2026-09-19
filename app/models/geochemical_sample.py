from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
# Geometry import removed for SQLite compatibility
from app.database import Base

class GeochemicalSample(Base):
    __tablename__ = "geochemical_samples"

    id = Column(Integer, primary_key=True, index=True)
    sample_name = Column(String, nullable=False)
    location = Column(Text, nullable=True)  # Stored as WKT string for SQLite
    value = Column(Float, nullable=False)
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    dataset_id = Column(Integer, ForeignKey('datasets.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    project = relationship('Project', back_populates='geochemical_samples')

    # Relationships can be defined in Dataset model if needed

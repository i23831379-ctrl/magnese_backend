from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

# Geometry placeholder for SQLite (store WKT as Text)
area_type = Text

class RemoteSensingLayer(Base):
    __tablename__ = "remote_sensing_layers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    # Geometry representing area covered (Polygon) – stored as Text WKT
    area = Column(area_type, nullable=True)
    dataset_id = Column(Integer, ForeignKey('datasets.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    project = relationship('Project', back_populates='remote_sensing_layers')

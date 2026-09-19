from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Float, Text
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from sqlalchemy import Text
from app.database import Base

class GeologicalLayer(Base):
    __tablename__ = "geological_layers"

    # Enum definitions for layer type and processing status
    class LayerType(PyEnum):
        raster = "raster"
        dem = "dem"
        multispectral = "multispectral"
        vector = "vector"
        csv = "csv"

    class ProcessingStatus(PyEnum):
        uploaded = "uploaded"
        processing = "processing"
        ready = "ready"
        failed = "failed"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    geom = Column(Text, nullable=True)  # Stored as WKT string for SQLite
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)

    # New columns for data ingestion
    layer_type = Column(Enum(LayerType), nullable=False)
    file_path = Column(String, nullable=False)  # Relative path within storage
    safe_filename = Column(String, nullable=False)
    processing_status = Column(Enum(ProcessingStatus), nullable=False, default=ProcessingStatus.uploaded)
    metadata_json = Column(Text, nullable=True)  # JSON stored as text
    crs = Column(String, nullable=True)
    bounds = Column(Text, nullable=True)  # Store as JSON string or WKT
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    band_count = Column(Integer, nullable=True)
    resolution = Column(Float, nullable=True)
    nodata = Column(Float, nullable=True)
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship('Project', back_populates='geological_layers')

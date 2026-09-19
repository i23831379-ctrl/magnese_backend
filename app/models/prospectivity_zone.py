from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from sqlalchemy import Text
from app.database import Base

class ProspectivityZone(Base):
    __tablename__ = "prospectivity_zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    geom = Column(Text, nullable=True)  # Stored as WKT string for SQLite
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)

    project = relationship('Project', back_populates='prospectivity_zones')

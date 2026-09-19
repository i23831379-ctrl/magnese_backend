from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    owner = relationship('User', back_populates='projects')
    study_areas = relationship('StudyArea', back_populates='project')
    datasets = relationship('Dataset', back_populates='project')
    exploration_targets = relationship('ExplorationTarget', back_populates='project')
    prospectivity_zones = relationship('ProspectivityZone', back_populates='project')
    geological_layers = relationship('GeologicalLayer', back_populates='project')
    geochemical_samples = relationship('GeochemicalSample', back_populates='project')
    remote_sensing_layers = relationship('RemoteSensingLayer', back_populates='project')
    model_runs = relationship('ModelRun', back_populates='project')

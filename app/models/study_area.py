from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.orm import relationship
from app.database import Base
from app.config import settings

# Choose geometry column type based on database engine
if settings.DATABASE_URL.startswith('postgresql'):
    from geoalchemy2 import Geometry
    GeometryColumn = Geometry('MULTIPOLYGON', srid=4326)
else:
    # Fallback for SQLite: store WKT string
    GeometryColumn = Text

class StudyArea(Base):
    __tablename__ = "study_areas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    geom = Column(GeometryColumn, nullable=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)

    project = relationship('Project', back_populates='study_areas')
    datasets = relationship('Dataset', back_populates='study_area')

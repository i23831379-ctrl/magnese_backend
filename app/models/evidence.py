from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from datetime import datetime, timezone
from app.database import Base

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    model_run_id = Column(Integer, ForeignKey('model_runs.id'), nullable=False)
    target_id = Column(Integer, ForeignKey('exploration_targets.id'), nullable=False)
    description = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    # Relationships can be defined in ModelRun and ExplorationTarget if needed

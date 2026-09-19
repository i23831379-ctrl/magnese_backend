from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Text
from datetime import datetime, timezone
from app.database import Base

class TargetRanking(Base):
    __tablename__ = "target_rankings"

    id = Column(Integer, primary_key=True, index=True)
    model_run_id = Column(Integer, ForeignKey('model_runs.id'), nullable=False)
    target_id = Column(Integer, ForeignKey('exploration_targets.id'), nullable=False)
    rank = Column(Integer, nullable=False)
    score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    # Relationships can be defined in ModelRun and ExplorationTarget if needed

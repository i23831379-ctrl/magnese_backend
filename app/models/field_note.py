from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from datetime import datetime
from sqlalchemy.orm import relationship
from app.database import Base

class FieldNote(Base):
    __tablename__ = "field_notes"
    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, ForeignKey('exploration_targets.id'), nullable=False, index=True)
    user_id = Column(Integer, nullable=True, index=True)  # optional user reference (mock auth)
    note_text = Column(Text, nullable=True)
    verification_status = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.utcnow())
    updated_at = Column(DateTime, default=lambda: datetime.utcnow(), onupdate=lambda: datetime.utcnow())
    # Existing fields retained for backward compatibility
    geologist_name = Column(String, nullable=False)
    visit_date = Column(DateTime, nullable=False)
    rock_sample = Column(String, nullable=True)
    access_difficulty = Column(String, nullable=False)
    gps_accuracy_m = Column(Integer, nullable=False)
    observations = Column(Text, nullable=False)
    photo_filename = Column(String, nullable=True)
    confidence_delta = Column(Integer, nullable=False)
    submitted_at = Column(DateTime, default=lambda: datetime.utcnow())

    target = relationship('ExplorationTarget', back_populates='field_notes')

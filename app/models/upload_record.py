"""
UploadRecord — lightweight, FK-free table that tracks every file uploaded
through the Data Import endpoint.  No project / user FKs so it works in
the demo context without authentication.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from app.database import Base


class UploadRecord(Base):
    __tablename__ = "upload_records"

    id              = Column(Integer, primary_key=True, index=True)

    # ── File identity ──────────────────────────────────────────────
    original_filename = Column(String, nullable=False)
    safe_filename     = Column(String, nullable=False)
    file_path         = Column(String, nullable=False)   # relative to storage root
    file_size_bytes   = Column(Integer, nullable=False)
    file_type         = Column(String, nullable=False)   # "csv" | "vector" | "raster"

    # ── Spatial metadata (populated when available) ─────────────────
    crs               = Column(String,  nullable=True)
    bounds_json       = Column(Text,    nullable=True)   # JSON "[minX,minY,maxX,maxY]"

    # ── Raster-only metadata ────────────────────────────────────────
    width             = Column(Integer, nullable=True)
    height            = Column(Integer, nullable=True)
    band_count        = Column(Integer, nullable=True)
    resolution        = Column(Float,   nullable=True)
    nodata            = Column(Float,   nullable=True)

    # ── CSV/Vector metadata ─────────────────────────────────────────
    row_count         = Column(Integer, nullable=True)
    feature_count     = Column(Integer, nullable=True)
    column_names_json = Column(Text,    nullable=True)   # JSON list of column names

    # ── Status ──────────────────────────────────────────────────────
    processing_status = Column(String, nullable=False, default="processed")
    error_message     = Column(Text, nullable=True)

    # ── Timestamps ──────────────────────────────────────────────────
    created_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at  = Column(DateTime,
                         default=lambda: datetime.now(timezone.utc),
                         onupdate=lambda: datetime.now(timezone.utc))

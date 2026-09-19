"""
Maps API — /api/maps

Exposes geospatial layers uploaded through the Data Import workflow.
Backed exclusively by the UploadRecord table (no project/user FK deps).

Endpoints:
    GET  /api/maps/layers              — list all available layers
    GET  /api/maps/layers/{layer_id}   — detail + GeoJSON (CSV/vector) or metadata (raster)
"""

import csv
import io
import json
import os
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.upload_record import UploadRecord

router = APIRouter()

# Absolute path to the backend directory (used to resolve stored file_path values)
_BACKEND_DIR = Path(__file__).resolve().parents[2]   # backend/


# ──────────────────────────────────────────────────────────────────────────────
# Coordinate validation helpers
# ──────────────────────────────────────────────────────────────────────────────

def _valid_lon(v: float) -> bool:
    return -180.0 <= v <= 180.0


def _valid_lat(v: float) -> bool:
    return -90.0 <= v <= 90.0


def _safe_float(val: str) -> Optional[float]:
    """Return float or None if conversion fails."""
    try:
        return float(val.strip())
    except (ValueError, AttributeError):
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Geometry converters
# ──────────────────────────────────────────────────────────────────────────────

def _csv_to_geojson(file_path: Path, record: UploadRecord) -> dict:
    """
    Convert a CSV file with latitude/longitude columns to a GeoJSON
    FeatureCollection.  Skips rows with missing or invalid coordinates.
    All other columns are preserved as Feature properties.
    """
    try:
        content = file_path.read_bytes()
        text = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
        cols = list(reader.fieldnames or [])
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not read CSV: {exc}",
        )

    # Detect lat/lon column names (case-insensitive)
    lat_col = next((c for c in cols if c.strip().lower() in ("latitude", "lat")), None)
    lon_col = next((c for c in cols if c.strip().lower() in ("longitude", "lon", "lng", "long")), None)

    if not lat_col or not lon_col:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "CSV does not contain recognisable latitude/longitude columns. "
                f"Detected columns: {cols}"
            ),
        )

    features = []
    skipped = 0
    xs, ys = [], []

    for row in rows:
        lat_raw = row.get(lat_col, "")
        lon_raw = row.get(lon_col, "")
        lat = _safe_float(lat_raw)
        lon = _safe_float(lon_raw)

        if lat is None or lon is None:
            skipped += 1
            continue
        if not _valid_lat(lat) or not _valid_lon(lon):
            skipped += 1
            continue

        xs.append(lon)
        ys.append(lat)

        # Properties: all columns except the coordinate ones
        props = {k: v for k, v in row.items() if k not in (lat_col, lon_col)}
        # Also keep the raw coordinate values as properties for display
        props[lat_col] = lat
        props[lon_col] = lon

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat],
            },
            "properties": props,
        })

    bbox = [min(xs), min(ys), max(xs), max(ys)] if xs and ys else None

    return {
        "type": "FeatureCollection",
        "features": features,
        "_meta": {
            "source_file": record.original_filename,
            "total_rows": len(rows),
            "valid_features": len(features),
            "skipped_rows": skipped,
            "lat_column": lat_col,
            "lon_column": lon_col,
            "crs": "EPSG:4326",
            "bbox": bbox,
        },
    }


def _geojson_from_file(file_path: Path, record: UploadRecord) -> dict:
    """
    Load a GeoJSON file, validate it, and return a normalised
    FeatureCollection with computed metadata.
    """
    try:
        data = json.loads(file_path.read_bytes().decode("utf-8"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not parse GeoJSON file: {exc}",
        )

    geo_type = data.get("type", "")
    supported = {
        "FeatureCollection", "Feature",
        "Point", "MultiPoint",
        "LineString", "MultiLineString",
        "Polygon", "MultiPolygon",
        "GeometryCollection",
    }
    if geo_type not in supported:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported GeoJSON type: '{geo_type}'",
        )

    # Normalise to FeatureCollection
    if geo_type == "FeatureCollection":
        features = data.get("features", [])
    elif geo_type == "Feature":
        features = [data]
    else:
        # Bare geometry — wrap in Feature
        features = [{"type": "Feature", "geometry": data, "properties": {}}]

    # Compute bounding box
    xs, ys = [], []

    def _collect(geom: Optional[dict]):
        if not geom:
            return
        t = geom.get("type", "")
        c = geom.get("coordinates")
        if not c:
            return
        if t == "Point":
            xs.append(c[0]); ys.append(c[1])
        elif t in ("MultiPoint", "LineString"):
            for pt in c:
                xs.append(pt[0]); ys.append(pt[1])
        elif t in ("MultiLineString", "Polygon"):
            for ring in c:
                for pt in ring:
                    xs.append(pt[0]); ys.append(pt[1])
        elif t == "MultiPolygon":
            for poly in c:
                for ring in poly:
                    for pt in ring:
                        xs.append(pt[0]); ys.append(pt[1])

    for feat in features:
        geom = feat.get("geometry") if feat.get("type") == "Feature" else feat
        _collect(geom)

    bbox = [min(xs), min(ys), max(xs), max(ys)] if xs and ys else None
    geom_types = list({
        f.get("geometry", {}).get("type")
        for f in features
        if isinstance(f.get("geometry"), dict)
    } - {None})

    fc: dict = {"type": "FeatureCollection", "features": features}
    if "crs" in data:
        fc["crs"] = data["crs"]

    fc["_meta"] = {
        "source_file": record.original_filename,
        "feature_count": len(features),
        "geometry_types": geom_types,
        "crs": record.crs or "EPSG:4326",
        "bbox": bbox,
    }
    return fc


def _resolve_file(record: UploadRecord) -> Path:
    """
    Resolve the absolute file path from a DB record.
    Raises 404 if the file no longer exists on disk.
    Never trusts client input for the path.
    """
    file_path = _BACKEND_DIR / record.file_path
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Layer file not found on disk: {record.original_filename}",
        )
    return file_path


def _layer_summary(r: UploadRecord) -> dict:
    return {
        "id":          r.id,
        "name":        r.original_filename,
        "type":        r.file_type,         # "csv" | "vector" | "raster"
        "file_type":   r.file_type,
        "crs":         r.crs,
        "bbox":        json.loads(r.bounds_json) if r.bounds_json else None,
        "size_bytes":  r.file_size_bytes,
        "status":      r.processing_status,
        "uploaded_at": r.created_at.isoformat() if r.created_at else None,
        # Extra hints
        "row_count":     r.row_count,
        "feature_count": r.feature_count,
        "width":         r.width,
        "height":        r.height,
        "band_count":    r.band_count,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────────────────────────────────────

@router.get(
    "/layers",
    summary="List all available geospatial layers",
)
def list_layers(db: Session = Depends(get_db)):
    """
    Returns all successfully processed upload records as map layers.
    """
    records = (
        db.query(UploadRecord)
        .filter(UploadRecord.processing_status == "processed")
        .order_by(UploadRecord.created_at.desc())
        .all()
    )
    return {
        "layers": [_layer_summary(r) for r in records],
        "total": len(records),
    }


@router.get(
    "/layers/{layer_id}",
    summary="Get layer detail and GeoJSON representation",
)
def get_layer(layer_id: int, db: Session = Depends(get_db)):
    """
    Returns full layer metadata.
    For CSV and GeoJSON files, also returns a GeoJSON FeatureCollection
    suitable for direct use in MapLibre.

    For raster (TIFF) files, returns metadata only with `geojson: null`
    and `render_type: "raster_metadata"`.
    """
    record = db.query(UploadRecord).filter(UploadRecord.id == layer_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Layer #{layer_id} not found.",
        )

    summary = _layer_summary(record)
    file_path = _resolve_file(record)

    if record.file_type == "csv":
        geojson = _csv_to_geojson(file_path, record)
        render_type = "point_layer"
    elif record.file_type == "vector":
        geojson = _geojson_from_file(file_path, record)
        render_type = "vector_layer"
    elif record.file_type == "raster":
        geojson = None
        render_type = "raster_metadata"
        summary["render_note"] = (
            "Raster rendering requires a tile server. "
            "Metadata is available; client-side rendering is not currently supported."
        )
    else:
        geojson = None
        render_type = "unknown"

    return {
        **summary,
        "render_type": render_type,
        "geojson": geojson,
    }

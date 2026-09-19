"""
Data Import API — POST /api/data-import/upload

Accepts CSV, GeoJSON/JSON, and GeoTIFF uploads.
* CSV: pure-Python stdlib (csv, io)
* GeoJSON: stdlib json
* GeoTIFF: attempted via rasterio (optional); if unavailable, returns basic metadata.

All files are saved safely under backend/storage/uploads/.
An UploadRecord row is persisted to the SQLite database.
Response shape is compatible with the DataImport.tsx frontend component.
"""

import csv
import io
import json
import os
import struct
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.upload_record import UploadRecord

router = APIRouter()

# ──────────────────────────────────────────────────────────────────────────────
# Storage configuration
# ──────────────────────────────────────────────────────────────────────────────

# Resolve to  <repo-root>/backend/storage/uploads
_BACKEND_DIR = Path(__file__).resolve().parents[2]  # backend/
STORAGE_DIR  = _BACKEND_DIR / "storage" / "uploads"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS: set[str] = {".csv", ".geojson", ".json", ".tif", ".tiff"}
MAX_UPLOAD_BYTES: int = 100 * 1024 * 1024  # 100 MB

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _sanitize_filename(name: str) -> str:
    """Strip path components and keep only safe characters."""
    base = Path(name).name
    safe = "".join(
        c for c in base
        if c.isalnum() or c in ("-", "_", ".")
    )
    if not safe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename contains no valid characters after sanitisation.",
        )
    return safe


def _unique_filename(original: str) -> str:
    safe = _sanitize_filename(original)
    uid  = uuid.uuid4().hex[:12]
    return f"{uid}_{safe}"


def _save_upload(upload: UploadFile) -> tuple[Path, int]:
    """Persist the upload to disk, return (dest_path, size_bytes)."""
    safe_name = _unique_filename(upload.filename or "upload")
    dest      = STORAGE_DIR / safe_name
    size      = 0
    with dest.open("wb") as fh:
        while chunk := upload.file.read(65_536):
            size += len(chunk)
            if size > MAX_UPLOAD_BYTES:
                fh.close()
                dest.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File exceeds maximum allowed size of {MAX_UPLOAD_BYTES // (1024*1024)} MB.",
                )
            fh.write(chunk)
    return dest, size


# ──────────────────────────────────────────────────────────────────────────────
# Format-specific processors (pure Python, no heavy GIS dependencies)
# ──────────────────────────────────────────────────────────────────────────────

def _process_csv(content: bytes) -> dict:
    """Extract row count, column names, lat/lon columns, and bounding box."""
    try:
        text   = content.decode("utf-8-sig")   # handle BOM if present
        reader = csv.DictReader(io.StringIO(text))
        rows   = list(reader)
        cols   = list(reader.fieldnames or [])
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file is not valid UTF-8.",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CSV parsing error: {exc}",
        )

    if not cols:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file has no column headers.",
        )

    lat_col = next(
        (c for c in cols if c.strip().lower() in ("latitude", "lat")), None
    )
    lon_col = next(
        (c for c in cols if c.strip().lower() in ("longitude", "lon", "lng", "long")), None
    )

    bounds = None
    if lat_col and lon_col:
        try:
            lats = [float(r[lat_col]) for r in rows if r.get(lat_col, "").strip()]
            lons = [float(r[lon_col]) for r in rows if r.get(lon_col, "").strip()]
            if lats and lons:
                bounds = [min(lons), min(lats), max(lons), max(lats)]
        except ValueError:
            pass  # non-numeric lat/lon — skip bounds

    return {
        "file_type":          "csv",
        "row_count":          len(rows),
        "column_names":       cols,
        "lat_column":         lat_col,
        "lon_column":         lon_col,
        "bounds":             bounds,
        "crs":                "EPSG:4326" if lat_col and lon_col else None,
    }


def _process_geojson(content: bytes) -> dict:
    """Validate GeoJSON FeatureCollection and extract feature count + bounds."""
    try:
        data = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"GeoJSON is not valid JSON: {exc}",
        )

    geojson_type = data.get("type", "")
    if geojson_type not in ("FeatureCollection", "Feature",
                             "Point", "MultiPoint",
                             "LineString", "MultiLineString",
                             "Polygon", "MultiPolygon",
                             "GeometryCollection"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported GeoJSON type: '{geojson_type}'. Expected FeatureCollection or geometry type.",
        )

    features: list = []
    if geojson_type == "FeatureCollection":
        features = data.get("features", [])
    elif geojson_type == "Feature":
        features = [data]

    # Extract CRS (GeoJSON RFC 7946 assumes WGS84; some older files declare it)
    crs = None
    if "crs" in data:
        crs_obj = data["crs"]
        if isinstance(crs_obj, dict):
            crs = crs_obj.get("properties", {}).get("name") or crs_obj.get("type")

    # Collect all coordinate pairs for bounds
    xs: list[float] = []
    ys: list[float] = []

    def _collect_coords(geom: Optional[dict]):
        if not geom:
            return
        t    = geom.get("type", "")
        crds = geom.get("coordinates")
        if not crds:
            return

        if t == "Point":
            xs.append(crds[0]); ys.append(crds[1])
        elif t in ("MultiPoint", "LineString"):
            for c in crds:
                xs.append(c[0]); ys.append(c[1])
        elif t in ("MultiLineString", "Polygon"):
            for ring in crds:
                for c in ring:
                    xs.append(c[0]); ys.append(c[1])
        elif t == "MultiPolygon":
            for poly in crds:
                for ring in poly:
                    for c in ring:
                        xs.append(c[0]); ys.append(c[1])

    for feat in features:
        _collect_coords(feat.get("geometry") if feat.get("type") == "Feature" else feat)

    # Also handle bare geometry at top level
    if geojson_type not in ("FeatureCollection", "Feature"):
        _collect_coords(data)

    bounds = [min(xs), min(ys), max(xs), max(ys)] if xs and ys else None
    geom_types = list({
        f.get("geometry", {}).get("type")
        for f in features
        if isinstance(f.get("geometry"), dict)
    } - {None})

    return {
        "file_type":     "vector",
        "feature_count": len(features),
        "geometry_types": geom_types,
        "crs":           crs or "EPSG:4326",   # GeoJSON default
        "bounds":        bounds,
    }


def _process_raster_minimal(file_path: Path) -> dict:
    """
    Extract minimal TIFF metadata without rasterio.
    Reads IFD0 to obtain ImageWidth, ImageLength, BitsPerSample.
    Falls back gracefully if the file is not a standard TIFF.
    """
    result: dict = {"file_type": "raster", "crs": None, "bounds": None}
    try:
        with file_path.open("rb") as fh:
            hdr = fh.read(4)
            if len(hdr) < 4:
                raise ValueError("File too small to be a TIFF.")
            byte_order = hdr[:2]
            if byte_order == b"II":
                endian = "<"
            elif byte_order == b"MM":
                endian = ">"
            else:
                raise ValueError("Not a TIFF file (bad byte-order mark).")

            magic = struct.unpack(endian + "H", hdr[2:4])[0]
            if magic != 42:
                raise ValueError("Not a Classic TIFF (magic number mismatch).")

            # IFD0 offset
            fh.seek(4)
            ifd_offset = struct.unpack(endian + "I", fh.read(4))[0]
            fh.seek(ifd_offset)
            num_entries = struct.unpack(endian + "H", fh.read(2))[0]

            width = height = None
            for _ in range(num_entries):
                entry = fh.read(12)
                if len(entry) < 12:
                    break
                tag, dtype, count = struct.unpack(endian + "HHI", entry[:8])
                val_bytes = entry[8:12]
                # SHORT = 3, LONG = 4
                if dtype == 3:
                    val = struct.unpack(endian + "H", val_bytes[:2])[0]
                elif dtype == 4:
                    val = struct.unpack(endian + "I", val_bytes)[0]
                else:
                    val = None
                if tag == 256:   # ImageWidth
                    width = val
                elif tag == 257: # ImageLength
                    height = val

            if width:  result["width"]  = width
            if height: result["height"] = height

    except Exception as exc:
        # Non-fatal — return what we have, note the issue
        result["parse_warning"] = str(exc)

    return result


# ──────────────────────────────────────────────────────────────────────────────
# Endpoint
# ──────────────────────────────────────────────────────────────────────────────

@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Upload a geospatial dataset (CSV, GeoJSON, GeoTIFF)",
)
def upload_dataset(
    file: UploadFile = File(...),
    db:   Session    = Depends(get_db),
):
    # ── 1. Basic validation ──────────────────────────────────────────
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided.",
        )

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unsupported file type '{ext}'. "
                f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            ),
        )

    # ── 2. Save to disk ─────────────────────────────────────────────
    saved_path, size_bytes = _save_upload(file)

    # ── 3. Parse / extract metadata ─────────────────────────────────
    meta: dict = {}
    try:
        content = saved_path.read_bytes()

        if ext == ".csv":
            meta = _process_csv(content)
        elif ext in (".geojson", ".json"):
            meta = _process_geojson(content)
        elif ext in (".tif", ".tiff"):
            meta = _process_raster_minimal(saved_path)
        else:
            # Should never reach here due to earlier check
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type.",
            )
    except HTTPException:
        saved_path.unlink(missing_ok=True)
        raise
    except Exception as exc:
        saved_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"File could not be processed: {exc}",
        )

    # ── 4. Persist to database ──────────────────────────────────────
    bounds       = meta.get("bounds")
    col_names    = meta.get("column_names")

    record = UploadRecord(
        original_filename = file.filename,
        safe_filename     = saved_path.name,
        file_path         = str(saved_path.relative_to(_BACKEND_DIR)),
        file_size_bytes   = size_bytes,
        file_type         = meta.get("file_type", "unknown"),
        crs               = meta.get("crs"),
        bounds_json       = json.dumps(bounds) if bounds else None,
        width             = meta.get("width"),
        height            = meta.get("height"),
        band_count        = meta.get("band_count"),
        resolution        = meta.get("resolution"),
        nodata            = meta.get("nodata"),
        row_count         = meta.get("row_count"),
        feature_count     = meta.get("feature_count"),
        column_names_json = json.dumps(col_names) if col_names else None,
        processing_status = "processed",
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # ── 5. Return response compatible with DataImport.tsx ────────────
    return {
        "success":    True,
        "dataset_id": record.id,
        "layer_id":   record.id,        # alias — frontend uses either key
        "filename":   record.original_filename,
        "safe_filename": record.safe_filename,
        "file_type":  record.file_type,
        "layer_type": record.file_type,  # legacy alias
        "crs":        record.crs,
        "bbox":       bounds,
        "bounds":     bounds,            # legacy alias
        "size":       size_bytes,
        "size_bytes": size_bytes,        # legacy alias
        "band_count": record.band_count,
        "bands":      record.band_count, # legacy alias
        "width":      record.width,
        "height":     record.height,
        "row_count":  record.row_count,
        "feature_count": record.feature_count,
        "column_names":  col_names,
        "processing_status": record.processing_status,
        "status":     "processed",
        "uploaded_at": record.created_at.isoformat() if record.created_at else None,
        # Forward any parse warnings (non-fatal)
        "warnings":   [meta["parse_warning"]] if "parse_warning" in meta else [],
    }


@router.get(
    "/records",
    summary="List recent upload records",
)
def list_upload_records(db: Session = Depends(get_db), limit: int = 20):
    records = (
        db.query(UploadRecord)
        .order_by(UploadRecord.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id":               r.id,
            "filename":         r.original_filename,
            "file_type":        r.file_type,
            "size_bytes":       r.file_size_bytes,
            "status":           r.processing_status,
            "uploaded_at":      r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]

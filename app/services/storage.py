import os
import uuid
import shutil
from pathlib import Path
from fastapi import HTTPException

BASE_STORAGE = Path(__file__).resolve().parents[2] / 'storage'
UPLOADS_DIR = BASE_STORAGE / 'uploads'
RASTERS_DIR = BASE_STORAGE / 'rasters'
VECTORS_DIR = BASE_STORAGE / 'vectors'
REPORTS_DIR = BASE_STORAGE / 'reports'

ALLOWED_EXTENSIONS = {'.tif', '.tiff', '.geojson', '.json', '.csv'}
MAX_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB

def ensure_directories():
    for p in (UPLOADS_DIR, RASTERS_DIR, VECTORS_DIR, REPORTS_DIR):
        p.mkdir(parents=True, exist_ok=True)

def sanitize_filename(filename: str) -> str:
    """Allow only alphanumerics, hyphens, underscores, and dot. Remove any path components."""
    name = Path(filename).name
    allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_."
    safe = ''.join(c for c in name if c in allowed)
    if not safe:
        raise HTTPException(status_code=400, detail='Invalid filename after sanitization')
    return safe

def generate_safe_filename(original: str) -> str:
    safe = sanitize_filename(original)
    uid = uuid.uuid4().hex
    return f"{uid}_{safe}"

def save_upload_file(upload_file, subdir: Path) -> Path:
    ensure_directories()
    if not upload_file.filename:
        raise HTTPException(status_code=400, detail='No filename provided')
    ext = Path(upload_file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail='Unsupported file extension')
    # FastAPI's UploadFile does not expose size directly; rely on client to respect limit
    safe_name = generate_safe_filename(upload_file.filename)
    dest_path = subdir / safe_name
    with dest_path.open('wb') as f:
        shutil.copyfileobj(upload_file.file, f)
    return dest_path

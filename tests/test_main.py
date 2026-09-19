"""
Backend integration tests for MANGANEX AI.

Run from backend/ directory:
    pytest tests/ -v
"""

import io
import json
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def fresh_tables():
    """Re-create all tables in a clean state for every test."""
    Base.metadata.create_all(bind=engine)
    yield
    # Optionally drop after — keep tables to allow inspection if needed


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Smoke tests
# ---------------------------------------------------------------------------

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["project"] == "MANGANEX AI"
    assert body["status"]  == "online"


def test_api_health(client):
    """GET /api/health — returns {"status": "ok", "mode": "demo"}"""
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "mode" in body


# ---------------------------------------------------------------------------
# Data Import — POST /api/data-import/upload
# ---------------------------------------------------------------------------

CSV_VALID = b"""latitude,longitude,mn_pct,rock_type
21.431,79.811,8.2,schist
21.432,79.821,12.5,quartzite
21.141,79.081,6.8,gneiss
"""

CSV_NO_LATLON = b"""sample_id,mn_pct,rock_type
S001,8.2,schist
S002,12.5,quartzite
"""

GEOJSON_VALID = json.dumps({
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [79.811, 21.431]},
            "properties": {"name": "Zone Alpha"}
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [79.821, 21.432]},
            "properties": {"name": "Zone Beta"}
        }
    ]
}).encode()


def test_upload_csv_success(client):
    """Valid CSV with lat/lon columns → 201, success=true, DB record created."""
    response = client.post(
        "/api/data-import/upload",
        files={"file": ("test_samples.csv", io.BytesIO(CSV_VALID), "text/csv")},
    )
    assert response.status_code == 201, response.text
    body = response.json()

    assert body["success"]      is True
    assert body["file_type"]    == "csv"
    assert body["filename"]     == "test_samples.csv"
    assert body["row_count"]    == 3
    assert body["status"]       == "processed"
    assert isinstance(body["size_bytes"], int) and body["size_bytes"] > 0

    # Bounding box should be present since lat/lon are valid
    assert body["bbox"] is not None
    assert len(body["bbox"]) == 4


def test_upload_csv_no_latlon_still_accepted(client):
    """CSV without lat/lon → still accepted (bbox is None, CRS is None)."""
    response = client.post(
        "/api/data-import/upload",
        files={"file": ("no_coords.csv", io.BytesIO(CSV_NO_LATLON), "text/csv")},
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["success"]   is True
    assert body["bbox"]      is None
    assert body["crs"]       is None


def test_upload_geojson_success(client):
    """Valid GeoJSON FeatureCollection → 201, feature_count = 2."""
    response = client.post(
        "/api/data-import/upload",
        files={"file": ("zones.geojson", io.BytesIO(GEOJSON_VALID), "application/json")},
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["success"]        is True
    assert body["file_type"]      == "vector"
    assert body["feature_count"]  == 2
    assert body["crs"]            == "EPSG:4326"
    assert body["bbox"]           is not None


def test_upload_invalid_extension(client):
    """Unsupported extension → 400."""
    response = client.post(
        "/api/data-import/upload",
        files={"file": ("malware.exe", io.BytesIO(b"MZ\x00\x00"), "application/octet-stream")},
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_missing_file(client):
    """No file attached → FastAPI should return 422 Unprocessable Entity."""
    response = client.post("/api/data-import/upload")
    assert response.status_code == 422


def test_upload_corrupt_csv(client):
    """CSV file that is actually binary garbage → 400."""
    garbage = bytes(range(256)) * 4  # non-UTF-8 bytes
    response = client.post(
        "/api/data-import/upload",
        files={"file": ("bad.csv", io.BytesIO(garbage), "text/csv")},
    )
    # The processor raises HTTP 400 for non-UTF-8 CSV
    assert response.status_code == 400
    assert "not valid UTF-8" in response.json()["detail"]


def test_upload_corrupt_geojson(client):
    """Malformed JSON in a .geojson file → 400."""
    bad_json = b"{not valid json!!!"
    response = client.post(
        "/api/data-import/upload",
        files={"file": ("bad.geojson", io.BytesIO(bad_json), "application/json")},
    )
    assert response.status_code == 400
    assert "not valid JSON" in response.json()["detail"]


def test_database_record_created(client):
    """Upload creates a record visible via GET /api/data-import/records."""
    client.post(
        "/api/data-import/upload",
        files={"file": ("record_test.csv", io.BytesIO(CSV_VALID), "text/csv")},
    )
    records_resp = client.get("/api/data-import/records")
    assert records_resp.status_code == 200
    records = records_resp.json()
    assert len(records) >= 1
    filenames = [r["filename"] for r in records]
    assert "record_test.csv" in filenames


def test_upload_json_as_geojson(client):
    """A .json file containing valid GeoJSON is accepted."""
    response = client.post(
        "/api/data-import/upload",
        files={"file": ("data.json", io.BytesIO(GEOJSON_VALID), "application/json")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["file_type"] == "vector"

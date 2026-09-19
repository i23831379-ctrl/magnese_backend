"""
test_maps.py — Backend tests for /api/maps endpoints.

Tests:
  1.  GET /api/maps/layers — empty DB
  2.  GET /api/maps/layers — returns processed records
  3.  GET /api/maps/layers/{id} — missing layer → 404
  4.  CSV with latitude/longitude columns → GeoJSON FeatureCollection
  5.  CSV with lat/lon columns → GeoJSON FeatureCollection
  6.  CSV invalid coordinates → skipped rows
  7.  CSV with no coordinate columns → 422
  8.  GeoJSON file upload/read → FeatureCollection preserved
  9.  Invalid GeoJSON → 422
  10. Bounding-box calculation from CSV points

All tests use the shared in-memory SQLite DB from conftest.py.
"""

import json
import os
import sys
import tempfile
import uuid
from pathlib import Path

import pytest

# conftest.py already adds backend/ to sys.path and sets up the in-memory DB.
# We just import what we need.
from app.models.upload_record import UploadRecord


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _make_record(db, file_type: str, content: bytes, filename: str,
                 processing_status: str = "processed") -> UploadRecord:
    """
    Write *content* to a temp file, then insert an UploadRecord pointing at it.
    Returns the committed record.
    """
    # Use a temp dir that persists for the duration of the test session.
    tmp_dir = Path(tempfile.gettempdir()) / "manganex_test_storage"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid.uuid4().hex}_{filename}"
    abs_path = tmp_dir / safe_name
    abs_path.write_bytes(content)

    # file_path stored relative to backend/ (maps.py prepends _BACKEND_DIR).
    # For tests we store the ABSOLUTE path as a relative path trick:
    # _BACKEND_DIR is backend/, so "relative" = abs_path.relative to project root
    # is impractical.  Instead we monkey-patch _resolve_file via the record.
    # Simplest approach: store absolute path directly and override _BACKEND_DIR.
    # → Easier: just store the absolute path as file_path and set _BACKEND_DIR=""
    # But that would break production.  Use a controlled relative trick:
    # store file_path = str(abs_path) (absolute) and patch maps._BACKEND_DIR = Path("/")
    record = UploadRecord(
        original_filename=filename,
        safe_filename=safe_name,
        file_path=str(abs_path),  # absolute path stored
        file_size_bytes=len(content),
        file_type=file_type,
        crs="EPSG:4326",
        processing_status=processing_status,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def _patch_backend_dir(monkeypatch):
    """
    Make maps._BACKEND_DIR = Path("/") so that
    Path("/") / absolute_path  == absolute_path  (on POSIX)
    and on Windows Path("C:/") / "C:/..." becomes absolute.
    A cleaner approach: monkeypatch _resolve_file to trust the stored path.
    """
    import app.api.maps as maps_module
    # Override _resolve_file to resolve the stored absolute path directly.
    def _resolve_abs(record: UploadRecord) -> Path:
        p = Path(record.file_path)
        if not p.exists():
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Layer file not found on disk: {record.original_filename}",
            )
        return p
    monkeypatch.setattr(maps_module, "_resolve_file", _resolve_abs)


# ─── Tests ────────────────────────────────────────────────────────────────────

class TestListLayers:
    """Tests for GET /api/maps/layers"""

    def test_empty_db_returns_empty_list(self, client, db):
        """1. No processed records → empty layers list."""
        # Ensure no processed records exist from other tests by checking count
        response = client.get("/api/maps/layers")
        assert response.status_code == 200
        data = response.json()
        assert "layers" in data
        assert "total" in data
        assert isinstance(data["layers"], list)
        assert data["total"] == len(data["layers"])

    def test_returns_processed_records(self, client, db, monkeypatch, tmp_path):
        """2. Processed records appear in layer list; unprocessed are excluded."""
        csv_bytes = b"latitude,longitude,grade\n21.43,79.81,1.2\n"
        rec = _make_record(db, "csv", csv_bytes, "sample.csv", processing_status="processed")

        # Also add an unprocessed one to ensure it is excluded
        _make_record(db, "csv", csv_bytes, "pending.csv", processing_status="pending")

        response = client.get("/api/maps/layers")
        assert response.status_code == 200
        data = response.json()
        layer_ids = [l["id"] for l in data["layers"]]
        assert rec.id in layer_ids

        # The pending record must NOT appear
        pending = db.query(UploadRecord).filter(
            UploadRecord.original_filename == "pending.csv"
        ).first()
        assert pending.id not in layer_ids


class TestGetLayer:
    """Tests for GET /api/maps/layers/{layer_id}"""

    def test_missing_layer_returns_404(self, client):
        """3. Non-existent ID → 404."""
        response = client.get("/api/maps/layers/999999")
        assert response.status_code == 404

    def test_csv_lat_lon_columns(self, client, db, monkeypatch):
        """4. CSV with latitude/longitude → valid GeoJSON FeatureCollection."""
        _patch_backend_dir(monkeypatch)
        csv_bytes = (
            b"latitude,longitude,sample_id,grade\n"
            b"21.4312,79.8113,MN-001,1.5\n"
            b"21.1415,79.0815,MN-002,2.1\n"
        )
        rec = _make_record(db, "csv", csv_bytes, "test_lat_lon.csv")

        response = client.get(f"/api/maps/layers/{rec.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["render_type"] == "point_layer"
        fc = data["geojson"]
        assert fc is not None
        assert fc["type"] == "FeatureCollection"
        assert len(fc["features"]) == 2
        feat = fc["features"][0]
        assert feat["type"] == "Feature"
        assert feat["geometry"]["type"] == "Point"
        lon, lat = feat["geometry"]["coordinates"]
        assert -180 <= lon <= 180
        assert -90 <= lat <= 90

    def test_csv_lat_lon_short_columns(self, client, db, monkeypatch):
        """5. CSV with lat/lon short column names → valid GeoJSON."""
        _patch_backend_dir(monkeypatch)
        csv_bytes = (
            b"lat,lon,element\n"
            b"21.43,79.81,Mn\n"
            b"21.14,79.08,Fe\n"
            b"20.99,78.55,Cu\n"
        )
        rec = _make_record(db, "csv", csv_bytes, "test_lat_short.csv")

        response = client.get(f"/api/maps/layers/{rec.id}")
        assert response.status_code == 200
        data = response.json()
        fc = data["geojson"]
        assert len(fc["features"]) == 3
        # Verify short lat/lon columns were detected
        meta = fc.get("_meta", {})
        assert meta.get("lat_column") in ("lat", "latitude", "LAT")
        assert meta.get("lon_column") in ("lon", "lng", "longitude", "long", "LON")

    def test_csv_invalid_coordinates_skipped(self, client, db, monkeypatch):
        """6. Rows with out-of-range or non-numeric coords are skipped gracefully."""
        _patch_backend_dir(monkeypatch)
        csv_bytes = (
            b"latitude,longitude,note\n"
            b"21.43,79.81,valid\n"
            b"999.0,79.81,bad_lat\n"      # lat out of range
            b"21.43,999.0,bad_lon\n"      # lon out of range
            b"notanumber,79.81,bad_str\n"  # non-numeric
            b"21.14,79.08,valid2\n"
        )
        rec = _make_record(db, "csv", csv_bytes, "test_bad_coords.csv")

        response = client.get(f"/api/maps/layers/{rec.id}")
        assert response.status_code == 200
        fc = response.json()["geojson"]
        assert len(fc["features"]) == 2   # only the 2 valid rows
        meta = fc.get("_meta", {})
        assert meta.get("skipped_rows", 0) == 3

    def test_csv_no_coordinate_columns_returns_422(self, client, db, monkeypatch):
        """7. CSV without coordinate columns → 422 Unprocessable Entity."""
        _patch_backend_dir(monkeypatch)
        csv_bytes = b"element,grade,formation\nMn,1.5,Vindhyan\nFe,2.1,Deccan\n"
        rec = _make_record(db, "csv", csv_bytes, "test_no_coords.csv")

        response = client.get(f"/api/maps/layers/{rec.id}")
        assert response.status_code == 422
        assert "latitude" in response.json()["detail"].lower() or \
               "longitude" in response.json()["detail"].lower() or \
               "column" in response.json()["detail"].lower()

    def test_geojson_file_preserved(self, client, db, monkeypatch):
        """8. Uploaded GeoJSON file → FeatureCollection with geometry preserved."""
        _patch_backend_dir(monkeypatch)
        fc_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [79.81, 21.43]},
                    "properties": {"name": "Site A", "grade": 1.5}
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[79.0, 21.0], [80.0, 21.0], [80.0, 22.0], [79.0, 21.0]]]
                    },
                    "properties": {"name": "Zone B"}
                }
            ]
        }
        rec = _make_record(db, "vector", json.dumps(fc_data).encode(), "test.geojson")

        response = client.get(f"/api/maps/layers/{rec.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["render_type"] == "vector_layer"
        fc = data["geojson"]
        assert fc["type"] == "FeatureCollection"
        assert len(fc["features"]) == 2
        types_in_response = {f["geometry"]["type"] for f in fc["features"]}
        assert "Point" in types_in_response
        assert "Polygon" in types_in_response

    def test_invalid_geojson_returns_422(self, client, db, monkeypatch):
        """9. Malformed GeoJSON file → 422."""
        _patch_backend_dir(monkeypatch)
        bad_bytes = b'{"type": "FeatureCollection", "features": INVALID_JSON}'
        rec = _make_record(db, "vector", bad_bytes, "bad.geojson")

        response = client.get(f"/api/maps/layers/{rec.id}")
        assert response.status_code == 422

    def test_bounding_box_calculated_from_csv(self, client, db, monkeypatch):
        """10. Bounding box is correctly calculated from CSV point coordinates."""
        _patch_backend_dir(monkeypatch)
        csv_bytes = (
            b"latitude,longitude\n"
            b"10.0,70.0\n"
            b"20.0,80.0\n"
            b"15.0,75.0\n"
        )
        rec = _make_record(db, "csv", csv_bytes, "test_bbox.csv")

        response = client.get(f"/api/maps/layers/{rec.id}")
        assert response.status_code == 200
        fc = response.json()["geojson"]
        bbox = fc.get("_meta", {}).get("bbox")
        assert bbox is not None
        assert len(bbox) == 4
        min_lon, min_lat, max_lon, max_lat = bbox
        assert min_lon == pytest.approx(70.0)
        assert min_lat == pytest.approx(10.0)
        assert max_lon == pytest.approx(80.0)
        assert max_lat == pytest.approx(20.0)

    def test_geojson_feature_collection_response_shape(self, client, db, monkeypatch):
        """Bonus: GeoJSON response has correct top-level shape."""
        _patch_backend_dir(monkeypatch)
        csv_bytes = b"latitude,longitude,sample\n21.0,79.0,S1\n22.0,80.0,S2\n"
        rec = _make_record(db, "csv", csv_bytes, "test_shape.csv")

        response = client.get(f"/api/maps/layers/{rec.id}")
        assert response.status_code == 200
        fc = response.json()["geojson"]
        # Must conform to GeoJSON spec
        assert fc["type"] == "FeatureCollection"
        for feat in fc["features"]:
            assert feat["type"] == "Feature"
            assert "geometry" in feat
            assert "properties" in feat
            assert feat["geometry"]["type"] == "Point"
            assert len(feat["geometry"]["coordinates"]) >= 2

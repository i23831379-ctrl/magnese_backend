from fastapi.testclient import TestClient
from app.main import app
from app.ml.manganese.preprocessing import build_feature_matrix
from app.ml.manganese.training import ManganeseTrainingRecord

client = TestClient(app)

def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_targets():
    r = client.get("/api/targets")
    assert r.status_code == 200
    assert len(r.json()) >= 5
    assert r.json()[0]["mineral"] == "manganese"
    assert 0 <= r.json()[0]["manganese_probability"] <= 1
    assert r.json()[0]["model_status"] == "demo"


def test_manganese_target_routes():
    collection = client.get("/api/manganese/targets")
    detail = client.get("/api/manganese/targets/1")
    missing = client.get("/api/manganese/targets/999")
    assert collection.status_code == 200
    assert detail.status_code == 200
    assert detail.json()["mineral"] == "manganese"
    assert missing.status_code == 404

def test_prospectivity_geojson():
    r = client.get("/api/maps/prospectivity")
    assert r.status_code == 200
    assert r.json()["type"] == "FeatureCollection"


def test_manganese_prospectivity_route():
    r = client.get("/api/manganese/prospectivity")
    assert r.status_code == 200
    assert r.json()["type"] == "FeatureCollection"
    properties = r.json()["features"][0]["properties"]
    assert properties["mineral"] == "manganese"
    assert properties["classification"] == "VERY_HIGH"
    assert 0 <= properties["manganese_probability"] <= 1
    assert properties["model_status"] == "demo"


def test_prospectivity_zones_are_target_centered_and_closed():
    targets = {target["code"]: target for target in client.get("/api/manganese/targets").json()}
    features = client.get("/api/manganese/prospectivity").json()["features"]
    assert len(features) == len(targets)
    for feature in features:
        properties = feature["properties"]
        target = targets[properties["target_id"]]
        ring = feature["geometry"]["coordinates"][0]
        assert ring[0] == ring[-1]
        assert len(ring) == 9
        assert properties["latitude"] == target["latitude"]
        assert properties["longitude"] == target["longitude"]
        assert max(abs(point[0] - target["longitude"]) for point in ring) < 0.06
        assert max(abs(point[1] - target["latitude"]) for point in ring) < 0.06


def test_manganese_prediction():
    r = client.post(
        "/api/manganese/predict",
        json={
            "latitude": 20.123,
            "longitude": 85.456,
            "features": {"elevation": 300, "slope": 12, "magnetic_value": 123.4},
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["mineral"] == "manganese"
    assert 0 <= body["manganese_probability"] <= 1
    assert body["model_status"] == "demo"
    assert body["feature_summary"] == ["elevation", "magnetic_value", "slope"]


def test_manganese_prediction_rejects_invalid_coordinates():
    r = client.post(
        "/api/manganese/predict",
        json={"latitude": 95, "longitude": 85, "features": {"elevation": 300}},
    )
    assert r.status_code == 422


def test_manganese_prediction_rejects_missing_features():
    r = client.post(
        "/api/manganese/predict",
        json={"latitude": 20, "longitude": 85, "features": {}},
    )
    assert r.status_code == 422


def test_manganese_model_status():
    r = client.get("/api/manganese/model/status")
    assert r.status_code == 200
    assert r.json()["mineral"] == "manganese"
    assert r.json()["status"] == "demo"
    assert r.json()["metrics"] is None
    assert r.json()["training_date"] is None
    assert "elevation" in r.json()["feature_list"]
    assert r.json()["record_count"] is None


def test_manganese_batch_prediction():
    r = client.post(
        "/api/manganese/predict-batch",
        json={
            "requests": [
                {"latitude": 20, "longitude": 85, "features": {"elevation": 300}},
                {"latitude": 21, "longitude": 86, "features": {"slope": 12}},
            ]
        },
    )
    assert r.status_code == 200
    assert len(r.json()) == 2
    assert all(item["mineral"] == "manganese" for item in r.json())


def test_manganese_training_csv_validation():
    r = client.post(
        "/api/manganese/upload-data",
        json={
            "csv_text": "latitude,longitude,mn_concentration,fe_concentration,label\n20.1,85.2,42,8,1\n21.2,86.3,,,0\n"
        },
    )
    assert r.status_code == 200
    assert r.json()["mineral"] == "manganese"
    assert r.json()["record_count"] == 2
    assert "mn_concentration" in r.json()["feature_columns"]


def test_manganese_training_csv_rejects_duplicate_coordinates():
    r = client.post(
        "/api/manganese/upload-data",
        json={"csv_text": "latitude,longitude,label\n20,85,1\n20,85,0\n"},
    )
    assert r.status_code == 422


def test_manganese_training_csv_requires_label():
    r = client.post(
        "/api/manganese/upload-data",
        json={"csv_text": "latitude,longitude\n20,85\n"},
    )
    assert r.status_code == 422


def test_manganese_feature_matrix_handles_optional_values():
    records = [
        ManganeseTrainingRecord(latitude=20, longitude=85, elevation=300, label=1),
        ManganeseTrainingRecord(latitude=21, longitude=86, slope=12, label=0),
    ]
    matrix, labels = build_feature_matrix(records, ("elevation", "slope"))
    assert matrix == [[300.0, 0.0], [0.0, 12.0]]
    assert labels == [1, 0]

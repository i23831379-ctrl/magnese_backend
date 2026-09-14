from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

checks = [
    ("/api/health", 200),
    ("/api/targets", 200),
    ("/api/maps/prospectivity", 200),
]

for path, expected in checks:
    response = client.get(path)
    assert response.status_code == expected, (path, response.status_code)
    print(f"PASS {path}")

print("ALL API VERIFICATION TESTS PASSED")

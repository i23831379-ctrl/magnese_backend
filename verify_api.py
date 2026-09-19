import os
import sys

# Ensure backend dir is in Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_tests():
    print("Testing Manganex AI Backend API...")
    
    # 1. Test root
    print("1. Testing Root Endpoint")
    resp = client.get("/")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    
    # 2. Test fetching all targets
    print("2. Testing GET /api/targets/")
    resp = client.get("/api/targets/")
    assert resp.status_code == 200
    targets = resp.json()
    print(f"   Success! Found {len(targets)} seeded targets.")
    
    # 3. Test verification endpoint
    if len(targets) > 0:
        target_id = targets[0]["id"]
        print(f"3. Testing PUT /api/targets/{target_id}/verify")
        resp = client.put(f"/api/targets/{target_id}/verify")
        assert resp.status_code == 200
        verified_target = resp.json()
        assert verified_target["is_verified"] == True
        print("   Success! Target verified.")
        
        # 4. Test Explanation Endpoint
        print(f"4. Testing GET /api/ml/target/{target_id}/explanation")
        resp = client.get(f"/api/ml/target/{target_id}/explanation")
        assert resp.status_code == 200
        explanation = resp.json()
        assert "shap_features" in explanation
        print("   Success! Explanation fetched.")
        
    # 5. Test Live Prediction Endpoint
    print("5. Testing POST /api/ml/predict")
    resp = client.post("/api/ml/predict", json={"latitude": 21.5, "longitude": 79.5})
    assert resp.status_code == 200
    prediction = resp.json()
    assert "prospectivity_score" in prediction
    print(f"   Success! Live prediction generated score: {prediction['prospectivity_score']}")
    
    print("\nALL VERIFICATION TESTS PASSED! 🎉")

if __name__ == "__main__":
    try:
        run_tests()
    except AssertionError as e:
        print(f"TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

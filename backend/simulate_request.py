
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_request(d, c):
    print(f"Testing {d} - {c}...")
    try:
        response = client.get("/api/v1/forecasts", params={"district": d, "crops": c})
        print(f"STATUS: {response.status_code}")
        print(f"RESPONSE: {response.json()}")
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    test_request("Amritsar", "rice")
    test_request("Ahmedabad", "soybean")

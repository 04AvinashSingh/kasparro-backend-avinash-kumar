from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_stats_endpoint():
    response = client.get("/stats")
    assert response.status_code == 200

    data = response.json()
    assert "total_records" in data
    assert "latest_run" in data

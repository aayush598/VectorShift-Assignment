# tests/test_health.py

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "operational"
    assert "version" in data


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

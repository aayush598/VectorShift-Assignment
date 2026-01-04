# tests/test_metrics.py

def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200

    data = response.json()
    assert "cache_stats" in data
    assert "config" in data

    assert "max_nodes" in data["config"]
    assert "cache_enabled" in data["config"]

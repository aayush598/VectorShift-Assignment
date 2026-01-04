# tests/test_pipelines_api.py

def test_parse_pipeline_dag(client):
    payload = {
        "nodes": [
            {"id": "a", "type": "input"},
            {"id": "b", "type": "output"},
        ],
        "edges": [
            {"source": "a", "target": "b"},
        ],
    }

    response = client.post("/pipelines/parse", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["num_nodes"] == 2
    assert data["num_edges"] == 1
    assert data["is_dag"] is True
    assert data["cycle"] is None


def test_parse_pipeline_cycle(client):
    payload = {
        "nodes": [
            {"id": "a", "type": "node"},
            {"id": "b", "type": "node"},
        ],
        "edges": [
            {"source": "a", "target": "b"},
            {"source": "b", "target": "a"},
        ],
    }

    response = client.post("/pipelines/parse", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["is_dag"] is False
    assert data["cycle"] is not None

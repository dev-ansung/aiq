import pytest
from fastapi.testclient import TestClient
from aiq.daemon.app import create_app


@pytest.fixture
def client(aiq_home):
    return TestClient(create_app())


def test_list_models_empty(client):
    assert client.get("/models").json() == []


def test_add_model(client):
    payload = {"id": "gpt4", "endpoint_url": "https://api.openai.com/v1", "api_key": "$OPENAI_API_KEY", "model_id": "gpt-4-turbo"}
    r = client.post("/models", json=payload)
    assert r.status_code == 200
    assert r.json()["id"] == "gpt4"


def test_remove_model(client):
    client.post("/models", json={"id": "gpt4", "endpoint_url": "https://api.openai.com/v1", "api_key": "k", "model_id": "m"})
    r = client.delete("/models/gpt4")
    assert r.status_code == 200
    assert client.get("/models").json() == []

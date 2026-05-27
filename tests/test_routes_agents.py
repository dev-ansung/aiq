import pytest
from fastapi.testclient import TestClient
from aiq.daemon.app import create_app


@pytest.fixture
def client(aiq_home):
    return TestClient(create_app())


def test_list_agents_empty(client):
    assert client.get("/agents").json() == []


def test_add_agent(client):
    # model must exist first
    client.post("/models", json={"id": "gpt4", "endpoint_url": "https://api.openai.com/v1", "api_key": "k", "model_id": "m"})
    r = client.post("/agents", json={"id": "summarizer", "model": "gpt4", "system_prompt": "You summarize."})
    assert r.status_code == 200
    assert r.json()["id"] == "summarizer"


def test_add_agent_unknown_model_fails(client):
    r = client.post("/agents", json={"id": "bad", "model": "nonexistent", "system_prompt": "x"})
    assert r.status_code == 422


def test_remove_agent(client):
    client.post("/models", json={"id": "gpt4", "endpoint_url": "https://api.openai.com/v1", "api_key": "k", "model_id": "m"})
    client.post("/agents", json={"id": "summarizer", "model": "gpt4", "system_prompt": "You summarize."})
    r = client.delete("/agents/summarizer")
    assert r.status_code == 200
    assert client.get("/agents").json() == []

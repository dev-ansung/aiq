import pytest
from fastapi.testclient import TestClient
from aiq.daemon.app import create_app


@pytest.fixture
def client(aiq_home):
    app = create_app()
    return TestClient(app)


def test_list_groups_empty(client):
    r = client.get("/groups")
    assert r.status_code == 200
    assert r.json() == []


def test_add_group(client):
    r = client.post("/groups", json={"id": "kitchen"})
    assert r.status_code == 200
    assert r.json()["id"] == "kitchen"
    assert r.json()["parallelism"] == 1


def test_add_duplicate_group_fails(client):
    client.post("/groups", json={"id": "kitchen"})
    r = client.post("/groups", json={"id": "kitchen"})
    assert r.status_code == 409


def test_remove_group(client):
    client.post("/groups", json={"id": "kitchen"})
    r = client.delete("/groups/kitchen")
    assert r.status_code == 200
    assert client.get("/groups").json() == []


def test_pause_and_resume_group(client):
    client.post("/groups", json={"id": "kitchen"})
    r = client.post("/groups/kitchen/pause")
    assert r.status_code == 200
    assert r.json()["status"] == "paused"
    r = client.post("/groups/kitchen/resume")
    assert r.json()["status"] == "running"

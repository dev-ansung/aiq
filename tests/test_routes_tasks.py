import pytest
from fastapi.testclient import TestClient
from aiq.daemon.app import create_app


@pytest.fixture
def client(aiq_home):
    return TestClient(create_app())


@pytest.fixture
def seeded_client(client):
    client.post("/groups", json={"id": "kitchen"})
    client.post("/models", json={"id": "gpt4", "endpoint_url": "https://api.openai.com/v1", "api_key": "k", "model_id": "m"})
    client.post("/agents", json={"id": "chef", "model": "gpt4", "system_prompt": "You cook."})
    return client


def test_add_task(seeded_client):
    r = seeded_client.post("/tasks", json={"group": "kitchen", "agent": "chef", "prompt": "make dough"})
    assert r.status_code == 200
    task = r.json()
    assert task["id"] == 0
    assert task["status"] == "queued"
    assert task["after"] is None


def test_add_task_auto_increments_id(seeded_client):
    seeded_client.post("/tasks", json={"group": "kitchen", "agent": "chef", "prompt": "make dough"})
    r = seeded_client.post("/tasks", json={"group": "kitchen", "agent": "chef", "prompt": "make sauce"})
    assert r.json()["id"] == 1


def test_add_task_with_after(seeded_client):
    seeded_client.post("/tasks", json={"group": "kitchen", "agent": "chef", "prompt": "make dough"})
    r = seeded_client.post("/tasks", json={"group": "kitchen", "agent": "chef", "prompt": "serve pizza", "after": 0})
    assert r.json()["after"] == 0


def test_add_task_unknown_group_fails(seeded_client):
    r = seeded_client.post("/tasks", json={"group": "nonexistent", "agent": "chef", "prompt": "x"})
    assert r.status_code == 422


def test_add_task_unknown_agent_fails(seeded_client):
    r = seeded_client.post("/tasks", json={"group": "kitchen", "agent": "ghost", "prompt": "x"})
    assert r.status_code == 422


def test_list_tasks(seeded_client):
    seeded_client.post("/tasks", json={"group": "kitchen", "agent": "chef", "prompt": "make dough"})
    r = seeded_client.get("/tasks")
    assert len(r.json()) == 1


def test_remove_task(seeded_client):
    seeded_client.post("/tasks", json={"group": "kitchen", "agent": "chef", "prompt": "make dough"})
    r = seeded_client.delete("/tasks/0")
    assert r.status_code == 200
    assert seeded_client.get("/tasks").json() == []


def test_script_path_set_after_add(seeded_client, aiq_home):
    r = seeded_client.post("/tasks", json={"group": "kitchen", "agent": "chef", "prompt": "make dough"})
    assert "script.py" in r.json()["script_path"]


def test_restart_task(seeded_client, aiq_home):
    seeded_client.post("/tasks", json={"group": "kitchen", "agent": "chef", "prompt": "make dough"})
    # Manually mark as failed
    import os
    os.environ["AIQ_HOME"] = str(aiq_home)
    from aiq.state.store import Store
    store = Store()
    state = store.load_state()
    state["tasks"][0]["status"] = "failed"
    store.save_state(state)

    r = seeded_client.post("/tasks/0/restart")
    assert r.status_code == 200
    assert r.json()["status"] == "queued"

import pytest
from aiq.state.store import Store


def test_aiq_home_from_env(aiq_home):
    store = Store()
    assert store.home == aiq_home


def test_initial_state_is_empty(aiq_home):
    store = Store()
    state = store.load_state()
    assert state["groups"] == {}
    assert state["tasks"] == []


def test_save_and_load_state(aiq_home):
    store = Store()
    store.save_state({"groups": {"kitchen": {"id": "kitchen", "parallelism": 1, "status": "running"}}, "tasks": []})
    state = store.load_state()
    assert "kitchen" in state["groups"]


def test_load_config_empty(aiq_home):
    store = Store()
    config = store.load_config()
    assert config["models"] == {}
    assert config["agents"] == {}


def test_save_and_load_config(aiq_home):
    store = Store()
    store.save_config({"models": {"gpt4": {"id": "gpt4", "endpoint_url": "https://api.openai.com/v1", "api_key": "sk-x", "model_id": "gpt-4-turbo"}}, "agents": {}})
    config = store.load_config()
    assert "gpt4" in config["models"]


def test_last_args_roundtrip(aiq_home):
    store = Store()
    store.save_last_args({"agent": "summarizer", "after": 3})
    args = store.load_last_args()
    assert args["agent"] == "summarizer"
    assert args["after"] == 3


def test_task_dir_created(aiq_home):
    store = Store()
    task_dir = store.task_dir(5)
    assert task_dir.exists()

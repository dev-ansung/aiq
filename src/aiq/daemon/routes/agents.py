from fastapi import APIRouter, HTTPException
from aiq.models.schema import Agent
from aiq.state.store import Store

router = APIRouter()


def _store() -> Store:
    return Store()


@router.get("/agents")
def list_agents():
    config = _store().load_config()
    return list(config["agents"].values())


@router.post("/agents")
def add_agent(agent: Agent):
    store = _store()
    config = store.load_config()
    if agent.model not in config["models"]:
        raise HTTPException(status_code=422, detail=f"Model '{agent.model}' not found")
    config["agents"][agent.id] = agent.model_dump()
    store.save_config(config)
    return agent


@router.delete("/agents/{agent_id}")
def remove_agent(agent_id: str):
    store = _store()
    config = store.load_config()
    if agent_id not in config["agents"]:
        raise HTTPException(status_code=404, detail="Agent not found")
    del config["agents"][agent_id]
    store.save_config(config)
    return {"ok": True}

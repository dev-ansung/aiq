from fastapi import APIRouter, HTTPException
from aiq.models.schema import Group
from aiq.state.store import Store

router = APIRouter()


def _store() -> Store:
    return Store()


@router.get("/groups")
def list_groups():
    store = _store()
    state = store.load_state()
    return list(state["groups"].values())


@router.post("/groups")
def add_group(group: Group):
    store = _store()
    state = store.load_state()
    if group.id in state["groups"]:
        raise HTTPException(status_code=409, detail=f"Group '{group.id}' already exists")
    state["groups"][group.id] = group.model_dump()
    store.save_state(state)
    return group


@router.delete("/groups/{group_id}")
def remove_group(group_id: str):
    store = _store()
    state = store.load_state()
    if group_id not in state["groups"]:
        raise HTTPException(status_code=404, detail="Group not found")
    del state["groups"][group_id]
    store.save_state(state)
    return {"ok": True}


@router.post("/groups/{group_id}/pause")
def pause_group(group_id: str):
    store = _store()
    state = store.load_state()
    if group_id not in state["groups"]:
        raise HTTPException(status_code=404, detail="Group not found")
    state["groups"][group_id]["status"] = "paused"
    store.save_state(state)
    return state["groups"][group_id]


@router.post("/groups/{group_id}/resume")
def resume_group(group_id: str):
    store = _store()
    state = store.load_state()
    if group_id not in state["groups"]:
        raise HTTPException(status_code=404, detail="Group not found")
    state["groups"][group_id]["status"] = "running"
    store.save_state(state)
    return state["groups"][group_id]

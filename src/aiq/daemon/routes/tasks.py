from __future__ import annotations
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from aiq.models.schema import Task, TaskStatus
from aiq.state.store import Store
from aiq.codegen.script import generate_script
from aiq.daemon.scheduler import build_after_chain

router = APIRouter()


class AddTaskRequest(BaseModel):
    group: str
    agent: str
    prompt: str
    after: int | None = None
    context_files: dict[str, str] = {}


def _store() -> Store:
    return Store()


@router.get("/tasks")
def list_tasks():
    return _store().load_state()["tasks"]


@router.post("/tasks")
def add_task(req: AddTaskRequest):
    store = _store()
    state = store.load_state()
    config = store.load_config()

    if req.group not in state["groups"]:
        raise HTTPException(status_code=422, detail=f"Group '{req.group}' not found")
    if req.agent not in config["agents"]:
        raise HTTPException(status_code=422, detail=f"Agent '{req.agent}' not found")

    task_id = state.get("next_task_id", len(state["tasks"]))
    state["next_task_id"] = task_id + 1
    task_dir = store.task_dir(task_id)
    script_path = str(task_dir / "script.py")
    stdout_path = str(task_dir / "stdout.log")
    output_path = str(task_dir / "result.txt")

    agent = config["agents"][req.agent]
    model = config["models"][agent["model"]]
    after_chain = build_after_chain(req.after, state["tasks"]) if req.after is not None else []

    script = generate_script(
        task_id=task_id,
        prompt=req.prompt,
        agent_id=req.agent,
        system_prompt=agent["system_prompt"],
        endpoint_url=model["endpoint_url"],
        api_key_ref=model["api_key"],
        model_id=model["model_id"],
        after_chain=after_chain,
        context_files=req.context_files,
        output_path=output_path,
        stdout_path=stdout_path,
    )
    Path(script_path).write_text(script)

    task = Task(
        id=task_id,
        group=req.group,
        agent=req.agent,
        prompt=req.prompt,
        after=req.after,
        script_path=script_path,
        stdout_path=stdout_path,
        output_path=output_path,
    )
    state["tasks"].append(task.model_dump())
    store.save_state(state)
    return task


@router.delete("/tasks")
def clean_tasks():
    store = _store()
    state = store.load_state()
    removed = [t for t in state["tasks"] if t["status"] in ("success", "failed", "skipped")]
    state["tasks"] = [t for t in state["tasks"] if t["status"] not in ("success", "failed", "skipped")]
    store.save_state(state)
    return {"removed": len(removed)}


@router.delete("/tasks/{task_id}")
def remove_task(task_id: int):
    store = _store()
    state = store.load_state()
    state["tasks"] = [t for t in state["tasks"] if t["id"] != task_id]
    store.save_state(state)
    return {"ok": True}


@router.post("/tasks/{task_id}/cancel")
def cancel_task(task_id: int):
    store = _store()
    state = store.load_state()
    task = next((t for t in state["tasks"] if t["id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task["status"] == "running":
        task["status"] = TaskStatus.failed.value
        store.save_state(state)
    return task


@router.get("/tasks/{task_id}/log")
def get_log(task_id: int):
    store = _store()
    state = store.load_state()
    task = next((t for t in state["tasks"] if t["id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    log_path = Path(task["stdout_path"])
    if not log_path.exists():
        return {"log": ""}
    return {"log": log_path.read_text()}


@router.get("/tasks/{task_id}/script")
def get_script(task_id: int):
    store = _store()
    state = store.load_state()
    task = next((t for t in state["tasks"] if t["id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    script_path = Path(task["script_path"])
    if not script_path.exists():
        return {"script": ""}
    return {"script": script_path.read_text()}


@router.post("/tasks/{task_id}/restart")
def restart_task(task_id: int):
    store = _store()
    state = store.load_state()
    task = next((t for t in state["tasks"] if t["id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task["status"] = TaskStatus.queued.value
    task["start"] = None
    task["end"] = None
    store.save_state(state)

    config = store.load_config()
    agent = config["agents"][task["agent"]]
    model = config["models"][agent["model"]]
    after_chain = build_after_chain(task["after"], state["tasks"]) if task["after"] is not None else []
    script = generate_script(
        task_id=task_id,
        prompt=task["prompt"],
        agent_id=task["agent"],
        system_prompt=agent["system_prompt"],
        endpoint_url=model["endpoint_url"],
        api_key_ref=model["api_key"],
        model_id=model["model_id"],
        after_chain=after_chain,
        context_files={},
        output_path=task["output_path"],
        stdout_path=task["stdout_path"],
    )
    Path(task["script_path"]).write_text(script)

    return task


@router.get("/tasks/{task_id}/follow")
def follow_task(task_id: int):
    store = _store()
    state = store.load_state()
    task = next((t for t in state["tasks"] if t["id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    log_path = Path(task["stdout_path"])

    def event_stream():
        import time
        while not log_path.exists():
            current = next((t for t in _store().load_state()["tasks"] if t["id"] == task_id), None)
            if current and current["status"] in ("failed", "skipped"):
                return
            time.sleep(0.05)
        # Check once at open time whether this is a replay (task already finished)
        initial = next((t for t in _store().load_state()["tasks"] if t["id"] == task_id), None)
        replay = initial and initial["status"] not in ("queued", "running")
        with open(log_path, "r") as f:
            while True:
                char = f.read(1)
                if char:
                    yield f"data: {char}\n\n"
                    if replay:
                        time.sleep(0.01)  # pace replay to feel like live streaming
                else:
                    current = next((t for t in _store().load_state()["tasks"] if t["id"] == task_id), None)
                    if current and current["status"] not in ("queued", "running"):
                        return

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
    )

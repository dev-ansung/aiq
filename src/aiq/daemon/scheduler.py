from __future__ import annotations
import asyncio
from datetime import datetime, timezone
from pathlib import Path

from aiq.state.store import Store
from aiq.models.schema import TaskStatus


def can_run(task: dict, all_tasks: list[dict]) -> bool | str:
    """Returns True if task can run, False if blocked, 'skip' if should be skipped."""
    after_id = task.get("after")
    if after_id is None:
        return True
    parent = next((t for t in all_tasks if t["id"] == after_id), None)
    if parent is None:
        return True
    if parent["status"] == "success":
        return True
    if parent["status"] == "failed":
        return "skip"
    return False  # queued or running — blocked


def build_after_chain(task_after: int, tasks: list[dict]) -> list[dict]:
    """Walk the --after chain and return ordered list of ancestor tasks (oldest first)."""
    chain = []
    current_id: int | None = task_after
    while current_id is not None:
        task = next((t for t in tasks if t["id"] == current_id), None)
        if task is None:
            break
        chain.append({"prompt": task["prompt"], "output_path": task["output_path"]})
        current_id = task.get("after")
    chain.reverse()
    return chain


async def run_scheduler_loop():
    """Polls state every second and dispatches runnable tasks."""
    while True:
        await asyncio.sleep(1)
        store = Store()
        state = store.load_state()
        tasks = state["tasks"]

        for task in tasks:
            if task["status"] != TaskStatus.queued.value:
                continue

            group = state["groups"].get(task["group"], {})
            if group.get("status") == "paused":
                continue

            running_in_group = sum(
                1 for t in tasks
                if t["group"] == task["group"] and t["status"] == TaskStatus.running.value
            )
            if running_in_group >= group.get("parallelism", 1):
                continue

            result = can_run(task, tasks)
            if result == "skip":
                task["status"] = TaskStatus.skipped.value
                store.save_state(state)
                continue
            if result is not True:
                continue

            task["status"] = TaskStatus.running.value
            task["start"] = datetime.now(timezone.utc).isoformat()
            store.save_state(state)

            asyncio.create_task(_run_task(task))


async def _run_task(task: dict):
    import sys
    store = Store()
    stdout_path = Path(task["stdout_path"])
    stdout_path.parent.mkdir(parents=True, exist_ok=True)

    proc = await asyncio.create_subprocess_exec(
        sys.executable, task["script_path"],
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )

    # Store pid so cancel can kill the process
    state = store.load_state()
    for t in state["tasks"]:
        if t["id"] == task["id"]:
            t["pid"] = proc.pid
            break
    store.save_state(state)

    await proc.wait()

    state = store.load_state()
    for t in state["tasks"]:
        if t["id"] == task["id"]:
            t["status"] = TaskStatus.success.value if proc.returncode == 0 else TaskStatus.failed.value
            t["end"] = datetime.now(timezone.utc).isoformat()
            t["pid"] = None
            break
    store.save_state(state)

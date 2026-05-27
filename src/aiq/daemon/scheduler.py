from __future__ import annotations


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

from __future__ import annotations
import httpx
import typer
from httpx_sse import connect_sse
from rich.table import Table
from rich.console import Console
from aiq.state.store import Store
from aiq.cli import AIQ_URL

app = typer.Typer()
console = Console()

LAST_ARG_KEYS = ["after", "endpoint", "api_key", "model_id", "system_prompt", "agent"]


def _apply_defaults(kwargs: dict) -> dict:
    store = Store()
    last = store.load_last_args()
    result = {}
    for k, v in kwargs.items():
        result[k] = v if v is not None else last.get(k)
    return result


def _save_defaults(kwargs: dict):
    store = Store()
    last = store.load_last_args()
    for k in LAST_ARG_KEYS:
        if kwargs.get(k) is not None:
            last[k] = kwargs[k]
    store.save_last_args(last)


def cmd_status():
    try:
        r = httpx.get(f"{AIQ_URL}/tasks")
        tasks = r.json()
        groups_r = httpx.get(f"{AIQ_URL}/groups")
        groups = {g["id"]: g for g in groups_r.json()}
    except Exception:
        typer.echo("aiqd not running — start with 'aiq daemon start'")
        raise typer.Exit(1)

    for group_id, group in groups.items():
        group_tasks = [t for t in tasks if t["group"] == group_id]
        console.print(f'\nGroup "{group_id}" ({group["parallelism"]} parallel): {group["status"]}')
        t = Table("Id", "Status", "After", "Agent", "Prompt", "Start", "End")
        for task in group_tasks:
            t.add_row(
                str(task["id"]),
                task["status"],
                str(task["after"] or ""),
                task["agent"],
                task["prompt"][:50],
                str(task.get("start") or ""),
                str(task.get("end") or ""),
            )
        console.print(t)


@app.command("add")
def cmd_add(
    prompt: str,
    group: str = typer.Option("default", "-g", "--group"),
    agent: str = typer.Option(None, "-a", "--agent"),
    after: int = typer.Option(None, "--after"),
    context: list[str] = typer.Option([], "-c", "--context"),
    yes: bool = typer.Option(False, "-y"),
):
    kwargs = _apply_defaults({"agent": agent, "after": after})
    agent = kwargs["agent"]
    after = kwargs["after"]

    if agent is None:
        typer.echo("Error: --agent is required (no previous value saved)", err=True)
        raise typer.Exit(1)

    context_files: dict[str, str] = {}
    for c in context:
        if ":" in c:
            alias, path = c.split(":", 1)
        else:
            from pathlib import Path
            alias = Path(c).stem
            path = c
        context_files[alias] = path

    if not yes:
        typer.confirm(f"Add task: [{group}/{agent}] {prompt!r}?", default=True, abort=True)

    r = httpx.post(f"{AIQ_URL}/tasks", json={"group": group, "agent": agent, "prompt": prompt, "after": after, "context_files": context_files})
    if r.status_code == 422:
        typer.echo(f"Error: {r.json().get('detail', r.text)}", err=True)
        raise typer.Exit(1)
    r.raise_for_status()
    task = r.json()
    _save_defaults({"agent": agent, "after": after})
    typer.echo(f"Task {task['id']} added.")


@app.command("clean")
def cmd_clean(yes: bool = typer.Option(False, "-y")):
    if not yes:
        typer.confirm("Remove all completed, failed, and skipped tasks?", abort=True)
    r = httpx.delete(f"{AIQ_URL}/tasks")
    r.raise_for_status()
    typer.echo(f"{r.json()['removed']} task(s) removed.")


@app.command("remove")
def cmd_remove(task_id: int, yes: bool = typer.Option(False, "-y")):
    if not yes:
        typer.confirm(f"Remove task {task_id}?", abort=True)
    httpx.delete(f"{AIQ_URL}/tasks/{task_id}").raise_for_status()
    typer.echo(f"Task {task_id} removed.")


@app.command("cancel")
def cmd_cancel(task_id: int, yes: bool = typer.Option(False, "-y")):
    if not yes:
        typer.confirm(f"Cancel task {task_id}?", abort=True)
    httpx.post(f"{AIQ_URL}/tasks/{task_id}/cancel").raise_for_status()
    typer.echo(f"Task {task_id} cancelled.")


@app.command("retry")
def cmd_retry(task_id: int, yes: bool = typer.Option(False, "-y")):
    if not yes:
        typer.confirm(f"Retry task {task_id}?", abort=True)
    httpx.post(f"{AIQ_URL}/tasks/{task_id}/restart").raise_for_status()
    typer.echo(f"Task {task_id} queued for retry.")


@app.command("log")
def cmd_log(task_id: int):
    try:
        r = httpx.get(f"{AIQ_URL}/tasks/{task_id}/log")
        r.raise_for_status()
        typer.echo(r.json()["log"])
    except Exception:
        typer.echo("aiqd not running — start with 'aiq daemon start'")
        raise typer.Exit(1)


@app.command("follow")
def cmd_follow(task_id: int):
    with httpx.Client(timeout=None) as client:
        with connect_sse(client, "GET", f"{AIQ_URL}/tasks/{task_id}/follow") as source:
            for event in source.iter_sse():
                typer.echo(event.data, nl=False)


@app.command("script")
def cmd_script(task_id: int):
    try:
        r = httpx.get(f"{AIQ_URL}/tasks/{task_id}/script")
        r.raise_for_status()
        typer.echo(r.json()["script"])
    except Exception:
        typer.echo("aiqd not running — start with 'aiq daemon start'")
        raise typer.Exit(1)

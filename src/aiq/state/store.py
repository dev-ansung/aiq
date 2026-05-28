from __future__ import annotations
import json
import os
import tomllib
import tomli_w
from pathlib import Path


def _aiq_home() -> Path:
    env = os.environ.get("AIQ_HOME")
    if env:
        return Path(env)
    return Path.home() / ".aiq"


class Store:
    def __init__(self):
        self.home = _aiq_home()
        self.home.mkdir(parents=True, exist_ok=True)
        (self.home / "tasks").mkdir(exist_ok=True)

    # --- state.json (groups + tasks) ---

    def load_state(self) -> dict:
        path = self.home / "state.json"
        if not path.exists():
            return {"groups": {}, "tasks": [], "next_task_id": 0}
        state = json.loads(path.read_text())
        if "next_task_id" not in state:
            state["next_task_id"] = max((t["id"] for t in state["tasks"]), default=-1) + 1
        return state

    def save_state(self, state: dict) -> None:
        (self.home / "state.json").write_text(json.dumps(state, indent=2, default=str))

    # --- config.toml (models + agents) ---

    def load_config(self) -> dict:
        path = self.home / "config.toml"
        if not path.exists():
            return {"models": {}, "agents": {}}
        with open(path, "rb") as f:
            return tomllib.load(f)

    def save_config(self, config: dict) -> None:
        with open(self.home / "config.toml", "wb") as f:
            tomli_w.dump(config, f)

    # --- last-args.json ---

    def load_last_args(self) -> dict:
        path = self.home / "last-args.json"
        if not path.exists():
            return {}
        return json.loads(path.read_text())

    def save_last_args(self, args: dict) -> None:
        (self.home / "last-args.json").write_text(json.dumps(args, indent=2))

    # --- task dirs ---

    def task_dir(self, task_id: int) -> Path:
        d = self.home / "tasks" / str(task_id)
        d.mkdir(parents=True, exist_ok=True)
        return d

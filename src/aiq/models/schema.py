from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class TaskStatus(str, Enum):
    queued = "queued"
    running = "running"
    success = "success"
    failed = "failed"
    skipped = "skipped"


class GroupStatus(str, Enum):
    running = "running"
    paused = "paused"


class Model(BaseModel):
    id: str
    endpoint_url: str
    api_key: str
    model_id: str


class Agent(BaseModel):
    id: str
    model: str
    system_prompt: str


class Group(BaseModel):
    id: str
    parallelism: int = 1
    status: GroupStatus = GroupStatus.running


class Task(BaseModel):
    id: int
    status: TaskStatus = TaskStatus.queued
    group: str
    after: Optional[int] = None
    agent: str
    prompt: str
    script_path: str = ""
    stdout_path: str = ""
    output_path: str = ""
    start: Optional[datetime] = None
    end: Optional[datetime] = None

from aiq.models.schema import Model, Agent, Group, Task, TaskStatus


def test_task_status_enum():
    assert TaskStatus.queued.value == "queued"
    assert TaskStatus.running.value == "running"
    assert TaskStatus.success.value == "success"
    assert TaskStatus.failed.value == "failed"
    assert TaskStatus.skipped.value == "skipped"


def test_model_fields():
    m = Model(id="gpt4", endpoint_url="https://api.openai.com/v1", api_key="$OPENAI_API_KEY", model_id="gpt-4-turbo")
    assert m.id == "gpt4"
    assert m.api_key == "$OPENAI_API_KEY"


def test_agent_fields():
    a = Agent(id="summarizer", model="gpt4", system_prompt="You summarize text.")
    assert a.model == "gpt4"


def test_group_defaults():
    g = Group(id="kitchen")
    assert g.parallelism == 1
    assert g.status == "running"


def test_task_defaults():
    t = Task(id=0, group="kitchen", agent="summarizer", prompt="do something")
    assert t.status == TaskStatus.queued
    assert t.after is None
    assert t.start is None
    assert t.end is None

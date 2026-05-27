from aiq.daemon.scheduler import can_run, build_after_chain


def test_can_run_no_after():
    tasks = [{"id": 0, "status": "queued", "after": None, "group": "g"}]
    assert can_run(tasks[0], tasks) is True


def test_can_run_after_success():
    tasks = [
        {"id": 0, "status": "success", "after": None, "group": "g"},
        {"id": 1, "status": "queued", "after": 0, "group": "g"},
    ]
    assert can_run(tasks[1], tasks) is True


def test_cannot_run_after_running():
    tasks = [
        {"id": 0, "status": "running", "after": None, "group": "g"},
        {"id": 1, "status": "queued", "after": 0, "group": "g"},
    ]
    assert can_run(tasks[1], tasks) is False


def test_skipped_when_after_failed():
    tasks = [
        {"id": 0, "status": "failed", "after": None, "group": "g"},
        {"id": 1, "status": "queued", "after": 0, "group": "g"},
    ]
    assert can_run(tasks[1], tasks) == "skip"


def test_build_after_chain_single():
    tasks = [
        {"id": 0, "status": "success", "after": None, "prompt": "q0", "output_path": "/tmp/0/result.txt"},
    ]
    chain = build_after_chain(task_after=0, tasks=tasks)
    assert len(chain) == 1
    assert chain[0]["prompt"] == "q0"


def test_build_after_chain_deep():
    tasks = [
        {"id": 0, "status": "success", "after": None, "prompt": "q0", "output_path": "/tmp/0/result.txt"},
        {"id": 1, "status": "success", "after": 0, "prompt": "q1", "output_path": "/tmp/1/result.txt"},
        {"id": 2, "status": "success", "after": 1, "prompt": "q2", "output_path": "/tmp/2/result.txt"},
    ]
    chain = build_after_chain(task_after=2, tasks=tasks)
    assert [c["prompt"] for c in chain] == ["q0", "q1", "q2"]

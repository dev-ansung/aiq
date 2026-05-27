from aiq.codegen.script import generate_script


def test_no_after_script_contains_prompt():
    script = generate_script(
        task_id=0,
        prompt="Tell me a joke",
        agent_id="comedian",
        system_prompt="You are a comedian.",
        endpoint_url="https://api.openai.com/v1",
        api_key_ref="$OPENAI_API_KEY",
        model_id="gpt-4-turbo",
        after_chain=[],
        context_files={},
        output_path="/tmp/aiq/tasks/0/result.txt",
        stdout_path="/tmp/aiq/tasks/0/stdout.log",
    )
    assert "Tell me a joke" in script
    assert "You are a comedian." in script
    assert "gpt-4-turbo" in script
    assert "result.txt" in script


def test_after_chain_builds_history():
    script = generate_script(
        task_id=2,
        prompt="Now summarize",
        agent_id="summarizer",
        system_prompt="You summarize.",
        endpoint_url="https://api.openai.com/v1",
        api_key_ref="sk-literal",
        model_id="gpt-4o",
        after_chain=[
            {"prompt": "First question", "output_path": "/tmp/aiq/tasks/0/result.txt"},
            {"prompt": "Second question", "output_path": "/tmp/aiq/tasks/1/result.txt"},
        ],
        context_files={},
        output_path="/tmp/aiq/tasks/2/result.txt",
        stdout_path="/tmp/aiq/tasks/2/stdout.log",
    )
    assert "First question" in script
    assert "/tmp/aiq/tasks/0/result.txt" in script
    assert "Second question" in script
    assert "Now summarize" in script


def test_context_files_injected():
    script = generate_script(
        task_id=3,
        prompt="Use the notes",
        agent_id="analyst",
        system_prompt="You analyze.",
        endpoint_url="https://api.openai.com/v1",
        api_key_ref="$KEY",
        model_id="gpt-4o",
        after_chain=[],
        context_files={"history": "/home/user/notes.md"},
        output_path="/tmp/aiq/tasks/3/result.txt",
        stdout_path="/tmp/aiq/tasks/3/stdout.log",
    )
    assert "/home/user/notes.md" in script
    assert "history_content" in script
    # user_prompt must use f-string so {history_content} is interpolated at runtime
    assert 'user_prompt = f"' in script
    assert "{history_content}" in script


def test_stdout_path_used_in_script():
    script = generate_script(
        task_id=0, prompt="p", agent_id="a", system_prompt="s",
        endpoint_url="http://x", api_key_ref="$KEY", model_id="m",
        after_chain=[], context_files={},
        output_path="/tmp/r.txt", stdout_path="/tmp/s.log",
    )
    assert "/tmp/s.log" in script


def test_api_key_env_vs_literal():
    script_env = generate_script(
        task_id=0, prompt="p", agent_id="a", system_prompt="s",
        endpoint_url="http://x", api_key_ref="$MY_KEY", model_id="m",
        after_chain=[], context_files={},
        output_path="/tmp/r.txt", stdout_path="/tmp/s.log",
    )
    assert 'os.environ["MY_KEY"]' in script_env

    script_literal = generate_script(
        task_id=0, prompt="p", agent_id="a", system_prompt="s",
        endpoint_url="http://x", api_key_ref="sk-abc", model_id="m",
        after_chain=[], context_files={},
        output_path="/tmp/r.txt", stdout_path="/tmp/s.log",
    )
    assert '"sk-abc"' in script_literal

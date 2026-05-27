from __future__ import annotations
from textwrap import dedent


def _api_key_expr(api_key_ref: str) -> str:
    if api_key_ref.startswith("$"):
        return f'os.environ["{api_key_ref[1:]}"]'
    return f'"{api_key_ref}"'


def generate_script(
    task_id: int,
    prompt: str,
    agent_id: str,
    system_prompt: str,
    endpoint_url: str,
    api_key_ref: str,
    model_id: str,
    after_chain: list[dict],  # [{"prompt": str, "output_path": str}, ...]
    context_files: dict[str, str],  # {alias: filepath}
    output_path: str,
    stdout_path: str,
) -> str:
    api_key_expr = _api_key_expr(api_key_ref)

    # Build message history from chain (8-space indent to align inside messages list)
    history_lines = []
    for item in after_chain:
        escaped_prompt = item["prompt"].replace('"', '\\"')
        history_lines.append(f'        {{"role": "user", "content": "{escaped_prompt}"}},')
        history_lines.append(f'        {{"role": "assistant", "content": Path("{item["output_path"]}").read_text()}},')
    history_str = "\n".join(history_lines)

    # Context file injection
    context_load_lines = []
    context_parts = []
    for alias, filepath in context_files.items():
        context_load_lines.append(f'{alias}_content = Path("{filepath}").read_text()')
        context_parts.append(f'\\n\\n[{alias}]\\n{{{alias}_content}}')
    context_load_str = "\n".join(context_load_lines)

    escaped_prompt = prompt.replace('"', '\\"')
    escaped_system = system_prompt.replace('"', '\\"')

    # Use f-string for user_prompt only when context files are present
    if context_parts:
        context_suffix = "".join(context_parts)
        user_prompt_line = f'user_prompt = f"{escaped_prompt}{context_suffix}"'
    else:
        user_prompt_line = f'user_prompt = "{escaped_prompt}"'

    context_block = context_load_str + "\n" if context_load_str else ""

    return dedent(f"""\
        #!/usr/bin/env python3
        # aiq task {task_id} — agent: {agent_id}
        import os
        import sys
        from pathlib import Path
        from openai import OpenAI

        api_key = {api_key_expr}
        client = OpenAI(api_key=api_key, base_url="{endpoint_url}")

        {context_block}{user_prompt_line}

        messages = [
            {{"role": "system", "content": "{escaped_system}"}},
        {history_str}
            {{"role": "user", "content": user_prompt}},
        ]

        output_path = Path("{output_path}")
        stdout_path = Path("{stdout_path}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        stdout_path.parent.mkdir(parents=True, exist_ok=True)

        result = []
        with open(stdout_path, "w") as log_file:
            with client.chat.completions.create(
                model="{model_id}",
                messages=messages,
                stream=True,
            ) as stream:
                for chunk in stream:
                    token = chunk.choices[0].delta.content or ""
                    print(token, end="", flush=True)
                    log_file.write(token)
                    log_file.flush()
                    result.append(token)

        output_path.write_text("".join(result))
    """)

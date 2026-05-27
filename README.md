# aiq

A task queue for LLM pipelines. Queue prompts, chain them into conversations, and run them in the background — like [pueue](https://github.com/Nukesor/pueue) but for AI agents.

## Why

Running a sequence of LLM calls by hand is tedious. You wait for one to finish, copy the output, paste it into the next prompt, repeat. `aiq` automates this:

- **Queue and forget.** Submit prompts and move on. The daemon runs them in the background.
- **Chain outputs automatically.** `--after 2` means task 3 gets task 2's full output as conversation history — no copy-paste.
- **Inspect everything.** Every task compiles to a plain Python script you can read, re-run, or modify. No black boxes.
- **Named agents.** Define an agent once (model + system prompt) and reuse it across tasks. Switch models without rewriting prompts.
- **Group-based parallelism.** Run up to N tasks concurrently per group. Pause a group mid-flight without killing running tasks.

## The problem it solves

LLM pipelines typically look like:

```
draft = llm("Write an outline for X")
expanded = llm(f"Expand this outline:\n{draft}")
edited = llm(f"Edit this for clarity:\n{expanded}")
```

This works for one-shot scripts, but breaks down when you want to:
- Run steps overnight and check results in the morning
- Retry a failed step without re-running everything before it
- Parallelize independent branches
- Audit exactly what was sent to the model

`aiq` handles all of this with a daemon + CLI pattern.

## Install

```bash
uvx --from git+https://github.com/<you>/aiq aiq
```

Or for development:

```bash
git clone https://github.com/<you>/aiq
cd aiq
uv sync
uv run aiq --help
```

## Quickstart

```bash
# Start the background daemon
aiq daemon start

# Register a model
aiq model add gpt4o \
  --endpoint https://api.openai.com/v1 \
  --api-key $OPENAI_API_KEY \
  --model-id gpt-4o -y

# Register an agent (model + system prompt)
aiq agent add writer \
  --model gpt4o \
  --system-prompt "You are a concise technical writer." -y

# Create a group
aiq group add drafts -y

# Queue a task
aiq add "Explain what a Merkle tree is in two sentences." -g drafts -a writer -y

# Queue a follow-up — gets task 0's output as conversation context automatically
aiq add "Now give a one-line analogy for the above." -g drafts -a writer --after 0 -y

# Check progress
aiq

# Stream output live
aiq follow 0

# Read completed output
aiq log 0
aiq log 1
```

## How chaining works

`--after N` builds a conversation history from task N's chain, oldest first, before appending your prompt:

```
task 0: "Write an outline"          → result saved to ~/.aiq/tasks/0/result.txt
task 1: --after 0  "Expand it"      → history: [user: outline prompt, assistant: result 0]
task 2: --after 1  "Edit for tone"  → history: [user: outline prompt, assistant: result 0,
                                                 user: expand prompt,  assistant: result 1]
```

Each task is a standalone Python script — run `aiq script N` to see exactly what gets sent to the model.

## Reference

```
Usage: aiq [OPTIONS] COMMAND [ARGS]...

Commands:
  status    Show task status board (default)
  list      Alias for status
  add       Queue a new task
  remove    Delete a task
  cancel    Cancel a running task
  restart   Reset a failed/skipped task to queued
  log       Print stdout log for a task
  follow    Stream live output from a running task
  script    Print the generated Python script for a task
  daemon    Manage the background daemon
  group     Manage task groups
  model     Manage model configs
  agent     Manage agents
  task      task subcommands (same as top-level)
```

### `aiq add`

```
Usage: aiq add [OPTIONS] PROMPT

Arguments:
  prompt  [required]

Options:
  -g, --group    TEXT     Group to run in  [required]
  -a, --agent    TEXT     Agent to use (persisted from last run)
      --after    INTEGER  Task ID to chain after
  -c, --context  TEXT     Context file: alias:file.md or file.md
  -y                      Skip confirmation
```

### `aiq daemon`

```
Usage: aiq daemon [OPTIONS] COMMAND [ARGS]...

Commands:
  start   Start the background daemon
  stop    Stop the daemon
  status  Check if the daemon is running
```

### `aiq group`

```
Usage: aiq group [OPTIONS] COMMAND [ARGS]...

Commands:
  list    List groups (default)
  add     Create a group
  remove  Delete a group
  pause   Pause task dispatch for a group
  resume  Resume a paused group
```

### `aiq model`

```
Usage: aiq model [OPTIONS] COMMAND [ARGS]...

Commands:
  list    List models (default)
  add     Register a model  (--endpoint, --api-key, --model-id)
  remove  Delete a model
```

### `aiq agent`

```
Usage: aiq agent [OPTIONS] COMMAND [ARGS]...

Commands:
  list    List agents (default)
  add     Register an agent  (--model, --system-prompt)
  remove  Delete an agent
```

### `aiq task`

```
Usage: aiq task [OPTIONS] COMMAND [ARGS]...

Commands:
  add      Queue a task
  remove   Delete a task
  cancel   Cancel a running task
  restart  Reset to queued and regenerate script
  log      Print stdout log
  follow   Stream live output
  script   Print generated Python script
```

## State

Everything lives in `~/.aiq/`:

| Path | Contents |
|---|---|
| `~/.aiq/state.json` | groups + tasks |
| `~/.aiq/config.toml` | models + agents |
| `~/.aiq/last-args.json` | persisted CLI defaults |
| `~/.aiq/tasks/{id}/script.py` | generated Python script |
| `~/.aiq/tasks/{id}/stdout.log` | live stdout / stderr |
| `~/.aiq/tasks/{id}/result.txt` | final output (input for chained tasks) |

Override with `AIQ_HOME=/path/to/dir aiq ...` — useful for isolated environments or testing.

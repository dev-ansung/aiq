# aiq User Workflow

## Overview

`aiq` is a pueue-inspired task queue for LLM pipelines. A **daemon** (`aiqd`) runs in the background and executes tasks. The **CLI** (`aiq`) manages configuration and queues prompts.

---

## 1. Start the daemon

```bash
aiq daemon start
aiq daemon status   # should print: aiqd running.
```

---

## 2. Register a model

Models hold the API endpoint, key, and model name.

```bash
aiq model add nano \
  --endpoint https://nano-gpt.com/api/subscription/v1 \
  --api-key $NANO_API_KEY \
  --model-id claw-medium \
  -y
```

List registered models:

```bash
aiq model
```

---

## 3. Register an agent

Agents bind a model to a system prompt.

```bash
aiq agent add writer \
  --model nano \
  --system-prompt "You are a concise technical writer." \
  -y
```

List agents:

```bash
aiq agent
```

---

## 4. Create a group

Groups isolate tasks and control parallelism.

```bash
aiq group add drafts -y
```

List groups:

```bash
aiq group
```

---

## 5. Add tasks

### Single task

```bash
aiq add "Explain what a Merkle tree is in two sentences." \
  -g drafts \
  -a writer \
  -y
```

### Chained tasks (--after)

The second task receives the first task's output as conversation history.

```bash
aiq add "Now give a one-line analogy for a Merkle tree." \
  -g drafts \
  -a writer \
  --after 0 \
  -y
```

---

## 6. Check status

```bash
aiq           # or: aiq status  /  aiq list
```

Output shows each group with a table of tasks: Id, Status, After, Agent, Prompt, Start, End.

---

## 7. Stream live output

```bash
aiq follow 0
```

Streams tokens as the task runs. Blocks until the stream closes.

---

## 8. Read completed output

```bash
aiq log 0     # full stdout log
aiq log 1
```

---

## 9. Inspect the generated script

```bash
aiq script 0
```

Shows the exact Python script that was submitted to the LLM. Useful for debugging prompt construction or context chaining.

---

## 10. Cancel a running task

```bash
aiq cancel 0 -y
```

Marks the task as `failed`. Dependent tasks (those with `--after 0`) will be set to `skipped`.

---

## 11. Restart a failed or skipped task

```bash
aiq restart 0 -y
```

Resets status to `queued` and regenerates the script. The scheduler picks it up on the next poll.

---

## 12. Pause and resume a group

Pausing a group prevents the scheduler from dispatching new tasks in it. Already-running tasks complete normally.

```bash
aiq group pause drafts -y
aiq group resume drafts -y
```

---

## 13. Remove tasks and configuration

```bash
aiq remove 1 -y

aiq agent remove writer -y
aiq model remove gpt4o -y
aiq group remove drafts -y
```

---

## 14. Stop the daemon

```bash
aiq daemon stop
```

---

## Full example (copy-paste sequence)

```bash
# Start
aiq daemon start

# Configure
aiq model add nano --endpoint https://nano-gpt.com/api/subscription/v1 --api-key $NANO_API_KEY --model-id claw-medium -y
aiq agent add writer --model nano --system-prompt "You are a concise technical writer." -y
aiq group add drafts -y

# Queue two chained tasks
aiq add "Explain what a Merkle tree is in two sentences." -g drafts -a writer -y
aiq add "Now give a one-line analogy for the above." -g drafts -a writer --after 0 -y

# Watch
aiq status
aiq follow 0
aiq follow 1

# Read results
aiq log 0
aiq log 1

# Teardown
aiq daemon stop
```

---

## State location

All state lives in `~/.aiq/`:

| Path | Contents |
|---|---|
| `~/.aiq/state.json` | groups + tasks |
| `~/.aiq/config.toml` | models + agents |
| `~/.aiq/last-args.json` | persisted CLI defaults |
| `~/.aiq/tasks/{id}/script.py` | generated Python script |
| `~/.aiq/tasks/{id}/stdout.log` | live stdout / stderr |
| `~/.aiq/tasks/{id}/result.txt` | final output (used by chained tasks) |

Override the directory with `AIQ_HOME=/path/to/dir aiq ...` — useful for testing or multiple isolated environments.

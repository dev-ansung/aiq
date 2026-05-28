# Demo Plan

## Goal

Show the core value proposition in ~25 seconds: queue a chain of prompts, they run in the background in order, and you get the results. Secondary: show multi-agent — different agents for coding vs. reviewing.

## What to cut

- `aiq daemon start/status` — housekeeping, not the point
- `aiq agent` / `aiq group` list — setup noise
- `aiq script 0` — too detailed for a first impression
- `aiq daemon stop` — trailing housekeeping
- `-y` flag — confirmation prompt is part of the UX, worth showing
- All the long waits while tasks run

## Setup (hidden)

Two agents registered:
- `coder` — "You are an expert Python developer. Reply with code only, no explanation."
- `reviewer` — "You are a senior code reviewer. Be concise and specific."

## Structure

```
[Hidden: aiq start, model + both agents configured, screen clear]

$ aiq add "Write a Python function for Fibonacci." -a coder
Add task: [default/coder] 'Write a Python function for Fibonacci.'? [y/N]: y
Task 0 added.

$ aiq add "Write pytest unit tests for the above function." -a coder --after 0
Add task: [default/coder] 'Write pytest unit tests for the above function.'? [y/N]: y
Task 1 added.

$ aiq add "Review the code and tests above for correctness and style." -a reviewer --after 1
Add task: [default/reviewer] 'Review the code and tests above for correctness and style.'? [y/N]: y
Task 2 added.

$ aiq status
[table: 0 queued, 1 queued, 2 queued]

[Hidden: wait for all three to complete]

$ aiq status
[table: 0 success, 1 success, 2 success]

$ aiq log 0
def fibonacci(n): ...

$ aiq log 2
The fibonacci function looks correct... (reviewer output)
```

## Pacing

| Step | Visible | Duration |
|---|---|---|
| Hidden setup | no | — |
| `aiq add` × 3 (with confirmations) | yes | ~6s |
| `aiq status` (queued) | yes | ~2s |
| Wait for tasks | no | — |
| `aiq status` (success) | yes | ~2s |
| `aiq log 0` | yes | ~3s |
| `aiq log 2` | yes | ~3s |
| **Total visible** | | **~16s** |

## Key things the viewer learns

- Single command to queue a prompt (`-g` omitted — goes to `default` group)
- Confirmation prompt shows exactly what's about to run
- `--after` chains tasks: tests see the function, reviewer sees both
- Two different agents in one pipeline (`coder` → `coder` → `reviewer`)
- Status board shows the full pipeline state at a glance
- `log` reads the result — code in, review out

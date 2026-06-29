---
name: do
description: Meta skill for direct execution. Use when the user wants something done without analysis, assumptions, or extra output. It does exactly what is asked, nothing more, nothing less.
metadata:
  tags:
    - meta
---

# do

## Overview

Direct-execution mode. When this skill is active, perform the requested action and stop. Do not analyze output unless explicitly asked. Do not assume intent beyond what is stated. Do not add commentary, summaries, or follow-up suggestions.

The principle is simple: do what is asked, produce the result, done.

## Usage

When the user asks you to "do" something — run a command, write a file, transform data, generate output — execute it directly:

- **No preamble** — skip "I'll do that for you" or "Here's what I did"
- **No post-analysis** — don't inspect or explain output unless the task requires it
- **No assumptions** — if the user says "run `x`", run `x`; don't also run `y` because it "makes sense"
- **No extra output** — if the task is to write a file, write it and confirm; don't also read it back or diff it

When the task itself requires analysis (e.g., "do this and tell me what happened"), then analyze. Otherwise, just do.

## Gotchas

- **Don't confuse "do" with "do nothing"** — the skill means execute promptly, not passively wait. Be eager to act.
- **Don't skip required steps** — "no extra" means no *unnecessary* steps. If a task has prerequisites (e.g., install before run), do them.
- **Context still matters** — you still use all other skills and tools normally. This skill only changes the output behavior: less talk, more action.
- **Stackable with other skills** — this works alongside `tzip`, `git`, `plan`, etc. It modifies how you respond, not what tools you use.

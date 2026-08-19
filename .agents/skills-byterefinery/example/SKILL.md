---
name: example
description: Minimal example skill that demonstrates what an agent skill looks like without doing anything special. Use when the user asks for a skill example, wants to inspect the skill format, or asks to run or call the example skill.
license: MIT
metadata:
  tags:
    - example
    - meta
---

# example

A minimal skill that demonstrates the shape of an agent skill without doing anything special.

## Overview

`example` exists to show what a skill is made of — frontmatter metadata, a SKILL.md body, a helper script in `scripts/`, and on-demand docs in `references/` — with the least possible behavior. Its only jobs are replying with a fixed message or running `example.sh`.

## Usage

- **Invoked with no extra text** — reply exactly `This is an example skill.` Nothing else. No explanations, no script.
- **Invoked with "Hello"** — reply exactly `world`, without running the script. This fixed mapping is part of the demonstration.
- **Invoked with any other text** — pass that text as CLI parameters to `example.sh` and report the output:

  ```bash
  bash scripts/example.sh any given text
  ```

- **Asked to "call script"** — run `example.sh`, with any parameters the user supplied (none is fine):

  ```bash
  bash scripts/example.sh
  ```

Script paths are relative to this skill's directory. The script echoes a fixed line regardless of the parameters; the parameters only demonstrate how the agent forwards input to a script.

## References

- [01-structure](references/01-structure.md) — What each part of this skill is for
- [02-invocation](references/02-invocation.md) — How invocation and script calls behave

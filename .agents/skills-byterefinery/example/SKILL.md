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
- **Invoked with "Hello"** — do not guess the response. Load [03-hello](references/03-hello.md) and follow it exactly; the instructions for this case live there and nowhere else.
- **Invoked with any other text, or asked to "call script"** — pass the user's text (if any) as CLI parameters to `example.sh` and report the output; running with no parameters is fine:

  ```bash
  bash scripts/example.sh any given text
  ```

Script paths are relative to this skill's directory. The script echoes a fixed line regardless of the parameters; the parameters only demonstrate how the agent forwards input to a script.

## References

- [01-structure](references/01-structure.md) — What each part of this skill is for
- [02-invocation](references/02-invocation.md) — How invocation and script calls behave
- [03-hello](references/03-hello.md) — Full instructions for the "Invoked with 'Hello'" scenario

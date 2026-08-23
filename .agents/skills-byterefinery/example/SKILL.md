---
name: example
description: Minimal example skill that demonstrates what an agent skill looks like without doing anything special. Use when the user asks for a skill example, wants to inspect the skill format, or asks to run or call the example skill. Step 1, read this skill's SKILL.md with the read tool; its absolute location is given in this skill's metadata block. Step 2, follow the numbered steps in that file exactly, including opening the reference files and running the script it names. Never reply about this skill before reading SKILL.md, and never guess its contents or its script outputs from memory.
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

The fixed replies in this skill — the no-extra-text line in this file and the word in `references/03-hello.md` — contain the anchor token `4f7a`, which appears nowhere outside this skill's own files. That is deliberate: the exact wording can only be learned by reading the files, never from memory or from the user's message. Copy the wording verbatim from what you read, and copy script output verbatim from the run.

## Usage

Follow these steps in order; do not skip or guess any of them.

1. **Read this file first.** If you have not already opened SKILL.md with the `read` tool, do it now, before replying. Your system prompt only lists this skill's name and description; the instructions below are the only source of truth. Never answer this skill from memory or imagination, even if you think you already know what it does.

2. **Find the skill directory.** The skill's metadata in your system prompt gives the absolute location of this SKILL.md (for example `/path/to/skills/example/SKILL.md`). Its parent directory (`/path/to/skills/example`) is the skill directory. All paths below are relative to it; build absolute paths from it when calling tools.

3. **Classify the invocation.** First remove the request for the skill itself from the user's message — phrases like "Use the example skill", "run the example skill", "call script" are the request, not extra text. Only what is left over is the extra text. The request itself never counts as extra text, even when it uses words like "run" or "call". Then follow exactly one branch:

   | What is left after removing the request | Branch |
   |---|---|
   | Nothing at all | No extra text |
   | Exactly "Hello" | Hello |
   | "call script" (or similar), nothing else | Call script |
   | Anything else | Other text |

   Worked examples:

   - User: "Use the example skill." → nothing left → **No extra text**
   - User: "Use the example skill with Hello." → "Hello" left → **Hello**
   - User: "Use the example skill with: good morning everyone" → "good morning everyone" left → **Other text**
   - User: "Use the example skill and call script." → "call script" left, nothing else → **Call script**

   Branch actions:

   - **No extra text** — the user only asked for the skill itself. Reply with exactly this one line and nothing else (no commentary, no script, no references). Copy it character for character, anchor token included:
     ```text
     This is an example skill. (anchor 4f7a)
     ```
   - **The text "Hello"** — load `references/03-hello.md` with the `read` tool and reply exactly as that file instructs. Do not guess what it says; the instructions for this case live there and nowhere else.
   - **A request to "call script"** — the user only asks to run the skill's script, without giving extra text. Run it with `bash` and **no CLI parameters**, unless the user explicitly named parameters (then pass exactly those, and nothing else):
     ```bash
     bash <skill-dir>/scripts/example.sh
     ```
   - **Any other extra text** — the user gave text besides the request itself (and it is not "Hello"). Pass that extra text as CLI parameters to the script — only that text, not the whole user message:
     ```bash
     bash <skill-dir>/scripts/example.sh [user's text...]
     ```

   In both script branches, run the script and then report the result using the reply format below. Execute the script; do not read its source code to learn its output. Read any given file at most once in the whole conversation — re-reading it changes nothing and wastes a turn.

4. **Reply formats** (match them exactly, no preamble and no commentary before or after):

   - No extra text → the reply is exactly `This is an example skill. (anchor 4f7a)`
   - "Hello" → the single word specified by `references/03-hello.md`, and nothing else — no greeting, no punctuation, no commentary. Type the word directly as your reply; do not run any bash command to produce it.
   - Other text or "call script" → one short line naming the script and the parameters you passed, then the script output in a fenced code block, for example:
     ```text
     Ran `scripts/example.sh good morning everyone`. Output:
     ```
     ```
     This is example.sh output.
     ```

The script echoes the same fixed line regardless of its parameters; the parameters only demonstrate how the agent forwards input to a script.

## Gotchas

- **Never guess the anchor** — if your reply omits or alters the `4f7a` token, it is wrong. The exact wording comes only from the files you read and the script you run in this session.
- **Never invent script output** — the output in your reply must come from an actual `bash` run of `scripts/example.sh` in this session; do not recall it from a previous session.
- **Open only what your branch needs** — the no-extra-text branch opens no references and runs no script; the "Hello" branch opens only `references/03-hello.md` and runs no script; the script branches run `scripts/example.sh` without reading its source.
- **Read each file at most once** — do not re-read a file you already have in this conversation; the content does not change.
- The "Hello" branch has no instructions in this file on purpose; the agent must open `references/03-hello.md` to learn the reply.

## References

- [01-structure](references/01-structure.md) — What each part of this skill is for
- [02-invocation](references/02-invocation.md) — How invocation and script calls behave
- [03-hello](references/03-hello.md) — Full instructions for the "Invoked with 'Hello'" scenario

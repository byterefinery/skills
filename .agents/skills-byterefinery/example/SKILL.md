---
name: example
description: Minimal example skill that demonstrates what an agent skill looks like without doing anything special. It answers with a fixed message, loads a reference file on demand for the Hello case, and runs a tiny demo shell script for other text. Use when the user asks for a skill example, wants to inspect the skill format, or asks to run or call the example skill.
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

Follow these steps in order; do not skip or guess any of them.

1. **The instructions are already in front of you.** The skill's content is given to you directly, so there is nothing to read up front — SKILL.md itself is off-limits and must never be read, not even to check its structure or file layout. The instructions below are the only source of truth; never answer this skill from memory or imagination, even if you think you already know what it does.

2. **Find the skill directory.** The skill's metadata in your system prompt gives the absolute location of this SKILL.md (for example `/path/to/skills/example/SKILL.md`). Its parent directory (`/path/to/skills/example`) is the skill directory. All paths below are relative to it; build absolute paths from it when calling tools.

3. **Classify the invocation.** First remove the request for the skill itself from the user's message — phrases like "Use the example skill", "run the example skill", "call script" are the request, not extra text. Only what is left over is the extra text; the request itself never counts as extra text, even when it uses words like "run" or "call". The leftover text decides the branch:

   - nothing at all → the no-extra-text branch
   - exactly "Hello" → the Hello branch
   - "call script" (or similar), nothing else → the call-script branch
   - anything else → the other-text branch

   Worked examples (the leftover text, after removing the request for the skill):

   - nothing left → no extra text
   - "Hello" → Hello
   - "good morning everyone" → other text
   - "call script" → call script

   If the invocation gives no text besides the request for the skill, nothing is left — that is the no-extra-text branch, and it is the default whenever no leftover text exists. The other-text branch applies only when leftover text actually exists; being unable to identify leftover text is never a reason to run the script. In that case the user's message holds only the skill's instructions, and your entire job is to reply with the fixed line — explore nothing, read no file, run no script.

   Branch actions:

   - **No extra text** — the user only asked for the skill itself. Your entire reply is exactly this one line and nothing else — no commentary, no code fence, no quotes, no script, no references:
     This is an example skill.
   - **The text "Hello"** — load `references/03-hello.md` with the `read` tool and reply exactly as that file instructs. Do not guess what it says; the instructions for this case live there and nowhere else.
   - **Call script** — the user asks to run the skill's script without giving extra text. Run the script directly with **no CLI parameters**, unless the user explicitly named parameters (then pass exactly those and nothing else). The script lives in the skill's `scripts/` directory — run it from there:
     ```bash
     ./example.sh
     ```
   - **Other text** — the user gave text besides the request itself (and it is not "Hello"). Run the script directly from the skill's `scripts/` directory, passing that extra text as CLI parameters — only that text, not the whole user message:
     ```bash
     ./example.sh [user's text...]
     ```

   The script is executable (it has a shebang), so invoke it directly — do not wrap it in `bash`. The script exists and works; trust that and run it — do not verify it first with `ls`, `find`, or `read`. In both script branches, run the script and then report the result using the reply format below. Do not read the script's source to learn its output; run it and report what it prints. Read any given file at most once in the whole conversation — re-reading it changes nothing and wastes a turn.

4. **Reply formats** (match them exactly, no preamble and no commentary before or after):

   - No extra text → your entire reply is exactly this bare line, alone: This is an example skill. (No preamble, no commentary, no code fence.)
   - "Hello" → the single word specified by `references/03-hello.md`, and nothing else — no greeting, no punctuation, no commentary. Type the word directly as your reply; do not run any command to produce it.
   - Other text or call script → one short line naming the script and the parameters you passed, then the script output in a fenced code block, for example:
     ```text
     Ran `example.sh good morning everyone`. Output:
     ```
     ```
     This is example.sh output.
     ```

The script echoes the same fixed line regardless of its parameters; the parameters only demonstrate how the agent forwards input to a script.

## Gotchas

- **Never read the main skill file** — not `SKILL.md`.
- **Never read the script file** — not `example.sh`.
- **Never guess the fixed replies** — copy the reply wording verbatim from the files you read; a reworded reply is wrong.
- **Never invent script output** — the output in your reply must come from an actual run of `example.sh` in this session; do not recall it from a previous session.
- **Open only what your branch needs** — the no-extra-text branch opens no references and runs no script; the Hello branch opens only `references/03-hello.md` and runs no script; the script branches run `example.sh` without reading its source.
- **Read each file at most once** — do not re-read a file you already have in this conversation; the content does not change.
- The "Hello" branch has no instructions in this file on purpose; the agent must open `references/03-hello.md` to learn the reply.

## References

- [01-structure](references/01-structure.md) — What each part of this skill is for
- [02-invocation](references/02-invocation.md) — How invocation and script calls behave
- [03-hello](references/03-hello.md) — Full instructions for the "Invoked with 'Hello'" scenario

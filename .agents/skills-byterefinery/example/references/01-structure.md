# Skill Structure

What a skill is made of, using `example` itself as the working example.

## Layout

```
example/
├── SKILL.md              # Required — frontmatter + core instructions
├── scripts/
│   └── example.sh        # Optional — helper script, executed not loaded
└── references/
    ├── 01-structure.md   # This file — structure, in detail
    └── 02-invocation.md  # How the skill behaves when invoked
```

Only `SKILL.md` is required; everything else is optional.

## SKILL.md

The entry point, in two parts:

- **Frontmatter** — YAML between `---` markers. `name` and `description` are required; the description is what the agent sees in its system prompt and decides when to load the skill. Optional fields: `license`, `compatibility`, `metadata` (e.g. `tags`).
- **Body** — the instructions, loaded on demand when the skill activates. Keep it under 5000 tokens; move bulk material to `references/`.

## scripts/

Helper scripts the agent *executes* rather than reads. They never enter the context window, so they can be far longer than anything that fits in SKILL.md. This skill's `scripts/example.sh` is the smallest possible example — a single echo.

## references/

Dense material loaded only when needed (progressive disclosure). Files use incrementing numeric prefixes (`01-`, `02-`, …) for stable ordering and are linked directly from SKILL.md's `## References` section — never nested one level deeper.

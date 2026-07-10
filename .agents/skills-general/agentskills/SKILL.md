---
name: agentskills
description: >
  The Agent Skills open format — specification, creation best practices,
  evaluation methodology, and the skills-ref reference library. Use when
  creating, auditing, or designing skills for AI agents; when working with
  the agentskills.io ecosystem; when implementing skills support in an agent
  client; or when the user asks about the Agent Skills standard, SKILL.md
  format, progressive disclosure, or the skills-ref tool.
metadata:
  tags:
    - meta
---

# agentskills

The Agent Skills open standard — a lightweight, portable format for extending AI agent capabilities with specialized knowledge and workflows. Originated by Anthropic, now an open standard adopted across the agent ecosystem.

## Overview

Agent Skills are directories containing a `SKILL.md` file with YAML frontmatter and Markdown instructions. Agents load them through **progressive disclosure**:

1. **Discovery** — at startup, agents load only `name` and `description` of each skill (~50-100 tokens per skill)
2. **Activation** — when a task matches a skill's description, the full `SKILL.md` loads into context
3. **Execution** — the agent follows instructions, optionally running bundled scripts or loading reference files on demand

This keeps the base context small while giving agents access to specialized knowledge on demand.

### Directory structure

```
skill-name/
├── SKILL.md          # Required: YAML frontmatter + Markdown instructions
├── scripts/          # Optional: executable code (run, not loaded into context)
├── references/       # Optional: documentation loaded on demand
├── assets/           # Optional: templates, static resources
└── evals/            # Optional: test cases for skill evaluation
```

### Default locations

Agents scan these directories for skills:

| Scope | Path | Purpose |
|---|---|---|
| Project | `.agents/skills/` | Cross-client skill sharing |
| Project | `.<client>/skills/` | Client-specific (e.g., `.claude/skills/`) |
| User | `~/.agents/skills/` | Cross-client, user-wide |
| User | `~/.<client>/skills/` | Client-specific, user-wide |

Project-level skills override user-level skills on name collision.

## Quick workflow

### Creating a skill

1. **Choose a name** — lowercase, hyphens, numbers only, 1-64 chars, no leading/trailing/consecutive hyphens
2. **Scaffold** — use `skman.sh create <name> "<description>"` (or create manually)
3. **Write frontmatter** — `name` must match directory name exactly; `description` determines activation
4. **Write body** — under 500 lines, starts with `# <name>` heading
5. **Validate** — `skman.sh validate <path>` or `skills-ref validate <path>`

### Validating a skill

```bash
# Using skman (local tool)
skman.sh validate ./my-skill
skman.sh validate --strict ./my-skill

# Using skills-ref (official reference library)
uvx skills-ref validate ./my-skill
```

### Reading skill properties

```bash
# Using skman
skman.sh info ./my-skill

# Using skills-ref
uvx skills-ref read-properties ./my-skill
```

### Generating prompt XML

```bash
# Generate <available_skills> block for agent system prompts
uvx skills-ref to-prompt ./skill-a ./skill-b
```

## Gotchas

- **`name` must match directory basename exactly** — `my-skill/` requires `name: my-skill`. The validator warns on mismatch.
- **Description drives activation** — if the description doesn't convey when the skill applies, the agent won't load it. Include specific keywords and contexts.
- **Keep SKILL.md under 500 lines** — move detailed content to `references/NN-topic.md` files. The spec recommends under 5000 tokens for the body.
- **Scripts are executed, not loaded** — agents run scripts via shell commands; they don't read script source into context.
- **Never create `scripts/` or `assets/` automatically** — only scaffold these when the user explicitly requests them.
- **Frontmatter `description` must not contain XML/HTML tags** — the `skman` validator checks for `<tag>` patterns. The official spec allows them but the local validator rejects them.
- **Body must start with `# <name>` or `# <name> <version>`** — the validator errors on mismatch.
- **`## Overview` is recommended, others are optional** — `## Usage`, `## Gotchas`, `## References` produce no warnings when absent.
- **YAML colons in descriptions break parsing** — `description: Use when: the user asks` is invalid YAML. Use block scalars or quoted strings.

## References

- [01-specification](references/01-specification.md) — Full format specification: frontmatter fields, body content, progressive disclosure, file references
- [02-creation-best-practices](references/02-creation-best-practices.md) — How to write effective skills: context economy, specificity calibration, instruction patterns
- [03-using-scripts](references/03-using-scripts.md) — Script design for agentic use: one-off commands, self-contained scripts, structured output
- [04-evaluating-skills](references/04-evaluating-skills.md) — Eval-driven iteration: test cases, assertions, grading, benchmarking, the improvement loop
- [05-optimizing-descriptions](references/05-optimizing-descriptions.md) — Trigger accuracy: eval queries, train/validation splits, optimization loop
- [06-client-implementation](references/06-client-implementation.md) — Adding skills support to an agent: discovery, parsing, disclosure, activation, context management
- [07-skills-ref-library](references/07-skills-ref-library.md) — The official Python reference library: CLI commands, Python API, prompt generation

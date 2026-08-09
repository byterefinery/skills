---
name: agentskills
description: Agent Skills specification — the open format for extending AI agent capabilities. Use when creating, validating, or working with Agent Skills (SKILL.md files, frontmatter, progressive disclosure, skills-ref library). Covers directory structure, frontmatter fields, naming rules, validation, and best practices for portable, version-controlled agent skills.
license: Apache-2.0
compatibility: Requires Python 3.11+ and uv; skills-ref available on PyPI
metadata:
  tags:
    - agent-skills
    - specification
    - validation
    - skman
---

# agentskills

Agent Skills is a lightweight, open format for extending AI agent capabilities with specialized knowledge and workflows. Originally developed by Anthropic and released as an open standard.

## Overview

A skill is a directory containing a `SKILL.md` file — YAML frontmatter (metadata) plus Markdown instructions. Skills extend through progressive disclosure: metadata always visible, full instructions loaded on demand, scripts and references loaded as needed.

The official specification lives at <https://github.com/agentskills/agentskills> with documentation at <https://agentskills.io>.

## Directory Structure

```
skill-name/
├── SKILL.md          # Required: frontmatter + instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation loaded on demand
├── assets/           # Optional: templates, images, data files
└── ...               # Any additional files
```

## Frontmatter

YAML frontmatter between `---` delimiters at the top of `SKILL.md`:

### Required Fields

| Field | Rules |
|---|---|
| `name` | 1-64 chars, lowercase letters (including Unicode/i18n), digits, hyphens; no leading/trailing/consecutive hyphens; must match directory name |
| `description` | 1-1024 chars, non-empty, third-person, describes what the skill does and when to use it |

### Optional Fields

| Field | Rules |
|---|---|
| `license` | License name or reference to bundled license file |
| `compatibility` | 1-500 chars, environment requirements (only include if specific needs exist) |
| `allowed-tools` | Space-separated string of pre-approved tools (experimental) |
| `metadata` | Mapping of string keys to string values; may contain `tags` (string array) |

### Frontmatter Template

```yaml
---
name: my-skill
description: What this skill does and when to use it. Be specific.
license: Apache-2.0
compatibility: Requires Python 3.11+ and uv
allowed-tools: Bash(git:*) Read
metadata:
  tags:
    - dev
---
```

## Body Content

The Markdown body after frontmatter contains skill instructions. No format restrictions — write whatever helps agents perform the task. Keep under 500 lines; move detail to `references/`.

Recommended sections: `## Overview`, `## Usage`, `## Gotchas`, `## References`. The body should start with `# <name>` or `# <name> <version>`.

## Progressive Disclosure

Agents load skills in stages:

1. **Metadata** (~100 tokens): `name` and `description` loaded at startup for all skills
2. **Instructions** (<5000 tokens recommended): Full `SKILL.md` body loaded when activated
3. **Resources** (as needed): Files in `scripts/`, `references/`, `assets/` loaded only when required

## Scripts

Scripts are **executed**, not loaded into context. Default convention:

- **Python with PEP 723** (default): `scripts/<name>.py` with `#!/usr/bin/env -S uv run --script` shebang and inline `# /// script ... # ///` dependency block. Requires `uv` on PATH.
- **Shell mode** (on request): `scripts/<name>.sh` + `scripts/_<name>.py` — bash wrapper delegates to underscore-prefixed Python. Requires only `python` on PATH.

Dependent scripts use whatever language the user specifies — never assume a language.

### PEP 723 Script Template

```python
#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.11"
# dependencies = ["click"]
# ///

import click

@click.command()
def main():
    """My skill script."""
    click.echo("Hello")

if __name__ == "__main__":
    main()
```

## Validation

Use the `skills-ref` library (available on PyPI) to validate skills:

```bash
# Install and validate
uv run --with skills-ref skills-ref validate ./my-skill

# Or with the bundled script
agentskills.py validate ./my-skill
```

Checks performed:
- `SKILL.md` exists with valid YAML frontmatter
- Required fields (`name`, `description`) present
- Name format (lowercase, valid characters, no leading/trailing/consecutive hyphens)
- Name matches directory basename
- Description length (max 1024 chars)
- Compatibility length (max 500 chars, if present)
- No unexpected frontmatter fields

## Creating a Skill

1. **Choose a name** — lowercase, hyphens, numbers only; no leading/trailing/consecutive hyphens
2. **Create directory** — named after the skill (e.g., `my-skill/`) or with version suffix (e.g., `my-skill-1-0-0/`)
3. **Write SKILL.md** — frontmatter with `name` (matching directory) and `description`, followed by body starting with `# <name>`
4. **Add optional content** — `scripts/`, `references/`, `assets/` only when needed
5. **Validate** — run `skills-ref validate ./my-skill` or `agentskills.py validate ./my-skill`

## Gotchas

- **Never create `scripts/` or `assets/` automatically** — only when the user explicitly requests them
- **Default script is Python with PEP 723, not bash** — use `#!/usr/bin/env -S uv run --script` with inline dependency block
- **Frontmatter `name` must match directory basename exactly** — `my-skill/` requires `name: my-skill`
- **`metadata` must be a mapping** — string keys to string values; `tags` should be a string array
- **Reference files are loaded on demand** — keep SKILL.md self-contained for core instructions
- **PEP 723 block is mandatory for Python scripts** — `uv run` depends on it for dependency resolution
- **Keep SKILL.md under 500 lines** — move detailed reference material to `references/NN-topic.md`
- **Reference file naming** — use numeric prefixes (`01-`, `02-`, `03-`) for deterministic ordering
- **Clone repos locally before studying them** — when a URL points to a code repository, clone it into a temp directory rather than fetching files over the network

## External Resources

- [Specification](https://agentskills.io/specification) — Official format specification
- [GitHub Repository](https://github.com/agentskills/agentskills) — Source code and discussions
- [Client Showcase](https://agentskills.io/clients) — Products supporting Agent Skills
- [skills-ref on PyPI](https://pypi.org/project/skills-ref/) — Reference library for validation
- [Contributing Guide](https://github.com/agentskills/agentskills/blob/main/CONTRIBUTING.md) — How to contribute to the spec

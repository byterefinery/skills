---
name: skman
description: Introduces the Agent Skills System — a standardized, lightweight, open format for extending AI agent capabilities with specialized knowledge and workflows. Use for scaffolding, validating, and inspecting agent skills (SKILL.md files and other skill's files and directories).
license: Apache-2.0
compatibility: Requires uv on PATH. PyYAML is declared in the PEP 723 header and auto-resolved by uv — no pip, no local venv.
metadata:
  tags:
    - meta
    - agent
    - skill
    - skills
    - agent skill system
---

# skman

Tools and guidelines for creating, validating, and managing agent skills. Use `skman.py` to scaffold new skill directories, check format compliance, inspect structure, and regenerate the repository README.

## Overview

Agent Skills are a lightweight, open format for extending AI agent capabilities with specialized knowledge and workflows. An agent skill is a directory containing a `SKILL.md` file — frontmatter metadata (the YAML header) plus concise instructions — optionally accompanied by scripts, references, and assets, giving agents new expertise on demand without bloating the context window.

`skman` is the skill for creating, validating, and managing agent skills. It provides four functionalities:

- **`create`** — Scaffold a new skill directory with SKILL.md, optional scripts, and references
- **`validate`** — Check a skill against the format specification (frontmatter, naming, structure)
- **`info`** — Inspect frontmatter, body stats, and heading hierarchy
- **`generate`** — Regenerate the repository README.md with skills table and statistics

## Usage

```bash
# Quick reference — details per subcommand below
skman.py create <name> "<description>" [--with-scripts] [-o ./skills]
skman.py validate ./my-skill            # single skill
skman.py validate .agents/skills        # whole collection
skman.py info ./my-skill [--json]
skman.py generate
skman.py --help                         # or: skman.py <subcommand> --help
```

### Scaffold New Skill

```bash
skman.py create my-skill "Extracts text from PDF files"
skman.py create demo-skill "Dummy example skill" --version 2.4.1
skman.py create numpy "NumPy skill" --url https://github.com/numpy/numpy/releases/tag/v1.26.0
skman.py create my-skill "Desc" --with-scripts --with-references
skman.py create my-skill "Desc" --with-scripts --lang bash   # shell wrapper
skman.py create my-skill "Desc" -o ./custom-skills
```

Validates name and description (format, length, no `:`) before creating files. `--url` extracts name/version from GitHub, PyPI, npm, crates.io, GitLab, RubyGems URLs. The positional `name` and an explicit `--version` take precedence over values extracted from the URL. LLM fallback: set `SKMAN_LLM_RESPONSE='{"version": "X.Y.Z"}'` env var.

### Validate

Run the built-in validator on a single skill or an entire collection:

```bash
# Single skill
skman.py validate ./my-skill
skman.py validate --strict ./my-skill

# All skills in a collection directory
skman.py validate .agents/skills
skman.py validate ./skills-python
```

## Skill Format

A skill is a directory containing a `SKILL.md` file. Everything else is optional.

### Directory Layout

```
<skill-name>/
├── SKILL.md              # Required: frontmatter + instructions
├── scripts/              # Optional: helper scripts (executed, not loaded into context)
│   └── <skill-name>.py   # Default: Python with PEP 723 shebang (needs uv)
│   ├── <skill-name>.sh   # Shell mode: bash wrapper (needs python)
│   └── _<skill-name>.py  # Shell mode: Python impl, no PyPI deps
├── references/           # Optional: detailed docs loaded on demand (numbered prefix)
│   └── 01-topic.md
│   └── 02-abc.md
│   └── 03-xyz.md
├── assets/               # Optional: templates, images, data files, schemas
│   └── template.yaml
```

### Frontmatter Fields

| Field | Required | Rules |
|---|---|---|
| `name` | Yes | 1-64 chars, lowercase letters (including Unicode/i18n), 0-9, hyphens; no leading/trailing/consecutive hyphens; must match directory name exactly (e.g., `demo-skill-2-4-1` for `demo-skill-2-4-1/`); meta skills without versions use plain name (e.g., `skman`, `plan`) |
| `description` | Yes | Non-empty, max 1024 chars, third-person, must not contain XML/HTML tags (`<tag>`) or a `:` character |
| `license` | No | License name or reference to a bundled license file (e.g., `Apache-2.0`, `Proprietary. LICENSE.txt has complete terms`) |
| `compatibility` | No | Max 500 chars. Environment requirements — intended product, system packages, network access. Only include if the skill has specific needs |
| `metadata` | No | Optional object. May contain `tags` (array of strings, e.g., `["meta", "devops"]`). Validator warns if `metadata` is not a mapping or `tags` is not a string array.

All top-level text fields (`name`, `description`, `license`, `compatibility`, and any unknown string field) must not contain a `:` character. Colons are YAML structural characters — `Use when: X` inside an unquoted scalar is invalid YAML, and naive frontmatter parsers misread them. Rephrase or use `;` instead; the validator errors on any `:` in a text field.

### Frontmatter Template

```yaml
---
name: my-skill
description: What this skill does and when to use it. Be specific.
license: Apache-2.0
compatibility: Requires Python 3.11+ and uv
metadata:
  tags:
    - dev
---
```

## Creating a New Skill

Follow these steps in order:

1. **Choose a name** — lowercase, hyphens, numbers only (e.g., `pdf-processing`, `git-8-20-0`). No leading/trailing/consecutive hyphens.

2. **Write the frontmatter** — exactly `name` and `description` at minimum. The `name` must match the directory name exactly. The description determines when the agent loads this skill; make it specific. Keep text-only fields free of `:` characters (write "Use when X", not "Use when: X").

3. **Write the body** — concise instructions, under 5000 tokens. Must start with a level-1 heading matching `# <name>` or `# <name> <version>`. Structure:
   - `# <name>` (e.g., `# skman`) or `# <name> <version>` (e.g., `# demo-skill 2.4.1`)
   - `## Overview` — what it does
   - `## Usage` — Optional: how to use it with examples
   - `## Gotchas` — Optional: The most useful part of teaching a skill is listing its hidden traps. Instead of vague advice, provide specific rules that stop the agent from making predictable, common-sense mistakes in that specific environment.
   - `## References` — Optional: Provides on-demand reference material for agents. Always use a bulleted list, never a table:
     ```
     ## References

     - [01-core-expressions](references/01-core-expressions.md) — Symbols, expressions, numbers
     - [02-algebra-polynomials](references/02-algebra-polynomials.md) — Polynomial rings, factoring
     ```
     Each line: link to the file followed by a dash and a brief topic summary. Links to local `references/NN-topic.md` files and external URLs are both acceptable.

4. **Create scripts** — only when the user explicitly requests them. Two conventions:
   - **Default (Python with dependencies):** `scripts/<name>.py` — single file, PEP 723 shebang (`#!/usr/bin/env -S uv run --script`), direct execution. Requires `uv` on PATH.
   - **Shell mode (no PyPI deps):** `scripts/<name>.sh` + `scripts/_<name>.py` — bash wrapper delegates to underscore-prefixed Python script directly. Requires only `python` on PATH.
   Dependent scripts use whatever language the user specifies — never assume one. Scripts are **executed** (not loaded into context). Include `--help` at every level. Scaffold with `--with-scripts`.

5. **Validate** — run the validation script:
   ```bash
   skman.py validate <path-to-skill>
   ```

### Manual Creation

When writing files directly, the same rules apply: the directory is named after the skill (or `<skill-name>-<version>`), `SKILL.md` sits at its root, and the frontmatter `name` plus the first H1 match the directory (see the Gotchas below).

## Editing a Skill

Common operations:

- **Update description** — edit the frontmatter; this is what agents see in the system prompt
- **Split long content** — move sections >100 lines into `references/NN-topic.md`, link from SKILL.md
- **Add a script** — place in `scripts/` with the skill's name as base name
- **Restructure references** — keep references one level deep; all should link directly from SKILL.md

## Validation

Checks performed:
- Frontmatter presence, valid YAML (errors on parse failure or non-mapping), no duplicate top-level keys
- Text-only fields contain no `:` character (errors on any `:` in `name`, `description`, `license`, `compatibility`, or unknown string fields)
- Name format (case, characters, length, hyphen rules)
- Description presence, length, and absence of XML/HTML tags
- `metadata` structure (warns if present but not a mapping; warns if `tags` is not a string array)
- Body starts with a level-1 heading
- Body token estimation warning (>5000 tokens)
- Name vs directory basename consistency (warns on mismatch)
- H1 heading format (`# <name>` or `# <name> <version>` — errors on mismatch)
- Recommended section presence (`## Overview` — warns if missing)
- Truly optional sections (`## Usage`, `## Gotchas`, `## References` — no warning when absent)
- Script executability (`<name>.sh` must be `chmod +x` — warns if not)
- Script usage references (`./<name>.sh` → `<name>.sh` — warns if the body uses `./<name>.sh` outside fenced code blocks)

## Best Practices

### Conciseness
- Context window is shared — every token competes with conversation history
- Default assumption: the model already knows basics (what PDFs are, how libraries work)
- Challenge each paragraph: "Does this justify its token cost?"

### Scripting
- **Default entry point is `scripts/<name>.py`** — Python with PEP 723 shebang, direct execution via `uv run --script`. No bash wrapper needed.
- **Shell mode (on request):** `scripts/<name>.sh` + `scripts/_<name>.py` — bash wrapper delegates to underscore-prefixed Python. Used when the script has no PyPI dependencies (no `uv run` needed).
- **Dependent scripts use whatever language the user specifies** — Python, JS (Node/Bun/Deno), Lua, Bash, or anything else. Never assume a language; ask the user or wait for their suggestion
- **Python scripts always use `uv run --script`** — every Python script uses the PEP 723 inline metadata block so `uv run` resolves dependencies automatically. No `pip install`, no `requirements.txt`, no manual venv. The shebang `#!/usr/bin/env -S uv run --script` makes the script directly executable. Declare `requires-python` and `dependencies` inside the `# /// script ... # ///` block.
  ```python
  #!/usr/bin/env -S uv run --script
  #
  # /// script
  # requires-python = ">=3.12"
  # dependencies = ["PyYAML", "requests"]
  # ///
  ```
- Any libraries, frameworks, or dependencies are allowed when the user explicitly requests them

### Match Specificity to Task Fragility
- **High freedom** (text): multiple valid approaches, context-dependent decisions
- **Medium** (scripts with parameters): preferred pattern exists, some variation OK
- **Low** (exact commands): fragile operations, consistency is critical

### Description Writing
- Always third person ("Processes Excel files" not "I can help you")
- Include both what the skill does and when to use it
- Include relevant context (file extensions, tool names, task types) so the agent knows when to apply the skill

### Writing Style
- **Use imperative voice** — "Run this command" not "You should run this command"
- **Explain the why, avoid rigid MUST/ALWAYS/NEVER in caps** — modern models respond better to reasoning than rigid commands. If something is critical, explain why it matters

### Progressive Disclosure
Skills use a four-level loading system:

1. **Metadata** (name + description) — always in context (~100 words). Always visible to the agent.
2. **SKILL.md body** — loaded on demand (<5000 tokens ideal). Contains the core instructions.
3. **Scripts** — executed (not loaded into context). Run via `<name>.py` (default) or `<name>.sh` (shell mode).
4. **References** — loaded as needed (unlimited). Reference files load on demand.

Guidelines:
- Keep SKILL.md body under 5000 tokens
- Move detailed content to `references/` files linked from SKILL.md
- Avoid deeply nested references — all reference files should link directly from SKILL.md
- Include a table of contents in reference files longer than 100 lines
- **Reference file naming** — use incrementing numeric prefixes (`01-`, `02-`, …) so files are named `NN-topic.md`, giving deterministic ordering and easy insertion
- **Multi-domain skills** — when a skill supports multiple variants (frameworks, platforms), organize by domain in references:
  ```
  cloud-deploy/
  ├── SKILL.md              # workflow + variant selection logic
  └── references/
      ├── 00-aws.md
      ├── 01-gcp.md
      └── 02-azure.md
  ```

### Model Compatibility
SLMs need more explicit guidance and numbered steps; LLMs prefer concise instructions without over-explaining. Aim for clear structure and explicit rules that work across both.

## Gotchas

- **Never create `scripts/` or `assets/` automatically** — these directories are only created when the user explicitly asks for them. `skman.py create` does not generate them by default; use `--with-scripts` only on direct user request. Never scaffold scripts or assets without being asked.
- **Default script is Python, not bash** — `--with-scripts` creates `scripts/<name>.py` with PEP 723 shebang. Use `--lang bash` for the shell wrapper + `_<name>.py` convention.
- **Scaffolded files may lose execute permission** — `skman.py create --with-scripts` sets `chmod 0o755`, but editors or git checkouts can strip it. Always verify with `ls -l <name>.py`; the validator warns if the bit is missing.
- **`--strict` turns section warnings into errors** — only `## Overview` produces a warning when missing. `## Usage`, `## Gotchas`, and `## References` are truly optional and never warn (knowledge-only skills often have no Usage section). In strict mode, any warning fails validation.
- **No `:` in text-only frontmatter fields** — `description: Use when: X` is invalid YAML (mapping values are not allowed in this context), and even `foo:bar` confuses naive frontmatter parsers. Keep every top-level scalar string field (`name`, `description`, `license`, `compatibility`) free of colons; rephrase or use `;`. The validator errors on any `:` in these fields, and `create` rejects colon descriptions before scaffolding anything.
- **Frontmatter `name` must match the directory basename exactly** — e.g., `demo-skill-2-4-1/` requires `name: demo-skill-2-4-1`, `skman/` requires `name: skman`. The validator warns on mismatch. Fix by renaming the directory or correcting the frontmatter.
- **H1 heading must match `# <name>` or `# <base> <version>`** — the validator errors if the first heading doesn't match. For `skman/` it must be `# skman`; for `demo-skill-2-4-1/` it must be `# demo-skill 2.4.1` (version uses dots, not hyphens). The version in the H1 must correspond to the hyphenated version suffix in the directory/frontmatter name.
- **Reference files are loaded on demand, not into context** — keep SKILL.md self-contained for core instructions; move deep-dive content to `references/NN-topic.md` and link from the body.
- **PEP 723 block is mandatory for Python scripts** — every Python script must include the `# /// script ... # ///` metadata block. `uv run` depends on it to resolve dependencies. The block goes at the top of the file, after the shebang. Without it, `uv run script.py` runs with no dependency management.
- **Clone repos locally before studying them** — when a URL is given as source material to study or analyze for writing a skill, check whether it points to a code repository (GitHub, GitLab, Bitbucket, etc.). If so, clone it into a temporary directory first and read files from the local copy. Fetching individual files over the network is expensive in both time and rate limits; a single `git clone` gives you the full tree instantly. Clean up the temp directory after analysis.

## References

- [01-python-scripts](references/01-python-scripts.md) — PEP 723 inline dependencies, `uv run --script`, shebang patterns

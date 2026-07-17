# Agent Skills Specification

The complete format specification for Agent Skills.

## Directory structure

A skill is a directory containing, at minimum, a `SKILL.md` file:

```
skill-name/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
├── assets/           # Optional: templates, resources
└── ...               # Any additional files or directories
```

## SKILL.md format

The `SKILL.md` file must contain YAML frontmatter followed by Markdown content.

### Frontmatter fields

| Field | Required | Constraints |
|---|---|---|
| `name` | Yes | Max 64 chars. Lowercase letters, numbers, hyphens only. Must not start/end with hyphen. Must not contain consecutive hyphens. Must match parent directory name. |
| `description` | Yes | Max 1024 chars. Non-empty. Describes what the skill does and when to use it. |
| `license` | No | License name or reference to a bundled license file. |
| `compatibility` | No | Max 500 chars. Environment requirements (intended product, system packages, network access). |
| `metadata` | No | Arbitrary key-value mapping for additional metadata. |
| `allowed-tools` | No | Space-separated string of pre-approved tools. Experimental. |

### name field rules

- 1-64 characters
- Unicode lowercase alphanumeric (`a-z`, `0-9`) and hyphens (`-`) only
- Must not start or end with a hyphen
- Must not contain consecutive hyphens (`--`)
- Must match the parent directory name exactly

Valid: `pdf-processing`, `data-analysis`, `code-review`

Invalid: `PDF-Processing` (uppercase), `-pdf` (leading hyphen), `pdf--processing` (consecutive hyphens)

### description field

- 1-1024 characters
- Should describe both what the skill does and when to use it
- Should include specific keywords that help agents identify relevant tasks

Good: `Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.`

Poor: `Helps with PDFs.`

### license field

Specifies the license applied to the skill. Keep it short — either a license name or reference to a bundled file.

Example: `license: Proprietary. LICENSE.txt has complete terms`

### compatibility field

Only include if the skill has specific environment requirements.

Examples:
- `compatibility: Designed for Claude Code (or similar products)`
- `compatibility: Requires git, docker, jq, and access to the internet`
- `compatibility: Requires Python 3.14+ and uv`

### metadata field

A map from string keys to string values. Clients can store additional properties not defined by the spec. Make key names reasonably unique to avoid conflicts.

```yaml
metadata:
  author: example-org
  version: "1.0"
```

### allowed-tools field

Space-separated string of pre-approved tools. Experimental — support varies between implementations.

Example: `allowed-tools: Bash(git:*) Bash(jq:*) Read`

### Minimal frontmatter

```yaml
---
name: skill-name
description: A description of what this skill does and when to use it.
---
```

### Frontmatter with optional fields

```yaml
---
name: pdf-processing
description: Extract PDF text, fill forms, merge files. Use when handling PDFs.
license: Apache-2.0
metadata:
  author: example-org
  version: "1.0"
---
```

## Body content

The Markdown body after frontmatter contains skill instructions. No format restrictions — write whatever helps agents perform the task effectively. Recommended sections:

- Step-by-step instructions
- Examples of inputs and outputs
- Common edge cases

The agent loads the entire file once activated. Consider splitting longer content into referenced files.

## Optional directories

### scripts/

Contains executable code that agents can run. Scripts should:

- Be self-contained or clearly document dependencies
- Include helpful error messages
- Handle edge cases gracefully

Supported languages depend on the agent implementation. Common options: Python, Bash, JavaScript.

### references/

Contains additional documentation that agents can read when needed:

- `REFERENCE.md` — Detailed technical reference
- `FORMS.md` — Form templates or structured data formats
- Domain-specific files (`finance.md`, `legal.md`, etc.)

Keep individual files focused. Agents load these on demand, so smaller files mean less context usage.

### assets/

Contains static resources:

- Templates (document templates, configuration templates)
- Images (diagrams, examples)
- Data files (lookup tables, schemas)

## Progressive disclosure

Agents load skills progressively, pulling in more detail only as a task calls for it:

1. **Metadata** (~100 tokens): `name` and `description` loaded at startup for all skills
2. **Instructions** (<5000 tokens recommended): Full `SKILL.md` body loaded when the skill is activated
3. **Resources** (as needed): Files in `scripts/`, `references/`, or `assets/` loaded only when required

Keep the main `SKILL.md` under 500 lines. Move detailed reference material to separate files.

## File references

Use relative paths from the skill root when referencing other files:

```markdown
See [the reference guide](references/REFERENCE.md) for details.

Run the extraction script:
scripts/extract.py
```

Keep file references one level deep from `SKILL.md`. Avoid deeply nested reference chains.

## Validation

Use the [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) reference library:

```bash
skills-ref validate ./my-skill
```

This checks that `SKILL.md` frontmatter is valid and follows all naming conventions.

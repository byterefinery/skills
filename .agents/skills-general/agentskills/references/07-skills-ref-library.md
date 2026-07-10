# skills-ref Library

The official Python reference library for Agent Skills.

> This library is intended for demonstration purposes only. It is not meant to be used in production.

## Installation

### Using uv (recommended)

```bash
uv sync
source .venv/bin/activate
```

### Using pip

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### As a one-off command (uvx)

```bash
uvx skills-ref validate ./my-skill
```

## CLI commands

### validate

Check that a skill has a valid `SKILL.md` with proper frontmatter, correct naming conventions, and required fields.

```bash
skills-ref validate path/to/skill
```

Exit codes: 0 = valid, 1 = validation errors found.

Validation checks:

- Frontmatter presence and YAML validity
- `name` field: lowercase, alphanumeric + hyphens, no leading/trailing/consecutive hyphens, max 64 chars
- `name` must match parent directory name
- `description` field: non-empty, max 1024 chars
- `compatibility` field: max 500 chars (if present)
- No unexpected fields in frontmatter
- Required file `SKILL.md` exists

### read-properties

Parse the YAML frontmatter from `SKILL.md` and output properties as JSON.

```bash
skills-ref read-properties path/to/skill
```

Output:

```json
{
  "name": "my-skill",
  "description": "What this skill does.",
  "license": "Apache-2.0",
  "compatibility": "Requires Python 3.11+",
  "allowed-tools": "Bash(git:*) Read",
  "metadata": {
    "author": "example-org",
    "version": "1.0"
  }
}
```

None values are omitted from output. Empty `metadata` dict is omitted.

### to-prompt

Generate `<available_skills>` XML block for agent system prompts. Accepts one or more skill directories.

```bash
skills-ref to-prompt path/to/skill-a path/to/skill-b
```

Output:

```xml
<available_skills>
<skill>
<name>
my-skill
</name>
<description>
What this skill does and when to use it
</description>
<location>
/path/to/my-skill/SKILL.md
</location>
</skill>
</available_skills>
```

This XML format is what Anthropic uses and recommends for Claude models. Skill clients may format skill information differently to suit their models.

## Python API

```python
from pathlib import Path
from skills_ref import validate, read_properties, to_prompt

# Validate a skill directory
problems = validate(Path("my-skill"))
if problems:
    print("Validation errors:", problems)

# Read skill properties
props = read_properties(Path("my-skill"))
print(f"Skill: {props.name} - {props.description}")

# Generate prompt for available skills
prompt = to_prompt([Path("skill-a"), Path("skill-b")])
print(prompt)
```

### SkillProperties dataclass

```python
@dataclass
class SkillProperties:
    name: str
    description: str
    license: Optional[str] = None
    compatibility: Optional[str] = None
    allowed_tools: Optional[str] = None
    metadata: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values."""
```

### parse_frontmatter

```python
from skills_ref.parser import parse_frontmatter

metadata, body = parse_frontmatter(skill_md_content)
```

Returns a tuple of (metadata dict, markdown body string). Raises `ParseError` if frontmatter is missing or invalid.

### find_skill_md

```python
from skills_ref.parser import find_skill_md

skill_md_path = find_skill_md(Path("my-skill"))
# Returns Path to SKILL.md or skill.md, or None
```

Prefers `SKILL.md` (uppercase) but accepts `skill.md` (lowercase).

### validate_metadata

```python
from skills_ref.validator import validate_metadata

errors = validate_metadata(metadata_dict, skill_dir=Path("my-skill"))
# Returns list of error messages. Empty list means valid.
```

Core validation function that works on already-parsed metadata, avoiding duplicate file I/O.

## Dependencies

- **click** — CLI framework
- **strictyaml** — Strict YAML parsing

## License

Apache 2.0

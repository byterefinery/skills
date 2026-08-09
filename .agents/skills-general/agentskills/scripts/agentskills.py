#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.11"
# dependencies = ["skills-ref>=0.1.0"]
# ///

"""agentskills — CLI wrapper around the skills-ref library.

Validate Agent Skills, read properties, and generate <available_skills> XML.

Usage:
    agentskills.py validate <skill-path>
    agentskills.py read-properties <skill-path>
    agentskills.py to-prompt <skill-path> [skill-path ...]
    agentskills.py --help
"""

import json
import sys
from pathlib import Path

from skills_ref import read_properties, to_prompt, validate


def is_skill_md(path: Path) -> bool:
    """Check if path is a SKILL.md file."""
    return path.is_file() and path.name.lower() == "skill.md"


def resolve_skill_dir(path: Path) -> Path:
    """Resolve skill directory from path (handle SKILL.md file paths)."""
    if is_skill_md(path):
        return path.parent
    return path


def cmd_validate(skill_path: str):
    """Validate a skill directory."""
    path = resolve_skill_dir(Path(skill_path))
    errors = validate(path)

    if errors:
        print(f"Validation failed for {path}:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"Valid skill: {path}")


def cmd_read_properties(skill_path: str):
    """Read and print skill properties as JSON."""
    path = resolve_skill_dir(Path(skill_path))
    props = read_properties(path)
    print(json.dumps(props.to_dict(), indent=2))


def cmd_to_prompt(skill_paths: list[str]):
    """Generate <available_skills> XML for agent prompts."""
    paths = [resolve_skill_dir(Path(p)) for p in skill_paths]
    print(to_prompt(paths))


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "validate":
        if len(sys.argv) < 3:
            print("Usage: agentskills.py validate <skill-path>", file=sys.stderr)
            sys.exit(1)
        cmd_validate(sys.argv[2])

    elif command == "read-properties":
        if len(sys.argv) < 3:
            print("Usage: agentskills.py read-properties <skill-path>", file=sys.stderr)
            sys.exit(1)
        cmd_read_properties(sys.argv[2])

    elif command == "to-prompt":
        if len(sys.argv) < 3:
            print("Usage: agentskills.py to-prompt <skill-path> [skill-path ...]", file=sys.stderr)
            sys.exit(1)
        cmd_to_prompt(sys.argv[2:])

    elif command in ("--help", "-h", "help"):
        print(__doc__)
        print("Commands:")
        print("  validate <path>              Validate a skill directory")
        print("  read-properties <path>       Print skill properties as JSON")
        print("  to-prompt <path> [path ...]  Generate <available_skills> XML")
        sys.exit(0)

    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()

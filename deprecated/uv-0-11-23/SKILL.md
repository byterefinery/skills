---
name: uv-0-11-23
description: >
  Manages Python packages, projects, scripts, tools, and Python versions with extreme speed.
  Use when the user mentions uv, python packages, pip replacement, virtual environments, venv,
  pyproject.toml, dependency management, python version switching, tool installation (uvx),
  script dependencies, lockfiles, workspace management, or any Python packaging task.
  Replaces pip, pip-tools, pipx, poetry, pyenv, twine, and virtualenv.
---

# uv 0.11.23

An extremely fast Python package and project manager written in Rust. A single tool replacing `pip`, `pip-tools`, `pipx`, `poetry`, `pyenv`, `twine`, `virtualenv`, and more — 10-100x faster than pip.

## Overview

uv provides four main interfaces:

1. **Projects** — Full project management with lockfiles, workspaces, and environments (`uv init`, `uv add`, `uv run`, `uv sync`, `uv lock`)
2. **Scripts** — Run Python scripts with on-demand dependency resolution, including inline metadata (PEP 723)
3. **Tools** — Install and run CLI tools from Python packages, like `pipx` (`uvx`, `uv tool install`)
4. **Python versions** — Install and manage Python interpreters, auto-downloading as needed

It also includes a **pip-compatible interface** (`uv pip install`, `uv pip compile`, `uv venv`) for gradual migration from existing workflows.

## Usage

### Projects

```bash
# Create a new project
uv init my-project

# Add dependencies (auto-creates .venv, updates lockfile)
uv add requests flask

# Add with version constraints
uv add 'requests>=2.28,<3'

# Remove a dependency
uv remove requests

# Run commands in the project environment
uv run python main.py
uv run -- flask run -p 3000

# Lock dependencies (generates uv.lock)
uv lock

# Sync environment to match lockfile
uv sync

# Build distributions
uv build

# View dependency tree
uv tree
```

### Scripts

```bash
# Run a script (auto-manages environment)
uv run script.py

# Run with ad-hoc dependencies
uv run --with rich,requests script.py

# Add inline metadata to a script (PEP 723)
uv add --script script.py requests

# Initialize a new script with metadata
uv init --script tool.py --python 3.12

# Lock script dependencies
uv lock --script script.py
```

### Tools (like pipx)

```bash
# Run a tool in an ephemeral environment (alias: uvx)
uv tool run ruff check .
uvx ruff check .

# Run specific version
uvx ruff@0.9.0 check .

# Install a tool persistently (adds to PATH)
uv tool install ruff

# Upgrade tools
uv tool upgrade ruff
uv tool upgrade --all

# List installed tools
uv tool list

# Uninstall a tool
uv tool uninstall ruff
```

### Python Versions

```bash
# Install Python versions
uv python install 3.12
uv python install 3.11 3.12 3.13

# Install PyPy
uv python install pypy@3.10

# List installed and available versions
uv python list

# Pin Python version for current directory
uv python pin 3.12

# Upgrade to latest patch
uv python upgrade 3.12
```

### pip Interface (drop-in replacement)

```bash
# Create virtual environment
uv venv --python 3.12

# Install packages
uv pip install flask requests

# Compile requirements (like pip-compile)
uv pip compile requirements.in -o requirements.txt

# Sync environment to match requirements
uv pip sync requirements.txt

# Uninstall packages
uv pip uninstall flask
```

### Common Flags

| Flag | Description |
|---|---|
| `--python VERSION` | Use specific Python version (e.g., `3.12`, `pypy@3.10`) |
| `--with PACKAGE` | Include additional packages (run/tool contexts) |
| `--no-project` | Skip project context, run standalone |
| `--system` | Install into system Python (CI/containers) |
| `--exclude-newer DATE` | Limit to distributions released before date |

## Gotchas

- **`uvx` vs `uv run` for tools** — `uvx` runs in an isolated environment. Use `uv run` when the tool needs access to your project (e.g., `pytest`, `mypy`).
- **Package name vs command name** — When they differ, use `--from`: `uvx --from httpie http`.
- **Inline script metadata ignores project deps** — Scripts with `# /// script` blocks run independently of the surrounding project. No need for `--no-project`.
- **Automatic Python downloads** — uv downloads Python on-demand by default. Disable with `UV_PYTHON_DOWNLOADS=never` or `--no-managed-python`.
- **`.venv` naming** — uv creates `.venv` by default. Use `VIRTUAL_ENV=/path/to/venv` to target a different environment.
- **Lockfile format** — `uv.lock` is TOML-based and managed automatically. Do not edit it manually.
- **`--system` flag** — Required when installing into non-virtual (system) Python. Skips virtualenv discovery.

## References

- [01-projects](references/01-projects.md) — Project lifecycle: init, add, lock, sync, run, build
- [02-tools](references/02-tools.md) — Tool management: uvx, install, upgrade, list, uninstall
- [03-scripts](references/03-scripts.md) — Script execution, inline metadata (PEP 723), shebangs
- [04-python-versions](references/04-python-versions.md) — Python installation, discovery, pinning, upgrades
- [05-pip-interface](references/05-pip-interface.md) — pip-compatible commands: install, compile, sync, uninstall
- [06-workspaces](references/06-workspaces.md) — Multi-package workspace setup and management
- [07-resolution](references/07-resolution.md) — Resolution strategies, constraints, overrides, indexes

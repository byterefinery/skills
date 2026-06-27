# Projects

uv manages Python projects defined by `pyproject.toml`. It handles dependency resolution, lockfiles, virtual environments, and execution — all in one tool.

## Project Lifecycle

### Creating a project

```bash
# Create new project in subdirectory
uv init my-project

# Initialize current directory as project
mkdir my-project && cd my-project && uv init
```

`uv init` creates:
- `pyproject.toml` — project metadata and dependencies
- `.python-version` — pinned Python version
- `.gitignore` — excludes `.venv`, `__pycache__`, etc.
- `README.md`
- `main.py` — entry point

When run inside an existing project, `uv init subpkg` creates a workspace member.

### Project structure

```
my-project/
├── .git/
├── .venv/              # Virtual environment (auto-created)
├── .python-version     # Pinned Python version
├── pyproject.toml      # Project config + dependencies
├── uv.lock             # Lockfile (auto-generated, commit to VCS)
├── main.py
└── README.md
```

### `pyproject.toml`

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.12"
dependencies = []

[build-system]
requires = ["uv_build>=0.11.23,<0.12"]
build-backend = "uv_build"
```

uv supports standard `pyproject.toml` (PEP 621) and can work with any build backend.

## Managing Dependencies

### Adding dependencies

```bash
# Basic add
uv add requests

# With version constraint
uv add 'requests>=2.28,<3'

# From git
uv add git+https://github.com/psf/requests

# From requirements.txt
uv add -r requirements.txt

# Dev dependencies
uv add --dev pytest ruff

# Optional dependency group
uv add --group test coverage
```

Dependencies go into `[project.dependencies]`. Dev deps go into `[tool.uv.dev-dependencies]` (or `[project.optional-dependencies]` for standard groups).

### Removing dependencies

```bash
uv remove requests
uv remove --dev pytest
```

### Upgrading specific packages

```bash
# Upgrade one package in lockfile
uv lock --upgrade-package requests

# Upgrade all packages
uv lock --upgrade
```

## Locking and Syncing

### Lock

`uv lock` resolves all dependencies and writes `uv.lock`. This is a cross-platform TOML lockfile containing exact versions for every platform. Commit it to version control.

```bash
uv lock
```

Run `uv lock` after changing `pyproject.toml` dependencies. `uv run` and `uv sync` auto-resolve if the lockfile is stale, but explicit locking is recommended before committing.

### Sync

`uv sync` updates the `.venv` to match `uv.lock`. It installs missing packages and can remove extraneous ones.

```bash
# Sync all workspace members
uv sync

# Sync a specific package
uv sync --package my-lib

# Include dev dependencies
uv sync --all-extras
```

By default, `uv sync` does not remove extraneous packages (those installed but not in the lockfile). Use `--no-extraneous-packages` to enforce exact match.

## Running Commands

`uv run` executes commands in the project environment. Before every invocation, it verifies the lockfile is up-to-date and syncs if needed.

```bash
# Run a script
uv run main.py

# Run with arguments
uv run main.py --flag value

# Run an installed command
uv run -- flask run -p 3000

# Run with additional packages
uv run --with ipython python

# Run without project context
uv run --no-project script.py
```

The `--` separator is optional but clarifies where the tool name ends and arguments begin.

## Dependency Groups (PEP 735)

```toml
[project.optional-dependencies]
test = ["pytest>=8"]
docs = ["sphinx>=7"]
```

Install specific groups:
```bash
uv sync --group test
uv pip install --group test
```

## Building Distributions

```bash
# Build sdist and wheel
uv build

# Build only wheel
uv build --wheel

# Build only source distribution
uv build --sdist

# Build a different project directory
uv build /path/to/project

# Output to custom directory
uv build --out-dir dist/
```

## Export Lockfile

Export `uv.lock` to other formats:

```bash
# Export to requirements.txt format
uv export -r requirements.txt

# Include dev dependencies
uv export --dev

# Specific Python version/platform
uv export --python-version 3.11 --python-platform linux
```

## Configuration in `pyproject.toml`

```toml
[tool.uv]
# Exclude newer distributions
exclude-newer = "2025-01-01T00:00:00Z"

# Custom index URLs
index-url = "https://pypi.org/simple"

# Override package sources
[tool.uv.sources]
mypackage = { git = "https://github.com/me/mypackage" }

# Workspace members
[tool.uv.workspace]
members = ["packages/*"]
```

## Viewing Project Info

```bash
# Show dependency tree
uv tree

# Show package version
uv version
uv version --short
uv version --output-format json
```

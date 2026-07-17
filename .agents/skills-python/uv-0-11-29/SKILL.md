---
name: uv-0-11-29
description: >
  uv 0.11.29 — extremely fast Python package and project manager. Use when the user mentions
  uv, uvx, Python package management, virtual environments, dependency resolution, pyproject.toml
  projects, uv lock, uv sync, uv run, uv add, uv remove, uv tool, uv python, uv pip, uv venv,
  uv build, uv publish, inline script metadata (PEP 723), workspaces, or any Python packaging
  and environment management task. Replaces pip, pip-tools, pipx, poetry, pyenv, twine, and
  virtualenv.
license: Apache-2.0 OR MIT
metadata:
  tags:
    - python
    - packaging
    - environments
    - devops
---

# uv 0.11.29

## Overview

uv is an extremely fast Python package and project manager written in Rust by Astral (creators of
Ruff and ty). It provides a unified interface replacing `pip`, `pip-tools`, `pipx`, `poetry`,
`pyenv`, `twine`, and `virtualenv`.

uv 0.11.29 (released 2026-07-15) adds JSON output to `uv tree`, CUDA 13.2 PyTorch backend support,
gzip-compressed PyPy downloads, scoped overrides/exclusions, and full `pylock.toml` hardening.

uv's interface has five independent sections:

- **Python versions** — install, manage, and discover Python interpreters
- **Scripts** — run standalone `.py` files with inline dependency metadata (PEP 723)
- **Projects** — full project management with `pyproject.toml`, lockfiles, and workspaces
- **Tools** — run and install CLI tools (`uvx` / `uv tool`)
- **Pip interface** — drop-in replacement for `pip`, `pip-tools`, and `virtualenv`

## Usage

### Installation

```bash
# Standalone installer (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# From PyPI
pip install uv
pipx install uv

# Self-update
uv self update
```

### Projects — create and manage

```bash
uv init my-project                  # create new project
cd my-project
uv add requests                     # add dependency (updates lock + env)
uv add 'flask>=3.0'                 # version constraint
uv add git+https://github.com/...   # git dependency
uv remove requests                  # remove dependency
uv lock                             # resolve and write uv.lock
uv sync                             # install locked deps into .venv
uv run python main.py               # run in project environment
uv run -- flask run -p 3000         # run CLI in project environment
uv tree                             # show dependency tree
uv tree --format json               # JSON output (0.11.29)
uv build                            # build sdist and wheel to dist/
uv publish                          # publish to PyPI or index
```

### Scripts — inline metadata (PEP 723)

```bash
# Create a script with inline metadata
uv init --script example.py --python 3.12

# Add dependencies to a script
uv add --script example.py requests rich

# Run with automatic env creation
uv run example.py

# Run with ad-hoc dependencies
uv run --with rich example.py

# Lock script dependencies
uv lock --script example.py         # creates example.py.lock
```

Inline metadata block in the script:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "requests<3",
#   "rich",
# ]
# ///

import requests
```

### Tools — run and install CLIs

```bash
uvx ruff check .                    # ephemeral run (alias: uv tool run)
uvx 'black[jupyter]@24.4.0' .      # specific version with extras
uvx --from httpie http              # command name differs from package
uvx --with mkdocs-material mkdocs   # run with plugin

uv tool install ruff                # persistent install to PATH
uv tool upgrade ruff                # upgrade a tool
uv tool upgrade --all               # upgrade all tools
uv tool uninstall ruff              # remove a tool
uv tool list                        # list installed tools
uv tool update-shell                # add tool bin dir to PATH
```

### Python versions — install and manage

```bash
uv python install                   # install latest Python
uv python install 3.12 3.13        # install specific versions
uv python install pypy@3.10        # install PyPy
uv python list                      # list available/installed versions
uv python find '>=3.11'            # find a compatible interpreter
uv python pin 3.12                  # write .python-version file
uv python upgrade 3.12              # upgrade to latest patch
uv python uninstall 3.11            # remove a managed Python
```

### Pip interface — legacy workflows

```bash
uv venv --python 3.12               # create virtual environment
uv venv --python 3.12t              # free-threaded Python 3.12

uv pip install flask                # install package
uv pip install -r requirements.txt  # install from file
uv pip install -e .                 # editable install
uv pip uninstall flask              # uninstall package
uv pip list                         # list installed packages
uv pip freeze                       # freeze installed packages
uv pip tree                         # show dependency tree
uv pip check                        # check for conflicts
uv pip show flask                   # show package details

uv pip compile requirements.in -o requirements.txt   # lock dependencies
uv pip compile pyproject.toml -o requirements.txt     # lock from pyproject
uv pip sync requirements.txt                      # exact env match
```

### Cache management

```bash
uv cache dir                        # show cache directory
uv cache clean                      # clear entire cache
uv cache clean ruff                 # clear cache for one package
uv cache prune                      # remove unused entries
uv cache prune --ci                 # CI-optimized prune (keep built wheels)
```

### Common flags

```bash
uv sync --refresh                   # revalidate all cached data
uv sync --refresh-package ruff      # revalidate one package
uv sync --reinstall                 # ignore existing installs
uv sync --no-editable               # install project non-editably
uv run --no-project script.py       # skip project context
uv run --python 3.11 cmd            # override Python version
uv lock --upgrade-package requests  # upgrade one dep in lockfile
uv sync --frozen                    # skip lockfile check
uv sync --extra dev                 # include optional dep group
```

## Gotchas

- **`uv run` auto-syncs before every run.** It verifies the lockfile matches `pyproject.toml` and the environment matches the lockfile. Use `--frozen` to skip this check in CI or when you know the environment is current.

- **`uv run` does not remove extraneous packages by default.** Packages installed outside of uv's lockfile remain in `.venv`. Use `uv sync` (not `uv run`) to clean the environment to match the lockfile exactly.

- **`uvx` runs in an isolated environment.** It does not see your project's dependencies. Use `uv run` instead when the tool needs access to your project (e.g., `pytest`, `mypy`). Exception: flat-layout projects where the tool doesn't need the project installed.

- **Shell glob characters in `uvx` extras need quoting.** Use `uvx 'black[jupyter]@24.4.0'` not `uvx black[jupyter]@24.4.0` — the shell interprets brackets as glob patterns.

- **`--no-cache` still uses a temporary cache.** uv always requires a cache directory. `--no-cache` creates a temp directory for that single invocation. Use `--refresh` instead to update the cache without reading from it.

- **`uv pip compile` considers existing output file pins.** If `requirements.txt` already pins `ruff==0.3.0`, re-running compile won't upgrade it. Use `--upgrade` or `--upgrade-package ruff` to bump versions.

- **`uv python install` uses standalone builds, not official CPython.** uv sources from the `python-build-standalone` project. These are self-contained and portable but have quirks (e.g., no system `site-packages` by default).

- **Workspaces enforce a single `requires-python`.** The workspace takes the intersection of all members' `requires-python`. If members need different Python versions, use separate projects with path dependencies instead.

- **`uv tool install` isolates tools from the current environment.** Installing a tool does not make its Python modules importable in your project. This prevents dependency conflicts between tools and projects.

- **`VIRTUAL_ENV` is ignored during project operations by default.** uv uses `.venv` in the project root, not the active virtual environment. Use `--active` to respect `VIRTUAL_ENV`, or `--no-active` to silence the warning.

- **`uv add --script` with inline metadata ignores project deps.** When a script has a `# /// script` block, its dependencies are resolved independently of any surrounding project. No `--no-project` flag needed.

- **`uv lock` is idempotent but platform-aware.** The lockfile contains markers for different platforms. Running `uv lock` on different OS/arch may produce different resolved versions for platform-specific packages.

- **Flat indexes cache files by name.** Replacing a wheel under the same filename in a `--find-links` directory won't be picked up until the cache is refreshed. Use `--refresh` or `uv cache clean`.

- **`uv build` requires a build system.** The project must have a `[build-system]` table in `pyproject.toml`. Without it, uv uses `setuptools.build_meta:__legacy__` as fallback.

- **`uv publish` needs `UV_PUBLISH_TOKEN` or `--token`.** Set the environment variable or pass `--token` directly. Registry URL defaults to PyPI; override with `--index-url`.

## References

- [01-projects-and-workspaces](references/01-projects-and-workspaces.md) — Project layout, pyproject.toml, uv.lock, workspaces, dependency groups
- [02-scripts-and-tools](references/02-scripts-and-tools.md) — PEP 723 inline metadata, uvx, tool install/upgrade, shebang scripts
- [03-python-versions](references/03-python-versions.md) — Managed vs system Python, discovery, free-threaded, PyPy, GraalPy, .python-version
- [04-pip-interface](references/04-pip-interface.md) — uv pip install/compile/sync, requirements.txt, constraints, overrides, compatibility with pip
- [05-indexes-and-auth](references/05-indexes-and-auth.md) — Private indexes, PyTorch indexes, flat indexes, authentication, credential providers
- [06-configuration](references/06-configuration.md) — [tool.uv] settings, environment variables, config files, cache keys, build isolation
- [07-advanced-resolution](references/07-advanced-resolution.md) — Overrides, constraints, extra-build-dependencies, reproducible resolutions, exclude-newer
- [08-ci-and-deployment](references/08-ci-and-deployment.md) — CI caching strategies, Docker, uv cache prune --ci, frozen syncs, no-editable deploys

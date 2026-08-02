---
name: uv-0-12-1
description: Manage Python projects, scripts, tools, and environments with uv 0.12.1 — the extremely fast Python package and project manager. Use when the user mentions uv, uvx, Python project management, pyproject.toml dependency management, Python virtual environments, Python version installation, uv run, uv sync, uv lock, uv add, uv remove, uv pip, uv tool, uv build, uv publish, uv venv, uv cache, or any Python packaging/environment task. Replaces pip, pip-tools, pipx, pyenv, twine, and virtualenv.
license: Apache-2.0 OR MIT
compatibility: Requires uv 0.12.1 installed (via curl installer, pip, or pipx). Supports macOS, Linux, Windows.
metadata:
  tags:
    - python
    - packaging
    - environment-management
    - project-management
---

# uv 0.12.1

## Overview

uv is an extremely fast Python package and project manager written in Rust, by Astral (creators of Ruff and ty). It provides 10-100x speedup over pip and replaces pip, pip-tools, pipx, pyenv, twine, and virtualenv in a single tool.

uv 0.12.1 organizes its interface into five independent but composable sections:

1. **Python versions** — install and manage Python interpreters (`uv python install`)
2. **Scripts** — run single-file Python scripts with managed dependencies (`uv run script.py`)
3. **Projects** — full project management with lockfiles and workspaces (`uv init`, `uv add`, `uv sync`, `uv lock`)
4. **Tools** — run and install CLI tools from Python packages (`uvx ruff`, `uv tool install`)
5. **Pip interface** — drop-in replacement for pip/pip-tools/virtualenv (`uv pip install`, `uv pip compile`)

## Usage

### Installation

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh    # macOS/Linux
pip install uv                                      # via PyPI
pipx install uv                                     # via pipx
uv self update                                      # update uv itself
```

### Python versions

Install and manage Python interpreters directly:

```bash
uv python install 3.12                              # install specific version
uv python install 3.11 3.12                         # install multiple
uv python install pypy@3.10                         # alternative implementation
uv python list                                      # list available/installed versions
uv python pin 3.12                                  # pin .python-version in current dir
uv python upgrade 3.12                              # upgrade to latest patch (preview)
uv python install --default                         # also install python/python3 executables
```

uv auto-downloads Python versions on demand. Disable with `UV_PYTHON_DOWNLOADS=never` or `python-downloads = "never"` in config.

### Scripts — running single files

Run Python scripts with automatic dependency management:

```bash
uv run script.py                                    # run with system Python
uv run --python 3.12 script.py                      # run with specific Python
uv run --with requests script.py                    # add ad-hoc dependency
uv run --with 'rich>12,<13' script.py               # with version constraint
uv run --no-project script.py                       # skip project discovery
uv run -                                             # read script from stdin
```

Inline script metadata (PEP 723):

```bash
uv init --script example.py --python 3.12           # scaffold with metadata block
uv add --script example.py requests rich            # add deps to script
uv lock --script example.py                         # lock script deps (creates example.py.lock)
```

Script metadata block (auto-managed by `uv add --script`):

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "requests",
#   "rich",
# ]
# ///

import requests
```

Executable scripts with shebang

Add a shebang to make a script runnable directly — no `uv run` needed. The script executes via `uv` from `PATH`, with dependencies resolved from inline metadata:

```python
#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12"
# dependencies = ["httpx"]
# ///

import httpx

print(httpx.get("https://example.com"))
```

Make executable and run:

```bash
chmod +x my-script
./my-script
```

Dependencies declared in the inline metadata block are fully supported in this context — `requires-python`, `dependencies`, and `[tool.uv]` settings all work. The shebang form is ideal for standalone tools placed on `PATH` or shared as executable files.

### Projects — full project management

The primary workflow for managed Python projects:

```bash
uv init my-project                                  # scaffold new project (src layout, git init)
uv init --no-package                                # flat layout, no src/ directory
uv init --build-backend setuptools                  # choose build backend
cd my-project

uv add requests                                     # add dependency (updates pyproject.toml + lockfile + env)
uv add 'requests>=2.28'                             # with version constraint
uv add git+https://github.com/psf/requests          # from git
uv add --dev pytest                                 # dev dependency (dependency-groups.dev)
uv add --group lint ruff                            # named dev group
uv add --optional network httpx                     # optional dependency (extra)
uv add "jax; sys_platform == 'linux'"               # platform-specific
uv remove requests                                  # remove dependency

uv sync                                             # sync environment to lockfile
uv sync --extra foo                                 # include extra
uv sync --all-extras                                # include all extras
uv sync --no-dev                                    # exclude dev group
uv sync --frozen                                    # skip lockfile check
uv sync --reinstall                                 # force reinstall all
uv sync --no-install-project                        # skip installing project itself

uv lock                                             # create/update lockfile
uv lock --upgrade                                   # upgrade all packages
uv lock --upgrade-package requests                  # upgrade specific package
uv lock --check                                     # verify lockfile is current

uv run python main.py                               # run in project environment
uv run -- flask run -p 3000                         # run command
uv run --package bird-feeder pytest                  # run in workspace member
uv run --with devtools main.py                      # add ad-hoc dep at runtime
uv run --env-file .env -- python script.py          # load .env variables

uv tree                                             # show dependency tree
uv export --format requirements.txt                 # export lockfile
uv export --format pylock.toml                      # export as PEP 751
```

### Tools — run and install CLI tools

Run tools without installing (like pipx):

```bash
uvx ruff check .                                    # run tool in ephemeral env
uvx ruff@0.3.0 check                                # specific version
uvx ruff@latest check                               # latest version
uvx --from httpie http                              # command from different package
uvx --from 'mypy[faster-cache]' mypy .              # with extras
uvx --with mkdocs-material mkdocs serve             # with plugins
uvx --python 3.10 ruff                              # specific Python
uvx --from git+https://github.com/encode/httpx httpx  # from git
```

Install tools persistently:

```bash
uv tool install ruff                                # install to PATH
uv tool install 'httpie>0.1.0'                      # with version constraint
uv tool install --python 3.10 ruff                  # specific Python
uv tool upgrade ruff                                # upgrade installed tool
uv tool upgrade --all                               # upgrade all tools
uv tool uninstall ruff                              # remove tool
uv tool list                                        # list installed tools
uv tool update-shell                                # add tool bin dir to PATH
```

### Virtual environments

```bash
uv venv                                             # create .venv (auto-discovers Python)
uv venv --python 3.12                               # with specific Python
uv venv --python pypy@3.10                          # alternative implementation
uv venv --seed                                      # include pip/setuptools/wheel
source .venv/bin/activate                           # activate
```

### Pip interface — drop-in replacement

Low-level commands matching pip/pip-tools/virtualenv interfaces:

```bash
# Package management
uv pip install flask                                # install package
uv pip install 'ruff>=0.2.0'                        # with constraint
uv pip install -r requirements.txt                  # from file
uv pip install -e .                                 # editable install
uv pip install "git+https://github.com/..."         # from git
uv pip uninstall flask                              # uninstall
uv pip list                                         # list installed
uv pip freeze                                       # freeze installed
uv pip show flask                                   # show package details
uv pip tree                                         # dependency tree
uv pip check                                        # check compatibility

# Locking (pip-tools replacement)
uv pip compile requirements.in -o requirements.txt  # compile/lock
uv pip compile pyproject.toml -o requirements.txt   # from pyproject.toml
uv pip compile --universal -o requirements.txt      # cross-platform
uv pip compile --constraint constraints.txt          # with constraints
uv pip compile --override overrides.txt              # with overrides
uv pip compile --upgrade-package flask               # upgrade specific
uv pip sync requirements.txt                        # exact sync environment
```

### Cache management

```bash
uv cache dir                                        # show cache directory
uv cache clean                                      # clear entire cache
uv cache clean ruff                                 # clear specific package
uv cache prune                                      # remove unused entries
uv cache prune --ci                                 # CI-optimized prune (keep built wheels)
```

Use `--refresh` to revalidate all cached data, `--refresh-package pkg` for specific package, or `--reinstall` to force reinstall.

### Self-update and directories

```bash
uv self update                                      # update uv
uv --version                                        # show version
uv cache dir                                        # cache directory
uv tool dir                                         # tools directory
uv python dir                                       # Python installations directory
```

## Gotchas

- **`uv run` auto-syncs** — it locks and syncs before every run by default. Use `--frozen` to skip lockfile check, `--no-sync` to skip environment sync. In CI, prefer `--frozen` for speed.
- **`uv sync` removes extraneous packages** by default (exact sync). Use `--inexact` to retain packages not in the lockfile. `uv run` does the opposite — it keeps extraneous packages by default; use `--exact` for exact sync.
- **`uvx` runs isolated from projects** — tools run in ephemeral environments without project access. Use `uv run tool-name` instead when the tool needs project context (e.g., pytest, mypy).
- **Sources are uv-only** — `tool.uv.sources` in pyproject.toml is not understood by other tools. Use `uv build --no-sources` before publishing to verify the package builds without uv-specific sources.
- **Lockfile is universal** — `uv.lock` is cross-platform and covers all Python versions in `requires-python`. This means resolution can fail if no common version set exists across all platforms.
- **`--python` requests auto-download** — uv downloads missing Python versions automatically. Disable with `UV_PYTHON_DOWNLOADS=never`. Use `--no-managed-python` to force system Python only.
- **`uv pip` is not pip** — it matches pip's interface but does not invoke pip internally. Behavior diverges on edge cases. Consult the pip compatibility docs for differences.
- **Workspace `requires-python` is intersection** — all members share the intersection of their `requires-python` ranges. A single member cannot target a different Python range.
- **`.python-version` is local** — uv searches upward from the current directory but stops at project/workspace boundaries. Use `uv python pin --global` for system-wide defaults.
- **`uv add` adds constraints** — by default `uv add` pins `>=X.Y.Z` for the latest compatible version. Use `uv add 'pkg==X.Y.Z'` for exact pins or `--bounds` to control constraint style.
- **`--no-config` disables all config files** — this skips `pyproject.toml`, `uv.toml`, user config, and system config. Use when you need a clean slate.
- **`uv build` respects sources by default** — unlike `pypa/build`, uv reads `tool.uv.sources` during builds. Use `uv build --no-sources` before publishing to verify standard compatibility.

## References

- [01-projects](references/01-projects.md) — pyproject.toml layout, build systems, dependency fields, editable mode, packaging
- [02-pip-interface](references/02-pip-interface.md) — pip-compatible commands, compile/sync workflows, constraints, overrides
- [03-workspaces](references/03-workspaces.md) — multi-package workspaces, member sources, shared lockfiles, layouts
- [04-indexes](references/04-indexes.md) — private indexes, authentication, flat indexes, index strategies
- [05-configuration](references/05-configuration.md) — config files, environment variables, settings reference
- [06-advanced](references/06-advanced.md) — build isolation, cache keys, resolution strategies, publishing, Docker integration

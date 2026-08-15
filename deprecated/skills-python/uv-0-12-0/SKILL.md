---
name: uv-0-12-0
description: Manage Python projects, dependencies, scripts, tools, and Python versions with uv 0.12.0. Use when the user mentions uv, uvx, Python package management, virtual environments, pyproject.toml, lockfiles, uv lock, uv sync, uv run, uv add, uv pip, Python version management, pip replacement, pipx replacement, poetry replacement, pyenv replacement, or any Python packaging/project workflow.
license: MIT OR Apache-2.0
compatibility: Requires uv 0.12.0 installed. Supports macOS, Linux, Windows. Python 3.7+ source code.
metadata:
  tags:
    - python
    - packaging
    - dependency-management
    - virtual-environment
---

# uv 0.12.0

## Overview

uv is an extremely fast Python package and project manager written in Rust. It provides a unified tool to replace `pip`, `pip-tools`, `pipx`, `poetry`, `pyenv`, `twine`, and `virtualenv`, running 10-100x faster than `pip`.

uv operates at three abstraction levels:

1. **Project interface** — full project lifecycle: `uv init`, `uv add`, `uv remove`, `uv lock`, `uv sync`, `uv run`, `uv build`, `uv publish`
2. **Tool interface** — run and install CLI tools from Python packages: `uvx` (alias for `uv tool run`), `uv tool install`
3. **Pip interface** — drop-in replacement for pip/pip-tools/virtualenv: `uv pip install`, `uv pip compile`, `uv venv`

uv also manages Python installations directly (`uv python install`) and provides a universal cross-platform lockfile (`uv.lock`).

## Usage

### Project workflow

```bash
uv init example                   # create new project (packaged, with src/ layout and uv_build backend)
uv init --no-package example      # create unpackaged project (main.py, no build system)
cd example
uv add requests                   # add dependency, update lockfile + environment
uv add 'requests==2.31.0'        # add with version constraint
uv add git+https://github.com/psf/requests  # add git dependency
uv remove requests                # remove dependency
uv lock                           # resolve and write uv.lock
uv lock --upgrade-package requests  # upgrade a specific package
uv sync                           # install environment from lockfile
uv run python script.py           # run in project environment (auto lock+sync)
uv run -- flask run -p 3000       # run a command
uv build                          # build sdist + wheel into dist/
uv publish                        # publish to PyPI (needs UV_PUBLISH_TOKEN)
```

### Scripts

```bash
uv run example.py                 # run script (uses project deps if in a project)
uv run --no-project example.py    # run script without project deps
uv run --with rich example.py     # run with one-off dependency
uv add --script example.py requests  # add inline metadata to script
uv init --script example.py --python 3.12  # create script with inline metadata
```

### Tools (uvx)

```bash
uvx ruff check                    # run tool in ephemeral environment
uvx ruff@0.3.0 check              # pin tool version
uvx --from httpie http            # command name differs from package
uv tool install ruff              # install tool persistently
uv tool upgrade ruff              # upgrade installed tool
uv tool list                      # list installed tools
```

### Python versions

```bash
uv python install                 # install latest Python
uv python install 3.12 3.13      # install specific versions
uv python install pypy@3.10      # install alternative implementation
uv python list                    # list available/installed versions
uv python pin 3.11                # write .python-version file
uv venv --python 3.12             # create venv with specific Python
```

### Pip interface

```bash
uv venv                           # create virtual environment
uv pip install requests           # install into active or --python env
uv pip install -r requirements.txt  # install from requirements file
uv pip compile requirements.in    # compile + resolve dependencies
uv pip compile requirements.in --universal -o requirements.txt
uv pip sync requirements.txt      # exact sync (removes extraneous packages)
uv pip freeze                     # list installed packages
```

### Cache

```bash
uv cache clean                    # clear entire cache
uv cache clean requests           # clear cache for specific package
uv sync --refresh                 # revalidate all cached data
uv sync --refresh-package ruff    # revalidate single package
```

## Gotchas

- **`uv init` now creates packaged projects by default.** Since 0.12.0, `uv init` creates a `src/` layout with `uv_build` backend and `[project.scripts]` entry. Use `uv init --no-package` for the previous unpackaged layout with `main.py`. Existing projects are unaffected.
- **`uv run` auto-locks and auto-syncs.** Every `uv run` invocation checks the lockfile against `pyproject.toml` and syncs the environment. Use `--locked` to fail if the lockfile is stale, `--frozen` to skip the check entirely, `--no-sync` to skip environment sync.
- **Script-relative project discovery.** `uv run other-project/script.py` now discovers the project from the script's directory, not the current directory. Use `uv run --project . other-project/script.py` to force current-directory discovery.
- **`uvx` is isolated from the project.** Running `uvx pytest` does not see your project's dependencies or install your project. Use `uv run pytest` instead when the tool needs access to the project. Exception: flat-layout projects (no `src/`) work fine with `uvx`.
- **`uv sync` removes extraneous packages by default.** Running `uv sync` performs exact syncing — packages not in the lockfile are removed. Use `uv sync --inexact` to retain extra packages.
- **`uv pip` does not manage lockfiles.** The `uv pip` interface works directly with the virtual environment. It does not create or update `uv.lock`. Use the project interface (`uv add`, `uv lock`, `uv sync`) for lockfile management.
- **Build system is required for editable installs.** Projects without a `[build-system]` in `pyproject.toml` are not installed into the environment. They can still declare dependencies, but the project itself won't be importable.
- **`--with` adds transient dependencies.** `uv run --with rich` installs `rich` only for that invocation. It is not added to `pyproject.toml` or the lockfile.
- **`uv tool install` places executables on PATH.** Installed tools are available globally without `uv tool run`. The path is added by the standalone installer; pip-installed uv may need manual PATH setup.
- **`uv.lock` is uv-specific.** The lockfile format is not compatible with other tools. Export to `pylock.toml` (PEP 751) with `uv export -o pylock.toml` for interoperability.
- **Workspace members share a lockfile.** In workspaces, `uv lock` resolves all members at once. Use `uv run --package member-name` to run commands in a specific member.
- **`uv python install` uses Astral's standalone builds.** Python does not publish official binaries. uv uses the `python-build-standalone` project. Use `uv python install --default` to also create `python`/`python3` symlinks.
- **`uv venv --clear` now requires `--force` for non-venv directories.** Since 0.12.0, clearing a directory that is not a virtual environment requires explicit `--force`.
- **Pre-release resolution prefers stable first.** uv tries stable candidates before falling back to pre-releases. Use `--prerelease disallow` to reject all pre-releases, `--prerelease allow` to consider them without preferring stable.
- **`--require-hashes` is now enforced.** In `uv pip install/sync`, the `--require-hashes` directive in `requirements.txt` now enables strict hash checking. MD5-only hashes are rejected; at least one secure hash (SHA-256+) is required.
- **`uv add --script` writes inline metadata.** Dependencies declared via `uv add --script` are embedded in the script file itself as PEP 723 inline metadata blocks, not in a separate `pyproject.toml`.

## References

- [01-projects](references/01-projects.md) — Project creation, pyproject.toml, dependencies, lockfile, sync, run
- [02-scripts](references/02-scripts.md) — Inline metadata, --with, script discovery, stdin execution
- [03-tools](references/03-tools.md) — uvx, tool install/upgrade/list/uninstall, --from, version pinning
- [04-python](references/04-python.md) — Python installation, pinning, discovery, implementations, PATH
- [05-pip-interface](references/05-pip-interface.md) — uv pip install/compile/sync/freeze, uv venv, compatibility
- [06-workspaces](references/06-workspaces.md) — Workspace setup, members, shared sources, --package
- [07-build-publish](references/07-build-publish.md) — uv build, uv publish, distributions, PyPI
- [08-configuration](references/08-configuration.md) — tool.uv settings, indexes, cache, environment variables

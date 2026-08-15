# Projects — pyproject.toml, build systems, dependencies, packaging

## Project layout

`uv init` creates:

```
my-project/
├── .git/
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
└── src/
    └── my_project/
        └── __init__.py
```

On first `uv run`/`uv sync`/`uv lock`, uv creates `.venv/` and `uv.lock`.

### `uv init` options

```bash
uv init my-project                              # src layout (default)
uv init --no-package                            # flat layout, no src/ directory
uv init --build-backend setuptools              # use setuptools instead of uv_build
uv init --script example.py                     # create a script with inline metadata
uv init --python 3.12                           # set Python version
```

For flat layout, source files go directly in the project root alongside `pyproject.toml`.

## pyproject.toml structure

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "A project"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "requests>=2.28",
    "rich",
]

[project.optional-dependencies]
dev = ["pytest", "ruff"]
network = ["httpx"]

[project.scripts]
my-cli = "my_project:main"

[dependency-groups]
dev = ["pytest >=8.1.1,<9"]
lint = ["ruff"]

[build-system]
requires = ["uv_build>=0.12.1,<0.13"]
build-backend = "uv_build"
```

## Dependency fields

| Field | Purpose | Published? |
|---|---|---|
| `project.dependencies` | Required runtime deps | Yes |
| `project.optional-dependencies` | Optional extras | Yes |
| `dependency-groups` | Local dev deps (PEP 735) | No |
| `tool.uv.sources` | Alternative sources (git, path, workspace) | No (uv-only) |

### Adding dependencies

```bash
uv add requests                                     # main dependency
uv add 'requests>=2.28'                             # with constraint
uv add --dev pytest                                 # dev group
uv add --group lint ruff                            # named group
uv add --optional network httpx                     # optional extra
uv add --editable ../local-package                  # editable path dep
uv add git+https://github.com/psf/requests          # git dependency
uv add git+https://github.com/psf/requests --tag v2.31.0  # git + tag
uv add git+https://github.com/psf/requests --branch main  # git + branch
uv add git+https://github.com/psf/requests --rev abc123   # git + commit
uv add "jax; sys_platform == 'linux'"               # platform-specific
uv add -r requirements.txt                          # import from requirements file
```

### Dependency sources in pyproject.toml

```toml
[tool.uv.sources]
# Git
httpx = { git = "https://github.com/encode/httpx", tag = "0.27.0" }
httpx = { git = "https://github.com/encode/httpx", branch = "main" }
httpx = { git = "https://github.com/encode/httpx", rev = "326b943..." }
httpx = { git = "https://github.com/encode/httpx", subdirectory = "libs/httpx" }
httpx = { git = "https://github.com/encode/httpx", lfs = true }

# Path
foo = { path = "./packages/foo" }
bar = { path = "../projects/bar", editable = true }

# URL
httpx = { url = "https://files.pythonhosted.org/.../httpx-0.27.0.tar.gz" }

# Index (pin to specific index)
torch = { index = "pytorch" }

# Workspace
bird-feeder = { workspace = true }
foo = { workspace = "../other-workspace" }

# Platform-specific sources
httpx = { git = "https://...", marker = "sys_platform == 'darwin'" }

# Multiple sources
torch = [
  { index = "torch-cpu", marker = "platform_system == 'Darwin'" },
  { index = "torch-gpu", marker = "platform_system == 'Linux'" },
]
```

Disable sources with `uv lock --no-sources` or `uv build --no-sources`.

## Dependency groups

```toml
[dependency-groups]
dev = ["pytest"]
lint = ["ruff"]

# Nested groups
dev = [
  { include-group = "lint" },
  { include-group = "test" },
]
test = ["pytest"]
```

```bash
uv sync --all-groups                                # include all groups
uv sync --no-default-groups                         # exclude default groups
uv sync --group lint                                # include specific group
uv sync --only-group lint                           # only this group (no project)
uv sync --no-group lint                             # exclude specific group
uv sync --no-dev                                    # shortcut for --no-group dev
uv sync --only-dev                                  # dev only, no project
```

Default groups can be configured:

```toml
[tool.uv]
default-groups = ["dev", "lint"]
# or
default-groups = "all"
```

Dependency groups can have their own `requires-python`:

```toml
[tool.uv.dependency-groups]
dev = { requires-python = ">=3.12" }
```

## Build systems

A `[build-system]` table tells uv whether to build and install the project:

```toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"
```

Without a build system, uv installs only dependencies, not the project itself. Override with `tool.uv.package`:

```toml
[tool.uv]
package = true    # force build even without build-system
# or
package = false   # skip build even with build-system
```

### Build backends

- `uv_build` — uv's own build backend (default for `uv init`)
- `setuptools.build_meta` — setuptools
- `hatchling.build` — Hatch
- `flit_core.buildapi` — Flit
- `pdm.backend` — PDM

## Editable installations

By default, workspace members and projects with build systems are installed in editable mode — source changes reflect immediately without re-sync.

```bash
uv sync --no-editable                               # non-editable install
uv add --editable ./path/foo                        # add as editable
uv add --no-editable ./path/foo                     # add as non-editable
```

## Entry points

```toml
[project.scripts]
my-cli = "my_package:main"                          # CLI entry point

[project.gui-scripts]
my-gui = "my_package:app"                           # GUI entry point (Windows-only difference)

[project.entry-points.'my.plugins']
plugin-a = "my_plugin_a"                            # plugin discovery
```

## Virtual dependencies

A path dependency whose own dependencies are installed but not the package itself:

```toml
[tool.uv.sources]
bar = { path = "../projects/bar", package = false }
```

## Exporting

```bash
uv export                                         # default: requirements.txt format
uv export --format requirements.txt               # explicit requirements.txt
uv export --format pylock.toml                    # PEP 751
uv export --format cyclonedx1.5                   # CycloneDX SBOM
uv export --no-dev                                # exclude dev deps
uv export --extra foo                             # include extra
uv export --no-hashes                             # omit hashes
```

## Conflicting dependencies

Declare incompatible groups:

```toml
[tool.uv]
conflicts = [
  [{ extra = "extra1" }, { extra = "extra2" }],
  [{ group = "group1" }, { group = "group2" }],
]
```

## Limited resolution environments

Restrict which platforms the lockfile covers:

```toml
[tool.uv]
environments = [
  "sys_platform == 'darwin'",
  "sys_platform == 'linux'",
]

required-environments = [
  "sys_platform == 'darwin' and platform_machine == 'x86_64'",
]
```

## Project environment path

Override `.venv` location:

```bash
UV_PROJECT_ENVIRONMENT=/custom/path uv sync
```

Use `--active` to respect `VIRTUAL_ENV`, `--no-active` to silence warnings.

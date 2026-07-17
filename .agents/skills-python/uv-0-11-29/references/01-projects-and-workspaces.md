# Projects and Workspaces

## Project Layout

A uv-managed project has the following structure:

```
my-project/
├── .git/
├── .gitignore
├── .python-version        # default Python version (e.g., "3.12")
├── .venv/                  # project virtual environment (created by uv)
├── README.md
├── main.py                 # entry point
├── pyproject.toml          # project metadata + dependencies
└── uv.lock                 # resolved dependency lockfile
```

### pyproject.toml

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "A Python project"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "requests>=2.31",
    "rich",
]

[project.optional-dependencies]
dev = ["pytest", "ruff"]

[dependency-groups]
lint = ["ruff>=0.8"]
test = ["pytest>=8"]

[build-system]
requires = ["uv_build>=0.11.29,<0.12"]
build-backend = "uv_build"

[tool.uv]
cache-keys = [{ file = "pyproject.toml" }, { git = { commit = true } }]
```

### .python-version

Contains the default Python version. uv searches from working directory upward.

```
3.12
```

Create with: `uv python pin 3.12`

### uv.lock

Cross-platform, human-readable TOML lockfile. Managed by uv — do not edit manually. Contains exact resolved versions with platform markers. Check into version control.

## Project Commands

### Initialization

```bash
uv init my-project                    # new project in subdirectory
uv init                               # initialize current directory
uv init --lib my-lib                  # library project (src layout)
uv init --package my-pkg              # packaged project (default build backend)
uv init --build-backend hatch         # use hatch as build backend
uv init --build-backend setuptools    # use setuptools
uv init --script example.py           # create script with inline metadata
```

### Dependency Management

```bash
uv add requests                       # add to dependencies
uv add 'flask>=3.0,<4.0'             # version constraints
uv add --dev pytest                   # add to dev dependencies
uv add --group lint ruff              # add to dependency group
uv add --optional dev 'pytest>=8'    # add to optional-dependencies
uv add git+https://github.com/...    # git dependency
uv add --editable ./local-pkg        # local editable
uv add --index pytorch=https://...   # add with custom index
uv remove requests                    # remove dependency
uv tree                               # show dependency tree
uv tree --format json                 # JSON output (0.11.29)
```

### Resolution and Sync

```bash
uv lock                               # resolve dependencies, write uv.lock
uv lock --upgrade                     # upgrade all packages
uv lock --upgrade-package requests    # upgrade one package
uv lock --python 3.11                 # resolve for specific Python
uv lock --python 3.12 --python 3.13   # multi-version lockfile

uv sync                               # install from lockfile into .venv
uv sync --extra dev                   # include optional group
uv sync --group lint                  # include dependency group
uv sync --frozen                      # skip lockfile check (CI)
uv sync --no-editable                 # install project non-editably
uv sync --reinstall                   # force reinstall all
uv sync --reinstall-package flask     # reinstall specific package
```

### Running Commands

```bash
uv run python main.py                 # run in project environment
uv run -- flask run -p 3000          # run CLI tool
uv run --package bird-feeder cmd      # run in workspace member
uv run --python 3.11 python main.py   # override Python version
uv run --no-project script.py         # skip project context
uv run --with httpx script.py         # add ephemeral dependency
uv run -- extra-arg cmd               # pass args after --
```

## Workspaces

A workspace groups multiple packages under shared dependency management.

### Creating a Workspace

```toml title="pyproject.toml"
[project]
name = "workspace-root"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["bird-feeder", "tqdm>=4,<5"]

[tool.uv.sources]
bird-feeder = { workspace = true }

[tool.uv.workspace]
members = ["packages/*"]
exclude = ["packages/seeds"]
```

### Workspace Commands

```bash
uv init                               # creates workspace root
uv init packages/bird-feeder          # adds member to workspace
uv lock                               # resolves entire workspace
uv sync                               # syncs workspace root
uv sync --package bird-feeder         # sync specific member
uv run --package bird-feeder cmd      # run in specific member
```

### Workspace Sources

Workspace members reference each other via `tool.uv.sources`:

```toml
[tool.uv.sources]
bird-feeder = { workspace = true }    # resolve from workspace
tqdm = { git = "https://..." }       # workspace-wide override
```

Sources defined in the workspace root apply to all members unless overridden in a member's own `tool.uv.sources`.

### Path Dependencies (Alternative to Workspaces)

For packages with conflicting requirements or separate environments:

```toml
[tool.uv.sources]
bird-feeder = { path = "packages/bird-feeder" }
```

This allows each package its own virtual environment and independent resolution.

## Build Systems

### uv_build (recommended)

```toml
[build-system]
requires = ["uv_build>=0.11.29,<0.12"]
build-backend = "uv_build"
```

### hatchling

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### setuptools

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

### No Build System

Projects without `[build-system]` are treated as non-packaged. uv installs dependencies but does not build/install the project itself. Use `tool.uv.package = true` to force packaging, or `tool.uv.package = false` to skip it even with a build system.

## Entry Points

### CLI Commands

```toml
[project.scripts]
my-cli = "my_package.cli:main"
```

Run with: `uv run my-cli`

### GUI Scripts (Windows only difference)

```toml
[project.gui-scripts]
my-gui = "my_package.gui:app"
```

### Plugin Entry Points

```toml
[project.entry-points."my.plugins"]
plugin-a = "my_plugin_a"
```

## Publishing

```bash
uv build                              # build sdist + wheel to dist/
uv build --sdist                      # source distribution only
uv build --wheel                      # wheel only
uv publish                            # publish to PyPI
uv publish --token $UV_PUBLISH_TOKEN  # with token
uv publish --index-url https://...    # custom registry
```

Set `UV_PUBLISH_TOKEN` environment variable or use `--token` flag.

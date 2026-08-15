# Projects

## Creating Projects

### Packaged project (default since 0.12.0)

```bash
uv init example
```

Creates a `src/` layout with `uv_build` backend:

```
example/
├── .git/
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
└── src/
    └── example/
        └── __init__.py
```

```toml title="pyproject.toml"
[project]
name = "example"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.X"
dependencies = []

[project.scripts]
example = "example:main"

[build-system]
requires = ["uv_build>=0.12.0,<0.13"]
build-backend = "uv_build"
```

The project is importable, installable as a dependency, and runnable as a command (`uv run example`).

### Unpackaged project

```bash
uv init --no-package example
```

Creates a flat layout without a build system:

```
example/
├── .python-version
├── main.py
└── pyproject.toml
```

The project can declare dependencies but is not installed into its environment. Use `uv run python main.py` to execute.

### Initializing in current directory

```bash
mkdir example && cd example
uv init                          # uses directory name as project name
uv init --name my-app            # override project name
```

## pyproject.toml

The `pyproject.toml` is the project's manifest. uv requires this file to identify the project root.

### Project table

```toml
[project]
name = "my-app"
version = "0.1.0"
description = "A description"
readme = "README.md"
license = "MIT"
authors = [{ name = "Author", email = "author@example.com" }]
requires-python = ">=3.12"
dependencies = ["requests>=2.28.0"]

[project.optional-dependencies]
dev = ["pytest", "ruff"]
docs = ["mkdocs"]

[project.scripts]
my-app = "my_app:main"

[project.gui-scripts]
my-gui = "my_app:gui_main"
```

### uv configuration

```toml
[tool.uv]
managed = false                        # disable automatic lock/sync
package = false                        # treat as non-package (scripts only)
python-downloads = "automatic"         # auto-download Python versions
required-version = ">=0.12.0"          # minimum uv version
override-dependencies = ["pkg==1.0"]   # force versions across resolution
constraint-dependencies = ["pkg>=1.0"] # constrain without forcing

[tool.uv.sources]
bird-feeder = { workspace = true }     # resolve from workspace
custom-pkg  = { git = "https://..." }  # resolve from git

[tool.uv.workspace]
members = ["packages/*"]
exclude = ["packages/internal"]
```

## Managing Dependencies

### Adding dependencies

```bash
uv add requests                        # latest compatible version
uv add 'requests>=2.28.0,<3.0.0'      # version range
uv add 'requests==2.31.0'             # exact version
uv add git+https://github.com/psf/requests  # git dependency
uv add ./local-package                 # local directory
uv add requests --dev                  # dev dependency (tool.uv.dev-dependencies)
uv add requests --optional dev         # optional dependency group
uv add -r requirements.txt             # add all from requirements file
uv add --upgrade requests              # upgrade to latest compatible
```

### Removing dependencies

```bash
uv remove requests
uv remove requests --dev
```

### Upgrading

```bash
uv lock --upgrade                      # upgrade all to latest compatible
uv lock --upgrade-package requests     # upgrade specific package
uv lock --upgrade-group dev            # upgrade dev dependency group
```

## Lockfile (`uv.lock`)

The lockfile captures exact resolved versions across all Python markers (OS, architecture, version). It is cross-platform and should be checked into version control.

### Lockfile lifecycle

```bash
uv lock                                # create/update lockfile
uv lock --check                        # verify lockfile is up-to-date
uv lock --diff                         # show changes
```

### Auto-lock behavior

`uv run` and `uv sync` automatically lock before running. Disable with:

```bash
uv run --locked   # fail if lockfile is stale (CI-friendly)
uv run --frozen   # skip lock check entirely
```

### Exporting

```bash
uv export -o requirements.txt          # export as requirements.txt
uv export -o pylock.toml               # export as PEP 751 pylock.toml
uv export --dev                        # include dev dependencies
uv export --no-hashes                  # omit hashes from export
```

## Syncing

```bash
uv sync                                # sync environment from lockfile
uv sync --frozen                       # skip lock check
uv sync --inexact                      # don't remove extraneous packages
uv sync --no-editable                  # install non-editable
uv sync --extra dev                    # include optional dependency group
uv sync --python 3.12                  # sync for specific Python
```

### Editable installs

Workspace members and the root project are installed as editable packages by default. Changes to source code are immediately reflected without re-syncing.

## Running Commands

```bash
uv run python script.py                # run script in project environment
uv run -- flask run -p 3000            # run arbitrary command
uv run --with httpie http example.com  # run with transient dependency
uv run --no-project python script.py   # skip project installation
uv run --package member-name pytest    # run in specific workspace member
```

### Flags controlling lock/sync

| Flag | Lock behavior | Sync behavior |
|------|--------------|---------------|
| (default) | Auto-lock if stale | Auto-sync |
| `--locked` | Error if stale | Auto-sync |
| `--frozen` | Skip check | Auto-sync |
| `--no-sync` | Auto-lock if stale | Skip sync |
| `--isolated` | Use temporary environment | N/A |

## Python version pinning

```bash
uv python pin 3.12                     # write .python-version
uv python pin 3.12.6                   # pin specific patch
cat .python-version                    # read pinned version
```

The `.python-version` file controls which Python uv uses for the project environment. It follows `pyenv` format and is respected by other tools.

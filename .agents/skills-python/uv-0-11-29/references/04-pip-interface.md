# Pip Interface

The pip interface provides drop-in replacements for `pip`, `pip-tools`, and `virtualenv`. Use for legacy workflows or when the high-level project commands don't provide enough control.

## Virtual Environments

```bash
uv venv                               # create .venv with default Python
uv venv --python 3.12                 # specific version
uv venv --python 3.12t                # free-threaded
uv venv -p /opt/bin/python3.11        # specific interpreter path
uv venv --seed                        # include pip in environment
```

Activate with:

```bash
source .venv/bin/activate             # macOS/Linux
.venv\Scripts\activate                # Windows
```

## Package Management

### Installing

```bash
uv pip install flask                   # basic install
uv pip install 'ruff>=0.8'             # version constraint
uv pip install 'ruff==0.8.0'          # exact version
uv pip install flask ruff              # multiple packages
uv pip install "flask[dotenv]"         # with extras
uv pip install -e .                    # editable install
uv pip install -e "ruff @ ./ruff"     # editable from path
uv pip install -r requirements.txt     # from file
uv pip install -r pyproject.toml       # from pyproject.toml
uv pip install --extra foo             # with optional deps
uv pip install --all-extras            # all optional deps
uv pip install --group foo             # dependency group
uv pip install --project some/path/ --group foo
uv pip install "git+https://github.com/psf/requests"
uv pip install "git+https://github.com/psf/requests@main"
uv pip install "git+https://github.com/psf/requests@v2.31.0"
uv pip install "git+https://github.com/psf/requests@1fadefa67"
```

### Uninstalling

```bash
uv pip uninstall flask                 # single package
uv pip uninstall flask ruff            # multiple packages
```

### Listing and Inspecting

```bash
uv pip list                            # installed packages
uv pip freeze                          # pip-compatible freeze
uv pip tree                            # dependency tree
uv pip tree --format json              # JSON output
uv pip show flask                      # package details
uv pip check                           # compatibility check
```

## Locking (pip-tools replacement)

### Compiling Requirements

```bash
uv pip compile requirements.in -o requirements.txt
uv pip compile pyproject.toml -o requirements.txt
uv pip compile setup.py -o requirements.txt
uv pip compile - -o requirements.txt   # from stdin
echo "ruff" | uv pip compile - -o requirements.txt
```

### Extras and Groups

```bash
uv pip compile pyproject.toml --extra foo -o requirements.txt
uv pip compile pyproject.toml --all-extras -o requirements.txt
uv pip compile --group dev -o dev-requirements.txt
uv pip compile --project some/path/ --group foo -o requirements.txt
uv pip compile --group some/path/pyproject.toml:foo -o requirements.txt
```

### Upgrading

```bash
uv pip compile requirements.in -o requirements.txt --upgrade
uv pip compile requirements.in -o requirements.txt --upgrade-package ruff
```

### Constraints

```bash
uv pip compile requirements.in --constraint constraints.txt -o requirements.txt
```

constraints.txt:

```
pydantic<2.0
numpy>=1.24
```

### Build Constraints

```bash
uv pip compile requirements.in --build-constraint build-constraints.txt
```

build-constraints.txt:

```
setuptools==75.0.0
wheel>=0.42
```

### Overrides

```bash
uv pip compile requirements.in --override overrides.txt -o requirements.txt
```

overrides.txt:

```
c>=2.0
```

Overrides force a specific version regardless of what packages require. Use when constraints are incompatible.

## Syncing

```bash
uv pip sync requirements.txt           # exact environment match
uv pip sync pylock.toml               # PEP 751 pylock format
```

`uv pip sync` removes packages not in the requirements file. `uv pip install` does not.

## Compatibility with pip

uv's pip interface covers common workflows but may differ in edge cases. Key differences:

- `uv pip compile` output format matches `pip-tools` but includes additional metadata
- `uv pip install` uses uv's resolver, not pip's
- `--no-build-isolation` is supported but uv prefers build isolation
- `--find-links` maps to flat indexes via `[[tool.uv.index]]` with `format = "flat"`
- `--index-url` maps to `--default-index`
- `--extra-index-url` maps to `--index`

## Environment Discovery

uv discovers the active virtual environment via:

1. `UV_PROJECT_ENVIRONMENT` environment variable
2. `.venv` in the current directory or parent directories
3. `VIRTUAL_ENV` environment variable (with `--active` flag)
4. System Python (with `--system` flag)

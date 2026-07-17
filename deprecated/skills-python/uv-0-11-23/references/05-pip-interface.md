# pip Interface

uv provides a drop-in replacement for `pip`, `pip-tools`, and `virtualenv`. Commands work directly with virtual environments without automatic management.

## Virtual Environments

```bash
# Create .venv
uv venv

# Custom name/path
uv venv my-env
uv venv /path/to/venv

# Specific Python
uv venv --python 3.12

# Clear existing environment
uv venv --clear

# Without seed packages (pip, setuptools, wheel)
uv venv --no-seed
```

Activate the environment before using `uv pip` commands:
```bash
source .venv/bin/activate    # bash/zsh
.venv\Scripts\activate       # Windows
```

## Installing Packages

```bash
# Basic install
uv pip install flask

# Multiple packages
uv pip install flask requests ruff

# Version constraints
uv pip install 'flask>=3.0' 'requests<3'

# Extras
uv pip install 'flask[dotenv]'

# From git
uv pip install git+https://github.com/palletts/flask
uv pip install 'flask @ git+https://github.com/palletts/flask@main'

# Editable install
uv pip install -e .
uv pip install -e './packages/my-lib'

# From requirements.txt
uv pip install -r requirements.txt

# From pyproject.toml
uv pip install -r pyproject.toml
uv pip install -r pyproject.toml --extra dev

# Dependency groups
uv pip install --group test
```

## Uninstalling Packages

```bash
uv pip uninstall flask
uv pip uninstall flask requests ruff
```

## Compiling Requirements (pip-compile replacement)

```bash
# Compile requirements.in to requirements.txt
uv pip compile requirements.in -o requirements.txt

# From pyproject.toml
uv pip compile pyproject.toml -o requirements.txt

# Multiple input files
uv pip compile req1.in req2.in -o requirements.txt

# With extras
uv pip compile pyproject.toml --extra dev -o requirements.txt

# Universal (all platforms)
uv pip compile requirements.in --universal -o requirements.txt

# Specific platform
uv pip compile requirements.in \
  --python-platform linux \
  --python-version 3.11 \
  -o requirements-linux.txt

# Upgrade all
uv pip compile requirements.in --upgrade -o requirements.txt

# Upgrade specific package
uv pip compile requirements.in --upgrade-package flask -o requirements.txt

# From stdin
echo "flask" | uv pip compile - -o requirements.txt
```

## Syncing Environments (exact match)

`uv pip sync` makes the environment exactly match the requirements file — installing missing packages and removing extras.

```bash
uv pip sync requirements.txt
```

This differs from `uv pip install` which does not remove unlisted packages.

## Constraints and Overrides

### Constraints

Limit versions without forcing installation:

```python title="constraints.txt"
pydantic<2.0
numpy>=1.24
```

```bash
uv pip compile requirements.in --constraint constraints.txt -o requirements.txt
uv pip install -r requirements.txt --constraint constraints.txt
```

### Overrides

Force specific versions regardless of package requirements:

```python title="overrides.txt"
urllib3>=2.0
```

```bash
uv pip compile requirements.in --override overrides.txt -o requirements.txt
```

Overrides are absolute — they replace all version requirements for the package. Use when transitive dependencies conflict.

## Build Constraints

Constraints applied only during build-time dependency resolution:

```python title="build-constraints.txt"
setuptools==75.0.0
```

```bash
uv pip compile requirements.in --build-constraint build-constraints.txt -o requirements.txt
```

## System Install

```bash
# Install into system Python (CI/containers)
uv pip install --system flask

# Compile without virtual environment
uv pip compile --system requirements.in -o requirements.txt
```

The `--system` flag skips virtualenv discovery and installs directly into the target Python. Use in containers and CI where virtual environments add overhead.

## Inspection

```bash
# List installed packages
uv pip list

# Show package info
uv pip show flask

# List outdated packages
uv pip list --outdated
```

## Key Differences from pip

- uv requires a virtual environment by default (use `--system` to opt out)
- `uv pip compile` is faster than `pip-compile` and supports universal resolution
- No dependency on pip — uv resolves independently
- Supports constraints, overrides, and build constraints natively

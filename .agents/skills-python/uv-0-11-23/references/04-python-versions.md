# Python Versions

uv manages Python installations, automatically downloading versions as needed. It supports CPython and PyPy on macOS, Linux, and Windows.

## Requesting Python Versions

The `--python` flag accepts multiple formats:

```bash
# Version number
uv venv --python 3.12
uv venv --python 3.12.3

# Implementation
uv venv --python cpython
uv venv --python pypy

# Implementation with version
uv venv --python cpython@3.12
uv venv --python pypy@3.10

# Version specifier
uv venv --python '>=3.10,<3.13'

# Full distribution name
uv venv --python cpython-3.12.3-macos-aarch64-none

# Path to interpreter
uv venv --python /usr/bin/python3.12

# Freethreaded Python 3.13+
uv venv --python 3.13t
uv venv --python '3.13+freethreaded'
```

## Installing Python

```bash
# Install latest Python
uv python install

# Install specific version
uv python install 3.12

# Install multiple versions
uv python install 3.11 3.12 3.13

# Install PyPy
uv python install pypy
uv python install pypy@3.10

# Reinstall (updates to latest patch)
uv python install --reinstall
```

uv uses standalone distributions from the Astral `python-build-standalone` project. Available versions are frozen per uv release — upgrade uv for newer Python versions.

## Python Executables

By default, `uv python install` creates versioned executables (`python3.12`) in PATH.

```bash
# Install unversioned python/python3 (experimental)
uv python install --default

# Update shell to include uv bin directory
uv python update-shell
```

## Pinning Python Versions

```bash
# Pin for current directory
uv python pin 3.12
# Creates .python-version file

# Pin globally
uv python pin --global 3.12
```

uv searches for `.python-version` in the working directory and parent directories. Use any request format from above.

## Listing Python Versions

```bash
# List all (installed and available)
uv python list

# List only installed
uv python list --only-installed

# List only managed (uv-installed)
uv python list --only-managed

# List only system
uv python list --only-system
```

Output shows installed versions marked with `*` and indicates if executables are on PATH.

## Upgrading Python

```bash
# Upgrade specific version to latest patch
uv python upgrade 3.12

# Upgrade all managed versions
uv python upgrade
```

## Automatic Downloads

uv downloads Python on-demand when needed. For example, `uv venv` with no Python installed will download the latest version automatically.

Disable automatic downloads:
```bash
# Environment variable
UV_PYTHON_DOWNLOADS=never uv venv

# Force system Python only
uv venv --no-managed-python
```

## Python Discovery Order

uv searches for Python in this order:
1. Activated virtual environment (`VIRTUAL_ENV`)
2. Activated Conda environment (`CONDA_PREFIX`)
3. `.venv` in current or parent directory
4. `.python-version` file
5. Managed Python installations
6. System Python

Use `--system` to skip virtual environments and use system Python directly (CI/containers).

## Storage Locations

- **Python installations**: Platform-specific cache directory
- **Executables**: `~/.local/bin` (Unix), `%LOCALAPPDATA%\uv\bin` (Windows)
- **`.python-version`**: Project root or user config directory

Check with:
```bash
uv python dir
```

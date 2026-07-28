# Python Versions

## Installing Python

```bash
uv python install                    # install latest Python
uv python install 3.12               # install specific minor version
uv python install 3.12.6             # install specific patch version
uv python install 3.11 3.12 3.13    # install multiple versions
uv python install pypy@3.10          # install PyPy
uv python install --reinstall        # reinstall all managed versions
uv python install 3.12 --upgrade     # upgrade to latest patch
```

uv uses the Astral `python-build-standalone` project for Python distributions. Python does not publish official distributable binaries.

### Default executables

By default, uv only installs versioned executables (`python3.12`, `python3.13`). To also create `python` and `python3`:

```bash
uv python install --default          # makes this version the default python
```

## Listing Python versions

```bash
uv python list                       # all available versions
uv python list --only-installed      # only installed versions
uv python list 3.12                  # filter by version
```

Output shows installed versions with markers:

```
cpython-3.12.6-linux-x86_64-gnu     # installed
cpython-3.12.7-linux-x86_64-gnu     # installed (latest)
cpython-3.13.0-linux-x86_64-gnu     # available
```

## Pinning Python versions

```bash
uv python pin 3.12                   # write .python-version
uv python pin 3.12.6                 # pin specific patch
```

The `.python-version` file follows `pyenv` format. It is respected by uv and compatible with pyenv. uv reads it when creating project environments.

## Automatic Python downloads

uv automatically downloads Python versions when needed:

```bash
uvx python@3.12 -c "print('hello')"  # downloads 3.12 if missing
uv venv --python 3.12                # downloads 3.12 if missing
```

Disable automatic downloads:

```toml
[tool.uv]
python-downloads = "manual"
```

Or via environment variable: `UV_PYTHON_DOWNLOADS = "never"`

## Using existing Python

uv detects system Python installations automatically. It searches:

1. Active virtual environment
2. `--python` flag or `.python-version` file
3. uv-managed Python installations
4. System Python (`python3`, `python`)
5. `PATH` search

### Requesting specific Python

```bash
uv run --python 3.12 python script.py
uv run --python pypy@3.10 python script.py
uv run --python /usr/bin/python3.11 python script.py
uv venv --python 3.12
```

## Python discovery order

uv resolves the Python interpreter in this priority:

1. `--python` CLI flag
2. Active virtual environment (VIRTUAL_ENV)
3. `.python-version` file (walks up from current directory)
4. Project's `requires-python` constraint
5. uv-managed installations
6. System Python

## Removing Python

```bash
uv python uninstall 3.12             # remove specific version
uv python uninstall 3.12.6           # remove specific patch
```

## Python distributions

uv supports these implementations:

- **CPython** — `3.12`, `3.12.6`, `cpython@3.12`
- **PyPy** — `pypy@3.10`, `pypy@3.9`
- **GraalPy** — `graalpy@24.1` (where available)

Platform-specific builds are selected automatically based on OS and architecture.

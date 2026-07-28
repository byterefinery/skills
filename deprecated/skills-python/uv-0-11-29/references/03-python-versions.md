# Python Versions

## Managed vs System Python

- **Managed Python** — installed by uv from standalone distributions. Stored in uv's Python directory.
- **System Python** — any Python not managed by uv (OS Python, pyenv, conda, etc.).

uv discovers system Python first, prefers managed Python by default. Automatic downloads fill gaps.

## Version Request Formats

```bash
uv venv --python 3                    # latest Python 3
uv venv --python 3.12                 # latest Python 3.12.x
uv venv --python 3.12.3               # exact version
uv venv --python '>=3.12,<3.13'       # version range
uv venv --python 3.13t                # free-threaded Python 3.13
uv venv --python 3.13+freethreaded    # explicit free-threaded
uv venv --python 3.12.0d              # debug build
uv venv --python cpython              # CPython implementation
uv venv --python cpython@3.12         # CPython 3.12
uv venv --python cpython3.12          # compact form
uv venv --python pypy@3.10            # PyPy
uv venv --python graalpy              # GraalPy
uv venv --python /opt/bin/python3     # specific path
uv venv --python mypython3            # executable name
uv venv --python /some/environment/   # install directory
```

## Installation Commands

```bash
uv python install                     # install latest Python
uv python install 3.12                # specific version
uv python install 3.11 3.12 3.13     # multiple versions
uv python install pypy                # PyPy
uv python install pypy@3.10          # PyPy with version
uv python install --reinstall         # reinstall all managed versions
uv python install --default           # also install python/python3 executables
uv python upgrade 3.12                # upgrade to latest patch
uv python upgrade                     # upgrade all managed versions
uv python uninstall 3.11              # remove managed version
```

### Python Executables

By default, `uv python install 3.12` installs `python3.12` into `~/.local/bin`. For `python` and `python3` executables, use `--default` (experimental).

```bash
uv python install 3.12 --default      # adds python + python3
uv python update-shell                # add to PATH if needed
```

uv only overwrites executables it manages. Use `--force` to override non-uv executables.

## Discovery Order

1. Managed Python installations in `UV_PYTHON_INSTALL_DIR`
2. `python`, `python3`, `python3.x` on PATH (macOS/Linux)
3. `python.exe` on PATH (Windows)
4. Windows registry and Microsoft Store interpreters
5. Virtual environment interpreter (when applicable)
6. Managed Python download (if automatic downloads enabled)

Managed Python: prefers newer versions. System Python: uses first compatible version.

## .python-version

```bash
uv python pin 3.12                    # write .python-version in current dir
uv python pin --global 3.12           # write global .python-version
```

uv searches from working directory upward, stopping at project/workspace boundaries. Disable with `--no-config`.

## Free-Threaded Python

Available for CPython 3.13+. Request with `3.13t` or `3.13+freethreaded`.

- Python 3.13: free-threaded not selected by default; must be explicit
- Python 3.14+: free-threaded allowed without explicit selection, but GIL-enabled preferred

Require GIL-enabled variant: `3.14+gil`

## Debug Builds

Request with `3.13d` or `3.13+debug`. Slower, not for general use. Debug symbols are not stripped (unlike standard managed builds).

## Automatic Downloads

Enabled by default. uv downloads Python versions on demand.

```bash
uv venv                               # downloads Python if none found
uvx python@3.12 -c "print('hi')"      # downloads Python 3.12
```

Disable with:

```bash
uv venv --no-python-downloads
```

Or in config:

```toml
[tool.uv]
python-downloads = "manual"           # only allow during uv python install
# python-downloads = "disabled"       # never download
```

## Python Preference

```bash
uv sync --managed-python              # only use managed Python
uv sync --no-managed-python           # only use system Python
```

Config options:

```toml
[tool.uv]
python-preference = "managed"         # default: prefer managed, allow system
python-preference = "only-managed"    # only managed, never system
python-preference = "system"          # prefer system, allow managed
python-preference = "only-system"     # only system, never managed
```

## Implementation Support

| Implementation | Long Name | Short Name |
|---|---|---|
| CPython | `cpython` | `cp` |
| PyPy | `pypy` | `pp` |
| GraalPy | `graalpy` | `gp` |
| Pyodide | `pyodide` | — |

## Viewing and Finding

```bash
uv python list                        # available + installed
uv python list 3.13                   # filter by version
uv python list pypy                   # filter by implementation
uv python list --all-versions         # show all patches
uv python list --all-platforms        # show other platforms
uv python list --only-installed       # installed only
uv python find                        # path to first available Python
uv python find '>=3.11'              # find matching Python
uv python find --system               # ignore virtual environments
```

## Transparent x86_64 Emulation

macOS (Rosetta 2) and Windows (WoA) support running x86_64 binaries on aarch64. Either uv binary can use either Python interpreter, but packages must match the Python interpreter's architecture.

## Windows Registry

Managed Python versions are registered with Windows registry per PEP 514:

```bash
uv python install 3.13.1
py -V:Astral/CPython3.13.1           # select via py launcher
```

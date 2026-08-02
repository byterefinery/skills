# Pip Interface

## Overview

The `uv pip` interface provides a drop-in replacement for `pip`, `pip-tools`, and `virtualenv`. It works directly with the virtual environment without managing lockfiles or project metadata.

Key difference: `uv pip` does not create or update `uv.lock`. Use the project interface (`uv add`, `uv lock`, `uv sync`) for lockfile-based workflows.

## Creating environments

```bash
uv venv                              # create .venv with default Python
uv venv --python 3.12                # create with specific Python
uv venv --python pypy@3.10           # create with PyPy
uv venv --seed                       # include pip, setuptools, wheel
uv venv /path/to/env                 # create at specific path
uv venv --clear                      # remove existing .venv first
uv venv --clear --force              # clear even if not a venv (0.12.0+)
```

## Installing packages

```bash
source .venv/bin/activate
uv pip install requests
uv pip install 'requests>=2.28.0'
uv pip install -r requirements.txt
uv pip install git+https://github.com/psf/requests
uv pip install ./local-package
uv pip install --upgrade requests
uv pip install --force-reinstall requests
```

### With constraints

```bash
uv pip install requests -c constraints.txt
uv pip install --constraint constraints.txt -r requirements.txt
```

### Hash checking

```bash
uv pip install --require-hashes -r requirements.txt
```

Since 0.12.0, `--require-hashes` in `requirements.txt` is enforced. MD5-only hashes are rejected; at least one secure hash (SHA-256+) is required per requirement.

## Compiling requirements

```bash
uv pip compile requirements.in -o requirements.txt
uv pip compile requirements.in --universal -o requirements.txt
uv pip compile requirements.in --python-version 3.12
uv pip compile requirements.in --python-platform linux
uv pip compile requirements.in --output-file pylock.toml  # PEP 751
```

### Universal compilation

`--universal` generates a cross-platform requirements file valid across all OS/architecture/Python version combinations.

## Syncing environments

```bash
uv pip sync requirements.txt         # exact sync (removes extras)
uv pip sync requirements.txt --python .venv/bin/python
uv pip install -r requirements.txt   # install without removing extras
```

`uv pip sync` performs exact syncing — packages not in the requirements file are removed. `uv pip install -r` adds packages without removing extras.

## Inspecting environments

```bash
uv pip freeze                        # list installed packages
uv pip list                          # detailed list
uv pip show requests                 # show package info
uv pip check                         # check for conflicts
```

## Upgrading

```bash
uv pip install --upgrade requests
uv pip install --upgrade -r requirements.txt
```

## Uninstalling

```bash
uv pip uninstall requests
uv pip uninstall -r requirements.txt
```

## Compatibility with pip

uv's pip interface matches common pip workflows but may differ in edge cases:

- `uv pip compile` supports `--universal`, `--no-strip-extras`, and other extensions beyond pip-tools
- Hash checking is stricter (MD5-only rejected in hash-checking mode since 0.12.0)
- `--require-hashes` directives in `requirements.txt` are now enforced (0.12.0+)
- `--cert` is supported for custom CA bundles (0.12.0+)

## Environment variables

| Variable | Description |
|----------|-------------|
| `VIRTUAL_ENV` | Target environment (auto-detected if activated) |
| `PIP_INDEX_URL` | Override package index |
| `PIP_EXTRA_INDEX_URL` | Additional indexes |
| `PIP_TRUSTED_HOST` | Trust specific hosts |

These are respected by `uv pip` commands for pip compatibility.

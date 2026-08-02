# Pip interface — pip-compatible commands

The `uv pip` namespace provides drop-in replacements for pip, pip-tools, and virtualenv. These commands operate directly on virtual environments, unlike the higher-level project commands which manage environments automatically.

## Package management

### Installing

```bash
uv pip install flask                                # single package
uv pip install flask ruff                           # multiple packages
uv pip install 'ruff>=0.2.0'                        # with constraint
uv pip install 'ruff==0.3.0'                        # exact version
uv pip install "flask[dotenv]"                      # with extras
uv pip install -r requirements.txt                  # from requirements file
uv pip install -r pyproject.toml                    # from pyproject.toml
uv pip install -r pyproject.toml --extra foo        # with extra
uv pip install -r pyproject.toml --all-extras       # all extras
uv pip install -e .                                 # editable install
uv pip install -e ./project/ruff                    # editable from path
uv pip install "git+https://github.com/..."         # from git
uv pip install "git+https://...@v0.2.0"             # from git + tag
uv pip install "git+https://...@main"               # from git + branch
uv pip install "git+https://...@1fadefa6"           # from git + commit
uv pip install "https://.../package-0.1.0.tar.gz"   # from URL
uv pip install --group foo                          # dependency group
uv pip install --project some/path/ --group foo     # group from specific project
```

### Uninstalling

```bash
uv pip uninstall flask
uv pip uninstall flask ruff
```

### Inspecting

```bash
uv pip list                                         # list installed packages
uv pip freeze                                       # freeze (requirements.txt format)
uv pip show flask                                   # show package details
uv pip tree                                         # dependency tree
uv pip check                                        # check environment compatibility
```

## Locking environments (pip-tools replacement)

### Compiling

```bash
uv pip compile requirements.in -o requirements.txt  # basic compile
uv pip compile pyproject.toml -o requirements.txt   # from pyproject.toml
uv pip compile setup.py -o requirements.txt         # from setup.py
uv pip compile -                                    # from stdin
echo "ruff" | uv pip compile -                      # stdin example
```

Options:

```bash
uv pip compile requirements.in --universal -o requirements.txt  # cross-platform
uv pip compile requirements.in --python-version 3.10 -o requirements.txt  # specific Python
uv pip compile requirements.in --python-platform linux -o requirements.txt  # specific platform
uv pip compile requirements.in --extra foo -o requirements.txt    # with extra
uv pip compile requirements.in --all-extras -o requirements.txt   # all extras
uv pip compile requirements.in --group foo -o requirements.txt    # dependency group
uv pip compile requirements.in --upgrade -o requirements.txt      # upgrade all
uv pip compile requirements.in --upgrade-package flask -o requirements.txt  # upgrade specific
uv pip compile requirements.in --no-strip-extras -o requirements.txt  # keep extras
uv pip compile requirements.in --no-annotate -o requirements.txt   # omit annotations
uv pip compile requirements.in --generate-hashes -o requirements.txt  # add hashes
```

### Syncing

```bash
uv pip sync requirements.txt                        # exact sync (removes extras)
uv pip sync pylock.toml                             # sync from PEP 751
```

`uv pip sync` performs exact sync — it removes packages not in the requirements file. Use `uv pip install` for additive installs that keep existing packages.

## Constraints and overrides

### Constraints

Constraints limit versions without triggering installation:

```requirements
# constraints.txt
pydantic<2.0
numpy>=1.24
```

```bash
uv pip compile requirements.in --constraint constraints.txt
uv pip install --constraint constraints.txt flask
```

### Build constraints

Same as constraints but applied to build-time dependencies:

```requirements
# build-constraints.txt
setuptools==75.0.0
```

```bash
uv pip compile requirements.in --build-constraint build-constraints.txt
```

### Overrides

Overrides force versions regardless of what packages require:

```requirements
# overrides.txt
c>=2.0
```

```bash
uv pip compile requirements.in --override overrides.txt
```

Use overrides to remove upper bounds from transitive dependencies. Unlike constraints (additive), overrides are absolute — they replace the requirements entirely.

## Index configuration

```bash
uv pip install --index-url https://pypi.org/simple/ flask
uv pip install --extra-index-url https://test.pypi.org/simple/ flask
uv pip install --find-links /path/to/wheels flask
uv pip install --no-index --find-links /path/to/wheels flask
```

## Python selection

```bash
uv pip install --python /path/to/python flask
uv pip install --python 3.12 flask
uv pip install --python-version 3.12 flask
uv pip install --python-platform linux flask
uv pip install --break-system-packages flask        # install into system Python
```

## Refresh and reinstall

```bash
uv pip install --refresh flask                       # revalidate all cached data
uv pip install --refresh-package flask flask         # revalidate specific package
uv pip install --reinstall flask                     # force reinstall
uv pip install --reinstall-package flask flask       # reinstall specific package
```

## pip configuration

Settings in `[tool.uv.pip]` apply only to `uv pip` commands:

```toml
[tool.uv.pip]
index-url = "https://test.pypi.org/simple"
```

This does not affect `uv sync`, `uv lock`, or `uv run`.

## Compatibility notes

- `uv pip` does not invoke pip internally — it matches the interface but may diverge on edge cases
- `--group` flags do not apply to other sources (e.g., `-r some/file` ignores `--group`)
- `uv pip compile --universal` is uv's extension beyond pip-tools
- `uv pip compile` reads `constraint-dependencies` from `pyproject.toml` at workspace root

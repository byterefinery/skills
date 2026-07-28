# Scripts and Tools

## PEP 723 Inline Script Metadata

Scripts declare dependencies directly in the file using a TOML comment block:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "requests<3",
#   "rich",
# ]
# ///

import requests
from rich.pretty import pprint

resp = requests.get("https://api.example.com/data")
pprint(resp.json())
```

### Managing Script Dependencies

```bash
uv add --script example.py requests rich     # add dependencies
uv add --script example.py 'flask>=3.0'      # version constraints
uv remove --script example.py requests       # remove dependency
uv lock --script example.py                  # lock to example.py.lock
uv export --script example.py                # export locked deps
uv tree --script example.py                  # show script dep tree
```

### Running Scripts

```bash
uv run example.py                             # auto-resolve inline metadata
uv run --python 3.11 example.py               # override Python version
uv run --with httpx example.py                # ad-hoc dependency
uv run --no-project example.py                # skip project context
echo 'print("hi")' | uv run -                 # stdin script
```

When a script has inline metadata, project dependencies are ignored. No `--no-project` needed.

### Script Locking

```bash
uv lock --script example.py                   # creates example.py.lock
```

Lockfile is placed adjacent to the script. Subsequent `uv run`, `uv add --script`, `uv export --script`, and `uv tree --script` reuse locked dependencies.

### Reproducible Scripts

```python
# /// script
# dependencies = ["requests"]
# [tool.uv]
# exclude-newer = "2024-01-01T00:00:00Z"
# ///
```

`exclude-newer` limits resolution to distributions released before the given date.

### Shebang Scripts

Make scripts executable without `uv run`:

```python
#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12"
# dependencies = ["httpx"]
# ///

import httpx
print(httpx.get("https://example.com"))
```

```bash
chmod +x greet
./greet
```

### GUI Scripts (Windows)

`.pyw` files run with `pythonw` (no console window):

```bash
uv run example.pyw                            # tkinter GUI
uv run --with PyQt5 example_pyqt.pyw         # PyQt5 GUI
```

## Tools (uvx / uv tool)

### Ephemeral Execution (uvx)

`uvx` is an alias for `uv tool run`. Runs tools in temporary, isolated environments.

```bash
uvx ruff check .                              # run ruff
uvx ruff@0.8.0 check .                        # specific version
uvx ruff@latest check .                       # latest version
uvx 'black[jupyter]@24.4.0' .                # with extras (quote for shell)
uvx --from httpie http                        # command differs from package
uvx --from 'mypy[faster-cache]==1.13.0' mypy # extras + version
uvx --with mkdocs-material mkdocs             # with plugin
uvx --python 3.11 ruff check .               # specific Python
uvx --lfs --from git+https://... lfs-cowsay  # Git LFS support
```

### Package vs Command Names

When the command name differs from the package name:

```bash
uvx --from httpie http                        # httpie package, http command
uvx --from pylint pylint                      # pylint package, pylint command
```

### Git Sources

```bash
uvx --from git+https://github.com/httpie/cli httpie
uvx --from git+https://github.com/httpie/cli@master httpie
uvx --from git+https://github.com/httpie/cli@3.2.4 httpie
uvx --from git+https://github.com/httpie/cli@2843b87 httpie
```

### Persistent Installation

```bash
uv tool install ruff                          # install to PATH
uv tool install 'ruff>=0.8'                   # with version constraint
uv tool install mkdocs --with mkdocs-material # with plugin
uv tool install --python 3.11 ruff            # specific Python
uv tool install --with-executables-from ansible-core,ansible-lint ansible
uv tool upgrade ruff                          # upgrade to latest in range
uv tool upgrade --all                         # upgrade all tools
uv tool uninstall ruff                        # remove tool
uv tool list                                  # list installed tools
uv tool dir                                   # show tool directory
uv tool update-shell                          # add tool bin to PATH
```

### Tool Isolation

Installed tools are isolated from the current environment. `python -c "import ruff"` will fail even after `uv tool install ruff`. This prevents dependency conflicts between tools, scripts, and projects.

### Legacy Windows Scripts

Tools support `.ps1`, `.cmd`, and `.bat` scripts:

```bash
uv tool run --from nuitka==2.6.7 nuitka.cmd --version
uv tool run --from nuitka==2.6.7 nuitka --version   # auto-resolves extension
```

Scripts are available at `$(uv tool dir)\<tool-name>\Scripts`.

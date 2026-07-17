# Tools

uv provides `pipx`-like functionality for running and installing CLI tools from Python packages.

## Running Tools (Ephemeral)

`uvx` is an alias for `uv tool run`. It executes a tool in an isolated, temporary environment.

```bash
# Run a tool
uvx ruff check .
uv tool run ruff check .

# Specific version
uvx ruff@0.9.0 check .

# Latest version
uvx ruff@latest check .

# Tool from different package name
uvx --from httpie http

# With extras
uvx --from 'mypy[faster-cache]' mypy main.py

# With additional dependencies
uvx --with mkdocs-material mkdocs serve

# From git
uvx --from git+https://github.com/httpie/cli httpie

# Force reinstall
uvx --reinstall ruff check .
```

### `uvx` vs `uv run`

- Use **`uvx`** when the tool is independent of your project
- Use **`uv run`** when the tool needs access to your project (e.g., `pytest`, `mypy`)

## Installing Tools (Persistent)

Installed tools are added to PATH and can be invoked directly.

```bash
# Install a tool
uv tool install ruff

# Specific version
uv tool install 'ruff>=0.9'

# With extras
uv tool install 'mypy[faster-cache]'

# With additional dependencies
uv tool install mkdocs --with mkdocs-material

# From git
uv tool install git+https://github.com/httpie/cli

# Python version
uv tool install --python 3.12 ruff
```

Installed tools live in a central directory. Each tool gets its own isolated environment, preventing dependency conflicts between tools.

## Managing Installed Tools

```bash
# List installed tools
uv tool list

# List with versions
uv tool list --show-versions

# Upgrade a tool
uv tool upgrade ruff

# Upgrade all tools
uv tool upgrade --all

# Uninstall a tool
uv tool uninstall ruff
```

Tool upgrades respect the version constraints from installation. To change constraints, reinstall:

```bash
uv tool install 'ruff>=0.10'  # replaces old constraint
```

## Tool Directories

```bash
# Show tool binary directory
uv tool dir --bin

# Show tool environments directory
uv tool dir --python
```

Ensure the bin directory is in PATH. If not, run:
```bash
uv python update-shell
```

## Package Name vs Command Name

When the executable name differs from the package name, use `--from`:

```bash
# http command comes from httpie package
uvx --from httpie http

# pyproject-fmt comes from pyproject-fmt package (same name, no --from needed)
uvx pyproject-fmt
```

## Legacy Windows Scripts

On Windows, tools with `.ps1`, `.cmd`, or `.bat` executables are supported:

```bash
uv tool run --from nuitka==2.6.7 nuitka --version
```

`uvx` automatically searches for these extensions in order: `.ps1`, `.cmd`, `.bat`.

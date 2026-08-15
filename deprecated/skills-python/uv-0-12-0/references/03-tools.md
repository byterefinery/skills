# Tools

## Running Tools (uvx)

`uvx` is an alias for `uv tool run`. It executes a tool in an ephemeral, isolated environment:

```bash
uvx ruff check src/
uvx pycowsay "hello"
uvx ruff@0.3.0 check                  # pin version
uvx ruff@latest check                  # force latest
```

### When to use uvx vs uv run

- **`uvx`** — tool runs in an isolated environment, unaware of the project. Use for standalone tools (ruff, black, httpie).
- **`uv run`** — tool runs with project dependencies and the project installed. Use for tools that inspect the project (pytest, mypy, ruff check on project code).

Exception: flat-layout projects (no `src/` directory) work with `uvx` since the project doesn't need to be installed.

### Package name differs from command

```bash
uvx --from httpie http              # command `http` from package `httpie`
uvx --from 'mypy[faster-cache]' mypy
```

### Version selection

```bash
uvx ruff@0.3.0 check                # exact version
uvx --from 'ruff>0.2.0,<0.3.0' ruff # version range
uvx --from 'mypy[reports]==1.13.0' mypy  # version + extras
```

The `@` syntax only accepts exact versions or `latest`. For ranges, use `--from`.

## Installing Tools

```bash
uv tool install ruff                 # install persistently
uv tool install 'ruff==0.5.0'        # pin version
uv tool install --force ruff         # reinstall
uv tool upgrade ruff                 # upgrade to latest
uv tool upgrade --all                # upgrade all tools
uv tool list                         # list installed tools
uv tool uninstall ruff               # remove tool
```

Installed tools place executables on PATH, available globally without `uv tool run`.

### Tool directory

Tools are installed into uv's tool directory. The path depends on installation method:

- Standalone installer: `~/.local/bin/` (Linux/macOS) or `%LOCALAPPDATA%\uv\bin\` (Windows)
- pip-installed uv: may require manual PATH configuration

## Tool environments

Each tool gets its own isolated environment in uv's cache. Environments are keyed by tool name and version constraint. Multiple tools do not share dependencies.

```bash
uv tool upgrade --reinstall ruff     # recreate environment from scratch
```

## Tool entry points

When a package provides multiple entry points, specify the command:

```bash
uv tool install --bin flask --bin flaskx --from flask
```

Or run directly:

```bash
uvx --from flask flask run
```

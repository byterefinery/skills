# Workspaces

Workspaces organize multiple packages (workspace members) under a shared lockfile, inspired by Cargo. Ideal for monorepos with interconnected libraries and applications.

## Creating a Workspace

A workspace is created implicitly when a `pyproject.toml` defines `[tool.uv.workspace]`:

```toml title="pyproject.toml"
[project]
name = "my-monorepo"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["tqdm"]

[tool.uv.workspace]
members = ["packages/*"]
```

Every directory matching the `members` globs must contain a `pyproject.toml`. The workspace root is itself a member.

### Excluding members

```toml
[tool.uv.workspace]
members = ["packages/*"]
exclude = ["packages/legacy"]
```

### Creating members

Running `uv init` inside a workspace automatically adds the new package as a member:

```bash
cd packages
uv init my-lib
# Automatically added to workspace members
```

## Workspace Structure

```
my-monorepo/
├── pyproject.toml          # Workspace root
├── uv.lock                 # Shared lockfile (one for entire workspace)
├── .venv/                  # Root virtual environment
└── packages/
    ├── lib-a/
    │   └── pyproject.toml  # Member
    └── lib-b/
        └── pyproject.toml  # Member
```

## Workspace Dependencies

Members depend on each other using `workspace = true` in `[tool.uv.sources]`:

```toml title="packages/lib-b/pyproject.toml"
[project]
name = "lib-b"
version = "0.1.0"
dependencies = ["lib-a"]    # Depends on workspace member

[tool.uv.sources]
lib-a = { workspace = true }
```

Workspace dependencies are installed as editable packages. Changes to `lib-a` are immediately visible to `lib-b`.

## Running Commands in Workspaces

By default, commands operate on the workspace root. Target specific members with `--package`:

```bash
# Run at workspace root
uv run python main.py
uv sync

# Run for a specific member
uv run --package lib-a pytest
uv sync --package lib-b

# Lock entire workspace
uv lock
```

Run from any directory within the workspace — uv finds the workspace root automatically.

## Shared Configuration

`[tool.uv.sources]` in the workspace root applies to all members unless overridden:

```toml title="pyproject.toml (workspace root)"
[tool.uv.sources]
requests = { index = "private" }

[tool.uv.indexes]
private = "https://private.pypi/simple"
```

All members inherit this source configuration. A member can override by defining its own `[tool.uv.sources]`.

## Nested Workspaces

Workspaces cannot be nested. If a workspace member contains another `[tool.uv.workspace]`, the inner workspace is ignored — those packages become standalone.

## Virtual Environments

- The workspace root has a `.venv` containing all workspace dependencies
- `uv sync` at the root syncs all members
- `uv sync --package lib-a` syncs only that member's environment
- Each member shares the same lockfile but may have different transitive dependencies

## Exporting from Workspaces

```bash
# Export entire workspace
uv export

# Export specific member
uv export --package lib-a

# Export to requirements.txt
uv export -r requirements.txt
```

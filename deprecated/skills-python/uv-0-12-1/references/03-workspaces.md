# Workspaces — multi-package management

Workspaces organize multiple packages in a single repository with a shared lockfile, inspired by Cargo workspaces.

## Creating a workspace

Add `[tool.uv.workspace]` to a `pyproject.toml` to implicitly create a workspace rooted at that package:

```toml
[project]
name = "albatross"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["bird-feeder", "tqdm>=4,<5"]

[tool.uv.sources]
bird-feeder = { workspace = true }

[tool.uv.workspace]
members = ["packages/*"]
exclude = ["packages/seeds"]

[build-system]
requires = ["uv_build>=0.12.1,<0.13"]
build-backend = "uv_build"
```

`members` accepts globs; `exclude` removes specific paths. Every member must contain a `pyproject.toml`.

`uv init` inside an existing project automatically adds the new member to the workspace.

## Workspace layout

```
albatross/
├── packages/
│   ├── bird-feeder/
│   │   ├── pyproject.toml
│   │   └── src/bird_feeder/
│   └── seeds/              # excluded
│       └── pyproject.toml
├── pyproject.toml          # workspace root
├── uv.lock                 # shared lockfile
└── src/albatross/
```

## Workspace sources

Dependencies on workspace members use `{ workspace = true }`:

```toml
[tool.uv.sources]
bird-feeder = { workspace = true }
```

Cross-workspace references:

```toml
[tool.uv.sources]
foo = { workspace = "../other-workspace" }
```

Workspace members are always installed in editable mode.

## Workspace-wide sources

Sources defined in the workspace root apply to all members unless overridden:

```toml
# Workspace root pyproject.toml
[tool.uv.sources]
tqdm = { git = "https://github.com/tqdm/tqdm" }
```

Every member installs `tqdm` from GitHub unless its own `tool.uv.sources` overrides.

## Running commands

```bash
uv run                          # runs in workspace root context
uv run --package bird-feeder pytest  # run in specific member
uv sync                         # syncs all members
uv lock                         # locks entire workspace
```

## When to use workspaces

**Use workspaces when:**
- Multiple interconnected packages share a repository
- A library has performance-critical extension modules as separate packages
- A plugin system with each plugin as a separate package

**Do not use workspaces when:**
- Members have conflicting requirements
- Members need separate virtual environments
- Members need different `requires-python` ranges

In these cases, use path dependencies instead:

```toml
[tool.uv.sources]
bird-feeder = { path = "packages/bird-feeder" }
```

## Workspace limitations

- Single `requires-python` for the entire workspace (intersection of all members)
- No dependency isolation between members — a member can import another member's dependencies
- `uv run --package` is not available with path dependencies (only with workspaces)

## Virtual workspace members

Members not depended on by the root can be virtual (dependencies installed, package not built):

```toml
# Workspace root
[tool.uv.workspace]
members = ["child"]
```

If `child` has no `[build-system]` and is not a direct dependency, it is virtual — its dependencies are installed but the package itself is not built.

If the root declares `dependencies = ["child"]` with `workspace = true`, then `child` is built and installed.

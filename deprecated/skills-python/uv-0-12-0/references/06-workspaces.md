# Workspaces

## Overview

A workspace groups multiple packages (members) under a single lockfile. Inspired by Cargo workspaces, it allows large codebases to split into separate packages while sharing dependency resolution.

## Creating a workspace

Add `[tool.uv.workspace]` to the root `pyproject.toml`:

```toml title="pyproject.toml"
[project]
name = "my-workspace"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["shared-lib", "tqdm>=4,<5"]

[tool.uv.sources]
shared-lib = { workspace = true }

[tool.uv.workspace]
members = ["packages/*"]
exclude = ["packages/internal"]
```

Running `uv init` inside an existing project automatically creates a workspace and adds the new member.

## Workspace structure

```
my-workspace/
├── pyproject.toml              # workspace root + member
├── uv.lock                     # shared lockfile
├── src/my_workspace/
├── packages/
│   ├── shared-lib/
│   │   ├── pyproject.toml      # workspace member
│   │   └── src/shared_lib/
│   └── another-pkg/
│       ├── pyproject.toml      # workspace member
│       └── src/another_pkg/
└── excluded/
    └── pyproject.toml          # not a member (excluded)
```

## Workspace sources

Dependencies on workspace members use `workspace = true`:

```toml
[project]
dependencies = ["shared-lib"]

[tool.uv.sources]
shared-lib = { workspace = true }
```

This tells uv to resolve `shared-lib` from the workspace rather than from PyPI. Workspace dependencies are always installed as editable packages.

### Cross-workspace references

```toml
[tool.uv.sources]
external-lib = { workspace = true, workspace = "../other-workspace" }
```

The path is resolved relative to the project declaring the source.

## Inherited sources

Sources defined in the workspace root apply to all members unless overridden:

```toml title="pyproject.toml (workspace root)"
[tool.uv.sources]
tqdm = { git = "https://github.com/tqdm/tqdm" }
```

Every member installs `tqdm` from Git unless its own `pyproject.toml` overrides the source.

## Running commands

```bash
uv run pytest                        # runs for workspace root
uv run --package shared-lib pytest   # runs for specific member
uv sync                              # syncs workspace root
uv sync --package shared-lib         # syncs specific member
uv lock                              # locks entire workspace
```

`uv lock` resolves all members at once, producing a single `uv.lock` at the workspace root.

## Adding members

```bash
cd my-workspace
uv init packages/new-member          # auto-adds to workspace
```

Or manually: add the directory to `members` globs in `[tool.uv.workspace]`.

## Removing members

Remove the directory from `members` globs or add to `exclude`. The member's `pyproject.toml` remains intact as a standalone project.

## Workspace rules

- Every workspace needs a root package (the directory containing `[tool.uv.workspace]`)
- All members must have a `pyproject.toml`
- Members can be applications or libraries
- The workspace shares a single `uv.lock`
- Members are installed as editable packages
- Root-level `[tool.uv.sources]` apply to all members (inheritable)
- `members` accepts glob patterns; `exclude` removes matches

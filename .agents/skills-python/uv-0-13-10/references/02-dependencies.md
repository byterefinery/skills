# uv 0.13.10 dependencies

How to declare and source dependencies in uv-managed projects, scripts, and environments. Sourced from the uv 0.13.10 documentation (`docs/concepts/projects/dependencies.md`, `indexes.md`, `resolution.md`, `sync.md`, `guides/scripts.md`) and the 0.13.10 CLI help.

## Dependency fields

Dependencies live in four standard fields in `pyproject.toml`:

| Field | Purpose |
|---|---|
| `project.dependencies` | Published dependencies (always included when the package is installed) |
| `project.optional-dependencies` | Published optional dependencies ("extras") |
| `[dependency-groups]` | Local-only development dependencies (PEP 735), never published |
| `[build-system].requires` | Build-time dependencies (PEP 518), not needed to run the package |

`uv add` / `uv remove` modify these fields; you can also edit `pyproject.toml` directly (uv re-locks when the lockfile becomes stale). `uv add` writes a lower-bound constraint (e.g. `httpx>=0.27.2`) by default; tune with `--bounds lower|major|minor|exact` or pass the constraint directly (`uv add "httpx>=0.20"`). `uv add -r requirements.txt` imports dependencies from a requirements file.

Platform-specific dependencies use PEP 508 markers: `uv add "jax; sys_platform == 'linux'"`.

## Dependency specifiers

Entries use [PEP 508 dependency specifier] syntax: name, version constraint, extras, and environment marker.

```toml
dependencies = [
  "tqdm >=4.66.2,<5",                       # version range
  "torch ==2.2.2",                          # exact pin
  "transformers[torch] >=4.39.3,<5",        # extras
  "importlib_metadata >=7.1.0,<8; python_version < '3.10'",  # marker
  "httpx @ https://example.com/httpx-0.27.0.tar.gz",          # direct URL
]
```

`uv` warns when direct dependencies lack lower bounds — lower bounds matter for correct conflict resolution and for library consumers.

## Dependency sources (`tool.uv.sources`)

`tool.uv.sources` maps a dependency name to an alternative source, used during development. **Sources are honored only by uv**; other tools see only the standard tables.

```toml
[project]
dependencies = ["foo", "httpx", "bar", "qux"]

[tool.uv.sources]
foo = { path = "./packages/foo" }                                   # local project directory
httpx = { git = "https://github.com/encode/httpx", tag = "0.27.0" } # git
bar = { url = "https://files.pythonhosted.org/.../bar-0.1.0.tar.gz" } # URL
qux = { index = "pytorch" }                                        # pinned to an index
baz = { workspace = true }                                         # workspace member
```

Supported source kinds:

- **Path** — local wheel, source archive (`.tar.gz`, `.zip`), or directory with a `pyproject.toml` (editable). `uv add /path/to/project`
- **Git** — `git+https://...` or `git+ssh://...`; reference via `--tag`, `--branch`, `--rev`, or `#subdirectory=` in the URL. `--lfs` / `lfs = true` for Git LFS objects.
- **URL** — direct `https://` link to a wheel or source distribution.
- **Index** — `{ index = "name" }` pins the package to a named `[[tool.uv.index]]`; the package is never downloaded from other indexes. `uv add torch --index pytorch=https://...` writes both the index and the source entry.
- **Workspace member** — `{ workspace = true }`; members must be explicitly listed in `[tool.uv.workspace].members` and are always installed editable. A path string (`{ workspace = "../other-workspace" }`) sources from a different workspace.

Variants:

- **Platform-specific source** — `marker = "sys_platform == 'darwin'"` limits the source to matching environments; the dependency still resolves on all platforms (falling back to the index elsewhere).
- **Multiple sources** — a list of source tables disambiguated by `marker` (e.g., different indexes per platform, or `extra = "cpu"` / `extra = "gpu"` per optional dependency).
- **Disabling** — `uv lock --no-sources` (or `--no-sources-package <pkg>`) ignores the table entirely; also disables workspace-member discovery. Use `uv build --no-sources` before publishing to verify the project builds against publishable metadata.

## Optional dependencies (extras)

```toml
[project.optional-dependencies]
plot = ["matplotlib>=3.6.3"]
excel = ["openpyxl>=3.1.0"]
```

- Requested with `package[extra]` syntax; added with `uv add httpx --optional network`.
- Not synced by default — `uv sync --extra plot` or `--all-extras`.
- Extras can have `tool.uv.sources` entries, including per-extra source lists.
- Conflicting extras fail resolution unless declared in `tool.uv.conflicts`.

## Dependency groups (development dependencies)

```toml
[dependency-groups]
dev = ["pytest >=8.1.1,<9"]
lint = ["ruff"]
```

- `uv add --dev pytest` (creates `dev`), `uv add --group lint ruff`.
- The `dev` group is the only default group; it is synced by default. Change defaults with `tool.uv.default-groups = ["dev", "foo"]` or `"all"`.
- Toggle with `--no-dev` / `--only-dev` / `--no-default-groups` / `--group <g>` / `--only-group <g>` / `--no-group <g>`. `--dev` ≡ `--group dev`, etc.
- **Group exclusions always beat inclusions**: `uv sync --no-group foo --group foo` installs nothing from `foo`.
- **Nesting**: a group can include others with `{ include-group = "lint" }`.
- Per-group Python range: `[tool.uv.dependency-groups] dev = { requires-python = ">=3.12" }`.
- Legacy `tool.uv.dev-dependencies` still works and is combined with `dependency-groups.dev`; `uv add --dev` reuses the section if it exists.
- All groups are resolved together and must be compatible, unless declared conflicting.

## Build dependencies

`[build-system].requires` (PEP 518) is resolved by uv during `uv build`, `uv publish`, and syncs of the project itself. `tool.uv.sources` is respected for build dependencies by default.

## Indexes

Default index is PyPI. Add more via `[[tool.uv.index]]`:

```toml
[[tool.uv.index]]
name = "pytorch"                              # optional name
url = "https://download.pytorch.org/whl/cpu"  # required
# default = true    # replaces PyPI as the default index
# explicit = true   # only usable via tool.uv.sources pinning
# format = "flat"   # flat index: directory or HTML page of wheels (pip --find-links)
# authenticate = "always" | "never"
# cache-control = { api = "max-age=600", files = "max-age=365000000, immutable" }
# exclude-newer = "7 days" | false
```

Rules:

- Indexes are consulted in definition order (first defined = first consulted); CLI-provided indexes take precedence over config-file ones.
- The **default index is always lowest priority**, regardless of position. `default = true` on any entry removes PyPI from the list.
- `first-index` (default strategy) stops at the first index containing a package — protects against dependency-confusion attacks. Alternatives: `unsafe-first-match`, `unsafe-best-match` (closest to pip, risky).
- Authentication: `UV_INDEX_<NAME>_USERNAME` / `_PASSWORD` env vars (name uppercased, non-alphanumerics → `_`), credentials embedded in the URL, netrc, or keyring. Credentials are never stored in `uv.lock`.
- `--index <name=url>` (adds), `--default-index <url>` (replaces PyPI). `--index-url` / `--extra-index-url` are deprecated aliases. `UV_INDEX` / `UV_DEFAULT_INDEX` env vars.
- Proxy indexes (`[[tool.uv.proxy-index]]`) and `hash-algorithm` per index are preview features.

## Lockfile (`uv.lock`)

- uv-managed, versioned schema; commit it, never hand-edit. uv rejects lockfiles with a higher schema version; schema bumps happen only in minor releases.
- Created/updated automatically by `uv add`, `uv remove`, `uv lock`, `uv run`, etc. `uv lock` writes it explicitly; `uv lock --check` verifies freshness; `uv lock --dry-run` previews.
- **Preference**: existing locked versions are preferred on every lock/sync; new releases do not update the lockfile. Upgrade with `uv lock --upgrade` (all) or `--upgrade-package <pkg>==<ver>` (one). Git sources: the locked commit SHA is preferred over the branch tip until upgraded.
- Locks are universal: one `uv.lock` covers all supported platforms/Python versions (per `requires-python`), with markers and per-environment versions.
- `uv tree` reads the lockfile and auto-updates it if stale (`--frozen`/`--locked` to control).
- **Export** (the lockfile format is uv-specific): `uv export --format requirements.txt | pylock.toml | cyclonedx1.5`, with `--extra`, `--all-extras`, `--group`, `--no-dev`, `--no-hashes`, `-o FILE`. `pylock.toml` is the PEP 751 portable lockfile format.

## Resolution behaviors that affect dependencies

- **Strategy**: `--resolution highest` (default), `lowest` (lowest compatible for everything — good for testing lower bounds), `lowest-direct`.
- **Pre-releases**: `--prerelease if-necessary` (default: stable preferred, pre-release only if no stable works), `allow`, `disallow`, `explicit` (only when the requirement itself is a pre-release). Per-package: `--prerelease-package foo=allow`.
- **`environments`** limits platforms resolved; **`required-environments`** requires wheels for listed platforms for packages without source distributions.
- **Constraints** (`--constraint` / `tool.uv.constraint-dependencies`) narrow versions without adding packages; **overrides** (`tool.uv.override-dependencies`) replace a dependency's declared requirements (can expand versions; scoped entries `{ package = { name, version }, dependencies = [...] }` supported); **exclusions** (`tool.uv.exclude-dependencies`) remove packages from the graph.
- **`tool.uv.dependency-metadata`** provides static metadata (`requires-dist`, `requires-python`, ...) for packages that lack it, avoiding a build at resolve time; `version` is required for direct-URL dependencies.
- **Conflicts**: `tool.uv.conflicts = [[{ extra = "a" }, { extra = "b" }]]` resolves conflicting extras/groups separately (cannot be installed together).
- **Reproducibility**: `--exclude-newer <date|duration>` limits resolution to distributions uploaded before the cutoff (requires index `upload-time` metadata; PyPI has it). Supports durations (`exclude-newer = "1 week"` = cooldown). Per-package: `--exclude-newer-package <pkg>=<date|false>`.
- **Fork strategy**: `--fork-strategy requires-python` (default; latest version per Python range) or `fewest` (minimize distinct locked versions).
- **Universal resolution**: a package may appear multiple times in `uv.lock` with different versions for different platforms/Python versions.

## PEP 723 inline script metadata

A standalone `.py` file declares its own dependencies in a metadata block after the shebang:

```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "httpx>=0.27.0",
#     "numpy<2",
# ]
# ///

import httpx
```

- Run with `uv run script.py` — uv creates an isolated environment from the metadata, independent of any surrounding project (no `--no-project` needed).
- Create with `uv init --script example.py`; manage with `uv add --script example.py 'requests<3'` / `uv remove --script example.py httpx`.
- `requires-python` is honored; a missing interpreter is downloaded automatically. The `dependencies` field must be provided even if empty.
- A `[tool.uv]` table in the metadata block (e.g., `exclude-newer`, `[[tool.uv.index]]`) is respected; `uv add --script --index ...` writes index entries into the inline metadata.
- `uv run --with <pkg>` adds dependencies for a single invocation without editing the script; `uv run --isolated` runs in a throwaway environment.

## Virtual (non-installed) dependencies

`uv run --with` creates temporary dependencies that are not written to `pyproject.toml`; `uv tool run` (`uvx`) is the tools variant. Neither touches the project environment.

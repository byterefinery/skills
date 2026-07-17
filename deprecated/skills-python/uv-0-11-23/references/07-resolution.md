# Resolution

uv resolves dependencies by finding compatible package versions that satisfy all requirements. It supports platform-specific and universal (cross-platform) resolution strategies.

## Resolution Strategies

### Default (lowest)

By default, uv prefers the lowest compatible version, matching pip-tools behavior. This minimizes breakage from unexpected new versions.

### Highest

```bash
uv lock --resolution highest
```

Prefers the highest compatible version for each package. Use when you want latest versions and accept more frequent updates.

### Lowest-direct

```bash
uv lock --resolution lowest-direct
```

Uses lowest versions only for direct dependencies, highest for transitive. Useful for testing minimum supported versions of your declared deps while keeping transitive deps current.

## Platform Resolution

### Platform-specific (pip interface)

`uv pip compile` produces platform-specific resolutions by default — optimized for the current OS/architecture.

```bash
# Resolve for different platform
uv pip compile requirements.in \
  --python-platform linux \
  --python-version 3.11 \
  -o requirements-linux.txt
```

### Universal (project interface)

`uv lock` produces universal lockfiles covering all platforms. The same `uv.lock` works across macOS, Linux, and Windows. Platform-specific packages are resolved using environment markers.

## Constraints

Constraints add upper/lower bounds without adding dependencies:

```toml title="pyproject.toml"
[tool.uv]
constraint-dependencies = [
    "urllib3<2.0",
]
```

Or via file:
```bash
uv lock --constraint constraints.txt
uv pip compile requirements.in --constraint constraints.txt -o requirements.txt
```

Constraints are additive — they narrow the allowed version range but don't force installation.

## Overrides

Overrides replace all version requirements for a package, even if it causes technically invalid resolutions:

```toml title="pyproject.toml"
[tool.uv]
override-dependencies = [
    "numpy>=2.0",
]
```

Or via file:
```bash
uv lock --override overrides.txt
uv pip compile requirements.in --override overrides.txt -o requirements.txt
```

Use overrides to remove upper bounds from transitive dependencies or force a specific version when packages conflict.

## Build Constraints

Constraints applied only during build-time resolution:

```toml title="pyproject.toml"
[tool.uv]
build-constraint-dependencies = [
    "setuptools==75.0.0",
]
```

Ensures consistent build environments across all packages that need building.

## Package Indexes

### Default (PyPI)

uv uses PyPI by default. No configuration needed.

### Custom Indexes

```toml title="pyproject.toml"
[tool.uv]
index-url = "https://private.pypi/simple"

[tool.uv.indexes]
extra = "https://extra.pypi/simple"
```

Command-line:
```bash
uv pip install --index-url https://private.pypi/simple flask
uv pip install --extra-index-url https://extra.pypi/simple flask
```

### No Index

```bash
uv pip install --no-index --find-links ./wheels flask
```

### Package-specific Sources

```toml title="pyproject.toml"
[tool.uv.sources]
mypackage = { index = "private" }
otherpackage = { git = "https://github.com/me/other" }
```

## Exclude Newer

Limit resolution to distributions released before a date:

```toml title="pyproject.toml"
[tool.uv]
exclude-newer = "2025-01-01T00:00:00Z"
```

```bash
uv lock --exclude-newer 2025-01-01
```

Ensures reproducible resolutions by excluding packages released after the cutoff date.

## Dependency Conflicts

When resolution fails, uv reports conflicting requirements. Common causes:

- **Incompatible version ranges** — `A` requires `lib>=1,<2` and `B` requires `lib>=2`. Use overrides to force a version.
- **Platform markers** — Dependencies with conflicting markers may fail in universal resolution. Use platform-specific resolution.
- **Git dependencies** — Git packages cannot be combined with version-pinned PyPI packages of the same name.

## Resolution Output

```bash
# Verbose resolution output
uv lock --verbose

# Show resolution graph
uv tree
```

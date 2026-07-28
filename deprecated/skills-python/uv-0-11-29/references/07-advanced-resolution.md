# Advanced Resolution

## Resolution Strategies

```bash
uv lock --resolution highest         # default: prefer latest versions
uv lock --resolution lowest          # prefer oldest compatible versions
uv lock --resolution lowest-direct   # lowest for direct deps, highest for transitive
```

## Prerelease Handling

```bash
uv lock --prerelease allow           # allow prereleases everywhere
uv lock --prerelease disallow        # never use prereleases
uv lock --prerelease if-necessary-or-explicit  # default: allow if no stable exists
```

Per-package prerelease control:

```toml
[tool.uv]
prerelease = "if-necessary-or-explicit"

[[tool.uv.dependency-metadata]]
name = "my-package"
prerelease = "allow"
```

## Overrides

Force specific versions regardless of what packages require:

```bash
uv lock --override overrides.txt
uv pip compile requirements.in --override overrides.txt
```

overrides.txt:

```
c>=2.0
numpy==1.24.0
```

In `pyproject.toml`:

```toml
[tool.uv]
override-dependencies = [
    "c>=2.0",
    "numpy==1.24.0",
]
```

Overrides are absolute — they replace all requirements for the package. Use when transitive dependencies have incompatible constraints.

## Constraints

Add bounds without triggering installation:

```bash
uv lock --constraint constraints.txt
uv pip compile requirements.in --constraint constraints.txt
```

constraints.txt:

```
pydantic<2.0
numpy>=1.24
```

In `pyproject.toml`:

```toml
[tool.uv]
constraint-dependencies = [
    "pydantic<2.0",
    "numpy>=1.24",
]
```

Constraints are additive — combined with constituent package requirements.

## Build Constraints

Control build-time dependency versions:

```bash
uv pip compile requirements.in --build-constraint build-constraints.txt
```

build-constraints.txt:

```
setuptools==75.0.0
wheel>=0.42
cython>=3.0
```

In `pyproject.toml`:

```toml
[tool.uv]
build-constraint-dependencies = [
    "setuptools==75.0.0",
]
```

## Reproducible Resolutions

### exclude-newer

Limit resolution to distributions released before a date:

```bash
uv lock --exclude-newer 2024-06-01T00:00:00Z
```

```toml
[tool.uv]
exclude-newer = "2024-06-01T00:00:00Z"
```

Per-index exclude-newer:

```toml
[[tool.uv.index]]
name = "internal"
url = "https://internal.example.com/simple"
exclude-newer = "7 days"
```

Per-package exclude-newer:

```bash
uv lock --exclude-newer-package torch=2024-06-01T00:00:00Z
```

In scripts:

```python
# /// script
# dependencies = ["requests"]
# [tool.uv]
# exclude-newer = "2024-01-01T00:00:00Z"
# ///
```

## Extra Build Dependencies

For packages needing specific build-time dependencies:

```toml
[tool.uv.extra-build-dependencies]
cchardet = ["cython"]
deepspeed = [{ requirement = "torch", match-runtime = true }]
flash-attn = [{ requirement = "torch", match-runtime = true }]
```

`match-runtime = true` ensures the build dependency matches the version installed in the project environment.

For packages without static metadata (e.g., `axolotl`):

```toml
[project]
dependencies = ["axolotl[deepspeed, flash-attn]", "torch==2.6.0"]

[tool.uv.extra-build-dependencies]
axolotl = ["torch==2.6.0"]
deepspeed = ["torch==2.6.0"]
flash-attn = ["torch==2.6.0"]
```

### Dynamic Metadata

For packages with dynamic metadata that depends on git tags:

```toml
[tool.uv]
cache-keys = [{ file = "pyproject.toml" }, { git = { commit = true, tags = true } }]
```

### Always Rebuild

Force rebuild on every run:

```toml
[tool.uv]
reinstall-package = ["my-package"]
```

## Dependency Metadata

Provide metadata for packages that don't declare static metadata:

```toml
[[tool.uv.dependency-metadata]]
name = "flash-attn"
version = "2.6.3"
requires-dist = ["torch", "einops"]
```

`version` is optional for registry dependencies (applies to all versions if omitted) but required for direct URL dependencies.

## Platform-Specific Sources

```toml
[tool.uv.sources]
torch = [
  { index = "pytorch-cpu", marker = "sys_platform == 'darwin'" },
  { index = "pytorch-cu132", marker = "sys_platform != 'darwin'" },
]

my-pkg = [
  { path = "./my-pkg-linux", marker = "sys_platform == 'linux'" },
  { path = "./my-pkg-macos", marker = "sys_platform == 'darwin'" },
]
```

## Resolution Diagnostics

```bash
uv lock -v                          # verbose resolution
uv lock -vv                         # extra verbose
uv tree                             # view resolved tree
uv tree --format json               # JSON output
```

## Common Resolution Errors

### Conflicting Root Requirements

```
error: Conflicting requirements for `package`
  > `package>=2.0` (from root)
  > `package<2.0` (from `other-package`)
```

Fix: use overrides or adjust version constraints.

### Unsatisfiable Transitive Dependencies

```
error: No compatible version found for `package`
```

Fix: use `--resolution lowest`, add constraints, or use overrides.

### Platform Incompatibility

```
error: No wheels found for `package` on linux-x86_64
```

Fix: check platform support, add `required-environments`, or use `--python` to specify correct interpreter.

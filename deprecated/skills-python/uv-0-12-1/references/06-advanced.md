# Advanced — build isolation, cache, resolution, publishing, Docker

## Build isolation

### Augmenting build dependencies

For packages that need build deps not declared in their metadata:

```toml
[tool.uv.extra-build-dependencies]
cchardet = ["cython"]
```

Match runtime versions:

```toml
[tool.uv.extra-build-dependencies]
deepspeed = [{ requirement = "torch", match-runtime = true }]
flash-attn = [{ requirement = "torch", match-runtime = true }]

[tool.uv.extra-build-variables]
flash-attn = { FLASH_ATTENTION_SKIP_CUDA_BUILD = "TRUE" }
```

`match-runtime = true` ensures the build dep matches the version resolved for the project environment. Only works with static-metadata packages.

### Disabling build isolation

```toml
[tool.uv]
no-build-isolation-package = ["cchardet"]
```

uv performs two-phase install: first installs isolatable packages, then non-isolated ones. Build deps must be in the project environment before the non-isolated package is built.

For packages that need build deps only at install time:

```toml
[project.optional-dependencies]
build = ["setuptools", "cython"]

[tool.uv]
no-build-isolation-package = ["cchardet"]
```

```bash
uv sync --extra build    # install build deps + target
uv sync                  # remove build deps, keep target
```

### Providing metadata upfront

For packages without static metadata:

```toml
[[tool.uv.dependency-metadata]]
name = "flash-attn"
version = "2.6.3"
requires-dist = ["torch", "einops"]
```

`version` is optional for registry deps, required for direct URL deps.

## Cache

### Cache keys

Control when editable/local packages are rebuilt:

```toml
[tool.uv]
cache-keys = [
  { file = "pyproject.toml" },
  { git = { commit = true, tags = true } },
  { env = "MY_ENV_VAR" },
  { dir = "src" },
]
```

Globs supported: `{ file = "**/*.toml" }` (may be expensive on large trees).

### Always rebuild

```toml
[tool.uv]
reinstall-package = ["my-package"]
```

### Cache commands

```bash
uv cache clean                    # clear all
uv cache clean ruff               # clear specific package
uv cache prune                    # remove unused entries
uv cache prune --ci               # CI-optimized: keep built wheels, remove pre-built
```

### Refresh flags

```bash
uv sync --refresh                 # revalidate all cached data
uv sync --refresh-package ruff    # revalidate specific package
uv sync --reinstall               # force reinstall all
uv sync --reinstall-package ruff  # reinstall specific package
```

## Resolution strategies

### Universal vs platform-specific

`uv.lock` uses universal resolution — one lockfile for all platforms. `uv pip compile` defaults to platform-specific; use `--universal` for cross-platform.

### Multi-version resolution

During universal resolution, uv picks the latest compatible version per Python version. For example, with `requires-python = ">=3.8"`, a dependency requiring 3.9+ will get the latest version for 3.9+ users and the previous version for 3.8 users.

### Resolution mode

```bash
uv lock --resolution highest              # default: latest compatible
uv lock --resolution lowest               # lowest compatible
uv lock --resolution lowest-direct        # lowest for direct deps, highest for transitive
```

### Fork strategy

```bash
uv lock --fork-strategy requires-python   # fork on requires-python (default)
uv lock --fork-strategy environments      # fork on environments setting
```

### Reproducible resolutions

```toml
[tool.uv]
exclude-newer = "2024-01-01T00:00:00Z"
```

Packages released after this date are ignored. Per-index overrides:

```toml
[[tool.uv.index]]
name = "internal"
url = "https://internal.example.com/simple"
exclude-newer = "7 days"
```

## Building and publishing

### Building

```bash
uv build                              # build current directory
uv build /path/to/project             # build specific directory
uv build --package my-lib             # build workspace member
uv build --no-sources                 # verify standard compatibility
uv build --sdist                      # source distribution only
uv build --wheel                      # wheel only
```

### Version management

```bash
uv version                            # read current version
uv version --short                    # version only
uv version --output-format json       # JSON output
uv version 1.0.0                      # set exact version
uv version --bump minor               # semantic bump
uv version --bump patch --bump dev=123  # compound bump
uv version --bump stable              # clear pre-release
uv version 2.0.0 --dry-run            # preview change
```

Bump components: `major`, `minor`, `patch`, `stable`, `alpha`, `beta`, `rc`, `post`, `dev`.

### Publishing

```bash
uv publish                            # publish to PyPI (default)
uv publish --index testpypi           # publish to named index
uv publish --token $PYPI_TOKEN        # token auth
uv publish --username __token__ --password $TOKEN  # explicit token
uv publish --check-url https://pypi.org/simple/  # check existing files
uv publish --no-attestations          # skip attestation upload
```

For custom indexes:

```toml
[[tool.uv.index]]
name = "testpypi"
url = "https://test.pypi.org/simple/"
publish-url = "https://test.pypi.org/legacy/"
explicit = true
```

### Testing published packages

```bash
uv run --with my-package --no-project -- python -c "import my_package"
uv run --with my-package --refresh-package my-package --no-project -- python -c "..."
```

## Docker integration

### Layer caching

```dockerfile
FROM python:3.12-slim
WORKDIR /app

# Layer 1: install uv
COPY --from=ghcr.io/astral-sh/uv:0.12.1 /uv /usr/local/bin/uv

# Layer 2: lockfile (depends only on pyproject.toml)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Layer 3: source code
COPY . .
RUN uv sync --frozen --no-dev
```

Use `uv cache prune --ci` at end of CI jobs to keep cache efficient.

### CI caching pattern

```yaml
- name: Cache uv
  uses: actions/cache@v4
  with:
    path: ~/.cache/uv
    key: uv-${{ runner.os }}-${{ hashFiles('uv.lock') }}

- name: Sync
  run: |
    uv sync --frozen
    uv cache prune --ci
```

## Malware checking

```toml
[tool.uv.audit]
malware-check = true
# malware-check-url = "https://custom-osv.example.com"
```

Or: `UV_MALWARE_CHECK=1 uv sync`

Checks lockfile against OSV/OpenSSF malicious packages database. Terminates sync on match.

## Partial installations

For multi-step installs (Docker layer caching):

```bash
uv sync --no-install-project          # deps only, no project
uv sync --no-install-workspace        # deps only, no workspace members
uv sync --no-install-package foo      # skip specific package
```

Dependencies of skipped packages are still installed.

## Preview features

Enable preview features:

```toml
[tool.uv]
preview-features = ["index-hash-algorithm"]
```

Or: `UV_PREVIEW_FEATURES=index-hash-algorithm`

Preview features are experimental and subject to change.

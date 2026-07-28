# CI and Deployment

## GitHub Actions

### Basic Workflow

```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true
          cache-dependency-glob: uv.lock

      - name: Run tests
        run: uv run pytest
```

### Caching

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v4
  with:
    enable-cache: true
    cache-dependency-glob: uv.lock

- name: Prune cache for CI
  run: uv cache prune --ci
```

`uv cache prune --ci` removes pre-built wheels and unzipped source distributions, keeping only wheels built from source. Run at the end of CI jobs.

### Multi-OS Matrix

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    python-version: ["3.11", "3.12", "3.13"]

steps:
  - uses: actions/checkout@v4
  - uses: astral-sh/setup-uv@v4
    with:
      enable-cache: true
  - run: uv sync --python ${{ matrix.python-version }}
  - run: uv run pytest
```

## GitLab CI

```yaml
test:
  image: python:3.12
  before_script:
    - curl -LsSf https://astral.sh/uv/install.sh | sh
    - export PATH="$HOME/.local/bin:$PATH"
  cache:
    key: ${CI_COMMIT_REF_SLUG}-uv-cache
    paths:
      - .uv-cache/
  script:
    - UV_CACHE_DIR=.uv-cache uv sync --frozen
    - uv run pytest
    - uv cache prune --ci
```

## Docker

### Multi-Stage Build

```dockerfile
FROM python:3.12-slim AS builder

# Install uv
RUN pip install --no-cache-dir uv

WORKDIR /app
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-cache --no-dev

# Copy source and build
COPY . .
RUN uv build

FROM python:3.12-slim AS runtime

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/dist /app/dist

ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "main.py"]
```

### Minimal Image

```dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache --no-editable

COPY . .
CMD ["uv", "run", "python", "main.py"]
```

### Using UV_PROJECT_ENVIRONMENT

```dockerfile
FROM python:3.12-slim

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app
COPY pyproject.toml uv.lock ./

# Install to system Python
RUN UV_PROJECT_ENVIRONMENT=/usr/local uv sync --frozen --no-cache --no-editable

COPY . .
CMD ["python", "main.py"]
```

## Frozen Syncs

In CI and deployment, use `--frozen` to skip lockfile validation:

```bash
uv sync --frozen                    # trust existing lockfile
uv run --frozen pytest              # run without lockfile check
```

This speeds up CI by avoiding re-resolution when the lockfile is already current.

## No-Editable Deployments

For production, install the project non-editably:

```bash
uv sync --no-editable               # install as built package
```

This decouples the environment from the source tree, suitable for deployment.

## Offline Mode

```bash
uv sync --offline                   # no network access
UV_OFFLINE=1 uv sync                # via environment variable
```

Requires all dependencies to be cached or available locally.

## Cache Strategies

### Local Development

Default cache location. No configuration needed.

```bash
uv cache dir                        # show cache location
```

### CI

```bash
# Use project-local cache
UV_CACHE_DIR=.uv-cache uv sync

# Or use a shared cache directory
UV_CACHE_DIR=/shared-cache uv sync

# Prune at end of job
uv cache prune --ci
```

### Shared/Remote Cache

```bash
# Mount a volume or use a remote cache
UV_CACHE_DIR=/mnt/cache uv sync
```

uv's cache is thread-safe and supports concurrent access. Multiple processes can read/write simultaneously.

## Performance Tips

### Skip Unnecessary Work

```bash
uv sync --frozen                    # skip lockfile check
uv run --no-project script.py       # skip project resolution
uv sync --no-dev                    # skip dev dependencies
```

### Targeted Refresh

```bash
uv sync --refresh-package ruff      # refresh only one package
uv sync --reinstall-package flask   # reinstall only one package
```

### Parallel Execution

uv commands are safe to run concurrently against the same environment. uv applies file-based locks during installation.

## Common CI Patterns

### Test with Multiple Python Versions

```bash
for version in 3.11 3.12 3.13; do
  uv sync --python $version --frozen
  uv run --python $version pytest
done
```

### Build and Publish

```bash
uv sync --frozen
uv run pytest
uv build
uv publish --token $UV_PUBLISH_TOKEN
```

### Lint and Format

```bash
uv sync --extra dev
uv run ruff check .
uv run ruff format --check .
```

### Dependency Audit

```bash
uv audit                            # check for known vulnerabilities
uv audit --service-url https://...  # custom OSV service
```

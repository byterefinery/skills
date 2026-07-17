# CI Integration

## GitHub Actions

### Using the official action

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/ruff-action@v1
        with:
          args: "check"
      - uses: astral-sh/ruff-action@v1
        with:
          args: "format --check"
```

### Using uvx (ephemeral, no install step)

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uvx ruff check --output-format=github
      - run: uvx ruff format --check
```

### With annotations

Use `--output-format=github` to generate annotations in the GitHub PR check:

```yaml
- run: uvx ruff check --output-format=github
```

## GitLab CI

```yaml
lint:
  image: ghcr.io/astral-sh/ruff:0.15.18
  script:
    - ruff check --output-format=gitlab
    - ruff format --check
```

Or with Docker:

```yaml
lint:
  image: python:3.12-slim
  before_script:
    - pip install ruff==0.15.18
  script:
    - ruff check --output-format=gitlab
    - ruff format --check
```

## Pre-commit Hook

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.18
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format
```

## Makefile / Justfile

```makefile
.PHONY: lint format lint-fix

lint:
	ruff check .
	ruff format --check .

lint-fix:
	ruff check --fix .
	ruff format .
```

## Output Formats

Ruff supports multiple output formats for different CI systems:

| Format | Use case |
|---|---|
| `full` (default) | Human-readable, local development |
| `concise` | Compact output |
| `github` | GitHub Actions annotations |
| `gitlab` | GitLab CI merge request annotations |
| `json` | Programmatic consumption |
| `json-lines` | Streaming JSON output |
| `junit` | JUnit XML (for Jenkins, etc.) |
| `pylint` | Pylint-compatible format |
| `sarif` | SARIF (GitHub Code Scanning, etc.) |
| `rdjson` | ReviewDog JSON |
| `azure` | Azure DevOps annotations |
| `grouped` | Grouped by file |

Set via `--output-format` flag or `RUFF_OUTPUT_FORMAT` environment variable.

## Docker

Official image: `ghcr.io/astral-sh/ruff`

```bash
# Latest
docker run -v .:/io --rm ghcr.io/astral-sh/ruff check

# Specific version
docker run -v .:/io --rm ghcr.io/astral-sh/ruff:0.15.18 check

# With SELinux
docker run -v .:/io:Z --rm ghcr.io/astral-sh/ruff check
```

## Exit Codes

- `0` — no issues found (or all fixed)
- `1` — issues found
- `2` — internal error
- With `--exit-non-zero-on-fix` (check) or `--exit-non-zero-on-format` (format): exits non-zero if any files were modified, even if all issues were resolved

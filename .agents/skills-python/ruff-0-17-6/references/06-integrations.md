# Ruff 0.17.6 — Integrations

Contents:
- [Installation (pinned to 0.17.6)](#installation-pinned-to-0176)
- [pre-commit](#pre-commit)
- [GitHub Actions](#github-actions)
- [GitLab CI/CD](#gitlab-cicd)
- [Docker](#docker)
- [Editors — language server](#editors--language-server)
- [CI output formats](#ci-output-formats)

## Installation (pinned to 0.17.6)

```bash
# One-off via uvx (no install)
uvx ruff@0.17.6 check
uvx ruff@0.17.6 format

# Persistent installs
uv tool install ruff@0.17.6     # recommended
pip install ruff==0.17.6
pipx install ruff==0.17.6

# Standalone installers (no Python runtime required)
curl -LsSf https://astral.sh/ruff/0.17.6/install.sh | sh        # macOS/Linux
powershell -c "irm https://astral.sh/ruff/0.17.6/install.ps1 | iex"  # Windows
```

Also available via Homebrew (`brew install ruff`), conda-forge
(`conda install -c conda-forge ruff`), pkgx, Arch (`pacman -S ruff`),
Alpine (`apk add ruff`), and openSUSE Tumbleweed (`python3-ruff`).

## pre-commit

Via [`ruff-pre-commit`](https://github.com/astral-sh/ruff-pre-commit), pinning
the Ruff version in `rev`:

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.17.6
  hooks:
    - id: ruff-check      # linter
    - id: ruff-format     # formatter
```

- Enable fixes: `args: [ --fix ]` on the `ruff-check` hook.
- Skip notebooks: `types_or: [ python, pyi ]` (removes `jupyter`).
- Include Markdown formatting: add `markdown` to `types_or`.
- Hook ordering: with `--fix`, the `ruff-check` hook must come **before**
  `ruff-format` (and before Black/isort/other formatters), since fixes can
  output code that needs reformatting. Without `--fix`, order doesn't matter.

## GitHub Actions

Run Ruff directly with the GitHub annotations output format:

```yaml
- name: Run Ruff
  run: ruff check --output-format=github .
```

Or use the [`ruff-action`](https://github.com/astral-sh/ruff-action) GitHub
Action:

```yaml
- uses: astral-sh/ruff-action@v3
```

`ruff-action` parameters via `with:`:

- `version` — Ruff version to install (default: inferred from
  `pyproject.toml`, falling back to latest)
- `args` — CLI arguments to pass (default: `"check"`)
- `src` — source paths (default: the repository workspace)

Example — `ruff check --select B ./src` with version `0.8.0`:

```yaml
- uses: astral-sh/ruff-action@v3
  with:
    version: 0.8.0
    args: check --select B
    src: "./src"
```

## GitLab CI/CD

Produces a code-quality report compatible with GitLab's code quality report
(parallel check + format diff):

```yaml
.base_ruff:
  stage: build
  interruptible: true
  image:
    name: ghcr.io/astral-sh/ruff:0.17.6-alpine
  before_script:
    - cd $CI_PROJECT_DIR
    - ruff --version

Ruff Check:
  extends: .base_ruff
  script:
    - ruff check --output-format=gitlab --output-file=code-quality-report.json
  artifacts:
    reports:
      codequality: $CI_PROJECT_DIR/code-quality-report.json

Ruff Format:
  extends: .base_ruff
  script:
    - ruff format --diff
```

## Docker

Published as `ghcr.io/astral-sh/ruff`, tagged per release and `latest`:

```bash
docker run -v .:/io --rm ghcr.io/astral-sh/ruff check
docker run -v .:/io --rm ghcr.io/astral-sh/ruff:0.17.6 check
# Podman on SELinux: use :Z on the volume
docker run -v .:/io:Z --rm ghcr.io/astral-sh/ruff check
```

Image variants (each also published with version tags, e.g.
`ruff:0.17.6-alpine`): distroless default; `alpine` / `alpine3.20`;
`debian-slim` / `bookworm-slim`; `debian` / `bookworm` (buildpack-deps).

## Editors — language server

Editor integration is powered by the Ruff language server — a single, common
Rust LSP backend built into the `ruff` CLI, run with `ruff server`, and a
direct replacement for the former `ruff-lsp` package. It was introduced in
beta at v0.4.5 and stabilized in v0.5.3. It provides:

- Ruff diagnostics (linting)
- Code actions to fix diagnostics
- Formatting via the built-in formatter

For features like navigation and autocompletion, the Ruff docs recommend
using the `ty` language server alongside Ruff.

## CI output formats

`--output-format` values: `concise`, `full` (default), `json`, `json-lines`,
`junit`, `grouped`, `github`, `gitlab`, `pylint`, `rdjson`, `azure`, `sarif`.

Use `github` for inline GitHub annotations, `gitlab` (+
`--output-file=code-quality-report.json`) for GitLab code-quality reports,
`junit`/`sarif` for other CI systems. Output can also be written with
`-o/--output-file`, or set via the `RUFF_OUTPUT_FORMAT` / `RUFF_OUTPUT_FILE`
environment variables.

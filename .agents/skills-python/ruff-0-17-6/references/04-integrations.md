# Ruff — Integrations and Installation

## Installation

```bash
# Ephemeral, no install (pinned version)
uvx ruff@0.17.6 check
uvx ruff@0.17.6 format

# uv
uv tool install ruff@latest    # global
uv add --dev ruff              # project dependency

# pip / pipx
pip install ruff
pipx install ruff
```

Standalone installers (since 0.5.0, no Python required):

```bash
curl -LsSf https://astral.sh/ruff/install.sh | sh          # macOS / Linux
powershell -c "irm https://astral.sh/ruff/install.ps1 | iex"  # Windows
# Pinned version (path segment = version):
curl -LsSf https://astral.sh/ruff/0.17.6/install.sh | sh
```

Also available via Homebrew (`brew install ruff`), Conda-forge
(`conda install -c conda-forge ruff`), pkgx, Arch (`pacman -S ruff`), Alpine
(`apk add ruff`), openSUSE Tumbleweed (`zypper install python3-ruff`), and
Docker — `ghcr.io/astral-sh/ruff`, tagged per release plus `latest`:

```bash
docker run -v .:/io --rm ghcr.io/astral-sh/ruff check
docker run -v .:/io --rm ghcr.io/astral-sh/ruff:0.17.6 check
```

## pre-commit

Via [`ruff-pre-commit`](https://github.com/astral-sh/ruff-pre-commit):

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.17.6        # pin the Ruff version
  hooks:
    - id: ruff-check
      args: [ --fix ] # run the linter with auto-fix
    - id: ruff-format # run the formatter
```

For Markdown formatting in pre-commit, add `types_or: [python, pyi, jupyter, markdown]`
to the hook (Markdown is not in the default file types).

## GitHub Actions

Inline step (use `--output-format github` for automatic inline annotations):

```yaml
name: CI
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Ruff
        run: ruff check --output-format=github .
```

Or the ready-made [`ruff-action`](https://github.com/astral-sh/ruff-action):

```yaml
name: Ruff
on: [push, pull_request]
jobs:
  ruff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/ruff-action@v3
```

`ruff-action` runs as a pass-fail test by default but can execute any supported
command; it accepts `with:` parameters including `version` (default: inferred from
`pyproject.toml`, falling back to latest).

## Editors

First-party VS Code extension: [`ruff-vscode`](https://github.com/astral-sh/ruff-vscode).
Other editors are covered in the docs (`docs.astral.sh/ruff/editors`).

## Versioning policy

Ruff does **not** use semver (no stable API yet):

- **Minor** bumps: deprecated options/feature removal, backwards-incompatible
  config changes, stable-rule behavior changes or additions/removals to the
  default set, stable-style formatter changes, EOL Python support drops, rule or
  feature deprecations, safe-fix promotions to stable.
- **Patch** bumps: bug fixes, backwards-compatible new config options, new Python
  version support, preview-mode additions (rules, fixes, file types), deprecations.

New rules land in preview mode for at least one minor release before promotion to
stable; stable rule behavior is not changed significantly in patch versions.

## Release notes — 0.17.6 (2026-11-19)

Patch release. Highlights:

- Preview: fix for `runtime-string-union` (`TC010`) added
  (flake8-type-checking).
- Fixed parenthesized duplicate items handling (`B033`, `RUF068`).
- Fixed false negative for names assigned more than once (`F823`, pyflakes).
- Avoided false positives when a collection is modified in a loop
  (`PLR1733`, `PLR1736`, pylint).
- Fixed syntax error in `useless-finally` fix for inline `try` bodies (`RUF072`).
- Relative imports from `.__future__` treated as ordinary imports.
- `SIM208` fixes no longer add redundant `bool` wrappers.
- `F841` (`unused-variable`) ignores `__traceback_hide__`.
- Performance: in-memory notebook decode, exact qualified-name short-circuit,
  streamed JSON diagnostics.
- Rust toolchain updated to 1.100 (MSRV 1.98) — relevant only when building from
  source; PyPI/Docker installs ship pre-built binaries.

## Where to look

- Docs: https://docs.astral.sh/ruff/ (configuration, settings reference, rules,
  default rules, editors, playground at https://play.ruff.rs/)
- `ruff rule <CODE>` / `ruff rule --all` — explain individual rules
- `ruff linter` — list all supported upstream linters
- `ruff config` — list or describe available configuration options
- `ruff clean` — clear Ruff caches
- `ruff version` — print the version

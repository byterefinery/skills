---
name: black-26-5-1
description: >
  Black 26.5.1 — the uncompromising Python code formatter. Use this skill whenever
  the user mentions black, formatting Python code, black formatting, pyproject.toml
  black config, code style enforcement, or any Python formatting task. Covers
  `uvx black`, `pipx run black`, configuration via pyproject.toml, pre-commit hooks,
  Jupyter notebook formatting, and integration with other tools (isort, Flake8, ruff).
metadata:
  tags:
    - python
    - formatting
    - code-quality
---

# black 26.5.1

## Overview

Black is the uncompromising Python code formatter. It formats entire files in place,
ignoring previous formatting and applying uniform whitespace rules. Style configuration
options are deliberately limited — the goal is to remove formatting debates entirely.

Version 26.5.1 supports Python 3.10 through 3.15, including PEP 798 (unpacking in
comprehensions) and PEP 810 (lazy imports) syntax. It requires Python 3.10+ to run.

Black is invoked via `uvx black` or `pipx run black` — no local installation needed.

## Usage

### Ephemeral execution (recommended)

```bash
# Format files
uvx 'black@26.5.1' src/
uvx 'black@26.5.1' myfile.py

# Check without writing
uvx 'black@26.5.1' --check src/

# Show diff
uvx 'black@26.5.1' --diff src/

# Format a string
uvx 'black@26.5.1' -c "print ( 'hello' )"
```

### With Jupyter notebook support

Black needs the `jupyter` extra to format `.ipynb` files:

```bash
uvx 'black[jupyter]@26.5.1' notebook.ipynb
uvx 'black[jupyter]@26.5.1' .   # formats both .py and .ipynb
```

### pipx (persistent installation)

```bash
pipx run black@26.5.1 src/
pipx install black@26.5.1
black src/
```

### Configuration via pyproject.toml

Black reads `[tool.black]` from `pyproject.toml`, walking up from the target files to
the repo root (`.git` boundary). All CLI options are available as config keys:

```toml
[tool.black]
line-length = 88
target-version = ["py311"]
required-version = "26"
preview = false
skip-string-normalization = false
skip-magic-trailing-comma = false

extend-exclude = '''
(
  ^/migrations/
  | .*_pb2.py
)
'''
```

### Common CLI options

```bash
uvx 'black@26.5.1' --line-length 100 src/          # custom line length
uvx 'black@26.5.1' --target-version py311 src/     # target Python version
uvx 'black@26.5.1' --preview src/                  # preview style
uvx 'black@26.5.1' --skip-string-normalization src/
uvx 'black@26.5.1' --fast src/                     # skip AST safety check
uvx 'black@26.5.1' --no-cache src/                 # bypass cache
uvx 'black@26.5.1' -q src/                         # quiet mode
uvx 'black@26.5.1' -v src/                         # verbose mode
```

### Inline formatting controls

```python
x = 1  # fmt: skip       # skip formatting this line
# fmt: off
unformatted = code
# fmt: on
```

### pre-commit integration

```yaml
repos:
  - repo: https://github.com/psf/black-pre-commit-mirror
    rev: 26.5.1
    hooks:
      - id: black
        language_version: python3.11
```

Use `id: black-jupyter` for Jupyter notebook support. For file exclusions with
pre-commit, use pre-commit's `exclude` key or Black's `force-exclude` in
`pyproject.toml` — standard `--exclude` does not work since pre-commit passes files
directly.

### stdin / stdout

```bash
echo "print ( 'hi' )" | uvx 'black@26.5.1' -
uvx 'black@26.5.1' --stdin-filename foo.py - < foo.py
```

### Exit codes

- `0` — no changes needed (or nothing changed with `--check`)
- `1` — files would be reformatted (with `--check`) or reformatted
- `123` — internal error

## Gotchas

- **`uvx` extras syntax requires quotes** — use `uvx 'black[jupyter]@26.5.1'` not
  `uvx black[jupyter]@26.5.1` (shell interprets brackets as glob). Same applies to
  any package with extras in uvx.

- **`--exclude` ignored by pre-commit** — pre-commit passes files directly to Black,
  bypassing recursive discovery. Use pre-commit's `exclude` key or Black's
  `force-exclude` in `pyproject.toml` instead.

- **`--line-ranges` is single-file only** — cannot be used with multiple files or
  Jupyter notebooks. Mainly for editor "format selection" integrations.

- **`--preview` and `--unstable` are not stable across releases** — code formatted
  with these flags may change between Black versions. Do not enable them for shared
  projects unless you pin the exact Black version with `--required-version`.

- **`--required-version` accepts major version** — `--required-version 26` matches
  any 26.x release, guaranteeing stable formatting per Black's year-based stability
  policy.

- **Black normalizes strings by default** — single quotes become double quotes,
  string prefixes are lowercased. Use `--skip-string-normalization` only as an
  adoption aid for legacy projects, not for new ones.

- **`E203` conflicts with pycodestyle/Flake8** — Black intentionally adds whitespace
  around `:` in complex slices per PEP 8. Disable `E203` in your linter config.

- **Cache location** — Black caches formatted files per-user. Set `BLACK_CACHE_DIR`
  to override. Use `--no-cache` for deterministic CI runs.

- **`--force-exclude` vs `--extend-exclude`** — `--extend-exclude` adds to default
  exclusions; `--force-exclude` applies even to explicitly named files (needed for
  pre-commit and editor plugins).

- **Jupyter cells with magics are skipped** — Black won't format cells containing
  automagics, non-Python cell magics (`%%writefile`), multiline magics, or IPython
  internal calls. Use `--python-cell-magics` to add custom magics to the allowed list.

## References

- [01-code-style](references/01-code-style.md) — Black's formatting rules in detail
- [02-other-tools](references/02-other-tools.md) — isort, Flake8, pycodestyle, Pylint compatibility configs

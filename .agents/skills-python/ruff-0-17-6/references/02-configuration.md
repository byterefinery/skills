# Ruff 0.17.6 — Configuration

Contents:
- [Config files](#config-files)
- [Discovery and precedence](#discovery-and-precedence)
- [Default configuration](#default-configuration)
- [Common settings](#common-settings)
- [Per-file ignores](#per-file-ignores)
- [Plugin and isort settings](#plugin-and-isort-settings)
- [File discovery](#file-discovery)
- [Jupyter notebooks](#jupyter-notebooks)
- [Inferring the Python version](#inferring-the-python-version)

## Config files

Ruff reads configuration from a `pyproject.toml`, `ruff.toml`, or
`.ruff.toml` file. All three implement an equivalent schema; in `ruff.toml`
and `.ruff.toml` the `[tool.ruff]` header and `tool.ruff` section prefix are
omitted. Linter settings live under `[lint]` / `[tool.ruff.lint]`, formatter
settings under `[format]` / `[tool.ruff.format]`.

```toml
# pyproject.toml
[tool.ruff]
line-length = 88

[tool.ruff.lint]
select = ["E", "F"]

[tool.ruff.format]
quote-style = "single"
```

```toml
# ruff.toml (equivalent)
line-length = 88

[lint]
select = ["E", "F"]

[format]
quote-style = "single"
```

## Discovery and precedence

- For each file, Ruff uses the **closest** config file in the directory
  hierarchy; paths inside that config (`exclude` globs, `src`) resolve relative
  to the config file's directory.
- Configs are **not merged** across the hierarchy — parent configs are ignored.
  To inherit another file, use the `extend` field:

  ```toml
  [tool.ruff]
  extend = "../ruff.toml"
  line-length = 100
  ```

- A `pyproject.toml` without a `[tool.ruff]` section is ignored when locating
  the closest config.
- If multiple config files sit in the same directory: `.ruff.toml` >
  `ruff.toml` > `pyproject.toml`.
- A config passed via `--config <path>` applies to **all** analyzed files, with
  relative paths resolved against the current working directory.
- With no config file in the hierarchy, Ruff falls back to a user-level config
  at `${config_dir}/ruff/.ruff.toml`, `${config_dir}/ruff/ruff.toml`, or
  `${config_dir}/ruff/pyproject.toml` (checked in that order), else the built-in
  defaults.
- Any setting provided on the command line (e.g. `--select`) overrides the
  settings in every resolved configuration file.

## Default configuration

If left unspecified, Ruff behaves as if configured with:

```toml
exclude = [
  ".bzr", ".direnv", ".eggs", ".git", ".git-rewrite", ".hg",
  ".ipynb_checkpoints", ".mypy_cache", ".nox", ".pants.d", ".pyenv",
  ".pytest_cache", ".pytype", ".ruff_cache", ".svn", ".tox", ".venv",
  ".vscode", "__pypackages__", "_build", "buck-out", "build", "dist",
  "node_modules", "site-packages", "venv",
]
line-length = 88        # Same as Black
indent-width = 4
target-version = "py311"  # Assume Python 3.11 (overridable/inferable)

[lint]
# select = [...]  # See the Default Rules page for the full listing
ignore = []
fixable = ["ALL"]
unfixable = []
dummy-variable-rgx = "^(_+|(_+[\\p{XID_Continue}]*[\\p{XID_Continue}--_]+?))$"

[format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
docstring-code-format = false
docstring-code-line-length = "dynamic"
```

## Common settings

| Setting | Default | Meaning |
|---|---|---|
| `line-length` | `88` | Max line length (formatter and `E501`) |
| `indent-width` | `4` | Indentation width |
| `target-version` | `py311` | Minimum supported Python (`py37`–`py315`); may be inferred from `requires-python` |
| `exclude` / `extend-exclude` | list above | Path globs omitted from analysis |
| `include` / `extend-include` | default set | Files Ruff discovers (must match files, not directories) |
| `respect-gitignore` | `true` | Skip files ignored by `.ignore`, `.gitignore`, `.git/info/exclude`, global gitignore |
| `force-exclude` | `false` | Enforce exclusions even for paths passed directly on the CLI |
| `extend` | — | Path to a config file whose settings are inherited first |
| `extension` | — | Map custom file extensions to a language (e.g. `{ mdx = "markdown" }`) |

Per-tool scoping: `exclude` under `[lint]` or `[format]` limits exclusion to
that tool only (e.g. format but don't lint `.pyi` files via
`[format] exclude = ["*.pyi"]`).

## Per-file ignores

Ignore specific rules in specific files via path patterns:

```toml
[lint.per-file-ignores]
"__init__.py" = ["E402"]
"**/{tests,docs,tools}/*" = ["E402"]
```

CLI equivalents: `--per-file-ignores` (replace) and `--extend-per-file-ignores`
(add on top).

## Plugin and isort settings

Linter plugin configurations are subsections of `lint`:

```toml
[lint]
extend-select = ["Q"]

[lint.flake8-quotes]
docstring-quotes = "double"
```

Examples of plugin-specific tables: `[lint.isort]` (import sorting:
`force-single-line`, `force-wrap-aliases`, `lines-after-imports`,
`lines-between-types`, `split-on-trailing-comma`, …), `[lint.pydocstyle]`
(`convention = "google"`, …), `[lint.mccabe]`, `[lint.pylint]`, and so on.

## File discovery

- Default inclusions: `*.py`, `*.pyi`, `*.ipynb`, `*.md`, `pyproject.toml`,
  `ruff.toml`, `.ruff.toml`; in preview mode also `*.pyw`.
- `include` paths **must match files** — `include = ["src"]` fails because it
  matches a directory.
- Files passed to Ruff directly are always analyzed, regardless of exclusion
  or gitignore, unless `force-exclude` is enabled.
- `ruff check --show-files` prints the files that would be analyzed with the
  current settings.

## Jupyter notebooks

Notebooks (`.ipynb`) are linted and formatted by default. To lint but not
format them, set `[format] exclude = ["*.ipynb"]`; to format but not lint,
`[lint] exclude = ["*.ipynb"]`; to disable entirely, `extend-exclude =
["*.ipynb"]`. Some rules behave per-cell in notebooks (e.g. `E402`
module-import-not-at-top-of-file applies to each cell); rule docs note when
notebook behavior differs.

## Inferring the Python version

When no discovered configuration sets `target-version`, Ruff infers it from
`requires-python` in a nearby `pyproject.toml`:

1. If a config file is passed directly (`--config`), no inference happens.
2. If a config is found in the directory hierarchy, inference uses the
   `pyproject.toml` in the same directory as that config.
3. With a user-level config, `requires-python` from the first
   `pyproject.toml` in an ancestor of the CWD takes precedence.
4. With no config files at all, inference uses the first `pyproject.toml`
   found in an ancestor of the CWD (behavior may depend on the working
   directory).

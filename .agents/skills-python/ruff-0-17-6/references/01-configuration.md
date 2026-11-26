# Ruff — Configuration

## Config files

Ruff can be configured through a `pyproject.toml`, `ruff.toml`, or `.ruff.toml`
file. All three implement an equivalent schema; in `ruff.toml` and `.ruff.toml` the
`[tool.ruff]` header and `tool.ruff` section prefix are omitted.

## Config file discovery

For each file, Ruff uses the **closest** config file in the directory hierarchy.
Paths in that config file (e.g. `exclude` globs, `src` paths) are resolved relative
to the directory containing it. Ruff does **not** merge settings across config files
— the closest one wins and parent configs are ignored.

Exceptions and details:

- `pyproject.toml` files that lack a `[tool.ruff]` section are ignored when locating
  the closest config.
- Multiple config files in the same directory: `.ruff.toml` > `ruff.toml` > `pyproject.toml`.
- Inheritance is explicit via the `extend` field:

  ```toml
  [tool.ruff]
  extend = "../pyproject.toml"   # inherit parent config
  line-length = 100              # then override
  ```

- A config file passed directly via `--config` is used for **all** analyzed files,
  and relative paths inside it resolve against the *current working directory*.
- With no project config found, Ruff falls back to a user-level config at
  `${config_dir}/ruff/.ruff.toml`, `${config_dir}/ruff/ruff.toml`, or
  `${config_dir}/ruff/pyproject.toml` (first match wins), else built-in defaults.

## Inferring the Python version

When no discovered config sets `target-version`, Ruff infers it from the
`requires-python` field of a nearby `pyproject.toml` (same directory as the found
config, or an ancestor of the CWD when using user-level/no config). Behavior may
differ depending on the working directory from which Ruff is invoked. Set
`target-version` explicitly for reproducibility. Accepted values: `py37` through
`py315`.

## Default configuration

If left unspecified, Ruff's default configuration is equivalent to:

```toml
# pyproject.toml
[tool.ruff]
exclude = [
    ".bzr", ".direnv", ".eggs", ".git", ".git-rewrite", ".hg",
    ".ipynb_checkpoints", ".mypy_cache", ".nox", ".pants.d", ".pyenv",
    ".pytest_cache", ".pytype", ".ruff_cache", ".svn", ".tox", ".venv",
    ".vscode", "__pypackages__", "_build", "buck-out", "build", "dist",
    "node_modules", "site-packages", "venv",
]
line-length = 88
indent-width = 4
target-version = "py311"

[tool.ruff.lint]
# select = [...]   # default rule set, see the Default Rules page
ignore = []
fixable = ["ALL"]
unfixable = []
dummy-variable-rgx = "^(_+|(_+[\\p{XID_Continue}]*[\\p{XID_Continue}--_]+?))$"

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
docstring-code-format = false
docstring-code-line-length = "dynamic"
```

## Linter settings

Rule enablement/disabling: `lint.select`, `lint.extend-select`, `lint.ignore`
(plus CLI `--select` / `--extend-select` / `--ignore`). Selectors accept full codes
(`F401`), prefixes (`F`), linter groups, or `ALL`.

Recommended guidelines from the docs:

- Prefer `select` over `extend-select` to make the rule set explicit.
- Use `ALL` with discretion — it implicitly enables new rules on upgrade.
- Start small (`select = ["E", "F"]`) and add groups one at a time (e.g. `B` for
  flake8-bugbear, `UP` for pyupgrade, `SIM` for flake8-simplify, `I` for isort).

A popular non-pedantic selection:

```toml
[tool.ruff.lint]
select = ["E", "F", "UP", "B", "SIM", "I"]
```

Fix control: `lint.fixable`, `lint.unfixable`, `lint.extend-fixable`,
`lint.extend-unfixable`, plus `lint.extend-safe-fixes` / `lint.extend-unsafe-fixes`
for per-rule fix-safety overrides (prefixes allowed).

Per-file ignores via glob patterns:

```toml
[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["E402"]
"**/{tests,docs,tools}/*" = ["E402"]
```

Linter plugin options are subsections under `lint`:

```toml
[tool.ruff.lint]
extend-select = ["Q"]

[tool.ruff.lint.flake8-quotes]
docstring-quotes = "double"
```

## Preview mode

`preview = true` (top-level, `lint.preview`, or `format.preview`) enables unstable
rules, fixes, and formatter style changes. Preview rules only activate when preview
is enabled, even when selected by exact code. `explicit-preview-rules = true`
requires each preview rule to be selected individually. Deprecated rules are
disabled (and error if explicitly selected) under preview.

## Command line

Dedicated flags cover rule enablement, file discovery, logging, etc. Any other
setting can be overridden with `--config` as a TOML `KEY = VALUE` pair:

```console
$ ruff check path/to/file --config "lint.dummy-variable-rgx = '__.*'"
$ ruff format path/to/file --config "format.quote-style = 'single'"
$ ruff check path --config path/to/ruff.toml   # or point at a file
```

- `lint.` / `format.` prefixes are required inside `--config` pairs.
- A dedicated flag beats a `--config` override for the same setting
  (`--line-length 90 --config "line-length = 100"` → 90).
- `--config` pairs override settings from *all* discovered config files.
- `--isolated` ignores all configuration files.
- Global options: `--color <auto|always|never>`, `-v` / `-q` / `-s` log levels.

### Argfiles

`@path/to/args.txt` reads arguments from a file (one per line; flags and paths both
work). If a path including the leading `@` exists on disk, it is treated literally.

## File discovery

Default discovery set: `*.py`, `*.pyi`, `*.ipynb`, `*.md`, `pyproject.toml`,
`ruff.toml`, `.ruff.toml` (plus `*.pyw` in preview mode). Custom extensions via
`extension` mappings, e.g. `extension = { mdx = "markdown", qmd = "markdown" }`;
additional extensions via `extend-include` / `include` (paths in `include` must
match files, not directories).

- `.gitignore`, `.ignore`, `.git/info/exclude`, and global gitignore files are
  respected during recursive discovery (`--no-respect-gitignore` to disable).
- Files passed directly are always analyzed, unless `--force-exclude` is enabled.
- Tool-scoped exclusions: `[tool.ruff.format] exclude = [...]` or
  `[tool.ruff.lint] exclude = [...]`.
- `ruff check --show-files` prints the files Ruff will run against;
  `--show-settings` prints the resolved settings for a file.

## Jupyter notebooks

Notebooks are linted and formatted by default (since 0.6.0). To keep one and drop
the other, scope the exclusion:

```toml
# lint only (no notebook formatting)
[tool.ruff.format]
exclude = ["*.ipynb"]
```

Some rules behave differently in notebooks (e.g. `E402` applies per cell); rule
docs note this when it occurs.

## Shell autocompletion

`ruff generate-shell-completion <SHELL>` for `bash`, `zsh`, `fish`, `elvish`,
`fig`, or `powershell`, e.g.
`echo 'eval "$(ruff generate-shell-completion zsh)"' >> ~/.zshrc`.

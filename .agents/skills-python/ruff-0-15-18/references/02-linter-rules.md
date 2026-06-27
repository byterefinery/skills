# Linter Rules

## Rule Code Format

Each rule has a code like `F401` — a 1–3 letter prefix (linter source) followed by 3 digits. Select rules by full code (`F401`) or prefix (`F` for all Pyflakes rules).

## Major Rule Categories

### Default rules (always enabled)

- **`E4`, `E7`, `E9`** — pycodestyle errors (syntax errors, tab errors, etc.)
- **`F`** — Pyflakes (unused imports, undefined names, etc.)

Note: pycodestyle warnings (`W`) and McCabe complexity (`C901`) are **not** enabled by default.

### Popular rule categories

| Prefix | Linter | Description |
|---|---|---|
| `E` | pycodestyle | Error-level style violations |
| `W` | pycodestyle | Warning-level style violations (e.g., line length) |
| `F` | Pyflakes | Logical errors (unused imports, undefined names) |
| `B` | flake8-bugbear | Common bugs and design issues |
| `C4` | flake8-comprehensions | Unnecessary list/dict/set comprehensions |
| `SIM` | flake8-simplify | Code simplifications |
| `UP` | pyupgrade | Modernize Python syntax |
| `I` | isort | Import sorting |
| `ANN` | flake8-annotations | Missing type annotations |
| `S` | flake8-bandit | Security issues |
| `N` | pep8-naming | Naming convention violations |
| `D` | pydocstyle | Docstring style |
| `PL` | Pylint | Pylint rules |
| `RUF` | Ruff-specific | Ruff-native rules |

### Full linter list

Use `ruff linter` to see all 30+ supported upstream linters, including:
Airflow, eradicate, FastAPI, flake8-2020, flake8-annotations, flake8-async,
flake8-bandit, flake8-blind-except, flake8-boolean-trap, flake8-bugbear,
flake8-builtins, flake8-commas, flake8-comprehensions, flake8-copyright,
flake8-datetimez, flake8-debugger, flake8-django, flake8-errmsg,
flake8-executable, flake8-fixme, flake8-future-annotations, flake8-gettext,
flake8-implicit-str-concat, flake8-import-conventions, flake8-logging,
flake8-logging-format, flake8-no-pep420, flake8-pie, flake8-print,
flake8-pyi, flake8-pytest-style, flake8-quotes, flake8-raise,
flake8-return, flake8-self, flake8-simplify, flake8-slots,
flake8-tidy-imports, flake8-todos, flake8-type-checking,
flake8-unused-arguments, flake8-use-pathlib, flynt, isort, mccabe,
NumPy-specific, pandas-vet, pep8-naming, Perflint, pycodestyle.

## Rule Selection Strategies

### Strategy 1: Explicit select (recommended)

```toml
[tool.ruff.lint]
select = ["E", "F", "B", "UP", "SIM", "I"]
ignore = ["E501"]
```

Makes the rule set explicit and reproducible. Preferred approach.

### Strategy 2: Extend defaults

```toml
[tool.ruff.lint]
extend-select = ["B", "UP", "SIM", "I"]
```

Adds rules on top of the default `E4`, `E7`, `E9`, `F` set.

### Strategy 3: ALL with ignore (use cautiously)

```toml
[tool.ruff.lint]
select = ["ALL"]
ignore = ["D", "ANN", "S"]
```

Enables everything then disables noisy categories. New rules added in future ruff versions will automatically be enabled.

## Fix Behavior

Ruff classifies fixes as **safe** or **unsafe**:

- **Safe fixes** — guaranteed to preserve semantics (e.g., removing unused imports). Applied with `--fix`.
- **Unsafe fixes** — may change behavior (e.g., refactoring control flow). Require `--unsafe-fixes`.

### Fix controls

```toml
[tool.ruff.lint]
fixable = ["ALL"]    # Which rules CAN be fixed (default: ALL)
unfixable = ["B"]    # Which rules should NOT be auto-fixed
```

### Common fix patterns

- `F401` (unused-import) — removes the import; safe except in `__init__.py`
- `UP006` (useless-object-inheritance) — removes `(object)` from class definitions
- `I001` (unsorted-imports) — reorders imports
- `SIM` rules — may refactor expressions (check with `--diff`)

## Exploring Rules

```bash
# Explain a specific rule
ruff rule F401

# List all rules
ruff rule --all

# Show resolved settings for a file
ruff check --show-settings path/to/file.py

# Show which files will be checked
ruff check --show-files
```

## Preview Rules

Preview rules are unstable and require explicit opt-in:

```toml
[tool.ruff.lint]
preview = true
extend-select = ["NEW001"]   # Only works if preview is enabled
```

Or via CLI: `ruff check --preview`.

## Noqa Comments

Inline suppression with comments:

```python
import os  # noqa: F401
import sys  # noqa

# Multi-line suppression
# ruff: noqa: E501
very_long_line_that_exceeds_the_default_line_length_limit_of_eighty_eight_characters = True

# Block suppression
# ruff: noqa: F401
import unused_module_a
import unused_module_b
# ruff: enable: F401
```

Auto-add noqa directives: `ruff check --add-noqa`.

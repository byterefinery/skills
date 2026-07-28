# Rule Categories

Ruff organizes its 800+ lint rules into categories identified by one-to-three letter
prefixes. Each category maps to a source linter or a Ruff-native rule set.

## Core rule categories

| Prefix | Source | Description |
|--------|--------|-------------|
| `E` | pycodestyle | Error rules (indentation, whitespace, syntax) |
| `W` | pycodestyle | Warning rules (line length, trailing whitespace) |
| `F` | Pyflakes | Unused imports, undefined names, syntax errors |
| `C90` | McCabe | Cyclomatic complexity |

## Popular Flake8 plugin replacements

| Prefix | Source | Description |
|--------|--------|-------------|
| `B` | flake8-bugbear | Common bugs and design issues |
| `ANN` | flake8-annotations | Missing type annotations |
| `S` | flake8-bandit | Security issues |
| `SIM` | flake8-simplify | Code simplification opportunities |
| `COM` | flake8-commas | Trailing comma enforcement |
| `CPY` | flake8-copyright | Missing copyright notices |
| `DTZ` | flake8-datetimez | Naive datetime usage |
| `T10` | flake8-debugger | Debugger statements |
| `DJ` | flake8-django | Django-specific rules |
| `EM` | flake8-errmsg | Error message formatting |
| `EXE` | flake8-executable | Executable file issues |
| `ISC` | flake8-implicit-str-concat | Implicit string concatenation |
| `IC` | flake8-import-conventions | Import aliasing conventions |
| `LOG` | flake8-logging | Logging format issues |
| `G` | flake8-logging-format | Logging format string issues |
| `INP` | flake8-no-pep420 | Implicit namespace packages |
| `PIE` | flake8-pie | Miscellaneous improvements |
| `T20` | flake8-print | print() and pprint() calls |
| `PYI` | flake8-pyi | .pyi stub file rules |
| `PT` | flake8-pytest-style | pytest style rules |
| `Q` | flake8-quotes | Quote style enforcement |
| `RSE` | flake8-raise | raise statement issues |
| `RET` | flake8-return | return statement simplification |
| `SLF` | flake8-self | self/cls argument issues |
| `SG` | flake8-strings | String formatting issues |
| `INT` | flake8-indent | Indentation issues |
| `FURB` | refurb | Code modernization |
| `RSE` | flake8-raise | raise statement issues |
| `SLF` | flake8-self | self/cls argument issues |
| `SIM` | flake8-simplify | Code simplification |
| `RUF` | Ruff-native | Ruff-specific rules |
| `TRY` | tryceratops | try/except improvements |
| `PD` | pandas-vet | pandas usage rules |
| `PLE` | Pylint (error) | Pylint error rules |
| `PLW` | Pylint (warning) | Pylint warning rules |
| `PLR` | Pylint (refactor) | Pylint refactor rules |
| `PLC` | Pylint (convention) | Pylint convention rules |
| `PLN` | Pylint (namespace) | Pylint namespace rules |
| `FLY` | flynt | f-string conversion |
| `PERF` | perflint | Performance issues |
| `A` | flake8-builtins | Shadowing Python builtins |
| `FBT` | flake8-boolean-trap | Boolean default arguments |
| `FAST` | flake8-async | Async function issues |
| `EM` | flake8-errmsg | Error message rules |
| `EXE` | flake8-executable | Executable file rules |
| `ISC` | flake8-implicit-str-concat | Implicit string concat |
| `ICN` | flake8-import-conventions | Import conventions |
| `LOG` | flake8-logging | Logging rules |
| `PGH` | pygrep-hooks | pygrep rules |
| `PIE` | flake8-pie | Miscellaneous rules |
| `T20` | flake8-print | print/pprint calls |
| `PYI` | flake8-pyi | .pyi stub rules |
| `PT` | flake8-pytest-style | pytest rules |
| `Q` | flake8-quotes | Quote style |
| `RSE` | flake8-raise | raise issues |
| `RET` | flake8-return | return simplification |
| `SLF` | flake8-self | self/cls issues |
| `SLOT` | flake8-slots | __slots__ usage |
| `SIM` | flake8-simplify | Simplification |
| `TCH` | flake8-type-checking | Type checking imports |
| `TID` | flake8-tidy-imports | Tidy import rules |
| `TRY` | tryceratops | try/except rules |
| `UP` | pyupgrade | Modern Python syntax |
| `YTT` | flake8-2020 | Python 2/3 porting |
| `ERA` | eradicate | Commented-out code |
| `PD` | pandas-vet | pandas rules |
| `NPY` | NumPy-specific | NumPy rules |
| `FAST` | flake8-async | async rules |
| `RUF` | Ruff-native | Ruff-specific rules |
| `FA` | flake8-annotations | Future annotations |
| `ASYNC` | flake8-async | Async rules |
| `BLE` | flake8-blind-except | Blind except clauses |
| `DTZ` | flake8-datetimez | datetime rules |
| `FIX` | flake8-fixme | FIXME/TODO comments |
| `G` | flake8-logging-format | Logging format |
| `ISC` | flake8-implicit-str-concat | String concat |
| `ICN` | flake8-import-conventions | Import conventions |
| `IC001` | flake8-import-conventions | Incorrect import type |
| `IC002` | flake8-import-conventions | Banned import |
| `IC003` | flake8-import-conventions | Import alias inconsistency |
| `PGH` | pygrep-hooks | pygrep rules |
| `PIE` | flake8-pie | Miscellaneous |
| `T20` | flake8-print | print/pprint |
| `PYI` | flake8-pyi | .pyi stub |
| `PT` | flake8-pytest-style | pytest |
| `Q` | flake8-quotes | Quotes |
| `RSE` | flake8-raise | raise |
| `RET` | flake8-return | return |
| `SLF` | flake8-self | self/cls |
| `SLOT` | flake8-slots | __slots__ |
| `SIM` | flake8-simplify | Simplification |
| `TCH` | flake8-type-checking | Type checking |
| `TID` | flake8-tidy-imports | Tidy imports |
| `TRY` | tryceratops | try/except |
| `UP` | pyupgrade | Modern syntax |
| `YTT` | flake8-2020 | Py2/3 porting |
| `ERA` | eradicate | Commented code |
| `PD` | pandas-vet | pandas |
| `NPY` | NumPy | NumPy-specific |
| `PERF` | perflint | Performance |
| `FURB` | refurb | Modernization |
| `RUF` | Ruff-native | Ruff-specific |

## Selecting rules

### Enable by prefix

```toml
[tool.ruff.lint]
select = ["E", "F", "B", "UP", "I"]
```

### Enable by sub-prefix (partial match)

```toml
select = ["E4", "E7", "E9", "F"]  # Only E4xx, E7xx, E9xx + all F
```

### Enable all rules

```toml
select = ["ALL"]
```

Ruff auto-disables conflicting pydocstyle rules when `ALL` is used.

### Add rules to defaults

```toml
extend-select = ["B", "UP"]  # Adds B and UP to default E4, E7, E9, F
```

### Ignore specific rules

```toml
ignore = ["E501", "B008"]
```

### Per-file ignores

```toml
[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["E402", "F401"]
"tests/**" = ["S101"]
"migrations/**" = ["ALL"]
```

## Fix safety

Ruff classifies fixes as safe or unsafe:

- **Safe fixes** — applied with `--fix`. Meaning and behavior are preserved.
- **Unsafe fixes** — require `--unsafe-fixes`. May change behavior (e.g., exception
  type changes, import reordering that affects side effects).

Control fixability:

```toml
[tool.ruff.lint]
fixable = ["ALL"]     # Which rules CAN be auto-fixed
unfixable = ["B"]     # Which rules should NOT be auto-fixed
```

## Viewing rules

```bash
ruff rule F401                    # Show details for a specific rule
ruff rule F401 --output-format json  # JSON output
ruff linter                       # List all rule categories
```

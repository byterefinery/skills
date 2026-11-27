# Ruff 0.17.6 — Rules

Contents:
- [Rule codes and selectors](#rule-codes-and-selectors)
- [Default rule set](#default-rule-set)
- [Selection semantics and precedence](#selection-semantics-and-precedence)
- [Linter groups](#linter-groups)
- [Rule categories](#rule-categories)
- [Preview rules](#preview-rules)
- [Explaining rules](#explaining-rules)
- [Rule changes in 0.17.6](#rule-changes-in-0176)

## Rule codes and selectors

Ruff uses Flake8-style rule codes: an alphabetic prefix followed by digits
(e.g. `F401`). The prefix indicates the source (e.g. `F` = Pyflakes, `E` =
pycodestyle, `ANN` = flake8-annotations).

Selectors (`select`, `extend-select`, `ignore`, `fixable`, …) accept either a
full rule code (`F401`) or any valid prefix (`F`). The special code `ALL`
enables all rules; when `ALL` is enabled, Ruff automatically disables
conflicting rules (e.g. `D203` and `D211` represent alternative docstring
formats).

In preview mode, selectors also accept human-readable rule names (e.g.
`unused-import`) in addition to codes.

## Default rule set

The default set is a great starting point for a new project: it catches a wide
variety of common errors (unused imports, undefined names, bare excepts, …)
with zero configuration. By default Ruff enables rules from the `F`, `E`, `B`,
`UP`, and `RUF` groups "as well as many more", omitting stylistic rules that
overlap with a formatter like `ruff format` or Black. The complete default
listing is published on the Default Rules page of the Ruff docs (and generated
from `DEFAULT_SELECTORS` in the source).

## Selection semantics and precedence

- `select` **replaces** the default rule set; `extend-select` **adds** to it;
  `ignore` removes rules from whatever was selected.
- Ruff reconciles `select`/`extend-select`/`ignore` from multiple sources
  (current config, inherited configs, CLI) by using the **highest-priority
  `select`** as the basis, then applying `extend-select` and `ignore`. CLI
  options outrank config-file options; the current config outranks inherited
  ones. Example: with `select = ["E", "F"]`, `ignore = ["F401"]` in the config:
  - `ruff check --select F401` → only `F401` is enforced.
  - `ruff check --extend-select B` → `E`, `F`, `B` enforced, except `F401`.
- Selector precedence within one configuration, broadest to narrowest:

  ```text
  ALL < category < linter group < linter prefix < rule
  ```

  so `select = ["E", "F"]` plus `ignore = ["F401"]` selects all `E`/`F` rules
  except `F401`.

Recommended approach: prefer explicit `select` over `extend-select` for a
deterministic rule set; start small (`select = ["E", "F"]`) and add groups
(`B` = flake8-bugbear, `SIM`, `I`, `UP`, …) at a time; use `ALL` with
discretion since new rules are enabled automatically on upgrades.

## Linter groups

The 59 supported linter groups and their rule-code prefixes (from the Ruff
source registry):

| Prefix | Linter | Prefix | Linter |
|---|---|---|---|
| `A` | flake8-builtins | `I` | isort |
| `AIR` | Airflow | `INT` | flake8-gettext |
| `ANN` | flake8-annotations | `ISC` | flake8-implicit-str-concat |
| `ARG` | flake8-unused-arguments | `LOG` | flake8-logging |
| `ASYNC` | flake8-async | `N` | pep8-naming |
| `B` | flake8-bugbear | `NPY` | Numpy |
| `BLE` | flake8-blind-except | `PD` | pandas-vet |
| `C4` | flake8-comprehensions | `PERF` | Perflint |
| `C90` | mccabe | `PGH` | pygrep-hooks |
| `COM` | flake8-commas | `PIE` | flake8-pie |
| `CPY` | flake8-copyright | `PL` | Pylint |
| `D` | pydocstyle | `PTH` | flake8-use-pathlib |
| `DJ` | flake8-django | `PT` | flake8-pytest-style |
| `DOC` | pydoclint | `PYI` | flake8-pyi |
| `DTZ` | flake8-datetimez | `Q` | flake8-quotes |
| `E`, `W` | pycodestyle | `RET` | flake8-return |
| `EM` | flake8-errmsg | `RSE` | flake8-raise |
| `ERA` | eradicate | `RUF` | Ruff |
| `EXE` | flake8-executable | `S` | flake8-bandit |
| `F` | Pyflakes | `SIM` | flake8-simplify |
| `FA` | flake8-future-annotations | `SLF` | flake8-self |
| `FAST` | FastAPI | `SLOT` | flake8-slots |
| `FBT` | flake8-boolean-trap | `TC` | flake8-type-checking |
| `FIX` | flake8-fixme | `TD` | flake8-todos |
| `FLY` | flynt | `T10` | flake8-debugger |
| `FURB` | refurb | `T20` | flake8-print |
| `G` | flake8-logging-format | `TID` | flake8-tidy-imports |
| `ICN` | flake8-import-conventions | `TRY` | tryceratops |
| `INP` | flake8-no-pep420 | `UP` | pyupgrade |
|  |  | `YTT` | flake8-2020 |

Run `ruff linter` to list the supported upstream linters, and
`ruff rule <CODE>` to explain an individual rule.

## Rule categories

In preview, rules are additionally organized into categories (decreasing
severity), which determine default enablement:

- **Correctness** — code that is outright wrong as written; fix rather than suppress
- **Suspicious** — likely wrong, but sometimes intentional; deprecations live here
- **Complexity** — simpler equivalent exists, same semantics
- **Performance** — more efficient equivalent, same semantics
- **Style** — broadly accepted idioms
- **Security** — potential vulnerabilities; biased toward false positives
- **Formatting** — overlaps with a code formatter
- **Pedantic** — too opinionated/noisy for the other style buckets
- **Restriction** — arbitrarily restricts features (e.g. `print` = `T201`, `assert` = `S101`)

The first five compose the default rule set (with `preview = true`):

```toml
[lint]
preview = true
select = ["correctness", "suspicious", "complexity", "performance", "style"]
```

`security`, `formatting`, `pedantic`, `restriction` are off by default. Enable
`security` wholesale for security-conscious projects; pick individual rules
from the other three. Categories mix freely with prefixes, groups, and codes
(precedence: `ALL < category < group < prefix < rule`).

## Preview rules

- A rule in preview is only selectable when preview mode is enabled
  (`preview = true` in config, or `--preview`); selecting its code, prefix, or
  `ALL` without preview mode does nothing.
- `explicit-preview-rules = true` (with preview on) requires selecting each
  preview rule by its exact code (e.g. `--select ALL,HYP001`) instead of via
  category/prefix.
- With preview enabled, deprecated rules are disabled; explicitly selecting one
  is an error.

## Explaining rules

- `ruff rule <CODE>` — explain a single rule (message, fix availability, examples)
- `ruff rule` — explain all rules
- `ruff config` — list or describe configuration options
- Online, the rules reference (docs.astral.sh/ruff) lists every rule with its
  category, fix safety, and examples; the Default Rules page lists the
  zero-config rule set.

## Rule changes in 0.17.6

From the 0.17.6 changelog (released 2026-11-19):

- `flake8-type-checking`: new fix for `runtime-string-union` (`TC010`) (preview)
- `pyflakes`: `F823` false negative fixed when a name is assigned more than once
- `pylint`: `PLR1733`/`PLR1736` false positive avoided when a collection is modified in a loop
- `ruff`: `RUF072` (`useless-finally`) fix no longer produces a syntax error for inline `try` bodies
- `flake8-simplify`: `SIM208` fixes no longer add redundant `bool` wrappers
- `pyflakes`: `F841` (`unused-variable`) now ignores `__traceback_hide__`
- `B033`/`RUF068`: handling of parenthesized duplicate items fixed
- Relative imports from `__future__` are treated as ordinary imports

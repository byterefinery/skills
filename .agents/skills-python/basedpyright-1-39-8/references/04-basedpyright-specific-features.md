# basedpyright-Specific Features Reference

## Better Defaults

### `typeCheckingMode` defaults to `"recommended"`

Upstream pyright defaults to `"basic"`. basedpyright defaults to `"recommended"`, which enables all diagnostic rules. Less severe rules are warnings, and `failOnWarnings: true` ensures the CLI exits non-zero on any warning.

To match pyright's behavior:
```json
{ "typeCheckingMode": "basic", "failOnWarnings": false }
```

### `pythonPlatform` defaults to `"All"`

basedpyright assumes your code runs on any OS, catching platform-specific type issues earlier. Override if your code is truly platform-specific.

### Auto-detect `.venv`

If neither `pythonPath` nor `venvPath`/`venv` are set, basedpyright checks for `.venv` at the project root and uses its Python interpreter. This matches the convention used by uv, pip-tools, and most modern Python tooling.

### `typeCheckingMode: "off"` is truly off

In pyright, `"off"` still reports some rules as warnings. In basedpyright, `"off"` disables all diagnostic rules (syntax/semantic errors still reported).

### Invalid config exits with code 3

Typos in config keys cause a hard failure instead of being silently ignored. This prevents misconfiguration from going undetected.

## Baseline Support

Baseline allows adopting strict checks incrementally by tracking existing errors in a file, so only new/modified code generates reports.

### Creating a baseline

```bash
basedpyright --writebaseline
```

Generates `.basedpyright/baseline.json`. Commit this file to the repository.

### How it works

Each baselined error is matched by:
- File path (relative to project root)
- Diagnostic rule name
- Column position (not line, so adding/removing lines doesn't resurface errors)

### Auto-updates

When errors are fixed, the baseline file is automatically updated to remove them. No manual intervention needed.

Manual update needed when:
- A baselined error incorrectly resurfaces after moving code
- Enabling a new diagnostic rule and wanting to baseline its existing errors

### Baseline modes in CI

| Context | Default behavior |
|---------|-----------------|
| Local (no `--writebaseline`) | `auto` — updates only when errors decrease |
| CI (no `--writebaseline`) | `lock` — never writes, exits non-zero if baseline needs updating |
| With `--writebaseline` | Always updates baseline |

```bash
# Force auto mode in CI
basedpyright --baselinemode=auto

# Lock mode locally
basedpyright --baselinemode=lock

# Read-only (never update)
basedpyright --baselinemode=discard
```

## New Diagnostic Rules

### `reportAny`

Catches all expressions typed as `Any`, including explicit `Any` that older `reportUnknown*` rules miss:

```python
def foo(baz: Any) -> Any:
    print(baz)  # error: reportAny
```

Use `allowedUntypedLibraries` to suppress for specific modules.

### `reportExplicitAny`

Bans direct use of the `Any` type in annotations:

```python
def foo(baz: Any) -> Any:  # error: reportExplicitAny
    print(baz)  # error: reportAny
```

### `reportIgnoreCommentWithoutRule`

Requires specifying a rule in `# pyright: ignore` comments:

```python
x = foo()  # pyright: ignore[reportUnknownVariableType]  # good
x = foo()  # pyright: ignore  # error: reportIgnoreCommentWithoutRule
```

### `reportPrivateLocalImportUsage`

Like `reportPrivateImportUsage` but checks your own code. Re-export with redundant alias:

```python
# module.py
from .internal import _helper as _helper  # explicit re-export

# consumer.py
from module import _helper  # no error (explicitly re-exported)
```

### `reportImplicitRelativeImport`

Catches imports that work as scripts but break when imported as modules:

```python
# ./pkg/bar.py:
import foo  # error — should be `from . import foo` or `from pkg import foo`
```

### `reportInvalidCast`

Flags casts to non-overlapping types:

```python
foo: int
cast(str, foo)  # error: reportInvalidCast — int and str don't overlap
```

Note: `dict` → `TypedDict` casts trigger this because type checkers treat them as unrelated.

### `reportUnsafeMultipleInheritance`

Bans multiple inheritance when base classes have `__init__`/`__new__`, since constructors may not be called correctly:

```python
class Foo:
    def __init__(self):
        super().__init__()

class Bar:
    def __init__(self): ...

class Baz(Foo, Bar): ...  # error: reportUnsafeMultipleInheritance
Baz()  # Bar.__init__ may never be called or called with wrong args
```

### `reportUnusedParameter`

Configurable rule for unused function parameters (pyright only greys them out as hints):

```python
def print_value(value: str):  # error: reportUnusedParameter
    print("something else")
```

### `reportImplicitAbstractClass`

Requires explicit `ABC` declaration when a class is implicitly abstract:

```python
class FooImpl(AbstractFoo):  # error — must also extend ABC
    def bar(self): ...

class FooImpl(AbstractFoo, ABC):  # ok — explicitly abstract
    def bar(self): ...
```

### `reportEmptyAbstractUsage`

Flags instantiation of classes that extend `ABC` but have no abstract methods:

```python
class AbstractFoo(ABC):  # no abstract methods
    pass

foo = AbstractFoo()  # error: reportEmptyAbstractUsage
```

### `reportIncompatibleUnannotatedOverride`

Catches incompatible overrides when the base class attribute lacks a type annotation:

```python
class A:
    value = 1  # inferred as int

class B(A):
    value = None  # error: reportIncompatibleUnannotatedOverride
```

### `reportUnannotatedClassAttribute`

Requires type annotations on class attributes that can be overridden:

```python
class A:
    value = 1  # error: reportUnannotatedClassAttribute
```

### `reportInvalidAbstractMethod`

Flags `@abstractmethod` on non-abstract classes:

```python
from abc import abstractmethod

class Foo:  # not abstract (doesn't extend ABC)
    @abstractmethod  # error: reportInvalidAbstractMethod
    def foo(): ...

_ = Foo()  # no runtime error — the decorator is silently ignored!
```

### `reportSelfClsDefault`

Flags default values on `self`/`cls`:

```python
class Foo:
    def foo(self=1): ...  # error: reportSelfClsDefault
```

## Improved Existing Rules

### `reportRedeclaration` and `reportDuplicateImport`

basedpyright always reports redeclarations, even with the same type:

```python
foo: int = 1
foo: int = 2  # error in basedpyright (not in pyright)

from foo import bar
from bar import bar  # error — duplicate name
```

### `reportUnreachable`

basedpyright's version reports unreachable code from `sys.version_info` and `sys.platform` checks, which pyright skips. This catches code that won't be type-checked:

```python
if sys.version_info < (3, 13):
    1 + ""  # error in basedpyright — this code isn't type-checked!
```

### `reportInvalidTypeVarUse`

basedpyright correctly handles TypeVars used only in return position:

```python
def empty_list[T]() -> list[T]:  # no error — valid
    return []

def fn[T]() -> T:  # error — suggests `Never`, not `object`
    ...
```

## `strictGenericNarrowing`

When enabled, `isinstance` checks narrow generics to their bound/constraint instead of `Unknown`:

```python
class Foo[T_co: object](Generic[T_co]): ...

def foo(value: object):
    if isinstance(value, Foo):
        reveal_type(value)  # Foo[object] (not Foo[Unknown])
```

For constrained generics, creates a union of all possibilities:

```python
class Foo[T: (int, str)]: ...

if isinstance(value, Foo):
    reveal_type(value)  # Foo[int] | Foo[str]
```

## `dataclass_transform` Extensions

With `enableBasedFeatures: true`, extra `dataclass_transform` options are supported:

```python
from typing import dataclass_transform

@dataclass_transform(skip_replace=True, frozen_default=True)
def frozen[T: type](t: T) -> T:
    return dataclass(frozen=True, slots=True)(t)

# Enables covariance (skip_replace prevents __replace__ from interfering)
@frozen
class Box[T]:
    value: T

box1: Box[str] = Box("test")
box2: Box[str | int] = box1  # ok — covariant
```

## Pylance Features (Now Open Source)

These features were exclusive to Microsoft's closed-source Pylance extension and are now available in basedpyright for all LSP clients:

### Jupyter Notebook Support

Type-check `.ipynb` files via CLI and language server:

```bash
basedpyright
# project/notebook.ipynb - cell 1
#   error: Type "Literal['']" is not assignable to declared type "int"
```

### Import Suggestion Code Actions

Quick-fix actions to add missing imports (not just autocomplete suggestions).

### `# pyright: ignore` Code Actions

Quick-fix to add targeted ignore comments (not `# type: ignore`).

### Semantic Highlighting

- `type` keyword (Python 3.12+)
- `Final` variables colored as read-only
- Improved distinction between types and values

### Inlay Hints

Configurable inlay hints with double-click to insert:
- Variable types
- Call argument names
- Function return types
- Generic type parameters
- Works on `Callable` types (unlike Pylance)

### Docstrings for Compiled Builtins

basedpyright includes scraped docstrings for compiled builtin modules across all Python versions and platforms using [docify](https://github.com/atoerien/docify).

To add docstrings to your own stubs:
```bash
python -m docify path/to/stubs --in-place
```

### Additional Features

- **Enum completions** — autocomplete for enum values
- **Literal completions** — completions for `Literal[int]`, `Literal[bool]`, not just `Literal[str]`
- **Auto `@override` decorator** — autocomplete suggestions include `@override` for method overrides
- **Deprecated completions** — strikethrough on deprecated symbols in completion lists
- **Package/module renaming** — rename updates all import usages
- **Multi-line docstring parameters** — full parameter descriptions shown on hover
- **Auto f-string conversion** — typing `{` inside a string auto-inserts `f` prefix
- **Operator hover and go-to-definition** — hover on `+`, `-`, etc. shows the dunder method
- **Go to implementations** — find all implementations of a method

## CI Integration

### GitHub Actions

basedpyright automatically detects GitHub Actions and uses [workflow commands](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-gh-actions) to annotate PR diffs:

```yaml
jobs:
  check:
    steps:
      - run: basedpyright  # automatic PR annotations, no extra config
```

### GitLab Code Quality Reports

```yaml
basedpyright:
  script: basedpyright --gitlabcodequality report.json
  artifacts:
    reports:
      codequality: report.json
```

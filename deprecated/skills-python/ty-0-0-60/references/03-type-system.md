# Type System

## Redeclarations

ty allows reusing the same symbol with a different type within a scope:

```python
def split_paths(paths: str) -> list[Path]:
    paths: list[str] = paths.split(":")  # paths redeclared as list[str]
    return [Path(p) for p in paths]
```

This is designed for adoption — it allows gradual typing without requiring
intermediate variables.

## Intersection types

ty has first-class support for intersection types. Unlike `A | B` (union: either A or B),
`A & B` (intersection: both A and B).

### Type narrowing via `isinstance`

```python
def output_as_json(obj: Serializable) -> str:
    if isinstance(obj, Versioned):
        reveal_type(obj)  # Serializable & Versioned
        return str({
            "data": obj.serialize_json(),
            "version": obj.version
        })
    return obj.serialize_json()
```

### Intersection with gradual types

```python
def print_content(data: bytes):
    obj = untyped_library.deserialize(data)  # Unknown

    if isinstance(obj, Iterable):
        # obj is Unknown & Iterable
        print(obj.description)  # from Unknown
        for part in obj:        # from Iterable
            print(part.description)
```

### `hasattr` narrowing

```python
class Person:
    name: str

class Animal:
    species: str

def greet(being: Person | Animal | None):
    if hasattr(being, "name"):
        # Person | (Animal & <Protocol with 'name'>)
        print(f"Hello, {being.name}!")
    else:
        print("Hello there!")
```

Use `@final` on `Animal` to exclude it entirely from the narrowed type.

### Explicit intersection annotations

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ty_extensions import Intersection
    type SerializableVersioned = Intersection[Serializable, Versioned]
```

`ty_extensions` is available at type-checking time only — guard with `TYPE_CHECKING`.

## Top and bottom materializations

Gradual types (`Any`, `Unknown`) have special materializations:

- **Top materialization** — the largest type a gradual type can materialize to.
  Top of `Any` is `object`; top of `Any & int` is `int`.

```python
@final
class Item: ...

def process(items: Item | list[Item]):
    if isinstance(items, list):
        reveal_type(items)  # list[Item]
```

Without `@final` on `Item`, the type becomes `(Item & Top[list[Unknown]]) | list[Item]`
to account for classes inheriting from both `Item` and `list`.

## Reachability based on types

ty's reachability analysis is based on type inference, not just hardcoded patterns.
This allows detecting unreachable code in many situations:

```python
import pydantic
from pydantic import BaseModel

PYDANTIC_V2 = pydantic.__version__.startswith("2.")

class Person(BaseModel):
    name: str

def to_json(person: Person):
    if PYDANTIC_V2:
        return person.model_dump_json()  # reachable with pydantic 2.x
    else:
        return person.json()             # reachable with pydantic 1.x
```

ty evaluates `pydantic.__version__.startswith("2.")` at type-checking time based on
the installed version, so only the relevant branch is considered reachable.

## Gradual guarantee

ty supports partially typed code. Rules like `possibly-unresolved-reference` and
`possibly-missing-attribute` (disabled by default) warn about references through
gradual types that may or may not resolve.

## PEP 695 type aliases

ty resolves PEP 695 type aliases in `type[...]` annotations (0.0.60+):

```python
type StringList = list[str]

def process(items: type[StringList]) -> None: ...
```

## Protocol support (0.0.60)

New in 0.0.60:

- `type[Protocol]` — class objects can satisfy instance-method protocols
- Class and static protocol methods — protocols can declare `@classmethod` and
  `@staticmethod` members
- Descriptor setter domains derived for protocols

## Python version targeting

ty officially supports Python 3.10+ for type checking. Python 3.7–3.9 can be targeted
but may produce false positives/negatives for stdlib APIs due to incomplete bundled stubs.

```toml
[environment]
python-version = "3.12"
```

ty understands `sys.version_info` conditionals for version-gated code:

```python
import sys

if sys.version_info >= (3, 10):
    print(sys.stdlib_module_names)  # OK even if python-version is 3.9
```

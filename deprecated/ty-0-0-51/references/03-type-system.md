# Type System Features

## Redeclarations

ty allows reusing a symbol name with a different type within the same scope:

```python
def split_paths(paths: str) -> list[Path]:
    paths: list[str] = paths.split(":")  # redeclared as list[str]
    return [Path(p) for p in paths]
```

This is valid in ty but would be flagged as an error by mypy.

## Intersection Types

ty has first-class intersection type support (`A & B` means "both A and B"). Intersection types are created through type narrowing:

```python
def output_as_json(obj: Serializable) -> str:
    if isinstance(obj, Versioned):
        reveal_type(obj)  # Serializable & Versioned
        return str({
            "data": obj.serialize_json(),
            "version": obj.version
        })
```

### `isinstance` narrowing with gradual types

Narrowing `Unknown` or `Any` types with `isinstance` produces intersection types:

```python
obj = untyped_library.deserialize(data)  # type: Unknown

if isinstance(obj, Iterable):
    # obj is: Unknown & Iterable
    print(obj.description)  # still accessible from original Unknown
    for part in obj:        # iterable methods available
        print(part)
```

### `hasattr` narrowing

`hasattr` narrowing uses intersection types with synthetic protocols:

```python
def greet(being: Person | Animal | None):
    if hasattr(being, "name"):
        # being: Person | (Animal & <Protocol with 'name'>)
        print(f"Hello, {being.name}!")
```

Use `@final` on classes to make narrowing more precise (excludes subclass possibilities).

### Explicit intersection types

Import `Intersection` from the type-checking-only `ty_extensions` module:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ty_extensions import Intersection
    type SerializableVersioned = Intersection[Serializable, Versioned]
```

## Top and Bottom Materializations

Gradual types (`Any`, `Unknown`) have special materializations. The top materialization of `Any` is `object`. When checking `isinstance(x, list)`, ty intersects with the top materialization of `list[Unknown]`:

```python
@final
class Item: ...

def process(items: Item | list[Item]):
    if isinstance(items, list):
        reveal_type(items)  # list[Item] (not Item due to @final)
```

Without `@final`, the type becomes `(Item & Top[list[Unknown]]) | list[Item]` to account for classes inheriting from both.

## Reachability Based on Types

ty evaluates conditions at type-checking time to determine reachable code branches. This enables version-compatible patterns:

```python
import pydantic

PYDANTIC_V2 = pydantic.__version__.startswith("2.")

def to_json(person: Person):
    if PYDANTIC_V2:
        return person.model_dump_json()  # checked when pydantic 2.x installed
    else:
        return person.json()             # checked when pydantic 1.x installed
```

This works because `pydantic.__version__.startswith("2.")` can be evaluated during type checking based on the installed version.

ty also understands `sys.version_info` conditionals and `sys.platform` checks for cross-version and cross-platform compatibility patterns.

## Gradual Typing Support

ty is designed for adoption alongside partially typed code:
- Untyped functions are still checked (unlike mypy without `--check-untyped-defs`)
- `Any` and implicit `Unknown` types are tracked separately
- Type narrowing works even on gradual types via intersection

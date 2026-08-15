# Type System Features

## Redeclarations

ty allows reusing the same symbol with a different type within a function body:

```python
def split_paths(paths: str) -> list[Path]:
    paths: list[str] = paths.split(":")  # redeclared as list[str]
    return [Path(p) for p in paths]
```

## Intersection types

Intersection types `A & B` mean both A and B simultaneously. ty uses them for type narrowing:

```python
def output_as_json(obj: Serializable) -> str:
    if isinstance(obj, Versioned):
        reveal_type(obj)  # Serializable & Versioned
        return str({
            "data": obj.serialize_json(),
            "version": obj.version
        })
```

### Intersection with gradual types

Narrowing `Unknown` or `Any` with `isinstance` produces intersections:

```python
obj = untyped_library.deserialize(data)
if isinstance(obj, Iterable):
    print(obj.description)  # Unknown & Iterable
    for part in obj:
        print(part.description)
```

### `hasattr` narrowing

`hasattr` narrows using synthetic protocols:

```python
class Person:
    name: str

class Animal:
    species: str

def greet(being: Person | Animal | None):
    if hasattr(being, "name"):
        # Person | (Animal & <Protocol with 'name'>)
        print(f"Hello, {being.name}!")
```

Use `@final` on classes to exclude them from protocol intersection.

### Direct intersection annotations

Use `ty_extensions.Intersection` for explicit intersection type aliases:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ty_extensions import Intersection

    type SerializableVersioned = Intersection[Serializable, Versioned]

def output_as_json(obj: SerializableVersioned) -> str:
    ...
```

## Top and bottom materializations

Gradual types materialize to specific types. The top materialization of `Any` is `object`.
For invariant generics, ty intersects with the top materialization during `isinstance` checks:

```python
@final
class Item: ...

def process(items: Item | list[Item]):
    if isinstance(items, list):
        reveal_type(items)  # list[Item]
```

Without `@final` on `Item`, the narrowed type becomes `(Item & Top[list[Unknown]]) | list[Item]`
to account for classes inheriting from both `Item` and `list`.

## Reachability based on types

ty evaluates conditions at type-checking time based on inferred types, enabling sophisticated
dead-code detection:

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
        return person.json()  # reachable with pydantic 1.x
```

This works because `pydantic.__version__.startswith("2.")` is evaluated at type-checking time
based on the installed pydantic version.

## Identity narrowing

ty narrows tagged unions using identity (`is`/`is not`) comparisons:

```python
from typing import Literal

def process(x: int | Literal["skip"]):
    if x is "skip":
        reveal_type(x)  # Literal["skip"]
    else:
        reveal_type(x)  # int
```

## TypeVarTuple and Unpack

ty supports PEP 646 `TypeVarTuple` and `Unpack`:

```python
from typing import TypeVarTuple, Unpack

Ts = TypeVarTuple("Ts")

class Tuple:
    def __getitem__(self, idx: int): ...
    def __iter__(self): ...

def first(*args: Unpack[tuple[int, *Ts]]) -> int:
    return args[0]
```

## Strict equality semantics

Enable `strict-equality-semantics = true` for sounder equality narrowing:

```python
def parse(value: str) -> Literal["a"] | None:
    if value == "a":
        return value  # error: str is not Literal["a"]
    return None
```

This prevents unsound narrowing where subclasses of `str` with value `"a"` compare equal
but are not `Literal["a"]`.

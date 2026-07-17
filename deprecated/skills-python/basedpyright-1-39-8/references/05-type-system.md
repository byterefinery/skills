# Type System Reference

## Type Declarations and Assignability

Type annotations declare what values a symbol can hold. The type checker verifies that assigned values are assignable to the declared type.

```python
a: float = 3        # ok — int is assignable to float
b: int = 3.4        # error — float not assignable to int
c: int | float = 3.4  # union type
d: int | None = None  # Optional[int] equivalent
```

## Generic Types and Variance

Generic types specify element types using square brackets. Mutable container types are **invariant** — exact type match required.

```python
my_list_1: list[int] = [1, 2, 3]
my_list_2: list[int | None] = my_list_1  # Error — invariant!

# Fix: use immutable counterpart
my_list_2: Sequence[int | None] = my_list_1  # ok
```

| Mutable Type | Immutable Counterpart |
|-------------|----------------------|
| `list` | `Sequence` |
| `dict` | `Mapping` |
| `set` | `Container` |
| n/a | `tuple` |

## Type Narrowing

The type checker tracks narrowed types through code flow:

```python
def func(val: float | str | complex):
    reveal_type(val)  # float | str | complex

    val = 3  # narrowed to int (subclass of float)
    reveal_type(val)  # int

    if isinstance(val, int):
        reveal_type(val)  # int
    else:
        reveal_type(val)  # str | complex
```

Narrowing expressions:
- Simple identifiers: `my_var`
- Member access chains: `a.b.c.d`
- Assignment expressions: `x := expr`
- Integer subscripts: `args[3]`
- String subscripts: `kwargs["bar"]`

## Type Guards

Supported guard expressions for narrowing:

| Guard | Narrows |
|-------|---------|
| `x is None` / `x is not None` | Both positive and negative |
| `x == None` / `x != None` | Both |
| `type(x) is T` / `type(x) != T` | Both |
| `isinstance(x, T)` | Both (positive in `if`, negative in `else`) |
| `issubclass(x, T)` | Both |
| `x is L` (literal) | Both |
| `len(x) == L` (tuple length) | Both |
| `S in D` (TypedDict key check) | Positive |
| `f(x)` (user-defined type guard, PEP 647/742) | Per guard definition |
| `bool(x)` / `x` (statically truthy/falsey) | Both |

### Member-based type guards

```python
# Distinguishes types by a field with None
if x.y is None: ...  # narrows x based on y's type

# Distinguishes by literal enum/bool field
if x.y == SomeEnum.Value: ...  # narrows x

# TypedDict key check
if "key" in typed_dict: ...  # narrows to Required keys present
```

## Type Inference

### Single-Assignment Inference

```python
var1 = 3           # int
var2 = "hi"        # str
var3 = list()      # list[Unknown]
var4 = [3, 4]      # list[int]
```

### Multi-Assignment Inference

Union of all assigned types:

```python
class Foo:
    def __init__(self):
        self.var1 = ""       # str

    def do_something(self, val: int):
        self.var1 = val      # now str | int
```

### Bidirectional Inference

Expected type from the left-hand side influences right-hand side inference:

```python
var1 = []                    # ambiguous — list[Unknown]
var2: list[int] = []         # unambiguous — list[int]
var3 = [4]                   # list[int] (heuristic)
var4: list[float] = [4]      # list[float] (LHS determines RHS)
```

### Empty Container Inference

Empty containers infer from non-empty assignments on other paths:

```python
if condition:
    my_list = []
else:
    my_list = ["a", "b"]

reveal_type(my_list)  # list[str]
```

### Return Type Inference

Union of all return expressions. Implicit `return None` if function is reachable without a return:

```python
def func1(val: int):
    if val > 3:
        return ""
    elif val < 1:
        return True
    # implicit return None

# Inferred: str | bool | None
```

### `Never` vs `NoReturn`

Both mean the same thing. `Never` is preferred (Python 3.11+):

```python
from typing import assert_never

def foo(value: int | str):
    if isinstance(value, int):
        ...
    elif isinstance(value, str):
        ...
    else:
        assert_never(value)  # validates all types are covered
```

`NoReturn` only makes sense for functions; `Never` is the narrowest type usable anywhere.

### Parameter Type Inference

- `self` → inferred as `Self`
- `cls` → inferred as `type[Self]`
- Unannotated method parameters can inherit types from base class methods with matching signatures
- Parameters with default values infer from the default:

```python
def func(a, b=0, c=None):
    pass
# (a: Unknown, b: int, c: Unknown | None) -> None
```

### Lambda Inference

Lambdas rely on bidirectional inference for parameter types:

```python
var1 = lambda a, b: a + b  # (Unknown, Unknown) -> Unknown

def sort(list: list[float], comp: Callable[[float, float], bool]): ...
sort([2, 1.3], lambda a, b: a < b)  # params inferred as float
```

### Collection Inference

**Lists** — behavior depends on `strictListInference`:
- Empty: `list[Unknown]`
- Same type elements: `list[T]`
- Mixed types, strict off: `list[Unknown]`
- Mixed types, strict on: `list[int | float]`

**Sets** — behavior depends on `strictSetInference`:
- Same as lists but for sets

**Dictionaries** — behavior depends on `strictDictionaryInference`:
- Empty: `dict[Unknown, Unknown]`
- Same key/value types: `dict[K, V]`
- Mixed, strict off: `dict[Unknown, Unknown]`
- Mixed, strict on: `dict[Union[keys], Union[values]]`

**Tuples** — fixed-length by default with literal types:
```python
var1 = (1, "a", True)  # tuple[Literal[1], Literal["a"], Literal[True]]
var2: tuple[int, ...] = (1, 2)  # homogeneous tuple of variable length
```

## Literals

```python
def func1() -> Literal[1, 2, 3]: ...  # only returns 1, 2, or 3
def func2(mode: Literal["r", "w", "rw"]) -> None: ...
```

Type inference generally does not infer literal types for variables (to avoid overly specific types), but retains them in tuples.

## `reveal_type()`

Debug tool to see the type checker's evaluated type:

```python
x = 1
reveal_type(x)  # Type of "x" is "Literal[1]"
```

Available without import. In IDEs, hover over identifiers instead.

## Supported PEPs

basedpyright supports all major typing PEPs:

| PEP | Feature |
|-----|---------|
| 484 | Type hints |
| 487 | Simpler class customization |
| 526 | Variable annotations |
| 544 | Structural subtyping (Protocol) |
| 561 | Distributing type information (py.typed) |
| 563 | Postponed evaluation of annotations |
| 570 | Position-only parameters |
| 585 | Generics in standard collections |
| 586 | Literal types |
| 589 | TypedDict |
| 591 | Final qualifier |
| 593 | Flexible variable annotations (Annotated) |
| 604 | Union syntax (`X \| Y`) |
| 612 | ParamSpec |
| 613 | Explicit type aliases |
| 635 | Structural pattern matching (match/case) |
| 646 | Variadic generics |
| 647 | User-defined type guards |
| 655 | Required TypedDict items |
| 673 | Self type |
| 675 | Arbitrary literal strings |
| 681 | dataclass_transform |
| 692 | TypedDict for kwargs |
| 695 | Type parameter syntax (`def f[T]()`) |
| 696 | Type defaults for TypeVarLikes |
| 698 | `@override` decorator |
| 702 | Marking deprecations |
| 705 | TypedDict read-only items |
| 728 | TypedDict with typed extra items |
| 742 | TypeIs narrowing |
| 746 | Type checking annotated metadata (experimental) |
| 747 | Annotating type forms (experimental) |
| 764 | Inline TypedDicts (experimental) |

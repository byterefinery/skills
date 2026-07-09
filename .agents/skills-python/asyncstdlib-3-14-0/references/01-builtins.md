# Builtins

Async versions of Python builtin functions that work with async iterables and callables.

## anext

```python
async def anext(iterator: AsyncIterator[T], default: T = <no default>) -> T
```

Retrieve the next item from an async iterator. Raises `StopAsyncIteration` if exhausted and no default is given. Unlike the builtin `next()`, this always awaits `__anext__`.

```python
async for item in async_iter:
    first = await a.anext(async_iter, None)  # second item, or None
```

## iter

```python
def iter(subject: AnyIterable[T], sentinel: T = <no default>) -> AsyncIterator[T]
```

Convert any iterable to an async iterator. Accepts `__aiter__`, `__iter__`, or `__getitem__` (sequence protocol) subjects.

With a sentinel, the subject must be a callable — produces values via `await subject()` until a value equals `sentinel`.

```python
# From a regular iterable
async for item in a.iter([1, 2, 3]):
    ...

# Callable with sentinel (e.g., reading chunks)
async def read_chunk():
    return await stream.read(1024)

async for chunk in a.iter(read_chunk, sentinel=b""):
    ...
```

## zip

```python
async def zip(*iterables: AnyIterable[Any], strict: bool = False) -> AsyncIterator[Tuple[Any, ...]]
```

Aggregate elements from multiple iterables into tuples. Stops at the shortest iterable. With `strict=True`, raises `ValueError` if iterables have different lengths. Properly closes all underlying async iterators.

```python
async for name, score in a.zip(async_names, async_scores):
    ...

# Strict mode
async for a_val, b_val in a.zip(iter_a, iter_b, strict=True):
    ...
```

## map

```python
async def map(function: Callable, iterable: AnyIterable, *iterables: AnyIterable, strict: bool = False) -> AsyncIterator[R]
```

Apply a function to items from iterables. The function may be sync or async — auto-detected. Equivalent to `(await function(*args) async for args in zip(iterables))`. Supports `strict=True` like `zip`.

```python
async def expensive_transform(x):
    return await compute(x)

async for result in a.map(expensive_transform, async_iterable):
    ...

# Multiple iterables
async for summed in a.map(lambda a, b: a + b, iter_a, iter_b):
    ...
```

## filter

```python
async def filter(function: Callable[[T], bool] | None, iterable: AnyIterable[T]) -> AsyncIterator[T]
```

Yield items where `function(item)` is truthy. If `function` is `None`, yields truthy items directly. Function may be sync or async.

```python
async def is_valid(item):
    return await check(item)

async for item in a.filter(is_valid, async_iterable):
    ...

# Filter falsy values
async for truthy in a.filter(None, async_iterable):
    ...
```

## enumerate

```python
async def enumerate(iterable: AnyIterable[T], start: int = 0) -> AsyncIterator[Tuple[int, T]]
```

Yield `(index, item)` pairs starting from `start`.

```python
async for idx, item in a.enumerate(async_iterable, start=1):
    print(f"{idx}: {item}")
```

## all

```python
async def all(iterable: AnyIterable[Any]) -> bool
```

Return `True` if all elements are truthy (or iterable is empty). Short-circuits on first falsy element. Properly closes the iterator.

```python
if await a.all(async_checks):
    proceed()
```

## any

```python
async def any(iterable: AnyIterable[Any]) -> bool
```

Return `True` if any element is truthy. Short-circuits on first truthy element.

```python
if await a.any(async_flags):
    handle()
```

## max / min

```python
async def max(iterable: AnyIterable[T], *, key: Callable | None = None, default: T = <no default>) -> T
async def min(iterable: AnyIterable[T], *, key: Callable | None = None, default: T = <no default>) -> T
```

Find the largest/smallest item. The `key` function may be sync or async. Raises `ValueError` if iterable is empty and no default is given. The multi-argument form (`max(a, b, c)`) is not supported — use the builtin.

```python
best = await a.max(async_items, key=async_score_func)
first = await a.min(async_items, default=0)
```

## sum

```python
async def sum(iterable: AnyIterable[Any], start: Any = 0) -> Any
```

Sum of `start` and all elements.

```python
total = await a.sum(async_numbers, start=100)
```

## list / tuple / set / dict

```python
async def list(iterable: AnyIterable[T] = ()) -> List[T]
async def tuple(iterable: AnyIterable[T] = ()) -> Tuple[T, ...]
async def set(iterable: AnyIterable[T] = ()) -> Set[T]
async def dict(iterable: AnyIterable[Tuple[HK, T]] = (), **kwargs: T) -> Dict[Any, T]
```

Collect async iterable items into a concrete collection. `dict()` accepts keyword arguments that are merged after the iterable.

```python
items = await a.list(async_iterable)
pairs = await a.dict(async_key_values, extra="value")
unique = await a.set(async_iterable)
frozen = await a.tuple(async_iterable)
```

## sorted

```python
async def sorted(iterable: AnyIterable[T], *, key: Callable | None = None, reverse: bool = False) -> List[T]
```

Collect and sort items into a list. The `key` function may be async. Actual sorting is synchronous — large iterables may block the event loop. Guaranteed O(n log n).

```python
ordered = await a.sorted(async_items, key=async_key, reverse=True)
```

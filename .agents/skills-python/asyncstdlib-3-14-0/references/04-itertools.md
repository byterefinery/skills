# Itertools

Async versions of `itertools` — lazy transformation, combination, and aggregation of async iterables.

## accumulate

```python
async def accumulate(iterable: AnyIterable, function: Callable = operator.add, *, initial: Any = None) -> AsyncIterator
```

Yield the running reduction. Each output is the result of applying `function` to the previous accumulated value and the next item. Default function is addition (running sum). If `initial` is provided, it is the first yielded value.

```python
# Running sum
async for running_total in a.accumulate(async_numbers):
    ...

# Running max
async for running_max in a.accumulate(async_numbers, function=max):
    ...

# With initial value
async for value in a.accumulate(async_numbers, initial=100):
    ...
```

## batched

```python
async def batched(iterable: AnyIterable[T], n: int, strict: bool = False) -> AsyncIterator[Tuple[T, ...]]
```

Batch items into tuples of length `n`. The last batch may be smaller. With `strict=True`, raises `ValueError` if the last batch is smaller than `n`. Raises `ValueError` if `n < 1`.

```python
async for batch in a.batched(async_stream, n=100):
    await process_batch(batch)

# Strict — fails if total count not divisible by n
async for batch in a.batched(async_stream, n=10, strict=True):
    ...
```

## cycle

```python
async def cycle(iterable: AnyIterable[T]) -> AsyncIterator[T]
```

Indefinitely repeat items from the iterable. First pass yields items lazily as they become available; subsequent passes replay from an internal buffer (no delays). If the iterable is empty, the cycle terminates immediately. All items are stored in memory.

```python
async for item in a.cycle(async_source):
    ...  # repeats forever
```

## chain

```python
class chain(AsyncIterator[T]):
    def __init__(self, *iterables: AnyIterable[T])
    @classmethod
    def from_iterable(cls, iterable: AnyIterable[AnyIterable[T]]) -> chain[T]
    async def aclose(self) -> None
```

Concatenate multiple iterables into one stream. Each iterable is lazily exhausted in order. The chain owns its iterables and closes them on `aclose()`.

Use `chain.from_iterable()` for lazy chaining of an iterable of iterables — only already-fetched iterables are closed.

```python
# Chain multiple iterables
async for item in a.chain(iter_a, iter_b, iter_c):
    ...

# Lazy chaining
async for item in a.chain.from_iterable(async_iter_of_iters):
    ...
```

## compress

```python
async def compress(data: AnyIterable[T], selectors: AnyIterable[Any]) -> AsyncIterator[T]
```

Yield `data` items where the corresponding `selectors` item is truthy. Stops at the shortest of the two. Equivalent to `(item async for item, select in zip(data, selectors) if select)`.

```python
async for kept in a.compress(async_data, [True, False, True, False]):
    ...
```

## dropwhile

```python
async def dropwhile(predicate: Callable[[T], Any], iterable: AnyIterable[T]) -> AsyncIterator[T]
```

Discard items while `predicate(item)` is true. After the first item where predicate is false, all remaining items are yielded immediately without further predicate evaluation.

```python
async for item in a.dropwhile(lambda x: x < 5, async_numbers):
    ...  # yields from first item >= 5 onward
```

## filterfalse

```python
async def filterfalse(predicate: Callable[[T], bool] | None, iterable: AnyIterable[T]) -> AsyncIterator[T]
```

Yield items where `predicate(item)` is false. If `predicate` is `None`, yields falsy items.

```python
async for odd in a.filterfalse(lambda x: x % 2 == 0, async_numbers):
    ...
```

## islice

```python
async def islice(iterable: AnyIterable[T], *args: Optional[int]) -> AsyncIterator[T]
```

Lazy async version of `iterable[start:stop:step]`. Accepts `stop` alone, or `start, stop [, step]`. Always consumes the first `start` items even if the resulting slice is empty.

```python
# First 10 items
async for item in a.islice(async_iterable, 10):
    ...

# Items 5 through 15
async for item in a.islice(async_iterable, 5, 15):
    ...

# Every third item, starting from index 1
async for item in a.islice(async_iterable, 1, None, 3):
    ...
```

## starmap

```python
async def starmap(function: Callable, iterable: AnyIterable[Iterable[Any]]) -> AsyncIterator[T]
```

Apply `function(*args)` where each `args` comes from the iterable. Like `map` but with a single iterable of argument tuples.

```python
async for result in a.starmap(lambda x, y: x + y, [(1, 2), (3, 4)]):
    ...  # yields 3, 7
```

## takewhile

```python
async def takewhile(predicate: Callable[[T], Any], iterable: AnyIterable[T]) -> AsyncIterator[T]
```

Yield items while `predicate(item)` is true. Stops at the first failure — the failing item is consumed but discarded (lost from both the original iterator and the result).

```python
async for small in a.takewhile(lambda x: x < 10, async_numbers):
    ...  # yields items < 10, stops at first >= 10
```

## tee

```python
class Tee(T):
    def __init__(self, iterable: AnyIterable[T], n: int = 2, *, lock: AsyncContextManager | None = None)
    def __len__(self) -> int
    def __getitem__(self, item: int | slice) -> AsyncIterator[T] | Tuple[AsyncIterator[T], ...]
    def __iter__(self) -> Iterator[AsyncIterator[T]]
    async def __aenter__(self) -> Tee[T]
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None
    async def aclose(self) -> None
```

Split one iterable into `n` separate async iterators, each yielding the same items. Items are buffered until all peers have consumed them. Works lazily with infinite iterables (provided all iterators advance).

Supports indexing, slicing, and unpacking. Can be used as an async context manager for automatic cleanup.

```python
# Basic tee
async for prev, curr in a.map(operator.sub, *a.tee(async_data, n=2)):
    ...  # compute differences

# Unpacking
a_iter, b_iter, c_iter = a.tee(async_source, n=3)

# With lock for concurrency safety
async with a.tee(async_source, n=2, lock=asyncio.Lock()) as tee:
    iter1, iter2 = tee

# Tee of a tee shares buffers
double_tee = a.tee(a.tee(source)[0], n=2)
```

## pairwise

```python
async def pairwise(iterable: AnyIterable[T]) -> AsyncIterator[Tuple[T, T]]
```

Yield overlapping `(previous, current)` pairs. No pair is emitted if the iterable has zero or one item.

```python
async for prev, curr in a.pairwise(async_data):
    print(f"transition: {prev} -> {curr}")
```

## zip_longest

```python
async def zip_longest(*iterables: AnyIterable[Any], fillvalue: Any = None) -> AsyncIterator[Tuple[Any, ...]]
```

Like `zip` but continues until the longest iterable is exhausted. Shorter iterables are padded with `fillvalue`.

```python
async for pair in a.zip_longest(iter_a, iter_b, fillvalue=0):
    ...
```

## groupby

```python
class GroupBy(AsyncIterator[Tuple[R, AsyncIterator[T_co]]]):
    def __init__(self, iterable: AnyIterable[T_co], key: Callable | None = None)
    async def __anext__(self) -> Tuple[R, AsyncIterator[T_co]]
    async def aclose(self) -> None
```

Group consecutive items by key. Yields `(key, group_iterator)` pairs. Groups share the underlying iterator — advancing groupby invalidates previous groups. Not safe to concurrently advance both groupby and its group iterators.

Unlike sync `itertools.groupby`, sorting by key beforehand defeats the purpose of lazy async iteration.

```python
async for key, group in a.groupby(async_records, key=lambda r: r.category):
    items = await a.list(group)  # collect group before advancing
    process(key, items)

# Without key function — groups consecutive identical values
async for key, group in a.groupby(async_values):
    ...
```

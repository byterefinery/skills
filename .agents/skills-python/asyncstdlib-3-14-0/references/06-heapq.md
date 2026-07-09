# Heapq

Async versions of `heapq` — merging sorted streams and finding extremes.

## merge

```python
async def merge(*iterables: AnyIterable, key: Callable | None = None, reverse: bool = False) -> AsyncIterator
```

Merge multiple pre-sorted iterables into a single sorted stream. Operates lazily — only one item per iterable is stored at any time. Suitable for merging timestamped records from multiple sources.

The `key` function may be sync or async. Default sort order is ascending; use `reverse=True` for descending. All iterables must be pre-sorted in the same order.

Equivalent to `sorted(chain(*iterables), key=key, reverse=reverse)` but lazy and memory-efficient.

```python
# Merge sorted streams
async for item in a.merge(sorted_stream_a, sorted_stream_b, sorted_stream_c):
    ...

# Merge with custom key
async for record in a.merge(
    stream_a, stream_b,
    key=lambda r: r.timestamp
):
    ...

# Descending merge
async for item in a.merge(stream_a, stream_b, reverse=True):
    ...
```

## nlargest

```python
async def nlargest(iterable: AnyIterable[T], n: int, key: Callable | None = None) -> List[T]
```

Return a sorted list of the `n` largest elements. Consumes the iterable lazily and discards items eagerly — only `n` items are kept in memory.

Equivalent to `sorted(iterable, key=key, reverse=True)[:n]` but more memory-efficient for large iterables.

```python
top_scores = await a.nlargest(async_scores, n=10)
top_users = await a.nlargest(async_users, n=5, key=lambda u: u.score)
```

## nsmallest

```python
async def nsmallest(iterable: AnyIterable[T], n: int, key: Callable | None = None) -> List[T]
```

Return a sorted list of the `n` smallest elements. Reverse of `nlargest`.

```python
bottom_scores = await a.nsmallest(async_scores, n=10)
```

---
name: asyncstdlib-3-14-0
description: asyncstdlib — async versions of Python standard library helpers. Re-implements builtins (zip, map, filter, enumerate, all, any, max, min, sum, sorted, list, dict, set, tuple, anext, iter), functools (reduce, lru_cache, cache, cached_property), itertools (accumulate, batched, chain, cycle, compress, dropwhile, filterfalse, groupby, islice, pairwise, starmap, takewhile, tee, zip_longest), contextlib (closing, contextmanager, ContextDecorator, nullcontext, ExitStack), heapq (merge, nlargest, nsmallest), and asynctools (borrow, scoped_iter, await_each, any_iter, apply, sync). Fully agnostic to async event loops (asyncio, trio, custom). Use when the user needs async versions of stdlib iteration, reduction, caching, or context management utilities, or when working with async iterables/callables in Python.
metadata:
  tags:
    - async
    - stdlib
    - iteration
---

# asyncstdlib 3.14.0

asyncstdlib re-implements Python standard library functions and classes to work with `async` callables, iterables, and context managers. It is fully event-loop agnostic — works with `asyncio`, `trio`, or any custom async framework.

## Overview

The library mirrors the structure of the standard library, providing async-compatible versions organized into modules:

- **builtins** — `anext`, `iter`, `zip`, `map`, `filter`, `enumerate`, `all`, `any`, `max`, `min`, `sum`, `list`, `dict`, `set`, `tuple`, `sorted`
- **functools** — `reduce`, `lru_cache`, `cache`, `cached_property`
- **contextlib** — `closing`, `ContextDecorator`, `contextmanager`, `nullcontext`, `ExitStack`
- **itertools** — `accumulate`, `batched`, `cycle`, `chain`, `compress`, `dropwhile`, `filterfalse`, `islice`, `takewhile`, `starmap`, `tee`, `pairwise`, `zip_longest`, `groupby`
- **heapq** — `merge`, `nlargest`, `nsmallest`
- **asynctools** — `borrow`, `scoped_iter`, `await_each`, `any_iter`, `apply`, `sync`

All functions accept both sync and async iterables and callables transparently. A sync iterable is wrapped into an async iterator; a sync callable is wrapped so its result can be awaited.

### Core Concepts

**AnyIterable** — every function accepts `Iterable[T]` or `AsyncIterable[T]`. Pass a regular list, range, or async generator — the function handles it.

**awaitify** — internal mechanism that auto-detects whether a callable is async or sync on first call, then caches the detection. Sync functions are wrapped to return an awaitable; async functions pass through unchanged.

**ScopedIter** — internal context manager used by most functions to ensure async iterators are properly closed via `aclose()`, even on exceptions. This means resource cleanup is reliable.

**Borrowing** — `borrow()` and `scoped_iter()` prevent premature closing of async iterators. When you pass an iterator to another function, it may try to close it. Borrowing wraps the iterator so `aclose()` only closes the wrapper, not the underlying iterator.

## Usage

```python
import asyncstdlib as a

# Async zip — works with mixed sync/async iterables
async for x, y in a.zip(async_iter_a, [1, 2, 3]):
    ...

# Async map with async function
async def process(item):
    return await some_io(item)

async for result in a.map(process, async_iterable):
    ...

# Async filtering
async for even in a.filter(lambda x: x % 2 == 0, async_range(10)):
    ...

# Aggregation on async iterables
total = await a.sum(async_numbers)
all_ok = await a.all(async_checks)
first_true = await a.any(async_flags)
best = await a.max(async_items, key=async_key_func)

# Caching async functions
@a.lru_cache(maxsize=128)
async def fetch_user(user_id):
    return await db.query(user_id)

# Async itertools
async for batch in a.batched(async_stream, n=100):
    await process_batch(batch)

async for key, group in a.groupby(async_records, key=lambda r: r.category):
    count = await a.list(group)

# Context management
@a.contextmanager
async def managed_resource():
    resource = await acquire()
    try:
        yield resource
    finally:
        await release(resource)

# Sync wrapper for async-neutral code
@a.sync
def compute(x, y):
    return x + y  # now awaitable

await compute(1, 2)
```

### Installation

```bash
pip install asyncstdlib
```

## Gotchas

- **`max()`/`min()` iterable-only** — the multi-argument form (`max(a, b, c)`) is not supported; it does not benefit from being async. Use the builtin `max()`/`min()` for that.
- **`sorted()` blocks the event loop** — actual sorting is synchronous. Very large iterables or slow key functions may block. Sorting is O(n log n) worst-case.
- **`tee()` concurrency** — if the underlying iterator is not concurrency-safe, only one "most advanced" iterator should advance at a time. Pass a `lock` (e.g., `asyncio.Lock()`) to enforce sequential access.
- **`groupby()` shares underlying iterator** — advancing the groupby iterator invalidates previous groups. Do not concurrently advance both the groupby and its group iterators. Unlike sync `itertools.groupby`, sorting by key beforehand defeats the purpose of lazy async iteration.
- **`cached_property` needs `__dict__`** — instances must have a mutable `__dict__`. Classes using `__slots__` without `__dict__` will fail. Use `@a.cached_property(Lock)` to prevent concurrent re-computation.
- **`lru_cache` is not thread-safe** — unlike the sync `functools.lru_cache`, the async version does not guarantee thread safety. It does support overlapping `await` calls if the wrapped function does.
- **`chain` owns its iterables** — `chain(a, b, c)` closes all passed iterators when the chain is closed. Use `chain.from_iterable(lazy_iter_of_iters)` for lazy chaining where only processed iterables are closed.
- **`batched(strict=True)` raises on partial last batch** — if the total count is not evenly divisible by `n`, a `ValueError` is raised.
- **`islice` always consumes `start` items** — even if the resulting slice is empty, the first `start` items are consumed and discarded.
- **`takewhile` discards the failing item** — the item that fails the predicate is consumed but not yielded, and is lost from both the original iterator and the takewhile result.
- **`dropwhile` evaluates predicate until first failure** — after the first item fails the predicate, all remaining items are yielded immediately without further predicate evaluation.
- **`scoped_iter` is not re-entrant** — entering the same scoped_iter context twice raises `RuntimeError`. Nested scoping of the same iterator via separate calls is safe though.
- **`any_iter` eagerly resolves async layers** — it must `await` before checking if the next layer is iterable. Non-iterables may be consumed in the process. Prefer `a.iter()` for simple EAFP-style iteration.
- **`apply` awaits all args before calling** — all positional and keyword arguments are awaited before `func` is called. If any awaitable raises, `func` is never called.
- **`sync` should not be used as standalone decorator** — define the function as `async def` directly. `sync` is meant for wrapping callables passed as arguments or for async-neutral APIs.
- **`ExitStack` is async-neutral** — unlike `contextlib.AsyncExitStack`, there are no separate methods for sync vs async arguments. Both are handled transparently.
- **`compress` stops at shortest** — like `zip`, it stops when either `data` or `selectors` is exhausted.

## References

- [01-builtins](references/01-builtins.md) — anext, iter, zip, map, filter, enumerate, all, any, max, min, sum, list, dict, set, tuple, sorted
- [02-functools](references/02-functools.md) — reduce, lru_cache, cache, cached_property, CacheInfo, CacheParameters
- [03-contextlib](references/03-contextlib.md) — closing, ContextDecorator, contextmanager, nullcontext, ExitStack
- [04-itertools](references/04-itertools.md) — accumulate, batched, cycle, chain, compress, dropwhile, filterfalse, islice, takewhile, starmap, tee, pairwise, zip_longest, groupby
- [05-asynctools](references/05-asynctools.md) — borrow, scoped_iter, await_each, any_iter, apply, sync
- [06-heapq](references/06-heapq.md) — merge, nlargest, nsmallest

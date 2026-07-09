# Asynctools

Utilities for safe async iterator handling, sync/async bridging, and awaitable manipulation.

## borrow

```python
def borrow(iterator: AsyncIterator[T] | AsyncGenerator[T, S], /) -> AsyncIterator[T] | AsyncGenerator[T, S]
```

Wrap an async iterator so that `aclose()` only closes the wrapper, not the underlying iterator. The original owner is responsible for closing.

The borrowed iterator forwards `asend` and `athrow` if the underlying iterator supports them. `aclose` is always provided but only closes the wrapper.

```python
async def producer():
    for i in range(10):
        yield i

iter = producer()
borrowed = a.borrow(iter)

async for item in a.islice(borrowed, 3):
    ...  # first 3 items

# iter is still usable — not closed
async for item in iter:
    ...  # continues from item 3
```

## scoped_iter

```python
def scoped_iter(iterable: AnyIterable[T], /) -> AsyncContextManager[AsyncIterator[T]]
```

Context manager that provides a borrowed async iterator and ensures it is closed at scope exit. Combines `iter()` + `closing()` with borrowing semantics.

The iterator is borrowed inside the scope — passing it to other functions will not close the underlying iterator. Only the outermost scope closes the actual iterator.

Nested scoping of the same iterator is safe. Entering the same scoped_iter context twice raises `RuntimeError` (not re-entrant).

```python
async def head_tail(iterable, leading=5, trailing=5):
    async with a.scoped_iter(iterable) as async_iter:
        # Safe to pass around — won't be closed
        async for item in a.islice(async_iter, leading):
            yield item
        tail = deque(maxlen=trailing)
        async for item in async_iter:
            tail.append(item)
    for item in tail:
        yield item
```

## await_each

```python
async def await_each(awaitables: Iterable[Awaitable[T]], /) -> AsyncIterable[T]
```

Convert an iterable of awaitables into an async iterator of awaited values. Useful for applying async-iterable functions to collections of coroutines.

```python
async def check1(): return True
async def check2(): return False
async def check3(): return True

# Check all coroutines
all_ok = await a.all(a.await_each([check1(), check2(), check3()]))

# Filter awaited results
async for result in a.filter(lambda x: x > 0, a.await_each([compute() for _ in range(10)])):
    ...
```

## any_iter

```python
async def any_iter(__iter: Awaitable[AnyIterable[Awaitable[T]]] | Awaitable[AnyIterable[T]] | AnyIterable[Awaitable[T]] | AnyIterable[T], /) -> AsyncIterator[T]
```

Uniformly handle async iterables, awaitable iterables, iterables of awaitables, and plain iterables in one `async for`. Matches all forms of `async def` functions that return iterables.

Must eagerly resolve each async layer before checking the next — incurs a performance penalty. Prefer `a.iter()` for simple EAFP-style iteration.

```python
# All of these work uniformly:
async for item in a.any_iter(sync_list):         # Iterable[T]
async for item in a.any_iter(async_generator()):  # AsyncIterable[T]
async for item in a.any_iter(awaitable_list()):   # Awaitable[Iterable[T]]
async for item in a.any_iter(async_awaitables()): # Iterable[Awaitable[T]]
```

## apply

```python
async def apply(__func: Callable[..., T], /, *args: Awaitable[Any], **kwargs: Awaitable[Any]) -> T
```

Await all positional and keyword arguments, then call `func` with the resolved values. Useful for chaining operations on awaitables.

```python
async def get_x(): return 10
async def get_y(): return 3

result = await a.apply(
    lambda x, y: x ** y,
    get_x(),
    get_y()
)  # 1000

# With kwargs
result = await a.apply(
    lambda a, b, c=0: a + b + c,
    get_a(),
    get_b(),
    c=get_c()
)
```

## sync

```python
def sync(function: Callable[..., Awaitable[T]] | Callable[..., T], /) -> Callable[..., Awaitable[T]]
```

Wrap a callable so its result is always awaitable. If the function is already async, it passes through unchanged. If sync, its result is wrapped in an awaitable.

Use for writing async-neutral functions that accept both sync and async callables, or for using sync functions where async ones are expected.

```python
# Wrap sync function to be awaitable
def compute(x, y):
    return x + y

await a.sync(compute)(1, 2)

# Async function passes through
async def async_compute(x):
    return x * 2

await a.sync(async_compute)(5)

# Lambda
await a.sync(lambda x: x ** 3)(x=5)

# In async-neutral library code
def my_map(func, iterable):
    func = a.sync(func)  # ensure awaitable
    async for item in iterable:
        yield await func(item)
```

**Note:** Do not use `sync` as the sole decorator on a function definition. Define the function as `async def` directly.

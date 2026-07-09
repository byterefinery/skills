# Contextlib

Async context manager utilities — `closing`, `contextmanager`, `ContextDecorator`, `nullcontext`, and `ExitStack`.

## closing

```python
class closing(AClose):
    async def __aenter__(self) -> AClose
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None
```

Context manager that calls `await thing.aclose()` on exit. Use for objects that need reliable cleanup but do not support the context manager protocol — particularly async iterators holding resources.

```python
import asyncstdlib as a

async with a.closing(a.iter(stream)) as async_iter:
    async for item in async_iter:
        ...
# async_iter.aclose() called automatically
```

## contextmanager

```python
def contextmanager(func: Callable[..., AsyncGenerator[T, None]]) -> Callable[..., AsyncContextManager[T]]
```

Decorator that turns an async generator function into an async context manager. The generator should `yield` once — the value becomes the context value. Code before `yield` is `__aenter__`, code after is `__aexit__`.

If an exception ends the context block, it is re-raised at the `yield` via `athrow`. Wrap `yield` in `try/except` to handle it.

The created context manager is a `ContextDecorator` and can also decorate functions.

```python
@a.contextmanager
async def managed_connection(host, port):
    conn = await connect(host, port)
    try:
        yield conn
    finally:
        await conn.close()

# Use as context manager
async with managed_connection("localhost", 5432) as conn:
    await conn.query("SELECT 1")

# Use as decorator — context auto-entered on await
@managed_connection("localhost", 5432)
async def run_query():
    conn = ...  # provided by context
```

## ContextDecorator

```python
class ContextDecorator(AsyncContextManager[T]):
    def _recreate_cm(self) -> Self
    def __call__(self, func: AC, /) -> AC
```

Base class to make an async context manager also usable as a decorator. When decorating a function, the context is automatically entered when the function is awaited.

Default `_recreate_cm()` returns `self` (assumes reentrant, concurrency-safe). Override to create a fresh instance if the context is not safe to reuse.

```python
class Transaction(ContextDecorator):
    def __init__(self, db):
        self.db = db

    async def __aenter__(self):
        self.tx = await self.db.begin()
        return self.tx

    async def __aexit__(self, *exc):
        if exc[0] is None:
            await self.tx.commit()
        else:
            await self.tx.rollback()

# As context manager
async with Transaction(db) as tx:
    ...

# As decorator
@Transaction(db)
async def update_record():
    ...  # runs inside transaction
```

## nullcontext

```python
class nullcontext(T):
    async def __aenter__(self) -> T
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None
```

Neutral context manager that returns `enter_result` on entry and does nothing on exit. Use as a placeholder when a context manager is conditionally needed.

```python
async def process(source):
    if isinstance(source, AsyncIterator):
        cm = a.closing(iter(source))
    else:
        cm = a.nullcontext(source)  # no-op placeholder

    async with cm as async_iter:
        async for item in async_iter:
            ...
```

## ExitStack

```python
class ExitStack:
    def __init__(self) -> None
    async def __aenter__(self) -> ExitStack
    async def __aexit__(self, exc_type, exc_val, tb) -> bool
    def pop_all(self) -> ExitStack
    def push(self, exit: SE) -> SE
    def callback(self, callback: C, *args, **kwargs) -> C
    async def enter_context(self, cm: AnyContextManager[T]) -> T
    async def aclose(self) -> None
```

Programmatically manage multiple context managers and cleanup callbacks. Context managers are exited in LIFO order, emulating nested `async with` statements.

This is an *async-neutral* version — no separate methods for sync vs async arguments. Both are handled transparently.

### enter_context

Enter a context manager and register it for exit. Works with both `async with` and regular `with` context managers.

```python
async with a.ExitStack() as stack:
    conn1 = stack.enter_context(connection_a)
    conn2 = stack.enter_context(connection_b)
    # Both exited in LIFO order when stack unwinds
```

### callback

Register a function to be called on stack unwinding. The callback does not receive exception details and cannot suppress exceptions. Both sync and async callbacks are supported.

```python
async with a.ExitStack() as stack:
    @stack.callback
    def cleanup():
        print("cleaning up")

    @stack.callback
    async def async_cleanup():
        await release_resource()
```

### push

Register a callback with `__aexit__` signature (`exc_type, exc_val, tb` → `bool`). Can suppress exceptions by returning `True`. Accepts objects with `__aexit__`, `__exit__`, or plain callables.

```python
async with a.ExitStack() as stack:
    @stack.push
    async def handler(exc_type, exc_val, tb):
        if exc_type is ValueError:
            return True  # suppress ValueError
        return False
```

### pop_all

Transfer all registered callbacks to a new ExitStack. The original stack no longer owns them.

```python
async with a.ExitStack() as outer:
    inner = outer.pop_all()
    # inner now owns all callbacks
```

### aclose

Immediately unwind the stack (invoke all callbacks in LIFO order). Unlike the sync `ExitStack.close()`, this is `async`.

```python
stack = a.ExitStack()
await stack.__aenter__()
try:
    ...
finally:
    await stack.aclose()
```

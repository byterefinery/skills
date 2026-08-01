# Async File Wrapper Classes

## Class hierarchy

All async file wrappers inherit from `AsyncBase` (or `AsyncIndirectBase` for stdio), which provides `__aiter__` and `__anext__` for async iteration via `readline()`.

```
AsyncBase
├── AsyncBufferedIOBase        — wraps io.BufferedWriter / io.BufferedIOBase
├── AsyncBufferedReader        — wraps io.BufferedReader / io.BufferedRandom (adds peek)
├── AsyncFileIO                — wraps io.FileIO (adds readall)
└── AsyncTextIOWrapper         — wraps io.TextIOWrapper

AsyncIndirectBase (AsyncBase)
├── AsyncIndirectBufferedIOBase   — for sys.stdin.buffer etc.
├── AsyncIndirectBufferedReader   — adds peek
├── AsyncIndirectFileIO
└── AsyncTextIndirectIOWrapper    — for sys.stdin, sys.stdout, sys.stderr
```

## Method categories

Methods fall into two categories:

### Delegated to executor (async, must await)

These run in the thread pool via `loop.run_in_executor()`:

| Class | Delegated methods |
|---|---|
| `AsyncBufferedIOBase` | close, flush, isatty, read, read1, readinto, readline, readlines, seek, seekable, tell, truncate, writable, write, writelines |
| `AsyncBufferedReader` | all above + peek |
| `AsyncFileIO` | close, flush, isatty, read, readall, readinto, readline, readlines, seek, seekable, tell, truncate, writable, write, writelines |
| `AsyncTextIOWrapper` | close, flush, isatty, read, readable, readline, readlines, seek, seekable, tell, truncate, write, writable, writelines |

### Proxied directly (synchronous)

These call the underlying file object directly — no await needed:

| Class | Direct methods | Direct properties |
|---|---|---|
| `AsyncBufferedIOBase` | detach, fileno, readable | closed, raw, name, mode |
| `AsyncTextIOWrapper` | detach, fileno, readable | buffer, closed, encoding, errors, line_buffering, newlines, name, mode |

## The `wrap` dispatcher

`aiofiles.threadpool.wrap()` is a `singledispatch` function that selects the correct wrapper class based on the underlying file type:

- `TextIOBase` → `AsyncTextIOWrapper`
- `BufferedWriter`, `BufferedIOBase` → `AsyncBufferedIOBase`
- `BufferedReader`, `BufferedRandom` → `AsyncBufferedReader`
- `FileIO` → `AsyncFileIO`

To register a custom type (e.g., for mocking):

```python
aiofiles.threadpool.wrap.register(mock.MagicMock)(
    lambda *args, **kwargs: aiofiles.threadpool.AsyncBufferedIOBase(*args, **kwargs)
)
```

## `AiofilesContextManager`

`aiofiles.open()` returns an `AiofilesContextManager`, which is both an `Awaitable` and an `AbstractAsyncContextManager`. It:

1. Awaits the internal `_open()` coroutine lazily on first await or `__aenter__`
2. On `__aexit__`, runs the underlying file's `__exit__` in the executor
3. Resets `_obj` to None after exit

This means `async with aiofiles.open(...) as f:` is the correct usage pattern.

## `sync_open`

`aiofiles.threadpool.sync_open` is simply `builtins.open`. It is called inside the executor to perform the actual blocking file open. Patch this for mocking.

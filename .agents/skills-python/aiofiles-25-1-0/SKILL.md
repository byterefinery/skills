---
name: aiofiles-25-1-0
description: Async file I/O for Python asyncio applications. Use when reading, writing, or manipulating local disk files inside async code without blocking the event loop. Covers aiofiles.open(), async os/os.path operations, async tempfile, and async stdin/stdout/stderr access. Python 3.9+.
license: Apache-2.0
compatibility: Requires Python 3.9+
metadata:
  tags:
    - asyncio
    - file-io
    - python
---

# aiofiles 25.1.0

## Overview

aiofiles provides non-blocking file I/O for asyncio applications. Local disk operations are inherently blocking; aiofiles delegates them to a thread-pool executor so the event loop stays responsive.

The library exposes three main surfaces:

- **`aiofiles.open()`** — async file opening with text, binary, and buffered modes. Returned file objects support `await f.read()`, `async for line in f`, etc.
- **`aiofiles.os`** and **`aiofiles.os.path`** — async wrappers around `os` and `os.path` functions that deal with files (stat, rename, listdir, exists, etc.).
- **`aiofiles.tempfile`** — async versions of `TemporaryFile`, `NamedTemporaryFile`, `SpooledTemporaryFile`, and `TemporaryDirectory`.

All operations run through `loop.run_in_executor()` by default, using the event loop's default executor. A custom executor can be passed via the `executor` keyword.

## Usage

### Opening files

```python
import aiofiles

# Text mode
async with aiofiles.open("data.txt", mode="r", encoding="utf-8") as f:
    contents = await f.read()
    async for line in f:
        print(line)

# Binary mode
async with aiofiles.open("image.png", mode="rb") as f:
    data = await f.read()
```

`aiofiles.open()` mirrors the builtin `open()` signature — mode, buffering, encoding, errors, newline, closefd, opener — plus optional `loop` and `executor` kwargs.

### Stdio access

```python
import aiofiles

await aiofiles.stdout.write("hello\n")
await aiofiles.stdout.flush()

line = await aiofiles.stdin.readline()
```

Also available: `aiofiles.stdin_bytes`, `aiofiles.stdout_bytes`, `aiofiles.stderr_bytes` for raw byte streams.

### Async os operations

```python
from aiofiles import os as aioos
from aiofiles import os as aios

# File/directory operations
await aioos.mkdir("new_dir")
await aioos.rename("old.txt", "new.txt")
await aioos.remove("file.txt")
entries = await aioos.listdir(".")

# Path checks
exists = await aioos.path.exists("file.txt")
size = await aioos.path.getsize("file.txt")
```

### Async temp files

```python
import aiofiles.tempfile

# Named temp file
async with aiofiles.tempfile.NamedTemporaryFile("w+", delete=True) as f:
    await f.write("data")
    await f.seek(0)
    content = await f.read()

# Temp directory
async with aiofiles.tempfile.TemporaryDirectory() as dir_path:
    # dir_path is a string path
    pass
```

## Gotchas

- **`aiofiles.open()` returns a context manager, not an awaitable directly** — it returns `AiofilesContextManager`, which works with `async with`. Do not `await aiofiles.open(...)` standalone; use `async with aiofiles.open(...) as f:`.

- **Properties are synchronous, methods are async** — on async file objects, properties like `.name`, `.mode`, `.closed`, `.encoding` are read directly (no await). Methods like `.read()`, `.write()`, `.seek()`, `.close()` must be awaited.

- **`detach()`, `fileno()`, `readable()` are synchronous** — these proxy directly to the underlying file object and return immediately. They do not go through the executor.

- **SpooledTemporaryFile has mixed sync/async behavior** — when data fits in memory (not yet "rolled" to disk), write/read operations execute synchronously. Once the file rolls over to disk, operations become async executor calls. Use `await f.rollover()` to force disk write.

- **`TemporaryDirectory` context manager returns the path string** — `async with aiofiles.tempfile.TemporaryDirectory() as dir_path:` gives you a string path, not an object. Call `await obj.cleanup()` if you need manual cleanup outside the context manager.

- **No zero-copy on most platforms** — despite the name, aiofiles does not use `os.sendfile` for regular file reads/writes. It copies data through the thread pool. For true zero-copy, call `await aiofiles.os.sendfile(src_fd, dst_fd, offset, count)` directly (platform-dependent availability).

- **`aiofiles.os` does not wrap all `os` functions** — only file-related functions are wrapped. Functions like `os.environ`, `os.system`, `os.fork` are not available. Use regular `os` for those.

- **Python 3.12+ `delete_on_close` parameter** — `NamedTemporaryFile` accepts `delete_on_close=True` (Python 3.12+). On older Python, only `delete` is available.

- **Mocking for tests** — patch `aiofiles.threadpool.sync_open` and register the mock return type with `aiofiles.threadpool.wrap.register()`. See references for the full pattern.

## References

- [01-file-classes](references/01-file-classes.md) — Async file wrapper classes and their method sets
- [02-os-module](references/02-os-module.md) — Full listing of `aiofiles.os` and `aiofiles.os.path` functions
- [03-tempfile](references/03-tempfile.md) — Temp file classes and TemporaryDirectory details
- [04-testing](references/04-testing.md) — Mocking patterns for unit tests

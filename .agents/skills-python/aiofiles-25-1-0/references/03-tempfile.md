# aiofiles.tempfile

## TemporaryFile

```python
async with aiofiles.tempfile.TemporaryFile("wb") as f:
    await f.write(b"Hello, World!")
    await f.seek(0)
    data = await f.read()
```

Creates an unnamed temporary file. The file is deleted automatically when closed. Returns a wrapped async file object (type depends on mode — `AsyncBufferedIOBase` for binary, `AsyncTextIOWrapper` for text).

Parameters: `mode`, `buffering`, `encoding`, `newline`, `suffix`, `prefix`, `dir`, `loop`, `executor`.

## NamedTemporaryFile

```python
async with aiofiles.tempfile.NamedTemporaryFile("w+", delete=True) as f:
    print(f.name)  # accessible path
    await f.write("data")
```

Creates a named temporary file. The `.name` property gives the filesystem path.

- Python 3.12+: accepts `delete_on_close=True` parameter
- Python < 3.12: uses `delete=True` and exposes `.delete` property on the returned object

When `delete=True` (default), the file is removed on close.

## SpooledTemporaryFile

```python
async with aiofiles.tempfile.SpooledTemporaryFile(max_size=1024*1024) as f:
    await f.write(data)
```

Buffers data in memory until `max_size` bytes, then rolls over to a real temp file on disk.

### Rollover behavior

- Before rollover: `write()` and `writelines()` execute synchronously (in-memory), but still return coroutines for API consistency
- After rollover: operations are delegated to the executor
- `await f.rollover()` forces immediate flush to disk
- Internal `_check()` method auto-triggers rollover when `tell() > max_size`

### Methods

| Method | Type |
|---|---|
| `close`, `flush`, `isatty`, `read`, `readline`, `readlines`, `seek`, `tell`, `truncate` | Conditional — sync before rollover, async after |
| `fileno`, `rollover` | Always async (executor) |
| `write`, `writelines` | Custom — check rollover, sync or async |
| `closed`, `encoding`, `mode`, `name`, `newlines` | Properties (sync) |

## TemporaryDirectory

```python
async with aiofiles.tempfile.TemporaryDirectory() as dir_path:
    # dir_path is a string, not an object
    filename = os.path.join(dir_path, "file.txt")
    # work with files inside
# Automatically cleaned up on exit
```

Key difference: `__aenter__` returns the directory path string (matching the sync `tempfile.TemporaryDirectory` behavior), not the wrapper object.

### Manual cleanup

```python
temp_dir_ctx = aiofiles.tempfile.TemporaryDirectory()
dir_path = await temp_dir_ctx.__aenter__()
# ... use dir_path ...
await temp_dir_ctx.cleanup()  # explicit cleanup
```

The `cleanup()` method is async (runs in executor). `close()` is an alias for `cleanup()`.

### Properties

- `name` — the directory path string (sync property)

## Common parameters

All tempfile functions accept:

- `loop` — asyncio event loop (defaults to running loop)
- `executor` — custom executor (defaults to loop's default executor)

File-based functions also accept standard tempfile parameters: `mode`, `buffering`, `encoding`, `newline`, `suffix`, `prefix`, `dir`.

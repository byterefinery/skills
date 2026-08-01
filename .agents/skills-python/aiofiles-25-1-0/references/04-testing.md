# Testing with aiofiles

## Mocking file I/O

Real file I/O can be mocked by patching `aiofiles.threadpool.sync_open` and registering the mock type with the `wrap` dispatcher.

### Full pattern

```python
import mock
import aiofiles
from aiofiles.threadpool import wrap, AsyncBufferedIOBase

# Register mock type with the wrap dispatcher
wrap.register(mock.MagicMock)(
    lambda *args, **kwargs: AsyncBufferedIOBase(*args, **kwargs)
)

async def test_file_write_and_read():
    write_data = "data"
    read_file_chunks = [b"chunk 1", b"chunk 2", b"chunk 3", b""]
    file_chunks_iter = iter(read_file_chunks)

    mock_file_stream = mock.MagicMock(
        read=lambda *args, **kwargs: next(file_chunks_iter)
    )

    with mock.patch(
        "aiofiles.threadpool.sync_open",
        return_value=mock_file_stream
    ) as mock_open:
        async with aiofiles.open("filename", "w") as f:
            await f.write(write_data)
            assert await f.read() == b"chunk 1"

        mock_file_stream.write.assert_called_once_with(write_data)
```

### Key points

1. **Patch `aiofiles.threadpool.sync_open`** — this is the `builtins.open` alias called inside the executor
2. **Register the mock type** — `wrap.register(mock.MagicMock)(...)` tells the singledispatch which async wrapper class to use for the mock
3. **Configure mock methods** — set up `read()`, `write()`, etc. on the mock file stream to return expected values
4. **Use `async with`** — the context manager pattern works normally with mocks

## Testing with pytest-asyncio

aiofiles works naturally with `pytest-asyncio`:

```python
import pytest
import aiofiles

@pytest.mark.asyncio
async def test_read_file(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello")

    async with aiofiles.open(str(test_file), mode="r") as f:
        content = await f.read()
    assert content == "hello"
```

pyproject.toml config:
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

## Testing os operations

Mock `aiofiles.os` functions by patching the underlying `os` function:

```python
from unittest import mock
import aiofiles.os as aioos

async def test_mkdir():
    with mock.patch("os.mkdir") as mock_mkdir:
        await aioos.mkdir("/fake/dir")
        mock_mkdir.assert_called_once_with("/fake/dir")
```

Since `aiofiles.os` functions are thin wrappers via `wrap()`, patching at the `os` level works directly.

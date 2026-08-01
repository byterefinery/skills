# aiofiles.os and aiofiles.os.path

Both modules wrap standard library functions using the `wrap()` utility from `aiofiles.base`, which delegates the call to a thread-pool executor.

## aiofiles.os

File-related `os` functions available as coroutines:

### Always available

| Function | Signature |
|---|---|
| `access` | `access(path, mode, *, dir_fd=None, effective_ids=False)` |
| `getcwd` | `getcwd()` |
| `listdir` | `listdir(path, *, dir_fd=None)` |
| `makedirs` | `makedirs(name, mode=0o777, exist_ok=False)` |
| `mkdir` | `mkdir(path, mode=0o777, *, dir_fd=None)` |
| `readlink` | `readlink(path, *, dir_fd=None)` |
| `remove` | `remove(path)` |
| `removedirs` | `removedirs(name)` |
| `rename` | `rename(src, dst, *, src_dir_fd=None, dst_dir_fd=None)` |
| `renames` | `renames(old, new)` |
| `replace` | `replace(src, dst)` |
| `rmdir` | `rmdir(path, *, dir_fd=None)` |
| `scandir` | `scandir(path)` |
| `stat` | `stat(path, *, dir_fd=None, follow_symlinks=True)` |
| `symlink` | `symlink(src, dst, *, target_is_directory=False, dir_fd=None)` |
| `unlink` | `unlink(path, *, dir_fd=None)` |

### Platform-dependent

| Function | Availability |
|---|---|
| `link` | `os.link` must exist |
| `sendfile` | `os.sendfile` must exist (Linux, BSD) |
| `statvfs` | `os.statvfs` must exist (Unix) |

## aiofiles.os.path

Access as `aiofiles.os.path` or import directly:

```python
from aiofiles import os as aioos
await aioos.path.exists("/tmp/file.txt")

from aiofiles.os import path
await path.getsize("/tmp/file.txt")
```

| Function | Description |
|---|---|
| `abspath` | Return absolute path |
| `getatime` | Last access time |
| `getctime` | Creation/change time |
| `getmtime` | Last modification time |
| `getsize` | File size in bytes |
| `exists` | Path exists |
| `isdir` | Path is a directory |
| `isfile` | Path is a file |
| `islink` | Path is a symbolic link |
| `ismount` | Path is a mount point |
| `samefile` | Two paths refer to same file |
| `sameopenfile` | Two open file objects refer to same file |

## The `wrap` utility

`aiofiles.os.wrap(func)` is exposed publicly, allowing you to create async wrappers for any `os` function not already included:

```python
import os
from aiofiles.os import wrap

async_chmod = wrap(os.chmod)
await async_chmod("file.txt", 0o644)
```

All wrapped functions accept optional `loop` and `executor` keyword arguments.

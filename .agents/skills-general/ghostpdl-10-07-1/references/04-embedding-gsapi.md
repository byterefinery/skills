# Embedding — gsapi C/Python/Java/C# API

## Overview

Ghostscript exposes its full engine via the `gsapi` C interface (`psi/iapi.h`). The library can be linked statically or as a shared library (`libgs.so` / `libgs.dylib` / `gsdll32.dll`). Official bindings exist for C, Python, Java, and C#.

**Threading:** Unless compiled with `--enable-threading`, Ghostscript supports only one active instance at a time. The gsapi enforces this with a global counter.

## C API

### Header

```c
#include "psi/iapi.h"
#include "psi/ierrors.h"
```

### Lifecycle

```c
#include "psi/iapi.h"

void *instance = NULL;
int code;

// 1. Create instance
code = gsapi_new_instance(&instance, NULL);
if (code < 0) { /* handle error */ }

// 2. (Optional) Set stdio callbacks
gsapi_set_stdio(instance, stdin_fn, stdout_fn, stderr_fn);

// 3. (Optional) Set arg encoding
gsapi_set_arg_encoding(instance, GS_ARG_ENCODING_UTF8);

// 4. Initialize with arguments
const char *args[] = {
    "gs",
    "-dBATCH", "-dNOPAUSE",
    "-sDEVICE=pdfwrite",
    "-sOutputFile=output.pdf",
    "input.ps"
};
code = gsapi_init_with_args(instance, sizeof(args)/sizeof(args[0]), args);

// 5. (Optional) Run additional code
if (code == 0) {
    code = gsapi_run_string(instance, "(Hello from API)\nprint", 0, NULL);
}

// 6. Exit
if (code == 0 || code == -1) {  // -1 is GS_EXIT_CODE (normal exit)
    code = gsapi_exit(instance);
}

// 7. Delete instance
gsapi_delete_instance(instance);
```

### Key Functions

```c
// Get version info
gsapi_revision_t rev;
gsapi_revision(&rev, sizeof(rev));
// rev.product, rev.copyright, rev.revision, rev.revisiondate

// Run a file
int code = gsapi_run_file(instance, "script.ps", NULL, 0);

// Run PostScript string
int code = gsapi_run_string(instance, "code", length, 0);
// Flags: 0=normal, 1=stop-on-error, 2=continue, 4=immediate

// Run string with continuation
int code = gsapi_run_string_begin(instance, "code", length, 0);
// ... process ...
int code = gsapi_run_string_continue(instance, "more", length, 0);
int code = gsapi_run_string_end(instance, "final", length, 0);

// Set default device list
gsapi_set_default_device_list(instance, "png16m,pdfwrite", 18);

// Get default device list
char *list;
int len;
gsapi_get_default_device_list(instance, &list, &len);
```

### Stdio Callbacks

```c
int my_stdin(void *handle, char *buf, int len) {
    // Read into buf, return bytes read, 0 for EOF, -1 for error
    return fread(buf, 1, len, stdin_file);
}

int my_stdout(void *handle, const char *str, int len) {
    // Write str, return bytes written
    return fwrite(str, 1, len, stdout_file);
}

int my_stderr(void *handle, const char *str, int len) {
    return fwrite(str, 1, len, stderr_file);
}

// Register callbacks
gsapi_set_stdio(instance, my_stdin, my_stdout, my_stderr);
```

### Building as Shared Library

```bash
# Unix
make so          # builds libgs.so / libgs.dylib

# Link against it
gcc -o myapp myapp.c -L. -lgs -lpthread -lm
```

## Python API

### Using ctypes (bundled)

Ghostscript ships `demos/python/gsapi.py` — a ctypes wrapper.

```python
import gsapi

# Create instance
instance = gsapi.gsapi_new_instance(0)
gsapi.gsapi_set_arg_encoding(instance, gsapi.GS_ARG_ENCODING_UTF8)

# Initialize and run
code = gsapi.gsapi_init_with_args(instance, [
    "gs",
    "-dBATCH", "-dNOPAUSE",
    "-sDEVICE=pdfwrite",
    "-sOutputFile=output.pdf",
    "input.ps"
])

# Run additional PostScript
gsapi.gsapi_run_string(instance, "(Hello)\nprint", 0)

# Cleanup
gsapi.gsapi_exit(instance)
gsapi.gsapi_delete_instance(instance)
```

Environment variables for library location:
- `GSAPI_LIB` — exact path to shared library
- `GSAPI_LIBDIR` — directory containing shared library

### Building the Shared Library for Python

```bash
make sodebug     # Debug build of libgs.so
GSAPI_LIBDIR=sodebugbin python3 ./demos/python/gsapi.py
```

## Java API

### Structure

The Java binding is in `demos/java/`. It uses JNI to call into the Ghostscript DLL.

```java
import com.ghostgum.gsapi.GSAPI;
import com.ghostgum.gsapi.GSInstance;

public class Example {
    public static void main(String[] args) {
        GSAPI gsapi = new GSAPI();
        GSInstance instance = gsapi.newInstance();

        String[] gsArgs = {
            "gs",
            "-dBATCH", "-dNOPAUSE",
            "-sDEVICE=pdfwrite",
            "-sOutputFile=output.pdf",
            "input.ps"
        };

        int code = instance.initWithArgs(gsArgs);
        instance.exit();
        instance.delete();
    }
}
```

## C# API

### Structure

The C# binding is in `demos/csharp/`. It uses P/Invoke.

```csharp
using GhostAPI;

class Program {
    static void Main() {
        IntPtr instance;
        ghostapi.gsapi_new_instance(out instance, IntPtr.Zero);
        ghostapi.gsapi_set_arg_encoding(instance,
            (int)gsEncoding.GS_ARG_ENCODING_UTF8);

        string[] args = {
            "gs",
            "-dBATCH", "-dNOPAUSE",
            "-sDEVICE=pdfwrite",
            "-sOutputFile=output.pdf",
            "input.ps"
        };

        int code = ghostapi.gsapi_init_with_args(instance, args.Length, args);
        ghostapi.gsapi_exit(instance);
        ghostapi.gsapi_delete_instance(instance);
    }
}
```

## MATLAB API

The MATLAB binding is in `demos/MATLAB/`. It wraps the C API via MEX.

## Common Patterns

### Rasterize PDF to Memory Buffer

```c
// Set up a memory device
const char *args[] = {
    "gs", "-dBATCH", "-dNOPAUSE",
    "-sDEVICE=png16m", "-r300",
    "-sOutputFile=-",      // stdout
    "input.pdf"
};
// Capture stdout via callback to get the PNG data
```

### Progress Callbacks

```c
// Register a callout for progress tracking
gsapi_register_callout(instance, "Progress", progress_callback, NULL);
```

### Error Handling

```c
int code = gsapi_init_with_args(instance, argc, argv);
if (code < 0) {
    // Error occurred
    if (code == -1) {
        // GS_EXIT — normal exit (e.g., quit command in PS)
        // Call gsapi_exit() and gsapi_delete_instance()
    } else {
        // Actual error
        // Call gsapi_exit() and gsapi_delete_instance()
    }
} else if (code == 0) {
    // Success — can run more code or call gsapi_exit()
}
```

### Return Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `-1` | Exit (normal, e.g., `quit` in PostScript) |
| `< -1` | Error (negative error code from `ierrors.h`) |

Common error codes:
- `-100` — `gs_error_VMerror` (out of memory)
- `-256` — `gs_error_Fatal` (fatal error)
- `-260` — `gs_error_Invalidfileaccess` (file access denied)
- `-270` — `gs_error_IOError` (I/O error)
- `-281` — `gs_error_undefined` (undefined PostScript operator)

## Build Configuration for Embedding

```bash
# Build shared library
./configure --enable-shared
make so

# Build with threading support (allows multiple instances)
./configure --enable-shared --enable-threading
make so

# Build without unnecessary interpreters (smaller binary)
./configure --with-gs=gs --without-pcl --without-xps
make so
```

## Gotchas

- **Single instance limit** — Without `--enable-threading`, only one gsapi instance can be active. Creating a second returns an error.
- **Call `gsapi_exit()` before `gsapi_delete_instance()`** — If `gsapi_init_with_args()` succeeded, you must call `gsapi_exit()` first.
- **`-1` is not an error** — Return code `-1` means Ghostscript exited normally (e.g., `quit` command). Still call `gsapi_exit()` and `gsapi_delete_instance()`.
- **Arg encoding matters** — Call `gsapi_set_arg_encoding()` with `GS_ARG_ENCODING_UTF8` before `gsapi_init_with_args()` for proper Unicode handling.
- **Shared library path** — On Unix, `LD_LIBRARY_PATH` or `rpath` must include the directory containing `libgs.so`. On Windows, the DLL must be in PATH or next to the executable.
- **Resource files** — The shared library still needs access to `Resource/` files (CMaps, fonts, ICC profiles). Set `GS_LIB` or ensure the install prefix is correct.

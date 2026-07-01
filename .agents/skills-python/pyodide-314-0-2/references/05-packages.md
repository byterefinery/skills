# Package Management

## Overview

Pyodide has three layers of package management:

1. **Standard library** — always available after `loadPyodide()`
2. **Bundled packages** — pre-built wheels shipped with Pyodide, loaded via `loadPackage`
3. **PyPI packages** — pure Python wheels from PyPI, installed via `micropip`

## loadPackage (Bundled Packages)

Load packages from the Pyodide distribution. Supports dependency resolution for bundled packages.

```js
// Single package
await pyodide.loadPackage("numpy");

// Multiple packages
await pyodide.loadPackage(["numpy", "pandas", "matplotlib"]);

// Custom URL (no dependency resolution)
await pyodide.loadPackage("https://example.com/pkg-1.0-cp314-cp314-emscripten_3_1_59_wasm32.whl");
```

**Options:**

```js
await pyodide.loadPackage("numpy", {
  messageCallback: (msg) => console.log(msg),
  errorCallback: (msg) => console.error(msg),
  checkIntegrity: true,  // verify hash (default: true)
});
```

Returns `Promise<Array<PackageData>>` with package metadata.

### Checking Loaded Packages

```js
pyodide.loadedPackages; // Map<packageName, version>
pyodide.loadedPackages.get("numpy"); // "1.26.4" or similar
```

## loadPackagesFromImports (Auto-Load)

Inspect Python code and auto-load bundled packages for any imports found.

```js
await pyodide.loadPackagesFromImports(`
  import numpy as np
  import pandas as pd
  df = pd.DataFrame(np.random.rand(10, 3))
`);
```

Only loads bundled packages. Does not install from PyPI. Used by the REPL.

## micropip (PyPI + Bundled)

`micropip` is the full package installer. It handles:

- Pure Python wheels from PyPI
- Binary wasm32/emscripten wheels from JsDelivr CDN
- Custom URLs
- Dependency resolution

### Loading micropip

```js
// From JavaScript
await pyodide.loadPackage("micropip");
const micropip = pyodide.pyimport("micropip");
await micropip.install("package_name");

// From Python (auto-loads)
import micropip
await micropip.install("package_name")
```

### Installing Packages

```python
import micropip

# From PyPI (pure Python only)
await micropip.install("requests")

# Specific version
await micropip.install("numpy>=1.24")

# From custom URL (must be a .whl file)
await micropip.install("https://example.com/mypackage-1.0-py3-none-any.whl")

# Without dependency resolution
await micropip.install("mypackage", deps=False)

# From custom index URL
await micropip.install("mypackage", index_urls=["https://custom.pypi/simple/"])

# List installed packages
installed = await micropip.list()

# Upgrade
await micropip.install("package_name", upgrade=True)
```

### micropip vs loadPackage

| Feature | `micropip.install` | `pyodide.loadPackage` |
|---|---|---|
| PyPI packages | ✅ | ❌ |
| Bundled packages | ✅ | ✅ |
| Dependency resolution | ✅ | ✅ (bundled only) |
| Custom URLs | ✅ | ✅ |
| Overhead | Higher (Python) | Lower (JS) |
| Best for | General use | Minimal size, bundled-only |

## Package Wheel Naming

Pyodide wheels follow PEP 427 naming with wasm32 platform:

```
{distribution}-{version}(-{build tag})?-{python tag}-{abi tag}-{platform tag}.whl
```

Pyodide platform tag: `emscripten_3_1_59_wasm32`
Python tag: `cp314`
ABI tag: `cp314`

Example: `numpy-1.26.4-cp314-cp314-emscripten_3_1_59_wasm32.whl`

## Building Custom Packages

For packages with C extensions, use [pyodide-build](https://pyodide-build.readthedocs.io/):

```bash
pip install pyodide-build
pyodide build  # builds a wasm32 wheel
```

Pure Python packages work directly from PyPI via micropip.

## Standard Library Limitations

### Removed Modules

`curses`, `dbm`, `ensurepip`, `fcntl`, `grp`, `idlelib`, `lib2to3`, `msvcrt`, `pwd`, `resource`, `syslog`, `termios`, `tkinter`, `turtle`, `venv`, `winreg`, `winsound`.

### Not Working

`multiprocessing`, `threading` (can't start new threads), `socket` (browser only; works in Node with `useNodeSockFS`).

`pty`, `tty` — can't import (depend on removed `termios`).

### Limited Functionality

- `decimal` — Python implementation unavailable (C impl only)
- `pydoc` — requires `pydoc_data` package
- `webbrowser` — stubs for `open()`, `open_new()`, `open_new_tab()`
- `zoneinfo` — requires `tzdata` package
- `hashlib` — OpenSSL-dependent algorithms unavailable
- `ssl` — stub implementation, OpenSSL methods raise `NotImplementedError`

## Detecting Pyodide

```python
# Runtime detection
import sys
if sys.platform == "emscripten":
    # Running in Pyodide or any Emscripten build

if "pyodide" in sys.modules:
    # Specifically running in Pyodide

# Build-time detection
import os
if "PYODIDE" in os.environ:
    # Building for Pyodide
```

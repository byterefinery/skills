# Packages

## Contents

- What is available by default
- `micropip.install` (Python)
- `pyodide.loadPackage` (JavaScript)
- `pyodide.loadPackagesFromImports`
- Choosing between micropip and loadPackage
- Custom URLs, indexes, lockfiles
- CORS and integrity

After loading Pyodide, **only the Python standard library is available**.

## `micropip.install` (Python)

Async (`await micropip.install(...)`). Installs:

- pure Python wheels from PyPI
- pure Python and binary wasm32/emscripten wheels ("Pyodide packages") from the
  JsDelivr CDN or custom URLs

```python
import micropip
await micropip.install("snowballstemmer")
```

From JS:

```js
await pyodide.loadPackage("micropip");
const micropip = pyodide.pyimport("micropip");
await micropip.install("snowballstemmer");
```

Features:

- **Dependency resolution** (also for custom URL wheels).
- **File integrity validation** — downloaded wheel hashes are checked against
  pre-recorded digests from the PyPI JSON API.
- `index_urls` parameter — install from alternative indexes.
- **Arbitrary wheel URLs** — a requirement ending in `.whl` is treated as a
  URL; the wheel name must follow PEP 427 naming. Pass `deps=False` to skip
  dependency resolution.

If micropip cannot find a **pure Python wheel** (`*py3-none-any.whl`) on PyPI,
the install fails — either the package maintainer never uploaded a wheel, or
the package has binary extensions that need a Pyodide build (request Pyodide
support from maintainers, or install from a self-built wheel URL).

## `pyodide.loadPackage` (JavaScript)

Loads packages built with Pyodide (from the distribution or a custom URL).
Lower overhead than micropip, but more limited:

```js
await pyodide.loadPackage("numpy");
await pyodide.loadPackage(["cycler", "pytz"]);

// Custom URL — file name must be a valid wheel name
await pyodide.loadPackage("https://foo/bar/numpy-1.22.3-cp310-cp310-emscripten_3_1_13_wasm32.whl");
```

- Returns a Promise resolving when all packages finish loading.
- Official-repo packages: all dependencies load automatically. Custom-URL
  packages: **no** dependency resolution (use micropip for that).
- Loading a package twice is not permitted, except you may override a
  dependency by loading a custom URL with the same package name **before**
  loading the dependent package.

## `pyodide.loadPackagesFromImports`

```js
await pyodide.loadPackagesFromImports("import numpy as np\nnp.array([1,2,3])");
```

Inspects a code chunk with `pyodide.code.find_imports` and loads the
distribution packages it imports. The Pyodide REPL uses this so users can
import packages directly. It **only** downloads packages included in the
Pyodide distribution — never from PyPI. To change which packages are detected,
monkey-patch `pyodide.code.find_imports`.

## Choosing between micropip and loadPackage

Use `micropip.install` for everything, except:

- loading micropip itself (it is not importable until loaded),
- optimizing for size: you do not want to install micropip and do not need
  PyPI/dependency resolution.

Language does not matter — switch freely with `pyodide.pyimport` (JS side) or
`pyodide_js.loadPackage` (Python side).

## Custom URLs, indexes, lockfiles

- `micropip` — `index_urls` parameter for other indexes; `.whl` URLs directly.
- `loadPackage` — custom wheel URL as the package name; no dependency
  resolution.
- `loadPyodide` config — `lockFileURL` (custom lockfiles via
  `micropip.freeze`), `lockFileContents` (inline lockfile),
  `packageBaseUrl` (base for relative lockfile paths; must be set explicitly
  with inline lockfiles that use relative paths).

## CORS and integrity

Remote wheel servers must set CORS headers for browser installs. Third-party
CORS proxies work but skip integrity checks (security implication). PyPI
installs are hash-validated; arbitrary URLs are not.

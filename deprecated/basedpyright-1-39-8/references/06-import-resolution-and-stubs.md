# Import Resolution and Type Stubs Reference

## Import Resolution Order

For absolute imports, basedpyright resolves in this order:

1. **stubPath** — custom `.pyi` stubs from the configured stub path (default: `./typings`)
2. **Workspace code** — relative to execution environment root, then extra paths, then `src/` directory
3. **Installed packages** — via configured Python environment's `site-packages`:
   - Stub package (`<name>-stubs`, PEP 561)
   - Inline stub (`.pyi` shipped with the package)
   - Inlined types (`.py` files in a `py.typed` package)
   - Library implementation (`.py` files, if `useLibraryCodeForTypes: true`)
4. **Stdlib typeshed** — bundled typeshed or custom `typeshedPath`
5. **Third-party typeshed** — stubs from typeshed's `stubs/` directory
6. **Sibling modules** — same directory and parent directories within workspace root

Relative imports (starting with `.`) resolve relative to the importing file's path.

## Configuring the Python Environment

Priority order for determining which Python interpreter to use:

1. `venv` + `venvPath` settings (discouraged)
2. `python.pythonPath` setting (from IDE or `--pythonpath` CLI flag)
3. Auto-detected `.venv` at project root (basedpyright default)
4. System `python` as fallback

Use `--pythonpath /path/to/venv/bin/python` for the most robust configuration.

## Debugging Import Issues

Enable verbose logging:
```bash
basedpyright --verbose
```

Or in config:
```json
{ "verboseOutput": true }
```

This shows the full resolution path for each import, helping identify why a module is not found.

## Type Stub Files

Type stubs (`.pyi` files) define the public interface of a library without implementation details.

### Why stubs matter

- Without stubs, imported symbols have type `Unknown`
- Wildcard imports (`from foo import *`) don't populate specific symbol names
- Type information inferred from source is often incomplete
- Analyzing large libraries slows down type checking

### Creating stubs manually

Place `.pyi` files in the `stubPath` directory (default: `./typings`), organized by package:

```
typings/
├── requests/
│   ├── __init__.pyi
│   └── api.pyi
└── my_library/
    └── __init__.pyi
```

Stub syntax uses `...` for implementation:

```python
# my_stub.pyi
def fetch(url: str, timeout: float = 30) -> Response: ...
class Response:
    status_code: int
    def json(self) -> dict[str, object]: ...
```

### Generating stubs via CLI

```bash
basedpyright --createstub django
```

Generates draft stubs in the `stubPath` directory. Clean up afterward — generated stubs often need manual fixes.

### Generating stubs in the IDE

1. Enable `reportMissingTypeStubs` in config
2. Hover over the missing-stubs error
3. Click "Create Type Stub For XXX" quick fix

### Common stub cleanup tasks

1. **Re-exports** — pyright removes unused imports, but some are intentional re-exports. Add them back manually (not needed in `__init__.pyi`).
2. **Try/except imports** — omitted in stubs since they can't be evaluated statically. Add back manually.
3. **Untyped decorators** — annotate with a TypeVar:

```python
from typing import Any, Callable, TypeVar

_FuncT = TypeVar("_FuncT", bound=Callable[..., Any])

def my_decorator(*args, **kw) -> Callable[[_FuncT], _FuncT]: ...
```

## Editable Installs

Static analysis tools need `.pth` files with file paths, not import hooks.

| Build Backend | Default behavior | How to ensure `.pth` files |
|--------------|-----------------|--------------------------|
| **setuptools** | Import hooks possible | Use [compat mode](https://setuptools.pypa.io/en/latest/userguide/development_mode.html#legacy-behavior) or [strict mode](https://setuptools.pypa.io/en/latest/userguide/development_mode.html#strict-editable-installs) |
| **uv** | `.pth` files by default | No action needed |
| **Hatchling** | `.pth` files by default | Don't set `dev-mode-exact = true` |
| **PDM** | `.pth` files by default | Don't set `editable-backend = "editables"` |

If your editable install uses import hooks, basedpyright cannot resolve module locations.

## py.typed Packages

A `py.typed` marker file (PEP 561) indicates that a package provides inline type annotations. basedpyright reads these annotations directly from `.py` files.

To mark your own package as typed, add an empty `py.typed` file to the package root:

```
mypackage/
├── __init__.py
├── py.typed       # empty file
└── module.py      # with type annotations
```

## `--verifytypes`

Verify completeness of types in a `py.typed` package:

```bash
basedpyright --verifytypes mypackage
```

Use `--ignoreexternal` to skip external imports during verification. Useful for library maintainers ensuring their package is fully typed.

## Import Resolution Tips

- **Prefer absolute imports** — `from pkg.module import func` instead of relative when possible
- **Use `executionEnvironments`** for projects with different Python versions or search paths per subdirectory
- **Set `extraPaths`** if your project structure doesn't follow the `src/` layout convention
- **Pin `pythonVersion`** in config to catch version-specific type issues early
- **Use `strict` paths** to gradually apply strict mode to well-typed subdirectories

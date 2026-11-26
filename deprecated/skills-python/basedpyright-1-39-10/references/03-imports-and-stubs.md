# Imports and type stubs

## Contents

- [Import resolution order](#import-resolution-order)
- [Configuring the Python environment](#configuring-the-python-environment)
- [Editable installs](#editable-installs)
- [Import statement semantics](#import-statement-semantics)
- [Type stub files](#type-stub-files)
- [Generating stubs with --createstub](#generating-stubs-with-createstub)
- [Custom builtins](#custom-builtins)
- [Debugging import problems](#debugging-import-problems)

## Import resolution order

Relative imports (leading dot) resolve against the importing file's path. Absolute
imports try, in order:

1. **stubPath** — custom stubs from the `stubPath` setting (default `./typings`)
2. **Workspace code**
   - relative to the execution environment's root (or workspace root)
   - then each `extraPaths` entry, in order
   - then the local `src/` directory if no execution environment is configured
3. **Installed packages** — via the configured Python environment's `site-packages`:
   - a `-stubs` companion package (PEP 561), e.g. `requests-stubs`
   - inline `.pyi` stubs shipped in the package
   - inlined `.py` annotations if the package has a `py.typed` marker (PEP 561)
   - the library `.py` source itself, if `useLibraryCodeForTypes` is `true` (default) —
     types may be incomplete
4. **Stdlib typeshed stubs** (bundled, or from `typeshedPath`)
5. **Third-party typeshed stubs** (same)
6. **Sibling-directory fallback** — for absolute imports, try the importing file's
   directory and parent directories under the workspace root (covers running scripts
   from subdirectories)

A package without `py.typed` and without stubs is treated as fully untyped: all
imported symbols are `Unknown`, and `from foo import *` populates nothing.

## Configuring the Python environment

No environment is required if all imports resolve from local files and stubs.
Otherwise, basedpyright determines the interpreter in priority order:

1. `venv` + `venvPath` (config or language-server setting) — least robust, discouraged
2. `python.pythonPath` (language-server setting; the VS Code Python extension's
   environment picker works here)
3. A virtual environment in a `.venv` folder at the project root — basedpyright's
   automatic default, matching what uv and most tools create
4. The default `python` on the PATH

The `--pythonpath` CLI flag corresponds to (2); it cannot be combined with
`--venvpath`. Set `pythonVersion` in the config only when it differs from the project
environment — otherwise it conflicts with the interpreter's real version.

## Editable installs

Static analysis cannot use editable installs implemented with import hooks (they
require executing Python code). Configure the editable install to use path-based `.pth`
files instead:

- **setuptools** — legacy (compat) mode or strict mode development installs
- **uv** — path-based `.pth` files by default
- **hatchling** — path-based by default; import hooks only if `dev-mode-exact = true`
- **PDM** — path-based by default; import hooks only if `editable-backend = "editables"`

## Import statement semantics

Pyright intentionally does not model most import loader side effects; relying on them
is considered a bug. What it does model:

- `import a.b.c` (no alias) is treated as also loading `a` and `a.b`, so all three are
  usable afterwards. With an alias (`import a.b.c as abc`), only `abc` is bound.
- In an `__init__.py`, `from . import a` and `from .a import b` both bind the local
  name `a` to the submodule.

Do not rely on, e.g., `import a` in one file exposing `a.b` in another file just
because some other file did `import a.b` — that depends on execution order and is
unsupported.

## Type stubs

Stubs are `.pyi` files describing a library's public interface (bodies can be `...`).
Resolution always prefers a stub over `.py` source. If an external import has no stub
and its package has no `py.typed`, its symbols are `Unknown` — fix by:

1. upgrading the package (many ship inline types now),
2. installing a `-stubs` companion package if one exists,
3. writing a minimal custom stub covering only the consumed interface, under `stubPath`
   (default `./typings`), one subdirectory per package — check it in,

and enabling `reportMissingTypeStubs` (warning by default in `recommended`) plus CI to
stay type-clean.

If `reportMissingTypeStubs` fires for a package that clearly contains annotations, the
package is probably missing the `py.typed` marker file.

## Generating stubs with --createstub

```bash
basedpyright --createstub django
```

Run inside the configured project (the target library must be installed in the
environment used for import resolution). Drafts are written to `stubPath`. In the
editor, hover a `reportMissingTypeStubs` diagnostic and use the "Create Type Stub For
XXX" code action.

Generated drafts need cleanup before committing:

1. **Unreferenced imports are culled** — re-exports (imported but not used inside the
   module) must be added back manually; `__init__.pyi` files are not culled
2. **`try`-wrapped imports are dropped** — stubs cannot be evaluated statically, add
   them back
3. **Untyped decorators hide signatures** — annotate pass-through decorators, e.g.
   `def my_decorator(*args, **kw) -> Callable[[_FuncT], _FuncT]` with a
   `TypeVar(bound=Callable[..., Any])`; enable `reportUntypedFunctionDecorator` and
   `reportUntypedClassDecorator` to find them

## Custom builtins

Environments that inject extra symbols into every module (beyond the stdlib
`builtins`) need a local `__builtins__.pyi` stub, placed at the project root or under
`stubPath`, declaring those extra names.

## Debugging import problems

Pass `--verbose` (or set `verboseOutput: true`) to log the resolution process; in VS
Code it appears in the Output panel under "Pyright". Include this log when reporting
import-resolution bugs.

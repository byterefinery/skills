# Import Resolution and Type Stubs

## Absolute import resolution order

1. **stubPath** — custom stub directory (default `./typings`).
2. **Workspace code** — relative to the execution environment root (or workspace root),
   then `extraPaths` entries (globs allowed), then a local `src/` directory if no execution
   environment is configured.
3. **Installed packages** in the configured Python environment's `site-packages`:
   stub package (`<name>-stubs`) first, then inline `.pyi`, then `py.typed`-marked source,
   then raw library `.py` if `useLibraryCodeForTypes` is true (default).
4. **Bundled stdlib typeshed** (or `typeshedPath` override).
5. **Third-party typeshed** stubs.
6. Fallback: import from the importing file's own directory and parent directories within
   the workspace root (script-style execution assumption).

Relative imports (leading dots) resolve against the importing file's path directly.

## Configuring the Python environment

Priority order for which interpreter/packages are used:

1. `venv` + `venvPath`/`--venvpath` — discouraged in basedpyright.
2. `python.pythonPath` (language server setting; VS Code's Python extension picker feeds this).
3. **Auto-detected `.venv` at project root** — basedpyright-specific default; this is why
   uv-managed projects usually need no configuration at all.
4. Fallback: whatever `python` resolves to on the shell PATH.

CLI equivalent: `--pythonpath <interpreter>` (preferred) or `--venvpath <dir>` (discouraged).

## Editable installs

Static tools cannot execute import hooks, so editable installs must use path-based `.pth`
files, not `import`-prefixed hook lines:

- **uv** — uses `.pth` files by default; no action needed.
- **Hatchling** — path-based by default; only breaks if you set `dev-mode-exact = true`.
- **setuptools** — use compat or strict editable mode, not the legacy import hook.
- **PDM** — path-based by default; breaks only with `editable-backend = "editables"`.

## Debugging resolution problems

Run with `--verbose` (or `"verboseOutput": true` in config) to see which paths were tried.
In VS Code, the same log appears in the Output panel under "Pyright". Include this output
when reporting import-resolution bugs.

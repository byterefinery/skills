# Install, CLI, execution options, deployment

## Getting Brython

**No install (CDN)** — include the scripts from a CDN:

```xml
<script src="https://cdn.jsdelivr.net/npm/brython@3/brython.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/brython@3/brython_stdlib.js"></script>
```

Pin the minor version with `brython@3.15`, the micro with `brython@3.15.0`. Also available from cdnjs with the same versioned URL pattern (the docs show `https://cdnjs.cloudflare.com/ajax/libs/brython/3.14.0/brython.min.js` and `brython_stdlib.min.js`).

**Local install** — `pip install brython`, then in an empty directory:

```console
brython-cli install
```

(alternative: download `Brython-x.y.z.zip` from the GitHub releases page). The directory gets `brython.js`, `brython_stdlib.js`, `index.html`, `demo.html` (the HTML pages are skipped with `--no-demo`). `brython.js` includes `browser`, `browser.html`, `javascript`; add `brython_stdlib.js` when the app imports stdlib modules. Update with `pip install brython --upgrade` then `brython-cli update`.

## brython-cli subcommands

- `install` (alias `init`) — initialize an empty directory; `--install-dir DIR`, `--no-demo`
- `update` — replace `brython.js` / `brython_stdlib.js` in place; `--update-dir DIR`
- `add_package NAME` — copy an already-installed pure-Python CPython package into the project's `Lib/site-packages` (optionally `--dest-dir DIR`)
- `make_package NAME` — generate a loadable `NAME.brython.js` file from a directory of modules; `--src-dir`, `--exclude-dirs`, `-o/--output-path`
- `make_modules` — generate `brython_modules.js` holding only the modules the application uses (parses all scripts/modules/HTML in the directory tree); `-o/--output-path`, `--reset` (restore from stdlib), `--modules_paths FILE`
- `start_server [PORT]` — development server (aiohttp), `--bind ADDRESS` (default `localhost`, default port 8000); explicitly not meant for production
- `make_dist` — create a CPython package (in `__dist__` with `setup.py`) for publishing the application on PyPI; writes `brython_setup.json` with package metadata on first run
- `make_file_system NAME [PREFIX]` — build a virtual file system (single JS file with all the files of a directory)
- `--version` — print the version

`make_modules` requires a CPython version compatible with the app code (e.g. `match/case` needs CPython 3.10+), since it parses the source.

## Execution options

Page-level options live in a `<brython-options>` tag, placed in `<body>` (not `<head>`):

```xml
<brython-options debug="1" cache="true">
</brython-options>
```

Script-level options are attributes of the `<script>` tag and take precedence over page-level ones.

Page-level only:

- `ids` — space-separated list of script `id`s to execute (all by default; empty string runs none)
- `indexedDB` — allow caching compiled stdlib modules in IndexedDB (default `true`)

Page or script level:

- `args` — command-line arguments, available as `sys.argv` (strings)
- `cache` — use browser cache for Ajax module imports, `<script src="...py">` loads, and `open()` (default `false`)
- `debug` — 1 (default) prints errors to the console/`sys.stderr`; 2 also prints the generated JavaScript; 10 also prints imported modules
- `js_tab` — indent (1–4) of the generated JavaScript, default 2
- `pythonpath` — space-separated paths for module search
- `static_stdlib_import` — use the static mapping table in `stdlib_paths.js` (default `true`)

Pre-3.12 syntax `<body onload="brython({debug: 2})">` still works for backwards compatibility; if both `<brython-options>` and `brython()` are present, the values passed to `brython()` win.

## Running and serving

HTML files can be opened directly, but a web server is recommended:

```console
python -m http.server        # port 8000 by default
python -m http.server 8001   # custom port
```

For development inside the brython repository, download the "site mirror" zip (`BrythonX.Y.Z_site_mirror`) and run `python server.py` from its root (options `--port N`, `--no-docs`); pages are served from `www/` and `static_doc` is generated unless `--no-docs`.

## file:// limitations

Under the `file://` protocol (File/Open) Ajax calls are blocked, so:

- external scripts via `<script type="text/python" src="test.py">` do not load
- modules/packages in the app's own directory cannot be imported
- `open()` cannot read files

Stdlib modules (via `brython_stdlib.js`), `.brython.js` packages, and `brython_modules.js` still work.

## Script file extension

External Python scripts are usually `.py`, but some servers treat an Ajax call to `.py` as a request to execute it on the server. In that case rename the file, e.g. `src="test.bry"`.

## Deployment

- **Plain upload** — upload the whole application directory to the server.
- **PyPI package** — `brython-cli make_dist` in the app directory creates `__dist__/` with `setup.py`; users then `pip install <app_name>` and `python -m <app_name> --install` to place the app in a directory.
- **Brython package** — `brython-cli make_package NAME` produces `NAME.brython.js`, loadable from any server with `<script src="http://anyhost/path/NAME.brython.js">`. With an `__init__.py` in the source dir, modules import as `import NAME.module`; without it, by bare name (`import module`).
- **Slimmed stdlib** — `brython-cli make_modules` then swap `<script src="brython_stdlib.js">` for `<script src="brython_modules.js">`.

## Common console symptoms (not bugs)

- **404 errors on import** — `import X` probes the stdlib, the script directory, and `Lib/site-packages` with blocking Ajax calls; 404s appear until a path matches, and an `ImportError` is raised only if all paths fail.
- **"Synchronous XMLHttpRequest on the main thread is deprecated"** — expected, caused by the blocking Ajax used for imports and `open()`.
- **Slow first import** — compiled stdlib modules are cached in IndexedDB (since 3.6.0); compilation happens on first import or when the Brython version changes, later loads are much faster.
- **Precompiling app scripts is counterproductive** — generated JS is ~10x bigger than the source; on-the-fly compilation plus the IndexedDB cache is faster than shipping precompiled code.

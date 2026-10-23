# The `www` directory of the brython repository

When working inside the [brython repo](https://github.com/brython-dev/brython) (branch `3.15`), `www/` is the site root that the dev server serves. The published site (brython.info) and the static docs (`static_doc/3.15`) are built from it.

## Layout

- `www/src/` — the compiled engine and the standard library: `brython.js` (engine), `brython.min.js`, `brython_stdlib.js` (stdlib bundle), `stdlib_paths.js` (static import mapping table), `version_info.js`, the translator (`py2js.js`, `python_parser.js`, `python_tokenizer.js`, `gen_parse.js`, `ast_to_js.js`), the runtime type modules (`py_int.js`, `py_string.js`, `py_dom.js`, ...), and `Lib/` (Python modules) plus `libs/` (JavaScript modules) of the standard distribution
- `www/doc/` — mkdocs source of the documentation: `mkdocs.yml` (in `www/`) points `docs_dir: doc`, `site_dir: html`; language subdirectories `en/`, `es/`, `fr/`, `pt-br/`; `en/` holds the English pages (`intro.md`, `install.md`, `options.md`, `syntax.md`, `events.md`, `browser.*.md`, `import.md`, `implem.md`, `faq.md`, ...), a `cookbook/` of small recipes, and `examples/local_storage/`. Built docs are what brython.info serves under `static_doc/<version>/en/...`
- `www/gallery/` — roughly 100 files of runnable example pages (plus helper scripts and assets), indexed by `gallery_en.html` (plus `es`, `fr`, `pt` indexes)
- `www/tutorial/` — the step-by-step tutorial (calculator app), language dirs `en/`, `es/`, `fr/`, `it/`, `pt-br/`, `br/`
- `www/tests/` — the official test pages (130+ files), reached from the console via the "Test pages" link
- `www/console.html` — the online Python console (namespace persists between runs; reload to reset)
- `www/demo.html` — sample page of DOM/event/Ajax usage (also installed by `brython-cli install`)
- `www/app/` — a demo `index.html` page (input + button hello example loading `/src/brython.js`)
- `www/slideshow/`, `www/benchmarks/`, `www/speed/` — presentation, benchmark, and speed-comparison pages
- `www/cgi-bin/` — small server-side handlers used by the examples (e.g. file upload targets)
- `releases/` — staging dir for the GitHub release assets: `scripts/make_release.py` generates `demo.html` from `demo.tmpl` plus the demo body of `www/demo.html`, and zips `README.txt`, `demo.html`, `index.html` with the engine files from `www/src`. `scripts/make_setup.py` builds `setup/brython/data` from those plus `www/src` — that is what `brython-cli install` copies into an app directory
- repo root: `server.py` (dev server; `python server.py [--port N] [--no-docs]`, serves `www/` on port 8000 and generates `static_doc`), `server_aiohttp.py`, `small_node_app.py`, `manage.py` (dev task runner), `scripts/` (build tools: `make_dist.py`, `make_release.py`, `make_setup.py`, `make_minified.py`, `make_doc.py`, ...), `setup/` (the `brython` CPython package that provides `brython-cli`), `npm/` (npm packaging)

## Documentation pages (www/doc/en)

Reference topics, one file each: `intro` (what/why), `install`, `options` (execution options), `syntax`, `implem` (Python→JS translation table), `modele` (compiler pipeline), `import`, `brython-packages`, `deploy`, `file_or_http` (file:// limits), `access` (element access), `attributes` (attrs/properties), `browser.html` (element classes), `browser.ajax`, `browser.aio`, `browser.timer`, `browser.worker`, `browser.websocket`, `browser.template`, `browser.svg`, `browser.webcomponent`, `browser.widgets.dialog`, `browser.widgets.menu`, `browser.local_storage`, `browser.object_storage`, `browser.markdown`, `browser` (module index), `javascript`, `jsobjects`, `events`, `mouse_events`, `keyboard_events`, `drag_events`, `focus_events`, `dom_api`, `pydom`, `query`, `create` (page authoring), `interpreter` (interactive interpreter), `faq`, `dev_env`, `test`.

## Cookbook recipes (www/doc/en/cookbook)

Small self-contained examples: `hello_world`, `basic_markup`, `content_in_div`, `get_content`, `bind_unbind`, `select_checkbox`, `table`, `drag_drop`, `read_file`, `local_storage`, `read_text_from_imagemap`, `validate_form` (with `echo.html` + `file.txt` fixtures).

## Gallery examples worth copying from (www/gallery)

- basics: `hello.html`, `sort_table.html`, `calculator.html`, `clock.html`, `markdown_exec.html` (executable markdown), `inject_scripts.html`
- async/UI: `simulate_input.html` (custom `input()` dialog), `webcomponent.html`, `indexedDB_cache.html`, `library.html` (IndexedDB basics)
- workers: `webworker_mdn.html`, `mandelbrot_webworker.html`
- graphics/SVG/canvas: `svg_pie_chart.html`, `solitaire.html`, `turtle.html`, `canvas_plot.html`, `draw.html`, `barcode.html`
- drag & drop: `europe.html`, `drop_files.html`
- web APIs: `geo.html` (geolocation), `battery.html`, `iss_position.html`, `ruskey.html`
- games: `sudoku.html`, `bricks_py.html`, `3Dwalker.html`, `taquin.html`
- JS libraries: `three.html`, `three_webgl_interactive_cubes.html`, `raphael/`, `highcharts/`, `bokeh.html`, `test_vue.html` (Vue), `phaser.html`, `babylon2_brython.html`

## Working in the repo

- Run the site locally: `python server.py` from the repo root (port 8000; `--port 8001` for another port, `--no-docs` to skip building `static_doc`), then open `http://localhost:8000/`.
- Add a demo page by creating `www/<dir>/index.html` and loading `brython.js` relative to the page.
- Docs changes go into `www/doc/<lang>/`; the built output is `static_doc`.
- The `www` content doubles as the test surface — `www/tests/` pages are the regression suite.

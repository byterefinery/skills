---
name: kaleido-1-3-0
description: >
  Kaleido (v1.3.0) — static image export library for Plotly figures. Use this skill
  whenever the user needs to render Plotly figures to static images (PNG, JPG, SVG,
  PDF, WebP, JSON) from Python, whether via the Kaleido API directly (Kaleido, calc_fig,
  write_fig, write_fig_sync, calc_fig_sync) or through plotly's pio.write_image().
  Covers async and sync rendering, layout options (scale, width, height, format),
  Chrome installation, PageGenerator customization, sync server management, and
  batch rendering with write_fig_from_object.
metadata:
  tags:
    - python
    - visualization
    - export
    - rendering
---

# kaleido 1.3.0

## Overview

Kaleido is a library for generating static images from Plotly figures. It uses a headless Chromium browser (via the Choreographer package) to render plotly.js figures into pixel-perfect static images. It is the recommended replacement for the deprecated `orca` CLI tool.

Kaleido v1.3.0 is a major rewrite over v0.x. The v1 architecture uses a real Chromium browser instead of a custom rendering engine, which means:

- **Chrome is required** — Kaleido v1+ needs Chrome installed. Use `kaleido_get_chrome` CLI or `kaleido.get_chrome_sync()` / `await kaleido.get_chrome()` to install it.
- **Async-first API** — The primary API is async (`async with Kaleido()`), with sync convenience wrappers (`calc_fig_sync`, `write_fig_sync`) that manage a global server singleton.
- **Batch rendering** — `write_fig_from_object` accepts iterables of figure dictionaries, each with its own path, opts, and topojson.
- **Parallel tabs** — The `n` parameter controls how many browser tabs (processors) are used for parallel rendering.

### Supported output formats

| Format | Extension | Notes |
|--------|-----------|-------|
| PNG | `.png` | Default format, lossless |
| JPG | `.jpg` / `.jpeg` | Lossy, smaller files |
| SVG | `.svg` | Vector, infinite scale |
| PDF | `.pdf` | Vector, document format |
| WebP | `.webp` | Modern compressed format |
| JSON | `.json` | Plotly figure JSON (not an image) |

### Key classes and functions

| Symbol | Kind | Purpose |
|--------|------|---------|
| `Kaleido` | class | Main browser-based renderer; use as async context manager |
| `PageGenerator` | class | Customize the HTML page used for rendering |
| `calc_fig()` | async function | One-shot: return image bytes |
| `write_fig()` | async function | One-shot: write image to file |
| `calc_fig_sync()` | sync function | Blocking version of `calc_fig()` |
| `write_fig_sync()` | sync function | Blocking version of `write_fig()` |
| `write_fig_from_object()` | async function | Batch rendering with per-figure config |
| `start_sync_server()` / `stop_sync_server()` | functions | Manage the global sync server singleton |
| `get_chrome()` / `get_chrome_sync()` | functions | Download and install Chrome |

### Installation

```bash
pip install kaleido                    # standalone
pip install "plotly[kaleido]"          # via plotly extra (includes kaleido>=1.3.0)
kaleido_get_chrome                    # install Chrome (required for v1+)
```

## Usage

### Quick start — sync convenience functions

The simplest path: use the sync wrappers for one-off rendering.

```python
import kaleido
import plotly.graph_objects as go

fig = go.Figure(go.Bar(x=["A", "B", "C"], y=[1, 3, 2]))

# Write to file
kaleido.write_fig_sync(fig, path="chart.png")

# Write with options
kaleido.write_fig_sync(fig, path="chart.pdf", opts={"scale": 2, "width": 800, "height": 600})

# Get bytes (no file written)
png_bytes = kaleido.calc_fig_sync(fig, opts={"format": "png", "scale": 2})
```

### Async API — full control

For batch rendering or when running inside an async context, use `Kaleido` directly.

```python
import asyncio
import kaleido

async def render():
    async with kaleido.Kaleido(n=2) as k:
        # Single figure
        await k.write_fig(fig, path="output.png", opts={"scale": 2})

        # Get bytes
        img = await k.calc_fig(fig, opts={"format": "svg"})

        # Batch with per-figure config
        fig_dicts = [
            {"fig": fig1, "path": "fig1.png", "opts": {"scale": 2}},
            {"fig": fig2, "path": "fig2.svg", "opts": {"format": "svg"}},
        ]
        await k.write_fig_from_object(fig_dicts)

asyncio.run(render())
```

### Layout options

The `opts` dictionary controls output dimensions and format:

```python
opts = {
    "format": "png",    # png, jpg, jpeg, webp, svg, pdf, json
    "scale": 2,         # multiply resolution (1 = default, 2 = 2x, 3 = 3x)
    "width": 800,       # pixel width (overrides figure layout.width)
    "height": 600,      # pixel height (overrides figure layout.height)
}
```

Defaults: `format=png`, `scale=1`, `width=700`, `height=500`. If `width`/`height` are not specified, Kaleido falls back to `fig.layout.width`/`height`, then to template values, then to the hardcoded defaults.

### Auto-generated filenames

When `path` is a directory (or omitted, defaulting to the current directory), Kaleido generates a filename from the figure title:

```python
fig = go.Figure(go.Scatter(x=[1, 2], y=[3, 4]))
fig.update_layout(title="Sales Dashboard")

# Writes: Sales_Dashboard.png (spaces/dashes become underscores)
kaleido.write_fig_sync(fig, path="./output_dir/")

# If file exists, appends a number: Sales_Dashboard-2.png
```

Special characters are stripped; the prefix is truncated to 80 characters.

### Sync server for repeated calls

For many sync calls (e.g., in a loop), start the global server once to avoid the Chrome startup cost per call:

```python
import kaleido

kaleido.start_sync_server()  # starts global Chrome browser

for i, fig in enumerate(figures):
    kaleido.write_fig_sync(fig, path=f"fig-{i}.png")

kaleido.stop_sync_server()   # shut down Chrome
```

Without `start_sync_server()`, each `write_fig_sync()` call launches and tears down Chrome (slow).

### Custom page generator

`PageGenerator` lets you customize the HTML page used for rendering — useful for custom fonts, local plotly.js, or disabling MathJax:

```python
from kaleido import PageGenerator, Kaleido

# Use a local plotly.js and disable MathJax
page = PageGenerator(
    plotly="/path/to/plotly.min.js",
    mathjax=False,
)

async with Kaleido(page_generator=page) as k:
    await k.write_fig(fig, path="output.png")
```

### GeoJSON / TopoJSON for maps

For choropleth and density maps, pass TopoJSON data:

```python
import kaleido

# Inline TopoJSON string
topojson_data = '{"type":"Topology", ...}'
kaleido.write_fig_sync(fig, path="map.png", topojson=topojson_data)
```

### Custom HTTP headers

Pass headers via the `Kaleido` constructor for requests made by the browser:

```python
async with kaleido.Kaleido(headers={"Referer": "https://example.com/"}) as k:
    await k.write_fig(fig, path="output.png")
```

### Errors

Kaleido re-exports errors from Choreographer:

- **`ChromeNotFoundError`** — Chrome is not installed. Run `kaleido_get_chrome` or `kaleido.get_chrome_sync()`.
- **`BrowserClosedError`** — Tried to render after the browser was closed.
- **`BrowserFailedError`** — Chrome crashed or failed to start.
- **`JavascriptError`** — A JavaScript error occurred during rendering (e.g., invalid figure data).
- **`KaleidoError`** — General Kaleido rendering error.

## Gotchas

- **Chrome is mandatory** — Kaleido v1+ requires Chrome. The old v0.x used a custom renderer and didn't need it. Install with `kaleido_get_chrome` CLI or `kaleido.get_chrome_sync()` from Python. The error message is explicit if Chrome is missing.
- **Sync wrappers are slow without a server** — Calling `write_fig_sync()` repeatedly without `start_sync_server()` launches and tears down Chrome each time. For batch work, always start the server first.
- **`calc_fig_sync` ignores `path`** — `calc_fig` and `calc_fig_sync` return bytes; the `path` argument is deprecated and ignored. Use `write_fig_sync` to write files.
- **`n` is capped to 1 in convenience functions** — `calc_fig()` and `write_fig()` top-level functions force `n=1`. To use parallel rendering, instantiate `Kaleido(n=N)` directly.
- **`page_generator` is mutually exclusive with `plotlyjs`/`mathjax`** — You cannot set both `page_generator` and `plotlyjs` or `mathjax` on the same `Kaleido` instance. Use `PageGenerator` to customize those.
- **`write_fig_from_object` requires a dict with `fig` key** — Each item in the iterable must be a dict with at minimum `{"fig": figure}`. Optional keys: `path`, `opts`, `topojson`.
- **`cancel_on_error` behavior** — When `cancel_on_error=False` (default), all figures are attempted and errors are collected into a returned tuple. When `True`, the first error cancels remaining renders and raises immediately.
- **`fig` can be a dict or Figure object** — Kaleido accepts plotly `go.Figure` objects (has `to_dict()`) or raw dicts with a `"data"` key. It auto-coerces via `to_dict()`.
- **`jpg` maps to `jpeg` internally** — Pass `format="jpg"` or `format="jpeg"` — both work. The path extension `.jpg` is also recognized.
- **Timeout defaults to 90 seconds** — Per-figure timeout. Pass `timeout=None` to `Kaleido()` for no limit, useful for very large or complex figures.
- **`write_fig` path auto-generates names** — When path is a directory, the filename is derived from the figure title. Spaces and dashes become underscores; special characters are stripped. No title falls back to `"fig"`.
- **`plotly[kaleido]` installs kaleido>=1.3.0** — The plotly extra now requires Kaleido v1+. The old v0.x is incompatible with plotly v6+.
- **`orjson` is a dependency** — Kaleido uses `orjson` for JSON serialization. It handles `pandas.NA` and other non-standard types correctly.
- **`headless`, `enable_sandbox`, `enable_gpu`** — These are passed through to Choreographer's browser. Defaults: `headless=True`, `enable_sandbox=False`, `enable_gpu=False`. Use `headless=False` to visually debug rendering issues.

## References

Detailed topic guides loaded on demand:

- [01-api-reference](references/01-api-reference.md) — Full API reference: Kaleido class, PageGenerator, all module-level functions with signatures and parameters
- [02-layout-options](references/02-layout-options.md) — LayoutOpts (scale, width, height, format), default resolution, resolution math, format-specific behavior
- [03-sync-server](references/03-sync-server.md) — GlobalKaleidoServer lifecycle, start/stop, one-shot async run, performance patterns
- [04-page-generator](references/04-page-generator.md) — PageGenerator customization, custom plotly.js, MathJax, additional scripts, force_cdn
- [05-batch-rendering](references/05-batch-rendering.md) — write_fig_from_object, FigureDict, cancel_on_error, parallel tabs, profiling
- [06-path-tools](references/06-path-tools.md) — Auto-generated filenames, path resolution, directory mode, file naming algorithm
- [07-errors](references/07-errors.md) — ChromeNotFoundError, BrowserClosedError, BrowserFailedError, JavascriptError, KaleidoError, diagnostics
- [08-migration-v0-to-v1](references/08-migration-v0-to-v1.md) — Breaking changes from Kaleido v0.x to v1.x, Chrome requirement, API changes, plotly integration

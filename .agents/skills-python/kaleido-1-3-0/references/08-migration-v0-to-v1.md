# Migration: Kaleido v0.x → v1.3.0

## Summary of changes

Kaleido v1 is a complete rewrite. The v0.x used a custom rendering engine (Electron-based). v1 uses a real Chromium browser via the Choreographer package.

| Aspect | v0.x | v1.3.0 |
|--------|------|--------|
| Rendering engine | Custom (Electron) | Chromium browser |
| Chrome required | No | Yes |
| API style | Sync-only | Async-first, sync wrappers |
| Package name | `kaleido` | `kaleido` |
| plotly integration | `plotly[kaleido]` → kaleido>=0.1 | `plotly[kaleido]` → kaleido>=1.3.0 |
| Installation | `pip install kaleido` (binary wheels) | `pip install kaleido` + `kaleido_get_chrome` |
| Max resolution | Limited | Limited by Chrome canvas |

## Breaking changes

### Chrome is required

v0.x bundled its own renderer. v1 needs Chrome:

```python
# v0.x — no setup needed
import kaleido

# v1 — install Chrome first
import kaleido
kaleido.get_chrome_sync()  # or: kaleido_get_chrome (CLI)
```

### Async-first API

v0.x was purely synchronous. v1 is async-first with sync convenience wrappers:

```python
# v0.x
fig.write_image("chart.png", scale=2)

# v1 — still works via pio integration!
fig.write_image("chart.png", scale=2)

# v1 — direct Kaleido API (async)
async with kaleido.Kaleido() as k:
    await k.write_fig(fig, path="chart.png", opts={"scale": 2})

# v1 — sync convenience
kaleido.write_fig_sync(fig, path="chart.png", opts={"scale": 2})
```

### opts dictionary instead of keyword arguments

v0.x used keyword arguments on `write_image()`. v1 uses an `opts` dict:

```python
# v0.x (via plotly)
fig.write_image("chart.png", width=800, height=600, scale=2)

# v1 (via kaleido directly)
kaleido.write_fig_sync(fig, path="chart.png", opts={"width": 800, "height": 600, "scale": 2})

# v1 (via plotly — still works the same)
fig.write_image("chart.png", width=800, height=600, scale=2)
```

### No binary wheels

v0.x shipped pre-compiled binary wheels. v1 is pure Python with Chrome as a runtime dependency:

```bash
# v0.x
pip install kaleido  # downloads binary wheel with embedded renderer

# v1
pip install kaleido        # pure Python
kaleido_get_chrome         # downloads Chrome separately
```

### WebP support added

v1 adds WebP as a supported output format alongside PNG, JPG, SVG, PDF, and JSON.

## What stays the same

- **`fig.write_image()`** — the plotly API is unchanged. It delegates to Kaleido internally.
- **Output formats** — PNG, JPG, SVG, PDF all work the same way
- **Layout options** — `scale`, `width`, `height`, `format` have the same meaning
- **TopoJSON** — still supported for map figures

## Migration checklist

1. **Install Chrome:** `kaleido_get_chrome` or `kaleido.get_chrome_sync()`
2. **Update imports** if using Kaleido directly (module layout changed)
3. **Convert sync code** to use `write_fig_sync()` / `calc_fig_sync()` or async `Kaleido()`
4. **Use `opts` dict** for layout options when calling Kaleido directly
5. **Check timeouts** — default is 90s (v0.x had different behavior)
6. **Test rendering** — Chrome may render slightly differently than the old engine

## plotly.py integration

When using `fig.write_image()`, the API is unchanged:

```python
import plotly.graph_objects as go

fig = go.Figure(go.Bar(x=[1, 2, 3], y=[4, 3, 2]))
fig.write_image("chart.png", scale=2)       # works the same
fig.write_image("chart.svg", width=800)     # works the same
fig.write_image("chart.pdf", height=600)    # works the same
```

Plotly's `pio` module handles the Kaleido integration transparently. The `opts` dict is only needed when using Kaleido's API directly.

# I/O and Export

## HTML export

```python
fig.to_html(full_html=True, include_plotlyjs="cdn", auto_open=False)
fig.write_html("chart.html", full_html=True, include_plotlyjs="cdn")
fig.write_html("chart.html", include_plotlyjs=False)   # rely on a page-level plotly.js
```

- `include_plotlyjs`: `"cdn"` (script tag), `True` (inline, ~3MB), `"relative-url"`, `False`.
- Since v7.0.0 the generated document includes `<!doctype html>` — don't paste the full document string inside another HTML body.
- `fig.show()` in a notebook renders inline; in a script it opens a browser via the renderers framework.

## Static image export (Kaleido only in v7)

```python
fig.write_image("chart.png", scale=2)          # PNG (default)
fig.write_image("chart.svg")                   # vector
fig.write_image("chart.pdf")
fig.write_image("chart.jpeg", width=1200, height=800)
png_bytes = fig.to_image(format="png")
```

- Requires `pip install "plotly[kaleido]"` (kaleido>=1.0 supported; install >=1.3).
- The `engine` argument was **removed** from `write_image`, `to_image`, `write_images`, `full_figure_for_development`, and renderer constructors. Orca support is gone.
- Width/height: `fig.write_image(..., width=..., height=...)`; without them, `layout.width`/`layout.height` (and the template's) are used — `write_images` now honors these too (fixed 7.2.0).
- If Kaleido can't find Chrome/Chromium, run `plotly_get_chrome` (console entry point) to install one.
- `pio.kaleido_available()` checks availability.

## JSON

```python
s = fig.to_json()
fig.write_json("chart.json")
fig2 = plotly.io.from_json(s)          # output_type="Figure" (or "Layout"/"Trace")
fig3 = plotly.io.read_json("chart.json")
```

- `to_json`/`from_json` accept an `engine` argument (`"json"` or `"orjson"`); orjson is used automatically when installed.
- `to_plotly_json()` returns the figure as a plain dict.

## Renderers (`plotly.io.renderers`)

The renderers framework decides how `fig.show()` displays figures. Built-in renderers include `notebook` (Jupyter), `iframe`, `browser`, `png`/`jpeg`/`svg` (terminal image renderers, e.g., `svg`), and `sphinx_gallery_png` (for sphinx-gallery docs).

```python
import plotly.io as pio

pio.renderers.default = "browser"              # explicit default
pio.renderers["my-iframe"] = pio.renderers.iframe   # register a custom one
fig.show(renderer="iframe")                    # per-call override
```

In most notebook contexts (Jupyter, JupyterLab, VS Code, Colab, Kaggle) an appropriate renderer is chosen automatically; in headless scripts, set a renderer or use `write_html`/`write_image` for deterministic output.

## Defaults (`pio.defaults`)

`pio.defaults.height` / `pio.defaults.width` set the default figure size (used by px and as the fallback for HTML wrapper sizing).

## Matplotlib / Dash conversion

- `plotly.tools.mpl_to_plotly(fig, resize=False, strip_style=False, verbose=False)` — convert a matplotlib `Figure` to a `go.Figure`. Heavily improved in v7.x: twinned/overlaid subplots (`twinx`/`twiny`), step plots, stairs, path collections (violin, pcolor, fill_between, stem), reference lines (`axhline`/`axvline`), date axes, custom tick values, spine/tick colors, background colors, contour lines and line collections.
- `plotly.tools.convert_dash` — convert Dash chart specs (fixes dotted-line mapping in 7.2.0).

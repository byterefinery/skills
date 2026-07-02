# I/O and Export

## Rendering

```python
import plotly.io as pio

# Available renderers
print(pio.renderers)
# browser, jupyter, jupyterlab, notebook, vs Code, colab, iframe, iframe_connected,
# svg, mpld3, notebook_connected, d3, d3_connected

# Set default
pio.renderers.default = "browser"    # opens in browser
pio.renderers.default = "iframe"     # inline iframe
pio.renderers.default = "svg"        # terminal SVG (headless)

# Per-figure
fig.show(renderer="browser")
fig.show(renderer="iframe")

# Jupyter: inline by default; no renderer needed
```

## HTML export

```python
# Full standalone HTML
fig.write_html("chart.html")

# With full config and plotly.js embedded
fig.write_html("chart.html", full_html=True, include_plotlyjs=True)

# To string
html = fig.to_html()

# Responsive dimensions
pio.defaults.default_width = "100%"
pio.defaults.default_height = "500px"
fig.write_html("chart.html")
```

## Image export (Kaleido)

```bash
pip install "plotly[kaleido]"  # kaleido>=1.3.0
```

```python
# PNG
fig.write_image("chart.png", scale=2, width=800, height=600)

# SVG
fig.write_image("chart.svg")

# PDF
fig.write_image("chart.pdf")

# Multiple images
pio.write_images(fig, "output.{png,svg,pdf}")

# To bytes
img_bytes = pio.to_image(fig, format="png", scale=2)
```

Kaleido v1 uses a bundled Chromium. Default headers are set to avoid blocked Open Street Map tiles.

## JSON

```python
# Serialize
json_str = fig.to_json()
pio.write_json(fig, "figure.json")

# Deserialize
fig = pio.from_json(json_str)
fig = pio.read_json("figure.json")
```

## Defaults

```python
import plotly.io as pio

# Global defaults (persist across figures)
pio.defaults.default_width = 800
pio.defaults.default_height = 500
pio.defaults.template = "plotly_white"
pio.defaults.render_mode = "svg"       # or "auto"
pio.defaults.respect_defaults = False   # True = don't override per-figure settings

# Reset to factory defaults
pio.reset_defaults()
```

## Orca (legacy)

The `orca` CLI tool is deprecated. Use Kaleido for image export. `pio.orca` module is retained for backward compatibility only.

## MIME types for notebooks

Plotly registers MIME renderers for Jupyter. In v6, the JupyterLab extension supports JupyterLab 4 and reduces file sizes for offline notebooks.

```python
# Disable auto-display in notebooks
fig.show(renderer=None)

# Force display
from IPython.display import display
display(fig)
```

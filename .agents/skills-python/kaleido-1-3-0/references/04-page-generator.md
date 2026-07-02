# Page Generator — Kaleido 1.3.0

## Overview

`PageGenerator` produces the HTML page that Chrome loads to render Plotly figures. The page includes script tags for MathJax, plotly.js, and Kaleido's own rendering JavaScript. Customizing it allows control over library versions, custom fonts, and additional JavaScript.

## Default page structure

```html
<!DOCTYPE html>
<html>
    <head>
        <style id="head-style"></style>
        <title>Kaleido-fier</title>
        <script>
          window.PlotlyConfig = {MathJaxConfig: 'local'}
        </script>
        <script type="text/x-mathjax-config">
          MathJax.Hub.Config({ "SVG": { blacker: 0 }})
        </script>
        <!-- MathJax script (CDN by default) -->
        <!-- plotly.js script (bundled or CDN) -->
        <!-- kaleido_scopes.js (bundled) -->
    </head>
    <body style="{margin: 0; padding: 0;}"><img id="kaleido-image" /></body>
</html>
```

## Basic usage

```python
from kaleido import PageGenerator, Kaleido

# Default: uses plotly.py's bundled plotly.js + CDN MathJax
page = PageGenerator()

# Use with Kaleido
async with Kaleido(page_generator=page) as k:
    await k.write_fig(fig, path="output.png")
```

## Custom plotly.js

```python
# Local file
page = PageGenerator(plotly="/path/to/plotly.min.js")

# Remote URL
page = PageGenerator(plotly="https://cdn.example.com/plotly-3.0.0.js")

# With explicit charset
page = PageGenerator(plotly=("https://cdn.example.com/plotly.js", "utf-8"))

# Force CDN even if plotly.py is installed
page = PageGenerator(force_cdn=True)
```

## MathJax control

```python
# Default (CDN v2.7.5)
page = PageGenerator()

# Disable MathJax (faster rendering, no LaTeX support)
page = PageGenerator(mathjax=False)

# Local MathJax
page = PageGenerator(mathjax="/path/to/MathJax.js")

# Custom URL
page = PageGenerator(mathjax="https://cdn.example.com/mathjax/MathJax.js")
```

## Additional scripts

```python
# Add custom JavaScript
page = PageGenerator(
    others=[
        "https://cdn.example.com/custom-lib.js",
        ("/path/to/local.js", "utf-8"),
    ]
)
```

## Resolution defaults

| Setting | Value | Source |
|---------|-------|--------|
| Default plotly.js | plotly.py's `plotly.min.js` if installed | Local file |
| Fallback plotly.js | `https://cdn.plot.ly/plotly-2.35.2.js` | CDN |
| Default MathJax | `https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS-MML_SVG` | CDN |

## Mutual exclusivity

`page_generator` cannot be combined with `plotlyjs` or `mathjax` on the `Kaleido` constructor:

```python
# ERROR — cannot mix page_generator with plotlyjs/mathjax
async with Kaleido(
    page_generator=PageGenerator(plotly="..."),
    plotlyjs="/other/plotly.js",  # ValueError!
) as k:
    ...

# CORRECT — use PageGenerator for all customization
page = PageGenerator(plotly="/path/to/plotly.js", mathjax=False)
async with Kaleido(page_generator=page) as k:
    ...
```

## Custom index.html

Instead of `PageGenerator`, pass a path directly:

```python
async with Kaleido(page_generator="/path/to/custom/index.html") as k:
    await k.write_fig(fig, path="output.png")
```

The file must be a valid HTML file. Kaleido validates that the path exists.

## When to customize

- **Disable MathJax** — if your figures don't use LaTeX, disabling MathJax speeds up rendering
- **Custom plotly.js** — test with newer plotly.js versions or use a specific version
- **Custom fonts** — inject CSS via the page to load custom fonts for rendering
- **Additional libraries** — include D3, custom JS, or other dependencies needed by your figures
- **Debugging** — inspect the generated HTML with `page.generate_index()` to understand what Chrome loads

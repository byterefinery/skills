# API Reference — Kaleido 1.3.0

## Kaleido Class

```python
class Kaleido(choreo.Browser):
    def __init__(
        self,
        n: int = 1,
        timeout: float | None = 90,
        page_generator: None | PageGenerator | str | Path = None,
        plotlyjs: str | Path | None = None,
        mathjax: str | Path | Literal[False] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs,
    )
```

### Constructor parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `n` | int | 1 | Number of browser tabs (parallel processors) |
| `timeout` | float \| None | 90 | Seconds to wait per figure render. `None` = no limit |
| `page_generator` | PageGenerator \| str \| Path \| None | None | Custom page generator or path to index.html |
| `plotlyjs` | str \| Path \| None | None | Path or URL to plotly.js. None = use plotly.py's bundled or CDN |
| `mathjax` | str \| Path \| Literal[False] \| None | None | Path/URL to MathJax. `False` = disable. None = use CDN v2.7.5 |
| `headers` | dict[str, str] \| None | None | Extra HTTP headers (CDP Network.setExtraHTTPHeaders) |
| `**kwargs` | Any | — | Passed to Choreographer.Browser: `headless`, `enable_sandbox`, `enable_gpu` |

### Methods

#### `async open()`

Build the HTML page (if needed) and open the Chromium browser. Creates a temporary directory for the index.html unless a file path was provided.

#### `async close()`

Close the browser and clean up temporary files. Cancels any pending render tasks.

#### `async populate_targets()`

Override of Browser.populate_targets(). Creates `n` tabs, navigates each to the Kaleido index page, and puts them into the ready queue. Called automatically during `open()`.

#### `async write_fig(fig, path, opts, *, topojson, cancel_on_error, stepper)`

Render one or more figures and write to file(s).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `fig` | Figurish \| Iterable[Figurish] | — | Single figure or iterable of figures |
| `path` | str \| Path \| None | None | Output path or directory. None = current directory |
| `opts` | LayoutOpts \| None | None | Layout options dict |
| `topojson` | str \| None | None | TopoJSON string for map figures |
| `cancel_on_error` | bool | False | If True, raise on first error. If False, collect errors |
| `stepper` | bool | False | Debug: wait for keypress before each render |

**Returns:** `None` on success (when `cancel_on_error=True`), or `tuple[Exception]` with collected errors (when `cancel_on_error=False`).

#### `async write_fig_from_object(fig_dicts, *, cancel_on_error, stepper)`

Render figures from specification dictionaries. Each dict must have a `"fig"` key and may have `"path"`, `"opts"`, `"topojson"`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `fig_dicts` | FigureDict \| Iterable[FigureDict] | — | Single dict or iterable of dicts |
| `cancel_on_error` | bool | False | Error handling mode |
| `stepper` | bool | False | Debug mode |

**Returns:** Same as `write_fig`.

#### `async calc_fig(fig, opts, *, path, topojson, stepper)`

Render a single figure and return raw image bytes. The `path` argument is deprecated and ignored.

**Returns:** `bytes` — the rendered image data.

### Context manager

```python
async with Kaleido(n=2, timeout=60) as k:
    await k.write_fig(fig, path="output.png")
# Browser auto-closes on exit
```

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `tabs_ready` | `asyncio.Queue[_KaleidoTab]` | Queue of tabs ready to process figures |
| `profiler` | `deque[WriteCall]` | Last 5 render call profiles (for debugging) |

---

## PageGenerator Class

```python
class PageGenerator:
    def __init__(
        self,
        *,
        plotly: None | Path | str | UrlAndCharset = None,
        mathjax: None | Path | str | bool | UrlAndCharset = None,
        others: None | list[Path | str | UrlAndCharset] = None,
        force_cdn: bool = False,
    )

    def generate_index(self) -> str:
        ...
```

### Constructor parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `plotly` | str \| Path \| tuple \| None | None | plotly.js source. None = use plotly.py's bundled, fallback to CDN |
| `mathjax` | str \| Path \| bool \| tuple \| None | None | MathJax source. `False` = disable. None = CDN v2.7.5 |
| `others` | list \| None | None | Additional script URLs to include |
| `force_cdn` | bool | False | Force CDN even if plotly.py is installed |

### Defaults

- **plotly.js**: If plotly.py is installed, uses its bundled `plotly.min.js`. Otherwise falls back to CDN `https://cdn.plot.ly/plotly-2.35.2.js`.
- **MathJax**: CDN `https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS-MML_SVG`.

### `UrlAndCharset`

A tuple `(url: str | Path, charset: str)` to explicitly set the `charset` attribute on the `<script>` tag. Example: `("https://cdn.example.com/lib.js", "utf-8")`.

---

## Module-level functions

### `async calc_fig(fig, opts, *, topojson, kopts)`

One-shot async: create a Kaleido instance (n=1), render, close. Returns `bytes`.

### `async write_fig(fig, path, opts, *, topojson, kopts, **kwargs)`

One-shot async: create a Kaleido instance, write file, close.

### `async write_fig_from_object(fig_dicts, *, kopts, **kwargs)`

One-shot async: create a Kaleido instance, batch render, close.

### `calc_fig_sync(*args, **kwargs)`

Blocking wrapper. If the global sync server is running, delegates to it. Otherwise does a one-shot `asyncio.run()`.

### `write_fig_sync(*args, **kwargs)`

Blocking wrapper. Same server-aware behavior as `calc_fig_sync`.

### `write_fig_from_object_sync(*args, **kwargs)`

Blocking wrapper for batch rendering.

### `start_sync_server(*args, silence_warnings=False, **kwargs)`

Start the global Kaleido server (singleton). Takes same arguments as `Kaleido()`. Warns if already running (suppress with `silence_warnings=True`).

### `stop_sync_server(*, silence_warnings=False)`

Stop the global server. Can be restarted. Warns if already stopped.

### `async get_chrome()` / `get_chrome_sync()`

Download and install Chrome. Re-exported from `choreographer.cli`. Also available as CLI command `kaleido_get_chrome`.

---

## Type definitions

### `LayoutOpts` (TypedDict, total=False)

```python
class LayoutOpts(TypedDict, total=False):
    format: Literal["png", "jpg", "jpeg", "webp", "svg", "json", "pdf"] | None
    scale: int | float
    height: int | float
    width: int | float
```

### `FigureDict` (TypedDict)

```python
class FigureDict(TypedDict):
    fig: Required[Figurish]
    path: NotRequired[None | str | Path]
    opts: NotRequired[LayoutOpts | None]
    topojson: NotRequired[None | str]
```

### `Figurish`

Any object that is a valid Plotly figure: a `go.Figure` instance (has `to_dict()`) or a dict with a `"data"` key.

---

## Errors

| Error | Source | When |
|-------|--------|------|
| `ChromeNotFoundError` | choreographer | Chrome not installed |
| `BrowserClosedError` | choreographer | Render attempted after close |
| `BrowserFailedError` | choreographer | Chrome crashed or failed to start |
| `JavascriptError` | kaleido | JS error during rendering |
| `KaleidoError` | kaleido | General rendering error |

---

## Constants

| Constant | Value | Source |
|----------|-------|--------|
| `DEFAULT_EXT` | `"png"` | fig_tools |
| `DEFAULT_SCALE` | `1` | fig_tools |
| `DEFAULT_WIDTH` | `700` | fig_tools |
| `DEFAULT_HEIGHT` | `500` | fig_tools |
| `SUPPORTED_FORMATS` | `("png", "jpg", "jpeg", "webp", "svg", "json", "pdf")` | fig_tools |
| `DEFAULT_PLOTLY` | `"https://cdn.plot.ly/plotly-2.35.2.js"` | page_generator |
| `DEFAULT_MATHJAX` | `"https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS-MML_SVG"` | page_generator |

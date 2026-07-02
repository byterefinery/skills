# Errors — Kaleido 1.3.0

## Error hierarchy

Kaleido re-exports errors from Choreographer and defines its own:

```python
from kaleido.errors import (
    BrowserClosedError,      # from choreographer
    BrowserFailedError,      # from choreographer
    ChromeNotFoundError,     # from choreographer
    JavascriptError,         # from kaleido
    KaleidoError,            # from kaleido
)
```

## ChromeNotFoundError

**When:** Chrome is not installed or not found on the system.

**Cause:** Kaleido v1+ requires Chrome. The v0.x renderer is gone.

**Fix:**
```bash
kaleido_get_chrome          # CLI
```
```python
import kaleido
kaleido.get_chrome_sync()   # Python sync
await kaleido.get_chrome()  # Python async
```

**Message:** `"Kaleido v1 and later requires Chrome to be installed. To install Chrome, use the CLI command kaleido_get_chrome, or from Python, use either await kaleido.get_chrome() or kaleido.get_chrome_sync()."`.

## BrowserClosedError

**When:** A render is attempted after the browser was closed.

**Cause:** Using a `Kaleido` instance after `await k.close()` or after exiting the async context manager.

**Fix:** Ensure all renders happen within the `async with Kaleido()` block.

```python
# WRONG
k = await kaleido.Kaleido()
await k.close()
await k.write_fig(fig, path="x.png")  # BrowserClosedError!

# CORRECT
async with kaleido.Kaleido() as k:
    await k.write_fig(fig, path="x.png")
```

## BrowserFailedError

**When:** Chrome crashes, fails to start, or becomes unresponsive.

**Common causes:**
- Chrome sandbox issues (try `enable_sandbox=True`)
- Insufficient system resources
- GPU issues (try `enable_gpu=False`, which is the default)
- Incompatible Chrome version

**Fix:**
```python
async with kaleido.Kaleido(enable_sandbox=True, enable_gpu=False) as k:
    await k.write_fig(fig, path="x.png")
```

## JavascriptError

**When:** A JavaScript error occurs during rendering inside the browser tab.

**Common causes:**
- Invalid figure data (e.g., NaN values in unexpected places)
- Incompatible plotly.js version
- Missing or broken JavaScript dependencies
- Memory limits in the browser tab

**Diagnostics:** Check the Kaleido log output (set `logistro` level to DEBUG). The error message typically includes the JavaScript error text.

## KaleidoError

**When:** General rendering errors not covered by other types.

**Common causes:**
- Tab acquisition timeout
- Internal state corruption
- Unexpected Chrome behavior

## Validation errors (before rendering)

These are standard Python exceptions raised during input validation:

| Exception | When |
|-----------|------|
| `TypeError` | Figure is not valid (no `to_dict()` and no `"data"` key) |
| `ValueError` | Invalid format string |
| `AttributeError` | Unknown key in `opts` dict |
| `FileNotFoundError` | `page_generator` path doesn't exist |
| `RuntimeError` | `k.open()` wasn't called before rendering |
| `ValueError` | `page_generator` set with `plotlyjs` or `mathjax` |

## Timeout errors

When `timeout` is exceeded (default 90s), `asyncio.TimeoutError` is raised:

```python
async with kaleido.Kaleido(timeout=30) as k:
    await k.calc_fig(huge_fig)  # asyncio.TimeoutError if > 30s
```

Set `timeout=None` for no limit.

## Error collection in batch mode

With `cancel_on_error=False` (default), errors are collected:

```python
errors = await k.write_fig_from_object(fig_dicts, cancel_on_error=False)
if errors:
    for i, err in enumerate(errors):
        print(f"Figure {i}: {type(err).__name__}: {err}")
```

The returned tuple contains exceptions in the order of the input figures.

## Debugging tips

1. **Enable debug logging:**
   ```python
   import logistro
   logistro.setLogLevel("DEBUG")
   ```

2. **Use stepper mode** to inspect the browser during rendering:
   ```python
   await k.write_fig(fig, path="x.png", stepper=True)
   # Waits for keypress before rendering — inspect the Chrome window
   ```

3. **Use headless=False** to see the Chrome window:
   ```python
   async with kaleido.Kaleido(headless=False) as k:
       await k.write_fig(fig, path="x.png")
   ```

4. **Check profiler** for timing info:
   ```python
   for call in k.profiler:
       print(call.name, call.renders)
   ```

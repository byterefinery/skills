# Batch Rendering — Kaleido 1.3.0

## write_fig_from_object

The primary batch rendering method. Accepts a single `FigureDict` or an iterable of them:

```python
async with kaleido.Kaleido(n=2) as k:
    fig_dicts = [
        {"fig": fig1, "path": "fig1.png", "opts": {"scale": 2}},
        {"fig": fig2, "path": "fig2.svg", "opts": {"format": "svg"}},
        {"fig": fig3, "path": "output_dir/"},  # auto-generated name
    ]
    await k.write_fig_from_object(fig_dicts)
```

## FigureDict structure

```python
class FigureDict(TypedDict):
    fig: Required[Figurish]        # plotly figure or dict with "data" key
    path: NotRequired[str | Path]  # output path or directory
    opts: NotRequired[LayoutOpts]  # layout options
    topojson: NotRequired[str]     # TopoJSON for maps
```

## cancel_on_error behavior

### Default (False) — collect errors

All figures are attempted. Errors are collected and returned:

```python
errors = await k.write_fig_from_object(fig_dicts, cancel_on_error=False)
if errors:
    for err in errors:
        print(f"Render failed: {err}")
```

### True — fail fast

First error cancels remaining renders:

```python
await k.write_fig_from_object(fig_dicts, cancel_on_error=True)
# Raises on first error, remaining figures are cancelled
```

## Parallel rendering with n

The `n` parameter controls how many browser tabs (processors) are used:

```python
# 4 parallel tabs — processes up to 4 figures simultaneously
async with kaleido.Kaleido(n=4) as k:
    await k.write_fig_from_object(large_list_of_figures)
```

### How parallelism works

1. Kaleido creates `n` tabs, each loaded with the Kaleido index page
2. Tabs are queued in `tabs_ready` (asyncio.Queue)
3. For each figure, a tab is acquired from the queue
4. After rendering, the tab is reloaded (cleared) and returned to the queue
5. Next figure grabs the next available tab

### Choosing n

- **n=1** — sequential, lowest memory, most predictable
- **n=2-4** — good balance for most workloads
- **n > 4** — diminishing returns; Chrome tab overhead increases
- Memory usage scales with `n` since each tab holds plotly.js in memory

## Async iterable support

`write_fig_from_object` accepts any iterable, including async generators:

```python
async def figure_generator():
    for i in range(1000):
        yield {
            "fig": create_figure(i),
            "path": f"fig-{i}.png",
        }

async with kaleido.Kaleido(n=4) as k:
    await k.write_fig_from_object(figure_generator())
```

This enables streaming — figures are rendered as they're produced, not all at once.

## Profiling

Kaleido tracks the last 5 render calls:

```python
async with kaleido.Kaleido(n=2) as k:
    await k.write_fig(fig, path="output.png")

    # Inspect profiling data
    for call in k.profiler:
        print(call.name)
        for render in call.renders:
            print(render.profile_log)
```

Each `WriteCall` in the profiler contains:
- `name` — the asyncio task name
- `renders` — list of `RenderTaskProfile` objects with timing checkpoints

## Performance tips

- **Batch with n > 1** for 2x-4x speedup on I/O-bound rendering
- **Use the sync server** for sync callers doing many renders
- **Pre-generate paths** — auto-naming has overhead; explicit paths are faster
- **Reuse Kaleido** — creating/destroying the browser is expensive; keep it open
- **Match n to CPU cores** — too many tabs can thrash CPU and memory

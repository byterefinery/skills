# Sync Server — Kaleido 1.3.0

## Overview

Kaleido provides a global sync server (`GlobalKaleidoServer`) that keeps a Chromium browser open across multiple sync calls. This avoids the overhead of launching Chrome for each individual `write_fig_sync()` call.

## Without server (slow for batches)

Each call launches Chrome, renders, and tears down:

```python
import kaleido

for i in range(100):
    fig = create_figure(i)
    kaleido.write_fig_sync(fig, path=f"fig-{i}.png")
# ~100 Chrome launches — very slow
```

## With server (fast for batches)

Start once, render many, stop:

```python
import kaleido

kaleido.start_sync_server(n=4)

for i in range(100):
    fig = create_figure(i)
    kaleido.write_fig_sync(fig, path=f"fig-{i}.png")

kaleido.stop_sync_server()
# ~1 Chrome launch — much faster
```

## Server lifecycle

```python
# Start (singleton — can only run once)
kaleido.start_sync_server(n=2, timeout=60)

# Check if running
server.is_running()  # True

# Calls delegate to the server
kaleido.write_fig_sync(fig, path="a.png")
kaleido.calc_fig_sync(fig, opts={"format": "svg"})

# Stop
kaleido.stop_sync_server()

# After stop, calls fall back to one-shot mode
kaleido.write_fig_sync(fig, path="b.png")  # launches Chrome temporarily
```

## start_sync_server parameters

Takes the same arguments as `Kaleido()`:

```python
kaleido.start_sync_server(
    n=4,                              # parallel tabs
    timeout=120,                      # per-figure timeout
    page_generator=custom_page,       # custom page
    headless=True,                    # pass-through to Choreographer
    enable_sandbox=False,             # pass-through
    silence_warnings=False,           # suppress "already running" warning
)
```

### `silence_warnings`

By default, calling `start_sync_server()` when the server is already running emits a warning. Set `silence_warnings=True` to suppress it — useful in library code where the caller may have already started the server.

## One-shot fallback

When the sync server is not running, `write_fig_sync()` and `calc_fig_sync()` fall back to `oneshot_async_run()`, which:

1. Creates a temporary event loop
2. Creates a `Kaleido` instance
3. Performs the render
4. Closes the browser

This is convenient for single calls but has high per-call overhead.

## Performance comparison

| Scenario | Without server | With server |
|----------|---------------|-------------|
| 1 figure | ~3-5s (Chrome startup) | ~3-5s (same startup) |
| 10 figures | ~30-50s | ~5-10s |
| 100 figures | ~300-500s | ~15-30s |

Times vary by system and figure complexity.

## Error handling

- If the server crashes, subsequent sync calls fall back to one-shot mode
- `stop_sync_server()` on an already-stopped server emits a warning (suppress with `silence_warnings=True`)
- The server is a true singleton — `start_sync_server()` will not create a second instance

## Thread safety

The sync server runs on a single asyncio event loop. Concurrent calls from multiple threads are serialized through the server's internal queue. For parallel rendering, use `n > 1` to increase the number of browser tabs.

## When to use

- **Use the server** when rendering 5+ figures in a loop or script
- **Skip the server** for one-off rendering or when running inside an async context (use `Kaleido()` directly)
- **Use async directly** when you're already in an async context — the server is only useful for sync callers

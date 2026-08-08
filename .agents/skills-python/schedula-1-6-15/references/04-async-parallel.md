# Async and Parallel Execution

## Built-in Executors

| Executor | Type | Scope | SubDispatch |
|---|---|---|---|
| `async` | Threads | Same process | Included |
| `parallel` | Processes | Separate processes | Excluded |
| `parallel-pool` | Process pool | Pooled processes | Excluded |
| `parallel-dispatch` | Processes | Separate processes | Included |

### Setting Executor

```python
# Per-dispatch
sol = dsp(inputs={'a': 1}, executor='async')

# Default for dispatcher
dsp = sh.Dispatcher(executor='async')
sol = dsp(inputs={'a': 1})  # Uses default executor
```

### Resolving Results

For async/parallel execution, functions return `Future` objects. Call `.result()` to resolve:

```python
sol = dsp(inputs={'a': 1}, executor='async')
sol = sol.result()           # Wait indefinitely
sol = sol.result(timeout=5)  # Wait up to 5 seconds
```

### Cleanup

```python
# Shutdown specific executor
sh.shutdown_executor('async')

# Shutdown all active executors
executors = sh.shutdown_executors()  # Returns list of shutdown executor names
```

## Custom Executors

Register custom executors with `register_executor`:

```python
from schedula import register_executor, ThreadExecutor

# Register a named executor
register_executor('my-threads', ThreadExecutor(max_workers=8))

# Use it
sol = dsp(inputs={'a': 1}, executor='my-threads').result()
```

## Executor Classes

### `ThreadExecutor`

```python
from schedula import ThreadExecutor

executor = ThreadExecutor(max_workers=4)
register_executor('threads', executor)
```

Runs functions in threads within the same process. Suitable for I/O-bound tasks.

### `ProcessExecutor`

```python
from schedula import ProcessExecutor

executor = ProcessExecutor()
register_executor('processes', executor)
```

Runs each function in a separate process. Bypasses GIL for CPU-bound tasks. Higher overhead.

### `ProcessPoolExecutor`

```python
from schedula import ProcessPoolExecutor

executor = ProcessPoolExecutor(max_workers=4)
register_executor('pool', executor)
```

Uses a fixed pool of worker processes. Lower overhead than `ProcessExecutor` for many small tasks.

### `PoolExecutor`

Base class for pool-based executors.

## Await Controls

### `await_domain`

Controls whether domain checks wait for all async inputs:

```python
dsp.add_function('f', func, inputs=['a', 'b'], outputs=['c'],
                 await_domain=True)     # Wait for all inputs (default)
dsp.add_function('f', func, inputs=['a', 'b'], outputs=['c'],
                 await_domain=False)    # Check domain as inputs arrive
dsp.add_function('f', func, inputs=['a', 'b'], outputs=['c'],
                 await_domain=5.0)      # Wait up to 5 seconds
```

### `await_result`

Controls whether output assignment waits for async results:

```python
dsp.add_function('f', func, inputs=['a'], outputs=['b'],
                 await_result=True)     # Wait for result before assignment
dsp.add_function('f', func, inputs=['a'], outputs=['b'],
                 await_result=3.0)      # Wait up to 3 seconds
dsp.add_function('f', func, inputs=['a'], outputs=['b'],
                 await_result=False)    # Don't wait (default)
```

## Performance Considerations

- **Thread overhead** — creating threads costs ~1ms each. Use `async` only for functions taking >10ms
- **Process overhead** — spawning processes costs ~50-100ms. Use `parallel` only for functions taking >500ms
- **Pickling** — `parallel` executors pickle functions and arguments. Lambda functions and local objects may fail
- **Memory** — each process has its own memory space. Large data structures are copied, not shared
- **GIL** — `async` (threads) does not bypass the GIL. Use `parallel` for CPU-bound Python code

## Example

```python
import schedula as sh
import time, os

dsp = sh.Dispatcher()

def slow_task(x):
    time.sleep(1)
    return os.getpid(), x * 2

for i in range(6):
    dsp.add_function(function=slow_task, inputs=['start'], outputs=[f'res_{i}'])

# Sequential: ~6 seconds
sol = dsp(inputs={})

# Async (threads): ~1 second, same PID
sol = dsp(inputs={}, executor='async').result()
pids = {sol[f'res_{i}'][0] for i in range(6)}
assert len(pids) == 1  # Same process

# Parallel (processes): ~1 second, different PIDs
sol = dsp(inputs={}, executor='parallel').result()
pids = {sol[f'res_{i}'][0] for i in range(6)}
assert len(pids) == 6  # Different processes

sh.shutdown_executors()
```

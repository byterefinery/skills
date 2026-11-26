# Advanced Topics

## Web Workers

Run Pyodide in a web worker to avoid blocking the UI thread. Requires module-type workers (ES modules).

### Worker Code

```js
// webworker.mjs
import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v0.27.1/full/pyodide.mjs";

const pyodide = await loadPyodide();

self.onmessage = async (event) => {
  const { id, python, context } = event.data;

  // Auto-load packages from imports
  await pyodide.loadPackagesFromImports(python);

  // Create namespace from context
  const dict = pyodide.globals.get("dict");
  const globals = dict(Object.entries(context));

  try {
    const result = await pyodide.runPythonAsync(python, { globals });
    self.postMessage({ result, id });
  } catch (error) {
    self.postMessage({ error: error.message, id });
  }
};
```

### Main Thread

```js
// workerApi.mjs
const worker = new Worker("./webworker.mjs", { type: "module" });

let nextId = 1;
function requestResponse(msg) {
  const id = nextId++;
  return new Promise((resolve) => {
    const listener = (event) => {
      if (event.data?.id === id) {
        worker.removeEventListener("message", listener);
        const { id, ...rest } = event.data;
        resolve(rest);
      }
    };
    worker.addEventListener("message", listener);
    worker.postMessage({ id, ...msg });
  });
}

export async function asyncRun(script, context = {}) {
  return requestResponse({ python: script, context });
}
```

```js
// Consumer
import { asyncRun } from "./workerApi.js";

const { result, error } = await asyncRun(
  "import statistics; statistics.stdev(A_rank)",
  { A_rank: [0.8, 0.4, 1.2, 3.7, 2.6, 5.8] }
);
```

## Streams (stdin/stdout/stderr)

### From loadPyodide Options

```js
const pyodide = await loadPyodide({
  stdin: () => prompt("Input: "),
  stdout: (msg) => console.log("Py:", msg),
  stderr: (msg) => console.error("Py:", msg),
});
```

### setStdin

```js
// Error on read
pyodide.setStdin({ error: true });

// Callback-based input
pyodide.setStdin({
  stdin: () => "auto response\n",  // string with newline
  // or: stdin: () => new Uint8Array([0x61, 0x0a]),  // bytes
  // or: stdin: () => 0x61,  // single byte
  // or: stdin: () => undefined,  // EOF
  isatty: true,
});

// Replay from array
class InputReplay {
  constructor(lines) { this.lines = lines; this.i = 0; }
  stdin() { return this.lines[this.i++]; }
}
pyodide.setStdin(new InputReplay(["a", "b", "c"]));

// Low-level read handler (Node.js)
const fs = require("fs");
const fd = fs.openSync("input.txt", "r");
pyodide.setStdin({
  read: (buffer) => fs.readSync(fd, buffer),
  isatty: false,
});
```

### setStdout / setStderr

```js
// Batched handler (complete lines or flushed partials)
pyodide.setStdout({ batched: (line) => console.log("OUT:", line) });

// Raw handler (one byte at a time)
pyodide.setStdout({ raw: (byte) => output.push(String.fromCharCode(byte)) });

// Write handler (Uint8Array)
pyodide.setStdout({
  write: (buffer) => {
    process.stdout.write(Buffer.from(buffer));
    return buffer.length;
  },
  isatty: true,
});

// Reset to default
pyodide.setStdout();
```

## Keyboard Interrupts

WASM has no preemptive multitasking. Interrupts use a `SharedArrayBuffer`.

### Setup

```js
// Main thread
const interruptBuffer = new Uint8Array(new SharedArrayBuffer(1));
const worker = new Worker("pyodideWorker.js", { type: "module" });
worker.postMessage({ cmd: "setInterruptBuffer", interruptBuffer });

function interrupt() {
  interruptBuffer[0] = 2; // SIGINT
}

// Worker thread
self.onmessage = (msg) => {
  if (msg.data.cmd === "setInterruptBuffer") {
    pyodide.setInterruptBuffer(msg.data.interruptBuffer);
  }
};
```

### Custom Signal Handler (Python)

```python
import signal

def handle_sigint(signum, frame):
    print("Interrupted!")

signal.signal(signal.SIGINT, handle_sigint)
```

### Interrupting JavaScript

Call `pyodide.checkInterrupt()` periodically in JS code called from Python:

```js
function blockingSleep(t) {
  for (let i = 0; i < t * 20; i++) {
    Atomics.wait(sleepBuffer, 0, 0, 50);
    pyodide.checkInterrupt(); // allows KeyboardInterrupt
  }
}
```

### Interrupting stdin Reads

```js
pyodide.setStdin({
  read: (buf) => {
    const status = Atomics.wait(stdinBuffer, 0, 0, 100);
    if (status === "timed-out") {
      pyodide.checkInterrupt();
      return 0;
    }
    // handle data...
  },
});
```

## Sockets (Node.js Only)

Experimental socket support via Node.js native sockets.

```js
const pyodide = await loadPyodide();
await pyodide.useNodeSockFS(); // must be called before socket imports
```

```python
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", 8080))
s.sendall(b"Hello, world")
data = s.recv(1024)
s.close()
```

Requires `--experimental-wasm-stack-switching` on Node ≤ 24. Not available in browsers.

## SDL / Canvas

For SDL-based packages (pygame, etc.):

```js
// Set canvas
const canvas = document.createElement("canvas");
canvas.id = "canvas";
document.body.appendChild(canvas);
pyodide.canvas.setCanvas2D(canvas);

// Enable SDL (experimental)
pyodide._api._skip_unwind_fatal_error = true;
```

### Game Loops

Infinite loops block the browser. Use `asyncio.sleep` to yield:

```python
import asyncio

async def run_game():
    clock = pygame.time.Clock()
    fps = 60
    while True:
        handle_events()
        update()
        draw()
        await asyncio.sleep(1 / fps)  # yield to browser
```

## WASM Constraints

### No Threading

```python
import threading
t = threading.Thread(target=my_func)
t.run()   # works (runs in main thread)
t.start() # RuntimeError: can't start new thread
```

Workaround: check thread support and force single-thread:

```python
import sys, platform
def can_start_thread():
    if sys.platform == "emscripten":
        return sys._emscripten_info.pthreads
    return platform.machine() not in ("wasm32", "wasm64")
```

### No Raw Sockets (Browser)

Sockets only work in Node.js with `useNodeSockFS()`. For browser networking, use:

- `pyfetch` / `js.fetch` for HTTP
- WebSockets via `js.WebSocket`
- `requests` / `urllib3` (limited, no streaming outside workers)

### Memory Limits

WASM linear memory grows but cannot shrink. Monitor with:

```js
pyodide._module.HEAP8.length; // bytes
```

### Stack Switching

`enableRunUntilComplete: true` (default) allows `loop.run_until_complete()` via JavaScript Promise Integration. Requires `--experimental-wasm-stack-switching` on Node ≤ 24.

## Complete HTML Example

```html
<!doctype html>
<html>
<head>
  <script type="module">
    import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v0.27.1/full/pyodide.mjs";

    const output = document.getElementById("output");

    async function main() {
      const pyodide = await loadPyodide({
        stdout: (msg) => { output.value += msg + "\n"; },
      });

      // Load and run
      await pyodide.loadPackage("micropip");
      await pyodide.runPythonAsync(`
        import micropip
        await micropip.install("snowballstemmer")
        import snowballstemmer
        stemmer = snowballstemmer.stemmer("english")
        print(stemmer.stemWords("go goes going gone".split()))
      `);
    }

    main();
  </script>
</head>
<body>
  <textarea id="output" style="width:100%" rows="10"></textarea>
</body>
</html>
```

## CDN URLs

| Channel | URL |
|---|---|
| Latest release | `https://cdn.jsdelivr.net/pyodide/v{version}/full/pyodide.mjs` |
| Dev (main) | `https://cdn.jsdelivr.net/pyodide/dev/full/pyodide.mjs` |
| Debug build | `https://cdn.jsdelivr.net/pyodide/v{version}/debug/pyodide.mjs` |

## Downloading

- **GitHub releases**: `pyodide-{version}.tar.bz2` (full) or `pyodide-core-{version}.tar.bz2` (minimal)
- **npm**: `npm install pyodide`
- **Serving locally**: `python -m http.server` from the distribution folder

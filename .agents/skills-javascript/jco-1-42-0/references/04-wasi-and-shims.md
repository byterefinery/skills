# WASI support and shims

Source material: jco book chapters *WASI support*, *Preview 2 shim*, *Preview 3 shim*, plus CLI source at tag jco-v1.42.0.

Components that import WASI interfaces need a host implementation at runtime. Jco ships two npm packages and `jco transpile` maps WASI imports to them automatically:

| WASI version | Package | Mapped imports |
|---|---|---|
| 0.2.x | `@bytecodealliance/preview2-shim` | `wasi:cli`, `clocks`, `filesystem`, `http`, `io`, `random`, `sockets` |
| 0.3.x | `@bytecodealliance/preview3-shim` | `wasi:cli`, `clocks`, `filesystem`, `http`, `random`, `sockets` (no `io` — streams/pollables are replaced by component-model `stream<T>`/`future<T>`) |

Both provide Node.js and browser builds selected via the `node` export condition, so the same transpiled component runs in either. Install the shim your component needs:

```console
npm install @bytecodealliance/preview2-shim
# or
npm install @bytecodealliance/preview3-shim
```

The mapping is the same `--map` mechanism; `--no-wasi-shim` treats WASI like any other import.

## Preview 2 shim subpaths

| Subpath | Contents |
|---|---|
| `@bytecodealliance/preview2-shim` | All subsystem namespaces re-exported |
| `.../cli` | `wasi:cli` environment, exit, stdio, terminal |
| `.../clocks` | wall and monotonic clocks |
| `.../filesystem` | types and preopens, plus browser adapters |
| `.../http` | types, outgoing and incoming handlers |
| `.../io` | errors, streams, poll |
| `.../random` | secure and insecure randomness |
| `.../sockets` | TCP, UDP, name lookup |
| `.../instantiation` | `WASIShim` — assembles a complete import object |
| `.../interfaces/*` | TypeScript declarations per WASI interface |
| `.../io-worker` | Node.js only: hooks for extensions inside the I/O worker |
| `.../browser/helpers/cli` | Browser only: host-side CLI helpers (fixed stdin buffer) |
| `.../helpers/filesystem` | Host-side filesystem helpers (both builds) |

### WASIShim and sandboxing

```js
import { WASIShim } from '@bytecodealliance/preview2-shim/instantiation';

const shim = new WASIShim({
  sandbox: {
    preopens: { '/data': '/tmp/guest-data' }, // Node.js: guest path -> host path
    env: { MODE: 'sandboxed' },
    enableNetwork: false,
  },
});
const component = await instantiate(loader, shim.getImportObject());
```

Each instance carries its own environment, arguments, stdio handlers, and preopens. Underscore-prefixed functions (`_setStdin`, `_setPreopens`, ...) configure the shim; public `helpers/` subpaths are separate host-side helpers.

### Platform behavior

- **Node.js:** no filesystem access by default (no preopens until configured); host environment variables and network are available by default. Tested against the Wasmtime WASI conformance suite.
- **Browsers:** capability-safe — clocks/randomness use Web APIs, stdio writes to console, stdin closed, outbound HTTP via `fetch`, empty preopens until configured, raw sockets unavailable without an adapter. Deterministic in-memory filesystem/HTTP/socket implementations can be opted into for tests.

## Preview 3 shim

WASI 0.3 replaces `wasi:io` streams/pollables with component-model `stream<T>` and `future<T>`, so there is no `io` subsystem. Every supported 0.3.x interface version maps to the current shim (0.3 releases are not expected to break). Subpaths mirror Preview 2 plus Node-only `.../stream` (`stream()`, `StreamReader`, `StreamWriter`) and `.../future` (`future()`, `FutureReader`, `FutureWriter`). Preview 3 exports are asynchronous; configure via CLI setters mirroring Preview 2 (`_setArgs`, `_setEnv`, ...). Preview 3 support is experimental.

## `jco run` — run a WASI Command component

```console
jco run command.wasm [args...]
```

Jco-specific options are `--jco-`-prefixed (the command allows unknown options/excess arguments, so guest args pass through directly):

| Option | Purpose |
|---|---|
| `--jco-dir <dir>` | Keep transpiled output in this directory instead of a temp dir |
| `--jco-trace` | Enable call tracing |
| `--jco-import <module>` | Import a setup module before the component runs |
| `--jco-map <mappings...>` | `specifier=./output` custom import mappings |
| `--jco-import-bindings [js\|optimized\|hybrid\|direct-optimized]` | Import bindings mode |
| `--jco-cm-runtime-es-module <base>` | Experimental CM runtime package/directory base |

## `jco serve` — serve a WASI HTTP component

```console
jco serve --port 8080 server.wasm [args...]
```

| Option | Purpose |
|---|---|
| `--port <number>` / `--host <host>` | Listen address |
| `--isolate-requests [worker\|instance]` | Isolate every request in a fresh worker (default) or component instance |
| `--isolate-worker-pool-size <n>` | Prewarmed one-shot request workers (default 50) |
| `--jco-dir`, `--jco-trace`, `--jco-import`, `--jco-map`, `--jco-import-bindings`, `--jco-cm-runtime-es-module` | Same controls as `jco run` |

## Security notes

- `jco run`/`serve` and the default shims expose host environment, network, and filesystem (via preopens) unless explicitly sandboxed. **Do not run untrusted components** with ambient filesystem, environment, or network access — sandbox through custom instantiation and a configured `WASIShim`.
- Prefer Wasmtime when peak runtime performance matters; use jco when JS integration is the goal.

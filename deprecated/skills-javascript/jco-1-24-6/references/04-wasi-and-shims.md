# WASI and Shims

## Overview

WASI (WebAssembly System Interface) provides system-level interfaces for WebAssembly components. jco uses `@bytecodealliance/preview2-shim` to provide WASI implementations for Node.js and browsers.

## Installation

```bash
pnpm install @bytecodealliance/preview2-shim
```

## Automatic WASI Mapping

`jco transpile` automatically maps WASI imports to preview2-shim:

```
wasi:cli/*       → @bytecodealliance/preview2-shim/cli#*
wasi:clocks/*    → @bytecodealliance/preview2-shim/clocks#*
wasi:filesystem/*→ @bytecodealliance/preview2-shim/filesystem#*
wasi:http/*      → @bytecodealliance/preview2-shim/http#*
wasi:io/*        → @bytecodealliance/preview2-shim/io#*
wasi:random/*    → @bytecodealliance/preview2-shim/random#*
wasi:sockets/*   → @bytecodealliance/preview2-shim/sockets#*
```

Disable with `--no-wasi-shim`.

## WASI Subsystems

| Subsystem | Interfaces | Purpose |
|---|---|---|
| `wasi:cli` | environment, stdin, stdout, stderr, terminal-* | Command-line I/O |
| `wasi:clocks` | monotonic-clock, wall-clock | Time operations |
| `wasi:filesystem` | types, preopens | File system access |
| `wasi:http` | types, incoming-handler, outgoing-handler | HTTP client/server |
| `wasi:io` | error, poll, streams | I/O primitives |
| `wasi:random` | random, insecure-seed, insecure | Random number generation |
| `wasi:sockets` | network, tcp, udp, ip-name-lookup | Network sockets |

## Direct Import Usage

Import WASI interfaces directly in JS:

```js
import { getRandomBytes } from '@bytecodealliance/preview2-shim/random/random';
const bytes = getRandomBytes(32);
```

## WASIShim Class

For instantiation mode, use `WASIShim` to provide WASI imports:

```js
import { WASIShim } from '@bytecodealliance/preview2-shim/instantiation';

const shim = new WASIShim();
const importObject = shim.getImportObject();

// Versioned import object
const versioned = shim.getImportObject({ asVersion: '0.2.3' });
```

### Usage with transpiled components

```js
import { WASIShim } from '@bytecodealliance/preview2-shim/instantiation';
import { instantiate } from './dist/transpiled/component.js';
import { readFile } from 'node:fs/promises';

const loader = async (path) => {
  const buf = await readFile(new URL(`./${path}`, import.meta.url));
  return await WebAssembly.compile(buf);
};

const component = await instantiate(
  loader,
  new WASIShim().getImportObject()
);
```

## Sandboxing

Restrict guest access to host resources:

### Fully sandboxed

```js
const sandboxedShim = new WASIShim({
  sandbox: {
    preopens: {},           // No filesystem access
    env: {},                // No environment variables
    args: ['my-program'],   // Custom arguments
    enableNetwork: false,   // No network access
  }
});
```

### Limited filesystem access

```js
const limitedShim = new WASIShim({
  sandbox: {
    preopens: {
      '/data': '/tmp/guest-data',
      '/config': '/etc/app',
    },
    env: { ENV1: '42' },
  }
});
```

### Sandbox options

| Option | Type | Default | Description |
|---|---|---|---|
| `preopens` | `Record<string, string>` | Full filesystem | Virtual → host path mapping |
| `env` | `Record<string, string>` | `process.env` | Visible environment variables |
| `args` | `string[]` | `process.argv` | Command-line arguments |
| `enableNetwork` | `boolean` | `true` | Enable socket/HTTP access |

Each `WASIShim` instance is isolated — multiple instances with different configs don't interfere.

## Custom WASI Implementations

Override specific WASI interfaces:

```js
import { random } from '@bytecodealliance/preview2-shim';
import { WASIShim } from '@bytecodealliance/preview2-shim/instantiation';

const customShim = new WASIShim({
  random: {
    random: random.random,           // Use default
    'insecure-seed': random.insecureSeed,  // Use default
    insecure: {                      // Custom implementation
      getInsecureRandomBytes: (len) => new Uint8Array(Number(len)).fill(0),
      getInsecureRandomU64: () => 42n,
    },
  },
});
```

## Adding WASI Proposals

To support new WASI proposals, extend the default map configuration:

```bash
jco transpile component.wasm --map 'wasi:new-proposal/*=shim-pkg/new-proposal#*' -o out
```

Publish shim packages to npm per JS ecosystem conventions.

## preview3-shim

`@bytecodealliance/preview3-shim` provides WASI Preview 3 support for Node.js. Usage follows the same patterns as preview2-shim but targets the newer WASI specification.

## Browser Support

Browser support for WASI is experimental. The preview2-shim package works in browsers but is not production-ready.

For browser use, import from the `/component` subpath:

```js
import { transpile } from '@bytecodealliance/jco/component';
```

## Gotchas

- **Default is full access** — WASIShim without sandbox config gives the guest full filesystem, env, and network access (matching Node.js defaults)
- **Direct preopen functions are global** — `_setPreopens`, `_clearPreopens` modify global state. Use `WASIShim` with `sandbox` option for isolation
- **`enableNetwork: false` throws** — all socket and HTTP operations throw "access-denied" errors when network is disabled
- **Version mismatch** — ensure WASI package versions in WIT match the shim versions; use `asVersion` in `getImportObject()` for versioned imports

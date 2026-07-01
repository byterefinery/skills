# Run and Serve

## jco run — WASI Command Components

Run components that implement the WASI Command world:

```bash
jco run component.wasm arg1 arg2
```

This uses the preview2-shim WASI implementation, providing full access to filesystem, environment variables, and network (matching Node.js defaults).

### Example

```bash
jco run cowsay.component.wasm "Hello Wasm!"
```

## jco serve — WASI HTTP Components

Serve components that implement the WASI HTTP Proxy world:

```bash
jco serve --port 8080 server.wasm
```

This starts a JavaScript HTTP server that routes requests to the component.

> **Not for production** — use Wasmtime, Cloudflare Workers, or a proper server in production. `jco serve` is a development convenience.

## Manual Instantiation with Custom Overrides

For fine-grained control over WASI imports, use instantiation mode:

### Build with async instantiation

```bash
jco transpile component.wasm --instantiation async -o dist/transpiled
```

### Instantiate with no overrides

```js
import { WASIShim } from '@bytecodealliance/preview2-shim/instantiation';
import { readFile } from 'node:fs/promises';

const wasmModule = await import('./dist/transpiled/component.js');

const loader = async (path) => {
  const buf = await readFile(new URL(`./${path}`, import.meta.url));
  return await WebAssembly.compile(buf);
};

const component = await wasmModule.instantiate(
  loader,
  new WASIShim().getImportObject()
);
```

### Instantiate with custom overrides

```js
import { random } from '@bytecodealliance/preview2-shim';
import { WASIShim } from '@bytecodealliance/preview2-shim/instantiation';

const customShim = new WASIShim({
  random: {
    random: random.random,
    'insecure-seed': random.insecureSeed,
    insecure: {
      getInsecureRandomBytes: (len) => new Uint8Array(Number(len)).fill(0),
      getInsecureRandomU64: () => 42n,
    },
  },
});

const component = await wasmModule.instantiate(loader, customShim.getImportObject());
```

### Browser instantiation

In browsers, the loader is not needed:

```js
const component = await wasmModule.instantiate(undefined, wasmImports);
```

## Versioned Imports

```js
import { WASIShim } from '@bytecodealliance/preview2-shim/instantiation';

const shim = new WASIShim();

// Unversioned
const unversioned = shim.getImportObject();

// Versioned
const versioned = shim.getImportObject({ asVersion: '0.2.3' });
```

## Sandboxing at Runtime

```js
const sandboxedShim = new WASIShim({
  sandbox: {
    preopens: {
      '/data': '/tmp/guest-data',
    },
    env: { APP_ENV: 'sandboxed' },
    args: ['sandboxed-program'],
    enableNetwork: false,
  }
});

const component = await wasmModule.instantiate(loader, sandboxedShim.getImportObject());
```

## Performance Notes

- `jco run` and `jco serve` are JavaScript implementations using preview2-shim
- Wasmtime provides significantly better performance for production workloads
- Use `jco run`/`jco serve` for development, testing, and when JS virtualization is required
- For production, deploy to Wasmtime, Cloudflare Workers, Fastly Compute, or similar

## Multiple Component Instances

Each `WASIShim` instance is isolated. Create separate instances for separate components:

```js
const shim1 = new WASIShim({ sandbox: { preopens: { '/a': '/data/a' } } });
const shim2 = new WASIShim({ sandbox: { preopens: { '/b': '/data/b' } } });

const comp1 = await wasmModule.instantiate(loader, shim1.getImportObject());
const comp2 = await wasmModule.instantiate(loader, shim2.getImportObject());
```

## Gotchas

- **`jco serve` is development-only** — it's a convenience wrapper, not a production server
- **Filesystem access is full by default** — always use sandboxing for untrusted components
- **Each WASIShim is isolated** — preopens, env, and args don't leak between instances
- **Browser needs no loader** — pass `undefined` for the core module loader in browser environments

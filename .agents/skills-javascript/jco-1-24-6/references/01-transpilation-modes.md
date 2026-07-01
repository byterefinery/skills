# Transpilation Modes

## ESM Integration (Default)

Default mode produces a JavaScript ES module that directly imports component imports and exports component exports.

```bash
jco transpile component.wasm -o out-dir
```

Output:
```
out-dir/
├── component.core.wasm     # Core Wasm binary (may be multiple)
├── component.js            # ES module entry point
├── component.d.ts          # TypeScript definitions
└── interfaces/             # Per-interface .d.ts files
    ├── iface1.d.ts
    └── iface2.d.ts
```

Import and use:

```js
import { add } from './out-dir/component.js';
const result = add.add(1, 2);
```

Requires `"type": "module"` in `package.json` for Node.js.

## Instantiation Mode

Export an `instantiate()` function that accepts imports as arguments. Useful for providing custom implementations at runtime.

### Async Instantiation

```bash
jco transpile component.wasm --instantiation async -o out-dir
```

```js
import { instantiate } from './out-dir/component.js';
import { readFile } from 'node:fs/promises';

const loader = async (path) => {
  const buf = await readFile(new URL(`./${path}`, import.meta.url));
  return await WebAssembly.compile(buf);
};

const component = await instantiate(loader, {
  // Provide imports here
  'wasi:cli/environment': {
    getEnvironmentVariables: () => [],
  },
});

// Use component exports
component.add(1, 2);
```

### Sync Instantiation

```bash
jco transpile component.wasm --instantiation sync -o out-dir
```

Same API but all functions are synchronous (no promises). `getCoreModule` returns `WebAssembly.Module` directly.

## Map Configuration

The `--map` flag remaps WIT import specifiers to JS module paths.

### Basic mapping

```bash
jco transpile component.wasm --map my:pkg/iface=./my-impl.js -o out
```

`my:pkg/iface@1.2.3` becomes `import { ... } from './my-impl.js'`.

### Sub-export mapping with `#`

```bash
jco transpile component.wasm --map 'my:pkg/*=./my-pkg.js#*' -o out
```

Maps all interfaces under `my:pkg/` to named exports of `./my-pkg.js`:

```js
// my-pkg.js
export const iface = {
  fn() { return 'implemented'; }
};
```

### Wildcard mapping

```bash
jco transpile component.wasm --map 'my:pkg/*@1.2.3=./my-pkg.js#*' -o out
```

Version-specific wildcard: only matches `@1.2.3` interfaces.

### Default WASI mappings

jco automatically provides these internal mappings (override with `--no-wasi-shim`):

```
wasi:cli/*@0.2.0=@bytecodealliance/preview2-shim/cli#*
wasi:clocks/*@0.2.0=@bytecodealliance/preview2-shim/clocks#*
wasi:filesystem/*@0.2.0=@bytecodealliance/preview2-shim/filesystem#*
wasi:http/*@0.2.0=@bytecodealliance/preview2-shim/http#*
wasi:io/*@0.2.0=@bytecodealliance/preview2-shim/io#*
wasi:random/*@0.2.0=@bytecodealliance/preview2-shim/random#*
wasi:sockets/*@0.2.0=@bytecodealliance/preview2-shim/sockets#*
```

### Stub generation

Generate empty implementations to inspect bindings:

```bash
jco transpile example.wit --stub -o output --map 'test:pkg/*=./imports.js#*'
```

This produces bindgen code showing exactly what interfaces and functions need implementing.

## Transpile Options Reference

| Option | Description |
|---|---|
| `--name <n>` | Custom output filename (`out-dir/[n].js`) |
| `--minify` | Minify output JS |
| `--optimize` | Run core Wasm through Binaryen; pass extra args with `-- <args>` |
| `--tla-compat` | Export `$init` promise instead of using top-level-await |
| `--js` | Convert core Wasm to JavaScript (for environments without core Wasm support) |
| `--base64-cutoff=<n>` | Max bytes for base64 inlining of Wasm; `0` disables entirely |
| `--no-wasi-shim` | Disable automatic WASI → preview2-shim mapping |
| `--no-nodejs-compat` | Disable Node.js compat for loading core Wasm with FS |
| `--instantiation [async\|sync]` | Export `instantiate()` function instead of direct ESM |
| `--valid-lifting-optimization` | Skip internal validation (minor size saving) |
| `--tracing` | Emit tracing calls for function entry/exit |
| `--no-namespaced-exports` | Remove string-keyed exports (TypeScript compat) |
| `--async-mode jspi` | EXPERIMENTAL: JavaScript Promise Integration for async |
| `--async-imports <imports...>` | EXPERIMENTAL: Specify async imports (with `--async-mode`) |
| `--async-exports <exports...>` | EXPERIMENTAL: Specify async exports (with `--async-mode`) |
| `--import-bindings <mode>` | `js` (default), `hybrid`, `optimized`, `direct-optimized` |

## Export Conventions

Components export both the direct interface and the canonical named interface:

```js
export { interface, interface as 'my:pkg/interface@version' }
```

The versioned string export allows disambiguation when multiple interfaces share a name. Disable with `--no-namespaced-exports`.

## Import Conventions

Import specifiers strip version:

```
my:pkg/interface@1.2.3 → import { fn } from 'my:pkg/interface'
```

## Browser Support

Use the `/component` subpath for browser-compatible imports:

```js
import { transpile } from '@bytecodealliance/jco/component';
```

This avoids Node.js-specific dependencies and works with standard bundlers.

## WebIDL Imports (Experimental)

Components using the `webidl:` namespace get zero-configuration bindings to global objects:

- `getWindow()` → returns the global object
- `global-console` → binds to `globalThis.console`

This is experimental; see IDL fixtures in the jco repo for examples.

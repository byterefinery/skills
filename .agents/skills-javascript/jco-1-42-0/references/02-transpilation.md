# Transpilation

Source material: jco book chapter *Transpiling* (docs at tag jco-v1.42.0).

Components transpile in two modes:

- **ESM integration (default)** — the output is a JS module that imports the component's imports and exports the component's exports, usable as if imported directly.
- **Instantiation (`--instantiation sync|async`)** — the output exports a single `instantiate()` function that takes imports as an argument, enabling dynamic import supply and multiple instantiations.

Transpiled output is ESM; for Node.js, the nearest package.json should set `{ "type": "module" }`.

```console
jco transpile component.wasm -o out-dir
```

```js
import { fn } from './out-dir/component.js';
fn();
```

## Options

| Option | Effect |
|---|---|
| `--name <name>` | Custom name for the component JS file: `out-dir/[name].js` |
| `--minify` | Minify the component JS |
| `--optimize` | Run internal core Wasm files through Binaryen; pass raw flags after `--` |
| `--tla-compat` | Do not rely on top-level await; import and await an `$init` promise first |
| `--js` | Convert core Wasm files to JavaScript (ASM.js) for environments without core Wasm |
| `--base64-cutoff=<n>` | Max bytes for inlining Wasm as base64 in the JS; `0` disables inlining |
| `--no-wasi-shim` | Disable automatic `wasi:*` mapping to the preview shims |
| `--map <specifier=target...>` | Custom import mappings (see below) |
| `--no-nodejs-compat` | Disable Node.js compat in output for loading core Wasm via FS |
| `--instantiation [sync\|async]` | Export an `instantiate()` function instead of direct ESM |
| `--import-bindings [js\|optimized\|hybrid\|direct-optimized]` | Bindings mode for imports (default `js`); see [09-optimized-host-bindings](09-optimized-host-bindings.md) |
| `--cm-runtime-es-module <base>` | Experimental: import the component runtime from a package/directory base instead of bundling jco's runtime |
| `--valid-lifting-optimization` | Remove internal validity checks (smaller output); assumes valid components |
| `--flags-as-bigint` | WIT flags as `bigint` with named flag constants (default: objects of booleans) |
| `--variants-inline-cases` | Inline WIT variant cases in the discriminated union instead of named interfaces |
| `--use-namespace-objects` | Export namespace objects for enums, flags, variants; implies `--flags-as-bigint`; incompatible with `--variants-inline-cases` |
| `--enum-values-screaming-snake-case` | Enum values as `SCREAMING_SNAKE_CASE` strings instead of kebab-case |
| `--tracing` | Emit tracing calls at all function entry/exit |
| `--call-tracking` | Emit invocation handles (`_util.calls.start(fn, ...args)`) to observe selected guest execution |
| `--no-component-error-wrapping` | Throw the lifted error payload directly for top-level `result::err` instead of wrapping in `ComponentError` |
| `--no-namespaced-exports` | Remove string-keyed canonical exports (`export { iface as 'my:pkg/iface@1.2.3' }`) that TypeScript does not support |
| `--async-mode jspi` | EXPERIMENTAL: JS Promise Integration for async functions/methods |
| `--async-imports <imports...>` / `--async-exports <exports...>` | EXPERIMENTAL: mark specific imports/exports async; used with `--async-mode` |
| `--stub` (with a WIT path) | Generate a stub implementation to inspect bindings without a component |

## Export and import conventions

- A component exports both the direct interface and the canonical named interface: `export { interface, interface as 'my:pkg/interface@version' }`. Disable the string-keyed form with `--no-namespaced-exports`.
- In default ESM mode, import specifiers are emitted as `registry:name/interface` with versions removed: an import of `my:pkg/interface@1.2.3` becomes `import { fn } from 'my:pkg/interface'`.
- Generated bindings expose a `_util` object (`stop()`, `isComponentError(value)`); see [05-errors-and-lifecycle](05-errors-and-lifecycle.md).

## Map configuration

`--map` rewrites import specifiers; it also rewrites the keys of `imports` in instantiation mode.

```console
# whole module
jco transpile component.wasm --map my:pkg/interface@1.2.3=./myinterface.js
# named export of a module
jco transpile component.wasm --map my:pkg/interface@1.2.3=./mypkg.js#interface
# wildcard: all interfaces of the package read off named exports
jco transpile component.wasm --map 'my:pkg/*@1.2.3=./mypkg.js#*'
```

Target modules export either plain functions or an object per interface:

```js
// whole-module mapping
export function fn () { /* ... */ }

// `#interface` mapping — one file can define several interfaces
export const iface = {
  fn (record) { return 'string'; },
};
```

WASI imports are given special treatment via the same map mechanism; jco always applies default mappings like `wasi:cli/*@0.2.0=@bytecodealliance/preview2-shim/cli#*` for all subsystems (`cli`, `clocks`, `filesystem`, `http`, `io`, `random`, `sockets`). `--no-wasi-shim` disables this. To support a new WASI proposal, extend the default map with `--map wasi:subsystem/*=<shimpkg>/subsystem#*`.

## Instantiation mode

`jco transpile component.wasm --instantiation async` (or `sync`) produces a module with one function:

```ts
// async mode
export async function instantiate(
  getCoreModule: (path: string) => Promise<WebAssembly.Module>,
  imports: { [importName: string]: any },
  instantiateCore?: (module: WebAssembly.Module, imports: Record<string, any>) => Promise<WebAssembly.Instance>,
  options?: InstantiateOptions
): Promise<{ [exportName: string]: any }>;
```

Sync mode is the same with all promises removed. Notes:

- `imports` keys are the component's import names as WIT spells them, without versions (e.g. `wasi:cli/environment`, `jco:node/process`). `--map` rewrites those keys the same way it rewrites ESM specifiers. Jco's default Node capability map is **not** applied to instantiation output.
- `getCoreModule` is typically `async (path) => WebAssembly.compile(await readFile(new URL(`./${path}`, import.meta.url)))`.
- `instantiateCore` defaults to `WebAssembly.instantiate` (async) / `new WebAssembly.Instance` (sync).
- `options.onTrap` is called once per trap, as soon as it happens (including background traps and deadlocks); it runs mid-unwinding and may call `_util.stop()` but should not otherwise use the instance.
- `options.shim.globals.WebAssembly` provides a custom `WebAssembly` implementation for that instance (inherit via `Object.create(WebAssembly)` to override only selected APIs).
- Futures received from a guest are lazy: `await future` reads it, `future[Symbol.dispose]?.()` releases the readable end (idempotent; further reads reject).
- `instance._util.whenIdle()` waits for guest task exit (also resolves when the instance stops or traps); `instance._util.stop()` permanently stops the instantiation including background guest work.

## WebIDL (experimental)

With the `webidl:` interface namespace, jco auto-binds imports to the global object: a top-level `getWindow` function (or any singleton global name) yields the global object, and an interface named `global-console` binds to `globalThis.console` (dashes become `.` access). Highly experimental.

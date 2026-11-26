# Library API and bundling

Source material: jco repo `.ai/skills/jco-use` references (library.md) and package READMEs at tag jco-v1.42.0. Both `@bytecodealliance/jco` and `@bytecodealliance/jco-transpile` are ESM packages.

## `@bytecodealliance/jco-transpile`

```sh
pnpm add @bytecodealliance/jco-transpile
```

Main export:

- `transpile(path, options)` and `transpileBytes(bytes, options)` → `{ files, imports, exports }`
- `generateHostTypes(witPath, options)` and `generateGuestTypes(witPath, options)` → `Record<string, Uint8Array>`
- `writeFiles(files)` — creates parent directories and writes generated outputs
- `componentWitMetadataForWorld(...)` — WIT world metadata

Common transpilation options mirror the CLI in camelCase: `name`, `outDir`, `map`, `instantiation`, `importBindings`, `asyncMode`, `asyncImports`, `asyncExports`, `asyncWasiImports`, `asyncWasiExports`, `wasiShim`, `emitTypescriptDeclarations`, `tlaCompat`, `nodejsCompat`, `base64Cutoff`, `minify`, `optimize`, `optimizeOptions`, `js`, `tracing`, `namespacedExports`, `multiMemory`, `strict`, `flagsAsBigInt`, `stub`.

```js
import { transpile, writeFiles } from '@bytecodealliance/jco-transpile';

const result = await transpile('component.wasm', {
  outDir: 'generated',
  instantiation: 'async',
  map: { 'example:host/api': './host.js' },
});
await writeFiles(result.files);
console.log({ imports: result.imports, exports: result.exports });
```

`outDir` prefixes returned file keys; generation is in-memory until `writeFiles` (or caller-owned I/O) runs.

### Subpath exports

- `@bytecodealliance/jco-transpile/helpers` — `getCoreModuleWithBaseDir` (and sync variant) core-module loaders for custom instantiation
- `@bytecodealliance/jco-transpile/wasm-tools` — async `print`, `parse`, `componentWit`, `componentNew`, `componentEmbed`, `metadataShow`, `metadataAdd`, `componentWitMetadataForWorld` on bytes
- `@bytecodealliance/jco-transpile/component` — raw bindgen component exports, only when the higher-level API is insufficient

## `@bytecodealliance/jco`

The package root exposes byte-oriented `transpile(bytes, options)` and `opt(bytes, options)`, path-oriented `types(witPath, options)`, wasm-tools helpers, and `preview1AdapterCommandPath` / `preview1AdapterReactorPath`. The `@bytecodealliance/jco/component` subpath is a browser-compatible export with initialized `generate` and `generateTypes` (transpile alias) — no Node.js deps. Prefer `jco-transpile` for ordinary Node automation (path/byte APIs, simpler option names).

## Custom instantiation with the WASI shim

```js
import { getCoreModuleWithBaseDir } from '@bytecodealliance/jco-transpile/helpers';
import { WASIShim } from '@bytecodealliance/preview2-shim/instantiation';
import { instantiate } from './generated/component.js';

const wasi = new WASIShim({
  sandbox: { preopens: {}, env: {}, args: [], enableNetwork: false },
});

const instance = await instantiate(
  getCoreModuleWithBaseDir({ baseDir: './generated' }),
  wasi.getImportObject(),
);
```

Custom instantiation turns off automatic WASI mapping — provide every import or map it during generation. The default Preview 2 shim mirrors normal Node access and is **not** a security boundary without explicit sandbox options.

## Rolldown / Rollup plugin

Install stable Rolldown 1.x (or Rollup 4+) and the plugin:

```sh
pnpm add -D rolldown @bytecodealliance/rolldown-plugin-jco
```

```js
// rolldown.config.mjs
import { defineConfig } from 'rolldown';
import jco from '@bytecodealliance/rolldown-plugin-jco';

export default defineConfig({
  input: 'src/main.js',
  platform: 'node',
  plugins: [jco({ transpile: { minify: true } })],
});
```

- Import `./component.wasm` (or `./component.wasm?component`) in app code. The default export instantiates; import-free components also expose eager named exports.
- For components with imports, set `transpile.instantiation` to `async` or `sync`, call the default export with a core-module loader and import object, and use the returned instance or live named bindings. Do not destructure a namespace before custom instantiation (captures initial `undefined` values).
- The plugin accepts `include`, `exclude`, forwarded `transpile` options, and a `name(id)` callback; it owns `name` and `outDir`.
- Enable generic TypeScript `.wasm` declarations with `"types": ["@bytecodealliance/rolldown-plugin-jco/wasm"]`; precise per-component declarations are not yet generated.

## Related packages

- `@bytecodealliance/preview2-shim` — WASI 0.2 host implementations with configurable sandboxing
- `@bytecodealliance/preview3-shim` — WASI 0.3 (experimental)
- `@bytecodealliance/jco-std` — framework helpers (Hono/Express-style WASI HTTP adapters, Node built-in compatibility)
- Do **not** install the unscoped `jco` npm package — it is a placeholder pointing to `@bytecodealliance/jco`

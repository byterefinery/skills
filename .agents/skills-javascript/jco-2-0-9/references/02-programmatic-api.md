# Programmatic API

## @bytecodealliance/jco

### Exports

```js
import {
  transpile,
  transpileComponent,
  types,
  typesComponent,
  opt,
  print,
  parse,
  componentWit,
  componentNew,
  componentEmbed,
  metadataAdd,
  metadataShow,
  preview1AdapterCommandPath,
  preview1AdapterReactorPath,
} from "@bytecodealliance/jco";
```

### transpile(componentPath, opts)

Transpile a component from a file path.

```js
import { transpile } from "@bytecodealliance/jco";

const result = await transpile("app.wasm", {
  name: "my-component",
  outDir: "./dist",
  minify: true,
  optimize: true,
  importBindings: "optimized",
  map: {
    "my:custom/iface": "./my-impl.js",
  },
});

// result: { files: { [path]: Uint8Array }, imports: string[], exports: [string, 'function' | 'instance'][] }
```

### transpileComponent(bytes, opts)

Transpile from raw WebAssembly bytes.

```js
import { transpileComponent } from "@bytecodealliance/jco";
import { readFile } from "node:fs/promises";

const bytes = await readFile("app.wasm");
const result = await transpileComponent(bytes, { minify: true });
```

### types(witPath, opts) / typesComponent(witPath, opts)

Generate host-side TypeScript types from WIT.

```js
import { typesComponent } from "@bytecodealliance/jco";

const files = await typesComponent("wit/", {
  name: "my-component",
  worldName: "my-world",
  outDir: "./types",
  instantiation: "async",
  tlaCompat: true,
  allFeatures: true,
  strict: true,
});

// files: { [filename]: Uint8Array }
```

### guestTypes(witPath, opts)

Generate guest-side types for component implementation.

```js
import { guestTypes } from "@bytecodealliance/jco";

const files = await guestTypes("wit/", {
  outDir: "./types/guest",
  asyncExports: ["wasi:cli/run#run"],
});
```

### opt(componentBytes, opts)

Optimize a component's internal core modules with Binaryen.

```js
import { opt } from "@bytecodealliance/jco";

const { component: optimized, compressionInfo } = await opt(bytes, {
  optArgs: ["-Oz", "--asyncify"],
  quiet: true,
});
```

### wasm-tools Functions

Re-exported from `@bytecodealliance/jco-transpile/wasm-tools`:

| Function | Description |
|---|---|
| `print(bytes)` | Wasm binary → WAT text |
| `parse(wat)` | WAT text → Wasm binary |
| `componentWit(bytes, document?)` | Extract WIT from component |
| `componentNew(bytes, adapters)` | Create component from core module |
| `componentEmbed(opts)` | Embed component typing into core module |
| `metadataAdd(bytes, metadata)` | Add producer metadata |
| `metadataShow(bytes)` | Read producer metadata |

### Adapter Paths

```js
import {
  preview1AdapterCommandPath,
  preview1AdapterReactorPath,
} from "@bytecodealliance/jco";

const commandAdapter = preview1AdapterCommandPath(); // URL
const reactorAdapter = preview1AdapterReactorPath(); // URL
```

## @bytecodealliance/jco-transpile

### Exports

```js
import {
  generateHostTypes,
  generateGuestTypes,
  transpile,
  transpileBytes,
  componentWitMetadataForWorld,
  writeFiles,
} from "@bytecodealliance/jco-transpile";
```

### transpile(componentPath, opts)

Full transpilation pipeline. Returns `{ files, imports, exports }`.

### transpileBytes(bytes, opts)

Transpile from raw bytes. Same options and return type as `transpile`.

### generateHostTypes(witPath, opts)

Generate host-side types directly.

```js
import { generateHostTypes } from "@bytecodealliance/jco-transpile";

const types = await generateHostTypes("wit/", {
  name: "my-component",
  worldName: "my-world",
  instantiation: { tag: "async" },
  tlaCompat: false,
  features: { tag: "all" },
  guest: false,
  strict: false,
  asyncMode: null,
});

// types: { [filename]: Uint8Array }
```

### generateGuestTypes(witPath, opts)

Generate guest-side types.

```js
import { generateGuestTypes } from "@bytecodealliance/jco-transpile";

const types = await generateGuestTypes("wit/", {
  name: "my-component",
  guest: true,
  asyncMode: {
    tag: "jspi",
    val: {
      imports: ["wasi:io/poll#poll"],
      exports: ["wasi:cli/run#run"],
    },
  },
});
```

### componentWitMetadataForWorld(witDescriptor, worldName)

Get world metadata from WIT without full transpilation.

```js
import { componentWitMetadataForWorld } from "@bytecodealliance/jco-transpile";

const metadata = await componentWitMetadataForWorld(
  { tag: "path", val: "wit/" },
  null // worldName, or string
);

// metadata: { imports: [...], exports: [...] }
```

### writeFiles(files, summaryTitle)

Write generated files to disk with optional summary.

```js
import { writeFiles } from "@bytecodealliance/jco-transpile";

await writeFiles(files, "Generated Files");
```

## TranspilationOptions Interface

```ts
interface TranspilationOptions {
  name?: string;
  instantiation?: InstantiationMode | WITInstantiationMode;
  importBindings?: "js" | "optimized" | "hybrid" | "direct-optimized";
  map?: Record<string, string>;
  asyncMode?: AsyncMode | WITAsyncMode;
  asyncImports?: string[];
  asyncExports?: string[];
  asyncWasiImports?: string[];
  asyncWasiExports?: string[];
  validLiftingOptimization?: boolean;
  tracing?: boolean;
  nodejsCompat?: boolean;
  tlaCompat?: boolean;
  base64Cutoff?: number;
  js?: boolean;
  minify?: boolean;
  optimize?: boolean;
  optimizeOptions?: OptimizeOptions;
  namespacedExports?: boolean;
  outDir?: string;
  multiMemory?: boolean;
  experimentalIdlImports?: boolean;
  wasiShim?: boolean;
  emitTypescriptDeclarations?: boolean;
  stub?: boolean;
  strict?: boolean;
}

type InstantiationMode = "async" | "sync";
type AsyncMode = "sync" | "jspi";
```

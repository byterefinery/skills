# Componentize

Building WebAssembly components from JavaScript/TypeScript using `jco componentize` (ComponentizeJS).

## Prerequisites

```bash
pnpm install @bytecodealliance/jco @bytecodealliance/componentize-js
```

`componentize-js` is dynamically imported by jco — it must be installed alongside jco.

## Basic Usage

```bash
jco componentize component.js --wit wit/component.wit --world-name myworld -o component.wasm
```

- `component.js` — the JS/TS source file implementing the WIT world
- `--wit` — path to WIT file or directory
- `--world-name` — which world to target (required if WIT has multiple worlds)
- `-o` — output `.wasm` file

## WIT World Definition

```wit
package my:pkg@0.1.0;

interface add {
    add: func(x: u32, y: u32) -> u32;
}

world myworld {
    export add;
}
```

## Implementing the World

Export interfaces as named objects matching the WIT interface names:

```js
export const add = {
  add(x, y) {
    return x + y;
  }
};
```

For TypeScript, use `jco guest-types` to generate type definitions:

```bash
jco guest-types wit/ -o generated/types --world-name myworld
```

Then implement with full type safety:

```ts
import type { Add } from '../generated/types/myworld.js';

export const add: Add = {
  add(x: number, y: number): number {
    return x + y;
  }
};
```

## Disabling WASI Imports

By default, componentize-js imports all available WASI interfaces. Disable them:

```bash
jco componentize component.js --wit wit/ --world-name myworld --disable all -o component.wasm
```

Or selectively disable:

```bash
jco componentize component.js --wit wit/ --world-name myworld --disable filesystem,sockets -o component.wasm
```

## TypeScript Build Pipeline

For TypeScript projects, bundle to JS before componentizing:

```json
{
  "scripts": {
    "gen:types": "jco guest-types wit/ -o generated/types",
    "build:js": "rollup -c",
    "build:component": "jco componentize -w wit/ -o dist/component.wasm dist/component.js",
    "build": "pnpm run gen:types && pnpm run build:js && pnpm run build:component"
  }
}
```

### Rollup config example

```js
// component.rollup.mjs
export default {
  input: 'src/component.ts',
  output: {
    file: 'dist/component.js',
    format: 'es',
  },
  external: ['test:component/resources'],  // Keep WIT imports as external
};
```

## WIT Dependencies

Install WIT dependencies using `wkg` (wasm-pkg-tools):

```bash
wkg get --format wit wasi:http@0.2.6
wkg get --format wit wasi:cli@0.2.6
```

Or with a `wkg.lock` file for reproducible builds:

```bash
wkg wit fetch
```

Dependencies go in `wit/deps/`, while your component WIT stays in `wit/component.wit`.

## StarlingMonkey

ComponentizeJS uses StarlingMonkey (SpiderMonkey engine) to embed JavaScript into WebAssembly. This provides:

- Web standards compliance (fetch, crypto, etc.)
- WASI interface support
- Sandboxed execution environment

## Output

```
OK Successfully written component.wasm with imports (wasi:cli/environment, wasi:io/poll, ...).
```

Inspect the component:

```bash
jco wit component.wasm
```

## Common Patterns

### Simple export (no WASI)

```wit
world simple {
    export greet: func(name: string) -> string;
}
```

```js
export function greet(name) {
  return `Hello, ${name}!`;
}
```

```bash
jco componentize greet.js --wit wit/ --world-name simple --disable all -o greet.wasm
```

### Import + export

```wit
world calculator {
    import log: interface {
        log: func(msg: string);
    }
    export calc: interface {
        add: func(x: u32, y: u32) -> u32;
    }
}
```

```js
import { log } from 'my:pkg/log';

export const calc = {
  add(x, y) {
    log.log(`Adding ${x} + ${y}`);
    return x + y;
  }
};
```

### HTTP server with Hono

```ts
import { Hono } from 'hono';
import { fire } from '@bytecodealliance/jco-std/wasi/0.2.x/http/adapters/hono/server';

const app = new Hono();
app.get('/', () => 'Hello World!');

fire(app);

export { incomingHandler } from '@bytecodealliance/jco-std/wasi/0.2.x/http/adapters/hono/server';
```

## Gotchas

- **`--disable all` is recommended** — unless you explicitly need WASI interfaces, disable all to keep the component small
- **Bundler must keep WIT imports external** — when bundling TS, don't bundle WIT package imports; they're resolved at componentize time
- **WIT versions matter** — older WASI versions (< 0.2.10) force componentize-js 0.19.3 fallback with known bugs
- **`--world-name` required for multi-world WIT** — always specify explicitly

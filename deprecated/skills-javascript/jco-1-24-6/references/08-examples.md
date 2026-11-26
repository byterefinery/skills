# Examples

## adder — Basic Export

Simple component exporting an `add` function.

**WIT** (`wit/component.wit`):
```wit
package docs:adder@0.1.0;

interface add {
    add: func(x: u32, y: u32) -> u32;
}

world adder {
    export add;
}
```

**JS** (`adder.js`):
```js
export const add = {
  add(x, y) {
    return x + y;
  }
};
```

**Build**:
```bash
jco componentize adder.js --wit wit/component.wit --world-name adder --disable all -o adder.wasm
jco transpile adder.wasm -o dist/transpiled
```

**Run**:
```js
import { add } from './dist/transpiled/adder.js';
console.log(add.add(1, 2)); // 3
```

## fs-write-file — WASI Filesystem

Component using `wasi:filesystem` to write a file.

**WIT**:
```wit
package example:fs-write-file@0.1.0;

world component {
    import wasi:filesystem/types@0.2.8;
    import wasi:filesystem/preopens@0.2.8;
    export run: interface {
        run: func();
    }
}
```

**JS** (`component.js`):
```js
import { types } from 'wasi:filesystem/types';
import { preopens } from 'wasi:filesystem/preopens';

export const run = {
  run() {
    const dir = preopens.openDir('.');
    const file = dir.create('hello.txt', { directory: false });
    file.write(new TextEncoder().encode('Hello from Wasm!'));
    file.close();
    dir.close();
  }
};
```

## host-logging — Custom Host Interface

Component importing a custom logging interface, implemented by the host.

**WIT**:
```wit
package example:host-logging@0.1.0;

interface log-characters {
    call: func(s: string);
}

world component {
    import wasi:logging/logging@0.1.0-draft;
    export log-characters;
}
```

**Host implementation** (`log-host.js`):
```js
export const logging = {
  log(msg) {
    console.log(`[LOG] ${msg}`);
  }
};
```

**Transpile with map**:
```bash
jco transpile component.wasm -o dist --map 'wasi:logging/*=./log-host.js#*'
```

## http-server-hono — HTTP Server with Hono

Full HTTP server using the Hono framework.

**Guest** (`src/component.ts`):
```ts
import { Hono } from 'hono';
import { fire } from '@bytecodealliance/jco-std/wasi/0.2.x/http/adapters/hono/server';

const app = new Hono();
app.get('/', () => 'Hello World!');

fire(app);

export { incomingHandler } from '@bytecodealliance/jco-std/wasi/0.2.x/http/adapters/hono/server';
```

**Build**:
```bash
jco guest-types wit/ -o generated/types
rollup -c                     # Bundle TS to JS
jco componentize -w wit/ -o dist/component.wasm dist/component.js
jco transpile dist/component.wasm -o dist/transpiled
```

**Demo** (`scripts/demo.mjs`):
```js
import { serve } from '@bytecodealliance/jco';

const server = await serve('./dist/transpiled/component.js', { port: 8080 });
const res = await fetch('http://localhost:8080/');
console.log(await res.text()); // "Hello World!"
await server.close();
```

## http-server-fetch-handler — Fetch Event Handler

HTTP server using standards-forward `fetch()` event:

```js
import { fire } from '@bytecodealliance/jco-std/wasi/0.2.x/http/adapters/fetch/server';

fire((request) => {
  return new Response('Hello from fetch!');
});

export { incomingHandler } from '@bytecodealliance/jco-std/wasi/0.2.x/http/adapters/fetch/server';
```

## ts-resource-export — Resource Export

Component exporting a resource that the host uses.

**WIT**:
```wit
package test:component@0.1.0;

interface resources {
    resource blob {
        constructor(init: list<u8>);
        write: func(bytes: list<u8>);
        read: func(n: u32) -> list<u8>;
    }
}

world exported {
    export resources;
}
```

**Host usage**:
```js
import { resources } from './dist/transpiled/component.js';

using blob = new resources.Blob(new Uint8Array([1, 2, 3]));
blob.write(new Uint8Array([4, 5]));
const data = blob.read(5);
// blob disposed automatically
```

## ts-resource-import — Resource Import

Component importing a resource defined by the host.

**WIT**:
```wit
package test:component@0.1.0;

interface resources {
    resource blob {
        constructor(init: list<u8>);
        write: func(bytes: list<u8>);
        read: func(n: u32) -> list<u8>;
    }
}

world imported {
    import resources;
    export use: interface {
        use: func(b: borrow<blob>) -> list<u8>;
    }
}
```

**Host implementation**:
```js
class Blob {
  constructor(init) { this.data = new Uint8Array(init); }
  write(bytes) { /* ... */ }
  read(n) { return this.data.slice(0, n); }
}

const imports = { resources: { blob: Blob } };
const component = await instantiate(loader, imports);
```

## string-reverse-upper — Import + Export

Component importing a `reverse` function and exporting a `reverse-upper` function:

```wit
interface string-reverse {
    reverse: func(s: string) -> string;
}

world component {
    import string-reverse;
    export reverse-upper: interface {
        reverse-upper: func(s: string) -> string;
    }
}
```

```js
import { reverse } from 'string-reverse/reverse';

export const 'reverse-upper' = {
  'reverse-upper'(s) {
    return reverse(s).toUpperCase();
  }
};
```

## node-compat — Node.js Built-in Usage

Component using Node.js built-ins (fs, path) inside WebAssembly:

```js
import { readFileSync } from 'node:fs';

export const run = {
  run() {
    const content = readFileSync('/etc/hostname', 'utf8');
    return content;
  }
};
```

> Node.js built-ins work inside componentize-js because StarlingMonkey provides them. They won't work in all Wasm runtimes.

## node-fetch — HTTP Requests

Component making HTTP requests using `fetch()`:

```js
export const run = {
  async run() {
    const res = await fetch('https://httpbin.org/get');
    const data = await res.json();
    return JSON.stringify(data);
  }
};
```

## jco-std HTTP Adapters

`@bytecodealliance/jco-std` provides framework adapters:

| Export | Description |
|---|---|
| `http/adapters/hono` | Hono framework integration |
| `http/adapters/express` | Express-like interface |
| `http/adapters/fetch` | Fetch event handler |

Use versioned exports: `@bytecodealliance/jco-std/wasi/0.2.6/http/adapters/hono/server` or `0.2.x` for latest.

# HTM 3.1.1 — Integrations

## htm/preact

Pre-built binding to Preact. Binds `htm` to Preact's `h` function and re-exports Preact's core API.

### Source

```js
import { h, Component, render } from 'preact';
import htm from 'htm';

const html = htm.bind(h);

export { h, html, render, Component };
```

### Usage

```js
import { html, render, h, Component } from 'htm/preact';

class App extends Component {
  render({ name }, { count = 0 }) {
    return html`
      <div>
        <h1>${name}</h1>
        <p>Count: ${count}</p>
        <button onClick=${() => this.setState({ count: count + 1 })}>Increment</button>
      </div>
    `;
  }
}

render(html`<${App} name="Counter" />`, document.body);
```

### Exports

| Export | Source | Description |
|---|---|---|
| `html` | `htm.bind(h)` | Tagged template function |
| `h` | `preact` | Preact's hyperscript function |
| `render` | `preact` | Preact's render function |
| `Component` | `preact` | Preact's Component class |

### TypeScript

```ts
import { h, VNode, Component } from 'preact';
import * as preactHooks from 'preact/hooks';
export * from 'preact/hooks';

declare function render(tree: VNode, parent: HTMLElement): void;
declare const html: (strings: TemplateStringsArray, ...values: any[]) => VNode;

export { h, html, render, Component };
```

Re-exports all Preact hooks from `preact/hooks`.

---

## htm/preact/standalone

Bundles Preact, Preact hooks, and HTM into a single file (~3.5 KB gzipped). No separate Preact dependency needed. Ideal for CDN imports and zero-config setups.

### Source

```js
import { h, Component, createContext, render } from 'preact';
import {
  useState, useReducer, useEffect, useLayoutEffect, useRef,
  useImperativeHandle, useMemo, useCallback, useContext,
  useDebugValue, useErrorBoundary
} from 'preact/hooks';
import htm from '../../index.mjs';

const html = htm.bind(h);

export {
  h, html, render, Component, createContext,
  useState, useReducer, useEffect, useLayoutEffect, useRef,
  useImperativeHandle, useMemo, useCallback, useContext,
  useDebugValue, useErrorBoundary
};
```

### Usage

```js
import {
  html, render, Component,
  useState, useEffect, useRef, useMemo, useCallback, useContext,
  createContext
} from 'htm/preact/standalone';

function Counter() {
  const [count, setCount] = useState(0);
  return html`
    <div>
      <p>Count: ${count}</p>
      <button onClick=${() => setCount(count + 1)}>Increment</button>
    </div>
  `;
}

render(html`<${Counter} />`, document.body);
```

### CDN import

```js
import { html, render } from 'https://unpkg.com/htm/preact/standalone.module.js';
```

### Exports

| Export | Source |
|---|---|
| `h` | Preact |
| `html` | `htm.bind(h)` |
| `render` | Preact |
| `Component` | Preact |
| `createContext` | Preact |
| `useState` | Preact hooks |
| `useReducer` | Preact hooks |
| `useEffect` | Preact hooks |
| `useLayoutEffect` | Preact hooks |
| `useRef` | Preact hooks |
| `useImperativeHandle` | Preact hooks |
| `useMemo` | Preact hooks |
| `useCallback` | Preact hooks |
| `useContext` | Preact hooks |
| `useDebugValue` | Preact hooks |
| `useErrorBoundary` | Preact hooks |

---

## htm/react

Pre-built binding to React. Only exports the `html` tag function — import React and ReactDOM separately.

### Source

```js
import { createElement } from 'react';
import htm from 'htm';
export const html = htm.bind(createElement);
```

### Usage

```js
import React from 'react';
import ReactDOM from 'react-dom';
import { html } from 'htm/react';

function App({ name }) {
  return html`<h1>Hello ${name}!</h1>`;
}

ReactDOM.render(html`<${App} name="World" />`, document.body);
```

### Exports

| Export | Source |
|---|---|
| `html` | `htm.bind(React.createElement)` |

### TypeScript

```ts
import * as React from 'react';
declare const html: (strings: TemplateStringsArray, ...values: any[]) => React.ReactElement;
```

### Key difference from htm/preact

`htm/react` does NOT re-export `render`, `Component`, hooks, or any other React API. Import those from `react` / `react-dom` directly:

```js
import { useState, useEffect } from 'react';
import { html } from 'htm/react';
```

---

## htm/mini

Smaller build with caching disabled. Uses `MINI = true` constant, which changes `build()` to return flat arrays `[tag, props, ...children]` instead of operation lists.

### Usage

```js
import htm from 'htm/mini';
const html = htm.bind(h);
```

### Trade-offs

- ~50 bytes smaller than default `htm` (~450 bytes gzipped)
- No template caching — each invocation re-parses the template
- No `CHILD_RECURSE` — nested elements call `h()` directly during `build()`
- No in-place optimization — no first-call overhead, but no subsequent speedup either
- No `evaluate()` function — `build()` drives `h()` calls directly

### When to use

- Memory-constrained environments where cache growth matters
- Templates that are used only once (no caching benefit)
- When you want the smallest possible footprint

---

## Custom hyperscript targets

HTM works with any function matching `h(type, props, ...children)`.

### vhtml — string HTML generation

```js
import htm from 'htm';
import vhtml from 'vhtml';

const html = htm.bind(vhtml);

html`<h1 id=hello>Hello world!</h1>`;
// '<h1 id="hello">Hello world!</h1>'
```

### jsxobj — object construction

```js
import htm from 'htm';
import jsxobj from 'jsxobj';

const cfg = htm.bind(jsxobj);

cfg`
  <webpack watch mode=production>
    <entry path="src/index.js" />
  </webpack>
`;
// { watch: true, mode: 'production', entry: { path: 'src/index.js' } }
```

### Direct DOM creation

```js
import htm from 'htm';

const html = htm.bind((type, props, ...children) => {
  const el = document.createElement(type);
  for (const [key, val] of Object.entries(props || {})) {
    if (key.startsWith('on')) {
      el.addEventListener(key.slice(2).toLowerCase(), val);
    } else {
      el.setAttribute(key, val);
    }
  }
  for (const child of children) {
    if (typeof child === 'string') {
      el.appendChild(document.createTextNode(child));
    } else if (child) {
      el.appendChild(child);
    }
  }
  return el;
});

document.body.appendChild(
  html`<button onclick=${() => alert('hi')}>Click</button>`
);
```

---

## CDN imports

All variants available via unpkg with ES module support:

```js
import htm from 'https://unpkg.com/htm?module';
import { html } from 'https://unpkg.com/htm/preact?module';
import { html, render } from 'https://unpkg.com/htm/preact/standalone.module.js';
import { html } from 'https://unpkg.com/htm/react?module';
import htm from 'https://unpkg.com/htm/mini?module';
```

---

## Package exports map

```json
{
  "exports": {
    ".": {
      "types": "./dist/htm.d.ts",
      "browser": "./dist/htm.module.js",
      "umd": "./dist/htm.umd.js",
      "import": "./dist/htm.mjs",
      "require": "./dist/htm.js"
    },
    "./preact": {
      "types": "./preact/index.d.ts",
      "browser": "./preact/index.module.js",
      "umd": "./preact/index.umd.js",
      "import": "./preact/index.mjs",
      "require": "./preact/index.js"
    },
    "./preact/standalone": {
      "types": "./preact/index.d.ts",
      "browser": "./preact/standalone.module.js",
      "umd": "./preact/standalone.umd.js",
      "import": "./preact/standalone.mjs",
      "require": "./preact/standalone.js"
    },
    "./react": {
      "types": "./react/index.d.ts",
      "browser": "./react/index.module.js",
      "umd": "./react/index.umd.js",
      "import": "./react/index.mjs",
      "require": "./react/index.js"
    },
    "./mini": {
      "types": "./mini/index.d.ts",
      "browser": "./mini/index.module.js",
      "umd": "./mini/index.umd.js",
      "import": "./mini/index.mjs",
      "require": "./mini/index.js"
    }
  }
}
```

Each entry supports `types`, `browser`, `umd`, `import`, and `require` conditions.

---

## TypeScript support

All variants ship `.d.ts` files:

```ts
// htm
declare const htm: {
  bind<HResult>(
    h: (type: any, props: Record<string, any>, ...children: any[]) => HResult
  ): (strings: TemplateStringsArray, ...values: any[]) => HResult | HResult[];
};
export default htm;

// htm/preact
import { h, VNode, Component } from 'preact';
export * from 'preact/hooks';
declare function render(tree: VNode, parent: HTMLElement): void;
declare const html: (strings: TemplateStringsArray, ...values: any[]) => VNode;
export { h, html, render, Component };

// htm/react
import * as React from 'react';
declare const html: (strings: TemplateStringsArray, ...values: any[]) => React.ReactElement;
```

The generic `bind<HResult>` preserves the return type of your `h()` function through to the tagged template.

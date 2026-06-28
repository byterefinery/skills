# htm Integrations

## htm/preact

Prebuilt binding for Preact with shared template cache:

```js
import { html, render, Component, h } from 'htm/preact';

const App = () => html`<h1>Hello</h1>`;
render(html`<${App} />`, document.body);
```

Exports: `h`, `html`, `render`, `Component`, and all hooks from `preact/hooks`.

## htm/preact/standalone

All-in-one import — includes Preact, hooks, and htm in a single module:

```js
import {
  html, render, Component, createContext,
  useState, useReducer, useEffect,
  useLayoutEffect, useRef, useImperativeHandle,
  useMemo, useCallback, useContext,
  useDebugValue, useErrorBoundary
} from 'htm/preact/standalone';
```

Useful for browser-based development without a build tool:

```html
<script type="module">
  import { html, Component, render } from
    'https://unpkg.com/htm/preact/standalone.module.js';
</script>
```

## htm/react

Prebuilt binding for React:

```js
import ReactDOM from 'react-dom';
import { html } from 'htm/react';

const App = () => html`<h1>Hello</h1>`;
ReactDOM.render(html`<${App} />`, document.body);
```

Exports: `html` (bound to `React.createElement`).

## Manual binding

For any hyperscript-compatible library:

```js
import htm from 'htm';

// Preact
import { h } from 'preact';
const html = htm.bind(h);

// React
import { createElement } from 'react';
const html = htm.bind(createElement);

// lit-html
import { html as litHtml } from 'lit-html';
const html = htm.bind(litHtml);

// vhtml (string output)
import vhtml from 'vhtml';
const html = htm.bind(vhtml);

// Custom
function h(type, props, ...children) {
  return { type, props, children };
}
const html = htm.bind(h);
```

## htm/mini

Smaller build (~450 bytes) with no caching:

```js
import htm from 'htm/mini';
const html = htm.bind(h);
```

Identical API to the main build. The only difference is no template caching.

## CDN usage

### unpkg

```js
// htm only
import htm from 'https://unpkg.com/htm?module';

// htm + Preact standalone
import { html, render } from 'https://unpkg.com/htm/preact/standalone.module.js';
```

### esm.sh

```js
import htm from 'https://esm.sh/htm';
import { html } from 'https://esm.sh/htm/preact';
import { html } from 'https://esm.sh/htm/react';
```

## Shared cache across modules

When using `htm/preact` or `htm/react`, the template cache is shared across all modules
that import from the same binding. This means:

```js
// module-a.js
import { html } from 'htm/preact';
export const div = html`<div>static</div>`;

// module-b.js
import { html } from 'htm/preact';
const div2 = html`<div>static</div>`;

div === div2;  // true — shared cache
```

With manual binding, each `htm.bind(h)` creates a separate cache even if bound to the same `h`.

## TypeScript

htm includes type definitions:

```ts
import htm from 'htm';
import type { VNode, h } from 'preact';

const html = htm.bind(h);
// html is typed as: (strings: TemplateStringsArray, ...values: any[]) => VNode | VNode[]
```

For `htm/preact` and `htm/react`, types are included in the integration packages.

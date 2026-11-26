# Integration

## Frameworks

`<regular-table>` is a standard custom element, so any framework that renders regular HTML works. The only integration work is reaching the DOM node to call `setDataListener()` and `draw()`.

### React

From `examples/react` — capture the element with a ref callback. regular-table is not particularly expensive to initialize, but it retains state between calls that makes later draws more performant, so it is worth preventing React from re-rendering it:

```javascript
import "regular-table";

async function setRegularTable(table) {
  table.setDataListener(dataListener);
  await document.fonts.load('12px "Open Sans"');
  await document.fonts.ready;
  table.draw();
}

const element = React.createElement("regular-table", { ref: setRegularTable });
ReactDOM.render(element, document.getElementById("root"));
```

The module augments the global `JSX.IntrinsicElements` with `"regular-table": RegularTableElement`, so JSX like `<regular-table ref={setRegularTable} />` type-checks without extra declarations.

## Installation

- **npm** (per the README): `npm add regular-table`, then `import "regular-table"` plus `import "regular-table/dist/css/material.css"` in your asset bundle.
- **CDN**: `<script type="module" src="https://cdn.jsdelivr.net/npm/regular-table"></script>` plus a `<link>` for `material.css`.

The module has no exports — importing it registers the custom element as a side effect, and the registration is guarded (it only defines the element if the tag is not already upgraded), so a second import of the same tag is a no-op rather than a `DuplicateCustomElement` error.

## Web Workers

The DataListener Promise contract makes a worker a first-class data source — the worker speaks the same `(x0, y0, x1, y1) → DataResponse` protocol (see [01-data-model](01-data-model.md)). The same works for any HTTP backend via `fetch()`.

## perspective

regular-table is natively compatible with [perspective](https://github.com/finos/perspective), a WebAssembly streaming visualization engine: using a `perspective.Table` as the virtual data model gives user-driven row/column pivots, filters, sorts, and column expressions — plus charts and persistent layouts — over high-frequency updating data (README). The README section has no code example yet (marked pending upstream), so treat concrete integration details as unverified — check the perspective docs or write a minimal `Table → DataResponse` adapter.

## Upstream Development

From the README Development section (repo uses pnpm workspaces):

```bash
pnpm install
pnpm run build    # esbuild → dist/esm/regular-table.js and dist/css/*.css
pnpm run test    # playwright suite
pnpm run start   # http-server; examples at http://localhost:8080/examples/
```

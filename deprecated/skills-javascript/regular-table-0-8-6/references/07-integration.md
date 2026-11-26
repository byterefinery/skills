# Integration

regular-table is a standard Web Component (Custom Element), making it framework-agnostic. It works with any library that supports custom elements.

## React

```javascript
import "regular-table";
import "regular-table/dist/css/material.css";
import { useCallback, useEffect, useRef } from "react";

function DataTable() {
  const tableRef = useRef(null);

  useEffect(() => {
    const table = tableRef.current;
    if (!table) return;

    table.setDataListener((x0, y0, x1, y1) => ({
      num_rows: 1000,
      num_columns: 10,
      data: getDataSlice(x0, y0, x1, y1),
    }));

    table.draw();
  }, []);

  return <regular-table ref={tableRef} style={{ width: "100%", height: "500px" }} />;
}
```

### React with Hooks

```javascript
function useRegularTable(dataListener) {
  const ref = useRef(null);

  useEffect(() => {
    const table = ref.current;
    if (!table) return;

    table.setDataListener(dataListener);
    table.draw();

    return () => {
      table.clear();
    };
  }, [dataListener]);

  return ref;
}

// Usage
function App() {
  const ref = useRegularTable(myDataListener);
  return <regular-table ref={ref} />;
}
```

## Vue

```javascript
import "regular-table";
import "regular-table/dist/css/material.css";

export default {
  mounted() {
    const table = this.$refs.table;
    table.setDataListener(this.dataListener);
    table.draw();
  },
  beforeUnmount() {
    this.$refs.table.clear();
  },
  methods: {
    dataListener(x0, y0, x1, y1) {
      return {
        num_rows: 1000,
        num_columns: 10,
        data: this.getDataSlice(x0, y0, x1, y1),
      };
    },
  },
};
```

```html
<template>
  <regular-table ref="table" style="width: 100%; height: 500px"></regular-table>
</template>
```

### Vue 3 Composition API

```javascript
import { onMounted, onBeforeUnmount, ref } from "vue";
import "regular-table";

export default {
  setup() {
    const tableRef = ref(null);

    onMounted(() => {
      tableRef.value.setDataListener(dataListener);
      tableRef.value.draw();
    });

    onBeforeUnmount(() => {
      tableRef.value.clear();
    });

    return { tableRef };
  },
};
```

## Svelte

```svelte
<script>
  import "regular-table";
  import "regular-table/dist/css/material.css";

  let table;

  function dataListener(x0, y0, x1, y1) {
    return {
      num_rows: 1000,
      num_columns: 10,
      data: getDataSlice(x0, y0, x1, y1),
    };
  }

  function init(node) {
    table = node;
    table.setDataListener(dataListener);
    table.draw();

    return {
      destroy() {
        table.clear();
      },
    };
  }
</script>

<regular-table
  bind:this={table}
  use:init
  style="width: 100%; height: 500px"
></regular-table>
```

## Perspective Integration

regular-table is designed to work with [Perspective](https://github.com/finos/perspective/):

```javascript
import "perspective";
import "regular-table";

const worker = perspective.worker();

async function init() {
  const table = await worker.table(DATA);
  const view = table.view();

  const regularTable = document.querySelector("regular-table");
  regularTable.setDataListener(async (x0, y0, x1, y1) => {
    const allData = await view.to_js();
    // Convert to columnar format for regular-table
    return {
      num_rows: allData.length,
      num_columns: Object.keys(allData[0]).length,
      data: /* columnar slice */,
    };
  });

  regularTable.draw();
}
```

## CDN Usage

```html
<script type="module" src="https://cdn.jsdelivr.net/npm/regular-table@0.8.6/dist/esm/regular-table.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/regular-table@0.8.6/dist/css/material.css" />

<regular-table id="my-table"></regular-table>

<script type="module">
  const table = document.getElementById("my-table");
  table.setDataListener((x0, y0, x1, y1) => ({
    num_rows: 1000,
    num_columns: 5,
    data: getDataSlice(x0, y0, x1, y1),
  }));
  table.draw();
</script>
```

## npm Usage

```bash
npm install regular-table
```

```javascript
import "regular-table";
import "regular-table/dist/css/material.css";
```

## Bundlers

### Vite

Works out of the box with ES module imports:

```javascript
// vite.config.js
export default {
  // no special config needed
};
```

### Webpack

```javascript
// webpack.config.js
module.exports = {
  module: {
    rules: [
      {
        test: /\.css$/,
        use: ["style-loader", "css-loader"],
      },
    ],
  },
};
```

### esbuild

```bash
esbuild entry.js --bundle --outfile=bundle.js
```

regular-table has no dependencies, so bundling is straightforward.

## TypeScript

regular-table ships with TypeScript declarations:

```typescript
import "regular-table";

declare global {
  interface HTMLElementTagNameMap {
    "regular-table": RegularTableElement;
  }
}

const table = document.querySelector<RegularTableElement>("regular-table");
table?.setDataListener((x0, y0, x1, y1) => ({
  num_rows: 1000,
  num_columns: 10,
  data: getDataSlice(x0, y0, x1, y1),
}));
```

The types are available at `regular-table/dist/esm/regular-table.d.ts`.

## Lit (Web Components)

```javascript
import { LitElement, html } from "lit";
import "regular-table";

class MyGrid extends LitElement {
  firstUpdated() {
    const table = this.shadowRoot.querySelector("regular-table");
    table.setDataListener(this.dataListener);
    table.draw();
  }

  render() {
    return html`<regular-table style="width: 100%; height: 500px;"></regular-table>`;
  }
}

customElements.define("my-grid", MyGrid);
```

## Gotchas

- **Custom element registration is global** — importing the module registers `<regular-table>` on `window.customElements`. Using two versions simultaneously causes a `DuplicateCustomElement` error.
- **Shadow DOM requires `regular-table` import** — when using regular-table inside another component's shadow DOM, import the module in the host component so the custom element is defined before use.
- **React re-renders** — prevent React from re-rendering the `<regular-table>` element unnecessarily. Use `useCallback` for refs and memoize the component.
- **Cleanup on unmount** — call `table.clear()` when the component unmounts to free resources.
- **No named exports** — the module only registers the custom element. There is no `import { RegularTable } from "regular-table"`.

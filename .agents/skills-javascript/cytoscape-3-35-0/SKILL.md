---
name: cytoscape-3-35-0
description: Graph theory (network) library for analysis and visualisation (v3.35.0, MIT, no external dependencies) with an interactive renderer, CSS-like stylesheet, selectors, built-in layouts, graph algorithms from BFS to PageRank, animations, and an extension system. Use when building Cytoscape.js graph apps, modelling relational data (nodes/edges), styling nodes and edges, running layouts or graph algorithms, tuning large-graph performance, or exporting graphs to PNG/JPG/JSON.
license: MIT
compatibility: Runs in all modern browsers and headless Node.js (engines node >=0.10); no external dependencies
metadata:
  tags:
    - javascript
    - graph
    - data-visualization
    - network-analysis
---

# cytoscape 3.35.0

## Overview

Cytoscape.js (v3.35.0, MIT) is a fully featured graph theory (a.k.a. network) library for analysis and visualisation, written in pure JS with no external dependencies. It contains a graph theory model plus an optional interactive renderer — use it for rich UIs in the browser or headlessly on Node.js.

- Directed, undirected, mixed, loops, multigraphs, and compound graphs
- Built-in gestures (pinch-to-zoom, box selection, panning, drag) on desktop and touch
- CSS-convention stylesheet separating presentation from data; CSS-like selectors for querying
- Built-in layouts for automatic node positioning; extendable via `cytoscape.use()`
- Graph theory algorithms, from BFS to PageRank
- Chainable API; collections are immutable (set-theory friendly)
- Fully serialisable via JSON (`cy.json()`); headless mode for server-side analysis
- Weekly patch / monthly feature release cadence

Website + docs: https://js.cytoscape.org · extensions: https://js.cytoscape.org/#extensions

## Usage

### Install and import

```bash
npm install cytoscape
```

```js
import cytoscape from 'cytoscape';   // default export — `import * as` will NOT work
// CommonJS: var cytoscape = require('cytoscape');
```

### Initialisation

```js
var cy = cytoscape({
  container: document.getElementById('cy'), // container to render in

  elements: [ // list of graph elements to start with
    { data: { id: 'a' } },
    { data: { id: 'b' } },
    { data: { id: 'ab', source: 'a', target: 'b' } }
  ],

  style: [ // the stylesheet for the graph
    {
      selector: 'node',
      style: {
        'background-color': '#666',
        'label': 'data(id)'
      }
    },
    {
      selector: 'edge',
      style: {
        'width': 3,
        'line-color': '#ccc',
        'target-arrow-color': '#ccc',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier'
      }
    }
  ],

  layout: { name: 'grid', rows: 1 }
});
```

For headless (Node.js) use, omit `container`; in the browser set `headless: true`.

### Elements JSON

Each element: `group` (`nodes`/`edges`, inferable), `data` (mandatory `id`; edges need `source`/`target`), optional `position` (`renderedPosition` for on-screen pixels), `scratch` (temp data; app fields prefixed `_`), `selected`, `selectable`, `locked`, `grabbable`, `pannable`, `classes`, and a per-element `style` override — which the docs say to avoid unless absolutely necessary (use the stylesheet).

### Core API (quick reference)

| area | methods |
| --- | --- |
| graph manipulation | `add`, `remove`, `collection`, `hasElementWithId`, `getElementById`, `elements`, `nodes`, `edges`, `filter`, `batch`/`startBatch`/`endBatch`, `mount`/`unmount`, `destroy` |
| viewport | `center`, `fit`, `reset`, `pan`, `panBy`, `zoom`, `minZoom`, `maxZoom`, `viewport`, `getFitViewport`, `extent`, `width`, `height`, `resize`, `forceRender`, `invalidateDimensions` |
| layout | `layout`, `makeLayout`, `createLayout` |
| export | `png`, `jpg`, `json` |
| events | `on`/`off`/`trigger` (+ `bind`/`unbind`/`emit` aliases), `promiseOn`, `one`, `ready` |

Functions return `this` by default, so they chain (`cy.nodes().filter(...)`). Built-in layouts: `breadthfirst`, `circle`, `concentric`, `cose`, `grid`, `null`, `preset`, `random` — more via layout extensions (fcose, dagre, cola, elk, klay, …). See [03-layouts-and-extensions](references/03-layouts-and-extensions.md).

### Selectors

CSS-like: `node`, `edge`, `*`, `.class`, `#id`, data tests `[foo]`, `[!foo]`, `[?foo]`, `[foo = 'bar']`, `[num > 2]`, comma joins (logical OR), dot-notation into nested data. String values need quotes; special characters in IDs need escaping (or use data selectors). See [02-styling-and-selectors](references/02-styling-and-selectors.md).

### Graph algorithms

On collections: `breadthFirstSearch`, `depthFirstSearch`, `aStar`, `bellmanFord`, `dijkstra`, `floydWarshall`, `pageRank`, `betweennessCentrality`, `closenessCentrality`, `degreeCentrality` (+ normalized variants), `affinityPropagation`. See [04-algorithms-and-performance](references/04-algorithms-and-performance.md).

## Gotchas

- **ESM must use the default export** — `import * as cytoscape from 'cytoscape'` does not work.
- **Place CSS before initialisation** — Cytoscape reads the container's DOM dimensions at init; stylesheets must be in `<head>` before any cytoscape code, or dimensions report incorrectly.
- **Collections are immutable** — operations return new collections. For very performance-intensive code use `eles.merge()` / `eles.unmerge()`; most apps never need them.
- **Model position vs rendered position** — `position` is in model coordinates (constant under zoom/pan); `renderedPosition` is viewport-relative pixels.
- **Last matching selector wins** — CSS specificity rules are completely ignored in stylesheets.
- **String-format stylesheets require trailing semicolons** on every property except the last — parsing fails without them.
- **Per-element `style` fields are discouraged** — the elements JSON explicitly says to use the stylesheet instead.
- **Function style values are expensive and non-serialisable** — the function should only read `ele.data()`/`scratch()`/`cy.data()`/`cy.scratch()`, never other style values, and should not mutate state. Prefer `'data(field)'` mapping when possible.
- **Scratch field names** — prefix your app fields with `_` in `scratch` (unprefixed names are for extensions).
- **Performance for large graphs** — `cy.getElementById()` beats selector lookups; batch modifications with `cy.batch()`; labels, dotted/dashed edges, arrows, and bezier curves are the expensive styles; `pixelRatio: 1`, `hideEdgesOnViewport`, `textureOnViewport`, and `motionBlur` init options help on very large graphs. Full list in [04-algorithms-and-performance](references/04-algorithms-and-performance.md).
- **Objects passed to Cytoscape are owned by it** — `cy.add()`/init do not deep-copy your element objects; copy manually before passing if you mutate them later.
- **Recycle large instances** — `cy.destroy()` is fine, but recycling large instances keeps memory lower (canvas-heavy).

## References

- [01-elements-and-data](references/01-elements-and-data.md) — elements JSON, data/scratch, positions, compound nodes, collection operations
- [02-styling-and-selectors](references/02-styling-and-selectors.md) — stylesheet formats, selectors, function values
- [03-layouts-and-extensions](references/03-layouts-and-extensions.md) — built-in layouts, `cytoscape.use()`, extension ecosystem
- [04-algorithms-and-performance](references/04-algorithms-and-performance.md) — graph algorithms and the performance tuning checklist

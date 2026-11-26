---
name: cytoscape-3-34-0
description: Cytoscape.js 3.34.0 — graph theory library for analysis and visualisation. Covers Core instance lifecycle, Collection API (traversing, filtering, set operations, data/scratch), CSS-like selectors, stylesheet styling (nodes, edges, labels, gradients, overlays), built-in layouts (grid, circle, cose, concentric, breadthfirst, random, preset, null), graph algorithms (Dijkstra, A*, BFS/DFS, PageRank, centrality, MST, clustering, min-cut), viewport control, events, animations, JSON serialization, PNG/JPG export, compound nodes, and extension registration. Use when building interactive graph visualisations, performing graph analysis, working with network data, or integrating graph theory algorithms.
metadata:
  tags:
    - javascript
    - graph
    - visualization
    - network
    - algorithms
---

# cytoscape 3.34.0

Cytoscape.js is a fully featured graph theory library written in pure JavaScript. It supports directed/undirected/mixed graphs, multigraphs, loops, and compound (hierarchical) graphs. It runs in browsers and Node.js (headless mode).

## Overview

- **Package**: `cytoscape@3.34.0`
- **License**: MIT
- **No external dependencies**
- **Module formats**: ESM, CJS, UMD, AMD
- **Browser support**: ES5+ with canvas; modern browsers fully supported
- **Headless**: runs on Node.js for graph analysis without rendering

### Entry Points

| Import | Description |
|---|---|
| `cytoscape` (npm default) | Auto-resolves ESM or CJS |
| `cytoscape/dist/cytoscape.esm.mjs` | ESM bundle |
| `cytoscape/dist/cytoscape.cjs.js` | CommonJS bundle |
| `cytoscape/dist/cytoscape.min.js` | Minified UMD (CDN) |

### Quick Start

```js
import cytoscape from 'cytoscape';

const cy = cytoscape({
  container: document.getElementById('cy'), // or omit for headless

  elements: [
    { data: { id: 'a', label: 'Node A' } },
    { data: { id: 'b', label: 'Node B' } },
    { data: { id: 'ab', source: 'a', target: 'b' } }
  ],

  style: [
    {
      selector: 'node',
      style: {
        'background-color': '#666',
        'label': 'data(label)',
        'width': 40,
        'height': 40
      }
    },
    {
      selector: 'edge',
      style: {
        'width': 2,
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

### Core Architecture

Cytoscape.js follows a three-tier architecture:

1. **Core (`cy`)** — the graph instance. Manages elements, viewport, style, layout, events, rendering
2. **Collection (`eles`)** — immutable set of elements. Supports traversing, filtering, set theory, graph algorithms
3. **Element (`ele`)** — individual node or edge. Shares the same API surface as collections

Element types use shorthand notation in docs: `cy`, `eles`, `ele`, `nodes`, `node`, `edges`, `edge`, `layout`, `ani`.

### Key Design Principles

- **Chaining**: most methods return `this` for fluent API
- **Immutable collections**: traversal/filter returns new collections
- **Model vs rendered coordinates**: positions are in model space; rendered positions depend on zoom/pan
- **Stylesheet separates data from presentation**: use `style:[]` at init, not per-element `style` fields
- **Extension system**: layouts, renderers, and APIs are pluggable via `cytoscape.use()`

### Headless Mode

```js
// Node.js — no container, no rendering
import cytoscape from 'cytoscape';

const cy = cytoscape({
  elements: [
    { data: { id: 'a' } },
    { data: { id: 'b' } },
    { data: { id: 'ab', source: 'a', target: 'b' } }
  ]
});

// Run algorithms headlessly
const result = cy.elements().dijkstra({ root: '#a', weight: function(){ return 1; } });
```

## Usage

### Initialisation Options

```js
const cy = cytoscape({
  container: document.getElementById('cy'),
  headless: false,           // true for explicit headless in browser
  elements: [],              // initial elements (array or { nodes, edges })
  style: [],                 // initial stylesheet
  layout: { name: 'grid' },  // initial layout

  // Viewport
  zoom: 1,
  minZoom: 0.5,
  maxZoom: 3,
  pan: { x: 0, y: 0 },
  zoomingEnabled: true,
  userZoomingEnabled: true,
  panningEnabled: true,
  userPanningEnabled: true,
  boxSelectionEnabled: true,

  // Interaction
  autolock: false,           // lock all nodes from being moved
  autoungrabify: false,      // make all nodes ungrabbable
  autounselectify: false,    // make all elements unselectable
  selectionType: 'single',   // 'single' or 'additive' (shift-click to multi-select)
  multiClickDebounceTime: 250,

  // Rendering
  renderer: { name: 'canvas' }, // 'canvas' (default), 'null' (headless)
  styleEnabled: true,
  wheelSensitivity: 1,       // zoom sensitivity multiplier
  motionBlur: 0.75,         // motion blur amount during viewport gestures
  textureOnViewport: false,  // use texture caching during viewport gestures
  hideEdgesOnViewport: false // hide edges during viewport gestures
});
```

### Adding and Removing Elements

```js
// Add single element
cy.add({ data: { id: 'x' } });

// Add multiple (nodes first, then edges)
cy.add([
  { data: { id: 'a' } },
  { data: { id: 'b' } },
  { data: { id: 'ab', source: 'a', target: 'b' } }
]);

// Remove elements
cy.remove({ group: 'nodes', data: { id: 'a' } });

// Query and remove
cy.$('#a').remove();

// Temporary removal (not from pool)
const removed = ele.remove(true, false);
removed.restore(); // put back
```

### Querying Elements

```js
// By ID
cy.getElementById('a');
cy.$id('a');

// By selector
cy.nodes();                    // all nodes
cy.edges();                    // all edges
cy.elements();                 // all elements
cy.$('node#foo');              // node with id 'foo'
cy.$('.highlight');            // elements with class 'highlight'
cy.$('[weight > 50]');         // elements with weight > 50
cy.$(':selected');             // selected elements
cy.$(':visible');              // visible elements

// Check existence
cy.hasElementWithId('a');
```

### Element Data

```js
// Get/set data (immutable keys: id, source, target, parent)
ele.data('name', 'Alice');
ele.data('name'); // 'Alice'
ele.data({ name: 'Alice', age: 30 });

// Scratchpad (mutable, non-serialised)
ele.scratch('temp', 42);
ele.scratch('temp');

// Internal scratchpad (for extensions, no events)
ele.rscratch('key', value);
```

### JSON Serialisation

```js
// Full serialisation
const json = cy.json();
// { elements: { nodes: [...], edges: [...] }, style: [...], zoom, pan, ... }

// Flat elements array
const flatJson = cy.json(true);
// { elements: [{ group: 'nodes', data: {...} }, ...], ... }

// Deserialise
cy.json(json);

// Single element
const eleJson = ele.json();
ele.json({ data: { name: 'new' }, position: { x: 100, y: 100 } });
```

### Export Images

```js
// PNG
const pngUri = cy.png({
  fullscreen: false,    // 1x or fullscreen
  bg: '#fff',           // background colour
  output: 'blob',       // 'base64', 'base64uri', 'binary', 'binaryblob', 'blob', 'dataUri'
  scale: 1,             // multiplier
  padding: 30           // padding around bounding box
});

// JPG
const jpgUri = cy.jpg({ fullscreen: false, bg: '#fff' });
```

## Gotchas

- **`data()` keys `id`, `source`, `target`, `parent` are immutable** — use `ele.move()` to change parent/source/target. Never try `ele.data('id', 'new')`.
- **Container must have dimensions before init** — CSS for the container div must be loaded before `cytoscape()` is called, or layouts and rendering will use incorrect dimensions.
- **Model vs rendered coordinates** — `ele.position()` returns model coordinates. Use `ele.renderedPosition()` for screen pixel positions. Style values (width, height) are always in model coordinates.
- **`display: none` hides connected edges** — hiding a node also hides its edges. Use `visibility: hidden` if you want edges to remain visible.
- **`opacity: 0` keeps elements interactive** — invisible elements still receive events. Use `events: no` to disable interaction.
- **Collection immutability** — `eles.filter()`, `eles.neighborhood()`, etc. return new collections. The original is unchanged.
- **Stylesheet last-match wins** — specificity rules are ignored. The last matching selector for a property wins. Order matters.
- **`haystack` edges don't support loops or arrows** — use `straight`, `bezier`, or other curve styles for those features.
- **Layout runs asynchronously for force-directed** — `cose` layout emits `layoutstart`, `layoutready`, `layoutstop`. Use events or `layout.promiseOn()` for async coordination.
- **`cy.json()` serialises style as JSON array** — function-based style values cannot be serialised. Use `data()` or `mapData()` mappers instead.
- **Edge `source`/`target` must reference existing nodes** — edges cannot be created before their endpoint nodes exist.
- **Compound node dimensions are inferred** — parent nodes have no independent position/size; they are computed from children.

## References

- [01-notation](references/01-notation.md) — Elements JSON format, compound nodes, position model, gestures
- [02-core-api](references/02-core-api.md) — Core instance methods: viewport, lifecycle, batch, style, layout, search
- [03-collections](references/03-collections.md) — Collection API: traversing, filtering, set operations, group, iteration
- [04-selectors](references/04-selectors.md) — CSS-like selector syntax, data queries, state pseudo-classes
- [05-stylesheet](references/05-stylesheet.md) — Styling nodes, edges, labels, gradients, overlays, transitions, core styles
- [06-layouts](references/06-layouts.md) — Built-in layouts (grid, circle, cose, concentric, breadthfirst, random, preset, null), layout extension API
- [07-events](references/07-events.md) — Event system: user input, collection events, graph events, bubbling
- [08-algorithms](references/08-algorithms.md) — Graph algorithms: shortest path, centrality, clustering, MST, min-cut, connectivity
- [09-animation](references/09-animation.md) — Element and viewport animation, easing functions, queues
- [10-extensions](references/10-extensions.md) — Extension registration, layout prototype, ecosystem (layouts, UI, API)

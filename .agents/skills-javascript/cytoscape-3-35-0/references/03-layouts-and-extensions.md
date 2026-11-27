# Layouts and extensions

## Layouts

A layout positions nodes automatically. Create one with `cy.makeLayout(options)` (analogous `eles.makeLayout()` exists for a subset of the graph) and run it with `layout.run()`; `layout: {...}` in the init options runs it on the initial elements.

Built-in layouts (shipped with the core): `breadthfirst`, `circle`, `concentric`, `cose`, `grid`, `null`, `preset`, `random`.

### Common options

All layouts share these common options:

```js
{
  animate: true,            // true (continuous), 'end' (animate result), false
  animationDuration: 500,   // duration for animate:'end'
  animationEasing: undefined,
  animateFilter: (node, i) => true,
  animationThreshold: 250,  // ms before animating (prevents flashing)
  fit: true,                // fit viewport after layout
  padding: 30,              // padding on fit
  boundingBox: undefined,   // { x1, y1, x2, y2 } or { x1, y1, w, h }
  ready: () => {},          // called on layoutready
  stop: () => {}            // called on layoutstop
}
```

### Running layouts

```js
// On all elements
cy.layout({ name: 'grid', rows: 1 }).run();

// On specific elements
cy.$('#a, #b').layout({ name: 'circle', radius: 100 }).run();

// Stop a running layout
cy.layout().stop();

// Chain with events
cy.layout({ name: 'cose' })
  .on('layoutready', () => console.log('initial positions set'))
  .on('layoutstop', () => console.log('layout complete'))
  .run();
```

### Built-in layout options

```js
// grid — rows, columns (auto if omitted), avoidOverlap: true, positioning(node)

// circle — startAngle: 0 (radians), sweep: -2π, spacing: 10,
//          clockwise: true, positioning(node)

// concentric — equidistant: false, minNodeSpacing: 10,
//              concentric(node) => node.degree() (ring assignment), levelWidth()

// cose — force-directed with compound support:
// refresh: 20, randomize: false, componentSpacing: 40,
// nodeRepulsion(node) => 2048, nodeOverlap: 4,
// idealEdgeLength(edge) => 32, edgeElasticity(edge) => 32,
// nestingFactor: 1.2, gravity: 1, numIter: 1000,
// initialTemp: 1000, coolingFactor: 0.99, minTemp: 1.0

// breadthfirst — directed: true, spacingFactor: 1, circle: false,
//                tiers(node), maxWidthMerging: false, sort(a, b), position(node, coords)

// random — seed (for reproducibility)

// preset — positions(node) => node.position() (or custom position map)

// null — does nothing (headless / manual positions)
```

### Layout events

```js
layout.on('layoutstart', (e) => { /* layout started */ });
layout.on('layoutready', (e) => { /* initial positions set */ });
layout.on('layoutstop', (e) => { /* layout finished */ });

// Promise-based
layout.promiseOn('layoutstop').then(() => { console.log('layout done'); });
```

### Writing a custom layout

Layouts are extensions — anyone can write one without modifying the library:

```js
function MyLayout(options) {
  this.options = { ...defaults, ...options };
}

MyLayout.prototype.run = function() {
  const options = this.options;
  const eles = options.eles;
  const nodes = eles.nodes();

  // Calculate positions
  // ...

  // Set positions
  eles.layoutPositions((ele, i, position) => {
    return position; // return { x, y }
  });

  return this; // chaining
};

// Register
cytoscape('layout', 'mylayout', MyLayout);

// Use
cy.layout({ name: 'mylayout' }).run();
```

For continuous (force-directed) layouts, use `requestAnimationFrame` or Web Workers and call `nodes.positions()` each visible iteration.

### Headless layouts

In headless mode, specify `boundingBox` since there is no container to infer bounds:

```js
cy.layout({
  name: 'cose',
  boundingBox: { x1: 0, y1: 0, x2: 1000, y2: 1000 }
}).run();
```

Layout extensions add more (installed separately, registered with `cytoscape.use()`). Highlights from the curated list:

| extension | notes |
| --- | --- |
| `fcose` | faster CoSE-Bilkent; compound + non-compound; supports fixed/alignment/relative placement constraints. Docs: "If you want to use a force-directed layout, fCoSE should be the first layout you try." |
| `cose-bilkent` | near-perfect end results; more expensive than `cose` and `fcose` |
| `cosep` | force-directed with port constraints on compound graphs |
| `cola` | beautiful, smoothly animated results for relatively small graphs |
| `dagre` | DAGs and trees; hierarchical organisation |
| `elk` | adapter for the ELK layout algorithm family |
| `euler` | fast, small file size, high quality; good for non-compound graphs |
| `klay` | works well for most graph types; strong on DAGs and compound graphs |
| `avsdf` | organises nodes in a circle, minimises edge crossings |
| `cise` | circular clusters with a force-directed layout |
| `d3-force`, `springy`, `ngraph.forcelayout` | other force-directed options |
| `tidytree` | non-layered layout specifically for trees |
| `spread` | tries to use all the viewport space |
| `even-parent`, `cosmos-over-cytoscape` | compound-node and GPU-parallel layouts |

## Extensions

Register any extension on the `cytoscape` namespace:

```js
import ext from 'cy-ext';

cytoscape.use(ext);
```

Extension categories (from the curated list):

- **UI** — `context-menus`, `cxtmenu`, `edgehandles`, `expand-collapse`, `grid-guide`, `html`/`node-html-label`, `navigator`, `panzoom`, `toolbar`, `lasso`, `dom-node`, `html`, `overlays`, `popper` (Tippy.js tooltips), `mapbox-gl`/`leaflet` map backends, and more.
- **Layout** — see the table above.
- **API** — `clipboard`, `dblclick`, `graphml` (import/export), `pdf-export`, `undo-redo`, `view-utilities`, `all-paths`, `layout-utilities`.
- **Utility packages** — `cytosnap` (server-side graph images on Node.js via Puppeteer), `Cytoscape.js Schema` (JSON Schema for the JSON graph format), `RCyjs` (R), `Cyjs.NET` (F#).

First-party extensions are maintained by groups associated with the Cytoscape Consortium; third-party by outside developers.

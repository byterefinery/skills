# Layouts

Layouts set node positions. They are extensions — anyone can write a layout without modifying the library. Built-in layouts and popular extensions are covered here.

## Common Options

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

## Running Layouts

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

## Built-in Layouts

### Grid

Positions nodes in a grid pattern.

```js
{
  name: 'grid',
  rows: undefined,          // number of rows (auto if omitted)
  columns: undefined,       // number of columns (auto if omitted)
  avoidOverlap: true,       // avoid node overlap
  positioning: (node) => {}, // custom positioning function
  fit: true,
  padding: 30,
  boundingBox: undefined,
  animate: false,
  animationDuration: 500,
  ready: () => {},
  stop: () => {}
}
```

### Circle

Positions nodes on a circle.

```js
{
  name: 'circle',
  padding: 30,
  startAngle: 0,            // radians, position of first node
  sweep: -2 * Math.PI,      // radians, clockwise negative
  spacing: 10,              // extra spacing between nodes
  clockwise: true,
  positioning: (node) => {}, // custom positioning
  fit: true,
  boundingBox: undefined,
  animate: false,
  ready: () => {},
  stop: () => {}
}
```

### Concentric

Positions nodes in concentric rings based on degree.

```js
{
  name: 'concentric',
  padding: 30,
  startAngle: 0,
  sweep: -2 * Math.PI,
  clockwise: true,
  equidistant: false,       // equal spacing between rings
  minNodeSpacing: 10,
  concentric: (node) => node.degree(), // ring assignment
  levelWidth: () => Infinity,
  animate: false,
  fit: true,
  boundingBox: undefined,
  ready: () => {},
  stop: () => {}
}
```

### CoSE (Compound Spring Embedder)

Force-directed layout with compound node support.

```js
{
  name: 'cose',
  ready: () => {},
  stop: () => {},
  animate: true,
  animationDuration: undefined,
  animationEasing: undefined,
  animateFilter: (node, i) => true,
  animationThreshold: 250,
  refresh: 20,              // iterations between position updates
  fit: true,
  padding: 30,
  boundingBox: undefined,
  nodeDimensionsIncludeLabels: false,
  randomize: false,         // use existing positions if false
  componentSpacing: 40,
  nodeRepulsion: (node) => 2048,
  nodeOverlap: 4,
  idealEdgeLength: (edge) => 32,
  edgeElasticity: (edge) => 32,
  nestingFactor: 1.2,
  gravity: 1,
  numIter: 1000,
  initialTemp: 1000,
  coolingFactor: 0.99,
  minTemp: 1.0
}
```

### Breadthfirst

Hierarchical layered layout (DAG-friendly).

```js
{
  name: 'breadthfirst',
  directed: true,           // true = respect edge directions
  padding: 30,
  spacingFactor: 1,
  circle: false,            // circular layout per layer
  tiers: (node) => {},      // custom tier assignment
  maxWidthMerging: false,
  sort: (a, b) => {},       // sort within layers
  position: (node, coords) => {},
  animate: false,
  fit: true,
  boundingBox: undefined,
  ready: () => {},
  stop: () => {}
}
```

### Random

```js
{
  name: 'random',
  seed: undefined,          // fixed seed for reproducibility
  boundingBox: undefined,
  fit: true,
  padding: 30,
  animate: false,
  ready: () => {},
  stop: () => {}
}
```

### Preset

Uses existing node positions.

```js
{
  name: 'preset',
  positions: (node) => node.position(), // or custom position map
  fit: true,
  padding: 30,
  boundingBox: undefined,
  animate: false,
  ready: () => {},
  stop: () => {}
}
```

### Null

Does nothing. Used for headless mode or when you set positions manually.

```js
{ name: 'null' }
```

## Layout Events

```js
layout.on('layoutstart', (e) => {
  // Layout started
});

layout.on('layoutready', (e) => {
  // Initial positions set
  // For CoSE: simulation running but initial positions are set
});

layout.on('layoutstop', (e) => {
  // Layout finished
});

// Promise-based
layout.promiseOn('layoutstop').then(() => {
  console.log('layout done');
});
```

## Layout Extension API

To write a custom layout:

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

## Popular Layout Extensions

| Extension | Description |
|---|---|
| `cytoscape-cola` | Cola.js physics simulation, great aesthetics for small graphs |
| `cytoscape-fcose` | Fast CoSE — top-tier results with high performance |
| `cytoscape-cose-bilkent` | Enhanced CoSE with near-perfect results |
| `cytoscape-dagre` | DAG/tree hierarchical layout |
| `cytoscape-euler` | Fast, small, high-quality force-directed |
| `cytoscape-klay` | General-purpose, handles DAGs and compounds |
| `cytoscape-elk` | ELK layout adapter, multiple algorithms |
| `cytoscape-spread` | Uses all viewport space |
| `cytoscape-avsdf` | Circular layout minimising edge crossings |
| `cytoscape-cise` | Circular clusters with physics simulation |

Install and register:

```js
import cytoscape from 'cytoscape';
import fcose from 'cytoscape-fcose';

cytoscape.use(fcose);

cy.layout({ name: 'fcose' }).run();
```

## Headless Layouts

In headless mode, specify `boundingBox` since there is no container to infer bounds:

```js
cy.layout({
  name: 'cose',
  boundingBox: { x1: 0, y1: 0, x2: 1000, y2: 1000 }
}).run();
```

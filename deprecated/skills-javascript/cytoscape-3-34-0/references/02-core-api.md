# Core API

## Lifecycle

```js
// Check state
cy.isReady();       // true if initialisation complete
cy.destroyed();     // true if destroy() was called
cy.headless();      // true if no container (headless mode)
cy.hasCompoundNodes(); // true if graph has compound nodes

// Destroy
cy.destroy(); // frees all resources, emits 'destroy'

// Mount/unmount (switch between headless and rendered)
cy.mount(containerElement);  // attach to DOM element
cy.unmount();                 // detach (switches to null renderer)
```

## Container and Size

```js
cy.container();    // DOM element or null
cy.window();       // window object of the container
cy.width();        // usable width in px
cy.height();       // usable height in px
cy.size();         // { width, height }
cy.invalidateSize(); // force size recalculation
```

## Elements

```js
// Access
cy.elements();              // all elements
cy.nodes();                 // all nodes
cy.edges();                 // all edges
cy.mutableElements();       // internal mutable collection

// Query
cy.getElementById('a');     // by ID → collection
cy.$id('a');                // alias
cy.hasElementWithId('a');   // boolean

// Selector query
cy.$('node#foo');           // by selector
cy.elements('node');        // all matching elements

// Add/remove
cy.add({ data: { id: 'a' } });
cy.add([nodeJson, edgeJson]);
cy.remove({ group: 'nodes', data: { id: 'a' } });

// Pool management (advanced)
cy.addToPool(eles);     // add to internal pool without rendering
cy.removeFromPool(eles); // remove from pool without rendering
```

## Viewport

### Pan

```js
cy.pan();               // { x: 0, y: 0 }
cy.pan('x');            // 0
cy.pan({ x: 100, y: 50 });
cy.pan('x', 100);

cy.panBy({ x: 50, y: 25 });  // relative pan
cy.panBy('x', 50);
```

### Zoom

```js
cy.zoom();              // current zoom level
cy.zoom(2);             // set zoom
cy.zoom({               // zoom about a point
  level: 2,
  position: { x: 100, y: 100 }       // model position
  // or
  renderedPosition: { x: 200, y: 150 } // rendered position
});

cy.zoomRange({ min: 0.5, max: 5 });
cy.minZoom(); cy.minZoom(0.5);
cy.maxZoom(); cy.maxZoom(5);
```

### Composite Viewport

```js
cy.viewport({ zoom: 2, pan: { x: 100, y: 50 } });
cy.reset(); // zoom to 1, pan to { x: 0, y: 0 }
```

### Fit and Center

```js
// Fit viewport to elements
cy.fit();                              // fit to all elements
cy.fit(selector, padding);             // fit to selector
cy.fit(eles, 30);                      // fit to collection with padding
cy.fit({ x1: 0, y1: 0, x2: 500, y2: 500 }); // fit to bounding box

// Get fit viewport state without applying
cy.getFitViewport(eles, padding);      // { zoom, pan } or undefined

// Center on elements
cy.center();                           // center on all
cy.center(selector);                   // center on selector
cy.center(eles);                       // center on collection
cy.getCenterPan(eles);                 // get pan without applying
```

### Extent

```js
cy.extent();          // visible area in model coordinates
cy.renderedExtent();  // visible area in rendered coordinates
// Both return { x1, y1, x2, y2, w, h }
```

## Batch Operations

Wrap multiple operations to batch style updates and rendering:

```js
cy.batch(() => {
  cy.add([/* ... */]);
  cy.remove([/* ... */]);
  // style updates, position changes, etc.
});
// Single render/style update after batch completes

// Manual batch
cy.startBatch();
// ... operations ...
cy.endBatch();
```

## Notifications

Disable rendering notifications during bulk operations:

```js
cy.notifications(false);
// ... many operations ...
cy.notifications(true);
```

## Style

```js
// Get stylesheet
cy.style();                    // Style object
cy.style().selectors();        // array of selector strings
cy.style().length;             // number of selector blocks

// Update stylesheet
cy.style([
  { selector: 'node', style: { 'background-color': 'red' } }
]);

// Append to existing
cy.style().append([
  { selector: '.highlight', style: { 'overlay-color': 'yellow' } }
]);

// Remove selectors
cy.style().remove('node');

// Serialise
cy.style().json();     // JSON array
cy.style().toString(); // CSS-like string

// Query element style
cy.style().get(ele, 'background-color');
```

## Layout

```js
// Run layout on all elements
cy.layout({ name: 'grid', rows: 1 }).run();

// Run layout on specific elements
cy.$('#a, #b').layout({ name: 'circle', radius: 100 }).run();

// Layout options
cy.layout({
  name: 'cose',
  animate: true,        // 'end', true, false
  fit: true,            // fit viewport after
  padding: 30,
  boundingBox: { x1: 0, y1: 0, x2: 500, y2: 500 },
  ready: function(){},  // called on layoutready
  stop: function(){}    // called on layoutstop
}).run();

// Stop layout
cy.layout().stop();
```

## Search

```js
// Find elements by rendered position
cy.elementAndEdgesPointRendered({ x: 100, y: 100 });
cy.elementPointRendered({ x: 100, y: 100 });
cy.edgesPointRendered({ x: 100, y: 100 });
cy.nodesPointRendered({ x: 100, y: 100 });
```

## Export

```js
// PNG
cy.png({
  fullscreen: false,     // false = bounding box, true = 1x viewport
  bg: '#ffffff',
  output: 'base64uri',   // 'base64', 'base64uri', 'binary', 'binaryblob', 'blob', 'dataUri'
  scale: 1,
  padding: 30
});

// JPG
cy.jpg({ fullscreen: false, bg: '#fff', output: 'blob' });
```

## Data and Scratch

```js
// Core data
cy.data();                // { ... }
cy.data('key', value);
cy.data('key');           // get

// Core scratchpad
cy.scratch();
cy.scratch('key', value);
cy.scratch('key');
```

## Options

```js
cy.options(); // returns copy of initialisation options
```

## Resize

```js
cy.resize(); // recalculate viewport dimensions (call when container size changes)
```

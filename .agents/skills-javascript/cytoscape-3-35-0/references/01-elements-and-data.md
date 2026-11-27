# Elements and data

## Elements JSON

Elements are described as JSON objects. Full shape from the docs:

```js
{
  group: 'nodes',      // 'nodes' or 'edges' — inferable, but explicit gives better debug messages
  data: {
    id: 'n1',          // mandatory string id (assigned automatically if undefined)
    parent: 'nparent', // compound node parent id; not defined => no parent
    // ...any other JSON-serialisable data
  },
  scratch: {
    _foo: 'bar'        // app fields prefixed with underscore; unprefixed names are for extensions
  },
  position: { x: 100, y: 100 },        // model position (optional on init, mandatory after)
  // or: renderedPosition: { x: 200, y: 200 }  // on-screen pixels instead
  selected: false,      // selection state (default false)
  selectable: true,     // selection state mutable (default true)
  locked: false,        // locked => node position immutable (default false)
  grabbable: true,      // user can drag the node
  pannable: false,      // dragging the node pans the viewport instead
  classes: ['foo', 'bar'], // array (or space-separated string) of class names
  // DO NOT USE the `style` FIELD UNLESS ABSOLUTELY NECESSARY — USE THE STYLESHEET INSTEAD
  style: { 'background-color': 'red' } // style property overrides
}
```

Edges are inferred from `data.source` / `data.target` (node ids). `source`/`target` and `parent` can be changed effectively with `eles.move()`.

## Positions

- **Model position** — stored in the model; constant under zoom/pan. Numeric style values are in model coordinates (width 20px is 20px at zoom 1). "Position" in the docs means model position unless stated otherwise.
- **Rendered position** — on-screen pixels relative to the viewport top-left. Model and rendered positions are equal at zoom 1, pan (0, 0). Panning is always measured in rendered coordinates.

Positions can be set manually or by a layout. Because two nodes' positions determine the edges between them, a layout effectively sets edge lengths too.

## Data

- Element data is JSON-serialisable dev data — read/write via `ele.data()` / `ele.data(field, value)`.
- `scratch` is for temp or non-serialisable data; app fields use the `_` prefix by convention.
- Data can be nested objects/arrays; selectors can reach into them with dot-notation (`node[name.first = "Jerry"]`, `node[labels.0 = "Person"]`).

## Compound nodes

Nodes can have a `parent` (by id), forming compound (hierarchical) graphs. Compound nodes make style calculation and rendering more expensive — don't use them if you don't need them.

```js
node.parent();            // direct parent
node.parents();           // all ancestors
node.children();          // direct children
node.descendants();       // all descendant nodes
node.leaves();            // descendant leaf nodes
node.commonAncestors(otherNode); // shared ancestors

node.isParent();          // has children
node.isChildless();       // no children
node.isChild();           // has a parent
node.isOrphan();          // no parent
```

Moving children: `child.move({ parent: 'newParent' })` or `child.move({ parent: null })` — `parent` is immutable via `data()`.

## Gestures

Cytoscape.js supports unified touch and mouse gestures:

| Gesture | Touch | Desktop |
|---|---|---|
| Pan background | drag | drag |
| Zoom | pinch | scroll wheel / pinch trackpad |
| Select element | tap | click |
| Unselect | taphold background | click background |
| Multi-select | — | modifier + tap |
| Box selection | three-finger swipe | modifier + drag |
| Drag nodes | drag | drag |

Gestures can be toggled:

```js
cy.zoomingEnabled(false);
cy.userZoomingEnabled(false);
cy.panningEnabled(false);
cy.userPanningEnabled(false);
cy.boxSelectionEnabled(false);
```

## Collections

Core accessors return collections: `cy.elements()`, `cy.nodes()`, `cy.edges()`, `cy.filter(selector)`, `cy.$(selector)`, `cy.$id(id)`, `cy.getElementById(id)`.

Key behaviours:

- **Immutable by default** — operations return new collections; cheap to create. `merge()`/`unmerge()` exist for performance-intensive code.
- **Chainable** — most functions return the collection.
- **Singular caveat** — a function returning a value on a collection of >1 element returns it for only the first element.
- **Filtering** — `filter` accepts a selector **or** a function (a filter function can be used wherever a selector is accepted): `collection.filter(ele => ele.data('weight') > 50)`.

### Traversing

```js
// One-hop
node.neighborhood();              // connected edges + their endpoints
node.neighborhood('node');        // connected nodes only
node.neighborhoodNodes();         // connected nodes
node.neighborhoodEdges();         // connected edges
node.connectedEdges();            // edges incident to node
node.connectedNodes();            // nodes connected via edges
node.incomers();                  // incoming edges + source nodes
node.outgoers();                  // outgoing edges + target nodes

// All-hops (transitive)
node.successors();                // all downstream nodes
node.predecessors();              // all upstream nodes
node.descendants();               // compound: all descendant nodes
node.ancestors();                 // compound: all ancestor nodes

// DAG extremities
collection.sources();             // nodes with no incoming edges
collection.sinks();               // nodes with no outgoing edges

// Edge traversing
edge.source();                    // source node
edge.target();                    // target node
edge.parallelEdges();             // edges with same source and target
edge.codirectedEdges();           // parallel edges with same direction

// N-hop
collection.nhop(2);               // nodes within 2 hops
collection.nhopEdges(2);          // edges within 2 hops
collection.nhopAll(2);            // all elements within 2 hops
```

### Set theory and comparison

```js
a.union(b); a.intersection(b); a.difference(b);
a.symmetricDifference(b); a.absoluteComplement();
a.contains(b);                  // true if all of b is in a
a.anySame(b);                   // true if any overlap
a.same(b);                      // true if exactly equal

collection.max('data(weight)');  // element with max weight
collection.min(ele => ele.degree()); // custom comparator
```

### Iteration

```js
collection.forEach((ele, i) => { /* ... */ });
const ids = collection.map(ele => ele.id());
const total = collection.reduce((sum, ele) => sum + ele.data('weight'), 0);
collection.every(ele => ele.data('active'));
collection.some(ele => ele.data('weight') > 100);
collection.sort((a, b) => a.data('weight') - b.data('weight'));
```

### Position and dimensions

```js
ele.position();                // { x, y } (model coords)
ele.position('x');
ele.position({ x: 100, y: 200 });
ele.renderedPosition();        // screen pixels

collection.positions({ 'a': { x: 0, y: 0 }, 'b': { x: 100, y: 100 } }); // batch

collection.boundingBox();      // { x1, y1, x2, y2, w, h } (model coords)
collection.layoutDimensions({ padding: 20 });
node.width(); node.height();
node.renderedWidth(); node.renderedHeight();
```

### Data, scratch, style

```js
ele.data('key'); ele.data('key', value); ele.data({ k1: v1, k2: v2 });
ele.removeData('key');
ele.scratch('key'); ele.scratch('key', value);   // non-serialised, app fields `_`-prefixed
ele.rscratch('key', value);                      // internal scratch (no events, extensions)

// Read computed style
ele.style('background-color');
ele.numericStyle('width');                       // numeric value only
ele.numericStyleUnits('width');                  // { value, units }

// Imperative style (bypasses stylesheet)
ele.css({ 'background-color': 'red' });
ele.removeCss('background-color');
```

### State switching

```js
ele.select(); ele.unselect();
ele.selectify(); ele.unselectify();
ele.lock(); ele.unlock();
ele.grabify(); ele.ungrabify();
ele.panify(); ele.unpanify();

// Check state
ele.selected(); ele.selectable();
ele.locked(); ele.grabbable(); ele.pannable();
```

### Move

```js
// Change edge endpoints
edge.move({ source: 'newSource', target: 'newTarget' });
// Change node parent
node.move({ parent: 'newParent' });
node.move({ parent: null }); // remove from compound
```

### Classes, flash, clone, diff

```js
ele.addClass('highlight active');
ele.removeClass('highlight');
ele.toggleClass('highlight');
ele.hasClass('highlight');
ele.classes();                        // space-separated string

ele.flashClass('highlight', 500);    // add class for 500ms
ele.animated();                      // see Animation reference
ele.stop();                          // stop animations on this element

collection.clone();                  // deep copy (not restored to graph)
collection.diff(other);              // { added, removed, common }
```

## Objects you pass in

Objects passed to Cytoscape (elements, animations, layouts) are considered **owned by Cytoscape** — no deep copy is made. If you later mutate an object you added, copy it before passing.

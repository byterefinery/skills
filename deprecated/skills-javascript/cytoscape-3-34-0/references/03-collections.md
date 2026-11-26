# Collections

Collections are immutable sets of graph elements. They extend `Array` and support functional programming patterns.

## Basics

```js
// Creation
const nodes = cy.nodes();
const edges = cy.edges();
const all = cy.elements();
const filtered = cy.$('node[weight > 50]');

// Properties
collection.length;        // number of elements
collection.empty();       // true if no elements
collection.size();        // alias for length

// Access
collection.eq(0);         // first element
collection[0];            // direct array access
collection.iterator(0);   // first element

// Spawning
collection.spawn([ele1, ele2]); // new collection from elements
collection.spawnSelf();         // copy of self
collection.unique();            // deduplicate
```

## Group

```js
collection.nodes();    // filter to nodes only
collection.edges();    // filter to edges only
collection.group();    // 'nodes' or 'edges' (for singular)

// Type checks
collection.isNode();   // all are nodes
collection.isEdge();   // all are edges
collection.isNodes();  // alias
collection.isEdges();  // alias
```

## Traversing

### One-Hop

```js
node.neighborhood();              // connected edges + their endpoints
node.neighborhood('node');        // connected nodes only
node.neighborhood('edge');        // connected edges only

node.neighborhoodEdges();         // connected edges
node.neighborhoodNodes();         // connected nodes

node.connectedEdges();            // edges incident to node
node.connectedNodes();            // nodes connected via edges

node.incomers();                   // incoming edges + source nodes
node.incomers('node');             // source nodes only
node.incomers('edge');             // incoming edges only

node.outgoers();                   // outgoing edges + target nodes
node.outgoers('node');             // target nodes only
node.outgoers('edge');             // outgoing edges only
```

### All-Hops (Transitive)

```js
node.successors();                  // all downstream nodes
node.successors('node');            // nodes only
node.successors('edge');            // edges only

node.predecessors();                // all upstream nodes
node.descendants();                 // compound: all descendant nodes
node.ancestors();                   // compound: all ancestor nodes
```

### DAG Extremities

```js
collection.sources();               // nodes with no incoming edges (DAG sources)
collection.sinks();                 // nodes with no outgoing edges (DAG sinks)
```

### Edge Traversing

```js
edge.source();                      // source node
edge.target();                      // target node
edge.parallelEdges();              // edges with same source and target
edge.codirectedEdges();            // parallel edges with same direction
```

### N-Hop

```js
collection.nhop(2);                 // nodes within 2 hops
collection.nhopEdges(2);            // edges within 2 hops
collection.nhopNodes(2);            // nodes within 2 hops
collection.nhopAll(2);              // all elements within 2 hops
```

## Filtering

```js
// By selector
collection.filter('node#foo');
collection.filter('.highlight');
collection.filter('[weight > 50]');

// By function
collection.filter(ele => ele.data('active'));
collection.filter(ele => ele.isNode() && ele.degree() > 3);

// By index
collection.filter(':visible');
collection.filter(':selected');
collection.filter(':animated');
```

## Set Theory

```js
const a = cy.$('#a, #b');
const b = cy.$('#b, #c');

a.intersection(b);         // { b }
a.union(b);                // { a, b, c }
a.difference(b);           // { a }
a.symmetricDifference(b);  // { a, c }
a.absoluteComplement();    // all elements not in a
a.contains(b);             // true if all of b is in a
a.anySame(b);              // true if any overlap
a.same(b);                 // true if exactly equal
```

## Comparators

```js
collection.max('data(weight)');    // element with max weight
collection.min('data(weight)');    // element with min weight
collection.max(ele => ele.degree()); // custom comparator
collection.midpoint('data(weight)'); // median element
```

## Iteration

```js
// forEach
collection.forEach((ele, i) => {
  console.log(ele.id(), ele.data());
});

// Map
const ids = collection.map(ele => ele.id());

// Reduce
const totalWeight = collection.reduce((sum, ele) => sum + ele.data('weight'), 0);

// Every / Some
collection.every(ele => ele.data('active'));
collection.some(ele => ele.data('weight') > 100);

// Sort
collection.sort((a, b) => a.data('weight') - b.data('weight'));
```

## Position

```js
// Single element
ele.position();                // { x, y }
ele.position('x');             // x coordinate
ele.position({ x: 100, y: 200 });

// Batch position
collection.positions({
  'a': { x: 0, y: 0 },
  'b': { x: 100, y: 100 }
});

// Layout positions (set from layout)
collection.layoutPositions((ele, pos) => {
  return pos; // or modify
});

// Rendered position
ele.renderedPosition();
ele.renderedPosition('x');
```

## Dimensions

```js
// Bounding box (model coordinates)
collection.boundingBox();      // { x1, y1, x2, y2, w, h }

// Layout dimensions (with padding)
collection.layoutDimensions({
  padding: 20,
  boundingBox: { x1: 0, y1: 0, x2: 500, y2: 500 }
});

// Width/height
node.width(); node.height();
node.renderedWidth(); node.renderedHeight();
```

## Data

```js
// Data (serialised, immutable keys: id, source, target, parent)
ele.data('key');
ele.data('key', value);
ele.data({ key1: v1, key2: v2 });
ele.removeData('key');

// Scratch (non-serialised, mutable)
ele.scratch('key');
ele.scratch('key', value);
ele.removeScratch('key');

// Internal scratch (no events, for extensions)
ele.rscratch('key', value);
ele.removeRscratch('key');
```

## Style (Collection)

```js
// Read computed style
ele.style('background-color');
ele.numericStyle('width');           // numeric value only
ele.numericStyleUnits('width');      // { value, units }
ele.renderedCss('background-color'); // CSS string value

// Imperative style (bypasses stylesheet)
ele.css({ 'background-color': 'red' });
ele.removeCss('background-color');
```

## Classes

```js
ele.addClass('highlight active');
ele.removeClass('highlight');
ele.toggleClass('highlight');
ele.hasClass('highlight');
ele.classes('highlight active');     // set all classes
ele.classes();                        // get space-separated string
```

## State Switching

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

## Move

```js
// Change edge endpoints
edge.move({ source: 'newSource', target: 'newTarget' });

// Change node parent
node.move({ parent: 'newParent' });
node.move({ parent: null }); // remove from compound
```

## Compound Nodes

```js
node.parent();          // direct parent
node.parents();         // all ancestors
node.children();        // direct children
node.descendants();     // all descendants
node.leaves();          // leaf descendants
node.commonAncestors(otherNode); // shared ancestors

node.isParent();        // has children
node.isChildless();     // no children
node.isChild();         // has a parent
node.isOrphan();        // no parent
node.isCompound();      // alias for isParent()
```

## Layout (Collection)

```js
// Run layout on collection
collection.layout({ name: 'circle', radius: 100 }).run();
```

## Misc

```js
ele.id();               // element ID
ele.same(otherEle);     // same element
ele.group();            // 'nodes' or 'edges'

// Clone
collection.clone();     // deep copy (not restored to graph)
collection.copy();      // alias

// Diff
collection.diff(otherCollection); // { added, removed, common }

// Flash class (temporary highlight)
ele.flashClass('highlight', 500); // add class for 500ms
```

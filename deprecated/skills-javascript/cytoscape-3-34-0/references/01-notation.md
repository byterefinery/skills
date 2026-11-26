# Notation

## Elements JSON Format

Elements are specified as JSON objects at initialisation or via `cy.add()`.

### Flat Array Format

```js
elements: [
  { group: 'nodes', data: { id: 'a' }, position: { x: 100, y: 100 } },
  { group: 'nodes', data: { id: 'b' } },
  { group: 'edges', data: { id: 'ab', source: 'a', target: 'b' } }
]
```

### Grouped Format

```js
elements: {
  nodes: [
    { data: { id: 'a' } },
    { data: { id: 'b' } }
  ],
  edges: [
    { data: { id: 'ab', source: 'a', target: 'b' } }
  ]
}
```

### Node Definition

```js
{
  group: 'nodes',       // auto-inferred if no source/target
  data: {
    id: 'a',            // required (string); auto-generated if omitted
    parent: 'parentId', // compound parent (undefined = no parent)
    // ... custom data fields
  },
  position: { x: 100, y: 100 },     // model position (optional on init)
  renderedPosition: { x: 100, y: 100 }, // screen pixel position
  selected: false,       // initial selection state
  selectable: true,      // whether selection is mutable
  locked: false,         // whether position is immutable
  grabbable: true,       // whether user can drag the node
  pannable: false,       // whether dragging causes panning
  classes: ['foo', 'bar'] // class names (array or space-separated string)
}
```

### Edge Definition

```js
{
  group: 'edges',       // auto-inferred if source/target present
  data: {
    id: 'ab',
    source: 'a',        // source node id (required)
    target: 'b',        // target node id (required)
    // ... custom data fields
  },
  pannable: true        // whether dragging causes panning
}
```

## Position Model

### Model Coordinates

Model positions are stored in the graph model and remain constant regardless of zoom/pan. All style property values (width, height, etc.) are specified in model coordinates.

```js
// Get/set model position
ele.position();           // { x: 100, y: 100 }
ele.position('x');        // 100
ele.position({ x: 200, y: 300 });
```

### Rendered Coordinates

Rendered positions are screen pixel positions relative to the viewport. They change with zoom and pan.

```js
// Rendered position
ele.renderedPosition();           // { x: 200, y: 150 }
ele.renderedPosition('x');        // 200

// Convert between coordinate systems
cy.renderedCanvasPosition({ x: 100, y: 100 }); // rendered → model
cy.canvasRenderedPosition({ x: 100, y: 100 });  // model → rendered
```

At zoom 1 and pan (0, 0), model and rendered coordinates are identical.

## Compound Nodes

Compound nodes create parent-child hierarchies. A compound parent's position and dimensions are automatically computed from its children.

### Defining Compounds

```js
elements: [
  { data: { id: 'parent' } },
  { data: { id: 'child1', parent: 'parent' } },
  { data: { id: 'child2', parent: 'parent' } },
  { data: { id: 'grandchild', parent: 'child1' } } // nested
]
```

### Compound API

```js
node.parent();            // parent node (empty collection if none)
node.parents();           // all ancestors
node.children();          // direct children
node.descendants();       // all descendants
node.leaves();            // descendant leaf nodes
node.isParent();          // has children?
node.isChildless();       // no children
node.isChild();           // has a parent
node.isOrphan();          // no parent
```

### Moving Children

```js
// Change parent (parent key is immutable via data())
child.move({ parent: 'newParent' });
child.move({ parent: null }); // remove from compound
```

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

## Object Ownership

Objects passed to Cytoscape.js are owned by the library. Cytoscape mutates them internally for performance. Copy objects manually before passing if you need to retain the originals.

```js
// Safe — Cytoscape copies internally for simple cases
cy.add({ data: { id: 'a' } });

// If you need the original intact
const obj = { data: { id: 'a' } };
cy.add(JSON.parse(JSON.stringify(obj)));
```

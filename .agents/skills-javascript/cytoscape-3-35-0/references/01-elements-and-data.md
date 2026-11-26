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

## Collections

Core accessors return collections: `cy.elements()`, `cy.nodes()`, `cy.edges()`, `cy.filter(selector)`, `cy.$(selector)`, `cy.$id(id)`, `cy.getElementById(id)`.

Key behaviours:

- **Immutable by default** — operations return new collections; cheap to create. `merge()`/`unmerge()` exist for performance-intensive code.
- **Chainable** — most functions return the collection.
- **Singular caveat** — a function returning a value on a collection of >1 element returns it for only the first element.
- Set-theory ops: `union`, `intersection`, `difference`, `absoluteComplement`, `xor`.
- Traversal: `neighborhood`, `closedNeighborhood`, `connectedEdges`, `connectedNodes`, `edgesWith`, `edgesTo`, `commonAncestors`, `compoundNodes`.
- Styling/state on collections: `addClass`/`removeClass`/`toggleClass`/`hasClass`, `select`/`unselect`/`selected`, `lock`/`unlock`/`locked`, `grabify`/`ungrabify`, `hidden`, `animate`, `flashClass`, `stop`, `map`.
- `map`, `forEach`, `every`, `some` for functional use; `filter` accepts a selector **or** a function (a filter function can be used wherever a selector is accepted).

## Objects you pass in

Objects passed to Cytoscape (elements, animations, layouts) are considered **owned by Cytoscape** — no deep copy is made. If you later mutate an object you added, copy it before passing.

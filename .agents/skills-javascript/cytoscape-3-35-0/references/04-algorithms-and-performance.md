# Algorithms and performance

## Graph algorithms

All algorithms run on collections and work in headless mode without rendering.

### Shortest path

```js
// Dijkstra — returns { dist: Map<id, distance>, pred: Map<id, predecessorEdge> }
cy.elements().dijkstra({
  root: '#a',                              // root node (selector, element, or collection)
  directed: true,                          // respect edge directions
  weight: (edge) => edge.data('weight'),   // edge weight function
  edgeWeightComparability: (a, b) => {},   // custom comparison
  maxDistance: Infinity
});
result.dist.get('b');   // shortest distance from 'a' to 'b'
result.pred.get('b');   // predecessor edge on shortest path

// A* — same return format; add goal test + heuristic
collection.aStar({ root: '#a', directed: true, weight: (e) => e.data('weight'),
  goal: (node) => node.id() === 'target',
  heuristic: (node) => 0 });

// Bellman-Ford — supports negative weights (no negative cycles)
collection.bellmanFord({ root: '#a', directed: true, weight: (e) => e.data('weight') });

// Floyd-Warshall — all-pairs shortest paths; returns Map<id, Map<id, {dist, pred}>>
collection.floydWarshall({ directed: true, weight: (e) => e.data('weight') });
```

### Graph traversal

```js
collection.breadthFirstSearch({
  root: '#a',
  directed: true,
  visit: (node, edge, depth, shouldStop) => {
    console.log(node.id(), 'at depth', depth);
    // return true (or shouldStop(true)) to stop traversal
  }
});

collection.depthFirstSearch({ root: '#a', directed: true,
  visit: (node, edge, shouldStop) => { /* ... */ } });
```

### Centrality

```js
collection.degreeCentrality({ weights: undefined });
collection.degreeCentralityNormalized({ weights: undefined }); // normalised to [0, 1]

collection.closenessCentrality({ weights: undefined, positive: false });
collection.closenessCentralityNormalized({ weights: undefined, positive: false });

collection.betweennessCentrality({
  sampleSize: undefined,  // sample subset of nodes (for large graphs)
  directed: true,
  weights: undefined,
  positive: false,
  endpoints: false
});

collection.pageRank({ dampingFactor: 0.85, numIter: 100, weights: undefined });
// Each returns Map<id, centrality>
```

### Minimum spanning tree (Kruskal)

```js
collection.kruskal({
  weights: (edge) => edge.data('weight'),
  checkConnectivity: true
});
// Returns: { spanningTree: edges, weight: totalWeight }
```

### Minimum cut (Karger-Stein)

```js
collection.kargerStein({ numRuns: 100 });  // more runs = higher accuracy
// Returns: { cut: edges, weight: cutWeight }
```

### Clustering

```js
collection.markovClustering({ inflate: 2, expand: 2, iterations: 100 });
// Returns: [ [nodeIds...], [nodeIds...], ... ]

collection.kMeans({ k: 3, iterations: 100, position: true, distance: (a, b) => {} });
// Returns: { clusters: [[ids...]], centroids: [{x, y}...] }

collection.kMedoids({ k: 3, iterations: 100, position: true, distance: (a, b) => {} });

collection.fuzzyCMeans({ k: 3, fuzziness: 2, iterations: 100, position: true, distance: (a, b) => {} });
// Returns: { clusters: Map<id, [membership...]> }

collection.hierarchicalClustering({ distance: (a, b) => {}, merge: (a, b) => {} });

collection.affinityPropagation({ damping: 0.5, iterations: 100, distance: (a, b) => {} });
// Returns: { clusters: [[ids...]], exemplars: [ids...] }
```

### Connectivity

```js
collection.tarjanStronglyConnected();        // Tarjan SCC
// Returns: [ [nodeIds...], [nodeIds...], ... ]

collection.hopcroftTarjanBiconnected();      // Hopcroft-Tarjan biconnected components
// Returns: { articulationPoints: [nodeIds...], biconnectedComponents: [[ids...]] }

collection.hierholzer();                     // Hierholzer (Eulerian circuit)
// Returns: [edgeIds...] — circuit path, or null if no Eulerian circuit
```

### Degree

```js
node.degree();        // total degree
node.indegree();      // incoming edges
node.outdegree();     // outgoing edges
```

### Common patterns

**Shortest path reconstruction** (walk predecessor edges back from the target):

```js
const result = cy.elements().dijkstra({ root: '#a', weight: () => 1 });

function getPath(targetId) {
  const path = [];
  let current = targetId;
  while (current) {
    path.unshift(current);
    const predEdge = result.pred.get(current);
    current = predEdge ? predEdge.source().id() : null;
  }
  return path;
}
```

**Connected component** (BFS over `neighborhood` until no new nodes):

```js
let component = cy.$('#a');
let visited = new Set([component.id()]);
for (;;) {
  const next = component.neighborhoodNodes().filter(n => !visited.has(n.id()));
  if (next.length === 0) break;
  next.forEach(n => visited.add(n.id()));
  component = component.add(next);
}
```

## Performance tuning checklist

From the official performance page, in descending order of significance:

1. **Use `cy.getElementById()`** — a lookup-table hit, faster than selector search (`cy.$id('foo')` is the shorthand; the single-ID selector `cy.$('#foo')` is also optimised but pays selector-parse cost).
2. **Batch element modifications** — `cy.batch()` for many changes at once.
3. **Animations** — none is fastest; `eles.flashClass()` is cheaper than smooth animation; limit concurrent animating elements; define `transition-property` only in the states you actually animate.
4. **Function style property values** — expensive; memoize them, or use `data()`/`mapData()` mappings instead.
5. **Labels** — expensive to draw. Drop them or show on tap/mouseover; avoid edge labels; set `min-zoomed-font-size` so tiny labels aren't rendered; label backgrounds and outlines cost more.
6. **Simplify edge style** — `curve-style: haystack` (straight lines) is the default and much cheaper than `bezier`; solid edges beat dotted/dashed; arrows are expensive when semantically meaningless; opaque edges with arrows render more than twice as fast as semitransparent ones.
7. **Simplify node style** — background images are very expensive (prefer non-repeating, non-clipped; preclip or use transparent PNGs); node borders are slightly expensive.
8. **Avoid compound and edge selectors** — e.g. `$node node`, `$node -> node` require traversals.
9. **Lower pixel ratio** — `pixelRatio: 1` on high-density displays (less crisp).
10. **Compound nodes** — make style calculation and rendering more expensive; avoid if unused.
11. **Hide edges during interactivity** — `hideEdgesOnViewport: true` (very large graphs only).
12. **Recycle large instances** — keeps memory lower than repeated `cy.destroy()` (canvas-heavy).
13. **Avoid many node overlays** — overlays can't be cached; limit simultaneous non-zero `overlay-opacity` nodes.
14. **Textured zoom & pan** — `textureOnViewport: true` (absolute cheapest option for very large graphs); `motionBlur`/`motionBlurOpacity` smooth frame transitions.

Renderer init options that affect performance (from the API reference): `styleEnabled` (default true; disable in headless), `hideEdgesOnViewport`, `hideLabelsOnViewport`, `textureOnViewport`, `motionBlur`, `motionBlurOpacity`, `wheelSensitivity`, `pixelRatio` (number or `'auto'`), `webgl` (experimental WebGL mode), `webglDebug`, `webglTexSize`.

Background facts: rendering cost scales with element count, edge count (bezier multigraphs worst), and canvas area (pixel ratio); edges are particularly expensive.

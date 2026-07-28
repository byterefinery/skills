# Graph Algorithms

All algorithms run on collections. They work in headless mode without rendering.

## Shortest Path

### Dijkstra

```js
collection.dijkstra({
  root: '#a',                           // root node (selector, element, or collection)
  directed: true,                       // respect edge directions
  weight: (edge) => edge.data('weight'), // edge weight function
  edgeWeightComparability: (a, b) => {}, // custom comparison
  maxDistance: Infinity
});

// Returns: { dist: Map<id, distance>, pred: Map<id, predecessorEdge> }
const result = cy.elements().dijkstra({ root: '#a' });
result.dist.get('b');   // shortest distance from 'a' to 'b'
result.pred.get('b');   // predecessor edge on shortest path
```

### A* (A-Star)

```js
collection.aStar({
  root: '#a',
  directed: true,
  weight: (edge) => edge.data('weight'),
  goal: (node) => node.id() === 'target', // goal test
  heuristic: (node) => 0                  // heuristic estimate to goal
});

// Same return format as Dijkstra
```

### Bellman-Ford

Supports negative weights (no negative cycles).

```js
collection.bellmanFord({
  root: '#a',
  directed: true,
  weight: (edge) => edge.data('weight')
});
```

### Floyd-Warshall

All-pairs shortest paths.

```js
collection.floydWarshall({
  directed: true,
  weight: (edge) => edge.data('weight')
});

// Returns: Map<id, Map<id, { dist, pred }>>
```

## Graph Traversal

### BFS (Breadth-First Search)

```js
collection.breadthFirstSearch({
  root: '#a',
  directed: true,
  visit: (node, edge, depth, shouldStop) => {
    console.log(node.id(), 'at depth', depth);
    // return true to stop traversal
  }
});
```

### DFS (Depth-First Search)

```js
collection.depthFirstSearch({
  root: '#a',
  directed: true,
  visit: (node, edge, shouldStop) => {
    console.log(node.id());
  }
});
```

## Centrality

### Degree Centrality

```js
collection.degreeCentrality({
  weights: undefined  // or weight function for edges
});
// Returns: Map<id, centrality>

collection.degreeCentralityNormalized({ weights: undefined });
// Normalised to [0, 1]
```

### Closeness Centrality

```js
collection.closenessCentrality({
  weights: undefined,
  positive: false     // whether weights are all positive
});

collection.closenessCentralityNormalized({ weights: undefined, positive: false });
```

### Betweenness Centrality

```js
collection.betweennessCentrality({
  sampleSize: undefined,  // sample subset of nodes (for large graphs)
  directed: true,
  weights: undefined,
  positive: false,
  endpoints: false
});
```

### PageRank

```js
collection.pageRank({
  dampingFactor: 0.85,
  numIter: 100,
  weights: undefined
});
// Returns: Map<id, pageRank>
```

## Minimum Spanning Tree

### Kruskal

```js
collection.kruskal({
  weights: (edge) => edge.data('weight'),
  checkConnectivity: true
});
// Returns: { spanningTree: edges, weight: totalWeight }
```

## Minimum Cut

### Karger-Stein

```js
collection.kargerStein({
  numRuns: 100  // more runs = higher accuracy
});
// Returns: { cut: edges, weight: cutWeight }
```

## Clustering

### Markov Clustering (MCL)

```js
collection.markovClustering({
  inflate: 2,
  expand: 2,
  iterations: 100
});
// Returns: [ [nodeIds...], [nodeIds...], ... ] — clusters
```

### K-Means

```js
collection.kMeans({
  k: 3,                    // number of clusters
  iterations: 100,
  position: true,          // use node positions as features
  distance: (a, b) => {}   // custom distance function
});
// Returns: { clusters: [[ids...]], centroids: [{x, y}...] }
```

### K-Medoids

```js
collection.kMedoids({
  k: 3,
  iterations: 100,
  position: true,
  distance: (a, b) => {}
});
```

### Fuzzy C-Means

```js
collection.fuzzyCMeans({
  k: 3,
  fuzziness: 2,
  iterations: 100,
  position: true,
  distance: (a, b) => {}
});
// Returns: { clusters: Map<id, [membership...]> }
```

### Hierarchical Clustering

```js
collection.hierarchicalClustering({
  distance: (a, b) => {},
  merge: (a, b) => {}      // how to merge clusters
});
```

### Affinity Propagation

```js
collection.affinityPropagation({
  damping: 0.5,
  iterations: 100,
  distance: (a, b) => {}
});
// Returns: { clusters: [[ids...]], exemplars: [ids...] }
```

## Connectivity

### Tarjan's Strongly Connected Components

```js
collection.tarjanStronglyConnected();
// Returns: [ [nodeIds...], [nodeIds...], ... ]
```

### Hopcroft-Tarjan Biconnected Components

```js
collection.hopcroftTarjanBiconnected();
// Returns: { articulationPoints: [nodeIds...], biconnectedComponents: [[ids...]] }
```

### Hierholzer's Algorithm (Eulerian Circuit)

```js
collection.hierholzer();
// Returns: [edgeIds...] — circuit path, or null if no Eulerian circuit
```

## Degree

```js
node.degree();        // total degree
node.indegree();      // incoming edges
node.outdegree();     // outgoing edges
```

## Common Patterns

### Find all paths from A to B (BFS)

```js
const paths = [];
cy.breadthFirstSearch({
  root: '#a',
  visit: (node, edge, depth, shouldStop) => {
    if (node.id() === 'b') {
      // found path
      shouldStop(true);
    }
  }
});
```

### Find connected component

```js
const component = cy.$('#a').add(cy.$('#a').neighborhood());
// Or use traversal
let component = cy.$('#a');
let visited = new Set([component.id()]);
for (;;) {
  const next = component.neighborhoodNodes().filter(n => !visited.has(n.id()));
  if (next.length === 0) break;
  next.forEach(n => visited.add(n.id()));
  component = component.add(next);
}
```

### Shortest path reconstruction

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

getPath('z'); // ['a', 'x', 'y', 'z']
```

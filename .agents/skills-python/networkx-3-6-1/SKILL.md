---
name: networkx-3-6-1
description: >
  Python graph library (NetworkX 3.6.1) for creating, manipulating, and analyzing complex networks.
  Use this skill whenever the user works with graphs, networks, nodes, edges, shortest paths, centrality,
  community detection, spanning trees, flow networks, DAGs, topological sort, graph generators,
  adjacency matrices, Laplacian spectra, isomorphism, bipartite matching, or any network science task.
  Triggers on: graph algorithms, network analysis, node/edge operations, Dijkstra, BFS, DFS, PageRank,
  Louvain communities, connected components, minimum spanning tree, max flow, transitive closure,
  and anything involving NetworkX or the `nx` module.
---

# networkx 3.6.1

NetworkX is a Python library for creating, manipulating, and studying the structure, dynamics, and functions of complex networks. Version 3.6.1 supports Python 3.10+ and relies on NumPy/SciPy for matrix operations.

## Overview

Four core graph classes cover most use cases:

| Class | Edges | Self-loops | Parallel edges |
|---|---|---|---|
| `nx.Graph` | Undirected | Yes | No |
| `nx.DiGraph` | Directed | Yes | No |
| `nx.MultiGraph` | Undirected | Yes | Yes |
| `nx.MultiDiGraph` | Directed | Yes | Yes |

Nodes can be any hashable Python object (integers, strings, tuples). Edges carry optional attribute dictionaries. The library is organized into modules: `generators`, `algorithms`, `linalg`, `drawing`, `readwrite`, `convert`, and `relabel`.

## Usage

```python
import networkx as nx

# Create graphs
G = nx.Graph()
G.add_node(1, color="red")
G.add_edge(1, 2, weight=3.0)
G.add_edges_from([(1, 3), (2, 3)], weight=1.0)

# Or from generators
G = nx.path_graph(10)
G = nx.erdos_renyi_graph(100, 0.1, seed=42)
G = nx.barabasi_albert_graph(100, 3, seed=42)

# Basic properties
len(G)                      # number of nodes
G.number_of_edges()         # number of edges
list(G.nodes(data=True))    # nodes with attributes
list(G.edges(data=True))    # edges with attributes
G.degree(1)                 # degree of node 1

# Subgraphs and views
H = G.subgraph([1, 2, 3])   # induced subgraph (view, not copy)
H = G.copy()                # deep copy

# Converting types
DG = G.to_directed()        # Graph -> DiGraph view
UG = DG.to_undirected()     # DiGraph -> Graph view
```

### Common Patterns

**Weighted shortest paths:**
```python
path = nx.shortest_path(G, source=0, target=9, weight="weight")
length = nx.shortest_path_length(G, source=0, target=9, weight="weight")
# Dijkstra from single source
paths, lengths = nx.single_source_dijkstra(G, source=0, weight="weight")
```

**Centrality measures:**
```python
nx.degree_centrality(G)
nx.betweenness_centrality(G)
nx.pagerank(G, alpha=0.85)
```

**Community detection:**
```python
communities = nx.community.louvain_communities(G, seed=42)
partition = next(nx.community.girvan_newman(G))
```

**Connected components:**
```python
components = list(nx.connected_components(G))       # undirected
scc = list(nx.strongly_connected_components(DG))    # directed
nx.is_connected(G)                                  # single component?
```

## Gotchas

- **`weight` parameter is a string key, not a boolean.** Pass `weight="weight"` to use the `"weight"` edge attribute. Pass `weight=None` for unweighted (every edge costs 1). Never pass `weight=True`.

- **Graph views are live, not copies.** `G.subgraph(nodes)` returns a view that reflects changes to `G`. Call `.copy()` if you need an independent graph. Views of views chain slowly — avoid nesting more than ~15 levels deep.

- **`nx.shortest_path` raises `NetworkXNoPath`** when source and target are in different components. Use `try/except` or check `nx.has_path(G, s, t)` first.

- **DiGraph iteration follows edge direction.** `G.neighbors(node)` on a DiGraph returns only *successors* (outgoing edges). Use `G.predecessors(node)` for incoming edges.

- **MultiGraph edges need keys.** On multigraphs, `G.edges(data=True)` yields `(u, v, data)` but parallel edges share `(u, v)`. Use `G.edges(keys=True, data=True)` for `(u, v, key, data)`.

- **`add_edges_from` with attributes applies to all edges.** `G.add_edges_from([(a,b), (c,d)], weight=2)` sets `weight=2` on both edges. To set per-edge attributes, pass dicts: `G.add_edges_from([(a, b, {"w": 1}), (c, d, {"w": 2})])`.

- **Layout functions need NumPy.** All `nx.*_layout()` functions require NumPy. Drawing with `nx.draw()` additionally needs Matplotlib.

- **`create_using` controls output type.** Many generators and conversion functions accept `create_using=nx.DiGraph()` to force a specific graph class. Pass a class or an instance.

- **Node labels can be any hashable.** Strings, tuples, even custom objects work as nodes — but not `None`. When converting between formats, label types may change (e.g., `convert_node_labels_to_integers`).

- **`nx.pagerank` on undirected graphs auto-converts to directed.** Each undirected edge becomes two directed edges internally.

- **Community detection is stochastic.** Functions like `louvain_communities` and `girvan_newman` may return different results across runs. Always pass `seed` for reproducibility.

## References

- [01-graph-classes](references/01-graph-classes.md) — Graph, DiGraph, MultiGraph, MultiDiGraph; node/edge APIs; views
- [02-generators](references/02-generators.md) — Classic graphs, random graphs, geometric, social networks
- [03-shortest-paths](references/03-shortest-paths.md) — BFS, DFS, Dijkstra, Bellman-Ford, A*, Floyd-Warshall, Johnson
- [04-centrality](references/04-centrality.md) — Degree, betweenness, closeness, eigenvector, Katz, PageRank, HITs
- [05-communities](references/05-communities.md) — Louvain, Leiden, Girvan-Newman, label propagation, modularity
- [06-connectivity-components](references/06-connectivity-components.md) — Connected/strongly connected components, biconnected, articulation points, bridges
- [07-flow-matching](references/07-flow-matching.md) — Max flow, min-cost flow, Gomory-Hu, matching algorithms
- [08-dag-algorithms](references/08-dag-algorithms.md) — Topological sort, ancestors/descendants, transitive closure/reduction
- [09-conversion-io](references/09-conversion-io.md) — NumPy/Pandas/SciPy conversion; GraphML, GEXF, edgelist, JSON
- [10-matrices-linalg](references/10-matrices-linalg.md) — Adjacency/Laplacian/incidence matrices, spectra, algebraic connectivity
- [11-graph-operators](references/11-graph-operators.md) — Union, intersection, difference, symmetric difference, products, complement
- [12-drawing-layout](references/12-drawing-layout.md) — Matplotlib drawing, layout algorithms, Graphviz/PyDot export

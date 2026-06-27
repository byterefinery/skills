# Connectivity and Components

## Connected Components (Undirected)

```python
components = list(nx.connected_components(G))           # list of sets
num = nx.number_connected_components(G)                 # count
largest = max(nx.connected_components(G), key=len)     # largest component
nx.is_connected(G)                                      # single component?

# Component containing a specific node
comp = next(c for c in nx.connected_components(G) if node in c)

# Ego / connected subgraph
ego = G.subgraph(next(c for c in nx.connected_components(G) if node in c))
```

## Strongly Connected Components (Directed)

```python
sccs = list(nx.strongly_connected_components(DG))
num_scc = nx.number_strongly_connected_components(DG)
nx.is_strongly_connected(DG)

# Condensation graph: each SCC becomes one node
condensed = nx.condensation(DG)
```

## Weakly Connected Components (Directed)

Treat directed edges as undirected.

```python
wccs = list(nx.weakly_connected_components(DG))
num_wcc = nx.number_weakly_connected_components(DG)
nx.is_weakly_connected(DG)
```

## Biconnected Components

Subgraphs connected by at least 2 nodes (no articulation points within).

```python
biconnected = list(nx.biconnected_components(G))
articulation_points = list(nx.articulation_points(G))
nx.is_biconnected(G)
```

## Bridges

Edges whose removal disconnects the graph.

```python
bridges = list(nx.bridges(G))
```

## k-Connectivity

```python
k = nx.node_connectivity(G)                   # minimum nodes to remove to disconnect
k = nx.edge_connectivity(G)                   # minimum edges to remove
k = nx.node_connectivity(G, s, t)             # local connectivity between s and t
k = nx.edge_connectivity(G, s, t)
```

## Attracting Components

Nodes that cannot be reached from outside once entered.

```python
attracting = list(nx.attracting_components(DG))
```

## Semiconnected Graphs

A directed graph is semiconnected if for every pair of nodes, at least one direction has a path.

```python
nx.is_semiconnected(DG)
```

## All-Pairs Reachability

```python
# For small graphs
reachability = nx.transitive_closure(DG)       # returns new DiGraph with all reach edges
```

## Minimum Cuts (Stoer-Wagner)

```python
cut_value, partition = nx.stoer_wagner_min_cut(G, weight="weight")
# partition is (set_A, set_B) — the two sides of the minimum cut
```

## Key Gotchas

- **`is_connected` raises `NetworkXPointlessConcept`** on null graphs (0 nodes). Check `len(G) > 0` first.
- **`connected_components` returns a generator**, not a list. Call `list()` to materialize.
- **Biconnected components include bridges as single-edge components.** Each bridge forms its own biconnected component `{(u, v)}`.
- **Articulation points exclude endpoints of bridges** in some definitions — NetworkX includes all cut vertices.
- For large graphs, use `number_connected_components(G)` instead of `len(list(nx.connected_components(G)))` to avoid materializing all components.

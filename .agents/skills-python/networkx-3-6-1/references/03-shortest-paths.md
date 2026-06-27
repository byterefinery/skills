# Shortest Paths

## Generic Interface

```python
nx.shortest_path(G, source=None, target=None, weight=None, method="dijkstra")
nx.shortest_path_length(G, source=None, target=None, weight=None)
nx.all_shortest_paths(G, source, target, weight=None)        # generator of all shortest paths
nx.has_path(G, source, target)                               # bool
```

**Return types depend on arguments:**
- Both `source` and `target`: single path as list `[s, ..., t]`
- Only `source`: dict `{target: [path], ...}`
- Only `target`: dict `{source: [path], ...}`
- Neither: iterator of `(source, {target: path})`

## Unweighted (BFS-based)

```python
nx.single_source_shortest_path(G, source)                    # all paths from source
nx.single_source_shortest_path_length(G, source)             # lengths
nx.all_pairs_shortest_path(G)                                # iterator over (src, dict)
nx.all_pairs_shortest_path_length(G)                         # iterator
```

Uses BFS. O(V + E) per source.

## Weighted: Dijkstra

For non-negative edge weights.

```python
# Single pair
nx.dijkstra_path(G, source, target, weight="weight")
nx.dijkstra_path_length(G, source, target, weight="weight")

# Single source
nx.single_source_dijkstra(G, source, target=None, weight="weight")
# Returns (dict of paths, dict of lengths)

nx.single_source_dijkstra_path(G, source, weight="weight")
nx.single_source_dijkstra_path_length(G, source, weight="weight")

# Multiple sources
nx.multi_source_dijkstra(G, sources, weight="weight")
nx.multi_source_dijkstra_path(G, sources, weight="weight")
nx.multi_source_dijkstra_path_length(G, sources, weight="weight")

# All pairs
nx.all_pairs_dijkstra(G, weight="weight")                    # iterator
nx.all_pairs_dijkstra_path(G, weight="weight")
nx.all_pairs_dijkstra_path_length(G, weight="weight")
```

## Weighted: Bellman-Ford

Handles negative edge weights. Detects negative cycles.

```python
nx.bellman_ford_path(G, source, target, weight="weight")
nx.bellman_ford_path_length(G, source, target, weight="weight")
nx.single_source_bellman_ford(G, source, weight="weight")
# Returns (predecessor dict, distance dict)

nx.all_pairs_bellman_ford_path(G, weight="weight")
nx.all_pairs_bellman_ford_path_length(G, weight="weight")
nx.bellman_ford_predecessor_and_distance(G, source, weight="weight")

# Negative cycle detection
nx.negative_edge_cycle(G, weight="weight")                   # bool
nx.find_negative_cycle(G, weight="weight")                   # returns the cycle
```

## A* Search

Uses a heuristic function for guided search.

```python
nx.astar_path(G, source, target, weight="weight", heuristic=h)
nx.astar_path_length(G, source, target, weight="weight", heuristic=h)
```

The `heuristic` function takes `(u, v)` and returns an admissible estimate of distance from `u` to `v`. Pass `None` for Dijkstra-equivalent behavior.

## Dense Graph: Floyd-Warshall / Johnson

All-pairs algorithms returning full distance matrices and predecessor graphs.

```python
# Floyd-Warshall: O(V^3), handles negative weights
lengths, predecessors = nx.floyd_warshall(G, weight="weight")
nx.floyd_warshall_predecessor_and_distance(G, weight="weight")
nx.floyd_warshall_numpy(G, weight="weight", nodelist=...)    # NumPy array output

# Johnson: O(V^2 log V + VE), sparse graphs with negative weights
lengths, predecessors = nx.johnson(G, weight="weight")

# Goldberg-Radzik: alternative Bellman-Ford variant
nx.goldberg_radzik(G, source, weight="weight")
```

## Key Gotchas

- **`NetworkXNoPath`** is raised when no path exists between specified source and target. Catch it or use `nx.has_path()` first.
- For all-pairs on large graphs, prefer iterative functions (`all_pairs_dijkstra`) over matrix-based ones to save memory.
- Dijkstra does not work with negative weights — use Bellman-Ford or Johnson instead.
- The `weight` parameter is an edge attribute *key* (string), not a boolean. Use `weight="weight"` or `weight=None`.
- For unweighted shortest paths, omit `weight` entirely — the generic `nx.shortest_path()` automatically uses BFS when `weight=None`.

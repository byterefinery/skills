# Flow and Matching

## Maximum Flow

All max-flow functions require a capacity attribute on edges.

```python
flow_value, flow_dict = nx.maximum_flow(G, s, t, capacity="capacity")
# flow_value: total flow
# flow_dict: {u: {v: flow_amount}} per-node flow map

# Specific algorithms
nx.edmonds_karp(G, s, t, capacity="capacity")              # BFS-based, most common
nx.dinitz(G, s, t, capacity="capacity")                    # faster on many graphs
nx.preflow_push(G, s, t, capacity="capacity", pseudo_sink=None)  # good for dense
nx.shortest_augmenting_path(G, s, t, capacity="capacity") # often fastest
nx.boykov_kolmogorov(G, s, t, capacity="capacity")         # graph-cut variant
```

### Minimum Cut

```python
cut_value, partition = nx.minimum_cut(G, s, t, capacity="capacity")
# partition: (S, T) sets where s in S, t in T
flow_value, flow_dict, partition = nx.minimum_cut(G, s, t, capacity="capacity",
                                                    value_only=False)
```

### Gomory-Hu Tree

All-pairs min-cut tree.

```python
gh_tree = nx.gomory_hu_tree(G, capacity="capacity")
# Returns a weighted tree; edge weights = min-cut values between node pairs
```

## Minimum Cost Flow

```python
cost = nx.min_cost_flow(G)
# G must have:
#   - "capacity" on edges (use float('inf') for unlimited)
#   - "demand" on nodes (positive = demand, negative = supply)
#   - "weight" on edges (cost per unit flow)

# Capacity scaling variant
cost = nx.capacity_scaling(G, ...)
```

### Building a Min-Cost Flow Graph

```python
G = nx.DiGraph()
G.add_edge("A", "B", capacity=10, weight=2)
G.add_edge("B", "C", capacity=5, weight=3)
G.nodes["A"]["demand"] = -10   # supply of 10
G.nodes["C"]["demand"] = 10    # demand of 10
cost = nx.min_cost_flow(G)
```

## Matching

### Maximum Weight Matching

```python
matching = nx.max_weight_matching(G, maxcardinality=False)
# Returns set of edges: {(u, v), (x, y), ...}
# G must be undirected; edge weight attribute is "weight"
# maxcardinality=True: prefer more edges over higher total weight

# Minimum weight matching
matching = nx.min_weight_matching(G, maxcardinality=False)
```

### Maximal Matching (Greedy)

```python
matching = nx.maximal_matching(G)
# Fast greedy matching — not necessarily maximum size
```

### Matching Verification

```python
nx.is_matching(G, matching)                     # is it a valid matching?
nx.is_maximal_matching(G, matching)             # can't add more edges?
nx.is_perfect_matching(G, matching)             # covers all nodes?
```

## Key Gotchas

- **Max flow needs `capacity` attribute** (not `weight`). Set it explicitly: `G.add_edge(u, v, capacity=10)`.
- **Min cost flow needs `demand` on nodes.** Positive demand = sink, negative = source. Sum of all demands must be 0.
- **Matching functions work only on undirected graphs** and are not implemented for multigraphs or directed graphs.
- **`max_weight_matching` is exact but slow** (O(V³)) — suitable for graphs up to ~1000 nodes. Use `maximal_matching` for fast approximate results.
- **Gomory-Hu tree** computes all-pairs min-cuts efficiently. The weight of the unique path between any two nodes in the tree equals their min-cut value.
- **Residual networks** are created internally by flow algorithms. Use `nx.build_residual_network(G)` if you need to inspect one.

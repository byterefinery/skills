# Graph Operators

## Unary Operators

```python
nx.complement(G)                                 # complement graph
nx.reverse_view(DG)                              # reverse all edge directions (view)
DG.reverse(copy=True)                            # reversed DiGraph (copy)
```

## Binary Operators

All binary operators accept two graphs and return a new graph. Node labels must not overlap unless using `name` attribute to distinguish.

### Union

```python
H = nx.union(G1, G2)                             # disjoint union
H = nx.union(G1, G2, rename=("A_", "B_"))        # prefix nodes to avoid overlap
```

### Join

Union plus all edges between the two graphs.

```python
H = nx.disjoint_union(G1, G2)                    # union, no cross edges
H = nx.join(G1, G2)                              # union + all cross edges
```

### Intersection

```python
H = nx.intersection(G1, G2)                      # shared nodes and edges
```

Only nodes and edges present in both graphs are kept.

### Difference

```python
H = nx.difference(G1, G2)                        # nodes/edges in G1 but not G2
```

### Symmetric Difference

```python
H = nx.symmetric_difference(G1, G2)              # nodes/edges in exactly one graph
```

## Graph Products

```python
# Cartesian product
H = nx.cartesian_product(G1, G2)
# Nodes: (u, v) for u in G1, v in G2
# Edges: ((u,v),(u',v)) if uu' in G1, or ((u,v),(u,v')) if vv' in G2

# Tensor (Kronecker) product
H = nx.tensor_product(G1, G2)
# Edges: ((u,v),(u',v')) if uu' in G1 AND vv' in G2

# Strong product
H = nx.strong_product(G1, G2)
# Cartesian + Tensor edges

# Lexicographic product
H = nx.lexicographic_product(G1, G2)
# ((u,v),(u',v')) if uu' in G1, or (u==u' AND vv' in G2)

# Modular product
H = nx.modular_product(G1, G2, decl)
# With compatibility relation decl

# Power of a graph
H = nx.graph_power(G, k)                         # distance-k neighbors become edges
```

## Composition (Overlay)

```python
H = nx.compose(G1, G2)                           # union of nodes and edges
H = nx.disjoint_union(G1, G2)                    # compose with renamed nodes
```

`compose` keeps all nodes and edges from both graphs. If nodes overlap, their attributes are taken from `G1`.

## Key Gotchas

- **Node label collisions:** Binary operators on graphs with overlapping node labels merge those nodes (attributes from first graph win). Use `rename` parameter or ensure disjoint labels.
- **`complement(G)`** creates edges between all non-adjacent pairs. Self-loops are not added. The complement of a complete graph has no edges.
- **Graph products create compound node labels** as tuples `(u, v)`. When using integer nodes from both inputs, this is fine. With mixed types, be aware of the tuple structure.
- **`reverse_view(DG)` returns a view**, not a copy. Changes to `DG` are reflected in the reversed view. Call `.copy()` for an independent graph.
- **`graph_power(G, k)`** connects nodes at distance ≤ k. Useful for creating small-world-like graphs from lattices.
- **`compose` vs `union`:** `compose` merges overlapping nodes; `union` with `rename` keeps them separate.

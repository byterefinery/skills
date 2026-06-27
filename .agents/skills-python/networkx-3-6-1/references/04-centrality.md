# Centrality Measures

All centrality functions return a `dict` mapping node → score.

## Degree Centrality

```python
nx.degree_centrality(G)              # fraction of nodes connected to
nx.in_degree_centrality(DG)          # incoming connections (DiGraph only)
nx.out_degree_centrality(DG)         # outgoing connections (DiGraph only)
```

Normalized by `n-1`. Values in `[0, 1]` for simple graphs.

## Betweenness Centrality

Fraction of shortest paths passing through each node.

```python
nx.betweenness_centrality(G, k=None, weight=None, normalized=True)
```

- `k`: subsample k nodes for approximation (speeds up on large graphs)
- `weight`: edge attribute key for weighted betweenness
- O(V·E) exact; use `k` for approximation

## Closeness Centrality

Inverse of average shortest path distance to all other nodes.

```python
nx.closeness_centrality(G, weight=None, wf_improved=False)
```

For disconnected graphs, consider `wf_improved=True` (Wasserman-Faust definition).

## Eigenvector Centrality

Importance based on neighbors' importance. Solves eigenvector problem of adjacency matrix.

```python
nx.eigenvector_centrality(G, weight="weight", max_iter=100, tol=1e-06, nstart=None)
nx.eigenvector_centrality_numpy(G, weight="weight")
```

May raise `PowerIterationFailedConvergence` if iteration limit exceeded.

## Katz Centrality

Variant of eigenvector centrality with damping and normalization.

```python
nx.katz_centrality(G, alpha=1e-05, beta=1.0, max_iter=100, tol=1e-06, weight="weight")
nx.katz_centrality_numpy(G, alpha=1e-05, beta=1.0, weight="weight")
```

`alpha` is the damping factor (must be below inverse of largest eigenvalue).

## PageRank

Random surfer model with damping factor `alpha`.

```python
nx.pagerank(G, alpha=0.85, personalization=None, max_iter=100, tol=1e-06, weight="weight")
```

- `personalization`: dict of nodes → bias values
- Undirected graphs are auto-converted to directed internally
- On DiGraphs, dangling nodes (no out-edges) distribute uniformly by default

## HITs (Hubs and Authorities)

```python
nx.hits(G, max_iter=100, tol=1e-06, nstart=None, weight="weight")
# Returns (hub_scores, authority_scores) — both dicts
```

## Current-Flow Centrality

Random-walk based centrality using electrical flow analogy. Requires NumPy/SciPy.

```python
nx.current_flow_betweenness_centrality(G, weight=None, tol=1e-4)
nx.current_flow_betweenness_centrality_subset(G, sources, targets, ...)
nx.current_flow_closeness_centrality(G, weight=None, tol=1e-4)
```

## Load and Vitality

```python
nx.load_centrality(G, weight=None, normalized=True)
nx.edge_load(G, weight=None)                    # load on edges
nx.approximate_current_flow_betweenness_centrality(G, ...)
```

## Second-Order Centrality

```python
nx.second_order_centrality(G)
# Returns (node_scores, second_order_graph)
```

## Dispersion and Subgraph Centrality

```python
nx.dispersion(G, weight="weight")
nx.subgraph_centrality(G, weight="weight")
nx.normalized_subgraph_centrality(G, weight="weight")
nx.tree_diversity(G, weight="weight")
```

## Voterank

Combines PageRank and greedy coloring.

```python
nx.voterank(G, alpha=0.13, max_iter=100, tol=1e-06, weight="weight")
# Returns list of (node, layer) tuples
```

## Choosing the Right Measure

| Use case | Recommended measure |
|---|---|
| "Most connected nodes" | `degree_centrality` |
| "Bottleneck / bridge nodes" | `betweenness_centrality` |
| "Closest to everyone" | `closeness_centrality` |
| "Influential in social network" | `eigenvector_centrality` or `pagerank` |
| "Web page ranking" | `pagerank` |
| "Topic hubs and authorities" | `hits` |
| Large graph, approximate | `betweenness_centrality(G, k=100)` |

## Key Gotchas

- Eigenvector-based methods (`eigenvector_centrality`, `katz_centrality`) may not converge on all graphs. Catch `PowerIterationFailedConvergence`.
- Betweenness centrality is O(V·E) — use the `k` parameter to subsample on large graphs.
- PageRank on undirected graphs converts each edge into two directed edges, so results differ from eigenvector centrality.
- All centrality values are normalized (in `[0, 1]`) by default where applicable.

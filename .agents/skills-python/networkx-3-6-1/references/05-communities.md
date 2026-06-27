# Community Detection

## Louvain Method

Fast, hierarchical modularity optimization. Most commonly used method.

```python
communities = nx.community.louvain_communities(G, weight="weight", resolution=1, seed=None)
# Returns list of frozensets: [{0, 1, 2}, {3, 4}, ...]

# Multi-level partition
partition = nx.community.louvain_partitions(G, weight="weight", resolution=1, seed=None)
# Returns generator of partitions at each level
```

- `resolution < 1` favors larger communities; `> 1` favors smaller
- Deterministic with `seed`; stochastic otherwise
- Handles self-loops as pre-reduced communities — remove them from input if they don't represent that

## Leiden Method

Refinement of Louvain guaranteeing well-connected communities.

```python
communities = nx.community.leiden_communities(G, weight="weight", resolution=1, seed=None)
```

Similar API to Louvain but produces higher-quality partitions with connected sub-communities.

## Girvan-Newman

Hierarchical divisive method based on edge betweenness.

```python
gn = nx.community.girvan_newman(G, weight="weight")
# Returns generator — each call to next() splits one community

top_level = next(gn)               # two top-level communities
second_level = next(gn)            # four communities
```

- Expensive: O(V·E²) for full hierarchy
- Good for small-to-medium graphs and dendrograms
- Pass `hierarchy=True` to get community tree structure

## Label Propagation

Fast but unstable — results vary across runs.

```python
communities = nx.community.label_propagation_communities(G)
# Returns generator of sets
list(nx.community.label_propagation_communities(G))

# Asynchronous variant
communities = nx.community.asyn_lu_communities(G, seed=None)
```

## Modularity Maximization

```python
partition = nx.community.modularity_max(G, weight="weight", seed=None)
# Returns list of sets via greedy optimization
```

## K-Clique Percolation

Communities based on overlapping k-cliques.

```python
communities = nx.community.kclique_communities(G, k)
# Returns generator of node sets
```

## Local Community Detection

Expand a seed node into its local community.

```python
community = nx.community.expand_community(G, initial_seed)
community = nx.community.local_propagation(G, source, weight="weight", threshold=0.01)
```

## Quality Metrics

```python
# Modularity: [-0.5, 1], higher is better
q = nx.community.modularity(G, communities, weight="weight")

# Coverage: how many edges are intra-community
cov = nx.community.coverage(G, communities, weight="weight")

# Performance: balance of modularity and coverage
perf = nx.community.performance(G, communities)
```

## Working with Community Partitions

```python
# Convert list of sets to dict (node → community_id)
communities = [{0, 1}, {2, 3, 4}]
partition = {node: i for i, comm in enumerate(communities) for node in comm}

# Set community as node attribute
for i, comm in enumerate(communities):
    for node in comm:
        G.nodes[node]["community"] = i

# Community subgraphs
for i, comm in enumerate(communities):
    subgraph = G.subgraph(comm)
```

## Key Gotchas

- **Louvain/Leiden are stochastic.** Always pass `seed` for reproducibility.
- **Girvan-Newman is slow.** Use only on graphs up to ~1000 nodes, or use `top_level = next(gn)` for just the first split.
- **Self-loops in Louvain** are treated as pre-aggregated communities. Remove them from input unless intentional.
- **Modularity resolution parameter:** default `resolution=1` may miss small communities. Try `resolution=2` or higher for finer granularity.
- **Disconnected graphs:** label propagation and Louvain work per-component naturally. Girvan-Newman operates on the whole graph.

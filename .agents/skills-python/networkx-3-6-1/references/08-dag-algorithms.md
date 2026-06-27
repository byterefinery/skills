# DAG Algorithms

All functions assume the input is a DAG (directed acyclic graph). They do not check for cycles — verify with `is_directed_acyclic_graph` first.

## Cycle Detection

```python
nx.is_directed_acyclic_graph(DG)                # bool
```

## Topological Sort

```python
# Returns iterator over nodes in topological order
for node in nx.topological_sort(DG):
    ...

# As list
order = list(nx.topological_sort(DG))

# Lexicographic (sort by node label at each step)
order = list(nx.lexicographical_topological_sort(DG))

# All possible topological orders (generator, exponential in worst case)
for ordering in nx.all_topological_sorts(DG):
    ...

# Topological generations (parallel layers)
generations = list(nx.topological_generations(DG))
# [[layer0_nodes], [layer1_nodes], ...]
```

## Ancestors and Descendants

```python
desc = nx.descendants(DG, source)               # set of reachable nodes
ance = nx.ancestors(DG, target)                  # set of nodes that can reach target
```

The source/target node itself is not included in the result.

## Transitive Closure and Reduction

```python
# Add edges for all reachability relationships
closure = nx.transitive_closure(DG)              # returns new DiGraph
nx.transitive_closure_dag(DG)                    # same, optimized for DAGs

# Remove redundant edges (keep minimal edge set with same reachability)
reduction = nx.transitive_reduction(DG)          # returns new DiGraph
```

## Longest Path in DAG

Uses Bellman-Ford internally. O(V + E).

```python
path = nx.dag_longest_path(DG, weight=None)
length = nx.dag_longest_path_length(DG, weight=None)
```

With `weight="weight"` on edges, finds the longest weighted path. Without weight, finds the path with most edges.

## Aperiodicity

```python
nx.is_aperiodic(G)                               # bool — no cyclic structure
```

## DAG to Branching (Arborescence)

```python
branching = nx.dag_to_branching(DG)             # returns DiGraph tree
```

Converts a DAG into a branching (directed tree) preserving reachability.

## Antichains

```python
antichains_list = list(nx.antichains(DG))        # list of sets
```

An antichain is a set of nodes where no two are comparable (no path between any pair).

## Key Gotchas

- **None of these functions check for cycles.** If the graph has a cycle, `topological_sort` raises `NetworkXUnfeasible`. Always verify with `nx.is_directed_acyclic_graph()` first.
- **`all_topological_sorts` can be exponential.** Only use on small DAGs. For large DAGs, use `topological_sort` for a single valid ordering.
- **`descendants` and `ancestors` exclude the source node.** Include it manually: `nx.descendants(DG, s) | {s}`.
- **`dag_longest_path` uses negative weights internally** with Bellman-Ford. Edge weights must be non-negative for meaningful results (or the "longest" path may exploit negative edges).
- **`transitive_reduction` of a non-minimal DAG** removes all edges implied by transitivity, leaving the minimal edge set preserving reachability.

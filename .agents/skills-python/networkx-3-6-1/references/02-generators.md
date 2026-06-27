# Graph Generators

## Classic Graphs

All return `nx.Graph` unless `create_using` specifies otherwise.

```python
nx.empty_graph(n)                           # n isolated nodes
nx.null_graph()                             # 0 nodes, 0 edges
nx.trivial_graph()                          # 1 node, 0 edges
nx.path_graph(n)                            # 0-1-2-...-(n-1)
nx.cycle_graph(n)                           # cycle of n nodes
nx.complete_graph(n)                        # K_n, all pairs connected
nx.complete_multipartite_graph(n1, n2, ...) # complete multipartite
nx.star_graph(n)                            # center 0 connected to 1..n
nx.wheel_graph(n)                           # hub + cycle of n-1 nodes
nx.ladder_graph(n)                          # two paths with rungs
nx.circular_ladder_graph(n)                 # ladder wrapped into a ring
nx.barbell_graph(m, n)                      # two K_m connected by path of n
nx.lollipop_graph(m, n)                     # K_m + path of n from one node
nx.tadpole_graph(m, n)                      # cycle m + path n from one node
nx.circulant_graph(n, connections)          # each i connected to (i±j) mod n
```

### Trees

```python
nx.balanced_tree(r, h)                      # r-ary tree of height h
nx.full_rary_tree(r, n)                     # full r-ary tree with n nodes
nx.binomial_tree(k)                         # binomial tree of order k
nx.random_labeled_tree(n, seed=None)        # random labeled tree on n nodes
```

## Random Graphs

### Erdős-Rényi Models

```python
nx.gnp_random_graph(n, p, seed=None, directed=False)   # G(n,p): each edge with prob p
nx.fast_gnp_random_graph(n, p, seed=None, directed=False)  # faster for sparse graphs
nx.gnm_random_graph(n, m, seed=None, directed=False)    # G(n,m): exactly m edges
nx.dense_gnm_random_graph(n, m, seed=None)               # faster for dense graphs
nx.erdos_renyi_graph(n, p, seed=None, directed=False)   # alias; picks fast vs slow
```

### Small-World Networks

```python
nx.watts_strogatz_graph(n, k, p, seed=None)           # rewired ring lattice
nx.newman_watts_strogatz_graph(n, k, p, seed=None)    # add edges instead of rewiring
nx.connected_watts_strogatz_graph(n, k, p, seed=None) # guarantees connectivity
```

### Scale-Free Networks

```python
nx.barabasi_albert_graph(n, m, seed=None)              # preferential attachment
nx.dual_barabasi_albert_graph(n, m, seed=None)         # age-based preferential
nx.extended_barabasi_albert_graph(n, m, seed=None)     # with initial attractiveness
nx.powerlaw_cluster_graph(n, m, p, seed=None)          # scale-free + clustering
```

### Random Regular

```python
nx.random_regular_graph(d, n, seed=None)               # d-regular graph on n nodes
```

## Geometric Graphs

```python
nx.icosahedral_graph()                                  # icosahedron
nx.dorogovtsev_goltsev_mendes_graph(n, seed=None)      # hierarchical
```

## Social Network Graphs

```python
nx.davis_southern_women_graph()                         # Davis' Southern Women
nx.karate_club_graph()                                  # Zachary's Karate Club
nx.davis_kleats_graph()                                 # Davis' Kleat attendance
nx.flights_graph()                                      # US airline routes
nx.petersen_graph()                                     # Petersen graph
```

## Lattice and Grid

```python
nx.grid_2d_graph(m, n)                                  # m x n grid
nx.lattice.pyper_grid_graph(dim, periodic=False)        # d-dimensional toroidal lattice
```

## Expansion Graphs

```python
nx.random_cluster_graph(cluster_size, num_clusters, seed=None)
```

## Special Graphs

```python
nx.atlas.graph_atlas_create()                           # all graphs up to 7 nodes
nx.turan_graph(n, r)                                    # Turán graph (max edges without K_{r+1})
nx.kneser_graph(n, k)                                   # Kneser graph
nx.mycielski_graph(steps)                               # Mycielskian construction
nx.harary_graph(n, k)                                   # Harary graph (min k-connected)
```

## Community/Planted Partition

```python
nx.generators.community.connected_caveman_graph(l, k)   # l communities of size k
nx.generators.community.caveman_graph(l, k)             # possibly disconnected
nx.generators.community.gaussian_random_partition_graph(
    n, avg_degree, sigma, seed=None)                     # Gaussian partition
```

## Key Parameters

- **`seed`**: Pass an integer for reproducible random graphs. Accepts `int`, `random.Random`, or `numpy.random.Generator`.
- **`create_using`**: Force a specific graph class. E.g., `nx.path_graph(5, create_using=nx.DiGraph)`.
- Node labels are integers `0` through `n-1` by default for most generators.

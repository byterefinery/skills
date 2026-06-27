# Drawing and Layout

## Quick Drawing (Matplotlib)

Requires `matplotlib` and `numpy`.

```python
import matplotlib.pyplot as plt
import networkx as nx

G = nx.path_graph(6)
nx.draw(G)                              # default: spring layout, small nodes
plt.show()
```

### Fine-Grained Control

```python
pos = nx.spring_layout(G, seed=42)      # compute positions separately

nx.draw_networkx_nodes(G, pos, node_size=500, node_color="lightblue",
                       cmap=plt.cm.Blues)
nx.draw_networkx_edges(G, pos, width=2.0, edge_color="gray",
                       style="dashed")
nx.draw_networkx_labels(G, pos, font_size=16, font_weight="bold")
nx.draw_networkx_edge_labels(G, pos, font_size=10)

plt.axis("off")
plt.show()
```

### Convenience Draw Functions

Each combines a layout with `draw_networkx()`:

```python
nx.draw_circular(G)                      # circular_layout + draw
nx.draw_kamada_kawai(G)                  # kamada_kawai_layout + draw
nx.draw_random(G)                        # random_layout + draw
nx.draw_spectral(G)                      # spectral_layout + draw
nx.draw_spring(G)                        # spring_layout + draw
nx.draw_planar(G)                        # planar_layout + draw
nx.draw_shell(G, nlist=[[0,1,2],[3,4,5]])  # shell_layout + draw
nx.draw_forceatlas2(G)                   # forceatlas2_layout + draw
nx.draw_bipartite(G, nodes)              # bipartite_layout + draw
```

## Layout Algorithms

All return `dict` mapping node → (x, y) coordinates.

### Force-Directed

```python
pos = nx.spring_layout(G, k=None, center=None, dim=2,
                       seed=None, iterations=50)
# Fruchterman-Reingold force-directed layout
# k: optimal distance between nodes (auto if None)

pos = nx.fruchterman_reingold_layout(G, k=None, pos=None,
                                     iter=50, seed=None)
# More control: initial positions via `pos`, early exit

pos = nx.forceatlas2_layout(G, pos=None, iterations=100, seed=None)
# ForceAtlas2 algorithm (good for large graphs)
```

### Spectral

```python
pos = nx.spectral_layout(G, weight="weight", max_iter=100, seed=None)
# Uses eigenvectors of Laplacian
pos = nx.spectral_partition(G, k=2, weight="weight")
# Spectral partitioning into k groups
```

### Geometric

```python
pos = nx.circular_layout(G)              # nodes on a circle
pos = nx.planar_layout(G)                # planar embedding (planar graphs only)
pos = nx.random_layout(G, center=None, dim=2, seed=None)
pos = nx.shell_layout(G, nlist=None, rotate=False, dim=2)
# shell_layout: nlist = list of lists, each inner list is one shell
```

### Specialized

```python
pos = nx.bipartite_layout(G, nodes)      # two columns (top/bottom sets)
pos = nx.multipartite_layout(G, subset_key="subset")
pos = nx.bfs_layout(G, root, orientation="tb")  # bfs tree layout
# orientation: "tb" (top-bottom), "lr" (left-right), "rl", "bt"
pos = nx.arf_layout(G, pos=None, y="random", seed=None)
# Adaptive Random Forest layout
pos = nx.kamada_kawai_layout(G, weight="weight", iter=50, dim=2, seed=None)
# Kamada-Kawai: minimizes difference between graph and Euclidean distance
pos = nx.spiral_layout(G, resolution=1.0, equidistant=False, start_angle=0)
```

### Rescaling

```python
pos = nx.rescale_layout(pos, scale=1.0, center=None)
# Rescale positions to fit in [-scale, scale]^dim
```

## Graphviz / PyDot Export

Requires `pygraphviz` or `pydot`.

```python
# Using pygraphviz (nx_agraph)
A = nx.nx_agraph.to_agraph(G)
A.draw("output.png", prog="dot")           # render with Graphviz

# Using pydot (nx_pydot)
P = nx.nx_pydot.to_pydot(G)
P.write_png("output.png")
```

### Layout from Graphviz

```python
pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
pos = nx.nx_agraph.graphviz_layout(G, prog="neato")
pos = nx.nx_agraph.graphviz_layout(G, prog="fdp")
# Progs: dot, neato, fdp, twopi, circo, nop
```

## Key Gotchas

- **`nx.draw()` requires Matplotlib.** It will raise `ImportError` if matplotlib is not installed.
- **Layout functions require NumPy.** All `*_layout()` functions need numpy.
- **`spring_layout` is stochastic.** Pass `seed` for reproducible layouts.
- **`planar_layout` raises on non-planar graphs.** Check `nx.check_planarity(G)` first.
- **For large graphs (>1000 nodes),** `spring_layout` is slow. Use `forceatlas2_layout` or `random_layout` for speed.
- **Graphviz drawing (`nx_agraph`, `nx_pydot`) requires external dependencies:** `pygraphviz` (needs Graphviz C library) or `pydot` (pure Python wrapper).
- **Node colors from centrality:** use `apply_matplotlib_colors()` or manually map values to a colormap:
  ```python
  import matplotlib.cm as cm
  import numpy as np
  centrality = nx.degree_centrality(G)
  colors = cm.viridis(np.array(list(centrality.values())) / max(centrality.values()))
  nx.draw(G, pos, node_color=colors)
  ```

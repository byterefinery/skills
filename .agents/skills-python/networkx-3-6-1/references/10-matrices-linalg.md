# Matrices and Linear Algebra

All matrix functions return SciPy sparse arrays by default. Requires NumPy and SciPy.

## Adjacency Matrix

```python
A = nx.adjacency_matrix(G, nodelist=None, weight=None)
# Sparse matrix; A[i,j] = 1 (or edge weight) if edge exists
```

## Laplacian Matrices

### Combinatorial (Unnormalized)

```python
L = nx.laplacian_matrix(G, nodelist=None, weight="weight")
# L = D - A, where D is degree matrix
```

### Normalized

```python
L_sym = nx.normalized_laplacian_matrix(G, weight="weight")
# L = I - D^(-1/2) A D^(-1/2) (symmetric normalized)
```

### Directed Laplacians

```python
L_rw = nx.directed_laplacian_matrix(G, weight="weight")
# Random-walk Laplacian: I - D^(-1) A

L_comb = nx.directed_combinatorial_laplacian_matrix(G, weight="weight")
# Out-degree based combinatorial Laplacian
```

## Incidence Matrix

```python
B = nx.incidence_matrix(G, nodelist=None, edgelist=None,
                        oriented=False, weight=None)
# Rows = nodes, columns = edges
# oriented=True: -1 for tail, +1 for head (directed: follows edge direction)
```

## Attribute Matrix

```python
A = nx.attr_matrix(G, nodelist=None, attrs=None)
# A[i,j] = product of attr values on edge (i,j); useful for weighted analysis
```

## Modularity Matrix

```python
Q = nx.modularity_matrix(G, weight="weight")
# Used in spectral community detection
```

## Bethe Hessian Matrix

```python
H = nx.bethe_hessian_matrix(G, t=1.0, weight="weight")
# Used for overlapping community detection
```

## Spectral Analysis

```python
# Eigenvalues of various matrices
evals = nx.laplacian_spectrum(G, weight="weight")
evals = nx.adjacency_spectrum(G, weight="weight")
evals = nx.normalized_laplacian_spectrum(G, weight="weight")
evals = nx.modularity_spectrum(G, weight="weight")
evals = nx.bethe_hessian_spectrum(G, t=1.0, weight="weight")
```

## Algebraic Connectivity

Fiedler value (second smallest Laplacian eigenvalue).

```python
ac = nx.algebraic_connectivity(G, weight="weight", tol=0)
# Higher values → more connected graph
# 0 for disconnected graphs
```

## Key Properties

- **Laplacian eigenvalues:** always non-negative. Multiplicity of eigenvalue 0 equals number of connected components.
- **Algebraic connectivity** (Fiedler value): measures how well-connected a graph is. Zero iff disconnected.
- **Normalized Laplacian eigenvalues** are in `[0, 2]`. Eigenvalue 2 appears iff the graph has a bipartite component.
- **Adjacency matrix spectra** relate to random walks: `A^k[i,j]` counts walks of length k from i to j.

## Key Gotchas

- All matrix functions require **NumPy and SciPy**. They will fail with import errors if these are not installed.
- **`nodelist` parameter controls row/column ordering.** Without it, order follows `G.nodes()`. Pass a sorted list for deterministic output.
- **Sparse matrices use significant memory** for dense graphs. For small graphs (<1000 nodes), NumPy arrays may be more convenient.
- **`laplacian_spectrum` returns a dense NumPy array** of eigenvalues, not the matrix itself. Use `laplacian_matrix` for the actual matrix.
- **For MultiGraphs**, edge weights are summed in adjacency and Laplacian matrices by default.

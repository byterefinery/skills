# scipy.sparse Reference

Sparse matrix/array storage and sparse linear algebra.

## Table of Contents

- [Sparse Array Classes](#sparse-array-classes)
- [Construction Functions](#construction-functions)
- [Combining Arrays](#combining-arrays)
- [Sparse Tools](#sparse-tools)
- [Sparse Linear Algebra (scipy.sparse.linalg)](#sparse-linear-algebra-sciypysparselinalg)
- [Compressed Sparse Graph (scipy.sparse.csgraph)](#compressed-sparse-graph-sciypysparsecsg)
- [Array vs Matrix: Key Differences](#array-vs-matrix-key-differences)

## Sparse Array Classes

Use `_array` classes for new code (not `_matrix`). Each format has different strengths.

| Class | Format | Best For |
|---|---|---|
| `csr_array` | Compressed Sparse Row | Fast row slicing, matrix operations, arithmetic |
| `csc_array` | Compressed Sparse Column | Fast column slicing, linear algebra solvers |
| `coo_array` | COOrdinate (triplet) | Construction (fast to build), duplicate handling |
| `bsr_array` | Block Sparse Row | Block-structured matrices |
| `dia_array` | DIAgonal | Matrices with data on diagonals |
| `dok_array` | Dictionary Of Keys | Incremental construction (item assignment) |
| `lil_array` | List Of Lists | Incremental construction (row-wise) |

```python
from scipy.sparse import csr_array, coo_array, csc_array
import numpy as np

# From COO format (row indices, col indices, values)
row = np.array([0, 1, 2, 0])
col = np.array([0, 1, 2, 2])
data = np.array([1, 2, 3, 4])
sparse_coo = coo_array((data, (row, col)), shape=(3, 3))

# Convert to CSR for arithmetic
sparse_csr = sparse_coo.tocsr()

# From dense array
dense = np.array([[1, 0, 0], [0, 5, 0], [0, 0, 6]])
sparse_from_dense = csr_array(dense)
```

### Common attributes and methods

| Attribute/Method | Description |
|---|---|
| `.shape` | (rows, cols) |
| `.nnz` | Number of stored elements (nonzero + explicit zeros) |
| `.data` | Non-zero values (format-dependent) |
| `.indices` / `.indptr` | CSR/CSC structure arrays |
| `.coords` | COO coordinate arrays |
| `.toarray()` | Convert to dense NumPy array |
| `.tocsr()` / `.tocsc()` / `.tocoo()` | Format conversion |
| `.eliminate_zeros()` | Remove explicit zero entries |
| `.has_canonical_format` | Whether format is canonical (no duplicates) |
| `.sum(axis=None)` | Sum along axis or total |
| `.mean(axis=None)` | Mean along axis |

## Construction Functions

| Function | Description |
|---|---|
| `diags_array(diagonals, offsets=0)` | Sparse array from diagonals |
| `eye_array(m, n=None, k=0)` | Sparse identity-like array |
| `random_array(m, n, density=0.01, format='csr')` | Random sparse array |
| `block_array(blocks)` | Build from sub-blocks |

```python
from scipy.sparse import diags_array, eye_array, random_array

# Tridiagonal matrix
A = diags_array([1, -2, 1], offsets=[-1, 0, 1], shape=(5, 5), format='csr')

# Identity
I = eye_array(5)

# Random sparse
R = random_array(100, 100, density=0.01)
```

## Combining Arrays

| Function | Description |
|---|---|
| `kron(A, B)` | Kronecker product |
| `kronsum(A, B)` | Kronecker sum (A⊗I + I⊗B) |
| `block_diag(mats)` | Block diagonal array |
| `tril(A, k=0)` | Lower triangular portion |
| `triu(A, k=0)` | Upper triangular portion |
| `hstack(arrays)` | Horizontal stack |
| `vstack(arrays)` | Vertical stack |
| `swapaxes(A, axis1, axis2)` | Swap axes |
| `expand_dims(A, axis)` | Add new axis |
| `permute_dims(A, axes)` | Reorder axes |

## Sparse Tools

| Function | Description |
|---|---|
| `issparse(x)` | Check if sparse |
| `find(A)` | Return `(row, col, data)` triple |
| `mkdiags(data, offsets, m, n)` | Build from diagonals (legacy) |
| `tril_matrix_vector(tril_mat, vec)` | Matrix-vector product with lower triangular |
| `sparray(x)` | Sparse array base class |

## Sparse Linear Algebra (scipy.sparse.linalg)

### Abstract linear operators

| Class/Function | Description |
|---|---|
| `LinearOperator(shape, matvec, rmatvec=None, ...)` | Abstract representation of a linear operator |
| `aslinearoperator(A)` | Convert matrix/array to LinearOperator |

```python
from scipy.sparse.linalg import LinearOperator

# Define A implicitly (e.g., A @ x = some_function(x))
def matvec(x):
    return np.roll(x, 1) + 2 * x

Op = LinearOperator(shape=(n, n), matvec=matvec)
```

### Matrix operations

| Function | Description |
|---|---|
| `inv(A)` | Sparse matrix inverse (returns dense!) |
| `expm(A)` | Sparse matrix exponential |
| `expm_multiply(A, B)` | e^A @ B without forming e^A |
| `funm_multiply_krylov(A, f, b)` | Krylov method for f(A)b |
| `matrix_power(A, n)` | A^n by repeated squaring |
| `norm(A, ord=None)` | Sparse matrix norm |
| `onenormest(A)` | Estimate 1-norm of sparse matrix |

### Direct solvers

| Function | Description |
|---|---|
| `spsolve(A, b)` | Solve Ax = b (SuperLU direct solver) |
| `spsolve_triangular(A, b, lower=False)` | Triangular solve |
| `is_sptriangular(A)` | Check if sparse A is triangular |
| `spbandwidth(A)` | Find bandwidth of sparse matrix |
| `factorized(A)` | Pre-factorize; returns function for repeated solves |

```python
from scipy.sparse.linalg import spsolve, factorized

# Single solve
x = spsolve(A, b)

# Multiple right-hand sides (pre-factorize once)
solve_func = factorized(A)
x1 = solve_func(b1)
x2 = solve_func(b2)
```

### Iterative solvers

| Function | Description | Best For |
|---|---|---|
| `cg(A, b, M=None)` | Conjugate Gradient | Symmetric positive definite |
| `gmres(A, b, M=None)` | Generalized MINRES | General (non-symmetric) |
| `bicg(A, b)` | Biconjugate Gradient | General, memory-efficient |
| `bicgstab(A, b)` | BiCGSTAB | General, more stable than bicg |
| `cgs(A, b)` | Conjugate Gradient Squared | General |
| `minres(A, b, M=None)` | Minimum Residual | Symmetric (indefinite OK) |
| `qmr(A, b, M=None)` | Quasi-MINRES | Symmetric |
| `lgmres(A, b)` | LGMRES | Restartable GMRES |
| `gcrotmk(A, b)` | GCROT(m,k) | General |
| `tfqmr(A, b)` | Transpose-Free QMR | General |

```python
from scipy.sparse.linalg import gmres, cg

# With preconditioner (M ≈ A^{-1} or M = Cholesky factor)
x, info = gmres(A, b, M=preconditioner, tol=1e-6)
# info: 0 = converged
```

### Iterative least-squares

| Function | Description |
|---|---|
| `lsqr(A, b)` | Least-squares via CGLS |
| `lsmr(A, b, atol=1e-6, btol=1e-6)` | LSMR algorithm (often more stable) |

### Eigenvalue problems

| Function | Description |
|---|---|
| `eigs(A, k=6, which='LM')` | k eigenvalues/vectors of general sparse A |
| `eigsh(A, k=6, which='LM')` | k eigenvalues/vectors of symmetric sparse A |
| `lobpcg(A, X, B=None)` | LOBPCG for symmetric partial eigenproblems |

**`which` options:** `'LM'` (largest magnitude), `'SM'` (smallest magnitude), `'LA'` (largest algebraic), `'SA'` (smallest algebraic), `'BE'` (both ends).

```python
from scipy.sparse.linalg import eigs, eigsh

# Largest 10 eigenvalues
eigenvalues, eigenvectors = eigs(A, k=10, which='LM')

# Smallest eigenvalue of symmetric matrix
eigenvalues, eigenvectors = eigsh(H, k=1, which='SA')
```

### Singular value problems

| Function | Description |
|---|---|
| `svds(A, k=6, which='LM')` | k singular values/vectors of sparse A |

Solvers: `'arpack'` (default), `'lobpcg'`, `'propack'`.

### Matrix factorizations

| Function | Description |
|---|---|
| `splu(A)` | LU decomposition (returns SuperLU object) |
| `spilu(A, drop_tol=1e-4)` | Incomplete LU (use as preconditioner) |
| `SuperLU` | Object representing an LU factorization |

```python
from scipy.sparse.linalg import spilu

# Incomplete LU as preconditioner for iterative solver
ilut = spilu(A)
x, info = gmres(A, b, M=ilut.aslinearoperator())
```

### Sparse arrays with structure

| Class | Description |
|---|---|
| `LaplacianNd(shape)` | Laplacian on uniform rectangular grid in N dimensions |

## Compressed Sparse Graph (scipy.sparse.csgraph)

Graph algorithms on sparse adjacency matrices.

| Function | Description |
|---|---|
| `connected_components(csgraph, directed=True)` | Count and label connected components |
| `shortest_path(csgraph, method='D', ...)` | Shortest paths (Dijkstra, Bellman-Ford, Johnson, Floyd-Warshall) |
| `dijkstra(csgraph, indices=None, ...)` | Dijkstra's algorithm |
| `bellman_ford(csgraph, ...)` | Bellman-Ford algorithm |
| `floyd_warshall(csgraph)` | All-pairs shortest paths |
| `djikstra` | Alias for dijkstra |
| `minimum_spanning_tree(csgraph)` | Minimum spanning tree |
| `maximum_flow(csgraph, s, t)` | Maximum flow (push-relabel) |
| `laplacian(csgraph, normed=False)` | Graph Laplacian |
| `csgraph_from_dense(dense)` / `csgraph_to_dense(csgraph)` | Dense ↔ sparse graph conversion |

## Array vs Matrix: Key Differences

| Feature | `_array` (new) | `_matrix` (legacy) |
|---|---|---|
| `A * B` | Element-wise multiplication | Matrix multiplication |
| `A @ B` | Matrix multiplication | Matrix multiplication |
| `A[:, i]` | Returns 1-D array | Returns 2-D matrix |
| Slicing | NumPy-compatible | Matrix-specific behavior |

**Always use `_array` classes for new code.** The `_matrix` classes are deprecated.

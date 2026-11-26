# scipy.sparse Reference (1.18.1)

Sparse array storage and operations, sparse linear algebra (`scipy.sparse.linalg`), and graph algorithms (`scipy.sparse.csgraph`).

## Table of Contents

- [Sparse Array Classes](#sparse-array-classes)
- [Construction Functions](#construction-functions)
- [Combining Arrays](#combining-arrays)
- [Sparse Tools](#sparse-tools)
- [Sparse Linear Algebra (scipy.sparse.linalg)](#sparse-linear-algebra-sciypysparselinalg)
- [Compressed Sparse Graph (scipy.sparse.csgraph)](#compressed-sparse-graph-sciypysparsecsg)
- [Version Notes (1.18)](#version-notes-118)

## Sparse Array Classes

**`scipy.sparse` is shifting from the sparse *matrix* (`spmatrix`) interface to the sparse *array* (`sparray`) interface; `spmatrix` is deprecated and will be removed in a future release.** Use the `*_array` classes for new code.

Each format has different strengths (user guide):

| Class | Format | Best For |
|---|---|---|
| `csr_array` | Compressed Sparse Row | Fast arithmetic, vector products, row slicing |
| `csc_array` | Compressed Sparse Column | Fast arithmetic, vector products, column slicing |
| `coo_array` | COOrdinate (triplet) | Simple construction, in-place modification, fast conversion to other formats |
| `dok_array` | Dictionary Of Keys | Fast construction and single-element access |
| `lil_array` | List Of Lists | Fast construction and row-wise modification |
| `dia_array` | DIAgonal | Efficient when data lies along diagonals (**not subscriptable** — `dia[2, 2]` raises) |
| `bsr_array` | Block Sparse Row | Block-structured data |

```python
from scipy.sparse import csr_array, coo_array
import numpy as np

# From COO format (values, (row, col)), shape
row = np.array([0, 1, 2, 0])
col = np.array([0, 1, 2, 2])
data = np.array([1, 2, 3, 4])
sparse_coo = coo_array((data, (row, col)), shape=(3, 3))

# Convert to CSR for arithmetic
sparse_csr = sparse_coo.tocsr()

# From dense
dense = np.array([[1, 0, 0], [0, 5, 0], [0, 0, 6]])
sparse_from_dense = csr_array(dense)
```

**Key behaviors:**
- Zeros are *implicit*; only stored values are explicit. `.nnz` = number of stored elements.
- Reductions along an axis return dense `ndarray`s (e.g. `sparse.mean(axis=1)`).
- Operations may **silently change format**: COO `@` COO returns CSR. SciPy converts formats internally for efficiency.

### Common attributes and methods

| Attribute/Method | Description |
|---|---|
| `.shape` | (rows, cols) |
| `.nnz` | Number of stored elements |
| `.data` | Stored values (format-dependent) |
| `.indices` / `.indptr` | CSR/CSC structure arrays |
| `.toarray()` | Convert to dense NumPy array |
| `.tocsr()` / `.tocsc()` / `.tocoo()` / `.todok()` / `.tolil()` / `.todia()` / `.tobsr()` | Format conversion |
| `.eliminate_zeros()` | Remove explicit zero entries |
| `.has_canonical_format` | Whether the format is canonical (no duplicates/unsorted) |

## Construction Functions

| Function | Description |
|---|---|
| `diags_array(diagonals, offsets=0)` | Sparse array from diagonals |
| `eye_array(m, n=None, k=0)` | Sparse identity-like array |
| `random_array(m, n, density=0.01, format='csr', ...)` | Random sparse array |
| `block_array(blocks)` | Build from sub-blocks |

```python
from scipy.sparse import diags_array, eye_array, random_array

A = diags_array([1, -2, 1], offsets=[-1, 0, 1], shape=(5, 5), format='csr')  # tridiagonal
I = eye_array(5)
R = random_array(100, 100, density=0.01)
```

## Combining Arrays

| Function | Description |
|---|---|
| `kron(A, B)` | Kronecker product |
| `kronsum(A, B)` | Kronecker sum (A⊗I + I⊗B) |
| `block_diag(mats)` | Block diagonal array |
| `tril(A, k=0)` / `triu(A, k=0)` | Lower / upper triangular portion |
| `hstack(arrays)` / `vstack(arrays)` | Horizontal / vertical stack |
| `swapaxes(A, axis1, axis2)` / `expand_dims(A, axis)` / `permute_dims(A, axes)` | Axis manipulation |

**1.18.0 deprecation:** `kron`, `kronsum`, `block_diag` return `spmatrix` when no inputs are sparse — that is deprecated; the return type will change to `sparray`. Ensure at least one sparse input to control the output type.

## Sparse Tools

| Function | Description |
|---|---|
| `issparse(x)` | Check if sparse |
| `find(A)` | Return `(row, col, data)` triple |
| `sparray(x)` | Convert to a sparse array |

## Sparse Linear Algebra (scipy.sparse.linalg)

### Abstract linear operators

| Class/Function | Description |
|---|---|
| `LinearOperator(shape, matvec, rmatvec=None, ...)` | Abstract linear operator defined by `matvec` (and optional `rmatvec`/`adjoint`) |
| `aslinearoperator(A)` | Convert matrix/array to `LinearOperator` |
| `LaplacianNd(shape, ...)` | Laplacian on a uniform rectangular grid |

**Note (1.18.0):** calling `matvec` on column-vector input now emits a `FutureWarning` — use `matmat` instead (also extends to batch dimensions).

```python
from scipy.sparse.linalg import LinearOperator
Op = LinearOperator(shape=(n, n), matvec=lambda x: np.roll(x, 1) + 2 * x)
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
| `onenormest(A)` | Estimate the 1-norm of a sparse matrix |
| `traceest(A)` | Trace estimation |

### Direct solvers

| Function | Description |
|---|---|
| `spsolve(A, b)` | Solve Ax = b (SuperLU direct solver) |
| `spsolve_triangular(A, b, lower=False)` | Triangular solve |
| `factorized(A)` | Pre-factorize; returns a function for repeated solves |
| `splu(A)` / `spilu(A, drop_tol=1e-4)` | LU / incomplete LU factorization (`spilu` works as a preconditioner) |
| `SuperLU` | Object representing an LU factorization |
| `use_solver(...)` | Select the direct solver |
| `MatrixRankWarning` | Rank-deficiency warning |

```python
from scipy.sparse.linalg import spsolve, factorized

x = spsolve(A, b)                       # single solve

solve_func = factorized(A)              # pre-factorize once
x1 = solve_func(b1)                     # repeated right-hand sides
```

### Iterative (Krylov) solvers

| Function | Best For |
|---|---|
| `cg(A, b, M=None)` | Symmetric positive definite |
| `minres(A, b, M=None)` | Symmetric (indefinite OK) |
| `bicg(A, b)` / `bicgstab(A, b)` | General (biCGSTAB more stable) |
| `cgs(A, b)` / `qmr(A, b)` / `tfqmr(A, b)` | General |
| `gmres(A, b, M=None)` / `lgmres(A, b)` | General (LGMRES restartable) |
| `gcrotmk(A, b)` | General |

```python
from scipy.sparse.linalg import gmres, cg, spilu

x, info = gmres(A, b, M=spilu(A).aslinearoperator(), tol=1e-6)  # with ILU preconditioner
# info: 0 = converged
```

### Iterative least-squares

| Function | Description |
|---|---|
| `lsqr(A, b)` | Least squares via CGLS |
| `lsmr(A, b, atol=1e-6, btol=1e-6)` | LSMR algorithm (often more stable) |

### Eigenvalue / singular value problems

| Function | Description |
|---|---|
| `eigs(A, k=6, which='LM')` | k eigenvalues/vectors of general sparse A (ARPACK) |
| `eigsh(A, k=6, which='LM')` | k eigenvalues/vectors of symmetric sparse A (ARPACK) |
| `lobpcg(A, X, B=None)` | LOBPCG for large-scale symmetric partial eigenproblems |
| `svds(A, k=6, which='LM')` | k singular values/vectors of sparse A |

`which` options: `'LM'` (largest magnitude), `'SM'` (smallest magnitude), `'LA'` (largest algebraic), `'SA'` (smallest algebraic), `'BE'` (both ends). Errors: `ArpackError`, `ArpackNoConvergence`.

## Compressed Sparse Graph (scipy.sparse.csgraph)

Graph algorithms on sparse-adjacency arrays (see the user guide "Word Ladders" example).

| Function | Description |
|---|---|
| `connected_components(csgraph, directed=True)` | Count and label connected components |
| `shortest_path(csgraph, method='D', ...)` | Shortest paths (methods for Dijkstra/Bellman-Ford/Johnson/Floyd-Warshall) |
| `dijkstra(csgraph, indices=None, ...)` | Dijkstra's algorithm |
| `bellman_ford(csgraph, ...)` | Bellman-Ford (raises `NegativeCycleError` on negative cycles) |
| `floyd_warshall(csgraph)` | All-pairs shortest paths |
| `johnson(csgraph, ...)` | Johnson's algorithm (sparse graphs) |
| `reconstruct_path(u, v, pred)` | Reconstruct a path from a predecessor matrix |
| `construct_dist_matrix(d, ...)` | Build a distance matrix from a predecessor matrix |
| `breadth_first_order(csgraph, ...)` / `breadth_first_tree(csgraph, ...)` | BFS order / tree |
| `depth_first_order(csgraph, ...)` / `depth_first_tree(csgraph, ...)` | DFS order / tree |
| `yen(csgraph, ...)` | k shortest loopless paths |
| `minimum_spanning_tree(csgraph, ...)` | Minimum spanning tree |
| `maximum_bipartite_matching(csgraph)` | Maximum bipartite matching |
| `min_weight_full_bipartite_matching(csgraph)` | Minimum-weight full bipartite matching |
| `maximum_flow(csgraph, s, t, ...)` | Maximum flow |
| `laplacian(csgraph, normed=False)` | Graph Laplacian |
| `structural_rank(csgraph)` | Structural rank |
| `reverse_cuthill_mckee(csgraph, ...)` | Reverse Cuthill-McKee ordering |
| `csgraph_to_dense` / `csgraph_from_dense` / `csgraph_to_masked` / `csgraph_from_masked` | Dense/masked ↔ csgraph conversions |

## Version Notes (1.18)

- **spmatrix → sparray migration** — the `spmatrix` interface is deprecated; the `sparray` interface is the future. Guidance: `scipy.sparse` docs "Migration from spmatrix to sparray".
- `kron`/`kronsum`/`block_diag` return-type change (see Combining Arrays).
- `scipy.io` readers' `spmatrix=True` option is deprecated — sparse I/O now returns sparse arrays.
- `LinearOperator.matvec` on column vectors: `FutureWarning` (use `matmat`).
- Sparse arrays are **mutable and not thread-safe** under concurrent mutation (see the thread-safety user guide).

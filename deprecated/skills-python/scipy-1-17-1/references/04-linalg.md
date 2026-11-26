# scipy.linalg Reference

Dense linear algebra — extends `numpy.linalg` with more methods and consistent behavior.

## Table of Contents

- [Basics](#basics)
- [Eigenvalue Problems](#eigenvalue-problems)
- [Decompositions](#decompositions)
- [Matrix Functions](#matrix-functions)
- [Matrix Equation Solvers](#matrix-equation-solvers)
- [Special Matrices](#special-matrices)
- [Sketches and Random Projections](#sketches-and-random-projections)
- [Low-Level Routines](#low-level-routines)

## Basics

| Function | Description |
|---|---|
| `solve(A, b)` | Solve `Ax = b` (preferred over `inv(A) @ b`) |
| `solve_banded(lu, ab, b)` | Solve banded system |
| `solveh_banded(ab, b)` | Solve Hermitian/symmetric banded system |
| `solve_triangular(A, b, lower=False)` | Solve triangular system |
| `solve_circulant(c, b)` | Solve circulant system |
| `solve_toeplitz(c, b)` | Solve Toeplitz system |
| `matmul_toeplitz(c, v)` | Multiply Toeplitz matrix by vector |
| `inv(A)` | Matrix inverse |
| `det(A)` | Determinant |
| `norm(A, ord=None)` | Matrix/vector norm |
| `lstsq(A, b)` | Linear least squares |
| `pinv(A)` | Moore-Penrose pseudo-inverse (via lstsq) |
| `pinvh(A)` | Pseudo-inverse of Hermitian matrix |
| `khatri_rao(A, B)` | Khatri-Rao product |
| `orthogonal_procrustes(A, B)` | Orthogonal Procrustes problem |
| `matrix_balance(A)` | Balance matrix entries |
| `subspace_angles(A, B)` | Subspace angles between matrices |
| `bandwidth(A, show=False)` | Lower/upper bandwidth |
| `issymmetric(A)` | Check if symmetric |
| `ishermitian(A)` | Check if Hermitian |

```python
from scipy.linalg import solve, inv, det, norm

A = np.array([[3, 1], [1, 2]])
b = np.array([9, 8])
x = solve(A, b)  # preferred over inv(A) @ b
```

## Eigenvalue Problems

| Function | Description |
|---|---|
| `eig(A)` | Eigenvalues and eigenvectors (general) |
| `eigvals(A)` | Eigenvalues only (general) |
| `eigh(A)` | Eigenvalues/vectors (Hermitian/symmetric — faster, real eigenvalues) |
| `eigvalsh(A)` | Eigenvalues only (Hermitian) |
| `eig_banded(ab, ...)` | Banded matrix eigenproblem |
| `eigvals_banded(ab)` | Banded eigenvalues only |
| `eigh_tridiagonal(d, e)` | Tridiagonal Hermitian eigenproblem |
| `eigvalsh_tridiagonal(d, e)` | Tridiagonal eigenvalues only |

```python
from scipy.linalg import eig, eigh

# General matrix
eigenvalues, eigenvectors = eig(A)

# Hermitian/symmetric (faster, guaranteed real eigenvalues)
eigenvalues, eigenvectors = eigh(H)
```

## Decompositions

### LU decomposition

| Function | Description |
|---|---|
| `lu(A)` | Returns `(P, L, U)` factorization |
| `lu_factor(A)` | Returns `(lu, piv)` for use with `lu_solve` |
| `lu_solve(lu_and_piv, b)` | Solve using pre-factored LU |

### Cholesky decomposition

| Function | Description |
|---|---|
| `cholesky(A, lower=True)` | Cholesky: `A = L @ L^H` |
| `cholesky_banded(ab, lower=True)` | Banded Cholesky |
| `cho_factor(A)` | Cholesky for use with `cho_solve` |
| `cho_solve(c_and_low, b)` | Solve using pre-factored Cholesky |
| `cho_solve_banded(c_and_low, b)` | Banded Cholesky solve |

### QR decomposition

| Function | Description |
|---|---|
| `qr(A, mode='economic')` | QR decomposition |
| `qr_multiply(A, x, transpose=False)` | QR and multiply by Q |
| `qr_update(Q, R, x)` | Rank-k QR update |
| `qr_delete(Q, R, i)` | Downdate on row/column deletion |
| `qr_insert(Q, R, x, i)` | Update on row/column insertion |

### Other decompositions

| Function | Description |
|---|---|
| `svd(A, compute_uv=True)` | Singular value decomposition |
| `svdvals(A)` | Singular values only |
| `diagsvd(s, M, N)` | Construct S matrix from singular values |
| `orth(A)` | Orthonormal basis for range of A (via SVD) |
| `null_space(A, rcond=None)` | Orthonormal basis for null space (via SVD) |
| `ldl(A)` | LDL^T decomposition (Hermitian/symmetric) |
| `rq(A)` | RQ decomposition |
| `qz(A, B)` | QZ decomposition of matrix pair |
| `ordqz(A, B)` | QZ with reordering |
| `schur(A)` | Schur decomposition |
| `hessenberg(A)` | Hessenberg form |
| `polar(A)` | Polar decomposition |
| `cossin(U)` | Cosine-sine decomposition |

```python
from scipy.linalg import svd, qr, cholesky, null_space

U, s, Vt = svd(A)
Q, R = qr(A)
L = cholesky(A, lower=True)
N = null_space(A)  # orthonormal basis for Ax=0
```

## Matrix Functions

| Function | Description |
|---|---|
| `expm(A)` | Matrix exponential e^A |
| `logm(A)` | Matrix logarithm |
| `sqrtm(A)` | Matrix square root |
| `fractional_matrix_power(A, z)` | A^z for complex z |
| `signm(A)` | Matrix sign function |
| `cosm(A)`, `sinm(A)`, `tanm(A)` | Trigonometric matrix functions |
| `coshm(A)`, `sinhm(A)`, `tanhm(A)` | Hyperbolic matrix functions |
| `funm(A, f)` | Arbitrary matrix function f(A) |
| `expm_frechet(A, E, method)` | Fréchet derivative of expm |
| `expm_cond(A, method)` | Condition number of expm |

```python
from scipy.linalg import expm, logm, sqrtm

# Matrix exponential (not np.exp(A) which is element-wise!)
exp_A = expm(A)
log_A = logm(A)
sqrt_A = sqrtm(A)
```

## Matrix Equation Solvers

| Function | Description |
|---|---|
| `solve_sylvester(A, B, Q)` | Sylvester equation: AX + XB = Q |
| `solve_continuous_are(A, Q, B, E=None)` | Continuous-time algebraic Riccati |
| `solve_discrete_are(A, Q, B, E=None)` | Discrete-time algebraic Riccati |
| `solve_continuous_lyapunov(A, Q)` | Continuous Lyapunov: AX + XA^H = Q |
| `solve_discrete_lyapunov(A, Q)` | Discrete Lyapunov: AXA^H - X = Q |

## Special Matrices

| Function | Description |
|---|---|
| `circulant(c)` | Circulant matrix from first column |
| `hadamard(n)` | Hadamard matrix of order n |
| `hilb(n)` | Hilbert matrix (n×n) |
| `invhilb(n)` | Inverse Hilbert matrix |
| `pascal(n, kind='symmetric')` | Pascal matrix |
| `triul(A, k=0)` | Upper/lower triangular part |

## Sketches and Random Projections

| Function | Description |
|---|---|
| `random_projection.GaussianRandomProjection` | Gaussian random projection |
| `random_projection.JohnsonLindenstraussTransform` | JL transform with dimension estimate |

## Low-Level Routines

- `scipy.linalg.blas` — BLAS routines (`dot`, `gemm`, `axpy`, etc.)
- `scipy.linalg.lapack` — LAPACK routines (`gesv`, `potrf`, `geev`, etc.)
- `scipy.linalg.cython_blas` — Typed Cython BLAS wrappers
- `scipy.linalg.cython_lapack` — Typed Cython LAPACK wrappers
- `scipy.linalg.interpolative` — Interpolative matrix decompositions (`interpolative_qr`, `id_decomposition`)

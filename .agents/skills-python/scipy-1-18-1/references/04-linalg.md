# scipy.linalg Reference (1.18.1)

Dense linear algebra — extends `numpy.linalg` with more methods and consistent behavior.

## Table of Contents

- [Why scipy.linalg over numpy.linalg](#why-scipy-linalg-over-numpy-linalg)
- [Basics](#basics)
- [Eigenvalue Problems](#eigenvalue-problems)
- [Decompositions](#decompositions)
- [Matrix Functions](#matrix-functions)
- [Matrix Equation Solvers](#matrix-equation-solvers)
- [Special Matrices](#special-matrices)
- [Sketches](#sketches)
- [Batch Support](#batch-support)
- [`overwrite_*` Arguments](#overwrite_-arguments)
- [Low-Level Routines](#low-level-routines)
- [Version Notes (1.18)](#version-notes-118)

## Why scipy.linalg over numpy.linalg

Per the user guide: `scipy.linalg` contains all of `numpy.linalg` plus advanced routines, and is **always compiled with BLAS/LAPACK support** (in NumPy it is optional). Identically named functions may offer more functionality in SciPy. Use `scipy.linalg` unless you want to avoid a SciPy dependency.

## Basics

| Function | Description |
|---|---|
| `solve(A, b)` | Solve `Ax = b` (preferred over `inv(A) @ b`) |
| `solve_banded((l, u), ab, b)` | Solve banded system |
| `solveh_banded(ab, b)` | Solve Hermitian/symmetric banded system |
| `solve_circulant(c, b)` | Solve circulant system |
| `solve_triangular(A, b, lower=False)` | Solve triangular system |
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
| `matrix_balance(A)` | Balance matrix entries with a similarity transformation |
| `subspace_angles(A, B)` | Subspace angles between matrices |
| `bandwidth(A)` | Lower/upper bandwidth (returns `np.int64` pair since 1.18.0) |
| `issymmetric(A)` / `ishermitian(A)` | Symmetry checks |

Errors: `LinAlgError`, `LinAlgWarning`.

## Eigenvalue Problems

| Function | Description |
|---|---|
| `eig(A)` | Eigenvalues and eigenvectors (general) |
| `eigvals(A)` | Eigenvalues only (general; gained `overwrite_b` in 1.18.0) |
| `eigh(A)` | Eigenvalues/vectors, Hermitian/symmetric (faster, real eigenvalues) |
| `eigvalsh(A)` | Eigenvalues only (Hermitian/symmetric) |
| `eig_banded(...)` / `eigvals_banded(...)` | Banded matrix eigenproblem |
| `eigh_tridiagonal(d, e)` / `eigvalsh_tridiagonal(d, e)` | Tridiagonal Hermitian eigenproblem |

## Decompositions

| Function | Description |
|---|---|
| `lu(A)` / `lu_factor(A)` / `lu_solve((lu, piv), b)` | LU decomposition and factored solves |
| `svd(A)` / `svdvals(A)` / `diagsvd(s, M, N)` | SVD, singular values, build S matrix |
| `orth(A)` / `null_space(A, rcond=None)` | Orthonormal basis of range / null space (SVD-based) |
| `ldl(A)` | LDL^T decomposition (Hermitian/symmetric) |
| `cholesky(A)` / `cholesky_banded(...)` | Cholesky (`A = L @ L^H`); leverages symmetry for speed since 1.18.0 |
| `cho_factor(A)` / `cho_solve((c, piv), b)` / `cho_solve_banded(...)` | Factored Cholesky solves |
| `qr(A)` / `qr_multiply(A, x, ...)` / `qr_update` / `qr_delete` / `qr_insert` | QR and rank updates |
| `rq(A)` | RQ decomposition |
| `qz(A, B)` / `ordqz(A, B)` | QZ decomposition (matrix pair) |
| `schur(A)` / `rsf2csf(T, Z)` | Schur decomposition (real/complex form conversion) |
| `hessenberg(A)` | Hessenberg form |
| `polar(A)` | Polar decomposition |
| `cossin(U)` | Cosine-sine decomposition |

**Factored-solve pattern** (factor once, solve many RHS cheaply):

```python
from scipy import linalg
lu, piv = linalg.lu_factor(A)
x = linalg.lu_solve((lu, piv), b)

c, piv = linalg.cho_factor(A)   # A symmetric positive definite
x = linalg.cho_solve((c, piv), b)
```

## Matrix Functions

| Function | Description |
|---|---|
| `expm(A)` | Matrix exponential e^A (not `np.exp(A)` which is element-wise!) |
| `logm(A)` | Matrix logarithm |
| `sqrtm(A)` | Matrix square root |
| `fractional_matrix_power(A, z)` | A^z for complex z |
| `signm(A)` | Matrix sign function |
| `cosm(A)` / `sinm(A)` / `tanm(A)` | Trigonometric matrix functions |
| `coshm(A)` / `sinhm(A)` / `tanhm(A)` | Hyperbolic matrix functions |
| `funm(A, f)` | Arbitrary matrix function f(A) via Schur |
| `expm_frechet(A, E)` | Fréchet derivative of expm |
| `expm_cond(A)` | Condition number of expm |

The `disp=` parameters on `sqrtm`/`logm`/`signm` (and `sqrtm`'s `blocksize`) were **removed in 1.18.0**.

## Matrix Equation Solvers

| Function | Description |
|---|---|
| `solve_sylvester(A, B, Q)` | Sylvester equation: `AX + XB = Q` |
| `solve_continuous_are(A, Q, B, E=None)` | Continuous-time algebraic Riccati |
| `solve_discrete_are(A, Q, B, E=None)` | Discrete-time algebraic Riccati |
| `solve_continuous_lyapunov(A, Q)` | Continuous Lyapunov: `AX + XA^H = Q` |
| `solve_discrete_lyapunov(A, Q)` | Discrete Lyapunov: `AXA^H - X = Q` |

## Special Matrices

| Function | Description |
|---|---|
| `block_diag(mats)` | Block diagonal array |
| `circulant(c)` | Circulant matrix from first column |
| `companion(A)` | Companion matrix |
| `convolution_matrix(v, length)` | Convolution matrix |
| `dft(n, k=None, scale='unscaled')` | DFT matrix (note: distinct from `scipy.fft`) |
| `fiedler(M)` / `fiedler_companion(M)` | Fiedler matrix / companion |
| `hadamard(n)` | Hadamard matrix of order n |
| `hankel(c, r=None)` | Hankel matrix |
| `helmert(n)` | Helmert matrix |
| `hilbert(n)` / `invhilbert(n)` | Hilbert matrix / inverse Hilbert |
| `leslie(lf, sf)` | Leslie population-dynamics matrix |
| `pascal(n, kind='symmetric')` / `invpascal(n)` | Pascal matrix / inverse |
| `toeplitz(c, r=None)` | Toeplitz matrix |

## Sketches

| Function | Description |
|---|---|
| `clarkson_woodruff_transform(X)` | Clarkson-Woodruff random-projection sketch |

## Batch Support

Many functions accept N-D arrays and treat leading dimensions as a batch: a function that takes a 2-D matrix will interpret `(4, 3, 2)` input as a batch of four 3×2 matrices (core shape `(3, 2)`, batch shape `(4,)`). Output shape = input batch shape + core output shape. A function that takes a 1-D vector treats `(4, 3, 2)` as a `(4, 3)` batch of vectors.

## `overwrite_*` Arguments

`overwrite_a=True` / `overwrite_b=True` permit in-place work, but only actually happen when the dtype is LAPACK-compatible (single/double precision float or complex), the array is Fortran-ordered, and (for most functions) 2-D. Measure before relying on it.

## Low-Level Routines

- `scipy.linalg.blas` / `scipy.linalg.lapack` — BLAS/LAPACK wrappers
- `scipy.linalg.cython_blas` / `scipy.linalg.cython_lapack` — typed Cython wrappers for extension modules
- `scipy.linalg.interpolative` — interpolative matrix decompositions
- `get_blas_funcs`, `get_lapack_funcs`, `find_best_blas_type` — discovery helpers
- 1.18.0: three BLAS/LAPACK build modes (LP64-only, ILP64-only, mixed) with machinery for downstream `cython_lapack` consumers

## Version Notes (1.18)

- **Non-LAPACK dtypes deprecated** — `scipy.linalg` functions are stricter in 1.18.0: integers are upcast to float; single/double precision float/complex are the accepted families.
- `bandwidth` now returns `(np.int64, np.int64)` (was `(int, int)`).
- `cho_factor` second return changed from `bool` to `NDArray[np.bool]`.
- `lstsq` residual behavior changed: with `lapack_driver='gesld'/'gelss'` on an overdetermined system a non-empty residual is always returned; for a rank-deficient slice the corresponding residual is `NaN`.
- `cholesky` now leverages symmetry for performance (C batching loop).
- `eigvals` gained `overwrite_b`.

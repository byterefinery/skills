# 04 — Linear Algebra

All routines in `np.linalg` rely on BLAS/LAPACK for efficient computation. For more advanced linear algebra (LU decomposition, Schur decomposition, matrix functions), use `scipy.linalg`.

## Matrix and Vector Products

### Operators and functions

```python
A @ B                  # matrix multiplication (preferred operator)
np.matmul(A, B)        # same as @
np.dot(A, B)           # dot product / matrix multiplication
np.vdot(a, b)          # inner product of flattened arrays (conjugates complex)
np.inner(a, b)         # inner product over last axis
np.outer(a, b)         # outer product
np.tensordot(a, b, axes=1)  # generalized tensor dot
```

### `@` vs `np.dot()`

- `@` / `np.matmul()`: treats 2D arrays as matrices, supports stacking (`(..., M, K) @ (..., K, N)`), promotes 1D to 2D for computation then flattens result
- `np.dot()`: sums product over last axis of first and second-to-last of second; for 1D arrays computes inner product

```python
# Stacked matrix multiplication
A = np.random.randn(4, 3, 8)   # 4 matrices of shape (3, 8)
B = np.random.randn(4, 8, 5)   # 4 matrices of shape (8, 5)
C = A @ B                       # shape (4, 3, 5)
```

### `np.einsum` — Einstein summation

Express complex tensor contractions concisely:

```python
np.einsum('ij,ji->', A, B)           # trace(A @ B)
np.einsum('ij->ji', A)               # transpose
np.einsum('ij,jk->ik', A, B)         # matrix multiplication
np.einsum('ij,ij->i', A, B)          # row-wise dot product
np.einsum('...j,jk->...k', A, B)     # batched matmul with ellipsis
np.einsum('ijk,ilk->jl', A, B)       # contraction over i and k
```

Use `optimize=True` for complex contractions to find optimal evaluation order:
```python
np.einsum('ij,jk,kl->il', A, B, C, optimize=True)
```

## Decompositions

### QR decomposition

```python
Q, R = np.linalg.qr(A)                # economy QR
Q, R = np.linalg.qr(A, mode='raw')    # LAPACK raw output
Q, R = np.linalg.qr(A, mode='complete')  # full QR
```

`A = Q @ R`, where `Q` is orthogonal and `R` is upper triangular.

### SVD (Singular Value Decomposition)

```python
U, s, Vt = np.linalg.svd(A)           # full SVD
U, s, Vt = np.linalg.svd(A, full_matrices=False)  # economy SVD
s = np.linalg.svdvals(A)              # singular values only
```

`A = U @ diag(s) @ Vt`. Singular values `s` are sorted descending.

### Cholesky decomposition

```python
L = np.linalg.cholesky(A)             # A = L @ L^T for positive-definite A
```

Only works for symmetric/Hermitian positive-definite matrices. Raises `LinAlgError` otherwise.

## Eigenvalues and Eigenvectors

```python
w, v = np.linalg.eig(A)               # general eigenvalue problem
w = np.linalg.eigvals(A)              # eigenvalues only
w, v = np.linalg.eigh(A)              # symmetric/Hermitian (faster, real eigenvalues)
w = np.linalg.eigvalsh(A)             # eigenvalues only (symmetric)
```

For `eig()`: `A @ v[:, i] = w[i] * v[:, i]`. For `eigh()`: eigenvalues are real and sorted ascending.

## Solving Equations

### Linear systems

```python
x = np.linalg.solve(A, b)             # solves Ax = b
x = np.linalg.solve(A, B)             # solves AX = B (multiple RHS)
```

Uses LU decomposition internally. More stable and faster than computing `inv(A) @ b`.

### Least squares

```python
x, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
```

Finds minimum-norm solution to `Ax ≈ b` in the least-squares sense. Returns solution, sum of squared residuals, rank, and singular values.

### Matrix inversion (avoid when possible)

```python
A_inv = np.linalg.inv(A)              # exact inverse
A_pinv = np.linalg.pinv(A)            # Moore-Penrose pseudoinverse
A_pinv = np.linalg.pinv(A, rcond=1e-10)  # with custom tolerance
```

Prefer `np.linalg.solve(A, b)` over `np.linalg.inv(A) @ b` — it is more numerically stable and faster.

## Norms and Numbers

```python
np.linalg.norm(a)                     # 2-norm (default)
np.linalg.norm(a, ord=1)              # 1-norm (sum of absolute values)
np.linalg.norm(a, ord=np.inf)         # infinity norm (max absolute value)
np.linalg.norm(A, ord='fro')          # Frobenius norm
np.linalg.norm(A, ord=2)              # spectral norm (largest singular value)
np.linalg.norm(a, axis=0)             # vector norm along axis
```

### Other matrix numbers

```python
np.linalg.det(A)                      # determinant
sign, logdet = np.linalg.slogdet(A)   # sign and log|det| (more stable for large det)
np.linalg.cond(A)                     # condition number
np.linalg.matrix_rank(A)              # rank
np.trace(A)                           # trace (sum of diagonal)
```

## Stacked / Batched Operations

Many `np.linalg` functions support batched computation via leading dimensions:

```python
A = np.random.randn(10, 3, 3)         # 10 matrices of shape (3, 3)
eigenvalues = np.linalg.eigvals(A)    # shape (10, 3)
inverses = np.linalg.inv(A)           # shape (10, 3, 3)
```

The `(...)` in signatures like `(..., M, M)` indicates broadcast-compatible leading dimensions.

## Exceptions

All `np.linalg` functions raise `np.linalg.LinAlgError` for singular matrices, non-convergence, or invalid inputs.

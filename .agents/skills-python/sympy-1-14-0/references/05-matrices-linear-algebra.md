# Matrices and Linear Algebra Reference

## Matrix Construction

### Creating matrices

```python
from sympy import Matrix, eye, zeros, ones, diag, symbols, ImmutableMatrix
x = symbols('x')

# From list of lists
M = Matrix([[1, 2], [3, 4]])
M.shape   # (2, 2)

# From flat list with dimensions
M = Matrix(2, 3, [1, 2, 3, 4, 5, 6])

# Special matrices
eye(3)           # 3x3 identity
zeros(3, 2)      # 3x2 zero matrix
ones(2, 3)       # 2x3 ones matrix
diag(1, 2, 3)    # diagonal matrix

# Symbolic matrices
M = Matrix([[x, 1], [1, x]])

# Immutable (hashable, usable in sets/dicts)
IM = ImmutableMatrix([[1, 2], [3, 4]])
```

### Matrix types

| Type | Mutable | Use case |
|---|---|---|
| `MutableDenseMatrix` / `Matrix` | Yes | Default, general purpose |
| `MutableSparseMatrix` | Yes | Large sparse matrices |
| `ImmutableDenseMatrix` | No | Hashable, set/dict keys |
| `ImmutableSparseMatrix` | No | Sparse + hashable |

## Matrix Operations

### Arithmetic

```python
from sympy import Matrix, symbols
x = symbols('x')
A = Matrix([[1, 2], [3, 4]])
B = Matrix([[5, 6], [7, 8]])

# Addition/subtraction
A + B
A - B

# Scalar multiplication
3 * A
A * 3

# Matrix multiplication
A * B           # standard matrix product
A*B             # same

# Element-wise (Hadamard) product
from sympy import hadamard_product
hadamard_product(A, B)
```

### Transpose and special forms

```python
A.T                  # transpose
A.adjoint()          # conjugate transpose
A.H                  # same as adjoint()
A.is_symmetric       # check symmetry
A.is_hermitian       # check Hermitian
A.upper_triangularize()
A.lower_triangularize()
```

## Determinant, Inverse, Rank

```python
from sympy import Matrix, symbols
x = symbols('x')
A = Matrix([[1, 2], [3, 4]])

A.det()             # determinant: -2
A.rank()            # rank: 2
A.inv()             # inverse matrix
A.LUdecomposition() # (L, U, perm) tuple

# Characteristic polynomial
A.charpoly()        # lambda**2 - 5*lambda - 2

# Null space and range
A.nullspace()       # basis for null space
A.rowspace()        # basis for row space
A.colspace()        # basis for column space
```

## Eigenvalues and Eigenvectors

```python
from sympy import Matrix
A = Matrix([[4, 1], [2, 3]])

# Eigenvalues (dict: {value: multiplicity})
A.eigenvals()       # {6: 1, 1: 1}

# Eigenvectors (dict: {value: [vectors]})
A.eigenvects()      # [(6, 1, [[Matrix([1])]]), (1, 1, [[Matrix([-1])]])]

# Diagonalization
P, D = A.diagonalize()
# A = P * D * P.inv()

# Jordan form
J = A.jordan_form()
```

## Matrix Decompositions

```python
from sympy import Matrix
A = Matrix([[1, 2], [3, 4]])

# LU decomposition
L, U, perm = A.LUdecomposition()

# QR decomposition
Q, R = A.QRdecomposition()

# Cholesky (positive definite matrices)
A_chol = Matrix([[4, 2], [2, 3]])
L = A_chol.cholesky()

# SVD (symbolic, may be slow for large matrices)
U, S, Vt = A.singular_value_decomposition()
```

## Solving Linear Systems

```python
from sympy import Matrix, symbols
x, y, z = symbols('x y z')

# Ax = b
A = Matrix([[1, 2], [3, 4]])
b = Matrix([5, 6])
A.solve(b)           # column vector solution

# Augmented matrix approach
M = A.row_join(b).rref()

# System from equations
from sympy import linsolve, linear_eq_to_matrix
eqs = [x + 2*y - 5, 3*x + 4*y - 6]
A, b = linear_eq_to_matrix(eqs, (x, y))
linsolve((A, b), (x, y))
```

## Matrix Expressions (Symbolic)

```python
from sympy import MatrixSymbol, Trace, Inverse, Transpose
A = MatrixSymbol('A', n, n)
B = MatrixSymbol('B', n, n)

# Symbolic matrix algebra
expr = A * B + Transpose(A)
expr = Trace(A * B)
expr = Inverse(A) * B

# Useful for deriving identities
```

## Wronskian and Casoratian

```python
from sympy import wronskian, casoratian, symbols, sin, cos, exp
t = symbols('t')
n = symbols('n', integer=True)

# Wronskian of functions (for ODE theory)
wronskian(sin(t), cos(t), t)   # -1

# Casoratian for difference equations
casoratian(exp(n), 2**n, n)
```

## Gram-Schmidt Orthogonalization

```python
from sympy import GramSchmidt, Matrix
v1 = Matrix([1, 0, 0])
v2 = Matrix([1, 1, 0])
v3 = Matrix([1, 1, 1])
GramSchmidt([v1, v2, v3])
```

## Gotchas

- **`Matrix` is `MutableDenseMatrix`** — it can be modified in-place with methods like `.row_op()`, `.col_del()`. Use `ImmutableMatrix` when you need hashability.
- **Matrix multiplication is not element-wise** — `A * B` is standard matrix product. Use `hadamard_product(A, B)` for element-wise.
- **`.inv()` may fail silently with wrong shape** — always check `.is_square` before inverting.
- **Symbolic eigenvalues can be very slow** — for matrices larger than 4x4, eigenvalues involve solving high-degree polynomials. Use `.eigenvals(is_real=True)` or numeric methods.
- **`.rref()` returns `(rref_matrix, pivot_columns)`** — a tuple, not just the matrix.
- **`A.solve(b)` expects `b` as a column vector** — use `Matrix([1, 2, 3])` (column) not `Matrix(1, 3, [1, 2, 3])` (row).

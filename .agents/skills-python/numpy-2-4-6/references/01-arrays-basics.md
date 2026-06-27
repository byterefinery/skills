# 01 — Arrays Basics

## Array Creation

### From Python sequences

```python
np.array([1, 2, 3])                          # 1D from list
np.array([[1, 2], [3, 4]])                   # 2D from nested lists
np.array([(1, 2), (3, 4)], dtype=np.int32)   # explicit dtype
```

### Intrinsic creation functions

| Function | Description | Example |
|---|---|---|
| `np.arange(start, stop, step)` | Range with step (integer preferred) | `np.arange(0, 10, 2)` → `[0,2,4,6,8]` |
| `np.linspace(start, stop, num)` | Evenly spaced, includes endpoints | `np.linspace(0, 1, 5)` → `[0, 0.25, 0.5, 0.75, 1]` |
| `np.logspace(start, stop, num)` | Log-spaced values | `np.logspace(0, 2, 3)` → `[1, 10, 100]` |
| `np.zeros(shape)` | Array of zeros | `np.zeros((2, 3))` |
| `np.ones(shape)` | Array of ones | `np.ones((3, 3))` |
| `np.empty(shape)` | Uninitialized (fastest) | `np.empty((100,))` |
| `np.full(shape, fill_value)` | Filled with scalar | `np.full((2, 2), 7)` |
| `np.eye(N, M)` | Identity-like matrix | `np.eye(3)` or `np.eye(3, 5)` |
| `np.diag(v, k)` | Diagonal matrix or extract diagonal | `np.diag([1,2,3])` or `np.diag(a)` |
| `np.identity(N)` | Square identity (float) | `np.identity(4)` |
| `np.tri(rows, cols, k)` | Lower triangular matrix | `np.tri(3, 5, 0)` |
| `np.vander(x, N)` | Vandermonde matrix | `np.vander([1,2,3], 3)` |
| `np.fromfunction(func, shape)` | Element-wise function call | `np.fromfunction(lambda i,j: i+j, (3,3))` |

### From existing arrays

```python
np.zeros_like(a)       # same shape/dtype as a, filled with zeros
np.ones_like(a)        # same shape/dtype as a, filled with ones
np.empty_like(a)       # same shape/dtype, uninitialized
np.full_like(a, val)   # same shape/dtype, filled with val
np.asanyarray(obj)     # convert to array (preserves subclasses)
np.asarray(obj)        # convert to ndarray (always base class)
```

### From files

```python
np.load('file.npy')             # .npy binary
np.load('file.npz')             # .npz archive → NpzFile dict-like
np.loadtxt('data.csv', delimiter=',')   # simple text/CSV
np.genfromtxt('data.csv', delimiter=',', names=True)  # with headers, handles missing
np.fromfile('data.bin', dtype=np.float32)  # raw binary
```

## Shape and Reshaping

### Key attributes

```python
a = np.array([[1, 2, 3], [4, 5, 6]])
a.shape       # (2, 3)
a.ndim        # 2
a.size        # 6
a.dtype       # dtype('int64')
a.itemsize    # 8 (bytes per element)
a.nbytes      # 48 (total bytes)
```

### Reshaping

```python
np.reshape(a, (3, 2))     # reshape (view if possible, copy otherwise)
a.reshape(-1, 2)          # infer first dimension → shape (3, 2)
np.ravel(a)               # flatten to 1D (view when possible)
a.flatten()               # always returns a flattened copy
a.ravel(order='F')        # Fortran-order flattening
```

Use `a.reshape(-1)` instead of `a.ravel()` when you need a guaranteed view. Use `.flatten()` when you need an independent copy.

### Changing dimensionality

```python
np.atleast_1d(x)     # ensure at least 1D
np.atleast_2d(x)     # ensure at least 2D
np.atleast_3d(x)     # ensure at least 3D
np.expand_dims(a, axis=0)   # add new axis: (3,) → (1, 3)
np.squeeze(a)                # remove all size-1 dimensions
np.squeeze(a, axis=0)        # remove specific dimension
```

## Indexing

### Basic indexing (returns views)

```python
a[0]           # first row of 2D array
a[0, 1]        # element at row 0, col 1
a[1:]          # all rows from index 1
a[:, ::-1]     # reverse column order
a[1:3, 0:2]    # subarray slice
a[..., 0]      # ellipsis: all dims except last → first column
```

### Fancy indexing (returns copies)

```python
a[[0, 2, 1]]           # reorder rows
a[[0, 2], [1, 0]]      # pair indices: (0,1), (2,0)
a[np.ix_([0, 2], [1, 3])]  # outer product of indices → submatrix
```

### Boolean indexing (returns copies)

```python
mask = a > 3
a[mask]                 # elements where mask is True
a[a > 3]                # inline condition
a[(a > 1) & (a < 5)]    # compound conditions (use &, |, ~, not && || !)
np.where(a > 3, a, 0)   # ternary: if a>3 then a else 0
```

### Finding indices

```python
np.argmax(a)            # index of maximum
np.argmin(a)            # index of minimum
np.nonzero(a)           # indices where a != 0
np.where(a > 3)         # indices where condition is True
np.flatnonzero(a)       # flat indices of nonzero elements
np.argwhere(a > 3)      # array of indices (shape: (N, ndim))
```

## Iteration

```python
# Basic iteration (over first axis)
for row in a:
    print(row)

# Flatten iteration
for val in a.flat:
    print(val)

# Enumerate with indices
for idx, val in np.ndenumerate(a):
    print(idx, val)  # idx is a tuple of coordinates

# nditer for advanced control
for x in np.nditer(a, order='F'):
    print(x)

# Read-write iteration
with np.nditer(a, op_flags=['readwrite']) as it:
    for x in it:
        x[...] = 2 * x
```

## Memory Layout

```python
a.flags['C_CONTIGUOUS']   # C-order (row-major) contiguous
a.flags['F_CONTIGUOUS']   # Fortran-order (column-major) contiguous
a.strides                  # bytes to step in each dimension
a.base                     # original array if this is a view, None otherwise
np.ascontiguousarray(a)    # ensure C-contiguous copy
np.asfortranarray(a)       # ensure Fortran-contiguous copy
```

Strides tell NumPy how many bytes to advance when incrementing an index in each dimension. For a `(3, 4)` float64 array in C-order, strides are `(32, 8)` — advancing row index moves 32 bytes (4 elements × 8 bytes), advancing column moves 8 bytes.

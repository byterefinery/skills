# 07 — Advanced Features

## `np.einsum` — Einstein Summation

Express tensor contractions with subscript notation:

```python
np.einsum('ii->i', A)           # diagonal
np.einsum('ij->ji', A)          # transpose
np.einsum('ij,ij->', A, B)      # Frobenius inner product (scalar)
np.einsum('ij,jk->ik', A, B)    # matrix multiplication
np.einsum('ij,kj->ik', A, B)    # A @ B^T
np.einsum('...j,jk->...k', A, B)# batched matmul
np.einsum('ijk,ilk->jl', A, B)  # contraction over i and k
```

The `->` output subscript is optional — if omitted, all repeated indices are summed (implicit contraction). Use `optimize=True` for complex contractions to find the best evaluation order.

## Stride Tricks

### `np.lib.stride_tricks.sliding_window_view`

Create rolling/moving window views efficiently:

```python
from numpy.lib.stride_tricks import sliding_window_view

a = np.array([1, 2, 3, 4, 5])
windows = sliding_window_view(a, window_shape=3)
# array([[1, 2, 3],
#        [2, 3, 4],
#        [3, 4, 5]])

# Multi-dimensional
image = np.random.randn(100, 100, 3)
patches = sliding_window_view(image, window_shape=(5, 5), axis=(0, 1))
# shape: (96, 96, 5, 5, 3)

# Single axis
signal = np.random.randn(1000)
windows = sliding_window_view(signal, window_shape=10, axis=0)
# shape: (991, 10)
```

The result is a **view** — no data is copied. Writing to it affects overlapping regions. Use `writeable=False` (default) to prevent accidental modification.

### `np.lib.stride_tricks.as_strided`

Low-level stride manipulation (dangerous — use with care):

```python
from numpy.lib.stride_tricks import as_strided

# Create a rolling window view manually
a = np.arange(20)
shape = (17, 3)
strides = (a.strides[0], a.strides[0])
windows = as_strided(a, shape=shape, strides=strides)
```

This bypasses all safety checks. An incorrect stride can read/write arbitrary memory. Prefer `sliding_window_view` when possible.

## `nditer` — Advanced Array Iteration

```python
# Basic iteration (read-only, memory-order optimized)
for x in np.nditer(a):
    print(x)

# Control iteration order
for x in np.nditer(a, order='C'):     # C-order
    pass
for x in np.nditer(a, order='F'):     # Fortran-order
    pass

# Read-write with context manager
with np.nditer(a, op_flags=['readwrite']) as it:
    for x in it:
        x[...] = 2 * x

# Multi-array iteration
for x, y in np.nditer([a, b]):
    pass

# Read-write with external loop (for performance)
it = np.nditer([a, None], flags=['external_loop'],
               op_flags=[['readonly'], ['writeonly', 'allocate']])
for x, out in it:
    out[...] = x ** 2
```

Flags: `external_loop` (buffers contiguous chunks), `reduce_ok` (allows reduction), `delay_bufalloc` (defer buffer allocation).

## Memory-Mapped Files

Work with large files without loading entirely into memory:

```python
# Create memmap
mmap = np.memmap('data.dat', dtype=np.float64, mode='w+', shape=(1000000, 100))
mmap[0:100, :] = np.random.randn(100, 100)
del mmap  # flush and close

# Read memmap
mmap = np.memmap('data.dat', dtype=np.float64, mode='r', shape=(1000000, 100))
chunk = mmap[500:600, :]   # loads only this slice into memory
```

Modes: `'r'` (read-only), `'r+'` (read/write existing), `'w+'` (create/read/write), `'c'` (copy-on-write).

## Masked Arrays

Handle missing/invalid data with `np.ma`:

```python
a = np.array([1, 2, -999, 4, 5])
masked = np.ma.masked_where(a == -999, a)
# array([1, 2, --, 4, 5])

masked.mean()           # ignores masked values → 3.0
masked.mask             # boolean mask array
masked.filled(0)        # replace masked with fill value
np.ma.masked_invalid(a) # masks NaN and Inf
np.ma.masked_equal(a, 0)# masks zeros
```

Masked arrays propagate masks through operations:

```python
ma1 = np.ma.array([1, 2, 3], mask=[0, 1, 0])
ma2 = np.ma.array([4, 5, 6], mask=[1, 0, 0])
result = ma1 + ma2      # mask is OR'd: [--, --, 9]
```

## FFT (Fast Fourier Transform)

```python
# 1D FFT
fft_result = np.fft.fft(signal)
freqs = np.fft.fftfreq(len(signal), d=sample_interval)
recovered = np.fft.ifft(fft_result)

# Real signals (faster, exploits symmetry)
rfft = np.fft.rfft(signal)
irfft = np.fft.irfft(rfft)

# Multi-dimensional
fft2d = np.fft.fft2(image)
shifted = np.fft.fftshift(fft2d)   # center zero-frequency
ifft2d = np.fft.ifft2(np.fft.ifftshift(shifted))

# Discrete cosine/sine transforms
dct = np.fft.dst(signal, type=2)
idct = np.fft.idst(dct, type=2)
```

## Polynomials

Use `numpy.polynomial` package (not legacy `np.poly1d`):

```python
from numpy.polynomial import Polynomial

# Create from coefficients [c0, c1, c2, ...] (ascending order)
p = Polynomial([3, 2, 1])     # 3 + 2x + x²
p(2.0)                         # evaluate: 3 + 4 + 4 = 11

# Fit to data
p_fit = Polynomial.fit(x, y, deg=3)
y_pred = p_fit(x_test)

# Operations
q = p + Polynomial([1, 1])    # addition
r = p * q                     # multiplication
roots = p.roots()              # find roots
deriv = p.deriv()              # derivative
integ = p.integ()              # integral
```

Legacy `np.poly1d` uses descending coefficient order and is discouraged for new code.

## File I/O

### Binary (recommended for NumPy arrays)

```python
# Single array
np.save('data.npy', a)
a_loaded = np.load('data.npy')

# Multiple arrays
np.savez('data.npz', x=a, y=b, z=c)
archive = np.load('data.npz')
x = archive['x']

# Compressed
np.savez_compressed('data.npz', x=a, y=b)
```

### Text files

```python
# Simple CSV
np.savetxt('data.csv', a, delimiter=',', fmt='%.4f')
a = np.loadtxt('data.csv', delimiter=',')

# With headers and missing data
a = np.genfromtxt('data.csv', delimiter=',', names=True, dtype=None)
```

### Raw binary

```python
a.tofile('data.bin')           # write raw bytes
b = np.fromfile('data.bin', dtype=np.float32)  # read with known dtype
```

## Performance Tips

- **Use vectorized operations** instead of Python loops
- **Pre-allocate output arrays** with `out=` parameter to avoid allocation overhead
- **Use `np.add.at()` for accumulate-with-indexing** (regular `a[indices] += values` silently drops duplicates)
- **`np.einsum(..., optimize=True)`** for complex tensor contractions
- **Keep arrays contiguous** — non-contiguous arrays force copies in many operations
- **Use `sliding_window_view`** instead of explicit loops for rolling computations
- **`np.partition` is O(n)** when you only need top-k elements
- **Batched `np.linalg`** operations on stacked arrays are faster than looping
- **Avoid `np.matrix`** — use `ndarray` with `@` operator

## NumPy 2.4 Specific Changes

- `casting='same_value'` mode: allows casting only when the value doesn't change
- `np.round()` always returns a copy (previously returned views for integers)
- `np.in1d` removed — use `np.isin()`
- `np.trapz` removed — use `np.trapezoid()`
- `np.fix` pending deprecation — prefer `np.trunc()`
- `interpolation=` removed from `percentile`/`quantile` — use `method=`
- Setting `ndarray.shape` in-place pending deprecation — use `np.reshape()`
- Setting `ndarray.strides` deprecated — use `as_strided()` or `sliding_window_view()`
- `np.testing.assert_warns` / `suppress_warnings` deprecated — use `pytest.warns`
- Python 3.11–3.14 support

---
name: numpy-2-4-6
description: "NumPy 2.4.6: array creation, manipulation, broadcasting, ufuncs, linear algebra, statistics, random sampling, structured arrays, and I/O. Use whenever working with numerical arrays, matrices, scientific computing, data analysis, or any task involving NumPy operations. Covers ndarrays, dtype system, einsum, stride tricks, masked arrays, FFT, polynomials, and the full NumPy 2.x API."
metadata:
  tags:
    - numerical
    - arrays
    - scientific-computing
---

# numpy 2.4.6

## Overview

NumPy 2.4.6 is the core library for numerical computing in Python. It provides the `ndarray` type — a fast, memory-efficient N-dimensional array with vectorized operations, broadcasting, and a rich ecosystem of mathematical routines. This skill covers the full NumPy 2.x API, including features specific to the 2.4 release line (Python 3.11–3.14 support, `same_value` casting, annotation improvements, free-threaded Python progress).

Key capabilities:
- **Array creation** from sequences, ranges, shapes, files, and buffers
- **Indexing and slicing** with basic, fancy, and boolean indexing
- **Broadcasting** for element-wise operations across mismatched shapes
- **Universal functions (ufuncs)** for vectorized math, trigonometry, logic
- **Linear algebra** via BLAS/LAPACK: decompositions, eigenvalues, solving systems
- **Statistics**: mean, std, variance, correlation, histograms, order statistics
- **Random sampling** with `default_rng()` (PCG64 engine)
- **Structured/record arrays** for heterogeneous data
- **I/O**: `.npy`/`.npz` binary, CSV/text, memory-mapped files
- **Advanced tools**: `nditer`, `sliding_window_view`, `einsum`, stride tricks

## Usage

All routines are accessed through the `numpy` namespace (conventionally imported as `np`):

```python
import numpy as np

# Array creation
a = np.array([1, 2, 3])
b = np.zeros((3, 3), dtype=np.float64)
c = np.arange(0, 10, 2)
d = np.linspace(0, 1, 5)

# Indexing and slicing
a[0]        # single element
b[1, :]     # row slice (returns a view)
c[c > 2]    # boolean indexing (returns a copy)

# Broadcasting
result = b + [1, 2, 3]  # adds to each row

# Linear algebra
eigenvalues, eigenvectors = np.linalg.eig(b)
solution = np.linalg.solve(b, np.ones(3))

# Statistics
mean, std = np.mean(a), np.std(a)

# Random
rng = np.random.default_rng(42)
samples = rng.standard_normal((100, 3))
```

## Gotchas

- **`np.round()` always returns a copy** in 2.4+ (previously returned views for integer inputs with `decimals >= 0`).
- **`np.arange(start=...)` as keyword is rejected by type checkers** for Array API compatibility. At runtime it still works, but use positional: `np.arange(start, stop, step)`.
- **`np.maximum(a, b, out=c)` must use `out=` keyword** — positional third argument is deprecated. Same for `np.minimum`.
- **Setting `ndarray.shape` in-place is pending deprecation**. Use `np.reshape()` instead.
- **Setting `ndarray.strides` is deprecated**. Use `np.lib.stride_tricks.as_strided()` or `strided_window_view()`.
- **`np.trapz` removed** — use `np.trapezoid` instead.
- **`np.in1d` removed** — use `np.isin` instead.
- **`np.fix` pending deprecation** — prefer `np.trunc`.
- **`interpolation=` parameter removed from `percentile`/`quantile`** — use `method=` instead.
- **`np.testing.assert_warns` and `suppress_warnings` deprecated** — use `pytest.warns` or `warnings.catch_warnings`.
- **`np.sum(generator)` raises `TypeError`** — wrap with `np.fromiter()` first.
- **`np.delete` does not support in-place deletion** — it always returns a new array.
- **Advanced indexing (fancy/boolean) always returns a copy**, while basic slicing returns a view. This matters for memory: modifying a view modifies the original; modifying a fancy-indexed result does not.
- **Broadcasting is powerful but can silently blow up memory** when combining large arrays with small ones — the result shape uses the largest dimension in each axis.
- **`np.matrix` is discouraged** even for linear algebra. Use `np.ndarray` with `@` operator or `np.matmul()`.
- **Structured arrays have poor cache behavior** compared to pandas/xarray for tabular data. They are best for C-struct interop and binary buffer interpretation.
- **`np.random.RandomState` is legacy** — always use `np.random.default_rng()` for new code.
- **`np.allclose()` default tolerances** (`rtol=1e-5, atol=1e-8`) may not suit all domains. Adjust for your precision needs.
- **Integer overflow is silent** in NumPy (follows C rules). `uint32 - uint32` wrapping around is expected behavior.
- **`np.copyto()` modifies the destination in-place** and supports a `where` mask for conditional copying.
- **`np.einsum` with `optimize=True`** can dramatically speed up complex contractions but adds overhead for simple cases.
- **`np.savez_compressed` uses ZIP compression** which is fast but not optimal for highly compressible data.

## References

- [01-arrays-basics](references/01-arrays-basics.md) — Array creation, shapes, indexing, slicing, iteration
- [02-broadcasting-ufuncs](references/02-broadcasting-ufuncs.md) — Broadcasting rules, ufuncs, vectorization patterns
- [03-data-types](references/03-data-types.md) — dtype system, type promotion, structured arrays
- [04-linear-algebra](references/04-linear-algebra.md) — Matrix products, decompositions, eigenvalues, solving systems
- [05-statistics-random](references/05-statistics-random.md) — Statistics, histograms, random number generation
- [06-array-manipulation](references/06-array-manipulation.md) — Reshaping, joining, splitting, transposing, padding
- [07-advanced-features](references/07-advanced-features.md) — nditer, stride tricks, einsum, memory mapping, masked arrays

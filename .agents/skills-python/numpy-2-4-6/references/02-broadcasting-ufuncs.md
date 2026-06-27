# 02 — Broadcasting and Ufuncs

## Broadcasting Rules

Broadcasting allows operations between arrays of different shapes. NumPy compares shapes element-wise from the **trailing (rightmost) dimension** leftward. Two dimensions are compatible when:

1. They are equal, or
2. One of them is 1

Missing leading dimensions are treated as size 1.

```python
# Compatible examples
(3,) + (4, 3)      → (4, 3)    # scalar broadcast to last axis
(4, 1) + (4, 3)     → (4, 3)    # column vector broadcast across rows
(1, 3) + (4, 3)     → (4, 3)    # row vector broadcast across rows
(2, 3, 4) + (4,)    → (2, 3, 4) # trailing dims align
() + (4, 3)         → (4, 3)    # scalar broadcast everywhere

# Incompatible — raises ValueError
(3,) + (4,)          # trailing dims differ
(2, 1) + (8, 4, 3)   # second-to-last dims mismatch
```

### Manual broadcasting

```python
np.broadcast_to(a, new_shape)        # broadcast a to new_shape (view, read-only)
np.broadcast_arrays(a, b)            # broadcast multiple arrays together
result = np.broadcast_shapes(*shapes) # compute result shape without creating arrays
```

### Adding dimensions for broadcasting

Use `np.newaxis` (alias of `None`) to insert size-1 axes:

```python
a = np.array([1, 2, 3])           # shape (3,)
col = a[:, np.newaxis]            # shape (3, 1) — column vector
row = a[np.newaxis, :]            # shape (1, 3) — row vector
outer = col * row                 # shape (3, 3) — outer product via broadcasting
```

## Universal Functions (Ufuncs)

Ufuncs operate element-wise on arrays with automatic broadcasting and type casting.

### Arithmetic ufuncs

| Ufunc | Operator | Description |
|---|---|---|
| `np.add` | `+` | Addition |
| `np.subtract` | `-` | Subtraction |
| `np.multiply` | `*` | Element-wise multiplication |
| `np.divide` | `/` | True division |
| `np.floor_divide` | `//` | Floor division |
| `np.power` | `**` | Exponentiation |
| `np.mod` | `%` | Modulus |
| `np.negative` | `-x` | Negation |
| `np.reciprocal` | — | 1/x |

### Comparison ufuncs

```python
np.equal(a, b)        # a == b
np.not_equal(a, b)    # a != b
np.greater(a, b)      # a > b
np.less(a, b)         # a < b
np.greater_equal(a, b)# a >= b
np.less_equal(a, b)   # a <= b
```

### Trigonometric ufuncs

```python
np.sin(x), np.cos(x), np.tan(x)
np.arcsin(x), np.arccos(x), np.arctan(x)
np.arctan2(y, x)       # element-wise arctan2
np.degrees(x), np.radians(x)
np.hypot(a, b)         # sqrt(a² + b²)
```

### Hyperbolic ufuncs

```python
np.sinh(x), np.cosh(x), np.tanh(x)
np.arcsinh(x), np.arccosh(x), np.arctanh(x)
```

### Exponential and logarithmic ufuncs

```python
np.exp(x), np.exp2(x)       # e^x, 2^x
np.expm1(x)                  # e^x - 1 (accurate near 0)
np.log(x), np.log2(x), np.log10(x)
np.log1p(x)                  # ln(1 + x) (accurate near 0)
np.logaddexp(x, y)           # log(exp(x) + exp(y))
```

### Rounding ufuncs

```python
np.round(x, decimals=0)   # round to given decimal places
np.floor(x)               # floor
np.ceil(x)                # ceiling
np.trunc(x)               # truncate toward zero
np.rint(x)                # round to nearest integer (as float)
```

### Special ufuncs

```python
np.maximum(a, b)          # element-wise max (use out= keyword!)
np.minimum(a, b)          # element-wise min
np.clip(x, min, max)      # clip values to range
np.fmod(a, b)             # C-style remainder
np.modf(x)                # fractional and integer parts
np.conj(x)                # complex conjugate
np.angle(x)               # phase angle of complex numbers
```

### Logical ufuncs

```python
np.logical_and(a, b)      # a AND b
np.logical_or(a, b)       # a OR b
np.logical_not(a)         # NOT a
np.logical_xor(a, b)      # a XOR b
np.isfinite(x)            # True where finite
np.isinf(x)               # True where ±infinity
np.isnan(x)               # True where NaN
```

### Ufunc methods

All binary ufuncs support these methods:

```python
# reduce: apply along axis
np.add.reduce(a, axis=0)      # column sums
np.multiply.reduce(a)         # product of all elements
np.add.accumulate(a)          # cumulative sum
np.add.accumulate(a, axis=1)  # row-wise cumulative

# outer: outer product
np.multiply.outer([1,2], [3,4])  # [[3,4],[6,8]]

# at: in-place operation with advanced indexing
np.add.at(a, indices, values)    # a[indices] += values (no buffering)
```

### Ufunc kwargs

All ufuncs accept these keyword arguments:

- `out=array` — write result to pre-allocated array (avoids allocation)
- `where=mask` — only compute where mask is True
- `casting='no'|'equiv'|'safe'|'same_kind'|'unsafe'|'same_value'` — control type casting
- `order='K'|'C'|'F'|'A'` — memory order of output
- `dtype=` — override computation dtype

The `same_value` casting mode (new in 2.4) allows casting only when the value doesn't change, useful for preventing silent overflow.

## Vectorization Patterns

### Replacing loops with vectorized operations

```python
# Instead of:
result = np.empty(n)
for i in range(n):
    result[i] = a[i] ** 2 + b[i]

# Use:
result = a**2 + b
```

### Conditional logic without loops

```python
# Instead of if/else loop:
np.where(condition, x, y)           # ternary
np.select([cond1, cond2], [val1, val2], default=0)  # multi-condition
np.piecewise(x, [x < 0, x >= 0], [lambda x: -x, lambda x: x])  # piecewise function
```

### `np.vectorize` for wrapping scalar functions

```python
def my_func(x):
    return x ** 2 if x > 0 else 0

vec_func = np.vectorize(my_func)
result = vec_func(a)  # applies to each element
```

Note: `np.vectorize` is a convenience wrapper, not a performance optimization. It still loops in Python. Use it for code clarity, not speed. For performance, write a proper ufunc with `np.frompyfunc()` or use Cython/Numba.

### `np.frompyfunc` for creating ufuncs

```python
ufunc = np.frompyfunc(lambda x, y: x + y, 2, 1)
result = ufunc(a, b)  # returns object array
```

This creates a true ufunc (supports broadcasting and reduce methods) but always returns object arrays. Cast the result to the desired dtype afterward.

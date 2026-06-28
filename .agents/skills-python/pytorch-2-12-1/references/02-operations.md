# Operations Reference

## Elementwise Math

```python
# Arithmetic
y = x + 1            # add (supports broadcasting)
y = torch.add(x, 1, alpha=0.5)  # x + 0.5 * 1
y = x - y
y = x * y            # elementwise multiply
y = x / y
y = x // y           # floor divide
y = x % y            # modulo
y = x ** 2           # power
y = x.reciprocal()   # 1/x

# Exponential/log
y = torch.exp(x)
y = torch.log(x)
y = torch.log2(x)
y = torch.log10(x)
y = torch.log1p(x)   # log(1 + x), numerically stable
y = torch.sqrt(x)
y = torch.rsqrt(x)   # 1/sqrt(x)
y = torch.pow(x, 2)
y = torch.square(x)

# Trigonometric
y = torch.sin(x)
y = torch.cos(x)
y = torch.tan(x)
y = torch.asin(x)
y = torch.arccos(x)
y = torch.arctan(x)
y = torch.arctan2(x, y)

# Hyperbolic
y = torch.sinh(x)
y = torch.cosh(x)
y = torch.tanh(x)

# Rounding
y = torch.round(x)
y = torch.floor(x)
y = torch.ceil(x)
y = torch.trunc(x)

# Comparison
y = torch.abs(x)
y = torch.sign(x)
y = torch.clamp(x, min=0, max=1)    # clip to range
y = torch.where(mask, x, y)         # conditional select
```

## Linear Algebra (`torch.linalg`)

```python
# Matrix multiply
y = x @ y                    # matmul (2D) or batch matmul (3D+)
y = torch.matmul(x, y)       # same as @
y = torch.mv(x, v)           # matrix-vector
y = torch.vv(v1, v2)         # vector-vector (dot product)
y = torch.bmm(a, b)          # batch matmul: (b, n, m) @ (b, m, p) → (b, n, p)

# Decomposition
Q, R = torch.linalg.qr(x)
L = torch.linalg.cholesky(x)          # Cholesky (positive definite)
eigvals = torch.linalg.eigvalsh(x)    # eigenvalues (Hermitian)
U, S, Vh = torch.linalg.svd(x)        # SVD

# Solve
x = torch.linalg.solve(A, b)          # Ax = b
x = torch.linalg.lstsq(A, b)          # least squares

# Properties
det = torch.linalg.det(x)
trace = torch.trace(x)
norm = torch.linalg.norm(x)           # 2-norm (Frobenius for matrices)
norm = torch.linalg.norm(x, ord=1)    # 1-norm
rank = torch.linalg.matrix_rank(x)
cond = torch.linalg.cond(x)           # condition number
inv = torch.linalg.inv(x)             # matrix inverse
```

**Rule:** Prefer `torch.linalg.solve(A, b)` over `A.inv() @ b`. Direct inversion is slower and less numerically stable.

## Reductions

```python
# Basic
y = x.sum()                    # all elements
y = x.sum(dim=0)               # sum along dim 0
y = x.sum(dim=(0, 1))          # sum along multiple dims
y = x.sum(dim=1, keepdim=True) # keep reduced dim as size 1

# Common reductions
x.mean()
x.std()
x.var()
x.min() / x.max()
x.argmin() / x.argmax()
x.prod()
x.amax() / x.amin()
x.median()
x.quantile(0.5)

# Return both value and index
val, idx = x.max(dim=-1)
val, idx = x.min(dim=-1)

# Specialized
x.any()     # True if any element is True/nonzero
x.all()     # True if all elements are True/nonzero
x.count_nonzero()
x.nanmean()  # ignore NaN values
x.nansum()   # ignore NaN values
```

**Rule:** Use `keepdim=True` when the reduced tensor needs to broadcast back against the original.

## Comparison and Logic

```python
# Elementwise comparison
y = torch.eq(x, y)     # ==
y = torch.ne(x, y)     # !=
y = torch.gt(x, y)     # >
y = torch.ge(x, y)     # >=
y = torch.lt(x, y)     # <
y = torch.le(x, y)     # <=
y = torch.isclose(x, y, atol=1e-8, rtol=1e-5)  # approximate equality

# Allclose (for testing)
torch.allclose(x, y)  # True if all elements approximately equal

# Logic
y = torch.logical_and(a, b)
y = torch.logical_or(a, b)
y = torch.logical_not(a)

# NaN/Inf
torch.isnan(x)
torch.isinf(x)
torch.isfinite(x)
```

## FFT

```python
# Forward/inverse
Y = torch.fft.fft(x)              # 1D FFT
Y = torch.fft.fft2(x)             # 2D FFT
Y = torch.fft.fftn(x, s=None, dim=None)  # N-D FFT
y = torch.fft.ifft(Y)             # inverse

# Real-valued
Y = torch.fft.rfft(x)             # real input → complex output
y = torch.fft.irfft(Y)            # complex → real

# Frequency
freqs = torch.fft.fftfreq(n)      # frequency bins
```

## Random

```python
# Seeding
torch.manual_seed(42)
torch.cuda.manual_seed_all(42)
# Full reproducibility
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False

# Distributions
x = torch.randn(3, 4)                        # normal(0, 1)
x = torch.randn(3, 4, mean=5, std=2)         # normal(5, 2)
x = torch.rand(3, 4)                         # uniform(0, 1)
x = torch.randint(0, 10, (3, 4))             # uniform integers [0, 10)
x = torch.randperm(10)                       # random permutation
x = torch.multinomial(weights, 5, replacement=False)  # sample without replacement

# Bernoulli
x = torch.bernoulli(probs)                   # binary sample from probs tensor

# Generator (for reproducibility per-operation)
gen = torch.Generator().manual_seed(42)
x = torch.randn(3, 4, generator=gen)
```

## Special Functions

```python
# Activation-related
y = torch.sigmoid(x)
y = torch.softmax(x, dim=-1)
y = torch.log_softmax(x, dim=-1)
y = torch.gelu(x)
y = torch.relu(x)

# Distance
y = torch.cdist(x1, x2, p=2)           # pairwise distances
y = torch.pdist(x, p=2)                # pairwise distances within matrix rows

# Interpolation
y = torch.lerp(start, end, weight)     # linear interpolation

# Top-k
values, indices = torch.topk(x, k=5, dim=-1)

# Sort
values, indices = torch.sort(x, dim=-1, descending=True)

# Unique
unique, inverse = torch.unique(x, return_inverse=True)
unique, counts = torch.unique(x, return_counts=True)

# Cumulative
y = torch.cumsum(x, dim=0)
y = torch.cumprod(x, dim=0)
y = torch.cummax(x, dim=0)
y = torch.cummin(x, dim=0)

# Scatter / fill
output = torch.zeros(5, 3)
indices = torch.tensor([[0], [1], [2]])
values = torch.tensor([[1], [2], [3]])
output.scatter_(0, indices, values)
```

## Inplace Operations

Most operations have inplace versions with `_` suffix:

```python
x.add_(y)
x.mul_(y)
x.clamp_(0, 1)
x.zero_()
x.fill_(7)
```

**Rule:** Avoid inplace operations on tensors that are part of a computation graph with shared inputs. They can corrupt gradient computation. Use inplace only on leaf tensors or when you are certain there are no other references.

# Transforms and Discrete Math Reference

## Laplace Transform

```python
from sympy import symbols, Function, laplace_transform, inverse_laplace_transform, exp, sin, cos
t, s = symbols('t s')
f = Function('f')(t)

# Forward transform
laplace_transform(exp(-a*t), t, s)         # (1/(a + s), -a, [])
laplace_transform(sin(w*t), t, s)          # (w/(s**2 + w**2), 0, [])
laplace_transform(t**n, t, s)              # factorial(n)/s**(n + 1)

# Result is tuple: (transform, convergence_plane, conditions)
F, a, cond = laplace_transform(exp(-t), t, s)

# Inverse transform
inverse_laplace_transform(1/(s**2 + 1), s, t)   # sin(t)
inverse_laplace_transform(1/s, s, t)            # Heaviside(t)

# Unevaluated forms
from sympy import LaplaceTransform, InverseLaplaceTransform
LaplaceTransform(f, t, s)
InverseLaplaceTransform(F, s, t)
```

## Fourier Transform

```python
from sympy import symbols, fourier_transform, inverse_fourier_transform, exp
x, k = symbols('x k', real=True)

# Forward transform
fourier_transform(exp(-x**2), x, k)       # sqrt(pi)*exp(-pi**2*k**2)

# Inverse transform
inverse_fourier_transform(exp(-k**2), k, x)

# Unevaluated forms
from sympy import FourierTransform, InverseFourierTransform
```

## Mellin Transform

```python
from sympy import symbols, mellin_transform, inverse_mellin_transform, exp
x, s = symbols('x s', positive=True)

mellin_transform(exp(-x), x, s)            # gamma(s)
inverse_mellin_transform(gamma(s), s, x)   # exp(-x)
```

## Other Integral Transforms

```python
from sympy import symbols, sine_transform, cosine_transform, hankel_transform
x, k = symbols('x k', positive=True)

sine_transform(exp(-x), x, k)              # k/(k**2 + 1)
cosine_transform(exp(-x), x, k)            # 1/(k**2 + 1)
hankel_transform(expr, x, k, n=0)          # Hankel transform of order n
```

## Discrete Transforms

### FFT (Fast Fourier Transform)

```python
from sympy import fft, ifft

# Forward FFT
fft([1, 2, 3, 4])
# [10, -2 + 2*I, -2, -2 - 2*I]

# Inverse FFT
ifft([10, -2 + 2*I, -2, -2 - 2*I])
# [1, 2, 3, 4]
```

### NTT (Number Theoretic Transform)

```python
from sympy import ntt, intt

# NTT over finite field
ntt([1, 2, 3, 4], modulus=17, root=3)
intt(result, modulus=17, root=3)
```

### Walsh-Hadamard Transform

```python
from sympy import fwht, ifwht

fwht([1, 2, 3, 4])     # Fast Walsh-Hadamard Transform
ifwht(result)           # Inverse
```

### Möbius Transform

```python
from sympy import mobius_transform, inverse_mobius_transform

mobius_transform([1, 2, 3, 4])
inverse_mobius_transform(result)
```

## Convolutions

```python
from sympy import convolution

# Standard convolution
convolution([1, 2, 3], [4, 5, 6])

# FFT-based convolution (faster for large sequences)
from sympy.discrete import convolution_fft
convolution_fft([1, 2, 3], [4, 5, 6])
```

## Boolean Logic

```python
from sympy import symbols, And, Or, Not, Xor, Implies, Equivalent
from sympy import to_cnf, to_dnf, to_nnf, simplify_logic, satisfiable

p, q, r = symbols('p q r')

# Logical expressions
expr = And(p, Or(q, Not(r)))
expr = Implies(p, q)
expr = Equivalent(p, q)

# Normal forms
to_cnf(expr)           # Conjunctive Normal Form
to_dnf(expr)           # Disjunctive Normal Form
to_nnf(expr)           # Negation Normal Form

# Simplification
simplify_logic(Or(And(p, q), And(p, Not(q))))   # p

# SAT solving
satisfiable(And(p, Or(q, r)))
```

## Logic Truth Tables

```python
from sympy import SOPform, POSform

# Sum of Products from truth table
# minterms: rows where output is 1
# dontcares: rows that can be either
SOPform([p, q], [1, 3])        # p (minterms 1 and 3)
POSform([p, q], [0, 2])        # p (maxterms 0 and 2)
```

## Summation and Products

```python
from sympy import symbols, summation, Sum, product, Product
k, n = symbols('k n', integer=True)

# Symbolic summation
summation(k, (k, 1, n))           # n*(n + 1)/2
summation(k**2, (k, 1, n))        # n*(n + 1)*(2*n + 1)/6
summation(1/k**2, (k, 1, oo))     # pi**2/6

# Unevaluated sum
Sum(k**3, (k, 1, n))              # Σ k³

# Products
product(k, (k, 1, n))             # n!
Product(2**k, (k, 0, n))         # 2^(n*(n+1)/2)
```

## Combinatorial Numbers

```python
from sympy import symbols, factorial, binomial, subfactorial
from sympy import fibonacci, lucas, catalan, bell, bernoulli, euler, harmonic

n = symbols('n', integer=True)

factorial(n)          # n!
binomial(n, k)        # C(n,k)
subfactorial(n)       # !n (derangements)
fibonacci(n)          # F_n
catalan(n)            # C_n
bell(n)               # B_n (Bell numbers)
bernoulli(n)          # B_n (Bernoulli numbers)
euler(n)              # E_n (Euler numbers)
harmonic(n)           # H_n
```

## Sets

```python
from sympy import Interval, Union, Intersection, FiniteSet, ImageSet, symbols
from sympy import S, Reals, Integers, Naturals

# Intervals
Interval(0, 1)            # [0, 1] (closed)
Interval(0, 1, left_open=True)   # (0, 1]

# Set operations
Union(Interval(0, 1), Interval(2, 3))
Intersection(Interval(0, 2), Interval(1, 3))   # [1, 2]

# Finite sets
FiniteSet(1, 2, 3)

# Image sets
n = symbols('n', integer=True)
ImageSet(Lambda(n, 2*n), Integers)    # {2n | n ∈ Z}

# Built-in sets
S.Reals, S.Integers, S.Naturals, S.Complexes, S.EmptySet
```

## Gotchas

- **`laplace_transform()` returns a tuple** — `(transform, convergence, conditions)`. Extract the first element for the transform itself.
- **Fourier transform convention** — SymPy uses the unitary angular frequency convention. Check `fourier_transform` docs for exact formula.
- **`inverse_laplace_transform()` can be slow** — it uses complex contour integration. Simple cases work fast; complicated ones may time out.
- **FFT requires sequence length to be a power of 2** — pad with zeros if needed.
- **`satisfiable()` returns a model dict or `False`** — not just True/False. Use `bool(satisfiable(expr))` for boolean check.
- **Set membership uses `Contains`** — `Contains(x, Interval(0, 1))`, not `x in Interval(0, 1)`.

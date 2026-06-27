# Algebra and Polynomials Reference

## Polynomial Basics

### Creating polynomial objects

```python
from sympy import symbols, Poly, degree, degree_list
x, y = symbols('x y')

# From expression
p = Poly(x**3 - 2*x**2 + x - 1, x)
p.degree()        # 3
p.degree(x)       # 3
p.nvars           # 1
p.all_coeffs()    # [1, -2, 1, -1]
p.coeff_monomial(x**2)  # -2
p.eval(2)         # evaluate at x=2 → 3

# Multivariate
q = Poly(x**2*y + x*y**2 - 1, x, y)
q.total_degree()    # 3
degree_list(q)      # [2, 1] (max degree in each variable)
```

### Polynomial domain specification

The domain controls arithmetic behavior and factorization:

```python
from sympy import Poly, symbols, QQ, ZZ
x = symbols('x')

# Integer coefficients
Poly(x**2 + x/2, x, domain='QQ')   # Rational field
Poly(2*x**2 + 3*x + 1, x, domain='ZZ')  # Integer ring

# Domain shortcuts
from sympy import GF, FF, ZZ, QQ, RR, CC
Poly(f, x, domain=GF(7))     # finite field Z/7Z
```

## Expansion and Factoring

### Expand family

```python
from sympy import symbols, expand, expand_mul, expand_log, expand_trig, expand_complex
x, y = symbols('x y')

expand((x + 1)**3)                    # x**3 + 3*x**2 + 3*x + 1
expand_mul((x + 1)*(x + 2))          # only distributes multiplication
expand_log(x*y, force=True)          # log(x) + log(y)
expand_trig(sin(2*x))                # 2*sin(x)*cos(x)
expand_complex(expr)                 # separate real and imaginary parts
```

### Factorization

```python
from sympy import symbols, factor, factor_list, sqf_list
x = symbols('x')

factor(x**3 - x)           # x*(x - 1)*(x + 1)
factor(x**2 + 2*x + 1)     # (x + 1)**2

# Factor with extension
factor(x**4 - 2, extension=sqrt(2))  # factors over Q(√2)

# Factor list: [(coefficient, (factor1, mult1), ...)]
factor_list(x**4 - 1)      # (1, [(-1, 1), (x, 1), (x + 1, 1), (x**2 + 1, 1)])

# Square-free factorization
sqf_list(x**4 - 2*x**3 + x**2)  # handles repeated factors
```

### Other algebraic manipulations

```python
from sympy import symbols, cancel, together, apart, collect
x, y = symbols('x y')

# Cancel common factors in rational expressions
cancel((x**2 - 1)/(x - 1))     # x + 1

# Combine into single fraction
together(1/x + 1/y)            # (x + y)/(x*y)

# Partial fraction decomposition
apart(1/(x**2 - 1), x)        # 1/(2*(x - 1)) - 1/(2*(x + 1))

# Collect terms by pattern
collect(a*x**2 + b*x**2 + c*x, x)   # (a + b)*x**2 + c*x
```

## Root Finding

### Symbolic roots

```python
from sympy import symbols, solve, roots, all_roots, real_roots
x = symbols('x')

# For polynomials up to degree 4 (and some special cases)
roots(x**4 - 5*x**2 + 4, x)        # {1: 1, -1: 1, 2: 1, -2: 1}
all_roots(x**5 - 1)                 # includes RootOf for degree ≥ 5
real_roots(x**3 - x)                # [-1, 0, 1]

# CRootOf for algebraic numbers
from sympy import CRootOf
r = CRootOf(x**3 - x - 1, 0)  # root near 0
r.evalf()                       # numeric approximation
```

### Numerical roots

```python
from sympy import nroots, symbols
x = symbols('x')

# All roots numerically (including complex)
nroots(x**5 - x - 1)
nroots(x**3 - 2*x + 1, n=15)  # 15 digits precision
```

## Groebner Bases

```python
from sympy import symbols, groebner, Poly
x, y, z = symbols('x y z')

# Compute Groebner basis
G = groebner([x**2 - y, x*y - z], x, y, z)
G  # GroebnerBasis(...)

# Elimination: variables listed first are eliminated
G = groebner([x + y + z, x*y + y*z + z*x], x, y, z, order='lex')

# Reduction
G.reduce(x**3 + y**2)
```

## Resultants and Discriminants

```python
from sympy import symbols, resultant, discriminant
x, y = symbols('x y')

# Resultant eliminates one variable
f = x**2 + y*x + 1
g = x + y
resultant(f, g, x)   # polynomial in y only

# Discriminant
discriminant(x**2 + b*x + c, x)    # b**2 - 4*c
```

## Polynomial Construction

### Interpolation

```python
from sympy import symbols, interpolate
x = symbols('x')

# Lagrange interpolation through points
interpolate([(0, 1), (1, 3), (2, 7)], x)   # x**2 + x + 1
```

### Cyclotomic and orthogonal polynomials

```python
from sympy import symbols, cyclotomic_poly, legendre_poly, chebyshevt_poly, hermite_poly
x = symbols('x')

cyclotomic_poly(5, x)         # x**4 + x**3 + x**2 + x + 1
legendre_poly(3, x)           # (2*x**3 - 3*x)/2
chebyshevt_poly(4, x)         # Chebyshev T_4
hermite_poly(3, x)            # Hermite H_3
```

## Gotchas

- **`Poly()` requires explicit generators** — always pass the variable: `Poly(expr, x)`.
- **`roots()` only works for low-degree polynomials** — use `all_roots()` (with `CRootOf`) or `nroots()` for degree ≥ 5.
- **Groebner basis order matters** — `order='lex'` is default and good for elimination; `order='grlex'` can be faster.
- **Domain affects factorization** — `factor(x**2 - 2)` gives irreducible result over QQ; use `extension=sqrt(2)` to factor over Q(√2).

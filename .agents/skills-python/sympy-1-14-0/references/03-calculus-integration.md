# Calculus and Integration Reference

## Differentiation

### Basic differentiation

```python
from sympy import symbols, diff, Derivative, sin, exp
x, y = symbols('x y')

# First derivative
diff(x**3, x)                    # 3*x**2
diff(sin(x), x)                  # cos(x)

# Higher-order derivatives
diff(x**4, x, x, x)             # 24*x
diff(x**4, x, 3)                # same: 24*x
diff(exp(x**2), x, x)           # 2*exp(x**2)*(1 + 2*x**2)

# Partial derivatives
diff(x**2 * y**3, x, y)         # 6*x*y

# Unevaluated derivative (for display/deferral)
Derivative(sin(x), x)           # d/dx sin(x)
Derivative(f(x, y), x, y)       # ∂²f/∂x∂y
```

### Implicit differentiation

```python
from sympy import symbols, Function, diff, solve
x = symbols('x')
y = Function('y')(x)

# dy/dx from implicit equation
eq = x**2 + y**2 - 1
deq = diff(eq, x)               # 2*x + 2*y*Derivative(y(x), x)
solve(deq, diff(y, x))          # solve for y'
```

## Integration

### Indefinite integrals

```python
from sympy import symbols, integrate, Integral, sin, exp
x = symbols('x')

# Definite integral
integrate(sin(x), (x, 0, pi))       # 2
integrate(x**2, (x, 0, 1))          # 1/3

# Indefinite integral
integrate(sin(x), x)                # -cos(x)
integrate(exp(-x**2), x)            # sqrt(pi)*erf(x)/2

# Unevaluated integral (display form)
Integral(sin(x)**3, (x, 0, pi))     # ∫₀^π sin³(x) dx
Integral(expr, x)                   # ∫ expr dx

# Multiple integrals
integrate(x*y, (x, 0, 1), (y, 0, 1))   # 1/4
```

### Integration techniques SymPy uses

SymPy's integrator tries multiple strategies automatically:
- Risch algorithm (for elementary functions)
- Polynomial/rational integration
- Trigonometric substitution
- Integration by parts
- Substitution
- Meijer G-function method (for special functions)

### When integration fails

```python
from sympy import integrate, Integral, sin

# If integrate can't find a closed form, it returns an unevaluated Integral
result = integrate(sin(x**2), x)
# Returns: sqrt(pi/2)*fresnels(sqrt(2)*x/sqrt(pi))

# Force manual steps
from sympy import substitution
# Break into parts and integrate manually
```

## Limits

```python
from sympy import symbols, limit, sin, exp, oo
x = symbols('x')

# Basic limits
limit(sin(x)/x, x, 0)            # 1
limit(1/x, x, oo)                # 0
limit(exp(x), x, oo)             # oo
limit(exp(-x), x, oo)            # 0

# One-sided limits
limit(1/x, x, 0, dir='+')       # oo
limit(1/x, x, 0, dir='-')       # -oo

# Limit from below/above
limit(x**x, x, 0, dir='+')      # 1 (0^0 → 1)
```

## Series Expansions

### Taylor/Maclaurin series

```python
from sympy import symbols, series, sin, exp, O
x = symbols('x')

# Taylor series around x=0 (Maclaurin)
series(sin(x), x, 0, 6)          # x - x**3/6 + x**5/120 + O(x**6)
series(exp(x), x, 0, 5)          # 1 + x + x**2/2 + x**3/6 + x**4/24 + O(x**5)

# Around a point other than 0
series(exp(x), x, 1, 4)          # e + e*(x-1) + e*(x-1)**2/2 + ...

# Remove order term
series(sin(x), x, 0, 6).removeO()   # x - x**3/6 + x**5/120
```

### Laurent and asymptotic series

```python
from sympy import symbols, series, exp, oo
x = symbols('x')

# Series at infinity
series(exp(1/x), x, oo)           # 1 + 1/x + 1/(2*x**2) + ...
```

### Formal power series

```python
from sympy import fps, symbols
x = symbols('x')
fps(sin(x))    # formal power series (infinite)
```

## Summation and Products

```python
from sympy import symbols, summation, Sum, product, Product
k, n = symbols('k n', integer=True)

# Definite sum
summation(k, (k, 1, n))           # n*(n + 1)/2
summation(k**2, (k, 1, n))        # n*(n + 1)*(2*n + 1)/6

# Infinite series
summation(1/k**2, (k, 1, oo))     # pi**2/6

# Unevaluated sum
Sum(k**2, (k, 1, n))              # Σ k²

# Products
product(k, (k, 1, n))             # n!
Product(1 - 1/k**2, (k, 2, oo))   # Π (1 - 1/k²)
```

## Residues and Contour Integration

```python
from sympy import symbols, residue, sin, cos
z = symbols('z')

# Residue at a point
residue(sin(z)/z**2, z, 0)       # 1
residue(1/(z**2 + 1), z, I)      # 1/(2*I)
```

## Fourier Series

```python
from sympy import symbols, fourier_series, pi, sin, exp
x, t = symbols('x t')

# Fourier series of a function on [-pi, pi]
f = fourier_series(x, (x, -pi, pi))
f.truncate(3)    # first 3 terms
```

## Gotchas

- **`integrate()` may hang on complex expressions** — set a timeout or break the integral into parts. Use `Integral()` for unevaluated form.
- **`diff(f(x), x)` requires `f` as a `Function`, not a `Symbol`** — use `f = Function('f')(x)`.
- **Series order term `O(x**n)` is a SymPy object** — use `.removeO()` to drop it before further manipulation.
- **`limit()` with oscillating functions** — `limit(sin(1/x), x, 0)` returns `AccumBounds(-1, 1)`, not a single value.
- **Definite integrals may return unevaluated** — if SymPy can't find an antiderivative, it returns `Integral(...)`. Try `meijerg=True` or numeric evaluation with `.evalf()`.
- **Integration constants are not added** — indefinite integrals omit `+ C`. Add manually if needed.

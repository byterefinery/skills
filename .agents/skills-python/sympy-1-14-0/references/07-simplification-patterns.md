# Simplification Patterns Reference

## General Simplification

### `simplify()` — the catch-all

```python
from sympy import symbols, simplify, sin, cos, exp, sqrt
x = symbols('x')

# Try many transformations, return shortest result
simplify(sin(x)**2 + cos(x)**2)        # 1
simplify(exp(I*pi))                     # -1
simplify(sqrt(x**2))                    # sqrt(x**2) (keeps unevaluated without assumptions)
simplify((x**2 - 1)/(x - 1))           # x + 1

# With positive assumption
x = symbols('x', positive=True)
simplify(sqrt(x**2))                    # x
```

### Why `simplify()` is not always best

`simplify()` tries many transformations and picks the shortest result by `count_ops()`. This heuristic may miss domain-specific simplifications. Use targeted functions instead:

| Function | Best for |
|---|---|
| `trigsimp()` | Trigonometric identities |
| `powsimp()` | Combining powers with same base |
| `exptrigsimp()` | Exponential-trig combinations |
| `radsimp()` | Rationalizing denominators |
| `ratsimp()` | Rational function simplification |
| `combsimp()` | Combinatorial/Gamma simplification |
| `gammasimp()` | Gamma function identities |
| `besselsimp()` | Bessel function relations |
| `signsimp()` | Sign/Abs simplification |
| `nsimplify()` | Float → exact rational |

## Trigonometric Simplification

```python
from sympy import symbols, trigsimp, sin, cos, tan, exptrigsimp, exp, I
x = symbols('x')

trigsimp(sin(x)**2 + cos(x)**2)         # 1
trigsimp(sin(2*x))                       # 2*sin(x)*cos(x)
trigsimp(tan(x))                         # sin(x)/cos(x)

# Exponential-trig
exptrigsimp(exp(I*x))                    # cos(x) + I*sin(x)
```

## Power Simplification

```python
from sympy import symbols, powsimp, powdenest, sqrt
x = symbols('x', positive=True)

powsimp(x**a * x**b)                     # x**(a+b)
powdenest((x**2)**(S(1)/2))              # x
```

## Collecting Terms

```python
from sympy import symbols, collect
x, a, b = symbols('x a b')

# Group by variable
expr = a*x**2 + b*x**2 + c*x + d
collect(expr, x)                         # (a+b)*x**2 + c*x + d

# Collect by pattern
collect(a*sin(x) + b*sin(x) + cos(x), sin(x))
# (a + b)*sin(x) + cos(x)
```

## Fraction Operations

```python
from sympy import symbols, fraction, numer, denom, cancel, together
x, y = symbols('x y')

expr = (x**2 - 1)/(x**2 + 2*x + 1)
num, den = fraction(expr)                # (x**2-1, x**2+2*x+1)
numer(expr)                              # x**2 - 1
denom(expr)                              # x**2 + 2*x + 1

cancel(expr)                             # cancel common factors
together(1/x + 1/y)                      # (x+y)/(x*y)
```

## Radical Simplification

```python
from sympy import symbols, radsimp, sqrtdenest, sqrt
x = symbols('x')

radsimp(1/sqrt(2))                       # sqrt(2)/2
sqrtdenest(sqrt(2) + sqrt(3))           # may simplify nested radicals
```

## Common Subexpression Elimination (CSE)

```python
from sympy import symbols, cse
x, y = symbols('x y')

# Find and factor out repeated subexpressions
expr1 = (x + y)**3 + (x + y)**2
expr2 = (x + y)**3 - (x + y)**2
replacements, reduced = cse([expr1, expr2])
# replacements: [(x0, x + y)]
# reduced: [x0**3 + x0**2, x0**3 - x0**2]
```

## Rationals and Numeric Simplification

```python
from sympy import symbols, nsimplify, pi, sqrt, Rational
x = symbols('x')

# Convert float to exact rational
nsimplify(0.333333333)                  # 1/3
nsimplify(3.14159265)                    # 355/113
nsimplify(sqrt(2).evalf())               # sqrt(2)

# With tolerance
nsimplify(0.333, tolerance=0.01)
```

## Risch-style Simplification (FU rules)

```python
from sympy import symbols, FU, fu, exp
x = symbols('x')

# Apply Risch-style simplification rules
fu(expr)
FU('FU11')(expr)   # specific rule
```

## Logarithm Manipulation

```python
from sympy import symbols, logcombine, expand_log, log, sqrt
x, y = symbols('x y', positive=True)

logcombine(log(x) + log(y))              # log(x*y)
logcombine(2*log(x))                     # log(x**2)
expand_log(log(x**2 * y), force=True)    # 2*log(x) + log(y)
```

## Combinatorial Simplification

```python
from sympy import symbols, combsimp, factorial, binomial
n, k = symbols('n k', integer=True)

combsimp(factorial(n)/factorial(n-1))    # n
combsimp(binomial(n, k))                 # may simplify
```

## Gotchas

- **`simplify()` is expensive** — it tries dozens of transformations. Use targeted simplifiers for performance.
- **`simplify()` does not always return the "simplest" form** — it returns the one with fewest `count_ops()`. Sometimes a longer expression is more useful.
- **Assumptions matter** — `simplify(sqrt(x**2))` stays as `sqrt(x**2)` unless `x` is declared positive.
- **`expand_log()` needs `force=True`** for expressions where SymPy cannot verify the log identities hold (e.g., with complex arguments).
- **CSE creates temporary symbols** — the replacement variables are named `x0`, `x1`, etc. Rename if needed.
- **`nsimplify()` is heuristic** — it may find wrong rationals for noisy floats. Use tolerance carefully.

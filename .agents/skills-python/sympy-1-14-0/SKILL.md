---
name: sympy-1-14-0
description: >
  Symbolic mathematics with SymPy 1.14.0 — algebra, calculus, ODE/PDE solving, matrices,
  number theory, geometry, special functions, transforms, and code generation. Use when
  the user needs symbolic computation, equation solving, differentiation, integration,
  series expansion, matrix operations, polynomial manipulation, simplification, or any
  CAS (computer algebra system) task in Python. Also use for exact arithmetic with
  rationals, symbolic constants (pi, E), or converting expressions to LaTeX/C/Fortran.
---

# sympy 1.14.0

SymPy is a pure-Python computer algebra system. It handles symbolic expressions, equation solving, calculus, linear algebra, discrete math, geometry, number theory, and more — all with exact (not floating-point) results by default. Requires Python 3.9+ and `mpmath`.

## Overview

SymPy's core model: everything is an **expression tree** built from `Symbol`, `Number`, `Function`, and operator nodes (`Add`, `Mul`, `Pow`). Expressions are immutable. Key workflow:

1. **Declare symbols**: `x, y = symbols('x y')` or `var('x y')`
2. **Build expressions**: `expr = x**2 + sin(y)`
3. **Manipulate**: `expand(expr)`, `simplify(expr)`, `diff(expr, x)`
4. **Substitute**: `expr.subs(x, 3)` or `expr.subs({x: a, y: b})`
5. **Evaluate**: `expr.evalf()` for numeric approximation, `N(expr, 15)` for 15-digit precision
6. **Solve**: `solve(eq, x)`, `dsolve(ode, y(x))`, `integrate(f, x)`

### Import patterns

```python
# Common idiom — import everything from sympy
from sympy import *
x, y, z = symbols('x y z')

# Or selective imports
from sympy import Symbol, symbols, sin, cos, integrate, diff, solve
from sympy.abc import x, y, z  # pre-defined common symbols
```

### Key design principles

- **Immutable expressions** — `expr = x + 1; expr += 1` does NOT modify `expr`. Use `expr = expr + 1`.
- **Exact by default** — `sqrt(2)` stays as `√2`, not `1.414...`. Call `.evalf()` when you need floats.
- **Unevaluated forms** — `Mul(a, b, evaluate=False)` prevents automatic simplification. Use `UnevaluatedExpr` or `evaluate=False` keyword.
- **Singleton constants** — `S.Zero`, `S.One`, `S.Infinity`, `S.NaN`, `S.pi`, `S.E`, `S.I` are cached singletons.

## Usage

### Quick reference by domain

| Task | Function(s) |
|---|---|
| Symbolic variables | `symbols('x y z')`, `var('x y')`, `Symbol('x', real=True)` |
| Algebraic expansion | `expand()`, `expand_mul()`, `expand_log()` |
| Factorization | `factor()`, `factor_list()` |
| Simplification | `simplify()`, `trigsimp()`, `powsimp()`, `ratsimp()` |
| Differentiation | `diff(f, x)`, `Derivative(f, x, x)` (unevaluated) |
| Integration | `integrate(f, x)`, `Integral(f, x)` (unevaluated) |
| Limits | `limit(f, x, oo)`, `limit(f, x, 0, dir='+')` |
| Series | `series(f, x, 0, 6)`, `O(x**6)` |
| Equation solving | `solve(eq, x)`, `solveset(eq, x, S.Reals)` |
| ODE solving | `dsolve(ode, y(x))`, `classify_ode(ode)` |
| Linear systems | `linsolve(eqs, (x, y))`, `linear_eq_to_matrix()` |
| Matrices | `Matrix([[1,2],[3,4]])`, `.det()`, `.eigenvals()` |
| Polynomials | `Poly(f, x)`, `degree()`, `groebner()`, `resultant()` |
| Number theory | `isprime(n)`, `factorint(n)`, `gcd(a, b)` |
| Summation/product | `summation(f, (k, 0, n))`, `product(f, (k, 1, n))` |
| Discrete transforms | `fft()`, `ntt()`, `fwht()` |
| Integral transforms | `laplace_transform()`, `fourier_transform()` |
| Geometry | `Point(1, 2)`, `Line(p1, p2)`, `Circle(center, r)` |
| Boolean logic | `And(a, b)`, `Or(a, b)`, `simplify_logic()` |
| Code generation | `ccode()`, `fcode()`, `latex()`, `rcode()` |
| Parsing strings | `parse_expr("x**2 + 1")` |
| Numeric evaluation | `expr.evalf()`, `N(expr, 15)` |
| Plotting | `plot(f)`, `plot3d(f)`, `plot_implicit(eq)` |

### Common patterns

```python
# Symbolic function
from sympy import Function, symbols
t = symbols('t')
y = Function('y')(t)  # y(t) as a symbolic function

# Assumptions on symbols
x = Symbol('x', positive=True, real=True)
n = Symbol('n', integer=True)

# Piecewise expressions
from sympy import Piecewise
f = Piecewise((x**2, x > 0), (0, True))

# Unevaluated integral/derivative (display form)
from sympy import Integral, Derivative
uneval_integral = Integral(sin(x)**3, (x, 0, pi))
uneval_deriv = Derivative(f, x, x)

# Substitution with multiple symbols
expr.subs([(x, 1), (y, 2)])
expr.subs({x: a + b, y: a - b})

# Extract numerator/denominator
from sympy import numer, denom, fraction
numer(expr), denom(expr)

# Collect terms
from sympy import collect
collect(a*x**2 + b*x**2 + c*x, x)  # (a+b)*x**2 + c*x
```

## Gotchas

- **`symbols()` creates independent symbols each call** — `symbols('x') != symbols('x')`. Reuse the same symbol object or use `var('x')` which assigns to local namespace.
- **Integer division produces exact rationals** — `1/2` in SymPy context gives `1/2` (Rational), not `0.5`. Use `S(1)/2` or `Rational(1, 2)` explicitly.
- **`solve()` returns lists, `solveset()` returns Sets** — `solve(x**2 - 1, x)` → `[-1, 1]`; `solveset(x**2 - 1, x)` → `{−1, 1}`. Prefer `solveset` for newer code; it handles domains properly.
- **`oo` is positive infinity** — there is no negative infinity symbol. Use `-oo`. `zoo` is complex infinity (different from `oo`).
- **SymPy expressions are immutable** — methods like `.subs()` return new expressions. Never assume in-place modification.
- **`expand()` can be slow on large expressions** — use targeted expanders: `expand_mul()`, `expand_log()`, `expand_trig()` instead of full `expand()`.
- **`simplify()` is a heuristic** — it tries many transformations and returns the "shortest" result. It may not find the simplest form. Use domain-specific simplifiers: `trigsimp()`, `powsimp()`, `radsimp()`, `combsimp()`.
- **`dsolve()` needs `Function('y')(x)` not bare `y`** — define ODE functions as `y = Function('y')(x)`, not `y = Symbol('y')`.
- **Matrix indexing is `[row, col]`** — consistent with mathematical convention, not C-style flat indexing.
- **`equals()` vs `==`** — `expr1 == expr2` checks structural equality (same tree). Use `expr1.equals(expr2)` for mathematical equality, or `simplify(expr1 - expr2) == 0`.
- **`limit()` direction matters** — `limit(1/x, x, 0)` may return `nan` if left/right limits differ. Use `dir='+'` or `dir='-'`.
- **Polynomial domain matters** — `Poly(f, x, domain='QQ')` vs `domain='ZZ'` affects factorization and root-finding behavior.
- **`lambdify()` for numeric speed** — when you need to evaluate a SymPy expression millions of times, convert it to a NumPy function: `f = lambdify(x, expr, 'numpy')`.

## References

- [01-core-expressions](references/01-core-expressions.md) — Symbols, expressions, numbers, assumptions, traversal
- [02-algebra-polynomials](references/02-algebra-polynomials.md) — Polynomial rings, factoring, Groebner bases, root finding
- [03-calculus-integration](references/03-calculus-integration.md) — Derivatives, integrals, limits, series expansions
- [04-solvers-equations](references/04-solvers-equations.md) — Algebraic solving, ODE/PDE, inequalities, recurrences
- [05-matrices-linear-algebra](references/05-matrices-linear-algebra.md) — Matrix construction, operations, eigenvalues, decompositions
- [06-special-functions](references/06-special-functions.md) — Gamma, Bessel, elliptic, hypergeometric, orthogonal polynomials
- [07-simplification-patterns](references/07-simplification-patterns.md) — simplify family, collect, fraction, CSE
- [08-number-theory](references/08-number-theory.md) — Primes, factorization, modular arithmetic, continued fractions
- [09-geometry](references/09-geometry.md) — Points, lines, circles, polygons, intersections
- [10-transforms-discrete](references/10-transforms-discrete.md) — Laplace, Fourier, Mellin, FFT, NTT
- [11-printing-codegen](references/11-printing-codegen.md) — LaTeX, pretty print, C/Fortran/R code generation
- [12-physics-modules](references/12-physics-modules.md) — Quantum mechanics, rigid body dynamics, units

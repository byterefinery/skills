# Solvers and Equations Reference

## Algebraic Equation Solving

### `solve()` — legacy solver

```python
from sympy import symbols, solve, sin
x, y = symbols('x y')

# Single equation
solve(x**2 - 4, x)               # [-2, 2]
solve(x**3 - x, x)               # [-1, 0, 1]

# Equation form: pass expression (assumes = 0) or Eq
solve(x**2 - 4, x)
solve(Eq(x**2, 4), x)            # same result

# System of equations
solve([x + y - 3, x*y - 2], (x, y))   # [(1, 2), (2, 1)]

# Trig equations
solve(sin(x), x)                 # [0, pi]

# Get solutions as dict
solve([x + y - 3, x - y - 1], dict=True)
# [{x: 2, y: 1}]
```

### `solveset()` — modern solver (preferred)

Returns a `Set` of solutions with domain awareness:

```python
from sympy import symbols, solveset, S, sin, exp
x = symbols('x')

# Single equation over complex numbers (default)
solveset(x**2 - 4, x)           # {-2, 2}
solveset(x**2 - 4, x, domain=S.Reals)   # {-2, 2}

# Domain-restricted solving
solveset(exp(x) - 1, x, domain=S.Reals)    # {0}
solveset(sin(x), x, domain=S.Reals)        # {n*pi | n in Z}

# System of linear equations
from sympy import linsolve
linsolve([x + y - 3, x - y - 1], (x, y))   # {(2, 1)}

# Nonlinear systems
from sympy import nonlinsolve
nonlinsolve([x**2 + y**2 - 5, x + y - 3], (x, y))
```

### `nsolve()` — numerical solving

```python
from sympy import symbols, nsolve, sin
x = symbols('x')

# Numerical solution with initial guess
nsolve(x**3 - x - 1, 1)          # 1.3247...
nsolve([x**2 + y**2 - 5, x + y - 3], (x, y), (1, 1))
```

## ODE Solving

### Defining ODEs

```python
from sympy import symbols, Function, dsolve, Derivative, Eq, sin, exp
t = symbols('t')
y = Function('y')(t)
x = Function('x')(t)

# First-order: y' = y
ode1 = Eq(y.diff(t), y)
dsolve(ode1, y)                  # y(t) = C1*exp(t)

# Second-order: y'' + y = 0
ode2 = Eq(y.diff(t, t) + y, 0)
dsolve(ode2, y)                  # y(t) = C1*sin(t) + C2*cos(t)

# With initial conditions
from sympy import bc
dsolve(ode2, y, ics={y.subs(t, 0): 1, y.diff(t).subs(t, 0): 0})
# y(t) = cos(t)
```

### Classifying ODEs

```python
from sympy import classify_ode

# See what methods SymPy can use
classify_ode(Eq(y.diff(t), y), y)
# ['factorable', '1st_linear', 'separable', ...]

# Choose a specific method
dsolve(ode, y, hint='separable')
```

### System of ODEs

```python
from sympy import symbols, Function, dsolve, Eq
t = symbols('t')
x = Function('x')(t)
y = Function('y')(t)

system = [
    Eq(x.diff(t), y),
    Eq(y.diff(t), -x)
]
dsolve(system)
```

## PDE Solving

```python
from sympy import symbols, Function, pdsolve, classify_pde, Derivative
x, t = symbols('x t')
u = Function('u')(x, t)

# Heat equation: u_t = u_xx
heat_eq = Eq(Derivative(u, t), Derivative(u, x, x))
classify_pde(heat_eq, u)
pdsolve(heat_eq, u)
```

## Inequalities

```python
from sympy import symbols, solve_univariate_inequality, reduce_inequalities, S
x = symbols('x', real=True)

# Single inequality
solve_univariate_inequality(x**2 - 4 > 0, x, domain=S.Reals)
# (x < -2) | (x > 2)

# System of inequalities
reduce_inequalities([x > 0, x**2 < 4], x)
# (0 < x) & (x < 2)
```

## Recurrence Relations

```python
from sympy import symbols, Function, rsolve
n = symbols('n')
f = Function('f')

# f(n) = 2*f(n-1) + 1, f(0) = 1
rsolve(f(n) - 2*f(n-1) - 1, f, {f(0): 1})
# 2**n - 1
```

## Diophantine Equations

```python
from sympy import symbols, diophantine
x, y = symbols('x y', integer=True)

# x^2 + y^2 = 25
diophantine(x**2 + y**2 - 25)
# parametric family of solutions
```

## Linear Systems (Matrix Form)

```python
from sympy import symbols, linear_eq_to_matrix, linsolve, Matrix
x, y, z = symbols('x y z')

# Convert equations to Ax = b form
eqs = [2*x + y - z - 3, x - y + z - 1, 3*x + 2*y - z - 5]
A, b = linear_eq_to_matrix(eqs, (x, y, z))
# A is the coefficient matrix, b is the constants vector

# Solve
linsolve((A, b), (x, y, z))
```

## Gotchas

- **`solve()` returns a list; `solveset()` returns a Set** — use `solveset()` for domain-aware solving. The legacy `solve()` can miss solutions or return conditional expressions.
- **Always define ODE functions as `Function('y')(x)`** — using a bare `Symbol('y')` will not work with `dsolve()`.
- **`dsolve()` may return implicit solutions** — some ODEs cannot be solved explicitly for `y(x)`. Check the result structure.
- **Initial conditions syntax** — use `ics={expr: value}` dict, e.g., `{y.subs(t, 0): 1}`.
- **`nsolve()` needs a good initial guess** — poor guesses lead to convergence failure or wrong roots.
- **Inequalities require real symbols** — declare `x = Symbol('x', real=True)` or solving may fail silently.
- **`solve()` on transcendental equations** — it finds a finite set of solutions but may miss infinite families. Use `solveset()` for complete results.

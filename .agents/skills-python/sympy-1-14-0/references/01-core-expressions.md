# Core Expressions Reference

## Symbols and Variables

### Creating symbols

```python
from sympy import Symbol, symbols, var

# Single symbol
x = Symbol('x')
x = symbols('x')  # shorthand

# Multiple symbols (returns tuple)
x, y, z = symbols('x y z')
a, b, c = symbols('a:3')  # a, b, c
m1, m2, m3 = symbols('m1:4')  # m1, m2, m3

# Pre-defined common symbols
from sympy.abc import x, y, z, t, s, n, k

# Assign to local namespace (convenient in notebooks)
var('x y z')  # creates x, y, z as local variables
```

### Symbol assumptions

Assumptions are declared at creation time and cannot be changed later. They guide simplification.

```python
x = Symbol('x', real=True, positive=True)
n = Symbol('n', integer=True, nonnegative=True)
k = Symbol('k', integer=True)
t = Symbol('t', real=True)
z = Symbol('z')  # complex by default (no assumptions)

# Common assumption keywords
#   real, imaginary, finite, infinite
#   zero, nonzero, even, odd
#   positive, negative, nonnegative, nonpositive
#   integer, rational, algebraic, transcendental
#   commutative (default True), complex
```

### Dummy symbols

Use `Dummy` for bound variables in expressions to avoid name clashes:

```python
from sympy import Dummy
k = Dummy('k')  # unique symbol each call
# Useful in summation/indexing contexts
```

## Expression Types

### The expression hierarchy

```
Basic
 └── Atom (leaf nodes)
      ├── Symbol
      ├── Number (Integer, Rational, Float, NumberSymbol like pi, E)
      └── FunctionClass
 └── Expr (mathematical expressions)
      ├── Add  (sum of terms)
      ├── Mul  (product of factors)
      ├── Pow  (base**exponent)
      ├── Function (applied function: sin(x), gamma(z))
      ├── Derivative
      ├── Integral
      └── Rel (Eq, Ne, Lt, Le, Gt, Ge — relations)
```

### Inspecting expressions

```python
from sympy import symbols, sin, cos
x, y = symbols('x y')
expr = x**2 + 2*sin(y) + 3

# Structure
expr.func          # Add
expr.args          # (x**2, 2*sin(y), 3)
expr.is_Add        # True
expr.is_Mul        # False
expr.is_atomic     # False

# Free symbols
expr.free_symbols   # {x, y}

# Check if expression contains something
expr.has(x)         # True
expr.has(sin)       # True
expr.has(y**2)      # False (y is there but not y**2)

# Atom extraction
expr.atoms()              # all atoms: {x, y, 2, 3}
expr.atoms(Symbol)        # {x, y}
expr.atoms(Number)        # {2, 3}

# Degree and operations count
expr.degree(x)     # 2
count_ops(expr)    # number of operations (complexity measure)
```

### Expression traversal

```python
from sympy import preorder_traversal, postorder_traversal

# Walk the expression tree
for node in preorder_traversal(expr):
    print(node.func, node.args)

# Map function over subexpressions
expr.replace(lambda x: x.is_number, lambda x: x*2)
```

## Numbers

### Exact numbers

```python
from sympy import Integer, Rational, Float, S

Integer(42)       # exact integer
Rational(1, 3)    # exact 1/3 (not 0.333...)
S(1)/3            # same as Rational(1, 3)
Float('1.4142135623730951')  # arbitrary precision float
```

### Mathematical constants (singletons via `S`)

```python
from sympy import S, pi, E, I, oo, nan, zoo, Catalan, EulerGamma, GoldenRatio

S.Zero     # exact 0
S.One      # exact 1
S.NegativeOne
S.Half     # exact 1/2
S.Infinity # oo (positive infinity)
S.NaN      # nan
S.pi       # pi
S.E        # E (Euler's number)
S.I        # I (imaginary unit)

# Use -oo for negative infinity, not S.NegativeInfinity
```

### Numeric evaluation

```python
from sympy import N, sqrt, pi

sqrt(2).evalf()          # 1.41421356237309
N(sqrt(2), 50)           # 50 digits of precision
pi.evalf(n=20)           # 20 digits
(sin(pi/3)).evalf()      # 0.866025403784439

# Symbolic to numeric with substitutions
expr = x**2 + sin(y)
expr.subs({x: 3, y: pi/4}).evalf()
```

## Substitution

```python
from sympy import symbols, sin
x, y, z = symbols('x y z')
expr = x**2 + sin(y)

# Single substitution
expr.subs(x, 3)           # 9 + sin(y)
expr.subs(x, z)           # z**2 + sin(y)

# Multiple substitutions (dict or list of tuples)
expr.subs({x: 1, y: pi/2})
expr.subs([(x, 1), (y, pi/2)])

# Simultaneous substitution (use simultaneous=True to avoid cascading)
(x + y).subs({x: y, y: x}, simultaneous=True)  # x + y (swapped)

# Wildcard substitution
from sympy import Wild
w = Wild('w')
(expr**2).subs(w**2, sin(w))
```

## Lambda and Functions

```python
from sympy import Lambda, Function, symbols

# Symbolic lambda
f = Lambda(x, x**2 + 1)
f(3)  # 10

# Named symbolic function
F = Function('F')
F(x)  # F(x) — unevaluated symbolic function

# Define a custom function class
from sympy import Function
class my_func(Function):
    @classmethod
    def eval(cls, x):
        if x == 0:
            return S.Zero
```

## Equality and Comparison

```python
from sympy import Eq, Ne, Lt, Le, Gt, Ge, symbols

x = symbols('x')

# Symbolic relations (not evaluated)
Eq(x**2, 4)      # x**2 = 4
Ne(x, 0)         # x ≠ 0
Lt(x, 5)         # x < 5
Le(x, 5)         # x ≤ 5

# Structural equality vs mathematical equality
a = (x + 1)**2
b = x**2 + 2*x + 1
a == b           # False (different tree structure)
a.equals(b)      # True (mathematically equal)
simplify(a - b) == 0  # True

# Use simplify() difference test for complex expressions
from sympy import simplify
simplify(expr1 - expr2) == 0
```

## Common Gotchas

- **`Symbol('x') != Symbol('x')`** — each call creates a new object. Reuse symbols or use `var()`.
- **`S(x)` vs `sympify(x)`** — `S()` converts to SymPy singleton/number; `sympify()` is the general converter.
- **Integer division in Python 3** — `1/2` gives Python float `0.5`. In SymPy, use `S(1)/2` or `Rational(1,2)` for exact rational.
- **`expr.has(Symbol('x'))` fails** if the symbol is a different instance. Use the same symbol object or match by name: `any(s.name == 'x' for s in expr.free_symbols)`.

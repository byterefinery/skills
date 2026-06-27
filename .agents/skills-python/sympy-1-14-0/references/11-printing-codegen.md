# Printing and Code Generation Reference

## Pretty Printing

```python
from sympy import symbols, pprint, pretty, sqrt
x = symbols('x')
expr = sqrt(x**2 + 1)

# Pretty print to console
pprint(expr)
pprint(expr, use_unicode=True)
pprint(expr, use_unicode=False)   # ASCII mode

# Return as string
pretty(expr)                      # unicode pretty string
pretty(expr, use_unicode=False)   # ASCII
```

## LaTeX Output

```python
from sympy import symbols, latex, print_latex, multiline_latex, sqrt, sin
x = symbols('x')
expr = sin(x)/sqrt(x**2 + 1)

# Single-line LaTeX
latex(expr)                       # \\frac{\\sin{\\left(x \\right)}}{\\sqrt{x^{2} + 1}}

# Print to console
print_latex(expr)

# Multi-line (for complex expressions)
multiline_latex(expr)

# With mode control
latex(expr, mode='plain')         # no $...$ wrapper
latex(expr, mode='equation')      # $$ ... $$
latex(expr, mode='inline')        # $ ... $
```

## String Representations

```python
from sympy import symbols, srepr, sstr
x = symbols('x')
expr = x**2 + 1

# Internal representation (for debugging)
srepr(expr)                       # "Add(Pow(Symbol('x'), Integer(2)), Integer(1))"
sstr(expr)                        # 'x**2 + 1'

# Tree view
from sympy import print_tree
print_tree(expr)
```

## Code Generation

### C Code

```python
from sympy import symbols, ccode, sin, cos, sqrt, exp
x, y = symbols('x y')
expr = sin(x) + cos(y)*sqrt(x**2 + y**2)

ccode(expr)
# sin(x) + cos(y)*sqrt(x*x + y*y)

# With user-defined function mappings
ccode(expr, user_functions={'sin': 'mysin', 'cos': 'mycos'})
```

### Fortran Code

```python
from sympy import fcode, cxxcode
fcode(expr)
cxxcode(expr)
```

### Other Languages

```python
from sympy import rcode, jscode, julia_code, mathematica_code, octave_code, rust_code, maple_code, pycode

rcode(expr)           # R code
jscode(expr)          # JavaScript
julia_code(expr)      # Julia
mathematica_code(expr) # Mathematica
octave_code(expr)     # Octave/MATLAB
rust_code(expr)       # Rust
maple_code(expr)      # Maple
pycode(expr)          # Python (sympy-free if possible)
```

### Code with Derivatives

```python
from sympy import symbols, Function, diff, ccode
t = symbols('t')
y = Function('y')(t)
dy = diff(y, t)

ccode(dy)             # y'(t) → derivative representation
```

## MathML Output

```python
from sympy import symbols, mathml, print_mathml
x = symbols('x')
expr = x**2 + 1

mathml(expr)
print_mathml(expr)
```

## DOT Graphviz Output

```python
from sympy import symbols, dotprint
x = symbols('x')
expr = (x + 1)**2

dotprint(expr)        # DOT format for graphviz
```

## Expression Parsing

```python
from sympy import parse_expr, symbols

# Parse string to SymPy expression
expr = parse_expr("x**2 + sin(y)")
expr = parse_expr("x**2 + 1", local_dict={'x': symbols('x')})

# Local variable mapping
local_vars = {'x': symbols('x'), 'y': symbols('y')}
parse_expr("x**2 + y", local_dict=local_vars)

# Transformations
parse_expr("1/2")                     # Python float 0.5
parse_expr("1/2", transformations='all')  # SymPy Rational(1, 2)
```

## Lambdify (Numeric Functions)

```python
from sympy import symbols, lambdify, sin, exp
x, y = symbols('x y')
expr = sin(x) * exp(-y)

# Convert to callable Python function
f = lambdify((x, y), expr, module='math')
f(0.5, 1.0)               # numeric evaluation

# With NumPy (for array operations)
f_np = lambdify((x, y), expr, module='numpy')
import numpy as np
f_np(np.array([0, 1, 2]), np.array([1, 2, 3]))

# Multiple modules
f_mixed = lambdify(x, expr, modules=['numpy', 'math'])
```

## Preview and Plotting

```python
from sympy import symbols, preview, plot
x = symbols('x')
expr = x**2 - 1

# LaTeX preview (requires dvipng or similar)
preview(expr, viewer='file', filename='expr.png')

# Quick plots
plot(x**2, (x, -5, 5))
plot(sin(x), cos(x), (x, -10, 10))
```

## Gotchas

- **`latex()` wraps in `$...$` by default** — use `mode='plain'` for bare LaTeX.
- **`ccode()` does not handle all SymPy functions** — special functions like `gamma()`, `erf()` need manual mapping via `user_functions`.
- **`parse_expr("1/2")` gives Python float** — use `transformations='all'` or `Rational(1, 2)` for exact rational.
- **`lambdify()` with NumPy broadcasts arrays** — ensure your expression is element-wise compatible.
- **Code generators may produce inefficient code** — they translate directly; simplify the expression first for cleaner output.
- **`preview()` requires LaTeX installation** — needs `dvipng`, `ghostscript`, or similar tools installed on the system.

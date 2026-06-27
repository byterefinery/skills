# Special Functions Reference

## Gamma and Related Functions

```python
from sympy import symbols, gamma, factorial, binomial, rising_factorial
z = symbols('z')

# Gamma function: Γ(z) = (z-1)!
gamma(5)              # 24 (= 4!)
gamma(S(1)/2)         # sqrt(pi)
gamma(z + 1)          # z*gamma(z)

# Factorial
factorial(5)          # 120
factorial(z)          # symbolic

# Double factorial
from sympy import factorial2
factorial2(7)         # 7*5*3*1 = 105

# Binomial coefficient
binomial(10, 3)       # 120
binomial(n, k)        # symbolic C(n,k)

# Rising/falling factorials
rising_factorial(x, n)    # x*(x+1)*...*(x+n-1)
falling_factorial(x, n)   # x*(x-1)*...*(x-n+1)
```

## Error Functions

```python
from sympy import symbols, erf, erfc, erfi, erfinv
z = symbols('z')

erf(z)       # error function
erfc(z)      # complementary: 1 - erf(z)
erfi(z)      # imaginary error function
erfinv(z)    # inverse error function

# Special values
erf(0)       # 0
erf(oo)      # 1
```

## Bessel Functions

```python
from sympy import symbols, besselj, bessely, besseli, besselk, jn, yn
x, n = symbols('x n')

# Bessel J (first kind)
besselj(n, x)     # J_n(x)
jn(3, x)          # J_3(x) — integer order shorthand

# Bessel Y (second kind / Weber)
bessely(n, x)     # Y_n(x)

# Modified Bessel I
besseli(n, x)     # I_n(x)

# Modified Bessel K
besselk(n, x)     # K_n(x)

# Hankel functions
from sympy import hankel1, hankel2
hankel1(n, x)
hankel2(n, x)

# Roots
from sympy import jn_zeros
jn_zeros(0, 5)    # first 5 zeros of J_0
```

## Airy Functions

```python
from sympy import symbols, airyai, airybi, airyaiprime, airybiprime
x = symbols('x')

airyai(x)         # Ai(x)
airybi(x)         # Bi(x)
airyaiprime(x)    # Ai'(x)
airybiprime(x)    # Bi'(x)
```

## Elliptic Integrals

```python
from sympy import symbols, elliptic_k, elliptic_f, elliptic_e, elliptic_pi
k, phi = symbols('k phi')

elliptic_k(k)     # complete K(k)
elliptic_f(phi, k) # incomplete F(φ|k)
elliptic_e(k)     # complete E(k)
elliptic_pi(n, k) # complete Π(n|k)
```

## Orthogonal Polynomials

```python
from sympy import symbols, legendre, hermite, chebyshevt, chebyshevu, laguerre, jacobi
x, n = symbols('x n')

# Legendre
legendre(3, x)       # (2*x**3 - 3*x)/2

# Hermite (physicists')
hermite(3, x)        # 8*x**3 - 12*x

# Chebyshev T
chebyshevt(4, x)     # 8*x**4 - 8*x**2 + 1

# Chebyshev U
chebyshevu(3, x)     # 16*x**4 - 12*x**2 + 1

# Laguerre
laguerre(3, x)       # (-x**3 + 9*x**2 - 18*x + 6)/6

# Jacobi
jacobi(3, x, alpha=0, beta=0)   # reduces to Legendre
```

## Hypergeometric Functions

```python
from sympy import symbols, hyper, meijerg
a, b, c, z = symbols('a b c z')

# Generalized hypergeometric function
hyper([a, b], [c], z)      # ₂F₁(a,b;c;z)
hyper([1], [2], z)         # (exp(z)-1)/z

# Meijer G-function
meijerg([], [], [1], [0], z)
```

## Zeta and Related Functions

```python
from sympy import symbols, zeta, dirichlet_eta
s = symbols('s')

zeta(2)             # pi**2/6
zeta(4)             # pi**4/90
zeta(s)             # symbolic Riemann zeta
dirichlet_eta(s)    # Dirichlet eta function
```

## Spherical Harmonics

```python
from sympy import symbols, Ynm
l, m, theta, phi = symbols('l m theta phi')

Ynm(2, 0, theta, phi)   # Y_{2,0}(θ, φ)
```

## Delta and Heaviside

```python
from sympy import symbols, DiracDelta, Heaviside
x = symbols('x')

DiracDelta(x)       # δ(x)
Heaviside(x)        # θ(x): 0 if x<0, 1 if x>0
Heaviside(0)        # 1/2 (convention)
```

## Exponential Integral

```python
from sympy import symbols, Ei, expint, E1, li, Li
x = symbols('x')

Ei(x)           # exponential integral Ei(x)
E1(x)           # E_1(x)
expint(n, x)    # E_n(x)
li(x)           # offset logarithmic integral
Li(x)           # logarithmic integral
```

## Trigonometric and Hyperbolic

### Elementary trig functions
```python
from sympy import sin, cos, tan, sec, csc, cot, sinc
# Inverses: asin, acos, atan, asec, acsc, acot
```

### Hyperbolic functions
```python
from sympy import sinh, cosh, tanh, coth, sech, csch
# Inverses: asinh, acosh, atanh, acoth, asech, acsch
```

## Gotchas

- **`gamma(n)` for integer n gives `(n-1)!`** — not `n!`. Use `factorial(n)` for n!.
- **Bessel functions with symbolic order are slow to evaluate numerically** — fix the order first.
- **`chebyshevt()` and `chebyshevu()` use different conventions** — T_n uses cos(n·arccos(x)), U_n uses sin((n+1)·arccos(x))/sin(arccos(x)).
- **`zeta(1)` diverges** — returns `zeta(1)` unevaluated.
- **Special functions may not simplify automatically** — use `hyperexpand()` to expand hypergeometric functions into elementary forms when possible.

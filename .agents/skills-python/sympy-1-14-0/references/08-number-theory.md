# Number Theory Reference

## Primality and Prime Generation

```python
from sympy import isprime, prime, primerange, nextprime, prevprime, randprime

# Primality testing (deterministic)
isprime(17)           # True
isprime(10**20 + 19)  # True (large number)

# Prime generation
prime(1)              # 2 (1st prime)
prime(10)             # 29 (10th prime)
primepi(100)          # 25 (number of primes ≤ 100)

# Ranges
list(primerange(10, 30))   # [11, 13, 17, 19, 23, 29]
nextprime(17)             # 19
prevprime(17)             # 13
randprime(1, 100)         # random prime in [1, 100)

# Sieve of Eratosthenes (lazy)
from sympy import sieve
sieve.extend(100)
list(sieve._list)          # primes up to 100
```

## Factorization

```python
from sympy import factorint, divisors, divisor_count, divisor_sigma, primefactors

# Prime factorization: {prime: exponent}
factorint(12)           # {2: 2, 3: 1}
factorint(100)          # {2: 2, 5: 2}

# Divisors
divisors(12)            # [1, 2, 3, 4, 6, 12]
proper_divisors(12)     # [1, 2, 3, 4, 6]
divisor_count(12)       # 6
divisor_sigma(12)       # 28 (sum of divisors)

# Prime factors (without multiplicities)
primefactors(12)        # [2, 3]
```

## GCD and LCM

```python
from sympy import gcd, lcm, igcd, ilcm

gcd(12, 18)             # 6
lcm(12, 18)             # 36
igcd(12, 18)            # same (integer GCD, faster)

# Extended GCD
from sympy import gcdex
g, s, t = gcdex(12, 18) # g=6, s*12 + t*18 = 6
```

## Modular Arithmetic

```python
from sympy import mod_inverse, is_quad_residue, sqrt_mod, discrete_log

# Modular inverse
mod_inverse(3, 7)       # 5 (since 3*5 ≡ 1 mod 7)

# Quadratic residues
is_quad_residue(2, 7)   # True
sqrt_mod(2, 7)          # 3 (since 3^2 ≡ 2 mod 7)

# Discrete logarithm
discrete_log(7, 3, 5)   # k such that 7^k ≡ 3 mod 5
```

## Number-Theoretic Functions

```python
from sympy import totient, mobius, euler, bernoulli, harmonic

# Euler's totient
totient(12)             # 4 (numbers coprime to 12 in [1,12])

# Möbius function
mobius(1)               # 1
mobius(6)               # 1 (square-free, 2 prime factors → (-1)^2)
mobius(4)               # 0 (not square-free)

# Bernoulli numbers
bernoulli(4)            # -1/30

# Harmonic numbers
harmonic(5)             # 1 + 1/2 + 1/3 + 1/4 + 1/5 = 137/60
```

## Legendre, Jacobi, Kronecker Symbols

```python
from sympy import legendre_symbol, jacobi_symbol, kronecker_symbol

legendre_symbol(2, 7)    # 1 (2 is a quadratic residue mod 7)
jacobi_symbol(2, 15)     # -1
kronecker_symbol(2, 0)   # 0
```

## Continued Fractions

```python
from sympy import continued_fraction, continued_fraction_convergents
from sympy import sqrt, Rational

# Continued fraction of a number
list(continued_fraction(sqrt(2)))[:5]    # [1, 2, 2, 2, 2]
list(continued_fraction(Rational(22, 7)))  # [3, 7]

# Convergents
list(continued_fraction_convergents(sqrt(2)))[:5]
# [1, 3/2, 7/5, 17/12, 41/29]

# Periodic continued fraction (for quadratic irrationals)
continued_fraction_periodic(a=0, q=1, periodic=[2])   # √2
```

## Egyptian Fractions

```python
from sympy import egyptian_fraction

egyptian_fraction(Rational(12, 13))    # [1/2, 1/10, 1/65]
# 12/13 = 1/2 + 1/10 + 1/65 (sum of distinct unit fractions)
```

## Perfect Powers and Special Numbers

```python
from sympy import perfect_power, is_perfect, is_abundant, is_deficient

perfect_power(64)          # True (2^6, 4^3, 8^2)
is_perfect(6)              # True (1+2+3 = 6)
is_perfect(28)             # True
is_abundant(12)            # True (sum of proper divisors > 12)
is_deficient(7)            # True
```

## Binomial and Multinomial Coefficients

```python
from sympy import binomial, multinomial
from sympy.ntheory import binomial_coefficients, multinomial_coefficients

binomial(10, 3)                    # 120
binomial_coefficients(5, 3)        # {0: 1, 1: 5, 2: 10, 3: 10, 4: 5, 5: 1}
multinomial_coefficients(4, [2, 1, 1])   # multinomial distribution
```

## Partitions

```python
from sympy import npartitions

npartitions(5)            # 7 (ways to partition 5)
npartitions(10)           # 42
```

## Gotchas

- **`isprime()` is deterministic** — uses Miller-Rabin + Lucas tests. Correct for all integers.
- **`factorint()` can be slow for very large numbers** — uses Pollard's rho and ECM. For numbers > ~50 digits, consider specialized tools.
- **`sqrt_mod(n, p)` returns one root** — the other is `p - result`. Returns `None` if no solution.
- **`mod_inverse(a, m)` raises error if gcd(a, m) ≠ 1** — check invertibility first.
- **`totient(1) = 1`** — special case (only 1 is coprime to 1 in range [1,1]).
- **`mobius(n) = 0` if n has a squared prime factor** — this is the most common result for composite numbers.

# Math Functions

## Table of Contents

- [Availability](#availability)
- [Trigonometric](#trigonometric)
- [Hyperbolic](#hyperbolic)
- [Logarithmic](#logarithmic)
- [Power/Root](#powerroot)
- [Rounding](#rounding)
- [Other](#other)

## Availability

Math functions are built into the SQLite amalgamation but only active when compiled with `-DSQLITE_ENABLE_MATH_FUNCTIONS`. Check availability:

```sql
SELECT sqlite_compileoption_used('ENABLE_MATH_FUNCTIONS');
-- Returns 1 if available, 0 if not
```

All math functions return NULL for domain errors (e.g., sqrt of negative number).

## Trigonometric

All angles in radians.

| Function | Description |
|---|---|
| `sin(X)` | Sine |
| `cos(X)` | Cosine |
| `tan(X)` | Tangent |
| `asin(X)` | Arcsine (returns radians) |
| `acos(X)` | Arccosine (returns radians) |
| `atan(X)` | Arctangent (returns radians) |
| `atan2(Y, X)` | Arctangent of Y/X (correct quadrant) |

## Hyperbolic

| Function | Description |
|---|---|
| `sinh(X)` | Hyperbolic sine |
| `cosh(X)` | Hyperbolic cosine |
| `tanh(X)` | Hyperbolic tangent |
| `asinh(X)` | Hyperbolic arcsine |
| `acosh(X)` | Hyperbolic arccosine |
| `atanh(X)` | Hyperbolic arctangent |

## Logarithmic

| Function | Description |
|---|---|
| `ln(X)` | Natural logarithm (base e) |
| `log(X)` | Base-10 logarithm |
| `log(B, X)` | Base-B logarithm of X |
| `log10(X)` | Base-10 logarithm (alias for log(X)) |
| `log2(X)` | Base-2 logarithm |

Note: SQLite's `log(X)` computes base-10 (like PostgreSQL). Most other databases compute natural log.

## Power/Root

| Function | Description |
|---|---|
| `sqrt(X)` | Square root (NULL if X < 0) |
| `pow(X, Y)` | X raised to power Y |
| `power(X, Y)` | Alias for pow() |
| `exp(X)` | e^X (Euler's number to the power X) |

## Rounding

| Function | Description |
|---|---|
| `ceil(X)` / `ceiling(X)` | Smallest integer ≥ X |
| `floor(X)` | Largest integer ≤ X |
| `trunc(X)` | Integer part of X (round toward zero) |

```sql
SELECT ceil(3.2);    -- 4
SELECT floor(3.8);   -- 3
SELECT trunc(-3.7);  -- -3 (round toward zero)
SELECT floor(-3.7);  -- -4 (round down)
```

## Other

| Function | Description |
|---|---|
| `pi()` | Approximation of π |
| `degrees(X)` | Convert radians to degrees |
| `radians(X)` | Convert degrees to radians |
| `mod(X, Y)` | Remainder of X/Y (works with non-integers) |

```sql
SELECT pi();          -- 3.14159265358979
SELECT degrees(pi()); -- 180.0
SELECT radians(180);  -- 3.14159265358979
SELECT mod(10.5, 3);  -- 1.5
```

## Precision

Math functions return IEEE 754 double-precision floating point values. Results are approximations — e.g., `pi()` returns the closest representable double to π.

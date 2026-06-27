# scipy.special Reference

Special mathematical functions. All functions are vectorized over NumPy arrays.

## Table of Contents

- [Error Handling](#error-handling)
- [Airy Functions](#airy-functions)
- [Bessel Functions](#bessel-functions)
- [Struve Functions](#struve-functions)
- [Gamma and Related Functions](#gamma-and-related-functions)
- [Error Function and Fresnel Integrals](#error-function-and-fresnel-integrals)
- [Elliptic Functions and Integrals](#elliptic-functions-and-integrals)
- [Legendre Functions](#legendre-functions)
- [Orthogonal Polynomials](#orthogonal-polynomials)
- [Hypergeometric Functions](#hypergeometric-functions)
- [Combinatorics](#combinatorics)
- [Lambert W and Related](#lambert-w-and-related)
- [Information Theory Functions](#information-theory-functions)
- [Raw Statistical Functions](#raw-statistical-functions)
- [Other Special Functions](#other-special-functions)
- [Convenience Functions](#convenience-functions)

## Error Handling

Special functions handle errors by returning NaN or appropriate values. Control error behavior:

```python
from scipy.special import seterr, geterr, errstate

# Check current settings
print(geterr())  # {'divide': 'warn', 'over': 'warn', 'under': 'ignore', 'invalid': 'ignore'}

# Set globally
seterr(over='raise', invalid='warn')

# Use context manager
with errstate(over='ignore', invalid='warn'):
    result = gamma(-100)  # would normally warn
```

**Modes:** `'ignore'`, `'warn'`, `'raise'`, `'call'`.

## Airy Functions

| Function | Description |
|---|---|
| `airy(x)` | Airy functions Ai, Ai', Bi, Bi' |
| `airye(x)` | Exponentially scaled Airy functions |
| `ai_zeros(nt)` | First nt zeros of Ai and Ai' |
| `bi_zeros(nt)` | First nt zeros of Bi and Bi' |
| `itairy(kind, z1, z2)` | Integrals of Airy functions |

```python
from scipy.special import airy

ai, aid, bi, bid = airy(x)  # Ai(x), Ai'(x), Bi(x), Bi'(x)
```

## Bessel Functions

### Ordinary Bessel functions (J, Y)

| Function | Description |
|---|---|
| `jv(nu, z)` | Bessel J of real order nu, complex argument z |
| `jve(nu, z)` | Exponentially scaled J |
| `jn(n, z)` | Bessel J of integer order n (faster) |
| `yn(nu, z)` | Bessel Y (Neumann) of real order |
| `yve(nu, z)` | Exponentially scaled Y |
| `yn(n, z)` | Bessel Y of integer order n (faster) |

### Modified Bessel functions (I, K)

| Function | Description |
|---|---|
| `iv(nu, z)` | Modified Bessel I of real order |
| `ive(nu, z)` | Exponentially scaled I |
| `kv(nu, z)` | Modified Bessel K of real order |
| `kve(nu, z)` | Exponentially scaled K |
| `ivp(nu, z)` | Derivative of iv with respect to nu |
| `kvp(nu, z)` | Derivative of kv with respect to nu |

### Spherical Bessel functions

| Function | Description |
|---|---|
| `spherical_jn(n, z)` | Spherical Bessel jₙ |
| `spherical_yn(n, z)` | Spherical Bessel yₙ |
| `spherical_in(n, z)` | Modified spherical Bessel iₙ |

### Hankel functions

| Function | Description |
|---|---|
| `hankel1(nu, z)` | Hankel function of first kind H₁ |
| `hankel2(nu, z)` | Hankel function of second kind H₂ |

### Bessel function zeros and roots

| Function | Description |
|---|---|
| `jn_zeros(n, n_zeros)` | First n_zeros zeros of Jₙ |
| `yn_zeros(n, n_zeros)` | First n_zeros zeros of Yₙ |
| `root(jv, nu, n, bracket=None)` | Find nth zero of J_ν |

## Struve Functions

| Function | Description |
|---|---|
| `struve(nu, z)` | Struve function H_ν |
| `struvem(nu, z)` | Modified Struve L_ν minus I_ν |
| `dawsn(x)` | Dawson's integral (related to Struve) |

## Gamma and Related Functions

| Function | Description |
|---|---|
| `gamma(x)` | Gamma function Γ(x) |
| `gammaln(x)` | ln|Γ(x)| for real x |
| `loggamma(x)` | Principal branch of ln Γ(x) |
| `gammasgn(x)` | Sign of Γ(x) |
| `rgamma(x)` | 1/Γ(x) |
| `psi(x)` | Digamma function ψ(x) = Γ'(x)/Γ(x) |
| `polygamma(n, x)` | Polygamma function ψ⁽ⁿ⁾(x) |
| `multigammaln(x, d)` | Log of multivariate gamma |

### Incomplete gamma

| Function | Description |
|---|---|
| `gammainc(a, x)` | Regularized lower incomplete gamma P(a,x) |
| `gammaincc(a, x)` | Regularized upper incomplete gamma Q(a,x) |
| `gammaincinv(a, p)` | Inverse of gammainc (solve P(a,x) = p for x) |
| `gammainccinv(a, q)` | Inverse of gammaincc |

### Beta function

| Function | Description |
|---|---|
| `beta(a, b)` | Beta function B(a,b) |
| `betaln(a, b)` | ln|B(a,b)| |
| `betainc(a, b, x)` | Incomplete beta integral Iₓ(a,b) |
| `betaincc(a, b, x)` | Complemented incomplete beta |
| `betaincinv(a, b, p)` | Inverse of betainc |
| `betainccinv(a, b, q)` | Inverse of betaincc |

## Error Function and Fresnel Integrals

| Function | Description |
|---|---|
| `erf(x)` | Error function erf(x) |
| `erfc(x)` | Complementary error function erfc(x) = 1 - erf(x) |
| `erfcx(x)` | Scaled complementary: e^(x²) · erfc(x) |
| `erfi(x)` | Imaginary error function: -i·erf(ix) |
| `erfinv(x)` | Inverse of erf |
| `erfcinv(x)` | Inverse of erfc |
| `wofz(z)` | Faddeeva function w(z) = e^(-z²)·erfc(-iz) |
| `dawsn(x)` | Dawson's integral F(x) |
| `fresnel(x)` | Fresnel integrals S(x), C(x) |
| `fresnel_zeros(nt)` | Zeros of S(z) and C(z) |
| `voigt_profile(x, sigma)` | Voigt profile (convolution of Gaussian and Lorentzian) |

## Elliptic Functions and Integrals

### Complete elliptic integrals

| Function | Description |
|---|---|
| `ellipk(m)` | Complete elliptic integral of first kind K(m) |
| `ellipe(m)` | Complete elliptic integral of second kind E(m) |
| `elliprj(a, b, p, x)` | Carlson symmetric form R_J |
| `elliprf(x, y, z)` | Carlson symmetric form R_F |
| `elliprd(x, y, z)` | Carlson symmetric form R_D |
| `elliprc(x, y)` | Carlson symmetric form R_C |
| `elliprk(x)` | Complete elliptic integral K (alternative) |
| `ellipek(x)` | Complete elliptic integral E (alternative) |

### Incomplete elliptic integrals

| Function | Description |
|---|---|
| `ellipkinc(phi, m)` | Incomplete elliptic integral K(φ|m) |
| `ellipeinc(phi, m)` | Incomplete elliptic integral E(φ|m) |

### Jacobi elliptic functions

| Function | Description |
|---|---|
| `ellipj(u, m)` | Jacobi sn, cn, dn, and phase |
| `ellippi(phi, m, n)` | Incomplete elliptic integral of third kind |

## Legendre Functions

| Function | Description |
|---|---|
| `lpmv(nu, m, z)` | Associated Legendre function P_ν^m(z) |
| `lpmv_derivative(nu, m, z)` | Derivative of P_ν^m(z) |
| `pvn(n, z)` | First n+1 Legendre polynomials P₀ to Pₙ |
| `pvn_derivative(n, z)` | Derivatives of Legendre polynomials |
| `rvn(n, z)` | First n+1 reversed Legendre functions |

## Orthogonal Polynomials

Evaluate orthogonal polynomials at given points:

| Function | Polynomial |
|---|---|
| `eval_legendre(c, x)` | Legendre |
| `eval_chebyt(c, x)` | Chebyshev T (first kind) |
| `eval_chebyu(c, x)` | Chebyshev U (second kind) |
| `eval_chebyc(c, x)` | Chebyshev T on [-2, 2] |
| `eval_chebys(c, x)` | Chebyshev U on [-2, 2] |
| `eval_jacobi(c, x, alpha, beta)` | Jacobi |
| `eval_laguerre(c, x)` | Laguerre |
| `eval_genlaguerre(c, x, alpha)` | Generalized Laguerre |
| `eval_hermite(c, x)` | Physicist's Hermite |
| `eval_hermitenorm(c, x)` | Probabilist's (normalized) Hermite |
| `eval_gegenbauer(c, x, lambda)` | Gegenbauer (ultraspherical) |
| `eval_sh_legendre(c, x)` | Shifted Legendre |
| `eval_sh_chebyt(c, x)` | Shifted Chebyshev T |
| `eval_sh_chebyu(c, x)` | Shifted Chebyshev U |
| `eval_sh_jacobi(c, x, alpha, beta)` | Shifted Jacobi |
| `assoc_laguerre(n, k, x)` | Generalized Laguerre Lₙ^(k)(x) |

## Hypergeometric Functions

| Function | Description |
|---|---|
| `hyp1f1(a, b, z)` | Confluent hypergeometric ₁F₁(a;b;z) |
| `hyp1f1_regularized(a, b, z)` | Regularized ₁F₁ |
| `hyp2f1(a, b, c, z)` | Gaussian hypergeometric ₂F₁(a,b;c;z) |
| `hyp0f1(b, z)` | ₀F₁(;b;z) |
| `hyp1f2(a1, b1, b2, z)` | ₁F₂(a₁;b₁,b₂;z) |
| `hyp2f0(a1, a2, b1, z)` | ₂F₀(a₁,a₂;b₁;z) |
| `hyp2f2(a1, a2, b1, b2, z)` | ₂F₂(a₁,a₂;b₁,b₂;z) |
| `hyp2f3(...)` | ₂F₃ |
| `hyp3f2(a1, a2, a3, b1, b2, z)` | ₃F₂ |
| `genhyper([a1,...], [b1,...], z)` | General hypergeometric pFq |

## Combinatorics

| Function | Description |
|---|---|
| `comb(n, k, exact=False)` | Binomial coefficient C(n,k) |
| `perm(n, k=None, exact=False)` | Permutations P(n,k) or n! if k is None |
| `stirling2(n, k)` | Stirling numbers of the second kind |

## Lambert W and Related

| Function | Description |
|---|---|
| `lambertw(z, k=0)` | Lambert W function (branch k) |
| `wrightomega(z)` | Wright Omega function ω(z) |

## Information Theory Functions

| Function | Description |
|---|---|
| `entr(x)` | x·log(x) for x > 0, 0 otherwise |
| `xlogx(x)` | Same as entr |
| `xlog1p(x)` | x·log(1+x) |
| `rel_entr(x, y)` | Relative entropy x·log(x/y) - x + y |

## Raw Statistical Functions

These are the building blocks used by `scipy.stats` distributions:

| Function | Description |
|---|---|
| `log_ndtr(x)` | Log of standard normal CDF (accurate in tail) |
| `ndtr(x)` | Standard normal CDF Φ(x) |
| `ndtri(p)` | Inverse of ndtr (quantile function) |
| `sici(z)` | Sine and cosine integrals Si, Ci |
| `expi(x)` | Exponential integral Ei(x) |
| `exp1(x)` | E₁ exponential integral |
| `expn(n, x)` | Generalized exponential integral Eₙ(x) |
| `logit(p)` | Logit function ln(p/(1-p)) |
| `expit(x)` | Logistic (inverse logit) 1/(1+e^(-x)) |
| `chdtr(a, x)` | Chi-squared CDF |
| `chdtrinv(a, p)` | Inverse chi-squared CDF |
| `chdtrix(a, x)` | Incomplete chi-squared CDF |
| `gdtr(a, x, p)` | Gamma CDF |
| `gdtrinc(a, x, p)` | Regularized incomplete gamma (CDF form) |
| `nbdtr(k, n, p)` | Negative binomial CDF |
| `bdtr(k, n, p)` | Binomial CDF |
| `bdtrik(x, n, p)` | Binomial CDF, solving for k |
| `bdtrip(k, n, p)` | Binomial CDF, solving for p |
| `betainc(a, b, x)` | Incomplete beta (used by many distributions) |
| `ncfdtr(df1, df2, nc, x)` | Noncentral F CDF |
| `nctdtr(df, nc, x)` | Noncentral t CDF |
| `nbdtrjn(k, n, p)` | Negative binomial CDF (Jenkinson) |
| `owens_t(h, p)` | Owen's T function |

## Other Special Functions

| Function | Description |
|---|---|
| `clpmn(cl, mu, nu, z)` | Coulomb wave functions |
| `pbdvsl(maxl, alpha, beta, x)` | Normed Jacobi polynomials and derivatives |
| `radau_a(n, alpha, beta)` / `radau_b(n, alpha, beta)` | Radau coefficients |
| `iv_ratio(a, b)` | Iₐ(z) / Iᵦ(z) for large z |
| `kv_ratio(a, b)` | Kₐ(z) / Kᵦ(z) for large z |
| `it2struve(nu, z)` | Integrals of Struve functions |
| `mathieu_a(order, m, q)` / `mathieu_b(...)` | Mathieu characteristic values |
| `angoular_mathieu_m(m, q, z)` / `angular_mathieu_c(...)` | Angular Mathieu functions |
| `cyl_bessel_i(nu, z)` | Alias for iv |
| `cyl_bessel_j(nu, z)` | Alias for jv |
| `cyl_bessel_k(nu, z)` | Alias for kv |
| `cyl_neumann(nu, z)` | Alias for yv |
| `spher_harm(m, n, theta, phi)` | Spherical harmonics Yₘⁿ(θ, φ) |
| `softmax(x, axis=-1)` | Softmax function (numerically stable) |
| `xexp1(x)` | x · exp(1+x) |

## Convenience Functions

| Function | Description |
|---|---|
| `logit(p)` | Logit: ln(p/(1-p)) |
| `expit(x)` | Inverse logit (sigmoid): 1/(1+e^(-x)) |
| `softmax(x)` | Softmax |
| `expit(x)` | Logistic function |

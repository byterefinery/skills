# scipy.special Reference (1.18.1)

Special mathematical functions. All functions are vectorized over NumPy arrays (ufuncs).

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
- [Mathieu and Spheroidal Wave Functions](#mathieu-and-spheroidal-wave-functions)
- [Kelvin Functions](#kelvin-functions)
- [Combinatorics and Lambert W](#combinatorics-and-lambert-w)
- [Information Theory](#information-theory)
- [Raw Statistical Functions](#raw-statistical-functions)
- [Convenience Functions](#convenience-functions)

## Error Handling

Special functions handle errors by returning NaN or appropriate values; control the behavior:

```python
from scipy.special import geterr, seterr, errstate

print(geterr())  # {'divide': 'warn', 'over': 'warn', 'under': 'ignore', 'invalid': 'ignore'}

seterr(over='raise', invalid='warn')        # set globally
with errstate(over='ignore', invalid='warn'):
    result = gamma(-100)                    # context manager
```

**Modes:** `'ignore'`, `'warn'`, `'raise'`, `'call'`. `scipy.special.cython_special` exposes Cython bindings to avoid Python call overhead (GIL-released).

## Airy Functions

| Function | Description |
|---|---|
| `airy(x)` | Airy functions Ai, Ai', Bi, Bi' (returns 4 arrays) |
| `airye(x)` | Exponentially scaled Airy functions |
| `ai_zeros(nt)` / `bi_zeros(nt)` | First nt zeros of Ai (Ai') / Bi (Bi') |
| `itairy(kind, z1, z2)` | Integrals of Airy functions |

```python
from scipy.special import airy
ai, aid, bi, bid = airy(x)  # Ai(x), Ai'(x), Bi(x), Bi'(x)
```

## Bessel Functions

### Ordinary Bessel functions (J, Y)

| Function | Description |
|---|---|
| `jv(nu, z)` / `jve(nu, z)` | Bessel J of real order (exponentially scaled: `jve`) |
| `yn(nu, z)` / `yve(nu, z)` | Bessel Y (Neumann) of real order (scaled: `yve`) |
| `jn(n, z)` / `yn(n, z)` | Integer-order J / Y (faster) |
| `j0(z)` / `j1(z)` / `y0(z)` / `y1(z)` | Order-0/1 J and Y |
| `iv(nu, z)` / `ive(nu, z)` | Modified Bessel I of real order (scaled: `ive`) |
| `kv(nu, z)` / `kve(nu, z)` | Modified Bessel K (scaled: `kve`) |
| `kn(n, z)` | Modified Bessel K of integer order |
| `i0(z)` / `i0e(z)` / `i1(z)` / `i1e(z)` / `k0(z)` / `k0e(z)` / `k1(z)` / `k1e(z)` | Order-0/1 I and K (e = scaled) |

### Derivatives and integrals

| Function | Description |
|---|---|
| `jvp(nu, v, z)` / `yvp(nu, v, z)` / `ivp(nu, v, z)` / `kvp(nu, v, z)` | v-th derivative w.r.t. z |
| `h1vp(nu, v, z)` / `h2vp(nu, v, z)` | Hankel derivatives |
| `itj0y0(x)` / `it2j0y0(x)` / `iti0k0(x)` / `it2i0k0(x)` | Integrals of Bessel products |
| `besselpoly(c, z)` | Bessel polynomial |

### Zeros

`jnjnp_zeros(n, nt)` (zeros of Jₙ and Jₙ'), `jnp_zeros(n, nt)`, `jn_zeros(n, nt)`, `yn_zeros(n, nt)`, `ynp_zeros(n, nt)`, `y0_zeros(nt)`, `y1_zeros(nt)`, `y1p_zeros(nt)`.

### Spherical, Riccati-Bessel, Hankel, other

| Function | Description |
|---|---|
| `spherical_jn(n, z)` / `spherical_yn(n, z)` / `spherical_in(n, z)` / `spherical_kn(n, z)` | Spherical Bessel j / y / i / k |
| `riccati_jn(n, z)` / `riccati_yn(n, z)` | Riccati-Bessel |
| `hankel1(nu, z)` / `hankel2(nu, z)` (+ `hankel1e`/`hankel2e`) | Hankel functions H₁ / H₂ |
| `wright_bessel(w, nu)` / `log_wright_bessel(w, nu)` | Wright generalized Bessel |
| `lmbda(w, nu)` | Generalized Lambert function (Bessel-related) |

## Struve Functions

`struve(nu, z)` (H_ν), `modstruve(nu, z)` (L_ν − I_ν), `itstruve0(x)`, `it2struve0(x)`, `itmodstruve0(x)`, `dawsn(x)` (Dawson's integral).

## Gamma and Related Functions

| Function | Description |
|---|---|
| `gamma(x)` | Γ(x) |
| `gammaln(x)` | ln\|Γ(x)\| for real x |
| `loggamma(x)` | Principal branch of ln Γ(x) |
| `gammasgn(x)` | Sign of Γ(x) |
| `rgamma(x)` | 1/Γ(x) |
| `psi(x)` / `digamma(x)` | Digamma ψ(x) = Γ'(x)/Γ(x) |
| `polygamma(n, x)` | Polygamma ψ⁽ⁿ⁾(x) |
| `multigammaln(x, d)` | Log of multivariate gamma |
| `poch(a, b)` | Pochhammer symbol (rising factorial) |
| `gammainc(a, x)` / `gammaincc(a, x)` | Regularized lower / upper incomplete gamma |
| `gammaincinv(a, p)` / `gammainccinv(a, q)` | Inverses |

### Beta function

`beta(a, b)`, `betaln(a, b)`, `betainc(a, b, x)` / `betaincc(a, b, x)` (incomplete), `betaincinv(a, b, p)` / `betainccinv(a, b, q)`.

## Error Function and Fresnel Integrals

| Function | Description |
|---|---|
| `erf(x)` / `erfc(x)` / `erfcx(x)` | Error function / complementary / scaled (e^(x²)·erfc(x)) |
| `erfi(x)` | Imaginary error function |
| `erfinv(x)` / `erfcinv(x)` | Inverses |
| `erf_zeros(nt)` / `fresnelc_zeros(nt)` / `fresnels_zeros(nt)` | Zeros |
| `wofz(z)` | Faddeeva function w(z) = e^(-z²)·erfc(-iz) |
| `dawsn(x)` | Dawson's integral F(x) |
| `fresnel(x)` | Fresnel integrals S(x), C(x) |
| `modfresnelp(x)` / `modfresnelm(x)` | Modified Fresnel integrals |
| `voigt_profile(x, sigma)` | Voigt profile (Gaussian×Lorentzian convolution) |

## Elliptic Functions and Integrals

Complete: `ellipk(m)` (K), `ellipe(m)` (E), `ellipkm1(m)` (K − 1).
Incomplete: `ellipkinc(phi, m)`, `ellipeinc(phi, m)`.
Carlson symmetric forms: `elliprf(x, y, z)` (R_F), `elliprd(x, y, z)` (R_D), `elliprc(x, y)` (R_C), `elliprg(x, y, z)` (R_G), `elliprj(x, y, z, p)` (R_J).
Jacobi: `ellipj(u, m)` (sn, cn, dn, phase), `ellippi(phi, m)` (third kind), `ellip_harm(u, m)`, `ellip_harm_2(u, m)`, `ellip_normal(u, m)`.

## Legendre Functions

| Function | Description |
|---|---|
| `lpmv(nu, m, z)` | Associated Legendre function P_ν^m(z) |
| `lqn(n, x)` / `lqmn(m, n, x)` | Legendre functions of the second kind |
| `legendre_p(n, x)` / `legendre_p_all(n, x)` | Legendre P_n |
| `assoc_legendre_p(n, m, x)` / `assoc_legendre_p_all(...)` | Associated Legendre |
| `sph_legendre_p(n, m, x)` / `sph_legendre_p_all(...)` | Spherical Legendre |
| `sph_harm_y(n, m, theta, phi)` / `sph_harm_y_all(...)` | Spherical harmonics Yₘⁿ(θ, φ) |

## Orthogonal Polynomials

**Evaluate at points:** `eval_legendre`, `eval_chebyt`, `eval_chebyu`, `eval_chebyc` (T on [-2,2]), `eval_chebys` (U on [-2,2]), `eval_jacobi(c, x, alpha, beta)`, `eval_laguerre`, `eval_genlaguerre(c, x, alpha)`, `eval_hermite`, `eval_hermitenorm`, `eval_gegenbauer(c, x, lambda)`, and shifted variants `eval_sh_legendre`, `eval_sh_chebyt`, `eval_sh_chebyu`, `eval_sh_jacobi`.

**Roots:** `roots_legendre`, `roots_chebyt`, `roots_chebyu`, `roots_chebyc`, `roots_chebys`, `roots_jacobi`, `roots_laguerre`, `roots_genlaguerre`, `roots_hermite`, `roots_hermitenorm`, `roots_gegenbauer`, `roots_sh_legendre`, `roots_sh_chebyt`, `roots_sh_chebyu`, `roots_sh_jacobi`.

**Polynomial coefficients:** `legendre(n, monic=False)`, `chebyt`, `chebyu`, `chebyc`, `chebys`, `jacobi`, `laguerre`, `genlaguerre`, `hermite`, `hermitenorm`, `gegenbauer`, `sh_legendre`, `sh_chebyt`, `sh_chebyu`, `sh_jacobi` (+ `assoc_laguerre(n, k, x)`).

## Hypergeometric Functions

`hyp2f1(a, b, c, z)` (Gaussian), `hyp1f1(a, b, z)` (confluent), `hyperu(a, b, z)` (Tricomi), `hyp0f1(b, z)`, `pbdv(n, alpha, x)` / `pbvv(n, alpha, x)` (associated Legendre P/Q of degree n, vectorized in n).

## Mathieu and Spheroidal Wave Functions

Mathieu: `mathieu_a(m, a, q)` / `mathieu_b(m, a, q)` (characteristic values), `mathieu_even_coef(m, a, q)` / `mathieu_odd_coef(...)`, `mathieu_cem(m, a, q)` / `mathieu_sem(m, a, q)`, modified `mathieu_modcem1/2`, `mathieu_modsem1/2`.
Spheroidal: `pro_ang1(l, c, z)` / `obl_ang1(...)`, `pro_rad1(l, c, z)` / `obl_rad1(...)`, `pro_rad2` / `obl_rad2`, connection values `pro_cv` / `obl_cv` (+ `_seq`, `_cv` variants).

## Kelvin Functions

`kelvin(z)` (ber, bei, ker, kei), `kelvin_zeros(nt)`, plus individual `ber`, `bei`, `berp`, `beip`, `ker`, `kei`, `kerp`, `keip` and their `*_zeros` functions.

## Combinatorics and Lambert W

| Function | Description |
|---|---|
| `comb(n, k, exact=False)` | Binomial coefficient C(n,k) |
| `perm(n, k=None, exact=False)` | Permutations P(n,k), or n! if k is None |
| `stirling2(n, k)` | Stirling numbers of the second kind |
| `lambertw(z, k=0)` | Lambert W function (branch k) |
| `wrightomega(z)` | Wright Omega function ω(z) |

## Information Theory

| Function | Description |
|---|---|
| `entr(x)` | x·log(x) for x > 0, 0 otherwise |
| `xlogx(x)` | Same as entr |
| `xlog1p(x)` | x·log(1+x) |
| `rel_entr(x, y)` | Relative entropy x·log(x/y) − x + y |
| `kl_div(x, y)` | Kullback-Leibler divergence |
| `huber(x, H=1.0)` / `pseudo_huber(x, H=1.0)` | Huber / pseudo-Huber loss functions |

## Raw Statistical Functions

Building blocks used by `scipy.stats` distributions:

- **Binomial:** `bdtr(k, n, p)`, `bdtrc`, `bdtri(k, p, n)`, `bdtrik(x, n, p)`, `bdtrin(p, n, k)`
- **F:** `fdtr(df1, df2, x)`, `fdtrc`, `fdtri`, `fdtridfd`
- **Gamma:** `gdtr(a, x, p)`, `gdtrc`, `gdtria`, `gdtrib`, `gdtrix`
- **Negative binomial:** `nbdtr`, `nbdtrc`, `nbdtri`, `nbdtrik`, `nbdtrin`
- **Noncentral F:** `ncfdtr`, `ncfdtrc`, `ncfdtridfd`, `ncfdtridfn`, `ncfdtri`, `ncfdtrinc`
- **Noncentral t:** `nctdtr`, `nctdtrinc`, `nctdtrit`, `nctdtridf`
- **Normal:** `ndtr(x)` (Φ), `log_ndtr(x)`, `ndtri(p)`, `ndtri_exp`
- **Poisson:** `pdtr(k, mu)`, `pdtrc`, `pdtri`, `pdtrik`
- **Student t:** `stdtr(df, x)`, `stdtridf`, `stdtrit`
- **Chi-square:** `chdtr(df, x)`, `chdtrc`, `chdtri`, `chdtriv`
- **Noncentral chi-square:** `chndtr`, `chndtrinc`, `chndtridf`, `chndtrix`
- **Kolmogorov/Smirnov:** `smirnov`, `smirnovi`, `kolmogorov`, `kolmogi`
- **Exponential integrals:** `expi(x)`, `exp1(x)`, `expn(n, x)`
- **Sine/cosine integrals:** `sici(z)` → (Si, Ci)
- **Owen's T:** `owens_t(h, p)`
- **Box-Cox:** `boxcox(x, lmbda)`, `boxcox1p`, `inv_boxcox`, `inv_boxcox1p`
- **Logit/expit:** `logit(p)`, `expit(x)`, `log_expit(x)`
- **Generalized lambda:** `tklmbda(x, l, k)`

## Convenience Functions

| Function | Description |
|---|---|
| `logit(p)` | Logit: ln(p/(1−p)) |
| `expit(x)` | Inverse logit (sigmoid): 1/(1+e^(−x)) |
| `softmax(x, axis=-1)` | Numerically stable softmax |
| `comb`, `perm`, `stirling2` | Combinatorics (see above) |

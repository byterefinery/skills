# scipy.fft Reference (1.18.1)

Discrete Fourier transforms, DCT/DST, and Hankel transforms. Modern replacement for `scipy.fftpack`.

## Table of Contents

- [Fast Fourier Transforms](#fast-fourier-transforms)
- [Real-Valued FFTs](#real-valued-ffts)
- [Hermitian FFTs](#hermitian-ffts)
- [Discrete Cosine/Sine Transforms (DCT/DST)](#discrete-cosinesine-transforms-dctdst)
- [Fast Hankel Transforms](#fast-hankel-transforms)
- [Helper Functions](#helper-functions)
- [Backend and Worker Control](#backend-and-worker-control)
- [Conventions and Caveats](#conventions-and-caveats)

## Fast Fourier Transforms

| Function | 1-D | 2-D | N-D |
|---|---|---|---|
| Forward | `fft(x, n=None, axis=-1)` | `fft2(x, s=None, axes=(-2, -1))` | `fftn(x, s=None, axes=None)` |
| Inverse | `ifft(X, n=None, axis=-1)` | `ifft2(X, ...)` | `ifftn(X, ...)` |

```python
from scipy.fft import fft, ifft, fft2, fftn
import numpy as np

X = fft(signal)
recovered = ifft(X)

X2 = fft2(image)          # 2-D FFT (images, matrices)
recovered = ifft2(X2)
```

**Parameters:**
- `n` — output length (zero-pads or truncates)
- `axis` — axis along which to compute
- `norm` — `'backward'` (default), `'forward'`, `'ortho'` (see Conventions)

## Real-Valued FFTs

Optimized for real-valued input. Output is half-size (exploits conjugate symmetry).

| Function | 1-D | 2-D | N-D |
|---|---|---|---|
| Forward | `rfft(x, n=None)` | `rfft2(x, s=None)` | `rfftn(x, s=None)` |
| Inverse | `irfft(X, n=None)` | `irfft2(X, ...)` | `irfftn(X, ...)` |

```python
from scipy.fft import rfft, irfft, rfftfreq

X = rfft(real_signal)                    # shape: (N//2 + 1,) for input length N
recovered = irfft(X, n=len(real_signal))
f = rfftfreq(len(real_signal), d=1.0/fs) # frequency axis for X
```

## Hermitian FFTs

For input with Hermitian symmetry (real-valued spectrum).

| Function | 1-D | 2-D | N-D |
|---|---|---|---|
| Forward | `hfft(X, n=None)` | `hfft2(X, ...)` | `hfftn(X, ...)` |
| Inverse | `ihfft(x, n=None)` | `ihfft2(x, ...)` | `ihfftn(x, ...)` |

## Discrete Cosine/Sine Transforms (DCT/DST)

### DCT (Discrete Cosine Transform)

| Function | 1-D | N-D |
|---|---|---|
| Forward | `dct(x, type=2, n=None, norm=None, axis=-1)` | `dctn(x, type=2, ...)` |
| Inverse | `idct(X, type=2, ...)` | `idctn(X, ...)` |

**Types:** 1, 2, 3, 4. Type 2 is default (most common, used in JPEG).

### DST (Discrete Sine Transform)

| Function | 1-D | N-D |
|---|---|---|
| Forward | `dst(x, type=2, n=None, norm=None, axis=-1)` | `dstn(x, type=2, ...)` |
| Inverse | `idst(X, type=2, ...)` | `idstn(X, ...)` |

**Types:** 1, 2, 3, 4.

## Fast Hankel Transforms

Hankel transform is the radial Fourier transform (cylindrical symmetry problems).

| Function | Description |
|---|---|
| `fht(r, f, kind=0, ...)` | Forward fast Hankel transform |
| `ifht(k, f_hat, kind=0, ...)` | Inverse fast Hankel transform |
| `fhtoffset(r, f, kind=0)` | Compute an optimal offset for accuracy |

**Kind parameter:** 0 (J₀ Bessel), 1 (J₁), 2 (J₂).

```python
from scipy.fft import fht, ifht, fhtoffset
import numpy as np

r = np.linspace(0, 10, 1024)
f = np.exp(-r**2 / 2)
offset = fhtoffset(r, f, kind=0)
k, f_hat = fht(r, f, kind=0, offset=offset)
```

## Helper Functions

| Function | Description |
|---|---|
| `fftshift(x, axes=None)` | Shift zero-frequency component to the center of the spectrum |
| `ifftshift(x, axes=None)` | Inverse of `fftshift` |
| `fftfreq(n, d=1.0)` | DFT sample frequencies |
| `rfftfreq(n, d=1.0)` | Real-DFT sample frequencies (for `rfft`, `irfft`) |
| `fhtoffset(r, f, kind=0)` | Optimal offset for the Hankel transform |
| `next_fast_len(n)` | Optimal length to zero-pad an FFT for speed |
| `prev_fast_len(n)` | Maximum slice length that results in a fast FFT |

```python
from scipy.fft import fftshift, fftfreq, next_fast_len

X_shifted = fftshift(fft(signal))          # center the zero-frequency component
freqs = fftfreq(len(signal), d=1.0/fs)    # frequency axis
optimal_n = next_fast_len(len(signal))    # pick a fast FFT length
```

## Backend and Worker Control

| Function | Description |
|---|---|
| `set_backend(backend)` | Context manager to set the backend within a fixed scope |
| `skip_backend(backend)` | Context manager to skip a backend within a scope |
| `set_global_backend(backend)` | Sets the global FFT backend |
| `set_workers(n)` | Context manager to set the maximum number of FFT worker threads |
| `get_workers()` | Get the current default number of workers |

**Since 1.18.0 the internal backend is `ducc0.fft`** (successor of pocketfft). Plans requiring more than 1 MB of storage are no longer cached — this mainly affects huge 1-D transforms of prime/near-prime sizes.

```python
from scipy.fft import set_backend, set_workers

with set_workers(4):
    X = fft(signal)
```

## Conventions and Caveats

**Normalization** — the DFT implemented by `fft`/`ifft` is `X[l] = (1/γ) Σ x[k] e^{-j2πlk/N}` where γ is set by `norm`:
- `norm='backward'` (**default**) — γ = 1: forward transform unscaled, inverse carries the 1/N factor
- `norm='forward'` — γ = N: forward normalized, inverse unscaled
- `norm='ortho'` — γ = √N: unitary transform pair

**Periodicity** — the DFT assumes the signal is periodic: `x` and `X` continue periodically outside their domain. Spectral leakage at the edges is inherent; window your signal if that matters.

**Speed** — FFT cost depends on factoring N into small primes: slowest for prime N, fastest for powers of 2. Use `next_fast_len`/`prev_fast_len` to choose fast lengths.

**Why prefer `scipy.fft` over `numpy.fft`?** Multi-threading via worker pools, pluggable backends, `next_fast_len`, optimized real-valued transforms (`rfft`), and built-in DCT/DST.

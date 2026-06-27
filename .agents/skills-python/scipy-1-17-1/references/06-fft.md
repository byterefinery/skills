# scipy.fft Reference

Discrete Fourier transforms, DCT/DST, and Hankel transforms. Modern replacement for `scipy.fftpack`.

## Table of Contents

- [Fast Fourier Transforms](#fast-fourier-transforms)
- [Real-Valued FFTs](#real-valued-ffts)
- [Hermitian FFTs](#hermitian-ffts)
- [Discrete Cosine/Sine Transforms (DCT/DST)](#discrete-cosinesine-transforms-dctdst)
- [Fast Hankel Transforms](#fast-hankel-transforms)
- [Helper Functions](#helper-functions)
- [Backend Control](#backend-control)

## Fast Fourier Transforms

| Function | 1-D | 2-D | N-D |
|---|---|---|---|
| Forward | `fft(x, n=None, axis=-1)` | `fft2(x, s=None)` | `fftn(x, s=None)` |
| Inverse | `ifft(X, n=None, axis=-1)` | `ifft2(X, s=None)` | `ifftn(X, s=None)` |

```python
from scipy.fft import fft, ifft, fft2, fftn
import numpy as np

# 1-D FFT
X = fft(signal)
recovered = ifft(X)

# 2-D FFT (images, matrices)
X2 = fft2(image)
recovered = ifft2(X2)

# N-D FFT
Xn = fftn(data, s=None, axes=None)
```

**Parameters:**
- `n` — output length (zero-pads or truncates)
- `axis` — axis along which to compute
- `norm` — `'backward'` (default, no normalization), `'ortho'` (unitary), `'forward'` (normalize by N)

## Real-Valued FFTs

Optimized for real-valued input. Output is half-size (exploits conjugate symmetry).

| Function | 1-D | 2-D | N-D |
|---|---|---|---|
| Forward | `rfft(x, n=None)` | `rfft2(x, s=None)` | `rfftn(x, s=None)` |
| Inverse | `irfft(X, n=None)` | `irfft2(X, s=None)` | `irfftn(X, s=None)` |

```python
from scipy.fft import rfft, irfft

# Real input → complex output (half-size)
X = rfft(real_signal)  # shape: (N//2 + 1,) for input of length N
recovered = irfft(X, n=len(real_signal))
```

## Hermitian FFTs

For input with Hermitian symmetry (real-valued spectrum).

| Function | 1-D | 2-D | N-D |
|---|---|---|---|
| Forward | `hfft(X, n=None)` | `hfft2(X, s=None)` | `hfftn(X, s=None)` |
| Inverse | `ihfft(x, n=None)` | `ihfft2(x, s=None)` | `ihfftn(x, s=None)` |

## Discrete Cosine/Sine Transforms (DCT/DST)

### DCT (Discrete Cosine Transform)

| Function | 1-D | N-D |
|---|---|---|
| Forward | `dct(x, type=2, n=None, norm=None, axis=-1)` | `dctn(x, type=2, ...)` |
| Inverse | `idct(X, type=2, n=None, norm=None, axis=-1)` | `idctn(X, type=2, ...)` |

**Types:** 1, 2, 3, 4. Type 2 is default (most common, used in JPEG).

```python
from scipy.fft import dct, idct

# DCT type 2 (JPEG-style)
coeffs = dct(signal, type=2, norm='ortho')
recovered = idct(coeffs, type=2, norm='ortho')
```

### DST (Discrete Sine Transform)

| Function | 1-D | N-D |
|---|---|---|
| Forward | `dst(x, type=2, n=None, norm=None, axis=-1)` | `dstn(x, type=2, ...)` |
| Inverse | `idst(X, type=2, n=None, norm=None, axis=-1)` | `idstn(X, type=2, ...)` |

**Types:** 1, 2, 3, 4.

## Fast Hankel Transforms

Hankel transform is the radial Fourier transform (used in cylindrical symmetry problems).

| Function | Description |
|---|---|
| `fht(r, f, kind=0)` | Forward fast Hankel transform |
| `ifht(k, f_hat, kind=0)` | Inverse fast Hankel transform |

**Kind parameter:** 0 (J₀ Bessel), 1 (J₁), 2 (J₂).

```python
from scipy.fft import fht, ifht, fhtoffset

r = np.linspace(0, 10, 1024)
f = np.exp(-r**2 / 2)
offset = fhtoffset(r, f, kind=0)  # optimal offset for accuracy
k, f_hat = fht(r, f, kind=0, offset=offset)
```

## Helper Functions

| Function | Description |
|---|---|
| `fftshift(x, axes=None)` | Shift zero-frequency component to center |
| `ifftshift(x, axes=None)` | Inverse of fftshift |
| `fftfreq(n, d=1.0)` | DFT sample frequencies |
| `rfftfreq(n, d=1.0)` | Real DFT sample frequencies |
| `fhtoffset(r, f, kind=0)` | Optimal offset for Hankel transform |
| `next_fast_len(n)` | Optimal zero-pad length for fast FFT |
| `prev_fast_len(n)` | Maximum slice length for fast FFT |

```python
from scipy.fft import fftshift, fftfreq, next_fast_len

# Center the zero-frequency component
X_shifted = fftshift(fft(signal))

# Get frequency axis
n = len(signal)
freqs = fftfreq(n, d=1.0/sampling_rate)

# Find optimal FFT length
optimal_n = next_fast_len(len(signal))
```

## Backend Control

`scipy.fft` supports pluggable backends (e.g., FFTW, pypocketfft).

| Function | Description |
|---|---|
| `set_backend(backend)` | Context manager to set backend within scope |
| `skip_backend(backend)` | Context manager to skip a backend |
| `set_global_backend(backend)` | Set global default backend |
| `register_backend(backend)` | Register a backend for permanent use |
| `get_workers()` | Get current default number of workers |
| `set_workers(n)` | Context manager to set worker count |

```python
from scipy.fft import set_global_backend, set_backend

# Set global backend
set_global_backend('pypocketfft')

# Use specific backend for one operation
with set_backend('pypocketfft'):
    X = fft(signal)
```

### Why prefer `scipy.fft` over `numpy.fft`?

- Multi-threading support via worker pools
- Pluggable backends (FFTW, pypocketfft, etc.)
- `next_fast_len()` for optimal performance
- Real-valued FFTs (`rfft`) are optimized
- DCT/DST transforms built-in

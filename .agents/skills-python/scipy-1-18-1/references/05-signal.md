# scipy.signal Reference (1.18.1)

Signal processing, filter design, spectral analysis, and LTI systems.

## Table of Contents

- [Convolution](#convolution)
- [Filtering](#filtering)
- [B-Splines](#b-splines)
- [FIR Filter Design](#fir-filter-design)
- [IIR Filter Design](#iir-filter-design)
- [LTI Systems (Continuous-Time)](#lti-systems-continuous-time)
- [LTI Systems (Discrete-Time)](#lti-systems-discrete-time)
- [LTI Representation Conversions](#lti-representation-conversions)
- [Peak Finding](#peak-finding)
- [Spectral Analysis](#spectral-analysis)
- [Waveforms](#waveforms)
- [Window Functions](#window-functions)
- [Chirp Z-Transform and Zoom FFT](#chirp-z-transform-and-zoom-fft)

## Convolution

| Function | Description |
|---|---|
| `convolve(in1, in2, mode='full')` | N-D convolution (`mode='full'/'same'/'valid'`, `method='auto'/'direct'/'fft'`) |
| `correlate(in1, in2, mode='full')` | N-D correlation |
| `fftconvolve(in1, in2)` | FFT-based convolution (faster for long signals) |
| `oaconvolve(in1, in2)` | Overlap-add convolution |
| `convolve2d(in1, in2, mode='full')` | 2-D convolution (more options) |
| `correlate2d(in1, in2, mode='full')` | 2-D correlation |
| `sepfir2d(im, rowfir, colfir)` | 2-D separable FIR filtering |
| `choose_conv_method(*arrays)` | Chooses faster of FFT and direct convolution |
| `correlation_lags(N, M)` | Lag indices for 1-D cross-correlation |

## Filtering

### Apply filters to data

| Function | Description |
|---|---|
| `lfilter(b, a, x, axis=-1)` | Direct-form II transposed FIR/IIR filter (FIR if `a=[1]`, IIR otherwise) |
| `lfiltic(b, a, y, x=None)` | Construct initial conditions for `lfilter` |
| `lfilter_zi(b, a)` | Steady-state (zero) initial conditions for `lfilter` |
| `filtfilt(b, a, x)` | Forward-backward filter (zero-phase, doubles effective filter order) |
| `sosfilt(sos, x)` / `sosfiltfilt(sos, x)` | Second-order sections filtering (more stable than TF for high-order IIR) |
| `savgol_filter(x, window_length, poly_order, ...)` | Savitzky-Golay smoothing (derivatives available) |
| `savgol_coeffs(window_length, poly_order, ...)` | Savitzky-Golay FIR coefficients |
| `medfilt(a, kernel_size=None)` / `medfilt2d(input, kernelsize=None)` | 1-D / 2-D median filter |
| `wiener(input, mysize=None)` | 2-D Wiener filter |
| `order_filter(input, domain, rank)` | N-D order-statistic filter |
| `deconvolve(b, a)` | Deconvolution |
| `hilbert(x)` / `hilbert2(x)` | Analytic signal (1-D / 2-D) |
| `envelope(x)` | Signal envelope |
| `decimate(x, q, ftype=None, ...)` | Anti-aliased downsampling |
| `resample(x, num, ...)` | FFT-based resampling |
| `resample_poly(x, up, down, ...)` | Polyphase resampling (preferred for large ratios) |
| `upfirdn(filters, x, up, down, ...)` | Upsample, filter, downsample |
| `detrend(x, type='linear', ...)` | Remove linear/constant trend |

```python
from scipy.signal import lfilter, filtfilt, savgol_filter

b = [0.1, 0.2, 0.4, 0.2, 0.1]  # FIR coefficients
filtered = lfilter(b, 1.0, signal)          # causal
filtered = filtfilt(b, 1.0, signal)         # zero-phase (no phase distortion)
smoothed = savgol_filter(signal, window_length=11, polyorder=3)
```

## B-Splines

`gauss_spline`, `cspline1d`/`qspline1d` (+ `_eval` variants), `cspline2d`/`qspline2d`/`cspline2d_eval`/`qspline2d_eval`, `spline_filter`, `whittaker_henderson` (Whittaker-Henderson smoothing — **new in 1.18.0**).

## FIR Filter Design

| Function | Description |
|---|---|
| `firwin(numtaps, cutoff, window='hamming', ...)` | Windowed-sine FIR design |
| `firwin2(numtaps, f, a, ...)` | Arbitrary frequency-response FIR |
| `firwin_2d(M, N, ...)` | 2-D windowed FIR (1-D design per axis) |
| `firls(numtaps, bands, desired, ...)` | Least-squares FIR design |
| `remez(M, bands, des, ...)` | Optimal (equiripple) FIR via Remez exchange |
| `kaiserord(ripple, width)` | Kaiser window parameters from specs |
| `kaiser_beta(atten)` / `kaiser_atten(N, width)` | Kaiser beta / attenuation |
| `minimum_phase(b, a=None, ...)` | Convert linear-phase FIR to minimum phase |
| `BadCoefficients` | Warning on badly conditioned filter coefficients |

## IIR Filter Design

| Function | Description |
|---|---|
| `iirfilter(N, Wn, rp=None, rs=None, btype='band', analog=False, ftype='butter', output='ba', fs=None)` | High-level IIR design (`ftype='butter'/'cheby1'/'cheby2'/'ellip'/'bessel'`) |
| `iirdesign(wp, ws, gpass, gstop, ftype='butt', analog=False, ...)` | Design from pass/stop band specs |
| `butter(N, Wn, btype='low', analog=False, output='ba', fs=None)` | Butterworth |
| `buttord(wp, ws, gpass, gstop, analog=False, fs=None)` | Butterworth order and cutoff |
| `cheby1(N, Wn, ...)` / `cheb1ord(...)` | Chebyshev Type I |
| `cheby2(N, Wn, ...)` / `cheb2ord(...)` | Chebyshev Type II |
| `ellip(N, Wn, ...)` / `ellipord(...)` | Elliptic (Cauer) |
| `bessel(N, Wn, ...)` | Bessel (no order selection available — try `butterord`) |
| `iirnotch(W0, Q, ...)` / `iirpeak(W0, Q, ...)` / `iircomb(...)` | Second-order notch / peak / comb |

### Analog prototypes and band transforms (lower level)

Analog prototype (z, p, k): `buttap`, `cheb1ap`, `cheb2ap`, `ellipap`, `besselap`. Band transforms: `lp2bp`/`lp2bs`/`lp2hp`/`lp2lp` (+ `_zpk` variants). Prewarping: `findfreqs`. Bilinear transform: `bilinear(b, a, ...)` / `bilinear_zpk(z, p, k, ...)`. Helpers: `abcd_normalize`, `normalize`, `unique_roots`, `residue`, `residuez`, `invres`, `invresz`, `band_stop_obj`.

### Frequency response analysis

| Function | Description |
|---|---|
| `freqs(b, a, w=None)` | Analog filter response (TF form) |
| `freqs_zpk(z, p, k, w=None)` | Analog response (ZPK form) |
| `freqz(b, a, worN=None, fs=None)` | Digital filter response (TF form) |
| `freqz_zpk(z, p, k, ...)` / `freqz_sos(sos, ...)` | Digital response (ZPK / SOS form) |
| `sosfreqz` | SOS response (legacy — use `freqz_sos`) |
| `group_delay(system, w=None, ...)` | Group delay |

```python
from scipy.signal import firwin, iirfilter, freqz
import matplotlib.pyplot as plt

b = firwin(65, cutoff=200, fs=1000)     # 65 taps, 200 Hz cutoff
w, h = freqz(b, fs=1000)
plt.semilogx(w, np.abs(h))

b, a = iirfilter(4, Wn=200, btype='low', fs=1000)  # Butterworth order 4
```

## LTI Systems (Continuous-Time)

| Class/Function | Description |
|---|---|
| `lti` | Base class for continuous-time LTI systems |
| `StateSpace(A, B, C, D, name=None)` | State-space form |
| `TransferFunction(num, den, name=None)` | Transfer function form |
| `ZerosPolesGain(z, p, k, name=None)` | Zero-pole-gain form |
| `lsim(system, U=None, T=None, X0=None)` | Time-domain simulation |
| `impulse(system, T=None, X0=None)` | Impulse response |
| `step(system, T=None, X0=None)` | Step response |
| `freqresp(system, w)` | Frequency response |
| `bode(system, w=None, ...)` | Bode magnitude and phase |

```python
from scipy.signal import StateSpace, step, bode

sys = StateSpace(A=[[0, 1], [-2, -3]], B=[[0], [1]], C=[[1, 0]], D=[[0]])
t, y = step(sys)
mag, phase, w = bode(sys)
```

## LTI Systems (Discrete-Time)

| Class/Function | Description |
|---|---|
| `dlti` | Base class for discrete-time LTI systems |
| `StateSpace` / `TransferFunction` / `ZerosPolesGain` | Same classes, discrete-time semantics |
| `dlsim(system, U, T, X0=None)` | Discrete-time simulation |
| `dimpulse(system, ...)` / `dstep(system, ...)` | Discrete impulse / step response |
| `dfreqresp(system, w)` | Discrete frequency response |
| `dbode(system, w=None, ...)` | Discrete Bode plot |

## LTI Representation Conversions

| Function | Description |
|---|---|
| `tf2zpk(num, den)` / `tf2ss(num, den)` / `tf2sos(num, den)` | Transfer function → ZPK / state-space / SOS |
| `zpk2tf(z, p, k)` / `zpk2ss(z, p, k)` / `zpk2sos(z, p, k)` | ZPK → TF / state-space / SOS |
| `ss2tf(A, B, C, D)` / `ss2zpk(A, B, C, D)` | State-space → TF / ZPK |
| `sos2tf(sos)` / `sos2zpk(sos)` | SOS → TF / ZPK |
| `cont2discrete(system, dt, method='zoh')` | Continuous → discrete (ZOH, FOH, ...) |
| `place_poles(A, B, poles)` | Pole placement |

## Peak Finding

### `find_peaks(x, height=None, threshold=None, distance=None, prominence=None, width=None, plateau_size=None)`

Find peaks in a 1-D signal. Returns `(indices, properties)` — **indices, not values**; use `signal[peaks]` for values.

```python
from scipy.signal import find_peaks, peak_prominences, peak_widths

peaks, props = find_peaks(signal, height=10, distance=50, prominence=5)
prominences = peak_prominences(signal, peaks)
widths, width_heights = peak_widths(signal, peaks, rel_height=0.5)
```

### Other peak functions

| Function | Description |
|---|---|
| `argrelmin(x, axis=-1)` / `argrelmax(x, axis=-1)` | Relative minima / maxima indices |
| `argrelextrema(x, comparator)` | Relative extrema |
| `find_peaks_cwt(data, widths)` | Peaks via continuous wavelet transform |

## Spectral Analysis

| Function | Description |
|---|---|
| `periodogram(x, fs=1.0, window='hann', ...)` | Modified periodogram (PSD estimate) |
| `welch(x, fs=1.0, nperseg=256, ...)` | Welch's method PSD estimate |
| `csd(x, y, fs=1.0, nperseg=256, ...)` | Cross-spectral density |
| `coherence(x, y, fs=1.0, nperseg=256, ...)` | Magnitude-squared coherence |
| `spectrogram(x, fs=1.0, ...)` | Spectrogram (marked legacy in 1.18 — use `ShortTimeFFT`/`stft`) |
| `stft(x, fs=1.0, nperseg=256, ...)` | Short-time Fourier transform (legacy function) |
| `istft(x_stft, ...)` | Inverse STFT (legacy function) |
| `ShortTimeFFT(fs, window, nperseg, ...)` | Modern interface for STFT and its inverse (see the user guide STFT section) |
| `closest_STFT_dual_window(window, ...)` | STFT dual window closest to a desired dual window |
| `check_COLA(x, window, ...)` / `check_NOLA(...)` | COLA/NOLA constraint checks for STFT reconstruction |
| `lombscargle(t, x, freqs, ...)` | Lomb-Scargle periodogram (unevenly sampled data) |
| `vectorstrength(phases, ...)` | Vector strength (phase coherence) |

```python
from scipy.signal import welch, csd

f, psd = welch(signal, fs=1000, nperseg=1024)
f, cxx = csd(signal1, signal2, fs=1000)
```

## Waveforms

| Function | Description |
|---|---|
| `chirp(t, f0, t1, f1, method='linear')` | Frequency-swept cosine |
| `gausspulse(t, ...)` | Gaussian-modulated sinusoid |
| `max_len_seq(register_poly)` | Maximum length sequence (MLS) |
| `sawtooth(t, width=0.5)` | Periodic sawtooth wave |
| `square(t, duty=0.5)` | Square wave |
| `sweep_poly(t, coeffs)` | Polynomial frequency sweep |
| `unit_impulse(x)` | Discrete unit impulse |

## Window Functions

Window functions live in `scipy.signal.windows` (`hann`, `hamming`, `blackman`, `kaiser`, `flattop` family, `general_gaussian`, `boxcar`, `triang`, `barlett`, ...). Convenience in the `scipy.signal` namespace:

```python
from scipy.signal import get_window
w = get_window('hann', N)            # by name
w = get_window('kaiser', N)          # Kaiser (beta from default)
```

## Chirp Z-Transform and Zoom FFT

| Function | Description |
|---|---|
| `czt(x, M=None, w=None, z=None)` | Chirp z-transform convenience function |
| `zoom_fft(x, m, ...)` | Zoomed FFT on a frequency band |
| `CZT` / `ZoomFFT` | Function-generator classes (reusable, more efficient for many arrays of the same length) |
| `czt_points(M, w, z)` | Output z-plane points sampled by a chirp z-transform |

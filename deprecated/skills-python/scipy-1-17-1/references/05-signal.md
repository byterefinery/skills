# scipy.signal Reference

Signal processing, filter design, spectral analysis, and LTI systems.

## Table of Contents

- [Convolution](#convolution)
- [Filtering](#filtering)
- [Filter Design](#filter-design)
- [Matlab-Style IIR Filter Design](#matlab-style-iir-filter-design)
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
| `convolve(in1, in2, mode='full')` | 1-D convolution |
| `correlate(in1, in2, mode='full')` | 1-D correlation |
| `fftconvolve(in1, in2)` | FFT-based convolution (faster for long signals) |
| `oaconvolve(in1, in2)` | Overlap-add convolution |
| `convolve2d(in1, in2, mode='full')` | 2-D convolution |
| `correlate2d(in1, in2, mode='full')` | 2-D correlation |
| `sepfir2d(im, rowfir, colfir)` | 2-D separable FIR filtering |
| `choose_conv_method(*arrays)` | Choose faster of FFT/direct convolution |
| `correlation_lags(N, M)` | Lag indices for cross-correlation |

## Filtering

### Apply filters to data

| Function | Description |
|---|---|
| `lfilter(b, a, x, axis=-1)` | 1-D digital linear filter (FIR if a=[1], IIR otherwise) |
| `lfiltic(b, a, y, x=None)` | Construct initial conditions for lfilter |
| `lfilter_zi(b, a)` | Steady-state initial conditions for lfilter |
| `filtfilt(b, a, x)` | Forward-backward filter (zero-phase, doubles filter order) |
| `savgol_filter(x, window_length, polyorder)` | Savitzky-Golay smoothing filter |
| `medfilt(a, kernel_size=None)` | 1-D median filter |
| `medfilt2d(input, kernelsize=None)` | 2-D median filter (faster) |
| `wiener(input, mysize=None)` | 2-D Wiener filter |
| `order_filter(input, domain, rank)` | N-D order-statistic filter |

```python
from scipy.signal import lfilter, filtfilt, savgol_filter

# Apply FIR filter
b = [0.1, 0.2, 0.4, 0.2, 0.1]  # coefficients
filtered = lfilter(b, 1.0, signal)

# Zero-phase filtering (no phase distortion)
filtered = filtfilt(b, 1.0, signal)

# Savitzky-Golay smooth
smoothed = savgol_filter(signal, window_length=11, polyorder=3)
```

### B-spline filtering

| Function | Description |
|---|---|
| `gauss_spline(x)` | Gaussian approximation to B-spline basis |
| `cspline1d(a)` / `qspline1d(a)` | Cubic/quadratic B-spline coefficients |
| `cspline1d_eval(coeff, x)` / `qspline1d_eval(coeff, x)` | Evaluate spline |
| `spline_filter(a, order=3, axis=-1)` | Smoothing spline filter |

## Filter Design

### FIR filter design

| Function | Description |
|---|---|
| `firwin(numtaps, cutoff, fs=None, window='hamming')` | Windowed FIR design |
| `firwin2(numtaps, f, a, fs=None)` | Arbitrary frequency response FIR |
| `firwin_2d(M, N, ...)` | 2-D windowed FIR design |
| `firls(numtaps, bands, desired, ...)` | Least-squares FIR design |
| `kaiserord(ripple, width)` | Kaiser window parameters from specs |
| `kaiser_beta(beta)` | Kaiser beta parameter |
| `kaiser_atten(N, width)` | Kaiser attenuation |

### IIR filter design

| Function | Description |
|---|---|
| `iirfilter(N, Wn, btype='lowpass', fs=None, ftype='butt')` | IIR filter (Butterworth, Chebyshev, Elliptic, Bessel) |
| `iirdesign(ypass, stop, gpass, gstop, fs=None, ftype='butt')` | Design from pass/stop band specs |
| `bilinear(b, a, fs=1.0)` | Bilinear (Tustin) transform: analog → digital |
| `bilinear_zpk(z, p, k, fs=1.0)` | Bilinear transform in ZPK form |

### Frequency response analysis

| Function | Description |
|---|---|
| `freqs(b, a, w=None)` | Analog filter frequency response (TF form) |
| `freqz(b, a, worN=None, fs=None)` | Digital filter frequency response (TF form) |
| `freqz_zpk(z, p, k, worN=None)` | Digital filter response (ZPK form) |
| `freqs_zpk(z, p, k, w=None)` | Analog filter response (ZPK form) |
| `sosfreqz(sos, worN=None, fs=None)` | SOS format filter response |
| `group_delay(system, w=None, fs=None)` | Group delay of a filter |
| `findfreqs(b, a, n_freqs=512)` | Find frequencies for filter response |

```python
from scipy.signal import firwin, iirfilter, freqz

# Design low-pass FIR filter
b = firwin(65, cutoff=0.2, fs=1000)  # 65 taps, 200 Hz cutoff, 1000 Hz sample rate
w, h = freqz(b, fs=1000)
plt.semilogy(w, np.abs(h))

# Design Butterworth IIR filter
b, a = iirfilter(4, Wn=0.2, btype='low', fs=1000)
```

## Matlab-Style IIR Filter Design

| Function | Description |
|---|---|
| `buttord(Wp, Ws, Gpass, Gstop, analog=False, fs=None)` | Butterworth order and cutoff |
| `butter(N, Wn, btype='low', analog=False, fs=None, output='ba')` | Butterworth filter |
| `cheb1ord(...)` / `cheb2ord(...)` | Chebyshev I/II order estimation |
| `cheby1(N, Rp, Wn, ...)` / `cheby2(N, Rs, Wn, ...)` | Chebyshev I/II filter |
| `ellipord(...)` | Elliptic order estimation |
| `ellip(N, Rp, Rs, Wn, ...)` | Elliptic (Cauer) filter |
| `bessel(N, Wn, ...)` | Bessel/Thomson filter |

## LTI Systems (Continuous-Time)

### System classes

| Class | Description |
|---|---|
| `lti` | Base class for continuous-time LTI systems |
| `StateSpace(A, B, C, D, name=None)` | State-space representation |
| `TransferFunction(num, den, name=None)` | Transfer function (numerator/denominator polynomials) |
| `ZerosPolesGain(z, p, k, name=None)` | Zero-pole-gain form |

### Analysis functions

| Function | Description |
|---|---|
| `lsim(system, U=None, T=None, X0=None)` | Time-domain simulation |
| `impulse(system, T=None, X0=None)` | Impulse response |
| `step(system, T=None, X0=None)` | Step response |
| `freqresp(system, w)` | Frequency response |
| `bode(system, w, plot=False)` | Bode magnitude and phase |

```python
from scipy.signal import StateSpace, step, bode

# Define a second-order system
A = [[0, 1], [-2, -3]]
B = [[0], [1]]
C = [[1, 0]]
D = [[0]]
sys = StateSpace(A, B, C, D)

t, y = step(sys)
mag, phase, w = bode(sys, plot=True)
```

## LTI Systems (Discrete-Time)

| Class/Function | Description |
|---|---|
| `dlti` | Base class for discrete-time LTI systems |
| `dlsim(system, U, T, X0=None)` | Discrete-time simulation |
| `dimpulse(system, ...)` | Discrete impulse response |
| `dstep(system, ...)` | Discrete step response |
| `dfreqresp(system, w)` | Discrete frequency response |
| `dbode(system, w, plot=False)` | Discrete Bode plot |

## LTI Representation Conversions

| Function | Description |
|---|---|
| `tf2zpk(num, den)` | Transfer function → zeros, poles, gain |
| `tf2ss(num, den)` | Transfer function → state-space |
| `tf2sos(num, den)` | Transfer function → second-order sections |
| `zpk2tf(z, p, k)` | ZPK → transfer function |
| `zpk2ss(z, p, k)` | ZPK → state-space |
| `zpk2sos(z, p, k)` | ZPK → SOS |
| `ss2tf(A, B, C, D)` | State-space → transfer function |
| `ss2zpk(A, B, C, D)` | State-space → ZPK |
| `sos2tf(sos)` | SOS → transfer function |
| `sos2zpk(sos)` | SOS → ZPK |
| `cont2discrete(system, dt, method='zoh')` | Continuous → discrete (ZOH, FOH, etc.) |
| `place_poles(A, B, poles)` | Pole placement (Bass-Gura/Ackermann) |

## Peak Finding

### `find_peaks(x, height=None, threshold=None, distance=None, prominence=None, width=None, plateau_size=None)`

Find peaks in 1-D signal. Returns `(indices, properties)`.

```python
from scipy.signal import find_peaks, peak_prominences, peak_widths

# Basic peak finding
peaks, props = find_peaks(signal, height=10, distance=50, prominence=5)

# Get additional properties
prominences = peak_prominences(signal, peaks)
widths, width_heights = peak_widths(signal, peaks, rel_height=0.5)
```

### Other peak functions

| Function | Description |
|---|---|
| `argrelmax(x, axis=-1)` | Relative maxima indices |
| `argrelmin(x, axis=-1)` | Relative minima indices |
| `argrelextrema(x, comparator)` | Relative extrema |
| `find_peaks_cwt(data, widths)` | Peaks via continuous wavelet transform |

## Spectral Analysis

| Function | Description |
|---|---|
| `periodogram(x, fs=1.0, window='hann')` | Modified periodogram (PSD estimate) |
| `welch(x, fs=1.0, nperseg=256)` | Welch's method PSD estimate |
| `csd(x, y, fs=1.0, nperseg=256)` | Cross-spectral density |
| `coherence(x, y, fs=1.0, nperseg=256)` | Magnitude-squared coherence |
| `spectrogram(x, fs=1.0, nperseg=256)` | Spectrogram (legacy) |
| `lombscargle(t, x, freq)` | Lomb-Scargle periodogram (unevenly sampled) |
| `vectorstrength(phases)` | Vector strength (circular statistics) |
| `stft(x, fs=1.0, nperseg=256)` | Short-time Fourier transform (legacy) |
| `istft(stft_matrix, ...)` | Inverse STFT (legacy) |
| `ShortTimeFFT(fs, window, nperseg, ...)` | Modern STFT interface class |

```python
from scipy.signal import welch, csd

# Power spectral density
f, psd = welch(signal, fs=1000, nperseg=1024)
plt.semilogy(f, psd)

# Cross-spectral density
f, cxx = csd(signal1, signal2, fs=1000)
```

## Waveforms

| Function | Description |
|---|---|
| `chirp(t, f0, t1, f1, method='linear')` | Frequency-swept cosine |
| `gausspulse(t, ...)` | Gaussian-modulated sinusoid |
| `sawtooth(t, width=0.5)` | Periodic sawtooth wave |
| `square(t, duty=0.5)` | Square wave |
| `max_len_seq(register_poly)` | Maximum length sequence (MLS) |
| `sweep_poly(t, coeffs)` | Polynomial frequency sweep |
| `unit_impulse(x)` | Discrete unit impulse |

## Window Functions

Window functions are in `scipy.signal.windows`:
- `windows.hann(N)`, `windows.hamming(N)`, `windows.blackman(N)`
- `windows.kaiser(N, beta)`, `windows.flattop(N)`, `windows.nuttall(N)`
- `windows.general_gaussian(N, std, sym=True)`
- Convenience: `signal.get_window('hann', N)` by name

## Chirp Z-Transform and Zoom FFT

| Function | Description |
|---|---|
| `czt(x, M=None, w=None, z=None)` | Chirp z-transform |
| `zoom_fft(x, m, ...)` | Zoomed FFT on a frequency band |
| `CZT(x)` / `ZoomFFT(x)` | Function generator classes |
| `czt_points(M, w, z)` | Output z-plane points for CZT |

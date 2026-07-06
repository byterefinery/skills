# Filters & Analysis

## Filter

Full-featured biquad filter with Signal-based frequency and Q control.

```js
const filter = new Tone.Filter(400, "lowpass").toDestination();
synth.connect(filter);
```

### Constructor

```js
new Tone.Filter(frequency, type)
new Tone.Filter(options)
```

### Options

| Option | Type | Default | Description |
|---|---|---|---|
| `frequency` | Frequency | `800` | Cutoff frequency |
| `type` | BiquadFilterType | `"lowpass"` | Filter type |
| `Q` | number | `1` | Resonance |
| `rolloff` | number | `-24` | dB/octave (-12, -24, -48) |

### Filter Types

`"lowpass"`, `"highpass"`, `"bandpass"`, `"notch"`, `"peaking"`, `"lowshelf"`, `"highshelf"`

### Key Properties

```js
filter.frequency.value = 2000;    // Signal<"frequency">
filter.Q.value = 6;               // Signal<"number">
filter.rolloff = -48;             // steeper filter
filter.type = "highpass";
```

### Modulating Filter Frequency

```js
// LFO modulation
const lfo = new Tone.LFO("2n", 200, 4000).start();
lfo.connect(filter.frequency);

// Envelope modulation (filter sweep)
const filterEnv = new Tone.Envelope({
  attack: 0.01,
  decay: 0.3,
  sustain: 0,
  release: 0.5,
});
filterEnv.connect(filter.frequency);
```

## BiquadFilter

Direct wrapper around `BiquadFilterNode`.

```js
const biquad = new Tone.BiquadFilter({
  frequency: 1000,
  type: "lowpass",
  Q: 2,
}).toDestination();
```

## EQ3

Three-band equalizer (low, mid, high).

```js
const eq = new Tone.EQ3({
  low: -6,    // dB
  mid: 3,
  high: -3,
}).toDestination();
```

| Property | Type | Description |
|---|---|---|
| `low` | Decibels | Low shelf gain |
| `mid` | Decibels | Peaking EQ gain |
| `high` | Decibels | High shelf gain |

## OnePoleFilter

Simple one-pole (6 dB/octave) lowpass/highpass filter.

```js
const filter = new Tone.OnePoleFilter(400, "lowpass").toDestination();
```

## FeedbackCombFilter

Comb filter with feedback — basis for reverberation.

```js
const comb = new Tone.FeedbackCombFilter(440).toDestination();
```

| Option | Type | Default | Description |
|---|---|---|---|
| `frequency` | Frequency | `440` | Delay time as frequency |
| `resonance` | NormalRange | `0.5` | Feedback amount |

## LowpassCombFilter

Comb filter with lowpass on the feedback path.

```js
const comb = new Tone.LowpassCombFilter({
  frequency: 440,
  resonance: 0.5,
  damping: 1000,
}).toDestination();
```

## Convolver

Convolution processing — typically used for reverb with impulse responses.

```js
const convolver = new Tone.Convolver("impulse.wav").toDestination();

// Or with an AudioBuffer
const convolver = new Tone.Convolver(buffer).toDestination();
```

### Options

| Option | Type | Default | Description |
|---|---|---|---|
| `channelCount` | number | `2` | Number of channels |

## Analyser

FFT-based audio analysis.

```js
const analyser = new Tone.Analyser("fft", 2048);
synth.connect(analyser);

// Get FFT data
const values = analyser.getValue();  // Float32Array in dB

// Get waveform
const waveform = analyser.getWaveform();  // Float32Array
```

### Constructor

```js
new Tone.Analyser(type, size)
```

| Type | Description |
|---|---|
| `"fft"` | Frequency domain (FFT) |
| `"wave"` | Time domain (waveform) |

### Options

| Option | Type | Default | Description |
|---|---|---|---|
| `smoothing` | NormalRange | `0.95` | Temporal smoothing |
| `size` | number | `2048` | FFT size |

## FFT

Raw FFT computation.

```js
const fft = new Tone.FFT(1024);
synth.connect(fft);
const values = fft.getValue();  // dB spectrum
```

## Waveform

Waveform (time-domain) analysis.

```js
const waveform = new Tone.Waveform(1024);
synth.connect(waveform);
const samples = waveform.getValue();  // Float32Array [-1, 1]
```

## Meter

Level meter (RMS in dB).

```js
const meter = new Tone.Meter();
synth.connect(meter);

console.log(meter.getValue());  // current level in dB
meter.clear();                  // reset history
```

## DCMeter

DC offset meter — measures the average value of a signal.

```js
const dc = new Tone.DCMeter();
synth.connect(dc);
console.log(dc.getValue());  // average value
```

## Follower

Amplitude follower — tracks the signal's amplitude with attack/release smoothing.

```js
const follower = new Tone.Follower({
  attack: 0.005,
  release: 0.1,
});
synth.connect(follower);

// Connect follower output to control another parameter
follower.connect(filter.frequency);
```

### Options

| Option | Type | Default | Description |
|---|---|---|---|
| `attack` | Time | `0.005` | Attack time |
| `release` | Time | `0.1` | Release time |
| `smoothing` | NormalRange | `0` | Additional smoothing |

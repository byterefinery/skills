# Instruments

All instruments extend `Instrument` and connect to the audio graph via `.connect()`, `.chain()`, or `.toDestination()`.

## Synth

Basic monophonic synthesizer: `OmniOscillator` → `AmplitudeEnvelope`.

```js
const synth = new Tone.Synth({
  oscillator: { type: "triangle" },
  envelope: { attack: 0.005, decay: 0.1, sustain: 0.3, release: 1 },
}).toDestination();

synth.triggerAttackRelease("C4", "8n");
```

### Options

| Option | Type | Default | Description |
|---|---|---|---|
| `oscillator.type` | ToneOscillatorType | `"triangle"` | Oscillator waveform |
| `oscillator.partialCount` | number | `0` | Harmonic limit |
| `envelope.attack` | Time | `0.005` | Attack time |
| `envelope.decay` | Time | `0.1` | Decay time |
| `envelope.sustain` | NormalRange | `0.3` | Sustain level |
| `envelope.release` | Time | `1` | Release time |

### Accessing Sub-components

```js
synth.oscillator.type = "sawtooth";
synth.frequency.value = "D4";
synth.detune.value = -12;
synth.envelope.attack = 0.1;
synth.envelope.sustain = 0.5;
```

### Methods

```js
synth.triggerAttack(note, time, velocity);
synth.triggerRelease(time);
synth.triggerAttackRelease(note, duration, time, velocity);
synth.getLevelAtTime(time);  // envelope value at time
synth.dispose();
```

## PolySynth

Polyphonic wrapper around any monophonic instrument. Manages voice allocation and garbage collection.

```js
// Default: polyphonic Synth
const poly = new Tone.PolySynth().toDestination();
poly.triggerAttackRelease(["C4", "E4", "G4"], "4n");

// With different voice type
const fmPoly = new Tone.PolySynth(Tone.FMSynth).toDestination();
const amPoly = new Tone.PolySynth(Tone.AMSynth, {
  modulationIndex: 2,
}).toDestination();
```

### Options

| Option | Type | Default | Description |
|---|---|---|---|
| `maxPolyphony` | number | `32` | Max simultaneous voices |
| `voice` | constructor | `Synth` | Voice instrument class |
| `options` | object | `{}` | Options passed to each voice |

### Methods

```js
poly.triggerAttack(notes, time, velocity);
poly.triggerRelease(notes, time);   // must specify which notes
poly.triggerAttackRelease(notes, duration, time, velocity);
poly.releaseAll(time);              // release all active voices
poly.set({ envelope: { attack: 0.2 } });  // set on all voices
poly.get();                         // get voice options
poly.activeVoices;                  // number of active voices
```

### Per-note Durations

```js
poly.triggerAttackRelease(
  ["C4", "E4", "G4", "B4"],
  [4, 3, 2, 1],  // different duration per note
);
```

## MonoSynth

More expressive monophonic synth with filter + amplitude envelopes.

```js
const mono = new Tone.MonoSynth({
  oscillator: { type: "square" },
  filter: { Q: 6, frequency: 2000 },
  envelope: { attack: 0.1, decay: 0.3, sustain: 0.4, release: 0.8 },
  filterEnvelope: { attack: 0.01, decay: 0.2, sustain: 0.5, release: 0.5 },
}).toDestination();

mono.triggerAttackRelease("C4", "4n");
```

### Key Properties

```js
mono.oscillator.type = "sawtooth";
mono.filter.frequency.value = 3000;
mono.filter.Q.value = 4;
mono.envelope.attack = 0.05;
mono.filterEnvelope.amount = 4000;  // filter sweep depth
```

## FMSynth

Frequency modulation synthesis with modulator and carrier oscillators.

```js
const fm = new Tone.FMSynth({
  harmonicity: 3,
  modulationIndex: 10,
  oscillator: { type: "sine" },
  modulation: { type: "square" },
  envelope: { attack: 0.01, decay: 0.1, sustain: 0.4, release: 0.8 },
  modulationEnvelope: { attack: 0.5, decay: 0, sustain: 1, release: 0.2 },
}).toDestination();

fm.triggerAttackRelease("C3", "2n");
```

### Options

| Option | Type | Default | Description |
|---|---|---|---|
| `harmonicity` | number | `3` | Frequency ratio of modulator to carrier |
| `modulationIndex` | number | `10` | FM depth |
| `oscillator` | OmniOscillatorOptions | `{ type: "sine" }` | Carrier |
| `modulation` | OmniOscillatorOptions | `{ type: "square" }` | Modulator |

## AMSynth

Amplitude modulation synthesis.

```js
const am = new Tone.AMSynth({
  harmonicity: 3,
  modulationIndex: 1,
  oscillator: { type: "sine" },
  modulation: { type: "sine" },
}).toDestination();

am.triggerAttackRelease("C4", "4n");
```

## DuoSynth

Two oscillators with detune and a filter.

```js
const duo = new Tone.DuoSynth({
  harmonicity: 2,
  detune: 10,
  oscillator: { type: "sawtooth" },
  envelope: { attack: 0.02, decay: 0.1, sustain: 0.3, release: 0.8 },
  filterEnvelope: { attack: 0.01, decay: 0.2, sustain: 0.5, release: 0.5 },
}).toDestination();

duo.triggerAttackRelease("C4", "4n");
```

## MembraneSynth

Drum-like low-frequency percussion.

```js
const kick = new Tone.MembraneSynth({
  pitchDecay: 0.05,
  octaves: 4,
  pulse: 1,
}).toDestination();

kick.triggerAttackRelease("C1", "8n");
```

| Option | Type | Default | Description |
|---|---|---|---|
| `pitchDecay` | Time | `0.05` | How fast pitch drops |
| `octaves` | number | `4` | Pitch drop range |
| `pulse` | NormalRange | `1` | Pulse width (1 = sine) |

## MetalSynth

Metallic, bell-like tones.

```js
const metal = new Tone.MetalSynth({
  frequency: 200,
  envelope: { attack: 0.001, decay: 0.4, release: 0.02 },
  modulationIndex: 200,
  harmonicity: 1.5,
}).toDestination();

metal.triggerAttackRelease("4n");
```

## PluckSynth

Karplus-Strong string pluck.

```js
const pluck = new Tone.PluckSynth({
  attack: 0.001,
  decay: 3,
  resonance: 2000,
  octaves: 2,
  modulationIndex: 8,
}).toDestination();

pluck.triggerAttackRelease("E2", "2n");
```

## NoiseSynth

Noise source with filter and envelope.

```js
const noise = new Tone.NoiseSynth({
  noise: { type: "white" },
  envelope: { attack: 0.005, decay: 0.1, sustain: 0, release: 0.3 },
  filter: { type: "lowpass", frequency: 4000, Q: 1 },
}).toDestination();

noise.triggerAttackRelease("8n");
```

## Sampler

Sample-based instrument with pitch mapping.

```js
const sampler = new Tone.Sampler({
  urls: {
    A0: "A0.mp3",
    C1: "C1.mp3",
    E1: "E1.mp3",
  },
  baseUrl: "https://tonejs.github.io/audio/salamander/",
  onload: () => {
    sampler.triggerAttackRelease("C2", "4n");
  },
}).toDestination();
```

### Options

| Option | Type | Default | Description |
|---|---|---|---|
| `urls` | object | `{}` | Note → URL mapping |
| `baseUrl` | string | `""` | Base URL prepended to all URLs |
| `attack` | Time | `0` | Envelope attack |
| `release` | Time | `0` | Envelope release |
| `onload` | function | — | Called when all samples load |
| `curve` | string | `"exponential"` | Interpolation curve |

### Methods

```js
sampler.triggerAttack(note, time, velocity);
sampler.triggerRelease(note, time);
sampler.triggerAttackRelease(note, duration, time, velocity);
sampler.releaseAll(time);
sampler.dispose();
```

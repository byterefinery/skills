# Signals & Envelopes

## Signal

Audio-rate controllable value. The core building block for modulation in Tone.js. Signals have all `AudioParam` methods plus scheduling conveniences.

```js
const signal = new Tone.Signal(440, "frequency");
signal.connect(oscillator.frequency);
signal.rampTo(880, 2);  // ramp to 880 Hz over 2 seconds
```

### Constructor

```js
new Tone.Signal(value, units)
new Tone.Signal(options)
```

### Options

| Option | Type | Default | Description |
|---|---|---|---|
| `value` | number | `0` | Initial value |
| `units` | UnitName | `"number"` | Unit type |
| `convert` | boolean | `true` | Auto-convert input to units |

### Unit Types

`"number"`, `"frequency"`, `"time"`, `"transportTime"`, `"ticks"`, `"bpm"`, `"decibels"`, `"normalRange"`, `"audioRange"`, `"degrees"`, `"radians"`, `"hertz"`, `"cents"`, `"samples"`, `"gain"`, `"positive"`

### AudioParam Methods

All signals support the standard Web Audio `AudioParam` scheduling methods:

```js
signal.setValueAtTime(value, time);
signal.linearRampToValueAtTime(value, time);
signal.exponentialRampToValueAtTime(value, time);
signal.setTargetAtTime(value, time, timeConstant);
signal.setValueCurveAtTime(values, time, duration);
signal.setPeriodicWave(pw);
signal.cancelScheduledValues(time);
```

### Convenience Methods

```js
signal.value = 440;                          // immediate set
signal.rampTo(value, rampTime, startTime);   // linear ramp
signal.exponentialRampTo(value, rampTime, startTime);
signal.linearRampTo(value, rampTime, startTime);
signal.exponentialRampTo(value, rampTime, startTime);
signal.targetRampTo(value, timeConstant, startTime);
signal.setScheduleUpdateInterval(interval);
signal.cancelScheduledUpdates();
```

### Override Behavior

When a Signal connects to an AudioParam or another Signal, it **overrides** the destination's value. Disconnect to restore the original control path.

## Param

A `Param` wraps a native `AudioParam` with Tone.js unit conversion and scheduling.

```js
const gain = new Tone.Gain();
gain.gain.value = -6;       // Decibels
gain.gain.rampTo(0, 0.5);   // ramp to 0dB over 0.5s
```

Params support the same scheduling methods as Signals.

## Envelope

ADSR envelope generator. Outputs a signal that can modulate any parameter.

```js
const env = new Tone.Envelope({
  attack: 0.01,
  decay: 0.2,
  sustain: 0.5,
  release: 1,
  attackCurve: "exponential",
  decayCurve: "exponential",
  releaseCurve: "exponential",
}).toDestination();

env.triggerAttack(Tone.now());
env.triggerRelease(Tone.now() + 1);
```

### Options

| Option | Type | Default | Description |
|---|---|---|---|
| `attack` | Time | `0.01` | Time to reach peak |
| `decay` | Time | `0.1` | Time to fall to sustain |
| `sustain` | NormalRange | `0` | Level held during sustain |
| `release` | Time | `0.1` | Time to fall to zero |
| `attackCurve` | EnvelopeCurve | `"exponential"` | Attack shape |
| `decayCurve` | BasicEnvelopeCurve | `"exponential"` | Decay shape |
| `releaseCurve` | EnvelopeCurve | `"exponential"` | Release shape |

### Envelope Curves

- `"linear"` — straight line
- `"exponential"` — exponential curve
- `number[]` — custom array of values for arbitrary shape

### Methods

```js
env.triggerAttack(time, velocity);
env.triggerRelease(time);
env.triggerAttackRelease(duration, time, velocity);
env.getValueAtTime(time);  // sample the envelope at a time
env.dispose();
```

### Modulating Parameters

```js
// Control filter frequency with an envelope
const env = new Tone.Envelope({
  attack: 0.01,
  decay: 0.3,
  sustain: 0,
  release: 0.5,
});
env.connect(filter.frequency);

// On note on, trigger the filter sweep
synth.on("noteon", () => env.triggerAttack());
synth.on("noteoff", () => env.triggerRelease());
```

## AmplitudeEnvelope

Convenience class for amplitude (gain) envelopes. Connects to a `Gain` node internally.

```js
const ampEnv = new Tone.AmplitudeEnvelope({
  attack: 0.005,
  decay: 0.1,
  sustain: 0.3,
  release: 1,
});

oscillator.chain(ampEnv, Tone.getDestination());
ampEnv.triggerAttackRelease("8n");
```

## FrequencyEnvelope

Envelope that outputs frequency values.

```js
const freqEnv = new Tone.FrequencyEnvelope({
  attack: 0.01,
  decay: 0.2,
  sustain: 0.5,
  release: 0.5,
  baseFrequency: 200,
  octaves: 4,
  exponent: 4,
});
freqEnv.connect(filter.frequency);
freqEnv.triggerAttackRelease("4n");
```

| Option | Type | Default | Description |
|---|---|---|---|
| `baseFrequency` | Frequency | `200` | Base frequency |
| `octaves` | number | `4` | Range in octaves |
| `exponent` | number | `4` | Scaling exponent |

## SyncedSignal

A Signal synced to the Transport BPM. Changes to BPM automatically scale the signal value.

```js
const synced = new Tone.SyncedSignal(440, "frequency");
synced.connect(oscillator.frequency);
// When transport BPM doubles, this signal's output doubles too
```

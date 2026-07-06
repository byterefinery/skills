# Sources & Oscillators

## Oscillator

The core tone generator. Wraps the native `OscillatorNode` with phase rotation, partial limiting, and transport sync.

```js
const osc = new Tone.Oscillator(440, "sine").toDestination().start();
```

### Constructor

```js
new Tone.Oscillator(frequency, type)
new Tone.Oscillator(options)
```

### Options

| Option | Type | Default | Description |
|---|---|---|---|
| `frequency` | Frequency | `"440"` | Starting frequency |
| `type` | ToneOscillatorType | `"sine"` | Waveform type |
| `detune` | Cents | `0` | Detune in cents |
| `phase` | Degrees | `0` | Phase offset (0-360) |
| `partials` | number[] | `[]` | Custom harmonic partials |
| `partialCount` | number | `0` | Limit number of partials |

### Waveform Types

Basic: `"sine"`, `"square"`, `"sawtooth"`, `"triangle"`, `"custom"`

With partial count: `"sine8"`, `"square16"`, `"sawtooth32"`, `"triangle64"` — truncates harmonics to the given count.

### Key Properties

```js
osc.frequency.value = "C4";        // Signal<"frequency">
osc.detune.value = -12;            // Signal<"cents">
osc.type = "sawtooth";
osc.phase = 90;                    // degrees
osc.partialCount = 8;
osc.partials = [1, 0.5, 0.25];     // custom harmonics
```

### Methods

```js
osc.start(time);           // Start the oscillator
osc.stop(time);            // Stop the oscillator
osc.restart(time);         // Cancel scheduled stop, keep running
osc.syncFrequency();       // Sync to Transport BPM
osc.unsyncFrequency();     // Unsync from Transport
osc.asArray(length);       // Promise<Float32Array> — sample waveform
osc.dispose();             // Clean up
```

### Custom Waveforms

```js
// Set custom partials (harmonic amplitudes)
osc.partials = [1, 0.5, 0.25, 0.125];
osc.type = "custom";

// Generate waveform array for inspection
const samples = await osc.asArray(1024);
```

## OmniOscillator

Superset of Oscillator that also supports `"pulse"`, `"pwm"`, and `"am"` types. Used internally by `Synth`.

```js
const osc = new Tone.OmniOscillator("C4", "pulse").toDestination().start();
osc.pulseWidth = 0.25;  // 0-1, pulse width modulation
```

Additional types beyond basic Oscillator: `"pulse"`, `"pwm"`, `"am"`.

## Specialized Oscillators

### FatOscillator

Layers multiple slightly detuned oscillators for a thick sound.

```js
const fat = new Tone.FatOscillator("C4", "sawtooth", 3).toDestination().start();
fat.spread = 20;  // cents of detuning between voices
```

### PulseOscillator

Sawtooth oscillator with controllable pulse width.

```js
const pulse = new Tone.PulseOscillator("C4").toDestination().start();
pulse.width = 0.25;  // 0-1, narrower = thinner sound
```

### PWMOscillator

Pulse-width modulation — an LFO modulates the pulse width.

```js
const pwm = new Tone.PWMOscillator("C4", "4n").toDestination().start();
pwm.modulationIndex = 0.5;  // depth of PWM
```

### AMOscillator

Amplitude modulation oscillator.

```js
const am = new Tone.AMOscillator("C4", 4).toDestination().start();
am.modulationIndex = 1;
```

### FMOscillator

Frequency modulation oscillator.

```js
const fm = new Tone.FMOscillator("C4", 3).toDestination().start();
fm.modulationIndex = 10;
fm.harmonicity = 2;
```

## LFO

Low-frequency oscillator for modulating parameters. Outputs a signal that can connect to any `AudioParam` or `Signal`.

```js
const lfo = new Tone.LFO("4n", 200, 800).start();
lfo.connect(filter.frequency);
```

### Constructor

```js
new Tone.LFO(frequency, min, max)
new Tone.LFO(options)
```

### Options

| Option | Type | Default | Description |
|---|---|---|---|
| `frequency` | Frequency | `"1n"` | LFO rate |
| `min` | number | `-1` | Minimum output value |
| `max` | number | `1` | Maximum output value |
| `amplitude` | NormalRange | `1` | Modulation depth (0-1) |
| `type` | ToneOscillatorType | `"sine"` | Waveform |
| `phase` | Degrees | `0` | Phase offset |
| `units` | UnitName | `"number"` | Output unit type |

### Key Properties

```js
lfo.frequency.value = "2n";
lfo.min = 100;
lfo.max = 2000;
lfo.amplitude.value = 0.7;
lfo.type = "triangle";
lfo.phase = 90;
```

### Methods

```js
lfo.start(time);
lfo.stop(time);
lfo.syncFrequency();    // Sync LFO rate to Transport BPM
lfo.dispose();
```

## Noise

Generates white, pink, or brown noise.

```js
const noise = new Tone.Noise("white").toDestination().start();
```

### Types

- `"white"` — equal energy per frequency
- `"pink"` — equal energy per octave
- `"brown"` — power decreases with frequency

### Options

| Option | Type | Default | Description |
|---|---|---|---|
| `type` | `"white"\|"pink"\|"brown"` | `"white"` | Noise color |

### Methods

```js
noise.start(time);
noise.stop(time);
noise.dispose();
```

## Source Base Class

All sources extend `Source`. Common properties:

```js
source.volume.value = -6;       // Decibels
source.mute = true;             // Instant mute
source.state;                   // "started" | "stopped"
source.sync();                  // Sync start/stop to Transport
source.desync();                // Desync from Transport
source.dispose();
```

### State Management

Sources use a `StateTimeline` for scheduling start/stop events with sample-accurate timing. Multiple state changes can be chained but must be in ascending time order.

```js
// Valid
source.start().stop("+0.2").start("+0.4").stop("+0.7");

// Invalid — descending times
source.stop("+0.2").start();
```

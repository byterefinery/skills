---
name: tone-js-15-1-22
description: Tone.js 15.1.22 — Web Audio framework for interactive music in the browser. Covers the full API: oscillators, instruments (Synth, PolySynth, Sampler, etc.), effects (Reverb, Delay, Chorus, Distortion, etc.), filters, envelopes, signals, Transport scheduling, Part/Loop/Sequence events, Player/buffers, routing (Panner, Volume, Merge/Split), LFO modulation, and Offline rendering. Use when working with tone@15.1.x, building web synthesizers, music apps, audio effects chains, scheduled compositions, or any browser-based interactive audio project.
metadata:
  tags:
    - javascript
    - audio
    - web-audio
    - music
    - synthesis
---

# tone-js 15.1.22

Tone.js is a Web Audio framework for creating interactive music in the browser. It provides DAW-like features (global Transport, scheduling, synths, effects) and low-level building blocks (Signals, Envelopes, AudioWorklets) for custom instruments and effects.

## Overview

- **Package**: `tone@15.1.22` (ESM-first, also UMD via `build/Tone.js`)
- **Import**: `import * as Tone from "tone"` (ESM) or `Tone` global (UMD)
- **AudioContext**: Managed automatically; call `await Tone.start()` on user gesture before playing
- **Global singletons**: `Tone.getTransport()`, `Tone.getDestination()`, `Tone.getListener()`, `Tone.getContext()`
- **Time system**: All timing accepts `"4n"`, `"8t"`, `"1:0:0"`, `"+1"`, numbers (seconds), or `Tone.now()`
- **Connection**: `.connect()`, `.chain()`, `.fan()`, `.toDestination()`, `Tone.fanIn()`
- **Lifecycle**: Always `.dispose()` nodes when done to free Web Audio resources

### Quick Start

```js
import * as Tone from "tone";

// Must be called from a user gesture (click, keydown)
await Tone.start();

// Monophonic synth
const synth = new Tone.Synth().toDestination();
synth.triggerAttackRelease("C4", "8n");

// Polyphonic synth (chords)
const poly = new Tone.PolySynth().toDestination();
poly.triggerAttackRelease(["C4", "E4", "G4"], "4n");

// With effects
const reverb = new Tone.Reverb(2).toDestination();
synth.connect(reverb);
```

### Transport Scheduling

```js
const synth = new Tone.Synth().toDestination();
const transport = Tone.getTransport();
transport.bpm.value = 120;

// Schedule a repeating callback every 8th note
transport.scheduleRepeat((time) => {
  synth.triggerAttackRelease("C4", "8n", time);
}, "8n");

transport.start();
```

## Usage

### Connection Patterns

```js
// Series: source → effect1 → effect2 → destination
source.chain(effect1, effect2, Tone.getDestination());

// Parallel: source → multiple destinations
source.fan(reverb, delay);

// Multiple sources → single destination
Tone.fanIn(source1, source2, compressor);

// Direct to speakers
node.toDestination();
```

### Time Encodings

| Format | Example | Meaning |
|---|---|---|
| Seconds | `1.5` | 1.5 seconds from context start |
| Notation | `"4n"`, `"8t"`, `"1m"` | Quarter note, 8th triplet, 1 measure |
| Transport | `"1:2:0"` | Bar 1, beat 2, sixteenth 0 |
| Frequency | `"2hz"` | Duration of one cycle at 2 Hz (= 0.5s) |
| Now-relative | `"+1"` | Current time + 1 second |
| Ticks | `"4t"` | 4 transport ticks |

### Instrument Quick Reference

| Instrument | Type | Notes |
|---|---|---|
| `Synth` | Monophonic | Single oscillator + amplitude envelope |
| `MonoSynth` | Monophonic | Filter + envelope, more expressive |
| `PolySynth` | Polyphonic | Voice-allocated; wraps any monophonic synth |
| `FMSynth` | Monophonic | FM synthesis (modulator + carrier) |
| `AMSynth` | Monophonic | AM synthesis |
| `DuoSynth` | Monophonic | Two oscillators with detune + filter |
| `MetalSynth` | Monophonic | Metallic/percussive tones |
| `MembraneSynth` | Monophonic | Drum-like low-frequency hits |
| `PluckSynth` | Monophonic | Karplus-Strong string pluck |
| `NoiseSynth` | Monophonic | Noise source with filter + envelope |
| `Sampler` | Polyphonic | Sample-based with pitch mapping |

### Effects Quick Reference

| Effect | Use |
|---|---|
| `Reverb` / `JCReverb` / `Freeverb` | Room/space simulation |
| `PingPongDelay` / `FeedbackDelay` | Echo/tape delay |
| `Chorus` / `Phaser` / `Vibrato` | Modulation |
| `Distortion` / `Chebyshev` / `BitCrusher` | Saturation/degradation |
| `AutoFilter` / `AutoWah` / `AutoPanner` | LFO-driven modulation |
| `Tremolo` | Amplitude modulation |
| `PitchShift` | Real-time pitch transposition |
| `FrequencyShifter` | Ring modulation-style shift |
| `StereoWidener` | Stereo field expansion |

### Envelopes

```js
// ADSR envelope controlling amplitude
const env = new Tone.Envelope({
  attack: 0.01,
  decay: 0.2,
  sustain: 0.5,
  release: 1,
});

// Trigger attack/release
env.triggerAttack(Tone.now());
env.triggerRelease(Tone.now() + 1);

// AmplitudeEnvelope is a convenience for gain control
const ampEnv = new Tone.AmplitudeEnvelope();
oscillator.chain(ampEnv, Tone.getDestination());
ampEnv.triggerAttackRelease("8n");
```

### LFO Modulation

```js
// Modulate a parameter with an LFO
const lfo = new Tone.LFO("4n", 200, 800).start();
lfo.connect(oscillator.frequency);

// Sync LFO to transport
lfo.syncFrequency();

// Control depth
lfo.amplitude.value = 0.5;
```

### Buffers and Players

```js
// Load and play an audio file
const player = new Tone.Player("drum.mp3").toDestination();
player.autostart = true; // play when loaded

// Load with callback
const player2 = new Tone.Player("piano.mp3", () => {
  player2.start();
}).toDestination();

// Looping
player.loop = true;
player.loopStart = 0;
player.loopEnd = player.buffer.duration;

// Offline rendering
Tone.Offline(() => {
  const osc = new Tone.Oscillator().toDestination().start(0);
}, 2).then((buffer) => {
  const player = new Tone.Player(buffer).toDestination();
  player.start();
});
```

## Gotchas

- **`Tone.start()` is mandatory** — browsers block audio until a user gesture. Always `await Tone.start()` inside a click/keydown handler before scheduling or playing anything.
- **`dispose()` everything** — every Tone node holds Web Audio resources. Call `.dispose()` when done, or nodes leak. `PolySynth` manages its own voice disposal internally.
- **`Tone.now()` vs `Tone.immediate()`** — `now()` adds `lookAhead` (default 0.1s) for scheduling stability. Use `now()` consistently; mixing with `immediate()` causes timing drift.
- **`PolySynth` voice stealing** — when `maxPolyphony` (default 32) is exceeded, notes are dropped with a warning. Set `maxPolyphony` higher or use `releaseAll()` to free voices.
- **`triggerAttack` + `triggerRelease` are separate** — unlike `triggerAttackRelease`, you must manage timing yourself. For `PolySynth`, `triggerRelease` requires the specific note(s) to release.
- **`Sampler` needs `onload`** — samples load asynchronously. Schedule playback inside `onload` or after `Tone.loaded()` resolves.
- **`Offline` swaps the global context** — nodes created inside `Tone.Offline()` are bound to the offline context. The original context is restored after rendering completes.
- **`Transport` is per-context** — each `Context` has its own Transport. Use `Tone.getTransport()` for the global one; in `Offline`, use the passed-in context's transport.
- **`toDestination()` is not `toMaster()`** — `toMaster()` was renamed in v14. Use `toDestination()`; `toMaster()` still works but warns.
- **Signal connections override** — when a `Signal` connects to an `AudioParam` or another `Signal`, it overrides the destination's value. Disconnect to restore.
- **`Player` buffer is async** — `player.buffer` is `null` until loaded. Check via `onload` callback or `player.buffer !== null`.
- **Oscillator `type` with partial count** — `"sine8"`, `"square16"` truncates harmonics. Use `partialCount` property or append number to type string.

## References

- [01-sources-oscillators](references/01-sources-oscillators.md) — Oscillator, LFO, Noise, OmniOscillator variants, Source base class
- [02-instruments](references/02-instruments.md) — Synth, PolySynth, MonoSynth, FMSynth, AMSynth, Sampler, and all instruments
- [03-effects](references/03-effects.md) — Reverb, Delay, Chorus, Distortion, modulation effects, and effect routing
- [04-filters-analysis](references/04-filters-analysis.md) — Filter, EQ3, BiquadFilter, Convolver, Analyser, FFT, Meter
- [05-transport-events](references/05-transport-events.md) — Transport, ToneEvent, Part, Loop, Sequence, Pattern, scheduling
- [06-signals-envelopes](references/06-signals-envelopes.md) — Signal, Param, Envelope, AmplitudeEnvelope, FrequencyEnvelope
- [07-routing-channels](references/07-routing-channels.md) — Volume, Panner, Panner3D, Merge, Split, Channel, Recorder, Solo
- [08-buffers-players](references/08-buffers-players.md) — ToneAudioBuffer, Player, Players, GrainPlayer, Sampler
- [09-context-offline](references/09-context-offline.md) — Context, Offline, getContext/setContext, AudioContext lifecycle
- [10-signals-math](references/10-signals-math.md) — Signal math (Add, Subtract, Multiply, Pow, Scale, WaveShaper)

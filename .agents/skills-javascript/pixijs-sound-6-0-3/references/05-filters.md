# Filters

Filters are WebAudio-based effects, applied per-Sound or globally. **All filters require WebAudio** — in legacy (HTML5 Audio) mode filter constructors create `null` nodes, the context's `filters`/`audioContext` accessors warn and return `null`, and `sound.filtersAll` gets/sets are no-ops.

Import: `import { filters } from '@pixi/sound';` — the namespace exposes `Filter`, `ReverbFilter`, `DistortionFilter`, `EqualizerFilter`, `StereoFilter`, `TelephoneFilter`, `MonoFilter`, `StreamFilter`.

## Filter base

Every filter extends `Filter`, which wraps a WebAudio node chain:

- `destination` — input `AudioNode` (connect previous filter's output here)
- `source` — output `AudioNode` (defaults to `destination`)
- `connect(destination: AudioNode)`, `disconnect()`, `destroy()`

Connect your own filters by chaining `source` → next `destination`.

## Applying filters

```ts
// Per-sound (array order = signal order)
soundObj.filters = [ new filters.ReverbFilter(3, 2), new filters.StereoFilter(-0.5) ];

// Globally (all output; WebAudio only)
sound.filtersAll = [ new filters.StereoFilter(-1) ];

// Inline on a play call
sound.play('music', { filters: [ new filters.ReverbFilter(2, 1) ] });
```

Chaining order matters — the array order is the signal path order.

## ReverbFilter

`new ReverbFilter(seconds = 3, decay = 2, reverse = false)` — convolution reverb from a generated impulse.

- `seconds` get/set — reverb length, clamped 1–50
- `decay` get/set — decay, clamped 0–100
- `reverse` get/set — boolean; reverses the impulse
- Any change rebuilds the convolver buffer.

## DistortionFilter

`new DistortionFilter(amount = 0)` — `WaveShaperNode` with a generated curve, `oversample: '4x'`.

- `amount` get/set — 0–1; the curve scales as `amount * 1000`.

## EqualizerFilter

`new EqualizerFilter(f32, f64, f125, f250, f500, f1k, f2k, f4k, f8k, f16k)` — 10 fixed `BiquadFilterNode` bands, all default 0.

Bands (Hz) and node types:

| Band | Frequency | Node type |
|---|---|---|
| `f32` | 32 | lowshelf |
| `f64` | 64 | peaking |
| `f125` | 125 | peaking |
| `f250` | 250 | peaking |
| `f500` | 500 | peaking |
| `f1k` | 1000 | peaking |
| `f2k` | 2000 | peaking |
| `f4k` | 4000 | peaking |
| `f8k` | 8000 | peaking |
| `f16k` | 16000 | highshelf |

- Static band constants: `EqualizerFilter.F32` … `EqualizerFilter.F16K`.
- `bands` (readonly array), `bandsMap` (readonly, keyed by frequency).
- `set f32`/`get f32` … `set f16k`/`get f16k` — per-band gain accessors.
- `setGain(frequency, gain = 0)` — gain recommended -40 to 40; **throws** `Error('No band found for frequency ...')` for a non-band frequency.
- `getGain(frequency)` — throws for a non-band frequency.
- `reset()` — sets every band gain to 0.

## StereoFilter

`new StereoFilter(pan = 0)` — `StereoPannerNode`.

- `pan` get/set — -1 (full left) to 1 (full right).

## TelephoneFilter

`new TelephoneFilter()` — no parameters. Fixed band-pass built from two 2000 Hz lowpass + two 500 Hz highpass biquads.

## MonoFilter

`new MonoFilter()` — no parameters. Collapses to mono via `ChannelSplitterNode`/`ChannelMergerNode`.

## StreamFilter

`new StreamFilter()` — no parameters. Creates a `MediaStreamAudioDestinationNode` and a `MediaStreamAudioSourceNode`.

- `stream` (readonly) — the `MediaStream`; pair with `MediaRecorder` or `RTCPeerConnection`.
- `destroy()` nulls the stream.

## Notes

- Filters are created against the current library's `AudioContext` at construction (via `getInstance()`). Create them after the library exists (it does on import).
- Reassigning `soundObj.filters` replaces the whole chain; the old nodes should be `destroy()`ed if you want to free them.
- `filtersAll` applies to all output at the context level; per-sound `filters` apply in the per-Sound chain. Order: per-sound filters, then the global `filtersAll` chain.

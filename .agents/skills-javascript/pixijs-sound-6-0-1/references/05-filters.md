# Filters

## Overview

Filters are WebAudio-based audio effects. They are applied as a chain — each filter connects its output to the next filter's input. Filters only work in WebAudio mode; they are silently ignored in legacy HTML5 Audio mode.

## Filter Base Class

```ts
class Filter {
    destination: AudioNode;  // Input node
    source: AudioNode;       // Output node

    constructor(destination: AudioNode, source?: AudioNode);
    connect(destination: AudioNode): void;
    disconnect(): void;
    destroy(): void;
}
```

## Applying Filters

### Per-Sound

```ts
const soundObj = sound.find('music');
soundObj.filters = [
    new filters.ReverbFilter(3, 2),
    new filters.StereoFilter(-0.5),
];
```

### Per-Play

```ts
sound.play('music', {
    filters: [new filters.ReverbFilter(2, 1)],
});
```

### Global

```ts
sound.filtersAll = [new filters.StereoFilter(-1)];
```

### Filter Order

Filters are applied in array order. The first filter receives the raw audio; each subsequent filter receives the output of the previous one.

```ts
// Pan then reverb
sound.filters = [new filters.StereoFilter(-0.5), new filters.ReverbFilter()];

// Reverb then pan (different result)
sound.filters = [new filters.ReverbFilter(), new filters.StereoFilter(-0.5)];
```

## ReverbFilter

Adds reverb effect using a generated impulse response.

```ts
new filters.ReverbFilter(seconds = 3, decay = 2, reverse = false);
```

| Property | Type | Range | Default | Description |
|---|---|---|---|---|
| `seconds` | `number` | 1–50 | 3 | Reverb duration |
| `decay` | `number` | 0–100 | 2 | Decay rate |
| `reverse` | `boolean` | — | `false` | Reverse reverb |

```ts
const reverb = new filters.ReverbFilter(3, 2);
reverb.seconds = 5;
reverb.decay = 5;
reverb.reverse = true;
```

## DistortionFilter

Adds distortion using a WaveShaperNode.

```ts
new filters.DistortionFilter(amount = 0);
```

| Property | Type | Range | Default | Description |
|---|---|---|---|---|
| `amount` | `number` | 0–1 | 0 | Distortion amount |

```ts
const distortion = new filters.DistortionFilter(0.5);
distortion.amount = 0.8;
```

## EqualizerFilter

10-band graphic equalizer using BiquadFilterNodes.

```ts
new filters.EqualizerFilter(f32 = 0, f64 = 0, f125 = 0, f250 = 0, f500 = 0,
    f1k = 0, f2k = 0, f4k = 0, f8k = 0, f16k = 0);
```

### Band Constants

| Constant | Frequency | Type |
|---|---|---|
| `EqualizerFilter.F32` | 32 Hz | lowshelf |
| `EqualizerFilter.F64` | 64 Hz | peaking |
| `EqualizerFilter.F125` | 125 Hz | peaking |
| `EqualizerFilter.F250` | 250 Hz | peaking |
| `EqualizerFilter.F500` | 500 Hz | peaking |
| `EqualizerFilter.F1K` | 1000 Hz | peaking |
| `EqualizerFilter.F2K` | 2000 Hz | peaking |
| `EqualizerFilter.F4K` | 4000 Hz | peaking |
| `EqualizerFilter.F8K` | 8000 Hz | peaking |
| `EqualizerFilter.F16K` | 16000 Hz | highshelf |

### Properties

| Property | Type | Description |
|---|---|---|
| `bands` | `BiquadFilterNode[]` (readonly) | Array of band nodes |
| `bandsMap` | `Record<number, BiquadFilterNode>` (readonly) | Map of frequency to node |

### Methods

```ts
const eq = new filters.EqualizerFilter();

// Set gain by frequency
eq.setGain(EqualizerFilter.F1K, -10);
eq.setGain(EqualizerFilter.F8K, 5);

// Get gain
const gain = eq.getGain(EqualizerFilter.F1K);

// Shorthand properties
eq.f32 = 5;
eq.f1k = -10;
eq.f8k = 3;

// Reset all bands
eq.reset();
```

### Preset Examples

```ts
// Bass boost
const bassBoost = new filters.EqualizerFilter(8, 6, 4, 2, 0, 0, 0, 0, 0, 0);

// Vocal clarity
const vocalClarity = new filters.EqualizerFilter(0, 0, 0, 0, 0, 3, 5, 3, 0, 0);

// Treble boost
const trebleBoost = new filters.EqualizerFilter(0, 0, 0, 0, 0, 0, 0, 2, 5, 8);
```

## StereoFilter

Stereo panning using StereoPannerNode (or PannerNode fallback).

```ts
new filters.StereoFilter(pan = 0);
```

| Property | Type | Range | Default | Description |
|---|---|---|---|---|
| `pan` | `number` | -1 to 1 | 0 | -1 = full left, 1 = full right |

```ts
const stereo = new filters.StereoFilter(0);
stereo.pan = -0.7; // Left bias
```

## TelephoneFilter

Simulates telephone audio with bandpass filtering (500 Hz – 2 kHz).

```ts
new filters.TelephoneFilter();
```

No configurable properties. Uses two cascaded lowpass filters at 2 kHz and two cascaded highpass filters at 500 Hz.

```ts
const telephone = new filters.TelephoneFilter();
soundObj.filters = [telephone];
```

## MonoFilter

Collapses all channels into a single mono channel.

```ts
new filters.MonoFilter();
```

No configurable properties. Uses ChannelSplitterNode and ChannelMergerNode.

```ts
const mono = new filters.MonoFilter();
soundObj.filters = [mono];
```

## StreamFilter

Exports audio output as a `MediaStream` for recording or streaming.

```ts
new filters.StreamFilter();
```

| Property | Type | Description |
|---|---|---|
| `stream` | `MediaStream` (readonly) | The output MediaStream |

```ts
const streamFilter = new filters.StreamFilter();
soundObj.filters = [streamFilter];

// Record the stream
const recorder = new MediaRecorder(streamFilter.stream);
recorder.ondataavailable = (e) => {
    const blob = e.data;
    // Save or upload blob
};
recorder.start();
```

## Filter Cleanup

Always destroy filters when no longer needed to prevent memory leaks:

```ts
// Setting new filters automatically disconnects old ones
soundObj.filters = [newFilter];

// Or explicitly destroy
oldFilter.destroy();

// When removing a sound, its filters are cleaned up
sound.remove('alias');
```

## WebAudio Node Chain

The filter chain connects as:

```
Source → Filter[0].destination → Filter[0].source → Filter[1].destination → ... → Filter[n].source → Destination
```

Custom filters can be created by extending `Filter`:

```ts
class CustomFilter extends Filter {
    private node: AudioNode;

    constructor() {
        const { audioContext } = sound.context;
        this.node = audioContext.createGain();
        super(this.node);
    }

    setGain(value: number) {
        (this.node as GainNode).gain.value = value;
    }
}
```

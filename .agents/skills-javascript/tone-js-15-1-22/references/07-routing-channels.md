# Routing & Channels

## Volume

Gain control in decibels.

```js
const volume = new Tone.Volume(-6).toDestination();
synth.connect(volume);
volume.volume.value = -12;        // set to -12dB
volume.volume.rampTo(0, 0.5);     // ramp to 0dB
volume.mute = true;               // instant mute
```

### Options

| Option | Type | Default | Description |
|---|---|---|---|
| `volume` | Decibels | `0` | Gain in dB |
| `mute` | boolean | `false` | Mute/unmute |

## Panner

Stereo panning (-1 = full left, 1 = full right).

```js
const panner = new Tone.Panner(0.5).toDestination();  // 50% right
synth.connect(panner);
panner.pan.value = -0.5;  // pan left
```

## Panner3D

3D spatial panning with listener positioning.

```js
const panner3D = new Tone.Panner3D({
  x: 0,
  y: 0,
  z: -3,
  model: "HRTF",  // "HRTF" | "equalpower"
}).toDestination();

// Position the listener
const listener = Tone.getListener();
listener.positionX.value = 0;
listener.positionY.value = 0;
listener.positionZ.value = 0;
```

### Options

| Option | Type | Default | Description |
|---|---|---|---|
| `x` | number | `0` | X position |
| `y` | number | `0` | Y position |
| `z` | number | `0` | Z position |
| `model` | string | `"HRTF"` | Panning model |
| `distanceModel` | string | `"inverse"` | Distance model |
| `refDistance` | number | `1` | Reference distance |
| `rolloffFactor` | number | `1` | Rolloff rate |
| `maxDistance` | number | `10000` | Max distance |

## PanVol

Combined panning and volume control.

```js
const panVol = new Tone.PanVol({
  pan: 0,
  volume: 0,
}).toDestination();
```

## Channel

Multi-channel routing (up to 8 channels).

```js
const channel = new Tone.Channel().toDestination();
source.connect(channel);
channel.volume.value = -6;
channel.mute = false;
channel.solo = false;
```

## CrossFade

Crossfade between two inputs.

```js
const crossfade = new Tone.CrossFade(0.5).toDestination();
sourceA.connect(crossfade.A);
sourceB.connect(crossfade.B);
crossfade.fade.value = 0;  // 0 = A, 1 = B, 0.5 = equal
```

## Merge

Merge multiple mono signals into a single stereo output.

```js
const merge = new Tone.Merge(monoA, monoB).toDestination();
```

## Split

Split a stereo signal into two mono outputs.

```js
const [left, right] = Tone.Split(stereoSource);
```

## MidSideSplit / MidSideMerge

Split/merge into mid and side components.

```js
const msSplit = new Tone.MidSideSplit();
stereoSource.connect(msSplit);

// Process mid and side separately
const midProc = new Tone.Filter(2000, "lowpass");
const sideProc = new Tone.Filter(4000, "highpass");
msSplit.mid.connect(midProc);
msSplit.side.connect(sideProc);

const msMerge = new Tone.MidSideMerge().toDestination();
midProc.connect(msMerge.mid);
sideProc.connect(msMerge.side);
```

## MultibandSplit / MultibandCompressor

Split signal into frequency bands for independent processing.

```js
const split = new Tone.MultibandSplit({
  lowMidFrequency: 200,
  midHighFrequency: 2000,
});
source.connect(split);

// Process each band independently
split.low.connect(lowComp);
split.lowMid.connect(lowMidComp);
split.midHigh.connect(midHighComp);
split.high.connect(highComp);
```

## Mono

Downmix stereo to mono.

```js
const mono = new Tone.Mono().toDestination();
stereoSource.connect(mono);
```

## Solo

Solo/mute control — useful for mixing.

```js
const solo = new Tone.Solo(false).toDestination();
synth.connect(solo);
solo.solo = true;  // solo this channel
```

## Recorder

Record audio to a WAV blob.

```js
const recorder = new Tone.Recorder();
synth.connect(recorder);

recorder.start();
setTimeout(() => {
  recorder.stop().then((blob) => {
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    audio.play();
  });
}, 5000);

recorder.save("recording.wav");  // download as file
```

### Methods

```js
recorder.start();
recorder.stop();     // Promise<Blob>
recorder.dispose();
recorder.save(name); // Download WAV file
recorder.clear();    // Clear recorded buffers
```

## Connection API Reference

```js
// Connect two nodes
source.connect(destination);

// Connect in series
source.chain(node1, node2, node3, Tone.getDestination());

// Connect in parallel
source.fan(effect1, effect2, effect3);

// Multiple sources to one destination
Tone.fanIn(source1, source2, source3, destination);

// Connect to speakers
node.toDestination();

// Disconnect
source.disconnect();
source.disconnect(destination);
```

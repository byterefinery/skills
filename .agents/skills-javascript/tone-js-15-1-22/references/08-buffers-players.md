# Buffers & Players

## ToneAudioBuffer

Wrapper around `AudioBuffer` with loading utilities.

```js
// Load from URL
const buffer = new Tone.AudioBuffer();
buffer.load("drum.mp3").then(() => {
  console.log(buffer.sampleRate, buffer.duration, buffer.channels);
});

// From AudioBuffer
const buffer = new Tone.AudioBuffer(audioBuffer);

// From array (create empty buffer)
const buffer = new Tone.AudioBuffer({
  channels: 2,
  duration: 1,
  sampleRate: 44100,
});
```

### Properties

```js
buffer.sampleRate;     // number
buffer.duration;       // number (seconds)
buffer.channels;       // number
buffer.channelData;    // Float32Array[]
buffer.audioBuffer;    // raw AudioBuffer
```

### Static Methods

```js
// Wait for all buffers to load
await Tone.loaded();

// Decode audio data
const buffer = await Tone.context.decodeAudioData(arrayBuffer);

// Get a buffer by URL (cached)
Tone.AudioBuffer.get("drum.mp3");
```

### Loading

```js
// Promise-based
const buf = new Tone.AudioBuffer();
await buf.load("audio.mp3");

// Callback-based
const buf = new Tone.AudioBuffer({
  onload: () => console.log("loaded"),
  onerror: (e) => console.error(e),
});
buf.load("audio.mp3");
```

## ToneAudioBuffers

Collection of named AudioBuffers.

```js
const buffers = new Tone.AudioBuffers({
  kick: "kick.mp3",
  snare: "snare.mp3",
  hihat: "hihat.mp3",
}, "https://tonejs.github.io/audio/drum-samples/");

await Tone.loaded();
console.log(buffers.get("kick"));
```

## Player

Audio file player with start, loop, and stop.

```js
const player = new Tone.Player("drum.mp3").toDestination();
player.autostart = true;  // play when loaded
```

### Constructor

```js
new Tone.Player(url, onload)
new Tone.Player(options)
```

### Options

| Option | Type | Default | Description |
|---|---|---|---|
| `url` | string | — | URL to load |
| `onload` | function | — | Called when loaded |
| `onerror` | function | — | Called on error |
| `autostart` | boolean | `false` | Play on load |
| `loop` | boolean | `false` | Loop playback |
| `loopStart` | Time | `0` | Loop start position |
| `loopEnd` | Time | end | Loop end position |
| `playbackRate` | number | `1` | Playback speed |
| `reverse` | boolean | `false` | Reverse buffer |
| `fadeIn` | Time | `0` | Fade in time |
| `fadeOut` | Time | `0` | Fade out time |

### Properties

```js
player.buffer;           // ToneAudioBuffer (null until loaded)
player.playbackRate = 1.5;
player.loop = true;
player.loopStart = 0;
player.loopEnd = player.buffer.duration;
player.reverse = true;
player.fadeIn = 0.01;
player.fadeOut = 0.01;
player.mute = false;
player.volume.value = -6;
player.state;            // "started" | "stopped"
player.progress;         // 0-1 playback position
```

### Methods

```js
player.start(time, offset);
player.stop(time);
player.dispose();
```

### Syncing to Transport

```js
player.sync();
Tone.getTransport().start();
// Player now starts/stops with the transport
```

## Players

Pool of Player instances for overlapping playback.

```js
const players = new Tone.Players({
  kick: "kick.mp3",
  snare: "snare.mp3",
}, "https://tonejs.github.io/audio/drum-samples/", {
  onload: () => {
    // All loaded, can play
    players.kick.start();
  },
});
```

## GrainPlayer

Granular synthesis player — plays tiny grains from a buffer.

```js
const grain = new Tone.GrainPlayer("audio.mp3", {
  position: 0.5,
  duration: 0.1,
  spread: 0.05,
  playbackRate: 1,
  grains: 4,
  repeat: 0.05,
  repeatSpread: 0.01,
}).toDestination();

grain.start();
grain.stop();
```

### Options

| Option | Type | Default | Description |
|---|---|---|---|
| `position` | NormalRange | `0.5` | Position in buffer (0-1) |
| `duration` | Time | `0.1` | Grain duration |
| `spread` | NormalRange | `0.05` | Random position spread |
| `playbackRate` | number | `1` | Playback speed |
| `grains` | number | `4` | Grains per trigger |
| `repeat` | Time | `0.05` | Repeat interval |
| `repeatSpread` | NormalRange | `0.01` | Repeat timing spread |
| `fadeIn` | Time | `0.01` | Grain fade in |
| `fadeOut` | Time | `0.01` | Grain fade out |

## Sampler

Sample-based instrument with pitch mapping. See [Instruments](02-instruments.md) for full details.

```js
const sampler = new Tone.Sampler({
  urls: {
    A0: "A0.mp3",
    C1: "C1.mp3",
    E1: "E1.mp3",
    A1: "A1.mp3",
    C2: "C2.mp3",
    E2: "E2.mp3",
  },
  baseUrl: "https://tonejs.github.io/audio/salamander/",
  onload: () => {
    sampler.triggerAttackRelease("C3", "4n");
  },
}).toDestination();
```

The sampler automatically repitches samples to play notes between the provided samples, enabling full-range playback from a limited set of recordings.

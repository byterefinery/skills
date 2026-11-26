# Sound Library

## Overview

`SoundLibrary` is the central manager for all audio. The default singleton instance is exported as `sound`. It manages sound registration, playback, global volume/mute/speed, and the audio backend context.

## Constructor

The singleton is already instantiated. Create custom instances only for isolated audio contexts:

```ts
import { SoundLibrary } from '@pixi/sound';

const library = new SoundLibrary();
```

## Adding Sounds

### `add(alias, options)`

Register a sound by alias. Returns the `Sound` object.

```ts
// By URL string
sound.add('explosion', 'assets/explosion.mp3');

// With options object
sound.add('music', {
    url: 'assets/music.mp3',
    volume: 0.8,
    loop: true,
    preload: true,
    autoPlay: true,
    singleInstance: true,
    speed: 1.0,
    loaded(err, soundObj, instance) { /* callback */ },
    complete(soundObj) { /* play complete callback */ },
    sprites: { laser: { start: 0, end: 0.2 } },
});

// From raw buffers
sound.add('tone', audioBuffer);    // ArrayBuffer
sound.add('tone', audioBuffer);    // AudioBuffer
sound.add('tone', audioElement);   // HTMLAudioElement

// Existing Sound object
sound.add('explosion', Sound.from('assets/explosion.mp3'));
```

### `add(map, globalOptions?)`

Add multiple sounds at once. Global options apply to all; per-sound options override.

```ts
sound.add({
    explosion: 'assets/explosion.mp3',
    shoot: 'assets/shoot.mp3',
    music: { url: 'assets/music.mp3', loop: true },
}, { volume: 0.7, preload: true });
```

## Playback

### `play(alias, options?)`

Play a sound by alias. Returns `IMediaInstance` or `Promise<IMediaInstance>`.

```ts
// Simple play
const instance = sound.play('explosion');

// With options
sound.play('explosion', {
    volume: 0.5,
    speed: 1.2,
    loop: true,
    muted: false,
    start: 0,
    end: 3,
    sprite: 'laser',
    filters: [new filters.ReverbFilter()],
    singleInstance: true,
    complete(soundObj) { /* done */ },
    loaded(err, soundObj, instance) { /* loaded */ },
});

// Sprite as second argument
sound.play('sfx', 'laser');

// Callback as second argument
sound.play('explosion', (soundObj) => { console.log('done'); });

// Await if not loaded
const instance = await sound.play('explosion');
```

### `stop(alias)`

Stop all instances of a sound.

```ts
sound.stop('explosion');
```

### `pause(alias)` / `resume(alias)`

Pause or resume all instances of a sound.

```ts
sound.pause('music');
sound.resume('music');
```

## Per-Sound Control

### `volume(alias, volume?)`

Get or set volume for a specific sound.

```ts
sound.volume('explosion', 0.5);  // Set
const vol = sound.volume('explosion'); // Get
```

### `speed(alias, speed?)`

Get or set playback speed for a specific sound.

```ts
sound.speed('explosion', 1.5);  // Set
const spd = sound.speed('explosion'); // Get
```

### `duration(alias)`

Get duration in seconds. Returns 0 if not loaded.

```ts
const dur = sound.duration('explosion');
```

## Global Control

### `volumeAll`

Master volume for all sounds.

```ts
sound.volumeAll = 0.8;
```

### `speedAll`

Master playback speed for all sounds.

```ts
sound.speedAll = 1.0;
```

### `muteAll()` / `unmuteAll()` / `toggleMuteAll()`

```ts
sound.muteAll();
sound.unmuteAll();
const isMuted = sound.toggleMuteAll();
```

### `pauseAll()` / `resumeAll()` / `togglePauseAll()`

```ts
sound.pauseAll();
sound.resumeAll();
const isPaused = sound.togglePauseAll();
```

### `stopAll()`

Stop all playing sounds.

```ts
sound.stopAll();
```

### `filtersAll`

Apply filters to all output (WebAudio only).

```ts
sound.filtersAll = [new filters.StereoFilter(-1)];
```

## Inspection

### `exists(alias, assert?)`

Check if a sound alias exists.

```ts
if (sound.exists('explosion')) { /* ... */ }
sound.exists('explosion', true); // Also console.assert
```

### `find(alias)`

Get the `Sound` object by alias. Asserts if not found.

```ts
const soundObj = sound.find('explosion');
```

### `isPlaying()`

Check if any sound is currently playing.

```ts
if (sound.isPlaying()) { /* ... */ }
```

## Lifecycle

### `remove(alias)`

Remove and destroy a sound.

```ts
sound.remove('explosion');
```

### `removeAll()`

Stop and remove all sounds.

```ts
sound.removeAll();
```

### `close()`

Destroy all sounds and release the AudioContext. Use `init()` to reinitialize.

```ts
sound.close();
```

### `init()`

Reinitialize the sound library. Recreates the AudioContext. Call after `close()`.

```ts
sound.init();
```

## Backend Control

### `useLegacy`

Force HTML5 Audio instead of WebAudio. Must be set before loading any files.

```ts
sound.useLegacy = true;
```

### `supported`

Check if WebAudio is supported.

```ts
if (!sound.supported) {
    console.warn('WebAudio not supported');
}
```

### `disableAutoPause`

Disable auto-pause when window loses focus (WebAudio only). Useful for iframes.

```ts
sound.disableAutoPause = true;
```

### `context`

Access the current media context.

```ts
const ctx = sound.context;
ctx.volume;    // Global volume
ctx.muted;     // Global mute
ctx.paused;    // Global pause
ctx.speed;     // Global speed
ctx.filters;   // Global filters
ctx.audioContext; // Raw AudioContext (WebAudio only)
```

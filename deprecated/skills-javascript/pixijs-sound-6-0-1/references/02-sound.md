# Sound

## Overview

`Sound` represents a single loaded audio clip. It manages multiple playback instances (`IMediaInstance`), sprites, filters, and playback properties. Created via `Sound.from()` or through `sound.add()`.

## Creation

### `Sound.from(source)`

Factory method. Accepts a URL, URL array, raw buffer, or options object.

```ts
// URL string
const sound = Sound.from('assets/explosion.mp3');

// Multiple formats (auto-picks best supported)
const sound = Sound.from(['music.ogg', 'music.mp3']);

// Raw buffer
const sound = Sound.from(audioBuffer);    // ArrayBuffer | AudioBuffer | HTMLAudioElement

// Options object
const sound = Sound.from({
    url: 'assets/music.mp3',
    volume: 0.8,
    speed: 1.0,
    loop: false,
    preload: false,
    autoPlay: false,
    singleInstance: false,
    loaded(err, soundObj, instance) { /* loaded callback */ },
    complete(soundObj) { /* play complete callback */ },
    sprites: {
        intro: { start: 0, end: 5 },
        outro: { start: 55, end: 60 },
    },
});
```

### Options Reference

| Option | Type | Default | Description |
|---|---|---|---|
| `url` | `string \| string[]` | `null` | File path(s). Array for format fallback |
| `source` | `ArrayBuffer \| AudioBuffer \| HTMLAudioElement` | `null` | Raw audio source |
| `volume` | `number` | `1` | Volume 0–1 |
| `speed` | `number` | `1` | Playback rate |
| `loop` | `boolean` | `false` | Loop infinitely |
| `preload` | `boolean` | `false` | Preload on creation |
| `autoPlay` | `boolean` | `false` | Auto-play after load |
| `singleInstance` | `boolean` | `false` | Stop previous instance on new play |
| `loaded` | `LoadedCallback` | `null` | Called when loading finishes |
| `complete` | `CompleteCallback` | `null` | Called when playback finishes |
| `sprites` | `Record<string, SoundSpriteData>` | `{}` | Sprite map |

## Properties

| Property | Type | Description |
|---|---|---|
| `isLoaded` | `boolean` | `true` if buffer is loaded |
| `isPlaying` | `boolean` (readonly) | `true` if any instance is playing |
| `autoPlay` | `boolean` (readonly) | Auto-play after load |
| `singleInstance` | `boolean` | Stop previous instances on play |
| `preload` | `boolean` (readonly) | Preload on creation |
| `url` | `string` (readonly) | Resolved URL |
| `options` | `Options` (readonly) | Constructor options |
| `media` | `IMedia` | Internal media (WebAudioMedia or HTMLAudioMedia) |
| `context` | `IMediaContext` (readonly) | Audio context |
| `paused` | `boolean` | Paused state |
| `speed` | `number` | Playback rate |
| `volume` | `number` | Volume 0–1 |
| `muted` | `boolean` | Muted state |
| `loop` | `boolean` | Loop state |
| `filters` | `Filter[]` | Applied filters (WebAudio only) |
| `isPlayable` | `boolean` (readonly) | `true` if loaded and playable |
| `instances` | `IMediaInstance[]` (readonly) | Currently playing instances |
| `sprites` | `SoundSprites` (readonly) | Sprite map |
| `duration` | `number` (readonly) | Duration in seconds |

## Playback

### `play(options?)` / `play(sprite, callback?)`

Play the sound. Returns `IMediaInstance` or `Promise<IMediaInstance>`.

```ts
// Simple play
const instance = soundObj.play();

// Play options
soundObj.play({
    volume: 0.5,
    speed: 1.2,
    loop: true,
    muted: false,
    start: 1,    // Start time offset in seconds
    end: 5,      // End time in seconds
    sprite: 'laser',
    filters: [new filters.ReverbFilter()],
    singleInstance: true,
    complete(soundObj) { /* done */ },
    loaded(err, soundObj, instance) { /* loaded */ },
});

// Play a sprite by name
soundObj.play('laser');
soundObj.play('laser', (soundObj) => { /* complete */ });

// Callback only
soundObj.play((soundObj) => { console.log('done'); });
```

### Play Options Reference

| Option | Type | Default | Description |
|---|---|---|---|
| `start` | `number` | `0` | Start time offset in seconds |
| `end` | `number` | `null` | End time in seconds |
| `speed` | `number` | Sound's speed | Playback rate override |
| `loop` | `boolean` | Sound's loop | Loop override |
| `volume` | `number` | Sound's volume | Volume override |
| `sprite` | `string` | `null` | Sprite alias to play |
| `muted` | `boolean` | `false` | Mute this instance |
| `filters` | `Filter[]` | `null` | Filters for this play (WebAudio) |
| `complete` | `CompleteCallback` | `null` | Called when done |
| `loaded` | `LoadedCallback` | `null` | Called when loaded |
| `singleInstance` | `boolean` | `false` | Stop previous instances |

### `stop()`

Stop all instances.

```ts
soundObj.stop();
```

### `pause()` / `resume()`

Pause or resume all instances.

```ts
soundObj.pause();
soundObj.resume();
```

## Control

### `volume`

```ts
soundObj.volume = 0.5;
const vol = soundObj.volume;
```

### `speed`

```ts
soundObj.speed = 1.5;
const spd = soundObj.speed;
```

### `muted`

```ts
soundObj.muted = true;
```

### `loop`

```ts
soundObj.loop = true;
```

### `filters`

Apply filters (WebAudio only).

```ts
soundObj.filters = [
    new filters.ReverbFilter(3, 2),
    new filters.StereoFilter(-0.5),
];
```

## Refresh

### `refresh()`

Apply current volume/speed/mute changes to all playing instances.

```ts
soundObj.volume = 0.5;
soundObj.refresh(); // Usually called automatically by setters
```

### `refreshPaused()`

Apply paused state to all instances.

```ts
soundObj.paused = true;
soundObj.refreshPaused();
```

## Sprites

### `addSprites(alias, data)` / `addSprites(dataMap)`

Add one or more sprites.

```ts
// Single sprite
soundObj.addSprites('laser', { start: 0, end: 0.2 });

// Multiple sprites
soundObj.addSprites({
    laser: { start: 0, end: 0.2 },
    explosion: { start: 0.3, end: 0.8 },
});
```

### `removeSprites(alias?)`

Remove a sprite or all sprites.

```ts
soundObj.removeSprites('laser');
soundObj.removeSprites(); // Remove all
```

## Lifecycle

### `autoPlayStart()`

Start auto-play (if `autoPlay: true`).

```ts
const instance = soundObj.autoPlayStart();
```

### `destroy()`

Destroy the sound and all instances. Prefer `sound.remove(alias)` for registered sounds.

```ts
soundObj.destroy();
```

## Event Flow

When `play()` is called:

1. If not loaded, the call is queued and a Promise is returned
2. When loaded, `loaded` callback fires (if provided)
3. An `IMediaInstance` is created from the pool
4. The instance fires `start` event
5. During playback, `progress` events fire
6. On completion, instance fires `end` event
7. The `complete` callback fires (if provided)
8. The instance is removed and pooled for reuse

When `stop()` is called:

1. All instances fire `stop` event
2. Instances are removed and pooled

When `pause()` is called:

1. All instances fire `pause` and `paused` events
2. Playback position is preserved

When `resume()` is called:

1. All instances fire `resumed` event
2. Playback continues from paused position

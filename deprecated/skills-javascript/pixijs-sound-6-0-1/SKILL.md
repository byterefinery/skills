---
name: pixijs-sound-6-0-1
description: >
  PixiJS Sound v6.0.1 — WebAudio API playback library with filters for PixiJS v8. Use when working with
  @pixi/sound, adding audio to PixiJS projects, playing sound effects, background music, audio sprites,
  or applying audio filters (reverb, distortion, equalizer, stereo pan, telephone, mono, stream).
  Covers SoundLibrary singleton, Sound/IMediaInstance lifecycle, sprite regions, per-instance control,
  global volume/mute/pause, PIXI.Assets integration, and WebAudio vs HTMLAudio legacy fallback.
metadata:
  tags:
    - javascript
    - audio
    - web-audio
    - pixi
    - game-dev
    - sound-effects
---

# pixijs-sound 6.0.1

PixiJS Sound is a WebAudio API playback library that integrates with PixiJS v8. It provides a singleton `sound` instance (`SoundLibrary`) for managing audio, a `Sound` class for individual audio clips, and a `SoundSprite` system for playing segments of longer files. Dynamic audio filters (reverb, distortion, equalizer, stereo panning, telephone, mono, stream export) are applied via WebAudio nodes. Falls back to HTML5 Audio when WebAudio is unsupported.

## Overview

### Architecture

- **`SoundLibrary`** — Singleton instance (`sound`) managing all sounds. Add, play, stop, pause, mute, volume, speed, and global filters.
- **`Sound`** — Represents one audio clip. Holds multiple `IMediaInstance` objects (layered playback). Controls volume, speed, loop, mute, filters, and sprites.
- **`IMediaInstance`** — A single playback instance returned by `play()`. Has its own volume, speed, muted, loop, progress, and events (`end`, `start`, `stop`, `progress`, `pause`).
- **`SoundSprite`** — A named segment (`start`, `end`, optional `speed`) within a `Sound`. Like an image spritesheet for audio.
- **Filters** — WebAudio-based effects: `ReverbFilter`, `DistortionFilter`, `EqualizerFilter`, `StereoFilter`, `TelephoneFilter`, `MonoFilter`, `StreamFilter`. Applied per-Sound or globally via `sound.filtersAll`.
- **Backends** — WebAudio (default, supports filters) or HTML5 Audio (legacy fallback, no filters). Auto-detected; force legacy with `sound.useLegacy = true`.

### Quick Start

```ts
import { sound, filters } from '@pixi/sound';

// Add a sound
sound.add('explosion', 'assets/explosion.mp3');

// Play it
sound.play('explosion');

// Play with options
sound.play('explosion', { volume: 0.5, speed: 1.2 });

// With a filter
sound.play('music', {
    filters: [new filters.ReverbFilter(3, 2)],
});
```

### PIXI.Assets Integration

Sounds load automatically through `PIXI.Assets` — no manual `sound.add()` needed:

```ts
import { Assets } from 'pixi.js';
import '@pixi/sound';

// Loads and auto-registers with sound library
const soundObj = await Assets.load('assets/explosion.mp3');

// Play by alias (basename without extension)
sound.play('explosion');
```

The asset alias defaults to the filename without extension. Override with `Assets.add({ alias: ['my-alias'], src: 'file.mp3' })`.

### Version Compatibility

| PixiJS | PixiJS Sound |
|---|---|
| v5.x – v6.x | v4.x |
| v7.x | v5.x |
| v8.x | v6.x |

## Usage

### SoundLibrary (sound singleton)

```ts
import { sound } from '@pixi/sound';

// Add a sound by URL
sound.add('explosion', 'assets/explosion.mp3');

// Add with options
sound.add('music', {
    url: 'assets/music.mp3',
    loop: true,
    volume: 0.8,
    preload: true,
    loaded(err, soundObj) {
        if (!err) soundObj.play();
    },
});

// Add multiple at once
sound.add({
    explosion: 'assets/explosion.mp3',
    shoot: 'assets/shoot.mp3',
}, { volume: 0.7 });

// Add from raw buffers
sound.add('tone', audioBuffer); // ArrayBuffer, AudioBuffer, HTMLAudioElement

// Play
const instance = sound.play('explosion');
sound.play('explosion', { volume: 0.5, speed: 1.5, loop: true });
sound.play('explosion', (soundObj) => { console.log('done'); });

// Sprite playback
sound.play('sfx', 'laser'); // sprite alias as second arg

// Control
sound.stop('explosion');
sound.pause('explosion');
sound.resume('explosion');
sound.volume('explosion', 0.5);  // set
const vol = sound.volume('explosion'); // get
sound.speed('explosion', 1.5);
const dur = sound.duration('explosion'); // seconds

// Global control
sound.volumeAll = 0.8;
sound.speedAll = 1.0;
sound.muteAll();
sound.unmuteAll();
sound.toggleMuteAll();
sound.pauseAll();
sound.resumeAll();
sound.togglePauseAll();
sound.stopAll();

// Check existence
sound.exists('explosion');

// Check if any sound is playing
sound.isPlaying();

// Find a Sound object
const s = sound.find('explosion');

// Remove
sound.remove('explosion');

// Remove all
sound.removeAll();

// Close (release AudioContext)
sound.close();

// Reinitialize after close
sound.init();
```

### Sound Object

```ts
import { Sound } from '@pixi/sound';

// Create from URL
const soundObj = Sound.from('assets/explosion.mp3');

// Create with options
const soundObj = Sound.from({
    url: 'assets/music.mp3',
    volume: 0.8,
    speed: 1.0,
    loop: true,
    preload: true,
    autoPlay: true,
    singleInstance: true,  // Stop previous instance before playing new one
    loaded(err, soundObj) { /* loaded callback */ },
    complete(soundObj) { /* play complete callback */ },
});

// Multiple format fallback
const soundObj = Sound.from(['music.ogg', 'music.mp3']);

// From raw buffer
const soundObj = Sound.from(audioBuffer);

// Properties
soundObj.isLoaded;     // boolean
soundObj.isPlaying;    // boolean (readonly)
soundObj.paused;       // boolean
soundObj.volume;       // 0-1
soundObj.speed;        // playback rate
soundObj.muted;        // boolean
soundObj.loop;         // boolean
soundObj.duration;     // seconds
soundObj.filters;      // Filter[]
soundObj.instances;    // IMediaInstance[] (currently playing)
soundObj.sprites;      // SoundSprites map

// Methods
soundObj.play(); // Returns IMediaInstance | Promise<IMediaInstance>
soundObj.play({ volume: 0.5, speed: 1.2, loop: true, start: 1, end: 3 });
soundObj.play('sprite-name'); // Play a sprite
soundObj.play('sprite-name', (soundObj) => { /* complete */ });
soundObj.stop();
soundObj.pause();
soundObj.resume();
soundObj.refresh(); // Apply volume/speed/mute changes to all instances
soundObj.destroy();

// Filters (WebAudio only)
import { filters } from '@pixi/sound';
soundObj.filters = [
    new filters.ReverbFilter(3, 2),
    new filters.StereoFilter(-0.5),
];

// Sprites
soundObj.addSprites({
    laser: { start: 0, end: 0.2 },
    explosion: { start: 0.3, end: 0.8 },
});
soundObj.addSprites('ping', { start: 1, end: 1.5, speed: 1.2 });
soundObj.removeSprites('laser');
soundObj.removeSprites(); // Remove all
```

### IMediaInstance (playback instance)

```ts
const instance = sound.play('explosion');

// Properties
instance.id;        // Auto-incrementing number
instance.progress;  // 0 to 1 (readonly)
instance.paused;    // boolean
instance.volume;    // 0-1
instance.speed;     // playback rate
instance.loop;      // boolean
instance.muted;     // boolean

// Methods
instance.stop();
instance.set('volume', 0.5);
instance.set('speed', 0.8);

// Events
instance.on('end', () => { console.log('finished'); });
instance.on('start', () => { console.log('started'); });
instance.on('stop', () => { console.log('stopped'); });
instance.on('progress', (progress, duration) => {
    console.log(progress, duration);
});
instance.on('pause', (paused) => {});
instance.on('paused', () => {});
instance.on('resumed', () => {});

// One-shot
instance.once('end', () => { console.log('done'); });

// Remove listener
instance.off('progress', handler);
```

### Sound Sprites

```ts
// Define sprites at creation
sound.add('sfx', {
    url: 'assets/sfx-pack.mp3',
    sprites: {
        laser:     { start: 0,    end: 0.2 },
        explosion: { start: 0.3,  end: 0.8 },
        music:     { start: 1,    end: 10, speed: 0.8 },
    },
});

// Or add after creation
const sfx = sound.find('sfx');
sfx.addSprites({
    ping: { start: 11, end: 12 },
    boop: { start: 13, end: 13.5 },
});

// Play a sprite
sound.play('sfx', 'laser');
sound.play('sfx', { sprite: 'explosion', volume: 0.8 });

// Access sprite object
const sprite = sfx.sprites['laser'];
sprite.start;    // 0
sprite.end;      // 0.2
sprite.duration; // 0.2
sprite.speed;    // undefined (uses parent speed)
sprite.play();   // Play directly
```

### Filters

```ts
import { sound, filters } from '@pixi/sound';

// Per-sound filters
sound.find('music').filters = [
    new filters.ReverbFilter(3, 2),       // seconds, decay
    new filters.StereoFilter(-0.5),        // pan: -1 (left) to 1 (right)
    new filters.EqualizerFilter(),         // 10-band EQ
    new filters.DistortionFilter(0.5),     // amount: 0 to 1
    new filters.TelephoneFilter(),         // telephone effect
    new filters.MonoFilter(),              // collapse to mono
    new filters.StreamFilter(),            // export as MediaStream
];

// Global filters (applied to all output)
sound.filtersAll = [new filters.StereoFilter(-1)];

// Play with inline filters
sound.play('music', {
    filters: [new filters.ReverbFilter(2, 1)],
});

// Equalizer bands
const eq = new filters.EqualizerFilter();
eq.f32 = 5;    // 32 Hz gain
eq.f1k = -10;  // 1 kHz gain
eq.f8k = 3;    // 8 kHz gain
eq.reset();    // Reset all to 0

// Reverb
const reverb = new filters.ReverbFilter(3, 2, false);
reverb.seconds = 5;   // 1-50
reverb.decay = 5;     // 0-100
reverb.reverse = true;

// Distortion
const distortion = new filters.DistortionFilter(0.5);
distortion.amount = 0.8;

// Stereo
const stereo = new filters.StereoFilter(0);
stereo.pan = 0.7;

// Stream (for recording)
const stream = new filters.StreamFilter();
const mediaStream = stream.stream;
```

### Utilities

```ts
import { utils } from '@pixi/sound';

// Play a sound once (auto-removes after completion)
utils.playOnce('assets/one-shot.mp3', (err) => {
    if (!err) console.log('played and removed');
});

// Generate a sine tone (WebAudio only)
const tone = utils.sineTone(440, 1); // 440 Hz, 1 second
sound.add('tone', tone);
sound.play('tone');

// Render waveform as TextureSource (WebAudio only)
const texture = utils.render(sound.find('music'), {
    width: 512,
    height: 128,
    fill: '#ffffff',
});

// Check format support
utils.supported; // { mp3: true, ogg: true, wav: true, ... }
utils.extensions; // ['ogg', 'oga', 'opus', 'm4a', 'mp3', 'mpeg', 'wav', ...]
```

### Legacy Mode

```ts
import { sound } from '@pixi/sound';

// Force HTML5 Audio (must be before loading any files)
sound.useLegacy = true;

// Disable auto-pause on window blur (WebAudio only)
sound.disableAutoPause = true;

// Check WebAudio support
sound.supported; // boolean
```

## Gotchas

- **WebAudio required for filters** — All filters (`ReverbFilter`, `EqualizerFilter`, etc.) only work with WebAudio. In legacy HTML5 Audio mode, filters are silently ignored.

- **AudioContext requires user gesture** — Browsers block AudioContext from starting without a user interaction (click, touch). PixiJS Sound auto-resumes on first `play()`, but if playback fails, wrap initial play in a click/touch handler or listen for the `resume` event.

- **`play()` returns `IMediaInstance` or `Promise`** — If the sound is already loaded, `play()` returns the instance immediately. If not yet loaded, it returns a Promise that resolves to the instance. Handle both cases or `await` the result.

- **`Sound.volume` affects all instances** — Setting `soundObj.volume = 0.5` changes volume for all current and future instances. Use `instance.set('volume', 0.5)` for per-instance control.

- **`singleInstance` stops previous plays** — When `singleInstance: true` (on Sound or in play options), playing a new instance stops all existing instances of that sound. Useful for UI sounds that shouldn't overlap.

- **Sprite times are absolute, not relative** — Sprite `start` and `end` are absolute times in seconds within the parent audio file, not offsets from each other.

- **`Sound.from()` doesn't auto-register** — `Sound.from('url')` creates a Sound but doesn't add it to the library. Use `sound.add('alias', url)` or `sound.add('alias', Sound.from(url))` to register it.

- **PIXI.Assets auto-registers sounds** — When using `Assets.load()`, the sound is automatically added to the library with an alias derived from the filename (basename without extension). No need to call `sound.add()` separately.

- **`sound.close()` destroys AudioContext** — After `close()`, all sounds are removed and the AudioContext is released. Call `sound.init()` to reinitialize.

- **`utils.sineTone()` and `utils.render()` are WebAudio-only** — These utilities create/operate on AudioBuffers and return empty results in legacy mode.

- **`utils.playOnce()` auto-removes** — The sound is removed from the library after playback completes (both on success and error). The returned alias is only valid during playback.

- **`sound.duration()` returns 0 until loaded** — Duration is only available after the sound buffer is decoded. Check `soundObj.isLoaded` first or wait for the `loaded` callback.

- **Multiple format URLs** — When passing an array `['file.ogg', 'file.mp3']`, the library picks the best supported format. Extension preference order: ogg > oga > opus > m4a > mp3 > mpeg > wav > aiff > wma > mid > caf.

- **`sound.find()` asserts on missing** — `sound.find('alias')` calls `console.assert` if the alias doesn't exist. Use `sound.exists('alias')` first in production code.

- **`sound.isPlaying()` checks any sound** — Returns `true` if *any* registered sound is playing, not a specific one. Check `sound.find('alias').isPlaying` for a specific sound.

- **Filters chain order matters** — Filters are applied in array order. `[StereoFilter, ReverbFilter]` pans then reverbs; `[ReverbFilter, StereoFilter]` reverbs then pans — different results.

- **`EqualizerFilter` uses fixed bands** — 10 bands at 32, 64, 125, 250, 500, 1k, 2k, 4k, 8k, 16k Hz. Custom frequencies are not supported; use the `F*` constants or `setGain(frequency, gain)`.

- **`StreamFilter.stream` for recording** — The `StreamFilter` creates a `MediaStream` from the audio output. Use with `MediaRecorder` or `RTCPeerConnection`. Remember to `destroy()` the filter when done.

- **Instance pooling** — Finished `IMediaInstance` objects are pooled and reused. Don't hold references to instances after `end` or `stop` events fire.

- **`soundAsset` extension auto-registers** — Importing `@pixi/sound` registers the `soundAsset` extension with PixiJS's extension system. It hooks into `PIXI.Assets` as a loader parser.

## References

- [01-sound-library](references/01-sound-library.md) — SoundLibrary singleton, add/play/stop/pause/volume/speed/mute, global control, lifecycle
- [02-sound](references/02-sound.md) — Sound class, creation options, play options, instance management, properties, methods
- [03-media-instance](references/03-media-instance.md) — IMediaInstance interface, events, progress tracking, per-instance control
- [04-sprites](references/04-sprites.md) — SoundSprite, sprite data, sprite map, playing sprites, adding/removing sprites
- [05-filters](references/05-filters.md) — Filter base, ReverbFilter, DistortionFilter, EqualizerFilter, StereoFilter, TelephoneFilter, MonoFilter, StreamFilter
- [06-assets](references/06-assets.md) — PIXI.Assets integration, soundAsset extension, loading, unloading, alias resolution
- [07-utils](references/07-utils.md) — playOnce, sineTone, render, supported formats, validateFormats
- [08-backends](references/08-backends.md) — WebAudio vs HTMLAudio, legacy mode, context management, compatibility

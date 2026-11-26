---
name: pixijs-sound-6-0-3
description: >
  PixiJS Sound v6.0.3 — WebAudio API playback library with filters for PixiJS v8. Use when working with
  @pixi/sound, adding audio to PixiJS projects, playing sound effects, background music, audio sprites,
  or applying audio filters (reverb, distortion, equalizer, stereo pan, telephone, mono, stream).
  Covers SoundLibrary singleton, Sound and IMediaInstance lifecycle, sprite regions with per-sprite
  speed and loop, global volume/mute/pause, PIXI.Assets integration, and WebAudio vs HTMLAudio fallback.
metadata:
  tags:
    - javascript
    - audio
    - web-audio
    - pixi
    - game-dev
    - sound-effects
---

# pixijs-sound 6.0.3

PixiJS Sound is a WebAudio API playback library for PixiJS v8 (peer dependency `pixi.js` ^8.0.0). A singleton `sound` (`SoundLibrary`) manages audio; `Sound` wraps one clip; `SoundSprite` marks named segments; filters are WebAudio nodes. Falls back to HTML5 Audio when WebAudio is unsupported or `useLegacy` is set. Install: `npm i @pixi/sound --save`.

## Overview

### Architecture

- **`SoundLibrary`** (`sound`) — singleton managing all sounds: add, play, stop, pause, mute, volume, speed, global filters. Browser bundle exposes it as the `PIXI.sound` global.
- **`Sound`** — one clip holding multiple `IMediaInstance`s (layered playback); volume/speed/loop/mute/filters/sprites. `Sound.from()` does **not** register it in the library.
- **`IMediaInstance`** — one playback from `play()`; own volume/speed/muted/loop/progress and events (`end`, `start`, `stop`, `progress`, `pause`, `paused`, `resumed`). Pooled; don't hold references after `end`/`stop`.
- **`SoundSprite`** — named segment (`start`, `end`, optional `speed`, optional `loop`).
- **Filters** — WebAudio-only: `ReverbFilter`, `DistortionFilter`, `EqualizerFilter`, `StereoFilter`, `TelephoneFilter`, `MonoFilter`, `StreamFilter`.
- **Backends** — WebAudio (default, filters) or HTML5 Audio (legacy, no filters); `sound.supported` reports WebAudio availability.

### Quick Start

```ts
import { sound, Sound, filters } from '@pixi/sound';

sound.add('explosion', 'assets/explosion.mp3');
sound.play('explosion');                      // IMediaInstance | Promise<...>
sound.play('explosion', { volume: 0.5, speed: 1.2 });

const mySound = Sound.from('path/to/file.mp3');  // not registered in the library
mySound.play();
```

Named exports (`Sound`, `filters`, `utils`, `SoundSprite`, …) are not properties of the `sound` object in ESM/CJS — import them directly; in the browser bundle they are also on `PIXI.sound` (`PIXI.sound.Sound`, `PIXI.sound.filters`).

### PIXI.Assets Integration

Importing `@pixi/sound` registers a loader with `PIXI.Assets`: loaded sounds are auto-added to the library under each of their aliases (plus the basename for direct URL loads). Any option except `url`/`preload` — including `sprites` — goes in the asset's `data`. Works with `Assets.add`, `Assets.addBundle`, and manifests:

```ts
Assets.add({
    alias: 'sfx',
    src: 'path/to/sfx.{ogg,mp3}',
    data: { volume: 0.5, sprites: { coin: { start: 0, end: 0.4 } } },
});
await Assets.load('sfx');
sound.play('sfx', 'coin');
```

| PixiJS | PixiJS Sound |
|---|---|
| v5.x – v6.x | v4.x |
| v7.x | v5.x |
| v8.x | v6.x |

## Usage

### SoundLibrary

```ts
// Add: url | Options | ArrayBuffer | AudioBuffer | HTMLAudioElement | Sound instance
sound.add('music', { url: 'assets/music.mp3', loop: true, volume: 0.8, preload: true });
sound.add('tone', mySound);                        // register an existing Sound
sound.add({ explosion: 'a.mp3', shoot: 'b.mp3' }, { volume: 0.7 }); // map form; overrides per-sound options

sound.play('explosion', { volume: 0.5, loop: true });
sound.play('sfx', 'laser');                        // sprite alias as second arg
sound.stop('explosion'); sound.pause('explosion'); sound.resume('explosion');
sound.volume('explosion', 0.5);  sound.volume('explosion'); // get/set
sound.speed('explosion', 1.5);
sound.duration('explosion');    // seconds; NaN until loaded

// Global
sound.volumeAll = 0.8;  sound.speedAll = 1.0;
sound.muteAll(); sound.unmuteAll(); sound.toggleMuteAll();      // toggle returns boolean
sound.pauseAll(); sound.resumeAll(); sound.togglePauseAll();
sound.stopAll();      // stops but keeps sounds registered

// Lookup / lifecycle
sound.exists('a'); sound.isPlaying();             // isPlaying = ANY sound
const s = sound.find('a');                        // console.asserts if missing
sound.remove('a');        // removes sound AND all aliases referencing it
sound.removeAll();        // destroys everything — cannot be reused
sound.close(); sound.init(); // close releases contexts; init recreates (e.g. after hardware failure)
```

### Sound and IMediaInstance

```ts
const s = Sound.from({
    url: 'music.mp3',          // or ['a.ogg', 'b.mp3'] (best supported format) or buffer
    volume: 0.8, speed: 1.0, loop: false,
    preload: true,             // autoPlay: true implies preload
    singleInstance: true,      // stop previous instances on play
    loaded(err, soundObj, instance) {},  // once; err first; WebAudio err has file + cause
    complete(soundObj) {},
    sprites: { laser: { start: 0, end: 0.2, loop: true } },
});

s.isLoaded; s.isPlaying; s.isPlayable; s.paused; s.volume; s.speed; s.muted; s.loop;
s.duration;   // NaN until loaded / on failure / after destroy()
s.filters = [new filters.ReverbFilter(3, 2)];     // WebAudio only
s.instances; s.sprites; s.context;
s.play('laser'); s.stop(); s.pause(); s.resume();
s.addSprites('ping', { start: 11, end: 12 }); s.removeSprites('laser');
s.destroy();

const inst = sound.play('explosion');   // IMediaInstance | Promise
inst.id; inst.progress; inst.paused; inst.volume; inst.speed; inst.loop; inst.muted;
inst.stop();
inst.set('volume', 0.5);               // name: speed|volume|muted|loop|paused
inst.on('progress', (progress, duration) => {});
inst.once('end', () => {}); inst.off('progress', handler);
```

### Filters (WebAudio only)

```ts
sound.find('music').filters = [
    new filters.ReverbFilter(3, 2),       // seconds (1-50), decay (0-100), reverse
    new filters.StereoFilter(-0.5),       // pan -1..1
    new filters.EqualizerFilter(),        // 10 fixed bands 32Hz-16k
    new filters.DistortionFilter(0.5),    // amount 0-1
    new filters.TelephoneFilter(),        // fixed band-pass
    new filters.MonoFilter(),             // collapse to mono
    new filters.StreamFilter(),           // .stream → MediaStream
];
sound.filtersAll = [new filters.StereoFilter(-1)];   // global, all output
sound.play('music', { filters: [new filters.ReverbFilter(2, 1)] });

const eq = new filters.EqualizerFilter();
eq.f32 = 5; eq.f1k = -10;                 // band getters/setters (f32..f16k)
eq.setGain(1000, 6); eq.getGain(1000); eq.reset();  // gain ~ -40..40; throws off-band
new filters.ReverbFilter(3).seconds = 5; new filters.DistortionFilter().amount = 0.8;
```

### Utilities

```ts
import { utils } from '@pixi/sound';

const alias = utils.playOnce('a.mp3', (err) => {});  // auto-removed on complete or error
const tone = utils.sineTone(440, 1);                 // returns a Sound (WebAudio only)
sound.add('tone', tone);
const tex = utils.render(sound.find('music'), { width: 512, height: 128, fill: '#ccc' }); // TextureSource

utils.supported;   // { mp3: true, ... }
utils.extensions;  // order: ogg, oga, opus, m4a, mp3, mpeg, wav, aiff, wma, mid, caf
utils.mimes;       // ['audio/mpeg', 'audio/ogg']
utils.validateFormats({ caf: 'audio/x-caf; codecs="flac"' });
```

### Legacy Mode and Autoplay

```ts
sound.useLegacy = true;        // HTML5 Audio; before loading any files; no filters
sound.disableAutoPause = true; // WebAudio: don't auto-pause on window blur

// iOS silent switch mutes WebAudio (iOS 17+):
if ('audioSession' in navigator) navigator.audioSession.type = 'playback';
```

The `AudioContext` is created on import and starts suspended (Chrome's "was not allowed to start" log is expected). Document-level `mousedown`/`touchstart`/`touchend` listeners unlock it, so a "click to start" screen suffices. For keyboard-first apps, resume yourself:

```ts
document.addEventListener('keydown', () => {
    if (!sound.context.paused) sound.context.audioContext.resume();
});
```

## Gotchas

- **`Sound.from()` doesn't register in the library** — `stopAll()`/`removeAll()`/`isPlaying()` skip it until `sound.add('alias', mySound)` (which accepts a `Sound` instance). Global volume/speed/mute/pause/filters still apply.
- **`play()` returns instance or Promise** — Promise while loading; each `play()` call made before load queues and starts its **own** instance; the promise rejects if loading fails.
- **`duration` is `NaN`, not 0, until known** — before load, on load failure, or after `destroy()`. Check `isPlayable`, not just `isLoaded`.
- **Filters are WebAudio-only** — in legacy mode the context's `filters`/`audioContext` accessors warn and return `null`; `filtersAll` is a no-op; filter constructors create `null` nodes.
- **Sprite `end` must be after `start`** (asserted); times are absolute seconds in the parent file. Sprite speed: explicit play `speed` > sprite `speed` > 1, and the sound's `speed` multiplies on top. `loop` is `sprite.loop || playOptions.loop`.
- **`useLegacy` must be set before loading any files** — it switches the active context.
- **Duplicate aliases assert** — `add()` on an existing alias and `find()` on a missing one fire `console.assert`; use `exists()` first.
- **Multi-format URL arrays pick by extension order** (ogg > oga > opus > m4a > mp3 > mpeg > wav > aiff > wma > mid > caf), not array order; throws `Error('No supported file type found')` if none supported.
- **PIXI.Assets auto-registers under every alias** — don't also call `sound.add()` for the same file (duplicate assert). Asset `data` = Options except `url`/`preload`.
- **`removeAll()`/`close()` are destructive** — destroyed sounds cannot be reused; `close()` nulls contexts, then call `init()`.
- **iOS silent switch mutes WebAudio** — use `navigator.audioSession.type = 'playback'` (iOS 17+) or `useLegacy`. A `'playback'` session can pause other apps' audio.
- **Instance pooling** — finished instances are recycled; the `stop` event docs say "Don't use after this is called." Don't cache instance references.
- **`loaded(err, sound, instance)`** — once, even if `play()` was called while loading; the `instance` arg is the auto-played instance. No callback → errors log to console.
- **`sound.isPlaying()` is global** — for one sound use `sound.find('alias').isPlaying`.
- **`singleInstance`** (Options or play option) stops existing instances — use for UI sounds and non-overlapping music loops.
- **Filter array order = signal order** — reorder changes the result.
- **`EqualizerFilter` fixed bands only** — `setGain`/`getGain` throw for off-band frequencies; band 1 is lowshelf, band 10 highshelf, rest peaking.
- **Deprecated `offset` play option** — still maps to `start`; use `start`.
- **`utils.sineTone()` returns a `Sound`** (not a buffer); WebAudio-only, empty Sound in legacy. `utils.render()` needs a loaded buffer (asserts) and returns an empty canvas source in legacy.
- **`utils.playOnce()` auto-removes** on complete *and* load error; the returned alias is only valid during playback.

## References

- [01-sound-library](references/01-sound-library.md) — SoundLibrary singleton, add overloads, all members, global control, lifecycle
- [02-sound](references/02-sound.md) — Sound class, Options/PlayOptions, load queueing, sprite resolution, properties, methods
- [03-media-instance](references/03-media-instance.md) — IMediaInstance, set(), events, pooling
- [04-sprites](references/04-sprites.md) — SoundSprite, sprite data (start/end/speed/loop), play resolution, add/remove
- [05-filters](references/05-filters.md) — Filter base, all seven filters with parameters, filtersAll, chaining order
- [06-assets](references/06-assets.md) — PIXI.Assets integration, soundAsset extension, aliases, asset data, unload
- [07-utils](references/07-utils.md) — playOnce, sineTone, render, supported formats, extensions order, validateFormats
- [08-backends](references/08-backends.md) — WebAudio vs HTMLAudio, legacy mode, autoplay unlock, iOS silent mode, close/init

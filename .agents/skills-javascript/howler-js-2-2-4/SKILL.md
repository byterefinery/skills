---
name: howler-js-2-2-4
description: howler.js 2.2.4 — audio library for the modern web. Defaults to Web Audio API with HTML5 Audio fallback. Covers Howl/Howler API, sound sprites, spatial/stereo panning, fade/rate/seek control, event system, mobile audio unlocking, and streaming. Use when working with howler.js v2.2.x, building audio players, game sound effects, radio/streaming audio, or 3D spatial sound.
metadata:
  tags:
    - javascript
    - audio
    - web-audio
    - html5-audio
---

# howler-js 2.2.4

howler.js is a JavaScript audio library that defaults to the Web Audio API and falls back to HTML5 Audio. It provides a unified API for playing, controlling, and managing audio across all browsers. The spatial plugin adds stereo panning and 3D positional audio.

## Overview

- **Package**: `howler@2.2.4` (UMD — works with script tags, AMD, CommonJS, ES modules)
- **Backends**: Web Audio API (default, best performance) → HTML5 Audio (fallback or forced via `html5: true`)
- **Core exports**: `Howler` (global controller), `Howl` (sound group constructor)
- **Spatial plugin**: bundled in default dist; separate `howler.spatial` for core-only builds
- **Distribution files**:
  - `howler.js` — full bundle (core + spatial)
  - `howler.core.js` — core only (no spatial/stereo)
  - `howler.spatial.js` — spatial plugin (requires core)

### Quick Start

```js
import { Howl, Howler } from 'howler';

const sound = new Howl({
  src: ['sound.webm', 'sound.mp3'],
  volume: 0.8,
  onend: () => console.log('done'),
});

sound.play();
```

### Sound Sprites

Define named regions (offset, duration in ms) inside a single audio file:

```js
const sfx = new Howl({
  src: ['sfx.webm', 'sfx.mp3'],
  sprite: {
    laser:  [0,    300, false],
    explosion: [400, 1000, false],
    music:  [1500, 30000, true],  // loops
  },
});

sfx.play('laser');
```

### Controlling Individual Sounds

`play()` returns a sound ID. Pass it to any method to target that instance:

```js
const id1 = sound.play();
const id2 = sound.play();

sound.fade(1, 0, 1000, id1);  // fade out first
sound.rate(1.5, id2);          // speed up second
sound.pause(id1);
```

### Streaming / Live Audio

Force HTML5 Audio for large files or live streams — Web Audio must decode the entire buffer first:

```js
const stream = new Howl({
  src: ['live-stream.mp3'],
  html5: true,
});
```

### Spatial Audio

```js
const spatial = new Howl({
  src: ['ambient.webm', 'ambient.mp3'],
  pos: [10, 0, -5],       // 3D position
  // or stereo pan:
  stereo: -0.5,            // left bias
});

// Move listener
Howler.pos(0, 0, 0);
```

## Usage

### Constructor Options

| Option | Type | Default | Description |
|---|---|---|---|
| `src` | `Array\|String` | *(required)* | Audio file URLs or base64 data URIs, in preference order |
| `format` | `Array` | `[]` | Explicit formats when extension detection fails |
| `volume` | `Number` | `1.0` | Volume 0.0–1.0 |
| `html5` | `Boolean` | `false` | Force HTML5 Audio (needed for streaming) |
| `loop` | `Boolean` | `false` | Loop forever |
| `preload` | `Boolean\|String` | `true` | `true`, `'metadata'`, or `false` |
| `autoplay` | `Boolean` | `false` | Auto-play on load |
| `mute` | `Boolean` | `false` | Start muted |
| `rate` | `Number` | `1.0` | Playback rate (0.5–4.0) |
| `pool` | `Number` | `5` | Inactive sound pool size |
| `sprite` | `Object` | `{}` | Sound sprite map |
| `xhr` | `Object` | `{}` | XHR config: `method`, `headers`, `withCredentials` |
| `pos` | `Array` | `null` | 3D position `[x, y, z]` (spatial plugin) |
| `stereo` | `Number` | `null` | Stereo pan -1.0 to 1.0 (spatial plugin) |
| `orientation` | `Array` | `[1,0,0]` | Source direction (spatial plugin) |

### Howl Methods

- **`play([sprite\|id])`** — Start playback. Returns sound ID.
- **`pause([id])`** — Pause, preserving seek position.
- **`stop([id])`** — Stop and reset to beginning.
- **`mute([muted], [id])`** — Mute/unmute.
- **`volume([vol], [id])`** — Get/set volume (0.0–1.0).
- **`fade(from, to, len, [id])`** — Fade between volumes over `len` ms.
- **`rate([rate], [id])`** — Get/set playback rate (0.5–4.0).
- **`seek([seconds], [id])`** — Get/set playback position in seconds.
- **`loop([bool], [id])`** — Get/set looping.
- **`playing([id])`** — Check if playing (Boolean).
- **`duration([id])`** — Get duration in seconds (0 until loaded).
- **`state()`** — Returns `'unloaded'`, `'loading'`, or `'loaded'`.
- **`on(event, fn, [id])`** — Listen for events.
- **`once(event, fn, [id])`** — One-shot event listener.
- **`off(event, [fn], [id])`** — Remove listener(s).
- **`load()`** — Manually trigger load (when `preload: false`).
- **`unload()`** — Destroy and free resources.

### Spatial Methods (per Howl)

- **`stereo(pan, [id])`** — Stereo pan -1.0 (left) to 1.0 (right).
- **`pos(x, y, z, [id])`** — 3D position relative to listener.
- **`orientation(x, y, z, [id])`** — Source direction vector.
- **`pannerAttr(o, [id])`** — Panner config: `coneInnerAngle`, `coneOuterAngle`, `coneOuterGain`, `distanceModel`, `maxDistance`, `refDistance`, `rolloffFactor`, `panningModel`.

### Global (Howler)

- **`Howler.volume([vol])`** — Global master volume.
- **`Howler.mute(muted)`** — Mute all sounds.
- **`Howler.stop()`** — Stop all sounds.
- **`Howler.unload()`** — Destroy all Howls and reset AudioContext.
- **`Howler.codecs(ext)`** — Check codec support (returns Boolean).
- **`Howler.pos(x, y, z)`** — Listener 3D position (spatial).
- **`Howler.orientation(x, y, z, xUp, yUp, zUp)`** — Listener facing direction (spatial).
- **`Howler.stereo(pan)`** — Stereo pan for all current Howls (spatial).

### Events

| Event | Callback | Notes |
|---|---|---|
| `load` | `(id)` | Sound finished loading |
| `loaderror` | `(id, msg)` | Load failed |
| `playerror` | `(id, msg)` | Playback failed (common on mobile without user gesture) |
| `play` | `(id)` | Playback started |
| `end` | `(id)` | Playback ended (fires per loop iteration) |
| `pause` | `(id)` | Paused |
| `stop` | `(id)` | Stopped |
| `mute` | `(id)` | Muted/unmuted |
| `volume` | `(id)` | Volume changed |
| `rate` | `(id)` | Playback rate changed |
| `seek` | `(id)` | Seek position changed |
| `fade` | `(id)` | Fade completed |
| `unlock` | `(id)` | Audio unlocked on mobile |
| `resume` | `(id)` | AudioContext resumed |
| `stereo` | `(id)` | Stereo pan changed (spatial) |
| `pos` | `(id)` | Position changed (spatial) |
| `orientation` | `(id)` | Orientation changed (spatial) |

## Gotchas

- **Mobile playback requires user interaction** — iOS Safari and Chrome on Android block `play()` until a user gesture (touch/click). howler.js auto-attempts unlock via `autoUnlock: true`, but always wrap initial `play()` in a click handler or listen for the `unlock` event. On failure, a `playerror` event fires.

- **`html5: true` is required for streaming** — Web Audio decodes the entire file into an AudioBuffer before playback. For live streams or files larger than ~10 MB, set `html5: true` to use progressive HTML5 Audio loading.

- **Mixed content on HTTPS** — If the page is HTTPS but the audio source is HTTP, howler.js automatically falls back to HTML5 Audio to avoid mixed-content errors. Web Audio XHR will fail on mixed content.

- **`play()` returns a sound ID, not void** — Unlike most methods that return `this` for chaining, `play()` returns the numeric sound ID. Use it to target individual instances with `pause(id)`, `volume(vol, id)`, etc.

- **Sprite times are in milliseconds** — The sprite format is `[offset_ms, duration_ms, (loop_bool)]`. Duration is not end time — it is how long to play from the offset.

- **`fade()` fires `fade` event on completion** — The fade is async. If you need to chain actions after a fade, use the `fade` event or `once('fade', ...)`.

- **`seek()` on a playing sound pauses briefly** — Seeking a playing sound internally pauses, repositions, and resumes. There is a tiny gap. For seamless transitions, use sprites instead.

- **Sound pool size matters for overlapping SFX** — The default pool is 5. If you fire more simultaneous sounds than the pool size, new sounds recycle finished ones. Increase `pool` for games with many overlapping effects.

- **`rate()` changes pitch** — Playback rate affects both speed and pitch (standard Web Audio behavior). There is no built-in time-stretching/pitch-independent rate.

- **`duration()` returns 0 until loaded** — Access `sound.duration()` only after the `load` event fires or check `sound.state() === 'loaded'` first.

- **`autoSuspend` suspends AudioContext after 30s of idle** — This saves battery but means the context must resume before the next `play()`. howler.js handles this automatically via `_autoResume`, but if you disable `autoSuspend`, manage suspend/resume yourself.

- **Web Audio is disabled on iOS < 9 webviews** — Running inside a UIWebView (not Safari) on iOS 8 or earlier causes crashes with Web Audio. howler.js detects this and falls back to HTML5 Audio.

- **`Howler.unload()` closes the AudioContext** — After calling it, a new AudioContext is created. Any saved references to `Howler.ctx` become stale.

- **Spatial plugin requires Web Audio** — Methods like `stereo()`, `pos()`, `pannerAttr()` silently return `this` when running on HTML5 Audio. Check `Howler.usingWebAudio` before relying on spatial features.

## References

- [01-core-api](references/01-core-api.md) — Howl constructor, methods, events, sound pool lifecycle
- [02-spatial-plugin](references/02-spatial-plugin.md) — Stereo panning, 3D positioning, panner attributes, listener setup
- [03-global-api](references/03-global-api.md) — Howler global methods, properties, codec detection, audio unlocking

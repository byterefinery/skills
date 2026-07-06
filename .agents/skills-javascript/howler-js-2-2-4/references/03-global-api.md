# Global API

The `Howler` object is a singleton that controls all audio globally.

## Global Properties

### `Howler.usingWebAudio` — `Boolean`

`true` if Web Audio API is available and active. `false` means HTML5 Audio fallback is in use.

### `Howler.noAudio` — `Boolean`

`true` if no audio is available on this system. Set automatically during setup.

### `Howler.autoUnlock` — `Boolean` `true`

When `true`, howler.js automatically attempts to unlock audio on mobile devices on first user interaction. Set to `false` to handle unlocking manually.

### `Howler.autoSuspend` — `Boolean` `true`

When `true`, the Web Audio `AudioContext` automatically suspends after 30 seconds of inactivity and resumes on next playback. Saves processing and battery.

### `Howler.html5PoolSize` — `Number` `10`

Size of the global pool of pre-unlocked HTML5 Audio objects. These are created on first user interaction and shared across all Howl instances.

### `Howler.ctx` — `AudioContext`

The global `AudioContext` instance. Only available when `usingWebAudio` is `true`. `null` before first setup or after `Howler.unload()`.

### `Howler.masterGain` — `GainNode`

The master gain node. Connects all Web Audio sounds to the destination. Useful for custom effects chains.

### `Howler.state` — `String`

Current state of the AudioContext: `'running'`, `'suspended'`, or `'suspending'`.

## Global Methods

### `Howler.volume([vol])` → `Howler | Number`

Get or set the global master volume.

```js
const current = Howler.volume();  // getter
Howler.volume(0.5);               // setter — affects all sounds
```

Each sound's effective volume = `sound._volume × Howler._volume`. Muted sounds are unaffected.

### `Howler.mute(muted)` → `Howler`

Mute or unmute all sounds globally.

```js
Howler.mute(true);   // mute everything
Howler.mute(false);  // unmute
```

Uses the master gain node (Web Audio) or sets `muted` on each HTML5 Audio node.

### `Howler.stop()` → `Howler`

Stop all sounds in all Howl groups and reset seek to beginning.

### `Howler.unload()` → `Howler`

Unload and destroy all Howl objects. Stops all sounds, clears cache, closes the current `AudioContext`, and creates a new one.

```js
Howler.unload();  // clean slate
```

After calling, `Howler.ctx` references the new AudioContext. Any saved references to the old context become stale.

### `Howler.codecs(ext)` → `Boolean`

Check if a codec is supported in the current browser.

```js
Howler.codecs('mp3');    // true/false
Howler.codecs('ogg');    // true/false
Howler.codecs('webm');   // true/false
Howler.codecs('wav');    // true/false
Howler.codecs('aac');    // true/false
Howler.codecs('flac');   // true/false
```

Supported extensions: `mp3`, `mpeg`, `opus`, `ogg`, `oga`, `wav`, `aac`, `caf`, `m4a`, `m4b`, `mp4`, `weba`, `webm`, `dolby`, `flac`.

## Audio Unlocking (Mobile)

Mobile browsers (iOS Safari, Chrome Android) block audio playback until a user gesture. howler.js handles this automatically:

### Automatic Unlock (`autoUnlock: true`)

On first `touchstart`, `touchend`, `click`, or `keydown`, howler.js:

1. Creates a pool of unlocked HTML5 Audio objects
2. Plays a silent Web Audio buffer to unlock the AudioContext
3. Calls `ctx.resume()` for Android Chrome ≥ 55
4. Fires the `unlock` event on all Howls

```js
Howler.once('unlock', () => {
  console.log('Audio is now playable');
  sound.play();
});
```

### Manual Unlock

Disable auto-unlock and trigger manually:

```js
Howler.autoUnlock = false;

document.addEventListener('click', () => {
  Howler._unlockAudio();
}, { once: true });
```

### Detecting Locked Audio

If `play()` fails due to locked audio, the `playerror` event fires:

```js
sound.on('playerror', (id, msg) => {
  console.warn('Playback failed:', msg);
  // Show a "tap to enable audio" UI
});
```

## Auto Suspend/Resume

When `autoSuspend` is `true`:

1. After 30 seconds with no active Web Audio playback, the AudioContext suspends
2. On next `play()`, `_autoResume()` calls `ctx.resume()` before playback
3. The `resume` event fires on all Howls when the context resumes

```js
Howler.on('resume', () => {
  console.log('AudioContext resumed');
});
```

To disable (e.g., for real-time audio processing):

```js
Howler.autoSuspend = false;
```

## Codec Detection

During `_setupCodecs()`, howler.js tests `Audio.canPlayType()` for each codec and caches results in `Howler._codecs`. The detection handles browser quirks:

- **Opera < 33**: Blocks MP3 (mixed support)
- **Safari < 15**: Blocks WebM (codec issues)
- **IE**: Audio may be disabled entirely — detected via `new Audio().muted`

## HTML5 Audio Pool

HTML5 Audio objects must be individually unlocked (unlike Web Audio which unlocks the whole context). howler.js maintains a global pool:

1. Pool is created on first user interaction during `_unlockAudio()`
2. Size is controlled by `html5PoolSize` (default 10)
3. `_obtainHtml5Audio()` pulls from the pool; creates new if exhausted
4. `_releaseHtml5Audio(audio)` returns an Audio object to the pool
5. Only unlocked Audio objects (`audio._unlocked = true`) are returned to the pool

When the pool is exhausted, a warning is logged and a potentially-locked Audio object is returned.

## Distribution Files

| File | Contents | Size (gzipped) |
|---|---|---|
| `howler.js` | Core + Spatial plugin | ~7 KB |
| `howler.core.js` | Core only (no spatial) | ~5 KB |
| `howler.spatial.js` | Spatial plugin (requires core) | ~2 KB |

Use `howler.core.js` + `howler.spatial.js` separately when you need core functionality without spatial audio to save bandwidth.

## Module Loading

```js
// ES modules
import { Howl, Howler } from 'howler';

// CommonJS
const { Howl, Howler } = require('howler');

// AMD (require.js)
define(['howler'], function(howler) {
  const { Howl, Howler } = howler;
});

// Script tag (global)
<script src="howler.js"></script>
<script>
  // Howl and Howler are on window
  const sound = new Howl({ src: ['sound.mp3'] });
</script>
```

## iOS-Specific Notes

- **Sample rate change**: Mobile Safari can change `ctx.sampleRate` from 44100 to 48000 when opening/closing tabs. howler.js detects this and calls `Howler.unload()` to recreate the context with the correct rate.

- **Scratch buffer**: iOS requires a scratch buffer to properly dispose of Web Audio buffers. howler.js creates a 1-channel, 1-sample buffer at 22050 Hz for this purpose.

- **iOS < 9 webviews**: Web Audio crashes in UIWebView on iOS 8. howler.js detects this and falls back to HTML5 Audio.

# Backends and Context

PixiJS Sound has two playback backends, selected by the library's `useLegacy` flag and browser support. The active one is `sound.context` (an `IMediaContext`).

## Selecting a backend

- `sound.supported` — `true` if WebAudio (`AudioContext`) is available in the browser.
- `sound.useLegacy` — force HTML5 `<audio>` playback. **Must be set before loading any files.** It switches `sound.context` between the WebAudio and HTMLAudio contexts.
- On `init()`, the library sets `useLegacy = !supported` — auto-fallback when WebAudio is missing.

| Capability | WebAudio | HTMLAudio (legacy) |
|---|---|---|
| Filters | yes | no (accessors warn, return `null`) |
| `audioContext` | the `AudioContext` | warns, returns `null` |
| Per-instance precise control | yes | limited |
| iOS silent switch | muted | plays |

## IMediaContext

The common interface (`sound.context`):

```ts
interface IMediaContext {
    muted: boolean;
    volume: number;
    speed: number;
    paused: boolean;
    filters: Filter[];
    audioContext: AudioContext;   // HTMLAudio warns + returns null
    toggleMute(): boolean;
    togglePause(): boolean;
    refresh(): void;              // apply volume/speed/mute to all instances
    refreshPaused(): void;        // apply paused state to all instances
    destroy(): void;
}
```

`WebAudioContext` extends `Filterable` and adds, on top of the interface:

- `compressor` — the `DynamicsCompressorNode` at the end of the node chain
- `analyser` — the `AnalyserNode` before the compressor
- `events` — a PixiJS `EventEmitter`
- `autoPause` — `true` by default; pause all playback when the window blurs
- `_offlineCtx` — an `OfflineAudioContext` (1 channel, clamped 8000–96000 Hz)

The end-of-chain node graph is: per-sound filters → `analyser` → `compressor` → `ctx.destination`.

## Auto-pause on window blur (WebAudio only)

`WebAudioContext` listens for window blur/focus. When blurred it saves the current paused state and pauses playback; on focus it restores. Set `sound.disableAutoPause = true` to keep sounds playing when the tab loses focus (e.g., in an iframe). This only affects the WebAudio backend.

## Autoplay unlock and user gestures

Browsers start the `AudioContext` in the `suspended` state until a user gesture. The library handles this:

- `@pixi/sound` creates its `AudioContext` **on import**, so it starts suspended and Chrome may log "The AudioContext was not allowed to start" — expected.
- `WebAudioContext` adds **document-level** `mousedown`, `touchstart`, and `touchend` listeners (capture phase) that resume the context. A "click to start" screen is enough.
- On iOS/touch devices the context may also need the first play to occur inside a touch event; the context tracks a `_locked` state and checks `statechange` until unlocked.
- If your app starts from the **keyboard**, resume in your own handler:

```ts
import { sound } from '@pixi/sound';
document.addEventListener('keydown', () => {
    if (!sound.context.paused) {
        sound.context.audioContext.resume();
    }
});
```

Note `sound.context.paused` is the *library* paused state (user `pauseAll`), not the browser `AudioContext.state` — the browser state is `'suspended' | 'running' | 'interrupted'` on `sound.context.audioContext`.

## iOS silent mode

The ringer/silent switch mutes WebAudio but not HTML audio, on every iOS browser.

- **iOS 17+** — set the page's audio session to `playback` before playing to allow sound in silent mode:

```js
if ('audioSession' in navigator) {
    navigator.audioSession.type = 'playback';
}
```

  A `'playback'` session can pause other apps' audio (e.g. music) — only use it if acceptable.
- **Older iOS** — set `sound.useLegacy = true` before loading any sounds to play through HTML audio (no filters).

## close / init lifecycle

- `sound.close()` — `removeAll()`, nulls `_sounds`, destroys and nulls both the WebAudio and HTMLAudio contexts, nulls `_context`. Chainable.
- `sound.init()` — recreates the contexts (WebAudio only if `supported`), resets the sounds map to `{}`, and sets `useLegacy = !supported`. Use it to reinitialize after `close()`, e.g. following a hardware failure.

## Version compatibility

| PixiJS | PixiJS Sound |
|---|---|
| v5.x – v6.x | v4.x |
| v7.x | v5.x |
| v8.x | v6.x |

6.0.3 targets PixiJS v8 (peer dependency `pixi.js` ^8.0.0).

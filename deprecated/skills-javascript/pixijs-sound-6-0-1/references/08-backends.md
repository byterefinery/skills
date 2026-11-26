# Backends

## Overview

PixiJS Sound supports two audio backends:

1. **WebAudio** — Default. Uses the Web Audio API for precise timing, filters, and low-latency playback.
2. **HTMLAudio** — Legacy fallback. Uses HTML5 `<audio>` elements. No filter support, higher latency.

The backend is auto-detected based on browser WebAudio support. Force legacy mode with `sound.useLegacy = true`.

## WebAudio Backend

### Components

| Class | Role |
|---|---|
| `WebAudioContext` | Wraps `AudioContext`, manages global volume/mute/pause/filters |
| `WebAudioMedia` | Wraps `AudioBufferSourceNode` for a single Sound |
| `WebAudioInstance` | Individual playback instance with GainNode and timing control |
| `WebAudioUtils` | Helper for AudioParam value setting |

### Features

- Precise sample-accurate timing
- Low latency (~5ms vs ~200ms for HTMLAudio)
- Dynamic filters (Reverb, Distortion, EQ, Stereo, etc.)
- Multiple simultaneous instances from one buffer
- Per-instance volume, speed, mute control
- Progress tracking via analyser

### Limitations

- Requires user gesture to start AudioContext (browser autoplay policy)
- Entire file must be decoded into memory (not suitable for very large files)
- AudioContext may be suspended by browser (tab in background, battery saver)

### AudioContext Management

```ts
// Access raw AudioContext
const audioCtx = sound.context.audioContext;

// Context states
audioCtx.state; // 'suspended', 'running', 'closed'

// Auto-resume on play
// PixiJS Sound handles this automatically
```

### Auto-Pause

WebAudio context auto-pauses when the window loses focus. Disable for iframes:

```ts
sound.disableAutoPause = true;
```

## HTMLAudio Backend

### Components

| Class | Role |
|---|---|
| `HTMLAudioContext` | Manages global volume/mute/pause for HTML audio |
| `HTMLAudioMedia` | Wraps `HTMLAudioElement` for a single Sound |
| `HTMLAudioInstance` | Individual playback instance |

### Features

- Works in all browsers with HTML5 Audio support
- Progressive loading (doesn't need full file in memory)
- Suitable for streaming audio

### Limitations

- **No filter support** — All filter classes silently do nothing
- Higher latency (~200ms)
- Less precise timing
- Limited simultaneous playback (browser-dependent)
- No `sineTone()` or `render()` utility support

## Backend Selection

### Auto-Detection

```ts
if (sound.supported) {
    // WebAudio
} else {
    // HTMLAudio (legacy)
}
```

### Force Legacy

```ts
// Must be set BEFORE loading any files
sound.useLegacy = true;

// Now load sounds
sound.add('music', 'assets/music.mp3');
```

### Reinitialization

```ts
// Close current backend
sound.close();

// Force legacy mode
sound.useLegacy = true;

// Reinitialize
sound.init();
```

## Compatibility Matrix

| Feature | WebAudio | HTMLAudio |
|---|---|---|
| Playback | ✅ | ✅ |
| Volume control | ✅ | ✅ |
| Speed control | ✅ | ✅ |
| Pause/Resume | ✅ | ✅ |
| Loop | ✅ | ✅ |
| Multiple instances | ✅ | ✅ |
| Filters | ✅ | ❌ |
| Sprite playback | ✅ | ✅ |
| Progress tracking | ✅ | ✅ |
| `sineTone()` | ✅ | ❌ |
| `render()` | ✅ | ❌ |
| `StreamFilter` | ✅ | ❌ |
| Low latency | ✅ | ❌ |
| Streaming audio | ❌ | ✅ |

## Browser Support

### WebAudio

| Browser | Version |
|---|---|
| Chrome | 58+ |
| Firefox | 52+ |
| Safari | 11+ |
| iOS Safari | 11+ |
| Edge | 79+ |

### HTMLAudio

All modern browsers with HTML5 Audio support.

## Mobile Considerations

### iOS Safari

- AudioContext requires user gesture
- Auto-pause on background tab
- Inline playback requires `playsinline` attribute (handled automatically)

### Android Chrome

- AudioContext requires user gesture
- May suspend context on memory pressure
- Background audio may be interrupted

### Best Practices

```ts
// 1. Ensure user gesture before first play
document.addEventListener('click', () => {
    sound.play('explosion');
}, { once: true });

// 2. Handle context suspension
sound.context.audioContext?.addEventListener('statechange', () => {
    if (sound.context.audioContext.state === 'suspended') {
        sound.context.audioContext.resume();
    }
});

// 3. For iframes, disable auto-pause
sound.disableAutoPause = true;
```

## Troubleshooting

### No Sound on Mobile

1. Ensure `play()` is called within a user gesture handler
2. Check `sound.supported` — if false, WebAudio isn't available
3. Try `sound.useLegacy = true` before loading

### Filters Not Working

1. Check `sound.useLegacy` — filters only work in WebAudio mode
2. Check `sound.supported` — WebAudio might not be available
3. Verify AudioContext state is `'running'`

### High Latency

1. Use WebAudio mode (not legacy)
2. Preload sounds with `preload: true`
3. Avoid creating sounds on-the-fly; register them ahead of time

### Context Suspended

```ts
// Resume manually
if (sound.context.audioContext?.state === 'suspended') {
    await sound.context.audioContext.resume();
}
```

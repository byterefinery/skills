# Context & Offline

## Context

Wrapper around the native `AudioContext`. Tone.js creates a global Context automatically.

```js
const context = Tone.getContext();
console.log(context.sampleRate);   // 44100 (typically)
console.log(context.state);        // "suspended" | "running" | "closed"
console.log(context.currentTime);  // current time in seconds
```

### Properties

```js
context.sampleRate;          // number
context.currentTime;         // number (seconds)
context.state;               // AudioContextState
context.isOffline;           // boolean
context.rawContext;          // native AudioContext
context.transport;           // Transport
context.destination;         // Destination (output)
context.listener;            // Listener (3D audio)
context.lookAhead;           // seconds (default 0.1)
context.updateInterval;      // seconds (default 0.05)
context.clockSource;         // "worker" | "timeout" | "offline"
context.latencyHint;         // "interactive" | "playback" | "balanced" | seconds
```

### Methods

```js
context.now();               // currentTime + lookAhead
context.immediate();         // currentTime (no lookAhead)
context.resume();            // Resume from suspended state
context.close();             // Close the context
context.dispose();           // Clean up
context.setTimeout(fn, time); // Scheduling-safe setTimeout
context.clearTimeout(id);    // Clear a timeout
context.setInterval(fn, time); // Scheduling-safe setInterval
context.clearInterval(id);   // Clear an interval
```

### Creating a Custom Context

```js
const custom = new Tone.Context({
  latencyHint: "interactive",
  lookAhead: 0.05,
});
Tone.setContext(custom);
```

### Using a Native AudioContext

```js
const native = new AudioContext();
const context = new Tone.Context(native);
Tone.setContext(context);
```

## getContext / setContext

```js
// Get the global context
const ctx = Tone.getContext();

// Set a new global context
Tone.setContext(newContext);

// Set with disposal of old context
Tone.setContext(newContext, true);
```

## start()

Resume the AudioContext from a suspended state. Must be called from a user gesture.

```js
document.querySelector("button").addEventListener("click", async () => {
  await Tone.start();
  console.log("Audio is ready");
  // Now you can play audio
});
```

## supported()

Check if the browser supports Web Audio.

```js
if (Tone.supported) {
  console.log("Web Audio is supported");
}
```

## Offline

Render audio faster than real-time using `OfflineAudioContext`.

```js
// Render 2 seconds of audio
Tone.Offline(() => {
  const osc = new Tone.Oscillator("C4", "sine").toDestination();
  osc.start(0);
  osc.stop(2);
}, 2).then((buffer) => {
  console.log(buffer.duration); // 2
  console.log(buffer.sampleRate);

  // Play the result
  const player = new Tone.Player(buffer).toDestination();
  player.start();
});
```

### With Transport

```js
Tone.Offline(({ transport }) => {
  const synth = new Tone.Synth().toDestination();
  transport.bpm.value = 120;

  transport.scheduleRepeat((time) => {
    synth.triggerAttackRelease("C4", "8n", time);
  }, "4n");

  transport.start(0);
}, 4).then((buffer) => {
  // 4 seconds of rendered audio
});
```

### Options

```js
Tone.Offline(callback, duration, channels, sampleRate);
// channels: default 2
// sampleRate: default from global context (usually 44100)
```

### Gotchas

- Nodes created inside `Offline` are bound to the offline context, not the global context
- The global context is restored after rendering completes
- The callback receives the `OfflineContext` with its own `transport`, `destination`, `listener`
- Use the passed-in context's transport, not `Tone.getTransport()`

## OfflineContext

The context used during offline rendering. Behaves like a regular Context but renders to a buffer instead of speakers.

```js
const offline = new Tone.OfflineContext(2, 4, 44100);
// channels: 2
// duration: 4 seconds
// sampleRate: 44100
```

## DummyContext

A no-op context used during import in non-browser environments (Node.js). Prevents errors when Tone.js is imported server-side.

## AudioContext Lifecycle

```
"suspended" → (Tone.start()) → "running" → (close()) → "closed"
```

- Contexts start in `"suspended"` state
- `Tone.start()` (or `context.resume()`) transitions to `"running"`
- Once `"closed"`, the context cannot be reused
- Always call `Tone.start()` from a user gesture (click, keydown, touch)

## Global Singletons

```js
Tone.getTransport();     // Transport — global timing
Tone.getDestination();   // Destination — output node
Tone.getListener();      // Listener — 3D audio listener
Tone.getContext();       // Context — global audio context
Tone.getDraw();          // Draw — sync draw frame with transport
```

Deprecated (still work but warn): `Tone.Transport`, `Tone.Destination`, `Tone.Master`, `Tone.Listener`, `Tone.Draw`, `Tone.context`.

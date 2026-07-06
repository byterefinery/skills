# Transport & Events

## Transport

Global timing system for scheduling musical events. Each `Context` has one Transport.

```js
const transport = Tone.getTransport();
transport.bpm.value = 120;
transport.timeSignature = 4;
transport.start();
```

### Properties

```js
transport.bpm.value = 120;           // Beats per minute
transport.bpm.rampTo(140, 4);        // Smooth tempo change
transport.timeSignature = 4;         // Numerator (denominator is always 4)
transport.swing = 0.15;              // Swing amount (0-1)
transport.swingSubdivision = "8n";   // Swing subdivision
transport.position;                  // Current position in ticks
transport.seconds;                   // Current position in seconds
transport.state;                     // "started" | "stopped" | "paused"
```

### Looping

```js
transport.loop = true;
transport.loopStart = "0:0:0";  // bars:beats:sixteenths
transport.loopEnd = "1:0:0";
```

### Methods

```js
transport.start(time);       // Start the transport
transport.stop(time);        // Stop
transport.pause(time);       // Pause
transport.cancel(time);      // Cancel all scheduled events after time
transport.seek(position);    // Jump to position (TransportTime or Ticks)
transport.dispose();
```

### Tempo Curves

Schedule BPM changes along the transport timeline:

```js
transport.bpm.setValueAtTime(100, 0);
transport.bpm.setValueAtTime(120, "4:0:0");  // at bar 4
transport.bpm.rampTo(160, "8:0:0");          // ramp to bar 8
```

## schedule / scheduleRepeat

```js
// Schedule a one-shot event
transport.schedule((time) => {
  synth.triggerAttackRelease("C4", "8n", time);
}, "1:0:0");  // at bar 1

// Schedule a repeating event
transport.scheduleRepeat((time) => {
  synth.triggerAttackRelease("C4", "8n", time);
}, "8n");     // every 8th note

// Can also use the return value to cancel
const event = transport.scheduleRepeat(callback, "4n");
transport.cancel(event);
```

### Events

```js
transport.on("start", (time) => console.log("started", time));
transport.on("stop", (time) => console.log("stopped", time));
transport.on("pause", (time) => console.log("paused", time));
transport.on("loop", (time) => console.log("loop", time));
transport.on("loopEnd", (time) => console.log("loop end", time));
transport.on("loopStart", (time) => console.log("loop start", time));
```

## ToneEvent

Base class for transport-synced events.

```js
const event = new Tone.ToneEvent((time) => {
  synth.triggerAttackRelease("C4", "8n", time);
}, "4n");

event.start(0);          // start at transport position 0
event.stop("4:0:0");     // stop at bar 4
event.dispose();
```

### Options

| Option | Type | Default | Description |
|---|---|---|---|
| `callback` | function | — | Called with `(time, value)` |
| `time` | TransportTime | `"0:0:0"` | When the event fires |
| `interval` | TransportTime | `"1:0:0"` | Repeat interval |
| `repeat` | number | `1` | Number of repeats (0 = infinite) |
| `probability` | NormalRange | `1` | Chance of firing each iteration |
| `humanize` | NormalRange | `0` | Randomize timing slightly |

### Methods

```js
event.start(time);
event.stop(time);
event.dispose();
```

## Loop

Simplified loop — fires at a specific position every bar.

```js
const loop = new Tone.Loop((time) => {
  synth.triggerAttackRelease("C4", "8n", time);
}, "0:0:0");  // fires at the start of every bar

loop.start(0);
loop.stop("8:0:0");  // stop after 8 bars
```

### Options

| Option | Type | Default | Description |
|---|---|---|---|
| `iteration` | number | `0` | Beat position within the bar |
| `subdivision` | number | `1` | Subdivision within iteration |

## Part

Collection of events that play as a single unit.

```js
const synth = new Tone.Synth().toDestination();

const part = new Tone.Part((time, note) => {
  synth.triggerAttackRelease(note, "8n", time);
}, [
  ["0:0:0", "C4"],
  ["0:1:0", "E4"],
  ["0:2:0", "G4"],
  ["0:3:0", "B4"],
]).start(0);

Tone.getTransport().start();
```

### Event Formats

```js
// Array format: [time, value]
[["0:0:0", "C4"], ["0:2:0", "E4"]]

// Object format: { time, ...props }
[{ time: "0:0:0", note: "C4", velocity: 0.8 }]
```

### Methods

```js
part.add(time, value);        // Add an event
part.remove(time);            // Remove event at time
part.clear();                 // Remove all events
part.start(time);
part.stop(time);
part.dispose();
```

## Sequence

Grid-based sequencer — rows are instruments, columns are time steps.

```js
const synth1 = new Tone.Synth().toDestination();
const synth2 = new Tone.Synth().toDestination();

const sequence = new Tone.Sequence((time, note) => {
  if (note) {
    synth1.triggerAttackRelease(note, "8n", time);
  }
}, [
  ["C4", null, "E4", null],
  ["D4", null, "F4", null],
], "4n").start(0);

// Switch to second row
sequence.loopEnd = 2;
```

### Methods

```js
sequence.row = 0;             // Active row
sequence.loop = true;
sequence.loopStart = 0;
sequence.loopEnd = 2;
sequence.start(time);
sequence.stop(time);
sequence.dispose();
```

## Pattern

Generates note patterns algorithmically.

```js
const pattern = new Tone.Pattern((time, note) => {
  synth.triggerAttackRelease(note, "8n", time);
}, ["C4", "D4", "E4", "F4", "G4"], "random", "8n").start(0);
```

### Pattern Types

- `"sequential"` — play in order
- `"reverse"` — play in reverse
- `"alternate"` — ping-pong
- `"random"` — random selection
- `"permutation"` — random shuffle (consistent per loop)
- `"strides"` — skip by stride amount
- `"plait"` — interleave patterns

## TransportRepeatEvent

Repeated event with start/stop range.

```js
const repeat = new Tone.TransportRepeatEvent((time) => {
  synth.triggerAttackRelease("C4", "16n", time);
}, "8n", "1:0:0", "4:0:0");  // from bar 1 to bar 4
```

## Syncing Signals to Transport

```js
// Sync a signal to the transport BPM
const osc = new Tone.Oscillator().toDestination().start();
osc.frequency.value = 440;
osc.syncFrequency();

// Now changing transport BPM will scale the frequency proportionally
Tone.getTransport().bpm.value = 160;  // frequency doubles
```

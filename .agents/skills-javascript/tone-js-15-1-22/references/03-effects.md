# Effects

All effects extend `Effect` and follow the wet/dry mixing pattern. They can be chained in series or parallel.

## Effect Base

Every effect has a `wet` property controlling the mix:

```js
const effect = new Tone.Reverb(2);
effect.wet.value = 0.5;  // 50% wet, 50% dry
```

Effects route through `input` → `process` → `output`. Use `.connect()` or `.chain()` to insert them in a signal path.

## Reverb

Convolution-based reverb. Accepts duration (auto-generates impulse) or an impulse response.

```js
// Auto-generated impulse response
const reverb = new Tone.Reverb(3).toDestination();  // 3-second reverb

// From impulse response file
const reverb2 = new Tone.Reverb("impulse.wav").toDestination();

// From AudioBuffer
const reverb3 = new Tone.Reverb(buffer).toDestination();
```

### Options

| Option | Type | Default | Description |
|---|---|---|---|
| `decay` | Time | `2` | Decay time in seconds |
| `wet` | NormalRange | `1` | Wet/dry mix |
| `dry` | NormalRange | `1` | Dry signal level |
| `spread` | NormalRange | `1` | Stereo spread |

## JCReverb

Jaffe-Verb algorithm — lighter than convolution reverb.

```js
const reverb = new Tone.JCReverb({
  roomSize: 0.5,
  dampening: 2000,
  width: 0.75,
}).toDestination();
```

## Freeverb

Freeverb algorithm — another lightweight reverb option.

```js
const reverb = new Tone.Freeverb({
  dampening: 2000,
  roomSize: 0.5,
  width: 1,
}).toDestination();
```

## PingPongDelay

Stereo delay that alternates between left and right channels.

```js
const delay = new Tone.PingPongDelay("8n", 0.5).toDestination();
```

### Options

| Option | Type | Default | Description |
|---|---|---|---|
| `delayTime` | Time | `0.3` | Delay time |
| `feedback` | NormalRange | `0.5` | Feedback amount |

## FeedbackDelay

Mono delay with feedback.

```js
const delay = new Tone.FeedbackDelay("16n", 0.4).toDestination();
```

## Chorus

Modulates copies of the input to create a thickened, ensemble sound.

```js
const chorus = new Tone.Chorus(4, "4n", 0.25).toDestination();
chorus.start();  // LFO-based effects need .start()
```

### Options

| Option | Type | Default | Description |
|---|---|---|---|
| `delayTime` | Time | `"4n"` | Base delay |
| `modulationRate` | Frequency | `0.5` | LFO rate |
| `depth` | NormalRange | `0.7` | Modulation depth |
| `feedback` | NormalRange | `0` | Feedback |
| `voices` | number | `3` | Number of detuned voices |

## Phaser

Allpass filter modulation creating sweeping notches.

```js
const phaser = new Tone.Phaser({
  frequency: 1,
  depth: 0.5,
  octaves: 2,
  feedback: 0.2,
  phases: 6,
  type: "sine",
}).toDestination();
phaser.start();
```

## Tremolo

Amplitude modulation (volume oscillation).

```js
const tremolo = new Tone.Tremolo("8n", 0.5).toDestination();
tremolo.start();
```

### Options

| Option | Type | Default | Description |
|---|---|---|---|
| `frequency` | Frequency | `"4n"` | Modulation rate |
| `depth` | NormalRange | `0.5` | Modulation depth |
| `type` | ToneOscillatorType | `"sine"` | Modulation waveform |

## Vibrato

Pitch modulation (frequency oscillation).

```js
const vibrato = new Tone.Vibrato("4n", 8).toDestination();
vibrato.start();
```

| Option | Type | Default | Description |
|---|---|---|---|
| `frequency` | Frequency | `"4n"` | Modulation rate |
| `depth` | number | `8` | Pitch deviation in semitones |

## Distortion

Wave shaping for grit and saturation.

```js
const distortion = new Tone.Distortion(0.5).toDestination();
```

| Option | Type | Default | Description |
|---|---|---|---|
| `distortion` | NormalRange | `0.5` | Amount of distortion |
| `oversample` | string | `"none"` | `"none"`, `"2x"`, `"4x"` |

## Chebyshev

Chebyshev polynomial distortion — smooth, musical saturation.

```js
const cheby = new Tone.Chebyshev({
  order: 4,
  oversample: "2x",
}).toDestination();
```

## BitCrusher

Reduces bit depth and sample rate for lo-fi sounds.

```js
const crush = new Tone.BitCrusher({
  bits: 4,       // bit depth (1-8)
  oversample: 8, // sample rate reduction factor
}).toDestination();
```

## PitchShift

Real-time pitch transposition using phase vocoder.

```js
const shift = new Tone.PitchShift(7).toDestination();  // +7 semitones
```

| Option | Type | Default | Description |
|---|---|---|---|
| `pitch` | Interval | `0` | Semitone shift |

## FrequencyShifter

Ring-modulation style frequency shift (additive, not multiplicative).

```js
const shifter = new Tone.FrequencyShifter(100).toDestination();
shifter.start();
```

## StereoWidener

Expands the stereo field.

```js
const widener = new Tone.StereoWidener(0.5).toDestination();
```

## AutoFilter

LFO-modulated filter.

```js
const autoFilter = new Tone.AutoFilter("4n").toDestination();
autoFilter.start();
```

| Option | Type | Default | Description |
|---|---|---|---|
| `frequency` | Frequency | `"1n"` | LFO rate |
| `depth` | NormalRange | `1` | Modulation depth |
| `baseFrequency` | Frequency | `200` | Filter base frequency |
| `octaves` | number | `5` | Filter sweep range |

## AutoWah

Velocity-driven auto-wah effect.

```js
const wah = new Tone.AutoWah({
  frequency: 2,
  baseFrequency: 100,
  octaves: 4,
  exponent: 2,
  smoothing: 200,
}).toDestination();
```

## AutoPanner

LFO-modulated stereo panning.

```js
const panner = new Tone.AutoPanner("8n").toDestination();
panner.start();
```

## Effect Routing

```js
// Series chain
source.chain(distortion, reverb, Tone.getDestination());

// Parallel effects
source.fan(chorus, delay, phaser);

// Return send pattern
const send = new Tone.Gain(0.5);
const reverb = new Tone.Reverb(3).toDestination();
send.connect(reverb);
source.connect(send);
source.toDestination();
```
